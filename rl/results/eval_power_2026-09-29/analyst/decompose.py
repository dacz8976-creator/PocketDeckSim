"""Variance decomposition of the 45-cell dMSE (score45.py's statistic) into the simulator side and the Limitless side.
dMSE = 1e4/K * sum_k [(N_k-L_k)^2 - (O_k-L_k)^2]   (N new, O current, L Limitless; fractions; K = 45)
It is EXACTLY linear in L_k:  dMSE_k = d_k*(N_k+O_k-2L_k), d_k = N_k-O_k, so the Limitless side enters only through d_k.
Delta method (first order):
  sim side  : Var_k = Var_i[ 2e4/K * ((N_k-L_k)*N_ki - (O_k-L_k)*O_ki) ] / n_k        (paired by deal; cells independent)
  Limitless : Var_k = (2e4/K * d_k)^2 * L_k(1-L_k)/nL_k                                (binomial, score.py's own model)
and a resampling check that mimics score.py's bootstrap (multinomial over the joint (o,n) categories of a cell's deals is
exactly resampling deals with replacement) with the sim side only, the Limitless side only (binomial; by event), and both.
usage: decompose.py <reading> [reps]"""
import sys, json, math, random, collections
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *

OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst/"


def pct(v, q):
    return v[min(len(v) - 1, max(0, int(q * len(v))))]


def prep_cells(pairs, deals):
    """per cell: category values and 'ratio' probabilities for sequential-binomial multinomial draws"""
    P = {}
    for k in pairs:
        c = collections.Counter(deals[k])
        items = sorted(c.items())
        n = len(deals[k])
        vo = [o for (o, x), _ in items]
        vn = [x for (o, x), _ in items]
        ratios, rem = [], 1.0
        for _, cnt in items:
            p = cnt / n
            ratios.append(min(1.0, p / rem) if rem > 1e-12 else 1.0)
            rem -= p
        P[k] = (n, vo, vn, ratios)
    return P


def draw_sim(rng, cell):
    n, vo, vn, ratios = cell
    rem, so, sn = n, 0.0, 0.0
    last = len(vo) - 1
    for j in range(last):
        if rem == 0:
            break
        kk = rng.binomialvariate(rem, ratios[j])
        so += kk * vo[j]; sn += kk * vn[j]; rem -= kk
    so += rem * vo[last]; sn += rem * vn[last]
    return so / n, sn / n


def analytic(pairs, lim, deals):
    K = len(pairs)
    O, N, L, nL, n = cell_stats(pairs, lim, deals)
    rows = {}
    for k in pairs:
        d = deals[k]
        nk = n[k]
        # linear form per deal
        z = [2e4 / K * ((N[k] - L[k]) * x - (O[k] - L[k]) * o) for o, x in d]
        m = sum(z) / nk
        vs = sum((v - m) ** 2 for v in z) / (nk - 1) / nk
        dk = N[k] - O[k]
        vl = (2e4 / K * dk) ** 2 * L[k] * (1 - L[k]) / nL[k]
        # descriptive: paired difference
        Dv = [x - o for o, x in d]
        mD = sum(Dv) / nk
        varD = sum((v - mD) ** 2 for v in Dv) / (nk - 1)
        flips = sum(1 for o, x in d if o != x) / nk
        vc = (2e4 / K) ** 2 * (varD / nk) * L[k] * (1 - L[k]) / nL[k]  # second-order cross term: sim noise in d_k x Limitless noise
        vo = sum((o - O[k]) ** 2 for o, _ in d) / (nk - 1)
        rows[k] = dict(O=O[k], N=N[k], L=L[k], nL=nL[k], n=nk, d=dk, e_cur=O[k] - L[k], e_new=N[k] - L[k],
                       contrib=1e4 / K * ((N[k] - L[k]) ** 2 - (O[k] - L[k]) ** 2), var_sim=vs, var_lim=vl, var_cross=vc,
                       varD=varD, varO=vo, flips=flips)
    return rows


def bootstrap(pairs, lim, deals, events, reps, seed=12345):
    K = len(pairs)
    O, N, L0, nL, n = cell_stats(pairs, lim, deals)
    P = prep_cells(pairs, deals)
    rng = random.Random(seed)
    rng_e = random.Random(seed + 1)
    evW = [[(e.get(k, (0, 0, 0))[0] + 0.5 * e.get(k, (0, 0, 0))[2]) for k in pairs] for e in events]
    evN = [[sum(e.get(k, (0, 0, 0))) for k in pairs] for e in events]
    ne = len(events)
    idx = range(K)
    Ol = [O[k] for k in pairs]; Nl = [N[k] for k in pairs]; Ll = [L0[k] for k in pairs]
    res = {m: [] for m in ("both", "sim", "lim", "both_ev", "lim_ev")}
    redrawn = 0

    def f(Nv, Ov, Lv):
        return sum((Nv[j] - Lv[j]) ** 2 - (Ov[j] - Lv[j]) ** 2 for j in idx) / K * 1e4

    for _ in range(reps):
        Ls = [rng.binomialvariate(nL[k], L0[k]) / nL[k] for k in pairs]
        Os, Ns = [], []
        for k in pairs:
            a, b = draw_sim(rng, P[k])
            Os.append(a); Ns.append(b)
        while True:
            pick = [rng_e.randrange(ne) for _ in range(ne)]
            tw = [0.0] * K; tn = [0] * K
            for e in pick:
                w, nn = evW[e], evN[e]
                for j in idx:
                    tw[j] += w[j]; tn[j] += nn[j]
            if all(tn):
                break
            redrawn += 1
        LE = [tw[j] / tn[j] for j in idx]
        res["both"].append(f(Ns, Os, Ls))
        res["sim"].append(f(Ns, Os, Ll))
        res["lim"].append(f(Nl, Ol, Ls))
        res["both_ev"].append(f(Ns, Os, LE))
        res["lim_ev"].append(f(Nl, Ol, LE))
    return res, redrawn


def moments(v):
    n = len(v)
    m = sum(v) / n
    var = sum((x - m) ** 2 for x in v) / (n - 1)
    sd = math.sqrt(var)
    sk = sum((x - m) ** 3 for x in v) / n / sd ** 3
    return m, var, sd, sk


def main():
    name = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    pairs, lim = load_limitless()
    events = load_events(pairs, lim)
    op, np_, on, nn = readings()[name]
    deals = load_reading(op, np_, pairs)
    O, N, L, nL, n = cell_stats(pairs, lim, deals)
    K = len(pairs)
    pt = dmse_point(pairs, O, N, L)
    rows = analytic(pairs, lim, deals)
    vs = sum(r["var_sim"] for r in rows.values())
    vl = sum(r["var_lim"] for r in rows.values())
    vc = sum(r["var_cross"] for r in rows.values())
    print(f"=== {name}: {nn} (new) vs {on} (current), K = {K} cells, 500 deals/cell, Limitless n = {sum(nL.values())}")
    print(f"point dMSE {pt:+.1f}  tau {on} {S.tau(O, n, L, nL, pairs):.2f} -> {nn} {S.tau(N, n, L, nL, pairs):.2f}")
    print(f"ANALYTIC (delta method): var_sim {vs:.1f} (sd {math.sqrt(vs):.2f}), var_lim {vl:.1f} (sd {math.sqrt(vl):.2f}), cross {vc:.1f}; "
          f"total sd {math.sqrt(vs + vl + vc):.2f}; Limitless share of variance {100 * vl / (vs + vl + vc):.1f}%; "
          f"95% half-width sim-only {1.96 * math.sqrt(vs):.1f}, Limitless-only {1.96 * math.sqrt(vl):.1f}, both {1.96 * math.sqrt(vs + vl + vc):.1f}")
    fl = sum(r["flips"] for r in rows.values()) / K
    vD = sum(r["varD"] for r in rows.values()) / K
    print(f"paired difference per deal: share of deals whose score differs {100 * fl:.0f}% (mean over cells); mean var(D) {vD:.3f} => sd {100 * math.sqrt(vD):.0f} points per deal")
    res, redrawn = bootstrap(pairs, lim, deals, events, reps)
    out = {"name": name, "new": nn, "old": on, "point": pt, "tau_old": S.tau(O, n, L, nL, pairs), "tau_new": S.tau(N, n, L, nL, pairs),
           "analytic": {"var_sim": vs, "var_lim": vl, "var_cross": vc}, "boot": {}, "cells": {f"{k[0]}|{k[1]}": v for k, v in rows.items()}}
    print(f"BOOTSTRAP ({reps} reps; multinomial resampling of deals; event redraws {redrawn}):")
    for m, label in (("both", "both sides (binomial Limitless)   "), ("sim", "simulator side only              "), ("lim", "Limitless side only (binomial)  "),
                     ("both_ev", "both sides (Limitless by event)  "), ("lim_ev", "Limitless side only (by event)   ")):
        v = sorted(res[m])
        mean, var, sd, sk = moments(v)
        lo, hi = pct(v, 0.025), pct(v, 0.975)
        print(f"  {label}: mean {mean:+7.2f} sd {sd:6.2f} var {var:8.1f} skew {sk:+.2f}  95% interval {lo:+7.1f} to {hi:+7.1f} (width {hi - lo:.1f})")
        out["boot"][m] = dict(mean=mean, var=var, sd=sd, skew=sk, lo=lo, hi=hi)
    vb = out["boot"]
    print(f"  additivity check: var_sim + var_lim = {vb['sim']['var'] + vb['lim']['var']:.1f} vs var_both = {vb['both']['var']:.1f} (the gap is the cross term, analytic {vc:.1f}); "
          f"(by event: {vb['sim']['var'] + vb['lim_ev']['var']:.1f} vs {vb['both_ev']['var']:.1f})")
    print(f"  Limitless share of variance: binomial {100 * vb['lim']['var'] / vb['both']['var']:.1f}%, by event {100 * vb['lim_ev']['var'] / vb['both_ev']['var']:.1f}%")
    # per-cell table
    print("PER CELL (sorted by total variance; sd_sim, sd_lim = that side's sd of the cell's part of dMSE, in points^2): d = new-cur (pts), e_cur = cur-Limitless miss (pts), contrib = the cell's part of the point dMSE")
    print("  cell                              d     e_cur   contrib   sd_sim  sd_lim   Lim share  larger side")
    order = sorted(pairs, key=lambda k: -(rows[k]["var_sim"] + rows[k]["var_lim"]))
    simdom = limdom = 0
    for k in order:
        r = rows[k]
        tot = r["var_sim"] + r["var_lim"]
        share = r["var_lim"] / tot if tot > 0 else 0.0
        side = "none (identical games)" if tot == 0 else ("Limitless" if r["var_lim"] > r["var_sim"] else "simulator")
        simdom += side == "simulator"
        limdom += side == "Limitless"
        print(f"  {k[0] + ' v ' + k[1]:<32}{100 * r['d']:+7.1f} {100 * r['e_cur']:+8.1f} {r['contrib']:+9.1f} {math.sqrt(r['var_sim']):8.2f} {math.sqrt(r['var_lim']):7.2f} {100 * share:9.0f}%  {side}")
    print(f"  cells where the simulator side has the larger variance: {simdom} of {K}; Limitless: {limdom}; neither (the two pilots played identical games and the rate did not move): {K - simdom - limdom}")
    json.dump(out, open(OUT + f"decomp_{name}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
