#!/usr/bin/env bash
# koh's remaining reading runs, moved from the cloud to the laptop (Dustin, Sept 28 evening: the laptop is free and
# runs 14 threads; the cloud finishes b2e_koh3 and stops). All at the official engine rl/engine-2026-09-28 (main-9b4df9b,
# built from 233bced, whose engine/ equals koh's build bd2907f), hash-checked against project_manifest.json.
# kph's registration section 5 step 6 and amendment 2 (no harm on the coverage rows):
#   - the Scizor row: koh3 and kog3 on both sides, and the mixed rows (koh3 on Scizor v kog3 on the panel list, the
#     gating direction; and koh3 on the panel list v kog3 on Scizor, reported only). new_decks.tsv pairings 0-7,
#     seed base 21,108,000,000.
#   - the four second lists (the variation check's own TSVs and deals: the table decks' at 72,000,000, Charizard Y's
#     at 21,106,000,000): koh3 and kog3 on both sides, and mixed rows with koh3 on the list's side (the TSV's
#     variant_side column) and kog3 on the other deck.
#   - the Rayquaza pre-set check with per-game rows (section 5 step 4's paired intervals): trace_pilot.py --per-game
#     on the same 200 deals (21,108,900,000+), koh3 and kpf3 on Rayquaza, kp3 on Lucario.
# No new seeds: every deal is one already played. Writes here only; STATUS.txt's last line is anchored.
# Usage (WSL): nohup setsid bash run_koh_laptop.sh > run.log 2>&1 &
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koh_2026-09-28/laptop_runs"
T="$R/rl/results/gauntlet_runs_2026-09-26/tsv"; SCAN="$R/rl/engine-2026-09-28/legality_scan"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; exit 1; }
until grep -q 'FLOOR RECHECK DONE' "$R/rl/results/floor_recheck_2026-09-28/timing.txt" 2>/dev/null; do sleep 60; done
grep -q "$(sha256sum "$SCAN" | cut -c1-64)" "$R/project_manifest.json" || die "the scan's hash is not the manifest's"
note "start at the official engine; scan $(sha256sum "$SCAN" | cut -c1-16)"
run() {  # name args...
  local name=$1; shift
  [ -s "$O/$name.jsonl" ] && return
  local s=$(date +%s)
  ( cd "$R/engine" && RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt" 2>&1 \
    || die "$name scan"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
SP=(--pairs "$T/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)")
run scizor_koh3 "${SP[@]}" --bot koh3
run scizor_kog3 "${SP[@]}" --bot kog3
run mixed_scizor_koh3_first "${SP[@]}" --bot-a koh3 --bot-b kog3
run mixed_scizor_koh3_second "${SP[@]}" --bot-a kog3 --bot-b koh3
for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
  [[ $v == *charizardy* ]] && base=21106000000 || base=72000000
  f="$T/var_$v.tsv"
  side_a=$(awk -F'\t' 'NR > 1 && $12 == "a" {print $1}' "$f" | paste -sd,)
  side_b=$(awk -F'\t' 'NR > 1 && $12 == "b" {print $1}' "$f" | paste -sd,)
  VP=(--pairs "$f" --root "$R" --seed-base $base)
  run var_${v}_koh3 "${VP[@]}" --bot koh3
  run var_${v}_kog3 "${VP[@]}" --bot kog3
  [ -z "$side_a" ] || run var_${v}_mixed_a "${VP[@]}" --pairings "$side_a" --bot-a koh3 --bot-b kog3
  [ -z "$side_b" ] || run var_${v}_mixed_b "${VP[@]}" --pairings "$side_b" --bot-a kog3 --bot-b koh3
  note "$v: list on side a in pairings [$side_a], side b in [$side_b]"
done
cd "$R"
for p in koh3 kpf3; do
  [ -s "$O/trace_rayquaza_v_lucario_${p}_pergame.jsonl" ] && continue
  nice -n 10 python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt \
    decks/screen/opponents/t-lucario.txt --games 200 --pilot $p --opp-pilot kp3 \
    --per-game "$O/trace_rayquaza_v_lucario_${p}_pergame.jsonl" > "$O/trace_rayquaza_v_lucario_${p}.txt" 2>&1 || die "trace $p"
  note "trace $p done"
done
echo "$(date -u +%F\ %T) KOH LAPTOP RUNS DONE" >> "$O/STATUS.txt"
