cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "A3b 051" "B4 116" "B1 154" "B2b 040" "B3 134" "A2 147" "B3b 065" "Scyther" "Mega Scizor ex"; do
  echo "=== $c"
  python3 lib/card.py "$c" 2>&1 | head -60
done
