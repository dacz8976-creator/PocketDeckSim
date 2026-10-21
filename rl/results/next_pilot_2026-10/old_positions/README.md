# ky3 phase 1: the old positions, exported (the laptop, Oct 15; review item M3)

These are the combined run's and the development run's decision states, as pg_pos positions, for the cases in `EXPECTED.md`.
Each position is the first deck-side decision of the case's turn.

## How they were made (`m3_driver.sh`; log in `run_log.txt`)
- **The requests:** 25 cases (`cases.tsv`), mapped to their game keys and to the turn's first decision. Every case's turn matches its row
  in `strength_2026-10-08_kx3_combined/skip_exact/skip_turns.tsv`.
  - 17 come from the combined run, the candidate arm (`requests_comb.tsv`).
  - 8 come from the development run, the frozen kx3 (`requests_dev.tsv`).
- **The builds:** `skip_replay.rs` with `--export` (sonnet/ky3-pilot d142d659), built on each run's own tree:
  - combined: 172cbe9c (engine tree 69a5a4419da2, skip_replay ff78a1e9ff7543a3);
  - frozen: d513e37b (engine tree 31dbd2e6e8ec, skip_replay db6d1be3e46efcb7).
  - Both manifests' deck files equal the repository's by sha256.
- **The replays:** 17 of 17 and 8 of 8 games replayed exactly (`check_*.jsonl`). 25 positions were written; no request was dropped at
  export (`dropped_export_*.tsv`).
- **The km3 check:** `skip_positions.py` with pg_pos built on main's engine (main 36f4dd62, engine tree 70652fff03af, pg_pos
  8e9f02481e4930e4). A position is kept when km3's first move equals the old engine's recorded km3 move in at least 7 of 12 seeds.

## Result: 22 kept (`kept.json`), 3 dropped (`dropped.tsv`)
- **Kept:**
  - every case in `EXPECTED.md` section A: F's six skips and the four "measure F first" cases;
  - all four section C negatives from these runs;
  - 8 of the 13 same-position turns;
  - both "reported" rows.
  - km3 agrees at 12 of 12 seeds except 06 v Hydreigon 1|1 t2 (9), 09 v Hydreigon 4|0 t2 (9) and draft A v Blaziken 0|0 t2 (10).
- **Dropped:** three same-position keep checks, each where km3 picks another setup move first:
  - 09 v Altaria 1|0 t4 (6 of 12);
  - 06 v Altaria 4|1 t2 (5 of 12; a split verdict anyway);
  - 06 v Blaziken 0|0 t3 (4 of 12).

## Not here
- deck 12 game 3 T4 and deck 13-A G5 T4 (hand-built; the review-fix job);
- the pause-game positions (already pg_pos).
