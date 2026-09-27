#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B1 196" "B1 102" "B1 184" "B3a 020" "B2b 040" "A4a 059" "B3 147" "B3b 064" "B2 153" "B1 225"; do
  echo "=== $c"
  python3 lib/card.py "$c" 2>&1 | head -30
done
