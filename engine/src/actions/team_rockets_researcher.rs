use rand::{seq::SliceRandom, Rng};

use crate::{
    actions::{
        apply_action_helpers::Mutation,
        outcomes::{
            saturated_geometric_classes, CoinPaths, CoinSeq, ForecastBuildError, Outcomes,
            MAX_GEOMETRIC_SATURATION_HEADS,
        },
    },
    card_ids::CardId,
    models::{Card, TrainerCard},
    State,
};

pub const MAX_PRICED_RESEARCHER_SUCCESSORS: usize = 4096;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum UnpricedForecastKind {
    ResearcherTooManyExactSuccessors {
        required_at_least: usize,
        limit: usize,
    },
    ResearcherGeometricBound {
        eligible: usize,
        max_supported: usize,
    },
    ResearcherNumeric,
    TrainerCoinObservableGeometric {
        card_id: String,
    },
    TrainerCoinUnsupported {
        card_id: String,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UnpricedForecast {
    pub kind: UnpricedForecastKind,
    pub reason: String,
}

impl UnpricedForecast {
    pub(crate) fn too_many(required_at_least: usize) -> Self {
        Self {
            kind: UnpricedForecastKind::ResearcherTooManyExactSuccessors {
                required_at_least,
                limit: MAX_PRICED_RESEARCHER_SUCCESSORS,
            },
            reason: format!(
                "Team Rocket's Researcher exact forecast needs at least {required_at_least} \
                 successor multisets; limit is {MAX_PRICED_RESEARCHER_SUCCESSORS}"
            ),
        }
    }

    fn geometric_bound(eligible: usize) -> Self {
        Self {
            kind: UnpricedForecastKind::ResearcherGeometricBound {
                eligible,
                max_supported: MAX_GEOMETRIC_SATURATION_HEADS,
            },
            reason: format!(
                "Team Rocket's Researcher has {eligible} eligible cards, above the exact geometric \
                 boundary {MAX_GEOMETRIC_SATURATION_HEADS}"
            ),
        }
    }

    fn numeric() -> Self {
        Self {
            kind: UnpricedForecastKind::ResearcherNumeric,
            reason: "Team Rocket's Researcher exact multiset probabilities were not representable"
                .into(),
        }
    }

    pub(crate) fn observable_geometric(card_id: impl Into<String>) -> Self {
        let card_id = card_id.into();
        Self {
            kind: UnpricedForecastKind::TrainerCoinObservableGeometric {
                card_id: card_id.clone(),
            },
            reason: format!(
                "Exact search cannot finitely price the complete public coin sequence for unsaturated Trainer effect {card_id}"
            ),
        }
    }

    pub(crate) fn unsupported_trainer_coin(card_id: impl Into<String>) -> Self {
        let card_id = card_id.into();
        Self {
            kind: UnpricedForecastKind::TrainerCoinUnsupported {
                card_id: card_id.clone(),
            },
            reason: format!(
                "Trainer coin producer {card_id} is not registered for Luxury Coin staging"
            ),
        }
    }
}

#[derive(Debug, Clone)]
struct EligibleGroup {
    card: Card,
    count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct SampledResearcherBatch {
    pub(crate) flips: CoinSeq,
}

impl SampledResearcherBatch {
    pub(crate) fn heads(&self) -> usize {
        self.flips.0.iter().filter(|face| **face).count()
    }
}

#[derive(Debug, Clone)]
pub(crate) struct ResearcherPlan {
    groups: Vec<EligibleGroup>,
    eligible_count: usize,
}

pub(crate) fn is_researcher_card(trainer_card: &TrainerCard) -> bool {
    matches!(
        CardId::from_card_id(&trainer_card.id),
        Some(CardId::B4a069TeamRocketsResearcher | CardId::B4a085TeamRocketsResearcher)
    )
}

fn is_eligible(card: &Card) -> bool {
    matches!(card, Card::Pokemon(pokemon) if pokemon.name.contains("Team Rocket"))
}

impl ResearcherPlan {
    pub(crate) fn from_state(state: &State, actor: usize) -> Self {
        let mut groups: Vec<EligibleGroup> = Vec::new();
        for card in state.decks[actor]
            .cards
            .iter()
            .filter(|card| is_eligible(card))
        {
            if let Some(group) = groups.iter_mut().find(|group| group.card == *card) {
                group.count += 1;
            } else {
                groups.push(EligibleGroup {
                    card: card.clone(),
                    count: 1,
                });
            }
        }
        groups.sort_by_key(|group| group.card.get_id());
        let eligible_count = groups.iter().map(|group| group.count).sum();
        Self {
            groups,
            eligible_count,
        }
    }

    pub(crate) fn priced_successor_count_capped(&self, cap: usize) -> usize {
        let sentinel = cap.saturating_add(1);
        self.groups.iter().fold(1usize, |count, group| {
            count
                .checked_mul(group.count.saturating_add(1))
                .filter(|next| *next <= cap)
                .unwrap_or(sentinel)
        })
    }

    pub(crate) fn ensure_priced(&self) -> Result<usize, UnpricedForecast> {
        if self.eligible_count > MAX_GEOMETRIC_SATURATION_HEADS {
            return Err(UnpricedForecast::geometric_bound(self.eligible_count));
        }
        let count = self.priced_successor_count_capped(MAX_PRICED_RESEARCHER_SUCCESSORS);
        if count > MAX_PRICED_RESEARCHER_SUCCESSORS {
            return Err(UnpricedForecast::too_many(count));
        }
        Ok(count)
    }

    pub(crate) fn sample_batch<R: Rng + ?Sized>(
        &self,
        rng: &mut R,
        force_first_heads: bool,
    ) -> SampledResearcherBatch {
        let mut flips = Vec::new();
        if force_first_heads {
            flips.push(true);
        }
        while rng.gen_bool(0.5) {
            flips.push(true);
        }
        flips.push(false);
        SampledResearcherBatch {
            flips: CoinSeq(flips),
        }
    }

    /// Resolve one real physical-card sample. Memory is O(M + H): O(M) candidate indices and the
    /// required uncapped concrete H* T trace retained by `batch`.
    pub(crate) fn apply_sampled<R: Rng>(
        &self,
        batch: &SampledResearcherBatch,
        rng: &mut R,
        state: &mut State,
        actor: usize,
    ) {
        let draw_count = batch.heads().min(self.eligible_count);
        let mut eligible_indices = state.decks[actor]
            .cards
            .iter()
            .enumerate()
            .filter_map(|(idx, card)| is_eligible(card).then_some(idx))
            .collect::<Vec<_>>();
        if draw_count == 0 {
            eligible_indices.clear();
        } else if draw_count < eligible_indices.len() {
            eligible_indices.shuffle(rng);
            eligible_indices.truncate(draw_count);
        }
        eligible_indices.sort_unstable_by(|a, b| b.cmp(a));
        let mut selected_cards = Vec::with_capacity(eligible_indices.len());
        for deck_idx in eligible_indices {
            selected_cards.push(state.decks[actor].cards.remove(deck_idx));
        }
        // The printed rule does not define a chosen-card order. Exact forecasts represent a
        // physical subset as a multiset, so actual play appends that subset in the same stable
        // CardId order. Existing cards retain their order and remain an observable hand prefix.
        selected_cards.sort_by_key(Card::get_id);
        state.hands[actor].extend(selected_cards);
        // Inherited engine policy: random deck-search effects normalize the hidden deck with one
        // shuffle even when the result selects no card. The printed text itself says no shuffle.
        state.decks[actor].shuffle(false, rng);
    }

    pub(crate) fn forecast_exact(&self, actor: usize) -> Result<Outcomes, UnpricedForecast> {
        self.ensure_priced()?;
        let classes =
            saturated_geometric_classes(self.eligible_count).map_err(|error| match error {
                ForecastBuildError::GeometricSaturationOutOfRange { .. } => {
                    UnpricedForecast::geometric_bound(self.eligible_count)
                }
                _ => UnpricedForecast::numeric(),
            })?;
        let mut branches = Vec::with_capacity(
            self.priced_successor_count_capped(MAX_PRICED_RESEARCHER_SUCCESSORS),
        );
        for (coin_probability, heads, coin_paths) in classes {
            let mut selections = Vec::new();
            let mut current = vec![0usize; self.groups.len()];
            enumerate_count_vectors(
                &self.groups,
                0,
                heads.min(self.eligible_count),
                &mut current,
                &mut selections,
            );
            let conditional = selection_probabilities(
                &self.groups,
                self.eligible_count,
                heads.min(self.eligible_count),
                &selections,
            )?;
            for (selection, selection_probability) in selections.into_iter().zip(conditional) {
                let selected = self
                    .groups
                    .iter()
                    .zip(selection)
                    .filter(|(_, count)| *count > 0)
                    .map(|(group, count)| (group.card.clone(), count))
                    .collect::<Vec<_>>();
                let mutation: Mutation = Box::new(move |rng, state, _action| {
                    for (card, count) in &selected {
                        for _ in 0..*count {
                            state.transfer_card_from_deck_to_hand(actor, card);
                        }
                    }
                    state.decks[actor].shuffle(false, rng);
                });
                let probability = coin_probability * selection_probability;
                if !probability.is_finite() || probability <= 0.0 {
                    return Err(UnpricedForecast::numeric());
                }
                branches.push((probability, mutation, coin_paths.clone()));
            }
        }
        Outcomes::from_branches_with_coin_paths(branches).map_err(|_| UnpricedForecast::numeric())
    }

    /// Exact conditional selection distribution after a concrete public batch is known.
    pub(crate) fn forecast_heads(
        &self,
        actor: usize,
        heads: usize,
    ) -> Result<Outcomes, UnpricedForecast> {
        let draw_count = heads.min(self.eligible_count);
        let mut selections = Vec::new();
        let mut current = vec![0usize; self.groups.len()];
        enumerate_count_vectors(&self.groups, 0, draw_count, &mut current, &mut selections);
        if selections.len() > MAX_PRICED_RESEARCHER_SUCCESSORS {
            return Err(UnpricedForecast::too_many(selections.len()));
        }
        let conditional =
            selection_probabilities(&self.groups, self.eligible_count, draw_count, &selections)?;
        let branches = selections
            .into_iter()
            .zip(conditional)
            .map(|(selection, probability)| {
                let selected = self
                    .groups
                    .iter()
                    .zip(selection)
                    .filter(|(_, count)| *count > 0)
                    .map(|(group, count)| (group.card.clone(), count))
                    .collect::<Vec<_>>();
                let mutation: Mutation = Box::new(move |rng, state, _action| {
                    for (card, count) in &selected {
                        for _ in 0..*count {
                            state.transfer_card_from_deck_to_hand(actor, card);
                        }
                    }
                    state.decks[actor].shuffle(false, rng);
                });
                (probability, mutation, CoinPaths::None)
            })
            .collect();
        Outcomes::from_branches_with_coin_paths(branches).map_err(|_| UnpricedForecast::numeric())
    }
}

fn enumerate_count_vectors(
    groups: &[EligibleGroup],
    group_idx: usize,
    remaining: usize,
    current: &mut [usize],
    output: &mut Vec<Vec<usize>>,
) {
    if group_idx == groups.len() {
        if remaining == 0 {
            output.push(current.to_vec());
        }
        return;
    }
    for count in 0..=groups[group_idx].count.min(remaining) {
        current[group_idx] = count;
        enumerate_count_vectors(groups, group_idx + 1, remaining - count, current, output);
    }
}

fn log_binomial(n: usize, k: usize) -> f64 {
    let k = k.min(n - k);
    (1..=k)
        .map(|i| ((n - k + i) as f64).ln() - (i as f64).ln())
        .sum()
}

fn selection_probabilities(
    groups: &[EligibleGroup],
    eligible_count: usize,
    draw_count: usize,
    selections: &[Vec<usize>],
) -> Result<Vec<f64>, UnpricedForecast> {
    let denominator = log_binomial(eligible_count, draw_count);
    let mut weights = Vec::with_capacity(selections.len());
    for selection in selections {
        let log_weight = groups
            .iter()
            .zip(selection)
            .map(|(group, chosen)| log_binomial(group.count, *chosen))
            .sum::<f64>()
            - denominator;
        let weight = log_weight.exp();
        if !weight.is_finite() || weight <= 0.0 {
            return Err(UnpricedForecast::numeric());
        }
        weights.push(weight);
    }
    let sum = weights.iter().sum::<f64>();
    if !sum.is_finite() || sum <= 0.0 {
        return Err(UnpricedForecast::numeric());
    }
    for weight in &mut weights {
        *weight /= sum;
    }
    Ok(weights)
}

pub(crate) fn copied_researcher_expansion(
    state: &State,
    actor: usize,
    candidates: &[(TrainerCard, usize)],
) -> Result<usize, UnpricedForecast> {
    let plan = ResearcherPlan::from_state(state, actor);
    let researcher_printings = candidates
        .iter()
        .filter(|(trainer, count)| *count > 0 && is_researcher_card(trainer))
        .count();
    if researcher_printings == 0 {
        return Ok(0);
    }
    let per_printing = plan.ensure_priced()?;
    let total = per_printing
        .checked_mul(researcher_printings)
        .unwrap_or(MAX_PRICED_RESEARCHER_SUCCESSORS + 1);
    if total > MAX_PRICED_RESEARCHER_SUCCESSORS {
        return Err(UnpricedForecast::too_many(total));
    }
    Ok(total)
}

#[cfg(test)]
mod tests {
    use std::collections::VecDeque;

    use rand::{Error, RngCore};

    use super::*;

    struct ScriptedRng {
        words: VecDeque<u64>,
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
    fn multiset_count_is_product_of_copy_counts_plus_one() {
        let plan = ResearcherPlan {
            groups: vec![
                EligibleGroup {
                    card: Card::Unknown,
                    count: 2,
                },
                EligibleGroup {
                    card: Card::Unknown,
                    count: 1,
                },
            ],
            eligible_count: 3,
        };
        assert_eq!(plan.priced_successor_count_capped(100), 6);
    }

    #[test]
    fn duplicate_physical_cards_have_hypergeometric_weights() {
        let groups = vec![
            EligibleGroup {
                card: Card::Unknown,
                count: 2,
            },
            EligibleGroup {
                card: Card::Unknown,
                count: 1,
            },
        ];
        let mut current = vec![0; 2];
        let mut one = Vec::new();
        enumerate_count_vectors(&groups, 0, 1, &mut current, &mut one);
        let probabilities = selection_probabilities(&groups, 3, 1, &one).unwrap();
        let weighted = one.into_iter().zip(probabilities).collect::<Vec<_>>();
        assert!(weighted
            .iter()
            .any(|(x, p)| x == &[1, 0] && (*p - 2.0 / 3.0).abs() < 1e-12));
        assert!(weighted
            .iter()
            .any(|(x, p)| x == &[0, 1] && (*p - 1.0 / 3.0).abs() < 1e-12));
    }

    #[test]
    fn actual_batch_keeps_twelve_heads_and_terminal_tail_without_a_cap() {
        let plan = ResearcherPlan {
            groups: Vec::new(),
            eligible_count: 0,
        };
        let mut words = VecDeque::from(vec![0; 12]);
        words.push_back(u64::MAX);
        let batch = plan.sample_batch(&mut ScriptedRng { words }, false);
        assert_eq!(batch.flips.0, [vec![true; 12], vec![false]].concat());
    }
}
