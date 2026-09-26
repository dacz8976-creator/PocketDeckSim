# B2e rows: the scan extension, the run and the reading (prepared Sept 26, 2026, revised after Fable's review; nothing built or played yet)

**Specification:** `../b2e_card_check_2026-09-26/README.md`, section 4 (the run) and section 5 (the reading), with its
`b2e_pairings.tsv`. This folder holds the tools to carry it out. When this was written the laptop was busy (an Altaria
training run and a cargo test at first, later another job's cargo build and scans), so **nothing here has been compiled
or run against the engine yet**. The Python checks were dry-run on made-up files and on the real reference files, and
the three shell scripts were run end to end against stand-in programs in a scratch folder (see "The checks" below).

## What

- Six tournament archetype lists and Dustin's six versions of them, each against the eight panel decks: 96 pairings.
- 500 deals per pairing, first with k3 on both sides, then with kp3 on both sides, on the same deals. No mixed rows, never the jev bot.
- Seeds: 21,106,000,000 + 10,000 × pairing + i, for i = 0 to 499. Even i puts the held deck in seat 0, odd i puts the panel deck in seat 0 (the table's convention).
- The result is a baseline, not a decision: how close the simulator gets on decks it was never checked against.

## How (run in this order, in WSL, only when the laptop is free)

**Never beside the network training, a build or another game run** (spec section 4, "Time"). The operator confirms
the queue is idle first. Each of the three scripts also checks it at its start (`idle_or_die`): it refuses to start
while the run-5 training (the run5-venv python: `train_v5.py`, its workers, the audit and held-out steps), `cargo`,
`rustc`, `deckgym` or any `legality_scan` program is running, and says which process it found (if `pgrep` itself
fails or is missing, it refuses too, rather than reading that as idle). It checks once, at the start, so nothing else
should be started on the laptop until the script ends. The build uses 2 jobs; the scans use all cores but two
(`RAYON_NUM_THREADS`), niced.

1. **`bash build_b2e_scan.sh`**: builds the scan program in a scratch folder, `/home/dacz8976/engine-b2e-7fc6ccb`.
   - Takes `git archive 7fc6ccb engine decks` (the official engine's commit) and applies `legality_scan_pairs.patch`.
   - Builds with `nice -n 10 cargo build --release --locked -j 2 --example legality_scan`, copies the program to `legality_scan_b2e_7fc6ccb`, and writes `identity.txt`.
   - `identity.txt` holds the program's sha256 on its first line, then the patch's hash, the official `deckgym` hash, and the hash of every deck file played.
   - It also copies in the pairings file and the six archetype lists, which 7fc6ccb doesn't have.
   - It stops loudly if the scratch folder already exists, if the patch touches any file except `engine/examples/legality_scan.rs`, or if the patch doesn't apply.
   - It also stops if a deck file differs from its committed version, or if the working copy's panel, Dustin or brew-08 files differ from 7fc6ccb's. (Checked Sept 26: all 14 of those files are identical to 7fc6ccb's.)
2. **`bash run_b2e_identity.sh`**: the identity check, on table pairings 0, 5, 13 and 23 × 500 deals, for k3 and for kp3. It plays 8,000 games in all: about 8 minutes per pilot at cloud speed, more on the laptop.
   - **(a) Default flags** (4,000 games). Each game is compared with the reference files, `../per_game_table_2026-09-25/k3_500.jsonl` and `../public_pricing_2026-09-25/kp3_500_*.jsonl`, by `../engine_identity_2026-09-25/compare.py`. Every field must match: decks, seed, first seat, the hash of every move, winner, points, turns and score. This is the check the specification asks for.
     - Given the whole 14,000-game reference, compare.py prints NOT IDENTICAL for any subset, because the other games show up as "only in reference". So each reference is first cut to exactly these 2,000 games per pilot, and compare.py must then say IDENTICAL.
     - Stricter, at no extra games: every line must also be **byte for byte** the line the official, unpatched 7fc6ccb scan wrote for the same deal (`../engine_identity_2026-09-25/{k3,kp3}_500.jsonl`, from legality_scan `d5c0a952…`). compare.py looks at nine fields only, so this also covers `hyper_ray`, `chase_order` and the absence of any added key ("without either flag the program must behave as today"). The table references can't serve here: they were written before `chase_order` existed.
   - **(b) `--pairs` mode** on the same deals (4,000 games), the code path that plays every B2e game. A pairings file lists the same four table pairings with their `decks/research` files (`b2e_checks.py table_tsv`), and the scan runs it with `--seed-base 72000000`. It must replay the same games: compare.py IDENTICAL against the table references, and equal to the official scan's lines once `a_file` and `b_file` are removed. These are the table's own deals, so no new seeds are used.
     - This relies on the table deals having no findings (the official logs say "none"). In `--pairs` mode a game with findings also carries `findings` and `finding_examples`, so such a deal would make (b) FAIL, not pass; the FAIL names the keys that differ.
   - **(c) The guards.** The scan must refuse `--pairs` without `--seed-base`, `--pairs` with `--decks`, a `seed_first` that doesn't match `--seed-base`, `--games` above 10,000 with `--pairs`, and `--seed-base` or `--root` without `--pairs`, before playing anything. (The `--games` test is given a pairings file that doesn't exist and the other two one deal of one pairing, so even a missing guard plays at most one game.)
   - The last line of `identity_check.txt` is either `IDENTITY PASS <program sha256>: ...` or `IDENTITY FAIL: <why>`. On a FAIL the script exits 1. The file also records the sha256 of every reference file used.
3. **`bash run_b2e_rows.sh`**: runs only if `identity_check.txt` ends in the PASS line for this exact program, and only if the scratch copies it will play (the pairings file and its 20 deck files) still have the hashes `identity.txt` recorded at build time. It will not overwrite a finished block file.
   - Runs `lib/deck_check.py files` on the twelve held files as played (`deck_check.txt`).
   - Then plays all 96 rows, k3 first, then kp3, each pilot in two runs, as section 4 names the files: `--pairings 0,...,47` (block A, the archetype lists) into `b2e_<pilot>_arch.{jsonl,txt}` and `--pairings 48,...,95` (block B, Dustin's files) into `b2e_<pilot>_dustin.{jsonl,txt}`, all with `--pairs b2e_pairings.tsv --seed-base 21106000000 --games 500`. The seeds and games are the same as one 96-row run would give: each game's seed depends only on its pairing and deal.
   - Each per-game file is written as `.jsonl.part` and renamed to `.jsonl` only when its scan exits 0, so a `.jsonl` here is always a finished block. If a scan stops, the finished blocks stay and the script refuses to start again until they are moved away (the rule against overwriting a finished run).
   - Output: `b2e_k3_arch`, `b2e_k3_dustin`, `b2e_kp3_arch`, `b2e_kp3_dustin` (`.jsonl`, one line per game, and `.txt`, the scan's log), and `timing.txt` (wall seconds per file).
   - Then runs the rows check (`rows_check.txt`, below).
   - Time: about 1.7 hours per pilot at cloud speed, and more on the laptop.
4. **`python3 read_b2e.py`**: the section-5 reading. It writes `b2e_tables.md`, `b2e_summary.json` and **`READING_draft.md`**.
   - `READING_draft.md` is section 4's `READING.md` as far as a program can write it, clearly marked as a draft: the spec citation, the program's sha256, the IDENTITY PASS and ROWS PASS lines, the tables, the legality findings per pairing, and `identity.txt`, `deck_check.txt` and `timing.txt` pasted in.
   - A person finishes it: for each CHECK code there is an empty "card that may allow it" block, and for each RULE code an empty explanation block. Copy it to `READING.md` and finish it there: `read_b2e.py` rewrites `READING_draft.md` every time it runs and never writes `READING.md`.

## The patch (`legality_scan_pairs.patch`, against `engine/examples/legality_scan.rs` at 7fc6ccb)

**New flags.** It adds three flags. Without `--pairs` and `--seed-base`, the program runs exactly as before.
- **`--pairs <tsv>`** plays exactly the rows of the pairings file, each row with its own two deck files, instead of the table's 28 pairings.
  - Each row plays `held_file` (the first-named deck; output `a` = `held_key`) against `panel_file` (the second-named deck; `b` = `opponent`).
  - Seats follow the table's convention, unchanged: `first_seat` = 0 for even i and 1 for odd i.
  - `--pairings` still filters, now by the file's pairing numbers.
  - With `--pairs`, the program refuses `--decks` and requires `--seed-base`, so B2e can never fall back onto the table's 72,000,000 seeds by accident.
  - If the file has a `seed_first` column, every row must equal base + 10,000 × pairing, or the program stops.
  - It refuses `--games` above 10,000: a pairing's sub-block holds 10,000 seeds, so more would spill into the next pairing's.
- **`--seed-base <n>`** replaces 72,000,000: seed = base + 10,000 × pairing + i. Only with `--pairs`: without it the program refuses, so a table-shaped file can't come from another seed block. The `--pairs` log line prints the base.
- **`--root <dir>`** (only with `--pairs`, refused without it; default `..`) says how the file's deck paths are found.
  - The paths in `b2e_pairings.tsv` are relative to the repo root. The scan runs from the `engine/` folder as it does today, so `..` is the root of whichever tree it runs in. An absolute path is used as it is.
  - The scripts run it in the scratch tree, so the decks read are the copies checked at build time, not files another session could edit mid-run.

**Per-game lines.** With `--pairs`, each `--games-out` line has today's fields (`pairing`, `a`, `b`, `i`, `seed`, `bot_a`, `bot_b`, `first_seat`, `winner_seat`, `points`, `turns`, `first_deck_score`, `moves`, plus `hyper_ray`/`chase_order` when present). It also has:
- `a_file` and `b_file`: the two deck paths, as the file gives them;
- only for a game that has legality findings (RULE or CHECK): `findings`, the codes and their counts, and `finding_examples`, each code's first example in that game (the scan's own text: the decks in seat order, the seed, the turn and the move or state). Section 4 asks for findings per pairing, each CHECK with its example; the log keeps only four examples per code for a whole run.

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

Everything the patch adds on top runs only with `--pairs` (the extra JSON fields, the extra log line, the TSV reader, the `--games` limit and the checks), or only checks that a flag is absent (the default run's two refusals look for `--seed-base` and `--root`, which a default run doesn't pass). Nothing in the game loop, the checks, the fingerprint or the per-game result changed.

This argument is checked in practice by step 2 before any B2e game is played: 4,000 default-flag games, move hash included, and every line byte for byte the official scan's. Step 2 also replays the same deals through `--pairs`. The patch has not been compiled yet; the first compile is step 1.

## The checks

- **Build:** the patch touches one file and applies to 7fc6ccb's copy; a second apply fails, and the patched file equals `review/legality_scan_patched.rs` (checked Sept 26, again after the revision). The build uses `--locked` against 7fc6ccb's Cargo.lock. The deck files are checked against git (above), and their hashes go in `identity.txt`.
- **Identity:** before any B2e game (step 2). Default flags: 4,000 games, field by field including the move hash, and byte for byte the official scan's lines. `--pairs` mode: the same 4,000 deals replayed. Six refusals are also tested. The rows script and the reader both refuse to run without the PASS line for this program's sha256.
- **Rows** (`b2e_checks.py rows`, written to `rows_check.txt`; the reader runs it again). It takes the four block files:
  - Each block file holds exactly its block's 48 pairings × 500 deals, one line per (pairing, i), and nothing from the other block. Together a pilot's two files hold all 96 pairings.
  - Every line has every field the specification names, plus `a_file` and `b_file`, and `moves` is a 16-hex-digit hash.
  - Every seed = `seed_first` + i = 21,106,000,000 + 10,000 × pairing + i, and none is past `seed_last`.
  - `first_seat` = i mod 2.
  - `a`, `b`, `a_file` and `b_file` match the TSV row, and `bot_a` = `bot_b` = the pilot.
  - Each score agrees with its winner.
  - A game with `findings` names one example per finding code in `finding_examples` (the same codes); a game without has neither.
  - k3 and kp3 are on the same (pairing, i, seed) set.
  - Each file's per-game findings add up to its own log's findings section.
  - It prints RULE and CHECK findings per pairing, each code with its first example in that pairing. Its last line is `ROWS PASS ...` or `ROWS FAIL ...`.

### Dry runs (no games, no build; Sept 26, after the revision)

- **Python, made-up 96 × 500 block files** (the real TSV and Limitless files, read only):
  - A clean set passes the rows check, and the reader writes all three files. `READING_draft.md` starts with the DRAFT mark and has the spec citation, sha256, both PASS lines, the tables, each CHECK code with each pairing's own first example (a code in pairing 3 and pairing 70 shows both, each with its own deal and seed), one empty card block per CHECK code, and identity.txt, deck_check.txt and timing.txt.
  - A set with a RULE finding in one pairing passes the rows check. The reader withholds that cell and that deck's panel score under that pilot, and the draft lists the RULE with its example and an empty explanation block.
  - Fourteen planted defects each make the rows check FAIL and the reader refuse. The reader refuses both at its gate and, with a forged ROWS PASS line, through its own re-run of the rows check. The defects: a wrong seed; a game in the other block's file; a finding without examples; examples naming other codes; examples without findings; a log that disagrees with its file; a missing game; a game in both of a pilot's files; a wrong pilot; a missing field; a deal given as text; a missing file; a wrong first seat; a score that disagrees with its winner.
  - The arch and dustin files swapped, on the command line or on disk, fail too. The reader also refuses a missing IDENTITY PASS line and a rows_check.txt that names another binary.
- **Python, the real reference files:** the cuts of `k3_500.jsonl` and of `kp3_500_*` to pairings 0, 5, 13 and 23 give exactly 2,000 games each with the right pilot, and k3 games are refused as kp3. compare.py on the official scan's lines against the table cuts prints the three lines the identity script looks for, for both pilots.
  - `same` fails the table references against the official lines as it should, now naming the key: "chase_order (new only)" in 635 (k3) and 651 (kp3) lines.
  - `same --drop a_file,b_file` passes the official lines with the file keys added. With findings planted in one line it fails, naming `finding_examples`, `findings` and the changed field. `table_tsv` writes the four-row file.
- **idle_or_die**, on harmless processes started and killed within a second: 28 checks, all pass.
  - Found: a process with a watched name (test names standing in for cargo and a scan); a name longer than 15 characters (`legality_scan_b2e_7fc6ccb`, seen as `legality_scan_b`); a `deckgym`; a process started as the run5-venv's `bin/python`, `python3` or `python3.14`; a python with `train_v5.py` as an argument.
  - Not found: a name that only starts like a watched one; `my_legality_scan` (the match is anchored); a program whose argv[0] claims a watched name; another venv's python; a path that only ends like the venv's; a bash, or the checker itself, whose command line names every pattern.
  - The three scripts' blocks are identical, and each calls it once. Run for real at the time of writing, it found the other job's cargo, rustc and a legality_scan, so it would have refused.
  - Revised in the second review (Sept 26): `pgrep` finding nothing (exit 1) counts as idle, but any other `pgrep` failure (not installed, a bad pattern) now stops the script instead of reading as idle. Checked under `set -euo pipefail` on harmless processes: nothing running passes; a bad pattern and a PATH without `pgrep` both stop with "pgrep -x ... failed"; a running match stops; the 28 checks above and both flow tests below pass again.
- **The shell scripts, end to end, against stand-in programs** (copies of the scripts with only the folders pointed at scratch):
  - `run_b2e_rows.sh` writes the four block files with the right `--pairings` lists, `.part` names and `RAYON_NUM_THREADS`. It then passes its rows check and the reader reads the result.
  - A second run refuses. A scan stopped in the last block leaves its `.part` and keeps the three finished blocks, and the reader refuses that run.
  - `run_b2e_rows.sh` also refuses while a watched process runs (writing nothing), without the PASS line, and with a changed deck copy.
  - `run_b2e_identity.sh` passes with a correct stand-in and records all six refusals.
  - It FAILs if the stand-in lacks the `--games` guard or accepts `--seed-base` without `--pairs`. It also FAILs, naming `finding_examples` and `findings`, if one `--pairs` game has findings.
  - While a watched process runs it stops as "IDENTITY NOT RUN" and leaves an earlier `identity_check.txt` untouched.
- All three shell scripts and `review/check_patch.sh` pass `bash -n`. Every file here is LF only.

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
  - Each CHECK and RULE code is listed per pairing with that pairing's own first example (from the per-game `finding_examples`), in `rows_check.txt`, `b2e_summary.json` and `READING_draft.md`. `b2e_tables.md` also pastes the four logs' findings sections.
  - Naming the card that may allow a CHECK is left to the person who finishes `READING.md`.

## Where this differs from the specification (for the reviewer)

- **Folder name.** The spec names the folder `rl/results/b2e_runs_<date>/`; this one is `rl/results/b2e_rows_2026-09-26/`. The four per-game files now have section 4's names (`b2e_k3_arch`, `b2e_k3_dustin`, `b2e_kp3_arch`, `b2e_kp3_dustin`).
- **`run_b2e.sh`** is split into three scripts: build, identity and rows (each step gates the next).
- **`READING.md`** is written as `READING_draft.md` for a person to finish (the card for each CHECK needs a person); the draft says so at the top and states the two differences above.
- **Extra fields and flag.** The per-game `findings` and `finding_examples` fields and the `--root` flag are small additions the spec doesn't name.

## Seed block (one row for START_HERE's seed table when the run is recorded; not added there)

| Seeds | Used by |
|---|---|
| 21,106,000,000 – 21,106,999,999 | B2e, held-out archetypes against the panel (Sept 26): seed 21,106,000,000 + pairing × 10,000 + i, pairings 0–95, i < 500, k3 and kp3 on the same deals (used up to 21,106,950,499); 21,106,999,000–21,106,999,001: the six 2-game smokes; sub-blocks 96–98 spare |

## Files

| File | What it is |
|---|---|
| `legality_scan_pairs.patch` | The change to `engine/examples/legality_scan.rs` at 7fc6ccb (+114 −12 lines). |
| `build_b2e_scan.sh` | Step 1: scratch build, writes `identity.txt`. |
| `run_b2e_identity.sh` | Step 2: default-flag and `--pairs` replays and the six refusals; writes `identity_check.txt`, `identity_{k3,kp3}.{jsonl,txt}`, `identity_pairs_{k3,kp3}.{jsonl,txt}`. |
| `run_b2e_rows.sh` | Step 3: `deck_check.txt`, `b2e_{k3,kp3}_{arch,dustin}.{jsonl,txt}`, `timing.txt`, `rows_check.txt`. |
| `b2e_checks.py` | The subset, same-lines, table_tsv and rows checks the scripts and the reader use. |
| `read_b2e.py` | Step 4: writes `b2e_tables.md`, `b2e_summary.json` and `READING_draft.md`. |
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

## Changes after Fable's review (Sept 26)

Fable's review of commit 8aa6ea3: `../fable_reviews_2026-09-26/b2e_rows_review.md` (no high finding; four medium, eleven low). What changed, item by item:

| Item | Finding | Change |
|---|---|---|
| **M3** | Each pairing's CHECK examples were lost (the log keeps four per code for the whole run). | The patch adds `finding_examples` to each `--pairs` games-out line of a game with findings: each code's first example in that game. The new lines sit inside `if let Some(..) = &row.files`, which only `--pairs` sets, so default lines are unchanged (identity step (a) checks them byte for byte). `b2e_checks.py rows` requires `finding_examples` to name exactly the game's finding codes and collects each pairing's first example per code; `rows_check.txt`, `b2e_summary.json` and `READING_draft.md` list each CHECK per pairing with its own example. |
| **M1** | Two files per pilot, not section 4's four. | `run_b2e_rows.sh` runs each pilot twice, `--pairings 0..47` into `b2e_<pilot>_arch` and `48..95` into `b2e_<pilot>_dustin` (same seeds and games), after checking that the TSV's blocks are exactly those numbers. `b2e_checks.py rows` takes the four files, checks each holds exactly its block, and checks each against its own log. `read_b2e.py` requires and reads the four. The gates refuse if any of the four finished files exists, and the reader refuses if any of the four files or logs is missing. Each block's log now keeps its own four examples per code. |
| **M4** | Nothing enforced "not beside the training"; the build and scans were uncapped. | `idle_or_die`, identical in the three scripts, runs first. It matches process names exactly (`pgrep -x cargo`, `rustc`, `deckgym.*`, `legality_scan.*`), the run5-venv python by its exact path as argv[0], and any python given `train_v5.py` as an argument. There is no `pgrep -f`, so a script's own command line can't match. The build uses `cargo -j 2`; the scans use `RAYON_NUM_THREADS` = cores − 2 (at least 1; 0 would mean every core), niced. The rule is in each script's header and in "How" above. Tested as described under "Dry runs". |
| **M2** | READING.md was not produced. | `read_b2e.py` also writes `READING_draft.md` (step 4 above), marked as a draft. It never writes `READING.md`. |
| **L1** | `--seed-base` and `--root` were accepted without `--pairs`. | Both are refused without `--pairs` (identity step (c) tests both). The `--pairs` log line already prints the seed base, and a default run can now only use 72,000,000. |
| **L7** | No limit on `--games` per pairing. | `--pairs` refuses `--games` above 10,000 (identity step (c) tests it). |
| **L8** | A failed scan left an empty games-out file the rows script then refused to overwrite. | The rows script writes `.jsonl.part` and renames it only on exit 0. |
| **L2** | A `same` FAIL didn't say why. | `same` prints the keys that differ (on one side only, or with different values), per line and counted over all lines. The identity script's header says step (b) relies on the table deals having no findings. |
| L3, L4, L5, L6, L9, L10, L11 | | Not changed in this pass (see below). |

Not changed in this pass: this pass took M1 to M4 and the lows that were a line or two (L1, L7, L8, L2).
- **L3** (assert the official `deckgym`/`legality_scan` hashes): both are recorded in `identity.txt`, and the review found they match the spec today.
- **L4** (a probe replay with a non-default seed base): needs about a minute of extra games and its own comparison. Guard (c) and the rows check's per-game seed check still catch a wrong base, only later.
- **L5** (identity step (a) comparing the log's findings section and per-pairing lines): more than a line or two.
- **L6** (pin the inputs' hashes to a commit): means choosing the commit to pin. `inputs_sha256.txt` and `inputs_source.txt` already record what was played.
- **L9** (checked seed arithmetic): the TSV's pairings are 0 to 95, far from overflow, and the rows check verifies every seed.
- **L10** (`arg()` taking a flag as a value): behaviour from before the patch, and changing it would touch the default path's parsing.
- **L11** (the canonical `--root` in the log): cosmetic.

**Rust in the patch that has never been compiled.** The whole patch is still uncompiled; step 1 is its first compile. These are the expressions this revision added:
- `assert!(games <= 10_000, "--pairs: a pairing's sub-block holds 10,000 seeds, so --games {games} is too many");`
- the `else` branch with `assert!(arg(&args, "--seed-base").is_none(), "...")` and `assert!(arg(&args, "--root").is_none(), "--root is only for --pairs");`
- `let first: BTreeMap<&String, &String> = r.findings.examples.iter().filter_map(|(code, e)| e.first().map(|x| (code, x))).collect();`
- `line["finding_examples"] = serde_json::json!(first);`

`BTreeMap` is already imported, and `json!` serializes a map of string references as it does the existing `r.findings.count`. Each game's `examples` holds exactly one text per code: `record` in `play_one` pushes an example only the first time a code appears in that game.
