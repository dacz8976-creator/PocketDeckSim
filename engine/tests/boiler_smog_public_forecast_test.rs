use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    data_exporter::ExportedDataPoint,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    observation::{hidden_continuation_reason, PlayerObservation, RevealedKnowledge},
    players::{public_clock_effect_value_function, ExpectiMiniMaxPlayer, Player},
    state::GameOutcome,
    test_support::get_initialized_game_with_board,
    Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

const WEEZING_PRINTS: [CardId; 3] = [
    CardId::B4a043TeamRocketsWeezingEx,
    CardId::B4a083TeamRocketsWeezingEx,
    CardId::B4a092TeamRocketsWeezingEx,
];

fn card(id: CardId) -> Card {
    get_card_by_enum(id)
}

fn prepared_game(evolution: CardId, opponent: PlayedCard) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        7001,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B4a042TeamRocketsKoffing)],
        vec![opponent],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![card(evolution)];
    state.hands[1] = vec![card(CardId::PA001Potion), card(CardId::PA005PokeBall)];
    state.decks[0].cards = vec![card(CardId::A1033Charmander)];
    state.decks[1].cards = vec![card(CardId::A1001Bulbasaur)];
    state.points = [0, 0];
    state.winner = None;
    state.move_generation_stack.clear();
    game.set_state(state);
    game
}

fn legally_evolve(game: &mut Game<'static>, evolution: CardId) -> (Action, Action) {
    let state = game.get_state_clone();
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    let evolve = actions
        .into_iter()
        .find(|action| {
            matches!(
                &action.action,
                SimpleAction::Evolve {
                    evolution: candidate,
                    in_play_idx: 0,
                    from_deck: false,
                } if candidate.get_id() == card(evolution).get_id()
            )
        })
        .expect("the hand evolution must be generated as a legal action");
    assert!(!evolve.is_stack);
    game.apply_action(&evolve);

    let state = game.get_state_clone();
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 2);
    let use_ability = choices
        .iter()
        .find(|action| {
            action.is_stack
                && matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 })
        })
        .cloned()
        .expect("Boiler Smog must be offered after the hand evolution");
    let noop = choices
        .iter()
        .find(|action| action.is_stack && matches!(action.action, SimpleAction::Noop))
        .cloned()
        .expect("the on-evolve ability must remain optional");
    (use_ability, noop)
}

fn apply_forecast(state: &State, action: &Action, seed: u64) -> State {
    let (probabilities, mut mutations) = try_forecast_action(state, action)
        .expect("action should have an exact forecast")
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    let mut result = state.clone();
    mutations.pop().unwrap()(&mut StdRng::seed_from_u64(seed), &mut result, action);
    result
}

fn forecast_branches(state: &State, action: &Action, seed: u64) -> Vec<(f64, State)> {
    let (probabilities, mutations) = try_forecast_action(state, action)
        .expect("action should have an exact forecast")
        .into_branches();
    assert_eq!(probabilities.len(), mutations.len());
    assert!((probabilities.iter().sum::<f64>() - 1.0).abs() < 1e-12);
    probabilities
        .into_iter()
        .zip(mutations)
        .map(|(probability, mutation)| {
            let mut result = state.clone();
            mutation(
                &mut StdRng::seed_from_u64(seed),
                &mut result,
                action,
            );
            (probability, result)
        })
        .collect()
}

fn k3(state: &State) -> ExpectiMiniMaxPlayer {
    ExpectiMiniMaxPlayer {
        deck: state.decks[state.current_player].clone(),
        max_depth: 3,
        write_debug_trees: false,
        value_function: Box::new(public_clock_effect_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    }
}

#[test]
fn legal_boiler_smog_continuation_is_public_deterministic_for_all_prints() {
    for evolution in WEEZING_PRINTS {
        let mut game = prepared_game(evolution, PlayedCard::from_id(CardId::A1001Bulbasaur));
        let (use_ability, _) = legally_evolve(&mut game, evolution);
        let state = game.get_state_clone();
        let observation = game.observation(0);
        assert!(observation.visible_state().hands[1]
            .iter()
            .all(|candidate| *candidate == Card::Unknown));
        assert!(observation.visible_state().decks[1].cards
            .iter()
            .all(|candidate| *candidate == Card::Unknown));
        assert_eq!(
            hidden_continuation_reason(observation.visible_state(), &use_ability),
            None
        );

        for seed in [0, 1] {
            let result = apply_forecast(observation.visible_state(), &use_ability, seed);
            assert!(result.get_active(1).is_poisoned());
            assert!(result.get_active(1).is_burned());
        }
        assert!(!state.get_active(1).is_poisoned());
        assert!(!state.get_active(1).is_burned());
    }
}

#[test]
fn boiler_smog_public_forecast_keeps_visible_status_immunity() {
    let mut game = prepared_game(
        CardId::B4a043TeamRocketsWeezingEx,
        PlayedCard::from_id(CardId::A2a071ArceusEx).with_remaining_hp(10),
    );
    let mut state = game.get_state_clone();
    state.points = [2, 0];
    game.set_state(state);
    let (use_ability, noop) = legally_evolve(&mut game, CardId::B4a043TeamRocketsWeezingEx);
    let observation = game.observation(0);
    assert_eq!(hidden_continuation_reason(observation.visible_state(), &use_ability), None);
    let used = apply_forecast(observation.visible_state(), &use_ability, 17);
    let declined = apply_forecast(observation.visible_state(), &noop, 17);
    for state in [&used, &declined] {
        assert!(!state.get_active(1).is_poisoned());
        assert!(!state.get_active(1).is_burned());
        assert_eq!(state.winner, None);
        let end = state
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|action| matches!(action.action, SimpleAction::EndTurn))
            .unwrap();
        let settled = forecast_branches(state, &end, 17);
        assert!(settled.iter().all(|(_, result)| result.points[0] == 2));
        assert!(settled.iter().all(|(_, result)| result.winner.is_none()));
    }
}

#[test]
fn boiler_smog_is_invariant_to_same_count_private_opponent_hands() {
    let mut game = prepared_game(
        CardId::B4a043TeamRocketsWeezingEx,
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    let (use_ability, _) = legally_evolve(&mut game, CardId::B4a043TeamRocketsWeezingEx);
    let original = game.get_state_clone();
    let mut alternate = original.clone();
    alternate.hands[1] = vec![card(CardId::A1033Charmander), card(CardId::A1033Charmander)];
    let views = [
        PlayerObservation::from_state(&original, 0, &RevealedKnowledge::default()),
        PlayerObservation::from_state(&alternate, 0, &RevealedKnowledge::default()),
    ];
    assert_eq!(views[0], views[1]);
    let results = views.map(|view| {
        assert_eq!(hidden_continuation_reason(view.visible_state(), &use_ability), None);
        apply_forecast(view.visible_state(), &use_ability, 29)
    });
    assert_eq!(results[0], results[1]);
    assert!(results[0].get_active(1).is_poisoned());
    assert!(results[0].get_active(1).is_burned());
}

#[test]
fn true_opponent_hand_identity_effects_remain_unpriced() {
    let mut spy_game = get_initialized_game_with_board(
        7002,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B4a062TeamRocketsKecleon)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut spy_state = spy_game.get_state_clone();
    spy_state.hands[0].clear();
    spy_state.hands[1] = vec![card(CardId::PA001Potion), card(CardId::PA005PokeBall)];
    spy_state.decks[1].cards = vec![card(CardId::A1033Charmander)];
    spy_game.set_state(spy_state);
    let (_, spy_actions) = spy_game.get_state_clone().generate_possible_actions();
    let spy = spy_actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 }))
        .expect("Spy Ops must be a generated action");
    assert_eq!(
        hidden_continuation_reason(spy_game.observation(0).visible_state(), &spy),
        Some("effect or choice depends on unrevealed opponent cards")
    );

    let boss = card(CardId::B4a071TeamRocketsBoss);
    let mut boss_state = spy_game.get_state_clone();
    boss_state.hands[0] = vec![boss.clone()];
    boss_state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
    boss_state.move_generation_stack.clear();
    spy_game.set_state(boss_state);
    let (_, boss_actions) = spy_game.get_state_clone().generate_possible_actions();
    let play_boss = boss_actions
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == boss.get_id())
        })
        .expect("Team Rocket's Boss must be a generated action");
    assert_eq!(
        hidden_continuation_reason(spy_game.observation(0).visible_state(), &play_boss),
        Some("effect or choice depends on unrevealed opponent cards")
    );
}

#[test]
fn saved_k3_root_prices_and_selects_boiler_smog_without_private_hand_dependence() {
    let row: ExportedDataPoint =
        serde_json::from_str(include_str!("fixtures/boiler_smog_ply23.json")).unwrap();
    assert_eq!(row.actor, 1);
    assert_eq!(row.information_model.as_deref(), Some("closed-counts-unpriced-v6"));
    assert!(matches!(row.chosen_action.action, SimpleAction::Noop));
    let use_ability = row
        .playable_actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 }))
        .cloned()
        .expect("saved root must offer Boiler Smog");
    assert!(row.unpriced_branches.iter().any(|branch| {
        branch.action == use_ability
            && branch.reason == "effect or choice depends on unrevealed opponent cards"
    }));
    let seed = row.decision_randomness.as_ref().unwrap().search_seed;
    assert_eq!(seed, 12_463_439_594_353_392_692);

    let mut alternate = row.state.clone();
    let count = alternate.hands[0].len();
    alternate.hands[0] = (0..count)
        .map(|index| card(if index % 2 == 0 { CardId::PA001Potion } else { CardId::PA005PokeBall }))
        .collect();
    let views = [
        PlayerObservation::from_state(&row.state, row.actor, &Default::default()),
        PlayerObservation::from_state(&alternate, row.actor, &Default::default()),
    ];
    assert_eq!(views[0], views[1]);
    for view in views {
        assert_eq!(hidden_continuation_reason(view.visible_state(), &use_ability), None);
        let chosen = k3(&row.state).decision_fn(
            &mut StdRng::seed_from_u64(seed),
            &view,
            &row.playable_actions,
        );
        assert_eq!(chosen, use_ability);
    }
}

#[test]
fn boiler_smog_is_chosen_when_its_public_checkup_damage_wins() {
    let mut game = prepared_game(
        CardId::B4a043TeamRocketsWeezingEx,
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10),
    );
    let mut state = game.get_state_clone();
    state.points = [2, 0];
    game.set_state(state);
    let (use_ability, noop) = legally_evolve(&mut game, CardId::B4a043TeamRocketsWeezingEx);
    let state = game.get_state_clone();
    let view = game.observation(0);
    for seed in [0, 1, 29, 97] {
        let chosen = k3(&state).decision_fn(
            &mut StdRng::seed_from_u64(seed),
            &view,
            &[noop.clone(), use_ability.clone()],
        );
        assert_eq!(chosen, use_ability, "search seed {seed}");
    }

    let after_use = apply_forecast(view.visible_state(), &use_ability, 17);
    let end = after_use
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::EndTurn))
        .expect("EndTurn must remain available after the optional ability");
    let won = forecast_branches(&after_use, &end, 17);
    assert_eq!(won.len(), 2, "Burn recovery remains a real public coin branch");
    assert!(won.iter().all(|(_, result)| result.points[0] == 3));
    assert!(won
        .iter()
        .all(|(_, result)| result.winner == Some(GameOutcome::Win(0))));

    let after_noop = apply_forecast(view.visible_state(), &noop, 17);
    let end = after_noop
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::EndTurn))
        .unwrap();
    let not_won = forecast_branches(&after_noop, &end, 17);
    assert!(not_won.iter().all(|(_, result)| result.points[0] == 2));
    assert!(not_won.iter().all(|(_, result)| result.winner.is_none()));
}
