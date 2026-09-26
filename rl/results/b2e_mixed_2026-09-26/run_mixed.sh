#!/usr/bin/env bash
# Descriptive attribution for B2e (Fable's suggestion, Sept 26 morning): kp3-against-k3 mixed rows on the Manectric
# (pairings 0-7) and Raticate (8-15) archetype pairings, both directions, on the SAME B2e deals (seed 21,106,000,000
# + 10,000 x pairing + i, i < 500; no new seeds), same binary as B2e's rows (identity PASS 45ecfda4...).
#   first:  kp3 pilots the held archetype deck, k3 its panel opponent
#   second: k3 pilots the held deck, kp3 the panel opponent
# Read against b2e_k3_arch.jsonl (k3|k3) and b2e_kp3_arch.jsonl (kp3|kp3) by read_mixed.py. Attribution only.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/b2e_mixed_2026-09-26"
E="$R/rl/results/b2e_rows_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
TSV=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ "$(tail -n 1 "$E/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] || { echo "no identity PASS for $SHA"; exit 1; }
if pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null || pgrep -x 'legality_scan.*' >/dev/null || pgrep -x 'deckgym.*' >/dev/null; then echo "not idle"; exit 1; fi
echo "scan binary $SHA" > "$D/identity.txt"
THREADS=$(( $(nproc) - 2 ))
PAIRINGS=$(seq -s, 0 15)
cd "$B/engine"
for dir in first second; do
  if [ $dir = first ]; then A=kp3; Bb=k3; else A=k3; Bb=kp3; fi
  s=$(date +%s)
  RAYON_NUM_THREADS=$THREADS nice -n 10 "$SCAN" --pairs "$B/$TSV" --seed-base 21106000000 --games 500 \
    --bot-a "$A" --bot-b "$Bb" --pairings "$PAIRINGS" --games-out "$D/mixed_$dir.jsonl.part" > "$D/mixed_$dir.txt" 2>&1
  mv "$D/mixed_$dir.jsonl.part" "$D/mixed_$dir.jsonl"
  echo "mixed_$dir (bot_a $A, bot_b $Bb) $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
python3 "$D/read_mixed.py" > "$D/mixed_reading.txt"
echo done >> "$D/timing.txt"
