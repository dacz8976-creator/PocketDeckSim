#!/usr/bin/env bash
# The rules engine switch, sitting 1: PLAN.md steps 4-7c (Dustin, Sept 30, "Sure go for all 9": a conditional go, "pin
# if all pass"; README.md here). The candidate, the two builds, and the replays and counters that need no carrier list.
# Nothing is pinned and the manifest is not touched. The shared working copy is never checked out, switched, stashed or
# reset, and no engine file is edited: the candidate is made with git merge-tree, commit-tree and update-ref, and the
# checkpoint commits come from a private index (checkpoint.sh). Shape: ../engine_switch_2026-09-30/prepare.sh, with the
# Sept 28 watch build (../engine_switch_2026-09-28/build_watch.sh) and a checkpoint commit and push after every step.
#
#   4  The candidate (no game). After a fetch (at most 5 min; offline, the local objects): the merge of main's HEAD and
#      R = f8cfa9c (on origin/sonnet/rules-fixes; engine/ = ab56bf4's, after the second read's fixes; was 1abdbe8), made without the
#      working copy: git merge-tree --write-tree (a conflict halts), git commit-tree with parents main and R and the final
#      merge message, kept at refs/pocketdecksim/rules-switch-candidate (not a branch: GitHub Desktop does not list it, a
#      push does not send it) and recorded in candidate.txt (made once; a later start checks it and never remakes it).
#      Checks, git only:
#      - R is on origin/sonnet/rules-fixes and cut from cae37a3, whose engine/ is c9df626's; the only commits touching
#        engine/ between cae37a3 and R are F1-F4 and F7's six (8e0622a 160a9d4 d479f01 c476556 0311971 893f9d6);
#      - main's engine/ is the official engine's source (tree 9c84fef, main-d363ba8's);
#      - the candidate's engine/ is R's tree 38af8b0 byte for byte (so Sonnet's suite at R, 2,018 passed, counts);
#      - outside rl/results/ the candidate changes exactly the 9 files of PLAN.md's list (card_validation.rs among
#        them), each one modified, nothing added: actions/apply_action.rs, actions/apply_attack_action.rs, actions/attack_outcome.rs,
#        hooks/core.rs, card_validation.rs, and the tests b4a_attack_batch2_test.rs, victini_victory_star_test.rs,
#        pokemon/hisuian_goodra_securely_sheltered_test.rs, pokemon/meowth_carefree_steps_test.rs. F3's, F4's and F7's
#        test paths are read at R (git diff-tree of c476556, 0311971, 893f9d6) and must be among them (today
#        victini_victory_star_test.rs and b4a_attack_batch2_test.rs: no new test file);
#      - engine/src/players/ and every Cargo.lock unchanged; nothing deleted anywhere;
#      - both F5 instrument_scan.py scripts in the candidate are R's blobs.
#   5  The plain build (no game; Sept 30's took 10 min): one git archive of the candidate (engine/ and decks/) into
#      /home/dacz8976/engine-rules-<short>; cargo build --release --locked of deckgym, examples/legality_scan and
#      examples/goldfish. Their sha256 and the pinned old programs' (rl/engine-2026-09-30/, which must equal its SHA256SUMS
#      and the manifest) go to programs.sha256 and PIN_STATUS.txt, checked before and after every later step (a program
#      that differs halts); a build is never redone after step 5 passed. The references are taken from the candidate (git
#      cat-file, blob-checked) into <build>/ref (<short>_refs.sha256); each of step 7's 15 must have the sha256 recorded
#      when it was played or adopted (REF7 below), and the 4 floor pages' 12 files must be the blobs recorded at 4690810
#      (the km3 pages on d363ba8; a page rewritten on main since would be another baseline). The inputs the games read are recorded (<short>_inputs.sha256): each
#      inside the repository must be the candidate's file, and floor.py must be the blob the floor pages were made with
#      (4690810's).
#   6  The watch build (no game; Sept 28's took 9 min): a second git archive of the candidate in its own folder,
#      /home/dacz8976/engine-rules-watch-<short>; both F5 instrument_scan.py scripts (taken from the candidate,
#      blob-checked) applied to its examples/legality_scan.rs, Victory Star's first, then the coin script (the order of
#      Sonnet's scratch build b7a5fa47); its source must differ from the plain build's in that one file; cargo build
#      --release --locked --example legality_scan. Its sha256 in watch.sha256 and PIN_STATUS.txt; watch_patch.txt says
#      what was patched.
#   7  Identity for every pilot, PLAN.md step 7 exactly (151,240 games; Sept 30's pace about 3.2 h, 4.9 h at 8.6 a
#      second), on the plain legality_scan, each v the recorded games:
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
#   7b The table's counters (28,000 games; ~30-60 min): the watch build plays k3 and kp3 on the 28 cells (--decks, i <
#      500). Every watch game must equal step 7's plain game on every field the plain build records; every repair counter
#      must read 0 in every game. The two off-gate counters (F5's) are evidence for different rewritten lines, so each
#      gets its own verdict: offgate_helper_choice (queued_attack_damage_choice's else branch) must be above 0 in at
#      least one game, condition 3 of the refactor rule (the table runs B's rewritten helpers); offgate_discard_then_damage
#      (discard_then_damage_choice's fall-through, the equivalence readings' rows 13 and 22) is reported, and when it
#      reads 0 the record says that condition 3 for rows 13 and 22 is carried to steps 8 and 8b, not met on the table.
#      counters_7b.txt.
#   7c Dustin's decks whose attackers run B's rewritten helpers: 02 (Absol), 06 (Heatmor), 08 (Gabite), 14 (Team
#      Rocket's Hypno) (11,520 games; ~15-30 min):
#      - plain: each deck's recorded km3 floor page (floor_dustin_2026-09-30/<deck>_games.jsonl, _coverage.json and .md;
#        1,920 games each, on d363ba8) replayed by floor.py's own call (deckgym simulate --seed-stream, its own seeds, and
#        the recorded run's environment: no RAYON_NUM_THREADS) on the new deckgym through floor_with.py: every game equal
#        on every field of floor.py's per-game summary record (a summary, not moves or decisions: the scans below carry
#        those), the coverage byte-equal, the page equal but for its program path (floor_7c/);
#      - watch: the 32 pairings (the 4 decks x the 8 panel lists, km3 v km3, i < 60) through the watch legality_scan and
#        through the pinned old one (rl/engine-2026-09-30/), on the same seeds: identical on every field the old one
#        records; every repair counter 0; offgate_helper_choice above 0 in at least one game of OFFGATE7C, the pairings of
#        02, 06 and 08 against t-altaria, t-hydreigon and t-weezing. Those three lists hold no attacker whose helper B
#        rewrote (HELPERS.md at 1abdbe8; t-weezing's Hoopa ex is AlsoChoiceBenchDamage, which the counter leaves out), and
#        the counter does not record which side fired it, so a firing there is Dustin's own Absol (02), Heatmor (06) or
#        Gabite (08): "the check has to be where the change is". The panel's own helpers (t-blaziken, t-lucario,
#        t-sceptile, t-suicune, t-vespiquen) are step 7b's evidence, not this one's. One line per deck.
#        Seeds: the rules switch's block, 23,100,000,000 + pairing x 10,000 + i, with pairings 40-71 (02: 40-47, 06:
#        48-55, 08: 56-63, 14: 64-71), i < 60, so 23,100,400,000 - 23,100,710,059. Step 8 takes pairings 0-31 and 8b
#        32-35 of the same block (up to 23,100,350,499): no collision. The block is in START_HERE's seed table (a start
#        refuses until the committed START_HERE.md lists 23,100,000,000). pairs_7c.tsv and seeds_7c.txt are committed
#        before any 7c game (and pushed with that checkpoint when the network allows; offline, the games go on).
#        Lines in identity_7c.txt and counters_7c.txt.
#   Then "SITTING 1 DONE <candidate> <time>". identity_check.txt is identity_7.txt + identity_7c.txt and
#   table_counters.txt is counters_7b.txt + counters_7c.txt, rebuilt at every checkpoint. Sitting 2 (steps 8-10) is a
#   separate script; it takes the builds and the candidate from candidate.txt, programs.sha256 and watch.sha256.
#   Games: 151,240 + 28,000 + 11,520 = 190,760.
# Identity (7, 7b, 7c): games matched by (pairing, i), counts asserted (both files hold exactly the expected deals, once
# each), every field the reference records equal (switch_check.py same: moves, decisions, openings, winner_seat, points,
# seed, first_seat, bot_a, bot_b, a, b, a_file, b_file, turns, first_deck_score and the per-game counters); every game is
# the one the command plays (switch_check.py complete); every scan page is free of RULE findings. The checks run from a
# private copy of switch_check.py, sitting1_check.py, floor_with.py and checkpoint.sh made at each start (in /tmp, removed
# at the end); the sha256 of sitting1.sh and of each copy is in the START line. Every start refuses unless sitting1.sh and
# its helpers are committed and unchanged (so the evidence names committed code).
#
# STATUS.txt: a timestamped note per action and these anchored lines, at column 0:
#   SITTING 1 START <time> <short>: ...                   every start
#   STEP <n> DONE <short> <time> <summary>                 a step passed (n = 4, 5, 6, 7, 7b, 7c); then its checkpoint
#   SITTING 1 HALT <time> <short>: step <n>: <why>        a check failed: an identity difference, a missing or extra game,
#                                                          a counter, watch not equal to plain, a RULE finding, a program
#                                                          crash (any exit but a stop signal's), a candidate check, a
#                                                          program, reference, input or evidence file that differs from its
#                                                          record. Nothing later runs. A later start refuses until
#                                                          SITTING1_AFTER_HALT='<written reason>' is set (it is noted).
#   SITTING 1 STOPPED <time> <short>: step <n>: <why>     the script could not carry on (a build, fetch, git or checkpoint
#                                                          failure, a push it may not make, a stop signal, the watchdog's
#                                                          hard stop): not a result; a plain restart resumes at that step.
#                                                          It ends with the untracked files left in this folder.
#   SITTING 1 PAUSED <time> <short>: before step <n>: ... the next step could not finish before the deadline, so it was
#                                                          not started; a plain start (the next evening) resumes there.
#   SITTING 1 DONE <candidate> <time>                      every step passed.
#   HALT, STOPPED, PAUSED and DONE also go to PIN_STATUS.txt; the last line matching ^SITTING 1 (HALT|STOPPED|PAUSED|DONE)
#   is the run's state. These lines never carry the words FAILED or MISMATCH (pin.sh's convention).
#   SITTING 1 NOT PUSHED <time> <short>: <why>            after the record commit, when it could not be made or pushed
#                                                          (left uncommitted; the next start's first checkpoint commits it):
#                                                          main is not origin/main, and a person has to see to it by 7:00 am.
# Checkpoints (checkpoint.sh): after each step passes, its STEP DONE line and its files are committed to main (only this
# folder's paths, from a private index; main moves only if it is where the commit was built) and pushed (fast-forward
# only, after a fetch). Each step's files are listed with their sha256 in step_<n>.sha256 (committed); a later start
# skips a DONE step after checking those, and every checkpoint checks every DONE step's files again before it commits
# them, so a 7:15 am cut loses at most the step in progress. Within that step, a game file completed earlier (synced
# to disk before its .run record names the same program and command) is reused and checked again, as prepare.sh did; a
# kept file that is no longer intact (a power-off?) is moved aside as <name>.*.broken_<stamp> and played again, never a
# halt. A HALT, STOPPED, PAUSED or DONE line is committed and pushed too (STATUS.txt, PIN_STATUS.txt, the timings, the
# check files and, on a HALT, the halted step's files so far; best effort, and a "SITTING 1 NOT PUSHED" line when it
# could not be). The push rules (Dustin: main = origin/main by 7:00 am, and this run pushes only its own commits):
# - a push is only a fast-forward of origin/main, and only of commits this run made (.sitting1.ours) or that the start
#   allowed (unpushed commits that touch only this folder and START_HERE.md: the runner's own);
# - origin/main with commits main lacks, or main carrying another session's unpushed commit (still there a minute
#   later), stops the run (SITTING 1 STOPPED, with what to do): it is never forced, merged or pushed along;
# - an offline fetch or push is noted, the games go on, and the next checkpoint pushes again;
# - past the deadline, a checkpoint's fetch and push get at most a quarter of the time left until the deadline + 30 min.
# The deadline: DEADLINE (default 11:30 UTC = 6:30 am Central daylight time; the next 11:30 after the start). Before each
# step the time it needs is estimated: its games still to play / the measured rate (all games timed so far in
# timing.tsv, or RATE before 2,000 have been) x SAFETY, plus OVERHEAD_MIN; for the builds EST5_MIN and EST6_MIN. A step
# that would end after the deadline is not started: "SITTING 1 PAUSED", committed and pushed, and the run ends cleanly.
# A watchdog backs that up: at HARD_STOP (default the deadline + 20 min, 6:50 am CDT) it stops the group, outside a
# checkpoint, with SITTING 1 STOPPED (also after a laptop sleep: it reads the clock every 20 s). A start between 11:30
# and 21:00 UTC (6:30 am - 4 pm CDT) without an explicit DEADLINE is refused: the default would be the next morning's,
# through the away hours.
# One run at a time: flock on .sitting1.lock (fd 9; the children inherit it, git calls close it).
# Every start refuses (with what to do) when: sitting1.sh or a helper is not committed as it is here; the working copy is
# not on main; START_HERE.md (committed) does not list the 23,100,000,000 block; a git lock file (.git/index.lock,
# .git/refs/heads/main.lock) stays for 15 s; files in this folder are staged in the shared index and differ from the
# working copy (staged entries equal to it, which an interrupted checkpoint leaves, are unstaged and noted);
# origin/main (after a fetch of at most 2 min) has commits main lacks; main carries unpushed commits that are not this
# switch's; the last run halted (SITTING1_AFTER_HALT); it is daytime (above). The flags a power-off can leave
# (.sitting1.ckpt, .sitting1.hardstop) are removed once the lock is held.
# Files written outside this folder: the build folders /home/dacz8976/engine-rules-<short> and engine-rules-watch-<short>,
# the private copies in /tmp, the candidate commit and its ref (once), the objects git merge-tree writes, the checkpoint
# commits on main (pushed), and the shared index's entries for exactly the committed paths (checkpoint.sh; pin.sh does
# the same, and README.md records this exception).
#
# Usage (WSL), after sitting1.sh and its helpers are committed:
#   nohup setsid bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules_2026-10/sitting1.sh" \
#     >> /home/dacz8976/sitting1_rules.log 2>&1 &
#   bash sitting1.sh --dry-run   git checks only: no fetch, build, game, commit or ref (git merge-tree's tree objects
#                                aside), a scratch copy of legality_scan.rs patched in /tmp, and git push --dry-run (no
#                                write) to see that a checkpoint can push
#   bash quiet.sh pause|resume|stop|status    as ../engine_switch_2026-09-30/quiet.sh, for this run's process group
# Knobs (environment): THREADS 14, NICE 10, JOBS 14 (cargo), DEADLINE 11:30 (HH:MM UTC, an ISO time, or off), HARD_STOP
#   auto (the deadline + 20 min; HH:MM UTC, an ISO time, or off), RATE 8.6 (games a second before any is measured),
#   SAFETY 1.25, OVERHEAD_MIN 10, EST5_MIN 40, EST6_MIN 25, SITTING1_AFTER_HALT (above). An input file that changes
#   after step 5 halts (there is no renewal knob: a changed input would not be the candidate's file anyway).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules_2026-10
O="$R/$REL"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[ "$HERE" -ef "$O" ] || { echo "sitting1.sh: run the copy in $O (this one is in $HERE)" >&2; exit 2; }
DRY=0
case "${1:-}" in "") ;; --dry-run) DRY=1;; *) echo "usage: bash sitting1.sh [--dry-run]" >&2; exit 2;; esac
if [ $DRY -eq 0 ] && [ -z "${SITTING1_REEXEC:-}" ] && [ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]; then
  SITTING1_REEXEC=1 exec setsid bash "$O/sitting1.sh" "$@"   # its own process group (quiet.sh and the watchdog act on it)
fi

# ---- The fixed names (Dustin's decision; PLAN.md; the README's carriers do not enter sitting 1).
RC=f8cfa9c1df4bbcfb72a3b9d9b0247b081a1ffd26     # R: sonnet/rules-fixes after the second read's fixes (Sept 30 night; was 1abdbe8)
RBR=origin/sonnet/rules-fixes
RTREE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5  # R's engine/ (ab56bf4's; f8cfa9c changes rl/results/ only)
CAE=cae37a3dfd090160e4cc070c8141b6f9854fbf15    # where R's branch was cut (the cloud branch; A + B + S1-S4)
C9=c9df626dfb09f77e37bd3b430c92dd1f3bf3f885     # the cloud's last engine commit
MAIN_ENGINE=9c84fefd44a4719678415b0e12a717b8ead373a9   # the official engine's source (main-d363ba8's engine/)
PAGES=4690810278b40b490d7c57aee2c7b35ae315ddab   # the commit of the km3 floor pages (floor_dustin_2026-09-30)
F_ENGINE=(8e0622aae03cd24fb0d96ae167e04d836d54b874 160a9d4cbcba79365e99a9bd6fc79594ced3a7dc d479f01aa7a8861c0828d6760524a15e9be732ac
          c4765561ebd2796aaa4f16009500bd1d9d91036d 03119712621da8a870a63084caef914181c516a6 893f9d65bc349ddb7845ce89e4c41c9dda48fee1
          ab56bf4e8475bf6c863e52f49b872eee2fb63616)   # ab56bf4: F7's tests corrected + core.rs comments (the second read, finding 1)
F_TESTS=(c4765561ebd2796aaa4f16009500bd1d9d91036d 03119712621da8a870a63084caef914181c516a6 893f9d65bc349ddb7845ce89e4c41c9dda48fee1)
ALLOWED=(engine/src/actions/apply_action.rs engine/src/actions/apply_attack_action.rs engine/src/actions/attack_outcome.rs
         engine/src/hooks/core.rs engine/src/card_validation.rs engine/tests/b4a_attack_batch2_test.rs
         engine/tests/victini_victory_star_test.rs engine/tests/pokemon/hisuian_goodra_securely_sheltered_test.rs
         engine/tests/pokemon/meowth_carefree_steps_test.rs)
CREF=refs/pocketdecksim/rules-switch-candidate     # not a branch
VS_SCRIPT=rl/results/victory_star_repair_2026-09-30/instrument_scan.py
COIN_SCRIPT=rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py
OLDP="$R/rl/engine-2026-09-30"   # the pinned old programs (main-d363ba8), as SHA256SUMS and the manifest record them
OLD_GYM="$OLDP/deckgym"; OLD_SCAN="$OLDP/legality_scan"; OLD_GOLD="$OLDP/goldfish"
OLD_SHA=("$OLD_GYM" 119389c57de425c55e951de6e14bcbe9811a6cf2861c88c4fa43b6cdb9ccd215
         "$OLD_SCAN" fe244ecd92e159706c1ee0fc9933037e87d885c4a1cb9b4f37ee7adf96067be1
         "$OLD_GOLD" 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073)
PFRESH_T=rl/results/kta_tables_2026-09-29/pairs/fresh_table28.tsv; PFRESH_N=rl/results/kta_tables_2026-09-29/pairs/fresh_new_decks.tsv
PDEV_N=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv
FLOOR_DIR=rl/results/floor_dustin_2026-09-30
FLOOR_DECKS=(02-arceus-crobat 06-mega-blaziken-tournament-list 08-garchomp-toolbox 14-comfey-raticate-hypno)
SEED7C=23100000000; P7C=$(seq -s, 40 71)
# Where 7c's offgate_helper_choice must fire: 02, 06 and 08 against t-altaria, t-hydreigon and t-weezing (the sorted panel's
# lists 0, 2 and 7), whose lists hold no attacker with a rewritten helper (HELPERS.md at 1abdbe8), so only Dustin's Absol,
# Heatmor or Gabite can fire it there.
OFFGATE7C=40,42,47,48,50,55,56,58,63
ALL28=$(seq -s, 0 27); N17=$(seq -s, 8 24)
# Step 7's references and the sha256 each had when its games were played or adopted (a rewrite of one halts):
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
for d in "${FLOOR_DECKS[@]}"; do REFS+=("$FLOOR_DIR/${d}_games.jsonl" "$FLOOR_DIR/${d}_coverage.json" "$FLOOR_DIR/$d.md"); done
# Step 7, one scan per line: name|bot|pairings|deals|deals source|reference|max i|label. k3's and kp3's new-17 files run
# first: played Sept 27 at 9bffbda and never replayed since, they are the only references with no later identity check,
# so a difference there that predates this switch shows after about 35 minutes, not 2.5 hours.
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
SPEC7C=("7c_watch_km3|km3|P7C|60|P7C" "7c_old_km3|km3|P7C|60|P7C")

# ---- Knobs.
DL_GIVEN=${DEADLINE:+1}   # DEADLINE given explicitly (a daytime start needs it)
THREADS=${THREADS:-14}; NICE=${NICE:-10}; JOBS=${JOBS:-14}; DEADLINE=${DEADLINE:-11:30}; HARD_STOP=${HARD_STOP:-auto}
RATE=${RATE:-8.6}; SAFETY=${SAFETY:-1.25}; OVERHEAD_MIN=${OVERHEAD_MIN:-10}; EST5_MIN=${EST5_MIN:-40}; EST6_MIN=${EST6_MIN:-25}
for x in "$THREADS" "$NICE" "$JOBS" "$OVERHEAD_MIN" "$EST5_MIN" "$EST6_MIN"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "sitting1.sh: knob value $x is not a whole number" >&2; exit 2; }
done
for x in "$RATE" "$SAFETY"; do
  [[ $x =~ ^[0-9]+(\.[0-9]+)?$ ]] && awk -v v="$x" 'BEGIN {exit !(v > 0)}' || { echo "sitting1.sh: knob value $x is not a positive number" >&2; exit 2; }
done
to_epoch() {  # spec start-epoch: HH:MM (UTC; the next one after the start), an ISO time, or off (0)
  local s=$1 t d
  case $s in
    off) echo 0;;
    [0-2][0-9]:[0-5][0-9]) d=$(date -u -d "@$2" +%F) && t=$(date -u -d "$d $s" +%s) || return 1
                           [ "$t" -gt "$2" ] || t=$((t + 86400)); echo "$t";;
    *) date -u -d "$s" +%s;;
  esac
}
fmt() { if [ "$1" -gt 0 ]; then date -u -d "@$1" +%FT%TZ; else echo off; fi; }
T0=$(date +%s)
DL=$(to_epoch "$DEADLINE" "$T0") || { echo "sitting1.sh: DEADLINE=$DEADLINE is not HH:MM, an ISO time or off" >&2; exit 2; }
if [ "$HARD_STOP" = auto ]; then if [ "$DL" -gt 0 ]; then HS=$((DL + 1200)); else HS=0; fi
else HS=$(to_epoch "$HARD_STOP" "$T0") || { echo "sitting1.sh: HARD_STOP=$HARD_STOP is not auto, HH:MM, an ISO time or off" >&2; exit 2; }; fi
KNOBS="threads $THREADS, nice $NICE, cargo jobs $JOBS, deadline $(fmt "$DL") ($DEADLINE), hard stop $(fmt "$HS") ($HARD_STOP), rate $RATE before measurement, safety $SAFETY, overhead $OVERHEAD_MIN min, build estimates $EST5_MIN and $EST6_MIN min"

# ---- Notes, stops and the anchored lines.
S=""; C=""; M=""; T=""; STEP=start; FINISHED=0; RECORD=0; LOCKED=0; PLAYED=0; REUSED=0; PRIV=""; WD=""; HALT_FILES=()
HALTED=0; CKPT_ALL=(); DONE_STEPS=(); KEEP_FILES=(); BAD=""; STEP_FILES=(); B=""; W=""; GYM=""; SCAN=""; GOLD=""; WSCAN=""; PIN_GYM=""
PINS="$O/programs.sha256"; WPINS="$O/watch.sha256"; CK="$O/switch_check.py"; CK2="$O/sitting1_check.py"; FW="$O/floor_with.py"
CKPT_OURS="$O/.sitting1.ours"   # the commits this switch's runs made or a start allowed: the only ones a push may carry
export CKPT_OURS
ts() { date -u +%FT%TZ; }
note() { if [ $DRY -eq 1 ]; then echo "$*"; else echo "$(ts) $*" >> "$O/STATUS.txt"; fi; }
pin_note() { if [ $DRY -eq 1 ]; then echo "(PIN_STATUS) $*"; else echo "$(ts) $*" >> "$O/PIN_STATUS.txt"; fi; }
state_line() {  # the anchored line, in both files; a pasted checker's FAILED / MISMATCH reworded (pin.sh stops on them)
  local l=$*
  l=${l//FAILED open or read/missing or unreadable}; l=${l//FAILED/does not match its record}; l=${l//MISMATCH/mismatch}
  if [ $DRY -eq 1 ]; then echo "$l"; else echo "$l" >> "$O/STATUS.txt"; echo "$l" >> "$O/PIN_STATUS.txt"; fi
}
halt() { state_line "SITTING 1 HALT $(ts) ${S:-?}: step $STEP: $*"; FINISHED=1; RECORD=1; HALTED=1; exit 1; }
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
rebuild_combined() {  # identity_check.txt and table_counters.txt from the per-step files there are
  local f; local -a a=() b=()
  for f in identity_7.txt identity_7c.txt; do [ ! -f "$O/$f" ] || a+=("$O/$f"); done
  for f in counters_7b.txt counters_7c.txt; do [ ! -f "$O/$f" ] || b+=("$O/$f"); done
  if [ ${#a[@]} -gt 0 ]; then cat -- "${a[@]}" > "$O/identity_check.txt"; fi
  if [ ${#b[@]} -gt 0 ]; then cat -- "${b[@]}" > "$O/table_counters.txt"; fi
}
ckpt_list() {  # extra REL paths: CF, every file a checkpoint commits now
  local f; CF=()
  for f in STATUS.txt PIN_STATUS.txt timing.tsv identity_check.txt table_counters.txt; do [ ! -f "$O/$f" ] || CF+=("$REL/$f"); done
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
push_lim() {  # max: the seconds a checkpoint's fetch may take (its push gets 3 x); past the deadline, a quarter of the
  local now l=$1  # time left until the deadline + 30 min (7:00 am CDT by default), at least 30 s
  now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ "$now" -ge "$DL" ]; then
    l=$(( (DL + 1800 - now) / 4 )); [ "$l" -le "$1" ] || l=$1; [ "$l" -ge 30 ] || l=30
  fi
  echo "$l"
}
ckpt_msg() {  # title summary
  printf '%s\n' "Rules switch sitting 1, $1 ($REL only)" "" "$2" "" \
    "Candidate ${C:-?} (main ${M:0:7} + R ${RC:0:7}), made off-tree; checkpoint commit by $REL/sitting1.sh" \
    "(PLAN.md steps 4-7c) from a private index. No engine file, no pin, the manifest untouched." "" \
    "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > "$PRIV/ckpt.msg"
}
checkpoint() {  # title summary [extra REL paths]: commit and push; a commit that cannot be made, or a push this run may not
  local title=$1 summary=$2 out push rc=0 prc=0; shift 2  # make (origin/main ahead, or another session's commit on main), stops the run
  done_files || halt "the evidence of $BAD changed since its checkpoint (found before the checkpoint \"$title\"; nothing more is committed)"
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
not_pushed() {  # why: after the record commit, a line in both files (left uncommitted; the next start's first checkpoint commits it)
  state_line "SITTING 1 NOT PUSHED $(ts) ${S:-?}: $*; main $(git -C "$R" rev-parse --short refs/heads/main 9>&- 2> /dev/null), origin/main $(git -C "$R" rev-parse --short refs/remotes/origin/main 9>&- 2> /dev/null) (as last fetched). main must equal origin/main by 7:00 am: a person looks at the reason, then in GitHub Desktop Fetch origin, Pull origin if it offers it, Push origin"
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
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then
    echo "$(ts) sitting1.sh: the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"
    not_pushed "the record commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"; return 0
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
merge_tree() {  # main: MT, the tree of the merge of main and R; a conflict halts
  local out rc=0
  out=$(git -C "$R" merge-tree --write-tree --name-only "$1" "$RC" 9>&-) || rc=$?
  case $rc in
    0) MT=$(head -n 1 <<< "$out");;
    1) halt "the merge of main ${1:0:7} and R ${RC:0:7} has conflicts: $(tail -n +2 <<< "$out" | head -n 20 | tr '\n' ' ')";;
    *) die "git merge-tree failed (exit $rc): $(head -n 3 <<< "$out" | tr '\n' ' ')";;
  esac
  [[ $MT =~ ^[0-9a-f]{40}$ ]] || die "git merge-tree printed no tree"
}
r_checks() {  # [resume]: R's own facts (independent of main). On a resume (the candidate recorded, its second parent R),
  local got want c f p br mode=${1:-}; local -a tests=()  # a branch deleted or rewritten since is a note, not a halt
  git -C "$R" cat-file -e "$RC^{commit}" 2> /dev/null || die "R ${RC:0:7} is not here (fetch origin)"
  if git -C "$R" rev-parse -q --verify "$RBR^{commit}" > /dev/null && git -C "$R" merge-base --is-ancestor "$RC" "$RBR" 2> /dev/null; then
    br="on $RBR (tip $(git -C "$R" rev-parse --short "$RBR"))"
  elif [ "$mode" = resume ]; then
    br="no longer on $RBR (deleted or rewritten since the candidate was made; the candidate's second parent, checked below, pins R)"
  else halt "R ${RC:0:7} is not on $RBR"; fi
  [ "$(git -C "$R" rev-parse "$RC:engine")" = "$RTREE" ] || halt "R's engine/ is not tree ${RTREE:0:7}"
  git -C "$R" merge-base --is-ancestor "$C9" "$CAE" && git -C "$R" merge-base --is-ancestor "$CAE" "$RC" \
    || halt "R is not cut from cae37a3, or cae37a3 does not carry c9df626"
  git -C "$R" diff --quiet "$C9" "$CAE" -- engine || halt "engine/ changed between c9df626 and cae37a3"
  got=$(git -C "$R" log --format=%H "$CAE..$RC" -- engine | LC_ALL=C sort)
  want=$(printf '%s\n' "${F_ENGINE[@]}" | LC_ALL=C sort)
  [ "$got" = "$want" ] || halt "the commits that touch engine/ between cae37a3 and R are not exactly F1-F4 and F7's six plus ab56bf4: $(git -C "$R" log --format=%h "$CAE..$RC" -- engine | tr '\n' ' ')"
  for c in "${F_TESTS[@]}"; do
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      case " ${ALLOWED[*]} " in *" $f "*) ;; *) halt "${c:0:7} (F3, F4 or F7) touches $f, which is not in the plan's file list";; esac
      case $f in engine/tests/*) tests+=("$f");; *) halt "${c:0:7} (F3, F4 or F7) touches $f, not a test";; esac
    done < <(git -C "$R" diff-tree --no-commit-id -r --name-only "$c")
  done
  note "R ${RC:0:7} is $br, cut from cae37a3 (engine/ = c9df626's); the engine commits since are F1-F4 and F7's six plus ab56bf4 (F7's tests corrected, core.rs comments); F3, F4 and F7's tests are in $(printf '%s\n' "${tests[@]}" | LC_ALL=C sort -u | tr '\n' ' ')(both in the plan's list); R's engine/ is tree ${RTREE:0:7}"
}
cand_msg() {  # main tree: the candidate's message (the final merge message)
  cat <<EOF
Merge sonnet/rules-fixes at ${RC:0:7} (R) into main: the rules switch candidate (Dustin, Sept 30: "Sure go for all 9")

Repairs A (Victory Star with a Confused attacker) and B (coin-flip damage prevention and Chase Order), kd's follow-ons
and the fixes F1-F4 and F7 (rl/results/engine_switch_rules_2026-10/PLAN.md). engine/ is R's tree 38af8b0 byte for
byte. Against main ${1:0:7}, the first parent, outside rl/results/ only these change:
$(git -C "$R" diff --name-only "$1" "$2" -- . ':(exclude)rl/results/' | sed 's/^/  /')
engine/src/players/ and Cargo.lock do not. Made off-tree by rl/results/engine_switch_rules_2026-10/sitting1.sh (step 4:
git merge-tree, git commit-tree), which builds and replays this commit; main reaches the rules switch only through the
pin (PLAN.md steps 11-14), after every replay passes and with Dustin's word.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
}
candidate_checks() {  # tree-ish main: step 4's checks on the candidate (in a dry run, the merge tree)
  local c=$1 m=$2 et ns st f n=0 lock del addm; local -a seen=() rmod=()
  [ "$(git -C "$R" rev-parse "$m:engine")" = "$MAIN_ENGINE" ] \
    || halt "main ${m:0:7}'s engine/ is not the official engine's source (tree 9c84fef, main-d363ba8's): the switch's base has moved"
  et=$(git -C "$R" rev-parse "$c:engine") || die "no engine/ in $c"
  [ "$et" = "$RTREE" ] || halt "the candidate's engine/ is tree $et, not R's 38af8b0 exactly; it differs in: $(git -C "$R" diff --name-only "$RC" "$c" -- engine | tr '\n' ' ')(the plan's byte check; this goes to Dustin)"
  ns=$(git -C "$R" diff --no-renames --name-status "$m" "$c" -- . ':(exclude)rl/results/') || die "git diff main..candidate"
  while IFS=$'\t' read -r st f; do
    [ -n "$st" ] || continue
    case " ${ALLOWED[*]} " in *" $f "*) ;; *) halt "outside rl/results/ the candidate changes $f ($st), which PLAN.md does not allow";; esac
    [ "$st" = M ] || halt "the candidate's $f has status $st against main, not M (modified)"
    seen+=("$f")
  done <<< "$ns"
  for f in "${ALLOWED[@]}"; do
    case " ${seen[*]} " in *" $f "*) n=$((n + 1));; *) halt "the candidate does not change $f, which PLAN.md's list names (R is not what the plan describes)";; esac
  done
  git -C "$R" diff --quiet "$m" "$c" -- engine/src/players/ || halt "the candidate changes engine/src/players/"
  lock=$(git -C "$R" diff --name-only "$m" "$c" | grep -E '(^|/)Cargo\.lock$' || true)
  [ -z "$lock" ] || halt "the candidate changes $(tr '\n' ' ' <<< "$lock")"
  del=$(git -C "$R" diff --no-renames --diff-filter=D --name-only "$m" "$c") || die "git diff --diff-filter=D"
  [ -z "$del" ] || halt "the candidate deletes $(head -n 5 <<< "$del" | tr '\n' ' ')"
  for f in "$VS_SCRIPT" "$COIN_SCRIPT"; do
    [ "$(git -C "$R" rev-parse -q --verify "$c:$f" || true)" = "$(git -C "$R" rev-parse "$RC:$f")" ] || halt "the candidate's $f is not R's (F5's script)"
  done
  addm=$(git -C "$R" diff --no-renames --name-status "$m" "$c" -- rl/results/ | cut -f1 | sort | uniq -c | tr -s ' \n' ' ')
  mapfile -t rmod < <(git -C "$R" diff --no-renames --diff-filter=M --name-only "$m" "$c" -- rl/results/)
  note "candidate checks pass: engine/ is R's tree 38af8b0; main ${m:0:7}'s engine/ is 9c84fef (main-d363ba8's); outside rl/results/ exactly the $n files of the plan's list change, each modified; players/ and Cargo.lock unchanged; nothing deleted; both F5 scripts are R's. Under rl/results/ (status counts):$addm; existing files it modifies: ${rmod[*]:-(none)}"
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
REFSUM=""; INPUTS=""
verify_refs() {  # when
  local out
  out=$(cd "$B/ref" && sha256sum -c --quiet --strict -- "$REFSUM" 2>&1) || halt "a reference file differs from ${REFSUM##*/} ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
}
gate_refs() {  # dir when: step 7's references have the sha256 recorded when they were played or adopted
  local x p sha src got
  for x in "${REF7[@]}"; do
    p=${x%%|*}; sha=${x#*|}; src=${sha#*|}; sha=${sha%%|*}
    got=$(sha256sum < "$1/$p" | cut -c1-64) || die "sha256 of $p"
    [ "$got" = "$sha" ] || halt "$p ($2) has sha256 ${got:0:16}.., not ${sha:0:16}.. as $src records it"
  done
}
inputs_rel() {  # the repository's files the games read, relative, sorted (the build's own decks are added by inputs_list)
  local f
  { for f in "$R"/decks/research/*.txt "$R"/decks/screen/opponents/*.txt; do echo "${f#"$R"/}"; done
    for f in "$PFRESH_T" "$PFRESH_N" "$PDEV_N" decks/screen/floor.py lib/brew_pages.py lib/brew_consistency.py \
             lib/deckgym-database.json engine/src/players/public_pricing_player.rs project_manifest.json; do echo "$f"; done
    for f in "${FLOOR_DECKS[@]}"; do echo "decks/dustin/$f.txt"; done
    python3 "$CK" pairs-decks "$R/$PFRESH_T" "$R/$PFRESH_N" "$R/$PDEV_N"
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
blob_check_inputs() {  # tree-ish: every repository input in the working copy is that tree's file; floor.py is the pages'
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
  [ "$(git -C "$R" rev-parse "$1:decks/screen/floor.py")" = "$(git -C "$R" rev-parse "$PAGES:decks/screen/floor.py")" ] \
    || halt "decks/screen/floor.py is not the blob the floor pages were made with (4690810's): a replay would not be floor.py's own call"
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
  note "inputs recorded (before any game): ${#IN[@]} files, ${INPUTS##*/}; the $BLOBS_OK inside the repository equal the candidate's files; floor.py is the floor pages' blob; every step checks them"
}
floor_pages_check() {  # tree-ish: the 4 floor pages' 12 files are the blobs recorded at 4690810 (the km3 pages on d363ba8)
  local d x p a b
  for d in "${FLOOR_DECKS[@]}"; do
    for x in _games.jsonl _coverage.json .md; do
      p="$FLOOR_DIR/$d$x"
      a=$(git -C "$R" rev-parse -q --verify "$1:$p" 9>&- || true); b=$(git -C "$R" rev-parse -q --verify "$PAGES:$p" 9>&- || true)
      [ -n "$b" ] || die "$p is not in 4690810, the floor pages' commit"
      [ "$a" = "$b" ] || halt "$p in ${1:0:7} is ${a:0:7}, not the blob ${b:0:7} recorded at 4690810 (the km3 floor pages on d363ba8): step 7c would replay against another baseline"
    done
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
  note "references taken from the candidate (git cat-file, blob-checked) into $B/ref: ${#REFS[@]} files (step 7's 15, each with the sha256 recorded when it was played or adopted, and the 4 floor pages' games, coverage and page, each the blob recorded at 4690810), ${REFSUM##*/}"
}
old_programs() {  # the pinned old programs equal their SHA256SUMS and the manifest's record
  local k got rec man
  for ((k = 0; k < ${#OLD_SHA[@]}; k += 2)); do
    got=$(sha256sum < "${OLD_SHA[k]}" | cut -c1-64) || halt "${OLD_SHA[k]} is missing"
    rec=$(awk -v n="${OLD_SHA[k]##*/}" '$2 == n {print $1}' "$OLDP/SHA256SUMS")
    [ "$got" = "${OLD_SHA[k+1]}" ] && [ "$rec" = "$got" ] || halt "${OLD_SHA[k]} has sha256 ${got:0:16}.., not ${OLD_SHA[k+1]:0:16}.. (its SHA256SUMS says ${rec:0:16}..)"
  done
  man=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["available_release"]; print(r["sha256"], r["legality_scan_sha256"], r["goldfish_sha256"], r["artifact"], r["legality_scan"], r["goldfish"])' "$R/project_manifest.json") \
    || halt "project_manifest.json cannot be read"
  [ "$man" = "${OLD_SHA[1]} ${OLD_SHA[3]} ${OLD_SHA[5]} rl/engine-2026-09-30/deckgym rl/engine-2026-09-30/legality_scan rl/engine-2026-09-30/goldfish" ] \
    || halt "the manifest's available release is not the Sept 30 programs (main-d363ba8): $man"
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
    P7C) SA=(--pairs "$O/pairs_7c.tsv" --root "$R" --seed-base "$SEED7C");;
    *) die "no deals source $1";;
  esac
}
pl_of() { case $1 in ALL28) echo "$ALL28";; N17) echo "$N17";; P7C) echo "$P7C";; esac; }
cells_of() { case $1 in ALL28) echo 28;; N17) echo 17;; P7C) echo 32;; esac; }
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
ident() {  # outfile label name expect max_i ref...: one line per reference; any difference halts
  local idf=$1 label=$2 name=$3 expect=$4 maxi=$5 r line rc=0; shift 5
  local -a args=(same "$O/$name.jsonl" --expect "$expect" --label "$label")
  [ -z "$maxi" ] || args+=(--max-i "$maxi")
  for r in "$@"; do args+=(--ref "$r"); done
  line=$(python3 "$CK" "${args[@]}") || rc=$?
  echo "$line" >> "$idf"
  case $rc in
    0) note "identity: $(tr '\n' ' ' <<< "$line" | cut -c1-400)";;
    1) halt "IDENTITY: $label differs from its reference (${idf##*/}): $(grep -o 'DIFFERS: .*' <<< "$line" | head -n 2 | tr '\n' ' ')";;
    *) halt "the identity check for $label could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$line")";;
  esac
}
counters_check() {  # outfile label offgate-pairings require-discard(yes|no) files...
  local cf=$1 label=$2 og=$3 rd=$4 out rc=0; shift 4
  local -a args=(counters "$@" --label "$label")
  [ -z "$og" ] || args+=(--offgate-in "$og")
  [ "$rd" != yes ] || args+=(--require-discard)
  out=$(python3 "$CK2" "${args[@]}") || rc=$?
  echo "$out" >> "$cf"
  case $rc in
    0) note "counters: $(tail -n 1 <<< "$out")";;
    1) halt "COUNTERS: $label (${cf##*/}): $(grep -E 'NOT all 0|does not pass' <<< "$out" | head -n 2 | tr '\n' ' ')";;
    *) halt "the counters check for $label could not read its input (exit $rc): $(tail -n 1 <<< "$out")";;
  esac
}
run_floor() {  # deck: floor.py's own call on the new deckgym, then the comparison with the recorded page
  local d=$1 dir="$O/floor_7c" deck="decks/dustin/$1.txt" want rc=0 s secs out x was_kept label
  local -a outs=("${1}_games.jsonl" "${1}_coverage.json" "$1.md" "$1.run" "$1.txt")
  label="7c plain, deck ${d:0:2}: floor.py's own call (seed 7,100, km3 both sides, 240 a matchup; no RAYON_NUM_THREADS, as recorded) on the new deckgym v the recorded km3 floor page, on every field of floor.py's per-game summary record (not moves or decisions)"
  want=$(run_record "$GYM" "$R" "floor.py=$(sha256sum < "$R/decks/screen/floor.py" | cut -c1-64)" \
    "floor_with.py=$(sha256sum < "$FW" | cut -c1-64)" "$deck" --out "$REL/floor_7c")
  while :; do
    if kept "$dir/${d}_games.jsonl" "$dir/$d.run" "$want" && [ -e "$dir/${d}_coverage.json" ] && [ -e "$dir/$d.md" ]; then
      was_kept=1; note "floor $d: kept from an earlier start"
    else
      was_kept=0
      rm -rf -- "$dir/$d.part"; rm -f -- "$dir/${d}_games.jsonl" "$dir/${d}_coverage.json" "$dir/$d.md" "$dir/$d.run"
      mkdir -p -- "$dir/$d.part"
      s=$(date +%s)
      # The recorded run (floor_dustin_2026-09-30/run_floor.sh) set no RAYON_NUM_THREADS, so neither does this (rayon's
      # default, every logical CPU); nice changes no game.
      ( cd "$R" && unset PDL_DB RAYON_NUM_THREADS && nice -n "$NICE" python3 "$FW" "$GYM" "$PIN_GYM" \
          "$R/decks/screen/floor.py" "$deck" --out "$dir/$d.part" ) > "$dir/$d.txt" 2>&1 || rc=$?
      [ $rc -eq 0 ] || stopped_or_failed $rc "floor.py on the new deckgym for $d (see floor_7c/$d.txt)"
      for x in _games.jsonl _coverage.json .md; do [ -s "$dir/$d.part/$d$x" ] || halt "floor.py wrote no $d$x (floor_7c/$d.txt)"; done
      durable "$dir/$d.part/${d}_games.jsonl" "$dir/$d.part/${d}_coverage.json" "$dir/$d.part/$d.md" "$dir/$d.txt"
      mv -- "$dir/$d.part/${d}_coverage.json" "$dir/$d.part/$d.md" "$dir/"; mv -- "$dir/$d.part/${d}_games.jsonl" "$dir/"
      rmdir -- "$dir/$d.part"
      printf '%s\n' "$want" > "$dir/$d.run"   # last: only a complete, synced page gets a record
      secs=$(( $(date +%s) - s )); x=$(grep -c . "$dir/${d}_games.jsonl")
      timing_row "floor_$d" "$x" "$secs" "$GYM"; PLAYED=$((PLAYED + x))
      note "floor $d replayed in $secs s ($x games)"
    fi
    rc=0
    out=$(python3 "$CK2" floor "$dir" "$B/ref/$FLOOR_DIR" "$d" --label "$label") || rc=$?
    if [ $rc -ne 0 ] && [ $was_kept -eq 1 ]; then  # a kept page is replayed once; the replay's comparison decides
      set_aside "floor $d" "$dir" "its comparison with the recorded page did not pass (exit $rc: $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1 | cut -c1-200)$(tail -n 1 <<< "$out" | grep -o 'malformed.*' | cut -c1-200))" "${outs[@]}"
      continue
    fi
    break
  done
  [ $was_kept -eq 0 ] || REUSED=$((REUSED + $(grep -c . "$dir/${d}_games.jsonl")))
  STEP_FILES+=("floor_7c/${d}_games.jsonl" "floor_7c/${d}_coverage.json" "floor_7c/$d.md" "floor_7c/$d.run" "floor_7c/$d.txt")
  echo "$out" >> "$O/identity_7c.txt"
  case $rc in
    0) note "identity: $(cut -c1-400 <<< "$out")";;
    1) halt "IDENTITY: deck $d's floor replay differs from its recorded page (identity_7c.txt): $(grep -o 'DIFFERS: .*' <<< "$out" | head -n 1)";;
    *) halt "the floor comparison for $d could not read its input (exit $rc): $(tail -n 1 <<< "$out")";;
  esac
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
  local x nm bot pl n g=0 d
  case $1 in
    7) for x in "${SPEC7[@]}"; do IFS='|' read -r nm bot pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + $(cells_of "$pl") * n)); done;;
    7b) for x in "${SPEC7B[@]}"; do IFS='|' read -r nm bot pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + $(cells_of "$pl") * n)); done;;
    7c) for d in "${FLOOR_DECKS[@]}"; do [ -e "$O/floor_7c/${d}_games.jsonl" ] || g=$((g + 1920)); done
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
    7c) HALT_FILES=(identity_7c.txt counters_7c.txt pairs_7c.tsv seeds_7c.txt floor_7c/NOTE.txt);;
  esac
  need=$(need_s "$1"); now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ $((now + need)) -gt "$DL" ]; then
    case $1 in 4|5|6) how="the build estimate";; *) how="$(games_left "$1") games at $(rate) games a second x $SAFETY";; esac
    sdone=$(grep -oE "^STEP [0-9a-z]+ DONE $S " "$O/STATUS.txt" 2> /dev/null | cut -d' ' -f2 | tr '\n' ' ' || true)
    state_line "SITTING 1 PAUSED $(ts) ${S:-?}: before step $1: it needs about $((need / 60)) min ($how, plus $OVERHEAD_MIN), so it would end after the deadline $(fmt "$DL"); not started. Steps done: ${sdone:-none }(committed). A plain start, the next evening, resumes at step $1"
    FINISHED=1; RECORD=1; exit 0
  fi
  [ "$1" = 4 ] || [ "$1" = 5 ] || { check_pins "before step $1"; verify_refs "before step $1"; verify_inputs "before step $1"; }
  note "step $1: $2 (about $((need / 60)) min with the overhead; deadline $(fmt "$DL"))"
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
  local c files; FOREIGN=""; ALLOWED_NEW=()  # unpushed ones not yet in .sitting1.ours that touch only this folder and START_HERE.md
  for c in $(git -C "$R" rev-list "$1..$2" 9>&-); do
    if grep -qxF "$c" "$CKPT_OURS" 2> /dev/null; then continue; fi
    files=$(git -C "$R" diff-tree --no-commit-id -r --name-only "$c" 9>&-) || files="?"
    if ! git -C "$R" rev-parse -q --verify "$c^2" > /dev/null 9>&- && ! grep -qvE "^($REL/|START_HERE\\.md\$)" <<< "$files"; then
      ALLOWED_NEW+=("$c")   # the runner's own commit (sitting1.sh, its helpers, the seed row), or a checkpoint a power-off left unrecorded
    else FOREIGN+="${c:0:7} "; fi
  done
}

# ---- The dry run: git checks only.
dry_run() {
  local m o x p sha got n d tmp out t rc=0 nst; local -a stg=()
  STEP=dry; S=dry
  m=$(git -C "$R" rev-parse refs/heads/main); o=$(git -C "$R" rev-parse refs/remotes/origin/main)
  echo "dry run: main ${m:0:7}, origin/main ${o:0:7}, $RBR $(git -C "$R" rev-parse --short "$RBR") (as last fetched; no fetch now)"
  r_checks
  merge_tree "$m"; T=$MT
  echo "dry run: the merge of main ${m:0:7} and R ${RC:0:7} is tree $T, no conflicts"
  candidate_checks "$T" "$m"
  for x in "${REF7[@]}"; do
    p=${x%%|*}; sha=${x#*|}; sha=${sha%%|*}
    got=$(git -C "$R" cat-file blob "$T:$p" | sha256sum | cut -c1-64) || halt "the reference $p is not in the merge tree"
    [ "$got" = "$sha" ] || halt "$p in the merge tree has sha256 ${got:0:16}.., not the recorded ${sha:0:16}.."
  done
  echo "dry run: step 7's 15 references are in the merge tree with the sha256 recorded when they were played or adopted"
  for d in "${FLOOR_DECKS[@]}"; do
    n=$(git -C "$R" cat-file blob "$T:$FLOOR_DIR/${d}_games.jsonl" | grep -c .) || halt "$FLOOR_DIR/${d}_games.jsonl is not in the merge tree"
    git -C "$R" cat-file -e "$T:$FLOOR_DIR/${d}_coverage.json" && git -C "$R" cat-file -e "$T:$FLOOR_DIR/$d.md" || halt "deck $d's floor page is incomplete"
    [ "$n" = 1920 ] || halt "$FLOOR_DIR/${d}_games.jsonl holds $n games, not 1,920"
  done
  floor_pages_check "$T"
  echo "dry run: the 4 floor pages (02, 06, 08, 14) are in the merge tree, 1,920 games each, with their coverage and page; all 12 files are the blobs recorded at 4690810"
  blob_check_inputs "$T"
  echo "dry run: the $BLOBS_OK repository inputs in the working copy equal the merge tree's files; floor.py is 4690810's blob (the pages')"
  old_programs
  echo "dry run: rl/engine-2026-09-30/{deckgym,legality_scan,goldfish} equal their SHA256SUMS and the manifest's available release"
  tmp=$(mktemp -d /tmp/sitting1_dry.XXXXXX)
  git -C "$R" cat-file blob "$T:engine/examples/legality_scan.rs" > "$tmp/legality_scan.rs"
  git -C "$R" cat-file blob "$T:$VS_SCRIPT" > "$tmp/vs.py"; git -C "$R" cat-file blob "$T:$COIN_SCRIPT" > "$tmp/coin.py"
  out=$( (python3 "$tmp/vs.py" "$tmp/legality_scan.rs" && python3 "$tmp/coin.py" "$tmp/legality_scan.rs") 2>&1) || rc=$?
  [ $rc -eq 0 ] || { rm -rf -- "$tmp"; halt "the F5 scripts do not apply to the candidate's legality_scan.rs: $out"; }
  echo "dry run: both F5 scripts apply to the candidate's legality_scan.rs, Victory Star's then the coin script (a scratch copy in /tmp): patched file sha256 $(sha256sum < "$tmp/legality_scan.rs" | cut -c1-16).., $(grep -c 'offgate_\|coin_\|vs_' "$tmp/legality_scan.rs") counter lines"
  out=$(python3 "$CK2" pairs7c --repo "$R" --out "$tmp/pairs_7c.tsv") || { rm -rf -- "$tmp"; halt "pairs7c: $out"; }
  echo "dry run: $out"
  rm -rf -- "$tmp"
  echo "dry run: seeds: step 7 replays the recorded deals (23,000,000,000 and 23,001,000,000 fresh; 72,000,000 table; 21,108,000,000 new cells); 7b the table's 72,000,000; 7c's floor replays seed 7,100 (floor.py's); 7c's scans 23,100,000,000 + pairing x 10,000 + i, pairings 40-71, i < 60"
  [ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] && echo "dry run: the working copy is on main" || echo "dry run: NOTE the working copy is not on main (a start refuses)"
  nst=$(git -C "$R" diff --cached --name-only -- "$REL")
  if [ -z "$nst" ]; then echo "dry run: nothing in $REL is staged in the shared index"
  else
    mapfile -t stg <<< "$nst"
    if git -C "$R" diff --quiet -- "${stg[@]}"; then echo "dry run: NOTE staged in the shared index under $REL, equal to the working copy (a start unstages them): $(tr '\n' ' ' <<< "$nst")"
    else echo "dry run: NOTE staged in the shared index under $REL, and different from the working copy (a start refuses): $(tr '\n' ' ' <<< "$nst")"; fi
  fi
  for x in sitting1.sh checkpoint.sh sitting1_check.py switch_check.py floor_with.py quiet.sh .gitignore; do
    if git -C "$R" ls-files --error-unmatch -- "$REL/$x" > /dev/null 2>&1 && git -C "$R" diff --quiet HEAD -- "$REL/$x"; then t="committed"; else t="NOT committed (a start refuses until it is)"; fi
    echo "dry run: $x: $t"
  done
  if git -C "$R" grep -q -F '23,100,000,000' HEAD -- START_HERE.md; then echo "dry run: START_HERE.md (committed) lists the 23,100,000,000 block"
  elif git -C "$R" grep -q -F '23,100,000,000' -- START_HERE.md; then echo "dry run: NOTE START_HERE.md lists the 23,100,000,000 block in the working copy only: a start refuses until that row is committed (with the runner)"
  else echo "dry run: NOTE START_HERE.md does not list the 23,100,000,000 block: a start refuses until it does (committed)"; fi
  x=$(git_locks); [ -z "$x" ] && echo "dry run: no git lock file (index.lock, refs/heads/main.lock)" || echo "dry run: NOTE git lock file here now: $(tr '\n' ' ' <<< "$x")(a start waits 15 s for it, then refuses)"
  if git -C "$R" merge-base --is-ancestor "$o" "$m"; then
    unpushed_check "$o" "$m"
    echo "dry run: origin/main ${o:0:7} is main or behind it ($(git -C "$R" rev-list --count "$o..$m") unpushed commits; this switch's by its own record or touching only $REL and START_HERE.md: $(( $(git -C "$R" rev-list --count "$o..$m") - $(wc -w <<< "$FOREIGN") )))"
    [ -z "$FOREIGN" ] || echo "dry run: NOTE main carries unpushed commits that are not this switch's: $FOREIGN(a start refuses: this run pushes only its own commits)"
  else echo "dry run: NOTE origin/main ${o:0:7} has commits main lacks: a start refuses (Pull origin first)"; fi
  if [ -z "$DL_GIVEN" ]; then t=$(date -u +%H%M); if [ "$t" -ge 1130 ] && [ "$t" -lt 2100 ]; then echo "dry run: NOTE it is $(date -u +%H:%M) UTC: a start now without an explicit DEADLINE refuses (daytime)"; fi; fi
  rc=0; out=$(GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" push --dry-run --porcelain origin "refs/heads/main:refs/heads/main" 2>&1) || rc=$?
  echo "dry run: git push --dry-run origin main (no write; the credentials): exit $rc, $(grep -E '^[=!*+ -]|^Done|rejected|fatal|error' <<< "$out" | head -n 3 | tr '\n' ' ')"
  echo "dry run: a start now would have the deadline $(fmt "$DL") and the hard stop $(fmt "$HS"); before any game is timed, at $(rate) games a second x $SAFETY + $OVERHEAD_MIN min: step 4 $(( $(need_s 4) / 60 )) min, 5 $(( $(need_s 5) / 60 )), 6 $(( $(need_s 6) / 60 )), 7 $(( $(need_s 7) / 60 )) ($(games_left 7) games), 7b $(( $(need_s 7b) / 60 )) ($(games_left 7b)), 7c $(( $(need_s 7c) / 60 )) ($(games_left 7c))"
  echo "dry run: every check passes (nothing written but git merge-tree's tree objects in .git)"
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
for x in sitting1.sh checkpoint.sh sitting1_check.py switch_check.py floor_with.py quiet.sh .gitignore; do
  if ! git -C "$R" ls-files --error-unmatch -- "$REL/$x" > /dev/null 2>&1 || ! git -C "$R" diff --quiet HEAD -- "$REL/$x"; then
    refuse "$REL/$x is not committed as it is here; commit sitting1.sh and its helpers first (the evidence names committed code)"
  fi
done
[ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] || refuse "the working copy is not on main"
if [ -z "$DL_GIVEN" ]; then
  x=$(date -u +%H%M)
  if [ "$x" -ge 1130 ] && [ "$x" -lt 2100 ]; then
    refuse "it is $(date -u +%H:%M) UTC, daytime: the default deadline is the next 11:30 UTC, so the run would carry on through the away and class hours. At home in the day, give DEADLINE explicitly (HH:MM UTC, an ISO time, or off)"
  fi
fi
git -C "$R" grep -q -F '23,100,000,000' HEAD -- START_HERE.md 9>&- \
  || refuse "START_HERE.md, as committed, does not list the rules switch's seed block 23,100,000,000 (PLAN.md step 8: it goes into the seed table before any game; step 7c is its first use). Commit its row with the runner, then start again"
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
if [ ${#ALLOWED_NEW[@]} -gt 0 ]; then printf '%s\n' "${ALLOWED_NEW[@]}" >> "$CKPT_OURS"; fi
PUSHNOTE="$FETCHED; main ${x:0:7}, origin/main ${LK:0:7}, $(git -C "$R" rev-list --count "$LK..$x" 9>&-) unpushed commits, all this switch's$([ ${#ALLOWED_NEW[@]} -eq 0 ] || echo " (allowed at this start, as they touch only $REL and START_HERE.md: $(printf '%s\n' "${ALLOWED_NEW[@]}" | cut -c1-7 | tr '\n' ' ' | sed 's/ $//'))")"
LOCKED=1
st=$(< "/proc/$$/stat"); st=${st##*) }; read -r -a stf <<< "$st"
echo "$$ $(ts) ${stf[19]}" > "$O/.sitting1.pgid"   # group id, time, the leader's start time (quiet.sh checks it)
trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
[ ! -s "$O/candidate.txt" ] || S=$(sed -n 's/^candidate //p' "$O/candidate.txt" | cut -c1-7)
PRIV=$(mktemp -d /tmp/sitting1_rules.XXXXXX) || { PRIV=""; die "mktemp -d for the private copies"; }
cp -- "$O/switch_check.py" "$O/sitting1_check.py" "$O/floor_with.py" "$O/checkpoint.sh" "$PRIV/" || die "copying the helpers"
CK="$PRIV/switch_check.py"; CK2="$PRIV/sitting1_check.py"; FW="$PRIV/floor_with.py"
# shellcheck source=checkpoint.sh
source "$PRIV/checkpoint.sh"
last=$(grep -E '^SITTING 1 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
case $last in
  "SITTING 1 HALT "*)
    if [ -z "${SITTING1_AFTER_HALT:-}" ]; then
      echo "$(ts) sitting1.sh: start refused: the last run halted ($last). A mismatch stops everything and goes to Dustin first; once it is explained (or a script fault is fixed), start with SITTING1_AFTER_HALT='<written reason>'" >&2
      LOCKED=0; exit 1
    fi
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    echo "SITTING 1 RESUMED AFTER HALT $(ts) ${S:-?}: SITTING1_AFTER_HALT='${SITTING1_AFTER_HALT//$'\n'/ }' (stamp $stamp)" >> "$O/STATUS.txt"
    # The halted run's check files are kept (a step that runs again starts its file afresh) and committed with the next
    # checkpoint, so its DIFFERS lines survive even if the halt's own record commit failed.
    for x in identity_7.txt:7 counters_7b.txt:7b identity_7c.txt:7c counters_7c.txt:7c; do
      f=${x%%:*}; n=${x#*:}
      if [ -s "$O/$f" ] && ! grep -q "^STEP $n DONE ${S:-none} " "$O/STATUS.txt"; then
        mv -- "$O/$f" "$O/${f%.txt}.before_resume_$stamp.txt"; KEEP_FILES+=("$REL/${f%.txt}.before_resume_$stamp.txt")
        echo "$(ts) the halted run's $f is kept as ${f%.txt}.before_resume_$stamp.txt (committed with the next checkpoint); step $n writes $f afresh" >> "$O/STATUS.txt"
      fi
    done;;
  "SITTING 1 DONE "*)
    echo "$(ts) sitting1.sh: SITTING 1 DONE is already recorded ($last); nothing to do" >&2; LOCKED=0; exit 0;;
esac
CODE="sitting1.sh $(sha256sum < "$O/sitting1.sh" | cut -c1-16), checkpoint.sh $(sha256sum < "$PRIV/checkpoint.sh" | cut -c1-16), switch_check.py $(sha256sum < "$CK" | cut -c1-16), sitting1_check.py $(sha256sum < "$CK2" | cut -c1-16), floor_with.py $(sha256sum < "$FW" | cut -c1-16) (sha256; HEAD $(git -C "$R" rev-parse --short HEAD))"
echo "SITTING 1 START $(ts) ${S:-?}: $KNOBS; pid $$; load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $({ ps -C legality_scan,deckgym,tool_census,goldfish,cargo -o pid=,comm= 2> /dev/null || true; } | tr -s ' \n' ' '); code: $CODE (the checks run from private copies made now); git: $PUSHNOTE$UNSTAGED" >> "$O/STATUS.txt"
pin_note "sitting 1 start ${S:-?}: $CODE"
if [ "$HS" -gt 0 ]; then  # the watchdog: past HARD_STOP (read every 20 s, so also after a sleep), outside a checkpoint, TERM to the group
  ( trap - EXIT HUP INT TERM; exec 9>&-
    while sleep 20; do
      [ "$(date +%s)" -ge "$HS" ] || continue
      [ ! -e "$O/.sitting1.ckpt" ] || continue
      : > "$O/.sitting1.hardstop"; kill -TERM -- "-$$" 2> /dev/null; exit 0
    done ) &
  WD=$!
fi

# ---- Step 4: the candidate.
STEP=4
if step_is_done 4 || [ -s "$O/candidate.txt" ]; then  # made at an earlier start: checked, never remade
  C=$(sed -n 's/^candidate //p' "$O/candidate.txt"); M=$(sed -n 's/^main //p' "$O/candidate.txt"); T=$(sed -n 's/^tree //p' "$O/candidate.txt")
  [[ $C =~ ^[0-9a-f]{40}$ && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ ]] || halt "candidate.txt does not hold a candidate, main and tree"
  S=${C:0:7}
  r_checks resume
  merge_tree "$M"
  [ "$MT" = "$T" ] || halt "the merge of main ${M:0:7} and R is now tree $MT, not the recorded $T"
  [ "$(git -C "$R" rev-parse -q --verify "$CREF" || true)" = "$C" ] || halt "$CREF is not the recorded candidate $C"
  [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || halt "the candidate's tree is not the recorded $T"
  [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$RC" ] \
    && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null || halt "the candidate's parents are not main ${M:0:7} and R"
  candidate_checks "$C" "$M"
  if step_is_done 4; then skip_done 4
  else STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + R ${RC:0:7}), made at an earlier start and checked"; fi
elif EX=$(git -C "$R" rev-parse -q --verify "$CREF"); then
  # The ref is here but candidate.txt is not: a start stopped between update-ref and moving candidate.txt into place.
  P=$O/candidate.txt.part
  C=$(sed -n 's/^candidate //p' "$P" 2> /dev/null || true); M=$(sed -n 's/^main //p' "$P" 2> /dev/null || true)
  T=$(sed -n 's/^tree //p' "$P" 2> /dev/null || true)
  why="$CREF exists (${EX:0:7}) but neither candidate.txt nor a matching candidate.txt.part records it: look at it (git log -1 $CREF), then delete it (git update-ref -d $CREF) or restore candidate.txt, and start again"
  [[ $C == "$EX" && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ ]] || die "$why"
  [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$RC" ] \
    && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null && [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || die "$why (its parents or tree differ)"
  merge_tree "$M"
  [ "$MT" = "$T" ] || die "$why (the merge of main ${M:0:7} and R is tree $MT, not $T)"
  [ "$(git -C "$R" cat-file commit "$C" | sed '1,/^$/d')" = "$(cand_msg "$M" "$T")" ] || die "$why (its message is not sitting1.sh's)"
  S=${C:0:7}
  r_checks resume; candidate_checks "$C" "$M"
  durable "$P"; mv -- "$P" "$O/candidate.txt"
  note "candidate $C adopted: $CREF, made by a start that stopped before recording it"
  STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + R ${RC:0:7}), adopted"
else
  begin_step 4 "the candidate: the merge of main and R, off-tree"
  # At most 5 minutes (a stalled network counts as offline), no auto-maintenance, no prompt, without fd 9.
  if GIT_TERMINAL_PROMPT=0 timeout -k 30 300 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then note "fetched origin"
  else
    git -C "$R" cat-file -e "$RC^{commit}" 2> /dev/null || die "git fetch origin failed or timed out and R is not here"
    note "git fetch origin failed or timed out (offline?); R is here, so the candidate is made from the local objects"
  fi
  r_checks
  M=$(git -C "$R" rev-parse refs/heads/main)
  note "main is ${M:0:7} (origin/main $(git -C "$R" rev-parse --short origin/main))"
  merge_tree "$M"; T=$MT
  candidate_checks "$T" "$M"   # on the tree, before any commit is made of it
  C=$(cand_msg "$M" "$T" | git -C "$R" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$T" -p "$M" -p "$RC" -F - 9>&-) \
    || die "git commit-tree failed"
  [[ $C =~ ^[0-9a-f]{40}$ ]] || die "git commit-tree printed no commit"
  S=${C:0:7}
  printf 'candidate %s\nmain %s\nr %s\ntree %s\nengine_tree %s\nmade %s\ncheck engine/ is R'"'"'s tree 38af8b0 byte for byte; against main, outside rl/results/, exactly the %s files of PLAN.md'"'"'s list (card_validation.rs among them) change, each modified; engine/src/players/ and Cargo.lock unchanged; nothing deleted\n' \
    "$C" "$M" "$RC" "$T" "$(git -C "$R" rev-parse "$T:engine")" "$(ts)" "${#ALLOWED[@]}" > "$O/candidate.txt.part"
  durable "$O/candidate.txt.part"
  git -C "$R" update-ref -m "sitting1.sh step 4: the rules switch candidate" "$CREF" "$C" "" 9>&- || die "git update-ref $CREF failed"
  mv -- "$O/candidate.txt.part" "$O/candidate.txt"; durable "$O"
  note "candidate made: $C (merge of main ${M:0:7} and R ${RC:0:7}, tree ${T:0:7}; at $CREF)"
  pin_note "candidate $C: the merge of main ${M:0:7} and R ${RC:0:7} (sonnet/rules-fixes), at $CREF; engine/ tree $(git -C "$R" rev-parse "$C:engine") (R's 38af8b0)"
  STEP_FILES=(candidate.txt); finish_step 4 "candidate $C (main ${M:0:7} + R ${RC:0:7}): engine/ = R's, exactly the plan's ${#ALLOWED[@]} engine files, players/ and Cargo.lock unchanged, no conflict"
fi

# ---- Step 5: the plain build, the references, the inputs.
B=/home/dacz8976/engine-rules-$S; W=/home/dacz8976/engine-rules-watch-$S
[[ $S =~ ^[0-9a-f]{7}$ ]] || die "no candidate short name ($S)"
GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"; GOLD="$B/engine/target/release/examples/goldfish"
WSCAN="$W/engine/target/release/examples/legality_scan"
REFSUM="$O/${S}_refs.sha256"; INPUTS="$O/${S}_inputs.sha256"
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
  for p in "$OLD_SCAN" "$OLD_GOLD" "$OLD_GYM"; do pin_note "sha256 $(prog_sha "$p") rl/engine-2026-09-30/${p##*/} (the pinned old program; SHA256SUMS and the manifest agree)"; done
  mkdir -p "$PRIV"; extract_refs
  write_inputs
  check_pins "after the build"
  STEP_FILES=(programs.sha256 "${S}_refs.sha256" "${S}_inputs.sha256" build.log)
  finish_step 5 "deckgym $(prog_sha "$GYM" | cut -c1-16), legality_scan $(prog_sha "$SCAN" | cut -c1-16), goldfish $(prog_sha "$GOLD" | cut -c1-16) from one archive of $S (cargo --locked); ${#REFS[@]} references blob-checked, step 7's 15 with their recorded sha256, the floor pages' 12 files 4690810's blobs; inputs recorded"
fi
PIN_GYM=$(prog_sha "$GYM")

# ---- Step 6: the watch build.
if step_is_done 6; then
  STEP=6; check_pins "at this start; the watch build of an earlier start"; skip_done 6
else
  # An earlier, unfinished attempt's watch.sha256 goes first (it is in no step manifest until step 6 is DONE): else a
  # start that stopped after its rm -rf of the watch folder would check that old record before step 6 and halt.
  rm -f -- "$WPINS"
  begin_step 6 "the watch build: both F5 instrument_scan.py scripts on legality_scan, in $W"
  rm -rf -- "$W"; mkdir -p "$W"; echo "$C" > "$W/COMMIT"
  git -C "$R" archive "$C" engine decks | tar -x -C "$W" || die "git archive $C engine decks | tar (the watch build)"
  out=$(diff -rq -- "$B/decks" "$W/decks" 2>&1) || halt "the watch build's decks/ differ from the plain build's: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  mkdir -p "$PRIV/f5"
  for f in "$VS_SCRIPT" "$COIN_SCRIPT"; do
    blob=$(git -C "$R" rev-parse "$C:$f"); dst="$PRIV/f5/$(basename "$(dirname "$f")").py"
    git -C "$R" cat-file blob "$blob" > "$dst"
    [ "$(git -C "$R" hash-object --no-filters -- "$dst")" = "$blob" ] && [ "$blob" = "$(git -C "$R" rev-parse "$RC:$f")" ] \
      || halt "$f taken from the candidate is not R's blob"
  done
  WSRC="$W/engine/examples/legality_scan.rs"
  { echo "The watch build of $C ($W), sitting1.sh step 6. The two F5 scripts, taken from the candidate (R's blobs), applied in this order:"
    for f in "$VS_SCRIPT" "$COIN_SCRIPT"; do echo "  $f blob $(git -C "$R" rev-parse "$C:$f") sha256 $(sha256sum < "$PRIV/f5/$(basename "$(dirname "$f")").py" | cut -c1-64)"; done
    echo "engine/examples/legality_scan.rs before: sha256 $(sha256sum < "$WSRC" | cut -c1-64)"
  } > "$O/watch_patch.txt"
  python3 "$PRIV/f5/victory_star_repair_2026-09-30.py" "$WSRC" >> "$O/watch_patch.txt" 2>&1 \
    || halt "Victory Star's F5 script did not apply to legality_scan.rs (watch_patch.txt)"
  python3 "$PRIV/f5/coin_prevention_repair_2026-09-30.py" "$WSRC" >> "$O/watch_patch.txt" 2>&1 \
    || halt "the coin repair's F5 script did not apply to legality_scan.rs (watch_patch.txt)"
  for x in vs_confusion_first_built vs_confused_choice vs_confused_choice_first vs_confused_attack coin_cut_recorded \
           coin_full_prevention coin_queued_offered offgate_helper_choice offgate_discard_then_damage coin_defender_attack \
           coin_queued_attack_damage coin_queued_offered_any vs_confused_choice_chosen vs_confused_choice_offered \
           offgate_helper_by_mechanic; do
    grep -q "\"$x\"" "$WSRC" || halt "the patched legality_scan.rs does not write the counter $x"
  done
  echo "engine/examples/legality_scan.rs after: sha256 $(sha256sum < "$WSRC" | cut -c1-64), $(diff "$B/engine/examples/legality_scan.rs" "$WSRC" | grep -c '^>') lines added, $(diff "$B/engine/examples/legality_scan.rs" "$WSRC" | grep -c '^<') removed; it writes all 15 counters (R = f8cfa9c: every firing tick kept)" >> "$O/watch_patch.txt"
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
  pin_note "watch build of $C in $W: sha256 $(prog_sha "$WSCAN") legality_scan (both F5 scripts; watch_patch.txt)"
  STEP_FILES=(watch.sha256 watch_patch.txt watch_build.log)
  finish_step 6 "watch legality_scan $(prog_sha "$WSCAN" | cut -c1-16) (Victory Star's then the coin F5 script; its source differs from the plain build's in that file only)"
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
  counters_check "$O/counters_7b.txt" "7b the table's counters, k3 and kp3 on the 28 cells (watch build; both off-gate counters required: research/vespiquen's Chase Order discard fires offgate_discard_then_damage, the laptop's second read of R, SECOND_READ_F1_F7_opus.md finding 2)" "" yes "$O/${S}_watch_table_k3.jsonl" "$O/${S}_watch_table_kp3.jsonl"
  STEP_FILES+=(counters_7b.txt)
  x=$(grep -F ": PASS: " "$O/counters_7b.txt" | tail -n 1); x=${x#*: PASS: }; x=${x#*every game: yes; }
  finish_step 7b "the watch build on the 28 cells: k3 and kp3 14,000 each, equal to the plain games on every field; every repair counter 0 in all 28,000 games; $x (each off-gate counter has its own line in counters_7b.txt)"
fi

# ---- Step 7c: Dustin's decks that run B's rewritten helpers.
if step_is_done 7c; then STEP=7c; skip_done 7c
else
  begin_step 7c "Dustin's decks 02, 06, 08, 14: the 4 floor pages replayed (7,680 games) and 32 pairings x 60 on the watch and the old legality_scan (3,840): $(games_left 7c) of 11,520 still to play"
  mkdir -p "$O/floor_7c"
  python3 "$CK2" pairs7c --repo "$R" --out "$PRIV/pairs_7c.tsv" > "$PRIV/pairs7c.raw" || halt "pairs7c: $(cat "$PRIV/pairs7c.raw")"
  sed "s#$PRIV/pairs_7c.tsv#engine_switch_rules_2026-10/pairs_7c.tsv#" "$PRIV/pairs7c.raw" > "$PRIV/pairs7c.out"
  if [ -e "$O/pairs_7c.tsv" ]; then cmp -s -- "$PRIV/pairs_7c.tsv" "$O/pairs_7c.tsv" || halt "pairs_7c.tsv is here but is not what pairs7c writes now (the decks or the panel changed?)"
  else cp -- "$PRIV/pairs_7c.tsv" "$O/pairs_7c.tsv"; fi
  printf '%s\n' "The rules switch's step 7c seeds (sitting1.sh), recorded and committed before any 7c game (pushed with that checkpoint when the network allows)." \
    "$(cat "$PRIV/pairs7c.out")" \
    "Block: 23,100,000,000 + pairing x 10,000 + i (PLAN.md step 8's block, in START_HERE's seed table). Step 8: pairings 0-31; step 8b: 32-35; step 7c: 40-71 (02: 40-47, 06: 48-55, 08: 56-63, 14: 64-71)." \
    "The floor replays use floor.py's own seeds: 7,100 + 1,000 x opponent (seat 0) and + 500 (seat 1), as recorded." > "$O/seeds_7c.txt"
  printf '%s\n' "Replays for the rules switch's step 7c (sitting1.sh): floor.py's own call, unchanged, on the candidate's new deckgym" \
    "(floor_with.py), compared with floor_dustin_2026-09-30's recorded km3 pages. Evidence only: these are not floor pages and" \
    "carry no verdict to use; their '- Engine:' line names the new program, the one difference allowed. The comparison is on" \
    "every field of floor.py's per-game summary record (seed, seat, result, points, turns and the like), not on moves or" \
    "decisions: the 32 scans beside them carry those. Run as floor_dustin_2026-09-30/run_floor.sh ran them: no" \
    "RAYON_NUM_THREADS (rayon's default, every logical CPU: $(nproc 2> /dev/null || echo '?') here); nice $NICE, where the recorded run used 19" \
    "(nice changes no game)." > "$O/floor_7c/NOTE.txt"
  if ! step_is_done 7c-seeds; then
    echo "STEP 7c-seeds DONE $S $(ts) pairs_7c.tsv and seeds_7c.txt recorded before any 7c game" >> "$O/STATUS.txt"
  fi
  checkpoint "step 7c's seeds, before any 7c game" "pairs_7c.tsv: $(cat "$PRIV/pairs7c.out")" "$REL/pairs_7c.tsv" "$REL/seeds_7c.txt" "$REL/floor_7c/NOTE.txt"
  : > "$O/identity_7c.txt"; : > "$O/counters_7c.txt"
  for d in "${FLOOR_DECKS[@]}"; do run_floor "$d"; done
  scan_args P7C
  run_scan "${S}_7c_watch_km3" "$WSCAN" "$W/engine" "$P7C" 60 "${SA[@]}" --bot km3
  run_scan "${S}_7c_old_km3" "$OLD_SCAN" "$B/engine" "$P7C" 60 "${SA[@]}" --bot km3
  ident "$O/identity_7c.txt" "7c watch v the pinned old legality_scan (rl/engine-2026-09-30), km3, decks 02/06/08/14 v the 8 panel lists, i < 60 (seeds 23,100,000,000 + 10,000 x pairing + i, pairings 40-71)" \
    "${S}_7c_watch_km3" 1920 "" "$O/${S}_7c_old_km3.jsonl"
  counters_check "$O/counters_7c.txt" "7c the counters on decks 02/06/08/14 (watch build; offgate_helper_choice needed in pairings $OFFGATE7C: 02, 06 and 08 v t-altaria, t-hydreigon and t-weezing, which hold no rewritten-helper attacker, so only Dustin's Absol, Heatmor or Gabite fire it there; no t-vespiquen pairing is in that scope, so offgate_discard_then_damage is reported, not required, here)" "$OFFGATE7C" no "$O/${S}_7c_watch_km3.jsonl"
  STEP_FILES+=(pairs_7c.tsv seeds_7c.txt floor_7c/NOTE.txt identity_7c.txt counters_7c.txt)
  x=$(grep -F ": PASS: " "$O/counters_7c.txt" | tail -n 1); x=${x#*: PASS: }; x=${x#*every game: yes; }
  finish_step 7c "decks 02, 06, 08, 14: the 4 floor pages replayed on the new deckgym, 1,920 of 1,920 games each equal on floor.py's per-game summary record (coverage equal, pages equal but for the program); the 32 pairings x 60 identical on the watch and the old legality_scan; every repair counter 0; in 02, 06 and 08 v t-altaria, t-hydreigon and t-weezing (Dustin's own attackers only): $x (per deck in counters_7c.txt)"
fi

# ---- Done.
STEP=done
pin_note "every check of sitting 1 passed for $C: the candidate (engine/ = R's), the plain and watch builds, identity for every pilot (151,240 games), the table's counters (28,000), Dustin's decks 02/06/08/14 (11,520). This start played $PLAYED games and reused $REUSED."
state_line "SITTING 1 DONE $C $(ts)"
FINISHED=1; RECORD=1
}
main "$@"
