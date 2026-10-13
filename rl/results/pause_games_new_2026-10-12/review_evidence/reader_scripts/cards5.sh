cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
export PYTHONDONTWRITEBYTECODE=1
for n in 'Togekiss' 'Togetic'; do
python3 -B lib/card.py "$n" 2>&1 | head -c 2000
done
