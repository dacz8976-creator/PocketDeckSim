# B2e rows: review of commit 8aa6ea3, lens = the Rust patch (Fable, Sept 26, 2026)

Reviewed by reading only. No cargo, no binary, no game, no background process. Read-only on the repo apart from
this file. Scratch: `.../scratchpad/b2e_review/` (three bash scripts run through WSL: `git show`, sha256, a dry-run
`git apply --check` in a temp folder, `diff -u`).

**Verdict in one line:** the patch does what section 4 asks and, by reading, leaves the default path byte for byte
as it was; no high finding. One acknowledged spec deviation (folder and file names) and a handful of hygiene notes.

## 1. What was established before reading the code

| Fact | How |
|---|---|
| `review/legality_scan_7fc6ccb.rs` is byte-identical to `git show 7fc6ccb:engine/examples/legality_scan.rs`, and so is the working tree's `engine/examples/legality_scan.rs` (HEAD did not touch the file after 7fc6ccb) | sha256 `7332d4c0…` for all three; `git diff --stat 7fc6ccb HEAD -- engine/examples/legality_scan.rs` empty |
| `legality_scan_pairs.patch` applies cleanly to 7fc6ccb's file (`git apply --check` exit 0, `patch --dry-run` exit 0, in a temp copy outside the repo) and the result is byte-identical to `review/legality_scan_patched.rs` | sha256 `3284e42c…` for both |
| The commit only adds files under `rl/results/b2e_rows_2026-09-26/`; it does not edit the engine | `git show --stat 8aa6ea3` |
| Working tree = commit for every tracked file (only untracked ko_audit/kt_carrier files differ) | `git status --porcelain`, `git diff --stat HEAD` empty |
| Every committed file, the patch and the TSV are LF; the jsonl references carry no CR | `grep $'\r'`, `tr -cd '\r' | wc -c` |
| `b2e_pairings.tsv`: header + 96 rows, pairings 0–95 in section 4's order, `seed_first` = 21,106,000,000 + 10,000 × p, `seed_last` = seed_first + 499 | read in full |
| The 20 deck files the TSV names: 14 exist in 7fc6ccb and equal the working copy; the six `h-*.txt` are not in 7fc6ccb, are committed, and equal HEAD | `git cat-file -e`, `cmp` |
| `decks/research/`, `decks/screen/opponents/`, the five `decks/dustin/*` files, `decks/brews/brew-08-entei-rainbow-cave.txt` and `engine/Cargo.lock` all exist at 7fc6ccb (`git archive 7fc6ccb engine decks` and `--locked` will work) | `git ls-tree 7fc6ccb` |
| The official Sept 25 logs (identity `k3_500.txt`, `kp3_500.txt`; table `k3_500.txt`; pricing `kp3_500_worst5.txt`, `kp3_500_rest.txt`) all end "Findings … none"; no per-game `findings` key exists in the official jsonl | `sed`/`grep` |
| Per-game JSON keys are emitted sorted (serde_json's default BTreeMap map; the reference lines show `a, b, bot_a, …, winner_seat`), so a key added only in `--pairs` mode cannot reorder default-mode lines | reference jsonl first lines; `engine/Cargo.toml` at 7fc6ccb has `serde_json = "1.0"` with no `preserve_order` |

## 2. Default path, hunk by hunk (neither `--pairs` nor `--seed-base`)

Reference = `git show 7fc6ccb:engine/examples/legality_scan.rs` (line numbers R), patched = `review/legality_scan_patched.rs` (P).

| Reference | Patched | Same behaviour? |
|---|---|---|
| R32–35 `NAMES`, `SEED_BASE = 72_000_000` | P46–49 unchanged | yes |
| R370–373 `play_one(decks: &[Deck; 8], pairing, i, …)`: `pairs[pairing]`, `seed = SEED_BASE + pairing as u64 * 10_000 + i` | P401–402 `play_one(lineup, pairing, (a, b), i, …)`: `seed = lineup.seed_base + pairing as u64 * 10_000 + i`; `(a, b)` passed by the caller | yes: caller builds rows from the identical `pairs` list in the identical order (P568–569); `seed_base` = `SEED_BASE` when the flag is absent (P557); `as` binds tighter than `*`, so the arithmetic is the same u64 expression |
| R374–379 first_seat = i % 2, d0/d1, codes, `create_players(decks[d0].clone(), decks[d1].clone(), codes)`, `Game::new(players, seed)` | P403–408 identical apart from `lineup.decks[..]` | yes; `Vec<Deck>` holds the same eight decks loaded from `{dir}/{n}.txt` in NAMES order (P567) |
| R399 `NAMES[d0], NAMES[d1]` in the example text | P428 `lineup.names[d0], lineup.names[d1]` | yes; same strings (P570), `String` prints as `&str` |
| R406–470 game loop, `check_offered`, `check_state`, `update_turn`, Hyper Ray and Chase Order counters, fingerprint | untouched (P435–499; `diff -u` has no hunk there) | yes |
| R478–491 flag parsing, bot checks, jev refusal, `games_out` creation | P544–564: the same, plus P556–562 reading `--pairs`, `--seed-base`, `--root` and two asserts that fire only when `--pairs` is given | yes; with no new flag no assert fires and the order of side effects (bot check → games-out file → deck load) is the same as before |
| R492–493 decks `[Deck; 8]` and `pairs` | P566–571 the `None` arm: same loads, same `expect("deck file")`, same `pairs`, enumerated into `rows` with `files: None` | yes |
| R495–496 header line | P575–576 unchanged; P577–579 adds a line only with `--pairs` | yes |
| R498–509 `for (p, (a, b)) in pairs.iter().enumerate()`, `--pairings` filter, `results`, score, flagged, distinct, print | P581–594 `for row in &rows`, same p/a/b, same filter, same print with `lineup.names[a]` (`{:>9}` pads a `String` the same way) | yes |
| R510–538 Hyper Ray and Chase Order summaries | untouched | yes |
| R543–548 per-game JSON | P628–633 same keys, `lineup.names[a]` for `a`/`b` (to_value of a `String` equals to_value of a `&str`) | yes |
| R549–555 optional `hyper_ray`, `chase_order` | untouched; P641–647 adds `a_file`, `b_file`, `findings` only when `row.files` is `Some`, which is only in `--pairs` mode | yes |
| R564–573 findings summary | untouched | yes |

Seed census of the patched file (grep "seed"): the seed is computed once (P402), used once (`Game::new`, P408), printed in the example text (P427) and in the JSON (P488→P629). There is no other RNG, no `--seed-stream`, and the legality checks take no seed. `SEED_BASE` appears only as the default (P557) and in a comment.

## 3. `--pairs` path, against the lens questions

- **TSV parsing (P505–540).** BOM stripped; `str::lines()` strips `\r\n`, so CRLF is tolerated silently; blank lines skipped; the header is parsed by column name (`pairing`, `held_key`, `held_file`, `opponent`, `panel_file` required, `seed_first` optional); every field trimmed; a row shorter than the header panics with the row text; a pairing that fails to parse or repeats panics; an empty file panics. Column positions are not assumed, so `block`, `seed_last`, `sub_block_end` may sit anywhere or be absent.
- **Pairing number.** `Row.pairing` is the file's `pairing` column (P525, P536), not the row index; the seed (P402) and the `--pairings` filter (P583) use it. Identity step (b) runs a four-row file (0, 5, 13, 23) whose seeds must equal the table's, which proves this in practice.
- **Held deck first, seat 0 on even i.** `held_file` is pushed first (`a`, P531–532), `panel_file` second (`b = a + 1`, P534–536); `play_one` puts `a` in seat 0 when `first_seat == 0`, that is for even i (P403–404). Same convention as the table.
- **Labels.** `a` = `held_key`, `b` = `opponent` (P533, P535, P629); the file paths go to `a_file`/`b_file` (P641–643).
- **Seed.** `seed_base + pairing as u64 * 10_000 + i`, all u64; 21,106,000,000 + 950,000 + 499 is far below u64's range. No use of the old base anywhere on this path. The optional `seed_first` cross-check (P527–530) compares the parsed column with `seed_base + pairing × 10,000`; a non-numeric value gives `None` and fails.
- **Guards (P559–562).** `--pairs` refuses a missing `--seed-base` and a `--decks`, before the games-out file is created and before any deck is read. The default `--seed-base` is `SEED_BASE` = 72,000,000 (P557), not 21,106,000,000, so the identity replay with default flags runs on the table's seeds and B2e can never fall back onto them by accident.
- **Paths.** `Path::new(root).join(file)` (P515); `--root` defaults to `..` (P558). The TSV's paths are repo-root-relative; the scripts run the scan from `$B/engine` where `$B` mirrors the repo layout (`git archive 7fc6ccb engine decks` plus the copied TSV and deck files, `build_b2e_scan.sh:28–44`), so `..` is `$B`. An absolute `file` overrides `root` (std `join` semantics), as the doc says. `Deck::from_file` reads relative to the process cwd (`engine/src/deck.rs:31–33`), consistent with this.
- **Per-game `findings` (P644–646)** is `Findings.count` (occurrences per code) for a game that has any; `b2e_checks.py:246–249, 262–265` sums occurrences and games-affected and compares with the log's summary, which is what `Findings::merge` (P62–77) prints. Consistent.

## 4. Compiles in principle (by reading)

- `Deck::from_file(file_path: &str) -> Result<Self, String>` (`engine/src/deck.rs:31`): the `{e}` in the panic needs `Display`, which `String` has; `full: &str` matches the parameter.
- `let full = full.to_str().expect(..)` shadows a `PathBuf` with a `&str` that borrows it; the `PathBuf` lives to the end of the closure, so this is legal.
- Closures `col`/`need`/`load` hold only shared borrows of `header`, `path`, `root`; `lineup` and `rows` are mutated separately; `lines` is `mut` for `next()` then consumed by `for`.
- `match &pairs_file { None => …, Some(path) => read_pairs(path, &root, seed_base) }`: `&String` coerces to `&str`; both arms return `(Lineup, Vec<Row>)`.
- `json!(file_a)`, `json!(r.findings.count)`: the macro's expression arm calls `to_value(&expr)`, so nothing is moved out of `row` or `r`.
- The par_iter closure captures `&Lineup`, which needs `Deck: Sync` exactly as the old `&[Deck; 8]` did.
- Inline format captures mixed with a positional `{:?}` (P525) are allowed. `assert_eq!` with a message and `Option<u64>` operands is fine.
- No clap: the tool keeps its hand-rolled `arg()` (P501–503); the doc header (P22–34) matches the flags read at P544–558.

## 5. The identity check and the compare

- `run_b2e_identity.sh:35` uses the very file `rl/results/engine_identity_2026-09-25/compare.py` (its sha256 is written to `identity_check.txt`, line 73). It compares `a, b, seed, first_seat, moves, winner_seat, points, turns, first_deck_score` (`compare.py:14`), the move hash included, keyed by (pairing, i).
- A missing file: Python raises in `load`, exit code 1 → `compare_ok` fails (`run_b2e_identity.sh:51–53`). A short file: the missing games count as "only in reference" → `RESULT: NOT IDENTICAL`, exit 1; and lines 54–56 additionally grep for `games in both: 2,000; … 2,000 of 2,000`, `only in new: 0; only in reference: 0` and `RESULT: IDENTICAL`. Loud in every case.
- Before compare.py, `b2e_checks.py subset` cuts each reference to exactly the four pairings × 500 deals and checks the pilot fields (lines 72–99); after it, `same` checks byte-for-byte equality with the official 7fc6ccb scan's own lines (lines 122–156), which covers `hyper_ray` (pairing 13 has Hydreigon) and `chase_order` (pairing 5 has it) and the absence of any added key.
- Step (b) replays the same four pairings through `--pairs` with `--seed-base 72000000` (lines 105–115) and step (c) tests the three refusals (88–90). `run_b2e_rows.sh:23–26` and `read_b2e.py:81–95` refuse without the `IDENTITY PASS <sha>` line for the binary named on `identity.txt`'s first line.
- The one place a wrong default would have mattered, P557, defaults to 72,000,000. `run_b2e_rows.sh:15` and `read_b2e.py:69` both carry 21,106,000,000 and the scan cross-checks it against the TSV's `seed_first` column on every row.

## 6. Findings

None high.

**M1 (medium, spec deviation, acknowledged).** Section 4 names the run folder `rl/results/b2e_runs_<date>/` with `run_b2e.sh` and four per-block files `b2e_{k3,kp3}_{arch,dustin}.{txt,jsonl}`; the commit uses `rl/results/b2e_rows_2026-09-26/`, three scripts, and two files `b2e_k3.jsonl` / `b2e_kp3.jsonl` (`run_b2e_rows.sh:11–13, 49–50`). The README says so (`README.md:113–114`) and the reader splits blocks by pairing number (`read_b2e.py:250–251`), so no number changes. Fix: leave the layout, but state the deviation and the folder name in `READING.md` (the spec says to cite the README as the specification), or rename to the spec's names before the run.

**L1 (low).** `--seed-base` without `--pairs` is accepted (P557) and replays the 28 table pairings on another block, while the "pairings from … seed base …" line prints only with `--pairs` (P577–579); the `.txt` log then says nothing about the base. Fix: print `seed base N` whenever `--seed-base` is given (default output stays unchanged), or refuse `--seed-base` without `--pairs`.

**L2 (low).** `--root` is read always (P558) but used only by `read_pairs`; without `--pairs` it is silently ignored. Fix: `assert!(arg(&args, "--root").is_none() || pairs_file.is_some(), "--root is for --pairs")`.

**L3 (low).** The scan ignores the TSV's `seed_last`/`sub_block_end` columns and has no `--games <= 10_000` guard (P545, P402), so a `--games` above 10,000 would spill into the next pairing's sub-block silently, as the unpatched tool would. The scripts pass 500 and `b2e_checks.py:234` catches a seed past `seed_last` after the fact. Fix: `assert!(games <= 10_000, "a pairing's sub-block holds 10,000 seeds")` in `main`, or check `seed_first + games - 1 <= seed_last` in `read_pairs` when the column exists.

**L4 (low).** The games-out file is created (P563–564) before `read_pairs` validates the TSV and loads the decks (P565–573); a rejected TSV or a missing deck file leaves an empty `b2e_<bot>.jsonl`, which `run_b2e_rows.sh:35` then refuses to overwrite ("move it away"). The unpatched tool also created the file before loading decks, so this is not a behaviour change. Fix: in `run_b2e_rows.sh`, remove the output file in `die` when it is empty, or write to `b2e_<bot>.jsonl.part` and rename on success.

**L5 (low).** Identity step (b) compares `--pairs` lines with the official lines after dropping only `a_file,b_file` (`run_b2e_identity.sh:114`); a game with a per-game `findings` key (P644–646) would fail as "differs" with no hint why. Today no table game has any finding (all five official logs read "none"), so this cannot fire now. Fix: make `same` name the keys that differ, or drop `findings` there as well and check it separately.

**L6 (low, hygiene).** `pairing as u64 * 10_000` (P402, P528) is unchecked arithmetic; correct for p ≤ 95, but an absurd `pairing` in a TSV would wrap silently in a release build. Fix: `checked_mul(10_000).and_then(|x| x.checked_add(seed_base))…expect("seed overflow")`, or `assert!(pairing < 100_000)` in `read_pairs`.

**L7 (low, pre-existing).** `arg()` (P501–503) returns whatever token follows a flag, so `--pairs --seed-base 5` reads `--seed-base` as the pairs path. The scripts always pass values. Fix (optional): reject a value that starts with `--`.

**L8 (low).** The `--pairs` log line prints `deck paths relative to ..` (P578), which does not say which tree was read. Fix: print `std::fs::canonicalize(&root)` when it resolves, so the log shows `/home/dacz8976/engine-b2e-7fc6ccb`.

## 7. Verified OK (no change needed)

- Default path byte-for-byte: NAMES, the pairs list, SEED_BASE 72,000,000, seat assignment, per-game JSON keys and values, the legality checks, the summary output (section 2).
- `--pairs`: header by name, tab-separated, trimmed, BOM/CRLF tolerated, blank lines skipped, short rows and duplicate pairings rejected, pairing column used as p (section 3).
- Held deck first-named and in seat 0 on even i; `a` = held key, `b` = opponent label, files in `a_file`/`b_file`.
- Seed = base + pairing × 10,000 + i in u64; the only seed use is `Game::new`; no other RNG; `--seed-base` reaches every seed; default base is the table's.
- `--pairs` requires an explicit `--seed-base`, refuses `--decks`, checks `seed_first`.
- Compiles in principle: types, borrows, closures and macros checked against `Deck::from_file`'s real signature.
- The compare is the Sept 25 `compare.py` itself, nine fields with the move hash, and fails loudly on a missing or short file; the byte-for-byte and `--pairs` replays and the refusal tests add to it; the rows script and the reader gate on the PASS line and the binary's sha256.
- The patch applies cleanly to 7fc6ccb, touches only `engine/examples/legality_scan.rs`, and the committed patched copy is what the patch produces.
- The TSV and its 20 deck files are committed and equal to 7fc6ccb where 7fc6ccb has them.

## 8. Notes outside the lens

- START_HERE's `20,000,000,000+` row ends "new blocks go above the last one used" (22,599,999,999), whereas the spec claims 21,106,000,000 lies outside every range; that is true of every listed sub-range, and the README drafts the seed-table row. A spec matter, not the patch's.
- The identity check plays 8,000 games and the rows 96,000; the scripts `nice` everything but do not check the training queue. Not reviewed here.
