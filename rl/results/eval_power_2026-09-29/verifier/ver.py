#!/usr/bin/env python3
"""Independent check of the 45-cell dMSE power analysis (verifier).  Read-only: loads files, prints numbers.
Usage: ver.py <reading> <mode[,mode...]>   modes: analytic, mc, brute, floor, mde
"""
import csv, itertools, json, math, random, sys, time
from operator import itemgetter

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results"
KOG = f"{R}/kog_composition_2026-09-27"
KPF = f"{R}/kpf_2026-09-26/reading"
KOH = "/tmp/koh_cloud"
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
PAIRS28 = list(itertools.combinations(NAMES, 2))
NEWD = ["rayquaza", "altaria_greninja"]
NEW17 = [(d, o) for d in NEWD for o in NAMES] + [("rayquaza", "altaria_greninja")]
KEYS = PAIRS28 + NEW17
K = len(KEYS)
assert K == 45

READ = {
    "koh3_vs_kog3": ([f"{KOG}/table_kog3.jsonl", f"{KOG}/new17_kog3.jsonl"], [f"{KOH}/table_koh3.jsonl", f"{KOH}/new17_koh3.jsonl"]),
    "kog3_vs_kp3": ([f"{KPF}/table_kp3.jsonl", f"{KPF}/new17_kp3.jsonl"], [f"{KOG}/table_kog3.jsonl", f"{KOG}/new17_kog3.jsonl"]),
    "kpf3_vs_kp3": ([f"{KPF}/table_kp3.jsonl", f"{KPF}/new17_kp3.jsonl"], [f"{KPF}/table_kpf3.jsonl", f"{KPF}/new17_kpf3.jsonl"]),
    "kpg3_vs_kp3": ([f"{KPF}/table_kp3.jsonl", f"{KPF}/new17_kp3.jsonl"], [f"{KPF}/table_kpg3.jsonl", f"{KPF}/new17_kpg3.jsonl"]),
    "kog3_vs_kpg3": ([f"{KPF}/table_kpg3.jsonl", f"{KPF}/new17_kpg3.jsonl"], [f"{KOG}/table_kog3.jsonl", f"{KOG}/new17_kog3.jsonl"]),
    "kpr3_vs_kp3": ([f"{KPF}/table_kp3.jsonl", f"{KPF}/new17_kp3.jsonl"], [f"{KPF}/table_kpr3.jsonl", f"{KPF}/new17_kpr3.jsonl"]),
}


def load_L():
    v2 = json.load(open(f"{R}/scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]
    cells = {tuple(k.split("|")): tuple(v) for k, v in v2.items()}
    assert len(cells) == 28 and set(cells) == set(PAIRS28)
    rows = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(open(f"{R}/gauntlet_runs_2026-09-26/gauntlet_cells.csv", encoding="utf-8", newline=""))}
    for a, b in NEW17:
        r = rows[("development", a, b)]
        cells[(a, b)] = (int(r["W"]), int(r["L"]), int(r["T"]))
    return cells


def load_games(paths):
    out, seeds = {}, {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = (r["a"], r["b"]) if "a" in r else PAIRS28[r["pairing"]]
            out.setdefault(k, {})[r["i"]] = float(r["first_deck_score"])
            seeds.setdefault(k, {})[r["i"]] = r.get("seed")
    return out, seeds


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def pct(v, q):
    return v[min(len(v) - 1, max(0, int(q * len(v))))]


def svar(sumx, sumxx, n):
    return (sumxx - sumx * sumx / n) / (n - 1)


class Data:
    pass


def build(name):
    Lc = load_L()
    (op, np_) = READ[name]
    og, os_ = load_games(op)
    ng, ns_ = load_games(np_)
    d = Data()
    d.keys = KEYS
    d.W = {k: Lc[k] for k in KEYS}
    d.nL = {k: sum(Lc[k]) for k in KEYS}
    d.L = {k: (Lc[k][0] + 0.5 * Lc[k][2]) / d.nL[k] for k in KEYS}
    d.Ov, d.Nv = {}, {}
    for k in KEYS:
        deals = sorted(set(og[k]) & set(ng[k]))
        for i in deals:
            assert os_[k][i] == ns_[k][i], (k, i)
        d.Ov[k] = [og[k][i] for i in deals]
        d.Nv[k] = [ng[k][i] for i in deals]
    d.n = {k: len(d.Ov[k]) for k in KEYS}
    d.O = {k: sum(d.Ov[k]) / d.n[k] for k in KEYS}
    d.N = {k: sum(d.Nv[k]) / d.n[k] for k in KEYS}
    return d


def dmse(d, N, O, L):
    return sum((N[k] - L[k]) ** 2 - (O[k] - L[k]) ** 2 for k in KEYS) / K * 1e4


def tau(S, nS, L, nL):
    acc = sum((S[k] - L[k]) ** 2 - L[k] * (1 - L[k]) / nL[k] - S[k] * (1 - S[k]) / nS[k] for k in KEYS)
    return 100 * math.sqrt(max(0.0, acc / K))


def cell_var(d, k):
    """Analytic per-cell variance components of the cell's contribution (fractions^2 of the sum; divide by K^2 later)."""
    n = d.n[k]
    Nv, Ov = d.Nv[k], d.Ov[k]
    N, O, L = d.N[k], d.O[k], d.L[k]
    g = [(N - L) * a - (O - L) * b for a, b in zip(Nv, Ov)]
    mg = sum(g) / n
    vg = sum((x - mg) ** 2 for x in g) / (n - 1)
    D = [a - b for a, b in zip(Nv, Ov)]
    mD = sum(D) / n
    vD = sum((x - mD) ** 2 for x in D) / (n - 1)
    vL = L * (1 - L) / d.nL[k]
    dd = N - O
    return dict(sim=4 * vg / n, lim=4 * dd * dd * vL, cross=4 * (vD / n) * vL, vD=vD, ndiff=sum(1 for x in D if x != 0) / n)


def analytic(d, tag):
    print(f"\n### ANALYTIC {tag}")
    Kf = float(K)
    pt = dmse(d, d.N, d.O, d.L)
    tN, tO = tau(d.N, d.n, d.L, d.nL), tau(d.O, d.n, d.L, d.nL)
    print(f"deals per cell: min {min(d.n.values())} max {max(d.n.values())}; Limitless matches total {sum(d.nL.values())} (28 table cells {sum(d.nL[k] for k in PAIRS28)}, 17 new {sum(d.nL[k] for k in NEW17)}); min cell n {min(d.nL.values())}")
    print(f"dMSE point {pt:+.2f}; tau old {tO:.2f}, tau new {tN:.2f}; tau^2 old {tO**2:.1f}, new {tN**2:.1f}, diff {tN**2 - tO**2:+.1f}")
    cv = {k: cell_var(d, k) for k in KEYS}
    S = sum(c["sim"] for c in cv.values()) / Kf**2 * 1e8
    Lm = sum(c["lim"] for c in cv.values()) / Kf**2 * 1e8
    X = sum(c["cross"] for c in cv.values()) / Kf**2 * 1e8
    tot = S + Lm + X
    print(f"variance points^4: sim {S:.1f} (sd {math.sqrt(S):.2f}), Limitless {Lm:.1f} (sd {math.sqrt(Lm):.2f}), cross {X:.1f} (sd {math.sqrt(X):.2f}); total {tot:.1f} sd {math.sqrt(tot):.2f}")
    print(f"Limitless share of total variance {100*Lm/tot:.1f}%; sim share {100*S/tot:.1f}%; cross {100*X/tot:.1f}%; Limitless share of (sim+Limitless) {100*Lm/(S+Lm):.1f}%")
    print(f"half-width both {1.96*math.sqrt(tot):.1f}; sim only {1.96*math.sqrt(S):.1f}; Limitless only {1.96*math.sqrt(Lm):.1f}; sim+cross {1.96*math.sqrt(S+X):.1f}")
    print(f"interval both {pt-1.96*math.sqrt(tot):+.1f} to {pt+1.96*math.sqrt(tot):+.1f}; sim-only {pt-1.96*math.sqrt(S):+.1f} to {pt+1.96*math.sqrt(S):+.1f}; Limitless-only {pt-1.96*math.sqrt(Lm):+.1f} to {pt+1.96*math.sqrt(Lm):+.1f}")
    # per cell
    rows = []
    for k in KEYS:
        s = math.sqrt(cv[k]["sim"]) / Kf * 1e4
        l = math.sqrt(cv[k]["lim"]) / Kf * 1e4
        rows.append((k, s, l, cv[k]["lim"] / Kf**2 * 1e8, cv[k]["sim"] / Kf**2 * 1e8, 100 * (d.N[k] - d.O[k])))
    nsl = sum(1 for r in rows if r[1] > r[2] and (r[1] > 0 or r[2] > 0))
    nll = sum(1 for r in rows if r[2] > r[1])
    nz = sum(1 for r in rows if r[1] == 0 and r[2] == 0)
    print(f"cells: sim larger {nsl} / Limitless larger {nll} / no movement {nz}")
    tl = sorted(rows, key=lambda r: -r[3])
    cum = 0
    print("top cells by Limitless variance (cell part sd: Limitless, sim; d = new-old in points; cum share of Limitless var):")
    for j, r in enumerate(tl[:12]):
        cum += r[3]
        print(f"   {r[0][0]} v {r[0][1]:<17} L {r[2]:5.2f}  sim {r[1]:5.2f}  d {r[5]:+6.1f}  cum {100*cum/Lm:5.1f}%  (nL {d.nL[r[0]]})")
    for top in (6, 10):
        print(f"top {top} cells' share of Limitless variance: {100*sum(r[3] for r in tl[:top])/Lm:.1f}%")
    ray = [r for r in rows if "rayquaza" in r[0]]
    ag = [r for r in rows if "altaria_greninja" in r[0] and "rayquaza" not in r[0]]
    pn = [r for r in rows if "rayquaza" not in r[0] and "altaria_greninja" not in r[0]]
    for nm, grp in (("Rayquaza(9)", ray), ("A/G(8)", ag), ("panel(28)", pn)):
        print(f"  group {nm}: {len(grp)} cells; share of Limitless var {100*sum(r[3] for r in grp)/Lm:.1f}%; share of sim var {100*sum(r[4] for r in grp)/S:.1f}%")
    ts = sorted(rows, key=lambda r: -r[4])
    print("top cells by sim variance:")
    for r in ts[:6]:
        print(f"   {r[0][0]} v {r[0][1]:<17} sim {r[1]:5.2f}  L {r[2]:5.2f}  d {r[5]:+6.1f}")
    # deal-differ share
    nd = sum(cv[k]["ndiff"] for k in KEYS) / Kf
    vdm = sum(cv[k]["vD"] for k in KEYS) / Kf
    print(f"share of deals whose score differs: {100*nd:.1f}%; mean per-deal diff sd {100*math.sqrt(vdm):.1f} points (rms over cells)")
    return dict(S=S, Lm=Lm, X=X, pt=pt, tO=tO, tN=tN, cv=cv)


def mde(d, A, tag):
    print(f"\n### MDE {tag}")
    S, Lm, X, tO = A["S"], A["Lm"], A["X"], A["tO"]
    t2 = tO ** 2

    def sd(a=1.0, b=1.0):
        return math.sqrt(S / a + Lm / b + X / (a * b))

    def re(delta):
        return math.sqrt(max(0.0, t2 + delta))  # delta is negative ddmse -> pass -m

    z80 = 1.959964 + 0.841621
    print(f"tau_old^2 = {t2:.1f}; z50 = 1.96, z80 = {z80:.3f}")
    for lab, a, b in (("now", 1, 1), ("sim x2", 2, 1), ("sim x4", 4, 1), ("Limitless x0.5", 1, .5), ("Limitless x1.5", 1, 1.5), ("Limitless x2", 1, 2),
                      ("sim x4 + L x1.5", 4, 1.5), ("sim x4 + L x4", 4, 4)):
        s = sd(a, b)
        m50, m80 = 1.96 * s, z80 * s
        print(f"  {lab:<18} sd {s:5.1f}  MDE50 {m50:5.1f} -> real error {math.sqrt(t2 - m50):5.2f} | MDE80 {m80:5.1f} -> {math.sqrt(max(t2 - m80, 0)):5.2f}")
    print(f"  floor unlimited sim {1.96*math.sqrt(Lm):.1f}; floor unlimited Limitless {1.96*math.sqrt(S):.1f}")
    pt = A["pt"]
    for lab, a, b in (("now", 1, 1), ("sim x4", 4, 1), ("Limitless x1.5", 1, 1.5), ("Limitless x2.13", 1, 2.128), ("sim x4 + L x2.13", 4, 2.128), ("Limitless x0.5", 1, .5)):
        s = sd(a, b)
        print(f"  power at true = observed {pt:+.1f}, {lab}: {100*norm_cdf((abs(pt)-1.96*s)/s):.1f}%")
    # sample size to reach 80% at observed effect
    s_target = abs(pt) / z80
    tv = s_target ** 2
    # sim x4
    for a in (1, 4):
        rest = S / a
        if tv > rest:
            b = (Lm + X / a) / (tv - rest)
            print(f"  to reach 80% at |effect| {abs(pt):.1f} with sim x{a}: Limitless x{b:.2f} = {b*sum(d.nL.values()):.0f} matches")
        else:
            print(f"  sim x{a}: not reachable with any Limitless size")


def mc(d, reps, tag, events_path=None):
    print(f"\n### MONTE CARLO {tag} ({reps} reps)")
    rng = random.Random(777001)
    t0 = time.time()
    NN = {k: [x * x for x in d.Nv[k]] for k in KEYS}
    ig = {k: itemgetter(*range(d.n[k])) for k in KEYS}  # unused placeholder to keep API simple
    both, simo, limo = [], [], []
    N0, O0, L0 = d.N, d.O, d.L
    for r in range(reps):
        Ls = {k: rng.binomialvariate(d.nL[k], L0[k]) / d.nL[k] for k in KEYS}
        Ns, Os = {}, {}
        for k in KEYS:
            n = d.n[k]
            idx = rng.choices(range(n), k=n)
            f = itemgetter(*idx)
            Ns[k] = sum(f(d.Nv[k])) / n
            Os[k] = sum(f(d.Ov[k])) / n
        both.append(dmse(d, Ns, Os, Ls))
        simo.append(dmse(d, Ns, Os, L0))
        limo.append(dmse(d, N0, O0, Ls))
    for nm, v in (("both", both), ("sim only", simo), ("Limitless only (binomial)", limo)):
        m = sum(v) / len(v)
        sdv = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
        vs = sorted(v)
        print(f"  {nm:<26} mean {m:+7.2f} sd {sdv:6.2f} var {sdv*sdv:7.1f}  95% pct interval {pct(vs, .025):+.1f} to {pct(vs, .975):+.1f}  (half-width {(pct(vs,.975)-pct(vs,.025))/2:.1f})")
    if events_path:
        ev = json.load(open(events_path, encoding="utf-8"))["events"]
        evc = [{tuple(k.split("|")): tuple(v) for k, v in e["cells"].items()} for e in ev]
        tot = {k: tuple(sum(e.get(k, (0, 0, 0))[j] for e in evc) for j in range(3)) for k in KEYS}
        assert all(tot[k] == tuple(d.W[k]) for k in KEYS), "events do not sum to the cells"
        rng2 = random.Random(777002)
        lim_e, red = [], 0
        for r in range(reps):
            while True:
                draw = [evc[rng2.randrange(len(evc))] for _ in evc]
                c = {k: [sum(e.get(k, (0, 0, 0))[j] for e in draw) for j in range(3)] for k in KEYS}
                nE = {k: sum(c[k]) for k in KEYS}
                if all(nE.values()):
                    break
                red += 1
            LE = {k: (c[k][0] + 0.5 * c[k][2]) / nE[k] for k in KEYS}
            lim_e.append(dmse(d, N0, O0, LE))
        m = sum(lim_e) / len(lim_e)
        sdv = math.sqrt(sum((x - m) ** 2 for x in lim_e) / (len(lim_e) - 1))
        vs = sorted(lim_e)
        print(f"  {'Limitless only (by event)':<26} mean {m:+7.2f} sd {sdv:6.2f} var {sdv*sdv:7.1f}  95% pct interval {pct(vs, .025):+.1f} to {pct(vs, .975):+.1f}  ({len(ev)} events, {red} redrawn)")
    print(f"  ({time.time()-t0:.0f}s)")


def brute(d, reps, tag, mult_sim=1):
    """Power at 'truth = the reading' by whole-experiment simulation: deals resampled (paired), Limitless redrawn,
    the analytic sd estimated inside each experiment; success = est + 1.96 sd < 0."""
    print(f"\n### BRUTE FORCE {tag} ({reps} experiments)")
    rng = random.Random(888001)
    t0 = time.time()
    NN = {k: [x * x for x in d.Nv[k]] for k in KEYS}
    OO = {k: [x * x for x in d.Ov[k]] for k in KEYS}
    NO = {k: [a * b for a, b in zip(d.Nv[k], d.Ov[k])] for k in KEYS}
    ests, wins, sds = [], 0, []
    for r in range(reps):
        est = 0.0
        vs = vl = vx = 0.0
        for k in KEYS:
            n = d.n[k]
            idx = rng.choices(range(n), k=n)
            f = itemgetter(*idx)
            sN, sO, sNN, sOO, sNO = sum(f(d.Nv[k])), sum(f(d.Ov[k])), sum(f(NN[k])), sum(f(OO[k])), sum(f(NO[k]))
            Nb, Ob = sN / n, sO / n
            Lb = rng.binomialvariate(d.nL[k], d.L[k]) / d.nL[k]
            a, b = Nb - Lb, Ob - Lb
            est += a * a - b * b
            sg, sgg = a * sN - b * sO, a * a * sNN + b * b * sOO - 2 * a * b * sNO
            vg = svar(sg, sgg, n)
            sD, sDD = sN - sO, sNN + sOO - 2 * sNO
            vD = svar(sD, sDD, n)
            vL = Lb * (1 - Lb) / d.nL[k]
            vs += 4 * vg / n
            vl += 4 * (Nb - Ob) ** 2 * vL
            vx += 4 * vD / n * vL
        est = est / K * 1e4
        sd = math.sqrt(vs / mult_sim + vl + vx / mult_sim) / K * 1e4
        ests.append(est)
        sds.append(sd)
        if est + 1.96 * sd < 0:
            wins += 1
    m = sum(ests) / reps
    sdv = math.sqrt(sum((x - m) ** 2 for x in ests) / (reps - 1))
    msd = sum(sds) / reps
    obs = dmse(d, d.N, d.O, d.L)
    print(f"  mean est {m:+.2f} (observed {obs:+.2f}); MC sd of est {sdv:.2f}; mean in-experiment analytic sd {msd:.2f}")
    print(f"  fraction of experiments whose interval clears zero: {100*wins/reps:.1f}%  (Normal rule at observed: {100*norm_cdf((abs(obs)-1.96*msd)/msd):.1f}%)")
    print(f"  ({time.time()-t0:.0f}s)")


def floor(d, reps, tag, nsim=500):
    print(f"\n### NOISE FLOOR / TOP CELLS {tag}  (the OLD pilot vs Limitless)")
    S, L, nL = d.O, d.L, d.nL
    sq = {k: (S[k] - L[k]) ** 2 for k in KEYS}
    tot = sum(sq.values()) * 1e4
    lnoise = {k: L[k] * (1 - L[k]) / nL[k] * 1e4 for k in KEYS}
    snoise = {k: S[k] * (1 - S[k]) / d.n[k] * 1e4 for k in KEYS}
    print(f"raw sum of squared miss {tot:.0f}, mean {tot/K:.1f}, raw RMS {math.sqrt(tot/K):.2f}")
    ml, ms = sum(lnoise.values()) / K, sum(snoise.values()) / K
    bias = tot / K - ml - ms
    print(f"Limitless noise mean {ml:.1f} (sum {ml*K:.0f}, {100*ml*K/tot:.1f}% of raw), sim noise mean {ms:.1f} ({100*ms*K/tot:.1f}%), bias mean {bias:.1f} ({100*bias*K/tot:.1f}%), tau {math.sqrt(bias):.2f}")
    print(f"noise-floor raw RMS: Limitless alone {math.sqrt(ml):.2f}; with sim noise {math.sqrt(ml+ms):.2f}")
    print(f"observed average absolute miss {100*sum(abs(S[k]-L[k]) for k in KEYS)/K:.2f}")
    # cells beyond noise
    far = [k for k in KEYS if abs(S[k] - L[k]) * 100 > 2 * math.sqrt(lnoise[k] + snoise[k])]
    below = [k for k in KEYS if sq[k] * 1e4 < lnoise[k] + snoise[k]]
    print(f"cells missing by more than 2 sd of pure noise: {len(far)}; cells with squared miss below expected noise: {len(below)}")
    print("top 10 by squared miss: cell | old / Limitless | nL | miss | miss^2 | % of raw sum | Limitless-noise share of miss^2")
    top = sorted(KEYS, key=lambda k: -sq[k])[:10]
    for k in top:
        print(f"   {k[0]} v {k[1]:<17} {100*S[k]:5.1f} / {100*L[k]:5.1f} | {nL[k]:3d} | {100*(S[k]-L[k]):+6.1f} | {sq[k]*1e4:6.0f} | {100*sq[k]*1e4/tot:5.1f}% | {100*lnoise[k]/(sq[k]*1e4):3.0f}%")
    print(f"top 10 hold {100*sum(sq[k] for k in top)*1e4/tot:.1f}% of raw sum; Limitless noise in them {100*sum(lnoise[k] for k in top)/(sum(sq[k] for k in top)*1e4):.1f}% of their miss^2; their excess {100*sum(sq[k]*1e4-lnoise[k]-snoise[k] for k in top)/(tot-ml*K-ms*K):.1f}% of all excess")
    ray = [k for k in KEYS if "rayquaza" in k]
    ag = [k for k in KEYS if "altaria_greninja" in k and "rayquaza" not in k]
    pn = [k for k in KEYS if k not in ray and k not in ag]
    exc = {k: sq[k] * 1e4 - lnoise[k] - snoise[k] for k in KEYS}
    te = sum(exc.values())
    for nm, g in (("Rayquaza(9)", ray), ("A/G(8)", ag), ("panel(28)", pn), ("new 17", ray + ag)):
        e = sum(exc[k] for k in g)
        print(f"   group {nm}: share of excess {100*e/te:.1f}%; group tau {math.sqrt(max(0,e/len(g))):.1f}; Limitless matches {sum(nL[k] for k in g)}")
    # perfect simulator
    rng = random.Random(999001)
    taus, raws, absm = [], [], []
    for r in range(reps):
        Ls = {k: rng.binomialvariate(nL[k], L[k]) / nL[k] for k in KEYS}
        Ss = {k: rng.binomialvariate(nsim, L[k]) / nsim for k in KEYS}
        taus.append(tau(Ss, {k: nsim for k in KEYS}, Ls, nL))
        raws.append(100 * math.sqrt(sum((Ss[k] - Ls[k]) ** 2 for k in KEYS) / K))
        absm.append(100 * sum(abs(Ss[k] - Ls[k]) for k in KEYS) / K)
    taus.sort()
    print(f"perfect simulator (truth = Limitless observed rates), {reps} draws:")
    print(f"   tau-hat: median {pct(taus,.5):.2f}, mean {sum(taus)/reps:.2f}, 95th pct {pct(taus,.95):.2f}, share <= 5.5 {100*sum(1 for t in taus if t<=5.5)/reps:.1f}%")
    print(f"   raw RMS mean {sum(raws)/reps:.2f}; average absolute miss mean {sum(absm)/reps:.2f}")


def main():
    name = sys.argv[1]
    modes = sys.argv[2].split(",")
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    d = build(name)
    A = analytic(d, name) if ("analytic" in modes or "mde" in modes) else None
    if "mde" in modes:
        mde(d, A, name)
    if "mc" in modes:
        mc(d, reps, name, f"{R}/scoreboard_v3_2026-09-27/limitless_45_dev_events.json")
    if "brute" in modes:
        brute(d, reps, name)
    if "brute4" in modes:
        brute(d, reps, name + " simulator x4 (sim variance /4)", mult_sim=4)
    if "floor" in modes:
        floor(d, reps, name)


if __name__ == "__main__":
    main()
