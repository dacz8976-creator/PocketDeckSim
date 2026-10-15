import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "010706": base + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/TURN_LEDGER.json",
 "015011": base + "BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS/TURN_LEDGER.json",
}
for k, p in paths.items():
    d = json.load(open(p, encoding="utf-8"))
    print("=====", k, type(d))
    if isinstance(d, dict):
        for kk, v in d.items():
            if isinstance(v, list):
                print(kk, "list", len(v))
            elif isinstance(v, dict):
                print(kk, "dict", list(v.keys())[:30])
            else:
                print(kk, repr(v)[:200])
        rows = None
        for kk in ("turns", "rows", "ledger", "turn_rows"):
            if kk in d:
                rows = d[kk]
                break
        if rows:
            r = rows[0]
            print("ROW KEYS", list(r.keys()))
            for kk, v in r.items():
                print("  ", kk, ":", json.dumps(v, ensure_ascii=False)[:600])
    else:
        print(len(d))
        print(list(d[0].keys()))
