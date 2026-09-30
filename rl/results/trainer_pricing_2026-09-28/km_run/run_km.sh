#!/usr/bin/env bash
# km's laptop runner: every laptop step of ../REGISTRATION_DRAFT.md (km, registered Sept 29 at 55e5d95 with Dustin's
# word; its top block "Registration (Sept 29, Dustin's word)" governs), read with its Amendment 1 (Sept 30, before any
# km game on the laptop): km re-issued on kta. km3 = kta3 + N2 at the cloud's new build B, and km3 is read against kta3
# (the adopted working pilot: kog + kt's switch 1 as ec7e1a8 defines it) everywhere: the identity games, the timing pair,
# the thresholds, the footprint, the 45 cells, (c), (d), coverage and the counters (Amendment 1 (b) items 1-2). Built
# from ../../kta_2026-09-29/run_kta.sh and ../../kt_tables_2026-09-28/run_kt.sh; its general machinery (the lock,
# resumable outputs, the inputs record, the STATUS lines, the HALT and stop-cause gate) is the Sept 29 runner's.
#
# ONE SET (Amendment 1 (b) item 3: "The runner and the reader use this set and no other"): the candidate (km3), the
# baseline (kta3), B, its branch, round head and round folder, the kt build and the official engine it is checked
# against, the counter tool's source sha256, kta3's reference files (ec7e1a8's, with their sha256, pairings, deals, seed
# bases and pairs files), and the cloud's km3 smoke and tool-test outputs all come from km_config.json through
# km_config.py (`shell`, eval'd below). Nothing in this file names a build, a baseline or a reference file of its own. A
# null (required) value in the config stops every part before anything is written; km_config.py also refuses any value
# the committed amendment fixes (the codes, the kt build, the official engine, the tool's source, the eight reference
# files with their sha256, pairings, deals, seed bases and pairs files) when it differs from the amendment's. The
# laptop's program hashes are recorded by part B in <out>/programs.txt and its "KM PART B DONE" line; every later part
# checks the programs against them before its first game and after its last, and read_km.py reads the same two records.
# THE ONE LIST (Amendment 1 (b) item 4): part I writes <out>/km_inputs.sha256 before its first game (km_check.py one-list
# write): the set as "# set" lines (the candidate, the baseline, B in full, the build folder, the tool's source sha256,
# the eight reference files and the cloud's outputs with their sha256, the three programs with theirs) and sha256sum
# lines for the config, the eight reference files, the cloud's outputs as extracted, the build's tool source and
# decks/research, every pairs file and deck list the runs read (equal to B's tree, part B's check), and the programs.
# Its sha256 goes to STATUS.txt as "KM INPUTS WRITTEN <S> <time> km_inputs.sha256 <sha256> ...", and it is committed with
# part I's record. From then on every check_pins (before each part's first game and after its last) runs `sha256sum -c`
# on it and km_check.py one-list check: the list's sha256 is the last "KM INPUTS (WRITTEN|CHANGED) <S>" line's, its set
# is the loaded config's entry by entry, the config loaded is the one it lists, programs.txt names exactly its programs,
# and every file has its sha256; any difference is a HALT. The runner never rewrites it: it changes only by a dated
# STATUS.txt line, "KM INPUTS CHANGED <S> <UTC time> km_inputs.sha256 <new sha256>: <why>", written by hand with the new
# list ((b) item 4). read_km.py makes the same check before it reads anything. Every game is played by the
# laptop's build of B (Amendment 1 (d) item 3: never the official program, whose kta<N> is the kp-based preset, and never
# 9c11b30's programs, which have the same kp-based presets; (d) item 4); every output name starts with B's short hash
# <S>_.
#
# Four parts, each invoked alone, in this order, one run at a time (flock on <out>/.run_km.lock):
#   bash run_km.sh B   the build (Amendment 1 (e) items 1-2). B and the round head must be commits on the config's
#        branch, B an ancestor of the round head, BUILD.md at the round head (in the round folder) must name B in full,
#        and B's engine/ must differ from the kt build ec7e1a8's (and so from the official 233bced's) in
#        engine/src/players/ only, engine/UPSTREAM.md aside ((c) item 2 and (e) item 1: `git diff ec7e1a8 B -- engine/
#        ':!engine/UPSTREAM.md'`; a notes file no build reads, which "stays as the branch has it"; whether it differs is
#        noted). git archive B engine decks into /home/dacz8976/engine-km-<S>, the counter tool's
#        source from B's tree (sha256 = the config's) as engine/examples/tool_census.rs, then cargo: deckgym,
#        legality_scan and tool_census. The build's decks/research must equal the working tree's (the table's lists),
#        and every pairs file the runs read and every deck list they name (clause (d)'s too) must equal B's tree byte
#        for byte ((b) item 4, "the deck lists from B's tree": km_check.py one-list tree).
#        Records the three programs' sha256 in <out>/programs.txt (from then on the pins) and in its "KM PART B DONE"
#        line, beside B in full and the tool's source sha256 ((e) item 3: "Its hashes first"), and copies the tool's
#        source as built to <out>/tool_census.rs. No game.
#   bash run_km.sh I   (e) item 3, the laptop's identity games at B, in its order and at its sizes (5,240 games). Needs
#        <out>/GO_km_build (Amendment 1 (g) step 3: Dustin's Sept 30 word on the build, which takes effect once the
#        cloud's round is committed as passed; the parent writes it then, after the tier-1 second read of B's diff, (g)
#        step 4) and, in the registered run, Amendment 1 committed ((g) step 1): REGISTRATION_DRAFT.md committed and
#        unchanged from HEAD, with its "## Amendment 1 ... kta" heading in HEAD's text. In the registered run the output
#        folder is km_tables_<today, UTC> at part I's first start ((c) item 4: named for "the date of the laptop's first
#        km game"; rename it, or set KM_OUT, if part B ran on an earlier day). kta3's reference files are
#        checked whole against the config first (km_check.py refs: sha256, every game kta3 on both sides on its deal;
#        committed on main in the registered run). Then km's one list, km_inputs.sha256, is written (once: a restart
#        checks it) and checked, before the first game ((b) item 4; (e) item 3). Through legality_scan, every page free
#        of rule findings, each run v
#        its reference on moves, decisions, openings, winner, points, seed, seats and deck files (every field where the
#        reference is the cloud's km3 smoke at B), deals as the references have them:
#          1. kta3 on the 28 table cells, i < 20 (560), v the table reference (ec7e1a8_kta3_table.jsonl);
#          2. kta3 on the 17 new cells, i < 20 (340), v the new17 reference (ec7e1a8_kta3_new17.jsonl);
#          3. km3 equal to kta3 on the 28 cells with neither damage Stadium, i < 20 (560: table 7, 9-12, 14-17, 22-27 v
#             the table reference; new_decks.tsv 10-15, 18-24 v the new17 reference);
#          4. km3 where N2 acts: pairings 0, 2 and 19, i < 40 (120), v the cloud's km3 smoke at B (the config's);
#          5. kta3 on the coverage references, i < 20 (2,660): B2e's 96 pairings, Scizor's 8 (new_decks.tsv 0-7), the
#             four second lists, each v its ec7e1a8 file, on the config's seed bases. A difference is a HALT like any
#             other ((e) item 4): step 5's replacement (kta3 at B on the group's 500 deals, entering the one list by a
#             dated line) has no code here; a failed coverage baseline stops and goes to Dustin, and the replacement
#             part is written only if he approves it.
#        Through the counter tool (the build's, from the build's engine/, whose ../decks/research is B's):
#          6. 8a's slice, --no-counts: kta3 on i < 20 of the 17 named cells (340 rows) v the table / new17 references,
#             and km3 on pairings 0 and 2, i < 40 (80 rows) v the cloud's km3 smoke: move fingerprint, both decks, seed
#             and seats (rows-v-games), with the number of cells asserted (17, and 2);
#          7. tool test 3's exact command (--seed-base 20000900000 --pairings 2 --games 20 --bot kp3 --rows-out
#             --trace-out): rows and trace byte-identical to the files B's round commits (the config's paths and sha256);
#          8. tool test 1's run of the tool (--games 20 --bot kp3 --games-out): stdout and games-out with the sha256 B's
#             STATUS.txt records (the config's).
#        One identity_check.txt line per check, "<k> <label>: <n> of <n> ... equal ...; PASS" (read_km.py's format).
#        They are recorded as agreement on the tested games (Amendment 1 (e), Dustin: "Describe cross-machine
#        verification as agreement on the tested games"), never as the programs being identical. Any difference,
#        missing game, rule finding, wrong cell count, program unlike its pin or tool source unlike the config's stops
#        with a "HALT" line ((e) item 4). Then STOP: (e) item 5 commits the pins, the check, its log, the game files and
#        the tool outputs "before the timing pair".
#   bash run_km.sh T   the timing pair, then the development sample and the thresholds ((g) step 4; step 3; section
#        4.0 steps 5-6). Needs part I done, GO_km_build and, in the registered run, part I's record committed and
#        unchanged ((e) item 5): programs.txt, tool_census.rs, km_inputs.sha256 (the one list), identity_check.txt (and
#        any identity_check_attempt<k>.txt), part I's game, row and tool-test files with their pages and logs, part I's
#        inputs record, run_km.sh, km_check.py, km_config.py and km_config.json; and HEAD's STATUS.txt holding the "KM
#        PART B DONE <S>" line, the "KM INPUTS WRITTEN|CHANGED <S>" line with the list's sha256, and a "KM PART I DONE
#        <S> ... knobs <knobs>" line.
#        1. The timing pair (section 4.1, "Timing", re-based by Amendment 1 (c) item 4): km3's 40-deal run on pairings 0
#           and 2 within 1.25 x kta3's wall time, both arms always fresh at B, user+sys CPU beside; if over, both arms
#           once more and the second pair decides; no other game program may run meanwhile. A restart does not get a new
#           pair unless KM_TIMING_RETRY='<written reason>' is set (the earlier files are kept as <S>_timing_attempt<k>_*).
#           A passed pair is recorded "KM TIMING DONE <S> ... knobs <knobs>" and not repeated.
#        2. In the registered run, km_thresholds.py committed and unchanged (step 5: "committed, with its sha256 and the
#           Python version, before the sample's first game").
#        3. The counter tool, deals 200-299 of the 14 gating cells, kta3 then km3 (1,400 games each). kta3's rows equal
#           the table / new17 references deal by deal (move fingerprint, both decks, seed, seats; a difference is a
#           HALT); km3's are checked for the right deals, seeds, seats, decks and bots now, and against km3's own games
#           in part R. Then km_thresholds.py writes thresholds.json and thresholds.txt (the counts, both rates, the
#           interval and T, nothing else). The tool's stdout table is not kept (nothing else in the sample is read).
#           STOP: the independent check and the thresholds amendment are the parent's.
#   A HALT in part I or T (a check that failed: "IDENTITY FAILED", "DIFFERENCE", "RULE FINDING", an incomplete run, a
#        program unlike its pin, the tool's source unlike the config's) is not replayed: that part refuses to start again
#        until KM_STOP_CAUSE='<the cause, found and written down>' is set, which is noted beside it ((e) item 4: "The
#        check is not repeated or resized to get past it; its cause is found and written down first"). An earlier
#        identity_check.txt is kept as identity_check_attempt<k>.txt, never emptied.
#   bash run_km.sh R   the registered games (section 5; section 7's rows 3-9, in that order), km3 against kta3
#        throughout. Needs part T done and <out>/GO_km_tables (written by the parent after Dustin's separate go-ahead
#        for the tables, (g) step 5 and block item 9) naming the committed amendment that wrote M1's and M2's numbers in
#        ("amendment <commit>"; section 4.0 steps 8-9) and the independent check's committed output ("check <path from
#        the repo root>"; step 7); in the registered run, thresholds.json first committed strictly before the check's
#        output, and that strictly before the amendment (steps 6, 7, 8: three commits, in that order, km_check.py
#        commit-order), the sample's two raw rows files first committed with thresholds.json or before it (step 7
#        computes the check "from those committed raw files"); km_inputs.sha256, the sample's raw files, the timing
#        pair's files, thresholds.json/.txt, km_thresholds.py, and the
#        reading code (footprint_km.py, read_km.py, test_read_km.sh, with km_config.py and km_config.json, which the
#        reader reads: section 4.0, "Reading code": "committed before any km result is read") committed and unchanged.
#        3. km3 on both sides of the 45 cells on the table's deals (500); footprint.txt by footprint_km.py (step 1: km3's
#           moves against the config's kta3 table / new17 references), for the parent to read and commit alone; the
#           sample's km3 arm against these games (deals 200-299).
#        4. the counters (step 3): kta3 then km3, deals 0-199 of the 17 cells, each arm checked deal by deal against its
#           own games (kta3: the table / new17 references; km3: step 3's games).
#        5. mixed rows on the 45 cells, both directions (km3 on one deck, kta3 on the other), 500 deals, on the cells
#           whose km3 games differ from kta3's references (section 7 row 5; clause (c)'s "pairings where km3's footprint
#           is non-zero"): coverage_skip.py's test.
#        6. clause (d): 9 rows x 2 arms x 2,000 deals: the table's deals 0-499 of the 9 Lucario cells and D2's block
#           22,900,000,000 + row x 10,000 + j (j < 1,500, Lucario first-named); arm kta3 (both sides) and arm km3 (km3 on
#           Lucario, kta3 on the other deck). Read once.
#        7-9. coverage: B2e (96 pairings), Scizor (8), the four second lists: km3 on both sides, then coverage_skip.py
#           (../../kta_2026-09-29/coverage_skip.py; Dustin's condition, block item 7) against kta3's coverage references
#           (the config's), then own-side mixed rows (km3 on the held deck / Scizor / the second list, kta3 on the panel
#           list) on every pairing it does not skip.
#
# STATUS.txt (in <out>) gets a note per step, and per part an anchored line:
#   "KM PART B DONE <S> <time> B <B in full> deckgym <sha> legality_scan <sha> tool_census <sha> (tool source <sha>)",
#   "KM INPUTS WRITTEN <S> <time> km_inputs.sha256 <sha> ...", "KM PART I DONE
#   <S> <time> knobs <knobs>", "KM TIMING DONE <S> <time> knobs <knobs>", "KM PART T DONE <S> <time> thresholds.json
#   <sha> knobs <knobs>", "KM PART R DONE <S> <time> knobs <knobs>", or "KM FAILED <time> <S>: part <X>: <why>" ("...
#   part <X>[: timing]: HALT: <why>" for a check that failed; a written cause is noted as "<time> KM STOP CAUSE <S> part
#   <X>: '<cause>' ..."). The last line matching ^KM (PART . DONE|FAILED) is the state. Resumable: an output is written
#   to .part and moved only when complete; a finished output is reused only when it is exactly the expected set of deals,
#   each the game that step plays (seed, seats, bots, decks), otherwise the run stops ("move it away first"). Inputs: at a
#   part's first start, the sha256 of every file its games and checks read besides the programs (the config among them)
#   goes to <out>/<S>_inputs_<part>.sha256; every step checks it and any change stops the part (KM_INPUTS_RENEW='<written
#   reason>' records a new list, noted). The runner is one function, main, called on the last line, so bash has read the
#   whole file before the first command runs.
#
# Usage (WSL): nohup setsid bash "rl/results/trainer_pricing_2026-09-28/km_run/run_km.sh" <B|I|T|R> > <log> 2>&1 &
#   Output folder: KM_OUT, else the one rl/results/km_tables_* folder, else rl/results/km_tables_<UTC date> (section
#   4.0, "Output folders"). KM_OUT is resolved as kta's runner resolves KTA_OUT.
# Knobs (environment): THREADS 12, NICE 10, BUILD_JOBS 14 (cargo), KM_BUILD (the build folder). The registered run is
#   CAND km3, CAND_LABEL km3, ID20 20 and ID40 40 ((e) item 3's sizes: i < 20 for part I's scan groups and 8a's kta3
#   slice, i < 40 for km3 on the smoke's pairings), TIMING_GAMES 40, SAMPLE_GAMES 100, GAMES 500, D_BLOCK 1500,
#   COUNTER_GAMES 200; any other value, and the smoke-only KM_STANDIN (a folder of stand-in programs copied in place of
#   cargo), KM_ALLOW_BUSY (time the pair while other game programs run) and KM_CONFIG (a stand-in config in place of
#   km_config.json), need KM_OUT outside rl/results. A smoke uses CAND=kta3 with a label other than kta3 and km3 (e.g.
#   ktax), so its games never sit in files named for either code; KM_CHECK_COMMITS=1 makes a smoke apply the registered
#   run's commit checks too (a smoke's own files are not in git, so those checks then refuse).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole runner (called on the last line; the body is left unindented)
PART=${1:-}
case $PART in B|I|T|R) ;; *) echo "usage: bash run_km.sh B|I|T|R (see the header)" >&2; exit 1;; esac
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
[ ! "$HERE" -ef "$R/rl/results/trainer_pricing_2026-09-28/km_run" ] || HERE="$R/rl/results/trainer_pricing_2026-09-28/km_run"
REG=rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md          # the registration and its amendments
SKIPPY="$R/rl/results/kta_2026-09-29/coverage_skip.py"
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
if [ -n "${KM_OUT:-}" ]; then O=$(canon_out "$KM_OUT") || { echo "run_km: cannot resolve KM_OUT $KM_OUT" >&2; exit 1; }
else
  shopt -s nullglob; ex=("$R"/rl/results/km_tables_*/); shopt -u nullglob
  case ${#ex[@]} in
    0) O="$R/rl/results/km_tables_$(date -u +%F)";;
    1) O=${ex[0]%/};;
    *) echo "run_km: ${#ex[@]} km_tables_* folders; set KM_OUT" >&2; exit 1;;
  esac
fi
SMOKE=1; case "$O/" in "$R"/rl/results/*) SMOKE=0;; esac
# ---- The one set (km_config.json), read before anything is written: a null required value stops here.
CFGF="$HERE/km_config.json"
if [ -n "${KM_CONFIG:-}" ]; then
  [ $SMOKE -eq 1 ] || { echo "run_km: KM_CONFIG (a stand-in config) is for smokes (KM_OUT outside rl/results); the registered run reads $CFGF" >&2; exit 1; }
  CFGF=$(realpath -- "$KM_CONFIG")
fi
CFGSH=$(python3 "$HERE/km_config.py" shell --config "$CFGF") \
  || { echo "run_km: $CFGF is not complete or not valid (km_config.py's STOP above); nothing was written" >&2; exit 1; }
eval "$CFGSH"   # CFG_CAND CFG_BASE COMMIT S BRANCH ROUND_HEAD ROUND_DIR KT_BUILD OFFICIAL TOOL_SRC(_SHA) SMOKE_* T3_* T1_* PINS_NAME; REFS* arrays
BC=$CFG_BASE                                                             # the baseline code, kta3, on every baseline side
[ "${REFSEED[table]}" = 72000000 ] || { echo "run_km: the table reference's seed base is not legality_scan's --decks base 72,000,000" >&2; exit 1; }
NEWD="$R/${REFPAIRS[new17]}"                                              # new_decks.tsv (the 17 new cells and Scizor)
[ "${REFPAIRS[scizor]}" = "${REFPAIRS[new17]}" ] && [ "${REFSEED[scizor]}" = "${REFSEED[new17]}" ] \
  || { echo "run_km: Scizor's pairings are new_decks.tsv's, on the new cells' seed base" >&2; exit 1; }
ref() { echo "$R/${REFS[$1]}"; }                                          # a reference file by group
B=${KM_BUILD:-/home/dacz8976/engine-km-$S}
GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"
CENSUS="$B/engine/target/release/examples/tool_census"; REF="$B/ref"
SM="$REF/${SMOKE_SRC##*/}"; T3R_REF="$REF/${T3_ROWS_SRC##*/}"; T3T_REF="$REF/${T3_TRACE_SRC##*/}"   # the cloud's outputs, from the round head
THREADS=${THREADS:-12}; NICE=${NICE:-10}; BUILD_JOBS=${BUILD_JOBS:-14}
CAND=${CAND:-$CFG_CAND}; CAND_LABEL=${CAND_LABEL:-$CAND}; CL=$CAND_LABEL
ID20=${ID20:-20}; ID40=${ID40:-40}; TIMING_GAMES=${TIMING_GAMES:-40}; SAMPLE_GAMES=${SAMPLE_GAMES:-100}; GAMES=${GAMES:-500}
D_BLOCK=${D_BLOCK:-1500}; COUNTER_GAMES=${COUNTER_GAMES:-200}
KNOBS="$CAND/$CL/$ID20/$ID40/$TIMING_GAMES/$SAMPLE_GAMES/$GAMES/$D_BLOCK/$COUNTER_GAMES"
REGISTERED="$CFG_CAND/$CFG_CAND/20/40/40/100/500/1500/200"
if [ $SMOKE -eq 0 ]; then
  [ "$KNOBS" = "$REGISTERED" ] || { echo "run_km: knobs $KNOBS are not the registered run; a smoke needs KM_OUT outside rl/results" >&2; exit 1; }
  [ -z "${KM_STANDIN:-}${KM_ALLOW_BUSY:-}" ] \
    || { echo "run_km: KM_STANDIN and KM_ALLOW_BUSY are for smokes (KM_OUT outside rl/results)" >&2; exit 1; }
fi
CHECK_COMMITS=1; [ $SMOKE -eq 0 ] || [ -n "${KM_CHECK_COMMITS:-}" ] || CHECK_COMMITS=0   # the registered run's commit checks
case $CAND in
  "$CFG_CAND") [ "$CL" = "$CFG_CAND" ] || { echo "run_km: CAND=$CFG_CAND needs CAND_LABEL=$CFG_CAND (the registered files' label)" >&2; exit 1; };;
  "$BC") case $CL in "$BC"|"$CFG_CAND") echo "run_km: a $BC smoke needs a label other than $BC and $CFG_CAND (e.g. CAND_LABEL=ktax)" >&2; exit 1;; esac;;
  *) echo "run_km: CAND must be $CFG_CAND (registered) or $BC (a smoke)" >&2; exit 1;;
esac
[[ $CL =~ ^[a-z0-9]+$ ]] || { echo "run_km: CAND_LABEL must be lower-case letters and digits" >&2; exit 1; }
for x in "$THREADS" "$NICE" "$BUILD_JOBS" "$ID20" "$ID40" "$TIMING_GAMES" "$SAMPLE_GAMES" "$GAMES" "$D_BLOCK" "$COUNTER_GAMES"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "run_km: knob value $x is not a number" >&2; exit 1; }
done
# ID20 reads deals of the 500-deal kta3 references; ID40 the cloud's 40-deal km3 smoke.
[ "$ID20" -ge 1 ] && [ "$ID20" -le "${REFDEALS[table]}" ] && [ "$ID40" -ge 1 ] && [ "$ID40" -le "$SMOKE_DEALS" ] \
  || { echo "run_km: ID20 must be 1-${REFDEALS[table]} and ID40 1-$SMOKE_DEALS (their references hold those deals)" >&2; exit 1; }
mkdir -p "$O"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
sha() { sha256sum -- "$1" | cut -d' ' -f1; }
others() { { ps -C legality_scan,deckgym,tool_census -o pid=,comm= 2>/dev/null || true; } | tr -s ' \n' ' ' | sed 's/^ *//; s/ *$//'; }
exec 9> "$O/.run_km.lock"; flock -n 9 || { note "run_km $PART: another km run holds the lock; this one exits"; exit 2; }
FINISHED=0; PHASE="part $PART (setup)"
die() { note "FAILED: $PHASE: $*"; echo "KM FAILED $(date -u +%FT%TZ) $S: $PHASE: $*" >> "$O/STATUS.txt"; FINISHED=1; exit 1; }
halt() { die "HALT: $*"; }   # a check that failed ((e) item 4): parts I and T then wait for KM_STOP_CAUSE
on_exit() {
  local rc=$?
  [ "$FINISHED" -eq 1 ] || echo "KM FAILED $(date -u +%FT%TZ) $S: $PHASE: stopped with exit code $rc outside a check (see the log)" >> "$O/STATUS.txt"
  [ -z "${TMPD:-}" ] || rm -rf -- "$TMPD"
}
TMPD=""
trap on_exit EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
note "KM PART $PART START $S: out $O; build $B (B = $COMMIT); $CL ($CAND) against $BC; config $CFGF (sha256 $(sha "$CFGF" | cut -c1-16)); knobs $KNOBS ($([ $SMOKE -eq 0 ] && echo "the registered run" || echo "NOT the registered run: a smoke")); commit checks $([ $CHECK_COMMITS -eq 1 ] && echo on || echo off); threads $THREADS, nice $NICE; load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $(others)"

# ---- Helpers.
PINS="$O/$PINS_NAME"   # sha256sum lines for the three programs (read_km.py reads the same file)
LIST="$O/km_inputs.sha256"; LIST_REQUIRED=0   # km's one list (Amendment 1 (b) item 4): written by part I, required after
INPUTS="$O/${S}_inputs_$PART.sha256"; INPUTS_READY=0; NOVERIFY=0
committed() {  # path: tracked by git and unchanged from HEAD
  local rel=${1#"$R"/}
  git -C "$R" ls-files --error-unmatch -- "$rel" > /dev/null 2>&1 && git -C "$R" diff --quiet HEAD -- "$rel"
}
need_done() {  # part [knobs|any]: that part's anchored DONE line is in STATUS.txt (with these knobs, unless "any")
  if [ "${2:-}" = any ]; then grep -Eq "^KM PART $1 DONE $S " "$O/STATUS.txt" && return 0
  else grep -Eq "^KM PART $1 DONE $S .* knobs $KNOBS\$" "$O/STATUS.txt" && return 0; fi
  die "part $1 has not passed here$([ "${2:-}" = any ] || echo " with knobs $KNOBS") (no 'KM PART $1 DONE $S' line in STATUS.txt)"
}
gate() {  # file reason: a GO file the parent writes; its first line is noted
  [ -s "$O/$1" ] || die "no $1 in $O: $2. The parent writes it (non-empty: where the word is recorded) when that is true; this part plays no game before"
  note "$1 present: $(head -n 1 "$O/$1")"
}
check_pins() {  # when: the build's commit (B), the three programs against the pins, the tool's source; then the inputs
  [ "$(cat "$B/COMMIT" 2>/dev/null)" = "$COMMIT" ] || die "$B/COMMIT is not B $COMMIT (part B builds it)"
  [ -s "$PINS" ] || die "no pins $PINS (part B records them)"
  local p out
  for p in "$GYM" "$SCAN" "$CENSUS"; do [ -x "$p" ] || die "no program $p"; done
  out=$(sha256sum -c --quiet --strict -- "$PINS" 2>&1) || halt "a program differs from its pin ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')"
  [ "$(sha "$B/engine/examples/tool_census.rs")" = "$TOOL_SRC_SHA" ] || halt "the build's tool_census.rs is not sha256 $TOOL_SRC_SHA ($1)"
  [ ! -e "$O/tool_census.rs" ] || [ "$(sha "$O/tool_census.rs")" = "$TOOL_SRC_SHA" ] || halt "$O/tool_census.rs is not sha256 $TOOL_SRC_SHA ($1)"
  if [ -e "$LIST" ] || [ "$LIST_REQUIRED" -eq 1 ]; then check_list "$1"; fi
  [ "$INPUTS_READY" -eq 0 ] || verify_inputs "$1"
}
check_list() {  # when: km's one list ((b) item 4) against the files (sha256sum -c) and the config, programs.txt and STATUS.txt
  local out
  [ -s "$LIST" ] || die "km's one list ${LIST##*/} is missing ($1): part I writes it before its first game and it is committed with part I's record (Amendment 1 (b) item 4)"
  out=$(cd "$R" && sha256sum -c --quiet --strict -- "$LIST" 2>&1) \
    || halt "a file differs from km's one list ${LIST##*/} ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')(it changes only by a dated 'KM INPUTS CHANGED' line in STATUS.txt, (b) item 4)"
  out=$(python3 "$HERE/km_check.py" one-list check --config "$CFGF" --root "$R" --build "$B" --out "$O" --programs "$PINS" 2>&1) \
    || halt "km's one list ${LIST##*/} ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')"
}
write_list() {  # part I, before its first game: km's one list, once; its sha256 in a dated STATUS.txt line ((b) item 4)
  local out
  if [ ! -e "$LIST" ]; then
    ! grep -Eq "^KM INPUTS (WRITTEN|CHANGED) $S " "$O/STATUS.txt" \
      || die "STATUS.txt records km's one list, but ${LIST##*/} is not in $O: restore it (it changes only by a dated STATUS.txt line, (b) item 4)"
    out=$(python3 "$HERE/km_check.py" one-list write --config "$CFGF" --root "$R" --build "$B" --programs "$PINS" --dest "$LIST.part" 2>&1) \
      || die "km's one list could not be written: $out"
    mv "$LIST.part" "$LIST"
    echo "KM INPUTS WRITTEN $S $(date -u +%FT%TZ) km_inputs.sha256 $(sha "$LIST") (Amendment 1 (b) item 4, km's one list, before part I's first game: B $COMMIT, $CFG_CAND against $BC, tool source $TOOL_SRC_SHA, programs as programs.txt; $out)" >> "$O/STATUS.txt"
  else
    grep -Eq "^KM INPUTS (WRITTEN|CHANGED) $S " "$O/STATUS.txt" \
      || die "${LIST##*/} is in $O but STATUS.txt has no 'KM INPUTS WRITTEN|CHANGED $S' line for it (a run stopped between writing it and recording it?): check it and record it by hand, or move it away, before any game"
    note "km's one list was written before ($(grep -E "^KM INPUTS (WRITTEN|CHANGED) $S " "$O/STATUS.txt" | tail -n 1 | cut -c1-120)); checked, not rewritten"
  fi
  LIST_REQUIRED=1
  check_list "part I, before its first game"
  note "km's one list checked: $(python3 "$HERE/km_check.py" one-list check --config "$CFGF" --root "$R" --build "$B" --out "$O" --programs "$PINS" | cut -c1-400)"
}
check_refs() {  # when: kta3's reference files, whole, against the config (Amendment 1 (b) item 3)
  local out; local -a args=(refs --config "$CFGF" --root "$R")
  [ $CHECK_COMMITS -eq 0 ] || args+=(--committed)
  out=$(python3 "$HERE/km_check.py" "${args[@]}" 2>&1) \
    || die "the reference files are not the config's ($1): $(echo "$out" | grep -v 'PASS$' | head -n 3 | tr '\n' ' ')"
  note "reference files ($1): $(grep -c 'PASS$' <<< "$out") of ${#REFS[@]} groups PASS: sha256 = the config's, every game $BC on both sides on its deal$([ $CHECK_COMMITS -eq 1 ] && echo ', committed and unchanged')"
}
input_list() { python3 "$HERE/km_check.py" inputs --part "$PART" --root "$R" --build "$B" --here "$HERE" --out "$O" --config "$CFGF"; }
verify_inputs() {  # when
  local out
  [ -s "$INPUTS" ] || die "the inputs record ${INPUTS##*/} is missing ($1)"
  out=$(cd "$R" && sha256sum -c --quiet --strict -- "$INPUTS" 2>&1) \
    || die "an input file changed since part $PART's first start ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')(${INPUTS##*/}; restore it, or set KM_INPUTS_RENEW='<written reason>')"
  out=$(diff <(cut -c67- "$INPUTS") <(input_list) 2>&1) \
    || die "the list of input files changed since part $PART's first start ($1): $(echo "$out" | grep '^[<>]' | head -n 3 | tr '\n' ' ')"
}
record_inputs() {  # at a part's first start (or with KM_INPUTS_RENEW), before its first game; then checked at every step
  local lst; local -a IN
  if [ -e "$INPUTS" ] && [ -n "${KM_INPUTS_RENEW:-}" ]; then
    mv "$INPUTS" "$INPUTS.renewed_$(date -u +%Y%m%dT%H%M%SZ)"; note "KM_INPUTS_RENEW='${KM_INPUTS_RENEW//$'\n'/ }': part $PART's inputs recorded afresh (the old record kept beside)"
  fi
  if [ ! -e "$INPUTS" ]; then
    lst=$(input_list) || die "km_check.py inputs failed"
    mapfile -t IN <<< "$lst"
    (cd "$R" && sha256sum -- "${IN[@]}") > "$INPUTS.part" || die "sha256 of part $PART's input files (is a listed file missing?)"
    mv "$INPUTS.part" "$INPUTS"
    note "part $PART's inputs recorded: ${#IN[@]} files, ${INPUTS##*/} (sha256 $(sha "$INPUTS" | cut -c1-16))"
  fi
  INPUTS_READY=1
  verify_inputs "part $PART start"
}
extract() {  # commit path dest [sha256]: a file from git, once; checked against the blob (and the sha256 when given)
  local c=$1 p=$2 d=$3
  mkdir -p "$(dirname "$d")"
  if [ ! -e "$d" ]; then git -C "$R" show "$c:$p" > "$d.part" || die "git show $c:$p"; mv "$d.part" "$d"; fi
  [ "$(git -C "$R" hash-object -- "$d")" = "$(git -C "$R" rev-parse "$c:$p")" ] || die "$d is not $c:$p: move it away first"
  [ -z "${4:-}" ] || [ "$(sha "$d")" = "$4" ] || die "$d is not sha256 $4 (the config's)"
}
rules() {  # page name: a RULE finding stops parts I and T, and is recorded (the reading stops until explained) in R
  local out
  if out=$(python3 "$HERE/km_check.py" rules "$O/$1.txt"); then return 0; fi
  [ "$PART" = R ] || halt "RULE FINDING: a scan page has a RULE finding or is incomplete: $out"
  note "RULE FINDING (the reading stops until it is explained): $out"; echo "$out" >> "$O/${S}_rule_findings.txt"
}
run() {  # name pairings games args...: legality_scan from the build's engine/ folder
  local name=$1 pl=$2 n=$3 s x out prev="" sb=72000000 pf="" bot="" ba="" bb=""; local -a chk; shift 3
  [ -n "$pl" ] || die "run $name: no pairings"
  for x in "$@"; do
    case $prev in --pairs) pf=$x;; --seed-base) sb=$x;; --bot) bot=$x;; --bot-a) ba=$x;; --bot-b) bb=$x;; esac
    prev=$x
  done
  ba=${ba:-$bot}; bb=${bb:-$bot}
  [ -n "$ba" ] && [ -n "$bb" ] || die "run $name: no bots named"
  chk=(--pairings "$pl" --games "$n" --seed-base "$sb" --bot-a "$ba" --bot-b "$bb")
  if [ -n "$pf" ]; then chk+=(--pairs "$pf"); else chk+=(--decks); fi
  [ "$NOVERIFY" -eq 1 ] || verify_inputs "before $name"
  if [ -e "$O/$name.jsonl" ]; then
    out=$(python3 "$HERE/km_check.py" complete "$O/$name.jsonl" "${chk[@]}") \
      || die "$name.jsonl is there but is not the expected complete output ($out): move it away first"
    [ -e "$O/$name.txt" ] || die "$name.jsonl is there without its page $name.txt: move it away first"
    rules "$name"; return 0
  fi
  s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$SCAN" "$@" --pairings "$pl" --games "$n" \
      --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt" 2>&1 || die "$name (see $name.txt)"
  [ "$NOVERIFY" -eq 1 ] || verify_inputs "after $name"
  out=$(python3 "$HERE/km_check.py" complete "$O/$name.jsonl.part" "${chk[@]}") \
    || halt "$name: the scan's output is not the expected complete set of deals ($out)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
  rules "$name"
}
rows_run() {  # name cells first games code counts(yes|no) [quiet]: the counter tool, one row per game
  local name=$1 cells=$2 first=$3 n=$4 code=$5 counts=$6 quiet=${7:-} s out so; local -a args chk
  args=(--cells km17); [ "$cells" = km17 ] || args+=(--pairings "$cells")
  args+=(--first-deal "$first" --games "$n" --bot "$code" --decks ../decks/research --root "$R")
  chk=(--cells "$cells" --first-deal "$first" --games "$n" --bot "$code" --root "$R")
  if [ "$counts" = yes ]; then chk+=(--counts); else args+=(--no-counts); chk+=(--no-counts); fi
  verify_inputs "before $name"
  if [ -e "$O/$name.jsonl" ]; then
    out=$(python3 "$HERE/km_check.py" rows-complete "$O/$name.jsonl" "${chk[@]}") \
      || die "$name.jsonl is there but is not the expected complete rows ($out): move it away first"
    return 0
  fi
  so="$O/$name.txt"; [ -z "$quiet" ] || so=/dev/null
  s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$CENSUS" "${args[@]}" --rows-out "$O/$name.jsonl.part" ) \
    > "$so" 2> "$O/$name.log" || die "$name (see $name.log)"
  verify_inputs "after $name"
  out=$(python3 "$HERE/km_check.py" rows-complete "$O/$name.jsonl.part" "${chk[@]}") \
    || halt "$name: the tool's rows are not the expected complete set ($out)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") rows)"
}
rows_v_games() {  # label rows from to table new17: step 3's deal-by-deal check of a measuring run; any difference stops
  python3 "$HERE/km_check.py" rows-v-games "$2" --from "$3" --to "$4" --table "$5" --new17 "$6" --label "$1" \
    >> "$O/${S}_rows_checks.txt" || halt "DIFFERENCE: $1 (see ${S}_rows_checks.txt): the reading stops"
  note "$(tail -n 1 "$O/${S}_rows_checks.txt")"
}
same() {  # label mine ref max_i expect fields [more]: identity at the laptop's build; any difference stops
  [ -s "$3" ] || die "identity reference $3 is missing"
  python3 "$HERE/km_check.py" same "$2" "$3" --max-i "$4" --expect "$5" --label "$1" --fields "$6" >> "$O/identity_check.txt" \
    || halt "IDENTITY FAILED: $1 (see identity_check.txt)${7:-}"
}
rows_id() {  # label rows from to table new17|"" cells: the counter tool's rows v game files (8a's slice), cells asserted
  local -a nw=(); [ -z "$6" ] || nw=(--new17 "$6")
  [ -s "$5" ] || die "identity reference $5 is missing"
  python3 "$HERE/km_check.py" rows-v-games "$2" --from "$3" --to "$4" --table "$5" "${nw[@]}" --label "$1" --cells "$7" \
    >> "$O/identity_check.txt" || halt "IDENTITY FAILED: $1 (see identity_check.txt)"
}
stop_gate() {  # parts I and T: after a HALT of this part, no start until its cause is written down (KM_STOP_CAUSE)
  local ln
  ln=$({ grep -nE "^KM FAILED [^ ]+ $S: part $PART(: [a-z]+)?: HALT: " "$O/STATUS.txt" || true; } | tail -n 1 | cut -d: -f1)
  [ -n "$ln" ] || return 0
  [ "$(tail -n +"$ln" "$O/STATUS.txt" | { grep -cE "^[0-9T:Z-]+ KM STOP CAUSE $S part $PART: " || true; })" -eq 0 ] || return 0
  [ -n "${KM_STOP_CAUSE:-}" ] || die "part $PART stopped on a check before (STATUS.txt line $ln: $(sed -n "${ln}p" "$O/STATUS.txt" | cut -c1-260)). Amendment 1 (e) item 4: 'The check is not repeated or resized to get past it; its cause is found and written down first.' Set KM_STOP_CAUSE='<the cause>' (noted in STATUS.txt) to start part $PART again; nothing was moved or emptied"
  note "KM STOP CAUSE $S part $PART: '${KM_STOP_CAUSE//$'\n'/ }' (the stop it answers, STATUS.txt line $ln: $(sed -n "${ln}p" "$O/STATUS.txt" | cut -c1-260))"
}
part_I_record() {  # the files part I leaves ((e) item 5: committed before the timing pair)
  local f
  shopt -s nullglob
  for f in "$PINS" "$O/tool_census.rs" "$LIST" "$O/identity_check.txt" "$O"/identity_check_attempt*.txt "$O/${S}_inputs_I.sha256"* \
           "$O/${S}_laptop_id_"* "$O/${S}_laptop_tool_test"* "$HERE/run_km.sh" "$HERE/km_check.py" "$HERE/km_config.py" "$CFGF"; do
    echo "$f"
  done
  shopt -u nullglob
}
minus() { python3 -c 'import sys; r = set(x for x in sys.argv[2].split(",") if x); print(",".join(x for x in sys.argv[1].split(",") if x and x not in r))' "$1" "$2"; }
baseline() {  # a kta3 reference file; a smoke with fewer deals than 500 reads a copy cut to i < GAMES
  if [ $SMOKE -eq 1 ] && [ "$GAMES" -lt 500 ]; then
    local c="$O/smoke_ref/${1##*/}"; mkdir -p "$O/smoke_ref"
    [ -e "$c" ] || python3 -c 'import json, sys; n = int(sys.argv[3]); open(sys.argv[2], "w").writelines(l for l in open(sys.argv[1]) if json.loads(l)["i"] < n)' "$1" "$c" "$GAMES"
    echo "$c"
  else echo "$1"; fi
}
skip() {  # group base cand pairings deals context: coverage_skip.py; prints the pairings whose mixed rows run
  python3 "$SKIPPY" --group "$1" --base "$2" --cand "$3" --pairings "$4" --deals "$5" --context "$6" \
    --report "$O/${S}_skip_$1.txt" --json "$O/${S}_skip_$1.json" --base-code "$BC" --cand-code "$CAND" || return $?
  local g
  { echo "coverage_skip.txt: the coverage shortcut's comparisons (../../kta_2026-09-29/coverage_skip.py; $CL against $BC's references; one report per group, in the runner's order)"
    for g in table new17 b2e scizor var_v-lucario_2 var_v-suicune_2 var_v-weezing_2 var_l-charizardy; do
      [ ! -e "$O/${S}_skip_$g.txt" ] || { echo; cat "$O/${S}_skip_$g.txt"; }
    done; } > "$O/coverage_skip.txt.part" && mv "$O/coverage_skip.txt.part" "$O/coverage_skip.txt"
}
npairs() { awk -F, '{print NF}' <<< "$1"; }

# =====================================================================================================================
part_B() {
PHASE="part B"
if grep -Eq "^KM PART B DONE $S " "$O/STATUS.txt" && [ -s "$PINS" ]; then
  check_pins "part B, done before"
  note "part B was done before ($(grep -E "^KM PART B DONE $S " "$O/STATUS.txt" | tail -n 1)); the programs still equal their pins; nothing rebuilt"
  FINISHED=1; return 0
fi
source "$HOME/.cargo/env" 2>/dev/null || true
git -C "$R" fetch -q origin || note "git fetch failed; using the local objects"
git -C "$R" cat-file -e "$COMMIT^{commit}" || die "no commit $COMMIT (B, the config's build.commit; fetch origin)"
git -C "$R" cat-file -e "$ROUND_HEAD^{commit}" || die "no commit $ROUND_HEAD (the config's build.round_head; fetch origin)"
git -C "$R" merge-base --is-ancestor "$COMMIT" "$ROUND_HEAD" || die "B $S is not an ancestor of the round head ${ROUND_HEAD:0:7}"
git -C "$R" merge-base --is-ancestor "$ROUND_HEAD" "$BRANCH" || die "the round head ${ROUND_HEAD:0:7} is not on $BRANCH"
bm=$(git -C "$R" show "$ROUND_HEAD:$ROUND_DIR/BUILD.md" 2> /dev/null) || die "no $ROUND_DIR/BUILD.md at the round head ${ROUND_HEAD:0:7}"
grep -qF "$COMMIT" <<< "$bm" || die "$ROUND_DIR/BUILD.md at the round head ${ROUND_HEAD:0:7} does not name B $COMMIT in full (Amendment 1 (c) item 2)"
for x in "$KT_BUILD" "$OFFICIAL"; do   # (e) item 1; (c) item 2: players/ only, from ec7e1a8 and so from 233bced, UPSTREAM.md aside
  outside=$(git -C "$R" diff --name-only "$x" "$COMMIT" -- engine/ ':!engine/UPSTREAM.md' | grep -v '^engine/src/players/' || true)
  [ -z "$outside" ] || die "Amendment 1 (e) item 1: B's engine/ differs from ${x:0:7}'s outside engine/src/players/ (engine/UPSTREAM.md aside): $(echo $outside)"
done
up=$(git -C "$R" diff --quiet "$KT_BUILD" "$COMMIT" -- engine/UPSTREAM.md && echo "is ec7e1a8's" || echo "differs from ec7e1a8's (exempt: (c) item 2, a notes file no build reads, 'it stays as the branch has it')")
note "(e) item 1: git diff ${KT_BUILD:0:7} $S -- engine/ ':!engine/UPSTREAM.md' changes $(git -C "$R" diff --name-only "$KT_BUILD" "$COMMIT" -- engine/ ':!engine/UPSTREAM.md' | tr '\n' ' ')(players/ only; from the official ${OFFICIAL:0:7} too); engine/UPSTREAM.md $up; BUILD.md at the round head ${ROUND_HEAD:0:7} names B"
TMPD=$(mktemp -d)
git -C "$R" show "$COMMIT:$TOOL_SRC" > "$TMPD/tool_census.rs" || die "git show $S:$TOOL_SRC"
[ "$(sha "$TMPD/tool_census.rs")" = "$TOOL_SRC_SHA" ] || die "(e) item 2: the counter tool's source in B's tree is sha256 $(sha "$TMPD/tool_census.rs"), not the config's $TOOL_SRC_SHA; it is not built or used"
note "(e) item 2: the counter tool's source ($S:$TOOL_SRC) is sha256 $TOOL_SRC_SHA, the config's"
mkdir -p "$TMPD/tree"; git -C "$R" archive "$COMMIT" engine decks | tar -x -C "$TMPD/tree"
if [ -e "$B" ]; then
  [ "$(cat "$B/COMMIT" 2>/dev/null)" = "$COMMIT" ] || die "$B exists and is not the build of $COMMIT: move it away first"
  diff -rq -x target -x tool_census.rs "$TMPD/tree/engine" "$B/engine" > /dev/null \
    || die "$B/engine is not $S's engine/ (plus the tool): $(diff -rq -x target -x tool_census.rs "$TMPD/tree/engine" "$B/engine" | head -n 3 | tr '\n' ' ')move it away first"
  diff -rq "$TMPD/tree/decks" "$B/decks" > /dev/null || die "$B/decks is not $S's decks/: move it away first"
  cmp -s "$TMPD/tool_census.rs" "$B/engine/examples/tool_census.rs" || die "$B's tool_census.rs is not the pinned source: move it away first"
  note "$B exists: $S's engine/ and decks/ and the tool's source exactly (a build there resumes)"
else
  mkdir -p "$B"; cp -r "$TMPD/tree/engine" "$TMPD/tree/decks" "$B/"
  cp "$TMPD/tool_census.rs" "$B/engine/examples/tool_census.rs"; echo "$COMMIT" > "$B/COMMIT"
  note "$B written: git archive $S engine decks, the counter tool's source as engine/examples/tool_census.rs"
fi
for f in "$B"/decks/research/*.txt; do  # the table's lists: the build's copy (--decks) equals the working tree's
  cmp -s "$f" "$R/decks/research/${f##*/}" || die "decks/research/${f##*/} in the working tree differs from $S's"
done
# (b) item 4, "the deck lists from B's tree": every pairs file the --pairs runs read from the working tree, every deck
# list they name, clause (d)'s lists and decks/research's, byte for byte B's (km_inputs.sha256 then pins them).
out=$(python3 "$HERE/km_check.py" one-list tree --config "$CFGF" --root "$R") || die "the working tree is not B's for the lists the runs read: $out"
note "$out"
if [ -n "${KM_STANDIN:-}" ]; then
  mkdir -p "$B/engine/target/release/examples"
  cp "$KM_STANDIN/deckgym" "$GYM"; cp "$KM_STANDIN/legality_scan" "$SCAN"; cp "$KM_STANDIN/tool_census" "$CENSUS"
  note "SMOKE: no cargo; stand-in programs from $KM_STANDIN copied in (plumbing only)"
else
  note "cargo $(cargo --version 2>/dev/null || echo '?'), $(rustc --version 2>/dev/null || echo 'rustc ?'); building in $B/engine (-j $BUILD_JOBS, nice $NICE)"
  ( cd "$B/engine" && nice -n "$NICE" cargo build --release -j "$BUILD_JOBS" \
      && nice -n "$NICE" cargo build --release --example legality_scan --example tool_census -j "$BUILD_JOBS" ) \
    > "$O/${S}_build.log" 2>&1 || die "the build (${S}_build.log)"
fi
for p in "$GYM" "$SCAN" "$CENSUS"; do [ -x "$p" ] || die "the build left no program $p"; done
diff -rq -x target -x tool_census.rs "$TMPD/tree/engine" "$B/engine" > /dev/null \
  || die "the build changed $B/engine's sources: $(diff -rq -x target -x tool_census.rs "$TMPD/tree/engine" "$B/engine" | head -n 3 | tr '\n' ' ')"
sha256sum -- "$GYM" "$SCAN" "$CENSUS" > "$PINS.new"
if [ -e "$PINS" ]; then
  cmp -s "$PINS.new" "$PINS" || die "the programs built now differ from the pins recorded before ($PINS): games already played bind to those; a new build needs a new output folder"
  rm -f "$PINS.new"
else mv "$PINS.new" "$PINS"; fi
if [ -e "$O/tool_census.rs" ]; then cmp -s "$O/tool_census.rs" "$B/engine/examples/tool_census.rs" || die "$O/tool_census.rs is not the source built"
else cp "$B/engine/examples/tool_census.rs" "$O/tool_census.rs"; fi   # the counter tool's source as built
check_pins "after the build"
note "pins (${PINS##*/}): deckgym $(sha "$GYM"), legality_scan $(sha "$SCAN"), tool_census $(sha "$CENSUS"). The cloud's programs differ by machine (a Rust build embeds its paths); part I's games at this build are checked as agreement on the tested games (Amendment 1 (e))"
FINISHED=1
echo "KM PART B DONE $S $(date -u +%FT%TZ) B $COMMIT deckgym $(sha "$GYM") legality_scan $(sha "$SCAN") tool_census $(sha "$CENSUS") (tool source $TOOL_SRC_SHA)" >> "$O/STATUS.txt"
}

# =====================================================================================================================
part_I() {
PHASE="part I"
need_done B any
if grep -Eq "^KM PART I DONE $S .* knobs $KNOBS\$" "$O/STATUS.txt"; then
  check_pins "part I, done before"; note "part I passed before with these knobs; not repeated"; FINISHED=1; return 0
fi
stop_gate
gate GO_km_build "Dustin's Sept 30 word on the build (Amendment 1 (g) step 3), in effect once the cloud's round is committed as passed, and the tier-1 second read of B's diff done ((g) step 4)"
local f a1 out
if [ $CHECK_COMMITS -eq 1 ]; then  # (g) step 1: the amendment is committed before any km game
  committed "$R/$REG" || die "$REG is not committed, or differs from HEAD: part I plays Amendment 1 (e) item 3, and (g) step 1 commits the amendment before any km game. Commit the amendment first"
  grep -Eq '^## Amendment 1 .*kta' <(git -C "$R" show "HEAD:$REG") || die "HEAD's $REG has no '## Amendment 1 ... kta' section: part I plays Amendment 1 (e) item 3, which is not committed"
  a1=$(git -C "$R" log -S'## Amendment 1 ' --format=%h HEAD -- "$REG" | head -n 1)
  note "Amendment 1 is committed (last changed in ${a1:-?}); $REG is unchanged from HEAD $(git -C "$R" rev-parse --short HEAD)"
fi
if [ $SMOKE -eq 0 ] && [ ! -e "$LIST" ] && [ "${O##*/}" != "km_tables_$(date -u +%F)" ]; then   # (c) item 4
  die "the output folder is ${O##*/}, but (c) item 4 names it km_tables_<date of the laptop's first km game>, and part I's first game is today, km_tables_$(date -u +%F) (UTC). Rename the folder (nothing in it binds to its name before part I), or set KM_OUT, then start part I again"
fi
check_pins "part I start"
check_refs "part I start"
extract "$ROUND_HEAD" "$SMOKE_SRC" "$SM" "$SMOKE_SHA"                    # the cloud's km3 smoke at B (identity 7)
out=$(python3 "$HERE/km_check.py" complete "$SM" --pairings "$SMOKE_PAIRINGS" --games "$SMOKE_DEALS" --seed-base 72000000 \
        --bot-a "$CFG_CAND" --bot-b "$CFG_CAND" --decks) || die "the cloud's km3 smoke is not the complete set the config names: $out"
note "the cloud's km3 smoke: $out"
extract "$ROUND_HEAD" "$T3_ROWS_SRC" "$T3R_REF" "$T3_ROWS_SHA"
extract "$ROUND_HEAD" "$T3_TRACE_SRC" "$T3T_REF" "$T3_TRACE_SHA"
write_list   # km's one list, before the first game ((b) item 4; (e) item 3: "Its hashes first")
record_inputs
if [ -s "$O/identity_check.txt" ]; then   # an earlier start's record is kept, never emptied ((e) item 4)
  f=1; while [ -e "$O/identity_check_attempt$f.txt" ]; do f=$((f + 1)); done
  mv "$O/identity_check.txt" "$O/identity_check_attempt$f.txt"
  note "the earlier identity_check.txt is kept as identity_check_attempt$f.txt; this start writes a new one"
fi
: > "$O/identity_check.txt"
# (e) item 3, in its order and at its sizes: i < 20 (ID20) for the scan groups and 8a's kta3 slice, i < 40 (ID40) for km3
# on the smoke's pairings. Deals as the references have them. A kta3 smoke's "km3" arm is kta3, so it is held against
# kta3's table reference.
local I=$ID20 J=$ID40 n v g np s k T15 N13 t3r t3t t1o t1g kref kfields
local -a TAB NEW
T15=7,9,10,11,12,14,15,16,17,22,23,24,25,26,27; N13=10,11,12,13,14,15,18,19,20,21,22,23,24   # the 28 cells with neither damage Stadium
TAB=(--decks ../decks/research); NEW=(--pairs "$NEWD" --root "$R" --seed-base "${REFSEED[new17]}")
if [ "$CAND" = "$CFG_CAND" ]; then kref=$SM; kfields=all; else kref=$(ref table); kfields=id; fi
# 1. kta3 on the 28 table cells, i < 20 (560), v the table reference.
n=${S}_laptop_id_${BC}_table_i$I; run $n "${REFPAIRINGS[table]}" $I "${TAB[@]}" --bot "$BC"
same "1 $BC, laptop build, the 28 table cells, i < $I, v ${REFS[table]##*/}" "$O/$n.jsonl" "$(ref table)" $I $(( $(npairs "${REFPAIRINGS[table]}") * I )) id
# 2. kta3 on the 17 new cells, i < 20 (340), v the new17 reference.
n=${S}_laptop_id_${BC}_new17_i$I; run $n "${REFPAIRINGS[new17]}" $I "${NEW[@]}" --bot "$BC"
same "2 $BC, laptop build, the 17 new cells, i < $I, v ${REFS[new17]##*/}" "$O/$n.jsonl" "$(ref new17)" $I $(( $(npairs "${REFPAIRINGS[new17]}") * I )) id
# 3. km3 equal to kta3 on the 28 cells with neither damage Stadium, i < 20 (560), v the same deals of kta3's references.
n=${S}_laptop_id_${CL}_table15_i$I; run $n "$T15" $I "${TAB[@]}" --bot "$CAND"
same "3 $CL (as $CAND) equal to $BC, laptop build, the 15 table cells with neither damage Stadium, i < $I, v ${REFS[table]##*/}" \
  "$O/$n.jsonl" "$(ref table)" $I $((15 * I)) id
n=${S}_laptop_id_${CL}_new13_i$I; run $n "$N13" $I "${NEW[@]}" --bot "$CAND"
same "3 $CL (as $CAND) equal to $BC, laptop build, the 13 new cells with neither damage Stadium, i < $I, v ${REFS[new17]##*/}" \
  "$O/$n.jsonl" "$(ref new17)" $I $((13 * I)) id
# 4. km3 where N2 acts: the smoke's pairings (0, 2 and 19), i < 40 (120), v the cloud's km3 smoke at B.
n=${S}_laptop_id_${CL}_smoke_i$J; run $n "$SMOKE_PAIRINGS" $J "${TAB[@]}" --bot "$CAND"
same "4 $CL (as $CAND), laptop build, pairings $SMOKE_PAIRINGS (where N2 acts), i < $J, v ${kref##*/}" \
  "$O/$n.jsonl" "$kref" $J $(( $(npairs "$SMOKE_PAIRINGS") * J )) $kfields
# 5. kta3 on the coverage references, i < 20 (2,660), each on its own seed base and pairs file.
for g in b2e scizor var_v-lucario_2 var_v-suicune_2 var_v-weezing_2 var_l-charizardy; do
  np=$(npairs "${REFPAIRINGS[$g]}")
  n=${S}_laptop_id_${g}_${BC}_i$I
  run $n "${REFPAIRINGS[$g]}" $I --pairs "$R/${REFPAIRS[$g]}" --root "$R" --seed-base "${REFSEED[$g]}" --bot "$BC"
  same "5 $BC, laptop build, $g ($np pairings), i < $I, v ${REFS[$g]##*/}" "$O/$n.jsonl" "$(ref "$g")" $I $((np * I)) id \
    ". A failed coverage baseline stops here and goes to Dustin: step 5's replacement (kta3 at B on the group's 500 deals, entering km_inputs.sha256 by a dated line, (b) item 4) has no code until he approves it"
done
# 6. The counter tool, 8a's slice, --no-counts: kta3 on i < 20 of the 17 named cells (340) v kta3's references; km3 on
#    pairings 0 and 2, i < 40 (80) v the cloud's smoke; fingerprint, both decks, seed, seats; cells asserted.
n=${S}_laptop_id_tool_${BC}_km17_i$I; rows_run $n km17 0 $I "$BC" no
rows_id "6 the counter tool's $BC (8a's slice, --no-counts), laptop build, the 17 named cells, i < $I, v ${REFS[table]##*/} / ${REFS[new17]##*/}" \
  "$O/$n.jsonl" 0 $((I - 1)) "$(ref table)" "$(ref new17)" 17
n=${S}_laptop_id_tool_${CL}_p02_i$J; rows_run $n table:0,table:2 0 $J "$CAND" no
rows_id "6 the counter tool's $CL (as $CAND; 8a's slice, --no-counts), laptop build, pairings 0 and 2, i < $J, v ${kref##*/}" \
  "$O/$n.jsonl" 0 $((J - 1)) "$kref" "" 2
# 7. Tool test 3's exact command (check_tool.sh's test 3; kp3 on diagnostic seeds 20,000,920,000-019): its rows and its
#    trace byte for byte the files B's round commits. The build's engine/ is the cwd, as check_tool.sh runs it.
t3r="$O/${S}_laptop_tool_test3_trace_rows.jsonl"; t3t="$O/${S}_laptop_tool_test3_trace.tsv"
if [ -e "$t3r" ] || [ -e "$t3t" ]; then
  [ -e "$t3r" ] && [ -e "$t3t" ] || die "only one of tool test 3's two outputs is in $O: move it away first"
  note "tool test 3's outputs are there from an earlier start: compared again, not replayed"
else
  verify_inputs "before tool test 3"; s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$CENSUS" --seed-base 20000900000 --pairings 2 --games 20 --bot kp3 \
      --rows-out "$t3r.part" --trace-out "$t3t.part" ) > "$O/${S}_laptop_tool_test3.txt" 2> "$O/${S}_laptop_tool_test3.log" \
    || die "tool test 3 (see ${S}_laptop_tool_test3.log)"
  verify_inputs "after tool test 3"
  mv "$t3r.part" "$t3r"; mv "$t3t.part" "$t3t"
  note "tool test 3 played in $(( $(date +%s) - s )) s ($(wc -l < "$t3r") games)"
fi
k=0
if cmp -s "$t3r" "$T3R_REF" && [ "$(sha "$t3r")" = "$T3_ROWS_SHA" ]; then k=$((k + 1)); fi
if cmp -s "$t3t" "$T3T_REF" && [ "$(sha "$t3t")" = "$T3_TRACE_SHA" ]; then k=$((k + 1)); fi
echo "7 tool test 3's exact command, laptop build (kp3, Altaria v Lucario, seeds 20,000,920,000-019, 20 games; counts compared byte for byte, none read): $k of 2 files equal byte for byte to B's round's ${T3_ROWS_SRC##*/} and ${T3_TRACE_SRC##*/} (cmp; sha256 $(sha "$t3r" | cut -c1-16) and $(sha "$t3t" | cut -c1-16), expected ${T3_ROWS_SHA:0:16} and ${T3_TRACE_SHA:0:16}); $([ $k -eq 2 ] && echo PASS || echo FAIL)" >> "$O/identity_check.txt"
[ $k -eq 2 ] || halt "IDENTITY FAILED: tool test 3's rows or trace differ from B's round's (see identity_check.txt)"
# 8. Tool test 1's run of the tool (kp3, the table's first 20 deals of the 28 pairings, 560 games): its stdout and
#    games-out with the sha256 B's STATUS.txt records.
t1o="$O/${S}_laptop_tool_test1_stdout.txt"; t1g="$O/${S}_laptop_tool_test1_games.jsonl"
if [ -e "$t1o" ] || [ -e "$t1g" ]; then
  [ -e "$t1o" ] && [ -e "$t1g" ] || die "only one of tool test 1's two outputs is in $O: move it away first"
  note "tool test 1's outputs are there from an earlier start: compared again, not replayed"
else
  verify_inputs "before tool test 1"; s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$CENSUS" --games 20 --bot kp3 --games-out "$t1g.part" ) \
    > "$t1o.part" 2> "$O/${S}_laptop_tool_test1.log" || die "tool test 1 (see ${S}_laptop_tool_test1.log)"
  verify_inputs "after tool test 1"
  mv "$t1g.part" "$t1g"; mv "$t1o.part" "$t1o"
  note "tool test 1 played in $(( $(date +%s) - s )) s ($(wc -l < "$t1g") games)"
fi
k=0
if [ "$(sha "$t1o")" = "$T1_STDOUT_SHA" ]; then k=$((k + 1)); fi
if [ "$(sha "$t1g")" = "$T1_GAMES_SHA" ]; then k=$((k + 1)); fi
echo "8 tool test 1's run of the tool, laptop build (kp3, the table's first 20 deals of the 28 pairings, 560 games; counts compared byte for byte, none read): $k of 2 outputs equal byte for byte to B's round's by sha256 (stdout $(sha "$t1o" | cut -c1-16), games-out $(sha "$t1g" | cut -c1-16); expected ${T1_STDOUT_SHA:0:16} and ${T1_GAMES_SHA:0:16}); $([ $k -eq 2 ] && echo PASS || echo FAIL)" >> "$O/identity_check.txt"
[ $k -eq 2 ] || halt "IDENTITY FAILED: tool test 1's stdout or games-out differ from B's round's (see identity_check.txt)"
check_pins "after the identity games"
note "identity at the laptop's build (Amendment 1 (e) item 3), recorded as agreement on the tested games: $(grep -c . "$O/identity_check.txt") checks, every one PASS: $(tr '\n' ' ' < "$O/identity_check.txt" | cut -c1-3000)"
FINISHED=1
echo "KM PART I DONE $S $(date -u +%FT%TZ) knobs $KNOBS" >> "$O/STATUS.txt"
note "STOP after part I: (e) item 5 commits the pins, identity_check.txt, its log, the game files and the tool outputs before the timing pair (part T checks them)"
}

# =====================================================================================================================
part_T() {
PHASE="part T"
LIST_REQUIRED=1   # km's one list, from part I: checked with the pins before the first game and after the last
need_done I
local tj="$O/thresholds.json" tt="$O/thresholds.txt" kt="$HERE/km_thresholds.py" n0 n1 prev
prev=$(sed -n "s#^KM PART T DONE $S [^ ]* thresholds.json \([0-9a-f]*\) knobs $KNOBS\$#\1#p" "$O/STATUS.txt" | tail -n 1)
if [ -n "$prev" ]; then
  [ "$(sha "$tj")" = "$prev" ] || die "thresholds.json is not the file part T wrote (sha256 $prev)"
  check_pins "part T, done before"; note "part T passed before (thresholds.json sha256 $prev); not repeated"; FINISHED=1; return 0
fi
stop_gate
gate GO_km_build "Dustin's Sept 30 word on the build (Amendment 1 (g) step 3): the timing pair, the threshold sample and the independent check"
check_pins "part T start"
local -a REC; local hs f nrec=0
if [ $CHECK_COMMITS -eq 1 ]; then
  # (e) item 5: part I's pins, check, log, game files and tool outputs are committed before the timing pair.
  mapfile -t REC < <(part_I_record)
  for f in "${REC[@]}"; do
    committed "$f" || die "${f#"$R"/} is not committed, or differs from HEAD: Amendment 1 (e) item 5 commits part I's pins, check, log, game files and tool outputs before the timing pair"
  done
  hs=$(git -C "$R" show "HEAD:${O#"$R"/}/STATUS.txt" 2>/dev/null) || die "${O#"$R"/}/STATUS.txt is not committed: it is part I's log ((e) item 5)"
  grep -Eq "^KM PART B DONE $S " <<< "$hs" || die "HEAD's STATUS.txt has no 'KM PART B DONE $S' line: the pins are committed with the log that records them ((e) item 5)"
  grep -Eq "^KM PART I DONE $S .* knobs $KNOBS\$" <<< "$hs" || die "HEAD's STATUS.txt has no 'KM PART I DONE $S ... knobs $KNOBS' line: part I is committed as passed before the timing pair ((e) item 5)"
  grep -Eq "^KM INPUTS (WRITTEN|CHANGED) $S .* km_inputs\.sha256 $(sha "$LIST")( |\$)" <<< "$hs" || die "HEAD's STATUS.txt has no 'KM INPUTS WRITTEN|CHANGED $S ... km_inputs.sha256 $(sha "$LIST")' line: km's one list is committed with the line that records it ((b) item 4; (e) item 5)"
  nrec=${#REC[@]}
  note "part I's record committed and unchanged ($nrec files, and HEAD's STATUS.txt holds the part B and part I DONE lines and the one list's KM INPUTS line)"
fi
check_refs "part T start"
record_inputs
# ---- 1. The timing pair (section 4.1, re-based: km3 against kta3 at B): both arms always fresh, wall time gates, CPU
#         beside; the second pair decides if needed. A passed pair is not repeated.
local F=${S}_timing cur arch nfail x k rc=0
if grep -Eq "^KM TIMING DONE $S .* knobs $KNOBS\$" "$O/STATUS.txt"; then
  note "the timing pair passed before ($(grep -E "^KM TIMING DONE $S " "$O/STATUS.txt" | tail -n 1 | cut -c1-200)); not repeated"
else
  shopt -s nullglob; cur=(); for f in "$O/${F}_"*; do case ${f##*/} in "${F}_attempt"*) ;; *) cur+=("$f");; esac; done
  arch=("$O/${F}_attempt"*); shopt -u nullglob
  nfail=$(grep -c -E "^[0-9T:Z-]+ FAILED: part T: timing" "$O/STATUS.txt" || true)
  if [ ${#cur[@]} -gt 0 ] || [ "$nfail" -gt 0 ]; then
    [ -n "${KM_TIMING_RETRY:-}" ] || die "timing: a pair was started before (${#cur[@]} timing files, $nfail timing failures): both arms are rerun once and the second pair decides, so a restart does not get a new pair. To time again anyway, set KM_TIMING_RETRY='<written reason>' (noted; the earlier files are kept as ${F}_attempt<k>_*)"
    k=1; while :; do shopt -s nullglob; x=("$O/${F}_attempt${k}_"*); shopt -u nullglob; [ ${#x[@]} -gt 0 ] || break; k=$((k + 1)); done
    for f in "${cur[@]}"; do mv -- "$f" "$O/${F}_attempt${k}_${f##*/${F}_}"; done
    note "KM TIMING RETRY $S: KM_TIMING_RETRY='${KM_TIMING_RETRY//$'\n'/ }'; the earlier ${#cur[@]} timing files moved to ${F}_attempt${k}_*"
  fi
  TIMEFORMAT='TIMING %R %U %S'
  timing_arms() {  # pair
    local arm code lab busy
    for arm in "$BC:$BC" "$CAND:$CL"; do
      code=${arm%%:*}; lab=${arm#*:}
      rm -f "$O/${F}_${lab}_$TIMING_GAMES.jsonl" "$O/${F}_${lab}_$TIMING_GAMES.txt"
      verify_inputs "before timing arm $lab, pair $1"
      busy=$(others)
      if [ -n "$busy" ]; then
        [ -n "${KM_ALLOW_BUSY:-}" ] || die "timing: other game programs are running ($busy); the pair needs the laptop to itself"
        note "SMOKE: timing arm $lab with other game programs running ($busy)"
      fi
      NOVERIFY=1
      { time run ${F}_${lab}_$TIMING_GAMES 0,2 $TIMING_GAMES --decks ../decks/research --bot "$code"; } 2> "$O/${F}_${lab}_$1.time"
      NOVERIFY=0; verify_inputs "after timing arm $lab, pair $1"
    done
  }
  timing_ratio() {  # pair; exit 0 within, 1 over, 2 unreadable
    python3 - "$O/${F}_${BC}_$1.time" "$O/${F}_${CL}_$1.time" "$BC" "$CL" <<'EOF'
import re, sys
vals = []
for p in sys.argv[1:3]:
    text = open(p).read()
    recs = [re.fullmatch(r"TIMING (\d+\.\d+) (\d+\.\d+) (\d+\.\d+)", ln.strip()) for ln in text.splitlines() if ln.startswith("TIMING")]
    if len(recs) != 1 or recs[0] is None:
        print(f"unreadable timing record {p}: {text!r}")
        sys.exit(2)
    vals.append(tuple(map(float, recs[0].groups())))
(wa, ua, sa), (wb, ub, sb) = vals
r, c, base, lab = wb / wa, (ub + sb) / max(ua + sa, 1e-9), sys.argv[3], sys.argv[4]
print(f"{base} {wa:.1f} s wall, {ua + sa:.1f} s CPU; {lab} {wb:.1f} s wall, {ub + sb:.1f} s CPU; "
      f"{lab}/{base} wall {r:.3f} (limit 1.25: {'within' if r <= 1.25 else 'OVER'}), CPU {c:.3f}")
sys.exit(0 if r <= 1.25 else 1)
EOF
  }
  PHASE="part T: timing"
  timing_arms 1
  timing_ratio 1 > "$O/${F}_1.txt" || rc=$?
  [ $rc -le 1 ] || die "$(cat "$O/${F}_1.txt")"
  if [ $rc -eq 0 ]; then note "timing: $(cat "$O/${F}_1.txt")"
  else
    note "timing, first pair: $(cat "$O/${F}_1.txt"); rerunning both arms once"
    timing_arms 2
    rc=0; timing_ratio 2 > "$O/${F}_2.txt" || rc=$?
    [ $rc -le 1 ] || die "$(cat "$O/${F}_2.txt")"
    [ $rc -eq 0 ] || die "$CL over 1.25 x $BC's wall time on both pairs ($(cat "$O/${F}_2.txt")); no km game"
    note "timing, second pair (decides): $(cat "$O/${F}_2.txt")"
  fi
  PHASE="part T"
  check_pins "after the timing pair"
  echo "KM TIMING DONE $S $(date -u +%FT%TZ) knobs $KNOBS" >> "$O/STATUS.txt"
fi
# ---- 2. km_thresholds.py committed, with its sha256 and the Python version, before the sample's first game (step 5).
if [ $CHECK_COMMITS -eq 1 ]; then
  committed "$kt" || die "km_thresholds.py is not committed, or differs from HEAD (section 4.0 step 5: committed, with its sha256 and the Python version, before the sample's first game; (g) step 4)"
fi
note "km_thresholds.py sha256 $(sha "$kt"), $(python3 --version 2>&1), $([ $CHECK_COMMITS -eq 1 ] && echo "committed at $(git -C "$R" log -1 --format=%h -- "${kt#"$R"/}")" || echo "SMOKE: commits not checked")"
# ---- 3. The sample: the counter tool, deals 200-299 of the 14 gating cells, kta3 then km3.
local GATE14="table:0,table:1,table:2,table:3,table:4,table:8,table:13,table:18,table:19,table:20,table:21,new_decks.tsv:8,new_decks.tsv:9,new_decks.tsv:16"
local last=$((200 + SAMPLE_GAMES - 1))
n0=${S}_sample_${BC}_rows; n1=${S}_sample_${CL}_rows
rows_run $n0 "$GATE14" 200 $SAMPLE_GAMES "$BC" yes quiet
rows_v_games "the sample's $BC arm, deals 200-$last of the 14 gating cells, v ${REFS[table]##*/} / ${REFS[new17]##*/}" "$O/$n0.jsonl" 200 $last "$(ref table)" "$(ref new17)"
rows_run $n1 "$GATE14" 200 $SAMPLE_GAMES "$CAND" yes quiet
note "the sample's $CL arm: its deals, seeds, seats, decks and bots are the sample's (rows-complete); its moves are checked against $CL's own games in part R"
python3 "$kt" sample --kta3 "$O/$n0.jsonl" --km3 "$O/$n1.jsonl" --base-code "$BC" --cand-code "$CAND" --json "$tj.new" --txt "$tt.new" \
  --tool-source-sha "$TOOL_SRC_SHA" --tool-program-sha "$(sha "$CENSUS")" > /dev/null || die "km_thresholds.py sample failed"
if [ -e "$tj" ] || [ -e "$tt" ]; then
  cmp -s "$tj.new" "$tj" && cmp -s "$tt.new" "$tt" || die "thresholds.json/.txt differ from a recomputation from the same files"
  rm -f "$tj.new" "$tt.new"
else mv "$tj.new" "$tj"; mv "$tt.new" "$tt"; fi
note "thresholds written: thresholds.txt and thresholds.json (sha256 $(sha "$tj")); $(grep '^  RESULT' "$tt" | sed 's/^  //' | tr '\n' ' ')"
check_pins "after part T"
FINISHED=1
echo "KM PART T DONE $S $(date -u +%FT%TZ) thresholds.json $(sha "$tj") knobs $KNOBS" >> "$O/STATUS.txt"
note "STOP after part T: the independent check (another agent, its own code, from the committed raw files) and the dated amendment are next, each committed on its own; part R needs GO_km_tables (Dustin's separate go-ahead for the tables) with 'amendment <commit>' and 'check <path>' lines"
}

# =====================================================================================================================
part_R() {
PHASE="part R"
LIST_REQUIRED=1   # km's one list, from part I: checked with the pins before the first game and after the last
local tj="$O/thresholds.json" prev amend chk cf out f
prev=$(sed -n "s#^KM PART T DONE $S [^ ]* thresholds.json \([0-9a-f]*\) knobs $KNOBS\$#\1#p" "$O/STATUS.txt" | tail -n 1)
[ -n "$prev" ] || die "part T has not passed here with knobs $KNOBS"
[ "$(sha "$tj")" = "$prev" ] || die "thresholds.json is not the file part T wrote (sha256 $prev)"
if grep -Eq "^KM PART R DONE $S .* knobs $KNOBS\$" "$O/STATUS.txt"; then
  check_pins "part R, done before"; note "part R finished before with these knobs; nothing to do"; FINISHED=1; return 0
fi
gate GO_km_tables "Dustin's separate go-ahead for the tables (Amendment 1 (g) step 5; block item 9), the independent check's committed output and the committed amendment with M1's and M2's numbers (section 4.0 steps 7-9)"
if [ $CHECK_COMMITS -eq 1 ]; then
  # Section 4.0 steps 5-6 (the sample's raw files, km_thresholds.py and its output, with the timing pair's files) and
  # "Reading code" (read_km.py "committed before any km result is read", with the config it reads; the footprint, this
  # part's first output, is one), committed and unchanged.
  local -a TIMEF; shopt -s nullglob; TIMEF=("$O/${S}_timing_"*); shopt -u nullglob
  for f in "$LIST" "$HERE/km_thresholds.py" "$tj" "$O/thresholds.txt" "$O/${S}_sample_${BC}_rows.jsonl" "$O/${S}_sample_${CL}_rows.jsonl" \
           "${TIMEF[@]}" "$HERE/footprint_km.py" "$HERE/read_km.py" "$HERE/test_read_km.sh" "$HERE/km_config.py" "$CFGF"; do
    committed "$f" || die "${f#"$R"/} is not committed, or differs from HEAD (section 4.0 steps 5-6 and 'Reading code': committed before any registered km game)"
  done
  amend=$(sed -n 's/^amendment \([0-9a-f]\{7,40\}\)\([^0-9a-f].*\)\{0,1\}$/\1/p' "$O/GO_km_tables" | head -n 1)
  [ -n "$amend" ] || die "GO_km_tables names no 'amendment <commit>' line (section 4.0 step 8: the dated amendment is committed before any registered km game)"
  # Step 7: "The independent check agrees, and its output is committed." GO_km_tables names that output.
  chk=$(sed -n 's/^check \(.*[^ ]\) *$/\1/p' "$O/GO_km_tables" | head -n 1)
  [ -n "$chk" ] || die "GO_km_tables names no 'check <path>' line (section 4.0 step 7: the independent check agrees, and its output is committed; the path from the repo root)"
  case $chk in /*) cf=$chk;; *) cf="$R/$chk";; esac
  [ -s "$cf" ] || die "the independent check's output $chk (GO_km_tables) is missing or empty"
  committed "$cf" || die "the independent check's output ${cf#"$R"/} is not committed, or differs from HEAD (section 4.0 step 7)"
  # Steps 6, 7, 8 in that order, each its own commit: thresholds.json, then the check's output, then the amendment; the
  # sample's raw rows files with thresholds.json or before it (step 7 computes the check "from those committed raw files").
  out=$(python3 "$HERE/km_check.py" commit-order --root "$R" --amendment "$amend" --registration "$REG" \
          --paths "${tj#"$R"/}" "${cf#"$R"/}" \
          --with-or-before "${O#"$R"/}/${S}_sample_${BC}_rows.jsonl" "${O#"$R"/}/${S}_sample_${CL}_rows.jsonl") || die "$out"
  note "amendment $amend; the independent check's output ${cf#"$R"/}; $out"
fi
check_pins "part R start"
check_refs "part R start"
# Clause (d)'s block (D2): written into pairs.new; a later start must write the same file.
local PN="$O/pairs.new" PF="$O/pairs"
rm -rf "$PN"; mkdir -p "$PN"
python3 "$HERE/km_check.py" d-pairs --out "$PN/d_lucario_block.tsv" --base 22900000000 --deals "$D_BLOCK" > "$PN/pairs_check.txt" \
  || die "km_check.py d-pairs"
sed -i "s#$PN/#$PF/#g" "$PN/pairs_check.txt"
if [ -d "$PF" ]; then
  diff -rq "$PN" "$PF" > /dev/null || die "the pairs file written now differs from $PF's (an earlier start)"
  rm -rf "$PN"
else mv "$PN" "$PF"; fi
note "clause (d)'s block: $(cat "$PF/pairs_check.txt")"
record_inputs
local ALL28 N17 SC8 B96 D9 CTX COV RT RN RB RS pv rv sa sb v g
ALL28=${REFPAIRINGS[table]}; N17=${REFPAIRINGS[new17]}; SC8=${REFPAIRINGS[scizor]}; B96=${REFPAIRINGS[b2e]}; D9=$(seq -s, 0 8)
local -a TAB NEW DB BB FV
TAB=(--decks ../decks/research); NEW=(--pairs "$NEWD" --root "$R" --seed-base "${REFSEED[new17]}")

# ---- 3. km3 on both sides of the 45 cells (step 1's games; section 7 row 3), then the footprint, first.
run ${S}_${CL}_table "$ALL28" $GAMES "${TAB[@]}" --bot "$CAND"
run ${S}_${CL}_new17 "$N17" $GAMES "${NEW[@]}" --bot "$CAND"
if [ $SMOKE -eq 1 ]; then note "SMOKE: footprint_km.py not run (it asserts $CFG_CAND on both sides and reads all 500 deals)"
else
  TMPD=$(mktemp -d)
  cp "$O/${S}_${CL}_table.jsonl" "$TMPD/table_${CFG_CAND}.jsonl"; cp "$O/${S}_${CL}_new17.jsonl" "$TMPD/new17_${CFG_CAND}.jsonl"
  python3 "$HERE/footprint_km.py" "$TMPD" --config "$CFGF" > "$O/footprint.txt.new" || die "footprint_km.py (see footprint.txt.new)"
  rm -rf -- "$TMPD"; TMPD=""
  if [ -e "$O/footprint.txt" ]; then
    cmp -s "$O/footprint.txt.new" "$O/footprint.txt" || die "footprint.txt differs from a recomputation from the same files"
    rm -f "$O/footprint.txt.new"
  else
    mv "$O/footprint.txt.new" "$O/footprint.txt"
    note "footprint written (footprint.txt, $CL against $BC's references, from ${S}_${CL}_table.jsonl $(sha "$O/${S}_${CL}_table.jsonl" | cut -c1-16) and ${S}_${CL}_new17.jsonl $(sha "$O/${S}_${CL}_new17.jsonl" | cut -c1-16)): the parent reads it and commits it alone, before anything else is read (step 1)"
  fi
fi
if [ "$GAMES" -ge 300 ]; then
  rows_v_games "the sample's $CL arm, deals 200-299, v $CL's own games (the footprint run)" "$O/${S}_sample_${CL}_rows.jsonl" 200 299 \
    "$O/${S}_${CL}_table.jsonl" "$O/${S}_${CL}_new17.jsonl"
else note "SMOKE: the sample's $CL arm not checked against its own games (the smoke has i < $GAMES only)"; fi

# ---- 4. The counters (step 3; section 7 row 4): deals 0-199 of the 17 cells, kta3 then km3, each checked deal by deal.
rows_run ${S}_counters_${BC}_rows km17 0 $COUNTER_GAMES "$BC" yes
rows_v_games "the counters' $BC arm, deals 0-$((COUNTER_GAMES - 1)) of the 17 cells, v ${REFS[table]##*/} / ${REFS[new17]##*/}" \
  "$O/${S}_counters_${BC}_rows.jsonl" 0 $((COUNTER_GAMES - 1)) "$(ref table)" "$(ref new17)"
rows_run ${S}_counters_${CL}_rows km17 0 $COUNTER_GAMES "$CAND" yes
rows_v_games "the counters' $CL arm, deals 0-$((COUNTER_GAMES - 1)) of the 17 cells, v $CL's own games" \
  "$O/${S}_counters_${CL}_rows.jsonl" 0 $((COUNTER_GAMES - 1)) "$O/${S}_${CL}_table.jsonl" "$O/${S}_${CL}_new17.jsonl"

# ---- 5. Mixed rows on the 45 cells (section 7 row 5; step 4, (c) and the vetoes): both directions, km3 on one deck and
#         kta3 on the other, on the cells whose games differ from kta3's references.
check_pins "before the 45 cells' mixed rows"
CTX="The 45 cells' mixed rows (step 4: (c) on 'the pairings where km3's footprint is non-zero', the vetoes' mixed rows; section 7 row 5: 'the cells with a changed game'), $CL against $BC's references (Amendment 1 (b) item 2). This comparison uses the coverage condition, which gives that set or a larger one; a cell whose $CL games equal $BC's on every deal has mixed rows equal to $BC's."
RT=$(skip table "$(baseline "$(ref table)")" "$O/${S}_${CL}_table.jsonl" "$ALL28" $GAMES "$CTX") || die "coverage_skip.py, the 28 table cells"
RN=$(skip new17 "$(baseline "$(ref new17)")" "$O/${S}_${CL}_new17.jsonl" "$N17" $GAMES "$CTX") || die "coverage_skip.py, the 17 new cells"
note "45 cells' mixed rows: table pairings [${RT}], new pairings [${RN}], both directions, $GAMES deals; skipped: table [$(minus "$ALL28" "$RT")], new [$(minus "$N17" "$RN")]"
if [ -n "$RT" ]; then
  run ${S}_mixed_table_${CL}_first "$RT" $GAMES "${TAB[@]}" --bot-a "$CAND" --bot-b "$BC"
  run ${S}_mixed_table_${CL}_second "$RT" $GAMES "${TAB[@]}" --bot-a "$BC" --bot-b "$CAND"
fi
if [ -n "$RN" ]; then
  run ${S}_mixed_new17_${CL}_first "$RN" $GAMES "${NEW[@]}" --bot-a "$CAND" --bot-b "$BC"
  run ${S}_mixed_new17_${CL}_second "$RN" $GAMES "${NEW[@]}" --bot-a "$BC" --bot-b "$CAND"
fi

# ---- 6. Clause (d) (step 4 (d); D2): 9 rows x 2 arms; the table's deals 0-499 of the 9 Lucario cells, then the block.
check_pins "before clause (d)"
run ${S}_d_${BC}_table "2,8,13,18,19,20,21" $GAMES "${TAB[@]}" --bot "$BC"
run ${S}_d_${CL}_table_lucario_b "2,8,13" $GAMES "${TAB[@]}" --bot-a "$BC" --bot-b "$CAND"
run ${S}_d_${CL}_table_lucario_a "18,19,20,21" $GAMES "${TAB[@]}" --bot-a "$CAND" --bot-b "$BC"
run ${S}_d_${BC}_new "8,16" $GAMES "${NEW[@]}" --bot "$BC"
run ${S}_d_${CL}_new_lucario_b "8,16" $GAMES "${NEW[@]}" --bot-a "$BC" --bot-b "$CAND"
DB=(--pairs "$PF/d_lucario_block.tsv" --root "$R" --seed-base 22900000000)
run ${S}_d_${BC}_block "$D9" $D_BLOCK "${DB[@]}" --bot "$BC"
run ${S}_d_${CL}_block "$D9" $D_BLOCK "${DB[@]}" --bot-a "$CAND" --bot-b "$BC"

# ---- 7. B2e (step 5; section 7 row 7): km3 both sides, the shortcut against kta3's B2e reference, the held deck's
#         own-side mixed row (km3 on the held deck, kta3 on the panel list).
check_pins "before coverage"
COV="Coverage (step 5; block item 7): $CL's both-sides games against $BC's references (Amendment 1 (b) item 2); the own-side mixed rows run on every pairing listed RUN."
BB=(--pairs "$R/${REFPAIRS[b2e]}" --root "$R" --seed-base "${REFSEED[b2e]}")
run ${S}_b2e_${CL} "$B96" $GAMES "${BB[@]}" --bot "$CAND"
RB=$(skip b2e "$(baseline "$(ref b2e)")" "$O/${S}_b2e_${CL}.jsonl" "$B96" $GAMES "$COV Pairings 0-47 (held-out) count; 48-95 (Dustin's files) are reported.") \
  || die "coverage_skip.py, B2e"
note "B2e: own-side mixed rows (the held deck, side a) on [${RB}], skipped [$(minus "$B96" "$RB")] (${S}_skip_b2e.txt)"
[ -z "$RB" ] || run ${S}_mixed_b2e_${CL}_first "$RB" $GAMES "${BB[@]}" --bot-a "$CAND" --bot-b "$BC"

# ---- 8. Scizor (section 7 row 8): new_decks.tsv pairings 0-7, km3 on Scizor (side a) in the mixed row.
run ${S}_scizor_${CL} "$SC8" $GAMES "${NEW[@]}" --bot "$CAND"
RS=$(skip scizor "$(baseline "$(ref scizor)")" "$O/${S}_scizor_${CL}.jsonl" "$SC8" $GAMES "$COV") || die "coverage_skip.py, Scizor"
note "Scizor: own-side mixed rows on [${RS}], skipped [$(minus "$SC8" "$RS")] (${S}_skip_scizor.txt)"
[ -z "$RS" ] || run ${S}_mixed_scizor_${CL}_first "$RS" $GAMES "${NEW[@]}" --bot-a "$CAND" --bot-b "$BC"

# ---- 9. The four second lists (section 7 row 9), each on its own deals; km3 on the second list in the mixed row.
for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
  g=var_$v
  FV=(--pairs "$R/${REFPAIRS[$g]}" --root "$R" --seed-base "${REFSEED[$g]}")
  pv=${REFPAIRINGS[$g]}
  run ${S}_var_${v}_${CL} "$pv" $GAMES "${FV[@]}" --bot "$CAND"
  rv=$(skip $g "$(baseline "$(ref "$g")")" "$O/${S}_var_${v}_${CL}.jsonl" "$pv" $GAMES "$COV") || die "coverage_skip.py, $v"
  sa=$(python3 "$HERE/km_check.py" pairings-of "$R/${REFPAIRS[$g]}" --side a --only "$rv")
  sb=$(python3 "$HERE/km_check.py" pairings-of "$R/${REFPAIRS[$g]}" --side b --only "$rv")
  note "$v: own-side mixed rows on side a [${sa}], side b [${sb}], skipped [$(minus "$pv" "$rv")] (${S}_skip_$g.txt)"
  [ -z "$sa" ] || run ${S}_var_${v}_${CL}_mixed_a "$sa" $GAMES "${FV[@]}" --bot-a "$CAND" --bot-b "$BC"
  [ -z "$sb" ] || run ${S}_var_${v}_${CL}_mixed_b "$sb" $GAMES "${FV[@]}" --bot-a "$BC" --bot-b "$CAND"
done

check_pins "after the last game"
[ ! -e "$O/${S}_rule_findings.txt" ] || note "RULE findings were recorded (${S}_rule_findings.txt): the reading stops until they are explained"
FINISHED=1
echo "KM PART R DONE $S $(date -u +%FT%TZ) knobs $KNOBS" >> "$O/STATUS.txt"
}

case $PART in B) part_B;; I) part_I;; T) part_T;; R) part_R;; esac
}  # main
main "$@"; exit $?
