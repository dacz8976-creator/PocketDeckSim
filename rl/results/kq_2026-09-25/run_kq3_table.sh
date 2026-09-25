#!/usr/bin/env bash
# kq3 on all 28 pairings x the table's first 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i =
# first-named deck in seat 0), per-game output, paired with ../per_game_table_2026-09-25/k3_500 and
# ../public_pricing_2026-09-25/kp3_500_*. Pairing 21 is Lucario v Weezing, where B2c found the habits.
# Usage: run_kq3_table.sh <legality_scan built at ba20dd8>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
s=$(date +%s)
"$SCAN" --decks ../decks/research --games 500 --bot kq3 --games-out "$D/kq3_500.jsonl" > "$D/kq3_500.txt" 2>&1
echo "kq3_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
echo "kq3 table done" >> "$D/timing.txt"
