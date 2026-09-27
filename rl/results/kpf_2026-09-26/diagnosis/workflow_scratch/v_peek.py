import json, os
from collections import Counter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
recs = [json.loads(l) for l in open(os.path.join(HERE, "divergences.jsonl"), encoding="utf-8")]
v = [r for r in recs if r["deck"] == "vespiquen"]
print(len(v), Counter(r["kind"] for r in v))
print(json.dumps(v[0], indent=1))
print(Counter((r["kind"], r["actor_is_kpf"]) for r in v))
sel = json.load(open(os.path.join(HERE, "selected.json"), encoding="utf-8"))
print(json.dumps(sel[0], indent=1))
print(Counter((g["deck"], g["a"], g["b"]) for g in sel if g["deck"] == "vespiquen"))
