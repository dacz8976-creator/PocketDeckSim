# Review of commit 8aa6ea3 (the B2e rows) against the B2e run specification

Fable, the "Deck pilot bot project review" session, Sept 26, 2026, 03:25. Written on Dustin's instruction to review the
laptop session's commit 8aa6ea3 on main ("B2e rows: legality_scan --pairs/--seed-base patch (against 7fc6ccb, not yet
compiled), build, identity and run scripts, reader; reviewed by reading") against the specification the same night's
earlier work produced, `rl/results/b2e_card_check_2026-09-26/README.md` sections 4 (the run) and 5 (the reading). This
review is independent of the laptop session's own reading (its folder README, "Review (Sept 26, before any build)").
The laptop session owns the code and decides what to change; Dustin decides direction.

## For Dustin, in plain words

The laptop session prepared everything needed to play the 96 held-out pairings (the six tournament lists and your six
versions, each against the eight panel decks, 500 deals each, two pilots). I read all of it against the specification
without building or running anything, because the laptop is shared with the training queue tonight. Nothing I found
would make a game, a seed or a seat wrong, and the check that runs before the real games is strong enough to catch a
wrong tool. The run can go ahead as it is, when the laptop is free. There are a few tidy-ups, listed below with exact
fixes, for the laptop session to decide on; two of them are cheaper to do before the run than after. Nothing outside
`rl/results/fable_reviews_2026-09-26/` and the session scratchpad was written.

## How this review was done (and what it did not do)

- By reading only. No cargo (no build, check or test), no engine binary, no game, no background process: the no-build
  rule for tonight (a build from another job nearly triggered the OOM killer; seven training workers were at about
  100% CPU while the lens notes were written). The only things executed were read-only git commands, sha256 sums,
  a `diff`, and `git apply` of the patch onto a scratch copy of 7fc6ccb's file in the session scratchpad, outside
  the repo.
- What was read: the commit's ten files under `rl/results/b2e_rows_2026-09-26/` (`README.md`, `b2e_checks.py`,
  `build_b2e_scan.sh`, `legality_scan_pairs.patch`, `read_b2e.py`, `run_b2e_identity.sh`, `run_b2e_rows.sh`,
  `review/check_patch.sh`, `review/legality_scan_7fc6ccb.rs`, `review/legality_scan_patched.rs`); the reference tool
  `git show 7fc6ccb:engine/examples/legality_scan.rs`; the reference per-game files
  `rl/results/per_game_table_2026-09-25/k3_500.jsonl` and `rl/results/public_pricing_2026-09-25/kp3_500_{worst5,rest}.jsonl`;
  the Sept 25 identity (`rl/results/engine_identity_2026-09-25/compare.py`, `identity.txt`); START_HERE's seed table;
  the spec and its `b2e_pairings.tsv`.
- The working tree equals the commit for all ten files (checked at 03:25: `git status` clean and
  `git diff 8aa6ea3` empty on the folder; HEAD is 1ff9369, five commits later, none touching the folder). Line
  numbers below are the working-tree files. "patched.rs" is `review/legality_scan_patched.rs`, which is byte for byte
  what the patch produces from 7fc6ccb's file (checked); "patch" lines are `legality_scan_pairs.patch`.
- Three lens notes beside this file carry the full evidence: `b2e_rows_review_spec.md` (specification compliance),
  `b2e_rows_review_rust.md` (the Rust patch, hunk by hunk), `b2e_rows_review_scripts.md` (the scripts and the run
  discipline). Where two lenses raised the same issue it appears once below, with every line reference.
- No card's text is stated anywhere in this review.

## Verdict

No high finding. The tool change does what section 4 asks and, by reading every changed hunk against 7fc6ccb, leaves
the default run unchanged: same eight decks in the same order, same 28 pairings, seed base 72,000,000 when no flag is
given, same seat rule (even deal = first-named deck in seat 0), same JSON keys and values, same legality checks. The
`--pairs` path plays the held deck first-named, seeds each game at 21,106,000,000 + 10,000 x pairing + deal, and
refuses to run without an explicit `--seed-base`, so B2e cannot fall back onto the table's seeds by accident. The
identity check is stronger than the spec's minimum (4,000 default-flag games per pilot pair compared move hash for move
hash with the Sept 25 references by the Sept 25 `compare.py`, then byte for byte with the official scan's own lines,
then the same deals replayed through `--pairs`, then three refusal tests), and both the rows script and the reader
refuse to start without that PASS line bound to the binary's sha256; it would catch a wrong tool rather than pass it.
So the commit is safe to compile and run as it stands. Two things before pressing go. First, the run must start only
when the training queue is idle; the spec requires it and nothing in the three scripts checks it (M4), so either the
operator confirms it by hand or the gate is added first. Second, two small changes are cheap before the build and cost
a partial re-run after it, because they change what the run writes: keep each pairing's CHECK examples (M3, a few lines
in the patch) and write the four block-split files section 4 names (M1, a loop change in `run_b2e_rows.sh`). READING.md
(M2) and the eleven low items can wait until the run is read. Four medium findings, eleven low, none withdrawn.

## Findings, by severity

Severity scale: high = would produce wrong games, a wrong seed or deal convention, a silent change to default behaviour,
or an identity check that could pass while the tool is wrong; medium = spec deviation or missing step; low = hygiene.

### Medium

**M1. The run folder and files differ from section 4 (declared in the folder README).**
- Where: `run_b2e_rows.sh:11` (`D=".../b2e_rows_2026-09-26"`) and `:47-52` (one
  `--games-out "$D/b2e_$bot.jsonl"` per pilot over all 96 rows); the same `D=` at `build_b2e_scan.sh:12` and
  `run_b2e_identity.sh:30`; `read_b2e.py:82, 170` (reads `b2e_{pilot}.jsonl`), `:250-251` (splits blocks by pairing
  number, 0-47 lists and 48-95 Dustin's), `:450` (writes `b2e_tables.md`); `README.md:109, 111-115` (the disclosure).
- Spec section 4 "Run folder and files": `rl/results/b2e_runs_<date>/`, `run_b2e.sh`, and four per-game pairs
  `b2e_k3_arch`, `b2e_kp3_arch`, `b2e_k3_dustin`, `b2e_kp3_dustin` `.{txt,jsonl}`, plus `READING.md`.
- What it costs: the folder name and the three-script split cost nothing (the split is better: each step gates the
  next). The two-files-per-pilot choice does cost something beyond the name: the scan keeps at most four examples
  per finding code for the whole run (`patched.rs:50` `EXAMPLES_KEPT = 4`, `:72-76`, merged at `:652-654`, printed
  `:656-665`), so one log per pilot gives a reader half the examples per block that four logs would.
- Fix, either of: (a) match the spec: in `run_b2e_rows.sh:47-52` run each pilot twice with the existing filter,
  `--pairings 0,1,...,47` to `b2e_${bot}_arch.{txt,jsonl}` and `--pairings 48,...,95` to
  `b2e_${bot}_dustin.{txt,jsonl}` (same seeds, same games, no extra cost: `read_pairs` still checks every row's
  `seed_first` before the filter at `patched.rs:583` skips a pairing), extend the "no finished file" gate at `:35` to
  the four names, and let `b2e_checks.check_rows` (`b2e_checks.py:199`, `files: {pilot: path}`) and `read_b2e.py:170`
  take a list of paths per pilot, loading all of them before the existing per-pilot checks (the "per-game findings =
  the log's section" check then sums two logs per pilot); or (b) keep the layout and state the mapping to section 4's
  names in one line of READING.md and one line of the spec README section 4, and in the START_HERE seed row when it
  is added. (b) is enough for the names; (a) also fixes the halved examples.

**M2. READING.md is not produced.**
- Where: `read_b2e.py:449-453` writes `b2e_tables.md` and `b2e_summary.json` only; `README.md:109`: READING.md "is
  still to be written by whoever reads the run".
- Spec section 4: `READING.md` with section 5's tables filled in, citing the README as the specification, with the
  `python lib/deck_check.py files` output pasted in.
- Fix: have `read_b2e.py` also write `READING.md`: a header citing `../b2e_card_check_2026-09-26/README.md` sections 4
  and 5, the binary's sha256, the `IDENTITY PASS` and `ROWS PASS` lines, then the same tables, the findings sections,
  `deck_check.txt` and `timing.txt` (all already assembled at `:425-447`), with a clearly marked empty block per CHECK
  code for "the card that may allow it", the one part that needs a human. The folder is then complete when the run
  finishes.

**M3. Each pairing's CHECK examples are lost; section 4's "CHECK is listed with its example" cannot be met per pairing.**
- Where: patch `:176-182` (`patched.rs:641-647`): the per-game JSON carries `findings` as code -> count only. Examples
  are kept four per code for the entire run (`patched.rs:50, 72-76`) and pooled across all 96 pairings by
  `all.merge(r.findings)` at `:653`; `read_b2e.py:430-438` can only paste that pooled section.
- Spec section 4: "Report findings per pairing ... CHECK is listed with its example and the card that may allow it."
  A code that first appears in pairing 3 uses up its four examples there; the same code in pairing 70 has none.
- Fix: in `--pairs` mode, fold each pairing's results into a per-pairing `Findings` and print that pairing's section
  (code, occurrences, games, examples) right after its per-pairing line inside the loop (`patched.rs:581-594`), before
  merging into `all`; or add `"finding_examples": {code: first example}` to each JSON line in `--pairs` mode (the
  strings already exist in `r.findings.examples`). Then `read_b2e.py` lists each CHECK with its own pairing's example.
  Cheap before the build; after the run it means replaying the affected pairings.

**M4. Nothing enforces "run when the network training has finished, not beside it"; the build and the scans are uncapped.**
- Where: `build_b2e_scan.sh:63` (`nice -n 10 cargo build --release --locked --example legality_scan`, no job cap);
  `run_b2e_rows.sh:1-8` (header says nothing about training) and `:49` (the scan under `nice -n 10` only; its rayon
  loop uses every core, patch `:152`, 7fc6ccb `:502`); `run_b2e_identity.sh:25-26, 96, 108` (8,000 games the same
  way). The only statement of the rule is `README.md:15` ("when the laptop is free"); the commit message says "Runs in
  the overnight queue after the kpr rows", but no file in the repo encodes that order.
- Spec section 4 "Time": run it when the network training has finished, not beside it. Tonight's near-OOM is the
  reason this is medium rather than low. (Observation, not a gate: at 03:25 a `pgrep` for `run5-venv/bin/python`,
  `cargo` and `rustc` found nothing.)
- Fix: one `idle_or_die` function at the top of all three scripts, e.g.
  `if pgrep -f 'run5-venv/bin/python' >/dev/null || pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; then die "training or a build is running: B2e never runs beside it"; fi`
  (take the training pattern from the actual launcher under `rl/runs/`; optionally also refuse while any
  `rl/runs/*/STATUS.txt` says a run is still going); build with `-j 2` (or `CARGO_BUILD_JOBS=2`) and keep `nice`;
  run the scans with `RAYON_NUM_THREADS=$(( $(nproc) - 2 ))`; put the rule in each script's header and in README
  "How" ("the operator confirms the queue is idle first").

### Low

**L1. `--seed-base` without `--pairs` is accepted and reseeds a table-shaped run with no sign in the log; `--root` without `--pairs` is silently ignored.**
- Where: `patched.rs:557-562` (patch `:117-123`): only `--pairs` is guarded; `:558` reads `--root` always but only
  `read_pairs` uses it; `:577-579`: the "pairings from ... seed base ..." line prints only with `--pairs`. Allowed by
  the spec's "without either flag ... as today" wording; the `seed` field records the base, so it is not silent in
  the JSON, but such a file would look like a table file.
- Fix: beside the two guards at `:559-562`, `assert!(pairs_file.is_some() || arg(&args, "--seed-base").is_none(), "--seed-base is only for --pairs")`
  and `assert!(arg(&args, "--root").is_none() || pairs_file.is_some(), "--root is for --pairs")`; or print
  `seed base {seed_base}` on the first log line whenever it differs from `SEED_BASE`.

**L2. Identity step (b) would FAIL, not pass, on a table game that carries a per-game `findings` key; it cannot fire today.**
- Where: `run_b2e_identity.sh:114` (`same --drop a_file,b_file`); `b2e_checks.py:135-141` (the dropped keys must be
  present and every other key is compared); `patched.rs:644-646` adds `findings` in `--pairs` mode when a game has
  any. All five official logs end "Findings ... none" (`engine_identity_2026-09-25/{k3,kp3}_500.txt`, the table's
  `k3_500.txt`, the pricing `kp3_500_worst5.txt` and `kp3_500_rest.txt`), so no table deal has one; the strictness
  currently doubles as a "still no findings on table deals" check. Safe direction, but a future FAIL there would say
  "differs" with no hint why.
- Fix: make `same` print the keys that differ (`set(new) ^ set(ref)` and per-key mismatches) so such a FAIL is
  diagnosed at once; and either say in the script header that (b) relies on the table's zero findings, or drop
  `findings` as optional there and check the summed findings against the log with `log_findings` instead.

**L3. The official `deckgym` and `legality_scan` hashes are recorded, not asserted.**
- Where: `build_b2e_scan.sh:76-77` write whatever `sha256sum` says for `rl/engine-2026-09-25/{deckgym,legality_scan}`
  into `identity.txt`; `run_b2e_identity.sh:73` records the reference files' hashes the same way. Both official files
  hash to the spec's values today (checked), so a replaced file would be recorded, not refused.
- Fix: `[ "$(sha256sum "$R/rl/engine-2026-09-25/deckgym" | cut -d' ' -f1)" = f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034 ] || die "official deckgym is not the spec's"`
  and the same for `legality_scan` against `d5c0a9528e076299875ac603667f7076951de885ea8465f3be0d1089b5afbbfb`.

**L4. The `--pairs` replay uses the default base, so it cannot show a non-default `--seed-base` is honoured.**
- Where: `run_b2e_identity.sh:38` (`TABLE_BASE=72000000`, equal to `SEED_BASE`, 7fc6ccb `:35`) and `:108`. A patch
  that parsed the flag and ignored it would pass (b). What does cover it: guard (c) at `:90` (`--seed-base 72000001`
  must be refused through `read_pairs`' `seed_first` check, `patched.rs:527-530`, so the parsed value reaches the row
  reader), and `b2e_checks.py:234` checks every seed against base + 10,000p + i after the run (the JSON `seed` is the
  value passed to `Game::new`, `patched.rs:402, 408`). A wrong base would be found after about 3.4 hours of games
  rather than before.
- Fix (optional, one minute of games, no new seeds): a probe TSV whose pairing 0 is table pairing 1's decks
  (`decks/research/altaria.txt` v `decks/research/hydreigon.txt`) with `seed_first` 72,010,000, run with
  `--seed-base 72010000 --games 500`; its seeds are table pairing 1's deals, so its `moves` per deal must equal
  `ref_k3.jsonl`'s pairing-1 lines keyed on `i`.

**L5. Identity step (a) compares the per-game lines only, not the log's findings section or per-pairing lines.**
- Where: `run_b2e_identity.sh:96-103`. In default mode the JSON carries no findings (7fc6ccb `:543-556`); they are
  printed in the log (`:564-573`). The official logs say "none" (`engine_identity_2026-09-25/k3_500.txt:46`,
  `kp3_500.txt:46`). The check code is untouched by the patch, so this is a completeness gap, not a likely failure.
- Fix: after each default replay, require the findings section of `identity_$bot.txt` to be exactly `  none` and
  diff its four per-pairing lines against the same lines of `engine_identity_2026-09-25/<bot>_500.txt` (`grep -F` on
  "altaria v blaziken", "altaria v suicune", "blaziken v sceptile", "hydreigon v sceptile").

**L6. The pairings file and the six archetype lists are compared to HEAD, not to a pinned commit.**
- Where: `build_b2e_scan.sh:31` (`git show "HEAD:$TSV" | cmp -s - "$TSV"`) and `:40` (the same per deck file). A
  later commit that edits a list would be accepted silently. Traceable afterwards: `inputs_sha256.txt` goes into
  `identity.txt` (`:80-81`), `inputs_source.txt` names the last commit touching each file (`:48`), and
  `run_b2e_rows.sh:29-33` re-checks the played copies against those hashes.
- Fix: pin the expected sha256 of the TSV and the six lists (as committed before 8aa6ea3) in the build script, or
  assert `git log -1 --format=%h -- "$f"` equals the commit the spec was written at.

**L7. No `--games <= 10,000` guard; the TSV's `seed_last`/`sub_block_end` columns are ignored.**
- Where: `patched.rs:402` (`seed_base + pairing as u64 * 10_000 + i`, no bound on `i`), `:545` (`--games` parsed
  unbounded), `:512-513, 527-530` (`read_pairs` reads only `pairing`, `held_key`, `held_file`, `opponent`,
  `panel_file` and the optional `seed_first`). A `--games` above 10,000 would spill into the next pairing's sub-block
  silently, as the unpatched tool would. The scripts pass 500; `b2e_checks.py:234` catches a seed past `seed_last`
  only after the run.
- Fix: in `main`, `assert!(games <= 10_000, "a pairing's sub-block holds 10,000 seeds")`; or in `read_pairs`, when a
  `seed_last` column exists, assert `seed_first + games - 1 <= seed_last` (pass `games` in).

**L8. The games-out file is created before the TSV is validated and the decks load.**
- Where: `patched.rs:563-564` creates `--games-out`, then `:565-573` runs `read_pairs`; a rejected TSV or a missing
  deck file leaves an empty `b2e_<bot>.jsonl`, which `run_b2e_rows.sh:35` then refuses to overwrite ("move it away").
  Not a behaviour change: the unpatched tool also created the file before loading decks.
- Fix: in `run_b2e_rows.sh`, write to `"$D/b2e_$bot.jsonl.part"` and `mv` into place only on exit 0 (or remove an
  empty output file in `die`).

**L9. Seed arithmetic is unchecked.**
- Where: `patched.rs:402` and `:528` (`pairing as u64 * 10_000`). Correct for p <= 95 (largest seed 21,106,950,499,
  far inside u64), but an absurd `pairing` value in a TSV would wrap silently in a release build.
- Fix: in `read_pairs`, `assert!(pairing < 100_000, "pairs file {path}: pairing {pairing} is out of range")`, or
  `checked_mul`/`checked_add` with `.expect("seed overflow")`.

**L10. Pre-existing: `arg()` returns whatever token follows a flag.**
- Where: `patched.rs:501-503`. `--pairs --seed-base 5` would read `--seed-base` as the pairs path (the file open then
  fails loudly). The scripts always pass values.
- Fix (optional): in `arg()`, return `None` (or panic) when the following token starts with `--`.

**L11. The `--pairs` log line prints "deck paths relative to ..", which does not say which tree was read.**
- Where: `patched.rs:578`, with `root` defaulting to `..` (`:558`).
- Fix: print `std::fs::canonicalize(&root).map(|p| p.display().to_string()).unwrap_or(root.clone())` so the log
  shows `/home/dacz8976/engine-b2e-7fc6ccb`.

## Raised and withdrawn

None. Every item the three lenses raised survived verification; no lens reported a refuted item.

## What was verified fine (so nobody re-checks it)

The patch and the default path
- `review/legality_scan_7fc6ccb.rs` is byte-identical to `git show 7fc6ccb:engine/examples/legality_scan.rs`
  (sha256 7332d4c0...); the patch applies cleanly to it (`git apply --check` and a real apply in scratch, +104 -12,
  one file, `engine/examples/legality_scan.rs` only) and the result is byte-identical to
  `review/legality_scan_patched.rs`; `git apply --check` in the repo also passes. `engine/` is unchanged between
  7fc6ccb and HEAD.
- Every changed hunk walked against 7fc6ccb: without `--pairs` or `--seed-base` the program loads the same eight
  `NAMES` decks in the same order, enumerates the same 28 pairs in the same order, uses `SEED_BASE` = 72,000,000,
  computes the same seed (`patched.rs:402` = reference `:373`, `as` binds before `*`), the same seats (`:403-404`),
  the same players, the same example strings, the same per-game JSON keys and values (keys are emitted sorted by
  serde_json's BTreeMap, so a key added only in `--pairs` mode cannot reorder default lines), and the same summary.
  The game loop, `check_offered`, `check_state`, the Hyper Ray and Chase Order counters and the fingerprint are
  untouched (no hunk there). The seed is computed once and used once (`Game::new`); no other RNG.
- Compiles in principle (by reading): `Deck::from_file(&str)` matches (`engine/src/deck.rs:31`), the borrows and
  closures in `read_pairs` are legal, `json!` takes references, the `par_iter` closure captures `&Lineup` as the old
  `&[Deck; 8]` did, `HashSet` is already imported. Not compiled here, by the rule; the commit message says so too.

The `--pairs` path
- TSV read by column name (`pairing`, `held_key`, `held_file`, `opponent`, `panel_file` required, `seed_first`
  optional), BOM and CRLF tolerated, blank lines skipped, short rows and duplicate pairings refused, rows in file
  order, `Row.pairing` = the file's number (not the row index) for the seed and for the `--pairings` filter.
- Held deck first-named and in seat 0 on even i through the unchanged `play_one`; `a` = `held_key`, `b` =
  `opponent`; files in `a_file`/`b_file`.
- `--pairs` requires an explicit `--seed-base`, refuses `--decks`, checks every row's `seed_first` against base +
  10,000p, all before the games-out file exists or a deck loads. Deck paths resolve against `--root` (default `..`,
  which is the scratch tree's root when run from `$B/engine`, as both scripts do); an absolute path is used as is.
- `b2e_pairings.tsv`: header + 96 rows, pairings 0-95 in section 4's order (p = 8d + o, +48 for block B),
  `seed_first` = 21,106,000,000 + 10,000p, `seed_last` = `seed_first` + 499, `sub_block_end` = `seed_first` +
  9,999 (recomputed: 0 bad rows; largest seed used 21,106,950,499). The block lies outside every START_HERE range
  (nearest 21,101,300,001 below and 22,000,000,000 above); sub-blocks 96-99 are never touched. The seed-table row is
  drafted in `README.md:117-121` and START_HERE is not edited, as the spec asks.

The build
- `git archive 7fc6ccb engine decks` into a fresh folder outside the repo (refuses an existing one); the card
  database is compiled-in generated code, so `engine/` is a complete build tree; `--locked` against 7fc6ccb's
  committed `Cargo.lock`. The 14 deck files 7fc6ccb has must equal the working copy's (they do); the six `h-*.txt`
  lists and the TSV are copied only after `cmp` against HEAD; `inputs_sha256.txt` and `inputs_source.txt` record
  what was played and where it came from. `identity.txt`'s first line is the binary's sha256, then the patch's, the
  official `deckgym`'s and `legality_scan`'s, the toolchain, and every input's hash.

The identity check
- Pairings 0, 5, 13, 23 x 500 deals for k3 and kp3 (the spec's minimum), k3 against
  `per_game_table_2026-09-25/k3_500.jsonl`, kp3 against `public_pricing_2026-09-25/kp3_500_worst5.jsonl` (pairings 0,
  2, 9, 13, 23) plus `kp3_500_rest.jsonl`; each reference first cut to exactly 2,000 games with the pilot fields
  checked (`b2e_checks.py subset`). The compare is the Sept 25 `compare.py` itself (sha256 recorded), nine fields
  including the move hash, keyed by (pairing, i); a missing or short file fails loudly (exit 1, and the script also
  greps for "2,000 of 2,000", "only in new: 0; only in reference: 0" and "RESULT: IDENTICAL").
- Stricter than asked: byte-for-byte equality with the official 7fc6ccb scan's own lines
  (`engine_identity_2026-09-25/{k3,kp3}_500.jsonl`, which carry `chase_order`; the table references predate it), so
  `hyper_ray`, `chase_order` and the absence of any added key are covered; then the same deals replayed through
  `--pairs` with `--seed-base 72000000` (no new seeds); then the three refusals. On any failure the script writes
  `IDENTITY FAIL: ...` and exits 1; the PASS line carries the binary's hash.
- The rows script (`run_b2e_rows.sh:21-36`) refuses without the PASS line for this exact sha256, without
  `identity.txt` naming it, if the repo's TSV changed since the build, if any of the 21 played copies no longer
  hashes as recorded, or if a finished output exists; the reader (`read_b2e.py:81-95`) repeats the PASS gate,
  requires `rows_check.txt` to name the same binary and carry `ROWS PASS`, and re-runs the rows check.

The rows and the rows check
- 96 pairings x 500 deals, k3 then kp3 on the same deals, `--pairs <TSV> --seed-base 21106000000 --games 500
  --bot <pilot>`, each with its `.txt` log and a `timing.txt` line (wall seconds, cores, end time).
  `deck_check.py files` runs on the twelve held files as played, before any game, output to `deck_check.txt`.
- `b2e_checks.py rows` requires 96 x 500 lines per file, one per (pairing, i), every spec field plus
  `a_file`/`b_file`, a 16-hex-digit `moves`, seed = `seed_first` + i = base + 10,000p + i and not past `seed_last`,
  `first_seat` = i mod 2, `a`/`b`/files as the TSV row, `bot_a` = `bot_b` = the pilot, score consistent with the
  winner (0.5 on a draw, matching 7fc6ccb `:445-448`), k3 and kp3 on the same (pairing, i, seed) set, and per-game
  findings summed = the log's findings section (the parser handles codes containing ": "). No mixed rows, never jev.

The reader (section 5)
- Cell = mean of `first_deck_score` x 100 with ties counted; panel score = equal-weight mean of the eight cells
  with band 1.96 sqrt(sum p(1-p)/n)/8 (`panel_bands.py`'s formula), under k3 and kp3, list and Dustin's file; gap =
  panel minus the Limitless equal-weight average, pooled (the reference) and development beside it, Whimsicott's
  development gap over its seven development opponents; per-cell miss = sim minus pooled, "beyond" when |miss| >
  sqrt(band_L^2 + band_S^2) with band_S from the simulator's own p at 500 games; one-sided Limitless cells read as
  "no information"; bands over 15 marked wide; the known sceptile/vespiquen/altaria misses noted, not fixed; list
  difference per pilot; veto baseline |kp3 - L| with k3 beside it; A2's bar on kp3, block A, against the pooled 3.7
  intervals, stated not applied. RULE findings withhold the cell and every panel score that needs it. The Limitless
  cells and averages are recomputed from `limitless_cells.csv`'s W-L-T-n and checked against its rounded columns;
  `check_layout` re-derives d, o and the key for every TSV row before anything is read; the "untrusted-prone" flags
  match section 6's table. "kp3 minus k3 paired by deal" is an addition the spec does not ask for; harmless.

Hygiene that is fine
- Every committed file, the patch and the TSV are LF with no CR. Nothing is written outside the results folder
  except the scratch build tree in `/home/dacz8976/engine-b2e-7fc6ccb` (as the kpr build did); no `__pycache__`.
  Absolute `R`, `D`, `B` paths as in `build_kpr_scan.sh`; `BASE`/`GAMES` appear in the rows script, the reader and
  the TSV, and the rows check ties all three together. Deck lists come only from the TSV.

## Outside the commit (not findings against it)

- START_HERE's "20,000,000,000+" row ends "new blocks go above the last one used" (22,599,999,999), while the spec
  says 21,106,000,000 lies outside every listed range; both are true, and the README drafts the seed-table row. A
  spec wording matter, mine to settle, not the commit's.

## Paste-ready message for the laptop session

```
From Fable (review session), Sept 26, 03:25. Review of your commit 8aa6ea3 (B2e rows) against the spec,
rl/results/b2e_card_check_2026-09-26/README.md sections 4 and 5. Full text with every line reference:
rl/results/fable_reviews_2026-09-26/b2e_rows_review.md (three lens notes beside it). Read only; nothing compiled
or run, per tonight's no-build rule.

Verdict: no high finding. The patch does what section 4 asks and leaves the default run unchanged hunk for hunk;
--pairs seeds at base + 10,000p + i with the held deck first-named and in seat 0 on even deals; the identity check
is stronger than asked and the rows script and reader gate on its PASS line and the binary's sha256. Safe to
compile and run as is, once the queue is idle. Four medium items, eleven low, none withdrawn. You own the code
and decide.

Medium
M1 Layout differs from section 4 (declared): b2e_rows_2026-09-26/ not b2e_runs_<date>/, three scripts, two files
   per pilot not four, b2e_tables.md not READING.md (run_b2e_rows.sh:11, 47-52; read_b2e.py:170, 250-251, 450;
   README.md:111-115). The two-file choice also halves per-block examples (EXAMPLES_KEPT = 4 per code per run,
   patched.rs:50, 72-76, 653). Fix: run each pilot twice with --pairings 0..47 / 48..95 into the four files and
   let check_rows and the reader take a list per pilot; or keep it and state the mapping in READING.md and spec
   section 4, one line each.
M2 READING.md not produced (read_b2e.py:449-453; README.md:109). Fix: have read_b2e.py write it too: header
   citing the spec, sha256, PASS lines, the tables, findings sections, deck_check.txt, timing.txt, and an empty
   block per CHECK code for "the card that may allow it".
M3 Per-pairing CHECK examples are lost: JSON findings are code -> count only (patch 176-182), examples pooled
   four per code per run (patched.rs:50, 72-76, 653). Fix, before the build: print each pairing's findings section
   after its line in the loop (patched.rs:581-594), or add "finding_examples" per JSON line in --pairs mode.
M4 Nothing checks the trainer is idle; no job or thread cap (build_b2e_scan.sh:63; run_b2e_rows.sh:1-8, 49;
   run_b2e_identity.sh:96, 108; README.md:15 only). Fix: idle_or_die (pgrep run5-venv python / cargo / rustc)
   at the top of all three, cargo -j 2, RAYON_NUM_THREADS=$(( $(nproc) - 2 )), the rule in each header.

Low (one line each; details in the file)
L1 --seed-base and --root accepted without --pairs, base not in the log (patched.rs:557-562, 577-579): assert
   or print it.
L2 same --drop a_file,b_file would FAIL on a table game with a findings key (b2e_checks.py:135-141; identity
   :114); safe direction, cannot fire today: make same print the differing keys, note it in the header.
L3 Official deckgym/legality_scan hashes recorded, not asserted against the spec's (build :76-77): compare.
L4 --pairs replay uses base 72,000,000 = SEED_BASE (identity :38, :108), so it cannot show a non-default base is
   honoured; guard (c) and the rows check cover it late. Optional probe TSV, one minute of games.
L5 Identity (a) ignores the log's findings section and per-pairing lines (identity :96-103): require "none" and
   diff the four lines.
L6 Inputs compared to HEAD, not a pinned commit (build :31, :40): pin the hashes.
L7 No --games <= 10,000 guard; seed_last ignored (patched.rs:402, 545): assert.
L8 games-out created before the TSV is validated (patched.rs:563-573), leaving an empty file the rows script
   refuses to overwrite (:35): write .part and mv on success.
L9 Unchecked seed arithmetic (patched.rs:402, 528): assert pairing < 100_000.
L10 Pre-existing: arg() takes the next token even if it is a flag (patched.rs:501-503): optional.
L11 Log says "relative to .." (patched.rs:578): print the canonical path.

Verified fine, no need to re-check: patch applies to 7fc6ccb byte for byte and touches one file; default path
unchanged (decks, pairs, SEED_BASE, seats, JSON keys, checks, summary); --pairs reader and guards; seeds inside
sub-blocks 0-95 of 21,106,000,000 and outside every START_HERE range; identity replay on 0,5,13,23 x 500 per pilot
against the right references with the Sept 25 compare.py, plus byte-for-byte, --pairs replay and refusals; rows
and reader gates; rows check; deck_check before the games; section 5 arithmetic; LF files; nothing written
outside the folder and the scratch tree.
```
