import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
D = json.load(open(P, encoding="utf-8"))
pos = D if isinstance(D, list) else (D.get("positions") or D)
if isinstance(pos, dict):
    print("keys", list(pos.keys())[:20])
    pos = list(pos.values())
for p in pos:
    if p["id"] in sys.argv[1:]:
        print("=" * 20, p["id"])
        print(json.dumps(p, ensure_ascii=False, indent=1))
