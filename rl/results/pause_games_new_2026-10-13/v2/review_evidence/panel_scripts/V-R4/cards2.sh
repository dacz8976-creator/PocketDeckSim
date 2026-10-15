cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B2b 056" "B3 134" "B3a 045" "B3a 043" "B2 097" "P-B 006" "Rainbow Cave" "Soothing Shore" "B2b 001"; do
  echo "################ $c"
  python3 lib/card.py "$c"
done
