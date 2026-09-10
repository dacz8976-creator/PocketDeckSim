use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

/// Ting-Lu's Arrogant Impact: 130, but the attack does NOTHING if Ting-Lu's remaining HP
/// is 60 or less.
#[test]
fn test_arrogant_impact_does_nothing_at_low_hp() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a062TingLu)
            .with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
            ])
            .with_remaining_hp(60)],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a062TingLu, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 180,
        "Arrogant Impact should do nothing with 60 or less remaining HP"
    );
}

/// Negative: at more than 60 remaining HP the attack deals its full 130.
#[test]
fn test_arrogant_impact_full_damage_at_high_hp() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a062TingLu)
            .with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
            ])
            .with_remaining_hp(70)],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a062TingLu, 0),
        is_stack: false,
    });
    // 180 - 130 = 50.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 50,
        "Arrogant Impact should deal 130 with more than 60 remaining HP"
    );
}

/// Flutter Mane's Hexing Flight: 90, but the attack does NOTHING unless this Pokémon moved
/// from the Bench to the Active Spot this turn.
#[test]
fn test_hexing_flight_full_damage_after_moving_to_active() {
    let mut flutter_mane = PlayedCard::from_id(CardId::B3b035FlutterMane)
        .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]);
    flutter_mane.moved_to_active_this_turn = true;

    let mut game = get_test_game_with_board(vec![flutter_mane], vec![sponge()]);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3b035FlutterMane, 0),
        is_stack: false,
    });
    // 180 - 90 = 90.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 90,
        "Hexing Flight should deal 90 after moving from the Bench this turn"
    );
}

/// Negative: without having moved from the Bench this turn, Hexing Flight does nothing.
#[test]
fn test_hexing_flight_does_nothing_without_moving() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3b035FlutterMane)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3b035FlutterMane, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 180,
        "Hexing Flight should do nothing unless it moved from the Bench this turn"
    );
}
