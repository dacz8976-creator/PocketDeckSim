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

#[test]
fn test_oricorio_kindle_discards_random_energy_from_both_actives() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3034Oricorio)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire])],
        vec![sponge().with_energy(vec![EnergyType::Water, EnergyType::Psychic])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3034Oricorio, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy.len(),
        1,
        "Kindle should discard 1 random Energy from the attacker"
    );
    assert_eq!(
        state.get_active(1).attached_energy.len(),
        1,
        "Kindle should discard 1 random Energy from the defender"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180 - 40,
        "Kindle should deal its printed 40 damage"
    );
}

#[test]
fn test_dedenne_electric_nibbling_discards_lightning_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1094Dedenne).with_energy(vec![EnergyType::Colorless])],
        vec![sponge().with_energy(vec![EnergyType::Lightning, EnergyType::Grass])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1094Dedenne, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).attached_energy,
        vec![EnergyType::Grass],
        "Electric Nibbling should discard exactly the [L] Energy"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 20);
}

#[test]
fn test_dedenne_electric_nibbling_does_nothing_without_lightning_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1094Dedenne).with_energy(vec![EnergyType::Colorless])],
        vec![sponge().with_energy(vec![EnergyType::Grass])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1094Dedenne, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).attached_energy,
        vec![EnergyType::Grass],
        "Without a [L] Energy attached nothing should be discarded"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 20);
}

#[test]
fn test_surskit_firefighting_discards_fire_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3009Surskit).with_energy(vec![EnergyType::Colorless])],
        vec![sponge().with_energy(vec![EnergyType::Fire])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3009Surskit, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.get_active(1).attached_energy.is_empty(),
        "Firefighting should discard the [R] Energy"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 10);
}

#[test]
fn test_giratina_crisis_dive_discards_two_random_self_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2a061Giratina).with_energy(vec![
                EnergyType::Grass,
                EnergyType::Psychic,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2a061Giratina, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy.len(),
        1,
        "Crisis Dive should discard 2 random Energy from the attacker"
    );
    assert_eq!(state.discard_energies[0].len(), 2);
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 120);
}

#[test]
fn test_koraidon_rampaging_fang_discards_two_fighting() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2a063Koraidon).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a063Koraidon, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Colorless, EnergyType::Colorless],
        "Rampaging Fang should discard 2 [F] Energy"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 120);
}

#[test]
fn test_single_strike_urshifu_power_blast_discards_one_darkness() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3113SingleStrikeUrshifu).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3113SingleStrikeUrshifu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let mut remaining = state.get_active(0).attached_energy.clone();
    remaining.sort_by_key(|e| format!("{e:?}"));
    assert_eq!(
        remaining,
        vec![EnergyType::Colorless, EnergyType::Darkness],
        "Power Blast should discard exactly one [D] Energy"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 110);
}

#[test]
fn test_groudon_gaia_blast_discards_two_from_own_side_only() {
    for seed in 0..20 {
        let mut game = deckgym::test_support::get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::B2b035Groudon).with_energy(vec![
                    EnergyType::Fighting,
                    EnergyType::Fighting,
                    EnergyType::Colorless,
                    EnergyType::Colorless,
                ]),
                PlayedCard::from_id(CardId::A1001Bulbasaur)
                    .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
            ],
            vec![sponge().with_energy(vec![EnergyType::Water, EnergyType::Water])],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B2b035Groudon, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        let own_total: usize = state
            .enumerate_in_play_pokemon(0)
            .map(|(_, p)| p.attached_energy.len())
            .sum();
        assert_eq!(
            own_total, 4,
            "Seed {seed}: Gaia Blast should discard 2 random Energy from among your own Pokémon"
        );
        assert_eq!(
            state.get_active(1).attached_energy.len(),
            2,
            "Seed {seed}: the opponent's Energy must never be touched"
        );
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 130);
    }
}

#[test]
fn test_aurorus_hail_prison_discards_two_water_and_paralyzes() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2042Aurorus).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Colorless,
        ])],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2042Aurorus, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Colorless],
        "Hail Prison should discard 2 [W] Energy from the attacker"
    );
    assert!(
        state.get_active(1).is_paralyzed(),
        "Hail Prison should paralyze the opponent's Active Pokémon"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 90);
}

#[test]
fn test_galvantula_electric_shock_discards_all_energy_and_paralyzes() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3b027Galvantula).with_energy(vec![
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3b027Galvantula, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.get_active(0).attached_energy.is_empty(),
        "Electric Shock should discard all Energy from the attacker"
    );
    assert!(state.get_active(1).is_paralyzed());
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 70);
}
