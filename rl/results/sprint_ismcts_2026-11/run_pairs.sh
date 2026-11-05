#!/usr/bin/env bash
# Paired runs: CAND v km3 and km3 v km3 on the same seeds, every deck x opponent.
#   run_pairs.sh <deckgym binary> <out dir> <cand code> <games per pairing> <seed base> <threads> <deck>... -- <opponent>...
# Pairing k (in the order given) uses seeds <seed base> + 1000k ... + games - 1. The baseline is skipped if already there.
set -euo pipefail
BIN=$1 OUT=$2 CAND=$3 N=$4 SEED=$5 J=$6; shift 6
DECKS=(); while [ "$1" != "--" ]; do DECKS+=("$1"); shift; done; shift; OPPS=("$@")
k=0
for d in "${DECKS[@]}"; do for o in "${OPPS[@]}"; do
  s=$((SEED + 1000 * k)); k=$((k + 1))
  tag="$(basename "$d" .txt)__$(basename "$o" .txt)"
  for P in "$CAND,km3" "km3,km3"; do
    dir="$OUT/${P/,/__}/$tag"
    if [ -d "$dir" ] && [ "$(ls "$dir" | wc -l)" -ge "$N" ]; then continue; fi
    mkdir -p "$dir"
    t0=$(date +%s.%N)
    "$BIN" simulate "$d" "$o" --players "$P" --num "$N" --seed "$s" --seed-stream -p -j "$J" --results-output "$dir" > /dev/null 2> "$dir.err"
    echo "$P $tag seeds $s.. $(echo "$(date +%s.%N) - $t0" | bc) s" >> "$OUT/timing.txt"
  done
done; done
