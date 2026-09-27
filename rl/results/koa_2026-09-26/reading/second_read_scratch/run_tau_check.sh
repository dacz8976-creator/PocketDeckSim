#!/usr/bin/env bash
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
S="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/koa_2026-09-26/reading/second_read_scratch"
cd "$S"
python3 tau_check.py > "$S/tau_check_output.txt" 2>&1; echo "exit $?" >> "$S/tau_check_output.txt"
