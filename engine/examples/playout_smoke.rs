//! The play-out chooser's smoke check (branch claude/playout-pilot, Oct 2): the pilot (`--code`, default `kx3`) against km3
//! on two scratch decks, `--deals` deals, each played twice with the pilot in each seat, and the same deals played km3 v km3
//! (the pairing). Per game: the seed, the pilot's seat, the result of both arms, the pilot's decisions, how many it
//! changed from km3's move, the milliseconds per decision and the seconds per game. One JSON line per game to `--out`, and
//! a summary on stdout. Games run one at a time; the pilot's play-outs use rayon's threads (RAYON_NUM_THREADS).
//!   playout_smoke --a <deck> --b <deck> --deals 20 --seed-base <n> [--code kx3] [--out games.jsonl] [--trace-out trace.jsonl]
//!     [--seats 0,1] [--resume]
//! `--resume` skips the games already in `--out` (by seed and seat) and appends to both files: every game is seeded and the
//! pilot is deterministic, so a stopped run resumed gives the games an unbroken run would. The summary line then covers the
//! games this invocation played; `rl/results/playout_pilot_2026-10-02/smoke/summarize.py` reads the whole files.
use std::io::Write;
use std::sync::{Arc, Mutex};
use std::time::Instant;

use deckgym::actions::Action;
use deckgym::observation::PlayerObservation;
use deckgym::players::playout_player::PlayoutPlayer;
use deckgym::players::{create_players, parse_player_code, Player, PlayerCode};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;

#[derive(Default, Clone)]
struct Log {
    decisions: usize,
    changed: usize,
    millis: Vec<f64>,
    traces: Vec<String>,
}

/// The pilot, with each decision's report kept for the summary.
struct Recording {
    inner: PlayoutPlayer,
    log: Arc<Mutex<Log>>,
    keep_trace: bool,
}

impl std::fmt::Debug for Recording {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.inner.fmt(f)
    }
}

impl Player for Recording {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        let report = self.inner.evaluate(rng, observation, actions);
        if std::env::var_os("SMOKE_PROGRESS").is_some() {
            eprintln!("decision turn {} seat {}: {} candidates, {} rounds, {:.0} ms, changed {}",
                report.turn, report.actor, report.candidates.len(), report.rounds, report.millis, report.chosen != report.km3);
        }
        let mut log = self.log.lock().unwrap();
        log.decisions += 1;
        log.changed += (report.chosen != report.km3) as usize;
        log.millis.push(report.millis);
        if self.keep_trace && report.rounds > 0 {
            log.traces.push(
                serde_json::json!({
                    "turn": report.turn, "seat": report.actor, "rounds": report.rounds, "ms": report.millis.round(),
                    "km_move": report.candidates[report.km3].label, "chosen": report.candidates[report.chosen].label,
                    "reason": report.reason, "lists": report.lists, "failed_rounds": report.failed_rounds,
                    "candidates": report.candidates.iter().map(|c| serde_json::json!({
                        "move": c.label, "score": c.score, "diff": c.diff, "se": if c.se.is_finite() { c.se } else { -1.0 }
                    })).collect::<Vec<_>>(),
                    "dropped": report.dropped.iter().map(|d| d.label.clone()).collect::<Vec<_>>(),
                })
                .to_string(),
            );
        }
        report.candidates[report.chosen].action.clone()
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, actions: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, state, actions)
    }
    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn score(state: &State, seat: usize) -> f64 {
    match state.winner {
        Some(GameOutcome::Win(w)) if w == seat => 1.0,
        Some(GameOutcome::Win(_)) => 0.0,
        _ => 0.5,
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let deals: u64 = arg(&args, "--deals").map_or(20, |s| s.parse().unwrap());
    let base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let code_text = arg(&args, "--code").unwrap_or_else(|| "kx3".into());
    let PlayerCode::KX { params } = parse_player_code(&code_text).expect("a kx code") else { panic!("--code must be a kx code") };
    let resume = args.iter().any(|a| a == "--resume");
    let open = |p: String| {
        if resume {
            std::fs::OpenOptions::new().create(true).append(true).open(p).unwrap()
        } else {
            std::fs::File::create(p).unwrap()
        }
    };
    // The games already played (by seed and seat), when resuming.
    let done: std::collections::BTreeSet<(u64, usize)> = match (resume, arg(&args, "--out")) {
        (true, Some(p)) => std::fs::read_to_string(&p)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
            .map(|v| (v["seed"].as_u64().unwrap(), v["pilot_seat"].as_u64().unwrap() as usize))
            .collect(),
        _ => Default::default(),
    };
    let mut out = arg(&args, "--out").map(open);
    let mut trace_out = arg(&args, "--trace-out").map(open);
    let km3 = || parse_player_code("km3").unwrap();
    let seats: Vec<usize> = arg(&args, "--seats").map_or(vec![0, 1], |s| s.split(',').map(|x| x.parse().unwrap()).collect());
    println!("code {} ({}), {} deals x 2 seats, deck A (the pilot's) v deck B, rayon threads {}{}",
        params.code(), PlayoutPlayer::new(deck_a.clone(), deck_b.clone(), params.clone()).knowledge_label(), deals,
        rayon::current_num_threads(), if resume { format!("; resuming: {} games already played", done.len()) } else { String::new() });
    let (mut paired, mut game_secs, mut all_ms, mut changed, mut decisions) = (Vec::new(), Vec::new(), Vec::new(), 0usize, 0usize);
    let (mut pilot_total, mut ref_total) = (0.0f64, 0.0f64);
    for i in 0..deals {
        let seed = base + i;
        for seat in seats.iter().copied() {
            if done.contains(&(seed, seat)) {
                continue;
            }
            // The pilot's arm: deck A with the pilot in `seat`, deck B with km3.
            let log = Arc::new(Mutex::new(Log::default()));
            let pilot = Recording {
                inner: PlayoutPlayer::new(deck_a.clone(), deck_b.clone(), params.clone()),
                log: log.clone(),
                keep_trace: trace_out.is_some(),
            };
            let other = create_players(deck_b.clone(), deck_a.clone(), vec![km3(), km3()]).remove(0);
            let players: Vec<Box<dyn Player>> =
                if seat == 0 { vec![Box::new(pilot), other] } else { vec![other, Box::new(pilot)] };
            let t = Instant::now();
            let mut game = Game::new(players, seed);
            game.play();
            let secs = t.elapsed().as_secs_f64();
            let pilot_score = score(&game.get_state_clone(), seat);
            // The reference arm: the same deal, km3 on both sides.
            let (d0, d1) = if seat == 0 { (deck_a.clone(), deck_b.clone()) } else { (deck_b.clone(), deck_a.clone()) };
            let mut reference = Game::new(create_players(d0, d1, vec![km3(), km3()]), seed);
            reference.play();
            let ref_score = score(&reference.get_state_clone(), seat);
            let log = log.lock().unwrap().clone();
            let ms_mean = log.millis.iter().sum::<f64>() / log.millis.len().max(1) as f64;
            let line = serde_json::json!({
                "seed": seed, "pilot_seat": seat, "pilot_score": pilot_score, "km3_score": ref_score,
                "turns": game.get_state_clone().turn_count, "decisions": log.decisions, "changed": log.changed,
                "ms_per_decision": ms_mean.round(), "ms_max": log.millis.iter().cloned().fold(0.0, f64::max).round(),
                "seconds": (secs * 10.0).round() / 10.0,
            });
            println!("{line}");
            if let Some(f) = out.as_mut() {
                writeln!(f, "{line}").unwrap();
            }
            if let Some(f) = trace_out.as_mut() {
                for t in &log.traces {
                    writeln!(f, "{{\"seed\":{seed},\"pilot_seat\":{seat},\"decision\":{t}}}").unwrap();
                }
            }
            paired.push(pilot_score - ref_score);
            pilot_total += pilot_score;
            ref_total += ref_score;
            game_secs.push(secs);
            all_ms.extend(log.millis.iter().cloned());
            changed += log.changed;
            decisions += log.decisions;
        }
    }
    let n = paired.len() as f64;
    let mean = paired.iter().sum::<f64>() / n;
    let sd = (paired.iter().map(|d| (d - mean).powi(2)).sum::<f64>() / (n - 1.0).max(1.0)).sqrt();
    all_ms.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let pct = |p: f64| all_ms.get(((all_ms.len() as f64 - 1.0) * p).round() as usize).cloned().unwrap_or(0.0);
    println!(
        "summary: {} games (played by this invocation); pilot score {:.3}, km3 v km3 on the same deals {:.3}; paired difference {:+.3} ± {:.3} (95%); \
         decisions {decisions}, changed from km3's move {changed}; ms per decision mean {:.0}, median {:.0}, p95 {:.0}, max {:.0}; \
         seconds per game mean {:.1}, max {:.1}",
        paired.len(),
        pilot_total / n,
        ref_total / n,
        mean,
        1.96 * sd / n.sqrt(),
        all_ms.iter().sum::<f64>() / all_ms.len().max(1) as f64,
        pct(0.5),
        pct(0.95),
        pct(1.0),
        game_secs.iter().sum::<f64>() / n,
        game_secs.iter().cloned().fold(0.0, f64::max),
    );
}
