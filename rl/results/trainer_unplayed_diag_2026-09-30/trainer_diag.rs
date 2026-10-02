//! km3 unplayed-Trainer diagnosis (Sept 30; diagnosis only, nothing gates on it). Replays named floor games
//! (rl/results/floor_dustin_2026-09-30/) at the official engine's source (main-d363ba8) exactly as `deckgym simulate
//! --seed-stream` plays them: `create_players` with km3 on both sides, `Game::new` on the game's own seed, `play_tick`.
//! At each decision of the deck's seat where playing `--card` from hand is offered, it asks km3 for its root score of
//! every offered move (`diag_km_root_scores`: the same observation, determinization seed and search seed as the real
//! decision) and prints one JSON row: the turn, the offered moves with their scores, the move km3 then played, and a
//! board summary. It checks that the best-scoring move is the move played. A last row per game gives the final points
//! and turn, to check the replay against the floor's per-game file.
//!   trainer_diag --deck D --opponents DIR --card "Iris" --games t-altaria:0:7103,t-blaziken:1:8612
use deckgym::actions::SimpleAction;
use deckgym::models::{Card, TrainerType};
use deckgym::observation::canonical_actions;
use deckgym::players::expectiminimax_player::diag_km_root_scores;
use deckgym::players::value_functions::public_clock_effect_km_value_function as km_value;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn side(state: &State, p: usize) -> serde_json::Value {
    let mons: Vec<serde_json::Value> = state
        .enumerate_in_play_pokemon(p)
        .map(|(idx, x)| {
            let retreat = match &x.card {
                Card::Pokemon(c) => c.retreat_cost.len() as i64,
                _ => -1,
            };
            serde_json::json!({"slot": idx, "name": x.get_name(), "hp": x.get_remaining_hp(),
                "energy": x.attached_energy.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
                "printed_retreat": retreat, "tools": x.attached_tools.len()})
        })
        .collect();
    serde_json::json!({"in_play": mons, "hand": state.hands[p].iter().map(|c| c.get_name()).collect::<Vec<_>>(),
        "points": state.points[p]})
}

/// Whether km's score reads the card's effect at all: km's static score (the real state, from the deck's side) after
/// really playing the card, minus its score after only moving the card from hand to the discard pile. 0 means the
/// score gives the effect nothing; the card leaving the hand is priced the same either way.
fn static_effect(state: &State, seat: usize, play: &deckgym::actions::Action, card: &str, decks: (&Deck, &Deck)) -> (f64, f64, f64) {
    let now = km_value(state, seat);
    let players = create_players(decks.0.clone(), decks.1.clone(), vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()]);
    let mut side = Game::from_state(state.clone(), players, 0);
    side.apply_action(play);
    let played = km_value(&side.get_state_clone(), seat);
    let mut only = state.clone();
    if let Some(i) = only.hands[seat].iter().position(|c| c.get_name() == card) {
        let c = only.hands[seat].remove(i);
        only.discard_piles[seat].push(c);
    }
    let hand_only = km_value(&only, seat);
    (now, played, hand_only)
}

fn is_supporter(action: &SimpleAction) -> bool {
    matches!(action, SimpleAction::Play { trainer_card } if trainer_card.trainer_card_type == TrainerType::Supporter)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_path = arg(&args, "--deck").expect("--deck");
    let opp_dir = arg(&args, "--opponents").expect("--opponents");
    let card = arg(&args, "--card").expect("--card");
    let deck = Deck::from_file(&deck_path).expect("deck");
    for spec in arg(&args, "--games").expect("--games").split(',') {
        let parts: Vec<&str> = spec.split(':').collect();
        let (opp_name, seat, seed): (&str, usize, u64) = (parts[0], parts[1].parse().unwrap(), parts[2].parse().unwrap());
        let opp = Deck::from_file(&format!("{opp_dir}/{opp_name}.txt")).expect("opponent deck");
        let (d0, d1) = if seat == 0 { (deck.clone(), opp.clone()) } else { (opp.clone(), deck.clone()) };
        let code = || parse_player_code("km3").unwrap();
        let players = create_players(d0, d1, vec![code(), code()]);
        let mut game = Game::new(players, seed);
        let mut counts = [0u64; 2];
        let mut tick = 0usize;
        let mut mismatches = 0usize;
        while !game.is_game_over() {
            let state = game.get_state_clone();
            let (actor, mut actions) = state.generate_possible_actions();
            canonical_actions(&mut actions);
            let mut probe = None;
            if actions.len() > 1 {
                let decision = game.randomness().decision(actor, counts[actor]);
                counts[actor] += 1;
                let offered = actions.iter().any(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == card));
                if actor == seat && offered {
                    let observation = game.observation(actor);
                    let mut rng = StdRng::seed_from_u64(decision.search_seed);
                    let scores = diag_km_root_scores(deck.clone(), 3, &mut rng, &observation, &actions);
                    let play = actions.iter().find(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == card)).unwrap().clone();
                    let (d0, d1) = if seat == 0 { (&deck, &opp) } else { (&opp, &deck) };
                    let fx = static_effect(&state, seat, &play, &card, (d0, d1));
                    probe = Some((scores, fx));
                }
            }
            let chosen = game.play_tick();
            let after = game.get_state_clone();
            let brief = |st: &State, q: usize| st.maybe_get_active(q).map(|a| format!("{} {}hp {}E", a.get_name(), a.get_remaining_hp(), a.attached_energy.len()));
            let track = serde_json::json!({"points_before": state.points, "points_after": after.points,
                "own_active": brief(&state, seat), "opp_active": brief(&state, 1 - seat)});
            if let Some((scores, fx)) = probe {
                // The decision's own rule: the best score, ties to the shorter win, then the later move.
                let best = (0..scores.len())
                    .max_by(|&a, &b| {
                        scores[a].0.partial_cmp(&scores[b].0).unwrap().then_with(|| {
                            let (wa, wb) = (scores[a].1, scores[b].1);
                            match (wa, wb) {
                                (Some(x), Some(y)) => y.cmp(&x),
                                (Some(_), None) => std::cmp::Ordering::Greater,
                                (None, Some(_)) => std::cmp::Ordering::Less,
                                (None, None) => std::cmp::Ordering::Equal,
                            }
                        })
                    })
                    .unwrap();
                let chosen_idx = actions.iter().position(|a| a.action == chosen.action);
                if chosen_idx != Some(best) {
                    mismatches += 1;
                }
                let moves: Vec<serde_json::Value> = actions
                    .iter()
                    .zip(&scores)
                    .map(|(a, (s, w))| serde_json::json!({"move": format!("{:?}", a.action), "score": s, "win_distance": w}))
                    .collect();
                println!("{}", serde_json::json!({"opponent": opp_name, "seat": seat, "seed": seed, "tick": tick,
                    "turn": state.turn_count, "moves": moves, "chosen": format!("{:?}", chosen.action),
                    "chosen_idx": chosen_idx, "best_idx": best, "own": side(&state, seat), "opp": side(&state, 1 - seat),
                    "chosen_supporter": is_supporter(&chosen.action),
                    "static": {"now": fx.0, "after_playing": fx.1, "after_only_discarding": fx.2, "effect": fx.1 - fx.2},
                    "track": track}));
            } else {
                // Every other move of the deck, so a turn's whole line is on record.
                if chosen.actor == seat {
                    println!("{}", serde_json::json!({"opponent": opp_name, "seat": seat, "seed": seed, "tick": tick,
                        "turn": state.turn_count, "chosen": format!("{:?}", chosen.action), "move_only": true,
                        "chosen_supporter": is_supporter(&chosen.action), "track": track}));
                } else {
                    // The opponent's moves too (Goo-zooka's effect lands on their next turn: did they retreat, and
                    // with how much Energy on the Active against its printed Retreat Cost).
                    let opp_active = state.maybe_get_active(1 - seat).map(|a| {
                        let printed = match &a.card { Card::Pokemon(c) => c.retreat_cost.len() as i64, _ => -1 };
                        serde_json::json!({"name": a.get_name(), "energy": a.attached_energy.len(), "printed_retreat": printed})
                    });
                    println!("{}", serde_json::json!({"opponent": opp_name, "seat": seat, "seed": seed, "tick": tick,
                        "turn": state.turn_count, "chosen": format!("{:?}", chosen.action), "opp_move": true,
                        "opp_active_before": opp_active, "track": track}));
                }
            }
            tick += 1;
        }
        let end = game.get_state_clone();
        println!("{}", serde_json::json!({"opponent": opp_name, "seat": seat, "seed": seed, "done": true,
            "points": end.points, "turns": end.turn_count, "winner": format!("{:?}", end.winner), "probe_mismatches": mismatches}));
    }
}
