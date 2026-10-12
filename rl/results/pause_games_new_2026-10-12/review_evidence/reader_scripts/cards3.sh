cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
export PYTHONDONTWRITEBYTECODE=1
for n in 'Stakataka' 'Garchomp' "Team Rocket's Tinkaton" 'Happiny' 'Lucky Ice Pop' 'Wally'; do
  echo "######## $n"
  python3 -B lib/card.py "$n" 2>&1 | head -c 2500
done
