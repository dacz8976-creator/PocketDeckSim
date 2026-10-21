# Deck journal build: report for the laptop's review

Built from `rl/deck_journal/SPEC.md` and, in the second job, `INTEGRATION_BRIEF.md` Parts B-E with the coordinator's addendum
(Oct 15) by the Sonnet credit worker. Standard library only; no engine binary, no cargo.
Files: `journal.py`, `test_journal.py` (61 tests, all pass on Python 3.14.4), `first_fill.py`, `reviewed_testers.json` (empty:
only the laptop adds entries), `testdata/` (the fixture), `journals/01-muk-glimmora-kingambit-regigigas.json` and its `.md`.
Run the tests with `python3 -W ignore rl/deck_journal/test_journal.py` (about 15 s). `journal.py check` is ok.

## Second job (Parts B-E): what changed
Tests first: commit 87c99c84 (38 of 53 tests then in the file failed or errored on `da8c728e`'s `journal.py`; the other 15 were the
earlier tests that still held). Then the code.

**The setup reader (Part C).** `journal.py add-result --deck STEM --kind setup --run FOLDER --by WHO [--only ID,ID]
[--corrects FOLDER@COMMIT]`; the old `add_setup` and its options are gone.
- A run is read from `git show <commit>:<folder>/results.json`, `commit` being the last commit on `origin/main` that touches the
  folder; `files_sha256` holds results.json and RESULTS.md (RESULTS.md is hashed, never parsed). Nothing is written when any check fails
  (a refusal leaves the journal as it was).
- Refused: folder dirty or with untracked files; not on main (the amendment-1 runs, today); `SUPERSEDED.md`; a schema other than
  `setup-tester results v2`, or a missing field; code sha not in `reviewed_testers.json` or a different `tester_commit`;
  `tree_clean` not true; the three ids disagreeing or null; two versions with one id; no `setup.P1` or `p1_exact`; impossible counts
  (n per seat from the deal rule, x_no <= x_yes <= n, ranges inside 0-1, `G5.n5` exempt for x > n); a version not in the journal (the
  message names it and the add-version command); the same run filed twice; the same folder at another commit without `--corrects`.
- One result per version: tester, engine, seeds, deals, config (`pawniard_bench`, `setup_bench`, the Copycat valuation with its
  value table, fallback rule and disagreement count, `all` = the run's config), `p1` (exact and simulated), `clocks`, `plan_lines`
  (the 15 P ids, each cell `x_no`, `x_yes`, `n`, `range`, `range_method` boot or wilson), `plan_given_moment`, `held`, `rulings`,
  `descriptive` (67 setup measures, the G5 mean, K clocks, exact), `comparisons` (direct against the run's base, inverted for the
  base, none between two others; clock differences pooled and flagged by the tester's rule), `not_valued`.
- **Departures from the brief's mapping, because the real v2 file differs from the brief's guess:** the Copycat fields live under
  `run.copycat` (the addendum's valuation rule replaces the N=2, M=1 placeholder; there is no `copycat_nm_status`); the no-knockout
  runs' bench trigger is `at_once` with no reserved slot (not `now` with a reserved slot); P3 is three causes (`P3.pawn_lead`,
  `P3.pawn_promo`, `P3.grimer_muk`); `given_moment` is stored apart from the plan lines; the run's base is the version named `base`.
  P2 and P3 are held only if `run.rulings` lacks R1 or R2 (the fixture has both, so both show numbers).
- **The view (about 16 lines per block, up to 9 setup lines: header, P1+P2, P3, P4-P5 on your games' pace, P4 on three set paces, the
  comparison with what he plays, not valued, speed). This is the view-length departure from the spec's "about 10 lines"; the
  coordinator approved it (addendum section 3).** Header reads "Copycat played by your valuation, approximated (value table in the
  run's RESULTS.md)" and adds how often the fallback rule would play it differently. Held lines print no digits; lines the run lists
  as zero by construction print so (medium's two "wins outright" lines; slow is the 180-HP Mega ex, knockouts on their turns 3/5/7;
  the 220-HP row stays in RESULTS.md). Undecided games: the figure counts them as no, and `[x% as yes]` shows the other end (the run's
  rule is v2). A merged block takes the setup result of whichever of its versions holds one and names that id.

**Part B fixes.**
1. `add-result --kind bot --deck-path PATH` (committed on main, its raw card list's first 12 hex digits = the version id; the stem
   names the deck for `harness_bots`; `deck_path`, `deck_file_sha256`, `card_list_sha256` stored). His list's `file` is
   `decks/dustin/01-kingambit-as-played.txt`.
2. `--origin "agent proposal"` without `--parent` is refused (also checked by `check`); an inferred parent breaks ties to NOW PLAYING,
   then the newest (`choose_parent`; `version_from_code` uses it). An agent proposal's "Changed" line is computed against NOW PLAYING
   and adds "(built on <parent>)".
3. Played outcomes read SUMMARY.json `result`, then `outcome` (a word, a sentence or a dict's `owner_result`), then `owner_result` /
   `method`; `result_key` and `result_raw` are stored. All 12 packets have a result: 010706, 210823, 203719 win; 210041, 225319 loss;
   the other seven as their `result` says.
4. Dates: the packet's own date field when it has one (`local_match_date`, `match_date_local`, `match_date`,
   `local_recording_start`), else the UTC video name in America/Chicago. The 12 games read "Oct 11-12". **Correction to the first
   report's item 9: the video names are UTC, not local.**
5. Bot lines: older-engine results grouped by `games_sha256` ("17 results on 11 game sets", not "17 from 9 runs"); the floor line
   says it counts wins only; the label comes from the manifest stage ("dev", never "exam"); "kx3 games n of N" (N = the arm's games
   in the run); `knows_the_panel_lists` stored, and kx3 carries "its number is the optimistic end".
6. In a merged block each bot line names its own version id.
7. `--file` checks the file's raw card list against the id (`mp.card_list_sha256`), with no Energy-alias clean-up.
8. `committed()` also requires the source commit to be an ancestor of `main_ref` (an argument; default `origin/main`, then `main`);
   `main_commit` is stored in every setup and bot result.
9. `save()` checks the copy on disk and `origin/main`'s copy (the `--ref` option is gone; tests pass the ref as an argument); a new
   key on an earlier version and a changed `title` are detected. `corrects` is a field of a new result naming the (kind, source,
   commit, version) it corrects; the earlier result stays; the view shows the newest result nothing corrects, plus "(corrected <date>)".
10. test_journal.py's count compared with itself is fixed (the merged block names the root once). Deck 01 holds 19 bot results: 2 on
    the current engine, 16 from 8 harness runs, and 1 floor (the earlier "17 older-engine results from 8 runs" counted the floor in
    with the harness results).

**First fill (Part E), regenerated on the branch (nothing was on main).** Deck 01 and his list A `73dfed58d1d6` (file
`decks/dustin/01-kingambit-as-played.txt`, 12 played games with outcomes and local dates), the regrouped deck-01 bot lines, the
note. Agent proposals: B `78b2ba4b7e24` (parent A), C `74075f8030e0` (parent B) and B+ `a76361f7ffbc` (parent B), each reason
starting "WITHDRAWN Oct 15: cuts cards his plan uses" and then the deliverable's reason, origin_source the deliverable on main
(6acfaacc); and the two current proposals with parent A: **A1 `6f3bbf39374e`** (-1 Lucky Ice Pop B2 145, +1 Rare Candy A3 144) and
**A2 `ba59eb4ecb12`** (-1 Lucky Ice Pop, -1 Professor's Research, +1 Rare Candy, +1 Juliana B3a 071), origin_source "laptop review +
Astra's review, Oct 15 (tester fix brief section D)". **No setup result is filed**: the view says "Setup odds: not computed yet".

**The fixture.** `testdata/versions_small.json` and `testdata/setup_run_small/` (results.json, RESULTS.md), made by the tester at
`8cd276fb` (origin/sonnet/setup-tester) in a clean temporary worktree with this command (no engine program)
`python3 rl/setup_tester/setup_tester.py --versions <versions_small.json> --deals 2000 --clock-deals 1000 --out <testdata/setup_run_small> --name journal_fixture`
(99 s; deals 0-1,999 of the registered 24.7B block; versions base = A, deck01, B and C; the base deck file was copied into the worktree
untracked, since that branch predates it). Its code sha is `2c8b531f85b4…`; it is not in `reviewed_testers.json`, so tests use a
temporary reviewed file. Its numbers are small-run numbers; the fixture is test data, not a result.

## Still open (not in this job)
- Journal findings 5 (binding precedence; "his note" without a QR; catalog never read), 6 (current engine decided when filed, not at
  render) and 10 (every tie labelled confirmed; dropped INTEGRATION problems). These must land before the journal is used for ladder
  games, for new packets, or past the next engine pin.
- Tester items outside the fix job's A-C. Section D (the A/A1/A2 comparison) is run by the laptop after its review; the real run is
  then filed from main after the laptop adds its entry to `reviewed_testers.json`.
- `test_setup_tester.py` was not re-run here (8 minutes); the tester branch's own report says 88 pass at `8cd276fb`.

## First job (the spec's build), still true except where the second job changed it
- Each result has `kind, at, by, source, commit`; `file_first_commit_date` and `origin_source` are extra entry fields; `diff` lists
  removals first, then additions, one line per copy; `printing_only` lists each swap once.
- The Haxorus lists are not filed (their own deck's journal); `first_fill.py` is Kingambit only.
- No `versions.json` exists on main yet, so the ladder paths (`ladder_from_notes`, `ladder_from_reading`) are tested on synthetic games
  only and no Kingambit ladder result is filed.
- A bot result needs a deck file on main (or `--deck-path`); His list has none that a bot ran, so nothing is filed under it.
- The "KW files reproduce all 12 filmed codes" claim is not re-tested; binding compares card sets, as the spec says.
