import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
for g in ["20261013_010837000_iOS", "20261013_014423000_iOS"]:
    d = json.load(open(base + g + "/TURN_LEDGER.json", encoding="utf-8"))
    print("=" * 80, g, type(d))
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list):
                print(k, "list", len(v))
            elif isinstance(v, dict):
                print(k, "dict", list(v.keys())[:30])
            else:
                print(k, repr(v)[:200])
        rows = None
        for k in ("turns", "rows", "ledger", "turn_rows"):
            if k in d:
                rows = d[k]
                break
    else:
        rows = d
    if rows:
        print("row keys:", list(rows[0].keys()))
        print(json.dumps(rows[0], indent=1, ensure_ascii=False)[:6000])
