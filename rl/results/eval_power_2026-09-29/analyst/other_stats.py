"""Part 4 support: would a different statistic have more power than the 45-cell unweighted dMSE?
Compared on the same six readings, same bootstrap (deals resampled within cell; Limitless binomial), by the ratio |estimate|/sd (z):
  cell      : score.py's statistic, mean over 45 cells of (N-L)^2 - (O-L)^2
  cell_w    : the same with each cell weighted by 1/(L(1-L)/nL + tau0^2), tau0^2 = 14.05^2 (down-weights cells with few real matches), weights mean 1
  deck      : the 10 deck averages (each deck's mean score over its 9 cells, as score.py's deck_avgs), mean over decks of (N_j-L_j)^2 - (O_j-L_j)^2
z is one draw per reading, not a power; the variance split (sim / Limitless) is the useful part."""
import sys, math, random, json
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *
from decompose import prep_cells, draw_sim

TAU0SQ = 14.05 ** 2 / 1e4
pairs, lim = load_limitless()
K = len(pairs)
decks = sorted({d for k in pairs for d in k})
members = {d: [(i, 1 if k[0] == d else -1) for i, k in enumerate(pairs) if d in k] for d in decks}
assert all(len(v) == 9 for v in members.values()) and len(decks) == 10


def deck_avg(v):
    return [sum((v[i] if s == 1 else 1 - v[i]) for i, s in members[d]) / 9 for d in decks]


def stats(Nv, Ov, Lv, w):
    cell = sum((Nv[j] - Lv[j]) ** 2 - (Ov[j] - Lv[j]) ** 2 for j in range(K)) / K * 1e4
    cellw = sum(w[j] * ((Nv[j] - Lv[j]) ** 2 - (Ov[j] - Lv[j]) ** 2) for j in range(K)) / K * 1e4
    Nd, Od, Ld = deck_avg(Nv), deck_avg(Ov), deck_avg(Lv)
    deck = sum((Nd[j] - Ld[j]) ** 2 - (Od[j] - Ld[j]) ** 2 for j in range(10)) / 10 * 1e4
    return cell, cellw, deck


def sd(v):
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


reps = 8000
for name in ["koh3_vs_kog3", "kpf3_vs_kp3", "kpr3_vs_kp3", "kog3_vs_kp3", "kpg3_vs_kp3", "kog3_vs_kpg3"]:
    op, np_, on, nn = readings()[name]
    deals = load_reading(op, np_, pairs)
    O, N, L0, nL, n = cell_stats(pairs, lim, deals)
    P = prep_cells(pairs, deals)
    Ol = [O[k] for k in pairs]; Nl = [N[k] for k in pairs]; Ll = [L0[k] for k in pairs]
    w = [1 / (L0[k] * (1 - L0[k]) / nL[k] + TAU0SQ) for k in pairs]
    mw = sum(w) / K
    w = [x / mw for x in w]
    pt = stats(Nl, Ol, Ll, w)
    rng = random.Random(4242)
    R = {m: ([], [], []) for m in ("both", "sim", "lim")}
    for _ in range(reps):
        Ls = [rng.binomialvariate(nL[k], L0[k]) / nL[k] for k in pairs]
        Os, Ns = [], []
        for k in pairs:
            a, b = draw_sim(rng, P[k]); Os.append(a); Ns.append(b)
        for m, args in (("both", (Ns, Os, Ls)), ("sim", (Ns, Os, Ll)), ("lim", (Nl, Ol, Ls))):
            s = stats(*args, w)
            for i in range(3):
                R[m][i].append(s[i])
    print(f"== {nn} vs {on}")
    for i, lab in enumerate(("cell (45, unweighted)", "cell weighted by reliability", "deck (10 deck averages)")):
        sb, ss, sl = sd(R["both"][i]), sd(R["sim"][i]), sd(R["lim"][i])
        print(f"  {lab:<30} point {pt[i]:+7.1f}  sd {sb:6.1f} (sim {ss:5.1f}, Limitless {sl:5.1f}; Limitless share {100 * sl * sl / (ss * ss + sl * sl):3.0f}%)  z = {pt[i] / sb:+5.2f}  95% half-width {1.96 * sb:5.1f}")
