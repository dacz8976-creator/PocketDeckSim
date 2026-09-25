#!/usr/bin/env bash
# kp3's mixed rows against k3 on all 28 pairings x the table's first 500 deals (72,000,000 + pairing x 10,000 + i,
# i < 500), both directions, on the official legality_scan (main-7fc6ccb). For rule v2's vetoes in the holdout
# confirmation of kp3; run before any holdout file is opened (simulator side only).
# Usage: run_kp3_mixed.sh   (from anywhere in WSL)
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd)
SCAN="$R/rl/engine-2026-09-25/legality_scan"
echo "legality_scan $(sha256sum "$SCAN" | cut -d' ' -f1)" > "$D/identity.txt"
cd "$R/engine"
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run mixed_kp3_first --bot-a kp3 --bot-b k3
run mixed_kp3_second --bot-a k3 --bot-b kp3
echo "kp3 mixed rows done" >> "$D/timing.txt"
