#!/usr/bin/env bash
# kt on kog, Sept 28-29 night (Dustin's GO via Fable; README.md is the plan, committed before any kt game).
# Build ec7e1a8 (233bced + kt's presets on kog). Every step writes to scratch and moves into this folder when complete;
# STATUS.txt logs each step. Any identity failure, timing over 1.25x, or scan failure stops the run.
set -euo pipefail
R=/home/user/PocketDeckSim; D=$R/rl/results/kt_kog_2026-09-28; BUILD=ec7e1a8
S=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/ktkog
SCAN=$S/scan_$BUILD; W=$S/out; T=${THREADS:-4}
NEW=$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv; B2E=$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
REF=$R/rl/results
mkdir -p "$W" "$D/identity"
note() { echo "$(date -u +%FT%TZ) $*" >> "$D/STATUS.txt"; }
die() { note "BLOCKED: $*"; exit 1; }
[ "$(git -C "$R" diff --name-only 233bced "$BUILD" -- engine/ | grep -v '^engine/src/players/' | wc -l)" = 0 ] \
  || die "the build touches engine/ outside players/"
note "start: build $BUILD; scan sha256 $(sha256sum "$SCAN" | cut -c1-64); deckgym sha256 $(sha256sum "$S/deckgym_$BUILD" | cut -c1-64); engine/ diff from 233bced: players/ only"

TABLE=(--decks ../decks/research)
NEW17=(--pairs "$NEW" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
B2E96=(--pairs "$B2E" --seed-base 21106000000 --pairings "$(seq -s, 0 95)")
scan() {  # dest name games bot-a bot-b args...
  local dest=$1 name=$2 n=$3 ba=$4 bb=$5; shift 5
  if [ -s "$dest/$name.jsonl" ]; then note "$name exists, skipped"; return; fi
  local s=$(date +%s)
  ( cd "$R/engine" && RAYON_NUM_THREADS=$T "$SCAN" "$@" --games "$n" --bot-a "$ba" --bot-b "$bb" \
      --games-out "$W/$name.jsonl" > "$W/$name.txt" 2>&1 ) || die "scan $name"
  mv "$W/$name.jsonl" "$W/$name.txt" "$dest/"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$dest/$name.jsonl") games)"
}
ident() {  # label name reference deals
  python3 "$D/identity.py" "$1" "$D/identity/$2.jsonl" "$3" "$4" > /dev/null || die "IDENTITY FAILED: $1 (identity/identity_check.txt)"
  note "identity: $(tail -1 "$D/identity/identity_check.txt")"
}

# 1. The full suite.
if [ ! -s "$D/suite.log" ]; then
  s=$(date +%s)
  ( cd "$R/engine" && cargo test --release --features test-utils > "$S/suite.log" 2>&1 ) || { cp "$S/suite.log" "$D/"; die "suite (suite.log)"; }
  cp "$S/suite.log" "$D/"
  note "suite: $(grep -E '^test result' "$D/suite.log" | awk '{p+=$4; f+=$6} END {print p" passed, "f" failed"}') in $(( $(date +%s) - s )) s"
fi

# 2. Identity at the build.
I=$D/identity
scan "$I" ${BUILD}_k3_500 500 k3 k3 "${TABLE[@]}";          ident "k3, 500 table deals, v the pin's frozen table" ${BUILD}_k3_500 "$REF/engine_switch_2026-09-28/pin_identity_k3_500.jsonl" 500
scan "$I" ${BUILD}_kp3_500 500 kp3 kp3 "${TABLE[@]}";       ident "kp3, 500 table deals, v the pin's frozen table" ${BUILD}_kp3_500 "$REF/engine_switch_2026-09-28/pin_identity_kp3_500.jsonl" 500
scan "$I" ${BUILD}_kog3_500 500 kog3 kog3 "${TABLE[@]}";    ident "kog3, 500 table deals, v a823b6d_kog3_500" ${BUILD}_kog3_500 "$REF/kog_2026-09-27/a823b6d_kog3_500.jsonl" 500
scan "$I" ${BUILD}_new17_kog3_500 500 kog3 kog3 "${NEW17[@]}"; ident "kog3, the 17 new cells, v new17_kog3" ${BUILD}_new17_kog3_500 "$REF/kog_composition_2026-09-27/new17_kog3.jsonl" 500
scan "$I" ${BUILD}_b2e_kog3_40 40 kog3 kog3 "${B2E96[@]}";  ident "kog3, B2e's 96 pairings i < 40, v koh's b2e_kog3" ${BUILD}_b2e_kog3_40 "$REF/koh_2026-09-28/reading/b2e_kog3.jsonl" 40
scan "$I" ${BUILD}_kq3_500 500 kq3 kq3 "${TABLE[@]}";       ident "kq3, 500 table deals, v official_kq3_500" ${BUILD}_kq3_500 "$REF/kt_2026-09-26/identity/official_kq3_500.jsonl" 500
scan "$I" ${BUILD}_kd3_40 40 kd3 kd3 "${TABLE[@]}";         ident "kd3, 40 table deals, v af8489f_kd3_40" ${BUILD}_kd3_40 "$REF/rules09_fixes_2026-09-26/af8489f_kd3_40.jsonl" 40
scan "$I" ${BUILD}_kpr3_40 40 kpr3 kpr3 "${TABLE[@]}";      ident "kpr3, 40 table deals, v af8489f_kpr3_40" ${BUILD}_kpr3_40 "$REF/rules09_fixes_2026-09-26/af8489f_kpr3_40.jsonl" 40
note "IDENTITY DONE"

# 3. Timing: kog3 then kt3 on the first 40 table deals, back to back.
if [ ! -s "$D/timing.txt" ]; then
  for b in kog3 kt3; do
    s=$(date +%s.%N)
    ( cd "$R/engine" && RAYON_NUM_THREADS=$T "$SCAN" "${TABLE[@]}" --games 40 --bot $b > "$S/timing_$b.txt" 2>&1 ) || die "timing $b"
    echo "$b $(echo "$(date +%s.%N) - $s" | bc)" >> "$S/timing_raw.txt"
  done
  python3 - "$S/timing_raw.txt" > "$D/timing.txt" <<'EOF' || die "TIMING: kt3 over 1.25x kog3 (timing.txt)"
import sys
t = dict((b, float(x)) for b, x in (l.split() for l in open(sys.argv[1])))
r = t["kt3"] / t["kog3"]
print(f"40 table deals per pairing (1,120 games), 4 threads, back to back: kog3 {t['kog3']:.0f} s, kt3 {t['kt3']:.0f} s; "
      f"kt3 / kog3 = {r:.2f} (the bound is 1.25): {'within' if r <= 1.25 else 'OVER'}")
sys.exit(0 if r <= 1.25 else 1)
EOF
  note "timing: $(cat "$D/timing.txt")"
fi

# 4. The four tables on the 45 cells.
for code in kt3 kta3 ktb3 ktc3; do
  scan "$D" ${BUILD}_table_${code}_500 500 $code $code "${TABLE[@]}"
  scan "$D" ${BUILD}_new17_${code}_500 500 $code $code "${NEW17[@]}"
done
note "TABLES DONE"

# 5. The footprint (moves only), read first; committed alone by hand.
[ -s "$D/footprint.txt" ] || python3 "$D/footprint.py" > "$D/footprint.txt" || die "footprint"
note "FOOTPRINT WRITTEN (commit it alone before anything else is read)"

# 6. Mixed rows against kog3 on the 45 cells: kt3, then kta3.
for code in kt3 kta3; do
  scan "$D" ${BUILD}_mixed_table_${code}_first 500 $code kog3 "${TABLE[@]}"
  scan "$D" ${BUILD}_mixed_table_${code}_second 500 kog3 $code "${TABLE[@]}"
  scan "$D" ${BUILD}_mixed_new17_${code}_first 500 $code kog3 "${NEW17[@]}"
  scan "$D" ${BUILD}_mixed_new17_${code}_second 500 kog3 $code "${NEW17[@]}"
  note "MIXED DONE $code"
done
note "KT RUN DONE"
