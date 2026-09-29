"""Part 3: where kog3's 14.0 real error comes from on the 45 development cells, and the noise floor.
score.py's tau = sqrt(mean_k[(S-L)^2 - L(1-L)/nL - S(1-S)/nS]) (points), i.e. the raw mean squared miss with the expected
sampling noise of BOTH sides already subtracted. So 14.0 is already the noise-corrected number; the raw RMS miss is larger.
Here: per cell squared miss, expected Limitless noise, expected simulator noise, the excess (= real bias^2), the top 10,
the raw-RMS noise floor of a perfect simulator, and the distribution of tau-hat a perfect simulator would produce."""
import sys, math, random, json
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *

pairs, lim = load_limitless()
op, np_, on, nn = readings()["koh3_vs_kog3"]          # O = kog3 500-deal cell rates
deals = load_reading(op, np_, pairs)
O, N, L, nL, n = cell_stats(pairs, lim, deals)
K = len(pairs)
S_ = O
rows = []
for k in pairs:
    e = 100 * (S_[k] - L[k])
    vl = 1e4 * L[k] * (1 - L[k]) / nL[k]
    vs = 1e4 * S_[k] * (1 - S_[k]) / n[k]
    rows.append(dict(k=k, e=e, e2=e * e, vl=vl, vs=vs, exc=e * e - vl - vs, L=100 * L[k], S=100 * S_[k], nL=nL[k]))
tot_e2 = sum(r["e2"] for r in rows); tot_vl = sum(r["vl"] for r in rows); tot_vs = sum(r["vs"] for r in rows)
tot_exc = tot_e2 - tot_vl - tot_vs
print(f"kog3 on the 45 development cells (K = {K}); all numbers in points (rates x100) or points^2")
print(f"sum e^2 = {tot_e2:.0f}  -> raw MSE {tot_e2 / K:.1f}, raw RMS miss {math.sqrt(tot_e2 / K):.2f}")
print(f"expected Limitless noise  sum L(1-L)/nL = {tot_vl:.0f} -> mean {tot_vl / K:.1f} pts^2")
print(f"expected simulator noise  sum S(1-S)/500 = {tot_vs:.0f} -> mean {tot_vs / K:.1f} pts^2")
print(f"excess (real bias^2) = {tot_exc:.0f} -> mean {tot_exc / K:.1f} -> tau-hat = {math.sqrt(tot_exc / K):.2f}  (score.py prints 14.0)")
print(f"shares of the raw sum of squared misses: real bias {100 * tot_exc / tot_e2:.0f}%, Limitless noise {100 * tot_vl / tot_e2:.0f}%, simulator noise {100 * tot_vs / tot_e2:.0f}%")
print(f"NOISE FLOOR (raw RMS miss a perfect simulator would still show): Limitless noise alone {math.sqrt(tot_vl / K):.2f}; "
      f"with the simulator's own 500-deal noise {math.sqrt((tot_vl + tot_vs) / K):.2f} (raw RMS observed {math.sqrt(tot_e2 / K):.2f})")
# mean absolute miss (the 'average miss' column: 13.0 in score.py's print)
am = sum(abs(r["e"]) for r in rows) / K
floor_am = sum(math.sqrt(r["vl"] + r["vs"]) * math.sqrt(2 / math.pi) for r in rows) / K
print(f"average (absolute) miss: observed {am:.1f} (score.py prints 13.0); a perfect simulator would show about {floor_am:.1f} (sum of sd*sqrt(2/pi))")
zs = [abs(r["e"]) / math.sqrt(r["vl"] + r["vs"]) for r in rows]
print(f"cells whose miss is beyond 2 sd of pure noise: {sum(z > 2 for z in zs)} of {K}; beyond 1 sd: {sum(z > 1 for z in zs)}; a perfect simulator expects about {0.0455 * K:.1f} and {0.317 * K:.0f}")
print()
print("TOP 10 CELLS BY SQUARED MISS (kog3 - Limitless), and what noise alone would give")
print(f"{'cell':<32}{'kog3':>6}{'Lim':>6}{'nL':>5}{'miss':>7}{'miss^2':>8}{'% of sum':>9}{'Lim noise':>10}{'sim noise':>10}{'noise share':>12}{'excess':>8}{'z':>6}")
top = sorted(rows, key=lambda r: -r["e2"])
cum = 0.0
for r in top[:10]:
    cum += r["e2"]
    print(f"{r['k'][0] + ' v ' + r['k'][1]:<32}{r['S']:6.1f}{r['L']:6.1f}{r['nL']:5d}{r['e']:+7.1f}{r['e2']:8.0f}{100 * r['e2'] / tot_e2:8.1f}%{r['vl']:10.0f}{r['vs']:10.0f}{100 * (r['vl'] + r['vs']) / r['e2']:11.0f}%{r['exc']:8.0f}{abs(r['e']) / math.sqrt(r['vl'] + r['vs']):6.1f}")
top10 = top[:10]
e2_10 = sum(r["e2"] for r in top10); vl_10 = sum(r["vl"] for r in top10); vs_10 = sum(r["vs"] for r in top10)
print(f"top 10 together: miss^2 {e2_10:.0f} = {100 * e2_10 / tot_e2:.0f}% of the total; Limitless noise expected in them {vl_10:.0f} ({100 * vl_10 / e2_10:.0f}% of their squared miss), "
      f"simulator noise {vs_10:.0f} ({100 * vs_10 / e2_10:.0f}%), excess {e2_10 - vl_10 - vs_10:.0f} = {100 * (e2_10 - vl_10 - vs_10) / tot_exc:.0f}% of all excess")
rest = [r for r in rows if r not in top10]
print(f"the other 35 cells: miss^2 {sum(r['e2'] for r in rest):.0f}, expected noise {sum(r['vl'] + r['vs'] for r in rest):.0f}, excess {sum(r['exc'] for r in rest):.0f}")
neg = [r for r in rows if r["exc"] < 0]
print(f"cells whose squared miss is below the expected noise (excess < 0): {len(neg)}")
# rank by excess (real bias) instead
print()
print("TOP 10 CELLS BY EXCESS (miss^2 minus expected noise = the cell's part of tau^2*K)")
for r in sorted(rows, key=lambda r: -r["exc"])[:10]:
    print(f"  {r['k'][0] + ' v ' + r['k'][1]:<32} miss {r['e']:+6.1f}  excess {r['exc']:6.0f} = {100 * r['exc'] / tot_exc:4.1f}% of the total excess (nL {r['nL']})")
rq = [r for r in rows if "rayquaza" in r["k"]]
ag = [r for r in rows if "altaria_greninja" in r["k"] and "rayquaza" not in r["k"]]
pn = [r for r in rows if "rayquaza" not in r["k"] and "altaria_greninja" not in r["k"]]
for lab, g in (("9 Rayquaza cells", rq), ("8 Altaria/Greninja cells (not vs Rayquaza)", ag), ("28 panel cells", pn)):
    ex = sum(r["exc"] for r in g)
    print(f"  group {lab}: excess {ex:.0f} = {100 * ex / tot_exc:.0f}% of the total; group tau-hat {math.sqrt(max(0, ex / len(g))):.1f}; raw RMS {math.sqrt(sum(r['e2'] for r in g) / len(g)):.1f}; noise floor RMS {math.sqrt(sum(r['vl'] + r['vs'] for r in g) / len(g)):.1f}")

# perfect simulator: truth L* = observed L; Limitless drawn Bin(nL, L*), simulator Bin(500, L*): distribution of raw RMS and tau-hat
rng = random.Random(777)
raw, taus = [], []
for _ in range(20000):
    acc_raw = acc_tau = 0.0
    for k in pairs:
        Lk = rng.binomialvariate(nL[k], L[k]) / nL[k]
        Sk = rng.binomialvariate(n[k], L[k]) / n[k]
        m = (Sk - Lk) ** 2
        acc_raw += m
        acc_tau += m - Lk * (1 - Lk) / nL[k] - Sk * (1 - Sk) / n[k]
    raw.append(100 * math.sqrt(acc_raw / K)); taus.append(100 * math.sqrt(max(0.0, acc_tau / K)))
raw.sort(); taus.sort()
q = lambda v, p: v[int(p * (len(v) - 1))]
print()
print("PERFECT SIMULATOR (truth = the observed Limitless cells; both sides redrawn at their real sizes, 20,000 draws)")
print(f"  raw RMS miss: median {q(raw, .5):.2f}, 5-95% {q(raw, .05):.2f} to {q(raw, .95):.2f}")
print(f"  tau-hat (score.py's real error): median {q(taus, .5):.2f}, mean {sum(taus) / len(taus):.2f}, 90th pct {q(taus, .9):.2f}, 95th pct {q(taus, .95):.2f}, 99th {q(taus, .99):.2f}; share of draws <= 5.5: {100 * sum(t <= 5.5 for t in taus) / len(taus):.1f}%")
json.dump(dict(raw_rms=math.sqrt(tot_e2 / K), floor_lim=math.sqrt(tot_vl / K), floor_both=math.sqrt((tot_vl + tot_vs) / K), tau=math.sqrt(tot_exc / K),
               cells=[dict(k="|".join(r["k"]), **{a: b for a, b in r.items() if a != "k"}) for r in rows]),
          open("/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst/noise_floor.json", "w"), indent=1)
