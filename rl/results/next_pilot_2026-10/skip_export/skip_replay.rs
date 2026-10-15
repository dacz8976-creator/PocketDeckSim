//! skip_replay (the cloud, Oct 12; Fable, direct route): the exact attack-skipping measure the combined run's pre-registration
//! promised (`../PREREGISTRATION.md` line 7), as an identity replay of the recorded games, not a re-run. Nothing in the engine or the
//! players changes; this file is an example program built in a copy of the program's own source.
//!
//! Each game of a strength run's `games.jsonl` is rebuilt as the harness built it (rl/strength/src/main.rs: `Game::new` with the
//! two seats' players from `parse_player_code`, the record's seed; the deck in the record's seat). The opponent side is km3 and
//! plays itself (it is cheap: no play-outs). The deck side plays the moves its log records, each found among the legal moves by
//! the harness's own label (`label` in main.rs, copied below); a label that names more than one legal move is tried each way,
//! depth first, until the rest of the log and the ending agree (as `trainer_habits scripted` does). The engine draws its
//! search randomness per decision from (seat, decision number), not from the game's dealing and coin stream, so playing the
//! logged moves without the pilot's search leaves every coin, draw and km3 decision as it was.
//!
//! A game counts as replayed only when every logged decision was found, each at the logged turn with the logged number of legal
//! moves, and the points, turns and winner are as recorded. For each deck-side decision (a point where the deck's pilot was
//! asked, i.e. had two or more legal moves) one line is written: the legal moves (labels), whether any was an attack, the move
//! taken and whether it was an attack.
//!
//! Oct 12, Fable's two follow-ups:
//!   - KM3 PROPOSAL (`--km3`): at every deck-side decision with an attack legal (`--km3-all`: at every decision), km3 is asked for
//!     its move from the same observation and the same search randomness the engine gave the deck's pilot there in play: the
//!     engine seeds each decision's search from (seat, decision number) (`GameRandomness::decision`, game.rs `play_tick`), and
//!     the replayed game asks the deck side exactly the decisions it asked in play, so `decision_fn` here receives that very
//!     seed; km3 gets a copy of it. km3 keeps no memory between decisions (ExpectiMiniMaxPlayer holds only its settings), so its
//!     answer is the move km3 would have made at that decision in play. In km3's own games it must equal the recorded move.
//!     Written as `km3_move` and `km3_attacked` on each decision line (null where km3 wasn't asked).
//!   - BOARD STATE (`--boards <skip_turns.tsv> --bot NAME --boards-out FILE`): at each deck-side decision in that bot's listed
//!     skip turns, the true board before the decision (both Actives and Benches: name, HP / max HP, Energy, Tools, Special
//!     Conditions; the deck side's hand names and deck count; points, turn, the legal moves and the one taken), each legal
//!     attack's expected damage to the opponent's Active and its chance to Knock it Out, and the opponent's Active's attacks
//!     with their cost and the same forecast against ours, as if it attacked from this board. The forecast is the engine's own:
//!     `try_forecast_action` gives an attack's branches and their probabilities (`apply_action` samples one of them in play);
//!     each branch is applied to a copy of the board and its queued choices are resolved (the first offered each time), and the
//!     damage is read off the Active it hit.
//! Oct 12, the laptop's review (REVIEW_SKIP_EXACT_laptop.md on main):
//!   - A label that names more than one legal move (DiscardOwnCards, ApplyDamage, DiscardToolFromPokemon,
//!     MoveRandomOpponentEnergyToActive) is now resolved by asking the pilot that played (the record's `pilot_deck`, built as the
//!     harness builds it) from the same observation and search randomness: km3 and kx3 keep no memory between decisions, so its
//!     answer is the move it made in play. Only if the pilot's move isn't one of the label's moves does the old trial order apply;
//!     such a game is counted in `ambiguous_unresolved`.
//!   - The check also compares each logged decision's points (`p`), Active (`act`) and Bench count (`b`), and the game's plies and
//!     the opponent's number of decisions (`moves_opp.n`). The opponent's pilot is the record's `pilot_opp`.
//!   skip_replay --games <games.jsonl> --manifest <manifest.json> --arm X|ref --out decisions.jsonl --check check.jsonl
//!               [--threads N] [--limit N] [--km3 | --km3-all] [--boards skip_turns.tsv --bot NAME --boards-out boards.jsonl]
//!               [--export requests.tsv --pos-out positions.json --drop-out dropped.tsv]
//! Oct 15 (next_pilot_2026-10, brief item 6; Sonnet): EXPORT MODE (`--export`), the route that brings old-engine decisions to the current engine.
//!   requests.tsv: `id <TAB> game key <TAB> decision number [<TAB> km3_move]`, one per line (a first line starting `id` is a header). At each
//!   requested deck-side decision of its game the exact true state before it (the old engine's own, both hands, both decks, the discard
//!   piles, every flag) is written as a pg_pos position (`pause_games_decisions_2026-10-02/harness/pg_pos.rs`, main 28df6315 or later):
//!   the deck side is "me" whichever seat it sat in. The fields pg_pos builds itself are given in its form (hand, discard, board, Energy
//!   Zone, knock-out counts, Stadium, turn effects, `top` = the whole deck in order); what it can't build (a Pokemon's ability_used,
//!   moved_to_active_this_turn and the like, the turn flags) travels in the position's `flags` key, which pg_pos writes over the built
//!   state: `in_play_pokemon` (both boards, exactly as the old engine serialised them) and the turn flags. The opponent's hand and deck
//!   order can't be written (pg_pos deals them from his list, `filler`), so the position is approximate there, and the km3 check below
//!   is what decides whether the approximation matters.
//!   Written with the position: `km3_move`, km3's own move at that decision from the replay (as `--km3` asks it); if the request names a
//!   recorded km3_move and the replay's differs, the request is dropped. A request is also dropped, with its reason, when its game did
//!   not replay exactly, its decision is not a turn-level one (a queued choice is pending), or a flag pg_pos can't carry is set.
//!   `--drop-out` lists every dropped request (id, key, decision, reason). The second half of the rule, "kept only where km3 on the
//!   current engine makes its recorded km3_move in most of 12 seeds", is `skip_positions.py` (it runs pg_pos).
//! Run from the repository root the manifest's deck paths are relative to.
use std::collections::{BTreeMap, BTreeSet};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

use deckgym::actions::{Action, SimpleAction};
use deckgym::actions::try_forecast_action;
use deckgym::models::{Card, PlayedCard};
use deckgym::observation::PlayerObservation;
use deckgym::players::{create_players, parse_player_code, Player};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;
use serde_json::{json, Value};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// The strength harness's label (rl/strength/src/main.rs `label`, with the observation's state), to find each logged move.
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

fn is_attack(a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_))
}

/// One logged decision of the deck side: the move's label, the game turn and the number of legal moves the harness recorded.
#[derive(Debug, Clone)]
struct Logged {
    label: String,
    turn: u64,
    n: u64,
    p: Value,
    act: String,
    b: u64,
}

/// What a scripted replay saw.
#[derive(Debug, Default, Clone)]
struct ScriptLog {
    used: usize,
    missing: Vec<String>,
    ambiguous: Vec<(usize, usize)>,
    resolved_by_pilot: usize,
    unresolved: usize,
    decisions: Vec<Value>,
    boards: Vec<Value>,
    /// Export mode: one {"position": ..} or {"dropped": reason, ..} per request reached.
    exports: Vec<Value>,
}

/// One Pokémon in play: name, HP and max HP, Energy, Tools, Special Conditions.
fn mon(p: &PlayedCard) -> Value {
    let raw = serde_json::to_value(p).unwrap_or(Value::Null);
    let counters = raw["damage_counters"].as_u64().unwrap_or(0);
    let mut cond = Vec::new();
    for (on, name) in [(p.is_poisoned(), "Poisoned"), (p.is_burned(), "Burned"), (p.is_asleep(), "Asleep"), (p.is_paralyzed(), "Paralyzed"),
                       (p.is_confused(), "Confused")] {
        if on {
            cond.push(name);
        }
    }
    json!({"name": p.get_name(), "hp": p.get_remaining_hp(), "max_hp": p.get_remaining_hp() as u64 + counters,
           "energy": p.attached_energy.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
           "tools": p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>(), "conditions": cond})
}

fn side(state: &State, player: usize) -> Value {
    let slots = &state.in_play_pokemon[player];
    json!({"active": slots[0].as_ref().map(mon), "bench": slots[1..].iter().flatten().map(mon).collect::<Vec<_>>()})
}

/// The engine's expected damage of `action` to `target`'s Active, and the chance it is Knocked Out: every branch of
/// `try_forecast_action` applied to a copy of `state`, its queued choices resolved (the first offered), weighted by its probability.
fn forecast(state: &State, action: &Action, target: usize, decks: &(Deck, Deck)) -> Value {
    let Some(before) = state.in_play_pokemon[target][0].clone() else { return Value::Null };
    let attacker = action.actor;
    let run = || -> Result<(f64, f64, usize), String> {
        let outcomes = try_forecast_action(state, action).map_err(|e| format!("unpriced: {:?}", e.kind))?;
        let (probs, muts) = outcomes.into_branches();
        let (mut dmg, mut ko) = (0.0, 0.0);
        let n = probs.len();
        for (p, m) in probs.into_iter().zip(muts) {
            let mut st = state.clone();
            let mut rng = StdRng::seed_from_u64(20_990_000_000);
            m(&mut rng, &mut st, action);
            let code = parse_player_code("km3").unwrap();
            let mut g = Game::from_state(st, create_players(decks.0.clone(), decks.1.clone(), vec![code.clone(), code]), 20_990_000_000);
            for _ in 0..60 {
                let s = g.get_state_clone();
                if g.is_game_over() || s.move_generation_stack.is_empty() {
                    break;
                }
                let (_, acts) = s.generate_possible_actions();
                if acts.is_empty() {
                    break;
                }
                g.apply_action(&acts[0]);
            }
            let after = g.get_state_clone();
            let knocked = after.points[attacker] > state.points[attacker]
                || after.in_play_pokemon[target][0].as_ref().map_or(true, |a| a.get_id() != before.get_id());
            let hp_after = if knocked { 0 } else { after.in_play_pokemon[target][0].as_ref().unwrap().get_remaining_hp() };
            dmg += p * before.get_remaining_hp().saturating_sub(hp_after) as f64;
            ko += p * knocked as u8 as f64;
        }
        Ok((dmg, ko, n))
    };
    match std::panic::catch_unwind(std::panic::AssertUnwindSafe(run)) {
        Ok(Ok((d, k, n))) => json!({"expected_damage": (d * 10.0).round() / 10.0, "ko_chance": (k * 1000.0).round() / 1000.0, "branches": n}),
        Ok(Err(e)) => json!({"not_forecast": e}),
        Err(_) => json!({"not_forecast": "the engine's forecast refused this board (a panic, caught)"}),
    }
}

/// A card as pg_pos writes it: "Name SET NNN".
fn card_str(c: &Card) -> String {
    format!("{} {}", c.get_name(), c.get_id())
}

/// The pair `[seat 0's, seat 1's]` as `[the deck side's, the other's]`.
fn sw<T: Clone>(a: &[T; 2], seat: usize) -> [T; 2] {
    if seat == 0 { a.clone() } else { [a[1].clone(), a[0].clone()] }
}

/// A turn effect names players by seat; the position puts the deck side at seat 0, so for a deck side that sat at seat 1 every player
/// index inside the effect is swapped.
fn swap_players(v: &mut Value) {
    match v {
        Value::Object(m) => {
            for (k, x) in m.iter_mut() {
                if matches!(k.as_str(), "player" | "source_player" | "target_player") {
                    if let Some(n) = x.as_u64().filter(|n| *n < 2) {
                        *x = json!(1 - n);
                    }
                } else {
                    swap_players(x);
                }
            }
        }
        Value::Array(a) => a.iter_mut().for_each(swap_players),
        _ => {}
    }
}

/// The turn flags a position carries in its `flags` key (name, whether the pair is indexed by seat). The two that the engine leaves out of
/// its serialised form while all false (`skip_serializing_if`) can't be carried when set: pg_pos checks the key exists in its own state.
const FLAGS: [(&str, bool); 14] = [
    ("has_played_support", false), ("has_retreated", false), ("has_played_stadium", false), ("has_used_stadium", true),
    ("knocked_out_by_opponent_attack_this_turn", false), ("knocked_out_by_opponent_attack_last_turn", false),
    ("knocked_out_types_by_opponent_attack_this_turn", false), ("knocked_out_types_by_opponent_attack_last_turn", false),
    ("attack_name_used_this_turn", true), ("attack_name_used_last_turn", true), ("attack_name_used_count", true),
    ("points_gained_this_turn", true), ("points_gained_during_own_last_turn", true), ("own_knockouts_this_game", true),
];
const FLAGS_SKIPPED_WHEN_FALSE: [&str; 2] = ["victory_star_used_this_turn", "luxury_coin_used_this_turn"];

/// The true state before a turn-level decision of `seat`, as a pg_pos position (the deck side is "me"). Err names why it can't be one.
fn export_position(st: &State, seat: usize, id: &str, deck_key: &str, opp_key: &str, km3_move: Option<&str>) -> Result<Value, String> {
    let (actor, _) = st.generate_possible_actions();
    if actor != seat || st.current_player != seat {
        return Err(format!("not the deck side's turn-level decision (the actor is seat {actor})"));
    }
    if !st.move_generation_stack.is_empty() || st.pending_attack_coin_choice.is_some() || st.pending_misty_target_choice.is_some()
        || st.pending_trainer_coin_choice.is_some()
    {
        return Err("a queued choice is pending (pg_pos clears the queue, so it can't be rebuilt)".to_string());
    }
    let raw = serde_json::to_value(st).map_err(|e| e.to_string())?;
    let (me, opp) = (seat, 1 - seat);
    let strs = |v: &[Card]| v.iter().map(card_str).collect::<Vec<_>>();
    let energies = |v: &[deckgym::models::EnergyType]| v.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>();
    let board = |side: usize| -> Vec<Value> {
        st.in_play_pokemon[side]
            .iter()
            .flatten()
            .map(|p| {
                let r = serde_json::to_value(p).unwrap_or(Value::Null);
                let cond: Vec<&str> = [(p.is_poisoned(), "Poisoned"), (p.is_burned(), "Burned"), (p.is_asleep(), "Asleep"),
                                       (p.is_paralyzed(), "Paralyzed"), (p.is_confused(), "Confused")]
                    .iter()
                    .filter(|(on, _)| *on)
                    .map(|(_, n)| *n)
                    .collect();
                json!({"card": card_str(&p.card), "hp": p.get_remaining_hp(), "energy": energies(&p.attached_energy), "tools": strs(&p.attached_tools),
                       "behind": strs(&p.cards_behind), "new": r["played_this_turn"].as_bool().unwrap_or(false), "conditions": cond})
            })
            .collect()
    };
    let zone = |side: usize| (serde_json::to_value(st.energy_zone[side].current).unwrap_or(Value::Null),
                              serde_json::to_value(st.energy_zone[side].next).unwrap_or(Value::Null));
    let (own_ko, ko) = (raw["own_knockouts_this_game"][me].clone(), raw["own_knockouts_this_game"][opp].clone());
    let mut flags = serde_json::Map::new();
    for key in FLAGS_SKIPPED_WHEN_FALSE {
        if let Some(v) = raw.get(key) {
            if v.as_array().map_or(true, |a| a.iter().any(|x| x.as_bool() != Some(false))) {
                return Err(format!("{key} is set, and pg_pos can't carry it"));
            }
        }
    }
    for (key, pair) in FLAGS {
        let Some(v) = raw.get(key) else { continue };
        let v = if pair { json!(sw(&[v[0].clone(), v[1].clone()], seat)) } else { v.clone() };
        flags.insert(key.to_string(), v);
    }
    flags.insert("in_play_pokemon".to_string(), json!(sw(&[raw["in_play_pokemon"][0].clone(), raw["in_play_pokemon"][1].clone()], seat)));
    let mut turn_effects = Vec::new();
    if let Some(m) = raw["turn_effects"].as_object() {
        for (turn, list) in m {
            for e in list.as_array().into_iter().flatten() {
                let mut e = e.clone();
                if seat == 1 {
                    swap_players(&mut e);
                }
                turn_effects.push(json!({"turn": turn.parse::<u64>().unwrap_or(0), "effect": e}));
            }
        }
    }
    let stadium = match &st.active_stadium {
        None => Value::Null,
        Some(c) => {
            let owner = st.active_stadium_owner.ok_or("a Stadium with no owner")?;
            json!({"card": card_str(c), "owner": if owner == seat { 0 } else { 1 }})
        }
    };
    let (mz, oz) = (zone(me), zone(opp));
    Ok(json!({
        "id": id, "deck": deck_key, "filler": opp_key, "turn_count": st.turn_count, "points": [st.points[me], st.points[opp]],
        "me": {"hand": strs(&st.hands[me]), "top": strs(&st.decks[me].cards), "deck_count": st.decks[me].cards.len(),
               "discard": strs(&st.discard_piles[me]), "discard_energy": energies(&st.discard_energies[me]), "board": board(me),
               "energy_now": mz.0, "energy_next": mz.1, "knockouts": own_ko},
        "opp": {"hand_count": st.hands[opp].len(), "deck_count": st.decks[opp].cards.len(), "discard": strs(&st.discard_piles[opp]),
                "discard_energy": energies(&st.discard_energies[opp]), "board": board(opp), "energy_now": oz.0, "energy_next": oz.1, "knockouts": ko},
        "stadium": stadium, "turn_effects": turn_effects, "flags": Value::Object(flags), "km3_move": km3_move,
    }))
}

/// The export requests: game key -> (decision, id, recorded km3_move).
fn parse_requests(text: &str) -> Result<BTreeMap<String, Vec<(usize, String, Option<String>)>>, String> {
    let mut out: BTreeMap<String, Vec<(usize, String, Option<String>)>> = BTreeMap::new();
    for (n, line) in text.lines().enumerate() {
        let c: Vec<&str> = line.split('\t').collect();
        if line.trim().is_empty() || (n == 0 && c[0] == "id") {
            continue;
        }
        if c.len() < 3 {
            return Err(format!("line {}: expected id, game key, decision [, km3_move]", n + 1));
        }
        let d: usize = c[2].trim().parse().map_err(|_| format!("line {}: decision '{}' is not a number", n + 1, c[2]))?;
        let rec = c.get(3).map(|s| s.trim()).filter(|s| !s.is_empty()).map(String::from);
        out.entry(c[1].trim().to_string()).or_default().push((d, c[0].trim().to_string(), rec));
    }
    Ok(out)
}

/// The board at one of the deck side's decisions (the true state before it), with the forecasts.
fn board(state: &State, seat: usize, actions: &[Action], labels: &[String], chosen: &Action, decks: &(Deck, Deck)) -> Value {
    let opp = 1 - seat;
    let ours: Vec<Value> = actions
        .iter()
        .zip(labels)
        .filter(|(a, _)| is_attack(a))
        .map(|(a, l)| {
            let SimpleAction::Attack(at) = &a.action else { unreachable!() };
            json!({"move": l, "cost": at.energy_required.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(), "printed_damage": at.fixed_damage,
                   "forecast": forecast(state, a, opp, decks)})
        })
        .collect();
    let mut theirs = Vec::new();
    if let Some(Card::Pokemon(pc)) = state.in_play_pokemon[opp][0].as_ref().map(|p| &p.card) {
        let mut as_if = state.clone();
        as_if.current_player = opp;
        as_if.move_generation_stack.clear();
        for at in &pc.attacks {
            let a = Action { actor: opp, action: SimpleAction::Attack(at.clone()), is_stack: false };
            theirs.push(json!({"attack": at.title, "cost": at.energy_required.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
                               "printed_damage": at.fixed_damage, "forecast_against_ours": forecast(&as_if, &a, seat, decks)}));
        }
    }
    json!({"turn": state.turn_count, "points": [state.points[seat], state.points[opp]],
           "ours": side(state, seat), "theirs": side(state, opp),
           "hand": state.hands[seat].iter().map(|c| c.get_name()).collect::<Vec<_>>(), "deck_count": state.decks[seat].cards.len(),
           "legal": labels, "taken": harness_label(chosen, state), "our_attacks": ours, "their_active_attacks": theirs})
}

/// Plays the moves a log records, each found by its label among the legal moves; at an ambiguous label, the option `forced`
/// names (else the first). Records every decision it is asked for.
#[derive(Debug)]
struct Scripted {
    logged: Vec<Logged>,
    next: usize,
    deck: Deck,
    forced: BTreeMap<usize, usize>,
    log: Arc<Mutex<ScriptLog>>,
    /// The true state before the current tick (set by the replay loop), for the board records.
    truth: Arc<Mutex<Option<State>>>,
    seat: usize,
    decks: (Deck, Deck),
    km: Option<Box<dyn Player>>,
    km_all: bool,
    board_turns: BTreeSet<u64>,
    /// The pilot that played this side, asked only where a label names more than one legal move.
    pilot: Box<dyn Player>,
    /// Export requests for this game (decision, id, recorded km3_move), and the deck keys the positions name.
    exports: Vec<(usize, String, Option<String>)>,
    deck_key: String,
    opp_key: String,
}

impl Player for Scripted {
    fn decision_fn(&mut self, _rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        let state = observation.visible_state();
        let k = self.next;
        self.next += 1;
        let want = self.logged.get(k).cloned();
        let labels: Vec<String> = actions.iter().map(|a| harness_label(a, state)).collect();
        let mut log = self.log.lock().unwrap();
        log.used = self.next;
        let Some(want) = want else {
            log.missing.push(format!("decision {k}: asked beyond the log ({} decisions logged)", self.logged.len()));
            return actions[0].clone();
        };
        if want.turn != state.turn_count as u64 || want.n != actions.len() as u64 {
            log.missing.push(format!("decision {k}: logged turn {} with {} legal moves, replayed turn {} with {}", want.turn, want.n,
                                     state.turn_count, actions.len()));
        }
        let me = self.seat;
        let p = json!([state.points[me], state.points[1 - me]]);
        let act = state.in_play_pokemon[me][0].as_ref().map(|c| c.get_name()).unwrap_or_default();
        let b = state.in_play_pokemon[me][1..].iter().filter(|c| c.is_some()).count() as u64;
        if want.p != p || want.act != act || want.b != b {
            log.missing.push(format!("decision {k}: logged p {} act '{}' b {}, replayed p {p} act '{act}' b {b}", want.p, want.act, want.b));
        }
        let mut distinct: Vec<Action> = Vec::new();
        for (a, l) in actions.iter().zip(&labels) {
            if *l == want.label && !distinct.contains(a) {
                distinct.push(a.clone());
            }
        }
        let chosen = match distinct.len() {
            0 => {
                log.missing.push(format!("decision {k}: '{}' matched no legal move", want.label));
                actions[0].clone()
            }
            1 => distinct.remove(0),
            n => {
                log.ambiguous.push((k, n));
                // the pilot that played, asked from this decision's own observation and search randomness
                let asked = self.pilot.decision_fn(&mut _rng.clone(), observation, actions);
                if let Some(i) = distinct.iter().position(|a| *a == asked) {
                    log.resolved_by_pilot += 1;
                    distinct.remove(i)
                } else {
                    log.unresolved += 1;
                    let i = self.forced.get(&k).copied().unwrap_or(0).min(n - 1);
                    distinct.remove(i)
                }
            }
        };
        let attacks: Vec<String> = actions.iter().zip(&labels).filter(|(a, _)| is_attack(a)).map(|(_, l)| l.clone()).collect();
        // km3's proposal from this decision's own observation and search randomness (a copy of the seed play_tick gave the pilot here)
        let km = match &mut self.km {
            Some(km) if self.km_all || !attacks.is_empty() || self.exports.iter().any(|e| e.0 == k) => Some(km.decision_fn(&mut _rng.clone(), observation, actions)),
            _ => None,
        };
        log.decisions.push(json!({
            "decision": k, "turn": state.turn_count, "legal": labels, "attack_legal": !attacks.is_empty(), "attacks": attacks,
            "taken": harness_label(&chosen, state), "taken_attack": is_attack(&chosen),
            "km3_move": km.as_ref().map(|a| harness_label(a, state)), "km3_attacked": km.as_ref().map(is_attack),
        }));
        if let Some((_, id, recorded)) = self.exports.iter().find(|e| e.0 == k) {
            let truth = self.truth.lock().unwrap().clone().expect("the true state before the tick");
            let mine = km.as_ref().map(|a| harness_label(a, state));
            let made = match (recorded, &mine) {
                (Some(r), m) if m.as_ref() != Some(r) => Err(format!("the old engine's km3 here is {:?}, the recorded km3_move is {r:?}", m)),
                _ => export_position(&truth, self.seat, id, &self.deck_key, &self.opp_key, mine.as_deref()),
            };
            log.exports.push(match made {
                Ok(p) => json!({"id": id, "decision": k, "position": p}),
                Err(why) => json!({"id": id, "decision": k, "dropped": why}),
            });
        }
        if self.board_turns.contains(&(state.turn_count as u64)) {
            let truth = self.truth.lock().unwrap().clone().expect("the true state before the tick");
            let mut b = board(&truth, self.seat, actions, &labels, &chosen, &self.decks);
            b["decision"] = json!(k);
            b["km3_move"] = json!(km.as_ref().map(|a| harness_label(a, state)));
            log.boards.push(b);
        }
        chosen
    }
    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        actions[0].clone()
    }
}

/// Replays one record; returns its check line and its decision lines.
/// The replay's options: km3's proposals, and the skip turns (key -> turns) whose boards are written.
struct Options {
    km3: bool,
    km3_all: bool,
    board_turns: BTreeMap<String, BTreeSet<u64>>,
    /// Export requests by game key (`--export`).
    exports: BTreeMap<String, Vec<(usize, String, Option<String>)>>,
}

fn replay(g: &Value, lists: &BTreeMap<String, Deck>, opt: &Options) -> (Value, Vec<Value>, Vec<Value>, Vec<Value>) {
    let (dn, on) = (g["deck"].as_str().unwrap(), g["opp"].as_str().unwrap());
    let seat = g["seat"].as_u64().unwrap() as usize;
    let seed = g["seed"].as_u64().unwrap();
    let (dd, od) = (&lists[dn], &lists[on]);
    let (d0, d1) = if seat == 0 { (dd, od) } else { (od, dd) };
    let logged: Vec<Logged> = g["log"]
        .as_array()
        .expect("the record has no deck-side log (log_level none): nothing to replay from")
        .iter()
        .map(|e| Logged {
            label: e["a"].as_str().unwrap().to_string(),
            turn: e["t"].as_u64().unwrap(),
            n: e["n"].as_u64().unwrap(),
            p: e["p"].clone(),
            act: e["act"].as_str().unwrap_or("").to_string(),
            b: e["b"].as_u64().unwrap_or(u64::MAX),
        })
        .collect();
    let winner_of = |end: &State| match end.winner {
        Some(GameOutcome::Win(w)) if w == seat => "deck",
        Some(GameOutcome::Win(_)) => "opp",
        _ => "tie",
    };
    let opp_code = parse_player_code(g["pilot_opp"].as_str().unwrap()).unwrap();
    let mut forced: BTreeMap<usize, usize> = BTreeMap::new();
    let mut attempts = 0;
    loop {
        attempts += 1;
        let log = Arc::new(Mutex::new(ScriptLog::default()));
        let mut players = create_players(d0.clone(), d1.clone(), vec![opp_code.clone(), opp_code.clone()]);
        let truth = Arc::new(Mutex::new(None));
        let mine = opt.exports.get(g["key"].as_str().unwrap()).cloned().unwrap_or_default();
        let km: Option<Box<dyn Player>> = (opt.km3 || opt.km3_all || !mine.is_empty())
            .then(|| create_players(d0.clone(), d1.clone(), vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()]).remove(seat));
        let pilot_code = parse_player_code(g["pilot_deck"].as_str().unwrap()).unwrap();
        let codes = if seat == 0 { vec![pilot_code, opp_code.clone()] } else { vec![opp_code.clone(), pilot_code] };
        let pilot = create_players(d0.clone(), d1.clone(), codes).remove(seat);
        players[seat] = Box::new(Scripted {
            logged: logged.clone(), next: 0, deck: dd.clone(), forced: forced.clone(), log: log.clone(), truth: truth.clone(), seat,
            decks: (d0.clone(), d1.clone()), km, km_all: opt.km3_all,
            board_turns: opt.board_turns.get(g["key"].as_str().unwrap()).cloned().unwrap_or_default(),
            pilot, exports: mine, deck_key: dn.to_string(), opp_key: on.to_string(),
        });
        let mut game = Game::new(players, seed);
        let (mut ticks, mut opp_asked) = (0usize, 0u64);
        while !game.is_game_over() && ticks < 20_000 {
            let st = game.get_state_clone();
            let (actor, acts) = st.generate_possible_actions();
            opp_asked += (actor != seat && acts.len() > 1) as u64;
            *truth.lock().unwrap() = Some(st);
            game.play_tick();
            ticks += 1;
        }
        let end = game.get_state_clone();
        let log = log.lock().unwrap().clone();
        let same = log.missing.is_empty()
            && log.used == logged.len()
            && g["points"] == json!([end.points[seat], end.points[1 - seat]])
            && g["turns"].as_u64() == Some(end.turn_count as u64)
            && g["winner"] == winner_of(&end)
            && g["plies"].as_u64() == Some(ticks as u64)
            && g["moves_opp"]["n"].as_u64() == Some(opp_asked);
        let next = log.ambiguous.iter().rev().find(|(d, n)| forced.get(d).copied().unwrap_or(0) + 1 < *n).copied();
        if same || next.is_none() || attempts >= 64 {
            let check = json!({"key": g["key"], "arm": g["arm"], "pilot_deck": g["pilot_deck"], "replayed_exactly": same,
                               "decisions_logged": logged.len(), "decisions_used": log.used, "missing": log.missing,
                               "ambiguous": log.ambiguous.len(), "ambiguous_resolved_by_pilot": log.resolved_by_pilot,
                               "ambiguous_unresolved": log.unresolved, "attempts": attempts,
                               "checked": ["label", "turn", "n", "p", "act", "b", "points", "turns", "winner", "plies", "moves_opp_n"],
                               "plies": ticks, "moves_opp_n": opp_asked,
                               "turns": end.turn_count, "points": [end.points[seat], end.points[1 - seat]], "winner": winner_of(&end)});
            let rows = log
                .decisions
                .into_iter()
                .map(|mut d| {
                    d["key"] = g["key"].clone();
                    d["arm"] = g["arm"].clone();
                    d["pilot"] = g["pilot_deck"].clone();
                    d["deck"] = g["deck"].clone();
                    d["first"] = g["first"].clone();
                    d["replayed_exactly"] = json!(same);
                    d
                })
                .collect();
            let boards = log
                .boards
                .into_iter()
                .map(|mut b| {
                    b["key"] = g["key"].clone();
                    b["pilot"] = g["pilot_deck"].clone();
                    b["replayed_exactly"] = json!(same);
                    b
                })
                .collect();
            // an export is kept only from a game that replayed exactly (otherwise its states are not the recorded game's)
            let key = g["key"].clone();
            let mut reached: BTreeSet<usize> = BTreeSet::new();
            let mut exports: Vec<Value> = log
                .exports
                .into_iter()
                .map(|mut e| {
                    reached.insert(e["decision"].as_u64().unwrap() as usize);
                    e["key"] = key.clone();
                    if same || e.get("dropped").is_some() {
                        e
                    } else {
                        json!({"id": e["id"], "decision": e["decision"], "key": key, "dropped": "the game did not replay exactly"})
                    }
                })
                .collect();
            for (d, id, _) in opt.exports.get(g["key"].as_str().unwrap()).into_iter().flatten() {
                if !reached.contains(d) {
                    exports.push(json!({"id": id, "decision": d, "key": key, "dropped": format!("decision {d} was never asked of the deck side (the log has {})", logged.len())}));
                }
            }
            return (check, rows, boards, exports);
        }
        let (d, _) = next.unwrap();
        let tried = forced.get(&d).copied().unwrap_or(0);
        forced.retain(|&k, _| k < d);
        forced.insert(d, tried + 1);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let manifest: Value = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--manifest").expect("--manifest")).unwrap()).unwrap();
    let arm = arg(&args, "--arm").expect("--arm");
    let limit: usize = arg(&args, "--limit").map_or(usize::MAX, |n| n.parse().unwrap());
    let threads: usize = arg(&args, "--threads").map_or(4, |n| n.parse().unwrap());
    let lists: BTreeMap<String, Deck> = manifest["decks"]
        .as_array()
        .unwrap()
        .iter()
        .chain(manifest["opponents"].as_array().unwrap())
        .map(|d| (d["name"].as_str().unwrap().to_string(), Deck::from_file(d["path"].as_str().unwrap()).unwrap()))
        .collect();
    let records: Vec<Value> = std::fs::read_to_string(arg(&args, "--games").expect("--games"))
        .unwrap()
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| serde_json::from_str::<Value>(l).unwrap())
        .filter(|g| g["arm"] == arm.as_str())
        .take(limit)
        .collect();
    let mut board_turns: BTreeMap<String, BTreeSet<u64>> = BTreeMap::new();
    if let Some(path) = arg(&args, "--boards") {
        let bot = arg(&args, "--bot").expect("--bot with --boards");
        for line in std::fs::read_to_string(path).unwrap().lines().skip(1) {
            let c: Vec<&str> = line.split('\t').collect();
            if c[0] == bot {
                board_turns.entry(c[1].to_string()).or_default().insert(c[2].parse().unwrap());
            }
        }
    }
    let exports = arg(&args, "--export").map_or_else(BTreeMap::new, |p| parse_requests(&std::fs::read_to_string(p).unwrap()).unwrap_or_else(|e| panic!("--export: {e}")));
    let export_keys: BTreeSet<String> = exports.keys().cloned().collect();
    let opt = Options { km3: args.iter().any(|a| a == "--km3"), km3_all: args.iter().any(|a| a == "--km3-all"), board_turns, exports };
    std::panic::set_hook(Box::new(|_| {}));   // a forecast the engine refuses is caught and recorded; keep stderr quiet
    let next = AtomicUsize::new(0);
    let out: Mutex<Vec<(usize, Value, Vec<Value>, Vec<Value>, Vec<Value>)>> = Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..threads {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::SeqCst);
                if i >= records.len() {
                    break;
                }
                let (check, rows, boards, exports) = replay(&records[i], &lists, &opt);
                out.lock().unwrap().push((i, check, rows, boards, exports));
            });
        }
    });
    let mut out = out.into_inner().unwrap();
    out.sort_by_key(|(i, _, _, _, _)| *i);
    let mut fd = std::fs::File::create(arg(&args, "--out").expect("--out")).unwrap();
    let mut fc = std::fs::File::create(arg(&args, "--check").expect("--check")).unwrap();
    use std::io::Write;
    let mut fb = arg(&args, "--boards-out").map(|p| std::fs::File::create(p).unwrap());
    let (mut exact, mut rows_n, mut boards_n) = (0, 0, 0);
    let (mut positions, mut dropped): (Vec<Value>, Vec<String>) = (Vec::new(), Vec::new());
    let seen: BTreeSet<String> = out.iter().map(|o| o.1["key"].as_str().unwrap_or_default().to_string()).collect();
    for k in export_keys.iter().filter(|k| !seen.contains(*k)) {
        for (d, id, _) in &opt.exports[k] {
            dropped.push(format!("{id}\t{k}\t{d}\tno record of this game key in --games for arm {arm}"));
        }
    }
    for (_, check, rows, boards, exports) in &out {
        for e in exports {
            match e.get("position") {
                Some(p) => positions.push(p.clone()),
                None => dropped.push(format!("{}\t{}\t{}\t{}", e["id"].as_str().unwrap_or(""), e["key"].as_str().unwrap_or(""), e["decision"], e["dropped"].as_str().unwrap_or(""))),
            }
        }
        if let Some(fb) = fb.as_mut() {
            for b in boards {
                writeln!(fb, "{}", b).unwrap();
                boards_n += 1;
            }
        }
        exact += check["replayed_exactly"].as_bool().unwrap() as usize;
        writeln!(fc, "{}", check).unwrap();
        for r in rows {
            writeln!(fd, "{}", r).unwrap();
            rows_n += 1;
        }
    }
    if let Some(p) = arg(&args, "--pos-out") {
        std::fs::write(p, serde_json::to_string_pretty(&positions).unwrap()).unwrap();
    }
    if let Some(p) = arg(&args, "--drop-out") {
        std::fs::write(p, format!("id\tkey\tdecision\treason\n{}", dropped.iter().map(|d| format!("{d}\n")).collect::<String>())).unwrap();
    }
    if !export_keys.is_empty() {
        println!("export: {} positions written, {} requests dropped", positions.len(), dropped.len());
    }
    println!("skip_replay: arm {arm}: {} games, replayed exactly {exact}; {rows_n} deck-side decisions; {boards_n} board records", out.len());
}

#[cfg(test)]
mod tests {
    //! The export mode's tests (`cargo test --release --example skip_replay`, from engine/ with this file copied into engine/examples/).
    use super::*;

    /// Deck 12's file; the tests run with it named in SKIP_TEST_DECK when this file is built in a copy of the engine tree.
    fn deck_path() -> String {
        std::env::var("SKIP_TEST_DECK").unwrap_or_else(|_| "../decks/dustin/12-ariados-whimsicott-ogerpon.txt".to_string())
    }

    /// A real mid-game state in which `seat` is asked a turn-level decision (empty stack, two or more legal moves).
    fn midgame(seat: usize, seed: u64) -> State {
        let d = Deck::from_file(&deck_path()).unwrap();
        let r = || parse_player_code("r").unwrap();
        let mut g = Game::new(create_players(d.clone(), d, vec![r(), r()]), seed);
        for _ in 0..4000 {
            let st = g.get_state_clone();
            let (actor, acts) = st.generate_possible_actions();
            if !g.is_game_over() && st.turn_count >= 6 && actor == seat && acts.len() > 1 && st.move_generation_stack.is_empty() {
                return st;
            }
            if g.is_game_over() {
                break;
            }
            g.play_tick();
        }
        panic!("no turn-level decision for seat {seat} at seed {seed}");
    }

    fn names(v: &Value) -> Vec<String> {
        v.as_array().unwrap().iter().map(|x| x.as_str().unwrap().to_string()).collect()
    }

    #[test]
    fn the_position_is_the_deck_sides_view_with_the_deck_in_order() {
        for seat in [0usize, 1] {
            let st = midgame(seat, 20_000_000_100 + seat as u64);
            let p = export_position(&st, seat, "t1", "deck12", "deck12", Some("EndTurn")).unwrap();
            assert_eq!(p["id"], "t1");
            assert_eq!(p["deck"], "deck12");
            assert_eq!(p["turn_count"], st.turn_count as u64);
            assert_eq!(p["points"], json!([st.points[seat], st.points[1 - seat]]));
            assert_eq!(names(&p["me"]["hand"]), st.hands[seat].iter().map(card_str).collect::<Vec<_>>());
            assert_eq!(names(&p["me"]["top"]), st.decks[seat].cards.iter().map(card_str).collect::<Vec<_>>());
            assert_eq!(p["me"]["deck_count"], st.decks[seat].cards.len() as u64);
            assert_eq!(p["opp"]["hand_count"], st.hands[1 - seat].len() as u64);
            assert_eq!(p["opp"]["deck_count"], st.decks[1 - seat].cards.len() as u64);
            assert_eq!(names(&p["opp"]["discard"]), st.discard_piles[1 - seat].iter().map(card_str).collect::<Vec<_>>());
            assert_eq!(p["km3_move"], "EndTurn");
            let active = st.in_play_pokemon[seat][0].as_ref().unwrap();
            assert_eq!(p["me"]["board"][0]["card"], card_str(&active.card));
            assert_eq!(p["me"]["board"][0]["hp"], active.get_remaining_hp() as u64);
        }
    }

    #[test]
    fn the_exact_board_and_flags_travel_in_the_flags_key_swapped_for_seat_one() {
        for seat in [0usize, 1] {
            let st = midgame(seat, 20_000_000_200 + seat as u64);
            let p = export_position(&st, seat, "t2", "deck12", "deck12", None).unwrap();
            let raw = serde_json::to_value(&st).unwrap();
            // the first slot of "in_play_pokemon" in the flags is the deck side's own board, byte for byte
            assert_eq!(p["flags"]["in_play_pokemon"][0], raw["in_play_pokemon"][seat]);
            assert_eq!(p["flags"]["in_play_pokemon"][1], raw["in_play_pokemon"][1 - seat]);
            assert_eq!(p["flags"]["has_used_stadium"], json!([raw["has_used_stadium"][seat], raw["has_used_stadium"][1 - seat]]));
            assert_eq!(p["flags"]["attack_name_used_count"], json!([raw["attack_name_used_count"][seat], raw["attack_name_used_count"][1 - seat]]));
            assert_eq!(p["flags"]["has_played_support"], raw["has_played_support"]);
            assert_eq!(p["flags"]["has_retreated"], raw["has_retreated"]);
            assert_eq!(p["me"]["knockouts"], raw["own_knockouts_this_game"][seat]);
            assert_eq!(p["opp"]["knockouts"], raw["own_knockouts_this_game"][1 - seat]);
            assert_eq!(p["me"]["energy_next"], raw["energy_zone"][seat]["next"]);
        }
    }

    #[test]
    fn player_indices_inside_a_turn_effect_are_swapped_for_seat_one() {
        let mut v = json!({"ReducedDamageForTarget": {"amount": 20, "player": 0, "scope": "AllOwn", "only_from_ex": false}});
        swap_players(&mut v);
        assert_eq!(v["ReducedDamageForTarget"]["player"], 1);
        assert_eq!(v["ReducedDamageForTarget"]["amount"], 20);
    }

    #[test]
    fn a_pending_choice_or_the_other_seats_turn_is_refused_with_a_reason() {
        let st = midgame(0, 20_000_000_300);
        assert!(export_position(&st, 1, "t3", "d", "d", None).unwrap_err().contains("not the deck side's"));
        let mut s2 = st.clone();
        s2.move_generation_stack.push((0, vec![SimpleAction::EndTurn]));
        assert!(export_position(&s2, 0, "t3", "d", "d", None).unwrap_err().contains("queued choice"));
    }

    #[test]
    fn requests_parse_with_and_without_a_recorded_move() {
        let r = parse_requests("id\tkey\tdecision\tkm3_move\nA\tg1\t14\tAttack:Pierce\nB\tg2\t3\n\n").unwrap();
        assert_eq!(r["g1"], vec![(14usize, "A".to_string(), Some("Attack:Pierce".to_string()))]);
        assert_eq!(r["g2"], vec![(3usize, "B".to_string(), None)]);
    }

    /// Records the deck side's decisions in the harness's log form while a real pilot plays them.
    #[derive(Debug)]
    struct Recorder {
        inner: Box<dyn Player>,
        deck: Deck,
        seat: usize,
        log: Arc<Mutex<Vec<Value>>>,
    }
    impl Player for Recorder {
        fn decision_fn(&mut self, rng: &mut StdRng, o: &PlayerObservation, actions: &[Action]) -> Action {
            let a = self.inner.decision_fn(rng, o, actions);
            let st = o.visible_state();
            let me = self.seat;
            self.log.lock().unwrap().push(json!({"a": harness_label(&a, st), "t": st.turn_count, "n": actions.len(), "p": [st.points[me], st.points[1 - me]],
                "act": st.in_play_pokemon[me][0].as_ref().map(|c| c.get_name()).unwrap_or_default(),
                "b": st.in_play_pokemon[me][1..].iter().filter(|c| c.is_some()).count()}));
            a
        }
        fn get_deck(&self) -> Deck {
            self.deck.clone()
        }
        fn decide_omniscient(&mut self, rng: &mut StdRng, s: &State, actions: &[Action]) -> Action {
            self.inner.decide_omniscient(rng, s, actions)
        }
    }

    /// A km3 v km3 game played and logged as the harness logs it, then replayed with export requests: the whole route in one process.
    /// With SKIP_E2E_OUT set, the exported positions are written there (for pg_pos, test_skip_positions.E2E).
    #[test]
    fn replaying_a_logged_game_with_export_requests_writes_the_states_the_game_had() {
        for seat in [0usize, 1] {
            let deck = Deck::from_file(&deck_path()).unwrap();
            let code = parse_player_code("km3").unwrap();
            let seed = 20_000_000_400 + seat as u64;
            let log = Arc::new(Mutex::new(Vec::new()));
            let mut players = create_players(deck.clone(), deck.clone(), vec![code.clone(), code.clone()]);
            let inner = create_players(deck.clone(), deck.clone(), vec![code.clone(), code.clone()]).remove(seat);
            players[seat] = Box::new(Recorder { inner, deck: deck.clone(), seat, log: log.clone() });
            let mut game = Game::new(players, seed);
            let (mut ticks, mut opp_asked) = (0usize, 0u64);
            let mut truth_at: BTreeMap<usize, State> = BTreeMap::new();
            let mut asked = 0usize;
            while !game.is_game_over() && ticks < 20_000 {
                let st = game.get_state_clone();
                let (actor, acts) = st.generate_possible_actions();
                opp_asked += (actor != seat && acts.len() > 1) as u64;
                if actor == seat && acts.len() > 1 {
                    truth_at.insert(asked, st);
                    asked += 1;
                }
                game.play_tick();
                ticks += 1;
            }
            let end = game.get_state_clone();
            let rec = json!({"key": format!("e2e|{seat}"), "arm": "X", "deck": "d12", "opp": "d12", "seat": seat, "seed": seed, "first": "n/a",
                "log": *log.lock().unwrap(), "pilot_opp": "km3", "pilot_deck": "km3", "points": [end.points[seat], end.points[1 - seat]],
                "turns": end.turn_count, "plies": ticks, "moves_opp": {"n": opp_asked},
                "winner": match end.winner { Some(GameOutcome::Win(w)) if w == seat => "deck", Some(GameOutcome::Win(_)) => "opp", _ => "tie" }});
            assert_eq!(asked, log.lock().unwrap().len());
            // the requests: every turn-level decision from turn 4 on, up to 6 of them, with km3's own move as the recorded one
            let wanted: Vec<usize> = truth_at.iter()
                .filter(|(_, s)| s.turn_count >= 4 && s.move_generation_stack.is_empty()).map(|(k, _)| *k).step_by(5).take(6).collect();
            assert!(wanted.len() >= 3, "too few turn-level decisions: {}", wanted.len());
            let recorded: Vec<String> = wanted.iter().map(|k| rec["log"][*k]["a"].as_str().unwrap().to_string()).collect();
            let text: String = wanted.iter().zip(&recorded).map(|(k, r)| format!("p{seat}_{k}\te2e|{seat}\t{k}\t{r}\n")).collect();
            let opt = Options { km3: false, km3_all: false, board_turns: BTreeMap::new(), exports: parse_requests(&text).unwrap() };
            let lists: BTreeMap<String, Deck> = [("d12".to_string(), deck.clone())].into_iter().collect();
            let (check, _, _, exports) = replay(&rec, &lists, &opt);
            assert_eq!(check["replayed_exactly"], true, "{check}");
            assert_eq!(exports.len(), wanted.len());
            for (e, k) in exports.iter().zip(&wanted) {
                // km3 asked at the replayed decision is km3 as it played: the recorded move agrees, so nothing is dropped
                let p = e.get("position").unwrap_or_else(|| panic!("decision {k} dropped: {e}"));
                let t = &truth_at[k];
                assert_eq!(p["turn_count"], t.turn_count as u64);
                assert_eq!(names(&p["me"]["hand"]), t.hands[seat].iter().map(card_str).collect::<Vec<_>>());
                assert_eq!(p["km3_move"], rec["log"][*k]["a"]);
            }
            if let Ok(path) = std::env::var("SKIP_E2E_OUT") {
                let ps: Vec<Value> = exports.iter().map(|e| e["position"].clone()).collect();
                std::fs::write(format!("{path}.{seat}.json"), serde_json::to_string_pretty(&ps).unwrap()).unwrap();
            }
        }
    }
}
