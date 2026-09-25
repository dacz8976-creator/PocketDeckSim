#!/usr/bin/env bash
# B2b: k3 with the status-clock feature on both sides, table deals only (72,000,000 + pairing x 10,000 + i,
# i < 500). Altaria v Blaziken (0), Lucario (2), Sceptile (3), Suicune (4); controls with no Sleep or
# Paralysis in either list: Blaziken v Lucario (8), Sceptile v Suicune (22).
# Usage: run_status_clock.sh <legality_scan built at ca8c0b9 with --features status-clock>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
s=$(date +%s)
"$SCAN" --decks ../decks/research --games 500 --pairings 0,2,3,4,8,22 --bot k3 \
  --games-out "$D/status_clock_k3_500.jsonl" > "$D/status_clock_k3_500.txt" 2>&1
echo "status_clock_k3_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
