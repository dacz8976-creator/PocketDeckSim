#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
grep -m5 ':: Activate' dump_base.txt
grep -m3 ':: Play' dump_base.txt
grep -m3 ':: AttachTool' dump_base.txt
grep -m3 ':: UseStadium' dump_base.txt
grep -m3 ':: DrawCard' dump_base.txt
grep -m2 ':: ChooseRandomEvolutionTarget' dump_base.txt
grep -c 'Attach {.*is_turn_energy: false' dump_base.txt
grep -m3 'Attach {.*is_turn_energy: false' dump_base.txt