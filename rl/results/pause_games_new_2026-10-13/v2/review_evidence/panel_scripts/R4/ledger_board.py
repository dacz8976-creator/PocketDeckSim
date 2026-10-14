import json, sys
P = sys.argv[1]
t = int(sys.argv[2])
key = sys.argv[3] if len(sys.argv) > 3 else "board_after"
d = json.load(open(P + "/TURN_LEDGER.json"))
for r in d["turns"]:
    if r["turn_number"] == t:
        print(json.dumps(r[key], indent=1, ensure_ascii=False))
