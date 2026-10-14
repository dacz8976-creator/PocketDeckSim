import json
base = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/review_evidence/"
D = json.load(open(base + "verify_panel_output.json", encoding="utf-8"))
for i, r in enumerate(D["result"]):
    rv = r.get("review") or {}
    for f in rv.get("findings") or []:
        print(i, "|", f.get("severity"), "|", f.get("title"))
    for c in r.get("challenged") or []:
        v = c.get("verdict") or {}
        print("   challenged:", c.get("title"), "->", {k: v.get(k) for k in v if k != "reasoning"})
