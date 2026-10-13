cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
for n in "$@"; do echo "==== $n"; python3 lib/card.py "$n"; done
