"""Item 6: M1 and M2 on the gating deals (0-199) from the counter rows, owner's side only, exact Fractions against
T1 = 100263/362752 and T2 = 24383/75980 (Amendment 2), with the guard (kta3's own rate on the same deals, compared
with the same exact T). Written from step 3 ("The rates": R = turns played added up / turns offered added up, owner's
side only, Lucario's for Arena of Antiquity over table 2, 8, 13, 18, 19, 20, 21 and new_decks 8, 16; Altaria's for
Training Area over table 0, 1, 3, 4 and new_decks 9) and Amendment 2.
Also (beside, not asked): the counter rows' deals, seeds, seats and bots; their move fingerprints against the
both-sides games (kta3's references; km3's own footprint games); and T1, T2 and the frozen paired bootstrap
re-derived from the sample rows (deals 200-299) with this script's own code, as Amendment 2's check.
Writes OUT/sr5_m1m2.txt."""
import sys, ast, random
from fractions import Fraction as Fr
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

lines = []
p = lines.append
T1, T2 = Fr(100263, 362752), Fr(24383, 75980)
LINES = {"M1": ("Arena of Antiquity", "lucario", M1_CELLS, T1, 20260929),
         "M2": ("Training Area", "altaria", M2_CELLS, T2, 20260930)}


def load_rows(path, bots, lo, hi, cells, ref_games):
    rows = rd(path)
    out = {}
    nmv = 0
    for r in rows:
        src = "table" if r["source"] == "table" else "new"
        key = (src, r["pairing"])
        cell = cell_of(src, r["pairing"])
        assert (r["a"], r["b"]) == cell, (r["a"], r["b"], cell)
        assert list(r["bots"]) == list(bots), r["bots"]
        base = TABLE_BASE if src == "table" else NEW_BASE
        assert r["seed"] == base + r["pairing"] * 10000 + r["i"] and r["first_seat"] == r["i"] % 2, (key, r["i"])
        assert lo <= r["i"] < hi
        assert key not in out or r["i"] not in out[key]
        g = ref_games[cell][r["i"]]
        assert g["seed"] == r["seed"] and g["first_seat"] == r["first_seat"]
        if g["moves"] != r["moves"]:
            nmv += 1
        counts = ast.literal_eval(r["counts"]) if isinstance(r["counts"], str) else r["counts"]
        out.setdefault(key, {})[r["i"]] = counts
    assert set(out) == set(cells), (sorted(out), sorted(cells))
    assert all(set(v) == set(range(lo, hi)) for v in out.values())
    return out, nmv


def owner_counts(counts, owner, card):
    ent = [c for c in counts if c["deck"] == owner]
    assert len(ent) == 1, (owner, [c["deck"] for c in counts])
    x = ent[0]["cards"].get(card, {"offered": 0, "played": 0})
    return x["played"], x["offered"]


REF = by_key(rd(KT + "/ec7e1a8_kta3_table.jsonl") + rd(KT + "/ec7e1a8_kta3_new17.jsonl"), ab)
KMG = by_key(rd(B + "km3_table.jsonl") + rd(B + "km3_new17.jsonl"), ab)
ALL17 = [("table", p_) for p_ in (0, 1, 2, 3, 4, 5, 6, 8, 13, 18, 19, 20, 21)] + [("new", p_) for p_ in (8, 9, 16, 17)]
C_kta, mv_kta = load_rows(B + "counters_kta3_rows.jsonl", ("kta3", "kta3"), 0, 200, ALL17, REF)
C_km, mv_km = load_rows(B + "counters_km3_rows.jsonl", ("km3", "km3"), 0, 200, ALL17, KMG)
p(f"COUNTER ROWS, deals 0-199 of the 17 named cells: kta3 {sum(len(v) for v in C_kta.values())} rows, km3 {sum(len(v) for v in C_km.values())} rows;"
  f" cells, deals, seeds, seats and bots as registered; move fingerprints v the both-sides games: kta3 v kta3's references {mv_kta} differ,"
  f" km3 v km3's footprint games {mv_km} differ")

p("")
for name, (card, owner, cells, T, _) in LINES.items():
    tot = {}
    for arm, C in (("kta3", C_kta), ("km3", C_km)):
        pl = of = 0
        per = []
        for key in cells:
            cp = co = 0
            for i in range(200):
                a_, b_ = owner_counts(C[key][i], owner, card)
                cp += a_
                co += b_
            pl += cp
            of += co
            per.append((key, cp, co))
        tot[arm] = (pl, of, per)
    kp, ko, kper = tot["km3"]
    tp, to, tper = tot["kta3"]
    Rkm, Rkt = Fr(kp, ko), Fr(tp, to)
    passes = Rkm >= T
    guard = Rkt >= T
    p(f"{name}, {card} ({owner}'s side), deals 0-199 of {len(cells)} cells:")
    p(f"  km3: played {kp} of {ko} offered turns = {Rkm} = {float(Rkm) * 100:.4f}%")
    p(f"  kta3: played {tp} of {to} offered turns = {Rkt} = {float(Rkt) * 100:.4f}%")
    p(f"  T = {T} = {float(T) * 100:.4f}%")
    p(f"  km3 rate >= T (exact Fraction comparison): {passes}  (km3 - T = {Rkm - T} = {float(Rkm - T) * 100:+.4f} points)")
    p(f"  GUARD: kta3's rate >= T: {guard}  (kta3 - T = {float(Rkt - T) * 100:+.4f} points) -> {'NOT SHOWN AT THIS SIZE (guard)' if guard else 'guard clear'}")
    p(f"  LINE: {'PASS' if passes and not guard else 'NOT PASSED'}")
    rises = sum(1 for (k1, a1, b1), (k2, a2, b2) in zip(kper, tper) if b1 and b2 and Fr(a1, b1) > Fr(a2, b2))
    p(f"  per cell (km3 played/offered | kta3 played/offered; reported): "
      + "; ".join(f"{k1[0]} {k1[1]}: {a1}/{b1} | {a2}/{b2}" for (k1, a1, b1), (k2, a2, b2) in zip(kper, tper))
      + f"; cells where km3's rate is higher: {rises} of {len(cells)}")

# ---------- Amendment 2 re-derived from the sample rows (deals 200-299, the 14 gating cells)
p("")
p("AMENDMENT 2 re-derived from the sample rows (deals 200-299), this script's own code:")
GATE14 = M1_CELLS + M2_CELLS
S_kta, smv_kta = load_rows(B + "sample_kta3_rows.jsonl", ("kta3", "kta3"), 200, 300, GATE14, REF)
S_km, smv_km = load_rows(B + "sample_km3_rows.jsonl", ("km3", "km3"), 200, 300, GATE14, KMG)
p(f"  sample rows: kta3 {sum(len(v) for v in S_kta.values())}, km3 {sum(len(v) for v in S_km.values())}; fingerprints v both-sides games: kta3 {smv_kta} differ, km3 {smv_km} differ")
for name, (card, owner, cells, T, seed) in LINES.items():
    units = []
    for key in cells:
        dl = []
        for i in range(200, 300):
            dl.append(owner_counts(S_km[key][i], owner, card) + owner_counts(S_kta[key][i], owner, card))
        units.append(dl)
    kp = sum(u[0] for dl in units for u in dl); ko = sum(u[1] for dl in units for u in dl)
    tp = sum(u[2] for dl in units for u in dl); to = sum(u[3] for dl in units for u in dl)
    Tm = (Fr(kp, ko) + Fr(tp, to)) / 2
    rng = random.Random(seed)
    diffs, zero = [], 0
    for _ in range(10000):
        a = b = c = d = 0
        for dl in units:
            for _ in range(100):
                u = dl[rng.randrange(100)]
                a += u[0]; b += u[1]; c += u[2]; d += u[3]
        if b == 0 or d == 0:
            diffs.append(0.0); zero += 1
        else:
            diffs.append(a / b - c / d)
    diffs.sort()
    lo, hi = diffs[250], diffs[9750]
    p(f"  {name}: kta3 {tp}/{to} = {Fr(tp, to)}, km3 {kp}/{ko} = {Fr(kp, ko)}; T = {Tm} (Amendment 2: {T}; equal: {Tm == T});"
      f" paired 95% interval {lo!r} to {hi!r} (zero-offered replicates {zero}); lower bound above zero: {lo > 0}")
write("sr5_m1m2.txt", lines)
