# Real Limitless cells for the six B2e held-out archetypes

Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records). Script: `cells.py` in this folder. Machine-readable: `limitless_cells.csv`.

## Window and data sets

- Event window (split.json): **2026-08-26 to 2026-09-24** (UTC event start dates). First event start 2026-08-26T10:35:00.000Z, last 2026-09-24T17:00:00.000Z.
- Events (events.json): **126** total, **63 development**, **63 holdout** (random half split, seed 26092500001).
- Records by split: development 14,127, holdout 16,089. Pooled = both halves.
- Records by mode: BO1 20,037, BO3 10,177, BO5 2. Every record is one unit (a BO3 set is one record, as on the scoreboard). BO5 records touching a held archetype: 0.

## How each result_status was treated

| result_status | records | winner field | treatment |
|---|---:|---|---|
| decisive | 26,277 | a player id | win (1) or loss (0) from the held side |
| tie | 866 | 0 | tie, half a point, counted in T and n |
| double_loss | 1,063 | -1 | **excluded** from W-L-T and n (the scoreboard README: double losses are not ties). Counted in the DL column; `score_incl_dl` shows the score if it were a tie |
| bye_or_automatic_loss | 2,010 | player id or -1 | one side has no player or deck, so it never forms an archetype-vs-archetype pair; excluded by construction |

Other rules: a record counts for A vs B when one side's deck_name is exactly A and the other side's archetype label is B; mirrors are excluded; score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points.

## Identification of the six archetypes

Held side identified by exact deck_name. Deck ids and labels found under each name (all records in the window, any opponent):

| archetype | deck_name | deck_id [label] : records | labeled | unlabeled |
|---|---|---|---:|---:|
| manectric_heliolisk | Mega Manectric ex Heliolisk | `mega-manectric-ex-b2b-heliolisk-b1a` [(no label)]: 7; `mega-manectric-ex-b2b-heliolisk-b4` [manectric_heliolisk]: 1318 | 1318 | 7 |
| raticate_ninetales | Team Rocket's Raticate ex Alolan Ninetales ex | `team-rockets-raticate-ex-b4a-alolan-ninetales-ex-b2` [raticate_ninetales]: 637 | 637 | 0 |
| hoopa_absol | Hoopa ex Mega Absol ex | `hoopa-ex-b4-mega-absol-ex-b1` [hoopa_absol]: 1377 | 1377 | 0 |
| garchomp | Garchomp | `garchomp-a2` [(no label)]: 24; `garchomp-b4a` [garchomp]: 359 | 359 | 24 |
| whimsicott_ariados | Whimsicott ex Ariados | `whimsicott-ex-b1-ariados-b1a` [whimsicott_ariados]: 204 | 204 | 0 |
| charizardy_entei | Mega Charizard Y ex Entei ex | `mega-charizard-y-ex-b1a-entei-ex-a4a` [charizardy_entei]: 1229 | 1229 | 0 |

Panel opponents identified by archetype label; each label maps to exactly one deck_name: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

## Development half only

Cell format: score% (+/- band) W-L-T n=all records [n BO1-only, score BO1-only]. DL = double losses excluded.

| archetype | lucario | altaria | sceptile | vespiquen | suicune | hydreigon | weezing | blaziken | equal-weight avg | pooled record |
|---|---|---|---|---|---|---|---|---|---|---|
| manectric_heliolisk | **40.3%** (+/-16.0) 14-21-1 n=36 DL=2 [BO1 n=23, 47.8%] | **53.9%** (+/-13.7) 26-22-3 n=51 DL=2 [BO1 n=34, 52.9%] | **36.8%** (+/-15.3) 13-23-2 n=38 DL=2 [BO1 n=20, 20.0%] | **41.7%** (+/-17.6) 12-17-1 n=30 [BO1 n=16, 46.9%] | **64.3%** (+/-17.7) 17-9-2 n=28 [BO1 n=19, 60.5%] | **40.0%** (+/-21.5) 8-12-0 n=20 DL=2 [BO1 n=12, 50.0%] | **33.3%** (+/-26.7) 4-8-0 n=12 DL=1 [BO1 n=11, 27.3%] | **73.3%** (+/-22.4) 10-3-2 n=15 [BO1 n=12, 79.2%] | **48.0%** over 8 opp. | 47.6% (+/-6.5) 104-115-11 n=230 DL=9 [BO1 n=147] |
| raticate_ninetales | **48.0%** (+/-19.6) 12-13-0 n=25 DL=1 [BO1 n=22, 45.5%] | **10.0%** (+/-18.6) 1-9-0 n=10 DL=1 [BO1 n=4, 0.0%] | **53.1%** (+/-24.5) 8-7-1 n=16 DL=1 [BO1 n=14, 46.4%] | **42.9%** (+/-25.9) 6-8-0 n=14 DL=1 [BO1 n=8, 37.5%] | **42.1%** (+/-22.2) 8-11-0 n=19 DL=1 [BO1 n=12, 50.0%] | **42.9%** (+/-36.7) 3-4-0 n=7 [BO1 n=4, 50.0%] | **32.1%** (+/-24.5) 4-9-1 n=14 [BO1 n=13, 26.9%] | **87.5%** (+/-22.9) 7-1-0 n=8 [BO1 n=6, 83.3%] | **44.8%** over 8 opp. | 44.2% (+/-9.2) 49-62-2 n=113 DL=5 [BO1 n=83] |
| hoopa_absol | **49.2%** (+/-12.6) 29-30-1 n=60 DL=2 [BO1 n=41, 50.0%] | **70.4%** (+/-9.9) 54-21-6 n=81 DL=3 [BO1 n=61, 65.6%] | **40.4%** (+/-14.0) 18-27-2 n=47 DL=1 [BO1 n=33, 48.5%] | **23.2%** (+/-15.6) 5-20-3 n=28 [BO1 n=17, 23.5%] | **48.3%** (+/-17.9) 14-15-1 n=30 DL=1 [BO1 n=19, 50.0%] | **65.4%** (+/-18.3) 17-9-0 n=26 DL=2 [BO1 n=17, 58.8%] | **36.8%** (+/-21.7) 7-12-0 n=19 DL=1 [BO1 n=13, 38.5%] | **79.2%** (+/-23.0) 9-2-1 n=12 [BO1 n=8, 68.8%] | **51.6%** over 8 opp. | 52.8% (+/-5.6) 153-136-14 n=303 DL=10 [BO1 n=209] |
| garchomp | **50.0%** (+/-21.9) 9-9-2 n=20 DL=1 [BO1 n=16, 56.2%] | **36.4%** (+/-28.4) 4-7-0 n=11 [BO1 n=10, 30.0%] | **50.0%** (+/-40.0) 3-3-0 n=6 [BO1 n=6, 50.0%] | **40.0%** (+/-42.9) 2-3-0 n=5 [BO1 n=4, 50.0%] | **22.2%** (+/-27.2) 2-7-0 n=9 DL=1 [BO1 n=6, 33.3%] | **33.3%** (+/-37.7) 2-4-0 n=6 [BO1 n=4, 25.0%] | **13.6%** (+/-20.3) 1-9-1 n=11 [BO1 n=6, 25.0%] | **50.0%** (+/-69.3) 1-1-0 n=2 [BO1 n=1, 0.0%] | **36.9%** over 8 opp. | 36.4% (+/-11.3) 24-43-3 n=70 DL=2 [BO1 n=53] |
| whimsicott_ariados | **62.5%** (+/-33.5) 5-3-0 n=8 [BO1 n=3, 66.7%] | **100.0%** (+/-0.0) 1-0-0 n=1 DL=2 [BO1 n=0] | **0.0%** (+/-0.0) 0-2-0 n=2 [BO1 n=0] | **42.9%** (+/-36.7) 3-4-0 n=7 [BO1 n=4, 25.0%] | **50.0%** (+/-40.0) 3-3-0 n=6 [BO1 n=4, 50.0%] | **40.0%** (+/-42.9) 2-3-0 n=5 [BO1 n=4, 50.0%] | **20.0%** (+/-35.1) 1-4-0 n=5 [BO1 n=3, 0.0%] | no data | **45.1%** over 7 opp. | 44.1% (+/-16.7) 15-19-0 n=34 DL=2 [BO1 n=18] |
| charizardy_entei | **72.3%** (+/-12.8) 34-13-0 n=47 [BO1 n=41, 70.7%] | **39.8%** (+/-13.1) 21-32-1 n=54 [BO1 n=38, 43.4%] | **74.2%** (+/-15.4) 23-8-0 n=31 DL=1 [BO1 n=25, 72.0%] | **54.3%** (+/-20.4) 12-10-1 n=23 [BO1 n=20, 62.5%] | **20.0%** (+/-20.2) 3-12-0 n=15 [BO1 n=12, 25.0%] | **43.8%** (+/-19.8) 10-13-1 n=24 DL=1 [BO1 n=20, 37.5%] | **46.4%** (+/-26.1) 6-7-1 n=14 [BO1 n=12, 54.2%] | **36.4%** (+/-28.4) 4-7-0 n=11 [BO1 n=9, 44.4%] | **48.4%** over 8 opp. | 52.5% (+/-6.6) 113-102-4 n=219 DL=2 [BO1 n=177] |

Totals per archetype in this data set (all opponents, any status):

| archetype | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| manectric_heliolisk | 651 | 646 | 5 | 602 | 26 | 23 | 230 | 12 |
| raticate_ninetales | 279 | 279 | 0 | 258 | 11 | 10 | 113 | 7 |
| hoopa_absol | 764 | 764 | 0 | 716 | 18 | 30 | 303 | 12 |
| garchomp | 185 | 169 | 16 | 162 | 15 | 8 | 70 | 2 |
| whimsicott_ariados | 95 | 95 | 0 | 87 | 3 | 5 | 34 | 0 |
| charizardy_entei | 638 | 638 | 0 | 612 | 11 | 15 | 219 | 11 |

## Holdout half only

Cell format: score% (+/- band) W-L-T n=all records [n BO1-only, score BO1-only]. DL = double losses excluded.

| archetype | lucario | altaria | sceptile | vespiquen | suicune | hydreigon | weezing | blaziken | equal-weight avg | pooled record |
|---|---|---|---|---|---|---|---|---|---|---|
| manectric_heliolisk | **38.6%** (+/-12.6) 21-34-2 n=57 DL=3 [BO1 n=30, 38.3%] | **52.5%** (+/-12.7) 29-26-4 n=59 DL=4 [BO1 n=26, 44.2%] | **42.3%** (+/-15.5) 16-22-1 n=39 [BO1 n=25, 40.0%] | **60.3%** (+/-15.4) 23-15-1 n=39 [BO1 n=22, 54.5%] | **63.2%** (+/-21.7) 10-5-4 n=19 [BO1 n=7, 64.3%] | **51.6%** (+/-17.6) 16-15-0 n=31 [BO1 n=19, 47.4%] | **37.5%** (+/-33.5) 3-5-0 n=8 [BO1 n=6, 33.3%] | **56.8%** (+/-20.7) 12-9-1 n=22 [BO1 n=11, 50.0%] | **50.3%** over 8 opp. | 49.8% (+/-5.9) 130-131-13 n=274 DL=7 [BO1 n=146] |
| raticate_ninetales | **34.5%** (+/-17.3) 10-19-0 n=29 [BO1 n=22, 31.8%] | **9.1%** (+/-12.0) 2-20-0 n=22 [BO1 n=15, 6.7%] | **7.7%** (+/-14.5) 1-12-0 n=13 DL=1 [BO1 n=13, 7.7%] | **50.0%** (+/-18.9) 13-13-1 n=27 DL=1 [BO1 n=18, 47.2%] | **56.7%** (+/-25.1) 8-6-1 n=15 DL=2 [BO1 n=11, 68.2%] | **54.5%** (+/-29.4) 6-5-0 n=11 DL=2 [BO1 n=8, 62.5%] | **35.3%** (+/-22.7) 6-11-0 n=17 DL=1 [BO1 n=11, 36.4%] | **50.0%** (+/-31.0) 5-5-0 n=10 [BO1 n=8, 50.0%] | **37.2%** over 8 opp. | 36.1% (+/-7.8) 51-91-2 n=144 DL=7 [BO1 n=106] |
| hoopa_absol | **34.3%** (+/-15.7) 12-23-0 n=35 DL=1 [BO1 n=17, 29.4%] | **72.9%** (+/-11.3) 41-14-4 n=59 [BO1 n=23, 56.5%] | **21.7%** (+/-14.7) 6-23-1 n=30 DL=1 [BO1 n=17, 26.5%] | **28.0%** (+/-17.6) 7-18-0 n=25 DL=1 [BO1 n=12, 16.7%] | **52.4%** (+/-21.4) 11-10-0 n=21 [BO1 n=11, 45.5%] | **70.5%** (+/-19.1) 15-6-1 n=22 [BO1 n=10, 55.0%] | **42.9%** (+/-25.9) 6-8-0 n=14 [BO1 n=11, 36.4%] | **58.3%** (+/-27.9) 7-5-0 n=12 [BO1 n=7, 42.9%] | **47.6%** over 8 opp. | 49.5% (+/-6.6) 105-107-6 n=218 DL=3 [BO1 n=108] |
| garchomp | **33.3%** (+/-23.9) 4-9-2 n=15 [BO1 n=13, 30.8%] | **71.4%** (+/-33.5) 5-2-0 n=7 [BO1 n=6, 66.7%] | **22.2%** (+/-27.2) 2-7-0 n=9 [BO1 n=7, 28.6%] | **46.2%** (+/-27.1) 6-7-0 n=13 DL=1 [BO1 n=11, 45.5%] | **41.7%** (+/-27.9) 5-7-0 n=12 [BO1 n=8, 50.0%] | **28.6%** (+/-33.5) 2-5-0 n=7 [BO1 n=4, 25.0%] | **20.0%** (+/-35.1) 1-4-0 n=5 [BO1 n=4, 25.0%] | **0.0%** (+/-0.0) 0-8-0 n=8 [BO1 n=7, 0.0%] | **32.9%** over 8 opp. | 34.2% (+/-10.7) 25-49-2 n=76 DL=1 [BO1 n=60] |
| whimsicott_ariados | **12.5%** (+/-22.9) 1-7-0 n=8 DL=1 [BO1 n=6, 16.7%] | **0.0%** (+/-0.0) 0-3-0 n=3 [BO1 n=3, 0.0%] | **33.3%** (+/-53.3) 1-2-0 n=3 DL=1 [BO1 n=3, 33.3%] | **50.0%** (+/-49.0) 2-2-0 n=4 [BO1 n=4, 50.0%] | **66.7%** (+/-53.3) 2-1-0 n=3 DL=1 [BO1 n=3, 66.7%] | **100.0%** (+/-0.0) 1-0-0 n=1 [BO1 n=0] | **33.3%** (+/-53.3) 1-2-0 n=3 [BO1 n=1, 0.0%] | **0.0%** (+/-0.0) 0-1-0 n=1 [BO1 n=0] | **37.0%** over 8 opp. | 30.8% (+/-17.7) 8-18-0 n=26 DL=3 [BO1 n=20] |
| charizardy_entei | **60.9%** (+/-14.1) 26-16-4 n=46 [BO1 n=27, 59.3%] | **41.8%** (+/-13.8) 20-28-1 n=49 DL=2 [BO1 n=26, 48.1%] | **72.6%** (+/-15.7) 22-8-1 n=31 DL=1 [BO1 n=19, 71.1%] | **68.2%** (+/-15.9) 22-10-1 n=33 DL=1 [BO1 n=20, 72.5%] | **13.9%** (+/-16.0) 2-15-1 n=18 [BO1 n=12, 20.8%] | **52.6%** (+/-22.5) 9-8-2 n=19 [BO1 n=9, 61.1%] | **61.5%** (+/-26.4) 7-4-2 n=13 [BO1 n=10, 65.0%] | **29.4%** (+/-21.7) 5-12-0 n=17 [BO1 n=11, 18.2%] | **50.1%** over 8 opp. | 52.7% (+/-6.5) 113-101-12 n=226 DL=4 [BO1 n=134] |

Totals per archetype in this data set (all opponents, any status):

| archetype | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| manectric_heliolisk | 674 | 672 | 2 | 617 | 25 | 32 | 274 | 8 |
| raticate_ninetales | 358 | 358 | 0 | 329 | 19 | 10 | 144 | 10 |
| hoopa_absol | 613 | 613 | 0 | 574 | 15 | 24 | 218 | 12 |
| garchomp | 198 | 190 | 8 | 191 | 4 | 3 | 76 | 5 |
| whimsicott_ariados | 109 | 109 | 0 | 95 | 11 | 3 | 26 | 1 |
| charizardy_entei | 591 | 591 | 0 | 560 | 14 | 17 | 226 | 13 |

## Pooled (both halves)

Cell format: score% (+/- band) W-L-T n=all records [n BO1-only, score BO1-only]. DL = double losses excluded.

| archetype | lucario | altaria | sceptile | vespiquen | suicune | hydreigon | weezing | blaziken | equal-weight avg | pooled record |
|---|---|---|---|---|---|---|---|---|---|---|
| manectric_heliolisk | **39.2%** (+/-9.9) 35-55-3 n=93 DL=5 [BO1 n=53, 42.5%] | **53.2%** (+/-9.3) 55-48-7 n=110 DL=6 [BO1 n=60, 49.2%] | **39.6%** (+/-10.9) 29-45-3 n=77 DL=2 [BO1 n=45, 31.1%] | **52.2%** (+/-11.8) 35-32-2 n=69 [BO1 n=38, 51.3%] | **63.8%** (+/-13.7) 27-14-6 n=47 [BO1 n=26, 61.5%] | **47.1%** (+/-13.7) 24-27-0 n=51 DL=2 [BO1 n=31, 48.4%] | **35.0%** (+/-20.9) 7-13-0 n=20 DL=1 [BO1 n=17, 29.4%] | **63.5%** (+/-15.5) 22-12-3 n=37 [BO1 n=23, 65.2%] | **49.2%** over 8 opp. | 48.8% (+/-4.4) 234-246-24 n=504 DL=16 [BO1 n=293] |
| raticate_ninetales | **40.7%** (+/-13.1) 22-32-0 n=54 DL=1 [BO1 n=44, 38.6%] | **9.4%** (+/-10.1) 3-29-0 n=32 DL=1 [BO1 n=19, 5.3%] | **32.8%** (+/-17.1) 9-19-1 n=29 DL=2 [BO1 n=27, 27.8%] | **47.6%** (+/-15.3) 19-21-1 n=41 DL=2 [BO1 n=26, 44.2%] | **48.5%** (+/-16.8) 16-17-1 n=34 DL=3 [BO1 n=23, 58.7%] | **50.0%** (+/-23.1) 9-9-0 n=18 DL=2 [BO1 n=12, 58.3%] | **33.9%** (+/-16.7) 10-20-1 n=31 DL=1 [BO1 n=24, 31.2%] | **66.7%** (+/-21.8) 12-6-0 n=18 [BO1 n=14, 64.3%] | **41.2%** over 8 opp. | 39.7% (+/-6.0) 100-153-4 n=257 DL=12 [BO1 n=189] |
| hoopa_absol | **43.7%** (+/-10.0) 41-53-1 n=95 DL=3 [BO1 n=58, 44.0%] | **71.4%** (+/-7.5) 95-35-10 n=140 DL=3 [BO1 n=84, 63.1%] | **33.1%** (+/-10.5) 24-50-3 n=77 DL=2 [BO1 n=50, 41.0%] | **25.5%** (+/-11.7) 12-38-3 n=53 DL=1 [BO1 n=29, 20.7%] | **50.0%** (+/-13.7) 25-25-1 n=51 DL=1 [BO1 n=30, 48.3%] | **67.7%** (+/-13.2) 32-15-1 n=48 DL=2 [BO1 n=27, 57.4%] | **39.4%** (+/-16.7) 13-20-0 n=33 DL=1 [BO1 n=24, 37.5%] | **68.8%** (+/-18.5) 16-7-1 n=24 [BO1 n=15, 56.7%] | **49.9%** over 8 opp. | 51.4% (+/-4.3) 258-243-20 n=521 DL=13 [BO1 n=317] |
| garchomp | **42.9%** (+/-16.4) 13-18-4 n=35 DL=1 [BO1 n=29, 44.8%] | **50.0%** (+/-23.1) 9-9-0 n=18 [BO1 n=16, 43.8%] | **33.3%** (+/-23.9) 5-10-0 n=15 [BO1 n=13, 38.5%] | **44.4%** (+/-23.0) 8-10-0 n=18 DL=1 [BO1 n=15, 46.7%] | **33.3%** (+/-20.2) 7-14-0 n=21 DL=1 [BO1 n=14, 42.9%] | **30.8%** (+/-25.1) 4-9-0 n=13 [BO1 n=8, 25.0%] | **15.6%** (+/-17.8) 2-13-1 n=16 [BO1 n=10, 25.0%] | **10.0%** (+/-18.6) 1-9-0 n=10 [BO1 n=8, 0.0%] | **32.5%** over 8 opp. | 35.3% (+/-7.8) 49-92-5 n=146 DL=3 [BO1 n=113] |
| whimsicott_ariados | **37.5%** (+/-23.7) 6-10-0 n=16 DL=1 [BO1 n=9, 33.3%] | **25.0%** (+/-42.4) 1-3-0 n=4 DL=2 [BO1 n=3, 0.0%] | **20.0%** (+/-35.1) 1-4-0 n=5 DL=1 [BO1 n=3, 33.3%] | **45.5%** (+/-29.4) 5-6-0 n=11 [BO1 n=8, 37.5%] | **55.6%** (+/-32.5) 5-4-0 n=9 DL=1 [BO1 n=7, 57.1%] | **50.0%** (+/-40.0) 3-3-0 n=6 [BO1 n=4, 50.0%] | **25.0%** (+/-30.0) 2-6-0 n=8 [BO1 n=4, 0.0%] | **0.0%** (+/-0.0) 0-1-0 n=1 [BO1 n=0] | **32.3%** over 8 opp. | 38.3% (+/-12.3) 23-37-0 n=60 DL=5 [BO1 n=38] |
| charizardy_entei | **66.7%** (+/-9.6) 60-29-4 n=93 [BO1 n=68, 66.2%] | **40.8%** (+/-9.5) 41-60-2 n=103 DL=2 [BO1 n=64, 45.3%] | **73.4%** (+/-11.0) 45-16-1 n=62 DL=2 [BO1 n=44, 71.6%] | **62.5%** (+/-12.7) 34-20-2 n=56 DL=1 [BO1 n=40, 67.5%] | **16.7%** (+/-12.7) 5-27-1 n=33 [BO1 n=24, 22.9%] | **47.7%** (+/-14.9) 19-21-3 n=43 DL=1 [BO1 n=29, 44.8%] | **53.7%** (+/-18.8) 13-11-3 n=27 [BO1 n=22, 59.1%] | **32.1%** (+/-17.3) 9-19-0 n=28 [BO1 n=20, 30.0%] | **49.2%** over 8 opp. | 52.6% (+/-4.6) 226-203-16 n=445 DL=6 [BO1 n=311] |

Totals per archetype in this data set (all opponents, any status):

| archetype | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| manectric_heliolisk | 1325 | 1318 | 7 | 1219 | 51 | 55 | 504 | 20 |
| raticate_ninetales | 637 | 637 | 0 | 587 | 30 | 20 | 257 | 18 |
| hoopa_absol | 1377 | 1377 | 0 | 1290 | 33 | 54 | 521 | 24 |
| garchomp | 383 | 359 | 24 | 353 | 19 | 11 | 146 | 10 |
| whimsicott_ariados | 204 | 204 | 0 | 182 | 14 | 8 | 60 | 1 |
| charizardy_entei | 1229 | 1229 | 0 | 1172 | 25 | 32 | 445 | 27 |

## Cross-check against the scoreboard's own development records

`held_archetype_records.csv` (development only, 48 panel cells) was recomputed with this script's rules: **41 of 48 cells match exactly**, 7 differ.

| archetype | opponent | scoreboard W-L-T | this script by deck_name | this script by label | label-only matches? |
|---|---|---|---|---|---|
| manectric_heliolisk | sceptile | 13-22-2 (n=37) | 13-23-2 (n=38, DL=2) | 13-22-2 (n=37) | yes |
| manectric_heliolisk | vespiquen | 11-17-1 (n=29) | 12-17-1 (n=30, DL=0) | 11-17-1 (n=29) | yes |
| garchomp | altaria | 2-7-0 (n=9) | 4-7-0 (n=11, DL=0) | 2-7-0 (n=9) | yes |
| garchomp | lucario | 9-8-1 (n=18) | 9-9-2 (n=20, DL=1) | 9-8-1 (n=18) | yes |
| garchomp | suicune | 1-7-0 (n=8) | 2-7-0 (n=9, DL=1) | 1-7-0 (n=8) | yes |
| garchomp | vespiquen | 2-2-0 (n=4) | 2-3-0 (n=5, DL=0) | 2-2-0 (n=4) | yes |
| garchomp | weezing | 1-8-1 (n=10) | 1-9-1 (n=11, DL=0) | 1-8-1 (n=10) | yes |

Differences come from the unlabeled same-name variants (Garchomp `garchomp-a2`, Manectric `mega-manectric-ex-b2b-heliolisk-b1a`): the scoreboard keyed on the archetype label (exact deck id), this report keys on deck_name as the task specifies.

## Notes

- Thin cells (n under ~20) have bands of 20+ points; Whimsicott and Garchomp are thin against most of the panel.
- A cell at exactly 0% or 100% shows a +/-0.0 band: the 1.96 sqrt(p(1-p)/n) formula collapses there. Read those cells as 'n tiny, no real information', not as certain.
- The pooled equal-weight average is the average of the pooled cells, not the average of the two halves' averages, so it can fall outside them when a cell's halves differ in size (Garchomp vs blaziken: 1-1 development, 0-8 holdout).
- A BO3 record is one match unit, the same convention as the scoreboard; the BO1-only numbers are shown for readers who want single-game units.
- The development half is the half the skill model and decklist selection used; holdout is untouched by any fitting.
