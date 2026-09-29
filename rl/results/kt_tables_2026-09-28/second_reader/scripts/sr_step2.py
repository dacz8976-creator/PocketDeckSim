"""Steps 2 and 3: kt3 on the ordinary rule and kta3 on the reserve route, with the second reader's own arithmetic.
usage: sr_step2.py CODE [reps]"""
import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader")
from sr_lib import *

code = sys.argv[1]
reps = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
lim = limitless45()
KOG = [R + "/kog_composition_2026-09-27/table_kog3.jsonl", R + "/kog_composition_2026-09-27/new17_kog3.jsonl"]
O_g = load(KOG, ab)
N_g = load([f"{K}/{B}_{code}_table.jsonl", f"{K}/{B}_{code}_new17.jsonl"], ab)
MF = load([f"{K}/{B}_mixed_table_{code}_first.jsonl", f"{K}/{B}_mixed_new17_{code}_first.jsonl"], ab)
MS = load([f"{K}/{B}_mixed_table_{code}_second.jsonl", f"{K}/{B}_mixed_new17_{code}_second.jsonl"], ab)
for k in CELLS45:
    assert set(O_g[k]) == set(N_g[k]) == set(MF[k]) == set(MS[k])
    for i in O_g[k]:
        assert O_g[k][i]["seed"] == N_g[k][i]["seed"] == MF[k][i]["seed"] == MS[k][i]["seed"]
        assert (MF[k][i]["bot_a"], MF[k][i]["bot_b"]) == (code, "kog3"), (k, i)
        assert (MS[k][i]["bot_a"], MS[k][i]["bot_b"]) == ("kog3", code), (k, i)
        assert (N_g[k][i]["bot_a"], N_g[k][i]["bot_b"]) == (code, code)

L = {k: lim_rate(lim, k)[0] for k in CELLS45}
nL = {k: lim_rate(lim, k)[1] for k in CELLS45}
O = cell_means(O_g, CELLS45)
N = cell_means(N_g, CELLS45)
nS = {k: len(O_g[k]) for k in CELLS45}
Q = [k for k in CELLS45 if k not in QUARANTINE]

# own-side changes: {cell: {deck: [per-deal points]}}
own = {}
for k in CELLS45:
    own[k] = {k[0]: paired_change(O_g[k], MF[k], +1), k[1]: paired_change(O_g[k], MS[k], -1)}


def report(keys, label):
    print(f"\n=== {code} v kog3: {label} ({len(keys)} cells)")
    d_point = sum((N[k] - L[k]) ** 2 - (O[k] - L[k]) ** 2 for k in keys) / len(keys) * 1e4
    to, tn = tau(O, nS, L, nL, keys), tau(N, nS, L, nL, keys)
    print(f"  dMSE ({code} - kog3): {d_point:+.2f} points^2")
    print(f"  real error kog3 {to:.2f}  {code} {tn:.2f}   margin (kog3 - {code}) {to - tn:+.3f}")
    grow = {k: 100 * (abs(N[k] - L[k]) - abs(O[k] - L[k])) for k in keys}
    cell_veto = [(k, g) for k, g in grow.items() if g > 6]
    do, dn, dl = deck_avgs(O, keys), deck_avgs(N, keys), deck_avgs(L, keys)
    deck_ch = {d: 100 * (abs(dn[d] - dl[d]) - abs(do[d] - dl[d])) for d in dl}
    deck_veto = [(d, g) for d, g in deck_ch.items() if g > 2]
    print("  cell misses growing > 6:", [(f"{a} v {b}", round(g, 2)) for (a, b), g in cell_veto] or "none")
    print("  deck gaps growing > 2:", [(d, round(g, 2)) for d, g in deck_veto] or "none")
    print("  all deck gap changes:", {d: round(v, 2) for d, v in sorted(deck_ch.items())})
    print("  max cell miss growth:", max(((round(g, 2), f"{a} v {b}") for (a, b), g in grow.items())))
    counted = []
    for (a, b), g in cell_veto:
        band = 196 * math.sqrt(L[(a, b)] * (1 - L[(a, b)]) / nL[(a, b)])
        sides = {d: pool([v]) for d, v in own[(a, b)].items()}
        worse = [d for d, (m, h, _) in sides.items() if m < -h]
        print(f"   cell veto {a} v {b} +{g:.1f}: band ±{band:.1f}; sides " + "; ".join(f"{d} {m:+.1f} ± {h:.1f}" for d, (m, h, _) in sides.items()) + (" -> COUNTS" if worse and band <= 15 else " -> does not count"))
        if worse and band <= 15:
            counted.append(f"{a} v {b}")
    for d, g in deck_veto:
        dk = [k for k in keys if d in k]
        own_parts = [own[k][d] for k in dk]
        opp_parts = [own[k][k[1] if k[0] == d else k[0]] for k in dk]
        mo, ho, _ = pool(own_parts)
        mp, hp, _ = pool(opp_parts)
        worse = mo < -ho or mp < -hp
        print(f"   deck veto {d} +{g:.1f}: own side {mo:+.2f} ± {ho:.2f}; opponents' side {mp:+.2f} ± {hp:.2f} -> {'COUNTS' if worse else 'investigation item (neither side worse)'}")
        if worse:
            counted.append(d)
    print("  vetoes that count under rule v2:", counted or "none")
    # deck table
    print("  deck averages kog3 / new / Limitless / change in miss:")
    for d in DECKS10:
        if d in dl:
            print(f"     {d:>17}: {100*do[d]:5.1f} / {100*dn[d]:5.1f} / {100*dl[d]:5.1f}  {deck_ch[d]:+.2f}")
    # analytic (delta-method) interval for dMSE
    var = 0.0
    for k in keys:
        n = nS[k]
        a_ = 2 * (N[k] - L[k])
        b_ = -2 * (O[k] - L[k])
        ni = [score(N_g[k][i]) for i in sorted(N_g[k])]
        oi = [score(O_g[k][i]) for i in sorted(O_g[k])]
        z = [a_ * x + b_ * y for x, y in zip(ni, oi)]
        m, v = mean_var_of_mean(z)
        var += v + (2 * (O[k] - N[k])) ** 2 * (L[k] * (1 - L[k]) / nL[k])
    sd = math.sqrt(var) / len(keys) * 1e4
    print(f"  delta-method interval for dMSE: {d_point:+.2f} ± {1.96*sd:.2f} -> ({d_point-1.96*sd:+.1f}, {d_point+1.96*sd:+.1f}); sd {sd:.2f}")
    return d_point, to - tn


def own_boot(keys, reps, seed):
    rng = random.Random(seed)
    Oi = {k: [score(O_g[k][i]) for i in sorted(O_g[k])] for k in keys}
    Ni = {k: [score(N_g[k][i]) for i in sorted(N_g[k])] for k in keys}
    dm, dt = [], []
    for _ in range(reps):
        Ls = {k: rng.binomialvariate(nL[k], L[k]) / nL[k] for k in keys}
        Os, Ns = {}, {}
        for k in keys:
            n = nS[k]
            idx = rng.choices(range(n), k=n)
            g = Oi[k].__getitem__
            h = Ni[k].__getitem__
            Os[k] = sum(map(g, idx)) / n
            Ns[k] = sum(map(h, idx)) / n
        dm.append(sum((Ns[k] - Ls[k]) ** 2 - (Os[k] - Ls[k]) ** 2 for k in keys) / len(keys) * 1e4)
        dt.append(tau(Os, nS, Ls, nL, keys) - tau(Ns, nS, Ls, nL, keys))
    dm.sort(); dt.sort()
    return (pct(dm, 0.025), pct(dm, 0.975)), (pct(dt, 0.05), pct(dt, 0.95)), (pct(dt, 0.025), pct(dt, 0.975)), (sum(dm) / len(dm), sum(dt) / len(dt))


r45 = report(CELLS45, "all 45 cells")
r44 = report(Q, "decision set, Altaria v Sceptile quarantined")
for keys, label in ((CELLS45, "45"), (Q, "44")):
    bi = own_boot(keys, reps, 777001 if label == "45" else 777002)
    print(f"\n  own bootstrap ({reps} reps, {label} cells): dMSE 95% {bi[0][0]:+.1f} to {bi[0][1]:+.1f}; margin 90% {bi[1][0]:+.3f} to {bi[1][1]:+.3f} (95%: {bi[2][0]:+.3f} to {bi[2][1]:+.3f}); boot means dMSE {bi[3][0]:+.2f} margin {bi[3][1]:+.3f}")
