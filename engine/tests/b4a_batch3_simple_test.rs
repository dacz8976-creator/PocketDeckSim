use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerType},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

fn attack(card_id: CardId, index: usize) -> Action {
    Action {
        actor: 0,
        action: attack_action(card_id, index),
        is_stack: false,
    }
}

fn tinkaton(card_id: CardId) -> PlayedCard {
    PlayedCard::from_id(card_id).with_energy(vec![
        EnergyType::Metal,
        EnergyType::Metal,
        EnergyType::Colorless,
    ])
}

fn sturdy_bulbasaur(energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::new(
        get_card_by_enum(CardId::A1001Bulbasaur),
        0,
        300,
        energy,
        false,
        vec![],
    )
}

fn has_attack(state: &deckgym::State, title: &str) -> bool {
    state.generate_possible_actions().1.iter().any(
        |action| matches!(&action.action, SimpleAction::Attack(attack) if attack.title == title),
    )
}

fn can_retreat_to(state: &deckgym::State, bench_idx: usize) -> bool {
    state
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(idx) if idx == bench_idx))
}

fn finish_retreat_choice(game: &mut Game<'static>) {
    let (_, payments) = game.get_state_clone().generate_possible_actions();
    if matches!(payments.first().map(|action| &action.action),
        Some(SimpleAction::ChooseRetreatEnergy { .. })) {
        assert!(payments.iter().all(|action| matches!(
            action.action, SimpleAction::ChooseRetreatEnergy { .. }
        )));
        game.apply_action(&payments[0]);
    }
}

#[test]
fn pile_driving_hammer_adds_two_to_attack_and_retreat_cost_for_both_printings() {
    for card_id in [
        CardId::B4a050TeamRocketsTinkaton,
        CardId::B4a075TeamRocketsTinkaton,
    ] {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![tinkaton(card_id)],
            vec![
                sturdy_bulbasaur(vec![
                    EnergyType::Grass,
                    EnergyType::Colorless,
                    EnergyType::Colorless,
                ]),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );

        game.apply_action(&attack(card_id, 0));
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_remaining_hp(), 220);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        });
        game.play_until_stable();

        assert!(
            !has_attack(&game.get_state_clone(), "Vine Whip"),
            "three Energy cannot pay Vine Whip's printed two plus the two-Colorless rider"
        );
        assert!(game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::Retreat(1))));

        game.apply_action(&Action {
            actor: 1,
            action: SimpleAction::Retreat(1),
            is_stack: false,
        });
        finish_retreat_choice(&mut game);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_name(), "Charmander");
        assert_eq!(
            state.in_play_pokemon[1][1]
                .as_ref()
                .expect("the former defender should be Benched")
                .attached_energy
                .len(),
            0,
            "printed retreat one plus the rider's two should discard all three Energy"
        );
    }
}

#[test]
fn pile_driving_hammer_riders_respect_crystal_body_and_clear_veil() {
    let protected = [
        (
            PlayedCard::from_id(CardId::A2034Regice)
                .with_energy(vec![EnergyType::Water, EnergyType::Water]),
            "Frost Smash",
            2,
        ),
        (
            sturdy_bulbasaur(vec![EnergyType::Grass, EnergyType::Colorless])
                .with_tool(get_card_by_enum(CardId::B4149ClearVeil)),
            "Vine Whip",
            1,
        ),
    ];

    for (defender, expected_attack, printed_retreat_cost) in protected {
        let hp_before = defender.get_remaining_hp();
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![tinkaton(CardId::B4a050TeamRocketsTinkaton)],
            vec![defender, PlayedCard::from_id(CardId::A1033Charmander)],
        );
        game.apply_action(&attack(CardId::B4a050TeamRocketsTinkaton, 0));
        let state = game.get_state_clone();
        assert!(
            state.get_active(1).get_remaining_hp() < hp_before,
            "damage still lands"
        );
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        });
        game.play_until_stable();
        assert!(
            has_attack(&game.get_state_clone(), expected_attack),
            "attack-effect immunity must reject the added attack cost"
        );
        assert!(
            can_retreat_to(&game.get_state_clone(), 1),
            "attack-effect immunity must reject the added retreat cost"
        );
        game.apply_action(&Action {
            actor: 1,
            action: SimpleAction::Retreat(1),
            is_stack: false,
        });
        finish_retreat_choice(&mut game);
        assert_eq!(
            game.get_state_clone().discard_energies[1].len(),
            printed_retreat_cost,
            "only the printed retreat cost should be paid"
        );
    }
}

#[test]
fn pile_driving_hammer_riders_expire_after_the_opponents_next_turn() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![tinkaton(CardId::B4a050TeamRocketsTinkaton)],
        vec![
            sturdy_bulbasaur(vec![
                EnergyType::Grass,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    game.apply_action(&attack(CardId::B4a050TeamRocketsTinkaton, 0));
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
    assert!(!has_attack(&game.get_state_clone(), "Vine Whip"));

    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state);
    assert!(
        has_attack(&game.get_state_clone(), "Vine Whip"),
        "the two-Colorless rider must be gone after the affected turn"
    );
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
        finish_retreat_choice(&mut game);
    assert_eq!(
        game.get_state_clone().discard_energies[1].len(),
        1,
        "only Bulbasaur's printed retreat cost remains after expiry"
    );
}

#[test]
fn pile_driving_hammer_riders_clear_when_defender_retreats_and_stay_gone_when_repromoted() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![tinkaton(CardId::B4a050TeamRocketsTinkaton)],
        vec![
            sturdy_bulbasaur(vec![
                EnergyType::Grass,
                EnergyType::Grass,
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    game.apply_action(&attack(CardId::B4a050TeamRocketsTinkaton, 0));
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
        finish_retreat_choice(&mut game);

    let mut state = game.get_state_clone();
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .expect("the former defender should be Benched")
            .attached_energy
            .len(),
        2,
        "the active rider made the retreat consume printed one plus two more Energy"
    );
    state.in_play_pokemon[1].swap(0, 1);
    state.current_player = 1;
    game.set_state(state);
    assert!(
        has_attack(&game.get_state_clone(), "Vine Whip"),
        "the re-promoted Pokémon must not regain the cleared attack-cost rider"
    );
}

fn slowpoke_game(seed: u64, discard: Vec<Card>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B4a025TeamRocketsSlowpoke)
            .with_energy(vec![EnergyType::Psychic])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.discard_piles[0] = discard;
    game.set_state(state);
    game
}

#[test]
fn scavenge_randomly_recovers_only_items_and_exposes_both_candidates() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let poke_ball = get_card_by_enum(CardId::PA005PokeBall);
    let supporter = get_card_by_enum(CardId::A2152Cynthia);
    let tool = get_card_by_enum(CardId::A2147GiantCape);
    let mut saw_potion = false;
    let mut saw_poke_ball = false;

    for seed in 0..80 {
        let mut game = slowpoke_game(
            seed,
            vec![
                potion.clone(),
                supporter.clone(),
                poke_ball.clone(),
                tool.clone(),
            ],
        );
        game.apply_action(&attack(CardId::B4a025TeamRocketsSlowpoke, 0));
        let state = game.get_state_clone();
        assert_eq!(state.hands[0].len(), 1);
        let recovered = &state.hands[0][0];
        assert!(matches!(recovered, Card::Trainer(t) if t.trainer_card_type == TrainerType::Item));
        saw_potion |= recovered == &potion;
        saw_poke_ball |= recovered == &poke_ball;
        assert!(state.discard_piles[0].contains(&supporter));
        assert!(state.discard_piles[0].contains(&tool));
    }
    assert!(saw_potion && saw_poke_ball);
}

#[test]
fn scavenge_with_no_item_is_an_effect_only_noop() {
    let supporter = get_card_by_enum(CardId::A2152Cynthia);
    let mut game = slowpoke_game(0, vec![supporter.clone()]);
    game.apply_action(&attack(CardId::B4a025TeamRocketsSlowpoke, 0));
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.discard_piles[0], vec![supporter]);
}

#[test]
fn scavenge_follows_existing_put_into_hand_policy_above_the_draw_cap() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let mut game = slowpoke_game(0, vec![potion.clone()]);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur); 10];
    game.set_state(state);

    game.apply_action(&attack(CardId::B4a025TeamRocketsSlowpoke, 0));
    let state = game.get_state_clone();
    assert_eq!(state.hands[0].len(), 11);
    assert!(!state.discard_piles[0].contains(&potion));
}

#[test]
fn scavenge_does_not_consume_the_defenders_first_damage_shield() {
    let mut game = slowpoke_game(0, vec![get_card_by_enum(CardId::PA001Potion)]);
    let mut state = game.get_state_clone();
    state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B2073MimikyuEx));
    game.set_state(state);
    game.apply_action(&attack(CardId::B4a025TeamRocketsSlowpoke, 0));
    assert!(
        !game
            .get_state_clone()
            .get_active(1)
            .prevent_first_attack_damage_used
    );
}

#[test]
fn copied_scavenge_recovers_into_the_copying_players_hand() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Psychic,
        ])],
        vec![PlayedCard::from_id(CardId::B4a025TeamRocketsSlowpoke)],
    );
    let mut state = game.get_state_clone();
    state.hands = [vec![], vec![]];
    state.discard_piles[0] = vec![potion.clone()];
    game.set_state(state);

    game.apply_action(&attack(CardId::A1a032MewEx, 1));
    let copied = game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Scavenge"))
        .expect("Genome Hacking should offer Scavenge");
    game.apply_action(&copied);

    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![potion]);
    assert!(state.hands[1].is_empty());
}
