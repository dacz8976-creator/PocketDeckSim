R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/POSITION_TABLE.md"
import sys
for l in open(R, encoding="utf-8"):
    if any(k in l for k in sys.argv[1:]):
        print(l[:900])
