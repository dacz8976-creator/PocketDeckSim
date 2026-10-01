Decision this informs: PLAN.md step 8c's gate before step 8, the trace load. These are step 8b's early-warning rows, played on the cloud's scratch build of R. Set by the Fable coordinator via Dustin, Oct 1 morning. The laptop's own 8b run tonight must equal these rows (its `sitting2_check.py cloud8b`).
- **Not played:** no table game, carrier game or identity replay.
- **Not changed:** no engine file.

Seeds: the plan's own, 23,100,000,000 + pairing × 10,000 + i, pairings 32-35, i < 40 (START_HERE's 23.1B row). These are the same deals the laptop's sitting 2 plays as 8b.

# Step 8b's early-warning rows, on the cloud's build of R

## In plain words

- **The rows are played: 960 games.**
  - 4 pairings × 40 deals × 2 bots (km3, k3) × 3 builds:
    - old: `rl/engine-2026-09-30`'s source, main d363ba8's `engine/`;
    - new: R at f8cfa9c, whose `engine/` is ab56bf4's, tree 38af8b0, the same tree as the laptop's candidate 5a18d31;
    - watch: R with both `instrument_scan.py` scripts, R's version.
  - Every program was built from `git archive` in a fresh target folder.
- **The checks pass:**
  - **Watch equals new** on every field new records: 160 of 160 games, for each bot.
  - **The pinned old `legality_scan`** (`rl/engine-2026-09-30/`, SHA256SUMS verified) gives the same rows as the old program built from source: 160 of 160 on every field, for each bot. That is the program the laptop runs as "old".
  - **No rule findings** on any of the 8 scan pages (nor on the pinned program's 2).
- **63 of the 320 deals change** between old and new: km3 32, k3 31.

  | pairing | km3 changed | k3 changed |
  |---|---|---|
  | 32 fire_victini v psychic_confuse | 9 | 8 |
  | 33 fire_heatmor v meowth_carefree | 13 | 13 |
  | 34 t-vespiquen v meowth_carefree | 10 | 8 |
  | 35 l-sharpedo v meowth_carefree | 0 | 2 |
- **The laptop's own checker passes both bots** (`sitting2_check.py touched` and `stepsum`, from main 38e1c566, run on these rows):
  - no changed game has every repair counter at 0;
  - reach: A in 22 games, B(b) / Chase Order in 80, B(a) unreached (it rests on its tests, as the plan says);
  - rows 13 and 22 (the off-gate discard counter in unchanged games): pairing 35, the Wild Swing control, is met in 15 games. **Pairing 34, Chase Order's discard, is NOT met:** the counter fired in none of its 62 unchanged games. It is a report line in `stepsum`, not a stop;
  - CONDITION 3: 1 game (km3, pairing 34, i = 35).
- **Every changed game is explained** (`tightened_rule.py`, R's, unchanged; `classify_8b.py`):
  - **50 on the board**: a reach counter fired at or before the first differing tick, in its turn or at the cause tick;
  - **13 lookahead only, both halves hold**: the same state, the same offered moves and a different choice, with no counter in that window. A probe run on R at that tick finds the repair's gate inside the bot's 3 plies (`coin_probe.rs` for repair B, `vs_probe.rs` for repair A);
  - **0 needing a judgment, 0 unexplained.**
  - The golden probes on the games explained on the board all find the gate on the table, and the 8 negative controls (unchanged games) find nothing.
- **The CONDITION 3 game** (km3 34 / 35) is one of the 13: a lookahead difference at tick 86, where `coin_probe` finds a queued coin-path choice offered after 2 of the mover's moves. So under the coordinator's Oct 1 ruling it is explained, and it is listed as a pin-gate item.
- **The share and the trace load for step 8:**
  - **Changed games that no exact counter explains: 13 of 320 deals (4.1%)**, km3 8 of 160 and k3 5 of 160. Each bot's share times its step 8 deals (km3 16,000, k3 8,000; 72,000 games = 24,000 deals × 3 builds) gives **about 1,050 such games in step 8** (975 with one share for both bots).
  - **Needing a hand trace or a judgment after the probes: 0 of 13, so an implied 0 for step 8.**
  - **The sample is small.** 0 of 13 doesn't rule out a few percent. By the rule of three, the share of no-counter games that need a hand trace could be up to about 3 in 13 at 95% confidence, which would be up to about 240 in step 8.
  - **8b's decks are not step 8's lists**, so the extrapolation is the plan's arithmetic, not a forecast of the carriers.
  - **The automated half has a cost** (timed here): a trace is about 0.8 s per game per engine with km3, and a probe about 2 s. Step 8 would have about 4,750 changed games to trace on both engines (63/320 of each bot's deals), roughly 2 hours on one core, and about 1,050 to probe on both probes, roughly 70 minutes on one core. Both split across cores.
- **For `trace_load.txt`** (the laptop's file; not written here):
  - The plan's own definition, "the share of changed games that no exact counter explains, multiplied by step 8's games", gives about 1,050. That is above 50, but every one of them is the automated check's (trace plus probe), and the plan's threshold of about 50 is about hand traces.
  - On this sample, the implied hand traces are 0.
  - Which number goes on the TRACE LOAD line is the coordinator's and Dustin's call.
  - The CLOUD8B lines can name this folder's new-build rows: `<this commit> km3 rl/results/engine_switch_rules_2026-10/early_warning_8b/8b_new_km3.jsonl`, and the same with k3. Their format passes `sitting2_check.py cloud8b` (checked against themselves: 160 of 160 deals, 17 fields, `a_file` and `b_file` left out).

## How the rows were made (`run_8b.sh`, output in `run_output.txt`)

- **The deck root is laid out as the laptop's repository will be** when sitting 2 plays 8b:
  - `decks/` from main 38e1c566;
  - the carrier lists from e0d149a;
  - `scratch_8b/` from R's blobs: `fire_victini.txt` and `psychic_confuse.txt` from `victory_star_repair_2026-09-30/smoke/`, `fire_heatmor.txt` and `meowth_carefree.txt` from `coin_prevention_repair_2026-09-30/smoke/`.
  - `pairs_8.tsv` and `seeds_8.txt` are written by the laptop's own `sitting2_check.py pairs8`, so pairings 32-35 have the laptop's names, paths and seeds.
- **Each scan:** `legality_scan --pairs pairs_8.tsv --root <root> --seed-base 23100000000 --pairings 32,33,34,35 --games 40 --bot <km3|k3> --games-out ...`.
  - The rows are `8b_<old|new|watch|pinned>_<bot>.jsonl`, and the scan pages `scan_page_*.txt`.
  - The programs' sha256s are in `run_output.txt`. Binaries built on another machine differ in bytes; the rows are what must match.
- **The traces** (`traces/`): `vs_trace.rs` (R's) built on each engine, for every changed game and a few unchanged ones for the controls.
  - Each trace's move fingerprint equals its scan row's, for all 63 changed games on both engines.
  - The tracer's seat rule (an even i puts the first-named deck in seat 0) matches all 320 scan rows.
- **The classification** (`classify_8b.py`, output in `classify_output.txt` and `summary.json`):
  - It is `tightened_rule.py`'s rule, as R's `first_diff.py` and `coin_lookahead.py` apply it, generalized to the four pairings, both bots and both repairs.
  - The reach counters are `sitting2_check.py`'s REACH.
  - For a lookahead difference, both probes run at the first differing tick. A coin probe that finds the queued choice only at the leaf (ply 3, in a mixed frame) would be "needs a judgment", as in `coin_lookahead.py`; none did.

## Files

- `README.md`: this note.
- `run_8b.sh`, `run_output.txt`: the builds and the scans.
- `pairs_8.tsv`, `seeds_8.txt`: written by `sitting2_check.py pairs8`, as the laptop's.
- `8b_old_*.jsonl`, `8b_new_*.jsonl`, `8b_watch_*.jsonl`, `8b_pinned_*.jsonl`: the rows (km3 and k3, 160 games each).
- `scan_page_*.txt`: the scan pages.
- `touched_8b_km3.txt`, `touched_8b_k3.txt`, `handoff_8b_km3.tsv`, `handoff_8b_k3.tsv`, `stepsum_8b.txt`: the laptop's checker on these rows.
- `classify_8b.py`, `classify_output.txt`, `summary.json`: the classification.
- `traces/`: the per-tick traces (old and new, every changed game; the controls' games).
