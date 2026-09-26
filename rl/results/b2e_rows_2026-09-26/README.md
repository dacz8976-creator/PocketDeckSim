# B2e rows: the scan extension, the run and the reading (prepared Sept 26, 2026; nothing built or played yet)

**Specification:** `../b2e_card_check_2026-09-26/README.md`, section 4 (the run) and section 5 (the reading), with its
`b2e_pairings.tsv`. This folder holds the tools to carry it out. When this was written the laptop was busy (an Altaria
training run and a cargo test), so **nothing here has been compiled or run against the engine yet**. The Python checks
were dry-run on made-up files and on the real reference files (see "Checks" below).

## What

- Six tournament archetype lists and Dustin's six versions of them, each against the eight panel decks: 96 pairings.
- 500 deals per pairing, first with k3 on both sides, then with kp3 on both sides, on the same deals. No mixed rows, never the jev bot.
- Seeds: 21,106,000,000 + 10,000 × pairing + i, for i = 0 to 499. Even i puts the held deck in seat 0, odd i puts the panel deck in seat 0 (the table's convention).
- The result is a baseline, not a decision: how close the simulator gets on decks it was never checked against.

## How (run in this order, in WSL, when the laptop is free)

1. **`bash build_b2e_scan.sh`**: builds the scan program in a scratch folder, `/home/dacz8976/engine-b2e-7fc6ccb`.
   - Takes `git archive 7fc6ccb engine decks` (the official engine's commit) and applies `legality_scan_pairs.patch`.
   - Builds with `nice -n 10 cargo build --release --locked --example legality_scan`, copies the program to `legality_scan_b2e_7fc6ccb`, and writes `identity.txt`.
   - `identity.txt` holds the program's sha256 on its first line, then the patch's hash, the official `deckgym` hash, and the hash of every deck file played.
   - It also copies in the pairings file and the six archetype lists, which 7fc6ccb doesn't have.
   - It stops loudly if the scratch folder already exists, if the patch touches any file except `engine/examples/legality_scan.rs`, or if the patch doesn't apply.
   - It also stops if a deck file differs from its committed version, or if the working copy's panel, Dustin or brew-08 files differ from 7fc6ccb's. (Checked Sept 26: all 14 of those files are identical to 7fc6ccb's.)
2. **`bash run_b2e_identity.sh`**: the identity check, on table pairings 0, 5, 13 and 23 × 500 deals, for k3 and for kp3. It plays 8,000 games in all: about 8 minutes per pilot at cloud speed, more on the laptop.
   - **(a) Default flags** (4,000 games). Each game is compared with the reference files, `../per_game_table_2026-09-25/k3_500.jsonl` and `../public_pricing_2026-09-25/kp3_500_*.jsonl`, by `../engine_identity_2026-09-25/compare.py`. Every field must match: decks, seed, first seat, the hash of every move, winner, points, turns and score. This is the check the specification asks for.
     - Given the whole 14,000-game reference, compare.py prints NOT IDENTICAL for any subset, because the other games show up as "only in reference". So each reference is first cut to exactly these 2,000 games per pilot, and compare.py must then say IDENTICAL.
     - Stricter, at no extra games: every line must also be **byte for byte** the line the official, unpatched 7fc6ccb scan wrote for the same deal (`../engine_identity_2026-09-25/{k3,kp3}_500.jsonl`, from legality_scan `d5c0a952…`). compare.py looks at nine fields only, so this also covers `hyper_ray`, `chase_order` and the absence of any added key ("without either flag the program must behave as today"). The table references can't serve here: they were written before `chase_order` existed.
   - **(b) `--pairs` mode** on the same deals (4,000 games), the code path that plays every B2e game. A pairings file lists the same four table pairings with their `decks/research` files (`b2e_checks.py table_tsv`), and the scan runs it with `--seed-base 72000000`. It must replay the same games: compare.py IDENTICAL against the table references, and equal to the official scan's lines once `a_file` and `b_file` are removed. These are the table's own deals, so no new seeds are used.
   - **(c) The `--pairs` guards.** The scan must refuse `--pairs` without `--seed-base`, `--pairs` with `--decks`, and a `seed_first` that doesn't match `--seed-base`, before playing anything.
   - The last line of `identity_check.txt` is either `IDENTITY PASS <program sha256>: ...` or `IDENTITY FAIL: <why>`. On a FAIL the script exits 1. The file also records the sha256 of every reference file used.
3. **`bash run_b2e_rows.sh`**: runs only if `identity_check.txt` ends in the PASS line for this exact program, and only if the scratch copies it will play (the pairings file and its 20 deck files) still have the hashes `identity.txt` recorded at build time. It will not overwrite a finished run.
   - Runs `lib/deck_check.py files` on the twelve held files as played (`deck_check.txt`).
   - Then plays all 96 rows, k3 first, then kp3: `--pairs b2e_pairings.tsv --seed-base 21106000000 --games 500`.
   - Output: `b2e_k3.jsonl` and `b2e_kp3.jsonl` (one line per game), `.txt` logs, and `timing.txt`.
   - Then runs the rows check (`rows_check.txt`, below).
   - Time: about 1.7 hours per pilot at cloud speed, and more on the laptop.
4. **`python3 read_b2e.py`**: the section-5 reading. It writes `b2e_tables.md` and `b2e_summary.json`.

## The patch (`legality_scan_pairs.patch`, against `engine/examples/legality_scan.rs` at 7fc6ccb)

**New flags.** It adds three flags. Without `--pairs` and `--seed-base`, the program runs exactly as before.
- **`--pairs <tsv>`** plays exactly the rows of the pairings file, each row with its own two deck files, instead of the table's 28 pairings.
  - Each row plays `held_file` (the first-named deck; output `a` = `held_key`) against `panel_file` (the second-named deck; `b` = `opponent`).
  - Seats follow the table's convention, unchanged: `first_seat` = 0 for even i and 1 for odd i.
  - `--pairings` still filters, now by the file's pairing numbers.
  - With `--pairs`, the program refuses `--decks` and requires `--seed-base`, so B2e can never fall back onto the table's 72,000,000 seeds by accident.
  - If the file has a `seed_first` column, every row must equal base + 10,000 × pairing, or the program stops.
- **`--seed-base <n>`** replaces 72,000,000: seed = base + 10,000 × pairing + i.
- **`--root <dir>`** (only used with `--pairs`; default `..`) says how the file's deck paths are found.
  - The paths in `b2e_pairings.tsv` are relative to the repo root. The scan runs from the `engine/` folder as it does today, so `..` is the root of whichever tree it runs in. An absolute path is used as it is.
  - The scripts run it in the scratch tree, so the decks read are the copies checked at build time, not files another session could edit mid-run.

**Per-game lines.** With `--pairs`, each `--games-out` line has today's fields (`pairing`, `a`, `b`, `i`, `seed`, `bot_a`, `bot_b`, `first_seat`, `winner_seat`, `points`, `turns`, `first_deck_score`, `moves`, plus `hyper_ray`/`chase_order` when present). It also has:
- `a_file` and `b_file`: the two deck paths, as the file gives them;
- `findings`: the codes and counts of that game's rule findings, only for a game that has any. Section 4 asks for findings per pairing, and the log only prints them summed over the whole run.

**Why the default run is unchanged.** The patch removes 12 lines. Each is replaced by code that computes the same thing when no new flag is given:
- `fn play_one(decks: &[Deck; 8], pairing, i, ...)` becomes `play_one(lineup, pairing, (a, b), i, ...)`.
  - The deck pair `(a, b) = pairs[pairing]`, which play_one used to look up, is now passed in by the caller. In the default run the caller builds `rows` from the same `pairs` list, in the same order (`pairs.into_iter().enumerate()`), so each pairing gets the same pair.
- `let seed = SEED_BASE + pairing * 10_000 + i` becomes `lineup.seed_base + ...`. The default run sets `seed_base` to `SEED_BASE` when there is no `--seed-base`.
- `create_players(decks[d0].clone(), decks[d1].clone(), codes)` becomes `lineup.decks[d0/d1]`.
  - In the default run, `lineup.decks` holds the eight `NAMES` decks, loaded from `{dir}/{n}.txt` in the same order, so each index is the same deck.
  - The array `[Deck; 8]` became a `Vec<Deck>`: the same values in a different container.
- `NAMES[d0], NAMES[d1]` in the finding examples become `lineup.names[..]`, which holds the same eight strings in the same order.
- The deck loading and `pairs` lines move into the `None` arm of `match &pairs_file`, unchanged apart from the container. They still run after the games-out file is created, as before.
- `for (p, (a, b)) in pairs.iter().enumerate()` becomes `for row in &rows`, with the same p, a and b in the same order. The `--pairings` filter, `play_one`'s arguments, the scores and the counters are unchanged.
- The two `NAMES[*a], NAMES[*b]` in the per-pairing print line and in the JSON line become `lineup.names[a], lineup.names[b]`. They are the same strings, and the `{:>9}` padding pads a `String` the same way it pads a `&str`.

Everything the patch adds on top runs only with `--pairs` (the extra JSON fields, the extra log line, the TSV reader and the checks) or only reads a flag. Nothing in the game loop, the checks, the fingerprint or the per-game result changed.

This argument is checked in practice by step 2 before any B2e game is played: 4,000 default-flag games, move hash included, and every line byte for byte the official scan's. Step 2 also replays the same deals through `--pairs`. The patch has not been compiled yet; the first compile is step 1.

## The checks

- **Build:** the patch touches one file and applies to 7fc6ccb's copy; a second apply fails, and the patched file equals the one the patch was written from (checked Sept 26). The build uses `--locked` against 7fc6ccb's Cargo.lock. The deck files are checked against git (above), and their hashes go in `identity.txt`.
- **Identity:** before any B2e game (step 2). Default flags: 4,000 games, field by field including the move hash, and byte for byte the official scan's lines. `--pairs` mode: the same 4,000 deals replayed. The three `--pairs` refusals are also tested. The rows script and the reader both refuse to run without the PASS line for this program's sha256.
- **Rows** (`b2e_checks.py rows`, written to `rows_check.txt`; the reader runs it again):
  - Each file has exactly 96 × 500 lines, one per (pairing, i).
  - Every line has every field the specification names, plus `a_file` and `b_file`, and `moves` is a 16-hex-digit hash.
  - Every seed = `seed_first` + i = 21,106,000,000 + 10,000 × pairing + i, and none is past `seed_last`.
  - `first_seat` = i mod 2.
  - `a`, `b`, `a_file` and `b_file` match the TSV row, and `bot_a` = `bot_b` = the pilot.
  - Each score agrees with its winner.
  - k3 and kp3 are on the same (pairing, i, seed) set.
  - The per-game findings add up to the log's findings section.
  - It prints RULE and CHECK findings per pairing. Its last line is `ROWS PASS ...` or `ROWS FAIL ...`.
- **Dry runs done here (Python only; no games):**
  - On made-up 96 × 500 files: a clean set passes. A set with one wrong seed fails and the reader refuses. A set with a RULE finding in one pairing passes the rows check, and the reader withholds that cell and that deck's kp3 panel score.
  - A missing PASS line makes the reader refuse.
  - On the real references: the cut of `k3_500.jsonl` and of `kp3_500_*` to pairings 0, 5, 13 and 23 gives exactly 2,000 games each, with the right pilot. compare.py on such a cut prints the three lines the identity script looks for.
  - All three shell scripts pass `bash -n`.

## What is read (`read_b2e.py`; descriptive only)

- **Cell score:** the held deck's (wins + ½ ties)/500 × 100, with its ties counted. Beside it, the Limitless pooled and development cells, recomputed from `limitless_cells.csv` (W-L-T-n) and checked against that file's rounded columns.
- **Per-cell miss** = sim − Limitless pooled. "Beyond the band" when |miss| > sqrt(band_L² + band_S²), with band_S the simulator's 95% band at 500 games.
  - A Limitless cell at 0% or 100% is read as "no information".
  - Bands over 15 points are marked "wide".
  - The panel's known sceptile, vespiquen and altaria errors are noted, not fixed.
- **Panel score:** the equal-weight mean of the eight cells, under k3 and under kp3, for the archetype list and for Dustin's file.
- **Gap** = panel score − the Limitless equal-weight average. The pooled average is the reference, with the development one beside it. Whimsicott's development gap uses the same seven opponents as its development average (no blaziken).
- **List difference** = the archetype list's panel score − Dustin's file's, per pilot.
- **kp3 − k3**, paired by deal.
- **A2's bar line:** kp3 on both sides, the six archetype lists, each panel score against its pooled interval from README 3.7 (`panel_intervals.csv`). It reports how many are inside. It does not lift or apply the screen's hold.
- **The veto baseline:** |kp3 − L| per archetype (k3's beside it).
- **Legality findings per pairing.** A pairing with a RULE finding is withheld under that pilot until it is explained, and so is every panel score that needs that pairing.
  - The scan's own findings sections (with the example games it keeps) are pasted from `b2e_k3.txt` and `b2e_kp3.txt`, so each CHECK can be listed with its example, as section 4 asks. Naming the card that may allow it is left to whoever writes `READING.md`.

`READING.md` (section 4 of the spec) is still to be written by whoever reads the run, from `b2e_tables.md`, with `deck_check.txt` pasted in.

## Where this differs from the specification (for the reviewer)

- **Folder and file names.** The spec names the folder `rl/results/b2e_runs_<date>/`, with four per-game files split by block (`b2e_k3_arch`, `b2e_k3_dustin`, `b2e_kp3_arch`, `b2e_kp3_dustin`). This folder follows the task as given: one file per pilot, `b2e_k3.jsonl` and `b2e_kp3.jsonl`. The block is readable from the pairing number (0–47 archetype lists, 48–95 Dustin's files).
- **`run_b2e.sh`** is split into three scripts: build, identity and rows.
- **Extra fields and flag.** The per-game `findings` field and the `--root` flag are small additions the spec doesn't name.

## Seed block (one row for START_HERE's seed table when the run is recorded; not added there)

| Seeds | Used by |
|---|---|
| 21,106,000,000 – 21,106,999,999 | B2e, held-out archetypes against the panel (Sept 26): seed 21,106,000,000 + pairing × 10,000 + i, pairings 0–95, i < 500, k3 and kp3 on the same deals (used up to 21,106,950,499); 21,106,999,000–21,106,999,001: the six 2-game smokes; sub-blocks 96–98 spare |

## Files

| File | What it is |
|---|---|
| `legality_scan_pairs.patch` | The change to `engine/examples/legality_scan.rs` at 7fc6ccb (+104 −12 lines). |
| `build_b2e_scan.sh` | Step 1: scratch build, writes `identity.txt`. |
| `run_b2e_identity.sh` | Step 2: default-flag and `--pairs` replays, writes `identity_check.txt`, `identity_{k3,kp3}.{jsonl,txt}`, `identity_pairs_{k3,kp3}.{jsonl,txt}`. |
| `run_b2e_rows.sh` | Step 3: `deck_check.txt`, `b2e_{k3,kp3}.{jsonl,txt}`, `timing.txt`, `rows_check.txt`. |
| `b2e_checks.py` | The subset, same-lines, table_tsv and rows checks the scripts and the reader use. |
| `read_b2e.py` | Step 4: writes `b2e_tables.md` and `b2e_summary.json`. |
| `review/` | The Sept 26 review: `check_patch.sh` extracts 7fc6ccb's `legality_scan.rs` (`legality_scan_7fc6ccb.rs`) and checks the patch applies (`legality_scan_patched.rs` is the result), with no build. |

## Review (Sept 26, before any build)

- **The patch** applies cleanly to 7fc6ccb's file, and a second apply fails. Every changed hunk was walked; the default path computes the same decks, pairs, seeds, seats, players, names and JSON as before.
- **The inputs:** all 14 panel, Dustin and brew-08 files equal 7fc6ccb's. The six archetype lists and the pairings file equal HEAD. `engine/Cargo.lock` is committed at 7fc6ccb, so `--locked` works.
- **Changed by the review:**
  - The identity check gained the byte-for-byte comparison, the `--pairs` replay and the guard tests (step 2 above).
  - The rows check now requires every field.
  - The rows script re-checks the played copies' hashes.
  - The reader pastes the scan's findings examples.
- **Tested with Python only, no games:**
  - The whole script flow ran against a stand-in program in the session scratchpad, not here: identity FAILs on one changed default line and on one changed `--pairs` line, then PASSes. The rows script refuses before a PASS, after a FAIL, on a changed deck copy and on an existing result, and the reader reads a clean run.
  - `same` fails the table references against the official output, as it should, because of `chase_order`.
