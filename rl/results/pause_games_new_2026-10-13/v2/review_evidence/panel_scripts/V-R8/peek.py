import json, sys
V = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(V, encoding="utf-8"))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:10])
    items = d.get("positions", d)
else:
    items = d
first = items[0] if isinstance(items, list) else items[list(items.keys())[0]]
print(json.dumps(first, indent=1, ensure_ascii=False)[:6000])
