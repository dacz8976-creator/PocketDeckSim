//! The play-out chooser (`kx<N>`, engine/src/players/playout_player.rs; branch claude/playout-pilot, Oct 2). Written
//! before the player: the parse of its code, an immediate win taken, km3's move kept within the noise, the drops of the
//! candidate cap reported, no information leak (the same observation over different hidden cards gives the same
//! evaluation and the same move, also through `Game`), and determinism (same seeds, same moves).
use deckgym::actions::{Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{Knowledge, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, parse_player_code, PlayerCode};
use deckgym::test_support::{get_test_game_with_board, load_test_decks};
use deckgym::{Game, State};
use rand::{rngs::StdRng, SeedableRng};

/// Small play-out settings for tests: 4 play-outs per candidate, at most 4 candidates.
fn small(knowledge: Knowledge, z: f64) -> PlayoutParams {
    PlayoutParams { rollouts: 4, cap: 4, z, knowledge, ..PlayoutParams::new(3) }
}

fn pilot(params: PlayoutParams) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    PlayoutPlayer::new(deck_a, deck_b, params)
}

/// km3's own choice for `actor` at `state`, with the decision randomness the pilot is given.
fn km3_choice(state: &State, actor: usize, seed: u64) -> Action {
    let (deck_a, deck_b) = load_test_decks();
    let mut km3 = create_players(deck_a, deck_b, vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()])
        .remove(actor);
    let observation = PlayerObservation::from_state(state, actor, &RevealedKnowledge::default());
    let actions = state.generate_possible_actions().1;
    km3.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions)
}

/// A battle position (turn 3 or later) where player 0 decides among three or more distinct moves: km3 plays a test-deck
/// game from `seed` until one comes.
fn midgame(seed: u64) -> State {
    let (deck_a, deck_b) = load_test_decks();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), seed);
    loop {
        assert!(!game.is_game_over(), "seed {seed}: the game ended before a position came");
        let state = game.get_state_clone();
        let (actor, actions) = state.generate_possible_actions();
        let distinct: std::collections::BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
        if actor == 0 && state.turn_count >= 3 && state.current_player == 0 && distinct.len() >= 3 {
            return state;
        }
        game.play_tick();
    }
}

#[test]
fn the_code_parses_with_defaults_and_parameters_and_leaves_the_other_codes_alone() {
    let PlayerCode::KX { params } = parse_player_code("kx3").unwrap() else { panic!("kx3 is not KX") };
    assert_eq!(params, PlayoutParams::new(3));
    assert_eq!((params.rollouts, params.cap, params.z, params.knowledge, params.budget_ms, params.trace),
               (16, 12, 2.0, Knowledge::Realistic, 0, false));
    let PlayerCode::KX { params } = parse_player_code("KX3_r8_c5_z1.5_lab_t30_trace").unwrap() else { panic!() };
    assert_eq!((params.depth, params.rollouts, params.cap, params.z, params.knowledge, params.budget_ms, params.trace),
               (3, 8, 5, 1.5, Knowledge::Lab, 30_000, true));
    for bad in ["kx", "kx3_q1", "kx3_r0", "kx3_c1", "kxx3", "kx3_"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
    assert_eq!(parse_player_code("km3").unwrap(), PlayerCode::KM { max_depth: 3 });
    assert_eq!(parse_player_code("k3").unwrap(), PlayerCode::K { max_depth: 3 });
}

/// Mega Absol ex with Darkness Claw paid for, against the opponent's only Pokémon, Abra: the attack knocks it out and
/// wins. With the noise threshold at 0 the pilot must find it: every play-out after the attack is a win.
#[test]
fn an_immediate_win_is_taken() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1151MegaAbsolEx).with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        vec![PlayedCard::from_id(CardId::A1115Abra)],
    );
    let mut state = game.get_state_clone();
    state.move_generation_stack.clear();
    game.set_state(state);
    let state = game.get_state_clone();
    let actions = state.generate_possible_actions().1;
    assert!(actions.len() >= 2, "the position offers alternatives: {actions:?}");
    for knowledge in [Knowledge::Lab, Knowledge::Realistic] {
        let mut p = pilot(small(knowledge, 0.0));
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let report = p.evaluate(&mut StdRng::seed_from_u64(5), &observation, &actions);
        let chosen = &report.candidates[report.chosen].action;
        assert!(matches!(&chosen.action, SimpleAction::Attack(a) if a.title == "Darkness Claw"), "{knowledge:?}: chose {chosen:?}");
        assert_eq!(report.candidates[report.chosen].score, 1.0, "{knowledge:?}: every play-out after the knockout is a win");
    }
}

/// With an unreachable noise threshold the pilot always keeps km3's move; with the threshold at 0 it keeps the move with
/// the best play-out score (km3's on a tie).
#[test]
fn within_the_noise_km3s_move_is_kept() {
    for seed in [3u64, 11] {
        let state = midgame(seed);
        let actions = state.generate_possible_actions().1;
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let km3 = km3_choice(&state, 0, 9);
        let report = pilot(small(Knowledge::Lab, 1e9)).evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
        assert_eq!(report.candidates[report.km3].action, km3, "seed {seed}: the report's km3 move is km3's");
        assert_eq!(report.chosen, report.km3, "seed {seed}: kept km3's move: {}", report.reason);
        let open = pilot(small(Knowledge::Lab, 0.0)).evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
        let best = open.candidates.iter().map(|c| c.score).fold(f64::MIN, f64::max);
        assert_eq!(open.candidates[open.chosen].score, best, "seed {seed}: with no threshold, the best play-out score");
        if open.candidates[open.km3].score == best {
            assert_eq!(open.chosen, open.km3, "seed {seed}: a tie keeps km3's move");
        }
    }
}

/// The candidate cap: km3's move is always kept, and every dropped move is named with its reason.
#[test]
fn a_capped_candidate_list_keeps_km3s_move_and_names_the_drops() {
    let state = midgame(3);
    let actions = state.generate_possible_actions().1;
    let distinct: std::collections::BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let report = pilot(PlayoutParams { cap: 2, ..small(Knowledge::Lab, 2.0) })
        .evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
    assert_eq!(report.candidates.len(), 2);
    assert_eq!(report.candidates[report.km3].action, km3_choice(&state, 0, 9));
    assert_eq!(report.candidates.len() + report.dropped.len(), distinct.len(), "every distinct move is a candidate or a drop");
    assert!(report.dropped.iter().all(|d| !d.reason.is_empty()));
}

/// Swap a card between the opponent's hand and deck, and reverse both decks: the hidden cards change, the observation
/// doesn't.
fn other_hidden_cards(state: &State) -> State {
    let mut other = state.clone();
    let opponent = 1;
    if let (Some(h), Some(d)) = (other.hands[opponent].first().cloned(), other.decks[opponent].cards.iter().position(|c| {
        Some(c) != other.hands[opponent].first()
    })) {
        let deck_card = other.decks[opponent].cards[d].clone();
        other.decks[opponent].cards[d] = h;
        other.hands[opponent][0] = deck_card;
    }
    other.decks[0].cards.reverse();
    other.decks[1].cards.reverse();
    other
}

#[test]
fn the_choice_cannot_depend_on_the_opponents_hand_or_either_decks_order() {
    let state = midgame(3);
    let other = other_hidden_cards(&state);
    assert!(other.hands[1] != state.hands[1] || other.decks[1].cards != state.decks[1].cards, "the hidden cards differ");
    let (obs_a, obs_b) = (
        PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default()),
        PlayerObservation::from_state(&other, 0, &RevealedKnowledge::default()),
    );
    assert_eq!(obs_a, obs_b, "the same observation");
    let actions = state.generate_possible_actions().1;
    for knowledge in [Knowledge::Lab, Knowledge::Realistic] {
        let a = pilot(small(knowledge, 2.0)).evaluate(&mut StdRng::seed_from_u64(21), &obs_a, &actions);
        let b = pilot(small(knowledge, 2.0)).evaluate(&mut StdRng::seed_from_u64(21), &obs_b, &actions);
        let scores = |r: &deckgym::players::playout_player::DecisionReport| {
            r.candidates.iter().map(|c| (format!("{:?}", c.action), c.score, c.diff)).collect::<Vec<_>>()
        };
        assert_eq!(scores(&a), scores(&b), "{knowledge:?}: the same play-out results");
        assert_eq!(a.chosen, b.chosen, "{knowledge:?}: the same choice");
        // Through Game: the game hands the pilot only its observation.
        let code = PlayerCode::KX { params: small(knowledge, 2.0) };
        let (deck_a, deck_b) = load_test_decks();
        let play = |s: &State| {
            let players = create_players(deck_a.clone(), deck_b.clone(), vec![code.clone(), parse_player_code("km3").unwrap()]);
            let mut game = Game::from_state(s.clone(), players, 77);
            game.play_tick()
        };
        assert_eq!(play(&state), play(&other), "{knowledge:?}: the same move through Game");
    }
}

#[test]
fn the_same_seeds_give_the_same_moves() {
    let state = midgame(11);
    let code = PlayerCode::KX { params: small(Knowledge::Realistic, 2.0) };
    let run = || {
        let (deck_a, deck_b) = load_test_decks();
        let players = create_players(deck_a, deck_b, vec![code.clone(), parse_player_code("km3").unwrap()]);
        let mut game = Game::from_state(state.clone(), players, 1234);
        let mut moves = Vec::new();
        while moves.len() < 12 && !game.is_game_over() {
            moves.push(format!("{:?}", game.play_tick()));
        }
        moves
    };
    assert_eq!(run(), run());
}

/// A whole short game through `Game::new` (setup included), to the end, without a panic.
#[test]
fn a_whole_game_plays_to_the_end() {
    let (deck_a, deck_b) = load_test_decks();
    let code = PlayerCode::KX { params: PlayoutParams { rollouts: 2, cap: 3, ..PlayoutParams::new(3) } };
    let mut game = Game::new(create_players(deck_a, deck_b, vec![code, parse_player_code("km3").unwrap()]), 31);
    while !game.is_game_over() {
        game.play_tick();
    }
}
