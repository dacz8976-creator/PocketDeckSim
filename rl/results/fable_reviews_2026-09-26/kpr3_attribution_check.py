#!/usr/bin/env python3
"""Fable's adversarial recomputation of the kpr3 table readout (rl/results/kpr_2026-09-25/README.md at aa87fa3).

Inputs: copies of branch files made with `git show origin/claude/pensive-ptolemy-spwc0b:<path>` (see MANIFEST.txt).
Everything here is a plain recount of the per-game files; nothing is decided.
"""
import json, math, re, sys
from collections import defaultdict
from pathlib import Path

B = Path(r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\75cb92d0-6f2d-44b8-a636-513a8f7ee71a\scratchpad\reviews\branch")
DECKS = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]


def load(*names):
    games = {}
    for n in names:
        for line in open(B / n, encoding="utf-8"):
            if line.strip():
                g = json.loads(line)
                k = (g["pairing"], g["i"])
                assert k not in games, (n, k)
                games[k] = g
    return games


def limitless():
    text = (B / "limitless_check_2026-09-23.md").read_text(encoding="utf-8")
    text = text.split("### Rules4, every pairing")[1].split("## Part 2")[0]
    out = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(\w+) v (\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+) ± ([\d.]+)\s*\|", line)
        if m:
            out[(m.group(1), m.group(2))] = (float(m.group(4)), float(m.group(5)))
    return out


def paired(x, y):
    d = [b - a for a, b in zip(x, y)]
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in d) / max(n - 1, 1))
    return m, 1.96 * sd / math.sqrt(n)


def score_for(g, deck):
    s = g["first_deck_score"]
    return s if deck == g["a"] else 1 - s


kpr = load("kpr3_500.jsonl")
kp_id = load("identity_kp3_500.jsonl")
kp_tab = load("kp3_500_worst5.jsonl", "kp3_500_rest.jsonl")
k3 = load("k3_500.jsonl")
kq = load("kq3_500.jsonl")
kd = load("kd3_500.jsonl")
kq_id = load("identity_kq3_500.jsonl")
partial = load("kpr3_500_partial_c002d2f.jsonl")
lim = limitless()

print("=== A. integrity of kpr3_500.jsonl ===")
print("games:", len(kpr), "pairings:", len({p for p, _ in kpr}), "deals per pairing:",
      sorted({sum(1 for p, _ in kpr if p == q) for q in range(28)}))
bad_seed = [k for k, g in kpr.items() if g["seed"] != 72_000_000 + k[0] * 10_000 + k[1]]
bad_bot = [k for k, g in kpr.items() if (g["bot_a"], g["bot_b"]) != ("kpr3", "kpr3")]
bad_seat = [k for k, g in kpr.items() if g["first_seat"] != (k[1] % 2)]
print("seed formula violations:", len(bad_seed), "| bot fields not kpr3/kpr3:", len(bad_bot),
      "| first_seat != i%2:", len(bad_seat))
print("sample i=0:", {k: kpr[(0, 0)][k] for k in ("a", "b", "first_seat", "seed", "winner_seat", "first_deck_score")})
print("sample i=1:", {k: kpr[(0, 1)][k] for k in ("a", "b", "first_seat", "seed", "winner_seat", "first_deck_score")})
pair_decks = {p: (g["a"], g["b"]) for (p, _), g in kpr.items()}
same_pairs = all(pair_decks[p] == (kp_tab[(p, 0)]["a"], kp_tab[(p, 0)]["b"]) for p in range(28))
print("pairing -> decks same as kp3 table:", same_pairs)

print("\n=== B. identity claims ===")
def ident(x, y, label):
    keys = sorted(k for k in x if k in y)
    same = sum(1 for k in keys if x[k]["moves"] == y[k]["moves"])
    full = sum(1 for k in keys if all(x[k][f] == y[k][f] for f in ("moves", "winner_seat", "points", "turns", "first_deck_score")))
    print(f"{label}: {same} of {len(keys)} same moves; {full} of {len(keys)} same on all fields")
ident(kp_id, kp_tab, "identity_kp3_500 (53638a7) vs kp3 table (858b6fe)")
ident(kq_id, kq, "identity_kq3_500 (53638a7) vs kq3 table")
for bot, ref in (("k3", k3), ("kp3", kp_tab), ("kq3", kq)):
    ident(load(f"table_commit_identity_{bot}_40.jsonl"), ref, f"table_commit_identity_{bot}_40 (e09fb46) vs {bot} table")
ident(partial, kpr, "partial kpr3 at c002d2f (5,000) vs head kpr3_500")
print("partial pairings:", sorted({p for p, _ in partial}))

print("\n=== C. fit to Limitless (28 cells), recomputed ===")
def cells(games):
    s = defaultdict(lambda: [0.0, 0])
    for g in games.values():
        c = s[(g["a"], g["b"])]
        c[0] += g["first_deck_score"]; c[1] += 1
    return {k: 100 * v[0] / v[1] for k, v in s.items()}
tables = {"k3": cells(k3), "kp3": cells(kp_tab), "kq3": cells(kq), "kd3": cells(kd), "kpr3": cells(kpr)}
for bot, t in tables.items():
    miss = [t[c] - lim[c][0] for c in lim]
    print(f"{bot:5} mean|miss| {sum(abs(m) for m in miss)/28:.2f}  MSE {sum(m*m for m in miss)/28:.1f}")

print("\n=== D/E. per cell: kpr3 - kp3 paired, footprint, contribution to the MSE change ===")
print(f"{'cell':24} {'kp3':>6} {'kpr3':>6} {'change (95%)':>20} {'Lim':>6} {'band':>5} {'miss kp3':>9} {'miss kpr3':>9} {'dMSE/28':>8} {'differ':>7} {'turns kp3':>9} {'turns kpr3':>10} {'dturns':>7}")
rows = []
for p in range(28):
    a, b = pair_decks[p]
    keys = sorted(k for k in kpr if k[0] == p)
    sb = [kp_id[k]["first_deck_score"] for k in keys]
    so = [kpr[k]["first_deck_score"] for k in keys]
    m, h = paired(sb, so)
    L, band = lim[(a, b)]
    mb = 100 * sum(sb) / len(sb) - L
    mo = 100 * sum(so) / len(so) - L
    differ = sum(1 for k in keys if kp_id[k]["moves"] != kpr[k]["moves"])
    tb = sum(kp_id[k]["turns"] for k in keys) / len(keys)
    to = sum(kpr[k]["turns"] for k in keys) / len(keys)
    dmse = (mo * mo - mb * mb) / 28
    rows.append(dict(p=p, a=a, b=b, change=100 * m, half=100 * h, L=L, band=band, mb=mb, mo=mo, dmse=dmse, differ=differ, tb=tb, to=to))
    print(f"{p:2} {a[:9]:>9} v {b[:9]:9} {100*sum(sb)/500:6.1f} {100*sum(so)/500:6.1f} {100*m:+7.1f} ({100*(m-h):+5.1f},{100*(m+h):+5.1f}) {L:6.1f} {band:5.1f} {mb:+9.1f} {mo:+9.1f} {dmse:+8.1f} {differ:7} {tb:9.2f} {to:10.2f} {to-tb:+7.2f}")
tot = sum(r["dmse"] for r in rows)
hyd = sum(r["dmse"] for r in rows if "hydreigon" in (r["a"], r["b"]))
print(f"\nMSE change kpr3 - kp3 = {tot:+.1f}; from the 7 Hydreigon cells {hyd:+.1f}; from the other 21 cells {tot-hyd:+.1f}")
top = sorted(rows, key=lambda r: -abs(r["dmse"]))[:8]
print("largest |dMSE| contributions:", "; ".join(f"{r['a']} v {r['b']} {r['dmse']:+.1f}" for r in top))
print("footprint: games whose move fingerprint differs from kp3's:", sum(r["differ"] for r in rows), "of 14000 =",
      f"{100*sum(r['differ'] for r in rows)/14000:.1f}%")
print("cells with |change| beyond its 95% range:", sum(1 for r in rows if abs(r["change"]) > r["half"]), "of 28")
print("cells where the miss grew by more than 6:", [f"{r['a']} v {r['b']} ({r['mb']:+.1f} -> {r['mo']:+.1f})" for r in rows if abs(r["mo"]) - abs(r["mb"]) > 6])
print("Limitless bands over 15:", [f"{r['a']} v {r['b']} {r['band']}" for r in rows if r["band"] > 15])

print("\n=== F. Hydreigon: score change per cell vs Hyper Ray rate change (from the .txt files) ===")
def hyper_ray(txt):
    out = {}
    cur = None
    for line in open(B / txt, encoding="utf-8"):
        m = re.match(r"\s*(\w+) v (\w+)\s+first deck", line)
        if m:
            cur = (m.group(1), m.group(2))
        m = re.search(r"KO-able used (\d+) passed (\d+) \| not KO-able used (\d+) passed (\d+)", line)
        if m and cur:
            out[cur] = tuple(int(x) for x in m.groups())
    return out
hr_kp, hr_kpr = hyper_ray("identity_kp3_500.txt"), hyper_ray("kpr3_500.txt")
print(f"{'opponent':10} {'Hyd kp3':>8} {'Hyd kpr3':>8} {'change':>16} {'nonKO use kp3':>14} {'nonKO use kpr3':>15} {'KO pass kp3':>12} {'KO pass kpr3':>13}")
xs, ys = [], []
for r in rows:
    if "hydreigon" not in (r["a"], r["b"]):
        continue
    opp = r["b"] if r["a"] == "hydreigon" else r["a"]
    keys = sorted(k for k in kpr if k[0] == r["p"])
    sb = [score_for(kp_id[k], "hydreigon") for k in keys]
    so = [score_for(kpr[k], "hydreigon") for k in keys]
    m, h = paired(sb, so)
    c = (r["a"], r["b"])
    u1, p1, u2, p2 = hr_kp[c]; v1, q1, v2, q2 = hr_kpr[c]
    nonko_kp, nonko_kpr = u2 / (u2 + p2), v2 / (v2 + q2)
    xs.append(100 * (nonko_kpr - nonko_kp)); ys.append(100 * m)
    print(f"{opp:10} {100*sum(sb)/500:8.1f} {100*sum(so)/500:8.1f} {100*m:+6.1f} ± {100*h:4.1f}   {100*nonko_kp:5.0f}% ({u2}/{u2+p2}) {100*nonko_kpr:6.0f}% ({v2}/{v2+q2})   {100*p1/(u1+p1):5.1f}% ({p1}/{u1+p1}) {100*q1/(v1+q1):6.1f}% ({q1}/{v1+q1})")
mx, my = sum(xs) / 7, sum(ys) / 7
cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
r_ = cov / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
print(f"correlation over the 7 cells between the non-KO use change (points) and Hydreigon's score change: r = {r_:+.2f}")
allk = sum(v[1] for v in hr_kp.values()), sum(v[0] + v[1] for v in hr_kp.values())
allr = sum(v[1] for v in hr_kpr.values()), sum(v[0] + v[1] for v in hr_kpr.values())
print(f"KO-able Hyper Ray passed: kp3 {allk[0]} of {allk[1]}, kpr3 {allr[0]} of {allr[1]}")

print("\n=== G. what else moved: game length, seat, points, by deck ===")
def deck_rows(games, deck):
    out = {}
    for k, g in games.items():
        if deck in (g["a"], g["b"]):
            out[k] = score_for(g, deck)
    return out
print(f"{'deck':10} {'kp3':>6} {'kpr3':>6} {'change (95%)':>16} | {'seat0 kp3':>9} {'seat0 kpr3':>10} | {'seat1 kp3':>9} {'seat1 kpr3':>10} | {'turns kp3':>9} {'turns kpr3':>10}")
for deck in DECKS:
    a_, b_ = deck_rows(kp_id, deck), deck_rows(kpr, deck)
    keys = sorted(a_)
    m, h = paired([a_[k] for k in keys], [b_[k] for k in keys])
    # seat of `deck`: first-named deck sits in seat 0 on even i, seat 1 on odd i
    def seat_of(k):
        g = kpr[k]
        first = g["a"] == deck
        return 0 if (first == (k[1] % 2 == 0)) else 1
    s0 = [k for k in keys if seat_of(k) == 0]; s1 = [k for k in keys if seat_of(k) == 1]
    tb = sum(kp_id[k]["turns"] for k in keys) / len(keys); to = sum(kpr[k]["turns"] for k in keys) / len(keys)
    print(f"{deck:10} {100*sum(a_.values())/len(a_):6.1f} {100*sum(b_.values())/len(b_):6.1f} {100*m:+6.1f} ± {100*h:4.1f} | "
          f"{100*sum(a_[k] for k in s0)/len(s0):9.1f} {100*sum(b_[k] for k in s0)/len(s0):10.1f} | "
          f"{100*sum(a_[k] for k in s1)/len(s1):9.1f} {100*sum(b_[k] for k in s1)/len(s1):10.1f} | {tb:9.2f} {to:10.2f}")

# overall seat-0 (moving first?) score and game length
def seat0_score(games):
    return 100 * sum((g["first_deck_score"] if k[1] % 2 == 0 else 1 - g["first_deck_score"]) for k, g in games.items()) / len(games)
print(f"\nseat-0 deck's score over all games: kp3 {seat0_score(kp_id):.1f}, kpr3 {seat0_score(kpr):.1f}, k3 {seat0_score(k3):.1f}")
print(f"mean turns: kp3 {sum(g['turns'] for g in kp_id.values())/14000:.2f}, kpr3 {sum(g['turns'] for g in kpr.values())/14000:.2f}, k3 {sum(g['turns'] for g in k3.values())/14000:.2f}")
ties = lambda games: sum(1 for g in games.values() if g["first_deck_score"] == 0.5)
print(f"ties: kp3 {ties(kp_id)}, kpr3 {ties(kpr)}")
def pts(games):
    w = sum(max(g["points"]) for g in games.values()) / len(games)
    l = sum(min(g["points"]) for g in games.values()) / len(games)
    return w, l
print("mean winner points / loser points: kp3 %.2f / %.2f, kpr3 %.2f / %.2f" % (*pts(kp_id), *pts(kpr)))
# turn-length distribution shift
def tdist(games):
    d = defaultdict(int)
    for g in games.values():
        d[min(g["turns"], 30)] += 1
    return d
tk, tr = tdist(kp_id), tdist(kpr)
print("turn histogram (kp3 -> kpr3) for turns <= 12:", ", ".join(f"{t}: {tk[t]}->{tr[t]}" for t in range(1, 13)))
print("games of 20+ turns: kp3", sum(1 for g in kp_id.values() if g["turns"] >= 20), "kpr3", sum(1 for g in kpr.values() if g["turns"] >= 20))

print("\n=== H. deck-average table as the README prints it (recomputed) ===")
def deck_avg(t, deck):
    vals = [v if a == deck else 100 - v for (a, b), v in t.items() if deck in (a, b)]
    return sum(vals) / len(vals)
limc = {k: v[0] for k, v in lim.items()}
for deck in DECKS:
    print(f"{deck:10} Lim {deck_avg(limc, deck):5.1f}  k3 {deck_avg(tables['k3'], deck):5.1f}  kp3 {deck_avg(tables['kp3'], deck):5.1f}  kpr3 {deck_avg(tables['kpr3'], deck):5.1f}  gap kp3 {deck_avg(tables['kp3'], deck)-deck_avg(limc, deck):+5.1f}  gap kpr3 {deck_avg(tables['kpr3'], deck)-deck_avg(limc, deck):+5.1f}")
