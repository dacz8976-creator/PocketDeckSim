cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
export PYTHONDONTWRITEBYTECODE=1
for n in 'Caterpie' 'Metapod' 'Butterfree' 'Wailmer' 'Carvanha' 'Oricorio' 'Revavroom' 'Charmeleon' 'Dragonair' 'Feebas' 'Quick-Grow Extract'; do
  echo "######## $n"
  python3 -B lib/card.py "$n" 2>&1 | head -c 3000
done
