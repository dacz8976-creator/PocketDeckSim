#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/koa_2026-09-26/reading/second_read_scratch" || exit 1
python3 verify3.py > verify3_out.txt 2>&1
cat verify3_out.txt
