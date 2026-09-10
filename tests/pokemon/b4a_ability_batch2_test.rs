use std::collections::HashSet;

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::get_initialized_game,
};

fn evolve_from_hand(game: &mut deckgym::Game, evolution: CardId, in_play_idx: usize) {
    let card = get_card_by_enum(evolution);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![card.clone()];
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Evolve {
            evolution: card,
            in_play_idx,
            from_deck: false,
        },
        is_stack: false,
    });
}

fn choose_evolution_ability(game: &mut deckgym::Game, in_play_idx: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx },
        is_stack: true,
    });
}

#[test]
fn regal_bloom_uses_effective_grass_energy_from_jungle_totem() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.turn_count = 3;
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B4a005Serperior)
                .with_energy(vec![EnergyType::Grass, EnergyType::Fire]),
            PlayedCard::from_id(CardId::A1a006Serperior),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.set_state(state);

    // One printed Grass counts twice under Jungle Totem. The Fire Energy contributes nothing.
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 160);
}

#[test]
fn boiler_smog_is_optional_and_applies_both_conditions() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.turn_count = 3;
    state.current_player = 0;
    state.set_board(
        vec![PlayedCard::from_id(CardId::B4a042TeamRocketsKoffing)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.set_state(state);

    evolve_from_hand(&mut game, CardId::B4a043TeamRocketsWeezingEx, 0);
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Noop)));
    assert!(choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::UseAbility { in_play_idx: 0 })));

    choose_evolution_ability(&mut game, 0);
    let state = game.get_state_clone();
    assert!(state.get_active(1).is_poisoned());
    assert!(state.get_active(1).is_burned());
}

#[test]
fn boiler_smog_uses_ability_status_rules() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.turn_count = 3;
    state.current_player = 0;
    state.set_board(
        vec![PlayedCard::from_id(CardId::B4a042TeamRocketsKoffing)],
        vec![PlayedCard::from_id(CardId::A2a071ArceusEx)],
    );
    game.set_state(state);

    evolve_from_hand(&mut game, CardId::B4a043TeamRocketsWeezingEx, 0);
    choose_evolution_ability(&mut game, 0);
    let state = game.get_state_clone();
    assert!(!state.get_active(1).is_poisoned());
    assert!(!state.get_active(1).is_burned());
}

#[test]
fn thieving_incisors_is_optional_and_not_offered_without_energy() {
    for energies in [vec![EnergyType::Water], vec![]] {
        let mut game = get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.turn_count = 3;
        state.current_player = 0;
        state.set_board(
            vec![PlayedCard::from_id(CardId::B4a058TeamRocketsRattata)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(energies.clone())],
        );
        game.set_state(state);
        evolve_from_hand(&mut game, CardId::B4a059TeamRocketsRaticateEx, 0);

        let (_, choices) = game.get_state_clone().generate_possible_actions();
        let offered = choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::UseAbility { in_play_idx: 0 }));
        assert_eq!(offered, !energies.is_empty());
        if !energies.is_empty() {
            assert!(choices
                .iter()
                .any(|choice| matches!(choice.action, SimpleAction::Noop)));
        }
    }
}

#[test]
fn thieving_incisors_samples_all_eligible_energy_types() {
    let mut observed = HashSet::new();
    for seed in 0..64 {
        let mut game = get_initialized_game(seed);
        let mut state = game.get_state_clone();
        state.turn_count = 3;
        state.current_player = 0;
        state.set_board(
            vec![PlayedCard::from_id(CardId::B4a058TeamRocketsRattata)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Fire])],
        );
        game.set_state(state);
        evolve_from_hand(&mut game, CardId::B4a059TeamRocketsRaticateEx, 0);
        choose_evolution_ability(&mut game, 0);

        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy.len(), 1);
        assert_eq!(state.get_active(1).attached_energy.len(), 1);
        observed.insert(state.get_active(0).attached_energy[0]);
    }
    assert_eq!(
        observed,
        HashSet::from([EnergyType::Grass, EnergyType::Fire])
    );
}

#[test]
fn energy_heist_refreshes_regal_bloom_hp_and_knockout() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.turn_count = 3;
    state.current_player = 0;
    state.set_board(
        vec![PlayedCard::from_id(CardId::B4a058TeamRocketsRattata)],
        vec![
            PlayedCard::from_id(CardId::B4a005Serperior)
                .with_energy(vec![EnergyType::Grass])
                .with_damage(130),
            PlayedCard::from_id(CardId::A1a006Serperior),
        ],
    );
    game.set_state(state);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 30);

    evolve_from_hand(&mut game, CardId::B4a059TeamRocketsRaticateEx, 0);
    choose_evolution_ability(&mut game, 0);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_id() == "B4a 005"));
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Grass]);
}

#[test]
fn b4a_reprints_share_exact_effect_mappings() {
    for id in [
        CardId::B4a043TeamRocketsWeezingEx,
        CardId::B4a083TeamRocketsWeezingEx,
        CardId::B4a092TeamRocketsWeezingEx,
        CardId::B4a059TeamRocketsRaticateEx,
        CardId::B4a084TeamRocketsRaticateEx,
        CardId::B4a093TeamRocketsRaticateEx,
    ] {
        let card = get_card_by_enum(id);
        let Card::Pokemon(pokemon) = card else {
            panic!("target should be a Pokémon")
        };
        let effect = &pokemon.ability.as_ref().expect("target has ability").effect;
        assert!(deckgym::actions::ability_mechanic_from_effect(effect).is_some());
    }
}
