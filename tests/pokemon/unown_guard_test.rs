use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Lunatone's Moon Press: 50 damage from a [P] Pokémon. Mega Latios ex (180 HP, no Weakness) is
/// the damage sponge, so the raw and reduced numbers stay distinguishable.
fn latios_hp_after_moon_press(defender_board: Vec<PlayedCard>) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3073Lunatone)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        defender_board,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Unown's GUARD (A4 084): "This Ability works if you have any Unown in play with an Ability other
/// than GUARD. All of your Pokémon take -10 damage from attacks from your opponent's Pokémon."
/// A2a 034 Unown has CHECK, which satisfies the "other than GUARD" clause.
#[test]
fn test_unown_guard_reduces_damage_with_another_unown_in_play() {
    let hp = latios_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        PlayedCard::from_id(CardId::A4084Unown),
        PlayedCard::from_id(CardId::A2a034Unown),
    ]);
    assert_eq!(
        hp, 140,
        "GUARD should reduce the 50 damage attack to 40 for every Pokémon its controller has"
    );
}

/// NEGATIVE: GUARD alone does nothing — it needs a *different* Unown Ability in play.
#[test]
fn test_unown_guard_does_nothing_without_another_unown() {
    let hp = latios_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        PlayedCard::from_id(CardId::A4084Unown),
    ]);
    assert_eq!(
        hp, 130,
        "GUARD should be inactive when the only Unown in play is itself"
    );
}

/// NEGATIVE: a second GUARD Unown is still "an Unown with the GUARD Ability", so two GUARD Unown
/// do not enable each other.
#[test]
fn test_unown_guard_is_not_enabled_by_a_second_guard_unown() {
    let hp = latios_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        PlayedCard::from_id(CardId::A4084Unown),
        PlayedCard::from_id(CardId::A4084Unown),
    ]);
    assert_eq!(
        hp, 130,
        "Two GUARD Unown should not satisfy each other's 'Ability other than GUARD' clause"
    );
}

/// GUARD protects the whole board, including the Unown sitting on the Bench. Bulbasaur's Vine Whip
/// only hits the Active Spot, so the Bench check is driven through a benched-target attack instead:
/// Lunatone attacks the Active, and the benched GUARD Unown is untouched — what this asserts is
/// that the Active Mega Latios ex (not the ability holder itself) receives the reduction.
#[test]
fn test_unown_guard_protects_pokemon_other_than_itself() {
    let hp = latios_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        PlayedCard::from_id(CardId::A2a034Unown),
        PlayedCard::from_id(CardId::A4084Unown),
    ]);
    assert_eq!(
        hp, 140,
        "GUARD applies to all of its controller's Pokémon, regardless of board position"
    );
}
