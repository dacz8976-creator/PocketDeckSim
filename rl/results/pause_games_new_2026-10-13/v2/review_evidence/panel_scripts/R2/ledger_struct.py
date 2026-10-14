import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
G = {"203719": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS/",
     "225319": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/"}
for k, p in G.items():
    L = json.load(open(p + "TURN_LEDGER.json"))
    print("=====", k, type(L))
    if isinstance(L, dict):
        for kk, vv in L.items():
            if isinstance(vv, list):
                print(" key", kk, "list", len(vv))
            elif isinstance(vv, dict):
                print(" key", kk, "dict", list(vv.keys())[:20])
            else:
                print(" key", kk, repr(vv)[:200])
        rows = None
        for kk in ("turns", "rows", "ledger", "turn_rows"):
            if kk in L:
                rows = L[kk]
        if rows:
            r = rows[0]
            print(" row keys", list(r.keys()))
            for kk, vv in r.items():
                print("   ", kk, json.dumps(vv, ensure_ascii=False)[:400])
