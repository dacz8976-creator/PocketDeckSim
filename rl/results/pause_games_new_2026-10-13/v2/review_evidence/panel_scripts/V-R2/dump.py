import json, sys
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS/TURN_LEDGER.json"
L = json.load(open(P, encoding="utf-8"))
print(type(L), (list(L.keys()) if isinstance(L, dict) else len(L)))
rows = L["turns"] if isinstance(L, dict) and "turns" in L else L
if isinstance(L, dict):
    for k, v in L.items():
        if k != "turns":
            print("TOP", k, json.dumps(v, ensure_ascii=False)[:600])
which = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
for r in rows:
    t = r.get("turn") or r.get("turn_number")
    if which and t not in which:
        continue
    print("=" * 30, "TURN", t)
    print(json.dumps(r, ensure_ascii=False, indent=1))
