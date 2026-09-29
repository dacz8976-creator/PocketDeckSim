"""Part 2: minimum detectable effect of the 45-cell dMSE rule (whole 95% interval below zero  <=>  point + 1.96*sd < 0).
If the estimate is ~Normal(true, sd^2) (skew checked in decompose.py: |skew| <= 0.2), the interval clears zero with
probability Phi((|true| - 1.96 sd)/sd): 50% at |true| = 1.96 sd, 80% at (1.96 + 0.8416) sd = 2.80 sd.
Variance model (verified against score.py's own bootstrap in decompose.py):
   var = var_sim/ms + var_lim/mL + var_cross/(ms*mL)      ms = simulator deals per cell / 500, mL = Limitless matches / 2,214
   var_sim = (2e4/K)^2 sum_k [m_k^2 VarD_k + d_k^2 VarO_k]/n_k         m_k = N_k - L_k, d_k = N_k - O_k
   var_lim = (2e4/K)^2 sum_k d_k^2 L_k(1-L_k)/nL_k
   var_cross = (2e4/K)^2 sum_k (VarD_k/n_k) L_k(1-L_k)/nL_k
A. PLUG-IN: a future candidate that moves cells the way reading X did (the sd measured on X's own games).
B. SCENARIO: a well-aimed candidate that removes a fraction f of every cell's real (noise-corrected) miss, d_k = -f e*_k, with per-deal
   paired variance taken from a reference reading (footprint), floored at the feasible minimum |d_k|. True dMSE = -(2f - f^2) tau^2.
"""
import sys, json, math
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *
A = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst/"
Z50, Z80 = 1.96, 1.96 + 0.8416
TAU0 = 14.05           # kog3's real error (score.py: 14.0), the current working pilot; kp3 = 15.51
NAMES = ["koh3_vs_kog3", "kpf3_vs_kp3", "kpr3_vs_kp3", "kog3_vs_kp3", "kpg3_vs_kp3", "kog3_vs_kpg3"]
dec = {n: json.load(open(A + f"decomp_{n}.json")) for n in NAMES}

CONFIGS = [  # label, ms (simulator deals / 500), mL (Limitless matches / 2214)
    ("now: 500 deals, 2,214 matches", 1, 1),
    ("sim x2", 2, 1), ("sim x4", 4, 1), ("sim x8", 8, 1),
    ("Limitless x0.5 (post-freeze read alone, 1,107)", 1, 0.5),
    ("Limitless x1.5 (dev + post-freeze read, 3,321)", 1, 1.5),
    ("Limitless x2", 1, 2), ("Limitless x4", 1, 4), ("Limitless x infinity (sim noise only)", 1, 1e9),
    ("sim x4 + Limitless x1.5", 4, 1.5), ("sim x4 + Limitless x4", 4, 4), ("sim x infinity (Limitless noise only)", 1e9, 1),
]


def sd_cfg(v, ms, mL):
    return math.sqrt(v["var_sim"] / ms + v["var_lim"] / mL + v["var_cross"] / (ms * mL))


def tau_after(delta, tau0=TAU0):
    return math.sqrt(max(0.0, tau0 ** 2 - delta))


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


print("A. PLUG-IN: sd of dMSE (points^2) and the smallest true dMSE cleared 50% / 80% of the time; tau after = sqrt(14.05^2 - delta)")
print("   (a future candidate that moves the 45 cells the way each reading's candidate did; sd measured from that reading's games)")
for n in NAMES:
    v = dec[n]["analytic"]
    print(f"\n-- like {dec[n]['new']} vs {dec[n]['old']} (point dMSE {dec[n]['point']:+.1f}; analytic var: sim {v['var_sim']:.1f}, Limitless {v['var_lim']:.1f}, cross {v['var_cross']:.1f})")
    print(f"   {'configuration':<50}{'sd':>7}{'MDE50':>8}{'-> tau':>8}{'MDE80':>8}{'-> tau':>8}{'Limitless share':>17}")
    for lab, ms, mL in CONFIGS:
        s = sd_cfg(v, ms, mL)
        vt = v["var_sim"] / ms + v["var_lim"] / mL + v["var_cross"] / (ms * mL)
        share = (v["var_lim"] / mL) / vt
        print(f"   {lab:<50}{s:7.1f}{Z50 * s:8.1f}{tau_after(Z50 * s):8.2f}{Z80 * s:8.1f}{tau_after(Z80 * s):8.2f}{100 * share:16.0f}%")

print("\n\nPower at each reading's own observed effect (if the truth equalled the estimate; winner's-curse caveat):")
for n in NAMES:
    v = dec[n]["analytic"]
    est = -dec[n]["point"]
    row = []
    for lab, ms, mL in CONFIGS[:4] + [CONFIGS[5], CONFIGS[9]]:
        s = sd_cfg(v, ms, mL)
        row.append(f"{lab.split(':')[0].split(' (')[0]} {100 * Phi((est - Z50 * s) / s):.0f}%")
    print(f"  {dec[n]['new']} vs {dec[n]['old']}: effect {est:+.1f}:  " + " | ".join(row))

# ---------------- B. scenario ----------------
pairs, lim = load_limitless()
K = len(pairs)
kdec = dec["koh3_vs_kog3"]["cells"]        # kog3 is the current pilot here: O, L, e_cur, varO
nfloor = json.load(open(A + "noise_floor.json"))
cells = {tuple(c["k"].split("|")): c for c in nfloor["cells"]}
excess_total = sum(c["exc"] for c in cells.values())
pos = sum(max(0.0, c["exc"]) for c in cells.values())
scale = math.sqrt(excess_total / pos)
estar = {}
for k in pairs:
    c = cells[k]
    mag = math.sqrt(max(0.0, c["exc"])) * scale
    estar[k] = math.copysign(mag, c["e"]) / 100
tau2 = sum(1e4 * estar[k] ** 2 for k in pairs) / K
print(f"\n\nB. SCENARIO: well-aimed candidate; e*_k = kog3's noise-corrected miss (shrunk so mean e*^2 = {tau2:.1f} = tau-hat^2 = 14.05^2 = {14.05 ** 2:.1f})")
sigL2 = {k: lim_ for k, lim_ in ()}
Lk = {k: kdec[f"{k[0]}|{k[1]}"]["L"] for k in pairs}
nLk = {k: kdec[f"{k[0]}|{k[1]}"]["nL"] for k in pairs}
sigL2 = {k: Lk[k] * (1 - Lk[k]) / nLk[k] for k in pairs}
ek = {k: kdec[f"{k[0]}|{k[1]}"]["e_cur"] for k in pairs}          # observed miss (what the statistic sees)
VO = {k: kdec[f"{k[0]}|{k[1]}"]["varO"] for k in pairs}
REFS = {"surgical (feasible minimum: only games that must flip do)": None,
        "footprint of kog3 vs kp3 (6% of deals differ)": "kog3_vs_kp3",
        "footprint of koh3 vs kog3 (29% of deals differ)": "koh3_vs_kog3"}


def scen_var(f, ref):
    vs = vl = vc = 0.0
    for k in pairs:
        d = -f * estar[k]
        m = ek[k] + d
        vref = dec[ref]["cells"][f"{k[0]}|{k[1]}"]["varD"] if ref else 0.0
        VD = max(vref, abs(d))
        vs += (m * m * VD + d * d * VO[k]) / 500
        vl += d * d * sigL2[k]
        vc += VD / 500 * sigL2[k]
    c = (2e4 / K) ** 2
    return c * vs, c * vl, c * vc


def solve(ref, z, ms, mL):
    lo, hi = 1e-4, 0.95
    for _ in range(80):
        f = (lo + hi) / 2
        vs, vl, vc = scen_var(f, ref)
        s = math.sqrt(vs / ms + vl / mL + vc / (ms * mL))
        delta = (2 * f - f * f) * tau2
        if delta < z * s:
            lo = f
        else:
            hi = f
    f = (lo + hi) / 2
    vs, vl, vc = scen_var(f, ref)
    s = math.sqrt(vs / ms + vl / mL + vc / (ms * mL))
    return f, (2 * f - f * f) * tau2, s, (vl / mL) / (vs / ms + vl / mL + vc / (ms * mL))


for lab, ref in REFS.items():
    print(f"\n-- {lab}")
    print(f"   {'configuration':<50}{'f50':>6}{'MDE50':>8}{'tau':>7}{'f80':>7}{'MDE80':>8}{'tau':>7}{'sd@50':>8}{'Lim share@50':>14}")
    for lab2, ms, mL in CONFIGS:
        f5, d5, s5, sh5 = solve(ref, Z50, ms, mL)
        f8, d8, s8, sh8 = solve(ref, Z80, ms, mL)
        print(f"   {lab2:<50}{f5:6.3f}{d5:8.1f}{TAU0 * (1 - f5):7.2f}{f8:7.3f}{d8:8.1f}{TAU0 * (1 - f8):7.2f}{s5:8.1f}{100 * sh5:13.0f}%")
