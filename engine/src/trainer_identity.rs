//! One implementation per Trainer effect, however many printings carry it.
//!
//! Trainer logic used to be keyed by `CardId`, so every alternate-art or reprint of a Supporter or
//! Item had to be listed by hand in both `move_generation_trainer.rs` and
//! `apply_trainer_action.rs`, and a new printing of an old card showed up as "Trainer logic not
//! implemented" until someone did. Attacks, Abilities and Tools are keyed by their effect text
//! instead, which is what makes them robust to new printings.
//!
//! This module gives Trainers the same property. [`canonical_trainer_id`] maps any Trainer card
//! to the *first* printing (in `CardId` order) that carries the same effect text, so the two
//! `match` statements only need to name that one printing, and a reprint resolves to it with no
//! code change. In the current database every Trainer name has exactly one effect text, and the
//! only effect text shared across names is the Fossil one, which is dispatched before the match.
//!
//! This fork looks the canonical printing up by id first (upstream's #395 reads the card's effect
//! text): a table built once from the database maps every Trainer printing to the first `CardId`
//! with the same name and effect text, so dispatch never depends on the copy of the text that a
//! card object (in a saved state, say) carries. Only an id the table does not know falls back to
//! upstream's effect-text lookup. The two agree on every printing but the Fossils, which the table
//! keeps apart by name (an Old Amber reprint resolves to A1 218 Old Amber, not to A1 216 Helix
//! Fossil).

use std::collections::HashMap;
use std::sync::LazyLock;

use strum::IntoEnumIterator;

use crate::{card_ids::CardId, database::get_card_by_enum, models::Card, models::TrainerCard};

/// Effect text -> the first `CardId` (in enum order) of a Trainer printed with that text.
static CANONICAL_BY_EFFECT: LazyLock<HashMap<String, CardId>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    for id in CardId::iter() {
        if let Card::Trainer(trainer) = get_card_by_enum(id) {
            map.entry(trainer.effect).or_insert(id);
        }
    }
    map
});

/// Trainer printing -> the first `CardId` (in enum order) of a Trainer with the same name and
/// effect text.
static CANONICAL_BY_ID: LazyLock<HashMap<CardId, CardId>> = LazyLock::new(|| {
    let mut first: HashMap<(String, String), CardId> = HashMap::new();
    let mut map = HashMap::new();
    for id in CardId::iter() {
        if let Card::Trainer(trainer) = get_card_by_enum(id) {
            let canonical = *first.entry((trainer.name, trainer.effect)).or_insert(id);
            map.insert(id, canonical);
        }
    }
    map
});

/// The printing that carries this Trainer's implementation: the first `CardId` with the same
/// name and effect text. "First" is `CardId` enum order, which is set order with the promo sets
/// last, so a promo card that was later reprinted in a Deluxe Pack resolves to the Deluxe Pack
/// printing. For a card that is itself the first printing this is its own id. The card's id is
/// looked up first; only an id the database does not have falls back to the card's effect text.
/// Returns `None` only for a card whose id and effect text are both unknown, which cannot happen
/// for a card that came out of the database.
pub fn canonical_trainer_id(trainer_card: &TrainerCard) -> Option<CardId> {
    CardId::from_card_id(&trainer_card.id)
        .and_then(|id| CANONICAL_BY_ID.get(&id).copied())
        .or_else(|| {
            CANONICAL_BY_EFFECT
                .get(trainer_card.effect.as_str())
                .copied()
        })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::TrainerType;

    #[test]
    fn a_first_printing_is_its_own_canonical() {
        let Card::Trainer(copycat) = get_card_by_enum(CardId::B1225Copycat) else {
            panic!("B1 225 should be a Trainer");
        };
        assert_eq!(canonical_trainer_id(&copycat), Some(CardId::B1225Copycat));
    }

    #[test]
    fn reprints_resolve_to_the_first_printing() {
        for (reprint, first) in [
            (CardId::B1270Copycat, CardId::B1225Copycat),
            (CardId::B4b225Copycat, CardId::B1225Copycat),
            (CardId::B4b424Copycat, CardId::B1225Copycat),
            // Promo ids sort after every set in `CardId` order, so the Deluxe Pack printing
            // is the canonical one for Professor's Research, not P-A 007.
            (
                CardId::PA007ProfessorsResearch,
                CardId::A4b373ProfessorsResearch,
            ),
            (CardId::A4b329Erika, CardId::A1219Erika),
        ] {
            let Card::Trainer(card) = get_card_by_enum(reprint) else {
                panic!("{reprint:?} should be a Trainer");
            };
            assert_eq!(canonical_trainer_id(&card), Some(first), "{reprint:?}");
        }
    }

    /// Every Trainer in the database resolves, and to a printing with the same name and type:
    /// the guard that keeps effect-text keying honest if a future set ever reuses a text.
    #[test]
    fn every_trainer_resolves_to_a_same_named_printing() {
        for id in CardId::iter() {
            let Card::Trainer(card) = get_card_by_enum(id) else {
                continue;
            };
            let canonical = canonical_trainer_id(&card).unwrap_or_else(|| panic!("{id:?}"));
            let Card::Trainer(first) = get_card_by_enum(canonical) else {
                panic!("{canonical:?} should be a Trainer");
            };
            if card.trainer_card_type == TrainerType::Fossil {
                // All Fossils share one text and are played as Pokémon, never dispatched by id.
                continue;
            }
            assert_eq!(first.name, card.name, "{id:?} -> {canonical:?}");
            assert_eq!(first.trainer_card_type, card.trainer_card_type, "{id:?}");
        }
    }

    /// This fork's id-first lookup: a known id resolves through the database, whatever effect text
    /// the card object carries.
    #[test]
    fn a_known_id_resolves_whatever_text_the_card_carries() {
        let Card::Trainer(mut erika) = get_card_by_enum(CardId::A4b329Erika) else {
            panic!("A4b 329 should be a Trainer");
        };
        erika.effect = "A text no printing has.".to_string();
        assert_eq!(canonical_trainer_id(&erika), Some(CardId::A1219Erika));
    }

    /// Only an id the database does not know falls back to the effect text, as upstream reads it.
    #[test]
    fn an_unknown_id_falls_back_to_the_effect_text() {
        let Card::Trainer(mut copycat) = get_card_by_enum(CardId::B4b424Copycat) else {
            panic!("B4b 424 should be a Trainer");
        };
        copycat.id = "TEST 001".to_string();
        assert_eq!(canonical_trainer_id(&copycat), Some(CardId::B1225Copycat));
        copycat.effect = "A text no printing has.".to_string();
        assert_eq!(canonical_trainer_id(&copycat), None);
    }

    /// The id table keys on name and text, so each Fossil name keeps its own canonical printing
    /// (upstream's text-only lookup sends every Fossil to A1 216 Helix Fossil).
    #[test]
    fn a_fossil_resolves_to_the_first_printing_of_its_name() {
        for (fossil, first) in [
            (CardId::A1216HelixFossil, CardId::A1216HelixFossil),
            (CardId::A1217DomeFossil, CardId::A1217DomeFossil),
            (CardId::A4b313OldAmber, CardId::A1218OldAmber),
        ] {
            let Card::Trainer(card) = get_card_by_enum(fossil) else {
                panic!("{fossil:?} should be a Trainer");
            };
            assert_eq!(canonical_trainer_id(&card), Some(first), "{fossil:?}");
        }
    }
}
