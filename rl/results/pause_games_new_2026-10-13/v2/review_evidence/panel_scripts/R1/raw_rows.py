import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "010706": base + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/TURN_LEDGER.json",
 "015011": base + "BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS/TURN_LEDGER.json",
}
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R1/"
k = sys.argv[1]
d = json.load(open(paths[k], encoding="utf-8"))
with open(OUT + "raw_" + k + ".txt", "w", encoding="utf-8") as f:
    for kk in d:
        if kk != "turns":
            f.write("TOP " + kk + ": " + json.dumps(d[kk], ensure_ascii=False, indent=1) + "\n")
    for t in d["turns"]:
        f.write("\n################ TURN %s %s\n" % (t["turn_number"], t["who_played"]))
        f.write(json.dumps(t, ensure_ascii=False, indent=1))
        f.write("\n")
print("ok")
