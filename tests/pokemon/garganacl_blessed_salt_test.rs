use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    test_support::get_test_game_with_board,
    State,
};

/// Ends player 0's turn (which runs Pokémon Checkup) with `bench` sitting behind a damaged
/// Bulbasaur, and a damaged Charmander on the opponent's side.
fn end_turn_with_bench(bench: CardId) -> State {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(40),
            PlayedCard::from_id(bench).with_remaining_hp(100),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(30)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    game.get_state_clone()
}

fn remaining_hp(state: &State, player: usize, idx: usize) -> u32 {
    state.in_play_pokemon[player][idx]
        .as_ref()
        .expect("Pokemon should still be in play")
        .get_remaining_hp()
}

/// Garganacl (B3a 033) "Blessed Salt": "During Pokémon Checkup, heal 10 damage from each of your
/// Pokémon." The card prints no Active Spot requirement, so it heals from the Bench as well.
#[test]
fn test_blessed_salt_heals_each_of_your_pokemon_during_checkup() {
    let state = end_turn_with_bench(CardId::B3a033Garganacl);

    assert_eq!(
        remaining_hp(&state, 0, 0),
        50,
        "Blessed Salt should heal 10 from the Active Pokémon"
    );
    assert_eq!(
        remaining_hp(&state, 0, 1),
        110,
        "Blessed Salt should heal 10 from Garganacl itself, on the Bench"
    );
}

/// Blessed Salt is scoped to "each of *your* Pokémon" — the opponent's board is untouched.
#[test]
fn test_blessed_salt_does_not_heal_the_opponent() {
    let state = end_turn_with_bench(CardId::B3a033Garganacl);

    assert_eq!(
        remaining_hp(&state, 1, 0),
        30,
        "Blessed Salt should never heal the opponent's Pokémon"
    );
}

/// Negative test: the exact same board with a plain Pokémon on the Bench heals nobody, so the
/// test above is measuring the Ability and not some other checkup step.
#[test]
fn test_no_checkup_healing_without_blessed_salt() {
    let state = end_turn_with_bench(CardId::A1004VenusaurEx);

    assert_eq!(
        remaining_hp(&state, 0, 0),
        40,
        "without Blessed Salt nothing should heal during checkup"
    );
    assert_eq!(remaining_hp(&state, 0, 1), 100);
    assert_eq!(remaining_hp(&state, 1, 0), 30);
}
