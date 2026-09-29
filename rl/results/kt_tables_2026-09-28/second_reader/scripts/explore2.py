import json, glob, os, collections, sys
def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
def summ(p, maxcells=12):
    rows = load(p)
    cells = collections.OrderedDict()
    for r in rows:
        k = (r.get("pairing"), r.get("a"), r.get("b"), r.get("bot_a"), r.get("bot_b"))
        cells.setdefault(k, []).append(r["i"])
    print(os.path.basename(p), len(rows), "rows;", len(cells), "cells; fields:", sorted(rows[0].keys()))
    for k, v in list(cells.items())[:maxcells]:
        print("   ", k, len(v), min(v), max(v))
    if len(cells) > maxcells:
        print("    ...", list(cells.items())[-1][0])
for p in sys.argv[1:]:
    summ(p)
