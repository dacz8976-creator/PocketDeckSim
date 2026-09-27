#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
for spec in "72000056 t4" "72010089 t1" "72050131 t2" "72000027 t3" "72010118 t3"; do
  set -- $spec
  echo "=================== $1 $2 BASE"
  grep "^DUMP2 $1 " dump_base.txt | awk -v t="$2" '$4==t' | head -14 | cut -c1-420
  echo "------------------- $1 $2 KPF"
  grep "^DUMP2 $1 " dump_kpf.txt | awk -v t="$2" '$4==t' | head -14 | cut -c1-420
done