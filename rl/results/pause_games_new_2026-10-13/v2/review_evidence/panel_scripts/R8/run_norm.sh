#!/bin/bash
# run v2's normaliser on the 14 packets into R8/norm (read-only on the repo and on Recording_QA)
R8=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8
QA="/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"
NORM="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/scripts/normalize_ledger.py"
mkdir -p "$R8/norm"
: > "$R8/norm.log"
: > "$R8/games.txt"
for b in BATCH_2026-10-12_NEW_LONG_VIDEOS BATCH_2026-10-12_ADDITIONAL_TWO BATCH_2026-10-13_NEWEST_TWO BATCH_2026-10-13_REMAINING_SIX; do
  for d in "$QA/$b"/2026*; do
    [ -f "$d/TURN_LEDGER.json" ] || continue
    echo "$d" >> "$R8/games.txt"
    python3 -B "$NORM" "$d" "$R8/norm/$(basename "$d")" >> "$R8/norm.log" 2>&1
  done
done
cat "$R8/norm.log"
