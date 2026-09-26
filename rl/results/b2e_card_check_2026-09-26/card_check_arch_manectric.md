# Card-text check: h-manectric.txt (arch:manectric)

Date: 2026-09-26. Deck file: `rl/results/b2e_card_check_2026-09-26/decks/h-manectric.txt` (Limitless archetype "Mega Manectric ex Heliolisk").

How it was checked: for each of the 13 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` (database `lib/deckgym-database.json`, raw entry read for the Trainer subtype), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched on the same day. Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and punctuation differences (Pokémon/Pokemon) are ignored.

Coverage flags came from `rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel decks/screen/opponents --coverage rl/results/b2e_card_check_2026-09-26/coverage_arch_manectric.json` run in WSL (0 games played). The raw output is in `coverage_arch_manectric.json` next to this file.

## Summary

- Cards checked: 13 of 13 (all verified against Limitless).
- Mismatches: 1, low severity (Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning).
- High-severity mismatches: none. Every HP, type, stage, weakness, retreat cost, attack cost, damage figure and effect matches.
- Coverage flags: 1. Copycat is flagged "unpriced text rule" (its text reads the opponent's hand, which the k3 bot does not price). No card is flagged for printed-damage estimation, for paying off on the opponent's turn, for an engine limitation, or as not implemented. All 13 report "Fully implemented".
- Note on Mega Manectric ex: Limitless prints the Mega Evolution ex rule box ("When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points"). The engine's database entry has no field for that rule, but the engine's rules code gives 3 points for knocking out any Pokémon whose name starts with "Mega " (`engine/src/models/card.rs`, `is_mega`), so the rule is honored. Not counted as a mismatch.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Helioptile (B1a 028) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 60 / Fighting / 1 | 60 / Fighting / 1 | match |
|   |  | Attack: Thunder Shock | [L] 10. "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed." | [L] 10. "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed." | match |
|   |  | Ability | none | none | match |
| 2 | Heliolisk (B4 061) | Type / stage | Lightning, Stage 1 from Helioptile | Lightning, Stage 1, evolves from Helioptile | match |
|   |  | HP / weakness / retreat | 80 / Fighting / 1 | 80 / Fighting / 1 | match |
|   |  | Attack: Electrispark | [L] 40. "This attack also does 10 damage to each of your opponent's Benched Pokémon." | [L] 40. "This attack also does 10 damage to each of your opponent's Benched Pokémon." | match |
|   |  | Ability | none | none | match |
| 3 | Electrike (B2b 026) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 60 / Fighting / 1 | 60 / Fighting / 1 | match |
|   |  | Attack: Quick Attack | [L] 10. "Flip a coin. If heads, this attack does 30 more damage." | [L] 10+. "Flip a coin. If heads, this attack does 30 more damage." | match |
|   |  | Ability | none | none | match |
| 4 | Mega Manectric ex (B2b 027) | Type / stage | Lightning, Stage 1 from Electrike | Lightning, Stage 1, evolves from Electrike | match |
|   |  | HP / weakness / retreat | 180 / Fighting / 0 | 180 / Fighting / 0 | match |
|   |  | Attack: Lightning Accelerator | [LL] 80. "This attack does 30 more damage for each point you have gotten." | [LL] 80+. "This attack does 30 more damage for each point you have gotten." | match |
|   |  | Ability | none | none (rule box only: Mega Evolution ex, 3 points when Knocked Out) | match; rule handled by engine code, see note |
| 5 | Clemont (B1a 068) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Put 2 random cards from among Magneton, Heliolisk, and Clemont's Backpack from your deck into your hand." | "Put 2 random cards from among Magneton, Heliolisk, and Clemont's Backpack from your deck into your hand." | match |
| 6 | Professor's Research (P-A 007) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 7 | Copycat (B1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 8 | Cyrus (A2 150) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 9 | Clemont's Backpack (B1a 066) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "During this turn, attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon." | "During this turn, attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon." | match |
| 10 | Poké Ball (P-A 005) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning) |
| 11 | Field Blower (B3 147) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | match |
| 12 | Elegant Cape (B3b 065) | Trainer type | Tool | Trainer - Tool (Pokémon Tool) | match |
|   |  | Text | "The Stage 1 Pokémon this card is attached to gets +30 HP." | "The Stage 1 Pokémon this card is attached to gets +30 HP." | match |
| 13 | Training Area (B2 153) | Trainer type | Stadium | Trainer - Stadium | match |
|   |  | Text | "Attacks used by Stage 1 Pokémon in play (both yours and your opponent's) do +10 damage to the opponent's Active Pokémon." | "Attacks used by Stage 1 Pokémon in play (both yours and your opponent's) do +10 damage to the opponent's Active Pokémon." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Helioptile (B1a 028) | Fully implemented | none | - | - | - |
| Heliolisk (B4 061) | Fully implemented | none | - | - | - |
| Electrike (B2b 026) | Fully implemented | none | - | - | - |
| Mega Manectric ex (B2b 027) | Fully implemented | none | - | - (Lightning Accelerator's per-point bonus is priced by the estimator) | - |
| Clemont (B1a 068) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Clemont's Backpack (B1a 066) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Field Blower (B3 147) | Fully implemented | none | - | - | - |
| Elegant Cape (B3b 065) | Fully implemented | none | - | - | - |
| Training Area (B2 153) | Fully implemented | none | - | - | - |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Only the first class fired, on Copycat.

## Unverified

None. All 13 cards were read from both sources.
