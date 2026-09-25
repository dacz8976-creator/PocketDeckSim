#!/usr/bin/env bash
# B2a census: k3 and kp3 on the table's first 200 deals of all 28 pairings (table seeds only:
# 72,000,000 + pairing x 10,000 + i, i < 200). Usage: run_census.sh <census binary built at f8dfaf5>
set -euo pipefail
BIN=$1; D=$(cd "$(dirname "$0")" && pwd); cd "$D/../../../engine"
for bot in k3 kp3; do
  s=$(date +%s)
  "$BIN" --decks ../decks/research --games 200 --bot $bot --out "$D/census_$bot.json" \
    --games-out "$D/games_$bot.jsonl" > "$D/census_$bot.txt" 2> "$D/census_$bot.log"
  echo "$bot $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "census done" >> "$D/timing.txt"
