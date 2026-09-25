Decision this informs: the default pilot (k3, b3n1 or kp3). b3n1's gains in Hydreigon's seven matchups come from Hydreigon being piloted better, not from its opponents being piloted worse. The laptop's paired reading of these per-game files (ec0f89b on main: not adopted, on two narrow vetoes) can take that as settled. Engine commit e18ab4b (legality_scan with per-game output and per-seat bots).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, pairings in alphabetical order, even i = first-named deck in seat 0.

# Per-game tables (item 1), Sept 25

## k3 reproduces the laptop's table exactly

`k3_500.txt` matches the laptop's k3 table (`rl/results/option_b_table_2026-09-24.txt` on main, laptop build 02d9a9b) in all 28 cells. The score and the count of distinct games are identical in every cell. No game broke a rule anywhere in this folder: the scan checks every offered move and resulting state against RULES_FOR_AGENTS.md.

The census (`../unpriced_census_2026-09-25`) replays the first 200 deals of every pairing, and its games match these k3 games move for move: 5,600 of 5,600 fingerprints.

## b3n1 on the whole table

Paired with k3 on the same 500 deals per pairing (`analyze_tables.py --base k3_500.jsonl --other b3n1_500.jsonl`):

- **Against the Sept 23 Limitless table**, over all 28 cells: mean |miss| 9.66 → 8.30, mean squared miss 159.3 → 111.0. The laptop's reading uses the pre-set rule on 27 cells. It finds real error 11.5 → 9.2 and ΔMSE −46.8 (95% −84.7 to −7.5), but two vetoes fire narrowly (Altaria v Hydreigon, and the Vespiquen deck gap), so b3n1 is not adopted.
- **The biggest changes are all Hydreigon's:**
  - Hydreigon v Lucario +12.2, v Sceptile +16.8, v Suicune +6.0, v Vespiquen +11.8, v Weezing +15.8.
  - From the other side, Altaria v Hydreigon −7.6 and Blaziken v Hydreigon −12.4.
  - Also Blaziken v Sceptile +9.5, Altaria v Suicune +9.6, Suicune v Vespiquen −7.8.
- Per cell, with 95% ranges and each bot's miss: run `analyze_tables.py` as above.

## Hydreigon's seven cells under four pilotings

Hydreigon's score. Every row is on the same 500 deals per cell, and the changes are paired with k3 v k3 (`mixed_rows.py`).

| cell | k3 v k3 | b3n1 v b3n1 | b3n1 Hydreigon v k3 opponent | k3 Hydreigon v b3n1 opponent |
|---|---:|---:|---:|---:|
| v Altaria | 42.2 | 49.8 (+7.6) | 57.0 (+14.8 ± 5.2) | 40.6 (−1.6 ± 4.3) |
| v Blaziken | 35.5 | 47.9 (+12.4) | 55.5 (+20.0 ± 4.3) | 27.7 (−7.8 ± 4.2) |
| v Lucario | 30.6 | 42.8 (+12.2) | 43.6 (+13.0 ± 4.0) | 29.6 (−1.0 ± 4.1) |
| v Sceptile | 27.8 | 44.6 (+16.8) | 46.6 (+18.8 ± 4.3) | 27.0 (−0.8 ± 2.7) |
| v Suicune | 38.8 | 44.8 (+6.0) | 47.0 (+8.2 ± 5.0) | 36.2 (−2.6 ± 3.7) |
| v Vespiquen | 30.8 | 42.6 (+11.8) | 42.4 (+11.6 ± 5.0) | 27.0 (−3.8 ± 4.3) |
| v Weezing | 36.8 | 52.6 (+15.8) | 55.6 (+18.8 ± 4.7) | 32.4 (−4.4 ± 4.1) |
| **all 7 (3,500 deals)** | **34.6** | **46.4 (+11.8 ± 2.0)** | **49.7 (+15.0 ± 1.8)** | **31.5 (−3.1 ± 1.5)** |

What this shows:

- **Hydreigon plays better; its opponents don't play worse.**
  - Switching only Hydreigon's pilot to b3n1 is worth +15.0 points.
  - Switching only the opponent's pilot to b3n1 costs Hydreigon 3.1. That is, b3n1 opponents are slightly better against a k3 Hydreigon, never worse.
  - With both on b3n1, the two partly cancel (+11.8).
- **Why:** the option B attribution (`../option_b_attribution_2026-09-24.md`) and the census (`../unpriced_census_2026-09-25`) point the same way. Hydreigon's list has Darkness Claw and Copycat, which k3 scores as doing nothing and b3n1 prices through its sampled worlds.
- **The Altaria v Hydreigon veto is Hydreigon's gain showing up in Altaria's cell.** With b3n1 on Altaria's side only, Altaria does slightly better (Hydreigon −1.6). With b3n1 on Hydreigon's side only, Hydreigon gains 14.8. Limitless has Altaria at 57.0. k3 already sat there (57.8), because k3 underrates both decks. So the veto doesn't say b3n1 plays Altaria badly.

## Files

- `k3_500.{txt,jsonl}` and `b3n1_500.{txt,jsonl}`: the whole table for each bot, one JSON line per game. Each line has the pairing, deal, seed, seats, bots, winner seat (−1 = tie), points, turns, the first-named deck's score, a move fingerprint, and Hyper Ray counts.
- `mixed_hyd-{b3n1,k3}_{first,second}.{txt,jsonl}`: the mixed rows. The file name says which bot pilots Hydreigon. "first" = pairings 13–17, where Hydreigon is the first-named deck. "second" = pairings 1 and 7, where it is second-named.
- `run_item1.sh`: the commands. `timing.txt`: wall times. `analyze_tables.py` and `mixed_rows.py`: the readouts above.
