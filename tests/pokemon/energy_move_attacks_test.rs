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

#[test]
fn test_swanna_feathery_cyclone_moves_all_energy_to_chosen_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4063Swanna)
                .with_energy(vec![EnergyType::Water, EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4063Swanna, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);

    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|c| matches!(c.action, SimpleAction::MoveEnergies { .. })));
    game.apply_action(&choices[0]);

    let state = game.get_state_clone();
    assert!(
        state.get_active(0).attached_energy.is_empty(),
        "All Energy should have moved off Swanna"
    );
    let bench = state.in_play_pokemon[0][1].as_ref().unwrap();
    let mut moved = bench.attached_energy.clone();
    moved.sort_by_key(|e| format!("{e:?}"));
    assert_eq!(
        moved,
        vec![EnergyType::Grass, EnergyType::Water],
        "The mixed-type Energy set should land on the chosen benched Pokémon"
    );
}

#[test]
fn test_swanna_feathery_cyclone_without_bench_keeps_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4063Swanna)
            .with_energy(vec![EnergyType::Water, EnergyType::Grass])],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4063Swanna, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy.len(),
        2,
        "Without a benched Pokémon the Energy stays put"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
    let (_, choices) = state.generate_possible_actions();
    assert!(choices
        .iter()
        .all(|c| !matches!(c.action, SimpleAction::MoveEnergies { .. })));
}

#[test]
fn test_regice_reflect_energy_moves_two_random_energy_to_chosen_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3045Regice).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3045Regice, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 70);

    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|c| matches!(c.action, SimpleAction::MoveEnergies { .. })));
    game.apply_action(&choices[0]);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy.len(),
        1,
        "2 of Regice's 3 Energy should have moved"
    );
    let bench = state.in_play_pokemon[0][1].as_ref().unwrap();
    assert_eq!(bench.attached_energy.len(), 2);
}
