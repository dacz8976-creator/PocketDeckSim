# Limitless cells: Jumpluff ex Team Rocket's Electrode against the eight panel decks

Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records; development 14,127, holdout 16,089). Window 2026-08-26 to 2026-09-24 (UTC event start dates), 63 development and 63 holdout events (split seed 26092500001). Script: `cells_c-jumpluff_ex_team_rocket_s_electrode.py` (adapted from B2e's `cells.py`, same rules). Machine-readable: `cells_c-jumpluff_ex_team_rocket_s_electrode.csv`.

Counting rules: the held side is identified by exact deck_name, the panel side by archetype label; a tie is half a point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and shown as DL; byes have no opponent side and never form a pair; mirrors are excluded; every record is one unit, BO1 and BO3 alike (BO1-only figures are in the CSV); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% or 100% (read those cells as no information). Equal-weight = unweighted mean of the cell scores with n > 0, band = 1.96 sqrt(sum p(1-p)/n) / K, as B2e's `panel_bands.py`. Holdout rows are used only inside the pooled cells; no holdout-only table is written and no holdout standings file was opened. Pooled is the reference, as in B2e; development is reported beside it.

Panel labels: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

Held side deck ids and labels found under this name (all records in the window, any opponent): `jumpluff-ex-a4a-team-rockets-electrode-b4a` [(no label)]: 220.

## The cells

Cell format: W-L-T, n, score %, +/- 95% band. DL = double losses excluded.

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 5-5-1 (DL 1) | 11 | 50.0 | 29.5 | 7-10-1 (DL 3) | 18 | 41.7 | 22.8 |
| altaria | 2-5-0 | 7 | 28.6 | 33.5 | 7-9-0 (DL 2) | 16 | 43.8 | 24.3 |
| sceptile | 1-5-0 | 6 | 16.7 | 29.8 | 2-8-0 | 10 | 20.0 | 24.8 |
| vespiquen | 9-0-0 | 9 | 100.0 | 0.0 | 12-1-0 | 13 | 92.3 | 14.5 |
| suicune | 2-3-0 | 5 | 40.0 | 42.9 | 4-7-0 | 11 | 36.4 | 28.4 |
| hydreigon | 3-1-0 | 4 | 75.0 | 42.4 | 6-6-0 | 12 | 50.0 | 28.3 |
| weezing | 0-4-1 | 5 | 10.0 | 26.3 | 0-9-1 | 10 | 5.0 | 13.5 |
| blaziken | no games | 0 |  |  | 1-3-0 | 4 | 25.0 | 42.4 |
| **Equal-weight average** | 7 opp. | | **45.7** | 12.1 | 8 opp. | | **39.3** | 9.3 |
| Match-weighted | 22-23-2 (DL 1) | 47 | 48.9 | 14.3 | 39-53-2 (DL 5) | 94 | 42.6 | 10.0 |

## Totals for this archetype (all opponents, any status)

| Data set | records | scored (W/L/T) | W | L | T | double loss | bye | vs panel (scored) | thinnest panel cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 105 | 101 | 48 | 48 | 5 | 3 | 1 | 47 | 0 |
| pooled | 220 | 204 | 87 | 110 | 7 | 10 | 6 | 94 | 4 |

Opponent deck names met most often (pooled, scored or double-loss records, for context only): Mega Lucario ex Lucario (21); Mega Altaria ex Espeon (18); Vespiquen ex Shuckle ex (13); Hydreigon Mega Absol ex (12); Suicune ex Baxcalibur (11); Butterfree Mega Sceptile ex (10); Team Rocket's Weezing ex Hoopa ex (10); Mega Altaria ex (7); Magnezone Miraidon ex (6); Mega Manectric ex Heliolisk (5); Dedenne ex Indeedee ex (5); Mega Blaziken ex Greninja (4).

## Reading

- Pooled cells under 20 matches: lucario, altaria, sceptile, vespiquen, suicune, hydreigon, weezing, blaziken.
- These are descriptive baselines, not a test; the holdout half was spent on Sept 25 (B2e README section 3). Nothing here decides anything about the kt candidate.
