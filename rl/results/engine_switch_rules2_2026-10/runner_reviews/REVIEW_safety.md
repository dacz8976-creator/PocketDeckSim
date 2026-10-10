# Rules switch 2 runners: safety review (Opus, Oct 9, read-only)

Scope: the copies in `rl/results/engine_switch_rules2_2026-10/` (sitting1.sh, sitting2.sh, the three checkers, checkpoint.sh,
quiet.sh, pin/pin_rules.sh, pin/update_manifest_rules.py, pin/README.md) diffed against `../engine_switch_rules_2026-10/`, with
the unchanged logic read where it touches safety. Checks run: `bash -n` (all pass), Python `ast.parse` (all pass), `cmp`
(checkpoint.sh and quiet.sh are byte copies), CRLF scan (none), read-only `git`, `ps`, `df`, `du`, `free`. No shellcheck is
installed. Nothing was built, played, fetched, committed or pushed. Line numbers are the copies' unless marked "old".

Laptop facts this review relied on (23:29 UTC Oct 9): main = origin/main = d9f867c7; `origin/claude/coin-prevention-round2` =
056158c3 (moved past the spec's 31616338); `/tmp` is tmpfs (3.7 GB, RAM-backed; 7.5 GB RAM); `/` has 766 GB free, `/mnt/c` 27 GB;
the Oct 1 build folders are 474 MB and 265 MB. The combined run is `bash .../scratchpad/combined_chain.sh` (pgid 14332) running
`/home/dacz8976/kxc/172cbe9c/strength run ...` (pid 29189, comm `strength`, nice 19); it is not a launch_detached run (no
`~/runs/combined.pid`, no `LAUNCH_DETACHED_RUN` in its environment; the only pid file, `watch-combined.pid`, is dead). Its status
at 23:07Z: 614 of 1,120 games, +4 in 30 min.

---

## Findings (most severe first)

### 1. The busy check cannot see the combined run (blocker)
- **Where:** sitting1.sh:1292-1306 (`ps -C legality_scan,deckgym,goldfish,cargo,rustc,tool_census`, line 1298; pid files
  1299-1304), refusal 1465-1469; sitting2.sh:862-872 (comm regex line 864), refusal 1515-1520; pin_rules.sh:503-538 (gate 6).
- **What is wrong:** the combined run's program is named `strength`, which no list holds, and it was started by a chain script,
  not by launch_detached, so no `~/runs/*.pid` file names it. Both sittings' `busy_check`/`busy_now` return empty while it runs.
  Its chain also sits with no program at all on school days: `combined_chain.sh`:70-78 (`in_window`) sleeps 05:15-17:00
  Central and starts `strength run` again afterwards.
- **Failure scenario:** (a) the laptop session starts sitting 1 on Saturday or Sunday believing the combined run is done (it was
  expected Saturday night or Sunday; the 23:07Z status was 614 of 1,120): the start passes, and 14 threads at nice 10 run beside
  the nice-19 `strength run`, moving the combined run's kx3 timings (which its reading quotes) and the sitting's own rate and
  deadline estimates. (b) if the combined run spills into Monday, its chain idles 10:15-22:00 UTC with no program: a Monday
  start or resume of a sitting passes the check, and at 22:00 UTC the chain starts `strength run` beside it. PLAN line 360:
  "never beside a sitting".
- **Smallest fix:** in both sittings, add `strength` to the program names, and refuse when `pgrep -f` finds, outside this run's
  process group, the PATTERN or the CHAIN of any non-comment line of `$HOME/runs/watch.list` (the laptop's list of long runs;
  today `strength run --manifest rl/results/strength_2026-10-08_kx3_combined` and `combined_chain.sh`). Do the same in the pin's
  gate 6 (add `strength` to the case at pin_rules.sh:516). In sitting2.sh, move the busy refusal (1515-1520) above the unstage
  (1499-1507), as sitting1.sh has it. (Side note: a live launch_detached `run_watch.sh` watcher also counts as busy, which forces
  BUSY_OK=1 and turns the whole check off; skip pid files whose `cmd=` is `rl/strength/run_watch.sh`.)

### 2. The data files, `.gitignore` and `floor_with.py` are not in the folder (blocker to run; safe as is)
- **Where:** sitting1.sh:246 (DATAFILES), 439 (HELPERS); sitting2.sh:216, 346; pin_rules.sh:91, 232, 248.
- **What is wrong:** `switch2.env`, `allowed_engine_files.tsv`, `engine_commits.tsv`, `counters.tsv`, `floor_7c.tsv`,
  `reuse.tsv`, `tools_8c.tsv`, `.gitignore` and `floor_with.py` are absent (spec section 0 and 9 assign them to implementers A
  and C). Every start refuses, which is correct. But both dry runs halt at their first data check (sitting1.sh:1324,
  sitting2.sh:1306), so none of the dry runs' safety checks (env, busy, push --dry-run, reserved names, staged files) has been
  exercised. `git check-ignore` confirms nothing in the folder is ignored yet.
- **Failure scenario:** none while they are missing (refusal). Once a run starts with a `.gitignore` that is not Oct 1's, the
  lock, `.ours`, `.pgid`, `quiet.log`, `*.part` and `*.broken_*` files show in GitHub Desktop, which selects every changed file
  for its next commit.
- **Smallest fix:** write them as the spec says (`.gitignore` and `floor_with.py` byte copies, blobs ff44c03a and 7e4880fe),
  then run both dry runs.

### 3. Sitting 1 commits before it checks origin; sitting 2 does not (should fix)
- **Where:** sitting1.sh:583-598 (`checkpoint`: ckpt_commit at 588, then ckpt_push at 590) and 607-631 (`record_commit`: commit
  at 620, push at 625). sitting2.sh has the Oct 1 fix: `origin_ahead` 514-522, used at 526 and 565.
- **What is wrong:** sitting 1 makes the local commit on main first and learns only at the push that origin/main moved.
- **Failure scenario:** during a 4-7 hour sitting 1, a commit reaches origin/main from another clone (a cloud session, or
  Sonnet's separate clone). The next checkpoint commits on the stale main, ckpt_push returns 2, the run stops (SITTING 1
  STOPPED), and the record commit adds a second local commit. Main and origin/main have diverged; GitHub Desktop's "Pull
  origin" then makes a merge commit on main, and on the next start `unpushed_check` refuses on that merge until it is pushed.
- **Smallest fix:** copy sitting2.sh's `origin_ahead` and its two guards (526-528, 565-568, with `not_pushed ... uncommitted`)
  into sitting1.sh's `checkpoint` and `record_commit`.

### 4. A data-entry slip found at step 4 becomes a permanent HALT (should fix)
- **Where:** sitting1.sh: the START line (1533) is written before the fresh step 4 (1581-1607), whose checks halt: `p_checks`
  656-658, 686, 689 and, through `soft` (500-502, a halt outside the dry run), 661-685; `reserved_check` 703; `merge_tree` 640;
  `candidate_checks` 726-741.
- **What is wrong:** spec 1.2: "A mismatch is 'start refused' (before any candidate exists) or a HALT (after)". Here, before
  any candidate or game, a wrong value in `switch2.env` or a tsv is a HALT, written to STATUS.txt and PIN_STATUS.txt, committed
  and pushed.
- **Failure scenario:** at finalize time `P_TREE` is copied from the wrong commit (PLAN's status line names 140c0be2's tree
  8d71f693), or `allowed_engine_files.tsv` misses a file that (e) or (a) added. Sitting 1 writes "SITTING 1 HALT ... step 4".
  Every later start then needs `SITTING1_AFTER_HALT`, and the pin needs Dustin's words in `PIN_AFTER_HALT`
  (pin_rules.sh:360-362, which matches any `^SITTING [12] HALT` line ever written) for a typo made before any game.
- **Smallest fix:** in a fresh start (no `candidate.txt`, no CREF), run `p_checks`, `reserved_check`, `merge_tree` and
  `candidate_checks` (on the merge tree, as the dry run does at 1345-1349) before the START line, with a flag that makes
  `halt` and `soft` call `refuse` (exit 2, nothing recorded).

### 5. Sitting 1 does not refuse while sitting 2 holds its lock (should fix)
- **Where:** sitting1.sh:1440-1480 (no test of `.sitting2.lock`; the unstage at 1472-1480); compare sitting2.sh:1291-1298
  (`s1_lock_held`) and 1477.
- **What is wrong:** the only guard against a live sitting 2 is the busy check, which sees a plainly started sitting 2 only
  while one of its game programs runs.
- **Failure scenario:** sitting 2 runs from a plain start (the documented fallback) and is between games, inside a checkpoint
  after `git reset <commit> -- <paths>` and before `update-ref`. A chain `sitting1.sh && sitting2.sh` is started (sitting 1 is
  DONE). Sitting 1 passes its refusals and unstages those paths (`git reset -q -- ...`, 1478) before it reads its DONE line
  (1529). When sitting 2's update-ref lands, the shared index holds the old blobs for its paths: GitHub Desktop shows them as
  staged reverts, and the next commit through the shared index (the combined chain's `commit()` or a person's) records them
  reverted.
- **Smallest fix:** copy `s1_lock_held` as `s2_lock_held` into sitting1.sh and refuse when it is held, before the unstage.

### 6. Step 8-seeds writes three kept files without `.part` (should fix; small window)
- **Where:** sitting2.sh:1611 (`cp -- "$PRIV/$f" "$O/$f"` for pairs_8b2.tsv and pairs_will.tsv) and 1618 (seeds_8_2.txt);
  the next start compares them at 1610 and 1617 and halts on a difference. Sitting 1's equivalent uses `.part` + `mv` (1158).
- **Failure scenario:** a WSL restart or power-off during the copy, or before its fsync (`/mnt/c` is 9p to NTFS), leaves a
  truncated file. The next start halts ("is here but is not what ... writes now"), a HALT on record that again needs
  `SITTING2_AFTER_HALT` and, at the pin, Dustin's `PIN_AFTER_HALT`.
- **Smallest fix:** `cp -- "$PRIV/$f" "$O/$f.part"; durable "$O/$f.part"; mv -- "$O/$f.part" "$O/$f"` (the old runner had the
  same pattern for one file; the copy adds a second).

### 7. ALLOW_DAYTIME=1 is the default on weekdays too (note)
- **Where:** sitting1.sh:444, 1456-1461; sitting2.sh:351, 1482-1487.
- **What is wrong:** the brief asked for a daytime start allowed by default (Dustin's word covers the weekend), but the default
  also holds Monday to Friday.
- **Failure scenario:** after Monday's hard stop at 10:15 UTC (SITTING n STOPPED), the laptop session resumes the sitting at,
  say, 13:00 UTC. With DEADLINE=school the deadline becomes Tuesday 10:15 UTC, and 14 threads run through travel and Monday's
  class (1-4 pm Central = 18:00-21:00 UTC, PLAN line 315). PLAN line 28: "resumes Monday evening"; the laptop's quiet hours are
  class and travel.
- **Smallest fix:** when ALLOW_DAYTIME is not given, refuse a Monday-Friday start between 11:30 and 21:00 UTC (weekends stay
  open); an explicit ALLOW_DAYTIME=1 still overrides.

### 8. The pin's own gate is "8c_RESULT.txt committed"; it writes PREPARE DONE itself (note)
- **Where:** pin_rules.sh:829-833 (writes `PREPARE DONE $C` when absent) and 364-365 (only a PREPARE line for another
  candidate stops). Inherited from Oct 1 (old pin_rules.sh:592-594), with the comment that 8c_RESULT.txt takes its place.
- **What it means:** PLAN line 272's "after PREPARE DONE and your word" is not an independent gate: once 8c_RESULT.txt is
  committed in the right grammar and A8 = 0, the pin proceeds on Dustin's Oct 9 go. If the coordinator wants PREPARE DONE as
  the laptop session's own mark after its audit, require it (stop when it is absent) instead of writing it.

### 9. PIN_DUSTIN is any non-empty environment value (note)
- **Where:** pin_rules.sh:434-438, 441-444; update_manifest_rules.py:109-111, 202.
- **Failure scenario:** a `PIN_DUSTIN` left exported in a shell, or set by an agent from a paraphrase, satisfies the "judgment
  call waits for Dustin's word" gate when A8 > 0, and the text goes into the manifest's `approved` and the pin commit.
- **Smallest fix:** require the `PIN_DUSTIN` text to appear verbatim in the committed `8c_DECISION.md` (which the gate already
  requires when A8 > 0).

### 10. A start adopts and pushes any unpushed commit that touches only this folder or START_HERE.md (note)
- **Where:** sitting1.sh:1260-1269 and 1491; sitting2.sh:1278-1287 and 1521. Inherited from Oct 1.
- **Failure scenario:** another session commits a PLAN.md status note in this folder, or a seed-table reservation in
  START_HERE.md (as 2dfcb848 did), and has not pushed it yet. The start adds it to `.sitting*.ours`, and the first checkpoint
  pushes it as the run's own.
- **Smallest fix:** name the adopted commits in a refusal unless `ADOPT_UNPUSHED=<their ids>` is given, or accept only commits
  whose paths are the runner's HELPERS, the data files and START_HERE.md.

### 11. The pin is documented as fine without launch_detached (note)
- **Where:** pin_rules.sh:55-58 ("launch_detached is not needed"); 51-52 (after a hard kill mid-install, a person restores
  the files by hand).
- **Failure scenario:** the laptop session runs `wsl bash pin_rules.sh` inside a PowerShell tool call (2 min default, 10 min
  at most). If the call is cut during the merge's install or the pin's install and no trap runs, the working copy is left
  half-written with main unmoved, the case the header leaves to a person.
- **Smallest fix:** say in the usage to start the pin through `rl/strength/launch_detached.sh` (its own pid file is already
  exempt at 526), as the house rule asks for runs that must outlive the starting process.

### 12. update_manifest_rules.py's checks are `assert`s (note)
- **Where:** update_manifest_rules.py (40 asserts, e.g. 101-111, 122-127); pin_rules.sh:327 (env refusal).
- **Failure scenario:** with `PYTHONOPTIMIZE` set in the environment, every assert vanishes (the 8c grammar, the 40-zero result
  commit, PIN_DUSTIN, the MERGED line). The shell gates repeat most of them, so the exposure is small.
- **Smallest fix:** add `PYTHONOPTIMIZE` to the pin's environment refusal at 327.

---

## Checked, no finding
- **Deadline, Monday morning:** `school` gives the first Monday-Friday 10:15 UTC strictly after the start (a weekend start gets
  Monday's); HARD_STOP auto = the deadline (stopped by 10:15 UTC, before 11:30); PUSH_BY auto = deadline + 6,300 s = 12:00 UTC,
  used by `push_lim` (record pushes bounded to 120 s fetch / 360 s push); `off` disables the watchdog; a past deadline or hard
  stop only pauses or stops. PAUSED exits 3, so a `sitting1.sh && sitting2.sh` chain stops; "already DONE" exits 0.
- **launch_detached:** no re-exec when `LAUNCH_DETACHED_RUN` is set; no read from stdin anywhere (every `read` is from a file,
  here-string or heredoc); fetch and push run with `GIT_TERMINAL_PROMPT=0` under `timeout -k`; the HUP trap is a no-op under
  nohup, as documented; `.sitting*.pgid` stores the group leader's start time (field 22, index 19 checked); quiet.sh's `alive`
  works for a single sitting and for a `bash -c` chain naming both scripts; a TERM to the group is STOPPED with its record.
- **Resumability:** stale `.ckpt`/`.hardstop` flags removed after the lock; `/tmp` copies remade; game files kept only with a
  matching `.run` written after the synced rename; floor pages kept only with their `.run`; the candidate ref/`.part` window at
  step 4 is adopted; a lock file left by a kill makes the start wait 15 s and refuse with instructions; staged entries equal to
  the working copy (an interrupted checkpoint) are unstaged at the start.
- **Git:** no checkout, stash, reset --hard, clean, pull, merge, rebase or force anywhere; pushes are fast-forward of
  `main` only, after a fetch, and only of commits in `.sitting*.ours`; checkpoint commits come from a private index and are
  limited to this folder (`.sitting*`, `*.part` refused); the candidate is made with merge-tree/commit-tree and a
  `refs/pocketdecksim/` ref (never pushed); git identity passed with `-c`; `.gitattributes` is `* -text` (engine files never
  converted), and the pin writes engine files only from `git cat-file --filters` of the merge.
- **Nothing outside the allowed places is written by the sittings:** the old folder is only read (reused games, pairs files,
  carriers); `rm -rf` targets are `$B`/`$W` after `S` is checked as 7 hex, `$O/floor_7c/<page_id>` with page ids matching
  `^[A-Za-z0-9_]+$`, and mktemp folders; the dry runs write only in /tmp (symlinks there are removed with `rm -rf`, which does
  not follow them); the checkers write only their `--out` files; the manifest is read, never written, until the pin, which
  builds it in a scratch folder.
- **Refusing on unfilled values:** sitting 1 refuses on `P`, `P_TREE`, `COIN_SCRIPT_BLOB`, `SUITE_AT_P` and the marked tsvs;
  sitting 2 also on `MAGNEZONE_CARD_CHECK` and `tools_8c.tsv`; the pin on any `TO_FINALIZE` and any marked file; `ENGINE_DIR`
  may not be `rl/engine-2026-10-02`. Any `DECKGYM_*`, `PDL_EQUIV_DEALS` or `GOLDFISH_TRACE` in the environment refuses all three.
- **The pin:** holds both sitting locks; requires SITTING 1 and 2 DONE for the candidate, every STEP line and manifest, 8c's
  committed line with its sums, and Dustin's words for any HALT or judgment call; stops before any write on a clash; undoes an
  install on a stop; never pushes.
- **Disk:** build folders about 0.75 GB a candidate on a disk with 766 GB free; the evidence folder of Oct 1 was 166 MB, against
  27 GB free on `/mnt/c`.
