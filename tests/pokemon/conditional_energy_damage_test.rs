use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    // Mega Latios ex: 180 HP, no weakness — a damage sponge that never adds surprise modifiers.
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

/// Poliwrath ex's Hydro Knuckle: 100, +40 if any [W] Energy is attached to this Pokémon.
#[test]
fn test_hydro_knuckle_extra_damage_with_water_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4a042PoliwrathEx).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Water,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a042PoliwrathEx, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 40, "Hydro Knuckle should deal 140 with [W] attached");
}

/// Negative: without [W] Energy attached, Hydro Knuckle deals only 100.
#[test]
fn test_hydro_knuckle_base_damage_without_water_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4a042PoliwrathEx).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
            ]),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a042PoliwrathEx, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 80, "Hydro Knuckle should deal 100 without [W] attached");
}

/// Quagsire's Muddy Headbutt: 60, +60 if any [F] Energy is attached (same mechanic as
/// Poliwrath, with a different type parameter).
#[test]
fn test_muddy_headbutt_extra_damage_with_fighting_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3039Quagsire).with_energy(vec![
            EnergyType::Water,
            EnergyType::Fighting,
            EnergyType::Colorless,
        ])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3039Quagsire, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 60, "Muddy Headbutt should deal 120 with [F] attached");
}

/// Negative: Muddy Headbutt without [F] Energy deals only 60.
#[test]
fn test_muddy_headbutt_base_damage_without_fighting_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3039Quagsire).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
        ])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3039Quagsire, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 120,
        "Muddy Headbutt should deal 60 without [F] attached"
    );
}

/// Leafeon's Leaf Blast: 10, +20 for each [G] Energy attached to this Pokémon.
#[test]
fn test_leaf_blast_scales_with_grass_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3b002Leafeon).with_energy(vec![
            EnergyType::Grass,
            EnergyType::Grass,
            EnergyType::Grass,
        ])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3b002Leafeon, 0),
        is_stack: false,
    });
    // 10 + 20 × 3 = 70. 180 - 70 = 110.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 110, "Leaf Blast should deal 10 + 20 per [G] Energy");
}

/// Negative: Leaf Blast with no [G] Energy attached deals only its base 10.
#[test]
fn test_leaf_blast_base_damage_without_grass_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3b002Leafeon).with_energy(vec![EnergyType::Fire])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3b002Leafeon, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 170, "Leaf Blast should deal 10 with no [G] Energy");
}

/// Enamorus's Smitten Strike: 60, +60 if this Pokémon and the opponent's Active Pokémon
/// have 1 or more of the same type of Energy attached.
#[test]
fn test_smitten_strike_extra_damage_with_shared_energy_type() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3b033Enamorus).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
        ],
        vec![sponge().with_energy(vec![EnergyType::Water, EnergyType::Psychic])],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3b033Enamorus, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 60,
        "Smitten Strike should deal 120 with a shared Energy type"
    );
}

/// Negative: no Energy type in common between the two Actives → base 60 only.
#[test]
fn test_smitten_strike_base_damage_without_shared_energy_type() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3b033Enamorus).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
        ],
        vec![sponge().with_energy(vec![EnergyType::Water])],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3b033Enamorus, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 120,
        "Smitten Strike should deal 60 without a shared Energy type"
    );
}

/// Scrafty's Crush the Weak: 50, +50 if this Pokémon has more Energy attached than the
/// opponent's Active Pokémon.
#[test]
fn test_crush_the_weak_extra_damage_with_more_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2107Scrafty).with_energy(vec![
            EnergyType::Darkness,
            EnergyType::Darkness,
            EnergyType::Darkness,
        ])],
        vec![sponge().with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2107Scrafty, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 80,
        "Crush the Weak should deal 100 with the Energy lead"
    );
}

/// Negative: equal Energy counts → base 50 only.
#[test]
fn test_crush_the_weak_base_damage_without_energy_lead() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2107Scrafty)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        vec![sponge().with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2107Scrafty, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 130,
        "Crush the Weak should deal 50 without the Energy lead"
    );
}

/// Grafaiai's Colorful Attack: 30, +60 if your Pokémon in play have 3 or more different
/// types of Energy attached (counted across the whole board, not just the Active).
#[test]
fn test_colorful_attack_extra_damage_with_three_energy_types_in_play() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2a070Grafaiai).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1211Snorlax).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1211Snorlax).with_energy(vec![EnergyType::Water]),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a070Grafaiai, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 90,
        "Colorful Attack should deal 90 with 3 Energy types across the board"
    );
}

/// Negative: fewer than 3 different Energy types in play → base 30 only.
#[test]
fn test_colorful_attack_base_damage_with_few_energy_types() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2a070Grafaiai).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1211Snorlax).with_energy(vec![EnergyType::Darkness]),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a070Grafaiai, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 150,
        "Colorful Attack should deal 30 with fewer than 3 Energy types"
    );
}
