//! Scratch probe: replay a floor game with km3 to the start of `--turn`, then play that turn with `--code` on the deck's
//! side (km3 the opponent), from `Game::from_state` on the game's seed as tests/kr_judged_turns_test.rs does. At each
//! decision of the deck where Goo-zooka is offered, print kr's and km's root scores and the opponent's clock pieces
//! now, after Goo-zooka then EndTurn, and after EndTurn alone.
use deckgym::actions::SimpleAction;
use deckgym::observation::canonical_actions;
use deckgym::players::expectiminimax_player::diag_root_scores;
use deckgym::players::value_functions::{diag_kr_clock, public_clock_effect_km_value_function as km, public_clock_effect_kr_value_function as kr};
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;

fn arg(args: &[String], name: &str) -> String {
    args[args.iter().position(|a| a == name).unwrap() + 1].clone()
}

fn after(state: &State, d: (&Deck, &Deck), moves: &[&str]) -> State {
    let players = create_players(d.0.clone(), d.1.clone(), vec![parse_player_code("km3").unwrap(); 2]);
    let mut g = Game::from_state(state.clone(), players, 0);
    for m in moves {
        let (_, actions) = g.get_state_clone().generate_possible_actions();
        let a = actions.iter().find(|a| match (&a.action, *m) {
            (SimpleAction::EndTurn, "EndTurn") => true,
            (SimpleAction::Play { trainer_card }, n) => trainer_card.name == n,
            _ => false,
        });
        match a { Some(a) => g.apply_action(a), None => return g.get_state_clone() }
    }
    g.get_state_clone()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck = Deck::from_file(&arg(&args, "--deck")).unwrap();
    let opp = Deck::from_file(&arg(&args, "--opp")).unwrap();
    let seat: usize = arg(&args, "--seat").parse().unwrap();
    let seed: u64 = arg(&args, "--seed").parse().unwrap();
    let turn: u8 = arg(&args, "--turn").parse().unwrap();
    let code = arg(&args, "--code");
    let (d0, d1) = if seat == 0 { (deck.clone(), opp.clone()) } else { (opp.clone(), deck.clone()) };
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![km3(), km3()]), seed);
    while !(game.get_state_clone().turn_count == turn && game.get_state_clone().current_player == seat) {
        game.play_tick();
    }
    let start = game.get_state_clone();
    let mut codes = vec![km3(), km3()];
    codes[seat] = parse_player_code(&code).unwrap();
    let mut g = Game::from_state(start, create_players(d0.clone(), d1.clone(), codes), seed);
    let mut counts = [0u64; 2];
    let goo = "Team Rocket's Goo-zooka";
    while !g.is_game_over() && g.get_state_clone().turn_count == turn {
        let state = g.get_state_clone();
        let (actor, mut actions) = state.generate_possible_actions();
        canonical_actions(&mut actions);
        if actions.len() > 1 {
            let decision = g.randomness().decision(actor, counts[actor]);
            counts[actor] += 1;
            if actor == seat && actions.iter().any(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == goo)) {
                let observation = g.observation(actor);
                println!("-- decision, hand {:?}", state.hands[seat].iter().map(|c| c.get_name()).collect::<Vec<_>>());
                for (label, f) in [("kr", kr as fn(&State, usize) -> f64), ("km", km)] {
                    let mut rng = StdRng::seed_from_u64(decision.search_seed);
                    let scores = diag_root_scores(deck.clone(), f, &mut rng, &observation, &actions);
                    let mut rows: Vec<(f64, String)> = actions.iter().zip(&scores).map(|(a, s)| (s.0, format!("{:?}", a.action).chars().take(70).collect())).collect();
                    rows.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
                    println!("   {label}: {:?}", &rows[..rows.len().min(6)]);
                }
                let dd = (&d0, &d1);
                println!("   now:           {}", diag_kr_clock(&state, seat));
                println!("   goo, EndTurn:  {}", diag_kr_clock(&after(&state, dd, &[goo, "EndTurn"]), seat));
                println!("   EndTurn:       {}", diag_kr_clock(&after(&state, dd, &["EndTurn"]), seat));
            }
        }
        let chosen = g.play_tick();
        if chosen.actor == seat { println!("{:?}", format!("{:?}", chosen.action).chars().take(90).collect::<String>()); }
    }
}
