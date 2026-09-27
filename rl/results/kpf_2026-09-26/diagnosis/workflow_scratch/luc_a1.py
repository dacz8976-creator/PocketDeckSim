import json, os, re, math
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
recs = [json.loads(l) for l in open(os.path.join(D, "divergences.jsonl"), encoding="utf-8")]
L = [r for r in recs if r["deck"] == "lucario"]
print(len(L), Counter(r["kind"] for r in L))
print("actor_is_kpf", Counter((r["kind"], r["actor_is_kpf"]) for r in L))
print("pairings", Counter((r["a"], r["b"], r["kind"]) for r in L))
print("turns worse", sorted(Counter(r["turn"] for r in L if r["kind"]=="worse").items()))
print("turns better", sorted(Counter(r["turn"] for r in L if r["kind"]=="better").items()))
for kind in ("worse","better"):
    print("==", kind, "kpf_cat")
    c = Counter(r["kpf_cat"] for r in L if r["kind"]==kind)
    print(c.most_common())
    print("==", kind, "kp3_cat")
    c = Counter(r["kp3_cat"] for r in L if r["kind"]==kind)
    print(c.most_common())
# sample boards
for r in L[:5]:
    print(json.dumps(r, indent=0)[:1500])
