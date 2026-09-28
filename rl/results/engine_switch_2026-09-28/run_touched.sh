#!/usr/bin/env bash
# The touched-path check (Dustin, Sept 28: "the check has to be where the change is"). Waits for the pin's build and
# the watch build, then, on the old official build (rl/engine-2026-09-27, main-83e17ae) and the new build (233bced):
#   1. same-seed legality_scan games of the carrier lists against the 8 panel lists (touched.tsv): deck 07 (Barrier,
#      Jasmine), deck 05 (Cheren), the upstream metal-barrier example (Barrier, Adaman), a 2-Blue test list (Blue);
#      kp3 at 500 deals on old, new and the watch build (reach counts), k3 at 250 on old and new;
#   2. the Scizor coverage row (Barrier) replayed on the new build and the watch build against its recorded files
#      (made on an engine tree identical to 83e17ae), k3 and kp3;
#   3. Dustin's recorded Skarmory commands on both builds: the floor check's block and the largest Jasmine block
#      (jasmine_altskeptic/count.py, per-game move hashes), 1,920 games each.
# Then compare_touched.py. Seeds for part 1: 22,801,000,000 + pairing x 10,000 + i (START_HERE).
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-28"
C=233bced; NB=/home/dacz8976/engine-official-$C/engine/target/release; W=/home/dacz8976/engine-watch-$C/engine/target/release
OLD_SCAN="$R/rl/engine-2026-09-27/legality_scan"; OLD_GYM="$R/rl/engine-2026-09-27/deckgym"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/PIN_STATUS.txt"; }
until grep -q 'PREPARE DONE' "$O/PIN_STATUS.txt" 2>/dev/null && grep -q 'watch build of' "$O/PIN_STATUS.txt"; do
  grep -q 'FAILED' "$O/PIN_STATUS.txt" 2>/dev/null && { echo "a FAILED line; touched runs not started"; exit 1; }; sleep 60; done
mkdir -p "$O/touched"; T="$O/touched"
H=$'pairing\tblock\theld_key\theld_file\topponent\tpanel_file\tseed_first\tseed_last\tsub_block_end'
{ echo "$H"; p=0
  for spec in "deck07:decks/dustin/07-skarmory-stall.txt" "deck05:decks/dustin/05-indeedee-stoutland.txt" \
              "metalbarrier:engine/example_decks/metal-barrier.txt" "bluetest:rl/results/engine_switch_2026-09-28/lists/blue_test.txt"; do
    key=${spec%%:*}; file=${spec#*:}
    for opp in altaria blaziken hydreigon lucario sceptile suicune vespiquen weezing; do
      s=$((22801000000 + 10000 * p)); printf '%s\ttouched\t%s\t%s\t%s\tdecks/screen/opponents/t-%s.txt\t%s\t%s\t%s\n' $p $key "$file" $opp $opp $s $((s + 499)) $((s + 9999)); p=$((p + 1))
    done
  done; } > "$T/touched.tsv"
scan() {  # name binary bot games args...
  local name=$1 bin=$2 bot=$3 n=$4; shift 4
  [ -s "$T/$name.jsonl" ] && return
  ( cd "$R/engine" && RAYON_NUM_THREADS=14 nice -n 10 "$bin" "$@" --games $n --bot $bot --games-out "$T/$name.jsonl.part" ) > "$T/$name.txt" 2>&1 \
    || { note "FAILED: touched $name"; exit 1; }
  mv "$T/$name.jsonl.part" "$T/$name.jsonl"; note "touched $name done ($(wc -l < "$T/$name.jsonl") games)"
}
TP=(--pairs "$T/touched.tsv" --root "$R" --seed-base 22801000000 --pairings "$(seq -s, 0 31)")
scan carriers_kp3_old "$OLD_SCAN" kp3 500 "${TP[@]}"
scan carriers_kp3_new "$NB/examples/legality_scan" kp3 500 "${TP[@]}"
scan carriers_kp3_watch "$W/examples/legality_scan" kp3 500 "${TP[@]}"
scan carriers_k3_old "$OLD_SCAN" k3 250 "${TP[@]}"
scan carriers_k3_new "$NB/examples/legality_scan" k3 250 "${TP[@]}"
SP=(--pairs "$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)")
scan scizor_kp3_new "$NB/examples/legality_scan" kp3 500 "${SP[@]}"
scan scizor_k3_new "$NB/examples/legality_scan" k3 500 "${SP[@]}"
scan scizor_kp3_watch "$W/examples/legality_scan" kp3 500 "${SP[@]}"
for spec in floor:7100 alt:21102860000; do
  lab=${spec%%:*}; seed=${spec#*:}
  for side in old new; do
    [ $side = old ] && gym="$OLD_GYM" || gym="$NB/deckgym"
    f=/home/dacz8976/jasmine_altskeptic/summary_pin28_${lab}_${side}.json
    [ -s "$f" ] || { ( cd "$R" && nice -n 10 python3 /home/dacz8976/jasmine_altskeptic/count.py pin28_${lab}_${side} "$gym" --games 120 --base-seed $seed ) \
      > "$T/count_${lab}_${side}.log" 2>&1 || { note "FAILED: count.py $lab $side"; exit 1; }; }
    cp "$f" "$T/"; note "count.py $lab $side done"
  done
done
python3 "$O/compare_touched.py" > "$O/touched_check.txt" 2>&1 || { note "FAILED: compare_touched (touched_check.txt)"; exit 1; }
echo "$(date -u +%F\ %T) TOUCHED DONE" >> "$O/PIN_STATUS.txt"
