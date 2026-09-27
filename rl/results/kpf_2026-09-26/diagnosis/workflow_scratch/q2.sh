#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
echo "== KPF"; grep "^DUMP2 72000027 " dump_kpf.txt | awk '$4=="t4"||$4=="t5"||$4=="t6"||$4=="t7"' | cut -c1-330
echo "== BASE"; grep "^DUMP2 72000027 " dump_base.txt | awk '$4=="t5"||$4=="t7"' | cut -c1-330