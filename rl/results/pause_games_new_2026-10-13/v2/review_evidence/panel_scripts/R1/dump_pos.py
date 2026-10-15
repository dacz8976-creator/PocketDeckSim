import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R1/"
d = json.load(open(P))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:20])
    items = d.get("positions", d)
else:
    items = d
if isinstance(items, dict):
    items = list(items.values())
games = ["261012_010706000", "261013_015011000"]
for g in games:
    sel = [p for p in items if str(p.get("id", "")).startswith("KW-" + g + "-t")]
    print(g, len(sel), [p["id"] for p in sel])
    json.dump(sel, open(OUT + "pos_" + g + ".json", "w"), indent=1)
print(json.dumps(items[0], indent=1)[:3000])
