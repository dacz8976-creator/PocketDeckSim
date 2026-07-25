use deckgym::{actions::EFFECT_MECHANIC_MAP, card_ids::CardId, test_support::nth_attack};

/// Effect texts newly mapped by reusing an existing parameterized `Mechanic`.
///
/// The risk in this class of change is not logic — every mechanic here is already implemented and
/// covered elsewhere — it is transcribing a wrong number, or picking the wrong
/// `include_fixed_damage` for a "does N damage" versus "does N *more* damage" phrasing. Both fail
/// silently at runtime: games simply score wrong. This table pins every parameter so a typo fails
/// loudly instead.
///
/// `Mechanic` lives in a private module, so the expectation is written as its `Debug` rendering
/// rather than the value — comparing formatted output keeps the assertion at the public API
/// surface instead of widening upstream visibility just for a test.
const EXPECTED: &[(&str, &str)] = &[
    (
        "Heal 20 damage from each of your Pokémon.",
        "HealAllYourPokemon { amount: 20 }",
    ),
    (
        "Heal 50 damage from 1 of your Benched Pokémon.",
        "HealOneYourBenchedPokemon { amount: 50 }",
    ),
    (
        "Heal 20 damage from 1 of your Pokémon.",
        "HealOneYourPokemon { amount: 20 }",
    ),
    (
        "If this Pokémon's remaining HP is 30 or less, this attack does 60 more damage.",
        "ExtraDamageIfSelfHpAtMost { threshold: 30, extra_damage: 60 }",
    ),
    (
        "This attack does 20 damage to each of your opponent's Pokémon.",
        "DamageAllOpponentPokemon { damage: 20 }",
    ),
    (
        "This attack does 40 more damage for each Energy in your opponent's Active Pokémon's Retreat Cost.",
        "ExtraDamagePerRetreatCost { damage_per_energy: 40 }",
    ),
    (
        "Flip 2 coins. If both of them are heads, this attack does 20 more damage.",
        "ExtraDamageIfBothHeads { extra_damage: 20 }",
    ),
    // "40 MORE damage" — Lugia's Aeroblast keeps its printed 80 base on top of the coin damage.
    (
        "Flip 2 coins. This attack does 40 more damage for each heads.",
        "ExtraDamageForEachHeads { include_fixed_damage: true, damage_per_head: 40, num_coins: 2 }",
    ),
    // No "more": for this phrasing the printed fixed_damage IS the per-heads value (the same
    // convention as Golurk's 100 and Zapdos ex's 50), so the base must not be added again.
    (
        "Flip 3 coins. This attack does 30 damage for each heads.",
        "ExtraDamageForEachHeads { include_fixed_damage: false, damage_per_head: 30, num_coins: 3 }",
    ),
    (
        "If a Stadium is in play, this attack does 40 more damage.",
        "ExtraDamageIfStadiumInPlay { extra_damage: 40 }",
    ),
    (
        "If your opponent's Active Pokémon has damage on it, this attack does 50 more damage.",
        "ExtraDamageIfHurt { extra_damage: 50, opponent: true }",
    ),
    (
        "This attack does 70 damage to 1 of your opponent's Benched Pokémon.",
        "DirectDamage { damage: 70, bench_only: true }",
    ),
    (
        "If you played a Supporter card from your hand during this turn, this attack does 60 more damage.",
        "ExtraDamageIfSupportPlayedThisTurn { extra_damage: 60 }",
    ),
    (
        "This attack also does 50 damage to 1 of your opponent's Benched Pokémon.",
        "AlsoChoiceBenchDamage { opponent: true, damage: 50 }",
    ),
    (
        "If your opponent's Active Pokémon is Confused, this attack does 40 more damage.",
        "ExtraDamageIfDefenderConfused { extra_damage: 40 }",
    ),
];

fn normalize(s: &str) -> String {
    s.split_whitespace().collect::<Vec<_>>().join(" ")
}

#[test]
fn test_free_tier_effects_map_to_expected_mechanics() {
    for (text, expected_debug) in EXPECTED {
        let actual = EFFECT_MECHANIC_MAP
            .get(text)
            .unwrap_or_else(|| panic!("effect text is not mapped: {text}"));
        assert_eq!(
            normalize(&format!("{actual:?}")),
            normalize(expected_debug),
            "wrong mechanic or parameters mapped for: {text}"
        );
    }
}

/// Each mapped text must match its card's printed text byte for byte. `EFFECT_MECHANIC_MAP` is
/// keyed on the raw effect string, so a single stray character leaves the map entry dead and the
/// card still unimplemented — with nothing failing to say so.
#[test]
fn test_free_tier_effect_texts_match_the_printed_cards() {
    let samples = [
        (
            CardId::A4010Meganium,
            "Heal 20 damage from each of your Pokémon.",
        ),
        (
            CardId::B2076Indeedee,
            "This attack does 70 damage to 1 of your opponent's Benched Pokémon.",
        ),
        (
            CardId::B2131Lugia,
            "Flip 2 coins. This attack does 40 more damage for each heads.",
        ),
        (
            CardId::B2a028Palafin,
            "This attack also does 50 damage to 1 of your opponent's Benched Pokémon.",
        ),
        (
            CardId::B3068Oricorio,
            "If your opponent's Active Pokémon is Confused, this attack does 40 more damage.",
        ),
        (
            CardId::B2a074Tinkaton,
            "During your next turn, this Pokémon can't use Gigaton Hammer.",
        ),
    ];

    for (card_id, text) in samples {
        assert_eq!(
            nth_attack(card_id, 0).effect.as_deref(),
            Some(text),
            "{card_id:?}'s printed effect text does not match the mapped key"
        );
    }
}
