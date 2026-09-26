#!/usr/bin/env bash
# kpf3's mixed rows for the rule-v2 vetoes (kpf3 on one side only, kp3 on the other), on the same deals as the reading:
# the 28 table cells and the 17 new cells, each deck-a-only (first) and deck-b-only (second), at the same build.
# Waits for run_kpf_reading.sh's anchored last line, never on a process name or a command line.
# Usage (WSL): nohup setsid bash run_kpf_mixed.sh > mixed.log 2>&1 &
set -euo pipefail
O="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/reading"
B=/home/dacz8976/engine-kpf-9bffbda; SCAN="$B/engine/target/release/examples/legality_scan"
NEW=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
until grep -Eq '^[0-9-]+ [0-9:]+ KPF READING RUNS DONE$' "$O/STATUS.txt" 2>/dev/null; do
  grep -q ' FAILED: ' "$O/STATUS.txt" 2>/dev/null && { echo "reading runs failed; mixed rows not started"; exit 1; }
  sleep 60
done
cd "$B/engine"
mix() {  # name botA botB args...
  local name=$1 ba=$2 bb=$3; shift 3
  [ ! -s "$O/$name.jsonl" ] || { note "$name exists, skipped"; return; }
  local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --bot-a "$ba" --bot-b "$bb" --games-out "$O/$name.jsonl.part" \
    > "$O/$name.txt" 2>&1 || { note "FAILED: $name scan"; exit 1; }
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
mix mixed_table_kpf3_first kpf3 kp3 --decks ../decks/research
mix mixed_table_kpf3_second kp3 kpf3 --decks ../decks/research
NEW17=(--pairs "$B/$NEW" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
mix mixed_new17_kpf3_first kpf3 kp3 "${NEW17[@]}"
mix mixed_new17_kpf3_second kp3 kpf3 "${NEW17[@]}"
echo "$(date -u +%F\ %T) KPF MIXED ROWS DONE" >> "$O/STATUS.txt"
