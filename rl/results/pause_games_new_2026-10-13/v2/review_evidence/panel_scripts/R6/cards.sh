cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for n in "Pichu" "Mega Kangaskhan ex" "Team Rocket's Rattata" "Team Rocket's Raticate ex" "Red" "Ilima" "Dedenne ex" "Emolga" "Zeraora" "Electrical Cord" "Rocky Helmet" "Small Balloon" "Electric Generator" "Copycat" "Kingambit" "Glimmora" "Glimmet" "Pawniard" "Alolan Muk" "Alolan Grimer" "Regigigas" "Heavy Helmet" "Lucky Ice Pop"; do
  echo "################ $n"
  python3 -B lib/card.py "$n" 2>&1 | head -150
done
