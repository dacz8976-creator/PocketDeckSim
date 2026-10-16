"""Item 7's test 8: km3 and kmb3 on the same 80 deck-01 deals must play identically until the first decision of the deck's seat
where a Blade candidate at count >= 1 is reachable (count >= 1 and a Pawniard-line Pokemon in play). Prints every first difference."""
import json
import sys

LINE = ("Pawniard", "Bisharp", "Kingambit")


def load(p):
    return {r["seed"]: r for r in map(json.loads, open(p)) if r}


a, b = load(sys.argv[1]), load(sys.argv[2])
same = diff = viol = 0
rows = []
for seed in sorted(a):
    ra, rb = a[seed], b.get(seed)
    if rb is None:
        print("missing in the second arm:", seed)
        continue
    da, db = ra["decisions"], rb["decisions"]
    k = next((i for i, (x, y) in enumerate(zip(da, db)) if x["chosen"] != y["chosen"]), None)
    if k is None and len(da) == len(db):
        same += 1
        continue
    if k is None:
        k = min(len(da), len(db))
    diff += 1
    d = da[k] if k < len(da) else db[k]
    seat = ra["deck_seat"]
    count = d["own_kos"][seat]
    board = [s["n"] for s in d["boards"][seat] if s]
    reachable = count >= 1 and any(n in LINE for n in board)
    ok = d["actor"] == seat and reachable
    viol += not ok
    rows.append({"seed": seed, "decision": k, "turn": d["turn"], "actor": d["actor"], "deck_seat": seat, "count": count, "board": board,
                 "km3": da[k]["chosen"] if k < len(da) else None, "kmb3": db[k]["chosen"] if k < len(db) else None, "reachable": ok})
print(f"test 8: {len(a)} deals; identical {same}; differ {diff}; first difference NOT at a reachable Blade (count >= 1, a Pawniard-line "
      f"Pokemon in play, the deck's seat deciding): {viol}")
counts = {}
for r in rows:
    counts[r["count"]] = counts.get(r["count"], 0) + 1
print("first differences by the deck's own-knock-out count:", dict(sorted(counts.items())))
for r in rows:
    print(json.dumps(r))
