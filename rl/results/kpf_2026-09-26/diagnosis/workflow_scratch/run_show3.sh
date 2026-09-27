#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
python3 alt_show.py altaria "g['kind']=='worse' and g['own_turn'] and zs!=('B','A') and (zs==('A','B') or g['base'][0]['attack']!=g['kpf'][0]['attack'])" 24 | grep -v "board Z" 