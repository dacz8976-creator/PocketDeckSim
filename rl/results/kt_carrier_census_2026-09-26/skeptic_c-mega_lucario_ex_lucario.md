# Skeptic pass: c-mega_lucario_ex_lucario.txt (kt carrier census, Lists phase)

Date: 2026-09-26. Read-only pass over `decks/c-mega_lucario_ex_lucario.txt`, `provenance/c-mega_lucario_ex_lucario.json`, `card_check_c-mega_lucario_ex_lucario.md`, `cells_c-mega_lucario_ex_lucario.{py,md,csv,json}`, `coverage_c-mega_lucario_ex_lucario.json`, `carrier_entries.csv` and `census_summary.json`. Everything below was re-derived with my own scripts (scratch: `kt_census/skeptic_lucario.py`, `skeptic_lucario_alts.py`), not by re-running the author's. Holdout discipline kept: `split.json` lists 63 holdout event ids; every standings file I opened was asserted to be in `development_event_ids` first (63 files, none holdout). `matches.csv` holdout rows entered only the pooled cell, as B2e section 3 did. No engine game was played; nothing outside this folder and the scratch folder was written.

**Verdict: the pick, the deck file, the card check, the cells and the census-card claim all hold. One provenance sentence about an alternative list is wrong and should be corrected (section 5). Nothing else needs to change.**

## 1. (a) Is pikamon's list really the best-placing carrier entry in the development half?

Yes, two ways.

From `carrier_entries.csv`: 222 rows for "Mega Lucario ex Lucario", all in development events (0 rows from a holdout id). Ordered by placing, then larger event, then date, the top of the list is:

| placing | event size | date | player | event | carries |
|---:|---:|---|---|---|---|
| 1 | 112 | 2026-09-10 | pikamon | The Breakfast Club Daily #5-$5 + FA | Protective Poncho x1 (B2 147) |
| 1 | 46 | 2026-09-01 | frozen | Dark League Pop Up | Protective Poncho x1 |
| 1 | 8 | 2026-09-05 | drakioxp | notChaser CUP#2 Equipe Rocket! | Protective Poncho x1 |
| 2 | 113 | 2026-09-01 | aldous | Plasma Daily #22 | Protective Poncho x1 |
| 2 | 57 | 2026-08-30 | lazimus | Dark League Pop Up | Protective Poncho x1 |
| 2 | 48 | 2026-09-03 | thomasxavier21 | Block Dragon Pop Up (RR Vespiquen) | Protective Poncho x1 |

Three carriers placed 1st, exactly as the provenance says; pikamon's is the largest event, so the B2e rule (best placing, then larger event) picks it. No carrier entry carries a switch-1 card (`carries_switch1_card` is False on all 222). The largest event in the window with a carrier is PMPT #44 (378 players), where the archetype's best carrier placed 3rd (esteban0708, 11-2-0), as the provenance notes.

Independently from the standings: scanning all 63 development standings files for entries whose `deck.name` is exactly "Mega Lucario ex Lucario" gives 398 entries in 58 events, every one with a 20-card decklist (deck ids: `mega-lucario-ex-b3-lucario-a2` 396, `mega-lucario-ex-lucario-b3` 2). Matching each decklist line's SET + zero-padded NUMBER against the 76 ids of the 46 census cards in `census_summary.json`: 222 carriers (Protective Poncho 211 lists, Rocky Helmet 18, both 7), 0 switch-1 carriers, 0 same-name-other-printing hits. The set of (event, player) carrier pairs is identical to `carrier_entries.csv` (nothing missing either way). Sorting the carriers the same way puts pikamon first. For completeness, the only 1st-place entry of the archetype that is NOT a carrier is lickthatazz, 1st of 81 (FAREWELL B4!, 2026-08-26); it carries no census card, so the rule rightly passes over it.

Provenance of the pick (from `6aa22425a4272c53be64ca36_details.json.gz` and `_standings.json.gz`, development split): The Breakfast Club Daily #5-$5 + FA, 112 players, start 2026-09-10T20:20Z, player pikamon (display name Pikamon), placing 1, record 10-2-0, deck id mega-lucario-ex-b3-lucario-a2, https://play.limitlesstcg.com/tournament/6aa22425a4272c53be64ca36/player/pikamon/decklist. All match the provenance file.

## 2. (b) Does the file match the source decklist card for card and printing for printing?

Yes. The source entry has 16 decklist lines (pokemon + trainer sections; there is no energy section in the API entry, so "Energy: Fighting" is the author's line, justified below) summing to 20 cards. Comparing by (set, zero-padded number) with name and count on each side: zero differences, and the file's 16 lines are in the same order as the source. File bytes: 359, no BOM, 0 CR, 17 LF, ends with LF; first line `Energy: Fighting`; 16 card lines summing to 20. `python lib/deck_check.py files "rl/results/kt_carrier_census_2026-09-26/decks/c-mega_lucario_ex_lucario.txt"` prints "decks clean", exit 0 (re-run by me).

Energy line: `python lib/card.py` reports Riolu B3 079, Mega Lucario ex B3 081, Lucario A2 092, Bonsly B3 078 and Hitmonlee A1 154 all as Fighting (the raw database `energy_type` field agrees for all five), so "Energy: Fighting" is the only sensible line and matches `decks/screen/opponents/t-lucario.txt`.

Diff against the panel's `t-lucario.txt`, re-derived: the panel file's 15 lines are all in the census file with the same printings; the census file has 1 Copycat where the panel has 2 and adds 1 Lucky Ice Pop B2 145. That is the provenance's "-1 Copycat, +1 Lucky Ice Pop".

## 3. (c) Card-text comparisons and one Limitless cell, re-derived

Card texts (engine from `python lib/card.py "<SET> <NUM>"` run from the repo root; Limitless read from `pocket.limitlesstcg.com/cards/<SET>/<NUM>` in the Browser pane on 2026-09-26, since WebFetch is at its session limit):

- **Korrina (B3 149).** Engine: Trainer (raw database `trainer_card_type`: Supporter); "During this turn, attacks used by your [F] Pokémon do +30 damage to your opponent's Active Pokémon ex." Limitless: "Trainer - Supporter"; the same sentence word for word. Match, as reported.
- **Bonsly (B3 078).** Engine: Fighting, Stage 0, HP 30, weakness none ("weak -"), retreat 0; [no Energy] Teary Attack 10, "During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage." Limitless: Fighting, 30 HP, Basic, "0 Teary Attack 10", "During your opponent's next turn, attacks used by the Defending Pokémon do −30 damage.", Weakness none, Retreat 0. Match apart from the minus glyph, as reported.
- Extra, because it is the one census card in the list: **Protective Poncho (B2 147).** Engine: Trainer, "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." Limitless: "Trainer - Tool", the same sentence. Match.

Limitless cell, counted with my own code from `matches.csv` (30,216 rows) under the scoreboard's rules (held side by exact deck_name, panel side by archetype label, tie = half a point in n, double loss excluded and counted as DL, byes never pair, mirrors excluded, one unit per record):

| cell | W-L-T | DL | n | score | band | reported |
|---|---|---:|---:|---:|---:|---|
| altaria, development | 43-114-5 | 11 | 162 | 28.1 | 6.9 | 43-114-5, 162, 28.1, 6.9 |
| altaria, pooled | 90-234-11 | 20 | 335 | 28.5 | 4.8 | 90-234-11, 335, 28.5, 4.8 |
| vespiquen, development (second check) | 73-31-3 | 6 | 107 | 69.6 | 8.7 | 73-31-3, 107, 69.6, 8.7 |
| vespiquen, pooled | 141-58-7 | 9 | 206 | 70.1 | 6.2 | 141-58-7, 206, 70.1, 6.2 |

All identical to `cells_c-mega_lucario_ex_lucario.csv`. The altaria label maps to one deck_name only ("Mega Altaria ex Espeon", 4,445 sides). Mirror records set aside: 96 development, 212 pooled, as the cells file says. Development decisive-or-tie records with the archetype on a side: 2,044, the figure `census_summary.json` uses for the window rank-1 cross-check. The lucario cell is a mirror by construction (the archetype is the panel's own lucario deck_name), so its emptiness is right, and the equal-weight average over seven opponents is the correct reading of the rule.

Coverage: the goldfish binary's sha256 is 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997 (Get-FileHash), the value in `rl/engine-2026-09-25/README.md`. `coverage_c-mega_lucario_ex_lucario.json` has 16 entries, all "Fully implemented" with no limitations; the three flags (Copycat unpriced text rule, Bonsly pays off on the opponent's turn, Riolu printed-damage estimator) are the three the card check reports. I did not re-run goldfish.

## 4. (d) Does the list carry the census cards it claims?

Yes. Against the 46-card set in `census_summary.json` (76 printing ids), the file carries exactly one census printing: Protective Poncho B2 147 x1 (kind "other", not switch-1 relevant; `cards.md` group 4, priced at 0 by the kt draft). No Rocky Helmet, no group 1 to 3 card, and no card whose name is a census card's under another printing. So the provenance's "Protective Poncho x1; no Rocky Helmet and no group 1 to 3 card" is right, and this list cannot open the reserve route for switch 1 on its own; it is a group-4 carrier only.

Archetype status re-checked: `decks/classifier/limitless_2026-09-10.json` lists "Mega Lucario ex Lucario" at rank 1 with 485 players; no file in `decks/dustin/` or `decks/brews/` contains a Lucario or Riolu line (grep for "Lucario|Riolu": no match), so it is not Dustin's under any of the census's three levels. It is the panel's own lucario deck, which the provenance says plainly.

## 5. The one thing to fix

`provenance/c-mega_lucario_ex_lucario.json`, `alternatives_considered[1]` (drakioxp, 1st of 8, event 6a9c4f47a4272c53be647ff7, development): `differs_from_pick` ends with "no Pokémon Center Lady." That is wrong. drakioxp's source list (read from the standings file) is 2 Riolu B3 079, 2 Mega Lucario ex B3 081, 1 Lucario A2 092, 2 Hitmontop A4 102, 2 Professor's Research P-A 007, 2 Copycat B1 225, 1 Korrina B3 149, 1 Cyrus A2 150, **1 Pokémon Center Lady A2b 070**, 2 Poké Ball P-A 005, 1 X Speed P-A 002, 1 Field Blower B3 147, 1 Protective Poncho B2 147, 1 Arena of Antiquity B3 154 (20 cards). Its full diff against the pick is: 2 Hitmontop A4 102 in place of Bonsly and Hitmonlee; 2 Copycat and no Lucky Ice Pop. The "no Pokémon Center Lady" clause belongs to aldous only (whose entry already says it, correctly).

The other three alternative diffs were re-derived and are correct as written: frozen (Riolu A2 091 for B3 079; 2 Copycat; no Lucky Ice Pop), aldous (Riolu A2 091; Hitmontop A4 102 for Hitmonlee; 2 Copycat; Small Balloon B3b 064 for X Speed; no Pokémon Center Lady), lazimus (2 Hitmontop A4 102 for Bonsly and Hitmonlee; Sabrina A1 225 for Lucky Ice Pop). This error does not touch the pick, the deck file, the cells, the card check or the census-card claim; it is a wrong sentence about a list that was not chosen.

## 6. Notes that need no change

- Limitless lists a second version of Korrina (B3 #190) and of Bonsly (B3 #168). The source names #149 and #78, the file copies them, and `card.py "<SET> <NUM>"` resolves each id to one printing, so nothing turns on this.
- Because this archetype is the panel's own lucario deck, any later use of it under clause (d) will have no lucario cell to read (mirror) and its seven-cell average is the comparable number. That is a reading note for whoever applies the clause, not a defect in this census file.
