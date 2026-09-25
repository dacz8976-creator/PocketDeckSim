#!/usr/bin/env python3
"""Read legality_scan tables against Limitless with the rules agreed on Sept 24 (Fable + Claude Code).

Unpaired (per-cell rates only, as printed by the scan; vetoes and verdict are indicative):
    score.py <scan file> [<scan file> ...] --old k3 --new b3o3n4
Paired by deal (per-game files from legality_scan --games-out; this is the reading that decides):
    score.py --old-games k3_games.jsonl --new-games b3n1_games.jsonl [--old k3 --new b3n1]

Limitless cells and the scoreboard's own metrics come from rl/results/deep_search_table/deep_table.py.
Rules (section 8 of docs/REVIEW_2026-09-24_direction.md):
- Adoption: dMSE = mean over cells of (S_new - L)^2 - (S_old - L)^2; adopt only if the whole 95% interval is
  below 0 and no veto (a cell's miss grows by more than 6 points; a deck's 7-opponent gap grows by more than 2;
  a held-out deck moves more than 2 further, checked elsewhere). Vetoes are valid on paired readings only.
- Variant margin: real error tau = sqrt(mean[(S-L)^2 - SE_L^2 - SE_S^2]) in points; 90% interval of
  (cheap tau - expensive tau); E = 3.
- PASS: (a) tau <= 5.5; (b) every cell |S-L| - 1.96*sqrt(SE_L^2 + SE_S^2) <= 10; (c) every deck within 6.
- Altaria v Sceptile is quarantined (drift); decisions use the other 27 cells. Sceptile v Vespiquen counts but is
  drift-sensitive (see QUARANTINE below).
- Correlation, average miss, favorites right, pairings beyond chance: reported only.
Bootstrap: Limitless cells redrawn from Binomial(n, L); the simulator side is resampled by deal within each cell
(paired: the same deals for both bots) or, unpaired, drawn from Binomial(n, S) for each bot separately.
"""
import argparse, json, math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "deep_search_table"))
import deep_table as D  # noqa: E402

# Altaria v Sceptile stays quarantined: early play 37.5% (n 28) vs late 48.1% (n 80) in the development half,
# and the simulator's 38.3 matches early play. Sceptile v Vespiquen was lifted on Sept 25 (B6: the sim's 66 misses
# both halves, 45.0% early and 25.0% late) but is drift-sensitive: a fix landing near 60 matched early play only.
QUARANTINE = {("altaria", "sceptile")}


def parse_text(paths):
    cells, games = {}, {}
    for path in paths:
        bot = None
        for line in open(path, encoding="utf-8"):
            m = re.match(r"== (\S+)", line)
            if m and m.group(1) != "end":
                bot = m.group(1)
                continue
            m = re.match(r"bot (\S+), (\d+) table deals", line)
            if m:
                bot, games[m.group(1)] = m.group(1), int(m.group(2))
                continue
            m = re.match(r"\s*(\w+) v (\w+)\s+first deck\s+([\d.]+)%", line)
            if m and bot:
                cells.setdefault(bot, {})[(m.group(1), m.group(2))] = float(m.group(3)) / 100
    return cells, games


def parse_games(path):
    """{(a, b): {i: score of deck a}} from a --games-out file."""
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        k = (r["a"], r["b"]) if "a" in r else D.PAIRS[r["pairing"]]
        s = r.get("first_deck_score", r.get("score_a", r.get("score_first")))
        out.setdefault(k, {})[r["i"]] = float(s)
    return out


def lim(k):
    w, l, t = D.LIMITLESS[k]
    n = w + l + t
    return (w + 0.5 * t) / n, n


def deck_avgs(score, keys):
    tot = {}
    for a, b in keys:
        tot.setdefault(a, []).append(score[(a, b)])
        tot.setdefault(b, []).append(1 - score[(a, b)])
    return {d: sum(v) / len(v) for d, v in tot.items()}


def tau(S, nS, L, nL, keys):
    acc = 0.0
    for k in keys:
        acc += (S[k] - L[k]) ** 2 - L[k] * (1 - L[k]) / nL[k] - S[k] * (1 - S[k]) / nS[k]
    return 100 * math.sqrt(max(0.0, acc / len(keys)))


def pass_parts(S, nS, keys):
    L = {k: lim(k)[0] for k in keys}
    nL = {k: lim(k)[1] for k in keys}
    t = tau(S, nS, L, nL, keys)
    fails_b = [k for k in keys if 100 * (abs(S[k] - L[k]) - 1.96 * math.sqrt(L[k] * (1 - L[k]) / nL[k] + S[k] * (1 - S[k]) / nS[k])) > 10]
    ds, dl = deck_avgs(S, keys), deck_avgs(L, keys)
    fails_c = sorted(d for d in ds if abs(ds[d] - dl[d]) * 100 > 6)
    return t, fails_b, fails_c


def pct(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--old", default="k3")
    ap.add_argument("--new", default=None)
    ap.add_argument("--old-games")
    ap.add_argument("--new-games")
    ap.add_argument("--reps", type=int, default=4000)
    a = ap.parse_args()
    paired = bool(a.old_games and a.new_games)
    if paired:
        Og, Ng = parse_games(a.old_games), parse_games(a.new_games)
        allk = [k for k in D.PAIRS if k in Og and k in Ng]
        deals = {k: sorted(set(Og[k]) & set(Ng[k])) for k in allk}
        O = {k: sum(Og[k][i] for i in deals[k]) / len(deals[k]) for k in allk}
        N = {k: sum(Ng[k][i] for i in deals[k]) / len(deals[k]) for k in allk}
        nO = nN = {k: len(deals[k]) for k in allk}
        new_name = a.new or os.path.basename(a.new_games)
        src = f"{a.old_games} (current) vs {a.new_games} (new), paired by deal"
    else:
        cells, games = parse_text(a.files)
        new_name = a.new
        O, N = cells[a.old], cells[a.new]
        allk = [k for k in D.PAIRS if k in O and k in N]
        nO = {k: games[a.old] for k in allk}
        nN = {k: games[a.new] for k in allk}
        src = ", ".join(a.files) + " (per-cell rates only: UNPAIRED, vetoes and verdict indicative)"
    qk = [k for k in allk if k not in QUARANTINE]
    out = []
    p = out.append
    p(f"Reading: {new_name} (new) against {a.old} (current), {len(allk)} common pairings.")
    p(f"Source: {src}")
    p("")
    for label, keys in (("all cells", allk), ("decision set (Altaria v Sceptile quarantined)", qk)):
        p(f"== {label}: {len(keys)} pairings")
        for bot, S, nS in ((a.old, O, nO), (new_name, N, nN)):
            sc = D.score_table({k: 100 * S[k] for k in keys}, {k: nS[k] for k in keys})
            t, fb, fc = pass_parts(S, nS, keys)
            p(f"  {bot:>10}: real error {t:4.1f} | reported only: correlation {sc['correlation']:.2f}, average miss "
              f"{sc['average_miss']:.1f}, favorite right {sc['favorite_right']}/{len(keys)}, clear {sc['clear_right']}/"
              f"{sc['clear']}, beyond chance {sc['beyond_chance']}")
            p(f"              PASS (a) real error <= 5.5: {'yes' if t <= 5.5 else 'no'} | (b) cells over by >10 beyond "
              f"noise: {', '.join(f'{x} v {y}' for x, y in fb) or 'none'} | (c) decks off by >6: {', '.join(fc) or 'none'}")
        rng = random.Random(20260924)
        L0 = {k: lim(k)[0] for k in keys}
        nL = {k: lim(k)[1] for k in keys}
        d_point = sum((N[k] - L0[k]) ** 2 - (O[k] - L0[k]) ** 2 for k in keys) / len(keys) * 1e4
        t_point = tau(O, nO, L0, nL, keys) - tau(N, nN, L0, nL, keys)
        dm, dt = [], []
        for _ in range(a.reps):
            Ls = {k: rng.binomialvariate(nL[k], L0[k]) / nL[k] for k in keys}
            if paired:
                Os, Ns = {}, {}
                for k in keys:
                    idx = [deals[k][rng.randrange(len(deals[k]))] for _ in deals[k]]
                    Os[k] = sum(Og[k][i] for i in idx) / len(idx)
                    Ns[k] = sum(Ng[k][i] for i in idx) / len(idx)
            else:
                Os = {k: rng.binomialvariate(nO[k], O[k]) / nO[k] for k in keys}
                Ns = {k: rng.binomialvariate(nN[k], N[k]) / nN[k] for k in keys}
            dm.append(sum((Ns[k] - Ls[k]) ** 2 - (Os[k] - Ls[k]) ** 2 for k in keys) / len(keys) * 1e4)
            dt.append(tau(Os, nO, Ls, nL, keys) - tau(Ns, nN, Ls, nL, keys))
        dm.sort(); dt.sort()
        lo, hi = pct(dm, 0.025), pct(dm, 0.975)
        grow = [(k, 100 * (abs(N[k] - L0[k]) - abs(O[k] - L0[k]))) for k in keys]
        cell_veto = [(k, g) for k, g in grow if g > 6]
        do, dn, dl = deck_avgs(O, keys), deck_avgs(N, keys), deck_avgs(L0, keys)
        deck_ch = {d: 100 * (abs(dn[d] - dl[d]) - abs(do[d] - dl[d])) for d in dl}
        deck_veto = [(d, g) for d, g in deck_ch.items() if g > 2]
        adopt = hi < 0 and not cell_veto and not deck_veto
        tag = "" if paired else " [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]"
        p(f"  dMSE new - current: {d_point:+.1f} points^2, 95% interval {lo:+.1f} to {hi:+.1f} ({'below 0' if hi < 0 else 'not below 0'})")
        p(f"  real error, current minus new: {t_point:+.2f} points, 90% interval {pct(dt, 0.05):+.2f} to {pct(dt, 0.95):+.2f}"
          f" (margin rule: E = 3; 'current' is the cheap bot when comparing variants)")
        p(f"  cell veto (miss grows > 6): {', '.join(f'{x} v {y} +{g:.1f}' for (x, y), g in cell_veto) or 'none'}{tag}")
        p(f"  deck veto (gap grows > 2): {', '.join(f'{d} +{g:.1f}' for d, g in deck_veto) or 'none'}{tag}")
        p(f"  ADOPTION RULE: {'adopt' if adopt else 'do not adopt'}{tag} (held-out-deck veto checked separately)")
        p("")
        p(f"  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):")
        for d in D.NAMES:
            if d in dl:
                p(f"    {d:>9}: {100 * do[d]:5.1f} / {100 * dn[d]:5.1f} / {100 * dl[d]:5.1f}   {deck_ch[d]:+.1f}")
        p("")
    p("Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)")
    for k in allk:
        L, n_l = lim(k)
        hw = 196 * math.sqrt(L * (1 - L) / n_l)
        g = 100 * (abs(N[k] - L) - abs(O[k] - L))
        q = "  (quarantined)" if k in QUARANTINE else ""
        p(f"  {k[0]:>9} v {k[1]:<10} {100 * O[k]:5.1f} | {100 * N[k]:5.1f} | {100 * L:5.1f} ± {hw:4.1f} | {g:+.1f}{q}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
