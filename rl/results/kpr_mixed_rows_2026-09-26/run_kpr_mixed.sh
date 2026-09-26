#!/usr/bin/env bash
# kpr3's mixed rows for the rule-v2 read: kpr3 on one side only, kp3 on the other, on all 28 pairings x the table's
# first 500 deals (72,000,000 + pairing x 10,000 + i, i < 500, even i = first-named deck in seat 0), both directions,
# fixed before the laptop reads kpr3's table, so no choice depends on which vetoes fire. Same design as kd3's
# (../kd_mixed_rows_2026-09-25). Before the rows: (1) a kp3 spot replay on this build (pairings 0-2 against
# ../public_pricing_2026-09-25/kp3_500_*), since kp3 plays the other side of every mixed game; (2) kpr3 v kpr3 on
# pairing 1 against the cloud's kpr3_500.jsonl, move by move, so the kpr3 here is the table's kpr3.
# Usage: run_kpr_mixed.sh <legality_scan built at e09fb46> <that commit's engine/ folder> <cloud kpr3_500.jsonl>
set -euo pipefail
SCAN=$1; ENG=$2; CLOUD=$3; D=$(cd "$(dirname "$0")" && pwd); cd "$ENG"
echo "legality_scan $(sha256sum "$SCAN" | cut -d' ' -f1)  (built from e09fb46)" > "$D/identity.txt"
run() { local tag=$1; shift; local s=$(date +%s)
  "$SCAN" --decks ../decks/research --games 500 "$@" --games-out "$D/$tag.jsonl" > "$D/$tag.txt" 2>&1
  echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
run spot_kp3_p0-2 --pairings 0,1,2 --bot kp3
python3 "$D/../engine_identity_2026-09-25/compare.py" "$D/spot_kp3_p0-2.jsonl" \
  "$D/../public_pricing_2026-09-25/kp3_500_worst5.jsonl" "$D/../public_pricing_2026-09-25/kp3_500_rest.jsonl" \
  > "$D/spot_kp3_p0-2_compare.txt" || true   # exits 1 on a subset of the reference; the counts line is what's read
run kpr3_replay_p1 --pairings 1 --bot kpr3
python3 "$D/../engine_identity_2026-09-25/compare.py" "$D/kpr3_replay_p1.jsonl" "$CLOUD" \
  > "$D/kpr3_replay_p1_compare.txt" || true
run mixed_kpr3_first --bot-a kpr3 --bot-b kp3
run mixed_kpr3_second --bot-a kp3 --bot-b kpr3
echo "kpr mixed rows done" >> "$D/timing.txt"
