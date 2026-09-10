use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Lunatone's Moon Press: 50 damage from a [P] Pokémon. Eiscue has 80 HP and is weak to [M],
/// so it survives the attack either way and Weakness never applies.
fn eiscue_hp_after_moon_press(eiscue: PlayedCard) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3073Lunatone)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        vec![eiscue],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Eiscue's Ice Face: "If this Pokémon has full HP, it takes -40 damage from attacks from your
/// opponent's Pokémon."
#[test]
fn test_ice_face_reduces_damage_at_full_hp() {
    let hp = eiscue_hp_after_moon_press(PlayedCard::from_id(CardId::B1080Eiscue));
    assert_eq!(
        hp, 70,
        "Ice Face should turn Moon Press' 50 damage into 10 while Eiscue is undamaged"
    );
}

/// B1 236 is the same card at a different rarity.
#[test]
fn test_ice_face_full_art_reduces_damage_at_full_hp() {
    let hp = eiscue_hp_after_moon_press(PlayedCard::from_id(CardId::B1236Eiscue));
    assert_eq!(hp, 70, "B1 236 Eiscue should share Ice Face");
}

/// NEGATIVE: once Eiscue has taken any damage it is no longer at full HP, so the reduction stops.
#[test]
fn test_ice_face_does_nothing_once_damaged() {
    let hp =
        eiscue_hp_after_moon_press(PlayedCard::from_id(CardId::B1080Eiscue).with_remaining_hp(70));
    assert_eq!(
        hp, 20,
        "A damaged Eiscue should take Moon Press' full 50 damage"
    );
}
