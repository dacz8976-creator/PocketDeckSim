import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(P, encoding="utf-8"))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:10])
    items = d.get("positions", d)
else:
    items = d
games = sys.argv[1:] or ["261013_010837000", "261013_014423000"]
out = []
for p in (items if isinstance(items, list) else items.values()):
    pid = p.get("id", "")
    if any(("KW-" + g + "-t") in pid for g in games):
        out.append(p)
print(len(out))
for p in out:
    print("=" * 100)
    print(json.dumps(p, indent=1, ensure_ascii=False))
