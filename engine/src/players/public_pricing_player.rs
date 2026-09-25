//! B1' public pricing (`kp<N>`): the k<N> search, blind as ever, but effects whose text mentions the
//! opponent's hand or deck are priced instead of left unpriced.
//!
//! Blind, k<N> scores any such move as if nothing happened (`hidden_continuation_reason`'s text rule):
//! Darkness Claw's 80 damage counts as zero and Copycat as a no-op. The option B attribution
//! (rl/results/option_b_attribution_2026-09-24.md) found that pricing these, not information about
//! the opponent, is where the list guess moves the table. This player gets that pricing with no list:
//! the effect resolves against the opponent's Unknown cards, which have no identity, so only its public
//! parts count. Everything else is the k<N> search unchanged, and with none of these cards in play it
//! plays k<N>'s games move for move.

use rand::rngs::StdRng;
use std::fmt::Debug;

use super::expectiminimax_player::ExpectiMiniMaxPlayer;
use super::Player;
use crate::actions::Action;
use crate::observation::{with_public_pricing, PlayerObservation};
use crate::{Deck, State};

pub struct PublicPricingPlayer {
    pub search: ExpectiMiniMaxPlayer,
}

impl Debug for PublicPricingPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PublicPricingPlayer")
    }
}

impl Player for PublicPricingPlayer {
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        observation: &PlayerObservation,
        possible_actions: &[Action],
    ) -> Action {
        let search = &mut self.search;
        with_public_pricing(|| search.decision_fn(rng, observation, possible_actions))
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        let search = &mut self.search;
        with_public_pricing(|| search.decide_omniscient(rng, state, possible_actions))
    }

    fn get_deck(&self) -> Deck {
        self.search.get_deck()
    }
}

#[cfg(test)]
mod tests {
    use super::super::{get_player, PlayerCode};
    use super::*;
    use crate::actions::SimpleAction;
    use crate::card_ids::CardId;
    use crate::models::{Card, EnergyType, PlayedCard};
    use crate::observation::{hidden_continuation_reason, RevealedKnowledge};
    use crate::players::value_functions;
    use crate::test_support::get_test_game_with_board;
    use crate::Game;
    use rand::SeedableRng;

    fn k3_search() -> ExpectiMiniMaxPlayer {
        // The K arm of get_player, field for field.
        ExpectiMiniMaxPlayer {
            deck: Deck::default(),
            max_depth: 3,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_clock_effect_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }
    }

    /// Mega Absol ex with Darkness Claw paid for, against the opponent's only Pokémon, a 60-HP Abra
    /// (80 damage, +20 Weakness): the attack knocks it out and wins. The opponent's hand holds a card, so blind it is Unknown.
    fn darkness_claw_wins() -> (State, Vec<Action>) {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::B1151MegaAbsolEx)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
            vec![PlayedCard::from_id(CardId::A1115Abra)],
        );
        let mut state = game.get_state_clone();
        state.move_generation_stack.clear();
        if state.hands[1].is_empty() {
            state.hands[1].push(state.decks[1].cards.pop().unwrap());
        }
        game.set_state(state);
        let real = game.get_state_clone();
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        let search_state = observation.search_state(&mut StdRng::seed_from_u64(7));
        assert!(search_state.hands[1].iter().all(|c| *c == Card::Unknown));
        let (actor, actions) = search_state.generate_possible_actions();
        assert_eq!(actor, 0);
        (search_state, actions)
    }

    fn darkness_claw(actions: &[Action]) -> usize {
        actions
            .iter()
            .position(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == "Darkness Claw"))
            .expect("Darkness Claw is offered")
    }

    #[test]
    fn the_opponent_hand_text_rule_is_lifted_only_under_public_pricing() {
        let (state, actions) = darkness_claw_wins();
        let claw = &actions[darkness_claw(&actions)];
        assert!(hidden_continuation_reason(&state, claw).is_some(), "blind k-tiers leave it unpriced");
        assert_eq!(with_public_pricing(|| hidden_continuation_reason(&state, claw)), None);
        // The flag is scoped: it is off again afterwards, and the strict rule ignores it.
        assert!(hidden_continuation_reason(&state, claw).is_some());
        assert!(with_public_pricing(|| crate::observation::hidden_continuation_reason_strict(&state, claw)).is_some());
    }

    #[test]
    fn public_pricing_sees_a_winning_darkness_claw_that_k3_scores_as_nothing() {
        let (state, actions) = darkness_claw_wins();
        let claw = darkness_claw(&actions);
        let provenance = crate::players::public_reply::PublicReplyProvenance::untrusted();
        let blind = k3_search().score_candidates(&mut StdRng::seed_from_u64(1), &state, &actions, provenance);
        let priced = with_public_pricing(|| {
            k3_search().score_candidates(&mut StdRng::seed_from_u64(1), &state, &actions, provenance)
        });
        let mut won = state.clone();
        won.winner = Some(crate::state::GameOutcome::Win(0));
        let win_value = value_functions::public_clock_effect_value_function(&won, 0);
        assert_eq!(priced[claw].0, win_value, "priced: the knockout ends the game");
        assert!(blind[claw].0 < win_value, "blind: scored as the position before the attack");
        let best = priced.iter().map(|s| s.0).fold(f64::NEG_INFINITY, f64::max);
        assert_eq!(priced[claw].0, best, "priced: Darkness Claw is the best move");
    }

    /// Where neither deck has a card whose text mentions the opponent's hand or deck, kp3 must play k3's
    /// games move for move: the wrapper changes nothing else. (Every table list has Copycat, so these use
    /// example decks without any such card.)
    #[test]
    fn kp3_plays_k3_game_for_game_without_opponent_hand_cards() {
        let pairs = [("weezing-arbok", "fire"), ("mewtwoex", "blastoiseex"), ("hitmonlee", "arceusdialga")];
        let k3 = PlayerCode::K { max_depth: 3 };
        let kp3 = PlayerCode::KP { max_depth: 3 };
        for (a, b) in pairs {
            let deck = |n: &str| Deck::from_file(&format!("example_decks/{n}.txt")).unwrap();
            for seed in 0..6u64 {
                let play = |code: &PlayerCode| {
                    let empty = Deck::default();
                    let players = vec![get_player(deck(a), &empty, code), get_player(deck(b), &empty, code)];
                    let mut game = Game::new(players, 22_000_000_000 + seed);
                    let mut moves = Vec::new();
                    while !game.is_game_over() {
                        moves.push(game.play_tick());
                    }
                    moves
                };
                assert!(play(&k3) == play(&kp3), "{a} v {b}, seed {seed}: kp3 and k3 differ");
            }
        }
    }
}
