# Recount vs census_summary.json (kt carrier census, development half)

Date: 2026-09-26. Recount script: scratchpad kt_census/recount.py (copy: rl/results/kt_carrier_census_2026-09-26/recount.py). The recount was written and run from the data description before scan_census.py or its outputs were opened; this file is the comparison made afterwards.

## Totals

| quantity | recount | census |
|---|---|---|
| development events scanned | 63 | 63 |
| holdout events skipped (standings never opened) | 63 | 63 |
| standings entries | 4884 | 4884 |
| entries with a decklist | 4722 | 4722 |
| development matches.csv rows | 14127 | 14127 |
| card labels in the set | 46 | 46 |
| archetypes scanned (Sept 10 top 30 + window top 30) | 35 | 35 |
| Sept 10 top-30 archetypes with no decklists | 0 | 0 |

Archetype sets identical: True.

## Per-archetype comparison (n_lists, any_carrier_n, and the other counts)

| archetype | n_lists (recount / census) | any_carrier_n (recount / census) | n_entries | n_events | rank_window | window matches (recount / census) | dustin (recount / census) | per-card counts differ? |
|---|---|---|---|---|---|---|---|---|
| Mega Lucario ex Lucario | 398 / 398 | 222 / 222 | 398 / 398 | 58 / 58 | 1 / 1 | 2243 / 2044 | False / False | no |
| Mega Altaria ex Espeon | 336 / 336 | 0 / 0 | 336 / 336 | 52 / 52 | 2 / 2 | 2038 / 1879 | False / False | no |
| Butterfree Mega Sceptile ex | 244 / 244 | 3 / 3 | 244 / 244 | 50 / 50 | 3 / 3 | 1410 / 1320 | False / False | no |
| Vespiquen ex Shuckle ex | 233 / 233 | 4 / 4 | 233 / 233 | 52 / 52 | 4 / 4 | 1368 / 1259 | False / False | no |
| Suicune ex Baxcalibur | 200 / 200 | 22 / 22 | 200 / 200 | 47 / 47 | 5 / 5 | 1125 / 1036 | False / False | no |
| Team Rocket's Weezing ex Hoopa ex | 152 / 152 | 35 / 35 | 152 / 152 | 43 / 43 | 7 / 7 | 839 / 767 | True / True | no |
| Mega Blaziken ex | 108 / 108 | 97 / 97 | 108 / 108 | 38 / 38 | 13 / 14 | 598 / 557 | True / True | no |
| Hydreigon Mega Absol ex | 139 / 139 | 10 / 10 | 139 / 139 | 49 / 49 | 8 / 8 | 794 / 733 | True / True | no |
| Mega Sceptile ex Greninja | 98 / 98 | 0 / 0 | 98 / 98 | 39 / 39 | 15 / 15 | 588 / 548 | False / False | no |
| Team Rocket's Raticate ex Alolan Ninetales ex | 55 / 55 | 0 / 0 | 55 / 55 | 28 / 28 | 22 / 22 | 279 / 258 | True / True | no |
| Mega Manectric ex Heliolisk | 111 / 111 | 2 / 2 | 111 / 111 | 40 / 40 | 11 / 12 | 651 / 602 | True / True | no |
| Mega Charizard Y ex Entei ex | 106 / 106 | 23 / 23 | 106 / 106 | 43 / 43 | 12 / 11 | 638 / 612 | True / True | no |
| Magnezone Miraidon ex | 90 / 90 | 3 / 3 | 90 / 90 | 35 / 35 | 14 / 13 | 591 / 568 | False / False | no |
| Hoopa ex Mega Absol ex | 128 / 128 | 0 / 0 | 128 / 128 | 46 / 46 | 9 / 9 | 764 / 716 | True / True | no |
| Magnezone ex Magnezone | 65 / 65 | 31 / 31 | 65 / 65 | 28 / 28 | 18 / 18 | 374 / 345 | False / False | no |
| Mega Altaria ex Greninja | 125 / 125 | 1 / 1 | 125 / 125 | 42 / 42 | 10 / 10 | 715 / 680 | False / False | no |
| Dedenne ex Indeedee ex | 95 / 95 | 56 / 56 | 95 / 95 | 40 / 40 | 16 / 16 | 561 / 513 | True / True | no |
| Milotic ex Eevee ex | 51 / 51 | 0 / 0 | 51 / 51 | 28 / 28 | 20 / 20 | 311 / 285 | True / True | no |
| Mega Altaria ex | 44 / 44 | 2 / 2 | 44 / 44 | 28 / 28 | 21 / 21 | 280 / 260 | False / False | no |
| Mega Blaziken ex Greninja | 63 / 63 | 0 / 0 | 63 / 63 | 33 / 33 | 17 / 17 | 385 / 358 | True / True | no |
| Garchomp | 36 / 36 | 12 / 12 | 36 / 36 | 19 / 19 | 29 / 29 | 185 / 162 | True / True | no |
| Dragonair Mega Rayquaza ex | 143 / 143 | 141 / 141 | 143 / 143 | 44 / 44 | 6 / 6 | 857 / 818 | True / True | no |
| Mega Charizard X ex Mega Charizard Y ex | 30 / 30 | 14 / 14 | 30 / 30 | 18 / 18 | 32 / 32 | 154 / 147 | True / True | no |
| Mega Sharpedo ex Gyarados | 35 / 35 | 0 / 0 | 35 / 35 | 20 / 20 | 27 / 26 | 205 / 191 | False / False | no |
| Mega Manectric ex Team Rocket's Electrode | 22 / 22 | 14 / 14 | 22 / 22 | 19 / 19 | 36 / 37 | 116 / 109 | True / True | no |
| Whimsicott ex Ariados | 21 / 21 | 0 / 0 | 21 / 21 | 13 / 13 | 44 / 44 | 95 / 87 | True / True | no |
| Mega Altaria ex Chingling | 38 / 38 | 0 / 0 | 38 / 38 | 17 / 17 | 26 / 27 | 211 / 186 | False / False | no |
| Jumpluff ex Team Rocket's Electrode | 18 / 18 | 17 / 17 | 18 / 18 | 15 / 15 | 40 / 39 | 105 / 101 | False / False | no |
| Mega Altaria ex Igglybuff | 25 / 25 | 6 / 6 | 25 / 25 | 20 / 20 | 34 / 34 | 135 / 120 | False / False | no |
| Meowscarada ex Meowscarada | 29 / 29 | 0 / 0 | 29 / 29 | 22 / 22 | 28 / 28 | 185 / 173 | False / False | no |
| Zoroark ex Mega Absol ex | 54 / 54 | 4 / 4 | 54 / 54 | 29 / 29 | 19 / 19 | 324 / 304 | True / True | no |
| Beautifly Dustox | 47 / 47 | 0 / 0 | 47 / 47 | 24 / 24 | 23 / 23 | 256 / 232 | False / False | no |
| Miraidon ex Magnezone | 33 / 33 | 0 / 0 | 33 / 33 | 19 / 19 | 24 / 25 | 221 / 206 | False / False | no |
| Hoopa ex Mega Sableye ex | 34 / 34 | 34 / 34 | 34 / 34 | 24 / 24 | 25 / 24 | 216 / 208 | True / True | no |
| Hoopa ex Greninja | 31 / 31 | 6 / 6 | 31 / 31 | 22 / 22 | 30 / 30 | 174 / 160 | True / True | no |

## Differences

Archetypes where n_lists or any_carrier_n differ: 0.
Archetypes where anything compared differs: 35.

- Mega Lucario ex Lucario: differs in window_matches.
    - window matches: recount 2243 (every development row, both sides, byes and mirrors included), census 2044; rank 1 vs 1
- Mega Altaria ex Espeon: differs in window_matches.
    - window matches: recount 2038 (every development row, both sides, byes and mirrors included), census 1879; rank 2 vs 2
- Butterfree Mega Sceptile ex: differs in window_matches.
    - window matches: recount 1410 (every development row, both sides, byes and mirrors included), census 1320; rank 3 vs 3
- Vespiquen ex Shuckle ex: differs in window_matches.
    - window matches: recount 1368 (every development row, both sides, byes and mirrors included), census 1259; rank 4 vs 4
- Suicune ex Baxcalibur: differs in window_matches.
    - window matches: recount 1125 (every development row, both sides, byes and mirrors included), census 1036; rank 5 vs 5
- Team Rocket's Weezing ex Hoopa ex: differs in window_matches.
    - window matches: recount 839 (every development row, both sides, byes and mirrors included), census 767; rank 7 vs 7
- Mega Blaziken ex: differs in rank_window, window_matches.
    - window matches: recount 598 (every development row, both sides, byes and mirrors included), census 557; rank 13 vs 14
- Hydreigon Mega Absol ex: differs in window_matches.
    - window matches: recount 794 (every development row, both sides, byes and mirrors included), census 733; rank 8 vs 8
- Mega Sceptile ex Greninja: differs in window_matches.
    - window matches: recount 588 (every development row, both sides, byes and mirrors included), census 548; rank 15 vs 15
- Team Rocket's Raticate ex Alolan Ninetales ex: differs in window_matches.
    - window matches: recount 279 (every development row, both sides, byes and mirrors included), census 258; rank 22 vs 22
- Mega Manectric ex Heliolisk: differs in rank_window, window_matches.
    - window matches: recount 651 (every development row, both sides, byes and mirrors included), census 602; rank 11 vs 12
- Mega Charizard Y ex Entei ex: differs in rank_window, window_matches.
    - window matches: recount 638 (every development row, both sides, byes and mirrors included), census 612; rank 12 vs 11
- Magnezone Miraidon ex: differs in rank_window, window_matches.
    - window matches: recount 591 (every development row, both sides, byes and mirrors included), census 568; rank 14 vs 13
- Hoopa ex Mega Absol ex: differs in window_matches.
    - window matches: recount 764 (every development row, both sides, byes and mirrors included), census 716; rank 9 vs 9
- Magnezone ex Magnezone: differs in window_matches.
    - window matches: recount 374 (every development row, both sides, byes and mirrors included), census 345; rank 18 vs 18
- Mega Altaria ex Greninja: differs in window_matches.
    - window matches: recount 715 (every development row, both sides, byes and mirrors included), census 680; rank 10 vs 10
- Dedenne ex Indeedee ex: differs in window_matches.
    - window matches: recount 561 (every development row, both sides, byes and mirrors included), census 513; rank 16 vs 16
- Milotic ex Eevee ex: differs in window_matches.
    - window matches: recount 311 (every development row, both sides, byes and mirrors included), census 285; rank 20 vs 20
- Mega Altaria ex: differs in window_matches.
    - window matches: recount 280 (every development row, both sides, byes and mirrors included), census 260; rank 21 vs 21
- Mega Blaziken ex Greninja: differs in window_matches.
    - window matches: recount 385 (every development row, both sides, byes and mirrors included), census 358; rank 17 vs 17
- Garchomp: differs in window_matches.
    - window matches: recount 185 (every development row, both sides, byes and mirrors included), census 162; rank 29 vs 29
- Dragonair Mega Rayquaza ex: differs in window_matches.
    - window matches: recount 857 (every development row, both sides, byes and mirrors included), census 818; rank 6 vs 6
- Mega Charizard X ex Mega Charizard Y ex: differs in window_matches.
    - window matches: recount 154 (every development row, both sides, byes and mirrors included), census 147; rank 32 vs 32
- Mega Sharpedo ex Gyarados: differs in rank_window, window_matches.
    - window matches: recount 205 (every development row, both sides, byes and mirrors included), census 191; rank 27 vs 26
- Mega Manectric ex Team Rocket's Electrode: differs in rank_window, window_matches.
    - window matches: recount 116 (every development row, both sides, byes and mirrors included), census 109; rank 36 vs 37
- Whimsicott ex Ariados: differs in window_matches.
    - window matches: recount 95 (every development row, both sides, byes and mirrors included), census 87; rank 44 vs 44
- Mega Altaria ex Chingling: differs in rank_window, window_matches.
    - window matches: recount 211 (every development row, both sides, byes and mirrors included), census 186; rank 26 vs 27
- Jumpluff ex Team Rocket's Electrode: differs in rank_window, window_matches.
    - window matches: recount 105 (every development row, both sides, byes and mirrors included), census 101; rank 40 vs 39
- Mega Altaria ex Igglybuff: differs in window_matches.
    - window matches: recount 135 (every development row, both sides, byes and mirrors included), census 120; rank 34 vs 34
- Meowscarada ex Meowscarada: differs in window_matches.
    - window matches: recount 185 (every development row, both sides, byes and mirrors included), census 173; rank 28 vs 28
- Zoroark ex Mega Absol ex: differs in window_matches.
    - window matches: recount 324 (every development row, both sides, byes and mirrors included), census 304; rank 19 vs 19
- Beautifly Dustox: differs in window_matches.
    - window matches: recount 256 (every development row, both sides, byes and mirrors included), census 232; rank 23 vs 23
- Miraidon ex Magnezone: differs in rank_window, window_matches.
    - window matches: recount 221 (every development row, both sides, byes and mirrors included), census 206; rank 24 vs 25
- Hoopa ex Mega Sableye ex: differs in rank_window, window_matches.
    - window matches: recount 216 (every development row, both sides, byes and mirrors included), census 208; rank 25 vs 24
- Hoopa ex Greninja: differs in window_matches.
    - window matches: recount 174 (every development row, both sides, byes and mirrors included), census 160; rank 30 vs 30

## Causes, in plain language

1. **n_lists and any_carrier_n agree for every archetype** (all 30 Sept 10 names and the 5 window-only names), and so do n_entries, n_events and every per-card list count. The two scans read the same 63 development standings files, matched cards the same way (set + number, a same-name line with another printing is not a carrier), and never opened a holdout file.
2. **Window match counts differ on every archetype by a fixed rule, not by data.** The recount counted every development row of matches.csv (both sides, byes, double losses, mirrors); the census counts only rows with result_status decisive or tie (its README rule for resolved two-sided pairings). The probe below reproduces the census number exactly under that rule. The window top 30 has the same 30 members either way (same five Sept 10 names missing, same five window-only names present); a few adjacent ranks swap (for example Mega Blaziken ex 13 vs 14, Mega Manectric ex Heliolisk 11 vs 12).
3. **Dustin flag.** The first recount run flagged four archetypes as not Dustin's that the census flags as Dustin's: Milotic ex Eevee ex, Zoroark ex Mega Absol ex, Hoopa ex Mega Sableye ex, Hoopa ex Greninja. Three were the recount's omission (its hand-written map only covered the Sept 10 names, and the window-only names fell through): brew-07 carries Hoopa ex and Mega Sableye ex, and the other two share Hoopa ex / Mega Absol ex with held archetypes, exactly as the recount treated Hydreigon Mega Absol ex. Milotic ex Eevee ex is a judgment call (Eevee B1 184 in decks/dustin/15 versus the archetype's Eevee ex, a different card); the recount now follows the in-doubt rule and marks it Dustin's, noting the doubt is thin and the archetype carries none of the census cards, so the flag has no bearing on clause (d). After extending the map the two scans agree on every Dustin flag. The census's 'shares_pokemon' rule is mechanical (any Pokemon name in the archetype found as a card in any Dustin file); the recount's map is by main Pokemon, hand-written; on these 35 names they now give the same answer.
4. **Card-set labels.** Both scans keep Ferrothorn as two entries (B1 167 Guard Press in group 3; A3a 052 Steel Spikes ability in group 4). The recount labels the second 'Ferrothorn [A3a 052]'; the census labels both 'Ferrothorn'. Neither printing appears in any scanned list, so no count is affected.
5. **Frigibax.** 194 Suicune ex Baxcalibur lists carry Frigibax B2a 034, which is outside the set; python lib/card.py "Frigibax" shows that printing's attack is Chilly, not Stiffen, so both scans are right to count only the 22 lists with P-B 037. Both scans report the B2a lists under same-name-other-printing.

## Match-count rule probe (why window match counts may differ)

Census window_dev_matches for Mega Lucario ex Lucario = 2044. Rules tried on the development rows of matches.csv and the count each gives for that archetype:

- all_rows_both_sides: 2243
- exclude_bye: 2149
- decisive_only: 1991
- decisive_or_tie: 2044
- exclude_bye_and_double_loss: 2044
- mirror_once_all: 2147
- mirror_once_exclude_bye: 2053

Rules that reproduce the census number: ['decisive_or_tie', 'exclude_bye_and_double_loss'].
