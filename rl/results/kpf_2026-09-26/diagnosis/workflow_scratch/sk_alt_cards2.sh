#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B2b 051" "B3a 054" "B4 117" "B4 120" "B4 155" "B3a 072"; do
  echo "=== $c"
  python3 lib/card.py "$c" 2>&1 | head -30
done
