use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Runs the attacker's first attack into `defender` and returns the defender's remaining HP.
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

/// Magmar's Magma Punch: 50 damage from a [R] Pokémon.
fn fire_attacker() -> (CardId, Vec<EnergyType>) {
    (
        CardId::A1044Magmar,
        vec![EnergyType::Fire, EnergyType::Fire],
    )
}

/// Bruxish's Wave Splash: 50 damage from a [W] Pokémon.
fn water_attacker() -> (CardId, Vec<EnergyType>) {
    (
        CardId::A3055Bruxish,
        vec![EnergyType::Water, EnergyType::Colorless],
    )
}

/// Lunatone's Moon Press: 50 damage from a [P] Pokémon (neither [R] nor [W]).
fn psychic_attacker() -> (CardId, Vec<EnergyType>) {
    (
        CardId::A3073Lunatone,
        vec![EnergyType::Psychic, EnergyType::Colorless],
    )
}

/// Mamoswine's Thick Fat: "This Pokémon takes -30 damage from attacks from [R] or [W] Pokémon."
/// Mamoswine has 160 HP and is weak to [M], so neither attacker triggers Weakness.
#[test]
fn test_thick_fat_reduces_fire_attack_by_30() {
    let (attacker, energy) = fire_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A2033Mamoswine),
    );
    assert_eq!(
        hp, 140,
        "Thick Fat should turn Magma Punch's 50 damage into 20"
    );
}

#[test]
fn test_thick_fat_reduces_water_attack_by_30() {
    let (attacker, energy) = water_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A2160Mamoswine),
    );
    assert_eq!(
        hp, 140,
        "Thick Fat should turn Wave Splash's 50 damage into 20"
    );
}

/// Azumarill (A4 050) shares the -30 Thick Fat text and has 110 HP.
#[test]
fn test_thick_fat_azumarill_reduces_fire_attack_by_30() {
    let (attacker, energy) = fire_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A4050Azumarill),
    );
    assert_eq!(hp, 90, "Thick Fat should reduce the 50 damage attack to 20");
}

/// NEGATIVE: Thick Fat only cares about [R] and [W] attackers. A [P] attacker deals full damage.
#[test]
fn test_thick_fat_does_not_reduce_psychic_attack() {
    let (attacker, energy) = psychic_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A2033Mamoswine),
    );
    assert_eq!(
        hp, 110,
        "Thick Fat should not reduce damage from a [P] Pokémon"
    );
}

/// Piloswine (A2 032) prints the same ability at -20 instead of -30. Same mechanic, other amount.
#[test]
fn test_thick_fat_piloswine_reduces_fire_attack_by_20() {
    let (attacker, energy) = fire_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A2032Piloswine),
    );
    assert_eq!(
        hp, 80,
        "Piloswine's -20 Thick Fat should turn 50 damage into 30"
    );
}

/// NEGATIVE: the -20 printing is equally type-gated.
#[test]
fn test_thick_fat_piloswine_does_not_reduce_psychic_attack() {
    let (attacker, energy) = psychic_attacker();
    let hp = defender_hp_after_attack(
        attacker,
        energy,
        PlayedCard::from_id(CardId::A2032Piloswine),
    );
    assert_eq!(
        hp, 60,
        "Piloswine's Thick Fat should not reduce damage from a [P] Pokémon"
    );
}
