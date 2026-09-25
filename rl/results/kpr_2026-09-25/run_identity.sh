#!/usr/bin/env bash
# k3, kp3 and kq3 must replay the whole table unchanged with the kpr code in place (all 28 pairings x the table's
# first 500 deals), and kd3 (not adopted) its first 40 deals of every pairing. Deals: 72,000,000 + pairing x 10,000 + i.
# Fingerprints compared with ../per_game_table_2026-09-25/k3_500.jsonl, ../public_pricing_2026-09-25/kp3_500_*.jsonl,
# ../kq_2026-09-25/kq3_500.jsonl and ../kd_2026-09-25/kd3_500.jsonl.
# Usage: run_identity.sh <legality_scan built with the kpr code>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for spec in k3:500 kp3:500 kq3:500 kd3:40; do bot=${spec%%:*}; n=${spec##*:}; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$D/identity_${bot}_${n}.jsonl" > "$D/identity_${bot}_${n}.txt" 2>&1
  echo "identity_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "identity done" >> "$D/timing.txt"
