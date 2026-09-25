#!/usr/bin/env bash
# Item 1 runs: k3 and b3n1 on all 28 pairings x the table's first 500 deals, then the Hydreigon mixed
# rows. Table seeds only (72,000,000 + pairing x 10,000 + i, i < 500, even i = first-named deck in seat 0).
# Usage: run_item1.sh <scan binary built at engine commit e18ab4b>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run k3_500 --bot k3
run b3n1_500 --bot b3n1
# Hydreigon's 7 cells. It is the second-named deck in pairings 1 (altaria v hydreigon) and 7 (blaziken v
# hydreigon), the first-named in 13-17.
run mixed_hyd-b3n1_first --pairings 13,14,15,16,17 --bot-a b3n1 --bot-b k3
run mixed_hyd-b3n1_second --pairings 1,7 --bot-a k3 --bot-b b3n1
run mixed_hyd-k3_first --pairings 13,14,15,16,17 --bot-a k3 --bot-b b3n1
run mixed_hyd-k3_second --pairings 1,7 --bot-a b3n1 --bot-b k3
echo "item 1 done" >> "$D/timing.txt"
