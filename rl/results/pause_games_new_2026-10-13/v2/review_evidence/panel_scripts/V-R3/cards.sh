cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "B3 134" "B2a 093" "Mesagoza" "Glimmet" "Copycat"; do
  echo "=== $c"
  python3 -B lib/card.py "$c" 2>&1 | head -40
done
