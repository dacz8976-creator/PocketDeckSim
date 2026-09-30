//! kn smoke (Sept 30; scratch decks only, nothing gates on it). Plays `--num` games of `--deck` against `--opp`, the
//! deck in seat `--seat`, game k on seed `--seed` + k, with `--codes` (the deck's code, the opponent's) built by
//! `create_players` and played by `Game::new` and `play_tick`, as `deckgym simulate --seed-stream` plays them. Per
//! game it prints one JSON row: the result, the deck's chances for `--card` (its turns on which playing the card from
//! hand was offered at some decision, as the floor counts a played Trainer) and the turns it was played, and a
//! fingerprint of every move of the game (to count the games two codes play differently).
//!   kn_smoke --deck D --opp O --card "Peculiar Plaza" --seat 0 --seed 20960000000 --num 100 --codes kn3,km3
use deckgym::actions::SimpleAction;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};
use std::collections::BTreeSet;
use std::hash::{Hash, Hasher};

fn arg(args: &[String], name: &str) -> String {
    let i = args.iter().position(|a| a == name).unwrap_or_else(|| panic!("{name}"));
    args[i + 1].clone()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (deck_path, opp_path, card) = (arg(&args, "--deck"), arg(&args, "--opp"), arg(&args, "--card"));
    let seat: usize = arg(&args, "--seat").parse().unwrap();
    let (seed, num): (u64, u64) = (arg(&args, "--seed").parse().unwrap(), arg(&args, "--num").parse().unwrap());
    let codes: Vec<String> = arg(&args, "--codes").split(',').map(String::from).collect();
    let (deck, opp) = (Deck::from_file(&deck_path).unwrap(), Deck::from_file(&opp_path).unwrap());
    let is_card = |a: &SimpleAction| matches!(a, SimpleAction::Play { trainer_card } if trainer_card.name == card);
    for k in 0..num {
        let (d0, d1) = if seat == 0 { (deck.clone(), opp.clone()) } else { (opp.clone(), deck.clone()) };
        let mut seat_codes = vec![parse_player_code(&codes[1]).unwrap(); 2];
        seat_codes[seat] = parse_player_code(&codes[0]).unwrap();
        let mut game = Game::new(create_players(d0, d1, seat_codes), seed + k);
        let (mut offered, mut used) = (BTreeSet::new(), BTreeSet::new());
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        let mut plies = 0u32;
        while !game.is_game_over() && plies < 5000 {
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            if actor == seat && actions.iter().any(|a| is_card(&a.action)) {
                offered.insert(state.turn_count);
            }
            let chosen = game.play_tick();
            if chosen.actor == seat && is_card(&chosen.action) {
                used.insert(state.turn_count);
            }
            format!("{chosen:?}").hash(&mut hasher);
            plies += 1;
        }
        let end = game.get_state_clone();
        println!(
            "{}",
            serde_json::json!({"deck": deck_path, "opp": opp_path, "card": card, "seat": seat, "seed": seed + k,
                "codes": codes, "winner": format!("{:?}", end.winner), "points": end.points, "turns": end.turn_count,
                "plies": plies, "chances": offered, "used": used, "fingerprint": format!("{:016x}", hasher.finish())})
        );
    }
}
