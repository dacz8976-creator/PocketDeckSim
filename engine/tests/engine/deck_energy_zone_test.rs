// Ported from upstream deckgym-core #344 (the two tests in src/deck.rs `mod tests`), adapted to this fork's narrow version.
//
// The fork takes only the Dragon/Colorless rejection: an empty Energy list is NOT rejected by
// `Deck::is_valid` here (the hidden-information templates clear the opponent's Energy on
// purpose), so nothing below asserts on an empty list.

use deckgym::{models::EnergyType, Deck};

/// The Energy Zone cannot generate Dragon or Colorless energy, so a deck declaring either is not
/// buildable in-game. This is easy to get wrong when energy is inferred from a deck's Pokémon
/// types rather than its attack costs: an all-Dragon deck yields `Energy: Dragon`, which is not
/// playable.
#[test]
fn test_is_valid_rejects_non_selectable_energy() {
    // Sabrina, Cyrus, Pokémon Center Lady, 2 Oricorio, Pichu, May, 2 Copycat, 2 Dratini,
    // 2 Dragonair, Mega Rayquaza ex, 2 Rainbow Cave, 2 Poké Ball, 2 Professor's Research: 20 cards.
    let cards = "\n1 A1 225\n1 A2 150\n1 A2b 70\n2 A3 66\n1 A4 66\n1 B1 223\n2 B1 225\n2 B2b 51\n2 B4 117\n1 B4 120\n2 B4 155\n2 P-A 5\n2 P-A 7";

    for energy in ["Dragon", "Colorless"] {
        let deck = Deck::from_string(&format!("Energy: {energy}{cards}"))
            .expect("deck should still parse");
        assert_eq!(deck.cards.len(), 20);
        assert!(
            deck.cards.iter().filter(|c| c.is_basic()).count() >= 1,
            "deck should otherwise be legal, so only the energy is at fault"
        );
        assert!(!deck.is_valid(), "{energy} energy zone should be rejected");
    }

    // Same 20 cards, but declaring energy the Energy Zone can actually make.
    let deck = Deck::from_string(&format!("Energy: Fire, Lightning{cards}")).unwrap();
    assert!(deck.is_valid());

    // A mix is only as valid as its worst member.
    let deck = Deck::from_string(&format!("Energy: Fire, Dragon{cards}")).unwrap();
    assert!(!deck.is_valid());
}

#[test]
fn test_energy_type_is_selectable() {
    // Upstream iterates `EnergyType::SELECTABLE`; this fork has no such constant, so the eight
    // Energy Zone types are listed here.
    for energy in [
        EnergyType::Grass,
        EnergyType::Fire,
        EnergyType::Water,
        EnergyType::Lightning,
        EnergyType::Psychic,
        EnergyType::Fighting,
        EnergyType::Darkness,
        EnergyType::Metal,
    ] {
        assert!(energy.is_selectable(), "{energy:?} should be selectable");
    }
    assert!(!EnergyType::Dragon.is_selectable());
    assert!(!EnergyType::Colorless.is_selectable());
}
