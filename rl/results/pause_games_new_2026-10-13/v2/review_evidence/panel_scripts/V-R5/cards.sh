cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Darkrai" "Igglybuff" "Druddigon" "Regigigas" "Starting Plains"; do
  echo "=========== $c"
  python3 -B lib/card.py "$c"
done
