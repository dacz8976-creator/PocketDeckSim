use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{
        get_implementation_status, implementation_limitations, ImplementationStatus,
    },
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};
use rand::{rngs::StdRng, SeedableRng};
use std::{
    collections::hash_map::DefaultHasher,
    hash::{Hash, Hasher},
};

fn basculegion() -> PlayedCard {
    PlayedCard::from_id(CardId::B4a018HisuianBasculegion)
        .with_energy(vec![EnergyType::Water, EnergyType::Water])
}

fn soul_counter_damage(
    opponent_lifetime_points: u8,
    opponent_last_own_turn_points: u8,
    opponent_points_this_turn: u8,
) -> u32 {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![basculegion()],
        vec![PlayedCard::from_id(CardId::B4037WailordEx)],
    );
    let mut state = game.get_state_clone();
    state.points[1] = opponent_lifetime_points;
    state.points_gained_during_own_last_turn[1] = opponent_last_own_turn_points;
    state.points_gained_this_turn[1] = opponent_points_this_turn;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B4a018HisuianBasculegion, 0),
        is_stack: false,
    });

    250 - game.get_state_clone().get_active(1).get_remaining_hp()
}

#[test]
fn soul_counter_counts_only_opponents_most_recent_own_turn_points() {
    assert_eq!(soul_counter_damage(0, 0, 0), 50);
    assert_eq!(soul_counter_damage(1, 1, 0), 100);
    assert_eq!(soul_counter_damage(2, 2, 0), 150);

    // Lifetime points and points received during the attacker's turn are not eligible.
    assert_eq!(soul_counter_damage(2, 0, 2), 50);
}

fn end_turn(game: &mut deckgym::Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
}

#[test]
fn checkup_points_are_banked_for_the_outgoing_turn_owner() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );

    end_turn(&mut game, 0);

    let state = game.get_state_clone();
    assert_eq!(state.points[0], 1);
    assert_eq!(state.points_gained_during_own_last_turn, [1, 0]);
    assert_eq!(state.points_gained_this_turn, [0, 0]);
}

#[test]
fn points_received_during_opponents_turn_do_not_replace_own_turn_history() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.points_gained_during_own_last_turn[1] = 2;
    game.set_state(state);

    end_turn(&mut game, 0);

    let state = game.get_state_clone();
    assert_eq!(state.points[1], 1);
    assert_eq!(state.points_gained_during_own_last_turn[1], 2);
    assert_eq!(state.points_gained_this_turn, [0, 0]);
}

#[test]
fn point_free_own_turn_overwrites_older_nonzero_history() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.points_gained_during_own_last_turn[0] = 2;
    game.set_state(state);

    end_turn(&mut game, 0);

    assert_eq!(
        game.get_state_clone().points_gained_during_own_last_turn[0],
        0
    );
}

fn play_iris_and_attack(seed: u64, defender: PlayedCard) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B2b056Haxorus).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Metal,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![defender, PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::B2b067Iris)];
    game.set_state(state);

    let (_, actions) = game.get_state_clone().generate_possible_actions();
    let play_iris = actions
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Iris")
        })
        .expect("Iris should be playable");
    game.apply_action(&play_iris);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b056Haxorus, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn ex_knockout_and_iris_bonus_both_enter_turn_ledger() {
    let state = play_iris_and_attack(
        0,
        PlayedCard::from_id(CardId::A1129MewtwoEx).with_remaining_hp(10),
    );
    assert_eq!(state.points[0], 3);
    assert_eq!(state.points_gained_this_turn[0], 3);
}

#[test]
fn point_denial_also_denies_iris_bonus_and_never_enters_ledger() {
    let mut denied = 0;
    let mut awarded = 0;
    for seed in 0..40 {
        let state = play_iris_and_attack(seed, PlayedCard::from_id(CardId::B3a045Glimmora));
        assert_eq!(state.points_gained_this_turn[0], state.points[0]);
        match state.points[0] {
            0 => denied += 1,
            2 => awarded += 1,
            other => {
                panic!("seed {seed}: expected full denial (0) or base + Iris (2), got {other}")
            }
        }
    }
    assert!(denied > 0, "the point-denial branch was never sampled");
    assert!(awarded > 0, "the point-award branch was never sampled");
}

fn hash(state: &State) -> u64 {
    let mut hasher = DefaultHasher::new();
    state.hash(&mut hasher);
    hasher.finish()
}

#[test]
fn history_is_serialized_public_and_part_of_state_identity() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![basculegion()],
        vec![PlayedCard::from_id(CardId::B4037WailordEx)],
    );
    let mut state = game.get_state_clone();
    state.points_gained_this_turn = [1, 0];
    state.points_gained_during_own_last_turn = [0, 2];
    game.set_state(state.clone());

    let observation = game.observation(0);
    assert_eq!(observation.visible_state().points_gained_this_turn, [1, 0]);
    assert_eq!(
        observation
            .visible_state()
            .points_gained_during_own_last_turn,
        [0, 2]
    );
    let searched = observation.search_state(&mut StdRng::seed_from_u64(7));
    assert_eq!(searched.points_gained_during_own_last_turn, [0, 2]);

    let round_trip: State = serde_json::from_str(&serde_json::to_string(&state).unwrap()).unwrap();
    assert_eq!(round_trip, state);

    let mut legacy = serde_json::to_value(&state).unwrap();
    let object = legacy.as_object_mut().unwrap();
    object.remove("points_gained_this_turn");
    object.remove("points_gained_during_own_last_turn");
    let restored: State = serde_json::from_value(legacy).unwrap();
    assert_eq!(restored.points_gained_this_turn, [0, 0]);
    assert_eq!(restored.points_gained_during_own_last_turn, [0, 0]);

    let mut different = state.clone();
    different.points_gained_during_own_last_turn[1] = 1;
    assert_ne!(different, state);
    assert_ne!(hash(&different), hash(&state));
}

#[test]
fn card_mapping_is_present_but_checkup_boundary_is_honestly_unverified() {
    let Card::Pokemon(card) = get_card_by_enum(CardId::B4a018HisuianBasculegion) else {
        panic!("B4a 018 should be a Pokémon");
    };
    assert_eq!(card.attacks[0].title, "Soul Counter");
    assert_eq!(
        card.attacks[0].effect.as_deref(),
        Some("This attack does 50 more damage for each point your opponent got during their last turn.")
    );
    assert_eq!(
        get_implementation_status(CardId::B4a018HisuianBasculegion),
        ImplementationStatus::RulesUnverified
    );
    let limitations = implementation_limitations(CardId::B4a018HisuianBasculegion);
    assert!(limitations
        .iter()
        .any(|note| note.contains("Pokémon Checkup")));
    assert!(limitations.iter().any(|note| note.contains("Legacy")));
}
