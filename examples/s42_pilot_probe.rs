//! §42 — why does `x3` pilot WORSE than `p3`/`e3`?
//!
//! Runs the same matchup under several tiers and prints, per pilot:
//!   * the histogram of actions it CHOSE (Attack*/EndTurn* are turn-ending),
//!   * leaf accounting — how many terminal evaluations had the opponent's reply priced,
//!   * and the decisive number: among decisions offering BOTH a boundary-crossing candidate
//!     and a turn-preserving one, how often the turn-preserving one won.
//!
//!   cargo run --release --example s42_pilot_probe -- <deckA> <deckB> --num 40 [--tiers p3,x3]

use deckgym::optimize::{ParallelConfig, SimulationConfig};
use deckgym::players::s42_probe::take_pilot_stats;
use deckgym::players::{parse_player_code, take_opponent_ply_stats};
use deckgym::simulate;

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter()
        .position(|a| a == flag)
        .and_then(|i| args.get(i + 1))
        .cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_a = args
        .get(1)
        .cloned()
        .unwrap_or_else(|| "example_decks/venusaur-exeggutor.txt".to_string());
    let deck_b = args.get(2).cloned().unwrap_or_else(|| deck_a.clone());
    let num: u32 = arg(&args, "--num")
        .and_then(|v| v.parse().ok())
        .unwrap_or(40);
    let tiers: Vec<String> = arg(&args, "--tiers")
        .unwrap_or_else(|| "e3,p3,x3".to_string())
        .split(',')
        .map(|s| s.trim().to_string())
        .collect();

    println!("# s42 pilot probe");
    println!("# deckA = {deck_a}");
    println!("# deckB = {deck_b}");
    println!("# games per cell = {num}\n");

    for spec in &tiers {
        // A spec is "codeA:codeB", or a single code used for both seats.
        let (ca, cb) = match spec.split_once(':') {
            Some((a, b)) => (a.to_string(), b.to_string()),
            None => (spec.clone(), spec.clone()),
        };
        let _ = take_pilot_stats();
        let _ = take_opponent_ply_stats();

        let pa = parse_player_code(&ca).expect("valid player code");
        let pb = parse_player_code(&cb).expect("valid player code");
        simulate::simulate(
            &deck_a,
            &deck_b,
            SimulationConfig {
                num_games: num,
                players: Some(vec![pa, pb]),
                seed: None,
                seed_stream: false,
                data_output: None,
            },
            // Serial: the probe's counters are global, and interleaving seats across threads
            // would still be correct but the per-actor split is easier to trust this way.
            ParallelConfig {
                enabled: false,
                num_threads: None,
            },
        );

        let (stats, leaves) = take_pilot_stats();
        let (ply_nodes, _) = take_opponent_ply_stats();

        println!("================ {spec}  (p0={ca}, p1={cb}) ================");
        println!(
            "leaves: own-turn(unpriced) {} | budget-spent(unpriced) {} | after-opp-ply(priced) {} | turn-passed-but-depth0 {} | ply nodes {}",
            leaves[0], leaves[1], leaves[2], leaves[3], ply_nodes
        );
        let total_leaves: usize = leaves[0] + leaves[1] + leaves[2];
        if total_leaves > 0 {
            println!(
                "        priced share of leaves: {:.2}%",
                100.0 * leaves[2] as f64 / total_leaves as f64
            );
        }

        for actor in [0usize, 1usize] {
            let decisions = *stats.decisions.get(&actor).unwrap_or(&0);
            if decisions == 0 {
                continue;
            }
            let code = if actor == 0 { &ca } else { &cb };
            println!("\n-- p{actor} ({code}): {decisions} root decisions");
            let empty = Default::default();
            let hist = stats.chosen.get(&actor).unwrap_or(&empty);
            let mut rows: Vec<_> = hist.iter().collect();
            rows.sort_by(|a, b| b.1.cmp(a.1));
            for (kind, n) in rows {
                println!(
                    "   {kind:<12} {n:>7}  ({:.2}% of decisions)",
                    100.0 * *n as f64 / decisions as f64
                );
            }
            let cand = *stats.candidates.get(&actor).unwrap_or(&0);
            let cand_priced = *stats.candidates_priced.get(&actor).unwrap_or(&0);
            let mixed = *stats.mixed_decisions.get(&actor).unwrap_or(&0);
            let unpriced_win = *stats.chose_unpriced_when_mixed.get(&actor).unwrap_or(&0);
            println!(
                "   candidates {cand} of which priced {cand_priced} ({:.2}%)",
                if cand > 0 {
                    100.0 * cand_priced as f64 / cand as f64
                } else {
                    0.0
                }
            );
            if mixed > 0 {
                let base =
                    100.0 * (cand - cand_priced) as f64 / if cand > 0 { cand as f64 } else { 1.0 };
                println!(
                    "   MIXED decisions {mixed}: chose UNPRICED {unpriced_win} ({:.2}%)  [unpriced share of all candidates: {:.2}%]",
                    100.0 * unpriced_win as f64 / mixed as f64,
                    base
                );
            } else {
                println!("   MIXED decisions 0  (no tier-level pricing asymmetry to observe)");
            }
        }
        println!();
    }
}
