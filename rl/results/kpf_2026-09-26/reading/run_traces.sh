#!/usr/bin/env bash
# kpf's trace diagnostics (registration section 6) and the hoarding check (section 9): 200 Rayquaza v Lucario deals
# (seeds 21,108,900,000+), each pilot on Rayquaza against kp3 on Lucario, with the official build's deckgym
# (main-83e17ae, whose engine/ equals kpf's build). Waits for the pin's anchored last line.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; D="$R/rl/results/kpf_2026-09-26/reading"
until grep -q 'PIN DONE' "$R/rl/results/engine_switch_2026-09-26/PIN_STATUS.txt" 2>/dev/null; do
  grep -q 'PIN FAILED' "$R/rl/results/engine_switch_2026-09-26/PIN_STATUS.txt" 2>/dev/null && exit 1; sleep 30; done
E="$R/rl/engine-2026-09-27/deckgym"; cd "$R"
for p in kp3 kpr3 kpg3 kpf3; do
  nice -n 10 python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt \
    decks/screen/opponents/t-lucario.txt --games 200 --pilot $p --opp-pilot kp3 --engine "$E" > "$D/trace_rayquaza_v_lucario_${p}.txt" 2>&1
done
echo "$(date -u +%F\ %T) TRACES DONE" >> "$D/STATUS.txt"
