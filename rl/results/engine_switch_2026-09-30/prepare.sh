#!/usr/bin/env bash
# The engine switch carrying kta and km (Dustin, Sept 30, recorded in rl/RUN5.md under km, "The official engine switch
# carrying kta and km": "prepare now"; "pin if all pass": a mismatch stops everything, the manifest stays untouched and
# the laptop reports to him). PLAN.md here, steps 1-7: preparation only. Nothing is pinned; the manifest and main are
# not touched; the shared working copy is never checked out, switched, stashed or reset (the candidate is made with git
# merge-tree, commit-tree and update-ref). Rules items stay out (a players-only switch: main + B's engine/src/players/).
# kt3, ktb3 and ktc3 come as B defines them: diagnostic, no identity claim, not played here. The pin (plan steps 8-11)
# is a separate script, run only after "PREPARE DONE" and Dustin's word. Shape copied from ../engine_switch_2026-09-28/.
#
#   0. The candidate (no game). After a fetch (at most 5 min, no auto-maintenance; a failed or timed-out fetch uses the
#      local objects): the merge of main's HEAD and the cloud round head 53fc5a1 (B = 1f6319e, km's build), made without
#      the working copy: git merge-tree --write-tree (a conflict stops), git commit-tree with parents main and 53fc5a1
#      and the final merge message (when main has not moved, pin.sh fast-forwards main to this very commit), kept at
#      refs/pocketdecksim/engine-switch-candidate (not a branch: GitHub Desktop does not list it, a push does not send
#      it) and recorded in candidate.txt (made once; a later start checks it and never remakes it). Checks: engine/ is
#      exactly B's tree 9c84fef (any difference stops the run and goes to Dustin); engine/ differs from the official
#      engine's source 233bced and from ec7e1a8 (kta's recorded build) in engine/src/players/ only, engine/UPSTREAM.md
#      aside (B's fork notes on upstream deckgym-core merges and PRs differ from 233bced's; no build file names it,
#      checked with git grep); the diff from main outside rl/results/ is engine/src/players/ only (anything else, a
#      notes file included, stops the run, as pin.sh and plan step 8 would).
#   1. The build (no game, ~30 min): one git archive of the candidate (engine/ and decks/) into
#      /home/dacz8976/engine-switch-<short>, then cargo builds deckgym, examples/legality_scan and examples/goldfish as
#      Sept 28's pin_prepare.sh did. Their sha256 go to PIN_STATUS.txt and programs.sha256, checked before and after every
#      later step; a build is never redone after step 1 passed (a differing program stops the run). cargo runs with
#      --locked (the candidate's engine/Cargo.lock, the same blob as 1f6319e's, 233bced's and ec7e1a8's). The reference
#      files are taken from the candidate (git cat-file, blob-checked) into <build>/ref (<short>_refs.sha256); the six
#      gate references must also have the sha256 recorded when they were played (km_config.json and the skip records
#      for kta3's, km_tables_2026-09-30/1f6319e_skip_*.json for km3's). The input files the games read are recorded
#      (<short>_inputs.sha256; each inside the repository must be the candidate's file).
#   2. kta3 on the FRESH deals, first because it was never replayed at B (22,500 games, ~45 min), as run_kta.sh played
#      them (legality_scan --pairs <kta_tables_2026-09-29/pairs file> --root <repo> --seed-base B --bot kta3, in the
#      build's engine/):
#        fresh_table28.tsv,   pairings 0-27, i < 500, seeds 23,000,000,000 + 10,000 x pairing + i
#            v kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl (14,000)
#        fresh_new_decks.tsv, pairings 8-24, i < 500, seeds 23,001,000,000 + 10,000 x pairing + i
#            v kta_tables_2026-09-29/ec7e1a8_fresh_kta3_new17.jsonl (8,500)
#   3. kta3 on the development deals (22,500, ~45 min), as run_kt.sh played them:
#        --decks ../decks/research, pairings 0-27, i < 500, seeds 72,000,000 + 10,000 x pairing + i
#            v kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl (14,000; sha256 6b90d3cf.., as km_config.json names it)
#        --pairs gauntlet_runs_2026-09-26/tsv/new_decks.tsv, pairings 8-24, i < 500, seeds 21,108,000,000 + ...
#            v kt_tables_2026-09-28/ec7e1a8_kta3_new17.jsonl (8,500; sha256 1803e256..)
#   4. km3 on the same development deals (22,500, ~45 min), as run_km.sh played them
#            v km_tables_2026-09-30/1f6319e_km3_table.jsonl (14,000) and 1f6319e_km3_new17.jsonl (8,500)
#   5. k3, kp3 and kog3 on the table's 14,000 deals each (--decks, 72,000,000; 42,000 games; Sept 28 took 29 min) v the
#      Sept 28 pin's references: k3 kpf_2026-09-26/reading/table_k3.jsonl, kp3 kpf_2026-09-26/reading/table_kp3.jsonl,
#      kog3 kog_2026-09-27/a823b6d_kog3_500.jsonl and kog_composition_2026-09-27/table_kog3.jsonl. The Sept 28 pinned
#      programs' own games, engine_switch_2026-09-28/pin_identity_<code>_500.jsonl, are compared only where their bytes
#      differ from those references; today each is the same file byte for byte (the same git blob: k3 24fd1363, kp3
#      af03d284, kog3 97b08179, also table_kog3's), so one comparison covers them and the note says so; they add no
#      independent evidence. Lines in pin_identity.txt.
#   7. The command line, goldfish and the screen (5,040 games, ~15 min; runs before step 6, so the required checks are
#      all in before the extras):
#      deckgym simulate --num 240 --players C,C --seed 7100 --seed-stream -p decks/research/altaria.txt
#      decks/research/blaziken.txt (Sept 28's command, in the repository): k3, kp3 and kog3 must print Sept 28's lines
#      exactly (its pin_identity.txt: 150/90/0, 144/96/0, 149/91/0); kta3 and km3 must run clean (exit 0, one line each,
#      240 games, no panic). goldfish --deck <repo>/decks/research/altaria.txt --panel <repo>/decks/screen/opponents
#      --games 0 --coverage: both outputs byte-equal to Sept 28's pin_goldfish.txt and pin_goldfish_coverage.json.
#      run_screen.py, unchanged, kog3 on both sides, brew-06 and brew-06b, 240 games per matchup, seed 7,100 (3,840
#      games), run on the NEW deckgym through screen_with.py (the manifest is neither read nor touched): equal, line for
#      line, to floor_recheck_2026-09-28/run_screen.txt, the header's program path aside.
#   6. The extras, last (the plan: "suggested, not gates, reported beside"; EXTRAS=1; 24,740 games with kpr3 at 40
#      deals, the plan's count, ~50 min): kq3 on the table (--decks, 500) v kt_2026-09-26/identity/official_kq3_500.jsonl;
#      kog3 on the 17 new cells (new_decks.tsv, 21,108,000,000, 500) v kog_composition_2026-09-27/new17_kog3.jsonl; kd3
#      (--decks, 40 deals) v kt_2026-09-26/identity/43cef0b_kd3_40.jsonl; kpr3 (--decks, KPR3_DEALS, default 40, the
#      plan's and ec7e1a8's size; 500, its reference's size, makes step 6 37,620 games, ~25 min more) v
#      kpf_2026-09-26/reading/table_kpr3.jsonl i < KPR3_DEALS. A difference here stops the run too ("a mismatch stops
#      everything"); by then every required check is in the record.
#   Then the anchored line "PREPARE DONE <candidate> <time>" in STATUS.txt and PIN_STATUS.txt.
# Identity (steps 2-6): games matched by (pairing, i), counts asserted (both files hold exactly the expected deals, once
# each); every field the reference records must be equal (moves, decisions, openings, winner_seat, points, seed,
# first_seat, bot_a, bot_b, a, b, a_file, b_file, turns, first_deck_score and the counters); every game is the one the
# command plays (switch_check.py complete); every scan page is free of RULE findings. One line per reference file in
# identity_check.txt. Totals: steps 2-5 109,500 games; step 7 5,040; step 6 24,740 (37,620 with KPR3_DEALS=500): about
# 139,000 games, under 5 hours at 8.6 games a second (k3, kp3 and kog3 ran faster on Sept 28).
# The checks run from a private copy of switch_check.py and screen_with.py made at each start (in /tmp, removed at the
# end); the sha256 of prepare.sh and of both copies is in the START line and in PIN_STATUS.txt, so every line of one
# pass comes from one recorded checker, whatever happens to the working copy's files meanwhile.
#
# STATUS.txt: a timestamped note per action and these anchored lines, at column 0:
#   PREPARE START <time> <short>: ...                  every start
#   STEP <n> DONE <short> <time> <summary>              a step passed (n = 0..7)
#   PREPARE HALT <time> <short>: step <n>: <why>        a gate failed: an identity difference, a missing or extra game,
#                                                       a RULE finding, a program crash (any exit code but a stop
#                                                       signal's, SIGABRT and SIGSEGV included), the CLI, goldfish or
#                                                       screen output, the candidate's checks, a program, reference or
#                                                       input that differs from its record. Nothing later runs. Also in
#                                                       PIN_STATUS.txt. A later start refuses until
#                                                       PREPARE_AFTER_HALT='<written reason>' is set (it is noted).
#   PREPARE STOPPED <time> <short>: step <n>: <why>     the script could not carry on (a build, fetch or git failure, a
#                                                       stop signal: HUP, INT, KILL or TERM, an error outside a check):
#                                                       not an identity result; a restart resumes. Also in PIN_STATUS.txt.
#                                                       A PREPARE_REVERIFY start writes one first, withdrawing the
#                                                       earlier DONE until its own pass ends.
#   PREPARE DONE <candidate> <time>                     every gate passed. Also in PIN_STATUS.txt. The last line
#                                                       matching ^PREPARE (HALT|STOPPED|DONE) is the run's state.
# These lines never carry the words FAILED or MISMATCH (a checker's "FAILED" is written "does not match its record"):
# pin.sh stops on those words anywhere in PIN_STATUS.txt, and a halt on record is already its own gate there.
# Resumable: a game file is written as .part and kept only when complete, with a record <name>.run naming the program's
# sha256 and the exact command; a later start reuses it only when that record matches and it is complete, and compares
# it again. Every start re-runs every comparison, so identity_check.txt and pin_identity.txt always hold one whole pass.
# One run at a time: flock on .prepare.lock (fd 9). The children inherit it, so an orphaned legality_scan still holds
# it and a restart cannot race it; pin.sh takes the same lock, so a pin never reads a pass that is being rewritten.
# The whole script is one function, main, called on the last line.
# Files this writes outside this folder: the build folder /home/dacz8976/engine-switch-<short>, the private checker
# copy in /tmp, the candidate commit and its ref (once), and the objects git merge-tree --write-tree writes at every
# start and in a dry run (unreachable tree objects in .git; the candidate commit makes one set reachable).
#
# Usage (WSL):
#   nohup setsid bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_2026-09-30/prepare.sh" \
#     >> "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_2026-09-30/prepare.log" 2>&1 &
#   bash prepare.sh --dry-run   step 0's checks on today's merge tree only: no fetch, no commit, no ref; nothing written
#                               but the merge's tree objects in .git (git merge-tree --write-tree)
#   bash quiet.sh pause|resume  quiet hours: SIGSTOP / SIGCONT of this run's own process group (prepare.sh makes itself
#                               a group leader), nothing else
#   bash quiet.sh stop          the way to stop a run: TERM to the whole group (and CONT, in case it is paused); the
#                               record says PREPARE STOPPED and a plain restart resumes. A TERM to prepare.sh alone waits
#                               until the current scan ends (bash runs its trap only after the foreground child).
# Knobs (environment): THREADS 14, NICE 10, JOBS 14 (cargo), EXTRAS 1 (0 skips step 6; the DONE summary says so),
#   KPR3_DEALS 40 (the plan's; 500 is its reference's size), PREPARE_AFTER_HALT (above), PREPARE_REVERIFY=1 (check
#   every step again after a DONE, from the kept outputs), INPUTS_RENEW='<reason>' (record the inputs afresh). Smoke
#   only (SWITCH_OUT outside the repository, not /home/dacz8976/engine-*, and empty or an earlier smoke's folder, which
#   holds the .switch_smoke mark): SWITCH_STANDIN, a folder of stand-in deckgym, legality_scan and goldfish copied in
#   place of cargo's; the build is always <out>/build (SWITCH_BUILD, if set, must say so). A smoke makes no fetch, no
#   commit and no ref: the merge tree stands for the candidate.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[ ! "$HERE" -ef "$R/rl/results/engine_switch_2026-09-30" ] || HERE="$R/rl/results/engine_switch_2026-09-30"
DRY=0; [ "${1:-}" != --dry-run ] || DRY=1
if [ $DRY -eq 0 ] && [ -z "${SWITCH_REEXEC:-}" ] && [ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]; then
  SWITCH_REEXEC=1 exec setsid bash "${BASH_SOURCE[0]}" "$@"   # its own process group (quiet.sh pauses exactly this run)
fi

# ---- The fixed names (Dustin's decision; the plan).
RH=53fc5a1edf35f66873a7cb96f19374048e2e8597        # the cloud round head (B's round)
BCOMMIT=1f6319e4b72e34a42d2d3c3ffc7cc9a09fdfa6f3   # B, km's build
BTREE=9c84fefd44a4719678415b0e12a717b8ead373a9     # B's engine/ tree
KTB=ec7e1a867bdaae2b0b4a3d2730e36dfffb611900       # the kt build: kta3's recorded games
OFF=233bced99cf99b2a90aededaa48d1381ef147400       # the official engine's source (rl/engine-2026-09-28/)
BR=origin/claude/pensive-ptolemy-spwc0b
CREF=refs/pocketdecksim/engine-switch-candidate   # not a branch (pin.sh's CAND_REF says the same)
KTA_T=rl/results/kta_tables_2026-09-29; KT_T=rl/results/kt_tables_2026-09-28; KM_T=rl/results/km_tables_2026-09-30
P28=rl/results/engine_switch_2026-09-28
PFRESH_T=$KTA_T/pairs/fresh_table28.tsv; PFRESH_N=$KTA_T/pairs/fresh_new_decks.tsv
PDEV_N=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv
BREW06=decks/brews/brew-06-pyukumuku-silvally-payback.txt; BREW06B=decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt
REF_FRESH_KTA_T=$KTA_T/ec7e1a8_fresh_kta3_table.jsonl; REF_FRESH_KTA_N=$KTA_T/ec7e1a8_fresh_kta3_new17.jsonl
REF_KTA_T=$KT_T/ec7e1a8_kta3_table.jsonl; REF_KTA_N=$KT_T/ec7e1a8_kta3_new17.jsonl
REF_KM_T=$KM_T/1f6319e_km3_table.jsonl; REF_KM_N=$KM_T/1f6319e_km3_new17.jsonl
# The six gate references' sha256 as recorded when they were played (a later rewrite of one stops the run):
SHA_KTA_T=6b90d3cfa24e17815026dab7c787df327cfc859e491d1399889aaa2369a3c73b   # km_config.json's
SHA_KTA_N=1803e256e45d2d5a6208d61854067e88e05af51315cd4eefecda33c2f84603ba   # km_config.json's
SHA_FRESH_T=e3d7f4d71490aa2c074e21a7d3f3495912d3fa1d51d16ce77bc6bd96b51f7c5a # kta_tables_2026-09-29/ec7e1a8_fresh_skip_table.json, coverage_skip.txt
SHA_FRESH_N=b5216c940d4a3c680ba8bc67cf2c8097f458f7691d48963cbe9e3db5bfb6f3fa # kta_tables_2026-09-29/ec7e1a8_fresh_skip_new17.json
SHA_KM_T=aff167ac8ca56054fdf1e971a17cb2071d7362e6ee964f5575263d4100b61712    # km_tables_2026-09-30/1f6319e_skip_table.json, STATUS.txt
SHA_KM_N=8623d6f958ab46bd99ea6ff62389210521038cbc78b18273abc93dc1fd2339b2    # km_tables_2026-09-30/1f6319e_skip_new17.json
GATE_SHA=("$REF_FRESH_KTA_T" "$SHA_FRESH_T" "$REF_FRESH_KTA_N" "$SHA_FRESH_N" "$REF_KTA_T" "$SHA_KTA_T"
          "$REF_KTA_N" "$SHA_KTA_N" "$REF_KM_T" "$SHA_KM_T" "$REF_KM_N" "$SHA_KM_N")
REF_K3=rl/results/kpf_2026-09-26/reading/table_k3.jsonl; REF_KP3=rl/results/kpf_2026-09-26/reading/table_kp3.jsonl
REF_KOG3_A=rl/results/kog_2026-09-27/a823b6d_kog3_500.jsonl; REF_KOG3_B=rl/results/kog_composition_2026-09-27/table_kog3.jsonl
REF_PIN_K3=$P28/pin_identity_k3_500.jsonl; REF_PIN_KP3=$P28/pin_identity_kp3_500.jsonl; REF_PIN_KOG3=$P28/pin_identity_kog3_500.jsonl
REF_KQ3=rl/results/kt_2026-09-26/identity/official_kq3_500.jsonl; REF_KD3=rl/results/kt_2026-09-26/identity/43cef0b_kd3_40.jsonl
REF_KOG3_N=rl/results/kog_composition_2026-09-27/new17_kog3.jsonl; REF_KPR3=rl/results/kpf_2026-09-26/reading/table_kpr3.jsonl
REF_PIN_TXT=$P28/pin_identity.txt; REF_GOLD_TXT=$P28/pin_goldfish.txt; REF_GOLD_JSON=$P28/pin_goldfish_coverage.json
REF_SCREEN=rl/results/floor_recheck_2026-09-28/run_screen.txt
REFS=("$REF_FRESH_KTA_T" "$REF_FRESH_KTA_N" "$REF_KTA_T" "$REF_KTA_N" "$REF_KM_T" "$REF_KM_N" "$REF_K3" "$REF_KP3"
      "$REF_KOG3_A" "$REF_KOG3_B" "$REF_PIN_K3" "$REF_PIN_KP3" "$REF_PIN_KOG3" "$REF_KQ3" "$REF_KD3" "$REF_KOG3_N"
      "$REF_KPR3" "$REF_PIN_TXT" "$REF_GOLD_TXT" "$REF_GOLD_JSON" "$REF_SCREEN")
CLI_P0=decks/research/altaria.txt; CLI_P1=decks/research/blaziken.txt   # Sept 28: the first two of ls decks/research

canon_out() {  # as run_kta.sh: absolute, '..' and links resolved; spelled from $R when it lies in $R/rl/results
  local p d rest=""
  p=$(realpath -m -- "$1") || return 1
  d=$p
  while [ "$d" != / ]; do
    if [ -d "$d" ] && [ "$d" -ef "$R/rl/results" ]; then echo "$R/rl/results$rest"; return 0; fi
    rest="/${d##*/}$rest"; d=$(dirname -- "$d")
  done
  echo "$p"
}
O=$(canon_out "${SWITCH_OUT:-$HERE}") || { echo "prepare: cannot resolve SWITCH_OUT ${SWITCH_OUT:-}" >&2; exit 1; }
SMOKE=1; case "$O/" in "$R"/rl/results/*) SMOKE=0;; esac
if [ $DRY -eq 0 ]; then
  if [ $SMOKE -eq 0 ]; then
    [ "$O" = "$R/rl/results/engine_switch_2026-09-30" ] \
      || { echo "prepare: inside rl/results the output is rl/results/engine_switch_2026-09-30 only (not $O)" >&2; exit 1; }
    [ -z "${SWITCH_STANDIN:-}${SWITCH_BUILD:-}" ] \
      || { echo "prepare: SWITCH_STANDIN and SWITCH_BUILD are for smokes (SWITCH_OUT outside rl/results)" >&2; exit 1; }
  else  # a smoke writes only into a folder of its own, outside the repository and outside every engine build
    [ -n "${SWITCH_STANDIN:-}" ] && [ -d "$SWITCH_STANDIN" ] \
      || { echo "prepare: a smoke (SWITCH_OUT outside rl/results) needs SWITCH_STANDIN, a folder of stand-in programs" >&2; exit 1; }
    d=$O
    while [ -n "$d" ] && [ "$d" != / ]; do
      if [ -d "$d" ] && [ "$d" -ef "$R" ]; then echo "prepare: a smoke's SWITCH_OUT must lie outside the repository (not $O)" >&2; exit 1; fi
      d=$(dirname -- "$d")
    done
    case "$O/" in /home/dacz8976/engine-*|/home/dacz8976/|/) echo "prepare: a smoke's SWITCH_OUT may not be $O" >&2; exit 1;; esac
    if [ -d "$O" ] && [ -n "$(ls -A -- "$O")" ] && [ ! -e "$O/.switch_smoke" ]; then
      echo "prepare: a smoke's SWITCH_OUT must be empty or an earlier smoke's folder (with its .switch_smoke mark): $O" >&2; exit 1
    fi
    [ -z "${SWITCH_BUILD:-}" ] || [ "$(realpath -m -- "$SWITCH_BUILD")" = "$O/build" ] \
      || { echo "prepare: a smoke's build folder is <out>/build only (SWITCH_BUILD=$SWITCH_BUILD)" >&2; exit 1; }
    mkdir -p -- "$O"; : > "$O/.switch_smoke"
  fi
fi
THREADS=${THREADS:-14}; NICE=${NICE:-10}; JOBS=${JOBS:-14}; EXTRAS=${EXTRAS:-1}; KPR3_DEALS=${KPR3_DEALS:-40}
for x in "$THREADS" "$NICE" "$JOBS" "$KPR3_DEALS"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "prepare: knob value $x is not a number" >&2; exit 1; }
done
case $EXTRAS in 0|1) ;; *) echo "prepare: EXTRAS must be 0 or 1" >&2; exit 1;; esac
[ "$KPR3_DEALS" -ge 1 ] && [ "$KPR3_DEALS" -le 500 ] || { echo "prepare: KPR3_DEALS must be 1-500 (its reference holds 500 deals)" >&2; exit 1; }
KNOBS="threads $THREADS, nice $NICE, cargo jobs $JOBS, extras $EXTRAS, kpr3 deals $KPR3_DEALS"

# ---- Notes, stops and the anchored lines.
S=""; C=""; STEP=start; FINISHED=0; PLAYED=0; REUSED=0; LAST_ID=""; PRIV=""
ts() { date -u +%FT%TZ; }
note() { if [ $DRY -eq 1 ]; then echo "$*"; else echo "$(ts) $*" >> "$O/STATUS.txt"; fi; }
pin_note() { if [ $DRY -eq 1 ]; then echo "(PIN_STATUS) $*"; else echo "$(ts) $*" >> "$O/PIN_STATUS.txt"; fi; }
state_line() {  # the anchored line, in both files; a pasted checker's FAILED / MISMATCH reworded (pin.sh stops on them)
  local l=$*
  l=${l//FAILED open or read/missing or unreadable}; l=${l//FAILED/does not match its record}; l=${l//MISMATCH/mismatch}
  if [ $DRY -eq 1 ]; then echo "$l"; else echo "$l" >> "$O/STATUS.txt"; echo "$l" >> "$O/PIN_STATUS.txt"; fi
}
halt() { state_line "PREPARE HALT $(ts) ${S:-?}: step $STEP: $*"; FINISHED=1; exit 1; }
die() { state_line "PREPARE STOPPED $(ts) ${S:-?}: step $STEP: $*"; FINISHED=1; exit 1; }
on_exit() {
  local rc=$?
  if [ "$FINISHED" -eq 0 ] && [ $DRY -eq 0 ]; then
    state_line "PREPARE STOPPED $(ts) ${S:-?}: step $STEP: exit code $rc outside a check (a script, system or signal stop, not an identity result; see prepare.log)"
  fi
  if [ -n "$PRIV" ]; then rm -rf -- "$PRIV"; fi
}

# ---- Step 0's parts.
MT=""
merge_tree() {  # main: sets MT, the tree of the merge of main and the round head; a conflict halts
  local out rc=0
  out=$(git -C "$R" merge-tree --write-tree --name-only "$1" "$RH") || rc=$?
  case $rc in
    0) MT=$(head -n 1 <<< "$out");;
    1) halt "the merge of main ${1:0:7} and 53fc5a1 has conflicts: $(tail -n +2 <<< "$out" | head -n 20 | tr '\n' ' ')";;
    *) die "git merge-tree failed (exit $rc): $(head -n 3 <<< "$out" | tr '\n' ' ')";;
  esac
  [[ $MT =~ ^[0-9a-f]{40}$ ]] || die "git merge-tree printed no tree"
}
cand_msg() {  # main tree: the candidate's message. It is the final merge message: when main has not moved, pin.sh
              # fast-forwards main to this very commit (else it makes its own merge and this one stays off main).
  local n
  n=$(git -C "$R" diff --name-only "$1" "$2" -- engine/src/players/ | wc -l)
  cat <<EOF
Merge claude/pensive-ptolemy-spwc0b at 53fc5a1 into main: the kta/km engine switch, players only (Dustin, Sept 30: "pin if all pass")

engine/ is B's (km's build 1f6319e, tree 9c84fef). Against main ${1:0:7}, the first parent, only engine/src/players/
($n files) and rl/results/ change; the rules code is main's, and the pending rules items stay out. Made off-tree by
rl/results/engine_switch_2026-09-30/prepare.sh (step 0: git merge-tree, git commit-tree), which builds and replays
this commit (identity_check.txt there); main reaches it only through pin.sh, after PREPARE DONE and Dustin's word.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
}
candidate_checks() {  # tree-ish main: step 0's checks on the candidate (in a dry run or a smoke, the merge tree)
  local c=$1 m=$2 d f et nres base; local -a ups=() readers=() players=() others=()
  et=$(git -C "$R" rev-parse "$c:engine") || die "no engine/ in $c"
  [ "$(git -C "$R" rev-parse "$BCOMMIT:engine")" = "$BTREE" ] || halt "B ${BCOMMIT:0:7}'s engine/ is not tree 9c84fef"
  if [ "$et" != "$BTREE" ]; then
    d=$(git -C "$R" diff --name-only "$BCOMMIT" "$c" -- engine) || die "git diff B..candidate -- engine"
    halt "the candidate's engine/ is tree $et, not B's tree 9c84fef exactly; it differs in: $(tr '\n' ' ' <<< "$d")(the plan's byte check; this goes to Dustin)"
  fi
  note "engine/ is tree $et, B's (${BCOMMIT:0:7}) tree 9c84fef exactly"
  d=$(git -C "$R" grep -l -I -e UPSTREAM "$c" -- engine ':(exclude)engine/UPSTREAM.md' || true)
  if [ -n "$d" ]; then mapfile -t ups <<< "$d"; fi
  for f in "${ups[@]}"; do f=${f#*:}; case $f in *.md) ;; *) readers+=("$f");; esac; done
  [ ${#readers[@]} -eq 0 ] || halt "files under engine/ that a build may read name UPSTREAM: ${readers[*]} (UPSTREAM.md must be a notes file)"
  note "engine/UPSTREAM.md is the fork's notes on upstream deckgym-core (merges, PRs, what to take at the next merge); no build or program reads it: git grep finds no file under engine/ outside .md notes that names it (${#ups[@]} .md mentions)"
  for base in "$OFF" "$KTB"; do
    d=$(git -C "$R" diff --name-only "$base" "$c" -- engine ':(exclude)engine/src/players/' ':(exclude)engine/UPSTREAM.md') \
      || die "git diff ${base:0:7}..candidate -- engine"
    [ -z "$d" ] || halt "engine/ differs from ${base:0:7} outside engine/src/players/ (UPSTREAM.md aside): $(tr '\n' ' ' <<< "$d")"
  done
  note "players-only: against the official engine's source 233bced, engine/ changes only $(git -C "$R" diff --name-only "$OFF" "$c" -- engine/src/players/ | tr '\n' ' ')($(git -C "$R" diff --shortstat "$OFF" "$c" -- engine/src/players/ | sed 's/^ *//')), UPSTREAM.md aside; against ec7e1a8 too, players/ only"
  d=$(git -C "$R" diff --name-only "$m" "$c" -- . ':(exclude)rl/results/') || die "git diff main..candidate"
  if [ -n "$d" ]; then
    while IFS= read -r f; do
      case $f in engine/src/players/*) players+=("$f");; *) others+=("$f");; esac
    done <<< "$d"
  fi
  [ ${#others[@]} -eq 0 ] || halt "outside rl/results/ the candidate changes files other than engine/src/players/ (plan step 8 allows only the players files; notes too would stop the pin): ${others[*]}"
  nres=$(git -C "$R" diff --name-only "$m" "$c" -- rl/results/ | wc -l) || die "git diff main..candidate -- rl/results/"
  note "diff main ${m:0:7}..candidate outside rl/results/: players files ${players[*]:-(none)}; nothing else. Under rl/results/: $nres files come with it (the cloud's records)"
}

if [ $DRY -eq 1 ]; then  # step 0's checks on today's merge tree: no fetch, no commit, no ref; only merge-tree's objects
  STEP=0; S=dry
  M=$(git -C "$R" rev-parse refs/heads/main)
  echo "dry run: main ${M:0:7}, origin/main $(git -C "$R" rev-parse --short origin/main), $BR $(git -C "$R" rev-parse --short "$BR") (as last fetched; no fetch now)"
  git -C "$R" merge-base --is-ancestor "$RH" "$BR" || halt "53fc5a1 is not on $BR"
  git -C "$R" merge-base --is-ancestor "$BCOMMIT" "$RH" || halt "B is not an ancestor of 53fc5a1"
  merge_tree "$M"
  echo "dry run: the merge of main ${M:0:7} and 53fc5a1 is tree $MT, no conflicts"
  candidate_checks "$MT" "$M"
  echo "dry run: step 0's checks pass on that tree (nothing written but the merge's tree objects in .git)"
  FINISHED=1; exit 0
fi

# ---- One run at a time; the state of the last run; the start line.
mkdir -p "$O"
exec 9> "$O/.prepare.lock"   # held by this run and every child it starts (an orphaned scan keeps it); pin.sh takes it too
flock -n 9 || { echo "$(ts) prepare: another prepare.sh (or its orphaned child, or pin.sh) holds $O/.prepare.lock; this one exits" >> "$O/STATUS.txt"; exit 2; }
st=$(< "/proc/$$/stat"); st=${st##*) }; read -r -a stf <<< "$st"
echo "$$ $(ts) ${stf[19]}" > "$O/.prepare.pgid"   # group id, time, the leader's start time (quiet.sh checks it: no reused pid)
trap on_exit EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
[ ! -s "$O/candidate.txt" ] || S=$(sed -n 's/^candidate //p' "$O/candidate.txt" | cut -c1-7)
last=$(grep -E '^PREPARE (HALT|STOPPED|DONE) ' "$O/STATUS.txt" 2>/dev/null | tail -n 1 || true)
case $last in
  "PREPARE HALT "*)
    if [ -z "${PREPARE_AFTER_HALT:-}" ]; then
      note "start refused: the last run halted ($last). A mismatch stops everything and goes to Dustin first; once it is explained (or a script fault is fixed), start with PREPARE_AFTER_HALT='<written reason>'"
      FINISHED=1; exit 1
    fi
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    for f in identity_check.txt pin_identity.txt; do [ ! -e "$O/$f" ] || mv -- "$O/$f" "$O/${f%.txt}.halted_$stamp.txt"; done
    echo "PREPARE RESUMED AFTER HALT $(ts) ${S:-?}: PREPARE_AFTER_HALT='${PREPARE_AFTER_HALT//$'\n'/ }' (the halted pass's identity_check.txt and pin_identity.txt kept as *.halted_$stamp.txt)" >> "$O/STATUS.txt";;
  "PREPARE DONE "*)
    if [ -z "${PREPARE_REVERIFY:-}" ]; then
      note "PREPARE DONE is already recorded ($last); nothing to do (PREPARE_REVERIFY=1 checks every step again from the kept outputs)"
      FINISHED=1; exit 0
    fi
    # Before the evidence is rewritten, the DONE stops being the last state (in STATUS.txt and PIN_STATUS.txt), so no
    # pin reads a half-rewritten pass, and a re-verify killed without its trap leaves STOPPED, not DONE, behind.
    state_line "PREPARE STOPPED $(ts) ${S:-?}: step start: PREPARE_REVERIFY under way; the earlier DONE is withdrawn until this pass writes its own";;
esac
PRIV=$(mktemp -d /tmp/prepare_switch_2026-09-30.XXXXXX) || die "mktemp -d for the checker's private copy"
cp -- "$HERE/switch_check.py" "$HERE/screen_with.py" "$PRIV/" || die "copying switch_check.py and screen_with.py"
CK="$PRIV/switch_check.py"; SW="$PRIV/screen_with.py"
CODE="prepare.sh sha256 $(sha256sum < "${BASH_SOURCE[0]}" | cut -c1-64), switch_check.py $(sha256sum < "$CK" | cut -c1-64), screen_with.py $(sha256sum < "$SW" | cut -c1-64)"
echo "PREPARE START $(ts) ${S:-?}: out $O; $([ $SMOKE -eq 1 ] && echo "SMOKE (stand-in programs from $SWITCH_STANDIN; no fetch, commit or ref)" || echo "the registered run"); $KNOBS; pid $$; load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $({ ps -C legality_scan,deckgym,tool_census,goldfish -o pid=,comm= 2>/dev/null || true; } | tr -s ' \n' ' '); code: $CODE (the checks run from a private copy made now)" >> "$O/STATUS.txt"
pin_note "start ${S:-?}: $CODE (every check of this start runs from a private copy of these two, made at the start)"
: > "$O/identity_check.txt"; : > "$O/pin_identity.txt"   # every start writes one whole pass

# ---- Step 0: the candidate.
step_done() {  # n summary: the anchored line, once per candidate
  if ! grep -q "^STEP $1 DONE $S " "$O/STATUS.txt"; then echo "STEP $1 DONE $S $(ts) $2" >> "$O/STATUS.txt"; fi
  note "step $1 passed: $2"
}
STEP=0
if [ -s "$O/candidate.txt" ]; then  # made at an earlier start: checked, never remade
  C=$(sed -n 's/^candidate //p' "$O/candidate.txt"); M=$(sed -n 's/^main //p' "$O/candidate.txt"); T=$(sed -n 's/^tree //p' "$O/candidate.txt")
  [[ $C =~ ^[0-9a-f]{40}$ && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ ]] || halt "candidate.txt does not hold a candidate, main and tree"
  S=${C:0:7}
  merge_tree "$M"
  [ "$MT" = "$T" ] || halt "the merge of main ${M:0:7} and 53fc5a1 is now tree $MT, not the recorded $T"
  if [ $SMOKE -eq 0 ]; then
    [ "$(git -C "$R" rev-parse -q --verify "$CREF" || true)" = "$C" ] || halt "$CREF is not the recorded candidate $C"
    [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || halt "the candidate's tree is not the recorded $T"
    [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$RH" ] \
      && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null || halt "the candidate's parents are not main ${M:0:7} and 53fc5a1"
  else
    [ "$C" = "$T" ] || halt "smoke: candidate.txt's candidate is not its tree"
  fi
  now=$(git -C "$R" rev-parse refs/heads/main)
  if [ "$now" = "$M" ]; then note "candidate $C (made at an earlier start) checked: parents main ${M:0:7} and 53fc5a1, tree ${T:0:7}"
  else note "candidate $C (made at an earlier start) checked: parents main ${M:0:7} and 53fc5a1, tree ${T:0:7}; main has moved to ${now:0:7} since (the pin makes and checks its own merge)"; fi
  candidate_checks "$C" "$M"
elif [ $SMOKE -eq 0 ] && EX=$(git -C "$R" rev-parse -q --verify "$CREF"); then
  # The ref is here but candidate.txt is not: a start stopped between update-ref and moving candidate.txt into place.
  # Adopt the ref only if it is exactly the commit that start made (its candidate.txt.part, written before update-ref,
  # names it; parents, tree and message as prepare.sh makes them). Anything else is a stop for a person, not a halt.
  P=$O/candidate.txt.part
  C=$(sed -n 's/^candidate //p' "$P" 2>/dev/null || true); M=$(sed -n 's/^main //p' "$P" 2>/dev/null || true)
  T=$(sed -n 's/^tree //p' "$P" 2>/dev/null || true)
  why="$CREF exists (${EX:0:7}) but neither candidate.txt nor a matching candidate.txt.part records it: look at it (git log -1 $CREF), then delete it (git update-ref -d $CREF) or restore candidate.txt, and start again"
  [[ $C == "$EX" && $M =~ ^[0-9a-f]{40}$ && $T =~ ^[0-9a-f]{40}$ ]] || die "$why"
  [ "$(git -C "$R" rev-parse "$C^1")" = "$M" ] && [ "$(git -C "$R" rev-parse "$C^2")" = "$RH" ] \
    && ! git -C "$R" rev-parse -q --verify "$C^3" > /dev/null && [ "$(git -C "$R" rev-parse "$C^{tree}")" = "$T" ] || die "$why (its parents or tree differ)"
  merge_tree "$M"
  [ "$MT" = "$T" ] || die "$why (the merge of main ${M:0:7} and 53fc5a1 is tree $MT, not $T)"
  [ "$(git -C "$R" cat-file commit "$C" | sed '1,/^$/d')" = "$(cand_msg "$M" "$T")" ] || die "$why (its message is not prepare.sh's)"
  S=${C:0:7}
  mv -- "$P" "$O/candidate.txt"
  note "candidate $C adopted: $CREF, made by a start that stopped before recording it (candidate.txt.part names it; parents main ${M:0:7} and 53fc5a1, tree ${T:0:7}, prepare.sh's message)"
  candidate_checks "$C" "$M"
else
  if [ $SMOKE -eq 0 ]; then
    # At most 5 minutes (a stalled network counts as offline), no auto-maintenance (no detached gc in the shared .git),
    # no prompt, and without fd 9 (git holds no lock of this run).
    if GIT_TERMINAL_PROMPT=0 timeout -k 30 300 git -C "$R" fetch -q --no-auto-maintenance origin 9>&-; then note "fetched origin"
    else  # the round head is a fixed commit: offline, the local objects make the same merge
      git -C "$R" cat-file -e "$RH^{commit}" 2> /dev/null || die "git fetch origin failed or timed out and 53fc5a1 is not here"
      note "git fetch origin failed or timed out (offline?); 53fc5a1 is here, so the candidate is made from the local objects"
    fi
    git -C "$R" merge-base --is-ancestor "$RH" "$BR" || halt "53fc5a1 is not on $BR"
    br=$(git -C "$R" rev-parse "$BR")
    if [ "$br" != "$RH" ]; then note "$BR has moved past the round head, to ${br:0:7}; the candidate takes the round head 53fc5a1, which Dustin's decision names"; fi
  else note "smoke: no fetch; the merge tree stands for the candidate (no commit, no ref)"; fi
  git -C "$R" merge-base --is-ancestor "$BCOMMIT" "$RH" || halt "B ${BCOMMIT:0:7} is not an ancestor of the round head"
  M=$(git -C "$R" rev-parse refs/heads/main)
  note "main is ${M:0:7} (origin/main $(git -C "$R" rev-parse --short origin/main)); the round head 53fc5a1 is on $BR; B 1f6319e is its ancestor"
  merge_tree "$M"; T=$MT
  candidate_checks "$T" "$M"   # on the tree, before any commit is made of it
  if [ $SMOKE -eq 1 ]; then C=$T
  else
    C=$(cand_msg "$M" "$T" | git -C "$R" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$T" -p "$M" -p "$RH" -F -) \
      || die "git commit-tree failed"
    [[ $C =~ ^[0-9a-f]{40}$ ]] || die "git commit-tree printed no commit"
  fi
  S=${C:0:7}
  printf 'candidate %s\nmain %s\nround_head %s\ntree %s\nmade %s\n' "$C" "$M" "$RH" "$T" "$(ts)" > "$O/candidate.txt.part"
  if [ $SMOKE -eq 0 ]; then   # the .part is written first, so a stop right after update-ref can be recognised
    git -C "$R" update-ref -m "prepare.sh step 0: the engine switch candidate" "$CREF" "$C" "" || die "git update-ref $CREF failed"
  fi
  mv -- "$O/candidate.txt.part" "$O/candidate.txt"
  note "candidate made: $C (merge of main ${M:0:7} and 53fc5a1, tree ${T:0:7})$([ $SMOKE -eq 1 ] && echo "; SMOKE: the tree itself" || echo "; at $CREF")"
fi
if ! grep -q "^STEP 0 DONE $S " "$O/STATUS.txt"; then
  pin_note "candidate $C: the merge of main ${M:0:7} and the cloud round head 53fc5a1 (B = 1f6319e), $([ $SMOKE -eq 1 ] && echo "SMOKE: a tree, no commit" || echo "at $CREF"); engine/ tree $(git -C "$R" rev-parse "$C:engine") (B's 9c84fef); players-only against 233bced"
fi
step_done 0 "candidate $C, engine/ = B's, players-only, no conflict"

# ---- Step 1: the build, the references, the inputs.
STEP=1
if [ $SMOKE -eq 1 ]; then B="$O/build"; else B=/home/dacz8976/engine-switch-$S; fi   # SWITCH_BUILD only restates a smoke's
[[ $S =~ ^[0-9a-f]{7}$ ]] || die "no candidate short name ($S)"
case $B in /home/dacz8976/engine-switch-"$S"|"$O"/build) ;; *) die "the build folder $B is neither /home/dacz8976/engine-switch-$S nor a smoke's <out>/build";; esac
GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"; GOLD="$B/engine/target/release/examples/goldfish"
PINS="$O/programs.sha256"; REFSUM="$O/${S}_refs.sha256"; INPUTS="$O/${S}_inputs.sha256"
pin_of() { grep -F "  $1" "$PINS" | cut -c1-64; }
check_pins() {  # when: the build's commit and the three programs against step 1's record
  local out
  [ "$(cat "$B/COMMIT" 2>/dev/null)" = "$C" ] || halt "$B/COMMIT is not the candidate $C ($1)"
  [ -s "$PINS" ] || halt "programs.sha256 is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$PINS" 2>&1) || halt "a program differs from its pin ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
  note "programs checked ($1): deckgym $(pin_of "$GYM" | cut -c1-16), legality_scan $(pin_of "$SCAN" | cut -c1-16), goldfish $(pin_of "$GOLD" | cut -c1-16) = programs.sha256"
}
verify_refs() {  # when
  local out
  out=$(cd "$B/ref" && sha256sum -c --quiet --strict -- "$REFSUM" 2>&1) || halt "a reference file differs from ${REFSUM##*/} ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')"
}
inputs_list() {  # the files the games read beside the programs, absolute, sorted
  local f
  { for f in "$B"/decks/research/*.txt "$R"/decks/research/*.txt "$R"/decks/screen/opponents/*.txt; do echo "$f"; done
    for f in "$PFRESH_T" "$PFRESH_N" "$PDEV_N" "$BREW06" "$BREW06B" decks/screen/run_screen.py; do echo "$R/$f"; done
    python3 "$CK" pairs-decks "$R/$PFRESH_T" "$R/$PFRESH_N" "$R/$PDEV_N" | while IFS= read -r f; do echo "$R/$f"; done
  } | LC_ALL=C sort -u
}
verify_inputs() {  # when: every input unchanged since it was recorded, and the same list
  local out
  [ -s "$INPUTS" ] || halt "the inputs record ${INPUTS##*/} is missing ($1)"
  out=$(sha256sum -c --quiet --strict -- "$INPUTS" 2>&1) || halt "an input file changed ($1): $(head -n 3 <<< "$out" | tr '\n' ' ')(${INPUTS##*/})"
  out=$(diff <(cut -c67- "$INPUTS") <(inputs_list) 2>&1) || halt "the list of input files changed ($1): $(grep '^[<>]' <<< "$out" | head -n 3 | tr '\n' ' ')"
}
write_inputs() {  # every input inside the repository must be the candidate's file; then their sha256
  local lst f i n; local -a IN=() RELS=() H=() BL=()
  lst=$(inputs_list) || die "listing the input files failed"
  mapfile -t IN <<< "$lst"
  for f in "${IN[@]}"; do [ -f "$f" ] || halt "input file $f is missing"; case $f in "$R"/*) RELS+=("${f#"$R"/}");; esac; done
  mapfile -t H < <(printf '%s\n' "${RELS[@]}" | git -C "$R" hash-object --stdin-paths)
  mapfile -t BL < <(for f in "${RELS[@]}"; do printf '%s:%s\n' "$C" "$f"; done | git -C "$R" cat-file --batch-check='%(objectname) %(objecttype)')
  [ ${#H[@]} -eq ${#RELS[@]} ] && [ ${#BL[@]} -eq ${#RELS[@]} ] || die "hashing the input files failed"
  n=0
  for i in "${!RELS[@]}"; do
    [ "${BL[$i]}" = "${H[$i]} blob" ] || halt "input ${RELS[$i]} in the working copy is not the candidate's file (${BL[$i]})"
    n=$((n + 1))
  done
  for f in "$B"/decks/research/*.txt; do
    cmp -s -- "$f" "$R/decks/research/${f##*/}" || halt "the build's decks/research/${f##*/} (read by --decks) differs from the working copy's (read by the CLI)"
  done
  [ "$(ls "$B/decks/research" | wc -l)" = "$(ls "$R/decks/research" | wc -l)" ] || halt "the build's decks/research and the working copy's hold different lists"
  sha256sum -- "${IN[@]}" > "$INPUTS.part" || die "sha256 of the input files"
  mv -- "$INPUTS.part" "$INPUTS"
  note "inputs recorded (before any game): ${#IN[@]} files, ${INPUTS##*/} (sha256 $(sha256sum < "$INPUTS" | cut -c1-16)); the $n inside the repository equal the candidate's files; every step checks them"
}
extract_refs() {  # the reference files, from the candidate, blob-checked
  local p d blob
  for p in "${REFS[@]}"; do
    d="$B/ref/$p"; mkdir -p "$(dirname "$d")"
    blob=$(git -C "$R" rev-parse --verify -q "$C:$p") || halt "the reference $p is not in the candidate"
    git -C "$R" cat-file blob "$blob" > "$d.part" || die "git cat-file $p"
    [ "$(git -C "$R" hash-object --no-filters -- "$d.part")" = "$blob" ] || die "$p: the extracted file is not the candidate's blob"
    mv -- "$d.part" "$d"
  done
  gate_refs "taken from the candidate"
  (cd "$B/ref" && sha256sum -- "${REFS[@]}") > "$REFSUM.part" || die "sha256 of the references"
  mv -- "$REFSUM.part" "$REFSUM"
  note "references taken from the candidate (git cat-file, blob-checked) into $B/ref: ${#REFS[@]} files, ${REFSUM##*/}"
}
gate_refs() {  # when: the six gate references have the sha256 recorded when they were played
  local k got
  for ((k = 0; k < ${#GATE_SHA[@]}; k += 2)); do
    got=$(sha256sum < "$B/ref/${GATE_SHA[k]}" | cut -c1-64) || die "sha256 of ${GATE_SHA[k]}"
    [ "$got" = "${GATE_SHA[k+1]}" ] \
      || halt "${GATE_SHA[k]} ($1) has sha256 ${got:0:16}.., not ${GATE_SHA[k+1]:0:16}.. recorded when its games were played"
  done
  note "the six gate references ($1) have the sha256 recorded when they were played (km_config.json; kta_tables_2026-09-29 and km_tables_2026-09-30 skip records)"
}
if grep -q "^STEP 1 DONE $S " "$O/STATUS.txt"; then  # built at an earlier start: checked, never rebuilt
  check_pins "at this start; built at an earlier start"
  verify_refs "at this start"; gate_refs "at this start"
  if [ -n "${INPUTS_RENEW:-}" ]; then
    [ ! -e "$INPUTS" ] || mv -- "$INPUTS" "$INPUTS.renewed_$(date -u +%Y%m%dT%H%M%SZ)"
    note "INPUTS_RENEW='${INPUTS_RENEW//$'\n'/ }': the inputs recorded afresh (the old record kept beside)"
    write_inputs
  fi
  verify_inputs "at this start"
  note "step 1: the build, references and inputs of an earlier start, checked"
else
  rm -rf -- "$B"; mkdir -p "$B"; echo "$C" > "$B/COMMIT"
  git -C "$R" archive "$C" engine decks | tar -x -C "$B" || die "git archive $C engine decks | tar"
  note "one git archive of $C (engine/ and decks/) in $B"
  if [ $SMOKE -eq 1 ]; then
    mkdir -p "$(dirname "$SCAN")"
    install -m 755 "$SWITCH_STANDIN/deckgym" "$GYM"; install -m 755 "$SWITCH_STANDIN/legality_scan" "$SCAN"
    install -m 755 "$SWITCH_STANDIN/goldfish" "$GOLD"
    note "SMOKE: stand-in programs from $SWITCH_STANDIN in place of cargo's"
  else
    set +u; source "$HOME/.cargo/env" 2>/dev/null || true; set -u
    note "building: $(cargo --version), $(rustc --version), $JOBS jobs, nice $NICE (build.log)"
    s=$(date +%s)
    ( cd "$B/engine" && unset CARGO_TARGET_DIR && nice -n "$NICE" cargo build --release --locked -j "$JOBS" \
        && nice -n "$NICE" cargo build --release --locked --example legality_scan -j "$JOBS" \
        && nice -n "$NICE" cargo build --release --locked --example goldfish -j "$JOBS" ) > "$O/build.log" 2>&1 \
      || die "the build failed (build.log; with --locked, a Cargo.lock that needs updating fails here too)"
    note "built in $(( $(date +%s) - s )) s"
  fi
  for p in "$GYM" "$SCAN" "$GOLD"; do [ -x "$p" ] || die "no program $p after the build"; done
  sha256sum -- "$GYM" "$SCAN" "$GOLD" > "$PINS.part"; mv -- "$PINS.part" "$PINS"
  pin_note "built $C in $B$([ $SMOKE -eq 1 ] && echo " (SMOKE: stand-in programs)")"
  for p in "$GYM" "$SCAN" "$GOLD"; do pin_note "sha256 $(pin_of "$p") ${p##*/}"; done
  extract_refs
  write_inputs
  check_pins "after the build"
fi
PIN_GYM=$(pin_of "$GYM")
step_done 1 "deckgym $(pin_of "$GYM" | cut -c1-16), legality_scan $(pin_of "$SCAN" | cut -c1-16), goldfish $(pin_of "$GOLD" | cut -c1-16) from one archive of $S; ${#REFS[@]} references; inputs recorded"

# ---- The game helpers.
run_record() {  # program cwd args...: the text of a .run record (the program's pin and the exact command)
  local p=$1 d=$2; shift 2
  printf '%s sha256 %s\ncwd %s\nargs' "${p##*/}" "$(pin_of "$p")" "$d"; printf ' %q' "$@"; printf '\n'
}
kept() {  # file record-file want: an output of this program and command is here
  [ -e "$1" ] && [ -e "$2" ] && [ "$(cat "$2")" = "$3" ]
}
stopped_or_failed() {  # rc what: a stop signal is a stop (a restart plays it again); any other exit code is a halt
  local sig=$(( $1 - 128 )) name
  name=$(kill -l "$sig" 2> /dev/null || echo "?")
  case $1 in  # HUP, INT, KILL (also the OOM killer's), TERM: sent from outside, so a restart plays it again
    129|130|137|143) die "$2 was stopped by signal $sig (SIG$name); a restart plays it again";;
  esac
  # SIGABRT (a Rust abort or stack overflow), SIGSEGV, SIGBUS and the like come from the program itself: a crash
  if [ "$1" -gt 128 ]; then halt "$2 ended on signal $sig (SIG$name): a program crash, not a stop"; fi
  halt "$2 exited with code $1"
}
run_scan() {  # name pairings deals args...: legality_scan in the build's engine/ folder; then complete and RULE checks
  local name=$1 pl=$2 n=$3; shift 3
  local f="$O/$name" sb=72000000 pf="" bot="" ba="" bb="" prev="" x s out want rc=0; local -a chk
  for x in "$@"; do
    case $prev in --pairs) pf=$x;; --seed-base) sb=$x;; --bot) bot=$x;; --bot-a) ba=$x;; --bot-b) bb=$x;; esac
    prev=$x
  done
  ba=${ba:-$bot}; bb=${bb:-$bot}
  chk=(complete --pairings "$pl" --games "$n" --seed-base "$sb" --bot-a "$ba" --bot-b "$bb")
  if [ -n "$pf" ]; then chk+=(--pairs "$pf"); else chk+=(--decks); fi
  want=$(run_record "$SCAN" "$B/engine" "$@" --pairings "$pl" --games "$n")
  if [ -e "$f.jsonl" ]; then
    kept "$f.jsonl" "$f.run" "$want" \
      || halt "$name.jsonl is here, but its record $name.run does not name this program and command: move $name.* away first"
    out=$(python3 "$CK" "${chk[@]}" "$f.jsonl") \
      || halt "$name.jsonl is here but is not the complete output of this command ($out): move $name.* away first"
    REUSED=$((REUSED + $(wc -l < "$f.jsonl")))
    note "$name: kept from an earlier start ($out)"
  else
    rm -f -- "$f.jsonl.part" "$f.run"
    s=$(date +%s)
    ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$SCAN" "$@" --pairings "$pl" --games "$n" \
        --games-out "$f.jsonl.part" ) > "$f.txt" 2>&1 || rc=$?
    [ $rc -eq 0 ] || stopped_or_failed $rc "legality_scan for $name (see $name.txt)"
    out=$(python3 "$CK" "${chk[@]}" "$f.jsonl.part") \
      || halt "$name: the scan's output is not the complete set of deals, each the game this command plays ($out)"
    printf '%s\n' "$want" > "$f.run"; mv -- "$f.jsonl.part" "$f.jsonl"
    PLAYED=$((PLAYED + $(wc -l < "$f.jsonl")))
    note "$name played in $(( $(date +%s) - s )) s ($out)"
  fi
  out=$(python3 "$CK" rules "$f.txt") || halt "RULE FINDING or an incomplete page: $out"
}
ident() {  # label name expect max_i ref...: one line per reference in identity_check.txt; any difference halts
  local label=$1 name=$2 expect=$3 maxi=$4 r line rc=0; shift 4
  local -a args=(same "$O/$name.jsonl" --expect "$expect" --label "$label")
  [ -z "$maxi" ] || args+=(--max-i "$maxi")
  for r in "$@"; do args+=(--ref "$B/ref/$r"); done
  line=$(python3 "$CK" "${args[@]}") || rc=$?
  echo "$line" >> "$O/identity_check.txt"
  case $rc in
    0) LAST_ID=$line; note "identity: $(tr '\n' ' ' <<< "$line" | cut -c1-600)";;
    1) halt "IDENTITY: $label differs from its reference (identity_check.txt): $(grep -o 'DIFFERS: .*' <<< "$line" | head -n 2 | tr '\n' ' ')$(grep -v ' of [0-9]* equal on every field' <<< "$line" | head -n 1)";;
    *) halt "the identity check for $label could not read its input (exit $rc: a malformed or missing file, not a game result): $(tail -n 1 <<< "$line")";;
  esac
}
distinct_refs() {  # ref...: DREFS, the refs whose bytes differ from every earlier one; SAMEAS names the others
  local r q dup; DREFS=(); SAMEAS=""
  for r in "$@"; do
    dup=""
    for q in "${DREFS[@]}"; do if cmp -s -- "$B/ref/$r" "$B/ref/$q"; then dup=$q; break; fi; done
    if [ -n "$dup" ]; then SAMEAS+="${SAMEAS:+; }${r#rl/results/} is the same file as ${dup#rl/results/}, byte for byte"
    else DREFS+=("$r"); fi
  done
}
pin_line() {  # code [same-as]: the Sept 28 form ("k3 at the new build: v <ref> n of n; ...") of the last comparison, in pin_identity.txt
  echo "$1 at the new build: $(sed -E 's/^.*: (v [^ ]+ [0-9]+ of [0-9]+) equal on every field.*$/\1/' <<< "$LAST_ID" | paste -sd ';' - | sed 's/;/; /g')${2:+ ($2, so no separate comparison)}" >> "$O/pin_identity.txt"
}
step_begin() {  # n what
  STEP=$1
  check_pins "before step $1"; verify_refs "before step $1"; verify_inputs "before step $1"
  note "step $1: $2"
}
step_end() {  # n summary
  check_pins "after step $1"; verify_refs "after step $1"; verify_inputs "after step $1"
  pin_note "step $1: $2"
  step_done "$1" "$2"
}
ALL28=$(seq -s, 0 27); N17=$(seq -s, 8 24)
TAB=(--decks ../decks/research)
FT=(--pairs "$R/$PFRESH_T" --root "$R" --seed-base 23000000000)
FN=(--pairs "$R/$PFRESH_N" --root "$R" --seed-base 23001000000)
DN=(--pairs "$R/$PDEV_N" --root "$R" --seed-base 21108000000)

# ---- Step 2: kta3 on the fresh deals (never replayed at B), first.
step_begin 2 "kta3 on the fresh deals v ec7e1a8's committed fresh kta3 games: 22,500 games (about 45 min at 8.6 games a second)"
run_scan "${S}_fresh_kta3_table" "$ALL28" 500 "${FT[@]}" --bot kta3
ident "2 kta3 fresh, the 28 table cells (fresh_table28.tsv, seeds 23,000,000,000 + 10,000 x pairing + i)" "${S}_fresh_kta3_table" 14000 "" "$REF_FRESH_KTA_T"
run_scan "${S}_fresh_kta3_new17" "$N17" 500 "${FN[@]}" --bot kta3
ident "2 kta3 fresh, the 17 new cells (fresh_new_decks.tsv, seeds 23,001,000,000 + 10,000 x pairing + i)" "${S}_fresh_kta3_new17" 8500 "" "$REF_FRESH_KTA_N"
step_end 2 "kta3 on the fresh deals: 14,000 of 14,000 and 8,500 of 8,500 games equal ec7e1a8's (ec7e1a8_fresh_kta3_table, _new17)"

# ---- Step 3: kta3 on the development deals.
step_begin 3 "kta3 on the development deals v ec7e1a8_kta3_table and _new17: 22,500 games (about 45 min)"
run_scan "${S}_dev_kta3_table" "$ALL28" 500 "${TAB[@]}" --bot kta3
ident "3 kta3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_dev_kta3_table" 14000 "" "$REF_KTA_T"
run_scan "${S}_dev_kta3_new17" "$N17" 500 "${DN[@]}" --bot kta3
ident "3 kta3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)" "${S}_dev_kta3_new17" 8500 "" "$REF_KTA_N"
step_end 3 "kta3 on the development deals: 14,000 of 14,000 and 8,500 of 8,500 games equal ec7e1a8's (ec7e1a8_kta3_table, _new17)"

# ---- Step 4: km3 on the development deals.
step_begin 4 "km3 on the development deals v B's 1f6319e_km3_table and _new17: 22,500 games (about 45 min)"
run_scan "${S}_dev_km3_table" "$ALL28" 500 "${TAB[@]}" --bot km3
ident "4 km3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_dev_km3_table" 14000 "" "$REF_KM_T"
run_scan "${S}_dev_km3_new17" "$N17" 500 "${DN[@]}" --bot km3
ident "4 km3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)" "${S}_dev_km3_new17" 8500 "" "$REF_KM_N"
step_end 4 "km3: 14,000 of 14,000 and 8,500 of 8,500 games equal B's (1f6319e_km3_table, _new17)"

# ---- Step 5: k3, kp3 and kog3 on the table v the Sept 28 pin's references.
step_begin 5 "k3, kp3 and kog3 on the table's 14,000 deals each v the Sept 28 pin's references: 42,000 games (Sept 28 took 29 min; at most about 1 h 20 min)"
for code in k3 kp3 kog3; do
  run_scan "${S}_table_$code" "$ALL28" 500 "${TAB[@]}" --bot "$code"
  case $code in   # the Sept 28 pinned programs' own games are compared only where their bytes differ from the references
    k3) distinct_refs "$REF_K3" "$REF_PIN_K3";; kp3) distinct_refs "$REF_KP3" "$REF_PIN_KP3";;
    kog3) distinct_refs "$REF_KOG3_A" "$REF_KOG3_B" "$REF_PIN_KOG3";;
  esac
  [ -z "$SAMEAS" ] || note "$code: $SAMEAS (so one comparison covers them; no independent evidence)"
  ident "5 $code, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_table_$code" 14000 "" "${DREFS[@]}"
  pin_line "$code" "$SAMEAS"
done
step_end 5 "k3, kp3 and kog3: 14,000 of 14,000 each, equal to the Sept 28 references, which the Sept 28 pinned programs' own games equal byte for byte or are compared beside (pin_identity.txt)"

# ---- Step 7 (before step 6, so every required check is in before the extras): the command line, goldfish, the screen.
step_begin 7 "deckgym simulate (5 x 240 games), goldfish --coverage, run_screen under kog3 on brew-06 and 06b (3,840 games): about 15 min"
mapfile -t RS < <(ls "$R/decks/research")
[ "${RS[0]:-}" = altaria.txt ] && [ "${RS[1]:-}" = blaziken.txt ] \
  || halt "decks/research's first two lists are not altaria.txt and blaziken.txt (Sept 28's command took the first two)"
cli_run() {  # code
  local code=$1 f="$O/${S}_cli_$1" want line exp rc=0
  want=$(run_record "$GYM" "$R" simulate --num 240 --players "$code,$code" --seed 7100 --seed-stream -p "$CLI_P0" "$CLI_P1")
  if kept "$f.txt" "$f.run" "$want"; then note "cli $code: kept from an earlier start"
  else
    rm -f -- "$f.txt" "$f.run" "$f.txt.part"
    ( cd "$R" && nice -n "$NICE" "$GYM" simulate --num 240 --players "$code,$code" --seed 7100 --seed-stream \
        -p "$CLI_P0" "$CLI_P1" ) > "$f.txt.part" 2>&1 || rc=$?
    [ $rc -eq 0 ] || stopped_or_failed $rc "deckgym simulate $code (see ${f##*/}.txt.part)"
    printf '%s\n' "$want" > "$f.run"; mv -- "$f.txt.part" "$f.txt"; PLAYED=$((PLAYED + 240))
  fi
  line=$(python3 "$CK" cli "$f.txt" --code "$code" --num 240 2> /dev/null) \
    || halt "deckgym simulate $code did not run clean: $(python3 "$CK" cli "$f.txt" --code "$code" --num 240 2>&1 | tail -n 1)"
  echo "$line" >> "$O/pin_identity.txt"
  case $code in
    k3|kp3|kog3)
      exp=$(grep -F "cli $code,$code: " "$B/ref/$REF_PIN_TXT") || halt "Sept 28's pin_identity.txt has no line for cli $code"
      [ "$line" = "$exp" ] || halt "cli $code: '$line' is not Sept 28's '$exp'"
      note "cli $code: Sept 28's line, exactly ($line)";;
    *) note "cli $code: ran clean ($line)";;
  esac
}
for code in k3 kp3 kog3 kta3 km3; do cli_run "$code"; done
G="$O/${S}_goldfish"; GC="$O/${S}_goldfish_coverage"; rc=0
want=$(run_record "$GOLD" "$B/engine" --deck "$R/$CLI_P0" --panel "$R/decks/screen/opponents" --games 0 --coverage "${GC##*/}.json")
if kept "$G.txt" "$G.run" "$want" && [ -e "$GC.json" ]; then note "goldfish: kept from an earlier start"
else
  rm -f -- "$G.txt" "$G.run" "$GC.json" "$G.txt.part" "$GC.json.part"
  ( cd "$B/engine" && nice -n "$NICE" "$GOLD" --deck "$R/$CLI_P0" --panel "$R/decks/screen/opponents" --games 0 \
      --coverage "$GC.json.part" ) > "$G.txt.part" 2>&1 || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "goldfish --coverage (see ${G##*/}.txt.part)"
  printf '%s\n' "$want" > "$G.run"; mv -- "$GC.json.part" "$GC.json"; mv -- "$G.txt.part" "$G.txt"
fi
cmp -s -- "$G.txt" "$B/ref/$REF_GOLD_TXT" \
  || halt "goldfish's page differs from Sept 28's pin_goldfish.txt: $(diff -- "$B/ref/$REF_GOLD_TXT" "$G.txt" | head -n 6 | tr '\n' ' ')"
cmp -s -- "$GC.json" "$B/ref/$REF_GOLD_JSON" \
  || halt "goldfish --coverage differs from Sept 28's pin_goldfish_coverage.json: $(diff -- "$B/ref/$REF_GOLD_JSON" "$GC.json" | head -n 6 | tr '\n' ' ')"
note "goldfish --coverage: the page and the coverage file equal Sept 28's pin_goldfish.txt and pin_goldfish_coverage.json byte for byte"
SC="$O/${S}_run_screen"; rc=0
SARGS=("$BREW06" "$BREW06B" --games 240 --pilot kog3 --meta-pilot kog3 --seed 7100)
want=$(run_record "$GYM" "$R" "run_screen.py=$(sha256sum < "$R/decks/screen/run_screen.py" | cut -c1-64)" \
  "screen_with.py=$(sha256sum < "$SW" | cut -c1-64)" "${SARGS[@]}")
if kept "$SC.txt" "$SC.run" "$want"; then note "run_screen: kept from an earlier start"
else
  rm -f -- "$SC.txt" "$SC.run" "$SC.txt.part"
  ( cd "$R" && nice -n "$NICE" python3 "$SW" "$GYM" "$PIN_GYM" "$R/decks/screen/run_screen.py" "${SARGS[@]}" ) \
    > "$SC.txt.part" 2>&1 || rc=$?
  [ $rc -eq 0 ] || stopped_or_failed $rc "run_screen.py on the new deckgym (see ${SC##*/}.txt.part)"
  printf '%s\n' "$want" > "$SC.run"; mv -- "$SC.txt.part" "$SC.txt"; PLAYED=$((PLAYED + 3840))
fi
out=$(python3 "$CK" screen "$SC.txt" "$B/ref/$REF_SCREEN") \
  || halt "run_screen under kog3 on the new deckgym differs from floor_recheck_2026-09-28/run_screen.txt: $out"
note "$out"
step_end 7 "cli k3, kp3 and kog3 repeat Sept 28's lines and kta3 and km3 ran clean (pin_identity.txt); goldfish --coverage equals Sept 28's; run_screen under kog3 on brew-06 and 06b equals floor_recheck_2026-09-28/run_screen.txt"

# ---- Step 6, last: the extras, reported beside the gates (a difference still stops the run).
if [ "$EXTRAS" -eq 1 ]; then
  step_begin 6 "the extras (kq3 table, kog3 new cells, kd3 40 deals, kpr3 $KPR3_DEALS deals): $((14000 + 8500 + 1120 + 28 * KPR3_DEALS)) games (about $(( (14000 + 8500 + 1120 + 28 * KPR3_DEALS) / 516 )) min at most)"
  run_scan "${S}_table_kq3" "$ALL28" 500 "${TAB[@]}" --bot kq3
  ident "6 extra, kq3, the 28 table cells (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_table_kq3" 14000 "" "$REF_KQ3"
  run_scan "${S}_new17_kog3" "$N17" 500 "${DN[@]}" --bot kog3
  ident "6 extra, kog3, the 17 new cells (new_decks.tsv, seeds 21,108,000,000 + 10,000 x pairing + i)" "${S}_new17_kog3" 8500 "" "$REF_KOG3_N"
  run_scan "${S}_table_kd3_40" "$ALL28" 40 "${TAB[@]}" --bot kd3
  ident "6 extra, kd3, the 28 table cells, i < 40 (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_table_kd3_40" 1120 "" "$REF_KD3"
  run_scan "${S}_table_kpr3_$KPR3_DEALS" "$ALL28" "$KPR3_DEALS" "${TAB[@]}" --bot kpr3
  ident "6 extra, kpr3, the 28 table cells, i < $KPR3_DEALS (--decks, seeds 72,000,000 + 10,000 x pairing + i)" "${S}_table_kpr3_$KPR3_DEALS" $((28 * KPR3_DEALS)) \
    "$([ "$KPR3_DEALS" -lt 500 ] && echo "$KPR3_DEALS" || true)" "$REF_KPR3"
  step_end 6 "the extras: kq3 14,000, kog3 new cells 8,500, kd3 1,120 and kpr3 $((28 * KPR3_DEALS)) games (i < $KPR3_DEALS), all equal to their references"
  EXTRAS_SAID="the extras equal (kpr3 at $KPR3_DEALS deals)"
else
  STEP=6; note "step 6 (the extras) not run: EXTRAS=0"; EXTRAS_SAID="the extras not run (EXTRAS=0)"
fi

# ---- Done.
STEP=done
pin_note "every gate passed for $C: kta3 fresh, kta3 development, km3, k3, kp3 and kog3 identical ($(grep -c . "$O/identity_check.txt") reference files, identity_check.txt); $EXTRAS_SAID; the command line, goldfish and the screen as Sept 28. This start played $PLAYED games and reused $REUSED."
state_line "PREPARE DONE $C $(ts)"
FINISHED=1
}
main "$@"
