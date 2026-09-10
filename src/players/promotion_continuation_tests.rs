use super::*;
use crate::{
    actions::{forecast_action, Action, SimpleAction},
    card_ids::CardId,
    effects::TurnEffect,
    models::{EnergyType, PlayedCard},
    state::GameOutcome,
    State,
};
use rand::{rngs::StdRng, SeedableRng};

fn state_with_boards(owner: Vec<PlayedCard>, opponent: Vec<PlayedCard>) -> State {
    let mut state = State::default();
    state.current_player = 0;
    state.turn_count = 7;
    state.set_board(owner, opponent);
    state.hands = [Vec::new(), Vec::new()];
    for player in 0..2 {
        state.decks[player].cards.clear();
        state.energy_zone[player].current = None;
        state.energy_zone[player].next = None;
    }
    state
}

fn action_by_attack_title(state: &State, title: &str) -> Action {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Attack(attack) if attack.title == title)
        })
        .unwrap_or_else(|| panic!("expected attack {title}"))
}

fn apply_single(state: &mut State, action: &Action) {
    let (probabilities, mutations) = forecast_action(state, action).into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    mutations.into_iter().next().unwrap()(
        &mut StdRng::seed_from_u64(73),
        state,
        action,
    );
}

fn promotion_choice(player: usize, in_play_idx: usize) -> SimpleAction {
    SimpleAction::Promote {
        player,
        in_play_idx,
    }
}

fn choice_value(state: &State, player: usize) -> f64 {
    match state.in_play_pokemon[player][0]
        .as_ref()
        .map(PlayedCard::get_id)
        .as_deref()
    {
        Some("A1 033") => 10.0,
        Some("A1 003") => 20.0,
        None => -100.0,
        Some(_) => 0.0,
    }
}

#[test]
fn promote_is_serialized_distinctly_from_an_ordinary_switch() {
    let activate = SimpleAction::Activate {
        player: 1,
        in_play_idx: 2,
    };
    let promote = promotion_choice(1, 2);

    let activate_json = serde_json::to_value(&activate).unwrap();
    let promote_json = serde_json::to_value(&promote).unwrap();
    assert!(activate_json.get("Activate").is_some());
    assert!(promote_json.get("Promote").is_some());
    assert_ne!(activate_json, promote_json);
    assert_eq!(
        serde_json::from_value::<SimpleAction>(promote_json).unwrap(),
        promote
    );
}

#[test]
fn depth_zero_promotion_uses_the_frame_actor_for_max_and_min() {
    for (frame_actor, myself, expected) in [(0, 0, 20.0), (1, 0, 10.0)] {
        let mut state = state_with_boards(
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
                PlayedCard::from_id(CardId::A1003Venusaur),
            ],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
                PlayedCard::from_id(CardId::A1003Venusaur),
            ],
        );
        state.in_play_pokemon[frame_actor][0] = None;
        state.move_generation_stack.push((
            frame_actor,
            vec![promotion_choice(frame_actor, 1), promotion_choice(frame_actor, 2)],
        ));
        let evaluator: ValueFunction = Box::new(move |state, _| choice_value(state, frame_actor));
        let (score, node) = expectiminimax(
            &mut StdRng::seed_from_u64(74),
            &state,
            0,
            0,
            false,
            SearchFlags::default(),
            myself,
            &evaluator,
        );

        assert_eq!(score, expected);
        assert_eq!(node.acting_player, frame_actor);
        assert_eq!(node.children.len(), 2);
        assert!(node.children.iter().all(|child| {
            matches!(child.action.action, SimpleAction::Promote { player, .. }
                if player == frame_actor)
        }));
        let mut values = node
            .children
            .iter()
            .map(|child| child.value)
            .collect::<Vec<_>>();
        values.sort_by(f64::total_cmp);
        assert_eq!(values, vec![10.0, 20.0]);
    }
}

#[test]
fn promotion_leaves_nonzero_depth_for_the_next_ordinary_action() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1198Farfetchd)
                .with_energy(vec![EnergyType::Psychic]),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30)],
    );
    state.in_play_pokemon[0][0] = None;
    state.points = [2, 0];
    state
        .move_generation_stack
        .push((0, vec![promotion_choice(0, 1)]));
    let evaluator: ValueFunction = Box::new(|state, _| {
        if state.winner == Some(GameOutcome::Win(0)) {
            1.0
        } else {
            0.0
        }
    });

    let (score, node) = expectiminimax(
        &mut StdRng::seed_from_u64(81),
        &state,
        1,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    );

    assert_eq!(score, 1.0, "the retained action ply must see Farfetch'd's winning attack");
    assert_eq!(node.children.len(), 1);
    assert!(matches!(
        node.children[0].action.action,
        SimpleAction::Promote { .. }
    ));
    assert!(node.children[0].children[0]
        .children
        .iter()
        .any(|child| matches!(child.action.action, SimpleAction::Attack(_))));
}

#[test]
fn promotion_is_not_inferred_during_setup_through_private_or_generic_frames() {
    let base = || {
        let mut state = state_with_boards(
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
            vec![PlayedCard::from_id(CardId::A1053Squirtle)],
        );
        state.in_play_pokemon[0][0] = None;
        state.in_play_pokemon[0][1] = Some(PlayedCard::from_id(CardId::A1033Charmander));
        state
    };
    let evaluator: ValueFunction = Box::new(|_, _| 7.0);

    let mut setup = base();
    setup.turn_count = 0;
    setup
        .move_generation_stack
        .push((0, vec![promotion_choice(0, 1)]));
    let (score, node) = expectiminimax(
        &mut StdRng::seed_from_u64(75),
        &setup,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    );
    assert_eq!(score, 7.0);
    assert!(node.children.is_empty());

    let mut concealed = base();
    concealed.setup_opponent_hidden = true;
    concealed
        .move_generation_stack
        .push((0, vec![promotion_choice(0, 1)]));
    assert!(expectiminimax(
        &mut StdRng::seed_from_u64(76),
        &concealed,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    )
    .1
    .children
    .is_empty());

    let mut private = base();
    private.move_generation_stack.push((1, Vec::new()));
    assert!(expectiminimax(
        &mut StdRng::seed_from_u64(77),
        &private,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    )
    .1
    .children
    .is_empty());

    let mut covered = base();
    covered
        .move_generation_stack
        .push((0, vec![promotion_choice(0, 1)]));
    covered.move_generation_stack.push((
        0,
        vec![SimpleAction::Activate {
            player: 0,
            in_play_idx: 1,
        }],
    ));
    assert!(expectiminimax(
        &mut StdRng::seed_from_u64(78),
        &covered,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    )
    .1
    .children
    .is_empty());

    let mut incomplete = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1003Venusaur),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    incomplete.in_play_pokemon[0][0] = None;
    incomplete
        .move_generation_stack
        .push((0, vec![promotion_choice(0, 1)]));
    assert!(expectiminimax(
        &mut StdRng::seed_from_u64(80),
        &incomplete,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    )
    .1
    .children
    .is_empty());
}

#[test]
fn trigger_cleanup_removes_only_stale_same_board_switch_frames() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1057Psyduck),
        ],
    );
    state.in_play_pokemon[0][0] = None;
    let stale = (
        1,
        vec![
            SimpleAction::Activate {
                player: 0,
                in_play_idx: 1,
            },
            SimpleAction::Noop,
        ],
    );
    let private = (1, Vec::new());
    let all_noop = (0, vec![SimpleAction::Noop]);
    let other_player = (
        0,
        vec![SimpleAction::Activate {
            player: 1,
            in_play_idx: 1,
        }],
    );
    let mixed = (
        0,
        vec![
            SimpleAction::Activate {
                player: 0,
                in_play_idx: 1,
            },
            SimpleAction::ApplyDamage {
                attacking_ref: (1, 0),
                targets: vec![(10, 0, 1)],
                is_from_active_attack: false,
            },
        ],
    );
    let mixed_targets = (
        0,
        vec![
            SimpleAction::Activate {
                player: 0,
                in_play_idx: 1,
            },
            SimpleAction::Activate {
                player: 1,
                in_play_idx: 1,
            },
        ],
    );
    let prior_promote = (0, vec![promotion_choice(0, 1)]);
    state.move_generation_stack = vec![
        stale.clone(),
        private.clone(),
        all_noop.clone(),
        other_player.clone(),
        mixed.clone(),
        mixed_targets.clone(),
        prior_promote.clone(),
    ];

    state.trigger_promotion_or_declare_winner(0);

    assert!(!state.move_generation_stack.contains(&stale));
    for preserved in [
        private,
        all_noop,
        other_player,
        mixed,
        mixed_targets,
        prior_promote,
    ] {
        assert!(state.move_generation_stack.contains(&preserved));
    }
    assert_eq!(
        state
            .move_generation_stack
            .iter()
            .filter(|(actor, choices)| {
                *actor == 0 && choices.as_slice() == [promotion_choice(0, 1)]
            })
            .count(),
        2,
        "the existing Promote frame and the newly generated frame must both remain"
    );
}

#[test]
fn lethal_knock_back_leaves_one_promotion_while_nonlethal_keeps_the_switch() {
    let fixture = |target| {
        state_with_boards(
            vec![PlayedCard::from_id(CardId::A1163Grapploct)
                .with_energy(vec![EnergyType::Fighting; 3])],
            vec![
                PlayedCard::from_id(target),
                PlayedCard::from_id(CardId::A1033Charmander),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
        )
    };

    let mut lethal = fixture(CardId::A1001Bulbasaur);
    let attack = action_by_attack_title(&lethal, "Knock Back");
    apply_single(&mut lethal, &attack);
    assert_eq!(lethal.points, [1, 0]);
    assert!(lethal.in_play_pokemon[1][0].is_none());
    assert_eq!(lethal.move_generation_stack.len(), 1);
    let (actor, choices) = lethal.move_generation_stack.last().unwrap();
    assert_eq!(*actor, 1);
    assert_eq!(
        choices,
        &vec![promotion_choice(1, 1), promotion_choice(1, 2)]
    );
    assert!(!choices
        .iter()
        .any(|choice| matches!(choice, SimpleAction::Activate { .. })));
    let promote = lethal.generate_possible_actions().1[0].clone();
    apply_single(&mut lethal, &promote);
    assert!(lethal.in_play_pokemon[1][0].is_some());
    assert!(lethal.move_generation_stack.is_empty());
    assert_eq!(lethal.winner, None);

    let mut nonlethal = fixture(CardId::A1128Mewtwo);
    let before_hp = nonlethal.get_active(1).get_remaining_hp();
    let attack = action_by_attack_title(&nonlethal, "Knock Back");
    apply_single(&mut nonlethal, &attack);
    assert_eq!(nonlethal.points, [0, 0]);
    assert_eq!(nonlethal.get_active(1).get_remaining_hp(), before_hp - 70);
    assert_eq!(nonlethal.move_generation_stack.len(), 1);
    assert!(nonlethal.move_generation_stack[0]
        .1
        .iter()
        .all(|choice| matches!(choice, SimpleAction::Activate { player: 1, .. })));
}

#[test]
fn hala_rescue_preserves_knock_backs_ordinary_switch_choice() {
    let mut state = state_with_boards(
        vec![PlayedCard::from_id(CardId::A1163Grapploct)
            .with_energy(vec![EnergyType::Fighting; 3])],
        vec![
            PlayedCard::from_id(CardId::B1127Hariyama).with_remaining_hp(70),
            PlayedCard::from_id(CardId::A1033Charmander),
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
    let attack = action_by_attack_title(&state, "Knock Back");
    apply_single(&mut state, &attack);

    assert_eq!(state.points, [0, 0]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 10);
    assert_eq!(state.move_generation_stack.len(), 1);
    assert!(state.move_generation_stack[0]
        .1
        .iter()
        .all(|choice| matches!(choice, SimpleAction::Activate { player: 1, .. })));
    assert!(!state.move_generation_stack[0]
        .1
        .iter()
        .any(|choice| matches!(choice, SimpleAction::Promote { .. })));
}

#[test]
fn self_switch_retaliation_keeps_only_both_real_promotions() {
    let fixture = |target_hp| {
        state_with_boards(
            vec![
                PlayedCard::from_id(CardId::A4018Yanma)
                    .with_energy(vec![EnergyType::Colorless; 2])
                    .with_remaining_hp(50),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            vec![
                PlayedCard::from_id(CardId::A3054Pyukumuku).with_remaining_hp(target_hp),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
        )
    };

    let mut mutual_ko = fixture(20);
    let attack = action_by_attack_title(&mutual_ko, "U-turn");
    apply_single(&mut mutual_ko, &attack);
    assert_eq!(mutual_ko.points, [1, 1]);
    assert!(mutual_ko.in_play_pokemon[0][0].is_none());
    assert!(mutual_ko.in_play_pokemon[1][0].is_none());
    assert_eq!(mutual_ko.move_generation_stack.len(), 2);
    assert!(mutual_ko.move_generation_stack.iter().all(|(_, choices)| {
        !choices.is_empty()
            && choices
                .iter()
                .all(|choice| matches!(choice, SimpleAction::Promote { .. }))
    }));
    while !mutual_ko.move_generation_stack.is_empty() {
        let promote = mutual_ko.generate_possible_actions().1[0].clone();
        apply_single(&mut mutual_ko, &promote);
    }
    assert!(mutual_ko.in_play_pokemon[0][0].is_some());
    assert!(mutual_ko.in_play_pokemon[1][0].is_some());
    assert_eq!(mutual_ko.winner, None);

    let mut nonlethal = fixture(60);
    let attack = action_by_attack_title(&nonlethal, "U-turn");
    apply_single(&mut nonlethal, &attack);
    assert_eq!(nonlethal.points, [0, 0]);
    assert_eq!(nonlethal.get_active(1).get_remaining_hp(), 40);
    assert_eq!(nonlethal.move_generation_stack.len(), 1);
    assert!(nonlethal.move_generation_stack[0]
        .1
        .iter()
        .all(|choice| matches!(choice, SimpleAction::Activate { player: 0, .. })));
}

#[test]
fn optional_self_switch_noop_is_removed_when_final_scream_kos_the_attacker() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A4a003JumpluffEx)
                .with_energy(vec![EnergyType::Colorless])
                .with_remaining_hp(10),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::B2103Spiritomb),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );
    let attack = action_by_attack_title(&state, "Breeze-By Attack");
    apply_single(&mut state, &attack);

    assert_eq!(state.points, [1, 2]);
    assert!(state.in_play_pokemon[0][0].is_none());
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50
    );
    assert_eq!(state.move_generation_stack.len(), 2);
    assert!(state.move_generation_stack.iter().all(|(_, choices)| {
        !choices.is_empty()
            && choices
                .iter()
                .all(|choice| matches!(choice, SimpleAction::Promote { .. }))
    }));
    assert!(!state.move_generation_stack.iter().any(|(_, choices)| {
        choices.iter().any(|choice| {
            matches!(choice, SimpleAction::Activate { .. } | SimpleAction::Noop)
        })
    }));
}

#[test]
fn coin_ko_branch_resolves_promotion_without_changing_probability() {
    let state = state_with_boards(
        vec![PlayedCard::from_id(CardId::A1023ExeggutorEx)
            .with_energy(vec![EnergyType::Grass])],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );
    let attack = action_by_attack_title(&state, "Tropical Swing");
    let evaluator: ValueFunction = Box::new(|state, _| {
        if state.in_play_pokemon[1][0]
            .as_ref()
            .is_some_and(|pokemon| pokemon.get_id() == "A1 053")
        {
            1.0
        } else {
            0.0
        }
    });
    let (score, action_node) = expected_value_function(
        &mut StdRng::seed_from_u64(79),
        &state,
        &attack,
        0,
        0,
        false,
        SearchFlags::default(),
        0,
        &evaluator,
    );

    assert_eq!(score, 0.5);
    assert_eq!(action_node.children.len(), 2);
    let mut probabilities = action_node
        .children
        .iter()
        .map(|child| child.proba)
        .collect::<Vec<_>>();
    probabilities.sort_by(f64::total_cmp);
    assert_eq!(probabilities, vec![0.5, 0.5]);
}

#[test]
fn returning_an_active_uses_the_explicit_promotion_path() {
    let mut state = state_with_boards(
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let action = Action {
        actor: 0,
        action: SimpleAction::ReturnPokemonToHand { in_play_idx: 0 },
        is_stack: false,
    };
    apply_single(&mut state, &action);

    assert!(state.in_play_pokemon[0][0].is_none());
    assert_eq!(state.move_generation_stack.len(), 1);
    assert_eq!(
        state.move_generation_stack[0],
        (0, vec![promotion_choice(0, 1)])
    );
}
