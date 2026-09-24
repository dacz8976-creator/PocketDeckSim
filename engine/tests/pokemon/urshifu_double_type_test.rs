use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game},
};

/// Rapid Strike Urshifu (B3 051) Double Type: "As long as this Pokémon is in play, it is [W] and
/// [F] type."
/// Single Strike Urshifu (B3 113) Double Type: "As long as this Pokémon is in play, it is [F] and
/// [D] type."
///
/// Weakness reads the attacker's type, so it is the cleanest observable consequence: Single Strike
/// Urshifu is printed [D] but Double Type also makes it [F], and Rapid Strike Urshifu is printed
/// [W] but Double Type also makes it [F].
fn damage_from_single_strike_power_blast(defender: CardId) -> u32 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B3113SingleStrikeUrshifu).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Darkness,
            ]),
        ],
        vec![
            PlayedCard::from_id(defender),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    state.current_player = 0;
    game.set_state(state);

    let hp_before = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3113SingleStrikeUrshifu, 0),
        is_stack: false,
    });
    let hp_after = game.get_state_clone().get_active(1).get_remaining_hp();
    assert!(hp_after > 0, "the defender must survive so damage is exact");
    hp_before - hp_after
}

fn damage_from_rapid_strike_tornado_shot(defender: CardId) -> u32 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        // No Bench for the opponent, so Tornado Shot's "40 damage to 1 Benched Pokémon" half has
        // no target and the active damage lands immediately.
        vec![PlayedCard::from_id(defender)],
    );
    state.current_player = 0;
    game.set_state(state);

    let hp_before = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3051RapidStrikeUrshifu, 0),
        is_stack: false,
    });
    let hp_after = game.get_state_clone().get_active(1).get_remaining_hp();
    assert!(hp_after > 0, "the defender must survive so damage is exact");
    hp_before - hp_after
}

#[test]
fn test_single_strike_urshifu_counts_as_fighting_for_weakness() {
    // Mega Ampharos ex (B1 085) is weak to [F]. Single Strike Urshifu is printed [D], so the only
    // way Power Blast (110) hits for 130 is Double Type making it [F] as well.
    assert_eq!(
        damage_from_single_strike_power_blast(CardId::B1085MegaAmpharosEx),
        130
    );
}

#[test]
fn test_single_strike_urshifu_keeps_its_printed_darkness_type() {
    // Mega Gardevoir ex (B2 066) is weak to [D] — Double Type must not take the printed type away.
    assert_eq!(
        damage_from_single_strike_power_blast(CardId::B2066MegaGardevoirEx),
        130
    );
}

/// NEGATIVE: Double Type grants [F] and [D] and nothing else, so a [W]-weak defender takes plain
/// damage.
#[test]
fn test_single_strike_urshifu_is_not_water_type() {
    // Mega Charizard Y ex (B1a 014) is weak to [W].
    assert_eq!(
        damage_from_single_strike_power_blast(CardId::B1a014MegaCharizardYEx),
        110
    );
}

#[test]
fn test_rapid_strike_urshifu_counts_as_fighting_for_weakness() {
    // Rapid Strike Urshifu is printed [W]; Tornado Shot (40) hits Mega Ampharos ex for 60 only if
    // Double Type also makes it [F].
    assert_eq!(
        damage_from_rapid_strike_tornado_shot(CardId::B1085MegaAmpharosEx),
        60
    );
}

#[test]
fn test_rapid_strike_urshifu_keeps_its_printed_water_type() {
    assert_eq!(
        damage_from_rapid_strike_tornado_shot(CardId::B1a014MegaCharizardYEx),
        60
    );
}

/// NEGATIVE: Rapid Strike Urshifu is [W] and [F], not [D].
#[test]
fn test_rapid_strike_urshifu_is_not_darkness_type() {
    assert_eq!(
        damage_from_rapid_strike_tornado_shot(CardId::B2066MegaGardevoirEx),
        40
    );
}
