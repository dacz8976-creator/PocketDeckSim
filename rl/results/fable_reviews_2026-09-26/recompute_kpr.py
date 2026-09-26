#!/usr/bin/env python3
"""Independent recompute of the cloud's kpr3 readout (rl/results/kpr_2026-09-25/README.md on the cloud branch):
"mean squared miss 176.1 against kp3's 112.2".

    python recompute_kpr.py --kpr3 <kpr3_500.jsonl> [--out <folder>]

Inputs (read only):
  kpr3: the branch's rl/results/kpr_2026-09-25/kpr3_500.jsonl (28 pairings x 500 table deals, kpr3 on both sides)
  kp3:  rl/results/public_pricing_2026-09-25/kp3_500_worst5.jsonl + kp3_500_rest.jsonl (the laptop's kp3 table)
        cross-checked field by field against rl/results/engine_identity_2026-09-25/kp3_500.jsonl
  k3:   rl/results/per_game_table_2026-09-25/k3_500.jsonl (reference row)
  Limitless, Sept 23 table: rl/results/deep_search_table/deep_table.py (LIMITLESS), the cells score.py uses by default
  Limitless, scoreboard v2 (development half): rl/results/scoreboard_v2_2026-09-25/limitless_v2_dev.json

Definitions, taken from rl/results/table_readings_2026-09-24/score.py and recomputed here from scratch:
  cell score S   = mean over the cell's deals of the first-named deck's score (1 win, 0.5 tie, 0 loss), in %
  Limitless L    = (W + T/2) / n, in %
  mean squared miss (MSE) = mean over cells of (S - L)^2, points^2;  mean |miss| likewise
  real error tau = 100 * sqrt(max(0, mean over cells of [(S-L)^2 - L(1-L)/n_L - S(1-S)/n_S])) on fractions
  dMSE           = MSE(kpr3) - MSE(kp3), paired by deal; 95% interval by bootstrap (deals resampled within each cell,
                   the same deals for both bots; Limitless cells redrawn Binomial(n_L, L)); 4,000 replicates
  tau margin     = tau(kp3) - tau(kpr3), 90% interval from the same replicates
  cell veto      = a cell's |miss| grows by more than 6; deck veto = a deck's 7-opponent gap grows by more than 2
                   (point estimates only: whether a veto COUNTS under rule v2 needs the laptop's mixed rows)
Cell sets: all 28; the decision set of 27 (Altaria v Sceptile quarantined).
The bootstrap resamples each cell's deals by a multinomial over the (kp3, kpr3) outcome pairs, which is the same
distribution as drawing 500 deal indices with replacement, but a different code path from score.py's.
"""
import argparse, json, math, os, random, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(RES, "deep_search_table"))
import deep_table as D  # noqa: E402  (LIMITLESS, PAIRS, NAMES; importing runs nothing)

QUARANTINE = {("altaria", "sceptile")}
FIELDS = ("a", "b", "seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score")


def load(paths):
    out = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    k = (r["a"], r["b"])
                    if r["i"] in out.setdefault(k, {}):
                        raise SystemExit(f"{p}: deal {r['i']} of {k} twice")
                    out[k][r["i"]] = r
    return out


def identical(g1, g2):
    n = same = 0
    for k in g1:
        for i in g1[k]:
            n += 1
            r1, r2 = g1[k][i], g2.get(k, {}).get(i)
            if r2 is not None and all(r1.get(f) == r2.get(f) for f in FIELDS):
                same += 1
    return same, n, sum(len(c) for c in g2.values())


def lim_from(table):
    """{(a,b): (L fraction, n)}"""
    return {k: ((w + 0.5 * t) / (w + l + t), w + l + t) for k, (w, l, t) in table.items()}


def cells(games, deals):
    return {k: sum(games[k][i]["first_deck_score"] for i in deals[k]) / len(deals[k]) for k in deals}


def tau(S, nS, L, nL, keys):
    acc = sum((S[k] - L[k]) ** 2 - L[k] * (1 - L[k]) / nL[k] - S[k] * (1 - S[k]) / nS[k] for k in keys)
    return 100 * math.sqrt(max(0.0, acc / len(keys)))


def mse(S, L, keys):
    return 1e4 * sum((S[k] - L[k]) ** 2 for k in keys) / len(keys)


def mae(S, L, keys):
    return 100 * sum(abs(S[k] - L[k]) for k in keys) / len(keys)


def deck_avgs(S, keys):
    tot = {}
    for a, b in keys:
        tot.setdefault(a, []).append(S[(a, b)])
        tot.setdefault(b, []).append(1 - S[(a, b)])
    return {d: sum(v) / len(v) for d, v in tot.items()}


def multinomial(rng, n, probs):
    """Counts of n draws over categories with the given probabilities, by sequential binomials."""
    out, left, pleft = [], n, 1.0
    for p in probs:
        if left == 0 or pleft <= 0:
            out.append(0)
            continue
        q = min(1.0, max(0.0, p / pleft))
        c = rng.binomialvariate(left, q)
        out.append(c)
        left -= c
        pleft -= p
    if left:  # rounding remainder onto the last category
        out[-1] += left
    return out


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, max(0, int(q * len(v))))]


def bootstrap(base, other, deals, L, nL, keys, reps, seed):
    """dMSE (other - base) 95% and tau margin (base - other) 90%, paired by deal."""
    rng = random.Random(seed)
    cats = {}
    for k in keys:
        c = Counter((base[k][i]["first_deck_score"], other[k][i]["first_deck_score"]) for i in deals[k])
        n = len(deals[k])
        cats[k] = ([pair for pair in c], [c[pair] / n for pair in c], n)
    nS = {k: len(deals[k]) for k in keys}
    dm, dt = [], []
    for _ in range(reps):
        Ls = {k: rng.binomialvariate(nL[k], L[k]) / nL[k] for k in keys}
        Bs, Os = {}, {}
        for k in keys:
            pairs, probs, n = cats[k]
            cnt = multinomial(rng, n, probs)
            Bs[k] = sum(c * p[0] for c, p in zip(cnt, pairs)) / n
            Os[k] = sum(c * p[1] for c, p in zip(cnt, pairs)) / n
        dm.append(mse(Os, Ls, keys) - mse(Bs, Ls, keys))
        dt.append(tau(Bs, nS, Ls, nL, keys) - tau(Os, nS, Ls, nL, keys))
    return (pct(dm, 0.025), pct(dm, 0.975)), (pct(dt, 0.05), pct(dt, 0.95))


def paired_cell(base, other, deals, k, flip=False):
    d = [(other[k][i]["first_deck_score"] - base[k][i]["first_deck_score"]) * (-1 if flip else 1) for i in deals[k]]
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / max(n - 1, 1))
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n)


def paired_deck_pooled(base, other, deals, deck, keys):
    """The cloud's deck_averages.py --paired: all the deck's deals pooled, mean change and 95% half-width."""
    d = []
    for k in keys:
        if deck not in k:
            continue
        flip = k[1] == deck
        for i in deals[k]:
            x = other[k][i]["first_deck_score"] - base[k][i]["first_deck_score"]
            d.append(-x if flip else x)
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / max(n - 1, 1))
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kpr3", required=True, help="kpr3_500.jsonl (copied from the cloud branch)")
    ap.add_argument("--reps", type=int, default=4000)
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()

    out = []
    p = out.append
    kp3_paths = [os.path.join(RES, "public_pricing_2026-09-25", f) for f in ("kp3_500_worst5.jsonl", "kp3_500_rest.jsonl")]
    kp3_ref = os.path.join(RES, "engine_identity_2026-09-25", "kp3_500.jsonl")
    k3_path = os.path.join(RES, "per_game_table_2026-09-25", "k3_500.jsonl")
    v2_path = os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json")

    KP3, KPR3, K3 = load(kp3_paths), load([a.kpr3]), load([k3_path])
    same, n1, n2 = identical(KP3, load([kp3_ref]))
    p(f"kp3 table: {' + '.join(os.path.relpath(x, RES) for x in kp3_paths)}: {n1:,} games; "
      f"identical to engine_identity_2026-09-25/kp3_500.jsonl on {', '.join(FIELDS)}: {same:,} of {n1:,} ({n2:,} there)")
    p(f"kpr3 table: {a.kpr3}: {sum(len(c) for c in KPR3.values()):,} games")
    p(f"k3 table: {os.path.relpath(k3_path, RES)}: {sum(len(c) for c in K3.values()):,} games")
    bots = {(r.get("bot_a"), r.get("bot_b")) for c in KPR3.values() for r in c.values()}
    p(f"kpr3 file bots: {sorted(bots)}")

    allk = [k for k in D.PAIRS if k in KP3 and k in KPR3 and k in K3]
    deals = {k: sorted(set(KP3[k]) & set(KPR3[k]) & set(K3[k])) for k in allk}
    bad = [(k, i) for k in allk for i in deals[k] if len({KP3[k][i]["seed"], KPR3[k][i]["seed"], K3[k][i]["seed"]}) != 1]
    if bad:
        raise SystemExit(f"seed mismatch at {bad[0]}")
    p(f"pairings in all three files: {len(allk)}; deals per pairing: {min(len(v) for v in deals.values())}"
      f"-{max(len(v) for v in deals.values())}; seeds agree on every deal (paired by deal)")
    p("")

    S = {"k3": cells(K3, deals), "kp3": cells(KP3, deals), "kpr3": cells(KPR3, deals)}
    nS = {k: len(deals[k]) for k in allk}
    with open(v2_path, encoding="utf-8") as f:
        v2 = {tuple(k.split("|")): tuple(v) for k, v in json.load(f)["cells"].items()}
    tables = {"Sept 23 table (deep_table.py, the cloud's cells)": lim_from(D.LIMITLESS),
              "scoreboard v2, development half (limitless_v2_dev.json)": lim_from(v2)}
    sets = {"all 28 cells": allk, "decision set, 27 cells (Altaria v Sceptile quarantined)": [k for k in allk if k not in QUARANTINE]}

    summary = {}
    for tname, LT in tables.items():
        L = {k: LT[k][0] for k in allk}
        nL = {k: LT[k][1] for k in allk}
        for sname, keys in sets.items():
            p(f"== {tname}; {sname}")
            p(f"  {'bot':5} {'mean |miss|':>11} {'mean sq miss':>13} {'real error':>10}")
            for bot in ("k3", "kp3", "kpr3"):
                p(f"  {bot:5} {mae(S[bot], L, keys):11.2f} {mse(S[bot], L, keys):13.1f} {tau(S[bot], nS, L, nL, keys):10.1f}")
            d_point = mse(S["kpr3"], L, keys) - mse(S["kp3"], L, keys)
            t_point = tau(S["kp3"], nS, L, nL, keys) - tau(S["kpr3"], nS, L, nL, keys)
            (lo, hi), (tlo, thi) = bootstrap(KP3, KPR3, deals, L, nL, keys, a.reps, 20260926)
            p(f"  dMSE kpr3 - kp3: {d_point:+.1f} points^2, 95% {lo:+.1f} to {hi:+.1f} ({'below 0' if hi < 0 else 'not below 0'})")
            p(f"  real error, kp3 minus kpr3: {t_point:+.2f} points, 90% {tlo:+.2f} to {thi:+.2f} (margin rule E = 3)")
            grow = [(k, 100 * (abs(S['kpr3'][k] - L[k]) - abs(S['kp3'][k] - L[k]))) for k in keys]
            cv = [(k, g) for k, g in grow if g > 6]
            wide = {k for k in keys if 196 * math.sqrt(L[k] * (1 - L[k]) / nL[k]) > 15.0}
            p("  cell veto candidates (miss grows > 6): " + (", ".join(
                f"{x} v {y} +{g:.1f}" + (" [band > 15: never counts]" if (x, y) in wide else "") for (x, y), g in cv) or "none"))
            dk, dp, dl = deck_avgs(S["kp3"], keys), deck_avgs(S["kpr3"], keys), deck_avgs(L, keys)
            d3 = deck_avgs(S["k3"], keys)
            dch = {d: 100 * (abs(dp[d] - dl[d]) - abs(dk[d] - dl[d])) for d in dl}
            p("  deck veto candidates (gap grows > 2): " + (", ".join(f"{d} +{g:.1f}" for d, g in dch.items() if g > 2) or "none"))
            p(f"  Deck averages: {'deck':10} {'Limitless':>9} {'k3':>6} {'kp3':>6} {'kpr3':>6} {'kpr3-kp3 (paired, pooled deals)':>32} {'gap change':>10}")
            for d in D.NAMES:
                m, h, n = paired_deck_pooled(KP3, KPR3, deals, d, keys)
                p(f"                 {d:10} {100 * dl[d]:9.1f} {100 * d3[d]:6.1f} {100 * dk[d]:6.1f} {100 * dp[d]:6.1f} "
                  f"{m:+8.1f} ± {h:.1f} ({n:,} deals){'':6} {dch[d]:+.1f}")
            p("")
            summary[(tname, sname)] = dict(mse_kp3=mse(S["kp3"], L, keys), mse_kpr3=mse(S["kpr3"], L, keys),
                                          mse_k3=mse(S["k3"], L, keys), tau_kp3=tau(S["kp3"], nS, L, nL, keys),
                                          tau_kpr3=tau(S["kpr3"], nS, L, nL, keys), dmse=d_point, dmse95=(lo, hi),
                                          tmargin=t_point, tmargin90=(tlo, thi))

    L23 = {k: tables["Sept 23 table (deep_table.py, the cloud's cells)"][k] for k in allk}
    LV2 = {k: tables["scoreboard v2, development half (limitless_v2_dev.json)"][k] for k in allk}
    p("Per cell (first-named deck's score, %): k3 | kp3 | kpr3 | kpr3-kp3 paired (95%) | Sept 23 L ± band | miss change | v2 L ± band | miss change")
    for k in allk:
        m, h = paired_cell(KP3, KPR3, deals, k)
        l23, n23 = L23[k]
        lv2, nv2 = LV2[k]
        b23 = 196 * math.sqrt(l23 * (1 - l23) / n23)
        bv2 = 196 * math.sqrt(lv2 * (1 - lv2) / nv2)
        g23 = 100 * (abs(S["kpr3"][k] - l23) - abs(S["kp3"][k] - l23))
        gv2 = 100 * (abs(S["kpr3"][k] - lv2) - abs(S["kp3"][k] - lv2))
        q = "  (quarantined)" if k in QUARANTINE else ""
        p(f"  {k[0]:>9} v {k[1]:<10} {100 * S['k3'][k]:5.1f} | {100 * S['kp3'][k]:5.1f} | {100 * S['kpr3'][k]:5.1f} | "
          f"{m:+5.1f} ({m - h:+.1f}, {m + h:+.1f}) | {100 * l23:5.1f} ± {b23:4.1f} | {g23:+5.1f} | {100 * lv2:5.1f} ± {bv2:4.1f} | {gv2:+5.1f}{q}")
    p("")
    p("Summary (mean squared miss kp3 -> kpr3; real error kp3 -> kpr3; dMSE 95%; tau margin 90%):")
    for (tname, sname), s in summary.items():
        p(f"  {tname}; {sname}: MSE {s['mse_kp3']:.1f} -> {s['mse_kpr3']:.1f} (k3 {s['mse_k3']:.1f}); tau {s['tau_kp3']:.1f} -> {s['tau_kpr3']:.1f}; "
          f"dMSE {s['dmse']:+.1f} ({s['dmse95'][0]:+.1f}, {s['dmse95'][1]:+.1f}); margin {s['tmargin']:+.2f} ({s['tmargin90'][0]:+.2f}, {s['tmargin90'][1]:+.2f})")
    text = "\n".join(out)
    print(text)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "recompute_kpr_output.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(os.path.join(a.out, "recompute_kpr_summary.json"), "w", encoding="utf-8") as f:
        json.dump({f"{t} | {s}": v for (t, s), v in summary.items()}, f, indent=1)


if __name__ == "__main__":
    main()
