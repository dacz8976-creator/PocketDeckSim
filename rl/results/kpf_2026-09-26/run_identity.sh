#!/usr/bin/env bash
# kpf's identity checks at its build (REGISTRATION.md section 5), on the table's deals (72,000,000 + pairing x 10,000
# + i, i < 40, even i = first-named deck in seat 0; all 28 pairings, a superset of the registered 2 x 40):
# - kp3 and k3 must equal the repaired engine's references (../rules09_fixes_2026-09-26/af8489f_{kp3,k3}_500.jsonl, first
#   40 deals);
# - kpr3 must equal ../rules09_fixes_2026-09-26/af8489f_kpr3_40.jsonl;
# - kpf3 and kpg3 are run on the same deals as smokes (they must run clean), their changed games reported.
# Usage: run_identity.sh <legality_scan built at the kpf build commit>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
echo "kpf build scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$D/timing.txt"
for bot in kp3 k3 kpr3 kpf3 kpg3; do s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 40 --bot "$bot" --games-out "$D/identity_${bot}_40.jsonl" > "$D/identity_${bot}_40.txt" 2>&1
  echo "identity_${bot}_40 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "identity done" >> "$D/timing.txt"
