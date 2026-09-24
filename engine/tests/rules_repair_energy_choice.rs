use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    observation::{PlayerObservation, RevealedKnowledge},
    players::{ExpectiMiniMaxPlayer, Player},
    test_support::{attack_action, get_initialized_game, get_test_game_with_board},
    Deck,
};
use rand::{rngs::StdRng, SeedableRng};

fn apply_exact(state: &mut deckgym::State, action: &Action) {
    assert!(state.generate_possible_actions().1.contains(action));
    let (probabilities, mut mutations) = try_forecast_action(state, action).unwrap().into_branches();
    assert_eq!(probabilities, vec![1.0], "a player payment is not random");
    mutations.remove(0)(&mut StdRng::seed_from_u64(19), state, action);
}

#[test]
fn scorching_interruption_offers_distinct_payments_after_damage_before_ko() {
    let defender = PlayedCard::new(
        get_card_by_enum(CardId::A1033Charmander), 0, 50, vec![], false, vec![],
    );
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a054GougingFire)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Lightning])],
        vec![defender, PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    apply_exact(&mut state, &Action {
        actor: 0, action: attack_action(CardId::B3a054GougingFire, 0), is_stack: false,
    });
    assert_eq!(state.get_active(1).get_remaining_hp(), 0);
    assert_eq!(state.points[0], 0, "KO is deferred until the Energy choice and retaliation");
    assert_eq!(state.get_active(0).attached_energy.len(), 3);
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 2, "F/F/L gives FF or FL, not three physical-copy choices");
    let visible = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let (_, visible_choices) = visible.visible_state().generate_possible_actions();
    assert_eq!(choices.len(), visible_choices.len());
    assert!(choices.iter().all(|choice| visible_choices.contains(choice)),
        "the chooser sees its own exact legal payments");
    for choice in &choices {
        let payload = serde_json::to_value(&choice.action).unwrap();
        assert!(payload.get("ChooseAttackEnergyDiscard").is_some());
        let mut branch = state.clone();
        apply_exact(&mut branch, choice);
        assert_eq!(branch.get_active(0).attached_energy.len(), 1);
        assert_eq!(branch.points[0], 0);
    }
    let keep_fire = choices.iter().find(|choice| matches!(
        &choice.action, SimpleAction::ChooseAttackEnergyDiscard { energies, .. }
            if energies == &vec![EnergyType::Fire, EnergyType::Lightning]
    )).unwrap();
    apply_exact(&mut state, keep_fire);
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.discard_energies[0].len(), 2);
    let (_, reaction) = state.generate_possible_actions();
    assert!(matches!(reaction[0].action, SimpleAction::ResolveAttackRetaliation { .. }));
    apply_exact(&mut state, &reaction[0]);
    assert_eq!(state.points[0], 1);
}

#[test]
fn sweeping_billow_choice_is_visible_and_search_values_retained_energy() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a053WalkingWake)
            .with_energy(vec![EnergyType::Fire, EnergyType::Water])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx),
             PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    apply_exact(&mut state, &Action {
        actor: 0, action: attack_action(CardId::B3a053WalkingWake, 0), is_stack: false,
    });
    assert_eq!(state.get_active(1).get_remaining_hp(), 120);
    assert_eq!(state.in_play_pokemon[1][1].as_ref().unwrap().get_remaining_hp(), 160);
    assert_eq!(state.get_active(0).attached_energy.len(), 2);
    let (_, choices) = state.generate_possible_actions();
    assert_eq!(choices.len(), 2);
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let visible_choices = observation.visible_state().generate_possible_actions().1;
    assert_eq!(choices.len(), visible_choices.len());
    assert!(choices.iter().all(|choice| visible_choices.contains(choice)));
    let mut bot = ExpectiMiniMaxPlayer {
        deck: Deck::default(), max_depth: 1, write_debug_trees: false,
        value_function: Box::new(|position, player| {
            if position.get_active(player).attached_energy.contains(&EnergyType::Fire) { 100.0 } else { 0.0 }
        }),
        opponent_ply: 0, consistent_horizon: false, soft_opponent: false,
    };
    let chosen = bot.decision_fn(&mut StdRng::seed_from_u64(7), &observation, &choices);
    assert!(matches!(&chosen.action,
        SimpleAction::ChooseAttackEnergyDiscard { energies, .. } if energies == &vec![EnergyType::Water]
    ), "search should prefer retaining Fire: {chosen:?}");
    apply_exact(&mut state, &chosen);
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.discard_energies[0], vec![EnergyType::Water]);
}

#[test]
fn reduced_and_full_retreat_costs_offer_exact_distinct_payments() {
    for (discounted, expected_count) in [(true, 2), (false, 2)] {
        let mut game = get_initialized_game(42);
        let mut state = game.get_state_clone();
        let mut active = PlayedCard::from_id(CardId::B3a054GougingFire).with_energy(
            if discounted { vec![EnergyType::Fire, EnergyType::Lightning] }
            else { vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Lightning] }
        );
        if discounted { active = active.with_tool(get_card_by_enum(CardId::B3b064SmallBalloon)); }
        state.set_board(vec![active, PlayedCard::from_id(CardId::B3a053WalkingWake)],
            vec![PlayedCard::from_id(CardId::A1033Charmander)]);
        state.current_player = 0;
        state.turn_count = 3;
        game.set_state(state.clone());
        let retreat = Action { actor: 0, action: SimpleAction::Retreat(1), is_stack: false };
        assert!(state.generate_possible_actions().1.contains(&retreat));
        apply_exact(&mut state, &retreat);
        assert_eq!(state.get_active(0).get_name(), "Gouging Fire");
        let (_, choices) = state.generate_possible_actions();
        assert_eq!(choices.len(), expected_count);
        assert!(choices.iter().all(|choice| choice.is_stack));
        for choice in &choices {
            let payload = serde_json::to_value(&choice.action).unwrap();
            assert_eq!(payload["ChooseRetreatEnergy"]["to_in_play_idx"], 1);
            let mut branch = state.clone();
            apply_exact(&mut branch, choice);
            assert_eq!(branch.get_active(0).get_name(), "Walking Wake");
            assert!(!branch.generate_possible_actions().1.iter().any(|candidate|
                matches!(candidate.action, SimpleAction::Retreat(_))));
            assert_eq!(branch.in_play_pokemon[0][1].as_ref().unwrap().attached_energy.len(), 1);
        }
        let discard = if discounted { vec![EnergyType::Fire] }
            else { vec![EnergyType::Fire, EnergyType::Lightning] };
        let selected = choices.iter().find(|choice| matches!(
            &choice.action, SimpleAction::ChooseRetreatEnergy { energies, .. } if energies == &discard
        )).unwrap();
        apply_exact(&mut state, selected);
        assert_eq!(state.in_play_pokemon[0][1].as_ref().unwrap().attached_energy,
            vec![if discounted { EnergyType::Lightning } else { EnergyType::Fire }]);
    }
}
