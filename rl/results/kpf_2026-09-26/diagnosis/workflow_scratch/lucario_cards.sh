#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B3 079" "B3 081" "A2 092" "B3 078" "A1 154" "B1 225" "B3 149" "A2b 070" "A2 150" "B3 147" "B2 147" "B3 154" "P-A 002"; do
  echo "=== $c"
  python3 lib/card.py "$c" 2>&1 | head -40
done
