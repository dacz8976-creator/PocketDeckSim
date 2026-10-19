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
fn pg_label(a: &Action) -> String {
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
        SimpleAction::Activate { player, in_play_idx } => format!("Activate:{}@{}", player, in_play_idx),
        SimpleAction::Promote { player, in_play_idx } => format!("Promote:{}@{}", player, in_play_idx),
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
        _ => format!("{} (a choice)", pg_label(a)),
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
    let mut unseen: BTreeMap<String, u32> = BTreeMap::new();
    for c in &obs.known_own_deck {
        *unseen.entry(c.get_name()).or_insert(0) += 1;
    }
    json!({
        "turn_count": v.turn_count,
        "points": v.points,
        "stadium": v.active_stadium.as_ref().map(|c| c.get_name()),
        "stadium_owner": v.active_stadium_owner,
        "energy_zone": [v.energy_zone[0].current.map(|e| format!("{e:?}")), v.energy_zone[0].next.map(|e| format!("{e:?}"))],
        "me": {"board": board_lines(v, 0), "hand": names(&v.hands[0]), "discard": names(&v.discard_piles[0]), "discard_energy": energy_names(&v.discard_energies[0]),
               "deck_size": obs.known_own_deck.len(), "unseen_deck": unseen},
        "opp": {"board": board_lines(v, 1), "hand_count": v.hands[1].len(), "deck_count": v.decks[1].cards.len(), "discard": names(&v.discard_piles[1]),
                "discard_energy": energy_names(&v.discard_energies[1])},
    })
}

/// The State as JSON with every list whose ORDER carries no meaning put in a fixed order: hands, discard piles, discarded Energy, and each
/// Pokémon's attached Energy and Tools. Two plans that only differ in the order cards sit in such a list reach the same visible state.
/// (Own deck order is left alone: a plan never touches it, because it stops at the first draw.)
fn canonical_state_json(st: &State) -> Value {
    let mut v = serde_json::to_value(st).expect("state json"); // serde_json maps are sorted, so equal states give equal text
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
    v
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
fn diff_lines(a: &State, b: &State) -> Vec<String> {
    let mut out = Vec::new();
    for (side, who) in [(1usize, "Opponent"), (0usize, "You")] {
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
        out.push(format!("Points: you {} -> {}, opponent {} -> {}", a.points[0], b.points[0], a.points[1], b.points[1]));
    }
    out
}

type Path = Vec<(String, String)>; // (pg label, english)

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
    fn add(&mut self, before: &State, path: &Path, last: (String, String), end: &str, extra: Value) {
        let key = leaf_key(before, &last.0, &extra);
        if self.debug {
            let look = format!("{}|{}|{:?}|{:?}", last.0, extra, board_lines(before, 0), names(&before.hands[0]));
            let sv = canonical_state_json(before);
            if let Some(prev) = self.look_alike.get(&look) {
                if *prev != sv {
                    let mut d = Vec::new();
                    json_diff(prev, &sv, "state", &mut d);
                    eprintln!("SPLIT {} :: {}", path.iter().map(|p| p.0.clone()).chain(std::iter::once(last.0.clone())).collect::<Vec<_>>().join(" > "), d.join(" | "));
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
        let mut labels: Vec<String> = path.iter().map(|p| p.0.clone()).collect();
        let mut steps: Vec<String> = path.iter().map(|p| p.1.clone()).collect();
        labels.push(last.0);
        steps.push(last.1);
        self.plans.push(json!({
            "key": key, "labels": labels, "steps": steps, "n_steps": labels.len(), "end": end, "final": extra,
            "result": {"board": board_lines(before, 0), "hand": names(&before.hands[0]), "points": before.points,
                       "deck_size": before.decks[0].cards.len()},
        }));
    }
}

fn attack_info(st: &State, act: &Action) -> Value {
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
            let lines = diff_lines(&st2, &s1);
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
fn step_kind(st: &State, act: &Action) -> Kind {
    let me = 0usize;
    match &act.action {
        SimpleAction::Attack(_) => Kind::Attack(attack_info(st, act)),
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

fn list_plans(world: &State, lim: &Limits) -> (Vec<Value>, usize, usize, bool, usize) {
    let me = 0usize;
    let mut col = Collector {
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
        if path.len() >= lim.max_steps {
            deepest_cut += 1;
            col.capped = true;
            continue;
        }
        canonical_actions(&mut acts);
        for act in acts {
            let label = pg_label(&act);
            let text = english(&st, &act);
            match step_kind(&st, &act) {
                Kind::Attack(info) => col.add(&st, &path, (label, text), "attack", info),
                Kind::EndTurn => col.add(&st, &path, (label, text), "end_turn", json!({"kind": "end_turn"})),
                Kind::Chance(extra) => col.add(&st, &path, (label, text), "chance", extra),
                Kind::Child(s1) => {
                    if seen.insert(state_hash(&s1)) {
                        let mut p2 = path.clone();
                        p2.push((label, text));
                        q.push_back((s1, p2));
                    }
                }
            }
        }
    }
    let Collector { mut plans, total_found, capped, .. } = col;
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
    (plans, total_found, nodes, capped, deepest_cut)
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
            Some(w) => label_matches(&pg_label(a), w),
            None => matches!(a.action, SimpleAction::EndTurn),
        })
        .cloned()
        .collect();
    if cands.is_empty() {
        let only = acts.len() == 1 && !matches!(acts[0].action, SimpleAction::EndTurn | SimpleAction::Attack(_));
        if only {
            let a = acts[0].clone();
            return match step_kind(&st, &a) {
                Kind::Child(s1) => replay(s1, labels, i, Some(pg_label(&a)), out, depth + 1),
                Kind::Chance(extra) => {
                    out.push(leaf_key(&st, &pg_label(&a), &extra));
                    Ok(())
                }
                _ => Err("unexpected end".into()),
            };
        }
        return Err(format!("no legal action labelled {:?} at step {} (legal: {:?})", want, i, acts.iter().map(pg_label).collect::<Vec<_>>()));
    }
    // Every candidate is followed on its own: one that cannot follow the rest of the list (for example a slotless `Place:X` put on a slot where the later
    // `Tool:...@2` is not legal) is pruned, and the list is unfollowable only when NO candidate can follow it. (It used to give up on the first dead end.)
    let mut first_err: Option<String> = None;
    let mut any_ok = false;
    for a in cands {
        let label = pg_label(&a);
        let mark = out.len();
        let r: Result<(), String> = match step_kind(&st, &a) {
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

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--positions").expect("--positions")).unwrap()).unwrap();
    let decks = load_decks(&args);
    let only = arg_all(&args, "--only");
    let world_seed: u64 = arg(&args, "--world-seed").map(|x| x.parse().unwrap()).unwrap_or(1);
    let lim = Limits {
        max_plans: arg(&args, "--max-plans").map(|x| x.parse().unwrap()).unwrap_or(2000),
        max_nodes: arg(&args, "--max-nodes").map(|x| x.parse().unwrap()).unwrap_or(200_000),
        max_steps: arg(&args, "--max-steps").map(|x| x.parse().unwrap()).unwrap_or(30),
    };
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
        let (obs, world) = match world_of(pos, &decks, world_seed) {
            Ok(x) => x,
            Err(problems) => {
                println!("{}", json!({"kind": "problem", "id": id, "problems": problems}));
                continue;
            }
        };
        let start = start_block(&obs);
        let (plans, total_found, nodes, capped, depth_cut) = list_plans(&world, &lim);
        let mut h = std::collections::hash_map::DefaultHasher::new();
        Value::Array(plans.clone()).to_string().hash(&mut h);
        println!(
            "{}",
            json!({"kind": "plans", "id": id, "world_seed": world_seed, "start": start, "n_plans": plans.len(), "total_found": total_found, "capped": capped, "nodes": nodes,
                   "paths_cut_at_max_steps": depth_cut,
                   "limits": {"max_plans": lim.max_plans, "max_nodes": lim.max_nodes, "max_steps": lim.max_steps},
                   "plans_hash": format!("{:016x}", h.finish()), "plans": plans})
        );
    }
}
