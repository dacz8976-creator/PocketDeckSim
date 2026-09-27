#!/usr/bin/env bash
# kpg's held-out check (REGISTRATION.md section 4): kpg3 on B2e's 96 pairings and on the Scizor coverage row, at the
# official engine, after koa's runs (never two game runs at once beyond what's queued). Anchored waits only.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/kpg_2026-09-27"
SCAN="$R/rl/engine-2026-09-27/legality_scan"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
until grep -q 'KOA RUNS DONE' "$R/rl/results/koa_2026-09-26/reading/STATUS.txt" 2>/dev/null; do
  grep -q 'FAILED' "$R/rl/results/koa_2026-09-26/reading/STATUS.txt" 2>/dev/null && break; sleep 60; done
cd "$R/engine"
run() { local name=$1; shift; [ -s "$O/$name.jsonl" ] && return; local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --bot kpg3 --games-out "$O/$name.jsonl.part" > "$O/$name.txt" 2>&1 \
    || { note "FAILED: $name"; exit 1; }
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"; }
run b2e_kpg3 --pairs "$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 0 95)"
run scizor_kpg3 --pairs "$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)"
echo "$(date -u +%F\ %T) KPG HELDOUT RUNS DONE" >> "$O/STATUS.txt"
