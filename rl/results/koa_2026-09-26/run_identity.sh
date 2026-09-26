#!/usr/bin/env bash
# koa's identity checks (REGISTRATION.md section 4) at its build commit 9af40c8, against the repaired engine's
# references in ../rules09_fixes_2026-09-26/af8489f_*: k3 and kp3 over the whole table (28 pairings x 500 deals), kq3
# and kd3 on 40 deals per pairing, and koa3 on 40 deals per pairing for the setup-only check (every game whose two
# openings match kp3's must equal it move for move). Deals: 72,000,000 + pairing x 10,000 + i, even i = first-named deck
# in seat 0. Usage: run_identity.sh <legality_scan built at 9af40c8>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
echo "9af40c8 scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$D/timing.txt"
for spec in k3:500 kp3:500 kq3:40 kd3:40 koa3:40; do bot=${spec%%:*}; n=${spec##*:}; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$D/identity_${bot}_${n}.jsonl" > "$D/identity_${bot}_${n}.txt" 2>&1
  echo "identity_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "identity done" >> "$D/timing.txt"
