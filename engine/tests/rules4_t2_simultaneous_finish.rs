use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board},
};

fn finish(actor: usize, own_bench: bool, opposing_bench: bool, points: [u8; 2]) -> deckgym::State {
    let mut own = vec![PlayedCard::from_id(CardId::A4124SkarmoryEx)
        .with_remaining_hp(10)
        .with_energy(vec![EnergyType::Metal, EnergyType::Metal])];
    if own_bench {
        own.push(PlayedCard::from_id(CardId::A1001Bulbasaur));
    }
    let mut other = vec![PlayedCard::from_id(CardId::B4a020TeamRocketsElectrode)];
    if opposing_bench {
        other.push(PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx));
        other.push(PlayedCard::from_id(CardId::B4a019TeamRocketsVoltorb));
    }
    let (p0, p1) = if actor == 0 { (own, other) } else { (other, own) };
    let mut game = get_initialized_game_with_board(777, actor, 5, p0, p1);
    let mut state = game.get_state_clone();
    state.points = if actor == 0 { points } else { [points[1], points[0]] };
    game.set_state(state);
    game.apply_action(&Action {
        actor,
        action: attack_action(CardId::A4124SkarmoryEx, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn observed_t2_third_point_and_last_pokemon_loss_is_tie_in_both_seats() {
    for actor in 0..2 {
        let state = finish(actor, false, true, [2, 0]);
        assert_eq!(state.points[actor], 3);
        assert_eq!(state.points[1 - actor], 2);
        assert_eq!(state.enumerate_in_play_pokemon(actor).count(), 0);
        assert_eq!(state.enumerate_in_play_pokemon(1 - actor).count(), 2);
        assert_eq!(state.winner, Some(GameOutcome::Tie));
    }
}

#[test]
fn own_bench_keeps_third_point_victory_in_both_seats() {
    for actor in 0..2 {
        let state = finish(actor, true, true, [2, 0]);
        assert_eq!(state.points[actor], 3);
        assert_eq!(state.points[1 - actor], 2);
        assert_eq!(state.enumerate_in_play_pokemon(actor).count(), 1);
        assert_eq!(state.winner, Some(GameOutcome::Win(actor)));
    }
}

#[test]
fn both_three_point_and_both_empty_controls_retain_prior_results() {
    for actor in 0..2 {
        let both_points = finish(actor, true, true, [2, 1]);
        assert_eq!(both_points.points[actor], 3);
        assert_eq!(both_points.points[1 - actor], 3);
        assert_eq!(both_points.winner, Some(GameOutcome::Tie));

        // Compatibility controls only: the real app has not established these
        // boundary cases, so this narrow T2 repair leaves their old outcomes intact.
        let both_points_one_empty = finish(actor, false, true, [2, 1]);
        assert_eq!(both_points_one_empty.points[actor], 3);
        assert_eq!(both_points_one_empty.points[1 - actor], 3);
        assert_eq!(both_points_one_empty.enumerate_in_play_pokemon(actor).count(), 0);
        assert_eq!(both_points_one_empty.enumerate_in_play_pokemon(1 - actor).count(), 2);
        assert_eq!(both_points_one_empty.winner, Some(GameOutcome::Tie));

        let both_empty_one_at_three = finish(actor, false, false, [2, 0]);
        assert_eq!(both_empty_one_at_three.points[actor], 3);
        assert_eq!(both_empty_one_at_three.points[1 - actor], 2);
        assert_eq!(both_empty_one_at_three.enumerate_in_play_pokemon(actor).count(), 0);
        assert_eq!(both_empty_one_at_three.enumerate_in_play_pokemon(1 - actor).count(), 0);
        assert_eq!(both_empty_one_at_three.winner, Some(GameOutcome::Win(actor)));

        let both_empty = finish(actor, false, false, [0, 0]);
        assert_eq!(both_empty.points[actor], 1);
        assert_eq!(both_empty.points[1 - actor], 2);
        assert_eq!(both_empty.enumerate_in_play_pokemon(actor).count(), 0);
        assert_eq!(both_empty.enumerate_in_play_pokemon(1 - actor).count(), 0);
        assert_eq!(both_empty.winner, Some(GameOutcome::Tie));
    }
}
