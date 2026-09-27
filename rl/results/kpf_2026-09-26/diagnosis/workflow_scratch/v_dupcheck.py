import json, os, re
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sel = json.load(open(os.path.join(HERE, "selected.json"), encoding="utf-8"))
c = Counter(g["seed"] for g in sel)
dups = {s for s, n in c.items() if n > 1}
print("seeds selected more than once:", len(dups))
vs = [g for g in sel if g["deck"] == "vespiquen"]
print("vespiquen games whose seed is also selected for another deck:", sum(g["seed"] in dups for g in vs))
for g in vs:
    if g["seed"] in dups:
        others = [(h["deck"], h["config"], h["kind"]) for h in sel if h["seed"] == g["seed"] and h is not g]
        print(g["seed"], g["kind"], g["config"], "also:", others)
# how many traces per seed in each dump (tick==1 lines)
LINE = re.compile(r"DUMP2 (\d+) (\d+) ")
for name in ("dump_base.txt", "dump_kpf.txt"):
    starts = Counter()
    for line in open(os.path.join(HERE, name), encoding="utf-8"):
        m = LINE.match(line)
        if m and m.group(2) == "1":
            starts[int(m.group(1))] += 1
    vseeds = {g["seed"] for g in vs}
    print(name, "vesp seeds with >1 trace:", sum(1 for s in vseeds if starts[s] > 1), "missing:", sum(1 for s in vseeds if starts[s] == 0))
