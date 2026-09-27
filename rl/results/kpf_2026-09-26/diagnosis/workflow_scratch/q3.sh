#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
for f in dump_base.txt dump_kpf.txt; do echo "== $f"; grep "^DUMP2 72040147 " $f | awk '$4=="t3"' | head -8 | cut -c1-400; done