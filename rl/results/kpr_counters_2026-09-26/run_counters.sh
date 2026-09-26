#!/usr/bin/env bash
# The counters Fable's kpr review asked for (question 5), with one identity replay: kp3 and kpr3 on all 28 pairings x
# the table's first 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i = first-named deck in seat 0), with the
# legality_scan that adds per-cell counters for Mega Burning, Terminating Tail and Diving Icicles (as Hyper Ray) and
# every activated Ability's offered and used turns. The fingerprints must equal ../public_pricing_2026-09-25/kp3_500_*
# and ../kpr_2026-09-25/kpr3_500.jsonl: the counters only watch.
# Usage: run_counters.sh <legality_scan built with the counters>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for bot in kp3 kpr3; do s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 --bot "$bot" --games-out "$D/${bot}_500_counters.jsonl" > "$D/${bot}_500_counters.txt" 2>&1
  echo "${bot}_500_counters $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "counters done" >> "$D/timing.txt"
