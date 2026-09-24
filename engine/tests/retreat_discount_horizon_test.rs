//! Public-leaf horizon controls for temporary retreat discounts.
//!
//! X Speed and Leaf still reduce the legal Retreat Cost during their turn. The public static
//! leaf prices the board after a cutoff, though, so it must not treat an unused turn effect as a
//! retained asset. These fixtures cover both the waste boundary and a line where X Speed enables
//! a real retreat and an immediate win.

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    observation::{canonical_actions, PlayerObservation, RevealedKnowledge},
    players::{
        public_clock_effect_value_function,
        value_functions::{parametric_value_function_ex5, ValueFunctionParams},
        ExpectiMiniMaxPlayer, Player,
    },
    state::GameOutcome,
    Deck, State,
};
use rand::{rngs::StdRng, SeedableRng};

const RETREAT_ONLY: ValueFunctionParams = ValueFunctionParams {
    points: 0.0,
    pokemon_value: 0.0,
    hand_size: 0.0,
    deck_size: 0.0,
    active_retreat_cost: 1.0,
    active_pokemon_online_score: 0.0,
    active_safety: 0.0,
    active_has_tool: 0.0,
    is_winner: 0.0,
    turns_until_opponent_wins: 0.0,
    online_pokemon_count: 0.0,
    energy_distance_to_online: 0.0,
    opponent_discard_size: 0.0,
};

fn public_retreat_value(state: &State) -> f64 {
    parametric_value_function_ex5(
        state,
        0,
        &RETREAT_ONLY,
        true,
        false,
        false,
        false,
        false,
    )
}

fn actions(state: &State) -> Vec<Action> {
    let (actor, mut actions) = state.generate_possible_actions();
    assert_eq!(actor, state.current_player);
    canonical_actions(&mut actions);
    actions
}

fn is_x_speed(action: &Action) -> bool {
    matches!(
        &action.action,
        SimpleAction::Play { trainer_card } if trainer_card.id == "P-A 002"
    )
}

fn apply_exact(state: &mut State, action: &Action) {
    assert!(state.generate_possible_actions().1.contains(action));
    let (probabilities, mutations) = try_forecast_action(state, action)
        .expect("fixture action should have an exact forecast")
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    mutations.into_iter().next().unwrap()(
        &mut StdRng::seed_from_u64(47),
        state,
        action,
    );
}

fn choose(state: &State, depth: usize) -> Action {
    let offered = actions(state);
    let observation = PlayerObservation::from_state(state, 0, &RevealedKnowledge::default());
    let mut player = ExpectiMiniMaxPlayer {
        deck: Deck::default(),
        max_depth: depth,
        write_debug_trees: false,
        value_function: Box::new(public_clock_effect_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    };
    let chosen = player.decision_fn(
        &mut StdRng::seed_from_u64(91),
        &observation,
        &offered,
    );
    assert!(offered.contains(&chosen));
    chosen
}

fn base_state(owner_board: Vec<PlayedCard>) -> State {
    let mut state = State::default();
    state.current_player = 0;
    state.turn_count = 7;
    state.set_board(
        owner_board,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.hands = [vec![get_card_by_enum(CardId::PA002XSpeed)], vec![]];
    state.decks[0].cards.clear();
    state.decks[1].cards.clear();
    state.energy_zone[0].current = None;
    state.energy_zone[0].next = None;
    state.energy_zone[1].current = None;
    state.energy_zone[1].next = None;
    state
}

#[test]
fn unused_x_speed_cannot_improve_a_public_leaf_or_displace_end_turn() {
    let state = base_state(vec![PlayedCard::from_id(CardId::A1128Mewtwo)]);
    let initial_actions = actions(&state);
    assert!(initial_actions.iter().any(is_x_speed));
    assert!(initial_actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::EndTurn)));
    assert!(!initial_actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_))));
    assert_eq!(public_clock_effect_value_function(&state, 0), 99.0);
    assert_eq!(public_retreat_value(&state), -2.0);

    let x_speed = initial_actions.iter().find(|action| is_x_speed(action)).unwrap();
    let mut after_x_speed = state.clone();
    apply_exact(&mut after_x_speed, x_speed);

    assert!(!actions(&after_x_speed)
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_))));
    assert_eq!(
        public_retreat_value(&after_x_speed),
        public_retreat_value(&state),
        "an unused current-turn discount is not a lasting board improvement"
    );
    assert_eq!(
        public_clock_effect_value_function(&after_x_speed, 0),
        98.0,
        "playing X Speed loses its hand-card point when no retreat realizes the effect"
    );

    for depth in [1, 2, 3] {
        let chosen = choose(&state, depth);
        assert!(
            matches!(chosen.action, SimpleAction::EndTurn),
            "depth {depth} should retain the unusable X Speed, got {chosen:?}"
        );
    }
}

#[test]
fn necessary_x_speed_retreat_attack_win_remains_visible_at_depth_three() {
    let mut state = base_state(vec![
        PlayedCard::from_id(CardId::A1128Mewtwo)
            .with_energy(vec![EnergyType::Psychic]),
        PlayedCard::from_id(CardId::A1198Farfetchd)
            .with_energy(vec![EnergyType::Psychic]),
    ]);
    state.in_play_pokemon[1][0] = Some(
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30),
    );
    state.points = [2, 0];

    let initial_actions = actions(&state);
    assert!(initial_actions.iter().any(is_x_speed));
    assert!(!initial_actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_))));
    assert!(!initial_actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Attack(_))));
    let chosen = choose(&state, 3);
    assert!(is_x_speed(&chosen), "depth-three win must begin with X Speed: {chosen:?}");

    let mut line = state.clone();
    apply_exact(&mut line, &chosen);
    assert_eq!(public_retreat_value(&line), -2.0);

    let after_item = actions(&line);
    let retreat = after_item
        .iter()
        .find(|action| matches!(action.action, SimpleAction::Retreat(1)))
        .expect("X Speed must make the one-Energy retreat legal")
        .clone();
    apply_exact(&mut line, &retreat);
    assert_eq!(line.get_active(0).get_id(), "A1 198");
    assert_eq!(line.discard_energies[0], vec![EnergyType::Psychic]);

    let after_retreat = actions(&line);
    let attack = after_retreat
        .iter()
        .find(|action| matches!(action.action, SimpleAction::Attack(_)))
        .expect("Farfetch'd must have its one-Energy attack ready")
        .clone();
    apply_exact(&mut line, &attack);

    assert_eq!(line.points, [3, 0]);
    assert_eq!(line.winner, Some(GameOutcome::Win(0)));
}
