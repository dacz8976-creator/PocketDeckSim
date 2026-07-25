use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::get_test_game_with_board,
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

fn count_energy(pokemon: &PlayedCard, energy_type: EnergyType) -> usize {
    pokemon
        .attached_energy
        .iter()
        .filter(|&&energy| energy == energy_type)
        .count()
}

/// Tyranitar's Energy Plunder: "Once during your turn, you may move all [D] Energy from each of
/// your Pokémon to this Pokémon."
///
/// "Each of your Pokémon" covers the whole board, and only [D] Energy moves — everything else
/// stays where it is.
#[test]
fn test_energy_plunder_pulls_all_darkness_energy_to_tyranitar() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4119Tyranitar).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Grass,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Fire]),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Energy Plunder should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    let tyranitar = state.in_play_pokemon[0][0].as_ref().expect("Tyranitar");
    let bulbasaur = state.in_play_pokemon[0][1].as_ref().expect("Bulbasaur");
    let charmander = state.in_play_pokemon[0][2].as_ref().expect("Charmander");

    assert_eq!(
        count_energy(tyranitar, EnergyType::Darkness),
        4,
        "Tyranitar should end up with every [D] Energy on the board (1 of its own + 3 taken)"
    );
    assert_eq!(count_energy(bulbasaur, EnergyType::Darkness), 0);
    assert_eq!(count_energy(charmander, EnergyType::Darkness), 0);

    // Non-Darkness Energy is untouched.
    assert_eq!(count_energy(bulbasaur, EnergyType::Grass), 1);
    assert_eq!(count_energy(charmander, EnergyType::Fire), 1);
    assert_eq!(count_energy(tyranitar, EnergyType::Grass), 0);
    assert_eq!(count_energy(tyranitar, EnergyType::Fire), 0);
}

/// The ability moves Energy to *this* Pokémon, which may be on the Bench — the destination is not
/// the Active Spot.
#[test]
fn test_energy_plunder_works_with_a_benched_tyranitar() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A4179Tyranitar).with_energy(vec![EnergyType::Darkness]),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 1).expect("Energy Plunder should be available from the Bench");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert_eq!(
        count_energy(
            state.in_play_pokemon[0][1].as_ref().expect("Tyranitar"),
            EnergyType::Darkness
        ),
        3,
        "the benched Tyranitar should collect the Active Pokémon's [D] Energy"
    );
    assert_eq!(
        count_energy(
            state.in_play_pokemon[0][0].as_ref().expect("Bulbasaur"),
            EnergyType::Darkness
        ),
        0
    );
}

/// NEGATIVE: with no [D] Energy anywhere else on the board the ability can only move Energy from
/// Tyranitar to itself, which is a no-op, so it must not be offered.
#[test]
fn test_energy_plunder_not_offered_without_darkness_energy_elsewhere() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4119Tyranitar).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Energy Plunder should not be offered when only Tyranitar itself holds [D] Energy"
    );
}

/// NEGATIVE: the opponent's [D] Energy is not "your Pokémon".
#[test]
fn test_energy_plunder_does_not_take_opponent_energy() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4119Tyranitar)],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Energy Plunder should ignore the opponent's [D] Energy entirely"
    );
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_energy_plunder_is_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4119Tyranitar),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Darkness]),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Energy Plunder should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Energy Plunder should not be usable twice in the same turn"
    );
}
