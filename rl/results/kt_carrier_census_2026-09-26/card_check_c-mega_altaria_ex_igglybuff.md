# Card-text check: c-mega_altaria_ex_igglybuff.txt (Limitless archetype "Mega Altaria ex Igglybuff")

Date: 2026-09-26. Deck file: `rl/results/kt_carrier_census_2026-09-26/decks/c-mega_altaria_ex_igglybuff.txt` (khaeruibnum, 10th of 73, Sauna X Ev4de POG Tournament #27, 2026-09-11; provenance in `provenance/c-mega_altaria_ex_igglybuff.json`). This file reports; it decides nothing and changes no rule.

How it was checked (the B2e method, `rl/results/b2e_card_check_2026-09-26/card_check_arch_manectric.md`): for each of the 12 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` run from the repo root (database `lib/deckgym-database.json`; the raw entry was read for the Trainer subtype, HP, weakness and retreat fields), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched on the same day (all 12 fetches succeeded; none was refused). Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and punctuation differences (Pokémon/Pokemon) are ignored.

`python lib/deck_check.py files rl/results/kt_carrier_census_2026-09-26/decks/c-mega_altaria_ex_igglybuff.txt` printed "decks clean", exit 0 (no WARN). Every id resolves to "1 printings, 1 distinct" in card.py. The file is UTF-8 without BOM, LF line endings, 20 cards.

Coverage flags came from `rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel decks/screen/opponents --coverage rl/results/kt_carrier_census_2026-09-26/coverage_c-mega_altaria_ex_igglybuff.json` run in WSL from the repo root (0 games played, exit 0; the binary's sha256 was checked at run time as 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997, the hash `rl/engine-2026-09-25/README.md` lists for goldfish). The raw output is in `coverage_c-mega_altaria_ex_igglybuff.json` next to this file.

## Summary

- Cards checked: 12 of 12 (all verified against Limitless). Unverified: none.
- Mismatches: 1, low severity (Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning; the same item B2e reported and refuted as wording only).
- High-severity mismatches: none. Every HP, type, stage, weakness, retreat cost, attack cost, damage figure, effect text, ability text and Trainer subtype matches.
- Formatting notes, not counted as mismatches: Mega Altaria ex's Mega Harmony shows "40+" on Limitless and the integer 40 in the engine with the identical sentence "This attack does 30 more damage for each of your Benched Pokémon." (the database has no notation field; the same convention B2e noted for Team Rocket's Rattata). Limitless prints the Mega Evolution ex rule box on Mega Altaria ex ("When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points"); the database entry has no field for it, and B2e recorded that the engine applies it in code (`engine/src/models/card.rs`, `is_mega`).
- Coverage flags: 2, both "unpriced text rule". Copycat (its text reads the opponent's hand) and Team Rocket's Thieving Machine (its text reads the opponent's discard pile; flagged by the tool's own rule, reported as the tool gave it). No card is flagged for printed-damage estimation, for paying off on the opponent's turn, for an engine limitation, or as not implemented. All 12 report "Fully implemented".
- Census card in this list: Protective Poncho B2 147 (1 copy). It is a group-4 card in `cards.md` (kt switch 2, priced at 0 in the proposed registration), not a switch-1 card (groups 1 to 3). The goldfish tool does not flag it.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Swablu (B1 196) | Type / stage | Colorless, Basic (Stage 0) | Colorless, Basic | match |
|   |  | HP / weakness / retreat | 50 / Lightning / 1 | 50 / Lightning / 1 | match |
|   |  | Attack: Sing | [C] 0. "Your opponent's Active Pokémon is now Asleep." | [C] no damage. "Your opponent's Active Pokémon is now Asleep." | match |
|   |  | Ability | none | none | match |
| 2 | Mega Altaria ex (B1 102) | Type / stage | Psychic, Stage 1 from Swablu | Psychic, Stage 1, evolves from Swablu | match |
|   |  | HP / weakness / retreat | 190 / Metal / 1 | 190 / Metal / 1 | match |
|   |  | Attack: Mega Harmony | [PP] 40. "This attack does 30 more damage for each of your Benched Pokémon." | [PP] 40+. "This attack does 30 more damage for each of your Benched Pokémon." | match (40+ against 40 is notation only) |
|   |  | Ability | none | none (rule box only: Mega Evolution ex, 3 points when Knocked Out) | match; rule handled by engine code, see summary |
| 3 | Darkrai (B2b 040) | Type / stage | Darkness, Basic (Stage 0) | Darkness, Basic | match |
|   |  | HP / weakness / retreat | 100 / Grass / 2 | 100 / Grass / 2 | match |
|   |  | Ability: Bad Dreams | "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon." | "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon." | match |
|   |  | Attack: Dark Slumber | [CCC] 40. "Your opponent's Active Pokémon is now Asleep." | [CCC] 40. "Your opponent's Active Pokémon is now Asleep." | match |
| 4 | Igglybuff (A4a 059) | Type / stage | Colorless, Basic (Stage 0) | Colorless, Basic | match |
|   |  | HP / weakness / retreat | 30 / none / 0 | 30 / None / 0 | match |
|   |  | Attack: Sleepy Lullaby | [no Energy] 10. "Your opponent's Active Pokémon is now Asleep." | [0 Energy] 10. "Your opponent's Active Pokémon is now Asleep." | match |
|   |  | Ability | none | none | match |
| 5 | Professor's Research (P-A 007) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 6 | Leaf (A1a 068) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "During this turn, the Retreat Cost of your Active Pokémon is 2 less." | "During this turn, the Retreat Cost of your Active Pokémon is 2 less." | match |
| 7 | Copycat (B1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 8 | Cyrus (A2 150) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 9 | Sabrina (A1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | match |
| 10 | Poké Ball (P-A 005) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning) |
| 11 | Team Rocket's Thieving Machine (B4a 067) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Item card, except any Team Rocket's Thieving Machine, from your opponent's discard pile into your hand." | "Put a random Item card, except any Team Rocket's Thieving Machine, from your opponent's discard pile into your hand." | match |
| 12 | Protective Poncho (B2 147) | Trainer type | Tool | Trainer - Tool | match |
|   |  | Text | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Swablu (B1 196) | Fully implemented | none | - | - | - |
| Mega Altaria ex (B1 102) | Fully implemented | none | - | - | - |
| Darkrai (B2b 040) | Fully implemented | none | - | - | - (not flagged by the tool; its Bad Dreams text says "at the end of each turn", which includes the opponent's, so read the deck's sleep numbers with that in mind) |
| Igglybuff (A4a 059) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Leaf (A1a 068) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Sabrina (A1 225) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Team Rocket's Thieving Machine (B4a 067) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's discard pile) | - | - |
| Protective Poncho (B2 147) | Fully implemented | none | - | - | - (not flagged by the tool; kt's proposed registration prices it at 0, `cards.md` group 4) |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Only the first class fired, on Copycat and Team Rocket's Thieving Machine. Copycat sits in all eight panel lists too (B2e README section 6), so it is on both sides of every pairing. Untrusted-prone by B2e's column: no card the tool flags is the main attacker, the main ability or the deck's tempo card (Mega Harmony and Bad Dreams carry no flag); the deck's flagged cards are its two draw/recovery Items and Supporters.

## Unverified

None. All 12 cards were read from both sources.
