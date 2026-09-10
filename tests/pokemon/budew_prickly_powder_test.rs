use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Budew (B3 013 / 159) "Prickly Powder": "The Defending Pokémon loses all Abilities. This effect
/// lasts until the Defending Pokémon leaves the Active Spot."
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn prickly_powder(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3013Budew, 0),
        is_stack: false,
    });
}

/// Melmetal's Hard Coat ("This Pokémon takes -20 damage from attacks") fully absorbs Prickly
/// Powder's 10 damage — until Prickly Powder switches the Ability off.
#[test]
fn test_budew_prickly_powder_switches_off_a_passive_ability() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![PlayedCard::from_id(CardId::A1182Melmetal)],
    );

    prickly_powder(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        130,
        "Hard Coat is still on for the attack that applies Prickly Powder, so 10 - 20 = 0 damage"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    prickly_powder(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        120,
        "with Hard Coat switched off Prickly Powder should land its full 10 damage"
    );
}

/// Activated Abilities disappear from the Defending Pokémon's move generation too.
#[test]
fn test_budew_prickly_powder_removes_an_activated_ability_from_move_generation() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![PlayedCard::from_id(CardId::A1007Butterfree).with_damage(30)],
    );

    prickly_powder(&mut game);
    end_turn(&mut game, 0);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1);
    assert!(
        !choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::UseAbility { in_play_idx: 0 })),
        "Powder Heal should be unusable while Prickly Powder is on Butterfree"
    );
}

/// Negative: the same board without Prickly Powder keeps the Ability available.
#[test]
fn test_butterfree_keeps_its_ability_without_prickly_powder() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![PlayedCard::from_id(CardId::A1007Butterfree).with_damage(30)],
    );

    end_turn(&mut game, 0);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::UseAbility { in_play_idx: 0 })),
        "with no Prickly Powder applied, Powder Heal should still be offered"
    );
}
