use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Purrloin (A3b 045) "Playful Knockdown": "Discard all Pokémon Tools from your opponent's Active
/// Pokémon." The attack has no printed damage.
fn playful_knockdown(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3b045Purrloin, 0),
        is_stack: false,
    });
}

#[test]
fn test_purrloin_playful_knockdown_discards_the_defenders_tool() {
    let giant_cape = get_card_by_enum(CardId::A2147GiantCape);
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3b045Purrloin).with_energy(vec![EnergyType::Darkness])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_tool(giant_cape.clone())],
    );

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        90,
        "Giant Cape should be granting Bulbasaur its +20 HP before the attack"
    );

    playful_knockdown(&mut game);

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0]
            .as_ref()
            .expect("Bulbasaur should still be in play")
            .attached_tool
            .is_none(),
        "Playful Knockdown should discard the Tool"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        70,
        "losing Giant Cape should take Bulbasaur back down to its printed 70 HP"
    );
    assert!(state.discard_piles[1].contains(&giant_cape));
}

/// Negative: nothing to discard means the attack simply does nothing.
#[test]
fn test_purrloin_playful_knockdown_without_a_tool_attached() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3b045Purrloin).with_energy(vec![EnergyType::Darkness])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    playful_knockdown(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        70,
        "Playful Knockdown has no printed damage"
    );
    assert!(
        state.discard_piles[1].is_empty(),
        "nothing should be discarded when the Defending Pokémon has no Tool"
    );
}
