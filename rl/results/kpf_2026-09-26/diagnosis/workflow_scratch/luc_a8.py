import json, os
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
runs = defaultdict(list)
for g in sel:
    runs[g["seed"]].append((g["pairing"], g["config"], g["deck"], g["kind"]))
bad = Counter()
for s, rs in runs.items():
    if len(rs) > 1:
        rs = sorted(rs)
        for r in rs[1:]:
            bad[(r[2], r[3])] += 1
print("records whose classify.py divergence came from another deck's traced game (not the first run of that seed):")
for k, v in sorted(bad.items()):
    print("  ", k, v)
