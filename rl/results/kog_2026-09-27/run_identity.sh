#!/usr/bin/env bash
# kog's identity checks (the composition proof), on the table's deals (72,000,000 + pairing x 10,000 + i, even i =
# first-named deck in seat 0; all 28 pairings):
# - kog3 over all 500 deals, read by compose.py against the official koa3 and kpg3 tables;
# - k3 and kp3 over all 500 deals against the official references;
# - koa3 and kpg3 over the first 40 deals against the official tables (the build plays them as before).
# kt's identity runs, which share the machine, were lowered to the lowest CPU priority for these. OUT (default: this
# folder) takes the outputs while they run; they are copied here when complete.
# Usage: [OUT=<dir>] run_identity.sh <legality_scan built at the kog build commit> <label>
set -euo pipefail
SCAN=$1; L=$2; D=$(cd "$(dirname "$0")" && pwd); O=${OUT:-$D}; cd "$D/../../../engine"
echo "$L scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$O/timing.txt"
run() { local bot=$1 n=$2 s; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$O/${L}_${bot}_${n}.jsonl" > "$O/${L}_${bot}_${n}.txt" 2>&1
  echo "${L}_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$O/timing.txt"; }
run kog3 500; run koa3 40; run kpg3 40; run k3 500; run kp3 500
echo "$L identity done" >> "$O/timing.txt"
