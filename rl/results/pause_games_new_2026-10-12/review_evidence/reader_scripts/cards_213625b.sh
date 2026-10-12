cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
for n in "Lucky Ice Pop" "Quick-Grow Extract" "Fragrant Forest" "Hiking Trail" "Pinsir"; do echo "=== $n"; python3 lib/card.py "$n"; done
