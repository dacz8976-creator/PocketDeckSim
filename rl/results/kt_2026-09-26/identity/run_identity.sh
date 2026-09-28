#!/usr/bin/env bash
# kt's identity checks at its build (README "IDENTITY AND ORDER", step 3), on the table's deals (72,000,000 +
# pairing x 10,000 + i, even i = first-named deck in seat 0; all 28 pairings):
# - k3, kp3 and kq3 over all 500 deals (14,000 games each) must equal the repaired engine's references:
#   ../../rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl, and official_kq3_500.jsonl (kq3 from the official
#   program, rl/engine-2026-09-27/legality_scan e6ab9a9d, run first by this folder);
# - kd3 and kpr3 over the first 40 deals (1,120 games) must equal ../../rules09_fixes_2026-09-26/af8489f_{kd3,kpr3}_40;
# - kt3, kta3, ktb3 and ktc3 over the first 40 deals are smokes (clean runs), with kp3 on the same 40 deals run
#   between them for timing (kt3 within 1.25x of kp3).
# Waits for official_kq3_500 to finish so the timings share a quiet machine. compare.py reads the outputs.
# OUT (default: this folder) takes the outputs while they run; they are copied here when complete.
# Usage: [OUT=<dir>] run_identity.sh <legality_scan built at the kt build commit> <label>
set -euo pipefail
SCAN=$1; L=$2; D=$(cd "$(dirname "$0")" && pwd); O=${OUT:-$D}; cd "$D/../../../../engine"
until grep -q '^official_kq3_500' "$D/timing.txt" 2>/dev/null; do sleep 60; done
echo "$L scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$O/timing.txt"
run() { local bot=$1 n=$2 s; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$O/${L}_${bot}_${n}.jsonl" > "$O/${L}_${bot}_${n}.txt" 2>&1
  echo "${L}_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$O/timing.txt"; }
for bot in kp3 kt3 kta3 ktb3 ktc3 kd3 kpr3; do run "$bot" 40; done
for bot in k3 kp3 kq3; do run "$bot" 500; done
echo "$L identity done" >> "$O/timing.txt"
