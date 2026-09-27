#!/usr/bin/env bash
# koa's reading runs (REGISTRATION.md section 7, rl/results/opening_active_census_2026-09-26/), on the official engine
# (rl/engine-2026-09-27/legality_scan, main-83e17ae, which contains koa's code). The cloud's identity checks passed at
# 9af40c8 (../identity_check.txt); the official build equals 9bffbda's engine/. kp3's references at this engine are kpf's
# reading runs (../../kpf_2026-09-26/reading/table_kp3.jsonl, b2e_kp3.jsonl), which the official build replays.
# Order (the footprint is read first; the route is fixed by it before anything else is read):
#   table_koa3            : koa3 on both sides, the table's 14,000 deals
#   mixed_{koa3,kob3,kor3}_{first,second} : Altaria's 7 pairings (0-6), the candidate or a diagnostic on Altaria only
#                           (first) or on its opponents only (second), kp3 on the other side
#   b2e_koa3              : B2e's 48 archetype pairings (0-47), koa3 on both sides
# Not run: the variant-list check (section 7 (d)); its row against the table's own Altaria list needs a seed block the
# registration never wrote down.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koa_2026-09-26/reading"
SCAN="$R/rl/engine-2026-09-27/legality_scan"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
[ "$(sha256sum "$SCAN" | cut -c1-64)" = "$(python3 -c "import json; print(json.load(open('$R/project_manifest.json'))['available_release']['legality_scan_sha256'])")" ] \
  || { note "FAILED: the scan is not the official one"; exit 1; }
cd "$R/engine"
run() {  # name args...
  local name=$1; shift
  [ ! -s "$O/$name.jsonl" ] || { note "$name exists, skipped"; return; }
  local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --games-out "$O/$name.jsonl.part" > "$O/$name.txt" 2>&1 \
    || { note "FAILED: $name"; exit 1; }
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
run table_koa3 --decks ../decks/research --bot koa3
echo "$(date -u +%F\ %T) KOA TABLE DONE" >> "$O/STATUS.txt"
A=$(seq -s, 0 6)
for b in koa3 kob3 kor3; do
  run mixed_${b}_first --decks ../decks/research --pairings "$A" --bot-a $b --bot-b kp3
  run mixed_${b}_second --decks ../decks/research --pairings "$A" --bot-a kp3 --bot-b $b
done
run b2e_koa3 --pairs "$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 0 47)" --bot koa3
echo "$(date -u +%F\ %T) KOA RUNS DONE" >> "$O/STATUS.txt"
