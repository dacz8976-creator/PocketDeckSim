use clap::{ArgAction, Parser, Subcommand};
use colored::Colorize;
use deckgym::optimize::{ParallelConfig, SimulationConfig};
use deckgym::players::{parse_player_code, PlayerCode};
use deckgym::simulate::{initialize_logger, simulate_with_results};
use deckgym::{cli_optimize, Deck};
use log::warn;
use num_format::{Locale, ToFormattedString};
use std::fs;

mod cli_preflight;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Simulate games between two decks (or one deck against multiple decks in a folder)
    Simulate {
        /// Path to the first deck file
        deck_a: String,

        /// Path to the second deck file or folder containing multiple deck files
        deck_b_or_folder: String,

        /// Players' strategies as a comma-separated list (e.g., "e2,e4" or "r,e5")
        /// Available codes: aa, et, r, h, w, m, v, e<depth>, er
        /// Example: e2 = ExpectiMiniMax with depth 2
        #[arg(long, value_delimiter = ',', value_parser = parse_cli_player_code)]
        players: Option<Vec<PlayerCode>>,

        /// Shell command of the bot for the first seat when it is `proto` (bot protocol v1)
        #[arg(long)]
        bot_a: Option<String>,

        /// Shell command of the bot for the second seat when it is `proto`
        #[arg(long)]
        bot_b: Option<String>,

        /// Per-message timeout of a protocol bot, in milliseconds
        #[arg(long, default_value_t = 10000)]
        bot_timeout_ms: u64,

        /// Folder for the protocol bot decision logs
        #[arg(long)]
        bot_log: Option<String>,

        /// Number of simulations to run
        #[arg(short, long)]
        num: u32,

        /// Seed for random number generation
        #[arg(short, long)]
        seed: Option<u64>,

        /// s118. Use `seed + game_index` for each game instead of `seed` for all of them.
        /// Without this, `--seed` replays ONE game n times.
        #[arg(long, default_value_t = false)]
        seed_stream: bool,

        /// Run simulations in parallel
        #[arg(short, long, default_value_t = false)]
        parallel: bool,

        /// Number of threads to use (defaults to number of CPU cores if not specified)
        #[arg(short = 'j', long)]
        threads: Option<usize>,

        /// Increase verbosity (-v, -vv, -vvv, etc.)
        #[arg(short, long, action = ArgAction::Count, default_value_t = 1)]
        verbose: u8,

        /// Output folder for exporting (state, action) pairs in JSON format
        #[arg(long)]
        data_output: Option<String>,

        /// Output folder for compact per-game results, seeds and matchup identities
        #[arg(long)]
        results_output: Option<String>,
    },
    /// Optimize an incomplete deck against enemy decks
    Optimize {
        /// Path to the incomplete deck file (missing up to 4 cards)
        incomplete_deck: String,

        /// Comma-separated list of candidate card IDs for completion
        candidate_cards: String,

        /// Folder containing enemy deck files
        enemy_decks_folder: String,

        /// Number of simulations to run per enemy deck for each combination
        #[arg(short, long)]
        num: u32,

        /// Players' strategies as a comma-separated list (e.g., "e2,e4" or "r,e5")
        /// Available codes: aa, et, r, h, w, m, v, e<depth>, er
        /// Example: e2 = ExpectiMiniMax with depth 2
        #[arg(long, value_delimiter = ',', value_parser = parse_player_code)]
        players: Option<Vec<PlayerCode>>,

        /// Seed for random number generation
        #[arg(short, long)]
        seed: Option<u64>,

        /// Run simulations in parallel
        #[arg(short, long, default_value_t = false)]
        parallel: bool,

        /// Number of threads to use (defaults to number of CPU cores if not specified)
        #[arg(short = 'j', long)]
        threads: Option<usize>,

        /// Increase verbosity (-v, -vv, -vvv, etc.)
        #[arg(short, long, action = ArgAction::Count, default_value_t = 1)]
        verbose: u8,
    },
}

/// Simulate games between one deck and multiple decks in a folder
fn simulate_against_folder(
    deck_a_path: &str,
    decks_folder: &str,
    sim_config: SimulationConfig,
    parallel_config: ParallelConfig,
    results_output: Option<String>,
) {
    let total_num_simulations = sim_config.num_games;
    let players = sim_config.players;
    let seed = sim_config.seed;
    let seed_stream = sim_config.seed_stream;
    let data_output = sim_config.data_output;
    let parallel = parallel_config.enabled;
    let num_threads = parallel_config.num_threads;

    // Read all deck files from the folder
    let deck_paths: Vec<String> = fs::read_dir(decks_folder)
        .expect("Failed to read decks folder")
        .filter_map(|entry| {
            let entry = entry.ok()?;
            if entry.path().is_file() {
                Some(entry.path().to_str()?.to_string())
            } else {
                None
            }
        })
        .collect();

    // Load and validate decks
    let valid_decks: Vec<(String, Deck)> = deck_paths
        .iter()
        .filter_map(|path| {
            let deck = Deck::from_file(path).ok()?;
            if deck.cards.len() == 20 {
                Some((path.clone(), deck))
            } else {
                warn!("Skipping deck {} (invalid)", path);
                None
            }
        })
        .collect();

    if valid_decks.is_empty() {
        warn!("No valid decks found in folder: {}", decks_folder);
        return;
    }

    warn!(
        "Found {} valid deck files in folder",
        valid_decks.len().to_formatted_string(&Locale::en)
    );

    // Calculate games per deck (distribute evenly)
    let num_decks = valid_decks.len() as u32;
    let games_per_deck = total_num_simulations / num_decks;
    let remainder = total_num_simulations % num_decks;

    warn!(
        "Running {} total games ({} per deck)",
        total_num_simulations.to_formatted_string(&Locale::en),
        games_per_deck.to_formatted_string(&Locale::en)
    );

    // Run simulations against each deck
    for (i, (deck_path, _)) in valid_decks.iter().enumerate() {
        let deck_name = deck_path.split('/').next_back().unwrap_or(deck_path);
        let games_for_this_deck = if i < remainder as usize {
            games_per_deck + 1
        } else {
            games_per_deck
        };

        if games_for_this_deck == 0 {
            continue;
        }

        warn!("\n{}", "=".repeat(60));
        warn!(
            "Simulating against deck {}/{}: {}",
            i + 1,
            num_decks,
            deck_name
        );
        warn!("{}", "=".repeat(60));

        simulate_with_results(
            deck_a_path,
            deck_path,
            SimulationConfig {
                num_games: games_for_this_deck,
                players: players.clone(),
                seed,
                seed_stream,
                data_output: data_output.clone(),
            },
            ParallelConfig {
                enabled: parallel,
                num_threads,
            },
            results_output.clone(),
        ).unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(1);
        });
    }

    warn!("\n{}", "=".repeat(60));
    warn!("All simulations complete!");
    warn!("{}", "=".repeat(60));
}

/// Simulate's `--players` parser: `proto` is a placeholder filled from `--bot-a` / `--bot-b`.
fn parse_cli_player_code(s: &str) -> Result<PlayerCode, String> {
    if s.eq_ignore_ascii_case("proto") {
        return Ok(PlayerCode::Proto { command: String::new(), timeout_ms: 0, log: None });
    }
    parse_player_code(s)
}

fn main() {
    let cli = Cli::parse();
    eprintln!("PDL decision-integrity candidate {}: closed-list observations; unknown opponent continuations are UNPRICED. Historical seed results are not comparable.", env!("CARGO_PKG_VERSION"));

    // Branch depending on the chosen subcommand.
    match cli.command {
        Commands::Simulate {
            deck_a,
            deck_b_or_folder,
            players,
            bot_a,
            bot_b,
            bot_timeout_ms,
            bot_log,
            num,
            seed,
            seed_stream,
            parallel,
            threads,
            verbose,
            data_output,
            results_output,
        } => {
            let mut players = players;
            if bot_a.is_some() || bot_b.is_some() || players.as_ref().is_some_and(|p| p.iter().any(|c| matches!(c, PlayerCode::Proto { .. }))) {
                let mut seats = deckgym::players::fill_code_array(players);
                for (seat, bot) in [(0usize, &bot_a), (1usize, &bot_b)] {
                    let is_proto = matches!(seats[seat], PlayerCode::Proto { .. });
                    match (is_proto, bot) {
                        (true, Some(command)) => {
                            seats[seat] = PlayerCode::Proto { command: command.clone(), timeout_ms: bot_timeout_ms, log: bot_log.clone() };
                        }
                        (true, None) => {
                            eprintln!("player seat {seat} is `proto` but --bot-{} was not given", if seat == 0 { "a" } else { "b" });
                            std::process::exit(2);
                        }
                        (false, Some(_)) => {
                            eprintln!("--bot-{} was given but player seat {seat} is not `proto`", if seat == 0 { "a" } else { "b" });
                            std::process::exit(2);
                        }
                        (false, None) => {}
                    }
                }
                players = Some(seats);
            }
            initialize_logger(verbose);

            warn!("Welcome to {} simulation!", "deckgym".blue().bold());

            if let Err(error) = cli_preflight::simulation(&deck_a, &deck_b_or_folder) {
                eprintln!("{error}");
                std::process::exit(2);
            }

            // Check if deck_b_or_folder is a directory
            let path = std::path::Path::new(&deck_b_or_folder);
            if path.is_dir() {
                simulate_against_folder(
                    &deck_a,
                    &deck_b_or_folder,
                    SimulationConfig {
                        num_games: num,
                        players,
                        seed,
                        seed_stream,
                        data_output,
                    },
                    ParallelConfig {
                        enabled: parallel,
                        num_threads: threads,
                    },
                    results_output,
                );
            } else {
                simulate_with_results(
                    &deck_a,
                    &deck_b_or_folder,
                    SimulationConfig {
                        num_games: num,
                        players,
                        seed,
                        seed_stream,
                        data_output,
                    },
                    ParallelConfig {
                        enabled: parallel,
                        num_threads: threads,
                    },
                    results_output,
                ).unwrap_or_else(|error| {
                    eprintln!("{error}");
                    std::process::exit(1);
                });
            }
        }
        Commands::Optimize {
            incomplete_deck,
            candidate_cards,
            enemy_decks_folder,
            num,
            players,
            seed,
            parallel,
            threads,
            verbose,
        } => {
            initialize_logger(verbose);

            warn!("Welcome to {} optimizer!", "deckgym".blue().bold());

            if let Err(error) = cli_preflight::optimization(
                &incomplete_deck,
                &candidate_cards,
                &enemy_decks_folder,
            ) {
                eprintln!("{error}");
                std::process::exit(2);
            }

            let sim_config = SimulationConfig {
                num_games: num,
                players,
                seed,
                seed_stream: false,
                data_output: None,
            };
            let parallel_config = ParallelConfig {
                enabled: parallel,
                num_threads: threads,
            };

            cli_optimize(
                &incomplete_deck,
                &candidate_cards,
                &enemy_decks_folder,
                sim_config,
                parallel_config,
            );
        }
    }
}
