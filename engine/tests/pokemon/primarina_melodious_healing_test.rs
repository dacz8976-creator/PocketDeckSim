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

/// Primarina's Melodious Healing: "Once during your turn, you may heal 30 damage from each of your
/// [W] Pokémon."
///
/// The type filter is the whole point: Squirtle ([W]) heals, Bulbasaur ([G]) does not, even though
/// both are "each of your Pokémon".
#[test]
fn test_melodious_healing_heals_only_water_pokemon() {
    let mut game = get_test_game_with_board(
        vec![
            // Primarina: 140 HP, [W].
            PlayedCard::from_id(CardId::A3048Primarina).with_damage(50),
            // Squirtle: 60 HP, [W].
            PlayedCard::from_id(CardId::A1053Squirtle).with_damage(40),
            // Bulbasaur: 70 HP, [G] — must not be healed.
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Melodious Healing should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert_eq!(
        state.in_play_pokemon[0][0]
            .as_ref()
            .expect("Primarina")
            .get_remaining_hp(),
        120,
        "Primarina is a [W] Pokémon and should heal 30 (140 - 50 + 30)"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("Squirtle")
            .get_remaining_hp(),
        50,
        "Squirtle is a [W] Pokémon and should heal 30 (60 - 40 + 30)"
    );
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .expect("Bulbasaur")
            .get_remaining_hp(),
        20,
        "Bulbasaur is a [G] Pokémon and must NOT be healed (70 - 50)"
    );
}

/// NEGATIVE: the opponent's damaged [W] Pokémon are not "your" Pokémon.
#[test]
fn test_melodious_healing_does_not_heal_the_opponent() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3048Primarina).with_damage(30)],
        vec![PlayedCard::from_id(CardId::A1053Squirtle).with_damage(40)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Melodious Healing should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        140,
        "Primarina should be fully healed (140 - 30 + 30)"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        20,
        "the opponent's [W] Squirtle should keep its damage (60 - 40)"
    );
}

/// The untyped printings of this ability template must keep healing every Pokémon regardless of
/// type — adding the [W] filter as a parameter must not narrow them.
#[test]
fn test_untyped_heal_all_printing_still_heals_every_type() {
    // A1 007 Butterfree's Powder Heal: "Once during your turn, you may heal 20 damage from each
    // of your Pokémon." (no type filter)
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1007Butterfree).with_damage(50),
            PlayedCard::from_id(CardId::A1053Squirtle).with_damage(40),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action = use_ability_action(&actions, 0).expect("Powder Heal should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("Squirtle")
            .get_remaining_hp(),
        40,
        "the untyped printing heals the [W] Squirtle (60 - 40 + 20)"
    );
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .expect("Bulbasaur")
            .get_remaining_hp(),
        40,
        "the untyped printing also heals the [G] Bulbasaur (70 - 50 + 20)"
    );
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_melodious_healing_is_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3048Primarina).with_damage(90)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Melodious Healing should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Melodious Healing should not be usable twice in the same turn"
    );
    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        80,
        "only one 30-point heal should have been applied"
    );
}
