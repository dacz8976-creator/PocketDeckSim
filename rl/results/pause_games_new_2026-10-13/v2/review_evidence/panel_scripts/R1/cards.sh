cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for n in "Mega Diancie ex" "Indeedee ex" "Mega Gardevoir ex" "Kirlia" "Ralts" "Peculiar Plaza" "Giant Cape" "Regigigas" "Glimmora" "Glimmet" "Alolan Muk" "Alolan Grimer" "Kingambit" "Pawniard" "Falinks" "Tyrogue" "Mesagoza" "Heavy Helmet" "Lucky Ice Pop" "Copycat" "Ilima" "Sabrina" "Potion"; do
  echo "################ $n"
  python3 lib/card.py "$n" 2>&1 | head -80
done
