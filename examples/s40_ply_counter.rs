//! §40 — prove the opponent-turn ply actually FIRES before reading anything into its results.
//!
//! The lab has been burned three times by concluding a mechanism from an absence that turned
//! out to be a dead harness (§29-R seat order, §36 energy-cost law, §37-R Item lock via an
//! accented string). The rule that came out of it: before interpreting a zero, prove a
//! known-nonzero case. This binary is that proof for `x<N>`.
//!
//! It runs the same games at `e3` (ply disabled) and `x3` (ply enabled) and reports how many
//! times the search crossed the turn boundary. `e3` MUST report zero and `x3` MUST report a
//! large number; anything else means the null result is about the code, not the game.
//!
//!   cargo run --release --example s40_ply_counter -- <deck> --num 20

use deckgym::optimize::{ParallelConfig, SimulationConfig};
use deckgym::players::{parse_player_code, take_opponent_ply_stats};
use deckgym::simulate;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck = args
        .get(1)
        .cloned()
        .unwrap_or_else(|| "example_decks/venusaur-exeggutor.txt".to_string());
    let num: u32 = args
        .iter()
        .position(|a| a == "--num")
        .and_then(|i| args.get(i + 1))
        .and_then(|v| v.parse().ok())
        .unwrap_or(20);

    println!("deck: {deck}   games per tier: {num}\n");
    println!(
        "{:<6} {:>14} {:>16} {:>14}",
        "tier", "ply nodes", "ply branches", "branches/node"
    );
    println!("{}", "-".repeat(54));

    for tier in ["e3", "p3", "x3o1", "x3", "x3o5"] {
        // Reset the counters so each tier is measured in isolation.
        let _ = take_opponent_ply_stats();

        let code = parse_player_code(tier).expect("valid player code");
        simulate::simulate(
            &deck,
            &deck,
            SimulationConfig {
                num_games: num,
                players: Some(vec![code.clone(), code]),
                seed: None,
                data_output: None,
            },
            ParallelConfig {
                enabled: false,
                num_threads: None,
            },
        );

        let (nodes, branches) = take_opponent_ply_stats();
        let ratio = if nodes == 0 {
            0.0
        } else {
            branches as f64 / nodes as f64
        };
        println!("{tier:<6} {nodes:>14} {branches:>16} {ratio:>14.2}");
    }

    println!(
        "\nEXPECTED: e3 and p3 report exactly 0 (the ply is disabled).\n\
         x3* must report a large nonzero count, rising with the ply size.\n\
         If x3 reports 0, every §40 conclusion about the opponent ply is void."
    );
}
