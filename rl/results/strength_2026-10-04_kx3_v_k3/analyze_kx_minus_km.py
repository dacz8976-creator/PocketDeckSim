"""The k3 check's pre-registered reading (written Oct 4 before run A finished; see PREREGISTRATION.md's addendum).

kx3 minus km3, both facing k3, on the same deals: run A's X arm (kx3 on the deck v k3) minus run B's X arm (km3 on the
deck v k3), matched by (deck, opponent, seed, seat). Score: win 1, tie 1/2, loss 0 for the deck. Pooled mean of the
paired difference with mean +- 1.96*sd/sqrt(n), and the same per deck. Also checks that the two runs' reference arms
(k3 v k3) are identical game for game, as they must be.

Run from the repository root: python3 rl/results/strength_2026-10-04_kx3_v_k3/analyze_kx_minus_km.py
"""
import json, math, os, statistics as st, collections

A = "rl/results/strength_2026-10-04_kx3_v_k3/games.jsonl"
B = "rl/results/strength_2026-10-04_km3_v_k3/games.jsonl"
score = {"deck": 1.0, "tie": 0.5, "opp": 0.0}

def load(p):
    g = [json.loads(l) for l in open(p) if l.strip()]
    return {(x["arm"], x["deck"], x["opp"], x["seed"], x["seat"]): x for x in g}

a, b = load(A), load(B)
keys = sorted(k[1:] for k in a if k[0] == "X")
pairs = [(a[("X",) + k], b[("X",) + k]) for k in keys if ("X",) + k in b]
ref_same = sum(1 for k in keys if ("ref",) + k in a and ("ref",) + k in b
               and (a[("ref",) + k]["winner"], a[("ref",) + k]["points"], a[("ref",) + k]["turns"])
               == (b[("ref",) + k]["winner"], b[("ref",) + k]["points"], b[("ref",) + k]["turns"]))
print(f"run A X games {len(keys)}; matched in run B {len(pairs)}; reference arms identical in {ref_same} of {len(keys)}")

def summary(d):
    n = len(d); m = st.mean(d); sd = st.stdev(d) if n > 1 else 0.0
    h = 1.96 * sd / math.sqrt(n) if n > 1 else float("nan")
    return n, 100 * m, 100 * h

d_all = [score[x["winner"]] - score[y["winner"]] for x, y in pairs]
n, m, h = summary(d_all)
kx = 100 * st.mean(score[x["winner"]] for x, _ in pairs); km = 100 * st.mean(score[y["winner"]] for _, y in pairs)
print(f"POOLED kx3 - km3, both v k3: {m:+.1f} +- {h:.1f} points (n={n}); kx3 {kx:.1f}% v km3 {km:.1f}%; "
      f"95% interval {m - h:+.1f} to {m + h:+.1f}")
lo = m - h
print("RULE: " + ("interval above zero -> FREEZE" if lo > 0 else
                  ("interval below zero -> HOLD (kx3 played worse than km3 against k3)" if m + h < 0 else
                   "interval crosses zero -> HOLD the exam, inconclusive")))
byd = collections.defaultdict(list)
for x, y in pairs: byd[x["deck"]].append(score[x["winner"]] - score[y["winner"]])
print("per deck:")
for dk in sorted(byd):
    n, m, h = summary(byd[dk]); print(f"  {dk:40s} n={n:3d} {m:+6.1f} +- {h:5.1f}")
