#!/usr/bin/env bash
# The watch-only reach build: the new commit plus instrument_reach.py, in a scratch tree outside the repo.
# Usage (WSL): bash build_watch.sh <commit>
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-28"
C=$(git -C "$R" rev-parse "$1"); W=/home/dacz8976/engine-watch-${C:0:7}
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/PIN_STATUS.txt"; }
rm -rf "$W"; mkdir -p "$W"; echo "$C" > "$W/COMMIT"; git -C "$R" archive "$C" engine decks | tar -x -C "$W"
python3 "$O/instrument_reach.py" "$W/engine" > "$O/watch_patch.txt"
( cd "$W/engine" && nice -n 10 cargo build --release --example legality_scan -j 8 ) > "$O/watch_build.log" 2>&1 \
  || { note "WATCH BUILD FAILED (watch_build.log)"; exit 1; }
note "watch build of $C ready: $W/engine/target/release/examples/legality_scan"
