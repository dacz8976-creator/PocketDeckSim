import json
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
POS = json.load(open(R + "positions_all.json", encoding="utf-8"))
if isinstance(POS, dict): POS = POS.get("positions") or list(POS.values())
META = json.load(open(R + "games_meta.json", encoding="utf-8"))
for pid in ("KW-261013_020824000-t11", "KW-261012_210823000-t08", "KW-261012_203719000-t07"):
    p = [x for x in POS if x["id"] == pid][0]
    L = json.load(open(Q + META[p["game"]]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
    t = [x for x in L["turns"] if x["turn_number"] == p["turn_count"]][0]
    print("=====", pid)
    print("plan:", p["his_plan"], "| truncated_at", p["plan_truncated_at"], "| ended", p["his_plan_ended"], "| unresolved", p.get("unresolved"))
    print("board:", [(b["card"], b["hp"]) for b in p["me"]["board"]])
    print("notes:", p["notes"][:600])
    for pl in t["plays_in_order"]:
        print("   ", pl.get("order"), pl.get("kind"), "|", pl.get("card_name"), "|", pl.get("target"), "|", pl.get("result"), "|", pl.get("response"))

