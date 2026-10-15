cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for n in "Mega Lucario ex" "Riolu" "Rare Candy" "Copycat" "Hitmontop" "Protective Poncho" "Arena of Antiquity" "Pokémon Center Lady"; do
  echo "######## $n"
  python3 lib/card.py "$n" 2>&1 | head -60
done
