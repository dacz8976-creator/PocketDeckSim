# Limitless cells: Dragonair Mega Rayquaza ex against the eight panel decks

List: `decks/c-dragonair_mega_rayquaza_ex.txt` (kt carrier census, Sept 26, 2026; thefossilman, 1st of 219, Umbreon99's Aura Sphere #4, 2026-09-11; provenance in `provenance/c-dragonair_mega_rayquaza_ex.json`). The cells are for the Limitless archetype (exact deck_name "Dragonair Mega Rayquaza ex"), not for this one list: every list under that deck_name counts, whether or not it carries Gouging Fire (135 of the 143 development-half lists do; census.csv).

Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records), window 2026-08-26 to 2026-09-24 (UTC event start dates), 63 development and 63 holdout events. Script: `cells_c-dragonair_mega_rayquaza_ex.py` (adapted from `cells_c-mega_altaria_ex_igglybuff.py`, itself from B2e's `cells.py`; same counting rules). Machine-readable: `cells_c-dragonair_mega_rayquaza_ex.csv`, `cells_c-dragonair_mega_rayquaza_ex.json`.

Counting rules (B2e README section 3): the held side is identified by exact deck_name, the panel side by archetype label; a tie is half a point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and shown as DL; byes never form a pair; the held name is not a panel deck_name, so no panel cell is a mirror (Rayquaza-vs-Rayquaza records are set aside and counted below); every record is one unit, BO1 and BO3 alike (BO1-only figures in the CSV); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% or 100% (read those as 'no information'). Equal-weight average = unweighted mean of the cell scores with n > 0; its band = 1.96 sqrt(sum p(1-p)/n) / K (`panel_bands.py`). Match-weighted = all panel matches pooled. Holdout discipline: only matches.csv rows are read (development rows for the development cells, both halves for the pooled cells, exactly as B2e section 3 did); no holdout standings file was opened.

Held deck ids under this name (all records in the window, any opponent): `dragonair-mega-rayquaza-ex-b4` [(no label)]: 1696.

Panel labels: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

## Dragonair Mega Rayquaza ex

Cell format: W-L-T, n, score %, +/- 95% band (points). DL = double losses excluded.

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 42-15-1 (DL 4) | 58 | 73.3 | 11.4 | 76-43-1 (DL 5) | 120 | 63.7 | 8.6 |
| altaria | 39-44-3 (DL 2) | 86 | 47.1 | 10.5 | 82-83-8 (DL 3) | 173 | 49.7 | 7.5 |
| sceptile | 20-25-5 (DL 1) | 50 | 45.0 | 13.8 | 38-51-5 (DL 2) | 94 | 43.1 | 10.0 |
| vespiquen | 21-13-2 | 36 | 61.1 | 15.9 | 33-28-3 (DL 1) | 64 | 53.9 | 12.2 |
| suicune | 9-17-2 (DL 1) | 28 | 35.7 | 17.7 | 20-30-4 (DL 1) | 54 | 40.7 | 13.1 |
| hydreigon | 7-13-0 | 20 | 35.0 | 20.9 | 20-30-0 | 50 | 40.0 | 13.6 |
| weezing | 3-12-0 | 15 | 20.0 | 20.2 | 10-18-0 (DL 1) | 28 | 35.7 | 17.7 |
| blaziken | 4-4-0 | 8 | 50.0 | 34.6 | 10-13-0 (DL 1) | 23 | 43.5 | 20.3 |
| **Equal-weight average** | 8 opp. | | **45.9** | 6.9 | 8 opp. | | **46.3** | 4.8 |
| Match-weighted | 145-143-13 (DL 8) | 301 | 50.3 | 5.6 | 289-296-21 (DL 14) | 606 | 49.4 | 4.0 |

### The intervals in one place

| Data set | Equal-weight % | +/- | Interval | Opponents with data | Matches vs panel | Thinnest cell n | Records in window (any opponent) | Mirror records set aside |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| development | 45.9 | 6.9 | 39.0 to 52.8 | 8 of 8 | 301 | 8 | 857 (scored 818, DL 19, bye 20) | 23 |
| pooled | 46.3 | 4.8 | 41.5 to 51.1 | 8 of 8 | 606 | 23 | 1696 (scored 1610, DL 38, bye 48) | 37 |

### Notes

- Pooled cells under 20 matches (bands of 20+ points): none. A cell at exactly 0% or 100% shows a +/-0.0 band and contributes nothing to the equal-weight band, which then understates the real uncertainty.
- Pooled (both halves) is the reference figure the B2e README uses for its veto rule; the development-half figure is reported beside it. These are descriptive cells, not a test: the holdout half was spent on Sept 25.
- The archetype's window rank by development matches is 6 (census.csv), so its cells are among the thickest of the census lists; none of the eight panel cells is thin.
- Split consistency check (matches.csv split column against split.json): {'hold_ok': 16089, 'dev_ok': 14127}.
- This file reports; it decides nothing and changes no rule.
