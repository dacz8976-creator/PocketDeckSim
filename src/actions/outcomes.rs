use rand::{rngs::StdRng, Rng};

use super::apply_action_helpers::{Mutation, Mutations, Probabilities};
use super::Action;
use crate::State;

pub struct Outcomes {
    branches: Vec<OutcomeBranch>,
}

pub struct OutcomeBranch {
    pub probability: f64,
    pub mutation: Mutation,
    pub coin_paths: CoinPaths,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CoinSeq(pub Vec<bool>);

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CoinPaths {
    None,
    /// Equiprobable concrete paths. Duplicate entries deliberately represent multiplicity.
    Exact(Vec<CoinSeq>),
    /// Every concrete path is `H^n T` for some `n >= min_heads`. The outcome state is
    /// identical throughout this geometric tail, even though the concrete batch is unbounded.
    UntilTailsAtLeast {
        min_heads: usize,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CoinConditionError {
    NoMatchingPath,
    InvalidObservedPath,
    Numeric,
}

/// Largest saturation boundary whose `2^-K` tail remains positive in `f64`.
pub(crate) const MAX_GEOMETRIC_SATURATION_HEADS: usize = 1074;

impl CoinPaths {
    /// Whether this branch carries a nonempty class of acting-player coin paths.
    pub fn has_paths(&self) -> bool {
        match self {
            Self::None => false,
            Self::Exact(paths) => !paths.is_empty(),
            Self::UntilTailsAtLeast { min_heads } => *min_heads <= MAX_GEOMETRIC_SATURATION_HEADS,
        }
    }

    pub(crate) fn log_likelihood(
        &self,
        observed: &CoinSeq,
    ) -> Result<Option<f64>, CoinConditionError> {
        match self {
            Self::None => Ok(None),
            Self::Exact(paths) => {
                let matches = paths.iter().filter(|path| *path == observed).count();
                if matches == 0 {
                    Ok(None)
                } else {
                    Ok(Some((matches as f64).ln() - (paths.len() as f64).ln()))
                }
            }
            Self::UntilTailsAtLeast { min_heads } => {
                let Some((&false, heads)) = observed.0.split_last() else {
                    return Err(CoinConditionError::InvalidObservedPath);
                };
                if heads.iter().any(|face| !*face) || heads.len() < *min_heads {
                    return Ok(None);
                }
                Ok(Some(
                    -((heads.len() - min_heads + 1) as f64) * std::f64::consts::LN_2,
                ))
            }
        }
    }

    /// Test whether one concrete, terminating coin batch belongs to this branch.
    pub fn contains(&self, sequence: &CoinSeq) -> bool {
        match self {
            Self::None => false,
            Self::Exact(paths) => paths.contains(sequence),
            Self::UntilTailsAtLeast { min_heads } => {
                sequence.0.len() > *min_heads
                    && sequence.0.last() == Some(&false)
                    && sequence.0[..sequence.0.len() - 1].iter().all(|face| *face)
            }
        }
    }

    /// Sample one concrete member using only the caller-supplied RNG. Exact path classes are
    /// uniform; a symbolic class emits its required heads and then samples until the first tail.
    pub fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Option<CoinSeq> {
        match self {
            Self::None => None,
            Self::Exact(paths) => {
                if paths.is_empty() {
                    None
                } else {
                    let selected = if paths.len() == 1 {
                        0
                    } else {
                        rng.gen_range(0..paths.len())
                    };
                    Some(paths[selected].clone())
                }
            }
            Self::UntilTailsAtLeast { min_heads } => {
                if *min_heads > MAX_GEOMETRIC_SATURATION_HEADS {
                    return None;
                }
                let mut faces = vec![true; *min_heads];
                while rng.gen_bool(0.5) {
                    faces.push(true);
                }
                faces.push(false);
                Some(CoinSeq(faces))
            }
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ForecastBuildError {
    EmptyBranches,
    ProbabilityOutOfRange,
    ProbabilitySumInvalid,
    CoinPathsEmpty,
    GeometricSaturationOutOfRange {
        requested: usize,
        max_supported: usize,
    },
}

/// Exact successor-state classes for a flip-until-tails effect that stops changing at `K` heads.
pub(crate) fn saturated_geometric_classes(
    saturation_heads: usize,
) -> Result<Vec<(f64, usize, CoinPaths)>, ForecastBuildError> {
    if saturation_heads > MAX_GEOMETRIC_SATURATION_HEADS {
        return Err(ForecastBuildError::GeometricSaturationOutOfRange {
            requested: saturation_heads,
            max_supported: MAX_GEOMETRIC_SATURATION_HEADS,
        });
    }
    let mut classes = Vec::with_capacity(saturation_heads.saturating_add(1));
    let mut tail_probability = 1.0_f64;
    for heads in 0..saturation_heads {
        tail_probability *= 0.5;
        let mut sequence = vec![true; heads];
        sequence.push(false);
        classes.push((
            tail_probability,
            heads,
            CoinPaths::Exact(vec![CoinSeq(sequence)]),
        ));
    }
    if !tail_probability.is_finite() || tail_probability <= 0.0 {
        return Err(ForecastBuildError::GeometricSaturationOutOfRange {
            requested: saturation_heads,
            max_supported: MAX_GEOMETRIC_SATURATION_HEADS,
        });
    }
    classes.push((
        tail_probability,
        saturation_heads,
        CoinPaths::UntilTailsAtLeast {
            min_heads: saturation_heads,
        },
    ));
    if classes.iter().any(|(probability, _, _)| {
        !probability.is_finite() || *probability <= 0.0 || *probability > 1.0
    }) {
        return Err(ForecastBuildError::ProbabilityOutOfRange);
    }
    let sum = classes
        .iter()
        .map(|(probability, _, _)| probability)
        .sum::<f64>();
    if (sum - 1.0).abs() > 1e-9 {
        return Err(ForecastBuildError::ProbabilitySumInvalid);
    }
    Ok(classes)
}

impl Outcomes {
    pub fn has_any_coin_paths(&self) -> bool {
        self.branches
            .iter()
            .any(|branch| branch.coin_paths.has_paths())
    }

    pub fn has_symbolic_coin_paths(&self) -> bool {
        self.branches
            .iter()
            .any(|branch| matches!(branch.coin_paths, CoinPaths::UntilTailsAtLeast { .. }))
    }
    pub fn single(mutation: Mutation) -> Self {
        Self {
            branches: vec![OutcomeBranch {
                probability: 1.0,
                mutation,
                coin_paths: CoinPaths::None,
            }],
        }
    }

    pub fn single_fn<F>(f: F) -> Self
    where
        F: Fn(&mut StdRng, &mut State, &Action) + 'static,
    {
        Self::single(Box::new(f))
    }

    // Useful for constructing outcomes that are not based on coin flips, or when coin flip metadata is not needed.
    pub fn from_parts(probabilities: Probabilities, mutations: Mutations) -> Self {
        assert_eq!(
            probabilities.len(),
            mutations.len(),
            "from_parts length mismatch: probabilities={} mutations={}",
            probabilities.len(),
            mutations.len()
        );
        let built = probabilities
            .into_iter()
            .zip(mutations)
            .map(|(probability, mutation)| OutcomeBranch {
                probability,
                mutation,
                coin_paths: CoinPaths::None,
            })
            .collect();
        let outcomes = Self { branches: built };
        outcomes
            .validate()
            .expect("probability/mutation branches should be valid");
        outcomes
    }

    pub fn binary_coin(heads_mutation: Mutation, tails_mutation: Mutation) -> Self {
        Self {
            branches: vec![
                OutcomeBranch {
                    probability: 0.5,
                    mutation: heads_mutation,
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![true])]),
                },
                OutcomeBranch {
                    probability: 0.5,
                    mutation: tails_mutation,
                    coin_paths: CoinPaths::Exact(vec![CoinSeq(vec![false])]),
                },
            ],
        }
    }

    pub fn from_coin_branches(
        branches: Vec<(f64, Mutation, Vec<CoinSeq>)>,
    ) -> Result<Self, ForecastBuildError> {
        let built = branches
            .into_iter()
            .map(|(probability, mutation, sequences)| OutcomeBranch {
                probability,
                mutation,
                coin_paths: CoinPaths::Exact(sequences),
            })
            .collect();
        let outcomes = Self { branches: built };
        outcomes.validate()?;
        Ok(outcomes)
    }

    pub fn binomial_by_heads(
        flips: usize,
        mut make_mutation: impl FnMut(usize) -> Mutation,
    ) -> Self {
        let denominator = 2_usize.pow(flips as u32) as f64;
        let mut branches: Vec<(f64, Mutation, Vec<CoinSeq>)> = vec![];
        for heads in 0..=flips {
            let probability = Self::binomial_coefficient(flips, heads) as f64 / denominator;
            let sequences = generate_sequences_with_heads(flips, heads)
                .into_iter()
                .map(CoinSeq)
                .collect::<Vec<_>>();
            branches.push((probability, make_mutation(heads), sequences));
        }
        Self::from_coin_branches(branches)
            .expect("binomial_by_heads should always create valid branches")
    }

    /// Legacy finite helper. Its last path has `max_heads` heads and no terminating tail, so
    /// `max_heads` is a gameplay cap. Keep existing callers unchanged until each has a proven
    /// successor-state saturation boundary.
    pub fn geometric_until_tails(
        max_heads: usize,
        mut make_mutation: impl FnMut(usize) -> Mutation,
    ) -> Self {
        let mut branches: Vec<(f64, Mutation, Vec<CoinSeq>)> = vec![];
        for heads in 0..=max_heads {
            let mut sequence = vec![true; heads];
            let probability = if heads < max_heads {
                sequence.push(false);
                0.5_f64.powi((heads + 1) as i32)
            } else {
                0.5_f64.powi(heads as i32)
            };
            branches.push((probability, make_mutation(heads), vec![CoinSeq(sequence)]));
        }
        Self::from_coin_branches(branches)
            .expect("geometric_until_tails should always create valid branches")
    }

    /// Exact successor-state distribution for a geometric effect whose mutation is identical
    /// after `saturation_heads`. The terminal branch represents every `H^n T`, `n >= K`.
    pub fn geometric_until_tails_saturated(
        saturation_heads: usize,
        mut make_mutation: impl FnMut(usize) -> Mutation,
    ) -> Result<Self, ForecastBuildError> {
        let branches = saturated_geometric_classes(saturation_heads)?
            .into_iter()
            .map(|(probability, heads, coin_paths)| (probability, make_mutation(heads), coin_paths))
            .collect();
        Self::from_branches_with_coin_paths(branches)
    }

    /// Build outcomes from per-branch `(probability, mutation, coin_paths)` triples.
    /// Unlike `from_parts`, this preserves each branch's coin metadata, which is needed
    /// when converting from an `AttackOutcomes` distribution that already carries coin paths.
    pub fn from_branches_with_coin_paths(
        branches: Vec<(f64, Mutation, CoinPaths)>,
    ) -> Result<Self, ForecastBuildError> {
        let built = branches
            .into_iter()
            .map(|(probability, mutation, coin_paths)| OutcomeBranch {
                probability,
                mutation,
                coin_paths,
            })
            .collect();
        let outcomes = Self { branches: built };
        outcomes.validate()?;
        Ok(outcomes)
    }

    /// Consume the outcomes into per-branch `(probability, mutation, coin_paths)` triples,
    /// preserving coin metadata (unlike `into_branches`).
    pub fn into_branches_with_coin_paths(self) -> Vec<(f64, Mutation, CoinPaths)> {
        self.branches
            .into_iter()
            .map(|branch| (branch.probability, branch.mutation, branch.coin_paths))
            .collect()
    }

    /// Condition the distribution on one complete, publicly observed acting-player coin batch.
    /// Every matching branch is retained; the consumed coin metadata is stripped from successors.
    pub fn condition_on_coin_sequence(
        self,
        observed: &CoinSeq,
    ) -> Result<Self, CoinConditionError> {
        let mut retained = Vec::new();
        let mut malformed_symbolic = false;
        let mut max_log_weight = f64::NEG_INFINITY;
        for branch in self.branches {
            let log_likelihood = match branch.coin_paths.log_likelihood(observed) {
                Ok(Some(value)) => value,
                Ok(None) => continue,
                Err(CoinConditionError::InvalidObservedPath) => {
                    malformed_symbolic = true;
                    continue;
                }
                Err(error) => return Err(error),
            };
            if branch.probability <= 0.0 || !branch.probability.is_finite() {
                return Err(CoinConditionError::Numeric);
            }
            let log_weight = branch.probability.ln() + log_likelihood;
            max_log_weight = max_log_weight.max(log_weight);
            retained.push((log_weight, branch.mutation));
        }
        if retained.is_empty() {
            return Err(if malformed_symbolic {
                CoinConditionError::InvalidObservedPath
            } else {
                CoinConditionError::NoMatchingPath
            });
        }
        let mut branches = Vec::with_capacity(retained.len());
        let mut sum = 0.0;
        for (log_weight, mutation) in retained {
            let weight = (log_weight - max_log_weight).exp();
            if !weight.is_finite() || weight <= 0.0 {
                return Err(CoinConditionError::Numeric);
            }
            sum += weight;
            branches.push(OutcomeBranch {
                probability: weight,
                mutation,
                coin_paths: CoinPaths::None,
            });
        }
        if !sum.is_finite() || sum <= 0.0 {
            return Err(CoinConditionError::Numeric);
        }
        for branch in &mut branches {
            branch.probability /= sum;
        }
        Ok(Self { branches })
    }

    pub fn into_branches(self) -> (Probabilities, Mutations) {
        let mut probabilities = Vec::with_capacity(self.branches.len());
        let mut mutations = Vec::with_capacity(self.branches.len());
        for branch in self.branches {
            probabilities.push(branch.probability);
            mutations.push(branch.mutation);
        }
        (probabilities, mutations)
    }

    pub fn map_mutations(self, mut f: impl FnMut(Mutation) -> Mutation) -> Self {
        let branches = self
            .branches
            .into_iter()
            .map(|branch| OutcomeBranch {
                probability: branch.probability,
                mutation: f(branch.mutation),
                coin_paths: branch.coin_paths,
            })
            .collect();
        Self { branches }
    }

    /// Forces the first coin in each coin-path branch to be heads.
    ///
    /// Returns:
    /// - `Ok(forced)` when at least one coin-based branch exists and filtering succeeds.
    ///   Probabilities are reweighted and normalized after removing non-heads-first paths.
    /// - `Err(original_or_empty)` when forcing cannot be meaningfully applied.
    ///
    /// `Err` cases:
    /// 1. No coin metadata is present in the outcomes (`CoinPaths::None` everywhere).
    ///    In this case, there is nothing to force, so callers typically keep the original outcomes.
    /// 2. Coin metadata exists, but forcing first-heads removes all remaining probability mass
    ///    (for example, no sequence starts with heads after filtering).
    ///    This avoids constructing an invalid zero-probability distribution.
    pub fn force_first_heads(self) -> Result<Self, Self> {
        let mut saw_coin = false;
        let mut branches: Vec<OutcomeBranch> = vec![];

        for branch in self.branches {
            match branch.coin_paths {
                CoinPaths::None => branches.push(branch),
                CoinPaths::Exact(seqs) => {
                    saw_coin = true;
                    let total = seqs.len();
                    let kept = seqs
                        .into_iter()
                        .filter(|seq| seq.0.first().copied().unwrap_or(false))
                        .collect::<Vec<_>>();

                    if kept.is_empty() {
                        continue;
                    }

                    let scaled_probability = branch.probability * kept.len() as f64 / total as f64;
                    branches.push(OutcomeBranch {
                        probability: scaled_probability,
                        mutation: branch.mutation,
                        coin_paths: CoinPaths::Exact(kept),
                    });
                }
                CoinPaths::UntilTailsAtLeast { min_heads } => {
                    saw_coin = true;
                    let (retained, min_heads) = if min_heads == 0 {
                        (0.5, 1)
                    } else {
                        (1.0, min_heads)
                    };
                    branches.push(OutcomeBranch {
                        probability: branch.probability * retained,
                        mutation: branch.mutation,
                        coin_paths: CoinPaths::UntilTailsAtLeast { min_heads },
                    });
                }
            }
        }

        if !saw_coin {
            return Err(Self { branches });
        }

        let sum: f64 = branches.iter().map(|b| b.probability).sum();
        if sum <= 0.0 {
            return Err(Self { branches });
        }

        for branch in &mut branches {
            branch.probability /= sum;
        }

        Ok(Self { branches })
    }

    /// Apply Will inside one already-selected Trainer source. Non-coin branches keep their exact
    /// mass; only the coin-bearing subdistribution is conditioned on a first heads.
    pub fn force_first_heads_preserving_noncoin_mass(self) -> Result<Self, Self> {
        let has_coin = self
            .branches
            .iter()
            .any(|branch| branch.coin_paths.has_paths());
        let has_first_heads = self.branches.iter().any(|branch| match &branch.coin_paths {
            CoinPaths::None => false,
            CoinPaths::Exact(paths) => paths
                .iter()
                .any(|path| path.0.first().copied().unwrap_or(false)),
            CoinPaths::UntilTailsAtLeast { .. } => true,
        });
        if !has_coin || !has_first_heads {
            return Err(self);
        }
        let mut saw_coin = false;
        let mut original_coin_mass = 0.0;
        let mut retained_coin_mass = 0.0;
        let mut branches = Vec::new();
        for branch in self.branches {
            match branch.coin_paths {
                CoinPaths::None => branches.push(branch),
                CoinPaths::Exact(seqs) => {
                    saw_coin = true;
                    original_coin_mass += branch.probability;
                    let total = seqs.len();
                    let kept = seqs
                        .into_iter()
                        .filter(|seq| seq.0.first().copied().unwrap_or(false))
                        .collect::<Vec<_>>();
                    if kept.is_empty() {
                        continue;
                    }
                    let probability = branch.probability * kept.len() as f64 / total as f64;
                    retained_coin_mass += probability;
                    branches.push(OutcomeBranch {
                        probability,
                        mutation: branch.mutation,
                        coin_paths: CoinPaths::Exact(kept),
                    });
                }
                CoinPaths::UntilTailsAtLeast { min_heads } => {
                    saw_coin = true;
                    original_coin_mass += branch.probability;
                    let (retained, min_heads) = if min_heads == 0 {
                        (0.5, 1)
                    } else {
                        (1.0, min_heads)
                    };
                    let probability = branch.probability * retained;
                    retained_coin_mass += probability;
                    branches.push(OutcomeBranch {
                        probability,
                        mutation: branch.mutation,
                        coin_paths: CoinPaths::UntilTailsAtLeast { min_heads },
                    });
                }
            }
        }
        debug_assert!(saw_coin && retained_coin_mass > 0.0);
        let scale = original_coin_mass / retained_coin_mass;
        for branch in &mut branches {
            if branch.coin_paths.has_paths() {
                branch.probability *= scale;
            }
        }
        Ok(Self { branches })
    }

    pub(crate) fn binomial_coefficient(n: usize, k: usize) -> usize {
        if k > n {
            return 0;
        }
        if k == 0 || k == n {
            return 1;
        }

        let k = k.min(n - k);
        (0..k).fold(1usize, |acc, i| acc * (n - i) / (i + 1))
    }

    fn validate(&self) -> Result<(), ForecastBuildError> {
        if self.branches.is_empty() {
            return Err(ForecastBuildError::EmptyBranches);
        }
        let mut sum = 0.0_f64;
        for branch in &self.branches {
            if !branch.probability.is_finite() || !(0.0..=1.0).contains(&branch.probability) {
                return Err(ForecastBuildError::ProbabilityOutOfRange);
            }
            sum += branch.probability;
            match &branch.coin_paths {
                CoinPaths::Exact(seqs) if seqs.is_empty() => {
                    return Err(ForecastBuildError::CoinPathsEmpty);
                }
                CoinPaths::UntilTailsAtLeast { min_heads }
                    if *min_heads > MAX_GEOMETRIC_SATURATION_HEADS =>
                {
                    return Err(ForecastBuildError::GeometricSaturationOutOfRange {
                        requested: *min_heads,
                        max_supported: MAX_GEOMETRIC_SATURATION_HEADS,
                    });
                }
                _ => {}
            }
        }
        if (sum - 1.0).abs() > 1e-9 {
            return Err(ForecastBuildError::ProbabilitySumInvalid);
        }
        Ok(())
    }
}

pub(crate) fn generate_sequences_with_heads(flips: usize, heads: usize) -> Vec<Vec<bool>> {
    if flips == 0 {
        return vec![vec![]];
    }
    let mut out = Vec::new();
    let max_mask = 1_usize << flips;
    for mask in 0..max_mask {
        if mask.count_ones() as usize == heads {
            let mut seq = Vec::with_capacity(flips);
            for i in 0..flips {
                seq.push(((mask >> i) & 1) == 1);
            }
            out.push(seq);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use std::collections::VecDeque;

    use rand::{Error, RngCore};

    use super::{CoinPaths, CoinSeq, ForecastBuildError, Outcomes, MAX_GEOMETRIC_SATURATION_HEADS};

    struct ScriptedRng {
        words: VecDeque<u64>,
    }

    fn noop() -> super::Mutation {
        Box::new(|_, _, _| {})
    }

    #[test]
    fn conditioning_retains_all_matching_branches_with_likelihood_weights() {
        let outcomes = Outcomes::from_branches_with_coin_paths(vec![
            (0.1, noop(), CoinPaths::None),
            (0.2, noop(), CoinPaths::Exact(vec![CoinSeq(vec![false])])),
            (0.3, noop(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
            (
                0.4,
                noop(),
                CoinPaths::Exact(vec![
                    CoinSeq(vec![true]),
                    CoinSeq(vec![true]),
                    CoinSeq(vec![false]),
                ]),
            ),
        ])
        .unwrap();
        let conditioned = outcomes
            .condition_on_coin_sequence(&CoinSeq(vec![true]))
            .unwrap();
        let branches = conditioned.into_branches_with_coin_paths();
        assert_eq!(branches.len(), 2);
        assert!((branches[0].0 - 9.0 / 17.0).abs() < 1e-12);
        assert!((branches[1].0 - 8.0 / 17.0).abs() < 1e-12);
        assert!(branches
            .iter()
            .all(|(_, _, paths)| *paths == CoinPaths::None));
    }

    #[test]
    fn conditioning_handles_long_symbolic_batch_and_mixed_nonmatching_family() {
        let long = CoinSeq(
            std::iter::repeat(true)
                .take(900)
                .chain(std::iter::once(false))
                .collect(),
        );
        let conditioned = Outcomes::from_branches_with_coin_paths(vec![
            (0.5, noop(), CoinPaths::UntilTailsAtLeast { min_heads: 3 }),
            (0.5, noop(), CoinPaths::UntilTailsAtLeast { min_heads: 12 }),
        ])
        .unwrap()
        .condition_on_coin_sequence(&long)
        .unwrap();
        let probabilities = conditioned.into_branches().0;
        assert_eq!(probabilities.len(), 2);
        assert!((probabilities[0] - 1.0 / 513.0).abs() < 1e-12);
        assert!((probabilities[1] - 512.0 / 513.0).abs() < 1e-12);

        let exact_only = Outcomes::from_branches_with_coin_paths(vec![
            (0.5, noop(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
            (0.5, noop(), CoinPaths::UntilTailsAtLeast { min_heads: 0 }),
        ])
        .unwrap()
        .condition_on_coin_sequence(&CoinSeq(vec![true]))
        .unwrap();
        assert_eq!(exact_only.into_branches().0, vec![1.0]);

        let malformed = Outcomes::from_branches_with_coin_paths(vec![(
            1.0,
            noop(),
            CoinPaths::UntilTailsAtLeast { min_heads: 0 },
        )])
        .unwrap()
        .condition_on_coin_sequence(&CoinSeq(vec![true]));
        assert_eq!(
            malformed.err(),
            Some(super::CoinConditionError::InvalidObservedPath)
        );
    }

    #[test]
    fn trainer_will_preserves_noncoin_mass_and_error_returns_original() {
        let forced = Outcomes::from_branches_with_coin_paths(vec![
            (0.4, noop(), CoinPaths::None),
            (
                0.6,
                noop(),
                CoinPaths::Exact(vec![CoinSeq(vec![false]), CoinSeq(vec![true])]),
            ),
        ])
        .unwrap()
        .force_first_heads_preserving_noncoin_mass()
        .unwrap_or_else(|_| panic!("mixed coin and noncoin mass must retain a heads path"));
        let branches = forced.into_branches_with_coin_paths();
        assert!((branches[0].0 - 0.4).abs() < 1e-12);
        assert!((branches[1].0 - 0.6).abs() < 1e-12);
        assert_eq!(branches[1].2, CoinPaths::Exact(vec![CoinSeq(vec![true])]));

        let mixed = Outcomes::from_branches_with_coin_paths(vec![
            (0.2, noop(), CoinPaths::None),
            (
                0.4,
                noop(),
                CoinPaths::Exact(vec![CoinSeq(vec![false]), CoinSeq(vec![true])]),
            ),
            (0.4, noop(), CoinPaths::UntilTailsAtLeast { min_heads: 0 }),
        ])
        .unwrap()
        .force_first_heads_preserving_noncoin_mass()
        .unwrap_or_else(|_| panic!("mixed exact and symbolic classes must retain heads paths"))
        .into_branches_with_coin_paths();
        assert_eq!(mixed.len(), 3);
        assert!((mixed[0].0 - 0.2).abs() < 1e-12);
        assert!((mixed[1].0 - 0.4).abs() < 1e-12);
        assert!((mixed[2].0 - 0.4).abs() < 1e-12);
        assert_eq!(mixed[2].2, CoinPaths::UntilTailsAtLeast { min_heads: 1 });

        let original = Outcomes::from_branches_with_coin_paths(vec![
            (0.25, noop(), CoinPaths::None),
            (0.75, noop(), CoinPaths::Exact(vec![CoinSeq(vec![false])])),
        ])
        .unwrap();
        let returned = original
            .force_first_heads_preserving_noncoin_mass()
            .err()
            .expect("tails-only batch cannot be forced to heads")
            .into_branches_with_coin_paths();
        assert_eq!(returned[0].0, 0.25);
        assert_eq!(returned[0].2, CoinPaths::None);
        assert_eq!(returned[1].0, 0.75);
        assert_eq!(returned[1].2, CoinPaths::Exact(vec![CoinSeq(vec![false])]));
    }

    impl RngCore for ScriptedRng {
        fn next_u32(&mut self) -> u32 {
            self.next_u64() as u32
        }
        fn next_u64(&mut self) -> u64 {
            self.words.pop_front().expect("scripted RNG exhausted")
        }
        fn fill_bytes(&mut self, dest: &mut [u8]) {
            for chunk in dest.chunks_mut(8) {
                let bytes = self.next_u64().to_le_bytes();
                chunk.copy_from_slice(&bytes[..chunk.len()]);
            }
        }
        fn try_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), Error> {
            self.fill_bytes(dest);
            Ok(())
        }
    }

    #[test]
    fn geometric_until_tails_max_heads_5_probabilities() {
        let outcomes = Outcomes::geometric_until_tails(5, |_| Box::new(|_, _, _| {}));
        let (probabilities, _) = outcomes.into_branches();

        let expected = [0.5, 0.25, 0.125, 0.0625, 0.03125, 0.03125];
        assert_eq!(probabilities.len(), expected.len());
        for (actual, exp) in probabilities.iter().zip(expected.iter()) {
            assert!((actual - exp).abs() < 1e-9);
        }
        assert!((probabilities.iter().sum::<f64>() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn binomial_coefficient_sanity() {
        assert_eq!(Outcomes::binomial_coefficient(0, 0), 1);
        assert_eq!(Outcomes::binomial_coefficient(5, 0), 1);
        assert_eq!(Outcomes::binomial_coefficient(5, 5), 1);
        assert_eq!(Outcomes::binomial_coefficient(5, 2), 10);
        assert_eq!(
            Outcomes::binomial_coefficient(5, 2),
            Outcomes::binomial_coefficient(5, 3)
        );
    }
    #[test]
    fn saturated_geometric_k3_has_exact_probabilities_and_symbolic_tail() {
        let outcomes =
            Outcomes::geometric_until_tails_saturated(3, |_| Box::new(|_, _, _| {})).unwrap();
        let branches = outcomes.into_branches_with_coin_paths();
        assert_eq!(
            branches.iter().map(|branch| branch.0).collect::<Vec<_>>(),
            vec![0.5, 0.25, 0.125, 0.125]
        );
        assert_eq!(branches[0].2, CoinPaths::Exact(vec![CoinSeq(vec![false])]));
        assert_eq!(branches[3].2, CoinPaths::UntilTailsAtLeast { min_heads: 3 });
    }

    #[test]
    fn symbolic_sampler_has_no_hidden_head_cap() {
        let words = std::iter::repeat(0)
            .take(12)
            .chain(std::iter::once(u64::MAX))
            .collect();
        let mut rng = ScriptedRng { words };
        let class = CoinPaths::UntilTailsAtLeast { min_heads: 0 };
        let sampled = class.sample(&mut rng).unwrap();
        assert_eq!(
            sampled.0,
            std::iter::repeat(true)
                .take(12)
                .chain(std::iter::once(false))
                .collect::<Vec<_>>()
        );
        assert!(class.contains(&sampled));
    }

    #[test]
    fn symbolic_membership_requires_one_terminal_tail_and_minimum_heads() {
        let class = CoinPaths::UntilTailsAtLeast { min_heads: 3 };
        assert!(class.contains(&CoinSeq(vec![true, true, true, false])));
        assert!(class.contains(&CoinSeq(vec![true, true, true, true, false])));
        assert!(!class.contains(&CoinSeq(vec![true, true, false])));
        assert!(!class.contains(&CoinSeq(vec![true, true, true])));
        assert!(!class.contains(&CoinSeq(vec![true, true, true, false, true])));
        assert_eq!(class.clone(), class);
        assert_eq!(format!("{class:?}"), "UntilTailsAtLeast { min_heads: 3 }");
        let invalid = CoinPaths::UntilTailsAtLeast {
            min_heads: MAX_GEOMETRIC_SATURATION_HEADS + 1,
        };
        let mut rng = ScriptedRng {
            words: VecDeque::new(),
        };
        assert!(!invalid.has_paths());
        assert_eq!(invalid.sample(&mut rng), None);
    }

    #[test]
    fn force_first_heads_transforms_k0_symbolic_class() {
        let forced = Outcomes::geometric_until_tails_saturated(0, |_| Box::new(|_, _, _| {}))
            .unwrap()
            .force_first_heads()
            .ok()
            .expect("saturated geometric distribution has coin metadata");
        let branches = forced.into_branches_with_coin_paths();
        assert_eq!(branches.len(), 1);
        assert_eq!(branches[0].0, 1.0);
        assert_eq!(branches[0].2, CoinPaths::UntilTailsAtLeast { min_heads: 1 });
    }

    #[test]
    fn force_first_heads_reweights_exact_and_symbolic_classes_once() {
        let forced = Outcomes::geometric_until_tails_saturated(3, |_| Box::new(|_, _, _| {}))
            .unwrap()
            .force_first_heads()
            .ok()
            .expect("saturated geometric distribution has coin metadata");
        let branches = forced.into_branches_with_coin_paths();
        assert_eq!(
            branches.iter().map(|branch| branch.0).collect::<Vec<_>>(),
            vec![0.5, 0.25, 0.25]
        );
        assert_eq!(
            branches[0].2,
            CoinPaths::Exact(vec![CoinSeq(vec![true, false])])
        );
        assert_eq!(branches[2].2, CoinPaths::UntilTailsAtLeast { min_heads: 3 });
    }

    #[test]
    fn saturated_geometric_checks_the_actual_f64_boundary() {
        let supported =
            Outcomes::geometric_until_tails_saturated(MAX_GEOMETRIC_SATURATION_HEADS, |_| {
                Box::new(|_, _, _| {})
            })
            .unwrap();
        let branches = supported.into_branches_with_coin_paths();
        assert!(branches.last().unwrap().0 > 0.0);

        let error =
            Outcomes::geometric_until_tails_saturated(MAX_GEOMETRIC_SATURATION_HEADS + 1, |_| {
                Box::new(|_, _, _| {})
            })
            .err()
            .expect("unsupported boundary must return an error");
        assert_eq!(
            error,
            ForecastBuildError::GeometricSaturationOutOfRange {
                requested: MAX_GEOMETRIC_SATURATION_HEADS + 1,
                max_supported: MAX_GEOMETRIC_SATURATION_HEADS,
            }
        );
    }
}
