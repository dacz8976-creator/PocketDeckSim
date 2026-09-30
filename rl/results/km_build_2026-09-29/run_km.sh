#!/usr/bin/env bash
# km's identity checks at its build (the km registration, section 4.1, items 1 to 3 and 5 to 8; Cloud Opus's round).
# Usage: bash run_km.sh <build commit>. Plays through the build's own scan program, copied to scratch and named with
# the commit; each step writes to scratch and moves here when complete; STATUS.txt logs each step. Any identity
# failure or scan failure stops the run. No registered km game, no threshold sample and no reading: item 7's km3 smoke
# is checked for a clean, complete run only, and item 5's km3 games only for equality with kog3's.
set -euo pipefail
BUILD=$1
R=/home/user/PocketDeckSim; D=$R/rl/results/km_build_2026-09-29
S=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/km
SCAN=$S/bin/scan_$BUILD; W=$S/out; T=${THREADS:-4}
TSV=$R/rl/results/gauntlet_runs_2026-09-26/tsv; B2E=$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
REF=$R/rl/results; I=$D/identity
mkdir -p "$W" "$I"
note() { echo "$(date -u +%FT%TZ) $*" >> "$D/STATUS.txt"; }
die() { note "BLOCKED: $*"; exit 1; }

# Item 8: the diff of engine/ from 233bced touches engine/src/players/ only.
outside=$(git -C "$R" diff --name-only 233bced "$BUILD" -- engine/ | grep -v '^engine/src/players/' || true)
[ -z "$outside" ] || die "item 8: the build touches engine/ outside players/: $outside"
note "identity start: build $BUILD; scan sha256 $(sha256sum "$SCAN" | cut -c1-64); item 8: engine/ diff from 233bced is players/ only ($(git -C "$R" diff --name-only 233bced "$BUILD" -- engine/ | paste -sd' '))"

TABLE=(--decks ../decks/research)
NEW17=(--pairs "$TSV/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
scan() {  # name games bot-a bot-b args...
  local name=$1 n=$2 ba=$3 bb=$4; shift 4
  if [ -s "$I/$name.jsonl" ]; then note "$name exists, skipped"; return; fi
  local s=$(date +%s)
  ( cd "$R/engine" && RAYON_NUM_THREADS=$T "$SCAN" "$@" --games "$n" --bot-a "$ba" --bot-b "$bb" \
      --games-out "$W/$name.jsonl" > "$W/$name.txt" 2>&1 ) || die "scan $name"
  mv "$W/$name.jsonl" "$W/$name.txt" "$I/"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$I/$name.jsonl") games)"
}
ident() {  # label name reference deals [--pairings list]
  local label=$1 name=$2; shift 2
  python3 "$D/identity.py" "$label" "$I/$name.jsonl" "$@" > /dev/null || die "IDENTITY FAILED: $label (identity/identity_check.txt)"
  note "identity: $(tail -1 "$I/identity_check.txt")"
}

# Items 6 and 7 (pairings 0 and 2, 40 deals): kog3 at the build against the table file; km3's smoke, clean and complete.
scan ${BUILD}_kog3_p02_40 40 kog3 kog3 "${TABLE[@]}" --pairings 0,2
ident "item 6: kog3 at the km build, pairings 0 and 2, 40 deals, v table_kog3" ${BUILD}_kog3_p02_40 "$REF/kog_composition_2026-09-27/table_kog3.jsonl" 40 --pairings 0,2
scan ${BUILD}_km3_p02_40 40 km3 km3 "${TABLE[@]}" --pairings 0,2
ident "item 7: km3 smoke, pairings 0 and 2, 40 deals" ${BUILD}_km3_p02_40 --clean-only 40 --pairings 0,2

# Item 5: km3 on the 28 cells holding neither the panel Altaria nor the panel Lucario list, against kog3's files.
T15=7,9,10,11,12,14,15,16,17,22,23,24,25,26,27; N13=10,11,12,13,14,15,18,19,20,21,22,23,24
scan ${BUILD}_km3_table15_500 500 km3 km3 "${TABLE[@]}" --pairings $T15
ident "item 5: km3 on the 15 table cells without Altaria or Lucario, 500 deals, v table_kog3" ${BUILD}_km3_table15_500 "$REF/kog_composition_2026-09-27/table_kog3.jsonl" 500 --pairings $T15
scan ${BUILD}_km3_new13_500 500 km3 km3 --pairs "$TSV/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings $N13
ident "item 5: km3 on the 13 new cells without Altaria or Lucario, 500 deals, v new17_kog3" ${BUILD}_km3_new13_500 "$REF/kog_composition_2026-09-27/new17_kog3.jsonl" 500 --pairings $N13

# Item 1: k3, kp3 and kog3 in full; kog3 on the 17 new cells.
scan ${BUILD}_k3_500 500 k3 k3 "${TABLE[@]}"
ident "item 1: k3, 500 table deals, v the pin's frozen table" ${BUILD}_k3_500 "$REF/engine_switch_2026-09-28/pin_identity_k3_500.jsonl" 500
scan ${BUILD}_kp3_500 500 kp3 kp3 "${TABLE[@]}"
ident "item 1: kp3, 500 table deals, v the pin's frozen table" ${BUILD}_kp3_500 "$REF/engine_switch_2026-09-28/pin_identity_kp3_500.jsonl" 500
scan ${BUILD}_kog3_500 500 kog3 kog3 "${TABLE[@]}"
ident "item 1: kog3, 500 table deals, v bd2907f_kog3_500" ${BUILD}_kog3_500 "$REF/koh_2026-09-28/bd2907f_kog3_500.jsonl" 500
ident "item 1: kog3, 500 table deals, v table_kog3" ${BUILD}_kog3_500 "$REF/kog_composition_2026-09-27/table_kog3.jsonl" 500
scan ${BUILD}_new17_kog3_500 500 kog3 kog3 "${NEW17[@]}"
ident "item 1: kog3, the 17 new cells, 500 deals, v new17_kog3" ${BUILD}_new17_kog3_500 "$REF/kog_composition_2026-09-27/new17_kog3.jsonl" 500

# Item 2: kq3 in full; kd3 and kpr3 at 40 deals.
scan ${BUILD}_kq3_500 500 kq3 kq3 "${TABLE[@]}"
ident "item 2: kq3, 500 table deals, v official_kq3_500" ${BUILD}_kq3_500 "$REF/kt_2026-09-26/identity/official_kq3_500.jsonl" 500
scan ${BUILD}_kd3_40 40 kd3 kd3 "${TABLE[@]}"
ident "item 2: kd3, 40 table deals, v af8489f_kd3_40" ${BUILD}_kd3_40 "$REF/rules09_fixes_2026-09-26/af8489f_kd3_40.jsonl" 40
scan ${BUILD}_kpr3_40 40 kpr3 kpr3 "${TABLE[@]}"
ident "item 2: kpr3, 40 table deals, v af8489f_kpr3_40" ${BUILD}_kpr3_40 "$REF/rules09_fixes_2026-09-26/af8489f_kpr3_40.jsonl" 40

# Item 3: the kog3 coverage baselines at i < 40 of every pairing (B2e, Scizor, the four second lists).
scan ${BUILD}_b2e_kog3_40 40 kog3 kog3 --pairs "$B2E" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 0 95)"
ident "item 3: kog3, B2e's 96 pairings i < 40, v koh's reading/b2e_kog3" ${BUILD}_b2e_kog3_40 "$REF/koh_2026-09-28/reading/b2e_kog3.jsonl" 40
scan ${BUILD}_scizor_kog3_40 40 kog3 kog3 --pairs "$TSV/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)"
ident "item 3: kog3, Scizor's 8 pairings i < 40, v laptop_runs/scizor_kog3" ${BUILD}_scizor_kog3_40 "$REF/koh_2026-09-28/laptop_runs/scizor_kog3.jsonl" 40
for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
  [[ $v == *charizardy* ]] && base=21106000000 || base=72000000
  scan ${BUILD}_var_${v}_kog3_40 40 kog3 kog3 --pairs "$TSV/var_$v.tsv" --root "$R" --seed-base $base
  ident "item 3: kog3, second list $v i < 40, v laptop_runs/var_${v}_kog3" ${BUILD}_var_${v}_kog3_40 "$REF/koh_2026-09-28/laptop_runs/var_${v}_kog3.jsonl" 40
done
note "IDENTITY DONE (items 1-3 and 5-8; item 4 is a test; item 8a is the counter tool's check)"
