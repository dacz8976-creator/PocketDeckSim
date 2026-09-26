# Limitless cells: Mega Altaria ex Igglybuff against the eight panel decks

Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records), window 2026-08-26 to 2026-09-24 (UTC event start dates), 63 development and 63 holdout events. Script: `cells_c-mega_altaria_ex_igglybuff.py` (adapted from B2e's `cells.py`; same counting rules). Machine-readable: `cells_c-mega_altaria_ex_igglybuff.csv`, `cells_c-mega_altaria_ex_igglybuff.json`.

Counting rules (B2e README section 3): the held side is identified by exact deck_name, the panel side by archetype label; a tie is half a point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and shown as DL; byes never form a pair; mirrors cannot occur; every record is one unit, BO1 and BO3 alike (BO1-only figures in the CSV); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% or 100% (read those as 'no information'). Equal-weight average = unweighted mean of the cell scores with n > 0; its band = 1.96 sqrt(sum p(1-p)/n) / K (`panel_bands.py`). Match-weighted = all panel matches pooled. Holdout discipline: only matches.csv rows are read (development rows for the development cells, both halves for the pooled cells, exactly as B2e section 3 did); no holdout standings file was opened.

Held deck ids under this name (all records in the window, any opponent): `mega-altaria-ex-b1-igglybuff-a4a` [(no label)]: 271.

Panel labels: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

## Mega Altaria ex Igglybuff

Cell format: W-L-T, n, score %, +/- 95% band (points). DL = double losses excluded.

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 7-5-0 (DL 2) | 12 | 58.3 | 27.9 | 16-11-1 (DL 3) | 28 | 58.9 | 18.2 |
| altaria | 6-1-0 | 7 | 85.7 | 25.9 | 11-8-0 | 19 | 57.9 | 22.2 |
| sceptile | 2-6-0 | 8 | 25.0 | 30.0 | 2-7-2 | 11 | 27.3 | 26.3 |
| vespiquen | 3-1-0 | 4 | 75.0 | 42.4 | 6-6-0 (DL 1) | 12 | 50.0 | 28.3 |
| suicune | 0-1-0 | 1 | 0.0 | 0.0 | 2-3-0 | 5 | 40.0 | 42.9 |
| hydreigon | 0-1-0 | 1 | 0.0 | 0.0 | 3-2-0 | 5 | 60.0 | 42.9 |
| weezing | 2-2-0 (DL 1) | 4 | 50.0 | 49.0 | 3-2-1 (DL 1) | 6 | 58.3 | 39.4 |
| blaziken | 4-2-0 | 6 | 66.7 | 37.7 | 5-3-0 | 8 | 62.5 | 33.5 |
| **Equal-weight average** | 8 opp. | | **45.1** | 11.2 | 8 opp. | | **51.9** | 11.7 |
| Match-weighted | 24-19-0 (DL 3) | 43 | 55.8 | 14.8 | 48-42-4 (DL 5) | 94 | 53.2 | 10.1 |

### The intervals in one place

| Data set | Equal-weight % | +/- | Interval | Opponents with data | Matches vs panel | Thinnest cell n | Records in window (any opponent) |
|---|---:|---:|---|---:|---:|---:|---:|
| development | 45.1 | 11.2 | 33.9 to 56.3 | 8 of 8 | 43 | 1 | 135 (scored 120, DL 7, bye 8) |
| pooled | 51.9 | 11.7 | 40.2 to 63.5 | 8 of 8 | 94 | 5 | 271 (scored 240, DL 18, bye 13) |

### Notes

- Pooled cells under 20 matches (bands of 20+ points): altaria, sceptile, vespiquen, suicune, hydreigon, weezing, blaziken. A cell at exactly 0% or 100% shows a +/-0.0 band and contributes nothing to the equal-weight band, which then understates the real uncertainty.
- Pooled (both halves) is the reference figure the B2e README uses for its veto rule; the development-half figure is reported beside it. These are descriptive cells, not a test: the holdout half was spent on Sept 25.
- This file reports; it decides nothing and changes no rule.
