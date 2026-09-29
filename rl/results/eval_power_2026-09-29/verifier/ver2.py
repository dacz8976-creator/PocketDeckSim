#!/usr/bin/env python3
"""Verifier part 2: scenario B (well-aimed candidate removes a fraction f of every cell's miss) and a long Limitless-only
resampling (binomial vs by-event) to settle which is wider."""
import json, math, random, sys, time
import ver
from ver import *

base = ver.build("koh3_vs_kog3")           # base.O = kog3's rates, base.L = Limitless
m = {k: base.O[k] - base.L[k] for k in KEYS}
tau2 = sum(((base.O[k] - base.L[k]) ** 2 - base.L[k] * (1 - base.L[k]) / base.nL[k] - base.O[k] * (1 - base.O[k]) / base.n[k]) for k in KEYS) / K * 1e4
print(f"kog3 tau^2 {tau2:.1f}")


def sd_B(R, f, mult_sim=1):
    """sd (points^2) of dMSE for a candidate that has R's deal-level footprint and moves each cell a fraction f of kog3's miss."""
    vs = vl = vx = 0.0
    for k in KEYS:
        n = R.n[k]
        a, b = (1 - f) * m[k], m[k]
        g = [a * x - b * y for x, y in zip(R.Nv[k], R.Ov[k])]
        mg = sum(g) / n
        vg = sum((z - mg) ** 2 for z in g) / (n - 1)
        D = [x - y for x, y in zip(R.Nv[k], R.Ov[k])]
        mD = sum(D) / n
        vD = sum((z - mD) ** 2 for z in D) / (n - 1)
        vL = base.L[k] * (1 - base.L[k]) / base.nL[k]
        dd = f * m[k]
        vs += 4 * vg / n
        vl += 4 * dd * dd * vL
        vx += 4 * vD / n * vL
    tot = vs / mult_sim + vl + vx / mult_sim
    return math.sqrt(tot) / K * 1e4, (vs, vl, vx)


def solve(R, z, mult_sim=1):
    lo, hi = 1e-4, 0.5
    for _ in range(60):
        f = (lo + hi) / 2
        eff = (2 * f - f * f) * tau2
        if eff < z * sd_B(R, f, mult_sim)[0]:
            lo = f
        else:
            hi = f
    f = (lo + hi) / 2
    eff = (2 * f - f * f) * tau2
    s, (vs, vl, vx) = sd_B(R, f, mult_sim)
    return f, eff, s, vl / (vs + vl + vx) if mult_sim == 1 else None


z80 = 1.959964 + 0.841621
for nm in ("kog3_vs_kp3", "koh3_vs_kog3"):
    RD = ver.build(nm)
    for lab, ms in (("sim x1", 1), ("sim x4", 4)):
        for zl, z in (("MDE50", 1.959964), ("MDE80", z80)):
            f, eff, s, sh = solve(RD, z, ms)
            print(f"scenario B, footprint {nm}, {lab}, {zl}: effect {eff:.1f} (f = {100*f:.1f}%), sd {s:.2f}, real error {math.sqrt(tau2-eff):.2f}" + (f", Limitless share of var {100*sh:.1f}%" if sh is not None else ""))

# long Limitless-only resampling
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
rng = random.Random(4242)
N0, O0, L0 = base.N, base.O, base.L
vals = []
for _ in range(reps):
    Ls = {k: rng.binomialvariate(base.nL[k], L0[k]) / base.nL[k] for k in KEYS}
    vals.append(ver.dmse(base, N0, O0, Ls))
mu = sum(vals) / reps
vb = sum((x - mu) ** 2 for x in vals) / (reps - 1)
ev = json.load(open(f"{R}/scoreboard_v3_2026-09-27/limitless_45_dev_events.json", encoding="utf-8"))["events"]
evc = [{tuple(k.split("|")): tuple(v) for k, v in e["cells"].items()} for e in ev]
rng2 = random.Random(4243)
vals_e = []
for _ in range(reps):
    while True:
        draw = [evc[rng2.randrange(len(evc))] for _ in evc]
        c = {k: [sum(e.get(k, (0, 0, 0))[j] for e in draw) for j in range(3)] for k in KEYS}
        nE = {k: sum(c[k]) for k in KEYS}
        if all(nE.values()):
            break
    LE = {k: (c[k][0] + 0.5 * c[k][2]) / nE[k] for k in KEYS}
    vals_e.append(ver.dmse(base, N0, O0, LE))
mu_e = sum(vals_e) / reps
ve = sum((x - mu_e) ** 2 for x in vals_e) / (reps - 1)
print(f"Limitless-only, {reps} reps: binomial var {vb:.0f} (sd {math.sqrt(vb):.1f}); by-event var {ve:.0f} (sd {math.sqrt(ve):.1f}); ratio {ve/vb:.3f}")
