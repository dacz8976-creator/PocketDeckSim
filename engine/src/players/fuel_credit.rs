//! kpf's part F and the diagnostic kpg (registered Sept 26: `rl/results/kpf_2026-09-26/REGISTRATION.md`, section 4):
//! a credit for a side's discard-pile Energy when that side can pull it back.
//!
//! credit = K × min(E, CAP), K = 15, CAP = 4 (§117's pre-set constants, never fitted here). E counts the side's
//! discard-pile Energy that R's projection didn't already put on the Active, and only Energy an available recovery
//! source can move.
//!
//! The recovery class is every card whose effect attaches Energy from its owner's discard pile to a Pokémon, found
//! from the card texts (the test below walks every card and fails on one it doesn't classify). Today: Dragon's Blessing
//! (Dragonair B4 117), Combust (Flareon ex A3b 009), Flame Patch (B1 217), Professor Sada (B3a 072), Lusamine
//! (A3a 069) and Volkner (A2 153), reprints included. No attack, Tool or Stadium does it today; a Tool or Stadium that
//! does would be read through the same text table.
//!
//! Who can see what (Dustin's condition two):
//! - The own side (the evaluating player): a source in play, or among its own cards not yet discarded (hand or deck).
//! - The opponent's side: only a source visible in play that can use its effect as its text allows (a Pokémon with the
//!   Ability, holder position included, or a Tool or Stadium in play). Never its hand, deck or list.
//!
//! A source counts only Energy it can move, to a Pokémon it can target, under its play conditions. On the own side a
//! target may be in play or in its own remaining cards; on the opponent's side it must be in play.
use crate::{
    actions::{abilities::AbilityMechanic, get_ability_mechanic, get_in_play_ability_mechanic},
    hooks::{is_ancient_pokemon, is_ultra_beast},
    models::{Card, EnergyType, PlayedCard, TrainerCard},
    State,
};

/// §117's constants (s117_prereg.txt: "15.0 × min(4, …) … fixed here, not tuned").
pub(crate) const FUEL_CREDIT_PER_ENERGY: f64 = 15.0;
pub(crate) const FUEL_CREDIT_CAP: usize = 4;

/// Which Pokémon a recovery effect can attach to.
#[derive(Debug, Clone, Copy, PartialEq)]
enum RecoveryTarget {
    /// The owner's Active Pokémon of this type (Dragon's Blessing: [N]; Flame Patch: [R]).
    ActiveOfType(EnergyType),
    /// The holder of the Ability itself (Combust).
    Holder,
    /// Ancient Pokémon (Professor Sada).
    Ancient,
    /// Ultra Beasts (Lusamine).
    UltraBeast,
    /// Pokémon with one of these names (Volkner: Electivire or Luxray).
    Named(&'static [&'static str]),
}

/// One recovery effect: the Energy it can move (`None` = any type), what it can attach to, whether its holder must be
/// on the Bench (an Ability's own position condition), and whether the opponent must have a point (Lusamine).
#[derive(Debug, Clone, Copy, PartialEq)]
struct Recovery {
    moves: Option<EnergyType>,
    target: RecoveryTarget,
    holder_on_bench: bool,
    needs_opponent_point: bool,
}

/// The recovery effect of an Ability mechanic, if it has one.
fn ability_recovery(mechanic: &AbilityMechanic) -> Option<Recovery> {
    match mechanic {
        // Dragon's Blessing: "if this Pokémon is on your Bench, you may attach an Energy from your discard pile to
        // your Active [N] Pokémon."
        AbilityMechanic::AttachEnergyFromDiscardToActiveTypedFromBench { energy_type } => Some(Recovery {
            moves: None,
            target: RecoveryTarget::ActiveOfType(*energy_type),
            holder_on_bench: true,
            needs_opponent_point: false,
        }),
        // Combust: "attach a [R] Energy from your discard pile to this Pokémon."
        AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage { energy_type, .. } => Some(Recovery {
            moves: Some(*energy_type),
            target: RecoveryTarget::Holder,
            holder_on_bench: false,
            needs_opponent_point: false,
        }),
        _ => None,
    }
}

const FLAME_PATCH: &str = "Attach a [R] Energy from your discard pile to your Active [R] Pokémon.";
const PROFESSOR_SADA: &str = "Attach 3 different types of Energy from your discard pile to your Ancient Pokémon in any way you like.";
const LUSAMINE: &str = "You can use this card only if your opponent has gotten at least 1 point.Choose 1 of your Ultra Beasts. Attach 2 random Energy from your discard pile to that Pokémon.";
const VOLKNER: &str = "Choose 1 of your Electivire or Luxray. Attach 2 [L] Energy from your discard pile to that Pokémon.";

/// The recovery effect of a Trainer card (Item, Supporter, Tool or Stadium), keyed on its printed text.
fn trainer_recovery(trainer: &TrainerCard) -> Option<Recovery> {
    let (moves, target, needs_opponent_point) = match trainer.effect.as_str() {
        FLAME_PATCH => (Some(EnergyType::Fire), RecoveryTarget::ActiveOfType(EnergyType::Fire), false),
        PROFESSOR_SADA => (None, RecoveryTarget::Ancient, false),
        LUSAMINE => (None, RecoveryTarget::UltraBeast, true),
        VOLKNER => (Some(EnergyType::Lightning), RecoveryTarget::Named(&["Electivire", "Luxray"]), false),
        _ => return None,
    };
    Some(Recovery { moves, target, holder_on_bench: false, needs_opponent_point })
}

/// Whether `card` (in its owner's hand or deck) qualifies as `target`.
fn card_qualifies(card: &Card, target: RecoveryTarget) -> bool {
    let Card::Pokemon(pokemon) = card else { return false };
    match target {
        RecoveryTarget::ActiveOfType(energy_type) => pokemon.energy_type == energy_type,
        RecoveryTarget::Holder => false,
        RecoveryTarget::Ancient => is_ancient_pokemon(&pokemon.name),
        RecoveryTarget::UltraBeast => is_ultra_beast(&pokemon.name),
        RecoveryTarget::Named(names) => names.contains(&pokemon.name.as_str()),
    }
}

/// Whether the in-play `pokemon` qualifies as `target`.
fn in_play_qualifies(state: &State, pokemon: &PlayedCard, target: RecoveryTarget) -> bool {
    match target {
        RecoveryTarget::ActiveOfType(energy_type) => state.pokemon_is_type(pokemon, energy_type),
        RecoveryTarget::Holder => false,
        RecoveryTarget::Ancient => is_ancient_pokemon(&pokemon.get_name()),
        RecoveryTarget::UltraBeast => is_ultra_beast(&pokemon.get_name()),
        RecoveryTarget::Named(names) => names.contains(&pokemon.get_name().as_str()),
    }
}

/// The Energy types `side` can pull back from its discard pile now or later, as far as the evaluator may know:
/// `None` in the result means any type. `own` is true for the evaluating player's side.
fn movable_types(state: &State, side: usize, own: bool) -> Vec<Option<EnergyType>> {
    let opponent = 1 - side;
    let remaining: Vec<&Card> = if own {
        state.hands[side].iter().chain(state.decks[side].cards.iter()).collect()
    } else {
        Vec::new()
    };
    let has_target = |recovery: &Recovery, holder_counts: bool| -> bool {
        holder_counts && recovery.target == RecoveryTarget::Holder
            || state.enumerate_in_play_pokemon(side).any(|(_, p)| in_play_qualifies(state, p, recovery.target))
            || remaining.iter().any(|card| card_qualifies(card, recovery.target))
    };
    let usable = |recovery: &Recovery| !recovery.needs_opponent_point || state.points[opponent] >= 1;
    let mut moves = Vec::new();
    // Pokémon in play with a recovery Ability (switched off ones don't count); on the opponent's side its holder must
    // sit where the text lets it act.
    for (slot, pokemon) in state.enumerate_in_play_pokemon(side) {
        if let Some(recovery) = get_in_play_ability_mechanic(state, pokemon).and_then(ability_recovery) {
            let position_ok = own || !recovery.holder_on_bench || slot != 0;
            if position_ok && usable(&recovery) && has_target(&recovery, true) {
                moves.push(recovery.moves);
            }
        }
        for tool in &pokemon.attached_tools {
            if let Card::Trainer(trainer) = tool {
                if let Some(recovery) = trainer_recovery(trainer) {
                    if usable(&recovery) && has_target(&recovery, false) {
                        moves.push(recovery.moves);
                    }
                }
            }
        }
    }
    if let Some(Card::Trainer(stadium)) = state.active_stadium.as_ref() {
        if let Some(recovery) = trainer_recovery(stadium) {
            if usable(&recovery) && has_target(&recovery, false) {
                moves.push(recovery.moves);
            }
        }
    }
    // The own side's cards not yet discarded: Pokémon with a recovery Ability and recovery Trainers.
    for card in &remaining {
        let recovery = match card {
            Card::Pokemon(_) => get_ability_mechanic(card).and_then(ability_recovery),
            Card::Trainer(trainer) => trainer_recovery(trainer),
            _ => None,
        };
        if let Some(recovery) = recovery {
            if usable(&recovery) && has_target(&recovery, true) {
                moves.push(recovery.moves);
            }
        }
    }
    moves
}

/// kpf's part F for `side`: K × min(E, CAP), where E counts the Energy in `discard` (the side's discard pile less what
/// R's projection already used) that an available recovery source can move. `own` is true for the evaluating player.
pub(crate) fn fuel_credit(state: &State, side: usize, own: bool, discard: &[EnergyType]) -> f64 {
    if discard.is_empty() {
        return 0.0;
    }
    let movable = movable_types(state, side, own);
    let fuel = discard
        .iter()
        .filter(|energy| movable.iter().any(|moves| moves.is_none_or(|t| t == **energy)))
        .count();
    FUEL_CREDIT_PER_ENERGY * fuel.min(FUEL_CREDIT_CAP) as f64
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{card_ids::CardId, database::get_card_by_enum};
    use strum::IntoEnumIterator;

    /// The class is defined by what a card does: every card whose text attaches Energy "from your discard pile" is
    /// classified, and nothing else is. A new card with such a text fails here until it is added to the tables above.
    #[test]
    fn every_discard_energy_recovery_card_is_classified() {
        let mut classified = Vec::new();
        for id in CardId::iter() {
            let card = get_card_by_enum(id);
            let (texts, recovery): (Vec<String>, Option<Recovery>) = match &card {
                Card::Pokemon(p) => (
                    p.ability.iter().map(|a| a.effect.clone())
                        .chain(p.attacks.iter().filter_map(|a| a.effect.clone())).collect(),
                    get_ability_mechanic(&card).and_then(ability_recovery),
                ),
                Card::Trainer(t) => (vec![t.effect.clone()], trainer_recovery(t)),
                _ => (Vec::new(), None),
            };
            let recovers = texts.iter().any(|t| t.contains("from your discard pile") && t.contains("Energy") && t.to_lowercase().contains("attach"));
            assert_eq!(recovers, recovery.is_some(), "{} ({}): texts {texts:?}", card.get_name(), card.get_id());
            if recovery.is_some() {
                classified.push(card.get_name());
            }
        }
        classified.sort();
        classified.dedup();
        assert_eq!(classified, ["Dragonair", "Flame Patch", "Flareon ex", "Lusamine", "Professor Sada", "Volkner"]);
        // Dragonair's other printings have no Ability; only B4 117's does.
        assert!(get_ability_mechanic(&get_card_by_enum(CardId::B4117Dragonair)).and_then(ability_recovery).is_some());
    }

    fn board(state: &mut State, side: usize, ids: &[CardId]) {
        for (slot, id) in ids.iter().enumerate() {
            state.in_play_pokemon[side][slot] = Some(PlayedCard::from_id(*id));
        }
    }

    fn fresh() -> State {
        let mut state = State::default();
        state.turn_count = 5;
        state.decks[0].cards.clear();
        state.decks[1].cards.clear();
        state
    }

    const FIRE: EnergyType = EnergyType::Fire;

    /// The own side: Dragonair on the Bench, or in the own deck with a Dragon Pokémon to target, turns the credit on;
    /// with neither, it's off.
    #[test]
    fn the_own_side_counts_a_source_in_play_or_in_its_own_cards() {
        let discard = [FIRE, FIRE];
        let mut state = fresh();
        board(&mut state, 0, &[CardId::B4120MegaRayquazaEx]);
        assert_eq!(fuel_credit(&state, 0, true, &discard), 0.0, "no recovery source anywhere");
        state.decks[0].cards.push(get_card_by_enum(CardId::B4117Dragonair));
        assert_eq!(fuel_credit(&state, 0, true, &discard), 30.0, "a Dragonair still in the own deck");
        state.decks[0].cards.clear();
        board(&mut state, 0, &[CardId::B4120MegaRayquazaEx, CardId::B4117Dragonair]);
        assert_eq!(fuel_credit(&state, 0, true, &discard), 30.0, "a Dragonair on the own Bench");
        // Flame Patch in the own hand moves only [R] and needs a [R] Pokémon.
        let mut state = fresh();
        board(&mut state, 0, &[CardId::A1033Charmander]);
        state.hands[0].push(get_card_by_enum(CardId::B1217FlamePatch));
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE, EnergyType::Water]), 15.0, "Flame Patch moves the [R] only");
        board(&mut state, 0, &[CardId::A1053Squirtle]);
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE]), 0.0, "no [R] Pokémon to attach to");
    }

    /// The opponent's side: only a visible source that can act. A Dragonair on its Bench counts; in its Active Spot it
    /// can't use Dragon's Blessing, so it doesn't; one in its hand or deck is never read, nor is a Flame Patch there.
    #[test]
    fn the_opponents_side_counts_only_a_visible_source_that_can_act() {
        let discard = [FIRE, FIRE];
        let mut state = fresh();
        board(&mut state, 1, &[CardId::B4120MegaRayquazaEx, CardId::B4117Dragonair]);
        assert_eq!(fuel_credit(&state, 1, false, &discard), 30.0, "Dragonair on the opponent's Bench");
        board(&mut state, 1, &[CardId::B4117Dragonair]);
        state.in_play_pokemon[1][1] = None;
        assert_eq!(fuel_credit(&state, 1, false, &discard), 0.0, "Dragonair in the opponent's Active Spot");
        let mut state = fresh();
        board(&mut state, 1, &[CardId::A1033Charmander]);
        state.decks[1].cards.push(get_card_by_enum(CardId::B4117Dragonair));
        state.hands[1].push(get_card_by_enum(CardId::B1217FlamePatch));
        assert_eq!(fuel_credit(&state, 1, false, &discard), 0.0, "the opponent's deck and hand are never read");
        assert_eq!(fuel_credit(&state, 1, true, &discard), 30.0, "the same cards count for their owner");
    }

    /// Lusamine needs the opponent to have a point; Combust moves [R] onto its holder.
    #[test]
    fn play_conditions_and_holders_count() {
        let mut state = fresh();
        board(&mut state, 0, &[CardId::A3a043GuzzlordEx]);
        state.hands[0].push(get_card_by_enum(CardId::A3a069Lusamine));
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE]), 0.0, "the opponent has no point yet");
        state.points[1] = 1;
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE]), 15.0);
        let mut state = fresh();
        board(&mut state, 1, &[CardId::A3b009FlareonEx]);
        assert_eq!(fuel_credit(&state, 1, false, &[FIRE, EnergyType::Water]), 15.0, "Combust: [R] onto itself");
    }

    /// The cap: at most 4 Energy count, 60.
    #[test]
    fn the_credit_is_capped_at_four_energy() {
        let mut state = fresh();
        board(&mut state, 0, &[CardId::B4120MegaRayquazaEx, CardId::B4117Dragonair]);
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE; 3]), 45.0);
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE; 4]), 60.0);
        assert_eq!(fuel_credit(&state, 0, true, &[FIRE; 7]), 60.0);
    }
}
