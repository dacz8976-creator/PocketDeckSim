#!/usr/bin/env bash
# The full test suite at the new commit (Dustin, Sept 28: "Plus the full test suite, which includes those cards' own
# tests"), in the pin's scratch tree. Usage (WSL): bash run_suite.sh <commit>
set -uo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-28"
C=$(git -C "$R" rev-parse "$1"); B=/home/dacz8976/engine-official-${C:0:7}
source "$HOME/.cargo/env" 2>/dev/null || true
cd "$B/engine"
# Its own target folder: cargo test also rebuilds the examples, and the pin copies from target/release.
CARGO_TARGET_DIR="$B/target-suite" nice -n 15 cargo test --release --features test-utils -j 6 > "$O/suite.log" 2>&1; rc=$?
passed=$(grep -E '^test result:' "$O/suite.log" | sed -E 's/.* ([0-9]+) passed.*/\1/' | paste -sd+ | bc)
failed=$(grep -E '^test result:' "$O/suite.log" | sed -E 's/.* ([0-9]+) failed.*/\1/' | paste -sd+ | bc)
echo "$(date -u +%FT%TZ) SUITE at $C: exit $rc; passed $passed, failed $failed ($(grep -c '^test result:' "$O/suite.log") test binaries)" >> "$O/PIN_STATUS.txt"
grep -E '^test .*(metal_core|jasmine|cheren|blue|turn_effect|temporary_defender|permanent_tool).* \.\.\. ' "$O/suite.log" | sort > "$O/suite_touched_tests.txt"
echo "$(date -u +%F\ %T) SUITE DONE" >> "$O/PIN_STATUS.txt"
