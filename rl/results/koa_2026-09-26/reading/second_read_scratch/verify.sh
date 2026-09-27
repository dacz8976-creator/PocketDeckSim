#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/koa_2026-09-26/reading/second_read_scratch" || exit 1
python3 verify.py > verify_out.txt 2>&1
cat verify_out.txt
