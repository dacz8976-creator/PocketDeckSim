use deckgym::{
    actions::Action,
    card_ids::CardId,
    effects::CardEffect,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Ledian's Swift: 40, unaffected by Weakness. Tyrantrum is weak to [G] and Ledian is a
/// [G] attacker, but the +20 Weakness bonus must not apply.
#[test]
fn test_swift_ignores_weakness() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2002Ledian).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B2090Tyrantrum)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2002Ledian, 0),
        is_stack: false,
    });
    // Tyrantrum: 150 - 40 = 110 (not 150 - 60 = 90).
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 110, "Swift should ignore Weakness and deal exactly 40");
}

/// Ledian's Swift is also unaffected by effects on the opponent's Active Pokémon: a
/// ReducedDamage effect on the defender must not shave the 40.
#[test]
fn test_swift_ignores_defender_damage_reduction_effects() {
    let mut defender = PlayedCard::from_id(CardId::A1211Snorlax);
    defender.add_effect(CardEffect::ReducedDamage { amount: 20 }, 1);

    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2002Ledian).with_energy(vec![EnergyType::Colorless])],
        vec![defender],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2002Ledian, 0),
        is_stack: false,
    });
    // Snorlax: 150 - 40 = 110 (not 150 - 20 = 130).
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 110,
        "Swift should ignore effects on the opponent's Active and deal exactly 40"
    );
}
