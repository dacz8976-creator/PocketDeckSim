"""Second reader: the mixed rows' attribution numbers in kpr3_paired_reading.md, section 4 (own code).
Per cell: table change (kpr3 both sides - kp3 both sides, first deck's score), each deck's own side (kpr3 on that deck
only, that deck's score, minus kp3 v kp3 on the same deal), interaction. 95% half-width = 1.96 * sd / sqrt(n) of the
per-deal differences. Per deck: stratified over its cells (mean of cell means; variance of the mean summed / cells^2)."""
import math
import numpy as np
from check_common import PAIRS, NAMES, QUAR, KP3, KPR3, MIX1, MIX2, load, score

kp3 = load(KP3, ("kp3", "kp3"))
kpr3 = load(KPR3, ("kpr3", "kpr3"))
m1 = load(MIX1, ("kpr3", "kp3"))       # kpr3 on the first-named deck
m2 = load(MIX2, ("kp3", "kpr3"))       # kpr3 on the second-named deck
for t in (kp3, kpr3, m1, m2):
    assert set(t) == set(PAIRS) and all(sorted(t[k]) == list(range(500)) for k in PAIRS)


def v(t, k):
    return np.array([score(t[k][i]) for i in range(500)])


def mh(d):
    return d.mean(), 1.96 * d.std(ddof=1) / math.sqrt(len(d)), d.var(ddof=1) / len(d)


def pool(parts):
    ms = [mh(d) for d in parts]
    return np.mean([m for m, _, _ in ms]), 1.96 * math.sqrt(sum(x for _, _, x in ms)) / len(ms)


cell = {}
for k in PAIRS:
    base, tab, f, s = v(kp3, k), v(kpr3, k), v(m1, k), v(m2, k)
    cell[k] = {"table": 100 * (tab - base),                          # first deck's score
               k[0]: 100 * (f - base),                               # first deck's own side, first deck's score
               k[1]: -100 * (s - base),                              # second deck's own side, second deck's score
               "inter": 100 * ((tab - base) - (f - base) - (s - base))}   # first deck's view
print("== per cell: table change (first deck) | first deck's side | second deck's side | interaction (first deck's view)")
beyond = {"better": [], "worse": []}
for k in PAIRS:
    c = cell[k]
    parts = []
    for key in ("table", k[0], k[1], "inter"):
        m, h, _ = mh(c[key])
        parts.append(f"{m:+5.1f} +/- {h:3.1f}")
        if key in k:
            if m > h:
                beyond["better"].append((key, k))
            elif m < -h:
                beyond["worse"].append((key, k))
    print(f"  {k[0]:>9} v {k[1]:<10} " + " | ".join(parts) + ("  (quarantined)" if k == QUAR else ""))
for w in ("better", "worse"):
    cnt = {}
    for d, _ in beyond[w]:
        cnt[d] = cnt.get(d, 0) + 1
    print(f"  cell sides {w} beyond noise: {len(beyond[w])}: {cnt}")
print("  cell sides within 0.15 of their noise bound (4 decimals):")
for k in PAIRS:
    for d in k:
        m, h, _ = mh(cell[k][d])
        if abs(abs(m) - h) < 0.15:
            print(f"    {k[0]} v {k[1]}, {d}'s side: {m:+.4f} +/- {h:.4f} -> {'beyond' if abs(m) > h else 'within'}")


def deck_rows(keys, label):
    print(f"== per deck, {label}: table change | own side | opponents' side (their own score) | interaction (deck's view)")
    out = {}
    for d in NAMES:
        dk = [k for k in keys if d in k]
        tab, own, opp, inter = [], [], [], []
        for k in dk:
            o = k[1] if k[0] == d else k[0]
            sgn = 1 if k[0] == d else -1
            tab.append(sgn * cell[k]["table"])
            own.append(cell[k][d])
            opp.append(cell[k][o])
            inter.append(sgn * cell[k]["inter"])
        r = {n: pool(p) for n, p in (("table", tab), ("own", own), ("opp", opp), ("inter", inter))}
        out[d] = r
        flag = lambda m, h: " better" if m > h else (" worse" if m < -h else "")  # noqa: E731
        print(f"  {d:>9} ({len(dk)} cells): table {r['table'][0]:+5.1f} +/- {r['table'][1]:3.1f}{flag(*r['table'])} | own "
              f"{r['own'][0]:+5.1f} +/- {r['own'][1]:3.1f}{flag(*r['own'])} | opp {r['opp'][0]:+5.1f} +/- {r['opp'][1]:3.1f}"
              f"{flag(*r['opp'])} | inter {r['inter'][0]:+5.1f} +/- {r['inter'][1]:3.1f}{flag(*r['inter'])} | check: own - opp "
              f"+ inter = {r['own'][0] - r['opp'][0] + r['inter'][0]:+.2f}")
    return out


allrows = deck_rows(PAIRS, "all 28 cells")
deck_rows([k for k in PAIRS if k != QUAR], "decision set (27 cells)")

# Hydreigon's share: own side / table change.
h = allrows["hydreigon"]
print(f"== Hydreigon: own {h['own'][0]:+.2f} of table {h['table'][0]:+.2f} = {h['own'][0] / h['table'][0]:.2f}; "
      f"inter {h['inter'][0]:+.2f}")

# Head to head: kpr3's own score in all 28,000 mixed games, and the pooled change over the 56 cell sides.
sc = [score(m1[k][i]) for k in PAIRS for i in range(500)] + [1 - score(m2[k][i]) for k in PAIRS for i in range(500)]
base = [score(kp3[k][i]) for k in PAIRS for i in range(500)] + [1 - score(kp3[k][i]) for k in PAIRS for i in range(500)]
sides = [cell[k][k[0]] for k in PAIRS] + [cell[k][k[1]] for k in PAIRS]
m, hw = pool(sides)
print(f"== head to head: kpr3 scores {100 * np.mean(sc):.2f}% over {len(sc)} mixed games (kp3 v kp3 same deals, same sides "
      f"{100 * np.mean(base):.2f}%); pooled change over {len(sides)} cell sides {m:+.2f} +/- {hw:.2f}")
