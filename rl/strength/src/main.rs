//! strength: the paired pilot-strength harness (pre-registered, resumable, no engine/ change).
//!
//! It builds against an engine tree by path (see build.sh), so the pilot codes it knows are whatever `parse_player_code` resolves in that
//! engine. Games are the unit of work: every finished game is appended to games.jsonl (flushed) and a stopped run resumes by skipping the
//! keys already there. A pilot spec is either a code the engine knows (km3, kog3, ...) or `ext:<command ...>`, an external process that
//! is asked for each decision over JSON lines (see PROTOCOL.md): a slow pilot, or an LLM choosing among the legal moves, works the same.
//!
//!   strength run --manifest M/manifest.json --out M [--threads 2] [--max-games N] [--stop-after-min M] [--only-deck NAME]... [--dry-run]
//!   strength selfcheck --pilot km3 --deck-a A.txt --deck-b B.txt [--games 20] [--seed-base S]
//!
//! The manifest is written by strength_prereg.py before any game (it holds the pilots, decks, seeds and sizes the run executes).
mod ext;

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::PlayerObservation;
use deckgym::players::{create_players, parse_player_code, Player};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game};
use rand::rngs::StdRng;
use serde_json::{json, Value};
use std::collections::HashSet;
use std::fmt;
use std::io::Write;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

pub fn arg_all(args: &[String], name: &str) -> Vec<String> {
    args.iter().enumerate().filter(|(_, a)| *a == name).filter_map(|(i, _)| args.get(i + 1)).cloned().collect()
}
pub fn arg(args: &[String], name: &str) -> Option<String> {
    arg_all(args, name).into_iter().next()
}

/// A compact name for an action, the same everywhere (logs, intended-line tables, the external protocol).
pub fn label(a: &Action, obs: Option<&PlayerObservation>) -> String {
    let nm = |c: &deckgym::models::Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::UseAbility { in_play_idx } => {
            let title = obs
                .and_then(|o| o.visible_state().in_play_pokemon.get(a.actor).and_then(|s| s.get(*in_play_idx)).and_then(|p| p.as_ref()).cloned())
                .and_then(|p| match &p.card {
                    deckgym::models::Card::Pokemon(pc) => pc.ability.as_ref().map(|ab| ab.title.clone()),
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

/// What one seat's wrapper collects during a game.
#[derive(Default)]
pub struct SeatRec {
    pub times: Vec<f64>,
    pub log: Vec<Value>,
}

/// Times every real decision of the player it wraps and (for the deck under test) logs it compactly.
struct Wrapped {
    inner: Box<dyn Player>,
    rec: Arc<Mutex<SeatRec>>,
    keep_log: bool,
    first: bool, // is this seat the one that goes first
}
impl fmt::Debug for Wrapped {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Wrapped({:?})", self.inner)
    }
}
impl Player for Wrapped {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        let t0 = Instant::now();
        let a = self.inner.decision_fn(rng, observation, possible_actions);
        let dt = t0.elapsed().as_secs_f64();
        let mut r = self.rec.lock().unwrap();
        r.times.push((dt * 1000.0 * 1000.0).round() / 1000.0);
        if self.keep_log {
            let st = observation.visible_state();
            let me = a.actor;
            let t = st.turn_count as u32;
            let own = if self.first { (t + 1) / 2 } else { t / 2 };
            let act = st.in_play_pokemon[me][0].as_ref().map(|p| p.card.get_name()).unwrap_or_default();
            let bench = st.in_play_pokemon[me].iter().skip(1).filter(|p| p.is_some()).count();
            r.log.push(json!({"t": t, "o": own, "a": label(&a, Some(observation)), "n": possible_actions.len(), "ms": (dt * 1000.0 * 10.0).round() / 10.0,
                              "p": [st.points[me], st.points[1 - me]], "act": act, "b": bench}));
        }
        a
    }
    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &deckgym::State, possible_actions: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, state, possible_actions)
    }
}

fn load_deck(root: &Path, rel: &str) -> Deck {
    let p = if Path::new(rel).is_absolute() { PathBuf::from(rel) } else { root.join(rel) };
    let d = Deck::from_file(p.to_str().unwrap()).unwrap_or_else(|e| panic!("deck {rel}: {e}"));
    assert!(d.is_valid(), "deck {rel} is not a valid 20-card list");
    d
}

/// Builds the two seats' players: engine codes through `create_players`, `ext:` specs as external processes.
fn build_players(d0: &Deck, d1: &Deck, spec0: &str, spec1: &str, seed: u64, ext_timeout: Option<f64>, notes: &[ext::Meta; 2]) -> Vec<Box<dyn Player>> {
    let code = |s: &str| parse_player_code(if s.starts_with("ext:") { "r" } else { s }).unwrap_or_else(|e| panic!("pilot {s}: {e}"));
    let mut v = create_players(d0.clone(), d1.clone(), vec![code(spec0), code(spec1)]);
    for (seat, spec) in [spec0, spec1].iter().enumerate() {
        if let Some(cmd) = spec.strip_prefix("ext:") {
            let deck = if seat == 0 { d0 } else { d1 };
            v[seat] = Box::new(ext::ExtPlayer::spawn(cmd, deck.clone(), seat, seed, ext_timeout, notes[seat].clone()));
        }
    }
    v
}

fn fnv(h: &mut u64, bytes: &[u8]) {
    for b in bytes {
        *h ^= *b as u64;
        *h = h.wrapping_mul(0x100000001b3);
    }
}

fn selfcheck(args: &[String]) {
    let root = PathBuf::from(arg(args, "--root").unwrap_or_else(|| ".".into()));
    let pilot = arg(args, "--pilot").unwrap_or_else(|| "km3".into());
    let a = load_deck(&root, &arg(args, "--deck-a").expect("--deck-a"));
    let b = load_deck(&root, &arg(args, "--deck-b").expect("--deck-b"));
    let n: u64 = arg(args, "--games").map(|x| x.parse().unwrap()).unwrap_or(20);
    let base: u64 = arg(args, "--seed-base").map(|x| x.parse().unwrap()).unwrap_or(24_900_000_000);
    let mut h: u64 = 0xcbf29ce484222325;
    let (mut w0, mut w1, mut ties, mut turns) = (0u32, 0u32, 0u32, 0u32);
    for i in 0..n {
        let notes = [ext::new_meta(), ext::new_meta()];
        let mut game = Game::new(build_players(&a, &b, &pilot, &pilot, base + i, None, &notes), base + i);
        let out = game.play();
        let st = game.get_state_clone();
        match out {
            Some(GameOutcome::Win(0)) => w0 += 1,
            Some(GameOutcome::Win(_)) => w1 += 1,
            _ => ties += 1,
        }
        turns += st.turn_count as u32;
        fnv(&mut h, format!("{}|{:?}|{:?}|{}", base + i, out, st.points, st.turn_count).as_bytes());
    }
    println!("selfcheck pilot={pilot} games={n} seat0_wins={w0} seat1_wins={w1} ties={ties} turns={turns} digest={h:016x}");
}

#[derive(Clone)]
struct Job {
    deck: usize,
    opp: usize,
    deal: u64,
    seat: usize,
    arm: &'static str, // "ref" or "X"
    seed: u64,
}

fn key_of(deck: &str, opp: &str, deal: u64, seat: usize, arm: &str) -> String {
    format!("{deck}|{opp}|{deal}|{seat}|{arm}")
}

fn iso_now() -> String {
    chrono::Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Secs, true)
}

fn run(args: &[String]) {
    let mpath = arg(args, "--manifest").expect("--manifest");
    let out_dir = PathBuf::from(arg(args, "--out").expect("--out"));
    let man: Value = serde_json::from_str(&std::fs::read_to_string(&mpath).expect("manifest")).expect("manifest json");
    let root = PathBuf::from(man["repo_root"].as_str().unwrap_or("."));
    let reference = man["reference"].as_str().unwrap().to_string();
    let pilot = man["pilot"].as_str().unwrap().to_string();
    let decks: Vec<(String, String)> = man["decks"].as_array().unwrap().iter().map(|d| (d["name"].as_str().unwrap().into(), d["path"].as_str().unwrap().into())).collect();
    let opps: Vec<(String, String)> = man["opponents"].as_array().unwrap().iter().map(|d| (d["name"].as_str().unwrap().into(), d["path"].as_str().unwrap().into())).collect();
    let deals = man["deals"].as_u64().unwrap();
    let seats: Vec<usize> = man["seats"].as_array().unwrap().iter().map(|s| s.as_u64().unwrap() as usize).collect();
    let seed_base = man["seed_base"].as_u64().unwrap();
    let stride = man["pair_stride"].as_u64().unwrap_or(10_000);
    let log_level = man["log_level"].as_str().unwrap_or("deck").to_string();
    let ext_timeout = man.get("ext_timeout_s").and_then(|x| x.as_f64());
    let threads: usize = arg(args, "--threads").map(|x| x.parse().unwrap()).unwrap_or(man["threads"].as_u64().unwrap_or(2) as usize);
    let max_games: usize = arg(args, "--max-games").map(|x| x.parse().unwrap()).unwrap_or(usize::MAX);
    let stop_after = arg(args, "--stop-after-min").map(|x| Duration::from_secs_f64(x.parse::<f64>().unwrap() * 60.0));
    let only: HashSet<String> = arg_all(args, "--only-deck").into_iter().collect();
    let heldout: HashSet<String> = man["heldout_decks"].as_array().map(|a| a.iter().map(|x| x.as_str().unwrap().to_string()).collect()).unwrap_or_default();
    let locked = man["heldout_locked"].as_bool().unwrap_or(true);
    let stage = man["stage"].as_str().unwrap_or("dev").to_string();
    // the held-out guard: a development run never touches a held-out deck, on either side, while the lock is on
    for (n, _) in decks.iter().chain(opps.iter()) {
        if heldout.contains(n) && (locked || stage != "heldout") {
            panic!("refusing to run: {n} is a held-out deck (stage {stage}, lock {locked}); it is never used in development until the lock is lifted");
        }
    }

    // the job list, in a fixed order
    let mut jobs: Vec<Job> = vec![];
    for (di, (dn, _)) in decks.iter().enumerate() {
        if !only.is_empty() && !only.contains(dn) {
            continue;
        }
        for (oi, (on, _)) in opps.iter().enumerate() {
            if on == dn {
                continue;
            }
            let pair = (di as u64) * 1000 + oi as u64;
            for deal in 0..deals {
                for &seat in &seats {
                    for arm in ["ref", "X"] {
                        jobs.push(Job { deck: di, opp: oi, deal, seat, arm, seed: seed_base + pair * stride + deal });
                    }
                }
            }
        }
    }
    // resume: skip the keys already in games.jsonl (a truncated last line is ignored)
    let games_path = out_dir.join("games.jsonl");
    let mut done: HashSet<String> = HashSet::new();
    if let Ok(s) = std::fs::read_to_string(&games_path) {
        for l in s.lines() {
            if let Ok(v) = serde_json::from_str::<Value>(l) {
                if let Some(k) = v["key"].as_str() {
                    done.insert(k.to_string());
                }
            }
        }
    }
    let total = jobs.len();
    let todo: Vec<Job> = jobs.into_iter().filter(|j| !done.contains(&key_of(&decks[j.deck].0, &opps[j.opp].0, j.deal, j.seat, j.arm))).take(max_games).collect();
    eprintln!("strength: {total} games in the plan, {} already done, {} to play now ({threads} threads); pilot {pilot} vs reference {reference}", done.len(), todo.len());
    if args.iter().any(|a| a == "--dry-run") {
        return;
    }
    // load every deck once (Deck is Clone; each worker clones its own)
    let deck_cache: Vec<Deck> = decks.iter().map(|(_, p)| load_deck(&root, p)).collect();
    let opp_cache: Vec<Deck> = opps.iter().map(|(_, p)| load_deck(&root, p)).collect();
    // a run stopped in the middle of a write can leave a last line without its newline: end it, so the next record starts on its own line
    if let Ok(s) = std::fs::read(&games_path) {
        if !s.is_empty() && *s.last().unwrap() != b'\n' {
            let mut f = std::fs::OpenOptions::new().append(true).open(&games_path).expect("games.jsonl");
            f.write_all(b"\n").unwrap();
        }
    }
    let file = std::fs::OpenOptions::new().create(true).append(true).open(&games_path).expect("games.jsonl");
    let errfile = std::fs::OpenOptions::new().create(true).append(true).open(out_dir.join("errors.jsonl")).expect("errors.jsonl");
    let sink = Arc::new(Mutex::new((file, errfile)));
    let next = Arc::new(AtomicUsize::new(0));
    let finished = Arc::new(AtomicUsize::new(0));
    let t_start = Instant::now();
    let todo = Arc::new(todo);
    let run_started = iso_now();
    {
        let mut f = std::fs::OpenOptions::new().create(true).append(true).open(out_dir.join("run_log.jsonl")).unwrap();
        writeln!(f, "{}", json!({"event": "start", "at": run_started, "threads": threads, "planned": total, "already_done": done.len(), "to_play": todo.len(), "pilot": pilot, "reference": reference})).unwrap();
    }
    std::thread::scope(|scope| {
        for _ in 0..threads {
            let (next, finished, sink, todo) = (next.clone(), finished.clone(), sink.clone(), todo.clone());
            let (decks, opps, deck_cache, opp_cache, reference, pilot, log_level) = (&decks, &opps, &deck_cache, &opp_cache, &reference, &pilot, &log_level);
            scope.spawn(move || loop {
                if stop_after.is_some_and(|d| t_start.elapsed() > d) {
                    break;
                }
                let i = next.fetch_add(1, Ordering::SeqCst);
                if i >= todo.len() {
                    break;
                }
                let j = &todo[i];
                let (dn, on) = (&decks[j.deck].0, &opps[j.opp].0);
                let key = key_of(dn, on, j.deal, j.seat, j.arm);
                let spec_deck: &str = if j.arm == "X" { pilot } else { reference };
                let spec_opp: &str = reference;
                let res = catch_unwind(AssertUnwindSafe(|| {
                    let dd = &deck_cache[j.deck];
                    let od = &opp_cache[j.opp];
                    let (d0, d1, s0, s1) = if j.seat == 0 { (dd, od, spec_deck, spec_opp) } else { (od, dd, spec_opp, spec_deck) };
                    let notes = [ext::new_meta(), ext::new_meta()];
                    let recs = [Arc::new(Mutex::new(SeatRec::default())), Arc::new(Mutex::new(SeatRec::default()))];
                    let t0 = Instant::now();
                    let started = iso_now();
                    // who goes first is fixed by the seed before any pilot acts: read it off a bare game of the same seed
                    let raw = build_players(d0, d1, "r", "r", j.seed, None, &notes);
                    let first_seat = Game::new(raw, j.seed).get_state_clone().current_player;
                    let players = build_players(d0, d1, s0, s1, j.seed, ext_timeout, &notes);
                    let wrapped: Vec<Box<dyn Player>> = players
                        .into_iter()
                        .enumerate()
                        .map(|(seat, p)| {
                            Box::new(Wrapped { inner: p, rec: recs[seat].clone(), keep_log: log_level != "none" && (seat == j.seat || log_level == "full"), first: seat == first_seat }) as Box<dyn Player>
                        })
                        .collect();
                    let mut game = Game::new(wrapped, j.seed);
                    let outcome = game.play();
                    let st = game.get_state_clone();
                    let wall = t0.elapsed().as_secs_f64();
                    let (ds, os) = (j.seat, 1 - j.seat);
                    let winner = match outcome {
                        Some(GameOutcome::Win(s)) if s == ds => "deck",
                        Some(GameOutcome::Win(_)) => "opp",
                        _ => "tie",
                    };
                    let agg = |s: usize| {
                        let r = recs[s].lock().unwrap();
                        let tot: f64 = r.times.iter().sum();
                        json!({"n": r.times.len(), "total_s": (tot / 1000.0 * 1000.0).round() / 1000.0, "ms": r.times})
                    };
                    let mut rec = json!({
                        "key": key, "deck": dn, "opp": on, "deal": j.deal, "seat": j.seat, "arm": j.arm, "seed": j.seed,
                        "pilot_deck": spec_deck, "pilot_opp": spec_opp,
                        "first": if first_seat == ds { "deck" } else { "opp" }, "winner": winner,
                        "points": [st.points[ds], st.points[os]], "turns": st.turn_count, "wall_s": (wall * 1000.0).round() / 1000.0,
                        "moves_deck": agg(ds), "moves_opp": agg(os), "started_at": started,
                    });
                    let lg = recs[ds].lock().unwrap().log.clone();
                    if log_level != "none" {
                        rec["log"] = Value::Array(lg);
                    }
                    if log_level == "full" {
                        rec["log_opp"] = Value::Array(recs[os].lock().unwrap().log.clone());
                    }
                    // what an external pilot reports besides its choices: notes (reasoning), cost, tokens (summed over the game, per seat)
                    for (who, s) in [("deck", ds), ("opp", os)] {
                        let m = notes[s].lock().unwrap().clone();
                        if !m.notes.is_empty() || m.cost_usd > 0.0 || m.tokens > 0 {
                            rec[format!("ext_{who}")] = json!({"notes": m.notes, "cost_usd": m.cost_usd, "tokens": m.tokens});
                        }
                    }
                    rec
                }));
                let mut g = sink.lock().unwrap();
                match res {
                    Ok(rec) => {
                        writeln!(g.0, "{}", rec).unwrap();
                        g.0.flush().unwrap();
                    }
                    Err(e) => {
                        let msg = e.downcast_ref::<String>().cloned().or_else(|| e.downcast_ref::<&str>().map(|s| s.to_string())).unwrap_or_default();
                        writeln!(g.1, "{}", json!({"key": key, "error": msg, "at": iso_now()})).unwrap();
                        g.1.flush().unwrap();
                    }
                }
                let n = finished.fetch_add(1, Ordering::SeqCst) + 1;
                if n % 20 == 0 || n == todo.len() {
                    eprintln!("strength: {n}/{} games, {:.0} s elapsed", todo.len(), t_start.elapsed().as_secs_f64());
                }
            });
        }
    });
    let mut f = std::fs::OpenOptions::new().create(true).append(true).open(out_dir.join("run_log.jsonl")).unwrap();
    writeln!(f, "{}", json!({"event": "stop", "at": iso_now(), "played": finished.load(Ordering::SeqCst), "elapsed_s": t_start.elapsed().as_secs_f64()})).unwrap();
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("run") => run(&args),
        Some("selfcheck") => selfcheck(&args),
        _ => {
            eprintln!("usage: strength run --manifest M --out DIR [...] | strength selfcheck --pilot km3 --deck-a A --deck-b B [--games N]");
            std::process::exit(2);
        }
    }
}
