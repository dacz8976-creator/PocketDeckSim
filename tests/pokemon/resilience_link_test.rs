use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Lunatone's Moon Press (50 damage, [P]) attacks the defender's Active Pokémon.
/// None of the defenders used below are weak to [P], so Weakness never applies.
fn defender_hp_after_moon_press(defender_board: Vec<PlayedCard>) -> u32 {
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

/// Magnezone's Resilience Link: "If you have Arceus or Arceus ex in play, this Pokémon takes
/// -30 damage from attacks." Magnezone has 140 HP and is weak to [R].
#[test]
fn test_resilience_link_reduces_damage_with_arceus_in_play() {
    let hp = defender_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::A2a055Magnezone),
        PlayedCard::from_id(CardId::A2a070Arceus),
    ]);
    assert_eq!(
        hp, 120,
        "Resilience Link should turn Moon Press' 50 damage into 20 while Arceus is in play"
    );
}

/// Arceus ex counts as well.
#[test]
fn test_resilience_link_reduces_damage_with_arceus_ex_in_play() {
    let hp = defender_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::A2a026Raichu),
        PlayedCard::from_id(CardId::A2a071ArceusEx),
    ]);
    assert_eq!(
        hp, 70,
        "Resilience Link should also trigger off Arceus ex (Raichu: 90 HP - 20)"
    );
}

/// The promo Raichu (P-A 044) prints the same ability.
#[test]
fn test_resilience_link_promo_raichu_reduces_damage() {
    let hp = defender_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::PA044Raichu),
        PlayedCard::from_id(CardId::A2a070Arceus),
    ]);
    assert_eq!(hp, 70, "P-A 044 Raichu should share Resilience Link");
}

/// NEGATIVE: without an Arceus on the board the ability does nothing.
#[test]
fn test_resilience_link_does_nothing_without_arceus() {
    let hp = defender_hp_after_moon_press(vec![
        PlayedCard::from_id(CardId::A2a055Magnezone),
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    ]);
    assert_eq!(
        hp, 90,
        "Resilience Link should not reduce damage when no Arceus is in play"
    );
}

/// NEGATIVE: an Arceus on the *attacker's* board must not shield the defender.
#[test]
fn test_resilience_link_ignores_opponents_arceus() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3073Lunatone)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A2a070Arceus),
        ],
        vec![PlayedCard::from_id(CardId::A2a055Magnezone)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        90,
        "Resilience Link only looks at its own controller's board"
    );
}
