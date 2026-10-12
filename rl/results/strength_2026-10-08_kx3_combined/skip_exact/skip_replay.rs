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
//!   skip_replay --games <games.jsonl> --manifest <manifest.json> --arm X|ref --out decisions.jsonl --check check.jsonl
//!               [--threads N] [--limit N] [--km3 | --km3-all] [--boards skip_turns.tsv --bot NAME --boards-out boards.jsonl]
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
}

/// What a scripted replay saw.
#[derive(Debug, Default, Clone)]
struct ScriptLog {
    used: usize,
    missing: Vec<String>,
    ambiguous: Vec<(usize, usize)>,
    decisions: Vec<Value>,
    boards: Vec<Value>,
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
        // km3's proposal from this decision's own observation and search randomness (a copy of the seed play_tick gave the pilot here)
        let km = match &mut self.km {
            Some(km) if self.km_all || !attacks.is_empty() => Some(km.decision_fn(&mut _rng.clone(), observation, actions)),
            _ => None,
        };
        log.decisions.push(json!({
            "decision": k, "turn": state.turn_count, "legal": labels, "attack_legal": !attacks.is_empty(), "attacks": attacks,
            "taken": harness_label(&chosen, state), "taken_attack": is_attack(&chosen),
            "km3_move": km.as_ref().map(|a| harness_label(a, state)), "km3_attacked": km.as_ref().map(is_attack),
        }));
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
}

fn replay(g: &Value, lists: &BTreeMap<String, Deck>, opt: &Options) -> (Value, Vec<Value>, Vec<Value>) {
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
        let truth = Arc::new(Mutex::new(None));
        let km: Option<Box<dyn Player>> = (opt.km3 || opt.km3_all)
            .then(|| create_players(d0.clone(), d1.clone(), vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()]).remove(seat));
        players[seat] = Box::new(Scripted {
            logged: logged.clone(), next: 0, deck: dd.clone(), forced: forced.clone(), log: log.clone(), truth: truth.clone(), seat,
            decks: (d0.clone(), d1.clone()), km, km_all: opt.km3_all,
            board_turns: opt.board_turns.get(g["key"].as_str().unwrap()).cloned().unwrap_or_default(),
        });
        let mut game = Game::new(players, seed);
        let mut ticks = 0usize;
        while !game.is_game_over() && ticks < 20_000 {
            *truth.lock().unwrap() = Some(game.get_state_clone());
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
            return (check, rows, boards);
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
    let opt = Options { km3: args.iter().any(|a| a == "--km3"), km3_all: args.iter().any(|a| a == "--km3-all"), board_turns };
    std::panic::set_hook(Box::new(|_| {}));   // a forecast the engine refuses is caught and recorded; keep stderr quiet
    let next = AtomicUsize::new(0);
    let out: Mutex<Vec<(usize, Value, Vec<Value>, Vec<Value>)>> = Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..threads {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::SeqCst);
                if i >= records.len() {
                    break;
                }
                let (check, rows, boards) = replay(&records[i], &lists, &opt);
                out.lock().unwrap().push((i, check, rows, boards));
            });
        }
    });
    let mut out = out.into_inner().unwrap();
    out.sort_by_key(|(i, _, _, _)| *i);
    let mut fd = std::fs::File::create(arg(&args, "--out").expect("--out")).unwrap();
    let mut fc = std::fs::File::create(arg(&args, "--check").expect("--check")).unwrap();
    use std::io::Write;
    let mut fb = arg(&args, "--boards-out").map(|p| std::fs::File::create(p).unwrap());
    let (mut exact, mut rows_n, mut boards_n) = (0, 0, 0);
    for (_, check, rows, boards) in &out {
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
    println!("skip_replay: arm {arm}: {} games, replayed exactly {exact}; {rows_n} deck-side decisions; {boards_n} board records", out.len());
}
