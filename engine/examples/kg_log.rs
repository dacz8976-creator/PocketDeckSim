//! ky3 item 7's self-play logger (print-only; see src/kg_log.rs). Plays the deck under study against an opponent list, one game per
//! seed, and prints one JSON line per game on stdout (the file analyze_kg.py reads):
//!   kg_log --deck D.txt --opp O.txt --deck-pilot km3 --opp-pilot km3 --seat 0|1 --seed-base S --games N
//! Game i uses seed S+i and puts the deck under study in `--seat` (default 0); the record carries `deck_seat`, the seed and the codes.
use deckgym::kg_log::play_logged;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let need = |n: &str| arg(&args, n).unwrap_or_else(|| panic!("missing {n}"));
    let deck = Deck::from_file(&need("--deck")).expect("deck");
    let opp = Deck::from_file(&need("--opp")).expect("opponent list");
    let (code_deck, code_opp) = (arg(&args, "--deck-pilot").unwrap_or("km3".into()), arg(&args, "--opp-pilot").unwrap_or("km3".into()));
    let seat: usize = arg(&args, "--seat").map(|s| s.parse().expect("--seat 0|1")).unwrap_or(0);
    assert!(seat < 2, "--seat is 0 or 1");
    let seed_base: u64 = need("--seed-base").parse().expect("--seed-base");
    let games: u64 = arg(&args, "--games").map(|s| s.parse().expect("--games")).unwrap_or(1);
    for i in 0..games {
        let seed = seed_base + i;
        let (d0, d1, c0, c1) = if seat == 0 { (&deck, &opp, &code_deck, &code_opp) } else { (&opp, &deck, &code_opp, &code_deck) };
        let players = create_players(d0.clone(), d1.clone(), vec![parse_player_code(c0).expect("pilot code"), parse_player_code(c1).expect("pilot code")]);
        let mut game = Game::new(players, seed);
        let mut rec = play_logged(&mut game, seat);
        rec["seed"] = seed.into();
        rec["pilot_deck"] = code_deck.clone().into();
        rec["pilot_opp"] = code_opp.clone().into();
        println!("{rec}");
    }
}
