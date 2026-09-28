//! kog's check 3: where two codes' games on one table deal first differ. Built as an example (copy into
//! engine/examples/, `cargo build --release --example first_divergence`); it only watches.
//!
//!   first_divergence --decks ../decks/research --a altaria --b blaziken --pairing 1 --i 15 --x kog3 --y koa3
//!       [--fx <x's moves hex> --fy <y's moves hex>]
//!
//! Each game is played as legality_scan plays it (seed 72,000,000 + pairing x 10,000 + i; even i puts deck a in seat
//! 0; both seats piloted by the same code), and its move fingerprint is computed the same way, so `--fx`/`--fy`
//! check the replay is the table's game. Prints the first step where the two games' chosen moves differ: the turn
//! (0 = setup), who chose, how many moves were offered, both moves, and that player's discard-pile Energy, Flame
//! Patch copies in hand and deck, and Active.
use deckgym::actions::Action;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).map(|i| args[i + 1].clone())
}

struct Step {
    turn: u8,
    actor: usize,
    offered: usize,
    chosen: String,
    before: State,
}

fn play(dir: &str, a: &str, b: &str, pairing: u64, i: u64, code: &str) -> (Vec<Step>, String) {
    let deck = |n: &str| Deck::from_file(&format!("{dir}/{n}.txt")).unwrap();
    let (d0, d1) = if i % 2 == 0 { (deck(a), deck(b)) } else { (deck(b), deck(a)) };
    let c = parse_player_code(code).unwrap();
    let mut game = Game::new(create_players(d0, d1, vec![c.clone(), c]), 72_000_000 + pairing * 10_000 + i);
    let (mut steps, mut moves) = (Vec::new(), DefaultHasher::new());
    while !game.is_game_over() {
        let before = game.get_state_clone();
        let (actor, actions) = before.generate_possible_actions();
        let chosen: Action = game.play_tick();
        format!("{:?}", chosen).hash(&mut moves);
        steps.push(Step { turn: before.turn_count, actor, offered: actions.len(), chosen: format!("{:?}", chosen.action), before });
    }
    (steps, format!("{:016x}", moves.finish()))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let get = |n: &str| arg(&args, n).unwrap_or_else(|| panic!("{n} is required"));
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let (a, b) = (get("--a"), get("--b"));
    let (pairing, i): (u64, u64) = (get("--pairing").parse().unwrap(), get("--i").parse().unwrap());
    let (x, y) = (get("--x"), get("--y"));
    let (gx, fx) = play(&dir, &a, &b, pairing, i, &x);
    let (gy, fy) = play(&dir, &a, &b, pairing, i, &y);
    let check = |want: Option<String>, got: &str| want.map_or("not checked".to_string(), |w| (w == got).to_string());
    println!("seed {}: {x} moves {fx} (table: {}), {y} moves {fy} (table: {})", 72_000_000 + pairing * 10_000 + i,
             check(arg(&args, "--fx"), &fx), check(arg(&args, "--fy"), &fy));
    let Some(k) = (0..gx.len().min(gy.len())).find(|&k| gx[k].chosen != gy[k].chosen) else {
        println!("no difference in {} steps", gx.len().min(gy.len()));
        return;
    };
    let (sx, sy) = (&gx[k], &gy[k]);
    let st = &sx.before;
    let seat = |p: usize| if (p == 0) == (i % 2 == 0) { a.clone() } else { b.clone() };
    let flame = |cards: &mut dyn Iterator<Item = String>| cards.filter(|n| n == "Flame Patch").count();
    println!(
        "first difference at step {k}: turn {} ({}), player {} ({}) chooses from {} moves; same state in both: {}",
        sx.turn,
        if sx.turn == 0 { "setup" } else { "play" },
        sx.actor,
        seat(sx.actor),
        sx.offered,
        format!("{:?}", sx.before.in_play_pokemon) == format!("{:?}", sy.before.in_play_pokemon)
            && sx.before.hands == sy.before.hands
    );
    println!("  {x}: {}\n  {y}: {}", sx.chosen, sy.chosen);
    let p = sx.actor;
    println!(
        "  that player: discard-pile Energy {:?}; Flame Patch in hand {}, in deck {}; Active {}",
        st.discard_energies[p],
        flame(&mut st.hands[p].iter().map(|c| c.get_name())),
        flame(&mut st.decks[p].cards.iter().map(|c| c.get_name())),
        st.maybe_get_active(p).map_or("none".into(), |c| format!("{} ({} Energy)", c.get_name(), c.attached_energy.len()))
    );
}
