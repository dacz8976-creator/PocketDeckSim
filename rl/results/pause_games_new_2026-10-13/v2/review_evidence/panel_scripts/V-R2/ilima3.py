import json
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
META = json.load(open(R + "games_meta.json", encoding="utf-8"))
L = json.load(open(Q + META["kw-261013_020824000"]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
t = [x for x in L["turns"] if x["turn_number"] == 11][0]
for pl in t["plays_in_order"]:
    print(json.dumps(pl, ensure_ascii=False)[:900])
