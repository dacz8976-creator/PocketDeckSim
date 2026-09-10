use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Player 0's Popplio uses "Sing" (0 damage, "Your opponent's Active Pokémon is now Asleep.")
/// against whatever player 1 has in the Active Spot, and reports whether it fell asleep.
fn sing_at(defender: CardId) -> bool {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3045Popplio).with_energy(vec![EnergyType::Water])],
        vec![PlayedCard::from_id(defender)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3045Popplio, 0),
        is_stack: false,
    });

    game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .expect("defender should still be in play after a 0 damage attack")
        .is_asleep()
}

/// Hoothoot (A4 140) "Insomnia": "This Pokémon can't be Asleep."
#[test]
fn test_insomnia_blocks_asleep() {
    assert!(
        !sing_at(CardId::A4140Hoothoot),
        "Insomnia should keep Hoothoot awake through Sing"
    );
}

/// Negative control: without Insomnia the very same attack does put the defender to sleep, so the
/// test above is really measuring the Ability and not a broken Sing.
#[test]
fn test_pokemon_without_insomnia_still_falls_asleep() {
    assert!(
        sing_at(CardId::A1001Bulbasaur),
        "Sing should put a Pokémon without Insomnia to Sleep"
    );
}

/// Negative test for the *scope* of the immunity: Insomnia names only Asleep, so every other
/// Special Condition still lands. Weezing's Gas Leak poisons the opponent's Active Pokémon.
#[test]
fn test_insomnia_does_not_block_other_status_conditions() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1177Weezing)],
        vec![PlayedCard::from_id(CardId::A4140Hoothoot)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    });

    let state = game.get_state_clone();
    let hoothoot = state.in_play_pokemon[1][0]
        .as_ref()
        .expect("Hoothoot should still be in play");
    assert!(
        hoothoot.is_poisoned(),
        "Insomnia only prevents Asleep; Poisoned should still stick"
    );
}
