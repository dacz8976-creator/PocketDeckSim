//! Tool / turn-effect census (the laptop's request, Sept 25): on the Limitless table's own deals, how often each Tool,
//! Field Blower and each temporary damage-reduction effect is offered and played by the pilot, and where the Tools
//! go. It only watches: the games are the table's games (the move fingerprints must equal the pilot's table file).
//! Built as an example in a scratch copy of engine/ (the repo's engine is untouched):
//!
//!   cp tool_census.rs <scratch engine>/examples/ && cargo run --release --example tool_census -- \
//!       --decks ../decks/research --games 100 --bot kp3 --games-out census_games.jsonl
//!
//! Seeds: the table's deals only, 72,000,000 + pairing x 10,000 + i, even i = the first-named deck in seat 0.
//! Per deck and card:
//! - offered: the owner's turns on which playing the card (or using the attack) was among the legal moves;
//! - played: the turns on which it was played (used);
//! - for a Tool, where it was attached (Active or Bench) and the holder's name;
//! - for Field Blower, what it discarded (own or opponent's Tool, on the Active or the Bench, or the Stadium).
//!
//! Extended Sept 29 for km (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, step 3 and section 4.1,
//! identity 8a: Cloud Opus's counter-tool extension). With none of the options below it runs exactly as before: the
//! same games, the same stdout and the same `--games-out` rows. The options:
//! - `--cells km17`: km's 17 named cells. Table pairings 0-6, 8, 13 and 18-21 (legality_scan's numbers) on the table's
//!   base with `--decks`, and `new_decks.tsv` pairings 8, 9, 16 and 17 (Rayquaza and Altaria/Greninja against Lucario
//!   and Altaria) on 21,108,000,000 with that file's lists and seats. Each cell's deck names are checked against the
//!   registration's list.
//! - `--pairs <tsv> [--root <dir>]`: the cells of a pairings file, as legality_scan reads one (held_file is the
//!   first-named deck, panel_file the second), with `--seed-base`.
//! - `--seed-base <n>` (72,000,000 for the table by default), `--pairings <list>` (a subset of the cells, in their
//!   own order; `8` keeps every cell numbered 8, `table:8` or `new_decks.tsv:8` one source's), `--first-deal <n>`
//!   (deals n to n + games - 1; 0 by default).
//! - `--rows-out <path>`: one row per game: the source ("table" or the pairings file), the pairing, the cell's decks a
//!   and b (first-named first) and their files, i, the seed, first_seat, each seat's deck and bot, the move
//!   fingerprint (the same hash as legality_scan's `moves`), and per seat and per watched card the turns offered and
//!   played, Field Blower's and the Tools' targets, and each X Speed play (turn, whether Hiking Trail was in play,
//!   whether the seat retreated later that turn). `--no-counts` leaves out every count and prints no table: for identity checks on gating deals,
//!   whose counts are not read.
//! - `--trace-out <path>`: every decision of every game: source, pairing, i, seat, turn, every Trainer among the legal
//!   moves (by name, whether watched or not), and the chosen move. For checking the counts by hand. Not with
//!   `--no-counts` (a trace carries the counts).
//! - Refused, as legality_scan refuses its like: `--seed-base` with `--cells km17` (its bases are the registration's),
//!   `--decks` with `--pairs`, `--root` in table mode, `--cells` with `--pairs`, deals past a pairing's 10,000-seed
//!   block, and a pairings file with a pairing listed twice or a short row.
//! The rows watch the original cards (Tools, Field Blower, Stiffen) and also every Stadium, X Speed, Team Rocket's
//! Boss and Copycat. The stdout table keeps the original set.
use deckgym::actions::SimpleAction;
use deckgym::models::{Card, TrainerType};
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};
use rayon::prelude::*;
use std::collections::hash_map::DefaultHasher;
use std::collections::{BTreeMap, BTreeSet};
use std::hash::{Hash, Hasher};

const NAMES: [&str; 8] = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"];
const SEED_BASE: u64 = 72_000_000;
/// Attacks that put a temporary damage reduction on the attacker itself for the opponent's next turn (defender side),
/// found in the eight lists by their text ("During your opponent's next turn, this Pokemon takes -X damage").
const REDUCTION_ATTACKS: [&str; 1] = ["Stiffen"];
/// km's step 3: the Trainers the rows count besides the original ones and every Stadium.
const ROW_TRAINERS: [&str; 3] = ["X Speed", "Team Rocket's Boss", "Copycat"];
/// km's 17 named cells (registration, step 3, "The 17 named cells"): (pairing, first-named deck, second deck).
const KM17_TABLE: [(usize, &str, &str); 13] = [
    (0, "altaria", "blaziken"),
    (1, "altaria", "hydreigon"),
    (2, "altaria", "lucario"),
    (3, "altaria", "sceptile"),
    (4, "altaria", "suicune"),
    (5, "altaria", "vespiquen"),
    (6, "altaria", "weezing"),
    (8, "blaziken", "lucario"),
    (13, "hydreigon", "lucario"),
    (18, "lucario", "sceptile"),
    (19, "lucario", "suicune"),
    (20, "lucario", "vespiquen"),
    (21, "lucario", "weezing"),
];
const KM17_NEW: [(usize, &str, &str); 4] =
    [(8, "rayquaza", "lucario"), (9, "rayquaza", "altaria"), (16, "altaria_greninja", "lucario"), (17, "altaria_greninja", "altaria")];
const NEW_DECKS_TSV: &str = "rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv";
const NEW_DECKS_BASE: u64 = 21_108_000_000;

#[derive(Default, Clone)]
struct Tally {
    offered: u64,
    played: u64,
    detail: BTreeMap<String, u64>,
}

/// One cell: where its pairing number comes from, the number, its seed base, and its two decks (names, files and
/// lists), first-named first.
#[derive(Clone)]
struct Cell {
    source: String,
    pairing: usize,
    seed_base: u64,
    decks: [Deck; 2],
    names: [String; 2],
    files: [String; 2],
}

/// An X Speed play: seat, turn, whether Hiking Trail was in play, whether the seat retreated later that turn.
#[derive(Clone)]
struct XSpeedTurn {
    seat: usize,
    turn: u8,
    hiking_trail: bool,
    retreated: bool,
}

#[derive(Default)]
struct GameCensus {
    // (deck, card) -> tally
    t: BTreeMap<(String, String), Tally>,
    fingerprint: u64,
    seed: u64,
    // The rows' counts, per seat: card -> (turns offered, turns played, targets).
    seats: [BTreeMap<String, Tally>; 2],
    first_seat: usize,
    deck_of: [String; 2],
    xspeed: Vec<XSpeedTurn>,
    trace: Vec<String>,
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// The card a move plays: a Trainer's name, or a listed reduction attack's title.
fn card_of(action: &SimpleAction) -> Option<String> {
    match action {
        SimpleAction::Play { trainer_card } => Some(trainer_card.name.clone()),
        SimpleAction::Attack(attack) if REDUCTION_ATTACKS.contains(&attack.title.as_str()) => {
            Some(format!("attack {}", attack.title))
        }
        _ => None,
    }
}

fn watched(action: &SimpleAction) -> bool {
    match action {
        SimpleAction::Play { trainer_card } => {
            trainer_card.trainer_card_type == TrainerType::Tool || trainer_card.name == "Field Blower"
        }
        SimpleAction::Attack(attack) => REDUCTION_ATTACKS.contains(&attack.title.as_str()),
        _ => false,
    }
}

/// The rows' watched moves: the original ones, and every Stadium, X Speed, Team Rocket's Boss and Copycat.
fn row_watched(action: &SimpleAction) -> bool {
    watched(action)
        || matches!(action, SimpleAction::Play { trainer_card }
            if trainer_card.trainer_card_type == TrainerType::Stadium || ROW_TRAINERS.contains(&trainer_card.name.as_str()))
}

fn play_one(cell: &Cell, i: u64, bot: &str, trace: bool) -> GameCensus {
    let seed = cell.seed_base + cell.pairing as u64 * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (0, 1) } else { (1, 0) };
    let deck_of = [cell.names[d0].clone(), cell.names[d1].clone()];
    let codes = vec![parse_player_code(bot).unwrap(), parse_player_code(bot).unwrap()];
    let players = create_players(cell.decks[d0].clone(), cell.decks[d1].clone(), codes);
    let mut game = Game::new(players, seed);
    let mut moves = DefaultHasher::new();
    let mut census = GameCensus { seed, first_seat, deck_of: deck_of.clone(), ..Default::default() };
    // (seat, turn) -> cards offered / played that turn
    let mut offered: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut played: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut row_offered: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut row_played: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut pending: Option<(usize, String)> = None; // a Tool or Field Blower whose target choice comes next
    while !game.is_game_over() {
        let before = game.get_state_clone();
        let (actor, actions) = before.generate_possible_actions();
        for a in actions.iter().filter(|a| watched(&a.action)) {
            offered.insert((actor, before.turn_count, card_of(&a.action).unwrap()));
        }
        let row_names: BTreeSet<String> =
            actions.iter().filter(|a| row_watched(&a.action)).map(|a| card_of(&a.action).unwrap()).collect();
        for name in &row_names {
            row_offered.insert((actor, before.turn_count, name.clone()));
        }
        let chosen = game.play_tick();
        format!("{:?}", chosen).hash(&mut moves);
        if trace {
            // Every Trainer the owner could play, by name, watched or not.
            let playable: BTreeSet<&str> = actions
                .iter()
                .filter_map(|a| match &a.action {
                    SimpleAction::Play { trainer_card } => Some(trainer_card.name.as_str()),
                    _ => None,
                })
                .collect();
            let names: Vec<&str> = playable.iter().copied().collect();
            census.trace.push(format!(
                "{}\t{}\t{}\t{actor}\t{}\t{}\t{:?}",
                cell.source,
                cell.pairing,
                i,
                before.turn_count,
                names.join("|"),
                chosen.action
            ));
        }
        // The rows: the card played, the X Speed turns and whether the seat then retreated.
        if row_watched(&chosen.action) {
            let card = card_of(&chosen.action).unwrap();
            if card == "X Speed" {
                let hiking_trail = matches!(&before.active_stadium, Some(Card::Trainer(t)) if t.name == "Hiking Trail");
                census.xspeed.push(XSpeedTurn { seat: chosen.actor, turn: before.turn_count, hiking_trail, retreated: false });
            }
            row_played.insert((chosen.actor, before.turn_count, card));
        }
        if matches!(chosen.action, SimpleAction::Retreat(_)) {
            for x in census.xspeed.iter_mut().filter(|x| x.seat == chosen.actor && x.turn == before.turn_count) {
                x.retreated = true;
            }
        }
        if watched(&chosen.action) {
            let card = card_of(&chosen.action).unwrap();
            played.insert((chosen.actor, before.turn_count, card.clone()));
            if matches!(&chosen.action, SimpleAction::Play { .. }) {
                pending = Some((chosen.actor, card));
            }
            continue;
        }
        if let Some((seat, card)) = pending.take() {
            let where_ = match &chosen.action {
                SimpleAction::AttachTool { in_play_idx, .. } => {
                    let holder = before.in_play_pokemon[seat][*in_play_idx].as_ref().map(|p| p.get_name()).unwrap_or_default();
                    Some(format!("{} {holder}", if *in_play_idx == 0 { "Active" } else { "Bench" }))
                }
                SimpleAction::DiscardToolFromPokemon { player, in_play_idx, tool_idx } => {
                    let pokemon = before.in_play_pokemon[*player][*in_play_idx].as_ref();
                    let tool = pokemon.and_then(|p| p.attached_tools.get(*tool_idx)).map(|t| match t {
                        Card::Trainer(t) => t.name.clone(),
                        other => format!("{other:?}"),
                    });
                    Some(format!(
                        "{} Tool on {} ({})",
                        if *player == seat { "own" } else { "opponent's" },
                        if *in_play_idx == 0 { "Active" } else { "Bench" },
                        tool.unwrap_or_default()
                    ))
                }
                SimpleAction::DiscardActiveStadium => Some("Stadium".to_string()),
                _ => None,
            };
            if let Some(w) = where_ {
                *census.seats[seat].entry(card.clone()).or_default().detail.entry(w.clone()).or_default() += 1;
                let e = census.t.entry((deck_of[seat].clone(), card)).or_default();
                *e.detail.entry(w).or_default() += 1;
            } else {
                pending = None;
            }
        }
    }
    for (seat, _turn, card) in &offered {
        census.t.entry((deck_of[*seat].clone(), card.clone())).or_default().offered += 1;
    }
    for (seat, _turn, card) in &played {
        census.t.entry((deck_of[*seat].clone(), card.clone())).or_default().played += 1;
    }
    for (seat, _turn, card) in &row_offered {
        census.seats[*seat].entry(card.clone()).or_default().offered += 1;
    }
    for (seat, _turn, card) in &row_played {
        census.seats[*seat].entry(card.clone()).or_default().played += 1;
    }
    census.fingerprint = moves.finish();
    census
}

/// A pairings file's cells, as legality_scan's `read_pairs` reads them: held_file first-named, panel_file second,
/// deck paths relative to `root`, each row's seed_first checked against the base.
fn read_pairs(path: &str, root: &str, seed_base: u64) -> Vec<Cell> {
    let text = std::fs::read_to_string(path).unwrap_or_else(|e| panic!("pairs file {path}: {e}"));
    let mut lines = text.trim_start_matches('\u{feff}').lines().filter(|l| !l.trim().is_empty());
    let header: Vec<&str> = lines.next().expect("pairs file header").split('\t').map(str::trim).collect();
    let col = |name: &str| header.iter().position(|h| *h == name).unwrap_or_else(|| panic!("{path} has no {name} column"));
    let (c_pairing, c_held_key, c_held_file) = (col("pairing"), col("held_key"), col("held_file"));
    let (c_opponent, c_panel_file) = (col("opponent"), col("panel_file"));
    let c_seed_first = header.iter().position(|h| *h == "seed_first");
    let mut listed = BTreeSet::new();
    let load = |file: &str| {
        let full = std::path::Path::new(root).join(file);
        Deck::from_file(full.to_str().unwrap()).unwrap_or_else(|e| panic!("deck file {}: {e}", full.display()))
    };
    lines
        .map(|line| {
            let f: Vec<&str> = line.split('\t').map(str::trim).collect();
            assert!(f.len() >= header.len(), "pairs file {path}: short row {line:?}");
            let pairing: usize = f[c_pairing].parse().unwrap();
            assert!(listed.insert(pairing), "pairs file {path}: pairing {pairing} listed twice");
            if let Some(c) = c_seed_first {
                assert_eq!(f[c].parse::<u64>().ok(), Some(seed_base + pairing as u64 * 10_000), "pairing {pairing}: seed_first");
            }
            Cell {
                source: path.rsplit('/').next().unwrap().to_string(),
                pairing,
                seed_base,
                decks: [load(f[c_held_file]), load(f[c_panel_file])],
                names: [f[c_held_key].to_string(), f[c_opponent].to_string()],
                files: [f[c_held_file].to_string(), f[c_panel_file].to_string()],
            }
        })
        .collect()
}

/// The table's 28 cells in legality_scan's order, on `seed_base`.
fn table_cells(dir: &str, seed_base: u64) -> Vec<Cell> {
    let decks: [Deck; 8] = NAMES.map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file"));
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
    pairs
        .iter()
        .enumerate()
        .map(|(pairing, &(a, b))| Cell {
            source: "table".to_string(),
            pairing,
            seed_base,
            decks: [decks[a].clone(), decks[b].clone()],
            names: [NAMES[a].to_string(), NAMES[b].to_string()],
            files: [format!("{dir}/{}.txt", NAMES[a]), format!("{dir}/{}.txt", NAMES[b])],
        })
        .collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(100);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kp3".into());
    assert!(!bot.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    let first_deal: u64 = arg(&args, "--first-deal").map(|x| x.parse().unwrap()).unwrap_or(0);
    let only: Option<Vec<String>> = arg(&args, "--pairings").map(|x| x.split(',').map(|p| p.trim().to_string()).collect());
    let no_counts = args.iter().any(|a| a == "--no-counts");
    let has = |o: &str| args.iter().any(|a| a == o);
    assert!(first_deal + games <= 10_000, "deals {first_deal}..{} run past a pairing's 10,000 seeds", first_deal + games);
    assert!(!(no_counts && has("--trace-out")), "--trace-out carries the counts; not with --no-counts");
    assert!(!(has("--cells") && has("--pairs")), "--cells and --pairs are exclusive");
    assert!(!(has("--cells") && has("--seed-base")), "--cells km17 sets each cell's seed base; --seed-base is refused");
    assert!(!(has("--pairs") && has("--decks")), "--pairs names its own deck files; --decks is for the table");
    assert!(has("--cells") || has("--pairs") || !has("--root"), "--root is only for --pairs and --cells");
    let extended = ["--cells", "--pairs", "--seed-base", "--pairings", "--first-deal", "--rows-out", "--trace-out"]
        .iter()
        .any(|o| args.iter().any(|a| a == o))
        || no_counts;
    let cells: Vec<Cell> = match (arg(&args, "--cells").as_deref(), arg(&args, "--pairs")) {
        (Some("km17"), None) => {
            let root = arg(&args, "--root").unwrap_or_else(|| "..".into());
            let table = table_cells(&dir, SEED_BASE);
            let new = read_pairs(&format!("{root}/{NEW_DECKS_TSV}"), &root, NEW_DECKS_BASE);
            let mut cells = Vec::new();
            for (p, a, b) in KM17_TABLE {
                let c = table[p].clone();
                assert_eq!((c.names[0].as_str(), c.names[1].as_str()), (a, b), "table pairing {p}");
                cells.push(c);
            }
            for (p, a, b) in KM17_NEW {
                let c = new.iter().find(|c| c.pairing == p).unwrap_or_else(|| panic!("new_decks pairing {p}")).clone();
                assert_eq!((c.names[0].as_str(), c.names[1].as_str()), (a, b), "new_decks pairing {p}");
                cells.push(c);
            }
            cells
        }
        (Some(other), _) => panic!("unknown --cells {other} (the one named set is km17)"),
        (None, Some(path)) => {
            let root = arg(&args, "--root").unwrap_or_else(|| "..".into());
            let base: u64 = arg(&args, "--seed-base").expect("--pairs needs --seed-base").parse().unwrap();
            read_pairs(&path, &root, base)
        }
        (None, None) => {
            let base: u64 = arg(&args, "--seed-base").map(|x| x.parse().unwrap()).unwrap_or(SEED_BASE);
            table_cells(&dir, base)
        }
    };
    // `--pairings` keeps the listed cells in their own order, as legality_scan does. An entry "8" keeps every cell
    // numbered 8; "table:8" or "new_decks.tsv:8" keeps one source's (km17 has a pairing 8 in each).
    let cells: Vec<Cell> = match &only {
        Some(list) => {
            let keep = |c: &Cell| {
                list.iter().any(|e| match e.split_once(':') {
                    Some((source, p)) => source == c.source && p.parse::<usize>().ok() == Some(c.pairing),
                    None => e.parse::<usize>().ok() == Some(c.pairing),
                })
            };
            let kept: Vec<Cell> = cells.into_iter().filter(|c| keep(c)).collect();
            for e in list {
                assert!(
                    kept.iter().any(|c| e == &c.pairing.to_string() || e == &format!("{}:{}", c.source, c.pairing)),
                    "--pairings {e}: no such cell"
                );
            }
            kept
        }
        None => cells,
    };
    let trace = arg(&args, "--trace-out").is_some();
    let mut out = arg(&args, "--games-out").map(|p| std::io::BufWriter::new(std::fs::File::create(p).unwrap()));
    let mut rows = arg(&args, "--rows-out").map(|p| std::io::BufWriter::new(std::fs::File::create(p).unwrap()));
    let mut traces = arg(&args, "--trace-out").map(|p| std::io::BufWriter::new(std::fs::File::create(p).unwrap()));
    let mut total: BTreeMap<(String, String), Tally> = BTreeMap::new();
    for cell in &cells {
        let p = cell.pairing;
        let results: Vec<GameCensus> =
            (first_deal..first_deal + games).into_par_iter().map(|i| play_one(cell, i, &bot, trace)).collect();
        for (k, r) in results.iter().enumerate() {
            use std::io::Write;
            let i = first_deal + k as u64;
            if let Some(o) = out.as_mut() {
                writeln!(o, "{}", serde_json::json!({"pairing": p, "i": i, "seed": r.seed, "moves": format!("{:016x}", r.fingerprint)})).unwrap();
            }
            if let Some(o) = rows.as_mut() {
                let mut row = serde_json::json!({
                    "source": cell.source, "pairing": p, "a": cell.names[0], "b": cell.names[1], "a_file": cell.files[0],
                    "b_file": cell.files[1], "i": i,
                    "seed": r.seed, "first_seat": r.first_seat, "seat_decks": r.deck_of, "bots": [bot, bot],
                    "moves": format!("{:016x}", r.fingerprint),
                });
                if !no_counts {
                    let seats: Vec<serde_json::Value> = (0..2)
                        .map(|s| {
                            let cards: serde_json::Map<String, serde_json::Value> = r.seats[s]
                                .iter()
                                .map(|(c, t)| {
                                    (c.clone(), serde_json::json!({"offered": t.offered, "played": t.played, "targets": t.detail}))
                                })
                                .collect();
                            serde_json::json!({"seat": s, "deck": r.deck_of[s], "cards": cards})
                        })
                        .collect();
                    let xspeed: Vec<serde_json::Value> = r
                        .xspeed
                        .iter()
                        .map(|x| serde_json::json!({"seat": x.seat, "turn": x.turn, "hiking_trail": x.hiking_trail, "retreated": x.retreated}))
                        .collect();
                    row["counts"] = serde_json::Value::Array(seats);
                    row["xspeed"] = serde_json::Value::Array(xspeed);
                }
                writeln!(o, "{row}").unwrap();
            }
            if let Some(o) = traces.as_mut() {
                for line in &r.trace {
                    writeln!(o, "{line}").unwrap();
                }
            }
            for (k, v) in &r.t {
                let e = total.entry(k.clone()).or_default();
                e.offered += v.offered;
                e.played += v.played;
                for (d, n) in &v.detail {
                    *e.detail.entry(d.clone()).or_default() += n;
                }
            }
        }
        eprintln!("pairing {p} done");
    }
    if no_counts {
        println!("bot {bot}, deals {first_deal}..{} of {} cells: fingerprints only (--no-counts)", first_deal + games, cells.len());
        return;
    }
    if extended {
        let names: Vec<String> = cells.iter().map(|c| format!("{} {} ({} v {})", c.source, c.pairing, c.names[0], c.names[1])).collect();
        println!("bot {bot}, deals {first_deal}..{} of {} cells: {}", first_deal + games, cells.len(), names.join(", "));
    } else {
        println!("bot {bot}, the table's first {games} deals of each of the 28 pairings (both decks piloted by {bot})");
    }
    println!("deck        card                          turns offered  turns played   (%)   where");
    for ((deck, card), t) in &total {
        let pct = if t.offered > 0 { 100.0 * t.played as f64 / t.offered as f64 } else { 0.0 };
        let detail: Vec<String> = t.detail.iter().map(|(d, n)| format!("{d}: {n}")).collect();
        println!("{deck:<11} {card:<30} {:>13} {:>13} {pct:>6.1}   {}", t.offered, t.played, detail.join("; "));
    }
}
