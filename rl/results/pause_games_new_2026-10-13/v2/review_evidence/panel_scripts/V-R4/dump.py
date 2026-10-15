import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(P, encoding="utf-8"))
if isinstance(d, dict):
    print("top keys", list(d.keys())[:20])
    items = d.get("positions", d)
else:
    items = d
game = sys.argv[1]
for p in (items if isinstance(items, list) else items.values()):
    pid = p.get("id") or p.get("position_id")
    if game in str(pid):
        print("=" * 30, pid)
        print(json.dumps(p, ensure_ascii=False, indent=1))
