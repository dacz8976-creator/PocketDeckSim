import json, sys
P = sys.argv[1]
d = json.load(open(P + "/TURN_LEDGER.json"))
print(type(d))
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, list):
            print(k, "list", len(v))
        elif isinstance(v, dict):
            print(k, "dict", list(v.keys())[:30])
        else:
            print(k, repr(v)[:200])
    rows = None
    for k in ("turns", "rows", "ledger", "turn_ledger"):
        if k in d:
            rows = d[k]
            break
else:
    rows = d
if rows:
    print("rows", len(rows))
    r = rows[0]
    print("keys of row0:", list(r.keys()))
    for k, v in r.items():
        s = json.dumps(v, ensure_ascii=False)
        print("  ", k, ":", s[:600])
