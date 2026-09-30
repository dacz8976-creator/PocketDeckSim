"""Item 4: clause (d) to full precision. Written from step 4 (d) and D2 (the registration) and read_koh.py's paired()
(read alone): per row, Lucario's own-side score (first_deck_score when Lucario is side a, 1 - it when side b),
difference km3 arm minus kta3 arm per deal, in points; per-row mean and variance of the mean (n - 1 denominator,
over the row's N = 2,000 deals pooled: 500 table deals + 1,500 block deals); equal-weight mean of the 9 row means;
half-width 1.96 x sqrt(sum of per-row variances) / 9. Passes iff the whole interval is above zero.
Everything is computed exactly (fractions.Fraction; scores are multiples of 1/2) and the square root in Decimal at
60 digits, so the lower edge is exact to far more than 6 significant digits.
Also: every seed, seat, pairing, file and bot of both arms; the kta3 arm on deals 0-499 against kta3's references;
the km3 arm on deals 0-499 against clause (c)'s mixed rows (a determinism cross-check, reported).
Writes OUT/sr3_clause_d.txt."""
import sys
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

getcontext().prec = 60
lines = []
p = lines.append

REF = by_key(rd(KT + "/ec7e1a8_kta3_table.jsonl") + rd(KT + "/ec7e1a8_kta3_new17.jsonl"), ab)
blk_rows = tsv(K + "/pairs/d_lucario_block.tsv")
assert [int(r["pairing"]) for r in blk_rows] == list(range(9))

# ---------- the files (as named in STATUS.txt, part R)
KM_T = rd(B + "d_km3_table_lucario_a.jsonl") + rd(B + "d_km3_table_lucario_b.jsonl") + rd(B + "d_km3_new_lucario_b.jsonl")
KT_T = rd(B + "d_kta3_table.jsonl") + rd(B + "d_kta3_new.jsonl")
KM_B = rd(B + "d_km3_block.jsonl")
KT_B = rd(B + "d_kta3_block.jsonl")
p(f"files: km3 arm table deals {len(KM_T)}, block {len(KM_B)}; kta3 arm table deals {len(KT_T)}, block {len(KT_B)}")
vals = sorted({r["first_deck_score"] for r in KM_T + KT_T + KM_B + KT_B})
p(f"first_deck_score values seen: {vals}")

# the table-deal part: key by (a, b)
kmT = by_key(KM_T, ab)
ktT = by_key(KT_T, ab)
cells = [cell_of(s, pr) for s, pr in D_ROWS]
assert set(kmT) == set(ktT) == set(cells), (set(kmT) ^ set(cells), set(ktT) ^ set(cells))
# the block: key by the row number (the file's pairing field)
kmB = by_key(KM_B, pairing)
ktB = by_key(KT_B, pairing)
assert set(kmB) == set(ktB) == set(range(9))

checks = 0
ref_fields = ("moves", "decisions", "first_deck_score", "winner_seat", "points", "seed", "first_seat", "openings", "turns", "a", "b")
ref_diff = {}
row_diffs, row_parts, arm_avg = [], [], []
for row, (src, pr) in enumerate(D_ROWS):
    cell = cell_of(src, pr)
    luc_side = "a" if cell[0] == "lucario" else "b"
    assert "lucario" in cell
    base = TABLE_BASE if src == "table" else NEW_BASE
    km_bots = ("km3", "kta3") if luc_side == "a" else ("kta3", "km3")
    own = (lambda r: Fr(r["first_deck_score"]).limit_denominator(2)) if luc_side == "a" else (lambda r: 1 - Fr(r["first_deck_score"]).limit_denominator(2))
    # table deals 0-499
    a_, b_ = kmT[cell], ktT[cell]
    assert set(a_) == set(b_) == set(range(500)), (cell, len(a_), len(b_))
    tdiff = []
    rd_ = 0
    for i in range(500):
        x, y = a_[i], b_[i]
        assert (x["bot_a"], x["bot_b"]) == km_bots and (y["bot_a"], y["bot_b"]) == ("kta3", "kta3"), (cell, i)
        for g in (x, y):
            assert g["pairing"] == pr and g["seed"] == base + pr * 10000 + i and g["first_seat"] == i % 2, (cell, i, g["seed"])
            assert (g["a"], g["b"]) == cell
            assert g.get("a_file") == REF[cell][i].get("a_file") and g.get("b_file") == REF[cell][i].get("b_file"), (cell, i)
        checks += 2
        # the kta3 arm replays kta3's references
        if any(y.get(f) != REF[cell][i].get(f) for f in ref_fields):
            rd_ += 1
        tdiff.append(100 * (own(x) - own(y)))
    ref_diff[cell] = rd_
    # block deals j < 1500
    br = blk_rows[row]
    assert br["held_key"] == "lucario" and br["opponent"] == cell[1 if luc_side == "a" else 0], (row, br, cell)
    c_, d_ = kmB[row], ktB[row]
    assert set(c_) == set(d_) == set(range(1500)), (row, len(c_), len(d_))
    bdiff = []
    for j in range(1500):
        x, y = c_[j], d_[j]
        assert (x["bot_a"], x["bot_b"]) == ("km3", "kta3") and (y["bot_a"], y["bot_b"]) == ("kta3", "kta3"), (row, j)
        for g in (x, y):
            assert g["pairing"] == row and g["seed"] == D_BASE + row * 10000 + j and g["first_seat"] == j % 2, (row, j, g["seed"])
            assert g["a"] == "lucario" and g["b"] == br["opponent"], (row, j)
            assert g["a_file"] == br["held_file"] and g["b_file"] == br["panel_file"], (row, j, g["a_file"], g["b_file"])
        checks += 2
        bdiff.append(100 * (Fr(x["first_deck_score"]).limit_denominator(2) - Fr(y["first_deck_score"]).limit_denominator(2)))
    row_parts.append((tdiff, bdiff))
    row_diffs.append(tdiff + bdiff)
    # reported: the arms' own-side averages and the km3-arm games whose moves differ from the kta3 arm's
    km_own = [own(a_[i]) for i in range(500)] + [Fr(c_[j]["first_deck_score"]).limit_denominator(2) for j in range(1500)]
    kt_own = [own(b_[i]) for i in range(500)] + [Fr(d_[j]["first_deck_score"]).limit_denominator(2) for j in range(1500)]
    mvd = sum(1 for i in range(500) if a_[i]["moves"] != b_[i]["moves"]) + sum(1 for j in range(1500) if c_[j]["moves"] != d_[j]["moves"])
    arm_avg.append((float(sum(kt_own, Fr(0)) / 2000 * 100), float(sum(km_own, Fr(0)) / 2000 * 100), mvd))
p(f"seeds, seats, pairings, decks, files and bots checked on {checks} games (every game of both arms): all as registered"
  f" (table: base + pairing x 10,000 + i, i < 500, first_seat = i % 2; block: 22,900,000,000 + row x 10,000 + j, j < 1,500, Lucario side a, first_seat = j % 2)")
last_seed = max(g["seed"] for g in KM_B + KT_B)
p(f"  block seeds span {min(g['seed'] for g in KM_B + KT_B):,} to {last_seed:,}")
p(f"kta3 arm, deals 0-499, v kta3's references (fields {', '.join(ref_fields)}): games differing per row "
  f"{[ref_diff[cell_of(s, pr)] for s, pr in D_ROWS]}; total {sum(ref_diff.values())} of 4500 -> {'REPLAYS' if not sum(ref_diff.values()) else 'DIFFERS'}")

# km3 arm on 0-499 against clause (c)'s mixed rows (the same games by definition; determinism, reported)
MF = by_key(rd(B + "mixed_table_km3_first.jsonl") + rd(B + "mixed_new17_km3_first.jsonl"), ab)
MS = by_key(rd(B + "mixed_table_km3_second.jsonl") + rd(B + "mixed_new17_km3_second.jsonl"), ab)
cmp_n = cmp_d = 0
for src, pr in D_ROWS:
    cell = cell_of(src, pr)
    M = MF if cell[0] == "lucario" else MS
    for i in range(500):
        cmp_n += 1
        if any(kmT[cell][i].get(f) != M[cell][i].get(f) for f in ("moves", "decisions", "first_deck_score", "seed", "first_seat", "bot_a", "bot_b")):
            cmp_d += 1
p(f"km3 arm, deals 0-499, v clause (c)'s mixed rows with km3 on Lucario (moves, decisions, score, seed, seat, bots): {cmp_d} of {cmp_n} differ (reported)")


def exact_mv(d):
    n = len(d)
    m = sum(d, Fr(0)) / n
    v = sum(((x - m) ** 2 for x in d), Fr(0)) / (n - 1) / n
    return m, v


def dsqrt(fr):
    return (Decimal(fr.numerator) / Decimal(fr.denominator)).sqrt()


def dec(fr):
    return Decimal(fr.numerator) / Decimal(fr.denominator)


p("")
p("CLAUSE (d): Lucario's own side, km3 on Lucario (kta3 on the other deck) minus kta3 on both, points; N = 2,000 per row")
means, varis = [], []
for row, (src, pr) in enumerate(D_ROWS):
    cell = cell_of(src, pr)
    m, v = exact_mv(row_diffs[row])
    means.append(m)
    varis.append(v)
    hw = Decimal("1.96") * dsqrt(v)
    ch = sum(1 for x in row_diffs[row] if x != 0)
    tm, tv = exact_mv(row_parts[row][0])
    bm, bv = exact_mv(row_parts[row][1])
    p(f"  row {row} ({src} {pr}, {cell[0]} v {cell[1]}): mean {float(m):+.6f} (exact {m}), var of mean {float(v):.8f},"
      f" 95% {float(m) - float(hw):+.4f} to {float(m) + float(hw):+.4f}; deals with a changed result {ch};"
      f" table part {float(tm):+.3f}, block part {float(bm):+.3f}; Lucario kta3 {arm_avg[row][0]:.2f} -> km3 {arm_avg[row][1]:.2f}; km3-arm games whose moves differ {arm_avg[row][2]} (reported)")
p(f"  km3-arm games whose moves differ from the kta3 arm's: {sum(x[2] for x in arm_avg)} of 18000 (reported)")
k = len(means)
pooled = sum(means, Fr(0)) / k
sumv = sum(varis, Fr(0))
hw = Decimal("1.96") * dsqrt(sumv) / Decimal(k)
lo = dec(pooled) - hw
hi = dec(pooled) + hw
p(f"  POOLED (equal-weight mean of the 9 row means): {dec(pooled):.12f} (exact {pooled})")
p(f"  sum of per-row variances of the mean difference: {dec(sumv):.12f} (exact {sumv})")
p(f"  HALF-WIDTH 1.96 x sqrt(sum var) / 9 = {hw:.12f}")
p(f"  LOWER EDGE (mean - half-width) = {lo:.15f}")
p(f"  upper edge = {hi:.15f}")
p(f"  (d): whole 95% interval above zero: {lo > 0} -> {'PASS' if lo > 0 else 'FAIL'}; lower edge {lo:.6e}")
sd = hw / Decimal("1.96")
p(f"  sd {sd:.6f}; MDE50 (1.96 sd) {Decimal('1.96') * sd:.6f}; MDE80 (2.80 sd) {Decimal('2.80') * sd:.6f} (reported)")
shares = [float(m / sum(means, Fr(0))) for m in means]
p(f"  row shares of the pooled gain: {', '.join(f'{s:.3f}' for s in shares)} (reported)")
# leave-one-out and the stratified-within-row variant: reported only, not the registered statistic
for drop in range(k):
    mm = [m for j, m in enumerate(means) if j != drop]
    vv = [v for j, v in enumerate(varis) if j != drop]
    pm = sum(mm, Fr(0)) / 8
    h8 = Decimal("1.96") * dsqrt(sum(vv, Fr(0))) / 8
    p(f"    without row {drop}: {float(pm):+.3f} +/- {float(h8):.3f} (reported only)")
sv = Fr(0)
sm = []
for tdiff, bdiff in row_parts:
    tm, tv = exact_mv(tdiff)
    bm, bv = exact_mv(bdiff)
    sm.append(Fr(500, 2000) * tm + Fr(1500, 2000) * bm)
    sv += Fr(500, 2000) ** 2 * tv + Fr(1500, 2000) ** 2 * bv
ps = sum(sm, Fr(0)) / 9
hs = Decimal("1.96") * dsqrt(sv) / 9
p(f"  NOT the registered statistic (reported only): stratified within each row (500 table + 1,500 block, weights 1/4, 3/4):"
  f" {dec(ps):.6f} +/- {hs:.6f}, lower edge {dec(ps) - hs:.6f}")
write("sr3_clause_d.txt", lines)
