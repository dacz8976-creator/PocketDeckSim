#!/usr/bin/env bash
# Rules switch 2, sitting 1: PLAN.md steps 4-7c (rl/results/engine_switch_rules2_2026-10/PLAN.md, section 5; its section 0,
# the Oct 8 update, wins over sections 1-9). The copy of Oct 1's ../engine_switch_rules_2026-10/sitting1.sh, adapted, not
# rewritten (PLAN.md section 5), as the laptop session's ADAPTATION_SPEC.md (items S1-1 to S1-31, Oct 9) says. Dustin, Oct 9
# (PLAN.md lines 24-29; RELEASE_PACKAGE.md): "1-3 sure" (the go, "update if everything passes", with the two stricter
# checks; the scope; the new reference games) and "Alright it is fine to use the laptop over the weekend"; the school-morning
# rule applies on Monday Oct 12 (no new game after 5:15 am Central); the pin still waits for his word on any judgment call.
# Sitting 1 makes the candidate, the two builds, and the replays and counters that need no carrier list. Nothing is pinned
# and the manifest is not touched. The shared working copy is never checked out, switched, stashed or reset, and no engine
# file is edited: the candidate is made with git merge-tree, commit-tree and update-ref, and the checkpoint commits come from
# a private index (checkpoint.sh, Oct 1's, a byte copy). A checkpoint commit and push after every step.
#
# What was adapted from Oct 1's copy (with the ADAPTATION_SPEC.md items):
# - P, the round-2 package's final engine commit on origin/claude/coin-prevention-round2, taken by commit, not by branch
#   head, replaces R (f8cfa9c) and its cae37a3 / c9df626 / F1-F7 checks; main's engine/ is still the official engine's
#   (main-8626a35, tree 38af8b0), and P stacks on it (S1-4, S1-13 to S1-15).
# - The fixed names are read from this folder's data files (switch2.env, allowed_engine_files.tsv, engine_commits.tsv,
#   counters.tsv, floor_7c.tsv; a regex read, never sourced) and checked against git; the fixed ones must also be the values
#   this runner was written for. A start refuses while a value or file it needs is marked TO FINALIZE (P had not landed when
#   this was written); the dry run notes them and goes on (S1-3).
# - Step 4's file list is a data file with each file's status (26 files at 31616338, an added test among them, so a status
#   other than M is no longer refused by itself), and Cargo.toml joins Cargo.lock and players/ as unchanged; P's files under
#   this folder must not clash with this folder's (S1-13, S1-15; ADAPTATION_SPEC.md 1.10).
# - Precondition (g), the suite at P, is checked at the start (SUITE_AT_P) (S1-16).
# - The old programs are rl/engine-2026-10-02/ (main-8626a35) (S1-6).
# - Step 6's coin script is P's blob (b7e3bc00's, with P2's counters; PLAN.md step 6's "da08620's version" predates it),
#   and the watch build must write all 42 counters of counters.tsv (S1-5, S1-24).
# - Step 7b: round 2's exact counters 0 on the table, the three named off-gate counters above 0 somewhere, the others
#   reported (S1-26).
# - Step 7c: Oct 1's four pages and 32 rows as before, deck 10's page (its t-weezing row reported), draft D's root page (from
#   the 9cc6667 blob, copied here) and amended page, and 24 new watch rows on the 23,300,000,000 block; the replay-on-the-old-
#   engine rule; deck 10 v t-weezing's changed games go to 8c (S1-7, S1-9, S1-21 to S1-23, S1-27 to S1-30).
# - The deadline defaults to the next weekday 10:15 UTC (5:15 am CDT), the hard stop to the deadline itself, the push-by to
#   12:00 UTC (7:00 am CDT); a daytime start is allowed (ALLOW_DAYTIME); a start refuses beside another game run (BUSY_OK) or
#   with any DECKGYM_* variable set; PAUSED exits 3, so a chain sitting1.sh && sitting2.sh stops there; it runs under
#   rl/strength/launch_detached.sh (S1-10, S1-11, S1-17, S1-18; ADAPTATION_SPEC.md 1.3-1.5, 1.8, 1.9).
#
#   4  The candidate (no game). After a fetch (at most 5 min; offline, the local objects): the merge of main's HEAD and P
#      (switch2.env), made without the working copy: git merge-tree --write-tree (a conflict halts), git commit-tree with
#      parents main and P and the final merge message, kept at refs/pocketdecksim/rules-switch2-candidate (not a branch:
#      GitHub Desktop does not list it, a push does not send it) and recorded in candidate.txt (made once; a later start
#      checks it and never remakes it). Checks, git only:
#      - P is on origin/claude/coin-prevention-round2, its engine/ is P_TREE, and it stacks on the official engine 8626a35;
#        the commits that touch engine/ between 8626a35 and P are exactly engine_commits.tsv's, each of its kind (tests
#        first: only engine/tests/ under engine/, each in the file list; src: engine/src/; merge: two parents; none of the
#        others touches anything outside engine/ and rl/results/); git diff --name-status 8626a35 P -- engine/ is exactly
#        allowed_engine_files.tsv (paths and statuses); players/, Cargo.lock and Cargo.toml unchanged;
#      - main's engine/ is the official engine's source (tree 38af8b0, main-8626a35's; PLAN.md section 0);
#      - the candidate's engine/ is P's tree byte for byte (so the suite at P counts: precondition (g));
#      - outside rl/results/ the candidate changes exactly allowed_engine_files.tsv's files, each with its listed status;
#      - engine/src/players/, every Cargo.lock and every Cargo.toml unchanged; nothing deleted anywhere;
#      - both watch scripts in the candidate are P's blobs (switch2.env names them);
#      - P's files under this folder (early_warning_8b/, tightened_rule.py, ...) clash with none of main's or the working
#        copy's (else the merge here and at the pin would conflict).
#   5  The plain build (no game; Oct 1's took about 10 min): one git archive of the candidate (engine/ and decks/) into
#      /home/dacz8976/engine-rules2-<short>; cargo build --release --locked of deckgym, examples/legality_scan and
#      examples/goldfish (CARGO_TARGET_DIR unset: the target folder is in the build folder, on the WSL disk). Their sha256
#      and the pinned old programs' (rl/engine-2026-10-02/, which must equal its SHA256SUMS and the manifest's available
#      release, main-8626a35) go to programs.sha256 and PIN_STATUS.txt, checked before and after every later step (a program
#      that differs halts); a build is never redone after step 5 passed. The references are taken from the candidate (git
#      cat-file, blob-checked) into <build>/ref (<short>_refs.sha256): step 7's 15, each with the sha256 recorded when it
#      was played or adopted (REF7 below), and floor_7c.tsv's 7 pages' 21 files, each the blob at its page's commit (4690810
#      for the five Sept 30 pages, 99cdec0c for draft D's root page, 19c77835 for D amended). The inputs the games read are
#      recorded (<short>_inputs.sha256): each inside the repository must be the candidate's file; floor.py must be one every
#      page allows (floor_7c.tsv: the blob the page was made with, or today's, which differs from the older one only in the
#      pinned ATTACKERS diff and names none of those pages' decks).
#   6  The watch build (no game): a second git archive of the candidate in its own folder, /home/dacz8976/engine-rules2-
#      watch-<short>; both instrument_scan.py scripts (taken from the candidate, blob-checked against switch2.env and P:
#      Victory Star's cd8fe70b, then the coin script at P) applied to its examples/legality_scan.rs; its source must differ
#      from the plain build's in that one file; it must write all 42 counters of counters.tsv, and the coin script's round-2
#      lists must be counters.tsv's round-2 rows; cargo build --release --locked --example legality_scan. Its sha256 in
#      watch.sha256 and PIN_STATUS.txt; watch_patch.txt says what was patched.
#   7  Identity for every pilot, PLAN.md step 7 exactly: the same files as Oct 1's step 7 (151,240 games), on the plain
#      legality_scan, each v the recorded games:
#        kta3 fresh  fresh_table28.tsv, pairings 0-27, i < 500, seeds 23,000,000,000 + 10,000 x pairing + i
#                      v kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl (14,000)
#                    fresh_new_decks.tsv, 8-24, i < 500, 23,001,000,000 + ...   v .../ec7e1a8_fresh_kta3_new17 (8,500)
#        kta3 dev    --decks, 0-27, i < 500, 72,000,000 + ...          v kt_tables_2026-09-28/ec7e1a8_kta3_table (14,000)
#                    new_decks.tsv, 8-24, i < 500, 21,108,000,000 + ... v kt_tables_2026-09-28/ec7e1a8_kta3_new17 (8,500)
#        km3         the same development deals              v km_tables_2026-09-30/1f6319e_km3_{table,new17}
#        k3, kp3     the same development deals              v kpf_2026-09-26/reading/{table,new17}_{k3,kp3}
#        kog3        the same development deals              v kog_2026-09-27/a823b6d_kog3_500, kog_composition_2026-09-27/new17_kog3
#        kq3         --decks, 0-27, i < 500                  v kt_2026-09-26/identity/official_kq3_500 (14,000)
#        kpr3        --decks, 0-27, i < 40                   v kpf_2026-09-26/reading/table_kpr3, i < 40 (1,120)
#        kd3         --decks, 0-27, i < 40, a gate (kd's follow-ons stay out of table games)
#                                                            v kt_2026-09-26/identity/43cef0b_kd3_40 (1,120)
#      k3's and kp3's are scoreboard v3's frozen 45 cells (their four files must have frozen_summary.json's sha256):
#      identical games mean those files already are the new engine's table. One line per file in identity_7.txt.
#   7b The table's counters (28,000 games): the watch build plays k3 and kp3 on the 28 cells (--decks, i < 500). Every
#      watch game must equal step 7's plain game on every field the plain build records, and must add exactly counters.tsv's
#      names to the plain record; round 2's exact counters (counters.tsv's role reach2; any key of a keyed one) must read 0
#      in every game; each of offgate_plain_attack_damage, offgate_by_attack (the first round's helpers and Chase Order's
#      discard) and offgate_confused_attack must be above 0 in at least one game; every other counter is reported, with a
#      NOTE when one of round 1's is above 0 (PLAN.md step 7b). counters_7b.txt.
#   7c-seeds (no game; its own STEP line, as on Oct 1, inside step 7c): Oct 1's pairs_7c.tsv checked in place (blob
#      d747cf5f); pairs_7c2.tsv and seeds_7c2.txt written (sitting1_check.py pairs7c2: 23,300,000,000 + pairing x 10,000 +
#      i, pairings 0-23, i < 60: deck 10 0-7, draft D's first list 8-15, D amended 16-23, each v the 8 sorted panel lists, so
#      deck 10 v t-weezing is pairing 7); D's first list copied byte for byte from the 9cc6667 blob (b15acdd1, sha256
#      4821877f) to floor_7c/d_first/ (its basename kept: floor.py names the page by it); <short>_inputs7c.sha256 (that copy,
#      the pages' decks, the panel, floor.py); floor_7c/NOTE.txt; committed (and pushed when the network allows) before any
#      7c game.
#   7c Dustin's lists where rewritten lines run (20,160 games; PLAN.md step 7c):
#      - plain: each page of floor_7c.tsv (02, 06, 08, 14 and 10 at 4690810; D's root page; D amended) replayed by floor.py's
#        own call (deckgym simulate --seed-stream, its own seeds, the recorded runs' environment: no RAYON_NUM_THREADS) on the
#        new deckgym through floor_with.py, into floor_7c/<page>/: every game equal on every field of floor.py's per-game
#        summary record, the coverage byte-equal, the page equal but for its program and its coverage program (the Sept 30
#        pages name rl/engine-2026-09-30/goldfish; the replay's coverage comes from the manifest's, rl/engine-2026-10-02/'s).
#        Deck 10's games against t-weezing may differ (Will with a Confused Xatu): counted and reported, "a new page in step
#        15", never a stop. On D's two pages only Victini's caveat may differ, in the coverage's limitations and the page's
#        engine cell (expected equal: the coverage comes from the old goldfish; the new caveat shows on step 15's pages).
#        A page that does not pass is first played again on the old deckgym (rl/engine-2026-10-02/, into
#        floor_7c/<page>/oldengine/) and that is compared with the recorded page too: "the difference predates switch 2" or
#        "it comes with switch 2", in identity_7c.txt. It still halts (PLAN.md step 7c).
#      - watch, Oct 1's 32 rows (decks 02/06/08/14 v the 8 panel lists, km3 v km3, i < 60; ../engine_switch_rules_2026-10/
#        pairs_7c.tsv in place, 23,100,000,000 + pairing x 10,000 + i, pairings 40-71): the watch legality_scan and the old
#        one on the same seeds, identical on every field the old one records; as on Oct 1 ("every repair counter 0"), by
#        purpose: round 2's exact and superset counters (reach2, superset2; any key of a keyed one) and round 1's (r1_exact,
#        r1_heads, r1_superset) 0 in every game; offgate_helper_choice and round 2's offgate_by_attack (it fires for the
#        same helpers, whose constructor round 2 rewrote) above 0 in at least one game of OFFGATE7C (02, 06 and 08 against
#        t-altaria, t-hydreigon and t-weezing, where only Dustin's Absol, Heatmor or Gabite fire them); the rest reported.
#      - watch, the 24 new rows (pairs_7c2.tsv): the watch and the old legality_scan; the 23 rows named equal identical on
#        every field the old one records (1,380 deals); deck 10 v t-weezing (pairing 7, a named row: PLAN.md section 6)
#        through sitting2_check.py touched (the watch build as the new side: 7b showed watch = plain): its changed games go to
#        8c (handoff_7c_km3.tsv, touched_7c.txt), never a stop here; offgate_vs_ungated_built above 0 in at least one game of
#        D's rows (8-23); offgate_confused_attack reported on deck 10's (0-7), not required there.
#      Lines in identity_7c.txt, counters_7c.txt and touched_7c.txt. The STEP line carries "changed <N> of 60 deals" once,
#      for pairing 7 (the pin sums those phrases), and deck 10's t-weezing floor line.
#   Then "SITTING 1 DONE <candidate> <time>". identity_check.txt is identity_7.txt + identity_7c.txt, table_counters.txt is
#   counters_7b.txt + counters_7c.txt and touched_check.txt is touched_7c.txt, rebuilt at every checkpoint (sitting 2 adds
#   its own). Sitting 2 (steps 8b-10) is a separate script; it takes the builds and the candidate from candidate.txt,
#   programs.sha256 and watch.sha256.
#   Games: 151,240 + 28,000 + 20,160 = 199,400 (PLAN.md section 3: "about 199,000").
# Identity (7, 7b, 7c): games matched by (pairing, i), counts asserted (both files hold exactly the expected deals, once
# each), every field the reference records equal (switch_check.py same: moves, decisions, openings, winner_seat, points,
# seed, first_seat, bot_a, bot_b, a, b, a_file, b_file, turns, first_deck_score and the per-game counters); every game is
# the one the command plays (switch_check.py complete); every scan page is free of RULE findings. The checks run from a
# private copy of switch_check.py, sitting1_check.py, sitting2_check.py, floor_with.py, checkpoint.sh and counters.tsv made
# at each start (in /tmp, removed at the end); the sha256 of sitting1.sh, of each copy and of each data file is in the START
# line. Every start refuses unless sitting1.sh, its helpers and the data files are committed and unchanged (so the evidence
# names committed code).
#
# STATUS.txt: a timestamped note per action and these anchored lines, at column 0:
#   SITTING 1 START <time> <short>: ...                   every start
#   STEP <n> DONE <short> <time> <summary>                 a step passed (n = 4, 5, 6, 7, 7b, 7c-seeds, 7c); then its checkpoint
#   SITTING 1 HALT <time> <short>: step <n>: <why>        a check failed: an identity difference in a row named equal, a
#                                                          missing or extra game, a counter, watch not equal to plain, a RULE
#                                                          finding, a program crash (any exit but a stop signal's), a
#                                                          candidate check, a program, reference, input or evidence file that
#                                                          differs from its record. Nothing later runs. A later start refuses
#                                                          until SITTING1_AFTER_HALT='<written reason>' is set (it is noted).
#                                                          Exit 1.
#   SITTING 1 STOPPED <time> <short>: step <n>: <why>     the script could not carry on (a build, fetch, git or checkpoint
#                                                          failure, a push it may not make, a stop signal, the watchdog's
#                                                          hard stop): not a result; a plain restart resumes at that step.
#                                                          It ends with the untracked files left in this folder. Exit 1.
#   SITTING 1 PAUSED <time> <short>: before step <n>: ... the next step could not finish before the deadline, so it was
#                                                          not started; a plain start (the next evening) resumes there. Exit 3.
#   SITTING 1 DONE <candidate> <time>                      every step passed. Exit 0 (and 0 for a start that finds it DONE).
#   HALT, STOPPED, PAUSED and DONE also go to PIN_STATUS.txt; the last line matching ^SITTING 1 (HALT|STOPPED|PAUSED|DONE)
#   is the run's state. These lines never carry the words FAILED or MISMATCH (pin.sh's convention).
#   SITTING 1 NOT PUSHED <time> <short>: <why>            after the record commit, when it could not be made or pushed
#                                                          (left uncommitted; the next start's first checkpoint commits it):
#                                                          main is not origin/main, and a person has to see to it by 7:00 am.
#   A start refused (with what to do, on stderr; nothing recorded) exits 2.
# Checkpoints (checkpoint.sh): after each step passes, its STEP DONE line and its files are committed to main (only this
# folder's paths, from a private index; main moves only if it is where the commit was built) and pushed (fast-forward
# only, after a fetch). Each step's files are listed with their sha256 in step_<n>.sha256 (committed); a later start
# skips a DONE step after checking those, and every checkpoint checks every DONE step's files again before it commits
# them, so a cut loses at most the step in progress. Within that step, a game file completed earlier (synced to disk before
# its .run record names the same program and command) is reused and checked again; a kept file that is no longer intact (a
# power-off?) is moved aside as <name>.*.broken_<stamp> and played again, never a halt. A HALT, STOPPED, PAUSED or DONE
# line is committed and pushed too (STATUS.txt, PIN_STATUS.txt, the timings, the check files and, on a HALT, the halted
# step's files so far; best effort, and a "SITTING 1 NOT PUSHED" line when it could not be). The push rules (Dustin: main =
# origin/main by 7:00 am on a morning he takes the laptop, and this run pushes only its own commits):
# - a push is only a fast-forward of origin/main, and only of commits this run made (.sitting1.ours) or that the start
#   allowed (unpushed commits that touch only this folder and START_HERE.md: the runner's own);
# - origin/main with commits main lacks, or main carrying another session's unpushed commit (still there a minute
#   later), stops the run (SITTING 1 STOPPED, with what to do): it is never forced, merged or pushed along;
# - an offline fetch or push is noted, the games go on, and the next checkpoint pushes again;
# - past the deadline, a checkpoint's fetch and push get at most a quarter of the time left until PUSH_BY.
# The deadline: DEADLINE (default school: the first Monday-Friday 10:15 UTC, 5:15 am CDT, after the start; a start on
# Saturday or Sunday gets Monday's; PLAN.md line 28: no new game after 5:15 am Central on a school day). Before each step
# the time it needs is estimated: its games still to play / the measured rate (all games timed so far in timing.tsv, or
# RATE before 2,000 have been) x SAFETY, plus OVERHEAD_MIN; for the builds EST5_MIN and EST6_MIN. A step that would end
# after the deadline is not started: "SITTING 1 PAUSED", committed and pushed, and the run ends (exit 3). A watchdog backs
# that up: at HARD_STOP (default the deadline itself: a step still going at 5:15 stops cleanly) it stops the run's process
# group, outside a checkpoint, with SITTING 1 STOPPED, committed and pushed by PUSH_BY (also after a laptop sleep: it reads
# the clock every 20 s); a plain start resumes it. A daytime start (11:30-21:00 UTC, without an explicit DEADLINE) is allowed
# on Saturday and Sunday and refused Monday-Friday (ALLOW_DAYTIME=auto, the default: Dustin's word covers the weekend, and a
# weekday is class and travel, so a stopped run resumes Monday evening, PLAN.md line 28); ALLOW_DAYTIME=1 allows it any day,
# and ALLOW_DAYTIME=0 refuses it any day, as on Oct 1.
# One run at a time: flock on .sitting1.lock (fd 9; the children inherit it, git calls close it).
# Every start refuses (exit 2, with what to do) when: sitting1.sh, a helper or a data file is not committed as it is here;
# a data file is malformed, or a value or file it needs is still marked TO FINALIZE; the helpers lack an option this runner
# calls; the working copy is not on main; sitting2.sh holds .sitting2.lock; the committed START_HERE.md has no seed-table
# line holding 23,300,000,000 and 36–37, or its 23,100,000,000 row does not hold 36–37 (the two rows drafted in the laptop
# session's seed_row_23_3B.md); a DECKGYM_* variable, PDL_EQUIV_DEALS or GOLDFISH_TRACE is set; another game program or
# long run is going (legality_scan, deckgym, goldfish, cargo, rustc, tool_census or strength outside this run's group; a
# process of a run $HOME/runs/watch.list names, its PATTERN or CHAIN; another live launch_detached run, a run_watch.sh
# watcher aside; unless BUSY_OK=1); a git lock file (.git/index.lock, .git/refs/heads/main.lock) stays for 15 s; files in
# this folder are staged in the shared index and differ from the working copy (staged entries equal to it, which an
# interrupted checkpoint leaves, are unstaged and noted); origin/main (after a fetch of at most 2 min) has commits main
# lacks; main carries unpushed commits that are not this switch's; precondition (g) is not met (SUITE_AT_P: the suite log
# at its commit names P and holds no failure); on a fresh start (no candidate yet), one of step 4's git checks fails on the
# merge tree (a data file or value that does not match git: refused, not a HALT); the last run halted
# (SITTING1_AFTER_HALT); it is daytime and ALLOW_DAYTIME refuses it (above). The flags a power-off can leave
# (.sitting1.ckpt, .sitting1.hardstop) are removed once the lock is held. Before each checkpoint commit (and the record
# commit) a bounded fetch: when origin/main has commits main lacks, nothing is committed and the run stops (SITTING 1
# STOPPED; the record is left uncommitted with a NOT PUSHED line), so main never needs a merge (sitting2.sh's Oct 1 fix).
# Files written outside this folder: the build folders /home/dacz8976/engine-rules2-<short> and engine-rules2-watch-<short>,
# the private copies in /tmp, the candidate commit and its ref (once), the objects git merge-tree writes, the checkpoint
# commits on main (pushed), and the shared index's entries for exactly the committed paths (checkpoint.sh; pin.sh does
# the same, and ../engine_switch_rules_2026-10/README.md records this exception).
#
# Usage (WSL), after sitting1.sh, its helpers and the data files are committed (every long laptop run starts this way;
# rl/strength/launch_detached.sh gives it its own session and process group, stdin closed, the log $HOME/runs/<name>.log):
#   bash rl/strength/launch_detached.sh start rules2-sitting1 --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/sitting1.sh"
#   bash rl/strength/launch_detached.sh start rules2-sitting2 --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/sitting2.sh"
#   # or both in one: -- bash -c 'bash ".../sitting1.sh" && bash ".../sitting2.sh"'   (exit 3 = PAUSED stops the chain; keep
#   # the chain a bash -c line naming both scripts, so quiet.sh still recognises the group's leader)
#   bash rl/strength/launch_detached.sh stop rules2-sitting1    the way to stop it (TERM to the group: SITTING 1 STOPPED)
#   bash sitting1.sh --dry-run   git checks only: no fetch, build, game, commit or ref (git merge-tree's tree objects
#                                aside), a scratch copy of legality_scan.rs patched in /tmp, the pairs files written in
#                                /tmp, and git push --dry-run (no write) to see that a checkpoint can push
#   bash quiet.sh pause|resume|stop|status    for this run's process group (.sitting1.pgid names the group's leader)
#   Started plainly (bash sitting1.sh, not under launch_detached), it re-executes itself under setsid when it does not lead
#   its own process group, as on Oct 1. A stop or a WSL restart is resumed by starting it again the same way.
# Knobs (environment): THREADS 14, NICE 10, JOBS 14 (cargo), DEADLINE school (school = the next Monday-Friday SCHOOL_CUT
#   UTC; HH:MM UTC, the next one; an ISO time; or off), SCHOOL_CUT 10:15, HARD_STOP auto (the deadline itself; HH:MM UTC, an
#   ISO time, or off), PUSH_BY auto (the deadline + 105 min, 12:00 UTC = 7:00 am CDT for 10:15; HH:MM UTC, an ISO time, or
#   off), ALLOW_DAYTIME auto (above; 1 or 0), BUSY_OK 0, RATE 8.6 (games a second before any is measured), SAFETY 1.25, OVERHEAD_MIN 10, EST5_MIN
#   40, EST6_MIN 25, SITTING1_AFTER_HALT (above). An input file that changes after step 5 halts (there is no renewal knob: a
#   changed input would not be the candidate's file anyway).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules2_2026-10
OLDREL=rl/results/engine_switch_rules_2026-10   # Oct 1's switch: read only (its pairs_7c.tsv is replayed in place)
O="$R/$REL"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[ "$HERE" -ef "$O" ] || { echo "sitting1.sh: run the copy in $O (this one is in $HERE)" >&2; exit 2; }
DRY=0
case "${1:-}" in "") ;; --dry-run) DRY=1;; *) echo "usage: bash sitting1.sh [--dry-run]" >&2; exit 2;; esac
# Its own process group (quiet.sh and the watchdog act on it). Under launch_detached (LAUNCH_DETACHED_RUN set) the run already
# has its own session and group, and leaving them would put it out of reach of launch_detached.sh stop: no re-exec there.
if [ $DRY -eq 0 ] && [ -z "${SITTING1_REEXEC:-}" ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ] \
   && [ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]; then
  SITTING1_REEXEC=1 exec setsid bash "$O/sitting1.sh" "$@"
fi

# ---- The data files (committed in this folder; read with a regex, never sourced; checked against git at every start and by
# the dry run). A value TO_FINALIZE, or a file whose first line starts "# TO FINALIZE", is not final: a start refuses while
# one this sitting needs carries it; the dry run notes it and goes on.
DATAFILES=(switch2.env allowed_engine_files.tsv engine_commits.tsv counters.tsv floor_7c.tsv)
DATA_ERR=""; MARKED=()
declare -gA ENV2=()
ENV_RE='^([A-Z0-9_]+)=([^ ]*)$'
HEX40='^[0-9a-f]{40}$'; HEX64='^[0-9a-f]{64}$'; SUITE_RE='^[0-9a-f]{7,40}:[^ ]+$'
load_env() {  # switch2.env into ENV2: KEY=VALUE lines, # comments and blank lines; anything else is a DATA_ERR
  local line n=0 k
  [ -f "$O/switch2.env" ] || { DATA_ERR+="switch2.env is missing; "; return 0; }
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1)); line=${line%$'\r'}
    case $line in ''|'#'*) continue;; esac
    if [[ $line =~ $ENV_RE ]]; then
      k=${BASH_REMATCH[1]}
      [ -z "${ENV2[$k]+x}" ] || DATA_ERR+="switch2.env line $n sets $k a second time; "
      ENV2[$k]=${BASH_REMATCH[2]}
    else DATA_ERR+="switch2.env line $n is not KEY=VALUE (no spaces, no quotes): ${line:0:60}; "; fi
  done < "$O/switch2.env"
}
getv() {  # var key [needed]: var = switch2.env's value of key; a needed key may be TO_FINALIZE (then MARKED), a fixed one may not
  local val=""
  if [ -n "${ENV2[$2]+x}" ]; then val=${ENV2[$2]}; else DATA_ERR+="switch2.env has no $2; "; fi
  if [ "$val" = TO_FINALIZE ]; then
    if [ "${3:-}" = needed ]; then MARKED+=("switch2.env: $2"); else DATA_ERR+="switch2.env: $2 is TO_FINALIZE, but it is a fixed value; "; fi
  fi
  printf -v "$1" '%s' "$val"
}
fixed() {  # var key want: a fixed value; it must also be the one this runner was written for (checked, not trusted)
  getv "$1" "$2"
  [ "${!1}" = "$3" ] || DATA_ERR+="switch2.env: $2 is '${!1}', not $3, the value sitting1.sh was written for (if it really changed, sitting1.sh changes with it); "
}
tsv_rows() {  # file header arrayname: the array gets the rows after the header (comment and blank lines skipped)
  local _f=$1 _want=$2 _line _hdr=""
  local -n _rows=$3
  _rows=()
  [ -f "$_f" ] || { DATA_ERR+="${_f##*/} is missing; "; return 0; }
  while IFS= read -r _line || [ -n "$_line" ]; do
    _line=${_line%$'\r'}
    case $_line in ''|'#'*) continue;; esac
    if [ -z "$_hdr" ]; then
      _hdr=$_line
      [ "$_hdr" = "$_want" ] || { DATA_ERR+="${_f##*/}: the header is not '${_want//$'\t'/ }' (tab-separated); "; return 0; }
      continue
    fi
    _rows+=("$_line")
  done < "$_f"
  [ -n "$_hdr" ] || DATA_ERR+="${_f##*/} has no header; "
}
is_marked() { local l=""; [ -f "$1" ] || return 1; IFS= read -r l < "$1" || true; [[ $l == '# TO FINALIZE'* ]]; }
data_sums() {  # dir: "file sha256-16, ..." of the data files there
  local f s=""
  for f in "${DATAFILES[@]}"; do [ ! -f "$1/$f" ] || s+="$f $(sha256sum < "$1/$f" | cut -c1-16), "; done
  printf '%s' "${s%, }"
}
load_env
getv P P needed; getv P_TREE P_TREE needed; getv COIN_SCRIPT_BLOB COIN_SCRIPT_BLOB needed; getv SUITE_AT_P SUITE_AT_P needed
fixed P_BRANCH P_BRANCH origin/claude/coin-prevention-round2
fixed OFFICIAL OFFICIAL 8626a35861b88ae86a70c2386d47f9d765cfa2bc        # the official engine (main-8626a35), the old side
fixed MAIN_ENGINE OFFICIAL_TREE 38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5  # its engine/, still main's (PLAN.md section 0)
fixed OLD_NAME OLD_RELEASE_NAME main-8626a35
fixed OLD_DIR OLD_DIR rl/engine-2026-10-02
fixed OLD_GYM_SHA OLD_DECKGYM_SHA256 2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
fixed OLD_SCAN_SHA OLD_LEGALITY_SCAN_SHA256 978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699
fixed OLD_GOLD_SHA OLD_GOLDFISH_SHA256 cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
fixed CREF CREF refs/pocketdecksim/rules-switch2-candidate   # not a branch (Oct 1's rules-switch-candidate stays as it is)
fixed VS_SCRIPT VS_SCRIPT rl/results/victory_star_repair_2026-09-30/instrument_scan.py
fixed VS_SCRIPT_BLOB VS_SCRIPT_BLOB cd8fe70b291b9d5258a384bca444379a71601bb5
fixed COIN_SCRIPT COIN_SCRIPT rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py
fixed SEED7C SEED_OLD_BLOCK 23100000000
fixed SEED7C2 SEED_NEW_BLOCK 23300000000
fixed PAIRS7C_BLOB OLD_PAIRS_7C_BLOB d747cf5f38f740cad6425c74f5b921e65fef5589
fixed D_FIRST_COMMIT D_FIRST_COMMIT 9cc666761df5c2598457a41bfa400ce835bd975c
fixed D_FIRST_BLOB D_FIRST_BLOB b15acdd100cfd216d180ad12bd2da659a0226807
fixed D_FIRST_SHA D_FIRST_SHA256 4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585
for x in P P_TREE COIN_SCRIPT_BLOB; do
  [ "${!x}" = TO_FINALIZE ] || [[ ${!x} =~ $HEX40 ]] || DATA_ERR+="switch2.env: $x is not 40 hex characters; "
done
[ "$SUITE_AT_P" = TO_FINALIZE ] || [[ $SUITE_AT_P =~ $SUITE_RE ]] || DATA_ERR+="switch2.env: SUITE_AT_P is not <commit>:<path>; "
ROWS=()
ALLOWED=(); ALLOWED_ST=()   # step 4's engine files (PLAN.md step 4) and their statuses against 8626a35
tsv_rows "$O/allowed_engine_files.tsv" $'status\tpath' ROWS
for x in "${ROWS[@]}"; do
  IFS=$'\t' read -r st f rest <<< "$x"
  if [[ $st =~ ^[AM]$ && $f == engine/* && -z $rest ]]; then ALLOWED+=("$f"); ALLOWED_ST+=("$st")
  else DATA_ERR+="allowed_engine_files.tsv: the row '${x//$'\t'/ }' is not 'A|M<TAB>engine/<path>'; "; fi
done
[ ${#ROWS[@]} -eq 0 ] || [ ${#ALLOWED[@]} -gt 0 ] || DATA_ERR+="allowed_engine_files.tsv lists no file; "
ENGINE_COMMITS=(); ENGINE_KINDS=()   # the commits that touch engine/ between 8626a35 and P, each with its kind
tsv_rows "$O/engine_commits.tsv" $'commit\tkind\tsubject' ROWS
for x in "${ROWS[@]}"; do
  IFS=$'\t' read -r c k rest <<< "$x"
  if [[ $c =~ $HEX40 && $k =~ ^(tests|src|merge)$ ]]; then ENGINE_COMMITS+=("$c"); ENGINE_KINDS+=("$k")
  else DATA_ERR+="engine_commits.tsv: the row '${x:0:60}' is not '<40 hex><TAB>tests|src|merge<TAB><subject>'; "; fi
done
COUNTER_NAMES=()   # the watch build's counters (sitting1_check.py reads the rest of each row)
tsv_rows "$O/counters.tsv" $'name\tscript\tshape\trole\tmechanic\trevert_switch' ROWS
for x in "${ROWS[@]}"; do
  IFS=$'\t' read -r n rest <<< "$x"
  if [[ $n =~ ^[a-z0-9_]+$ ]]; then COUNTER_NAMES+=("$n"); else DATA_ERR+="counters.tsv: '${n:0:40}' is not a counter name; "; fi
done
FP_ID=(); FP_NAME=(); FP_REFDIR=(); FP_COMMIT=(); FP_DECK=(); FP_DECKBLOB=(); FP_MADE=(); FP_OK=(); FP_MODE=()   # step 7c's pages
tsv_rows "$O/floor_7c.tsv" $'page_id\tname\tref_dir\tref_commit\tdeck\tdeck_blob\tfloor_py_made\tfloor_py_ok\tmode' ROWS
for x in "${ROWS[@]}"; do
  IFS=$'\t' read -r a1 a2 a3 a4 a5 a6 a7 a8 a9 rest <<< "$x"
  if [[ $a1 =~ ^[A-Za-z0-9_]+$ && $a2 =~ ^[A-Za-z0-9._-]+$ && $a3 == rl/results/* && $a4 =~ $HEX40 && $a5 =~ ^[A-Za-z0-9._/-]+\.txt$ \
        && $a6 =~ $HEX40 && $a7 =~ $HEX64 && $a8 =~ ^[0-9a-f]{64}(,[0-9a-f]{64})*$ && -n $a9 && -z $rest ]]; then
    FP_ID+=("$a1"); FP_NAME+=("$a2"); FP_REFDIR+=("$a3"); FP_COMMIT+=("$a4"); FP_DECK+=("$a5"); FP_DECKBLOB+=("$a6")
    FP_MADE+=("$a7"); FP_OK+=("$a8"); FP_MODE+=("$a9")
  else DATA_ERR+="floor_7c.tsv: the row of page '${a1:-?}' is malformed; "; fi
done
FLOOR_PY_DIFF=""   # "<blob made with> <blob of today> <sha256 of git diff between them>"
if [ -f "$O/floor_7c.tsv" ]; then
  x=$(grep -m 1 '^# FLOOR_PY_DIFF' "$O/floor_7c.tsv" || true)
  IFS=$'\t' read -r a1 a2 a3 a4 rest <<< "$x"
  if [[ $a2 =~ $HEX40 && $a3 =~ $HEX40 && $a4 =~ $HEX64 ]]; then FLOOR_PY_DIFF="$a2 $a3 $a4"
  else DATA_ERR+="floor_7c.tsv has no line '# FLOOR_PY_DIFF<TAB><blob><TAB><blob><TAB><sha256>'; "; fi
fi
D_FIRST_PATH=decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt   # D's list (today's; its first version at 9cc6667)
D_COPY="$REL/floor_7c/d_first/draft-D-entei-grimhound.txt"               # the first version's copy (repository path)
if [ -f "$O/floor_7c.tsv" ] && [ "${FP_ID[*]}" != "02 06 08 14 10 D_root D_amended" ]; then
  DATA_ERR+="floor_7c.tsv's pages are '${FP_ID[*]}', not 02 06 08 14 10 D_root D_amended (PLAN.md step 7c); "
fi
for k in "${!FP_ID[@]}"; do
  case ${FP_ID[$k]} in
    D_root) [ "${FP_DECK[$k]}" = "$D_COPY" ] && [ "${FP_DECKBLOB[$k]}" = "$D_FIRST_BLOB" ] \
              || DATA_ERR+="floor_7c.tsv: D_root's deck is not $D_COPY, blob $D_FIRST_BLOB (D's first list); ";;
    *) case ${FP_DECK[$k]} in "$REL"/*) DATA_ERR+="floor_7c.tsv: page ${FP_ID[$k]}'s deck is in this folder; ";; esac;;
  esac
done
ALLOW_MARKED=0; COMMITS_MARKED=0; COUNTERS_MARKED=0
if is_marked "$O/allowed_engine_files.tsv"; then ALLOW_MARKED=1; MARKED+=(allowed_engine_files.tsv); fi
if is_marked "$O/engine_commits.tsv"; then COMMITS_MARKED=1; MARKED+=(engine_commits.tsv); fi
if is_marked "$O/counters.tsv"; then COUNTERS_MARKED=1; MARKED+=(counters.tsv); fi
if is_marked "$O/floor_7c.tsv"; then MARKED+=(floor_7c.tsv); fi
DATA_SUMS=$(data_sums "$O")

# ---- The fixed names (Dustin's decision; PLAN.md; the data files above).
OLDP="$R/$OLD_DIR"   # the pinned old programs (main-8626a35), as SHA256SUMS and the manifest record them
OLD_GYM="$OLDP/deckgym"; OLD_SCAN="$OLDP/legality_scan"; OLD_GOLD="$OLDP/goldfish"
OLD_SHA=("$OLD_GYM" "$OLD_GYM_SHA" "$OLD_SCAN" "$OLD_SCAN_SHA" "$OLD_GOLD" "$OLD_GOLD_SHA")
PFRESH_T=rl/results/kta_tables_2026-09-29/pairs/fresh_table28.tsv; PFRESH_N=rl/results/kta_tables_2026-09-29/pairs/fresh_new_decks.tsv
PDEV_N=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv
PAIRS7C="$OLDREL/pairs_7c.tsv"   # Oct 1's 32 rows, replayed in place (blob-checked), pairings 40-71 of 23,100,000,000
P7C=$(seq -s, 40 71)
# Where 7c's offgate_helper_choice must fire on Oct 1's rows: 02, 06 and 08 against t-altaria, t-hydreigon and t-weezing (the
# sorted panel's lists 0, 2 and 7), whose lists hold no attacker with a rewritten helper (HELPERS.md at 1abdbe8), so only
# Dustin's Absol, Heatmor or Gabite can fire it there (as on Oct 1).
OFFGATE7C=40,42,47,48,50,55,56,58,63
P7C2=$(seq -s, 0 23); D7C2=8-23; TWEEZ7C2=7   # the new rows (pairs_7c2.tsv, 23,300,000,000): D's rows; deck 10 v t-weezing
ALL28=$(seq -s, 0 27); N17=$(seq -s, 8 24)
# Step 7's references and the sha256 each had when its games were played or adopted (a rewrite of one halts; PLAN.md step 7:
# the same files as Oct 1's step 7):
REF7=(
 "rl/results/kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl|e3d7f4d71490aa2c074e21a7d3f3495912d3fa1d51d16ce77bc6bd96b51f7c5a|kta_tables_2026-09-29/ec7e1a8_fresh_skip_table.json"
 "rl/results/kta_tables_2026-09-29/ec7e1a8_fresh_kta3_new17.jsonl|b5216c940d4a3c680ba8bc67cf2c8097f458f7691d48963cbe9e3db5bfb6f3fa|kta_tables_2026-09-29/ec7e1a8_fresh_skip_new17.json"
 "rl/results/kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl|6b90d3cfa24e17815026dab7c787df327cfc859e491d1399889aaa2369a3c73b|trainer_pricing_2026-09-28/km_run/km_config.json"
 "rl/results/kt_tables_2026-09-28/ec7e1a8_kta3_new17.jsonl|1803e256e45d2d5a6208d61854067e88e05af51315cd4eefecda33c2f84603ba|trainer_pricing_2026-09-28/km_run/km_config.json"
 "rl/results/km_tables_2026-09-30/1f6319e_km3_table.jsonl|aff167ac8ca56054fdf1e971a17cb2071d7362e6ee964f5575263d4100b61712|km_tables_2026-09-30/1f6319e_skip_table.json"
 "rl/results/km_tables_2026-09-30/1f6319e_km3_new17.jsonl|8623d6f958ab46bd99ea6ff62389210521038cbc78b18273abc93dc1fd2339b2|km_tables_2026-09-30/1f6319e_skip_new17.json"
 "rl/results/kpf_2026-09-26/reading/table_k3.jsonl|2437ba5bd348e158f77d74173b4feaaff8775d15d80f32db76326553d227ecb7|scoreboard_v3_2026-09-27/frozen_summary.json"
 "rl/results/kpf_2026-09-26/reading/new17_k3.jsonl|fd530f306c207a8610626d962960c475bc95e4b00bcddea87743ce85e572dfae|scoreboard_v3_2026-09-27/frozen_summary.json"
 "rl/results/kpf_2026-09-26/reading/table_kp3.jsonl|788e57a6be3f98cbf8185c45cb0ffce6b87e1aa19a156f3da667acf80e17309f|scoreboard_v3_2026-09-27/frozen_summary.json"
 "rl/results/kpf_2026-09-26/reading/new17_kp3.jsonl|5da94f914aa07c0ef91fb3b5439e6a3ad4d9409ae225543c10c81d53f21afdf4|scoreboard_v3_2026-09-27/frozen_summary.json"
 "rl/results/kog_2026-09-27/a823b6d_kog3_500.jsonl|00e4ddc899325fc00116c0cfa688e62c651c4b2d4dd31f2049c21226f98fb27b|engine_switch_2026-09-30/14c39f4_refs.sha256"
 "rl/results/kog_composition_2026-09-27/new17_kog3.jsonl|76f69b5e98105c72928bfedf1ca391ad0a4f258b1033d87f1fcc5a5e3533120b|engine_switch_2026-09-30/14c39f4_refs.sha256"
 "rl/results/kt_2026-09-26/identity/official_kq3_500.jsonl|1ed6df323fe71501fc2fd0996d2fdbd0d4bb56dec5d2ea8aac0748b0e6bc9664|engine_switch_2026-09-30/14c39f4_refs.sha256"
 "rl/results/kpf_2026-09-26/reading/table_kpr3.jsonl|40e5b17d09e9b5802ce7ce1891d8b50c054312455f8de9b48d1bbcbca08db381|engine_switch_2026-09-30/14c39f4_refs.sha256"
 "rl/results/kt_2026-09-26/identity/43cef0b_kd3_40.jsonl|e36a40c350c70512da74b171aa19d7dd10c255121e6a44981fb65406d81e6404|engine_switch_2026-09-30/14c39f4_refs.sha256"
)
REFS=(); for x in "${REF7[@]}"; do REFS+=("${x%%|*}"); done
for k in "${!FP_ID[@]}"; do
  x="${FP_REFDIR[$k]}/${FP_NAME[$k]}"; REFS+=("${x}_games.jsonl" "${x}_coverage.json" "$x.md")
done
# Step 7, one scan per line: name|bot|pairings|deals|deals source|reference|max i|label. k3's and kp3's new-17 files run
# first: played Sept 27 at 9bffbda and never replayed but on Oct 1, a difference there shows after about 35 minutes.
SPEC7=(
 "new17_k3|k3|N17|500|DN|${REFS[7]}||7 k3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i; scoreboard v3)"
 "new17_kp3|kp3|N17|500|DN|${REFS[9]}||7 kp3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i; scoreboard v3)"
 "fresh_kta3_table|kta3|ALL28|500|FT|${REFS[0]}||7 kta3 fresh, the 28 table cells (fresh_table28.tsv, seeds 23,000,000,000 + 10,000 x pairing + i)"
 "fresh_kta3_new17|kta3|N17|500|FN|${REFS[1]}||7 kta3 fresh, the 17 new cells (fresh_new_decks.tsv, seeds 23,001,000,000 + 10,000 x pairing + i)"
 "dev_kta3_table|kta3|ALL28|500|TAB|${REFS[2]}||7 kta3 development, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
 "dev_kta3_new17|kta3|N17|500|DN|${REFS[3]}||7 kta3 development, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)"
 "dev_km3_table|km3|ALL28|500|TAB|${REFS[4]}||7 km3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
 "dev_km3_new17|km3|N17|500|DN|${REFS[5]}||7 km3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)"
 "table_k3|k3|ALL28|500|TAB|${REFS[6]}||7 k3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i; scoreboard v3)"
 "table_kp3|kp3|ALL28|500|TAB|${REFS[8]}||7 kp3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i; scoreboard v3)"
 "table_kog3|kog3|ALL28|500|TAB|${REFS[10]}||7 kog3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
 "new17_kog3|kog3|N17|500|DN|${REFS[11]}||7 kog3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)"
 "table_kq3|kq3|ALL28|500|TAB|${REFS[12]}||7 kq3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
 "table_kpr3_40|kpr3|ALL28|40|TAB|${REFS[13]}|40|7 kpr3, the 28 table cells, i < 40 (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
 "table_kd3_40|kd3|ALL28|40|TAB|${REFS[14]}||7 kd3 (a gate), the 28 table cells, i < 40 (--decks, seeds 72,000,000 + 10,000 x pairing + i)"
)
SPEC7B=("watch_table_k3|k3|ALL28|500|TAB" "watch_table_kp3|kp3|ALL28|500|TAB")
SPEC7C=("7c_watch_km3|km3|P7C|60|P7C" "7c_old_km3|km3|P7C|60|P7C" "7c2_watch_km3|km3|P7C2|60|P7C2" "7c2_old_km3|km3|P7C2|60|P7C2")
HELPERS=(sitting1.sh checkpoint.sh sitting1_check.py switch_check.py sitting2_check.py floor_with.py quiet.sh .gitignore "${DATAFILES[@]}")

# ---- Knobs.
DL_GIVEN=${DEADLINE:+1}   # DEADLINE given explicitly (with ALLOW_DAYTIME=0, a daytime start needs it)
THREADS=${THREADS:-14}; NICE=${NICE:-10}; JOBS=${JOBS:-14}; DEADLINE=${DEADLINE:-school}; SCHOOL_CUT=${SCHOOL_CUT:-10:15}
HARD_STOP=${HARD_STOP:-auto}; PUSH_BY=${PUSH_BY:-auto}; ALLOW_DAYTIME=${ALLOW_DAYTIME:-auto}; BUSY_OK=${BUSY_OK:-0}
RATE=${RATE:-8.6}; SAFETY=${SAFETY:-1.25}; OVERHEAD_MIN=${OVERHEAD_MIN:-10}; EST5_MIN=${EST5_MIN:-40}; EST6_MIN=${EST6_MIN:-25}
for x in "$THREADS" "$NICE" "$JOBS" "$OVERHEAD_MIN" "$EST5_MIN" "$EST6_MIN"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "sitting1.sh: knob value $x is not a whole number" >&2; exit 2; }
done
for x in "$RATE" "$SAFETY"; do
  [[ $x =~ ^[0-9]+(\.[0-9]+)?$ ]] && awk -v v="$x" 'BEGIN {exit !(v > 0)}' || { echo "sitting1.sh: knob value $x is not a positive number" >&2; exit 2; }
done
[[ $ALLOW_DAYTIME =~ ^(0|1|auto)$ && $BUSY_OK =~ ^[01]$ ]] || { echo "sitting1.sh: ALLOW_DAYTIME is 0, 1 or auto; BUSY_OK is 0 or 1" >&2; exit 2; }
daytime_refused() {  # a start now, 11:30-21:00 UTC without an explicit DEADLINE, refused: always with ALLOW_DAYTIME=0; with
  local t   # auto (the default) on Monday-Friday only (Dustin's word covers the weekend; a weekday is class and travel)
  [ -z "$DL_GIVEN" ] || return 1
  t=$(date -u +%H%M); [ "$t" -ge 1130 ] && [ "$t" -lt 2100 ] || return 1
  [ "$ALLOW_DAYTIME" = 0 ] || { [ "$ALLOW_DAYTIME" = auto ] && [ "$(date -u +%u)" -le 5 ]; }
}
[[ $SCHOOL_CUT =~ ^[0-2][0-9]:[0-5][0-9]$ ]] || { echo "sitting1.sh: SCHOOL_CUT=$SCHOOL_CUT is not HH:MM (UTC)" >&2; exit 2; }
school_next() {  # start-epoch: the first Monday-Friday SCHOOL_CUT (UTC) strictly after it (a weekend start gets Monday's)
  local k d t dow
  for k in 0 1 2 3 4 5 6 7; do
    d=$(date -u -d "@$(($1 + k * 86400))" +%F) && t=$(date -u -d "$d $SCHOOL_CUT" +%s) && dow=$(date -u -d "$d" +%u) || return 1
    if [ "$dow" -le 5 ] && [ "$t" -gt "$1" ]; then echo "$t"; return 0; fi
  done
  return 1
}
to_epoch() {  # spec start-epoch: school, HH:MM (UTC; the next one after the start), an ISO time, or off (0)
  local s=$1 t d
  case $s in
    off) echo 0;;
    school) school_next "$2";;
    [0-2][0-9]:[0-5][0-9]) d=$(date -u -d "@$2" +%F) && t=$(date -u -d "$d $s" +%s) || return 1
                           [ "$t" -gt "$2" ] || t=$((t + 86400)); echo "$t";;
    *) date -u -d "$s" +%s;;
  esac
}
fmt() { if [ "$1" -gt 0 ]; then date -u -d "@$1" +%FT%TZ; else echo off; fi; }
T0=$(date +%s)
DL=$(to_epoch "$DEADLINE" "$T0") || { echo "sitting1.sh: DEADLINE=$DEADLINE is not school, HH:MM, an ISO time or off" >&2; exit 2; }
if [ "$HARD_STOP" = auto ]; then HS=$DL   # a step still going at the deadline stops cleanly (PLAN.md line 28)
else HS=$(to_epoch "$HARD_STOP" "$T0") || { echo "sitting1.sh: HARD_STOP=$HARD_STOP is not auto, HH:MM, an ISO time or off" >&2; exit 2; }; fi
if [ "$PUSH_BY" = auto ]; then if [ "$DL" -gt 0 ]; then PB=$((DL + 6300)); else PB=0; fi
else PB=$(to_epoch "$PUSH_BY" "$T0") || { echo "sitting1.sh: PUSH_BY=$PUSH_BY is not auto, HH:MM, an ISO time or off" >&2; exit 2; }; fi
KNOBS="threads $THREADS, nice $NICE, cargo jobs $JOBS, deadline $(fmt "$DL") ($DEADLINE; school = the next Monday-Friday $SCHOOL_CUT UTC), hard stop $(fmt "$HS") ($HARD_STOP), push by $(fmt "$PB") ($PUSH_BY), daytime start $(case $ALLOW_DAYTIME in 1) echo allowed;; 0) echo refused;; *) echo "allowed on weekends, refused Monday-Friday";; esac) (ALLOW_DAYTIME=$ALLOW_DAYTIME; without an explicit DEADLINE), beside another game run $([ "$BUSY_OK" = 1 ] && echo allowed || echo refused) (BUSY_OK), rate $RATE before measurement, safety $SAFETY, overhead $OVERHEAD_MIN min, build estimates $EST5_MIN and $EST6_MIN min"

# ---- Notes, stops and the anchored lines.
S=""; C=""; M=""; T=""; STEP=start; FINISHED=0; RECORD=0; LOCKED=0; PLAYED=0; REUSED=0; PRIV=""; WD=""; HALT_FILES=()
HALTED=0; CKPT_ALL=(); DONE_STEPS=(); KEEP_FILES=(); BAD=""; STEP_FILES=(); B=""; W=""; GYM=""; SCAN=""; GOLD=""; WSCAN=""; PIN_GYM=""
PG=$$; SUITE_NOTE=""; SUITE_WHY=""; RESERVED_NOTE=""; FLOORPY_NOTE=""; FLOOR_REPORT=""; CNT_PASS=""; CNT_OLD7C=""; CH7=""
BUSYNOTE=""; FOPTS=(); IN7=(); BLOBS_OK=0; PRECHECK=0
PINS="$O/programs.sha256"; WPINS="$O/watch.sha256"; CK="$O/switch_check.py"; CK2="$O/sitting1_check.py"; CK3="$O/sitting2_check.py"
FW="$O/floor_with.py"; CNT="$O/counters.tsv"
export SWITCH2_COUNTERS="$CNT"   # sitting1_check.py's counter model (sitting2_check.py imports it)
CKPT_OURS="$O/.sitting1.ours"   # the commits this switch's runs made or a start allowed: the only ones a push may carry
export CKPT_OURS
ts() { date -u +%FT%TZ; }
note() { if [ $DRY -eq 1 ] || [ "$PRECHECK" = 1 ]; then echo "$*"; else echo "$(ts) $*" >> "$O/STATUS.txt"; fi; }
pin_note() { if [ $DRY -eq 1 ]; then echo "(PIN_STATUS) $*"; else echo "$(ts) $*" >> "$O/PIN_STATUS.txt"; fi; }
state_line() {  # the anchored line, in both files; a pasted checker's FAILED / MISMATCH reworded (pin.sh stops on them)
  local l=$*
  l=${l//FAILED open or read/missing or unreadable}; l=${l//FAILED/does not match its record}; l=${l//MISMATCH/mismatch}
  if [ $DRY -eq 1 ]; then echo "$l"; else echo "$l" >> "$O/STATUS.txt"; echo "$l" >> "$O/PIN_STATUS.txt"; fi
}
halt() {  # (before the START line, step 4's pre-check makes a failed check a refused start: nothing recorded, no HALT on record)
  [ "$PRECHECK" != 1 ] || refuse "step 4's checks, run before any candidate or game (a data file or value that does not match git?): $*"
  state_line "SITTING 1 HALT $(ts) ${S:-?}: step $STEP: $*"; FINISHED=1; RECORD=1; HALTED=1; exit 1
}
soft() {  # marked what: a mismatch with a data file still marked TO FINALIZE is a NOTE in a dry run (usable before P lands);
  if [ $DRY -eq 1 ] && [ "$1" = 1 ]; then echo "dry run: NOTE (a file TO FINALIZE) $2"; else halt "$2"; fi   # else a halt
}
durable() {  # files...: fsync them before they are renamed into place or recorded (/mnt/c is 9p to NTFS: a power-off can keep
  sync -- "$@" 2> /dev/null || note "sync (fsync) of ${*##*/} did not succeed; carrying on"   # a rename and lose the data)
}
leftovers() {  # the untracked files left in this folder (GitHub Desktop shows them as changes; a restart reuses them)
  local l n
  l=$(git -C "$R" ls-files --others --exclude-standard -- "$REL" 9>&- 2> /dev/null) || return 0
  n=$(grep -c . <<< "$l" || true)
  if [ "$n" -eq 0 ]; then echo "; no untracked file is left here"; return 0; fi
  echo "; $n untracked files are left here (not committed; a restart reuses the complete game files among them): $(sed "s#^$REL/##" <<< "$l" | head -n 8 | tr '\n' ' ')$([ "$n" -le 8 ] || echo "...")"
}
die() {
  local hs=""
  [ "$PRECHECK" != 1 ] || refuse "step 4's checks, run before any candidate or game, could not run: $*"
  [ ! -e "$O/.sitting1.hardstop" ] || hs=" (the watchdog's hard stop at $(fmt "$HS"): the step ran past its estimate, or the laptop slept and woke after the deadline; a plain start resumes it)"
  state_line "SITTING 1 STOPPED $(ts) ${S:-?}: step $STEP: $*$hs$(leftovers)"; FINISHED=1; RECORD=1; exit 1
}
on_exit() {
  local rc=$? why
  trap '' HUP INT TERM   # a second stop signal must not cut the record short (checkpoint.sh's index step included)
  set +e
  if [ -n "$WD" ]; then kill "$WD" 2> /dev/null; fi
  if [ $DRY -eq 0 ] && [ $LOCKED -eq 1 ]; then
    if [ "$FINISHED" -eq 0 ]; then
      if [ -e "$O/.sitting1.hardstop" ]; then
        why="the watchdog's hard stop at $(fmt "$HS") (the step ran past its estimate, or the laptop slept and woke after the deadline); nothing of this step is committed; a plain start resumes it, reusing its complete game files"
      else why="exit code $rc outside a check (a script, system or signal stop, not a result; see the log)"; fi
      state_line "SITTING 1 STOPPED $(ts) ${S:-?}: step $STEP: $why$(leftovers)"
      RECORD=1
    fi
    rm -f -- "$O/.sitting1.hardstop" "$O/.sitting1.ckpt"
    if [ "$RECORD" -eq 1 ] && [ -n "$PRIV" ]; then record_commit; fi
  fi
  if [ -n "$PRIV" ]; then rm -rf -- "$PRIV"; fi
}
stopped_or_failed() {  # rc what: a stop signal is a stop (a restart plays it again); any other exit code is a halt
  local sig=$(( $1 - 128 )) name
  name=$(kill -l "$sig" 2> /dev/null || echo "?")
  case $1 in 129|130|137|143) die "$2 was stopped by signal $sig (SIG$name); a restart plays it again";; esac
  if [ "$1" -gt 128 ]; then halt "$2 ended on signal $sig (SIG$name): a program crash, not a stop"; fi
  halt "$2 exited with code $1"
}

# ---- The checkpoint commits (checkpoint.sh's functions; the copy in PRIV once the run has started).
rebuild_combined() {  # identity_check.txt, table_counters.txt and touched_check.txt from the per-step files there are
  local f; local -a a=() b=() t=()
  for f in identity_7.txt identity_7c.txt; do [ ! -f "$O/$f" ] || a+=("$O/$f"); done
  for f in counters_7b.txt counters_7c.txt; do [ ! -f "$O/$f" ] || b+=("$O/$f"); done
  [ ! -f "$O/touched_7c.txt" ] || t+=("$O/touched_7c.txt")
  if [ ${#a[@]} -gt 0 ]; then cat -- "${a[@]}" > "$O/identity_check.txt"; fi
  if [ ${#b[@]} -gt 0 ]; then cat -- "${b[@]}" > "$O/table_counters.txt"; fi
  if [ ${#t[@]} -gt 0 ]; then cat -- "${t[@]}" > "$O/touched_check.txt"; fi
}
ckpt_list() {  # extra REL paths: CF, every file a checkpoint commits now
  local f; CF=()
  for f in STATUS.txt PIN_STATUS.txt timing.tsv identity_check.txt table_counters.txt touched_check.txt; do [ ! -f "$O/$f" ] || CF+=("$REL/$f"); done
  CF+=("${CKPT_ALL[@]}" "${KEEP_FILES[@]}" "$@")
  mapfile -t CF < <(printf '%s\n' "${CF[@]}" | awk 'NF && !seen[$0]++')
}
done_files() {  # CKPT_ALL: every DONE step's files, each step's manifest checked again first; BAD: the steps whose files changed
  local n out; BAD=""; CKPT_ALL=()
  for n in "${DONE_STEPS[@]}"; do
    if out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$n.sha256" 2>&1); then
      mapfile -t -O "${#CKPT_ALL[@]}" CKPT_ALL < <(manifest_files "$n")
    else BAD+="step $n ($(head -n 2 <<< "$out" | tr '\n' ' ')) "; fi
  done
  [ -z "$BAD" ]
}
push_lim() {  # max: the seconds a checkpoint's fetch may take (its push gets 3 x); past the deadline, a quarter of the time
  local now l=$1  # left until PUSH_BY (12:00 UTC = 7:00 am CDT by default), at least 30 s
  now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ "$now" -ge "$DL" ] && [ "$PB" -gt 0 ]; then
    l=$(( (PB - now) / 4 )); [ "$l" -le "$1" ] || l=$1; [ "$l" -ge 30 ] || l=30
  fi
  echo "$l"
}
ckpt_msg() {  # title summary
  printf '%s\n' "Rules switch 2 sitting 1, $1 ($REL only)" "" "$2" "" \
    "Candidate ${C:-?} (main ${M:0:7} + P ${P:0:7}), made off-tree; checkpoint commit by $REL/sitting1.sh" \
    "(PLAN.md steps 4-7c) from a private index. No engine file, no pin, the manifest untouched." "" \
    "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > "$PRIV/ckpt.msg"
}
ORIGIN_WHY=""
origin_ahead() {  # seconds: a bounded fetch, then true when origin/main has commits main lacks (ORIGIN_WHY says so); sitting2.sh's
  local m o f="fetched origin"   # Oct 1 fix: nothing is committed on a stale main, so main never needs a merge
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
    die "$title: nothing committed: $ORIGIN_WHY. Main must equal origin/main by 7:00 am, and the runner never pulls or merges: in GitHub Desktop, Fetch origin, Pull origin, Push origin; then start again (it checks this step's files and commits them with its first checkpoint)"
  fi
  rebuild_combined; ckpt_list "$@"; ckpt_msg "$title" "$summary"
  : > "$O/.sitting1.ckpt"
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then rm -f -- "$O/.sitting1.ckpt"; die "$title: the checkpoint commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"; fi
  push=$(ckpt_push "$R" "$(push_lim 300)" 2> "$PRIV/push.err") || prc=$?
  rm -f -- "$O/.sitting1.ckpt"
  case $prc in
    0) note "checkpoint ($title): $out (${#CF[@]} paths named); $push";;
    2) die "$title: committed on main ($out) but not pushed: $(push_why). Main must equal origin/main by 7:00 am, and the runner never pulls: in GitHub Desktop, Fetch origin, Pull origin, Push origin; then start again (it resumes at the next step)";;
    3) die "$title: committed on main ($out) but not pushed: $(push_why). Once their owner has pushed them (or Dustin says they may go), start again (it resumes at the next step and pushes this run's commits)";;
    *) note "checkpoint ($title): $out (${#CF[@]} paths named); not pushed: $(push_why) (the run goes on; the next checkpoint pushes again)";;
  esac
}
push_why() {  # the reason ckpt_push gave: its "not pushed:" line (else the first lines of its stderr), without that prefix
  local l
  l=$(grep -m 1 '^not pushed: ' "$PRIV/push.err" 2> /dev/null) || l=$(head -n 2 "$PRIV/push.err" 2> /dev/null | tr '\n' ' ')
  echo "${l#not pushed: }"
}
not_pushed() {  # why [uncommitted]: after the record commit, a line in both files (left uncommitted; the next start's first
  local what="Fetch origin, Pull origin if it offers it, Push origin"   # checkpoint commits it)
  [ "${2:-}" != uncommitted ] || what="Fetch origin, Pull origin if it offers it; then, in GitHub Desktop, Commit this folder's changed files and Push origin"
  state_line "SITTING 1 NOT PUSHED $(ts) ${S:-?}: $1; main $(git -C "$R" rev-parse --short refs/heads/main 9>&- 2> /dev/null), origin/main $(git -C "$R" rev-parse --short refs/remotes/origin/main 9>&- 2> /dev/null) (as last fetched). main must equal origin/main by 7:00 am: a person looks at the reason, then in GitHub Desktop $what"
}
record_commit() {  # on exit after HALT, STOPPED, PAUSED or DONE: best effort; a record that is not pushed gets a NOT PUSHED line
  local out push rc=0 prc=0 last f
  local -a extra=()
  for f in "${HALT_FILES[@]}"; do [ ! -f "$O/$f" ] || extra+=("$REL/$f"); done
  if [ "$HALTED" -eq 1 ]; then  # the halted step's files so far (the games that differ among them), so origin can trace it
    for f in "${STEP_FILES[@]}"; do [ ! -f "$O/$f" ] || extra+=("$REL/$f"); done
  fi
  last=$(grep -E '^SITTING 1 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" | tail -n 1 | cut -c1-300)
  if ! done_files; then  # a DONE step's file changed: its files stay out of the record (checkpoint() halts on this)
    echo "$(ts) sitting1.sh: the record leaves out $BAD: those files changed since their checkpoint"
    echo "$(ts) the record commit leaves out $BAD: those files changed since their checkpoint" >> "$O/STATUS.txt"
  fi
  rebuild_combined; ckpt_list "${extra[@]}"; ckpt_msg "the record: ${last%% [0-9][0-9][0-9][0-9]-*}" "$last"
  if origin_ahead "$(push_lim 60)"; then  # as checkpoint(): no commit that would need a merge
    echo "$(ts) sitting1.sh: the record is not committed: $ORIGIN_WHY"
    not_pushed "the record is left uncommitted: $ORIGIN_WHY" uncommitted; return 0
  fi
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then
    echo "$(ts) sitting1.sh: the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"
    not_pushed "the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')" uncommitted; return 0
  fi
  push=$(ckpt_push "$R" "$(push_lim 120)" 2> "$PRIV/push.err") || prc=$?   # short: after a hard stop, 7:00 am is near
  if [ $prc -eq 0 ]; then echo "$(ts) sitting1.sh: the record ($last): $out; $push"
  else
    echo "$(ts) sitting1.sh: the record ($last): $out; not pushed: $(push_why)"
    not_pushed "the record is committed ($out) but not pushed: $(push_why)"
  fi
}

# ---- Step 4's parts (git only).
MT=""
merge_tree() {  # main: MT, the tree of the merge of main and P; a conflict halts
  local out rc=0
  out=$(git -C "$R" merge-tree --write-tree --name-only "$1" "$P" 9>&-) || rc=$?
  case $rc in
    0) MT=$(head -n 1 <<< "$out");;
    1) halt "the merge of main ${1:0:7} and P ${P:0:7} has conflicts: $(tail -n +2 <<< "$out" | head -n 20 | tr '\n' ' ')";;
    *) die "git merge-tree failed (exit $rc): $(head -n 3 <<< "$out" | tr '\n' ' ')";;
  esac
  [[ $MT =~ ^[0-9a-f]{40}$ ]] || die "git merge-tree printed no tree"
}
allowed_ns() { local k; for k in "${!ALLOWED[@]}"; do printf '%s\t%s\n' "${ALLOWED_ST[$k]}" "${ALLOWED[$k]}"; done | LC_ALL=C sort; }
ns_diff() {  # got want: what only git has, and what only allowed_engine_files.tsv has (status:path)
  echo "only in git: $(LC_ALL=C comm -23 <(echo "$1") <(echo "$2") | tr '\t\n' ': ')only in allowed_engine_files.tsv: $(LC_ALL=C comm -13 <(echo "$1") <(echo "$2") | tr '\t\n' ': ')"
}
p_checks() {  # [resume]: P's own facts (independent of main). On a resume (the candidate recorded, its second parent P), a
  local mode=${1:-} br got want c k kind np files o ns; local -a tests=()  # branch deleted or rewritten since is a note, not a halt
  git -C "$R" cat-file -e "$P^{commit}" 2> /dev/null || die "P ${P:0:7} is not here (fetch origin)"
  if git -C "$R" rev-parse -q --verify "$P_BRANCH^{commit}" > /dev/null && git -C "$R" merge-base --is-ancestor "$P" "$P_BRANCH" 2> /dev/null; then
    br="on $P_BRANCH (tip $(git -C "$R" rev-parse --short "$P_BRANCH"))"
  elif [ "$mode" = resume ]; then
    br="no longer on $P_BRANCH (deleted or rewritten since the candidate was made; the candidate's second parent, checked below, pins P)"
  else halt "P ${P:0:7} is not on $P_BRANCH"; fi
  [ "$(git -C "$R" rev-parse "$P:engine")" = "$P_TREE" ] || halt "P's engine/ is tree $(git -C "$R" rev-parse --short "$P:engine"), not P_TREE ${P_TREE:0:7} (switch2.env)"
  git -C "$R" merge-base --is-ancestor "$OFFICIAL" "$P" || halt "P ${P:0:7} does not stack on the official engine ${OFFICIAL:0:7} (main-8626a35)"
  got=$(git -C "$R" log --format=%H "$OFFICIAL..$P" -- engine | LC_ALL=C sort) || die "git log 8626a35..P -- engine"
  want=$(printf '%s\n' "${ENGINE_COMMITS[@]}" | LC_ALL=C sort)
  [ "$got" = "$want" ] || soft "$COMMITS_MARKED" "the commits that touch engine/ between 8626a35 and P are not exactly engine_commits.tsv's ${#ENGINE_COMMITS[@]}: only in git $(LC_ALL=C comm -23 <(echo "$got") <(echo "$want") | cut -c1-8 | tr '\n' ' ')only in the file $(LC_ALL=C comm -13 <(echo "$got") <(echo "$want") | cut -c1-8 | tr '\n' ' ')"
  for k in "${!ENGINE_COMMITS[@]}"; do
    c=${ENGINE_COMMITS[$k]}; kind=${ENGINE_KINDS[$k]}
    git -C "$R" cat-file -e "$c^{commit}" 2> /dev/null || { soft "$COMMITS_MARKED" "engine_commits.tsv names ${c:0:8}, which is not here"; continue; }
    np=$(git -C "$R" rev-list --parents -n 1 "$c" | wc -w); np=$((np - 1))
    if [ "$kind" = merge ]; then
      [ "$np" -eq 2 ] || soft "$COMMITS_MARKED" "${c:0:8} is listed as a merge but has $np parents"
      continue
    fi
    [ "$np" -eq 1 ] || { soft "$COMMITS_MARKED" "${c:0:8} is listed as $kind but has $np parents"; continue; }
    files=$(git -C "$R" diff-tree --no-commit-id -r --name-only "$c") || die "git diff-tree $c"
    o=$(grep -v -E '^(engine/|rl/results/)' <<< "$files" || true)
    [ -z "$o" ] || soft "$COMMITS_MARKED" "${c:0:8} ($kind) touches files outside engine/ and rl/results/: $(head -n 3 <<< "$o" | tr '\n' ' ')"
    case $kind in
      tests)
        while IFS= read -r f; do
          case $f in engine/*) ;; *) continue;; esac
          case $f in engine/tests/*) ;; *) soft "$COMMITS_MARKED" "${c:0:8} (tests first) touches $f, not a test"; continue;; esac
          case " ${ALLOWED[*]} " in *" $f "*) tests+=("$f");; *) soft "$ALLOW_MARKED" "${c:0:8} (tests first) touches $f, which allowed_engine_files.tsv does not list";; esac
        done <<< "$files";;
      src) grep -q '^engine/src/' <<< "$files" || soft "$COMMITS_MARKED" "${c:0:8} is listed as src but touches nothing in engine/src/";;
    esac
  done
  ns=$(git -C "$R" diff --no-renames --name-status "$OFFICIAL" "$P" -- engine/ | LC_ALL=C sort) || die "git diff 8626a35 P -- engine/"
  [ "$ns" = "$(allowed_ns)" ] || soft "$ALLOW_MARKED" "git diff --name-status 8626a35 P -- engine/ is not allowed_engine_files.tsv (PLAN.md step 4's list): $(ns_diff "$ns" "$(allowed_ns)")"
  git -C "$R" diff --quiet "$OFFICIAL" "$P" -- engine/src/players/ || halt "P changes engine/src/players/ (PLAN.md step 4: players/ must be unchanged)"
  o=$(git -C "$R" diff --name-only "$OFFICIAL" "$P") || die "git diff --name-only 8626a35 P"
  o=$(grep -E '(^|/)Cargo\.(lock|toml)$' <<< "$o" || true)
  [ -z "$o" ] || halt "P changes $(tr '\n' ' ' <<< "$o")(PLAN.md step 4: Cargo.lock and Cargo.toml must be unchanged)"
  note "P ${P:0:7} is $br, on top of the official engine 8626a35; the ${#ENGINE_COMMITS[@]} commits that touch engine/ since are engine_commits.tsv's, each of its kind; the tests-first commits touch $(printf '%s\n' "${tests[@]}" | LC_ALL=C sort -u | grep -c . || true) test files, all in the list; engine/ differs from 8626a35's in exactly allowed_engine_files.tsv's ${#ALLOWED[@]} files with their statuses; players/, Cargo.lock and Cargo.toml unchanged; P's engine/ is tree ${P_TREE:0:7}"
}
reserved_check() {  # main: P's files under this folder must not clash with main's or the working copy's (the merge here and at
  local m=$1 meta path mode typ blob a n=0 bad=""   # the pin would conflict); the same blob is fine (ADAPTATION_SPEC.md 1.10)
  while IFS=$'\t' read -r meta path; do
    [ -n "$path" ] || continue
    read -r mode typ blob <<< "$meta"
    [ "$typ" = blob ] || continue
    n=$((n + 1))
    a=$(git -C "$R" rev-parse -q --verify "$m:$path" 2> /dev/null || true)
    if [ -n "$a" ] && [ "$a" != "$blob" ]; then bad+="$path (main ${a:0:8}, P ${blob:0:8}) "; fi
    if [ -e "$R/$path" ] && [ "$(git -C "$R" hash-object --no-filters -- "$R/$path")" != "$blob" ]; then bad+="$path (the working copy's is not P's ${blob:0:8}) "; fi
  done < <(git -C "$R" ls-tree -r "$P" -- "$REL/")
  [ -z "$bad" ] || halt "P's files in $REL clash with this folder's: $bad(the merge at step 4 and at the pin would conflict: move this folder's file away; ADAPTATION_SPEC.md 1.10)"
  RESERVED_NOTE="P holds $n files under $REL (early_warning_8b/, tightened_rule.py, ...): none clashes with main's or the working copy's"
}
cand_msg() {  # main tree: the candidate's message (the final merge message)
  cat <<EOF
Merge claude/coin-prevention-round2 at ${P:0:7} (P) into main: the rules switch 2 candidate (Dustin, Oct 9: "1-3 sure", go "update if everything passes")

The round-2 coin package, the card-text job and its follow-up (Will, Victory Star, Trap Territory, Guts, Perish Body,
Luxury Coin and the Fossil lock), Cursed Jewel's Weakness on an attack's return damage (P2, with its off-switch), a Fossil
as an Item card at the seven other places (P3), Gholdengo's caveat text (P1), Bounded Field's x2 on a hit back, and one
revert switch per gate (default on) (rl/results/engine_switch_rules2_2026-10/PLAN.md sections 0 and 2; RELEASE_PACKAGE.md,
"What it is"). engine/ is P's tree ${P_TREE:0:7} byte for byte. Against main ${1:0:7}, the first parent, outside rl/results/
only these change:
$(git -C "$R" diff --name-only "$1" "$2" -- . ':(exclude)rl/results/' | sed 's/^/  /')
engine/src/players/, Cargo.lock and Cargo.toml do not. Made off-tree by rl/results/engine_switch_rules2_2026-10/sitting1.sh
(step 4: git merge-tree, git commit-tree), which builds and replays this commit; main reaches rules switch 2 only through the
pin (PLAN.md steps 11-14), after every replay passes and with Dustin's word on any judgment call.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
}
candidate_checks() {  # tree-ish main: step 4's checks on the candidate (in a dry run, the merge tree)
  local c=$1 m=$2 et ns lock del addm f p; local -a rmod=()
  [ "$(git -C "$R" rev-parse "$m:engine")" = "$MAIN_ENGINE" ] \
    || halt "main ${m:0:7}'s engine/ is not the official engine's source (tree 38af8b0, main-8626a35's): the switch's base has moved"
  et=$(git -C "$R" rev-parse "$c:engine") || die "no engine/ in $c"
  [ "$et" = "$P_TREE" ] || halt "the candidate's engine/ is tree $et, not P's ${P_TREE:0:7} exactly; it differs in: $(git -C "$R" diff --name-only "$P" "$c" -- engine | tr '\n' ' ')(PLAN.md step 4's byte check; this goes to Dustin)"
  ns=$(git -C "$R" diff --no-renames --name-status "$m" "$c" -- . ':(exclude)rl/results/' | LC_ALL=C sort) || die "git diff main..candidate"
  [ "$ns" = "$(allowed_ns)" ] || soft "$ALLOW_MARKED" "outside rl/results/ the candidate's changes against main are not allowed_engine_files.tsv's (paths and statuses): $(ns_diff "$ns" "$(allowed_ns)")"
  git -C "$R" diff --quiet "$m" "$c" -- engine/src/players/ || halt "the candidate changes engine/src/players/"
  lock=$(git -C "$R" diff --name-only "$m" "$c") || die "git diff --name-only main..candidate"
  lock=$(grep -E '(^|/)Cargo\.(lock|toml)$' <<< "$lock" || true)
  [ -z "$lock" ] || halt "the candidate changes $(tr '\n' ' ' <<< "$lock")"
  del=$(git -C "$R" diff --no-renames --diff-filter=D --name-only "$m" "$c") || die "git diff --diff-filter=D"
  [ -z "$del" ] || halt "the candidate deletes $(head -n 5 <<< "$del" | tr '\n' ' ')"
  f=$(git -C "$R" rev-parse -q --verify "$c:$VS_SCRIPT" || true); p=$(git -C "$R" rev-parse -q --verify "$P:$VS_SCRIPT" || true)
  [ -n "$f" ] && [ "$f" = "$VS_SCRIPT_BLOB" ] && [ "$f" = "$p" ] || halt "the candidate's $VS_SCRIPT is ${f:-none}, not ${VS_SCRIPT_BLOB:0:8} (switch2.env) and P's (${p:-none})"
  f=$(git -C "$R" rev-parse -q --verify "$c:$COIN_SCRIPT" || true); p=$(git -C "$R" rev-parse -q --verify "$P:$COIN_SCRIPT" || true)
  [ -n "$f" ] && [ "$f" = "$COIN_SCRIPT_BLOB" ] && [ "$f" = "$p" ] || halt "the candidate's $COIN_SCRIPT is ${f:-none}, not ${COIN_SCRIPT_BLOB:0:8} (switch2.env) and P's (${p:-none}): the coin script from P's branch, PLAN.md step 6"
  addm=$(git -C "$R" diff --no-renames --name-status "$m" "$c" -- rl/results/ | cut -f1 | sort | uniq -c | tr -s ' \n' ' ')
  mapfile -t rmod < <(git -C "$R" diff --no-renames --diff-filter=M --name-only "$m" "$c" -- rl/results/)
  note "candidate checks pass: engine/ is P's tree ${P_TREE:0:7}; main ${m:0:7}'s engine/ is 38af8b0 (main-8626a35's); outside rl/results/ exactly allowed_engine_files.tsv's ${#ALLOWED[@]} files change, each with its listed status; players/, Cargo.lock and Cargo.toml unchanged; nothing deleted; the watch scripts are P's (Victory Star ${VS_SCRIPT_BLOB:0:8}, coin ${COIN_SCRIPT_BLOB:0:8}). Under rl/results/ (status counts):$addm; existing files it modifies: ${rmod[*]:-(none)}"
}
suite_check() {  # precondition (g): SUITE_AT_P = <commit>:<path>, a suite log at that commit that names P and holds no failure
  local sc=${SUITE_AT_P%%:*} sp=${SUITE_AT_P#*:} txt tot
  git -C "$R" cat-file -e "$sc^{commit}" 2> /dev/null || { SUITE_WHY="SUITE_AT_P's commit $sc is not here (fetch origin)"; return 1; }
  txt=$(git -C "$R" show "$sc:$sp" 9>&- 2> /dev/null) || { SUITE_WHY="$sp is not in ${sc:0:8} (SUITE_AT_P)"; return 1; }
  grep -qF -- "${P:0:7}" <<< "$txt" || { SUITE_WHY="$sp at ${sc:0:8} does not name P ${P:0:7} (a suite at another commit; PLAN.md precondition (g) needs the suite at P)"; return 1; }
  grep -qE '(^|[^0-9])0 failed' <<< "$txt" || { SUITE_WHY="$sp at ${sc:0:8} holds no '0 failed' line"; return 1; }
  if grep -qE '(^|[^0-9])[1-9][0-9]* failed' <<< "$txt"; then
    SUITE_WHY="$sp at ${sc:0:8} records a failure: $(grep -m 1 -E '(^|[^0-9])[1-9][0-9]* failed' <<< "$txt" | cut -c1-160)"; return 1
  fi
  tot=$(grep -m 1 '^TOTAL: ' <<< "$txt" || true)
  SUITE_NOTE="precondition (g): $sp at ${sc:0:8} names P ${P:0:7} and records no failure (${tot:-no TOTAL line})"
}

# ---- Step 5's parts: programs, references, inputs.
prog_sha() {  # program path: its recorded sha256 (programs.sha256 or watch.sha256)
  # Only the records that exist: before step 6, watch.sha256 does not, and a cat of it failed the pipeline under
  # pipefail (the Oct 1 03:16 UTC stop, right after step 5 passed: PIN_GYM's bare assignment exited the run).
  local f fs=()
  for f in "$PINS" "$WPINS"; do [ ! -s "$f" ] || fs+=("$f"); done
  [ ${#fs[@]} -gt 0 ] || return 0
  awk -v p="$1" 'substr($0, 67) == p {print substr($0, 1, 64); exit}' "${fs[@]}"
}
check_pins() {  # when
  local out
  [ "$(cat "$B/COMMIT" 2> /dev/null)" = "$C" ] || halt "$B/COMMIT is not the candidate $C ($1)"
  [ -s "$PINS" ] || halt "programs.sha256 is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$PINS" 2>&1) || halt "a program differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  if [ -s "$WPINS" ]; then
    [ "$(cat "$W/COMMIT" 2> /dev/null)" = "$C" ] || halt "$W/COMMIT is not the candidate $C ($1)"
    out=$(sha256sum -c --quiet --strict -- "$WPINS" 2>&1) || halt "the watch build differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  fi
}
REFSUM=""; INPUTS=""; INPUTS7C=""
verify_refs() {  # when
  local out
  out=$(cd "$B/ref" && sha256sum -c --quiet --strict -- "$REFSUM" 2>&1) || halt "a reference file differs from ${REFSUM##*/} ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  out=$(diff <(cut -c67- "$REFSUM") <(printf '%s\n' "${REFS[@]}") 2>&1) || halt "the list of references changed since ${REFSUM##*/} was written ($1; floor_7c.tsv?): $(grep '^[<>]' <<< "$out" | head -n 3 | tr '\n' ' ')"
}
gate_refs() {  # dir when: step 7's references have the sha256 recorded when they were played or adopted
  local x p sha src got
  for x in "${REF7[@]}"; do
    p=${x%%|*}; sha=${x#*|}; src=${sha#*|}; sha=${sha%%|*}
    got=$(sha256sum < "$1/$p" | cut -c1-64) || die "sha256 of $p"
    [ "$got" = "$sha" ] || halt "$p ($2) has sha256 ${got:0:16}.., not ${sha:0:16}.. as $src records it"
  done
}
inputs_rel() {  # the repository's files the games read, relative, sorted (the build's own decks are added by inputs_list; D's
  local f k   # first-list copy, not in the candidate, has its own record, <short>_inputs7c.sha256)
  { for f in "$R"/decks/research/*.txt "$R"/decks/screen/opponents/*.txt; do echo "${f#"$R"/}"; done
    for f in "$PFRESH_T" "$PFRESH_N" "$PDEV_N" "$PAIRS7C" decks/screen/floor.py lib/brew_pages.py lib/brew_consistency.py \
             lib/deckgym-database.json engine/src/players/public_pricing_player.rs project_manifest.json; do echo "$f"; done
    for k in "${!FP_DECK[@]}"; do case ${FP_DECK[$k]} in "$REL"/*) ;; *) echo "${FP_DECK[$k]}";; esac; done
    python3 "$CK" pairs-decks "$R/$PFRESH_T" "$R/$PFRESH_N" "$R/$PDEV_N" "$R/$PAIRS7C"
  } | LC_ALL=C sort -u
}
inputs_list() {  # every input, absolute, sorted
  local f
  { for f in "$B"/decks/research/*.txt; do echo "$f"; done
    inputs_rel | while IFS= read -r f; do echo "$R/$f"; done
  } | LC_ALL=C sort -u
}
verify_inputs() {  # when
  local out
  [ -s "$INPUTS" ] || halt "the inputs record ${INPUTS##*/} is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$INPUTS" 2>&1) || halt "an input file changed ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')(${INPUTS##*/})"
  out=$(diff <(cut -c67- "$INPUTS") <(inputs_list) 2>&1) || halt "the list of input files changed ($1): $(grep '^[<>]' <<< "$out" | head -n 3 | tr '\n' ' ')"
}
floor_py_check() {  # S1-22: the working copy's floor.py may replay every page: its sha256 is one the page allows, and when it is
  local cur cursha k atk pa pb psha asha="" dsha=""   # not the one the page was made with, only the pinned diff (floor.py's ATTACKERS
  local -a own=() diffd=()                          # table) separates them, and that table names none of those pages' decks
  cur=$(git -C "$R" hash-object --no-filters -- "$R/decks/screen/floor.py") || die "git hash-object decks/screen/floor.py"
  cursha=$(sha256sum < "$R/decks/screen/floor.py" | cut -c1-64)
  atk=$(python3 "$CK2" attackers "$R/decks/screen/floor.py") || halt "floor.py's ATTACKERS table cannot be read: $atk"
  read -r pa pb psha <<< "$FLOOR_PY_DIFF"
  for k in "${!FP_ID[@]}"; do
    case ",${FP_OK[$k]}," in *",$cursha,"*) ;; *) halt "decks/screen/floor.py (sha256 ${cursha:0:16}..) is not one floor_7c.tsv allows for page ${FP_ID[$k]}: a replay would not be floor.py's own call";; esac
    if [ "$cursha" = "${FP_MADE[$k]}" ]; then own+=("${FP_ID[$k]}"); continue; fi
    if [ -z "$dsha" ]; then
      asha=$(git -C "$R" cat-file blob "$pa" | sha256sum | cut -c1-64) || die "git cat-file floor.py's blob ${pa:0:8}"
      [ "$cur" = "$pb" ] || halt "decks/screen/floor.py is blob ${cur:0:8}, not ${pb:0:8}, the newer end of floor_7c.tsv's FLOOR_PY_DIFF"
      dsha=$(git -C "$R" diff --no-color --no-ext-diff "$pa" "$pb" | sha256sum | cut -c1-64) || die "git diff ${pa:0:8} ${pb:0:8}"
      [ "$dsha" = "$psha" ] || halt "git diff ${pa:0:8} ${pb:0:8} (floor.py) has sha256 ${dsha:0:16}.., not the pinned ${psha:0:16}.. (floor_7c.tsv)"
    fi
    [ "$asha" = "${FP_MADE[$k]}" ] || halt "page ${FP_ID[$k]} was made with floor.py sha256 ${FP_MADE[$k]:0:16}.., which is not FLOOR_PY_DIFF's older blob ${pa:0:8} (sha256 ${asha:0:16}..)"
    ! grep -qxF -- "${FP_DECK[$k]}" <<< "$atk" || halt "floor.py's ATTACKERS names ${FP_DECK[$k]} (page ${FP_ID[$k]}): its failure-mode columns would differ from the page's"
    diffd+=("${FP_ID[$k]}")
  done
  FLOORPY_NOTE="floor.py is sha256 ${cursha:0:16}.."
  [ ${#own[@]} -eq 0 ] || FLOORPY_NOTE+=", the one page(s) ${own[*]} were made with"
  [ ${#diffd[@]} -eq 0 ] || FLOORPY_NOTE+="; for page(s) ${diffd[*]} it differs from the one they were made with (${pa:0:8}) only in the pinned diff (sha256 ${psha:0:16}.., the ATTACKERS table of floor.py), which names none of their decks"
}
blob_check_inputs() {  # tree-ish: every repository input in the working copy is that tree's file; floor.py may replay every page
  local i n=0 lst; local -a RELS=() H=() BL=()
  lst=$(inputs_rel) || die "listing the input files failed"
  mapfile -t RELS <<< "$lst"
  for i in "${RELS[@]}"; do [ -f "$R/$i" ] || halt "input file $i is missing"; done
  mapfile -t H < <(cd "$R" && printf '%s\n' "${RELS[@]}" | git hash-object --stdin-paths)
  mapfile -t BL < <(for i in "${RELS[@]}"; do printf '%s:%s\n' "$1" "$i"; done | git -C "$R" cat-file --batch-check='%(objectname) %(objecttype)')
  [ ${#H[@]} -eq ${#RELS[@]} ] && [ ${#BL[@]} -eq ${#RELS[@]} ] || die "hashing the input files failed"
  for i in "${!RELS[@]}"; do
    [ "${BL[$i]}" = "${H[$i]} blob" ] || halt "input ${RELS[$i]} in the working copy is not the candidate's file (${BL[$i]})"
    n=$((n + 1))
  done
  floor_py_check
  BLOBS_OK=$n
}
write_inputs() {
  local f
  blob_check_inputs "$C"
  for f in "$B"/decks/research/*.txt; do
    cmp -s -- "$f" "$R/decks/research/${f##*/}" || halt "the build's decks/research/${f##*/} (read by --decks) differs from the working copy's"
  done
  [ "$(ls "$B/decks/research" | wc -l)" = "$(ls "$R/decks/research" | wc -l)" ] || halt "the build's decks/research and the working copy's hold different lists"
  inputs_list > "$PRIV/inputs.lst" || die "listing the inputs"
  mapfile -t IN < "$PRIV/inputs.lst"
  sha256sum -- "${IN[@]}" > "$INPUTS.part" || die "sha256 of the input files"
  durable "$INPUTS.part"; mv -- "$INPUTS.part" "$INPUTS"
  note "inputs recorded (before any game): ${#IN[@]} files, ${INPUTS##*/}; the $BLOBS_OK inside the repository equal the candidate's files; $FLOORPY_NOTE; every step checks them"
}
floor_pages_check() {  # tree-ish: floor_7c.tsv's pages: their 3 files are the blobs at the page's commit, each deck its listed blob
  local k x p a b
  for k in "${!FP_ID[@]}"; do
    for x in _games.jsonl _coverage.json .md; do
      p="${FP_REFDIR[$k]}/${FP_NAME[$k]}$x"
      a=$(git -C "$R" rev-parse -q --verify "$1:$p" 9>&- || true); b=$(git -C "$R" rev-parse -q --verify "${FP_COMMIT[$k]}:$p" 9>&- || true)
      [ -n "$b" ] || die "$p is not in ${FP_COMMIT[$k]:0:8}, page ${FP_ID[$k]}'s commit (floor_7c.tsv; fetch origin?)"
      [ "$a" = "$b" ] || halt "$p in ${1:0:7} is ${a:0:7}, not the blob ${b:0:7} recorded at ${FP_COMMIT[$k]:0:8} (page ${FP_ID[$k]}): step 7c would replay against another baseline"
    done
    case ${FP_DECK[$k]} in
      "$REL"/*) a=$(git -C "$R" rev-parse -q --verify "$D_FIRST_COMMIT:$D_FIRST_PATH" 9>&- || true); b="${D_FIRST_COMMIT:0:7}'s $D_FIRST_PATH";;
      *) a=$(git -C "$R" rev-parse -q --verify "$1:${FP_DECK[$k]}" 9>&- || true); b="${FP_DECK[$k]} in ${1:0:7}";;
    esac
    [ "$a" = "${FP_DECKBLOB[$k]}" ] || halt "page ${FP_ID[$k]}'s deck, $b, is ${a:-missing}, not ${FP_DECKBLOB[$k]:0:8} (floor_7c.tsv): the page would be replayed on another list"
  done
}
extract_refs() {  # the references, from the candidate, blob-checked
  local p d blob
  floor_pages_check "$C"
  for p in "${REFS[@]}"; do
    d="$B/ref/$p"; mkdir -p "$(dirname "$d")"
    blob=$(git -C "$R" rev-parse --verify -q "$C:$p") || halt "the reference $p is not in the candidate"
    git -C "$R" cat-file blob "$blob" > "$d.part" || die "git cat-file $p"
    [ "$(git -C "$R" hash-object --no-filters -- "$d.part")" = "$blob" ] || die "$p: the extracted file is not the candidate's blob"
    mv -- "$d.part" "$d"
  done
  gate_refs "$B/ref" "taken from the candidate"
  (cd "$B/ref" && sha256sum -- "${REFS[@]}") > "$REFSUM.part" || die "sha256 of the references"
  durable "$REFSUM.part"; mv -- "$REFSUM.part" "$REFSUM"
  note "references taken from the candidate (git cat-file, blob-checked) into $B/ref: ${#REFS[@]} files (step 7's 15, each with the sha256 recorded when it was played or adopted, and floor_7c.tsv's ${#FP_ID[@]} pages' games, coverage and page, each the blob at its page's commit), ${REFSUM##*/}"
}
old_programs() {  # the pinned old programs equal their SHA256SUMS and the manifest's record (main-8626a35, rl/engine-2026-10-02/)
  local k got rec man
  for ((k = 0; k < ${#OLD_SHA[@]}; k += 2)); do
    got=$(sha256sum < "${OLD_SHA[k]}" | cut -c1-64) || halt "${OLD_SHA[k]} is missing"
    rec=$(awk -v n="${OLD_SHA[k]##*/}" '$2 == n {print $1}' "$OLDP/SHA256SUMS")
    [ "$got" = "${OLD_SHA[k+1]}" ] && [ "$rec" = "$got" ] || halt "${OLD_SHA[k]} has sha256 ${got:0:16}.., not ${OLD_SHA[k+1]:0:16}.. (its SHA256SUMS says ${rec:0:16}..)"
  done
  man=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["available_release"]; print(r["name"], r["sha256"], r["legality_scan_sha256"], r["goldfish_sha256"], r["artifact"], r["legality_scan"], r["goldfish"])' "$R/project_manifest.json") \
    || halt "project_manifest.json cannot be read"
  [ "$man" = "$OLD_NAME ${OLD_SHA[1]} ${OLD_SHA[3]} ${OLD_SHA[5]} $OLD_DIR/deckgym $OLD_DIR/legality_scan $OLD_DIR/goldfish" ] \
    || halt "the manifest's available release is not $OLD_NAME's programs in $OLD_DIR: $man"
}

# ---- The game helpers.
run_record() {  # program cwd args...: the text of a .run record (the program's recorded sha256 and the exact command)
  local p=$1 d=$2; shift 2
  printf '%s sha256 %s\ncwd %s\nargs' "${p##*/}" "$(prog_sha "$p")" "$d"; printf ' %q' "$@"; printf '\n'
}
kept() { [ -e "$1" ] && [ -e "$2" ] && [ "$(cat "$2")" = "$3" ]; }
set_aside() {  # label dir why files...: a kept output that is no longer intact (a power-off after its write?) is moved aside,
  local label=$1 dir=$2 why=$3 st x; shift 3  # not committed (.gitignore: *.broken_*), and played again: never a halt by itself
  st=$(date -u +%Y%m%dT%H%M%SZ)
  for x in "$@"; do [ ! -e "$dir/$x" ] || mv -- "$dir/$x" "$dir/$x.broken_$st"; done
  note "$label: kept from an earlier start, but $why: its files ($*) moved aside with the suffix .broken_$st (not committed) and played again; the new run's checks decide"
}
timing_row() {  # name games seconds program
  [ -s "$O/timing.tsv" ] || printf 'name\tgames\tseconds\tprogram_sha256\tended\n' > "$O/timing.tsv"
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$(prog_sha "$4" | cut -c1-16)" "$(ts)" >> "$O/timing.tsv"
}
scan_args() {  # deals source: SA
  case $1 in
    TAB) SA=(--decks ../decks/research);;
    FT) SA=(--pairs "$R/$PFRESH_T" --root "$R" --seed-base 23000000000);;
    FN) SA=(--pairs "$R/$PFRESH_N" --root "$R" --seed-base 23001000000);;
    DN) SA=(--pairs "$R/$PDEV_N" --root "$R" --seed-base 21108000000);;
    P7C) SA=(--pairs "$R/$PAIRS7C" --root "$R" --seed-base "$SEED7C");;
    P7C2) SA=(--pairs "$O/pairs_7c2.tsv" --root "$R" --seed-base "$SEED7C2");;
    *) die "no deals source $1";;
  esac
}
pl_of() { case $1 in ALL28) echo "$ALL28";; N17) echo "$N17";; P7C) echo "$P7C";; P7C2) echo "$P7C2";; esac; }
cells_of() { case $1 in ALL28) echo 28;; N17) echo 17;; P7C) echo 32;; P7C2) echo 24;; esac; }
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
  out=$(python3 "$CK" rules "$f.txt") || halt "RULE FINDING or an incomplete page: $out"
}
ident() { ident_f "" "" "$@"; }
ident_f() {  # filter-option filter-value outfile label name expect max_i ref...: switch_check.py same (with --pairings or
  local fo=$1 fv=$2 idf=$3 label=$4 name=$5 expect=$6 maxi=$7 r line rc=0; shift 7  # --exclude-pairings when given); one line
  local -a args=(same "$O/$name.jsonl" --expect "$expect" --label "$label")       # per reference; any difference halts
  [ -z "$maxi" ] || args+=(--max-i "$maxi")
  [ -z "$fo" ] || args+=("$fo" "$fv")
  for r in "$@"; do args+=(--ref "$r"); done
  line=$(python3 "$CK" "${args[@]}") || rc=$?
  echo "$line" >> "$idf"
  case $rc in
    0) note "identity: $(tr '\n' ' ' <<< "$line" | cut -c1-400)";;
    1) halt "IDENTITY: $label differs from its reference (${idf##*/}): $(grep -o 'DIFFERS: .*' <<< "$line" | head -n 2 | tr '\n' ' ')";;
    *) halt "the identity check for $label could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$line")";;
  esac
}
counters_check() {  # outfile label options-then-files...: sitting1_check.py counters with counters.tsv; CNT_PASS, its verdict
  local cf=$1 label=$2 out rc=0; shift 2
  out=$(python3 "$CK2" counters --counters "$CNT" --label "$label" "$@") || rc=$?
  echo "$out" >> "$cf"
  case $rc in
    0) note "counters: $(tail -n 1 <<< "$out" | cut -c1-600)"
       CNT_PASS=$(grep -F ": PASS: " <<< "$out" | tail -n 1); CNT_PASS=${CNT_PASS#*: PASS: };;
    1) halt "COUNTERS: $label (${cf##*/}): $(grep -E 'NOT all 0|does not pass' <<< "$out" | head -n 2 | tr '\n' ' ' | cut -c1-700)";;
    *) halt "the counters check for $label could not read its input (exit $rc: a missing or malformed counter is not the watch build's output): $(tail -n 1 <<< "$out")";;
  esac
}
floor_opts() {  # k: FOPTS, the comparison's options for page k (floor_7c.tsv's mode; --allow-coverage-program always)
  local tok; local -a toks=()
  FOPTS=(--allow-coverage-program)
  IFS=',' read -r -a toks <<< "${FP_MODE[$1]}"
  for tok in "${toks[@]}"; do
    case $tok in
      equal) ;;
      report-opponent:?*) FOPTS+=(--report-opponent "${tok#report-opponent:}");;
      caveat:?*) FOPTS+=(--allow-caveat "${tok#caveat:}");;
      *) halt "floor_7c.tsv: page ${FP_ID[$1]} has the mode '$tok', which sitting1.sh does not know";;
    esac
  done
}
floor_call() {  # deckgym its-sha256 deck outdir logfile: floor.py's own call through floor_with.py
  # The recorded runs (floor_dustin_2026-09-30/run_floor.sh; floor_drafts_2026-10-02/run_floor.sh and run_addendum.sh) set no
  # RAYON_NUM_THREADS, so neither does this (rayon's default, every logical CPU); nice changes no game.
  ( cd "$R" && unset PDL_DB RAYON_NUM_THREADS && nice -n "$NICE" python3 "$FW" "$1" "$2" \
      "$R/decks/screen/floor.py" "$3" --out "$4" ) > "$5" 2>&1
}
run_floor() {  # k: page k of floor_7c.tsv: floor.py's own call on the new deckgym, then the comparison with the recorded page
  local k=$1 rc=0 s secs out x was_kept label want
  local pid=${FP_ID[$1]} nm=${FP_NAME[$1]} deck=${FP_DECK[$1]}
  local dir="$O/floor_7c/${FP_ID[$1]}" rdir="floor_7c/${FP_ID[$1]}" refd="$B/ref/${FP_REFDIR[$1]}"
  local -a outs=("${nm}_games.jsonl" "${nm}_coverage.json" "$nm.md" "$nm.run" "$nm.txt")
  floor_opts "$k"
  label="7c plain, page $pid ($nm, ${FP_REFDIR[$k]#rl/results/} at ${FP_COMMIT[$k]:0:8}, mode ${FP_MODE[$k]}): floor.py's own call (seed 7,100, km3 both sides, 240 a matchup; no RAYON_NUM_THREADS, as recorded) on the new deckgym v the recorded km3 floor page, on every field of floor.py's per-game summary record (not moves or decisions)"
  want=$(run_record "$GYM" "$R" "floor.py=$(sha256sum < "$R/decks/screen/floor.py" | cut -c1-64)" \
    "floor_with.py=$(sha256sum < "$FW" | cut -c1-64)" "$deck" --out "$REL/$rdir")
  mkdir -p -- "$dir"
  while :; do
    if kept "$dir/${nm}_games.jsonl" "$dir/$nm.run" "$want" && [ -e "$dir/${nm}_coverage.json" ] && [ -e "$dir/$nm.md" ]; then
      was_kept=1; note "floor $pid: kept from an earlier start"
    else
      was_kept=0
      rm -rf -- "$dir/$nm.part"; rm -f -- "$dir/${nm}_games.jsonl" "$dir/${nm}_coverage.json" "$dir/$nm.md" "$dir/$nm.run"
      mkdir -p -- "$dir/$nm.part"
      s=$(date +%s); rc=0
      floor_call "$GYM" "$PIN_GYM" "$deck" "$dir/$nm.part" "$dir/$nm.txt" || rc=$?
      [ $rc -eq 0 ] || stopped_or_failed $rc "floor.py on the new deckgym for page $pid (see $rdir/$nm.txt)"
      for x in _games.jsonl _coverage.json .md; do [ -s "$dir/$nm.part/$nm$x" ] || halt "floor.py wrote no $nm$x ($rdir/$nm.txt)"; done
      durable "$dir/$nm.part/${nm}_games.jsonl" "$dir/$nm.part/${nm}_coverage.json" "$dir/$nm.part/$nm.md" "$dir/$nm.txt"
      mv -- "$dir/$nm.part/${nm}_coverage.json" "$dir/$nm.part/$nm.md" "$dir/"; mv -- "$dir/$nm.part/${nm}_games.jsonl" "$dir/"
      rmdir -- "$dir/$nm.part"
      printf '%s\n' "$want" > "$dir/$nm.run"   # last: only a complete, synced page gets a record
      secs=$(( $(date +%s) - s )); x=$(grep -c . "$dir/${nm}_games.jsonl")
      timing_row "floor_$pid" "$x" "$secs" "$GYM"; PLAYED=$((PLAYED + x))
      note "floor $pid replayed in $secs s ($x games)"
    fi
    rc=0
    out=$(python3 "$CK2" floor "$dir" "$refd" "$nm" --label "$label" "${FOPTS[@]}") || rc=$?
    if [ $rc -ne 0 ] && [ $was_kept -eq 1 ]; then  # a kept page is replayed once; the replay's comparison decides
      set_aside "floor $pid" "$dir" "its comparison with the recorded page did not pass (exit $rc: $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1 | cut -c1-200)$(tail -n 1 <<< "$out" | grep -o 'malformed.*' | cut -c1-200))" "${outs[@]}"
      continue
    fi
    break
  done
  [ $was_kept -eq 0 ] || REUSED=$((REUSED + $(grep -c . "$dir/${nm}_games.jsonl")))
  for x in "${outs[@]}"; do STEP_FILES+=("$rdir/$x"); done
  echo "$out" >> "$O/identity_7c.txt"
  case $rc in
    0) note "identity: $(head -n 1 <<< "$out" | cut -c1-400)"
       x=$(grep -m 1 -o 'REPORT-OPPONENT .*' <<< "$out" || true)
       [ -z "$x" ] || FLOOR_REPORT+="page $pid's ${x#REPORT-OPPONENT }; ";;
    1) old_engine_replay "$k" "$out";;   # halts
    *) halt "the floor comparison for page $pid could not read its input (exit $rc): $(tail -n 1 <<< "$out")";;
  esac
}
old_engine_replay() {  # k out: page k's replay did not pass. PLAN.md step 7c: first replay that page on the old engine
  local k=$1 out=$2 rc=0 s secs x od verdict   # (rl/engine-2026-10-02/), to see whether the difference predates switch 2; it
  local pid=${FP_ID[$1]} nm=${FP_NAME[$1]} deck=${FP_DECK[$1]}   # still stops the switch
  local dir="$O/floor_7c/${FP_ID[$1]}/oldengine" rdir="floor_7c/${FP_ID[$1]}/oldengine" refd="$B/ref/${FP_REFDIR[$1]}"
  floor_opts "$k"
  note "page $pid's replay differs from its recorded page; replaying it on the old deckgym ($OLD_DIR) first (PLAN.md step 7c)"
  rm -rf -- "$dir"; mkdir -p -- "$dir/$nm.part"
  s=$(date +%s)
  floor_call "$OLD_GYM" "$OLD_GYM_SHA" "$deck" "$dir/$nm.part" "$dir/$nm.txt" || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "floor.py on the old deckgym ($OLD_DIR) for page $pid, after its new replay differed (see $rdir/$nm.txt)"
  for x in _games.jsonl _coverage.json .md; do [ -s "$dir/$nm.part/$nm$x" ] || halt "floor.py on the old deckgym wrote no $nm$x ($rdir/$nm.txt)"; done
  mv -- "$dir/$nm.part/${nm}_coverage.json" "$dir/$nm.part/$nm.md" "$dir/$nm.part/${nm}_games.jsonl" "$dir/"; rmdir -- "$dir/$nm.part"
  run_record "$OLD_GYM" "$R" "floor.py=$(sha256sum < "$R/decks/screen/floor.py" | cut -c1-64)" \
    "floor_with.py=$(sha256sum < "$FW" | cut -c1-64)" "$deck" --out "$REL/$rdir" > "$dir/$nm.run"
  secs=$(( $(date +%s) - s )); x=$(grep -c . "$dir/${nm}_games.jsonl")
  timing_row "floor_old_$pid" "$x" "$secs" "$OLD_GYM"; PLAYED=$((PLAYED + x))
  for x in "${nm}_games.jsonl" "${nm}_coverage.json" "$nm.md" "$nm.run" "$nm.txt"; do STEP_FILES+=("$rdir/$x"); done
  rc=0
  od=$(python3 "$CK2" floor "$dir" "$refd" "$nm" --label "7c page $pid on the OLD deckgym ($OLD_DIR, $OLD_NAME) v the recorded page" "${FOPTS[@]}") || rc=$?
  case $rc in
    0) verdict="it comes with switch 2 (the old engine reproduces the recorded page; the new one does not)";;
    1) verdict="the difference predates switch 2 (the old engine differs from the recorded page too)";;
    *) verdict="the old engine's comparison could not read its input (exit $rc), so whether it predates switch 2 is not known";;
  esac
  { echo "$od"; echo "7c page $pid: the replay-on-the-old-engine rule (PLAN.md step 7c): $verdict. It still stops the switch."; } >> "$O/identity_7c.txt"
  halt "IDENTITY: page $pid's floor replay differs from its recorded page (identity_7c.txt): $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1 | cut -c1-400); on the old engine: $verdict"
}
touched_7c() {  # deck 10 v t-weezing (pairing 7 of the new rows, named): sitting2_check.py touched, the watch build as the new
  local out rc=0 hf=handoff_7c_km3.tsv   # side (7b showed watch = plain); its changed games go to 8c, never a stop here
  STEP_FILES+=("$hf")
  out=$(python3 "$CK3" touched --old "$O/${S}_7c2_old_km3.jsonl" --new "$O/${S}_7c2_watch_km3.jsonl" \
        --watch "$O/${S}_7c2_watch_km3.jsonl" --pairings "$TWEEZ7C2" --expect 60 --step 7c --bot km3 --repo "$R" \
        --counters "$CNT" --out-handoff "$O/$hf" \
        --label "7c deck 10 v t-weezing (pairing $TWEEZ7C2 of 23,300,000,000), km3, old v new (the old legality_scan, $OLD_DIR; the watch build as the new side)") || rc=$?
  echo "$out" >> "$O/touched_7c.txt"
  case $rc in
    0) note "touched: $(tail -n 1 <<< "$out" | cut -c1-400)";;
    1) halt "TOUCHED: 7c deck 10 v t-weezing (touched_7c.txt): $(grep -F 'does not pass' <<< "$out" | tail -n 1 | cut -c1-700)";;
    *) halt "the touched check for 7c's deck 10 v t-weezing could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$out")";;
  esac
  [ -s "$O/$hf" ] || halt "sitting2_check.py touched wrote no $hf"
  CH7=$(( $(grep -c . "$O/$hf") - 1 ))
}

# ---- Step 7c-seeds' parts (before any 7c game).
d_first_copy() {  # D's first list, byte for byte from the 9cc6667 blob, at floor_7c/d_first/ (its basename kept: floor.py names
  local f="$R/$D_COPY" b s   # the page by it)
  if [ -e "$f" ]; then
    b=$(git -C "$R" hash-object --no-filters -- "$f"); s=$(sha256sum < "$f" | cut -c1-64)
    [ "$b" = "$D_FIRST_BLOB" ] && [ "$s" = "$D_FIRST_SHA" ] || halt "$D_COPY is here but is ${b:0:8} (sha256 ${s:0:16}..), not D's first list ${D_FIRST_BLOB:0:8} (sha256 ${D_FIRST_SHA:0:16}..)"
    return 0
  fi
  b=$(git -C "$R" rev-parse -q --verify "$D_FIRST_COMMIT:$D_FIRST_PATH") || die "D's first list is not at ${D_FIRST_COMMIT:0:8} (fetch origin)"
  [ "$b" = "$D_FIRST_BLOB" ] || halt "${D_FIRST_COMMIT:0:8}:$D_FIRST_PATH is ${b:0:8}, not ${D_FIRST_BLOB:0:8} (switch2.env)"
  mkdir -p -- "$(dirname "$f")"
  git -C "$R" cat-file blob "$b" > "$f.part" || die "git cat-file D's first list"
  if [ "$(git -C "$R" hash-object --no-filters -- "$f.part")" != "$b" ] || [ "$(sha256sum < "$f.part" | cut -c1-64)" != "$D_FIRST_SHA" ]; then
    rm -f -- "$f.part"; die "the copy of D's first list is not the blob ${b:0:8} with sha256 ${D_FIRST_SHA:0:16}.."
  fi
  durable "$f.part"; mv -- "$f.part" "$f"
  note "D's first list copied byte for byte from ${D_FIRST_COMMIT:0:7}'s blob ${D_FIRST_BLOB:0:8} (sha256 ${D_FIRST_SHA:0:16}..) to $D_COPY"
}
inputs7c_list() {  # the files step 7c reads beside step 5's record: D's first-list copy, the pages' decks, the panel, floor.py
  local f k
  { for k in "${!FP_DECK[@]}"; do echo "$R/${FP_DECK[$k]}"; done
    for f in "$R"/decks/screen/opponents/*.txt; do echo "$f"; done
    echo "$R/decks/screen/floor.py"
  } | LC_ALL=C sort -u
}
verify_inputs7c() {  # when
  local out
  [ -s "$INPUTS7C" ] || halt "the step 7c inputs record ${INPUTS7C##*/} is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$INPUTS7C" 2>&1) || halt "a step 7c input changed ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')(${INPUTS7C##*/})"
  out=$(diff <(cut -c67- "$INPUTS7C") <(inputs7c_list) 2>&1) || halt "the list of step 7c's inputs changed ($1): $(grep '^[<>]' <<< "$out" | head -n 3 | tr '\n' ' ')"
}
seeds_7c() {  # step 7c-seeds: written (or, at a later start, checked) before any 7c game; its STEP line once; a checkpoint
  local got f
  got=$(git -C "$R" hash-object --no-filters -- "$R/$PAIRS7C" 2> /dev/null || true)
  [ "$got" = "$PAIRS7C_BLOB" ] || halt "$PAIRS7C is ${got:-missing}, not Oct 1's ${PAIRS7C_BLOB:0:8} (its 32 rows are replayed in place)"
  d_first_copy
  python3 "$CK2" pairs7c2 --repo "$R" --out "$PRIV/pairs_7c2.tsv" --seeds-out "$PRIV/seeds_7c2.txt" > "$PRIV/pairs7c2.raw" 2>&1 \
    || halt "pairs7c2: $(cat "$PRIV/pairs7c2.raw")"
  sed "s#$PRIV/pairs_7c2.tsv#$REL/pairs_7c2.tsv#" "$PRIV/pairs7c2.raw" > "$PRIV/pairs7c2.out"
  for f in pairs_7c2.tsv seeds_7c2.txt; do
    if [ -e "$O/$f" ]; then cmp -s -- "$PRIV/$f" "$O/$f" || halt "$f is here but is not what pairs7c2 writes now (a deck or the panel changed?)"
    else cp -- "$PRIV/$f" "$O/$f.part"; durable "$O/$f.part"; mv -- "$O/$f.part" "$O/$f"; fi
  done
  printf '%s\n' "Replays for rules switch 2's step 7c (sitting1.sh): floor.py's own call, unchanged, on the candidate's new deckgym" \
    "(floor_with.py), one folder per page of floor_7c.tsv, compared with the recorded pages: floor_dustin_2026-09-30's km3 pages" \
    "(02, 06, 08, 14 and 10, made on the Sept 30 engine), draft D's root page (floor_drafts_2026-10-02, made on rl/engine-2026-10-02" \
    "from D's first list, copied here to d_first/ from the 9cc6667 blob) and D amended (floor_drafts_2026-10-02/draft-D_amended, today's" \
    "list). Evidence only: these are not floor pages and carry no verdict to use. Their '- Engine:' line names the new program, a" \
    "difference allowed by design; so is their '- Coverage from' line: the Sept 30 pages name rl/engine-2026-09-30/goldfish, while" \
    "floor.py now takes the manifest's goldfish, rl/engine-2026-10-02/'s, so the replays name that one (the coverage files themselves" \
    "are compared byte for byte). Deck 10's games against t-weezing may differ (Will with a Confused Xatu): reported, and a new page" \
    "in step 15. The comparison is on every field of floor.py's per-game summary record (seed, seat, result, points, turns and the" \
    "like), not on moves or decisions: the scans beside them carry those. Run as the recorded runs ran: no RAYON_NUM_THREADS (rayon's" \
    "default, every logical CPU: $(nproc 2> /dev/null || echo '?') here); nice $NICE (nice changes no game). A page that differs is" \
    "replayed on the old deckgym too, into <page>/oldengine/ (PLAN.md step 7c)." > "$O/floor_7c/NOTE.txt"
  if [ -s "$INPUTS7C" ]; then verify_inputs7c "at 7c-seeds, recorded at an earlier start"
  else
    mapfile -t IN7 < <(inputs7c_list)
    sha256sum -- "${IN7[@]}" > "$INPUTS7C.part" || die "sha256 of step 7c's inputs"
    durable "$INPUTS7C.part"; mv -- "$INPUTS7C.part" "$INPUTS7C"
    note "step 7c's inputs recorded (before any 7c game): ${#IN7[@]} files, ${INPUTS7C##*/} (D's first-list copy among them)"
  fi
  if ! step_is_done 7c-seeds; then
    echo "STEP 7c-seeds DONE $S $(ts) pairs_7c2.tsv, seeds_7c2.txt, D's first-list copy (blob ${D_FIRST_BLOB:0:8}) and ${INPUTS7C##*/} recorded before any 7c game; Oct 1's pairs_7c.tsv is blob ${PAIRS7C_BLOB:0:8}" >> "$O/STATUS.txt"
  fi
  checkpoint "step 7c's seeds, before any 7c game" "$(cat "$PRIV/pairs7c2.out")" "$REL/pairs_7c2.tsv" "$REL/seeds_7c2.txt" \
    "$REL/floor_7c/NOTE.txt" "$D_COPY" "$REL/${INPUTS7C##*/}"
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
  [ "$1" = 4 ] || { check_pins "after step $1"; verify_refs "after step $1"; verify_inputs "after step $1"; }
  [ "$1" != 7c ] || verify_inputs7c "after step 7c"
  (cd "$O" && sha256sum -- "${STEP_FILES[@]}") > "$O/step_$1.sha256.part" || die "sha256 of step $1's files"
  durable "$O/step_$1.sha256.part"; mv -- "$O/step_$1.sha256.part" "$O/step_$1.sha256"; durable "$O"
  pin_note "step $1: $2"
  step_done "$1" "$2"
  DONE_STEPS+=("$1")
  checkpoint "step $1 passed" "$2"
}
rate() {  # games a second: measured over every game timed so far (timing.tsv), or RATE before 2,000 games
  if [ -s "$O/timing.tsv" ]; then
    awk -F'\t' -v d="$RATE" 'NR > 1 && $3 > 0 {g += $2; s += $3} END {if (g >= 2000 && s > 0) printf "%.2f", g / s; else print d}' "$O/timing.tsv"
  else echo "$RATE"; fi
}
games_left() {  # step: the games it still has to play (a complete kept file counts as played)
  local x nm bot pl n g=0 k
  case $1 in
    7) for x in "${SPEC7[@]}"; do IFS='|' read -r nm bot pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + $(cells_of "$pl") * n)); done;;
    7b) for x in "${SPEC7B[@]}"; do IFS='|' read -r nm bot pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + $(cells_of "$pl") * n)); done;;
    7c) for k in "${!FP_ID[@]}"; do [ -e "$O/floor_7c/${FP_ID[$k]}/${FP_NAME[$k]}_games.jsonl" ] || g=$((g + 1920)); done
        for x in "${SPEC7C[@]}"; do IFS='|' read -r nm bot pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + $(cells_of "$pl") * n)); done;;
  esac
  echo "$g"
}
need_s() {  # step: the seconds it needs (games / rate x safety, or the build estimate; plus the overhead)
  local base g
  case $1 in
    4) base=300;; 5) base=$((EST5_MIN * 60));; 6) base=$((EST6_MIN * 60));;
    *) g=$(games_left "$1"); base=$(awk -v g="$g" -v r="$(rate)" -v k="$SAFETY" 'BEGIN {printf "%d", g / r * k + 0.5}');;
  esac
  echo $((base + OVERHEAD_MIN * 60))
}
begin_step() {  # n what: the deadline check (a step that would end after it is not started), then the program checks
  local need now how sdone
  STEP=$1; STEP_FILES=()
  case $1 in  # a record of a halt or a stop also commits these (best effort), as they are
    4) HALT_FILES=(candidate.txt);; 5) HALT_FILES=(build.log);; 6) HALT_FILES=(watch_patch.txt watch_build.log);;
    7) HALT_FILES=(identity_7.txt);; 7b) HALT_FILES=(counters_7b.txt);;
    7c) HALT_FILES=(identity_7c.txt counters_7c.txt touched_7c.txt handoff_7c_km3.tsv pairs_7c2.tsv seeds_7c2.txt floor_7c/NOTE.txt
                    "${D_COPY#"$REL"/}" "${S}_inputs7c.sha256");;
  esac
  need=$(need_s "$1"); now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ $((now + need)) -gt "$DL" ]; then
    case $1 in 4|5|6) how="the build estimate";; *) how="$(games_left "$1") games at $(rate) games a second x $SAFETY";; esac
    sdone=$(grep -oE "^STEP [0-9a-z-]+ DONE $S " "$O/STATUS.txt" 2> /dev/null | cut -d' ' -f2 | tr '\n' ' ' || true)
    state_line "SITTING 1 PAUSED $(ts) ${S:-?}: before step $1: it needs about $((need / 60)) min ($how, plus $OVERHEAD_MIN), so it would end after the deadline $(fmt "$DL"); not started. Steps done: ${sdone:-none }(committed). A plain start, the next evening, resumes at step $1"
    FINISHED=1; RECORD=1; exit 3
  fi
  [ "$1" = 4 ] || [ "$1" = 5 ] || { check_pins "before step $1"; verify_refs "before step $1"; verify_inputs "before step $1"; }
  note "step $1: $2 (about $((need / 60)) min with the overhead; deadline $(fmt "$DL"))"
}

# ---- The start's checks (also reported by the dry run).
git_locks() {  # the git lock files a power-off in a checkpoint can leave behind: prints those that are here
  local lk p
  for lk in index.lock refs/heads/main.lock; do
    p=$(git -C "$R" rev-parse --git-path "$lk" 9>&-); case $p in /*) ;; *) p="$R/$p";; esac
    [ ! -e "$p" ] || echo "$p"
  done
}
FOREIGN=""; ALLOWED_NEW=()
unpushed_check() {  # origin main: FOREIGN, the unpushed commits that are not this switch's (short ids); ALLOWED_NEW, the
  local c files; FOREIGN=""; ALLOWED_NEW=()  # unpushed ones not yet in .sitting1.ours that touch only this folder and START_HERE.md
  for c in $(git -C "$R" rev-list "$1..$2" 9>&-); do
    if grep -qxF "$c" "$CKPT_OURS" 2> /dev/null; then continue; fi
    files=$(git -C "$R" diff-tree --no-commit-id -r --name-only "$c" 9>&-) || files="?"
    if ! git -C "$R" rev-parse -q --verify "$c^2" > /dev/null 9>&- && ! grep -qvE "^($REL/|START_HERE\\.md\$)" <<< "$files"; then
      ALLOWED_NEW+=("$c")   # the runner's own commit (sitting1.sh, its helpers, the data files, the seed rows), or a checkpoint a power-off left unrecorded
    else FOREIGN+="${c:0:7} "; fi
  done
}
seed_row_ok() {  # [work]: START_HERE.md, as committed (or the working copy's), has a line holding 23,300,000,000 and 36–37
  local txt      # (seed_row_23_3B.md section 1), and its 23,100,000,000 row holds 36–37 (section 2: the cloud's 8b rows there)
  if [ "${1:-}" = work ]; then txt=$(cat "$R/START_HERE.md" 2> /dev/null) || return 1
  else txt=$(git -C "$R" show "HEAD:START_HERE.md" 9>&- 2> /dev/null) || return 1; fi
  awk 'index($0, "23,300,000,000") && index($0, "36–37") {f = 1}
       index($0, "| 23,100,000,000 ") == 1 && index($0, "36–37") {g = 1} END {exit !(f && g)}' <<< "$txt"
}
env_check() {  # the variables a start refuses: any DECKGYM_* (the engine's revert switches, read process-wide: one left set plays
  local v out=""   # another engine and still passes every program hash), PDL_EQUIV_DEALS and GOLDFISH_TRACE
  for v in $(compgen -e); do case $v in DECKGYM_*|PDL_EQUIV_DEALS|GOLDFISH_TRACE) out+="$v ";; esac; done
  printf '%s' "$out"
}
ld_alive() {  # pidfile: a launch_detached run still going (its own test: the pid with its start time, or a process of its group
  local f=$1 pid st pg tag p e   # that carries its tag)
  pid=$(sed -n 's/^pid=//p' "$f"); st=$(sed -n 's/^starttime=//p' "$f"); pg=$(sed -n 's/^pgid=//p' "$f"); tag=$(sed -n 's/^tag=//p' "$f")
  if [ -n "$pid" ] && [ -d "/proc/$pid" ] && [ "$(awk '{print $22}' "/proc/$pid/stat" 2> /dev/null)" = "$st" ]; then return 0; fi
  [ -n "$pg" ] && [ -n "$tag" ] || return 1
  for p in $(pgrep -g "$pg" 2> /dev/null || true); do
    e=$(tr '\0' '\n' < "/proc/$p/environ" 2> /dev/null) || continue
    grep -qxF -- "LAUNCH_DETACHED_RUN=$tag" <<< "$e" && return 0
  done
  return 1
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
busy_check() {  # what runs beside this start: game programs (and strength) outside this run's process group, a long run
  local pg pid gp comm f tag out=""   # watch.list names, other live launch_detached runs (a run_watch.sh watcher aside: it reads
  pg=$(ps -o pgid= -p $$ | tr -d ' ')  # status files and pushes only its own status branch)
  while read -r pid gp comm; do
    [ -n "$pid" ] && [ "$gp" != "$pg" ] || continue
    out+="$comm($pid) "
  done < <(ps -C legality_scan,deckgym,goldfish,cargo,rustc,tool_census,strength -o pid=,pgid=,comm= 2> /dev/null || true)
  out+=$(watch_list_busy "$pg")
  for f in "${KX_RUNS_DIR:-$HOME/runs}"/*.pid; do
    [ -e "$f" ] || continue
    tag=$(sed -n 's/^tag=//p' "$f")
    [ -z "${LAUNCH_DETACHED_RUN:-}" ] || [ "$tag" != "$LAUNCH_DETACHED_RUN" ] || continue
    case $(sed -n 's/^cmd=//p' "$f") in *rl/strength/run_watch.sh*) continue;; esac
    if ld_alive "$f"; then out+="launch_detached run $(basename "$f" .pid) "; fi
  done
  printf '%s' "$out"
}
helper_interfaces() {  # the options this runner calls in the helpers it does not own exist (a mismatch would halt at step 7c)
  local h x
  h=$(python3 "$O/switch_check.py" same --help 2>&1) || { echo "switch_check.py same --help failed: $(tail -n 1 <<< "$h")"; return 1; }
  grep -qF -- '--exclude-pairings' <<< "$h" || { echo "switch_check.py same has no --exclude-pairings (ADAPTATION_SPEC.md SC-1: step 7c's 23 new rows named equal need it)"; return 1; }
  h=$(python3 "$O/sitting2_check.py" touched --help 2>&1) || { echo "sitting2_check.py touched --help failed: $(tail -n 1 <<< "$h")"; return 1; }
  for x in --old --new --watch --pairings --expect --step --bot --repo --counters --out-handoff --label; do
    grep -qF -- "$x" <<< "$h" || { echo "sitting2_check.py touched has no $x (ADAPTATION_SPEC.md C2-4: step 7c's deck 10 v t-weezing row needs it)"; return 1; }
  done
  grep -qF -- '7c' <<< "$h" || { echo "sitting2_check.py touched does not take --step 7c (ADAPTATION_SPEC.md C2-4)"; return 1; }
}

# ---- The dry run: git checks only.
dry_run() {
  local m o x p sha got n k tmp out t rc=0 nst; local -a stg=()
  STEP=dry; S=dry
  m=$(git -C "$R" rev-parse refs/heads/main); o=$(git -C "$R" rev-parse refs/remotes/origin/main)
  echo "dry run: main ${m:0:7}, origin/main ${o:0:7}, $P_BRANCH $(git -C "$R" rev-parse --short "$P_BRANCH" 2> /dev/null || echo '(not here)') (as last fetched; no fetch now)"
  [ -z "$DATA_ERR" ] || halt "the data files: ${DATA_ERR%; } (ADAPTATION_SPEC.md Appendix A gives their contents)"
  echo "dry run: data files (sha256): $DATA_SUMS"
  for x in "${MARKED[@]}"; do echo "dry run: NOTE $x is marked TO FINALIZE (P is not final yet): a start refuses until it is filled in and committed"; done
  if [ "$P" = TO_FINALIZE ]; then
    P=$(git -C "$R" rev-parse -q --verify "$P_BRANCH^{commit}") || halt "$P_BRANCH is not here (fetch origin)"
    P_TREE=$(git -C "$R" rev-parse "$P:engine")
    echo "dry run: NOTE P is TO FINALIZE: this dry run takes the tip of $P_BRANCH, ${P:0:8} (engine/ tree ${P_TREE:0:8}), in its place"
  elif [ "$P_TREE" = TO_FINALIZE ]; then
    P_TREE=$(git -C "$R" rev-parse "$P:engine") || halt "P ${P:0:8} is not here (fetch origin)"
    echo "dry run: NOTE P_TREE is TO FINALIZE: P's own engine/ tree ${P_TREE:0:8} is taken in its place"
  fi
  if [ "$COIN_SCRIPT_BLOB" = TO_FINALIZE ]; then
    COIN_SCRIPT_BLOB=$(git -C "$R" rev-parse "$P:$COIN_SCRIPT") || halt "P has no $COIN_SCRIPT"
    echo "dry run: NOTE COIN_SCRIPT_BLOB is TO FINALIZE: P's blob ${COIN_SCRIPT_BLOB:0:8} is taken in its place"
  fi
  x=$(env_check); if [ -z "$x" ]; then echo "dry run: env: no DECKGYM_* set"; else echo "dry run: NOTE set in this environment (a start refuses): $x"; fi
  x=$(busy_check)
  if [ -z "$x" ]; then echo "dry run: no other game program or launch_detached run is going"
  else echo "dry run: NOTE going now (a start refuses unless BUSY_OK=1): $x"; fi
  if x=$(helper_interfaces); then echo "dry run: switch_check.py same takes --exclude-pairings; sitting2_check.py touched takes --pairings, --counters and --step 7c"
  else echo "dry run: NOTE $x (a start refuses)"; fi
  p_checks
  reserved_check "$m"; echo "dry run: $RESERVED_NOTE"
  merge_tree "$m"; T=$MT
  echo "dry run: the merge of main ${m:0:7} and P ${P:0:7} is tree $T, no conflicts"
  candidate_checks "$T" "$m"
  if [ "$SUITE_AT_P" = TO_FINALIZE ]; then echo "dry run: NOTE SUITE_AT_P is TO FINALIZE: precondition (g), the suite at P, is not named yet (a start refuses)"
  elif suite_check; then echo "dry run: $SUITE_NOTE"
  else echo "dry run: NOTE precondition (g): $SUITE_WHY (a start refuses)"; fi
  for x in "${REF7[@]}"; do
    p=${x%%|*}; sha=${x#*|}; sha=${sha%%|*}
    got=$(git -C "$R" cat-file blob "$T:$p" | sha256sum | cut -c1-64) || halt "the reference $p is not in the merge tree"
    [ "$got" = "$sha" ] || halt "$p in the merge tree has sha256 ${got:0:16}.., not the recorded ${sha:0:16}.."
  done
  echo "dry run: step 7's 15 references are in the merge tree with the sha256 recorded when they were played or adopted"
  for k in "${!FP_ID[@]}"; do
    p="${FP_REFDIR[$k]}/${FP_NAME[$k]}"
    n=$(git -C "$R" cat-file blob "$T:${p}_games.jsonl" | grep -c .) || halt "${p}_games.jsonl is not in the merge tree"
    git -C "$R" cat-file -e "$T:${p}_coverage.json" && git -C "$R" cat-file -e "$T:$p.md" || halt "page ${FP_ID[$k]}'s floor page is incomplete in the merge tree"
    [ "$n" = 1920 ] || halt "${p}_games.jsonl holds $n games, not 1,920"
  done
  floor_pages_check "$T"
  echo "dry run: floor_7c.tsv's ${#FP_ID[@]} pages (${FP_ID[*]}) are in the merge tree, 1,920 games each, with their coverage and page; all $(( ${#FP_ID[@]} * 3 )) files are the blobs at their pages' commits, and each deck is its listed blob"
  blob_check_inputs "$T"
  echo "dry run: the $BLOBS_OK repository inputs in the working copy equal the merge tree's files; $FLOORPY_NOTE"
  old_programs
  echo "dry run: $OLD_DIR/{deckgym,legality_scan,goldfish} equal their SHA256SUMS and the manifest's available release ($OLD_NAME)"
  tmp=$(mktemp -d /tmp/sitting1_rules2_dry.XXXXXX)
  git -C "$R" cat-file blob "$T:engine/examples/legality_scan.rs" > "$tmp/legality_scan.rs"
  git -C "$R" cat-file blob "$T:$VS_SCRIPT" > "$tmp/vs.py"; git -C "$R" cat-file blob "$T:$COIN_SCRIPT" > "$tmp/coin.py"
  rc=0; out=$( (python3 "$tmp/vs.py" "$tmp/legality_scan.rs" && python3 "$tmp/coin.py" "$tmp/legality_scan.rs") 2>&1) || rc=$?
  [ $rc -eq 0 ] || { rm -rf -- "$tmp"; halt "the watch scripts do not apply to the candidate's legality_scan.rs: $out"; }
  rc=0; out=$(python3 "$CK2" script-names --counters "$CNT" --coin "$tmp/coin.py" --patched "$tmp/legality_scan.rs") || rc=$?
  if [ $rc -eq 0 ]; then
    echo "dry run: both watch scripts apply to the candidate's legality_scan.rs, Victory Star's then the coin script (a scratch copy in /tmp): patched file sha256 $(sha256sum < "$tmp/legality_scan.rs" | cut -c1-16)..; $out"
  elif [ "$COUNTERS_MARKED" = 1 ]; then echo "dry run: NOTE (a file TO FINALIZE) counters.tsv against the watch scripts: $out"
  else rm -rf -- "$tmp"; halt "counters.tsv against the watch scripts (exit $rc): $out"; fi
  out=$(python3 "$CK2" pairs7c --repo "$R" --out "$tmp/pairs_7c.tsv") || { rm -rf -- "$tmp"; halt "pairs7c: $out"; }
  cmp -s -- "$tmp/pairs_7c.tsv" "$R/$PAIRS7C" || { rm -rf -- "$tmp"; halt "pairs7c no longer writes Oct 1's $PAIRS7C byte for byte (a deck or the panel changed?)"; }
  got=$(git -C "$R" hash-object --no-filters -- "$R/$PAIRS7C")
  [ "$got" = "$PAIRS7C_BLOB" ] || { rm -rf -- "$tmp"; halt "$PAIRS7C is ${got:0:8}, not Oct 1's ${PAIRS7C_BLOB:0:8}"; }
  echo "dry run: Oct 1's $PAIRS7C is blob ${PAIRS7C_BLOB:0:8}, and pairs7c still writes it byte for byte (its 32 rows are replayed in place)"
  mkdir -p "$tmp/root/decks/screen/opponents" "$tmp/root/decks/dustin" "$tmp/root/$(dirname "$D_FIRST_PATH")" "$tmp/root/$(dirname "$D_COPY")"
  cp -- "$R"/decks/screen/opponents/*.txt "$tmp/root/decks/screen/opponents/"
  cp -- "$R/decks/dustin/10-xatu-oricorio-tr-weezing.txt" "$tmp/root/decks/dustin/"
  cp -- "$R/$D_FIRST_PATH" "$tmp/root/$D_FIRST_PATH"
  git -C "$R" cat-file blob "$D_FIRST_COMMIT:$D_FIRST_PATH" > "$tmp/root/$D_COPY" || { rm -rf -- "$tmp"; halt "D's first list is not at ${D_FIRST_COMMIT:0:8} (fetch origin)"; }
  got=$(git -C "$R" hash-object --no-filters -- "$tmp/root/$D_COPY"); x=$(sha256sum < "$tmp/root/$D_COPY" | cut -c1-64)
  [ "$got" = "$D_FIRST_BLOB" ] && [ "$x" = "$D_FIRST_SHA" ] || { rm -rf -- "$tmp"; halt "D's first list at ${D_FIRST_COMMIT:0:8} is ${got:0:8} (sha256 ${x:0:16}..), not ${D_FIRST_BLOB:0:8} (${D_FIRST_SHA:0:16}..)"; }
  out=$(python3 "$CK2" pairs7c2 --repo "$tmp/root" --out "$tmp/pairs_7c2.tsv" --seeds-out "$tmp/seeds_7c2.txt") || { rm -rf -- "$tmp"; halt "pairs7c2: $out"; }
  echo "dry run: $out (written in /tmp; D's first list from ${D_FIRST_COMMIT:0:7}'s blob ${D_FIRST_BLOB:0:8}, sha256 ${D_FIRST_SHA:0:16}..)"
  for x in pairs_7c2.tsv seeds_7c2.txt; do
    if [ ! -e "$O/$x" ]; then continue
    elif cmp -s -- "$tmp/$x" "$O/$x"; then echo "dry run: $x here equals what pairs7c2 writes now"
    else echo "dry run: NOTE $x is here and differs from what pairs7c2 writes now (step 7c-seeds would halt)"; fi
  done
  if [ -e "$R/$D_COPY" ]; then
    if cmp -s -- "$R/$D_COPY" "$tmp/root/$D_COPY"; then echo "dry run: $D_COPY is here and is D's first list"
    else echo "dry run: NOTE $D_COPY is here and is not D's first list (step 7c-seeds would halt)"; fi
  fi
  rm -rf -- "$tmp"
  echo "dry run: seeds: step 7 replays the recorded deals (23,000,000,000 and 23,001,000,000 fresh; 72,000,000 table; 21,108,000,000 new cells); 7b the table's 72,000,000; 7c's floor replays seed 7,100 (floor.py's); Oct 1's 7c rows 23,100,000,000 + pairing x 10,000 + i, pairings 40-71, i < 60 ($PAIRS7C, in place); the new rows 23,300,000,000 + pairing x 10,000 + i, pairings 0-23, i < 60 (pairs_7c2.tsv, written at 7c-seeds)"
  [ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] && echo "dry run: the working copy is on main" || echo "dry run: NOTE the working copy is not on main (a start refuses)"
  nst=$(git -C "$R" diff --cached --name-only -- "$REL")
  if [ -z "$nst" ]; then echo "dry run: nothing in $REL is staged in the shared index"
  else
    mapfile -t stg <<< "$nst"
    if git -C "$R" diff --quiet -- "${stg[@]}"; then echo "dry run: NOTE staged in the shared index under $REL, equal to the working copy (a start unstages them): $(tr '\n' ' ' <<< "$nst")"
    else echo "dry run: NOTE staged in the shared index under $REL, and different from the working copy (a start refuses): $(tr '\n' ' ' <<< "$nst")"; fi
  fi
  for x in "${HELPERS[@]}"; do
    if git -C "$R" ls-files --error-unmatch -- "$REL/$x" > /dev/null 2>&1 && git -C "$R" diff --quiet HEAD -- "$REL/$x"; then t="committed"; else t="NOT committed (a start refuses until it is)"; fi
    echo "dry run: $x: $t"
  done
  if seed_row_ok; then echo "dry run: START_HERE.md (committed) has a seed-table line with 23,300,000,000 and 36–37, and its 23,100,000,000 row holds 36–37"
  elif seed_row_ok work; then echo "dry run: NOTE START_HERE.md has switch 2's two seed rows in the working copy only: a start refuses until they are committed (with the runner)"
  else echo "dry run: NOTE START_HERE.md has no line holding both 23,300,000,000 and 36–37, or its 23,100,000,000 row lacks 36–37 (the laptop session's seed_row_23_3B.md drafts both rows): a start refuses until they are committed"; fi
  x=$(git_locks); [ -z "$x" ] && echo "dry run: no git lock file (index.lock, refs/heads/main.lock)" || echo "dry run: NOTE git lock file here now: $(tr '\n' ' ' <<< "$x")(a start waits 15 s for it, then refuses)"
  if git -C "$R" merge-base --is-ancestor "$o" "$m"; then
    unpushed_check "$o" "$m"
    echo "dry run: origin/main ${o:0:7} is main or behind it ($(git -C "$R" rev-list --count "$o..$m") unpushed commits; this switch's by its own record or touching only $REL and START_HERE.md: $(( $(git -C "$R" rev-list --count "$o..$m") - $(wc -w <<< "$FOREIGN") )))"
    [ -z "$FOREIGN" ] || echo "dry run: NOTE main carries unpushed commits that are not this switch's: $FOREIGN(a start refuses: this run pushes only its own commits)"
  else echo "dry run: NOTE origin/main ${o:0:7} has commits main lacks: a start refuses (Pull origin first)"; fi
  if daytime_refused; then echo "dry run: NOTE it is $(date -u +%a\ %H:%M) UTC: with ALLOW_DAYTIME=$ALLOW_DAYTIME, a start now without an explicit DEADLINE refuses (daytime)"; fi
  rc=0; out=$(GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" push --dry-run --porcelain origin "refs/heads/main:refs/heads/main" 2>&1) || rc=$?
  echo "dry run: git push --dry-run origin main (no write; the credentials): exit $rc, $(grep -E '^[=!*+ -]|^Done|rejected|fatal|error' <<< "$out" | head -n 3 | tr '\n' ' ')"
  echo "dry run: a start now would have the deadline $(fmt "$DL"), the hard stop $(fmt "$HS") and the push-by $(fmt "$PB"); before any game is timed, at $(rate) games a second x $SAFETY + $OVERHEAD_MIN min: step 4 $(( $(need_s 4) / 60 )) min, 5 $(( $(need_s 5) / 60 )), 6 $(( $(need_s 6) / 60 )), 7 $(( $(need_s 7) / 60 )) ($(games_left 7) games), 7b $(( $(need_s 7b) / 60 )) ($(games_left 7b)), 7c $(( $(need_s 7c) / 60 )) ($(games_left 7c))"
  echo "dry run: every check passes$([ ${#MARKED[@]} -eq 0 ] || echo " but the TO FINALIZE notes above") (nothing written but git merge-tree's tree objects in .git)"
  FINISHED=1; exit 0
}

trap on_exit EXIT
if [ $DRY -eq 1 ]; then S=dry; dry_run; fi

# ---- One run at a time; refusals before the start line; the state of the last run.
mkdir -p "$O"
exec 9> "$O/.sitting1.lock"
flock -n 9 || { echo "$(ts) sitting1.sh: another sitting1.sh (or its orphaned child) holds $O/.sitting1.lock; this one exits" >&2; exit 2; }
# The flags a power-off or a SIGKILL leaves behind (only on_exit removes them otherwise): a stale .sitting1.ckpt would keep
# the watchdog from its hard stop until the first checkpoint, a stale .sitting1.hardstop would mislabel any stop.
rm -f -- "$O/.sitting1.ckpt" "$O/.sitting1.hardstop"
refuse() { echo "$(ts) sitting1.sh: start refused: $*" >&2; exit 2; }
s2_lock_held() {  # a live sitting2.sh (or its orphaned child) holds .sitting2.lock (sitting2.sh's s1_lock_held, the other way)
  local held=1
  [ -e "$O/.sitting2.lock" ] || return 1
  exec 8< "$O/.sitting2.lock"
  if flock -n 8; then flock -u 8; held=1; else held=0; fi
  exec 8<&-
  return $held
}
# One sitting at a time: a sitting 2 between its game programs is invisible to the busy check, and this start would unstage
# paths of this folder (below) while its checkpoint holds them in the shared index.
if s2_lock_held; then refuse "sitting2.sh (or its orphaned child) holds $O/.sitting2.lock: one sitting at a time. If no sitting2.sh runs (SITTING=2 bash quiet.sh status), its lock is free, so look for the process holding it (fuser .sitting2.lock)"; fi
for x in "${HELPERS[@]}"; do
  if ! git -C "$R" ls-files --error-unmatch -- "$REL/$x" > /dev/null 2>&1 || ! git -C "$R" diff --quiet HEAD -- "$REL/$x"; then
    refuse "$REL/$x is not committed as it is here; commit sitting1.sh, its helpers and the data files first (the evidence names committed code)"
  fi
done
[ "$(data_sums "$O")" = "$DATA_SUMS" ] || refuse "a data file changed while this start read it; start again"
[ -z "$DATA_ERR" ] || refuse "the data files: ${DATA_ERR%; } (ADAPTATION_SPEC.md Appendix A gives their contents)"
[ ${#MARKED[@]} -eq 0 ] || refuse "$(printf '%s; ' "${MARKED[@]}")TO FINALIZE (P is not final yet, PLAN.md section 0's status): fill these in when P lands, commit them, then start again (a dry run shows the rest)"
x=$(helper_interfaces) || refuse "$x"
[ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] || refuse "the working copy is not on main"
if daytime_refused; then
  refuse "it is $(date -u +%a\ %H:%M) UTC, daytime$([ "$ALLOW_DAYTIME" = 0 ] && echo ", and ALLOW_DAYTIME=0" || echo " on a weekday (ALLOW_DAYTIME=auto: Dustin's word covers the weekend; a weekday is class and travel)"): the default deadline would carry the run through the day. Give DEADLINE explicitly (school, HH:MM UTC, an ISO time, or off), or start with ALLOW_DAYTIME=1"
fi
seed_row_ok || refuse "START_HERE.md, as committed, has no seed-table line holding both 23,300,000,000 and 36–37, or its 23,100,000,000 row does not hold 36–37 (rules switch 2's block, and the cloud's 8b rows 36-37 on 23,100,000,000; PLAN.md section 5: they go into the seed table before any game; the laptop session's seed_row_23_3B.md drafts both rows). Commit them with the runner, then start again"
x=$(env_check)
[ -z "$x" ] || refuse "set in this environment: $x(a DECKGYM_* variable is one of the engine's revert switches, read process-wide: one left set plays another engine and still passes every program hash; PDL_EQUIV_DEALS and GOLDFISH_TRACE change what the programs do). Unset them, then start again"
x=$(busy_check)
if [ -n "$x" ]; then
  [ "$BUSY_OK" = 1 ] || refuse "another game run is going: $x(PLAN.md section 9: never beside a sitting; the 2-day combined run must have ended). Start once it has, or with BUSY_OK=1 if it is known and wanted"
  BUSYNOTE="; beside another run, allowed by BUSY_OK=1: $x"
else BUSYNOTE="; no other game program or launch_detached run"; fi
for x in $(seq 1 15); do LK=$(git_locks); [ -n "$LK" ] || break; sleep 1; done
[ -z "$LK" ] || refuse "git's lock file $(tr '\n' ' ' <<< "$LK")is here and stayed 15 s (a git program is running, or a power-off left it there). If GitHub Desktop and every other git program are idle, delete it, then start again"
UNSTAGED=""
x=$(git -C "$R" diff --cached --name-only -- "$REL" 9>&-)
if [ -n "$x" ]; then  # an interrupted checkpoint leaves the working copy's own content staged here: that is unstaged
  mapfile -t STG <<< "$x"
  git -C "$R" diff --quiet -- "${STG[@]}" 9>&- \
    || refuse "files in $REL are staged in the shared index and differ from the working copy: $(tr '\n' ' ' <<< "$x")- if no other session staged them (only this runner writes here), unstage them, which leaves the files as they are (git -C \"$R\" reset -q -- $REL; in GitHub Desktop nothing is staged), then start again"
  git -C "$R" reset -q -- "${STG[@]}" 9>&- || refuse "files in $REL are staged in the shared index (the working copy's content) and unstaging them failed: $(tr '\n' ' ' <<< "$x")"
  UNSTAGED="; unstaged at this start (staged equal to the working copy, as an interrupted checkpoint leaves them): $(sed "s#^$REL/##" <<< "$x" | tr '\n' ' ')"
fi
# Main must equal origin/main by 7:00 am and the runner never pulls, so origin/main may not be ahead; and this run pushes
# only its own commits, so main may not carry another session's unpushed work.
if GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then FETCHED="fetched origin"
else FETCHED="git fetch origin failed or timed out (offline?), so origin/main as last fetched"; fi
x=$(git -C "$R" rev-parse refs/heads/main 9>&-); LK=$(git -C "$R" rev-parse refs/remotes/origin/main 9>&-)
git -C "$R" merge-base --is-ancestor "$LK" "$x" 9>&- \
  || refuse "origin/main ${LK:0:7} has commits main ${x:0:7} lacks ($FETCHED): no checkpoint could be pushed. In GitHub Desktop: Fetch origin, Pull origin, Push origin; then start again"
unpushed_check "$LK" "$x"
[ -z "$FOREIGN" ] || refuse "main carries commits that are not on origin/main and are not this switch's: $FOREIGN(another session's work, or a Pull's merge commit). This run pushes only its own commits: have them pushed first (GitHub Desktop: Push origin, with their owner's word), then start again"
suite_check || refuse "precondition (g), the suite at P (PLAN.md section 4): $SUITE_WHY. Name the suite log at P in switch2.env's SUITE_AT_P (<commit>:<path>), commit it, then start again"
# A fresh start (no candidate yet): step 4's git checks run now, on the merge tree, before the START line, so that a slip in a
# data file or value is a refused start (nothing recorded), not a HALT on record that later needs Dustin's words at the pin.
# Step 4 runs them again on the candidate it makes.
if [ ! -s "$O/candidate.txt" ] && ! git -C "$R" rev-parse -q --verify "$CREF" > /dev/null 9>&-; then
  PRECHECK=1
  p_checks; x=$(git -C "$R" rev-parse refs/heads/main 9>&-); reserved_check "$x"; merge_tree "$x"; candidate_checks "$MT" "$x"
  PRECHECK=0
fi
if [ ${#ALLOWED_NEW[@]} -gt 0 ]; then printf '%s\n' "${ALLOWED_NEW[@]}" >> "$CKPT_OURS"; fi
PUSHNOTE="$FETCHED; main ${x:0:7}, origin/main ${LK:0:7}, $(git -C "$R" rev-list --count "$LK..$x" 9>&-) unpushed commits, all this switch's$([ ${#ALLOWED_NEW[@]} -eq 0 ] || echo " (allowed at this start, as they touch only $REL and START_HERE.md: $(printf '%s\n' "${ALLOWED_NEW[@]}" | cut -c1-7 | tr '\n' ' ' | sed 's/ $//'))")"
LOCKED=1
# The run's process group: this script's own (a plain start re-executes itself to lead one), or, under launch_detached, the
# group launch_detached made (its leader may be a "bash -c '... sitting1.sh && ... sitting2.sh'" chain). quiet.sh and the
# watchdog act on that group; .sitting1.pgid names it, the time and its leader's start time (quiet.sh checks them).
PG=$(ps -o pgid= -p $$ | tr -d ' ')
st=""; [ ! -r "/proc/$PG/stat" ] || st=$(< "/proc/$PG/stat")
st=${st##*) }; read -r -a stf <<< "$st"
echo "$PG $(ts) ${stf[19]:-0}" > "$O/.sitting1.pgid"
trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM   # (HUP stays ignored under nohup, as launch_detached starts it)
[ ! -s "$O/candidate.txt" ] || S=$(sed -n 's/^candidate //p' "$O/candidate.txt" | cut -c1-7)
PRIV=$(mktemp -d /tmp/sitting1_rules2.XXXXXX) || { PRIV=""; die "mktemp -d for the private copies"; }
cp -- "$O/switch_check.py" "$O/sitting1_check.py" "$O/sitting2_check.py" "$O/floor_with.py" "$O/checkpoint.sh" "$O/counters.tsv" "$PRIV/" \
  || die "copying the helpers"
cmp -s -- "$PRIV/counters.tsv" "$O/counters.tsv" && [ "$(data_sums "$O")" = "$DATA_SUMS" ] || die "counters.tsv or another data file changed during this start"
CK="$PRIV/switch_check.py"; CK2="$PRIV/sitting1_check.py"; CK3="$PRIV/sitting2_check.py"; FW="$PRIV/floor_with.py"
CNT="$PRIV/counters.tsv"; export SWITCH2_COUNTERS="$CNT"
# shellcheck source=checkpoint.sh
source "$PRIV/checkpoint.sh"
last=$(grep -E '^SITTING 1 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
case $last in
  "SITTING 1 HALT "*)
    if [ -z "${SITTING1_AFTER_HALT:-}" ]; then
      echo "$(ts) sitting1.sh: start refused: the last run halted ($last). A mismatch stops everything and goes to Dustin first; once it is explained (or a script fault is fixed), start with SITTING1_AFTER_HALT='<written reason>'" >&2
      LOCKED=0; exit 2
    fi
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    echo "SITTING 1 RESUMED AFTER HALT $(ts) ${S:-?}: SITTING1_AFTER_HALT='${SITTING1_AFTER_HALT//$'\n'/ }' (stamp $stamp)" >> "$O/STATUS.txt"
    # The halted run's check files are kept (a step that runs again starts its file afresh) and committed with the next
    # checkpoint, so its DIFFERS lines survive even if the halt's own record commit failed.
    for x in identity_7.txt:7 counters_7b.txt:7b identity_7c.txt:7c counters_7c.txt:7c touched_7c.txt:7c; do
      f=${x%%:*}; n=${x#*:}
      if [ -s "$O/$f" ] && ! grep -q "^STEP $n DONE ${S:-none} " "$O/STATUS.txt"; then
        mv -- "$O/$f" "$O/${f%.txt}.before_resume_$stamp.txt"; KEEP_FILES+=("$REL/${f%.txt}.before_resume_$stamp.txt")
        echo "$(ts) the halted run's $f is kept as ${f%.txt}.before_resume_$stamp.txt (committed with the next checkpoint); step $n writes $f afresh" >> "$O/STATUS.txt"
      fi
    done;;
  "SITTING 1 DONE "*)
    echo "$(ts) sitting1.sh: SITTING 1 DONE is already recorded ($last); nothing to do" >&2; LOCKED=0; exit 0;;
esac
CODE="sitting1.sh $(sha256sum < "$O/sitting1.sh" | cut -c1-16), checkpoint.sh $(sha256sum < "$PRIV/checkpoint.sh" | cut -c1-16), switch_check.py $(sha256sum < "$CK" | cut -c1-16), sitting1_check.py $(sha256sum < "$CK2" | cut -c1-16), sitting2_check.py $(sha256sum < "$CK3" | cut -c1-16), floor_with.py $(sha256sum < "$FW" | cut -c1-16) (sha256; HEAD $(git -C "$R" rev-parse --short HEAD))"
echo "SITTING 1 START $(ts) ${S:-?}: $KNOBS; pid $$, process group $PG$([ "$PG" = "$$" ] && echo " (led by this script)" || echo " (launch_detached's; its leader names this script)"); load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $({ ps -C legality_scan,deckgym,tool_census,goldfish,cargo,strength -o pid=,comm= 2> /dev/null || true; } | tr -s ' \n' ' ')$BUSYNOTE; env: no DECKGYM_* set; P ${P:0:8} (engine/ ${P_TREE:0:8}; $P_BRANCH); $SUITE_NOTE; code: $CODE (the checks run from private copies made now); data: $DATA_SUMS (sha256); git: $PUSHNOTE$UNSTAGED" >> "$O/STATUS.txt"
pin_note "sitting 1 start ${S:-?}: $CODE; data: $DATA_SUMS; P ${P:0:8}"
if [ "$HS" -gt 0 ]; then  # the watchdog: past HARD_STOP (read every 20 s, so also after a sleep), outside a checkpoint, TERM to the group
  ( trap - EXIT HUP INT TERM; exec 9>&-
    while sleep 20; do
      [ "$(date +%s)" -ge "$HS" ] || continue
      [ ! -e "$O/.sitting1.ckpt" ] || continue
      : > "$O/.sitting1.hardstop"; kill -TERM -- "-$PG" 2> /dev/null; exit 0
    done ) &
  WD=$!
fi

# ---- Step 4: the candidate.
STEP=4
if step_is_done 4 || [ -s "$O/candidate.txt" ]; then  # made at an earlier start: checked, never remade
  C=$(sed -n 's/^candidate //p' "$O/candidate.txt"); M=$(sed -n 's/^main //p' "$O/candidate.txt"); T=$(sed -n 's/^tree //p' "$O/candidate.txt")
  x=$(sed -n 's/^p //p' "$O/candidate.txt")
  [[ $C =~ ^[0-9a-f]{40}$ && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ ]] || halt "candidate.txt does not hold a candidate, main and tree"
  [ "$x" = "$P" ] || halt "candidate.txt records P ${x:-(none)}, not switch2.env's P ${P:0:8}: the candidate was made from another P (a new P needs a new candidate: candidate.txt and $CREF are moved away first, with the coordinator's word)"
  S=${C:0:7}
  p_checks resume
  reserved_check refs/heads/main
  merge_tree "$M"
  [ "$MT" = "$T" ] || halt "the merge of main ${M:0:7} and P is now tree $MT, not the recorded $T"
  [ "$(git -C "$R" rev-parse -q --verify "$CREF" || true)" = "$C" ] || halt "$CREF is not the recorded candidate $C"
  [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || halt "the candidate's tree is not the recorded $T"
  [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$P" ] \
    && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null || halt "the candidate's parents are not main ${M:0:7} and P"
  candidate_checks "$C" "$M"
  if step_is_done 4; then skip_done 4
  else STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + P ${P:0:7}), made at an earlier start and checked"; fi
elif EX=$(git -C "$R" rev-parse -q --verify "$CREF"); then
  # The ref is here but candidate.txt is not: a start stopped between update-ref and moving candidate.txt into place.
  CPART=$O/candidate.txt.part
  C=$(sed -n 's/^candidate //p' "$CPART" 2> /dev/null || true); M=$(sed -n 's/^main //p' "$CPART" 2> /dev/null || true)
  T=$(sed -n 's/^tree //p' "$CPART" 2> /dev/null || true); x=$(sed -n 's/^p //p' "$CPART" 2> /dev/null || true)
  why="$CREF exists (${EX:0:7}) but neither candidate.txt nor a matching candidate.txt.part records it: look at it (git log -1 $CREF), then delete it (git update-ref -d $CREF) or restore candidate.txt, and start again"
  [[ $C == "$EX" && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ && $x == "$P" ]] || die "$why"
  [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$P" ] \
    && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null && [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || die "$why (its parents or tree differ)"
  merge_tree "$M"
  [ "$MT" = "$T" ] || die "$why (the merge of main ${M:0:7} and P is tree $MT, not $T)"
  [ "$(git -C "$R" cat-file commit "$C" | sed '1,/^$/d')" = "$(cand_msg "$M" "$T")" ] || die "$why (its message is not sitting1.sh's)"
  S=${C:0:7}
  p_checks resume; reserved_check refs/heads/main; candidate_checks "$C" "$M"
  durable "$CPART"; mv -- "$CPART" "$O/candidate.txt"
  note "candidate $C adopted: $CREF, made by a start that stopped before recording it"
  STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + P ${P:0:7}), adopted"
else
  begin_step 4 "the candidate: the merge of main and P, off-tree"
  # At most 5 minutes (a stalled network counts as offline), no auto-maintenance, no prompt, without fd 9.
  if GIT_TERMINAL_PROMPT=0 timeout -k 30 300 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then note "fetched origin"
  else
    git -C "$R" cat-file -e "$P^{commit}" 2> /dev/null || die "git fetch origin failed or timed out and P is not here"
    note "git fetch origin failed or timed out (offline?); P is here, so the candidate is made from the local objects"
  fi
  p_checks
  M=$(git -C "$R" rev-parse refs/heads/main)
  note "main is ${M:0:7} (origin/main $(git -C "$R" rev-parse --short origin/main))"
  reserved_check "$M"; note "$RESERVED_NOTE"
  merge_tree "$M"; T=$MT
  candidate_checks "$T" "$M"   # on the tree, before any commit is made of it
  C=$(cand_msg "$M" "$T" | git -C "$R" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$T" -p "$M" -p "$P" -F - 9>&-) \
    || die "git commit-tree failed"
  [[ $C =~ ^[0-9a-f]{40}$ ]] || die "git commit-tree printed no commit"
  S=${C:0:7}
  printf 'candidate %s\nmain %s\np %s\ntree %s\nengine_tree %s\nmade %s\ncheck engine/ is P'"'"'s tree %s byte for byte; against main, outside rl/results/, exactly the %s files of allowed_engine_files.tsv change, each with its listed status; engine/src/players/, Cargo.lock and Cargo.toml unchanged; nothing deleted; P'"'"'s files under this folder clash with none\n' \
    "$C" "$M" "$P" "$T" "$(git -C "$R" rev-parse "$T:engine")" "$(ts)" "${P_TREE:0:7}" "${#ALLOWED[@]}" > "$O/candidate.txt.part"
  durable "$O/candidate.txt.part"
  git -C "$R" update-ref -m "sitting1.sh step 4: the rules switch 2 candidate" "$CREF" "$C" "" 9>&- || die "git update-ref $CREF failed"
  mv -- "$O/candidate.txt.part" "$O/candidate.txt"; durable "$O"
  note "candidate made: $C (merge of main ${M:0:7} and P ${P:0:7}, tree ${T:0:7}; at $CREF)"
  pin_note "candidate $C: the merge of main ${M:0:7} and P ${P:0:7} (claude/coin-prevention-round2), at $CREF; engine/ tree $(git -C "$R" rev-parse "$C:engine") (P's ${P_TREE:0:7})"
  STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + P ${P:0:7}): engine/ = P's, exactly allowed_engine_files.tsv's ${#ALLOWED[@]} engine files with their statuses, players/, Cargo.lock and Cargo.toml unchanged, no conflict; P's files under this folder clash with none"
fi

# ---- Step 5: the plain build, the references, the inputs.
B=/home/dacz8976/engine-rules2-$S; W=/home/dacz8976/engine-rules2-watch-$S
[[ $S =~ ^[0-9a-f]{7}$ ]] || die "no candidate short name ($S)"
GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"; GOLD="$B/engine/target/release/examples/goldfish"
WSCAN="$W/engine/target/release/examples/legality_scan"
REFSUM="$O/${S}_refs.sha256"; INPUTS="$O/${S}_inputs.sha256"; INPUTS7C="$O/${S}_inputs7c.sha256"
if step_is_done 5; then  # built at an earlier start: checked, never rebuilt
  STEP=5
  check_pins "at this start; built at an earlier start"; old_programs
  verify_refs "at this start"; gate_refs "$B/ref" "at this start"
  verify_inputs "at this start"
  skip_done 5
else
  begin_step 5 "the plain build: one git archive of $S, cargo --locked (deckgym, legality_scan, goldfish)"
  old_programs
  rm -rf -- "$B"; mkdir -p "$B"; echo "$C" > "$B/COMMIT"
  git -C "$R" archive "$C" engine decks | tar -x -C "$B" || die "git archive $C engine decks | tar"
  note "one git archive of $C (engine/ and decks/) in $B"
  set +u; source "$HOME/.cargo/env" 2> /dev/null || true; set -u
  note "building: $(cargo --version), $(rustc --version), $JOBS jobs, nice $NICE (build.log)"
  s=$(date +%s)
  ( cd "$B/engine" && unset CARGO_TARGET_DIR && nice -n "$NICE" cargo build --release --locked -j "$JOBS" \
      && nice -n "$NICE" cargo build --release --locked --example legality_scan -j "$JOBS" \
      && nice -n "$NICE" cargo build --release --locked --example goldfish -j "$JOBS" ) > "$O/build.log" 2>&1 9>&- \
    || die "the build failed (build.log; with --locked, a Cargo.lock that needs updating fails here too)"
  note "built in $(( $(date +%s) - s )) s"
  for p in "$GYM" "$SCAN" "$GOLD"; do [ -x "$p" ] || die "no program $p after the build"; done
  sha256sum -- "$GYM" "$SCAN" "$GOLD" "$OLD_GYM" "$OLD_SCAN" "$OLD_GOLD" > "$PINS.part"; durable "$PINS.part"; mv -- "$PINS.part" "$PINS"
  pin_note "built $C in $B (cargo build --release --locked; build.log); a fresh build: $B was removed first and archived anew, so engine/target/ started empty and CARGO_TARGET_DIR was unset (no cached library from another tree can be reused; the coordinator's note on git archive's commit-time stamps, Sept 30)"
  for p in "$GYM" "$SCAN" "$GOLD"; do pin_note "sha256 $(prog_sha "$p") ${p##*/} (new, plain)"; done
  for p in "$OLD_SCAN" "$OLD_GOLD" "$OLD_GYM"; do pin_note "sha256 $(prog_sha "$p") $OLD_DIR/${p##*/} (the pinned old program, $OLD_NAME; SHA256SUMS and the manifest agree)"; done
  mkdir -p "$PRIV"; extract_refs
  write_inputs
  check_pins "after the build"
  STEP_FILES=(programs.sha256 "${S}_refs.sha256" "${S}_inputs.sha256" build.log)
  finish_step 5 "deckgym $(prog_sha "$GYM" | cut -c1-16), legality_scan $(prog_sha "$SCAN" | cut -c1-16), goldfish $(prog_sha "$GOLD" | cut -c1-16) from one archive of $S (cargo --locked); ${#REFS[@]} references blob-checked, step 7's 15 with their recorded sha256, the ${#FP_ID[@]} floor pages' $(( ${#FP_ID[@]} * 3 )) files the blobs at their pages' commits; inputs recorded"
fi
PIN_GYM=$(prog_sha "$GYM")

# ---- Step 6: the watch build.
if step_is_done 6; then
  STEP=6; check_pins "at this start; the watch build of an earlier start"; skip_done 6
else
  # An earlier, unfinished attempt's watch.sha256 goes first (it is in no step manifest until step 6 is DONE): else a
  # start that stopped after its rm -rf of the watch folder would check that old record before step 6 and halt.
  rm -f -- "$WPINS"
  begin_step 6 "the watch build: both instrument_scan.py scripts on legality_scan, in $W"
  rm -rf -- "$W"; mkdir -p "$W"; echo "$C" > "$W/COMMIT"
  git -C "$R" archive "$C" engine decks | tar -x -C "$W" || die "git archive $C engine decks | tar (the watch build)"
  out=$(diff -rq -- "$B/decks" "$W/decks" 2>&1) || halt "the watch build's decks/ differ from the plain build's: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  mkdir -p "$PRIV/watch"
  for f in "$VS_SCRIPT" "$COIN_SCRIPT"; do
    blob=$(git -C "$R" rev-parse "$C:$f"); dst="$PRIV/watch/$(basename "$(dirname "$f")").py"
    if [ "$f" = "$VS_SCRIPT" ]; then x=$VS_SCRIPT_BLOB; else x=$COIN_SCRIPT_BLOB; fi
    git -C "$R" cat-file blob "$blob" > "$dst"
    [ "$(git -C "$R" hash-object --no-filters -- "$dst")" = "$blob" ] && [ "$blob" = "$x" ] && [ "$blob" = "$(git -C "$R" rev-parse "$P:$f")" ] \
      || halt "$f taken from the candidate is ${blob:0:8}, not ${x:0:8} (switch2.env) and P's blob"
  done
  WSRC="$W/engine/examples/legality_scan.rs"
  { echo "The watch build of $C ($W), rules switch 2's sitting1.sh step 6 (main ${M:0:7} + P ${P:0:7}). The two instrument_scan.py scripts, taken from the candidate (P's blobs, as switch2.env names them), applied in this order:"
    for f in "$VS_SCRIPT" "$COIN_SCRIPT"; do echo "  $f blob $(git -C "$R" rev-parse "$C:$f") sha256 $(sha256sum < "$PRIV/watch/$(basename "$(dirname "$f")").py" | cut -c1-64)"; done
    echo "engine/examples/legality_scan.rs before: sha256 $(sha256sum < "$WSRC" | cut -c1-64)"
  } > "$O/watch_patch.txt"
  python3 "$PRIV/watch/victory_star_repair_2026-09-30.py" "$WSRC" >> "$O/watch_patch.txt" 2>&1 \
    || halt "Victory Star's instrument_scan.py did not apply to legality_scan.rs (watch_patch.txt)"
  python3 "$PRIV/watch/coin_prevention_repair_2026-09-30.py" "$WSRC" >> "$O/watch_patch.txt" 2>&1 \
    || halt "the coin script (P's instrument_scan.py) did not apply to legality_scan.rs (watch_patch.txt)"
  for x in "${COUNTER_NAMES[@]}"; do
    grep -q "\"$x\"" "$WSRC" || halt "the patched legality_scan.rs does not write the counter $x (counters.tsv)"
  done
  out=$(python3 "$CK2" script-names --counters "$CNT" --coin "$PRIV/watch/coin_prevention_repair_2026-09-30.py" --patched "$WSRC") \
    || halt "counters.tsv is not what the watch scripts write: $out"
  echo "engine/examples/legality_scan.rs after: sha256 $(sha256sum < "$WSRC" | cut -c1-64), $(diff "$B/engine/examples/legality_scan.rs" "$WSRC" | grep -c '^>') lines added, $(diff "$B/engine/examples/legality_scan.rs" "$WSRC" | grep -c '^<') removed; it writes all ${#COUNTER_NAMES[@]} counters of counters.tsv (every firing tick kept); $out" >> "$O/watch_patch.txt"
  out=$(diff -rq --exclude=target -- "$B/engine" "$W/engine" 2>&1 || true)
  [ "$out" = "Files $B/engine/examples/legality_scan.rs and $W/engine/examples/legality_scan.rs differ" ] \
    || halt "the watch build's source differs from the plain build's in more than examples/legality_scan.rs: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  echo "Its source differs from the plain build's ($B) in engine/examples/legality_scan.rs only (diff -rq, target/ aside); decks/ equal." >> "$O/watch_patch.txt"
  set +u; source "$HOME/.cargo/env" 2> /dev/null || true; set -u
  s=$(date +%s)
  ( cd "$W/engine" && unset CARGO_TARGET_DIR && nice -n "$NICE" cargo build --release --locked --example legality_scan -j "$JOBS" ) \
    > "$O/watch_build.log" 2>&1 9>&- || die "the watch build failed (watch_build.log)"
  note "watch build made in $(( $(date +%s) - s )) s"
  [ -x "$WSCAN" ] || die "no program $WSCAN after the watch build"
  sha256sum -- "$WSCAN" > "$WPINS.part"; durable "$WPINS.part"; mv -- "$WPINS.part" "$WPINS"
  pin_note "watch build of $C in $W: sha256 $(prog_sha "$WSCAN") legality_scan (both instrument_scan.py scripts, P's; watch_patch.txt)"
  STEP_FILES=(watch.sha256 watch_patch.txt watch_build.log)
  finish_step 6 "watch legality_scan $(prog_sha "$WSCAN" | cut -c1-16) (Victory Star's then the coin script, P's blobs ${VS_SCRIPT_BLOB:0:8} and ${COIN_SCRIPT_BLOB:0:8}; all ${#COUNTER_NAMES[@]} counters of counters.tsv written; its source differs from the plain build's in that file only)"
fi

# ---- Step 7: identity for every pilot.
if step_is_done 7; then STEP=7; skip_done 7
else
  begin_step 7 "identity for every pilot on the plain legality_scan: $(games_left 7) of 151,240 games still to play"
  : > "$O/identity_7.txt"
  for x in "${SPEC7[@]}"; do
    IFS='|' read -r nm bot pl n src ref maxi label <<< "$x"
    scan_args "$src"
    run_scan "${S}_$nm" "$SCAN" "$B/engine" "$(pl_of "$pl")" "$n" "${SA[@]}" --bot "$bot"
    ident "$O/identity_7.txt" "$label" "${S}_$nm" $(( $(cells_of "$pl") * n )) "$maxi" "$B/ref/$ref"
  done
  STEP_FILES+=(identity_7.txt)
  finish_step 7 "identity for every pilot: kta3 fresh 14,000 + 8,500, kta3 development 14,000 + 8,500, km3 14,000 + 8,500, k3 and kp3 14,000 + 8,500 each (scoreboard v3's 45 cells), kog3 14,000 + 8,500, kq3 14,000, kpr3 1,120, kd3 1,120 (a gate): 151,240 games, each equal to its reference on every field (identity_7.txt)"
fi

# ---- Step 7b: the table's counters (the watch build, k3 and kp3).
if step_is_done 7b; then STEP=7b; skip_done 7b
else
  begin_step 7b "the watch build on the 28 cells, k3 and kp3: $(games_left 7b) of 28,000 games still to play"
  : > "$O/counters_7b.txt"
  for x in "${SPEC7B[@]}"; do
    IFS='|' read -r nm bot pl n src <<< "$x"
    scan_args "$src"
    run_scan "${S}_$nm" "$WSCAN" "$W/engine" "$(pl_of "$pl")" "$n" "${SA[@]}" --bot "$bot"
    ident "$O/counters_7b.txt" "7b watch $bot v plain $bot, the 28 table cells (step 7's ${S}_table_$bot)" "${S}_$nm" 14000 "" "$O/${S}_table_$bot.jsonl"
  done
  counters_check "$O/counters_7b.txt" "7b the table's counters, k3 and kp3 on the 28 cells (watch build; PLAN.md step 7b: round 2's exact counters 0 in every game; offgate_plain_attack_damage, offgate_by_attack (the first round's helpers and Chase Order's discard) and offgate_confused_attack above 0 somewhere; the others reported)" \
    --zero-role reach2 --require offgate_plain_attack_damage,offgate_by_attack,offgate_confused_attack --report-rest \
    --plain "$O/${S}_table_k3.jsonl" --plain "$O/${S}_table_kp3.jsonl" "$O/${S}_watch_table_k3.jsonl" "$O/${S}_watch_table_kp3.jsonl"
  STEP_FILES+=(counters_7b.txt)
  finish_step 7b "the watch build on the 28 cells: k3 and kp3 14,000 each, equal to the plain games on every field, each adding exactly counters.tsv's names; $CNT_PASS (counters_7b.txt)"
fi

# ---- Step 7c: Dustin's lists where rewritten lines run.
if step_is_done 7c; then STEP=7c; skip_done 7c
else
  begin_step 7c "the 7 floor pages of floor_7c.tsv (13,440 games), Oct 1's 32 rows x 60 on the watch and the old legality_scan (3,840) and the 24 new rows x 60 (2,880): $(games_left 7c) of 20,160 still to play"
  mkdir -p "$O/floor_7c"
  seeds_7c
  : > "$O/identity_7c.txt"; : > "$O/counters_7c.txt"; : > "$O/touched_7c.txt"; FLOOR_REPORT=""; CH7=""; CNT_OLD7C=""
  for k in "${!FP_ID[@]}"; do run_floor "$k"; done
  scan_args P7C
  run_scan "${S}_7c_watch_km3" "$WSCAN" "$W/engine" "$P7C" 60 "${SA[@]}" --bot km3
  run_scan "${S}_7c_old_km3" "$OLD_SCAN" "$B/engine" "$P7C" 60 "${SA[@]}" --bot km3
  ident "$O/identity_7c.txt" "7c watch v the old legality_scan ($OLD_DIR, $OLD_NAME), km3, Oct 1's 32 rows: decks 02/06/08/14 v the 8 panel lists, i < 60 (seeds 23,100,000,000 + 10,000 x pairing + i, pairings 40-71; $PAIRS7C in place)" \
    "${S}_7c_watch_km3" 1920 "" "$O/${S}_7c_old_km3.jsonl"
  counters_check "$O/counters_7c.txt" "7c the counters on Oct 1's 32 rows (watch build; as on Oct 1, by purpose: this switch's own counters, round 2's exact and superset ones, 0 in every game, and round 1's as on Oct 1; offgate_helper_choice and round 2's offgate_by_attack (the same helpers' rewritten constructor) needed in pairings $OFFGATE7C: 02, 06 and 08 v t-altaria, t-hydreigon and t-weezing, which hold no rewritten-helper attacker, so only Dustin's Absol, Heatmor or Gabite fire them there)" \
    --zero-role reach2 --zero-role superset2 --zero-role r1_exact --zero-role r1_heads --zero-role r1_superset \
    --require offgate_helper_choice,offgate_by_attack --in "$OFFGATE7C" --report-rest \
    "$O/${S}_7c_watch_km3.jsonl"
  CNT_OLD7C=$CNT_PASS
  scan_args P7C2
  run_scan "${S}_7c2_watch_km3" "$WSCAN" "$W/engine" "$P7C2" 60 "${SA[@]}" --bot km3
  run_scan "${S}_7c2_old_km3" "$OLD_SCAN" "$B/engine" "$P7C2" 60 "${SA[@]}" --bot km3
  ident_f --exclude-pairings "$TWEEZ7C2" "$O/identity_7c.txt" "7c2 watch v the old legality_scan ($OLD_DIR), km3, the 23 new rows named equal: deck 10, D's first list and D amended v the 8 panel lists, i < 60, deck 10 v t-weezing (pairing $TWEEZ7C2) aside (seeds 23,300,000,000 + 10,000 x pairing + i, pairings 0-23; pairs_7c2.tsv)" \
    "${S}_7c2_watch_km3" 1380 "" "$O/${S}_7c2_old_km3.jsonl"
  touched_7c
  counters_check "$O/counters_7c.txt" "7c2 the counters on the 24 new rows (watch build; PLAN.md step 7c: offgate_vs_ungated_built needed in D's rows, pairings $D7C2; offgate_confused_attack reported on deck 10's rows 0-7, not required there)" \
    --require offgate_vs_ungated_built --in "$D7C2" --report-rest "$O/${S}_7c2_watch_km3.jsonl"
  STEP_FILES+=(pairs_7c2.tsv seeds_7c2.txt floor_7c/NOTE.txt "${D_COPY#"$REL"/}" "${S}_inputs7c.sha256" identity_7c.txt counters_7c.txt touched_7c.txt)
  finish_step 7c "Dustin's lists: the ${#FP_ID[@]} floor pages (${FP_ID[*]}) replayed on the new deckgym, every game equal on floor.py's per-game summary record but those against t-weezing on deck 10's page (${FLOOR_REPORT%; }), coverage equal, pages equal but for the program and the coverage program; Oct 1's 32 rows x 60 identical on the watch and the old legality_scan, $CNT_OLD7C; the 23 new rows named equal identical (1,380 deals); deck 10 v t-weezing (pairing $TWEEZ7C2 of 23,300,000,000): changed $CH7 of 60 deals (handoff_7c_km3.tsv, to 8c: a named row, never a stop here); the new rows' counters: $CNT_PASS (identity_7c.txt, counters_7c.txt, touched_7c.txt)"
fi

# ---- Done.
STEP=done
pin_note "every check of sitting 1 passed for $C: the candidate (main ${M:0:7} + P ${P:0:7}, engine/ = P's), the plain and watch builds, identity for every pilot (151,240 games), the table's counters (28,000), Dustin's lists in step 7c (20,160; deck 10 v t-weezing's changed games in handoff_7c_km3.tsv for 8c). This start played $PLAYED games and reused $REUSED."
state_line "SITTING 1 DONE $C $(ts)"
FINISHED=1; RECORD=1
}
main "$@"
