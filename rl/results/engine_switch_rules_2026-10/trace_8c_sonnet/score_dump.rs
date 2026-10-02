//! Step 8c follow-up (scratch, diagnosis only): replays a game to tick `--tick` on whichever engine this is built into, then plays that one
//! tick with PG_DUMP set, so the (patched, print-only) bot search prints every candidate's score at the decision. The same file is built
//! into the old engine (d363ba8), into R (f8cfa9c) and into a variant of R, each with the same print-only patch in
//! players/expectiminimax_player.rs (dg_patch.py).
//!   score_dump --a A.txt --b B.txt --seed-base 23100000000 --pairing 4 --bot k3 --deal 7 --tick 95 [--tree] [--all-from N]
//! --tree: also print each candidate's principal line. --all-from N: dump every bot decision from tick N on.
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
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
    let all_from: Option<usize> = arg(&args, "--all-from").map(|x| x.parse().unwrap());
    let mode = if args.iter().any(|a| a == "--tree") { "tree" } else { "1" };
    let seed = seed_base + pairing * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
    let code = || parse_player_code(&bot).unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![code(), code()]), seed);
    for t in 0..tick {
        assert!(!game.is_game_over(), "the game ended before tick {tick}");
        if all_from.is_some_and(|n| t >= n) {
            eprintln!("PGTICK {t}");
            std::env::set_var("PG_DUMP", mode);
        }
        game.play_tick();
        std::env::remove_var("PG_DUMP");
    }
    // the coin-Ability Pokemon (A2 114 Bastiodon, B3b 050 Hisuian Goodra, A4 080 Togekiss, B2 124 / B2 204 Meowth) in play at the tick, per seat
    {
        let state = game.get_state_clone();
        let coin = |seat: usize| -> Vec<String> {
            state.in_play_pokemon[seat].iter().flatten().map(|p| p.card.get_id())
                .filter(|id| ["A2 114", "B3b 050", "A4 080", "B2 124", "B2 204"].contains(&id.as_str())).collect()
        };
        eprintln!("PGBOARD coin seat0={:?} seat1={:?}", coin(0), coin(1));
    }
    eprintln!("PGTICK {tick} (the decision asked about)");
    std::env::set_var("PG_DUMP", mode);
    // --revert-queued (only in the VAR build): for this one decision the engine queues a coin target's damage as the plain ApplyDamage again
    if args.iter().any(|a| a == "--revert-queued") {
        std::env::set_var("PG_QUEUED_AS_APPLYDAMAGE", "1");
    }
    // --revert-cut (only in the VAR2 build): for this one decision a finite coin cut comes off the raw damage before the modifiers again (the old order)
    if args.iter().any(|a| a == "--revert-cut") {
        std::env::set_var("PG_CUT_BEFORE", "1");
    }
    let chosen = game.play_tick();
    std::env::remove_var("PG_DUMP");
    std::env::remove_var("PG_QUEUED_AS_APPLYDAMAGE");
    std::env::remove_var("PG_CUT_BEFORE");
    println!("deal {i}, tick {tick}: chose {:?}", chosen.action);
}
