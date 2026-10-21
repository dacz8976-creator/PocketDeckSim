cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
for n in "Caterpie" "Metapod" "Butterfree" "Accelgor" "Shelmet" "Budew"; do echo "=== $n"; python3 lib/card.py "$n"; done
