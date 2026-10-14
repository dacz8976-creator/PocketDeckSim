import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7"
d = sys.argv[1]
L = json.load(open(QA + "/" + d + "/TURN_LEDGER.json"))
out = open(OUT + "/ledger_" + d + ".txt", "w")
for i, t in enumerate(L["turns"]):
    out.write("=" * 100 + "\n")
    out.write("ROW %d\n" % i)
    for k, v in t.items():
        out.write("--- %s: %s\n" % (k, json.dumps(v, ensure_ascii=False)))
out.close()
