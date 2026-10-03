//! The play-out chooser's run-time lists (`KX_EXTRA_LISTS`; fixes round 1, Oct 3), in a test binary of its own: the
//! variable is read once per process, so no other test may run beside it.
use std::collections::BTreeMap;

use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{Knowledge, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, parse_player_code};
use deckgym::test_support::load_test_decks;
use deckgym::Game;
use rand::{rngs::StdRng, SeedableRng};

/// An extra list makes LAB exact for that opponent (the test decks' weezing-arbok, outside the meta pool), names it in
/// the label, and lets REALISTIC draw it: once the opponent's Weezing line is seen, it is the only consistent list.
#[test]
fn an_extra_list_makes_lab_exact_and_realistic_can_draw_it() {
    std::env::set_var("KX_EXTRA_LISTS", "arbok=example_decks/weezing-arbok.txt");
    let (deck_a, deck_b) = load_test_decks();
    // A battle position with the opponent's Pokémon in play and three or more distinct moves for player 0.
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a.clone(), deck_b.clone(), vec![km3(), km3()]), 3);
    let state = loop {
        assert!(!game.is_game_over());
        let state = game.get_state_clone();
        let (actor, actions) = state.generate_possible_actions();
        let distinct: std::collections::BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
        if actor == 0 && state.turn_count >= 3 && state.current_player == 0 && distinct.len() >= 3 {
            break state;
        }
        game.play_tick();
    };
    let actions = state.generate_possible_actions().1;
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let small = |knowledge| PlayoutParams { rollouts: 4, cap: 4, knowledge, ..PlayoutParams::new(3) };

    let mut lab = PlayoutPlayer::new(deck_a.clone(), deck_b.clone(), small(Knowledge::Lab));
    let label = lab.knowledge_label();
    assert!(label.starts_with("LAB (laboratory condition") && label.contains("extra:arbok") && label.contains("8 meta lists"), "{label}");
    let report = lab.evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    assert_eq!(report.lists, BTreeMap::from([("the exact list (LAB)".to_string(), 4)]));

    let mut real = PlayoutPlayer::new(deck_a, deck_b, small(Knowledge::Realistic));
    assert!(real.knowledge_label().contains("1 extra list from KX_EXTRA_LISTS: arbok"), "{}", real.knowledge_label());
    let report = real.evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    assert_eq!(report.lists, BTreeMap::from([("extra:arbok (1 of 1 consistent)".to_string(), 4)]));
}
