//! judge_plans: the legal WHOLE-TURN plans of a pg_pos position, from the engine's own full set of legal moves (never a bot's candidates).
//!
//!   judge_plans --positions P.json --deck KEY=path.txt [--deck ...] [--only ID]... [--world-seed N] [--max-plans N] [--max-nodes N] [--max-steps N]
//!
//! One JSON line per position on stdout: {"kind":"plans", "id", "start", "n_plans", "total_found", "capped", "nodes", "plans":[...]}.
//!
//! How it avoids leaking the future:
//!   * the position is built (the first part of this file is pg_pos.rs's `build`, copied) and then turned into the player's own
//!     PlayerObservation, which holds no unseen deck order and no opponent cards (only counts). Everything after that point reads that
//!     observation's `search_state` (the engine's own "one hypothetical deck order" world, seeded with a fixed constant, not by --world-seed).
//!     --world-seed only changes the REAL hidden cards of the built position, so two world seeds must give byte-identical output (a test).
//!   * a plan stops AT its first chance event and the event is described, never resolved: a draw or search (an action that touches the player's
//!     deck, or the engine marks as depending on hidden information), a coin flip (the engine's exact forecast has more than one branch), or an
//!     effect the engine cannot price. Attacks end the turn and are described by the engine's own forecast branches (with their chances).
//!   * plans that reach the same visible state by different orders of the same actions are one plan (state hash of the engine's State).
//! Nothing in engine/ is changed; the binary only calls the engine's public API.
#![allow(clippy::too_many_arguments)]
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::models::{Card, EnergyType, PlayedCard, StatusCondition};
use deckgym::observation::{canonical_actions, hidden_continuation_reason, PlayerObservation, RevealedKnowledge};
use deckgym::players::{create_players, parse_player_code};
use deckgym::state::EnergyZone;
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, seq::SliceRandom, SeedableRng};
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap, HashSet, VecDeque};
use std::hash::{Hash, Hasher};

// ---- copied unchanged from rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs (arg helpers, position builder): lines 30-345 ----
fn arg_all(args: &[String], name: &str) -> Vec<String> {
    args.iter().enumerate().filter(|(_, a)| *a == name).filter_map(|(i, _)| args.get(i + 1)).cloned().collect()
}
fn arg(args: &[String], name: &str) -> Option<String> {
    arg_all(args, name).into_iter().next()
}

fn card(s: &str) -> Card {
    Card::from_str_with_count(&format!("1 {s}")).unwrap_or_else(|e| panic!("card {s:?}: {e}")).1
}
fn cards(v: &Value) -> Vec<Card> {
    v.as_array().map(|a| a.iter().map(|x| card(x.as_str().unwrap())).collect()).unwrap_or_default()
}
fn energy(s: &str) -> EnergyType {
    serde_json::from_value(Value::String(s.to_string())).unwrap_or_else(|e| panic!("energy {s}: {e}"))
}
fn energies(v: &Value) -> Vec<EnergyType> {
    v.as_array().map(|a| a.iter().map(|x| energy(x.as_str().unwrap())).collect()).unwrap_or_default()
}

/// A Special Condition by its engine name ("Asleep", ...); None for a name the engine doesn't have.
fn condition(s: &str) -> Option<StatusCondition> {
    serde_json::from_value(Value::String(s.to_string())).ok()
}

/// One in-play Pokemon from its JSON; also returns every card it carries (for the unseen-deck bookkeeping).
fn pk(v: &Value, problems: &mut Vec<String>) -> (PlayedCard, Vec<Card>) {
    let c = card(v["card"].as_str().expect("card"));
    let base_hp = match &c {
        Card::Pokemon(p) => p.hp,
        _ => 40,
    };
    let behind = cards(&v["behind"]);
    let tools = cards(&v["tools"]);
    let mut carried = vec![c.clone()];
    carried.extend(behind.iter().cloned());
    carried.extend(tools.iter().cloned());
    let mut p = PlayedCard::new(c, 0, base_hp, energies(&v["energy"]), v["new"].as_bool().unwrap_or(false), behind);
    p.attached_tools = tools;
    if let Some(h) = v.get("hp").and_then(|h| h.as_u64()) {
        p = p.with_remaining_hp(h as u32);
    }
    for c in v.get("conditions").and_then(|x| x.as_array()).into_iter().flatten() {
        match c.as_str().and_then(condition) {
            Some(sc) => p = p.with_status_condition(sc),
            None => problems.push(format!("{}: condition {c} is not one the engine has (Asleep, Paralyzed, Confused, Poisoned, Burned)", p.get_name())),
        }
    }
    (p, carried)
}

fn remove_one(pool: &mut Vec<Card>, c: &Card) -> bool {
    if let Some(i) = pool.iter().position(|x| x.get_id() == c.get_id()) {
        pool.remove(i);
        true
    } else {
        false
    }
}

/// The opponent's discard from his own list: Supporters first, then Items, then any other Trainer, then (last resort) anything.
fn take_discard(pool: &mut Vec<Card>, n: usize) -> Vec<Card> {
    use deckgym::models::TrainerType;
    let mut out = Vec::new();
    for pass in 0..3 {
        while out.len() < n {
            let idx = pool.iter().position(|c| match (pass, c) {
                (0, Card::Trainer(t)) => matches!(t.trainer_card_type, TrainerType::Supporter),
                (1, Card::Trainer(t)) => matches!(t.trainer_card_type, TrainerType::Item),
                (2, Card::Trainer(_)) => true,
                _ => false,
            });
            match idx {
                Some(i) => out.push(pool.remove(i)),
                None => break,
            }
        }
    }
    while out.len() < n && !pool.is_empty() {
        out.push(pool.remove(0));
    }
    out
}

struct Built {
    state: State,
    summary: Value,
    problems: Vec<String>,
}

fn build(pos: &Value, deck_me: &Deck, deck_filler: &Deck, shuffle_seed: u64) -> Built {
    let mut problems = Vec::new();
    // a random-player game just to get a legal, stable State to overwrite (what test_support does)
    let r = || parse_player_code("r").unwrap();
    let mut g = Game::new(create_players(deck_me.clone(), deck_filler.clone(), vec![r(), r()]), 1);
    g.play_until_stable();
    let mut st = g.get_state_clone();

    let me = &pos["me"];
    let opp = &pos["opp"];
    let hand_me = cards(&me["hand"]);
    let discard_me = cards(&me["discard"]);
    let mut board_me = Vec::new();
    let mut known_me: Vec<Card> = hand_me.iter().cloned().chain(discard_me.iter().cloned()).collect();
    for p in me["board"].as_array().unwrap() {
        let (pc, carried) = pk(p, &mut problems);
        board_me.push(pc);
        known_me.extend(carried);
    }
    let mut board_opp = Vec::new();
    let mut opp_carried = 0usize;
    let mut opp_seen: Vec<Card> = Vec::new();
    for p in opp["board"].as_array().unwrap() {
        let (pc, carried) = pk(p, &mut problems);
        board_opp.push(pc);
        opp_carried += carried.len();
        opp_seen.extend(carried);
    }
    let stadium = pos.get("stadium").filter(|s| !s.is_null());
    let stadium_owner = stadium.map(|s| s["owner"].as_u64().unwrap() as usize);
    // A position that names a "filler" deck says that deck is the OPPONENT's exact 20-card list (the computer decks of the comparison recordings). Then the
    // opponent's hidden cards are dealt from that list minus everything of his that is visible (board, evolution stacks, Tools, his Stadium), shuffled by
    // the seed, and a discard count is filled from his own list, Supporters first, then Items (never from the pilot's list). Without a "filler" key the old
    // behaviour holds exactly: filler cards cycled from the pilot's own deck (the opponent's list is unknown).
    let known_opp = pos.get("filler").is_some();
    let mut opp_pool: Vec<Card> = Vec::new();
    if known_opp {
        opp_pool = deck_filler.cards.clone();
        for c in &opp_seen {
            if !remove_one(&mut opp_pool, c) {
                problems.push(format!("opponent card {} {} is not in the opponent's list, or is on his board more often than the list holds", c.get_id(), c.get_name()));
            }
        }
        if stadium_owner == Some(1) {
            let sc = card(stadium.unwrap()["card"].as_str().unwrap());
            if !remove_one(&mut opp_pool, &sc) {
                problems.push(format!("the opponent's Stadium {} is not in his list", sc.get_name()));
            }
        }
        let mut orng = StdRng::seed_from_u64(shuffle_seed ^ 0x0B10_0B10);
        opp_pool.shuffle(&mut orng);
    }
    // the opponent's discard is only a count of filler cards unless it is listed
    let discard_opp: Vec<Card> = match opp.get("discard_n").and_then(|x| x.as_u64()) {
        Some(n) if known_opp => take_discard(&mut opp_pool, n as usize),
        Some(n) => deck_filler.cards.iter().cycle().take(n as usize).cloned().collect(),
        None => {
            let listed = cards(&opp["discard"]);
            if known_opp {
                for c in &listed {
                    if !remove_one(&mut opp_pool, c) {
                        problems.push(format!("opponent discard card {} is not in the opponent's list", c.get_name()));
                    }
                }
            }
            listed
        }
    };
    if let Some(s) = stadium {
        if stadium_owner == Some(0) {
            known_me.push(card(s["card"].as_str().unwrap()));
        }
    }

    // the unseen own cards: the deck list minus everything seen
    let mut unseen = deck_me.cards.clone();
    for c in &known_me {
        if !remove_one(&mut unseen, c) {
            problems.push(format!("more copies of {} {} seen than the list holds", c.get_id(), c.get_name()));
        }
    }
    let mut rng = StdRng::seed_from_u64(shuffle_seed);
    unseen.shuffle(&mut rng);
    if let Some(n) = me.get("deck_count").and_then(|x| x.as_u64()) {
        if n as usize != unseen.len() {
            problems.push(format!("deck count: the position says {n}, the list minus seen cards leaves {}", unseen.len()));
        }
    }
    // an optional "top" fixes the first cards of the deck (for forced replays through a draw)
    if let Some(top) = me.get("top") {
        let mut t = cards(top);
        for c in &t {
            if !remove_one(&mut unseen, c) {
                problems.push(format!("top card {} is not in the unseen cards", c.get_name()));
            }
        }
        t.extend(unseen.drain(..));
        unseen = t;
    }

    // the Stadium first, so the board's HP bonuses (Starting Plains: +20 to every Basic) are in place when the board is set
    match stadium {
        Some(s) => {
            st.active_stadium = Some(card(s["card"].as_str().unwrap()));
            st.active_stadium_owner = stadium_owner;
        }
        None => {
            st.active_stadium = None;
            st.active_stadium_owner = None;
        }
    }
    st.set_board(board_me, board_opp);
    // each Pokemon's recorded HP is the HP the game showed, bonuses included: set it now that set_board has refreshed them (pk() could only
    // set it against the printed HP)
    for (side, spec) in [(0usize, me), (1usize, opp)] {
        for (i, p) in spec["board"].as_array().unwrap().iter().enumerate() {
            if let Some(h) = p.get("hp").and_then(|h| h.as_u64()) {
                st.in_play_pokemon[side][i] = st.in_play_pokemon[side][i].take().map(|c| c.with_remaining_hp(h as u32));
            }
        }
    }
    st.hands[0] = hand_me;
    st.decks[0].cards = unseen.clone();
    st.discard_piles[0] = discard_me;
    st.discard_energies[0] = energies(&me["discard_energy"]);

    let opp_hand_n = opp["hand_count"].as_u64().unwrap() as usize;
    let opp_deck_n = match opp.get("deck_count").and_then(|x| x.as_u64()) {
        Some(n) => n as usize,
        None => {
            let used = opp_hand_n + opp_carried + discard_opp.len() + usize::from(stadium_owner == Some(1));
            20usize.saturating_sub(used)
        }
    };
    let filler: Vec<Card> = if known_opp {
        // his own unseen cards, already shuffled; `deck_count` (if given) must match what the list leaves
        if opp_hand_n + opp_deck_n != opp_pool.len() {
            problems.push(format!("opponent hidden cards: hand {opp_hand_n} + deck {opp_deck_n} != the {} cards his list leaves", opp_pool.len()));
        }
        let mut f = opp_pool.clone();
        while f.len() < opp_hand_n + opp_deck_n {
            f.extend(deck_filler.cards.iter().cloned());
        }
        f
    } else {
        deck_filler.cards.iter().cycle().take(opp_hand_n + opp_deck_n).cloned().collect()
    };
    st.hands[1] = filler[..opp_hand_n].to_vec();
    st.decks[1].cards = filler[opp_hand_n..opp_hand_n + opp_deck_n].to_vec();
    st.discard_piles[1] = discard_opp;
    st.discard_energies[1] = energies(&opp["discard_energy"]);

    st.points = [pos["points"][0].as_u64().unwrap() as u8, pos["points"][1].as_u64().unwrap() as u8];
    st.turn_count = pos["turn_count"].as_u64().unwrap() as u8;
    st.current_player = 0;
    st.move_generation_stack.clear();
    let ez = |v: &Value| EnergyZone {
        current: v.get("energy_now").and_then(|x| x.as_str()).map(energy),
        next: v.get("energy_next").and_then(|x| x.as_str()).map(energy),
    };
    st.energy_zone = [ez(me), ez(opp)];

    // the private fields (turn effects, turn flags) go through the State's own serde form
    let mut val = serde_json::to_value(&st).expect("state to json");
    let mut te = serde_json::Map::new();
    if let Some(list) = pos.get("turn_effects").and_then(|x| x.as_array()) {
        for e in list {
            te.entry(e["turn"].as_u64().unwrap().to_string()).or_insert_with(|| json!([])).as_array_mut().unwrap().push(e["effect"].clone());
        }
    }
    val["turn_effects"] = Value::Object(te);
    // effects on an individual Pokemon (e.g. "attacks do 30 less this turn" from Bonsly's Teary Attack): a pk's "effects": [{"effect": .., "turns": n}]
    for (side, spec) in [(0usize, me), (1usize, opp)] {
        for (i, p) in spec["board"].as_array().unwrap().iter().enumerate() {
            if let Some(list) = p.get("effects").and_then(|x| x.as_array()) {
                let arr: Vec<Value> = list.iter().map(|e| json!([e["effect"].clone(), e["turns"].as_u64().unwrap_or(1)])).collect();
                val["in_play_pokemon"][side][i]["effects"] = Value::Array(arr);
            }
        }
    }
    if let Some(flags) = pos.get("flags").and_then(|x| x.as_object()) {
        for (k, v) in flags {
            assert!(val.get(k).is_some(), "no such state field {k}");
            val[k] = v.clone();
        }
    }
    let mut st: State = serde_json::from_value(val).expect("json back to state");
    // each side's own knock-outs earlier in the game (Kingambit's Overlord's Blade), before the bot moves
    for (side, spec) in [(0usize, me), (1usize, opp)] {
        match spec.get("knockouts") {
            None | Some(Value::Null) => {}
            Some(k) => match k.as_u64() {
                Some(n) => st.set_own_knockouts_this_game(side, n as u32),
                None => problems.push(format!("knockouts {k} is not a count")),
            },
        }
    }

    let describe = |side: usize| -> Value {
        let slots: Vec<Value> = st.in_play_pokemon[side]
            .iter()
            .enumerate()
            .filter_map(|(i, p)| p.as_ref().map(|p| (i, p)))
            .map(|(i, p)| {
                json!({
                    "slot": i, "card": p.card.get_name(), "id": p.card.get_id(), "hp": p.get_remaining_hp(),
                    "energy": p.attached_energy.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
                    "tools": p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>(),
                    "behind": p.cards_behind.iter().map(|t| t.get_name()).collect::<Vec<_>>(),
                })
            })
            .collect();
        Value::Array(slots)
    };
    let mut hand_names: Vec<String> = st.hands[0].iter().map(|c| c.get_name()).collect();
    hand_names.sort();
    let summary = json!({
        "turn_count": st.turn_count, "points": st.points,
        "me": {"hand": hand_names, "deck": st.decks[0].cards.len(), "discard": st.discard_piles[0].iter().map(|c| c.get_name()).collect::<Vec<_>>(), "board": describe(0),
               "energy_zone": [format!("{:?}", st.energy_zone[0].current), format!("{:?}", st.energy_zone[0].next)]},
        "opp": {"hand": st.hands[1].len(), "deck": st.decks[1].cards.len(), "board": describe(1)},
        "stadium": st.active_stadium.as_ref().map(|c| c.get_name()),
    });
    Built { state: st, summary, problems }
}


// ---------------------------------------------------------------------------------------------------------------------------------------
// From here on: the plan lister (new code). Everything below reads only the observation's search world.
// ---------------------------------------------------------------------------------------------------------------------------------------

/// Compact action name, identical to the one pg_pos prints (so a plan's labels can be compared with a position's "his_plan").
/// 0 for the actor `me`, 1 for the other side (labels print seat numbers relative to the actor in observation mode; identity when me == 0).
fn rel(p: usize, me: usize) -> usize {
    if p == me {
        0
    } else {
        1
    }
}

fn rel_num(v: &mut Value, me: usize) {
    if let Some(p) = v.as_u64() {
        *v = json!(rel(p as usize, me));
    }
}

fn rel_pair_first(v: &mut Value, me: usize) {
    if let Value::Array(a) = v {
        if let Some(x) = a.get_mut(0) {
            rel_num(x, me);
        }
    }
}

/// Maps every seat value inside an action's JSON (or a turn effect's) to the actor-relative number. `variant` is the action's variant name.
fn rel_seats(v: &mut Value, me: usize, variant: &str) {
    match v {
        Value::Object(m) => {
            for (k, x) in m.iter_mut() {
                match k.as_str() {
                    "player" | "source_player" | "target_player" => rel_num(x, me),
                    "attacking_ref" => rel_pair_first(x, me),
                    "prior_knockouts" | "damaged_refs" => {
                        if let Value::Array(items) = x {
                            items.iter_mut().for_each(|i| rel_pair_first(i, me));
                        }
                    }
                    "point_denial_flips" => {
                        if let Value::Array(items) = x {
                            for i in items.iter_mut() {
                                if let Value::Array(pair) = i {
                                    if let Some(first) = pair.get_mut(0) {
                                        rel_pair_first(first, me);
                                    }
                                }
                            }
                        }
                    }
                    "targets" if variant == "ApplyDamage" => {
                        if let Value::Array(items) = x {
                            for i in items.iter_mut() {
                                if let Value::Array(t) = i {
                                    if let Some(s) = t.get_mut(1) {
                                        rel_num(s, me);
                                    }
                                }
                            }
                        }
                    }
                    _ => rel_seats(x, me, variant),
                }
            }
        }
        Value::Array(a) => a.iter_mut().for_each(|x| rel_seats(x, me, variant)),
        _ => {}
    }
}

fn pg_label(a: &Action, me: usize) -> String {
    let nm = |c: &deckgym::models::Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::UseAbility { in_play_idx } => format!("Ability@{}", in_play_idx),
        SimpleAction::Attack(at) => format!("Attack:{}", at.title),
        SimpleAction::Retreat(i) => format!("Retreat:{}", i),
        SimpleAction::Attach { attachments, is_turn_energy } => format!(
            "Attach:{}{}",
            attachments.iter().map(|(n, e, i)| format!("{}{:?}@{}", n, e, i)).collect::<Vec<_>>().join("+"),
            if *is_turn_energy { " zone" } else { " fx" }
        ),
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("Tool:{}@{}", nm(tool_card), in_play_idx),
        SimpleAction::Heal { in_play_idx, amount, .. } => format!("Heal:{}@{}", amount, in_play_idx),
        SimpleAction::Activate { player, in_play_idx } => format!("Activate:{}@{}", if me == 0 { *player } else { rel(*player, me) }, in_play_idx),
        SimpleAction::Promote { player, in_play_idx } => format!("Promote:{}@{}", if me == 0 { *player } else { rel(*player, me) }, in_play_idx),
        SimpleAction::ChooseMistyTarget { in_play_idx } => format!("MistyTarget@{}", in_play_idx),
        // ChooseRetreatEnergy (which Energy a retreat pays) has NO short label: the old `RetreatPay:<slot>` dropped the payment, so two different payments were one
        // label (1,142 of 5,728 plans on the 92 old positions could not be named). It takes the Name#JSON fallback below, which carries every argument.
        SimpleAction::AttachTypedFromDiscard { in_play_idx, energy_type, .. } => format!("AttachTypedFromDiscard:{:?}@{}", energy_type, in_play_idx),
        SimpleAction::EndTurn => "EndTurn".to_string(),
        // Every other action: its name plus ALL its arguments, so two actions that differ only in a target (Field Blower's DiscardToolFromPokemon on
        // different Pokémon or Tools, say) never share a label. Short recorded labels (the bare name) still match, see label_matches.
        other => {
            let name = format!("{:?}", other).split(|c: char| c == ' ' || c == '{' || c == '(').next().unwrap_or("?").to_string();
            match serde_json::to_value(other) {
                Ok(Value::Object(m)) if m.len() == 1 && me != 0 => {
                    let mut inner = m.values().next().unwrap().clone();
                    rel_seats(&mut inner, me, &name);
                    format!("{}#{}", name, inner)
                }
                Ok(Value::Object(m)) if m.len() == 1 => format!("{}#{}", name, m.values().next().unwrap()),
                _ => name,
            }
        }
    }
}

fn slot_label(i: usize) -> String {
    if i == 0 {
        "Active".to_string()
    } else {
        format!("Bench {i}")
    }
}

fn slot_name(st: &State, side: usize, idx: usize) -> String {
    match st.in_play_pokemon[side].get(idx).and_then(|p| p.as_ref()) {
        Some(p) => format!("{} ({})", p.get_name(), slot_label(idx)),
        None => format!("an empty {} slot", slot_label(idx)),
    }
}

/// A plain-English name for one engine action, read against the state it is played in.
fn english(st: &State, a: &Action) -> String {
    let me = a.actor;
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play {}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Put {} on the Bench ({})", card.get_name(), slot_label(*idx)),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve {} into {}", slot_name(st, me, *in_play_idx), evolution.get_name()),
        SimpleAction::UseAbility { in_play_idx } => format!("Use the Ability of {}", slot_name(st, me, *in_play_idx)),
        SimpleAction::Attack(at) => format!("Attack with {} ({} damage printed)", at.title, at.fixed_damage),
        SimpleAction::Retreat(i) => format!("Retreat: switch the Active {} with {}", slot_name(st, me, 0), slot_name(st, me, *i)),
        SimpleAction::Attach { attachments, is_turn_energy } => {
            let parts: Vec<String> = attachments.iter().map(|(n, e, i)| format!("{n} {e:?} Energy to {}", slot_name(st, me, *i))).collect();
            format!("Attach {} ({})", parts.join(" and "), if *is_turn_energy { "this turn's Energy from the Energy Zone" } else { "by a card effect" })
        }
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("Attach {} to {}", tool_card.get_name(), slot_name(st, me, *in_play_idx)),
        SimpleAction::Activate { in_play_idx, player } | SimpleAction::Promote { in_play_idx, player } => {
            format!("Choose {} to be the Active Pokémon", slot_name(st, *player, *in_play_idx))
        }
        SimpleAction::EndTurn => "End the turn".to_string(),
        SimpleAction::DiscardToolFromPokemon { player, in_play_idx, tool_idx } => {
            let tool = st.in_play_pokemon[*player].get(*in_play_idx).and_then(|p| p.as_ref()).and_then(|p| p.attached_tools.get(*tool_idx)).map(|t| t.get_name()).unwrap_or_else(|| "?".into());
            format!("Discard the Tool {} from {} {}", tool, if *player == me { "your" } else { "the opponent's" }, slot_name(st, *player, *in_play_idx))
        }
        SimpleAction::UseStadium => format!("Use the Stadium {} (its once-per-turn effect)", st.active_stadium.as_ref().map(|c| c.get_name()).unwrap_or_else(|| "?".into())),
        SimpleAction::DiscardActiveStadium => "Discard the Stadium in play".to_string(),
        SimpleAction::ChooseRetreatEnergy { to_in_play_idx, energies } => format!(
            "Pay the retreat cost of {} (switching with {}) by discarding {} Energy",
            slot_name(st, me, 0),
            slot_name(st, me, *to_in_play_idx),
            energies.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>().join(" + ")
        ),
        _ => format!("{} (a choice)", pg_label(a, a.actor)),
    }
}

fn max_hp(p: &PlayedCard) -> u32 {
    let v = serde_json::to_value(p).unwrap_or(Value::Null);
    let g = |k: &str| v.get(k).and_then(|x| x.as_u64()).unwrap_or(0) as u32;
    let m = g("base_hp") + g("stadium_hp_bonus") + g("ability_hp_bonus");
    if m == 0 {
        p.get_remaining_hp()
    } else {
        m
    }
}

fn conditions(p: &PlayedCard) -> Vec<&'static str> {
    [(p.is_asleep(), "Asleep"), (p.is_paralyzed(), "Paralyzed"), (p.is_confused(), "Confused"), (p.is_poisoned(), "Poisoned"), (p.is_burned(), "Burned")]
        .iter()
        .filter(|(b, _)| *b)
        .map(|(_, n)| *n)
        .collect()
}

fn pk_line(i: usize, p: &PlayedCard) -> String {
    let en: Vec<String> = p.attached_energy.iter().map(|e| format!("{e:?}")).collect();
    let mut s = format!("{}: {} {}/{} HP, Energy [{}]", slot_label(i), p.get_name(), p.get_remaining_hp(), max_hp(p), en.join(", "));
    if !p.attached_tools.is_empty() {
        s += &format!(", Tool: {}", p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>().join(", "));
    }
    let c = conditions(p);
    if !c.is_empty() {
        s += &format!(", {}", c.join("+"));
    }
    if !p.cards_behind.is_empty() {
        s += &format!(" (evolved from {})", p.cards_behind.iter().map(|t| t.get_name()).collect::<Vec<_>>().join(" < "));
    }
    if p.played_this_turn {
        s += " (came into play this turn)";
    }
    if p.ability_used {
        s += " (its Ability was used this turn)";
    }
    s
}

fn board_lines(st: &State, side: usize) -> Vec<String> {
    st.in_play_pokemon[side].iter().enumerate().filter_map(|(i, p)| p.as_ref().map(|p| pk_line(i, p))).collect()
}

fn names(cards: &[Card]) -> Vec<String> {
    let mut v: Vec<String> = cards.iter().map(|c| c.get_name()).collect();
    v.sort();
    v
}

fn energy_names(e: &[EnergyType]) -> Vec<String> {
    let mut v: Vec<String> = e.iter().map(|x| format!("{x:?}")).collect();
    v.sort();
    v
}

fn start_block(obs: &PlayerObservation) -> Value {
    let v = obs.visible_state();
    let me = obs.actor;
    let mut unseen: BTreeMap<String, u32> = BTreeMap::new();
    for c in &obs.known_own_deck {
        *unseen.entry(c.get_name()).or_insert(0) += 1;
    }
    json!({
        "turn_count": v.turn_count,
        "points": [v.points[me], v.points[1 - me]],
        "stadium": v.active_stadium.as_ref().map(|c| c.get_name()),
        "stadium_owner": v.active_stadium_owner.map(|o| if o == me { 0 } else { 1 }),
        "energy_zone": [v.energy_zone[me].current.map(|e| format!("{e:?}")), v.energy_zone[me].next.map(|e| format!("{e:?}"))],
        "me": {"board": board_lines(v, me), "hand": names(&v.hands[me]), "discard": names(&v.discard_piles[me]), "discard_energy": energy_names(&v.discard_energies[me]),
               "deck_size": obs.known_own_deck.len(), "unseen_deck": unseen},
        "opp": {"board": board_lines(v, 1 - me), "hand_count": v.hands[1 - me].len(), "deck_count": v.decks[1 - me].cards.len(), "discard": names(&v.discard_piles[1 - me]),
                "discard_energy": energy_names(&v.discard_energies[1 - me])},
    })
}

/// The State as JSON with every list whose ORDER carries no meaning put in a fixed order: hands, discard piles, discarded Energy, and each
/// Pokémon's attached Energy and Tools. Two plans that only differ in the order cards sit in such a list reach the same visible state.
/// (Own deck order is left alone: a plan never touches it, because it stops at the first draw.)
fn canonical_state_json(st: &State) -> Value {
    let mut v = serde_json::to_value(st).expect("state json"); // serde_json maps are sorted, so equal states give equal text
    canonicalize_state_value(&mut v);
    v
}

fn canonicalize_state_value(v: &mut Value) {
    fn sort_list(x: &mut Value) {
        if let Value::Array(a) = x {
            a.sort_by_key(|e| e.to_string());
        }
    }
    for key in ["hands", "discard_piles", "discard_energies"] {
        if let Some(Value::Array(players)) = v.get_mut(key) {
            players.iter_mut().for_each(sort_list);
        }
    }
    if let Some(Value::Array(sides)) = v.get_mut("in_play_pokemon") {
        for side in sides.iter_mut() {
            if let Value::Array(slots) = side {
                for slot in slots.iter_mut() {
                    for field in ["attached_energy", "attached_tools"] {
                        if let Some(f) = slot.get_mut(field) {
                            sort_list(f);
                        }
                    }
                }
            }
        }
    }
}

/// Hash of what a player knows: own-deck list as a multiset (sorted) and the template State in canonical form.
fn obs_hash(obs: &PlayerObservation) -> u64 {
    let mut v = serde_json::to_value(obs).expect("observation json");
    if let Some(Value::Array(a)) = v.get_mut("known_own_deck") {
        a.sort_by_key(|e| e.to_string());
    }
    if let Some(t) = v.get_mut("template") {
        canonicalize_state_value(t);
    }
    let mut h = std::collections::hash_map::DefaultHasher::new();
    v.to_string().hash(&mut h);
    h.finish()
}

fn state_hash(st: &State) -> u64 {
    let v = canonical_state_json(st);
    let mut h = std::collections::hash_map::DefaultHasher::new();
    v.to_string().hash(&mut h);
    h.finish()
}

fn count_by_type(e: &[EnergyType]) -> BTreeMap<String, i32> {
    let mut m = BTreeMap::new();
    for x in e {
        *m.entry(format!("{x:?}")).or_insert(0) += 1;
    }
    m
}

/// What changed between two states on the two boards and the points (never hands or decks).
fn diff_lines(a: &State, b: &State, me: usize) -> Vec<String> {
    let mut out = Vec::new();
    for (side, who) in [(1 - me, "Opponent"), (me, "You")] {
        let n = a.in_play_pokemon[side].len().max(b.in_play_pokemon[side].len());
        for i in 0..n {
            let pa = a.in_play_pokemon[side].get(i).and_then(|x| x.as_ref());
            let pb = b.in_play_pokemon[side].get(i).and_then(|x| x.as_ref());
            match (pa, pb) {
                (Some(x), None) => out.push(format!("{who}: {} ({}) is Knocked Out or leaves play", x.get_name(), slot_label(i))),
                (None, Some(y)) => out.push(format!("{who}: {} takes the {} spot", y.get_name(), slot_label(i))),
                (Some(x), Some(y)) if x.get_name() != y.get_name() => {
                    out.push(format!("{who}: {} ({}) is replaced by {}", x.get_name(), slot_label(i), y.get_name()))
                }
                (Some(x), Some(y)) => {
                    let (hx, hy) = (x.get_remaining_hp(), y.get_remaining_hp());
                    if hx != hy {
                        out.push(format!("{who}: {} ({}) HP {} -> {}", x.get_name(), slot_label(i), hx, hy));
                    }
                    let (ex, ey) = (count_by_type(&x.attached_energy), count_by_type(&y.attached_energy));
                    if ex != ey {
                        out.push(format!("{who}: {} ({}) Energy {:?} -> {:?}", x.get_name(), slot_label(i), energy_names(&x.attached_energy), energy_names(&y.attached_energy)));
                    }
                    let (cx, cy) = (conditions(x), conditions(y));
                    if cx != cy {
                        out.push(format!("{who}: {} ({}) conditions {:?} -> {:?}", x.get_name(), slot_label(i), cx, cy));
                    }
                    if x.attached_tools.len() != y.attached_tools.len() {
                        out.push(format!("{who}: {} ({}) Tools {} -> {}", x.get_name(), slot_label(i), x.attached_tools.len(), y.attached_tools.len()));
                    }
                }
                _ => {}
            }
        }
    }
    if a.points != b.points {
        out.push(format!("Points: you {} -> {}, opponent {} -> {}", a.points[me], b.points[me], a.points[1 - me], b.points[1 - me]));
    }
    out
}

/// One plan step: its labels, the engine action itself (real seat), and whether its node had exactly one canonical action.
#[derive(Clone)]
struct Step {
    label: String,
    english: String,
    action: Action,
    forced: bool,
}

type Path = Vec<Step>;

fn str_hash(s: &str) -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    s.hash(&mut h);
    h.finish()
}

/// The identity of a plan: the visible state it reaches before its last step, and that last step (with its description).
/// Two move lists with the same key are the same plan, whatever order or slot numbers they used on the way.
fn leaf_key(before: &State, label: &str, extra: &Value) -> String {
    format!("{:016x}-{:016x}", state_hash(before), str_hash(&format!("{label}|{extra}")))
}

struct Collector {
    me: usize,
    /// plan key -> (the plan's actions with their real seats, forced flags); filled only for plans that are pushed
    actions: HashMap<String, (Vec<Action>, Vec<bool>)>,
    plans: Vec<Value>,
    keys: HashSet<String>,
    total_found: usize,
    max_plans: usize,
    capped: bool,
    /// JUDGE_DEBUG_SPLITS=1: for plans that look the same to the judge (same board, hand and last step) but are different engine states, say what differs.
    debug: bool,
    look_alike: HashMap<String, Value>,
}

/// The first few paths where two State values differ (debugging aid only).
fn json_diff(a: &Value, b: &Value, path: &str, out: &mut Vec<String>) {
    if out.len() >= 6 || a == b {
        return;
    }
    match (a, b) {
        (Value::Object(x), Value::Object(y)) => {
            for k in x.keys().chain(y.keys().filter(|k| !x.contains_key(*k))) {
                json_diff(x.get(k).unwrap_or(&Value::Null), y.get(k).unwrap_or(&Value::Null), &format!("{path}.{k}"), out);
            }
        }
        (Value::Array(x), Value::Array(y)) if x.len() == y.len() => {
            for (i, (p, q)) in x.iter().zip(y).enumerate() {
                json_diff(p, q, &format!("{path}[{i}]"), out);
            }
        }
        _ => out.push(format!("{path}: {} vs {}", a.to_string().chars().take(80).collect::<String>(), b.to_string().chars().take(80).collect::<String>())),
    }
}

impl Collector {
    fn add(&mut self, before: &State, path: &Path, last: Step, end: &str, extra: Value) {
        let key = leaf_key(before, &last.label, &extra);
        if self.debug {
            let look = format!("{}|{}|{:?}|{:?}", last.label, extra, board_lines(before, self.me), names(&before.hands[self.me]));
            let sv = canonical_state_json(before);
            if let Some(prev) = self.look_alike.get(&look) {
                if *prev != sv {
                    let mut d = Vec::new();
                    json_diff(prev, &sv, "state", &mut d);
                    eprintln!("SPLIT {} :: {}", path.iter().map(|p| p.label.clone()).chain(std::iter::once(last.label.clone())).collect::<Vec<_>>().join(" > "), d.join(" | "));
                }
            } else {
                self.look_alike.insert(look, sv);
            }
        }
        if !self.keys.insert(key.clone()) {
            return;
        }
        self.total_found += 1;
        if self.plans.len() >= self.max_plans {
            self.capped = true;
            return;
        }
        let mut labels: Vec<String> = path.iter().map(|p| p.label.clone()).collect();
        let mut steps: Vec<String> = path.iter().map(|p| p.english.clone()).collect();
        let mut acts: Vec<Action> = path.iter().map(|p| p.action.clone()).collect();
        let mut forced: Vec<bool> = path.iter().map(|p| p.forced).collect();
        labels.push(last.label);
        steps.push(last.english);
        acts.push(last.action);
        forced.push(last.forced);
        self.actions.insert(key.clone(), (acts, forced));
        self.plans.push(json!({
            "key": key, "labels": labels, "steps": steps, "n_steps": labels.len(), "end": end, "final": extra,
            "result": {"board": board_lines(before, self.me), "hand": names(&before.hands[self.me]), "points": [before.points[self.me], before.points[1 - self.me]],
                       "deck_size": before.decks[self.me].cards.len()},
        }));
    }
}

fn attack_info(st: &State, act: &Action, me: usize) -> Value {
    let SimpleAction::Attack(at) = &act.action else { unreachable!() };
    let mut info = json!({"title": at.title, "printed_damage": at.fixed_damage, "effect": at.effect});
    let st2 = st.clone();
    let act2 = act.clone();
    let res = std::panic::catch_unwind(std::panic::AssertUnwindSafe(move || -> Result<Vec<(f64, Vec<String>)>, String> {
        let o = try_forecast_action(&st2, &act2).map_err(|e| e.reason.to_string())?;
        let (probs, muts) = o.into_branches();
        let mut groups: Vec<(f64, Vec<String>)> = Vec::new();
        for (p, m) in probs.iter().zip(muts.into_iter()) {
            let mut s1 = st2.clone();
            let mut rng = StdRng::seed_from_u64(11);
            m(&mut rng, &mut s1, &act2);
            let lines = diff_lines(&st2, &s1, me);
            match groups.iter_mut().find(|g| g.1 == lines) {
                Some(g) => g.0 += *p,
                None => groups.push((*p, lines)),
            }
        }
        Ok(groups)
    }));
    match res {
        Ok(Ok(groups)) => {
            info["outcomes"] = Value::Array(groups.into_iter().map(|(p, l)| json!({"p": (p * 1000.0).round() / 1000.0, "lines": l})).collect());
        }
        Ok(Err(reason)) => info["unpriced"] = json!(reason),
        Err(_) => info["unpriced"] = json!("the engine could not forecast this attack"),
    }
    info
}

fn stack_wants_draw(st: &State, me: usize) -> bool {
    st.move_generation_stack.iter().any(|(who, choices)| *who == me && choices.iter().any(|c| matches!(c, SimpleAction::DrawCard { .. })))
}

struct Limits {
    max_plans: usize,
    max_nodes: usize,
    max_steps: usize,
}

/// What one legal action of the player is, for the plan lister: the end of a plan, or a step it can continue past.
enum Kind {
    Attack(Value),
    EndTurn,
    Chance(Value),
    Child(State),
}

/// The single place that decides whether an action ends a plan (an attack, ending the turn, a chance event) or is an ordinary step.
/// A chance event is: the engine marks the action as depending on information the player cannot see, or cannot price it; its exact forecast has more
/// than one branch (a coin, a random pick); or it changes the order of the player's own deck (a draw, a search, a shuffle).
fn step_kind(st: &State, act: &Action, me: usize) -> Kind {
    match &act.action {
        SimpleAction::Attack(_) => Kind::Attack(attack_info(st, act, me)),
        SimpleAction::EndTurn => Kind::EndTurn,
        _ => {
            let reason = hidden_continuation_reason(st, act);
            match try_forecast_action(st, act) {
                Err(e) => Kind::Chance(json!({"kind": "unpriced", "reason": e.reason.to_string()})),
                Ok(o) => {
                    let (probs, muts) = o.into_branches();
                    if probs.len() > 1 {
                        let ps: Vec<f64> = probs.iter().map(|p| (p * 1000.0).round() / 1000.0).collect();
                        return Kind::Chance(json!({"kind": "coin_or_random", "branch_chances": ps}));
                    }
                    let mut s1 = st.clone();
                    let mut rng = StdRng::seed_from_u64(7);
                    let first = muts.into_iter().next().expect("one outcome branch");
                    first(&mut rng, &mut s1, act);
                    let deck_touched = s1.decks[me].cards != st.decks[me].cards || stack_wants_draw(&s1, me);
                    if let Some(r) = reason {
                        Kind::Chance(json!({"kind": "hidden_information", "reason": r}))
                    } else if deck_touched {
                        Kind::Chance(json!({"kind": "your_deck", "deck_size_before": st.decks[me].cards.len(), "deck_size_after": s1.decks[me].cards.len(),
                                            "hand_size_before": st.hands[me].len(), "hand_size_after": s1.hands[me].len()}))
                    } else {
                        Kind::Child(s1)
                    }
                }
            }
        }
    }
}

/// What the search also knows beyond the plan JSON: every plan's actions, and the root's canonical actions with the child state's hash (None for an end).
struct Extras {
    actions: HashMap<String, (Vec<Action>, Vec<bool>)>,
    root: Vec<(Action, Option<u64>)>,
    root_hash: u64,
}

fn list_plans(world: &State, lim: &Limits, me: usize) -> (Vec<Value>, usize, usize, bool, usize, Extras) {
    let mut root: Vec<(Action, Option<u64>)> = Vec::new();
    let mut col = Collector {
        me,
        actions: HashMap::new(),
        plans: Vec::new(),
        keys: HashSet::new(),
        total_found: 0,
        max_plans: lim.max_plans,
        capped: false,
        debug: std::env::var("JUDGE_DEBUG_SPLITS").is_ok(),
        look_alike: HashMap::new(),
    };
    let mut seen: HashSet<u64> = HashSet::new();
    let mut q: VecDeque<(State, Path)> = VecDeque::new();
    seen.insert(state_hash(world));
    q.push_back((world.clone(), Vec::new()));
    let mut nodes = 0usize;
    let mut deepest_cut = 0usize;
    while let Some((st, path)) = q.pop_front() {
        nodes += 1;
        if nodes > lim.max_nodes {
            col.capped = true;
            break;
        }
        let (actor, mut acts) = st.generate_possible_actions();
        if actor != me {
            // an opponent frame in the middle of our turn (for example he must choose a new Active): the plan stops here
            if let Some(last) = path.last() {
                let mut before_path = path.clone();
                before_path.pop();
                col.add(&st, &before_path, last.clone(), "opponent_choice", json!({"kind": "opponent_choice"}));
            }
            continue;
        }
        let is_root = path.is_empty();
        if path.len() >= lim.max_steps {
            deepest_cut += 1;
            col.capped = true;
            continue;
        }
        canonical_actions(&mut acts);
        let forced = acts.len() == 1;
        for act in acts {
            let label = pg_label(&act, me);
            let text = english(&st, &act);
            let step = Step { label, english: text, action: act.clone(), forced };
            match step_kind(&st, &act, me) {
                Kind::Attack(info) => {
                    if is_root {
                        root.push((act.clone(), None));
                    }
                    col.add(&st, &path, step, "attack", info)
                }
                Kind::EndTurn => {
                    if is_root {
                        root.push((act.clone(), None));
                    }
                    col.add(&st, &path, step, "end_turn", json!({"kind": "end_turn"}))
                }
                Kind::Chance(extra) => {
                    if is_root {
                        root.push((act.clone(), None));
                    }
                    col.add(&st, &path, step, "chance", extra)
                }
                Kind::Child(s1) => {
                    let h = state_hash(&s1);
                    if is_root {
                        root.push((act.clone(), Some(h)));
                    }
                    if seen.insert(h) {
                        let mut p2 = path.clone();
                        p2.push(step);
                        q.push_back((s1, p2));
                    }
                }
            }
        }
    }
    let root_hash = state_hash(world);
    let Collector { mut plans, total_found, capped, actions, .. } = col;
    let rank = |p: &Value| match p["end"].as_str().unwrap_or("") {
        "attack" => 0,
        "chance" => 1,
        "end_turn" => 2,
        _ => 3,
    };
    plans.sort_by(|a, b| {
        (rank(a), a["n_steps"].as_u64(), a["labels"].to_string()).cmp(&(rank(b), b["n_steps"].as_u64(), b["labels"].to_string()))
    });
    for (i, p) in plans.iter_mut().enumerate() {
        p["n"] = json!(i + 1);
    }
    (plans, total_found, nodes, capped, deepest_cut, Extras { actions, root, root_hash })
}

/// A `Name#{json}` label with its JSON read and written back in the compact, key-sorted form the printers use, so key order and spacing in a requested
/// label never matter (serde_json keeps its maps sorted here). Anything else, and JSON that does not parse, is returned unchanged (it then simply
/// matches no legal action and the replay says so).
fn canon_label(l: &str) -> String {
    match l.split_once('#') {
        Some((name, js)) if name.chars().next().map_or(false, |c| c.is_ascii_alphabetic()) && name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_') => {
            match serde_json::from_str::<Value>(js) {
                Ok(mut v) => {
                    sort_energies(&mut v);
                    format!("{name}#{v}")
                }
                Err(_) => l.to_string(),
            }
        }
        _ => l.to_string(),
    }
}

/// A list of Energy types under the key `energies` is a multiset (which Energy a retreat pays or an attack discards): its order is not part of the action, so
/// the canonical label sorts it (judge.py `concrete_label` does the same on the Python side).
fn sort_energies(v: &mut Value) {
    if let Value::Object(m) = v {
        if let Some(Value::Array(a)) = m.get_mut("energies") {
            if a.iter().all(|x| x.is_string()) {
                a.sort_by(|x, y| x.as_str().cmp(&y.as_str()));
            }
        }
    }
}

/// Recorded plans name a Place or an Ability without its slot number. Both sides are compared in the canonical label form (key order and Energy order never matter).
fn label_matches(engine: &str, want: &str) -> bool {
    let engine = canon_label(engine);
    let engine = engine.as_str();
    engine == want || (!want.contains('#') && engine.split('#').next() == Some(want)) || ((want.starts_with("Place:") || want.starts_with("Ability")) && !want.contains('@') && engine.split('@').next() == Some(want))
}

/// Replays a move list (labels, as pg_pos and the bots print them) from the start of the turn through the SAME step rules as the plan lister and
/// returns the key(s) of the plan it ends in (several when a slotless label fits more than one legal action). A step the list does not name but the
/// engine forces (a single legal action, for example choosing what Ilima returns) is taken; the list stops being followed at its first chance event
/// or at an attack; a list that runs out is ended with End the turn.
fn replay(st: State, labels: &[String], i: usize, last: Option<String>, out: &mut Vec<String>, depth: usize) -> Result<(), String> {
    if depth > 80 {
        return Err("more than 80 steps".into());
    }
    let (actor, mut acts) = st.generate_possible_actions();
    if actor != 0 {
        return match last {
            Some(l) => {
                out.push(leaf_key(&st, &l, &json!({"kind": "opponent_choice"})));
                Ok(())
            }
            None => Err("the opponent is to act at the start".into()),
        };
    }
    canonical_actions(&mut acts);
    let want = labels.get(i);
    let cands: Vec<Action> = acts
        .iter()
        .filter(|a| match want {
            Some(w) => label_matches(&pg_label(a, 0), w),
            None => matches!(a.action, SimpleAction::EndTurn),
        })
        .cloned()
        .collect();
    if cands.is_empty() {
        let only = acts.len() == 1 && !matches!(acts[0].action, SimpleAction::EndTurn | SimpleAction::Attack(_));
        if only {
            let a = acts[0].clone();
            return match step_kind(&st, &a, 0) {
                Kind::Child(s1) => replay(s1, labels, i, Some(pg_label(&a, 0)), out, depth + 1),
                Kind::Chance(extra) => {
                    out.push(leaf_key(&st, &pg_label(&a, 0), &extra));
                    Ok(())
                }
                _ => Err("unexpected end".into()),
            };
        }
        return Err(format!("no legal action labelled {:?} at step {} (legal: {:?})", want, i, acts.iter().map(|x| pg_label(x, 0)).collect::<Vec<_>>()));
    }
    // Every candidate is followed on its own: one that cannot follow the rest of the list (for example a slotless `Place:X` put on a slot where the later
    // `Tool:...@2` is not legal) is pruned, and the list is unfollowable only when NO candidate can follow it. (It used to give up on the first dead end.)
    let mut first_err: Option<String> = None;
    let mut any_ok = false;
    for a in cands {
        let label = pg_label(&a, 0);
        let mark = out.len();
        let r: Result<(), String> = match step_kind(&st, &a, 0) {
            Kind::Attack(info) => {
                out.push(leaf_key(&st, &label, &info));
                Ok(())
            }
            Kind::EndTurn => {
                out.push(leaf_key(&st, &label, &json!({"kind": "end_turn"})));
                Ok(())
            }
            Kind::Chance(extra) => {
                out.push(leaf_key(&st, &label, &extra));
                Ok(())
            }
            Kind::Child(s1) => replay(s1, labels, i + 1, Some(label), out, depth + 1),
        };
        match r {
            Ok(()) => any_ok = true,
            Err(e) => {
                out.truncate(mark);
                if first_err.is_none() {
                    first_err = Some(e);
                }
            }
        }
    }
    if any_ok {
        Ok(())
    } else {
        Err(first_err.unwrap_or_else(|| "no candidate could follow the move list".into()))
    }
}

fn load_decks(args: &[String]) -> HashMap<String, Deck> {
    let mut decks: HashMap<String, Deck> = HashMap::new();
    for d in arg_all(args, "--deck") {
        let (k, path) = d.split_once('=').expect("--deck KEY=path");
        decks.insert(k.to_string(), Deck::from_file(path).expect("deck file"));
    }
    decks
}

/// The position's search world: built from the position, reduced to the player's own observation, then one fixed hypothetical deck order.
fn world_of(pos: &Value, decks: &HashMap<String, Deck>, world_seed: u64) -> Result<(PlayerObservation, State), Vec<String>> {
    let deck_me = decks.get(pos["deck"].as_str().unwrap()).expect("deck key").clone();
    let deck_filler = decks.get(pos["filler"].as_str().unwrap_or(pos["deck"].as_str().unwrap())).expect("filler key").clone();
    let built = build(pos, &deck_me, &deck_filler, world_seed);
    if !built.problems.is_empty() {
        return Err(built.problems);
    }
    // From here on only the player's own view exists: the real unseen cards are dropped with `built`.
    let obs = PlayerObservation::from_state(&built.state, 0, &RevealedKnowledge::default());
    drop(built);
    let mut rng = StdRng::seed_from_u64(0x5EED_0001);
    let world = obs.search_state(&mut rng);
    Ok((obs, world))
}

/// `world_of`, plus the legal list of the built state (after canonical_actions; None when the actor is not seat 0), for the exporter.
fn world_of_export(pos: &Value, decks: &HashMap<String, Deck>, world_seed: u64) -> Result<(PlayerObservation, State, Option<Vec<Action>>), Vec<String>> {
    let deck_me = decks.get(pos["deck"].as_str().unwrap()).expect("deck key").clone();
    let deck_filler = decks.get(pos["filler"].as_str().unwrap_or(pos["deck"].as_str().unwrap())).expect("filler key").clone();
    let built = build(pos, &deck_me, &deck_filler, world_seed);
    if !built.problems.is_empty() {
        return Err(built.problems);
    }
    let (actor, mut acts) = built.state.generate_possible_actions();
    canonical_actions(&mut acts);
    let legal = if actor == 0 { Some(acts) } else { None };
    let obs = PlayerObservation::from_state(&built.state, 0, &RevealedKnowledge::default());
    drop(built);
    let mut rng = StdRng::seed_from_u64(0x5EED_0001);
    let world = obs.search_state(&mut rng);
    Ok((obs, world, legal))
}

fn proc_kb(key: &str) -> u64 {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| s.lines().find(|l| l.starts_with(key)).and_then(|l| l.split_whitespace().nth(1).and_then(|x| x.parse().ok())))
        .unwrap_or(0)
}

fn plans_line(id: &str, world_seed: u64, start: Value, plans: &[Value], total_found: usize, nodes: usize, capped: bool, depth_cut: usize, lim: &Limits) -> Value {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    Value::Array(plans.to_vec()).to_string().hash(&mut h);
    json!({"kind": "plans", "id": id, "world_seed": world_seed, "start": start, "n_plans": plans.len(), "total_found": total_found, "capped": capped, "nodes": nodes,
           "paths_cut_at_max_steps": depth_cut,
           "limits": {"max_plans": lim.max_plans, "max_nodes": lim.max_nodes, "max_steps": lim.max_steps},
           "plans_hash": format!("{:016x}", h.finish()), "plans": plans})
}

fn plan_actions_line(id: &str, plans: &[Value], ex: &Extras) -> Value {
    let items: Vec<Value> = plans
        .iter()
        .filter_map(|p| {
            let key = p["key"].as_str()?;
            let (a, f) = ex.actions.get(key)?;
            Some(json!({"n": p["n"], "key": key, "actions": a, "forced": f}))
        })
        .collect();
    json!({"kind": "plan_actions", "id": id, "plans": items})
}

fn act_str(a: &Action) -> String {
    serde_json::to_string(a).unwrap_or_default()
}

fn root_check_line(id: &str, plans: &[Value], ex: &Extras, legal: Option<&[Action]>) -> Value {
    let mut first: HashMap<String, Vec<Value>> = HashMap::new();
    for p in plans {
        if let Some((a, _)) = p["key"].as_str().and_then(|k| ex.actions.get(k)) {
            if let Some(a0) = a.first() {
                first.entry(act_str(a0)).or_default().push(p["n"].clone());
            }
        }
    }
    let mut child_first: HashMap<u64, usize> = HashMap::new();
    let mut entries = Vec::new();
    let (mut n_plan, mut n_noop, mut n_dup, mut n_no) = (0, 0, 0, 0);
    for (j, (a, h)) in ex.root.iter().enumerate() {
        let ns = first.get(&act_str(a)).cloned().unwrap_or_default();
        let mut dup: Option<usize> = None;
        let class = if !ns.is_empty() {
            n_plan += 1;
            "plan"
        } else if *h == Some(ex.root_hash) {
            n_noop += 1;
            "noop"
        } else if let Some(k) = h.and_then(|hh| child_first.get(&hh).copied()) {
            dup = Some(k);
            n_dup += 1;
            "dup_of"
        } else {
            n_no += 1;
            "no_plan"
        };
        if let Some(hh) = h {
            child_first.entry(*hh).or_insert(j);
        }
        entries.push(json!({"action": a, "class": class, "plans": ns, "dup_of": dup}));
    }
    let root_set: HashSet<String> = ex.root.iter().map(|(a, _)| act_str(a)).collect();
    let (mut missing, mut extra) = (Vec::new(), Vec::new());
    let ok = match legal {
        Some(l) => {
            let legal_set: HashSet<String> = l.iter().map(act_str).collect();
            missing = l.iter().filter(|a| !root_set.contains(&act_str(a))).cloned().collect::<Vec<_>>();
            extra = ex.root.iter().filter(|(a, _)| !legal_set.contains(&act_str(a))).map(|(a, _)| a.clone()).collect::<Vec<_>>();
            json!(missing.is_empty() && extra.is_empty() && n_no == 0)
        }
        None => Value::Null,
    };
    json!({"kind": "root_check", "id": id, "ok": ok, "n_legal": legal.map(|l| l.len()), "n_root": ex.root.len(), "n_plan": n_plan, "n_noop": n_noop,
           "n_dup_of": n_dup, "n_no_plan": n_no, "missing_in_lister": missing, "extra_in_lister": extra, "root": entries})
}

fn card_str(c: &Card) -> String {
    format!("{} {}", c.get_name(), c.get_id())
}

fn pos_board(v: &State, side: usize) -> Value {
    Value::Array(
        v.in_play_pokemon[side]
            .iter()
            .filter_map(|p| p.as_ref())
            .map(|p| {
                json!({"card": card_str(&p.card), "behind": p.cards_behind.iter().map(card_str).collect::<Vec<_>>(),
                       "tools": p.attached_tools.iter().map(card_str).collect::<Vec<_>>()})
            })
            .collect(),
    )
}

/// The position fields the prompt reads, rebuilt from the actor's observation (the inverse of `build`), seat 0 = the actor.
fn pos_like(obs: &PlayerObservation) -> Value {
    let me = obs.actor;
    let opp = 1 - me;
    let v = obs.visible_state();
    // own_knockouts_this_game is pub(crate) and turn_effects private: both are read through the State's serde form
    let sv = serde_json::to_value(v).expect("state json");
    let tc = v.turn_count;
    let mut te: Vec<Value> = Vec::new();
    if let Some(list) = sv["turn_effects"].get(tc.to_string()).and_then(|x| x.as_array()) {
        for e in list {
            let mut e = e.clone();
            if me != 0 {
                rel_seats(&mut e, me, "");
            }
            te.push(json!({"turn": tc, "effect": e}));
        }
    }
    let stadium = v
        .active_stadium
        .as_ref()
        .map(|c| json!({"card": card_str(c), "owner": v.active_stadium_owner.map(|o| rel(o, me))}))
        .unwrap_or(Value::Null);
    json!({
        "turn_count": tc,
        "stadium": stadium,
        "turn_effects": te,
        "me": {"hand": v.hands[me].iter().map(card_str).collect::<Vec<_>>(), "discard": v.discard_piles[me].iter().map(card_str).collect::<Vec<_>>(),
               "board": pos_board(v, me), "knockouts": sv["own_knockouts_this_game"][me].clone()},
        "opp": {"board": pos_board(v, opp), "discard": v.discard_piles[opp].iter().map(card_str).collect::<Vec<_>>()},
    })
}

fn problem_line(id: &str, msg: &str) -> Value {
    json!({"kind": "problem", "id": id, "problems": [msg.chars().take(300).collect::<String>()]})
}

fn panic_text(e: Box<dyn std::any::Any + Send>) -> String {
    let m = e.downcast_ref::<String>().cloned().or_else(|| e.downcast_ref::<&str>().map(|s| s.to_string())).unwrap_or_else(|| "unknown".into());
    format!("panic: {m}")
}

/// Runs one input line's work; a deserialization error or a panic becomes a problem line and the run goes on.
fn guarded<F: FnOnce() -> Result<Vec<Value>, String>>(id: &str, f: F) -> Vec<Value> {
    match std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)) {
        Ok(Ok(v)) => v,
        Ok(Err(m)) => vec![problem_line(id, &m)],
        Err(e) => vec![problem_line(id, &panic_text(e))],
    }
}

fn read_jsonl(path: &str) -> Vec<String> {
    std::fs::read_to_string(path).unwrap().lines().filter(|l| !l.trim().is_empty()).map(|l| l.to_string()).collect()
}

fn obs_of(rec: &Value) -> Result<PlayerObservation, String> {
    serde_json::from_value::<PlayerObservation>(rec["pdl_observation"].clone()).map_err(|e| format!("observation: {e}"))
}

fn obs_mode_lines(id: &str, obs: &PlayerObservation, legal: Option<Vec<Action>>, lim: &Limits, fill: u64) -> Vec<Value> {
    let t0 = std::time::Instant::now();
    let me = obs.actor;
    let world = obs.search_state(&mut StdRng::seed_from_u64(fill));
    let start = start_block(obs);
    let (plans, total_found, nodes, capped, depth_cut, ex) = list_plans(&world, lim, me);
    vec![
        plans_line(id, 1, start, &plans, total_found, nodes, capped, depth_cut, lim),
        plan_actions_line(id, &plans, &ex),
        root_check_line(id, &plans, &ex, legal.as_deref()),
        json!({"kind": "pos_like", "id": id, "pos": pos_like(obs)}),
        json!({"kind": "stats", "id": id, "secs": t0.elapsed().as_secs_f64(), "vmhwm_kb": proc_kb("VmHWM:"), "vmpeak_kb": proc_kb("VmPeak:"), "fill_seed": fill}),
    ]
}

fn run_observations(file: &str, args: &[String], lim: &Limits) {
    let fill: u64 = arg(args, "--fill-seed").map(|x| x.parse().unwrap()).unwrap_or(0x5EED_0001);
    for line in read_jsonl(file) {
        let rec: Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                println!("{}", problem_line("?", &format!("input line: {e}")));
                continue;
            }
        };
        let id = rec["id"].as_str().unwrap_or("?").to_string();
        let out = guarded(&id, || {
            let obs = obs_of(&rec)?;
            let legal: Option<Vec<Action>> = match rec.get("legal_actions") {
                None | Some(Value::Null) => None,
                Some(v) => Some(serde_json::from_value(v.clone()).map_err(|e| format!("legal_actions: {e}"))?),
            };
            Ok(obs_mode_lines(&id, &obs, legal, lim, fill))
        });
        for l in out {
            println!("{l}");
        }
    }
}

fn trace_one(id: &str, rec: &Value) -> Result<Value, String> {
    let obs = obs_of(rec)?;
    let actions: Vec<Action> = serde_json::from_value(rec["actions"].clone()).map_err(|e| format!("actions: {e}"))?;
    let me = obs.actor;
    let mut st = obs.search_state(&mut StdRng::seed_from_u64(0x5EED_0001));
    let mut steps: Vec<Value> = Vec::new();
    let mut ended = false;
    for (i, act) in actions.iter().enumerate() {
        if ended {
            return Ok(json!({"kind": "trace", "id": id, "ok": false, "error": format!("step {i} follows a step that ended the plan"), "steps": steps}));
        }
        let (actor, mut acts) = st.generate_possible_actions();
        let fail = |m: String, steps: &Vec<Value>| json!({"kind": "trace", "id": id, "ok": false, "error": m, "steps": steps});
        if actor != me {
            return Ok(fail(format!("step {i}: the actor is {actor}, not {me}"), &steps));
        }
        canonical_actions(&mut acts);
        let forced = acts.len() == 1;
        if !acts.contains(act) {
            return Ok(fail(format!("step {i}: action is not among the node's canonical actions"), &steps));
        }
        match step_kind(&st, act, me) {
            Kind::Attack(_) => {
                steps.push(json!({"forced": forced, "end": "attack", "actor_after": Value::Null, "hash_after": Value::Null}));
                ended = true;
            }
            Kind::EndTurn => {
                steps.push(json!({"forced": forced, "end": "end_turn", "actor_after": Value::Null, "hash_after": Value::Null}));
                ended = true;
            }
            Kind::Chance(_) => {
                steps.push(json!({"forced": forced, "end": "chance", "actor_after": Value::Null, "hash_after": Value::Null}));
                ended = true;
            }
            Kind::Child(s1) => {
                let (a2, _) = s1.generate_possible_actions();
                if a2 == me {
                    let h = obs_hash(&PlayerObservation::from_state(&s1, me, &obs.revealed));
                    steps.push(json!({"forced": forced, "end": "child", "actor_after": a2, "hash_after": format!("{h:016x}")}));
                } else {
                    steps.push(json!({"forced": forced, "end": "opponent_choice", "actor_after": a2, "hash_after": Value::Null}));
                    ended = true;
                }
                st = s1;
            }
        }
    }
    Ok(json!({"kind": "trace", "id": id, "ok": true, "error": Value::Null, "steps": steps}))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let lim = Limits {
        max_plans: arg(&args, "--max-plans").map(|x| x.parse().unwrap()).unwrap_or(2000),
        max_nodes: arg(&args, "--max-nodes").map(|x| x.parse().unwrap()).unwrap_or(200_000),
        max_steps: arg(&args, "--max-steps").map(|x| x.parse().unwrap()).unwrap_or(30),
    };
    if let Some(file) = arg(&args, "--observations") {
        run_observations(&file, &args, &lim);
        return;
    }
    if let Some(file) = arg(&args, "--trace") {
        for line in read_jsonl(&file) {
            let rec: Value = match serde_json::from_str(&line) {
                Ok(v) => v,
                Err(e) => {
                    println!("{}", problem_line("?", &format!("input line: {e}")));
                    continue;
                }
            };
            let id = rec["id"].as_str().unwrap_or("?").to_string();
            let out = match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| trace_one(&id, &rec))) {
                Ok(Ok(v)) => v,
                Ok(Err(m)) => json!({"kind": "trace", "id": id, "ok": false, "error": m.chars().take(300).collect::<String>(), "steps": []}),
                Err(e) => json!({"kind": "trace", "id": id, "ok": false, "error": panic_text(e).chars().take(300).collect::<String>(), "steps": []}),
            };
            println!("{out}");
        }
        return;
    }
    if let Some(file) = arg(&args, "--obs-hash") {
        for line in read_jsonl(&file) {
            let rec: Value = match serde_json::from_str(&line) {
                Ok(v) => v,
                Err(e) => {
                    println!("{}", problem_line("?", &format!("input line: {e}")));
                    continue;
                }
            };
            let id = rec["id"].as_str().unwrap_or("?").to_string();
            let out = guarded(&id, || {
                let obs = obs_of(&rec)?;
                Ok(vec![json!({"kind": "obs_hash", "id": id, "hash": format!("{:016x}", obs_hash(&obs))})])
            });
            for l in out {
                println!("{l}");
            }
        }
        return;
    }
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--positions").expect("--positions")).unwrap()).unwrap();
    let decks = load_decks(&args);
    let only = arg_all(&args, "--only");
    let world_seed: u64 = arg(&args, "--world-seed").map(|x| x.parse().unwrap()).unwrap_or(1);
    let emit = args.iter().any(|a| a == "--emit-actions");
    let mut export_file = arg(&args, "--export-observations").map(|p| std::fs::File::create(p).expect("export file"));
    if let Some(file) = arg(&args, "--replay") {
        // --replay FILE.jsonl: one {"id", "tag", "labels": [...]} per line -> {"kind":"replay", "id", "tag", "ok", "keys": [...], "error"}
        let by_id: HashMap<String, &Value> = positions.iter().map(|p| (p["id"].as_str().unwrap().to_string(), p)).collect();
        let mut worlds: HashMap<String, Result<State, Vec<String>>> = HashMap::new();
        for line in std::fs::read_to_string(file).unwrap().lines().filter(|l| !l.trim().is_empty()) {
            let req: Value = serde_json::from_str(line).unwrap();
            let id = req["id"].as_str().unwrap().to_string();
            let labels: Vec<String> = req["labels"].as_array().unwrap().iter().map(|x| canon_label(x.as_str().unwrap())).collect();
            let world = worlds
                .entry(id.clone())
                .or_insert_with(|| match by_id.get(&id) {
                    Some(pos) => world_of(pos, &decks, world_seed).map(|(_, w)| w),
                    None => Err(vec![format!("unknown position {id}")]),
                })
                .clone();
            let res = world.map_err(|p| p.join("; ")).and_then(|w| {
                let mut out = Vec::new();
                replay(w, &labels, 0, None, &mut out, 0).map(|_| out)
            });
            match res {
                Ok(keys) => println!("{}", json!({"kind": "replay", "id": id, "tag": req["tag"], "ok": true, "keys": keys})),
                Err(e) => println!("{}", json!({"kind": "replay", "id": id, "tag": req["tag"], "ok": false, "keys": [], "error": e})),
            }
        }
        return;
    }
    for pos in &positions {
        let id = pos["id"].as_str().unwrap().to_string();
        if !only.is_empty() && !only.contains(&id) {
            continue;
        }
        let (obs, world, legal) = if export_file.is_some() || emit {
            match world_of_export(pos, &decks, world_seed) {
                Ok(x) => x,
                Err(problems) => {
                    println!("{}", json!({"kind": "problem", "id": id, "problems": problems}));
                    continue;
                }
            }
        } else {
            match world_of(pos, &decks, world_seed) {
                Ok((o, w)) => (o, w, None),
                Err(problems) => {
                    println!("{}", json!({"kind": "problem", "id": id, "problems": problems}));
                    continue;
                }
            }
        };
        if let Some(f) = export_file.as_mut() {
            use std::io::Write;
            writeln!(f, "{}", json!({"id": id, "pdl_observation": obs, "legal_actions": legal})).expect("write export");
            f.flush().expect("flush export");
        }
        let start = start_block(&obs);
        let (plans, total_found, nodes, capped, depth_cut, ex) = list_plans(&world, &lim, 0);
        println!("{}", plans_line(&id, world_seed, start, &plans, total_found, nodes, capped, depth_cut, &lim));
        if emit {
            println!("{}", plan_actions_line(&id, &plans, &ex));
            println!("{}", root_check_line(&id, &plans, &ex, legal.as_deref()));
        }
    }
}
