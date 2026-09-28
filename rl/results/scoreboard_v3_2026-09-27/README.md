# Scoreboard v3: the frozen table on the repaired engine (Sept 27)

Dustin, Sept 27: "k3 and kp3 on all 45 cells get re-run on the repaired build and become the new frozen table; the Sept 23 and Sept 25 tables stay as history with their hashes … every future reading should be against baselines on the same engine as the candidate, with no exceptions."

## In plain words

- **This is the yardstick from now on:** 45 cells.
  - The 28 table cells, plus Rayquaza's and Altaria/Greninja's 17.
  - Played by k3 and kp3 on the repaired engine, which is official from Sept 27 (main-83e17ae, `rl/engine-2026-09-27/`).
- **The repairs barely move it.** On the 28 cells, kp3's real error goes from 8.4 to 8.7 and k3's from 10.8 to 10.9 (development half). The repairs change few games, mostly in Suicune's, Weezing's and Altaria's cells.
- **The 17 new cells are where both pilots miss badly** (about 21-23): Rayquaza's discard-cost attacks and Rainbow Cave, and Altaria/Greninja's gap (`../gauntlet_runs_2026-09-26/`). kpf's reading is read against this table.

| Limitless half | Pilot | frozen 28 | 27 decision set | new 17 | all 45 | favourite right (45) |
|---|---|---:|---:|---:|---:|---:|
| development | k3 | 10.9 | 11.1 | 20.5 | 15.3 | 30/45 |
| development | kp3 | 8.7 | 8.9 | 22.6 | 15.5 | 28/45 |
| pooled | k3 | 11.7 | 11.7 | 16.2 | 13.6 | 33/45 |
| pooled | kp3 | 9.6 | 9.7 | 18.9 | 13.9 | 29/45 |

Real error is score.py's τ̂ in points; the target is 5.5. The development half is the scoreboard's half, and the pooled half is shown beside it. The 27-cell decision set drops Altaria v Sceptile (quarantined for drift).

## Where the games come from

- **Source:** kpf's reading runs at 9bffbda (`../kpf_2026-09-26/reading/table_{k3,kp3}.jsonl`, `new17_{k3,kp3}.jsonl`).
  - 9bffbda's `engine/` is identical to the official release's source (the merge 83e17ae).
  - The official build replays these table games (`../engine_switch_2026-09-26/pin_identity.txt`).
- **Seeds:** the table's 72,000,000 + p × 10,000 + i, and the gauntlet's 21,108,000,000 + p × 10,000 + i (pairings 8-24), i < 500.
- **Limitless cells:** scoreboard v2's development cells for the 28 (`../scoreboard_v2_2026-09-25/limitless_v2_dev.json`), and the gauntlet's cells for the 17 (`../gauntlet_runs_2026-09-26/gauntlet_cells.csv`).
- **Hashes:** the input files' sha256 are in `frozen_summary.json`.
- **Per cell:** `frozen_cells.csv`.
- **Per event (since Sept 28):** `limitless_45_dev_events.json` (from `build_events45.py`) has the 45 development cells for each of 59 tournament events. It sums exactly to the cells above, which is checked.
  - `score45.py` passes it by default, so every 45-cell reading prints the event-resampled interval beside the match-level one (Fable and Astra, Sept 28: a standing column).
  - The sensitivity on the readings already made (`events_sensitivity.txt`; kpg3, koa3, kog3, kpr3 and kpf3 against kp3) changes no conclusion. Every by-event interval is within about 0.2 points of its match-level one, and every ΔMSE interval below zero stays below zero. So treating matches as independent hasn't been flattering the readings.
- **History, unchanged:** the Sept 23 table (`../limitless_check_2026-09-23.md`), the Sept 25 references (`../per_game_table_2026-09-25/k3_500.jsonl`, `../public_pricing_2026-09-25/kp3_500_*.jsonl`) and scoreboard v2 (`../scoreboard_v2_2026-09-25/`).
