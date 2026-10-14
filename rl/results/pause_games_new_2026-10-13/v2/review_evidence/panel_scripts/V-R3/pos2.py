import json, sys
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
P = json.load(open(R + "positions_all.json", encoding="utf-8"))
for p in P:
    if p["id"] in sys.argv[1:]:
        print(p["id"], "board:", json.dumps(p["me"]["board"], ensure_ascii=False))
        print("   plan:", p["his_plan"])
# plans ending with Attack:Giga Turbo or containing it
print("--- Giga Turbo plans")
for p in P:
    pl = p["his_plan"]
    if any(s == "Attack:Giga Turbo" for s in pl):
        i = pl.index("Attack:Giga Turbo")
        print(p["id"], "| after:", pl[i + 1:], "| plan:", pl)
