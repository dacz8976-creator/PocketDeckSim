use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction, UnpricedForecastKind},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, TrainerCard},
    observation::{PlayerObservation, RevealedKnowledge, INFORMATION_MODEL},
    players::Player,
    state::MistySourceRoute,
    test_support::get_initialized_game,
    Game, State,
};
use rand::SeedableRng;

fn trainer(id: CardId) -> TrainerCard {
    get_card_by_enum(id).as_trainer()
}

fn play(id: CardId) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer(id),
        },
        is_stack: false,
    }
}

fn use_portrait() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    }
}

fn target(index: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::ChooseMistyTarget { in_play_idx: index },
        is_stack: true,
    }
}

fn reroll(index: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollTrainerCoins {
            luxury_coin_in_play_idx: index,
        },
        is_stack: true,
    }
}

fn setup(seed: u64, portrait: bool, gholdengo: bool) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    let mut own = if portrait {
        vec![
            PlayedCard::from_id(CardId::B2130Smeargle),
            PlayedCard::from_id(CardId::A1053Squirtle),
            PlayedCard::from_id(CardId::A1057Psyduck),
        ]
    } else {
        vec![
            PlayedCard::from_id(CardId::A1053Squirtle),
            PlayedCard::from_id(CardId::A1057Psyduck),
        ]
    };
    if gholdengo {
        own.push(PlayedCard::from_id(CardId::B4a051Gholdengo));
    }
    state.set_board(own, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    state.hands = [vec![], vec![]];
    state.decks[0].cards.clear();
    state.decks[1].cards.clear();
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn water_energy_count(state: &State, index: usize) -> usize {
    state.in_play_pokemon[0][index]
        .as_ref()
        .unwrap()
        .attached_energy
        .iter()
        .filter(|energy| **energy == EnergyType::Water)
        .count()
}

fn find_legal(game: &Game<'static>, wanted: impl Fn(&SimpleAction) -> bool) -> Action {
    game.get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| wanted(&action.action))
        .expect("expected legal action")
}

#[test]
fn target_is_publicly_chosen_before_rng_and_fixed_through_luxury_reroll() {
    for seed in 0..64 {
        let mut game = setup(seed, false, true);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
        game.set_state(state);

        game.apply_action(&play(CardId::A1220Misty));
        let staged = game.get_state_clone();
        assert!(staged.pending_misty_target_choice.is_some());
        assert!(staged.pending_trainer_coin_choice.is_none());
        assert_eq!(water_energy_count(&staged, 0), 0);
        assert_eq!(water_energy_count(&staged, 1), 0);
        assert_eq!(staged.discard_piles[0].len(), 1, "Play prefix runs once");

        game.apply_action(&target(1));
        let paused = game.get_state_clone();
        let pending = paused.pending_trainer_coin_choice.as_ref().unwrap();
        assert_eq!(pending.misty_target_in_play_idx, Some(1));
        assert_eq!(water_energy_count(&paused, 0), 0);
        assert_eq!(water_energy_count(&paused, 1), 0);
        assert_eq!(paused.discard_piles[0].len(), 1);
        let replacement_source = pending.luxury_coin_in_play_idx;
        if seed == 0 {
            let round_trip: State =
                serde_json::from_str(&serde_json::to_string(&paused).unwrap()).unwrap();
            let adopted = Game::from_state(round_trip, Vec::<Box<dyn Player>>::new(), 0);
            assert_eq!(
                adopted
                    .get_state_clone()
                    .pending_trainer_coin_choice
                    .unwrap()
                    .misty_target_in_play_idx,
                Some(1)
            );
        }

        game.apply_action(&reroll(replacement_source));
        let committed = game.get_state_clone();
        let replacement_heads = game
            .luxury_coin_resolution_history()
            .last()
            .unwrap()
            .replacement_faces
            .as_ref()
            .unwrap()
            .iter()
            .filter(|face| **face)
            .count();
        assert!(committed.pending_misty_target_choice.is_none());
        assert!(committed.pending_trainer_coin_choice.is_none());
        assert_eq!(water_energy_count(&committed, 0), 0);
        assert_eq!(water_energy_count(&committed, 1), replacement_heads);
        assert_eq!(
            committed.discard_piles[0].len(),
            1,
            "Play cost is not repeated"
        );
    }
}

#[test]
fn direct_target_commit_samples_only_after_choice_and_keeps_the_selected_slot() {
    let mut saw_heads = false;
    for seed in 0..64 {
        let mut game = setup(seed, false, false);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
        game.set_state(state);
        game.apply_action(&play(CardId::A1220Misty));
        let before = game.get_state_clone();
        assert_eq!(water_energy_count(&before, 0), 0);
        assert_eq!(water_energy_count(&before, 1), 0);
        game.apply_action(&target(1));
        let after = game.get_state_clone();
        assert_eq!(water_energy_count(&after, 0), 0);
        saw_heads |= water_energy_count(&after, 1) > 0;
    }
    assert!(
        saw_heads,
        "physical post-target batches retain heads outcomes"
    );
}

#[test]
fn unoffered_target_is_rejected_before_coin_rng_is_consumed() {
    let seed = 91;
    let mut rejected = setup(seed, false, false);
    let mut state = rejected.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
    rejected.set_state(state.clone());
    rejected.apply_action(&play(CardId::A1220Misty));

    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        rejected.apply_action(&target(3));
    }));
    assert!(result.is_err());
    rejected.apply_action(&target(1));

    let mut control = setup(seed, false, false);
    control.set_state(state);
    control.apply_action(&play(CardId::A1220Misty));
    control.apply_action(&target(1));
    assert_eq!(
        water_energy_count(&rejected.get_state_clone(), 1),
        water_energy_count(&control.get_state_clone(), 1),
        "a rejected target must not advance the gameplay RNG"
    );
}

#[test]
fn target_phase_is_serialized_and_copied_source_is_redacted_from_opponent() {
    let mut game = setup(7, false, false);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state);
    game.apply_action(&play(CardId::A3b069Penny));
    let referee = game.get_state_clone();
    let pending = referee.pending_misty_target_choice.as_ref().unwrap();
    assert!(matches!(
        pending.route,
        Some(MistySourceRoute::Penny { .. })
    ));
    let restored: State = serde_json::from_str(&serde_json::to_string(&referee).unwrap()).unwrap();
    assert_eq!(
        restored.pending_misty_target_choice,
        referee.pending_misty_target_choice
    );

    let actor = PlayerObservation::from_state(&referee, 0, &RevealedKnowledge::default());
    let opponent = PlayerObservation::from_state(&referee, 1, &RevealedKnowledge::default());
    assert_eq!(actor.information_model, "closed-counts-unpriced-v7");
    assert_eq!(INFORMATION_MODEL, "closed-counts-unpriced-v7");
    assert!(actor
        .visible_state()
        .pending_misty_target_choice
        .as_ref()
        .unwrap()
        .route
        .is_some());
    assert!(opponent
        .visible_state()
        .pending_misty_target_choice
        .as_ref()
        .unwrap()
        .route
        .is_none());
    let opponent_pending = serde_json::to_value(
        opponent
            .visible_state()
            .pending_misty_target_choice
            .as_ref()
            .unwrap(),
    )
    .unwrap();
    assert!(opponent_pending.get("route").unwrap().is_null());
}

#[test]
fn adopted_redacted_or_malformed_target_state_cannot_resume_private_resolution() {
    let mut game = setup(11, false, false);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state);
    game.apply_action(&play(CardId::A1220Misty));
    let valid = game.get_state_clone();
    assert!(
        Game::from_state(valid.clone(), Vec::<Box<dyn Player>>::new(), 1)
            .get_state_clone()
            .pending_misty_target_choice
            .is_some()
    );

    let redacted = PlayerObservation::from_state(&valid, 1, &RevealedKnowledge::default())
        .search_state(&mut rand::rngs::StdRng::seed_from_u64(2));
    let adopted = Game::from_state(redacted, Vec::<Box<dyn Player>>::new(), 2).get_state_clone();
    assert!(adopted.pending_misty_target_choice.is_none());
    assert!(!adopted
        .move_generation_stack
        .last()
        .is_some_and(|(_, choices)| {
            choices
                .iter()
                .all(|choice| matches!(choice, SimpleAction::ChooseMistyTarget { .. }))
        }));
}

#[test]
fn target_action_is_the_exact_search_boundary_after_a_finite_mandatory_phase() {
    let mut game = setup(13, false, true);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state.clone());
    let initial = try_forecast_action(&state, &play(CardId::A1220Misty)).unwrap();
    let (_, mut mutations) = initial.into_branches();
    assert_eq!(mutations.len(), 1);
    let mut rng = rand::rngs::StdRng::seed_from_u64(3);
    mutations.remove(0)(&mut rng, &mut state, &play(CardId::A1220Misty));
    let choice = state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::ChooseMistyTarget { .. }))
        .unwrap();
    let error = match try_forecast_action(&state, &choice) {
        Ok(_) => panic!("the public geometric batch must remain unpriced"),
        Err(error) => error,
    };
    assert!(matches!(
        error.kind,
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));
}

#[test]
fn will_routes_are_legal_for_portrait_misty_and_portrait_will_then_direct_misty() {
    for seed in 0..32 {
        let mut first = setup(seed, true, false);
        let mut state = first.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
        state.hands[1] = vec![get_card_by_enum(CardId::A1220Misty)];
        first.set_state(state);
        let will = find_legal(
            &first,
            |action| matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Will"),
        );
        first.apply_action(&will);
        let portrait = find_legal(&first, |action| {
            matches!(action, SimpleAction::UseAbility { in_play_idx: 0 })
        });
        first.apply_action(&portrait);
        first.apply_action(&target(1));
        assert!(water_energy_count(&first.get_state_clone(), 1) >= 1);

        let mut second = setup(seed, true, false);
        let mut state = second.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
        state.hands[1] = vec![get_card_by_enum(CardId::A4156Will)];
        second.set_state(state);
        let portrait = find_legal(&second, |action| {
            matches!(action, SimpleAction::UseAbility { in_play_idx: 0 })
        });
        second.apply_action(&portrait);
        let misty = find_legal(
            &second,
            |action| matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Misty"),
        );
        second.apply_action(&misty);
        second.apply_action(&target(1));
        assert!(water_energy_count(&second.get_state_clone(), 1) >= 1);
    }
}

#[test]
fn misty_printings_are_private_to_actor_but_have_identical_opponent_target_payloads() {
    let mut opponent_payloads = Vec::new();
    let mut actor_sources = Vec::new();
    for source in [CardId::A1220Misty, CardId::A1267Misty] {
        let mut game = setup(29, false, false);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
        state.decks[1].cards = vec![get_card_by_enum(source)];
        game.set_state(state);
        game.apply_action(&play(CardId::A3b069Penny));
        let referee = game.get_state_clone();
        let actor = PlayerObservation::from_state(&referee, 0, &RevealedKnowledge::default());
        let opponent = PlayerObservation::from_state(&referee, 1, &RevealedKnowledge::default());
        actor_sources.push(
            actor
                .visible_state()
                .pending_misty_target_choice
                .as_ref()
                .unwrap()
                .route
                .as_ref()
                .unwrap()
                .effect_trainer()
                .id
                .clone(),
        );
        opponent_payloads.push(
            serde_json::to_value(
                opponent
                    .visible_state()
                    .pending_misty_target_choice
                    .as_ref()
                    .unwrap(),
            )
            .unwrap(),
        );
    }
    assert_ne!(actor_sources[0], actor_sources[1]);
    assert_eq!(opponent_payloads[0], opponent_payloads[1]);
    let text = serde_json::to_string(&opponent_payloads).unwrap();
    assert!(!text.contains("A1 220"));
    assert!(!text.contains("A1 267"));
}
