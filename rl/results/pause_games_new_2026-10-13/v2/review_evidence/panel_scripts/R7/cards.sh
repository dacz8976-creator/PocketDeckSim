#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7/cards_out.txt"
: > "$OUT"
for n in "Riolu" "Mega Lucario ex" "Lucario" "Hitmontop" "Protective Poncho" "Arena of Antiquity" "Pokémon Center Lady" "Shuckle ex" "Combee" "Vespiquen ex" "Teal Mask Ogerpon ex" "Leaf Cape" "Fragrant Forest" "X Speed" "Sabrina" "Copycat" "Alolan Grimer" "Alolan Muk" "Glimmet" "Glimmora" "Pawniard" "Kingambit" "Regigigas" "Ilima" "Mesagoza" "Lucky Ice Pop" "Heavy Helmet" "Rare Candy" "Professor's Research" "Poké Ball"; do
  echo "################ $n" >> "$OUT"
  python3 lib/card.py "$n" >> "$OUT" 2>&1
done
