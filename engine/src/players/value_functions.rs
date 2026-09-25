// Collection of value functions for ExpectiMiniMaxPlayer
//
// Each value function evaluates a game state from a player's perspective
// and returns a score (higher is better for that player)

use log::trace;

use crate::actions::abilities::AbilityMechanic;
use crate::actions::attacks::{BenchDamageFilter, BenchSide, Mechanic};
use crate::actions::SimpleAction;
use crate::actions::{
    ability_mechanic_from_effect, get_in_play_ability_mechanic, has_any_in_play_ability, EFFECT_MECHANIC_MAP,
};
use crate::card_logic::get_highest_evolutions;
use crate::effects::{CardEffect, TurnEffect};
use crate::hooks::{
    energy_missing, get_retreat_cost_for_player, get_stage, persistent_defender_damage,
    special_condition_blocks_attack_or_retreat, to_playable_card, DamageModifierContext, DefenderHit,
};
use crate::models::{Attack, Card, EnergyType, PlayedCard, StatusCondition, TrainerType, BASIC_STAGE};
use crate::state::GameOutcome;
use crate::State;

/// Coefficients for the parametric value function
#[derive(Debug, Clone, Copy)]
pub struct ValueFunctionParams {
    pub points: f64,
    pub pokemon_value: f64,
    pub hand_size: f64,
    pub deck_size: f64,
    pub active_retreat_cost: f64,
    pub active_pokemon_online_score: f64,
    pub active_safety: f64,
    pub active_has_tool: f64,
    pub is_winner: f64,
    pub turns_until_opponent_wins: f64,
    pub online_pokemon_count: f64,
    pub energy_distance_to_online: f64,
    pub opponent_discard_size: f64,
}

impl ValueFunctionParams {
    /// Baseline parameters (same as original baseline function)
    pub const fn baseline() -> Self {
        Self {
            points: 10_000.0,
            pokemon_value: 1.0,
            hand_size: 1.0,
            deck_size: 1.0,
            active_retreat_cost: 1.0,
            active_pokemon_online_score: 500.0,
            active_safety: 1.0,
            active_has_tool: 10.0,
            is_winner: 100_000.0,
            turns_until_opponent_wins: 100.0,
            online_pokemon_count: 0.0,
            energy_distance_to_online: 0.0,
            opponent_discard_size: 0.1,
        }
    }

    /// §117 — the `g` tier's parameters: `baseline()` with the two dead
    /// "is-my-team-coming-online" features turned ON (they have been computed and
    /// multiplied by 0.0 in every run this project ever did). Values fixed in
    /// `s117_prereg.txt`: +50 per online Pokémon, −25 per missing energy across the team
    /// (own distance high = bad, hence negative).
    pub const fn development() -> Self {
        Self {
            online_pokemon_count: 50.0,
            energy_distance_to_online: -25.0,
            ..Self::baseline()
        }
    }

    /// Variant parameters
    pub const fn variant() -> Self {
        Self {
            points: 10_000.0,
            pokemon_value: 1.0,
            hand_size: 1.0,
            deck_size: 1.0,
            active_retreat_cost: 1.0,
            active_pokemon_online_score: 500.0,
            active_safety: 1.0,
            active_has_tool: 10.0,
            is_winner: 100_000.0,
            turns_until_opponent_wins: 100.0,
            online_pokemon_count: 0.0,
            energy_distance_to_online: 0.0,
            opponent_discard_size: 0.1,
        }
    }
}

pub fn baseline_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function(state, myself, &ValueFunctionParams::baseline())
}

/// Hidden-information-respecting variant of [`baseline_value_function`]. (§40)
///
/// The baseline function computes the OPPONENT's `active_pokemon_online_score` by scanning
/// the opponent's deck and hand for evolutions of their Active. That is information a real
/// player cannot see, it is weighted 500.0, and it is measured at a 125-point evaluation
/// swing on a 116-point baseline with deck size and hand size held constant — see
/// `tests/value_function_hidden_info_test.rs`.
///
/// This version evaluates the opponent's Active as the card actually ON THE BOARD, and is
/// otherwise identical. The player's own zones are still read in full, because a player may
/// legitimately see their own deck and hand.
pub fn public_baseline_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex(state, myself, &ValueFunctionParams::baseline(), true)
}

/// §115 — the `d` tier. [`public_baseline_value_function`] with ONE substitution: the
/// Pokémon term is [`calculate_pokemon_value_damage_aware`] instead of
/// [`calculate_pokemon_value`]. Everything else is identical, so `p<N>` vs `d<N>`
/// isolates the leaf evaluation of the board.
///
/// Motivation (§113): `calculate_pokemon_value` scores a Pokémon as
/// `remaining_HP × (relevant_energy + 1)` and never reads attack damage, so an undamaged
/// Bulbasaur (70 HP, 2-energy attack) outscores the Ivysaur it evolves into (100 HP,
/// 1-energy utility attack) 210 to 200 — evolution is priced as a downgrade and setup
/// decks never assemble (0 evolutions in 240 logged games; p3/p4/p5 identical, so it is
/// the leaf, not the depth).
pub fn public_damage_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex2(state, myself, &ValueFunctionParams::baseline(), true, true)
}

/// §116 — the `f` tier. [`public_damage_value_function`] with two substitutions:
/// attack damage everywhere in the d-path is [`estimated_attack_damage`] instead of raw
/// `fixed_damage`, and the ACTIVE's online score anchors to the target's best PAYABLE
/// attack (fewest missing, then highest estimated damage) instead of the
/// lexicographically-"most expensive" one. Everything else is identical, so `d<N>` vs
/// `f<N>` isolates effect-aware damage estimation.
pub fn public_effect_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex3(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        true,
        true,
    )
}

/// §117 — the `g` tier. [`public_effect_value_function`] with three additions, fixed in
/// `s117_prereg.txt`: (a) four more estimator classes (random-spread damage — the Draco
/// Meteor family — plus per-self-energy random hits and discard-per-heads EV); (b) a
/// discard-energy credit when a discard-recycler ability (Dragon's Blessing class) is in
/// play — the fuel reserve the bot demonstrably uses (~2 activations/game in every tier)
/// but valued at 0 by every tier before this one; (c) the two dead "team coming online"
/// features turned on via [`ValueFunctionParams::development`]. `f<N>` vs `g<N>`
/// isolates this bundle.
pub fn public_development_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex4(
        state,
        myself,
        &ValueFunctionParams::development(),
        true,
        true,
        true,
        true,
    )
}

/// s119 - the `k` tier (called `h` in s119's recommendation; `h` was already taken by the
/// HumanPlayer code, so it ships as `k`).
///
/// The isolation s119 asked for: the evolution-aware threat CLOCK **plus** s116's
/// effect-aware damage estimator and re-anchored online score, but **NO** additive Pokemon
/// VALUE term - the historical `HP x (energy+1)` leaf stays.
///
/// Why: s119 measured t3 (clock, no value) at r=+0.426 against real matchup win rates,
/// d3 (clock + value reading RAW `fixed_damage`) at +0.412, and f3 (clock + value reading
/// the effect-aware estimator) at +0.498. So the value term HURTS on raw damage and HELPS
/// on corrected damage. `k` separates the two things f3 added on top of t3: if k lands
/// between t3 and f3 (closer to t3), the value term is doing real work once its input is
/// right. If k MATCHES f3, the value term is inert and the whole gain is the estimator.
pub fn public_clock_effect_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex5(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        false, // value_aware  - NO additive Pokemon value term
        true,  // clock_aware  - evolution-aware threat scan
        true,  // effect_aware - s116 estimator + re-anchored online score
        false,
    )
}

/// B5 - the `kq` tier (players/mod.rs `KQ`, piloted like `kp`): `k`'s evaluator plus two card-agnostic
/// features, both fixed before any table was run:
/// - next-attack reduction in the threat clock: when the threatening Active carries effects that cut or
///   cancel its next attack, the first knockout's first attack turn is priced through them, or through the
///   owner's escape (a ready benched attacker), whichever is faster ([`first_attack_turn`]);
/// - benched-attacker readiness: `k`'s online score for the best benched attacker, on both sides as for
///   the Active, weighted [`KQ_BENCH_ATTACKER_WEIGHT`] = 250, half the Active's 500
///   ([`best_benched_attacker_online_score`]).
/// `k`, `kp` and every older tier reach [`parametric_value_function_ex6`] through
/// [`parametric_value_function_ex5`] with [`EvalFeatures::OFF`], where neither runs.
pub fn public_clock_effect_kq_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        false,
        true,
        true,
        false,
        EvalFeatures::KQ,
    )
}

/// The `kd` tier (players/mod.rs `KD`, piloted like `kp`): `k`'s evaluator with the damage-aware clock pricing
/// the threat's damage to each victim through the victim's Weakness and persistent damage reductions
/// ([`persistent_defender_damage`]), on both sides. kq's two features stay off. Fixed before any table was run.
pub fn public_clock_effect_kd_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        false,
        true,
        true,
        false,
        EvalFeatures::KD,
    )
}

/// The `kpr` tier (players/mod.rs `KPR`, piloted like `kp`): `k`'s evaluator with each side's Active priced as it
/// will stand at its next attack: its attached Energy plus the Energy its owner's public sources will have given it
/// by then ([`projected_active_energy`]). That copy is used in the Active online score (weight 500, both sides) and,
/// for the threatening Active's missing Energy and damage, in the damage-aware clock, which takes the faster of the
/// clock with and without it. kq's and kd's features stay off. Fixed before any table was run.
pub fn public_clock_effect_kpr_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        false,
        true,
        true,
        false,
        EvalFeatures::KPR,
    )
}

/// Weight of [`best_benched_attacker_online_score`] in `kq`: half the Active online score's 500 in
/// [`ValueFunctionParams::baseline`]. Pre-set before any A/B and not tuned on the table.
pub const KQ_BENCH_ATTACKER_WEIGHT: f64 = 250.0;

/// The evaluator switches added after `kp`. [`EvalFeatures::OFF`] is every older tier: no new code runs.
#[derive(Debug, Clone, Copy)]
struct EvalFeatures {
    /// kq: next-attack reduction in the threat clock ([`first_attack_turn`]).
    next_attack_reduction: bool,
    /// kq: weight of the benched-attacker readiness term ([`best_benched_attacker_online_score`]).
    bench_attacker_weight: f64,
    /// kd: the clock's damage to each victim goes through its Weakness and persistent reductions
    /// ([`persistent_defender_damage`]). Not combined with `next_attack_reduction`: no player code sets both, and
    /// if both were set, a knockout priced by kq's first attack turn would keep kq's arithmetic.
    defender_modifiers: bool,
    /// kpr: the Active online score and the damage-aware clock count the Energy each Active will have at its next
    /// attack ([`projected_active_energy`]), not only the Energy attached now.
    projected_readiness: bool,
}

impl EvalFeatures {
    const OFF: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: false,
        projected_readiness: false,
    };
    const KQ: EvalFeatures = EvalFeatures {
        next_attack_reduction: true,
        bench_attacker_weight: KQ_BENCH_ATTACKER_WEIGHT,
        defender_modifiers: false,
        projected_readiness: false,
    };
    const KD: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: true,
        projected_readiness: false,
    };
    const KPR: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: false,
        projected_readiness: true,
    };
}

/// s118 - the `t` tier. The s115 change with ONLY its threat-clock half enabled: the
/// evolution-aware `turns_until_opponent_wins` scan (no 30.0 sentinel), with the
/// HISTORICAL `HP x (energy+1)` Pokemon term. `p<N>` vs `t<N>` isolates the clock fix.
pub fn public_clock_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex5(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        false,
        true,
        false,
        false,
    )
}

/// s118 - the `v` tier. The s115 change with ONLY its Pokemon-value half enabled: the
/// additive damage/development-aware Pokemon term, with the HISTORICAL threat-clock scan
/// (30.0 sentinel intact). `p<N>` vs `v<N>` isolates the leaf value formula.
///
/// NOTE the adjacency: bare `v` is the long-standing `ValueFunctionPlayer`. `v<N>` (with a
/// depth digit) is this tier. Guarded by a parse test.
pub fn public_pokemon_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex5(
        state,
        myself,
        &ValueFunctionParams::baseline(),
        true,
        true,
        false,
        false,
        false,
    )
}


/// A variant of the baseline value function
pub fn variant_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function(state, myself, &ValueFunctionParams::variant())
}

/// Parametric value function that uses the provided coefficients.
///
/// Preserved bit-for-bit: it reads the opponent's hidden zones, as it always has. Callers
/// that want the hidden-information-respecting behaviour use
/// [`parametric_value_function_ex`] with `public_eval = true`.
pub fn parametric_value_function(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
) -> f64 {
    parametric_value_function_ex(state, myself, params, false)
}

/// [`parametric_value_function`], plus a switch for whether the OPPONENT's hidden zones
/// (deck and hand CONTENTS) may be read when scoring how "online" their Active is. (§40)
///
/// `public_eval = false` reproduces the historical behaviour exactly. `public_eval = true`
/// restricts the opponent's evaluation to public information.
pub fn parametric_value_function_ex(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
) -> f64 {
    parametric_value_function_ex2(state, myself, params, public_eval, false)
}

/// [`parametric_value_function_ex`], plus the §115 `damage_aware` switch. `false`
/// reproduces the historical behaviour bit-for-bit (the branch selects the same
/// [`calculate_pokemon_value`] call); `true` swaps in the damage/development-aware
/// Pokémon term used by the `d` tier.
pub fn parametric_value_function_ex2(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    damage_aware: bool,
) -> f64 {
    parametric_value_function_ex3(state, myself, params, public_eval, damage_aware, false)
}

/// [`parametric_value_function_ex2`], plus the §116 `effect_aware` switch. `false`
/// reproduces the d path bit-for-bit; `true` swaps `fixed_damage` for
/// [`estimated_attack_damage`] throughout and re-anchors the online score.
pub fn parametric_value_function_ex3(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    damage_aware: bool,
    effect_aware: bool,
) -> f64 {
    parametric_value_function_ex4(
        state,
        myself,
        params,
        public_eval,
        damage_aware,
        effect_aware,
        false,
    )
}

/// [`parametric_value_function_ex3`], plus the §117 `reserve_aware` switch (the extra
/// estimator classes + the discard-energy credit). `false` reproduces the f path
/// bit-for-bit; the dead-weight change rides in `params`, not in a flag.
#[allow(clippy::too_many_arguments)]
pub fn parametric_value_function_ex4(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    damage_aware: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    // s118: the historical `damage_aware` switch drove BOTH halves of the s115 change at
    // once. It is preserved here as "both on", so every existing tier is bit-identical.
    parametric_value_function_ex5(
        state,
        myself,
        params,
        public_eval,
        damage_aware,
        damage_aware,
        effect_aware,
        reserve_aware,
    )
}

/// [`parametric_value_function_ex4`], with the s115 change SPLIT into its two independent
/// halves (s118).
///
/// s115 shipped as one flag but was two logically separate edits, and `d<N>` therefore
/// confounds them:
///   * `value_aware`  - the additive Pokemon term (HP + dmg/(1+missing) + evolution
///     potential x 0.5^steps) replacing `HP x (energy+1)`. Prime suspect for the
///     pure-basics aggro regression (koraidon mirror ~41-42% under d/f/g).
///   * `clock_aware`  - the evolution-aware `turns_until_opponent_wins` scan, which
///     removes the 30.0 "can never win" sentinel and with it the -2,500 pt
///     anti-evolution cliff. Prime suspect for the venusaur/wailord anchor improvement.
///
/// `t<N>` = clock only, `v<N>` = value only, `d<N>` = both, `p<N>` = neither. The 2x2
/// tells us whether the anchor gain and the aggro loss ride on the same edit.
#[allow(clippy::too_many_arguments)]
pub fn parametric_value_function_ex5(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    value_aware: bool,
    clock_aware: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    parametric_value_function_ex6(
        state,
        myself,
        params,
        public_eval,
        value_aware,
        clock_aware,
        effect_aware,
        reserve_aware,
        EvalFeatures::OFF,
    )
}

/// [`parametric_value_function_ex5`] with the switches added after `kp` ([`EvalFeatures`]). With
/// [`EvalFeatures::OFF`] it is ex5 exactly: the clock takes its old path and no bench term is added.
#[allow(clippy::too_many_arguments)]
fn parametric_value_function_ex6(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    value_aware: bool,
    clock_aware: bool,
    effect_aware: bool,
    reserve_aware: bool,
    features: EvalFeatures,
) -> f64 {
    // A completed game has outcome utility only. Extra HP, cards, or points cannot
    // improve a win (or salvage a loss). Keep the historical private evaluator intact.
    if public_eval {
        if let Some(outcome) = state.winner {
            return match outcome {
                GameOutcome::Win(winner) if winner == myself => params.is_winner,
                GameOutcome::Win(_) => -params.is_winner,
                GameOutcome::Tie => 0.0,
            };
        }
    }
    if state.setup_opponent_hidden {
        // Own development terms only: a concealed opposing board must not become
        // a fictitious no-threat/no-Pokemon position in the battle evaluator.
        // Disable effect-based damage estimates here because some inspect targets.
        let pokemon_value = if value_aware {
            calculate_pokemon_value_damage_aware(state, myself, 1.0, false, false, false)
        } else {
            calculate_pokemon_value(state, myself, 1.0)
        };
        let (online, distance) = calculate_online_metrics(state, myself, 1.0);
        return pokemon_value * params.pokemon_value
            + state.hands[myself].len() as f64 * params.hand_size
            - state.decks[myself].cards.len() as f64 * params.deck_size
            - get_active_retreat_cost(state, myself, public_eval) as f64 * params.active_retreat_cost
            + calculate_active_pokemon_online_score(
                state,
                myself,
                false,
                false,
                false,
                features.projected_readiness.then_some(Horizon::ThroughNextTurn),
            ) * params.active_pokemon_online_score
            + calculate_active_safety(state, myself) * params.active_safety
            + online * params.online_pokemon_count
            + distance * params.energy_distance_to_online;
    }
    let opponent = (myself + 1) % 2;
    let (my, opp) = (
        extract_features(
            state,
            myself,
            1.0,
            false,
            value_aware,
            clock_aware,
            effect_aware,
            reserve_aware,
            public_eval,
            features.next_attack_reduction,
            features.defender_modifiers,
            features.projected_readiness.then_some(Horizon::ThroughNextTurn),
            features.projected_readiness.then_some(Horizon::NextAttack),
        ),
        extract_features(
            state,
            opponent,
            1.0,
            public_eval,
            value_aware,
            clock_aware,
            effect_aware,
            reserve_aware,
            public_eval,
            features.next_attack_reduction,
            features.defender_modifiers,
            features.projected_readiness.then_some(Horizon::NextAttack),
            features.projected_readiness.then_some(Horizon::ThroughNextTurn),
        ),
    );
    let score = (my.points - opp.points) * params.points
        + (my.pokemon_value - opp.pokemon_value) * params.pokemon_value
        + (my.hand_size - opp.hand_size) * params.hand_size
        + (opp.deck_size - my.deck_size) * params.deck_size
        + (-my.active_retreat_cost) * params.active_retreat_cost
        + (my.active_pokemon_online_score - opp.active_pokemon_online_score)
            * params.active_pokemon_online_score
        + (my.active_safety - opp.active_safety) * params.active_safety
        + (my.active_has_tool - opp.active_has_tool) * params.active_has_tool
        + (my.is_winner - opp.is_winner) * params.is_winner
        + (my.turns_until_opponent_wins - opp.turns_until_opponent_wins)
            * params.turns_until_opponent_wins
        + (my.online_pokemon_count - opp.online_pokemon_count) * params.online_pokemon_count
        + (my.energy_distance_to_online - opp.energy_distance_to_online)
            * params.energy_distance_to_online
        + opp.discard_size * params.opponent_discard_size;
    trace!("parametric_value_function: {score} (params: {params:?}, my: {my:?}, opp: {opp:?})");
    // kq: the best benched attacker's readiness, on both sides as for the Active (the opponent's priced from
    // the board only). Every older tier has weight 0 and skips it, so its score is untouched.
    if features.bench_attacker_weight != 0.0 {
        let my_bench =
            best_benched_attacker_online_score(state, myself, false, effect_aware, reserve_aware);
        let opp_bench =
            best_benched_attacker_online_score(state, opponent, public_eval, effect_aware, reserve_aware);
        return score + (my_bench - opp_bench) * features.bench_attacker_weight;
    }
    score
}

/// Features extracted from a player's game state
#[derive(Debug)]
struct Features {
    points: f64,
    pokemon_value: f64,
    hand_size: f64,
    deck_size: f64,
    active_retreat_cost: f64,
    online_pokemon_count: f64,
    energy_distance_to_online: f64,
    active_pokemon_online_score: f64,
    active_safety: f64,
    active_has_tool: f64,
    is_winner: f64,
    turns_until_opponent_wins: f64,
    discard_size: f64,
}

/// Extract features for a single player.
///
/// `public_only` restricts the extraction to information an opposing player is entitled to
/// see. Today that affects exactly one feature — `active_pokemon_online_score` — because it
/// is the only one that reads deck or hand CONTENTS; `hand_size` and `deck_size` are counts
/// and are public. (§40)
#[allow(clippy::too_many_arguments)]
fn extract_features(
    state: &State,
    player: usize,
    active_factor: f64,
    public_only: bool,
    value_aware: bool,
    clock_aware: bool,
    effect_aware: bool,
    reserve_aware: bool,
    public_evaluation: bool,
    next_attack_reduction: bool,
    defender_modifiers: bool,
    own_projection: Option<Horizon>,
    threat_projection: Option<Horizon>,
) -> Features {
    let points = state.points[player] as f64;
    let pokemon_value = if value_aware {
        calculate_pokemon_value_damage_aware(
            state,
            player,
            active_factor,
            public_only,
            effect_aware,
            reserve_aware,
        )
    } else {
        calculate_pokemon_value(state, player, active_factor)
    };
    let hand_size = state.hands[player].len() as f64;
    let deck_size = state.decks[player].cards.len() as f64;
    let active_retreat_cost = get_active_retreat_cost(state, player, public_evaluation) as f64;
    let (online_pokemon_count, energy_distance_to_online) =
        calculate_online_metrics(state, player, active_factor);
    let active_pokemon_online_score = calculate_active_pokemon_online_score(
        state,
        player,
        public_only,
        effect_aware,
        reserve_aware,
        own_projection,
    );
    let active_safety = calculate_active_safety(state, player);
    let active_has_tool = get_active_has_tool(state, player);
    let is_winner = check_is_winner(state, player);
    // §115: in the d path the threat scan is evolution-aware. `public_only` doubles as the
    // zone-read permission: it is true exactly when `player` is the OPPONENT of the
    // evaluating player, i.e. when the side being SCANNED for threats ((player+1)%2) is the
    // evaluating player themselves — whose deck and hand they may legitimately see.
    let turns_until_opponent_wins = if clock_aware {
        calculate_turns_until_opponent_wins_damage_aware(
            state,
            player,
            public_only,
            effect_aware,
            reserve_aware,
            public_evaluation,
            next_attack_reduction,
            defender_modifiers,
            threat_projection,
        )
    } else {
        calculate_turns_until_opponent_wins(state, player, public_evaluation)
    };
    let discard_size = state.discard_piles[player].len() as f64;

    Features {
        points,
        pokemon_value,
        hand_size,
        deck_size,
        active_retreat_cost,
        online_pokemon_count,
        energy_distance_to_online,
        active_pokemon_online_score,
        active_safety,
        active_has_tool,
        is_winner,
        turns_until_opponent_wins,
        discard_size,
    }
}

fn get_active_retreat_cost(state: &State, player: usize, public_evaluation: bool) -> usize {
    // Effective-cost hooks may scan opposing abilities. During concealed setup,
    // price our own board without exposing the opponent's unrevealed choices.
    let setup_view;
    let state = if public_evaluation && state.setup_opponent_hidden {
        let mut view = state.clone();
        view.in_play_pokemon[(player + 1) % 2] = Default::default();
        setup_view = view;
        &setup_view
    } else {
        state
    };
    state
        .maybe_get_active(player)
        .map(|card| {
            if public_evaluation {
                // Use the holder's side and persistent board modifiers while excluding
                // current-turn discounts that have no value unless a retreat follows.
                crate::hooks::get_board_retreat_cost_for_player(state, player, card).len()
            } else {
                card.card.get_retreat_cost().map(|rc| rc.len()).unwrap_or(5)
            }
        })
        .unwrap_or(0)
}

/// Check if active pokemon has a tool attached
fn get_active_has_tool(state: &State, player: usize) -> f64 {
    state
        .maybe_get_active(player)
        .map(|card| if card.has_tool_attached() { 1.0 } else { 0.0 })
        .unwrap_or(0.0)
}

/// Check if the player has won the game
fn check_is_winner(state: &State, player: usize) -> f64 {
    match state.winner {
        Some(GameOutcome::Win(winner)) if winner == player => 1.0,
        _ => 0.0,
    }
}

/// Calculate expected turns until opponent wins
/// Uses opponent's active damage and simulates KOs until opponent reaches 3 points
fn calculate_turns_until_opponent_wins(
    state: &State, player: usize, consume_bench: bool,
) -> f64 {
    let opponent = (player + 1) % 2;

    // Find the closest pokemon to being able to deal damage (by energy requirements)
    let best_threat = state
        .enumerate_in_play_pokemon(opponent)
        .filter_map(|(_, pokemon)| {
            let best_attack = pokemon
                .card
                .get_attacks()
                .iter()
                .filter(|atk| atk.fixed_damage > 0) // Only consider attacks that deal damage
                .map(|atk| {
                    let missing = energy_missing(pokemon, &atk.energy_required, state, opponent);
                    (atk.fixed_damage, missing.len())
                })
                .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage)); // Prioritize by missing energy, then by damage

            best_attack
        })
        .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage)); // Find pokemon with least missing energy
    let (max_damage, missing_energy) = match best_threat {
        Some((damage, missing)) => (damage as f64, missing),
        None => return 30.0, // No pokemon can deal damage
    };

    let mut total_turns = 0.0;
    let mut opp_points = state.points[opponent];

    // If the best threat still can't attack (missing energy), factor that into the calculation
    total_turns += missing_energy as f64;

    // Calculate turns to KO my active pokemon
    if let Some(my_active) = state.maybe_get_active(player) {
        let turns_to_ko = (my_active.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += my_active.card.get_knockout_points();
    }

    // Simulate KOing bench pokemon until opponent has 3+ points
    // Public estimates consume each victim once; running out of Pokemon also ends the game.
    // Keep the historical private arithmetic when consume_bench is false.
    let mut counted_slots = [false; 4];
    while opp_points < 3 {
        // Find the safest bench pokemon (highest hp / ko_points)
        let safest_bench = state
            .enumerate_bench_pokemon(player)
            .filter(|(slot, _)| !consume_bench || !counted_slots[*slot])
            .max_by_key(|(_, card)| {
                // if missing 1 point, just do by HP. if missing more than 1 point,
                // do by point yield hp / ko_points
                if opp_points == 2 {
                    card.get_remaining_hp()
                } else {
                    let ko_points = card.card.get_knockout_points().max(1) as u32;
                    card.get_remaining_hp() * 1000 / ko_points
                }
            });

        let Some((slot, safest_pokemon)) = safest_bench else {
            break; // No more bench pokemon
        };

        if consume_bench {
            counted_slots[slot] = true;
        }
        let turns_to_ko = (safest_pokemon.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += safest_pokemon.card.get_knockout_points();
    }

    total_turns
}

/// §115 — [`calculate_turns_until_opponent_wins`] with the SECOND instance of the §113
/// defect fixed. The original scans only attacks currently on the board and returns a
/// "can never win" sentinel of 30.0 when none deal damage — so evolving into a utility
/// Stage-1 (Ivysaur) zeroes the side's visible threat and the feature swings by thousands
/// of points at coefficient 100. That cliff, not the 10-point Pokémon-term gap, is the
/// bulk of why the pilot refused to evolve.
///
/// Here, when `read_scanned_zones` permits (see the call site: the scanned side is the
/// evaluating player, whose own deck + hand are legitimately visible), each in-play
/// Pokémon also threatens the attacks of its best evolution available in those zones,
/// priced against the energy already on the slot, with each evolution step still to take
/// counted as one more turn — the same unit as missing energy. When the scanned side is
/// the true opponent, the scan stays board-only, preserving §40's leak closure.
///
/// kpr (`projected_readiness`, the threat owner's [`Horizon`]): the smaller of this clock with the threatening Active
/// projected ([`at_next_attack`]) and without. Projecting only the Active can otherwise make the win slower: a weak
/// Active one attach short would displace a stronger benched attacker as the threat.
#[allow(clippy::too_many_arguments)]
fn calculate_turns_until_opponent_wins_damage_aware(
    state: &State,
    player: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    next_attack_reduction: bool,
    defender_modifiers: bool,
    projected_readiness: Option<Horizon>,
) -> f64 {
    let clock = |projected| {
        turns_until_opponent_wins_scan(
            state,
            player,
            read_scanned_zones,
            effect_aware,
            reserve_aware,
            consume_bench,
            next_attack_reduction,
            defender_modifiers,
            projected,
        )
    };
    match projected_readiness {
        Some(horizon) => clock(None).min(clock(Some(horizon))),
        None => clock(None),
    }
}

/// The body of [`calculate_turns_until_opponent_wins_damage_aware`], with the threatening Active projected over
/// `projected_readiness`'s horizon when it is set.
#[allow(clippy::too_many_arguments)]
fn turns_until_opponent_wins_scan(
    state: &State,
    player: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    next_attack_reduction: bool,
    defender_modifiers: bool,
    projected_readiness: Option<Horizon>,
) -> f64 {
    let opponent = (player + 1) % 2;

    // §116: with `effect_aware`, an attack threatens its ESTIMATED damage; otherwise its
    // `fixed_damage`, exactly as §115 shipped. §117's `reserve_aware` widens the
    // estimator's class coverage.
    let attack_damage = |atk: &Attack, slot: &PlayedCard| -> u32 {
        if effect_aware {
            estimated_attack_damage_ex(atk, slot, state, opponent, reserve_aware).round() as u32
        } else {
            atk.fixed_damage
        }
    };

    // Every attack the owner could threaten with, in scan order. The threat is the first with the fewest missing
    // Energy, then the most damage (the same pick as the historical per-slot scan, flattened).
    let mut candidates: Vec<ThreatCandidate> = Vec::new();
    for (slot, pokemon) in state.enumerate_in_play_pokemon(opponent) {
        // kpr: the Active's missing Energy and damage are counted as it will stand at its next attack
        // ([`at_next_attack`]).
        let projected;
        let charged: &PlayedCard = match projected_readiness {
            Some(horizon) if slot == 0 => {
                projected = at_next_attack(state, opponent, pokemon, horizon);
                &projected
            }
            _ => pokemon,
        };
        for (attack, atk) in pokemon.card.get_attacks().iter().enumerate() {
            let damage = attack_damage(atk, charged);
            if damage == 0 {
                continue;
            }
            let missing = energy_missing(charged, &atk.energy_required, state, opponent).len();
            candidates.push(ThreatCandidate { slot, damage, missing, form: None, attack });
        }
        if read_scanned_zones {
            if let Card::Pokemon(current) = &pokemon.card {
                for (form, target) in evolution_targets(state, opponent, pokemon).into_iter().enumerate() {
                    let Card::Pokemon(t) = &target else { continue };
                    let steps = t.stage.saturating_sub(current.stage) as usize;
                    if steps == 0 {
                        continue;
                    }
                    for (attack, atk) in target.get_attacks().iter().enumerate() {
                        let damage = attack_damage(atk, charged);
                        if damage > 0 {
                            let missing =
                                energy_missing(charged, &atk.energy_required, state, opponent).len() + steps;
                            candidates.push(ThreatCandidate { slot, damage, missing, form: Some(form), attack });
                        }
                    }
                }
            }
        }
    }
    let Some(threat) = candidates.iter().min_by_key(|c| (c.missing, u32::MAX - c.damage)) else {
        return 30.0; // No pokemon can deal damage, now or via any available evolution
    };
    let (max_damage, missing_energy, _threat_slot) = (threat.damage as f64, threat.missing, threat.slot);

    let mut total_turns = 0.0;
    let mut opp_points = state.points[opponent];

    total_turns += missing_energy as f64;

    // B2b diagnostic, only in builds with the `status-clock` feature: a threat in the Active Spot that is
    // Asleep misses its next attack half the time (the checkup coin), and one that is Paralyzed misses it.
    #[cfg(feature = "status-clock")]
    if _threat_slot == 0 {
        if let Some(threat) = state.maybe_get_active(opponent) {
            if threat.has_status(StatusCondition::Paralyzed) {
                total_turns += 1.0;
            } else if threat.has_status(StatusCondition::Asleep) {
                total_turns += 0.5;
            }
        }
    }

    // kd counts the victims its own way (kd_turns_to_win), capped at 30: 30 means "never", so no finite clock may
    // pass it. kq's first-attack pricing isn't combined with it.
    if defender_modifiers {
        return match kd_turns_to_win(state, player, opponent, &candidates, threat, consume_bench) {
            Some(turns) => (total_turns + turns).min(30.0),
            None => 30.0,
        };
    }

    // kq: when the threat is the Active and carries effects that cut or cancel its next attack, the first
    // knockout's first attack turn is priced through them (or through the owner's escape into a ready benched
    // attacker, whichever is faster). Only that turn: later turns keep the clock's pace.
    let mut first_turn_damage = if next_attack_reduction && _threat_slot == 0 {
        first_attack_turn(state, opponent, max_damage, &attack_damage)
    } else {
        None
    };

    if let Some(my_active) = state.maybe_get_active(player) {
        let turns_to_ko = match first_turn_damage.take() {
            None => (my_active.get_remaining_hp() as f64 / max_damage).ceil(),
            Some(first) => first.ko_turns(my_active.get_remaining_hp() as f64, max_damage),
        };
        total_turns += turns_to_ko;
        opp_points += my_active.card.get_knockout_points();
    }

    // Public estimates consume each victim once; running out of Pokemon also ends the game.
    // Keep the historical private arithmetic when consume_bench is false.
    let mut counted_slots = [false; 4];
    while opp_points < 3 {
        let safest_bench = state
            .enumerate_bench_pokemon(player)
            .filter(|(slot, _)| !consume_bench || !counted_slots[*slot])
            .max_by_key(|(_, card)| {
                if opp_points == 2 {
                    card.get_remaining_hp()
                } else {
                    let ko_points = card.card.get_knockout_points().max(1) as u32;
                    card.get_remaining_hp() * 1000 / ko_points
                }
            });

        let Some((slot, safest_pokemon)) = safest_bench else {
            break;
        };

        if consume_bench {
            counted_slots[slot] = true;
        }
        let turns_to_ko = match first_turn_damage.take() {
            None => (safest_pokemon.get_remaining_hp() as f64 / max_damage).ceil(),
            Some(first) => first.ko_turns(safest_pokemon.get_remaining_hp() as f64, max_damage),
        };
        total_turns += turns_to_ko;
        opp_points += safest_pokemon.card.get_knockout_points();
    }

    total_turns
}

/// One attack the damage-aware clock's scan found for the threatening side.
#[derive(Debug, Clone, Copy)]
struct ThreatCandidate {
    /// The in-play slot of the Pokemon that has it.
    slot: usize,
    /// The clock's damage estimate for it, before the victim's modifiers.
    damage: u32,
    /// Missing Energy, plus one per evolution step for an evolved form.
    missing: usize,
    /// `None` for the Pokemon as it is, or the index of the evolution target in `evolution_targets`. Forms are only
    /// scanned for the evaluating player's own threats, so no hidden zone of the opponent is read.
    form: Option<usize>,
    /// The attack's index on that form.
    attack: usize,
}

/// kd: the turns after the threat's own readiness until `owner` has knocked out enough of `victim_owner`'s Pokemon
/// to win, or `None` ("never") when it can't. kd runs only in public evaluation, where each victim counts once.
/// - Each hit goes through the victim's Weakness and persistent reductions (`persistent_defender_damage`), for the
///   attacking form and the attack it uses (its own text counts), plus the attack's bonus for who the defender is
///   (`defender_identity_bonus`) when it hits the victim as the Active.
/// - Reach: an attack that can hit the Active hits each victim as the Active (the defender promotes it); one that
///   can only damage the Bench can't touch the Active, and hits a benched victim where it is.
/// - A victim the global threat can't damage is priced with the owner's best candidate that can: fewest missing
///   Energy, then the most damage to that victim. It first waits for that candidate's missing Energy beyond the
///   threat's, counted once per Pokemon (Energy stays attached).
/// - After the Active, the defender promotes its benched victims in the order that makes the count longest (every
///   order of up to three is tried). One that nothing can damage would be promoted, so the count is "never".
/// - If nothing can damage the Active, it is never knocked out and nothing is promoted: the owner can only snipe
///   benched victims, in the order that wins soonest, and it's "never" if that can't reach 3 points.
fn kd_turns_to_win(
    state: &State,
    victim_owner: usize,
    owner: usize,
    candidates: &[ThreatCandidate],
    threat: &ThreatCandidate,
    consume_bench: bool,
) -> Option<f64> {
    debug_assert!(consume_bench, "kd runs in public evaluation, where each victim counts once");
    let mut pricer = KdPricer {
        state,
        owner,
        victim_owner,
        candidates,
        threat,
        threat_attacker: kd_attacker(state, owner, threat, &mut None),
        attackers: None,
    };
    let bench: Vec<&PlayedCard> = state.enumerate_bench_pokemon(victim_owner).map(|(_, victim)| victim).collect();
    let mut points = state.points[owner];
    let mut paid = [0usize; 4];
    let mut turns = 0.0;
    if let Some(active) = state.maybe_get_active(victim_owner) {
        let Some(price) = pricer.price(active, VictimPlace::Active) else {
            // Nothing reaches the Active: only snipes can score. The owner picks the order that wins soonest.
            let snipes: Vec<(KdPrice, u8)> = bench
                .iter()
                .filter_map(|victim| {
                    pricer.price(victim, VictimPlace::BenchedOnly).map(|price| (price, victim.card.get_knockout_points()))
                })
                .collect();
            return orders(snipes.len())
                .into_iter()
                .filter_map(|order| {
                    let (mut paid, mut turns, mut points) = ([0usize; 4], 0.0, points);
                    for index in order {
                        if points >= 3 {
                            break;
                        }
                        turns += snipes[index].0.pay(&mut paid);
                        points += snipes[index].1;
                    }
                    (points >= 3).then_some(turns)
                })
                .reduce(f64::min);
        };
        turns += price.pay(&mut paid);
        points += active.card.get_knockout_points();
    }
    if points >= 3 {
        return Some(turns);
    }
    let promoted: Vec<(KdPrice, u8)> = bench
        .iter()
        .map(|victim| {
            pricer
                .price(victim, VictimPlace::BenchedPromoted)
                .map(|price| (price, victim.card.get_knockout_points()))
        })
        .collect::<Option<_>>()?;
    let longest = orders(promoted.len())
        .into_iter()
        .map(|order| {
            let (mut paid, mut turns, mut points) = (paid, 0.0, points);
            for index in order {
                if points >= 3 {
                    break;
                }
                turns += promoted[index].0.pay(&mut paid);
                points += promoted[index].1;
            }
            turns
        })
        .fold(0.0, f64::max);
    Some(turns + longest)
}

/// Where kd's clock takes a victim to be when it is hit.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum VictimPlace {
    /// The Active.
    Active,
    /// Benched, and promoted when its turn comes: an attack that can hit the Active hits it as the Active, one that
    /// can only damage the Bench hits it on the Bench.
    BenchedPromoted,
    /// Benched, and never promoted (the Active is never knocked out): only attacks that damage the Bench reach it.
    BenchedOnly,
}

/// kd: the price of knocking one victim out with one candidate.
#[derive(Debug, Clone, Copy)]
struct KdPrice {
    /// Turns of attacks.
    ko_turns: f64,
    /// The attacking Pokemon's slot.
    slot: usize,
    /// Its missing Energy beyond the threat's.
    extra: usize,
}

impl KdPrice {
    /// Turns this knockout adds: the Energy still to attach to its attacker (Energy already counted for that Pokemon
    /// stays attached), then the attacks.
    fn pay(&self, paid: &mut [usize; 4]) -> f64 {
        let wait = self.extra.saturating_sub(paid[self.slot]);
        paid[self.slot] = paid[self.slot].max(self.extra);
        wait as f64 + self.ko_turns
    }
}

/// Every order of `0..n` (n is at most 3, the Bench's size).
fn orders(n: usize) -> Vec<Vec<usize>> {
    if n == 0 {
        return vec![vec![]];
    }
    let mut all = Vec::new();
    for first in 0..n {
        for rest in orders(n - 1) {
            let mut order = vec![first];
            order.extend(rest.into_iter().map(|index| if index >= first { index + 1 } else { index }));
            all.push(order);
        }
    }
    all
}

/// kd: the attacking form of candidate `c` and the attack it uses. `targets` caches `evolution_targets` for its slot.
fn kd_attacker(
    state: &State,
    owner: usize,
    c: &ThreatCandidate,
    targets: &mut Option<Vec<Card>>,
) -> (PlayedCard, Attack) {
    let pokemon = state.in_play_pokemon[owner][c.slot]
        .as_ref()
        .expect("the candidate was found in play");
    let form = match c.form {
        None => pokemon.clone(),
        Some(form) => {
            let targets = targets.get_or_insert_with(|| evolution_targets(state, owner, pokemon));
            to_playable_card(&targets[form], false)
        }
    };
    let attack = form.card.get_attacks()[c.attack].clone();
    (form, attack)
}

/// kd: the part of the clock's damage estimate that lands on the opponent's Bench, not the Active: the extra of
/// `AlsoBenchDamage`, `AlsoChoiceBenchDamage` and `AlsoChoiceBenchDamageFiltered` (when it has a target), which
/// `estimated_attack_damage_ex` adds to the attack's damage (kd runs it with `spread_aware` off). A hit on the Active
/// is priced without it.
fn estimated_bench_spill(attack: &Attack, state: &State, owner: usize) -> u32 {
    let Some(mechanic) = attack.effect.as_deref().and_then(|effect| EFFECT_MECHANIC_MAP.get(effect)) else {
        return 0;
    };
    match mechanic {
        Mechanic::AlsoBenchDamage { opponent: true, damage, .. }
        | Mechanic::AlsoChoiceBenchDamage { opponent: true, damage } => *damage,
        Mechanic::AlsoChoiceBenchDamageFiltered { opponent: true, damage, filter } => {
            let has_target = state
                .enumerate_bench_pokemon((owner + 1) % 2)
                .any(|(_, pokemon)| match filter {
                    BenchDamageFilter::Any => true,
                    BenchDamageFilter::Damaged => pokemon.is_damaged(),
                });
            if has_target {
                *damage
            } else {
                0
            }
        }
        _ => 0,
    }
}

/// kd: the attack's bonus that depends only on who the defending Active is (a Pokemon ex, its type, its stage, its
/// name, whether it has an Ability), for `victim` as that Active, as apply_attack_action prices it. The clock's
/// estimate leaves these at the printed damage.
fn defender_identity_bonus(state: &State, attack: &Attack, victim: &PlayedCard) -> u32 {
    let Some(mechanic) = attack.effect.as_deref().and_then(|effect| EFFECT_MECHANIC_MAP.get(effect)) else {
        return 0;
    };
    match mechanic {
        Mechanic::ExtraDamageIfEx { extra_damage } if victim.card.is_ex() => *extra_damage,
        Mechanic::ExtraDamageIfDefenderType { energy_types, extra_damage }
            if victim.card.get_type().is_some_and(|energy_type| energy_types.contains(&energy_type)) =>
        {
            *extra_damage
        }
        Mechanic::ExtraDamageIfDefenderStage { evolution, extra_damage }
            if (get_stage(victim) > BASIC_STAGE) == *evolution =>
        {
            *extra_damage
        }
        Mechanic::ExtraDamageIfDefenderNamed { name, extra_damage } if victim.get_name() == *name => *extra_damage,
        Mechanic::ExtraDamageIfDefenderNameContains { substring, extra_damage }
            if victim.get_name().contains(substring.as_str()) =>
        {
            *extra_damage
        }
        Mechanic::ExtraDamageIfOpponentActiveHasAbility { extra_damage } if has_any_in_play_ability(state, victim) => {
            *extra_damage
        }
        _ => 0,
    }
}

/// kd's pricing of victims for one clock call, building every candidate's attacker at most once.
struct KdPricer<'a> {
    state: &'a State,
    owner: usize,
    victim_owner: usize,
    candidates: &'a [ThreatCandidate],
    threat: &'a ThreatCandidate,
    threat_attacker: (PlayedCard, Attack),
    /// Every candidate's attacker, in `candidates` order, built on the first fallback.
    attackers: Option<Vec<(PlayedCard, Attack)>>,
}

impl KdPricer<'_> {
    /// (first, later): the expected damage of `c`'s first hit on `victim` at `place`, and of every hit after it. (0, 0)
    /// when the attack can't reach it there.
    fn hits(&self, c: &ThreatCandidate, (form, attack): &(PlayedCard, Attack), victim: &PlayedCard, place: VictimPlace) -> (f64, f64) {
        let (hit, base) = match (only_damages_the_bench(attack), place) {
            (true, VictimPlace::Active) | (false, VictimPlace::BenchedOnly) => return (0.0, 0.0),
            (true, _) => (DefenderHit::Benched, c.damage),
            (false, _) => (
                DefenderHit::Active,
                c.damage.saturating_sub(estimated_bench_spill(attack, self.state, self.owner))
                    + defender_identity_bonus(self.state, attack, victim),
            ),
        };
        let context = DamageModifierContext {
            attack_name: Some(&attack.title),
            attack_effect: attack.effect.as_deref(),
        };
        persistent_defender_damage(self.state, self.owner, form, self.victim_owner, victim, base, context, hit)
    }

    /// The price of knocking `victim` out at `place`: by the threat if it can damage it, else by the owner's best
    /// candidate that can; `None` if none can.
    fn price(&mut self, victim: &PlayedCard, place: VictimPlace) -> Option<KdPrice> {
        let hp = victim.get_remaining_hp() as f64;
        if hp == 0.0 {
            return Some(KdPrice { ko_turns: 0.0, slot: self.threat.slot, extra: 0 });
        }
        let (first, later) = self.hits(self.threat, &self.threat_attacker, victim, place);
        if later > 0.0 {
            return Some(KdPrice {
                ko_turns: ko_turns_after_first_attack(hp, first, later),
                slot: self.threat.slot,
                extra: 0,
            });
        }
        if self.attackers.is_none() {
            let mut targets: [Option<Vec<Card>>; 4] = Default::default();
            let built = self
                .candidates
                .iter()
                .map(|c| kd_attacker(self.state, self.owner, c, &mut targets[c.slot]))
                .collect();
            self.attackers = Some(built);
        }
        let attackers = self.attackers.as_ref().expect("built above");
        let (fallback, first, later) = self
            .candidates
            .iter()
            .zip(attackers)
            .filter_map(|(c, attacker)| {
                let (first, later) = self.hits(c, attacker, victim, place);
                (later > 0.0).then_some((c, first, later))
            })
            .min_by(|a, b| a.0.missing.cmp(&b.0.missing).then(b.2.total_cmp(&a.2)))?;
        Some(KdPrice {
            ko_turns: ko_turns_after_first_attack(hp, first, later),
            slot: fallback.slot,
            extra: fallback.missing - self.threat.missing,
        })
    }
}

/// kq: the first attack turn of the first knockout, when the threat (`owner`'s Active) carries effects that cut
/// or cancel its next attack. The owner takes whichever option is faster: attack through the effects, or retreat
/// (which clears them) into its best ready benched attacker. Damage never exceeds the clock's `max_damage`, so kq
/// can only make the opponent slower than `k` does, never faster.
#[derive(Debug, Clone, PartialEq)]
struct FirstAttackTurn {
    /// Attacking through the effects: (probability, damage) outcomes.
    through: Vec<(f64, f64)>,
    /// The best damage a benched Pokemon of the owner can do that turn instead.
    escape: f64,
}

impl FirstAttackTurn {
    /// Expected turns to knock out `hp` when this is the first attack turn and every later one does `max_damage`.
    fn ko_turns(&self, hp: f64, max_damage: f64) -> f64 {
        let through: f64 = self
            .through
            .iter()
            .map(|(p, damage)| p * ko_turns_after_first_attack(hp, *damage, max_damage))
            .sum();
        through.min(ko_turns_after_first_attack(hp, self.escape, max_damage))
    }
}

/// kq and kd: turns to knock out `hp` when the first attack does `first` and every later one `max_damage`.
fn ko_turns_after_first_attack(hp: f64, first: f64, max_damage: f64) -> f64 {
    if first >= hp {
        1.0
    } else {
        1.0 + ((hp - first) / max_damage).ceil()
    }
}

/// The highest evolutions of `pokemon` that `owner` has in deck or hand, sorted by card id. The clock's threat scan
/// and kd's threat form both read it, so a form index means the same card in both. The sort makes the form that
/// wins a tie independent of the order of the (shuffled) deck; tied forms have the same damage and missing
/// Energy, so the clock of every tier without kd is unchanged by it.
fn evolution_targets(state: &State, owner: usize, pokemon: &PlayedCard) -> Vec<Card> {
    let mut available: Vec<Card> = state.decks[owner].cards.to_vec();
    available.extend(state.hands[owner].iter().cloned());
    let mut targets = get_highest_evolutions(&pokemon.card, &available);
    targets.sort_by_cached_key(|card| card.get_id());
    targets
}

/// kq: [`FirstAttackTurn`] for `owner`, or `None` when its Active carries no effect that reaches its first attack
/// turn. Keyed on the effect types the engine enforces, never on card names:
/// - `CannotAttack` (move_generation/attacks.rs): no attack that turn;
/// - `CannotUseAttack(title)` (the same): that attack isn't offered, so its best other attack;
/// - `ReducedAttackDamage { amount }` (hooks/core.rs `modify_damage`): the amounts summed, floored at 0;
/// - `CoinFlipToBlockAttack` (apply_attack_action.rs): the attack happens or not on a coin, 50/50.
/// Timing follows Pocket: a Pokemon attaches one Energy a turn (from the Energy Zone, if this turn's is still
/// there) and may attack the same turn. The owner's next turn is this one if it is to move and hasn't attacked;
/// the Active's first attack turn is the one where its cheapest damaging attack is paid for, two global turns per
/// attach. An effect with `d` turns left is live through turn `t + d` (`PlayedCard::end_turn_maintenance`).
/// The escape is a retreat the Active can make on the owner's next turn (not blocked by a special condition,
/// `NoRetreat` or a retreat already made this turn, its Energy covering the cost) into a benched Pokemon whose
/// attack can hit the Active, paid for by then. Evolving, which also clears the effects, is not counted.
fn first_attack_turn(
    state: &State,
    owner: usize,
    max_damage: f64,
    attack_damage: &dyn Fn(&Attack, &PlayedCard) -> u32,
) -> Option<FirstAttackTurn> {
    let active = state.maybe_get_active(owner)?;
    let missing = |pokemon: &PlayedCard, attack: &Attack| {
        energy_missing(pokemon, &attack.energy_required, state, owner).len()
    };
    let attacks = active.card.get_attacks();
    let damaging: Vec<&Attack> = attacks.iter().filter(|atk| attack_damage(atk, active) > 0).collect();
    let fewest_missing = damaging.iter().map(|atk| missing(active, atk)).min()?;
    let t = state.turn_count as u32;
    let owner_to_move_now = state.current_player == owner
        && !state.end_turn_pending
        && state.attack_name_used_this_turn[owner].is_none();
    let next_turn = if owner_to_move_now {
        t
    } else if state.current_player != owner {
        t + 1
    } else {
        t + 2
    };
    // Energy attachable on the owner's next turn: this turn's, if it is still in the Energy Zone.
    let attach_next = if next_turn == t { state.energy_zone[owner].current.is_some() as usize } else { 1 };
    // The first attack turn, and how much Energy the Active can have had attached by then.
    let (first_attack, attachable) = match fewest_missing {
        0 => (next_turn, attach_next),
        m if attach_next == 1 => (next_turn + 2 * (m as u32 - 1), m),
        m => (next_turn + 2 * m as u32, m),
    };
    let (mut relevant, mut cannot_attack, mut coin_block, mut reduction) = (false, false, false, 0u32);
    let mut blocked: Vec<&str> = Vec::new();
    for (effect, turns_left) in active.get_effects() {
        if first_attack > t + *turns_left as u32 {
            continue;
        }
        match effect {
            CardEffect::CannotAttack => cannot_attack = true,
            CardEffect::CannotUseAttack(title) => blocked.push(title.as_str()),
            CardEffect::ReducedAttackDamage { amount } => reduction += *amount,
            CardEffect::CoinFlipToBlockAttack => coin_block = true,
            _ => continue,
        }
        relevant = true;
    }
    if !relevant {
        return None;
    }
    let through = if cannot_attack {
        vec![(1.0, 0.0)]
    } else {
        let best = damaging
            .iter()
            .filter(|atk| !blocked.contains(&atk.title.as_str()) && missing(active, atk) <= attachable)
            .map(|atk| attack_damage(atk, active) as f64)
            .fold(0.0, f64::max)
            .min(max_damage);
        let damage = (best - reduction as f64).max(0.0);
        if coin_block {
            vec![(0.5, damage), (0.5, 0.0)]
        } else {
            vec![(1.0, damage)]
        }
    };
    let can_retreat = !special_condition_blocks_attack_or_retreat(active)
        && !active.get_active_effects().contains(&CardEffect::NoRetreat)
        && !active.is_fossil()
        && !(next_turn == t && state.has_retreated);
    let retreat_cost = get_retreat_cost_for_player(state, owner, active).len();
    let escape = if !can_retreat {
        0.0
    } else {
        state
            .enumerate_bench_pokemon(owner)
            .flat_map(|(_, pokemon)| {
                pokemon
                    .card
                    .get_attacks()
                    .iter()
                    .filter(|atk| !only_damages_the_bench(atk))
                    .filter(|atk| {
                        // The turn's Energy goes either to the benched attacker or to the retreat.
                        let short = missing(pokemon, atk);
                        short <= attach_next && retreat_cost + short <= active.attached_energy.len() + attach_next
                    })
                    .map(|atk| attack_damage(atk, pokemon) as f64)
                    .collect::<Vec<_>>()
            })
            .fold(0.0, f64::max)
            .min(max_damage)
    };
    Some(FirstAttackTurn { through, escape })
}

/// Calculate online pokemon metrics: (count of online pokemon, total energy distance to online)
/// A pokemon is "online" if it can use at least one attack
/// Applies active_factor bonus to the active pokemon (position 0)
fn calculate_online_metrics(state: &State, player: usize, active_factor: f64) -> (f64, f64) {
    let (online_count, total_distance) = state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let min_distance = card
                .card
                .get_attacks()
                .iter()
                .map(|atk| {
                    let missing = energy_missing(card, &atk.energy_required, state, player);
                    missing.len()
                })
                .min()
                .unwrap_or(0);

            let position_factor = if pos == 0 { active_factor } else { 1.0 };

            if min_distance == 0 {
                (position_factor, 0.0) // Online pokemon with position bonus
            } else {
                (0.0, min_distance as f64 * position_factor) // Offline pokemon with weighted distance
            }
        })
        .fold((0.0, 0.0), |(count, dist), (c, d)| (count + c, dist + d));

    (online_count, total_distance)
}

/// Calculate total pokemon value (HP * Energy) for a player
fn calculate_pokemon_value(state: &State, player: usize, active_factor: f64) -> f64 {
    state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let relevant_energy = get_relevant_energy(state, player, card);
            let hp_energy_product = card.get_remaining_hp() as f64 * (relevant_energy + 1.0);
            if pos == 0 {
                hp_energy_product * active_factor
            } else {
                hp_energy_product
            }
        })
        .sum()
}

/// §115 — the `d` tier's Pokémon term. Scores each Pokémon in play as
///
/// ```text
/// remaining_HP + K_DAMAGE × best_damage_now + evolution_potential
/// ```
///
/// - `best_damage_now`: the best of the card's OWN attacks, each valued at
///   `fixed_damage / (1 + missing_energy)` against the slot's currently attached energy —
///   a ready 40 is worth 40, a 120 missing two energy is worth 40. This is the damage term
///   §113 showed was absent entirely, and because the anchor attack is chosen by DAMAGE it
///   also retires `get_relevant_energy`'s lexicographic-`.max()` quirk in this path.
/// - `evolution_potential`: the best evolution of this card available in the player's own
///   deck + hand, valued the same way (HP net of damage carried, plus its discounted best
///   damage against the energy already on the slot), then discounted by
///   `EVOLUTION_STEP_DISCOUNT^steps`. Each evolution step taken moves value out of the
///   discount and onto the board, so assembling a line is monotonically uphill —
///   Bulbasaur 180 < Ivysaur 240 < Mega Venusaur ex 280 on the §113 whiteboard example
///   that scored 210 > 200 under the old term. Reads the player's OWN hidden zones only;
///   under `public_only` (opponent eval) it contributes 0, preserving §40's leak closure.
fn calculate_pokemon_value_damage_aware(
    state: &State,
    player: usize,
    active_factor: f64,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    let board: f64 = state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let value = card.get_remaining_hp() as f64
                + K_DAMAGE
                    * best_attack_value_ex(card, &card.card, state, player, effect_aware, reserve_aware)
                + evolution_potential(state, player, card, public_only, effect_aware, reserve_aware);
            if pos == 0 {
                value * active_factor
            } else {
                value
            }
        })
        .sum();
    if reserve_aware {
        board + discard_energy_credit(state, player)
    } else {
        board
    }
}

/// §117 — the fuel reserve. Energy in the discard pile is worth something exactly when a
/// discard-recycler ability (Dragon's Blessing class) is in play to bring it back. Discard
/// piles and boards are public information, so this computes symmetrically for both sides
/// — no §40 leak. Constant and cap fixed in `s117_prereg.txt`.
fn discard_energy_credit(state: &State, player: usize) -> f64 {
    const K_DISCARD_ENERGY: f64 = 15.0;
    const DISCARD_ENERGY_CAP: usize = 4;
    let has_recycler = state.enumerate_in_play_pokemon(player).any(|(_, card)| {
        card.card
            .get_ability()
            .and_then(|a| ability_mechanic_from_effect(&a.effect).cloned())
            .is_some_and(|m| {
                matches!(
                    m,
                    AbilityMechanic::AttachEnergyFromDiscardToActiveTypedFromBench { .. }
                        | AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage { .. }
                )
            })
    });
    if !has_recycler {
        return 0.0;
    }
    K_DISCARD_ENERGY * state.discard_energies[player].len().min(DISCARD_ENERGY_CAP) as f64
}

/// §115 constants, fixed in `s115_prereg.txt` BEFORE the first d-tier game was run.
const K_DAMAGE: f64 = 1.0;
const EVOLUTION_STEP_DISCOUNT: f64 = 0.5;

/// §116 — what this attack would actually deal from this slot, given the state, for the
/// mechanic classes where that is cheap and deterministic (expected value for coin flips).
/// Falls back to `fixed_damage` for everything else. Mirrors the apply-side semantics in
/// `apply_attack_action.rs`; the covered classes are pre-registered in `s116_prereg.txt`
/// and pinned to hand-computed values in `tests/s116_estimated_damage_test.rs`.
///
/// Motivation (s116 census over pool9): `fixed_damage` misrepresents attacks across the
/// pool — Mega Burst prints 50 but deals 50 × Energy discarded, Brutal Bash prints 30 but
/// deals 30 + 30 × bench, Diving Icicles and Baneful Boom print 0. A value function that
/// reads only `fixed_damage` cannot see the point of banking Energy (measured: the 3rd
/// Energy on Mega Rayquaza ex is worth exactly 0.0 to both `p3` and `d3`), which is the
/// verified mechanism behind the Dragonair family's impatience.
fn estimated_attack_damage(attack: &Attack, slot: &PlayedCard, state: &State, player: usize) -> f64 {
    estimated_attack_damage_ex(attack, slot, state, player, false)
}

/// §117: `spread_aware` adds four more classes (gated so the §116 `f` tier stays
/// byte-compatible): random-spread damage (the Draco Meteor family — `fixed_damage: 0`
/// on the card), also-random-bench, per-self-energy random hits, and the
/// discard-per-heads EV.
fn estimated_attack_damage_ex(
    attack: &Attack,
    slot: &PlayedCard,
    state: &State,
    player: usize,
    spread_aware: bool,
) -> f64 {
    let fixed = attack.fixed_damage as f64;
    let Some(effect) = &attack.effect else {
        return fixed;
    };
    let Some(mechanic) = EFFECT_MECHANIC_MAP.get(effect.as_str()) else {
        return fixed;
    };
    if spread_aware {
        match mechanic {
            Mechanic::RandomSpreadDamage {
                times,
                damage_per_hit,
                ..
            } => return *times as f64 * *damage_per_hit as f64,
            Mechanic::AlsoRandomBenchDamage { damage } => return fixed + *damage as f64,
            Mechanic::RandomDamageToOpponentPokemonPerSelfEnergy {
                energy_type,
                damage_per_hit,
            } => {
                let count = slot
                    .attached_energy
                    .iter()
                    .filter(|e| *e == energy_type)
                    .count() as f64;
                return *damage_per_hit as f64 * count;
            }
            Mechanic::DiscardSelfEnergyPerHeadsExtraDamage {
                num_coins,
                damage_per_discarded_energy,
                ..
            } => return fixed + *damage_per_discarded_energy as f64 * *num_coins as f64 / 2.0,
            _ => {}
        }
    }
    let opponent = (player + 1) % 2;
    let count_attached = |types: &dyn Fn(&EnergyType) -> bool| {
        slot.attached_energy.iter().filter(|e| types(e)).count() as f64
    };
    match mechanic {
        // The attack's printed damage is the PER-ENERGY amount, not a base (see mechanic doc).
        Mechanic::SelfDiscardAllTypesEnergyDamagePerDiscarded {
            energy_types,
            damage_per_energy,
        } => *damage_per_energy as f64 * count_attached(&|e| energy_types.contains(e)),
        Mechanic::BenchCountDamage {
            include_fixed_damage,
            damage_per,
            energy_type,
            names,
            bench_side,
        } => {
            let players: Vec<usize> = match bench_side {
                BenchSide::YourBench => vec![player],
                BenchSide::OpponentBench => vec![opponent],
                BenchSide::BothBenches => vec![player, opponent],
            };
            let count = players
                .iter()
                .flat_map(|&pl| state.enumerate_bench_pokemon(pl))
                .filter(|(_, pokemon)| {
                    energy_type.is_none_or(|energy| state.pokemon_is_type(pokemon, energy))
                        && names
                            .as_ref()
                            .is_none_or(|ns| ns.contains(&pokemon.get_name()))
                })
                .count() as f64;
            (if *include_fixed_damage { fixed } else { 0.0 }) + *damage_per as f64 * count
        }
        Mechanic::EvolutionBenchCountDamage {
            include_fixed_damage,
            damage_per,
        } => {
            let count = state
                .enumerate_bench_pokemon(player)
                .filter(|(_, pokemon)| match &pokemon.card {
                    Card::Pokemon(p) => p.stage > 0,
                    _ => false,
                })
                .count() as f64;
            (if *include_fixed_damage { fixed } else { 0.0 }) + *damage_per as f64 * count
        }
        Mechanic::ExtraDamagePerEnergy {
            include_fixed_damage,
            opponent: on_opponent,
            damage_per_energy,
        } => {
            let count = if *on_opponent {
                state
                    .maybe_get_active(opponent)
                    .map(|c| c.attached_energy.len())
                    .unwrap_or(0) as f64
            } else {
                slot.attached_energy.len() as f64
            };
            (if *include_fixed_damage { fixed } else { 0.0 }) + *damage_per_energy as f64 * count
        }
        Mechanic::ExtraDamagePerSpecificEnergy {
            energy_type,
            damage_per_energy,
        } => fixed + *damage_per_energy as f64 * count_attached(&|e| e == energy_type),
        Mechanic::ExtraDamagePerSpecificEnergyAllYours {
            energy_type,
            damage_per_energy,
        } => {
            let count = state
                .enumerate_in_play_pokemon(player)
                .flat_map(|(_, c)| c.attached_energy.iter())
                .filter(|e| *e == energy_type)
                .count() as f64;
            fixed + *damage_per_energy as f64 * count
        }
        // eval1: Magmar's Derisive Roasting uses the defending Active's public
        // conditions. Match the apply-side count; Poison/Burn can coexist with one
        // of Asleep, Confused or Paralyzed. Count kinds, not duplicate status entries.
        Mechanic::ExtraDamagePerOpponentSpecialCondition {
            damage_per_condition,
        } => {
            let count = state.maybe_get_active(opponent).map_or(0, |defender| {
                [
                    StatusCondition::Asleep,
                    StatusCondition::Burned,
                    StatusCondition::Confused,
                    StatusCondition::Paralyzed,
                    StatusCondition::Poisoned,
                ]
                .into_iter()
                .filter(|condition| defender.has_status(*condition))
                .count()
            });
            fixed + *damage_per_condition as f64 * count as f64
        }
        Mechanic::ExtraDamagePerTrainerTypeInDiscard {
            trainer_type,
            damage_per_card,
        } => {
            let count = state.discard_piles[player]
                .iter()
                .filter(|c| match c {
                    Card::Trainer(t) => t.trainer_card_type == *trainer_type,
                    _ => false,
                })
                .count() as f64;
            fixed + *damage_per_card as f64 * count
        }
        Mechanic::ExtraDamagePerOwnPoint { damage_per_point } => {
            fixed + *damage_per_point as f64 * state.points[player] as f64
        }
        Mechanic::ExtraDamagePerOpponentPointDuringOwnLastTurn { damage_per_point } => {
            fixed
                + *damage_per_point as f64
                    * state.points_gained_during_own_last_turn[opponent] as f64
        }
        Mechanic::RevealTopDeckDamagePerPokemonName {
            reveal_count,
            name_fragment,
            damage_per,
        } => {
            // This is a future-damage heuristic, not the current attack forecast. A
            // shuffle's arbitrary sampled prefix must not improve an otherwise identical
            // position. Average over the known remaining multiset; the real/forecast attack
            // still reads its concrete prefix, including observation-authorized known tops.
            // ValueFunction receives no revealed-prefix provenance, so this heuristic does
            // not make a separate known-prefix adjustment or certify a knockout probability.
            let deck = &state.decks[player].cards;
            if deck.is_empty() {
                return 0.0;
            }
            // Partly hidden decks retain the prior visible-prefix lower bound. In
            // particular, do not dilute an authorized known top card across Unknown slots.
            if deck.iter().any(|card| matches!(card, Card::Unknown)) {
                return *damage_per as f64 * deck.iter().take(*reveal_count)
                    .filter(|card| matches!(card, Card::Pokemon(pokemon)
                        if pokemon.name.contains(name_fragment.as_str())))
                    .count() as f64;
            }
            let qualifying = deck.iter().filter(|card| {
                matches!(card, Card::Pokemon(pokemon) if pokemon.name.contains(name_fragment.as_str()))
            }).count();
            *damage_per as f64 * (*reveal_count).min(deck.len()) as f64
                * qualifying as f64 / deck.len() as f64
        }
        Mechanic::DirectDamage { damage, .. } => *damage as f64,
        Mechanic::DirectDamageAndSelfCardEffect { damage, .. } => *damage as f64,
        Mechanic::DelayedSpotDamage { amount } => *amount as f64,
        Mechanic::AlsoBenchDamage {
            opponent: hits_opponent,
            damage,
            ..
        }
        | Mechanic::AlsoChoiceBenchDamage {
            opponent: hits_opponent,
            damage,
        } => {
            if *hits_opponent {
                fixed + *damage as f64
            } else {
                fixed
            }
        }
        Mechanic::AlsoChoiceBenchDamageFiltered {
            opponent: hits_opponent,
            damage,
            filter,
        } => {
            let bench_player = if *hits_opponent { opponent } else { player };
            let has_target = state
                .enumerate_bench_pokemon(bench_player)
                .any(|(_, pokemon)| match filter {
                    BenchDamageFilter::Any => true,
                    BenchDamageFilter::Damaged => pokemon.is_damaged(),
                });
            if *hits_opponent && has_target {
                fixed + *damage as f64
            } else {
                fixed
            }
        }
        Mechanic::SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon { damage, .. } => {
            *damage as f64
        }
        Mechanic::SelfDiscardAllEnergyKnockOutOpponentActive => state
            .maybe_get_active(opponent)
            .map(|c| c.get_remaining_hp() as f64)
            .unwrap_or(fixed),
        Mechanic::CoinFlipExtraDamage { extra_damage }
        | Mechanic::CoinFlipExtraDamageOrSelfDamage { extra_damage, .. } => {
            fixed + *extra_damage as f64 / 2.0
        }
        Mechanic::ExtraDamageForEachHeads {
            include_fixed_damage,
            damage_per_head,
            num_coins,
        } => {
            (if *include_fixed_damage { fixed } else { 0.0 })
                + *damage_per_head as f64 * *num_coins as f64 / 2.0
        }
        // A fair flip-until-tails batch has E[heads] = 1. `Damage` replaces the printed
        // multiplier value; `BonusDamage` keeps the printed base and adds the same expectation.
        Mechanic::FlipUntilTailsDamage { damage_per_heads } => *damage_per_heads as f64,
        Mechanic::FlipUntilTailsBonusDamage { damage_per_heads } => {
            fixed + *damage_per_heads as f64
        }
        Mechanic::ExtraDamageIfExtraEnergy {
            required_extra_energy,
            extra_damage,
        } => {
            let mut full_cost = attack.energy_required.clone();
            full_cost.extend(required_extra_energy.iter().copied());
            if energy_missing(slot, &full_cost, state, player).is_empty() {
                fixed + *extra_damage as f64
            } else {
                fixed
            }
        }
        Mechanic::ExtraDamageIfCombinedActiveEnergyAtLeast {
            threshold,
            extra_damage,
        } => {
            let combined = state
                .maybe_get_active(player)
                .map(|c| c.attached_energy.len())
                .unwrap_or(0)
                + state
                    .maybe_get_active(opponent)
                    .map(|c| c.attached_energy.len())
                    .unwrap_or(0);
            if combined >= *threshold {
                fixed + *extra_damage as f64
            } else {
                fixed
            }
        }
        _ => fixed,
    }
}

/// Best damage the Pokémon occupying `slot` could throw using `form`'s attacks, discounted
/// by the energy still missing against the slot's CURRENT attached energy:
/// `fixed_damage / (1 + missing)`. `form` is the slot's own card for the in-place term, or
/// a prospective evolution for the potential term (energy survives evolution, so pricing a
/// future form against today's energy is exact).
fn best_attack_value(slot: &PlayedCard, form: &Card, state: &State, player: usize) -> f64 {
    best_attack_value_ex(slot, form, state, player, false, false)
}

/// §116: with `effect_aware`, each attack is valued at its ESTIMATED damage (see
/// [`estimated_attack_damage_ex`]) rather than `fixed_damage`; §117's `spread_aware`
/// extends the estimator's class coverage. All-false reproduces the §115 d-path
/// behaviour bit-for-bit; `(true, false)` the §116 f-path.
fn best_attack_value_ex(
    slot: &PlayedCard,
    form: &Card,
    state: &State,
    player: usize,
    effect_aware: bool,
    spread_aware: bool,
) -> f64 {
    if !effect_aware {
        return form
            .get_attacks()
            .iter()
            .filter(|atk| atk.fixed_damage > 0)
            .map(|atk| {
                let missing = energy_missing(slot, &atk.energy_required, state, player).len();
                atk.fixed_damage as f64 / (1.0 + missing as f64)
            })
            .fold(0.0, f64::max);
    }
    form.get_attacks()
        .iter()
        .filter_map(|atk| {
            let est = estimated_attack_damage_ex(atk, slot, state, player, spread_aware);
            if est <= 0.0 {
                return None;
            }
            let missing = energy_missing(slot, &atk.energy_required, state, player).len();
            Some(est / (1.0 + missing as f64))
        })
        .fold(0.0, f64::max)
}

/// §115 — what this slot could become: the best evolution reachable from the player's own
/// deck + hand (via [`get_highest_evolutions`], the same helper the online score already
/// uses), valued like a board Pokémon and discounted per evolution step still to take.
/// Damage counters carry through evolution in Pocket, so they are subtracted from the
/// target's HP.
fn evolution_potential(
    state: &State,
    player: usize,
    slot: &PlayedCard,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    if public_only {
        return 0.0;
    }
    let Card::Pokemon(current) = &slot.card else {
        return 0.0;
    };
    let mut available: Vec<Card> = state.decks[player].cards.to_vec();
    available.extend(state.hands[player].iter().cloned());
    get_highest_evolutions(&slot.card, &available)
        .iter()
        .filter_map(|target| {
            let Card::Pokemon(t) = target else {
                return None;
            };
            let steps = t.stage.saturating_sub(current.stage);
            if steps == 0 {
                return None;
            }
            let hp = t.hp.saturating_sub(slot.get_damage_counters()) as f64;
            let dmg = best_attack_value_ex(slot, target, state, player, effect_aware, reserve_aware);
            Some((hp + K_DAMAGE * dmg) * EVOLUTION_STEP_DISCOUNT.powi(steps as i32))
        })
        .fold(0.0, f64::max)
}

/// Helper function to calculate relevant energy for a Pokemon
fn get_relevant_energy(state: &State, player: usize, card: &PlayedCard) -> f64 {
    let most_expensive_attack_cost: Vec<EnergyType> = card
        .card
        .get_attacks()
        .iter()
        .map(|atk| atk.energy_required.clone())
        .max()
        .unwrap_or_default();

    let missing = energy_missing(card, &most_expensive_attack_cost, state, player);

    let total = most_expensive_attack_cost.len() as f64;
    total - missing.len() as f64
}

/// Calculate active safety
/// Defined as remaining HP divided by knockout points
fn calculate_active_safety(state: &State, player: usize) -> f64 {
    let Some(active_pokemon) = state.maybe_get_active(player) else {
        return 0.0; // No safety if no active pokemon
    };

    let ko_points = active_pokemon.card.get_knockout_points() as f64;
    let hp = active_pokemon.get_remaining_hp() as f64;

    hp / ko_points.max(1.0)
}

/// Calculate online score for active pokemon (0.0 to 1.0)
/// Returns 1.0 if the active pokemon has enough energy to use the highest attack
/// of its highest evolution available in deck+hand
/// With `projected` (kpr), the score is taken on the Active as it will stand over that [`Horizon`]: its attached
/// Energy plus [`projected_active_energy`]. The formula is otherwise unchanged.
fn calculate_active_pokemon_online_score(
    state: &State,
    player: usize,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
    projected: Option<Horizon>,
) -> f64 {
    let Some(active_pokemon) = state.maybe_get_active(player) else {
        return 0.0;
    };
    if let Some(horizon) = projected {
        let charged = at_next_attack(state, player, active_pokemon, horizon);
        return pokemon_online_score(state, player, &charged, public_only, effect_aware, reserve_aware);
    }
    pokemon_online_score(state, player, active_pokemon, public_only, effect_aware, reserve_aware)
}

/// kpr: how far ahead an Active is projected. Each side is read so that its value doesn't step inside the
/// searching player's own search, which runs from its turn to the start of the opponent's next turn (kp's blind
/// search goes no further).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Horizon {
    /// The evaluating player's own Active: ready by its next turn at the latest. While the owner's turn is running,
    /// this turn's unused sources count and so do next turn's; otherwise next turn's only. It steps only at the
    /// start of the owner's own turn, which the owner's search doesn't reach.
    ThroughNextTurn,
    /// The opponent's Active: at its very next attack. While the owner's turn is running, this turn's sources only;
    /// otherwise next turn's. It steps only at the end of the owner's turn, which the searching player's search
    /// doesn't reach (it stops at the start of that turn).
    NextAttack,
}

/// kpr: `owner`'s Active as it will stand over `horizon`: a copy with [`projected_active_energy`] attached.
fn at_next_attack(state: &State, owner: usize, active: &PlayedCard, horizon: Horizon) -> PlayedCard {
    let mut charged = active.clone();
    charged.attached_energy.extend(projected_active_energy(state, owner, active, horizon));
    charged
}

/// kpr: whether `owner`'s current turn can bring no more Energy or attacks: it has attacked, or its end is
/// already under way (a pending end, a forced `EndTurn` on the stack, a deferred or paused Checkup, an
/// end-of-turn evolution).
fn owner_turn_is_over(state: &State, owner: usize) -> bool {
    state.end_turn_pending
        || state.attack_name_used_this_turn[owner].is_some()
        || state.move_generation_stack.iter().any(|(_, choices)| {
            matches!(choices.as_slice(), [SimpleAction::EndTurn])
                || choices.iter().any(|choice| {
                    matches!(
                        choice,
                        SimpleAction::ResolvePokemonCheckup
                            | SimpleAction::FinishPokemonCheckup
                            | SimpleAction::ResolveEndTurnEvolution { .. }
                    )
                })
        })
}

/// kpr: the Energy `owner`'s Active will have been given by the end of `horizon`, from public sources its owner
/// controls.
///
/// Timing. The owner's turn is running if `owner` is to move and the turn isn't over ([`owner_turn_is_over`]).
/// - [`Horizon::ThroughNextTurn`] (the evaluating player's own Active): while the turn is running, this turn's unused
///   sources count, and so do next turn's; otherwise next turn's only. For the missing Energy of any one attack this
///   is the same as "this turn if this turn's sources pay for it, else next turn with both", so the same board scores
///   the same mid-turn and after the turn ends, except for sources left unused, which are really lost.
/// - [`Horizon::NextAttack`] (the opponent's Active): while the turn is running, this turn's sources only; otherwise
///   next turn's. At the opponent's rotation `next` becomes `current`, so its reading is the same just before and
///   just after the start of its turn.
///
/// Next turn is `turn_count + 2` while `owner` is to move, else `turn_count + 1`. Nothing is projected during setup
/// (turn 0).
///
/// Sources, each turn:
/// - the turn's attach from the Energy Zone, of the visible type: `current` this turn (if still unused), `next` next
///   turn; none if the Zone shows no type, or a `NoEnergyFromZoneToActive` turn effect covers that turn;
/// - Abilities that attach Energy to the Active, each once a turn, keyed on their mechanic (one already used this
///   turn counts only next turn): `AttachEnergyFromZoneToActiveTypedPokemon` (Ice Maker: to an Active of its type);
///   `AttachEnergyFromZoneToYourTypedPokemon`, `AttachEnergyFromZoneToSelf` and `AttachEnergyFromZoneToSelfAndDamage`
///   (Roar in Unison) when the Active holds them (the typed one only if the Active is of its type);
///   `AttachEnergyFromDiscardToSelfAndDamage` (Combust) when the Active holds it and that Energy is in the discard
///   pile; `AttachEnergyFromDiscardToActiveTypedFromBench` (Dragon's Blessing) from the Bench to an Active of its type.
///   The Zone ones are blocked with the turn's attach.
/// - Discard-pile sources take each discarded Energy once. Dragon's Blessing takes the type that leaves the Active's
///   attacks fewest missing Energy (the lowest for any one attack, then the total), ties to the one discarded first,
///   after the turn's other sources.
/// - An Ability that damages its holder is skipped once the damage it and earlier ones do would knock the Active out.
///
/// Not counted: an Ability that ends the turn (`AttachEnergyFromZoneToSelfAndEndTurn`: no attack follows it),
/// one-off Abilities (on evolving, end of the first turn), anything feeding the Bench, and Energy moved from the
/// Bench. Known limits: an attach that puts the Active to sleep (Snoozing Habit, Comatose, Stellar Cradle) still
/// counts; a `next` drawn inside the search (Rainbow Cave, or a search that crosses into `owner`'s next turn) is a
/// guess, which matters only for decks with more than one Energy type; an estimate that reads the Active from the
/// board (Energized Leaves' combined count) doesn't see the projected Energy; extra Energy can move the online
/// score's yardstick to a better attack with a lower ratio, only with mixed-type costs; and an observation hides the
/// opponent's stack, so a paused end of its turn (a point-denial coin at Checkup) reads as its turn running.
fn projected_active_energy(state: &State, owner: usize, active: &PlayedCard, horizon: Horizon) -> Vec<EnergyType> {
    if state.turn_count == 0 {
        return Vec::new();
    }
    let owner_to_move = state.current_player == owner;
    let running = owner_to_move && !owner_turn_is_over(state, owner);
    let mut turns: Vec<(u8, bool)> = Vec::with_capacity(2);
    if running {
        turns.push((state.turn_count, true));
    }
    if !running || horizon == Horizon::ThroughNextTurn {
        turns.push((state.turn_count + if owner_to_move { 2 } else { 1 }, false));
    }

    let mut charged = active.clone();
    let before = charged.attached_energy.len();
    let mut discard = state.discard_energies[owner].clone();
    let mut self_damage = 0u32;
    let remaining_hp = active.get_remaining_hp();
    for (turn, this_turn) in turns {
        let zone_blocked = state
            .get_turn_effects(turn)
            .iter()
            .any(|effect| matches!(effect, TurnEffect::NoEnergyFromZoneToActive));
        let zone = if this_turn {
            state.energy_zone[owner].current
        } else {
            state.energy_zone[owner].next
        };
        if !zone_blocked {
            charged.attached_energy.extend(zone);
        }
        let mut blessings = 0;
        for (slot, holder) in state.enumerate_in_play_pokemon(owner) {
            if this_turn && holder.ability_used {
                continue;
            }
            let holds_it = slot == 0;
            match get_in_play_ability_mechanic(state, holder) {
                Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type })
                    if !zone_blocked && state.pokemon_is_type(active, *energy_type) =>
                {
                    charged.attached_energy.push(*energy_type);
                }
                Some(AbilityMechanic::AttachEnergyFromZoneToYourTypedPokemon { energy_type })
                    if holds_it && !zone_blocked && state.pokemon_is_type(active, *energy_type) =>
                {
                    charged.attached_energy.push(*energy_type);
                }
                Some(AbilityMechanic::AttachEnergyFromZoneToSelf { energy_type, amount }) if holds_it && !zone_blocked => {
                    charged.attached_energy.extend(std::iter::repeat_n(*energy_type, *amount as usize));
                }
                Some(AbilityMechanic::AttachEnergyFromZoneToSelfAndDamage { energy_type, amount, self_damage: hit })
                    if holds_it && !zone_blocked && self_damage + hit < remaining_hp =>
                {
                    self_damage += hit;
                    charged.attached_energy.extend(std::iter::repeat_n(*energy_type, *amount as usize));
                }
                Some(AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage { energy_type, self_damage: hit })
                    if holds_it && self_damage + hit < remaining_hp =>
                {
                    if let Some(at) = discard.iter().position(|energy| energy == energy_type) {
                        discard.remove(at);
                        self_damage += hit;
                        charged.attached_energy.push(*energy_type);
                    }
                }
                Some(AbilityMechanic::AttachEnergyFromDiscardToActiveTypedFromBench { energy_type })
                    if !holds_it && state.pokemon_is_type(active, *energy_type) =>
                {
                    blessings += 1;
                }
                _ => {}
            }
        }
        for _ in 0..blessings {
            let Some(at) = best_discard_energy_for(state, owner, &charged, &discard) else { break };
            charged.attached_energy.push(discard.remove(at));
        }
    }
    charged.attached_energy.split_off(before)
}

/// kpr: the index in `discard` of the Energy that, attached to `charged`, leaves its attacks fewest missing Energy
/// (the lowest for any one attack, then the total), ties to the first; `None` if `discard` is empty.
fn best_discard_energy_for(state: &State, owner: usize, charged: &PlayedCard, discard: &[EnergyType]) -> Option<usize> {
    let mut best: Option<(usize, (usize, usize))> = None;
    for (at, energy) in discard.iter().enumerate() {
        if discard[..at].contains(energy) {
            continue;
        }
        let mut trial = charged.clone();
        trial.attached_energy.push(*energy);
        let missing: Vec<usize> = trial
            .card
            .get_attacks()
            .iter()
            .map(|atk| energy_missing(&trial, &atk.energy_required, state, owner).len())
            .collect();
        let key = (missing.iter().copied().min().unwrap_or(0), missing.iter().sum());
        if best.is_none_or(|(_, best_key)| key < best_key) {
            best = Some((at, key));
        }
    }
    best.map(|(at, _)| at)
}

/// The online score of any one of `player`'s in-play Pokemon: [`calculate_active_pokemon_online_score`]'s
/// measure, unchanged (its body, with the Active passed in), which `kq` also applies to the benched main
/// attacker ([`benched_main_attacker_online_score`]).
fn pokemon_online_score(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    // Get all cards available in deck + hand.
    //
    // §40: these are HIDDEN zones. When scoring an opponent we must not look in them, so
    // `public_only` leaves the list empty and the scan below falls through to the card that
    // is actually on the board — which is what an opposing player can see.
    let available_cards: Vec<Card> = if public_only {
        Vec::new()
    } else {
        let mut cards: Vec<Card> = state.decks[player].cards.to_vec();
        cards.extend(state.hands[player].iter().cloned());
        cards
    };

    // Find the highest evolution available
    let highest_evolutions = get_highest_evolutions(&active_pokemon.card, &available_cards);

    // If no evolutions found, use the current card
    let target_card = if highest_evolutions.is_empty() {
        &active_pokemon.card
    } else {
        // Use the first highest evolution (they should all be same stage)
        &highest_evolutions[0]
    };

    // §116 (`effect_aware`): anchor the score to the target's best PAYABLE attack —
    // fewest missing energy, then highest estimated damage — instead of the
    // lexicographically-"most expensive" cost, which for multi-type attackers can be a
    // cost this deck can never pay (so the score would be stuck regardless of charging).
    let yardstick_cost: Vec<EnergyType> = if effect_aware {
        target_card
            .get_attacks()
            .iter()
            .map(|atk| {
                let missing = energy_missing(active_pokemon, &atk.energy_required, state, player);
                let est =
                    estimated_attack_damage_ex(atk, active_pokemon, state, player, reserve_aware);
                (missing.len(), est, atk.energy_required.clone())
            })
            .min_by(|(m1, e1, _), (m2, e2, _)| {
                m1.cmp(m2).then(e2.partial_cmp(e1).unwrap_or(std::cmp::Ordering::Equal))
            })
            .map(|(_, _, cost)| cost)
            .unwrap_or_default()
    } else {
        // Get the highest attack energy cost from the target card (historical behaviour)
        target_card
            .get_attacks()
            .iter()
            .map(|atk| atk.energy_required.clone())
            .max()
            .unwrap_or_default()
    };

    if yardstick_cost.is_empty() {
        return 1.0; // No attack requirements, fully online
    }

    // Calculate how much energy we have vs need
    let missing = energy_missing(active_pokemon, &yardstick_cost, state, player);
    let total_needed = yardstick_cost.len() as f64;
    let have = total_needed - missing.len() as f64;

    // Return ratio (0.0 to 1.0)
    (have / total_needed).clamp(0.0, 1.0)
}

/// kq (B5): the best benched attacker's readiness: the highest [`pokemon_online_score`] (`k`'s Active online score,
/// unchanged) among `player`'s benched attackers, 0 when there is none. A benched Pokemon is an attacker when one
/// of its target forms (its highest evolutions in deck and hand on the evaluating player's own side, else the card
/// on the board; the opponent's side is priced from the board only) has an attack that costs Energy, can hit the
/// Active, and does damage: printed damage, a damage estimate with the spread classes on, or a damage mechanic the
/// estimator doesn't price ([`deals_damage_without_printing_it`]). So a free attack (Bonsly, Igglybuff: readiness
/// 1.0 for nothing), a Bench-only snipe or a utility attack can't stand in for an attacker, and benching another
/// Pokemon never lowers the score.
fn best_benched_attacker_online_score(
    state: &State,
    player: usize,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    let available_cards: Vec<Card> = if public_only {
        Vec::new()
    } else {
        let mut cards: Vec<Card> = state.decks[player].cards.to_vec();
        cards.extend(state.hands[player].iter().cloned());
        cards
    };
    let is_attacker = |pokemon: &PlayedCard| {
        let highest_evolutions = get_highest_evolutions(&pokemon.card, &available_cards);
        let forms: Vec<&Card> = if highest_evolutions.is_empty() {
            vec![&pokemon.card]
        } else {
            highest_evolutions.iter().collect()
        };
        forms.iter().any(|form| {
            form.get_attacks().iter().any(|atk| {
                !atk.energy_required.is_empty()
                    && !only_damages_the_bench(atk)
                    && (atk.fixed_damage > 0
                        || (effect_aware && estimated_attack_damage_ex(atk, pokemon, state, player, true) > 0.0)
                        || deals_damage_without_printing_it(atk))
            })
        })
    };
    state
        .enumerate_bench_pokemon(player)
        .filter(|(_, pokemon)| is_attacker(pokemon))
        .map(|(_, pokemon)| pokemon_online_score(state, player, pokemon, public_only, effect_aware, reserve_aware))
        .fold(0.0, f64::max)
}

/// kq: an attack with no printed damage whose mechanic damages or knocks out an opponent's Pokemon, among those the
/// damage estimate prices at 0 (found by scanning every card: the rest of that set is utility - draw, search, heal,
/// switch, charge, conditions). Keyed on mechanic types, not card names.
fn deals_damage_without_printing_it(attack: &Attack) -> bool {
    attack
        .effect
        .as_deref()
        .and_then(|effect| EFFECT_MECHANIC_MAP.get(effect))
        .is_some_and(|mechanic| {
            matches!(
                mechanic,
                Mechanic::CoinFlipDamageOrHealOpponent { .. }
                    | Mechanic::CoinFlipSetOpponentActiveRemainingHp { .. }
                    | Mechanic::CopyAttack { .. }
                    | Mechanic::DamageAllOpponentPokemon { .. }
                    | Mechanic::DamageAllOpponentPokemonWithNextTurnBonus { .. }
                    | Mechanic::DamageEqualToSelfDamage
                    | Mechanic::DamageEqualToSelfRemainingHp
                    | Mechanic::DamageToAnyOpponentPerTargetEnergy { .. }
                    | Mechanic::DirectDamageIfDamaged { .. }
                    | Mechanic::FlipCoinsRemoveOpponentActive { .. }
                    | Mechanic::HalveOpponentActiveRemainingHp
                    | Mechanic::InflictPoisonWithCustomCheckupDamage { .. }
                    | Mechanic::RandomDamageToOpponentPokemonPerSelfEnergy { .. }
                    | Mechanic::SelfDiscardAllEnergyAndDelayedSpotKnockOut
                    | Mechanic::SelfDiscardEnergyThenDamageAnyOpponentPokemon { .. }
                    | Mechanic::SelfDiscardTypedEnergyAndDamageAllOpponent { .. }
                    | Mechanic::SwitchInOpponentBenchedThenDamage { .. }
            )
        })
}

/// kq: an attack whose damage can only go to the opponent's Bench (its mechanic says so), not the Active.
fn only_damages_the_bench(attack: &Attack) -> bool {
    attack
        .effect
        .as_deref()
        .and_then(|effect| EFFECT_MECHANIC_MAP.get(effect))
        .is_some_and(|mechanic| {
            matches!(
                mechanic,
                Mechanic::DirectDamage { bench_only: true, .. }
                    | Mechanic::DirectDamageAndSelfCardEffect { bench_only: true, .. }
            )
        })
}

#[cfg(test)]
mod soul_counter_tests {
    use super::*;
    use crate::{card_ids::CardId, database::get_card_by_enum};

    #[test]
    fn soul_counter_expected_damage_uses_the_same_turn_history_as_resolution() {
        let attacker = PlayedCard::from_id(CardId::B4a018HisuianBasculegion);
        let defender = PlayedCard::from_id(CardId::B4037WailordEx);
        let mut state = State::default();
        state.set_board(vec![attacker], vec![defender]);
        state.current_player = 0;
        state.points[1] = 3;
        state.points_gained_this_turn[1] = 2;
        let attack = get_card_by_enum(CardId::B4a018HisuianBasculegion).get_attacks()[0].clone();

        assert_eq!(
            estimated_attack_damage(&attack, state.get_active(0), &state, 0),
            50.0,
            "lifetime and current-turn points must not inflate the estimate"
        );

        state.points_gained_during_own_last_turn[1] = 2;
        assert_eq!(
            estimated_attack_damage(&attack, state.get_active(0), &state, 0),
            150.0
        );
    }
}

#[cfg(test)]
mod filtered_bench_damage_estimate_tests {
    use super::*;
    use crate::{card_ids::CardId, database::get_card_by_enum};

    #[test]
    fn thunderclaw_estimate_only_includes_bench_damage_when_a_target_is_eligible() {
        let attacker = PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx);
        let attack = get_card_by_enum(CardId::B4a021TeamRocketsZapdosEx).get_attacks()[1].clone();
        let mut state = State::default();
        state.set_board(
            vec![attacker],
            vec![
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::A1056BlastoiseEx),
            ],
        );
        state.current_player = 0;

        assert_eq!(estimated_attack_damage(&attack, state.get_active(0), &state, 0), 90.0);
        state.in_play_pokemon[1][1] =
            Some(PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170));
        assert_eq!(estimated_attack_damage(&attack, state.get_active(0), &state, 0), 140.0);
    }
}

#[cfg(test)]
mod geometric_damage_estimate_tests {
    use super::*;
    use crate::{card_ids::CardId, database::get_card_by_enum};

    #[test]
    fn flip_until_tails_uses_one_expected_head_and_preserves_bonus_base() {
        let state = State::default();
        let furfrou = PlayedCard::from_id(CardId::B4a064Furfrou);
        let continuous_steps = match get_card_by_enum(CardId::B4a064Furfrou) {
            Card::Pokemon(card) => card.attacks[0].clone(),
            _ => panic!("Furfrou must be a Pokemon"),
        };
        assert_eq!(
            estimated_attack_damage(&continuous_steps, &furfrou, &state, 0),
            30.0
        );

        let iron_treads = PlayedCard::from_id(CardId::B3a051IronTreads);
        let rolling_spin = match get_card_by_enum(CardId::B3a051IronTreads) {
            Card::Pokemon(card) => card.attacks[0].clone(),
            _ => panic!("Iron Treads must be a Pokemon"),
        };
        assert_eq!(
            estimated_attack_damage(&rolling_spin, &iron_treads, &state, 0),
            80.0
        );
    }
}

#[cfg(test)]
mod rocket_frenzy_future_estimate_tests {
    use super::*;
    use crate::{card_ids::CardId,database::get_card_by_enum};

    fn estimate(ids: &[CardId]) -> f64 {
        let mut state=State::default();
        let slot=PlayedCard::from_id(CardId::PB091TeamRocketsWobbuffet);
        let attack=slot.card.get_attacks()[0].clone();
        state.decks[0].cards=ids.iter().map(|id|get_card_by_enum(*id)).collect();
        estimated_attack_damage(&attack,&slot,&state,0)
    }

    #[test]
    fn rocket_frenzy_future_mean_handles_empty_short_and_nonqualifying_decks() {
        assert_eq!(estimate(&[]),0.0);
        // All three cards would be revealed; only the two Pokemon qualify.
        assert_eq!(estimate(&[CardId::PB088TeamRocketsScyther,
            CardId::B4a069TeamRocketsResearcher,CardId::PB091TeamRocketsWobbuffet]),60.0);
        assert_eq!(estimate(&[CardId::B4a069TeamRocketsResearcher;8]),0.0);
        assert_eq!(estimate(&[CardId::PB091TeamRocketsWobbuffet;8]),180.0);
    }

    #[test]
    fn rocket_frenzy_future_mean_counts_physical_copies_not_prefix_positions() {
        // Four qualifying physical copies among eight cards: six draws average three = 90.
        let mut ids=vec![CardId::PB091TeamRocketsWobbuffet;4];
        ids.extend(vec![CardId::A1001Bulbasaur;4]);
        for _ in 0..8 {
            assert_eq!(estimate(&ids),90.0);
            ids.rotate_left(1);
        }
    }

    #[test]
    fn rocket_frenzy_future_mean_preserves_fractional_expected_damage() {
        // The sole qualifying card is in six of seven equally likely six-card reveals.
        let mut ids=vec![CardId::A1001Bulbasaur;6];
        ids.push(CardId::PB091TeamRocketsWobbuffet);
        assert!((estimate(&ids)-180.0/7.0).abs()<1e-12);
    }

    #[test]
    fn rocket_frenzy_future_estimate_preserves_known_prefix_in_partly_hidden_deck() {
        let slot=PlayedCard::from_id(CardId::PB091TeamRocketsWobbuffet);
        let attack=slot.card.get_attacks()[0].clone();
        let mut state=State::default();
        state.decks[1].cards=vec![Card::Unknown;20];
        state.decks[1].cards[0]=get_card_by_enum(CardId::PB091TeamRocketsWobbuffet);
        assert_eq!(estimated_attack_damage(&attack,&slot,&state,1),30.0);
        state.decks[1].cards[0]=get_card_by_enum(CardId::B4a069TeamRocketsResearcher);
        assert_eq!(estimated_attack_damage(&attack,&slot,&state,1),0.0);
        state.decks[1].cards[0]=Card::Unknown;
        assert_eq!(estimated_attack_damage(&attack,&slot,&state,1),0.0);
    }
}

#[cfg(test)]
mod kq_feature_tests {
    //! B5 `kq` features, each checked in a built position against `k`'s evaluator.
    use super::*;
    use crate::actions::{Action, SimpleAction};
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::test_support::{attack_action, get_initialized_game};

    /// Player 0: `victim` Active (and `victim_bench`). Player 1: `threat` Active (and `threat_bench`).
    /// Player 0 is to move on turn 5 and hasn't attacked.
    fn board(victim: Vec<PlayedCard>, threat: Vec<PlayedCard>) -> State {
        let mut state = State::default();
        state.set_board(victim, threat);
        state.turn_count = 5;
        state.current_player = 0;
        state
    }

    fn bulbasaur(energy: usize) -> PlayedCard {
        PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy([EnergyType::Grass, EnergyType::Colorless][..energy].to_vec())
    }

    fn with_effect(mut pokemon: PlayedCard, effect: CardEffect, turns: u8) -> PlayedCard {
        pokemon.add_effect(effect, turns);
        pokemon
    }

    fn hitmonlee() -> PlayedCard {
        PlayedCard::from_id(CardId::A1154Hitmonlee)
    }

    /// Turns until `player`'s opponent wins, as the clock prices it for k (`kq = false`) and kq.
    fn clock(state: &State, player: usize, kq: bool) -> f64 {
        calculate_turns_until_opponent_wins_damage_aware(state, player, false, true, false, true, kq, false, None)
    }

    /// [`first_attack_turn`] for `owner`, with the clock's own damage estimate and pace.
    fn first(state: &State, owner: usize, max_damage: f64) -> Option<FirstAttackTurn> {
        let damage = |atk: &Attack, slot: &PlayedCard| -> u32 {
            estimated_attack_damage_ex(atk, slot, state, owner, false).round() as u32
        };
        first_attack_turn(state, owner, max_damage, &damage)
    }

    #[test]
    fn next_attack_reduction_prices_each_effect_type_on_the_first_attack_turn() {
        // Hitmonlee (80 HP) v Bulbasaur with Vine Whip paid for (40): k counts 2 turns.
        let plain = board(vec![hitmonlee()], vec![bulbasaur(2)]);
        assert_eq!(first(&plain, 1, 40.0), None);
        assert_eq!((clock(&plain, 0, false), clock(&plain, 0, true)), (2.0, 2.0));
        let cases = [
            (vec![CardEffect::ReducedAttackDamage { amount: 30 }], vec![(1.0, 10.0)], 3.0),
            // Two cuts sum, as the engine sums them, floored at 0.
            (vec![CardEffect::ReducedAttackDamage { amount: 20 }, CardEffect::ReducedAttackDamage { amount: 30 }],
             vec![(1.0, 0.0)], 3.0),
            (vec![CardEffect::CannotAttack], vec![(1.0, 0.0)], 3.0),
            // Its only attack is blocked: nothing else to use.
            (vec![CardEffect::CannotUseAttack("Vine Whip".into())], vec![(1.0, 0.0)], 3.0),
            // The coin: all of Vine Whip half the time (2 turns), nothing the other half (3): 2.5 expected.
            (vec![CardEffect::CoinFlipToBlockAttack], vec![(0.5, 40.0), (0.5, 0.0)], 2.5),
        ];
        for (effects, through, turns) in cases {
            let mut threat = bulbasaur(2);
            for effect in &effects {
                threat.add_effect(effect.clone(), 1);
            }
            let state = board(vec![hitmonlee()], vec![threat]);
            assert_eq!(first(&state, 1, 40.0), Some(FirstAttackTurn { through, escape: 0.0 }), "{effects:?}");
            assert_eq!(clock(&state, 0, false), 2.0, "{effects:?}: k never reads it");
            assert_eq!(clock(&state, 0, true), turns, "{effects:?}");
        }
    }

    #[test]
    fn a_blocked_attack_leaves_the_best_other_attack_it_can_pay() {
        // Articuno ex with three Water: Blizzard (80) and Ice Wing (40) both paid for. Blizzard blocked: Ice Wing.
        let articuno = with_effect(
            PlayedCard::from_id(CardId::A1084ArticunoEx).with_energy(vec![EnergyType::Water; 3]),
            CardEffect::CannotUseAttack("Blizzard".into()),
            1,
        );
        let state = board(vec![hitmonlee()], vec![articuno]);
        assert_eq!(first(&state, 1, 80.0), Some(FirstAttackTurn { through: vec![(1.0, 40.0)], escape: 0.0 }));
        // Hitmonlee (80 HP): k says one turn; kq says Ice Wing then Blizzard, two.
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (1.0, 2.0));
        // With two Water, Ice Wing blocked: Blizzard is one short, and the turn's Water pays for it (capped at
        // the clock's pace, Ice Wing's 40): kq agrees with k.
        let articuno = with_effect(
            PlayedCard::from_id(CardId::A1084ArticunoEx).with_energy(vec![EnergyType::Water; 2]),
            CardEffect::CannotUseAttack("Ice Wing".into()),
            1,
        );
        let state = board(vec![hitmonlee()], vec![articuno]);
        assert_eq!(first(&state, 1, 40.0), Some(FirstAttackTurn { through: vec![(1.0, 40.0)], escape: 0.0 }));
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (2.0, 2.0));
    }

    #[test]
    fn next_attack_reduction_follows_the_effects_timing() {
        let cut = || CardEffect::ReducedAttackDamage { amount: 30 };
        // 0 turns left while player 0 is to move: it ends before Bulbasaur's next turn.
        let state = board(vec![hitmonlee()], vec![with_effect(bulbasaur(2), cut(), 0)]);
        assert_eq!(first(&state, 1, 40.0), None);
        // 0 turns left on Bulbasaur's own turn before it attacks: this is the turn it covers.
        let mut state = state;
        state.current_player = 1;
        assert!(first(&state, 1, 40.0).is_some());
        // One Energy short on its own turn: it attaches this turn's Energy and attacks through the cut...
        let mut short = board(vec![hitmonlee()], vec![with_effect(bulbasaur(1), cut(), 0)]);
        short.current_player = 1;
        short.energy_zone[1].current = Some(EnergyType::Grass);
        assert!(first(&short, 1, 40.0).is_some());
        // ...but once this turn's Energy is spent it can't attack before the cut has gone.
        short.energy_zone[1].current = None;
        assert_eq!(first(&short, 1, 40.0), None);
        // The same after Bulbasaur has attacked this turn: spent.
        state.attack_name_used_this_turn[1] = Some("Vine Whip".into());
        assert_eq!(first(&state, 1, 40.0), None);
        // One Energy short: in Pocket it attaches and attacks on its next turn, the turn the effect covers.
        let state = board(vec![hitmonlee()], vec![with_effect(bulbasaur(1), cut(), 1)]);
        assert_eq!(first(&state, 1, 40.0), Some(FirstAttackTurn { through: vec![(1.0, 10.0)], escape: 0.0 }));
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (3.0, 4.0));
        // Two Energy short: its first attack is two turns later, after a one-turn effect has ended...
        let state = board(vec![hitmonlee()], vec![with_effect(bulbasaur(0), cut(), 1)]);
        assert_eq!(first(&state, 1, 40.0), None);
        // ...but not after one that lasts while it stays Active (Octazooka's coin, u8::MAX turns).
        let state = board(
            vec![hitmonlee()],
            vec![with_effect(bulbasaur(0), CardEffect::CoinFlipToBlockAttack, crate::effects::UNTIL_LEAVES_ACTIVE_SPOT)],
        );
        assert!(first(&state, 1, 40.0).is_some());
        // Effects that don't touch its own attacks are not read.
        let state = board(vec![hitmonlee()], vec![with_effect(bulbasaur(2), CardEffect::ReducedDamage { amount: 30 }, 1)]);
        assert_eq!(first(&state, 1, 40.0), None);
    }

    #[test]
    fn the_owner_escapes_into_a_ready_benched_attacker_when_that_is_faster() {
        // A paid-up Bulbasaur on the Bench: retreating clears the lock and Vine Whip still lands: k's 2 turns.
        let locked = || with_effect(bulbasaur(2), CardEffect::CannotAttack, 1);
        let state = board(vec![hitmonlee()], vec![locked(), bulbasaur(2)]);
        assert_eq!(first(&state, 1, 40.0), Some(FirstAttackTurn { through: vec![(1.0, 0.0)], escape: 40.0 }));
        assert_eq!(clock(&state, 0, true), clock(&state, 0, false));
        // One Energy short on the Bench still escapes (attach, retreat, attack).
        let state = board(vec![hitmonlee()], vec![locked(), bulbasaur(1)]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 40.0);
        // A weak benched attacker (Riolu's Fighting Fist, 10) doesn't beat waiting: 3 turns either way.
        let riolu = PlayedCard::from_id(CardId::B3079Riolu).with_energy(vec![EnergyType::Fighting]);
        let state = board(vec![hitmonlee()], vec![locked(), riolu]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 10.0);
        assert_eq!(clock(&state, 0, true), 3.0);
        // A Bench-only snipe (Hitmonlee's Stretch Kick) can't hit the Active being knocked out: no escape.
        let sniper = hitmonlee().with_energy(vec![EnergyType::Fighting]);
        let state = board(vec![hitmonlee()], vec![locked(), sniper]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 0.0);
        assert_eq!(clock(&state, 0, true), 3.0);
    }

    #[test]
    fn the_escape_never_outpaces_the_clock_and_needs_a_payable_retreat() {
        // A benched Articuno ex (two Water; Blizzard 80 once the turn's Water goes on) behind a locked Bulbasaur:
        // the escape is capped at the clock's pace (40), so kq is never faster than k (2 turns).
        let articuno = |water| PlayedCard::from_id(CardId::A1084ArticunoEx).with_energy(vec![EnergyType::Water; water]);
        let state = board(vec![hitmonlee()], vec![with_effect(bulbasaur(2), CardEffect::CannotAttack, 1), articuno(2)]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 40.0);
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (2.0, 2.0));
        // A locked Articuno ex (one Water, Retreat Cost 2) behind a Bulbasaur one Energy short: the turn's Energy
        // can pay for Vine Whip or towards the retreat, not both, so there is no escape and the lock costs a turn.
        let state = board(vec![hitmonlee()], vec![with_effect(articuno(1), CardEffect::CannotAttack, 1), bulbasaur(1)]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 0.0);
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (3.0, 4.0));
        // With two Water on Articuno the retreat is paid and Vine Whip lands: k's 2 turns.
        let state = board(vec![hitmonlee()], vec![with_effect(articuno(2), CardEffect::CannotAttack, 1), bulbasaur(1)]);
        assert_eq!(first(&state, 1, 40.0).unwrap().escape, 40.0);
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (2.0, 2.0));
    }

    #[test]
    fn only_the_active_threat_and_only_the_first_knockout_are_repriced() {
        // The best threat is a benched Mega Lucario ex (Fighting Pulse 90, two Energy short) behind an unpowered
        // Articuno ex carrying a lasting coin block: the threat isn't the Active, so kq changes nothing (3 turns).
        let articuno = with_effect(
            PlayedCard::from_id(CardId::A1084ArticunoEx),
            CardEffect::CoinFlipToBlockAttack,
            crate::effects::UNTIL_LEAVES_ACTIVE_SPOT,
        );
        let state = board(vec![hitmonlee()], vec![articuno, PlayedCard::from_id(CardId::B3081MegaLucarioEx)]);
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (3.0, 3.0));
        // Hitmonlee then a benched Riolu (60 HP): the -30 slows the first knockout only (3 + 2 against 2 + 2).
        let riolu = PlayedCard::from_id(CardId::B3079Riolu);
        let state = board(
            vec![hitmonlee(), riolu],
            vec![with_effect(bulbasaur(2), CardEffect::ReducedAttackDamage { amount: 30 }, 1)],
        );
        assert_eq!((clock(&state, 0, false), clock(&state, 0, true)), (4.0, 5.0));
    }

    #[test]
    fn the_evaluators_own_locked_attacker_counts_against_it() {
        // Player 0's own Bulbasaur can't attack this turn (a self-lock): player 1's clock (turns until player 0
        // wins) gains a turn, and kq's value for player 0 drops by the clock's 100.
        let state = board(vec![with_effect(bulbasaur(2), CardEffect::CannotAttack, 1)], vec![hitmonlee()]);
        assert_eq!((clock(&state, 1, false), clock(&state, 1, true)), (2.0, 3.0));
        let gain = public_clock_effect_kq_value_function(&state, 0) - public_clock_effect_value_function(&state, 0);
        assert_eq!(gain, -100.0);
    }

    /// Through the Game API: Bonsly's Teary Attack (-30 on the Defending Pokemon's next attack) lands on
    /// Bulbasaur and Bonsly's turn ends. Bonsly (30 HP) now survives Vine Whip's reduced 10, so kq's clock
    /// counts one more turn before Bulbasaur can win: +100 for Bonsly's side, the clock's weight per turn.
    /// k's evaluation is unchanged, and nothing else differs (no Bench on either side).
    #[test]
    fn kq_values_a_landed_teary_attack_and_k_does_not() {
        let mut game = get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(vec![PlayedCard::from_id(CardId::B3078Bonsly)], vec![bulbasaur(2)]);
        state.current_player = 0;
        game.set_state(state);
        let k_before = public_clock_effect_value_function(&game.get_state_clone(), 0);
        let kq_before = public_clock_effect_kq_value_function(&game.get_state_clone(), 0);
        assert_eq!(kq_before, k_before, "no effect in play yet: kq and k agree");
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::B3078Bonsly, 0), is_stack: false });
        game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
        let after = game.get_state_clone();
        assert_eq!(after.current_player, 1);
        let k = public_clock_effect_value_function(&after, 0);
        let kq = public_clock_effect_kq_value_function(&after, 0);
        assert_eq!(kq - k, 100.0);
    }

    /// Player 0: Hitmonlee Active, then `bench`, with Mega Lucario ex in the deck (Riolu's target form: Fighting
    /// Pulse [FF] 90). Player 1: Bulbasaur Active, nothing benched.
    fn benched(bench: Vec<PlayedCard>) -> State {
        let mut mine = vec![hitmonlee()];
        mine.extend(bench);
        let mut state = board(mine, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
        state.decks[0].cards = vec![get_card_by_enum(CardId::B3081MegaLucarioEx)];
        state
    }

    fn riolu(fighting: usize) -> PlayedCard {
        PlayedCard::from_id(CardId::B3079Riolu).with_energy(vec![EnergyType::Fighting; fighting])
    }

    fn bench_score(state: &State, player: usize, public_only: bool) -> f64 {
        best_benched_attacker_online_score(state, player, public_only, true, false)
    }

    fn kq_gain(state: &State) -> f64 {
        public_clock_effect_kq_value_function(state, 0) - public_clock_effect_value_function(state, 0)
    }

    #[test]
    fn benched_attacker_readiness_counts_energy_on_the_attacker_being_built() {
        for (fighting, readiness) in [(0, 0.0), (1, 0.5), (2, 1.0)] {
            let state = benched(vec![riolu(fighting)]);
            assert_eq!(bench_score(&state, 0, false), readiness, "{fighting} Fighting toward Fighting Pulse [FF]");
            // In the value: 250 per unit of readiness, the opponent having no Bench; the clock is untouched.
            assert_eq!(kq_gain(&state), KQ_BENCH_ATTACKER_WEIGHT * readiness);
        }
        // The opponent sees the board only: Riolu is priced on its own Fighting Fist [F].
        assert_eq!(bench_score(&benched(vec![riolu(1)]), 0, true), 1.0);
    }

    #[test]
    fn the_opponents_bench_is_priced_from_the_board_only() {
        // Riolu (1 Fighting) on player 1's Bench and Mega Lucario ex in player 1's deck: player 0 sees Riolu on the
        // board (Fighting Fist [F], ready: 1.0, so -250). Reading player 1's deck would price Fighting Pulse (0.5).
        let mut state = benched(vec![]);
        state.in_play_pokemon[1][1] = Some(riolu(1));
        state.decks[1].cards = vec![get_card_by_enum(CardId::B3081MegaLucarioEx)];
        assert_eq!(kq_gain(&state), -KQ_BENCH_ATTACKER_WEIGHT);
    }

    #[test]
    fn the_best_benched_attacker_is_the_readiest_real_attacker() {
        let lucario = || PlayedCard::from_id(CardId::A2092Lucario).with_energy(vec![EnergyType::Fighting; 2]);
        // A paid-up Lucario (Submarine Blow [FF] 40) is ready: 1.0, and benching an unpowered Riolu next to it
        // doesn't lower that. Bench order doesn't matter.
        assert_eq!(bench_score(&benched(vec![lucario()]), 0, false), 1.0);
        assert_eq!(bench_score(&benched(vec![lucario(), riolu(0)]), 0, false), 1.0);
        assert_eq!(bench_score(&benched(vec![riolu(0), lucario()]), 0, false), 1.0);
        assert_eq!(bench_score(&benched(vec![riolu(0), riolu(2)]), 0, false), 1.0);
        assert_eq!(bench_score(&benched(vec![riolu(2), riolu(0)]), 0, false), 1.0);
        // A free attacker (Bonsly's Teary Attack costs nothing) is not an attacker: 0 alone, and it can't pin the
        // score at 1.0 while Riolu is being built.
        let bonsly = || PlayedCard::from_id(CardId::B3078Bonsly);
        assert_eq!(bench_score(&benched(vec![bonsly()]), 0, false), 0.0);
        assert_eq!(bench_score(&benched(vec![bonsly(), riolu(1)]), 0, false), 0.5);
        // Nor is a Bench-only snipe (Hitmonlee's Stretch Kick), even paid for.
        let sniper = hitmonlee().with_energy(vec![EnergyType::Fighting]);
        assert_eq!(bench_score(&benched(vec![sniper]), 0, false), 0.0);
    }

    #[test]
    fn attackers_with_no_printed_damage_still_count() {
        // Glaceon's Ice Blade (50 to any Pokemon, printed 0) is priced by the estimate; Xatu's Life Drain (the
        // Active's remaining HP becomes 10 on heads) is a damage mechanic the estimate doesn't price. Paid for: 1.0.
        let glaceon = PlayedCard::from_id(CardId::A3b073Glaceon).with_energy(vec![EnergyType::Water; 2]);
        assert_eq!(bench_score(&benched(vec![glaceon]), 0, false), 1.0);
        let xatu = PlayedCard::from_id(CardId::A4082Xatu).with_energy(vec![EnergyType::Psychic; 2]);
        assert_eq!(bench_score(&benched(vec![xatu]), 0, false), 1.0);
    }

    #[test]
    fn any_highest_evolution_can_make_a_benched_pokemon_an_attacker() {
        // Bulbasaur with a Grass, the deck listing a utility Ivysaur (Synthesis) before a damaging one (Razor Leaf):
        // either form makes Bulbasaur an attacker, whatever the deck order.
        let mut state = benched(vec![bulbasaur(1)]);
        state.decks[0].cards = vec![
            get_card_by_enum(CardId::B1a002Ivysaur),
            get_card_by_enum(CardId::A1002Ivysaur),
        ];
        assert!(bench_score(&state, 0, false) > 0.0);
        // With only the utility Ivysaur in the deck it isn't one.
        state.decks[0].cards = vec![get_card_by_enum(CardId::B1a002Ivysaur)];
        assert_eq!(bench_score(&state, 0, false), 0.0);
    }
}

#[cfg(test)]
mod kd_feature_tests {
    //! kd: the damage-aware clock prices the threat's damage to each victim through the victim's Weakness and
    //! persistent reductions, checked in built positions against `k`'s clock.
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;

    /// Player 0: `victim` Active (and Bench). Player 1: `threat` Active (and Bench). Player 0 to move on turn 5.
    fn board(victim: Vec<PlayedCard>, threat: Vec<PlayedCard>) -> State {
        let mut state = State::default();
        state.set_board(victim, threat);
        state.turn_count = 5;
        state.current_player = 0;
        state
    }

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    fn with(id: CardId, energy: EnergyType, count: usize) -> PlayedCard {
        mon(id).with_energy(vec![energy; count])
    }

    /// Mewtwo ex with Psychic Sphere (50) paid for.
    fn mewtwo() -> PlayedCard {
        with(CardId::A1129MewtwoEx, EnergyType::Psychic, 2)
    }

    /// Weedle with Sting (20) paid for.
    fn weedle() -> PlayedCard {
        with(CardId::A1008Weedle, EnergyType::Grass, 1)
    }

    /// Turns until player 0's opponent wins: (k's clock, kd's clock).
    fn clocks(state: &State, read_scanned_zones: bool) -> (f64, f64) {
        let clock = |kd: bool| {
            calculate_turns_until_opponent_wins_damage_aware(state, 0, read_scanned_zones, true, false, true, false, kd, None)
        };
        (clock(false), clock(true))
    }

    #[test]
    fn weakness_is_priced_per_victim() {
        // Two Riolu (60 HP, weak to Psychic) v Mewtwo ex's 50: k counts 2 + 2 turns, kd 1 + 1 (70 each).
        let riolus = board(vec![mon(CardId::B3079Riolu), mon(CardId::B3079Riolu)], vec![mewtwo()]);
        assert_eq!(clocks(&riolus, false), (4.0, 2.0));
        // Treecko is weak to Fire: no change.
        let treeckos = board(vec![mon(CardId::B3005Treecko), mon(CardId::B3005Treecko)], vec![mewtwo()]);
        assert_eq!(clocks(&treeckos, false), (4.0, 4.0));
        // One of each: only the Riolu speeds up, Active or benched.
        let mixed = board(vec![mon(CardId::B3079Riolu), mon(CardId::B3005Treecko)], vec![mewtwo()]);
        assert_eq!(clocks(&mixed, false), (4.0, 3.0));
        let mixed = board(vec![mon(CardId::B3005Treecko), mon(CardId::B3079Riolu)], vec![mewtwo()]);
        assert_eq!(clocks(&mixed, false), (4.0, 3.0));
        // A Colorless threat hits no Weakness: Pidgey's Peck (30) on Riolu is 2 turns either way.
        let pidgey = with(CardId::B1180Pidgey, EnergyType::Psychic, 2);
        assert_eq!(clocks(&board(vec![mon(CardId::B3079Riolu)], vec![pidgey]), false), (2.0, 2.0));
        // A damaged victim: Hitmonlee (weak to Psychic) at 70 HP falls to one 70 where k counts two 50s.
        let hitmonlee = mon(CardId::A1154Hitmonlee).with_remaining_hp(70);
        assert_eq!(clocks(&board(vec![hitmonlee], vec![mewtwo()]), false), (2.0, 1.0));
    }

    #[test]
    fn weakness_follows_the_evolution_the_threat_attacks_as() {
        // Swablu (Colorless) has no damaging attack of its own; its threat is Mega Altaria ex (Psychic) from its
        // owner's deck, Mega Harmony 40 with [P][P] already attached: one evolution step, then 40 a turn. Riolu is
        // weak to Psychic, so kd prices 60 a hit through the Mega's type: 1 + 1 turns, where k counts 1 + 2.
        let swablu = with(CardId::B1196Swablu, EnergyType::Psychic, 2);
        let mut state = board(vec![mon(CardId::B3079Riolu)], vec![swablu.clone()]);
        state.decks[1].cards.push(get_card_by_enum(CardId::B1102MegaAltariaEx));
        assert_eq!(clocks(&state, true), (3.0, 2.0));
        // The Mega is an ex, so Oricorio's Safeguard stops it: kd's sentinel.
        let mut state = board(vec![mon(CardId::A3066Oricorio)], vec![swablu]);
        state.decks[1].cards.push(get_card_by_enum(CardId::B1102MegaAltariaEx));
        assert_eq!(clocks(&state, true), (3.0, 30.0));
    }

    #[test]
    fn tied_evolutions_are_priced_the_same_whatever_the_deck_order() {
        // Eevee (A3b 055, no damaging attack, no Energy) with Espeon ex ([P][P] 80) and Umbreon ex ([D][D] 80) in its
        // owner's deck: a tie, 3 turns away. The victim, Espeon (90 HP), is weak to Darkness, so the form matters.
        // kd prices the same form (the first by card id, Espeon ex: 80, 2 hits) in either deck order.
        let clock = |order: [CardId; 2]| {
            let mut state = board(vec![mon(CardId::B3a020Espeon)], vec![mon(CardId::A3b055Eevee)]);
            state.decks[1].cards = order.iter().map(|id| get_card_by_enum(*id)).collect();
            clocks(&state, true)
        };
        assert_eq!(clock([CardId::A4083EspeonEx, CardId::A4112UmbreonEx]), (5.0, 5.0));
        assert_eq!(clock([CardId::A4112UmbreonEx, CardId::A4083EspeonEx]), (5.0, 5.0));
    }

    #[test]
    fn solid_shell_slows_the_clock() {
        // Shuckle ex (120 HP) v Bulbasaur's Vine Whip (40): k 3 turns, kd 6 (20 a hit).
        let bulbasaur = with(CardId::A1001Bulbasaur, EnergyType::Grass, 2);
        assert_eq!(clocks(&board(vec![mon(CardId::A4021ShuckleEx)], vec![bulbasaur]), false), (3.0, 6.0));
    }

    #[test]
    fn first_hit_protections_are_priced_once() {
        // Eiscue (80 HP, Ice Face -40 at full HP) v Mewtwo ex's 50: 10, then 50s: 3 turns where k counts 2.
        assert_eq!(clocks(&board(vec![mon(CardId::B1080Eiscue)], vec![mewtwo()]), false), (2.0, 3.0));
        // Mimikyu ex (120 HP, Disguise) v 50: the first hit is prevented, then 3 hits.
        assert_eq!(clocks(&board(vec![mon(CardId::B2073MimikyuEx)], vec![mewtwo()]), false), (3.0, 4.0));
    }

    #[test]
    fn a_victim_the_threat_cannot_damage_is_the_sentinel() {
        // Weedle's Sting (20) does 0 to Shuckle ex through Solid Shell: kd returns the clock's 30-turn sentinel.
        assert_eq!(clocks(&board(vec![mon(CardId::A4021ShuckleEx)], vec![weedle()]), false), (6.0, 30.0));
        // The same when that victim is on the Bench: Riolu takes 3 turns, then Shuckle ex can't be knocked out.
        let state = board(vec![mon(CardId::B3079Riolu), mon(CardId::A4021ShuckleEx)], vec![weedle()]);
        assert_eq!(clocks(&state, false), (9.0, 30.0));
        // Ice Face absorbing a whole hit leaves Eiscue at full HP, so it absorbs every hit.
        let bulbasaur = with(CardId::A1001Bulbasaur, EnergyType::Grass, 2);
        assert_eq!(clocks(&board(vec![mon(CardId::B1080Eiscue)], vec![bulbasaur]), false), (2.0, 30.0));
    }

    #[test]
    fn no_finite_kd_clock_passes_the_sentinel() {
        // Three Cloyster (120 HP, Shell Armor -10) v Sting: 12 hits each, 36, capped at 30 ("never") for kd.
        let cloysters = || vec![mon(CardId::A1067Cloyster), mon(CardId::A1067Cloyster), mon(CardId::A1067Cloyster)];
        assert_eq!(clocks(&board(cloysters(), vec![weedle()]), false), (18.0, 30.0));
        // Heavy Helmet on the Active Cloyster takes Sting to 0: still 30, never faster than without it.
        let mut helmeted = cloysters();
        helmeted[0] = mon(CardId::A1067Cloyster).with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));
        assert_eq!(clocks(&board(helmeted, vec![weedle()]), false), (18.0, 30.0));
    }

    #[test]
    fn a_victim_the_threat_cannot_damage_is_priced_with_the_best_attacker_that_can() {
        // Shuckle ex v Weedle (Sting 20, ready) and a benched Mewtwo ex with one [P] (Psychic Sphere 50, one short).
        // k's threat is Sting: 6 turns. Sting does 0 through Solid Shell, so kd prices Shuckle ex with Psychic
        // Sphere: 1 turn for its Energy, then 30 a hit, 4 hits: 5.
        let mewtwo_one = with(CardId::A1129MewtwoEx, EnergyType::Psychic, 1);
        let state = board(vec![mon(CardId::A4021ShuckleEx)], vec![weedle(), mewtwo_one.clone()]);
        assert_eq!(clocks(&state, false), (6.0, 5.0));
        // Two Shuckle ex: the fallback's Energy is counted once (5 + 4), not per victim (5 + 5).
        let state = board(vec![mon(CardId::A4021ShuckleEx), mon(CardId::A4021ShuckleEx)], vec![weedle(), mewtwo_one]);
        assert_eq!(clocks(&state, false), (12.0, 9.0));
    }

    #[test]
    fn victims_come_in_the_order_the_defender_would_promote_them() {
        // Riolu Active, Shuckle ex and Suicune ex benched, v Sting only. k takes Suicune ex next (more HP) and stops
        // at 3 points: 3 + 7. The defender would promote Shuckle ex, which Sting can't damage: kd's "never".
        let state = board(
            vec![mon(CardId::B3079Riolu), mon(CardId::A4021ShuckleEx), mon(CardId::A4a020SuicuneEx)],
            vec![weedle()],
        );
        assert_eq!(clocks(&state, false), (10.0, 30.0));
        // Opponent at 1 point, Treecko Active, Treecko and Riolu benched, v Mewtwo ex's 50. The next knockout wins,
        // so the defender promotes whichever lasts longer: Treecko (2 hits), not Riolu (1 hit, weak to Psychic).
        // Equal HP leaves k's order to the Bench slots; kd's is the same in either order.
        for bench in [[CardId::B3005Treecko, CardId::B3079Riolu], [CardId::B3079Riolu, CardId::B3005Treecko]] {
            let mut state = board(vec![mon(CardId::B3005Treecko), mon(bench[0]), mon(bench[1])], vec![mewtwo()]);
            state.points = [0, 1];
            assert_eq!(clocks(&state, false).1, 4.0);
        }
    }

    #[test]
    fn a_victim_already_at_0_hp_takes_no_turns() {
        let fainted = mon(CardId::B3079Riolu).with_remaining_hp(0);
        let state = board(vec![fainted, mon(CardId::B3005Treecko)], vec![mewtwo()]);
        assert_eq!(clocks(&state, false), (2.0, 2.0));
    }

    #[test]
    fn a_sniper_cannot_touch_the_active() {
        // Heatmor's Tongue Whip (30, Bench only) is the threat. k counts it knocking out the Active Vespiquen ex
        // (140 HP) in 5. It can't: with no other attacker and nothing to snipe, kd says "never".
        let heatmor = || with(CardId::B1044Heatmor, EnergyType::Fire, 1);
        assert_eq!(clocks(&board(vec![mon(CardId::B4011VespiquenEx)], vec![heatmor()]), false), (5.0, 30.0));
        // With a Combee benched and the opponent at 2 points, sniping Combee (50 HP, 30 a hit, no Weakness on the
        // Bench) wins in 2.
        let mut state = board(vec![mon(CardId::B4011VespiquenEx), mon(CardId::B4010Combee)], vec![heatmor()]);
        state.points = [0, 2];
        assert_eq!(clocks(&state, false), (5.0, 2.0));
        // Two Combee and the opponent at 1 point: the owner snipes both, 2 + 2.
        let mut state = board(
            vec![mon(CardId::B4011VespiquenEx), mon(CardId::B4010Combee), mon(CardId::B4010Combee)],
            vec![heatmor()],
        );
        state.points = [0, 1];
        assert_eq!(clocks(&state, false).1, 4.0);
        // A Protective Poncho on the only Combee: nothing can be scored, "never".
        let poncho = mon(CardId::B4010Combee).with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho));
        let mut state = board(vec![mon(CardId::B4011VespiquenEx), poncho], vec![heatmor()]);
        state.points = [0, 2];
        assert_eq!(clocks(&state, false).1, 30.0);
        // With a Charmander that can hit the Active (Ember 30, weak to Fire: 50), the Active falls to it instead.
        let charmander = with(CardId::A1033Charmander, EnergyType::Fire, 1);
        let state = board(vec![mon(CardId::B4011VespiquenEx)], vec![heatmor(), charmander]);
        assert_eq!(clocks(&state, false), (5.0, 3.0));
    }

    #[test]
    fn a_bonus_for_who_the_defender_is_counts_per_victim() {
        // Riolu's Fighting Fist is 10, +30 against a Pokemon ex. k's estimate reads 10: Shuckle ex in 12. kd prices
        // 40 - 20 (Solid Shell) = 20: 6, not "never".
        let riolu = with(CardId::B3079Riolu, EnergyType::Fighting, 1);
        assert_eq!(clocks(&board(vec![mon(CardId::A4021ShuckleEx)], vec![riolu]), false), (12.0, 6.0));
    }

    #[test]
    fn the_fallback_waits_only_for_energy_beyond_the_threats() {
        // Weedle with no Energy (Sting, one short) is the threat; Mewtwo ex with none is two short. Shuckle ex:
        // 1 turn for the threat's Energy, 1 more for Mewtwo's second, then 4 Psychic Spheres at 30: 6.
        let state = board(vec![mon(CardId::A4021ShuckleEx)], vec![mon(CardId::A1008Weedle), mon(CardId::A1129MewtwoEx)]);
        assert_eq!(clocks(&state, false), (7.0, 6.0));
    }

    #[test]
    fn the_fallback_hits_with_its_own_type() {
        // Weedle's Sting does 0 to Shuckle ex; Charmander (no Energy, Ember 30) is the fallback. Shuckle ex is weak to
        // Fire: 30 + 20 - 20 = 30 a hit, 1 turn for the Energy and 4 hits.
        let state = board(vec![mon(CardId::A4021ShuckleEx)], vec![weedle(), mon(CardId::A1033Charmander)]);
        assert_eq!(clocks(&state, false), (6.0, 5.0));
    }

    #[test]
    fn a_sniper_snipes_in_the_order_that_wins_soonest() {
        // Heatmor alone can't touch the Active Vespiquen ex. The opponent at 1 point needs 2 more: sniping the benched
        // Vespiquen ex (140 HP, 5 turns) does it alone, faster than Combee then Vespiquen ex (2 + 5).
        let heatmor = with(CardId::B1044Heatmor, EnergyType::Fire, 1);
        let mut state = board(
            vec![mon(CardId::B4011VespiquenEx), mon(CardId::B4010Combee), mon(CardId::B4011VespiquenEx)],
            vec![heatmor],
        );
        state.points = [0, 1];
        assert_eq!(clocks(&state, false).1, 5.0);
    }

    #[test]
    fn a_sniper_hits_a_benched_victim_where_it_is() {
        // Heatmor (Tongue Whip 30) is the threat and can't touch Bulbasaur; Charmander's Ember (50 on the Fire-weak
        // Bulbasaur) knocks it out in 2. Combee, benched, is sniped where it is: 30 a hit, no Weakness, 2 more.
        let state = board(
            vec![mon(CardId::A1001Bulbasaur), mon(CardId::B4010Combee)],
            vec![with(CardId::B1044Heatmor, EnergyType::Fire, 1), with(CardId::A1033Charmander, EnergyType::Fire, 1)],
        );
        assert_eq!(clocks(&state, false), (5.0, 4.0));
    }

    #[test]
    fn the_count_stops_at_3_points() {
        // The opponent at 2: knocking out Riolu wins, so the Shuckle ex that Sting can't damage never matters.
        let mut state = board(vec![mon(CardId::B3079Riolu), mon(CardId::A4021ShuckleEx)], vec![weedle()]);
        state.points = [0, 2];
        assert_eq!(clocks(&state, false), (3.0, 3.0));
    }

    #[test]
    fn the_fallback_with_the_most_damage_wins_a_tie_on_missing_energy() {
        // Sting does 0 to Shuckle ex. Riolu and Charmander are each one Energy short: Fighting Fist does 40 - 20 = 20,
        // Ember 30 + 20 (Weakness) - 20 = 30. kd takes Ember: 1 + 4.
        let state = board(
            vec![mon(CardId::A4021ShuckleEx)],
            vec![weedle(), mon(CardId::B3079Riolu), mon(CardId::A1033Charmander)],
        );
        assert_eq!(clocks(&state, false), (6.0, 5.0));
    }

    #[test]
    fn damage_to_the_bench_is_not_priced_on_the_active() {
        // Hoopa ex's Shadow Bullet: 30, and 20 to a benched Pokemon. The clock's estimate says 50; the Active takes 30,
        // 10 through Solid Shell: Shuckle ex in 12, where k counts 3.
        let hoopa = with(CardId::B4103HoopaEx, EnergyType::Darkness, 1);
        assert_eq!(clocks(&board(vec![mon(CardId::A4021ShuckleEx)], vec![hoopa]), false), (3.0, 12.0));
    }

    #[test]
    fn a_bonus_for_who_the_defender_is_needs_its_condition() {
        // Fighting Fist's +30 is only against a Pokemon ex: Riolu v Treecko (60 HP) is 10 a hit, 6 turns.
        let riolu = with(CardId::B3079Riolu, EnergyType::Fighting, 1);
        assert_eq!(clocks(&board(vec![mon(CardId::B3005Treecko)], vec![riolu]), false), (6.0, 6.0));
    }

    #[test]
    fn defender_identity_bonus_follows_each_condition() {
        let attack_with = |wanted: &dyn Fn(&Mechanic) -> bool| -> Attack {
            let mut texts: Vec<&str> =
                EFFECT_MECHANIC_MAP.iter().filter(|(_, mechanic)| wanted(mechanic)).map(|(text, _)| *text).collect();
            texts.sort();
            Attack {
                energy_required: vec![],
                title: "Test".to_string(),
                fixed_damage: 10,
                effect: Some(texts[0].to_string()),
            }
        };
        let state = State::default();
        let bonus = |attack: &Attack, victim: CardId| defender_identity_bonus(&state, attack, &mon(victim));
        let ex = attack_with(&|m| matches!(m, Mechanic::ExtraDamageIfEx { extra_damage: 30 }));
        assert_eq!((bonus(&ex, CardId::A1129MewtwoEx), bonus(&ex, CardId::B3005Treecko)), (30, 0));
        let darkness = attack_with(&|m| {
            matches!(m, Mechanic::ExtraDamageIfDefenderType { energy_types, extra_damage: 30 }
                if energy_types == &vec![EnergyType::Darkness])
        });
        assert_eq!((bonus(&darkness, CardId::B1155Deino), bonus(&darkness, CardId::B3005Treecko)), (30, 0));
        let basic = attack_with(&|m| {
            matches!(m, Mechanic::ExtraDamageIfDefenderStage { evolution: false, extra_damage: 60 })
        });
        assert_eq!((bonus(&basic, CardId::A1001Bulbasaur), bonus(&basic, CardId::A1034Charmeleon)), (60, 0));
        let zangoose = attack_with(&|m| matches!(m, Mechanic::ExtraDamageIfDefenderNamed { .. }));
        assert_eq!((bonus(&zangoose, CardId::A4a065Zangoose), bonus(&zangoose, CardId::A1001Bulbasaur)), (40, 0));
        let rocket = attack_with(&|m| matches!(m, Mechanic::ExtraDamageIfDefenderNameContains { .. }));
        assert_eq!((bonus(&rocket, CardId::B4a042TeamRocketsKoffing), bonus(&rocket, CardId::A1001Bulbasaur)), (70, 0));
        let ability = attack_with(&|m| matches!(m, Mechanic::ExtraDamageIfOpponentActiveHasAbility { .. }));
        assert_eq!((bonus(&ability, CardId::A4021ShuckleEx), bonus(&ability, CardId::A1001Bulbasaur)), (40, 0));
    }

    #[test]
    fn the_threats_own_text_reaches_the_clock() {
        // Staryu's Swift (20) isn't affected by effects on the opponent's Active: Solid Shell doesn't cut it, so
        // Shuckle ex falls in 6, not "never".
        let staryu = with(CardId::B4032Staryu, EnergyType::Water, 1);
        assert_eq!(clocks(&board(vec![mon(CardId::A4021ShuckleEx)], vec![staryu]), false), (6.0, 6.0));
    }

    #[test]
    fn disguise_is_not_a_victim_the_threat_cannot_damage() {
        // Mimikyu ex (120 HP, Disguise, weak to Darkness) v Mewtwo ex's Psychic Sphere (50, the threat) and
        // Zweilous's Darkness Fang (40 + 20 Weakness = 60), both ready. Sphere's first hit is prevented, but later
        // ones land, so the threat keeps the victim: 1 + 3. (Were the first hit taken as "can't damage", Darkness
        // Fang would take over: 1 + 2.)
        let zweilous = with(CardId::B1156Zweilous, EnergyType::Darkness, 2);
        let state = board(vec![mon(CardId::B2073MimikyuEx)], vec![mewtwo(), zweilous]);
        assert_eq!(clocks(&state, false).1, 4.0);
    }

    #[test]
    fn a_victim_at_0_hp_takes_no_turns_even_if_it_could_not_be_damaged() {
        let fainted = mon(CardId::A4021ShuckleEx).with_remaining_hp(0);
        let state = board(vec![fainted, mon(CardId::B3005Treecko)], vec![weedle()]);
        assert_eq!(clocks(&state, false), (3.0, 3.0));
    }

    #[test]
    fn a_sturdier_bench_never_shortens_the_count() {
        // Frigibax Active; Frigibax and Suicune ex benched; v Mewtwo ex's 50. The defender's longest order is Frigibax
        // then Suicune ex: 2 + 2 + 3. A Giant Cape on Suicune ex (160 HP) makes it 2 + 2 + 4, in either Bench order.
        let frigibax = || mon(CardId::B2a034Frigibax);
        for caped in [false, true] {
            let suicune = if caped {
                mon(CardId::A4a020SuicuneEx).with_tool(get_card_by_enum(CardId::A2147GiantCape))
            } else {
                mon(CardId::A4a020SuicuneEx)
            };
            let expected = if caped { 8.0 } else { 7.0 };
            let state = board(vec![frigibax(), frigibax(), suicune.clone()], vec![mewtwo()]);
            assert_eq!(clocks(&state, false).1, expected);
            let state = board(vec![frigibax(), suicune, frigibax()], vec![mewtwo()]);
            assert_eq!(clocks(&state, false).1, expected);
        }
    }

    #[test]
    fn the_kd_evaluator_prices_both_sides_and_nothing_else() {
        let k = public_clock_effect_value_function;
        let kd = public_clock_effect_kd_value_function;
        // Player 0's Riolu v player 1's Mewtwo ex. Player 0's clock drops a turn (Psychic Sphere does 70 to Riolu:
        // 2 turns to 1), worth -100. Player 1's clock drops 11 (Riolu, one Energy short, does 40 to an ex with Fighting
        // Fist, not 10: 1 + 15 turns to 1 + 4), worth +1,100.
        let exposed = board(vec![mon(CardId::B3079Riolu)], vec![mewtwo()]);
        assert_eq!(kd(&exposed, 0) - k(&exposed, 0), 1000.0);
        // Mirrored, the same two changes with the sides swapped.
        let threatening = board(vec![mewtwo()], vec![mon(CardId::B3079Riolu)]);
        assert_eq!(kd(&threatening, 0) - k(&threatening, 0), -1000.0);
        // No Weakness, reduction or defender bonus in play: the same value.
        let plain = board(vec![mon(CardId::B3005Treecko)], vec![mewtwo()]);
        assert_eq!(kd(&plain, 0), k(&plain, 0));
    }

    #[test]
    fn kd_reads_no_hidden_card_of_the_opponent() {
        // Player 1's Swablu has a Psychic Mega in its deck or hand, or a card of the same count that isn't one; my
        // Riolu is weak to Psychic. Evaluating as player 0, kd's value doesn't change: only the board is read.
        let value = |hidden: CardId, in_hand: bool| {
            let mut state = board(vec![mon(CardId::B3079Riolu)], vec![with(CardId::B1196Swablu, EnergyType::Psychic, 2)]);
            let card = get_card_by_enum(hidden);
            if in_hand {
                state.hands[1].push(card);
            } else {
                state.decks[1].cards.push(card);
            }
            public_clock_effect_kd_value_function(&state, 0)
        };
        for in_hand in [false, true] {
            assert_eq!(value(CardId::B1102MegaAltariaEx, in_hand), value(CardId::A1001Bulbasaur, in_hand));
        }
    }
}

#[cfg(test)]
mod kpr_feature_tests {
    //! kpr: the Active priced as it will stand at its next attack ([`projected_active_energy`]), in the online score
    //! and in the clock, checked in built positions against `k`'s values. Player 0 is the evaluating player unless a
    //! test says otherwise, so its Active is read over [`Horizon::ThroughNextTurn`].
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    fn with(id: CardId, energy: EnergyType, count: usize) -> PlayedCard {
        mon(id).with_energy(vec![energy; count])
    }

    /// Player 0 has `mine` in play, player 1 a Bulbasaur; player 1 is to move on turn 6, so player 0's next attack
    /// is its next turn, with `next` showing in its Energy Zone.
    fn opponents_turn(mine: Vec<PlayedCard>, next: Option<EnergyType>) -> State {
        let mut state = State::default();
        state.set_board(mine, vec![mon(CardId::A1001Bulbasaur)]);
        state.turn_count = 6;
        state.current_player = 1;
        state.energy_zone[0].next = next;
        state
    }

    /// As [`opponents_turn`], but player 0 is to move on turn 5 with `current` in its Energy Zone.
    fn my_turn(mine: Vec<PlayedCard>, current: Option<EnergyType>, next: Option<EnergyType>) -> State {
        let mut state = opponents_turn(mine, next);
        state.turn_count = 5;
        state.current_player = 0;
        state.energy_zone[0].current = current;
        state
    }

    /// Player 0's Active online score, player 0 evaluating: (k's, kpr's).
    fn scores(state: &State) -> (f64, f64) {
        let score = |projected| calculate_active_pokemon_online_score(state, 0, false, true, false, projected);
        (score(None), score(Some(Horizon::ThroughNextTurn)))
    }

    /// Turns until player 0 beats player 1, from player 1's side (player 0, evaluating, is the threat): (k's, kpr's).
    fn clocks(state: &State) -> (f64, f64) {
        let clock = |kpr| {
            calculate_turns_until_opponent_wins_damage_aware(state, 1, true, true, false, true, false, false, kpr)
        };
        (clock(None), clock(Some(Horizon::ThroughNextTurn)))
    }

    #[test]
    fn hydreigon_emptied_by_hyper_ray_is_ready_again_next_turn() {
        // Hyper Ray costs [D][D][D]. With no Energy left, k scores 0. Next turn the Zone gives one [D] and Roar in
        // Unison two more: kpr scores 1.
        let hydreigon = || vec![mon(CardId::B1157Hydreigon)];
        assert_eq!(scores(&opponents_turn(hydreigon(), Some(EnergyType::Darkness))), (0.0, 1.0));
        // With no Energy type showing in the Zone, only Roar in Unison counts: 2 of 3.
        assert_eq!(scores(&opponents_turn(hydreigon(), None)), (0.0, 2.0 / 3.0));
    }

    #[test]
    fn without_an_ability_only_the_turns_attach_counts() {
        // Zweilous (Darkness Fang, [D][D]) with no Energy: next turn's [D] makes it 1 of 2.
        let state = opponents_turn(vec![mon(CardId::B1156Zweilous)], Some(EnergyType::Darkness));
        assert_eq!(scores(&state), (0.0, 0.5));
    }

    #[test]
    fn the_same_board_scores_the_same_mid_turn_and_once_the_turn_is_over() {
        // Zweilous holding one [D], this turn's attach already made, [D] showing next: mid-turn its next attack is
        // next turn, 2 of 2, the same as once the turn is over. (Priced "this turn only", mid-turn would read 1 of 2
        // and ending the turn would gain 250 for nothing.)
        let mut state = my_turn(vec![with(CardId::B1156Zweilous, EnergyType::Darkness, 1)], None, Some(EnergyType::Darkness));
        assert_eq!(scores(&state), (0.5, 1.0));
        state.attack_name_used_this_turn[0] = Some("Darkness Fang".to_string());
        assert_eq!(scores(&state), (0.5, 1.0));
        // With this turn's [D] still unused, mid-turn counts it and next turn's; ending the turn without it loses it.
        let mut state = my_turn(vec![mon(CardId::B1156Zweilous)], Some(EnergyType::Darkness), Some(EnergyType::Darkness));
        assert_eq!(scores(&state), (0.0, 1.0));
        state.move_generation_stack.push((0, vec![SimpleAction::EndTurn]));
        assert_eq!(scores(&state), (0.0, 0.5));
    }

    #[test]
    fn the_opponents_active_is_priced_at_its_very_next_attack() {
        // Read as the opponent's Active ([`Horizon::NextAttack`]): while its turn runs, this turn's sources only.
        let as_opponent =
            |state: &State| calculate_active_pokemon_online_score(state, 0, false, true, false, Some(Horizon::NextAttack));
        // Zweilous holding one [D], this turn's attach made, [D] next, its owner to move: its next attack is this
        // turn, 1 of 2 (read as the evaluator's own, 2 of 2 by next turn).
        let mut state = my_turn(vec![with(CardId::B1156Zweilous, EnergyType::Darkness, 1)], None, Some(EnergyType::Darkness));
        assert_eq!((as_opponent(&state), scores(&state).1), (0.5, 1.0));
        // This turn's [D] still unused: 2 of 2 this turn.
        state.energy_zone[0].current = Some(EnergyType::Darkness);
        assert_eq!(as_opponent(&state), 1.0);
        // Once its turn is over, or on the other player's turn, next turn's: the two readings agree.
        state.energy_zone[0].current = None;
        state.attack_name_used_this_turn[0] = Some("Darkness Fang".to_string());
        assert_eq!((as_opponent(&state), scores(&state).1), (1.0, 1.0));
        let state = opponents_turn(vec![with(CardId::B1156Zweilous, EnergyType::Darkness, 1)], Some(EnergyType::Darkness));
        assert_eq!((as_opponent(&state), scores(&state).1), (1.0, 1.0));
    }

    #[test]
    fn the_opponents_reading_is_the_same_either_side_of_its_turn_start() {
        // The second review's board. Player 0, evaluating, to move on turn 5: Mega Lucario ex holding [F][F] (this
        // turn's attach made, [F] next) and a benched Riolu. Player 1: Chien-Pao ex (Icicle [W] 20; Diving Icicles
        // [W][W][W] 130) with no Energy, Baxcalibur (Ice Maker) benched, [W] next.
        let mut before = State::default();
        before.set_board(
            vec![with(CardId::B3081MegaLucarioEx, EnergyType::Fighting, 2), mon(CardId::B3079Riolu)],
            vec![mon(CardId::B2a037ChienPaoEx), mon(CardId::B2a036Baxcalibur)],
        );
        before.turn_count = 5;
        before.current_player = 0;
        before.energy_zone[0].next = Some(EnergyType::Fighting);
        before.energy_zone[1].next = Some(EnergyType::Water);
        // Player 1's turn starts: `next` rotates into `current`, and in player 0's search its new `next` is unknown.
        let mut after = before.clone();
        after.turn_count = 6;
        after.current_player = 1;
        after.energy_zone[1].current = after.energy_zone[1].next.take();
        // Turns until player 1 wins, from player 0's side. Before, player 1's next attack is next turn: [W] and Ice
        // Maker's [W] pay Icicle, 10 hits of 20 on Mega Lucario ex. After, its next attack is this turn: the same.
        let clock = |state: &State, horizon| {
            calculate_turns_until_opponent_wins_damage_aware(state, 0, false, true, false, true, false, false, Some(horizon))
        };
        assert_eq!(clock(&before, Horizon::NextAttack), 10.0);
        assert_eq!(clock(&after, Horizon::NextAttack), 10.0);
        // Read through its next turn, a second Ice Maker would pay Diving Icicles after the rotation: 2. That was the
        // step (about 800) against every line that ended player 0's turn.
        assert_eq!(clock(&after, Horizon::ThroughNextTurn), 2.0);
        // The whole evaluator: kpr's difference from k is the same on both sides of the boundary.
        let extra = |state: &State| public_clock_effect_kpr_value_function(state, 0) - public_clock_effect_value_function(state, 0);
        assert_eq!(extra(&before), extra(&after));
    }

    #[test]
    fn a_turn_that_is_ending_counts_only_next_turn() {
        // Zweilous with no Energy, this turn's [D] unused, nothing showing next: 1 of 2 while the turn runs, 0 once
        // it can bring nothing more.
        let running = my_turn(vec![mon(CardId::B1156Zweilous)], Some(EnergyType::Darkness), None);
        assert_eq!(scores(&running), (0.0, 0.5));
        let ending: Vec<Box<dyn Fn(&mut State)>> = vec![
            Box::new(|state| state.end_turn_pending = true),
            Box::new(|state| state.attack_name_used_this_turn[0] = Some("Darkness Fang".to_string())),
            Box::new(|state| state.move_generation_stack.push((0, vec![SimpleAction::EndTurn]))),
            Box::new(|state| state.move_generation_stack.push((0, vec![SimpleAction::ResolvePokemonCheckup]))),
            Box::new(|state| state.move_generation_stack.push((0, vec![SimpleAction::FinishPokemonCheckup]))),
            Box::new(|state| {
                state.move_generation_stack.push((1, vec![SimpleAction::ResolveEndTurnEvolution { player: 1 }]))
            }),
            // A marker under another choice still counts: Kiawe's [EndTurn] under its attach choice, a paused Checkup
            // under a promotion.
            Box::new(|state| {
                state.move_generation_stack.push((0, vec![SimpleAction::EndTurn]));
                let attach = SimpleAction::Attach { attachments: vec![(2, EnergyType::Fire, 0)], is_turn_energy: false };
                state.move_generation_stack.push((0, vec![attach]));
            }),
            Box::new(|state| {
                state.move_generation_stack.push((0, vec![SimpleAction::FinishPokemonCheckup]));
                state.move_generation_stack.push((0, vec![SimpleAction::Promote { player: 0, in_play_idx: 1 }]));
            }),
        ];
        for mark in ending {
            let mut state = running.clone();
            mark(&mut state);
            assert_eq!(scores(&state), (0.0, 0.0));
        }
        // On the opponent's turn, a [D] left over in `current` is gone at the rotation: it doesn't count.
        let mut theirs = running.clone();
        theirs.current_player = 1;
        assert_eq!(scores(&theirs), (0.0, 0.0));
    }

    #[test]
    fn nothing_is_projected_during_setup() {
        let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        state.turn_count = 0;
        assert_eq!(scores(&state), (0.0, 0.0));
    }

    #[test]
    fn an_ability_used_this_turn_counts_only_for_next_turn() {
        // Hydreigon with no Energy, nothing in the Zone. Roar in Unison unused: two [D] this turn and two next,
        // 3 of 3.
        let mut state = my_turn(vec![mon(CardId::B1157Hydreigon)], None, None);
        assert_eq!(scores(&state), (0.0, 1.0));
        // Already used this turn: next turn's two only, 2 of 3.
        state.in_play_pokemon[0][0].as_mut().unwrap().ability_used = true;
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
    }

    #[test]
    fn an_ability_that_would_knock_the_active_out_is_not_counted() {
        // Roar in Unison does 30 to Hydreigon (150 HP). With 30 HP left and one [D] plus this turn's [D]: Roar would
        // knock it out, so 2 of 3.
        let hurt = |damage| mon(CardId::B1157Hydreigon).with_damage(damage);
        let state = my_turn(vec![hurt(120).with_energy(vec![EnergyType::Darkness])], Some(EnergyType::Darkness), None);
        assert_eq!(scores(&state), (1.0 / 3.0, 2.0 / 3.0));
        // With 60 HP left, this turn's Roar is fine but a second, next turn, would knock it out: 2 of 3. With 90
        // left, both: 3 of 3.
        assert_eq!(scores(&my_turn(vec![hurt(90)], None, None)), (0.0, 2.0 / 3.0));
        assert_eq!(scores(&my_turn(vec![hurt(60)], None, None)), (0.0, 1.0));
        // Combust does 20 to Flareon ex: with 20 HP left it isn't counted.
        let flareon = |remaining| {
            let mut state = opponents_turn(vec![mon(CardId::A3b009FlareonEx).with_remaining_hp(remaining)], None);
            state.discard_energies[0].push(EnergyType::Fire);
            scores(&state)
        };
        assert_eq!(flareon(20), (0.0, 0.0));
        assert_eq!(flareon(40), (0.0, 1.0 / 3.0));
        // Over two turns (Flareon ex to move), Combust takes each discarded [R] once and its 20s add up.
        let flareon_to_move = |remaining, discarded| {
            let mut state = my_turn(vec![mon(CardId::A3b009FlareonEx).with_remaining_hp(remaining)], None, None);
            state.discard_energies[0].extend(vec![EnergyType::Fire; discarded]);
            scores(&state)
        };
        assert_eq!(flareon_to_move(150, 1), (0.0, 1.0 / 3.0));
        assert_eq!(flareon_to_move(150, 2), (0.0, 2.0 / 3.0));
        assert_eq!(flareon_to_move(30, 2), (0.0, 1.0 / 3.0));
        // Combust attaches to its holder only: a benched Flareon ex gives the Active (Charmander, Ember [R]) nothing.
        let mut state = opponents_turn(vec![mon(CardId::A1033Charmander), mon(CardId::A3b009FlareonEx)], None);
        state.discard_energies[0].push(EnergyType::Fire);
        assert_eq!(scores(&state), (0.0, 0.0));
    }

    #[test]
    fn ice_maker_feeds_an_active_of_its_type_only() {
        // Suicune ex (Crystal Waltz, [W][W]) Active, Baxcalibur benched: next turn's [W] plus Ice Maker's [W].
        let state = opponents_turn(vec![mon(CardId::A4a020SuicuneEx), mon(CardId::B2a036Baxcalibur)], Some(EnergyType::Water));
        assert_eq!(scores(&state), (0.0, 1.0));
        // A Grass Active gets the Zone's Energy only.
        let state = opponents_turn(vec![mon(CardId::A1001Bulbasaur), mon(CardId::B2a036Baxcalibur)], Some(EnergyType::Grass));
        assert_eq!(scores(&state), (0.0, 0.5));
    }

    #[test]
    fn zone_abilities_held_by_the_active_feed_only_the_active() {
        // Leafeon ex (Forest Breath: from the Active Spot, a [G] to one of your [G] Pokémon; Solar Beam [G][C][C]) as
        // the Active: next turn's [G] and its own, 2 of 3. Benched behind a Bulbasaur (Vine Whip, [G][C]), it can't
        // use it: the Bulbasaur gets the Zone's [G] only, 1 of 2.
        let state = opponents_turn(vec![mon(CardId::A2a010LeafeonEx)], Some(EnergyType::Grass));
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
        let state = opponents_turn(vec![mon(CardId::A1001Bulbasaur), mon(CardId::A2a010LeafeonEx)], Some(EnergyType::Grass));
        assert_eq!(scores(&state), (0.0, 0.5));
        // Magneton (Volt Charge: a [L] to itself; Spinning Attack [L][C][C][C]) as the Active: 2 of 4. Benched, it
        // charges itself, not the Active.
        let state = opponents_turn(vec![mon(CardId::A1098Magneton)], Some(EnergyType::Lightning));
        assert_eq!(scores(&state), (0.0, 0.5));
        let state = opponents_turn(vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1098Magneton)], Some(EnergyType::Grass));
        assert_eq!(scores(&state), (0.0, 0.5));
    }

    #[test]
    fn discard_pile_sources_need_the_energy_there() {
        // Flareon ex (Fire Spin, [R][R][C]) holds Combust: an [R] from the discard pile, if there is one.
        let mut state = opponents_turn(vec![mon(CardId::A3b009FlareonEx)], Some(EnergyType::Fire));
        assert_eq!(scores(&state), (0.0, 1.0 / 3.0));
        state.discard_energies[0].push(EnergyType::Fire);
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
        // Dragonair's Dragon's Blessing, from the Bench, to a Dragon Active: Dratini (Ram, [W][L]) with a [L] in the
        // discard pile and a [W] coming from the Zone.
        let mut state =
            opponents_turn(vec![mon(CardId::A1183Dratini), mon(CardId::B4117Dragonair)], Some(EnergyType::Water));
        assert_eq!(scores(&state), (0.0, 0.5));
        state.discard_energies[0].push(EnergyType::Lightning);
        assert_eq!(scores(&state), (0.0, 1.0));
    }

    #[test]
    fn dragons_blessing_takes_each_discarded_energy_once_and_the_type_the_active_needs() {
        // Haxorus (Frenzied Blade, [F][M][C]) with no Energy, two Dragonair, one [F] in the discard pile, [M] showing
        // next: [M] and the one [F], 2 of 3 (the second Dragonair finds nothing).
        let mut state = opponents_turn(
            vec![mon(CardId::B2b056Haxorus), mon(CardId::B4117Dragonair), mon(CardId::B4117Dragonair)],
            Some(EnergyType::Metal),
        );
        state.discard_energies[0].push(EnergyType::Fighting);
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
        // Holding an [M], one Dragonair, discard pile [M, F], [M] next: the Blessing takes the [F] it's missing, not
        // the first discarded: 3 of 3.
        let mut state = opponents_turn(
            vec![with(CardId::B2b056Haxorus, EnergyType::Metal, 1), mon(CardId::B4117Dragonair)],
            Some(EnergyType::Metal),
        );
        state.discard_energies[0].extend([EnergyType::Metal, EnergyType::Fighting]);
        assert_eq!(scores(&state), (1.0 / 3.0, 1.0));
        // Only from the Bench, and only to a Dragon Active: a Dragonair Active (Draconic Whip, [C][C]) gets nothing
        // from its own Blessing, nor does a Bulbasaur with a Dragonair behind it.
        for mine in [vec![mon(CardId::B4117Dragonair)], vec![mon(CardId::A1001Bulbasaur), mon(CardId::B4117Dragonair)]] {
            let mut state = opponents_turn(mine, None);
            state.discard_energies[0].push(EnergyType::Grass);
            assert_eq!(scores(&state), (0.0, 0.0));
        }
        // The Energy taken, with one Dragonair and nothing else coming.
        let blessed = |active: PlayedCard, discard: Vec<EnergyType>| {
            let mut state = opponents_turn(vec![active.clone(), mon(CardId::B4117Dragonair)], None);
            state.discard_energies[0] = discard;
            projected_active_energy(&state, 0, &active, Horizon::ThroughNextTurn)
        };
        // Dratini (Ram, [W][L]): [L] and [W] help alike, so the one discarded first.
        let (l, w) = (EnergyType::Lightning, EnergyType::Water);
        assert_eq!(blessed(mon(CardId::A1183Dratini), vec![l, w]), vec![l]);
        assert_eq!(blessed(mon(CardId::A1183Dratini), vec![w, l]), vec![w]);
        // Ultra Necrozma ex (Photon Claw [C][C][C]; Shoegaze [P][P][M][M]) holding [M][M][P]: either leaves Photon
        // Claw paid, [P] pays Shoegaze too, so the total decides.
        let (m, p) = (EnergyType::Metal, EnergyType::Psychic);
        assert_eq!(blessed(mon(CardId::PA081UltraNecrozmaEx).with_energy(vec![m, m, p]), vec![m, p]), vec![p]);
    }

    #[test]
    fn a_turn_effect_blocking_zone_attaches_to_the_active_blocks_the_projection() {
        // "Can't attach Energy from the Zone to the Active" on player 0's next turn: neither the turn's [D] nor Roar
        // in Unison counts.
        let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        state.turn_count = 7;
        state.add_turn_effect(TurnEffect::NoEnergyFromZoneToActive, 0);
        state.turn_count = 6;
        assert_eq!(scores(&state), (0.0, 0.0));
        // Nor Ice Maker's [W], Forest Breath's [G] or Volt Charge's [L].
        for mine in [
            vec![mon(CardId::A4a020SuicuneEx), mon(CardId::B2a036Baxcalibur)],
            vec![mon(CardId::A2a010LeafeonEx)],
            vec![mon(CardId::A1098Magneton)],
        ] {
            let mut state = opponents_turn(mine, None);
            state.turn_count = 7;
            state.add_turn_effect(TurnEffect::NoEnergyFromZoneToActive, 0);
            state.turn_count = 6;
            assert_eq!(scores(&state), (0.0, 0.0));
        }
        // Player 0 to move on turn 5 with the block on turn 5 only: this turn's [D] and Roar don't count, next
        // turn's (turn 7) Roar does: 2 of 3.
        let mut state = my_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness), None);
        state.add_turn_effect(TurnEffect::NoEnergyFromZoneToActive, 0);
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
        // With the block on turn 7 instead: this turn's Roar counts, next turn's doesn't: 2 of 3.
        let mut state = my_turn(vec![mon(CardId::B1157Hydreigon)], None, Some(EnergyType::Darkness));
        state.turn_count = 7;
        state.add_turn_effect(TurnEffect::NoEnergyFromZoneToActive, 0);
        state.turn_count = 5;
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
    }

    #[test]
    fn the_kpr_evaluator_differs_from_k_by_the_active_score_and_the_clock() {
        let k = public_clock_effect_value_function;
        let kpr = public_clock_effect_kpr_value_function;
        // Player 0's empty Hydreigon v player 1's Bulbasaur. Player 0: readiness 0 to 1, +500; its win, k counts 3
        // turns of missing Energy and 1 to knock Bulbasaur out, kpr 1: +300. Player 1, to move, is read at its very
        // next attack, this turn: with this turn's Zone empty, its [G] next doesn't count yet.
        let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        state.energy_zone[1].next = Some(EnergyType::Grass);
        assert_eq!(kpr(&state, 0) - k(&state, 0), 800.0);
        // With this turn's [G], its Bulbasaur (Vine Whip, [G][C]) gains 1 of 2 (-250) and is one Energy closer in
        // its clock (-100).
        state.energy_zone[1].current = Some(EnergyType::Grass);
        assert_eq!(kpr(&state, 0) - k(&state, 0), 450.0);
        // Player 0 mid-turn, its own Active read through its next turn: Zweilous holding one [D], this turn's attach
        // made, [D] next, against a bare Bulbasaur with nothing coming. Ready by next turn: +250 (1 of 2 to 2 of 2)
        // and one Energy nearer its win (+100). Read only to its next attack (this turn) it would gain nothing.
        let mut state = my_turn(vec![with(CardId::B1156Zweilous, EnergyType::Darkness, 1)], None, Some(EnergyType::Darkness));
        state.energy_zone[1].next = None;
        assert_eq!(kpr(&state, 0) - k(&state, 0), 350.0);
    }

    #[test]
    fn the_clock_counts_the_active_threats_energy_at_its_next_attack() {
        // Player 0's Hydreigon: k counts its 3 missing Energy and 1 hit on Bulbasaur; kpr sees it ready next turn.
        let state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        assert_eq!(clocks(&state), (4.0, 1.0));
        // Only the Active is projected. Bonsly (Teary Attack 10, free) is the threat: 7 hits on Bulbasaur. A benched
        // Zweilous holding one [D] stays one short: projected, it would be ready with 40 and the clock would be 2.
        let state = opponents_turn(
            vec![mon(CardId::B3078Bonsly), with(CardId::B1156Zweilous, EnergyType::Darkness, 1)],
            Some(EnergyType::Darkness),
        );
        assert_eq!(clocks(&state), (7.0, 7.0));
    }

    /// Player 0's `mine` against player 1's Suicune ex (140 HP) alone, player 1 to move.
    fn against_suicune(mine: Vec<PlayedCard>, next: Option<EnergyType>) -> State {
        let mut state = opponents_turn(mine.clone(), next);
        state.set_board(mine, vec![mon(CardId::A4a020SuicuneEx)]);
        state
    }

    #[test]
    fn the_clock_never_gets_slower_for_the_projection() {
        // Deino (Headbutt [D], 20) Active with nothing, Mega Absol ex (Darkness Claw [D][D], 80) benched holding a
        // [D], [D] next. k: Absol, one Energy and 2 hits, 3. Projected, Deino is ready first and would be the threat:
        // 7 hits. kpr takes the faster, 3.
        let state = against_suicune(
            vec![mon(CardId::B1155Deino), with(CardId::B1151MegaAbsolEx, EnergyType::Darkness, 1)],
            Some(EnergyType::Darkness),
        );
        assert_eq!(clocks(&state), (3.0, 3.0));
        let projected_only = turns_until_opponent_wins_scan(
            &state,
            1,
            true,
            true,
            false,
            true,
            false,
            false,
            Some(Horizon::ThroughNextTurn),
        );
        assert_eq!(projected_only, 7.0);
    }

    #[test]
    fn the_clock_prices_the_damage_the_active_will_do_at_its_next_attack() {
        // Mega Lucario ex (Fighting Pulse [F][F], 90, +50 with an extra [F]) holding [F][F], [F] next: k prices 90,
        // 2 hits on Suicune ex; at its next attack it has the extra [F] and does 140: 1.
        let state = against_suicune(vec![with(CardId::B3081MegaLucarioEx, EnergyType::Fighting, 2)], Some(EnergyType::Fighting));
        assert_eq!(clocks(&state), (2.0, 1.0));
    }

    #[test]
    fn the_clock_projects_the_actives_evolution_forms_too() {
        // Koffing (Division, no damage) Active with nothing, Weezing (Sludge Bomb [D][D], 70) in player 0's hand, [D]
        // next. k: 2 Energy, 1 evolution and 1 hit on Bulbasaur, 4. kpr: next turn's [D] leaves 1 Energy, so 3.
        let mut state = opponents_turn(vec![mon(CardId::A1a049Koffing)], Some(EnergyType::Darkness));
        state.hands[0].push(get_card_by_enum(CardId::B3102Weezing));
        assert_eq!(clocks(&state), (4.0, 3.0));
        // And their damage: Electabuzz (Charge, no damage) holding [L][L][L], Electivire (Exciting Voltage [L][L], 40,
        // +80 with 2 extra [L]) in hand, [L] next. k: 1 evolution and 2 hits of 40, 3. kpr: with the fourth [L] it
        // does 120, 1 hit: 2.
        let mut state = opponents_turn(vec![with(CardId::A2056Electabuzz, EnergyType::Lightning, 3)], Some(EnergyType::Lightning));
        state.hands[0].push(get_card_by_enum(CardId::A2057Electivire));
        assert_eq!(clocks(&state), (3.0, 2.0));
    }

    #[test]
    fn kpr_reads_no_hidden_card() {
        // The projection and the scores read the board, the Energy Zones and the discard piles, all public. Player
        // 1 is to move with [G] next. Its Bulbasaur (Vine Whip, [G][C]) holds a [G], so it's ready next turn; an
        // Ivysaur (Razor Leaf, [G][C][C]) hidden in its hand or deck must not make that 2 of 3. Nor may a hidden
        // Baxcalibur add Ice Maker's [W] to its Suicune ex.
        let value = |active: PlayedCard, next: EnergyType, hidden: CardId, in_hand: bool| {
            let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
            state.in_play_pokemon[1][0] = Some(active);
            state.energy_zone[1].next = Some(next);
            let card = get_card_by_enum(hidden);
            if in_hand {
                state.hands[1].push(card);
            } else {
                state.decks[1].cards.push(card);
            }
            public_clock_effect_kpr_value_function(&state, 0)
        };
        let bulbasaur = || with(CardId::A1001Bulbasaur, EnergyType::Grass, 1);
        let suicune = || mon(CardId::A4a020SuicuneEx);
        for in_hand in [false, true] {
            assert_eq!(
                value(bulbasaur(), EnergyType::Grass, CardId::A1002Ivysaur, in_hand),
                value(bulbasaur(), EnergyType::Grass, CardId::A1053Squirtle, in_hand)
            );
            assert_eq!(
                value(suicune(), EnergyType::Water, CardId::B2a036Baxcalibur, in_hand),
                value(suicune(), EnergyType::Water, CardId::A1001Bulbasaur, in_hand)
            );
        }
    }
}
