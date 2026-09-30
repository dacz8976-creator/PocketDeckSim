#!/bin/bash
# checker-a, step 2: append the comparison with thresholds.json to check_a.txt (run once, after run_check_a.sh).
set -euo pipefail
D="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30"
cd "$D/independent_check_a"
python3 compare_a.py "$D/independent_check_a/check_a.txt" "$D/thresholds.json"
