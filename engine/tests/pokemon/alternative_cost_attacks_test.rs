use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    // Mega Latios ex: 180 HP, no weakness — a safe damage sponge.
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

fn attack_offered(game: &deckgym::Game<'_>) -> bool {
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    choices
        .iter()
        .any(|c| matches!(c.action, SimpleAction::Attack(_)))
}

#[test]
fn test_boltund_defiant_spark_usable_for_one_lightning_when_damaged() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a031Boltund)
            .with_energy(vec![EnergyType::Lightning])
            .with_damage(10)],
        vec![sponge()],
    );

    assert!(
        attack_offered(&game),
        "With damage on it, Defiant Spark should be usable for 1 [L] Energy"
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a031Boltund, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 70);
}

#[test]
fn test_boltund_defiant_spark_not_offered_undamaged_with_one_energy() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a031Boltund).with_energy(vec![EnergyType::Lightning])],
        vec![sponge()],
    );

    assert!(
        !attack_offered(&game),
        "Undamaged, Defiant Spark still needs its printed [L][C][C] cost"
    );
}

#[test]
fn test_boltund_defiant_spark_printed_cost_still_works_undamaged() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a031Boltund).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])],
        vec![sponge()],
    );

    assert!(
        attack_offered(&game),
        "The printed cost path must be unaffected"
    );
}

#[test]
fn test_veluza_shedding_spiral_usable_for_one_water_with_empty_deck() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a031Veluza).with_energy(vec![EnergyType::Water])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards.clear();
    game.set_state(state);

    assert!(
        attack_offered(&game),
        "With no cards in the deck, Shedding Spiral should be usable for 1 [W] Energy"
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a031Veluza, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 90);
}

#[test]
fn test_veluza_shedding_spiral_not_offered_with_cards_in_deck() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2a031Veluza).with_energy(vec![EnergyType::Water])],
        vec![sponge()],
    );

    assert!(
        !attack_offered(&game),
        "With cards left in the deck, Shedding Spiral still needs its printed cost"
    );
}
