#!/usr/bin/env bash
# The one-time holdout confirmation of kp3 against k3 (rule: ../table_readings_2026-09-24/README.md, pre-registered at
# 10c4e66). Run once, after Dustin's go-ahead and after ../kp3_mixed_rows_2026-09-25/ is complete.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); cd "$D/.."
grep -q "kp3 mixed rows done" kp3_mixed_rows_2026-09-25/timing.txt || { echo "kp3 mixed rows not complete"; exit 1; }
[ ! -e "$D/limitless_holdout.json" ] || { echo "the holdout was already opened; this script runs once"; exit 1; }
date -u +"opened %Y-%m-%dT%H:%M:%SZ" > "$D/OPENED.txt"
python3 "$D/build_holdout.py" --open-holdout | tee -a "$D/OPENED.txt"
S=table_readings_2026-09-24/score.py
K=per_game_table_2026-09-25/k3_500.jsonl
P="public_pricing_2026-09-25/kp3_500_worst5.jsonl public_pricing_2026-09-25/kp3_500_rest.jsonl"
M="--mixed kp3_mixed_rows_2026-09-25/mixed_kp3_first.jsonl kp3_mixed_rows_2026-09-25/mixed_kp3_second.jsonl"
# (i) and (iii): the holdout cells alone
python3 $S --rules v2 --old-games $K --new-games $P --old k3 --new kp3 --limitless "$D/limitless_holdout.json" \
  --limitless-events "$D/limitless_holdout_events.json" $M > "$D/kp3_vs_k3_holdout.txt"
# (ii): development + holdout pooled
python3 $S --rules v2 --old-games $K --new-games $P --old k3 --new kp3 --limitless "$D/limitless_pooled.json" \
  --limitless-events "$D/limitless_pooled_events.json" $M > "$D/kp3_vs_k3_pooled.txt"
# the development half with the same mixed rows, for the sign in (i) and for comparison
python3 $S --rules v2 --old-games $K --new-games $P --old k3 --new kp3 \
  --limitless scoreboard_v2_2026-09-25/limitless_v2_dev.json \
  --limitless-events scoreboard_v2_2026-09-25/limitless_v2_dev_events.json $M > "$D/kp3_vs_k3_development.txt"
echo "confirmation outputs written" >> "$D/OPENED.txt"
