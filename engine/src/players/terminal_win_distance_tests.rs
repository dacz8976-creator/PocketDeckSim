use super::*;

use crate::models::Card;
use rand::SeedableRng;

fn action(actor: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::Noop,
        is_stack: false,
    }
}

fn state_child(probability: f64, win_distance: Option<usize>) -> DebugStateNode {
    DebugStateNode {
        acting_player: 0,
        children: vec![],
        proba: probability,
        value: 0.0,
        win_distance,
    }
}

fn action_child(actor: usize, value: f64, win_distance: Option<usize>) -> DebugActionNode {
    DebugActionNode {
        action: action(actor),
        children: vec![],
        value,
        unpriced_reason: None,
        win_distance,
    }
}

#[test]
fn chance_requires_every_positive_probability_branch_to_represent_a_win() {
    let children = vec![state_child(0.5, Some(2)), state_child(0.5, None)];
    assert_eq!(chance_win_distance(&children), None);
}

#[test]
fn chance_uses_worst_supported_distance_and_adds_the_action_edge() {
    let children = vec![
        state_child(0.25, Some(2)),
        state_child(0.50, Some(5)),
        state_child(0.25, Some(3)),
    ];
    assert_eq!(chance_win_distance(&children), Some(6));
}

#[test]
fn chance_ignores_zero_probability_children_but_requires_positive_support() {
    let supported_win_and_impossible_unknown =
        vec![state_child(1.0, Some(4)), state_child(0.0, None)];
    assert_eq!(
        chance_win_distance(&supported_win_and_impossible_unknown),
        Some(5)
    );

    let no_positive_probability_children =
        vec![state_child(0.0, Some(1)), state_child(0.0, None)];
    assert_eq!(chance_win_distance(&no_positive_probability_children), None);
}

#[test]
fn own_choice_uses_only_best_numeric_children_then_the_shortest_win() {
    let children = vec![
        action_child(0, 10.0, Some(5)),
        action_child(0, 10.0, Some(2)),
        action_child(0, 9.0, Some(1)),
    ];
    assert_eq!(choice_win_distance(&children, 10.0, 0, 0), Some(2));
}

#[test]
fn own_choice_can_select_a_represented_win_from_an_exact_score_tie() {
    let children = vec![
        action_child(0, 10.0, None),
        action_child(0, 10.0, Some(4)),
    ];
    assert_eq!(choice_win_distance(&children, 10.0, 0, 0), Some(4));
}

#[test]
fn own_choice_does_not_trade_numeric_score_for_a_shorter_win() {
    let children = vec![
        action_child(0, 11.0, None),
        action_child(0, 10.0, Some(1)),
    ];
    assert_eq!(choice_win_distance(&children, 11.0, 0, 0), None);

    let ordering = 10.0_f64
        .partial_cmp(&11.0)
        .unwrap()
        .then_with(|| prefer_shorter_win(Some(1), None));
    assert_eq!(ordering, std::cmp::Ordering::Less);
}

#[test]
fn opponent_choice_requires_every_modeled_choice_and_uses_the_worst_distance() {
    let all_wins = vec![
        action_child(1, 10.0, Some(2)),
        action_child(1, 12.0, Some(6)),
        action_child(1, 11.0, Some(4)),
    ];
    assert_eq!(choice_win_distance(&all_wins, 10.0, 1, 0), Some(6));

    let avoidable = vec![
        action_child(1, 10.0, Some(2)),
        action_child(1, 12.0, None),
    ];
    assert_eq!(choice_win_distance(&avoidable, 10.0, 1, 0), None);
}

#[test]
fn win_distance_order_prefers_shorter_then_represented_then_legacy_equal() {
    assert_eq!(
        prefer_shorter_win(Some(2), Some(5)),
        std::cmp::Ordering::Greater
    );
    assert_eq!(
        prefer_shorter_win(Some(2), None),
        std::cmp::Ordering::Greater
    );
    assert_eq!(
        prefer_shorter_win(None, Some(2)),
        std::cmp::Ordering::Less
    );
    assert_eq!(
        prefer_shorter_win(None, None),
        std::cmp::Ordering::Equal
    );
    assert_eq!(
        prefer_shorter_win(Some(3), Some(3)),
        std::cmp::Ordering::Equal
    );
}

#[test]
fn hidden_draw_is_unpriced_and_cannot_supply_a_win_distance() {
    let mut state = State::default();
    state.current_player = 0;
    state.turn_count = 3;
    state.decks[0].cards = vec![Card::Unknown];
    let draw = Action {
        actor: 0,
        action: SimpleAction::DrawCard { amount: 1 },
        is_stack: true,
    };
    let value_function: ValueFunction = Box::new(|_, _| 7.0);
    let mut rng = StdRng::seed_from_u64(17);

    let ((score, node), unpriced) = crate::observation::collect_unpriced(|| {
        expected_value_function(
            &mut rng,
            &state,
            &draw,
            2,
            0,
            false,
            SearchFlags::default(),
            0,
            &value_function,
        )
    });

    assert_eq!(score, 7.0);
    assert_eq!(node.win_distance, None);
    assert!(node.children.is_empty());
    assert_eq!(
        node.unpriced_reason.as_deref(),
        Some("draw reaches an unknown card identity")
    );
    assert_eq!(unpriced.len(), 1);
    assert_eq!(unpriced[0].action, draw);
    assert_eq!(
        unpriced[0].reason,
        "draw reaches an unknown card identity"
    );
}

#[test]
fn only_a_settled_own_win_has_zero_remaining_distance() {
    use crate::state::GameOutcome;
    let value: ValueFunction = Box::new(|_, _| 7.0);
    for (winner, expected) in [(Some(GameOutcome::Win(0)),Some(0)),
        (Some(GameOutcome::Win(1)),None),(Some(GameOutcome::Tie),None),(None,None)] {
        let mut state=State::default();state.current_player=0;state.turn_count=3;state.winner=winner;
        let (_,node)=expectiminimax(&mut StdRng::seed_from_u64(17),&state,0,0,false,
            SearchFlags::default(),0,&value);
        assert_eq!(node.win_distance,expected,"{winner:?}");
    }
}
