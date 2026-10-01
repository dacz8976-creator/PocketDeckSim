#!/usr/bin/env bash
# The rules engine switch, sitting 2: PLAN.md steps 8-10 (Dustin, Sept 30, "Sure go for all 9": a conditional go, "pin
# if all pass"; README.md here), on sitting 1's candidate and programs (record b55aad4: "SITTING 1 DONE 5a18d31..."). The
# carrier games, the scratch rows, km3's coverage baselines and the command line, goldfish and screen. Nothing is built,
# nothing is pinned and the manifest is not touched. The shared working copy is never checked out, switched, stashed or
# reset, and no engine file is edited; the checkpoint commits come from a private index (checkpoint.sh, unchanged).
# Derived from sitting1.sh (same framework, refusals, checkpoints, deadline and watchdog), with two of its traps fixed: a
# bare x=$(a | b) whose pipeline can fail in a normal run carries "|| true", and prog_sha reads only records that exist.
#
#   Before any step (a halt if not): candidate.txt names C = 5a18d31 (S = its first 7 characters); STATUS.txt's last
#      sitting 1 state is "SITTING 1 DONE <C>" with STEP 4/5/6/7/7b/7c DONE lines for S; step_4 ... step_7c.sha256 still
#      verify (and again at every checkpoint); the programs are sitting 1's, never rebuilt: B = /home/dacz8976/
#      engine-rules-<S> (deckgym, examples/legality_scan, examples/goldfish) and W = engine-rules-watch-<S> (the watch
#      legality_scan), both COMMIT files C, programs.sha256 and watch.sha256 verify, the pinned old programs
#      rl/engine-2026-09-30/ equal their SHA256SUMS and the manifest. The program checks run again before and after every
#      step (a halt). Sitting 1's references (<S>_refs.sha256, in B/ref) and inputs (<S>_inputs.sha256) are checked once
#      at the start, a NOTE on drift and never a halt: sitting 2 reads none of those files.
#   Inputs and references by step: <S>_inputs2.sha256 holds every file a sitting-2 game reads, in three groups: 8b and
#      8 (pairs_8.tsv's decks), 9 (its pairs files and their decks), 10 (altaria, blaziken, the panel, the two brews,
#      run_screen.py). Before and after a step only its own group is checked (a change halts); at the start a DONE
#      step's group is checked as a NOTE. <S>_refs2.sha256 likewise: step 9's references before and after step 9,
#      step 10's before and after step 10.
#   8-seeds (the plan's 8p; no game): after a fetch (at most 2 min), the coordinator's carriers (README.md here, "The
#      carrier lists") are copied byte for byte from e0d149a into carriers/ at the same paths they have there (git
#      cat-file; each file's blob id checked): garchomp_meowth.txt and alternates/{togekiss_meowth,hisuian_goodra,
#      houndoom_victini}.txt, with the provenance README.md and selection.json. e0d149a's object must be readable and
#      each blob as recorded (else a halt); its membership of origin/claude/pensive-ptolemy-spwc0b is a NOTE. 8b's
#      scratch decks are copied from the candidate into scratch_8b/ the same way (fire_victini, psychic_confuse from
#      victory_star_repair_2026-09-30/smoke/; fire_heatmor, meowth_carefree from coin_prevention_repair_2026-09-30/
#      smoke/). pairs_8.tsv (pairings 0-35; sitting2_check.py pairs8) and seeds_8.txt are written (made again and
#      compared when they are here). <S>_refs2.sha256: step 9's and step 10's references, taken from the candidate into
#      B/ref2 (blob-checked; step 9's six and the goldfish page and coverage also have the sha256 recorded when they were
#      made; run_screen.txt and the 5 command-line outputs are blob-checked, their sha256 recorded now in refs2).
#      <S>_inputs2.sha256 (above): each file the candidate's blob (the carriers: e0d149a's; scratch_8b: the candidate's
#      source files). "STEP 8-seeds DONE" and a checkpoint, before any game.
#   8b The scratch rows (960 games): pairings 32-35 (fire_victini v psychic_confuse, fire_heatmor v meowth_carefree,
#      t-vespiquen v meowth_carefree, l-sharpedo v meowth_carefree), i < 40, km3 then k3, each on the pinned old
#      legality_scan (cwd B/engine, as sitting 1's 7c ran it), the new one (cwd B/engine) and the watch build (cwd
#      W/engine): --pairs pairs_8.tsv --root <repo> --seed-base 23100000000. Per bot: (a) watch equals new on every
#      field new records (switch_check.py same, 160); (b) sitting2_check.py touched: a game whose watch row has every
#      repair counter 0 must equal the old game (a halt otherwise), the changed games are listed with the counters that
#      fired (handoff_8b_<bot>.tsv), and the reach of each counter goes to touched_8b.txt. A RULE finding on an OLD-build
#      page is noted as evidence (the old engine has the bugs the switch repairs); on a new or watch page it halts.
#      Then sitting2_check.py stepsum (into touched_8b.txt and the STEP line): one reach verdict per mechanic (A, B(a),
#      B(b)/Chase Order: "reached in N games (M ticks)" or "UNREACHED", a report: an unreached mechanic rests on its
#      tests); the off-gate discard counter in pairings 34 (Chase Order's discard) and 35 (the Wild Swing control), "met"
#      or "NOT met" each, counted over identical games only (changed games excluded; the refactor rule's condition 3
#      for rows 13 and 22, carried here by sitting 1's 7c); the
#      changed games and those with no reach counter; and "CONDITION 3 (PLAN.md:95: such games must be identical): N
#      games" (changed, coin_full_prevention fired, no reach counter fired): a pin-gate item, never a stop; when N > 0,
#      "a ruling is needed before the pin".
#   8c The gate before step 8 (no game; read after 8b, and again after step 10 when it waited): trace_load.txt here,
#      committed unchanged, read by sitting2_check.py trace-gate ("TRACE LOAD <n> <text naming the cloud commit>", and a
#      "DUSTIN ..." line when n > 50; the checker prints the id it parsed on a marked line "COMMIT <id>", which is
#      checked with git cat-file -e). Optional lines "CLOUD8B <commit> <bot> <path-in-commit>" name the cloud's NEW-build
#      rows for 8b: each is taken with git show and compared with this run's <S>_8b_new_<bot>.jsonl by sitting2_check.py
#      cloud8b (the cloud's rows filtered to the bot, pairings 32-35, i < 40; a_file, b_file and every field the new file
#      lacks left out; not exactly the same 160 deals: "not compared (owed)"; a matched deal that differs halts); without
#      them "8b v the cloud's rows: not compared (owed)". The reading, with the laptop's own 8b count of changed games
#      with no reach counter beside the declared load n, goes to gate_8c.txt, STATUS.txt and PIN_STATUS.txt (its words
#      reworded like an anchored line's). When it passes after 8b, step 8 runs then only if it fits before the deadline;
#      otherwise (or when it waits) steps 9 and 10 run first and the gate is read again; if it then passes and step 8
#      fits, step 8 runs in the same run. Only if it still waits does the run end "SITTING 2 PAUSED ... step 8 waits for
#      8c's trace load"; a later start runs step 8 only.
#   8  The carrier games (72,000 games): pairings 0-31 (the 4 carriers x the 8 panel lists), km3 i < 500 then k3 i <
#      250, each on old, new and watch (in that order), the same checks and stepsum as 8b (16,000 and 8,000 per build);
#      touched_8.txt, handoff_8_<bot>.tsv. Its STEP line carries the real count of changed games and of those with no
#      reach counter (the real trace load, before 8c), the reach verdicts and the CONDITION 3 count.
#      After 8b and 8: handoff_8c.tsv and handoff_8c.md (every changed game; what the cloud and Sonnet need to trace
#      them) and touched_check.txt (touched_8b.txt + touched_8.txt) are rebuilt at every checkpoint.
#   9  km3's coverage baselines (66,500 games) on the new legality_scan, each v its reference in km_tables_2026-09-30
#      (from the candidate, blob-checked, sha256 as recorded): B2e 48,000, Scizor 4,000, the 4 second lists 14,500
#      (SPEC9: checked by hand on Oct 1 against km_config.json:61-80 and run_km.sh part R; the dry run also checks that
#      each reference holds exactly those games, pairings, seed base and bots). Any difference halts (a km3 difference in
#      a coverage replay is never explained by the rules change). identity_9.txt.
#   10 deckgym simulate 240 games for k3, kp3, kog3, kta3 and km3 (from the repository, no RAYON_NUM_THREADS) v
#      engine_switch_2026-09-30/14c39f4_cli_<code>.txt on every line but line 6 (the wall time), with k3 150/90/0, kp3
#      144/96/0, kog3 149/91/0; goldfish --coverage byte-equal to 14c39f4_goldfish.txt and _coverage.json; run_screen
#      under km3 on brew-06 and 06b (screen_with.py, the new deckgym) v floor_recheck_2026-09-30/run_screen.txt.
#      identity_10.txt; the outputs are <S>_10_*.
#   Then "SITTING 2 DONE <C> <time>" (and REPLAYS DONE in PIN_STATUS.txt; the prepare-done mark is not this runner's:
#   it waits for 8c, and the runner never writes those two words, which older scripts grep for anywhere in
#   PIN_STATUS.txt), or, when step 8 still waits for the trace load, "SITTING 2 PAUSED ...". identity_check.txt is rebuilt
#   as identity_7 + 7c + 9 + 10. Games: 960 + 72,000 + 66,500 + 5,040 = 144,500.
# Seeds: 23,100,000,000 + pairing x 10,000 + i (START_HERE's seed table): step 8 pairings 0-31, 8b 32-35 (7c used 40-71).
#
# STATUS.txt (the same file as sitting 1's): a timestamped note per action and these anchored lines, at column 0:
#   SITTING 2 START <time> <S>: ...                       every start
#   STEP <n> DONE <S> <time> <summary>                     n = 8-seeds, 8b, 8, 9, 10; then its checkpoint
#   SITTING 2 HALT <time> <S>: step <n>: <why>            a check failed (an identity difference, a changed game with
#                                                          every repair counter 0, watch not equal to new, a missing or
#                                                          extra game, a RULE finding, a crash, a program, reference,
#                                                          input or evidence file that differs from its record). A later
#                                                          start refuses until SITTING2_AFTER_HALT='<written reason>'.
#   SITTING 2 STOPPED <time> <S>: step <n>: <why>         the script could not carry on (a fetch, git or checkpoint
#                                                          failure, a push it may not make, a stop signal, the hard stop):
#                                                          not a result; a plain restart resumes at that step.
#   SITTING 2 PAUSED <time> <S>: ...                      the next step could not finish before the deadline, or step 8
#                                                          waits for the trace load; a plain start resumes.
#   SITTING 2 DONE <C> <time>                              every step passed.
#   SITTING 2 NOT PUSHED <time> <S>: <why>                after the record commit, when it could not be made or pushed.
#   HALT, STOPPED, PAUSED, DONE and NOT PUSHED also go to PIN_STATUS.txt. The run's state is the last line matching
#   ^SITTING 2 (HALT|STOPPED|PAUSED|DONE) (sitting 1's lines never count). No FAILED or MISMATCH in them (pin.sh's rule).
# Checkpoints, the push rules, the deadline and the watchdog are sitting1.sh's (its header says how), with this run's
# names: commits "Rules switch sitting 2, <title> (rl/results/engine_switch_rules_2026-10 only)"; the commits a push may
# carry in .sitting2.ours; the flags .sitting2.ckpt and .sitting2.hardstop; the lock .sitting2.lock (fd 9). DEADLINE
# default 11:30 UTC (the next one after the start), HARD_STOP auto (the deadline + 10 min, so the record's push ends
# before 7:00 am CDT). Before each checkpoint commit (and the record commit) a fetch (bounded as the push's): when
# origin/main has commits main lacks, nothing is committed and the run stops (SITTING 2 STOPPED, what to do; the record
# is left uncommitted with a NOT PUSHED line), so main never needs a merge.
# Every start refuses (with what to do) when: sitting2.sh or a helper (sitting2_check.py, sitting1_check.py,
# switch_check.py, checkpoint.sh, quiet.sh, .gitignore, ../engine_switch_2026-09-30/screen_with.py) is not committed as
# it is; sitting1.sh's lock is held by a live run (flock -n on .sitting1.lock); the working copy is not on main; the
# committed START_HERE.md does not list the 23,100,000,000 block; a git lock file stays 15 s; files in this folder are
# staged and differ from the working copy; origin/main (after a fetch of at most 2 min) has commits main lacks; main
# carries unpushed commits that are not this switch's (only non-merge commits touching this folder alone are allowed:
# the runner's own commit); the last sitting 2 run halted (SITTING2_AFTER_HALT); it is daytime (11:30-21:00 UTC)
# without an explicit DEADLINE.
# Files written outside this folder: B/ref2 (the references of steps 9 and 10), the private copies in /tmp (removed at
# the end), the checkpoint commits on main (pushed), and the shared index. The shared index is written in two places,
# both inherited from sitting1.sh and recorded in README.md as its one exception: checkpoint.sh sets the entries of
# exactly the committed paths to the new commit's, and a start unstages files of this folder that are staged with the
# working copy's own content (what an interrupted checkpoint leaves; git reset -q -- <those paths>). Nothing else in it
# is touched. The working files .sitting2.* are in .gitignore here (and checkpoint.sh refuses them).
#
# Usage (WSL), after sitting2.sh and its helpers are committed:
#   nohup setsid bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules_2026-10/sitting2.sh" \
#     >> /home/dacz8976/sitting2_rules.log 2>&1 &
#   bash sitting2.sh --dry-run    git and file checks only: no fetch, game, commit or file here; pairs_8.tsv made in
#                                 /tmp from e0d149a's carriers and the candidate's decks, every deck blob checked; the
#                                 trace load read when trace_load.txt is here; git push --dry-run (no write)
#   SITTING=2 bash quiet.sh pause|resume|stop|status   quiet.sh acts on the process group in .sitting2.pgid and waits
#       out .sitting2.ckpt (SITTING=1|2 aware since Oct 1; committed with this runner: a start refuses until it is).
#       This script re-executes itself under setsid, so its group is its own.
# Knobs (environment): THREADS 14, NICE 10, DEADLINE 11:30 (HH:MM UTC, an ISO time, or off), HARD_STOP auto (the
#   deadline + 10 min), RATE 8.6 (games a second before 2,000 are timed in timing.tsv; sitting 1's rows count), SAFETY
#   1.25, OVERHEAD_MIN 10, SITTING2_AFTER_HALT (above).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules_2026-10
O="$R/$REL"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[ "$HERE" -ef "$O" ] || { echo "sitting2.sh: run the copy in $O (this one is in $HERE)" >&2; exit 2; }
DRY=0
case "${1:-}" in "") ;; --dry-run) DRY=1;; *) echo "usage: bash sitting2.sh [--dry-run]" >&2; exit 2;; esac
if [ $DRY -eq 0 ] && [ -z "${SITTING2_REEXEC:-}" ] && [ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]; then
  SITTING2_REEXEC=1 exec setsid bash "$O/sitting2.sh" "$@"   # its own process group (quiet.sh and the watchdog act on it)
fi

# ---- The fixed names.
CAND=5a18d31657897545a9eaaf849c9d0cb5b0a08ffa    # sitting 1's candidate (candidate.txt; main c9f4224 + R f8cfa9c)
RTREE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5   # its engine/ (R's tree)
S1_STEPS=(4 5 6 7 7b 7c)                           # sitting 1's steps: their manifests must still verify
OLDP="$R/rl/engine-2026-09-30"   # the pinned old programs (main-d363ba8), as SHA256SUMS and the manifest record them
OLD_GYM="$OLDP/deckgym"; OLD_SCAN="$OLDP/legality_scan"; OLD_GOLD="$OLDP/goldfish"
OLD_SHA=("$OLD_GYM" 119389c57de425c55e951de6e14bcbe9811a6cf2861c88c4fa43b6cdb9ccd215
         "$OLD_SCAN" fe244ecd92e159706c1ee0fc9933037e87d885c4a1cb9b4f37ee7adf96067be1
         "$OLD_GOLD" 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073)
# The cloud's carrier commit e0d149a (resolved with git rev-parse, Oct 1) and its branch (membership: a note).
E=e0d149a9ee1c8d24a7d59c7c3811bb0258af79b7
EBR=origin/claude/pensive-ptolemy-spwc0b
# The carriers (README.md here: garchomp_meowth plus the three alternates) and their provenance, at the same paths under
# this folder as in e0d149a, with their blob ids there.
CARRIERS=("carriers/garchomp_meowth.txt|ab8af3aee5de2cedac4b972bcf4ab8e5e83cbc2e"
          "carriers/alternates/togekiss_meowth.txt|14af182c3b0fecb75dcd6ee28d011c28e86a5f8f"
          "carriers/alternates/hisuian_goodra.txt|f21212d6ef071322c22bdb1bc0a61639562a8bb6"
          "carriers/alternates/houndoom_victini.txt|e78530111c591a249bfad650781a1890e280c32b"
          "carriers/README.md|f847db3d62db4fc4b5f4c7b5cfbfb1396d33b852"
          "carriers/selection.json|503d8255e403fcb5df7cd5e571ccc4ecba42c5fe")
# 8b's scratch decks: destination under this folder | the candidate's path | blob id.
SCRATCH=("scratch_8b/fire_victini.txt|rl/results/victory_star_repair_2026-09-30/smoke/fire_victini.txt|2589ce563d09eedcf11faa0d7e9f1d5a0d14ddf6"
         "scratch_8b/psychic_confuse.txt|rl/results/victory_star_repair_2026-09-30/smoke/psychic_confuse.txt|cc8e6b8f7bf6bbff0d29a2bb02c22d4ba9e6672f"
         "scratch_8b/fire_heatmor.txt|rl/results/coin_prevention_repair_2026-09-30/smoke/fire_heatmor.txt|b40d1db3415abafed2b98166c4572a757de1dea2"
         "scratch_8b/meowth_carefree.txt|rl/results/coin_prevention_repair_2026-09-30/smoke/meowth_carefree.txt|26815670db336f3d49c642d0ddaf2abf7c00bc64")
SHARPEDO=decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt; SHARPEDO_BLOB=34c28791effe9036451cd4901f97d517052ffc48
SEED8=23100000000; P8=$(seq -s, 0 31); P8B=32,33,34,35
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
HELPERS=(sitting2.sh sitting2_check.py sitting1_check.py switch_check.py checkpoint.sh quiet.sh .gitignore)

# ---- Knobs.
DL_GIVEN=${DEADLINE:+1}   # DEADLINE given explicitly (a daytime start needs it)
THREADS=${THREADS:-14}; NICE=${NICE:-10}; DEADLINE=${DEADLINE:-11:30}; HARD_STOP=${HARD_STOP:-auto}
RATE=${RATE:-8.6}; SAFETY=${SAFETY:-1.25}; OVERHEAD_MIN=${OVERHEAD_MIN:-10}
for x in "$THREADS" "$NICE" "$OVERHEAD_MIN"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "sitting2.sh: knob value $x is not a whole number" >&2; exit 2; }
done
for x in "$RATE" "$SAFETY"; do
  [[ $x =~ ^[0-9]+(\.[0-9]+)?$ ]] && awk -v v="$x" 'BEGIN {exit !(v > 0)}' || { echo "sitting2.sh: knob value $x is not a positive number" >&2; exit 2; }
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
DL=$(to_epoch "$DEADLINE" "$T0") || { echo "sitting2.sh: DEADLINE=$DEADLINE is not HH:MM, an ISO time or off" >&2; exit 2; }
if [ "$HARD_STOP" = auto ]; then if [ "$DL" -gt 0 ]; then HS=$((DL + 600)); else HS=0; fi
else HS=$(to_epoch "$HARD_STOP" "$T0") || { echo "sitting2.sh: HARD_STOP=$HARD_STOP is not auto, HH:MM, an ISO time or off" >&2; exit 2; }; fi
KNOBS="threads $THREADS, nice $NICE, deadline $(fmt "$DL") ($DEADLINE), hard stop $(fmt "$HS") ($HARD_STOP), rate $RATE before measurement, safety $SAFETY, overhead $OVERHEAD_MIN min"

# ---- Notes, stops and the anchored lines.
S=""; C=""; STEP=start; FINISHED=0; RECORD=0; LOCKED=0; PLAYED=0; REUSED=0; PRIV=""; WD=""; HALT_FILES=()
HALTED=0; CKPT_ALL=(); DONE_STEPS=(); KEEP_FILES=(); BAD=""; STEP_FILES=(); B=""; W=""; GYM=""; SCAN=""; GOLD=""; WSCAN=""
PIN_GYM=""; GATE_WHY="not read"; REFSUM=""; INPUTS=""; REFSUM2=""; INPUTS2=""; BLOBS2_OK=0; DRYTMP=""
PINS="$O/programs.sha256"; WPINS="$O/watch.sha256"; CK="$O/switch_check.py"; CK2="$O/sitting1_check.py"; CK3="$O/sitting2_check.py"
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
for x in km3 k3; do for y in old new watch; do SCANS8B+=("8b_${y}_$x"); SCANS8+=("8_${y}_$x"); done; done
rebuild_combined() {  # identity_check.txt, touched_check.txt and the 8c hand-off from the per-step files there are
  local f; local -a a=() t=() h=() j=()
  for f in identity_7.txt identity_7c.txt identity_9.txt identity_10.txt; do [ ! -f "$O/$f" ] || a+=("$O/$f"); done
  for f in touched_8b.txt touched_8.txt; do [ ! -f "$O/$f" ] || t+=("$O/$f"); done
  if [ ${#a[@]} -gt 0 ]; then cat -- "${a[@]}" > "$O/identity_check.txt"; fi
  if [ ${#t[@]} -gt 0 ]; then cat -- "${t[@]}" > "$O/touched_check.txt"; fi
  for f in 8b_km3 8b_k3 8_km3 8_k3; do [ ! -f "$O/handoff_$f.tsv" ] || h+=("$O/handoff_$f.tsv"); done
  if [ ${#h[@]} -gt 0 ] && [ -n "$PRIV" ] && [ -n "$S" ]; then
    for f in "${SCANS8B[@]}" "${SCANS8[@]}"; do [ ! -f "$O/${S}_$f.jsonl" ] || j+=("$O/${S}_$f.jsonl"); done
    if ! python3 "$CK3" handoff --tsv "$O/handoff_8c.tsv" --md "$O/handoff_8c.md" --candidate "$C" --rows "${h[@]}" \
         --files "${j[@]}" > "$PRIV/handoff.out" 2>&1; then
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
  local now l=$1  # time left until the deadline + 30 min (7:00 am CDT by default), at least 30 s
  now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ "$now" -ge "$DL" ]; then
    l=$(( (DL + 1800 - now) / 4 )); [ "$l" -le "$1" ] || l=$1; [ "$l" -ge 30 ] || l=30
  fi
  echo "$l"
}
ckpt_msg() {  # title summary
  printf '%s\n' "Rules switch sitting 2, $1 ($REL only)" "" "$2" "" \
    "Candidate ${C:-?} (sitting 1's; record b55aad4). Checkpoint commit by $REL/sitting2.sh (PLAN.md steps 8-10:" \
    "the carrier lists and seeds before any game, 8b, 8, 9, 10) from a private index. No engine file, no pin, the manifest untouched." "" \
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
    die "$title: nothing committed: $ORIGIN_WHY. Main must equal origin/main by 7:00 am, and the runner never pulls or merges: in GitHub Desktop, Fetch origin, Pull origin, Push origin; then start again (it checks this step's files and commits them with its first checkpoint)"
  fi
  rebuild_combined; ckpt_list "$@"; ckpt_msg "$title" "$summary"
  : > "$O/.sitting2.ckpt"
  out=$(ckpt_commit "$R" "$REL" "$PRIV" "$PRIV/ckpt.msg" "${CF[@]}" 2> "$PRIV/ckpt.err") || rc=$?
  if [ $rc -ne 0 ]; then rm -f -- "$O/.sitting2.ckpt"; die "$title: the checkpoint commit could not be made: $(head -n 3 "$PRIV/ckpt.err" | tr '\n' ' ')"; fi
  push=$(ckpt_push "$R" "$(push_lim 300)" 2> "$PRIV/push.err") || prc=$?
  rm -f -- "$O/.sitting2.ckpt"
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
  local what="Fetch origin, Pull origin if it offers it, Push origin"   # why [uncommitted]
  [ "${2:-}" != uncommitted ] || what="Fetch origin, Pull origin if it offers it; then, in GitHub Desktop, Commit this folder's changed files and Push origin"
  state_line "SITTING 2 NOT PUSHED $(ts) ${S:-?}: $1; main $(git -C "$R" rev-parse --short refs/heads/main 9>&- 2> /dev/null), origin/main $(git -C "$R" rev-parse --short refs/remotes/origin/main 9>&- 2> /dev/null) (as last fetched). main must equal origin/main by 7:00 am: a person looks at the reason, then in GitHub Desktop $what"
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
  push=$(ckpt_push "$R" "$(push_lim 120)" 2> "$PRIV/push.err") || prc=$?   # short: after a hard stop, 7:00 am is near
  if [ $prc -eq 0 ]; then echo "$(ts) sitting2.sh: the record ($last): $out; $push"
  else
    echo "$(ts) sitting2.sh: the record ($last): $out; not pushed: $(push_why)"
    not_pushed "the record is committed ($out) but not pushed: $(push_why)"
  fi
}

# ---- Sitting 1's record, the programs, the references and the inputs.
s1_checks() {  # candidate.txt, sitting 1's state and step lines, its manifests, the candidate commit: C and S
  local c last n out
  [ -s "$O/candidate.txt" ] || halt "candidate.txt is missing (sitting 1 makes it)"
  c=$(sed -n 's/^candidate //p' "$O/candidate.txt")
  [ "$c" = "$CAND" ] || halt "candidate.txt names ${c:-no candidate}, not $CAND (sitting 1's, record b55aad4)"
  C=$c; S=${C:0:7}
  git -C "$R" cat-file -e "$C^{commit}" 9>&- 2> /dev/null || halt "the candidate $C is not in this repository"
  [ "$(git -C "$R" rev-parse "$C:engine" 9>&-)" = "$RTREE" ] || halt "the candidate's engine/ is not R's tree ${RTREE:0:7}"
  last=$(grep -E '^SITTING 1 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
  case $last in "SITTING 1 DONE $C "*) ;; *) halt "sitting 1's last state is not 'SITTING 1 DONE $C' (it is: ${last:-none})";; esac
  for n in "${S1_STEPS[@]}"; do
    grep -q "^STEP $n DONE $S " "$O/STATUS.txt" || halt "STATUS.txt has no 'STEP $n DONE $S' line (sitting 1)"
    [ -s "$O/step_$n.sha256" ] || halt "sitting 1's step_$n.sha256 is missing"
    out=$(cd "$O" && sha256sum -c --quiet --strict -- "step_$n.sha256" 2>&1) \
      || halt "sitting 1's step $n evidence changed since its checkpoint: $(head -n 3 <<< "$out" | tr '\n' ' ')"
  done
}
set_paths() {
  B=/home/dacz8976/engine-rules-$S; W=/home/dacz8976/engine-rules-watch-$S
  GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"; GOLD="$B/engine/target/release/examples/goldfish"
  WSCAN="$W/engine/target/release/examples/legality_scan"
  REFSUM="$O/${S}_refs.sha256"; INPUTS="$O/${S}_inputs.sha256"; REFSUM2="$O/${S}_refs2.sha256"; INPUTS2="$O/${S}_inputs2.sha256"
}
prog_sha() {  # program path: its recorded sha256 (programs.sha256 or watch.sha256; only the records that exist)
  local f fs=()
  for f in "$PINS" "$WPINS"; do [ ! -s "$f" ] || fs+=("$f"); done
  [ ${#fs[@]} -gt 0 ] || return 0
  awk -v p="$1" 'substr($0, 67) == p {print substr($0, 1, 64); exit}' "${fs[@]}"
}
check_pins() {  # when: sitting 1's programs, as recorded (never rebuilt)
  local out p
  [ "$(cat "$B/COMMIT" 2> /dev/null)" = "$C" ] || halt "$B/COMMIT is not the candidate $C ($1)"
  [ "$(cat "$W/COMMIT" 2> /dev/null)" = "$C" ] || halt "$W/COMMIT is not the candidate $C ($1)"
  [ -s "$PINS" ] && [ -s "$WPINS" ] || halt "programs.sha256 or watch.sha256 is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$PINS" 2>&1) || halt "a program differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  out=$(sha256sum -c --quiet --strict -- "$WPINS" 2>&1) || halt "the watch build differs from its record ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  for p in "$GYM" "$SCAN" "$GOLD" "$OLD_SCAN" "$OLD_GYM" "$OLD_GOLD" "$WSCAN"; do
    [ -n "$(prog_sha "$p")" ] || halt "$p has no line in programs.sha256 / watch.sha256 ($1)"
  done
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
group_rel() {  # group pairs_8.tsv: the repository inputs of steps 8b and 8 (8), 9 or 10, relative, sorted
  local f
  case $1 in
    8) python3 "$CK" pairs-decks "$2";;
    9) printf '%s\n' "${P9F[@]}"; python3 "$CK" pairs-decks "${P9F[@]/#/$R/}";;
    10) for f in "$R"/decks/screen/opponents/*.txt; do echo "${f#"$R"/}"; done
        printf '%s\n' "$CLI_P0" "$CLI_P1" "$BREW06" "$BREW06B" decks/screen/run_screen.py;;
  esac | LC_ALL=C sort -u
}
inputs2_rel() {  # pairs_8.tsv: every sitting-2 input, relative, sorted (the three groups)
  { group_rel 8 "$1" && group_rel 9 "$1" && group_rel 10 "$1"; } | LC_ALL=C sort -u
}
inputs2_list() {  # pairs_8.tsv: every sitting-2 input, absolute, sorted
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
  lst=$(group_rel "$g" "$O/pairs_8.tsv" | while IFS= read -r f; do echo "$R/$f"; done) \
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
expected_blob() {  # repository path: the blob it must be (the candidate's; the carriers e0d149a's; scratch_8b the candidate's source)
  local p=$1 x d src b
  case $p in
    "$REL"/carriers/*) git -C "$R" rev-parse -q --verify "$E:$p" 9>&- || true;;
    "$REL"/scratch_8b/*)
      for x in "${SCRATCH[@]}"; do
        IFS='|' read -r d src b <<< "$x"
        [ "$REL/$d" != "$p" ] || { git -C "$R" rev-parse -q --verify "$C:$src" 9>&- || true; }
      done;;
    *) git -C "$R" rev-parse -q --verify "$C:$p" 9>&- || true;;
  esac
}
blob_check_inputs2() {  # root pairs-file: every sitting-2 input under root is the blob it must be: BLOBS2_OK
  local root=$1 i n=0 lst want got; local -a RELS=()
  lst=$(inputs2_rel "$2") || die "listing sitting 2's input files failed"
  mapfile -t RELS <<< "$lst"
  for i in "${RELS[@]}"; do
    [ -f "$root/$i" ] || halt "input file $i is missing"
    want=$(expected_blob "$i")
    [ -n "$want" ] || halt "input $i is in neither the candidate nor the carrier commit"
    got=$(git -C "$R" hash-object --no-filters -- "$root/$i" 9>&-) || die "git hash-object $i"
    [ "$got" = "$want" ] || halt "input $i is ${got:0:7}, not the blob ${want:0:7} it must be (the candidate's; for carriers/ e0d149a's)"
    n=$((n + 1))
  done
  BLOBS2_OK=$n
}
write_inputs2() {
  local lst; local -a IN=()
  blob_check_inputs2 "$R" "$O/pairs_8.tsv"
  lst=$(inputs2_list "$O/pairs_8.tsv") || die "listing sitting 2's inputs"
  mapfile -t IN <<< "$lst"
  sha256sum -- "${IN[@]}" > "$INPUTS2.part" || die "sha256 of sitting 2's input files"
  durable "$INPUTS2.part"; mv -- "$INPUTS2.part" "$INPUTS2"
  note "sitting 2's inputs recorded (before any game): ${#IN[@]} files, ${INPUTS2##*/}; all $BLOBS2_OK are the candidate's blobs (carriers/: e0d149a's; scratch_8b/: the candidate's smoke files); each step checks its own group (8b and 8: pairs_8.tsv's decks; 9: its pairs files and decks; 10: altaria, blaziken, the panel, the brews, run_screen.py) before and after it"
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
E_NOTE=""
e_checks() {  # the carrier commit: readable and holding the recorded blobs (else a halt); on the cloud branch (a note)
  local x p want got
  git -C "$R" cat-file -e "$E^{commit}" 9>&- 2> /dev/null \
    || halt "the carrier commit ${E:0:7} is not readable here (in GitHub Desktop, Fetch origin; if it is still missing, the cloud branch lost it: that goes to the coordinator)"
  if git -C "$R" rev-parse -q --verify "$EBR^{commit}" > /dev/null 9>&- && git -C "$R" merge-base --is-ancestor "$E" "$EBR" 9>&-; then
    E_NOTE="${E:0:7} is on $EBR (tip $(git -C "$R" rev-parse --short "$EBR" 9>&-), as last fetched)"
  else E_NOTE="NOTE ${E:0:7} is not on $EBR as last fetched (rewritten, or not fetched); its object is here and every blob is checked, so the copies stand"; fi
  for x in "${CARRIERS[@]}"; do
    p=${x%%|*}; want=${x#*|}
    got=$(git -C "$R" rev-parse -q --verify "$E:$REL/$p" 9>&- || true)
    [ "$got" = "$want" ] || halt "$REL/$p in ${E:0:7} is ${got:-missing}, not the recorded blob ${want:0:7}"
  done
}
scratch_checks() {  # 8b's scratch decks and l-sharpedo in the candidate are the recorded blobs
  local x d src want got
  for x in "${SCRATCH[@]}"; do
    IFS='|' read -r d src want <<< "$x"
    got=$(git -C "$R" rev-parse -q --verify "$C:$src" 9>&- || true)
    [ "$got" = "$want" ] || halt "$src in the candidate is ${got:-missing}, not the recorded blob ${want:0:7}"
  done
  got=$(git -C "$R" rev-parse -q --verify "$C:$SHARPEDO" 9>&- || true)
  [ "$got" = "$SHARPEDO_BLOB" ] || halt "$SHARPEDO in the candidate is ${got:-missing}, not ${SHARPEDO_BLOB:0:7}"
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
      note "EVIDENCE, not a stop: the pinned OLD legality_scan's page for $name lists RULE findings ($out): the old engine (main-d363ba8) has the bugs the switch repairs; the new and watch pages of the same deals must have none"
      pin_note "$name (the pinned old legality_scan): RULE findings noted as evidence of the old engine: $(reword "$out")"
    else halt "RULE FINDING or an incomplete page: $out"; fi
  fi
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
touched_check() {  # step bot expect outfile: sitting2_check.py touched on the bot's old, new and watch scans
  local st=$1 bot=$2 n=$3 tf=$4 out rc=0 hf="handoff_$1_$2.tsv"
  STEP_FILES+=("$hf")
  out=$(python3 "$CK3" touched --old "$O/${S}_${st}_old_$bot.jsonl" --new "$O/${S}_${st}_new_$bot.jsonl" \
        --watch "$O/${S}_${st}_watch_$bot.jsonl" --expect "$n" --step "$st" --bot "$bot" --repo "$R" --out-handoff "$O/$hf" \
        --label "$st $bot, old v new v watch (the pinned old legality_scan, the new one, the watch build)") || rc=$?
  echo "$out" >> "$tf"
  case $rc in
    0) note "touched: $(tail -n 1 <<< "$out" | cut -c1-400)";;
    1) halt "TOUCHED: $st $bot (${tf##*/}): $(grep -F 'does not pass' <<< "$out" | tail -n 1 | cut -c1-700)";;
    *) halt "the touched check for $st $bot could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$out")";;
  esac
}
carrier_set() {  # step bot pairings deals: the bot's scans on the old, new and watch builds, then checks (a) and (b)
  local st=$1 bot=$2 pl=$3 n=$4 exp tf="$O/touched_$1.txt"; local -a SA
  exp=$(( $(tr ',' '\n' <<< "$pl" | grep -c .) * n ))
  SA=(--pairs "$O/pairs_8.tsv" --root "$R" --seed-base "$SEED8")
  run_scan "${S}_${st}_old_$bot" "$OLD_SCAN" "$B/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
  run_scan "${S}_${st}_new_$bot" "$SCAN" "$B/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
  run_scan "${S}_${st}_watch_$bot" "$WSCAN" "$W/engine" "$pl" "$n" "${SA[@]}" --bot "$bot"
  ident "$tf" "$st watch v new, $bot, pairings $pl, i < $n (seeds 23,100,000,000 + 10,000 x pairing + i)" \
    "${S}_${st}_watch_$bot" "$exp" "" "$O/${S}_${st}_new_$bot.jsonl"
  touched_check "$st" "$bot" "$exp" "$tf"
}
SUM=""
step_summary() {  # step: sitting2_check.py stepsum over both bots into touched_<step>.txt; SUM, its summary line
  local st=$1 out rc=0
  out=$(python3 "$CK3" stepsum --step "$st" --watch "$O/${S}_${st}_watch_km3.jsonl" "$O/${S}_${st}_watch_k3.jsonl" \
        --rows "$O/handoff_${st}_km3.tsv" "$O/handoff_${st}_k3.tsv") || rc=$?
  echo "$out" >> "$O/touched_$st.txt"
  [ $rc -eq 0 ] || halt "the step summary of $st could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$out")"
  SUM=$(grep '^SUMMARY: ' <<< "$out" | tail -n 1 | sed 's/^SUMMARY: //' || true)
  note "step $st's summary: $SUM"
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
    8b) for x in "${SCANS8B[@]}"; do [ -e "$O/${S}_$x.jsonl" ] || g=$((g + 160)); done;;
    8) for x in "${SCANS8[@]}"; do
         case $x in *_km3) y=16000;; *) y=8000;; esac
         [ -e "$O/${S}_$x.jsonl" ] || g=$((g + y))
       done;;
    9) for x in "${SPEC9[@]}"; do IFS='|' read -r nm pf sb pl n _ <<< "$x"; [ -e "$O/${S}_$nm.jsonl" ] || g=$((g + n)); done;;
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
    8-seeds) HALT_FILES=(pairs_8.tsv seeds_8.txt);; 8b) HALT_FILES=(touched_8b.txt);; 8) HALT_FILES=(touched_8.txt);;
    9) HALT_FILES=(identity_9.txt);; 10) HALT_FILES=(identity_10.txt);;
  esac
  need=$(need_s "$1"); now=$(date +%s)
  if [ "$DL" -gt 0 ] && [ $((now + need)) -gt "$DL" ]; then
    case $1 in 8-seeds) how="a fetch and the extractions";; *) how="$(games_left "$1") games at $(rate) games a second x $SAFETY";; esac
    sdone=$(done_list)
    state_line "SITTING 2 PAUSED $(ts) ${S:-?}: before step $1: it needs about $((need / 60)) min ($how, plus $OVERHEAD_MIN), so it would end after the deadline $(fmt "$DL"); not started. Steps done: ${sdone:-none }(committed). A plain start, the next evening, resumes at step $1"
    FINISHED=1; RECORD=1; exit 0
  fi
  check_pins "before step $1"; old_programs; step_io "$1" "before step $1" halt
  note "step $1: $2 (about $((need / 60)) min with the overhead; deadline $(fmt "$DL"))"
}

# ---- Step 8c's gate and step 10's parts.
run_step8() {  # step 8, once 8c's gate has passed (after 8b, or again after step 10): the carrier games
  begin_step 8 "the carrier games: pairings 0-31, km3 i < 500 then k3 i < 250, each on the old, new and watch legality_scan: $(games_left 8) of 72,000 games still to play"
  : > "$O/touched_8.txt"
  carrier_set 8 km3 "$P8" 500
  carrier_set 8 k3 "$P8" 250
  step_summary 8
  STEP_FILES+=(touched_8.txt)
  finish_step 8 "the carrier games (pairings 0-31; km3 16,000 and k3 8,000 per build): watch equal to new on every field; every game with all repair counters 0 equal to the old game; the real trace load before 8c: $SUM (touched_8.txt; every changed game in handoff_8c.tsv for 8c)"
}
CLOUD_LINE=""
cloud8b_same() {  # bot file label: sitting2_check.py cloud8b, this run's 8b NEW-build rows v the cloud's (filtered to the
  local bot=$1 file=$2 label=$3 rc=0  # bot, pairings 32-35, i < 40; paths and fields the new file lacks left out). A
  CLOUD_LINE=$(python3 "$CK3" cloud8b --new "$O/${S}_8b_new_$bot.jsonl" --cloud "$file" --bot "$bot" \
         --label "8b new $bot (pairings 32-35, i < 40) v the cloud's NEW-build rows, $label") || rc=$?   # matched deal that
  echo "$CLOUD_LINE" >> "$O/gate_8c.txt"   # differs halts; returns 3 when not compared (owed). Never call it in $(...)
  case $rc in
    0) return 0;;
    1) halt "CLOUD 8B: this run's 8b new $bot differs from the cloud's NEW-build rows ($label; gate_8c.txt): $(grep -o 'DIFFERS: .*' <<< "$CLOUD_LINE" | head -n 1 | cut -c1-400)";;
    *) return 3;;
  esac
}
gate_8c() {  # GATE_WHY: empty when step 8 may run; else why it waits. The reading goes to gate_8c.txt, STATUS.txt and
  local f="$O/trace_load.txt" out="" rd="" rc=0 cid="" cmsg="" cl tag cc cb cp rest l8b n="" line  # PIN_STATUS.txt (reworded)
  echo "== 8c's gate, read at $(ts) (sitting2.sh)" >> "$O/gate_8c.txt"
  if [ ! -e "$f" ]; then GATE_WHY="trace_load.txt is not here"
  elif ! git -C "$R" ls-files --error-unmatch -- "$REL/trace_load.txt" > /dev/null 2>&1 9>&- \
       || ! git -C "$R" diff --quiet HEAD -- "$REL/trace_load.txt" 9>&-; then
    GATE_WHY="trace_load.txt is here but not committed as it is (commit it first: the gate reads committed words only)"
  else
    out=$(python3 "$CK3" trace-gate "$f") || rc=$?
    rd=$(head -n 1 <<< "$out")                                       # the reading; then the marked lines LOAD and COMMIT
    n=$(sed -n 's/^LOAD \([0-9][0-9]*\)$/\1/p' <<< "$out" | head -n 1)
    cid=$(sed -n 's/^COMMIT \([0-9a-f]*\)$/\1/p' <<< "$out" | head -n 1)
    case $rc in 0) GATE_WHY="";; 3) GATE_WHY=${rd#trace load: step 8 waits: };; *) GATE_WHY="the trace-gate check failed (exit $rc): $rd";; esac
    if [ -z "$GATE_WHY" ] && { [ -z "$cid" ] || ! git -C "$R" cat-file -e "$cid^{commit}" 9>&- 2> /dev/null; }; then
      GATE_WHY="the cloud commit ${cid:-(none marked)} that trace_load.txt names is not here (git cat-file -e; in GitHub Desktop, Fetch origin)"
    fi
    # The optional cross-check of 8b: CLOUD8B <commit> <bot> <path-in-commit>, the cloud's NEW-build rows (pairings 32-35, i < 40).
    cl=$(sed '1s/^\xEF\xBB\xBF//' "$f" | tr -d '\r' | grep -E '^CLOUD8B( |$)' || true)
    if [ -z "$cl" ]; then cmsg="8b v the cloud's rows: not compared (owed)"
    else
      while IFS=' ' read -r tag cc cb cp rest; do
        if ! [[ $cc =~ ^[0-9a-f]{7,40}$ && $cb =~ ^(km3|k3)$ && -n $cp && -z $rest ]]; then
          cmsg+="a CLOUD8B line is not 'CLOUD8B <commit> <km3|k3> <path>': not compared (owed); "
        elif ! git -C "$R" cat-file -e "$cc^{commit}" 9>&- 2> /dev/null; then
          cmsg+="8b $cb v the cloud's rows: commit $cc is not here (Fetch origin): not compared (owed); "
        elif ! git -C "$R" show "$cc:$cp" > "$PRIV/cloud8b_$cb.jsonl" 2> /dev/null 9>&-; then
          cmsg+="8b $cb v the cloud's rows: $cp is not in $cc: not compared (owed); "
        elif cloud8b_same "$cb" "$PRIV/cloud8b_$cb.jsonl" "$cc:$cp"; then
          cmsg+="8b $cb v the cloud's rows ($cc:$cp): $(grep -oE '[0-9]+ of [0-9]+ deals equal on the [0-9]+ fields both record' <<< "$CLOUD_LINE" || true); "
        else cmsg+="8b $cb v the cloud's rows ($cc:$cp): $(grep -o 'not compared (owed): .*' <<< "$CLOUD_LINE" | head -n 1 | cut -c1-250 || true); "; fi
      done <<< "$cl"
      cmsg=${cmsg%; }
    fi
  fi
  l8b=$(grep '^SUMMARY: ' "$O/touched_8b.txt" 2> /dev/null | tail -n 1 | grep -oE 'changed [0-9]+ of [0-9]+ deals \([0-9]+ with no reach counter\)' || true)
  line="the laptop's own 8b: ${l8b:-no count (touched_8b.txt has no summary)}; the cloud's declared trace load: ${n:-none read}"
  [ -n "$cmsg" ] || cmsg="8b v the cloud's rows: not compared (owed; trace_load.txt not read)"   # (no apostrophe inside ${:-})
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
  local c files; FOREIGN=""; ALLOWED_NEW=()  # unpushed non-merge ones not yet in .sitting2.ours that touch only this folder
  for c in $(git -C "$R" rev-list "$1..$2" 9>&-); do
    if grep -qxF "$c" "$CKPT_OURS" 2> /dev/null; then continue; fi
    files=$(git -C "$R" diff-tree --no-commit-id -r --name-only "$c" 9>&-) || files="?"
    if ! git -C "$R" rev-parse -q --verify "$c^2" > /dev/null 9>&- && ! grep -qvE "^$REL/" <<< "$files"; then
      ALLOWED_NEW+=("$c")   # the runner's own commit (sitting2.sh, its helpers), or a checkpoint a power-off left unrecorded
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
  local m o x p sha got n d src want tmp out t rc=0 nst lst; local -a stg=() lp=()
  STEP=dry; S=dry
  m=$(git -C "$R" rev-parse refs/heads/main); o=$(git -C "$R" rev-parse refs/remotes/origin/main)
  echo "dry run: main ${m:0:7}, origin/main ${o:0:7}, $EBR $(git -C "$R" rev-parse --short "$EBR" 2> /dev/null || echo '(none)') (as last fetched; no fetch now)"
  s1_checks; set_paths
  echo "dry run: candidate.txt names $C; sitting 1's last state is SITTING 1 DONE $C; STEP 4/5/6/7/7b/7c DONE for $S; step_4 ... step_7c.sha256 verify"
  check_pins "the dry run"; old_programs
  echo "dry run: the programs are sitting 1's: $B and $W (COMMIT $S), programs.sha256 and watch.sha256 verify; rl/engine-2026-09-30/ equals its SHA256SUMS and the manifest"
  s1_records
  echo "dry run: $S1REC (checked once at a start, a note either way)"
  for x in 8b 9 10; do
    if step_is_done "$x"; then step_io "$x" "the dry run" note; echo "dry run: step $x is DONE: its inputs and references checked as a note (any drift is a NOTE line above)"; fi
  done
  e_checks
  echo "dry run: ${E:0:7} is readable here and its carriers/ holds the recorded blobs: $(for x in "${CARRIERS[@]}"; do printf '%s %s; ' "${x%%|*}" "$(cut -c1-7 <<< "${x#*|}")"; done)$E_NOTE"
  scratch_checks
  echo "dry run: the candidate holds 8b's scratch decks and l-sharpedo as recorded: $(for x in "${SCRATCH[@]}"; do IFS='|' read -r d src want <<< "$x"; printf '%s %s; ' "${d#scratch_8b/}" "${want:0:7}"; done)l-sharpedo ${SHARPEDO_BLOB:0:7}"
  for x in "${CARRIERS[@]}" "${SCRATCH[@]}"; do
    p=${x%%|*}
    if [ -e "$O/$p" ]; then echo "dry run: NOTE $REL/$p is here already (step 8-seeds checks it is the recorded blob)"; fi
  done
  DRYTMP=$(mktemp -d /tmp/sitting2_dry.XXXXXX); tmp=$DRYTMP   # removed on exit, a halt included
  for x in "${CARRIERS[@]}"; do p=${x%%|*}; mkdir -p "$tmp/root/$REL/$(dirname "$p")"; git -C "$R" cat-file blob "${x#*|}" > "$tmp/root/$REL/$p"; done
  for x in "${SCRATCH[@]}"; do IFS='|' read -r d src want <<< "$x"; mkdir -p "$tmp/root/$REL/scratch_8b"; git -C "$R" cat-file blob "$want" > "$tmp/root/$REL/$d"; done
  mkdir -p "$tmp/root/decks/screen/opponents" "$tmp/root/$(dirname "$SHARPEDO")" "$tmp/root/decks/research" "$tmp/root/decks/brews"
  cp -- "$R"/decks/screen/opponents/*.txt "$tmp/root/decks/screen/opponents/"; cp -- "$R/$SHARPEDO" "$tmp/root/$SHARPEDO"
  out=$(python3 "$CK3" pairs8 --repo "$tmp/root" --out "$tmp/pairs_8.tsv" --seeds-out "$tmp/seeds_8.txt") || { rm -rf -- "$tmp"; halt "pairs8: $out"; }
  echo "dry run: $out"
  lst=$(python3 "$CK" pairs-decks "$tmp/pairs_8.tsv") || { rm -rf -- "$tmp"; halt "pairs-decks on the dry run's pairs_8.tsv"; }
  mapfile -t lp <<< "$lst"; n=0
  for p in "${lp[@]}"; do
    want=$(expected_blob "$p"); got=$(git -C "$R" hash-object --no-filters -- "$tmp/root/$p")
    [ -n "$want" ] && [ "$got" = "$want" ] || { rm -rf -- "$tmp"; halt "the dry run's deck $p is ${got:0:7}, not ${want:-nothing}"; }
    grep -qF "  $p $got" "$tmp/seeds_8.txt" || { rm -rf -- "$tmp"; halt "seeds_8.txt does not list $p with its blob $got"; }
    n=$((n + 1))
  done
  echo "dry run: pairs_8.tsv's $n deck files are the blobs they must be (carriers e0d149a's, scratch decks and the panel the candidate's), and seeds_8.txt lists each with its blob id; the panel lists and l-sharpedo in the working copy are the candidate's"
  echo "dry run: pairs_8.tsv rows 0, 31, 32 and 35: $(sed -n '2p;33p;34p;37p' "$tmp/pairs_8.tsv" | cut -f1,3,5,7,8 | tr '\t' ' ' | tr '\n' ';')"
  for f in pairs_8.tsv seeds_8.txt; do
    if [ -e "$O/$f" ]; then cmp -s -- "$tmp/$f" "$O/$f" && echo "dry run: $f is here and equals what pairs8 writes" || echo "dry run: NOTE $f is here and differs from what pairs8 writes (step 8-seeds would halt)"; fi
  done
  cp -- "$R/$CLI_P0" "$R/$CLI_P1" "$tmp/root/decks/research/"; cp -- "$R/$BREW06" "$R/$BREW06B" "$tmp/root/decks/brews/"
  cp -- "$R/decks/screen/run_screen.py" "$tmp/root/decks/screen/"
  for x in "${P9F[@]}"; do mkdir -p "$tmp/root/$(dirname "$x")"; cp -- "$R/$x" "$tmp/root/$x"; done
  lst=$(python3 "$CK" pairs-decks "${P9F[@]/#/$R/}") || { rm -rf -- "$tmp"; halt "pairs-decks on step 9's pairs files"; }
  while IFS= read -r p; do mkdir -p "$tmp/root/$(dirname "$p")"; cp -- "$R/$p" "$tmp/root/$p"; done <<< "$lst"
  blob_check_inputs2 "$tmp/root" "$tmp/pairs_8.tsv"
  echo "dry run: sitting 2's $BLOBS2_OK repository inputs (pairs_8.tsv's decks, step 9's pairs files and their $(grep -c . <<< "$lst") decks, altaria and blaziken, the panel, the two brews, run_screen.py) are the blobs they must be; by step: 8b and 8 $(group_rel 8 "$tmp/pairs_8.tsv" | grep -c .), 9 $(group_rel 9 "$tmp/pairs_8.tsv" | grep -c .), 10 $(group_rel 10 "$tmp/pairs_8.tsv" | grep -c .) files"
  rm -rf -- "$tmp"
  for x in rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs \
           "$REL/tightened_rule.py" "$REL/coin_probe.rs" "$REL/coin_lookahead.py"; do
    git -C "$R" cat-file -e "$C:$x" 2> /dev/null || echo "dry run: NOTE $x, which handoff_8c.md names at the candidate, is not in it"
  done
  echo "dry run: the hand-off's tracer, probes and classifier (vs_trace.rs, vs_probe.rs, tightened_rule.py, coin_probe.rs, coin_lookahead.py) checked at the candidate"
  for x in "${REFS2[@]}"; do
    p=${x%%|*}; sha=${x#*|}
    got=$(git -C "$R" cat-file blob "$C:$p" 2> /dev/null | sha256sum | cut -c1-64) || true
    git -C "$R" cat-file -e "$C:$p" 2> /dev/null || halt "the reference $p is not in the candidate"
    [ -z "$sha" ] || [ "$got" = "$sha" ] || halt "the reference $p in the candidate has sha256 ${got:0:16}.., not ${sha:0:16}.."
  done
  echo "dry run: sitting 2's ${#REFS2[@]} references are in the candidate; step 9's six and the goldfish page and coverage with the sha256 recorded when they were made; run_screen.txt (sha256 as given Oct 1) and the 5 command-line outputs blob-checked, their sha256 to be recorded in refs2"
  for x in "${SPEC9[@]}"; do
    IFS='|' read -r nm pf sb pl n ref sha _ <<< "$x"
    got=$(git -C "$R" cat-file blob "$C:$KMT/$ref" | python3 -c '
import json, sys
g = [json.loads(l) for l in sys.stdin if l.strip()]
print(len(g), ",".join(str(p) for p in sorted({x["pairing"] for x in g})), min(x["seed"] - 10000 * x["pairing"] - x["i"] for x in g), max(x["seed"] - 10000 * x["pairing"] - x["i"] for x in g), sorted({x["bot_a"] + "/" + x["bot_b"] for x in g}), sorted({x.get("a_file") is not None for x in g}))')
    [ "$got" = "$n $pl $sb $sb ['km3/km3'] [True]" ] || halt "step 9's $nm: its reference holds '$got', not '$n $pl $sb $sb km3/km3 with files' (games, pairings, seed base, bots)"
  done
  echo "dry run: step 9's six references hold exactly the games, pairings and seed bases of SPEC9 (km3 both sides, --pairs rows)"
  mapfile -t lp < <(ls "$R/decks/research")
  [ "${lp[0]:-}" = altaria.txt ] && [ "${lp[1]:-}" = blaziken.txt ] || halt "decks/research's first two lists are not altaria.txt and blaziken.txt"
  echo "dry run: step 10: decks/research starts with altaria.txt, blaziken.txt; $BREW06 and $BREW06B are here; run_screen.py sha256 $(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-16) (the reference was made with 4f102352)"
  if [ -e "$O/trace_load.txt" ]; then
    rc=0; out=$(python3 "$CK3" trace-gate "$O/trace_load.txt") || rc=$?
    committed "$REL/trace_load.txt" && t="committed" || t="NOT committed (step 8 would wait until it is)"
    echo "dry run: trace_load.txt is here, $t: exit $rc, $(reword "$(head -n 1 <<< "$out")")"
    x=$(sed -n 's/^COMMIT \([0-9a-f]*\)$/\1/p' <<< "$out" | head -n 1)
    if [ -n "$x" ]; then git -C "$R" cat-file -e "$x^{commit}" 2> /dev/null && echo "dry run: its commit $x is here" || echo "dry run: NOTE its commit $x is not here (step 8 would wait; Fetch origin)"; fi
    x=$(sed '1s/^\xEF\xBB\xBF//' "$O/trace_load.txt" | tr -d '\r' | grep -E '^CLOUD8B( |$)' || true)
    if [ -z "$x" ]; then echo "dry run: no CLOUD8B line: 8b v the cloud's rows would be noted as not compared (owed)"
    else
      while IFS=' ' read -r t d src want p; do
        if [[ $d =~ ^[0-9a-f]{7,40}$ && $src =~ ^(km3|k3)$ && -n $want && -z $p ]] && git -C "$R" cat-file -e "$d:$want" 2> /dev/null; then
          echo "dry run: CLOUD8B $src: $d:$want is here, $(git -C "$R" show "$d:$want" | grep -c .) rows (compared with ${S}_8b_new_$src.jsonl once 8b has run)"
        else echo "dry run: NOTE the line 'CLOUD8B $d $src $want${p:+ $p}' is malformed or its file is not here: it would be noted as not compared (owed)"; fi
      done <<< "$x"
    fi
  else echo "dry run: NOTE trace_load.txt is not here: step 8 would wait after 8b; steps 9 and 10 run, the gate is read again, and the run ends SITTING 2 PAUSED if it still waits"; fi
  [ "$(git -C "$R" symbolic-ref -q HEAD || true)" = refs/heads/main ] && echo "dry run: the working copy is on main" || echo "dry run: NOTE the working copy is not on main (a start refuses)"
  nst=$(git -C "$R" diff --cached --name-only -- "$REL")
  if [ -z "$nst" ]; then echo "dry run: nothing in $REL is staged in the shared index"
  else
    mapfile -t stg <<< "$nst"
    if git -C "$R" diff --quiet -- "${stg[@]}"; then echo "dry run: NOTE staged in the shared index under $REL, equal to the working copy (a start unstages them): $(tr '\n' ' ' <<< "$nst")"
    else echo "dry run: NOTE staged in the shared index under $REL, and different from the working copy (a start refuses): $(tr '\n' ' ' <<< "$nst")"; fi
  fi
  for x in "${HELPERS[@]/#/$REL/}" "$SCREEN_WITH"; do
    if committed "$x"; then t="committed"; else t="NOT committed as it is here (a start refuses until it is)"; fi
    echo "dry run: ${x#"$REL"/}: $t"
  done
  git -C "$R" check-ignore -q -- "$REL/.sitting2.lock" && echo "dry run: .sitting2.* is ignored by git" \
    || echo "dry run: NOTE .sitting2.* is not in .gitignore: the lock, .ours and .pgid files will show as untracked in GitHub Desktop (never commit them)"
  if git -C "$R" grep -q -F '23,100,000,000' HEAD -- START_HERE.md; then echo "dry run: START_HERE.md (committed) lists the 23,100,000,000 block"
  else echo "dry run: NOTE START_HERE.md (committed) does not list the 23,100,000,000 block: a start refuses"; fi
  x=$(git_locks); [ -z "$x" ] && echo "dry run: no git lock file (index.lock, refs/heads/main.lock)" || echo "dry run: NOTE git lock file here now: $(tr '\n' ' ' <<< "$x")(a start waits 15 s for it, then refuses)"
  if s1_lock_held; then echo "dry run: NOTE .sitting1.lock is held (sitting1.sh or its child is running): a start refuses"; else echo "dry run: .sitting1.lock is not held"; fi
  if git -C "$R" merge-base --is-ancestor "$o" "$m"; then
    unpushed_check "$o" "$m"
    echo "dry run: origin/main ${o:0:7} is main or behind it ($(git -C "$R" rev-list --count "$o..$m") unpushed commits; this switch's by its own record or touching only $REL: $(( $(git -C "$R" rev-list --count "$o..$m") - $(wc -w <<< "$FOREIGN") )))"
    [ -z "$FOREIGN" ] || echo "dry run: NOTE main carries unpushed commits that are not this switch's: $FOREIGN(a start refuses)"
  else echo "dry run: NOTE origin/main ${o:0:7} has commits main lacks: a start refuses (Pull origin first)"; fi
  if [ -z "$DL_GIVEN" ]; then t=$(date -u +%H%M); if [ "$t" -ge 1130 ] && [ "$t" -lt 2100 ]; then echo "dry run: NOTE it is $(date -u +%H:%M) UTC: a start now without an explicit DEADLINE refuses (daytime)"; fi; fi
  out=$(grep -E '^SITTING 2 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
  echo "dry run: sitting 2's last state: ${out:-none (no sitting 2 run yet)}; steps done: $(done_list)"
  rc=0; out=$(GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" push --dry-run --porcelain origin "refs/heads/main:refs/heads/main" 2>&1) || rc=$?
  echo "dry run: git push --dry-run origin main (no write; the credentials): exit $rc, $(grep -E '^[=!*+ -]|^Done|rejected|fatal|error' <<< "$out" | head -n 3 | tr '\n' ' ')"
  echo "dry run: step 8-seeds would: fetch (at most 2 min); copy ${#CARRIERS[@]} files from ${E:0:7} into carriers/ and ${#SCRATCH[@]} from the candidate into scratch_8b/; write pairs_8.tsv, seeds_8.txt, ${S}_refs2.sha256 (into $B/ref2), ${S}_inputs2.sha256; commit and push them before any game"
  echo "dry run: step 8b would run, for km3 then k3: (cd $B/engine; RAYON_NUM_THREADS=$THREADS nice -n $NICE) $OLD_SCAN, then $SCAN, then (cd $W/engine) $WSCAN, each --pairs $O/pairs_8.tsv --root <repo> --seed-base $SEED8 --bot <bot> --pairings $P8B --games 40 --games-out ${S}_8b_<old|new|watch>_<bot>.jsonl; then switch_check.py same (watch v new, 160) and sitting2_check.py touched"
  echo "dry run: step 8 (only when 8c's gate passes, after 8b or again after step 10) would run the same on pairings 0-31: km3 --games 500 (16,000 per build), then k3 --games 250 (8,000 per build)"
  echo "dry run: step 9 would run (cd $B/engine) $SCAN --bot km3 --games 500 on: $(for x in "${SPEC9[@]}"; do IFS='|' read -r nm pf sb pl n _ <<< "$x"; printf '%s (%s, seed base %s, %s games); ' "$nm" "${pf##*/}" "$sb" "$n"; done)each v its reference (switch_check.py same)"
  echo "dry run: step 10 would run (cd <repo>) $GYM simulate --num 240 --players <code>,<code> --seed 7100 --seed-stream -p $CLI_P0 $CLI_P1 for ${CLI_CODES[*]}; (cd $B/engine) $GOLD --deck <repo>/$CLI_P0 --panel <repo>/decks/screen/opponents --games 0 --coverage; (cd <repo>) python3 screen_with.py $GYM <its sha256> decks/screen/run_screen.py $BREW06 $BREW06B --games 240 --pilot km3 --meta-pilot km3 --seed 7100"
  echo "dry run: a start now would have the deadline $(fmt "$DL") and the hard stop $(fmt "$HS"); at $(rate) games a second x $SAFETY + $OVERHEAD_MIN min: 8-seeds $(( $(need_s 8-seeds) / 60 )) min, 8b $(( $(need_s 8b) / 60 )) ($(games_left 8b) games), 8 $(( $(need_s 8) / 60 )) ($(games_left 8)), 9 $(( $(need_s 9) / 60 )) ($(games_left 9)), 10 $(( $(need_s 10) / 60 )) ($(games_left 10))"
  echo "dry run: every check passes (nothing written outside /tmp)"
  FINISHED=1; exit 0
}

trap on_exit EXIT
if [ $DRY -eq 1 ]; then S=dry; dry_run; fi

# ---- One run at a time; refusals before the start line; the state of the last run.
exec 9> "$O/.sitting2.lock"
flock -n 9 || { echo "$(ts) sitting2.sh: another sitting2.sh (or its orphaned child) holds $O/.sitting2.lock; this one exits" >&2; exit 2; }
rm -f -- "$O/.sitting2.ckpt" "$O/.sitting2.hardstop"   # the flags a power-off or a SIGKILL leaves behind
refuse() { echo "$(ts) sitting2.sh: start refused: $*" >&2; exit 2; }
if s1_lock_held; then refuse "sitting1.sh (or its orphaned child) holds $O/.sitting1.lock: one sitting at a time. If no sitting1.sh runs (SITTING=1 bash quiet.sh status), its lock is free, so look for the process holding it (fuser .sitting1.lock)"; fi
for x in "${HELPERS[@]/#/$REL/}" "$SCREEN_WITH"; do
  committed "$x" || refuse "$x is not committed as it is here; commit sitting2.sh and its helpers first (the evidence names committed code)"
done
[ "$(git -C "$R" symbolic-ref -q HEAD 9>&- || true)" = refs/heads/main ] || refuse "the working copy is not on main"
if [ -z "$DL_GIVEN" ]; then
  x=$(date -u +%H%M)
  if [ "$x" -ge 1130 ] && [ "$x" -lt 2100 ]; then
    refuse "it is $(date -u +%H:%M) UTC, daytime: the default deadline is the next 11:30 UTC, so the run would carry on through the away and class hours. At home in the day, give DEADLINE explicitly (HH:MM UTC, an ISO time, or off)"
  fi
fi
git -C "$R" grep -q -F '23,100,000,000' HEAD -- START_HERE.md 9>&- \
  || refuse "START_HERE.md, as committed, does not list the rules switch's seed block 23,100,000,000"
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
st=$(< "/proc/$$/stat"); st=${st##*) }; read -r -a stf <<< "$st"
echo "$$ $(ts) ${stf[19]}" > "$O/.sitting2.pgid"   # group id, time, the leader's start time (quiet.sh checks it)
trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
S=$(sed -n 's/^candidate //p' "$O/candidate.txt" 2> /dev/null | cut -c1-7 || true)
PRIV=$(mktemp -d /tmp/sitting2_rules.XXXXXX) || { PRIV=""; die "mktemp -d for the private copies"; }
cp -- "$O/switch_check.py" "$O/sitting1_check.py" "$O/sitting2_check.py" "$O/checkpoint.sh" "$R/$SCREEN_WITH" "$PRIV/" || die "copying the helpers"
CK="$PRIV/switch_check.py"; CK2="$PRIV/sitting1_check.py"; CK3="$PRIV/sitting2_check.py"; SW="$PRIV/screen_with.py"
# shellcheck source=checkpoint.sh
source "$PRIV/checkpoint.sh"
last=$(grep -E '^SITTING 2 (HALT|STOPPED|PAUSED|DONE) ' "$O/STATUS.txt" 2> /dev/null | tail -n 1 || true)
case $last in
  "SITTING 2 HALT "*)
    if [ -z "${SITTING2_AFTER_HALT:-}" ]; then
      echo "$(ts) sitting2.sh: start refused: the last run halted ($last). A mismatch stops everything and goes to Dustin first; once it is explained (or a script fault is fixed), start with SITTING2_AFTER_HALT='<written reason>'" >&2
      LOCKED=0; exit 1
    fi
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    echo "SITTING 2 RESUMED AFTER HALT $(ts) ${S:-?}: SITTING2_AFTER_HALT='${SITTING2_AFTER_HALT//$'\n'/ }' (stamp $stamp)" >> "$O/STATUS.txt"
    # The halted run's check files are kept (a step that runs again starts its file afresh) and committed with the next
    # checkpoint, so its lines survive even if the halt's own record commit failed.
    for x in touched_8b.txt:8b touched_8.txt:8 identity_9.txt:9 identity_10.txt:10; do
      f=${x%%:*}; n=${x#*:}
      if [ -s "$O/$f" ] && ! grep -q "^STEP $n DONE ${S:-none} " "$O/STATUS.txt"; then
        mv -- "$O/$f" "$O/${f%.txt}.before_resume_$stamp.txt"; KEEP_FILES+=("$REL/${f%.txt}.before_resume_$stamp.txt")
        echo "$(ts) the halted run's $f is kept as ${f%.txt}.before_resume_$stamp.txt (committed with the next checkpoint); step $n writes $f afresh" >> "$O/STATUS.txt"
      fi
    done;;
  "SITTING 2 DONE "*)
    echo "$(ts) sitting2.sh: SITTING 2 DONE is already recorded ($last); nothing to do" >&2; LOCKED=0; exit 0;;
esac
CODELINE="sitting2.sh $(sha256sum < "$O/sitting2.sh" | cut -c1-16), checkpoint.sh $(sha256sum < "$PRIV/checkpoint.sh" | cut -c1-16), switch_check.py $(sha256sum < "$CK" | cut -c1-16), sitting1_check.py $(sha256sum < "$CK2" | cut -c1-16), sitting2_check.py $(sha256sum < "$CK3" | cut -c1-16), screen_with.py $(sha256sum < "$SW" | cut -c1-16) (sha256; HEAD $(git -C "$R" rev-parse --short HEAD 9>&-))"
IGN=""; git -C "$R" check-ignore -q -- "$REL/.sitting2.lock" 9>&- || IGN="; NOTE .sitting2.* is not in .gitignore (its lock, .ours and .pgid files show as untracked: never commit them)"
echo "SITTING 2 START $(ts) ${S:-?}: $KNOBS; pid $$; load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $({ ps -C legality_scan,deckgym,tool_census,goldfish,cargo -o pid=,comm= 2> /dev/null || true; } | tr -s ' \n' ' '); code: $CODELINE (the checks run from private copies made now); git: $PUSHNOTE$UNSTAGED$IGN" >> "$O/STATUS.txt"
pin_note "sitting 2 start ${S:-?}: $CODELINE"
if [ "$HS" -gt 0 ]; then  # the watchdog: past HARD_STOP (read every 20 s, so also after a sleep), outside a checkpoint, TERM to the group
  ( trap - EXIT HUP INT TERM; exec 9>&-
    while sleep 20; do
      [ "$(date +%s)" -ge "$HS" ] || continue
      [ ! -e "$O/.sitting2.ckpt" ] || continue
      : > "$O/.sitting2.hardstop"; kill -TERM -- "-$$" 2> /dev/null; exit 0
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
note "sitting 1's record holds: candidate $C, SITTING 1 DONE, its 6 steps' evidence as their manifests record; the programs are its builds ($B, $W) as recorded, never rebuilt; $S1REC"

# ---- Step 8-seeds (the plan's 8p): the carrier lists and the scratch decks onto main, the pairs and seeds, before any game.
if step_is_done 8-seeds; then STEP=8-seeds; skip_done 8-seeds
else
  begin_step 8-seeds "the carrier lists (e0d149a) and 8b's scratch decks (the candidate) into this folder, pairs_8.tsv and seeds_8.txt, sitting 2's references and inputs: before any game"
  if GIT_TERMINAL_PROMPT=0 timeout -k 10 120 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then note "fetched origin"
  else note "git fetch origin failed or timed out (offline?): $EBR as last fetched"; fi
  e_checks; scratch_checks
  note "$E_NOTE"
  for x in "${CARRIERS[@]}"; do p=${x%%|*}; copy_blob "${x#*|}" "$O/$p" "$REL/$p"; done
  for x in "${SCRATCH[@]}"; do IFS='|' read -r d src want <<< "$x"; copy_blob "$want" "$O/$d" "$REL/$d"; done
  for x in "${CARRIERS[@]}" "${SCRATCH[@]}"; do  # what git add stores (the attributes say -text: the same bytes)
    p=${x%%|*}; want=${x##*|}
    [ "$(git -C "$R" hash-object -- "$REL/$p" 9>&-)" = "$want" ] || halt "$REL/$p would not be stored as the blob ${want:0:7} (git's filters)"
  done
  note "copied byte for byte: ${#CARRIERS[@]} files from ${E:0:7} into carriers/ (the coordinator's four lists and the provenance) and ${#SCRATCH[@]} scratch decks from the candidate into scratch_8b/; each file's blob id checked"
  python3 "$CK3" pairs8 --repo "$R" --out "$PRIV/pairs_8.tsv" --seeds-out "$PRIV/seeds_8.txt" > "$PRIV/pairs8.out" 2>&1 \
    || halt "pairs8: $(tail -n 1 "$PRIV/pairs8.out")"
  for f in pairs_8.tsv seeds_8.txt; do
    if [ -e "$O/$f" ]; then cmp -s -- "$PRIV/$f" "$O/$f" || halt "$f is here but is not what pairs8 writes now (a deck or the panel changed?)"
    else cp -- "$PRIV/$f" "$O/$f"; durable "$O/$f"; fi
  done
  note "$(cat "$PRIV/pairs8.out")"
  extract_refs2
  write_inputs2
  STEP_FILES=(); for x in "${CARRIERS[@]}" "${SCRATCH[@]}"; do STEP_FILES+=("${x%%|*}"); done
  STEP_FILES+=(pairs_8.tsv seeds_8.txt "${S}_refs2.sha256" "${S}_inputs2.sha256")
  finish_step 8-seeds "the carriers (garchomp_meowth and the three alternates, with README.md and selection.json) from ${E:0:7} and 8b's 4 scratch decks from the candidate, byte for byte; pairs_8.tsv (pairings 0-35) and seeds_8.txt (23,100,000,000 + 10,000 x pairing + i); ${#REFS2[@]} references for steps 9 and 10; sitting 2's inputs recorded; all before any game"
  for x in "${CARRIERS[@]}" "${SCRATCH[@]}"; do
    p=${x%%|*}; want=${x##*|}
    [ "$(git -C "$R" rev-parse -q --verify "refs/heads/main:$REL/$p" 9>&- || true)" = "$want" ] || halt "main's $REL/$p is not the blob ${want:0:7} after the checkpoint"
  done
fi

# ---- Step 8b: the scratch rows.
if step_is_done 8b; then STEP=8b; skip_done 8b
else
  begin_step 8b "the scratch rows: pairings 32-35, km3 and k3 i < 40, each on the old, new and watch legality_scan: $(games_left 8b) of 960 games still to play"
  : > "$O/touched_8b.txt"
  carrier_set 8b km3 "$P8B" 40
  carrier_set 8b k3 "$P8B" 40
  step_summary 8b
  STEP_FILES+=(touched_8b.txt)
  finish_step 8b "the scratch rows (pairings 32-35, i < 40): watch equal to new on every field for km3 and k3 (160 each); every game with all repair counters 0 equal to the old game; $SUM (touched_8b.txt; every changed game in handoff_8c.tsv)"
fi

# ---- Step 8c's gate, then step 8: the carrier games (if the gate waits now, it is read again after step 10).
if step_is_done 8; then STEP=8; skip_done 8
else
  STEP=8c; gate_8c
  if [ -z "$GATE_WHY" ]; then
    if fits_now 8; then run_step8
    else note "8c's gate passed, but step 8 (about $(( $(need_s 8) / 60 )) min) would end after the deadline $(fmt "$DL"): steps 9 and 10 run first, then the gate is read again and step 8 runs only if it then fits"; fi
  fi
fi

# ---- Step 9: km3's coverage baselines.
if step_is_done 9; then STEP=9; skip_done 9
else
  begin_step 9 "km3's coverage baselines on the new legality_scan: B2e, Scizor and the 4 second lists, $(games_left 9) of 66,500 games still to play"
  : > "$O/identity_9.txt"
  for x in "${SPEC9[@]}"; do
    IFS='|' read -r nm pf sb pl n ref sha label <<< "$x"
    run_scan "${S}_$nm" "$SCAN" "$B/engine" "$pl" 500 --pairs "$R/$pf" --root "$R" --seed-base "$sb" --bot km3
    ident "$O/identity_9.txt" "$label" "${S}_$nm" "$n" "" "$B/ref2/$KMT/$ref"
  done
  STEP_FILES+=(identity_9.txt)
  finish_step 9 "km3's coverage baselines: B2e 48,000, Scizor 4,000, v-lucario_2, v-suicune_2 and v-weezing_2 3,500 each, l-charizardy 4,000: 66,500 games, each equal to km_tables_2026-09-30's 1f6319e reference on every field (identity_9.txt)"
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
  pin_note "every check of sitting 2 passed for $C: the scratch rows (960 games) and the carrier games (72,000), watch equal to new and every all-zero-counter game equal to the old one (their changed games go to 8c: handoff_8c.tsv); km3's coverage baselines (66,500); the command line, goldfish and the screen (5,040). Step 8: ${x:-see its STEP line}. REPLAYS DONE (PLAN.md step 10: sitting 1's 7, 7b, 7c and sitting 2's 8b, 8, 9, 10); the prepare-done mark is not this runner's to write: it waits for 8c's traces. This start played $PLAYED games and reused $REUSED."
  state_line "SITTING 2 DONE $C $(ts): step 8, ${x:-see its STEP line}"
else
  state_line "SITTING 2 PAUSED $(ts) ${S:-?}: step 8 waits for 8c's trace load (trace_load.txt; read after 8b and again after step 10): $GATE_WHY; steps done: $(done_list)(committed). Once trace_load.txt holds 'TRACE LOAD <n> <the cloud commit>' (and a DUSTIN line when n > 50) and is committed, a plain start runs step 8 only"
fi
FINISHED=1; RECORD=1
}
main "$@"; exit
