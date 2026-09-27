# Synthesis agent: exact two-sided binomial (p=0.5) for pooled worse/better splits.
from math import comb

def two_sided(k, n):
    lo = min(k, n - k)
    tail = sum(comb(n, i) for i in range(0, lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)

for label, w, b in [
    ("unevolved Basic fed/kept in front (Altaria 15/3 + Lucario bare Riolu 24/11 + Vespiquen Combee 9/2)", 15 + 24 + 9, 3 + 11 + 2),
    ("same, Altaria widened 23/12 instead of 15/3", 23 + 24 + 9, 12 + 11 + 2),
    ("attacker moved up by the clock channel (Altaria Darkrai 4/1 + Lucario evolved 34/24 + Vespiquen P2 14/7)", 4 + 34 + 14, 1 + 24 + 7),
    ("Altaria retreat-then-feed 31/14", 31, 14),
    ("Lucario forward 58 vs 35", 58, 35),
]:
    print(f"{label}: {w}/{b}  two-sided p = {two_sided(w, w + b):.2g}")
