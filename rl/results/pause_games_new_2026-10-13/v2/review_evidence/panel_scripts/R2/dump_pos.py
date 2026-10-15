import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R2/"
d = json.load(open(P))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:10])
    items = d.get("positions", d)
else:
    items = d
if isinstance(items, dict):
    items = list(items.values())
for game in ["261012_203719000", "261012_225319000"]:
    sel = [p for p in items if str(p.get("id", "")).startswith("KW-" + game + "-t")]
    print(game, len(sel), [p["id"] for p in sel])
    with open(OUT + "pos_" + game + ".json", "w") as f:
        json.dump(sel, f, indent=1, ensure_ascii=False)
print(json.dumps(items[0], indent=1)[:3000])
