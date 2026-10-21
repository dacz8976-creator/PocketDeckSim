import json, sys
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
d = json.load(open(V2 + "positions_all.json"))
print(type(d), len(d) if hasattr(d, '__len__') else '')
if isinstance(d, dict):
    print(list(d.keys())[:20])
    items = d.get('positions', d)
else:
    items = d
games = sys.argv[1:]
out = []
for p in (items if isinstance(items, list) else items.values()):
    pid = p.get('id', '')
    if any(pid.startswith('KW-' + g + '-t') for g in games):
        out.append(p)
print(len(out))
for p in out:
    print("=" * 100)
    print(json.dumps(p, indent=1, ensure_ascii=False))
