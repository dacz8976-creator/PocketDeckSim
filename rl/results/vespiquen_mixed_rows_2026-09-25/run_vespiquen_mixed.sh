#!/usr/bin/env bash
# Vespiquen's seven cells with kp3 on one side only, table deals only (72,000,000 + pairing x 10,000 + i,
# i < 500, even i = first-named deck in seat 0). Vespiquen is second-named in pairings 5, 11, 16, 20, 23, 25
# and first-named in 27. Both-sides rows are ../per_game_table_2026-09-25/k3_500 and
# ../public_pricing_2026-09-25/kp3_500_*. Usage: run_vespiquen_mixed.sh <legality_scan built at 150a305 (engine c7cb688)>
set -euo pipefail
SCAN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run mixed_vesp-kp3_second --pairings 5,11,16,20,23,25 --bot-a k3 --bot-b kp3
run mixed_vesp-kp3_first --pairings 27 --bot-a kp3 --bot-b k3
run mixed_vesp-k3_second --pairings 5,11,16,20,23,25 --bot-a kp3 --bot-b k3
run mixed_vesp-k3_first --pairings 27 --bot-a k3 --bot-b kp3
echo "vespiquen mixed done" >> "$D/timing.txt"
