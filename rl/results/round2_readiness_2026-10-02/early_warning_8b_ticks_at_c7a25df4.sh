#!/usr/bin/env bash
# Step 4, remade at c7a25df4 (Oct 10): coin_probe v2 (built on c7a25df4 by p2_probe_checks.sh) at the 21 look-ahead ticks and 4 controls of early_warning_8b/classify_output.txt.
set -uo pipefail
D=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/oct10/probe
R=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/r2
PAIRS=$R/rl/results/engine_switch_rules2_2026-10/early_warning_8b/pairs_8b.tsv
PROBE=$D/target/release/examples/coin_probe_v2
mkdir -p $D/runs8b
deck() { awk -F'\t' -v p="$1" -v c="$2" 'NR > 1 && $1 == p {print $c}' "$PAIRS"; }
while read -r kind bot p i t; do
  out=$D/runs8b/${bot}_${p}_${i}_${t}.txt
  (cd $D/src/engine && "$PROBE" --a "$D/root8b/$(deck $p 4)" --b "$D/root8b/$(deck $p 6)" --seed-base 23100000000 \
     --pairing $p --bot $bot --deal $i --tick $t > $out 2>&1); ec=$?
  echo "$kind $bot pairing $p i $i tick $t (exit $ec): $(grep -E '^RESULT' $out | paste -sd ' ')$(grep -q 'search stopped' $out && echo ' (node limit)')"
done <<'L'
look km3 35 2 89
look km3 35 3 44
look km3 35 10 43
look km3 35 13 60
look km3 35 14 41
look km3 35 26 44
look km3 35 30 38
look km3 35 31 58
look km3 35 35 90
look km3 35 37 48
look km3 35 38 69
look km3 37 15 51
look k3 35 10 40
look k3 35 13 59
look k3 35 14 42
look k3 35 19 35
look k3 35 26 41
look k3 35 30 38
look k3 37 23 77
look k3 37 34 48
look k3 37 35 68
control km3 33 1 9
control km3 33 3 8
control k3 33 1 9
control k3 33 3 8
L
