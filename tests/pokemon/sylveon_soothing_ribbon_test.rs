use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    test_support::get_test_game_with_board,
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Sylveon's Soothing Ribbon: "Once during your turn, if this Pokémon has a Pokémon Tool attached,
/// you may heal 30 damage from 1 of your Pokémon."
#[test]
fn test_soothing_ribbon_heals_a_chosen_pokemon_when_a_tool_is_attached() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3b030Sylveon)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Soothing Ribbon should be available with a tool");
    game.apply_action(&ability_action);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::Heal { .. })));

    let heal_bulbasaur = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Heal { in_play_idx: 1, .. }))
        .expect("the damaged Bulbasaur should be a heal target")
        .clone();
    game.apply_action(&heal_bulbasaur);

    assert_eq!(
        game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .expect("Bulbasaur")
            .get_remaining_hp(),
        50,
        "Soothing Ribbon should heal 30 damage (70 - 50 + 30)"
    );
}

/// NEGATIVE: with no Pokémon Tool attached the ability is not usable at all.
#[test]
fn test_soothing_ribbon_not_offered_without_a_tool() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3b030Sylveon),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Soothing Ribbon requires a Pokémon Tool attached to Sylveon"
    );
}

/// Any Pokémon Tool works — the card says "a Pokémon Tool", not a specific one — and Soothing
/// Ribbon carries no Active-Spot clause, so a benched Sylveon can use it. B3b 073 is the same card
/// at a different rarity.
#[test]
fn test_soothing_ribbon_works_from_the_bench_with_any_tool() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
            PlayedCard::from_id(CardId::B3b073Sylveon)
                .with_tool(get_card_by_enum(CardId::A2148RockyHelmet)),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 1).is_some(),
        "Soothing Ribbon should be offered from the Bench with any tool attached"
    );
}

/// NEGATIVE: nothing to heal means the ability is not offered, matching the existing
/// `HealOneYourPokemon` gating.
#[test]
fn test_soothing_ribbon_not_offered_with_no_damaged_pokemon() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3b030Sylveon)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Soothing Ribbon should not be offered when nothing is damaged"
    );
}

/// The Espeon ex printing of this template keeps its own gating: it needs the Active Spot and does
/// NOT need a tool. Adding the tool parameter must not leak into it.
#[test]
fn test_espeon_ex_psychic_healing_gating_is_unchanged() {
    // Active Espeon ex with no tool: still usable.
    let active_game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4083EspeonEx),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let (_actor, actions) = active_game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_some(),
        "Psychic Healing does not require a tool"
    );

    // Benched Espeon ex: still blocked by its "in the Active Spot" clause.
    let benched_game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
            PlayedCard::from_id(CardId::A4083EspeonEx),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let (_actor, actions) = benched_game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 1).is_none(),
        "Psychic Healing still requires Espeon ex to be in the Active Spot"
    );
}
