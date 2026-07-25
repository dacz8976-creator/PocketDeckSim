use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::get_test_game_with_board,
};

/// Puts Regigigas (fully powered for Giga Turbo) in the Active Spot behind `bench` and reports
/// whether the engine offers it an attack.
fn regigigas_can_attack(bench: [CardId; 3]) -> bool {
    let mut board = vec![
        PlayedCard::from_id(CardId::B3134Regigigas).with_energy(vec![
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ]),
    ];
    board.extend(bench.into_iter().map(PlayedCard::from_id));

    let game = get_test_game_with_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Attack(_)))
}

/// Regigigas (B3 134) "Seal of Antiquity": "If you don't have Regirock, Regice, and Registeel on
/// your Bench, this Pokémon can't attack."
#[test]
fn test_seal_of_antiquity_allows_attacking_with_the_full_regi_bench() {
    assert!(
        regigigas_can_attack([
            CardId::B3077Regirock,
            CardId::B3045Regice,
            CardId::B3116Registeel,
        ]),
        "with all three Regis on the Bench, Giga Turbo should be offered"
    );
}

/// Negative test: the condition is an *and*, so dropping any single Regi seals the attack away.
/// Bench order should not matter either, hence the swapped positions here.
#[test]
fn test_seal_of_antiquity_blocks_attacking_when_a_regi_is_missing() {
    assert!(
        !regigigas_can_attack([
            CardId::B3116Registeel,
            CardId::B3077Regirock,
            CardId::A1001Bulbasaur,
        ]),
        "without Regice on the Bench, Regigigas must not be offered an attack"
    );
    assert!(
        !regigigas_can_attack([
            CardId::B3045Regice,
            CardId::B3116Registeel,
            CardId::A1001Bulbasaur,
        ]),
        "without Regirock on the Bench, Regigigas must not be offered an attack"
    );
    assert!(
        !regigigas_can_attack([
            CardId::B3077Regirock,
            CardId::B3045Regice,
            CardId::A1001Bulbasaur,
        ]),
        "without Registeel on the Bench, Regigigas must not be offered an attack"
    );
}

/// The restriction is scoped to the Ability's holder: a Regigigas *on the Bench* does not stop the
/// Active Pokémon from attacking, and the Active Pokémon's own attacks are unaffected.
#[test]
fn test_seal_of_antiquity_only_restricts_its_own_holder() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1094Pikachu).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::B3134Regigigas),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Attack(_))),
        "a Benched Regigigas must not seal the Active Pokémon's attacks"
    );
}
