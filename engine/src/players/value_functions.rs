// Collection of value functions for ExpectiMiniMaxPlayer
//
// Each value function evaluates a game state from a player's perspective
// and returns a score (higher is better for that player)

use log::trace;

use crate::actions::abilities::AbilityMechanic;
use crate::actions::attacks::{BenchDamageFilter, BenchSide, Mechanic};
use crate::actions::{Action, SimpleAction};
use crate::actions::{
    ability_mechanic_from_effect, get_in_play_ability_mechanic, has_any_in_play_ability, EFFECT_MECHANIC_MAP,
};
use crate::card_logic::get_highest_evolutions;
use crate::effects::{CardEffect, TurnEffect};
use crate::hooks::{
    energy_missing, get_counterattack_damage, get_retreat_cost_for_player, get_stage, permanent_tool_reduction,
    persistent_defender_damage, special_condition_blocks_attack_or_retreat, temporary_defender_reduction,
    to_playable_card, DamageModifierContext, DefenderHit,
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

/// The `koa` tier (players/mod.rs `KOA`, piloted like `kp`): `k`'s evaluator plus switch A of the opening-Active
/// candidate in the setup evaluation (registered Sept 26, `rl/results/opening_active_census_2026-09-26/REGISTRATION.md`).
/// Nothing outside turn 0 changes.
pub fn public_clock_effect_koa_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KOA)
}

/// The `kob` diagnostic: `koa` with switch B in place of A. Mixed rows only; not registered for adoption.
pub fn public_clock_effect_kob_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KOB)
}

/// The `kor` diagnostic: `koa` with switch R in place of A. Mixed rows only; not registered for adoption.
pub fn public_clock_effect_kor_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KOR)
}

/// The `kpf` tier (players/mod.rs `KPF`, piloted like `kp`; registered Sept 26, `rl/results/kpf_2026-09-26/REGISTRATION.md`):
/// `kpr`'s evaluator (part R, kpr's projection exactly as built, amendment 5 included) plus part F, the discard-Energy
/// credit ([`super::fuel_credit::fuel_credit`]).
pub fn public_clock_effect_kpf_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KPF)
}

/// The `kpg` diagnostic: `k`'s evaluator plus part F only. Never adopted.
pub fn public_clock_effect_kpg_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KPG)
}

/// The `kph` tier (players/mod.rs `KPH`, piloted like `kp`; registered Sept 27, `rl/results/kph_2026-09-27/REGISTRATION.md`):
/// kpg + R', kpf's projection with its two diagnosed faults fixed: A, each evolution step still to take counts as one
/// missing Energy in the projected readiness; B, the clock may give the Zone Energy to a benched Pokemon that can reach
/// the Active Spot by the retreat rule.
pub fn public_clock_effect_kph_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KPH)
}

/// The `kpha` diagnostic: kpf + fix A only.
pub fn public_clock_effect_kpha_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KPHA)
}

/// The `kphb` diagnostic: kpf + fix B only.
pub fn public_clock_effect_kphb_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KPHB)
}

/// The `koh` tier (players/mod.rs `KOH`, piloted like `kp`): kph's R' (kpr's projection R with fixes A and B) on the
/// composed pilot kog (kp + koa's switch A + kpg's F), as kph's registration section 2 has it once kog is in force
/// (kog passed its composition check on Sept 28).
pub fn public_clock_effect_koh_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KOH)
}

/// The `kog` pilot (players/mod.rs `KOG`, piloted like `kp`): `k`'s evaluator with koa's switch A (the opening-Active
/// term, read only in the setup evaluation) and kpg's part F (the discard-Energy credit, read only after setup), each
/// exactly as in its own code. The composition of two separately read candidates (Dustin, Sept 27), not a new one.
pub fn public_clock_effect_kog_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KOG)
}

/// The `kt` tier (players/mod.rs `KT`, piloted like `kp`; registered Sept 26, `rl/results/kt_2026-09-26/README.md`,
/// amendments 1 and 2): `kog`'s evaluator with Tools and temporary damage cuts priced by what they do. Switch 1: the
/// defender's temporary cuts and damage-cut Tools in the threat clock. Switch 2: the flat +10 for a Tool on the Active
/// is 0. Switch 3: damage back to the attacker in the holder's own side's clock. kog's switch A and F on; kq's, kd's,
/// kpr's and kph's features off. Re-issued on kog (amendment 2); before that, these codes were the switches on kp.
pub fn public_clock_effect_kt_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KT)
}

/// The `kta` code: `kt` with switch 1 only, on kog (read by the route its footprint fixes, amendment 2).
pub fn public_clock_effect_kta_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KTA)
}

/// The `ktb` diagnostic: `kt` with switch 2 only.
pub fn public_clock_effect_ktb_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KTB)
}

/// The `ktc` diagnostic: `kt` with switch 3 only.
pub fn public_clock_effect_ktc_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KTC)
}

/// The `km` code (players/mod.rs `KM`, piloted like `kp`): kta with switch N2, the attacker's lasting Stadium damage
/// bonus (Training Area, Arena of Antiquity) in kta's threat clock for both sides
/// (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, registered Sept 29; re-issued on kta by
/// Amendment 1, Sept 30). kta's call with [`EvalFeatures::KM`].
pub fn public_clock_effect_km_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KM)
}

/// The `kn` code (players/mod.rs `KN`, piloted like `kp`): km with switch N1, the opponent's Active Retreat Cost
/// counted in the score as the bot's own is (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, "Appendix.
/// Parked: N1"; built Sept 30, not registered). km's call with [`EvalFeatures::KN`].
pub fn public_clock_effect_kn_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KN)
}

/// The `kr` code (players/mod.rs `KR`, piloted like `kp`): km with switch C2, a benched threat pays its Active's way
/// out in km's clock, on both sides (`rl/results/kn_build_2026-09-30/TIMING.md`, C2; built Sept 30, not registered).
/// N1's static term is off. km's call with [`EvalFeatures::KR`].
pub fn public_clock_effect_kr_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KR)
}

/// The `kro` diagnostic: kr's C2 in the opponent's clock only (their threats, how soon they win), for attribution.
pub fn public_clock_effect_kro_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, EvalFeatures::KRO)
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
    /// koa (switch A), kob (switch B), kor (switch R): the opening-Active term in the setup evaluation
    /// ([`super::opening_class::opening_active_term`]). Read only while the opponent's setup is masked.
    opening_first_turn_active: bool,
    opening_bench_working: bool,
    opening_readiness: bool,
    /// kpf and kpg (part F): the discard-Energy credit for a side that can pull that Energy back
    /// ([`super::fuel_credit::fuel_credit`]), over the pile R's projection left when R is on.
    fuel_credit: bool,
    /// kt switch 1 (kt, kta): the defender's temporary damage cuts and damage-cut Tools in the threat clock
    /// ([`kt_clock_c2`]). Not combined with kq's, kd's or kpr's clock features: no player code sets them together.
    defender_cuts: bool,
    /// kt switch 2 (kt, ktb): the flat +10 for a Tool on the Active (`active_has_tool`) is 0; each Tool counts only
    /// through the terms that read what it does for its holder.
    tool_by_holder: bool,
    /// kt switch 3 (kt, ktc): damage back to the attacker (Rocky Helmet, `Counterattack`, `CounterattackDamage`) in
    /// the holder's own side's clock ([`kt_clocks`]).
    counter_damage: bool,
    /// kph fix A (kph, kpha): with R on, the projected readiness counts each evolution step still to take as one
    /// missing Energy ([`evolution_aware_online_score`]).
    evolution_steps: bool,
    /// kph fix B (kph, kphb): with R on, the clock may also give the side's Zone Energy to a benched Pokemon that can
    /// reach the Active Spot by the retreat rule ([`calculate_turns_until_opponent_wins_projected`]).
    zone_to_bench: bool,
    /// km switch N2 (km): each hit in kt's clock ([`kt_clock_c2`]) carries the attacker's lasting Stadium damage
    /// bonus ([`lasting_stadium_damage_bonus`]). Read only in kt's clock, so only with switch 1 or 3 on (km: switch 1).
    stadium_bonus_in_clock: bool,
    /// Switch N1 (kn): the opponent's Active Retreat Cost counts in the score, as the bot's own does, through the same
    /// extraction ([`get_active_retreat_cost`], the board cost) and the same weight. Read only after setup.
    opponent_retreat_cost: bool,
    /// Switch C2 (kr, kro): in kt's clock ([`kt_clock_c2`]), a benched threat candidate of the opponent's (the clock of
    /// how soon they win) first pays what their Active lacks to retreat ([`benched_retreat_shortfall`]).
    retreat_opponent_threat: bool,
    /// Switch C2 (kr): the same for the bot's own benched threats (the clock of how soon it wins).
    retreat_own_threat: bool,
}

impl EvalFeatures {
    const OFF: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: false,
        projected_readiness: false,
        opening_first_turn_active: false,
        opening_bench_working: false,
        opening_readiness: false,
        fuel_credit: false,
        defender_cuts: false,
        tool_by_holder: false,
        counter_damage: false,
        evolution_steps: false,
        zone_to_bench: false,
        stadium_bonus_in_clock: false,
        opponent_retreat_cost: false,
        retreat_opponent_threat: false,
        retreat_own_threat: false,
    };
    const KQ: EvalFeatures = EvalFeatures {
        next_attack_reduction: true,
        bench_attacker_weight: KQ_BENCH_ATTACKER_WEIGHT,
        defender_modifiers: false,
        projected_readiness: false,
        opening_first_turn_active: false,
        opening_bench_working: false,
        opening_readiness: false,
        fuel_credit: false,
        defender_cuts: false,
        tool_by_holder: false,
        counter_damage: false,
        evolution_steps: false,
        zone_to_bench: false,
        stadium_bonus_in_clock: false,
        opponent_retreat_cost: false,
        retreat_opponent_threat: false,
        retreat_own_threat: false,
    };
    const KD: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: true,
        projected_readiness: false,
        opening_first_turn_active: false,
        opening_bench_working: false,
        opening_readiness: false,
        fuel_credit: false,
        defender_cuts: false,
        tool_by_holder: false,
        counter_damage: false,
        evolution_steps: false,
        zone_to_bench: false,
        stadium_bonus_in_clock: false,
        opponent_retreat_cost: false,
        retreat_opponent_threat: false,
        retreat_own_threat: false,
    };
    const KPR: EvalFeatures = EvalFeatures {
        next_attack_reduction: false,
        bench_attacker_weight: 0.0,
        defender_modifiers: false,
        projected_readiness: true,
        opening_first_turn_active: false,
        opening_bench_working: false,
        opening_readiness: false,
        fuel_credit: false,
        defender_cuts: false,
        tool_by_holder: false,
        counter_damage: false,
        evolution_steps: false,
        zone_to_bench: false,
        stadium_bonus_in_clock: false,
        opponent_retreat_cost: false,
        retreat_opponent_threat: false,
        retreat_own_threat: false,
    };
    const KOA: EvalFeatures = EvalFeatures { opening_first_turn_active: true, ..EvalFeatures::OFF };
    const KOB: EvalFeatures = EvalFeatures { opening_bench_working: true, ..EvalFeatures::OFF };
    const KOR: EvalFeatures = EvalFeatures { opening_readiness: true, ..EvalFeatures::OFF };
    /// kpf: R (kpr's projection, exactly as kpr uses it) and F. With F off it is [`EvalFeatures::KPR`].
    const KPF: EvalFeatures = EvalFeatures { fuel_credit: true, ..EvalFeatures::KPR };
    /// kpg (diagnostic): F only.
    const KPG: EvalFeatures = EvalFeatures { fuel_credit: true, ..EvalFeatures::OFF };
    /// kph: kpg + R' (`rl/results/kph_2026-09-27/REGISTRATION.md`): kpf's parts R and F with fixes A and B. With A and
    /// B off it is [`EvalFeatures::KPF`]; with R off it is kpg (A and B act only on R's projection).
    const KPH: EvalFeatures = EvalFeatures { evolution_steps: true, zone_to_bench: true, ..EvalFeatures::KPF };
    /// kpha (diagnostic): kpf + fix A only.
    const KPHA: EvalFeatures = EvalFeatures { evolution_steps: true, ..EvalFeatures::KPF };
    /// kphb (diagnostic): kpf + fix B only.
    const KPHB: EvalFeatures = EvalFeatures { zone_to_bench: true, ..EvalFeatures::KPF };
    /// koh: kog + R' (kph's R' on the composed pilot, `rl/results/kph_2026-09-27/REGISTRATION.md` section 2): koa's
    /// switch A with kph's flags. With R' off (R, A and B) it is [`EvalFeatures::KOG`].
    const KOH: EvalFeatures = EvalFeatures { opening_first_turn_active: true, ..EvalFeatures::KPH };
    /// kog: koa's switch A and kpg's F together, each exactly as in its own code (Dustin, Sept 27: one pilot by a
    /// composition check, RUN5 "Rules").
    const KOG: EvalFeatures = EvalFeatures { opening_first_turn_active: true, fuel_credit: true, ..EvalFeatures::OFF };
    /// kt: switches 1, 2 and 3 on kog (`rl/results/kt_2026-09-26/README.md`, amendment 2: re-issued on kog, Sept 28;
    /// from ed81c8b to 233bced these codes were the switches on kp).
    const KT: EvalFeatures =
        EvalFeatures { defender_cuts: true, tool_by_holder: true, counter_damage: true, ..EvalFeatures::KOG };
    /// kta (the reserve-route candidate, or read by the ordinary rule at a footprint of 15% or more): switch 1 on kog.
    const KTA: EvalFeatures = EvalFeatures { defender_cuts: true, ..EvalFeatures::KOG };
    /// ktb (diagnostic): switch 2 on kog.
    const KTB: EvalFeatures = EvalFeatures { tool_by_holder: true, ..EvalFeatures::KOG };
    /// ktc (diagnostic): switch 3 on kog.
    const KTC: EvalFeatures = EvalFeatures { counter_damage: true, ..EvalFeatures::KOG };
    /// km: kta + N2 (Amendment 1, Sept 30: km re-issued on kta). With N2's flag off it is [`EvalFeatures::KTA`].
    const KM: EvalFeatures = EvalFeatures { stadium_bonus_in_clock: true, ..EvalFeatures::KTA };
    /// kn: km + N1 (the parked switch, built Sept 30). With N1's flag off it is [`EvalFeatures::KM`].
    const KN: EvalFeatures = EvalFeatures { opponent_retreat_cost: true, ..EvalFeatures::KM };
    /// kr: km + C2 on both sides (TIMING.md's C2, built Sept 30), N1's static term off. With C2's flags off it is
    /// [`EvalFeatures::KM`].
    const KR: EvalFeatures =
        EvalFeatures { retreat_opponent_threat: true, retreat_own_threat: true, ..EvalFeatures::KM };
    /// kro (diagnostic): km + C2 in the opponent's clock only.
    const KRO: EvalFeatures = EvalFeatures { retreat_opponent_threat: true, ..EvalFeatures::KM };

    /// Whether kt's clock ([`kt_clocks`]) replaces kp's.
    fn kt_clock(&self) -> bool {
        self.defender_cuts || self.counter_damage
    }

    fn any_opening_switch(&self) -> bool {
        self.opening_first_turn_active || self.opening_bench_working || self.opening_readiness
    }
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
        let setup_score = pokemon_value * params.pokemon_value
            + state.hands[myself].len() as f64 * params.hand_size
            - state.decks[myself].cards.len() as f64 * params.deck_size
            - get_active_retreat_cost(state, myself, public_eval) as f64 * params.active_retreat_cost
            + calculate_active_pokemon_online_score_ex(
                state,
                myself,
                false,
                false,
                false,
                features.projected_readiness.then_some(Horizon::ThroughNextTurn),
                features.evolution_steps,
            ) * params.active_pokemon_online_score
            + calculate_active_safety(state, myself) * params.active_safety
            + online * params.online_pokemon_count
            + distance * params.energy_distance_to_online;
        // koa, kob, kor: the opening-Active term. Every other tier skips it, so its setup score is untouched.
        return if features.any_opening_switch() {
            setup_score
                + super::opening_class::opening_active_term(
                    state,
                    myself,
                    features.opening_first_turn_active,
                    features.opening_bench_working,
                    features.opening_readiness,
                )
        } else {
            setup_score
        };
    }
    let opponent = (myself + 1) % 2;
    // kt, kta, ktc: both clocks come from kt's clock, which switch 3 couples. Every other tier computes its own.
    let kt_clocks = (clock_aware && features.kt_clock())
        .then(|| kt_clocks(state, myself, public_eval, effect_aware, reserve_aware, features));
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
            kt_clocks.map(|(mine, _)| mine),
            features.evolution_steps,
            features.zone_to_bench,
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
            kt_clocks.map(|(_, theirs)| theirs),
            features.evolution_steps,
            features.zone_to_bench,
        ),
    );
    // kt, ktb (switch 2): no flat term for a Tool on the Active.
    let active_has_tool_weight = if features.tool_by_holder { 0.0 } else { params.active_has_tool };
    // kn (N1): the opponent's Active Retreat Cost counts as the bot's own does. It sits where the one-sided term sat, in
    // the same position in the sum, so with the flag off the score is the same expression, added in the same order.
    let active_retreat_cost_term = if features.opponent_retreat_cost {
        (opp.active_retreat_cost - my.active_retreat_cost) * params.active_retreat_cost
    } else {
        (-my.active_retreat_cost) * params.active_retreat_cost
    };
    let score = (my.points - opp.points) * params.points
        + (my.pokemon_value - opp.pokemon_value) * params.pokemon_value
        + (my.hand_size - opp.hand_size) * params.hand_size
        + (opp.deck_size - my.deck_size) * params.deck_size
        + active_retreat_cost_term
        + (my.active_pokemon_online_score - opp.active_pokemon_online_score)
            * params.active_pokemon_online_score
        + (my.active_safety - opp.active_safety) * params.active_safety
        + (my.active_has_tool - opp.active_has_tool) * active_has_tool_weight
        + (my.is_winner - opp.is_winner) * params.is_winner
        + (my.turns_until_opponent_wins - opp.turns_until_opponent_wins)
            * params.turns_until_opponent_wins
        + (my.online_pokemon_count - opp.online_pokemon_count) * params.online_pokemon_count
        + (my.energy_distance_to_online - opp.energy_distance_to_online)
            * params.energy_distance_to_online
        + opp.discard_size * params.opponent_discard_size;
    trace!("parametric_value_function: {score} (params: {params:?}, my: {my:?}, opp: {opp:?})");
    // kpf, kpg: part F, the discard-Energy credit on each side, weighted as the Pokémon value it is part of. Over the
    // pile R's projection left (each side at its own horizon, as R reads it), or the whole pile with R off, so no
    // Energy counts twice. The opponent's side reads only its board. Every other tier skips it.
    let score = if features.fuel_credit {
        let rest = |side: usize, horizon: Horizon| -> Vec<EnergyType> {
            match (features.projected_readiness, state.maybe_get_active(side)) {
                (true, Some(active)) => projected_active_energy_and_discard(state, side, active, horizon).1,
                _ => state.discard_energies[side].clone(),
            }
        };
        let my_fuel = super::fuel_credit::fuel_credit(state, myself, true, &rest(myself, Horizon::ThroughNextTurn));
        let opp_fuel = super::fuel_credit::fuel_credit(state, opponent, false, &rest(opponent, Horizon::NextAttack));
        score + (my_fuel - opp_fuel) * params.pokemon_value
    } else {
        score
    };
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
    clock: Option<f64>,
    evolution_steps: bool,
    zone_to_bench: bool,
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
    let active_pokemon_online_score = calculate_active_pokemon_online_score_ex(
        state,
        player,
        public_only,
        effect_aware,
        reserve_aware,
        own_projection,
        evolution_steps,
    );
    let active_safety = calculate_active_safety(state, player);
    let active_has_tool = get_active_has_tool(state, player);
    let is_winner = check_is_winner(state, player);
    // §115: in the d path the threat scan is evolution-aware. `public_only` doubles as the
    // zone-read permission: it is true exactly when `player` is the OPPONENT of the
    // evaluating player, i.e. when the side being SCANNED for threats ((player+1)%2) is the
    // evaluating player themselves — whose deck and hand they may legitimately see.
    // `clock`: kt's clock for this side, computed with the other side's (see `kt_clocks`).
    let turns_until_opponent_wins = if let Some(turns) = clock {
        turns
    } else if clock_aware {
        calculate_turns_until_opponent_wins_projected(
            state,
            player,
            public_only,
            effect_aware,
            reserve_aware,
            public_evaluation,
            next_attack_reduction,
            defender_modifiers,
            threat_projection,
            zone_to_bench,
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
// The kpr/kpf readings through kph's versions with its fixes off; the tests call them directly.
#[cfg_attr(not(test), allow(dead_code))]
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
    calculate_turns_until_opponent_wins_projected(
        state,
        player,
        read_scanned_zones,
        effect_aware,
        reserve_aware,
        consume_bench,
        next_attack_reduction,
        defender_modifiers,
        projected_readiness,
        false,
    )
}

/// [`calculate_turns_until_opponent_wins_damage_aware`] with kph's fix B (`zone_to_bench`): with a horizon, the clock
/// is also the smallest over the threatening side's benched Pokemon s of the clock with s given the side's Zone Energy
/// only ([`projected_zone_energy`]), when the side's Active can retreat into s ([`bench_can_reach_active`]). So it is
/// never slower than kpr's, and equal to it with an empty Bench.
#[allow(clippy::too_many_arguments)]
fn calculate_turns_until_opponent_wins_projected(
    state: &State,
    player: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    next_attack_reduction: bool,
    defender_modifiers: bool,
    projected_readiness: Option<Horizon>,
    zone_to_bench: bool,
) -> f64 {
    let clock = |projection| {
        turns_until_opponent_wins_scan_projected(
            state,
            player,
            read_scanned_zones,
            effect_aware,
            reserve_aware,
            consume_bench,
            next_attack_reduction,
            defender_modifiers,
            projection,
        )
    };
    match projected_readiness {
        Some(horizon) => {
            let kpr = clock(None).min(clock(Some(Projection::active(horizon))));
            let owner = (player + 1) % 2;
            if !zone_to_bench || !bench_can_reach_active(state, owner, horizon) {
                return kpr;
            }
            state
                .enumerate_bench_pokemon(owner)
                .map(|(slot, _)| Projection { horizon, slot, zone_only: true })
                .fold(kpr, |best, projection| best.min(clock(Some(projection))))
        }
        None => clock(None),
    }
}

/// The body of [`calculate_turns_until_opponent_wins_damage_aware`], with the threatening Active projected over
/// `projected_readiness`'s horizon when it is set.
#[allow(clippy::too_many_arguments)]
// The kpr/kpf readings through kph's versions with its fixes off; the tests call them directly.
#[cfg_attr(not(test), allow(dead_code))]
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
    turns_until_opponent_wins_scan_projected(
        state,
        player,
        read_scanned_zones,
        effect_aware,
        reserve_aware,
        consume_bench,
        next_attack_reduction,
        defender_modifiers,
        projected_readiness.map(Projection::active),
    )
}

/// [`turns_until_opponent_wins_scan`] with the threatening side's Pokemon in `projection`'s slot projected.
#[allow(clippy::too_many_arguments)]
fn turns_until_opponent_wins_scan_projected(
    state: &State,
    player: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    next_attack_reduction: bool,
    defender_modifiers: bool,
    projection: Option<Projection>,
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
    let candidates = threat_candidates(state, opponent, read_scanned_zones, projection, &attack_damage);
    let Some(threat) = candidates.iter().min_by_key(|c| (c.missing, u32::MAX - c.damage)) else {
        return 30.0; // No pokemon can deal damage, now or via any available evolution
    };
    let (max_damage, missing_energy, _threat_slot) = (threat.damage as f64, threat.missing, threat.slot);

    let mut total_turns = 0.0;
    let mut opp_points = state.points[opponent];

    total_turns += missing_energy as f64;
    total_turns += status_clock_turns(state, opponent, _threat_slot);

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

/// km (N2): the damage bonus a lasting Stadium adds to an attack by a Pokemon of `attacker_stage` and `attacker_types`
/// against the opponent's Active, through the engine's own Stadium bonus functions, as `hooks::modify_damage`'s Stadium
/// branch makes them for an active-to-active attack: Training Area +10 for a Stage 1 attacker, Arena of Antiquity +20
/// for an [F] attacker against an ex (the most over the attacker's types). Read-only. It returns 0 first thing with no
/// Stadium in play. The pin test (`km_tests`) ties it to `modify_damage`.
fn lasting_stadium_damage_bonus(state: &State, attacker_stage: u8, attacker_types: &[EnergyType], target_is_ex: bool) -> u32 {
    if state.active_stadium.is_none() {
        return 0;
    }
    let training_area = crate::stadiums::get_training_area_damage_bonus(state, attacker_stage);
    let arena_of_antiquity = attacker_types
        .iter()
        .map(|energy_type| crate::stadiums::get_arena_of_antiquity_damage_bonus(state, *energy_type, target_is_ex))
        .max()
        .unwrap_or(0);
    training_area + arena_of_antiquity
}

/// km (N2): the stage and types of the Pokemon that makes `threat`: `owner`'s Pokemon in the threat's slot, or its
/// evolution form when the threat is one (forms are scanned only for the evaluating player's own threats, so no hidden
/// zone of the opponent is read). `None` if the slot is empty.
fn threat_attacker_stage_and_types(state: &State, owner: usize, threat: &ThreatCandidate) -> Option<(u8, Vec<EnergyType>)> {
    let pokemon = state.in_play_pokemon[owner][threat.slot].as_ref()?;
    match threat.form {
        None => Some((get_stage(pokemon), state.pokemon_energy_types(pokemon))),
        Some(form) => {
            let mut evolved = pokemon.clone();
            evolved.card = evolution_targets(state, owner, pokemon).into_iter().nth(form)?;
            Some((get_stage(&evolved), state.pokemon_energy_types(&evolved)))
        }
    }
}

/// Every attack `owner` could threaten with, in scan order: each in-play Pokemon's damaging attacks, then (with
/// `read_scanned_zones`) those of its highest evolutions in `owner`'s deck or hand, one missing Energy per step.
/// `projection` counts one Pokemon as it will stand at its next attack: kpr's Active ([`at_next_attack`]), or kph's
/// benched Pokemon with the Zone Energy only. The damage-aware clock's threat is the first with the fewest missing
/// Energy, then the most damage. kp's clock and kt's read the same list.
fn threat_candidates(
    state: &State,
    owner: usize,
    read_scanned_zones: bool,
    projection: Option<Projection>,
    attack_damage: &dyn Fn(&Attack, &PlayedCard) -> u32,
) -> Vec<ThreatCandidate> {
    let mut candidates: Vec<ThreatCandidate> = Vec::new();
    for (slot, pokemon) in state.enumerate_in_play_pokemon(owner) {
        // kpr: the Active's missing Energy and damage are counted as it will stand at its next attack
        // ([`at_next_attack`]); kph's fix B: a benched Pokemon's with the Zone Energy ([`projected_zone_energy`]).
        let projected;
        let charged: &PlayedCard = match projection {
            Some(p) if slot == p.slot && p.zone_only => {
                let mut zone_fed = pokemon.clone();
                zone_fed.attached_energy.extend(projected_zone_energy(state, owner, p.horizon));
                projected = zone_fed;
                &projected
            }
            Some(p) if slot == p.slot => {
                projected = at_next_attack(state, owner, pokemon, p.horizon);
                &projected
            }
            _ => pokemon,
        };
        for (attack, atk) in pokemon.card.get_attacks().iter().enumerate() {
            let damage = attack_damage(atk, charged);
            if damage == 0 {
                continue;
            }
            let missing = energy_missing(charged, &atk.energy_required, state, owner).len();
            candidates.push(ThreatCandidate { slot, damage, missing, form: None, attack });
        }
        if read_scanned_zones {
            if let Card::Pokemon(current) = &pokemon.card {
                for (form, target) in evolution_targets(state, owner, pokemon).into_iter().enumerate() {
                    let Card::Pokemon(t) = &target else { continue };
                    let steps = t.stage.saturating_sub(current.stage) as usize;
                    if steps == 0 {
                        continue;
                    }
                    for (attack, atk) in target.get_attacks().iter().enumerate() {
                        let damage = attack_damage(atk, charged);
                        if damage > 0 {
                            let missing = energy_missing(charged, &atk.energy_required, state, owner).len() + steps;
                            candidates.push(ThreatCandidate { slot, damage, missing, form: Some(form), attack });
                        }
                    }
                }
            }
        }
    }
    candidates
}

/// B2b diagnostic, only in builds with the `status-clock` feature: a threat in the Active Spot that is Asleep misses
/// its next attack half the time (the checkup coin), and one that is Paralyzed misses it. 0 in every other build.
#[allow(unused_variables)]
fn status_clock_turns(state: &State, owner: usize, threat_slot: usize) -> f64 {
    #[cfg(feature = "status-clock")]
    if threat_slot == 0 {
        if let Some(threat) = state.maybe_get_active(owner) {
            if threat.has_status(StatusCondition::Paralyzed) {
                return 1.0;
            } else if threat.has_status(StatusCondition::Asleep) {
                return 0.5;
            }
        }
    }
    0.0
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

/// kt's damage-aware clock for one side: how soon `victim_owner`'s opponent wins. It is kp's clock
/// ([`turns_until_opponent_wins_scan`] as kp runs it: kq's, kd's and kpr's features off) with two changes, each behind
/// its own switch (`rl/results/kt_2026-09-26/README.md`):
/// - switch 1 (`cuts`): each victim's hits go through its damage cuts. f is the turn the clock already puts the threat's
///   first hit on ([`first_attack_turn_number`] from the threat's missing count, whatever its slot). The first hit of
///   the clock does `damage - temporary - permanent` (floored at 0), where temporary is
///   [`temporary_defender_reduction`] for turn f; every other hit does `damage - permanent`, per victim
///   ([`permanent_tool_reduction`]). A victim nothing more can damage makes the clock 30 ("never").
/// - switch 3 reads the parts: the Active victim's HP and hits, and the threat's slot ([`kt_clocks`]).
///
/// With `cuts` off and no counter cut, [`KtClock::total`] is kp's clock exactly (pinned by a test on played states).
///
/// km's switch N2 (`stadium_bonus`; Amendment 1 of km's registration, Sept 30): each hit on each victim also carries
/// the lasting Stadium damage bonus the threat's attacker gets against it ([`lasting_stadium_damage_bonus`], for the
/// attacker [`threat_attacker_stage_and_types`] reads), in the order `hooks::modify_damage` applies them: the bonus is
/// added to the attack's damage before Weakness, and the defender's cuts (switch 1) come off after, floored at 0. So a
/// hit is `(damage + bonus) - cuts`. The threat is still picked on unbonused damage. With no Training Area or Arena of
/// Antiquity in play the bonus is 0 and the arithmetic is kt's; every code but km runs it with N2 off.
///
/// C2 (`retreat_in`; kr on both sides, kro in the opponent's clock only; `rl/results/kn_build_2026-09-30/TIMING.md`):
/// before the threat is picked, each benched candidate's missing Energy also counts what its side's Active lacks to
/// retreat ([`benched_retreat_shortfall`]), so a benched threat pays its Active's way out. The Active's own candidates
/// are unchanged. With `retreat_in` off the arithmetic is km's; every code but kr and kro runs it off.
#[allow(clippy::too_many_arguments)]
fn kt_clock_c2(
    state: &State,
    victim_owner: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    cuts: bool,
    stadium_bonus: bool,
    retreat_in: bool,
) -> KtClock {
    let owner = (victim_owner + 1) % 2;
    let attack_damage = |atk: &Attack, slot: &PlayedCard| -> u32 {
        if effect_aware {
            estimated_attack_damage_ex(atk, slot, state, owner, reserve_aware).round() as u32
        } else {
            atk.fixed_damage
        }
    };
    let mut candidates = threat_candidates(state, owner, read_scanned_zones, None, &attack_damage);
    // C2 (kr, kro): a benched candidate first pays what its side's Active lacks to retreat. Off, nothing changes.
    if retreat_in {
        for candidate in candidates.iter_mut().filter(|c| c.slot != 0) {
            candidate.missing += benched_retreat_shortfall(state, owner, candidate.missing);
        }
    }
    let Some(threat) = candidates.iter().min_by_key(|c| (c.missing, u32::MAX - c.damage)).copied() else {
        return KtClock { lead: 30.0, active: None, rest: 0.0, threat_slot: None };
    };
    let lead = threat.missing as f64 + status_clock_turns(state, owner, threat.slot);
    // Switch 1: the threat as it attacks (its form and attack) and f, its first attack turn.
    let cuts = cuts.then(|| {
        let (attacker, attack) = kd_attacker(state, owner, &threat, &mut None);
        let (next_turn, attach_next) = owner_next_turn(state, owner);
        let (f, _) = first_attack_turn_number(next_turn, attach_next, threat.missing);
        (attacker, attack, f)
    });
    // km (N2): the threat's attacker's stage and types, read only with the flag on and a Stadium in play.
    let stadium_attacker = (stadium_bonus && state.active_stadium.is_some())
        .then(|| threat_attacker_stage_and_types(state, owner, &threat))
        .flatten();
    // The threat's damage against `victim`, with N2's bonus when it has one; the threat's damage otherwise.
    let damage_on = |victim: &PlayedCard| -> u32 {
        match &stadium_attacker {
            Some((stage, types)) => {
                threat.damage + lasting_stadium_damage_bonus(state, *stage, types, victim.card.is_ex())
            }
            None => threat.damage,
        }
    };
    // (the damage of `victim`'s first hit, of every later hit); `first` when it takes the clock's first hit.
    let hits_on = |victim: &PlayedCard, first: bool| -> (f64, f64) {
        let damage = damage_on(victim);
        let Some((attacker, attack, f)) = &cuts else {
            return (damage as f64, damage as f64);
        };
        let context = DamageModifierContext { attack_name: Some(&attack.title), attack_effect: attack.effect.as_deref() };
        let permanent = permanent_tool_reduction(state, victim_owner, victim, context);
        let temporary =
            if first { temporary_defender_reduction(state, victim_owner, victim, attacker, context, *f) } else { 0 };
        (
            damage.saturating_sub(permanent.saturating_add(temporary)) as f64,
            damage.saturating_sub(permanent) as f64,
        )
    };
    let mut opp_points = state.points[owner];
    let active = state.maybe_get_active(victim_owner).map(|victim| {
        let (first, later) = hits_on(victim, true);
        opp_points += victim.card.get_knockout_points();
        (victim.get_remaining_hp() as f64, first, later)
    });
    // The benched victims, as kp's clock picks them.
    let mut first_pending = active.is_none();
    let mut rest = 0.0;
    let mut counted_slots = [false; 4];
    while opp_points < 3 {
        let safest_bench = state
            .enumerate_bench_pokemon(victim_owner)
            .filter(|(slot, _)| !consume_bench || !counted_slots[*slot])
            .max_by_key(|(_, card)| {
                if opp_points == 2 {
                    card.get_remaining_hp()
                } else {
                    let ko_points = card.card.get_knockout_points().max(1) as u32;
                    card.get_remaining_hp() * 1000 / ko_points
                }
            });
        let Some((slot, victim)) = safest_bench else {
            break;
        };
        if consume_bench {
            counted_slots[slot] = true;
        }
        let (first, later) = hits_on(victim, first_pending);
        first_pending = false;
        rest += kt_hits(victim.get_remaining_hp() as f64, first, later);
        opp_points += victim.card.get_knockout_points();
    }
    KtClock { lead, active, rest, threat_slot: Some(threat.slot) }
}

/// [`kt_clock_c2`] with C2 off, as km's and kt's tests call it positionally.
#[cfg(test)]
#[allow(clippy::too_many_arguments)]
fn kt_clock_stadium(
    state: &State,
    victim_owner: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    cuts: bool,
    stadium_bonus: bool,
) -> KtClock {
    kt_clock_c2(state, victim_owner, read_scanned_zones, effect_aware, reserve_aware, consume_bench, cuts, stadium_bonus, false)
}

/// C2 (kr, kro; `rl/results/kn_build_2026-09-30/TIMING.md`): what `owner`'s Active still lacks to retreat, charged to a
/// benched threat candidate of `owner`'s with `missing` Energy to go: max(0, the Active's board Retreat Cost - the
/// Energy attached to it). The turn's attachment goes either to the retreat or to the attacker, as in kq's escape
/// (`retreat_cost + short <= attached + attach_next`).
/// - The cost is the engine's own board cost ([`crate::hooks::get_board_retreat_cost_for_player`]: Tools, Stadiums,
///   Abilities such as Trap Territory and Villainous Delivery, the stored effects; not this turn's discounts).
/// - A stored `IncreasedRetreatCost` (Goo-zooka's) counts only if it is live on the turn the threat would otherwise
///   attack: [`first_attack_turn_number`] for `missing` plus the shortfall without such effects, an effect with d turns
///   left being live through turn t + d, as switch 1 reads a temporary cut for turn f.
/// - An Active that can't retreat at all (a Special Condition that blocks it, `NoRetreat`) gets no charge: left as km's
///   clock has it, a stated limit. (A fossil Active's board cost is 0, so it gets none either.)
fn benched_retreat_shortfall(state: &State, owner: usize, missing: usize) -> usize {
    let Some(active) = state.maybe_get_active(owner) else {
        return 0;
    };
    if special_condition_blocks_attack_or_retreat(active) || active.get_active_effects().contains(&CardEffect::NoRetreat) {
        return 0;
    }
    // The Active's board cost with the stored IncreasedRetreatCost effects live through `turn` only (none for `None`),
    // by the engine's arithmetic on a copy whose stored effects are rebuilt without the others. The board cost reads no
    // Special Condition, so clearing them on the copy changes nothing else.
    let cost_through = |turn: Option<u32>| -> usize {
        let mut card = active.clone();
        card.clear_status_and_effects();
        for (effect, turns_left) in active.get_effects() {
            let live = turn.is_some_and(|f| f <= state.turn_count as u32 + *turns_left as u32);
            if !matches!(effect, CardEffect::IncreasedRetreatCost { .. }) || live {
                card.add_effect(effect.clone(), *turns_left);
            }
        }
        crate::hooks::get_board_retreat_cost_for_player(state, owner, &card).len()
    };
    let energy = active.attached_energy.len();
    let (next_turn, attach_next) = owner_next_turn(state, owner);
    let (turn, _) = first_attack_turn_number(next_turn, attach_next, missing + cost_through(None).saturating_sub(energy));
    cost_through(Some(turn)).saturating_sub(energy)
}

/// [`kt_clock_stadium`] with km's N2 off, as kt's tests call it positionally.
#[cfg(test)]
fn kt_clock(
    state: &State,
    victim_owner: usize,
    read_scanned_zones: bool,
    effect_aware: bool,
    reserve_aware: bool,
    consume_bench: bool,
    cuts: bool,
) -> KtClock {
    kt_clock_stadium(state, victim_owner, read_scanned_zones, effect_aware, reserve_aware, consume_bench, cuts, false)
}

/// One side's clock from [`kt_clock_c2`], in the parts switch 3 reads.
#[derive(Debug, Clone, Copy)]
struct KtClock {
    /// The turns before the threat's first hit (its missing Energy); 30 when nothing threatens.
    lead: f64,
    /// The victim owner's Active, the clock's first victim: (remaining HP, first hit's damage, every later hit's).
    /// `None` without an Active.
    active: Option<(f64, f64, f64)>,
    /// The turns for the benched victims after it.
    rest: f64,
    /// The threat's slot; `None` when nothing threatens.
    threat_slot: Option<usize>,
}

impl KtClock {
    /// Hits to knock out the Active victim with `cut` taken off its HP (switch 3); `None` without one.
    fn active_hits(&self, cut: f64) -> Option<f64> {
        self.active.map(|(hp, first, later)| kt_hits((hp - cut).max(0.0), first, later))
    }

    /// The clock, with `cut` taken off the Active victim's HP; 30 ("never") when nothing threatens or a victim can't
    /// be knocked out.
    fn total(&self, cut: f64) -> f64 {
        if self.threat_slot.is_none() {
            return 30.0;
        }
        let total = self.lead + self.active_hits(cut).unwrap_or(0.0) + self.rest;
        if total.is_finite() {
            total
        } else {
            30.0
        }
    }
}

/// kt: hits to knock out `hp` when the first does `first` and every later one `later`. kp's `ceil(hp / damage)` when
/// they are equal; infinite when nothing after the first can knock it out.
fn kt_hits(hp: f64, first: f64, later: f64) -> f64 {
    if hp <= 0.0 {
        0.0
    } else if first == later {
        (hp / later).ceil()
    } else {
        ko_turns_after_first_attack(hp, first, later)
    }
}

/// kt, kta, ktc, km: both sides' clocks, (turns until `myself`'s opponent wins, turns until `myself` wins), with the zone
/// reads and victim counting kp gives each side. Switch 3 (`counter_damage`) then takes the counter-damage of each
/// side's Active off the other side's Active in the holder's own clock ([`counter_cut`]); each clock reads the
/// other's hit count on its Active once, without the cut.
fn kt_clocks(
    state: &State,
    myself: usize,
    public_eval: bool,
    effect_aware: bool,
    reserve_aware: bool,
    features: EvalFeatures,
) -> (f64, f64) {
    let opponent = (myself + 1) % 2;
    let (cuts, n2) = (features.defender_cuts, features.stadium_bonus_in_clock);
    // C2 (kr, kro): `mine` is the opponent's threats (how soon they win), `theirs` the bot's own.
    let (c2_theirs, c2_mine) = (features.retreat_opponent_threat, features.retreat_own_threat);
    let mine = kt_clock_c2(state, myself, false, effect_aware, reserve_aware, public_eval, cuts, n2, c2_theirs);
    let theirs = kt_clock_c2(state, opponent, public_eval, effect_aware, reserve_aware, public_eval, cuts, n2, c2_mine);
    if !features.counter_damage {
        return (mine.total(0.0), theirs.total(0.0));
    }
    (mine.total(counter_cut(state, &mine, &theirs, opponent)), theirs.total(counter_cut(state, &theirs, &mine, myself)))
}

/// kt switch 3: the HP `holder_owner`'s clock (`ours`, on the other side's victims) takes off T, the other side's
/// Active, for the damage H, `holder_owner`'s Active, does back to its attacker (`get_counterattack_damage`: Rocky
/// Helmet, `Counterattack`, `CounterattackDamage`). c x k, where
/// - k = min(n_ours - 1 + s, n_theirs), the hits T lands on H before our knockout of T: n_ours is our clock's hit count
///   on T, n_theirs the other clock's (`theirs`) on H, both without the cut, and s = 1 if T's owner is to move (T
///   attacks first), else 0. The engine fires the counter on the knockout hit too, so T lands at most n_theirs.
/// - Only when T is the threat in the other side's clock and our clock's first victim. A Benched threat hasn't
///   attacked H yet, so its hits aren't counted. 0 when either count is infinite.
fn counter_cut(state: &State, ours: &KtClock, theirs: &KtClock, holder_owner: usize) -> f64 {
    let t_owner = (holder_owner + 1) % 2;
    if theirs.threat_slot != Some(0) {
        return 0.0;
    }
    let Some(holder) = state.maybe_get_active(holder_owner) else {
        return 0.0;
    };
    let c = get_counterattack_damage(state, holder);
    if c == 0 {
        return 0.0;
    }
    let (Some(n_ours), Some(n_theirs)) = (ours.active_hits(0.0), theirs.active_hits(0.0)) else {
        return 0.0;
    };
    if !(n_ours.is_finite() && n_theirs.is_finite()) {
        return 0.0;
    }
    let s = if owner_to_move_now(state, t_owner) { 1.0 } else { 0.0 };
    c as f64 * (n_ours - 1.0 + s).min(n_theirs).max(0.0)
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
    let (next_turn, attach_next) = owner_next_turn(state, owner);
    // The first attack turn, and how much Energy the Active can have had attached by then.
    let (first_attack, attachable) = first_attack_turn_number(next_turn, attach_next, fewest_missing);
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

/// Whether `owner` is to move now and can still attack this turn.
fn owner_to_move_now(state: &State, owner: usize) -> bool {
    state.current_player == owner && !state.end_turn_pending && state.attack_name_used_this_turn[owner].is_none()
}

/// The turn `owner` next attacks on (this one if it is to move and hasn't attacked), and the Energy it can attach
/// then: this turn's, if it is still in the Energy Zone.
fn owner_next_turn(state: &State, owner: usize) -> (u32, usize) {
    let t = state.turn_count as u32;
    let next_turn = if owner_to_move_now(state, owner) {
        t
    } else if state.current_player != owner {
        t + 1
    } else {
        t + 2
    };
    let attach_next = if next_turn == t { state.energy_zone[owner].current.is_some() as usize } else { 1 };
    (next_turn, attach_next)
}

/// The first attack turn of a Pokemon `missing` Energy short, and how much Energy it can have had attached by then:
/// one attach a turn, two global turns apart, from [`owner_next_turn`]'s turn. kq's [`first_attack_turn`] reads it
/// for the Active; kt's switch 1 for the clock's threat in any slot, with the clock's own missing count.
fn first_attack_turn_number(next_turn: u32, attach_next: usize, missing: usize) -> (u32, usize) {
    match missing {
        0 => (next_turn, attach_next),
        m if attach_next == 1 => (next_turn + 2 * (m as u32 - 1), m),
        m => (next_turn + 2 * m as u32, m),
    }
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
// The kpr/kpf readings through kph's versions with its fixes off; the tests call them directly.
#[cfg_attr(not(test), allow(dead_code))]
fn calculate_active_pokemon_online_score(
    state: &State,
    player: usize,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
    projected: Option<Horizon>,
) -> f64 {
    calculate_active_pokemon_online_score_ex(state, player, public_only, effect_aware, reserve_aware, projected, false)
}

/// [`calculate_active_pokemon_online_score`] with kph's fix A (`evolution_steps`) in the projected branch
/// ([`evolution_aware_online_score`]). Without a projection A changes nothing.
fn calculate_active_pokemon_online_score_ex(
    state: &State,
    player: usize,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
    projected: Option<Horizon>,
    evolution_steps: bool,
) -> f64 {
    let Some(active_pokemon) = state.maybe_get_active(player) else {
        return 0.0;
    };
    if let Some(horizon) = projected {
        let charged = at_next_attack(state, player, active_pokemon, horizon);
        if evolution_steps {
            return evolution_aware_online_score(
                state,
                player,
                active_pokemon,
                &charged,
                public_only,
                effect_aware,
                reserve_aware,
            );
        }
        return pokemon_online_score(state, player, &charged, public_only, effect_aware, reserve_aware);
    }
    pokemon_online_score(state, player, active_pokemon, public_only, effect_aware, reserve_aware)
}

/// kph's fix A: the projected readiness with each evolution step still to take counted as one missing Energy, the
/// clock's own rule (a step is a turn, the unit of missing Energy). `charged` is the Active as R projects it.
/// - `target` is the card [`pokemon_online_score`] measures against (the highest evolution in the owner's deck and
///   hand, or the card itself; on the opponent's side the card itself, so A never changes its reading), and
///   steps = target stage - the Active's stage (saturating).
/// - An attack costing nothing reads 1.0, as [`pokemon_online_score`] does.
/// - steps = 0: R's projected reading exactly.
/// - steps > 0: clamp((total - missing - steps) / total, 0, 1) on the projected Active, but never below the
///   unprojected reading (kp's).
fn evolution_aware_online_score(
    state: &State,
    player: usize,
    active: &PlayedCard,
    charged: &PlayedCard,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> f64 {
    let (target_stage, total, missing) =
        online_yardstick(state, player, charged, public_only, effect_aware, reserve_aware);
    if total == 0 {
        return 1.0;
    }
    let steps = match &active.card {
        Card::Pokemon(current) => target_stage.saturating_sub(current.stage),
        _ => 0,
    };
    if steps == 0 {
        return pokemon_online_score(state, player, charged, public_only, effect_aware, reserve_aware);
    }
    let projected = ((total as f64 - missing as f64 - steps as f64) / total as f64).clamp(0.0, 1.0);
    projected.max(pokemon_online_score(state, player, active, public_only, effect_aware, reserve_aware))
}

/// Which of the threatening side's Pokemon the clock projects, and how: kpr's projection of the Active
/// ([`Projection::active`]: [`at_next_attack`]), or kph's fix B, a benched `slot` given the Zone Energy only
/// ([`projected_zone_energy`]).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct Projection {
    horizon: Horizon,
    slot: usize,
    zone_only: bool,
}

impl Projection {
    fn active(horizon: Horizon) -> Projection {
        Projection { horizon, slot: 0, zone_only: false }
    }
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

/// kpr: whether the search would score `owner`'s EndTurn from here on the state before it. It does that when it can't
/// see the continuation (`observation::hidden_continuation_reason`), for example against an Active Caterpie whose
/// Quick Growth searches an unknown deck. Such a leaf is really past the turn, so the owner's own reading counts the
/// turn as over wherever that holds, mid-turn leaves included, and the two kinds of leaf read alike.
fn end_turn_scored_before_it(state: &State, owner: usize) -> bool {
    let end_turn = Action { actor: owner, action: SimpleAction::EndTurn, is_stack: false };
    crate::observation::hidden_continuation_reason(state, &end_turn).is_some()
}

/// kpr: the Energy `owner`'s Active will have been given by the end of `horizon`, from public sources its owner
/// controls.
///
/// Timing. The owner's turn is running if `owner` is to move and the turn isn't over ([`owner_turn_is_over`]); for
/// the own reading, also not where the search scores its EndTurn before it ([`end_turn_scored_before_it`]).
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
    projected_active_energy_and_discard(state, owner, active, horizon).0
}

/// [`projected_active_energy`], and `owner`'s discard-pile Energy it didn't use (kpf's part F counts only that).
fn projected_active_energy_and_discard(
    state: &State,
    owner: usize,
    active: &PlayedCard,
    horizon: Horizon,
) -> (Vec<EnergyType>, Vec<EnergyType>) {
    if state.turn_count == 0 {
        return (Vec::new(), state.discard_energies[owner].clone());
    }
    let turns = projection_turns(state, owner, horizon);

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
    (charged.attached_energy.split_off(before), discard)
}

/// kpr: the turns [`projected_active_energy`] reads for `owner` over `horizon`, each with whether it is the current
/// turn: this turn while `owner`'s turn is running (and, for [`Horizon::ThroughNextTurn`], next turn too), else next
/// turn only. Not for setup (turn 0), which projects nothing.
fn projection_turns(state: &State, owner: usize, horizon: Horizon) -> Vec<(u8, bool)> {
    let owner_to_move = state.current_player == owner;
    let running = owner_to_move
        && !owner_turn_is_over(state, owner)
        && !(horizon == Horizon::ThroughNextTurn && end_turn_scored_before_it(state, owner));
    let mut turns: Vec<(u8, bool)> = Vec::with_capacity(2);
    if running {
        turns.push((state.turn_count, true));
    }
    if !running || horizon == Horizon::ThroughNextTurn {
        turns.push((state.turn_count + if owner_to_move { 2 } else { 1 }, false));
    }
    turns
}

/// kph's fix B: the Energy a benched Pokemon of `owner`'s gets over `horizon`: exactly the Zone terms of
/// [`projected_active_energy`]'s turns (this turn's `current` if still unused, next turn's `next`), with the same
/// running test. No `NoEnergyFromZoneToActive` check (it blocks only the Active), no Ability and no discard-pile
/// Energy. Nothing during setup (turn 0).
fn projected_zone_energy(state: &State, owner: usize, horizon: Horizon) -> Vec<EnergyType> {
    if state.turn_count == 0 {
        return Vec::new();
    }
    projection_turns(state, owner, horizon)
        .into_iter()
        .filter_map(|(_, this_turn)| {
            if this_turn {
                state.energy_zone[owner].current
            } else {
                state.energy_zone[owner].next
            }
        })
        .collect()
}

/// kph's fix B: whether `owner`'s benched Pokemon can be in the Active Spot for its next attack over `horizon`, by the
/// game's retreat rule, read from the board (no Switch or X Speed in hand is assumed, so both sides are read alike):
/// - payment: the Active's board Retreat Cost (`get_board_retreat_cost_for_player`: without this turn's discounts such
///   as X Speed or Leaf) is at most the Energy attached to it (Retreat Costs are Colorless);
/// - not blocked: kq's retreat block (Asleep or Paralyzed, `NoRetreat`, a Fossil);
/// - when the attack is this turn (the turn list holds this turn only: `owner`'s turn is running and the horizon is
///   [`Horizon::NextAttack`]), no retreat already made this turn. For [`Horizon::ThroughNextTurn`] the attack can be
///   next turn, after a retreat then.
/// With no Active, the next one is promoted, so any benched Pokemon can be it.
fn bench_can_reach_active(state: &State, owner: usize, horizon: Horizon) -> bool {
    let Some(active) = state.maybe_get_active(owner) else {
        return true;
    };
    let cost = crate::hooks::get_board_retreat_cost_for_player(state, owner, active).len();
    let blocked = special_condition_blocks_attack_or_retreat(active)
        || active.get_active_effects().contains(&CardEffect::NoRetreat)
        || active.is_fossil();
    let turns = projection_turns(state, owner, horizon);
    let attack_this_turn = !turns.is_empty() && turns.iter().all(|(_, this_turn)| *this_turn);
    cost <= active.attached_energy.len() && !blocked && !(attack_this_turn && state.has_retreated)
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
    let (_, total, missing) = online_yardstick(state, player, active_pokemon, public_only, effect_aware, reserve_aware);
    if total == 0 {
        return 1.0; // No attack requirements, fully online
    }
    // Calculate how much energy we have vs need
    let total_needed = total as f64;
    let have = total_needed - missing as f64;

    // Return ratio (0.0 to 1.0)
    (have / total_needed).clamp(0.0, 1.0)
}

/// [`pokemon_online_score`]'s parts: the stage of the card it measures against (the highest evolution of
/// `active_pokemon` in `player`'s deck and hand, or the card itself), and its yardstick attack's cost and missing
/// Energy (0 and 0 when that card has no attack cost).
fn online_yardstick(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
    public_only: bool,
    effect_aware: bool,
    reserve_aware: bool,
) -> (u8, usize, usize) {
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

    let stage = match target_card {
        Card::Pokemon(pokemon) => pokemon.stage,
        _ => 0,
    };
    if yardstick_cost.is_empty() {
        return (stage, 0, 0);
    }
    let missing = energy_missing(active_pokemon, &yardstick_cost, state, player);
    (stage, yardstick_cost.len(), missing.len())
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
        after.queue_draw_action(1, 1); // as advance_turn leaves it: the turn's draw on the stack
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
        // A board that needs this turn's Zone: player 1's Mega Absol ex (Darkness Claw [D][D]) with no Energy and no
        // Ability source, [D] next. Before, next turn's [D]: 1 of 2. At the turn start (its draw on the stack), this
        // turn's [D]: 1 of 2 again.
        let mut before = before.clone();
        before.in_play_pokemon[1] = [Some(mon(CardId::B1151MegaAbsolEx)), None, None, None];
        before.energy_zone[1].next = Some(EnergyType::Darkness);
        let mut after = before.clone();
        after.turn_count = 6;
        after.current_player = 1;
        after.energy_zone[1].current = after.energy_zone[1].next.take();
        after.queue_draw_action(1, 1);
        let as_opponent = |state: &State| {
            calculate_active_pokemon_online_score(state, 1, true, true, false, Some(Horizon::NextAttack))
        };
        assert_eq!((as_opponent(&before), as_opponent(&after)), (0.5, 0.5));
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
    fn where_the_search_scores_end_turn_before_it_the_own_turn_counts_as_over() {
        // Player 1's Active is Caterpie (Quick Growth) and its deck is unknown, as in a search: the search scores
        // player 0's EndTurn on the state before it. Zweilous with no Energy, this turn's [D] unused, [D] next: the
        // own reading counts the turn as over, 1 of 2, on every leaf alike, so attaching before ending the turn keeps
        // its 250. With the deck known, the turn is running: 2 of 2.
        let mut state = my_turn(vec![mon(CardId::B1156Zweilous)], Some(EnergyType::Darkness), Some(EnergyType::Darkness));
        state.in_play_pokemon[1][0] = Some(mon(CardId::B3b001Caterpie));
        assert_eq!(scores(&state), (0.0, 1.0));
        state.decks[1].cards.push(Card::Unknown);
        assert_eq!(scores(&state), (0.0, 0.5));
        // Every search has the opponent's deck unknown; against an ordinary Active (a Bulbasaur) the EndTurn is played
        // out, and the turn runs: 2 of 2.
        let mut control = state.clone();
        control.in_play_pokemon[1][0] = Some(mon(CardId::A1001Bulbasaur));
        assert_eq!(scores(&control), (0.0, 1.0));
        // The reading at the next attack (the opponent's side) doesn't use it: holding one [D] with this turn's attach
        // made, it stays at this turn, 1 of 2.
        state.in_play_pokemon[0][0] = Some(with(CardId::B1156Zweilous, EnergyType::Darkness, 1));
        state.energy_zone[0].current = None;
        let as_opponent = calculate_active_pokemon_online_score(&state, 0, false, true, false, Some(Horizon::NextAttack));
        assert_eq!(as_opponent, 0.5);
    }

    #[test]
    fn nothing_is_projected_during_setup() {
        let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        state.turn_count = 0;
        assert_eq!(scores(&state), (0.0, 0.0));
        // From turn 1 on it is. Turn 1, player 0 to move with no Energy this turn (the first player's Zone is empty):
        // Zweilous gets next turn's [D], 1 of 2. Turn 2, with this turn's [D] and next turn's: 2 of 2.
        let mut state = my_turn(vec![mon(CardId::B1156Zweilous)], None, Some(EnergyType::Darkness));
        state.turn_count = 1;
        assert_eq!(scores(&state), (0.0, 0.5));
        state.turn_count = 2;
        state.energy_zone[0].current = Some(EnergyType::Darkness);
        assert_eq!(scores(&state), (0.0, 1.0));
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
    fn roar_in_unison_feeds_only_its_holder() {
        // Mega Absol ex (Darkness Claw [D][D]) Active with nothing, Hydreigon benched, [D] next: Roar attaches to the
        // Hydreigon, not the Active, which gets next turn's [D] only: 1 of 2.
        let state = opponents_turn(vec![mon(CardId::B1151MegaAbsolEx), mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
        assert_eq!(scores(&state), (0.0, 0.5));
    }

    #[test]
    fn ice_maker_works_from_the_active_and_from_each_baxcalibur() {
        // Baxcalibur (Buster Tail [W][W][W]) as the Active feeds itself: next turn's [W] and its own Ice Maker, 2 of 3.
        let state = opponents_turn(vec![mon(CardId::B2a036Baxcalibur)], Some(EnergyType::Water));
        assert_eq!(scores(&state), (0.0, 2.0 / 3.0));
        // Two Baxcalibur each attach one: Chien-Pao ex with no Energy, [W] next, reaches [W][W][W] for Diving Icicles
        // (130). Against Mega Lucario ex (190 HP): k counts Icicle, one Energy and 10 hits of 20; kpr 2 hits of 130.
        let mut state = opponents_turn(
            vec![mon(CardId::B2a037ChienPaoEx), mon(CardId::B2a036Baxcalibur), mon(CardId::B2a036Baxcalibur)],
            Some(EnergyType::Water),
        );
        state.set_board(state.in_play_pokemon[0].iter().flatten().cloned().collect(), vec![mon(CardId::B3081MegaLucarioEx)]);
        assert_eq!(clocks(&state), (11.0, 2.0));
        // A benched Baxcalibur that has used Ice Maker this turn feeds only next turn: Suicune ex (Crystal Waltz
        // [W][W]) to move, nothing in the Zone: 1 of 2.
        let mut baxcalibur = mon(CardId::B2a036Baxcalibur);
        baxcalibur.ability_used = true;
        let state = my_turn(vec![mon(CardId::A4a020SuicuneEx), baxcalibur], None, None);
        assert_eq!(scores(&state), (0.0, 0.5));
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
        // kph's fix B takes a further minimum, so it is never slower either. Deino holds nothing to pay its Retreat
        // Cost of 1, so its benched Absol isn't credited: 3, as kpr.
        let kph_clock = |state: &State| {
            calculate_turns_until_opponent_wins_projected(
                state,
                1,
                true,
                true,
                false,
                true,
                false,
                false,
                Some(Horizon::ThroughNextTurn),
                true,
            )
        };
        assert_eq!(kph_clock(&state), 3.0);
        // Deino holding a [D] is ready itself (Headbutt, 20: 7 hits for kpr, whose projection is the Active's), and can
        // retreat into Absol, which B gives next turn's [D]: ready, and 2 hits of 80 on Suicune ex.
        let state = against_suicune(
            vec![with(CardId::B1155Deino, EnergyType::Darkness, 1), with(CardId::B1151MegaAbsolEx, EnergyType::Darkness, 1)],
            Some(EnergyType::Darkness),
        );
        assert_eq!((clocks(&state).1, kph_clock(&state)), (7.0, 2.0));
        // With an empty Bench, B has no one to feed: kpr's clock.
        let state = against_suicune(vec![with(CardId::B1155Deino, EnergyType::Darkness, 1)], Some(EnergyType::Darkness));
        assert_eq!(kph_clock(&state), clocks(&state).1);
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
        // 1 is to move, read at its next attack (this turn), with a [G] in this turn's Zone. Its Bulbasaur (Vine Whip,
        // [G][C]) holds a [G], so it's ready this turn; an Ivysaur (Razor Leaf, [G][C][C]) hidden in its hand or deck
        // must not make that 2 of 3. Nor may a hidden Baxcalibur add Ice Maker's [W] to its Suicune ex.
        let value = |active: PlayedCard, current: EnergyType, hidden: CardId, in_hand: bool| {
            let mut state = opponents_turn(vec![mon(CardId::B1157Hydreigon)], Some(EnergyType::Darkness));
            state.in_play_pokemon[1][0] = Some(active);
            state.energy_zone[1].current = Some(current);
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

#[cfg(test)]
mod kpf_tests {
    use super::*;
    use crate::card_ids::CardId;

    /// A Rayquaza board on the evaluator's turn: Mega Rayquaza ex Active, Dragonair on the Bench (Dragon's Blessing
    /// unused), three [R] in the discard pile, against a Bulbasaur.
    fn rayquaza_board() -> State {
        let mut state = State::default();
        state.turn_count = 5;
        state.current_player = 0;
        state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::B4120MegaRayquazaEx));
        state.in_play_pokemon[0][1] = Some(PlayedCard::from_id(CardId::B4117Dragonair));
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
        state.discard_energies[0] = vec![EnergyType::Fire; 3];
        state.decks[0].cards.clear();
        state.decks[1].cards.clear();
        state
    }

    fn value(state: &State, features: EvalFeatures) -> f64 {
        parametric_value_function_ex6(state, 0, &ValueFunctionParams::baseline(), true, false, true, true, false, features)
    }

    /// kpf with F off is kpr; with R off it is kpg; with both off it is kp. Checked on the value, both seats.
    #[test]
    fn kpf_parts_switch_off_to_kpr_kpg_and_kp() {
        let mut boards = vec![rayquaza_board()];
        let mut other = rayquaza_board();
        other.current_player = 1;
        other.discard_energies[1] = vec![EnergyType::Grass; 2];
        boards.push(other);
        for state in &boards {
            let f_off = EvalFeatures { fuel_credit: false, ..EvalFeatures::KPF };
            let r_off = EvalFeatures { projected_readiness: false, ..EvalFeatures::KPF };
            let both_off = EvalFeatures { fuel_credit: false, projected_readiness: false, ..EvalFeatures::KPF };
            assert_eq!(value(state, f_off), public_clock_effect_kpr_value_function(state, 0));
            assert_eq!(value(state, r_off), public_clock_effect_kpg_value_function(state, 0));
            assert_eq!(value(state, both_off), public_clock_effect_value_function(state, 0));
        }
    }

    /// No double count: F counts only the discard-pile Energy R's projection didn't put on the Active. Here R's
    /// Dragon's Blessing takes [R] from the pile (this turn and next), so kpf's credit is on what is left; kpg, without
    /// R, credits the whole pile.
    #[test]
    fn f_counts_only_what_r_left_in_the_pile() {
        let state = rayquaza_board();
        let active = state.get_active(0);
        let (projected, left) = projected_active_energy_and_discard(&state, 0, active, Horizon::ThroughNextTurn);
        let from_pile = projected.iter().filter(|e| **e == EnergyType::Fire).count();
        assert!(from_pile >= 1, "Dragon's Blessing projects [R] from the pile: {projected:?}");
        assert_eq!(left.len(), 3 - from_pile);
        let kpf_credit = public_clock_effect_kpf_value_function(&state, 0) - public_clock_effect_kpr_value_function(&state, 0);
        let kpg_credit = public_clock_effect_kpg_value_function(&state, 0) - public_clock_effect_value_function(&state, 0);
        assert_eq!(kpf_credit, 15.0 * left.len() as f64);
        assert_eq!(kpg_credit, 45.0);
    }

    /// kpf on the opponent's side, with R on: R reads the opponent's Active at its next attack (NextAttack), and F
    /// counts the opponent's pile R left; kpg, without R, the whole pile.
    #[test]
    fn kpf_counts_the_opponents_pile_after_its_own_projection() {
        let mut state = rayquaza_board();
        state.discard_energies[0].clear();
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B4120MegaRayquazaEx));
        state.in_play_pokemon[1][1] = Some(PlayedCard::from_id(CardId::B4117Dragonair));
        state.discard_energies[1] = vec![EnergyType::Fire; 3];
        let (projected, left) =
            projected_active_energy_and_discard(&state, 1, state.get_active(1), Horizon::NextAttack);
        assert_eq!(projected.iter().filter(|e| **e == EnergyType::Fire).count(), 1, "one Blessing by its next attack");
        let kpf_credit = public_clock_effect_kpf_value_function(&state, 0) - public_clock_effect_kpr_value_function(&state, 0);
        let kpg_credit = public_clock_effect_kpg_value_function(&state, 0) - public_clock_effect_value_function(&state, 0);
        assert_eq!(kpf_credit, -15.0 * left.len() as f64);
        assert_eq!(kpf_credit, -30.0);
        assert_eq!(kpg_credit, -45.0);
    }

    /// The opponent's pile counts against the evaluator only through a source visible on its board.
    #[test]
    fn the_opponents_credit_needs_its_visible_source() {
        let mut state = rayquaza_board();
        state.discard_energies[0].clear();
        state.discard_energies[1] = vec![EnergyType::Fire; 2];
        let credit = |state: &State| public_clock_effect_kpg_value_function(state, 0) - public_clock_effect_value_function(state, 0);
        assert_eq!(credit(&state), 0.0, "Bulbasaur alone: no source");
        state.decks[1].cards.push(crate::database::get_card_by_enum(CardId::B4117Dragonair));
        assert_eq!(credit(&state), 0.0, "a Dragonair in the opponent's deck is never read");
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B4120MegaRayquazaEx));
        state.in_play_pokemon[1][1] = Some(PlayedCard::from_id(CardId::B4117Dragonair));
        assert_eq!(credit(&state), -30.0, "a Dragonair on the opponent's Bench: its two [R] count against the evaluator");
    }
}

#[cfg(test)]
mod kt_tests {
    //! kt (`rl/results/kt_2026-09-26/README.md`): switch 1's cuts in the clock, switch 2's flat term, switch 3's
    //! counter-damage, each on built positions; and kt's clock against kp's on played states.
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::effects::DamageReductionScope;
    use crate::players::RandomPlayer;
    use crate::{Deck, Game};

    /// The same switches on kp: `f` with kog's switch A and F off. From ed81c8b to 233bced the kt codes were these
    /// presets. Since amendment 2 (Sept 28) they are the switches on kog, and 43cef0b's tests read them this way.
    fn on_kp(f: EvalFeatures) -> EvalFeatures {
        EvalFeatures { opening_first_turn_active: false, fuel_credit: false, ..f }
    }

    /// `features`' value from `myself`'s view, evaluated as the public kt codes are.
    fn value(state: &State, myself: usize, features: EvalFeatures) -> f64 {
        parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, features)
    }

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

    fn tool(id: CardId) -> Card {
        get_card_by_enum(id)
    }

    /// Mewtwo ex with Psychic Sphere (50) paid for.
    fn mewtwo() -> PlayedCard {
        with(CardId::A1129MewtwoEx, EnergyType::Psychic, 2)
    }

    /// Turns until player 0's opponent wins: (kp's clock, kt's clock with switch 1).
    fn clocks(state: &State) -> (f64, f64) {
        let kp = turns_until_opponent_wins_scan(state, 0, false, true, false, true, false, false, None);
        let kt = kt_clock(state, 0, false, true, false, true, true).total(0.0);
        (kp, kt)
    }

    #[test]
    fn a_cut_live_on_the_threats_first_attack_turn_softens_the_first_hit() {
        // Snorlax at 100 HP against Mewtwo ex's 50, ready on its next turn (6): kp counts 2 hits. Stiffen's kind of
        // effect (-20, 1 turn left: live through turn 6) makes the first hit 30: 30 + 50 + 50, 3 hits.
        let mut snorlax = mon(CardId::B3b055Snorlax).with_remaining_hp(100);
        snorlax.add_effect(CardEffect::ReducedDamage { amount: 20 }, 1);
        assert_eq!(clocks(&board(vec![snorlax.clone()], vec![mewtwo()])), (2.0, 3.0));
        // Mewtwo ex 2 Energy short attacks on turn 8 at the earliest: the cut is gone by then.
        let unpowered = mon(CardId::A1129MewtwoEx);
        assert_eq!(clocks(&board(vec![snorlax], vec![unpowered])), (4.0, 4.0));
        // A turn effect for all the defender's Pokemon (Blue's kind), registered for turns 5 and 6: the same.
        let mut state = board(vec![mon(CardId::B3b055Snorlax).with_remaining_hp(100)], vec![mewtwo()]);
        let blue = TurnEffect::ReducedDamageForTarget {
            amount: 20,
            player: 0,
            scope: DamageReductionScope::AllPokemon,
            only_from_ex: false,
        };
        state.add_turn_effect(blue.clone(), 1);
        assert_eq!(clocks(&state), (2.0, 3.0));
        // Registered for turns 4 and 5 only: gone by the threat's turn 6.
        let mut state = board(vec![mon(CardId::B3b055Snorlax).with_remaining_hp(100)], vec![mewtwo()]);
        state.turn_count = 4;
        state.add_turn_effect(blue, 1);
        state.turn_count = 5;
        assert_eq!(clocks(&state), (2.0, 2.0));
        // Only the clock's first hit gets it: two Snorlax, the benched one is hit later and gets nothing.
        let mut state = board(
            vec![mon(CardId::B3b055Snorlax).with_remaining_hp(100), mon(CardId::B3b055Snorlax).with_remaining_hp(100)],
            vec![mewtwo()],
        );
        state.add_turn_effect(
            TurnEffect::ReducedDamageForTarget {
                amount: 20,
                player: 0,
                scope: DamageReductionScope::AllPokemon,
                only_from_ex: false,
            },
            1,
        );
        assert_eq!(clocks(&state), (4.0, 5.0));
    }

    #[test]
    fn metal_core_barrier_counts_on_the_holders_opponents_next_turn() {
        // Skarmory (80 HP, Metal) with the Barrier, Mewtwo ex ready. The holder to move: the opponent's next turn is
        // 6, the threat's first attack turn, so the first hit does 0: 1 + 2 hits where kp counts 2.
        let skarmory = || mon(CardId::A2111Skarmory).with_tool(tool(CardId::B2148MetalCoreBarrier));
        assert_eq!(clocks(&board(vec![skarmory()], vec![mewtwo()])), (2.0, 3.0));
        // The attacker to move on turn 5: the Barrier is live this turn, the threat's turn.
        let mut state = board(vec![skarmory()], vec![mewtwo()]);
        state.current_player = 1;
        assert_eq!(clocks(&state), (2.0, 3.0));
        // A threat 2 Energy short attacks after the Barrier is discarded.
        assert_eq!(clocks(&board(vec![skarmory()], vec![mon(CardId::A1129MewtwoEx)])), (4.0, 4.0));
    }

    #[test]
    fn lasting_tools_cut_every_hit_per_victim() {
        // Pidgey's Peck (30). Steel Apron on Skarmory (80): 20 a hit, 4 hits where kp counts 3.
        let pidgey = with(CardId::B1180Pidgey, EnergyType::Colorless, 2);
        let apron = mon(CardId::A2111Skarmory).with_tool(tool(CardId::A4153SteelApron));
        assert_eq!(clocks(&board(vec![apron.clone()], vec![pidgey.clone()])), (3.0, 4.0));
        // Per victim: a Bulbasaur Active (no Tool) keeps kp's 3; the benched Skarmory with the Apron takes 4.
        let state = board(vec![mon(CardId::A1001Bulbasaur), apron], vec![pidgey]);
        assert_eq!(clocks(&state), (6.0, 7.0));
        // Heavy Helmet (-20, Retreat Cost 3) against Weedle's Sting (20): nothing gets through, "never".
        let weedle = with(CardId::A1008Weedle, EnergyType::Grass, 1);
        let helmet = mon(CardId::B3b055Snorlax).with_tool(tool(CardId::B1219HeavyHelmet));
        assert_eq!(clocks(&board(vec![helmet], vec![weedle])), (7.0, 30.0));
    }

    #[test]
    fn a_benched_threat_is_timed_by_its_own_missing_energy() {
        // Mewtwo ex ready on the Bench behind a Pidgey with nothing attached: the clock's threat is the benched
        // Mewtwo ex (0 missing), first hit on turn 6, when the Stiffen-kind cut is still live.
        let mut snorlax = mon(CardId::B3b055Snorlax).with_remaining_hp(100);
        snorlax.add_effect(CardEffect::ReducedDamage { amount: 20 }, 1);
        let state = board(vec![snorlax], vec![mon(CardId::B1180Pidgey), mewtwo()]);
        assert_eq!(clocks(&state), (2.0, 3.0));
    }

    #[test]
    fn with_no_active_the_first_benched_victim_takes_the_first_hit() {
        // Player 0's Active was knocked out (promotion pending): the benched Snorlax at 100 HP is the clock's first
        // victim, so Blue's kind of cut (turns 5 and 6) goes on its first hit: 3 hits where kp counts 2.
        let mut state = board(vec![mon(CardId::B3b055Snorlax)], vec![mewtwo()]);
        state.in_play_pokemon[0] = [None, Some(mon(CardId::B3b055Snorlax).with_remaining_hp(100)), None, None];
        state.add_turn_effect(
            TurnEffect::ReducedDamageForTarget {
                amount: 20,
                player: 0,
                scope: DamageReductionScope::AllPokemon,
                only_from_ex: false,
            },
            1,
        );
        assert_eq!(clocks(&state), (2.0, 3.0));
    }

    #[test]
    fn an_evolved_threat_is_judged_as_the_form_it_attacks_as() {
        // Player 1's Swablu has no damaging attack; its threat is Mega Altaria ex from its deck (Mega Harmony 40, one
        // evolution step: first hit on turn 6). A cut only against an ex, live on turns 5 and 6, applies because the
        // form is an ex: Snorlax at 80 HP takes 20 then 40s, 3 hits where kp counts 2 (each after the 1 step).
        let only_ex = TurnEffect::ReducedDamageForTarget {
            amount: 20,
            player: 0,
            scope: DamageReductionScope::AllPokemon,
            only_from_ex: true,
        };
        let mut state = board(
            vec![mon(CardId::B3b055Snorlax).with_remaining_hp(80)],
            vec![with(CardId::B1196Swablu, EnergyType::Psychic, 2)],
        );
        state.decks[1].cards.push(get_card_by_enum(CardId::B1102MegaAltariaEx));
        state.add_turn_effect(only_ex, 1);
        let kp = turns_until_opponent_wins_scan(&state, 0, true, true, false, true, false, false, None);
        let kt = kt_clock(&state, 0, true, true, false, true, true).total(0.0);
        assert_eq!((kp, kt), (3.0, 4.0));
    }

    #[test]
    fn an_attack_that_ignores_the_defenders_effects_gets_no_cut_in_the_clock() {
        // Skarmory (80 HP) with the Barrier and Blue's kind of cut. Pidgey's Peck (30) is cut to 0 on its first hit:
        // 4 hits where kp counts 3. Sawk's Brick Break (30) ignores effects on the opponent's Active: 3, as kp.
        let skarmory = || mon(CardId::A2111Skarmory).with_tool(tool(CardId::B2148MetalCoreBarrier));
        let blue = TurnEffect::ReducedDamageForTarget {
            amount: 20,
            player: 0,
            scope: DamageReductionScope::AllPokemon,
            only_from_ex: false,
        };
        let mut state = board(vec![skarmory()], vec![with(CardId::B1180Pidgey, EnergyType::Colorless, 2)]);
        state.add_turn_effect(blue.clone(), 1);
        assert_eq!(clocks(&state), (3.0, 4.0));
        let mut state = board(vec![skarmory()], vec![with(CardId::B3086Sawk, EnergyType::Fighting, 1)]);
        state.add_turn_effect(blue, 1);
        assert_eq!(clocks(&state), (3.0, 3.0));
    }

    /// (turns until player 0's opponent wins, turns until player 0 wins) under `features`, player 0 evaluating.
    fn pair(state: &State, features: EvalFeatures) -> (f64, f64) {
        kt_clocks(state, 0, true, true, false, features)
    }

    #[test]
    fn rocky_helmet_takes_the_hits_the_threat_lands_off_its_hp_in_the_holders_clock() {
        // Player 0's Snorlax (130 HP, Mega Punch 70) with Rocky Helmet against Mewtwo ex (150 HP, 50 a hit), the
        // opponent's threat. Our clock on Mewtwo ex: 3 hits; theirs on Snorlax: 3. Player 0 to move, so Mewtwo ex
        // lands 3 - 1 = 2 hits before our knockout: 40 off its HP, 110, 2 hits.
        let snorlax = with(CardId::B3b055Snorlax, EnergyType::Colorless, 3).with_tool(tool(CardId::A2148RockyHelmet));
        let state = board(vec![snorlax.clone()], vec![mewtwo()]);
        assert_eq!(pair(&state, EvalFeatures::OFF), (3.0, 3.0));
        assert_eq!(pair(&state, EvalFeatures::KTC), (3.0, 2.0));
        let (mine, theirs) = (kt_clock(&state, 0, false, true, false, true, false), kt_clock(&state, 1, true, true, false, true, false));
        assert_eq!(counter_cut(&state, &theirs, &mine, 0), 40.0);
        // The opponent to move: Mewtwo ex attacks first and lands 3, capped at the 3 that knock Snorlax out.
        let mut state = board(vec![snorlax.clone()], vec![mewtwo()]);
        state.current_player = 1;
        let (mine, theirs) = (kt_clock(&state, 0, false, true, false, true, false), kt_clock(&state, 1, true, true, false, true, false));
        assert_eq!(counter_cut(&state, &theirs, &mine, 0), 60.0);
        // The opponent to move but its attack already made (its turn is ending): our turn comes first, 40 as above.
        let mut state = board(vec![snorlax.clone()], vec![mewtwo()]);
        state.current_player = 1;
        state.end_turn_pending = true;
        let (mine, theirs) = (kt_clock(&state, 0, false, true, false, true, false), kt_clock(&state, 1, true, true, false, true, false));
        assert_eq!(counter_cut(&state, &theirs, &mine, 0), 40.0);
        // The cap: a Snorlax at 50 HP falls to the first hit, which still fires the Helmet once.
        let weak = with(CardId::B3b055Snorlax, EnergyType::Colorless, 3)
            .with_tool(tool(CardId::A2148RockyHelmet))
            .with_remaining_hp(50);
        let state = board(vec![weak], vec![mewtwo()]);
        let (mine, theirs) = (kt_clock(&state, 0, false, true, false, true, false), kt_clock(&state, 1, true, true, false, true, false));
        assert_eq!(counter_cut(&state, &theirs, &mine, 0), 20.0);
    }

    #[test]
    fn the_counter_needs_the_threat_in_the_active_spot_and_works_for_both_sides() {
        // The opponent's threat is its benched Mewtwo ex; its Active (a bare Pidgey) hasn't attacked: no cut.
        let snorlax = with(CardId::B3b055Snorlax, EnergyType::Colorless, 3).with_tool(tool(CardId::A2148RockyHelmet));
        let state = board(vec![snorlax.clone()], vec![mon(CardId::B1180Pidgey), mewtwo()]);
        assert_eq!(pair(&state, EvalFeatures::KTC), pair(&state, EvalFeatures::OFF));
        // No counter-damage on the holder: nothing changes.
        let bare = with(CardId::B3b055Snorlax, EnergyType::Colorless, 3);
        let state = board(vec![bare.clone()], vec![mewtwo()]);
        assert_eq!(pair(&state, EvalFeatures::KTC), pair(&state, EvalFeatures::OFF));
        // The opponent's Mewtwo ex holds the Helmet and player 0's Snorlax is player 0's threat: the opponent's clock
        // on Snorlax takes the cut. Snorlax (130) takes 3 hits of 50; Mewtwo ex (150) 3 of 70; player 0 to move, so
        // Snorlax lands 3 hits: 60 off, 70 HP, 2 hits.
        let helmeted = mewtwo().with_tool(tool(CardId::A2148RockyHelmet));
        let state = board(vec![bare], vec![helmeted]);
        assert_eq!(pair(&state, EvalFeatures::OFF), (3.0, 3.0));
        assert_eq!(pair(&state, EvalFeatures::KTC), (2.0, 3.0));
    }

    #[test]
    fn switch_two_drops_only_the_flat_tool_term() {
        // A Giant Cape on player 0's Active: kp adds 10 for it; ktb doesn't. Nothing else differs. (43cef0b's test, on
        // the same switches on kp: amendment 2, item 7.)
        let caped = with(CardId::B3b055Snorlax, EnergyType::Colorless, 3).with_tool(tool(CardId::A2147GiantCape));
        let state = board(vec![caped], vec![mewtwo()]);
        let kp = public_clock_effect_value_function(&state, 0);
        assert!((kp - value(&state, 0, on_kp(EvalFeatures::KTB)) - 10.0).abs() < 1e-9);
        // From the other side it is -10 under kp and 0 under ktb.
        let kp1 = public_clock_effect_value_function(&state, 1);
        assert!((value(&state, 1, on_kp(EvalFeatures::KTB)) - kp1 - 10.0).abs() < 1e-9);
        // kta and ktc keep the flat term: with nothing for their clocks to act on, they are kp.
        assert_eq!(value(&state, 0, on_kp(EvalFeatures::KTA)), kp);
        assert_eq!(value(&state, 0, on_kp(EvalFeatures::KTC)), kp);
    }

    #[test]
    fn the_codes_switch_off_to_kp() {
        // 43cef0b's preset test, on the same switches on kp (amendment 2, item 7).
        let (kt, kta, ktb, ktc) =
            (on_kp(EvalFeatures::KT), on_kp(EvalFeatures::KTA), on_kp(EvalFeatures::KTB), on_kp(EvalFeatures::KTC));
        assert!(kt.defender_cuts && kt.tool_by_holder && kt.counter_damage);
        assert!(kta.defender_cuts && !kta.tool_by_holder && !kta.counter_damage);
        assert!(!ktb.defender_cuts && ktb.tool_by_holder && !ktb.counter_damage);
        assert!(!ktc.defender_cuts && !ktc.tool_by_holder && ktc.counter_damage);
        for f in [kt, kta, ktb, ktc] {
            // kq's, kd's, kpr's, the opening and kpf's features off.
            assert!(!f.next_attack_reduction && f.bench_attacker_weight == 0.0 && !f.defender_modifiers);
            assert!(!f.projected_readiness && !f.any_opening_switch() && !f.fuel_credit);
        }
        for f in [EvalFeatures::OFF, EvalFeatures::KQ, EvalFeatures::KD, EvalFeatures::KPR, EvalFeatures::KPF] {
            assert!(!f.defender_cuts && !f.tool_by_holder && !f.counter_damage);
        }
    }

    #[test]
    fn the_codes_are_kog_plus_their_switches() {
        // Amendment 2: kt<N> = kog<N> with the three switches on; kta, ktb and ktc = kog<N> with switch 1, 2 or 3 only.
        // With its switches off, each code is kog's preset exactly.
        let (kt, kta, ktb, ktc) = (EvalFeatures::KT, EvalFeatures::KTA, EvalFeatures::KTB, EvalFeatures::KTC);
        assert!(kt.defender_cuts && kt.tool_by_holder && kt.counter_damage);
        assert!(kta.defender_cuts && !kta.tool_by_holder && !kta.counter_damage);
        assert!(!ktb.defender_cuts && ktb.tool_by_holder && !ktb.counter_damage);
        assert!(!ktc.defender_cuts && !ktc.tool_by_holder && ktc.counter_damage);
        let switches_off =
            |f: EvalFeatures| EvalFeatures { defender_cuts: false, tool_by_holder: false, counter_damage: false, ..f };
        for f in [kt, kta, ktb, ktc] {
            assert_eq!(format!("{:?}", switches_off(f)), format!("{:?}", EvalFeatures::KOG));
            // kog's switch A and F on; kq's, kd's, kpr's (R) and kph's (A, B) features off.
            assert!(f.opening_first_turn_active && f.fuel_credit && !f.projected_readiness);
            assert!(!f.evolution_steps && !f.zone_to_bench && !f.next_attack_reduction && !f.defender_modifiers);
        }
        // kog, koh and the tiers before them have no kt switch.
        for f in [EvalFeatures::KOG, EvalFeatures::KOH, EvalFeatures::KPH, EvalFeatures::KPG] {
            assert!(!f.defender_cuts && !f.tool_by_holder && !f.counter_damage);
        }
    }

    /// Whether anything on `state` is something kt's switches read: a Tool in play, a damage-cut card effect or turn
    /// effect, or counter-damage on an Active.
    fn has_kt_source(state: &State) -> bool {
        let pokemon = (0..2).flat_map(|p| state.enumerate_in_play_pokemon(p).map(|(_, x)| x.clone()).collect::<Vec<_>>());
        let on_pokemon = pokemon.into_iter().any(|x| {
            x.has_tool_attached()
                || x.get_effects().iter().any(|(e, _)| {
                    matches!(e, CardEffect::ReducedDamage { .. } | CardEffect::ReducedDamageFromEx { .. })
                })
        });
        let turn_effects = (0..=u8::MAX).any(|t| {
            state.get_turn_effects(t).iter().any(|e| {
                matches!(e, TurnEffect::ReducedDamageForTarget { .. } | TurnEffect::ReducedDamageForType { .. })
            })
        });
        let counter = (0..2).any(|p| state.maybe_get_active(p).is_some_and(|a| get_counterattack_damage(state, a) > 0));
        on_pokemon || turn_effects || counter
    }

    #[test]
    fn on_played_states_kts_clock_is_kps_without_its_switches_and_kt_is_kp_with_nothing_to_price() {
        let deck = |name: &str| Deck::from_file(&format!("../decks/research/{name}.txt")).unwrap();
        let (mut states, mut with_source) = (0, 0);
        for (a, b) in [("blaziken", "suicune"), ("lucario", "altaria"), ("sceptile", "vespiquen"), ("hydreigon", "weezing")] {
            for seed in 0..3u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_000_000_000 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    game.play_tick();
                    ticks += 1;
                    let state = game.get_state_clone();
                    if state.setup_opponent_hidden || state.winner.is_some() {
                        continue;
                    }
                    states += 1;
                    for victim in 0..2 {
                        for zones in [false, true] {
                            let kp = turns_until_opponent_wins_scan(&state, victim, zones, true, false, true, false, false, None);
                            let kt = kt_clock(&state, victim, zones, true, false, true, false).total(0.0);
                            assert_eq!(kp, kt, "victim {victim}, zones {zones}, turn {}", state.turn_count);
                        }
                    }
                    let kp = public_clock_effect_value_function(&state, state.current_player);
                    if has_kt_source(&state) {
                        with_source += 1;
                    } else {
                        // 43cef0b's check, on the same switches on kp (amendment 2, item 7).
                        for f in [EvalFeatures::KT, EvalFeatures::KTA, EvalFeatures::KTB, EvalFeatures::KTC] {
                            assert_eq!(value(&state, state.current_player, on_kp(f)), kp, "turn {}", state.turn_count);
                        }
                    }
                }
            }
        }
        // Both kinds of state were met.
        assert!(states > 500 && with_source > 50 && with_source < states, "{states} states, {with_source} with a source");
    }

    #[test]
    fn kt_on_kog_is_koa_in_setup_and_the_switches_on_kp_plus_f_after_it() {
        // Amendment 2, item 7: on every position of 12 random games, from each player's own view, where the opponent's
        // setup is masked each code is koa's value (and so kog's); everywhere else it is the same switches on kp plus
        // kog's F term, exactly; and wherever nothing kt reads is on the board, it is kog's value, exactly.
        use crate::observation::{PlayerObservation, RevealedKnowledge};
        let research = |name: &str| format!("../decks/research/{name}.txt");
        let rayquaza = "../decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt".to_string();
        let pokemon_value = ValueFunctionParams::baseline().pokemon_value;
        let codes: [(EvalFeatures, fn(&State, usize) -> f64); 4] = [
            (EvalFeatures::KT, public_clock_effect_kt_value_function),
            (EvalFeatures::KTA, public_clock_effect_kta_value_function),
            (EvalFeatures::KTB, public_clock_effect_ktb_value_function),
            (EvalFeatures::KTC, public_clock_effect_ktc_value_function),
        ];
        let (mut setup, mut play, mut with_f, mut without_source) = (0, 0, 0, 0);
        let pairings = [
            (research("altaria"), research("blaziken")),
            (research("blaziken"), research("suicune")),
            (research("suicune"), research("lucario")),
            (rayquaza, research("blaziken")),
        ];
        for (a, b) in &pairings {
            for seed in 0..3u64 {
                let players: Vec<Box<dyn crate::players::Player>> = vec![
                    Box::new(RandomPlayer { deck: Deck::from_file(a).unwrap() }),
                    Box::new(RandomPlayer { deck: Deck::from_file(b).unwrap() }),
                ];
                let mut game = Game::new(players, 20_000_000_300 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        if view.winner.is_some() {
                            continue;
                        }
                        let turn = view.turn_count;
                        if view.setup_opponent_hidden {
                            setup += 1;
                            let koa = public_clock_effect_koa_value_function(view, me);
                            for (f, code) in codes {
                                assert_eq!(code(view, me), value(view, me, f));
                                assert_eq!(code(view, me), koa, "setup, turn {turn}");
                            }
                            continue;
                        }
                        play += 1;
                        let opp = (me + 1) % 2;
                        // kog's F with R off: the whole pile on each side (parametric_value_function_ex6).
                        let fuel = (crate::players::fuel_credit::fuel_credit(view, me, true, &view.discard_energies[me])
                            - crate::players::fuel_credit::fuel_credit(view, opp, false, &view.discard_energies[opp]))
                            * pokemon_value;
                        if fuel != 0.0 {
                            with_f += 1;
                        }
                        for (f, code) in codes {
                            assert_eq!(code(view, me), value(view, me, f));
                            assert_eq!(code(view, me), value(view, me, on_kp(f)) + fuel, "turn {turn}");
                        }
                        if !has_kt_source(view) {
                            without_source += 1;
                            let kog = public_clock_effect_kog_value_function(view, me);
                            for (_, code) in codes {
                                assert_eq!(code(view, me), kog, "turn {turn}");
                            }
                        }
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        // Every kind of position was met: setup, F acting, and positions with and without anything kt reads.
        assert!(
            setup > 0 && play > 500 && with_f > 0 && without_source > 0 && without_source < play,
            "{setup} setup, {play} play, {with_f} with F, {without_source} without a kt source"
        );
    }
}

#[cfg(test)]
mod kog_tests {
    //! kog = kp + koa's switch A + kpg's F. Switch A is read only in the setup evaluation, which returns before F; F
    //! only after it. So kog's value is koa's wherever the opponent's setup is masked, and kpg's everywhere else.
    use super::*;
    use crate::observation::{PlayerObservation, RevealedKnowledge};
    use crate::players::RandomPlayer;
    use crate::{Deck, Game};

    #[test]
    fn kog_is_koa_in_setup_and_kpg_after_it() {
        let flags = EvalFeatures::KOG;
        assert!(flags.opening_first_turn_active && flags.fuel_credit);
        assert!(!flags.opening_bench_working && !flags.opening_readiness && !flags.projected_readiness);
        assert!(!flags.next_attack_reduction && flags.bench_attacker_weight == 0.0 && !flags.defender_modifiers);
        assert!(!flags.defender_cuts && !flags.tool_by_holder && !flags.counter_damage);
        let deck = |name: &str| Deck::from_file(&format!("../decks/research/{name}.txt")).unwrap();
        let (mut setup, mut play) = (0, 0);
        for (a, b) in [("altaria", "blaziken"), ("blaziken", "suicune"), ("altaria", "lucario")] {
            for seed in 0..4u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_000_000_100 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        // Each player's own view, as the search evaluates it: the opponent's setup is masked at turn 0.
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        let kog = public_clock_effect_kog_value_function(view, me);
                        if view.setup_opponent_hidden {
                            setup += 1;
                            assert_eq!(kog, public_clock_effect_koa_value_function(view, me));
                        } else {
                            play += 1;
                            assert_eq!(kog, public_clock_effect_kpg_value_function(view, me));
                        }
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        assert!(setup > 0 && play > 500, "{setup} setup and {play} play evaluations");
    }
}

#[cfg(test)]
mod kph_tests {
    //! kph (`rl/results/kph_2026-09-27/REGISTRATION.md`, section 4): fix A in the projected readiness and fix B in the
    //! clock, on built boards (each states its timing), and their rules on played positions.
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::hooks::get_board_retreat_cost_for_player;
    use crate::players::RandomPlayer;
    use crate::{Deck, Game};

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    fn with(id: CardId, energy: EnergyType, count: usize) -> PlayedCard {
        mon(id).with_energy(vec![energy; count])
    }

    /// The leaf after player 0's EndTurn: player 1 to move on turn 6 with its turn running. Player 0 has `mine` and
    /// its Zone shows `current` and `next`; player 1 has `theirs`.
    fn after_end_turn(mine: Vec<PlayedCard>, theirs: Vec<PlayedCard>, current: Option<EnergyType>, next: Option<EnergyType>) -> State {
        let mut state = State::default();
        state.set_board(mine, theirs);
        state.turn_count = 6;
        state.current_player = 1;
        state.energy_zone[0].current = current;
        state.energy_zone[0].next = next;
        state
    }

    /// Mid-turn: as [`after_end_turn`], but player 0 is to move on turn 5 with its turn running.
    fn mid_turn(mine: Vec<PlayedCard>, theirs: Vec<PlayedCard>, current: Option<EnergyType>, next: Option<EnergyType>) -> State {
        let mut state = after_end_turn(mine, theirs, current, next);
        state.turn_count = 5;
        state.current_player = 0;
        state
    }

    fn bulbasaur() -> Vec<PlayedCard> {
        vec![mon(CardId::A1001Bulbasaur)]
    }

    /// Player 0's Active readiness, player 0 evaluating: (unprojected, R, A).
    fn readiness(state: &State) -> (f64, f64, f64) {
        let score = |projected, a| calculate_active_pokemon_online_score_ex(state, 0, false, true, false, projected, a);
        (score(None, false), score(Some(Horizon::ThroughNextTurn), false), score(Some(Horizon::ThroughNextTurn), true))
    }

    /// Turns until player 0 beats player 1 (player 0, evaluating, is the threat, read through its next turn):
    /// (kpr's clock, kph's with fix B).
    fn clocks(state: &State) -> (f64, f64) {
        let clock = |b| {
            calculate_turns_until_opponent_wins_projected(
                state,
                1,
                true,
                true,
                false,
                true,
                false,
                false,
                Some(Horizon::ThroughNextTurn),
                b,
            )
        };
        (clock(false), clock(true))
    }

    #[test]
    fn a_swablu_one_step_from_mega_altaria_ex_reads_half() {
        // Mid-turn. Swablu holding a [P], [P] in this turn's Zone; Mega Altaria ex (Mega Harmony [P][P]) is the deck's
        // only evolution. R: [P][P] of 2, 1.0. A: (2 - 0 - 1 step) / 2 = 0.5, and the unprojected reading is 0.5 too.
        let mut state = mid_turn(vec![with(CardId::B1196Swablu, EnergyType::Psychic, 1)], bulbasaur(), Some(EnergyType::Psychic), None);
        state.decks[0].cards = vec![get_card_by_enum(CardId::B1102MegaAltariaEx)];
        assert_eq!(readiness(&state), (0.5, 1.0, 0.5));
    }

    #[test]
    fn a_bare_riolu_reads_its_evolution_step_as_a_missing_energy() {
        // Riolu with nothing; Mega Lucario ex (Fighting Pulse [F][F]) is the deck's only evolution; [F] in the Zone now
        // and next. The yardstick is [F][F], as the registration's expected values assume.
        let riolu = || vec![mon(CardId::B3079Riolu)];
        let deck = || vec![get_card_by_enum(CardId::B3081MegaLucarioEx)];
        // After EndTurn: next turn's [F] only. R: 1 of 2, 0.5. A: (2 - 1 - 1) / 2 = 0.
        let mut state = after_end_turn(riolu(), bulbasaur(), Some(EnergyType::Fighting), Some(EnergyType::Fighting));
        state.decks[0].cards = deck();
        assert_eq!(readiness(&state), (0.0, 0.5, 0.0));
        // Mid-turn: this turn's and next turn's. R: 1.0. A: (2 - 0 - 1) / 2 = 0.5.
        let mut state = mid_turn(riolu(), bulbasaur(), Some(EnergyType::Fighting), Some(EnergyType::Fighting));
        state.decks[0].cards = deck();
        assert_eq!(readiness(&state), (0.0, 1.0, 0.5));
    }

    #[test]
    fn b_gives_an_opponents_benched_pokemon_one_zone_energy_at_the_usual_leaf() {
        // The usual leaf (player 1 to move, its turn running). Player 1's Bonsly (Retreat Cost 0) in front, a Bulbasaur
        // (Vine Whip [G][C], 40) benched holding a [G], [G] in its Zone now. Its next attack is this turn: the Active
        // gets this turn's [G] only, and so does the benched Bulbasaur.
        let mut state = after_end_turn(
            vec![mon(CardId::B3b055Snorlax)],
            vec![mon(CardId::B3078Bonsly), with(CardId::A1001Bulbasaur, EnergyType::Grass, 1)],
            None,
            None,
        );
        state.energy_zone[1].current = Some(EnergyType::Grass);
        state.energy_zone[1].next = Some(EnergyType::Grass);
        let bonsly = state.get_active(1).clone();
        assert_eq!(projected_active_energy(&state, 1, &bonsly, Horizon::NextAttack), vec![EnergyType::Grass]);
        assert_eq!(projected_zone_energy(&state, 1, Horizon::NextAttack), vec![EnergyType::Grass]);
        assert!(bench_can_reach_active(&state, 1, Horizon::NextAttack));
        // Player 0's clock (the opponent's threats on Snorlax, 130 HP): kpr's threat is Bonsly (10, 13 hits); B makes the
        // Bulbasaur ready this turn, 4 hits of 40.
        let opponents_clock = |state: &State, b| {
            calculate_turns_until_opponent_wins_projected(state, 0, false, true, false, true, false, false, Some(Horizon::NextAttack), b)
        };
        assert_eq!((opponents_clock(&state, false), opponents_clock(&state, true)), (13.0, 4.0));
        // Its attack is this turn, so a retreat already made this turn rules the Bulbasaur out.
        state.has_retreated = true;
        assert!(!bench_can_reach_active(&state, 1, Horizon::NextAttack));
        assert_eq!(opponents_clock(&state, true), 13.0);
    }

    #[test]
    fn q01_keeping_bonsly_in_front_reads_the_same_clock_as_the_swap() {
        // Dustin's Q01, both lines at the leaf after EndTurn: Bonsly (Retreat Cost 0) and Mega Lucario ex holding an [F],
        // [F] in the Zone next turn, against a Bulbasaur (70 HP). Swap: Mega Lucario ex in front, ready next turn,
        // 1 hit. Keep: kpr credits next turn's [F] to Bonsly only, so its threat stays Bonsly (10, 7 hits); B gives it
        // to the benched Mega Lucario ex, and the two lines read the same.
        let lucario = || with(CardId::B3081MegaLucarioEx, EnergyType::Fighting, 1);
        let keep = after_end_turn(vec![mon(CardId::B3078Bonsly), lucario()], bulbasaur(), None, Some(EnergyType::Fighting));
        let swap = after_end_turn(vec![lucario(), mon(CardId::B3078Bonsly)], bulbasaur(), None, Some(EnergyType::Fighting));
        assert_eq!((clocks(&keep), clocks(&swap)), ((7.0, 1.0), (1.0, 1.0)));
    }

    #[test]
    fn q10_a_benched_vespiquen_ex_behind_a_shuckle_ex_that_cant_pay_its_retreat_is_not_credited() {
        // Dustin's Q10, the bench-feed alternative, mid-turn: Shuckle ex in front, Vespiquen ex (Chase Order [G][G])
        // benched with a [G], [G] in the Zone now and next, X Speed played this turn and a retreat already made.
        let q10 = |shuckle_energy: usize| {
            let mut state = mid_turn(
                vec![with(CardId::A4021ShuckleEx, EnergyType::Grass, shuckle_energy), with(CardId::B4011VespiquenEx, EnergyType::Grass, 1)],
                bulbasaur(),
                Some(EnergyType::Grass),
                Some(EnergyType::Grass),
            );
            state.add_turn_effect(TurnEffect::ReducedRetreatCost { amount: 1 }, 0);
            state.has_retreated = true;
            state
        };
        // Shuckle ex with nothing: X Speed makes this turn's cost 0, but its board cost is 1, unpaid. Not credited.
        let state = q10(0);
        let shuckle = state.get_active(0);
        assert_eq!(get_retreat_cost_for_player(&state, 0, shuckle).len(), 0);
        assert_eq!(get_board_retreat_cost_for_player(&state, 0, shuckle).len(), 1);
        assert!(!bench_can_reach_active(&state, 0, Horizon::ThroughNextTurn));
        assert_eq!(clocks(&state).0, clocks(&state).1);
        // The positive control: Shuckle ex holding a [G] pays its board cost, and Vespiquen ex can be in front for
        // next turn's attack (a retreat then isn't ruled out by this turn's). Credited: Chase Order ready, 1 hit.
        let state = q10(1);
        assert!(bench_can_reach_active(&state, 0, Horizon::ThroughNextTurn));
        let (kpr, kph) = clocks(&state);
        assert!(kph < kpr, "kpr {kpr}, kph {kph}");
        assert_eq!(kph, 1.0);
    }

    #[test]
    fn b_gives_zone_energy_only_so_f_counts_nothing_twice() {
        // Mid-turn, player 0: Bonsly (Retreat Cost 0) in front, Charmander (Ember [R], 30) benched with nothing, two [R]
        // in the discard pile and a Flame Patch in hand, so F is live. B's projection holds only the Zone's Energy.
        let board = |zone: Option<EnergyType>| {
            let mut state = mid_turn(vec![mon(CardId::B3078Bonsly), mon(CardId::A1033Charmander)], bulbasaur(), zone, None);
            state.discard_energies[0] = vec![EnergyType::Fire, EnergyType::Fire];
            state.hands[0].push(get_card_by_enum(CardId::B1217FlamePatch));
            state
        };
        let state = board(None);
        assert!(super::super::fuel_credit::fuel_credit(&state, 0, true, &state.discard_energies[0]) > 0.0);
        // Nothing in the Zone: B gives nothing (never the discard pile's [R]), so kphb scores exactly as kpf.
        assert_eq!(projected_zone_energy(&state, 0, Horizon::ThroughNextTurn), vec![]);
        assert_eq!(public_clock_effect_kphb_value_function(&state, 0), public_clock_effect_kpf_value_function(&state, 0));
        // [R] in this turn's Zone: exactly that one [R], and the discard pile F reads is untouched.
        let state = board(Some(EnergyType::Fire));
        assert_eq!(projected_zone_energy(&state, 0, Horizon::ThroughNextTurn), vec![EnergyType::Fire]);
        let bonsly = state.get_active(0).clone();
        assert_eq!(
            projected_active_energy_and_discard(&state, 0, &bonsly, Horizon::ThroughNextTurn).1,
            vec![EnergyType::Fire, EnergyType::Fire]
        );
    }

    #[test]
    fn kph_reads_no_hidden_card() {
        // Player 1's side is read from its board. Its Swablu holds a [P]; a Mega Altaria ex hidden in its hand or deck
        // must not change the value (A reads the opponent's card as it is, steps 0), nor may a hidden Ivysaur behind
        // its Bulbasaur, benched where B reads it.
        let value = |hidden: CardId, in_hand: bool| {
            let mut state = after_end_turn(
                vec![mon(CardId::B3b055Snorlax)],
                vec![with(CardId::B1196Swablu, EnergyType::Psychic, 1), with(CardId::A1001Bulbasaur, EnergyType::Grass, 1)],
                None,
                None,
            );
            state.energy_zone[1].current = Some(EnergyType::Psychic);
            let card = get_card_by_enum(hidden);
            if in_hand {
                state.hands[1].push(card);
            } else {
                state.decks[1].cards.push(card);
            }
            public_clock_effect_kph_value_function(&state, 0)
        };
        for in_hand in [false, true] {
            assert_eq!(value(CardId::B1102MegaAltariaEx, in_hand), value(CardId::A1053Squirtle, in_hand));
            assert_eq!(value(CardId::A1002Ivysaur, in_hand), value(CardId::A1053Squirtle, in_hand));
        }
    }

    #[test]
    fn the_switches_fall_back_to_kpf_and_kpg() {
        // kph with A and B off is kpf's preset; A and B act only on R's projection, so with R off it is kpg.
        let off = EvalFeatures { evolution_steps: false, zone_to_bench: false, ..EvalFeatures::KPH };
        assert_eq!(format!("{off:?}"), format!("{:?}", EvalFeatures::KPF));
        assert_eq!(
            format!("{:?}", EvalFeatures { evolution_steps: false, ..EvalFeatures::KPH }),
            format!("{:?}", EvalFeatures::KPHB)
        );
        assert_eq!(
            format!("{:?}", EvalFeatures { zone_to_bench: false, ..EvalFeatures::KPH }),
            format!("{:?}", EvalFeatures::KPHA)
        );
        let r_off = EvalFeatures { projected_readiness: false, ..EvalFeatures::KPH };
        let value = |state: &State, me: usize, f: EvalFeatures| {
            parametric_value_function_ex6(state, me, &ValueFunctionParams::baseline(), true, false, true, true, false, f)
        };
        let mut n = 0;
        for_played_positions(|state| {
            for me in 0..2 {
                assert_eq!(value(state, me, r_off), public_clock_effect_kpg_value_function(state, me));
                n += 1;
            }
        });
        assert!(n > 1000, "{n} evaluations");
    }

    /// Every position of 12 random games of the table lists (Altaria v Lucario, Vespiquen v Hydreigon, Lucario v
    /// Vespiquen, Blaziken v Suicune), past setup.
    fn for_played_positions(mut check: impl FnMut(&State)) {
        let deck = |name: &str| Deck::from_file(&format!("../decks/research/{name}.txt")).unwrap();
        for (a, b) in [("altaria", "lucario"), ("vespiquen", "hydreigon"), ("lucario", "vespiquen"), ("blaziken", "suicune")] {
            for seed in 0..3u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_000_000_200 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    game.play_tick();
                    ticks += 1;
                    let state = game.get_state_clone();
                    if state.turn_count > 0 && state.winner.is_none() {
                        check(&state);
                    }
                }
            }
        }
    }

    #[test]
    fn on_played_positions_a_is_r_without_a_step_and_never_below_the_unprojected_reading_with_one() {
        let (mut same, mut stepped) = (0, 0);
        for_played_positions(|state| {
            for player in 0..2 {
                let Some(active) = state.maybe_get_active(player) else { continue };
                for public_only in [false, true] {
                    for horizon in [Horizon::ThroughNextTurn, Horizon::NextAttack] {
                        let charged = at_next_attack(state, player, active, horizon);
                        let (target_stage, total, _) = online_yardstick(state, player, &charged, public_only, true, false);
                        let Card::Pokemon(current) = &active.card else { continue };
                        let score = |projected, a| {
                            calculate_active_pokemon_online_score_ex(state, player, public_only, true, false, projected, a)
                        };
                        let (a, r, u) = (score(Some(horizon), true), score(Some(horizon), false), score(None, false));
                        if total == 0 || target_stage <= current.stage {
                            assert_eq!(a, r);
                            same += 1;
                        } else {
                            assert!(a >= u, "A {a} below the unprojected {u}");
                            stepped += 1;
                        }
                    }
                }
            }
        });
        assert!(same > 500 && stepped > 50, "{same} without a step, {stepped} with one");
    }

    #[test]
    fn on_played_positions_b_is_never_slower_than_r_and_equals_it_with_an_empty_bench() {
        let (mut faster, mut empty) = (0, 0);
        for_played_positions(|state| {
            for victim in 0..2 {
                for (zones, horizon) in [(false, Horizon::NextAttack), (true, Horizon::ThroughNextTurn)] {
                    let clock = |b| {
                        calculate_turns_until_opponent_wins_projected(state, victim, zones, true, false, true, false, false, Some(horizon), b)
                    };
                    let (r, b) = (clock(false), clock(true));
                    assert!(b <= r, "B {b} slower than R {r}");
                    if state.enumerate_bench_pokemon(1 - victim).next().is_none() {
                        assert_eq!(b, r);
                        empty += 1;
                    } else if b < r {
                        faster += 1;
                    }
                }
            }
        });
        assert!(faster > 10 && empty > 10, "{faster} faster, {empty} with an empty Bench");
    }
}

#[cfg(test)]
mod koh_tests {
    //! koh = kog + R'. Switch A is read only in the setup evaluation, where nothing is projected (turn 0), and F, R, A
    //! and B only after it. So koh's value is koa's where the opponent's setup is masked and kph's everywhere else; with
    //! A and B off (kog + R) it is koa's in setup and kpf's after; with R' off it is kog.
    use super::*;
    use crate::observation::{PlayerObservation, RevealedKnowledge};
    use crate::players::RandomPlayer;
    use crate::{Deck, Game};

    #[test]
    fn koh_is_kog_with_r_prime_and_reads_as_its_parts() {
        let r_prime_off =
            EvalFeatures { projected_readiness: false, evolution_steps: false, zone_to_bench: false, ..EvalFeatures::KOH };
        assert_eq!(format!("{r_prime_off:?}"), format!("{:?}", EvalFeatures::KOG));
        let kog_r = EvalFeatures { evolution_steps: false, zone_to_bench: false, ..EvalFeatures::KOH };
        assert_eq!(format!("{kog_r:?}"), format!("{:?}", EvalFeatures { opening_first_turn_active: true, ..EvalFeatures::KPF }));
        let value = |state: &State, me: usize, f: EvalFeatures| {
            parametric_value_function_ex6(state, me, &ValueFunctionParams::baseline(), true, false, true, true, false, f)
        };
        let deck = |name: &str| Deck::from_file(&format!("../decks/research/{name}.txt")).unwrap();
        let (mut setup, mut play) = (0, 0);
        for (a, b) in [("altaria", "blaziken"), ("lucario", "vespiquen"), ("altaria", "lucario"), ("vespiquen", "hydreigon")] {
            for seed in 0..3u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_000_000_300 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        let (koh, koh_ab_off) = (public_clock_effect_koh_value_function(view, me), value(view, me, kog_r));
                        if view.setup_opponent_hidden {
                            setup += 1;
                            let koa = public_clock_effect_koa_value_function(view, me);
                            assert_eq!((koh, koh_ab_off), (koa, koa));
                        } else {
                            play += 1;
                            assert_eq!(koh, public_clock_effect_kph_value_function(view, me));
                            assert_eq!(koh_ab_off, public_clock_effect_kpf_value_function(view, me));
                        }
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        assert!(setup > 0 && play > 500, "{setup} setup and {play} play evaluations");
    }
}

#[cfg(test)]
mod km_tests {
    //! km on kta (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, section 4.1, as Amendment 1 (c) item
    //! 3 re-bases it, Sept 30): switch N2, the attacker's lasting Stadium damage bonus, in kta's threat clock
    //! ([`kt_clock_stadium`], switch 1 on). 9c11b30 built and tested N2 on kog; these are those tests on kta's clock,
    //! with kta in kog's place, and the pin where N2 meets switch 1.
    //! Numbers from `lib/card.py`: Mega Lucario ex B3 081 (Stage 1
    //! [F], 190 HP, [F][F] Fighting Pulse 90); Kirlia A1 131 (Stage 1 [P], [P][C] Smack 30); Mega Rayquaza ex B4 120
    //! (Basic Dragon ex, 180 HP, no Weakness); Dratini A1 183 (Basic Dragon, 70 HP, no Weakness); Bonsly B3 078 ([-]
    //! Teary Attack 10); Riolu B3 079 (Basic [F]); Training Area B2 153 (+10 for a Stage 1 attacker); Arena of
    //! Antiquity B3 154 (+20 for an [F] attacker against an ex).
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::hooks::modify_damage;
    use crate::observation::{PlayerObservation, RevealedKnowledge};
    use crate::players::RandomPlayer;
    use crate::{Deck, Game};

    const PLAIN: DamageModifierContext<'static> = DamageModifierContext { attack_name: None, attack_effect: None };

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    /// Player 0: `victim` (Active, then Bench). Player 1: `threat`. Player 0 to move on turn 5; `stadium` in play.
    fn board(victim: Vec<PlayedCard>, threat: Vec<PlayedCard>, stadium: Option<CardId>) -> State {
        let mut state = State::default();
        state.set_board(victim, threat);
        state.turn_count = 5;
        state.current_player = 0;
        state.active_stadium = stadium.map(get_card_by_enum);
        state
    }

    /// kta's clock on `victim`'s side, as `kt_clocks` runs it in public evaluation (effect-aware, switch 1 on), with N2
    /// on (km) or off (kta).
    fn clock(state: &State, victim: usize, read_zones: bool, n2: bool) -> f64 {
        kt_clock_stadium(state, victim, read_zones, true, false, true, true, n2).total(0.0)
    }

    /// A code's value from `myself`'s view, evaluated as the public codes are.
    fn value(state: &State, myself: usize, features: EvalFeatures) -> f64 {
        parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, features)
    }

    fn lucario_ff() -> PlayedCard {
        mon(CardId::B3081MegaLucarioEx).with_energy(vec![EnergyType::Fighting; 2])
    }

    #[test]
    fn the_bonus_is_what_modify_damage_adds_for_an_active_to_active_attack() {
        // Every Stadium case, attacker Stage 0, 1 and 2 of [F], [R] and [P], against an ex and a non-ex with no
        // Weakness: the bonus equals modify_damage's result with the Stadium minus without it, base damage 50.
        let attackers = [
            CardId::A1143Machop,
            CardId::A1144Machoke,
            CardId::A1145Machamp,
            CardId::A1033Charmander,
            CardId::A1034Charmeleon,
            CardId::A1035Charizard,
            CardId::A1130Ralts,
            CardId::A1131Kirlia,
            CardId::A1132Gardevoir,
        ];
        let (mut cases, mut nonzero) = (0, 0);
        for stadium in [None, Some(CardId::B2153TrainingArea), Some(CardId::B3154ArenaofAntiquity)] {
            for attacker in attackers {
                for target in [CardId::A1183Dratini, CardId::B4120MegaRayquazaEx] {
                    let with = board(vec![mon(attacker)], vec![mon(target)], stadium);
                    let without = board(vec![mon(attacker)], vec![mon(target)], None);
                    let engine = modify_damage(&with, (0, 0), (50, 1, 0), true, PLAIN)
                        - modify_damage(&without, (0, 0), (50, 1, 0), true, PLAIN);
                    let a = with.get_active(0);
                    let ours = lasting_stadium_damage_bonus(
                        &with,
                        get_stage(a),
                        &with.pokemon_energy_types(a),
                        with.get_active(1).card.is_ex(),
                    );
                    assert_eq!(ours, engine, "{stadium:?}, {attacker:?} against {target:?}");
                    cases += 1;
                    nonzero += (ours > 0) as usize;
                }
            }
        }
        // 3 Stadium cases x 9 attackers x 2 targets. Training Area: the three Stage 1s against both targets (6);
        // Arena: the three [F] attackers against the ex (3).
        assert_eq!((cases, nonzero), (54, 9));
    }

    #[test]
    fn a_stadium_bonus_that_saves_a_hit_shortens_the_clock_by_one_turn() {
        // Mega Lucario ex with [F][F] (90) against a Mega Lucario ex (190 HP, ex): 3 hits; 2 with Training Area (100)
        // or Arena (110). The survival clock is exactly one turn shorter.
        let base = board(vec![mon(CardId::B3081MegaLucarioEx)], vec![lucario_ff()], None);
        assert_eq!((clock(&base, 0, false, false), clock(&base, 0, false, true)), (3.0, 3.0));
        for stadium in [CardId::B2153TrainingArea, CardId::B3154ArenaofAntiquity] {
            let state = board(vec![mon(CardId::B3081MegaLucarioEx)], vec![lucario_ff()], Some(stadium));
            assert_eq!(clock(&state, 0, false, false), 3.0, "kta doesn't see {stadium:?}");
            assert_eq!(clock(&state, 0, false, true), 2.0, "km: {stadium:?}");
        }
        // Against 180 HP: 2 hits of 90, 100 or 110 alike: no change.
        for stadium in [None, Some(CardId::B2153TrainingArea), Some(CardId::B3154ArenaofAntiquity)] {
            let state = board(vec![mon(CardId::B3081MegaLucarioEx).with_damage(10)], vec![lucario_ff()], stadium);
            assert_eq!((clock(&state, 0, false, false), clock(&state, 0, false, true)), (2.0, 2.0), "{stadium:?}");
        }
        // A [P] Stage 1 attacker gets Training Area's +10 and not Arena's +20: Kirlia's Smack (30) against Mega
        // Rayquaza ex (180, ex) is 6 hits, 5 with Training Area (40), 6 with Arena.
        let kirlia = || mon(CardId::A1131Kirlia).with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]);
        let with = |stadium| board(vec![mon(CardId::B4120MegaRayquazaEx)], vec![kirlia()], stadium);
        assert_eq!(clock(&with(None), 0, false, true), 6.0);
        assert_eq!(clock(&with(Some(CardId::B2153TrainingArea)), 0, false, true), 5.0);
        assert_eq!(clock(&with(Some(CardId::B3154ArenaofAntiquity)), 0, false, true), 6.0);
    }

    #[test]
    fn the_same_stadium_shortens_the_other_sides_clock_by_the_same_rule() {
        // Roles swapped: player 1 is the victim and player 0's Mega Lucario ex the threat.
        for (stadium, hits) in [
            (None, 3.0),
            (Some(CardId::B2153TrainingArea), 2.0),
            (Some(CardId::B3154ArenaofAntiquity), 2.0),
        ] {
            let state = board(vec![lucario_ff()], vec![mon(CardId::B3081MegaLucarioEx)], stadium);
            assert_eq!(clock(&state, 1, false, true), hits, "{stadium:?}");
            assert_eq!(clock(&state, 1, false, false), 3.0, "{stadium:?}");
        }
    }

    #[test]
    fn a_benched_stage_1_threat_gets_the_bonus() {
        // Player 1's Bonsly in front (Teary Attack 10) and a Mega Lucario ex with [F][F] benched: the threat is the
        // benched Mega (90 > 10, both ready). Against player 0's Mega Lucario ex (190): 3 hits, 2 with Training Area.
        let threat = vec![mon(CardId::B3078Bonsly), lucario_ff()];
        let state = board(vec![mon(CardId::B3081MegaLucarioEx)], threat.clone(), None);
        assert_eq!(clock(&state, 0, false, true), 3.0);
        let state = board(vec![mon(CardId::B3081MegaLucarioEx)], threat, Some(CardId::B2153TrainingArea));
        assert_eq!(clock(&state, 0, false, true), 2.0);
    }

    #[test]
    fn an_evolving_threat_is_priced_as_its_evolved_form_and_the_opponents_forms_are_not_scanned() {
        // Player 0's Riolu (Basic [F]) with Mega Lucario ex in player 0's hand. Scanned as player 0's own threat
        // (zones read), the evolved form's candidates carry the Stage 1 [F] form: Training Area +10 and Arena +20
        // against an ex. Riolu's own candidates are Stage 0: Arena's +20 only.
        let mut state = board(
            vec![mon(CardId::B3079Riolu).with_energy(vec![EnergyType::Fighting; 2])],
            vec![mon(CardId::B4120MegaRayquazaEx)],
            Some(CardId::B2153TrainingArea),
        );
        state.hands[0] = vec![get_card_by_enum(CardId::B3081MegaLucarioEx)];
        let damage = |atk: &Attack, _: &PlayedCard| atk.fixed_damage;
        let own = threat_candidates(&state, 0, true, None, &damage);
        let evolved: Vec<_> = own.iter().filter(|c| c.form.is_some()).collect();
        let current: Vec<_> = own.iter().filter(|c| c.form.is_none()).collect();
        assert!(!evolved.is_empty() && !current.is_empty());
        for c in &evolved {
            assert_eq!(threat_attacker_stage_and_types(&state, 0, c), Some((1, vec![EnergyType::Fighting])));
        }
        for c in &current {
            assert_eq!(threat_attacker_stage_and_types(&state, 0, c), Some((0, vec![EnergyType::Fighting])));
        }
        let bonus = |stadium: CardId, stage: u8| {
            let mut s = state.clone();
            s.active_stadium = Some(get_card_by_enum(stadium));
            lasting_stadium_damage_bonus(&s, stage, &[EnergyType::Fighting], true)
        };
        assert_eq!((bonus(CardId::B2153TrainingArea, 1), bonus(CardId::B2153TrainingArea, 0)), (10, 0));
        assert_eq!((bonus(CardId::B3154ArenaofAntiquity, 1), bonus(CardId::B3154ArenaofAntiquity, 0)), (20, 20));
        // As the opponent's threat (board only), no form is scanned, so the bonus is Riolu's own Stage 0's.
        let board_only = threat_candidates(&state, 0, false, None, &damage);
        assert!(!board_only.is_empty() && board_only.iter().all(|c| c.form.is_none()));
    }

    #[test]
    fn with_nothing_to_read_kms_clock_is_ktas() {
        // No Stadium, or a Stadium that adds no damage (Hiking Trail, Fragrant Forest): N2 changes nothing.
        for stadium in [None, Some(CardId::B2b069HikingTrail), Some(CardId::B3153FragrantForest)] {
            let state = board(vec![mon(CardId::B3081MegaLucarioEx)], vec![lucario_ff()], stadium);
            for victim in 0..2 {
                for zones in [false, true] {
                    assert_eq!(clock(&state, victim, zones, true), clock(&state, victim, zones, false), "{stadium:?}");
                }
            }
        }
    }

    #[test]
    fn km_is_kta_plus_n2_and_nothing_else() {
        // Amendment 1 (c) 3.2, flag-off identity, bitwise: with its flag cleared, KM's preset is KTA's, every field,
        // compared as `the_codes_are_kog_plus_their_switches` compares presets. KTA is kog + kt's switch 1.
        let km = EvalFeatures::KM;
        assert!(km.stadium_bonus_in_clock && km.defender_cuts && !km.tool_by_holder && !km.counter_damage);
        assert_eq!(
            format!("{:?}", EvalFeatures { stadium_bonus_in_clock: false, ..km }),
            format!("{:?}", EvalFeatures::KTA)
        );
        // Every other preset has the flag off.
        for f in [
            EvalFeatures::OFF,
            EvalFeatures::KQ,
            EvalFeatures::KD,
            EvalFeatures::KPR,
            EvalFeatures::KOA,
            EvalFeatures::KOB,
            EvalFeatures::KOR,
            EvalFeatures::KPF,
            EvalFeatures::KPG,
            EvalFeatures::KPH,
            EvalFeatures::KPHA,
            EvalFeatures::KPHB,
            EvalFeatures::KOH,
            EvalFeatures::KOG,
            EvalFeatures::KT,
            EvalFeatures::KTA,
            EvalFeatures::KTB,
            EvalFeatures::KTC,
        ] {
            assert!(!f.stadium_bonus_in_clock, "{f:?}");
        }
    }

    #[test]
    fn on_played_states_km_is_kta_wherever_no_damage_stadium_is_in_play() {
        // Values, bitwise, on every position of 12 random games of the lists that carry the two Stadiums (Altaria's
        // Training Area, Lucario's Arena), from each player's own view: km = kta in setup, and wherever neither
        // Training Area nor Arena of Antiquity is in play. Where one is, km differs from kta somewhere. And everywhere,
        // km's value with KM's flag cleared is kta's value function's (Amendment 1 (c) 3.2).
        let deck = |name: &str| Deck::from_file(&format!("../decks/research/{name}.txt")).unwrap();
        let is_damage_stadium = |state: &State| {
            crate::stadiums::has_stadium(state, CardId::B2153TrainingArea)
                || crate::stadiums::has_stadium(state, CardId::B3154ArenaofAntiquity)
        };
        let (mut same, mut with_stadium, mut differ) = (0, 0, 0);
        for (a, b) in [("altaria", "lucario"), ("lucario", "blaziken"), ("altaria", "suicune"), ("lucario", "altaria")] {
            for seed in 0..3u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_000_000_400 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        let (km, kta) =
                            (public_clock_effect_km_value_function(view, me), public_clock_effect_kta_value_function(view, me));
                        let flag_cleared = value(view, me, EvalFeatures { stadium_bonus_in_clock: false, ..EvalFeatures::KM });
                        assert_eq!(flag_cleared, kta, "turn {}", view.turn_count);
                        if view.setup_opponent_hidden || !is_damage_stadium(view) {
                            assert_eq!(km, kta, "turn {}", view.turn_count);
                            same += 1;
                        } else {
                            with_stadium += 1;
                            differ += (km != kta) as usize;
                        }
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        assert!(same > 500 && with_stadium > 50 && differ > 0, "{same} same, {with_stadium} with a Stadium, {differ} differ");
    }

    /// The score's card term for player 0: `(my.hand - opp.hand) * hand_size + (opp.deck - my.deck) * deck_size`
    /// (`parametric_value_function_ex6`; both weights 1 in the baseline).
    fn card_term(state: &State) -> f64 {
        let p = ValueFunctionParams::baseline();
        (state.hands[0].len() as f64 - state.hands[1].len() as f64) * p.hand_size
            + (state.decks[1].cards.len() as f64 - state.decks[0].cards.len() as f64) * p.deck_size
    }

    /// Plays `names` in order (each the legal Play of that Trainer), then EndTurn, from `state`; the card term after.
    fn card_term_after(state: &State, names: &[&str]) -> f64 {
        let mut game = crate::test_support::get_initialized_game(0);
        game.set_state(state.clone());
        for name in names.iter().copied().chain(["EndTurn"]) {
            let (_, actions) = game.get_state_clone().generate_possible_actions();
            let action = actions
                .into_iter()
                .find(|a| match (&a.action, name) {
                    (crate::actions::SimpleAction::EndTurn, "EndTurn") => true,
                    (crate::actions::SimpleAction::Play { trainer_card }, n) => trainer_card.name == n,
                    _ => false,
                })
                .unwrap_or_else(|| panic!("{name} is not legal here"));
            game.apply_action(&action);
        }
        card_term(&game.get_state_clone())
    }

    #[test]
    fn diagnostic_the_card_term_rewards_x_speed_before_copycat_and_a_play_under_hiking_trail_by_one() {
        // Open question 13 of km's registration (a diagnostic of section 1.2's arithmetic, not km's switch): on
        // boards that end the turn, with hands of inert cards (a Charizard with no Charmeleon in play can't be
        // played), only the card term compared.
        let inert = || get_card_by_enum(CardId::A1035Charizard);
        let mut game = crate::test_support::get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(vec![mon(CardId::A1143Machop)], vec![mon(CardId::A1183Dratini)]);
        state.current_player = 0;
        state.turn_count = 5;
        state.move_generation_stack.clear();
        state.active_stadium = None;
        state.hands[1] = vec![inert(), inert(), inert(), inert()];
        game.set_state(state);
        let base = game.get_state_clone();
        // 1. No Trail: X Speed then Copycat against Copycat alone. X Speed goes to the discard pile instead of into
        //    the shuffle, so the deck ends one card smaller: +1.
        let mut state = base.clone();
        state.hands[0] = vec![
            get_card_by_enum(CardId::PA002XSpeed),
            get_card_by_enum(CardId::B1225Copycat),
            inert(),
            inert(),
        ];
        let both = card_term_after(&state, &["X Speed", "Copycat"]);
        let copycat = card_term_after(&state, &["Copycat"]);
        assert_eq!(both - copycat, 1.0);
        // 2. Hiking Trail in play and a hand under 3: playing a card (X Speed) and ending the turn tops the hand up
        //    to 3 with one draw more than not playing it: +1.
        let mut state = base.clone();
        state.active_stadium = Some(get_card_by_enum(CardId::B2b069HikingTrail));
        state.hands[0] = vec![get_card_by_enum(CardId::PA002XSpeed), inert()];
        let played = card_term_after(&state, &["X Speed"]);
        let not_played = card_term_after(&state, &[]);
        assert_eq!(played - not_played, 1.0);
    }

    #[test]
    fn an_evolving_threat_that_the_clock_picks_is_priced_as_its_evolved_form() {
        // The full-clock Cubone/Marowak test (fb825d1, kept by Amendment 1 (f)), on kta's clock: through the whole
        // clock, not only the candidates. The board carries no cut, so kta's clock gives kog's numbers. Player 0's Cubone A1 151
        // (Basic [F], [C] Growl, no damage) with [F] attached and Marowak A1 152 (Stage 1 [F], [F] Bone Beatdown 40)
        // in player 0's hand; player 1's Mega Rayquaza ex (180, ex, no Weakness). Scanned with zones read (player 0's
        // own threat), the only damaging candidate is the Marowak form: 1 missing (the evolution step), 40 a hit.
        let mut state = board(
            vec![mon(CardId::A1151Cubone).with_energy(vec![EnergyType::Fighting])],
            vec![mon(CardId::B4120MegaRayquazaEx)],
            None,
        );
        state.hands[0] = vec![get_card_by_enum(CardId::A1152Marowak)];
        let with = |stadium: Option<CardId>| {
            let mut s = state.clone();
            s.active_stadium = stadium.map(get_card_by_enum);
            s
        };
        // kta: 1 + ceil(180 / 40) = 6 turns, whatever the Stadium.
        for stadium in [None, Some(CardId::B2153TrainingArea), Some(CardId::B3154ArenaofAntiquity)] {
            assert_eq!(clock(&with(stadium), 1, true, false), 6.0, "{stadium:?}");
        }
        // km: Training Area's +10 comes from the form's Stage 1 (Cubone, Stage 0, would get none): 1 + ceil(180 / 50)
        // = 5. Arena's +20 from its [F] against the ex: 1 + 180 / 60 = 4. Hiking Trail adds nothing: 6.
        assert_eq!(clock(&with(None), 1, true, true), 6.0);
        assert_eq!(clock(&with(Some(CardId::B2153TrainingArea)), 1, true, true), 5.0);
        assert_eq!(clock(&with(Some(CardId::B3154ArenaofAntiquity)), 1, true, true), 4.0);
        assert_eq!(clock(&with(Some(CardId::B2b069HikingTrail)), 1, true, true), 6.0);
        // Read as the opponent's threat (board only), no form is scanned, Cubone has no damaging attack, and the clock
        // is "never" (30) either way.
        let ta = with(Some(CardId::B2153TrainingArea));
        assert_eq!((clock(&ta, 1, false, true), clock(&ta, 1, false, false)), (30.0, 30.0));
    }

    #[test]
    fn where_n2_meets_switch_1_a_hit_in_ktas_clock_is_what_modify_damage_deals() {
        // Amendment 1 (c) 3.1, the case new to the re-issue. Player 1's attacker, ready (its first attack turn is 6),
        // against player 0's Active carrying a damage-cut Tool, a -20 live through turn 6 (Stiffen's kind), or both;
        // no Stadium, Training Area or Arena of Antiquity in play. In kta's clock the first hit carries every cut and
        // each later hit the lasting ones (switch 1). Under km each also carries N2's bonus: the clock's hits equal
        // what modify_damage deals for that active-to-active attack, the Stadium's bonus added before Weakness and
        // the cuts taken off after, floored at 0. Under kta they equal modify_damage on the same board with no
        // Stadium. The victims have no Weakness to [F] or [P] (card.py: Venusaur ex A1 004, 190 HP, Retreat 3, weak
        // Fire; Venusaur A1 003, 160 HP, Retreat 3, weak Fire; Melmetal ex B1 174, [M], 170 HP, Retreat 3, weak Fire).
        // Heavy Helmet B1 219: -20 with a Retreat Cost of 3 or more. Steel Apron A4 153: -10 for an [M] Pokemon.
        // Metal Core Barrier B2 148: -50 for an [M] Pokemon, discarded at the end of the opponent's turn (the first hit
        // only). Attackers: Mega Lucario ex (Stage 1 [F], 90), Kirlia A1 131 (Stage 1 [P], [P][C] Smack 30), Machop
        // A1 143 (Basic [F], [F] Knuckle Punch 20).
        let tool = |id: CardId| get_card_by_enum(id);
        let for_a_turn = |mut p: PlayedCard| {
            p.add_effect(CardEffect::ReducedDamage { amount: 20 }, 1);
            p
        };
        let venusaur_ex = || mon(CardId::A1004VenusaurEx);
        let melmetal_ex = || mon(CardId::B1174MelmetalEx);
        let helmet = || tool(CardId::B1219HeavyHelmet);
        // (the victim with every cut, the victim with its lasting cuts only)
        let victims = [
            (venusaur_ex().with_tool(helmet()), venusaur_ex().with_tool(helmet())),
            (mon(CardId::A1003Venusaur).with_tool(helmet()), mon(CardId::A1003Venusaur).with_tool(helmet())),
            (for_a_turn(venusaur_ex()), venusaur_ex()),
            (for_a_turn(venusaur_ex().with_tool(helmet())), venusaur_ex().with_tool(helmet())),
            (melmetal_ex().with_tool(tool(CardId::B2148MetalCoreBarrier)), melmetal_ex()),
            (
                for_a_turn(melmetal_ex().with_tool(tool(CardId::A4153SteelApron))),
                melmetal_ex().with_tool(tool(CardId::A4153SteelApron)),
            ),
        ];
        let attackers = [
            lucario_ff(),
            mon(CardId::A1131Kirlia).with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]),
            mon(CardId::A1143Machop).with_energy(vec![EnergyType::Fighting]),
        ];
        let bare = |state: &State| {
            let mut state = state.clone();
            state.active_stadium = None;
            state
        };
        let (mut cases, mut n2_acts, mut cut_acts) = (0, 0, 0);
        for stadium in [None, Some(CardId::B2153TrainingArea), Some(CardId::B3154ArenaofAntiquity)] {
            for attacker in &attackers {
                let attack = attacker.card.get_attacks()[0].clone();
                let context =
                    DamageModifierContext { attack_name: Some(&attack.title), attack_effect: attack.effect.as_deref() };
                let engine = |state: &State| modify_damage(state, (1, 0), (attack.fixed_damage, 0, 0), true, context) as f64;
                for (all_cuts, lasting_cuts) in &victims {
                    let first_board = board(vec![all_cuts.clone()], vec![attacker.clone()], stadium);
                    let later_board = board(vec![lasting_cuts.clone()], vec![attacker.clone()], stadium);
                    let hits = |n2: bool| {
                        let (_, first, later) =
                            kt_clock_stadium(&first_board, 0, false, true, false, true, true, n2).active.unwrap();
                        (first, later)
                    };
                    let label = format!("{stadium:?}, {} against {}", attacker.get_name(), all_cuts.get_name());
                    let (km, kta) = (hits(true), hits(false));
                    assert_eq!(km, (engine(&first_board), engine(&later_board)), "km: {label}");
                    assert_eq!(kta, (engine(&bare(&first_board)), engine(&bare(&later_board))), "kta: {label}");
                    cases += 1;
                    n2_acts += (km != kta) as usize;
                    cut_acts += (km.0 < attack.fixed_damage as f64) as usize;
                }
            }
        }
        // 3 Stadium cases x 3 attackers x 6 victims. N2 changes a hit in some, and a cut shortens a first hit in many.
        assert_eq!(cases, 54);
        assert!(n2_acts > 10 && cut_acts > 20, "{n2_acts} cases where N2 acts, {cut_acts} where a cut acts");
    }
}

#[cfg(test)]
mod kn_tests {
    //! kn = km + switch N1, the opponent's Active Retreat Cost counted in the score as the bot's own is
    //! (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, "Appendix. Parked: N1": its drafted tests, with
    //! km in the place of the retired draft's kog and kn in the place of its `kma`). Built Sept 30, not registered.
    //! Numbers from `lib/card.py`: Retreat Costs Team Rocket's Raticate ex B4a 059 0, Dratini A1 183 1, Ralts A1 130 1
    //! ([P]), Machop A1 143 2, Mewtwo ex A1 129 2 ([P]), Machamp A1 145 3, Charmander A1 033 1, Suicune ex A4a 020 2;
    //! Team Rocket's Goo-zooka B4a 068 (the opponent's Active +1 until the end of their next turn); Peculiar Plaza
    //! B2 155 (each [P] Pokemon in play 2 less); Ariados B1a 006 (Trap Territory: the opponent's Active +1); Small
    //! Balloon B3b 064 (a Basic 1 less); Inflatable Boat A4a 067 (a [W] Pokemon 1 less).
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::observation::{PlayerObservation, RevealedKnowledge};
    use crate::players::expectiminimax_player::ExpectiMiniMaxPlayer;
    use crate::players::public_pricing_player::PublicPricingPlayer;
    use crate::players::{create_players, PlayerCode, RandomPlayer};
    use crate::{Deck, Game};

    /// Scratch lists made for these tests (not table, held-out or Dustin's lists): Goo-zooka, Peculiar Plaza, and two
    /// opponents whose Actives carry a retreat Tool (Inflatable Boat, Small Balloon).
    pub(super) const GOO: &str = "Energy: Fighting\n2 Machop A1 143\n2 Machoke A1 144\n1 Machamp A1 145\n\
        2 Team Rocket's Rattata B4a 058\n2 Team Rocket's Raticate ex B4a 059\n2 Team Rocket's Goo-zooka B4a 068\n\
        2 Poké Ball P-A 005\n2 Professor's Research P-A 007\n1 Sabrina A1 225\n1 Cyrus A2 150\n1 Giant Cape A2 147\n\
        1 X Speed P-A 002\n1 Potion P-A 001\n";
    pub(super) const PLAZA: &str = "Energy: Psychic\n2 Mewtwo ex A1 129\n2 Ralts A1 130\n2 Kirlia A1 131\n2 Gardevoir A1 132\n\
        2 Peculiar Plaza B2 155\n2 Poké Ball P-A 005\n2 Professor's Research P-A 007\n1 Rare Candy A3 144\n\
        1 Sabrina A1 225\n1 Cyrus A2 150\n1 Giant Cape A2 147\n1 X Speed P-A 002\n1 Potion P-A 001\n";
    pub(super) const WATER_BOAT: &str = "Energy: Water\n2 Suicune ex A4a 020\n2 Squirtle A1 053\n2 Wartortle A1 054\n\
        1 Blastoise A1 055\n2 Inflatable Boat A4a 067\n2 Poké Ball P-A 005\n2 Professor's Research P-A 007\n\
        1 Rare Candy A3 144\n1 Sabrina A1 225\n1 Cyrus A2 150\n1 Giant Cape A2 147\n1 X Speed P-A 002\n\
        2 Potion P-A 001\n";
    pub(super) const FIRE_BALLOON: &str = "Energy: Fire\n2 Charmander A1 033\n2 Charmeleon A1 034\n2 Charizard A1 035\n\
        2 Small Balloon B3b 064\n2 Poké Ball P-A 005\n2 Professor's Research P-A 007\n2 Rare Candy A3 144\n\
        1 Sabrina A1 225\n1 Cyrus A2 150\n1 Giant Cape A2 147\n1 X Speed P-A 002\n2 Potion P-A 001\n";
    /// The pairs the played-state and move-for-move tests cycle through.
    pub(super) const PAIRS: [(&str, &str); 5] =
        [(GOO, WATER_BOAT), (GOO, FIRE_BALLOON), (PLAZA, FIRE_BALLOON), (PLAZA, WATER_BOAT), (GOO, PLAZA)];

    fn deck(list: &str) -> Deck {
        let deck = Deck::from_string(list).unwrap();
        assert!(deck.is_valid(), "{list}");
        deck
    }

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    /// A code's value from `myself`'s view, evaluated as the public codes are.
    fn value(state: &State, myself: usize, features: EvalFeatures) -> f64 {
        parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, features)
    }

    /// kn's value minus km's, from `myself`'s view.
    fn n1(state: &State, myself: usize) -> f64 {
        value(state, myself, EvalFeatures::KN) - value(state, myself, EvalFeatures::KM)
    }

    /// The board Retreat Cost of `player`'s Active, as the engine computes it for a public leaf.
    fn board_cost(state: &State, player: usize) -> f64 {
        crate::hooks::get_board_retreat_cost_for_player(state, player, state.get_active(player)).len() as f64
    }

    /// Player 0 (`mine`) against player 1 (`theirs`), player 0 to move on turn 5 after setup, `stadium` in play.
    fn position(mine: Vec<PlayedCard>, theirs: Vec<PlayedCard>, stadium: Option<CardId>) -> State {
        let game = crate::test_support::get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(mine, theirs);
        state.current_player = 0;
        state.turn_count = 5;
        state.move_generation_stack.clear();
        state.setup_opponent_hidden = false;
        state.active_stadium = stadium.map(get_card_by_enum);
        state
    }

    fn close(a: f64, b: f64) -> bool {
        (a - b).abs() < 1e-9
    }

    #[test]
    fn kn_is_km_plus_n1_and_nothing_else() {
        // With its flag cleared, KN's preset is KM's, every field, compared as presets are compared.
        let kn = EvalFeatures::KN;
        assert!(kn.opponent_retreat_cost && kn.stadium_bonus_in_clock && kn.defender_cuts);
        assert_eq!(format!("{:?}", EvalFeatures { opponent_retreat_cost: false, ..kn }), format!("{:?}", EvalFeatures::KM));
        // Every other preset has the flag off.
        for f in [
            EvalFeatures::OFF,
            EvalFeatures::KQ,
            EvalFeatures::KD,
            EvalFeatures::KPR,
            EvalFeatures::KOA,
            EvalFeatures::KOB,
            EvalFeatures::KOR,
            EvalFeatures::KPF,
            EvalFeatures::KPG,
            EvalFeatures::KPH,
            EvalFeatures::KPHA,
            EvalFeatures::KPHB,
            EvalFeatures::KOH,
            EvalFeatures::KOG,
            EvalFeatures::KT,
            EvalFeatures::KTA,
            EvalFeatures::KTB,
            EvalFeatures::KTC,
            EvalFeatures::KM,
        ] {
            assert!(!f.opponent_retreat_cost, "{f:?}");
        }
    }

    #[test]
    fn n1_the_term_is_the_opponents_active_retreat_cost() {
        // The drafted test "N1, the term": two Actives with Retreat Costs a and b and no effects; from player 0's view
        // kn - km = b, and from player 1's view kn - km = a. The bot's own cost counts in both codes, as before.
        let costs = [
            (CardId::B4a059TeamRocketsRaticateEx, 0.0),
            (CardId::A1183Dratini, 1.0),
            (CardId::A1143Machop, 2.0),
            (CardId::A1145Machamp, 3.0),
        ];
        for (mine, a) in costs {
            for (theirs, b) in costs {
                let state = position(vec![mon(mine)], vec![mon(theirs)], None);
                assert!(close(n1(&state, 0), b), "{mine:?} v {theirs:?}: {}", n1(&state, 0));
                assert!(close(n1(&state, 1), a), "{mine:?} v {theirs:?}, player 1's view: {}", n1(&state, 1));
            }
        }
    }

    #[test]
    fn n1_reads_the_board_cost_the_engine_computes() {
        // The term is the engine's own board Retreat Cost of the opponent's Active (the cost a public leaf reads, as
        // for the bot's own Active): Goo-zooka's effect, Trap Territory, Peculiar Plaza and the retreat Tools, each
        // moving it from the printed cost.
        let mut goo = mon(CardId::A1143Machop);
        goo.add_effect(CardEffect::IncreasedRetreatCost { amount: 1 }, 1);
        let cases: Vec<(&str, State, f64)> = vec![
            ("printed", position(vec![mon(CardId::A1183Dratini)], vec![mon(CardId::A1143Machop)], None), 2.0),
            ("Goo-zooka", position(vec![mon(CardId::A1183Dratini)], vec![goo], None), 3.0),
            (
                "Trap Territory",
                position(vec![mon(CardId::A1183Dratini), mon(CardId::B1a006Ariados)], vec![mon(CardId::A1143Machop)], None),
                3.0,
            ),
            (
                "Plaza on a [P] Active",
                position(vec![mon(CardId::A1183Dratini)], vec![mon(CardId::A1129MewtwoEx)], Some(CardId::B2155PeculiarPlaza)),
                0.0,
            ),
            (
                "Plaza on a non-[P] Active",
                position(vec![mon(CardId::A1183Dratini)], vec![mon(CardId::A1143Machop)], Some(CardId::B2155PeculiarPlaza)),
                2.0,
            ),
            (
                "Small Balloon",
                position(
                    vec![mon(CardId::A1183Dratini)],
                    vec![mon(CardId::A1143Machop).with_tool(get_card_by_enum(CardId::B3b064SmallBalloon))],
                    None,
                ),
                1.0,
            ),
            (
                "Inflatable Boat",
                position(
                    vec![mon(CardId::A1183Dratini)],
                    vec![mon(CardId::A4a020SuicuneEx).with_tool(get_card_by_enum(CardId::A4a067InflatableBoat))],
                    None,
                ),
                1.0,
            ),
        ];
        for (label, state, cost) in cases {
            assert_eq!(board_cost(&state, 1), cost, "{label}: the engine's cost");
            assert!(close(n1(&state, 0), cost), "{label}: kn - km = {}", n1(&state, 0));
        }
    }

    #[test]
    fn n1_goo_zooka_moves_kn_by_one_and_km_by_nothing() {
        // The drafted test "N1, Goo-zooka". The effect alone: +1 under kn, 0 under km. The whole play through the
        // game (the card leaves the hand and the effect lands): -1 under km (the card term), level under kn.
        let base = position(vec![mon(CardId::A1183Dratini)], vec![mon(CardId::A1143Machop)], None);
        let mut hit = base.clone();
        hit.get_active_mut(1).add_effect(CardEffect::IncreasedRetreatCost { amount: 1 }, 1);
        let delta = |a: &State, b: &State, f: EvalFeatures| value(b, 0, f) - value(a, 0, f);
        assert!(close(delta(&base, &hit, EvalFeatures::KN), 1.0), "kn: {}", delta(&base, &hit, EvalFeatures::KN));
        assert_eq!(delta(&base, &hit, EvalFeatures::KM), 0.0, "km");

        let mut game = crate::test_support::get_initialized_game(0);
        let mut before = base.clone();
        before.hands[0] = vec![get_card_by_enum(CardId::B4a068TeamRocketsGoozooka)];
        game.set_state(before.clone());
        let (_, actions) = before.generate_possible_actions();
        let play = actions
            .iter()
            .find(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Team Rocket's Goo-zooka"))
            .expect("Goo-zooka is playable");
        game.apply_action(play);
        let after = game.get_state_clone();
        assert_eq!(board_cost(&after, 1), 3.0, "the effect landed");
        assert!(close(delta(&before, &after, EvalFeatures::KM), -1.0), "km: {}", delta(&before, &after, EvalFeatures::KM));
        assert!(close(delta(&before, &after, EvalFeatures::KN), 0.0), "kn: {}", delta(&before, &after, EvalFeatures::KN));
    }

    #[test]
    fn n1_peculiar_plaza_counts_for_both_sides() {
        // The drafted test "N1, Plaza": Plaza in play against no Stadium. [P] Actives with cost 2 on both sides: kn 0,
        // km +2. Only the bot's Active [P]: +2 under both. Only theirs: -2 under kn, 0 under km.
        let (p, other) = (CardId::A1129MewtwoEx, CardId::A1143Machop);
        for (mine, theirs, kn, km) in [(p, p, 0.0, 2.0), (p, other, 2.0, 2.0), (other, p, -2.0, 0.0)] {
            let without = position(vec![mon(mine)], vec![mon(theirs)], None);
            let with = position(vec![mon(mine)], vec![mon(theirs)], Some(CardId::B2155PeculiarPlaza));
            let delta = |f: EvalFeatures| value(&with, 0, f) - value(&without, 0, f);
            assert!(close(delta(EvalFeatures::KN), kn), "{mine:?} v {theirs:?}: kn {}", delta(EvalFeatures::KN));
            assert!(close(delta(EvalFeatures::KM), km), "{mine:?} v {theirs:?}: km {}", delta(EvalFeatures::KM));
        }
    }

    #[test]
    fn n1_leaves_setup_to_km_and_reads_no_hidden_card() {
        // The drafted test "N1, setup and hidden cards". In setup (the opponent's board masked) kn's value is km's,
        // bit for bit: the setup path is untouched. After setup, the term doesn't move when the opponent's hand and
        // deck are swapped for other cards.
        let mut setup = position(vec![mon(CardId::A1143Machop)], vec![mon(CardId::A1145Machamp)], None);
        setup.setup_opponent_hidden = true;
        assert_eq!(value(&setup, 0, EvalFeatures::KN), value(&setup, 0, EvalFeatures::KM));

        let state = position(vec![mon(CardId::A1183Dratini)], vec![mon(CardId::A1145Machamp)], None);
        let mut swapped = state.clone();
        let other = || get_card_by_enum(CardId::B2155PeculiarPlaza);
        swapped.hands[1] = swapped.hands[1].iter().map(|_| other()).collect();
        swapped.decks[1].cards = swapped.decks[1].cards.iter().map(|_| other()).collect();
        assert!(close(n1(&state, 0), 3.0) && close(n1(&swapped, 0), 3.0), "{} {}", n1(&state, 0), n1(&swapped, 0));
    }

    #[test]
    fn on_played_states_kn_is_km_plus_the_opponents_active_retreat_cost() {
        // Values on every position of 10 random games of the scratch pairs, from each player's own view: kn = km
        // bit for bit in setup; after it, kn - km is the opponent's board Retreat Cost; and everywhere, kn's value with
        // KN's flag cleared is km's value function's, bit for bit.
        let (mut setup, mut after, mut nonzero) = (0, 0, 0);
        for (pair, (a, b)) in PAIRS.iter().enumerate() {
            for seed in 0..2u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_950_000_000 + 10 * pair as u64 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        let (kn, km) =
                            (public_clock_effect_kn_value_function(view, me), public_clock_effect_km_value_function(view, me));
                        let flag_cleared = value(view, me, EvalFeatures { opponent_retreat_cost: false, ..EvalFeatures::KN });
                        assert_eq!(flag_cleared, km, "turn {}", view.turn_count);
                        if view.setup_opponent_hidden || view.winner.is_some() || view.maybe_get_active(1 - me).is_none() {
                            if view.setup_opponent_hidden || view.winner.is_some() {
                                assert_eq!(kn, km, "turn {}", view.turn_count);
                            }
                            setup += 1;
                        } else {
                            let cost = board_cost(view, 1 - me);
                            assert!(close(kn - km, cost), "turn {}: kn - km = {}, cost {cost}", view.turn_count, kn - km);
                            after += 1;
                            nonzero += (cost > 0.0) as usize;
                        }
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        assert!(setup > 20 && after > 500 && nonzero > 300, "{setup} setup or ended, {after} after setup, {nonzero} with a cost");
    }

    /// One game on `seed`, `players` in seats 0 and 1: every move played, then the points and the winner.
    fn moves(players: Vec<Box<dyn crate::players::Player>>, seed: u64) -> Vec<String> {
        let mut game = Game::new(players, seed);
        let mut out = vec![];
        while !game.is_game_over() && out.len() < 3000 {
            out.push(format!("{:?}", game.play_tick()));
        }
        let state = game.get_state_clone();
        out.push(format!("points {:?} winner {:?}", state.points, state.winner));
        out
    }

    /// kn3 with N1 off: km3's player (as players/mod.rs builds the km, kn and kt codes) on kn's preset with the flag
    /// cleared.
    fn kn3_with_n1_off(deck: Deck) -> Box<dyn crate::players::Player> {
        Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: 3,
                write_debug_trees: false,
                value_function: Box::new(|state: &State, myself: usize| {
                    value(state, myself, EvalFeatures { opponent_retreat_cost: false, ..EvalFeatures::KN })
                }),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        })
    }

    #[test]
    fn kn3_with_n1_off_equals_km3_move_for_move_on_200_scratch_deals() {
        // 200 scratch deals: the five scratch pairs, 40 each, on Claude diagnostic seeds 20,951,000,000 + i, the
        // first-named list in seat 0 on even i. km3 against km3 (players/mod.rs, as `deckgym simulate` builds them)
        // and kn3 with N1 off against itself play the same moves, choices and results in every deal. kn3 itself
        // (N1 on, from players/mod.rs) differs from km3 somewhere in the first 40, so the lists reach N1.
        let deals: Vec<(Deck, Deck, u64)> = (0..200u64)
            .map(|i| {
                let (a, b) = PAIRS[(i / 40) as usize];
                let (a, b) = if i % 2 == 0 { (deck(a), deck(b)) } else { (deck(b), deck(a)) };
                (a, b, 20_951_000_000 + i)
            })
            .collect();
        let workers = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1).clamp(1, 8);
        let results: Vec<(usize, bool, Option<bool>)> = std::thread::scope(|scope| {
            let handles: Vec<_> = (0..workers)
                .map(|w| {
                    let deals = &deals;
                    scope.spawn(move || {
                        let mut out = vec![];
                        for (i, (a, b, seed)) in deals.iter().enumerate().filter(|(i, _)| i % workers == w) {
                            let km = moves(create_players(a.clone(), b.clone(), vec![PlayerCode::KM { max_depth: 3 }; 2]), *seed);
                            let off = moves(vec![kn3_with_n1_off(a.clone()), kn3_with_n1_off(b.clone())], *seed);
                            let on = (i < 40).then(|| {
                                moves(create_players(a.clone(), b.clone(), vec![PlayerCode::KN { max_depth: 3 }; 2]), *seed) != km
                            });
                            out.push((i, off == km, on));
                        }
                        out
                    })
                })
                .collect();
            handles.into_iter().flat_map(|h| h.join().unwrap()).collect()
        });
        assert_eq!(results.len(), 200);
        let differ: Vec<usize> = results.iter().filter(|r| !r.1).map(|r| r.0).collect();
        assert!(differ.is_empty(), "kn3 with N1 off differs from km3 on deals {differ:?}");
        let n1_moves = results.iter().filter(|r| r.2 == Some(true)).count();
        assert!(n1_moves > 0, "kn3 plays as km3 on all of the first 40 deals");
    }
}

#[cfg(test)]
mod kr_tests {
    //! kr = km + switch C2, a benched threat pays its Active's way out in km's clock (both sides), N1's static term off;
    //! kro = C2 in the opponent's clock only (`rl/results/kn_build_2026-09-30/TIMING.md`, C2). Built Sept 30, not
    //! registered. Numbers from `lib/card.py`: Retreat Costs Machop A1 143 2 (Basic [F]), Dratini A1 183 1 (Basic
    //! Dragon, [WL] Ram 40), Mewtwo ex A1 129 2 (Basic [P], [PC] Psychic Sphere 50), Suicune ex A4a 020 2 ([W]),
    //! Darkrai B2b 040 2 ([D]); Bombirdier B3 115 (Villainous Delivery: on the Bench, your Active [D] Pokemon's cost 1
    //! less); Ariados B1a 006 (Trap Territory: the opponent's Active +1); Small Balloon B3b 064 (a Basic 1 less);
    //! Inflatable Boat A4a 067 (a [W] Pokemon 1 less); Peculiar Plaza B2 155 (each [P] Pokemon 2 less); Team Rocket's
    //! Goo-zooka B4a 068 (`IncreasedRetreatCost { 1 }` until the end of the opponent's next turn).
    use super::kn_tests::PAIRS;
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::observation::{PlayerObservation, RevealedKnowledge};
    use crate::players::expectiminimax_player::ExpectiMiniMaxPlayer;
    use crate::players::public_pricing_player::PublicPricingPlayer;
    use crate::players::{create_players, PlayerCode, RandomPlayer};
    use crate::{Deck, Game};

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    fn deck(list: &str) -> Deck {
        Deck::from_string(list).unwrap()
    }

    /// A code's value from `myself`'s view, evaluated as the public codes are.
    fn value(state: &State, myself: usize, features: EvalFeatures) -> f64 {
        parametric_value_function_ex6(state, myself, &ValueFunctionParams::baseline(), true, false, true, true, false, features)
    }

    /// Player 0 (`zero`) against player 1 (`one`), player 0 to move on turn 5 after setup, `stadium` in play, and each
    /// side's next Energy visible (so a side's next turn has its attachment).
    fn position(zero: Vec<PlayedCard>, one: Vec<PlayedCard>, stadium: Option<CardId>) -> State {
        let game = crate::test_support::get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(zero, one);
        state.current_player = 0;
        state.turn_count = 5;
        state.move_generation_stack.clear();
        state.setup_opponent_hidden = false;
        state.has_retreated = false;
        state.active_stadium = stadium.map(get_card_by_enum);
        state.energy_zone[0].current = Some(EnergyType::Psychic);
        state.energy_zone[1].next = Some(EnergyType::Psychic);
        state
    }

    /// The engine's own retreat arithmetic for player 0 (to move): the fewest Energy that must be added to its Active
    /// before a Retreat is offered (`move_generation`: `can_retreat` and the Active's Energy covering its cost), or
    /// `None` if none is offered within 8.
    fn engine_shortfall(state: &State) -> Option<usize> {
        (0..8).find(|&k| {
            let mut s = state.clone();
            s.get_active_mut(0).attached_energy.extend(vec![EnergyType::Fighting; k]);
            let (actor, actions) = s.generate_possible_actions();
            assert_eq!(actor, 0);
            actions.iter().any(|a| matches!(a.action, SimpleAction::Retreat(_)))
        })
    }

    #[test]
    fn kr_and_kro_are_km_plus_c2_and_nothing_else() {
        // With C2's flags cleared, KR's and KRO's presets are KM's, every field, compared as presets are compared; KRO
        // is KR with the bot's own half off. N1's static term is off in both.
        let (kr, kro) = (EvalFeatures::KR, EvalFeatures::KRO);
        assert!(kr.retreat_opponent_threat && kr.retreat_own_threat && !kr.opponent_retreat_cost);
        assert!(kro.retreat_opponent_threat && !kro.retreat_own_threat && !kro.opponent_retreat_cost);
        let cleared = |f: EvalFeatures| format!("{:?}", EvalFeatures { retreat_opponent_threat: false, retreat_own_threat: false, ..f });
        assert_eq!(cleared(kr), format!("{:?}", EvalFeatures::KM));
        assert_eq!(cleared(kro), format!("{:?}", EvalFeatures::KM));
        assert_eq!(format!("{:?}", EvalFeatures { retreat_own_threat: false, ..kr }), format!("{kro:?}"));
        for f in [
            EvalFeatures::OFF,
            EvalFeatures::KQ,
            EvalFeatures::KD,
            EvalFeatures::KPR,
            EvalFeatures::KOA,
            EvalFeatures::KOB,
            EvalFeatures::KOR,
            EvalFeatures::KPF,
            EvalFeatures::KPG,
            EvalFeatures::KPH,
            EvalFeatures::KPHA,
            EvalFeatures::KPHB,
            EvalFeatures::KOH,
            EvalFeatures::KOG,
            EvalFeatures::KT,
            EvalFeatures::KTA,
            EvalFeatures::KTB,
            EvalFeatures::KTC,
            EvalFeatures::KM,
            EvalFeatures::KN,
        ] {
            assert!(!f.retreat_opponent_threat && !f.retreat_own_threat, "{f:?}");
        }
    }

    #[test]
    fn c2_pin_the_shortfall_is_the_engines_retreat_arithmetic() {
        // TIMING.md's pin, as N2's pinned its bonus against modify_damage: on boards with Goo-zooka's effect, Peculiar
        // Plaza, Trap Territory, Small Balloon, Inflatable Boat and Bombirdier, for every Energy count on the Active,
        // C2's shortfall for a benched threat ready now (missing 0, the owner to move) is the fewest Energy the engine
        // needs added to the Active before it offers a Retreat. The pin reads the cost arithmetic alone, so Goo-zooka's
        // effect here has 9 turns left and is live on any turn the retreat can come (with 1 turn left, a retreat that
        // itself waits for attachments would come after it expires: that timing is the next test's).
        let goo = |card: PlayedCard| {
            let mut card = card;
            card.add_effect(CardEffect::IncreasedRetreatCost { amount: 1 }, 9);
            card
        };
        let bench = || mon(CardId::A1129MewtwoEx);
        let other = || vec![mon(CardId::A1183Dratini)];
        let tool = |id: CardId, t: CardId| mon(id).with_tool(get_card_by_enum(t));
        let boards: Vec<(&str, State, usize)> = vec![
            ("printed", position(vec![mon(CardId::A1143Machop), bench()], other(), None), 2),
            ("Goo-zooka", position(vec![goo(mon(CardId::A1143Machop)), bench()], other(), None), 3),
            (
                "Trap Territory",
                position(vec![mon(CardId::A1143Machop), bench()], vec![mon(CardId::A1183Dratini), mon(CardId::B1a006Ariados)], None),
                3,
            ),
            ("Plaza, a [P] Active", position(vec![mon(CardId::A1129MewtwoEx), bench()], other(), Some(CardId::B2155PeculiarPlaza)), 0),
            ("Plaza, a non-[P] Active", position(vec![mon(CardId::A1143Machop), bench()], other(), Some(CardId::B2155PeculiarPlaza)), 2),
            (
                "Small Balloon",
                position(vec![tool(CardId::A1143Machop, CardId::B3b064SmallBalloon), bench()], other(), None),
                1,
            ),
            (
                "Inflatable Boat",
                position(vec![tool(CardId::A4a020SuicuneEx, CardId::A4a067InflatableBoat), bench()], other(), None),
                1,
            ),
            ("Bombirdier", position(vec![mon(CardId::B2b040Darkrai), mon(CardId::B3115Bombirdier)], other(), None), 1),
            (
                "Goo-zooka, Trap Territory and Small Balloon",
                position(
                    vec![goo(tool(CardId::A1143Machop, CardId::B3b064SmallBalloon)), bench()],
                    vec![mon(CardId::A1183Dratini), mon(CardId::B1a006Ariados)],
                    None,
                ),
                3,
            ),
        ];
        for (label, board, cost) in boards {
            for energy in 0..=cost + 1 {
                let mut state = board.clone();
                state.get_active_mut(0).attached_energy = vec![EnergyType::Fighting; energy];
                let engine = engine_shortfall(&state).expect("a Retreat is offered");
                assert_eq!(engine, cost.saturating_sub(energy), "{label}, {energy} Energy: the engine's cost");
                assert_eq!(benched_retreat_shortfall(&state, 0, 0), engine, "{label}, {energy} Energy");
            }
        }
        // An Active that can't retreat at all is left as today (a stated limit): Asleep, the engine offers no Retreat,
        // and C2 charges nothing.
        let asleep = position(
            vec![mon(CardId::A1143Machop).with_status_condition(StatusCondition::Asleep), bench()],
            other(),
            None,
        );
        assert_eq!(engine_shortfall(&asleep), None);
        assert_eq!(benched_retreat_shortfall(&asleep, 0, 0), 0);
    }

    #[test]
    fn c2_counts_a_raised_cost_only_while_it_is_live_when_the_threat_would_attack() {
        // Player 1's Active Dratini (cost 1) holds 1 Energy and carries Goo-zooka's effect, played on player 0's turn 5
        // with 1 turn left: live through turn 6, player 1's next turn. A benched threat that would attack on turn 6
        // (missing 0 or 1, with that turn's attachment) pays the raised cost: 1 more. One that would attack on turn 8
        // or later doesn't. An effect with 3 turns left (live through turn 8) counts for a threat attacking on 8.
        let with = |turns_left: u8| {
            let mut dratini = mon(CardId::A1183Dratini).with_energy(vec![EnergyType::Psychic]);
            dratini.add_effect(CardEffect::IncreasedRetreatCost { amount: 1 }, turns_left);
            position(vec![mon(CardId::A1143Machop)], vec![dratini, mon(CardId::A1129MewtwoEx)], None)
        };
        let without = position(
            vec![mon(CardId::A1143Machop)],
            vec![mon(CardId::A1183Dratini).with_energy(vec![EnergyType::Psychic]), mon(CardId::A1129MewtwoEx)],
            None,
        );
        for missing in 0..4 {
            assert_eq!(benched_retreat_shortfall(&without, 1, missing), 0, "no effect, missing {missing}");
        }
        assert_eq!(benched_retreat_shortfall(&with(1), 1, 0), 1);
        assert_eq!(benched_retreat_shortfall(&with(1), 1, 1), 1);
        assert_eq!(benched_retreat_shortfall(&with(1), 1, 2), 0, "attacks on turn 8: the effect is gone");
        assert_eq!(benched_retreat_shortfall(&with(1), 1, 3), 0);
        assert_eq!(benched_retreat_shortfall(&with(3), 1, 2), 1, "live through turn 8");
        assert_eq!(benched_retreat_shortfall(&with(3), 1, 3), 0, "attacks on turn 10");
    }

    /// km's clock for `victim_owner`'s side (the other side's threats), with C2 on or off, as kt_clocks runs it.
    fn clock(state: &State, victim_owner: usize, c2: bool) -> KtClock {
        kt_clock_c2(state, victim_owner, victim_owner == 1, true, false, true, true, true, c2)
    }

    #[test]
    fn c2_moves_the_clock_only_where_a_benched_threat_waits() {
        // Player 1's Mewtwo ex (1 Psychic: Psychic Sphere 1 short) waits on the Bench behind Dratini (1 Energy, cost 1,
        // Ram [WL] 2 short). km's threat is Mewtwo ex, 1 turn of lead. With Goo-zooka's effect on Dratini (live on turn
        // 6) the retreat costs 2, one more than Dratini holds: C2 adds 1, so 2 turns of lead. Without the effect, or
        // with Mewtwo ex itself in front, C2 changes nothing.
        let mewtwo = || mon(CardId::A1129MewtwoEx).with_energy(vec![EnergyType::Psychic]);
        let dratini = |goo: bool| {
            let mut card = mon(CardId::A1183Dratini).with_energy(vec![EnergyType::Psychic]);
            if goo {
                card.add_effect(CardEffect::IncreasedRetreatCost { amount: 1 }, 1);
            }
            card
        };
        let bot = || vec![mon(CardId::A1143Machop)];
        let waits = position(bot(), vec![dratini(true), mewtwo()], None);
        assert_eq!((clock(&waits, 0, false).lead, clock(&waits, 0, true).lead), (1.0, 2.0));
        assert_eq!(clock(&waits, 0, true).total(0.0) - clock(&waits, 0, false).total(0.0), 1.0);
        let no_effect = position(bot(), vec![dratini(false), mewtwo()], None);
        assert_eq!(clock(&no_effect, 0, true).total(0.0), clock(&no_effect, 0, false).total(0.0));
        let in_front = position(bot(), vec![mewtwo(), dratini(true)], None);
        assert_eq!(clock(&in_front, 0, true).total(0.0), clock(&in_front, 0, false).total(0.0));
        // The bot's own side, the same rule: player 0's Mewtwo ex waits behind Dratini with no Energy (cost 1): 1 more.
        let own = position(vec![mon(CardId::A1183Dratini), mewtwo()], vec![mon(CardId::A1143Machop)], None);
        assert_eq!((clock(&own, 1, false).lead, clock(&own, 1, true).lead), (1.0, 2.0));
    }

    #[test]
    fn on_played_states_kr_and_kro_are_km_with_their_flags_cleared_and_differ_somewhere() {
        // Every position of 10 random games of the scratch pairs, from each player's own view: kr's and kro's values
        // with their flags cleared are km's, bit for bit; in setup kr and kro are km; and both differ from km somewhere.
        let (mut positions, mut kr_differs, mut kro_differs) = (0, 0, 0);
        for (pair, (a, b)) in PAIRS.iter().enumerate() {
            for seed in 0..2u64 {
                let players: Vec<Box<dyn crate::players::Player>> =
                    vec![Box::new(RandomPlayer { deck: deck(a) }), Box::new(RandomPlayer { deck: deck(b) })];
                let mut game = Game::new(players, 20_952_000_000 + 10 * pair as u64 + seed);
                let mut ticks = 0;
                while !game.is_game_over() && ticks < 400 {
                    let state = game.get_state_clone();
                    for me in 0..2 {
                        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
                        let view = observation.visible_state();
                        let km = public_clock_effect_km_value_function(view, me);
                        let (kr, kro) =
                            (public_clock_effect_kr_value_function(view, me), public_clock_effect_kro_value_function(view, me));
                        for f in [EvalFeatures::KR, EvalFeatures::KRO] {
                            let cleared = EvalFeatures { retreat_opponent_threat: false, retreat_own_threat: false, ..f };
                            assert_eq!(value(view, me, cleared), km, "turn {}", view.turn_count);
                        }
                        if view.setup_opponent_hidden {
                            assert_eq!((kr, kro), (km, km), "setup");
                        }
                        positions += 1;
                        kr_differs += (kr != km) as usize;
                        kro_differs += (kro != km) as usize;
                    }
                    game.play_tick();
                    ticks += 1;
                }
            }
        }
        assert!(positions > 500 && kr_differs > 0 && kro_differs > 0, "{positions} positions, {kr_differs} kr, {kro_differs} kro");
    }

    /// One game on `seed`, `players` in seats 0 and 1: every move played, then the points and the winner.
    fn moves(players: Vec<Box<dyn crate::players::Player>>, seed: u64) -> Vec<String> {
        let mut game = Game::new(players, seed);
        let mut out = vec![];
        while !game.is_game_over() && out.len() < 3000 {
            out.push(format!("{:?}", game.play_tick()));
        }
        let state = game.get_state_clone();
        out.push(format!("points {:?} winner {:?}", state.points, state.winner));
        out
    }

    /// kr3 with C2 off: km3's player (as players/mod.rs builds km, kn and kr) on kr's preset with its flags cleared.
    fn kr3_with_c2_off(deck: Deck) -> Box<dyn crate::players::Player> {
        Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: 3,
                write_debug_trees: false,
                value_function: Box::new(|state: &State, myself: usize| {
                    let off = EvalFeatures { retreat_opponent_threat: false, retreat_own_threat: false, ..EvalFeatures::KR };
                    value(state, myself, off)
                }),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        })
    }

    #[test]
    fn kr3_with_c2_off_equals_km3_move_for_move_on_200_scratch_deals() {
        // 200 scratch deals: kn's five scratch pairs, 40 each, on Claude diagnostic seeds 20,953,000,000 + i, the
        // first-named list in seat 0 on even i. km3 against km3 (players/mod.rs, as `deckgym simulate` builds them)
        // and kr3 with C2 off against itself play the same moves, choices and results in every deal. kr3 itself (C2
        // on, from players/mod.rs) differs from km3 in at least one of the first 40, so the lists reach C2.
        let deals: Vec<(Deck, Deck, u64)> = (0..200u64)
            .map(|i| {
                let (a, b) = PAIRS[(i / 40) as usize];
                let (a, b) = if i % 2 == 0 { (deck(a), deck(b)) } else { (deck(b), deck(a)) };
                (a, b, 20_953_000_000 + i)
            })
            .collect();
        let workers = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1).clamp(1, 8);
        let results: Vec<(usize, bool, Option<bool>)> = std::thread::scope(|scope| {
            let handles: Vec<_> = (0..workers)
                .map(|w| {
                    let deals = &deals;
                    scope.spawn(move || {
                        let mut out = vec![];
                        for (i, (a, b, seed)) in deals.iter().enumerate().filter(|(i, _)| i % workers == w) {
                            let km = moves(create_players(a.clone(), b.clone(), vec![PlayerCode::KM { max_depth: 3 }; 2]), *seed);
                            let off = moves(vec![kr3_with_c2_off(a.clone()), kr3_with_c2_off(b.clone())], *seed);
                            let on = (i < 40).then(|| {
                                moves(create_players(a.clone(), b.clone(), vec![PlayerCode::KR { max_depth: 3 }; 2]), *seed) != km
                            });
                            out.push((i, off == km, on));
                        }
                        out
                    })
                })
                .collect();
            handles.into_iter().flat_map(|h| h.join().unwrap()).collect()
        });
        assert_eq!(results.len(), 200);
        let differ: Vec<usize> = results.iter().filter(|r| !r.1).map(|r| r.0).collect();
        assert!(differ.is_empty(), "kr3 with C2 off differs from km3 on deals {differ:?}");
        assert!(results.iter().any(|r| r.2 == Some(true)), "kr3 plays as km3 on all of the first 40 deals");
    }
}
