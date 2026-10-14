#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for n in "Riolu" "Mega Lucario ex" "Hitmonchan ex" "Tyrogue" "Serena" "X Speed" "Arena of Antiquity" "Froakie" "Staryu" "Starmie ex" "Greninja" "Sabrina" "Regigigas" "Alolan Grimer" "Alolan Muk" "Glimmet" "Glimmora" "Kingambit" "Pawniard" "Mesagoza" "Copycat" "Lucky Ice Pop" "Heavy Helmet" "Ilima" "Rare Candy" "Cyrus" "Poké Ball" "Professor's Research"; do
  echo "################ $n"
  python3 lib/card.py "$n" 2>&1 | head -150
done
