cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "A3b 051" "B4 116" "Alolan Meowth" "Meowth" "A1 186" "B1 180" "Giant Cape" "Elegant Cape" "Mesagoza" "Ilima" "Dragonair" "Scyther" "Mega Scizor ex"; do
  echo "################ $c"
  python3 lib/card.py "$c"
done
