#!/usr/bin/env bash
# kta's fresh Dustin-deck A/B (REGISTRATION.md 5.6; section 8 row 6): a copy of ../kt_tables_2026-09-28/run_kt_ab.sh with
# the block at 23,004,000,000 (kta_ab_play.py's default) and the kt3 arm dropped. Decks 07, 05, 11, 01, 03 against the
# 8 lists in decks/screen/opponents, 240 games per matchup (120 per seat) = 1,920 per deck and arm; arms kog3 and kta3 on
# the deck's seat, kog3 on the opponent's seat in both. Every arm plays the same seeds, so the arms pair by seed.
# Kept from the original: kta_ab_play.py's gate check, given the existing ../kt_tables_2026-09-28/GATE_koh_b2e_read with
# --gate (5.6; no new gate file); the deckgym sha256 check (the full pin here); one run at a time (the lock); a finished
# arm reused only at its full size; .part then move; kog3's arm for every deck first, then the candidate deck by deck.
# Its identity check points at kta's own record: no A/B game until section 4's checks are recorded as passed in the kta
# tables folder's STATUS.txt with this A/B's knobs (the anchored line "KTA PART A DONE ec7e1a8 <time> knobs <knobs>",
# written by run_kta.sh; for the registered A/B, the registered run's knobs exactly). Not kept: the call to
# read_kt_ab.py at the end (the A/B is read by the reading, read_kta.py, after the footprint is committed); each arm is
# instead checked complete (kta_check.py ab-complete: every (opponent, seat, i) once, seeds on the block's formula, the
# deck the file is named for, the opponents the sorted first 8 of decks/screen/opponents).
# The inputs: run_kta.sh's record <out>/ec7e1a8_fresh_inputs.sha256 (written at its first start) is checked before and
# after every arm (sha256sum -c, and the same list from kta_check.py inputs); any change stops the A/B. The whole script
# is one function, main, called on the last line.
# Run by run_kta.sh at its step 6 (it holds the lock and passes KTA_LOCK_HELD=1); it can also be run alone.
# Output (in the kta tables folder): ec7e1a8_fresh_ab_d<deck>_<arm>.jsonl, .txt beside; STATUS.txt notes, ending with an
# anchored "KTA AB DONE ec7e1a8 <time>" or "KTA AB FAILED <time> ec7e1a8: <why>".
# Knobs (environment; the defaults are the real run, and any other value needs KTA_OUT outside rl/results, compared as
# run_kta.sh compares it):
#   KTA_OUT, KTA_BUILD, THREADS (12), NICE (10), DECKS ("07 05 11 01 03"), CAND (kta3), CAND_LABEL (= CAND: kta3 for
#   kta3; for a kog3 smoke, a label other than kog3 and kta3), AB_GAMES (240 per matchup).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
main() {  # the whole script (called on the last line; the body is left unindented)
S=ec7e1a8
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
[ ! "$HERE" -ef "$R/rl/results/kta_2026-09-29" ] || HERE="$R/rl/results/kta_2026-09-29"   # one spelling (the inputs list)
GATE="$R/rl/results/kt_tables_2026-09-28/GATE_koh_b2e_read"
B=${KTA_BUILD:-/home/dacz8976/engine-kt-$S}
THREADS=${THREADS:-12}; NICE=${NICE:-10}; AB_GAMES=${AB_GAMES:-240}
DECKS=${DECKS:-"07 05 11 01 03"}; CAND=${CAND:-kta3}; CAND_LABEL=${CAND_LABEL:-$CAND}
PIN_GYM=407976366fa2104ee1f2663c94fe31b1c503466defe9d6154b7e60659cb0991c   # REGISTRATION.md section 4
BLOCK=23004000000
GYM="$B/engine/target/release/deckgym"
REGISTERED="12/10/kta3/kta3/500/2000/20/40/40/240/200/07 05 11 01 03/100"   # run_kta.sh's registered knobs
canon_out() {  # as run_kta.sh: absolute, '..' and links resolved, spelled from $R when inside $R/rl/results (-ef)
  local p d rest=""
  p=$(realpath -m -- "$1") || return 1
  d=$p
  while [ "$d" != / ]; do
    if [ -d "$d" ] && [ "$d" -ef "$R/rl/results" ]; then echo "$R/rl/results$rest"; return 0; fi
    rest="/${d##*/}$rest"; d=$(dirname -- "$d")
  done
  echo "$p"
}
if [ -n "${KTA_OUT:-}" ]; then O=$(canon_out "$KTA_OUT") || { echo "run_kta_ab: cannot resolve KTA_OUT $KTA_OUT" >&2; exit 1; }
else
  shopt -s nullglob; ex=("$R"/rl/results/kta_tables_*/); shopt -u nullglob
  [ ${#ex[@]} -eq 1 ] || { echo "run_kta_ab: set KTA_OUT (found ${#ex[@]} kta_tables_* folders)" >&2; exit 1; }
  O=${ex[0]%/}
fi
REAL=1
[ "$THREADS/$NICE/$AB_GAMES/$DECKS/$CAND/$CAND_LABEL" = "12/10/240/07 05 11 01 03/kta3/kta3" ] || REAL=0
case "$O/" in "$R"/rl/results/*) [ $REAL -eq 1 ] || { echo "run_kta_ab: non-registered knobs need KTA_OUT outside rl/results" >&2; exit 1; };; esac
case $CAND in
  kta3) [ "$CAND_LABEL" = kta3 ] || { echo "run_kta_ab: CAND=kta3 needs CAND_LABEL=kta3" >&2; exit 1; };;
  kog3) case $CAND_LABEL in kog3|kta3) echo "run_kta_ab: a kog3 smoke needs a label other than kog3 and kta3 (e.g. kogx)" >&2; exit 1;; esac;;
  *) echo "run_kta_ab: CAND must be kta3 (the registered code) or kog3 (a smoke)" >&2; exit 1;;
esac
[[ $CAND_LABEL =~ ^[a-z0-9]+$ ]] || { echo "run_kta_ab: CAND_LABEL must be lower-case letters and digits" >&2; exit 1; }
[ -d "$O" ] || { echo "run_kta_ab: no folder $O" >&2; exit 1; }
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: run_kta_ab: $*"; echo "KTA AB FAILED $(date -u +%FT%TZ) $S: $*" >> "$O/STATUS.txt"; exit 1; }
[ "$(cat "$B/COMMIT" 2>/dev/null)" = "ec7e1a867bdaae2b0b4a3d2730e36dfffb611900" ] || die "$B is not the build of $S"
[ -x "$GYM" ] || die "no deckgym at $GYM"
[ "$(sha256sum "$GYM" | cut -d' ' -f1)" = "$PIN_GYM" ] || die "deckgym sha256 is not the pin $PIN_GYM (section 4: the runner stops)"
# One run at a time: run_kta.sh passes the lock it holds (fd 9, KTA_LOCK_HELD=1); alone, this takes the same lock.
if [ -z "${KTA_LOCK_HELD:-}" ]; then
  exec 9> "$O/.run_kta.lock"; flock -n 9 || { note "run_kta_ab: another kta run holds the lock; this one exits"; exit 2; }
fi
sed -n "s/^KTA PART A DONE $S [^ ]* knobs //p" "$O/STATUS.txt" \
  | awk -F/ -v t="$THREADS" -v n="$NICE" -v c="$CAND" -v l="$CAND_LABEL" -v g="$AB_GAMES" -v d="$DECKS" -v real=$REAL -v reg="$REGISTERED" \
      '(real == 0 || $0 == reg) && $1 == t && $2 == n && $3 == c && $4 == l && $10 == g && $12 == d { ok = 1 } END { exit !ok }' \
  || die "section 4's checks are not recorded as passed with this A/B's knobs (no 'KTA PART A DONE $S <time> knobs ...' line in $O/STATUS.txt whose knobs are threads $THREADS, nice $NICE, $CAND as $CAND_LABEL, $AB_GAMES games, decks $DECKS$([ $REAL -eq 0 ] || echo ", the registered run"))"
[ -e "$GATE" ] || die "the gate file $GATE is missing (REGISTRATION.md 5.6: it is not moved and no new one is written)"
INPUTS="$O/${S}_fresh_inputs.sha256"
verify_inputs() {  # when: run_kta.sh's inputs record, the hashes (sha256sum -c) and the list (kta_check.py inputs)
  local out
  [ -s "$INPUTS" ] || die "no inputs record $INPUTS (run_kta.sh writes it at its first start, before any game) ($1)"
  out=$(cd "$R" && sha256sum -c --quiet --strict -- "$INPUTS" 2>&1) \
    || die "an input file changed since the run's first start ($1): $(echo "$out" | head -n 3 | tr '\n' ' ')(${S}_fresh_inputs.sha256)"
  out=$(diff <(cut -c67- "$INPUTS") <(python3 "$HERE/kta_check.py" inputs --root "$R" --pairs-dir "$O/pairs" --build "$B" \
          --decks "$DECKS" --here "$HERE" --gate "$GATE") 2>&1) \
    || die "the list of input files changed since the run's first start ($1): $(echo "$out" | grep '^[<>]' | head -n 3 | tr '\n' ' ')(${S}_fresh_inputs.sha256)"
}
verify_inputs "the A/B's start"
note "run_kta_ab $S: decks $DECKS, arms kog3 and $CAND (files '$CAND_LABEL'), $AB_GAMES games per matchup, $THREADS threads, nice $NICE; deckgym sha256 $PIN_GYM; seeds 23,004,000,000 + 10,000 x deck + 1,000 x opponent (+500 seat 1) + i; gate file $(head -c 80 "$GATE")...; the $(wc -l < "$INPUTS") input files unchanged"

unit() {  # deck code label: 8 x AB_GAMES games, written to .part and moved when complete
  local deck=$1 code=$2 lab=$3 name=${S}_fresh_ab_d${1}_${3} s out
  local -a abc=(--games "$AB_GAMES" --block $BLOCK --pilot "$code" --deck "$deck" --opp-dir "$R/decks/screen/opponents")
  verify_inputs "before $name"
  if [ -e "$O/$name.jsonl" ]; then  # reused only when complete (a smoke run's file must never pass as an arm)
    out=$(python3 "$HERE/kta_check.py" ab-complete "$O/$name.jsonl" "${abc[@]}") && return 0
    die "$name.jsonl is there but is not a complete arm of $((8 * AB_GAMES)) games ($out): move it away first"
  fi
  s=$(date +%s)
  ( RAYON_NUM_THREADS=$THREADS nice -n "$NICE" python3 "$HERE/kta_ab_play.py" --deck "$deck" --pilot "$code" --meta-pilot kog3 \
      --engine "$GYM" --expect-sha "$PIN_GYM" --games "$AB_GAMES" --block $BLOCK --gate "$GATE" --out "$O/$name.jsonl.part" ) \
      > "$O/$name.txt" 2>&1 || die "$name (see $name.txt)"
  verify_inputs "after $name"
  out=$(python3 "$HERE/kta_check.py" ab-complete "$O/$name.jsonl.part" "${abc[@]}") \
    || die "$name: the finished arm is not complete ($out)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
for deck in $DECKS; do unit "$deck" kog3 kog3; done                       # kog3's arm first
for deck in $DECKS; do unit "$deck" "$CAND" "$CAND_LABEL"; done           # then the candidate, deck by deck (07 first)
[ "$(sha256sum "$GYM" | cut -d' ' -f1)" = "$PIN_GYM" ] || die "deckgym sha256 changed during the A/B"
verify_inputs "the A/B's end"
echo "KTA AB DONE $S $(date -u +%FT%TZ)" >> "$O/STATUS.txt"
}  # main
main "$@"; exit $?
