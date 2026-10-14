import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(P, encoding="utf-8"))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:10])
    items = d.get("positions", d)
else:
    items = d
want = sys.argv[1:]
def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in ("evidence", "evidence_ids")}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o
if isinstance(items, dict):
    it = items.items()
else:
    it = [(p.get("id"), p) for p in items]
for pid, p in it:
    if any(w in str(pid) for w in want):
        print("=" * 20, pid)
        print(json.dumps(strip(p), ensure_ascii=False, indent=1))
