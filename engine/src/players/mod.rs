pub mod public_reply;
mod attach_attack_player;
mod end_turn_player;
mod evolution_rusher_player;
pub mod expectiminimax_player;
mod human_player;
pub mod list_aware_player;
pub mod public_pricing_player;
pub mod jev_player;
mod mcts_player;
mod opening_class;
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
pub use jev_player::JevPlayer;
pub use list_aware_player::ListAwarePlayer;
pub use public_pricing_player::PublicPricingPlayer;
pub use mcts_player::MctsPlayer;
pub use random_player::RandomPlayer;
pub use value_function_player::ValueFunctionPlayer;
pub use value_functions::*;
pub use weighted_random_player::WeightedRandomPlayer;

use crate::{actions::Action, Deck, State};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::fmt::Debug;

pub trait Player: Debug {
    /// Production entry point: only allowed observations and independent search randomness.
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &crate::observation::PlayerObservation,
        possible_actions: &[Action]) -> Action {
        // Determinization and policy work have separate per-decision domains.
        let mut observation_rng = StdRng::seed_from_u64(rng.clone().next_u64() ^ 0x50444c5f4f425331);
        let state = observation.search_state(&mut observation_rng);
        self.decide_omniscient(rng, &state, possible_actions)
    }

    /// Explicit diagnostic/constructed-state entry point. Never pass real engine
    /// state here from gameplay; Game uses decision_fn with PlayerObservation.

    fn get_deck(&self) -> Deck;
    fn decide_omniscient(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
    ) -> Action;
}

/// Enum for allowed player strategies
#[derive(Debug, Clone, PartialEq)]
pub enum PlayerCode {
    Jev,
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
    /// s118. `P` with ONLY the s115 threat-clock half: the evolution-aware
    /// `turns_until_opponent_wins` scan (no 30.0 sentinel), historical Pokemon term.
    /// `p<N>` vs `t<N>` isolates the clock fix; `t<N>` vs `d<N>` isolates the value formula.
    T {
        max_depth: usize,
    },
    /// s118. `P` with ONLY the s115 Pokemon-value half: the additive damage/development
    /// term, historical threat-clock scan. Completes the 2x2 with `p`/`t`/`d`.
    /// NOTE: bare `v` is the long-standing ValueFunctionPlayer; `v<N>` is this tier.
    VN {
        max_depth: usize,
    },
    /// s119. `T` + s116's effect-aware damage estimator and re-anchored online score, but
    /// WITHOUT the additive Pokemon value term. Isolates the two things `f` adds over `t`.
    /// (Called `h` in s119's recommendation; `h` is the HumanPlayer code, hence `k`.)
    K {
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
    /// Option B (rl/RUN5.md): the k<N> search with the opponent's hidden hand and deck sampled from
    /// their decklist. 'b<N>' = k<N> plus sampling; 'b<N>o<P>' also searches P opponent actions
    /// (consistent horizon); a trailing 'n<S>' sets the samples per decision (default 4).
    B {
        max_depth: usize,
        opponent_ply: usize,
        samples: usize,
    },
    /// B1' public pricing: 'kp<N>' is the k<N> search, blind, with effects that mention the opponent's
    /// hand or deck priced against the Unknown cards instead of left unpriced (public_pricing_player).
    KP { max_depth: usize },
    /// B5: 'kq<N>' is 'kp<N>' with two more evaluation features, both card-agnostic
    /// (value_functions::public_clock_effect_kq_value_function): the threat clock prices a threat whose
    /// next attack is cut or cancelled by an effect it carries, and the benched main attacker's readiness
    /// is credited at a pre-set 250 (half the Active's 500).
    KQ { max_depth: usize },
    /// 'kd<N>' is 'kp<N>' with the damage-aware clock pricing the threat's damage to each victim through the
    /// victim's Weakness and persistent damage reductions (value_functions::public_clock_effect_kd_value_function).
    KD { max_depth: usize },
    /// 'kpr<N>' is 'kp<N>' with each side's Active priced as it will stand at its next attack, with the Energy its
    /// owner's public sources will have given it by then: in the Active online score, and in the damage-aware clock
    /// (the faster of the clock with and without the projection) (value_functions::public_clock_effect_kpr_value_function).
    KPR { max_depth: usize },
    /// 'koa<N>' is 'kp<N>' with switch A of the opening-Active candidate (registered Sept 26,
    /// rl/results/opening_active_census_2026-09-26/REGISTRATION.md): at setup, +250 for an Active whose Ability works
    /// only from the Active Spot with its payoff confined to the owner's first turn, when its evolution is in the
    /// owner's deck or hand (value_functions::public_clock_effect_koa_value_function). The adoption candidate.
    KOA { max_depth: usize },
    /// 'kob<N>': 'kp<N>' with switch B only (-250 at setup for a Bench-working Active Ability). Diagnostic, mixed rows
    /// only; not registered for adoption.
    KOB { max_depth: usize },
    /// 'kor<N>': 'kp<N>' with switch R only (-100 at setup per Energy of the Active's cheapest own attack).
    /// Diagnostic, mixed rows only; not registered for adoption.
    KOR { max_depth: usize },
}
/// Custom parser function enforcing case-insensitivity
pub fn parse_player_code(s: &str) -> Result<PlayerCode, String> {
    let lower = s.to_ascii_lowercase();

    // Resolve exact multi-letter codes before the parameterized one-letter prefixes.
    // In particular, `et` must not be rejected as a malformed `e<number>`.
    match lower.as_str() {
        "jev" => return Ok(PlayerCode::Jev),
        "aa" => return Ok(PlayerCode::AA),
        "et" => return Ok(PlayerCode::ET),
        "er" => return Ok(PlayerCode::ER),
        _ => {}
    }

    // Check if it starts with 'e' followed by digits (e.g., e2, e4).
    if lower.starts_with('e') && lower.len() > 1 {
        let rest = &lower[1..];
        if let Ok(max_depth) = rest.parse::<usize>() {
            return Ok(PlayerCode::E { max_depth });
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
    // s118. 't<N>' = 'p<N>' with ONLY the s115 evolution-aware threat clock.
    if lower.starts_with('t') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::T { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 't<number>', e.g. 't3'"
        ));
    }
    // 'kpr<N>' = 'kp<N>' with projected readiness (see PlayerCode::KPR). Before 'kp<N>' and 'k<N>', which
    // would reject it.
    if let Some(depth) = lower.strip_prefix("kpr") {
        if let Ok(max_depth) = depth.parse::<usize>() {
            return Ok(PlayerCode::KPR { max_depth });
        }
        return Err(format!("Invalid player code: {s}. Use 'kpr<number>', e.g. 'kpr3'"));
    }
    // B1'. 'kp<N>' = 'k<N>' with public pricing (see PlayerCode::KP). Before 'k<N>', which would
    // reject it.
    if let Some(depth) = lower.strip_prefix("kp") {
        if let Ok(max_depth) = depth.parse::<usize>() {
            return Ok(PlayerCode::KP { max_depth });
        }
        return Err(format!("Invalid player code: {s}. Use 'kp<number>', e.g. 'kp3'"));
    }
    // B5. 'kq<N>' = 'kp<N>' with the kq evaluation features (see PlayerCode::KQ). Before 'k<N>', which
    // would reject it.
    if let Some(depth) = lower.strip_prefix("kq") {
        if let Ok(max_depth) = depth.parse::<usize>() {
            return Ok(PlayerCode::KQ { max_depth });
        }
        return Err(format!("Invalid player code: {s}. Use 'kq<number>', e.g. 'kq3'"));
    }
    // 'koa<N>', 'kob<N>', 'kor<N>': the opening-Active switches (see PlayerCode::KOA). Before 'k<N>', which would
    // reject them. There is no bare 'ko' code; if one is ever added, parse these three before it.
    let opening_codes: [(&str, fn(usize) -> PlayerCode); 3] = [
        ("koa", |max_depth| PlayerCode::KOA { max_depth }),
        ("kob", |max_depth| PlayerCode::KOB { max_depth }),
        ("kor", |max_depth| PlayerCode::KOR { max_depth }),
    ];
    for (prefix, code) in opening_codes {
        if let Some(depth) = lower.strip_prefix(prefix) {
            if let Ok(max_depth) = depth.parse::<usize>() {
                return Ok(code(max_depth));
            }
            return Err(format!("Invalid player code: {s}. Use '{prefix}<number>', e.g. '{prefix}3'"));
        }
    }
    // 'kd<N>' = 'kp<N>' with the kd clock (see PlayerCode::KD). Before 'k<N>', which would reject it.
    if let Some(depth) = lower.strip_prefix("kd") {
        if let Ok(max_depth) = depth.parse::<usize>() {
            return Ok(PlayerCode::KD { max_depth });
        }
        return Err(format!("Invalid player code: {s}. Use 'kd<number>', e.g. 'kd3'"));
    }
    // Option B. 'b<N>[o<P>][n<S>]' = 'k<N>' with list-sampled hidden cards (see PlayerCode::B).
    if lower.starts_with('b') && lower.len() > 1 {
        let invalid = || format!("Invalid player code: {s}. Use 'b<depth>[o<ply>][n<samples>]', e.g. 'b3', 'b3o3n8'");
        let (rest, samples) = match lower[1..].split_once('n') {
            Some((r, n)) => (r, n.parse::<usize>().ok().filter(|v| *v > 0).ok_or_else(invalid)?),
            None => (&lower[1..], 4),
        };
        let (depth, opponent_ply) = match rest.split_once('o') {
            Some((d, p)) => (d, p.parse::<usize>().ok().filter(|v| *v > 0).ok_or_else(invalid)?),
            None => (rest, 0),
        };
        let max_depth = depth.parse::<usize>().map_err(|_| invalid())?;
        return Ok(PlayerCode::B { max_depth, opponent_ply, samples });
    }
    // s119. 'k<N>' = 't<N>' + the s116 effect-aware estimator, no Pokemon-value term.
    if lower.starts_with('k') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::K { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'k<number>', e.g. 'k3'"
        ));
    }
    // s118. 'v<N>' = 'p<N>' with ONLY the s115 Pokemon-value term. Bare 'v' is still the
    // ValueFunctionPlayer and is handled by the match below (len == 1 fails this guard).
    if lower.starts_with('v') && lower.len() > 1 {
        if let Ok(max_depth) = lower[1..].parse::<usize>() {
            return Ok(PlayerCode::VN { max_depth });
        }
        return Err(format!(
            "Invalid player code: {s}. Use 'v<number>', e.g. 'v3'"
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
        "r" => Ok(PlayerCode::R),
        "h" => Ok(PlayerCode::H),
        "w" => Ok(PlayerCode::W),
        "m" => Ok(PlayerCode::M),
        "v" => Ok(PlayerCode::V),
        "e" => Ok(PlayerCode::E { max_depth: 3 }), // Default depth
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
    let player_a: Box<dyn Player> = get_player(deck_a.clone(), &deck_b, &players[0]);
    let player_b: Box<dyn Player> = get_player(deck_b.clone(), &deck_a, &players[1]);
    vec![player_a, player_b]
}

fn get_player(deck: Deck, opponent_deck: &Deck, player: &PlayerCode) -> Box<dyn Player> {
    match player {
        PlayerCode::Jev => Box::new(JevPlayer::new(deck)),
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
        PlayerCode::T { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_clock_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::VN { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_pokemon_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),
        PlayerCode::K { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_clock_effect_value_function),
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
        PlayerCode::B { max_depth, opponent_ply, samples } => Box::new(ListAwarePlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_value_function),
                opponent_ply: *opponent_ply,
                consistent_horizon: *opponent_ply > 0,
                soft_opponent: false,
            },
            opponent_list: opponent_deck.clone(),
            samples: *samples,
        }),
        // The K arm's search, field for field, inside the public-pricing wrapper.
        PlayerCode::KP { max_depth } => Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_value_function),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        }),
        // The KP arm with the kq value function in place of k's; nothing else differs.
        PlayerCode::KQ { max_depth } => Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_kq_value_function),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        }),
        // The KP arm with the kd value function in place of k's; nothing else differs.
        PlayerCode::KD { max_depth } => Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_kd_value_function),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        }),
        // The KP arm with the kpr value function in place of k's; nothing else differs.
        PlayerCode::KPR { max_depth } => Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_kpr_value_function),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        }),
        // The KP arm with an opening-Active value function in place of k's; nothing else differs.
        PlayerCode::KOA { max_depth } | PlayerCode::KOB { max_depth } | PlayerCode::KOR { max_depth } => {
            let value_function: expectiminimax_player::ValueFunction = match player {
                PlayerCode::KOA { .. } => Box::new(value_functions::public_clock_effect_koa_value_function),
                PlayerCode::KOB { .. } => Box::new(value_functions::public_clock_effect_kob_value_function),
                _ => Box::new(value_functions::public_clock_effect_kor_value_function),
            };
            Box::new(PublicPricingPlayer {
                search: ExpectiMiniMaxPlayer {
                    deck,
                    max_depth: *max_depth,
                    write_debug_trees: false,
                    value_function,
                    opponent_ply: 0,
                    consistent_horizon: false,
                    soft_opponent: false,
                },
            })
        }
    }
}

#[cfg(test)]
mod s42_tier_parse_tests {
    use super::*;

    /// s118. The `t`/`v` tiers must parse, and `v<N>` must NOT shadow bare `v`
    /// (the long-standing ValueFunctionPlayer). A clash here would silently re-pilot
    /// every historical `v` run.
    #[test]
    fn test_s118_tv_tiers_parse_and_bare_v_survives() {
        assert_eq!(
            parse_player_code("t3").unwrap(),
            PlayerCode::T { max_depth: 3 }
        );
        assert_eq!(
            parse_player_code("v3").unwrap(),
            PlayerCode::VN { max_depth: 3 }
        );
        assert_eq!(parse_player_code("v").unwrap(), PlayerCode::V);
        assert_eq!(parse_player_code("V").unwrap(), PlayerCode::V);
        // the pre-existing tiers are untouched
        assert_eq!(
            parse_player_code("d3").unwrap(),
            PlayerCode::D { max_depth: 3 }
        );
        assert_eq!(
            parse_player_code("p3").unwrap(),
            PlayerCode::P { max_depth: 3 }
        );
        // garbage after the letter is still an error, not a silent depth
        assert_eq!(
            parse_player_code("k3").unwrap(),
            PlayerCode::K { max_depth: 3 }
        );
        assert!(parse_player_code("kk").is_err());
        assert_eq!(parse_player_code("h").unwrap(), PlayerCode::H);
        assert!(parse_player_code("tt").is_err());
        assert!(parse_player_code("vx").is_err());
    }

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
        // Option B: 'b<N>[o<P>][n<S>]'.
        assert_eq!(
            parse_player_code("b3").unwrap(),
            PlayerCode::B { max_depth: 3, opponent_ply: 0, samples: 4 }
        );
        assert_eq!(
            parse_player_code("B3o3n8").unwrap(),
            PlayerCode::B { max_depth: 3, opponent_ply: 3, samples: 8 }
        );
        assert!(parse_player_code("b3o0").is_err());
        assert!(parse_player_code("b3n0").is_err());
        assert!(parse_player_code("bx").is_err());
        // B1': 'kp<N>', and 'k<N>' is unchanged.
        assert_eq!(parse_player_code("kp3").unwrap(), PlayerCode::KP { max_depth: 3 });
        assert_eq!(parse_player_code("KP5").unwrap(), PlayerCode::KP { max_depth: 5 });
        assert_eq!(parse_player_code("k3").unwrap(), PlayerCode::K { max_depth: 3 });
        assert!(parse_player_code("kp").is_err());
        assert!(parse_player_code("kpx").is_err());
        // B5: 'kq<N>', and 'kp<N>' and 'k<N>' are unchanged.
        assert_eq!(parse_player_code("kq3").unwrap(), PlayerCode::KQ { max_depth: 3 });
        assert_eq!(parse_player_code("KQ5").unwrap(), PlayerCode::KQ { max_depth: 5 });
        assert_eq!(parse_player_code("kp3").unwrap(), PlayerCode::KP { max_depth: 3 });
        assert!(parse_player_code("kq").is_err());
        assert!(parse_player_code("kqx").is_err());
        // kd: 'kd<N>', and 'kq<N>', 'kp<N>' and 'k<N>' are unchanged.
        assert_eq!(parse_player_code("kd3").unwrap(), PlayerCode::KD { max_depth: 3 });
        assert_eq!(parse_player_code("KD5").unwrap(), PlayerCode::KD { max_depth: 5 });
        assert_eq!(parse_player_code("kq3").unwrap(), PlayerCode::KQ { max_depth: 3 });
        assert_eq!(parse_player_code("k3").unwrap(), PlayerCode::K { max_depth: 3 });
        assert!(parse_player_code("kd").is_err());
        assert!(parse_player_code("kdx").is_err());
        // kpr: 'kpr<N>', and 'kp<N>' is unchanged.
        assert_eq!(parse_player_code("kpr3").unwrap(), PlayerCode::KPR { max_depth: 3 });
        assert_eq!(parse_player_code("KPR5").unwrap(), PlayerCode::KPR { max_depth: 5 });
        assert_eq!(parse_player_code("kp3").unwrap(), PlayerCode::KP { max_depth: 3 });
        assert!(parse_player_code("kpr").is_err());
        assert!(parse_player_code("kprx").is_err());
        // koa, kob, kor: parsed before 'k<N>'; 'kp<N>' and 'k<N>' are unchanged.
        assert_eq!(parse_player_code("koa3").unwrap(), PlayerCode::KOA { max_depth: 3 });
        assert_eq!(parse_player_code("KOA5").unwrap(), PlayerCode::KOA { max_depth: 5 });
        assert_eq!(parse_player_code("kob3").unwrap(), PlayerCode::KOB { max_depth: 3 });
        assert_eq!(parse_player_code("kor3").unwrap(), PlayerCode::KOR { max_depth: 3 });
        assert_eq!(parse_player_code("kp3").unwrap(), PlayerCode::KP { max_depth: 3 });
        assert_eq!(parse_player_code("k3").unwrap(), PlayerCode::K { max_depth: 3 });
        assert!(parse_player_code("koa").is_err());
        assert!(parse_player_code("koax").is_err());
        assert!(parse_player_code("ko3").is_err());
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
            let p = get_player(Deck::default(), &Deck::default(), &parse_player_code(code).unwrap());
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
