import json, sys
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
P = json.load(open(R + "positions_all.json", encoding="utf-8"))
items = P if isinstance(P, list) else P.get("positions", P)
if isinstance(items, dict):
    items = [dict(v, id=k) if isinstance(v, dict) else v for k, v in items.items()]
for p in items:
    pid = p.get("id") or p.get("position_id")
    if pid in sys.argv[1:]:
        print(json.dumps(p, indent=1, ensure_ascii=False))
