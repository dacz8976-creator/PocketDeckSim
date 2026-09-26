#!/usr/bin/env python3
"""kpr3's rule-v2 reading, the laptop's own recount (Sept 26). Read-only; prints to stdout.

Written from scratch (not from Fable's scripts) to reproduce, independently:
  - the footprint (games whose move fingerprint or result differs from kp3's, on the same deals), for the table and
    for the mixed rows, per deck and side;
  - the paired deck and cell changes on the table (kpr3 v kpr3 minus kp3 v kp3);
  - the mixed rows as attribution: each deck's own side (kpr3 on it only) and its opponents' side (kpr3 on them only),
    per cell and pooled per deck over all its cells, with the part neither side explains (the interaction);
  - the behaviour counters the per-game files carry (hyper_ray, chase_order), per cell, in four conditions.
Pooled changes are stratified like score.py: the mean of the cell means, variance summed per cell.

Usage: analysis.py <kpr3_500.jsonl copied from the cloud branch>   (run from anywhere)
"""
import json, math, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]          # rl/results
KPR = Path(sys.argv[1])
DECKS = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
QUAR = {("altaria", "sceptile")}
AWAIT = [("altaria", "hydreigon"), ("altaria", "suicune"), ("blaziken", "lucario"), ("lucario", "suicune"),
         ("suicune", "vespiquen")]
BAND_OUT = [("blaziken", "weezing"), ("hydreigon", "suicune"), ("hydreigon", "vespiquen")]


def load(*paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                k = (r["a"], r["b"], r["i"])
                assert k not in out, (p, k)
                out[k] = r
    return out


kp3 = load(R / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", R / "public_pricing_2026-09-25/kp3_500_rest.jsonl")
kpr = load(KPR)
mf = load(R / "kpr_mixed_rows_2026-09-26/mixed_kpr3_first.jsonl")     # kpr3 on the first-named deck only
ms = load(R / "kpr_mixed_rows_2026-09-26/mixed_kpr3_second.jsonl")    # kpr3 on the second-named deck only
k3 = load(R / "per_game_table_2026-09-25/k3_500.jsonl")
co_kp3 = load(R / "chase_order_2026-09-25/kp3_vespiquen.jsonl")      # kp3's table games replayed with the counter
spot = load(R / "kpr_mixed_rows_2026-09-26/spot_kp3_p0-2.jsonl")
rep1 = load(R / "kpr_mixed_rows_2026-09-26/kpr3_replay_p1.jsonl")
lim = json.load(open(R / "scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]

CELLS = sorted({(r["pairing"], r["a"], r["b"]) for r in kp3.values()})
CELLS = [(a, b) for _, a, b in CELLS]
FIELDS = ["seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score"]

print("== A. inputs")
for name, g, bots in (("kp3 table", kp3, {("kp3", "kp3")}), ("kpr3 table", kpr, {("kpr3", "kpr3")}),
                      ("mixed, kpr3 first", mf, {("kpr3", "kp3")}), ("mixed, kpr3 second", ms, {("kp3", "kpr3")})):
    gb = {(r["bot_a"], r["bot_b"]) for r in g.values()}
    same = sum(1 for k, r in g.items() if k in kp3 and r["seed"] == kp3[k]["seed"] and r["first_seat"] == kp3[k]["first_seat"])
    print(f"  {name:20} {len(g):6,} games; bots {sorted(gb)} (expected {sorted(bots)}); same deal and seat as kp3's: {same:,}")
    assert gb == bots and same == len(g) == 14000

print("\n== B. identity checks on the laptop's e09fb46 build (field by field)")
for name, new, ref in (("kp3 spot, pairings 0-2", spot, kp3), ("kpr3 v kpr3, pairing 1", rep1, kpr)):
    same = sum(1 for k, r in new.items() if all(r[f] == ref[k][f] for f in FIELDS))
    print(f"  {name}: {same:,} of {len(new):,} identical to the reference on {', '.join(FIELDS)}")
same = sum(1 for k, r in co_kp3.items() if all(r[f] == kp3[k][f] for f in FIELDS))
print(f"  kp3 Chase Order replay (chase_order_2026-09-25): {same:,} of {len(co_kp3):,} identical to kp3's table games")


def mv(d):
    n = len(d)
    m = sum(d) / n
    return m, sum((x - m) ** 2 for x in d) / (n - 1) / n


def pool(parts):
    """stratified: mean of cell means, 95% half-width"""
    s = [mv(d) for d in parts]
    return sum(m for m, _ in s) / len(s), 1.96 * math.sqrt(sum(v for _, v in s)) / len(s)


def f(m, h):
    return f"{m:+5.1f} ± {h:3.1f}"


def s(r):
    return 100 * r["first_deck_score"]


print("\n== C. footprint: games whose move fingerprint (or result) differs from kp3's on the same deal")
d_all = sum(1 for k in kp3 if kpr[k]["moves"] != kp3[k]["moves"])
r_all = sum(1 for k in kp3 if kpr[k]["first_deck_score"] != kp3[k]["first_deck_score"])
k3same = sum(1 for k in kp3 if k3[k]["moves"] == kp3[k]["moves"])
print(f"  table (kpr3 on both sides): moves differ {d_all:,} of 14,000 ({100*d_all/14000:.1f}%); identical {14000-d_all:,}; "
      f"result differs {r_all:,} ({100*r_all/14000:.1f}%)")
print(f"  for scale: kp3 and k3 identical in {k3same:,} of 14,000")
per = {c: sum(1 for i in range(500) if kpr[c + (i,)]["moves"] != kp3[c + (i,)]["moves"]) for c in CELLS}
lo, hi = min(per, key=per.get), max(per, key=per.get)
print(f"  least-changed cell {lo[0]} v {lo[1]} {per[lo]} of 500; most-changed {hi[0]} v {hi[1]} {per[hi]} of 500")
print("  mixed rows, kpr3 on one deck only (that deck's cells, both seats), moves differ / result differs, of 3,500:")
for d in DECKS:
    md = rd = 0
    for a, b in CELLS:
        if d not in (a, b):
            continue
        g = mf if d == a else ms
        for i in range(500):
            k = (a, b, i)
            md += g[k]["moves"] != kp3[k]["moves"]
            rd += g[k]["first_deck_score"] != kp3[k]["first_deck_score"]
    print(f"    kpr3 on {d:9}: moves differ {md:5,} ({100*md/3500:4.1f}%), result differs {rd:5,} ({100*rd/3500:4.1f}%)")
md = sum(1 for k in kp3 if mf[k]["moves"] != kp3[k]["moves"]) + sum(1 for k in kp3 if ms[k]["moves"] != kp3[k]["moves"])
print(f"  all mixed games: moves differ {md:,} of 28,000 ({100*md/28000:.1f}%)")


def diffs(c):
    """per-deal changes, first-named deck's view: table, A's side (kpr3 on A), B's side (kpr3 on B, B's view),
    interaction (A's view): table - A's side - (effect of kpr3 on B on A's score)"""
    t, A, B, I = [], [], [], []
    for i in range(500):
        k = c + (i,)
        base = s(kp3[k])
        dt, da, db = s(kpr[k]) - base, s(mf[k]) - base, -(s(ms[k]) - base)
        t.append(dt); A.append(da); B.append(db); I.append(dt - da + db)
    return t, A, B, I


D = {c: diffs(c) for c in CELLS}


def band(c):
    w, l, t = lim["|".join(c)]
    n = w + l + t
    L = (w + 0.5 * t) / n
    return L, 196 * math.sqrt(L * (1 - L) / n)


print("\n== D. per cell (first-named deck's view unless named): table change; A's own side; B's own side; interaction")
print("   (A's side = kpr3 on A only, A's score; B's side = kpr3 on B only, B's score; 95% ranges from per-deal differences)")
for c in CELLS:
    t, A, B, I = D[c]
    tag = ""
    if c in AWAIT:
        tag = "  [cell veto candidate that awaited mixed rows]"
    elif c in BAND_OUT:
        tag = f"  [never counts: Limitless band ±{band(c)[1]:.1f}]"
    elif c in QUAR:
        tag = "  [quarantined]"
    print(f"  {c[0]:>9} v {c[1]:<10} table {f(*pool([t]))} | {c[0]} side {f(*pool([A]))} | {c[1]} side {f(*pool([B]))}"
          f" | interaction {f(*pool([I]))}{tag}")


def deck_rows(keys, label):
    print(f"\n== E. per deck, {label}: own side (kpr3 on the deck only); opponents' side (kpr3 on its opponents only,"
          " the opponents' own score); table change; interaction (table - own + opponents' side)")
    for d in DECKS:
        own, opp, tab, inter = [], [], [], []
        for c in keys:
            if d not in c:
                continue
            t, A, B, I = D[c]
            if d == c[0]:
                own.append(A); opp.append(B); tab.append(t); inter.append(I)
            else:
                own.append(B); opp.append(A); tab.append([-x for x in t]); inter.append([-x for x in I])
        mo, ho = pool(own); mp, hp = pool(opp); mt, ht = pool(tab); mi, hi = pool(inter)
        fl = lambda m, h: (" worse" if m < -h else " better" if m > h else "      ")  # noqa: E731
        print(f"  {d:9} ({len(own)} cells): own {f(mo, ho)}{fl(mo, ho)} | opponents {f(mp, hp)}{fl(mp, hp)} | "
              f"table {f(mt, ht)} | own - opponents {mo - mp:+5.1f} | interaction {f(mi, hi)}")


sides = [D[c][1] for c in CELLS] + [D[c][2] for c in CELLS]
m, h = pool(sides)
print(f"\n== E0. kpr3 head to head against kp3 (all 28,000 mixed games; kp3 v kp3 on the same games is 50% by symmetry): "
      f"kpr3 scores {50 + m:.1f}% ({f(m, h)} points, pooled over the 56 cell sides)")
deck_rows(CELLS, "all 28 cells (7 per deck)")
deck_rows([c for c in CELLS if c not in QUAR], "decision set (27 cells; Altaria and Sceptile 6)")

print("\n== F. Hyper Ray (Hydreigon), per cell: [KO-able used, KO-able passed, not KO-able used, not KO-able passed]")
HYD = [c for c in CELLS if "hydreigon" in c]
conds = (("kp3 table", lambda c: kp3), ("kpr3 table", lambda c: kpr),
         ("mixed: kpr3 on Hydreigon", lambda c: mf if c[0] == "hydreigon" else ms),
         ("mixed: kpr3 on the opponent", lambda c: ms if c[0] == "hydreigon" else mf))


def hr_sum(g, c):
    t = [0, 0, 0, 0]
    per_game = []
    for i in range(500):
        h = g[c + (i,)].get("hyper_ray", [0, 0, 0, 0])
        t = [x + y for x, y in zip(t, h)]
        per_game.append(h)
    return t, per_game


def ratio_ci(per_game, num, den):
    """ratio of sums with a game-clustered delta-method 95% half-width, in percent"""
    ys = [sum(h[j] for j in num) for h in per_game]
    xs = [sum(h[j] for j in den) for h in per_game]
    X, Y = sum(xs), sum(ys)
    if X == 0:
        return float("nan"), float("nan"), 0, 0
    r = Y / X
    n = len(xs)
    v = n / (n - 1) * sum((y - r * x) ** 2 for x, y in zip(xs, ys)) / X ** 2
    return 100 * r, 196 * math.sqrt(v), Y, X


tot = {name: [] for name, _ in conds}
for c in HYD:
    print(f"  {c[0]} v {c[1]}")
    for name, g in conds:
        t, pg = hr_sum(g(c), c)
        tot[name] += pg
        u, hu, Yu, Xu = ratio_ci(pg, [2], [2, 3])
        p, hp, Yp, Xp = ratio_ci(pg, [1], [0, 1])
        print(f"    {name:28} {t}  no-KO used {Yu}/{Xu} = {u:4.0f}% ± {hu:2.0f} | KO-able passed {Yp}/{Xp} = {p:4.1f}% ± {hp:3.1f}")
print("  all seven cells pooled (turns summed):")
for name, _ in conds:
    pg = tot[name]
    u, hu, Yu, Xu = ratio_ci(pg, [2], [2, 3])
    p, hp, Yp, Xp = ratio_ci(pg, [1], [0, 1])
    print(f"    {name:28} no-KO used {Yu}/{Xu} = {u:4.1f}% ± {hu:3.1f} | KO-able passed {Yp}/{Xp} = {p:4.1f}% ± {hp:3.1f}")

print("\n  Hydreigon's own score change per cell against its no-KO Hyper Ray use change (table; and mixed own side):")
xs_t, ys_t, xs_o, ys_o = [], [], [], []
for c in HYD:
    t, A, B, I = D[c]
    sgn = 1 if c[0] == "hydreigon" else -1
    own = A if c[0] == "hydreigon" else B
    ut = ratio_ci(hr_sum(kpr, c)[1], [2], [2, 3])[0] - ratio_ci(hr_sum(kp3, c)[1], [2], [2, 3])[0]
    uo = ratio_ci(hr_sum(conds[2][1](c), c)[1], [2], [2, 3])[0] - ratio_ci(hr_sum(kp3, c)[1], [2], [2, 3])[0]
    mt, ht = pool([[sgn * x for x in t]]); mo, ho = pool([own])
    xs_t.append(ut); ys_t.append(mt); xs_o.append(uo); ys_o.append(mo)
    opp = c[1] if c[0] == "hydreigon" else c[0]
    print(f"    v {opp:9} table: use {ut:+5.1f} pts, Hydreigon {f(mt, ht)} | own side only: use {uo:+5.1f} pts, Hydreigon {f(mo, ho)}")


def corr(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


print(f"    correlation over the seven cells: table r = {corr(xs_t, ys_t):+.2f}; mixed own side r = {corr(xs_o, ys_o):+.2f}")

print("\n== G. Chase Order (Vespiquen's choice), per cell: discarded / offered, Combee discards; game-clustered 95% half-width")
VES = [c for c in CELLS if "vespiquen" in c]
cconds = (("kp3 table", lambda c: co_kp3), ("kpr3 table", lambda c: kpr),
          ("mixed: kpr3 on Vespiquen", lambda c: mf if c[0] == "vespiquen" else ms),
          ("mixed: kpr3 on the opponent", lambda c: ms if c[0] == "vespiquen" else mf))


def co_games(g, c):
    out = []
    for i in range(500):
        x = g[c + (i,)].get("chase_order") or {"offered": 0, "discarded": 0, "names": {}}
        nm = x.get("names", {})
        out.append([x["discarded"], x["offered"], nm.get("Combee", 0), nm.get("Shuckle ex", 0),
                    nm.get("Teal Mask Ogerpon ex", 0)])
    return out


ctot = {name: [] for name, _ in cconds}
for c in VES:
    print(f"  {c[0]} v {c[1]}")
    for name, g in cconds:
        pg = co_games(g(c), c)
        ctot[name] += pg
        r, h, Y, X = ratio_ci(pg, [0], [1])
        cb = sum(p[2] for p in pg)
        print(f"    {name:28} discarded {Y}/{X} = {r:4.1f}% ± {h:3.1f}  (Combee {cb}, Shuckle ex {sum(p[3] for p in pg)}, "
              f"Ogerpon ex {sum(p[4] for p in pg)})")
print("  all seven cells pooled:")
for name, _ in cconds:
    pg = ctot[name]
    r, h, Y, X = ratio_ci(pg, [0], [1])
    cbr, cbh, _, _ = ratio_ci(pg, [2], [1])
    print(f"    {name:28} choices {X:,}; discarded {Y:,} = {r:4.1f}% ± {h:3.1f}; Combee {sum(p[2] for p in pg)} "
          f"({cbr:.1f}% of choices ± {cbh:.1f})")
print("\n== H. counters the per-game files carry: hyper_ray, chase_order only (no Diving Icicles, Mega Burning, "
      "Terminating Tail or attach-Ability counters)")
