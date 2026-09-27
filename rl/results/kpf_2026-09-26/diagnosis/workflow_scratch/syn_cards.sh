#!/bin/bash
# Synthesis agent: card texts for the Pokemon in the three diagnosed lists and the Rayquaza list.
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B1 196" "B1 102" "B1 184" "B3a 020" "B2b 040" "A4a 059" \
         "B3 079" "B3 081" "A2 092" "B3 078" "A1 154" \
         "B4 010" "B4 011" "A4 021" "B2 017" \
         "B2b 051" "B3a 054" "B4 117" "B4 120"; do
  echo "=== $c"
  python3 lib/card.py "$c" 2>&1 | head -30
done
