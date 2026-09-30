//! Coin-flip prevention repair, Sonnet's S3 (Sept 30; scratch, diagnosis only). Replays chosen smoke-check games tick by
//! tick and prints one JSON line per tick: the deal, the tick, the mover, the turn, the offered moves (when there are two
//! or more), the chosen move and a board summary. The game is set up exactly as legality_scan's `play_one` sets up a
//! `--pairs` row (seed = seed base + pairing x 10,000 + i; even i puts the first-named deck in seat 0), and a last line
//! gives legality_scan's move fingerprint, to check the replay against the smoke files. Built as an example in a scratch
//! copy of each engine; diffing two engines' dumps gives each game's first differing decision.
//!   coin_trace --a fire_heatmor.txt --b meowth_carefree.txt --seed-base 20950000000 --bot kog3 --deals 16,23,29,32
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn board(state: &State) -> serde_json::Value {
    let side = |p: usize| -> Vec<String> {
        state
            .enumerate_in_play_pokemon(p)
            .map(|(idx, x)| format!("{idx}:{} {}hp {}E", x.get_name(), x.get_remaining_hp(), x.attached_energy.len()))
            .collect()
    };
    serde_json::json!({"p0": side(0), "p1": side(1), "hands": [state.hands[0].len(), state.hands[1].len()]})
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let seed_base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let pairing: u64 = arg(&args, "--pairing").map(|x| x.parse().unwrap()).unwrap_or(0);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kog3".into());
    let deals: Vec<u64> = arg(&args, "--deals").expect("--deals").split(',').map(|x| x.parse().unwrap()).collect();
    for i in deals {
        let seed = seed_base + pairing * 10_000 + i;
        let first_seat = if i % 2 == 0 { 0 } else { 1 };
        let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
        let code = || parse_player_code(&bot).unwrap();
        let players = create_players(d0.clone(), d1.clone(), vec![code(), code()]);
        let mut game = Game::new(players, seed);
        let mut moves = DefaultHasher::new();
        let mut tick = 0usize;
        while !game.is_game_over() {
            let before = game.get_state_clone();
            let (actor, actions) = before.generate_possible_actions();
            let chosen = game.play_tick();
            format!("{:?}", chosen).hash(&mut moves);
            let offered: Vec<String> = if actions.len() > 1 {
                actions.iter().map(|a| format!("{:?}", a.action)).collect()
            } else {
                vec![]
            };
            println!(
                "{}",
                serde_json::json!({"i": i, "tick": tick, "actor": actor, "chosen_actor": chosen.actor,
                    "turn": before.turn_count, "n": actions.len(), "offered": offered,
                    "chosen": format!("{:?}", chosen.action), "board": board(&before)})
            );
            tick += 1;
        }
        println!("{}", serde_json::json!({"i": i, "done": true, "ticks": tick, "first_seat": first_seat,
            "moves": format!("{:016x}", moves.finish())}));
    }
}
