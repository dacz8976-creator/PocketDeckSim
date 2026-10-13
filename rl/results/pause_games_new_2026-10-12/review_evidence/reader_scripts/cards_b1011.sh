#!/bin/bash
cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
for q in "Slowpoke" "Pichu" "Dratini" "Dragonair" "Dragonite" "Magikarp" "Mega Gyarados ex" "Eevee ex" "Feebas" "Glaceon ex" "Milotic ex" "Pyukumuku" "Giant Cape" "Poison Barb" "Horsea" "Seadra" "Kingdra ex" "Team Rocket's Koffing" "Team Rocket's Weezing ex" "Small Balloon" "Hiking Trail" "Soothing Shore" "Copycat" "Sabrina" "Rare Candy"; do
  echo "################ $q"
  python3 lib/card.py "$q" 2>&1
done
