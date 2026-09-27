import json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
c = Counter(g["seed"] for g in sel)
dups = [s for s, n in c.items() if n > 1]
print("selected", len(sel), "unique seeds", len(c), "dups", len(dups))
for s in dups[:10]:
    print([ (g["deck"], g["a"], g["b"], g["config"], g["kind"]) for g in sel if g["seed"] == s])
print(open(os.path.join(D, "run_dumps.sh")).read())
