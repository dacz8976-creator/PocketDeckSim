#!/usr/bin/env bash
# kd3's mixed rows for the v2 veto rule: kd3 on one side only, kp3 on the other, on all 28 pairings x the table's first
# 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i = first-named deck in seat 0). Fixed before kd3's table
# was read: every pairing, both directions, so no choice depends on which vetoes fire.
# First a kp3 spot replay on this build (pairings 0-2 against ../public_pricing_2026-09-25/kp3_500_*), since kp3 plays
# the other side of every mixed game.
# Usage: run_kd_mixed.sh <legality_scan built at the kd commit> <that commit's engine/ folder>
set -euo pipefail
SCAN=$1; ENG=$2; D=$(cd "$(dirname "$0")" && pwd); cd "$ENG"
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run spot_kp3_p0-2 --pairings 0,1,2 --bot kp3
python3 "$D/../engine_identity_2026-09-25/compare.py" "$D/spot_kp3_p0-2.jsonl" \
  "$D/../public_pricing_2026-09-25/kp3_500_worst5.jsonl" "$D/../public_pricing_2026-09-25/kp3_500_rest.jsonl" \
  > "$D/spot_kp3_p0-2_compare.txt" || true   # exits 1 on a subset of the reference; the counts line is what's read
run mixed_kd3_first --bot-a kd3 --bot-b kp3
run mixed_kd3_second --bot-a kp3 --bot-b kd3
echo "kd mixed rows done" >> "$D/timing.txt"
