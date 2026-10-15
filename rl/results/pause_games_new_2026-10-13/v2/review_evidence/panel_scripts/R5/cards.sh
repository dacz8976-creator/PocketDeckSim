cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "Igglybuff" "Darkrai" "Druddigon" "Haxorus" "Axew" "Dragonair" "Dratini" "Starting Plains" "Rainbow Cave" "Iris" "Rocky Helmet" "Sabrina" "Koraidon ex"; do
  echo "=================== $c"
  python3 lib/card.py "$c"
done
