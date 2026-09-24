//! Focused public-leaf regressions for consumed threat-clock targets and effective retreat cost.
//!
//! These tests isolate one coefficient at a time through the public parametric evaluator. They
//! check feature arithmetic and legal mobility, not action quality or win rate.

use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    players::value_functions::{parametric_value_function_ex5, ValueFunctionParams},
    State,
};

const ZERO: ValueFunctionParams = ValueFunctionParams {
    points: 0.0,
    pokemon_value: 0.0,
    hand_size: 0.0,
    deck_size: 0.0,
    active_retreat_cost: 0.0,
    active_pokemon_online_score: 0.0,
    active_safety: 0.0,
    active_has_tool: 0.0,
    is_winner: 0.0,
    turns_until_opponent_wins: 0.0,
    online_pokemon_count: 0.0,
    energy_distance_to_online: 0.0,
    opponent_discard_size: 0.0,
};

fn ready_ivysaur(remaining_hp: u32) -> PlayedCard {
    PlayedCard::from_id(CardId::A1002Ivysaur)
        .with_remaining_hp(remaining_hp)
        .with_energy(vec![
            EnergyType::Grass,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])
}

fn clock_state(owner_bench_hp: &[u32], points: [u8; 2]) -> State {
    let mut owner = vec![ready_ivysaur(60)];
    owner.extend(owner_bench_hp.iter().copied().map(ready_ivysaur));

    let mut state = State::default();
    state.current_player = 0;
    state.turn_count = 3;
    state.points = points;
    state.set_board(owner, vec![ready_ivysaur(60)]);
    state
}

fn clock_only(state: &State, public_evaluation: bool, clock_aware: bool) -> f64 {
    let params = ValueFunctionParams {
        turns_until_opponent_wins: 1.0,
        ..ZERO
    };
    parametric_value_function_ex5(
        state,
        0,
        &params,
        public_evaluation,
        false,
        clock_aware,
        false,
        false,
    )
}

fn retreat_only(state: &State, myself: usize, public_evaluation: bool) -> f64 {
    let params = ValueFunctionParams {
        active_retreat_cost: 1.0,
        ..ZERO
    };
    parametric_value_function_ex5(
        state,
        myself,
        &params,
        public_evaluation,
        false,
        false,
        false,
        false,
    )
}

fn pokemon_only(state: &State, myself: usize) -> f64 {
    let params = ValueFunctionParams {
        pokemon_value: 1.0,
        ..ZERO
    };
    parametric_value_function_ex5(state, myself, &params, true, false, false, false, false)
}

fn has_retreat_action(state: &State) -> bool {
    let (_, actions) = state.generate_possible_actions();
    actions
        .iter()
        .any(|action| matches!(&action.action, SimpleAction::Retreat(_)))
}

#[test]
fn public_clock_consumes_each_bench_slot_once_and_private_clock_is_unchanged() {
    for clock_aware in [false, true] {
        let one_bench = clock_state(&[60], [0, 0]);
        assert_eq!(
            clock_only(&one_bench, true, clock_aware),
            1.0,
            "public clock: owner survives Active+Bench for 2 turns; opponent survives Active for 1"
        );
        assert_eq!(
            clock_only(&one_bench, false, clock_aware),
            2.0,
            "private compatibility path retains the historical repeated-Bench arithmetic"
        );

        let mut opponent_one_bench = one_bench.clone();
        opponent_one_bench.in_play_pokemon.swap(0, 1);
        assert_eq!(
            clock_only(&opponent_one_bench, true, clock_aware),
            -1.0,
            "public consumption also applies to the opposing feature extraction"
        );
        assert_eq!(
            clock_only(&opponent_one_bench, false, clock_aware),
            -2.0,
            "private opposing extraction also retains historical repetition"
        );

        let distinct_benches = clock_state(&[60, 90], [0, 0]);
        assert_eq!(
            clock_only(&distinct_benches, true, clock_aware),
            3.0,
            "public clock must count the 90-HP and 60-HP Bench cards once each: 4 minus 1"
        );
        assert_eq!(
            clock_only(&distinct_benches, false, clock_aware),
            4.0,
            "private clock retains repetition of the safest 90-HP Bench: 5 minus 1"
        );
    }
}

#[test]
fn clock_stops_at_no_pokemon_or_the_score_threshold() {
    for clock_aware in [false, true] {
        for public_evaluation in [false, true] {
            assert_eq!(
                clock_only(&clock_state(&[], [0, 0]), public_evaluation, clock_aware),
                0.0,
                "one ready 60-HP Active on each side gives symmetric one-turn clocks"
            );
            assert_eq!(
                clock_only(
                    &clock_state(&[60], [0, 2]),
                    public_evaluation,
                    clock_aware,
                ),
                0.0,
                "at two points the first Active knockout reaches the threshold before Bench logic"
            );
        }
    }
}

#[test]
fn public_retreat_feature_uses_effective_cost_while_private_keeps_printed_cost() {
    let mut balloon = State::default();
    balloon.current_player = 0;
    balloon.turn_count = 3;
    balloon.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_tool(get_card_by_enum(CardId::B3b064SmallBalloon)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut plain_bulbasaur = balloon.clone();
    plain_bulbasaur.in_play_pokemon[0][0]
        .as_mut()
        .unwrap()
        .attached_tools
        .clear();
    assert!(!has_retreat_action(&plain_bulbasaur));
    assert_eq!(retreat_only(&plain_bulbasaur, 0, true), -1.0);
    assert!(has_retreat_action(&balloon));
    assert_eq!(retreat_only(&balloon, 0, true), 0.0);
    assert_eq!(retreat_only(&balloon, 0, false), -1.0);

    let mut plaza = State::default();
    plaza.current_player = 0;
    plaza.turn_count = 3;
    plaza.active_stadium = Some(get_card_by_enum(CardId::B2155PeculiarPlaza));
    plaza.active_stadium_owner = Some(1);
    plaza.set_board(
        vec![
            PlayedCard::from_id(CardId::A1128Mewtwo),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut plain_mewtwo = plaza.clone();
    plain_mewtwo.active_stadium = None;
    plain_mewtwo.active_stadium_owner = None;
    assert!(!has_retreat_action(&plain_mewtwo));
    assert_eq!(retreat_only(&plain_mewtwo, 0, true), -2.0);
    assert!(has_retreat_action(&plaza));
    assert_eq!(retreat_only(&plaza, 0, true), 0.0);
    assert_eq!(retreat_only(&plaza, 0, false), -2.0);

    // The holder is player 0 while player 1 owns the turn. Sky Support only exists on player 0's
    // Bench, so this catches accidental use of state.current_player when resolving "your" board.
    let mut off_turn_holder = State::default();
    off_turn_holder.current_player = 1;
    off_turn_holder.turn_count = 4;
    off_turn_holder.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A2a069Shaymin),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    assert_eq!(retreat_only(&off_turn_holder, 0, true), 0.0);
    assert_eq!(retreat_only(&off_turn_holder, 0, false), -1.0);
}

#[test]
fn concealed_setup_leaf_scores_only_the_evaluating_players_board() {
    fn setup_state(own: CardId, concealed_opponent: CardId) -> State {
        let mut state = State::default();
        state.current_player = 0;
        state.turn_count = 0;
        state.setup_opponent_hidden = true;
        state.set_board(
            vec![PlayedCard::from_id(own)],
            vec![PlayedCard::from_id(concealed_opponent)],
        );
        state
    }

    let bulbasaur_a = setup_state(CardId::A1001Bulbasaur, CardId::A1033Charmander);
    let bulbasaur_b = setup_state(CardId::A1001Bulbasaur, CardId::A1002Ivysaur);
    assert_eq!(pokemon_only(&bulbasaur_a, 0), 70.0);
    assert_eq!(
        pokemon_only(&bulbasaur_a, 0),
        pokemon_only(&bulbasaur_b, 0),
        "substituting a concealed opposing setup card must not change the public leaf"
    );

    let own_ivysaur = setup_state(CardId::A1002Ivysaur, CardId::A1033Charmander);
    assert_eq!(pokemon_only(&own_ivysaur, 0), 90.0);
    assert_ne!(
        pokemon_only(&bulbasaur_a, 0),
        pokemon_only(&own_ivysaur, 0),
        "the evaluating player's own setup board remains a priced input"
    );

    fn setup_retreat_state(concealed_opponent: CardId, own_shaymin: bool) -> State {
        let mut own = vec![PlayedCard::from_id(CardId::A1001Bulbasaur)];
        if own_shaymin {
            own.push(PlayedCard::from_id(CardId::A2a069Shaymin));
        }
        let mut state = State::default();
        state.current_player = 0;
        state.turn_count = 0;
        state.setup_opponent_hidden = true;
        state.set_board(own, vec![PlayedCard::from_id(concealed_opponent)]);
        state
    }

    let concealed_charmander = setup_retreat_state(CardId::A1033Charmander, false);
    let concealed_ariados = setup_retreat_state(CardId::B1a006Ariados, false);
    assert_eq!(retreat_only(&concealed_charmander, 0, true), -1.0);
    assert_eq!(
        retreat_only(&concealed_ariados, 0, true),
        -1.0,
        "concealed Trap Territory must not add to the setup leaf's retreat cost"
    );

    let own_shaymin = setup_retreat_state(CardId::B1a006Ariados, true);
    assert_eq!(
        retreat_only(&own_shaymin, 0, true),
        0.0,
        "masking the opponent must retain own-board Sky Support"
    );
}
