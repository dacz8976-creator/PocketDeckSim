#!/usr/bin/env bash
# km's identity checks at build B, km on kta (the km registration, section 4.1, as Amendment 1 (c) item 4 re-bases it;
# Cloud Opus's round, Dustin's Sept 30 assignment). Usage: bash run_km.sh <B's short commit>. Plays through B's own
# scan program, copied to scratch and named with the commit; each step writes to scratch and moves here when complete;
# STATUS.txt logs each step. Any identity failure or scan failure stops the run. No registered km game, no threshold
# sample and no reading: item 7's km3 smoke is checked for a clean, complete run only, and item 5's km3 games only for
# equality with kta3's.
set -euo pipefail
BUILD=$1
R=/home/user/PocketDeckSim; D=$R/rl/results/km_build_2026-09-30
S=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/km
SCAN=$S/binB/scan_$BUILD; W=$S/outB; T=${THREADS:-4}
TSV=$R/rl/results/gauntlet_runs_2026-09-26/tsv; B2E=$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
REF=$R/rl/results; KTA=$REF/kt_tables_2026-09-28; I=$D/identity
mkdir -p "$W" "$I"
note() { echo "$(date -u +%FT%TZ) $*" >> "$D/STATUS.txt"; }
die() { note "BLOCKED: $*"; exit 1; }

# Item 8: the diff of engine/ from ec7e1a8 touches engine/src/players/ only, engine/UPSTREAM.md aside.
outside=$(git -C "$R" diff --name-only ec7e1a8 "$BUILD" -- engine/ ':!engine/UPSTREAM.md' | grep -v '^engine/src/players/' || true)
[ -z "$outside" ] || die "item 8: the build touches engine/ outside players/: $outside"
note "identity start: build $BUILD; scan sha256 $(sha256sum "$SCAN" | cut -c1-64); item 8: engine/ diff from ec7e1a8 (UPSTREAM.md aside) is players/ only ($(git -C "$R" diff --name-only ec7e1a8 "$BUILD" -- engine/ ':!engine/UPSTREAM.md' | paste -sd' '))"

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

# Item 6: kta3 at B on pairings 0 and 2, 40 deals, against kta3's table file. Item 7: km3's smoke on pairings 0, 2
# and 19, 40 deals, clean and complete (the laptop's reference).
scan ${BUILD}_kta3_p02_40 40 kta3 kta3 "${TABLE[@]}" --pairings 0,2
ident "item 6: kta3 at B, pairings 0 and 2, 40 deals, v ec7e1a8_kta3_table" ${BUILD}_kta3_p02_40 "$KTA/ec7e1a8_kta3_table.jsonl" 40 --pairings 0,2
scan ${BUILD}_km3_smoke_40 40 km3 km3 "${TABLE[@]}" --pairings 0,2,19
ident "item 7: km3 smoke, pairings 0, 2 and 19, 40 deals" ${BUILD}_km3_smoke_40 --clean-only 40 --pairings 0,2,19
note "item 7's smoke file: identity/${BUILD}_km3_smoke_40.jsonl sha256 $(sha256sum "$I/${BUILD}_km3_smoke_40.jsonl" | cut -c1-64)"

# Item 5: km3 on the 28 cells holding neither the panel Altaria nor the panel Lucario list, against kta3's files.
T15=7,9,10,11,12,14,15,16,17,22,23,24,25,26,27; N13=10,11,12,13,14,15,18,19,20,21,22,23,24
scan ${BUILD}_km3_table15_500 500 km3 km3 "${TABLE[@]}" --pairings $T15
ident "item 5: km3 on the 15 table cells without Altaria or Lucario, 500 deals, v ec7e1a8_kta3_table" ${BUILD}_km3_table15_500 "$KTA/ec7e1a8_kta3_table.jsonl" 500 --pairings $T15
scan ${BUILD}_km3_new13_500 500 km3 km3 --pairs "$TSV/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings $N13
ident "item 5: km3 on the 13 new cells without Altaria or Lucario, 500 deals, v ec7e1a8_kta3_new17" ${BUILD}_km3_new13_500 "$KTA/ec7e1a8_kta3_new17.jsonl" 500 --pairings $N13

# Item 1: kta3 in full (the files the reading pairs km3 against), then k3, kp3 and kog3 in full, and kog3 on the new cells.
scan ${BUILD}_kta3_500 500 kta3 kta3 "${TABLE[@]}"
ident "item 1: kta3, 500 table deals, v ec7e1a8_kta3_table" ${BUILD}_kta3_500 "$KTA/ec7e1a8_kta3_table.jsonl" 500
scan ${BUILD}_new17_kta3_500 500 kta3 kta3 "${NEW17[@]}"
ident "item 1: kta3, the 17 new cells, 500 deals, v ec7e1a8_kta3_new17" ${BUILD}_new17_kta3_500 "$KTA/ec7e1a8_kta3_new17.jsonl" 500
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

# Item 3: the coverage baselines at i < 40 of every pairing, kta3's (re-based) and kog3's (kept).
for code in kta3 kog3; do
  if [ $code = kta3 ]; then
    b2e_ref=$KTA/ec7e1a8_b2e_kta3.jsonl; scizor_ref=$KTA/ec7e1a8_scizor_kta3.jsonl; var_ref() { echo "$KTA/ec7e1a8_var_$1_kta3.jsonl"; }
  else
    b2e_ref=$REF/koh_2026-09-28/reading/b2e_kog3.jsonl; scizor_ref=$REF/koh_2026-09-28/laptop_runs/scizor_kog3.jsonl
    var_ref() { echo "$REF/koh_2026-09-28/laptop_runs/var_$1_kog3.jsonl"; }
  fi
  scan ${BUILD}_b2e_${code}_40 40 $code $code --pairs "$B2E" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 0 95)"
  ident "item 3: $code, B2e's 96 pairings i < 40, v $(basename "$b2e_ref")" ${BUILD}_b2e_${code}_40 "$b2e_ref" 40
  scan ${BUILD}_scizor_${code}_40 40 $code $code --pairs "$TSV/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)"
  ident "item 3: $code, Scizor's 8 pairings i < 40, v $(basename "$scizor_ref")" ${BUILD}_scizor_${code}_40 "$scizor_ref" 40
  for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
    [[ $v == *charizardy* ]] && base=21106000000 || base=72000000
    scan ${BUILD}_var_${v}_${code}_40 40 $code $code --pairs "$TSV/var_$v.tsv" --root "$R" --seed-base $base
    ident "item 3: $code, second list $v i < 40, v $(basename "$(var_ref $v)")" ${BUILD}_var_${v}_${code}_40 "$(var_ref $v)" 40
  done
done
note "IDENTITY DONE (items 1-3 and 5-8; item 4 is a test; item 8a is the counter tool's check)"
