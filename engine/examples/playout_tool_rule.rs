//! Gate 2 of the Tool-placement rule (Oct 6; rl/results/playout_tool_rule_2026-10-06/README.md): at each position, every
//! move kx3 would consider (its candidates, cap included) played out `--rounds` times from the same sampled worlds and
//! seeds as kx3's `evaluate`, with the rule off and on (`PlayoutPlayer::tool_rule_study`, LAB). Per move: both means, the
//! paired difference (on - off) with its 95% interval, and the rounds the rule acted in; per position: kx3's choice
//! both ways (its own rule: the best mean, km3's move kept unless the lead exceeds z standard errors).
//!   playout_tool_rule --positions <positions.json> --rounds 128 --out results.jsonl [--resume]
//! positions.json: [{"id", "state": <state file>, "deck": <the pilot's list>, "opponent": <the opponent's list>, "seed"}];
//! the pilot is the side to move. `--resume` skips positions already in `--out`.
use std::collections::BTreeSet;
use std::io::Write;

use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{Knowledge, PlayoutParams, PlayoutPlayer};
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};
use serde_json::{json, Value};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn stats(xs: &[f64]) -> (f64, f64) {
    let n = xs.len() as f64;
    let m = xs.iter().sum::<f64>() / n;
    let se = if xs.len() < 2 { f64::INFINITY } else { (xs.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt() };
    (m, se)
}

/// kx3's choice from per-round scores (candidate 0 is km3's move): the best mean (km3's first on a tie, then the order
/// offered) replaces km3's only if its paired lead exceeds z standard errors.
fn choice(scores: &[Vec<f64>], z: f64) -> usize {
    let means: Vec<f64> = scores.iter().map(|s| s.iter().sum::<f64>() / s.len() as f64).collect();
    let best = (0..means.len()).fold(0, |b, c| if means[c] > means[b] { c } else { b });
    if best == 0 {
        return 0;
    }
    let diffs: Vec<f64> = scores[best].iter().zip(&scores[0]).map(|(a, b)| a - b).collect();
    let (d, se) = stats(&diffs);
    if d > 0.0 && d > z * se { best } else { 0 }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--positions").unwrap()).unwrap()).unwrap();
    let rounds: usize = arg(&args, "--rounds").map_or(128, |r| r.parse().unwrap());
    let out_path = arg(&args, "--out").unwrap();
    let done: BTreeSet<String> = if args.iter().any(|a| a == "--resume") {
        std::fs::read_to_string(&out_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|v| v["id"].as_str().map(String::from))
            .collect()
    } else {
        BTreeSet::new()
    };
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(&out_path).unwrap();
    for p in &positions {
        let id = p["id"].as_str().unwrap().to_string();
        if done.contains(&id) {
            continue;
        }
        let state: State = serde_json::from_str(&std::fs::read_to_string(p["state"].as_str().unwrap()).unwrap()).unwrap();
        let deck = Deck::from_file(p["deck"].as_str().unwrap()).unwrap();
        let opponent = Deck::from_file(p["opponent"].as_str().unwrap()).unwrap();
        let seed = p["seed"].as_u64().unwrap();
        let (me, actions) = state.generate_possible_actions();
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let params = PlayoutParams { rollouts: 1, cap: 12, z: 2.0, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
        let mut pilot = PlayoutPlayer::with_extra_lists(deck, opponent, params, Vec::new());
        // kx3's candidates (km3's move first, the cap's drops named): they don't depend on the number of play-outs.
        let candidates = pilot.evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let moves: Vec<_> = candidates.candidates.iter().map(|c| c.action.clone()).collect();
        let study = pilot.tool_rule_study(&mut StdRng::seed_from_u64(seed), &observation, &moves, rounds);
        let off: Vec<Vec<f64>> = study.moves.iter().map(|m| m.off.iter().map(|o| o.score).collect()).collect();
        let on: Vec<Vec<f64>> = study.moves.iter().map(|m| m.on.iter().map(|o| o.score).collect()).collect();
        let (c_off, c_on) = (choice(&off, 2.0), choice(&on, 2.0));
        let rows: Vec<Value> = study
            .moves
            .iter()
            .enumerate()
            .map(|(i, m)| {
                let d: Vec<f64> = on[i].iter().zip(&off[i]).map(|(a, b)| a - b).collect();
                let (dm, dse) = stats(&d);
                json!({"move": m.label, "off": stats(&off[i]).0, "on": stats(&on[i]).0, "on_minus_off": dm, "lo": dm - 1.96 * dse, "hi": dm + 1.96 * dse,
                       "rounds_acted": m.interventions.iter().filter(|&&n| n > 0).count(), "interventions": m.interventions.iter().sum::<usize>(),
                       "rounds_detail": {"off": m.off.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>(),
                                         "on": m.on.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>()}})
            })
            .collect();
        let line = json!({"id": id, "seed": seed, "rounds": study.rounds, "failed_rounds": study.failed_rounds, "knowledge": study.knowledge,
                          "lists": study.lists, "ms": study.millis.round(), "dropped": candidates.dropped.iter().map(|d| d.label.clone()).collect::<Vec<_>>(),
                          "kx3_choice_off": study.moves[c_off].label, "kx3_choice_on": study.moves[c_on].label, "moves": rows});
        writeln!(out, "{line}").unwrap();
        out.flush().unwrap();
        let acted: usize = study.moves.iter().map(|m| m.interventions.iter().filter(|&&n| n > 0).count()).sum();
        let worst = rows.iter().map(|r| r["on_minus_off"].as_f64().unwrap()).fold(f64::INFINITY, f64::min);
        let best = rows.iter().map(|r| r["on_minus_off"].as_f64().unwrap()).fold(f64::NEG_INFINITY, f64::max);
        println!(
            "{id}: {} moves x {} rounds; the rule acted in {acted} play-outs; on - off per move from {worst:+.3} to {best:+.3}; kx3's choice {} -> {}",
            rows.len(), study.rounds, if c_off == c_on { "unchanged" } else { "changed" }, study.moves[c_on].label.chars().take(60).collect::<String>()
        );
    }
}
