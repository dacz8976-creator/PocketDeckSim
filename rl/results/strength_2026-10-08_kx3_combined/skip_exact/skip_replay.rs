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
//!   skip_replay --games <games.jsonl> --manifest <manifest.json> --arm X|ref --out decisions.jsonl --check check.jsonl
//!               [--threads N] [--limit N]
//! Run from the repository root the manifest's deck paths are relative to.
use std::collections::BTreeMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

use deckgym::actions::{Action, SimpleAction};
use deckgym::models::Card;
use deckgym::observation::PlayerObservation;
use deckgym::players::{create_players, parse_player_code, Player};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
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
}

/// What a scripted replay saw.
#[derive(Debug, Default, Clone)]
struct ScriptLog {
    used: usize,
    missing: Vec<String>,
    ambiguous: Vec<(usize, usize)>,
    decisions: Vec<Value>,
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
                let i = self.forced.get(&k).copied().unwrap_or(0).min(n - 1);
                distinct.remove(i)
            }
        };
        let attacks: Vec<String> = actions.iter().zip(&labels).filter(|(a, _)| is_attack(a)).map(|(_, l)| l.clone()).collect();
        log.decisions.push(json!({
            "decision": k, "turn": state.turn_count, "legal": labels, "attack_legal": !attacks.is_empty(), "attacks": attacks,
            "taken": harness_label(&chosen, state), "taken_attack": is_attack(&chosen),
        }));
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
fn replay(g: &Value, lists: &BTreeMap<String, Deck>) -> (Value, Vec<Value>) {
    let (dn, on) = (g["deck"].as_str().unwrap(), g["opp"].as_str().unwrap());
    let seat = g["seat"].as_u64().unwrap() as usize;
    let seed = g["seed"].as_u64().unwrap();
    let (dd, od) = (&lists[dn], &lists[on]);
    let (d0, d1) = if seat == 0 { (dd, od) } else { (od, dd) };
    let logged: Vec<Logged> = g["log"]
        .as_array()
        .expect("the record has no deck-side log (log_level none): nothing to replay from")
        .iter()
        .map(|e| Logged { label: e["a"].as_str().unwrap().to_string(), turn: e["t"].as_u64().unwrap(), n: e["n"].as_u64().unwrap() })
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
        players[seat] = Box::new(Scripted { logged: logged.clone(), next: 0, deck: dd.clone(), forced: forced.clone(), log: log.clone() });
        let mut game = Game::new(players, seed);
        let mut ticks = 0usize;
        while !game.is_game_over() && ticks < 20_000 {
            game.play_tick();
            ticks += 1;
        }
        let end = game.get_state_clone();
        let log = log.lock().unwrap().clone();
        let same = log.missing.is_empty()
            && log.used == logged.len()
            && g["points"] == json!([end.points[seat], end.points[1 - seat]])
            && g["turns"].as_u64() == Some(end.turn_count as u64)
            && g["winner"] == winner_of(&end);
        let next = log.ambiguous.iter().rev().find(|(d, n)| forced.get(d).copied().unwrap_or(0) + 1 < *n).copied();
        if same || next.is_none() || attempts >= 64 {
            let check = json!({"key": g["key"], "arm": g["arm"], "pilot_deck": g["pilot_deck"], "replayed_exactly": same,
                               "decisions_logged": logged.len(), "decisions_used": log.used, "missing": log.missing,
                               "ambiguous": log.ambiguous.len(), "attempts": attempts,
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
            return (check, rows);
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
    assert!(records.iter().all(|g| g["pilot_opp"] == "km3"), "the opponent must be km3");
    let next = AtomicUsize::new(0);
    let out: Mutex<Vec<(usize, Value, Vec<Value>)>> = Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..threads {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::SeqCst);
                if i >= records.len() {
                    break;
                }
                let (check, rows) = replay(&records[i], &lists);
                out.lock().unwrap().push((i, check, rows));
            });
        }
    });
    let mut out = out.into_inner().unwrap();
    out.sort_by_key(|(i, _, _)| *i);
    let mut fd = std::fs::File::create(arg(&args, "--out").expect("--out")).unwrap();
    let mut fc = std::fs::File::create(arg(&args, "--check").expect("--check")).unwrap();
    use std::io::Write;
    let (mut exact, mut rows_n) = (0, 0);
    for (_, check, rows) in &out {
        exact += check["replayed_exactly"].as_bool().unwrap() as usize;
        writeln!(fc, "{}", check).unwrap();
        for r in rows {
            writeln!(fd, "{}", r).unwrap();
            rows_n += 1;
        }
    }
    println!("skip_replay: arm {arm}: {} games, replayed exactly {exact}; {rows_n} deck-side decisions", out.len());
}
