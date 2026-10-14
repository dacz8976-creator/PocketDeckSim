import json, sys
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_NEWEST_TWO/20261013_030351000_iOS/TURN_LEDGER.json"
d = json.load(open(P, encoding="utf-8"))
print(type(d))
if isinstance(d, dict):
    print(list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print(k, len(v))
            if v and isinstance(v[0], dict):
                print("  row keys:", list(v[0].keys()))
rows = d["rows"] if isinstance(d, dict) and "rows" in d else (d if isinstance(d, list) else None)
if rows is None:
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            rows = v; break
for r in rows:
    print(r.get("turn"), r.get("player") or r.get("actor") or r.get("side"), [k for k in r.keys()][:30])
