cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Drampa" "Dragonair" "Dratini" "Mega Rayquaza ex" "Ilima" "Lucky Ice Pop" "Rainbow Cave" "Mesagoza" "Glimmora" "Glimmet" "Kingambit" "Pawniard" "Heavy Helmet" "Copycat" "Regigigas" "Alolan Muk" "Alolan Grimer" "Rocky Helmet" "Cyrus"; do
  echo "################ $c"
  python3 lib/card.py "$c" 2>&1 | head -120
done
