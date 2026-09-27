#!/usr/bin/env bash
# kpr3 on all 28 pairings x the table's first 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i =
# first-named deck in seat 0), per-game output, paired with ../per_game_table_2026-09-25/k3_500 and
# ../public_pricing_2026-09-25/kp3_500_*. Then k3, kp3 and kq3 on the first 40 deals of every pairing with the same
# build, the identity check at the table's own commit (the full replay ran at 53638a7).
# Usage: run_kpr3_table.sh <legality_scan built at the kpr commit named in README.md>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
s=$(date +%s)
"$SCAN" --decks ../decks/research --games 500 --bot kpr3 --games-out "$D/kpr3_500.jsonl" > "$D/kpr3_500.txt" 2>&1
echo "kpr3_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
for bot in k3 kp3 kq3; do s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 40 --bot "$bot" --games-out "$D/table_commit_identity_${bot}_40.jsonl" > "$D/table_commit_identity_${bot}_40.txt" 2>&1
  echo "table_commit_identity_${bot}_40 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "kpr3 table done" >> "$D/timing.txt"
