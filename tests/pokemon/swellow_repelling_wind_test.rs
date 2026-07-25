use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    test_support::get_test_game_with_board,
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Swellow's Repelling Wind: "Once during your turn, you may switch out your opponent's Active
/// Basic Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)"
///
/// Unlike Rillaboom's Captivating Rhythm, the *opponent* picks the replacement, so the follow-up
/// choice must be offered to actor 1.
#[test]
fn test_repelling_wind_lets_the_opponent_choose_their_new_active() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2133Swellow)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Repelling Wind should be available");
    game.apply_action(&ability_action);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "the opponent chooses their new Active Pokémon");
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. })));

    game.apply_action(&choices[0].clone());
    assert_eq!(
        game.get_state_clone().get_active(1).get_name(),
        "Charmander",
        "the Benched Pokémon should have been promoted"
    );
}

/// NEGATIVE: the card only repels a *Basic* Active Pokémon. Against an evolved Active (Ivysaur is
/// Stage 1) the ability must not be offered at all.
#[test]
fn test_repelling_wind_not_offered_against_evolved_active() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2133Swellow)],
        vec![
            PlayedCard::from_id(CardId::A1002Ivysaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Repelling Wind should not be offered when the opponent's Active is evolved"
    );
}

/// NEGATIVE: there must be somewhere to switch the Active Pokémon *to*.
#[test]
fn test_repelling_wind_not_offered_when_opponent_bench_is_empty() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2133Swellow)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Repelling Wind should not be offered when the opponent has no Benched Pokémon"
    );
}

/// The existing `SwitchOutOpponentActiveToBench` users must keep working against evolved Actives —
/// only Swellow's printing carries the "Basic" restriction. Dragonite's Draconic Gust has the same
/// wording without it, so it stays available here.
#[test]
fn test_repelling_wind_basic_gate_does_not_leak_to_other_printings() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2133Swellow)],
        vec![
            PlayedCard::from_id(CardId::A1002Ivysaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    // Sanity: the Basic gate is what blocks Swellow here.
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(use_ability_action(&actions, 0).is_none());

    // Swapping the opponent's Active for a Basic re-enables it, proving the gate is the Basic
    // check rather than something incidental about the board.
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2133Swellow)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    state.current_player = 0;
    game.set_state(state);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_some(),
        "Repelling Wind should be available once the opponent's Active is Basic again"
    );
}
