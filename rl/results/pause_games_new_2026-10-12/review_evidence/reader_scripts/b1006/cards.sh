#!/bin/bash
cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
for n in "$@"; do
  echo "##### $n"
  python3 -B lib/card.py "$n" 2>&1 | head -c 6000
done
