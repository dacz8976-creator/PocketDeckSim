#!/bin/bash
# Hand trace of the one UNEXPLAINED 8c game (step 9, km3, pairing 34, deal 449, first difference at tick 68): the score dump at
# tick 68 on the official engine, on the candidate, and on the candidate with each round-2 gate off alone and with all off.
W=$HOME/runs/s2_8c; O=$W/out/hand_9_34_449; mkdir -p "$O"
env | grep -qE '^(DECKGYM_|PG_DUMP=)' && { echo "a DECKGYM_* or PG_DUMP variable is set"; exit 2; }
A=$W/root/rl/results/b2e_card_check_2026-09-26/decks/h-whimsicott.txt
B=$W/root/decks/screen/opponents/t-sceptile.txt
args=(--a "$A" --b "$B" --seed-base 21106000000 --pairing 34 --bot km3 --deal 449 --tick 68)
run() {  # <label> <binary> <cwd> [extra]
    local lab=$1 bin=$2 cwd=$3; shift 3
    (cd "$cwd" && nice -n 19 "$bin" "${args[@]}" "$@" > "$O/$lab.txt" 2>&1); echo "$lab rc $?: $(grep -m1 'chose' "$O/$lab.txt" | cut -c1-160); $(grep -c '^PGDUMP' "$O/$lab.txt") candidates"
}
run official "$W/bin_dump_old_score_dump" "$W/dump_old/engine" &
run p "$W/bin_dump_new_score_dump" "$W/dump_new/engine" &
run official_tree "$W/bin_dump_old_score_dump" "$W/dump_old/engine" --tree &
run p_tree "$W/bin_dump_new_score_dump" "$W/dump_new/engine" --tree &
run all_off "$W/bin_dump_new_score_dump" "$W/dump_new/engine" --revert all &
wait
for g in p2 g1 g2 g3 g4 g5 g6 g7 g8 g9 g10 g11 g1,g2; do run "off_$g" "$W/bin_dump_new_score_dump" "$W/dump_new/engine" --revert "$g" & done
wait
echo "== candidates, official v p v all_off"
for f in official p all_off off_g6; do echo "-- $f"; grep '^PGDUMP' "$O/$f.txt" | cut -c1-170; done
grep -h 'PGBOARD' "$O/official.txt" | head -3
