#!/usr/bin/env bash
# koh's B2e held-out rows on the laptop (Fable's overnight ruling, Sept 28: don't let the cloud's queue block kt's first
# game, which waits on this read). koh3 on both sides of B2e's 96 pairings x 500, seed base 21,106,000,000, at the
# official engine (233bced, whose engine/ equals koh's build bd2907f): the same rows the cloud is also running. If the
# cloud's b2e_koh3 lands too, the two must be identical game for game (a cross-check), and either serves the reading.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koh_2026-09-28/laptop_runs"
SCAN="$R/rl/engine-2026-09-28/legality_scan"; B2E="$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
grep -q "$(sha256sum "$SCAN" | cut -c1-64)" "$R/project_manifest.json" || { note "FAILED: b2e scan hash"; exit 1; }
[ -s "$O/b2e_koh3.jsonl" ] && exit 0
s=$(date +%s)
( cd "$R/engine" && RAYON_NUM_THREADS=12 nice -n 10 "$SCAN" --pairs "$B2E" --root "$R" --seed-base 21106000000 \
    --pairings "$(seq -s, 0 95)" --games 500 --bot koh3 --games-out "$O/b2e_koh3.jsonl.part" ) > "$O/b2e_koh3.txt" 2>&1 \
  || { note "FAILED: b2e_koh3 scan"; exit 1; }
mv "$O/b2e_koh3.jsonl.part" "$O/b2e_koh3.jsonl"
echo "$(date -u +%F\ %T) KOH B2E DONE in $(( $(date +%s) - s )) s ($(wc -l < "$O/b2e_koh3.jsonl") games)" >> "$O/STATUS.txt"
