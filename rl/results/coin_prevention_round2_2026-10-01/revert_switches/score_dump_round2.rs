//! Rules switch 2's revert switches, the revert check (PLAN (e); the cloud, Oct 9): `../switch_gates/score_dump_p2.rs` with its
//! `--revert-return` widened to `--revert LIST`, a comma list of gates (p2, g1 ... g11, or all) turned off for the one decision
//! asked about. Each gate's `with_*` function wraps that decision on this thread (the search is single-threaded), so the engine
//! is the official one at those gates for that one decision. Built into the switch head; main's score_dump.rs, unchanged, is
//! built into the official engine. Both are patched with main's print-only dg_patch.py (PG_DUMP prints every candidate's score).
//!   score_dump --a A.txt --b B.txt --seed-base 23100000000 --pairing 35 --bot km3 --deal 2 --tick 89 [--revert g1,g2]
use deckgym::actions::{
    with_fossil_as_item, with_fossil_item_lock, with_luxury_coin_own_stadium_only, with_own_side_coin, with_own_side_guts,
    with_perish_on_queued_hit, with_plain_hit_coin, with_queued_site_coin, with_return_weakness, with_round2,
    with_trap_territory_each, with_victory_star_after_block_coin, with_will_on_gate_coins,
};
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// Run `f` with every gate in `gates` off, the first outermost.
fn with_off<'a, R>(gates: &'a [String], f: Box<dyn FnOnce() -> R + 'a>) -> R {
    let Some((gate, rest)) = gates.split_first() else {
        return f();
    };
    let inner: Box<dyn FnOnce() -> R + 'a> = Box::new(move || with_off(rest, f));
    match gate.as_str() {
        "p2" => with_return_weakness(false, inner),
        "g1" => with_plain_hit_coin(false, inner),
        "g2" => with_queued_site_coin(false, inner),
        "g3" => with_own_side_coin(false, inner),
        "g4" => with_will_on_gate_coins(false, inner),
        "g5" => with_victory_star_after_block_coin(false, inner),
        "g6" => with_trap_territory_each(false, inner),
        "g7" => with_own_side_guts(false, inner),
        "g8" => with_perish_on_queued_hit(false, inner),
        "g9" => with_luxury_coin_own_stadium_only(false, inner),
        "g10" => with_fossil_item_lock(false, inner),
        "g11" => with_fossil_as_item(false, inner),
        "all" => with_round2(false, inner),
        other => panic!("unknown gate {other:?} (p2, g1 ... g11, all)"),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let seed_base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let pairing: u64 = arg(&args, "--pairing").map(|x| x.parse().unwrap()).unwrap_or(0);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kog3".into());
    let i: u64 = arg(&args, "--deal").expect("--deal").parse().unwrap();
    let tick: usize = arg(&args, "--tick").expect("--tick").parse().unwrap();
    let gates: Vec<String> = arg(&args, "--revert")
        .map(|list| list.split(',').filter(|g| !g.is_empty()).map(str::to_string).collect())
        .unwrap_or_default();
    let mode = if args.iter().any(|a| a == "--tree") { "tree" } else { "1" };
    let seed = seed_base + pairing * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
    let code = || parse_player_code(&bot).unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![code(), code()]), seed);
    for _ in 0..tick {
        assert!(!game.is_game_over(), "the game ended before tick {tick}");
        game.play_tick();
    }
    eprintln!("PGTICK {tick} (the decision asked about; gates off for it: {gates:?})");
    std::env::set_var("PG_DUMP", mode);
    let chosen = with_off(&gates, Box::new(|| game.play_tick()));
    std::env::remove_var("PG_DUMP");
    println!("deal {i}, tick {tick}: chose {:?}", chosen.action);
}
