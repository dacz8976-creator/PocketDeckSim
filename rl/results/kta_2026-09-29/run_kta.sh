#!/usr/bin/env bash
# kta's runner: every game of REGISTRATION.md here (registered at 363b6b7 with Dustin's word; its top block
# "Registration (Sept 29, Dustin's word)" governs), in section 8's order. Built from ../kt_tables_2026-09-28/run_kt.sh.
# Every game is played by the ec7e1a8 build's own programs (section 4), their sha256 checked against the pins before the
# first game, at each step and after the last; any other hash stops the run. Output names start ec7e1a8_fresh_.
#
#   0. the --pairs files (make_pairs.py; 3.2 and its "Tool limit"): development copies (identity only) and fresh ones,
#      each group inside its fresh sub-block; written once into <out>/pairs/, and a later start must write them identically.
#   A. section 4's checks, before any registered game (a failure stops the run; nothing later runs):
#      1. identity (check 2): this runner and its pairs files at the DEVELOPMENT bases, i < 20 of every group, kog3 and
#         kta3, equal kt's files game for game (7,440 games); the A/B tool (check 3): deck 07's first matchup, 240 games
#         per arm, at 22,600,000,000, equals kt's ec7e1a8_ab_d07_* rows (480 games); every scan page free of RULE
#         findings (check 5); all recorded in identity_check.txt (kt's name). 2. timing (check 4): kta3's 40-deal run on
#         the 28 table pairings within 1.25 x kog3's wall time, both arms always fresh, user+sys CPU beside; if over, both
#         arms rerun once and the second pair decides (ec7e1a8_fresh_timing_1.txt, _2.txt; the arms' records *_1.time,
#         *_2.time). Then the anchored line "KTA PART A DONE ec7e1a8 <time> knobs <knobs>"; a later start skips part A
#         only when that line's knobs are its own, and run_kta_ab.sh plays no A/B game without such a line.
#      A restart does not get a new timing pair: when part A has been started before (a "FAILED: part A:" note in
#      STATUS.txt, or any ec7e1a8_fresh_timing_* file), part A runs again only with KTA_PARTA_RETRY='<written reason>',
#      which is noted in STATUS.txt; the earlier timing files are then kept as ec7e1a8_fresh_timing_attempt<k>_*.
#   B. the registered games, on the fresh deals (3.2), in section 8's order:
#      3. kog3 and kta3 both sides on the 45 cells (22,500 each; the 28 from a --pairs file at 23,000,000,000, the 17 new
#         from new_decks.tsv at 23,001,000,000); then footprint.txt (5.1), which the parent reads and commits alone. The
#         runner does not stop for it (as kt's didn't).
#      4. mixed rows on the 45 cells (5.2 (c)): both directions, 500 deals, on every cell whose games differ (the cells
#         coverage_skip.py does not skip), and an i < 40 sample of both directions on the others; on the ordinary route
#         (footprint 15% or more, 5.3), both directions on all 45.
#      5. clause (d) (top block item 1; 5.2 (d)): the census Rayquaza list v the 8 panel lists, 2,000 deals per row,
#         seeds 23,003,000,000 + row x 10,000 + i; arm kog3 (kog3 both sides) and arm kta3 (kta3 on Rayquaza, kog3 on
#         the panel): 32,000 games.
#      6. the Dustin-deck A/B (5.6), by run_kta_ab.sh (a copy of run_kt_ab.sh): 5 decks x 1,920 x 2 arms at
#         23,004,000,000. Its rows carry the Jasmine counts (offered and played turns) the threshold and guard read (5.5).
#      7. the Rayquaza traces (5.5): the census list in seat 0 v Lucario (23,005,000,000) and v Vespiquen
#         (23,005,001,000), 200 games per arm, kta3 then kog3 on Rayquaza, kog3 on the other side: trace_pilot.py as
#         kt ran it, and kta_trace_moves.py on the same seeds for the per-game moves (the first-divergence tally).
#      8. the census counters (4.6): only with a tool_census that takes --seed-base (KTA_CENSUS, its own sha256 in
#         KTA_CENSUS_SHA); otherwise noted, and Stiffen's counter stays on the development deals, development-only.
#      9-12. coverage (5.5; top block item 3): Scizor, the four second lists, B2e: kog3 and kta3 both sides, then
#         coverage_skip.py per pairing by Dustin's condition (skip only when every corresponding deal is equal on the
#         complete move fingerprint, both decks, the seed and the seats; winners alone are not enough), whose report
#         names every skipped pairing and why, then the own-side mixed rows of every pairing not skipped. Each group's
#         report is ec7e1a8_fresh_skip_<group>.txt (and .json); coverage_skip.txt holds them all (the file read_kta.py
#         reads), the 45 cells' two groups included. A mixed-row file holds only the pairings its group's report runs.
#   STATUS.txt gets a note per step and, last, an anchored "KTA DONE ec7e1a8 <time>" or "KTA FAILED <time> ec7e1a8: <why>";
#   the last line matching ^KTA (DONE|FAILED) is the run's state. Resumable: an output is written to .part and moved
#   only when complete; a finished output is reused only when it is exactly the expected set of deals and every game
#   is the one that step plays (seed, seats, bots, decks: kta_check.py complete), otherwise the run stops ("move it away
#   first"). One run at a time (flock on <out>/.run_kta.lock). 12 threads, nice 10.
#   Inputs: at the first start, before any game, the sha256 of every file the games read beside the three pinned
#   programs (kta_check.py inputs: the deck files the pairs files name, decks/research, decks/screen/opponents, the
#   build's decks/research, the A/B's decks/dustin files, floor.py, trace_pilot.py, the gate file, the pairs files and
#   these scripts) goes to <out>/ec7e1a8_fresh_inputs.sha256 (committed with the tables); every step checks the hashes
#   (sha256sum -c) and the list, and any change stops the run. The whole runner is one function, main, called on the
#   last line, so bash has read the file to its end before the first command runs.
#
# Usage (WSL): nohup setsid bash "rl/results/kta_2026-09-29/run_kta.sh" > <log> 2>&1 &
#   Output folder: KTA_OUT, else the one rl/results/kta_tables_* folder, else rl/results/kta_tables_<UTC date> (section 9).
#   KTA_OUT is made absolute and compared with rl/results by the folder itself (realpath -m, then -ef on each existing
#   ancestor), so a relative path, '..', a link or another spelling of /mnt/c/Users is still inside rl/results.
# Knobs (environment; the defaults are the registered run, and any other value needs KTA_OUT outside rl/results):
#   THREADS 12, NICE 10, CAND kta3 (kog3 only for a smoke), CAND_LABEL = CAND (the candidate's file label: kta3 when
#   CAND=kta3; a smoke with CAND=kog3 uses a label other than kog3 and kta3, e.g. kogx), GAMES 500, D_GAMES 2000,
#   ID_GAMES 20, TIMING_GAMES 40, SAMPLE_GAMES 40, AB_GAMES 240, TRACE_GAMES 200, DECKS "07 05 11 01 03",
#   CENSUS_DEALS 100; KTA_BUILD (the build's folder); KTA_CENSUS / KTA_CENSUS_SHA (step 8); KTA_PARTA_RETRY (above).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole runner (called on the last line; the body is left unindented)
S=ec7e1a8; COMMIT=ec7e1a867bdaae2b0b4a3d2730e36dfffb611900; F=${S}_fresh
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
[ ! "$HERE" -ef "$R/rl/results/kta_2026-09-29" ] || HERE="$R/rl/results/kta_2026-09-29"   # one spelling (the inputs list)
KT="$R/rl/results/kt_tables_2026-09-28"
T="$R/rl/results/gauntlet_runs_2026-09-26/tsv"
B2E="$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"
RAYQ="rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt"
GATE="$KT/GATE_koh_b2e_read"
B=${KTA_BUILD:-/home/dacz8976/engine-kt-$S}
GYM="$B/engine/target/release/deckgym"; SCAN="$B/engine/target/release/examples/legality_scan"
CENSUS="$B/engine/target/release/examples/tool_census"
PIN_GYM=407976366fa2104ee1f2663c94fe31b1c503466defe9d6154b7e60659cb0991c      # section 4
PIN_SCAN=924751ba0926993eaee87ecc8fb8301ffd0b7eee8490bfb3369427794328f938
PIN_CENSUS=d9799c96015f74b952889a7f7d9820bbc12d5d97e4d267ad8acc2b63cdcc720b
THREADS=${THREADS:-12}; NICE=${NICE:-10}; CAND=${CAND:-kta3}; CAND_LABEL=${CAND_LABEL:-$CAND}; CL=$CAND_LABEL
GAMES=${GAMES:-500}; D_GAMES=${D_GAMES:-2000}; ID_GAMES=${ID_GAMES:-20}; TIMING_GAMES=${TIMING_GAMES:-40}
SAMPLE_GAMES=${SAMPLE_GAMES:-40}; AB_GAMES=${AB_GAMES:-240}; TRACE_GAMES=${TRACE_GAMES:-200}
DECKS=${DECKS:-"07 05 11 01 03"}; CENSUS_DEALS=${CENSUS_DEALS:-100}
KNOBS="$THREADS/$NICE/$CAND/$CL/$GAMES/$D_GAMES/$ID_GAMES/$TIMING_GAMES/$SAMPLE_GAMES/$AB_GAMES/$TRACE_GAMES/$DECKS/$CENSUS_DEALS"
REGISTERED="12/10/kta3/kta3/500/2000/20/40/40/240/200/07 05 11 01 03/100"
canon_out() {  # a folder as given: absolute, '..' and links resolved (realpath -m); spelled from $R when it lies in
               # $R/rl/results, found by comparing each existing ancestor with that folder itself (-ef: device and inode,
               # so another case of /mnt/c/Users, a relative path or a link cannot pass as outside it)
  local p d rest=""
  p=$(realpath -m -- "$1") || return 1
  d=$p
  while [ "$d" != / ]; do
    if [ -d "$d" ] && [ "$d" -ef "$R/rl/results" ]; then echo "$R/rl/results$rest"; return 0; fi
    rest="/${d##*/}$rest"; d=$(dirname -- "$d")
  done
  echo "$p"
}
if [ -n "${KTA_OUT:-}" ]; then O=$(canon_out "$KTA_OUT") || { echo "run_kta: cannot resolve KTA_OUT $KTA_OUT" >&2; exit 1; }
else
  shopt -s nullglob; ex=("$R"/rl/results/kta_tables_*/); shopt -u nullglob
  case ${#ex[@]} in
    0) O="$R/rl/results/kta_tables_$(date -u +%F)";;
    1) O=${ex[0]%/};;
    *) echo "run_kta: ${#ex[@]} kta_tables_* folders; set KTA_OUT" >&2; exit 1;;
  esac
fi
case "$O/" in "$R"/rl/results/*)
  [ "$KNOBS" = "$REGISTERED" ] || { echo "run_kta: knobs $KNOBS are not the registered run; a smoke needs KTA_OUT outside rl/results" >&2; exit 1; };;
esac
case $CAND in
  kta3) [ "$CL" = kta3 ] || { echo "run_kta: CAND=kta3 needs CAND_LABEL=kta3 (the registered files' label)" >&2; exit 1; };;
  kog3) case $CL in kog3|kta3) echo "run_kta: a kog3 smoke needs a label other than kog3 and kta3 (e.g. CAND_LABEL=kogx), so its games never sit in files named for either code" >&2; exit 1;; esac;;
  *) echo "run_kta: CAND must be kta3 (registered) or kog3 (a smoke)" >&2; exit 1;;
esac
[[ $CL =~ ^[a-z0-9]+$ ]] || { echo "run_kta: CAND_LABEL must be lower-case letters and digits" >&2; exit 1; }
for x in "$THREADS" "$NICE" "$GAMES" "$D_GAMES" "$ID_GAMES" "$TIMING_GAMES" "$SAMPLE_GAMES" "$AB_GAMES" "$TRACE_GAMES" "$CENSUS_DEALS"; do
  [[ $x =~ ^[0-9]+$ ]] || { echo "run_kta: knob value $x is not a number" >&2; exit 1; }
done
mkdir -p "$O"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
exec 9> "$O/.run_kta.lock"; flock -n 9 || { note "run_kta: another kta run holds the lock; this one exits"; exit 2; }
export KTA_OUT="$O" KTA_LOCK_HELD=1 KTA_BUILD="$B" THREADS NICE DECKS CAND CAND_LABEL AB_GAMES
FINISHED=0
PHASE=setup   # then "part A", then "part B": named in every FAILED line
die() { note "FAILED: $PHASE: $*"; echo "KTA FAILED $(date -u +%FT%TZ) $S: $PHASE: $*" >> "$O/STATUS.txt"; FINISHED=1; exit 1; }
on_exit() {
  local rc=$?
  [ "$FINISHED" -eq 1 ] || echo "KTA FAILED $(date -u +%FT%TZ) $S: stopped with exit code $rc outside a check ($PHASE; see the log)" >> "$O/STATUS.txt"
}
trap on_exit EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
note "KTA START $S: out $O; knobs $KNOBS ($([ "$KNOBS" = "$REGISTERED" ] && echo "the registered run" || echo "NOT the registered run: a smoke")); load $(cut -d' ' -f1-3 /proc/loadavg); other game programs running: $(ps -C legality_scan,deckgym,tool_census -o pid=,comm= | tr -s ' \n' ' ' || true)"

PF="$O/pairs"; INPUTS="$O/${F}_inputs.sha256"; INPUTS_READY=0; NOVERIFY=0
input_list() { python3 "$HERE/kta_check.py" inputs --root "$R" --pairs-dir "$PF" --build "$B" --decks "$DECKS" --here "$HERE" --gate "$GATE"; }
verify_inputs() {  # when: every input file unchanged since the first start (sha256sum -c), and the same list of them
  local out
  [ -s "$INPUTS" ] || die "the inputs record ${F}_inputs.sha256 is missing ($1)"
  out=$(cd "$R" && sha256sum -c --quiet --strict -- "$INPUTS" 2>&1) \
    || die "an input file changed since the first start ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')(${F}_inputs.sha256: every game of the run is played from the same files; restore it, or start a new run in a new folder)"
  out=$(diff <(cut -c67- "$INPUTS") <(input_list) 2>&1) \
    || die "the list of input files changed since the first start ($1): $(echo "$out" | grep '^[<>]' | head -n 3 | tr '\n' ' ')(${F}_inputs.sha256)"
}
write_inputs() {  # at the first start, before any game
  local lst IN
  lst=$(input_list) || die "kta_check.py inputs failed"
  mapfile -t IN <<< "$lst"
  (cd "$R" && sha256sum -- "${IN[@]}") > "$INPUTS.part" || die "sha256 of the input files (is a listed file missing?)"
  mv "$INPUTS.part" "$INPUTS"
  note "inputs recorded (first start, before any game): ${#IN[@]} files, ${F}_inputs.sha256 (sha256 $(sha256sum "$INPUTS" | cut -c1-16)); every step checks them and any change stops the run"
}
check_pins() {  # when: the three programs of section 4, and the build's commit; then the inputs (once recorded)
  [ "$(cat "$B/COMMIT" 2>/dev/null)" = "$COMMIT" ] || die "$B/COMMIT is not $COMMIT"
  local p pin h
  for p in "$GYM" "$SCAN" "$CENSUS"; do
    case $p in "$GYM") pin=$PIN_GYM;; "$SCAN") pin=$PIN_SCAN;; *) pin=$PIN_CENSUS;; esac
    [ -x "$p" ] || die "no program $p (section 4, check 7: a rebuild with git archive and its 45,000-game re-proof is a separate, deliberate step; this runner does not do it)"
    h=$(sha256sum "$p" | cut -d' ' -f1)
    [ "$h" = "$pin" ] || die "$p sha256 $h is not the pin $pin (section 4: a runner that finds any other hash stops)"
  done
  [ "$INPUTS_READY" -eq 0 ] || verify_inputs "$1"
  note "programs checked ($1): deckgym $PIN_GYM, legality_scan $PIN_SCAN, tool_census $PIN_CENSUS (commit $COMMIT)$([ "$INPUTS_READY" -eq 0 ] || echo "; the $(wc -l < "$INPUTS") input files unchanged")"
}
rules() {  # page name: section 4, check 5 (a RULE finding stops the run in part A, and holds the reading after it)
  local out
  if out=$(python3 "$HERE/kta_check.py" rules "$O/$1.txt"); then return 0; fi
  [ "$PHASE" = "part B" ] || die "section 4, check 5: $out"
  note "RULE FINDING (section 4, check 5: the reading stops until it is explained): $out"
  echo "$out" >> "$O/${F}_rule_findings.txt"
}
run() {  # name pairings games args...: legality_scan from the build's engine/ folder, THREADS threads, nice NICE
  local name=$1 pl=$2 n=$3 s x out prev="" sb=72000000 pf="" bot="" ba="" bb=""; local -a chk; shift 3
  [ -n "$pl" ] || die "run $name: no pairings"
  for x in "$@"; do  # what every game of the output must be (kta_check.py complete): seed base, bots, decks
    case $prev in --pairs) pf=$x;; --seed-base) sb=$x;; --bot) bot=$x;; --bot-a) ba=$x;; --bot-b) bb=$x;; esac
    prev=$x
  done
  ba=${ba:-$bot}; bb=${bb:-$bot}
  [ -n "$ba" ] && [ -n "$bb" ] || die "run $name: no bots named"
  chk=(--pairings "$pl" --games "$n" --seed-base "$sb" --bot-a "$ba" --bot-b "$bb")
  if [ -n "$pf" ]; then chk+=(--pairs "$pf"); else chk+=(--decks); fi
  [ "$NOVERIFY" -eq 1 ] || verify_inputs "before $name"
  if [ -e "$O/$name.jsonl" ]; then  # reused only when it is exactly the expected set of deals, each the expected game
    out=$(python3 "$HERE/kta_check.py" complete "$O/$name.jsonl" "${chk[@]}") \
      || die "$name.jsonl is there but is not the expected complete output ($out): move it away first"
    [ -e "$O/$name.txt" ] || die "$name.jsonl is there without its page $name.txt: move it away first"
    rules "$name"; return 0
  fi
  s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$SCAN" "$@" --pairings "$pl" --games "$n" \
      --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt" 2>&1 || die "$name (see $name.txt)"
  [ "$NOVERIFY" -eq 1 ] || verify_inputs "after $name"
  out=$(python3 "$HERE/kta_check.py" complete "$O/$name.jsonl.part" "${chk[@]}") \
    || die "$name: the scan's output is not the expected complete set of deals ($out)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
  rules "$name"
}
same() {  # label mine ref max_i expect: section 4, check 2
  [ -s "$3" ] || die "identity reference $3 is missing"
  python3 "$HERE/kta_check.py" same "$2" "$3" --max-i "$4" --expect "$5" --label "$1" >> "$O/identity_check.txt" \
    || die "IDENTITY FAILED: $1 (see identity_check.txt)"
}
minus() { python3 -c 'import sys; r = set(x for x in sys.argv[2].split(",") if x); print(",".join(x for x in sys.argv[1].split(",") if x and x not in r))' "$1" "$2"; }
skip() {  # group base cand pairings deals context: coverage_skip.py; prints the pairings whose mixed rows run
  python3 "$HERE/coverage_skip.py" --group "$1" --base "$2" --cand "$3" --pairings "$4" --deals "$5" --context "$6" \
    --report "$O/${F}_skip_$1.txt" --json "$O/${F}_skip_$1.json" --base-code kog3 --cand-code "$CAND" || return $?
  # coverage_skip.txt: every group's report so far, in the runner's order (the one file read_kta.py reads; committed).
  local g
  { echo "coverage_skip.txt: the coverage shortcut's comparisons (coverage_skip.py; one report per group, in the runner's order)"
    for g in table new17 scizor var_v-lucario_2 var_v-suicune_2 var_v-weezing_2 var_l-charizardy b2e; do
      [ ! -e "$O/${F}_skip_$g.txt" ] || { echo; cat "$O/${F}_skip_$g.txt"; }
    done; } > "$O/coverage_skip.txt.part" && mv "$O/coverage_skip.txt.part" "$O/coverage_skip.txt"
}
var_base() { case $1 in *charizardy*) echo "$2";; *) echo "$3";; esac; }   # list dev_or_fresh_b2e dev_or_fresh_table

check_pins "before the first game"
ALL28=$(seq -s, 0 27); N17=$(seq -s, 8 24); SC8=$(seq -s, 0 7); B96=$(seq -s, 0 95); D8=$(seq -s, 0 7)
VARS="v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy"
ARMS=("kog3:kog3" "$CAND:$CL")   # code:label; kog3 first, then the candidate

# ---- 0. The --pairs files (3.2). Written into pairs.new, then kept as pairs/ (a later start must write the same files).
PN="$O/pairs.new"
rm -rf "$PN"; mkdir -p "$PN"
mp() { python3 "$HERE/make_pairs.py" "$@" >> "$PN/pairs_check.txt" || die "make_pairs.py $* (see pairs.new/pairs_check.txt)"; }
mp table28 --base 72000000 --deals 500 --out "$PN/dev_table28.tsv"
mp rebase --src "$T/new_decks.tsv" --base 21108000000 --deals 500 --out "$PN/dev_new_decks.tsv" --same-as-src
mp rebase --src "$B2E" --base 21106000000 --deals 500 --out "$PN/dev_b2e.tsv" --same-as-src
for v in $VARS; do
  mp rebase --src "$T/var_$v.tsv" --base "$(var_base $v 21106000000 72000000)" --deals 500 --out "$PN/dev_var_$v.tsv" --same-as-src
done
mp d --base 22700000000 --deals 500 --out "$PN/dev_d_rayquaza.tsv" --compare "$KT/d_rayquaza.tsv"
mp table28 --base 23000000000 --deals 500 --out "$PN/fresh_table28.tsv" --group table
mp rebase --src "$T/new_decks.tsv" --base 23001000000 --deals 500 --out "$PN/fresh_new_decks.tsv" --group new
mp rebase --src "$B2E" --base 23002000000 --deals 500 --out "$PN/fresh_b2e.tsv" --group b2e
for v in $VARS; do
  mp rebase --src "$T/var_$v.tsv" --base "$(var_base $v 23002000000 23000000000)" --deals 500 --out "$PN/fresh_var_$v.tsv" \
    --group "$(var_base $v b2e table)"
done
mp d --base 23003000000 --deals 2000 --out "$PN/fresh_d_rayquaza.tsv" --group d
sed -i "s#$PN/#$PF/#g" "$PN/pairs_check.txt"
if [ -d "$PF" ]; then
  diff -rq "$PN" "$PF" > /dev/null || die "the pairs files written now differ from $PF (written by an earlier start): $(diff -rq "$PN" "$PF" | head -3 | tr '\n' ' ')"
  rm -rf "$PN"
else
  mv "$PN" "$PF"
fi
note "pairs files: $(cd "$PF" && sha256sum -- *.tsv | awk '{printf "%s %s; ", $2, substr($1, 1, 16)}')"
# The inputs: recorded at the first start, before any game; checked from here on at every step.
if [ ! -e "$INPUTS" ]; then
  shopt -s nullglob; old=("$O"/*.jsonl "$O"/*.jsonl.part); shopt -u nullglob
  [ ${#old[@]} -eq 0 ] || die "game files are in $O (e.g. ${old[0]##*/}) but no inputs record ${F}_inputs.sha256: the files they were played from are unknown; move them away first"
  write_inputs
fi
INPUTS_READY=1
verify_inputs "before the first game"

# ---- A. Section 4's checks, before any registered game.
PHASE="part A"
if sed -n "s/^KTA PART A DONE $S [^ ]* knobs //p" "$O/STATUS.txt" | grep -xF -- "$KNOBS" > /dev/null; then   # not -q (pipefail)
  note "section 4's checks passed at an earlier start with these knobs ($(grep "^KTA PART A DONE $S " "$O/STATUS.txt" | grep -F " knobs $KNOBS" | tail -n 1)); not repeated"
else
  # A restart does not get a new timing pair (4.4: both arms are rerun once and the second pair decides). If part A was
  # started before (a "FAILED: part A:" note, or any timing file), it runs again only with KTA_PARTA_RETRY='<reason>',
  # and the earlier timing files are kept as ${F}_timing_attempt<k>_* (the reading can print every attempt).
  shopt -s nullglob; cur=(); for f in "$O/${F}_timing_"*; do case ${f##*/} in "${F}_timing_attempt"*) ;; *) cur+=("$f");; esac; done
  arch=("$O/${F}_timing_attempt"*); shopt -u nullglob
  nfail=$(grep -c -E "^[0-9T:Z-]+ FAILED: part A: " "$O/STATUS.txt" || true)
  if [ ${#cur[@]} -gt 0 ] || [ ${#arch[@]} -gt 0 ] || [ "$nfail" -gt 0 ]; then
    [ -n "${KTA_PARTA_RETRY:-}" ] || die "part A was started before ($nfail part A failure notes in STATUS.txt; ${#cur[@]} timing files of an earlier attempt, ${#arch[@]} archived): 4.4 reruns both timing arms once and the second pair decides, so a restart does not get a new pair. To rerun part A anyway, set KTA_PARTA_RETRY='<written reason>' (noted here; the earlier timing files are kept as ${F}_timing_attempt<k>_*)"
    k=1; while :; do shopt -s nullglob; x=("$O/${F}_timing_attempt${k}_"*); shopt -u nullglob; [ ${#x[@]} -gt 0 ] || break; k=$((k + 1)); done
    for f in "${cur[@]}"; do mv -- "$f" "$O/${F}_timing_attempt${k}_${f##*/${F}_timing_}"; done
    note "KTA PART A RETRY $S: KTA_PARTA_RETRY='${KTA_PARTA_RETRY//$'\n'/ }'; $nfail part A failure notes above; $([ ${#cur[@]} -eq 0 ] && echo "no unarchived timing files" || echo "the earlier attempt's ${#cur[@]} timing files moved to ${F}_timing_attempt${k}_*"); archived before: ${#arch[@]} files"
  elif [ -n "${KTA_PARTA_RETRY:-}" ]; then
    note "KTA_PARTA_RETRY is set, but part A has no earlier failure or timing file here; nothing to archive"
  fi
  : > "$O/identity_check.txt"   # kt's name (run_kt.sh), as read_kta.py reads it
  I=$ID_GAMES
  ref() {  # group code: kt's file for that code at this binary (section 4, check 2)
    case "$2:$1" in
      kog3:table) echo "$KT/${S}_id_kog3_500.jsonl";;        kta3:table) echo "$KT/${S}_kta3_table.jsonl";;
      kog3:new17) echo "$KT/${S}_id_kog3_new17.jsonl";;      kta3:new17) echo "$KT/${S}_kta3_new17.jsonl";;
      kog3:scizor) echo "$KT/${S}_id_kog3_scz40.jsonl";;     kta3:scizor) echo "$KT/${S}_scizor_kta3.jsonl";;
      kog3:b2e) echo "$KT/${S}_id_kog3_b2e40.jsonl";;        kta3:b2e) echo "$KT/${S}_b2e_kta3.jsonl";;
      kog3:var_*) echo "$KT/${S}_id_kog3_${1}40.jsonl";;     kta3:var_*) echo "$KT/${S}_${1}_kta3.jsonl";;
      kog3:d) echo "$KT/${S}_d_kog3.jsonl";;                 kta3:d) echo "$KT/${S}_d_kta3.jsonl";;
      *) echo "/nonexistent/no-reference-for-$2-$1";;
    esac
  }
  # 1. Identity: the runner and its pairs files at the development bases, i < ID_GAMES of every group, kog3 and the candidate.
  for arm in "${ARMS[@]}"; do
    code=${arm%%:*}; lab=${arm#*:}
    if [ "$lab" = kog3 ]; then both=(--bot kog3); darm=(--bot kog3); else both=(--bot "$code"); darm=(--bot-a "$code" --bot-b kog3); fi
    n=${F}_id_${lab}_table_i$I;  run $n "$ALL28" $I --pairs "$PF/dev_table28.tsv" --root "$R" --seed-base 72000000 "${both[@]}"
    same "$lab (as $code), 28 table cells, i < $I" "$O/$n.jsonl" "$(ref table $code)" $I $((28 * I))
    n=${F}_id_${lab}_new17_i$I;  run $n "$N17" $I --pairs "$PF/dev_new_decks.tsv" --root "$R" --seed-base 21108000000 "${both[@]}"
    same "$lab (as $code), 17 new cells, i < $I" "$O/$n.jsonl" "$(ref new17 $code)" $I $((17 * I))
    n=${F}_id_${lab}_scizor_i$I; run $n "$SC8" $I --pairs "$PF/dev_new_decks.tsv" --root "$R" --seed-base 21108000000 "${both[@]}"
    same "$lab (as $code), Scizor, i < $I" "$O/$n.jsonl" "$(ref scizor $code)" $I $((8 * I))
    n=${F}_id_${lab}_b2e_i$I;    run $n "$B96" $I --pairs "$PF/dev_b2e.tsv" --root "$R" --seed-base 21106000000 "${both[@]}"
    same "$lab (as $code), B2e, i < $I" "$O/$n.jsonl" "$(ref b2e $code)" $I $((96 * I))
    for v in $VARS; do
      pv=$(python3 "$HERE/make_pairs.py" list "$PF/dev_var_$v.tsv")
      n=${F}_id_${lab}_var_${v}_i$I
      run $n "$pv" $I --pairs "$PF/dev_var_$v.tsv" --root "$R" --seed-base "$(var_base $v 21106000000 72000000)" "${both[@]}"
      same "$lab (as $code), second list $v, i < $I" "$O/$n.jsonl" "$(ref var_$v $code)" $I $(( $(echo "$pv" | tr ',' '\n' | wc -l) * I ))
    done
    n=${F}_id_${lab}_d_i$I;      run $n "$D8" $I --pairs "$PF/dev_d_rayquaza.tsv" --root "$R" --seed-base 22700000000 "${darm[@]}"
    same "$lab (as $code), clause (d) arm, i < $I" "$O/$n.jsonl" "$(ref d $code)" $I $((8 * I))
  done
  # Check 3: the A/B tool, deck 07's first matchup (t-altaria), at the development block, against kt's rows.
  for arm in "${ARMS[@]}"; do
    code=${arm%%:*}; lab=${arm#*:}; n=${F}_id_ab_d07_$lab
    abc=(--games "$AB_GAMES" --block 22600000000 --opponents 1 --pilot "$code" --deck 07 --opp-dir "$R/decks/screen/opponents")
    verify_inputs "before $n"
    if [ -e "$O/$n.jsonl" ]; then
      out=$(python3 "$HERE/kta_check.py" ab-complete "$O/$n.jsonl" "${abc[@]}") \
        || die "$n.jsonl is there but is not complete ($out): move it away first"
    else
      ( RAYON_NUM_THREADS=$THREADS nice -n "$NICE" python3 "$HERE/kta_ab_play.py" --deck 07 --pilot "$code" --meta-pilot kog3 \
          --engine "$GYM" --expect-sha "$PIN_GYM" --games "$AB_GAMES" --block 22600000000 --max-opponents 1 --gate "$GATE" \
          --out "$O/$n.jsonl.part" ) > "$O/$n.txt" 2>&1 || die "$n (see $n.txt)"
      verify_inputs "after $n"
      out=$(python3 "$HERE/kta_check.py" ab-complete "$O/$n.jsonl.part" "${abc[@]}") || die "$n: not complete ($out)"
      mv "$O/$n.jsonl.part" "$O/$n.jsonl"; note "$n done ($(wc -l < "$O/$n.jsonl") games)"
    fi
    python3 "$HERE/kta_check.py" ab-same "$O/$n.jsonl" "$KT/${S}_ab_d07_$code.jsonl" --label "A/B tool, $lab (as $code), deck 07 v t-altaria, development block" \
      >> "$O/identity_check.txt" || die "IDENTITY FAILED: the A/B tool (see identity_check.txt)"
  done
  note "identity: $(tr '\n' ' ' < "$O/identity_check.txt")"
  # 2. Timing (check 4): both arms always run fresh (a cached arm would time at 0 s), wall time gates, CPU beside.
  TIMEFORMAT='TIMING %R %U %S'   # bash's time: wall, user and sys seconds of the arm, on a line of its own
  timing_arms() {  # pair number: one <arm>_<pair>.time record per arm (the inputs are checked outside the timed part)
    local arm code lab
    for arm in "${ARMS[@]}"; do
      code=${arm%%:*}; lab=${arm#*:}
      rm -f "$O/${F}_timing_${lab}_$TIMING_GAMES.jsonl"   # the first pair's arm, when the second pair reruns it
      verify_inputs "before timing arm $lab, pair $1"; NOVERIFY=1
      { time run ${F}_timing_${lab}_$TIMING_GAMES "$ALL28" $TIMING_GAMES --decks ../decks/research --bot "$code"; } 2> "$O/${F}_timing_${lab}_$1.time"
      NOVERIFY=0; verify_inputs "after timing arm $lab, pair $1"
    done
  }
  timing_ratio() {  # pair number; exit 0 within, 1 over, 2 unreadable (the run stops)
    python3 - "$O/${F}_timing_kog3_$1.time" "$O/${F}_timing_${CL}_$1.time" "$CL" <<'EOF'
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
r, c, lab = wb / wa, (ub + sb) / (ua + sa), sys.argv[3]
print(f"kog3 {wa:.0f} s wall, {ua + sa:.0f} s CPU; {lab} {wb:.0f} s wall, {ub + sb:.0f} s CPU; "
      f"{lab}/kog3 wall {r:.2f} (limit 1.25: {'within' if r <= 1.25 else 'OVER'}), CPU {c:.2f}")
sys.exit(0 if r <= 1.25 else 1)
EOF
  }
  timing_arms 1   # no earlier timing file is here: any was archived above, with KTA_PARTA_RETRY's reason
  rc=0; timing_ratio 1 > "$O/${F}_timing_1.txt" || rc=$?
  [ $rc -le 1 ] || die "timing (section 4, check 4): $(cat "$O/${F}_timing_1.txt")"
  if [ $rc -eq 0 ]; then note "timing: $(cat "$O/${F}_timing_1.txt")"
  else
    note "timing, first pair: $(cat "$O/${F}_timing_1.txt"); rerunning both arms once"
    timing_arms 2
    rc=0; timing_ratio 2 > "$O/${F}_timing_2.txt" || rc=$?
    [ $rc -le 1 ] || die "timing (section 4, check 4): $(cat "$O/${F}_timing_2.txt")"
    [ $rc -eq 0 ] || die "timing (section 4, check 4): $CL over 1.25 x kog3's wall time on both pairs ($(cat "$O/${F}_timing_2.txt")); no table game"
    note "timing, second pair (decides): $(cat "$O/${F}_timing_2.txt")"
  fi
  check_pins "after section 4's checks"
  echo "KTA PART A DONE $S $(date -u +%FT%TZ) knobs $KNOBS" >> "$O/STATUS.txt"
fi
PHASE="part B"

# ---- 3. The 45 cells, both sides, kog3 then the candidate; then the footprint (5.1), for the parent to commit alone.
FT=(--pairs "$PF/fresh_table28.tsv" --root "$R" --seed-base 23000000000)
FN=(--pairs "$PF/fresh_new_decks.tsv" --root "$R" --seed-base 23001000000)
run ${F}_kog3_table "$ALL28" $GAMES "${FT[@]}" --bot kog3
run ${F}_kog3_new17 "$N17" $GAMES "${FN[@]}" --bot kog3
run ${F}_${CL}_table "$ALL28" $GAMES "${FT[@]}" --bot "$CAND"
run ${F}_${CL}_new17 "$N17" $GAMES "${FN[@]}" --bot "$CAND"
python3 "$HERE/kta_check.py" footprint --base-table "$O/${F}_kog3_table.jsonl" --base-new17 "$O/${F}_kog3_new17.jsonl" \
  --cand-table "$O/${F}_${CL}_table.jsonl" --cand-new17 "$O/${F}_${CL}_new17.jsonl" --code "$CL" --expect $((45 * GAMES)) \
  > "$O/footprint.txt.new" || die "the footprint (see footprint.txt.new)"
if [ -e "$O/footprint.txt" ]; then
  cmp -s "$O/footprint.txt.new" "$O/footprint.txt" || die "footprint.txt differs from a recomputation from the same files"
  rm -f "$O/footprint.txt.new"
else
  mv "$O/footprint.txt.new" "$O/footprint.txt"
  note "footprint written (footprint.txt): the parent reads it and commits it alone before anything else is read (5.1)"
fi
ROUTE=$(sed -n 's/^ROUTE //p' "$O/footprint.txt")
case $ROUTE in reserve|ordinary) ;; *) die "footprint.txt names no route";; esac
if [ "$ROUTE" = ordinary ]; then  # 5.1: first the hashes, the pairs files and the integrity line are checked
  check_pins "footprint 15% or more (5.1)"
  note "footprint 15% or more: pairs files now $(cd "$PF" && sha256sum -- fresh_*.tsv | awk '{printf "%s %s; ", $2, substr($1, 1, 16)}'); the integrity line is the reading's; mixed rows on all 45 cells (5.3)"
fi

# ---- 4. Mixed rows on the 45 cells (5.2 (c); 5.3 on the ordinary route).
check_pins "before the 45 cells' mixed rows"
CTX="The 45 cells' mixed rows (5.2 (c)): run on the cells whose kta3 games differ from kog3's; this comparison uses the coverage condition, which gives that set or a larger one. The cells skipped here get the i < 40 sample of both directions."
RT=$(skip table "$O/${F}_kog3_table.jsonl" "$O/${F}_${CL}_table.jsonl" "$ALL28" $GAMES "$CTX") || die "coverage_skip.py, the 28 table cells"
RN=$(skip new17 "$O/${F}_kog3_new17.jsonl" "$O/${F}_${CL}_new17.jsonl" "$N17" $GAMES "$CTX") || die "coverage_skip.py, the 17 new cells"
if [ "$ROUTE" = ordinary ]; then RT=$ALL28; RN=$N17; ST=""; SN=""
else ST=$(minus "$ALL28" "$RT"); SN=$(minus "$N17" "$RN"); fi
note "45 cells' mixed rows ($ROUTE route): table pairings [${RT}], new pairings [${RN}] at $GAMES deals both directions; i < $SAMPLE_GAMES sample on table [${ST}], new [${SN}]"
if [ -n "$RT" ]; then
  run ${F}_mixed_table_${CL}_first "$RT" $GAMES "${FT[@]}" --bot-a "$CAND" --bot-b kog3
  run ${F}_mixed_table_${CL}_second "$RT" $GAMES "${FT[@]}" --bot-a kog3 --bot-b "$CAND"
fi
if [ -n "$RN" ]; then
  run ${F}_mixed_new17_${CL}_first "$RN" $GAMES "${FN[@]}" --bot-a "$CAND" --bot-b kog3
  run ${F}_mixed_new17_${CL}_second "$RN" $GAMES "${FN[@]}" --bot-a kog3 --bot-b "$CAND"
fi
if [ -n "$ST" ]; then
  run ${F}_mixed_table_${CL}_first_s$SAMPLE_GAMES "$ST" $SAMPLE_GAMES "${FT[@]}" --bot-a "$CAND" --bot-b kog3
  run ${F}_mixed_table_${CL}_second_s$SAMPLE_GAMES "$ST" $SAMPLE_GAMES "${FT[@]}" --bot-a kog3 --bot-b "$CAND"
fi
if [ -n "$SN" ]; then
  run ${F}_mixed_new17_${CL}_first_s$SAMPLE_GAMES "$SN" $SAMPLE_GAMES "${FN[@]}" --bot-a "$CAND" --bot-b kog3
  run ${F}_mixed_new17_${CL}_second_s$SAMPLE_GAMES "$SN" $SAMPLE_GAMES "${FN[@]}" --bot-a kog3 --bot-b "$CAND"
fi

# ---- 5. Clause (d): 8 rows x D_GAMES deals, arm kog3 (both sides) and arm candidate (Rayquaza side; kog3 on the panel).
check_pins "before clause (d)"
FD=(--pairs "$PF/fresh_d_rayquaza.tsv" --root "$R" --seed-base 23003000000)
run ${F}_d_kog3 "$D8" $D_GAMES "${FD[@]}" --bot kog3
run ${F}_d_${CL} "$D8" $D_GAMES "${FD[@]}" --bot-a "$CAND" --bot-b kog3

# ---- 6. The Dustin-deck A/B (5.6), with its Jasmine counts (5.5): run_kta_ab.sh under this run's lock.
check_pins "before the A/B"
bash "$HERE/run_kta_ab.sh" || die "the A/B (run_kta_ab.sh; its notes are above)"

# ---- 7. The Rayquaza traces (5.5): census list in seat 0, 200 games per arm, the same seeds in both arms.
check_pins "before the traces"
trace() {  # opponent seed code label
  local opp=$1 seed=$2 code=$3 lab=$4 name=${F}_trace_rayquaza_${1}_${4} s
  local pg="$O/${name}_pergame.jsonl" mf="$O/${name}_moves.jsonl"
  verify_inputs "before $name"
  if [ -e "$pg" ] || [ -e "$mf" ]; then
    python3 "$HERE/kta_check.py" trace-complete "$pg" "$mf" --games "$TRACE_GAMES" --seed "$seed" > /dev/null \
      || die "$name: trace files are there but not complete: move them away first"
    return 0
  fi
  s=$(date +%s)
  ( cd "$R" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py "$R/$RAYQ" \
      "$R/decks/screen/opponents/t-$opp.txt" --games "$TRACE_GAMES" --seed "$seed" --pilot "$code" --opp-pilot kog3 \
      --engine "$GYM" --per-game "$pg.part" ) > "$O/$name.txt.part" 2>&1 || die "trace $name (see $name.txt.part)"
  ( cd "$R" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" python3 "$HERE/kta_trace_moves.py" --deck "$R/$RAYQ" \
      --opp "$R/decks/screen/opponents/t-$opp.txt" --games "$TRACE_GAMES" --seed "$seed" --pilot "$code" --opp-pilot kog3 \
      --engine "$GYM" --expect-sha "$PIN_GYM" --out "$mf.part" ) > "$O/${name}_moves.txt" 2>&1 || die "trace moves $name (see ${name}_moves.txt)"
  verify_inputs "after $name"
  python3 "$HERE/kta_check.py" trace-complete "$pg.part" "$mf.part" --games "$TRACE_GAMES" --seed "$seed" > /dev/null \
    || die "$name: trace_pilot.py's and kta_trace_moves.py's games are not the same complete set"
  mv "$O/$name.txt.part" "$O/$name.txt"; mv "$pg.part" "$pg"; mv "$mf.part" "$mf"
  note "$name done in $(( $(date +%s) - s )) s ($TRACE_GAMES games, seeds $seed+)"
}
for os_ in lucario:23005000000 vespiquen:23005001000; do
  trace "${os_%%:*}" "${os_##*:}" "$CAND" "$CL"
  trace "${os_%%:*}" "${os_##*:}" kog3 kog3
done

# ---- 8. The census counters (4.6): fresh deals only with a --seed-base tool_census; otherwise development-only.
if [ -n "${KTA_CENSUS:-}" ]; then
  [ -n "${KTA_CENSUS_SHA:-}" ] || die "KTA_CENSUS needs KTA_CENSUS_SHA (the changed tool's own sha256, section 4, check 6)"
  [ "$(sha256sum "$KTA_CENSUS" | cut -d' ' -f1)" = "$KTA_CENSUS_SHA" ] || die "$KTA_CENSUS is not sha256 $KTA_CENSUS_SHA"
  note "census counters with $KTA_CENSUS (sha256 $KTA_CENSUS_SHA), --seed-base 23000000000, first $CENSUS_DEALS deals of the 28 table pairings"
  for arm in "${ARMS[@]}"; do
    code=${arm%%:*}; lab=${arm#*:}; n=${F}_census_$lab
    verify_inputs "before $n"
    if [ ! -e "$O/$n.jsonl" ]; then
      ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$KTA_CENSUS" --decks ../decks/research --games "$CENSUS_DEALS" \
          --bot "$code" --seed-base 23000000000 --games-out "$O/$n.jsonl.part" ) > "$O/$n.txt.part" 2> "$O/$n.log" || die "$n (see $n.log)"
      python3 "$HERE/kta_check.py" census-fp "$O/$n.jsonl.part" "$O/${F}_${lab}_table.jsonl" --deals "$CENSUS_DEALS" \
        >> "$O/${F}_census_fingerprints.txt" || die "$n: seeds or move fingerprints differ from the fresh table file's"
      mv "$O/$n.jsonl.part" "$O/$n.jsonl"; mv "$O/$n.txt.part" "$O/$n.txt"; note "$n done"
    else
      python3 "$HERE/kta_check.py" census-fp "$O/$n.jsonl" "$O/${F}_${lab}_table.jsonl" --deals "$CENSUS_DEALS" > /dev/null \
        || die "$n.jsonl is there but does not match the fresh table file: move it away first"
    fi
  done
else
  note "census counters (section 8 row 8) not run on fresh deals: tool_census has 72,000,000 fixed and no --seed-base tool was supplied (KTA_CENSUS unset), so, as 4.6 says, Stiffen's counter stays on the development deals (kt's ${S}_census_kog3 and _kta3: kog3 58 of 127 offered turns, kta3 84 of 152), labelled development-only; it gates nothing either way"
fi

# ---- 9. Scizor (pairings 0-7 of new_decks.tsv at 23,001,000,000): both sides, the shortcut, both mixed directions.
check_pins "before coverage"
COV="Coverage (5.5): the own-side mixed rows run on every pairing listed RUN."
run ${F}_scizor_kog3 "$SC8" $GAMES "${FN[@]}" --bot kog3
run ${F}_scizor_${CL} "$SC8" $GAMES "${FN[@]}" --bot "$CAND"
RS=$(skip scizor "$O/${F}_scizor_kog3.jsonl" "$O/${F}_scizor_${CL}.jsonl" "$SC8" $GAMES "$COV") || die "coverage_skip.py, Scizor"
note "Scizor: mixed rows on [${RS}], skipped [$(minus "$SC8" "$RS")] (${F}_skip_scizor.txt)"
if [ -n "$RS" ]; then
  run ${F}_mixed_scizor_${CL}_first "$RS" $GAMES "${FN[@]}" --bot-a "$CAND" --bot-b kog3
  run ${F}_mixed_scizor_${CL}_second "$RS" $GAMES "${FN[@]}" --bot-a kog3 --bot-b "$CAND"
fi

# ---- 10. The four second lists (their main lists' fresh deals): both sides, the shortcut, the mixed row by side.
for v in $VARS; do
  FV=(--pairs "$PF/fresh_var_$v.tsv" --root "$R" --seed-base "$(var_base $v 23002000000 23000000000)")
  pv=$(python3 "$HERE/make_pairs.py" list "$PF/fresh_var_$v.tsv")
  run ${F}_var_${v}_kog3 "$pv" $GAMES "${FV[@]}" --bot kog3
  run ${F}_var_${v}_${CL} "$pv" $GAMES "${FV[@]}" --bot "$CAND"
  rv=$(skip var_$v "$O/${F}_var_${v}_kog3.jsonl" "$O/${F}_var_${v}_${CL}.jsonl" "$pv" $GAMES "$COV") || die "coverage_skip.py, $v"
  sa=$(python3 "$HERE/make_pairs.py" list "$PF/fresh_var_$v.tsv" --side a --only "$rv")
  sb=$(python3 "$HERE/make_pairs.py" list "$PF/fresh_var_$v.tsv" --side b --only "$rv")
  note "$v: mixed rows on side a [${sa}], side b [${sb}], skipped [$(minus "$pv" "$rv")] (${F}_skip_var_$v.txt)"
  [ -z "$sa" ] || run ${F}_var_${v}_${CL}_mixed_a "$sa" $GAMES "${FV[@]}" --bot-a "$CAND" --bot-b kog3
  [ -z "$sb" ] || run ${F}_var_${v}_${CL}_mixed_b "$sb" $GAMES "${FV[@]}" --bot-a kog3 --bot-b "$CAND"
done

# ---- 11-12. B2e (96 pairings at 23,002,000,000): both sides, the shortcut, the held deck's mixed row.
FB=(--pairs "$PF/fresh_b2e.tsv" --root "$R" --seed-base 23002000000)
run ${F}_b2e_kog3 "$B96" $GAMES "${FB[@]}" --bot kog3
run ${F}_b2e_${CL} "$B96" $GAMES "${FB[@]}" --bot "$CAND"
RB=$(skip b2e "$O/${F}_b2e_kog3.jsonl" "$O/${F}_b2e_${CL}.jsonl" "$B96" $GAMES "$COV Pairings 0-47 (held-out) count; 48-95 (Dustin's files) are reported.") \
  || die "coverage_skip.py, B2e"
note "B2e: mixed rows (the held deck, side a) on [${RB}], skipped [$(minus "$B96" "$RB")] (${F}_skip_b2e.txt)"
[ -z "$RB" ] || run ${F}_mixed_b2e_${CL}_first "$RB" $GAMES "${FB[@]}" --bot-a "$CAND" --bot-b kog3

check_pins "after the last game"
[ ! -e "$O/${F}_rule_findings.txt" ] || note "RULE findings were recorded (${F}_rule_findings.txt): the reading stops until they are explained"
FINISHED=1
echo "KTA DONE $S $(date -u +%FT%TZ)" >> "$O/STATUS.txt"
}  # main
main "$@"; exit $?
