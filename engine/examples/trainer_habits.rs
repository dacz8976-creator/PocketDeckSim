//! km3's late Trainer play (Oct 5; Fable via Dustin; rl/results/playout_trainer_habits_2026-10-05/README.md): Copycat,
//! the Tools (Elegant Cape, Giant Cape, Rocky Helmet, Protective Poncho) and the heal Supporters (Irida, Pokémon Center
//! Lady, Erika), recorded with the hand and board around each play. A read-only diagnosis: it replays games and play-outs
//! exactly as they were played (km3 on both sides) and only watches; nothing in the engine or the players changes.
//!   trainer_habits games --games <games.jsonl> --manifest <manifest.json> --out events.jsonl [--arm ref] [--limit N]
//!     The development run's games of one arm (ref: km3 on both sides), rebuilt as the strength harness builds them
//!     (`Game::new(create_players(seat 0's list, seat 1's list, [km3, km3]), seed)`) and checked against the run's own log:
//!     the deck's labels, points, turns and winner must match, or the game is reported as not replayed.
//!   trainer_habits playouts --plans <plans.json> --states <dir> --study <study.jsonl> --deck <list> --opponent <list>
//!       --rounds 128 --seed-base 24200001000 --out events.jsonl
//!     The continuation study's km3 continuations of both first moves at each position: the same LAB worlds and seeds as
//!     kx3's `evaluate` (rebuilt here), each play-out checked against the study's final-state digest.
//! Every event is one JSON line: the context, the player, the turn, the hand and board before, and what followed.
use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;

use deckgym::actions::{Action, SimpleAction};
use deckgym::models::{Card, EnergyType, TrainerType};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::{create_players, PlayerCode};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::seq::SliceRandom;
use rand::{rngs::StdRng, RngCore, SeedableRng};
use rayon::prelude::*;
use serde_json::{json, Value};

const TOOLS: [&str; 4] = ["Elegant Cape", "Giant Cape", "Rocky Helmet", "Protective Poncho"];
const HEALS: [&str; 3] = ["Irida", "Pokémon Center Lady", "Erika"];

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn fnv1a64(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ *b as u64).wrapping_mul(0x0000_0100_0000_01b3))
}

fn splitmix(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9e37_79b9_7f4a_7c15);
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    x ^ (x >> 31)
}

/// The strength harness's action label (rl/strength/src/main.rs `label`), for the replay check.
fn label(a: &Action) -> String {
    let nm = |c: &Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::Attack(at) => format!("Attack:{}", at.title),
        SimpleAction::Retreat(i) => format!("Retreat:{}", i),
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("Tool:{}@{}", nm(tool_card), in_play_idx),
        SimpleAction::EndTurn => "EndTurn".to_string(),
        _ => String::new(),
    }
}

fn damage(state: &State, player: usize, idx: usize) -> u64 {
    state.in_play_pokemon[player][idx]
        .as_ref()
        .map_or(0, |p| serde_json::to_value(p).ok().and_then(|v| v["damage_counters"].as_u64()).unwrap_or(0))
}

fn conditions(state: &State, player: usize, idx: usize) -> bool {
    state.in_play_pokemon[player][idx]
        .as_ref()
        .is_some_and(|p| p.is_poisoned() || p.is_paralyzed() || p.is_asleep() || p.is_burned() || p.is_confused())
}

/// The board of one player, as names (Active first), with remaining HP, damage and Energy count.
fn board(state: &State, player: usize) -> Vec<Value> {
    (0..4)
        .filter_map(|i| {
            state.in_play_pokemon[player][i].as_ref().map(|p| {
                json!({"slot": i, "name": p.get_name(), "hp": p.get_remaining_hp(), "damage": damage(state, player, i),
                       "energy": p.attached_energy.len(), "tools": p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>()})
            })
        })
        .collect()
}

/// A Pokémon card whose attacks the deck's Energy can pay (every symbol Colorless or one of the deck's types).
fn energy_matching(card: &Card, types: &[EnergyType]) -> bool {
    match card {
        Card::Pokemon(p) => p
            .attacks
            .iter()
            .any(|a| a.energy_required.iter().all(|e| *e == EnergyType::Colorless || types.contains(e))),
        _ => false,
    }
}

fn is_supporter(card: &Card) -> bool {
    matches!(card, Card::Trainer(t) if t.trainer_card_type == TrainerType::Supporter)
}

/// A hand, card by card: whether each card is playable now (a legal action of the decision uses it), or next turn (an
/// evolution of a Pokémon in play; a Supporter when the one-Supporter-a-turn rule is what stops it now, i.e. after a
/// Supporter this turn), a Supporter, and an Energy-matching Pokémon.
fn hand_profile(state: &State, player: usize, hand: &[Card], legal: &[Action], supporter_used: bool, types: &[EnergyType]) -> Value {
    let mut usable: BTreeSet<String> = BTreeSet::new();
    for a in legal.iter().filter(|a| a.actor == player) {
        match &a.action {
            SimpleAction::Play { trainer_card } => {
                usable.insert(trainer_card.id.clone());
            }
            SimpleAction::Place(c, _) => {
                usable.insert(c.get_id());
            }
            SimpleAction::Evolve { evolution, .. } => {
                usable.insert(evolution.get_id());
            }
            _ => {}
        }
    }
    let in_play: BTreeSet<String> = state.in_play_pokemon[player].iter().flatten().map(|p| p.get_name()).collect();
    let (mut now, mut next, mut supporters, mut matching) = (0, 0, 0, 0);
    let cards: Vec<Value> = hand
        .iter()
        .map(|c| {
            let playable_now = usable.contains(&c.get_id());
            let evolution_ready = matches!(c, Card::Pokemon(p) if p.evolves_from.as_ref().is_some_and(|f| in_play.contains(f)));
            let playable_next = !playable_now && (evolution_ready || (is_supporter(c) && supporter_used));
            now += playable_now as usize;
            next += playable_next as usize;
            supporters += is_supporter(c) as usize;
            matching += energy_matching(c, types) as usize;
            json!({"card": c.get_name(), "now": playable_now, "next": playable_next})
        })
        .collect();
    json!({"size": hand.len(), "playable_now": now, "playable_next": next, "supporters": supporters,
           "energy_matching_pokemon": matching, "cards": cards})
}

/// A Tool on the board, followed until its carrier leaves play or the game ends.
struct ToolTrack {
    event: Value,
    owner: usize,
    tool: Card,
    turn: usize,
    attacks: Vec<usize>,
    /// When and how the Tool's time on the board ended: its carrier knocked out, the Tool discarded (an opponent's
    /// Field Blower-like effect; the Pokémon stays), or some other way out of play.
    left: Option<(usize, &'static str)>,
    carrier: String,
}

/// A play whose effect resolves through a later choice (a heal's target): finished at the first state with no pending
/// choice.
struct Pending {
    event: Value,
    player: usize,
    before: State,
}

fn carrier_of(state: &State, owner: usize, tool: &Card) -> Option<usize> {
    (0..4).find(|&i| state.in_play_pokemon[owner][i].as_ref().is_some_and(|p| p.attached_tools.contains(tool)))
}

/// Plays `game` to the end (or `limit` ticks), watching every tick: the events, the final state, and the label of every real
/// decision (more than one legal move) with its actor.
fn watch(game: &mut Game, ctx: &Value, types: [Vec<EnergyType>; 2], decks: [String; 2], limit: usize) -> (Vec<Value>, State, Vec<(usize, String)>) {
    let mut events = Vec::new();
    let mut labels = Vec::new();
    let mut tools: Vec<ToolTrack> = Vec::new();
    let mut pending: Vec<Pending> = Vec::new();
    let mut ticks = 0;
    while !game.is_game_over() && ticks < limit {
        let before = game.get_state_clone();
        let (actor, legal) = before.generate_possible_actions();
        let a = game.play_tick();
        ticks += 1;
        let after = game.get_state_clone();
        if legal.len() > 1 {
            labels.push((actor, label(&a)));
        }
        let p = a.actor;
        let turn = before.turn_count as usize;
        let base = |kind: &str| {
            json!({"kind": kind, "ctx": ctx, "player": p, "deck": decks[p], "turn": turn, "points": [before.points[p], before.points[1 - p]],
                   "deck_left": before.decks[p].cards.len(), "opp_hand": before.hands[1 - p].len(),
                   "board": board(&before, p), "opp_board": board(&before, 1 - p), "legal": legal.len()})
        };
        match &a.action {
            SimpleAction::Play { trainer_card } if trainer_card.name == "Copycat" => {
                let mut hand = before.hands[p].clone();
                if let Some(i) = hand.iter().position(|c| matches!(c, Card::Trainer(t) if t.name == "Copycat")) {
                    hand.remove(i);
                }
                let mut e = base("copycat");
                e["hand_before"] = hand_profile(&before, p, &hand, &legal, false, &types[p]);
                pending.push(Pending { event: e, player: p, before: before.clone() });
            }
            SimpleAction::Play { trainer_card } if HEALS.contains(&trainer_card.name.as_str()) => {
                let mut e = base("heal");
                e["card"] = json!(trainer_card.name);
                // What the card could heal here, by its text.
                let own: Vec<usize> = (0..4).filter(|&i| before.in_play_pokemon[p][i].is_some()).collect();
                let potential: u64 = match trainer_card.name.as_str() {
                    "Irida" => own
                        .iter()
                        .filter(|&&i| before.in_play_pokemon[p][i].as_ref().unwrap().attached_energy.contains(&EnergyType::Water))
                        .map(|&i| damage(&before, p, i).min(40))
                        .sum(),
                    "Pokémon Center Lady" => own.iter().map(|&i| damage(&before, p, i).min(30)).max().unwrap_or(0),
                    _ => own
                        .iter()
                        .filter(|&&i| matches!(&before.in_play_pokemon[p][i].as_ref().unwrap().card, Card::Pokemon(pc) if pc.energy_type == EnergyType::Grass))
                        .map(|&i| damage(&before, p, i).min(50))
                        .max()
                        .unwrap_or(0),
                };
                e["potential"] = json!(potential);
                e["board_damage"] = json!(own.iter().map(|&i| damage(&before, p, i)).sum::<u64>());
                e["conditions"] = json!(own.iter().any(|&i| conditions(&before, p, i)));
                let mut hand = before.hands[p].clone();
                if let Some(i) = hand.iter().position(|c| matches!(c, Card::Trainer(t) if t.name == trainer_card.name)) {
                    hand.remove(i);
                }
                e["hand_before"] = hand_profile(&before, p, &hand, &legal, false, &types[p]);
                pending.push(Pending { event: e, player: p, before: before.clone() });
            }
            SimpleAction::AttachTool { in_play_idx, tool_card } if TOOLS.contains(&tool_card.get_name().as_str()) => {
                let mut e = base("tool");
                let carrier = before.in_play_pokemon[p][*in_play_idx].as_ref().unwrap();
                let (stage, ex) = match &carrier.card {
                    Card::Pokemon(pc) => (pc.stage, pc.name.ends_with(" ex")),
                    _ => (0, false),
                };
                let can_attack_now = matches!(&carrier.card, Card::Pokemon(pc) if pc.attacks.iter().any(|at| {
                    let mut need: BTreeMap<EnergyType, usize> = BTreeMap::new();
                    for e in &at.energy_required { *need.entry(*e).or_default() += 1; }
                    let colorless = need.remove(&EnergyType::Colorless).unwrap_or(0);
                    let mut have: BTreeMap<EnergyType, usize> = BTreeMap::new();
                    for e in &carrier.attached_energy { *have.entry(*e).or_default() += 1; }
                    need.iter().all(|(t, n)| have.get(t).copied().unwrap_or(0) >= *n) && carrier.attached_energy.len() >= at.energy_required.len().max(colorless)
                }));
                e["tool"] = json!(tool_card.get_name());
                e["carrier"] = json!({"name": carrier.get_name(), "slot": in_play_idx, "stage": stage, "ex": ex,
                                      "hp": carrier.get_remaining_hp(), "energy": carrier.attached_energy.len(), "can_attack_now": can_attack_now,
                                      "has_attacks": matches!(&carrier.card, Card::Pokemon(pc) if !pc.attacks.is_empty())});
                tools.push(ToolTrack { event: e, owner: p, tool: tool_card.clone(), turn, attacks: Vec::new(), left: None, carrier: carrier.get_name() });
            }
            SimpleAction::Attack(_) => {
                for t in tools.iter_mut().filter(|t| t.owner == p && t.left.is_none()) {
                    if carrier_of(&before, p, &t.tool) == Some(0) {
                        t.attacks.push(turn);
                    }
                }
            }
            _ => {}
        }
        // A carrier that left play: knocked out if its Pokémon card went to the discard pile at this tick.
        for t in tools.iter_mut().filter(|t| t.left.is_none()) {
            if let Some(i) = carrier_of(&before, t.owner, &t.tool) {
                t.carrier = before.in_play_pokemon[t.owner][i].as_ref().unwrap().get_name();
                if carrier_of(&after, t.owner, &t.tool).is_none() {
                    let count = |s: &State| s.discard_piles[t.owner].iter().filter(|c| c.get_name() == t.carrier).count();
                    let how = if matches!(a.action, SimpleAction::DiscardToolFromPokemon { .. }) {
                        "tool discarded"
                    } else if count(&after) > count(&before) {
                        "knocked out"
                    } else {
                        "other"
                    };
                    t.left = Some((turn, how));
                }
            }
        }
        if after.move_generation_stack.is_empty() {
            for done in pending.drain(..) {
                let mut e = done.event;
                let p = done.player;
                if e["kind"] == "copycat" {
                    let next_legal = if after.current_player == p { after.generate_possible_actions().1 } else { Vec::new() };
                    e["hand_after"] = hand_profile(&after, p, &after.hands[p].clone(), &next_legal, true, &types[p]);
                } else {
                    let healed: u64 = (0..4).map(|i| damage(&done.before, p, i).saturating_sub(damage(&after, p, i))).sum();
                    e["healed"] = json!(healed);
                }
                events.push(e);
            }
        }
    }
    let end = game.get_state_clone();
    for t in tools {
        let mut e = t.event;
        let w = t.turn + 2;
        e["attacks"] = json!(t.attacks);
        e["attacked_within_2"] = json!(t.attacks.iter().any(|&a| a <= w));
        e["ended"] = json!(t.left.map(|(turn, how)| json!({"turn": turn, "how": how})));
        e["knocked_out_within_2"] = json!(t.left.is_some_and(|(turn, how)| how == "knocked out" && turn <= w));
        // Attacks are counted while it carries the Tool.
        e["never_attacked"] = json!(t.attacks.is_empty());
        e["game_end_turn"] = json!(end.turn_count);
        events.push(e);
    }
    for e in events.iter_mut() {
        e["winner"] = json!(match end.winner {
            Some(GameOutcome::Win(w)) if w as u64 == e["player"].as_u64().unwrap() => "player",
            Some(GameOutcome::Win(_)) => "opponent",
            _ => "tie",
        });
    }
    (events, end, labels)
}

/// A list's Energy types (the field is private; the list serializes it).
fn energy_types(deck: &Deck) -> Vec<EnergyType> {
    serde_json::from_value(serde_json::to_value(deck).unwrap()["energy_types"].clone()).unwrap()
}

fn km3_pair(d0: &Deck, d1: &Deck) -> Vec<Box<dyn deckgym::players::Player>> {
    let code = PlayerCode::KM { max_depth: 3 };
    create_players(d0.clone(), d1.clone(), vec![code.clone(), code])
}

fn games(args: &[String]) {
    let manifest: Value = serde_json::from_str(&std::fs::read_to_string(arg(args, "--manifest").unwrap()).unwrap()).unwrap();
    let arm = arg(args, "--arm").unwrap_or_else(|| "ref".into());
    let limit: usize = arg(args, "--limit").map_or(usize::MAX, |n| n.parse().unwrap());
    let lists: BTreeMap<String, Deck> = manifest["decks"]
        .as_array()
        .unwrap()
        .iter()
        .chain(manifest["opponents"].as_array().unwrap())
        .map(|d| (d["name"].as_str().unwrap().to_string(), Deck::from_file(d["path"].as_str().unwrap()).unwrap()))
        .collect();
    let records: Vec<Value> = std::fs::read_to_string(arg(args, "--games").unwrap())
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str::<Value>(l).unwrap())
        .filter(|g| g["arm"] == arm.as_str())
        .take(limit)
        .collect();
    assert!(records.iter().all(|g| g["pilot_deck"] == "km3" && g["pilot_opp"] == "km3"), "the arm must be km3 on both sides");
    let results: Vec<(Vec<Value>, Value)> = records
        .par_iter()
        .map(|g| {
            let (dn, on) = (g["deck"].as_str().unwrap(), g["opp"].as_str().unwrap());
            let seat = g["seat"].as_u64().unwrap() as usize;
            let seed = g["seed"].as_u64().unwrap();
            let (dd, od) = (&lists[dn], &lists[on]);
            let (d0, d1) = if seat == 0 { (dd, od) } else { (od, dd) };
            let names = if seat == 0 { [dn.to_string(), on.to_string()] } else { [on.to_string(), dn.to_string()] };
            let mut game = Game::new(km3_pair(d0, d1), seed);
            let ctx = json!({"source": "game", "key": g["key"], "seed": seed, "deck_seat": seat});
            let (events, end, labels) = watch(&mut game, &ctx, [energy_types(d0), energy_types(d1)], names, usize::MAX);
            // The replay check: the deck's logged labels (of the kinds labelled here), points, turns and winner.
            let logged: Vec<String> = g["log"]
                .as_array()
                .unwrap()
                .iter()
                .map(|e| e["a"].as_str().unwrap().to_string())
                .filter(|l| ["Play:", "Place:", "Evolve:", "Attack:", "Retreat:", "Tool:", "EndTurn"].iter().any(|k| l.starts_with(k)))
                .collect();
            let replayed: Vec<String> = labels.iter().filter(|(a, l)| *a == seat && !l.is_empty()).map(|(_, l)| l.clone()).collect();
            let winner = match end.winner {
                Some(GameOutcome::Win(w)) if w == seat => "deck",
                Some(GameOutcome::Win(_)) => "opp",
                _ => "tie",
            };
            let same = logged == replayed
                && g["points"] == json!([end.points[seat], end.points[1 - seat]])
                && g["turns"].as_u64() == Some(end.turn_count as u64)
                && g["winner"] == winner;
            (events, json!({"key": g["key"], "replayed_exactly": same, "labels_logged": logged.len(), "labels_replayed": replayed.len()}))
        })
        .collect();
    write_out(args, results);
}

/// The study's LAB world j at a decision (`PlayoutPlayer::sample_round` with LAB, rebuilt from its public parts).
fn lab_world(observation: &PlayerObservation, exact: &Deck, base: u64, j: usize) -> (State, Deck, u64) {
    let mut rng = StdRng::seed_from_u64(splitmix(base.wrapping_add(j as u64)));
    let state = observation.visible_state();
    let opponent = 1 - observation.actor;
    let mut seen: Vec<Card> = Vec::new();
    for pokemon in state.in_play_pokemon[opponent].iter().flatten() {
        seen.push(pokemon.card.clone());
        seen.extend(pokemon.cards_behind.iter().cloned());
        seen.extend(pokemon.attached_tools.iter().cloned());
    }
    seen.extend(state.discard_piles[opponent].iter().cloned());
    if state.active_stadium_owner == Some(opponent) {
        seen.extend(state.active_stadium.iter().cloned());
    }
    seen.retain(|c| !c.is_unknown());
    let mut list = exact.clone();
    let mut matched = vec![false; list.cards.len()];
    let mut pending = Vec::new();
    for card in &seen {
        match (0..list.cards.len()).find(|&i| !matched[i] && list.cards[i] == *card) {
            Some(i) => matched[i] = true,
            None => pending.push(card),
        }
    }
    for card in pending {
        if let Some(i) = (0..list.cards.len()).find(|&i| !matched[i] && list.cards[i].get_name() == card.get_name()) {
            list.cards[i] = card.clone();
            matched[i] = true;
        }
    }
    let mut world = observation.search_state_with_opponent_list(&mut rng, &list);
    let named: Vec<Card> = list.cards.iter().filter(|c| !c.is_unknown()).cloned().collect();
    let mut slots: Vec<&mut Card> = world.hands[opponent].iter_mut().chain(world.decks[opponent].cards.iter_mut()).collect();
    for slot in slots.iter_mut().filter(|c| c.is_unknown()) {
        **slot = named.choose(&mut rng).cloned().unwrap_or(Card::Unknown);
    }
    assert!(world.turn_count > 0, "the positions are past setup");
    world.setup_opponent_hidden = false;
    (world, list, splitmix(base ^ 0x5eed_0000_0000_0000 ^ j as u64))
}

fn playouts(args: &[String]) {
    #[derive(serde::Deserialize)]
    struct Entry {
        id: String,
        first_move: deckgym::players::playout_player::Step,
        rival: deckgym::players::playout_player::Step,
    }
    let entries: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(args, "--plans").unwrap()).unwrap()).unwrap();
    let states = arg(args, "--states").unwrap();
    let deck = Deck::from_file(&arg(args, "--deck").unwrap()).unwrap();
    let opponent = Deck::from_file(&arg(args, "--opponent").unwrap()).unwrap();
    let rounds: usize = arg(args, "--rounds").map_or(128, |r| r.parse().unwrap());
    let seed_base: u64 = arg(args, "--seed-base").map_or(24_200_001_000, |s| s.parse().unwrap());
    let study: BTreeMap<String, Value> = std::fs::read_to_string(arg(args, "--study").unwrap())
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str::<Value>(l).unwrap())
        .map(|v| (v["id"].as_str().unwrap().to_string(), v))
        .collect();
    let mut jobs = Vec::new();
    for (i, raw) in entries.iter().enumerate() {
        let entry: Entry = serde_json::from_value(json!({"id": raw["id"], "first_move": raw["first_move"], "rival": raw["rival"]})).unwrap();
        let state: State = serde_json::from_str(&std::fs::read_to_string(format!("{states}/{}.json", entry.id)).unwrap()).unwrap();
        let me = state.generate_possible_actions().0;
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let base = StdRng::seed_from_u64(seed_base + i as u64).next_u64() ^ 0x4b58_504c_4159_4f55;
        let legal = state.generate_possible_actions().1;
        for (role, step) in [("plans_first_move", &entry.first_move), ("rival", &entry.rival)] {
            let first = legal.iter().find(|a| step.matches(&state, me, a)).expect("the move").clone();
            let expected: Vec<String> = study[&entry.id][role]["rounds_detail"]["km3"]
                .as_array()
                .unwrap()
                .iter()
                .map(|r| r[1].as_str().unwrap().to_string())
                .collect();
            for j in 0..rounds {
                jobs.push((entry.id.clone(), role, observation.clone(), base, j, first.clone(), me, expected[j].clone()));
            }
        }
    }
    let results: Vec<(Vec<Value>, Value)> = jobs
        .par_iter()
        .map(|(id, role, observation, base, j, first, me, expected)| {
            let (world, list, seed) = lab_world(observation, &opponent, *base, *j);
            let (d0, d1) = if *me == 0 { (&deck, &list) } else { (&list, &deck) };
            let names = if *me == 0 { ["draft A".to_string(), "computer".to_string()] } else { ["computer".to_string(), "draft A".to_string()] };
            let mut game = Game::from_state(world, km3_pair(d0, d1), seed);
            game.apply_action(first);
            let ctx = json!({"source": "playout", "position": id, "first": role, "round": j, "pilot": me});
            let (events, end, _) = watch(&mut game, &ctx, [energy_types(d0), energy_types(d1)], names, 4000);
            let digest = format!("{:016x}", fnv1a64(serde_json::to_string(&end).unwrap().as_bytes()));
            (events, json!({"position": id, "first": role, "round": j, "digest": digest, "replayed_exactly": digest == *expected}))
        })
        .collect();
    write_out(args, results);
}

fn write_out(args: &[String], results: Vec<(Vec<Value>, Value)>) {
    let out = arg(args, "--out").unwrap();
    let mut f = std::fs::File::create(&out).unwrap();
    let mut checks = std::fs::File::create(format!("{out}.replay.jsonl")).unwrap();
    let (mut n, mut exact) = (0, 0);
    for (events, check) in results {
        n += 1;
        exact += check["replayed_exactly"].as_bool().unwrap() as usize;
        writeln!(checks, "{check}").unwrap();
        for e in events {
            writeln!(f, "{e}").unwrap();
        }
    }
    println!("{n} games or play-outs, {exact} replayed exactly");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("games") => games(&args),
        Some("playouts") => playouts(&args),
        _ => eprintln!("usage: trainer_habits games ... | trainer_habits playouts ..."),
    }
}
