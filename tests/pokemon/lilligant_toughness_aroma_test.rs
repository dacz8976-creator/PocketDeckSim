//! Lilligant's Toughness Aroma (B1 018 / B1 329): "Each of your [G] Pokémon gets +20 HP."
//!
//! The buff is board-conditional, so it needs a negative test for a non-[G] Pokémon, for a board
//! with no Lilligant, and for a Lilligant sitting on the *opponent's* board. The last test covers
//! the awkward case: a buffed Pokémon that is only alive because of the +20 must be Knocked Out
//! the moment Lilligant leaves play.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Bulbasaur is [G] with 70 printed HP; Charmander is [R] with 60.
#[test]
fn test_toughness_aroma_gives_grass_pokemon_twenty_extra_hp() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B1018Lilligant),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        90,
        "Bulbasaur's 70 HP should become 90 while Lilligant is in play"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("Lilligant should be on the bench")
            .get_remaining_hp(),
        100,
        "Lilligant is itself a [G] Pokémon, so Toughness Aroma buffs it too"
    );
}

/// NEGATIVE: the buff is type-gated — a [R] Pokémon gets nothing.
#[test]
fn test_toughness_aroma_does_not_buff_non_grass_pokemon() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::B1018Lilligant),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        60,
        "Charmander is [R], so Toughness Aroma should leave its 60 HP alone"
    );
}

/// NEGATIVE: with no Lilligant in play the [G] Pokémon has its printed HP.
#[test]
fn test_grass_pokemon_has_printed_hp_without_lilligant() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        70,
        "Without Lilligant, Bulbasaur should have its printed 70 HP"
    );
}

/// NEGATIVE: "each of *your* [G] Pokémon" — the opponent's Lilligant does not buff your board.
#[test]
fn test_toughness_aroma_does_not_buff_the_opponents_grass_pokemon() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B1329Lilligant),
        ],
    );

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        70,
        "Your Bulbasaur should not benefit from the opponent's Lilligant"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        90,
        "The opponent's own Bulbasaur should be buffed by their Lilligant"
    );
}

/// A [G] Pokémon kept alive only by the +20 is Knocked Out the moment Lilligant leaves play.
///
/// Player 1's Active Lilligant (80 + 20 = 100 effective HP) already carries 70 damage, so
/// Lunatone's 50 damage Moon Press knocks it out. The Benched Bulbasaur carries 80 damage: it
/// survives at 10 HP while buffed (90 effective) but is dead on its printed 70 once the buff goes.
#[test]
fn test_grass_pokemon_is_knocked_out_when_lilligant_leaves_play() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3073Lunatone)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::B1018Lilligant).with_damage(70),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(80),
            PlayedCard::from_id(CardId::A1094Pikachu),
        ],
    );

    let before = game.get_state_clone();
    assert_eq!(
        before.in_play_pokemon[1][1]
            .as_ref()
            .expect("Bulbasaur should start on the bench")
            .get_remaining_hp(),
        10,
        "The Benched Bulbasaur should be alive at 10 HP thanks to Toughness Aroma"
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "Lilligant should have been Knocked Out"
    );
    assert!(
        state.in_play_pokemon[1][1].is_none(),
        "Bulbasaur should be Knocked Out once Lilligant's +20 HP is gone"
    );
    assert_eq!(
        state.points[0], 2,
        "Both knockouts should award a point to the attacker"
    );

    // Player 1 is left promoting their last Pokémon.
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 1);
    let promote = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. }))
        .expect("Player 1 should have to promote after losing their Active")
        .clone();
    game.apply_action(&promote);
    assert_eq!(game.get_state_clone().get_active(1).get_name(), "Pikachu");
}
