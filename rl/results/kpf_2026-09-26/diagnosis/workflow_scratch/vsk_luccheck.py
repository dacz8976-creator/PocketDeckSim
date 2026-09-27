import json, os, pickle
from collections import Counter
from vsk_lib import selection, trace_index, seat_of, D
T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
sel = selection(); ti = trace_index(sel)
old = {}
for line in open(os.path.join(D, "divergences.jsonl"), encoding="utf-8"):
    r = json.loads(line); old[(r["deck"], r["seed"], r["config"])] = r
c = Counter()
for x in sel:
    if x["deck"] == "vespiquen":
        continue
    k_ = ti(x)
    X, Y = T["base"][x["seed"]][k_], T["kpf"][x["seed"]][k_]
    k = next((n for n in range(min(len(X), len(Y))) if X[n]["act"] != Y[n]["act"]), None)
    o = old[(x["deck"], x["seed"], x["config"])]
    same = o["tick"] == X[k]["tick"] and o["kp3_act"] == X[k]["act"] and o["kpf_act"] == Y[k]["act"]
    own = X[k]["actor"] == seat_of(x)
    c[(x["deck"], x["pairing"], x["kind"], "trace%d" % k_, "old==new" if same else "OLD WRONG", "own seat" if own else "opp seat", "old_actor_is_kpf=%s" % o["actor_is_kpf"])] += 1
for k, v in sorted(c.items()):
    if k[3] == "trace1" or k[4] == "OLD WRONG" or k[5] == "opp seat":
        print(v, k)
print("total non-vespiquen records checked:", sum(c.values()), " old wrong:", sum(v for k, v in c.items() if k[4] == "OLD WRONG"))
