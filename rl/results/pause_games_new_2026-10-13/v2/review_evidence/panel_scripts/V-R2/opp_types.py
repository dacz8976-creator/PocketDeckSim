import json, collections
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
META = json.load(open(R + "games_meta.json", encoding="utf-8"))
for g in ("kw-261012_203719000", "kw-261012_010706000", "kw-261013_010003000"):
    L = json.load(open(Q + META[g]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
    zt = collections.Counter(); att = collections.Counter(); boardE = collections.Counter()
    for t in L["turns"]:
        for when in ("board_at_start", "board_after"):
            b = (t.get(when) or {}).get("opponent") or {}
            z = b.get("energy_zone") or {}
            for k in ("this_turn", "next"):
                ty = (z.get(k) or {}).get("type")
                if ty: zt[ty] += 1
            for pk in [b.get("active")] + list(b.get("bench_in_position_order") or []):
                if pk:
                    for ty, n in ((pk.get("attached_energy") or {}).get("by_type") or {}).items():
                        if n: boardE[ty] += n
        if t.get("who_played") == "opponent":
            for pl in t.get("plays_in_order") or []:
                e = pl.get("energy") or {}
                if e.get("type"): att[e["type"]] += 1
    print(g, "| opp zone types:", dict(zt), "| opp attach types:", dict(att), "| opp board energy:", dict(boardE))
    # last turn number and who
    last = L["turns"][-1]
    print("   last row:", last["turn_number"], last["who_played"])
