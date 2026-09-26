# Review of commit 8aa6ea3 (B2e rows) against the run specification: lens = specification compliance

Reviewer: Fable, Sept 26, 2026, by reading only. No cargo, no binary, no game was run; the laptop is running a
training queue (seven run5-venv workers at about 100% CPU while this was written).

What was reviewed: the ten files of commit 8aa6ea3 under `rl/results/b2e_rows_2026-09-26/` (unchanged in the
working tree: `git diff --stat 8aa6ea3` touches only `b4b_prep_2026-09-26/` and one doc). The specification is
`rl/results/b2e_card_check_2026-09-26/README.md`, section 4 (the run) and section 5 (the reading), with
`b2e_pairings.tsv`. The reference tool is `engine/examples/legality_scan.rs` at 7fc6ccb (`git show`, sha256
7332d4c0…974d, byte-identical to the committed `review/legality_scan_7fc6ccb.rs`). The reference per-game files
are `per_game_table_2026-09-25/k3_500.jsonl` (28 x 500) and `public_pricing_2026-09-25/kp3_500_{worst5,rest}.jsonl`
(5 + 23 pairings x 500). The Sept 25 identity was `engine_identity_2026-09-25/compare.py` + `identity.txt`.

Line numbers below are the working-tree files (= the commit). "patched.rs" is `review/legality_scan_patched.rs`,
which I confirmed equals 7fc6ccb's file with the patch applied (`patch -p1` in scratch, exit 0; `git apply --check`
in the repo also OK; numstat +104 -12, one file).

## Verdict in one line

No high finding. The tool change, the seeds, the seat convention, the pilots, the identity check and the section-5
arithmetic follow the specification. Four medium deviations (output file layout, no READING.md, per-pairing CHECK
examples lost, no "not beside training" guard) and four low ones.

## Section 4, item by item

| Spec item | Where in the commit | Result |
|---|---|---|
| Engine: official 7fc6ccb, deckgym f4d235e5… stays the reference; scan built from 7fc6ccb + this one change | `build_b2e_scan.sh:25-28` (`git archive 7fc6ccb engine decks`), `:51-59` (patch must touch `engine/examples/legality_scan.rs` only, numstat-checked, `git apply --check`), `:62-66` (`cargo build --release --locked --example legality_scan`, WSL) | OK. `engine/` is unchanged between 7fc6ccb and HEAD (`git diff --stat 7fc6ccb HEAD -- engine/` empty), `engine/Cargo.lock` exists at 7fc6ccb, the card database is compiled-in generated code (`engine/src/database.rs`, `card_ids.rs`), so the scratch tree needs nothing outside the archive. deckgym is not rebuilt. |
| Pilots: k3 both sides, then kp3 both sides, same deals; no mixed rows; never jev | `run_b2e_rows.sh:47-52` (`for bot in k3 kp3`, `--bot "$bot"`); `patched.rs:548-555` (`--bot` sets both sides; jev asserted out) | OK. `bot_a = bot_b = pilot` is re-checked per line by `b2e_checks.py:238-241`. |
| 96 pairings, order p = 8d + o (+48 block B), files h-<key>.txt / t-<label>.txt / Dustin's six | `b2e_pairings.tsv` rows 0-95; `read_b2e.py:151-159` (`check_layout` re-derives d, o and the key); `build_b2e_scan.sh:34-44` (20 distinct deck files, each equal to its committed or 7fc6ccb version) | OK. I re-checked: the 14 files that exist at 7fc6ccb are identical at HEAD; the six h-files are copied only after `git show HEAD:` matches the working copy. Block B keys are `dustin_<key>`, which `read_b2e.py:157` expects. |
| 500 deals, even i = held deck in seat 0, exactly as play_one at 7fc6ccb | `patched.rs:403-404` = reference lines 374-375 verbatim; `(a, b)` for a `--pairs` row is (held, panel) by construction (`patched.rs:531-536`) | OK. `b2e_checks.py:236-237` re-checks `first_seat = i % 2` on every line. |
| Seeds 21,106,000,000 + 10,000 p + i | `run_b2e_rows.sh:15` (`BASE=21106000000`), `patched.rs:402` (`lineup.seed_base + pairing * 10_000 + i`, pairing = the TSV's number, not the row index), `:527-530` (each row's `seed_first` must equal base + 10,000 p or the scan stops) | OK. Range used 21,106,000,000 to 21,106,950,499, inside the claimed block and outside every START_HERE range (nearest 21,101,300,001 and 22,000,000,000). `b2e_checks.py:233-235` checks seed = seed_first + i = base + 10,000 p + i and <= seed_last. |
| `--pairs <tsv>`, `--seed-base <n>`, default behaviour unchanged | `patched.rs:556-573`. Default arm: decks from `NAMES` in order, the same pair enumeration, `seed_base = SEED_BASE`, names = NAMES; `row.files = None` so no extra JSON key (`:641-647`) | OK. Every hunk walked; the default path computes the same decks, pairs, seed, seats, players, names and JSON as the reference. |
| Output fields a, b, pairing, bot_a, bot_b, first_seat, winner_seat, points, turns, first_deck_score, moves | `patched.rs:628-633` (unchanged keys), `:641-647` (`a_file`, `b_file`, `findings` only in `--pairs` mode) | OK. `a` = held_key, `b` = opponent (`:533, :535`). |
| Identity before any B2e game: default flags vs the reference files, field by field incl. the move hash, at least 0, 5, 13, 23 x 500 per pilot | `run_b2e_identity.sh:36` (`PAIRINGS=0,5,13,23`), `:92-103` (default flags, `compare.py` on the 2,000-game cut, then byte-for-byte against the official scan's own lines `engine_identity_2026-09-25/{k3,kp3}_500.jsonl`), `:105-115` (the `--pairs` path replays the same deals with `--seed-base 72000000`), `:87-90` (three refusal tests) | OK, and stronger than asked. `compare.py` compares a, b, seed, first_seat, moves, winner_seat, points, turns, first_deck_score. The byte-for-byte step also covers hyper_ray, chase_order and any added key (the table references predate chase_order: 0 lines with it, vs 2,022 in the official scan's k3 output). `run_b2e_rows.sh:22-26` and `read_b2e.py:81-95` refuse without the PASS line for the same sha256. |
| Run folder and files: `rl/results/b2e_runs_<date>/`, `run_b2e.sh`, `identity.txt` (scan sha256 + deckgym's), four output pairs, `timing.txt`, `READING.md` with deck_check pasted | folder is `b2e_rows_2026-09-26/`; three scripts; `identity.txt` from `build_b2e_scan.sh:71-84` (binary, patch, deckgym, official scan, every input's sha256); two output pairs `b2e_{k3,kp3}.{txt,jsonl}`; `timing.txt` `run_b2e_rows.sh:51`; `deck_check.txt` `:38-42`; `READING.md` not produced (`README.md:109`) | Deviations: findings 1, 2, 5 below. |
| Legality findings per pairing: RULE stops the reading, CHECK listed with its example | `b2e_checks.py:279-289` (per pairing, per pilot), `read_b2e.py:175-176, 195-197` (withholds the pairing and every panel score that needs it), `:430-438` (pastes the logs' findings sections) | RULE handling OK. CHECK examples per pairing are not available: finding 3. |
| Run after training, never beside it | not enforced anywhere; commit message says "overnight queue after the kpr rows" | Finding 4. |
| Fallback (deckgym simulate) | not used | OK (nothing to check). |
| Not part of B2e: no ranking, no list change, no mixed rows | `read_b2e.py:1-3` ("descriptive only"); no mixed rows in any script | OK. |

## Section 5, item by item (`read_b2e.py`)

- Cell score = mean of `first_deck_score` x 100 (`:186-191`), ties = `winner_seat` -1 counted per cell (`:190`, printed `:244-246`). Tie gives 0.5 in the reference (`legality_scan_7fc6ccb.rs:447`), and `b2e_checks.py:242-245` checks every line's score against its winner and seat. OK.
- Panel score = equal-weight mean of the eight cells, under k3 and kp3, archetype list and Dustin's file (`:195-200, :256`); band = 1.96 sqrt(sum p(1-p)/n)/8, panel_bands.py's formula. OK.
- Gap = panel score minus the Limitless equal-weight average, pooled and development (`:258-259`); Whimsicott's development gap over its seven development opponents (`:253, :257`, from `n > 0` in the CSV). OK.
- Per-cell miss = sim minus pooled cell; beyond when |miss| > sqrt(band_L^2 + band_S^2) (`:272, :388`, `math.hypot`); band_S = 1.96 sqrt(p(1-p)/500) from the simulator's own p (`:107-108`; 4.38 at 50%). One-sided cells read as "no information" (`:270-271, :385-386`); bands over 15 marked wide (`:128, :392-393`); the known sceptile/vespiquen/altaria misses noted, not fixed (`:64-68, :394-395`). OK.
- List difference = archetype list minus Dustin's file, per pilot (`:260-264`). OK.
- Veto baseline |kp3 - L| with k3 beside and the development figure beside (`:350-361`). OK.
- A2's bar: kp3, block A, each panel score against the pooled 3.7 interval from `panel_intervals.csv` (`:330-347`); stated, not applied. OK.
- The Limitless cells and averages are recomputed from W-L-T-n and checked against the CSV's rounded columns (`:111-148`); column names and archetype keys match `limitless_cells.csv` and `panel_intervals.csv` (checked). OK.
- "kp3 minus k3 paired by deal" (`:202-211`) is an addition the spec does not ask for; harmless.

## Findings

### 1. Medium: two per-pilot output files instead of the spec's four block-split pairs
- `run_b2e_rows.sh:47-52`: one `--games-out "$D/b2e_$bot.jsonl"` over all 96 rows per pilot; `README.md:113` discloses it.
- Spec section 4 "Run folder and files": `b2e_k3_arch`, `b2e_kp3_arch`, `b2e_k3_dustin`, `b2e_kp3_dustin` `.{txt,jsonl}`.
- Beyond the name: the scan's findings section and its examples are pooled over the whole run (`patched.rs:50` `EXAMPLES_KEPT = 4`, `:72-76`, `:652-665`), so one log per pilot halves what a reader gets per block.
- Fix: run each pilot twice, `--pairings 0,1,...,47` to `b2e_${bot}_arch.{txt,jsonl}` and `48,...,95` to `b2e_${bot}_dustin.{txt,jsonl}` (same seeds, same games, no extra cost), and let `b2e_checks.check_rows` and `read_b2e.py` take the two files per pilot (concatenate before the existing checks; the log-findings check then reads two logs). If the single file is kept on purpose, say so in READING.md and in the spec README's section 4 in one line each.

### 2. Medium: READING.md is not produced
- `read_b2e.py:449-453` writes `b2e_tables.md` and `b2e_summary.json`; `README.md:109`: READING.md "is still to be written by whoever reads the run".
- Spec section 4: `READING.md` with section 5's tables filled in, citing the README, with the `deck_check.py files` output pasted in.
- Fix: have `read_b2e.py` also write `READING.md`: a header citing the spec README sections 4 and 5, the binary sha256, the IDENTITY PASS and ROWS PASS lines, then the same tables, the findings sections, `deck_check.txt` and `timing.txt`, with a clearly marked empty block per CHECK code for "the card that may allow it" (the one part that needs a human). The folder is then complete when the run finishes.

### 3. Medium: per-pairing CHECK examples are lost
- `legality_scan_pairs.patch:176-182` (`patched.rs:641-647`): the per-game JSON carries `findings` as code -> count only. Examples are kept 4 per code for the entire run (`patched.rs:50, 72-76`, `all.merge` at `:653`).
- Spec section 4: "Report findings per pairing ... CHECK is listed with its example and the card that may allow it." A CHECK code that first appears in pairing 3 uses up its four examples; the same code in pairing 70 then has none, and `read_b2e.py:430-438` can only paste the pooled section.
- Fix: in `--pairs` mode, fold each pairing's results into a per-pairing `Findings` and print that pairing's section (code, occurrences, games, examples) right after its summary line, before merging into `all`; or add `"finding_examples": {code: first example}` to each JSON line in `--pairs` mode (the example string already exists in `r.findings.examples`). Then `read_b2e.py` lists each CHECK with its own pairing's example.

### 4. Medium: nothing enforces "run after training, never beside it"; the build is uncapped
- `build_b2e_scan.sh:63`: `nice -n 10 cargo build --release --locked --example legality_scan`, no job cap. `run_b2e_rows.sh:47-52` and `run_b2e_identity.sh:96, 108` start the scans with no check that the trainer is idle. The commit message queues the run "after the kpr rows", but no file in the folder (or elsewhere in the repo) encodes that order.
- Spec section 4 "Time": run when the network training has finished, not beside it. Tonight another job's build nearly triggered the OOM killer; at review time seven `run5-venv` python workers were at about 100% CPU (`rl/runs/diag-altaria-lucario/STATUS.txt`: FINISHED, report steps running).
- Fix: add one `idle_or_die` function to the top of all three scripts: die if `pgrep -f 'run5-venv/bin/python'`, `pgrep -x cargo` or `pgrep -x rustc` finds anything, or if any `rl/runs/*/STATUS.txt` contains "State: RUNNING"; build with `-j 2` (or `CARGO_BUILD_JOBS=2`) and keep `nice`; say in README "How" that the operator confirms the queue is idle first.

### 5. Low: folder and script names differ from the spec
- Folder `rl/results/b2e_rows_2026-09-26/` (spec: `rl/results/b2e_runs_<date>/`); `run_b2e.sh` split into `build_b2e_scan.sh`, `run_b2e_identity.sh`, `run_b2e_rows.sh` (`README.md:113-114` discloses both). The split is an improvement (each step gates the next); the folder name is just different.
- Fix: either `git mv` the folder to `b2e_runs_2026-09-26` before the run (the scripts hard-code `D=` at `build_b2e_scan.sh:12`, `run_b2e_identity.sh:30`, `run_b2e_rows.sh:11`) or state the mapping in one line of READING.md and of the spec README section 4.

### 6. Low: `--root` without `--pairs` is accepted and ignored; `--seed-base` without `--pairs` reseeds a table-shaped run silently
- `patched.rs:557-562`: only `--pairs` is guarded. `:577-579`: the seed base is printed only in `--pairs` mode, so a table run with a stray `--seed-base` writes 28-pairing files on non-table seeds with no sign in the log. The spec's "without either flag" wording allows this, so it is hygiene, not a breach.
- Fix: `assert!(arg(&args, "--root").is_none() || pairs_file.is_some(), "--root only with --pairs")`; print `seed base {seed_base}` on the first log line whenever it differs from `SEED_BASE`.

### 7. Low: the `--pairs` replay check would fail on a reference game with findings, although the tool would be right
- `b2e_checks.py:135-141` (`same --drop`): the dropped keys must be present and only they are removed; a `--pairs` line with findings also carries `findings` (`patched.rs:644-646`), which would then differ from the official line. Today it cannot fire: both official logs end "Findings ... none" (`engine_identity_2026-09-25/k3_500.txt`, `kp3_500.txt`), so the strictness doubles as a "still no findings on table deals" check.
- Fix: say so in `run_b2e_identity.sh`'s header (so a future FAIL there is read correctly), or add `--drop-optional findings` and compare the findings against the log instead.

### 8. Low: `identity.txt` hashes the official binaries without checking them against the spec's hashes
- `build_b2e_scan.sh:76-77` hash whatever is at `rl/engine-2026-09-25/{deckgym,legality_scan}`; the spec names f4d235e5…1034 and d5c0a952…bfbfb (`project_manifest.json`, `available_release`). A replaced file would be recorded, not refused.
- Fix: `[ "$(sha256sum "$R/rl/engine-2026-09-25/deckgym" | cut -d' ' -f1)" = f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034 ] || die`, and the same for `legality_scan` against d5c0a9528e076299875ac603667f7076951de885ea8465f3be0d1089b5afbbfb; `run_b2e_identity.sh:73` already records the reference files' hashes, which is enough there.

## Checked and found in order (so nobody re-checks them)

- The committed `review/legality_scan_7fc6ccb.rs` is byte-identical to `git show 7fc6ccb:engine/examples/legality_scan.rs`; the patch applies to it (dry run and real, in scratch) and the result is byte-identical to `review/legality_scan_patched.rs`; `git apply --check` in the repo passes; the patch touches one file, +104 -12.
- Default path unchanged: `fn play_one` (reference 370-375 vs patched 401-404), deck loading order (reference 492 vs patched 567), pair enumeration (reference 498 vs patched 568-569, 581-582), JSON keys (reference 544 vs patched 629), example strings (`lineup.names` = `NAMES` in the same order). `--seed-base` absent gives `SEED_BASE` (`patched.rs:557`).
- Seat rule and tie score unchanged (`patched.rs:403-404, 474-477`).
- The scan's `--pairings`, `--games`, `--bot`, `--games-out` parsing is the reference's (`patched.rs:544-550, 563`); `--games 500` and `--pairings 0,5,13,23` are the forms it takes.
- The `--pairs` reader: header by column name, BOM and CRLF tolerant, duplicate pairing refused, `seed_first` cross-checked, rows in file order, decks resolved against `--root` (default `..`, i.e. the scratch tree's root when run from `$B/engine`, which both scripts do); an absolute TSV path is fine. Deck::from_file takes `&str` (`engine/src/deck.rs:31`) and parses both the ids-only `decks/research` lines and the named `t-*.txt`/h-file lines through the same `Card::from_str_with_count`.
- The identity replay's `--pairs` step uses `decks/research/<name>.txt` (the table's own files, present at 7fc6ccb) with `--seed-base 72000000`, so it uses no new seeds.
- `b2e_checks.py rows`: 96 x 500 per file, every spec field, moves as 16 hex digits, seed and seat formulas, a/b/a_file/b_file/bot fields against the TSV row, score against winner, k3 and kp3 on the same (pairing, i, seed) set, per-game findings summed = the log's findings section (parser handles codes that contain ": ").
- `run_b2e_rows.sh` gates: identity PASS for this sha256, `identity.txt` names it, the repo's TSV unchanged since the build, the 21 played copies' hashes re-verified against `inputs_sha256.txt` and `identity.txt`, no finished file overwritten; `deck_check.py files` on the twelve held files as played (database resolved relative to `lib/`, so running from `$B` works).
- `read_b2e.py` gates: identity PASS, `rows_check.txt` first line = the same binary, ROWS PASS, and the rows check re-run.
- The `untrusted-prone` flags in `read_b2e.py:56-63` match the spec's section 6 table.
- Seed-table row prepared in `README.md:117-121`, not written to START_HERE (as the spec asks).
- No mixed rows, no ranking, no list change, no run of other decks.

## Scratch (not needed to reproduce anything)

`C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\75cb92d0-6f2d-44b8-a636-513a8f7ee71a\scratchpad\b2e_review\`:
`git_show.sh`, `dump_ref.sh`, `facts.sh`, `facts2.sh` (the read-only git and file checks above), `legality_scan_7fc6ccb.rs`
(the `git show` dump) and `patchtest/` (the patch applied to it).
