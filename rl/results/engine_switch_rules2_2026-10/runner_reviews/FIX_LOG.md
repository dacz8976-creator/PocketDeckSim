# Fix log: the two reviews of the rules switch 2 runner copies (Oct 9, fixer)

Folder: `rl/results/engine_switch_rules2_2026-10/` (written below as `O/`). Line numbers are the copies' after these fixes.

**What I did not run.** Nothing was built, played, fetched, committed or pushed. I ran no runner and no dry run. My checks were:
- `bash -n` and `py_compile`;
- grep, diff and comm;
- read-only git on refs already fetched (tip 056158c3, main d9f867c7);
- one Python script that made the citation text edits (`fix_cites.py`).

**Syntax after the fixes:**
- `bash -n` passes on `sitting1.sh`, `sitting2.sh`, `checkpoint.sh`, `quiet.sh` and `pin/pin_rules.sh`.
- `py_compile` passes on `sitting1_check.py`, `sitting2_check.py`, `switch_check.py`, `floor_with.py` and `pin/update_manifest_rules.py`.
- shellcheck is not installed.
- No file has a CR. No `__pycache__` was left behind.

**Checked against git (read-only):**
- `allowed_engine_files.tsv` equals `git diff --name-status 8626a35 31616338 -- engine/` (26 rows).
- `engine_commits.tsv` equals `git log 8626a35..31616338 -- engine/` (24 commits, each of its kind).
- `counters.tsv`'s round-2 rows equal the coin script's `R2_COUNTERS + R2_KEYED` at the tip (27 names; the keyed ones match), and all 42 names are quoted in the two scripts.
- Every `revert_switch` name is a `DECKGYM_*` that P's `engine/src/` reads and 8626a35's doesn't.
- `ROUND2_QUEUED` equals `tightened_rule.py`'s at the tip.
- Every `tools_8c.tsv` blob is at its commit.
- The pin's new 8C pattern (an ERE) matches a sample line and README's grammar line.

## Counts

**32 findings in all:** 20 evidence (B1, S1-S9, N1-N10) and 12 safety. Evidence B1 and safety 2 are the same defect.

| Verdict | Evidence | Safety | Total |
|---|---:|---:|---:|
| fixed | 12 | 10 | 22 |
| fixed in part, the rest left for the coordinator | 2 (S3, S9) | 0 | 2 |
| left for the coordinator or the laptop session | 3 (S4, N1, N2) | 1 (10) | 4 |
| not a defect | 3 (N5, N8, N10) | 1 (8) | 4 |

## Evidence review

### B1: the data files and two byte copies were missing (blocker). Fixed.
- **New in `O/`:** `switch2.env`, `allowed_engine_files.tsv`, `engine_commits.tsv`, `counters.tsv`, `floor_7c.tsv`, `reuse.tsv`, `tools_8c.tsv`.
  - They follow ADAPTATION_SPEC Appendix A, with the S1, S2 and S8 changes below.
  - Every value was checked against git: blobs, sha256, the reused files' sha256 and line counts, the floor pages at their commits, and floor.py's diff sha256.
  - The tsvs use real tabs and LF.
- **Byte copies from the Oct 1 folder:** `floor_with.py` (blob 7e4880fe) and `.gitignore` (blob ff44c03a).
- **Still marked TO FINALIZE:**
  - in `switch2.env`: `P`, `P_TREE`, `COIN_SCRIPT_BLOB`, `SUITE_AT_P`, `MAGNEZONE_CARD_CHECK`, `ENGINE_DIR`, `FR_REL` and `PIN_NOTED_EXTRA`;
  - the first line of `allowed_engine_files.tsv`, `engine_commits.tsv`, `counters.tsv` and `tools_8c.tsv`.
- **Left for the laptop session:** both dry runs (`bash sitting1.sh --dry-run`, `bash sitting2.sh --dry-run`). I was not allowed to run them.

### S1: the 8c tools were checked only for existence at the candidate. Fixed.
- **Why it was right:** (a) landed after the last engine commit.
  - The tip's `coin_probe_v2.rs` is 31857834; at 31616338 it is 3a52e9bf.
  - So with P = 31616338, the hand-off would have named the probe from before (a).
- **The fix:** P stays PLAN's P, the engine commit. Each tool is now pinned by its own commit and blob.
  - **`tools_8c.tsv`:** columns `role path commit blob`. All seven rows are at 056158c3.
  - **`validate_v2.py` dropped:** at the tip it still reads round 1's REACH names (lines 30-32), plus Oct 1's `pairs_8.tsv` and seed block. The file's comment says why.
  - **`sitting2.sh`:**
    - `tools_bad()` (911) replaces `tools_missing`;
    - it is used at the start refusal (1545) and in the dry run (1425);
    - the header check reads `role path commit blob` (265);
    - the header text is updated.
  - **`sitting2_check.py` handoff (860):** the tools table now names `commit:path` and the blob.

### S2: a gate's revert switch could only be one name. Fixed.
- **Read from the code** at 31616338, `apply_action_helpers.rs`:692-745.
  - The G2 comment says: "The old damage needs G1 off too".
  - Every other row's switch matches its G comment.
- **`counters.tsv`:** `coin_queued_by_attack` is now `DECKGYM_PLAIN_QUEUED_SITES+DECKGYM_NO_PLAIN_HIT_COIN`. The comment there gives the source.
- **`sitting1_check.py`:155:** the pattern allows names joined by `+`. The docstring says so.
- **`pin/pin_rules.sh`:333:** the pin splits on `+` before it checks the names against P's `engine/src/`.
- **`sitting2_check.py`:**
  - the RULE text, item 3 (796): "its switch set ... alone ..., and `DECKGYM_ROUND2_OFF` for every gate together";
  - the revert-switch section (872): a `+` set is set together.

### S3: "a game where every counter is 0 must be identical" was dropped with no recorded ruling. Fixed in part; the ruling is left for the coordinator.
- **The mechanical part, done:** the pin now counts these games and requires 8c to say it traced each one.
  - The 8C grammar gains `none <z> traced <z>; other_only <o> traced <o>`. Each must equal the hand-off's `none` and `other_only` rows.
  - Where it changed:
    - `pin_rules.sh`: the counts (405), the pattern (457) and the checks (476-479);
    - `update_manifest_rules.py`: the pattern (96), the check (106) and the manifest text (198);
    - the engine README text and the pin commit message;
    - `pin/README.md`'s grammar (61-66).
- **Left for the coordinator:** a recorded reading, before sitting 2, of whether such a game passes when 8c explains it in look-ahead.
  - PLAN section 6 keeps the last plan's line 148 ("A game where every counter is 0 must be identical"). The cloud's 8b already has one such game: k3, pairing 37, i 35.
  - Until then the runners send these games to 8c and never halt on them (ADAPTATION_SPEC A7).

### S4: 7c's deck 10 v t-weezing watch row is treated as a named row. Left for the coordinator.
- **Right on PLAN's letter:** section 6 names only "deck 10's t-weezing floor row".
- **Why I did not change it:** whether the watch row on the same matchup is named is a stop-rule reading. Relaxing it needs a recorded word, and tightening it would halt sitting 1 on an expected Will change. It is not mine to decide either way.
- **Today the copies follow ADAPTATION_SPEC A11:**
  - pairing 7's changed games go to 8c in `handoff_7c_km3.tsv`;
  - the STEP 7c line counts them;
  - the pin requires 8c verdicts for them.
- **If the coordinator reads PLAN literally,** two edits in `sitting1.sh`:
  1. 1829-1830: drop `ident_f --exclude-pairings "$TWEEZ7C2"` for a plain `ident` on 1,440 deals.
  2. 1831: drop the `touched_7c` call (its STEP phrase would then read `changed 0 of 60 deals`).

### S5: 7c's counter check on Oct 1's 32 rows was copied by name, not by purpose. Fixed.
- **`sitting1.sh`:1822** now passes:
  - `--zero-role reach2 --zero-role superset2` (this switch's own counters);
  - `--zero-role r1_exact --zero-role r1_heads --zero-role r1_superset` (round 1's, kept as on Oct 1);
  - `--require offgate_helper_choice,offgate_by_attack --in $OFFGATE7C` and `--report-rest`.
- **Why `offgate_by_attack` is safe to require there:**
  - it uses the same 15 helper mechanics (`R2_SITES`, coin script :135);
  - it has the same "plain ApplyDamage offered at the opponent" condition as `offgate_helper_choice`;
  - so it fires wherever Absol, Heatmor or Gabite fire `offgate_helper_choice`.
- **Why keeping round 1's zero check is harmless:** those games were all 0 on Oct 1. The widened round-1 counters fire only on round-2 paths, and those would also change the game.
- The header (step 7c) and the label are updated.

### S6: the trace-load gate's n did not cover the laptop's own 8b rows 40-46. Fixed.
- **The cloud's README says** its TRACE LOAD 0 covers rows 32-37 only ("Scope").
- **`sitting2_check.py` trace-gate** (900, 928, 1018):
  - takes `--extra-rows`;
  - adds each row there whose category is not `reach` to n;
  - waits when the total is above 50 and there is no DUSTIN line;
  - adds nothing when `trace_load.txt` has the line `COVERS 32-37,40-46`, so a cloud load that covers those rows is not counted twice.
- **`sitting2.sh` `gate_8c` (1203)** passes `handoff_8b_new2_{km3,k3}.tsv`.
- The header and the gate's text are updated.

### S7: a change in deck 10's floor row was never tied to its Will row. Fixed.
- **`pin_rules.sh`:430-442** reads the STEP 7c line's `page 10's t-weezing: <k> of <n> games differ`.
- **When k > 0,** step 8's pairing 60 (deck 10 v t-weezing) must have a changed game with `will_confused_attack` in its `reach2_counters`.
- **Otherwise it is a judgment call:**
  - the pin needs `PIN_DUSTIN`, verbatim in `8c_DECISION.md` (485-496);
  - `--check` with `PIN_CHECK_WITHOUT_8C` only prints a NOTE;
  - the pin commit message names it (1055).
- `pin/README.md` and the pin's usage text say so.

### S8: the pin's documents from PLAN were only NOTEs. Fixed.
- **`pin_rules.sh`:115:** `REQUIRED_DOCS` adds `rules/09`, `rules/04` and the READOUT.
- **`rules/02` and `PLAN.md`** stay NOTEs: PLAN's list does not name them.
- **`PIN_NOTED_EXTRA`'s files are now required:**
  - they are added to `REQUIRED_DOCS` (291);
  - in pin mode the pin refuses when the key is missing (296);
  - `switch2.env` sets it to `TO_FINALIZE`, so the pin refuses until it is named (256).
- `pin/README.md` (11, 84) is updated to match.

### S9: step 4's allowed list checked P against itself. Fixed in part; the coordinator's word is left.
- **The check is circular by design:** the list is approved when the file is finalized.
- **`allowed_engine_files.tsv` now records each file's scope,** commit by commit: 20e2651's 17, P1, P2 and its switch, P3, Bounded Field, and (e).
- **It also lists where PLAN and P differ:**
  - P3's `apply_abilities_action.rs` and `models/card.rs` are not in question 2a's list;
  - PLAN's `effect_mechanic_map.rs` and `effect_ability_mechanic_map.rs` are untouched by P;
  - (e) touches 10 listed source files, and PLAN's list does not include (e) at all.
- **Left for the coordinator, before the marker line goes:** a word on those files, and the same list for precondition (f)'s two readers.

### N1: the coin script differs from PLAN step 6. Left for the laptop session (no runner change).
- The deviation is right: section 0 (c) needs P2's counters.
- It is documented in `sitting1.sh`'s header and now also in `switch2.env`'s comment.
- **Open:** precondition (c)'s second read must cover blob 306f1f69, not only da08620's 1b2678bd.

### N2: `MAGNEZONE_CARD_CHECK` is checked only for existence. Left for the laptop session.
- The cloud's card-check file has no known grammar, so a "PASS" pattern could refuse a good file or pass a bad one.
- `switch2.env`'s comment now says: name it only once that file records the check as passed.

### N3: the seed-row check passed on the new row alone. Fixed.
- Both sittings now also require START_HERE's own `| 23,100,000,000 ...` row to hold `36–37` (seed_row_23_3B.md section 2):
  - `sitting1.sh` `seed_row_ok` (1308), with the dry-run and refusal texts;
  - `sitting2.sh` `seed_rows_ok` (866), with its texts.
- The drafted new row also mentions 23,100,000,000, so the check anchors on the start of the row.

### N4: the 8C line could not show "both halves". Fixed.
- The grammar adds `both_halves <l> of <l>`, checked to equal the look-ahead count:
  - `pin_rules.sh`:469;
  - `update_manifest_rules.py`, in the same assertion block (96-106);
  - README.

### N5: only part of 8b is cross-checked with the cloud. Not a defect.
- The laptop's watch must already equal its own new rows on every field, and its new rows 32-37 must equal the cloud's.
- Comparing watch counters with the cloud's watch file (made on 140c0be2) would add a halt that PLAN doesn't name.
- The cloud's own 8c run is PLAN's cross-check.

### N6: the data files could change between the sittings. Fixed for `counters.tsv`.
- **`sitting2.sh` `s1_counters_why` (921):**
  - the start refuses (1547) when `counters.tsv`'s sha256-16 is not the one in sitting 1's last START line;
  - the dry run notes it.
- **Not compared:**
  - `switch2.env` legitimately changes between the sittings (`MAGNEZONE_CARD_CHECK` is sitting 2's alone);
  - sitting 2 does not read `floor_7c.tsv`.

### N7: a failed hand-off rebuild was only a note. Fixed.
- **`pin_rules.sh`:408-416:** `handoff_8c.tsv` (HEAD) must equal the header plus the ten per-set `handoff_<set>.tsv` files, in sitting2.sh's order. Each of those files is in its step's manifest, which gate 2 checks.

### N8: `floor_py_check` reads only ATTACKERS. Not a defect today.
- A ROLES or ATTACKERS entry for a page's deck (or for D's original path) would show as a page difference, which halts. It is never a silent pass.
- The reviewer confirmed that neither table names those decks.

### N9: PLAN line citations were 4 lines stale. Fixed.
- PLAN.md's status keeps growing, so evidence text now cites by step or section, not line.
- **Files edited:**
  - `sitting1.sh`, `sitting2.sh`, `sitting1_check.py`, `sitting2_check.py`;
  - `pin/pin_rules.sh`, `pin/update_manifest_rules.py`, `pin/README.md`.
- **Exact replacements,** each count-checked (`fix_cites.py`). Two kinds of citation stay as they were:
  - PLAN lines 24-29 and 28 (the status block, still right);
  - citations of other files (`pin.sh` line 487, `run_km.sh`).

### N10: watch is never compared with plain on 7c's rows. Not a defect.
- This is as on Oct 1.
- Step 7b shows watch = plain on 28,000 table games on every field.

## Safety review

### 1: the busy check could not see the combined run (blocker). Fixed.
- **Both sittings:**
  - `strength` joins the program names;
  - `watch_list_busy` (sitting1.sh:1331, sitting2.sh:877) refuses on any process, outside the run's group, whose command line holds a non-comment `$HOME/runs/watch.list` line's PATTERN or CHAIN. That covers today's `strength run --manifest ...` and `combined_chain.sh`.
  - Watchers (`run_watch.sh`, `watch_all.sh`) are skipped: their command lines hold the pattern.
  - A live launch_detached pid file whose `cmd=` is `rl/strength/run_watch.sh` no longer counts as busy (sitting1.sh:1351, sitting2.sh:897). It reads status files and pushes only its own status branch with plumbing. It would otherwise force `BUSY_OK=1`, which turns the whole check off.
- **`sitting2.sh`:** the busy refusal moved before the git-lock wait and the unstage (1553), as `sitting1.sh` has it.
- **The pin's gate 6 (574, 579):**
  - any `strength` process is busy;
  - so are processes matching `watch.list`'s PATTERN or CHAIN (watchers and the pin itself skipped);
  - the pin has no override; its existing launch_detached rule is unchanged.

### 2: the data files were missing. Fixed. Same as B1.

### 3: sitting 1 committed before it checked origin. Fixed.
- **`sitting1.sh`:**
  - `origin_ahead` (603) is copied from `sitting2.sh`;
  - `checkpoint` stops before committing when origin/main is ahead (615);
  - `record_commit` leaves the record uncommitted with a NOT PUSHED line (654);
  - `not_pushed` gains sitting 2's "uncommitted" wording (636).
- The header says so.

### 4: a data-entry slip found at step 4 became a permanent HALT. Fixed.
- **`sitting1.sh`:1560-1567:** on a fresh start (no `candidate.txt`, no candidate ref), `p_checks`, `reserved_check`, `merge_tree` and `candidate_checks` run on the merge tree before the START line, with `PRECHECK=1`.
- **Under `PRECHECK`:**
  - `halt` and `die` become `refuse` (514, 533): exit 2, nothing recorded;
  - `note` prints instead of writing STATUS.txt (507).
- Step 4 runs the same checks again on the candidate.

### 5: sitting 1 did not refuse while sitting 2 held its lock. Fixed.
- `sitting1.sh` `s2_lock_held` (1507) refuses (1517) before the helper checks and the unstage.

### 6: step 8-seeds wrote kept files without `.part`. Fixed.
- `sitting2.sh`:1668 (`pairs_8b2.tsv`, `pairs_will.tsv`) and 1675 (`seeds_8_2.txt`) now do copy to `.part`, sync, then rename.

### 7: ALLOW_DAYTIME=1 was the default on weekdays too. Fixed.
- **The new default `auto`** (sitting1.sh:453, 462; sitting2.sh:358, 367):
  - a start between 11:30 and 21:00 UTC with no explicit DEADLINE is allowed on Saturday and Sunday;
  - it is refused Monday-Friday.
- `1` still allows it on any day, and `0` refuses it on any day (Oct 1's rule).
- **This departs from the brief's "default allowing it" on weekdays only.** Dustin's word covers the weekend. PLAN line 28 says a step stopped on Monday morning "resumes Monday evening". Weekday daytime is class and travel.
- The KNOBS text, the headers, the refusals (sitting1.sh:1528, sitting2.sh:1539) and the dry-run notes are updated.

### 8: the pin writes PREPARE DONE itself. Not a defect.
- This is Oct 1's design, documented in `pin/README.md`.
- The gate is `8c_RESULT.txt` in the exact grammar, which the laptop commits after the coordinator's audit. A judgment call still needs `PIN_DUSTIN`.
- If the coordinator wants PREPARE DONE as a separate mark, the pin can require it instead of writing it (`pin_rules.sh`, the `PREPARE DONE` lines before step 11).

### 9: `PIN_DUSTIN` accepted any value. Fixed.
- `pin_rules.sh`:485-496: when a judgment call waits, the words must appear in the committed `8c_DECISION.md`, whitespace aside.

### 10: a start adopts unpushed commits that touch only this folder or START_HERE.md. Left for the laptop session (inherited from Oct 1, not changed).
- A stricter rule (only the runners' helpers and data files) would refuse the laptop session's own unpushed `trace_load.txt` or 8c commits in this folder.
- Today only the laptop session writes here and in the seed table. The cost of the current rule is pushing such a commit, which the laptop session made.
- If another session starts writing in this folder, the laptop session should make sure those commits are pushed before a start.

### 11: the pin was documented as fine without launch_detached. Fixed.
- `pin_rules.sh` usage (55-64) and `pin/README.md` (The pin, 31) now:
  - start the pin through `rl/strength/launch_detached.sh start rules2-pin ...`;
  - say `--check` runs plainly.

### 12: `update_manifest_rules.py`'s checks are asserts. Fixed.
- `pin_rules.sh`:90 does `unset PYTHONOPTIMIZE`.
- The sittings' checkers use no `assert`.

## Values still to fill in when P lands (all in `O/`)

### `switch2.env`
| Key | Today's candidate value | Note |
|---|---|---|
| `P` | 316163384641dfba546e22e967cf1be8f0a80d5e | the last engine commit |
| `P_TREE` | 639d2f804ad9277137cec8f4de8790194f3b0b22 | |
| `COIN_SCRIPT_BLOB` | 306f1f6969af39c54bd09a164c8fab27a083c194 | |
| `SUITE_AT_P` | not yet | the suite has not run at 31616338; 5ec11518's `suite_p1.log` is at b0dc4844 and does not name P |
| `MAGNEZONE_CARD_CHECK` | not yet | the cloud's card check of `c-magnezone_ex_magnezone.txt` |
| `ENGINE_DIR` | at the pin | `rl/engine-<the pin's date>` |
| `FR_REL` | at the pin | step 15's folder |
| `PIN_NOTED_EXTRA` | at the pin | the files for Sonnet's note 8 and km3's new B2e reference |

### The tsv markers
Remove the `# TO FINALIZE` first line of each, after re-checking it against the final P:
- `allowed_engine_files.tsv`: with the coordinator's word on the scope (S9);
- `engine_commits.tsv`;
- `counters.tsv`: if (e) or (a) adds names;
- `tools_8c.tsv`: once (a) and (b) are final; its commit and blobs are pinned at 056158c3 today.

### Outside the data files, before a start
- START_HERE.md's two seed rows, from `seed_row_23_3B.md`, committed.
- Both dry runs.
- `trace_load.txt` before step 8.
- The coordinator's rulings S3 and S4, recorded before sitting 2.

## Files that need +x
None. Every copy is run through `bash` or `python3`, and the Oct 1 originals are committed 100644; keep 100644.
