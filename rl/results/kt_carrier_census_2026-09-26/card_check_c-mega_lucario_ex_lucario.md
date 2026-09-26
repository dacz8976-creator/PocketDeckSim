# Card-text check: c-mega_lucario_ex_lucario.txt (kt carrier census list)

Date: 2026-09-26. Deck file: `rl/results/kt_carrier_census_2026-09-26/decks/c-mega_lucario_ex_lucario.txt` (Limitless archetype "Mega Lucario ex Lucario"; pikamon, 1st of 112, The Breakfast Club Daily #5, 2026-09-10; provenance in `provenance/c-mega_lucario_ex_lucario.json`).

How it was checked, the way B2e did it (`rl/results/b2e_card_check_2026-09-26/card_check_arch_manectric.md`): for each of the 16 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` (database `lib/deckgym-database.json`; the raw entry read for the Trainer subtype, `trainer_card_type`), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` read on the same day. Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and glyph differences (Pokémon/Pokemon, "-30"/"−30") are ignored.

Fetch note: the WebFetch tool refused every page ("session limit"), so the pages were loaded in the Browser pane (`pocket.limitlesstcg.com`, the same URLs, main-element text) instead. Every card was read from both sources; none is unverified.

Coverage flags came from `rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel decks/screen/opponents --coverage rl/results/kt_carrier_census_2026-09-26/coverage_c-mega_lucario_ex_lucario.json` run in WSL (0 games played; goldfish sha256 318c82c8…be997, the hash in `rl/engine-2026-09-25/README.md`). The raw output is in `coverage_c-mega_lucario_ex_lucario.json` next to this file.

## Summary

- Cards checked: 16 of 16 (all verified against Limitless).
- Mismatches: 1, low severity (Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning; the same item B2e refuted, README section 6).
- High-severity mismatches: none. Every HP, type, stage, weakness, retreat cost, attack cost, damage figure, effect, ability and Trainer subtype matches.
- Coverage flags: 3 cards. Copycat is flagged "unpriced text rule" (reads the opponent's hand). Bonsly's Teary Attack is flagged "pays off on the opponent's turn" (its -30 lasts through the opponent's next turn). Riolu's Fighting Fist is flagged "printed-damage estimator" (the +30 against a Pokémon ex is priced at the printed 10). No card is flagged for an engine limitation or as not implemented; all 16 report "Fully implemented".
- Note on Mega Lucario ex: Limitless prints the Mega Evolution ex rule box (3 points when Knocked Out). The database entry has no field for it, but the engine applies it in code for any Pokémon whose name starts with "Mega " (`engine/src/models/card.rs`, `is_mega`; B2e README section 6). Not counted as a mismatch.
- Damage notation: Limitless prints "10+" for Riolu and "90+" for Mega Lucario ex where the engine stores the integer and the "more damage" sentence; the same convention B2e accepted for Rattata. Formatting only.
- Untrusted-prone? The main attacker (Mega Lucario ex, Fighting Pulse) and the main ability (Lucario, Fighting Coach) carry no flag. The flags sit on the opening attacker (Riolu's ex bonus), the defensive tempo card (Bonsly's Teary Attack) and Copycat, which is on both sides of every panel pairing. The panel's own `t-lucario.txt` runs the same three cards, so none of this is new to the table.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Riolu (B3 079) | Type / stage | Fighting, Basic (Stage 0) | Fighting, Basic | match |
|   |  | HP / weakness / retreat | 60 / Psychic / 1 | 60 / Psychic / 1 | match |
|   |  | Attack: Fighting Fist | [F] 10. "If your opponent's Active Pokémon is a Pokémon ex, this attack does 30 more damage." | [F] 10+. "If your opponent's Active Pokémon is a Pokémon ex, this attack does 30 more damage." | match |
|   |  | Ability | none | none | match |
| 2 | Mega Lucario ex (B3 081) | Type / stage | Fighting, Stage 1 from Riolu | Fighting, Stage 1, evolves from Riolu | match |
|   |  | HP / weakness / retreat | 190 / Psychic / 1 | 190 / Psychic / 1 | match |
|   |  | Attack: Fighting Pulse | [FF] 90. "If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage." | [FF] 90+. "If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage." | match |
|   |  | Ability | none | none (rule box only: Mega Evolution ex, 3 points when Knocked Out) | match; rule handled by engine code, see note |
| 3 | Lucario (A2 092) | Type / stage | Fighting, Stage 1 from Riolu | Fighting, Stage 1, evolves from Riolu | match |
|   |  | HP / weakness / retreat | 100 / Psychic / 2 | 100 / Psychic / 2 | match |
|   |  | Ability: Fighting Coach | "Attacks used by your [F] Pokémon do +20 damage to your opponent's Active Pokémon." | "Attacks used by your [F] Pokémon do +20 damage to your opponent's Active Pokémon." | match |
|   |  | Attack: Submarine Blow | [FF] 40, no effect | [FF] 40, no effect | match |
| 4 | Bonsly (B3 078) | Type / stage | Fighting, Basic (Stage 0) | Fighting, Basic | match |
|   |  | HP / weakness / retreat | 30 / none / 0 | 30 / none / 0 | match |
|   |  | Attack: Teary Attack | [no Energy] 10. "During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage." | [0] 10. "During your opponent's next turn, attacks used by the Defending Pokémon do −30 damage." | match |
|   |  | Ability | none | none | match |
| 5 | Hitmonlee (A1 154) | Type / stage | Fighting, Basic (Stage 0) | Fighting, Basic | match |
|   |  | HP / weakness / retreat | 80 / Psychic / 1 | 80 / Psychic / 1 | match |
|   |  | Attack: Stretch Kick | [F] no printed damage. "This attack does 30 damage to 1 of your opponent's Benched Pokémon." | [F] no printed damage. "This attack does 30 damage to 1 of your opponent's Benched Pokémon." | match |
|   |  | Ability | none | none | match |
| 6 | Professor's Research (P-A 007) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 7 | Copycat (B1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 8 | Korrina (B3 149) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "During this turn, attacks used by your [F] Pokémon do +30 damage to your opponent's Active Pokémon ex." | "During this turn, attacks used by your [F] Pokémon do +30 damage to your opponent's Active Pokémon ex." | match |
| 9 | Pokémon Center Lady (A2b 070) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | match |
| 10 | Cyrus (A2 150) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 11 | Poké Ball (P-A 005) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning; B2e refuted the same item) |
| 12 | Lucky Ice Pop (B2 145) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | match |
| 13 | Field Blower (B3 147) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | match |
| 14 | X Speed (P-A 002) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "During this turn, the Retreat Cost of your Active Pokémon is 1 less." | "During this turn, the Retreat Cost of your Active Pokémon is 1 less." | match |
| 15 | Protective Poncho (B2 147) | Trainer type | Tool | Trainer - Tool | match |
|   |  | Text | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | match |
| 16 | Arena of Antiquity (B3 154) | Trainer type | Stadium | Trainer - Stadium | match |
|   |  | Text | "Attacks used by each [F] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex." | "Attacks used by each [F] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Riolu (B3 079) | Fully implemented | none | - | FLAGGED ("Fighting Fist: ExtraDamageIfEx estimated at printed damage") | - |
| Mega Lucario ex (B3 081) | Fully implemented | none | - | - | - |
| Lucario (A2 092) | Fully implemented | none | - | - | - |
| Bonsly (B3 078) | Fully implemented | none | - | - | FLAGGED ("attack Teary Attack") |
| Hitmonlee (A1 154) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Korrina (B3 149) | Fully implemented | none | - | - | - |
| Pokémon Center Lady (A2b 070) | Fully implemented | none | - | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Lucky Ice Pop (B2 145) | Fully implemented | none | - | - | - |
| Field Blower (B3 147) | Fully implemented | none | - | - | - |
| X Speed (P-A 002) | Fully implemented | none | - | - | - |
| Protective Poncho (B2 147) | Fully implemented | none | - | - | - |
| Arena of Antiquity (B3 154) | Fully implemented | none | - | - | - |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Three flags fired: Copycat (unpriced), Riolu (estimator), Bonsly (opponent's turn).

Census note: the only census card in this list is Protective Poncho (group 4 in `cards.md`; the kt draft prices it at 0 on both sides). Bonsly's Teary Attack is a damage cut stored on the opponent's attacker, the "Growl-type" family that `cards.md` group 4 lists as considered and left out of switch 1; it is not a census card and is noted here only because it is the list's one temporary damage-cut effect.

## Unverified

None. All 16 cards were read from both sources.
