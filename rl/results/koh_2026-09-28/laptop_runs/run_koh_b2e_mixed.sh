#!/usr/bin/env bash
# koh's B2e own-side mixed rows (Dustin's coverage ruling, Sept 28 evening: coverage rows count for the mixed-row veto,
# so they are run every time): koh3 on the held deck (deck a in every B2e pairing), kog3 on the panel list, all 96
# pairings x 500 on B2e's deals (21,106,000,000). The held-out archetypes (0-47) count; Dustin's files (48-95) are
# reported. Waits for run_koh_b2e.sh's anchored line. Official engine.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koh_2026-09-28/laptop_runs"
SCAN="$R/rl/engine-2026-09-28/legality_scan"; B2E="$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
until grep -q 'KOH B2E DONE' "$O/STATUS.txt" 2>/dev/null; do grep -q 'FAILED: b2e' "$O/STATUS.txt" && exit 1; sleep 60; done
[ -s "$O/mixed_b2e_koh3_first.jsonl" ] && exit 0
s=$(date +%s)
( cd "$R/engine" && RAYON_NUM_THREADS=12 nice -n 12 "$SCAN" --pairs "$B2E" --root "$R" --seed-base 21106000000 \
    --pairings "$(seq -s, 0 95)" --games 500 --bot-a koh3 --bot-b kog3 --games-out "$O/mixed_b2e_koh3_first.jsonl.part" ) \
    > "$O/mixed_b2e_koh3_first.txt" 2>&1 || { note "FAILED: mixed_b2e_koh3_first"; exit 1; }
mv "$O/mixed_b2e_koh3_first.jsonl.part" "$O/mixed_b2e_koh3_first.jsonl"
echo "$(date -u +%F\ %T) KOH B2E MIXED DONE in $(( $(date +%s) - s )) s ($(wc -l < "$O/mixed_b2e_koh3_first.jsonl") games)" >> "$O/STATUS.txt"
