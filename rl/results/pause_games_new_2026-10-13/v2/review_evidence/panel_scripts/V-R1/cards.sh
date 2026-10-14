cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Mega Diancie ex" "Mega Gardevoir ex" "Indeedee ex" "Regigigas" "Alolan Muk" "Kingambit" "Alolan Grimer"; do
  echo "######## $c"
  python3 -B lib/card.py "$c"
done
