import json, sys
V = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(V, encoding="utf-8"))
ids = sys.argv[1:]
for p in d:
    if p["id"] in ids or any(p["id"].startswith(i) for i in ids):
        q = dict(p)
        q.pop("notes", None)
        print("=====", p["id"])
        print(json.dumps(q, ensure_ascii=False, indent=None)[:5000])
