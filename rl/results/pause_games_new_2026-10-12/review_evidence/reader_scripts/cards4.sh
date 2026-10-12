cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' || exit 1
export PYTHONDONTWRITEBYTECODE=1
python3 -B lib/card.py "Team Rocket's Weezing ex" 2>&1 | head -c 1500
cd /mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review
python3 -I -B s12_turnplays.py 015452000 3
python3 -I -B s12_turnplays.py 020258000 4
python3 -I -B s12_turnplays.py 020908000 4
python3 -I -B s12_turnplays.py 003458000 7
