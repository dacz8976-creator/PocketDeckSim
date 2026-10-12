#!/usr/bin/env bash
# Rules switch 2, sitting 2: PLAN.md (this folder) steps 8b, the trace-load gate, 8, 9 and 10 (section 5, its step table and
# "Two sittings"), on sitting 1's candidate and programs, never rebuilt. A copy of the Oct 1 switch's sitting2.sh
# (../engine_switch_rules_2026-10/sitting2.sh: the same framework, refusals, checkpoints, deadline and watchdog), adapted by
# ADAPTATION_SPEC.md (Oct 9; items S2-1 to S2-32). Dustin, Oct 9: "1-3 sure" (the go, "update if everything passes"; the
# scope and the new reference games as recommended) and "Alright it is fine to use the laptop over the weekend" (PLAN lines
# 24-29); the pin still waits for his word on any judgment call. Nothing is built, nothing is pinned and the manifest is not
# touched. The shared working copy is never checked out, switched, stashed or reset, and no engine file is edited; the
# checkpoint commits come from a private index (checkpoint.sh, a byte copy of Oct 1's).
# What was adapted from Oct 1's (everything else is Oct 1's, unchanged):
#   - this folder (REL) and Oct 1's (OLDREL: read in place, never written); the build folders engine-rules2-<S>;
#   - the fixed names come from the data files here (switch2.env, counters.tsv, tools_8c.tsv, reuse.tsv; read with a regex,
#     never sourced or run): a start refuses while a file or key it needs is marked TO FINALIZE (P is not final yet), and
#     the dry run notes each one;
#   - the candidate comes from candidate.txt (two parents: main, then P; engine/ = P's tree), not a constant; the old side
#     is the official engine main-8626a35 (rl/engine-2026-10-02/);
#   - step 8's carriers and 8b's rows 32-35 reuse Oct 1's recorded new-engine games as the old side (reuse.tsv; PLAN section
#     3: the same program on the same seeds); 8b plays the cloud's rows 32-37 (its own pairs file; 36-37 old here too)
#     and the new rows 40-46; step 8 adds the Will rows 60-62; step 9 names B2e pairings 32-39 and 80-87 (PLAN step 9 and
#     section 6);
#   - a changed game in a named row never halts the runner: it gets a category from its watch row (reach / offgate_only,
#     which is CONDITION 3 / other_only / none) and goes to 8c's hand-off (ADAPTATION_SPEC 1.12 and A7: Oct 1's halt on a
#     changed game "with every repair counter 0" is dropped; the cloud's k3 pairing 37 i 35 changed with no counter at all
#     and was explained in look-ahead). A deal that is not the same deal on the three sides still halts;
#   - the laptop's 8b rows must equal the cloud's (PLAN step 8b, precondition d): 8b compares them with P's
#     early_warning_8b/ files itself (a difference halts); the gate's CLOUD8B lines stay as an extra;
#   - the deadline (school mornings only, a parameter), the hard stop at the deadline, the push-by time, ALLOW_DAYTIME,
#     BUSY_OK, the environment check (no DECKGYM_* revert switch may be set), launch_detached, exit code 3 for PAUSED, and
#     "sitting 1 is not DONE" is a refusal (exit 2), not a halt.
#
#   Before any step, a refusal (exit 2, no HALT line, before the START line): switch2.env, counters.tsv, tools_8c.tsv and
#      reuse.tsv readable and committed as they are, and no file or key sitting 2 needs marked TO FINALIZE (switch2.env's P,
#      P_TREE, COIN_SCRIPT_BLOB, SUITE_AT_P and MAGNEZONE_CARD_CHECK; counters.tsv, tools_8c.tsv, reuse.tsv,
#      allowed_engine_files.tsv, engine_commits.tsv, floor_7c.tsv); sitting 1 DONE: candidate.txt names C and main,
#      STATUS.txt's last sitting 1 state is "SITTING 1 DONE <C>" with STEP 4/5/6/7/7b/7c-seeds/7c DONE lines for S (C's first
#      7 characters); counters.tsv is the one sitting 1's last START line recorded (its sha256: the reach roles that sorted
#      step 7c's changed games sort 8b's, 8's and 9's); every 8c tool of tools_8c.tsv is the blob it names at the commit it
#      names; MAGNEZONE_CARD_CHECK's <commit>:<path> is here (PLAN step 8b, "after the cloud's card checks"); counters.tsv
#      reads as the model sitting2_check.py knows (its 12 verdict groups cover the reach2 counters); no DECKGYM_* variable,
#      PDL_EQUIV_DEALS or GOLDFISH_TRACE is set (at P the engine reads its revert switches from the environment: one left set
#      would play another engine with every program hash passing); with BUSY_OK=0 nothing else runs (no legality_scan,
#      deckgym, goldfish, cargo, rustc, tool_census or strength outside this run's process group, no process of a long run
#      that $HOME/runs/watch.list names, its PATTERN or its CHAIN script, and no other live launch_detached run, a
#      run_watch.sh watcher aside); the committed START_HERE.md has a line holding 23,300,000,000 and 36–37 and the
#      23,100,000,000 row holds 36–37; and Oct 1's refusals (below). A path under this folder that P's tree holds and main or
#      the working copy holds with other bytes (the pin's merge would conflict, ADAPTATION_SPEC 1.10) is a NOTE here, in the
#      START line and PIN_STATUS.txt: step 4 and the pin stop on it.
#   Then (a halt if not): C's parents are candidate.txt's main and P, and C's engine/ and P's are P_TREE; step_4 ...
#      step_7c.sha256 still verify (and again at every checkpoint); the programs are sitting 1's, never rebuilt: B =
#      /home/dacz8976/engine-rules2-<S> (deckgym, examples/legality_scan, examples/goldfish) and W = engine-rules2-watch-<S>
#      (the watch legality_scan), both COMMIT files C, programs.sha256 and watch.sha256 verify; the old programs
#      rl/engine-2026-10-02/ have switch2.env's sha256, equal their SHA256SUMS and are the manifest's available release
#      (main-8626a35). The program checks run again before and after every step (a halt). Sitting 1's references
#      (<S>_refs.sha256, in B/ref) and inputs (<S>_inputs.sha256) are checked once at the start, a NOTE on drift and never a
#      halt: sitting 2 reads none of those files.
#   Inputs and references by step: <S>_inputs2.sha256 holds every file a sitting-2 game reads, in three groups: 8b and 8
#      (Oct 1's pairs_8.tsv, the reused games of reuse.tsv, and the decks of pairs_8.tsv, pairs_8b_cloud.tsv, pairs_8b2.tsv
#      and pairs_will.tsv), 9 (its pairs files and their decks), 10 (altaria, blaziken, the panel, the two brews,
#      run_screen.py). Before and after a step only its own group is checked (a change halts); at the start a DONE step's
#      group is checked as a NOTE. <S>_refs2.sha256 likewise: step 9's references before and after step 9, step 10's before
#      and after step 10.
#   8-seeds (no game): after a fetch (at most 2 min), Oct 1's files are checked in place (reuse.tsv: each file's sha256 and
#      its games, the complete set of deals for its bot, and its .run record naming the old legality_scan, 97891274..., with
#      Oct 1's command; pairs_8.tsv the blob switch2.env records; the decks of Oct 1's seeds_8.txt its blobs; each committed
#      as it is) and the cloud's pinned rows 32-35 must equal Oct 1's reused ones (sitting2_check.py cloud8b, 160 a bot; no
#      game). The cloud's pairs file is copied byte for byte from P (git cat-file; blob checked) to pairs_8b_cloud.tsv
#      (pairings 32-37, one seed block, 23,100,000,000, its rows 32-35 Oct 1's pairs_8.tsv's; P's decks_sha256.txt equal to
#      the working copy for every deck it names), water_round2.txt from P to scratch_8b2/ (blob checked); pairs_8b2.tsv
#      (pairings 40-46) and pairs_will.tsv (60-62) are written (sitting2_check.py pairs; 23,300,000,000 + pairing x 10,000 +
#      i), and seeds_8_2.txt (both blocks: every row's seeds per bot, every deck with its blob, the reused files with their
#      sha256); each is made again and compared when it is here. <S>_refs2.sha256: step 9's and step 10's references, taken
#      from C into B/ref2 (blob-checked; step 9's six and the goldfish page and coverage also with the sha256 recorded when
#      they were made). <S>_inputs2.sha256 (above). "STEP 8-seeds DONE" and a checkpoint, before any game.
#   8b The early-warning rows (2,800 games), km3 then k3, 40 deals: the cloud's rows 32-37 (pairs_8b_cloud.tsv, seeds
#      23,100,000,000): new and watch on all six, old (the official legality_scan, rl/engine-2026-10-02/) on 36-37 only, the
#      old side of 32-35 being Oct 1's reused games; then the new rows 40-46 (pairs_8b2.tsv, seeds 23,300,000,000): old, new
#      and watch. Old and new run with cwd B/engine, watch with cwd W/engine, each --pairs <file> --root <repo> --seed-base
#      <its block>. Per bot and row set: (a) watch equals new on every field new records (switch_check.py same); (b)
#      sitting2_check.py touched (old v new v watch): the three sides hold the same deals, each the same deal (pairing, i,
#      seed, seat, bots, decks); every changed game is listed with its category and the counters that fired
#      (handoff_8b_cloud_<bot>.tsv, handoff_8b_new2_<bot>.tsv), never a halt by itself; the reach of each counter goes to
#      touched_8b.txt. A RULE finding on an OLD-build page is noted as evidence (the old engine has the bugs the switch
#      repairs); on a new or watch page it halts. Then this run's rows v the cloud's own at P (early_warning_8b/): new 32-37
#      v 8b_new_<bot>.jsonl (240 a bot) and old 36-37 v 8b_pinned_<bot>.jsonl (80 a bot), on every field both record, the
#      paths aside: a difference, or rows that cannot be compared, halts (PLAN step 8b). Then sitting2_check.py stepsum
#      (into touched_8b.txt and the STEP line): one reach verdict per mechanic (12: "reached in N games (M ticks)" or
#      "UNREACHED (rests on its tests)", a report), the uncounted parts, the off-gate counters in identical games (a report),
#      the categories, "changed <N> of <M> deals (<K> with no reach2 counter)" and the CONDITION 3 count (a pin-gate item,
#      never a stop).
#   8c The gate before step 8 (no game; read after 8b, and again after step 10 when it waited; PLAN section 5's trace-load gate, as-is):
#      trace_load.txt here, committed unchanged, read by sitting2_check.py trace-gate ("TRACE LOAD <n> <text naming the cloud
#      commit>", and a "DUSTIN ..." line when the load is above 50; the load is n, the cloud's, which covers its rows 32-37
#      only, plus the laptop's own 8b rows 40-46 with no reach2 counter, from their hand-off rows; the checker prints the id
#      it parsed on a marked line "COMMIT <id>",
#      which is checked with git cat-file -e). Optional lines "CLOUD8B <commit> <bot> <path-in-commit>" (the cloud's
#      NEW-build rows, pairings 32-37, compared with <S>_8b_cloud_new_<bot>.jsonl, 240 deals) and "CLOUD8B_OLD <commit> <bot>
#      <path>" (its pinned rows, filtered to 36-37, compared with <S>_8b_cloud_old_<bot>.jsonl, 80 deals): a matched deal that
#      differs halts; other deals: "not compared (owed)". The reading, with the laptop's own 8b count beside the declared
#      load n, goes to gate_8c.txt, STATUS.txt and PIN_STATUS.txt (its words reworded like an anchored line's). When it
#      passes after 8b, step 8 runs then only if it fits before the deadline; otherwise (or when it waits) steps 9 and 10 run
#      first and the gate is read again; if it then passes and step 8 fits, step 8 runs in the same run. Only if it still
#      waits does the run end "SITTING 2 PAUSED ... step 8 waits for 8c's trace load"; a later start runs step 8 only.
#   8  The carriers and the Will rows (54,750 games): Oct 1's pairings 0-31 (its pairs_8.tsv, in place; seeds
#      23,100,000,000), km3 i < 500 then k3 i < 250, new and watch, the old side being Oct 1's reused games (16,000 and
#      8,000); then the Will rows 60-62 (deck 10, brew-01 and brew-04 v t-weezing; pairs_will.tsv, seeds 23,300,000,000),
#      km3 i < 500 then k3 i < 250, old, new and watch; the same checks and stepsum as 8b; touched_8.txt,
#      handoff_8_<bot>.tsv and handoff_8_will_<bot>.tsv. Its STEP line carries the real count of changed games and of those
#      with no reach2 counter (the real trace load, before 8c), the verdicts, the categories and the CONDITION 3 count.
#      At every checkpoint handoff_8c.tsv and handoff_8c.md (every changed game of 7c, 8b, 8 and 9; what 8c needs to trace
#      them) and touched_check.txt (touched_7c + 8b + 8 + 9) are rebuilt.
#   9  km3's coverage baselines (74,500 games) on the new legality_scan, each v its reference in km_tables_2026-09-30 (from
#      C, blob-checked, sha256 as recorded): B2e 48,000, Scizor 4,000, the 4 second lists 14,500 (SPEC9, as on Oct 1; the dry
#      run checks that each reference holds exactly those games, pairings, seed base and bots). B2e's 80 pairings without
#      Ariados (40,000), Scizor and the second lists must equal their references: a difference halts (identity_9.txt). The
#      16 named pairings (32-39 h-whimsicott, 80-87 deck 12; PLAN step 9) may change: the watch build plays them (8,000),
#      watch must equal plain there, and sitting2_check.py touched (the reference as the old side) lists their changed games
#      for 8c (handoff_9_km3.tsv, touched_9.txt); then stepsum 9.
#   10 deckgym simulate 240 games for k3, kp3, kog3, kta3 and km3 (from the repository, no RAYON_NUM_THREADS) v
#      engine_switch_2026-09-30/14c39f4_cli_<code>.txt on every line but line 6 (the wall time), with k3 150/90/0, kp3
#      144/96/0, kog3 149/91/0; goldfish --coverage byte-equal to 14c39f4_goldfish.txt and _coverage.json; run_screen under
#      km3 on brew-06 and 06b (screen_with.py, the new deckgym) v floor_recheck_2026-09-30/run_screen.txt. identity_10.txt;
#      the outputs are <S>_10_*. (PLAN step 10, as-is.)
#   Then "SITTING 2 DONE <C> <time>" (and REPLAYS DONE in PIN_STATUS.txt; the prepare-done mark is not this runner's: it
#   waits for 8c, and the runner never writes those two words, which older scripts grep for anywhere in PIN_STATUS.txt),
#   or, when step 8 still waits for the trace load, "SITTING 2 PAUSED ...". identity_check.txt is rebuilt as identity_7 +
#   7c + 9 + 10. Games: 2,800 + 54,750 + 74,500 + 5,040 = 137,090 (PLAN section 3, "about 137,000"; 8b is 480 above PLAN
#   step 8b's 2,320 because of the cloud's rows 36-37, ADAPTATION_SPEC A5).
# Seeds (START_HERE's seed table): 23,100,000,000 + pairing x 10,000 + i for Oct 1's step 8 pairings 0-31 and the cloud's
# 8b rows 32-37 (36-37 registered by switch 2's row); 23,300,000,000 + pairing x 10,000 + i for 8b's 40-46 and step 8's
# 60-62 (sitting 1's 7c used 0-23); step 9 keeps km_tables_2026-09-30's seeds. The blocks are switch2.env's.
#
# STATUS.txt (the same file as sitting 1's): a timestamped note per action and these anchored lines, at column 0:
#   SITTING 2 START <time> <S>: ...                       every start
#   STEP <n> DONE <S> <time> <summary>                     n = 8-seeds, 8b, 8, 9, 10; then its checkpoint. The lines of
#                                                          8b, 8 and 9 hold the phrase "changed <N> of <M> deals" once
#   SITTING 2 HALT <time> <S>: step <n>: <why>            a check failed (an identity difference in a row named equal,
#                                                          watch not equal to new, a missing, extra or repeated deal, a
#                                                          deal that is not the same deal on the three sides, a malformed
#                                                          counter, the laptop's 8b rows not equal to the cloud's, a RULE
#                                                          finding, a crash, a program, reference, input or evidence file
#                                                          that differs from its record). A later start refuses until
#                                                          SITTING2_AFTER_HALT='<written reason>'.
#   SITTING 2 STOPPED <time> <S>: step <n>: <why>         the script could not carry on (a fetch, git or checkpoint
#                                                          failure, a push it may not make, a stop signal, the hard stop):
#                                                          not a result; a plain restart resumes at that step.
#   SITTING 2 PAUSED <time> <S>: ...                      the next step could not finish before the deadline, or step 8
#                                                          waits for the trace load; a plain start resumes.
#   SITTING 2 DONE <C> <time>                              every step passed.
#   SITTING 2 NOT PUSHED <time> <S>: <why>                after the record commit, when it could not be made or pushed.
#   HALT, STOPPED, PAUSED, DONE and NOT PUSHED also go to PIN_STATUS.txt. The run's state is the last line matching
#   ^SITTING 2 (HALT|STOPPED|PAUSED|DONE) (sitting 1's lines never count). No FAILED or MISMATCH in them (pin.sh's rule).
#   Exit codes (ADAPTATION_SPEC 1.5): 0 DONE or already DONE; 1 HALT or STOPPED; 2 a refused start or usage; 3 PAUSED, so
#   that "sitting1.sh && sitting2.sh" under launch_detached stops on a pause.
# Checkpoints, the push rules, the deadline and the watchdog are sitting1.sh's (its header says how), with this run's
# names: commits "Rules switch 2 sitting 2, <title> (rl/results/engine_switch_rules2_2026-10 only)", the body naming
# "Candidate <C> (main <M7> + P <P7>)"; the commits a push may carry in .sitting2.ours; the flags .sitting2.ckpt and
# .sitting2.hardstop; the lock .sitting2.lock (fd 9). DEADLINE default school: the first Monday-Friday SCHOOL_CUT (10:15 UTC,
# 5:15 am CDT) after the start, so no new game after it (PLAN line 28; a start on Saturday or Sunday gets Monday's; weekend
# mornings have no cut); HARD_STOP auto = the deadline itself (a step still going then stops cleanly: its STOPPED record is
# committed and pushed, and a plain start resumes it); PUSH_BY auto = the deadline + 105 min (12:00 UTC, 7:00 am CDT), which
# bounds the pushes made after the deadline. Before each checkpoint commit (and the record commit) a fetch (bounded as the
# push's): when origin/main has commits main lacks, nothing is committed and the run stops (SITTING 2 STOPPED, what to do;
# the record is left uncommitted with a NOT PUSHED line), so main never needs a merge.
# Every start refuses (with what to do, exit 2) when: the refusals above; sitting2.sh, a helper (sitting2_check.py,
# sitting1_check.py, switch_check.py, checkpoint.sh, quiet.sh, .gitignore, ../engine_switch_2026-09-30/screen_with.py) or a
# data file it reads is not committed as it is; sitting1.sh's lock is held by a live run (flock -n on .sitting1.lock); the
# working copy is not on main; a git lock file stays 15 s; files in this folder are staged and differ from the working copy;
# origin/main (after a fetch of at most 2 min) has commits main lacks; main carries unpushed commits that are not this
# switch's (only non-merge commits touching this folder and START_HERE.md alone are allowed: the runner's own and the seed
# row); the last sitting 2 run halted (SITTING2_AFTER_HALT); it is daytime (11:30-21:00 UTC) without an explicit DEADLINE
# and ALLOW_DAYTIME=0, or ALLOW_DAYTIME=auto (the default) on a Monday-Friday.
# Files written outside this folder: B/ref2 (the references of steps 9 and 10), the private copies in /tmp (removed at the
# end), the checkpoint commits on main (pushed), and the shared index. The shared index is written in two places, both
# inherited from sitting1.sh and recorded in Oct 1's README.md as its one exception: checkpoint.sh sets the entries of
# exactly the committed paths to the new commit's, and a start unstages files of this folder that are staged with the
# working copy's own content (what an interrupted checkpoint leaves; git reset -q -- <those paths>). Nothing else in it is
# touched. The working files .sitting2.* are in .gitignore here (and checkpoint.sh refuses them). Oct 1's folder is only read.
#
# Usage (WSL), after sitting2.sh, its helpers and the data files are committed (ADAPTATION_SPEC 1.9):
#   R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
#   bash "$R/rl/strength/launch_detached.sh" start rules2-sitting2 --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/sitting2.sh"
#   or both sittings in one run (exit 3 = PAUSED, like a halt or a refusal, stops the chain):
#   bash "$R/rl/strength/launch_detached.sh" start rules2-sittings --dir "$R" -- bash -c 'bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules2_2026-10/sitting1.sh" && bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules2_2026-10/sitting2.sh"'
#   launch_detached gives the run its own session and process group (setsid nohup, stdin /dev/null, no tty, the log
#   $HOME/runs/<NAME>.log, LAUNCH_DETACHED_RUN set), so the re-execution under setsid is skipped there; a plain
#   "bash sitting2.sh" still re-executes itself under setsid. .sitting2.pgid holds the run's real process group (the chain's
#   bash -c when chained), which the watchdog and quiet.sh act on. "launch_detached.sh stop <NAME>" (TERM to the group) is a
#   STOPPED; a plain start resumes at the step boundary, also after a WSL restart (complete game files are reused, the /tmp
#   copies are made again, stale .ckpt and .hardstop flags are removed).
#   bash sitting2.sh --dry-run    git and file checks only: no fetch, game, commit or file here; usable before P is final
#                                 and before sitting 1 (it notes each TO FINALIZE mark, and without sitting 1's candidate
#                                 takes the decks and references from main and the cloud's files from P, or from P's
#                                 branch tip while P is TO FINALIZE; the 8c tools at tools_8c.tsv's own commits, blob-
#                                 checked); pairs_8b2.tsv and pairs_will.tsv made in
#                                 /tmp, every deck blob checked; the trace load read when trace_load.txt is here; git push
#                                 --dry-run (no write)
#   SITTING=2 bash quiet.sh pause|resume|stop|status   quiet.sh acts on the process group in .sitting2.pgid and waits out
#       .sitting2.ckpt (a byte copy of Oct 1's; a start refuses until it is committed here).
# Knobs (environment; ADAPTATION_SPEC 1.3): THREADS 14, NICE 10, DEADLINE school (or HH:MM UTC, the next one after the
#   start; an ISO time; off), SCHOOL_CUT 10:15 (UTC, for school), HARD_STOP auto (the deadline; or HH:MM, ISO, off), PUSH_BY
#   auto (the deadline + 105 min; or HH:MM, ISO), ALLOW_DAYTIME auto (a start between 11:30 and 21:00 UTC without an
#   explicit DEADLINE is allowed on Saturday and Sunday, Dustin's weekend, and refused Monday-Friday, class and travel; 1
#   allows it any day; 0 refuses it any day, as Oct 1), BUSY_OK 0 (1 starts beside another game program or long run,
#   noted), RATE 8.6 (games a second before 2,000 are timed in timing.tsv; sitting 1's rows count), SAFETY 1.25,
#   OVERHEAD_MIN 10, SITTING2_AFTER_HALT (above).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules2_2026-10
OLDREL=rl/results/engine_switch_rules_2026-10   # Oct 1's switch: its reused games, pairs_8.tsv, seeds_8.txt, carriers/ and scratch_8b/ are read in place, never written
O="$R/$REL"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[ "$HERE" -ef "$O" ] || { echo "sitting2.sh: run the copy in $O (this one is in $HERE)" >&2; exit 2; }
DRY=0
case "${1:-}" in "") ;; --dry-run) DRY=1;; *) echo "usage: bash sitting2.sh [--dry-run]" >&2; exit 2;; esac
if [ $DRY -eq 0 ] && [ -z "${SITTING2_REEXEC:-}" ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ] && [ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]; then
  SITTING2_REEXEC=1 exec setsid bash "$O/sitting2.sh" "$@"   # a plain start: its own process group (quiet.sh and the watchdog act on it)
fi
PG=$(ps -o pgid= -p $$ | tr -d ' ')   # the run's process group: its own, or launch_detached's (the chain's bash -c when chained)

# ---- The data files (committed here; read with a regex, never sourced or run; ADAPTATION_SPEC 1.2 and Appendix A).
DATA_FILES=(switch2.env counters.tsv tools_8c.tsv reuse.tsv allowed_engine_files.tsv engine_commits.tsv floor_7c.tsv)
DATA_READ=(switch2.env counters.tsv tools_8c.tsv reuse.tsv)             # the ones sitting 2 reads (private copies in a run)
NEED_KEYS=(P P_TREE COIN_SCRIPT_BLOB SUITE_AT_P MAGNEZONE_CARD_CHECK)   # a start refuses while one is TO_FINALIZE
HEX40_KEYS=(OFFICIAL OFFICIAL_TREE CLOUD8B_PAIRS_BLOB OLD_PAIRS_8_BLOB WATER_ROUND2_BLOB D_FIRST_BLOB VS_SCRIPT_BLOB)
HEX64_KEYS=(OLD_DECKGYM_SHA256 OLD_LEGALITY_SCAN_SHA256 OLD_GOLDFISH_SHA256)
WORD_KEYS=(P_BRANCH OLD_RELEASE_NAME OLD_DIR CLOUD8B_DIR SEED_OLD_BLOCK SEED_NEW_BLOCK)
declare -gA E2=() REUSE8=() REUSE8B=() SEEDS8_BLOB=()
MARKS=(); DATA_WHY=""; REUSE_ROWS=(); TOOL_ROWS=(); REUSE_PATHS=()
tsv_head() { sed '1s/^\xEF\xBB\xBF//' "$1" | tr -d '\r' | grep -v -m 1 -E '^#|^$' || true; }   # a data file's header row
tsv_rows() { sed '1s/^\xEF\xBB\xBF//' "$1" | tr -d '\r' | awk '/^#/ || !NF {next} !h {h = 1; next} {print}'; }   # its rows
read_data() {  # E2 (switch2.env), REUSE_ROWS, TOOL_ROWS; MARKS: what is TO FINALIZE; DATA_WHY: what cannot be read as it must
  local f ln n=0 k v re='^([A-Z0-9_]+)=([^ ]*)$' rmc='^[0-9a-f]{7,40}:[^ ]+$'
  E2=(); MARKS=(); DATA_WHY=""; REUSE_ROWS=(); TOOL_ROWS=()
  for f in "${DATA_FILES[@]}"; do
    if [ ! -s "$O/$f" ]; then DATA_WHY+="$f is missing; "; continue; fi
    v=$(sed -n '1{s/^\xEF\xBB\xBF//;p;q}' "$O/$f")   # its first line (the marker's place)
    if [[ $v == '# TO FINALIZE'* ]]; then MARKS+=("$f: the file is marked TO FINALIZE"); fi
  done
  if [ -s "$O/switch2.env" ]; then
    while IFS= read -r ln || [ -n "$ln" ]; do
      n=$((n + 1)); ln=${ln%$'\r'}; [ $n -ne 1 ] || ln=${ln#$'\xEF\xBB\xBF'}
      case $ln in ''|'#'*) continue;; esac
      if [[ $ln =~ $re ]]; then E2[${BASH_REMATCH[1]}]=${BASH_REMATCH[2]}
      else DATA_WHY+="switch2.env line $n is not KEY=VALUE (no spaces, no quotes); "; fi
    done < "$O/switch2.env"
    for k in "${NEED_KEYS[@]}"; do
      v=${E2[$k]:-}
      if [ -z "$v" ]; then DATA_WHY+="switch2.env has no $k; "
      elif [ "$v" = TO_FINALIZE ]; then MARKS+=("switch2.env: $k is TO FINALIZE"); fi
    done
    for k in "${HEX40_KEYS[@]}"; do [[ ${E2[$k]:-} =~ ^[0-9a-f]{40}$ ]] || DATA_WHY+="switch2.env's $k is not 40 hex; "; done
    for k in "${HEX64_KEYS[@]}"; do [[ ${E2[$k]:-} =~ ^[0-9a-f]{64}$ ]] || DATA_WHY+="switch2.env's $k is not 64 hex; "; done
    for k in "${WORD_KEYS[@]}"; do [ -n "${E2[$k]:-}" ] || DATA_WHY+="switch2.env has no $k; "; done
    for k in P P_TREE; do v=${E2[$k]:-}; [ -z "$v" ] || [ "$v" = TO_FINALIZE ] || [[ $v =~ ^[0-9a-f]{40}$ ]] || DATA_WHY+="switch2.env's $k is neither 40 hex nor TO_FINALIZE; "; done
    for k in SEED_OLD_BLOCK SEED_NEW_BLOCK; do [[ ${E2[$k]:-} =~ ^[1-9][0-9]{6,}$ ]] || DATA_WHY+="switch2.env's $k is not a seed block; "; done
    v=${E2[MAGNEZONE_CARD_CHECK]:-}; [ -z "$v" ] || [ "$v" = TO_FINALIZE ] || [[ $v =~ $rmc ]] || DATA_WHY+="switch2.env's MAGNEZONE_CARD_CHECK is not <commit>:<path>; "
  fi
  if [ -s "$O/reuse.tsv" ]; then
    [ "$(tsv_head "$O/reuse.tsv")" = $'path\tsha256\tgames\tbot\tpairings\tdeals' ] || DATA_WHY+="reuse.tsv's header is not: path sha256 games bot pairings deals; "
    mapfile -t REUSE_ROWS < <(tsv_rows "$O/reuse.tsv")
  fi
  if [ -s "$O/tools_8c.tsv" ]; then
    [ "$(tsv_head "$O/tools_8c.tsv")" = $'role\tpath\tcommit\tblob' ] || DATA_WHY+="tools_8c.tsv's header is not: role path commit blob; "
    mapfile -t TOOL_ROWS < <(tsv_rows "$O/tools_8c.tsv")
    [ ${#TOOL_ROWS[@]} -gt 0 ] || DATA_WHY+="tools_8c.tsv names no tool; "
  fi
}
set_names() {  # the fixed names from E2 and REUSE_ROWS (DATA_WHY grows when one is not as it must be)
  local x path sha games bot pl deals
  P=${E2[P]:-}; P_TREE=${E2[P_TREE]:-}; P_BRANCH=${E2[P_BRANCH]:-}; PX=$P; PXT=$P_TREE   # PX: P, or (dry run) P's branch tip
  OFFICIAL=${E2[OFFICIAL]:-}; OFFICIAL_TREE=${E2[OFFICIAL_TREE]:-}
  OLD_NAME=${E2[OLD_RELEASE_NAME]:-}; OLD_DIR=${E2[OLD_DIR]:-}
  OLDP="$R/$OLD_DIR"; OLD_GYM="$OLDP/deckgym"; OLD_SCAN="$OLDP/legality_scan"; OLD_GOLD="$OLDP/goldfish"
  OLD_SHA=("$OLD_GYM" "${E2[OLD_DECKGYM_SHA256]:-}" "$OLD_SCAN" "${E2[OLD_LEGALITY_SCAN_SHA256]:-}" "$OLD_GOLD" "${E2[OLD_GOLDFISH_SHA256]:-}")
  SEED_OLD=${E2[SEED_OLD_BLOCK]:-0}; SEED_NEW=${E2[SEED_NEW_BLOCK]:-0}
  CLOUD8B_DIR=${E2[CLOUD8B_DIR]:-}; CLOUD_PAIRS_BLOB=${E2[CLOUD8B_PAIRS_BLOB]:-}; OLD_PAIRS8_BLOB=${E2[OLD_PAIRS_8_BLOB]:-}
  WATER_BLOB=${E2[WATER_ROUND2_BLOB]:-}; D_FIRST_BLOB=${E2[D_FIRST_BLOB]:-}; MAGCHK=${E2[MAGNEZONE_CARD_CHECK]:-}
  REUSE8=(); REUSE8B=(); REUSE_PATHS=()
  [ -s "$O/reuse.tsv" ] || return 0
  for x in "${REUSE_ROWS[@]}"; do
    IFS=$'\t' read -r path sha games bot pl deals <<< "$x"
    if ! [[ $path == "$OLDREL"/*.jsonl && $sha =~ ^[0-9a-f]{64}$ && $games =~ ^[0-9]+$ && $bot =~ ^(km3|k3)$ && $deals =~ ^[0-9]+$ ]]; then
      DATA_WHY+="reuse.tsv's row '${x//$'\t'/ }' is not: <a .jsonl in $OLDREL> <sha256> <games> <km3|k3> <pairings> <deals>; "; continue
    fi
    REUSE_PATHS+=("$path")
    case $pl in
      0-31) [ -z "${REUSE8[$bot]:-}" ] || DATA_WHY+="reuse.tsv has two $bot rows for pairings 0-31; "; REUSE8[$bot]=$path;;
      32-35) [ -z "${REUSE8B[$bot]:-}" ] || DATA_WHY+="reuse.tsv has two $bot rows for pairings 32-35; "; REUSE8B[$bot]=$path;;
      *) DATA_WHY+="reuse.tsv's $path: pairings $pl are neither 0-31 (step 8) nor 32-35 (8b); ";;
    esac
  done
  for bot in km3 k3; do
    [ -n "${REUSE8[$bot]:-}" ] || DATA_WHY+="reuse.tsv has no $bot row for step 8's pairings 0-31; "
    [ -n "${REUSE8B[$bot]:-}" ] || DATA_WHY+="reuse.tsv has no $bot row for 8b's pairings 32-35; "
  done
}
data_sums() { local f out=""; for f in "${DATA_FILES[@]}"; do [ ! -s "$O/$f" ] || out+="$f $(sha256sum < "$O/$f" | cut -c1-16), "; done; printf '%s' "${out%, }"; }
commas() { local s=$1 out=""; while [ ${#s} -gt 3 ]; do out=",${s: -3}$out"; s=${s:0:${#s}-3}; done; printf '%s' "$s$out"; }
expand_pl() {  # "0-31" or "32-35,40": a comma list of pairings
  local part; local -a parts=() out=()
  IFS=',' read -r -a parts <<< "$1"
  for part in "${parts[@]}"; do
    if [[ $part =~ ^([0-9]+)-([0-9]+)$ ]]; then mapfile -t -O "${#out[@]}" out < <(seq "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")
    else out+=("$part"); fi
  done
  (IFS=,; printf '%s' "${out[*]}")
}

# ---- The fixed names (the others come from the data files: set_names).
S1_STEPS=(4 5 6 7 7b 7c)                 # sitting 1's steps with a manifest (step_<n>.sha256): they must still verify
S1_LINES=(4 5 6 7 7b 7c-seeds 7c)        # its STEP lines (7c-seeds has no manifest, as on Oct 1)
CREF=refs/pocketdecksim/rules-switch2-candidate   # sitting 1's ref for the candidate (a note when it is elsewhere)
WATER_SRC=rl/results/coin_prevention_round2_2026-10-01/smoke/water_round2.txt   # in P: 8b's row 44 (to scratch_8b2/)
WATER_DST=scratch_8b2/water_round2.txt
CLOUD_PAIRS=pairs_8b_cloud.tsv           # the cloud's early_warning_8b/pairs_8b.tsv, copied from P (that path is P's: ADAPTATION_SPEC 1.10)
P8=$(seq -s, 0 31)                       # step 8's carriers: Oct 1's pairs_8.tsv rows (23,100,000,000); Oct 1's games are the old side
P8B_CLOUD=32,33,34,35,36,37; P8B_PLAYED=36,37   # 8b: the cloud's rows (32-35 Oct 1's scratch rows, old side reused; 36-37 brew-07, brew-09 v t-altaria)
P8B_NEW=40,41,42,43,44,45,46             # 8b's new rows (pairs_8b2.tsv, 23,300,000,000)
PWILL=60,61,62                           # step 8's Will rows (pairs_will.tsv, 23,300,000,000)
NAMED9=32,33,34,35,36,37,38,39,80,81,82,83,84,85,86,87   # step 9's B2e pairings named as expected to change (PLAN step 9 and section 6)
# Step 9, one scan per line: name|pairs file|seed base|pairings|games|reference in km_tables_2026-09-30|its sha256|label.
# As run_km.sh part R (lines 883-912) ran them, km3 both sides, 500 deals: checked by hand on Oct 1 against
# km_config.json:61-80 and run_km.sh part R (the dry run checks each reference holds these games, pairings, seed base).
KMT=rl/results/km_tables_2026-09-30; GR=rl/results/gauntlet_runs_2026-09-26/tsv
SPEC9=(
 "cov_b2e_km3|rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv|21106000000|$(seq -s, 0 95)|48000|1f6319e_b2e_km3.jsonl|fa6fcaf5a4d219a1b4a9ad4ddd4cb0dbb83bc8498481c9ee69390dbfad863b63|9 km3 B2e, pairings 0-95 (b2e_pairings.tsv, seeds 21,106,000,000 + 10,000 x pairing + i)"
 "cov_scizor_km3|$GR/new_decks.tsv|21108000000|0,1,2,3,4,5,6,7|4000|1f6319e_scizor_km3.jsonl|5e0a5e0179e6eb9dbfe40d0ea4c4e14aa7faf516fcf91510432681ca8da6273b|9 km3 Scizor, pairings 0-7 (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)"
 "cov_var_v-lucario_2_km3|$GR/var_v-lucario_2.tsv|72000000|2,8,13,18,19,20,21|3500|1f6319e_var_v-lucario_2_km3.jsonl|824bcdf69c35c08c5a36e9c055d7b62f35991bd39fc300b24e1abad4c358f3fe|9 km3 second list v-lucario_2 (seeds 72,000,000 + 10,000 x pairing + i)"
 "cov_var_v-suicune_2_km3|$GR/var_v-suicune_2.tsv|72000000|4,10,15,19,22,25,26|3500|1f6319e_var_v-suicune_2_km3.jsonl|90b1160ddd52a0afacfdc20b366beda100f1d882106063b9d45949b8898c65ed|9 km3 second list v-suicune_2 (seeds 72,000,000 + 10,000 x pairing + i)"
 "cov_var_v-weezing_2_km3|$GR/var_v-weezing_2.tsv|72000000|6,12,17,21,24,26,27|3500|1f6319e_var_v-weezing_2_km3.jsonl|aa5786d463d7fa37d5e0c2097e397985c5b6fae5ad7a1a0ae55b3fb94865cd91|9 km3 second list v-weezing_2 (seeds 72,000,000 + 10,000 x pairing + i)"
 "cov_var_l-charizardy_km3|$GR/var_l-charizardy.tsv|21106000000|40,41,42,43,44,45,46,47|4000|1f6319e_var_l-charizardy_km3.jsonl|caca2523e930820a32fb3df84e3322d98cafdb9fc54f5bbdc3ff9b129ff02df3|9 km3 second list l-charizardy, pairings 40-47 (seeds 21,106,000,000 + 10,000 x pairing + i)"
)
P9F=(); for x in "${SPEC9[@]}"; do IFS='|' read -r _ p _ <<< "$x"; P9F+=("$p"); done
mapfile -t P9F < <(printf '%s\n' "${P9F[@]}" | awk '!seen[$0]++')
IFS='|' read -r B2E_NAME B2E_PAIRS B2E_SEED _ _ B2E_REF _ <<< "${SPEC9[0]}"   # the B2e scan: its named 16 pairings are watched too
# Step 10.
E30=rl/results/engine_switch_2026-09-30
CLI_P0=decks/research/altaria.txt; CLI_P1=decks/research/blaziken.txt; CLI_CODES=(k3 kp3 kog3 kta3 km3)
BREW06=decks/brews/brew-06-pyukumuku-silvally-payback.txt; BREW06B=decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt
SCREEN_WITH=$E30/screen_with.py; SCREEN_REF=rl/results/floor_recheck_2026-09-30/run_screen.txt
# Sitting 2's references (taken from the candidate into B/ref2, blob-checked), by step: path|sha256 it must have (step
# 9's six and the goldfish page and coverage: recorded when they were made; run_screen.txt: the value given on Oct 1, no
# earlier record; the command-line outputs: empty, blob-checked only). Every one's sha256 is recorded now in refs2.
REFS9=(); REFS10=()
for x in "${SPEC9[@]}"; do IFS='|' read -r _ _ _ _ _ ref sha _ <<< "$x"; REFS9+=("$KMT/$ref|$sha"); done
for x in "${CLI_CODES[@]}"; do REFS10+=("$E30/14c39f4_cli_$x.txt|"); done
REFS10+=("$E30/14c39f4_goldfish.txt|d944c62f9da2e57c74d9ab9260959f10d6df10d3b40b012cec88863a0b46f923"
         "$E30/14c39f4_goldfish_coverage.json|1be7855491d1ff6f09a62f2d42ae2dd80743732adf47eadc8bde86c58f315a8e"
         "$SCREEN_REF|c66b656b69e8620f3fe186f295d52296bc7dd04ee51d0a2f183113c61385ce3a")
REFS2=("${REFS9[@]}" "${REFS10[@]}")
HELPERS=(sitting2.sh sitting2_check.py sitting1_check.py switch_check.py checkpoint.sh quiet.sh .gitignore "${DATA_READ[@]}")

# ---- Knobs (ADAPTATION_SPEC 1.3, 1.4).
DL_GIVEN=${DEADLINE:+1}   # DEADLINE given explicitly (with ALLOW_DAYTIME=0, a daytime start needs it)
THREADS=${THREADS:-14}; NICE=${NICE:-10}; DEADLINE=${DEADLINE:-school}; SCHOOL_CUT=${SCHOOL_CUT:-10:15}
HARD_STOP=${HARD_STOP:-auto}; PUSH_BY=${PUSH_BY:-auto}; ALLOW_DAYTIME=${ALLOW_DAYTIME:-auto}; BUSY_OK=${BUSY_OK:-0}
RATE=${RATE:-8.6}; SAFETY=${SAFETY:-1.25}; OVERHEAD_MIN=${OVERHEAD_MIN:-10}
for x in "$THREADS" "$NICE" "$OVERHEAD_MIN"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "sitting2.sh: knob value $x is not a whole number" >&2; exit 2; }
done
for x in "$RATE" "$SAFETY"; do
  [[ $x =~ ^[0-9]+(\.[0-9]+)?$ ]] && awk -v v="$x" 'BEGIN {exit !(v > 0)}' || { echo "sitting2.sh: knob value $x is not a positive number" >&2; exit 2; }
done
[[ $ALLOW_DAYTIME =~ ^(0|1|auto)$ && $BUSY_OK =~ ^[01]$ ]] || { echo "sitting2.sh: ALLOW_DAYTIME is 0, 1 or auto; BUSY_OK is 0 or 1" >&2; exit 2; }
daytime_refused() {  # a start now, 11:30-21:00 UTC without an explicit DEADLINE, refused: always with ALLOW_DAYTIME=0; with
  local t   # auto (the default) on Monday-Friday only (Dustin's word covers the weekend; a weekday is class and travel)
  [ -z "$DL_GIVEN" ] || return 1
  t=$(date -u +%H%M); [ "$t" -ge 1130 ] && [ "$t" -lt 2100 ] || return 1
  [ "$ALLOW_DAYTIME" = 0 ] || { [ "$ALLOW_DAYTIME" = auto ] && [ "$(date -u +%u)" -le 5 ]; }
}
[[ $SCHOOL_CUT =~ ^[0-2][0-9]:[0-5][0-9]$ ]] || { echo "sitting2.sh: SCHOOL_CUT=$SCHOOL_CUT is not HH:MM (UTC)" >&2; exit 2; }
to_epoch() {  # spec start-epoch: HH:MM (UTC; the next one after the start), an ISO time, or off (0)
  local s=$1 t d
  case $s in
    off) echo 0;;
    [0-2][0-9]:[0-5][0-9]) d=$(date -u -d "@$2" +%F) && t=$(date -u -d "$d $s" +%s) || return 1
                           [ "$t" -gt "$2" ] || t=$((t + 86400)); echo "$t";;
    *) date -u -d "$s" +%s;;
  esac
}
deadline_of() {  # spec start-epoch: school = the first Monday-Friday SCHOOL_CUT (UTC) strictly after the start; else to_epoch
  local k d t dow
  [ "$1" = school ] || { to_epoch "$1" "$2"; return; }
  for k in 0 1 2 3 4 5 6 7; do
    d=$(date -u -d "@$(( $2 + k * 86400 ))" +%F) && t=$(date -u -d "$d $SCHOOL_CUT" +%s) && dow=$(date -u -d "$d" +%u) || return 1
    if [ "$dow" -le 5 ] && [ "$t" -gt "$2" ]; then echo "$t"; return 0; fi
  done
  return 1
}
fmt() { if [ "$1" -gt 0 ]; then date -u -d "@$1" +%FT%TZ; else echo off; fi; }
T0=$(date +%s)
DL=$(deadline_of "$DEADLINE" "$T0") || { echo "sitting2.sh: DEADLINE=$DEADLINE is not school, HH:MM, an ISO time or off" >&2; exit 2; }
if [ "$HARD_STOP" = auto ]; then HS=$DL   # 0 when DEADLINE=off
else HS=$(to_epoch "$HARD_STOP" "$T0") || { echo "sitting2.sh: HARD_STOP=$HARD_STOP is not auto, HH:MM, an ISO time or off" >&2; exit 2; }; fi
if [ "$PUSH_BY" = auto ]; then if [ "$DL" -gt 0 ]; then PB=$((DL + 6300)); else PB=0; fi
else PB=$(to_epoch "$PUSH_BY" "$T0") || { echo "sitting2.sh: PUSH_BY=$PUSH_BY is not auto, HH:MM or an ISO time" >&2; exit 2; }; fi
KNOBS="threads $THREADS, nice $NICE, deadline $(fmt "$DL") ($DEADLINE$([ "$DEADLINE" != school ] || echo ": the next Monday-Friday $SCHOOL_CUT UTC")), hard stop $(fmt "$HS") ($HARD_STOP), push by $(fmt "$PB") ($PUSH_BY), daytime start $ALLOW_DAYTIME (auto: weekends only; 1 always; 0 never, without an explicit DEADLINE), busy ok $BUSY_OK, rate $RATE before measurement, safety $SAFETY, overhead $OVERHEAD_MIN min"

# ---- Notes, stops and the anchored lines.
S=""; C=""; MAIN_C=""; CB=""; STEP=start; FINISHED=0; RECORD=0; LOCKED=0; PLAYED=0; REUSED=0; PRIV=""; WD=""; HALT_FILES=()
HALTED=0; CKPT_ALL=(); DONE_STEPS=(); KEEP_FILES=(); BAD=""; STEP_FILES=(); B=""; W=""; GYM=""; SCAN=""; GOLD=""; WSCAN=""
PIN_GYM=""; GATE_WHY="not read"; REFSUM=""; INPUTS=""; REFSUM2=""; INPUTS2=""; BLOBS2_OK=0; DRYTMP=""; S1_WHY=""; SEED_CLOUD=""
PINS="$O/programs.sha256"; WPINS="$O/watch.sha256"; CK="$O/switch_check.py"; CK2="$O/sitting1_check.py"; CK3="$O/sitting2_check.py"
CNT="$O/counters.tsv"; ENVF="$O/switch2.env"; TOOLSF="$O/tools_8c.tsv"; REUSEF="$O/reuse.tsv"   # the private copies once a run has started
SW="$R/$SCREEN_WITH"
CKPT_OURS="$O/.sitting2.ours"   # the commits this switch's sitting-2 runs made or a start allowed: the only ones a push may carry
export CKPT_OURS
ts() { date -u +%FT%TZ; }
note() { if [ $DRY -eq 1 ]; then echo "$*"; else echo "$(ts) $*" >> "$O/STATUS.txt"; fi; }
pin_note() { if [ $DRY -eq 1 ]; then echo "(PIN_STATUS) $*"; else echo "$(ts) $*" >> "$O/PIN_STATUS.txt"; fi; }
reword() {  # text: FAILED / MISMATCH reworded (pin.sh stops on them); for anchored lines and pasted or quoted words
  local l=$*
  l=${l//FAILED open or read/missing or unreadable}; l=${l//FAILED/does not match its record}; l=${l//MISMATCH/mismatch}
  printf '%s' "$l"
}
state_line() {  # the anchored line, in both files, reworded
  local l
  l=$(reword "$*")
  if [ $DRY -eq 1 ]; then echo "$l"; else echo "$l" >> "$O/STATUS.txt"; echo "$l" >> "$O/PIN_STATUS.txt"; fi
}
halt() { state_line "SITTING 2 HALT $(ts) ${S:-?}: step $STEP: $*"; FINISHED=1; RECORD=1; HALTED=1; exit 1; }
durable() {  # files...: fsync them before they are renamed into place or recorded (/mnt/c is 9p to NTFS)
  sync -- "$@" 2> /dev/null || note "sync (fsync) of ${*##*/} did not succeed; carrying on"
}
leftovers() {  # the untracked files left in this folder (GitHub Desktop shows them as changes; a restart reuses them)
  local l n
  l=$(git -C "$R" ls-files --others --exclude-standard -- "$REL" 9>&- 2> /dev/null) || return 0
  l=$(grep -v "^$REL/\.sitting2\." <<< "$l" || true)   # this run's own working files (also in .gitignore since Oct 1)
  n=$(grep -c . <<< "$l" || true)
  if [ "$n" -eq 0 ]; then echo "; no untracked file is left here"; return 0; fi
  echo "; $n untracked files are left here (not committed; a restart reuses the complete game files among them): $(sed "s#^$REL/##" <<< "$l" | head -n 8 | tr '\n' ' ')$([ "$n" -le 8 ] || echo "...")"
}
die() {
  local hs=""
  [ ! -e "$O/.sitting2.hardstop" ] || hs=" (the watchdog's hard stop at $(fmt "$HS"): the step ran past its estimate, or the laptop slept and woke after the deadline; a plain start resumes it)"
  state_line "SITTING 2 STOPPED $(ts) ${S:-?}: step $STEP: $*$hs$(leftovers)"; FINISHED=1; RECORD=1; exit 1
}
on_exit() {
  local rc=$? why
  trap '' HUP INT TERM   # a second stop signal must not cut the record short (checkpoint.sh's index step included)
  set +e
  if [ -n "$WD" ]; then kill "$WD" 2> /dev/null; fi
  if [ $DRY -eq 0 ] && [ $LOCKED -eq 1 ]; then
    if [ "$FINISHED" -eq 0 ]; then
      if [ -e "$O/.sitting2.hardstop" ]; then
        why="the watchdog's hard stop at $(fmt "$HS") (the step ran past its estimate, or the laptop slept and woke after the deadline); nothing of this step is committed; a plain start resumes it, reusing its complete game files"
      else why="exit code $rc outside a check (a script, system or signal stop, not a result; see the log)"; fi
      state_line "SITTING 2 STOPPED $(ts) ${S:-?}: step $STEP: $why$(leftovers)"
      RECORD=1
    fi
    rm -f -- "$O/.sitting2.hardstop" "$O/.sitting2.ckpt"
    if [ "$RECORD" -eq 1 ] && [ -n "$PRIV" ]; then record_commit; fi
  fi
  if [ -n "$PRIV" ]; then rm -rf -- "$PRIV"; fi
  if [ -n "$DRYTMP" ]; then rm -rf -- "$DRYTMP"; fi
}
stopped_or_failed() {  # rc what: a stop signal is a stop (a restart plays it again); any other exit code is a halt
  local sig=$(( $1 - 128 )) name
  name=$(kill -l "$sig" 2> /dev/null || echo "?")
  case $1 in 129|130|137|143) die "$2 was stopped by signal $sig (SIG$name); a restart plays it again";; esac
  if [ "$1" -gt 128 ]; then halt "$2 ended on signal $sig (SIG$name): a program crash, not a stop"; fi
  halt "$2 exited with code $1"
}

# ---- The checkpoint commits (checkpoint.sh's functions; the copy in PRIV once the run has started).
SCANS8B=(); SCANS8=()
for x in km3 k3; do
  SCANS8B+=("8b_cloud_old_$x" "8b_cloud_new_$x" "8b_cloud_watch_$x" "8b_new2_old_$x" "8b_new2_new_$x" "8b_new2_watch_$x")
  SCANS8+=("8_new_$x" "8_watch_$x" "8_will_old_$x" "8_will_new_$x" "8_will_watch_$x")
done
SCANS9=("$B2E_NAME" 9_watch_b2e_km3)   # step 9's files in the hand-off: the plain B2e scan and the named rows' watch scan
HANDOFF_ROWS=(7c_km3 8b_cloud_km3 8b_cloud_k3 8b_new2_km3 8b_new2_k3 8_km3 8_k3 8_will_km3 8_will_k3 9_km3)
rebuild_combined() {  # identity_check.txt, touched_check.txt and the 8c hand-off from the per-step files there are
  local f; local -a a=() t=() h=() j=()
  for f in identity_7.txt identity_7c.txt identity_9.txt identity_10.txt; do [ ! -f "$O/$f" ] || a+=("$O/$f"); done
  for f in touched_7c.txt touched_8b.txt touched_8.txt touched_9.txt; do [ ! -f "$O/$f" ] || t+=("$O/$f"); done
  if [ ${#a[@]} -gt 0 ]; then cat -- "${a[@]}" > "$O/identity_check.txt"; fi
  if [ ${#t[@]} -gt 0 ]; then cat -- "${t[@]}" > "$O/touched_check.txt"; fi
  for f in "${HANDOFF_ROWS[@]}"; do [ ! -f "$O/handoff_$f.tsv" ] || h+=("$O/handoff_$f.tsv"); done
  if [ ${#h[@]} -gt 0 ] && [ -n "$PRIV" ] && [ -n "$S" ]; then
    for f in 7c2_old_km3 7c2_watch_km3 "${SCANS8B[@]}" "${SCANS8[@]}" "${SCANS9[@]}"; do [ ! -f "$O/${S}_$f.jsonl" ] || j+=("$O/${S}_$f.jsonl"); done
    for f in "${REUSE_PATHS[@]}"; do [ ! -f "$R/$f" ] || j+=("$R/$f"); done
    [ ! -f "$B/ref2/$KMT/$B2E_REF" ] || j+=("$B/ref2/$KMT/$B2E_REF")
    if ! python3 "$CK3" handoff --tsv "$O/handoff_8c.tsv" --md "$O/handoff_8c.md" --candidate "$C" --main "$MAIN_C" \
         --env "$ENVF" --tools "$TOOLSF" --counters "$CNT" --rows "${h[@]}" --files "${j[@]}" > "$PRIV/handoff.out" 2>&1; then
      note "the hand-off for 8c (handoff_8c.tsv, .md) could not be rebuilt: $(tail -n 1 "$PRIV/handoff.out")"
    fi
  fi
}
ckpt_list() {  # extra REL paths: CF, every file a checkpoint commits now
  local f; CF=()
  for f in STATUS.txt PIN_STATUS.txt timing.tsv identity_check.txt table_counters.txt touched_check.txt handoff_8c.tsv handoff_8c.md gate_8c.txt; do
    [ ! -f "$O/$f" ] || CF+=("$REL/$f")
  done
  CF+=("${CKPT_ALL[@]}" "${KEEP_FILES[@]}" "$@")
  mapfile -t CF < <(printf '%s\n' "${CF[@]}" | awk 'NF && !seen[$0]++')
}
done_files() {  # CKPT_ALL: every DONE step's files, each manifest checked again first (sitting 1's too, not re-listed);
  local n out; BAD=""; CKPT_ALL=()  # BAD: the steps whose files changed
  for n in "${S1_STEPS[@]}"; do
    out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$n.sha256" 2>&1) || BAD+="sitting 1's step $n ($(head -n 2 <<< "$out" | tr '\n' ' ')) "
  done
  for n in "${DONE_STEPS[@]}"; do
    if out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$n.sha256" 2>&1); then
      mapfile -t -O "${#CKPT_ALL[@]}" CKPT_ALL < <(manifest_files "$n")
    else BAD+="step $n ($(head -n 2 <<< "$out" | tr '\n' ' ')) "; fi
  done
  [ -z "$BAD" ]
}
push_lim() {  # max: the seconds a checkpoint's fetch may take (its push gets 3 x); past the deadline, a quarter of the
  local now l=$1  # time left until the push-by time (PUSH_BY: the deadline + 105 min, 7:00 am CDT, by default), at least 30 s
  now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ "$PB" -gt 0 ] && [ "$now" -ge "$DL" ]; then
    l=$(( (PB - now) / 4 )); [ "$l" -le "$1" ] || l=$1; [ "$l" -ge 30 ] || l=30
  fi
  echo "$l"
}
ckpt_msg() {  # title summary
  printf '%s\n' "Rules switch 2 sitting 2, $1 ($REL only)" "" "$2" "" \
    "Candidate ${C:-?} (main ${MAIN_C:0:7} + P ${P:0:7}). Checkpoint commit by $REL/sitting2.sh (PLAN.md steps 8b, the" \
    "trace-load gate, 8, 9, 10: the pairs and seeds before any game) from a private index. No engine file, no pin, the manifest untouched." "" \
    "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > "$PRIV/ckpt.msg"
}
ORIGIN_WHY=""
origin_ahead() {  # seconds: a bounded fetch, then true when origin/main has commits main lacks (ORIGIN_WHY says so)
  local m o f="fetched origin"
  GIT_TERMINAL_PROMPT=0 timeout -k 10 "$1" git -C "$R" fetch -q --no-auto-maintenance origin 9>&- 2> /dev/null \
    || f="the fetch failed or timed out (offline?), so origin/main as last fetched"
  m=$(git -C "$R" rev-parse -q --verify refs/heads/main 9>&-) || { ORIGIN_WHY="no main"; return 1; }
  o=$(git -C "$R" rev-parse -q --verify refs/remotes/origin/main 9>&-) || { ORIGIN_WHY="no origin/main"; return 1; }
  ORIGIN_WHY="origin/main ${o:0:7} has commits main ${m:0:7} lacks ($f)"
  ! git -C "$R" merge-base --is-ancestor "$o" "$m" 9>&-
}
checkpoint() {  # title summary [extra REL paths]: commit and push; a commit that cannot be made, or a push this run may not
  local title=$1 summary=$2 out push rc=0 prc=0; shift 2  # make (origin/main ahead, or another session's commit on main), stops the run
  done_files || halt "the evidence of $BAD changed since its checkpoint (found before the checkpoint \"$title\"; nothing more is committed)"
  if origin_ahead "$(push_lim 120)"; then  # committing now would leave main needing a merge: stop first, nothing committed
    die "$title: nothing committed: $ORIGIN_WHY. Main must equal origin/main by the push-by time, and the runner never pulls or merges: in GitHub Desktop, Fetch origin, Pull origin, Push origin; then start again (it checks this step's files and commits them with its first checkpoint)"
  fi
  rebuild_combined; ckpt_list "$@"; ckpt_msg "$title" "$summary"
  : > "$O/.sitting2.ckpt"
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then rm -f -- "$O/.sitting2.ckpt"; die "$title: the checkpoint commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"; fi
  push=$(ckpt_push "$R" "$(push_lim 300)" 2> "$PRIV/push.err") || prc=$?
  rm -f -- "$O/.sitting2.ckpt"
  case $prc in
    0) note "checkpoint ($title): $out (${#CF[@]} paths named); $push";;
    2) die "$title: committed on main ($out) but not pushed: $(push_why). Main must equal origin/main by the push-by time, and the runner never pulls: in GitHub Desktop, Fetch origin, Pull origin, Push origin; then start again (it resumes at the next step)";;
    3) die "$title: committed on main ($out) but not pushed: $(push_why). Once their owner has pushed them (or Dustin says they may go), start again (it resumes at the next step and pushes this run's commits)";;
    *) note "checkpoint ($title): $out (${#CF[@]} paths named); not pushed: $(push_why) (the run goes on; the next checkpoint pushes again)";;
  esac
}
push_why() {  # the reason ckpt_push gave: its "not pushed:" line (else the first lines of its stderr), without that prefix
  local l
  l=$(grep -m 1 '^not pushed: ' "$PRIV/push.err" 2> /dev/null) || l=$(head -n 2 "$PRIV/push.err" 2> /dev/null | tr '\n' ' ')
  echo "${l#not pushed: }"
}
not_pushed() {  # why: after the record commit, a line in both files (left uncommitted; the next start's first checkpoint commits it)
  local what="Fetch origin, Pull origin if it offers it, Push origin"   # why [uncommitted]
  [ "${2:-}" != uncommitted ] || what="Fetch origin, Pull origin if it offers it; then, in GitHub Desktop, Commit this folder's changed files and Push origin"
  state_line "SITTING 2 NOT PUSHED $(ts) ${S:-?}: $1; main $(git -C "$R" rev-parse --short refs/heads/main 9>&- 2> /dev/null), origin/main $(git -C "$R" rev-parse --short refs/remotes/origin/main 9>&- 2> /dev/null) (as last fetched). main must equal origin/main by the push-by time ($(fmt "$PB")): a person looks at the reason, then in GitHub Desktop $what"
}
record_commit() {  # on exit after HALT, STOPPED, PAUSED or DONE: best effort; a record that is not pushed gets a NOT PUSHED line
  local out push rc=0 prc=0 last f
  local -a extra=()
  for f in "${HALT_FILES[@]}"; do [ ! -f "$O/$f" ] || extra+=("$REL/$f"); done
  if [ "$HALTED" -eq 1 ]; then  # the halted step's files so far (the games that differ among them), so origin can trace it
    for f in "${STEP_FILES[@]}"; do [ ! -f "$O/$f" ] || extra+=("$REL/$f"); done
  fi
  last=$(grep -E '^SITTING 2 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" | tail -n 1 | cut -c1-300 || true)
  if ! done_files; then  # a DONE step's file changed: its files stay out of the record (checkpoint() halts on this)
    echo "$(ts) sitting2.sh: the record leaves out $BAD: those files changed since their checkpoint"
    echo "$(ts) the record commit leaves out $BAD: those files changed since their checkpoint" >> "$O/STATUS.txt"
  fi
  rebuild_combined; ckpt_list "${extra[@]}"; ckpt_msg "the record: ${last%% [0-9][0-9][0-9][0-9]-*}" "$last"
  if origin_ahead "$(push_lim 60)"; then  # as checkpoint(): no commit that would need a merge
    echo "$(ts) sitting2.sh: the record is not committed: $ORIGIN_WHY"
    not_pushed "the record is left uncommitted: $ORIGIN_WHY" uncommitted; return 0
  fi
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then
    echo "$(ts) sitting2.sh: the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"
    not_pushed "the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')" uncommitted; return 0
  fi
  push=$(ckpt_push "$R" "$(push_lim 120)" 2> "$PRIV/push.err") || prc=$?   # short: after a hard stop, the push-by time is near
  if [ $prc -eq 0 ]; then echo "$(ts) sitting2.sh: the record ($last): $out; $push"
  else
    echo "$(ts) sitting2.sh: the record ($last): $out; not pushed: $(push_why)"
    not_pushed "the record is committed ($out) but not pushed: $(push_why)"
  fi
}

# ---- Sitting 1's record, the programs, the references and the inputs.
s1_state() {  # S1_WHY: empty when sitting 1 is DONE for the candidate candidate.txt names (then C, MAIN_C and S are set)
  local c m last n
  S1_WHY=""
  [ -s "$O/candidate.txt" ] || { S1_WHY="candidate.txt is not here (sitting 1 writes it at step 4)"; return 0; }
  c=$(sed -n 's/^candidate //p' "$O/candidate.txt" | head -n 1 || true); m=$(sed -n 's/^main //p' "$O/candidate.txt" | head -n 1 || true)
  [[ $c =~ ^[0-9a-f]{40}$ && $m =~ ^[0-9a-f]{40}$ ]] || { S1_WHY="candidate.txt has no 'candidate <40 hex>' and 'main <40 hex>' lines"; return 0; }
  last=$(grep -E '^SITTING 1 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
  case $last in "SITTING 1 DONE $c "*) ;; *) S1_WHY="sitting 1's last state is not 'SITTING 1 DONE $c' (it is: ${last:-none})"; return 0;; esac
  for n in "${S1_LINES[@]}"; do
    grep -q "^STEP $n DONE ${c:0:7} " "$O/STATUS.txt" || { S1_WHY="STATUS.txt has no 'STEP $n DONE ${c:0:7}' line (sitting 1)"; return 0; }
  done
  C=$c; MAIN_C=$m; S=${C:0:7}
}
s1_checks() {  # sitting 1's evidence (after s1_state): the candidate commit, P and the manifests; a halt when one is not as recorded
  local out n x
  git -C "$R" cat-file -e "$C^{commit}" 9>&- 2> /dev/null || halt "the candidate $C is not in this repository"
  [ "$(git -C "$R" rev-parse -q --verify "$C^1" 9>&- || true)" = "$MAIN_C" ] || halt "the candidate's first parent is not candidate.txt's main ${MAIN_C:0:7}"
  [ "$(git -C "$R" rev-parse -q --verify "$C^2" 9>&- || true)" = "$PX" ] || halt "the candidate's second parent is not P ${PX:0:7} (switch2.env)"
  ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null 9>&- 2>&1 || halt "the candidate has more than two parents"
  [ "$(git -C "$R" rev-parse "$C:engine" 9>&-)" = "$PXT" ] || halt "the candidate's engine/ is not P's tree ${PXT:0:7}"
  [ "$(git -C "$R" rev-parse "$PX:engine" 9>&-)" = "$PXT" ] || halt "P's engine/ is not P_TREE ${PXT:0:7} (switch2.env)"
  for n in "${S1_STEPS[@]}"; do
    [ -s "$O/step_$n.sha256" ] || halt "sitting 1's step_$n.sha256 is missing"
    out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$n.sha256" 2>&1) \
      || halt "sitting 1's step $n evidence changed since its checkpoint: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  done
  x=$(git -C "$R" rev-parse -q --verify "$CREF" 9>&- || true)
  [ "$x" = "$C" ] || note "NOTE $CREF is ${x:-missing}, not the candidate $C (a note: candidate.txt and the commit decide)"
}
set_paths() {
  B=/home/dacz8976/engine-rules2-$S; W=/home/dacz8976/engine-rules2-watch-$S
  GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"; GOLD="$B/engine/target/release/examples/goldfish"
  WSCAN="$W/engine/target/release/examples/legality_scan"
  REFSUM="$O/${S}_refs.sha256"; INPUTS="$O/${S}_inputs.sha256"; REFSUM2="$O/${S}_refs2.sha256"; INPUTS2="$O/${S}_inputs2.sha256"
}
prog_sha() {  # program path: its recorded sha256 (programs.sha256 or watch.sha256; the old programs: switch2.env's)
  local f h="" fs=()
  for f in "$PINS" "$WPINS"; do [ ! -s "$f" ] || fs+=("$f"); done
  [ ${#fs[@]} -eq 0 ] || h=$(awk -v p="$1" 'substr($0, 67) == p {print substr($0, 1, 64); exit}' "${fs[@]}")
  if [ -z "$h" ]; then case $1 in "$OLD_GYM") h=${OLD_SHA[1]};; "$OLD_SCAN") h=${OLD_SHA[3]};; "$OLD_GOLD") h=${OLD_SHA[5]};; esac; fi
  printf '%s' "$h"
}
check_pins() {  # when: sitting 1's programs, as recorded (never rebuilt); the old ones are old_programs'
  local out p
  [ "$(cat "$B/COMMIT" 2> /dev/null)" = "$C" ] || halt "$B/COMMIT is not the candidate $C ($1)"
  [ "$(cat "$W/COMMIT" 2> /dev/null)" = "$C" ] || halt "$W/COMMIT is not the candidate $C ($1)"
  [ -s "$PINS" ] && [ -s "$WPINS" ] || halt "programs.sha256 or watch.sha256 is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$PINS" 2>&1) || halt "a program differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  out=$(sha256sum -c --quiet --strict -- "$WPINS" 2>&1) || halt "the watch build differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  for p in "$GYM" "$SCAN" "$GOLD" "$WSCAN"; do
    [ -n "$(awk -v p="$p" 'substr($0, 67) == p {print; exit}' "$PINS" "$WPINS")" ] || halt "$p has no line in programs.sha256 / watch.sha256 ($1)"
  done
}
old_programs() {  # the old programs (rl/engine-2026-10-02/) have switch2.env's sha256, equal their SHA256SUMS and the manifest's record
  local k got rec man
  for ((k = 0; k < ${#OLD_SHA[@]}; k += 2)); do
    got=$(sha256sum < "${OLD_SHA[k]}" | cut -c1-64) || halt "${OLD_SHA[k]} is missing"
    rec=$(awk -v n="${OLD_SHA[k]##*/}" '$2 == n {print $1}' "$OLDP/SHA256SUMS")
    [ "$got" = "${OLD_SHA[k+1]}" ] && [ "$rec" = "$got" ] || halt "${OLD_SHA[k]} has sha256 ${got:0:16}.., not ${OLD_SHA[k+1]:0:16}.. (switch2.env; its SHA256SUMS says ${rec:0:16}..)"
  done
  man=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["available_release"]; print(r["name"], r["sha256"], r["legality_scan_sha256"], r["goldfish_sha256"], r["artifact"], r["legality_scan"], r["goldfish"])' "$R/project_manifest.json") \
    || halt "project_manifest.json cannot be read"
  [ "$man" = "$OLD_NAME ${OLD_SHA[1]} ${OLD_SHA[3]} ${OLD_SHA[5]} $OLD_DIR/deckgym $OLD_DIR/legality_scan $OLD_DIR/goldfish" ] \
    || halt "the manifest's available release is not $OLD_NAME's programs ($OLD_DIR/): $man"
}
S1REC=""
s1_records() {  # sitting 1's references and inputs records, once at the start: drift is a NOTE (sitting 2 reads none of
  local out r i  # those files); S1REC says what was found
  if out=$(cd "$B/ref" 2> /dev/null && sha256sum -c --quiet --strict -- "$REFSUM" 2>&1); then r="verify"
  else r="NOTE drift, not a stop: $(head -n 3 <<< "$out" | tr '\n' ' ')"; fi
  if out=$(sha256sum -c --quiet --strict -- "$INPUTS" 2>&1); then i="verify"
  else i="NOTE drift, not a stop: $(head -n 3 <<< "$out" | tr '\n' ' ')"; fi
  S1REC="sitting 1's references (${REFSUM##*/}, in $B/ref): $r; its inputs (${INPUTS##*/}): $i (sitting 2 reads none of those files)"
}
step_group() { case $1 in 8b|8) echo 8;; 9) echo 9;; 10) echo 10;; *) echo "";; esac; }
group_rel() {  # group dir: the repository inputs of steps 8b and 8 (8), 9 or 10, relative, sorted; dir holds this folder's
  local f  # pairs files (pairs_8b_cloud.tsv, pairs_8b2.tsv, pairs_will.tsv: $O in a run, /tmp in the dry run)
  case $1 in
    8) printf '%s\n' "$OLDREL/pairs_8.tsv" "${REUSE_PATHS[@]}"
       python3 "$CK" pairs-decks "$R/$OLDREL/pairs_8.tsv" "$2/$CLOUD_PAIRS" "$2/pairs_8b2.tsv" "$2/pairs_will.tsv";;
    9) printf '%s\n' "${P9F[@]}"; python3 "$CK" pairs-decks "${P9F[@]/#/$R/}";;
    10) for f in "$R"/decks/screen/opponents/*.txt; do echo "${f#"$R"/}"; done
        printf '%s\n' "$CLI_P0" "$CLI_P1" "$BREW06" "$BREW06B" decks/screen/run_screen.py;;
  esac | LC_ALL=C sort -u
}
inputs2_rel() {  # dir: every sitting-2 input, relative, sorted (the three groups)
  { group_rel 8 "$1" && group_rel 9 "$1" && group_rel 10 "$1"; } | LC_ALL=C sort -u
}
inputs2_list() {  # dir: every sitting-2 input, absolute, sorted
  local f lst
  lst=$(inputs2_rel "$1") || return 1
  while IFS= read -r f; do echo "$R/$f"; done <<< "$lst"
}
io_problem() {  # step when mode why: a halt (the step about to run or just run) or a NOTE (a DONE step's inputs drifted)
  if [ "$3" = halt ]; then halt "$4 ($2)"; else note "NOTE ($2): $4; step $1 is DONE, so this is drift after its games, not a stop"; fi
}
check_inputs() {  # step when halt|note: the step's group of sitting 2's inputs, as <S>_inputs2.sha256 records them
  local g lst sub miss out="" f
  g=$(step_group "$1"); [ -n "$g" ] || return 0
  [ -s "$INPUTS2" ] || { io_problem "$1" "$2" "$3" "the inputs record ${INPUTS2##*/} is missing"; return 0; }
  lst=$(group_rel "$g" "$O" | while IFS= read -r f; do echo "$R/$f"; done) \
    || { io_problem "$1" "$2" "$3" "listing step $1's input files failed"; return 0; }
  sub=$(awk 'NR == FNR {w[$0] = 1; next} (substr($0, 67) in w)' <(printf '%s\n' "$lst") "$INPUTS2")
  miss=$(LC_ALL=C comm -23 <(printf '%s\n' "$lst") <(cut -c67- <<< "$sub" | LC_ALL=C sort))
  if [ -n "$miss" ]; then
    io_problem "$1" "$2" "$3" "step $1's input files are not all in ${INPUTS2##*/}: $(head -n 3 <<< "$miss" | sed "s#^$R/##" | tr '\n' ' ')"
  elif ! out=$(sha256sum -c --quiet --strict - <<< "$sub" 2>&1); then
    io_problem "$1" "$2" "$3" "an input file of step $1 changed: $(head -n 3 <<< "$out" | tr '\n' ' ')(${INPUTS2##*/})"
  fi
}
check_refs() {  # step when halt|note: the step's references in B/ref2, as <S>_refs2.sha256 records them
  local x sub n out=""; local -a want=()
  case $1 in
    9) for x in "${REFS9[@]}"; do want+=("${x%%|*}"); done;;
    10) for x in "${REFS10[@]}"; do want+=("${x%%|*}"); done;;
    *) return 0;;
  esac
  [ -s "$REFSUM2" ] || { io_problem "$1" "$2" "$3" "the references record ${REFSUM2##*/} is missing"; return 0; }
  sub=$(awk 'NR == FNR {w[$0] = 1; next} (substr($0, 67) in w)' <(printf '%s\n' "${want[@]}") "$REFSUM2")
  n=$(grep -c . <<< "$sub" || true)
  if [ "$n" != "${#want[@]}" ]; then
    io_problem "$1" "$2" "$3" "${REFSUM2##*/} lists $n of step $1's ${#want[@]} references"
  elif ! out=$(cd "$B/ref2" 2> /dev/null && sha256sum -c --quiet --strict - <<< "$sub" 2>&1); then
    io_problem "$1" "$2" "$3" "a reference of step $1 differs from ${REFSUM2##*/}: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  fi
}
step_io() {  # step when halt|note: check_inputs and check_refs for one step
  check_inputs "$@"; check_refs "$@"
}
expected_blob() {  # repository path: the blob it must be (Oct 1's carriers and scratch decks: its seeds_8.txt's; water_round2:
  local p=$1  # P's; D's first list: 9cc6667's; everything else the candidate's, CB: main's in a dry run before sitting 1)
  case $p in
    "$OLDREL"/carriers/*|"$OLDREL"/scratch_8b/*) printf '%s' "${SEEDS8_BLOB[$p]:-}";;
    "$REL/$WATER_DST") printf '%s' "$WATER_BLOB";;
    "$REL"/floor_7c/d_first/*) printf '%s' "$D_FIRST_BLOB";;
    *) git -C "$R" rev-parse -q --verify "$CB:$p" 9>&- || true;;
  esac
}
blob_check_inputs2() {  # root dir: every sitting-2 input is the blob it must be (this folder's own inputs read under root,
  local root=$1 i n=0 lst want got f; local -a RELS=()   # the rest in the repository): BLOBS2_OK
  lst=$(inputs2_rel "$2") || die "listing sitting 2's input files failed"
  mapfile -t RELS <<< "$lst"
  for i in "${RELS[@]}"; do
    case $i in "$REL"/*) f="$root/$i";; *) f="$R/$i";; esac
    [ -f "$f" ] || halt "input file $i is missing"
    want=$(expected_blob "$i")
    [ -n "$want" ] || halt "input $i has no blob it must be (in neither ${CB:0:7}, Oct 1's seeds_8.txt nor switch2.env)"
    got=$(git -C "$R" hash-object --no-filters -- "$f" 9>&-) || die "git hash-object $i"
    [ "$got" = "$want" ] || halt "input $i is ${got:0:7}, not the blob ${want:0:7} it must be (the candidate's; Oct 1's carriers/ and scratch_8b/ its seeds_8.txt's; water_round2 P's)"
    n=$((n + 1))
  done
  BLOBS2_OK=$n
}
write_inputs2() {
  local lst; local -a IN=()
  blob_check_inputs2 "$R" "$O"
  lst=$(inputs2_list "$O") || die "listing sitting 2's inputs"
  mapfile -t IN <<< "$lst"
  sha256sum -- "${IN[@]}" > "$INPUTS2.part" || die "sha256 of sitting 2's input files"
  durable "$INPUTS2.part"; mv -- "$INPUTS2.part" "$INPUTS2"
  note "sitting 2's inputs recorded (before any game): ${#IN[@]} files, ${INPUTS2##*/}; all $BLOBS2_OK are the blobs they must be (the candidate's; Oct 1's carriers/ and scratch_8b/ its seeds_8.txt's; water_round2 P's); each step checks its own group (8b and 8: Oct 1's pairs_8.tsv and reused games, and the decks of the four pairs files; 9: its pairs files and decks; 10: altaria, blaziken, the panel, the brews, run_screen.py) before and after it"
}
extract_refs2() {  # step 9's and step 10's references, from the candidate into B/ref2, blob-checked, sha256 as recorded
  local x p sha blob d got; local -a ps=()
  for x in "${REFS2[@]}"; do
    p=${x%%|*}; sha=${x#*|}
    d="$B/ref2/$p"; mkdir -p "$(dirname "$d")"
    blob=$(git -C "$R" rev-parse --verify -q "$C:$p" 9>&-) || halt "the reference $p is not in the candidate"
    git -C "$R" cat-file blob "$blob" > "$d.part" 9>&- || die "git cat-file $p"
    [ "$(git -C "$R" hash-object --no-filters -- "$d.part" 9>&-)" = "$blob" ] || die "$p: the extracted file is not the candidate's blob"
    got=$(sha256sum < "$d.part" | cut -c1-64)
    [ -z "$sha" ] || [ "$got" = "$sha" ] || halt "the reference $p has sha256 ${got:0:16}.., not the recorded ${sha:0:16}.."
    mv -- "$d.part" "$d"; ps+=("$p")
  done
  (cd "$B/ref2" && sha256sum -- "${ps[@]}") > "$REFSUM2.part" || die "sha256 of sitting 2's references"
  durable "$REFSUM2.part"; mv -- "$REFSUM2.part" "$REFSUM2"
  note "sitting 2's references taken from the candidate (git cat-file, blob-checked) into $B/ref2: ${#ps[@]} files (step 9's 6 km3 coverage baselines and step 10's goldfish page and coverage, each with the sha256 recorded when it was made; run_screen.txt and the 5 command-line outputs blob-checked, their sha256 recorded now), ${REFSUM2##*/}; step 9's are checked before and after step 9, step 10's before and after step 10"
}
seeds8_read() {  # SEEDS8_BLOB: the deck files Oct 1's seeds_8.txt lists with their blob ids (its "Deck files" section)
  local f b
  SEEDS8_BLOB=()
  while read -r f b; do SEEDS8_BLOB[$f]=$b; done < <(awk '/^Deck files/ {d = 1; next} d && NF == 2 && length($2) == 40 && $2 ~ /^[0-9a-f]+$/ {print $1, $2}' "$R/$OLDREL/seeds_8.txt" 2> /dev/null || true)
}
REUSE_NOTE=""
reuse_checks() {  # Oct 1's files read in place (PLAN section 3): as reuse.tsv, switch2.env and Oct 1's seeds_8.txt record them
  local x path sha games bot pl deals got run want f n=0 lst out   # (a halt if not)
  for f in "$OLDREL/pairs_8.tsv" "$OLDREL/seeds_8.txt"; do committed "$f" || halt "$f is not committed as it is (Oct 1's record, read in place)"; done
  got=$(git -C "$R" hash-object --no-filters -- "$R/$OLDREL/pairs_8.tsv" 9>&-) || die "git hash-object $OLDREL/pairs_8.tsv"
  [ "$got" = "$OLD_PAIRS8_BLOB" ] || halt "$OLDREL/pairs_8.tsv is ${got:0:7}, not the blob ${OLD_PAIRS8_BLOB:0:7} switch2.env records"
  seeds8_read
  [ ${#SEEDS8_BLOB[@]} -gt 0 ] || halt "$OLDREL/seeds_8.txt lists no deck file"
  lst=$(python3 "$CK" pairs-decks "$R/$OLDREL/pairs_8.tsv") || halt "pairs-decks on Oct 1's pairs_8.tsv"
  while IFS= read -r f; do [ -n "${SEEDS8_BLOB[$f]:-}" ] || halt "Oct 1's seeds_8.txt does not list $f, a deck of its pairs_8.tsv"; done <<< "$lst"
  for f in "${!SEEDS8_BLOB[@]}"; do
    [ -f "$R/$f" ] || halt "$f (Oct 1's seeds_8.txt) is missing"
    got=$(git -C "$R" hash-object --no-filters -- "$R/$f" 9>&-) || die "git hash-object $f"
    [ "$got" = "${SEEDS8_BLOB[$f]}" ] || halt "$f is ${got:0:7}, not the blob ${SEEDS8_BLOB[$f]:0:7} Oct 1's seeds_8.txt records (its games are the old side only on those decks)"
    n=$((n + 1))
  done
  for x in "${REUSE_ROWS[@]}"; do
    IFS=$'\t' read -r path sha games bot pl deals <<< "$x"
    run=${path%.jsonl}.run
    committed "$path" && committed "$run" || halt "$path or its .run record is not committed as it is (Oct 1's record, read in place)"
    got=$(sha256sum < "$R/$path" | cut -c1-64)
    [ "$got" = "$sha" ] || halt "$path has sha256 ${got:0:16}.., not reuse.tsv's ${sha:0:16}.."
    [ "$(grep -c . "$R/$path" || true)" = "$games" ] || halt "$path does not hold reuse.tsv's $games games"
    out=$(python3 "$CK" complete "$R/$path" --pairings "$(expand_pl "$pl")" --games "$deals" --seed-base "$SEED_OLD" \
          --bot-a "$bot" --bot-b "$bot" --pairs "$R/$OLDREL/pairs_8.tsv") || halt "$path is not the complete set of deals reuse.tsv names ($out)"
    [ "$(sed -n 1p "$R/$run")" = "legality_scan sha256 ${OLD_SHA[3]}" ] \
      || halt "$run does not name the old legality_scan (${OLD_SHA[3]:0:16}..): Oct 1's games are the old side only because that program played them"
    want=$(printf 'args'; printf ' %q' --pairs "$R/$OLDREL/pairs_8.tsv" --root "$R" --seed-base "$SEED_OLD" --bot "$bot" --pairings "$(expand_pl "$pl")" --games "$deals")
    [ "$(sed -n 3p "$R/$run")" = "$want" ] || halt "$run's command is not Oct 1's pairs_8.tsv, seed base $SEED_OLD, bot $bot, pairings $pl, $deals games"
  done
  REUSE_NOTE="Oct 1's files read in place hold: pairs_8.tsv ${OLD_PAIRS8_BLOB:0:7}; the $n decks of its seeds_8.txt are its blobs; ${#REUSE_ROWS[@]} reused game files (reuse.tsv) have their sha256 and games, are the complete deals for their bot, and their .run records name the old legality_scan ${OLD_SHA[3]:0:16}.. with Oct 1's command"
}
copy_blob() {  # blob dest label: the file at dest is that blob, byte for byte (written from git when it is not here)
  local blob=$1 d=$2 got
  if [ -e "$d" ]; then
    got=$(git -C "$R" hash-object --no-filters -- "$d" 9>&-) || die "git hash-object $3"
    [ "$got" = "$blob" ] || halt "$3 is here already and is ${got:0:7}, not the blob ${blob:0:7} (an edited copy?): move it away, then start again"
    return 0
  fi
  mkdir -p -- "$(dirname "$d")"
  git -C "$R" cat-file blob "$blob" > "$d.part" 9>&- || die "git cat-file $3"
  got=$(git -C "$R" hash-object --no-filters -- "$d.part" 9>&-) || die "git hash-object $3"
  [ "$got" = "$blob" ] || die "$3: the written file is not the blob ${blob:0:7}"
  durable "$d.part"; mv -- "$d.part" "$d"
}
cloud_base() {  # pairs file: the one seed block of its rows (seed_first - 10,000 x pairing); fails when the rows disagree
  awk -F'\t' 'NR == 1 {next} {gsub(/\r/, "")} NF {b = $7 - 10000 * $1; if (seen && b != base) bad = 1; base = b; seen = 1}
              END {if (!seen || bad) exit 1; printf "%.0f\n", base}' "$1"
}
CLOUD_NOTE=""
cloud_checks() {  # tmpdir: the cloud's 8b files at P (PX): the pairs file and water_round2 are the blobs switch2.env records,
  local t=$1 got pl base ds d want lst bot rc out   # the pairs file reads as it must, P's decks_sha256.txt matches the working
  CLOUD_NOTE=""                                     # copy, and the cloud's pinned rows 32-35 equal Oct 1's reused ones (no game)
  got=$(git -C "$R" rev-parse -q --verify "$PX:$CLOUD8B_DIR/pairs_8b.tsv" 9>&- || true)
  [ "$got" = "$CLOUD_PAIRS_BLOB" ] || halt "P ${PX:0:7}'s $CLOUD8B_DIR/pairs_8b.tsv is ${got:-missing}, not the blob ${CLOUD_PAIRS_BLOB:0:7} switch2.env records"
  got=$(git -C "$R" rev-parse -q --verify "$PX:$WATER_SRC" 9>&- || true)
  [ "$got" = "$WATER_BLOB" ] || halt "P ${PX:0:7}'s $WATER_SRC is ${got:-missing}, not the blob ${WATER_BLOB:0:7} switch2.env records"
  git -C "$R" cat-file blob "$CLOUD_PAIRS_BLOB" > "$t/$CLOUD_PAIRS" 9>&- || die "git cat-file the cloud's pairs file"
  [ "$(tsv_head "$t/$CLOUD_PAIRS")" = "$(head -n 1 "$R/$OLDREL/pairs_8.tsv" | tr -d '\r')" ] || halt "the cloud's pairs file's header is not Oct 1's pairs_8.tsv's"
  pl=$(tail -n +2 "$t/$CLOUD_PAIRS" | tr -d '\r' | awk -F'\t' 'NF {print $1}' | sort -n | paste -sd, - || true)
  [ "$pl" = "$P8B_CLOUD" ] || halt "the cloud's pairs file holds pairings ${pl:-none}, not $P8B_CLOUD"
  base=$(cloud_base "$t/$CLOUD_PAIRS") || halt "the cloud's pairs file's rows do not share one seed block (seed_first - 10,000 x pairing)"
  [ "$base" = "$SEED_OLD" ] || halt "the cloud's pairs file's seed block is $base, not $SEED_OLD: its rows 32-35 reuse Oct 1's deals on that block, and one scan takes one seed base (if the cloud moved 36-37 to another block, the runner needs a second 8b scan for them: that goes to the coordinator)"
  cmp -s <(awk -F'\t' 'NR > 1 && $1 >= 32 && $1 <= 35' "$t/$CLOUD_PAIRS" | tr -d '\r') <(awk -F'\t' 'NR > 1 && $1 >= 32 && $1 <= 35' "$R/$OLDREL/pairs_8.tsv" | tr -d '\r') \
    || halt "the cloud's pairs file's rows 32-35 are not Oct 1's pairs_8.tsv rows 32-35 (the reused games are those deals)"
  ds=$(git -C "$R" show "$PX:$CLOUD8B_DIR/decks_sha256.txt" 9>&- 2> /dev/null) || halt "P ${PX:0:7} has no $CLOUD8B_DIR/decks_sha256.txt"
  lst=$(python3 "$CK" pairs-decks "$t/$CLOUD_PAIRS") || halt "pairs-decks on the cloud's pairs file"
  while IFS= read -r d; do
    want=$(awk -v p="$d" '$2 == p {print $1; exit}' <<< "$ds")
    got=$(sha256sum < "$R/$d" | cut -c1-64) || halt "$d (the cloud's pairs file) is missing"
    [ -n "$want" ] && [ "$got" = "$want" ] || halt "$d is ${got:0:16}.. here, and the cloud's decks_sha256.txt says ${want:-nothing}: the laptop's 8b rows could not equal the cloud's"
  done <<< "$lst"
  for bot in km3 k3; do
    git -C "$R" show "$PX:$CLOUD8B_DIR/8b_pinned_$bot.jsonl" > "$t/cloud_pinned_$bot.jsonl" 9>&- 2> /dev/null \
      || halt "P ${PX:0:7} has no $CLOUD8B_DIR/8b_pinned_$bot.jsonl"
    rc=0; out=$(python3 "$CK3" cloud8b --new "$R/${REUSE8B[$bot]}" --cloud "$t/cloud_pinned_$bot.jsonl" --bot "$bot" \
                --pairings 32-35 --expect 160 --label "Oct 1's reused 8b $bot games (pairings 32-35) v the cloud's pinned rows at P") || rc=$?
    case $rc in
      0) CLOUD_NOTE+="$bot $(grep -oE '[0-9]+ of [0-9]+ deals equal' <<< "$out" | head -n 1 || true); ";;
      1) halt "Oct 1's reused 8b $bot games differ from the cloud's pinned rows (the official legality_scan) on pairings 32-35: $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1 | cut -c1-300)";;
      *) halt "Oct 1's reused 8b $bot games could not be compared with the cloud's pinned rows: $(tail -n 1 <<< "$out" | cut -c1-300)";;
    esac
  done
  CLOUD_NOTE="the cloud's pairs file ${CLOUD_PAIRS_BLOB:0:7} (pairings $P8B_CLOUD, seed block $base, rows 32-35 Oct 1's) and water_round2 ${WATER_BLOB:0:7} are in P ${PX:0:7}; its decks_sha256.txt matches the working copy for its $(grep -c . <<< "$lst") decks; Oct 1's reused 8b games equal the cloud's pinned rows on 32-35: ${CLOUD_NOTE%; }"
}

# ---- The other start checks (ADAPTATION_SPEC 1.7-1.10).
seed_rows_ok() {  # [work]: START_HERE.md (as committed; the working copy with "work") has a line holding the new block and
  local t l o    # 36–37 (switch 2's row, seed_row_23_3B.md section 1), and the old block's own row holds 36–37 (section 2:
                 # the cloud's 8b rows 36-37 on that block)
  if [ "${1:-}" = work ]; then t=$(cat "$R/START_HERE.md" 2> /dev/null || true); else t=$(git -C "$R" show HEAD:START_HERE.md 9>&- 2> /dev/null || true); fi
  l=$(grep -F "$(commas "$SEED_NEW")" <<< "$t" || true)
  o=$(grep -E "^\| $(commas "$SEED_OLD") " <<< "$t" || true)
  grep -qE '36(–|-)37' <<< "$l" && grep -qE '36(–|-)37' <<< "$o"
}
env_set_now() {  # the variables a start refuses (at P the engine reads its revert switches from the environment)
  compgen -e | grep -E '^(DECKGYM_.*|PDL_EQUIV_DEALS|GOLDFISH_TRACE)$' | tr '\n' ' ' || true
}
watch_list_busy() {  # group: processes of the long runs $HOME/runs/watch.list names (its PATTERN and CHAIN columns: the
  local g=$1 runs=${KX_RUNS_DIR:-$HOME/runs} nm rd tot pat chain rest x re pid gp cl out=""   # 2-day combined run was a chain
  [ -r "$runs/watch.list" ] || return 0    # script's `strength run`, with no pid file), outside group g; watchers aside
  while IFS='|' read -r nm rd tot pat chain rest; do
    case $nm in ''|'#'*) continue;; esac
    for x in "$pat" "$chain"; do
      [ -n "$x" ] || continue
      re=$(printf '%s' "$x" | sed 's/[][\.*^$+?(){}|]/\\&/g')
      for pid in $(pgrep -f -- "$re" 2> /dev/null || true); do
        [ "$pid" != "$$" ] || continue
        gp=$(ps -o pgid= -p "$pid" 2> /dev/null | tr -d ' ' || true)
        [ -n "$gp" ] && [ "$gp" != "$g" ] || continue
        cl=$(tr '\0' ' ' 2> /dev/null < "/proc/$pid/cmdline" || true)
        case $cl in ''|*run_watch.sh*|*watch_all.sh*) continue;; esac
        out+="$nm's ${cl:0:80}($pid) "
      done
    done
  done < "$runs/watch.list"
  printf '%s' "$out"
}
busy_now() {  # what else runs (empty: nothing): a game program, cargo, rustc or strength outside this run's group; a long
  local out f nm tag runs=${KX_RUNS_DIR:-$HOME/runs}   # run watch.list names; another live launch_detached run (its pid file;
  # not this run's own tag; a run_watch.sh watcher is not counted: it reads status files and pushes only its own branch)
  out=$(ps -eo pid=,pgid=,comm= 2> /dev/null | awk -v g="$PG" '$2 != g && $3 ~ /^(legality_scan|deckgym|goldfish|cargo|rustc|tool_census|strength)$/ {printf "%s(%s) ", $3, $1}' || true)
  out+=$(watch_list_busy "$PG")
  for f in "$runs"/*.pid; do
    [ -e "$f" ] || continue
    nm=$(basename "$f" .pid); tag=$(sed -n 's/^tag=//p' "$f" 2> /dev/null || true)
    [ -z "${LAUNCH_DETACHED_RUN:-}" ] || [ "$tag" != "$LAUNCH_DETACHED_RUN" ] || continue
    case $(sed -n 's/^cmd=//p' "$f" 2> /dev/null || true) in *rl/strength/run_watch.sh*) continue;; esac
    if bash "$R/rl/strength/launch_detached.sh" status "$nm" > /dev/null 2>&1 9>&-; then out+="launch_detached run '$nm' "; fi
  done
  printf '%s' "$out"
}
tools_bad() {  # the 8c tools of tools_8c.tsv that are not the blob named at the commit named (empty: all are)
  local x role path tc tb got out=""
  for x in "${TOOL_ROWS[@]}"; do
    IFS=$'\t' read -r role path tc tb <<< "$x"
    if ! [[ $tc =~ ^[0-9a-f]{40}$ && $tb =~ ^[0-9a-f]{40}$ && -n $path ]]; then out+="$role (the row is not '<role> <path> <commit, 40 hex> <blob, 40 hex>') "; continue; fi
    got=$(git -C "$R" rev-parse -q --verify "$tc:$path" 9>&- 2> /dev/null || true)
    [ "$got" = "$tb" ] || out+="$role ($path at ${tc:0:8} is ${got:-missing}, not ${tb:0:8}) "
  done
  printf '%s' "$out"
}
s1_counters_why() {  # empty when counters.tsv is the one sitting 1's last START line recorded (its sha256's first 16), else why
  local rec cur
  rec=$(grep -E '^SITTING 1 START ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 | grep -oE 'counters\.tsv [0-9a-f]{16}' | head -n 1 || true)
  cur="counters.tsv $(sha256sum < "$O/counters.tsv" | cut -c1-16)"
  [ -n "$rec" ] || { printf '%s' "sitting 1's last START line records no counters.tsv sha256"; return 0; }
  [ "$rec" = "$cur" ] || printf '%s' "counters.tsv is ${cur#counters.tsv } here, but sitting 1's last START line recorded ${rec#counters.tsv } (the reach roles that sorted step 7c's changed games must sort 8b's, 8's and 9's: a change between the sittings goes to the coordinator, as step 7c's hand-off would be sorted again)"
}
reserved_clash() {  # commit: the paths under this folder that it holds and main or the working copy holds with other bytes
  local line meta p b mb wb out=""   # (the pin's merge of main and P would conflict there; ADAPTATION_SPEC 1.10)
  while IFS= read -r -d '' line; do
    meta=${line%%$'\t'*}; p=${line#*$'\t'}; b=${meta##* }
    mb=$(git -C "$R" rev-parse -q --verify "refs/heads/main:$p" 9>&- || true)
    if [ -n "$mb" ] && [ "$mb" != "$b" ]; then out+="$p (main ${mb:0:7}, P ${b:0:7}) "; continue; fi
    if [ -e "$R/$p" ]; then
      wb=$(git -C "$R" hash-object --no-filters -- "$R/$p" 9>&- || echo "?")
      [ "$wb" = "$b" ] || out+="$p (working copy ${wb:0:7}, P ${b:0:7}) "
    fi
  done < <(git -C "$R" ls-tree -r -z "$1" -- "$REL/" 9>&- 2> /dev/null || true)
  printf '%s' "$out"
}

# ---- The game helpers (sitting1.sh's).
run_record() {  # program cwd args...: the text of a .run record (the program's recorded sha256 and the exact command)
  local p=$1 d=$2; shift 2
  printf '%s sha256 %s\ncwd %s\nargs' "${p##*/}" "$(prog_sha "$p")" "$d"; printf ' %q' "$@"; printf '\n'
}
kept() { [ -e "$1" ] && [ -e "$2" ] && [ "$(cat "$2")" = "$3" ]; }
set_aside() {  # label dir why files...: a kept output that is no longer intact is moved aside (.broken_<stamp>, not
  local label=$1 dir=$2 why=$3 st x; shift 3  # committed) and played again: never a halt by itself
  st=$(date -u +%Y%m%dT%H%M%SZ)
  for x in "$@"; do [ ! -e "$dir/$x" ] || mv -- "$dir/$x" "$dir/$x.broken_$st"; done
  note "$label: kept from an earlier start, but $why: its files ($*) moved aside with the suffix .broken_$st (not committed) and played again; the new run's checks decide"
}
timing_row() {  # name games seconds program
  [ -s "$O/timing.tsv" ] || printf 'name\tgames\tseconds\tprogram_sha256\tended\n' > "$O/timing.tsv"
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$(prog_sha "$4" | cut -c1-16)" "$(ts)" >> "$O/timing.tsv"
}
run_scan() {  # name program cwd pairings deals args...: legality_scan; then the complete and RULE checks
  local name=$1 prog=$2 cwd=$3 pl=$4 n=$5; shift 5
  local f="$O/$name" sb=72000000 pf="" bot="" ba="" bb="" prev="" x s out cout="" want rc=0 secs g; local -a chk
  for x in "$@"; do
    case $prev in --pairs) pf=$x;; --seed-base) sb=$x;; --bot) bot=$x;; --bot-a) ba=$x;; --bot-b) bb=$x;; esac
    prev=$x
  done
  ba=${ba:-$bot}; bb=${bb:-$bot}
  chk=(complete --pairings "$pl" --games "$n" --seed-base "$sb" --bot-a "$ba" --bot-b "$bb")
  if [ -n "$pf" ]; then chk+=(--pairs "$pf"); else chk+=(--decks); fi
  want=$(run_record "$prog" "$cwd" "$@" --pairings "$pl" --games "$n")
  if [ -e "$f.jsonl" ]; then  # kept from an earlier start: its record must name this program and command, and it must be intact
    if [ ! -s "$f.run" ]; then set_aside "$name" "$O" "its record $name.run is missing or empty" "$name.jsonl" "$name.txt" "$name.run"
    elif [ "$(cat "$f.run")" != "$want" ]; then
      halt "$name.jsonl is here, but its record $name.run does not name this program and command: move $name.* away first"
    elif ! cout=$(python3 "$CK" "${chk[@]}" "$f.jsonl"); then
      set_aside "$name" "$O" "it is not the complete output of this command ($cout)" "$name.jsonl" "$name.txt" "$name.run"
    elif ! out=$(python3 "$CK" rules "$f.txt") && ! grep -q 'RULE findings' <<< "$out"; then
      set_aside "$name" "$O" "its page is incomplete ($out)" "$name.jsonl" "$name.txt" "$name.run"
    fi
  fi
  if [ -e "$f.jsonl" ]; then
    REUSED=$((REUSED + $(grep -c . "$f.jsonl")))
    note "$name: kept from an earlier start ($cout)"
  else
    rm -f -- "$f.jsonl.part" "$f.run"
    s=$(date +%s)
    ( cd "$cwd" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$prog" "$@" --pairings "$pl" --games "$n" \
        --games-out "$f.jsonl.part" ) > "$f.txt" 2>&1 || rc=$?
    [ $rc -eq 0 ] || stopped_or_failed $rc "legality_scan for $name (see $name.txt)"
    out=$(python3 "$CK" "${chk[@]}" "$f.jsonl.part") \
      || halt "$name: the scan's output is not the complete set of deals, each the game this command plays ($out)"
    printf '%s\n' "$want" > "$f.run"
    durable "$f.jsonl.part" "$f.txt" "$f.run"   # on disk before the rename that makes it a kept file
    mv -- "$f.jsonl.part" "$f.jsonl"
    secs=$(( $(date +%s) - s )); g=$(grep -c . "$f.jsonl")
    timing_row "$name" "$g" "$secs" "$prog"; PLAYED=$((PLAYED + g))
    note "$name played in $secs s ($out)"
  fi
  STEP_FILES+=("$name.jsonl" "$name.txt" "$name.run")   # before the checks below, so a halt's record carries them
  rc=0; out=$(python3 "$CK" rules "$f.txt") || rc=$?
  if [ $rc -ne 0 ]; then
    if [ "$prog" = "$OLD_SCAN" ] && grep -q 'RULE findings' <<< "$out"; then   # the old engine has the bugs the switch repairs
      note "EVIDENCE, not a stop: the official OLD legality_scan's page for $name lists RULE findings ($out): the old engine ($OLD_NAME, $OLD_DIR/) has the bugs the switch repairs; the new and watch pages of the same deals must have none"
      pin_note "$name (the official old legality_scan, $OLD_DIR/): RULE findings noted as evidence of the old engine: $(reword "$out")"
    else halt "RULE FINDING or an incomplete page: $out"; fi
  fi
}
ident() {  # outfile label name expect max_i filter ref...: one line per reference; any difference halts (filter: "" or one
  local idf=$1 label=$2 name=$3 expect=$4 maxi=$5 flt=$6 r line rc=0; shift 6   # token --pairings=P or --exclude-pairings=P)
  local -a args=(same "$O/$name.jsonl" --expect "$expect" --label "$label")
  [ -z "$maxi" ] || args+=(--max-i "$maxi")
  [ -z "$flt" ] || args+=("$flt")
  for r in "$@"; do args+=(--ref "$r"); done
  line=$(python3 "$CK" "${args[@]}") || rc=$?
  echo "$line" >> "$idf"
  case $rc in
    0) note "identity: $(tr '\n' ' ' <<< "$line" | cut -c1-400)";;
    1) halt "IDENTITY: $label differs from its reference (${idf##*/}): $(grep -o 'DIFFERS: .*' <<< "$line" | head -n 2 | tr '\n' ' ')";;
    *) halt "the identity check for $label could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$line")";;
  esac
}
touched_check() {  # step set bot expect outfile label new watch filter old...: sitting2_check.py touched (old v new v watch)
  local st=$1 hn=$2 bot=$3 n=$4 tf=$5 label=$6 new=$7 watch=$8 flt=$9 out rc=0 hf; shift 9   # into handoff_<set>.tsv
  hf="handoff_$hn.tsv"; STEP_FILES+=("$hf")
  local -a args=(touched --old "$@" --new "$new" --watch "$watch" --expect "$n" --step "$st" --bot "$bot" --repo "$R"
                 --counters "$CNT" --out-handoff "$O/$hf" --label "$label")
  [ -z "$flt" ] || args+=("$flt")
  out=$(python3 "$CK3" "${args[@]}") || rc=$?
  echo "$out" >> "$tf"
  case $rc in
    0) note "touched: $(tail -n 1 <<< "$out" | cut -c1-400)";;
    1) halt "TOUCHED: $label (${tf##*/}): $(grep -F 'does not pass' <<< "$out" | tail -n 1 | cut -c1-700)";;
    *) halt "the touched check for $label could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$out")";;
  esac
}
scan_set() {  # set bot pairs seedbase pairings deals oldmode: the set's scans (old when oldmode is play; new; watch), then
  local fam=$1 bot=$2 pf=$3 sb=$4 pl=$5 n=$6 om=$7 st exp tf ow; local -a SA OLDF=()   # (a) watch v new and (b) touched.
  st=${fam%%_*}; tf="$O/touched_$st.txt"   # set: 8b_cloud, 8b_new2, 8 (the carriers), 8_will; oldmode: play, or
  exp=$(( $(tr ',' '\n' <<< "$pl" | grep -c .) * n ))   # reuse:<file>[,<file>] (the old side's files, as they are)
  SA=(--pairs "$pf" --root "$R" --seed-base "$sb")
  case $om in
    play) run_scan "${S}_${fam}_old_$bot" "$OLD_SCAN" "$B/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
          OLDF=("$O/${S}_${fam}_old_$bot.jsonl"); ow="the official legality_scan, $OLD_DIR/";;
    reuse:?*) IFS=',' read -r -a OLDF <<< "${om#reuse:}"; ow="reused: $(printf '%s ' "${OLDF[@]##*/}")";;
    *) die "scan_set: oldmode $om is neither play nor reuse:<files>";;
  esac
  run_scan "${S}_${fam}_new_$bot" "$SCAN" "$B/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
  run_scan "${S}_${fam}_watch_$bot" "$WSCAN" "$W/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
  ident "$tf" "$st watch v new, $bot, $fam, pairings $pl, i < $n (seeds $(commas "$sb") + 10,000 x pairing + i)" \
    "${S}_${fam}_watch_$bot" "$exp" "" "" "$O/${S}_${fam}_new_$bot.jsonl"
  touched_check "$st" "${fam}_$bot" "$bot" "$exp" "$tf" "$st $bot, $fam, old v new v watch (old: ${ow% })" \
    "$O/${S}_${fam}_new_$bot.jsonl" "$O/${S}_${fam}_watch_$bot.jsonl" "" "${OLDF[@]}"
}
SUM=""
step_summary() {  # step: sitting2_check.py stepsum over both bots into touched_<step>.txt; SUM, its summary line
  local st=$1 out rc=0 x b; local -a wf=() rf=() fl=()
  case $st in
    8b) for x in 8b_cloud 8b_new2; do for b in km3 k3; do wf+=("$O/${S}_${x}_watch_$b.jsonl"); rf+=("$O/handoff_${x}_$b.tsv"); done; done;;
    8) for x in 8 8_will; do for b in km3 k3; do wf+=("$O/${S}_${x}_watch_$b.jsonl"); rf+=("$O/handoff_${x}_$b.tsv"); done; done;;
    9) wf=("$O/${S}_9_watch_b2e_km3.jsonl"); rf=("$O/handoff_9_km3.tsv"); fl=(--pairings "$NAMED9");;
  esac
  out=$(python3 "$CK3" stepsum --step "$st" --counters "$CNT" --watch "${wf[@]}" --rows "${rf[@]}" "${fl[@]}") || rc=$?
  echo "$out" >> "$O/touched_$st.txt"
  [ $rc -eq 0 ] || halt "the step summary of $st could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$out")"
  SUM=$(grep '^SUMMARY: ' <<< "$out" | tail -n 1 | sed 's/^SUMMARY: //' || true)
  note "step $st's summary: $SUM"
}
CLOUD_SUM=""
cloud_rows_8b() {  # this run's 8b rows v the cloud's own at P (PLAN step 8b, precondition d): new 32-37 v its 8b_new_<bot>,
  local bot kind mine f pl n rc out; CLOUD_SUM=""   # old 36-37 v its 8b_pinned_<bot>; a difference, or no comparison, halts
  for bot in km3 k3; do
    for kind in new old; do
      case $kind in
        new) mine="$O/${S}_8b_cloud_new_$bot.jsonl"; f=8b_new_$bot.jsonl; pl=32-37; n=240;;
        old) mine="$O/${S}_8b_cloud_old_$bot.jsonl"; f=8b_pinned_$bot.jsonl; pl=36-37; n=80;;
      esac
      git -C "$R" show "$P:$CLOUD8B_DIR/$f" > "$PRIV/cloud_$f" 9>&- 2> /dev/null \
        || halt "P ${P:0:7} has no $CLOUD8B_DIR/$f: this run's 8b rows cannot be compared with the cloud's (PLAN step 8b)"
      rc=0; out=$(python3 "$CK3" cloud8b --new "$mine" --cloud "$PRIV/cloud_$f" --bot "$bot" --pairings "$pl" --expect "$n" \
                  --label "8b $kind $bot (pairings $pl, i < 40) v the cloud's $f at P ${P:0:7}") || rc=$?
      echo "$out" >> "$O/touched_8b.txt"
      case $rc in
        0) CLOUD_SUM+="$kind $bot $(grep -oE '[0-9]+ of [0-9]+ deals equal' <<< "$out" | head -n 1 || true); ";;
        1) halt "CLOUD 8B: this run's 8b $kind $bot rows differ from the cloud's $f at P (PLAN step 8b: they must be equal; it goes to the coordinator): $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1 | cut -c1-400)";;
        *) halt "this run's 8b $kind $bot rows could not be compared with the cloud's $f at P (PLAN step 8b requires them equal): $(tail -n 1 <<< "$out" | cut -c1-400)";;
      esac
    done
  done
  CLOUD_SUM=${CLOUD_SUM%; }
}

# ---- Steps: done, skipped, estimated, finished.
step_is_done() { grep -q "^STEP $1 DONE $S " "$O/STATUS.txt" 2> /dev/null; }
step_done() { if ! step_is_done "$1"; then echo "STEP $1 DONE $S $(ts) $2" >> "$O/STATUS.txt"; fi; note "step $1 passed: $2"; }
manifest_files() { sed -E 's/^[0-9a-f]{64}  //' "$O/step_$1.sha256" | while IFS= read -r f; do echo "$REL/$f"; done; echo "$REL/step_$1.sha256"; }
skip_done() {  # n: a DONE step's committed evidence is unchanged; its files join every later checkpoint (checked again there)
  local out
  [ -s "$O/step_$1.sha256" ] || halt "step $1 is DONE but step_$1.sha256 is missing"
  out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$1.sha256" 2>&1) \
    || halt "the evidence of step $1 changed since its checkpoint: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  DONE_STEPS+=("$1")
  note "step $1: DONE at an earlier start; its $(grep -c . "$O/step_$1.sha256") files are as step_$1.sha256 records them"
}
finish_step() {  # n summary: the checks, the manifest, the anchored line, the checkpoint
  check_pins "after step $1"; old_programs; step_io "$1" "after step $1" halt
  (cd "$O" && sha256sum -- "${STEP_FILES[@]}") > "$O/step_$1.sha256.part" || die "sha256 of step $1's files"
  durable "$O/step_$1.sha256.part"; mv -- "$O/step_$1.sha256.part" "$O/step_$1.sha256"; durable "$O"
  pin_note "step $1: $2"
  step_done "$1" "$2"
  DONE_STEPS+=("$1")
  checkpoint "step $1 passed" "$2"
}
rate() {  # games a second: measured over every game timed so far (timing.tsv, sitting 1's included), or RATE before 2,000
  if [ -s "$O/timing.tsv" ]; then
    awk -F'\t' -v d="$RATE" 'NR > 1 && $3 > 0 {g += $2; s += $3} END {if (g >= 2000 && s > 0) printf "%.2f", g / s; else print d}' "$O/timing.tsv"
  else echo "$RATE"; fi
}
games_left() {  # step: the games it still has to play (a complete kept file counts as played)
  local x y nm pf sb pl n g=0
  case $1 in
    8b) for x in "${SCANS8B[@]}"; do
          case $x in 8b_cloud_old_*) y=80;; 8b_cloud_*) y=240;; *) y=280;; esac
          [ -e "$O/${S}_$x.jsonl" ] || g=$((g + y))
        done;;
    8) for x in "${SCANS8[@]}"; do
         case $x in 8_will_*_km3) y=1500;; 8_will_*) y=750;; *_km3) y=16000;; *) y=8000;; esac
         [ -e "$O/${S}_$x.jsonl" ] || g=$((g + y))
       done;;
    9) for x in "${SPEC9[@]}"; do IFS='|' read -r nm pf sb pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + n)); done
       [ -e "$O/${S}_9_watch_b2e_km3.jsonl" ] || g=$((g + 8000));;
    10) for x in "${CLI_CODES[@]}"; do [ -e "$O/${S}_10_cli_$x.run" ] || g=$((g + 240)); done
        [ -e "$O/${S}_10_run_screen.run" ] || g=$((g + 3840));;
  esac
  echo "$g"
}
need_s() {  # step: the seconds it needs (games / rate x safety; 5 min for 8-seeds; plus the overhead)
  local base g
  case $1 in
    8-seeds) base=300;;
    *) g=$(games_left "$1"); base=$(awk -v g="$g" -v r="$(rate)" -v k="$SAFETY" 'BEGIN {printf "%d", g / r * k + 0.5}');;
  esac
  echo $((base + OVERHEAD_MIN * 60))
}
fits_now() {  # step: it would end before the deadline (games / rate x safety + the overhead), or there is no deadline
  local need; need=$(need_s "$1")
  [ "$DL" -eq 0 ] || [ $(( $(date +%s) + need )) -le "$DL" ]
}
done_list() { grep -oE "^STEP (8-seeds|8b|8|9|10) DONE $S " "$O/STATUS.txt" 2> /dev/null | cut -d' ' -f2 | tr '\n' ' ' || true; }
begin_step() {  # n what: the deadline check (a step that would end after it is not started), then the checks
  local need now how sdone
  STEP=$1; STEP_FILES=()
  case $1 in  # a record of a halt or a stop also commits these (best effort), as they are
    8-seeds) HALT_FILES=("$CLOUD_PAIRS" pairs_8b2.tsv pairs_will.tsv seeds_8_2.txt);; 8b) HALT_FILES=(touched_8b.txt);;
    8) HALT_FILES=(touched_8.txt);; 9) HALT_FILES=(identity_9.txt touched_9.txt);; 10) HALT_FILES=(identity_10.txt);;
  esac
  need=$(need_s "$1"); now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ $((now + need)) -gt "$DL" ]; then
    case $1 in 8-seeds) how="a fetch and the extractions";; *) how="$(games_left "$1") games at $(rate) games a second x $SAFETY";; esac
    sdone=$(done_list)
    state_line "SITTING 2 PAUSED $(ts) ${S:-?}: before step $1: it needs about $((need / 60)) min ($how, plus $OVERHEAD_MIN), so it would end after the deadline $(fmt "$DL"); not started. Steps done: ${sdone:-none }(committed). A plain start after the deadline (Monday evening on a school morning) resumes at step $1"
    FINISHED=1; RECORD=1; exit 3
  fi
  check_pins "before step $1"; old_programs; step_io "$1" "before step $1" halt
  note "step $1: $2 (about $((need / 60)) min with the overhead; deadline $(fmt "$DL"))"
}

# ---- Step 8c's gate and step 10's parts.
run_step8() {  # step 8, once 8c's gate has passed (after 8b, or again after step 10): the carriers and the Will rows
  begin_step 8 "the carriers (Oct 1's pairings 0-31, new and watch; the old side Oct 1's reused games) and the Will rows (60-62; old, new and watch), km3 i < 500 then k3 i < 250: $(games_left 8) of 54,750 games still to play"
  : > "$O/touched_8.txt"
  scan_set 8 km3 "$R/$OLDREL/pairs_8.tsv" "$SEED_OLD" "$P8" 500 "reuse:$R/${REUSE8[km3]}"
  scan_set 8 k3 "$R/$OLDREL/pairs_8.tsv" "$SEED_OLD" "$P8" 250 "reuse:$R/${REUSE8[k3]}"
  scan_set 8_will km3 "$O/pairs_will.tsv" "$SEED_NEW" "$PWILL" 500 play
  scan_set 8_will k3 "$O/pairs_will.tsv" "$SEED_NEW" "$PWILL" 250 play
  step_summary 8
  STEP_FILES+=(touched_8.txt)
  finish_step 8 "the carriers (pairings 0-31; km3 16,000 and k3 8,000 new and watch, the old side Oct 1's reused games) and the Will rows (60-62; km3 1,500 and k3 750 per build): watch equal to new on every field; every deal the same deal on the three sides; the real trace load before 8c: $SUM (touched_8.txt; every changed game in handoff_8c.tsv for 8c)"
}
CLOUD_LINE=""
cloud8b_same() {  # kind bot file label: sitting2_check.py cloud8b, this run's 8b rows v the cloud's (kind new: its NEW-build
  local kind=$1 bot=$2 file=$3 label=$4 rc=0 mine pl n  # rows v <S>_8b_cloud_new_<bot>, pairings 32-37, 240 deals; kind
  case $kind in  # old: its pinned rows, filtered to 36-37, v <S>_8b_cloud_old_<bot>, 80 deals). A matched deal that differs
    new) mine="$O/${S}_8b_cloud_new_$bot.jsonl"; pl=32-37; n=240;;   # halts; returns 3 when not compared (owed). Never call
    *) mine="$O/${S}_8b_cloud_old_$bot.jsonl"; pl=36-37; n=80;;     # it in $(...)
  esac
  CLOUD_LINE=$(python3 "$CK3" cloud8b --new "$mine" --cloud "$file" --bot "$bot" --pairings "$pl" --expect "$n" \
         --label "8b $kind $bot (pairings $pl, i < 40) v the cloud's rows, $label") || rc=$?
  echo "$CLOUD_LINE" >> "$O/gate_8c.txt"
  case $rc in
    0) return 0;;
    1) halt "CLOUD 8B: this run's 8b $kind $bot differs from the cloud's rows ($label; gate_8c.txt): $(grep -o 'DIFFERS: .*' <<< "$CLOUD_LINE" | head -n 1 | cut -c1-400)";;
    *) return 3;;
  esac
}
gate_8c() {  # GATE_WHY: empty when step 8 may run; else why it waits. The reading goes to gate_8c.txt, STATUS.txt and
  local f="$O/trace_load.txt" out="" rd="" rc=0 cid="" cmsg="" cl tag cc cb cp rest l8b n="" line kind  # PIN_STATUS.txt (reworded)
  echo "== 8c's gate, read at $(ts) (sitting2.sh)" >> "$O/gate_8c.txt"
  if [ ! -e "$f" ]; then GATE_WHY="trace_load.txt is not here"
  elif ! git -C "$R" ls-files --error-unmatch -- "$REL/trace_load.txt" > /dev/null 2>&1 9>&- \
       || ! git -C "$R" diff --quiet HEAD -- "$REL/trace_load.txt" 9>&-; then
    GATE_WHY="trace_load.txt is here but not committed as it is (commit it first: the gate reads committed words only)"
  else
    # the cloud's load covers its rows 32-37 only (its early_warning_8b/README.md, "Scope"): the laptop's own 8b rows 40-46
    # with no reach2 counter are added to it (their hand-off rows, written by step 8b)
    out=$(python3 "$CK3" trace-gate "$f" --extra-rows "$O/handoff_8b_new2_km3.tsv" "$O/handoff_8b_new2_k3.tsv") || rc=$?
    rd=$(head -n 1 <<< "$out")                                       # the reading; then the marked lines LOAD and COMMIT
    n=$(sed -n 's/^LOAD \([0-9][0-9]*\)$/\1/p' <<< "$out" | head -n 1)
    cid=$(sed -n 's/^COMMIT \([0-9a-f]*\)$/\1/p' <<< "$out" | head -n 1)
    case $rc in 0) GATE_WHY="";; 3) GATE_WHY=${rd#trace load: step 8 waits: };; *) GATE_WHY="the trace-gate check failed (exit $rc): $rd";; esac
    if [ -z "$GATE_WHY" ] && { [ -z "$cid" ] || ! git -C "$R" cat-file -e "$cid^{commit}" 9>&- 2> /dev/null; }; then
      GATE_WHY="the cloud commit ${cid:-(none marked)} that trace_load.txt names is not here (git cat-file -e; in GitHub Desktop, Fetch origin)"
    fi
    # The optional cross-checks of 8b (8b itself already compared this run's rows with P's early_warning_8b/ files):
    # CLOUD8B <commit> <bot> <path> (NEW-build rows, pairings 32-37) and CLOUD8B_OLD <commit> <bot> <path> (pinned, 36-37).
    cl=$(sed '1s/^\xEF\xBB\xBF//' "$f" | tr -d '\r' | grep -E '^CLOUD8B(_OLD)?( |$)' || true)
    if [ -z "$cl" ]; then cmsg="8b v the cloud's rows in trace_load.txt: no CLOUD8B line (8b compared them with P's early_warning_8b/ files)"
    else
      while IFS=' ' read -r tag cc cb cp rest; do
        kind=new; [ "$tag" != CLOUD8B_OLD ] || kind=old
        if ! [[ $cc =~ ^[0-9a-f]{7,40}$ && $cb =~ ^(km3|k3)$ && -n $cp && -z $rest ]]; then
          cmsg+="a $tag line is not '$tag <commit> <km3|k3> <path>': not compared (owed); "
        elif ! git -C "$R" cat-file -e "$cc^{commit}" 9>&- 2> /dev/null; then
          cmsg+="8b $kind $cb v the cloud's rows: commit $cc is not here (Fetch origin): not compared (owed); "
        elif ! git -C "$R" show "$cc:$cp" > "$PRIV/cloud8b_${kind}_$cb.jsonl" 2> /dev/null 9>&-; then
          cmsg+="8b $kind $cb v the cloud's rows: $cp is not in $cc: not compared (owed); "
        elif cloud8b_same "$kind" "$cb" "$PRIV/cloud8b_${kind}_$cb.jsonl" "$cc:$cp"; then
          cmsg+="8b $kind $cb v the cloud's rows ($cc:$cp): $(grep -oE '[0-9]+ of [0-9]+ deals equal on the [0-9]+ fields both record' <<< "$CLOUD_LINE" || true); "
        else cmsg+="8b $kind $cb v the cloud's rows ($cc:$cp): $(grep -o 'not compared (owed): .*' <<< "$CLOUD_LINE" | head -n 1 | cut -c1-250 || true); "; fi
      done <<< "$cl"
      cmsg=${cmsg%; }
    fi
  fi
  l8b=$(grep '^SUMMARY: ' "$O/touched_8b.txt" 2> /dev/null | tail -n 1 | grep -oE 'changed [0-9]+ of [0-9]+ deals \([0-9]+ with no reach2 counter\)' || true)
  line="the laptop's own 8b: ${l8b:-no count (touched_8b.txt has no summary)}; the cloud's declared trace load: ${n:-none read} (rows 32-37; the gate adds the laptop's rows 40-46 with no reach2 counter, as its reading says)"
  [ -n "$cmsg" ] || cmsg="8b v the cloud's rows in trace_load.txt: not read (8b compared them with P's early_warning_8b/ files)"   # (no apostrophe inside ${:-})
  { echo "reading: ${rd:-none}"; echo "verdict: ${GATE_WHY:-step 8 may run}"; echo "$cmsg"; echo "$line"; } >> "$O/gate_8c.txt"
  if [ -z "$GATE_WHY" ]; then
    note "$(reword "8c's gate: $rd; commit $cid (git cat-file -e); trace_load.txt sha256 $(sha256sum < "$f" | cut -c1-16) (committed); $cmsg; $line: step 8 may run")"
    pin_note "$(reword "8c's gate before step 8: $rd; $cmsg; $line")"
  else
    note "$(reword "8c's gate: step 8 waits for 8c's trace load: $GATE_WHY; $cmsg; $line")"
    pin_note "$(reword "8c's gate before step 8: it waits ($GATE_WHY); $cmsg; $line")"
  fi
}
cli_compare() {  # code out ref: every line but line 6 equal, the cli line equal, k3/kp3/kog3 at PLAN's numbers; prints the line
  local code=$1 f=$2 ref=$3 d line refline exp got
  d=$(diff <(sed '6d' "$ref") <(sed '6d' "$f") 2>&1) || { echo "cli $code: ${f##*/} differs from ${ref##*/} beyond line 6 (the wall time): $(head -n 6 <<< "$d" | tr '\n' ' ')"; return 1; }
  { sed -n '6p' "$f" | grep -q '^Ran 240 simulations in ' && sed -n '6p' "$ref" | grep -q '^Ran 240 simulations in '; } \
    || { echo "cli $code: line 6 is not the 'Ran 240 simulations in ...' line in both files"; return 1; }
  line=$(python3 "$CK" cli "$f" --code "$code" --num 240 2> /dev/null) || { echo "cli $code: deckgym simulate did not run clean ($(python3 "$CK" cli "$f" --code "$code" --num 240 2>&1 | tail -n 1))"; return 1; }
  refline=$(python3 "$CK" cli "$ref" --code "$code" --num 240 2> /dev/null) || { echo "cli $code: the reference ${ref##*/} does not read as a clean output"; return 1; }
  [ "$line" = "$refline" ] || { echo "cli $code: '$line' is not the reference's '$refline'"; return 1; }
  case $code in k3) exp="150 90 0";; kp3) exp="144 96 0";; kog3) exp="149 91 0";; *) exp="";; esac
  if [ -n "$exp" ]; then
    got=$(sed -nE 's/.*Player 0 won: ([0-9]+) .*Player 1 won: ([0-9]+) .*Draws: ([0-9]+) .*/\1 \2 \3/p' <<< "$line")
    [ "$got" = "$exp" ] || { echo "cli $code: ${got:-?}, not $exp (PLAN.md step 10)"; return 1; }
  fi
  echo "10 cli $code,$code (deckgym simulate --num 240 --seed 7100 --seed-stream, altaria v blaziken, from the repository, no RAYON_NUM_THREADS) v ${ref#"$B/ref2/"}: equal on every line but line 6 (the wall time); $line$([ -z "$exp" ] || echo "($exp, as PLAN.md step 10 says)")"
}
out_run() {  # label base want compare-function args... (the run itself is the function PLAY_FN): a kept output is reused
  local label=$1 base=$2 want=$3 msg rc was_kept; shift 3  # once; if its comparison fails it is set aside and played again
  while :; do
    if kept "$O/$base.txt" "$O/$base.run" "$want" && { [ "$base" != "${S}_10_goldfish" ] || [ -e "$O/${S}_10_goldfish_coverage.json" ]; }; then
      was_kept=1; note "$label: kept from an earlier start"
    else was_kept=0; "$PLAY_FN"; fi
    rc=0; msg=$("$@") || rc=$?
    if [ $rc -ne 0 ] && [ $was_kept -eq 1 ]; then
      set_aside "$label" "$O" "its comparison did not pass ($(cut -c1-200 <<< "$msg"))" "$base.txt" "$base.run" $([ "$base" != "${S}_10_goldfish" ] || echo "${S}_10_goldfish_coverage.json")
      continue
    fi
    break
  done
  [ $was_kept -eq 0 ] || REUSED=$((REUSED + OUT_GAMES))
  [ $rc -eq 0 ] || halt "$msg"
  echo "$msg" >> "$O/identity_10.txt"; note "identity: $(cut -c1-400 <<< "$msg")"
}
play_cli() {
  local f="$O/${S}_10_cli_$CODE" rc=0 s secs
  rm -f -- "$f.txt" "$f.run" "$f.txt.part"
  s=$(date +%s)
  ( cd "$R" && unset RAYON_NUM_THREADS && nice -n "$NICE" "$GYM" simulate --num 240 --players "$CODE,$CODE" --seed 7100 --seed-stream \
      -p "$CLI_P0" "$CLI_P1" ) > "$f.txt.part" 2>&1 || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "deckgym simulate $CODE (see ${f##*/}.txt.part)"
  durable "$f.txt.part"; mv -- "$f.txt.part" "$f.txt"; printf '%s\n' "$WANT" > "$f.run"; durable "$f.run"
  secs=$(( $(date +%s) - s )); timing_row "${S}_10_cli_$CODE" 240 "$secs" "$GYM"; PLAYED=$((PLAYED + 240))
}
play_goldfish() {
  local G="$O/${S}_10_goldfish" GC="$O/${S}_10_goldfish_coverage" rc=0
  rm -f -- "$G.txt" "$G.run" "$GC.json" "$G.txt.part" "$GC.json.part"
  ( cd "$B/engine" && unset RAYON_NUM_THREADS && nice -n "$NICE" "$GOLD" --deck "$R/$CLI_P0" --panel "$R/decks/screen/opponents" \
      --games 0 --coverage "$GC.json.part" ) > "$G.txt.part" 2>&1 || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "goldfish --coverage (see ${G##*/}.txt.part)"
  [ -s "$GC.json.part" ] || halt "goldfish wrote no coverage file (${G##*/}.txt.part)"
  durable "$GC.json.part" "$G.txt.part"; mv -- "$GC.json.part" "$GC.json"; mv -- "$G.txt.part" "$G.txt"
  printf '%s\n' "$WANT" > "$G.run"; durable "$G.run"
}
gold_compare() {
  local G="$O/${S}_10_goldfish" GC="$O/${S}_10_goldfish_coverage" rt="$B/ref2/$E30/14c39f4_goldfish.txt" rj="$B/ref2/$E30/14c39f4_goldfish_coverage.json"
  cmp -s -- "$G.txt" "$rt" || { echo "goldfish's page differs from 14c39f4_goldfish.txt: $(diff -- "$rt" "$G.txt" | head -n 6 | tr '\n' ' ')"; return 1; }
  cmp -s -- "$GC.json" "$rj" || { echo "goldfish --coverage differs from 14c39f4_goldfish_coverage.json: $(diff -- "$rj" "$GC.json" | head -n 6 | tr '\n' ' ')"; return 1; }
  echo "10 goldfish --deck $R/$CLI_P0 --panel decks/screen/opponents --games 0 --coverage (from B/engine): the page and the coverage file equal 14c39f4_goldfish.txt and 14c39f4_goldfish_coverage.json byte for byte"
}
play_screen() {
  local SC="$O/${S}_10_run_screen" rc=0 s secs
  rm -f -- "$SC.txt" "$SC.run" "$SC.txt.part"
  s=$(date +%s)
  ( cd "$R" && unset RAYON_NUM_THREADS && nice -n "$NICE" python3 "$SW" "$GYM" "$PIN_GYM" "$R/decks/screen/run_screen.py" "${SARGS[@]}" ) \
    > "$SC.txt.part" 2>&1 || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "run_screen.py on the new deckgym (see ${SC##*/}.txt.part)"
  durable "$SC.txt.part"; mv -- "$SC.txt.part" "$SC.txt"; printf '%s\n' "$WANT" > "$SC.run"; durable "$SC.run"
  secs=$(( $(date +%s) - s )); timing_row "${S}_10_run_screen" 3840 "$secs" "$GYM"; PLAYED=$((PLAYED + 3840))
}
screen_compare() {
  local out rc=0
  out=$(python3 "$CK" screen "$O/${S}_10_run_screen.txt" "$B/ref2/$SCREEN_REF") || rc=$?
  if [ $rc -ne 0 ]; then
    echo "run_screen under km3 on brew-06 and 06b on the new deckgym differs from floor_recheck_2026-09-30/run_screen.txt: $out. One possible cause besides the engine: that reference was made with run_screen.py 4f102352, and this run used the current one, $(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-8) (its docstring says the output is unchanged without --weights)"
    return 1
  fi
  echo "10 $out (km3 on the deck and the panel, 240 games a matchup, seed 7,100; run_screen.py $(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-16), through screen_with.py on the new deckgym)"
}

# ---- The start's git checks (also reported by the dry run).
git_locks() {  # the git lock files a power-off in a checkpoint can leave behind: prints those that are here
  local lk p
  for lk in index.lock refs/heads/main.lock; do
    p=$(git -C "$R" rev-parse --git-path "$lk" 9>&-); case $p in /*) ;; *) p="$R/$p";; esac
    [ ! -e "$p" ] || echo "$p"
  done
}
FOREIGN=""; ALLOWED_NEW=()
unpushed_check() {  # origin main: FOREIGN, the unpushed commits that are not this switch's (short ids); ALLOWED_NEW, the
  local c files; FOREIGN=""; ALLOWED_NEW=()  # unpushed non-merge ones not yet in .sitting2.ours that touch only this folder and START_HERE.md
  for c in $(git -C "$R" rev-list "$1..$2" 9>&-); do
    if grep -qxF "$c" "$CKPT_OURS" 2> /dev/null; then continue; fi
    files=$(git -C "$R" diff-tree --no-commit-id -r --name-only "$c" 9>&-) || files="?"
    if ! git -C "$R" rev-parse -q --verify "$c^2" > /dev/null 9>&- && ! grep -qvE "^($REL/|START_HERE\\.md\$)" <<< "$files"; then
      ALLOWED_NEW+=("$c")   # the runner's own commit (sitting2.sh, its helpers, the data files, the seed row), or a checkpoint a power-off left unrecorded
    else FOREIGN+="${c:0:7} "; fi
  done
}
committed() {  # repository path: committed and unchanged in the working copy
  git -C "$R" ls-files --error-unmatch -- "$1" > /dev/null 2>&1 9>&- && git -C "$R" diff --quiet HEAD -- "$1" 9>&-
}
s1_lock_held() {  # a live sitting1.sh (or its orphaned child) holds .sitting1.lock
  local held=1
  [ -e "$O/.sitting1.lock" ] || return 1
  exec 8< "$O/.sitting1.lock"
  if flock -n 8; then flock -u 8; held=1; else held=0; fi
  exec 8<&-
  return $held
}

# ---- The dry run: git and file checks only.
dry_run() {
  local m o x p sha got n want tmp out t rc=0 nst lst role path nm pf sb pl ref notes=0; local -a stg=() lp=()
  STEP=dry; S=dry
  m=$(git -C "$R" rev-parse refs/heads/main); o=$(git -C "$R" rev-parse refs/remotes/origin/main)
  echo "dry run: main ${m:0:7}, origin/main ${o:0:7}, ${P_BRANCH:-P_BRANCH} $(git -C "$R" rev-parse --short "${P_BRANCH:-none}" 2> /dev/null || echo '(none)') (as last fetched; no fetch now)"
  [ -z "$DATA_WHY" ] || halt "the data files cannot be read as they must be (a start refuses; ADAPTATION_SPEC Appendix A): $DATA_WHY"
  if [ ${#MARKS[@]} -eq 0 ]; then echo "dry run: no data file or key sitting 2 needs is marked TO FINALIZE"
  else for x in "${MARKS[@]}"; do echo "dry run: NOTE $x (PLAN: P is not final yet; a start refuses until it is filled in and committed)"; notes=$((notes + 1)); done; fi
  echo "dry run: the data files, sha256: $(data_sums)"
  if [ "$P" = TO_FINALIZE ] || [ "$P_TREE" = TO_FINALIZE ]; then
    PX=$(git -C "$R" rev-parse -q --verify "$P_BRANCH^{commit}") || halt "P is TO FINALIZE and $P_BRANCH is not here (Fetch origin)"
    PXT=$(git -C "$R" rev-parse "$PX:engine")
    echo "dry run: NOTE P is TO FINALIZE: the checks below take P = $P_BRANCH's tip ${PX:0:7} (engine/ ${PXT:0:7}), as last fetched"
  else
    git -C "$R" cat-file -e "$P^{commit}" 2> /dev/null || halt "P ${P:0:7} is not here (Fetch origin)"
    [ "$(git -C "$R" rev-parse "$P:engine")" = "$P_TREE" ] || halt "P's engine/ is not P_TREE ${P_TREE:0:7} (switch2.env)"
    echo "dry run: P ${P:0:7} is here, its engine/ is P_TREE ${P_TREE:0:7}$(git -C "$R" merge-base --is-ancestor "$P" "$P_BRANCH" 2> /dev/null && echo ", on $P_BRANCH" || echo "; NOTE it is not on $P_BRANCH as last fetched")"
  fi
  s1_state
  if [ -z "$S1_WHY" ]; then
    CB=$C; s1_checks; set_paths
    echo "dry run: candidate.txt names $C (main ${MAIN_C:0:7} + P ${PX:0:7}); sitting 1's last state is SITTING 1 DONE $C; STEP 4/5/6/7/7b/7c-seeds/7c DONE for $S; step_4 ... step_7c.sha256 verify"
    check_pins "the dry run"; old_programs
    echo "dry run: the programs are sitting 1's: $B and $W (COMMIT $S), programs.sha256 and watch.sha256 verify; $OLD_DIR/ has switch2.env's sha256, equals its SHA256SUMS and is the manifest's available release ($OLD_NAME)"
    s1_records
    echo "dry run: $S1REC (checked once at a start, a note either way)"
    for x in 8b 9 10; do
      if step_is_done "$x"; then step_io "$x" "the dry run" note; echo "dry run: step $x is DONE: its inputs and references checked as a note (any drift is a NOTE line above)"; fi
    done
  else
    C=""; MAIN_C=""; CB=refs/heads/main; S=dry; B="<sitting 1's build folder>"; W="<sitting 1's watch build folder>"
    echo "dry run: NOTE sitting 1 is not DONE ($S1_WHY): a start refuses. Without its candidate the checks below take the decks and references from main ${m:0:7} and the cloud's files from P ${PX:0:7}; the programs are not checked"
    notes=$((notes + 1))
    old_programs
    echo "dry run: $OLD_DIR/ has switch2.env's sha256, equals its SHA256SUMS and is the manifest's available release ($OLD_NAME)"
  fi
  DRYTMP=$(mktemp -d /tmp/sitting2_rules2_dry.XXXXXX); tmp=$DRYTMP   # removed on exit, a halt included
  reuse_checks
  echo "dry run: $REUSE_NOTE"
  cloud_checks "$tmp"
  echo "dry run: $CLOUD_NOTE"
  for x in "$CLOUD_PAIRS" "$WATER_DST" pairs_8b2.tsv pairs_will.tsv seeds_8_2.txt; do
    if [ -e "$O/$x" ]; then echo "dry run: NOTE $REL/$x is here already (step 8-seeds checks it is what it must be)"; fi
  done
  mkdir -p "$tmp/root/rl/results" "$tmp/root/$REL/scratch_8b2"   # a root: this folder's new files here, the rest the repository's (links)
  ln -s "$R/decks" "$tmp/root/decks"
  for x in "$OLDREL" rl/results/kt_carrier_census_2026-09-26; do ln -s "$R/$x" "$tmp/root/$x"; done
  git -C "$R" cat-file blob "$WATER_BLOB" > "$tmp/root/$REL/$WATER_DST"
  out=$(python3 "$CK3" pairs --set 8b2 --repo "$tmp/root" --seed-base "$SEED_NEW" --out "$tmp/pairs_8b2.tsv") || halt "pairs 8b2: $out"
  echo "dry run: $out"
  out=$(python3 "$CK3" pairs --set will --repo "$tmp/root" --seed-base "$SEED_NEW" --out "$tmp/pairs_will.tsv") || halt "pairs will: $out"
  echo "dry run: $out"
  out=$(python3 "$CK3" seedrec --repo "$tmp/root" --out "$tmp/seeds_8_2.txt" --reuse "$REUSEF" \
        --rows "8b, the cloud's rows|$tmp/$CLOUD_PAIRS|32-37|km3=40,k3=40" "8b, the new rows|$tmp/pairs_8b2.tsv|40-46|km3=40,k3=40" \
               "8, Oct 1's carriers|$R/$OLDREL/pairs_8.tsv|0-31|km3=500,k3=250" "8, the Will rows|$tmp/pairs_will.tsv|60-62|km3=500,k3=250") \
    || halt "seedrec: $out"
  echo "dry run: $out"
  lst=$(python3 "$CK" pairs-decks "$tmp/$CLOUD_PAIRS" "$tmp/pairs_8b2.tsv" "$tmp/pairs_will.tsv" "$R/$OLDREL/pairs_8.tsv") || halt "pairs-decks on the dry run's pairs files"
  mapfile -t lp <<< "$lst"; n=0
  for p in "${lp[@]}"; do
    want=$(expected_blob "$p"); got=$(git -C "$R" hash-object --no-filters -- "$tmp/root/$p")
    [ -n "$want" ] && [ "$got" = "$want" ] || halt "the dry run's deck $p is ${got:0:7}, not ${want:-nothing}"
    grep -qF "  $p $got" "$tmp/seeds_8_2.txt" || halt "seeds_8_2.txt does not list $p with its blob $got"
    n=$((n + 1))
  done
  echo "dry run: the $n deck files of the four pairs files are the blobs they must be (the candidate's, or main's before sitting 1; Oct 1's carriers/ and scratch_8b/ its seeds_8.txt's; water_round2 P's), and seeds_8_2.txt lists each with its blob id"
  echo "dry run: pairs_8b2.tsv rows 40 and 46: $(sed -n '2p;8p' "$tmp/pairs_8b2.tsv" | cut -f1,3,5,7,8 | tr '\t' ' ' | tr '\n' ';'); pairs_will.tsv rows: $(sed -n '2,4p' "$tmp/pairs_will.tsv" | cut -f1,3,5,7,8 | tr '\t' ' ' | tr '\n' ';'); the cloud's rows 36-37: $(awk -F'\t' '$1 == 36 || $1 == 37' "$tmp/$CLOUD_PAIRS" | cut -f1,3,5,7,8 | tr '\t' ' ' | tr '\n' ';')"
  for x in pairs_8b2.tsv pairs_will.tsv seeds_8_2.txt; do
    if [ -e "$O/$x" ]; then cmp -s -- "$tmp/$x" "$O/$x" && echo "dry run: $x is here and equals what step 8-seeds writes" || echo "dry run: NOTE $x is here and differs from what step 8-seeds writes (step 8-seeds would halt)"; fi
  done
  blob_check_inputs2 "$tmp/root" "$tmp"
  echo "dry run: sitting 2's $BLOBS2_OK repository inputs are the blobs they must be; by step: 8b and 8 $(group_rel 8 "$tmp" | grep -c .) files (Oct 1's pairs_8.tsv, ${#REUSE_PATHS[@]} reused game files, the decks), 9 $(group_rel 9 "$tmp" | grep -c .), 10 $(group_rel 10 "$tmp" | grep -c .)"
  x=$(tools_bad)
  if [ -z "$x" ]; then echo "dry run: the ${#TOOL_ROWS[@]} 8c tools of tools_8c.tsv are the blobs it names at the commits it names: $(for x in "${TOOL_ROWS[@]}"; do IFS=$'\t' read -r role path tc tb <<< "$x"; printf '%s %s; ' "$role" "${tc:0:8}"; done)"
  else echo "dry run: NOTE the 8c tools of tools_8c.tsv are not all the blobs it names (a start refuses; Fetch origin?): $x"; notes=$((notes + 1)); fi
  x=$(s1_counters_why)
  if [ -z "$S1_WHY" ]; then
    if [ -z "$x" ]; then echo "dry run: counters.tsv is the one sitting 1's last START line recorded"
    else echo "dry run: NOTE $x (a start refuses)"; notes=$((notes + 1)); fi
  fi
  if git -C "$R" show "$PX:$REL/tightened_rule.py" > "$tmp/tightened_rule.py" 2> /dev/null; then
    out=$(python3 "$CK3" model --counters "$CNT" --tightened "$tmp/tightened_rule.py") || halt "counters.tsv: $out"
  else
    out=$(python3 "$CK3" model --counters "$CNT") || halt "counters.tsv: $out"; out+="; NOTE P has no $REL/tightened_rule.py to compare ROUND2_QUEUED with"
  fi
  echo "dry run: $out"
  if [ "$MAGCHK" = TO_FINALIZE ]; then echo "dry run: NOTE MAGNEZONE_CARD_CHECK is TO FINALIZE (PLAN step 8b: 8b's block-coin rows wait for the cloud's card checks; a start refuses)"
  elif git -C "$R" cat-file -e "${MAGCHK%%:*}:${MAGCHK#*:}" 2> /dev/null; then echo "dry run: MAGNEZONE_CARD_CHECK $MAGCHK is here"
  else echo "dry run: NOTE MAGNEZONE_CARD_CHECK $MAGCHK is not here (Fetch origin; a start refuses)"; notes=$((notes + 1)); fi
  for x in "${REFS2[@]}"; do
    p=${x%%|*}; sha=${x#*|}
    git -C "$R" cat-file -e "$CB:$p" 2> /dev/null || halt "the reference $p is not in ${CB:0:7}"
    got=$(git -C "$R" cat-file blob "$CB:$p" 2> /dev/null | sha256sum | cut -c1-64) || true
    [ -z "$sha" ] || [ "$got" = "$sha" ] || halt "the reference $p in ${CB:0:7} has sha256 ${got:0:16}.., not ${sha:0:16}.."
  done
  echo "dry run: sitting 2's ${#REFS2[@]} references are in ${CB:0:7}; step 9's six and the goldfish page and coverage with the sha256 recorded when they were made; run_screen.txt (sha256 as given Oct 1) and the 5 command-line outputs blob-checked, their sha256 to be recorded in refs2"
  for x in "${SPEC9[@]}"; do
    IFS='|' read -r nm pf sb pl n ref sha _ <<< "$x"
    got=$(git -C "$R" cat-file blob "$CB:$KMT/$ref" | python3 -c '
import json, sys
g = [json.loads(l) for l in sys.stdin if l.strip()]
print(len(g), ",".join(str(p) for p in sorted({x["pairing"] for x in g})), min(x["seed"] - 10000 * x["pairing"] - x["i"] for x in g), max(x["seed"] - 10000 * x["pairing"] - x["i"] for x in g), sorted({x["bot_a"] + "/" + x["bot_b"] for x in g}), sorted({x.get("a_file") is not None for x in g}))')
    [ "$got" = "$n $pl $sb $sb ['km3/km3'] [True]" ] || halt "step 9's $nm: its reference holds '$got', not '$n $pl $sb $sb km3/km3 with files' (games, pairings, seed base, bots)"
  done
  echo "dry run: step 9's six references hold exactly the games, pairings and seed bases of SPEC9 (km3 both sides, --pairs rows); the B2e one names pairings $NAMED9 among its 96"
  mapfile -t lp < <(ls "$R/decks/research")
  [ "${lp[0]:-}" = altaria.txt ] && [ "${lp[1]:-}" = blaziken.txt ] || halt "decks/research's first two lists are not altaria.txt and blaziken.txt"
  echo "dry run: step 10: decks/research starts with altaria.txt, blaziken.txt; $BREW06 and $BREW06B are here; run_screen.py sha256 $(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-16) (the reference was made with 4f102352)"
  if [ -e "$O/trace_load.txt" ]; then
    rc=0; out=$(python3 "$CK3" trace-gate "$O/trace_load.txt") || rc=$?
    committed "$REL/trace_load.txt" && t="committed" || t="NOT committed (step 8 would wait until it is)"
    echo "dry run: trace_load.txt is here, $t: exit $rc, $(reword "$(head -n 1 <<< "$out")")"
    x=$(sed -n 's/^COMMIT \([0-9a-f]*\)$/\1/p' <<< "$out" | head -n 1)
    if [ -n "$x" ]; then git -C "$R" cat-file -e "$x^{commit}" 2> /dev/null && echo "dry run: its commit $x is here" || echo "dry run: NOTE its commit $x is not here (step 8 would wait; Fetch origin)"; fi
    x=$(sed '1s/^\xEF\xBB\xBF//' "$O/trace_load.txt" | tr -d '\r' | grep -E '^CLOUD8B(_OLD)?( |$)' || true)
    if [ -z "$x" ]; then echo "dry run: no CLOUD8B line (8b compares its rows with P's early_warning_8b/ files itself)"
    else
      while IFS=' ' read -r t nm role path p; do
        if [[ $nm =~ ^[0-9a-f]{7,40}$ && $role =~ ^(km3|k3)$ && -n $path && -z $p ]] && git -C "$R" cat-file -e "$nm:$path" 2> /dev/null; then
          echo "dry run: $t $role: $nm:$path is here, $(git -C "$R" show "$nm:$path" | grep -c .) rows (compared once 8b has run)"
        else echo "dry run: NOTE the line '$t $nm $role $path${p:+ $p}' is malformed or its file is not here: it would be noted as not compared (owed)"; fi
      done <<< "$x"
    fi
  else echo "dry run: NOTE trace_load.txt is not here: step 8 would wait after 8b; steps 9 and 10 run, the gate is read again, and the run ends SITTING 2 PAUSED if it still waits (its proposed line, from the cloud's early_warning_8b/README.md: TRACE LOAD 0 with that folder's commit)"; fi
  [ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] && echo "dry run: the working copy is on main" || echo "dry run: NOTE the working copy is not on main (a start refuses)"
  nst=$(git -C "$R" diff --cached --name-only -- "$REL")
  if [ -z "$nst" ]; then echo "dry run: nothing in $REL is staged in the shared index"
  else
    mapfile -t stg <<< "$nst"
    if git -C "$R" diff --quiet -- "${stg[@]}"; then echo "dry run: NOTE staged in the shared index under $REL, equal to the working copy (a start unstages them): $(tr '\n' ' ' <<< "$nst")"
    else echo "dry run: NOTE staged in the shared index under $REL, and different from the working copy (a start refuses): $(tr '\n' ' ' <<< "$nst")"; fi
  fi
  for x in "${HELPERS[@]/#/$REL/}" "$SCREEN_WITH"; do
    if committed "$x"; then t="committed"; else t="NOT committed as it is here (a start refuses until it is)"; notes=$((notes + 1)); fi
    echo "dry run: ${x#"$REL"/}: $t"
  done
  git -C "$R" check-ignore -q -- "$REL/.sitting2.lock" && echo "dry run: .sitting2.* is ignored by git" \
    || echo "dry run: NOTE .sitting2.* is not in .gitignore: the lock, .ours and .pgid files will show as untracked in GitHub Desktop (never commit them)"
  if seed_rows_ok; then echo "dry run: START_HERE.md (committed) has a line holding $(commas "$SEED_NEW") and 36–37, and its $(commas "$SEED_OLD") row holds 36–37"
  elif seed_rows_ok work; then echo "dry run: NOTE START_HERE.md holds switch 2's seed rows in the working copy only: a start refuses until they are committed (with the runners)"; notes=$((notes + 1))
  else echo "dry run: NOTE START_HERE.md has no line holding $(commas "$SEED_NEW") and 36–37, or its $(commas "$SEED_OLD") row lacks 36–37 (seed_row_23_3B.md drafts both rows): a start refuses until they are committed"; notes=$((notes + 1)); fi
  x=$(git_locks); [ -z "$x" ] && echo "dry run: no git lock file (index.lock, refs/heads/main.lock)" || echo "dry run: NOTE git lock file here now: $(tr '\n' ' ' <<< "$x")(a start waits 15 s for it, then refuses)"
  if s1_lock_held; then echo "dry run: NOTE .sitting1.lock is held (sitting1.sh or its child is running): a start refuses"; else echo "dry run: .sitting1.lock is not held"; fi
  x=$(env_set_now); [ -z "$x" ] && echo "dry run: env: no DECKGYM_* (nor PDL_EQUIV_DEALS, GOLDFISH_TRACE) is set here" || { echo "dry run: NOTE set here: $x(a start refuses: at P the engine reads its revert switches from the environment)"; notes=$((notes + 1)); }
  x=$(busy_now); [ -z "$x" ] && echo "dry run: nothing else runs (no game program, cargo or rustc outside this group; no other live launch_detached run)" || echo "dry run: NOTE running now: $x(a start refuses unless BUSY_OK=1; the combined run must have ended)"
  x=$(reserved_clash "$PX"); [ -z "$x" ] && echo "dry run: P ${PX:0:7}'s paths under $REL clash with nothing on main or in the working copy (ADAPTATION_SPEC 1.10)" || { echo "dry run: NOTE P's tree holds paths under $REL that main or the working copy holds with other bytes (step 4 and the pin check this and stop; sitting 2 notes it): $x"; notes=$((notes + 1)); }
  if git -C "$R" merge-base --is-ancestor "$o" "$m"; then
    unpushed_check "$o" "$m"
    echo "dry run: origin/main ${o:0:7} is main or behind it ($(git -C "$R" rev-list --count "$o..$m") unpushed commits; this switch's by its own record or touching only $REL and START_HERE.md: $(( $(git -C "$R" rev-list --count "$o..$m") - $(wc -w <<< "$FOREIGN") )))"
    [ -z "$FOREIGN" ] || echo "dry run: NOTE main carries unpushed commits that are not this switch's: $FOREIGN(a start refuses)"
  else echo "dry run: NOTE origin/main ${o:0:7} has commits main lacks: a start refuses (Pull origin first)"; fi
  if daytime_refused; then echo "dry run: NOTE it is $(date -u +%a\ %H:%M) UTC: with ALLOW_DAYTIME=$ALLOW_DAYTIME a start now without an explicit DEADLINE refuses (daytime)"; fi
  out=$(grep -E '^SITTING 2 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
  echo "dry run: sitting 2's last state: ${out:-none (no sitting 2 run yet)}; steps done: $(done_list)"
  rc=0; out=$(GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" push --dry-run --porcelain origin "refs/heads/main:refs/heads/main" 2>&1) || rc=$?
  echo "dry run: git push --dry-run origin main (no write; the credentials): exit $rc, $(grep -E '^[=!*+ -]|^Done|rejected|fatal|error' <<< "$out" | head -n 3 | tr '\n' ' ')"
  echo "dry run: step 8-seeds would: fetch (at most 2 min); check Oct 1's files in place and the cloud's pinned rows 32-35 v Oct 1's; copy the cloud's pairs file to $CLOUD_PAIRS and water_round2 to $WATER_DST from P; write pairs_8b2.tsv, pairs_will.tsv, seeds_8_2.txt, ${S}_refs2.sha256 (into $B/ref2), ${S}_inputs2.sha256; commit and push them before any game"
  echo "dry run: step 8b would run, for km3 then k3: (cd $B/engine; RAYON_NUM_THREADS=$THREADS nice -n $NICE) $OLD_SCAN on pairings $P8B_PLAYED, then <new legality_scan> and (cd $W/engine) <watch legality_scan> on $P8B_CLOUD, each --pairs $O/$CLOUD_PAIRS --root <repo> --seed-base $SEED_OLD --bot <bot> --games 40; then old, new and watch on $P8B_NEW with --pairs $O/pairs_8b2.tsv --seed-base $SEED_NEW; switch_check.py same (watch v new) and sitting2_check.py touched per set; this run's rows v P's early_warning_8b/ files (new 240, old 80 a bot)"
  echo "dry run: step 8 (only when 8c's gate passes, after 8b or again after step 10) would run new and watch on Oct 1's pairings 0-31 (km3 --games 500, k3 --games 250; --pairs $R/$OLDREL/pairs_8.tsv --seed-base $SEED_OLD; the old side Oct 1's ${REUSE8[km3]##*/} and ${REUSE8[k3]##*/}), then old, new and watch on $PWILL (--pairs $O/pairs_will.tsv --seed-base $SEED_NEW)"
  echo "dry run: step 9 would run (cd $B/engine) <new legality_scan> --bot km3 --games 500 on: $(for x in "${SPEC9[@]}"; do IFS='|' read -r nm pf sb pl n _ <<< "$x"; printf '%s (%s, seed base %s, %s games); ' "$nm" "${pf##*/}" "$sb" "$n"; done)each v its reference (switch_check.py same; B2e with --exclude-pairings $NAMED9: 40,000); then (cd $W/engine) the watch legality_scan on B2e's pairings $NAMED9 (8,000), watch v plain on them, and sitting2_check.py touched (the reference as the old side)"
  echo "dry run: step 10 would run (cd <repo>) <new deckgym> simulate --num 240 --players <code>,<code> --seed 7100 --seed-stream -p $CLI_P0 $CLI_P1 for ${CLI_CODES[*]}; (cd $B/engine) <new goldfish> --deck <repo>/$CLI_P0 --panel <repo>/decks/screen/opponents --games 0 --coverage; (cd <repo>) python3 screen_with.py <new deckgym> <its sha256> decks/screen/run_screen.py $BREW06 $BREW06B --games 240 --pilot km3 --meta-pilot km3 --seed 7100"
  echo "dry run: a start now would have the deadline $(fmt "$DL") ($DEADLINE), the hard stop $(fmt "$HS") and the push-by time $(fmt "$PB"); at $(rate) games a second x $SAFETY + $OVERHEAD_MIN min: 8-seeds $(( $(need_s 8-seeds) / 60 )) min, 8b $(( $(need_s 8b) / 60 )) ($(games_left 8b) games), 8 $(( $(need_s 8) / 60 )) ($(games_left 8)), 9 $(( $(need_s 9) / 60 )) ($(games_left 9)), 10 $(( $(need_s 10) / 60 )) ($(games_left 10))"
  if [ "$notes" -eq 0 ]; then echo "dry run: every check passes (nothing written outside /tmp)"
  else echo "dry run: every check here passes, with $notes NOTE line(s) above that make a start refuse until they are settled (nothing written outside /tmp)"; fi
  FINISHED=1; exit 0
}

trap on_exit EXIT
read_data; set_names   # neither halts: the dry run reports what they found, a start refuses on it
if [ $DRY -eq 1 ]; then S=dry; dry_run; fi

# ---- One run at a time; refusals before the start line; the state of the last run.
exec 9> "$O/.sitting2.lock"
flock -n 9 || { echo "$(ts) sitting2.sh: another sitting2.sh (or its orphaned child) holds $O/.sitting2.lock; this one exits" >&2; exit 2; }
rm -f -- "$O/.sitting2.ckpt" "$O/.sitting2.hardstop"   # the flags a power-off or a SIGKILL leaves behind
refuse() { echo "$(ts) sitting2.sh: start refused: $*" >&2; exit 2; }
[ -z "$DATA_WHY" ] || refuse "the data files cannot be read as they must be (ADAPTATION_SPEC Appendix A): $DATA_WHY"
[ ${#MARKS[@]} -eq 0 ] || refuse "$(printf '%s; ' "${MARKS[@]}")(PLAN: P is not final yet; once the cloud says P landed, fill them in, commit, then start again)"
s1_state
[ -z "$S1_WHY" ] || refuse "sitting 1 is not DONE yet: $S1_WHY. Sitting 2 runs on sitting 1's candidate and programs: run sitting1.sh first"
CB=$C
if s1_lock_held; then refuse "sitting1.sh (or its orphaned child) holds $O/.sitting1.lock: one sitting at a time. If no sitting1.sh runs (SITTING=1 bash quiet.sh status), its lock is free, so look for the process holding it (fuser .sitting1.lock)"; fi
for x in "${HELPERS[@]/#/$REL/}" "$SCREEN_WITH"; do
  committed "$x" || refuse "$x is not committed as it is here; commit sitting2.sh, its helpers and the data files first (the evidence names committed code)"
done
[ "$(git -C "$R" symbolic-ref -q HEAD 9>&- || true)" = refs/heads/main ] || refuse "the working copy is not on main"
if daytime_refused; then
  refuse "it is $(date -u +%a\ %H:%M) UTC, daytime$([ "$ALLOW_DAYTIME" = 0 ] && echo ", and ALLOW_DAYTIME=0" || echo " on a weekday (ALLOW_DAYTIME=auto: Dustin's word covers the weekend; a weekday is class and travel)"): give DEADLINE explicitly (school, HH:MM UTC, an ISO time, or off), or start with ALLOW_DAYTIME=1"
fi
seed_rows_ok || refuse "START_HERE.md, as committed, has no line holding $(commas "$SEED_NEW") and 36–37, or its $(commas "$SEED_OLD") row does not hold 36–37 (rules switch 2's seed rows, both drafted in seed_row_23_3B.md; PLAN section 5: added and committed before any game)"
x=$(env_set_now)
[ -z "$x" ] || refuse "these environment variables are set: $x- at P the engine reads its revert switches (DECKGYM_*) from the environment, so one left set would play another engine with every program hash passing (ADAPTATION_SPEC 1.8): unset them, then start again"
x=$(tools_bad)
[ -z "$x" ] || refuse "the 8c tools of tools_8c.tsv are not all the blobs it names at the commits it names: $x(the hand-off names them so; Fetch origin, or finalize tools_8c.tsv when the cloud's tools land)"
x=$(s1_counters_why)
[ -z "$x" ] || refuse "$x"
git -C "$R" cat-file -e "${MAGCHK%%:*}:${MAGCHK#*:}" 9>&- 2> /dev/null || refuse "MAGNEZONE_CARD_CHECK names $MAGCHK, which is not here (PLAN step 8b: 8b's block-coin rows wait for the cloud's card checks of c-magnezone_ex_magnezone.txt; Fetch origin)"
x=$(python3 "$O/sitting2_check.py" model --counters "$O/counters.tsv" 9>&- 2>&1) || refuse "counters.tsv does not read as sitting2_check.py's model: $x"
CLASH=$(reserved_clash "$P")   # ADAPTATION_SPEC 1.10: step 4 and the pin stop on it; here a NOTE in the START line and PIN_STATUS.txt
# Before the shared index is touched (the unstage below), as sitting1.sh does it.
if [ "$BUSY_OK" = 1 ]; then BUSYNOTE="BUSY_OK=1, running now: $(busy_now)"
else
  BUSYNOTE=$(busy_now)
  [ -z "$BUSYNOTE" ] || refuse "another run is going: $BUSYNOTE(PLAN section 9, question 5: never beside a sitting; the 2-day combined run must have ended, its chain script included). BUSY_OK=1 starts anyway"
  BUSYNOTE="nothing else runs"
fi
LK=""
for x in $(seq 1 15); do LK=$(git_locks); [ -n "$LK" ] || break; sleep 1; done
[ -z "$LK" ] || refuse "git's lock file $(tr '\n' ' ' <<< "$LK")is here and stayed 15 s (a git program is running, or a power-off left it there). If GitHub Desktop and every other git program are idle, delete it, then start again"
UNSTAGED=""
x=$(git -C "$R" diff --cached --name-only -- "$REL" 9>&-)
if [ -n "$x" ]; then  # an interrupted checkpoint leaves the working copy's own content staged here: that is unstaged
  mapfile -t STG <<< "$x"
  git -C "$R" diff --quiet -- "${STG[@]}" 9>&- \
    || refuse "files in $REL are staged in the shared index and differ from the working copy: $(tr '\n' ' ' <<< "$x")- if no other session staged them (only the runners write here), unstage them, which leaves the files as they are (git -C \"$R\" reset -q -- $REL; in GitHub Desktop nothing is staged), then start again"
  git -C "$R" reset -q -- "${STG[@]}" 9>&- || refuse "files in $REL are staged in the shared index (the working copy's content) and unstaging them failed: $(tr '\n' ' ' <<< "$x")"
  UNSTAGED="; unstaged at this start (staged equal to the working copy, as an interrupted checkpoint leaves them): $(sed "s#^$REL/##" <<< "$x" | tr '\n' ' ')"
fi
if GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then FETCHED="fetched origin"
else FETCHED="git fetch origin failed or timed out (offline?), so origin/main as last fetched"; fi
x=$(git -C "$R" rev-parse refs/heads/main 9>&-); LK=$(git -C "$R" rev-parse refs/remotes/origin/main 9>&-)
git -C "$R" merge-base --is-ancestor "$LK" "$x" 9>&- \
  || refuse "origin/main ${LK:0:7} has commits main ${x:0:7} lacks ($FETCHED): no checkpoint could be pushed. In GitHub Desktop: Fetch origin, Pull origin, Push origin; then start again"
unpushed_check "$LK" "$x"
[ -z "$FOREIGN" ] || refuse "main carries commits that are not on origin/main and are not this switch's: $FOREIGN(another session's work, or a Pull's merge commit). This run pushes only its own commits: have them pushed first (GitHub Desktop: Push origin, with their owner's word), then start again"
if [ ${#ALLOWED_NEW[@]} -gt 0 ]; then printf '%s\n' "${ALLOWED_NEW[@]}" >> "$CKPT_OURS"; fi
PUSHNOTE="$FETCHED; main ${x:0:7}, origin/main ${LK:0:7}, $(git -C "$R" rev-list --count "$LK..$x" 9>&-) unpushed commits, all this switch's$([ ${#ALLOWED_NEW[@]} -eq 0 ] || echo " (allowed at this start, as they touch only $REL and START_HERE.md: $(printf '%s\n' "${ALLOWED_NEW[@]}" | cut -c1-7 | tr '\n' ' ' | sed 's/ $//'))")"
LOCKED=1
st=$(cat "/proc/$PG/stat" 2> /dev/null || echo "$PG (?) ? 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"); st=${st##*) }; read -r -a stf <<< "$st"
echo "$PG $(ts) ${stf[19]:-0}" > "$O/.sitting2.pgid"   # the run's group id, the time, the group leader's start time (quiet.sh checks it)
trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
PRIV=$(mktemp -d /tmp/sitting2_rules2.XXXXXX) || { PRIV=""; die "mktemp -d for the private copies"; }
cp -- "$O/switch_check.py" "$O/sitting1_check.py" "$O/sitting2_check.py" "$O/checkpoint.sh" "$R/$SCREEN_WITH" "$PRIV/" || die "copying the helpers"
for x in "${DATA_READ[@]}"; do
  cp -- "$O/$x" "$PRIV/$x" || die "copying $x"
  cmp -s -- "$O/$x" "$PRIV/$x" || die "$x changed while it was copied"
done
CK="$PRIV/switch_check.py"; CK2="$PRIV/sitting1_check.py"; CK3="$PRIV/sitting2_check.py"; SW="$PRIV/screen_with.py"
CNT="$PRIV/counters.tsv"; ENVF="$PRIV/switch2.env"; TOOLSF="$PRIV/tools_8c.tsv"; REUSEF="$PRIV/reuse.tsv"
export SWITCH2_COUNTERS="$CNT"   # sitting1_check.py and sitting2_check.py read the private copy (ADAPTATION_SPEC C1-9)
# shellcheck source=checkpoint.sh
source "$PRIV/checkpoint.sh"
last=$(grep -E '^SITTING 2 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
case $last in
  "SITTING 2 HALT "*)
    if [ -z "${SITTING2_AFTER_HALT:-}" ]; then
      echo "$(ts) sitting2.sh: start refused: the last run halted ($last). A mismatch stops everything and goes to Dustin first; once it is explained (or a script fault is fixed), start with SITTING2_AFTER_HALT='<written reason>'" >&2
      LOCKED=0; exit 2
    fi
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    echo "SITTING 2 RESUMED AFTER HALT $(ts) ${S:-?}: SITTING2_AFTER_HALT='${SITTING2_AFTER_HALT//$'\n'/ }' (stamp $stamp)" >> "$O/STATUS.txt"
    # The halted run's check files are kept (a step that runs again starts its file afresh) and committed with the next
    # checkpoint, so its lines survive even if the halt's own record commit failed.
    for x in touched_8b.txt:8b touched_8.txt:8 identity_9.txt:9 touched_9.txt:9 identity_10.txt:10; do
      f=${x%%:*}; n=${x#*:}
      if [ -s "$O/$f" ] && ! grep -q "^STEP $n DONE ${S:-none} " "$O/STATUS.txt"; then
        mv -- "$O/$f" "$O/${f%.txt}.before_resume_$stamp.txt"; KEEP_FILES+=("$REL/${f%.txt}.before_resume_$stamp.txt")
        echo "$(ts) the halted run's $f is kept as ${f%.txt}.before_resume_$stamp.txt (committed with the next checkpoint); step $n writes $f afresh" >> "$O/STATUS.txt"
      fi
    done;;
  "SITTING 2 DONE "*)
    echo "$(ts) sitting2.sh: SITTING 2 DONE is already recorded ($last); nothing to do" >&2; LOCKED=0; exit 0;;
esac
CODELINE="sitting2.sh $(sha256sum < "$O/sitting2.sh" | cut -c1-16), checkpoint.sh $(sha256sum < "$PRIV/checkpoint.sh" | cut -c1-16), switch_check.py $(sha256sum < "$CK" | cut -c1-16), sitting1_check.py $(sha256sum < "$CK2" | cut -c1-16), sitting2_check.py $(sha256sum < "$CK3" | cut -c1-16), screen_with.py $(sha256sum < "$SW" | cut -c1-16); data: $(data_sums) (sha256; HEAD $(git -C "$R" rev-parse --short HEAD 9>&-))"
IGN=""; git -C "$R" check-ignore -q -- "$REL/.sitting2.lock" 9>&- || IGN="; NOTE .sitting2.* is not in .gitignore (its lock, .ours and .pgid files show as untracked: never commit them)"
if [ -n "$CLASH" ]; then
  IGN+="; NOTE P's tree holds paths under $REL that main or the working copy holds with other bytes (the pin's merge would conflict there; step 4 and the pin stop on it): $CLASH"
  pin_note "NOTE at sitting 2's start: P's tree holds paths under $REL that main or the working copy holds with other bytes (ADAPTATION_SPEC 1.10): $CLASH"
fi
echo "SITTING 2 START $(ts) ${S:-?}: $KNOBS; pid $$, process group $PG$([ -z "${LAUNCH_DETACHED_RUN:-}" ] || echo " (launch_detached $LAUNCH_DETACHED_RUN)"); load $(cut -d' ' -f1-3 /proc/loadavg); env: no DECKGYM_* set; busy: $BUSYNOTE; P ${P:0:7} (engine/ ${P_TREE:0:7}), candidate ${C:0:7} (main ${MAIN_C:0:7}); code: $CODELINE (the checks run from private copies made now); git: $PUSHNOTE$UNSTAGED$IGN" >> "$O/STATUS.txt"
pin_note "sitting 2 start ${S:-?}: $CODELINE"
if [ "$HS" -gt 0 ]; then  # the watchdog: past HARD_STOP (read every 20 s, so also after a sleep), outside a checkpoint, TERM to the group
  ( trap - EXIT HUP INT TERM; exec 9>&-
    while sleep 20; do
      [ "$(date +%s)" -ge "$HS" ] || continue
      [ ! -e "$O/.sitting2.ckpt" ] || continue
      : > "$O/.sitting2.hardstop"; kill -TERM -- "-$PG" 2> /dev/null; exit 0
    done ) &
  WD=$!
fi

# ---- Sitting 1's record and programs (a halt if any is not as recorded).
STEP=start
s1_checks; set_paths
step_is_done 8-seeds || rm -f -- "$REFSUM2" "$INPUTS2"   # an unfinished 8-seeds' records: made again there
check_pins "at this start"; old_programs
s1_records
for x in 8b 9 10; do  # a DONE step's inputs and references: drift after its games is a note
  if step_is_done "$x"; then step_io "$x" "at this start" note; fi
done
PIN_GYM=$(prog_sha "$GYM")
note "sitting 1's record holds: candidate $C (main ${MAIN_C:0:7} + P ${P:0:7}; engine/ = P's tree), SITTING 1 DONE, its 6 manifests as recorded; the programs are its builds ($B, $W) as recorded, never rebuilt; $OLD_DIR/ as switch2.env, its SHA256SUMS and the manifest record it; $S1REC"

# ---- Step 8-seeds: the copies, the pairs and the seeds, Oct 1's files checked, before any game.
if step_is_done 8-seeds; then STEP=8-seeds; skip_done 8-seeds
else
  begin_step 8-seeds "Oct 1's reused files checked in place; the cloud's pairs file and water_round2 copied from P; pairs_8b2.tsv, pairs_will.tsv and seeds_8_2.txt; sitting 2's references and inputs: before any game"
  if GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then note "fetched origin"
  else note "git fetch origin failed or timed out (offline?): $P_BRANCH as last fetched (P ${P:0:7} is here: sitting 1 used it)"; fi
  reuse_checks; note "$REUSE_NOTE"
  cloud_checks "$PRIV"; note "$CLOUD_NOTE"
  copy_blob "$CLOUD_PAIRS_BLOB" "$O/$CLOUD_PAIRS" "$REL/$CLOUD_PAIRS"
  copy_blob "$WATER_BLOB" "$O/$WATER_DST" "$REL/$WATER_DST"
  for x in "$CLOUD_PAIRS|$CLOUD_PAIRS_BLOB" "$WATER_DST|$WATER_BLOB"; do  # what git add stores (the attributes say -text: the same bytes)
    p=${x%%|*}; want=${x##*|}
    [ "$(git -C "$R" hash-object -- "$REL/$p" 9>&-)" = "$want" ] || halt "$REL/$p would not be stored as the blob ${want:0:7} (git's filters)"
  done
  note "copied byte for byte from P ${P:0:7}: the cloud's $CLOUD8B_DIR/pairs_8b.tsv to $CLOUD_PAIRS and $WATER_SRC to $WATER_DST; each file's blob id checked"
  : > "$PRIV/pairs.out"
  for x in 8b2 will; do
    python3 "$CK3" pairs --set "$x" --repo "$R" --seed-base "$SEED_NEW" --out "$PRIV/pairs_$x.tsv" >> "$PRIV/pairs.out" 2>&1 \
      || halt "pairs $x: $(tail -n 1 "$PRIV/pairs.out")"
  done
  for f in pairs_8b2.tsv pairs_will.tsv; do
    if [ -e "$O/$f" ]; then cmp -s -- "$PRIV/$f" "$O/$f" || halt "$f is here but is not what sitting2_check.py pairs writes now (a deck changed?)"
    else cp -- "$PRIV/$f" "$O/$f.part"; durable "$O/$f.part"; mv -- "$O/$f.part" "$O/$f"; fi   # synced before the rename
  done
  python3 "$CK3" seedrec --repo "$R" --out "$PRIV/seeds_8_2.txt" --reuse "$REUSEF" \
    --rows "8b, the cloud's rows|$O/$CLOUD_PAIRS|32-37|km3=40,k3=40" "8b, the new rows|$O/pairs_8b2.tsv|40-46|km3=40,k3=40" \
           "8, Oct 1's carriers|$R/$OLDREL/pairs_8.tsv|0-31|km3=500,k3=250" "8, the Will rows|$O/pairs_will.tsv|60-62|km3=500,k3=250" \
    >> "$PRIV/pairs.out" 2>&1 || halt "seedrec: $(tail -n 1 "$PRIV/pairs.out")"
  if [ -e "$O/seeds_8_2.txt" ]; then cmp -s -- "$PRIV/seeds_8_2.txt" "$O/seeds_8_2.txt" || halt "seeds_8_2.txt is here but is not what seedrec writes now (a deck or a reused file changed?)"
  else cp -- "$PRIV/seeds_8_2.txt" "$O/seeds_8_2.txt.part"; durable "$O/seeds_8_2.txt.part"; mv -- "$O/seeds_8_2.txt.part" "$O/seeds_8_2.txt"; fi
  note "$(tr '\n' ' ' < "$PRIV/pairs.out")"
  extract_refs2
  write_inputs2
  STEP_FILES=("$CLOUD_PAIRS" "$WATER_DST" pairs_8b2.tsv pairs_will.tsv seeds_8_2.txt "${S}_refs2.sha256" "${S}_inputs2.sha256")
  finish_step 8-seeds "Oct 1's reused games, pairs_8.tsv and decks as recorded, and Oct 1's reused 8b games equal to the cloud's pinned rows on 32-35; the cloud's pairs file (pairings 32-37, seeds $(commas "$SEED_OLD")) and water_round2 from P byte for byte; pairs_8b2.tsv (40-46) and pairs_will.tsv (60-62), seeds $(commas "$SEED_NEW") + 10,000 x pairing + i; seeds_8_2.txt; ${#REFS2[@]} references for steps 9 and 10; sitting 2's inputs recorded; all before any game"
  for x in "$CLOUD_PAIRS|$CLOUD_PAIRS_BLOB" "$WATER_DST|$WATER_BLOB"; do
    p=${x%%|*}; want=${x##*|}
    [ "$(git -C "$R" rev-parse -q --verify "refs/heads/main:$REL/$p" 9>&- || true)" = "$want" ] || halt "main's $REL/$p is not the blob ${want:0:7} after the checkpoint"
  done
fi
SEED_CLOUD=$(cloud_base "$O/$CLOUD_PAIRS") || halt "the rows of $CLOUD_PAIRS do not share one seed block"
[ "$SEED_CLOUD" = "$SEED_OLD" ] || halt "$CLOUD_PAIRS's seed block is $SEED_CLOUD, not $SEED_OLD"

# ---- Step 8b: the early-warning rows.
if step_is_done 8b; then STEP=8b; skip_done 8b
else
  begin_step 8b "the early-warning rows: the cloud's 32-37 (new and watch; old on 36-37, Oct 1's reused games on 32-35) and the new 40-46 (old, new and watch), km3 and k3 i < 40: $(games_left 8b) of 2,800 games still to play"
  : > "$O/touched_8b.txt"
  for x in km3 k3; do
    run_scan "${S}_8b_cloud_old_$x" "$OLD_SCAN" "$B/engine" "$P8B_PLAYED" 40 --pairs "$O/$CLOUD_PAIRS" --root "$R" --seed-base "$SEED_CLOUD" --bot "$x"
    scan_set 8b_cloud "$x" "$O/$CLOUD_PAIRS" "$SEED_CLOUD" "$P8B_CLOUD" 40 "reuse:$R/${REUSE8B[$x]},$O/${S}_8b_cloud_old_$x.jsonl"
  done
  for x in km3 k3; do
    scan_set 8b_new2 "$x" "$O/pairs_8b2.tsv" "$SEED_NEW" "$P8B_NEW" 40 play
  done
  cloud_rows_8b
  step_summary 8b
  STEP_FILES+=(touched_8b.txt)
  finish_step 8b "the early-warning rows (the cloud's 32-37, 240 a bot; the new 40-46, 280 a bot; i < 40): watch equal to new on every field for km3 and k3; every deal the same deal on the three sides; this run's rows equal the cloud's at P (${CLOUD_SUM}); $SUM (touched_8b.txt; every changed game in handoff_8c.tsv)"
fi

# ---- Step 8c's gate, then step 8: the carriers and the Will rows (if the gate waits now, it is read again after step 10).
if step_is_done 8; then STEP=8; skip_done 8
else
  STEP=8c; gate_8c
  if [ -z "$GATE_WHY" ]; then
    if fits_now 8; then run_step8
    else note "8c's gate passed, but step 8 (about $(( $(need_s 8) / 60 )) min) would end after the deadline $(fmt "$DL"): steps 9 and 10 run first, then the gate is read again and step 8 runs only if it then fits"; fi
  fi
fi

# ---- Step 9: km3's coverage baselines, and the 16 named B2e pairings on the watch build.
if step_is_done 9; then STEP=9; skip_done 9
else
  begin_step 9 "km3's coverage baselines on the new legality_scan: B2e (its 80 pairings without Ariados equal; 32-39 and 80-87 named), Scizor and the 4 second lists; then the watch build on the 16 named pairings: $(games_left 9) of 74,500 games still to play"
  : > "$O/identity_9.txt"; : > "$O/touched_9.txt"
  for x in "${SPEC9[@]}"; do
    IFS='|' read -r nm pf sb pl n ref sha label <<< "$x"
    run_scan "${S}_$nm" "$SCAN" "$B/engine" "$pl" 500 --pairs "$R/$pf" --root "$R" --seed-base "$sb" --bot km3
    if [ "$nm" = "$B2E_NAME" ]; then
      ident "$O/identity_9.txt" "$label; pairings $NAMED9 left out (named as expected to change: PLAN step 9)" "${S}_$nm" $((n - 8000)) "" \
        "--exclude-pairings=$NAMED9" "$B/ref2/$KMT/$ref"
    else ident "$O/identity_9.txt" "$label" "${S}_$nm" "$n" "" "" "$B/ref2/$KMT/$ref"; fi
  done
  run_scan "${S}_9_watch_b2e_km3" "$WSCAN" "$W/engine" "$NAMED9" 500 --pairs "$R/$B2E_PAIRS" --root "$R" --seed-base "$B2E_SEED" --bot km3
  ident "$O/touched_9.txt" "9 watch v plain, km3, B2e's named pairings $NAMED9, i < 500 (seeds 21,106,000,000 + 10,000 x pairing + i)" \
    "${S}_9_watch_b2e_km3" 8000 "" "--pairings=$NAMED9" "$O/${S}_$B2E_NAME.jsonl"
  touched_check 9 9_km3 km3 8000 "$O/touched_9.txt" "9 km3, B2e's named pairings $NAMED9, the reference v the new plain scan v the watch build" \
    "$O/${S}_$B2E_NAME.jsonl" "$O/${S}_9_watch_b2e_km3.jsonl" "--pairings=$NAMED9" "$B/ref2/$KMT/$B2E_REF"
  step_summary 9
  STEP_FILES+=(identity_9.txt touched_9.txt)
  finish_step 9 "km3's coverage baselines: B2e's 80 pairings without Ariados 40,000, Scizor 4,000, v-lucario_2, v-suicune_2 and v-weezing_2 3,500 each, l-charizardy 4,000: 66,500 games played, 58,500 equal to km_tables_2026-09-30's 1f6319e references on every field (identity_9.txt); the 16 named pairings (32-39 h-whimsicott, 80-87 deck 12): watch equal to plain on 8,000; $SUM (touched_9.txt; every changed game in handoff_8c.tsv for 8c)"
fi

# ---- Step 10: the command line, goldfish, the screen.
if step_is_done 10; then STEP=10; skip_done 10
else
  begin_step 10 "deckgym simulate (5 x 240 games), goldfish --coverage, run_screen under km3 on brew-06 and 06b (3,840 games)"
  mapfile -t RS < <(ls "$R/decks/research")
  [ "${RS[0]:-}" = altaria.txt ] && [ "${RS[1]:-}" = blaziken.txt ] \
    || halt "decks/research's first two lists are not altaria.txt and blaziken.txt (the reference command took the first two)"
  : > "$O/identity_10.txt"
  for CODE in "${CLI_CODES[@]}"; do
    WANT=$(run_record "$GYM" "$R" simulate --num 240 --players "$CODE,$CODE" --seed 7100 --seed-stream -p "$CLI_P0" "$CLI_P1")
    PLAY_FN=play_cli; OUT_GAMES=240
    out_run "cli $CODE" "${S}_10_cli_$CODE" "$WANT" cli_compare "$CODE" "$O/${S}_10_cli_$CODE.txt" "$B/ref2/$E30/14c39f4_cli_$CODE.txt"
    STEP_FILES+=("${S}_10_cli_$CODE.txt" "${S}_10_cli_$CODE.run")
  done
  WANT=$(run_record "$GOLD" "$B/engine" --deck "$R/$CLI_P0" --panel "$R/decks/screen/opponents" --games 0 --coverage "${S}_10_goldfish_coverage.json")
  PLAY_FN=play_goldfish; OUT_GAMES=0
  out_run "goldfish" "${S}_10_goldfish" "$WANT" gold_compare
  STEP_FILES+=("${S}_10_goldfish.txt" "${S}_10_goldfish.run" "${S}_10_goldfish_coverage.json")
  SARGS=("$BREW06" "$BREW06B" --games 240 --pilot km3 --meta-pilot km3 --seed 7100)
  for f in "$BREW06" "$BREW06B"; do [ -f "$R/$f" ] || halt "$f is missing"; done
  WANT=$(run_record "$GYM" "$R" "run_screen.py=$(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-64)" \
    "screen_with.py=$(sha256sum < "$SW" | cut -c1-64)" "${SARGS[@]}")
  PLAY_FN=play_screen; OUT_GAMES=3840
  out_run "run_screen" "${S}_10_run_screen" "$WANT" screen_compare
  STEP_FILES+=("${S}_10_run_screen.txt" "${S}_10_run_screen.run" identity_10.txt)
  pin_note "step 10's run_screen used decks/screen/run_screen.py sha256 $(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-64) (its reference, floor_recheck_2026-09-30/run_screen.txt sha256 c66b656b69e8620f..., was made with run_screen.py 4f102352; the current one's docstring says the output is unchanged without --weights)"
  finish_step 10 "deckgym simulate: k3 150/90/0, kp3 144/96/0, kog3 149/91/0, and kta3 and km3 equal to 14c39f4_cli_*.txt (every line but the wall time); goldfish --coverage byte-equal to 14c39f4_goldfish*; run_screen under km3 on brew-06 and 06b equal to floor_recheck_2026-09-30/run_screen.txt (identity_10.txt)"
fi

# ---- 8c's gate again: when step 8 waited after 8b, it runs now if the gate passes and it fits before the deadline.
if ! step_is_done 8; then
  STEP=8c; gate_8c
  [ -n "$GATE_WHY" ] || run_step8
fi

# ---- Done, or paused for 8c's trace load.
STEP=done
if step_is_done 8; then
  x=$(grep "^STEP 8 DONE $S " "$O/STATUS.txt" | tail -n 1 | grep -o 'the real trace load before 8c: .*' | sed 's/ (touched_8.txt.*$//' || true)
  pin_note "every check of sitting 2 passed for $C: 8b (2,800 games; the cloud's rows 32-37 equal to the cloud's own at P), the carriers and the Will rows (54,750), watch equal to new throughout and every deal the same deal on the three sides (their changed games go to 8c: handoff_8c.tsv); km3's coverage (74,500: B2e's 80 pairings without Ariados, Scizor and the second lists equal; the 16 named pairings' changed games in handoff_8c.tsv); the command line, goldfish and the screen (5,040). Step 8: ${x:-see its STEP line}. REPLAYS DONE (PLAN.md steps 7-10: sitting 1's 7, 7b, 7c and sitting 2's 8b, 8, 9, 10); the prepare-done mark is not this runner's to write: it waits for 8c's traces and, on any judgment call, Dustin's word. This start played $PLAYED games and reused $REUSED."
  state_line "SITTING 2 DONE $C $(ts): step 8, ${x:-see its STEP line}"
else
  state_line "SITTING 2 PAUSED $(ts) ${S:-?}: step 8 waits for 8c's trace load (trace_load.txt; read after 8b and again after step 10): $GATE_WHY; steps done: $(done_list)(committed). Once trace_load.txt holds 'TRACE LOAD <n> <the cloud commit>' (and a DUSTIN line when n > 50) and is committed, a plain start runs step 8 only"
  FINISHED=1; RECORD=1; exit 3
fi
FINISHED=1; RECORD=1
}
main "$@"; exit
