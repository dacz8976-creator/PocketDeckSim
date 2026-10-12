cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
for c in "$@"; do python3 lib/card.py "$c"; echo; done
