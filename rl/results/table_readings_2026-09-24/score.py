#!/usr/bin/env python3
"""Read legality_scan tables against Limitless with the rules agreed on Sept 24 (Fable + Claude Code), refined Sept 25.

Unpaired (per-cell rates only, as printed by the scan; vetoes and verdict are indicative):
    score.py <scan file> [<scan file> ...] --old k3 --new b3o3n4
Paired by deal (per-game files from legality_scan --games-out; this is the reading that decides):
    score.py --old-games k3_games.jsonl --new-games b3n1_games.jsonl [--old k3 --new b3n1]
With mixed rows (the new bot on one side only, the same deals; any number of files, sorted by their bot_a/bot_b):
    score.py --old-games kp3.jsonl --new-games kd3.jsonl --mixed kd3_first.jsonl kp3_first.jsonl --old kp3 --new kd3
A deal's files may be split (e.g. worst5 + rest): pass them all after the flag.

Limitless cells and the scoreboard's own metrics come from rl/results/deep_search_table/deep_table.py.
Rules (section 8 of docs/REVIEW_2026-09-24_direction.md; rl/RUN5.md "Rules"):
- Adoption: dMSE = mean over cells of (S_new - L)^2 - (S_old - L)^2; adopt only if the whole 95% interval is
  below 0 and no veto (a cell's miss grows by more than 6 points; a deck's 7-opponent gap grows by more than 2;
  a held-out deck moves more than 2 further, checked elsewhere). Vetoes are valid on paired readings only.
  Which vetoes count depends on the rule version (RULES below; every reading prints the one it used):
  v1 (Sept 24): every veto counts. The Sept 24-25 readings (b3o3n4, b3n1, kp3, kq3) used v1 and keep it.
  v2 (pre-registered Sept 25, for tables read from then on): a veto counts only when mixed rows on the same deals
  show the changed pilot's own side got worse beyond the mixed row's paired noise (the 95% range of the per-deal
  differences, about +/-4 at 500 games), and never on a cell whose Limitless band is wider than +/-15 (BAND_MAX);
  otherwise it is an investigation item. For a cell (A, B): A's side is the row with the new bot on A only, B's side
  the row with it on B only, each against the current bot on both sides. For a deck D: D's side (new bot on D only)
  and the opponents' side (new bot on D's opponents only), each pooled over D's cells in the set (stratified: the
  mean of cell changes, variance summed per cell). A veto with no mixed rows showing a side worse, and some of its
  mixed rows missing, awaits them: the reading cannot adopt until they are in.
- Variant margin: real error tau = sqrt(mean[(S-L)^2 - SE_L^2 - SE_S^2]) in points; 90% interval of
  (cheap tau - expensive tau); E = 3.
- PASS: (a) tau <= 5.5; (b) every cell |S-L| - 1.96*sqrt(SE_L^2 + SE_S^2) <= 10; (c) every deck within 6.
- Altaria v Sceptile is quarantined (drift); decisions use the other 27 cells. Sceptile v Vespiquen counts but is
  drift-sensitive (see QUARANTINE below).
- Correlation, average miss, favorites right, pairings beyond chance: reported only.
Bootstrap: Limitless cells redrawn from Binomial(n, L); the simulator side is resampled by deal within each cell
(paired: the same deals for both bots) or, unpaired, drawn from Binomial(n, S) for each bot separately.
With --limitless-events, a second interval resamples the Limitless side by tournament event instead (matches within
an event share players and a field, so the binomial band is too narrow); the simulator draws are the same ones, and
the binomial interval is unchanged by the option. Both are reported until the event interval is made standard.
"""
import argparse, json, math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "deep_search_table"))
import deep_table as D  # noqa: E402

# Altaria v Sceptile stays quarantined: early play 37.5% (n 28) vs late 48.1% (n 80) in the development half,
# and the simulator's 38.3 matches early play. Sceptile v Vespiquen was lifted on Sept 25 (B6: the sim's 66 misses
# both halves, 45.0% early and 25.0% late) but is drift-sensitive: a fix landing near 60 matched early play only.
QUARANTINE = {("altaria", "sceptile")}

RULES = {
    "v1": "rules v1 (Sept 24): every cell and deck veto counts",
    "v2": "rules v2 (pre-registered Sept 25): a veto counts only when mixed rows on the same deals show the changed "
          "pilot's own side got worse beyond their paired noise, and never on a cell whose Limitless band is wider "
          "than +/-15; otherwise it is an investigation item",
}
# Points: the 95% binomial half-width of the Limitless cell as printed in the per-cell table. "About +/-15" was fixed at
# exactly 15.0 on Sept 25, before kd3's table and independently of any candidate; it is not moved after a reading.
# A band is wider than 15.0 only for a cell with fewer than 43 matches (at a 50% score; fewer still at lopsided scores).
# Coincidence noted in advance: on scoreboard v2, Hydreigon v Suicune (30.0%, 35 matches) has a band of +/-15.2, so it is
# out of cell vetoes by 0.2; the deck veto still covers Hydreigon and Suicune.
BAND_MAX = 15.0


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


def load_games(paths):
    """{(a, b): {i: record}} from one or more --games-out files; the record's score is under 's'."""
    out = {}
    for path in paths:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = (r["a"], r["b"]) if "a" in r else D.PAIRS[r["pairing"]]
            r["s"] = float(r.get("first_deck_score", r.get("score_a", r.get("score_first"))))
            cell = out.setdefault(k, {})
            if r["i"] in cell:
                raise SystemExit(f"{path}: deal {r['i']} of {k[0]} v {k[1]} appears twice")
            cell[r["i"]] = r
    return out


def bots_of(games):
    """The set of (bot_a, bot_b) in a per-game file, or None if it doesn't record them."""
    got = {(r.get("bot_a"), r.get("bot_b")) for cell in games.values() for r in cell.values()}
    return None if (None, None) in got else got


def same_deal(*recs):
    seeds = {r["seed"] for r in recs if "seed" in r}
    return len(seeds) <= 1


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


def diffs(base, other, flip):
    """Per-deal changes in points from base to other on their common deals; flip = read the second deck's side."""
    common = sorted(set(base) & set(other))
    bad = [i for i in common if not same_deal(base[i], other[i])]
    if bad:
        raise SystemExit(f"mixed rows: deal {bad[0]} has a different seed from the current bot's file")
    sign = -1 if flip else 1
    return [sign * 100 * (other[i]["s"] - base[i]["s"]) for i in common]


def mean_var(d):
    """Mean of per-deal differences and the variance of that mean."""
    n = len(d)
    m = sum(d) / n
    return m, sum((v - m) ** 2 for v in d) / max(n - 1, 1) / n


def side_change(parts):
    """Stratified pool over cells: (mean of cell means, 95% half-width, deals)."""
    mv = [mean_var(d) for d in parts]
    return sum(m for m, _ in mv) / len(mv), 1.96 * math.sqrt(sum(v for _, v in mv)) / len(mv), sum(len(d) for d in parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--old", default="k3")
    ap.add_argument("--new", default=None)
    ap.add_argument("--old-games", nargs="+")
    ap.add_argument("--new-games", nargs="+")
    ap.add_argument("--reps", type=int, default=4000)
    ap.add_argument("--limitless", help="JSON whose 'cells' are {\"a|b\": [W, L, T]}, replacing the Sept 23 cells "
                    "(scoreboard v2, ../scoreboard_v2_2026-09-25/limitless_v2_dev.json); default: deep_table.py's")
    ap.add_argument("--limitless-events", help="the same cells per tournament event (build_v2.py writes "
                    "limitless_v2_dev_events.json); adds the event-resampled dMSE and real-error intervals")
    ap.add_argument("--rules", choices=("v1", "v2"), required=True,
                    help="v1 for the Sept 24-25 readings (b3o3n4, b3n1, kp3, kq3); v2 for tables read from Sept 25 on")
    ap.add_argument("--mixed", nargs="+", default=[], help="per-game files with the new bot on one side only, on the "
                    "same deals (legality_scan --bot-a NEW --bot-b OLD, and --bot-a OLD --bot-b NEW, --games-out)")
    a = ap.parse_args()
    if a.limitless:
        with open(a.limitless, encoding="utf-8") as f:
            v2 = json.load(f)["cells"]
        D.LIMITLESS.clear()
        D.LIMITLESS.update({tuple(k.split("|")): tuple(v) for k, v in v2.items()})
    paired = bool(a.old_games and a.new_games)
    if paired:
        Ogr, Ngr = load_games(a.old_games), load_games(a.new_games)
        Og = {k: {i: r["s"] for i, r in c.items()} for k, c in Ogr.items()}
        Ng = {k: {i: r["s"] for i, r in c.items()} for k, c in Ngr.items()}
        allk = [k for k in D.PAIRS if k in Og and k in Ng]
        deals = {k: sorted(set(Og[k]) & set(Ng[k])) for k in allk}
        bad = [(k, i) for k in allk for i in deals[k] if not same_deal(Ogr[k][i], Ngr[k][i])]
        if bad:
            raise SystemExit(f"paired files disagree on the deal for {bad[0]}: different seeds")
        O = {k: sum(Og[k][i] for i in deals[k]) / len(deals[k]) for k in allk}
        N = {k: sum(Ng[k][i] for i in deals[k]) / len(deals[k]) for k in allk}
        nO = nN = {k: len(deals[k]) for k in allk}
        new_name = a.new or os.path.basename(a.new_games[0])
        src = f"{' + '.join(a.old_games)} (current) vs {' + '.join(a.new_games)} (new), paired by deal"
    else:
        cells, games = parse_text(a.files)
        new_name = a.new
        O, N = cells[a.old], cells[a.new]
        allk = [k for k in D.PAIRS if k in O and k in N]
        nO = {k: games[a.old] for k in allk}
        nN = {k: games[a.new] for k in allk}
        src = ", ".join(a.files) + " (per-cell rates only: UNPAIRED, vetoes and verdict indicative)"
    qk = [k for k in allk if k not in QUARANTINE]

    # Mixed rows: sort every game by which side the new bot is on, using the bot names the paired files record.
    mixed = {"first": {}, "second": {}}
    if a.mixed:
        if not paired:
            raise SystemExit("mixed rows need the paired per-game files (--old-games / --new-games)")
        ob, nb = bots_of(Ogr), bots_of(Ngr)
        if not ob or not nb or len(ob) != 1 or len(nb) != 1:
            raise SystemExit("mixed rows need bot_a/bot_b in the paired files, one bot per file")
        (old_bot, x), (new_bot, y) = ob.pop(), nb.pop()
        if old_bot != x or new_bot != y or old_bot == new_bot:
            raise SystemExit(f"paired files are not one bot on both sides: {old_bot}/{x}, {new_bot}/{y}")
        for k, cell in ((k, c) for path in a.mixed for k, c in load_games([path]).items()):
            for i, r in cell.items():
                side = {(new_bot, old_bot): "first", (old_bot, new_bot): "second"}.get((r.get("bot_a"), r.get("bot_b")))
                if side is None:
                    raise SystemExit(f"mixed row {k[0]} v {k[1]} deal {i}: bots {r.get('bot_a')}/{r.get('bot_b')} "
                                     f"are not {new_bot} on one side and {old_bot} on the other")
                if i in mixed[side].setdefault(k, {}):
                    raise SystemExit(f"mixed row {k[0]} v {k[1]} deal {i} ({side}) appears twice")
                mixed[side][k][i] = r

    events = None
    if a.limitless_events:
        with open(a.limitless_events, encoding="utf-8") as f:
            events = [{tuple(k.split("|")): tuple(v) for k, v in e["cells"].items()} for e in json.load(f)["events"]]
        total = {k: tuple(sum(e.get(k, (0, 0, 0))[j] for e in events) for j in range(3)) for k in allk}
        bad = [k for k in allk if total[k] != tuple(D.LIMITLESS[k])]
        if bad:
            raise SystemExit(f"--limitless-events does not sum to the Limitless cells in use for {bad[:3]}")

    out = []
    p = out.append
    p(f"Reading: {new_name} (new) against {a.old} (current), {len(allk)} common pairings.")
    p(f"Source: {src}")
    p(f"Limitless cells: {a.limitless or 'the Sept 23 table (deep_table.py)'}")
    if events:
        p(f"Limitless events: {a.limitless_events} ({len(events)} events)")
    p(f"Veto rule: {RULES[a.rules]}")
    if a.mixed:
        p(f"Mixed rows: {' + '.join(a.mixed)} ({sum(len(c) for c in mixed['first'].values())} games with {new_name} on "
          f"the first-named deck only, {sum(len(c) for c in mixed['second'].values())} on the second-named only)")
    p("")

    def own_changes(k):
        """{deck: per-deal changes of that deck's score with the new bot on that deck only} for cell k."""
        got = {}
        if k in mixed["first"]:
            got[k[0]] = diffs(Ogr[k], mixed["first"][k], flip=False)
        if k in mixed["second"]:
            got[k[1]] = diffs(Ogr[k], mixed["second"][k], flip=True)
        return got

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
        rng_e = random.Random(20260925)
        L0 = {k: lim(k)[0] for k in keys}
        nL = {k: lim(k)[1] for k in keys}
        d_point = sum((N[k] - L0[k]) ** 2 - (O[k] - L0[k]) ** 2 for k in keys) / len(keys) * 1e4
        t_point = tau(O, nO, L0, nL, keys) - tau(N, nN, L0, nL, keys)
        dm, dt, dm_e, dt_e, redrawn = [], [], [], [], 0
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
            if events:
                while True:  # a replicate where some cell has no match is drawn again (counted and reported)
                    draw = [events[rng_e.randrange(len(events))] for _ in events]
                    c = {k: [sum(e.get(k, (0, 0, 0))[j] for e in draw) for j in range(3)] for k in keys}
                    nE = {k: sum(c[k]) for k in keys}
                    if all(nE.values()):
                        break
                    redrawn += 1
                LE = {k: (c[k][0] + 0.5 * c[k][2]) / nE[k] for k in keys}
                dm_e.append(sum((Ns[k] - LE[k]) ** 2 - (Os[k] - LE[k]) ** 2 for k in keys) / len(keys) * 1e4)
                dt_e.append(tau(Os, nO, LE, nE, keys) - tau(Ns, nN, LE, nE, keys))
        dm.sort(); dt.sort(); dm_e.sort(); dt_e.sort()
        lo, hi = pct(dm, 0.025), pct(dm, 0.975)
        grow = [(k, 100 * (abs(N[k] - L0[k]) - abs(O[k] - L0[k]))) for k in keys]
        cell_veto = [(k, g) for k, g in grow if g > 6]
        do, dn, dl = deck_avgs(O, keys), deck_avgs(N, keys), deck_avgs(L0, keys)
        deck_ch = {d: 100 * (abs(dn[d] - dl[d]) - abs(do[d] - dl[d])) for d in dl}
        deck_veto = [(d, g) for d, g in deck_ch.items() if g > 2]
        tag = "" if paired else " [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]"
        p(f"  dMSE new - current: {d_point:+.1f} points^2, 95% interval {lo:+.1f} to {hi:+.1f} ({'below 0' if hi < 0 else 'not below 0'})"
          + (" [Limitless side binomial]" if events else ""))
        if events:
            lo_e, hi_e = pct(dm_e, 0.025), pct(dm_e, 0.975)
            p(f"  dMSE, Limitless side resampled by event: 95% interval {lo_e:+.1f} to {hi_e:+.1f} "
              f"({'below 0' if hi_e < 0 else 'not below 0'}; {redrawn} of {a.reps + redrawn} event draws redrawn because "
              f"a cell had no match)")
        p(f"  real error, current minus new: {t_point:+.2f} points, 90% interval {pct(dt, 0.05):+.2f} to {pct(dt, 0.95):+.2f}"
          f" (margin rule: E = 3; 'current' is the cheap bot when comparing variants)")
        if events:
            p(f"  real error, Limitless side resampled by event: 90% interval {pct(dt_e, 0.05):+.2f} to {pct(dt_e, 0.95):+.2f}")
        p(f"  cell veto (miss grows > 6): {', '.join(f'{x} v {y} +{g:.1f}' for (x, y), g in cell_veto) or 'none'}{tag}")
        p(f"  deck veto (gap grows > 2): {', '.join(f'{d} +{g:.1f}' for d, g in deck_veto) or 'none'}{tag}")
        counted, waiting = [], []
        if a.rules == "v1":
            counted = [f"{x} v {y}" for (x, y), _ in cell_veto] + [d for d, _ in deck_veto]
        else:
            for (x, y), g in cell_veto:
                L, n_l = lim((x, y))
                band = 196 * math.sqrt(L * (1 - L) / n_l)
                own = own_changes((x, y))
                sides = [f"{d}'s side {side_change([v])[0]:+.1f} ± {side_change([v])[1]:.1f}" for d, v in own.items()]
                worse = [d for d, v in own.items() if side_change([v])[0] < -side_change([v])[1]]
                if band > BAND_MAX:
                    why = f"never counts: Limitless band ±{band:.1f} is wider than ±{BAND_MAX:.0f}"
                elif worse:
                    why = f"COUNTS: {new_name} pilots {' and '.join(worse)} worse ({'; '.join(sides)})"
                    counted.append(f"{x} v {y}")
                elif len(own) < 2:
                    miss = [d for d in (x, y) if d not in own]
                    why = f"AWAITS mixed rows with {new_name} on {' and '.join(miss)} only" + (f" ({'; '.join(sides)})" if sides else "")
                    waiting.append(f"{x} v {y}")
                else:
                    why = f"investigation item: neither side worse ({'; '.join(sides)})"
                p(f"    {x} v {y} +{g:.1f}: {why}")
            for d, g in deck_veto:
                dk = [k for k in keys if d in k]
                own, opp, missing = [], [], []
                for k in dk:
                    ch = own_changes(k)
                    other = k[1] if k[0] == d else k[0]
                    (own.append(ch[d]) if d in ch else missing.append(f"{d} in {k[0]} v {k[1]}"))
                    (opp.append(ch[other]) if other in ch else missing.append(f"{other} in {k[0]} v {k[1]}"))
                parts = []
                if len(own) == len(dk):
                    m, h, n = side_change(own)
                    parts.append((f"{d}'s own side", m, h, n))
                if len(opp) == len(dk):
                    m, h, n = side_change(opp)
                    parts.append(("its opponents' side", m, h, n))
                sides = "; ".join(f"{s} {m:+.1f} ± {h:.1f} ({n:,} deals)" for s, m, h, n in parts)
                worse = [s for s, m, h, _ in parts if m < -h]
                if worse:
                    why = f"COUNTS: {new_name} pilots {' and '.join(worse)} worse ({sides})"
                    counted.append(d)
                elif missing:
                    why = f"AWAITS mixed rows: {len(missing)} of {2 * len(dk)} cell sides missing" + (f" ({sides})" if sides else "")
                    waiting.append(d)
                else:
                    why = f"investigation item: neither side worse ({sides})"
                p(f"    deck {d} +{g:.1f}: {why}")
        if hi >= 0:
            verdict = "do not adopt (dMSE interval not below 0)"
        elif counted:
            verdict = f"do not adopt (vetoes that count: {', '.join(counted)})"
        elif waiting:
            verdict = f"not decided: dMSE below 0, vetoes await mixed rows ({', '.join(waiting)})"
        else:
            verdict = "adopt" + (" (vetoes are investigation items)" if cell_veto or deck_veto else "")
        p(f"  ADOPTION RULE ({a.rules}): {verdict}{tag} (held-out-deck veto checked separately)")
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
    if a.mixed:
        p("")
        p(f"Mixed rows: each deck's own score change with {new_name} on that deck only, against {a.old} on both sides, "
          "same deals (95% range from per-deal differences)")
        for k in allk:
            ch = own_changes(k)
            if ch:
                p(f"  {k[0]:>9} v {k[1]:<10} " + "; ".join(
                    f"{d} {side_change([v])[0]:+5.1f} ± {side_change([v])[1]:3.1f} ({len(v)})" for d, v in ch.items()))
        p("")
        p(f"Mixed rows by deck, decision set (reported only; the vetoes above use them only when a veto fires): the deck's "
          f"own side with {new_name} on it only, and its opponents' own side with {new_name} on them only, pooled over the "
          "deck's cells (mean of cell changes, 95% range)")
        for d in D.NAMES:
            dk = [k for k in qk if d in k]
            own, opp = [], []
            for k in dk:
                ch = own_changes(k)
                other = k[1] if k[0] == d else k[0]
                if d in ch and other in ch:
                    own.append(ch[d]); opp.append(ch[other])
            if own and len(own) == len(dk):
                (mo, ho, _), (mp, hp, _) = side_change(own), side_change(opp)
                flag = lambda m, h: " (worse beyond noise)" if m < -h else ""  # noqa: E731
                p(f"  {d:>9}: own side {mo:+5.1f} ± {ho:3.1f}{flag(mo, ho)}; its opponents' side {mp:+5.1f} ± {hp:3.1f}"
                  f"{flag(mp, hp)} ({len(dk)} cells)")
    print("\n".join(out))


if __name__ == "__main__":
    main()
