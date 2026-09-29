"""Compact summary of decompose.py's JSON outputs: totals, groups of cells, worked arithmetic, and the Limitless sample sizes."""
import json, math, csv, sys
A = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst/"
NAMES = ["koh3_vs_kog3", "kog3_vs_kp3", "kpg3_vs_kp3", "kpf3_vs_kp3", "kpr3_vs_kp3", "kog3_vs_kpg3"]
K = 45
dec = {n: json.load(open(A + f"decomp_{n}.json")) for n in NAMES}
print("TOTALS (analytic delta method; the resampling check agrees within ~2% of the sd)")
print(f"{'reading':<16}{'dMSE':>7}{'sd sim':>8}{'sd Lim':>8}{'sd cross':>9}{'sd total':>9}{'boot sd':>8}{'Lim var%':>9}{'+-sim only':>11}{'+-Lim only':>11}{'+-both':>8}{'boot +-':>9}  cells: sim>Lim / Lim>sim / neither")
for n in NAMES:
    d = dec[n]; a = d["analytic"]; b = d["boot"]["both"]
    vt = a["var_sim"] + a["var_lim"] + a["var_cross"]
    simc = sum(1 for c in d["cells"].values() if c["var_sim"] > c["var_lim"])
    limc = sum(1 for c in d["cells"].values() if c["var_lim"] > c["var_sim"])
    print(f"{d['new'] + '/' + d['old']:<16}{d['point']:+7.1f}{math.sqrt(a['var_sim']):8.1f}{math.sqrt(a['var_lim']):8.1f}{math.sqrt(a['var_cross']):9.1f}{math.sqrt(vt):9.1f}{b['sd']:8.1f}"
          f"{100 * a['var_lim'] / vt:8.0f}%{1.96 * math.sqrt(a['var_sim']):11.1f}{1.96 * math.sqrt(a['var_lim']):11.1f}{1.96 * math.sqrt(vt):8.1f}{(b['hi'] - b['lo']) / 2:9.1f}{simc:>7d}/{limc}/{K - simc - limc}")

print("\nGROUPS OF CELLS: share of each side's variance carried by (9 Rayquaza cells | 8 Altaria/Greninja cells | 28 panel cells)")


def grp(k):
    a, b = k.split("|")
    return "R" if "rayquaza" in (a, b) else ("G" if "altaria_greninja" in (a, b) else "P")


for n in NAMES:
    d = dec[n]
    tot = {"sim": {}, "lim": {}}
    for k, c in d["cells"].items():
        g = grp(k)
        tot["sim"][g] = tot["sim"].get(g, 0) + c["var_sim"]
        tot["lim"][g] = tot["lim"].get(g, 0) + c["var_lim"]
    s = sum(tot["sim"].values()); l = sum(tot["lim"].values())
    print(f"{d['new'] + '/' + d['old']:<16} simulator variance: Rayquaza {100 * tot['sim']['R'] / s:3.0f}%, A/G {100 * tot['sim']['G'] / s:3.0f}%, panel {100 * tot['sim']['P'] / s:3.0f}%"
          f"   | Limitless variance: Rayquaza {100 * tot['lim']['R'] / l:3.0f}%, A/G {100 * tot['lim']['G'] / l:3.0f}%, panel {100 * tot['lim']['P'] / l:3.0f}%")

print("\nHOW CONCENTRATED: koh3 vs kog3, cumulative share of the Limitless variance by the biggest cells")
c = sorted(dec["koh3_vs_kog3"]["cells"].items(), key=lambda kv: -kv[1]["var_lim"])
tl = sum(v["var_lim"] for _, v in c)
cum = 0
for i, (k, v) in enumerate(c[:12], 1):
    cum += v["var_lim"]
    print(f"  {i:2d}. {k.replace('|', ' v '):<30} share {100 * v['var_lim'] / tl:4.1f}%  cumulative {100 * cum / tl:5.1f}%")

print("\nWORKED ARITHMETIC (koh3 vs kog3), K = 45; scores in points")
cells = dec["koh3_vs_kog3"]["cells"]
for k in ("rayquaza|vespiquen", "altaria_greninja|sceptile"):
    c = cells[k]
    d, L, nL, n = 100 * c["d"], 100 * c["L"], c["nL"], c["n"]
    N, O = 100 * c["N"], 100 * c["O"]
    sdL = 100 * math.sqrt(c["L"] * (1 - c["L"]) / nL)
    coefL = 2 * abs(d) / K
    m = N - L
    sdD = 100 * math.sqrt(c["varD"]); sdO = 100 * math.sqrt(c["varO"])
    print(f"  {k.replace('|', ' v ')}: kog3 {O:.1f} -> koh3 {N:.1f} (d = {d:+.1f}), Limitless {L:.1f} on {nL} matches")
    print(f"    Limitless side: binomial sd of the cell = 100*sqrt({c['L']:.3f}*{1 - c['L']:.3f}/{nL}) = {sdL:.1f}; weight 2|d|/K = 2*{abs(d):.1f}/45 = {coefL:.3f}; part of dMSE sd = {coefL * sdL:.2f}")
    t1 = 2 * abs(m) / K * sdD / math.sqrt(n)
    t2 = 2 * abs(d) / K * sdO / math.sqrt(n)
    print(f"    simulator side: per-deal linear form m*D_i + d*O_i, m = N-L = {m:+.1f}; sd(D) = {sdD:.0f} (paired koh3-kog3 per deal), sd(O) = {sdO:.0f} (kog3 per deal), n = {n}")
    print(f"      term m*D: 2*{abs(m):.1f}/45*{sdD:.0f}/sqrt({n}) = {t1:.2f}; term d*O: 2*{abs(d):.1f}/45*{sdO:.0f}/sqrt({n}) = {t2:.2f}; with their covariance the cell's sim sd = {math.sqrt(c['var_sim']):.2f}")

print("\nLIMITLESS SAMPLE SIZES (matches): development half per scoreboard cell, from frozen_cells.csv n columns only")
n_dev = n_pool = 0
rows = list(csv.DictReader(open("/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/scoreboard_v3_2026-09-27/frozen_cells.csv")))
n_dev = sum(int(r["n_dev"]) for r in rows); n_pool = sum(int(r["n_pooled"]) for r in rows)
print(f"  dev {n_dev}, pooled (dev + the spent Sept 25 holdout; sizes only, no outcome used) {n_pool} = x{n_pool / n_dev:.2f}")
ns = sorted(int(r["n_dev"]) for r in rows)
print(f"  dev per-cell n: min {ns[0]}, median {ns[len(ns) // 2]}, max {ns[-1]}; cells with n < 20: {sum(1 for x in ns if x < 20)}; n < 40: {sum(1 for x in ns if x < 40)}")
