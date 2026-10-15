cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Regigigas" "Glimmora" "Glimmet" "Alolan Grimer" "Alolan Muk" "Drampa" "Mesagoza" "Lucky Ice Pop" "Heavy Helmet" "Field Blower" "Copycat" "Kingambit" "Pawniard" "Ilima" "Poké Ball" "Professor's Research" "Rare Candy"; do
  echo "=================== $c"
  python3 lib/card.py "$c"
done
