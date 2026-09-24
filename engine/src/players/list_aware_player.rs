//! Option B (rl/RUN5.md, reopened Sept 24): k3's search, with the opponent's hidden hand and deck
//! guessed from their known decklist instead of left Unknown.
//!
//! Blind, k3 stops pricing any line that reaches an Unknown card: the opponent's next draw, a
//! hand-reveal attack, a Copycat count's cards. The see-everything test showed real information
//! moves Hydreigon v Lucario two-thirds of the way to Limitless. This player gets its information
//! the legitimate way: each decision samples `samples` worlds consistent with everything visible
//! and the opponent's list, scores every candidate in each world with the wrapped search, and plays
//! the candidate with the best total. It never reads the real hidden cards.

use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::fmt::Debug;

use super::expectiminimax_player::{prefer_shorter_win, ExpectiMiniMaxPlayer};
use super::public_reply::PublicReplyProvenance;
use super::Player;
use crate::actions::Action;
use crate::observation::PlayerObservation;
use crate::{Deck, State};

pub struct ListAwarePlayer {
    pub search: ExpectiMiniMaxPlayer,
    /// The opponent's decklist: the prior the hidden cards are drawn from.
    pub opponent_list: Deck,
    pub samples: usize,
}

impl Debug for ListAwarePlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ListAwarePlayer(samples: {})", self.samples)
    }
}

impl Player for ListAwarePlayer {
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        observation: &PlayerObservation,
        possible_actions: &[Action],
    ) -> Action {
        // Same determinization domain as the default decision_fn, so sampling never shares a
        // stream with the search's own chance draws.
        let mut observation_rng =
            StdRng::seed_from_u64(rng.clone().next_u64() ^ 0x50444c5f4f425331);
        let mut totals = vec![0.0; possible_actions.len()];
        // A win distance only counts for the tie-break if every sampled world found the win.
        let mut win_distance: Vec<Option<usize>> = Vec::new();
        for sample in 0..self.samples.max(1) {
            let state =
                observation.search_state_with_opponent_list(&mut observation_rng, &self.opponent_list);
            let scores = self.search.score_candidates(
                rng,
                &state,
                possible_actions,
                PublicReplyProvenance::from_observation(observation),
            );
            for (i, (score, distance)) in scores.into_iter().enumerate() {
                totals[i] += score;
                if sample == 0 {
                    win_distance.push(distance);
                } else {
                    win_distance[i] = match (win_distance[i], distance) {
                        (Some(a), Some(b)) => Some(a.max(b)),
                        _ => None,
                    };
                }
            }
        }
        let best = (0..possible_actions.len())
            .max_by(|&a, &b| {
                totals[a]
                    .partial_cmp(&totals[b])
                    .unwrap()
                    .then_with(|| prefer_shorter_win(win_distance[a], win_distance[b]))
            })
            .unwrap();
        possible_actions[best].clone()
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        self.search.decide_omniscient(rng, state, possible_actions)
    }

    fn get_deck(&self) -> Deck {
        self.search.get_deck()
    }
}
