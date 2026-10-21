import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
G = {"203719": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS/",
     "225319": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/"}
for g, p in G.items():
    L = json.load(open(p + "TURN_LEDGER.json"))
    pk, sk, bk, playk, aek, tk = set(), set(), set(), set(), set(), set()
    for t in L["turns"]:
        tk |= set(t.keys())
        for b in ("board_at_start", "board_after"):
            B = t.get(b) or {}
            bk |= set(B.keys())
            for side in ("owner", "opponent"):
                S = B.get(side) or {}
                sk |= set(S.keys())
                for x in [S.get("active")] + list(S.get("bench_in_position_order") or []):
                    if isinstance(x, dict):
                        pk |= set(x.keys())
        for pl in t.get("plays_in_order") or []:
            playk |= set(pl.keys())
        for ev in t.get("automatic_events_in_order") or []:
            if isinstance(ev, dict):
                aek |= set(ev.keys())
            else:
                aek.add("<str>")
    print("==", g)
    print(" turn keys", sorted(tk))
    print(" board keys", sorted(bk))
    print(" side keys", sorted(sk))
    print(" poke keys", sorted(pk))
    print(" play keys", sorted(playk))
    print(" auto ev keys", sorted(aek))
    print(" turns", [(t["turn_number"], t["who_played"]) for t in L["turns"]])
    print(" limits", L.get("limits"))
