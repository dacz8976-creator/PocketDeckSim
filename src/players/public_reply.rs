//! Bounded, closed-information certificates for an opponent's already-available attack win.
//!
//! This is deliberately not a general opponent model.  A certificate means that one legal,
//! visible-board attack has an exhaustively represented, deterministic terminal result in every
//! positive-probability branch.  Every attack or transition outside the registry below remains
//! unknown.  In particular, absence of a certificate is never evidence that a position is safe.

use serde::{Deserialize, Serialize};

use crate::{
    actions::{
        abilities::AbilityMechanic,
        attacks::{BenchDamageFilter, Mechanic},
        get_ability_mechanic, Action, SimpleAction, EFFECT_MECHANIC_MAP,
    },
    card_ids::CardId,
    effects::{CardEffect, TurnEffect},
    hooks::DamageModifierContext,
    models::{Attack, Card, EnergyType, TrainerType},
    observation::{hidden_continuation_reason, PlayerObservation},
    state::GameOutcome,
    State,
};

const PROBABILITY_TOLERANCE: f64 = 1.0e-12;

/// Why a public reply was not eligible for proof-producing evaluation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum UnsupportedReason {
    UntrustedState,
    InvalidObserver,
    InvalidProvenance,
    SetupConcealed,
    TerminalState,
    WrongActor,
    PrivateChoice,
    HiddenIdentity,
    HiddenOrder,
    UnsupportedForcedTransition,
    UnsupportedPrefixAction,
    UnsupportedAttackMechanic,
    UnsupportedHook,
    InvalidProbability,
    NonterminalPositiveBranch,
    UnresolvedContinuation,
}

/// A legal attack that was inspected but could not supply a terminal certificate.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct UnsupportedAction {
    pub action: Action,
    pub reason: UnsupportedReason,
}

/// Result of the bounded public attack scan.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum PublicReplyAssessment {
    /// At least one already legal opponent attack wins the match in every exhaustive,
    /// positive-probability branch admitted by this module.
    ProvenImmediateWin {
        action: Action,
        positive_branches: usize,
        probability_sum: f64,
    },
    /// No admitted attack proved a win.  This is an unknown result, not a safety claim.
    NoCertifiedWitness {
        unsupported: Vec<UnsupportedAction>,
    },
    /// The leaf itself is outside the public certification boundary.
    NotApplicable {
        reason: UnsupportedReason,
    },
}

impl PublicReplyAssessment {
    /// Stable text for the search's existing unpriced-branch recorder.
    pub fn unpriced_reason(&self) -> Option<&'static str> {
        match self {
            Self::ProvenImmediateWin { .. } => None,
            Self::NoCertifiedWitness { .. } => Some(
                "no certified public immediate winning reply; unsupported replies remain unknown",
            ),
            Self::NotApplicable { reason } => Some(reason.unpriced_reason()),
        }
    }
}

impl UnsupportedReason {
    pub fn unpriced_reason(self) -> &'static str {
        match self {
            Self::UntrustedState => "public reply certificate refused an untrusted raw state",
            Self::InvalidObserver => "public reply certificate observer is invalid",
            Self::InvalidProvenance => "public reply certificate lost transition provenance",
            Self::SetupConcealed => "public reply certificate cannot inspect concealed setup",
            Self::TerminalState => "public reply certificate received a terminal state",
            Self::WrongActor => "public reply certificate is not at the opponent's turn",
            Self::PrivateChoice => "public reply certificate encountered a private choice",
            Self::HiddenIdentity => "public reply certificate depends on a hidden card identity",
            Self::HiddenOrder => "public reply certificate depends on an unobserved card order",
            Self::UnsupportedForcedTransition => {
                "public reply certificate encountered an unsupported forced transition"
            }
            Self::UnsupportedPrefixAction => {
                "public reply certificate encountered an unsupported prefix action"
            }
            Self::UnsupportedAttackMechanic => {
                "public reply attack mechanic is outside the audited certificate registry"
            }
            Self::UnsupportedHook => {
                "public reply board contains a hook outside the audited certificate registry"
            }
            Self::InvalidProbability => {
                "public reply certificate produced an invalid probability distribution"
            }
            Self::NonterminalPositiveBranch => {
                "public reply attack has a positive-probability nonwinning branch"
            }
            Self::UnresolvedContinuation => {
                "public reply attack leaves an unresolved continuation"
            }
        }
    }
}

/// Copyable proof provenance carried beside the ordinary sampled search state.
///
/// It intentionally stores no sampled cards.  `advance` keeps it valid only across the small set
/// of public, order-independent transitions used by the recorded Zapdos/Kecleon witness.  Once
/// invalid, it can never become valid again by masking a later leaf.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) struct PublicReplyProvenance {
    observer: Option<usize>,
    invalid_reason: Option<UnsupportedReason>,
}

impl PublicReplyProvenance {
    pub(crate) fn from_observation(observation: &PlayerObservation) -> Self {
        if observation.actor < 2 {
            Self {
                observer: Some(observation.actor),
                invalid_reason: None,
            }
        } else {
            Self {
                observer: None,
                invalid_reason: Some(UnsupportedReason::InvalidObserver),
            }
        }
    }

    /// Raw omniscient or reconstructed states have no public transition provenance.
    pub(crate) const fn untrusted() -> Self {
        Self {
            observer: None,
            invalid_reason: Some(UnsupportedReason::UntrustedState),
        }
    }

    pub(crate) fn is_valid(self) -> bool {
        self.invalid_reason.is_none() && self.observer.is_some()
    }

    /// Record one chosen search transition.  This checks only whether the transition preserves
    /// the public projection needed by the reply proof.  For EndTurn, the newly rolled *future*
    /// Energy is intentionally irrelevant: assessment clears both Energy zones and admits only an
    /// attack already payable from attached public Energy.
    pub(crate) fn advance(self, before: &State, action: &Action) -> Self {
        if !self.is_valid() {
            return self;
        }
        match transition_admission(before, action) {
            Ok(()) => self,
            Err(reason) => Self {
                observer: self.observer,
                invalid_reason: Some(reason),
            },
        }
    }

    /// Assess an opponent leaf only while all preceding transitions retain public provenance.
    pub(crate) fn assess(self, leaf: &State, myself: usize) -> PublicReplyAssessment {
        if let Some(reason) = self.invalid_reason {
            return PublicReplyAssessment::NotApplicable { reason };
        }
        if self.observer != Some(myself) || myself >= 2 {
            return PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::InvalidObserver,
            };
        }
        assess_trusted_leaf(leaf, myself)
    }
}

/// Public diagnostic entry point.  It is safe because the state comes directly from an
/// observation rather than from `search_state`'s sampled own-deck ordering.
pub fn assess_observation(observation: &PlayerObservation) -> PublicReplyAssessment {
    PublicReplyProvenance::from_observation(observation)
        .assess(observation.visible_state(), observation.actor)
}

fn transition_admission(before: &State, action: &Action) -> Result<(), UnsupportedReason> {
    if before.turn_count == 0 || before.setup_opponent_hidden {
        return Err(UnsupportedReason::SetupConcealed);
    }
    if before.winner.is_some() {
        return Err(UnsupportedReason::TerminalState);
    }
    if action.actor >= 2 {
        return Err(UnsupportedReason::WrongActor);
    }
    if before.pending_attack_coin_choice.is_some()
        || before.pending_misty_target_choice.is_some()
        || before.pending_trainer_coin_choice.is_some()
        || before
            .move_generation_stack
            .last()
            .is_some_and(|(_, choices)| choices.is_empty())
    {
        return Err(UnsupportedReason::PrivateChoice);
    }
    if !serialized_turn_effects_are_only_current_retreat_discount(before) {
        return Err(UnsupportedReason::UnsupportedHook);
    }
    // Free-play generation consults Tool retreat hooks. Screen the board before asking it to
    // enumerate an action so malformed/deserialized attached cards cannot reach `ensure_tool_card`.
    if !matches!(action.action, SimpleAction::DrawCard { .. }) {
        prefix_board_admitted(before)?;
    }
    if !action_is_offered(before, action) {
        return Err(UnsupportedReason::UnsupportedPrefixAction);
    }

    match &action.action {
        SimpleAction::DrawCard { .. } => Err(UnsupportedReason::HiddenOrder),
        SimpleAction::Play { trainer_card }
            if !action.is_stack
                && CardId::from_card_id(&trainer_card.id) == Some(CardId::PA002XSpeed) =>
        {
            Ok(())
        }
        SimpleAction::Retreat(_) if !action.is_stack => Ok(()),
        SimpleAction::EndTurn if !action.is_stack => {
            if before.turn_count >= 30 {
                return Err(UnsupportedReason::UnsupportedForcedTransition);
            }
            if before
                .enumerate_in_play_pokemon(0)
                .chain(before.enumerate_in_play_pokemon(1))
                .any(|(_, pokemon)| pokemon.has_status_condition())
            {
                return Err(UnsupportedReason::UnsupportedForcedTransition);
            }
            Ok(())
        }
        SimpleAction::Attack(attack) if !action.is_stack => {
            prefix_attack_admitted(before, action.actor, attack)?;
            Ok(())
        }
        _ => Err(UnsupportedReason::UnsupportedPrefixAction),
    }
}

fn action_is_offered(state: &State, action: &Action) -> bool {
    let (actor, actions) = state.generate_possible_actions();
    actor == action.actor && actions.iter().any(|candidate| candidate == action)
}

fn prefix_attack_admitted(
    state: &State,
    actor: usize,
    attack: &Attack,
) -> Result<(), UnsupportedReason> {
    match certified_attack_kind(attack) {
        Ok(CertifiedAttackKind::SelfCounterattack { .. }) => {
            return Err(UnsupportedReason::UnsupportedPrefixAction);
        }
        Ok(_) => return Ok(()),
        Err(_) => {}
    }

    let Some(effect) = attack.effect.as_deref() else {
        return Ok(());
    };
    match EFFECT_MECHANIC_MAP.get(effect) {
        Some(Mechanic::AlsoChoiceBenchDamageFiltered {
            opponent: true,
            damage: _,
            filter: BenchDamageFilter::Damaged,
        }) => {
            let opponent = 1 - actor;
            if state
                .enumerate_bench_pokemon(opponent)
                .any(|(_, pokemon)| pokemon.is_damaged())
            {
                Err(UnsupportedReason::UnsupportedPrefixAction)
            } else {
                // With no eligible damaged Bench target this source route is exactly one ordinary
                // Active-damage outcome and cannot create a private target frame.
                Ok(())
            }
        }
        _ => Err(UnsupportedReason::UnsupportedAttackMechanic),
    }
}

fn assess_trusted_leaf(leaf: &State, myself: usize) -> PublicReplyAssessment {
    if leaf.turn_count == 0 || leaf.setup_opponent_hidden {
        return PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::SetupConcealed,
        };
    }
    if leaf.winner.is_some() {
        return PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::TerminalState,
        };
    }
    let opponent = 1 - myself;
    if leaf.current_player != opponent {
        return PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::WrongActor,
        };
    }
    if leaf.pending_attack_coin_choice.is_some()
        || leaf.pending_misty_target_choice.is_some()
        || leaf.pending_trainer_coin_choice.is_some()
    {
        return PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::PrivateChoice,
        };
    }

    let mut public = match projected_free_opponent_turn(leaf, opponent) {
        Ok(state) => state,
        Err(reason) => return PublicReplyAssessment::NotApplicable { reason },
    };
    if let Err(reason) = certificate_board_admitted(&public) {
        return PublicReplyAssessment::NotApplicable { reason };
    }

    // The visible preview that rotated into `current` is not required by an admitted attack, and
    // the next preview may be RNG-generated.  Clearing both prevents action generation from
    // treating either as a resource while leaving already attached public Energy unchanged.
    public.energy_zone.iter_mut().for_each(|zone| {
        zone.current = None;
        zone.next = None;
    });

    let (actor, actions) = public.generate_possible_actions();
    if actor != opponent {
        return PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::WrongActor,
        };
    }

    let mut unsupported = Vec::new();
    for action in actions.into_iter().filter(|candidate| {
        !candidate.is_stack && matches!(candidate.action, SimpleAction::Attack(_))
    }) {
        if hidden_continuation_reason(&public, &action).is_some() {
            unsupported.push(UnsupportedAction {
                action,
                reason: UnsupportedReason::HiddenIdentity,
            });
            continue;
        }
        let SimpleAction::Attack(attack) = &action.action else {
            unreachable!("the iterator retained only Attack actions")
        };
        let kind = match certified_attack_kind(attack) {
            Ok(kind) => kind,
            Err(reason) => {
                unsupported.push(UnsupportedAction { action, reason });
                continue;
            }
        };
        let branches = certified_attack_successors(&public, &action, kind);
        let probability_sum: f64 = branches.iter().map(|(probability, _)| *probability).sum();
        if branches.is_empty()
            || branches
                .iter()
                .any(|(probability, _)| !probability.is_finite() || *probability <= 0.0)
            || (probability_sum - 1.0).abs() > PROBABILITY_TOLERANCE
        {
            unsupported.push(UnsupportedAction {
                action,
                reason: UnsupportedReason::InvalidProbability,
            });
            continue;
        }
        if branches.iter().all(|(_, successor)| {
            successor.winner == Some(GameOutcome::Win(opponent))
                && successor.move_generation_stack.is_empty()
        }) {
            return PublicReplyAssessment::ProvenImmediateWin {
                action,
                positive_branches: branches.len(),
                probability_sum,
            };
        }
        let reason = if branches
            .iter()
            .any(|(_, successor)| !successor.move_generation_stack.is_empty())
        {
            UnsupportedReason::UnresolvedContinuation
        } else {
            UnsupportedReason::NonterminalPositiveBranch
        };
        unsupported.push(UnsupportedAction { action, reason });
    }

    PublicReplyAssessment::NoCertifiedWitness { unsupported }
}

fn projected_free_opponent_turn(
    leaf: &State,
    opponent: usize,
) -> Result<State, UnsupportedReason> {
    let mut public = leaf.clone();
    for player in 0..2 {
        public.hands[player].fill(Card::Unknown);
        public.decks[player].cards.fill(Card::Unknown);
        public.decks[player].energy_types.clear();
    }

    if public.move_generation_stack.is_empty() {
        return Ok(public);
    }
    if public.move_generation_stack.len() != 1 {
        return Err(UnsupportedReason::UnsupportedForcedTransition);
    }
    let (actor, choices) = public
        .move_generation_stack
        .pop()
        .expect("the singleton stack was just checked");
    if actor != opponent || choices.as_slice() != [SimpleAction::DrawCard { amount: 1 }] {
        return Err(if choices.is_empty() {
            UnsupportedReason::PrivateChoice
        } else {
            UnsupportedReason::UnsupportedForcedTransition
        });
    }

    // Count-only draw.  Never consult the concrete deck order carried by a search world.
    if public.hands[opponent].len() < 10 && public.decks[opponent].cards.pop().is_some() {
        public.hands[opponent].push(Card::Unknown);
    }
    Ok(public)
}

#[derive(Debug, Clone)]
enum CertifiedAttackKind {
    FixedDamage,
    TypedSelfDiscard(Vec<EnergyType>),
    HitAndHide,
    SelfCounterattack { amount: u32 },
}

fn certified_attack_kind(attack: &Attack) -> Result<CertifiedAttackKind, UnsupportedReason> {
    let Some(effect) = attack.effect.as_deref() else {
        return Ok(CertifiedAttackKind::FixedDamage);
    };
    match EFFECT_MECHANIC_MAP.get(effect) {
        Some(Mechanic::SelfDiscardEnergy { energies }) => {
            Ok(CertifiedAttackKind::TypedSelfDiscard(energies.clone()))
        }
        Some(Mechanic::DamageAndCardEffect {
            opponent: false,
            effect: CardEffect::PreventAllDamageAndEffects,
            duration: 1,
            coin_flip: true,
        }) => Ok(CertifiedAttackKind::HitAndHide),
        Some(Mechanic::DamageAndCardEffect {
            opponent: false,
            effect: CardEffect::Counterattack { amount },
            duration: 1,
            coin_flip: false,
        }) => Ok(CertifiedAttackKind::SelfCounterattack { amount: *amount }),
        _ => Err(UnsupportedReason::UnsupportedAttackMechanic),
    }
}

fn certified_attack_successors(
    state: &State,
    action: &Action,
    kind: CertifiedAttackKind,
) -> Vec<(f64, State)> {
    match kind {
        CertifiedAttackKind::FixedDamage => vec![(
            1.0,
            resolve_certified_attack(state, action, None, None),
        )],
        CertifiedAttackKind::TypedSelfDiscard(energies) => vec![(
            1.0,
            resolve_certified_attack(state, action, Some(&energies), None),
        )],
        CertifiedAttackKind::HitAndHide => vec![
            (
                0.5,
                resolve_certified_attack(
                    state,
                    action,
                    None,
                    Some(CardEffect::PreventAllDamageAndEffects),
                ),
            ),
            (0.5, resolve_certified_attack(state, action, None, None)),
        ],
        CertifiedAttackKind::SelfCounterattack { amount } => vec![(
            1.0,
            resolve_certified_attack(
                state,
                action,
                None,
                Some(CardEffect::Counterattack { amount }),
            ),
        )],
    }
}

/// Resolve only the four source-audited attack shapes.  This path contains no RNG argument and
/// does not call generic forecast mutations; exhaustive coverage follows from the registry itself.
fn resolve_certified_attack(
    state: &State,
    action: &Action,
    typed_self_discard: Option<&[EnergyType]>,
    post_damage_effect: Option<CardEffect>,
) -> State {
    let SimpleAction::Attack(attack) = &action.action else {
        unreachable!("certified attack resolver received another action")
    };
    let mut successor = state.clone();
    let opponent = 1 - action.actor;
    crate::actions::handle_damage_only(
        &mut successor,
        (action.actor, 0),
        &[(attack.fixed_damage, opponent, 0)],
        true,
        DamageModifierContext {
            attack_name: Some(&attack.title),
            attack_effect: attack.effect.as_deref(),
        },
    );

    if let Some(requested) = typed_self_discard {
        let mut remaining = successor.get_active(action.actor).attached_energy.clone();
        let mut actual = Vec::new();
        for energy in requested {
            if let Some(position) = remaining.iter().position(|candidate| candidate == energy) {
                remaining.swap_remove(position);
                actual.push(*energy);
            }
        }
        if !actual.is_empty() {
            successor.discard_from_active(action.actor, &actual);
        }
    }

    if let Some(effect) = post_damage_effect {
        successor
            .get_active_mut(action.actor)
            .add_effect(effect, 1);
    }
    crate::actions::handle_knockouts(&mut successor, (action.actor, 0), true);
    successor
}

fn prefix_board_admitted(state: &State) -> Result<(), UnsupportedReason> {
    common_board_hooks_admitted(state)
}

fn certificate_board_admitted(state: &State) -> Result<(), UnsupportedReason> {
    common_board_hooks_admitted(state)?;
    if !serialized_turn_effects_are_empty(state) {
        return Err(UnsupportedReason::UnsupportedHook);
    }
    Ok(())
}

/// Closed hook registry.  Weakness and Giant Cape HP are deterministic core data.  Spy Ops is a
/// manual hidden-information action and therefore inert unless selected; the scanner never selects
/// abilities.  Every passive/automatic ability, Stadium, other Tool, status, or effect is refused.
fn common_board_hooks_admitted(state: &State) -> Result<(), UnsupportedReason> {
    if state.active_stadium.is_some() {
        return Err(UnsupportedReason::UnsupportedHook);
    }
    if state.maybe_get_active(0).is_none() || state.maybe_get_active(1).is_none() {
        return Err(UnsupportedReason::UnsupportedHook);
    }
    if state.points.iter().any(|points| *points >= 3) {
        return Err(UnsupportedReason::TerminalState);
    }
    for player in 0..2 {
        for (_, pokemon) in state.enumerate_in_play_pokemon(player) {
            if pokemon.card.is_unknown()
                || pokemon.cards_behind.iter().any(Card::is_unknown)
                || pokemon.attached_tools.iter().any(Card::is_unknown)
            {
                return Err(UnsupportedReason::HiddenIdentity);
            }
            // Validate attachment representation before `is_knocked_out` reads effective HP and
            // reaches Tool helpers that assume every attached entry is a Tool Trainer card.
            if pokemon
                .attached_tools
                .iter()
                .any(|tool| !is_canonical_giant_cape(tool))
            {
                return Err(UnsupportedReason::UnsupportedHook);
            }
            if pokemon.has_status_condition() || pokemon.is_knocked_out() {
                return Err(UnsupportedReason::UnsupportedHook);
            }
            if matches!(
                CardId::from_card_id(&pokemon.card.get_id()),
                Some(
                    CardId::A1061Poliwrath
                        | CardId::A1a056Druddigon
                        | CardId::A2b028Pawmot
                        | CardId::A3a052Ferrothorn
                        | CardId::A4a065Zangoose
                        | CardId::B1297Poliwrath
                        | CardId::PA054Pawmot
                        | CardId::B1160DragalgeEx
                        | CardId::B1263DragalgeEx
                        | CardId::B1281DragalgeEx
                        | CardId::B3231DragalgeEx
                )
            ) {
                return Err(UnsupportedReason::UnsupportedHook);
            }
            if pokemon
                .get_active_effects()
                .iter()
                .any(|effect| !matches!(effect, CardEffect::PreventAllDamageAndEffects))
            {
                return Err(UnsupportedReason::UnsupportedHook);
            }
            if pokemon.card.get_ability().is_some()
                && !matches!(
                    get_ability_mechanic(&pokemon.card),
                    Some(AbilityMechanic::RevealRandomOpponentHandCard)
                )
            {
                return Err(UnsupportedReason::UnsupportedHook);
            }
        }
    }
    // HP bonuses are cached in PlayedCard.  With no Stadium and only the inert Spy Ops ability,
    // recomputation must be a no-op; otherwise stale or deserialized bonus state could decide KO.
    let hp_before: Vec<_> = (0..2)
        .flat_map(|player| {
            state
                .enumerate_in_play_pokemon(player)
                .map(move |(slot, pokemon)| (player, slot, pokemon.get_effective_total_hp()))
        })
        .collect();
    let mut refreshed = state.clone();
    refreshed.refresh_hp_bonuses_all();
    let hp_after: Vec<_> = (0..2)
        .flat_map(|player| {
            refreshed
                .enumerate_in_play_pokemon(player)
                .map(move |(slot, pokemon)| (player, slot, pokemon.get_effective_total_hp()))
        })
        .collect();
    if hp_before != hp_after {
        return Err(UnsupportedReason::UnsupportedHook);
    }
    Ok(())
}

fn is_canonical_giant_cape(card: &Card) -> bool {
    let Card::Trainer(tool) = card else {
        return false;
    };
    tool.trainer_card_type == TrainerType::Tool
        && tool.effect == "The Pokémon this card is attached to gets +20 HP."
        && matches!(
            CardId::from_card_id(&tool.id),
            Some(CardId::A2147GiantCape | CardId::A4b320GiantCape | CardId::A4b321GiantCape)
        )
}

fn serialized_turn_effects_are_empty(state: &State) -> bool {
    let Ok(value) = serde_json::to_value(state) else {
        return false;
    };
    value
        .get("turn_effects")
        .and_then(serde_json::Value::as_object)
        .is_some_and(|turns| {
            turns.iter().all(|(turn, effects)| {
                turn.parse::<u8>().is_ok_and(|turn| turn < state.turn_count)
                    || effects.as_array().is_some_and(Vec::is_empty)
            })
        })
}

fn serialized_turn_effects_are_only_current_retreat_discount(state: &State) -> bool {
    // A fresh observation may begin after X Speed was already played.  The source identity is not
    // needed for this proof: any public ReducedRetreatCost only changes whether the offered
    // deterministic Retreat is legal, and it cannot change the later attached-Energy attack.
    if state
        .get_current_turn_effects()
        .iter()
        .any(|effect| !matches!(effect, TurnEffect::ReducedRetreatCost { .. }))
    {
        return false;
    }

    let Ok(value) = serde_json::to_value(state) else {
        return false;
    };
    let Some(turns) = value
        .get("turn_effects")
        .and_then(serde_json::Value::as_object)
    else {
        return false;
    };
    turns.iter().all(|(turn, effects)| {
        let Some(effects) = effects.as_array() else {
            return false;
        };
        turn.parse::<u8>()
            .map(|turn| turn <= state.turn_count || effects.is_empty())
            .unwrap_or(false)
    })
}

#[cfg(test)]
mod tests {
    use rand::{rngs::StdRng, SeedableRng};

    use crate::{
        card_ids::CardId,
        database::get_card_by_enum,
        models::PlayedCard,
        observation::RevealedKnowledge,
        Deck,
    };

    use super::*;

    fn apply_single(state: &State, action: &Action, seed: u64) -> State {
        let (probabilities, mut mutations) =
            crate::actions::try_forecast_action(state, action)
                .expect("registered prefix action must forecast")
                .into_branches();
        assert_eq!(probabilities, vec![1.0]);
        assert_eq!(mutations.len(), 1);
        let mut result = state.clone();
        mutations
            .pop()
            .expect("one branch was asserted")(
            &mut StdRng::seed_from_u64(seed),
            &mut result,
            action,
        );
        result
    }

    #[test]
    fn trusted_prefix_normalizes_only_the_single_opponent_draw_by_count() {
        let fixture: serde_json::Value = serde_json::from_str(include_str!(
            "../../tests/fixtures/public_reply_observed.json"
        ))
        .expect("saved public fixture must parse");
        let root: State = serde_json::from_value(fixture["row"]["state"].clone())
            .expect("saved root must deserialize");
        let observation =
            PlayerObservation::from_state(&root, 0, &RevealedKnowledge::default());
        let mut provenance = PublicReplyProvenance::from_observation(&observation);

        let thunderclaw = root
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|action| {
                matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Thunderclaw")
            })
            .expect("saved root must offer Thunderclaw");
        provenance = provenance.advance(&root, &thunderclaw);
        let after_attack = apply_single(&root, &thunderclaw, 11);
        let end_turn = after_attack.generate_possible_actions().1[0].clone();
        assert!(matches!(end_turn.action, SimpleAction::EndTurn));
        provenance = provenance.advance(&after_attack, &end_turn);
        let opponent_draw = apply_single(&after_attack, &end_turn, 13);
        assert_eq!(
            opponent_draw.move_generation_stack.last(),
            Some(&(1, vec![SimpleAction::DrawCard { amount: 1 }]))
        );

        for hand_count in [0, 9, 10] {
            for deck_count in [0, 1, 5] {
                let mut leaf = opponent_draw.clone();
                leaf.hands[1] = vec![get_card_by_enum(CardId::PA001Potion); hand_count];
                leaf.decks[1].cards =
                    vec![get_card_by_enum(CardId::A1001Bulbasaur); deck_count];
                assert!(matches!(
                    provenance.assess(&leaf, 0),
                    PublicReplyAssessment::ProvenImmediateWin { .. }
                ));
            }
        }

        let mut extra = opponent_draw.clone();
        extra
            .move_generation_stack
            .push((1, vec![SimpleAction::EndTurn]));
        assert!(matches!(
            provenance.assess(&extra, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::UnsupportedForcedTransition
            }
        ));
        let mut private = opponent_draw;
        private.move_generation_stack = vec![(1, Vec::new())];
        assert!(matches!(
            provenance.assess(&private, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::PrivateChoice
            }
        ));
    }

    #[test]
    fn sampled_deck_order_draw_downgrades_and_cannot_be_repaired_at_leaf() {
        let mut referee = State::default();
        referee.turn_count = 2;
        referee.current_player = 0;
        referee.decks[0].cards = [
            CardId::A1001Bulbasaur,
            CardId::A1005Caterpie,
            CardId::A1008Weedle,
            CardId::A1033Charmander,
            CardId::A1053Squirtle,
            CardId::A1094Pikachu,
        ]
        .into_iter()
        .map(get_card_by_enum)
        .collect();
        referee.move_generation_stack.push((
            0,
            vec![SimpleAction::DrawCard { amount: 1 }],
        ));

        let observation =
            PlayerObservation::from_state(&referee, 0, &RevealedKnowledge::default());
        let mut first_rng = StdRng::seed_from_u64(0);
        let first = observation.search_state(&mut first_rng);
        let second = (1..128)
            .find_map(|seed| {
                let mut rng = StdRng::seed_from_u64(seed);
                let candidate = observation.search_state(&mut rng);
                (candidate.decks[0].cards != first.decks[0].cards).then_some(candidate)
            })
            .expect("at least one seed must produce a distinct six-card ordering");

        let action = first.generate_possible_actions().1[0].clone();
        assert!(matches!(
            action.action,
            SimpleAction::DrawCard { amount: 1 }
        ));
        let provenance = PublicReplyProvenance::from_observation(&observation);
        let first_invalid = provenance.advance(&first, &action);
        let second_invalid = provenance.advance(&second, &action);
        assert!(!first_invalid.is_valid());
        assert!(!second_invalid.is_valid());

        let mut masked_leaf = first.clone();
        masked_leaf.decks[0].cards.fill(Card::Unknown);
        assert!(matches!(
            first_invalid.assess(&masked_leaf, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::HiddenOrder
            }
        ));
        assert!(matches!(
            second_invalid.assess(&second, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::HiddenOrder
            }
        ));
    }

    #[test]
    fn raw_state_provenance_is_never_proof_producing() {
        let mut state = State::default();
        state.turn_count = 2;
        assert!(matches!(
            PublicReplyProvenance::untrusted().assess(&state, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::UntrustedState
            }
        ));
    }

    #[test]
    fn self_counterattack_resolver_matches_generic_terminal_order() {
        let mut state = State::new(&Deck::default(), &Deck::default());
        state.turn_count = 13;
        state.current_player = 1;
        state.set_board(
            vec![PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(80)],
            vec![PlayedCard::from_id(CardId::B3b041MegaSableyeEx)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        );
        state.points[1] = 1;

        let action = state
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|candidate| {
                matches!(&candidate.action, SimpleAction::Attack(attack) if attack.title == "Cursed Jewel")
            })
            .expect("Cursed Jewel must be offered with its printed Energy");
        let kind = certified_attack_kind(match &action.action {
            SimpleAction::Attack(attack) => attack,
            _ => unreachable!("the selected action is an attack"),
        })
        .expect("Cursed Jewel must match the audited mechanic");
        let mut certified = certified_attack_successors(&state, &action, kind);
        assert_eq!(certified.len(), 1);
        assert_eq!(certified[0].0, 1.0);
        let certified = certified.pop().expect("one branch was asserted").1;

        let generic = apply_single(&state, &action, 91);
        assert_eq!(generic.winner, Some(GameOutcome::Win(1)));
        assert_eq!(certified.winner, generic.winner);
        assert_eq!(certified.points, generic.points);
        assert_eq!(certified.in_play_pokemon, generic.in_play_pokemon);
        assert_eq!(
            certified.own_knockouts_this_game,
            generic.own_knockouts_this_game
        );
        assert!(certified.move_generation_stack.is_empty());
        assert!(generic.move_generation_stack.is_empty());
        assert!(certified.get_active(1).get_active_effects().iter().any(
            |effect| matches!(effect, CardEffect::Counterattack { amount: 40 })
        ));
        assert!(generic.get_active(1).get_active_effects().iter().any(
            |effect| matches!(effect, CardEffect::Counterattack { amount: 40 })
        ));
    }

    #[test]
    fn self_counterattack_attack_is_explicitly_rejected_as_a_prefix() {
        let mut state = State::new(&Deck::default(), &Deck::default());
        state.turn_count = 13;
        state.current_player = 0;
        state.set_board(
            vec![PlayedCard::from_id(CardId::B3b041MegaSableyeEx)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
            vec![PlayedCard::from_id(CardId::A1076StarmieEx)],
        );
        let observation =
            PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let provenance = PublicReplyProvenance::from_observation(&observation);
        let action = state
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|candidate| {
                matches!(&candidate.action, SimpleAction::Attack(attack) if attack.title == "Cursed Jewel")
            })
            .expect("Cursed Jewel must be offered with its printed Energy");

        let invalid = provenance.advance(&state, &action);
        assert_eq!(
            invalid.invalid_reason,
            Some(UnsupportedReason::UnsupportedPrefixAction)
        );
        let after = apply_single(&state, &action, 97);
        assert!(after.get_active(0).get_active_effects().iter().any(
            |effect| matches!(effect, CardEffect::Counterattack { amount: 40 })
        ));
        assert!(matches!(
            invalid.assess(&after, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::UnsupportedPrefixAction
            }
        ));
    }
}
