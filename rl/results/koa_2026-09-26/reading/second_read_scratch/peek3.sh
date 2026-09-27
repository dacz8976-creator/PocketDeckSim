#!/bin/bash
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
sed -n '112,145p' "$R/START_HERE.md"
echo "=== kpg / one pilot mentions ==="
grep -n "kpg" "$R/START_HERE.md" "$R/rl/RUN5.md" "$R/docs/REVIEW_2026-09-24_direction.md" | cut -c1-400 | head -20
grep -n -i "one pilot" "$R/START_HERE.md" "$R/rl/RUN5.md" "$R/docs/REVIEW_2026-09-24_direction.md" | cut -c1-300 | head -20
echo "=== table_koa3.txt head ==="
head -20 "$R/rl/results/koa_2026-09-26/reading/table_koa3.txt"
echo "=== kpf READING.md ==="
cat "$R/rl/results/kpf_2026-09-26/reading/READING.md"
echo "=== kpg STATUS / run script ==="
cat "$R/rl/results/kpg_2026-09-27/run_kpg_heldout.sh"
cat "$R/rl/results/kpg_2026-09-27/STATUS.txt" 2>/dev/null
