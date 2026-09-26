# Skeptic pass: c-jumpluff_ex_team_rocket_s_electrode.txt (Jumpluff ex Team Rocket's Electrode carrier list)

Date: 2026-09-26. Read-only pass over `decks/c-jumpluff_ex_team_rocket_s_electrode.txt` and its companions (`provenance/…json`, `card_check_…md`, `cells_…{py,md,csv}`, `coverage_…json`). Everything below was re-derived with my own scripts (scratchpad `kt_census/skeptic_jumpluff_lists.py`, `skeptic_jumpluff_cell.py`, `skeptic_jumpluff_extra.py`), written from the data description and the scoreboard's rules paragraph, not by re-running the other agent's scripts. Card text came only from `python lib/card.py "<SET> <NUM>"` (engine side) and the Limitless card page read as raw page text in the browser pane (Limitless side). No engine game was run; no holdout standings file was opened (the 63 holdout ids were loaded from `split.json` and asserted against every file opened; holdout rows of `matches.csv` were used only inside the pooled cells). Nothing in the repo was changed except this file.

**Verdict: nothing needs to change.** All four claims hold; details and numbers follow.

## (a) Is ravenoussix's list really the best-placing carrier entry in the development half?

Yes. My scan opened all 63 development standings files and found 18 entries whose `deck.name` is exactly "Jumpluff ex Team Rocket's Electrode" (all with a decklist, all 20 cards, all deck id `jumpluff-ex-a4a-team-rockets-electrode-b4a`). Checking every card of every list against all 82 printing ids in `cards.json`:

- 17 entries carry exactly `2 Rocky Helmet A2 148` and nothing else from the census set (no switch-1 card anywhere); 1 entry (tababahani, 29th of 113 at the same event, 4-3-0) carries nothing from the set.
- Ordered by placing, the carriers run 7, 9, 11, 11, 13, 17, 20, 31, 38, 43, 44, 47, 54, 90, then three unplaced. The 7th is ravenoussix (INLG | RavenousSix, US) at Plasma Daily #22| Team Rocket's Ambitions| FA Card, event id `6a96069dabb9482237504f7f` (development half), 113 players, 2026-09-01T17:00Z, record 6-2-1. No other carrier shares placing 7, so the B2e tiebreak (larger event) was never needed.
- Every row of the provenance's `alternatives_considered` (player, event id, size, date, placing, record) matches my scan line for line, including the three unplaced entries and the ineligible tababahani entry.
- tababahani's 29th-place list, checked directly: 2 Hoppip, 2 Jumpluff ex, 2 TR Voltorb, 2 TR Electrode, 2 Oricorio, 2 Professor's Research, 1 Copycat, 1 Cyrus, 1 Mars A2 155, 2 Rare Candy, 2 Poké Ball, 1 Red Card P-A 006. So "Mars and Red Card in place of Rocky Helmet" is right (it also runs a second Oricorio in place of Hiking Trail, which the provenance does not mention and does not need to: it is not a carrier either way).
- `carrier_entries.csv` rows 264 to 280 for this archetype agree with the scan (17 rows, same order).

## (b) Does the file match the source decklist card for card, printing for printing?

Yes. The raw standings entry for `ravenoussix` at `6a96069dabb9482237504f7f` holds 12 card lines (5 Pokémon, 7 Trainer) plus `energy: ["Lightning"]`. Compared by (name, SET NUM) with numbers zero-padded to three digits: 12 of 12 lines agree in name, set, number and count; 0 differences; 20 cards on both sides. Bytes: 290, no BOM, no CR, ends with LF, first line `Energy: Lightning`. `python lib/deck_check.py files rl/results/kt_carrier_census_2026-09-26/decks/c-jumpluff_ex_team_rocket_s_electrode.txt` printed "decks clean", exit 0. The provenance's player, country, event name, size, date, placing, record and URL (`https://play.limitlesstcg.com/tournament/6a96069dabb9482237504f7f/player/ravenoussix/decklist`) all match the details and standings files.

## (c) Card-text comparisons and a Limitless cell, re-derived

Card text (engine from `card.py`, Limitless from the raw card page):

- **Rocky Helmet A2 148** (the census card). Engine: Trainer, `trainer_card_type` Tool, "If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon." Limitless (`/cards/A2/148`): "Trainer - Tool", the same sentence word for word. Match, as reported. (Limitless lists versions A2 148, A4b 322, A4b 323, which is the same id set `cards.json` gives Rocky Helmet.)
- **Team Rocket's Electrode B4a 020**. Engine: Lightning, Stage 1 from Team Rocket's Voltorb, HP 70, weak Fighting, retreat 1; Ability Destiny Burst "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 70 damage to the Attacking Pokémon."; attack [L] Random Spark, `fixed_damage` 0, "This attack does 30 damage to 1 of your opponent's Pokémon." Limitless (`/cards/B4a/20`): "Lightning - 70 HP", "Stage 1 - Evolves from Team Rocket's Voltorb", the same Ability text, "L Random Spark" with no printed damage figure and the same effect sentence, "Weakness: Fighting", "Retreat: 1". Match on every field, and the card check's note that the 30 lives in the effect text, not a damage figure, is right.
- **Poké Ball P-A 005** (the one reported mismatch, checked as well). Engine: Item, "Put a random Basic Pokémon from your deck into your hand." Limitless (`/cards/P-A/5`): "Trainer - Item", "Put 1 random Basic Pokemon from your deck into your hand." Article against numeral and a dropped accent; same meaning; low severity, exactly as reported and as B2e refuted it.

Limitless cells, recomputed from `matches.csv` with the scoreboard's rules (held side exact deck_name, panel side archetype label, tie = half point in n, double loss excluded and counted as DL, byes never pair, mirrors excluded, one unit per record, band 1.96 sqrt(p(1-p)/n)). I recomputed three cells rather than one:

| Opponent | Dev W-L-T (DL) | n | Dev % | +/- | Pooled W-L-T (DL) | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 5-5-1 (1) | 11 | 50.0 | 29.5 | 7-10-1 (3) | 18 | 41.7 | 22.8 |
| vespiquen | 9-0-0 | 9 | 100.0 | 0.0 | 12-1-0 | 13 | 92.3 | 14.5 |
| weezing | 0-4-1 | 5 | 10.0 | 26.3 | 0-9-1 | 10 | 5.0 | 13.5 |

All three agree with `cells_c-jumpluff_ex_team_rocket_s_electrode.md` to the digit. The label-to-deck-name maps (lucario = Mega Lucario ex Lucario, vespiquen = Vespiquen ex Shuckle ex, weezing = Team Rocket's Weezing ex Hoopa ex) were read off the data, one name per label. The totals table also reproduces: held-deck records development 105 (96 decisive, 5 tie, 3 double loss, 1 bye; scored 101), pooled 220 (197 decisive, 7 tie, 10 double loss, 6 bye; scored 204), all under one deck id with no archetype label; `matches.csv` 30,216 rows, 14,127 development, 16,089 holdout, and every row's `split` column agrees with `split.json`. I also checked the equal-weight averages by hand from the eight cell scores (development 45.7 over 7 opponents, band 12.1; pooled 39.3 over 8, band 9.3) and the match-weighted figures (48.9 on 47; 42.6 on 94): they agree.

## (d) Does the list carry the census cards it claims?

Yes, and only those. The file holds `2 Rocky Helmet A2 148`; `A2 148` is one of Rocky Helmet's ids in `cards.json` (group 4, priced by kt switch 3 as counter damage, not a switch-1 damage cut). None of the other 11 printings in the list is among the 82 census ids, so the list carries no switch-1 card, exactly as the provenance says (`census_cards_carried`: Rocky Helmet x2 only). The coverage flags in `coverage_…json` (Copycat: unpriced text rule; Rocky Helmet and Team Rocket's Electrode: pays off on the opponent's turn; all 12 "Fully implemented", no limitations) match the card check's table.

## Side check on the "not Dustin's" flag

`census.csv` marks this archetype dustin=False, level "none". A grep of `decks/dustin/*.txt` and `decks/brews/*.txt` for Jumpluff, Hoppip, Skiploom, Electrode and Voltorb finds nothing, so the flag holds even under the conservative rule. (Oricorio A3 066 is in Dustin's deck 15, but Oricorio is not in the archetype name and is not a census card, so it does not bear on the flag.)

## Not re-derived

- The `goldfish --coverage` run itself (an engine binary; I stayed on the safe side of "run no engine games" and only checked that the JSON agrees with the card check's table).
- The other nine cards' Limitless pages (Hoppip, Jumpluff ex, TR Voltorb, Oricorio, Professor's Research, Cyrus, Copycat, Rare Candy, Hiking Trail): read from the card check only. The engine side of Jumpluff ex was confirmed from `card.py` ([C] Breeze-By Attack 70, Stage 2 from Skiploom, HP 160, weak Lightning, retreat 1).
