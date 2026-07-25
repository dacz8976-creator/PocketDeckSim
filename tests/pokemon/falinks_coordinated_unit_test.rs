//! Falinks' Coordinated Unit (B2 092 / B2 172): "If you have another Falinks in play, this
//! Pokémon's attacks do +20 damage to your opponent's Active Pokémon, and this Pokémon takes -20
//! damage from attacks from your opponent's Pokémon."
//!
//! Both halves of the ability get a positive and a negative test — "another" Falinks means a
//! second one, so a lone Falinks must do nothing.

use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Falinks' Invade: 20 damage for [F]. Mega Latios ex (180 HP, no Weakness) absorbs it so the
/// difference is never capped by a knockout.
fn latios_hp_after_invade(attacker_board: Vec<PlayedCard>) -> u32 {
    let mut game = get_test_game_with_board(
        attacker_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2092Falinks, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Bulbasaur's Vine Whip: 40 damage from a [G] Pokémon. Falinks' Weakness is [P], so a Grass
/// attacker keeps the arithmetic free of a Weakness bonus.
fn falinks_hp_after_vine_whip(defender_board: Vec<PlayedCard>) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        defender_board,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

fn active_falinks() -> PlayedCard {
    PlayedCard::from_id(CardId::B2092Falinks).with_energy(vec![EnergyType::Fighting])
}

#[test]
fn test_coordinated_unit_boosts_damage_with_another_falinks_in_play() {
    let hp = latios_hp_after_invade(vec![
        active_falinks(),
        PlayedCard::from_id(CardId::B2172Falinks),
    ]);
    assert_eq!(
        hp, 140,
        "A second Falinks should add 20 to Invade's 20 damage"
    );
}

/// NEGATIVE: a lone Falinks is not "another Falinks in play".
#[test]
fn test_coordinated_unit_does_not_boost_a_lone_falinks() {
    let hp = latios_hp_after_invade(vec![active_falinks()]);
    assert_eq!(hp, 160, "Invade alone should do its printed 20 damage");
}

#[test]
fn test_coordinated_unit_reduces_damage_with_another_falinks_in_play() {
    let hp = falinks_hp_after_vine_whip(vec![
        PlayedCard::from_id(CardId::B2092Falinks),
        PlayedCard::from_id(CardId::B2172Falinks),
    ]);
    assert_eq!(
        hp, 50,
        "A second Falinks should cut Vine Whip's 40 damage down to 20"
    );
}

/// NEGATIVE: a lone Falinks takes the full hit.
#[test]
fn test_coordinated_unit_does_not_protect_a_lone_falinks() {
    let hp = falinks_hp_after_vine_whip(vec![PlayedCard::from_id(CardId::B2092Falinks)]);
    assert_eq!(hp, 30, "A single Falinks should take all 40 damage");
}

/// NEGATIVE: the other Falinks has to be *yours*. One on the attacker's board does not count.
#[test]
fn test_coordinated_unit_is_not_enabled_by_opponents_falinks() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::B2172Falinks),
        ],
        vec![PlayedCard::from_id(CardId::B2092Falinks)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        30,
        "Only Falinks on your own board satisfy 'another Falinks in play'"
    );
}
