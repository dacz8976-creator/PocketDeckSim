#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for x in "$@"; do echo "##### $x"; python3 lib/card.py "$x"; done
