"""Reconciler (Sept 30): clause (d), a third independent computation from the raw (d) files.
Written from the registration's step 4 (d) text and read_koh.py's paired() (lines 109-118) only; it does not open
read_km.py, footprint_km.py, km_check.py or either reader's scripts. Rows and deals are read from each game's seed.
Exact arithmetic (Fraction), the square root in 60-digit Decimal, and a plain-float replica of paired() beside."""
import json, math, sys
from fractions import Fraction as F
from decimal import Decimal, getcontext
from collections import defaultdict

getcontext().prec = 60
REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
KM = REPO + "/rl/results/km_tables_2026-09-30/"
KT = REPO + "/rl/results/kt_tables_2026-09-28/"
OUT = KM + "second_reader/rc_clause_d.txt"
out = []
p = out.append

TABLE = {2: 0, 8: 1, 13: 2, 18: 3, 19: 4, 20: 5, 21: 6}   # table pairing -> row (rows 0-6 in increasing pairing)
NEW = {8: 7, 16: 8}                                        # new_decks.tsv pairing -> row
OPP = ["altaria", "blaziken", "hydreigon", "sceptile", "suicune", "vespiquen", "weezing", "rayquaza", "altaria_greninja"]


def rd(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def locate(seed):
    """(row, deal index 0-1999, i-or-j) from the seed alone."""
    if 22_900_000_000 <= seed <= 22_900_081_499:
        off = seed - 22_900_000_000
        row, j = divmod(off, 10_000)
        assert 0 <= row <= 8 and j < 1500, seed
        return row, 500 + j, j
    if 21_108_000_000 <= seed < 21_109_000_000:
        pr, i = divmod(seed - 21_108_000_000, 10_000)
        assert pr in NEW and i < 500, seed
        return NEW[pr], i, i
    pr, i = divmod(seed - 72_000_000, 10_000)
    assert pr in TABLE and 0 <= i < 500, seed
    return TABLE[pr], i, i


def arm(files, want_km):
    games, bad = {}, []
    for fn in files:
        for g in rd(KM + fn):
            row, deal, idx = locate(g["seed"])
            key = (row, deal)
            assert key not in games, ("duplicate", key)
            luc_first = g["a"] == "lucario"
            assert luc_first or g["b"] == "lucario", g["seed"]
            other = g["b"] if luc_first else g["a"]
            if other != OPP[row]:
                bad.append(("opponent", key, other))
            # seats: first-named deck in seat 0 on even i / Lucario (first-named in the block) in seat 0 on even j
            if g["first_seat"] != idx % 2:
                bad.append(("seat", key, g["first_seat"]))
            luc_bot, oth_bot = (g["bot_a"], g["bot_b"]) if luc_first else (g["bot_b"], g["bot_a"])
            if (luc_bot, oth_bot) != (("km3" if want_km else "kta3"), "kta3"):
                bad.append(("bots", key, luc_bot, oth_bot))
            s = g["first_deck_score"]
            assert s in (0.0, 0.5, 1.0), s
            own = F(s).limit_denominator(2) if luc_first else 1 - F(s).limit_denominator(2)
            games[key] = (own, g)
    return games, bad


km, bad_km = arm(["1f6319e_d_km3_table_lucario_a.jsonl", "1f6319e_d_km3_table_lucario_b.jsonl",
                  "1f6319e_d_km3_new_lucario_b.jsonl", "1f6319e_d_km3_block.jsonl"], True)
kt, bad_kt = arm(["1f6319e_d_kta3_table.jsonl", "1f6319e_d_kta3_new.jsonl", "1f6319e_d_kta3_block.jsonl"], False)
p(f"games: km3 arm {len(km)}, kta3 arm {len(kt)}; expected 18,000 each")
assert set(km) == set(kt) == {(r, d) for r in range(9) for d in range(2000)}
p(f"keys: both arms hold exactly rows 0-8 x deals 0-1999; opponent/seat/bot problems: km3 {len(bad_km)}, kta3 {len(bad_kt)}")
for b in (bad_km + bad_kt)[:10]:
    p(f"   {b}")
sig = lambda g: (g["seed"], g["first_seat"], g["a"], g["b"], g.get("a_file"), g.get("b_file"))
mism = [k for k in km if sig(km[k][1]) != sig(kt[k][1])]
nofile = sum(1 for k in km if km[k][1].get("a_file") is None) + sum(1 for k in kt if kt[k][1].get("a_file") is None)
p(f"pairing across arms (seed, seat, both decks, both deck files where recorded): {len(mism)} of 18,000 differ "
  f"({nofile} of 36,000 records carry no deck-file field: the table files, decks named by key)")
diffmoves = sum(1 for k in km if km[k][1]["moves"] != kt[k][1]["moves"])
p(f"km3-arm games whose moves differ from the kta3 arm's: {diffmoves} of 18,000")

# kta3 arm on deals 0-499 against kta3's reference files (the config's two files)
ref = {}
for fn, base, rows in (("ec7e1a8_kta3_table.jsonl", 72_000_000, TABLE), ("ec7e1a8_kta3_new17.jsonl", 21_108_000_000, NEW)):
    for g in rd(KT + fn):
        pr = (g["seed"] - base) // 10_000
        if pr in rows:
            ref[(rows[pr], g["seed"] - base - pr * 10_000)] = g
fields = ("moves", "decisions", "first_deck_score", "winner_seat", "seed", "first_seat", "a", "b", "a_file", "b_file", "turns")
rep_bad = [k for k in ref if any(ref[k].get(f) != kt[k][1].get(f) for f in fields)]
p(f"kta3 arm deals 0-499 replay kta3's references: {len(ref)} compared, {len(rep_bad)} differ on {', '.join(fields)}")

# the statistic (read_koh.py paired(): per row mean difference in points, (n-1) variance of the mean, equal weight)
rows = defaultdict(list)
for (r, d) in sorted(km):
    rows[r].append(100 * (km[(r, d)][0] - kt[(r, d)][0]))
means, vars_ = [], []
p("")
p("per row (points; km3 arm minus kta3 arm; 2,000 deals; half-width 1.96 x sd of the mean):")
for r in range(9):
    v = rows[r]
    n = len(v)
    m = sum(v, F(0)) / n
    var = sum(((x - m) ** 2 for x in v), F(0)) / (n - 1) / n
    means.append(m); vars_.append(var)
    hw = 1.96 * math.sqrt(var)
    a_kt = float(sum(kt[(r, d)][0] for d in range(2000)) * 100 / 2000)
    a_km = float(sum(km[(r, d)][0] for d in range(2000)) * 100 / 2000)
    p(f"   row {r} Lucario v {OPP[r]:<17} kta3 {a_kt:6.2f} -> km3 {a_km:6.2f}: {float(m):+.4f} +/- {hw:.4f}")
M = sum(means, F(0)) / 9
V = sum(vars_, F(0))
Z = F(196, 100)
Hd = Decimal(Z.numerator) / Decimal(Z.denominator) * (Decimal(V.numerator) / Decimal(V.denominator)).sqrt() / 9
Md = Decimal(M.numerator) / Decimal(M.denominator)
Ld = Md - Hd
p("")
p(f"POOLED MEAN (exact): {M} = {Md:.15f}")
p(f"sum of per-row variances of the mean (exact): {V} = {Decimal(V.numerator) / Decimal(V.denominator):.15f}")
p(f"half-width 1.96 x sqrt(sum) / 9 = {Hd:.15f}")
p(f"LOWER EDGE (mean - half-width) = {Ld:.15f}; upper edge {Md + Hd:.15f}")
p(f"exact test without a square root: M > 0 and (9M)^2 > 1.96^2 x sum:  {(9 * M) ** 2} > {Z ** 2 * V} = "
  f"{float(Z ** 2 * V):.6f}: {M > 0 and (9 * M) ** 2 > Z ** 2 * V}")
p(f"=> clause (d) {'PASSES' if Ld > 0 else 'FAILS'}: the whole 95% interval is {'above' if Ld > 0 else 'not above'} zero")
p(f"sd of the pooled mean {float((Decimal(V.numerator) / Decimal(V.denominator)).sqrt() / 9):.6f}; z = M / sd = "
  f"{float(Md / ((Decimal(V.numerator) / Decimal(V.denominator)).sqrt() / 9)):.4f}")

# plain-float replica of paired() (the order read_koh.py uses: dict insertion order, then sum)
cells = defaultdict(list)
for (r, d) in sorted(km):
    cells[r].append(100 * (float(km[(r, d)][0]) - float(kt[(r, d)][0])))
fm = [sum(v) / len(v) for v in cells.values()]
fv = [(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / len(v) for v, m in zip(cells.values(), fm)]
pm, ph = sum(fm) / 9, 1.96 * math.sqrt(sum(fv)) / 9
p(f"float replica of paired(): mean {pm!r}, half-width {ph!r}, lower edge {pm - ph!r}")

# shares and leave-one-out (reported only; no registered rule reads them)
tot = sum(means, F(0))
p("")
p("reported only: each row's share of the pooled sum, and the 8-row pool without it")
for r in range(9):
    m8 = (tot - means[r]) / 8
    h8 = 1.96 * math.sqrt(float(V - vars_[r])) / 8
    p(f"   row {r} {OPP[r]:<17} share {float(means[r] / tot) * 100:+6.1f}%   without it: {float(m8):+.4f} +/- {h8:.4f} "
      f"(lower edge {float(m8) - h8:+.4f})")
p(f"one km3-arm game from a win to a loss moves the pooled mean by 100 / 2,000 / 9 = {100 / 2000 / 9:.6f} points; "
  f"lower edge / that = {float(Ld) / (100 / 2000 / 9):.2f} games (variance held fixed)")
open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
