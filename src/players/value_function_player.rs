use rand::rngs::StdRng;
use std::fmt::Debug;

use crate::actions::{try_forecast_action, Action, SimpleAction};
use crate::{Deck, State};

use super::Player;

pub struct ValueFunctionPlayer {
    pub deck: Deck,
}

impl Player for ValueFunctionPlayer {
    fn decide_omniscient(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
    ) -> Action {
        // Get value for the possible actions
        let myself = possible_actions[0].actor;
        let scores: Vec<f64> = possible_actions
            .iter()
            .map(|action| {
                crate::observation::with_root_action(action, || {
                    if state.setup_opponent_hidden {
                        crate::observation::record_unpriced(
                            action,
                            "opponent setup is hidden; only own setup development is scored",
                        );
                    }
                    expected_value_function(rng, state, action, myself)
                })
            })
            .collect();

        // Select the one with best score
        let best_idx = scores
            .iter()
            .enumerate()
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .unwrap()
            .0;

        possible_actions[best_idx].clone()
    }

    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
}

fn expected_value_function(rng: &mut StdRng, state: &State, action: &Action, myself: usize) -> f64 {
    if let Some(reason) = crate::observation::hidden_continuation_reason(state, action) {
        crate::observation::record_unpriced(action, reason);
        return value_function(state, myself);
    }
    let forecast = match try_forecast_action(state, action) {
        Ok(forecast) => forecast,
        Err(error) => {
            crate::observation::record_unpriced(action, &error.reason);
            return value_function(state, myself);
        }
    };
    let (probabilities, mutations) = forecast.into_branches();
    let mut outcomes: Vec<State> = vec![];
    for mutation in mutations {
        let mut state = state.clone();
        mutation(rng, &mut state, action);
        outcomes.push(state);
    }
    outcomes
        .iter()
        .zip(probabilities.iter())
        .map(|(outcome, prob)| value_after_mandatory_continuation(rng, outcome, myself) * prob)
        .sum()
}

/// A Victory Star prompt or queued attack-damage target is a continuation of the attack being
/// valued, rather than a terminal zero-damage state. Resolve exactly this bounded choice and stop
/// after the attack commits.
fn value_after_mandatory_continuation(rng: &mut StdRng, state: &State, myself: usize) -> f64 {
    let queued_attack_damage_choice =
        state
            .move_generation_stack
            .last()
            .is_some_and(|(_, choices)| {
                !choices.is_empty()
                    && choices.iter().all(|choice| {
                        matches!(choice, SimpleAction::ApplyQueuedAttackDamage { .. })
                    })
            });
    if state.pending_attack_coin_choice.is_none()
        && state.pending_misty_target_choice.is_none()
        && state.pending_trainer_coin_choice.is_none()
        && !queued_attack_damage_choice
    {
        return value_function(state, myself);
    }
    let (actor, actions) = state.generate_possible_actions();
    if actions.is_empty() || actor != myself {
        let action = Action {
            actor,
            action: crate::actions::SimpleAction::Noop,
            is_stack: true,
        };
        crate::observation::record_unpriced(
            &action,
            "private pending choice is unavailable to this observer",
        );
        return value_function(state, myself);
    }
    actions
        .iter()
        .map(|action| expected_value_function(rng, state, action, myself))
        .fold(f64::NEG_INFINITY, f64::max)
}

fn value_function(state: &State, myself: usize) -> f64 {
    // TODO: Add more features. Other ideas:
    // Attached energy on enemies in play?
    // Can we give priorities to attached energies?
    // Health on the Active spot?
    // Closeness to getting a point(?) Num Knockouts?
    let attached_energy_in_play = state
        .enumerate_in_play_pokemon(myself)
        .map(|(_, card)| card.attached_energy.len() as f64)
        .sum::<f64>();
    let points = state.points[myself] as f64;

    points * 100.0 + attached_energy_in_play
}

impl Debug for ValueFunctionPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ValueFunctionPlayer")
    }
}

#[cfg(test)]
mod victory_star_observation_tests {
    use super::*;
    use crate::{actions::SimpleAction, models::Attack, state::PendingAttackCoinChoice};
    use rand::SeedableRng;

    #[test]
    fn redacted_victory_star_continuation_is_unpriced_without_panicking() {
        let mut state = State::default();
        state.pending_attack_coin_choice = Some(PendingAttackCoinChoice {
            actor: 0,
            attack: Attack {
                energy_required: Vec::new(),
                title: "Coin Attack".into(),
                fixed_damage: 0,
                effect: Some("Flip a coin.".into()),
            },
            original_is_stack: false,
            flips: vec![false],
            victory_star_in_play_idx: 1,
        });
        state
            .move_generation_stack
            .push((0, Vec::<SimpleAction>::new()));
        let mut rng = StdRng::seed_from_u64(8);

        let (score, branches) = crate::observation::collect_unpriced(|| {
            value_after_mandatory_continuation(&mut rng, &state, 1)
        });

        assert_eq!(score, value_function(&state, 1));
        assert_eq!(branches.len(), 1);
        assert_eq!(
            branches[0].reason,
            "private pending choice is unavailable to this observer"
        );
    }

    #[test]
    fn value_player_prices_mandatory_queued_attack_damage_before_scoring() {
        use crate::{card_ids::CardId, models::PlayedCard, test_support::nth_attack};

        let mut state = State::default();
        state.set_board(
            vec![PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx)],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(50),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
        );
        state.current_player = 0;
        state.turn_count = 3;
        let action = Action {
            actor: 0,
            action: SimpleAction::Attack(nth_attack(CardId::B4a021TeamRocketsZapdosEx, 1)),
            is_stack: false,
        };
        let mut rng = StdRng::seed_from_u64(9);

        assert_eq!(
            expected_value_function(&mut rng, &state, &action, 0),
            200.0,
            "the value player must see both mandatory knockouts, not the zero-damage pause"
        );
    }
}
