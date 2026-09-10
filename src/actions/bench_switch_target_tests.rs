use super::*;
use crate::{
    actions::{forecast_action, Action},
    card_ids::CardId,
    effects::TurnEffect,
    models::{EnergyType, PlayedCard},
};
use rand::{rngs::StdRng, SeedableRng};

fn state_with_boards(owner: Vec<PlayedCard>, opponent: Vec<PlayedCard>) -> State {
    let mut state = State::default();
    state.current_player = 0;
    state.turn_count = 9;
    state.set_board(owner, opponent);
    state.hands = [Vec::new(), Vec::new()];
    for player in 0..2 {
        state.decks[player].cards.clear();
        state.energy_zone[player].current = None;
        state.energy_zone[player].next = None;
    }
    state
}

fn apply_single(state: &mut State, action: &Action) {
    let (probabilities, mutations) = forecast_action(state, action).into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    mutations.into_iter().next().unwrap()(
        &mut StdRng::seed_from_u64(173),
        state,
        action,
    );
}

fn action_matching(state: &State, predicate: impl Fn(&SimpleAction) -> bool) -> Action {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| predicate(&action.action))
        .expect("expected generated action")
}

fn attack_by_title(state: &State, title: &str) -> Action {
    action_matching(state, |action| {
        matches!(action, SimpleAction::Attack(attack) if attack.title == title)
    })
}

fn activate(player: usize, in_play_idx: usize) -> SimpleAction {
    SimpleAction::Activate {
        player,
        in_play_idx,
    }
}

fn promote(player: usize, in_play_idx: usize) -> SimpleAction {
    SimpleAction::Promote {
        player,
        in_play_idx,
    }
}

fn breeze_by_fixture(fragile_bench_hp: u32) -> State {
    state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A4a003JumpluffEx)
                .with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1a017Magikarp)
                .with_remaining_hp(fragile_bench_hp),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::B2103Spiritomb),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    )
}

fn use_breeze_by(state: &mut State) {
    let attack = attack_by_title(state, "Breeze-By Attack");
    apply_single(state, &attack);
}

#[test]
fn final_scream_prunes_only_the_knocked_out_optional_switch_target() {
    let mut state = breeze_by_fixture(10);
    use_breeze_by(&mut state);

    assert_eq!(state.points, [1, 1]);
    assert_eq!(state.winner, None);
    assert_eq!(state.get_active(0).get_id(), "A4a 003");
    assert_eq!(state.get_active(0).get_remaining_hp(), 150);
    assert!(state.in_play_pokemon[0][1].is_none());
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .expect("Charmander survives Final Scream")
            .get_remaining_hp(),
        50
    );
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.move_generation_stack.len(), 2);
    assert_eq!(state.move_generation_stack[0], (1, vec![promote(1, 1)]));
    assert_eq!(
        state.move_generation_stack[1],
        (0, vec![activate(0, 2), SimpleAction::Noop])
    );
}

#[test]
fn retained_optional_switch_and_noop_each_expose_only_the_opponent_promotion() {
    let mut successor = breeze_by_fixture(10);
    use_breeze_by(&mut successor);

    let mut declined = successor.clone();
    let noop = action_matching(&declined, |action| matches!(action, SimpleAction::Noop));
    apply_single(&mut declined, &noop);
    assert_eq!(declined.get_active(0).get_id(), "A4a 003");
    assert_eq!(declined.move_generation_stack, vec![(1, vec![promote(1, 1)])]);

    let mut switched = successor;
    let switch = action_matching(&switched, |action| {
        matches!(action, SimpleAction::Activate { player: 0, in_play_idx: 2 })
    });
    apply_single(&mut switched, &switch);
    assert_eq!(switched.get_active(0).get_id(), "A1 033");
    assert_eq!(
        switched.in_play_pokemon[0][2]
            .as_ref()
            .expect("Jumpluff moved to the selected occupied Bench slot")
            .get_id(),
        "A4a 003"
    );
    assert_eq!(switched.move_generation_stack, vec![(1, vec![promote(1, 1)])]);
}

#[test]
fn final_scream_control_preserves_every_occupied_optional_target_in_order() {
    let mut state = breeze_by_fixture(20);
    use_breeze_by(&mut state);

    assert_eq!(state.points, [1, 0]);
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("Magikarp survives Final Scream")
            .get_remaining_hp(),
        10
    );
    assert_eq!(
        state.move_generation_stack.last().unwrap(),
        &(
            0,
            vec![activate(0, 1), activate(0, 2), SimpleAction::Noop]
        )
    );
}

#[test]
fn final_scream_removes_a_mandatory_switch_frame_when_its_only_target_is_gone() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A4018Yanma)
                .with_energy(vec![EnergyType::Colorless; 2]),
            PlayedCard::from_id(CardId::A1a017Magikarp).with_remaining_hp(10),
        ],
        vec![
            PlayedCard::from_id(CardId::B2103Spiritomb).with_remaining_hp(20),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    let attack = attack_by_title(&state, "U-turn");
    apply_single(&mut state, &attack);

    assert_eq!(state.points, [1, 1]);
    assert_eq!(state.get_active(0).get_id(), "A4 018");
    assert_eq!(state.get_active(0).get_remaining_hp(), 50);
    assert!(state.in_play_pokemon[0][1].is_none());
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.move_generation_stack, vec![(1, vec![promote(1, 1)])]);
}

#[test]
fn hala_survivor_remains_in_a_precomputed_switch_frame() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::A1053Squirtle),
            PlayedCard::from_id(CardId::B1127Hariyama).with_remaining_hp(10),
            PlayedCard::from_id(CardId::A1057Psyduck),
        ],
    );
    state.add_turn_effect(
        TurnEffect::SurviveKnockoutForSpecificPokemon {
            remaining_hp: 10,
            pokemon_names: vec!["Hariyama".to_string()],
            player: 1,
        },
        0,
    );
    state.move_generation_stack.push((
        0,
        vec![activate(1, 1), activate(1, 2), SimpleAction::Noop],
    ));
    handle_damage(&mut state, (0, 0), &[(10, 1, 1)], true, None);

    assert_eq!(state.points, [0, 0]);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .expect("Hala keeps Hariyama in play")
            .get_remaining_hp(),
        10
    );
    assert_eq!(
        state.move_generation_stack.last().unwrap(),
        &(
            0,
            vec![activate(1, 1), activate(1, 2), SimpleAction::Noop]
        )
    );
}

#[test]
fn cleanup_preserves_every_unrecognized_frame_shape() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![
            PlayedCard::from_id(CardId::A1143Machop),
            PlayedCard::from_id(CardId::A1057Psyduck),
        ],
    );
    state.in_play_pokemon[0][1] = None;
    state.in_play_pokemon[1][0] = None;
    let private = (0, Vec::new());
    let all_noop = (0, vec![SimpleAction::Noop]);
    let explicit_promote = (0, vec![promote(0, 2)]);
    let mixed_action = (
        0,
        vec![
            activate(0, 1),
            SimpleAction::ApplyDamage {
                attacking_ref: (1, 0),
                targets: vec![(10, 0, 1)],
                is_from_active_attack: false,
            },
        ],
    );
    let mixed_player = (0, vec![activate(0, 1), activate(1, 1)]);
    let invalid_player = (0, vec![activate(2, 1)]);
    let active_index = (0, vec![activate(0, 0)]);
    let out_of_range = (0, vec![activate(0, 4)]);
    let empty_active = (1, vec![activate(1, 1)]);
    let eligible = (
        1,
        vec![activate(0, 1), activate(0, 2), SimpleAction::Noop],
    );
    state.move_generation_stack = vec![
        private.clone(),
        all_noop.clone(),
        explicit_promote.clone(),
        mixed_action.clone(),
        mixed_player.clone(),
        invalid_player.clone(),
        active_index.clone(),
        out_of_range.clone(),
        empty_active.clone(),
        eligible,
    ];

    prune_stale_bench_activate_choices(&mut state);

    assert_eq!(
        state.move_generation_stack,
        vec![
            private,
            all_noop,
            explicit_promote,
            mixed_action,
            mixed_player,
            invalid_player,
            active_index,
            out_of_range,
            empty_active,
            (1, vec![activate(0, 2), SimpleAction::Noop]),
        ]
    );
}

#[test]
fn cleanup_drops_empty_mandatory_frame_but_keeps_optional_noop() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1143Machop)],
    );
    state.in_play_pokemon[0][1] = None;
    state.move_generation_stack = vec![
        (0, vec![activate(0, 1)]),
        (0, vec![activate(0, 1), SimpleAction::Noop]),
    ];

    prune_stale_bench_activate_choices(&mut state);

    assert_eq!(state.move_generation_stack, vec![(0, vec![SimpleAction::Noop])]);
}

#[test]
fn knockout_handler_does_not_prune_a_frame_when_nothing_was_knocked_out() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1143Machop)],
    );
    state.in_play_pokemon[0][1] = None;
    let frame = (
        0,
        vec![activate(0, 1), activate(0, 2), SimpleAction::Noop],
    );
    state.move_generation_stack.push(frame.clone());

    handle_knockouts(&mut state, (0, 0), false);

    assert_eq!(state.move_generation_stack, vec![frame]);
}
