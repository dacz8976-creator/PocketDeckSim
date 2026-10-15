import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
G = {"203719": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS/",
     "225319": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/"}
g, tn = sys.argv[1], int(sys.argv[2])
keys = sys.argv[3].split(",") if len(sys.argv) > 3 else None
L = json.load(open(G[g] + "TURN_LEDGER.json"))
for t in L["turns"]:
    if t["turn_number"] == tn:
        if keys:
            t = {k: t.get(k) for k in keys}
        print(json.dumps(t, indent=1, ensure_ascii=False))
