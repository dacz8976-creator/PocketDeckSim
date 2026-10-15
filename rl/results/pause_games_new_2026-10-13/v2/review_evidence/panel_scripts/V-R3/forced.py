import json, sys, glob, os
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/runs_forced/"
print(os.listdir(R)[:10])
S = json.load(open(R + "forced_summary.json", encoding="utf-8"))
for s in S:
    if s["id"] in sys.argv[1:]:
        print(json.dumps(s, ensure_ascii=False, indent=1)[:4000])
