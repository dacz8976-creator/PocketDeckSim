import json
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
S = json.load(open(V2 + "runs_forced/forced_summary.json"))
for s in S:
    if "203719" in s["id"] or "225319" in s["id"]:
        print(s["id"], "| force:", s["force"], "| note:", s["note"])
        print("   first_dev:", s["first_deviation"])
        print("   next_choice:", s.get("next_choice_km3"))
# one forced record for t07
import os
f = V2 + "runs_forced/forced_KW-261012_203719000-t07.json"
if os.path.exists(f):
    R = json.load(open(f))
    for r in R[:1]:
        for st in r["steps"]:
            print("  step", {k: v for k, v in st.items() if k != "legal"})
            if "legal" in st:
                print("     legal:", st["legal"][:30])
