#!/usr/bin/env bash
# Re-trace the unexplained games whose dumps came out empty, one game per scan call (both engines), appending to the
# dump files; then re-summarize. Usage: bash redo_missing.sh <bot> <pairing:deal:seed> ...
set -uo pipefail
O="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_2026-09-26"
bot=$1; shift
for g in "$@"; do
  IFS=: read -r p i s <<< "$g"
  for C in 5b75bf9 5bab907; do
    before=$(grep -c "^DUMP $s " "$O/dump_${C}_${bot}.txt")
    if [ "$before" -eq 0 ]; then
      ( cd /home/dacz8976/engine-dump-$C/engine && DUMP_SEEDS="$s" RAYON_NUM_THREADS=8 nice -n 10 \
        ./target/release/examples/legality_scan --decks ../decks/research --pairings "$p" --games $((i + 1)) --bot "$bot" 2>&1 \
        | grep "^DUMP $s " >> "$O/dump_${C}_${bot}.txt" )
    fi
    echo "$bot $g $C: $before -> $(grep -c "^DUMP $s " "$O/dump_${C}_${bot}.txt") lines"
  done
done
cd "$O" && python3 summarize_divergences.py > divergences.txt
