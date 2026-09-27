"""Skeptic's independent recount for the Altaria finding (does not import the analyst's scripts)."""
import json, re, sys, pickle, os
from collections import defaultdict, Counter
from math import comb

D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
OUT = D + "workflow_scratch/sk_alt_games.pkl"
RX = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")
MONRX = re.compile(r"^(.+?) (\d+)hp((?: [A-Z]{3})*) E\[([A-Za-z]*)\]$")


def side(s):
    parts = s.split(" | ")
    head = parts[0]
    m = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", head)
    act = parts[1].strip() if len(parts) > 1 else "-"
    bench = parts[2].strip() if len(parts) > 2 else ""
    def mon(x):
        mm = MONRX.match(x.strip())
        return None if not mm else (mm.group(1), int(mm.group(2)), mm.group(3).strip(), mm.group(4))
    a = None if act in ("-", "") else mon(act)
    b = [mon(x) for x in re.findall(r"[^,]+?hp(?: [A-Z]{3})* E\[[A-Za-z]*\]", bench)]
    return {"zc": m.group(1), "zn": m.group(2), "D": int(m.group(3)), "H": int(m.group(4)), "P": int(m.group(5)),
            "a": a, "b": [x for x in b if x]}


def load(name, seeds):
    g = defaultdict(list)
    last = {}
    with open(D + name, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("DUMP2"):
                continue
            sd = int(line.split(" ", 2)[1])
            if sd not in seeds:
                continue
            m = RX.match(line.rstrip("\n"))
            if not m:
                continue
            seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
            tick = int(tick)
            if sd not in last or tick <= last[sd]:
                g[sd].append([])
            last[sd] = tick
            g[sd][-1].append({"tick": tick, "turn": int(turn), "tomove": int(tomove), "actor": int(actor),
                              "act": act, "s": [s0, s1]})
    return g


recs = [json.loads(l) for l in open(D + "divergences.jsonl", encoding="utf-8")]
alt = [r for r in recs if r["deck"] == "altaria"]
seeds = {r["seed"] for r in alt}
if os.path.exists(OUT):
    base, kpf = pickle.load(open(OUT, "rb"))
else:
    base, kpf = load("dump_base.txt", seeds), load("dump_kpf.txt", seeds)
    pickle.dump((base, kpf), open(OUT, "wb"))

# 1. check the first divergence and which copy
ncopies = Counter((len(base[s]), len(kpf[s])) for s in seeds)
print("copies (base,kpf):", ncopies)
mism = 0
for r in alt:
    x, y = base[r["seed"]][0], kpf[r["seed"]][0]
    k = next((n for n in range(min(len(x), len(y))) if x[n]["act"] != y[n]["act"]), None)
    ok = k is not None and x[k]["tick"] == r["tick"] and x[k]["act"] == r["kp3_act"] and y[k]["act"] == r["kpf_act"]
    # base copies identical?
    if len(base[r["seed"]]) > 1:
        same = [z["act"] for z in base[r["seed"]][0]] == [z["act"] for z in base[r["seed"]][1]]
        if not same:
            print("base copies differ", r["seed"])
        # second kpf copy: where does it diverge, and by whom?
        y2 = kpf[r["seed"]][1]
        k2 = next((n for n in range(min(len(x), len(y2))) if x[n]["act"] != y2[n]["act"]), None)
        kseat = r["kpf_seat"]
        print(f"dup {r['seed']} first-copy div actor={x[k]['actor']} (alt seat {kseat}); second-copy div at "
              f"{k2} actor={x[k2]['actor'] if k2 is not None else None}")
    if not ok:
        mism += 1
        print("MISMATCH", r["seed"], k, r["tick"])
    r["k"] = k
print("mismatches:", mism, "of", len(alt))
pickle.dump(alt, open(D + "workflow_scratch/sk_alt_recs.pkl", "wb"))
