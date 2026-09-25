#!/usr/bin/env bash
# Item 2 runs: kp3 (B1' public pricing, engine commit 858b6fe) on the table's first 500 deals, the five
# worst cells first, then the other 23; together the whole table. Table seeds only (72,000,000 +
# pairing x 10,000 + i, i < 500, even i = first-named deck in seat 0). Waits for item 1 to finish.
# Usage: run_item2.sh <scan binary built at 858b6fe>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
until grep -q "item 1 done" "$D/../per_game_table_2026-09-25/timing.txt" 2>/dev/null; do sleep 30; done
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run kp3_500_worst5 --bot kp3 --pairings 13,23,2,0,9
run kp3_500_rest --bot kp3 --pairings 1,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20,21,22,24,25,26,27
echo "item 2 done" >> "$D/timing.txt"
