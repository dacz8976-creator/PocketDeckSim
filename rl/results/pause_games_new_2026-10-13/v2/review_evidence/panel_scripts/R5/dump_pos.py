import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(P, encoding="utf-8"))
games = sys.argv[1:] or ["261013_010003000", "261013_030351000"]
items = d if isinstance(d, list) else d.get("positions", d)
if isinstance(items, dict):
    print("top keys", list(items.keys())[:10])
    items = list(items.values())
out = []
for p in items:
    pid = p.get("id") or p.get("position_id")
    if any(pid.startswith("KW-" + g + "-t") for g in games):
        out.append(p)
print("count", len(out))
for p in out:
    print("=" * 100)
    print(json.dumps(p, indent=1, ensure_ascii=False))
