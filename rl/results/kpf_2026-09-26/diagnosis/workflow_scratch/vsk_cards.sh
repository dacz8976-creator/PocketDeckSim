#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B4 010" "B4 011" "A4 021" "B2 017" "A2 150" "B3 147" "A3 147" "B3 153" "P-A 002"; do
  echo "=== $c"
  python3 lib/card.py "$c"
done
