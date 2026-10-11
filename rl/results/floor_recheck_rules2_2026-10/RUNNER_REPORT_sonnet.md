# Step 15 runners: report (Sonnet, Oct 11)

Nothing was run with games: no floor.py, run_screen.py or deckgym, no goldfish. The only runs were the tests, the two runners' `--dry-run`
(before the pin: both end "BEFORE THE PIN", exit 0, nothing written; a real run refuses with exit 2) and a rehearsal of Part B's
two Python steps on the real files (below).

## Files (all in this folder)

- `run_check.sh`: Part A. A copy of Oct 2's runner with the PLAN's changes, plus `--dry-run` and `--engine-check`.
- `run_pages.sh`: Part B.
- `test_runners.py`: the tests and the break-it-on-purpose check (`--mutations`).
- `RUNNER_REPORT_sonnet.md`: this report. `PLAN.md` is not here: the pin installs it, and both runners refuse until it is committed with them.

## How to use

- Start both through `rl/strength/launch_detached.sh` (a real run refuses without its `LAUNCH_DETACHED_RUN` variable):
  `launch_detached.sh start floor-recheck2 -- bash rl/results/floor_recheck_rules2_2026-10/run_check.sh`, then, after `RESULT PASSED`,
  `launch_detached.sh start floor-pages2 -- bash rl/results/floor_recheck_rules2_2026-10/run_pages.sh`.
- `bash run_check.sh --dry-run` and `bash run_pages.sh --dry-run` run every check that doesn't need the pin (or, for Part B, Part A's result)
  and print the plan. Exit 0, or 2 if something that is not the pin's own fails.
- Exit codes: 0 done or passed, 1 not passed or stopped (Part B: "PAGES STOPPED", goes to Dustin), 2 refused (nothing written).

## What each runner does

Part A (the PLAN's list): refuses unless the PLAN and both runners are committed unchanged, no earlier output is here (including `pages/`), no
`DECKGYM_*`, the time is outside 10:15-22:00 UTC (or `ALLOW_DAYTIME=1`), and the engine checks pass (manifest release `rl/engine-2026-10-12/deckgym`
named main-<source commit>; the three hashes 0a9199bc / bf9d7502 / d8cfb779 in the record, SHA256SUMS, on disk and committed; source commit on HEAD,
holding P c7a25df4, its `engine/` tree 70652fff; main-8626a35 superseded in the history; current_engine.py resolves it; the pilot is km3; the pricing
file equals the source commit's). All 16 of Oct 2's files at 2d7082cf are blob-checked before any game. After the games the comparison puts the new
engine lines into Oct 2's file and needs every byte equal; each old engine line must occur exactly once per page and twice in `run_screen.txt`;
`_games.jsonl` and `_coverage.json` are byte-equal with no exceptions. The RESULT line is first in `verdicts.txt` (PASSED exit 0, NOT PASSED exit 1);
a mid-run stop logs RECHECK STOPPED and writes no RESULT. Each input's sha256 is reported (information only).

Part B: the same refusals, plus Part A's `verdicts.txt` must start "RESULT PASSED", `run_check.sh --engine-check` must pass, and every file it reads
(Oct 2's D pages, 7c's replays, `d_first/`, `floor_copy.diff`, `run_copy.py`, today's `floor.py`, the old Sept 30 pages) must be the committed one
(d_first's list also the 9cc6667 blob, sha256 4821877f). Then: deck 12, brew 07, brew 09 by floor.py's own call into `pages/12`, `pages/brew-07`,
`pages/brew-09` (each page checked for the new engine line, km3/km3, 1,920 games, a real floor verdict); D's victini-passive page from a rebuilt
private copy (today's floor.py plus Oct 2's one ROLES entry with the path changed; the copy's diff must be exactly that one line) run through
`run_copy.py`, its page, games and coverage compared with Oct 2's (games byte-equal, else STOP for Dustin; page equal but for the two engine lines
and Victini's caveat; coverage equal but for Victini's entries); D_root and D_amended from 7c's replay page with the new engine named, Victini's row
from the new goldfish's `--games 0 --coverage`, and the PLAN's one line (the flagged cards must be the same set and every other card's reasons
unchanged, else STOP). An `OLD_PAGE.txt` beside each page names its old page, its old and new verdict and wins, and what the PLAN expects. No deck 10.

## Tests

55 tests, all pass (`python3 -W ignore test_runners.py`, about 35 s). They run the real runner sources in a fake repository (git, committed
references, fake programs, fake floor.py/run_screen.py/goldfish that copy canned pages); only the engine hashes, P, its tree, 2d7082cf and D's
first-list sha256 are replaced by the fake ones (every replacement is asserted). `RealConstants` also checks the real file holds the spec's values.
Covered: the happy path; an engine line twice; a changed byte elsewhere; a missing file; a RESULT line first in both outcomes; games/coverage with no
exceptions; wins, the control, run_screen against the floor; a mid-run stop (no RESULT); each refusal (before the pin, the clock edges 10:14/10:15/21:59/
22:00, DECKGYM, not detached, earlier outputs, PLAN/runner changed or uncommitted, reference file changed/missing, program hash/SHA256SUMS/executable/
uncommitted, programs record, manifest name/superseded/source commit, P not in the source, wrong tree, pricing file, resolve, pilot); dry runs before
and after the pin writing nothing (files and folders); Part B's stops (a differing victini-passive game or page, a non-Victini coverage difference, Victini
unflagged, a floor failure, a non-floor page, an old-engine page, uncommitted inputs, the d_first blob, a changed ROLES anchor, a wrong copy diff, a Part B reference file changed after 9630c0dc and committed), and a crash in Part A's verdict script (exit 3).

## Broken on purpose (`python3 test_runners.py --mutations`): 54 of 54 fail a test

Each is one change to a runner copy; the first failing test is named.

```
run_check.sh: NOT PASSED exits 0 -> PartA.test_a_changed_byte_elsewhere_in_a_page
run_check.sh: P need not be in the source commit -> PartA.test_p_and_its_tree
run_check.sh: RESULT line not first -> PartA.test_happy_path_passes
run_check.sh: SHA256SUMS is not checked -> PartA.test_engine_program_hash_and_files
run_check.sh: a changed plan is accepted -> PartA.test_plan_or_runner_not_committed_unchanged
run_check.sh: a mid-run stop says nothing -> PartA.test_a_mid_run_stop_writes_no_result
run_check.sh: an old engine line may occur any number of times -> PartA.test_an_old_engine_line_twice_in_a_reference_page
run_check.sh: an uncommitted plan is accepted -> PartA.test_plan_or_runner_not_committed_unchanged
run_check.sh: any difference is accepted -> PartA.test_a_changed_byte_elsewhere_in_a_page
run_check.sh: coverage files are not compared -> PartA.test_games_and_coverage_have_no_exceptions
run_check.sh: current_engine is not checked -> PartA.test_resolve_and_pilot
run_check.sh: earlier outputs are ignored -> PartA.test_earlier_outputs_present
run_check.sh: launch_detached is not required -> PartA.test_not_started_through_launch_detached
run_check.sh: program hashes are not checked -> PartA.test_engine_program_hash_and_files
run_check.sh: reference blobs are not checked -> PartA.test_a_reference_file_missing_or_changed
run_check.sh: run_screen is not compared with the floor -> PartA.test_run_screen_must_equal_the_floor
run_check.sh: superseded is not checked -> PartA.test_manifest_facts
run_check.sh: the DECKGYM check is gone -> PartA.test_a_deckgym_variable
run_check.sh: the control may read anything -> PartA.test_the_control_must_read_untrusted
run_check.sh: the dry run creates a folder -> PartA.test_dry_run_after_the_pin
run_check.sh: the dry run writes a file -> PartA.test_dry_run_after_the_pin
run_check.sh: the engine lines are not put in -> PartA.test_clock_window
run_check.sh: the engine tree is not checked -> PartA.test_p_and_its_tree
run_check.sh: the pilot is not checked -> PartA.test_resolve_and_pilot
run_check.sh: the pin check is gone -> PartA.test_dry_run_before_the_pin
run_check.sh: the pin does not refuse -> PartA.test_engine_check_mode
run_check.sh: the pricing file is not checked -> PartA.test_pricing_file_must_equal_the_source_commits
run_check.sh: the programs record is not checked -> PartA.test_the_programs_record_must_name_sitting_1s_builds
run_check.sh: the window closes at 21:00 -> PartA.test_clock_window
run_check.sh: the window opens at 10:30 -> PartA.test_clock_window
run_check.sh: wins need not equal Oct 2's -> PartA.test_wins_differ_from_oct2
run_check.sh: a crash in the verdict script exits 1 -> PartA.test_a_crash_in_the_verdict_script_exits_3
run_pages.sh: reference files are not pinned to the named commit -> PartB.test_a_reference_file_changed_after_the_named_commit_stops_part_b
run_pages.sh: the D copy is not run at nice 10 -> RealConstants.test_the_runner_holds_the_specs_values
run_pages.sh: Part A's result is not required -> PartB.test_refuses_without_a_passed_part_a
run_pages.sh: Victini's caveat is not replaced -> PartB.test_happy_path
run_pages.sh: Victini-passive games are not compared -> PartB.test_a_victini_passive_game_that_differs_is_a_stop
run_pages.sh: a dry run before the pin fails -> PartB.test_dry_run
run_pages.sh: a non-floor page is accepted -> PartB.test_a_page_that_is_not_a_floor_page_is_a_stop
run_pages.sh: a page naming the old engine is accepted -> PartB.test_a_page_naming_the_old_engine_is_a_stop
run_pages.sh: a stop is not logged -> PartB.test_a_non_victini_coverage_difference_is_a_stop
run_pages.sh: an earlier pages/ is accepted -> PartB.test_earlier_pages_present
run_pages.sh: committed inputs are not checked -> PartB.test_dry_run_still_fails_on_inputs_that_are_not_the_pins
run_pages.sh: launch_detached is not required -> PartB.test_clock_launch_and_deckgym_refusals
run_pages.sh: no note beside a page -> PartB.test_happy_path
run_pages.sh: other coverage entries may differ -> PartB.test_an_unflagged_coverage_entry_that_differs_is_a_stop
run_pages.sh: the 9cc6667 list is not checked -> PartB.test_d_first_must_be_the_9cc6667_blob
run_pages.sh: the DECKGYM check is gone -> PartB.test_clock_launch_and_deckgym_refusals
run_pages.sh: the ROLES anchor is not checked -> PartB.test_floor_py_without_the_roles_anchor
run_pages.sh: the clock is ignored -> PartB.test_clock_launch_and_deckgym_refusals
run_pages.sh: the copy's diff is not checked -> PartB.test_the_copy_differs_from_floor_py_by_exactly_oct2s_line
run_pages.sh: the flagged cards may differ -> PartB.test_victini_no_longer_flagged_is_a_stop
run_pages.sh: the one line is not written -> PartB.test_happy_path
run_pages.sh: the plan commit is not checked -> PartB.test_plan_and_runner_must_be_committed
```

(An earlier pass found four survivors: the duplicate DECKGYM check in `run_check.sh`'s Python block (removed; the shell check remains), a dry run
that created an empty folder (the tests only compared files, now folders too), a no-op mutation, and a coverage check that only an unflagged entry
reaches (a test added). It also found two real bugs in my first draft of `run_pages.sh`, fixed before anything was committed: a stray empty line in
the copy-diff comparison and D's page folders being written relative to the repository instead of `pages/`.)

## Rehearsal on real files (no game)

Part B's `mkcopy` on the real `decks/screen/floor.py` adds exactly one ROLES line (the d_first path) and nothing else; `dtext` on the real 7c replays,
the real Oct 2 pages and the real `floor.py`'s `flagged_cards`, with a stand-in goldfish that rewrote only Victini's caveat, gave pages that differ from
Oct 2's only in the added line, the engine line, Victini's caveat and the coverage line, with games byte-equal. So the real Victini row's old text matched
`flagged_cards`' output exactly, which the runner requires.

## Differences from the PLAN, additions, and open points (the PLAN wins; these are for the laptop to rule on)

1. **PLAN.md is not in this branch** (the pin installs it), so "committed unchanged" is checked only at run time; it can't be shown here beyond the
   tests. It checks `git ls-files` and `git diff HEAD` for PLAN.md, run_check.sh and run_pages.sh.
2. **"Its source commit is on main"** is implemented as "an ancestor of HEAD", as Oct 2's runner did. Run it from main after the pin.
3. **Part B's references are now pinned** (laptop's required change): `REF_COMMIT` = main 9630c0dc (full hash in `run_pages.sh`); every file read under
   `floor_drafts_2026-10-02/` and `floor_dustin_2026-09-30/` must equal its blob at that commit, checked before any game (the HEAD-blob check stays
   too). Test and mutation added. The 7c files, floor.py and the lists are still checked as HEAD blobs (outside that instruction).
   Also done (laptop's optional items): (a) an uncaught exception in Part A's verdict script exits 3 with no RESULT line and no RECHECK STOPPED
   (NOT PASSED stays exit 1); (b) D's victini-passive copy runs at `nice -n 10`, as Oct 2 did (neither conflicts with the PLAN, which isn't here to
   read: the pin installs it; the other floor runs stay unniced, as Oct 2's Part A was).
4. **The victini-passive page**: Oct 2's page carried a 6-line note added after its run; the new page gets the equivalent note after the comparison (the
   comparison strips Oct 2's note first). The rebuilt copy, its diff and its path change are in `pages/D_victini-passive/` and the log. Oct 2's runner
   also asserted floor.py's sha256; the PLAN says "today's floor.py", so mine checks only that the ROLES anchor is there once and the diff is exactly the
   one line.
5. **Added beyond the PLAN, from the spec:** a real run refuses unless started through launch_detached.sh; `--dry-run`; `--engine-check` (Part B uses
   it); Part B writes `pages/run_pages.log`, `pages/timing.txt`, each page's `OLD_PAGE.txt`, and the copy's files under `pages/D_victini-passive/`.
6. The time rule is 10:15-22:00 UTC as the PLAN says (Oct 2's runner said 10:30).
7. D_root/D_amended's Victini row keeps the replay's role and counts (the games are the replay's) and takes only the caveat cell from the new coverage;
   if Victini were no longer flagged, or any other flagged card's text changed, it stops.
8. Not automated: the PLAN's "judged through step 8b/B2e rows" for deck 12, brew 07 and brew 09. The runner writes the old/new verdicts and wins in the
   note and the log; the reading is for the laptop and Dustin.
9. Untested against the real programs, by instruction: the fake floor.py/goldfish stand in. The first real run is Part A.
