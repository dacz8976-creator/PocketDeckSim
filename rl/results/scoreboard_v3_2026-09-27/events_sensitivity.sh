#!/usr/bin/env bash
# Event-level sensitivity of the 45-cell readings already made (Astra, Sept 28): each candidate against kp3 on the
# development data, with the match-level and the event-resampled intervals side by side. Reads existing runs only.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results"; K="$R/kpf_2026-09-26/reading"; O="$R/scoreboard_v3_2026-09-27"
dir_of() { case $1 in koa3) echo "$R/koa_2026-09-26/reading";; kog3) echo "$R/kog_composition_2026-09-27";; *) echo "$K";; esac; }
: > "$O/events_sensitivity.txt"
for b in kpg3 koa3 kog3 kpr3 kpf3; do
  D=$(dir_of $b)
  echo "=== $b against kp3, 45 cells (development half; rules v2; no mixed rows here, so vetoes aren't read)" >> "$O/events_sensitivity.txt"
  ( cd "$K" && nice -n 5 python3 score45.py --rules v2 --old-games "$K/table_kp3.jsonl" "$K/new17_kp3.jsonl" \
      --new-games "$D/table_$b.jsonl" "$D/new17_$b.jsonl" --old kp3 --new $b ) 2>&1 \
    | grep -E '^== |: real error [0-9]|dMSE|real error, ' >> "$O/events_sensitivity.txt"
done
cat "$O/events_sensitivity.txt"
