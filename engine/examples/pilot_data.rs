//! The planning pilot's data (branch claude/planning-pilot-data, Oct 2; rl/results/planning_pilot_data_2026-10-02/README.md).
//! Self-play games with one bot (km3) on both sides over a pool of lists, every pairing of two of them; for every decision
//! point (two or more moves offered) one row: the deal (pairing, i, seed, tick), the mover's seat and list, the features of
//! the position from the mover's view (`players::value_functions::pilot_features`, on the state km itself evaluates: the
//! mover's `PlayerObservation::search_state`), the move chosen, and the game's result for the mover. `own_turn` says
//! whether the decision is in the mover's own turn (a promotion after a knockout in the opponent's turn is not); `setup`
//! marks turn 0's choices.
//!
//! The games are legality_scan's: seed = base + pairing x stride + i; the first-named list sits in seat 0 when i is even
//! and in seat 1 when i is odd; `create_players` and `Game::new(players, seed)`; the example only reads states between
//! ticks, so each game's `moves` fingerprint (legality_scan's: a hash of every chosen Action) equals legality_scan's on
//! the same seed. On every row, km's terms added up as km adds them (`km_value`) are checked against km's own value
//! function on the same state; a mismatch is counted per game (`km_check_bad`) and printed.
//!   pilot_data --pool <pool.tsv> --root <repo root> --seed-base 24000000000 --stride 100000 --games <n per pairing>
//!              [--first-game <i0>] [--pairings 0,5,...] [--bot km3] --rows <rows.tsv> --games-out <games.jsonl>
//! Threads: rayon's (RAYON_NUM_THREADS).
use deckgym::actions::SimpleAction;
use deckgym::observation::{with_public_pricing, PlayerObservation, RevealedKnowledge};
use deckgym::players::value_functions::pilot_features::{pilot_features, Row};
use deckgym::players::{create_players, parse_player_code, public_clock_effect_km_value_function};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game};
use rand::{rngs::StdRng, SeedableRng};
use rayon::prelude::*;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::io::Write;
use std::path::PathBuf;
use std::time::Instant;

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// The meta columns before the features, and the label columns after them.
const META: [&str; 10] = ["pairing", "i", "seed", "tick", "seat", "deck", "opp_deck", "n_offered", "chosen_kind", "own_turn"];
const LABELS: [&str; 5] = ["result", "final_points_mine", "final_points_opp", "final_turn", "game_ticks"];

struct Decision {
    seat: usize,
    tick: u32,
    row: Row,
    n_offered: usize,
    chosen_kind: String,
    own_turn: bool,
}

struct GameOut {
    lines: Vec<String>,
    header: Option<String>,
    summary: String,
    rows: usize,
    km_bad: usize,
}

fn play(decks: &[(String, Deck)], bot: &str, seed: u64, pairing: usize, i: u64, (a, b): (usize, usize)) -> GameOut {
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (a, b) } else { (b, a) };
    let code = || parse_player_code(bot).unwrap();
    let players = create_players(decks[d0].1.clone(), decks[d1].1.clone(), vec![code(), code()]);
    let mut game = Game::new(players, seed);
    let seat_deck = [d0, d1];
    let mut moves = DefaultHasher::new();
    let mut decisions: Vec<Decision> = Vec::new();
    let (mut first_player, mut first_attack_turn): (Option<usize>, [Option<u8>; 2]) = (None, [None, None]);
    let (mut tick, mut km_bad) = (0u32, 0usize);
    while !game.is_game_over() {
        let before = game.get_state_clone();
        if first_player.is_none() && before.turn_count >= 1 {
            first_player = Some(before.current_player);
        }
        let (actor, actions) = before.generate_possible_actions();
        let row = (actions.len() > 1).then(|| {
            let view = PlayerObservation::from_state(&before, actor, &RevealedKnowledge::default())
                .search_state(&mut StdRng::seed_from_u64(7));
            let (row, km) = with_public_pricing(|| {
                (pilot_features(&view, actor, false), public_clock_effect_km_value_function(&view, actor))
            });
            let total = row.iter().find(|(n, _)| n == "km_value").map(|(_, v)| *v).unwrap();
            if (total - km).abs() > 1e-6 * km.abs().max(1.0) {
                km_bad += 1;
                eprintln!("km check: pairing {pairing} i {i} tick {tick}: terms add to {total}, km's value {km}");
            }
            row
        });
        let chosen = game.play_tick();
        format!("{:?}", chosen).hash(&mut moves);
        if matches!(chosen.action, SimpleAction::Attack(_)) && !chosen.is_stack {
            first_attack_turn[chosen.actor].get_or_insert(before.turn_count);
        }
        if let Some(row) = row {
            let kind: String = format!("{:?}", chosen.action).chars().take_while(|c| c.is_alphanumeric()).collect();
            decisions.push(Decision {
                seat: actor,
                tick,
                row,
                n_offered: actions.len(),
                chosen_kind: kind,
                own_turn: before.current_player == actor,
            });
        }
        tick += 1;
    }
    let end = game.get_state_clone();
    let winner: Option<usize> = match end.winner {
        Some(GameOutcome::Win(p)) => Some(p),
        _ => None,
    };
    let first = first_player.unwrap_or(0);
    let header = decisions.first().map(|d| {
        META.iter().map(|s| s.to_string())
            .chain(d.row.iter().map(|(n, _)| n.clone()))
            .chain(LABELS.iter().map(|s| s.to_string()))
            .collect::<Vec<_>>()
            .join("\t")
    });
    let lines: Vec<String> = decisions
        .into_iter()
        .map(|d| {
            let result = match winner {
                Some(p) if p == d.seat => "1",
                Some(_) => "0",
                None => "0.5",
            };
            let mut cols: Vec<String> = vec![
                pairing.to_string(), i.to_string(), seed.to_string(), d.tick.to_string(), d.seat.to_string(),
                decks[seat_deck[d.seat]].0.clone(), decks[seat_deck[1 - d.seat]].0.clone(), d.n_offered.to_string(),
                d.chosen_kind, (d.own_turn as u8).to_string(),
            ];
            for (name, v) in &d.row {
                let v = if name == "went_first" { (d.seat == first) as u8 as f64 } else { *v };
                cols.push(if v == v.trunc() && v.abs() < 1e15 { format!("{}", v as i64) } else { format!("{v:.6}") });
            }
            cols.extend([
                result.to_string(), end.points[d.seat].to_string(), end.points[1 - d.seat].to_string(),
                end.turn_count.to_string(), tick.to_string(),
            ]);
            cols.join("\t")
        })
        .collect();
    let summary = serde_json::json!({
        "pairing": pairing, "i": i, "seed": seed,
        "decks": [decks[d0].0.clone(), decks[d1].0.clone()],
        "first_player": first, "winner": winner.map_or(-1, |w| w as i64),
        "points": end.points, "turns": end.turn_count, "ticks": tick,
        "moves": format!("{:016x}", moves.finish()),
        "first_attack_turn": first_attack_turn, "rows": lines.len(), "km_check_bad": km_bad,
    })
    .to_string();
    GameOut { rows: lines.len(), lines, header, summary, km_bad }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let root = PathBuf::from(arg(&args, "--root").unwrap_or_else(|| "..".into()));
    let pool = std::fs::read_to_string(arg(&args, "--pool").expect("--pool")).expect("pool file");
    let decks: Vec<(String, Deck)> = pool
        .lines()
        .skip(1)
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let c: Vec<&str> = l.split('\t').collect();
            (c[0].to_string(), Deck::from_file(root.join(c[1]).to_str().unwrap()).unwrap_or_else(|e| panic!("{}: {e}", c[1])))
        })
        .collect();
    let mut pairs: Vec<(usize, usize)> = Vec::new();
    for a in 0..decks.len() {
        for b in a + 1..decks.len() {
            pairs.push((a, b));
        }
    }
    let base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let stride: u64 = arg(&args, "--stride").map_or(100_000, |s| s.parse().unwrap());
    let games: u64 = arg(&args, "--games").expect("--games").parse().unwrap();
    let first_game: u64 = arg(&args, "--first-game").map_or(0, |s| s.parse().unwrap());
    let bot = arg(&args, "--bot").unwrap_or_else(|| "km3".into());
    let only: Option<Vec<usize>> = arg(&args, "--pairings").map(|s| s.split(',').map(|x| x.parse().unwrap()).collect());
    let mut rows_out = std::io::BufWriter::new(std::fs::File::create(arg(&args, "--rows").expect("--rows")).unwrap());
    let mut games_out = std::io::BufWriter::new(std::fs::File::create(arg(&args, "--games-out").expect("--games-out")).unwrap());
    let start = Instant::now();
    let (mut n_games, mut n_rows, mut n_bad, mut header_written) = (0usize, 0usize, 0usize, false);
    for (pairing, &(a, b)) in pairs.iter().enumerate() {
        if only.as_ref().is_some_and(|o| !o.contains(&pairing)) {
            continue;
        }
        let t = Instant::now();
        let outs: Vec<GameOut> = (first_game..first_game + games)
            .into_par_iter()
            .map(|i| play(&decks, &bot, base + pairing as u64 * stride + i, pairing, i, (a, b)))
            .collect();
        let rows: usize = outs.iter().map(|o| o.rows).sum();
        for o in outs {
            if !header_written {
                if let Some(h) = &o.header {
                    writeln!(rows_out, "{h}").unwrap();
                    header_written = true;
                }
            }
            for line in &o.lines {
                writeln!(rows_out, "{line}").unwrap();
            }
            writeln!(games_out, "{}", o.summary).unwrap();
            n_bad += o.km_bad;
        }
        n_games += games as usize;
        n_rows += rows;
        println!(
            "pairing {pairing} ({} v {}): {games} games, {rows} rows, {:.1}s",
            decks[a].0, decks[b].0, t.elapsed().as_secs_f64()
        );
        rows_out.flush().unwrap();
        games_out.flush().unwrap();
    }
    let secs = start.elapsed().as_secs_f64();
    println!(
        "total: {n_games} games, {n_rows} rows, {secs:.1}s, {:.3} games/s, {:.1} rows/s, threads {}; km check mismatches: {n_bad}",
        n_games as f64 / secs, n_rows as f64 / secs, rayon::current_num_threads()
    );
}
