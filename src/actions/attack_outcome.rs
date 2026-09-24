use std::rc::Rc;

use rand::rngs::StdRng;

use crate::effects::CardEffect;
use crate::hooks::{modify_damage, DamageModifierContext};
use crate::State;

use super::apply_action_helpers::{
    apply_survive_knockout_turn_effects, guts_would_flip, handle_attack_retaliation,
    handle_damage_only, handle_knockouts, Mutation, Probabilities,
};
use super::outcomes::{
    generate_sequences_with_heads, saturated_geometric_classes, CoinConditionError, CoinPaths,
    CoinSeq, ForecastBuildError, Outcomes,
};
use super::{Action, SimpleAction};

/// A single damage target described as plain data: `(amount, is_opponent_target, in_play_idx)`.
/// `is_opponent_target` indicates whether `in_play_idx` refers to a slot on the attacker's
/// opponent's side (true) or the attacker's own side (false). The amount is the *raw*
/// pre-modifier damage; weakness/Giovanni/etc. are applied at resolution time via `modify_damage`.
pub type DamageTarget = (u32, bool, usize);

/// A reusable (multi-call) effect closure. Effects are stored as `Rc<dyn Fn>` rather than the
/// `FnOnce` `Mutation` so that an `AttackOutcome` can be cloned — which the defender
/// damage-prevention transform needs in order to split one branch into a heads variant
/// (active damage prevented) and a tails variant (full damage), both running the same effect.
type SharedEffect = Rc<dyn Fn(&mut StdRng, &mut State, &Action)>;

/// The structured result of (one branch of) an attack: the damage it deals, carried as data,
/// plus the non-damage effects that run before and/or after damage is applied.
///
/// Keeping damage out of the effect closures lets us (a) prevent only the active Pokémon's
/// damage on a defender's coin flip while still running effects, and (b) compute expected
/// damage by inspection without executing any closures.
#[derive(Clone)]
pub struct AttackOutcome {
    /// Damage targets dealt by this outcome (raw, pre-modifier).
    pub damage: Vec<DamageTarget>,
    /// Effect that runs before damage is applied (e.g. discard the defender's tool so that
    /// damage modifiers see the post-discard board).
    pre_damage_effect: Option<SharedEffect>,
    /// Effect that runs after damage is applied (the common case: status, energy moves, etc.).
    post_damage_effect: Option<SharedEffect>,
}

impl AttackOutcome {
    /// An outcome that does nothing (no damage, no effect).
    pub fn noop() -> Self {
        Self {
            damage: vec![],
            pre_damage_effect: None,
            post_damage_effect: None,
        }
    }

    /// Damage-only outcome.
    pub fn damage(targets: Vec<DamageTarget>) -> Self {
        Self {
            damage: targets,
            pre_damage_effect: None,
            post_damage_effect: None,
        }
    }

    /// Damage plus a post-damage effect.
    pub fn damage_then_effect<F>(targets: Vec<DamageTarget>, effect: F) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self {
            damage: targets,
            pre_damage_effect: None,
            post_damage_effect: Some(Rc::new(effect)),
        }
    }

    /// A pre-damage effect followed by damage (effect resolves before damage modifiers).
    pub fn effect_then_damage<F>(effect: F, targets: Vec<DamageTarget>) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self {
            damage: targets,
            pre_damage_effect: Some(Rc::new(effect)),
            post_damage_effect: None,
        }
    }

    /// A pre-damage effect, followed by damage, followed by a post-damage effect.
    pub fn effect_then_damage_then_effect<F, G>(
        before_damage: F,
        targets: Vec<DamageTarget>,
        after_damage: G,
    ) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
        G: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self {
            damage: targets,
            pre_damage_effect: Some(Rc::new(before_damage)),
            post_damage_effect: Some(Rc::new(after_damage)),
        }
    }

    /// An effect-only outcome that deals no Pokémon damage of its own.
    pub fn effect_only<F>(effect: F) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self {
            damage: vec![],
            pre_damage_effect: None,
            post_damage_effect: Some(Rc::new(effect)),
        }
    }

    /// Resolve `is_opponent_target` into concrete player indices for the acting player.
    fn resolved_targets(&self, actor: usize) -> Vec<(u32, usize, usize)> {
        let opponent = (actor + 1) % 2;
        self.damage
            .iter()
            .map(|(amount, is_opponent, idx)| {
                let target_player = if *is_opponent { opponent } else { actor };
                (*amount, target_player, *idx)
            })
            .collect()
    }

    /// Convert this structured outcome into a `Mutation` that applies it to the state:
    /// pre-effect, then damage (with modifiers/counterattacks), then post-effect, then knockouts.
    fn into_mutation(self) -> Mutation {
        Box::new(move |rng, state, action| {
            let attacking_ref = (action.actor, 0);
            let resolved = self.resolved_targets(action.actor);

            if let Some(pre) = &self.pre_damage_effect {
                pre(rng, state, action);
            }

            let mut damaged_actives = Vec::new();
            if !resolved.is_empty() {
                let attack_metadata = attack_metadata_from_action(state, action);
                damaged_actives = handle_damage_only(
                    state,
                    attacking_ref,
                    &resolved,
                    true,
                    DamageModifierContext {
                        attack_name: attack_metadata.name.as_deref(),
                        attack_effect: attack_metadata.effect.as_deref(),
                    },
                );
                // Hala-style survival changes a would-be knockout into 10 HP before the
                // attack's own switch or other post-damage choices are exposed.
                apply_survive_knockout_turn_effects(state);
            }

            // Keep a reaction continuation below any choices created by the attack effect. The
            // reference-bearing frame is installed before the effect runs so an immediate switch
            // can remap it through `apply_activate` as well.
            let reaction_stack_base = state.move_generation_stack.len();
            if !resolved.is_empty() {
                state.move_generation_stack.insert(
                    reaction_stack_base,
                    (
                        action.actor,
                        vec![SimpleAction::ResolveAttackRetaliation {
                            attacking_ref,
                            damaged_refs: damaged_actives.clone(),
                            perish_body_heads: false,
                            point_denial_flips: vec![],
                        }],
                    ),
                );
            }

            if let Some(post) = &self.post_damage_effect {
                post(rng, state, action);
            }

            let retaliation_deferred = !resolved.is_empty()
                && state.move_generation_stack.len() > reaction_stack_base + 1;
            if !resolved.is_empty() && !retaliation_deferred {
                let (_, choices) = state.move_generation_stack.remove(reaction_stack_base);
                let [SimpleAction::ResolveAttackRetaliation {
                    attacking_ref,
                    damaged_refs,
                    perish_body_heads,
                    point_denial_flips,
                }] = choices.as_slice()
                else {
                    unreachable!("the immediate attack-reaction frame must remain intact")
                };
                handle_attack_retaliation(state, *attacking_ref, damaged_refs);
                if *perish_body_heads {
                    apply_perish_body_retaliation(state, *attacking_ref, damaged_refs);
                }
                apply_point_denial_results(state, point_denial_flips);
            }

            // Only resolve knockouts here when this outcome dealt damage. Pure-effect outcomes
            // rely on the catch-all knockout pass in `wrap_with_common_logic`, matching the
            // historical behavior of effect-only outcomes.
            if !resolved.is_empty() && !retaliation_deferred {
                handle_knockouts(state, attacking_ref, true);
            }
        })
    }
}

/// A probability distribution over `AttackOutcome`s, mirroring `Outcomes` but with damage
/// carried as data. Built by the attack mechanic helpers and converted to `Outcomes` at the
/// boundary of `forecast_attack`/`forecast_copied_attack`.
pub struct AttackOutcomes {
    branches: Vec<AttackBranch>,
}

struct AttackBranch {
    probability: f64,
    outcome: AttackOutcome,
    coin_paths: CoinPaths,
}

impl AttackOutcomes {
    pub fn single(outcome: AttackOutcome) -> Self {
        Self {
            branches: vec![AttackBranch {
                probability: 1.0,
                outcome,
                coin_paths: CoinPaths::None,
            }],
        }
    }

    /// A single effect-only outcome (no damage). Analogous to `Outcomes::single_fn`.
    pub fn single_effect<F>(effect: F) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self::single(AttackOutcome::effect_only(effect))
    }

    pub fn from_parts(probabilities: Probabilities, outcomes: Vec<AttackOutcome>) -> Self {
        assert_eq!(
            probabilities.len(),
            outcomes.len(),
            "from_parts length mismatch: probabilities={} outcomes={}",
            probabilities.len(),
            outcomes.len()
        );
        let branches = probabilities
            .into_iter()
            .zip(outcomes)
            .map(|(probability, outcome)| AttackBranch {
                probability,
                outcome,
                coin_paths: CoinPaths::None,
            })
            .collect();
        Self { branches }
    }

    pub fn binary_coin(heads: AttackOutcome, tails: AttackOutcome) -> Self {
        Self {
            branches: vec![
                AttackBranch {
                    probability: 0.5,
                    outcome: heads,
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![true])]),
                },
                AttackBranch {
                    probability: 0.5,
                    outcome: tails,
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![false])]),
                },
            ],
        }
    }

    /// A binary coin whose heads and/or tails result has additional finite random successors.
    /// Heads remain before tails, matching [`Self::binary_coin`]'s established branch order.
    pub(crate) fn binary_coin_weighted(
        heads: Vec<(f64, AttackOutcome)>,
        tails: Vec<(f64, AttackOutcome)>,
    ) -> Result<Self, ForecastBuildError> {
        let mut branches = Vec::new();
        for (refinements, face) in [(heads, true), (tails, false)] {
            if refinements.is_empty() {
                return Err(ForecastBuildError::EmptyBranches);
            }
            let conditional_sum = refinements
                .iter()
                .map(|(probability, _)| *probability)
                .sum::<f64>();
            if refinements.iter().any(|(probability, _)| {
                !probability.is_finite() || *probability <= 0.0 || *probability > 1.0
            }) {
                return Err(ForecastBuildError::ProbabilityOutOfRange);
            }
            if !conditional_sum.is_finite() || (conditional_sum - 1.0).abs() > 1e-9 {
                return Err(ForecastBuildError::ProbabilitySumInvalid);
            }
            for (probability, outcome) in refinements {
                let combined = 0.5 * probability;
                if !combined.is_finite() || combined <= 0.0 {
                    return Err(ForecastBuildError::ProbabilityOutOfRange);
                }
                branches.push(AttackBranch {
                    probability: combined,
                    outcome,
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![face])]),
                });
            }
        }
        Ok(Self { branches })
    }

    pub fn from_coin_branches(branches: Vec<(f64, AttackOutcome, Vec<CoinSeq>)>) -> Self {
        let branches = branches
            .into_iter()
            .map(|(probability, outcome, sequences)| AttackBranch {
                probability,
                outcome,
                coin_paths: CoinPaths::Exact(sequences),
            })
            .collect();
        Self { branches }
    }

    pub fn binomial_by_heads(
        flips: usize,
        mut make_outcome: impl FnMut(usize) -> AttackOutcome,
    ) -> Self {
        let denominator = 2_usize.pow(flips as u32) as f64;
        let mut branches: Vec<(f64, AttackOutcome, Vec<CoinSeq>)> = vec![];
        for heads in 0..=flips {
            let probability = Outcomes::binomial_coefficient(flips, heads) as f64 / denominator;
            let sequences = generate_sequences_with_heads(flips, heads)
                .into_iter()
                .map(CoinSeq)
                .collect::<Vec<_>>();
            branches.push((probability, make_outcome(heads), sequences));
        }
        Self::from_coin_branches(branches)
    }

    /// Binomial coin classes whose effect has additional finite random successors.
    ///
    /// Each conditional distribution refines one heads-count class without changing the
    /// concrete coin paths carried by that class. This keeps acting-player coin provenance
    /// available to Will and Victory Star while separately pricing a non-coin random effect.
    pub(crate) fn binomial_by_heads_weighted(
        flips: usize,
        mut make_outcomes: impl FnMut(usize) -> Vec<(f64, AttackOutcome)>,
    ) -> Result<Self, ForecastBuildError> {
        let denominator = 2_usize.pow(flips as u32) as f64;
        let mut branches = Vec::new();
        for heads in 0..=flips {
            let coin_probability = Outcomes::binomial_coefficient(flips, heads) as f64 / denominator;
            let coin_paths = CoinPaths::Exact(
                generate_sequences_with_heads(flips, heads)
                    .into_iter()
                    .map(CoinSeq)
                    .collect(),
            );
            let refinements = make_outcomes(heads);
            if refinements.is_empty() {
                return Err(ForecastBuildError::EmptyBranches);
            }
            let conditional_sum = refinements
                .iter()
                .map(|(probability, _)| *probability)
                .sum::<f64>();
            if refinements.iter().any(|(probability, _)| {
                !probability.is_finite() || *probability <= 0.0 || *probability > 1.0
            }) {
                return Err(ForecastBuildError::ProbabilityOutOfRange);
            }
            if !conditional_sum.is_finite() || (conditional_sum - 1.0).abs() > 1e-9 {
                return Err(ForecastBuildError::ProbabilitySumInvalid);
            }
            for (probability, outcome) in refinements {
                let combined = coin_probability * probability;
                if !combined.is_finite() || combined <= 0.0 {
                    return Err(ForecastBuildError::ProbabilityOutOfRange);
                }
                branches.push(AttackBranch {
                    probability: combined,
                    outcome,
                    coin_paths: coin_paths.clone(),
                });
            }
        }
        Ok(Self { branches })
    }

    /// Legacy finite helper. Its final branch is an unterminated all-heads path, making
    /// `max_heads` a gameplay cap. Existing mechanics retain it until their saturation points
    /// are proven; new exact mechanics should use `geometric_until_tails_saturated`.
    pub fn geometric_until_tails(
        max_heads: usize,
        mut make_outcome: impl FnMut(usize) -> AttackOutcome,
    ) -> Self {
        let mut branches: Vec<(f64, AttackOutcome, Vec<CoinSeq>)> = vec![];
        for heads in 0..=max_heads {
            let mut sequence = vec![true; heads];
            let probability = if heads < max_heads {
                sequence.push(false);
                0.5_f64.powi((heads + 1) as i32)
            } else {
                0.5_f64.powi(heads as i32)
            };
            branches.push((probability, make_outcome(heads), vec![CoinSeq(sequence)]));
        }
        Self::from_coin_branches(branches)
    }

    /// Exact successor-state distribution for a geometric attack effect whose structured
    /// outcome is identical after `saturation_heads`.
    #[allow(dead_code)] // Primitive lands before the first card-specific saturation proof.
    pub fn geometric_until_tails_saturated(
        saturation_heads: usize,
        mut make_outcome: impl FnMut(usize) -> AttackOutcome,
    ) -> Result<Self, ForecastBuildError> {
        let branches = saturated_geometric_classes(saturation_heads)?
            .into_iter()
            .map(|(probability, heads, coin_paths)| AttackBranch {
                probability,
                outcome: make_outcome(heads),
                coin_paths,
            })
            .collect();
        Ok(Self { branches })
    }

    /// Exact geometric classes whose effect has additional finite random successors.
    ///
    /// `make_outcomes(heads)` returns the conditional distribution after that coin class. Each
    /// conditional probability must be positive and finite and the returned probabilities must
    /// sum to one. Every refined successor retains the source class's coin-path evidence; this
    /// lets Victory Star expose only the coin batch and defer the secondary random result until
    /// Keep/Reroll commits it.
    pub(crate) fn geometric_until_tails_saturated_weighted(
        saturation_heads: usize,
        mut make_outcomes: impl FnMut(usize) -> Vec<(f64, AttackOutcome)>,
    ) -> Result<Self, ForecastBuildError> {
        let mut branches = Vec::new();
        for (coin_probability, heads, coin_paths) in saturated_geometric_classes(saturation_heads)?
        {
            let refinements = make_outcomes(heads);
            if refinements.is_empty() {
                return Err(ForecastBuildError::EmptyBranches);
            }
            let conditional_sum = refinements
                .iter()
                .map(|(probability, _)| *probability)
                .sum::<f64>();
            if refinements.iter().any(|(probability, _)| {
                !probability.is_finite() || *probability <= 0.0 || *probability > 1.0
            }) {
                return Err(ForecastBuildError::ProbabilityOutOfRange);
            }
            if !conditional_sum.is_finite() || (conditional_sum - 1.0).abs() > 1e-9 {
                return Err(ForecastBuildError::ProbabilitySumInvalid);
            }
            for (probability, outcome) in refinements {
                let combined = coin_probability * probability;
                if !combined.is_finite() || combined <= 0.0 {
                    return Err(ForecastBuildError::ProbabilityOutOfRange);
                }
                branches.push(AttackBranch {
                    probability: combined,
                    outcome,
                    coin_paths: coin_paths.clone(),
                });
            }
        }
        Ok(Self { branches })
    }

    /// Adapter for effect-only producers that already return an `Outcomes` (e.g. the shared
    /// search/bench helpers). Each branch's `Mutation` becomes a post-damage effect with no
    /// structured damage, preserving probabilities and coin metadata.
    pub fn from_effect_outcomes(outcomes: Outcomes) -> Self {
        let branches = outcomes
            .into_branches_with_coin_paths()
            .into_iter()
            .map(|(probability, mutation, coin_paths)| {
                // Wrap the FnOnce mutation in an Rc<RefCell<Option<..>>> so it can be stored
                // as a (nominally reusable) SharedEffect. Effect-only outcomes are never
                // duplicated by the prevention transform, so it is only ever invoked once.
                let cell = std::cell::RefCell::new(Some(mutation));
                let effect: SharedEffect = Rc::new(move |rng, state, action| {
                    if let Some(m) = cell.borrow_mut().take() {
                        m(rng, state, action);
                    }
                });
                AttackBranch {
                    probability,
                    outcome: AttackOutcome {
                        damage: vec![],
                        pre_damage_effect: None,
                        post_damage_effect: Some(effect),
                    },
                    coin_paths,
                }
            })
            .collect();
        Self { branches }
    }

    /// Prepend a nullifying 0.5 gate (heads = the whole attack does nothing), scaling the base
    /// branches by 0.5. Used for confusion and CoinFlipToBlockAttack. Coin metadata is dropped
    /// (these are not card-effect coins owned by the acting player).
    pub fn prepend_nullifying_coin_gate(self) -> Self {
        let mut branches = vec![AttackBranch {
            probability: 0.5,
            outcome: AttackOutcome::noop(),
            coin_paths: CoinPaths::None,
        }];
        for branch in self.branches {
            branches.push(AttackBranch {
                probability: branch.probability * 0.5,
                outcome: branch.outcome,
                coin_paths: CoinPaths::None,
            });
        }
        Self { branches }
    }

    /// Apply the defender's "if any damage is done to this Pokémon by attacks, flip a coin; if
    /// heads, prevent that damage / this Pokémon takes -X damage from that attack" ability
    /// (e.g. Meowth's Carefree Steps, Bastiodon's Guarded Grill, Hisuian Goodra's Securely
    /// Sheltered) to each opponent in-play slot in `reductions`. Each entry pairs the slot index
    /// with the amount subtracted on heads — use `u32::MAX` for full prevention.
    ///
    /// The ability applies independently to each such Pokémon — whether Active or Benched — and
    /// only when it actually takes damage in a given branch. Each branch is therefore split into
    /// `2^k` sub-branches (where `k` is the number of those Pokémon taking damage in that branch),
    /// one per combination of heads/tails, reducing (saturating at 0, at which point the damage
    /// entry is removed) the damage to the Pokémon whose coin came up heads while keeping all
    /// other damage and all effects. Existing metadata is preserved unchanged: it describes the
    /// acting player's earlier attack-effect coins, while these defender coins stay unlabelled.
    pub fn split_with_damage_prevention(self, reductions: &[(usize, u32)]) -> Self {
        let mut branches = vec![];
        for branch in self.branches {
            // Only the protected Pokémon that actually take (>0) opponent damage flip a coin.
            let flipping: Vec<(usize, u32)> = reductions
                .iter()
                .copied()
                .filter(|(target_idx, _)| {
                    branch
                        .outcome
                        .damage
                        .iter()
                        .any(|(amount, is_opponent, idx)| {
                            *is_opponent && idx == target_idx && *amount > 0
                        })
                })
                .collect();

            if flipping.is_empty() {
                branches.push(branch);
                continue;
            }

            let combos = 1usize << flipping.len();
            let sub_probability = branch.probability / combos as f64;
            for mask in 0..combos {
                // The subset of flipping Pokémon whose coin came up heads (damage reduced).
                let reduced_now: Vec<(usize, u32)> = flipping
                    .iter()
                    .enumerate()
                    .filter(|(bit, _)| (mask >> bit) & 1 == 1)
                    .map(|(_, pair)| *pair)
                    .collect();
                let mut outcome = branch.outcome.clone();
                outcome.damage = outcome
                    .damage
                    .into_iter()
                    .filter_map(|(amount, is_opponent, idx)| {
                        if is_opponent {
                            if let Some((_, reduction)) =
                                reduced_now.iter().find(|(r_idx, _)| *r_idx == idx)
                            {
                                let reduced = amount.saturating_sub(*reduction);
                                return (reduced > 0).then_some((reduced, is_opponent, idx));
                            }
                        }
                        Some((amount, is_opponent, idx))
                    })
                    .collect();
                branches.push(AttackBranch {
                    probability: sub_probability,
                    outcome,
                    coin_paths: branch.coin_paths.clone(),
                });
            }
        }
        Self { branches }
    }

    /// Apply the defender's "if this Pokémon would be Knocked Out by damage from an attack,
    /// flip a coin; if heads, it is not Knocked Out and its remaining HP becomes 10" ability
    /// (e.g. Ursaluna's Guts) to each opponent in-play slot in `guts_indices`.
    ///
    /// The ability applies independently to each such Pokémon, and only in branches where the
    /// (modified) damage it takes would knock it out. Each such branch is split into `2^k`
    /// sub-branches, one per combination of heads/tails. On heads the damage still applies in
    /// full — so on-damage triggers like Rocky Helmet's counterattack fire normally — and a
    /// post-damage effect then sets the survivor's remaining HP to exactly 10 before knockouts
    /// are resolved. Existing acting-player coin metadata is copied unchanged; the Guts coin is
    /// deliberately not added to it.
    ///
    /// Knock outs are forecast with the pre-attack board (like `expected_damage_to`), so damage
    /// modifiers changed by a branch's own pre-damage effect are not taken into account.
    pub fn split_with_guts_survival(
        self,
        state: &State,
        acting_player: usize,
        attack_name: Option<&str>,
        attack_effect: Option<&str>,
        guts_indices: &[usize],
    ) -> Self {
        let opponent = (acting_player + 1) % 2;
        let mut branches = vec![];
        for branch in self.branches {
            // Only the Guts Pokémon that would be knocked out by this branch's damage flip a coin.
            let flipping: Vec<usize> = guts_indices
                .iter()
                .copied()
                .filter(|target_idx| {
                    let raw_total: u32 = branch
                        .outcome
                        .damage
                        .iter()
                        .filter(|(_, is_opponent, idx)| *is_opponent && idx == target_idx)
                        .map(|(amount, _, _)| *amount)
                        .sum();
                    guts_would_flip(
                        state,
                        (acting_player, 0),
                        raw_total,
                        (opponent, *target_idx),
                        true,
                        DamageModifierContext {
                            attack_name,
                            attack_effect,
                        },
                    )
                })
                .collect();

            if flipping.is_empty() {
                branches.push(branch);
                continue;
            }

            let combos = 1usize << flipping.len();
            let sub_probability = branch.probability / combos as f64;
            for mask in 0..combos {
                // The subset of flipping Pokémon whose coin came up heads (survive at 10 HP).
                let survivors: Vec<usize> = flipping
                    .iter()
                    .enumerate()
                    .filter(|(bit, _)| (mask >> bit) & 1 == 1)
                    .map(|(_, idx)| *idx)
                    .collect();
                let mut outcome = branch.outcome.clone();
                if !survivors.is_empty() {
                    let previous_post = outcome.post_damage_effect.take();
                    outcome.post_damage_effect = Some(Rc::new(move |rng, state, action| {
                        let opponent = (action.actor + 1) % 2;
                        for idx in &survivors {
                            if let Some(pokemon) = state.in_play_pokemon[opponent][*idx].as_mut() {
                                pokemon.set_remaining_hp(10);
                            }
                        }
                        if let Some(post) = &previous_post {
                            post(rng, state, action);
                        }
                    }));
                }
                branches.push(AttackBranch {
                    probability: sub_probability,
                    outcome,
                    coin_paths: branch.coin_paths.clone(),
                });
            }
        }
        Self { branches }
    }

    /// Apply the defender's "when this Pokémon is Knocked Out, flip a coin; if heads, your
    /// opponent can't get any points for it" ability (Dusknoir's Fade into Darkness, Glimmora's
    /// Shattering Crystal) to each opponent in-play slot in `denial_indices`.
    ///
    /// Structurally a sibling of [`Self::split_with_guts_survival`], with one important
    /// difference: this coin does not change whether the Pokémon dies, only whether the knockout
    /// scores. The branch records the coin result on the attack's reaction continuation. After
    /// every attack-effect choice resolves, that continuation rechecks the remapped defender and
    /// tags it with `CardEffect::DenyKnockoutPoints` on heads before knockout scoring.
    ///
    /// Splitting at forecast time rather than flipping inline during knockout resolution is what
    /// lets the search bots price the ability: a Glimmora in front of a lethal attack is a real
    /// 50/50 on whether the attacker banks a point, and e2/e3 need to see both branches to value
    /// it. Knockouts are forecast against the pre-attack board, matching
    /// `split_with_guts_survival`.
    pub fn split_with_point_denial(
        self,
        state: &State,
        acting_player: usize,
        attack_name: Option<&str>,
        attack_effect: Option<&str>,
        denial_indices: &[usize],
    ) -> Self {
        let opponent = (acting_player + 1) % 2;
        let mut branches = vec![];
        for branch in self.branches {
            // Only Pokémon this branch's damage would actually knock out flip a coin.
            let flipping: Vec<usize> = denial_indices
                .iter()
                .copied()
                .filter(|target_idx| {
                    let raw_total: u32 = branch
                        .outcome
                        .damage
                        .iter()
                        .filter(|(_, is_opponent, idx)| *is_opponent && idx == target_idx)
                        .map(|(amount, _, _)| *amount)
                        .sum();
                    would_knock_out(
                        state,
                        acting_player,
                        (opponent, *target_idx),
                        raw_total,
                        attack_name,
                        attack_effect,
                    )
                })
                .collect();

            if flipping.is_empty() {
                branches.push(branch);
                continue;
            }

            let combos = 1usize << flipping.len();
            let sub_probability = branch.probability / combos as f64;
            for mask in 0..combos {
                let flips: Vec<(usize, bool)> = flipping.iter().enumerate()
                    .map(|(bit, idx)| (*idx, (mask >> bit) & 1 == 1)).collect();
                let mut outcome = branch.outcome.clone();
                let previous_post = outcome.post_damage_effect.take();
                outcome.post_damage_effect = Some(Rc::new(move |rng, state, action| {
                    let opponent = 1 - action.actor;
                    let resolved_flips: Vec<((usize, usize), bool)> = flips
                        .iter()
                        .map(|&(idx, heads)| ((opponent, idx), heads))
                        .collect();
                    if let Some(SimpleAction::ResolveAttackRetaliation {
                        point_denial_flips,
                        ..
                    }) = state
                        .move_generation_stack
                        .iter_mut()
                        .rev()
                        .flat_map(|(_, choices)| choices.iter_mut().rev())
                        .find(|choice| {
                            matches!(choice, SimpleAction::ResolveAttackRetaliation { .. })
                        })
                    {
                        point_denial_flips.extend(resolved_flips);
                    } else {
                        let stack_base = state.move_generation_stack.len();
                        state.move_generation_stack.insert(
                            stack_base,
                            (
                                action.actor,
                                vec![SimpleAction::ResolveAttackRetaliation {
                                    attacking_ref: (action.actor, 0),
                                    damaged_refs: vec![],
                                    perish_body_heads: false,
                                    point_denial_flips: resolved_flips,
                                }],
                            ),
                        );
                    }
                    // Store the original references before the attack effect runs. An immediate
                    // switch then remaps the denial source through the already-installed frame.
                    if let Some(post) = &previous_post {
                        post(rng, state, action);
                    }
                }));
                branches.push(AttackBranch {
                    probability: sub_probability,
                    outcome,
                    coin_paths: branch.coin_paths.clone(),
                });
            }
        }
        Self { branches }
    }

    /// Apply the defender's "if this Pokémon is in the Active Spot and is Knocked Out by damage
    /// from an attack from your opponent's Pokémon, flip a coin; if heads, the Attacking Pokémon is
    /// Knocked Out" ability (Galarian Cursola's Perish Body).
    ///
    /// The third member of the `split_with_guts_survival` / `split_with_point_denial` family, and
    /// like them it splits at forecast time so the search bots price the coin instead of averaging
    /// it away — trading a lethal hit for a 50/50 on your own attacker is exactly the kind of
    /// decision e2/e3 need to see both sides of. Two differences from its siblings:
    ///
    /// - It only ever applies to the defender's Active Spot (the Ability says so), so it takes no
    ///   list of indices.
    /// - On heads the branch marks the attack's reaction continuation. After every attack-effect
    ///   choice resolves, that continuation rechecks the referenced defender's knockout and live
    ///   Ability before zeroing the referenced attacker's HP. The shared knockout pass then
    ///   resolves both knockouts in one attack-scoped wave.
    ///
    /// Knockouts are forecast against the pre-attack board, matching both siblings. Existing
    /// acting-player coin metadata is copied unchanged; the defender's coin is not added to it.
    pub fn split_with_attacker_knockout(
        self,
        state: &State,
        acting_player: usize,
        attack_name: Option<&str>,
        attack_effect: Option<&str>,
    ) -> Self {
        let opponent = (acting_player + 1) % 2;
        let mut branches = vec![];
        for branch in self.branches {
            let raw_total: u32 = branch
                .outcome
                .damage
                .iter()
                .filter(|(_, is_opponent, idx)| *is_opponent && *idx == 0)
                .map(|(amount, _, _)| *amount)
                .sum();
            if !would_knock_out(
                state,
                acting_player,
                (opponent, 0),
                raw_total,
                attack_name,
                attack_effect,
            ) {
                branches.push(branch);
                continue;
            }

            let sub_probability = branch.probability / 2.0;
            for heads in [true, false] {
                let mut outcome = branch.outcome.clone();
                if heads {
                    let previous_post = outcome.post_damage_effect.take();
                    outcome.post_damage_effect = Some(Rc::new(move |rng, state, action| {
                        if let Some(post) = &previous_post {
                            post(rng, state, action);
                        }
                        // The generic reaction frame sits below every choice the attack effect
                        // just created. Record this branch's heads result there so Perish Body
                        // follows both original Pokémon through any later switch.
                        if let Some(SimpleAction::ResolveAttackRetaliation {
                            perish_body_heads,
                            ..
                        }) = state
                            .move_generation_stack
                            .iter_mut()
                            .rev()
                            .flat_map(|(_, choices)| choices.iter_mut().rev())
                            .find(|choice| {
                                matches!(choice, SimpleAction::ResolveAttackRetaliation { .. })
                            })
                        {
                            *perish_body_heads = true;
                        }
                    }));
                }
                branches.push(AttackBranch {
                    probability: sub_probability,
                    outcome,
                    coin_paths: branch.coin_paths.clone(),
                });
            }
        }
        Self { branches }
    }

    /// Expected raw+modified damage dealt to a specific target across all branches, computed
    /// purely by inspecting branch data (no closures are executed, no RNG is consumed).
    ///
    /// `attack_name` should be the title of the attack being forecast (used by attack-name
    /// specific damage modifiers).
    ///
    /// This is a public lookup API for callers (e.g. bots/value functions) that want the expected
    /// damage of a forecast attack; it is not yet wired into the default engine paths.
    #[allow(dead_code)]
    pub fn expected_damage_to(
        &self,
        state: &State,
        attacking_ref: (usize, usize),
        target_player: usize,
        target_idx: usize,
        attack_name: Option<&str>,
        attack_effect: Option<&str>,
    ) -> f64 {
        let actor = attacking_ref.0;
        let opponent = (actor + 1) % 2;
        self.branches
            .iter()
            .map(|branch| {
                let raw: u32 = branch
                    .outcome
                    .damage
                    .iter()
                    .filter(|(_, is_opponent, idx)| {
                        let player = if *is_opponent { opponent } else { actor };
                        player == target_player && *idx == target_idx
                    })
                    .map(|(amount, _, idx)| {
                        modify_damage(
                            state,
                            attacking_ref,
                            (*amount, target_player, *idx),
                            true,
                            DamageModifierContext {
                                attack_name,
                                attack_effect,
                            },
                        )
                    })
                    .sum();
                branch.probability * raw as f64
            })
            .sum()
    }

    /// Convenience: expected modified damage dealt to the opponent's Active Pokémon.
    #[allow(dead_code)]
    pub fn expected_damage_to_opponent_active(
        &self,
        state: &State,
        acting_player: usize,
        attack_name: Option<&str>,
        attack_effect: Option<&str>,
    ) -> f64 {
        let opponent = (acting_player + 1) % 2;
        self.expected_damage_to(
            state,
            (acting_player, 0),
            opponent,
            0,
            attack_name,
            attack_effect,
        )
    }

    /// Victory Star supports any nonempty exact or symbolic class for the attack's own coin batch.
    /// A concrete member is sampled later with the RNG supplied to the selected mutation.
    pub(crate) fn all_branches_have_coin_paths(&self) -> bool {
        !self.branches.is_empty()
            && self
                .branches
                .iter()
                .all(|branch| branch.coin_paths.has_paths())
    }

    /// Condition on one concrete observed coin path. Multiple successors may share the same
    /// coin class when a card has secondary randomness (for example, random Energy selection).
    pub(crate) fn select_coin_path(self, flips: &[bool]) -> Result<Self, &'static str> {
        let concrete = CoinSeq(flips.to_vec());
        let mut retained = Vec::new();
        let mut malformed_symbolic = false;
        let mut max_log_weight = f64::NEG_INFINITY;
        for branch in self.branches {
            let log_likelihood = match branch.coin_paths.log_likelihood(&concrete) {
                Ok(Some(value)) => value,
                Ok(None) => continue,
                Err(CoinConditionError::InvalidObservedPath) => {
                    malformed_symbolic = true;
                    continue;
                }
                Err(_) => return Err("stored attack coin path has invalid likelihood"),
            };
            if branch.probability <= 0.0 || !branch.probability.is_finite() {
                return Err("stored attack coin path has invalid prior probability");
            }
            let log_weight = branch.probability.ln() + log_likelihood;
            max_log_weight = max_log_weight.max(log_weight);
            retained.push((log_weight, branch.outcome, branch.coin_paths));
        }
        if retained.is_empty() {
            return Err(if malformed_symbolic {
                "stored attack coin path is not a terminating geometric sequence"
            } else {
                "stored attack coin path does not match any regenerated branch"
            });
        }
        let mut selected = Vec::with_capacity(retained.len());
        let mut probability_sum = 0.0;
        for (log_weight, outcome, coin_paths) in retained {
            let probability = (log_weight - max_log_weight).exp();
            if !probability.is_finite() || probability <= 0.0 {
                return Err("stored attack coin path has invalid posterior probability");
            }
            probability_sum += probability;
            selected.push(AttackBranch {
                probability,
                outcome,
                coin_paths,
            });
        }
        if !probability_sum.is_finite() || probability_sum <= 0.0 {
            return Err("stored attack coin path has invalid posterior probability");
        }
        for branch in &mut selected {
            branch.probability /= probability_sum;
        }
        Ok(Self { branches: selected })
    }

    /// Lower into `Outcomes` and return its `(probabilities, mutations)` branches. Convenience
    /// used by tests that want to apply a specific branch's mutation directly.
    #[cfg(test)]
    pub fn into_branches(self) -> (Probabilities, super::apply_action_helpers::Mutations) {
        self.into_outcomes().into_branches()
    }

    /// Lower the structured distribution into a generic `Outcomes`, converting each
    /// `AttackOutcome` into a `Mutation`. This is the boundary between attack-specific
    /// forecasting and the shared apply/forecast machinery.
    pub fn into_outcomes(self) -> Outcomes {
        let branches = self
            .branches
            .into_iter()
            .map(|branch| {
                (
                    branch.probability,
                    branch.outcome.into_mutation(),
                    branch.coin_paths,
                )
            })
            .collect::<Vec<_>>();
        Outcomes::from_branches_with_coin_paths(branches)
            .expect("attack outcome branches should form a valid distribution")
    }
}

/// Whether `raw_total` (after damage modifiers) would knock out the Pokémon at `target`, forecast
/// against the pre-attack board. Shared by the on-knockout coin-flip splits.
fn would_knock_out(
    state: &State,
    acting_player: usize,
    target: (usize, usize),
    raw_total: u32,
    attack_name: Option<&str>,
    attack_effect: Option<&str>,
) -> bool {
    if raw_total == 0 {
        return false;
    }
    let Some(pokemon) = state.in_play_pokemon[target.0][target.1].as_ref() else {
        return false;
    };
    let modified = modify_damage(
        state,
        (acting_player, 0),
        (raw_total, target.0, target.1),
        true,
        DamageModifierContext {
            attack_name,
            attack_effect,
        },
    );
    let remaining = pokemon.get_remaining_hp();
    remaining > 0 && modified >= remaining
}

/// Apply a forecasted Perish Body heads after the attack effect and ordinary on-damaged reactions.
/// Both references follow the original Pokémon through attack-effect switches. The Ability and
/// knockout are checked again because the effect may have suppressed the Ability,
/// healed/evolved/removed the defender, or otherwise made the forecast-time trigger inapplicable.
pub(crate) fn apply_perish_body_retaliation(
    state: &mut State,
    attacking_ref: (usize, usize),
    damaged_refs: &[(usize, usize)],
) {
    let trigger_still_applies = damaged_refs.iter().any(|&(player, idx)| {
        state.in_play_pokemon[player][idx]
            .as_ref()
            .is_some_and(|pokemon| {
                idx == 0 && pokemon.is_knocked_out()
                    && matches!(
                        super::get_in_play_ability_mechanic(state, pokemon),
                        Some(
                            super::abilities::AbilityMechanic::CoinFlipToKnockOutAttackerOnKnockout
                        )
                    )
            })
    });
    if trigger_still_applies {
        if let Some(attacker) =
            state.in_play_pokemon[attacking_ref.0][attacking_ref.1].as_mut()
        {
            attacker.set_remaining_hp(0);
        }
    }
}

/// Apply forecasted point-denial coins after every attack-effect choice has resolved. References
/// are remapped with the reaction continuation when an effect switches either board. Rechecking
/// the live Ability prevents a suppressed, evolved, healed, or removed source from consuming a
/// stale forecast coin, while `KnockoutPointsCoinResolved` prevents the universal KO path from
/// offering the same coin a second time.
pub(crate) fn apply_point_denial_results(
    state: &mut State,
    flips: &[((usize, usize), bool)],
) {
    for &((player, idx), heads) in flips {
        let still_applies = state.in_play_pokemon[player][idx]
            .as_ref()
            .is_some_and(|pokemon| {
                pokemon.is_knocked_out()
                    && matches!(
                        super::get_in_play_ability_mechanic(state, pokemon),
                        Some(
                            super::abilities::AbilityMechanic::CoinFlipToDenyKnockoutPoints
                        )
                    )
            });
        if still_applies {
            let pokemon = state.in_play_pokemon[player][idx]
                .as_mut()
                .expect("point-denial source was just checked in play");
            pokemon.add_effect(CardEffect::KnockoutPointsCoinResolved, 0);
            if heads {
                pokemon.add_effect(CardEffect::DenyKnockoutPoints, 0);
            }
        }
    }
}

/// Look up the title of the attack being resolved, for attack-name-specific damage modifiers.
struct AttackMetadata {
    name: Option<String>,
    effect: Option<String>,
}

fn attack_metadata_from_action(_state: &State, action: &Action) -> AttackMetadata {
    match &action.action {
        SimpleAction::Attack(attack) | SimpleAction::ApplyQueuedAttackDamage { attack, .. } => {
            AttackMetadata {
                name: Some(attack.title.clone()),
                effect: attack.effect.clone(),
            }
        }
        _ => AttackMetadata {
            name: None,
            effect: None,
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::actions::outcomes::MAX_GEOMETRIC_SATURATION_HEADS;
    use crate::card_ids::CardId;
    use crate::models::PlayedCard;

    fn state_with_grimer_vs_meowth() -> State {
        let mut state = State::default();
        state.current_player = 0;
        // Grimer (Darkness) attacking Meowth (weakness Fighting) => no weakness multiplier,
        // so modify_damage returns the raw amount.
        state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::A1174Grimer));
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B2124Meowth));
        state
    }

    #[test]
    fn expected_damage_reads_branch_data_without_running_closures() {
        let state = state_with_grimer_vs_meowth();
        let outcomes = AttackOutcomes::single(AttackOutcome::damage(vec![(20, true, 0)]));
        let expected = outcomes.expected_damage_to_opponent_active(&state, 0, None, None);
        assert!(
            (expected - 20.0).abs() < 1e-9,
            "expected 20, got {expected}"
        );
    }

    #[test]
    fn expected_damage_halves_under_active_damage_prevention() {
        let state = state_with_grimer_vs_meowth();
        let outcomes = AttackOutcomes::single(AttackOutcome::damage(vec![(20, true, 0)]))
            .split_with_damage_prevention(&[(0, u32::MAX)]);
        // Heads branch (0.5) prevents the active damage, tails branch (0.5) deals 20.
        let expected = outcomes.expected_damage_to_opponent_active(&state, 0, None, None);
        assert!(
            (expected - 10.0).abs() < 1e-9,
            "expected 10, got {expected}"
        );
    }

    #[test]
    fn binomial_distribution_sums_to_one() {
        let outcomes = AttackOutcomes::binomial_by_heads(3, |heads| {
            AttackOutcome::damage(vec![(heads as u32 * 10, true, 0)])
        });
        let total: f64 = outcomes.branches.iter().map(|b| b.probability).sum();
        assert!((total - 1.0).abs() < 1e-9);
    }
    #[test]
    fn saturated_attack_adapter_preserves_symbolic_coin_metadata() {
        let outcomes = AttackOutcomes::geometric_until_tails_saturated(2, |heads| {
            AttackOutcome::damage(vec![(heads as u32 * 10, true, 0)])
        })
        .unwrap();
        assert!(outcomes.all_branches_have_coin_paths());
        let branches = outcomes.into_outcomes().into_branches_with_coin_paths();
        assert_eq!(branches.len(), 3);
        assert_eq!(branches[2].2, CoinPaths::UntilTailsAtLeast { min_heads: 2 });
        let error = AttackOutcomes::geometric_until_tails_saturated(
            MAX_GEOMETRIC_SATURATION_HEADS + 1,
            |_| AttackOutcome::noop(),
        )
        .err()
        .expect("attack constructor must reject an unrepresentable tail");
        assert!(matches!(
            error,
            ForecastBuildError::GeometricSaturationOutOfRange { .. }
        ));
    }

    #[test]
    fn weighted_geometric_refinement_preserves_coin_classes_and_posterior_weights() {
        let outcomes = AttackOutcomes::geometric_until_tails_saturated_weighted(1, |heads| {
            if heads == 0 {
                vec![
                    (0.25, AttackOutcome::damage(vec![(10, true, 0)])),
                    (0.75, AttackOutcome::damage(vec![(20, true, 0)])),
                ]
            } else {
                vec![(1.0, AttackOutcome::damage(vec![(30, true, 0)]))]
            }
        })
        .unwrap();
        assert_eq!(
            outcomes
                .branches
                .iter()
                .map(|branch| branch.probability)
                .collect::<Vec<_>>(),
            vec![0.125, 0.375, 0.5]
        );
        assert_eq!(
            outcomes.branches[0].coin_paths,
            outcomes.branches[1].coin_paths
        );
        assert_eq!(
            outcomes.branches[2].coin_paths,
            CoinPaths::UntilTailsAtLeast { min_heads: 1 }
        );

        let selected = outcomes.select_coin_path(&[false]).unwrap();
        assert_eq!(selected.branches.len(), 2);
        assert!((selected.branches[0].probability - 0.25).abs() < 1e-12);
        assert!((selected.branches[1].probability - 0.75).abs() < 1e-12);
        assert_eq!(selected.branches[0].outcome.damage[0].0, 10);
        assert_eq!(selected.branches[1].outcome.damage[0].0, 20);
    }

    #[test]
    fn attack_coin_conditioning_uses_path_likelihood_and_stays_stable_for_long_tails() {
        let overlapping_exact = AttackOutcomes {
            branches: vec![
                AttackBranch {
                    probability: 0.5,
                    outcome: AttackOutcome::damage(vec![(10, true, 0)]),
                    coin_paths: CoinPaths::Exact(vec![
                        CoinSeq(vec![true]),
                        CoinSeq(vec![false]),
                    ]),
                },
                AttackBranch {
                    probability: 0.5,
                    outcome: AttackOutcome::damage(vec![(20, true, 0)]),
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![true])]),
                },
            ],
        }
        .select_coin_path(&[true])
        .unwrap();
        assert!((overlapping_exact.branches[0].probability - 1.0 / 3.0).abs() < 1e-12);
        assert!((overlapping_exact.branches[1].probability - 2.0 / 3.0).abs() < 1e-12);

        let long = std::iter::repeat_n(true, 700)
            .chain(std::iter::once(false))
            .collect::<Vec<_>>();
        let symbolic = AttackOutcomes {
            branches: vec![
                AttackBranch {
                    probability: 0.2,
                    outcome: AttackOutcome::damage(vec![(10, true, 0)]),
                    coin_paths: CoinPaths::UntilTailsAtLeast { min_heads: 1 },
                },
                AttackBranch {
                    probability: 0.8,
                    outcome: AttackOutcome::damage(vec![(20, true, 0)]),
                    coin_paths: CoinPaths::UntilTailsAtLeast { min_heads: 1 },
                },
            ],
        }
        .select_coin_path(&long)
        .unwrap();
        assert!((symbolic.branches[0].probability - 0.2).abs() < 1e-12);
        assert!((symbolic.branches[1].probability - 0.8).abs() < 1e-12);

        let exact_beats_irrelevant_malformed_symbolic = AttackOutcomes {
            branches: vec![
                AttackBranch {
                    probability: 0.5,
                    outcome: AttackOutcome::noop(),
                    coin_paths: CoinPaths::UntilTailsAtLeast { min_heads: 1 },
                },
                AttackBranch {
                    probability: 0.5,
                    outcome: AttackOutcome::damage(vec![(20, true, 0)]),
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![true])]),
                },
            ],
        }
        .select_coin_path(&[true])
        .unwrap();
        assert_eq!(exact_beats_irrelevant_malformed_symbolic.branches.len(), 1);
        assert_eq!(
            exact_beats_irrelevant_malformed_symbolic.branches[0].outcome.damage[0].0,
            20
        );
    }

    #[test]
    fn weighted_geometric_refinement_rejects_invalid_conditional_distributions() {
        assert!(matches!(
            AttackOutcomes::geometric_until_tails_saturated_weighted(1, |_| vec![]),
            Err(ForecastBuildError::EmptyBranches)
        ));
        assert!(matches!(
            AttackOutcomes::geometric_until_tails_saturated_weighted(1, |_| {
                vec![(0.4, AttackOutcome::noop()), (0.4, AttackOutcome::noop())]
            }),
            Err(ForecastBuildError::ProbabilitySumInvalid)
        ));
        assert!(matches!(
            AttackOutcomes::geometric_until_tails_saturated_weighted(1, |_| {
                vec![(f64::NAN, AttackOutcome::noop())]
            }),
            Err(ForecastBuildError::ProbabilityOutOfRange)
        ));
        assert!(matches!(
            AttackOutcomes::geometric_until_tails_saturated_weighted(
                MAX_GEOMETRIC_SATURATION_HEADS,
                |_| vec![
                    (0.5, AttackOutcome::noop()),
                    (0.5, AttackOutcome::noop()),
                ],
            ),
            Err(ForecastBuildError::ProbabilityOutOfRange)
        ));
    }

    #[test]
    fn effect_adapter_preserves_symbolic_coin_metadata() {
        let effects =
            Outcomes::geometric_until_tails_saturated(1, |_| Box::new(|_, _, _| {})).unwrap();
        let attacks = AttackOutcomes::from_effect_outcomes(effects);
        assert!(attacks.all_branches_have_coin_paths());
        let branches = attacks.into_outcomes().into_branches_with_coin_paths();
        assert_eq!(
            branches.last().unwrap().2,
            CoinPaths::UntilTailsAtLeast { min_heads: 1 }
        );
    }

    #[test]
    fn serialized_concrete_path_selects_one_regenerated_symbolic_attack_branch() {
        let serialized = serde_json::to_string(&vec![true, true, true, false]).unwrap();
        let flips: Vec<bool> = serde_json::from_str(&serialized).unwrap();
        let selected = AttackOutcomes::geometric_until_tails_saturated(2, |heads| {
            AttackOutcome::damage(vec![(heads as u32 * 10, true, 0)])
        })
        .unwrap()
        .select_coin_path(&flips)
        .unwrap();
        assert_eq!(selected.branches.len(), 1);
        assert_eq!(selected.branches[0].probability, 1.0);
        assert_eq!(selected.branches[0].outcome.damage, vec![(20, true, 0)]);

        let unterminated = AttackOutcomes::geometric_until_tails_saturated(2, |heads| {
            AttackOutcome::damage(vec![(heads as u32 * 10, true, 0)])
        })
        .unwrap()
        .select_coin_path(&[true, true, true]);
        assert!(unterminated.is_err());
    }

    #[test]
    fn defender_coin_transforms_preserve_only_the_inherited_attacker_paths() {
        let mut state = State::default();
        state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::B4a064Furfrou));
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::A3096Conkeldurr));
        let base = || {
            AttackOutcomes::binary_coin(
                active_damage_outcome_for_test(200),
                active_damage_outcome_for_test(30),
            )
        };

        assert!(base()
            .split_with_damage_prevention(&[(0, 80)])
            .all_branches_have_coin_paths());
        assert!(base()
            .split_with_guts_survival(&state, 0, Some("Continuous Steps"), None, &[0])
            .all_branches_have_coin_paths());
        assert!(base()
            .split_with_point_denial(&state, 0, Some("Continuous Steps"), None, &[0])
            .all_branches_have_coin_paths());
        assert!(base()
            .split_with_attacker_knockout(&state, 0, Some("Continuous Steps"), None)
            .all_branches_have_coin_paths());
    }

    fn active_damage_outcome_for_test(damage: u32) -> AttackOutcome {
        AttackOutcome::damage(vec![(damage, true, 0)])
    }
}
