cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B4 124" "B4 120" "B3a 043" "B3a 045" "B3 134" "A3 149" "B2 097" "B4 155" "B1 219" "B2a 093"; do
  echo "######## $c"
  python3 -B lib/card.py "$c"
done
