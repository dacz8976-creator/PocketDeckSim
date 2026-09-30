#!/bin/bash
# checker-a: run check_a.py on the committed raw sample rows (WSL).
set -euo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$REPO/rl/results/km_tables_2026-09-30"
cd "$D/independent_check_a"
# the working-tree files must equal the ones committed at 1fc9e0b
for f in 1f6319e_sample_kta3_rows.jsonl 1f6319e_sample_km3_rows.jsonl; do
  c=$(git -C "$REPO" show "1fc9e0b:rl/results/km_tables_2026-09-30/$f" | sha256sum | cut -d' ' -f1)
  w=$(sha256sum "$D/$f" | cut -d' ' -f1)
  echo "$f committed-at-1fc9e0b $c working-tree $w"
  [ "$c" = "$w" ] || { echo "MISMATCH $f"; exit 1; }
done
python3 check_a.py "$D/1f6319e_sample_kta3_rows.jsonl" "$D/1f6319e_sample_km3_rows.jsonl" "$D/independent_check_a/check_a.txt"
