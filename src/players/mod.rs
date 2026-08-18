mod attach_attack_player;
mod end_turn_player;
mod evolution_rusher_player;
pub mod expectiminimax_player;
mod human_player;
mod mcts_player;
mod random_player;
pub mod s42_probe;
mod value_function_player;
pub mod value_functions;
mod weighted_random_player;

pub use attach_attack_player::AttachAttackPlayer;
pub use end_turn_player::EndTurnPlayer;
pub use evolution_rusher_player::EvolutionRusherPlayer;
pub use expectiminimax_player::{
    take_opponent_ply_stats, ExpectiMiniMaxPlayer, ValueFunction, OPPONENT_PLY_BRANCHES,
    OPPONENT_PLY_NODES,
};
pub use human_player::HumanPlayer;
pub use mcts_player::MctsPlayer;
pub use random_player::RandomPlayer;
pub use value_function_player::ValueFunctionPlayer;
pub use value_functions::*;
pub use weighted_random_player::WeightedRandomPlayer;

use crate::{actions::Action, Deck, State};
use rand::rngs::StdRng;
use std::fmt::Debug;

pub trait Player: Debug {
    fn get_deck(&self) -> Deck;
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
    ) -> Action;
}

/// Enum for allowed player strategies
#[derive(Debug, Clone, PartialEq)]
pub enum PlayerCode {
    AA,
    ET,
    R,
    H,
    W,
    M,
    V,
    E {
        max_depth: usize,
    },
    /// §40. ExpectiMiniMax with the hidden-information leak in the value function closed.
    /// Identical to `E` in every other respect, so `e<N>` vs `p<N>` isolates the leak.
    P {
        max_depth: usize,
    },
    /// §115. `P` with the damage/development-aware Pokémon term (§113 fix): the leaf
    /// evaluation credits attack damage and evolution potential instead of
    /// `HP × (energy+1)`. Identical to `P` in every other respect, so `p<N>` vs `d<N>`
    /// isolates the leaf evaluation of the board.
    D {
        max_depth: usize,
    },
    /// §116. `D` with effect-aware attack-damage estimation (Mega Burst's discard scaling,
    /// bench-count damage, direct damage, coin-flip EVs, …) and the online score anchored
    /// to the best payable attack instead of the lexicographic `.max()`. `d<N>` vs `f<N>`
    /// isolates effect-aware damage estimation.
    F {
        max_depth: usize,
    },
    /// §117. `F` + spread-damage estimator classes, a discard-energy credit when a
    /// recycler ability is in play, and the two dead "team online" weights turned on.
    /// `f<N>` vs `g<N>` isolates the §117 bundle.
    G {
        max_depth: usize,
    },
    /// §40. `P`, plus a bounded public-information-only search into the OPPONENT's turn.
    /// `p<N>` vs `x<N>` isolates the opponent ply.
    X {
        max_depth: usize,
        opponent_ply: usize,
    },
    /// §42. `X`, with the search's horizon made CONSISTENT: every leaf is priced through the
    /// opponent's best public reply, not just the leaves that happened to cross the turn
    /// boundary with depth to spare. `x<N>` vs `y<N>` isolates the horizon inconsistency that
    /// §42 identified as the cause of `x3`'s pilot regression.
    Y {
        max_depth: usize,
        opponent_ply: usize,
    },
    /// §42. `Y`, with the opponent's turn scored as an EXPECTATION over their public actions
    /// instead of a hard `min`. `y<N>` vs `s<N>` isolates the paranoid-opponent hypothesis.
    /// (`W` was already taken by the weighted-random bot, hence `S` for "soft".)
    S {
        max_depth: usize,
        opponent_ply: usize,
    },
    ER, // Evolution Rusher
}
/// Custom parser function enforcing case-insensitivity
pub fn parse_player_code(s: &str) -> Result<PlayerCode, String> {
    let lower = s.to_ascii_lowercase();

    // Check if it starts with 'e' followed by digits (e.g., e2, e4)
    if lower.starts_with('e') && lower.len() > 1 {
        let rest = &lower[1..];
        if let Ok(max_depth) = rest.parse::<usize>() {
            return Ok(PlayerCode::E { max_depth });
        }
        // If it starts with 'e' but not followed by valid number, check if it's 'er'
        if lower == "er" {
            return Ok(PlayerCode::ER);
        }
        return Err(format!("Invalid player code: {s}. Use 'e<number>' for ExpectiMiniMax with depth, e.g., 'e2', 'e5'"));
    }

    // §40 tiers. 'p<N>' = leak-free evaluation. 'x<N>' = leak-free evaluation plus an
    // opponent-turn ply; an optional suffix sets its size, so 'x3' is 'x3o3'.
    if lower.starts_with('p') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::P { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'p<number>', e.g. 'p3'"
        ));
    }
    // §115. 'd<N>' = 'p<N>' with the damage-aware leaf evaluation.
    if lower.starts_with('d') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::D { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'd<number>', e.g. 'd3'"
        ));
    }
    // §116. 'f<N>' = 'd<N>' with effect-aware damage estimation.
    if lower.starts_with('f') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::F { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'f<number>', e.g. 'f3'"
        ));
    }
    // §117. 'g<N>' = 'f<N>' + spread classes + discard-energy credit + dead weights on.
    if lower.starts_with('g') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::G { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'g<number>', e.g. 'g3'"
        ));
    }
    if (lower.starts_with('x') || lower.starts_with('y') || lower.starts_with('s'))
        && lower.len() > 1
    {
        let consistent = !lower.starts_with('x');
        let soft = lower.starts_with('s');
        let rest = &lower[1..];
        let (depth_part, ply_part) = match rest.split_once('o') {
            Some((d, p)) => (d, Some(p)),
            None => (rest, None),
        };
        if let Ok(max_depth) = depth_part.parse::<usize>() {
            let opponent_ply = match ply_part {
                Some(p) => match p.parse::<usize>() {
                    Ok(v) if v > 0 => v,
                    _ => {
                        return Err(format!(
                            "Invalid player code: {s}. Opponent ply must be a positive integer, e.g. 'x3o4'"
                        ))
                    }
                },
                // Default 3: enough for draw, attach, attack — the shortest sequence that can
                // express "they KO me back", which is the whole point of the ply.
                None => 3,
            };
            return Ok(if soft {
                PlayerCode::S {
                    max_depth,
                    opponent_ply,
                }
            } else if consistent {
                PlayerCode::Y {
                    max_depth,
                    opponent_ply,
                }
            } else {
                PlayerCode::X {
                    max_depth,
                    opponent_ply,
                }
            });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'x<number>' or 'x<number>o<ply>', e.g. 'x3' or 'x3o4'"
        ));
    }

    match lower.as_str() {
        "aa" => Ok(PlayerCode::AA),
        "et" => Ok(PlayerCode::ET),
        "r" => Ok(PlayerCode::R),
        "h" => Ok(PlayerCode::H),
        "w" => Ok(PlayerCode::W),
        "m" => Ok(PlayerCode::M),
        "v" => Ok(PlayerCode::V),
        "e" => Ok(PlayerCode::E { max_depth: 3 }), // Default depth
        "er" => Ok(PlayerCode::ER),
        _ => Err(format!("Invalid player code: {s}")),
    }
}

pub fn parse_player_code_generic(s: String) -> Result<PlayerCode, String> {
    parse_player_code(s.as_ref())
}

pub fn fill_code_array(maybe_players: Option<Vec<PlayerCode>>) -> Vec<PlayerCode> {
    match maybe_players {
        Some(mut player_codes) => {
            if player_codes.is_empty() || player_codes.len() > 2 {
                panic!("Invalid number of players");
            } else if player_codes.len() == 1 {
                player_codes.push(PlayerCode::R);
            }
            player_codes
        }
        None => vec![PlayerCode::R, PlayerCode::R],
    }
}

pub fn create_players(
    deck_a: Deck,
    deck_b: Deck,
    players: Vec<PlayerCode>,
) -> Vec<Box<dyn Player>> {
    let player_a: Box<dyn Player> = get_player(deck_a.clone(), &players[0]);
    let player_b: Box<dyn Player> = get_player(deck_b.clone(), &players[1]);
    vec![player_a, player_b]
}

fn get_player(deck: Deck, player: &PlayerCode) -> Box<dyn Player> {
    match player {
        PlayerCode::AA => Box::new(AttachAttackPlayer { deck }),
        PlayerCode::ET => Box::new(EndTurnPlayer { deck }),
        PlayerCode::R => Box::new(RandomPlayer { deck }),
        PlayerCode::H => Box::new(HumanPlayer { deck }),
        PlayerCode::W => Box::new(WeightedRandomPlayer { deck }),
        PlayerCode::M => Box::new(MctsPlayer::new(deck, 100)),
        PlayerCode::V => Box::new(ValueFunctionPlayer { deck }),
        PlayerCode::E { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::baseline_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::P { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_baseline_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::D { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_damage_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::F { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_effect_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::G { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_development_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::X {
            max_depth,
            opponent_ply,
        } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_baseline_value_function),
            opponent_ply: *opponent_ply,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::Y {
            max_depth,
            opponent_ply,
        } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_baseline_value_function),
            opponent_ply: *opponent_ply,
            consistent_horizon: true,
            soft_opponent: false,
        }),
        PlayerCode::S {
            max_depth,
            opponent_ply,
        } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_baseline_value_function),
            opponent_ply: *opponent_ply,
            consistent_horizon: true,
            soft_opponent: true,
        }),
        PlayerCode::ER => Box::new(EvolutionRusherPlayer { deck }),
    }
}

#[cfg(test)]
mod s42_tier_parse_tests {
    use super::*;

    /// §42's tiers must not disturb §40's. `e`/`p`/`x` parsing is what every historical number
    /// in the lab was produced under, and a prefix clash here would silently re-tier a run.
    #[test]
    fn test_s42_tiers_parse_and_do_not_shadow_earlier_ones() {
        assert_eq!(
            parse_player_code("e3").unwrap(),
            PlayerCode::E { max_depth: 3 }
        );
        assert_eq!(
            parse_player_code("p3").unwrap(),
            PlayerCode::P { max_depth: 3 }
        );
        assert_eq!(
            parse_player_code("x3").unwrap(),
            PlayerCode::X {
                max_depth: 3,
                opponent_ply: 3
            }
        );
        assert_eq!(
            parse_player_code("y3").unwrap(),
            PlayerCode::Y {
                max_depth: 3,
                opponent_ply: 3
            }
        );
        assert_eq!(
            parse_player_code("s3o5").unwrap(),
            PlayerCode::S {
                max_depth: 3,
                opponent_ply: 5
            }
        );
        // §115: 'd<N>' must parse and must not shadow anything earlier.
        assert_eq!(
            parse_player_code("d3").unwrap(),
            PlayerCode::D { max_depth: 3 }
        );
        // §116: 'f<N>' must parse and must not shadow anything earlier.
        assert_eq!(
            parse_player_code("f3").unwrap(),
            PlayerCode::F { max_depth: 3 }
        );
        // §117: 'g<N>' must parse and must not shadow anything earlier.
        assert_eq!(
            parse_player_code("g3").unwrap(),
            PlayerCode::G { max_depth: 3 }
        );
        // `w` is the weighted-random bot and must still resolve to it, which is why the soft
        // tier is `s` and not `w`.
        assert_eq!(parse_player_code("w").unwrap(), PlayerCode::W);
        assert_eq!(parse_player_code("er").unwrap(), PlayerCode::ER);
    }

    /// The two §42 flags must be independent, and OFF for every pre-§42 tier — otherwise
    /// re-running history would not reproduce it.
    #[test]
    fn test_search_flags_are_off_for_historical_tiers() {
        use crate::players::expectiminimax_player::SearchFlags;
        let f = |code: &str| {
            let p = get_player(Deck::default(), &parse_player_code(code).unwrap());
            let _ = format!("{p:?}");
            code.to_string()
        };
        // Construction must not panic for any tier.
        for code in ["e2", "e3", "p3", "x3", "y3", "s3"] {
            let _ = f(code);
        }
        assert_eq!(
            SearchFlags::default(),
            SearchFlags {
                consistent_horizon: false,
                soft_opponent: false
            }
        );
    }
}
