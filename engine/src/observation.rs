//! Closed-list policy boundary. Unknown slots are counts, never invented card identities.
use crate::{
    actions::{abilities::AbilityMechanic, Action, SimpleAction},
    models::Card,
    State,
};
use rand::{rngs::StdRng, seq::SliceRandom};
use serde::{Deserialize, Serialize};
use std::cell::RefCell;

pub const INFORMATION_MODEL: &str = "closed-counts-unpriced-v7";

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct RevealedKnowledge {
    pub deck_top: [Vec<Card>; 2],
    pub opponent_hand: Vec<Card>,
    /// Unordered physical cards publicly known to remain somewhere in the opponent's deck.
    #[serde(default)]
    pub opponent_deck_membership: Vec<Card>,
}

/// Contains no actual unseen ordering, opponent deck list, or other player's private choices.
/// The private template is already redacted, including in Debug/serialized representations.
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PlayerObservation {
    pub actor: usize,
    pub information_model: &'static str,
    pub known_own_deck: Vec<Card>,
    pub revealed: RevealedKnowledge,
    template: State,
}

fn canonical_cards(cards: &mut [Card]) {
    cards.sort_by_key(Card::get_id);
}

pub fn canonical_actions(actions: &mut [Action]) {
    actions.sort_by_cached_key(|a| serde_json::to_string(a).expect("serializable action"));
}

impl PlayerObservation {
    pub fn from_state(state: &State, actor: usize, revealed: &RevealedKnowledge) -> Self {
        let opponent = 1 - actor;
        let mut template = state.clone();
        template.private_reveal_events.clear();
        template.public_reveal_events.clear();
        template.luxury_coin_resolution_events.clear();
        // Starting Pokemon remain face down until both setup EndTurn actions resolve.
        // An explicit mask distinguishes concealed slots from an actually empty board.
        template.setup_opponent_hidden = state.turn_count == 0;
        if template.setup_opponent_hidden {
            template.in_play_pokemon[opponent].fill(None);
        }
        let mut known_own_deck = std::mem::take(&mut template.decks[actor].cards);
        canonical_cards(&mut known_own_deck);
        template.hands[opponent].fill(Card::Unknown);
        template.decks[opponent].cards.fill(Card::Unknown);
        // The configured opposing energy menu is not a revealed deck list. Use only
        // currently visible zone types; future undisclosed energy is not priced.
        template.decks[opponent].energy_types.clear();
        // Pending private choices belong only to their chooser. Never pass another
        // player's discard/evolution/card-selection payloads through a public stack.
        for (chooser, choices) in &mut template.move_generation_stack {
            if *chooser != actor {
                choices.clear();
            } else {
                choices.sort_by_cached_key(|a| serde_json::to_string(a).unwrap());
            }
        }
        if template
            .pending_trainer_coin_choice
            .as_ref()
            .is_some_and(|pending| pending.actor != actor)
        {
            if let Some(pending) = template.pending_trainer_coin_choice.as_mut() {
                pending.route = None;
            }
        }
        if template
            .pending_misty_target_choice
            .as_ref()
            .is_some_and(|pending| pending.actor != actor)
        {
            if let Some(pending) = template.pending_misty_target_choice.as_mut() {
                pending.route = None;
            }
        }
        let mut revealed = revealed.clone();
        // An already-resolved reveal/selection grants these specific cards to its actor.
        // Do not infer the rest of a partially revealed hand from the actual State.
        if let Some((chooser, choices)) = state.move_generation_stack.last() {
            if *chooser == actor {
                let cards: Vec<Card> = choices
                    .iter()
                    .filter_map(|a| match a {
                        SimpleAction::ShuffleOpponentHandCard { card } => Some(card.clone()),
                        SimpleAction::DiscardOpponentSupporter { supporter_card } => {
                            Some(supporter_card.clone())
                        }
                        _ => None,
                    })
                    .collect();
                if !cards.is_empty() {
                    revealed.opponent_hand = cards;
                }
            }
        }
        canonical_cards(&mut revealed.opponent_hand);
        canonical_cards(&mut revealed.opponent_deck_membership);
        for (slot, card) in template.hands[opponent]
            .iter_mut()
            .zip(&revealed.opponent_hand)
        {
            *slot = card.clone();
        }
        for player in 0..2 {
            if player != actor {
                for (slot, card) in template.decks[player]
                    .cards
                    .iter_mut()
                    .zip(&revealed.deck_top[player])
                {
                    *slot = card.clone();
                }
            }
        }
        Self {
            actor,
            information_model: INFORMATION_MODEL,
            known_own_deck,
            revealed,
            template,
        }
    }

    /// Public board/flags, own hand, and unknown opponent slots. Own deck cards are
    /// available separately as an unordered multiset, never as an ordered State.
    pub fn visible_state(&self) -> &State {
        &self.template
    }

    /// One hypothetical own-deck ordering per decision, driven only by the search RNG.
    /// Opponent cards remain Unknown: no matchup prior is silently introduced.
    pub fn search_state(&self, rng: &mut StdRng) -> State {
        let mut state = self.template.clone();
        let mut remainder = self.known_own_deck.clone();
        let top = &self.revealed.deck_top[self.actor];
        for card in top {
            let index = remainder
                .iter()
                .position(|c| c == card)
                .expect("revealed own top cards must belong to the remaining deck multiset");
            remainder.remove(index);
        }
        remainder.shuffle(rng);
        state.decks[self.actor].cards = top.iter().cloned().chain(remainder).collect();
        state
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct UnpricedBranch {
    pub action: Action,
    #[serde(default)]
    pub root_action: Option<Action>,
    pub reason: String,
    #[serde(default = "default_occurrences")]
    pub occurrences: usize,
    #[serde(default)]
    pub selected: bool,
}

fn default_occurrences() -> usize {
    1
}

thread_local! {
    static UNPRICED: RefCell<Vec<Vec<UnpricedBranch>>> = const { RefCell::new(Vec::new()) };
    static ROOT_ACTIONS: RefCell<Vec<Action>> = const { RefCell::new(Vec::new()) };
}

pub(crate) fn collect_unpriced<T>(f: impl FnOnce() -> T) -> (T, Vec<UnpricedBranch>) {
    struct Scope;
    impl Drop for Scope {
        fn drop(&mut self) {
            UNPRICED.with(|s| {
                s.borrow_mut().pop();
            });
        }
    }
    UNPRICED.with(|s| s.borrow_mut().push(Vec::new()));
    let scope = Scope;
    let value = f();
    let branches = UNPRICED.with(|s| s.borrow().last().unwrap().clone());
    drop(scope);
    (value, branches)
}

pub(crate) fn current_root_action() -> Option<Action> {
    ROOT_ACTIONS.with(|roots| roots.borrow().last().cloned())
}

pub(crate) fn with_root_action<T>(root: &Action, f: impl FnOnce() -> T) -> T {
    ROOT_ACTIONS.with(|roots| roots.borrow_mut().push(root.clone()));
    struct Scope;
    impl Drop for Scope {
        fn drop(&mut self) {
            ROOT_ACTIONS.with(|roots| {
                roots.borrow_mut().pop();
            });
        }
    }
    let scope = Scope;
    let value = f();
    drop(scope);
    value
}

pub(crate) fn mark_selected(branches: &mut [UnpricedBranch], selected: &Action) {
    for branch in branches {
        if branch.root_action.as_ref() == Some(selected) {
            branch.selected = true;
        }
    }
}

pub(crate) fn record_unpriced(action: &Action, reason: &str) {
    let root_action = ROOT_ACTIONS.with(|roots| roots.borrow().last().cloned());
    UNPRICED.with(|s| {
        for branches in s.borrow_mut().iter_mut() {
            if let Some(existing) = branches.iter_mut().find(|branch| {
                branch.action == *action
                    && branch.root_action == root_action
                    && branch.reason == reason
            }) {
                existing.occurrences += 1;
            } else {
                branches.push(UnpricedBranch {
                    action: action.clone(),
                    root_action: root_action.clone(),
                    reason: reason.into(),
                    occurrences: 1,
                    selected: false,
                });
            }
        }
    });
}

/// Conservative boundary, deliberately over-inclusive for effects mentioning hidden
/// zones. Returning a static leaf here means "unpriced", not "effect has zero value".
pub fn hidden_continuation_reason(state: &State, action: &Action) -> Option<&'static str> {
    if state.setup_opponent_hidden && matches!(action.action, SimpleAction::EndTurn) {
        return Some("setup handoff or reveal requires the concealed opponent board");
    }
    // EndTurn bundles Checkup with automatic abilities at the next turn's start.
    // Unknown deck slots must not be mistaken for "no eligible Pokemon" by those
    // searches. Conservatively leave the bundled action unpriced until its phases
    // can be forecast separately; known deck identities remain forecastable. Use the
    // printed mechanic: suppression may disappear during Checkup when its source is KO'd.
    if matches!(action.action, SimpleAction::EndTurn | SimpleAction::ResolvePokemonCheckup
        | SimpleAction::FinishPokemonCheckup) && state.turn_count > 0 {
        use crate::actions::abilities::{AbilityMechanic, RandomEvolutionTrigger};
        let next = 1 - state.current_player;
        if state.decks[next].cards.contains(&Card::Unknown) {
            let mechanic = state.maybe_get_active(next)
                .and_then(|pokemon| crate::actions::get_ability_mechanic(&pokemon.card));
            if matches!(mechanic,
                Some(AbilityMechanic::StartTurnRandomPokemonToHand { .. })
                | Some(AbilityMechanic::RandomEvolutionFromDeck {
                    trigger: RandomEvolutionTrigger::EndOfOpponentTurnIfActive,
                })
            ) {
                return Some("automatic next-turn ability searches an unknown deck");
            }
        }
    }
    let evolving_player = match action.action {
        SimpleAction::ChooseRandomEvolutionTarget { .. } => Some(action.actor),
        SimpleAction::ResolveEndTurnEvolution { player } => Some(player),
        _ => None,
    };
    if evolving_player.is_some_and(|player| state.decks[player].cards.contains(&Card::Unknown)) {
        return Some("random evolution searches an unknown deck");
    }
    let unknown = |p: usize| {
        state.hands[p].contains(&Card::Unknown) || state.decks[p].cards.contains(&Card::Unknown)
    };
    if let Some((_, choices)) = state.move_generation_stack.last() {
        if choices.is_empty() {
            return Some("private pending choice is unavailable to this observer");
        }
    }
    if !unknown(0) && !unknown(1) {
        return None;
    }
    match &action.action {
        SimpleAction::DrawCard { amount }
            if state.hands[action.actor].len() < 10
                && state.decks[action.actor]
                    .cards
                    .iter()
                    .take(*amount as usize)
                    .any(|c| *c == Card::Unknown) =>
        {
            return Some("draw reaches an unknown card identity")
        }
        SimpleAction::DiscardOwnCards { cards } if cards.contains(&Card::Unknown) => {
            return Some("opponent chooses which unknown cards to discard")
        }
        _ => {}
    }
    // Boiler Smog's printed sentence mentions both "your hand" (the already-resolved
    // evolution trigger) and the opponent (the public Active receiving conditions). Its
    // pending UseAbility branch reads no hidden identity. Keep this mapped-mechanic
    // exception local; other hand/deck text retains the conservative default below.
    let public_board_only_ability = match &action.action {
        SimpleAction::UseAbility { in_play_idx } => state
            .in_play_pokemon
            .get(action.actor)
            .and_then(|board| board.get(*in_play_idx))
            .and_then(Option::as_ref)
            .and_then(|pokemon| crate::actions::get_ability_mechanic(&pokemon.card))
            .is_some_and(|mechanic| {
                matches!(
                    mechanic,
                    AbilityMechanic::PoisonAndBurnOpponentActiveOnEvolve
                )
            }),
        _ => false,
    };
    let text = match &action.action {
        SimpleAction::Play { trainer_card } => trainer_card.effect.clone(),
        SimpleAction::Attack(attack) | SimpleAction::ApplyQueuedAttackDamage { attack, .. } => {
            attack.effect.clone().unwrap_or_default()
        }
        SimpleAction::UseAbility { in_play_idx } => state.in_play_pokemon[action.actor]
            [*in_play_idx]
            .as_ref()
            .and_then(|p| p.card.get_ability())
            .map(|a| a.effect)
            .unwrap_or_default(),
        SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. } => state
            .pending_attack_coin_choice
            .as_ref()
            .filter(|pending| pending.actor == action.actor)
            .and_then(|pending| pending.attack.effect.clone())
            .unwrap_or_default(),
        SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. } => state
            .pending_trainer_coin_choice
            .as_ref()
            .filter(|pending| pending.actor == action.actor)
            .and_then(|pending| pending.route.as_ref())
            .map(|route| route.effect_trainer().effect.clone())
            .unwrap_or_default(),
        SimpleAction::ChooseMistyTarget { .. } => state
            .pending_misty_target_choice
            .as_ref()
            .filter(|pending| pending.actor == action.actor)
            .and_then(|pending| pending.route.as_ref())
            .map(|route| route.effect_trainer().effect.clone())
            .unwrap_or_default(),
        _ => String::new(),
    }
    .to_lowercase();
    if !public_board_only_ability
        && text.contains("opponent")
        && (text.contains("hand") || text.contains("deck"))
        && unknown(1 - action.actor)
    {
        return Some("effect or choice depends on unrevealed opponent cards");
    }
    if unknown(action.actor)
        && (text.contains("hand") || text.contains("deck") || text.contains("draw"))
    {
        return Some("effect depends on unknown cards in the acting player's hidden zones");
    }
    None
}

/// Knowledge comes from actual resolved actions, never from speculative search.
/// Losing track of an ambiguous zone change clears knowledge instead of inventing it.
pub(crate) fn update_knowledge(
    knowledge: &mut [RevealedKnowledge; 2],
    before: &State,
    after: &State,
    action: &Action,
) {
    // Cache an already authorized reveal before consuming its selection stack.
    knowledge[action.actor] =
        PlayerObservation::from_state(before, action.actor, &knowledge[action.actor]).revealed;
    // The initial attack action only samples a public coin batch when Victory Star pauses it.
    // Defer text-driven hidden-zone invalidation until Keep/Reroll actually commits the attack.
    let staged_attack = before.pending_attack_coin_choice.is_none()
        && after.pending_attack_coin_choice.is_some()
        && matches!(action.action, SimpleAction::Attack(_));
    let staged_trainer = before.pending_trainer_coin_choice.is_none()
        && after.pending_trainer_coin_choice.is_some()
        && matches!(
            action.action,
            SimpleAction::Play { .. } | SimpleAction::UseStadium
        );
    let staged_misty = before.pending_misty_target_choice.is_none()
        && after.pending_misty_target_choice.is_some()
        && matches!(
            action.action,
            SimpleAction::Play { .. } | SimpleAction::UseAbility { .. }
        );
    let misty_target_staged_coin = before.pending_misty_target_choice.is_some()
        && after.pending_trainer_coin_choice.is_some()
        && matches!(action.action, SimpleAction::ChooseMistyTarget { .. });
    let text = if staged_attack || staged_trainer || staged_misty || misty_target_staged_coin {
        String::new()
    } else {
        match &action.action {
            SimpleAction::Play { trainer_card } => trainer_card.effect.clone(),
            SimpleAction::Attack(attack) | SimpleAction::ApplyQueuedAttackDamage { attack, .. } => {
                attack.effect.clone().unwrap_or_default()
            }
            SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. } => before
                .pending_attack_coin_choice
                .as_ref()
                .filter(|pending| pending.actor == action.actor)
                .and_then(|pending| pending.attack.effect.clone())
                .unwrap_or_default(),
            SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. } => {
                before
                    .pending_trainer_coin_choice
                    .as_ref()
                    .filter(|pending| pending.actor == action.actor)
                    .map(|pending| match &pending.original_action {
                        SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
                            trainer_card.effect.clone()
                        }
                        _ => pending
                            .route
                            .as_ref()
                            .map(|route| route.effect_trainer().effect.clone())
                            .unwrap_or_default(),
                    })
                    .unwrap_or_default()
            }
            SimpleAction::ChooseMistyTarget { .. } => before
                .pending_misty_target_choice
                .as_ref()
                .filter(|pending| pending.actor == action.actor)
                .and_then(|pending| pending.route.as_ref().map(|route| (pending, route)))
                .map(|(pending, route)| match &pending.original_action {
                    SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
                        trainer_card.effect.clone()
                    }
                    _ => route.effect_trainer().effect.clone(),
                })
                .unwrap_or_default(),
            _ => format!("{:?}", action.action),
        }
    }
    .to_lowercase();
    // A Portrait observer cannot see whether its hidden source was Misty directly or Penny which
    // then copied Misty. Invalidate from the public outer action so retained deck facts cannot
    // reveal whether the concealed Penny shuffle occurred.
    let resolving_copied_misty = matches!(action.action, SimpleAction::ChooseMistyTarget { .. })
        && !misty_target_staged_coin
        && before
            .pending_misty_target_choice
            .as_ref()
            .is_some_and(|pending| match &pending.original_action {
                SimpleAction::UseAbility { .. } => true,
                SimpleAction::Play { trainer_card } => trainer_card.name == "Penny",
                _ => false,
            });
    let conservative_penny_resolution = !staged_trainer
        && !staged_misty
        && !misty_target_staged_coin
        && (matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
            || (matches!(
                &action.action,
                SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. }
            ) && before.pending_trainer_coin_choice.as_ref().is_some_and(|pending| {
                matches!(&pending.original_action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
            }))
            || resolving_copied_misty);
    let known_draw = matches!(&action.action, SimpleAction::DrawCard { .. })
        || matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Professor's Research");
    for (viewer, known) in knowledge.iter_mut().enumerate() {
        let opponent = 1 - viewer;
        let opponent_known_top_before = known.deck_top[opponent].clone();
        for p in 0..2 {
            if known_draw && p == action.actor {
                let drawn = before.decks[p]
                    .cards
                    .len()
                    .saturating_sub(after.decks[p].cards.len());
                // A known top card drawn by the opponent becomes known hand information.
                if p != viewer {
                    known
                        .opponent_hand
                        .extend(known.deck_top[p].iter().take(drawn).cloned());
                }
                known.deck_top[p].drain(..drawn.min(known.deck_top[p].len()));
            } else if before.decks[p].cards != after.decks[p].cards || text.contains("shuffle") {
                known.deck_top[p].clear();
            }
        }
        if conservative_penny_resolution {
            known.deck_top[0].clear();
            known.deck_top[1].clear();
        }
        let before_len = before.decks[opponent].cards.len();
        let after_len = after.decks[opponent].cards.len();
        if after_len < before_len {
            let removed = before_len - after_len;
            let known_prefix = &opponent_known_top_before;
            if known_draw && action.actor == opponent && known_prefix.len() >= removed {
                for card in known_prefix.iter().take(removed) {
                    if let Some(index) = known
                        .opponent_deck_membership
                        .iter()
                        .position(|known| known == card)
                    {
                        known.opponent_deck_membership.remove(index);
                    }
                }
            } else {
                known.opponent_deck_membership.clear();
            }
        } else if conservative_penny_resolution
            || action_may_remove_from_deck(action, opponent, &text)
        {
            known.opponent_deck_membership.clear();
        }
        if let SimpleAction::BenchOpponentHandBasics { cards } = &action.action {
            if opponent == 1 - action.actor {
                for card in cards {
                    if let Some(index) = known.opponent_hand.iter().position(|known| known == card)
                    {
                        known.opponent_hand.remove(index);
                    }
                }
                continue;
            }
        }
        let selected = match &action.action {
            SimpleAction::ShuffleOpponentHandCard { card } if opponent == 1 - action.actor => {
                Some(card)
            }
            SimpleAction::DiscardOpponentSupporter { supporter_card }
                if opponent == 1 - action.actor =>
            {
                Some(supporter_card)
            }
            _ => None,
        };
        if let Some(card) = selected {
            if let Some(index) = known.opponent_hand.iter().position(|c| c == card) {
                known.opponent_hand.remove(index);
            }
        } else if known_draw && opponent == action.actor {
            if let SimpleAction::Play { trainer_card } = &action.action {
                let card = Card::Trainer(trainer_card.clone());
                if let Some(index) = known.opponent_hand.iter().position(|c| c == &card) {
                    known.opponent_hand.remove(index);
                }
            }
        } else if conservative_penny_resolution
            || before.hands[opponent] != after.hands[opponent]
            || text.contains("shuffle")
        {
            known.opponent_hand.clear();
        }
    }
    for event in after.private_reveal_events.iter() {
        if event.zone_owner != 1 - event.viewer {
            continue;
        }
        match event.kind {
            crate::state::PrivateRevealKind::RandomHandCard => {
                for card in &event.cards {
                    if !knowledge[event.viewer].opponent_hand.contains(card) {
                        knowledge[event.viewer].opponent_hand.push(card.clone());
                    }
                }
            }
            crate::state::PrivateRevealKind::WholeHand => {
                knowledge[event.viewer].opponent_hand = event.cards.clone();
            }
        }
    }
    for event in after.public_reveal_events.iter() {
        let viewer = 1 - event.zone_owner;
        match event.kind {
            crate::state::PublicRevealKind::DeckPrefixThenShuffle => {
                merge_multiset_lower_bound(
                    &mut knowledge[viewer].opponent_deck_membership,
                    &event.cards,
                );
                canonical_cards(&mut knowledge[viewer].opponent_deck_membership);
                knowledge[viewer].deck_top[event.zone_owner].clear();
                knowledge[event.zone_owner].deck_top[event.zone_owner].clear();
            }
        }
    }
    let actor = action.actor;
    if let SimpleAction::Play { trainer_card } = &action.action {
        match trainer_card.name.as_str() {
            "Hand Scope" | "Silver" => {
                knowledge[actor].opponent_hand = after.hands[1 - actor].clone()
            }
            "Pokédex" => {
                knowledge[actor].deck_top[actor] =
                    after.decks[actor].cards.iter().take(3).cloned().collect()
            }
            "Rotom Dex" => {
                knowledge[actor].deck_top[actor] =
                    after.decks[actor].cards.iter().take(1).cloned().collect()
            }
            _ => {}
        }
    }
    if let SimpleAction::UseAbility { in_play_idx } = &action.action {
        if let Some(ability) = before.in_play_pokemon[actor][*in_play_idx]
            .as_ref()
            .and_then(|p| p.card.get_ability())
        {
            if ability.title == "Data Scan" {
                knowledge[actor].deck_top[actor] =
                    after.decks[actor].cards.iter().take(1).cloned().collect();
            }
        }
    }
}

/// Whether the public action semantics allow at least one card to leave `deck_owner`'s deck.
/// This deliberately does not compare concealed card identities: equal public counts can hide a
/// swap, and a removal can be masked by adding more cards than were removed.
fn action_may_remove_from_deck(action: &Action, deck_owner: usize, text: &str) -> bool {
    if matches!(&action.action, SimpleAction::ChooseRandomEvolutionTarget { .. }
        | SimpleAction::ResolveEndTurnEvolution { .. }) {
        return action.actor == deck_owner;
    }
    if matches!(&action.action, SimpleAction::DrawCard { .. }) {
        return action.actor == deck_owner;
    }
    if !text.contains("deck") {
        return false;
    }

    let removal_words = text.contains("draw")
        || text.contains("from your deck")
        || text.contains("from their deck")
        || text.contains("from its deck")
        || text.contains("discard the top")
        || (text.contains("discard") && text.contains("deck"))
        || (text.contains("put") && text.contains("into your hand"));
    if !removal_words {
        // Pure reveals/shuffles and one-way additions preserve every established member.
        return false;
    }

    // Do not infer ownership from disconnected pronouns. For example, Chatot's Mimic removes
    // cards from your deck but also mentions the opponent's hand. Once public text permits a deck
    // removal, clearing either observer's opponent-membership lower bound is conservative.
    true
}

fn merge_multiset_lower_bound(existing: &mut Vec<Card>, observed: &[Card]) {
    let mut identities = observed.to_vec();
    canonical_cards(&mut identities);
    identities.dedup();
    for identity in identities {
        let observed_count = observed.iter().filter(|card| **card == identity).count();
        let existing_count = existing.iter().filter(|card| **card == identity).count();
        existing.extend(std::iter::repeat_n(
            identity,
            observed_count.saturating_sub(existing_count),
        ));
    }
}

#[cfg(test)]
mod attribution_tests {
    use super::*;
    use crate::{
        card_ids::CardId,
        database::get_card_by_enum,
        models::Attack,
        state::{
            MistySourceRoute, PendingAttackCoinChoice, PendingMistyTargetChoice,
            PendingTrainerCoinChoice, TrainerCoinEffectRoute,
        },
    };

    fn end_turn() -> Action {
        Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        }
    }

    #[test]
    fn root_attribution_counts_occurrences_and_keeps_reasons_separate() {
        let root_a = end_turn();
        let root_b = Action {
            actor: 0,
            action: SimpleAction::Noop,
            is_stack: false,
        };
        let child = Action {
            actor: 1,
            action: SimpleAction::Noop,
            is_stack: true,
        };
        let (_value, mut branches) = collect_unpriced(|| {
            with_root_action(&root_a, || {
                record_unpriced(&child, "same cutoff");
                record_unpriced(&child, "same cutoff");
                record_unpriced(&child, "different reason");
            });
            with_root_action(&root_b, || record_unpriced(&child, "same cutoff"));
        });
        assert_eq!(branches.len(), 3);
        assert_eq!(
            branches
                .iter()
                .find(|b| b.root_action.as_ref() == Some(&root_a) && b.reason == "same cutoff")
                .unwrap()
                .occurrences,
            2
        );
        assert_eq!(
            branches
                .iter()
                .find(|b| b.root_action.as_ref() == Some(&root_a) && b.reason == "different reason")
                .unwrap()
                .occurrences,
            1
        );
        assert_eq!(
            branches
                .iter()
                .find(|b| b.root_action.as_ref() == Some(&root_b))
                .unwrap()
                .occurrences,
            1
        );
        mark_selected(&mut branches, &root_b);
        assert!(
            !branches
                .iter()
                .find(|b| b.root_action.as_ref() == Some(&root_a))
                .unwrap()
                .selected
        );
        assert!(
            branches
                .iter()
                .find(|b| b.root_action.as_ref() == Some(&root_b))
                .unwrap()
                .selected
        );
    }

    fn hidden_zone_attack() -> Attack {
        Attack {
            energy_required: Vec::new(),
            title: "Astonish".into(),
            fixed_damage: 0,
            effect: Some("Flip a coin. If heads, your opponent reveals a random card from their hand and shuffles it into their deck.".into()),
        }
    }

    fn pending_state() -> State {
        let mut state = State::default();
        state.hands[1].push(Card::Unknown);
        state.decks[1].cards.push(Card::Unknown);
        state.pending_attack_coin_choice = Some(PendingAttackCoinChoice {
            actor: 0,
            attack: hidden_zone_attack(),
            original_is_stack: false,
            flips: vec![true],
            victory_star_in_play_idx: 1,
        });
        state.move_generation_stack.push((
            0,
            vec![
                SimpleAction::KeepAttackCoinResults,
                SimpleAction::RerollAttackCoins {
                    victory_star_in_play_idx: 1,
                },
            ],
        ));
        state
    }

    #[test]
    fn victory_star_choices_inherit_the_pending_attacks_hidden_zone_cutoff() {
        let state = pending_state();
        for action in state
            .move_generation_stack
            .last()
            .unwrap()
            .1
            .iter()
            .cloned()
        {
            let action = Action {
                actor: 0,
                action,
                is_stack: true,
            };
            assert_eq!(
                hidden_continuation_reason(&state, &action),
                Some("effect or choice depends on unrevealed opponent cards"),
            );
        }
    }

    #[test]
    fn victory_star_commit_uses_original_attack_text_to_invalidate_knowledge() {
        let before = pending_state();
        let mut after = before.clone();
        after.pending_attack_coin_choice = None;
        after.move_generation_stack.clear();
        let known_card = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut knowledge = [RevealedKnowledge::default(), RevealedKnowledge::default()];
        knowledge[0].opponent_hand.push(known_card.clone());
        knowledge[0].deck_top[1].push(known_card);

        update_knowledge(
            &mut knowledge,
            &before,
            &after,
            &Action {
                actor: 0,
                action: SimpleAction::KeepAttackCoinResults,
                is_stack: true,
            },
        );

        assert!(knowledge[0].opponent_hand.is_empty());
        assert!(knowledge[0].deck_top[1].is_empty());
    }

    #[test]
    fn staging_victory_star_does_not_invalidate_knowledge_before_attack_commit() {
        let mut before = pending_state();
        before.pending_attack_coin_choice = None;
        before.move_generation_stack.clear();
        let after = pending_state();
        let known_hand = get_card_by_enum(CardId::A1001Bulbasaur);
        let known_top = get_card_by_enum(CardId::A1033Charmander);
        let mut knowledge = [RevealedKnowledge::default(), RevealedKnowledge::default()];
        knowledge[0].opponent_hand.push(known_hand.clone());
        knowledge[0].deck_top[1].push(known_top.clone());

        update_knowledge(
            &mut knowledge,
            &before,
            &after,
            &Action {
                actor: 0,
                action: SimpleAction::Attack(hidden_zone_attack()),
                is_stack: false,
            },
        );

        assert_eq!(knowledge[0].opponent_hand, vec![known_hand]);
        assert_eq!(knowledge[0].deck_top[1], vec![known_top]);
    }

    fn pending_penny(copied: CardId) -> State {
        let mut state = State::default();
        let penny = get_card_by_enum(CardId::A3b069Penny).as_trainer();
        state.pending_trainer_coin_choice = Some(PendingTrainerCoinChoice {
            actor: 0,
            original_action: SimpleAction::Play {
                trainer_card: penny,
            },
            original_is_stack: false,
            flips: vec![false],
            luxury_coin_in_play_idx: 1,
            misty_target_in_play_idx: None,
            route: Some(TrainerCoinEffectRoute::Penny {
                copied: get_card_by_enum(copied).as_trainer(),
                shuffle_owner: 1,
            }),
        });
        state.move_generation_stack.push((
            0,
            vec![
                SimpleAction::KeepTrainerCoinResults,
                SimpleAction::RerollTrainerCoins {
                    luxury_coin_in_play_idx: 1,
                },
            ],
        ));
        state
    }

    fn penny_commit_knowledge(copied: CardId, deck_changes: bool) -> [RevealedKnowledge; 2] {
        let mut before = pending_penny(copied);
        before.decks[1].cards = vec![
            get_card_by_enum(CardId::A1001Bulbasaur),
            get_card_by_enum(CardId::A1033Charmander),
        ];
        let mut after = before.clone();
        after.pending_trainer_coin_choice = None;
        after.move_generation_stack.clear();
        let known = get_card_by_enum(CardId::A1001Bulbasaur);
        if deck_changes {
            after.decks[1].cards.reverse();
        }
        let mut knowledge = [RevealedKnowledge::default(), RevealedKnowledge::default()];
        for entry in &mut knowledge {
            entry.deck_top[0] = vec![known.clone()];
            entry.deck_top[1] = vec![known.clone()];
            entry.opponent_deck_membership = vec![known.clone()];
            entry.opponent_hand = vec![known.clone()];
        }
        update_knowledge(
            &mut knowledge,
            &before,
            &after,
            &Action {
                actor: 0,
                action: SimpleAction::KeepTrainerCoinResults,
                is_stack: true,
            },
        );
        knowledge
    }

    #[test]
    fn hidden_penny_source_cannot_change_post_commit_knowledge() {
        let misty = penny_commit_knowledge(CardId::A1220Misty, false);
        let researcher = penny_commit_knowledge(CardId::B4a069TeamRocketsResearcher, false);
        assert_eq!(misty, researcher);
        for knowledge in misty {
            assert!(knowledge.deck_top.iter().all(Vec::is_empty));
            assert!(knowledge.opponent_deck_membership.is_empty());
            assert!(knowledge.opponent_hand.is_empty());
        }
    }

    #[test]
    fn penny_shuffle_invalidates_known_top_even_when_permutation_matches() {
        let same = penny_commit_knowledge(CardId::A1220Misty, false);
        let changed = penny_commit_knowledge(CardId::A1220Misty, true);
        assert_eq!(same, changed);
        assert!(same
            .iter()
            .all(|knowledge| knowledge.deck_top.iter().all(Vec::is_empty)));
    }

    fn membership_after_same_length_hidden_swap(replacement: Card) -> Vec<Card> {
        let known = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut before = State::default();
        before.decks[1].cards = vec![known.clone()];
        let mut after = before.clone();
        after.decks[1].cards = vec![replacement];
        let mut knowledge = [RevealedKnowledge::default(), RevealedKnowledge::default()];
        knowledge[0].opponent_deck_membership = vec![known];
        update_knowledge(
            &mut knowledge,
            &before,
            &after,
            &Action {
                actor: 1,
                action: SimpleAction::Attack(Attack {
                    energy_required: Vec::new(),
                    title: "Hidden Swap".into(),
                    fixed_damage: 0,
                    effect: Some("Put 1 card from your deck into your hand. Then shuffle 1 card from your hand into your deck.".into()),
                }),
                is_stack: false,
            },
        );
        knowledge[0].opponent_deck_membership.clone()
    }

    #[test]
    fn membership_invalidation_cannot_distinguish_same_from_different_hidden_swap() {
        let same =
            membership_after_same_length_hidden_swap(get_card_by_enum(CardId::A1001Bulbasaur));
        let different =
            membership_after_same_length_hidden_swap(get_card_by_enum(CardId::A1033Charmander));
        assert_eq!(same, different);
        assert!(same.is_empty());
    }

    #[test]
    fn chatot_membership_clears_when_draw_is_masked_by_net_deck_growth() {
        let known = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut before = State::default();
        before.decks[1].cards = vec![known.clone(), get_card_by_enum(CardId::PA001Potion)];
        let mut after = before.clone();
        after.decks[1].cards = vec![
            get_card_by_enum(CardId::A1033Charmander),
            get_card_by_enum(CardId::PA001Potion),
            get_card_by_enum(CardId::PB088TeamRocketsScyther),
        ];
        let mut knowledge = [RevealedKnowledge::default(), RevealedKnowledge::default()];
        knowledge[0].opponent_deck_membership = vec![known];
        update_knowledge(
            &mut knowledge,
            &before,
            &after,
            &Action {
                actor: 1,
                action: SimpleAction::Attack(Attack {
                    energy_required: Vec::new(),
                    title: "Mimic".into(),
                    fixed_damage: 0,
                    effect: Some("Shuffle your hand into your deck. Draw a card for each card in your opponent's hand.".into()),
                }),
                is_stack: false,
            },
        );
        assert!(knowledge[0].opponent_deck_membership.is_empty());
    }

    #[test]
    fn portrait_misty_knowledge_does_not_reveal_hidden_nested_penny_source() {
        let misty = get_card_by_enum(CardId::A1220Misty).as_trainer();
        let penny = get_card_by_enum(CardId::A3b069Penny).as_trainer();
        let original_action = SimpleAction::UseAbility { in_play_idx: 0 };
        let action = Action {
            actor: 0,
            action: SimpleAction::ChooseMistyTarget { in_play_idx: 1 },
            is_stack: true,
        };
        let known = get_card_by_enum(CardId::PA001Potion);
        let mut direct = State::default();
        direct.pending_misty_target_choice = Some(PendingMistyTargetChoice {
            actor: 0,
            original_action: original_action.clone(),
            original_is_stack: false,
            route: Some(MistySourceRoute::Portrait {
                misty: misty.clone(),
            }),
        });
        direct
            .move_generation_stack
            .push((0, vec![SimpleAction::ChooseMistyTarget { in_play_idx: 1 }]));
        let mut nested = direct.clone();
        nested.pending_misty_target_choice.as_mut().unwrap().route =
            Some(MistySourceRoute::PortraitPenny {
                penny,
                misty,
                shuffle_owner: 1,
            });
        let mut direct_after = direct.clone();
        direct_after.pending_misty_target_choice = None;
        direct_after.move_generation_stack.pop();
        let mut nested_after = nested.clone();
        nested_after.pending_misty_target_choice = None;
        nested_after.move_generation_stack.pop();

        let initial = RevealedKnowledge {
            deck_top: [vec![known.clone()], vec![known.clone()]],
            opponent_hand: vec![known.clone()],
            opponent_deck_membership: vec![known],
        };
        let mut direct_knowledge = [initial.clone(), initial.clone()];
        let mut nested_knowledge = [initial.clone(), initial];
        update_knowledge(&mut direct_knowledge, &direct, &direct_after, &action);
        update_knowledge(&mut nested_knowledge, &nested, &nested_after, &action);
        assert_eq!(direct_knowledge, nested_knowledge);
        for knowledge in direct_knowledge {
            assert!(knowledge.deck_top[0].is_empty());
            assert!(knowledge.deck_top[1].is_empty());
            assert!(knowledge.opponent_deck_membership.is_empty());
        }
    }
}
