import json, sys
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
meta = json.load(open(R + "games_meta.json", encoding="utf-8"))
g = sys.argv[1]
turns = [int(x) for x in sys.argv[2].split(",")]
L = json.load(open(B + meta[g]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
for t in L["turns"]:
    if t["turn_number"] in turns:
        print("=== turn", t["turn_number"], t["who_played"])
        for p in t.get("plays_in_order") or []:
            print(" ", p.get("order"), p.get("kind"), "|", p.get("card_name"), "| tgt:", p.get("target"), "| res:", str(p.get("result") or p.get("details"))[:200])
            for ne in p.get("nested_events_in_order") or []:
                print("      nested:", json.dumps(ne, ensure_ascii=False)[:200])
        for e in t.get("automatic_events_in_order") or []:
            print("  auto:", json.dumps(e, ensure_ascii=False)[:250])
