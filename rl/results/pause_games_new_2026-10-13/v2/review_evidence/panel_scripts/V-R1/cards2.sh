cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Tyrogue" "Falinks" "Pawniard"; do
  echo "######## $c"
  python3 -B lib/card.py "$c"
done
