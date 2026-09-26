# Card-text check: c-jumpluff_ex_team_rocket_s_electrode.txt (carrier list, Jumpluff ex Team Rocket's Electrode)

Date: 2026-09-26. Deck file: `rl/results/kt_carrier_census_2026-09-26/decks/c-jumpluff_ex_team_rocket_s_electrode.txt` (Limitless archetype "Jumpluff ex Team Rocket's Electrode", deck id `jumpluff-ex-a4a-team-rockets-electrode-b4a`; provenance in `provenance/c-jumpluff_ex_team_rocket_s_electrode.json`). This file reports; it decides nothing.

How it was checked, the way B2e did it (`rl/results/b2e_card_check_2026-09-26/card_check_arch_manectric.md`): for each of the 12 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` run from the repo root (database `lib/deckgym-database.json`; the raw entry was read as well, for the Trainer subtype `trainer_card_type` and the attack's `fixed_damage`), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` on the same day. Every page was read twice: once through the WebFetch summarizer and once as the page's own raw text in the browser pane (the summarizer had shortened Jumpluff ex's attack name to "Breeze-By"; the page prints "Breeze-By Attack", which is what the engine has, so the raw text is what the table quotes). Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and accent differences (Pokémon/Pokemon) are ignored.

Coverage flags came from `rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel decks/screen/opponents --coverage rl/results/kt_carrier_census_2026-09-26/coverage_c-jumpluff_ex_team_rocket_s_electrode.json` run in WSL (0 games played; goldfish sha256 318c82c8...be997; exit 0). The raw output is in `coverage_c-jumpluff_ex_team_rocket_s_electrode.json` next to this file.

Deck check: `python lib/deck_check.py files rl/results/kt_carrier_census_2026-09-26/decks/c-jumpluff_ex_team_rocket_s_electrode.txt` printed "decks clean", exit 0, no WARN lines. The file is UTF-8 without BOM, LF line endings, 12 card lines, 20 cards, Energy: Lightning.

## Summary

- Cards checked: 12 of 12 (all verified against Limitless; none unverified, no fetch was refused).
- Mismatches: 1, low severity (Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning; the same one B2e refuted on the same printing).
- High-severity mismatches: none. Every HP, type, stage, evolves-from, weakness, retreat cost, attack cost, damage figure, effect, ability name and ability text matches.
- Coverage flags: 3. Copycat is flagged "unpriced text rule" (reads the opponent's hand). Rocky Helmet ("its effect") and Team Rocket's Electrode ("ability Destiny Burst") are flagged "pays off on the opponent's turn". All 12 report "Fully implemented" with no engine limitation; nothing is not implemented.
- Note on Jumpluff ex: Limitless prints the ex rule box ("When your Pokémon ex is Knocked Out, your opponent gets 2 points"). The database entry has no field for it; the engine's rules code treats any Pokémon whose name ends in "ex" as an ex (`engine/src/models/card.rs`, `is_ex`, line 186), so the rule is honored. Not counted as a mismatch (the same reading B2e gave the Mega box via `is_mega`).
- Note on Random Spark: the card prints no damage figure; its 30 is in the effect text. The engine stores `fixed_damage` 0 with the same effect sentence. Match.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Hoppip (A4a 001) | Type / stage | Grass, Basic (Stage 0) | Grass, Basic | match |
|   |  | HP / weakness / retreat | 50 / Lightning / 1 | 50 / Lightning / 1 | match |
|   |  | Attack: Splash | [C] 10, no effect | [C] Splash 10, no effect | match |
|   |  | Ability | none | none | match |
| 2 | Jumpluff ex (A4a 003) | Type / stage | Grass, Stage 2 from Skiploom | Grass, Stage 2, evolves from Skiploom | match |
|   |  | HP / weakness / retreat | 160 / Lightning / 1 | 160 / Lightning / 1 | match |
|   |  | Attack: Breeze-By Attack | [C] 70. "You may switch this Pokémon with 1 of your Benched Pokémon." | [C] Breeze-By Attack 70. "You may switch this Pokémon with 1 of your Benched Pokémon." | match |
|   |  | Ability / rule box | none | none; ex rule box (2 points when Knocked Out) | match; rule handled by engine code, see note |
| 3 | Team Rocket's Voltorb (B4a 019) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 60 / Fighting / 1 | 60 / Fighting / 1 | match |
|   |  | Attack: Rolling Attack | [L] 20, no effect | [L] Rolling Attack 20, no effect | match |
|   |  | Ability | none | none | match |
| 4 | Team Rocket's Electrode (B4a 020) | Type / stage | Lightning, Stage 1 from Team Rocket's Voltorb | Lightning, Stage 1, evolves from Team Rocket's Voltorb | match |
|   |  | HP / weakness / retreat | 70 / Fighting / 1 | 70 / Fighting / 1 | match |
|   |  | Ability: Destiny Burst | "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 70 damage to the Attacking Pokémon." | "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 70 damage to the Attacking Pokémon." | match |
|   |  | Attack: Random Spark | [L] printed 0. "This attack does 30 damage to 1 of your opponent's Pokémon." | [L] Random Spark, no printed damage. "This attack does 30 damage to 1 of your opponent's Pokémon." | match, see note |
| 5 | Oricorio (A3 066) | Type / stage | Lightning, Basic (Stage 0) | Lightning, Basic | match |
|   |  | HP / weakness / retreat | 70 / Fighting / 1 | 70 / Fighting / 1 | match |
|   |  | Ability: Safeguard | "Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex." | "Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex." | match |
|   |  | Attack: Zzzap | [LC] 50, no effect | [LC] Zzzap 50, no effect | match |
| 6 | Professor's Research (P-A 007) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 7 | Cyrus (A2 150) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 8 | Copycat (B1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 9 | Rare Candy (A3 144) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn." | same sentence, word for word | match |
| 10 | Poké Ball (P-A 005) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning) |
| 11 | Rocky Helmet (A2 148) | Trainer type | Tool | Trainer - Tool | match |
|   |  | Text | "If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon." | "If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon." | match |
| 12 | Hiking Trail (B2b 069) | Trainer type | Stadium | Trainer - Stadium | match |
|   |  | Text | "At the end of each player's turn, that player draws cards until they have 3 cards in their hand." | "At the end of each player's turn, that player draws cards until they have 3 cards in their hand." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Hoppip (A4a 001) | Fully implemented | none | - | - | - |
| Jumpluff ex (A4a 003) | Fully implemented | none | - | - | - |
| Team Rocket's Voltorb (B4a 019) | Fully implemented | none | - | - | - |
| Team Rocket's Electrode (B4a 020) | Fully implemented | none | - | - | FLAGGED ("ability Destiny Burst": 70 back to the attacker when it is Knocked Out) |
| Oricorio (A3 066) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Rare Candy (A3 144) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Rocky Helmet (A2 148) | Fully implemented | none | - | - | FLAGGED ("its effect": 20 back to the attacker) |
| Hiking Trail (B2b 069) | Fully implemented | none | - | - | - |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Two classes fired: unpriced text rule on Copycat, and pays off on the opponent's turn on Rocky Helmet and Team Rocket's Electrode.

Untrusted-prone, in B2e's sense: yes. The deck's whole counter plan (Electrode's Destiny Burst, and the two Rocky Helmet that are the census card) pays off on the opponent's turn, so its simulator numbers should be read with that flag beside them. That is also exactly the input the kt candidate's switch 3 prices (counter damage: `rl/results/kt_carrier_census_2026-09-26/cards.md`, group 4, Rocky Helmet), which is why this archetype is in the carrier census at all; it carries no switch-1 (damage-cut) card. Copycat is in this list and in all eight panel lists, so it sits on both sides of every pairing.

## Unverified

None. All 12 cards were read from both sources (card.py plus raw database entry; Limitless page via WebFetch and as raw page text).
