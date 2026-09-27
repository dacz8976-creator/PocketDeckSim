#!/usr/bin/env bash
# kpf's reading on the 45 cells (registration section 6), all at 9bffbda: kpf3, kpr3 and kpg3 each against kp3, rules
# v2, with kpf3's mixed rows. Writes score45_<bot>_vs_kp3.txt here.
set -euo pipefail
D="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/reading"; cd "$D"
nice -n 5 python3 score45.py --rules v2 --old-games table_kp3.jsonl new17_kp3.jsonl --new-games table_kpf3.jsonl new17_kpf3.jsonl \
  --old kp3 --new kpf3 --mixed mixed_table_kpf3_first.jsonl mixed_table_kpf3_second.jsonl mixed_new17_kpf3_first.jsonl mixed_new17_kpf3_second.jsonl \
  > score45_kpf3_vs_kp3.txt 2>&1
for b in kpr3 kpg3; do
  nice -n 5 python3 score45.py --rules v2 --old-games table_kp3.jsonl new17_kp3.jsonl --new-games table_$b.jsonl new17_$b.jsonl \
    --old kp3 --new $b > score45_${b}_vs_kp3.txt 2>&1
done
for b in kpf3 kpr3 kpg3; do echo "=== $b"; grep -E 'real error [0-9]|dMSE|real error, current|cell veto|deck veto|ADOPTION|mixed' score45_${b}_vs_kp3.txt | head -12 | cut -c1-260; done
