use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Wishiwashi ex's School Storm: 30 damage plus 40 more for each of your Benched
/// Wishiwashi and Wishiwashi ex.
#[test]
fn test_school_storm_counts_benched_wishiwashi_and_wishiwashi_ex() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3051WishiwashiEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
            ]),
            PlayedCard::from_id(CardId::A3050Wishiwashi),
            PlayedCard::from_id(CardId::A3051WishiwashiEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3051WishiwashiEx, 0),
        is_stack: false,
    });

    // 30 base + 40 × 2 matching benched (Wishiwashi + Wishiwashi ex; Snorlax does not count)
    // = 110. Mega Latios ex: 180 - 110 = 70.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 70,
        "School Storm should deal 30 + 40 per benched Wishiwashi/Wishiwashi ex"
    );
}

/// Negative: with no Wishiwashi on the Bench, School Storm deals only its base 30.
#[test]
fn test_school_storm_base_damage_without_matching_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3051WishiwashiEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
            ]),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3051WishiwashiEx, 0),
        is_stack: false,
    });

    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 150,
        "School Storm should deal only 30 with no benched Wishiwashi"
    );
}

/// Nidoqueen's Lovestrike: 80 damage plus 50 more for each of your Benched Nidoking.
#[test]
fn test_lovestrike_counts_benched_nidoking() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1168Nidoqueen).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Darkness,
            ]),
            PlayedCard::from_id(CardId::A1171Nidoking),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1168Nidoqueen, 0),
        is_stack: false,
    });

    // 80 base + 50 × 1 benched Nidoking = 130. Mega Latios ex: 180 - 130 = 50.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 50,
        "Lovestrike should deal 80 + 50 per benched Nidoking"
    );
}

/// Negative: without a Benched Nidoking (a Nidoqueen does not count), Lovestrike deals 80.
#[test]
fn test_lovestrike_base_damage_without_nidoking() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1168Nidoqueen).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Darkness,
            ]),
            PlayedCard::from_id(CardId::A1168Nidoqueen),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1168Nidoqueen, 0),
        is_stack: false,
    });

    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 100,
        "Lovestrike should deal only 80 with no benched Nidoking"
    );
}
