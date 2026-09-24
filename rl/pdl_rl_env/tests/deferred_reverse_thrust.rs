#[path = "../src/v2.rs"]
mod v2;

use deckgym::actions::{try_forecast_action, Action};
use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::state::GameOutcome;
use deckgym::test_support::attack_action;
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};

#[test]
fn reverse_thrust_deferred_knockout_baseline() {
    for bench_count in [1, 2] {
        let mut state = State::new(&Deck::default(), &Deck::default());
        state.turn_count = 10;
        state.current_player = 0;
        state.points[0] = 2;
        let mut own = vec![PlayedCard::from_id(CardId::B4a042TeamRocketsKoffing)
            .with_energy(vec![EnergyType::Darkness])];
        own.extend((0..bench_count).map(|_| PlayedCard::from_id(CardId::A1001Bulbasaur)));
        state.set_board(own, vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(60)]);
        let action = Action { actor: 0, action: attack_action(CardId::B4a042TeamRocketsKoffing, 0), is_stack: false };
        assert!(state.generate_possible_actions().1.contains(&action));
        let obs = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let (_, rows, seen) = v2::features(&obs, &[action.clone()], true);
        assert!(seen);
        let row = rows[0];
        let (probs, muts) = try_forecast_action(&state, &action).unwrap().into_branches();
        assert_eq!(probs.len(), 1);
        let mut after = state.clone();
        muts.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(1), &mut after, &action);
        let (chooser, choices) = after.move_generation_stack.last().unwrap();
        assert_eq!(*chooser, 0);
        assert_eq!(choices.len(), bench_count);
        println!("bench={bench_count} row_priced={} row_point={} row_win={} step_points={} pending_choices={}", row[0], row[1], row[3], after.points[0], choices.len());
        let diagnostic = v2::diagnostics(&obs, &[action.clone()], seen);
        let status: serde_json::Value = serde_json::from_str(&diagnostic[0]).unwrap();
        if bench_count == 1 {
            assert_eq!(row[0], 1.0);
            assert!((row[1] - 1.0 / 3.0).abs() < 1e-6);
            assert_eq!(row[3], 1.0);
            assert_eq!(status["status"], "priced");
            assert_eq!(status["new_rule_frame_seen"], true);
        } else {
            assert_eq!(row[0], 0.0);
            assert_eq!(row[1], 0.0);
            assert_eq!(row[3], 0.0);
            assert_eq!(status["status"], "deferred_choice_unpriced");
        }
        for choice in choices.clone() {
            let after_obs = PlayerObservation::from_state(&after, 0, &RevealedKnowledge::default());
            let (_, choice_rows, choice_seen) = v2::features(&after_obs, &[Action { actor: 0, action: choice.clone(), is_stack: true }], true);
            assert!(choice_seen);
            assert_eq!(choice_rows[0][0], 1.0);
            assert!((choice_rows[0][1] - 1.0 / 3.0).abs() < 1e-6);
            assert_eq!(choice_rows[0][3], 1.0);
            let next = Action { actor: 0, action: choice, is_stack: true };
            let (p, muts) = try_forecast_action(&after, &next).unwrap().into_branches();
            assert_eq!(p.len(), 1);
            let mut resolved = after.clone();
            muts.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(2), &mut resolved, &next);
            let mut forced = 0;
            while resolved.winner.is_none() && forced < 8 {
                let (_, legal) = resolved.generate_possible_actions();
                if legal.len() != 1 { break; }
                let rule = legal[0].clone();
                let (weights, effects) = try_forecast_action(&resolved, &rule).unwrap().into_branches();
                assert_eq!(weights.len(), 1);
                let mut next_state = resolved.clone();
                effects.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(3 + forced), &mut next_state, &rule);
                resolved = next_state;
                forced += 1;
            }
            println!("bench={bench_count} forced={forced} resolved_points={} winner={:?}", resolved.points[0], resolved.winner);
            assert_eq!(resolved.points[0], 3);
            assert!(matches!(resolved.winner, Some(GameOutcome::Win(0))));
        }
    }
}
