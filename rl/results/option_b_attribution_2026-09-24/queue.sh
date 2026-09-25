#!/usr/bin/env bash
# Runs after the before-fix arm: (b) fix 1 only, the k3 table check with both fixes, (c) both fixes.
S=$(cd "$(dirname "$0")" && pwd); cd /home/user/PocketDeckSim/engine
until [ "$(wc -l < "$S/timing.txt")" -ge 3 ]; do sleep 20; done
run() { local bin=$1 tag=$2 bot=$3 games=$4 pairs=$5; local s=$(date +%s)
  "$S/scan_$bin" --decks ../decks/research --games "$games" --pairings "$pairs" --bot "$bot" > "$S/${tag}_$bot.txt" 2>&1
  echo "$tag $bot $(( $(date +%s) - s )) s wall" >> "$S/timing.txt"; }
run wt-fix1 b_fix1 b3n1 500 13,23,2,0,9
run wt-fix1 b_fix1 b3o3n1 500 13,23,2,0,9
run wt-fix1c check_k3_fix1c k3 1000 0
run wt-fix1c c_fix1c b3n1 500 13,23,2,0,9
run wt-fix1c c_fix1c b3o3n1 500 13,23,2,0,9
echo "queue done" >> "$S/timing.txt"
