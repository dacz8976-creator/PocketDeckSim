use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_test_game_with_board},
};

/// Stoutland's Dangerous Bite: 70, +70 if the opponent's Active Pokémon is a Basic Pokémon.
#[test]
fn test_dangerous_bite_extra_damage_against_basic() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B1203Stoutland).with_energy(vec![
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
        ],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1203Stoutland, 0),
        is_stack: false,
    });
    // Snorlax (Basic, 150 HP, weak to Fighting only): 150 - 140 = 10.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 10, "Dangerous Bite should deal 140 against a Basic");
}

/// Negative: against an Evolution Pokémon, Dangerous Bite deals only its base 70.
#[test]
fn test_dangerous_bite_base_damage_against_evolution() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B1203Stoutland).with_energy(vec![
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
        ],
        vec![PlayedCard::from_id(CardId::B3071Hatterene)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1203Stoutland, 0),
        is_stack: false,
    });
    // Hatterene (Stage 2, 150 HP, weak to Darkness only): 150 - 70 = 80.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 80, "Dangerous Bite should deal 70 against an Evolution");
}

/// Kangaskhan's Cross-Cut: 20, +40 if the opponent's Active Pokémon is an Evolution Pokémon.
#[test]
fn test_cross_cut_extra_damage_against_evolution() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4133Kangaskhan).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B3071Hatterene)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4133Kangaskhan, 0),
        is_stack: false,
    });
    // Hatterene: 150 - 60 = 90.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 90, "Cross-Cut should deal 60 against an Evolution");
}

/// Negative: against a Basic Pokémon, Cross-Cut deals only its base 20.
#[test]
fn test_cross_cut_base_damage_against_basic() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4133Kangaskhan).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4133Kangaskhan, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 130, "Cross-Cut should deal 20 against a Basic");
}

/// Fearow's Peck Bugs: 30, +40 if the opponent's Active Pokémon is a [G] Pokémon.
#[test]
fn test_peck_bugs_extra_damage_against_grass() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4130Fearow).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B2002Ledian)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4130Fearow, 0),
        is_stack: false,
    });
    // Ledian ([G], 80 HP, weak to Fire only): 80 - 70 = 10.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 10, "Peck Bugs should deal 70 against a [G] Pokémon");
}

/// Negative: Peck Bugs against a non-Grass Pokémon deals only 30.
#[test]
fn test_peck_bugs_base_damage_against_non_grass() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4130Fearow).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4130Fearow, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 120,
        "Peck Bugs should deal 30 against a non-[G] Pokémon"
    );
}

/// Scovillain's Red-Hot Headbutt: 60, +40 if the opponent's Active is a [G] OR [M] Pokémon.
/// Covers the multi-type parameterization of the same mechanic.
#[test]
fn test_red_hot_headbutt_extra_damage_against_metal() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a013Scovillain)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B3118Bronzong)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a013Scovillain, 0),
        is_stack: false,
    });
    // Bronzong ([M], 120 HP, weak to Fire only): 120 - 100 = 20.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 20,
        "Red-Hot Headbutt should deal 100 against a [M] Pokémon"
    );
}

/// Negative: Red-Hot Headbutt against a type outside {[G], [M]} deals only 60.
#[test]
fn test_red_hot_headbutt_base_damage_against_water() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a013Scovillain)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B2b017Lapras)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a013Scovillain, 0),
        is_stack: false,
    });
    // Lapras ([W], 100 HP, weak to Lightning only): 100 - 60 = 40.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 40,
        "Red-Hot Headbutt should deal 60 against a [W] Pokémon"
    );
}

/// Seviper's Fateful Fang: 40, +40 if the opponent's Active Pokémon is Zangoose.
#[test]
fn test_fateful_fang_extra_damage_against_zangoose() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a048Seviper)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A4a065Zangoose)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a048Seviper, 0),
        is_stack: false,
    });
    // Zangoose (80 HP, weak to Fighting only): 80 - 80 = 0 → Knocked Out; attacker scores.
    let state = game.get_state_clone();
    assert_eq!(
        state.points[0], 1,
        "Fateful Fang should deal 80 against Zangoose and Knock Out the 80 HP target"
    );
}

/// Negative: Fateful Fang against any other Pokémon deals only 40.
#[test]
fn test_fateful_fang_base_damage_against_non_zangoose() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a048Seviper)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a048Seviper, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 110,
        "Fateful Fang should deal 40 against a non-Zangoose"
    );
}

/// Heatmor's Roasting Heat: 30, +60 if the opponent's Active Pokémon is Burned.
#[test]
fn test_roasting_heat_extra_damage_against_burned() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4037Heatmor)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)
            .with_status_condition(StatusCondition::Burned)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4037Heatmor, 0),
        is_stack: false,
    });
    // 180 - 90 = 90.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 90,
        "Roasting Heat should deal 90 against a Burned target"
    );
}

/// Negative: Roasting Heat against a non-Burned target deals only 30.
#[test]
fn test_roasting_heat_base_damage_against_not_burned() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4037Heatmor)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4037Heatmor, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 150,
        "Roasting Heat should deal 30 against a non-Burned target"
    );
}

/// Rotom's Assault Laser: 20, +30 if the OPPONENT's Active Pokémon has a Tool attached.
#[test]
fn test_assault_laser_extra_damage_against_tool_holder() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2062Rotom).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)
            .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2062Rotom, 0),
        is_stack: false,
    });
    // 180 - 50 = 130.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 130,
        "Assault Laser should deal 50 against a Tool holder"
    );
}

/// Negative: the tool has to be on the OPPONENT's Active — Rotom holding a Tool itself
/// while the opponent holds none gives no bonus.
#[test]
fn test_assault_laser_base_damage_when_only_self_has_tool() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2062Rotom)
            .with_energy(vec![EnergyType::Colorless])
            .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2062Rotom, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 160,
        "Assault Laser should deal 20 when only the attacker holds a Tool"
    );
}

/// Bronzong's Psychic Resonance: 50, +50 if the opponent has any [P] Pokémon in play
/// (Bench included).
#[test]
fn test_psychic_resonance_extra_damage_with_psychic_in_play() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3118Bronzong)
            .with_energy(vec![EnergyType::Metal, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::B3071Hatterene), // [P] on the Bench
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3118Bronzong, 0),
        is_stack: false,
    });
    // 180 - 100 = 80.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 80,
        "Psychic Resonance should deal 100 with an opposing [P] Pokémon in play"
    );
}

/// Negative: no [P] Pokémon anywhere on the opponent's board → base 50 only.
#[test]
fn test_psychic_resonance_base_damage_without_psychic_in_play() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3118Bronzong)
            .with_energy(vec![EnergyType::Metal, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3118Bronzong, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 130,
        "Psychic Resonance should deal 50 without an opposing [P] Pokémon"
    );
}
