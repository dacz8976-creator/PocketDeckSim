#!/usr/bin/env bash
# The engine repairs of Sept 26 (rules/09 and the laptop's repair list): k3 and kp3 over the table's 14,000 games
# (28 pairings x the first 500 deals, 72,000,000 + pairing x 10,000 + i, even i = first-named deck in seat 0) at each
# fix commit, with the legality_scan example as it stands at a03f491 (the counters only watch). compare.py reads the
# outputs against ../per_game_table_2026-09-25/k3_500.jsonl and ../public_pricing_2026-09-25/kp3_500_*.jsonl.
# Usage: [BOTS="k3:500 kp3:500"] run_replay.sh <commit>=<legality_scan built at that commit> ...
# BOTS lists bot:deals pairs (default k3 and kp3 over all 500 deals; spot references use e.g. "kq3:40 kd3:40").
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
BOTS=${BOTS:-"k3:500 kp3:500"}
for pair in "$@"; do c=${pair%%=*}; SCAN=${pair#*=}
  echo "$c scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$D/timing.txt"
  for spec in $BOTS; do bot=${spec%%:*}; n=${spec##*:}; s=$(date +%s)
    "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$D/${c}_${bot}_${n}.jsonl" > "$D/${c}_${bot}_${n}.txt" 2>&1
    echo "${c}_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
  done
done
echo "replay done: BOTS=$BOTS ${*%%=*}" >> "$D/timing.txt"
