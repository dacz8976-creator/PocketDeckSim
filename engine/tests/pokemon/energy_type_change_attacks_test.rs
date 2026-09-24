use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    // Mega Latios ex: 180 HP, no weakness — a safe damage sponge.
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

const BASIC_ENERGY_TYPES: [EnergyType; 8] = [
    EnergyType::Grass,
    EnergyType::Fire,
    EnergyType::Water,
    EnergyType::Lightning,
    EnergyType::Psychic,
    EnergyType::Fighting,
    EnergyType::Darkness,
    EnergyType::Metal,
];

#[test]
fn test_smeargle_splatter_coating_changes_random_energy_type() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4148Smeargle)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        // Colorless is not one of the 8 candidate types, so any change is observable.
        vec![sponge().with_energy(vec![EnergyType::Colorless])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4148Smeargle, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender_energy = &state.get_active(1).attached_energy;
    assert_eq!(defender_energy.len(), 1, "No Energy is added or removed");
    assert!(
        BASIC_ENERGY_TYPES.contains(&defender_energy[0]),
        "The Energy should now be one of the 8 basic types, got {:?}",
        defender_energy[0]
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50);
}

#[test]
fn test_smeargle_splatter_coating_without_energy_does_nothing_extra() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4148Smeargle)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4148Smeargle, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(state.get_active(1).attached_energy.is_empty());
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50);
}

#[test]
fn test_porygon_z_buggy_beam_changes_opponents_next_generated_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2129PorygonZ).with_energy(vec![
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])],
        vec![sponge()],
    );
    // Colorless is not one of the 8 candidate types, so the rewrite is observable.
    let mut state = game.get_state_clone();
    state.energy_zone[1].next = Some(EnergyType::Colorless);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2129PorygonZ, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let next = state.energy_zone[1]
        .next
        .expect("The opponent's next Energy should still be set");
    assert!(
        BASIC_ENERGY_TYPES.contains(&next),
        "Buggy Beam should set the opponent's next Energy to one of the 8 basic types, got {next:?}"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 80);
}
