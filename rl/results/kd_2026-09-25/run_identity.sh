#!/usr/bin/env bash
# k3, kp3 and kq3 must replay the table's games unchanged with the kd code in place: all 28 pairings x the
# table's first 500 deals (72,000,000 + pairing x 10,000 + i), fingerprints compared with
# ../per_game_table_2026-09-25/k3_500.jsonl, ../public_pricing_2026-09-25/kp3_500_*.jsonl and
# ../kq_2026-09-25/kq3_500.jsonl.
# Usage: run_identity.sh <legality_scan built with the kd code>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for bot in k3 kp3 kq3; do s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 --bot $bot --games-out "$D/identity_${bot}_500.jsonl" > "$D/identity_${bot}_500.txt" 2>&1
  echo "identity_${bot}_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "identity done" >> "$D/timing.txt"
