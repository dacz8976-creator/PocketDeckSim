import json, sys
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_NEWEST_TWO/20261013_030351000_iOS/TURN_LEDGER.json"
d = json.load(open(P, encoding="utf-8"))
def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "." + str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i, out)
    else:
        out.append((path, o))
for t in d["turns"]:
    tn = t["turn_number"]
    print("=" * 30, "turn", tn, t["who_played"])
    for key in ("board_at_start", "board_after"):
        b = t.get(key)
        print("--", key)
        print(json.dumps(b, ensure_ascii=False)[:6000])
    print("-- plays")
    print(json.dumps(t.get("plays_in_order"), ensure_ascii=False)[:5000])
    print("-- auto")
    print(json.dumps(t.get("automatic_events_in_order"), ensure_ascii=False)[:4000])
