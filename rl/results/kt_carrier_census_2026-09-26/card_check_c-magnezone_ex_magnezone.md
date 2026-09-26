# Card-text check: c-magnezone_ex_magnezone.txt (kt carrier census, "Magnezone ex Magnezone")

Date: 2026-09-26. Deck file: `rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt` (Limitless archetype "Magnezone ex Magnezone", deck id magnezone-ex-b3-magnezone-b1a; warpis, 6th of 97, The Breakfast Club Xastur's Showdown-$5+OAK+, 2026-08-28; provenance in `provenance/c-magnezone_ex_magnezone.json`). This file reports; it decides nothing.

How it was checked (B2e's method, `rl/results/b2e_card_check_2026-09-26/card_check_arch_manectric.md`): for each of the 15 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` (database `lib/deckgym-database.json`; the raw entry was read for the Trainer subtype, field `trainer_card_type`), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched on the same day (all 15 fetches succeeded). Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and punctuation differences (Pokémon/Pokemon) are ignored.

Coverage flags came from the official `rl/engine-2026-09-25/goldfish` (sha256 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997, the hash in `rl/engine-2026-09-25/README.md`) run in WSL: `goldfish --deck rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt --games 0 --panel decks/screen/opponents --coverage rl/results/kt_carrier_census_2026-09-26/coverage_c-magnezone_ex_magnezone.json` (0 games played, exit 0). The raw output is in `coverage_c-magnezone_ex_magnezone.json` next to this file.

## Summary

- Cards checked: 15 of 15 (all verified against Limitless).
- Mismatches: 1, low severity (Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning; the same difference B2e reported and refuted as wording only).
- High-severity mismatches: none. Every HP, type, stage, weakness, retreat cost, attack cost, damage figure, effect text, ability text and Trainer subtype matches.
- Formatting only, not counted: Teal Mask Ogerpon ex's Energized Leaves is shown as "60+" on Limitless and as the integer 60 in the engine, with the identical effect sentence (the database has no notation field; same convention as B2e's Electrike and Rattata notes). The ex rule box on Magnezone ex and Teal Mask Ogerpon ex ("When your Pokémon ex is Knocked Out, your opponent gets 2 points") has no database field and is applied in engine code.
- Coverage flags: 2. Copycat is flagged "unpriced text rule" (its text reads the opponent's hand, which k3 does not price; kp3's public pricing addresses this; Copycat is also in all eight panel lists). Magnezone B1a 026's Mirror Shot is flagged "pays off on the opponent's turn" (the coin-flip attack lock lasts through it; k3 never searches that turn). No card is flagged for printed-damage estimation, for an engine limitation, or as not implemented. All 15 report "Fully implemented".
- Untrusted-prone? Partly: the flagged attack belongs to the deck's secondary attacker (1 Magnezone B1a 026 beside 1 Magnezone ex B3 054, whose Storm Blade carries no flag). The main attacker is clean.
- The census card in this list is Protective Poncho B2 147 (group 4 in `cards.md`: a full Bench prevention, priced at 0 by the kt draft; not a switch-1 card). Its engine text matches Limitless.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Magnemite (B1a 024) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 50 / Fighting / 1 | 50 / Fighting / 1 | match |
|   |  | Attack: Electro Ball | [L] 30, no effect | [L] 30, no effect | match |
|   |  | Ability | none | none | match |
| 2 | Magneton (A1 098) | Type / stage | Lightning, Stage 1 from Magnemite | Lightning, Stage 1, evolves from Magnemite | match |
|   |  | HP / weakness / retreat | 80 / Fighting / 2 | 80 / Fighting / 2 | match |
|   |  | Ability: Volt Charge | "Once during your turn, you may take a [L] Energy from your Energy Zone and attach it to this Pokémon." | "Once during your turn, you may take a [L] Energy from your Energy Zone and attach it to this Pokémon." | match |
|   |  | Attack: Spinning Attack | [LCCC] 60, no effect | [LCCC] 60, no effect | match |
| 3 | Magnezone ex (B3 054) | Type / stage | Lightning, Stage 2 from Magneton | Lightning, Stage 2, evolves from Magneton | match |
|   |  | HP / weakness / retreat | 180 / Fighting / 2 | 180 / Fighting / 2 | match |
|   |  | Attack: Storm Blade | [LLL] 130. "Discard a [L] Energy from this Pokémon." | [LLL] 130. "Discard a [L] Energy from this Pokémon." | match |
|   |  | Ability / rule box | none; ex rule applied in code | none; "ex rule: When your Pokémon ex is Knocked Out, your opponent gets 2 points." | match (rule handled by engine code) |
| 4 | Magnezone (B1a 026) | Type / stage | Lightning, Stage 2 from Magneton | Lightning, Stage 2, evolves from Magneton | match |
|   |  | HP / weakness / retreat | 150 / Fighting / 2 | 150 / Fighting / 2 | match |
|   |  | Attack: Mirror Shot | [LCC] 90. "During your opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that attack doesn't happen." | [LCC] 90. "During your opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that attack doesn't happen." | match |
|   |  | Ability | none | none | match |
| 5 | Oricorio (A3 066) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 70 / Fighting / 1 | 70 / Fighting / 1 | match |
|   |  | Ability: Safeguard | "Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex." | "Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex." | match |
|   |  | Attack: Zzzap | [LC] 50, no effect | [LC] 50, no effect | match |
| 6 | Teal Mask Ogerpon ex (B2 017) | Type / stage | Grass, Basic (Stage 0) | Grass, Basic | match |
|   |  | HP / weakness / retreat | 130 / Fire / 1 | 130 / Fire / 1 | match |
|   |  | Ability: Soothing Wind | "Each of your Pokémon that has any Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions." | "Each of your Pokémon that has any Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions." | match |
|   |  | Attack: Energized Leaves | [GG] 60. "If the amount of Energy attached to both Active Pokémon is 5 or more, this attack does 60 more damage." | [GG] 60+. "If the amount of Energy attached to both Active Pokémon is 5 or more, this attack does 60 more damage." | match ("+" notation only) |
|   |  | Rule box | ex rule applied in code | "ex rule: When your Pokémon ex is Knocked Out, your opponent gets 2 points." | match (rule handled by engine code) |
| 7 | Professor's Research (P-A 007) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 8 | Lisia (B1 226) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Put 2 random Basic Pokémon with 50 HP or less from your deck into your hand." | "Put 2 random Basic Pokémon with 50 HP or less from your deck into your hand." | match |
| 9 | Clemont (B1a 068) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Put 2 random cards from among Magneton, Heliolisk, and Clemont's Backpack from your deck into your hand." | "Put 2 random cards from among Magneton, Heliolisk, and Clemont's Backpack from your deck into your hand." | match |
| 10 | Copycat (B1 225) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 11 | Pokémon Center Lady (A2b 070) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | match |
| 12 | Sabrina (A1 225) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | match |
| 13 | Cyrus (A2 150) | Trainer type | Supporter | Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 14 | Poké Ball (P-A 005) | Trainer type | Item | Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning; B2e refuted it as wording only) |
| 15 | Protective Poncho (B2 147) | Trainer type | Tool | Pokémon Tool | match |
|   |  | Text | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Magnemite (B1a 024) | Fully implemented | none | - | - | - |
| Magneton (A1 098) | Fully implemented | none | - | - | - |
| Magnezone ex (B3 054) | Fully implemented | none | - | - | - |
| Magnezone (B1a 026) | Fully implemented | none | - | - | FLAGGED ("attack Mirror Shot": the attack lock lasts through the opponent's turn) |
| Oricorio (A3 066) | Fully implemented | none | - | - | - |
| Teal Mask Ogerpon ex (B2 017) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Lisia (B1 226) | Fully implemented | none | - | - | - |
| Clemont (B1a 068) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Pokémon Center Lady (A2b 070) | Fully implemented | none | - | - | - |
| Sabrina (A1 225) | Fully implemented | none | - | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Protective Poncho (B2 147) | Fully implemented | none | - | - | - |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Two flags fired: Copycat (unpriced) and Magnezone's Mirror Shot (opponent's turn).

## Unverified

None. All 15 cards were read from both sources.
