import json
POS = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
for p in json.load(open(POS)):
    if "015659" in p["id"]:
        o = p["opp"]
        print(p["id"], "hand_count", o.get("hand_count"), "| disc", o.get("discard"), "| board", [(b["card"], b.get("hp"), b.get("behind")) for b in o["board"]])
        print("    my hand", p["me"]["hand"], "| notes:", p.get("notes", "")[:300])
