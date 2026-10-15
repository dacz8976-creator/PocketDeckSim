import json, sys
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7"
pos = json.load(open(V2 + "/positions_all.json"))
print(type(pos), len(pos))
if isinstance(pos, dict):
    print(list(pos.keys())[:10])
    items = pos.get("positions", pos)
else:
    items = pos
games = ["261013_015659000", "261013_020824000"]
sel = []
for p in items if isinstance(items, list) else items.values():
    pid = p.get("id", "")
    if any(pid.startswith("KW-" + g + "-t") for g in games):
        sel.append(p)
print("selected", len(sel), [p["id"] for p in sel])
for g in games:
    with open(OUT + "/pos_" + g + ".json", "w") as f:
        json.dump([p for p in sel if p["id"].startswith("KW-" + g)], f, indent=1)
for g, d in [("261013_015659000", "20261013_015659000_iOS"), ("261013_020824000", "20261013_020824000_iOS")]:
    L = json.load(open(QA + "/" + d + "/TURN_LEDGER.json"))
    print(g, type(L), list(L.keys()) if isinstance(L, dict) else len(L))
