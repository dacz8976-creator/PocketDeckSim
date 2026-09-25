#!/usr/bin/env bash
# kd3 on all 28 pairings x the table's first 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i =
# first-named deck in seat 0), per-game output, paired with ../per_game_table_2026-09-25/k3_500 and
# ../public_pricing_2026-09-25/kp3_500_*.
# Usage: run_kd3_table.sh <legality_scan built at the kd commit named in README.md>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
s=$(date +%s)
"$SCAN" --decks ../decks/research --games 500 --bot kd3 --games-out "$D/kd3_500.jsonl" > "$D/kd3_500.txt" 2>&1
echo "kd3_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
echo "kd3 table done" >> "$D/timing.txt"
