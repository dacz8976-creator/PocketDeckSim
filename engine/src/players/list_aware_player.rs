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

#[cfg(test)]
mod tests {
    use super::super::{get_player, PlayerCode};
    use crate::{Deck, Game};

    /// With an empty opponent list and one sample, `b3` must be `k3` exactly, game for game, on the
    /// Sept 23 table's deals: the same value function, search settings and random streams, and a guess
    /// that fills nothing. Then every difference a b-tier shows comes from the guess alone. Both bots
    /// come from the production constructor. PDL_EQUIV_DEALS sets the deals per pairing (default 12).
    #[test]
    fn b3_with_an_empty_list_plays_k3_game_for_game() {
        let names = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"];
        let deals: u64 = std::env::var("PDL_EQUIV_DEALS").ok().and_then(|v| v.parse().ok()).unwrap_or(12);
        let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
        let deck = |n: usize| Deck::from_file(&format!("../decks/research/{}.txt", names[n])).unwrap();
        let empty = Deck::default();
        let k3 = PlayerCode::K { max_depth: 3 };
        let b3 = PlayerCode::B { max_depth: 3, opponent_ply: 0, samples: 1 };
        // Hydreigon v Lucario, Sceptile v Vespiquen, Altaria v Blaziken; the table's seed and seat rule.
        for pairing in [13usize, 23, 0] {
            let (a, b) = pairs[pairing];
            for i in 0..deals {
                let seed = 72_000_000 + pairing as u64 * 10_000 + i;
                let (d0, d1) = if i % 2 == 0 { (a, b) } else { (b, a) };
                let play = |code: &PlayerCode| {
                    let players = vec![get_player(deck(d0), &empty, code), get_player(deck(d1), &empty, code)];
                    let mut game = Game::new(players, seed);
                    let mut moves = Vec::new();
                    while !game.is_game_over() {
                        moves.push(game.play_tick());
                    }
                    (moves, game.get_state_clone().winner)
                };
                let (k3_moves, k3_winner) = play(&k3);
                let (b3_moves, b3_winner) = play(&b3);
                assert_eq!(k3_moves.len(), b3_moves.len(), "seed {seed}: game lengths differ");
                assert!(k3_moves == b3_moves, "seed {seed}: the moves differ");
                assert_eq!(k3_winner, b3_winner, "seed {seed}");
            }
        }
    }
}
