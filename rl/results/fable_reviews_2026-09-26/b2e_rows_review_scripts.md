# B2e rows, commit 8aa6ea3: review of the scripts and the run discipline (Fable, Sept 26, 2026)

**What was reviewed.** Commit 8aa6ea3 on main ("B2e rows: legality_scan --pairs/--seed-base patch ..."), ten files under
`rl/results/b2e_rows_2026-09-26/`. All ten are unchanged in the working tree (`git diff --stat HEAD` is empty; the only
untracked files are ko_audit, kt_carrier_census and diag-altaria-lucario outputs). Read against the specification,
`rl/results/b2e_card_check_2026-09-26/README.md` sections 4 and 5, the official tool `engine/examples/legality_scan.rs`
at 7fc6ccb (`git show`), the reference per-game files, `rl/results/engine_identity_2026-09-25/` and START_HERE's seed
table. Nothing was built or played (no cargo, no engine binary, no game); the one thing executed was `git apply` of the
patch onto a scratch copy of 7fc6ccb's file, in the session scratchpad.

**Lens:** the build script, the identity script, the run script and the reader; whether the run discipline holds.

**Verdict in one line.** No high finding. The scripts build from a clean archive of 7fc6ccb plus the one-file patch,
record the hashes the spec asks for, replay exactly the pairings and deal counts the spec names for both pilots
against the right reference files, refuse to start the rows without a PASS bound to the binary's sha256, keep every
seed inside sub-blocks 0 to 95 of the claimed block, run deck_check on the twelve files before the games, and read
the cells, panel averages, gaps, per-cell misses and the veto baseline the way section 5 defines them. Two medium
items: the scripts do not check (or even state in their own headers) that no training run is beside them, and the
folder and file names deviate from section 4 (declared in the folder's README). The rest is hygiene.

## Findings

### M1. No "never beside training" check, no thread or job cap (medium: missing step of the run discipline)

- Spec section 4, "Time": "Run it when the network training has finished, not beside it". The task's own rule tonight:
  a build from another job nearly triggered the OOM killer.
- `run_b2e_rows.sh` lines 1 to 8 (header) and line 49: no check for a training process and no statement of the rule;
  the scan runs under `nice -n 10` only, and legality_scan's rayon loop uses every core (`into_par_iter`, patch line
  152; 7fc6ccb line 502). `run_b2e_identity.sh` lines 25 to 26, 96 and 108: the same (8,000 games).
  `build_b2e_scan.sh` line 63: `nice -n 10 cargo build --release --locked --example legality_scan` with no job cap.
- The only mention is the folder README, line 15: "run in this order, in WSL, when the laptop is free".
- Fix: at the top of all three scripts, one gate that refuses when a training or build process is running, e.g.
  `if pgrep -f '<the training launcher's command line>' >/dev/null || pgrep -x cargo >/dev/null || pgrep -x rustc
  >/dev/null; then die "training or a build is running: B2e never runs beside it"; fi` (pattern to be taken from the
  actual launcher, `rl/runs/...`), plus the rule in each header. Cap the build with `-j 2` (or `CARGO_BUILD_JOBS=2`)
  and the scans with `RAYON_NUM_THREADS=$(( $(nproc) - 2 ))` so a queued job cannot take the whole laptop.

### M2. Folder and file names deviate from section 4 (medium: spec deviation, declared)

- Spec section 4, "Run folder and files": `rl/results/b2e_runs_<date>/` with `run_b2e.sh`, `identity.txt`,
  `b2e_k3_arch.{txt,jsonl}`, `b2e_kp3_arch.{txt,jsonl}`, `b2e_k3_dustin.{txt,jsonl}`, `b2e_kp3_dustin.{txt,jsonl}`,
  `timing.txt`, `READING.md`.
- Implementation: folder `rl/results/b2e_rows_2026-09-26/` (`D=` in all three scripts: build line 12, identity line
  30, rows line 11); one per-game file per pilot, `b2e_k3.jsonl` and `b2e_kp3.jsonl` (rows line 49 to 50; reader
  line 170 and gate line 82); three scripts instead of `run_b2e.sh`; `b2e_tables.md` instead of `READING.md`
  (reader line 450; README line 109 says READING.md is still to be written by whoever reads the run).
- Declared in the folder README lines 111 to 115 ("follows the task as given"). The block is recoverable from the
  pairing number (0 to 47 archetype lists, 48 to 95 Dustin's files), so nothing is lost.
- Fix: either (a) keep the names and have `READING.md` and the START_HERE seed row state the mapping to section 4's
  names, or (b) match the spec: run the scan twice per pilot with `--pairings 0,...,47` and `48,...,95` into the four
  files (rows line 49; the reader's `files` dict at line 170 and `check_rows` at line 172 then take four paths).
  (a) is enough; the spec is mine and the deviation is explicit.

### L1. Official hashes are recorded, not asserted (low)

- `build_b2e_scan.sh` lines 76 to 77 write whatever `sha256sum` says for `rl/engine-2026-09-25/deckgym` and
  `legality_scan` into `identity.txt`; nothing compares them with the spec's `f4d235e5...1034` and `d5c0a952...bfbb`
  (spec section 4 "Engine"; `rl/engine-2026-09-25/README.md` lines 11 to 12). `run_b2e_identity.sh` line 73 records
  the reference files' hashes but asserts nothing about them either.
- Today both files hash to the spec's values (checked here), so this is hygiene.
- Fix: `[ "$(sha256sum "$R/rl/engine-2026-09-25/deckgym" | cut -d' ' -f1)" = f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034 ] || die ...`
  and the same for `legality_scan` with `d5c0a9528e076299875ac603667f7076951de885ea8465f3be0d1089b5afbbfb`.

### L2. The --pairs replay uses the default seed base, so it cannot show --seed-base is honoured (low)

- `run_b2e_identity.sh` line 38 and 108: (b) runs `--pairs` with `--seed-base 72000000`, which equals the compiled-in
  `SEED_BASE` (7fc6ccb line 35). A patch that parsed the flag and then ignored it would still pass (b).
- What does cover it: guard (c) at line 90 (`--seed-base 72000001` must be refused through read_pairs' seed_first
  check, patch lines 95 to 98, so the parsed value does reach the row reader), and after the run `b2e_checks.py rows`
  line 234 checks every seed against `base + 10,000 x pairing + i` and the TSV's `seed_first`; the JSON `seed` is the
  value passed to `Game::new` (patch line 50; 7fc6ccb lines 373 and 379), so it is the seed used. The gap is only
  that a wrong base would be found after 3.4 hours of games rather than before them.
- Fix (optional, one minute of games, no new seeds): a probe TSV with pairing 0 = table pairing 1's decks
  (`decks/research/altaria.txt`, `decks/research/hydreigon.txt`) and seed_first 72,010,000, run with
  `--seed-base 72010000 --games 500`; its seeds are table pairing 1's deals, so its `moves` per deal must equal
  `ref_k3.jsonl`'s pairing-1 lines (a five-line Python check keyed on `i`).

### L3. Identity (a) does not look at the log: findings and per-pairing lines are not compared (low)

- `run_b2e_identity.sh` lines 96 to 103 compare the per-game JSON lines only. In default mode the JSON carries no
  findings (7fc6ccb lines 543 to 556); findings live in the log's last section. The official logs say "none" for all
  28 pairings under both pilots (`engine_identity_2026-09-25/k3_500.txt` line 46, `kp3_500.txt` line 46).
- The check code (`check_offered`, `check_state`) is untouched by the patch, and the engine crate is the same, so
  this is a completeness gap, not a likely failure.
- Fix: after each default replay, `python3 b2e_checks.py`-style: require the findings section of
  `identity_$bot.txt` to be exactly `  none`, and diff its four per-pairing lines against the same lines of the
  official log (`grep -F` on "altaria v blaziken", "altaria v suicune", "blaziken v sceptile", "hydreigon v sceptile").

### L4. The --pairs replay comparison would fail, not pass, on a game that carries `findings` (low, safe direction)

- Patch lines 176 to 182: in `--pairs` mode a game with findings gets a `findings` key. `b2e_checks.py same` with
  `--drop a_file,b_file` (identity line 114; same() lines 136 to 141) requires the dropped keys and compares every
  other key, so such a line would differ from the official line and the identity would FAIL although the games are
  identical. It cannot fire today (no findings on any table pairing, above), and a spurious FAIL blocks rather than
  passes.
- Fix: let `same --drop` treat `findings` as optional (drop it when present) and, in the identity script, check the
  summed findings against the log with `log_findings` instead; or a one-line comment in the script saying the check
  relies on the table's zero findings.

### L5. Inputs are compared to HEAD, not to a pinned commit (low)

- `build_b2e_scan.sh` line 31 (`git show "HEAD:$TSV"`) and line 40 (`git show "HEAD:$f"`): the pairings file and the
  six archetype lists must equal their version at whatever HEAD is when the build runs. A later commit that edits a
  list would be accepted silently. Traceable afterwards: `inputs_sha256.txt` goes into `identity.txt` (lines 80 to 81)
  and `inputs_source.txt` records the last commit touching each file (line 48), and `run_b2e_rows.sh` lines 29 to 33
  re-check the played copies against those hashes.
- Fix: pin the expected hashes (the six lists and the TSV as committed in 8aa6ea3's parent, 4924008 or earlier) in
  the build script, or assert `git log -1 --format=%h -- "$f"` equals the commit the spec was written at.

### L6. `--seed-base` without `--pairs` is accepted (low)

- Patch lines 117 to 123: `--pairs` requires `--seed-base`, but `--seed-base` alone runs the table's 28 pairings on
  a foreign base with no refusal. Spec: "Without either flag the program must behave as today", so this is allowed,
  and the `seed` field records the base used, so it is not silent. Still, such a file would look like a table file.
- Fix: `assert!(pairs_file.is_some() || arg(&args, "--seed-base").is_none(), "--seed-base is only for --pairs")`.

## Verified as correct (with the evidence)

- **Clean build tree.** `build_b2e_scan.sh` line 28 takes `git archive 7fc6ccb engine decks` into a fresh folder (line
  20 refuses an existing one), not the working tree. The card database is compiled in (`engine/src/database.rs` is
  generated code), so `engine/` alone is a complete build tree, the same way the official program and the kpr build
  (`kpr_mixed_rows_2026-09-26/build_kpr_scan.sh` line 14) were made. The six archetype lists and the TSV are copied
  from the working copy only after `cmp` against HEAD (lines 31, 40); the 14 files 7fc6ccb already has must equal the
  working copy's (line 38; they do: `git diff --stat 7fc6ccb HEAD` on them is empty). Line 54 checks the file being
  patched is byte for byte 7fc6ccb's; lines 55 to 58 refuse a patch touching any other file and a patch that does not
  apply. `--locked` (line 63) against 7fc6ccb's committed `Cargo.lock` (present at that commit).
- **The patch.** Applies cleanly to 7fc6ccb's file (`git apply --check` and apply in a scratch tree here: +104 -12,
  one file; the result equals `review/legality_scan_patched.rs` byte for byte, and `review/legality_scan_7fc6ccb.rs`
  equals `git show 7fc6ccb:engine/examples/legality_scan.rs`). Default path: `seed_base` falls back to `SEED_BASE`
  (line 118), the eight `NAMES` decks are loaded in the same order from the same `{dir}/{n}.txt` (line 130), the 28
  pairs are the same list in the same order (lines 131 to 132), `play_one` computes the same seed, seats, codes and
  players (lines 49 to 56), the JSON has the same keys and no `a_file`/`b_file`/`findings` when `row.files` is None
  (lines 168 to 182). `--pairs`: held file first, `a` = held_key, `b` = opponent, `first_seat = i % 2` through the
  same `play_one`, seed = base + 10,000 x pairing + i, `--pairings` still filters by the file's numbers, refuses
  `--decks` and requires `--seed-base` before anything is created or loaded, checks `seed_first` per row before that
  row's decks load. `HashSet` is already imported (7fc6ccb line 29). Not compiled here (the rules), and the commit
  message says so.
- **identity.txt.** First line is the built binary's sha256 (build line 72), then the patch's, the official
  `deckgym`'s and the official `legality_scan`'s (lines 75 to 77), the toolchain, and the sha256 of the TSV and all
  20 deck files as played (lines 80 to 83). The identity script (line 70) and the rows script (line 26) and the
  reader (line 85) all bind to that first-line hash.
- **Identity replay.** Pairings 0, 5, 13, 23 x 500 deals (spec's minimum), k3 and kp3 (identity lines 36 to 37, 92).
  k3 against `per_game_table_2026-09-25/k3_500.jsonl`; kp3 against both `public_pricing_2026-09-25/kp3_500_worst5.jsonl`
  (pairings 0, 2, 9, 13, 23) and `kp3_500_rest.jsonl` (the other 23), lines 41 to 42 and 78; the `subset` cut keeps
  exactly 2,000 games per pilot and checks `bot_a = bot_b = pilot` (b2e_checks.py lines 72 to 99). compare.py is the
  Sept 25 tool, on its nine fields including the move hash, and must print `RESULT: IDENTICAL` with 2,000 of 2,000
  and none on one side (lines 49 to 57). Stricter than the spec: byte-for-byte equality with the official 7fc6ccb
  scan's own lines (`engine_identity_2026-09-25/{k3,kp3}_500.jsonl`, which carry `chase_order`; the table references
  do not, checked here), so `hyper_ray`, `chase_order` and the absence of any added key are covered. Then the
  `--pairs` path on the same deals (lines 105 to 115) and the three refusals (lines 88 to 90). On any failure the
  script writes `IDENTITY FAIL: ...` and exits 1 (line 46); the PASS line carries the binary's hash (line 118).
- **The run cannot start on a mismatch.** `run_b2e_rows.sh` lines 21 to 36: the binary must exist, its hash must be
  identity.txt's first line, `identity_check.txt` must END in `IDENTITY PASS <that hash>:`, the repo's TSV must equal
  the played copy, the 21 played inputs must still hash as recorded and each hash line must appear in identity.txt,
  and no finished `b2e_<pilot>.jsonl` may exist. The reader repeats the PASS gate and requires `rows_check.txt` to
  name the same binary and carry `ROWS PASS` (read_b2e.py lines 81 to 95), then re-runs the rows check (line 172).
- **The rows.** 96 pairings x 500 deals, k3 then kp3 on the same deals, `--pairs <TSV> --seed-base 21106000000
  --games 500 --bot <pilot>` (rows lines 15 to 16, 47 to 52), each with its `.txt` log and a `timing.txt` line
  (wall seconds, cores, end time). `b2e_checks.py rows` then requires 96 x 500 lines per file, one per (pairing, i),
  every spec field plus `a_file`/`b_file`, a 16-hex-digit `moves`, seed = seed_first + i = base + 10,000p + i and not
  past `seed_last`, `first_seat = i % 2`, `a`/`b`/files as the TSV row, `bot_a = bot_b = pilot`, score consistent
  with `winner_seat` (1 if the winner's seat is the held deck's `first_seat`, 0.5 on -1; matches 7fc6ccb lines 445 to
  448), k3 and kp3 on the same (pairing, i, seed) set, and per-game findings summed = the log's section (lines 199
  to 297; the log format at 7fc6ccb lines 564 to 573 parses as `log_findings` expects).
- **Seeds.** TSV: 96 rows, seed_first = 21,106,000,000 + 10,000p for p = 0 to 95, seed_last = seed_first + 499,
  sub_block_end = seed_first + 9,999 (recomputed here: 0 bad rows; max seed used 21,106,950,499). Sub-blocks 96 to 99
  are never touched: the identity replays use the table's own 72,000,000 block, and the refusal tests play nothing.
  The block lies above every row of START_HERE's table (21,101,000,000 to 21,101,300,001 below, 22,000,000,000
  above); the folder README line 121 has the row to add to START_HERE when the run is recorded.
- **deck_check first.** `run_b2e_rows.sh` lines 39 to 42: the 12 distinct held files from the TSV (the six lists and
  Dustin's six), `python3 lib/deck_check.py files` on the played copies in the scratch tree, output to
  `deck_check.txt`, `die` on failure, before any game; the reader pastes it into `b2e_tables.md` (lines 439 to 447).
  deck_check finds its database from its own folder (`lib/deck_check.py` lines 28 to 32), so running it from the
  scratch tree is fine.
- **Nothing written outside the results folder except the scratch build tree.** Build: `$B` (outside the repo, by
  design as kpr's) and `$D/identity.txt`. Identity: cuts, compare outputs, guard output and the probe TSV in `$B`;
  `identity_check.txt`, `identity_*.jsonl/.txt`, `identity_pairs_*.jsonl/.txt`, `timing.txt` in `$D`. Rows:
  `deck_check.txt`, `rows_check.txt`, `b2e_*.jsonl/.txt`, `timing.txt` in `$D`. Reader: `b2e_tables.md`,
  `b2e_summary.json` in `$D`, no `__pycache__` (line 49). START_HERE is not edited (README line 117).
- **The reader.** Cell = mean of `first_deck_score` over the 500 deals x 100 = (wins + 0.5 x ties)/500, ties
  counted (lines 185 to 191, 246). Panel score = equal-weight mean of the eight cells, band 1.96 sqrt(sum p(1-p)/n)/8
  (lines 195 to 200). Gap = panel minus the Limitless equal-weight average, pooled and development, read from
  `panel_intervals.csv` and recomputed from `limitless_cells.csv`'s W-L-T-n with a 0.05 tolerance (lines 111 to
  148); Whimsicott's development gap uses its seven opponents (lines 141, 253, 257). Per-cell miss = sim minus
  pooled, "beyond" when |miss| > sqrt(band_L^2 + band_S^2) with band_S at 500 games (lines 272, 388); one-sided
  Limitless cells read as no information; bands over 15 marked wide; the known sceptile/vespiquen/altaria misses
  noted, not fixed (lines 64 to 68). Veto baseline |kp3 - L| per archetype with k3 beside it (lines 350 to 361). A2's
  bar on kp3, block A, against the pooled intervals, stated not applied (lines 330 to 347). RULE findings withhold
  the cell and every panel score that needs it (lines 175 to 176, 196, 203). `check_layout` (lines 151 to 159)
  verifies the TSV is section 4's order before anything is read. The development Whimsicott v blaziken row exists in
  the CSV with n = 0 (line 49), so the `None` path at line 120 is exercised, not a KeyError.
- **Hard-coding.** Absolute `R`, `D`, `B` paths in all three scripts (as `build_kpr_scan.sh` lines 7 to 8); the
  date is the folder's name; pilots k3/kp3 are the spec's; `BASE`/`GAMES` appear in the rows script (15 to 16), the
  reader (69) and the TSV, and the rows check ties all three together (line 234). Deck lists come only from the TSV.
  The reader's `DECKS`/`PANEL` tables are the section 2/3 mapping and are checked against the TSV. Nothing the spec
  parametrises is hard-coded elsewhere.
- **Inputs.** The TSV and the deck files checked are LF, no CR; the patch is LF; `read_pairs` trims fields and
  `str::lines` would strip a CR anyway.

## What is still open (not findings against the commit)

- The patch has not been compiled; the first compile is `build_b2e_scan.sh`, which is allowed only when the laptop
  is free (M1). A compile error would stop at step 1 with `build.txt`.
- `READING.md` for the run folder and the START_HERE seed row are to be written when the run is recorded (declared).
