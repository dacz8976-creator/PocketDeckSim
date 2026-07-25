use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn defender_hp_after_attack(
    attacker_id: CardId,
    energy: Vec<EnergyType>,
    defender: PlayedCard,
) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(attacker_id).with_energy(energy)],
        vec![defender],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Staraptor's Defensive Whirlwind: "This Pokémon takes -30 damage from attacks from [F] Pokémon."
/// Hitmontop's Spinning Attack is 50 damage from a [F] Pokémon; Staraptor has 140 HP and is weak
/// to [L], so Weakness never enters the calculation.
#[test]
fn test_defensive_whirlwind_reduces_fighting_attack_by_30() {
    let hp = defender_hp_after_attack(
        CardId::A2085Hitmontop,
        vec![EnergyType::Fighting, EnergyType::Fighting],
        PlayedCard::from_id(CardId::PA047Staraptor),
    );
    assert_eq!(
        hp, 120,
        "Defensive Whirlwind should turn Spinning Attack's 50 damage into 20"
    );
}

/// NEGATIVE: a [P] attacker (Lunatone's Moon Press, also 50 damage) is not reduced at all.
#[test]
fn test_defensive_whirlwind_does_not_reduce_psychic_attack() {
    let hp = defender_hp_after_attack(
        CardId::A3073Lunatone,
        vec![EnergyType::Psychic, EnergyType::Colorless],
        PlayedCard::from_id(CardId::PA047Staraptor),
    );
    assert_eq!(
        hp, 90,
        "Defensive Whirlwind should not reduce damage from a [P] Pokémon"
    );
}
