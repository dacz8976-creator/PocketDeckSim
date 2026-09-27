#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/koa_2026-09-26/reading/second_read_scratch" || exit 1
python3 verify2.py > verify2_out.txt 2>&1
cat verify2_out.txt
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
echo "=== literal check ==="
cat "$R/rl/results/engine_switch_2026-09-26/literal_check.txt"
echo "=== rules09 dir ==="
ls "$R/rl/results/rules09_fixes_2026-09-26/" | head -60
echo "=== grep unconfirmed / verdict in koa reading ==="
grep -ril "unconfirmed\|working pilot" "$R/rl/results/koa_2026-09-26/" 2>/dev/null
echo "=== grep koa in START_HERE / RUN5 / direction for Sept 27 ==="
grep -n "koa" "$R/START_HERE.md" | head -20
grep -n "koa" "$R/rl/RUN5.md" | head
grep -n "koa" "$R/docs/REVIEW_2026-09-24_direction.md" | tail -15
echo "=== 9af40c8 commit message ==="
cd "$R" && git show -s --format=%B 9af40c8 | head -40
echo "=== seed table START_HERE ==="
grep -n -i "seed" "$R/START_HERE.md" | head -40
