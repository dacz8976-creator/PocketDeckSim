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
fn test_sableye_jeweled_gift_attaches_random_basic_energy_to_chosen_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3a040Sableye).with_energy(vec![EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a040Sableye, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|c| matches!(c.action, SimpleAction::Attach { .. })));
    game.apply_action(&choices[0]);

    let state = game.get_state_clone();
    let bench = state.in_play_pokemon[0][1].as_ref().unwrap();
    assert_eq!(bench.attached_energy.len(), 1);
    assert!(
        BASIC_ENERGY_TYPES.contains(&bench.attached_energy[0]),
        "Jeweled Gift attaches one of the 8 basic Energy types, got {:?}",
        bench.attached_energy[0]
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "Jeweled Gift deals no damage"
    );
}

#[test]
fn test_sableye_jeweled_gift_without_bench_does_nothing() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a040Sableye).with_energy(vec![EnergyType::Colorless])],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a040Sableye, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let (_, choices) = state.generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|c| !matches!(c.action, SimpleAction::Attach { .. })),
        "No attach choice without a benched Pokémon"
    );
}

#[test]
fn test_uxie_mind_boost_attaches_psychic_to_mesprit_only() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2075Uxie).with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A2076Mesprit),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2075Uxie, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 20);

    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(
        choices.len(),
        1,
        "Only Mesprit is a legal Mind Boost target (not Charmander)"
    );
    assert!(matches!(choices[0].action, SimpleAction::Attach { .. }));
    game.apply_action(&choices[0]);

    let state = game.get_state_clone();
    let mesprit = state.in_play_pokemon[0][1].as_ref().unwrap();
    assert_eq!(mesprit.attached_energy, vec![EnergyType::Psychic]);
}

#[test]
fn test_uxie_mind_boost_without_named_targets_does_nothing() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2075Uxie).with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2075Uxie, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 20);
    let (_, choices) = state.generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|c| !matches!(c.action, SimpleAction::Attach { .. })),
        "No attach choice without Mesprit or Azelf in play"
    );
}

#[test]
fn test_mesprit_supreme_blast_usable_with_uxie_and_azelf_on_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2076Mesprit).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A2075Uxie),
            PlayedCard::from_id(CardId::A2077Azelf),
        ],
        vec![sponge()],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|c| matches!(c.action, SimpleAction::Attack(_))),
        "Supreme Blast should be offered with Uxie and Azelf on the Bench"
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2076Mesprit, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 160);
    assert!(
        state.get_active(0).attached_energy.is_empty(),
        "Supreme Blast discards all Energy from Mesprit"
    );
}

#[test]
fn test_mesprit_supreme_blast_not_offered_without_azelf() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2076Mesprit).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A2075Uxie),
        ],
        vec![sponge()],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .all(|c| !matches!(c.action, SimpleAction::Attack(_))),
        "Supreme Blast must not be offered without both Uxie and Azelf on the Bench"
    );
}
