#!/usr/bin/env bash
# Deeper-search table: k4, then k5, then k6 piloting both sides of the Sept 23 Limitless check's 28 pairings,
# on that table's exact deals, scored against the same Limitless numbers. Nothing is trained or changed.
# Start, or resume after any interruption, with the same line in WSL Ubuntu:
#   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/results/deep_search_table/run_deep_table.sh"
# It runs in the background. Progress, in plain words, every minute: STATUS.txt beside this file.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$HOME/.cache/pocket-deck-lab/run5-venv/bin/python"   # add-on 0.7.2, installed by run_training_v5.sh
[ -x "$PY" ] || { echo "MISSING $PY (run_training_v5.sh creates it)"; exit 1; }
if pgrep -f "deep_table.py" >/dev/null; then echo "Already running. Progress: $HERE/STATUS.txt"; exit 0; fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$HERE"
echo "== $(date '+%Y-%m-%d %H:%M') start/resume" >> "$HERE/run.log"
nohup setsid "$PY" "$HERE/deep_table.py" --bots k4,k5,k6 --games 1000 --workers 8 >> "$HERE/run.log" 2>&1 < /dev/null &
sleep 30
if pgrep -f "deep_table.py" >/dev/null; then
  echo "Running. Progress: $HERE/STATUS.txt (updates every minute). You can close this window."
  tail -n 3 "$HERE/run.log"
else
  echo "It stopped. Last lines of run.log:"; tail -n 20 "$HERE/run.log"; exit 1
fi
