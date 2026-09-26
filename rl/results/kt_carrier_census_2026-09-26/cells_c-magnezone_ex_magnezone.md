# Limitless cells: Magnezone ex Magnezone against the eight panel decks (kt carrier census)

Descriptive only; this file reports and decides nothing. Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records). Script: `cells_c-magnezone_ex_magnezone.py` in this folder (adapted from B2e's `cells.py`, same counting rules). Machine-readable: `cells_c-magnezone_ex_magnezone.csv`, `cells_c-magnezone_ex_magnezone.json`.

## Window and data sets

- Event window (split.json): **2026-08-26 to 2026-09-24** (UTC event start dates). First event start 2026-08-26T10:35:00.000Z, last 2026-09-24T17:00:00.000Z.
- Events (events.json): **126** total, **63 development**, **63 holdout** (random half split, seed 26092500001).
- Records by split: development 14,127, holdout 16,089. Pooled = both halves. Holdout rows are used for the pooled cells only (B2e README section 3); no holdout standings file was opened and no holdout-only table is written.
- Records by mode: BO1 20,037, BO3 10,177, BO5 2. Every record is one unit (a BO3 set is one record). BO5 records touching this archetype: 0.

## Counting rules (B2e's, unchanged)

The held side is identified by exact deck_name ("Magnezone ex Magnezone"), the panel side by archetype label (each label maps to exactly one deck_name); a tie is half a point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and reported as DL; byes never form a pair; mirrors are excluded; every record is one unit; score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points (0 at 0% or 100%: read those cells as "no information"). Equal-weight = mean of the eight cell scores (opponents with n > 0), band from the same binomial formula divided by the number of opponents (B2e `panel_bands.py`); match-weighted = all panel matches pooled.

Panel opponents identified by archetype label; each label maps to exactly one deck_name: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

## Identification of the held archetype

Held side identified by exact deck_name. Deck ids and labels found under the name (all records in the window, any opponent):

| deck_name | deck_id [label] : records | labeled | unlabeled |
|---|---|---:|---:|
| Magnezone ex Magnezone | `magnezone-ex-b3-magnezone-a2` [(no label)]: 11; `magnezone-ex-b3-magnezone-b1a` [(no label)]: 774 | 0 | 785 |

## The cells

Cell format: W-L-T, n, score %, +/- 95% band. DL = double losses excluded.

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 12-12-0 | 24 | 50.0 | 20.0 | 21-32-1 (DL 1) | 54 | 39.8 | 13.1 |
| altaria | 11-11-0 (DL 1) | 22 | 50.0 | 20.9 | 27-22-0 (DL 3) | 49 | 55.1 | 13.9 |
| sceptile | 4-10-0 | 14 | 28.6 | 23.7 | 13-21-1 | 35 | 38.6 | 16.1 |
| vespiquen | 17-5-0 (DL 1) | 22 | 77.3 | 17.5 | 27-9-1 (DL 3) | 37 | 74.3 | 14.1 |
| suicune | 10-9-1 | 20 | 52.5 | 21.9 | 17-14-2 (DL 1) | 33 | 54.5 | 17.0 |
| hydreigon | 3-7-1 | 11 | 31.8 | 27.5 | 5-12-2 | 19 | 31.6 | 20.9 |
| weezing | 6-5-0 | 11 | 54.5 | 29.4 | 11-9-0 | 20 | 55.0 | 21.8 |
| blaziken | 5-3-0 (DL 1) | 8 | 62.5 | 33.5 | 10-12-1 (DL 1) | 23 | 45.7 | 20.4 |
| **Equal-weight average** | 8 opp. | | **50.9** | 8.8 | 8 opp. | | **49.3** | 6.2 |
| Match-weighted | 68-62-2 (DL 3) | 132 | 52.3 | 8.5 | 131-131-8 (DL 9) | 270 | 50.0 | 6.0 |

Pooled equal-weight interval: **43.2 to 55.5** (development 42.1 to 59.7). Thinnest pooled cell: n = 19; thinnest development cell: n = 8.

BO1-only figures (single-game units), pooled: lucario 9-13-0 n=22 (40.9%); altaria 10-14-0 n=24 (41.7%); sceptile 10-15-1 n=26 (40.4%); vespiquen 12-3-1 n=16 (78.1%); suicune 6-7-2 n=15 (46.7%); hydreigon 3-4-2 n=9 (44.4%); weezing 6-4-0 n=10 (60.0%); blaziken 4-5-0 n=9 (44.4%).

Totals for this archetype (all opponents, any status):

| data set | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 374 | 0 | 374 | 345 | 9 | 20 | 132 | 8 |
| pooled | 785 | 0 | 785 | 718 | 33 | 34 | 270 | 19 |

## Notes

- Thin cells (n under about 20) have bands of 20+ points; a cell at exactly 0% or 100% shows a +/-0.0 band and carries no real information.
- The pooled equal-weight average is the average of the pooled cells, not the average of the two halves' averages.
- A BO3 record is one match unit, the same convention as the scoreboard; the BO1-only numbers are for readers who want single-game units.
- The holdout half was spent once on Sept 25 (kp3 confirmation), so nothing here is a fresh test; development and pooled alike are descriptive baselines. Pooled is the reference figure, as in B2e.
