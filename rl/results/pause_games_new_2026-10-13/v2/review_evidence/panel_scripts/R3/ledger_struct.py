import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "210041": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
 "230258": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
}
for k, p in paths.items():
    d = json.load(open(p, encoding='utf-8'))
    print("#####", k, type(d))
    if isinstance(d, dict):
        for kk, vv in d.items():
            if isinstance(vv, list):
                print(kk, "list", len(vv))
            elif isinstance(vv, dict):
                print(kk, "dict keys", list(vv.keys())[:30])
            else:
                print(kk, repr(vv)[:300])
        rows = None
        for kk in ("turns", "rows", "ledger", "turn_rows"):
            if kk in d:
                rows = d[kk]
        if rows:
            print("row keys:", list(rows[0].keys()))
            print(json.dumps(rows[0], indent=1, ensure_ascii=False)[:6000])
    else:
        print(len(d))
        print(list(d[0].keys()))
