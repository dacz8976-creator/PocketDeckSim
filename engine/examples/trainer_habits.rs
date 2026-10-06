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
//!   trainer_habits scripted --games <games.jsonl> --manifest <manifest.json> --out events.jsonl [--arm X]
//!     (Oct 6) A strength run's arm whose deck side isn't km3 (kx3's arm X), replayed cheaply: the deck's side plays the
//!     moves its log records (each found by the harness's own label), the opponent km3 plays itself. A label that names
//!     more than one legal move (`DiscardToolFromPokemon` says not which Tool) is tried each way, depth first, until the
//!     rest of the log and the ending agree. Checked as the games mode is: every logged move found, and the points, turns
//!     and winner as recorded.
//!   ... scripted ... --redecide <kx code> --redecide-out <file> [--redecide-movable]
//!     (Oct 6, the Tool filter) At each of the deck side's Tool placements that had no printed effect (with
//!     `--redecide-movable`, only those where another placement had one), kx3 decides again from the very observation
//!     and search randomness the game gave it: with the code given (the development run's kx3 is
//!     `kx3_r16_c12_z2_real_t0_poolmeta`), which must place the Tool where the log says, and with `_tools` added. One JSON
//!     line per decision, from the replay that matched the log.
//!   ... scripted ... --attack-scan <kx code> --attack-out <file>
//!     (Oct 6, quiz 4, item 1) At each of the deck side's decisions with an attack among the legal moves, km3's proposal
//!     from the game's own observation and search randomness: one JSON line wherever km3 proposes an attack, saying
//!     whether the log played an attack; where it didn't, kx3 (the code given) decides again from the same randomness,
//!     with every candidate's score, its lead over km3's attack and the reason (it must play what the log says).
//!   ... scripted ... --noeffect-scan <kx code> --noeffect-out <file>
//!     (Oct 6, quiz 4, item 2) At each of the deck side's decisions where the logged move can do nothing now by its text
//!     (as kx3 reads it, from the observation), km3's proposal from the game's own observation and search randomness;
//!     where km3 proposed that very move, kx3 (the code given, with `_noeffect` added) decides again from the same
//!     randomness: whether the tie-break now plays another move, or km3's move is kept (by its play-outs, or because a
//!     move cleared the bar, or nothing else does something).
//!   trainer_habits positions --games <games.jsonl> --manifest <manifest.json> --at <at.json> --dir <dir>
//!     (Oct 6, quiz 4, item 3) Positions of a run rebuilt exactly: for each entry of `--at` ({id, key, decision, then}),
//!     the game of that key (an arm with km3 on both sides) is played to the deck side's decision number `decision` (the
//!     harness logs a decision wherever a player is asked, i.e. has more than one legal move), checked there against the
//!     log (turn, number of legal moves, and the move km3 then makes), and the full state before it is written to
//!     `<dir>/<id>.json`. The labels in `then` are played on from there first (each must name exactly one legal move),
//!     for a position a few moves later in the same turn. `<dir>/index.json` lists what was written.
//!     With `--kx3 <code>` (the development run's kx3 is `kx3_r16_c12_z2_real_t0_poolmeta`), kx3 also decides at the
//!     position from the game's own observation and search randomness (a game with kx3 on the deck side is the same game
//!     up to there), and its report is kept with the check that it plays what the kx3 arm's log says.
//! Every move with a card text (an Item or Supporter played, an Ability or the Stadium used, a Tool played) carries the
//! no-effect reader's verdict (Oct 6, quiz 4, item 2; playout_effects.rs): an "effect" event with the card, whether it
//! could do anything there (true, false, or null for an unread text), and whether the move was a real decision.
//! Every Tool placement also carries the Tool-placement rule's verdict (Oct 6, playout_tools.rs): whether it has an
//! effect there, and how many placements offered had one. With `--dump-states <dir> [--dump-max N]` (games mode), the
//! states where the deck's side played a Tool that the rule would have placed elsewhere are written out, for positions
//! where the rule acts.
//! Every event is one JSON line: the context, the player, the turn, the hand and board before, and what followed.
use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;

use deckgym::actions::{Action, SimpleAction};
use deckgym::models::{Card, EnergyType, TrainerType};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{action_card, effect_now, placements_with_effect, DecisionReport, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, Player, PlayerCode};
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

/// The Tool-placement rule's verdict on a placement: whether it has an effect there, and whether the rule would have
/// had km3 place it elsewhere (some offered placement has one).
fn rule_verdict(before: &State, legal: &[Action], a: &Action) -> Value {
    let effective = placements_with_effect(before, legal);
    json!({"has_effect": effective.contains(a), "offered": legal.len(), "with_effect": effective.len(),
           "rule_would_change": !effective.is_empty() && !effective.contains(a)})
}

fn carrier_of(state: &State, owner: usize, tool: &Card) -> Option<usize> {
    (0..4).find(|&i| state.in_play_pokemon[owner][i].as_ref().is_some_and(|p| p.attached_tools.contains(tool)))
}

/// Plays `game` to the end (or `limit` ticks), watching every tick: the events, the final state, and the label of every real
/// decision (more than one legal move) with its actor.
fn watch(game: &mut Game, ctx: &Value, types: [Vec<EnergyType>; 2], decks: [String; 2], limit: usize) -> (Vec<Value>, State, Vec<(usize, String)>, Vec<(usize, State)>) {
    let mut events = Vec::new();
    // The state where each player last played a Tool card, and those the rule would have placed elsewhere.
    let mut tool_played: [Option<State>; 2] = [None, None];
    let mut misplaced: Vec<(usize, State)> = Vec::new();
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
        if let Some(card) = action_card(&before, &a) {
            events.push(json!({"kind": "effect", "ctx": ctx, "player": p, "deck": decks[p], "turn": turn, "card": card,
                               "does_something": effect_now(&before, &a, &before.decks[p].cards), "decision": legal.len() > 1}));
        }
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
            SimpleAction::Play { trainer_card } if format!("{:?}", trainer_card.trainer_card_type) == "Tool" => {
                tool_played[p] = Some(before.clone());
            }
            SimpleAction::AttachTool { in_play_idx, tool_card } if !TOOLS.contains(&tool_card.get_name().as_str()) => {
                // Another Tool: its placement and the rule's verdict only.
                let verdict = rule_verdict(&before, &legal, &a);
                if verdict["rule_would_change"] == true {
                    if let Some(st) = &tool_played[p] {
                        misplaced.push((p, st.clone()));
                    }
                }
                let mut e = base("tool_other");
                e["tool"] = json!(tool_card.get_name());
                e["slot"] = json!(in_play_idx);
                e["rule"] = verdict;
                events.push(e);
            }
            SimpleAction::AttachTool { in_play_idx, tool_card } => {
                let verdict = rule_verdict(&before, &legal, &a);
                if verdict["rule_would_change"] == true {
                    if let Some(st) = &tool_played[p] {
                        misplaced.push((p, st.clone()));
                    }
                }
                let mut e = base("tool");
                e["rule"] = verdict;
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
    (events, end, labels, misplaced)
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
    let results: Vec<(Vec<Value>, Value, Vec<State>)> = records
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
            let (events, end, labels, misplaced) = watch(&mut game, &ctx, [energy_types(d0), energy_types(d1)], names, usize::MAX);
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
            // The deck side's misplaced Tools, for the rule's positions.
            let dumps: Vec<State> = misplaced.into_iter().filter(|(p, _)| *p == seat).map(|(_, st)| st).collect();
            (events, json!({"key": g["key"], "replayed_exactly": same, "labels_logged": logged.len(), "labels_replayed": replayed.len(),
                            "deck_seat": seat, "deck": dn, "opp": on, "misplaced_states": dumps.len()}), dumps)
        })
        .collect();
    if let Some(dir) = arg(args, "--dump-states") {
        let max: usize = arg(args, "--dump-max").map_or(usize::MAX, |n| n.parse().unwrap());
        std::fs::create_dir_all(&dir).unwrap();
        let mut index = Vec::new();
        for (_, check, dumps) in &results {
            for (i, st) in dumps.iter().enumerate() {
                if index.len() >= max {
                    break;
                }
                let id = format!("{}#{}", check["key"].as_str().unwrap(), i);
                let file = format!("pos{:02}.json", index.len());
                std::fs::write(format!("{dir}/{file}"), serde_json::to_string(st).unwrap()).unwrap();
                index.push(json!({"file": file, "game": id, "deck": check["deck"], "opp": check["opp"], "seat": check["deck_seat"], "turn": st.turn_count}));
            }
        }
        std::fs::write(format!("{dir}/index.json"), serde_json::to_string_pretty(&index).unwrap()).unwrap();
        println!("{} states written to {dir}", index.len());
    }
    write_out(args, results.into_iter().map(|(e, c, _)| (e, c)).collect());
}

/// The strength harness's label, whole (rl/strength/src/main.rs `label`), to find each logged move.
fn harness_label(a: &Action, state: &State) -> String {
    let nm = |c: &Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::UseAbility { in_play_idx } => {
            let title = state.in_play_pokemon.get(a.actor).and_then(|s| s.get(*in_play_idx)).and_then(|p| p.as_ref()).and_then(|p| match &p.card {
                Card::Pokemon(pc) => pc.ability.as_ref().map(|ab| ab.title.clone()),
                _ => None,
            });
            match title {
                Some(t) => format!("Ability:{}@{}", t, in_play_idx),
                None => format!("Ability@{}", in_play_idx),
            }
        }
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
        SimpleAction::ChooseRetreatEnergy { to_in_play_idx, .. } => format!("RetreatPay:{}", to_in_play_idx),
        SimpleAction::EndTurn => "EndTurn".to_string(),
        other => format!("{:?}", other).split(|c: char| c == ' ' || c == '{' || c == '(').next().unwrap_or("?").to_string(),
    }
}

/// What a scripted replay saw: decisions used, labels it could not find, and the ambiguous decisions (index, options).
#[derive(Debug, Default, Clone)]
struct ScriptLog {
    used: usize,
    missing: Vec<String>,
    ambiguous: Vec<(usize, usize)>,
}

/// kx3 deciding again at a logged Tool placement: the code, the opponent's list (as the harness gave it), whether only
/// placements the rule would move are redecided, and where the records go.
#[derive(Debug, Clone)]
struct Redecide {
    params: PlayoutParams,
    opponent: Deck,
    movable_only: bool,
    key: String,
    out: std::sync::Arc<std::sync::Mutex<Vec<Value>>>,
}

fn slot_of(a: &Action) -> Option<usize> {
    match a.action {
        SimpleAction::AttachTool { in_play_idx, .. } => Some(in_play_idx),
        _ => None,
    }
}

fn report_json(r: &DecisionReport) -> Value {
    json!({"km": slot_of(&r.candidates[r.km3].action), "chosen": slot_of(&r.candidates[r.chosen].action), "reason": r.reason,
           "candidates": r.candidates.iter().map(|c| json!([slot_of(&c.action), if c.score.is_finite() { json!(c.score) } else { Value::Null }])).collect::<Vec<_>>(),
           "dropped": r.dropped.iter().map(|d| json!({"move": d.label, "reason": d.reason})).collect::<Vec<_>>(), "rounds": r.rounds, "ms": r.millis.round()})
}

/// km3's proposal at each decision with an attack available, and kx3's decision again where the log left km3's attack.
#[derive(Debug)]
struct AttackScan {
    params: PlayoutParams,
    opponent: Deck,
    km: Box<dyn Player>,
    key: String,
    out: std::sync::Arc<std::sync::Mutex<Vec<Value>>>,
}

fn is_attack(a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_))
}

/// At the deck side's moves that can do nothing now, km3's proposal, and kx3 with `_noeffect` where km3 proposed it.
#[derive(Debug)]
struct NoEffectScan {
    params: PlayoutParams,
    opponent: Deck,
    km: Box<dyn Player>,
    key: String,
    out: std::sync::Arc<std::sync::Mutex<Vec<Value>>>,
}

/// Plays the moves a log records, each found by its label among the legal moves; at an ambiguous label, the option
/// `forced` names (else the first).
#[derive(Debug)]
struct Scripted {
    labels: Vec<String>,
    next: usize,
    deck: Deck,
    forced: BTreeMap<usize, usize>,
    log: std::sync::Arc<std::sync::Mutex<ScriptLog>>,
    redecide: Option<Redecide>,
    attack_scan: Option<AttackScan>,
    noeffect_scan: Option<NoEffectScan>,
}

impl Scripted {
    fn attack_scan(&mut self, rng: &StdRng, observation: &PlayerObservation, actions: &[Action], played: &Action, k: usize) {
        let deck = self.deck.clone();
        let Some(sc) = &mut self.attack_scan else { return };
        let state = observation.visible_state();
        if !actions.iter().any(is_attack) {
            return;
        }
        let proposal = sc.km.decision_fn(&mut rng.clone(), observation, actions);
        if !is_attack(&proposal) {
            return;
        }
        let mut rec = json!({"key": sc.key, "decision": k, "turn": state.turn_count, "km": harness_label(&proposal, state),
                             "played": harness_label(played, state), "played_an_attack": is_attack(played)});
        if !is_attack(played) {
            let r = PlayoutPlayer::new(deck, sc.opponent.clone(), sc.params.clone()).evaluate(&mut rng.clone(), observation, actions);
            let c = &r.candidates[r.chosen];
            rec["kx3"] = json!({
                "chosen_equals_played": c.action == *played, "km_score": r.candidates[r.km3].score, "chosen_score": c.score,
                "lead": c.diff, "se": c.se, "reason": r.reason, "rounds": r.rounds,
                "candidates": r.candidates.iter().map(|x| json!([harness_label(&x.action, state), x.score, x.diff, x.se])).collect::<Vec<_>>(),
            });
        }
        sc.out.lock().unwrap().push(rec);
    }

    fn noeffect_scan(&mut self, rng: &StdRng, observation: &PlayerObservation, actions: &[Action], played: &Action, k: usize) {
        let deck = self.deck.clone();
        let Some(sc) = &mut self.noeffect_scan else { return };
        let state = observation.visible_state();
        if effect_now(state, played, &observation.known_own_deck) != Some(false) {
            return;
        }
        let proposal = sc.km.decision_fn(&mut rng.clone(), observation, actions);
        let mut rec = json!({"key": sc.key, "decision": k, "turn": state.turn_count, "card": action_card(state, played),
                             "played": harness_label(played, state), "km": harness_label(&proposal, state), "km_proposed_it": proposal == *played});
        if proposal == *played {
            let r = PlayoutPlayer::new(deck, sc.opponent.clone(), sc.params.clone()).evaluate(&mut rng.clone(), observation, actions);
            let c = &r.candidates[r.chosen];
            let does = |a: &Action| effect_now(state, a, &observation.known_own_deck) != Some(false);
            rec["kx3"] = json!({
                "chosen": harness_label(&c.action, state), "chosen_does_something": does(&c.action), "plays_the_logged_move": c.action == *played,
                "tie_break": r.reason.starts_with("tie-break: no effect now"), "reason": r.reason, "rounds": r.rounds,
                "others_do_something": actions.iter().any(|a| does(a)),
                "candidates": r.candidates.iter().map(|x| json!([harness_label(&x.action, state), x.score, does(&x.action)])).collect::<Vec<_>>(),
            });
        }
        sc.out.lock().unwrap().push(rec);
    }

    fn redecide(&self, rng: &StdRng, observation: &PlayerObservation, actions: &[Action], played: &Action, k: usize) {
        let Some(re) = &self.redecide else { return };
        let state = observation.visible_state();
        if !actions.iter().all(|a| slot_of(a).is_some()) {
            return;
        }
        let effective = placements_with_effect(state, actions);
        if effective.contains(played) || (re.movable_only && effective.is_empty()) {
            return;
        }
        let decide = |tools: bool| {
            let params = PlayoutParams { tools, ..re.params.clone() };
            PlayoutPlayer::new(self.deck.clone(), re.opponent.clone(), params).evaluate(&mut rng.clone(), observation, actions)
        };
        let (off, on) = (decide(false), decide(true));
        let on_choice = on.candidates[on.chosen].action.clone();
        let tool = match &played.action {
            SimpleAction::AttachTool { tool_card, .. } => tool_card.get_name(),
            _ => unreachable!(),
        };
        let holder = |i: usize| state.in_play_pokemon[played.actor][i].as_ref().map(|p| p.card.get_name());
        re.out.lock().unwrap().push(json!({
            "key": re.key, "decision": k, "turn": state.turn_count, "tool": tool, "logged": slot_of(played),
            "board": (0..4).map(|i| holder(i)).collect::<Vec<_>>(),
            "effective": effective.iter().map(slot_of).collect::<Vec<_>>(), "rule_would_move": !effective.is_empty(),
            "off_equals_logged": off.candidates[off.chosen].action == *played,
            "on_lands_right": effective.contains(&on_choice),
            "off": report_json(&off), "on": report_json(&on),
        }));
    }
}

impl Player for Scripted {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        let chosen = self.choose(observation, actions);
        let k = self.next - 1;
        self.redecide(rng, observation, actions, &chosen, k);
        self.attack_scan(rng, observation, actions, &chosen, k);
        self.noeffect_scan(rng, observation, actions, &chosen, k);
        chosen
    }
    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        actions[0].clone()
    }
}

impl Scripted {
    fn choose(&mut self, observation: &PlayerObservation, actions: &[Action]) -> Action {
        let state = observation.visible_state();
        let want = self.labels.get(self.next).cloned().unwrap_or_default();
        self.next += 1;
        let k = self.next - 1;
        let mut distinct: Vec<Action> = Vec::new();
        for a in actions.iter().filter(|a| harness_label(a, state) == want) {
            if !distinct.contains(a) {
                distinct.push(a.clone());
            }
        }
        let mut log = self.log.lock().unwrap();
        log.used = self.next;
        match distinct.len() {
            0 => {
                log.missing.push(format!("decision {k}: '{want}' matched no legal move"));
                actions[0].clone()
            }
            1 => distinct.remove(0),
            n => {
                log.ambiguous.push((k, n));
                let i = self.forced.get(&k).copied().unwrap_or(0).min(n - 1);
                distinct.remove(i)
            }
        }
    }
}

fn scripted(args: &[String]) {
    let manifest: Value = serde_json::from_str(&std::fs::read_to_string(arg(args, "--manifest").unwrap()).unwrap()).unwrap();
    let arm = arg(args, "--arm").unwrap_or_else(|| "X".into());
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
    assert!(records.iter().all(|g| g["pilot_opp"] == "km3"), "the opponent must be km3");
    let redecide_code = arg(args, "--redecide").map(|c| PlayoutParams::parse(c.strip_prefix("kx").unwrap()).unwrap());
    let movable_only = args.iter().any(|a| a == "--redecide-movable");
    let redecided: std::sync::Mutex<Vec<Value>> = std::sync::Mutex::new(Vec::new());
    let attack_code = arg(args, "--attack-scan").map(|c| PlayoutParams::parse(c.strip_prefix("kx").unwrap()).unwrap());
    let scanned: std::sync::Mutex<Vec<Value>> = std::sync::Mutex::new(Vec::new());
    let noeffect_code = arg(args, "--noeffect-scan").map(|c| PlayoutParams { noeffect: true, ..PlayoutParams::parse(c.strip_prefix("kx").unwrap()).unwrap() });
    let noeffect_found: std::sync::Mutex<Vec<Value>> = std::sync::Mutex::new(Vec::new());
    let results: Vec<(Vec<Value>, Value)> = records
        .par_iter()
        .map(|g| {
            let (dn, on) = (g["deck"].as_str().unwrap(), g["opp"].as_str().unwrap());
            let seat = g["seat"].as_u64().unwrap() as usize;
            let seed = g["seed"].as_u64().unwrap();
            let (dd, od) = (&lists[dn], &lists[on]);
            let (d0, d1) = if seat == 0 { (dd, od) } else { (od, dd) };
            let names = if seat == 0 { [dn.to_string(), on.to_string()] } else { [on.to_string(), dn.to_string()] };
            let labels: Vec<String> = g["log"].as_array().unwrap().iter().map(|e| e["a"].as_str().unwrap().to_string()).collect();
            let winner_of = |end: &State| match end.winner {
                Some(GameOutcome::Win(w)) if w == seat => "deck",
                Some(GameOutcome::Win(_)) => "opp",
                _ => "tie",
            };
            let mut forced: BTreeMap<usize, usize> = BTreeMap::new();
            let mut attempts = 0;
            loop {
                attempts += 1;
                let log = std::sync::Arc::new(std::sync::Mutex::new(ScriptLog::default()));
                let records = std::sync::Arc::new(std::sync::Mutex::new(Vec::new()));
                let redecide = redecide_code.clone().map(|params| Redecide {
                    params,
                    opponent: od.clone(),
                    movable_only,
                    key: g["key"].as_str().unwrap().to_string(),
                    out: records.clone(),
                });
                let scan_out = std::sync::Arc::new(std::sync::Mutex::new(Vec::new()));
                let attack_scan = attack_code.clone().map(|params| AttackScan {
                    params,
                    opponent: od.clone(),
                    km: km3_pair(d0, d1).remove(seat),
                    key: g["key"].as_str().unwrap().to_string(),
                    out: scan_out.clone(),
                });
                let noeffect_out = std::sync::Arc::new(std::sync::Mutex::new(Vec::new()));
                let noeffect_scan = noeffect_code.clone().map(|params| NoEffectScan {
                    params,
                    opponent: od.clone(),
                    km: km3_pair(d0, d1).remove(seat),
                    key: g["key"].as_str().unwrap().to_string(),
                    out: noeffect_out.clone(),
                });
                let mut players = km3_pair(d0, d1);
                players[seat] = Box::new(Scripted {
                    labels: labels.clone(),
                    next: 0,
                    deck: dd.clone(),
                    forced: forced.clone(),
                    log: log.clone(),
                    redecide,
                    attack_scan,
                    noeffect_scan,
                });
                let mut game = Game::new(players, seed);
                let ctx = json!({"source": "scripted", "key": g["key"], "seed": seed, "deck_seat": seat, "pilot_deck": g["pilot_deck"]});
                let (events, end, _, _) = watch(&mut game, &ctx, [energy_types(d0), energy_types(d1)], names.clone(), usize::MAX);
                let log = log.lock().unwrap().clone();
                let same = log.missing.is_empty()
                    && log.used == labels.len()
                    && g["points"] == json!([end.points[seat], end.points[1 - seat]])
                    && g["turns"].as_u64() == Some(end.turn_count as u64)
                    && g["winner"] == winner_of(&end);
                // On a mismatch, the latest ambiguous decision with an untried option takes its next one.
                let next = log.ambiguous.iter().rev().find(|(d, n)| forced.get(d).copied().unwrap_or(0) + 1 < *n).copied();
                if same || next.is_none() || attempts >= 64 {
                    let check = json!({"key": g["key"], "replayed_exactly": same, "labels_logged": labels.len(), "labels_used": log.used,
                                       "missing": log.missing, "ambiguous": log.ambiguous.len(), "attempts": attempts});
                    for mut r in records.lock().unwrap().drain(..) {
                        r["replayed_exactly"] = json!(same);
                        redecided.lock().unwrap().push(r);
                    }
                    for mut r in scan_out.lock().unwrap().drain(..) {
                        r["replayed_exactly"] = json!(same);
                        scanned.lock().unwrap().push(r);
                    }
                    for mut r in noeffect_out.lock().unwrap().drain(..) {
                        r["replayed_exactly"] = json!(same);
                        noeffect_found.lock().unwrap().push(r);
                    }
                    break (events, check);
                }
                let (d, _) = next.unwrap();
                let tried = forced.get(&d).copied().unwrap_or(0);
                forced.retain(|&k, _| k < d);
                forced.insert(d, tried + 1);
            }
        })
        .collect();
    if let Some(path) = arg(args, "--noeffect-out") {
        let mut f = std::fs::File::create(path).unwrap();
        for r in noeffect_found.into_inner().unwrap() {
            writeln!(f, "{r}").unwrap();
        }
    }
    if let Some(path) = arg(args, "--attack-out") {
        let mut f = std::fs::File::create(path).unwrap();
        for r in scanned.into_inner().unwrap() {
            writeln!(f, "{r}").unwrap();
        }
    }
    if let Some(path) = arg(args, "--redecide-out") {
        let mut f = std::fs::File::create(path).unwrap();
        for r in redecided.into_inner().unwrap() {
            writeln!(f, "{r}").unwrap();
        }
    }
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
            let (events, end, _, _) = watch(&mut game, &ctx, [energy_types(d0), energy_types(d1)], names, 4000);
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

/// km3 on the deck side, and at its decision number `at` kx3's decision too (from the same observation and a copy of the
/// search randomness), kept with kx3's chosen move's label.
#[derive(Debug)]
struct Capture {
    inner: Box<dyn Player>,
    at: usize,
    count: usize,
    deck: Deck,
    opponent: Deck,
    params: PlayoutParams,
    out: std::sync::Arc<std::sync::Mutex<Option<(String, Value)>>>,
}

impl Player for Capture {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        if self.count == self.at {
            let r = PlayoutPlayer::new(self.deck.clone(), self.opponent.clone(), self.params.clone()).evaluate(&mut rng.clone(), observation, actions);
            let state = observation.visible_state();
            let label = harness_label(&r.candidates[r.chosen].action, state);
            let report = json!({
                "km": harness_label(&r.candidates[r.km3].action, state), "chosen": label, "reason": r.reason, "rounds": r.rounds,
                "candidates": r.candidates.iter().map(|c| json!({"move": harness_label(&c.action, state), "score": c.score, "diff": c.diff,
                    "se": if c.se.is_finite() { json!(c.se) } else { Value::Null }})).collect::<Vec<_>>(),
                "dropped": r.dropped.iter().map(|d| json!({"move": d.label, "reason": d.reason})).collect::<Vec<_>>(),
            });
            *self.out.lock().unwrap() = Some((label, report));
        }
        self.count += 1;
        self.inner.decision_fn(rng, observation, actions)
    }
    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, actions: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, state, actions)
    }
}

fn positions(args: &[String]) {
    let manifest: Value = serde_json::from_str(&std::fs::read_to_string(arg(args, "--manifest").unwrap()).unwrap()).unwrap();
    let lists: BTreeMap<String, Deck> = manifest["decks"]
        .as_array()
        .unwrap()
        .iter()
        .chain(manifest["opponents"].as_array().unwrap())
        .map(|d| (d["name"].as_str().unwrap().to_string(), Deck::from_file(d["path"].as_str().unwrap()).unwrap()))
        .collect();
    let records: Vec<Value> =
        std::fs::read_to_string(arg(args, "--games").unwrap()).unwrap().lines().map(|l| serde_json::from_str::<Value>(l).unwrap()).collect();
    let at: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(args, "--at").unwrap()).unwrap()).unwrap();
    let dir = arg(args, "--dir").unwrap();
    let kx_code = arg(args, "--kx3").map(|c| PlayoutParams::parse(c.strip_prefix("kx").unwrap()).unwrap());
    std::fs::create_dir_all(&dir).unwrap();
    let mut index = Vec::new();
    for p in &at {
        let id = p["id"].as_str().unwrap();
        let g = records.iter().find(|g| g["key"] == p["key"]).unwrap_or_else(|| panic!("{id}: no game {}", p["key"]));
        assert!(g["pilot_deck"] == "km3" && g["pilot_opp"] == "km3", "{id}: the arm must be km3 on both sides");
        let decision = p["decision"].as_u64().unwrap() as usize;
        let (dn, on) = (g["deck"].as_str().unwrap(), g["opp"].as_str().unwrap());
        let seat = g["seat"].as_u64().unwrap() as usize;
        let seed = g["seed"].as_u64().unwrap();
        let (d0, d1) = if seat == 0 { (&lists[dn], &lists[on]) } else { (&lists[on], &lists[dn]) };
        let logged = &g["log"][decision];
        // The game to the decision; `before` is the state where the deck side is asked for its decision number `decision`.
        let to_decision = |game: &mut Game| -> State {
            let mut count = 0;
            loop {
                assert!(!game.is_game_over(), "{id}: the game ended before decision {decision}");
                let before = game.get_state_clone();
                let (actor, legal) = before.generate_possible_actions();
                if actor == seat && legal.len() > 1 {
                    if count == decision {
                        return before;
                    }
                    count += 1;
                }
                game.play_tick();
            }
        };
        let captured = std::sync::Arc::new(std::sync::Mutex::new(None));
        let mut players = km3_pair(d0, d1);
        if let Some(params) = &kx_code {
            let inner = players.remove(seat);
            let (deck, opponent) = (lists[dn].clone(), lists[on].clone());
            players.insert(seat, Box::new(Capture { inner, at: decision, count: 0, deck, opponent, params: params.clone(), out: captured.clone() }));
        }
        let mut game = Game::new(players, seed);
        let state = to_decision(&mut game);
        let legal = state.generate_possible_actions().1;
        let played = game.play_tick();
        let check = json!({"turn": state.turn_count, "legal": legal.len(), "km3_plays": harness_label(&played, &state)});
        assert_eq!(check, json!({"turn": logged["t"], "legal": logged["n"], "km3_plays": logged["a"]}), "{id}: the position differs from the log");
        // kx3's own decision in the game, and the kx3 arm's logged move at the same decision.
        let kx3 = captured.lock().unwrap().take().map(|(label, report): (String, Value)| {
            let other = records.iter().find(|r| {
                r["deck"] == g["deck"] && r["opp"] == g["opp"] && r["seed"] == g["seed"] && r["seat"] == g["seat"] && r["pilot_deck"] != "km3"
            });
            let logged = other.map(|r| r["log"][decision]["a"].clone());
            json!({"chosen": label, "kx3_arm_logged": logged, "plays_what_the_log_says": logged.as_ref().is_some_and(|l| *l == label),
                   "report": report})
        });
        // The `then` moves, played on from the same position in a second copy of the game.
        let mut game = Game::new(km3_pair(d0, d1), seed);
        let mut state = to_decision(&mut game);
        let then: Vec<String> = p["then"].as_array().map_or(Vec::new(), |t| t.iter().map(|l| l.as_str().unwrap().to_string()).collect());
        for l in &then {
            let (actor, legal) = state.generate_possible_actions();
            assert_eq!(actor, seat, "{id}: \"{l}\" is not the deck side's to play");
            let found: Vec<&Action> = legal.iter().filter(|a| harness_label(a, &state) == *l).collect();
            assert_eq!(found.len(), 1, "{id}: \"{l}\" names {} legal moves", found.len());
            game.apply_action(found[0]);
            state = game.get_state_clone();
        }
        let (actor, legal) = state.generate_possible_actions();
        let labels: Vec<String> = legal.iter().map(|a| harness_label(a, &state)).collect();
        std::fs::write(format!("{dir}/{id}.json"), serde_json::to_string(&state).unwrap()).unwrap();
        index.push(json!({"id": id, "key": p["key"], "decision": decision, "deck": dn, "opp": on, "seat": seat, "seed": seed,
                          "checked_against_the_log": check, "kx3_in_the_game": kx3, "then": then, "turn": state.turn_count, "to_move": actor,
                          "legal": labels}));
        println!("{id}: written ({} legal moves for seat {actor})", legal.len());
    }
    std::fs::write(format!("{dir}/index.json"), serde_json::to_string_pretty(&index).unwrap()).unwrap();
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("games") => games(&args),
        Some("playouts") => playouts(&args),
        Some("scripted") => scripted(&args),
        Some("positions") => positions(&args),
        _ => eprintln!("usage: trainer_habits games ... | trainer_habits playouts ..."),
    }
}
