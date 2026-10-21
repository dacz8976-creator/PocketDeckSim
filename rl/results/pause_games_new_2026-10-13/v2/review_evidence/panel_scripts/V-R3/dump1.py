import json, sys
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
games = {
    "210041": B + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
    "230258": B + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
}
which = sys.argv[1]
turn = int(sys.argv[2])
L = json.load(open(games[which], encoding="utf-8"))
print(type(L), (list(L.keys()) if isinstance(L, dict) else len(L)))
rows = L if isinstance(L, list) else (L.get("turns") or L.get("rows") or L.get("ledger"))
if rows is None:
    for k, v in L.items():
        if isinstance(v, list):
            print("list key", k, len(v))
    sys.exit()
print("row keys", list(rows[0].keys()))
for r in rows:
    t = r.get("turn") or r.get("turn_number") or r.get("game_turn")
    if t == turn:
        print(json.dumps(r, indent=1, ensure_ascii=False)[:60000])
