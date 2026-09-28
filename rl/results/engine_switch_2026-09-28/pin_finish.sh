#!/usr/bin/env bash
# The kog engine switch, part 2, after the touched-path check (Dustin's ruling, Sept 28): merge the cloud branch at C
# into main (a merge commit M; main has results-only commits since the branch point), check that M's engine/ equals C's
# byte for byte (the programs are built from C), copy the programs to rl/engine-2026-09-28/, update the manifest (the
# Sept 27 release kept as history). The doc and screen edits and the pin commit follow in the same session.
# Usage (WSL): bash pin_finish.sh <commit>
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-28"
C=$(git -C "$R" rev-parse "$1"); B=/home/dacz8976/engine-official-${C:0:7}; P="$R/rl/engine-2026-09-28"
grep -q "PREPARE DONE $C" "$O/PIN_STATUS.txt" || { echo "prepare not done for $C"; exit 1; }
grep -q "TOUCHED DONE" "$O/PIN_STATUS.txt" || { echo "touched-path check not done"; exit 1; }
grep -q "SUITE at $C: exit 0; passed [0-9]*, failed 0" "$O/PIN_STATUS.txt" || { echo "suite not passed"; exit 1; }
! grep -q FAILED "$O/PIN_STATUS.txt" || { echo "a FAILED line in PIN_STATUS.txt"; exit 1; }
cd "$R"
git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com merge --no-ff -q -m "Merge claude/pensive-ptolemy-spwc0b at ${C:0:7} into main: the kog engine switch (Dustin, Sept 28)" "$C"
M=$(git rev-parse HEAD)
test -z "$(git diff "$C" "$M" -- engine)" || { echo "engine/ of the merge differs from $C"; exit 1; }
echo "$(date -u +%FT%TZ) MERGED ${C:0:7} into main as ${M:0:7}; engine/ identical to ${C:0:7}" >> "$O/PIN_STATUS.txt"
E="$B/engine/target/release"
mkdir -p "$P"; cp "$E/deckgym" "$P/deckgym"; cp "$E/examples/legality_scan" "$P/legality_scan"; cp "$E/examples/goldfish" "$P/goldfish"
( cd "$P" && sha256sum deckgym legality_scan goldfish > SHA256SUMS )
echo "$(date -u +%FT%TZ) PINNED in rl/engine-2026-09-28: $(tr '\n' ' ' < "$P/SHA256SUMS")" >> "$O/PIN_STATUS.txt"
python3 "$O/update_manifest.py" "$M" "$C"
echo "$(date -u +%F\ %T) PIN DONE ${M:0:7}" >> "$O/PIN_STATUS.txt"
