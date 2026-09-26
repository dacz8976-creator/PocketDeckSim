"""Second reader: the decision line of kpr3_paired_reading.md, recomputed with numpy (own code, own random stream).
Point estimates: MSE, real error (tau), favorites right, correlation, PASS parts, deck gaps, cell misses.
Intervals: paired deal bootstrap (multinomial counts per cell, the same draw for both bots), Limitless binomial and by
event (58 events redrawn with replacement; a draw with an empty cell is redrawn). 10,000 replicates."""
import math
import numpy as np
from check_common import (PAIRS, NAMES, QUAR, KP3, KPR3, K3, load, score, lim_v2, lim_s23, events_v2, frac)

R = 10_000
kp3 = load(KP3, ("kp3", "kp3"))
kpr3 = load(KPR3, ("kpr3", "kpr3"))
k3 = load(K3, ("k3", "k3"))
for t in (kp3, kpr3, k3):
    assert set(t) == set(PAIRS) and all(sorted(t[k]) == list(range(500)) for k in PAIRS)
arr = {name: {k: np.array([score(t[k][i]) for i in range(500)]) for k in PAIRS}
       for name, t in (("k3", k3), ("kp3", kp3), ("kpr3", kpr3))}
S = {name: {k: v.mean() for k, v in a.items()} for name, a in arr.items()}


def mse(Sb, L, keys):
    return 1e4 * np.mean([(Sb[k] - L[k][0]) ** 2 for k in keys])


def tau_pt(Sb, L, keys, nS=500):
    acc = np.mean([(Sb[k] - L[k][0]) ** 2 - L[k][0] * (1 - L[k][0]) / L[k][1] - Sb[k] * (1 - Sb[k]) / nS for k in keys])
    return 100 * math.sqrt(max(0.0, acc))


def pearson(x, y):
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


def fav(Sb, L, keys):
    return sum(1 for k in keys if (Sb[k] - 0.5) * (L[k][0] - 0.5) > 0)


def pass_b(Sb, L, keys):
    out = []
    for k in keys:
        p, n = L[k]
        if 100 * (abs(Sb[k] - p) - 1.96 * math.sqrt(p * (1 - p) / n + Sb[k] * (1 - Sb[k]) / 500)) > 10:
            out.append(f"{k[0]} v {k[1]}")
    return out


def deck_avg(Sb, keys):
    t = {}
    for a, b in keys:
        t.setdefault(a, []).append(Sb[(a, b)])
        t.setdefault(b, []).append(1 - Sb[(a, b)])
    return {d: np.mean(v) for d, v in t.items()}


def boot(old, new, Lraw, keys, seed, events=None):
    rng = np.random.default_rng(seed)
    L = {k: frac(Lraw[k]) for k in keys}
    Os, Ns, Ls, nL = [], [], [], []
    for k in keys:
        cnt = rng.multinomial(500, np.full(500, 1 / 500), size=R)
        Os.append(cnt @ arr[old][k] / 500)
        Ns.append(cnt @ arr[new][k] / 500)
        p, n = L[k]
        Ls.append(rng.binomial(n, p, size=R) / n)
        nL.append(np.full(R, n))
    Os, Ns, Ls, nL = map(np.array, (Os, Ns, Ls, nL))            # cells x R

    def dm(Lx):
        return 1e4 * np.mean((Ns - Lx) ** 2 - (Os - Lx) ** 2, axis=0)

    def tau(Sx, Lx, nx):
        return 100 * np.sqrt(np.maximum(0, np.mean((Sx - Lx) ** 2 - Lx * (1 - Lx) / nx - Sx * (1 - Sx) / 500, axis=0)))

    res = {"dmse_bin": np.percentile(dm(Ls), [2.5, 97.5]),
           "tau_bin": np.percentile(tau(Os, Ls, nL) - tau(Ns, Ls, nL), [5, 95])}
    if events is not None:
        E = np.array([[e.get(k, (0, 0, 0)) for k in keys] for e in events], dtype=float)   # events x cells x 3
        tot = E.sum(axis=0)
        assert all(tuple(tot[j].astype(int)) == tuple(Lraw[k]) for j, k in enumerate(keys)), "events do not sum to cells"
        rng_e = np.random.default_rng(seed + 1)
        LE, nE, redrawn, filled = np.zeros((len(keys), R)), np.zeros((len(keys), R)), 0, 0
        while filled < R:
            idx = rng_e.integers(0, len(events), size=len(events))
            c = E[idx].sum(axis=0)
            n = c.sum(axis=1)
            if (n == 0).any():
                redrawn += 1
                continue
            LE[:, filled] = (c[:, 0] + 0.5 * c[:, 2]) / n
            nE[:, filled] = n
            filled += 1
        res["dmse_ev"] = np.percentile(dm(LE), [2.5, 97.5])
        res["tau_ev"] = np.percentile(tau(Os, LE, nE) - tau(Ns, LE, nE), [5, 95])
        res["redrawn"] = redrawn
    return res


def f(x, d=1):
    return f"{x:+.{d}f}"


def report(title, old, new, Lraw, keys, seed, events=None, bots=("k3", "kp3", "kpr3")):
    L = {k: frac(Lraw[k]) for k in keys}
    print(f"== {title}: {len(keys)} cells, {new} against {old}")
    for b in bots:
        print(f"  {b:>5}: MSE {mse(S[b], L, keys):6.1f} | tau {tau_pt(S[b], L, keys):5.2f} | favorites right "
              f"{fav(S[b], L, keys)}/{len(keys)} | correlation {pearson([S[b][k] for k in keys], [L[k][0] for k in keys]):.2f}"
              f" | mean |miss| {100 * np.mean([abs(S[b][k] - L[k][0]) for k in keys]):.2f}")
        dl, ds = deck_avg({k: L[k][0] for k in keys}, keys), deck_avg(S[b], keys)
        off = sorted(d for d in dl if abs(ds[d] - dl[d]) * 100 > 6)
        print(f"         PASS (b) cells over by >10 beyond noise: {', '.join(pass_b(S[b], L, keys)) or 'none'} | (c) decks off"
              f" by >6: {', '.join(off) or 'none'}")
    d_pt = mse(S[new], L, keys) - mse(S[old], L, keys)
    t_pt = tau_pt(S[old], L, keys) - tau_pt(S[new], L, keys)
    b = boot(old, new, Lraw, keys, seed, events)
    print(f"  dMSE {new} - {old}: {f(d_pt)}; 95% binomial {f(b['dmse_bin'][0])} to {f(b['dmse_bin'][1])}"
          + (f"; by event {f(b['dmse_ev'][0])} to {f(b['dmse_ev'][1])} ({b['redrawn']} event draws redrawn)" if events else ""))
    print(f"  tau margin {old} - {new}: {f(t_pt, 2)}; 90% binomial {f(b['tau_bin'][0], 2)} to {f(b['tau_bin'][1], 2)}"
          + (f"; by event {f(b['tau_ev'][0], 2)} to {f(b['tau_ev'][1], 2)}" if events else ""))
    return L


v2, s23 = lim_v2(), lim_s23()
ev = events_v2()
dec = [k for k in PAIRS if k != QUAR]
print(f"inputs: kp3 {sum(len(c) for c in kp3.values())} games, kpr3 {sum(len(c) for c in kpr3.values())}, "
      f"k3 {sum(len(c) for c in k3.values())}; v2 cells {len(v2)}, {sum(sum(v) for v in v2.values())} matches; "
      f"events {len(ev)}")
L = report("scoreboard v2, decision set", "kp3", "kpr3", v2, dec, 7_000_001, ev)
report("scoreboard v2, all 28", "kp3", "kpr3", v2, PAIRS, 7_000_002, ev)
report("Sept 23 cells, decision set", "kp3", "kpr3", s23, dec, 7_000_003)
report("Sept 23 cells, all 28", "kp3", "kpr3", s23, PAIRS, 7_000_004)
report("scoreboard v2, decision set, against k3", "k3", "kpr3", v2, dec, 7_000_005, ev)
report("scoreboard v2, decision set, kp3 against k3 (for 'kp3 was -45.8')", "k3", "kp3", v2, dec, 7_000_006, ev)

# Rounded Sept 23 cells (one decimal of a percent), all 28: the cloud's 176.1 / 112.2 / 159.3.
Lr = {k: round(100 * frac(s23[k])[0], 1) / 100 for k in PAIRS}
print("== Sept 23 cells rounded to one decimal, all 28: MSE " +
      ", ".join(f"{b} {1e4 * np.mean([(S[b][k] - Lr[k]) ** 2 for k in PAIRS]):.1f}" for b in ("k3", "kp3", "kpr3")))

# Cell misses and vetoes on the v2 decision set.
print("== v2 decision set: cells (kp3 | kpr3 | Limitless +/- 95% | change in miss)")
for k in dec:
    p, n = frac(v2[k])
    g = 100 * (abs(S["kpr3"][k] - p) - abs(S["kp3"][k] - p))
    print(f"  {k[0]:>9} v {k[1]:<10} {100 * S['kp3'][k]:5.1f} | {100 * S['kpr3'][k]:5.1f} | {100 * p:5.1f} +/- "
          f"{196 * math.sqrt(p * (1 - p) / n):4.1f} | {g:+.2f}{'  CELL VETO CANDIDATE' if g > 6 else ''}")
p, n = frac(v2[QUAR])
print(f"  (quarantined) altaria v sceptile {100 * S['kp3'][QUAR]:5.1f} | {100 * S['kpr3'][QUAR]:5.1f} | {100 * p:5.1f} +/- "
      f"{196 * math.sqrt(p * (1 - p) / n):4.1f}")
Ld = {k: frac(v2[k])[0] for k in dec}
dl, do, dn = deck_avg(Ld, dec), deck_avg(S["kp3"], dec), deck_avg(S["kpr3"], dec)
print("== v2 decision set: deck averages kp3 / kpr3 / Limitless, gap change")
for d in NAMES:
    g = 100 * (abs(dn[d] - dl[d]) - abs(do[d] - dl[d]))
    print(f"  {d:>9}: {100 * do[d]:5.1f} / {100 * dn[d]:5.1f} / {100 * dl[d]:5.1f}  {g:+.2f}{'  DECK VETO CANDIDATE' if g > 2 else ''}")
