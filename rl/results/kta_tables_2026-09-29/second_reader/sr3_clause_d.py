"""Step 3: clause (d) (5.2 (d)): the census Rayquaza list v the eight panel lists, 8 rows x 2,000 fresh deals per arm,
kta3 (arm 2) and kog3 (arm 1) on the Rayquaza list, kog3 on the panel in both arms, paired by seed.
Seeds must be 23,003,000,000 + row x 10,000 + i, i < 2,000; even i puts the Rayquaza list in seat 0.
Statistic: equal-weight mean over rows of the per-row mean difference (kta3 minus kog3) of Rayquaza's own-side score,
half-width 1.96 x sqrt(sum of per-row variances of the mean difference) / 8; passes iff mean - half-width > 0.
Writes OUT/sr3_clause_d.txt."""
import sys, math
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

lines = []
p = lines.append
RAY = "rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt"
PANEL = sorted(NAMES)  # index 0-7, altaria to weezing (3.2)
A1 = by_key(rd(F + "d_kog3.jsonl"), pairing)
A2 = by_key(rd(F + "d_kta3.jsonl"), pairing)
assert sorted(A1) == sorted(A2) == list(range(8))
rows = []
changed = 0
better = worse = 0
for row in range(8):
    g1, g2 = A1[row], A2[row]
    assert set(g1) == set(g2) == set(range(2000)), (row, len(g1), len(g2))
    for i in range(2000):
        r1, r2 = g1[i], g2[i]
        seed = 23003000000 + row * 10000 + i
        assert r1["seed"] == r2["seed"] == seed, (row, i, r1["seed"], r2["seed"])
        assert (r1["bot_a"], r1["bot_b"]) == ("kog3", "kog3") and (r2["bot_a"], r2["bot_b"]) == ("kta3", "kog3"), (row, i)
        assert r1["a_file"] == r2["a_file"] == RAY, r1["a_file"]
        assert r1["b_file"] == r2["b_file"] == f"decks/research/{PANEL[row]}.txt", (row, r1["b_file"])
        assert r1["first_seat"] == r2["first_seat"] == i % 2, (row, i)
        if r1["moves"] != r2["moves"]:
            changed += 1
        if sc(r2) > sc(r1):
            better += 1
        elif sc(r2) < sc(r1):
            worse += 1
    d = paired(g1, g2, +1)
    m, v = mv(d)
    w1 = 100 * sum(sc(r) for r in g1.values()) / 2000
    w2 = 100 * sum(sc(r) for r in g2.values()) / 2000
    rows.append((PANEL[row], w1, w2, m, v, d))
p(f"seeds: every game 23,003,000,000 + row x 10,000 + i, i < 2,000, both arms, paired by seed: checked (16,000 games per arm)")
p(f"sides: Rayquaza = the census list (side a) in both arms; bots kog3/kog3 v kta3/kog3; even i = seat 0: checked")
p(f"kta3-arm games whose moves differ from kog3's: {changed} of 16,000; results better {better}, worse {worse}")
tot_m = sum(r[3] for r in rows)
for name, w1, w2, m, v, d in rows:
    share = f"{100 * m / tot_m:+.0f}%" if tot_m > 0 else "n/a"
    p(f"  v {name:<10}: kog3 {w1:5.2f} -> kta3 {w2:5.2f}  ({m:+.3f} +/- {1.96 * math.sqrt(v):.3f}); share {share}")
M = sum(r[3] for r in rows) / 8
sd = math.sqrt(sum(r[4] for r in rows)) / 8
HW = 1.96 * sd
p(f"POOLED (equal weight over 8 rows): {M:+.4f} +/- {HW:.4f} points (interval {M - HW:+.4f} to {M + HW:+.4f}); "
  f"sd {sd:.4f}; MDE50 {1.96 * sd:.3f}, MDE80 {2.80 * sd:.3f}")
p(f"CLAUSE (d): {'PASS: the whole 95% interval is above zero' if M - HW > 0 else 'FAIL: gain not shown at this size'}")
top = max(rows, key=lambda r: r[3])
p(f"  largest row: {top[0]} {top[3]:+.3f} = {100 * top[3] / tot_m:.0f}% of the sum of row means (more than half: {top[3] > tot_m / 2})")
wo = [r for r in rows if r is not top]
p(f"  without that row (7-row equal weight): {sum(r[3] for r in wo) / 7:+.3f}")
open(OUT + "/sr3_clause_d.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
