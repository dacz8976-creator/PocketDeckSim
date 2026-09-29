import json, glob, os, collections, sys
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results"
K = R + "/kt_tables_2026-09-28"
def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
def summ(p):
    rows = load(p)
    cells = collections.OrderedDict()
    for r in rows:
        k = (r.get("a"), r.get("b"), r.get("bot_a"), r.get("bot_b"))
        cells.setdefault(k, []).append(r["i"])
    print(os.path.basename(p), len(rows), "rows;", len(cells), "cells; keys sample fields:", sorted(rows[0].keys()))
    for k, v in list(cells.items())[:50]:
        print("   ", k, len(v), min(v), max(v))
for p in sys.argv[1:]:
    summ(p)
