"""Whole-game counts per species of Zone-attach target, retreats from/to, attacks: kpf - kp3, worse vs better."""
import json, sys
from collections import Counter, defaultdict
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import *

deck = sys.argv[1] if len(sys.argv) > 1 else "altaria"
recs, base, kpf = load_all(deck)


def counts(game, seat, from_turn=0):
    c = Counter()
    for ln in game:
        if ln["actor"] != seat or ln["turn"] < from_turn:
            continue
        d = describe(ln, seat)
        cc = cat(ln["act"])
        if cc.startswith("ATTACH") and "zone" in d:
            c[("zone", cc[8:9], d.split("(")[1].split(",")[0])] += 1
        elif cc == "RETREAT":
            fr, to = d[8:-1].split("->")
            c[("retreat from", fr)] += 1
            c[("retreat to", to)] += 1
        elif cc.startswith("ATTACK"):
            c[("attack", cc[7:])] += 1
    return c


agg = {k: defaultdict(list) for k in ("worse", "better")}
keys = set()
for r in recs:
    gb, gk = base[r["seed"]][0], kpf[r["seed"]][0]
    annotate(gb); annotate(gk)
    seat = r["kpf_seat"]
    k = next(n for n in range(min(len(gb), len(gk))) if gb[n]["act"] != gk[n]["act"])
    t = gb[k]["turn"]
    cb, ck = counts(gb, seat, t), counts(gk, seat, t)
    keys |= set(cb) | set(ck)
    agg[r["kind"]]["_games"].append(1)
    for key in set(cb) | set(ck):
        agg[r["kind"]][key].append(ck[key] - cb[key])
    agg[r["kind"]][("_basecount",) + tuple()].append(0)
    for key in cb:
        agg[r["kind"]][("base",) + key].append(cb[key])

n = {k: len(agg[k]["_games"]) for k in agg}
print("from the divergence turn on; mean per game of (kpf - kp3); worse n=%d better n=%d" % (n["worse"], n["better"]))
rows = []
for key in sorted(keys, key=str):
    w = sum(agg["worse"].get(key, [])) / n["worse"]
    b = sum(agg["better"].get(key, [])) / n["better"]
    bw = sum(agg["worse"].get(("base",) + key, [])) / n["worse"]
    bb = sum(agg["better"].get(("base",) + key, [])) / n["better"]
    # se of the difference of means
    def se(xs, N):
        xs = xs + [0] * (N - len(xs))
        m = sum(xs) / N
        return (sum((x - m) ** 2 for x in xs) / (N - 1) / N) ** 0.5
    s = (se(agg["worse"].get(key, []), n["worse"]) ** 2 + se(agg["better"].get(key, []), n["better"]) ** 2) ** 0.5
    rows.append((key, w, b, bw, bb, s))
for key, w, b, bw, bb, s in sorted(rows, key=lambda x: -abs(x[1] - x[2]) / (x[5] or 1)):
    print(f"  {str(key):55} worse {w:+.2f} better {b:+.2f}  (w-b)/se={(w - b) / (s or 1):+.2f}   kp3 base worse {bw:.2f} better {bb:.2f}")
