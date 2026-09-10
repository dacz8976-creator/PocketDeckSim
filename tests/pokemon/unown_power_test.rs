use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Lunatone's Moon Press: 50 damage. Mega Latios ex (180 HP, no Weakness) is the damage sponge so
/// the boosted and unboosted numbers stay distinguishable and nothing is capped by a knockout.
fn latios_hp_after_moon_press(attacker_board: Vec<PlayedCard>) -> u32 {
    let mut game = get_test_game_with_board(
        attacker_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

fn lunatone() -> PlayedCard {
    PlayedCard::from_id(CardId::A3073Lunatone)
        .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])
}

/// Unown's POWER (A4 085): "This Ability works if you have any Unown in play with an Ability other
/// than POWER. Attacks used by your Pokémon do +10 damage to your opponent's Active Pokémon."
/// A2a 034 Unown has CHECK, which satisfies the "other than POWER" clause.
#[test]
fn test_unown_power_boosts_damage_with_another_unown_in_play() {
    let hp = latios_hp_after_moon_press(vec![
        lunatone(),
        PlayedCard::from_id(CardId::A4085Unown),
        PlayedCard::from_id(CardId::A2a034Unown),
    ]);
    assert_eq!(
        hp, 120,
        "POWER should add 10 to the 50 damage attack used by any of its controller's Pokémon"
    );
}

/// NEGATIVE: POWER alone does nothing — it needs a *different* Unown Ability in play.
#[test]
fn test_unown_power_does_nothing_without_another_unown() {
    let hp = latios_hp_after_moon_press(vec![lunatone(), PlayedCard::from_id(CardId::A4085Unown)]);
    assert_eq!(
        hp, 130,
        "POWER should be inactive when the only Unown in play is itself"
    );
}

/// NEGATIVE: a second POWER Unown is still "an Unown with the POWER Ability", so two POWER Unown
/// do not enable each other.
#[test]
fn test_unown_power_is_not_enabled_by_a_second_power_unown() {
    let hp = latios_hp_after_moon_press(vec![
        lunatone(),
        PlayedCard::from_id(CardId::A4085Unown),
        PlayedCard::from_id(CardId::A4085Unown),
    ]);
    assert_eq!(
        hp, 130,
        "Two POWER Unown should not satisfy each other's 'Ability other than POWER' clause"
    );
}

/// POWER is board-wide and stacks: two POWER Unown enabled by one CHECK Unown add +10 each.
#[test]
fn test_unown_power_stacks_across_multiple_power_unown() {
    let hp = latios_hp_after_moon_press(vec![
        lunatone(),
        PlayedCard::from_id(CardId::A4085Unown),
        PlayedCard::from_id(CardId::A4085Unown),
        PlayedCard::from_id(CardId::A2a034Unown),
    ]);
    assert_eq!(
        hp, 110,
        "Each enabled POWER Unown should contribute its own +10"
    );
}

/// NEGATIVE: the opponent's Unown never boost your attacks.
#[test]
fn test_unown_power_on_opponent_board_does_not_boost_your_attack() {
    let mut game = get_test_game_with_board(
        vec![lunatone()],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A4085Unown),
            PlayedCard::from_id(CardId::A2a034Unown),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        130,
        "POWER only boosts attacks used by its own controller's Pokémon"
    );
}
