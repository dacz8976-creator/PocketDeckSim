cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Alolan Meowth" "Meowth" "Pidgey" "Mega Pidgeot ex" "Dratini" "Varoom" "Scyther" "Mega Scizor ex" "Orthworm" "Revavroom" "Glimmora" "Haxorus" "Axew" "Dragonair"; do
  echo "=================== $c"
  python3 lib/card.py "$c"
done
echo "=========== grep Nasty Plot"
python3 lib/card.py --help 2>&1 | head -30
