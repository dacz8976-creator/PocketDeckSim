#!/usr/bin/env bash
# kpr3's rule-v2 reading (laptop, Sept 26): score.py on kp3 (current) v kpr3 (new), paired by deal, with the mixed rows.
# The kpr3 table is the cloud's rl/results/kpr_2026-09-25/kpr3_500.jsonl on origin/claude/pensive-ptolemy-spwc0b (aa87fa3),
# copied out with git show (not kept in the repo); its sha256 is checked first (19b95ae0..., the blob Fable read).
# Usage (WSL): run_score.sh <copy of kpr3_500.jsonl>
set -euo pipefail
KPR=$1
cd "$(dirname "$0")/../.."     # rl/results
OUT=table_readings_2026-09-24/kpr3_reading
sha256sum "$KPR" | tee "$OUT/kpr3_500_sha256.txt"
grep -q '^19b95ae0f8849c815cb8b82158441a4bd8b2216f89d162d9466d1d02f9a5bde0 ' "$OUT/kpr3_500_sha256.txt"
S=table_readings_2026-09-24/score.py
KP3="public_pricing_2026-09-25/kp3_500_worst5.jsonl public_pricing_2026-09-25/kp3_500_rest.jsonl"
MIX="kpr_mixed_rows_2026-09-26/mixed_kpr3_first.jsonl kpr_mixed_rows_2026-09-26/mixed_kpr3_second.jsonl"
V2=scoreboard_v2_2026-09-25
# The deciding reading: scoreboard v2's development cells, both intervals, mixed rows.
python3 $S --rules v2 --old kp3 --new kpr3 --old-games $KP3 --new-games "$KPR" --mixed $MIX \
  --limitless $V2/limitless_v2_dev.json --limitless-events $V2/limitless_v2_dev_events.json > $OUT/kpr3_vs_kp3_v2.txt
# Descriptive: the Sept 23 cells (the cloud's table), with the mixed rows.
python3 $S --rules v2 --old kp3 --new kpr3 --old-games $KP3 --new-games "$KPR" --mixed $MIX > $OUT/kpr3_vs_kp3_sept23.txt
# Descriptive: against k3 on v2 (no mixed rows exist for that pair).
python3 $S --rules v2 --old k3 --new kpr3 --old-games per_game_table_2026-09-25/k3_500.jsonl --new-games "$KPR" \
  --limitless $V2/limitless_v2_dev.json --limitless-events $V2/limitless_v2_dev_events.json > $OUT/kpr3_vs_k3_v2.txt
echo done
