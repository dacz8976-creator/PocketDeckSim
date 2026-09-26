#!/usr/bin/env bash
# The rules/09 engine fixes of Sept 26: k3 and kp3 over the table's 14,000 games (28 pairings x the first 500 deals,
# 72,000,000 + pairing x 10,000 + i, even i = first-named deck in seat 0) at each fix commit, with the legality_scan
# example as it stands at a03f491 (the counters only watch). compare.py reads the outputs against
# ../per_game_table_2026-09-25/k3_500.jsonl and ../public_pricing_2026-09-25/kp3_500_*.jsonl.
# Usage: run_replay.sh <commit>=<legality_scan built at that commit> ...
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for pair in "$@"; do c=${pair%%=*}; SCAN=${pair#*=}
  echo "$c scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$D/timing.txt"
  for bot in k3 kp3; do s=$(date +%s)
    "$SCAN" --decks ../decks/research --games 500 --bot "$bot" --games-out "$D/${c}_${bot}_500.jsonl" > "$D/${c}_${bot}_500.txt" 2>&1
    echo "${c}_${bot}_500 $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
  done
done
echo "replay done: ${*%%=*}" >> "$D/timing.txt"
