#!/usr/bin/env bash
# koh's identity checks at its build (agreed with the laptop, Sept 27-28), on the table's deals (72,000,000 + pairing x
# 10,000 + i, even i = first-named deck in seat 0; all 28 pairings):
# - k3 and kp3 over the first 40 deals must equal the official references (../rules09_fixes_2026-09-26/af8489f_*_500);
# - kog3 over all 500 deals (koh with R' off) must equal the cloud's kog3 table, ../kog_2026-09-27/a823b6d_kog3_500
#   (which the laptop's table_kog3 equals, 14,000 of 14,000);
# - koh3 over the first 40 deals is a smoke (a clean run). The laptop reads it.
# koh with A and B off (kog + R) is checked on values in the tests (it has no code of its own).
# OUT (default: this folder) takes the outputs while they run; they are copied here when complete.
# Usage: [OUT=<dir>] run_identity.sh <legality_scan built at the koh build commit> <label>
set -euo pipefail
SCAN=$1; L=$2; D=$(cd "$(dirname "$0")" && pwd); O=${OUT:-$D}; cd "$D/../../../engine"
echo "$L scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$O/timing.txt"
run() { local bot=$1 n=$2 s; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$O/${L}_${bot}_${n}.jsonl" > "$O/${L}_${bot}_${n}.txt" 2>&1
  echo "${L}_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$O/timing.txt"; }
run k3 40; run kp3 40; run koh3 40; run kog3 500
echo "$L identity done" >> "$O/timing.txt"
