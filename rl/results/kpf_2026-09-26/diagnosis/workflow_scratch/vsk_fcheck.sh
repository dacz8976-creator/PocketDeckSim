#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
echo "lines with Dragonair/Flareon in kpf dump:"
grep -c -E "Dragonair|Flareon" dump_kpf.txt
echo "distinct placed/evolved pokemon names in kpf dump (all decks):"
grep -o -E "(Place|Evolve \{ evolution: )\(?Pokemon\([A-Za-z0-9-]+ [0-9]+ [^)]*\)" dump_kpf.txt | sed -E 's/.*Pokemon\([A-Za-z0-9-]+ [0-9]+ //; s/\)$//' | sort | uniq -c | sort -rn | head -60
