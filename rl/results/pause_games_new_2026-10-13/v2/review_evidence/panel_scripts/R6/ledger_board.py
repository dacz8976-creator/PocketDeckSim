import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
g = sys.argv[1]
t = int(sys.argv[2])
keys = sys.argv[3:]
d = json.load(open(base + g + "/TURN_LEDGER.json", encoding="utf-8"))
for r in d["turns"]:
    if r["turn_number"] == t:
        for k in keys:
            print("----", k)
            print(json.dumps(r.get(k), indent=1, ensure_ascii=False))
