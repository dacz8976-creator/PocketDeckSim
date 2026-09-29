"""Check of the Normal power rule by brute force. 'Bootstrap world': the reading's own paired per-deal joint distribution (per cell)
stands for the simulator truth and its Limitless cells for the real truth, so the true dMSE of that world is the reading's point
estimate. Repeat the whole experiment 4,000 times at each size (fresh deals from the joint, fresh Limitless ~ Binomial), compute the
estimate and the plug-in delta-method sd (the same formula verified against score.py's bootstrap), and count how often
estimate + 1.96*sd < 0 (the whole 95% interval below zero). Compare with Phi((|true| - 1.96 sd)/sd) from the analytic sd."""
import sys, math, random, json
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *
from decompose import prep_cells
import collections

pairs, lim = load_limitless()
K = len(pairs)
REPS = 4000


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def run(name, ms, mL, seed=99):
    op, np_, on, nn = readings()[name]
    deals = load_reading(op, np_, pairs)
    O0, N0, L0, nL0, n0 = cell_stats(pairs, lim, deals)
    cats = {}
    for k in pairs:
        c = collections.Counter(deals[k]); items = sorted(c.items())
        cats[k] = ([o for (o, x), _ in items], [x for (o, x), _ in items], [cnt / n0[k] for _, cnt in items])
    rng = random.Random(seed)
    truth = dmse_point(pairs, O0, N0, L0)
    clear = 0
    ests = []
    sds = []
    for _ in range(REPS):
        est = 0.0
        var = 0.0
        for k in pairs:
            vo, vn, pr = cats[k]
            n = n0[k] * ms
            # multinomial by sequential binomials
            rem, rp, cnt = n, 1.0, []
            for j, p in enumerate(pr[:-1]):
                kk = rng.binomialvariate(rem, min(1.0, p / rp)) if rem > 0 else 0
                cnt.append(kk); rem -= kk; rp -= p
            cnt.append(rem)
            O = sum(c * o for c, o in zip(cnt, vo)) / n
            N = sum(c * x for c, x in zip(cnt, vn)) / n
            nl = max(1, int(round(nL0[k] * mL)))
            L = rng.binomialvariate(nl, L0[k]) / nl
            est += ((N - L) ** 2 - (O - L) ** 2) * 1e4 / K
            # plug-in variance
            zs = [(2e4 / K) * ((N - L) * x - (O - L) * o) for o, x in zip(vo, vn)]
            zbar = sum(c * z for c, z in zip(cnt, zs)) / n
            vs = sum(c * (z - zbar) ** 2 for c, z in zip(cnt, zs)) / (n - 1) / n
            d = N - O
            Dv = [x - o for o, x in zip(vo, vn)]
            Dbar = sum(c * v for c, v in zip(cnt, Dv)) / n
            varD = sum(c * (v - Dbar) ** 2 for c, v in zip(cnt, Dv)) / (n - 1)
            sl = L * (1 - L) / nl
            var += vs + (2e4 / K * d) ** 2 * sl + (2e4 / K) ** 2 * varD / n * sl
        sd = math.sqrt(var)
        ests.append(est); sds.append(sd)
        clear += est + 1.96 * sd < 0
    m = sum(ests) / REPS
    sdest = math.sqrt(sum((e - m) ** 2 for e in ests) / (REPS - 1))
    msd = sum(sds) / REPS
    pred = Phi((-truth - 1.96 * sdest) / sdest)
    print(f"  {name:<14} sim x{ms:<3} Limitless x{mL:<4}: world truth {truth:+6.1f}; sd of the estimate over experiments {sdest:5.1f} (mean plug-in sd {msd:5.1f}); "
          f"whole interval below 0 in {100 * clear / REPS:4.1f}% of experiments; Normal rule Phi((|t|-1.96 sd)/sd) = {100 * pred:4.1f}%")


print("POWER BY BRUTE FORCE (4,000 whole experiments each)")
for name in ("koh3_vs_kog3", "kpf3_vs_kp3", "kog3_vs_kp3"):
    for ms, mL in ((1, 1), (4, 1), (1, 1.5), (4, 1.5)):
        run(name, ms, mL)
