import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7"
d = sys.argv[1]
L = json.load(open(QA + "/" + d + "/TURN_LEDGER.json"))
print("schema", L.get("schema"))
print("limits", json.dumps(L.get("limits", L.get("interpretation_limits")), indent=1)[:3000])
print("sources", json.dumps(L.get("sources"), indent=1)[:1500])
turns = L["turns"]
print("nturns", len(turns))
print("keys of turn0", list(turns[0].keys()))
for t in turns:
    print(t.get("turn"), t.get("owner", t.get("player")), {k: (len(json.dumps(v))) for k, v in t.items()})
