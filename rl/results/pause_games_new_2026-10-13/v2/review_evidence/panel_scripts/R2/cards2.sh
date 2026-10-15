cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Frigibax" "Arctibax" "Baxcalibur" "Suicune ex" "Chien-Pao ex" "Giant Cape" "Soothing Shore" "Pokémon Center Lady" "Poké Ball" "Professor's Research" "Rare Candy"; do
  echo "################ $c"
  python3 lib/card.py "$c" 2>&1 | head -60
done
