#!/usr/bin/env bash
# Chase Order discard count, kq3 v kp3, on Vespiquen's seven pairings (5, 11, 16, 20, 23, 25, 27) x the table's
# first 500 deals (72,000,000 + pairing x 10,000 + i). The games must equal the stored kq3 and kp3 tables.
# Usage: run_chase_order.sh <legality_scan built at b7c0ace>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for bot in kp3 kq3; do s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 --pairings 5,11,16,20,23,25,27 --bot $bot --games-out "$D/${bot}_vespiquen.jsonl" > "$D/${bot}_vespiquen.txt" 2>&1
  echo "${bot}_vespiquen $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "chase order done" >> "$D/timing.txt"
