#!/usr/bin/env bash
# Waits for run_kog_composition.sh's anchored last line (or a FAILED line), then reads (read_kog.py).
O="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kog_composition_2026-09-27"
until grep -Eq '^[0-9-]+ [0-9:]+ KOG COMPOSITION RUNS DONE$' "$O/STATUS.txt" 2>/dev/null; do
  grep -q ' FAILED: ' "$O/STATUS.txt" 2>/dev/null && { echo "RUNS FAILED" > "$O/READ_DONE.txt"; exit 1; }
  sleep 60
done
cd "$O" && nice -n 5 python3 read_kog.py > READING_numbers.txt 2> read.err
echo "READ DONE $(date -u +%FT%TZ)" > "$O/READ_DONE.txt"
