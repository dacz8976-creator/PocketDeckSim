#!/usr/bin/env bash
# The engine switch's literal check (Dustin, Sept 26: "every game that came out differently is one in which the
# mechanic fired"). Builds 5b75bf9 (the Legendary Pulse fix, just before the promotion fix) with instrument_scan.py's
# watch-only counters, and plays k3 and kp3 over the table's 14,000 deals. check_literal.py then requires:
# - the instrumented games equal the cloud's 5b75bf9 files (the counters change no play);
# - every game the Pulse fix changed (5b75bf9 vs 3102c9e) had a Legendary Pulse end of turn;
# - every game the promotion fix changed (5bab907 vs 5b75bf9) had an end-of-turn or Checkup Knock Out, read on
#   5b75bf9's trajectory (the games agree up to the first such Knock Out, so that is where the fix can first act).
# Runs beside the kpf queue at nice 19, 6 threads, build capped at 4 jobs.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/engine_switch_2026-09-26"; B=/home/dacz8976/engine-watch-5b75bf9; C=5b75bf9
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
cd "$R"
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  [ ! -e "$B" ] || { note "FAILED: $B exists without a scan"; exit 1; }
  mkdir -p "$B"; git rev-parse "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  python3 "$O/instrument_scan.py" "$B/engine/examples/legality_scan.rs" >> "$O/STATUS.txt" 2>&1 || { note "FAILED: instrument"; exit 1; }
  ( cd "$B/engine" && nice -n 19 cargo build --release --example legality_scan -j 4 ) > "$O/build.log" 2>&1 || { note "FAILED: build"; exit 1; }
  note "built instrumented $C"
fi
SCAN="$B/engine/target/release/examples/legality_scan"
cd "$B/engine"
for bot in k3 kp3; do
  out="$O/watch_${C}_${bot}_500"
  [ -s "$out.jsonl" ] && continue
  RAYON_NUM_THREADS=6 nice -n 19 "$SCAN" --decks ../decks/research --games 500 --bot $bot --games-out "$out.jsonl.part" \
    > "$out.txt" 2>&1 || { note "FAILED: $bot scan"; exit 1; }
  mv "$out.jsonl.part" "$out.jsonl"; note "watch $bot done ($(wc -l < "$out.jsonl") games)"
done
echo "$(date -u +%F\ %T) WATCH RUNS DONE" >> "$O/STATUS.txt"
