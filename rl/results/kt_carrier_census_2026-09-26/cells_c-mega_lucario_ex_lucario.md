# Limitless cells: Mega Lucario ex Lucario against the eight panel decks

List: `decks/c-mega_lucario_ex_lucario.txt` (kt carrier census, Sept 26, 2026). Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` (30,216 match records), window 2026-08-26 to 2026-09-24, 63 development and 63 holdout events (split.json). Script: `cells_c-mega_lucario_ex_lucario.py`; machine-readable: `cells_c-mega_lucario_ex_lucario.csv`, `cells_c-mega_lucario_ex_lucario.json`. Counting rules are B2e's (`rl/results/b2e_card_check_2026-09-26/README.md` section 3, `cells.py`): the held side by exact deck_name, the panel side by archetype label; a tie is half a point and counts in n; double losses are excluded and shown as DL; byes never form a pair; every record is one unit (BO1 and BO3 alike); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points. Only matches.csv was read; no standings file. Holdout rows enter the pooled cells only.

**The lucario cell is a mirror.** The archetype under review is the panel's own lucario deck (deck_name "Mega Lucario ex Lucario" on both sides), and the rules exclude mirrors, so that cell has no games and the equal-weight average is over the other seven opponents. Mirror records set aside: development 96, pooled 212.

Cell format: W-L-T, n, score %, +/- 95% band. Equal-weight = unweighted mean of the cell scores (opponents with n > 0), band 1.96 sqrt(sum p(1-p)/n)/K (`panel_bands.py` formula). Match-weighted = all panel matches pooled. DL = double losses excluded.

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | mirror, excluded | 0 | | | mirror, excluded | 0 | | |
| altaria | 43-114-5 | 162 | 28.1 | 6.9 | 90-234-11 | 335 | 28.5 | 4.8 |
| sceptile | 44-68-2 | 114 | 39.5 | 9.0 | 86-146-5 | 237 | 37.3 | 6.2 |
| vespiquen | 73-31-3 | 107 | 69.6 | 8.7 | 141-58-7 | 206 | 70.1 | 6.2 |
| suicune | 50-34-2 | 86 | 59.3 | 10.4 | 101-74-3 | 178 | 57.6 | 7.3 |
| hydreigon | 19-34-2 | 55 | 36.4 | 12.7 | 69-83-6 | 158 | 45.6 | 7.8 |
| weezing | 46-28-4 | 78 | 61.5 | 10.8 | 74-56-6 | 136 | 56.6 | 8.3 |
| blaziken | 35-24-0 | 59 | 59.3 | 12.5 | 78-63-3 | 144 | 55.2 | 8.1 |
| **Equal-weight average** | 7 opp. | | **50.5** | 3.9 | 7 opp. | | **50.1** | 2.7 |
| Match-weighted | 310-333-18 (DL 33) | 661 | 48.3 | 3.8 | 639-714-41 (DL 56) | 1394 | 47.3 | 2.6 |

## Identification

Held side identified by exact deck_name. Deck ids and labels found under that name (all records in the window, any opponent):

| deck_id [label] | records |
|---|---:|
| `mega-lucario-ex-b3-lucario-a2` [lucario] | 4742 |
| `mega-lucario-ex-lucario-b3` [(no label)] | 39 |

Panel opponents by archetype label; each label maps to exactly one deck_name: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon, sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur, hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.

## Totals per data set (all opponents, any status)

| data set | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | mirror records set aside | thinnest non-mirror cell n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 2243 | 2231 | 12 | 2044 | 105 | 94 | 661 | 96 | 55 |
| pooled | 4781 | 4742 | 39 | 4415 | 194 | 172 | 1394 | 212 | 136 |

## Notes

- These cells are descriptive baselines, not a test: the holdout half was spent on Sept 25 (B2e README section 3, "How to read these cells"). Pooled has twice the matches and is the reference figure; development is reported beside it.
- A cell at exactly 0% or 100% shows a +/-0.0 band; read it as no information, not as certain.
- BO1-only figures are in the CSV for readers who want single-game units.
- Split consistency check (matches.csv split column against split.json): {'hold_ok': 16089, 'dev_ok': 14127}.
