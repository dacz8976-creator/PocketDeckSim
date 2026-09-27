import json, os, pickle
from collections import Counter, defaultdict
from vsk_lib import *

sel = selection()
print("selected", len(sel), Counter((x["deck"], x["kind"]) for x in sel))
print("pairings per deck", {d: sorted({(x["pairing"], x["a"], x["b"], x["config"]) for x in sel if x["deck"] == d}) for d in ("vespiquen",)})
seeds = Counter(x["seed"] for x in sel)
dup = {s for s, n in seeds.items() if n > 1}
print("seeds appearing >1 in selection:", len(dup), Counter((x["pairing"], x["deck"], x["config"]) for x in sel if x["seed"] in dup))
base, kpf = load_traces("dump_base.txt"), load_traces("dump_kpf.txt")
print("trace counts base", Counter(len(v) for v in base.values()), "kpf", Counter(len(v) for v in kpf.values()))
ti = trace_index(sel)
# are duplicate base traces identical?
same = sum(1 for s in dup if all(a["act"] == b["act"] for a, b in zip(base[s][0], base[s][1])) and len(base[s][0]) == len(base[s][1]))
print("dup seeds with identical base traces:", same, "of", len(dup))

old = {}
for line in open(os.path.join(D, "divergences.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    old[(r["deck"], r["seed"], r["config"])] = r

out = []
for x in sel:
    if x["deck"] != "vespiquen":
        continue
    k_ = ti(x)
    X, Y = base[x["seed"]][k_], kpf[x["seed"]][k_]
    k = next((n for n in range(min(len(X), len(Y))) if X[n]["act"] != Y[n]["act"]), None)
    seat = seat_of(x)
    r = dict(x, trace=k_, k=k, turn=X[k]["turn"], actor=X[k]["actor"], seat=seat, kp3_act=X[k]["act"], kpf_act=Y[k]["act"])
    o = old[("vespiquen", x["seed"], x["config"])]
    r["old_same"] = (o["turn"] == r["turn"] and o["kp3_act"] == r["kp3_act"] and o["kpf_act"] == r["kpf_act"] and o["tick"] == X[k]["tick"])
    out.append(r)
print("vespiquen records", len(out), "trace idx", Counter(r["trace"] for r in out))
print("new divergence on own seat:", Counter((r["kind"], r["actor"] == r["seat"]) for r in out))
print("old record differs from new:", Counter((r["kind"], r["old_same"]) for r in out))
print("old actor_is_kpf for vespiquen:", Counter((o["kind"], o["actor_is_kpf"]) for o in old.values() if o["deck"] == "vespiquen"))
print("differing by pairing:", Counter((r["pairing"], r["a"], r["b"], r["kind"]) for r in out if not r["old_same"]))
# the other decks: which trace would be right for them, and is it trace 0?
print("other decks trace idx:", Counter((x["deck"], x["pairing"], x["a"], x["b"], ti(x)) for x in sel if x["deck"] != "vespiquen" and x["seed"] in dup))
pickle.dump({"base": base, "kpf": kpf}, open("/tmp/vsk_traces.pkl", "wb"))
json.dump(out, open("vsk_div.json", "w"))
