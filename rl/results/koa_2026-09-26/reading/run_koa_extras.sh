#!/usr/bin/env bash
# koa's reported-beside runs (registration amendments 1 and 2; the second reader's items 3-5), at the official engine,
# after the diagnostic rows (anchored wait):
#   new17_koa3              : koa3 on both sides of the 17 new scoreboard cells (gauntlet new_decks.tsv pairings 8-24)
#   b2e_dustin_koa3         : koa3 on B2e's pairings 48-95 (Dustin's files), beside kpf's kp3 rows
#   variant_{koa3,kp3}      : LaNora's Altaria list against the table's other 7 lists on the table's seeds for Altaria's
#                             pairings (0-6), koa3 or kp3 on the variant, kp3 on the opponent
#   variant_self_{koa3,kp3} : LaNora's list against the table's own Altaria list, amendment 2's block 21,109,000,000 + i
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koa_2026-09-26/reading"
SCAN="$R/rl/engine-2026-09-27/legality_scan"; V=decks/variants-2026-09-23/altaria_lanora_blockdragon_2026-09-10.txt
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
until grep -q 'DIAGNOSTIC ROWS DONE' "$O/STATUS.txt" 2>/dev/null; do grep -q 'FAILED' "$O/STATUS.txt" && break; sleep 60; done
# The TSVs, in B2e's format (the scan resolves paths against --root).
H=$'pairing\tblock\theld_key\theld_file\topponent\tpanel_file\tseed_first\tseed_last\tsub_block_end'
{ echo "$H"; p=0; for opp in blaziken hydreigon lucario sceptile suicune vespiquen weezing; do
    s=$((72000000 + 10000 * p)); printf '%s\tvariant\taltaria_lanora\t%s\t%s\tdecks/research/%s.txt\t%s\t%s\t%s\n' $p "$V" $opp $opp $s $((s + 499)) $((s + 9999)); p=$((p + 1)); done
} > "$O/variant7.tsv"
{ echo "$H"; printf '0\tvariant_self\taltaria_lanora\t%s\taltaria\tdecks/research/altaria.txt\t21109000000\t21109000499\t21109009999\n' "$V"; } > "$O/variant_self.tsv"
cd "$R/engine"
run() { local name=$1; shift; [ -s "$O/$name.jsonl" ] && return; local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --games-out "$O/$name.jsonl.part" > "$O/$name.txt" 2>&1 \
    || { note "FAILED: $name"; exit 1; }
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"; }
run new17_koa3 --pairs "$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 8 24)" --bot koa3
run b2e_dustin_koa3 --pairs "$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 48 95)" --bot koa3
run variant_koa3 --pairs "$O/variant7.tsv" --root "$R" --seed-base 72000000 --pairings "$(seq -s, 0 6)" --bot-a koa3 --bot-b kp3
run variant_kp3 --pairs "$O/variant7.tsv" --root "$R" --seed-base 72000000 --pairings "$(seq -s, 0 6)" --bot kp3
run variant_self_koa3 --pairs "$O/variant_self.tsv" --root "$R" --seed-base 21109000000 --pairings 0 --bot-a koa3 --bot-b kp3
run variant_self_kp3 --pairs "$O/variant_self.tsv" --root "$R" --seed-base 21109000000 --pairings 0 --bot kp3
echo "$(date -u +%F\ %T) KOA EXTRAS DONE" >> "$O/STATUS.txt"
