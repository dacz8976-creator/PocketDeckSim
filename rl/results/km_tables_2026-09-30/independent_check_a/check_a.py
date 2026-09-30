#!/usr/bin/env python3
"""checker-a: independent re-computation of km's M1/M2 thresholds from the raw sample rows.

Written from rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md only:
  - registration block, items 1-5 (exact midpoint; frozen paired-noise calculation; "cannot pass" final);
  - section 5, step 3, "The threshold rule for T1 and T2" and "The paired-noise calculation, frozen";
  - Amendment 1 (b) item 2, the M1/M2 line (kta3 is the baseline; T = (R_kta3 + R_km3) / 2 exact;
    replicate difference = sum_played_km3/sum_offered_km3 - sum_played_kta3/sum_offered_kta3).
  - score.py's pct (rl/results/table_readings_2026-09-24/score.py, lines 143-144), copied below.
It does not import or re-run km_thresholds.py, and it did not read thresholds.json before writing its numbers.

Usage: python3 check_a.py <kta3_rows.jsonl> <km3_rows.jsonl> <out.txt>
"""
import hashlib
import json
import platform
import random
import sys
from fractions import Fraction

# ---- the text's fixed definitions -------------------------------------------------------------

# Step 3, "The paired-noise calculation, frozen", item 1: the line's cells in this fixed order.
# A cell is (source, pairing): source "table" = the table's pairings, "new_decks.tsv" = new_decks.tsv's.
LINES = [
    {
        "name": "M1",
        "card": "Arena of Antiquity",
        "owner": "lucario",  # Lucario's side
        "cells": [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19),
                  ("table", 20), ("table", 21), ("new_decks.tsv", 8), ("new_decks.tsv", 16)],
        "seed": 20260929,
    },
    {
        "name": "M2",
        "card": "Training Area",
        "owner": "altaria",  # Altaria's side (the research/t- Altaria list, not Altaria/Greninja)
        "cells": [("table", 0), ("table", 1), ("table", 3), ("table", 4), ("new_decks.tsv", 9)],
        "seed": 20260930,
    },
]
DEALS = list(range(200, 300))  # i = 200, 201, ..., 299, increasing
REPS = 10000
BASE, CAND = "kta3", "km3"  # Amendment 1 (b) item 2: kta3 is the baseline


def pct(sorted_vals, q):
    # score.py (rl/results/table_readings_2026-09-24/score.py), lines 143-144, verbatim
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]


# ---- reading the raw rows ---------------------------------------------------------------------

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path, arm):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            assert r["bots"] == [arm, arm], (path, r["bots"])
            key = (r["source"], r["pairing"], r["i"])
            assert key not in rows, ("duplicate row", key)
            rows[key] = r
    return rows


def owner_counts(r, owner, card):
    """(offered, played) for the card on the owner's side of one game. Missing card = (0, 0)."""
    sides = [c for c in r["counts"] if c["deck"] == owner]
    assert len(sides) == 1, ("owner side not unique", r["source"], r["pairing"], r["i"], owner)
    side = sides[0]
    assert r["seat_decks"][side["seat"]] == owner
    entry = side["cards"].get(card)
    if entry is None:
        return 0, 0
    return int(entry["offered"]), int(entry["played"])


def fmt_pct(fr):
    return "%.1f%%" % float(fr * 100)


def main():
    kta_path, km_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = {BASE: load(kta_path, BASE), CAND: load(km_path, CAND)}
    out = []
    w = out.append
    w("checker-a: independent check of km's M1/M2 threshold sample (deals 200-299, 14 gating cells)")
    w("script: check_a.py (written from REGISTRATION_DRAFT.md; km_thresholds.py not used)")
    w("python: %s (%s)" % (platform.python_version(), sys.version.replace("\n", " ")))
    w("inputs:")
    w("  %s  sha256 %s  rows %d" % (kta_path.split("/")[-1], sha256(kta_path), len(rows[BASE])))
    w("  %s  sha256 %s  rows %d" % (km_path.split("/")[-1], sha256(km_path), len(rows[CAND])))
    w("check_a.py sha256 %s" % sha256(sys.argv[0]))
    w("")

    # Every row in the files belongs to one of the 14 cells, deals 200-299, both arms, paired by deal.
    all_cells = {c for L in LINES for c in L["cells"]}
    for arm in (BASE, CAND):
        keys = set(rows[arm])
        want = {(s, p, i) for (s, p) in all_cells for i in DEALS}
        assert keys == want, (arm, len(keys ^ want))
    for key in rows[BASE]:
        a, b = rows[BASE][key], rows[CAND][key]
        for fld in ("seed", "seat_decks", "first_seat", "a", "b", "a_file", "b_file"):
            assert a[fld] == b[fld], (key, fld)
    w("pairing check: both files hold exactly the 14 cells x deals 200-299 (1,400 rows each);")
    w("  every deal's two rows agree on seed, seat_decks, first_seat, a, b, a_file, b_file.")
    w("")

    for L in LINES:
        card, owner = L["card"], L["owner"]
        # units[c] = list over deals (increasing i) of (off_base, pl_base, off_cand, pl_cand)
        units = []
        tot = {BASE: [0, 0], CAND: [0, 0]}  # [offered, played]
        per_cell = []
        for (src, p) in L["cells"]:
            cell_units = []
            ct = {BASE: [0, 0], CAND: [0, 0]}
            for i in DEALS:
                ob, pb = owner_counts(rows[BASE][(src, p, i)], owner, card)
                oc, pc = owner_counts(rows[CAND][(src, p, i)], owner, card)
                cell_units.append((ob, pb, oc, pc))
                ct[BASE][0] += ob; ct[BASE][1] += pb
                ct[CAND][0] += oc; ct[CAND][1] += pc
            units.append(cell_units)
            r0 = rows[BASE][(src, p, DEALS[0])]
            per_cell.append(((src, p, r0["a"], r0["b"]), ct))
            for arm in (BASE, CAND):
                tot[arm][0] += ct[arm][0]; tot[arm][1] += ct[arm][1]

        w("=" * 100)
        w("%s  %s  (owner: %s's side; %d cells; bootstrap seed %d)" % (L["name"], card, owner, len(L["cells"]), L["seed"]))
        w("-" * 100)
        w("per cell, in the fixed order (reported only):  cell | kta3 played/offered | km3 played/offered")
        for (src, p, a, b), ct in per_cell:
            w("  %-14s %2d  %-17s v %-10s | %4d / %4d | %4d / %4d" % (src, p, a, b, ct[BASE][1], ct[BASE][0], ct[CAND][1], ct[CAND][0]))
        w("pooled counts (owner's side, all cells, deals 200-299):")
        w("  kta3: offered %d, played %d" % (tot[BASE][0], tot[BASE][1]))
        w("  km3:  offered %d, played %d" % (tot[CAND][0], tot[CAND][1]))

        cannot = []
        if tot[BASE][0] == 0 or tot[CAND][0] == 0:
            cannot.append("an arm's offered sum is 0")
            R_base = R_cand = T = None
        else:
            R_base = Fraction(tot[BASE][1], tot[BASE][0])
            R_cand = Fraction(tot[CAND][1], tot[CAND][0])
            T = (R_base + R_cand) / 2
            w("rates (exact fractions, reduced; display to one decimal):")
            w("  R_kta3 = %d/%d = %s   (%s)" % (tot[BASE][1], tot[BASE][0], R_base, fmt_pct(R_base)))
            w("  R_km3  = %d/%d = %s   (%s)" % (tot[CAND][1], tot[CAND][0], R_cand, fmt_pct(R_cand)))
            w("  T = (R_kta3 + R_km3) / 2 = %s   (%s)" % (T, fmt_pct(T)))
            w("  (more digits, display only: R_kta3 %.6f%%, R_km3 %.6f%%, T %.6f%%)" % (
                float(R_base * 100), float(R_cand * 100), float(T * 100)))

        # ---- the frozen paired bootstrap ----
        rng = random.Random(L["seed"])
        diffs = []
        zero_reps = 0
        n = len(DEALS)
        for _ in range(REPS):
            ob = pb = oc = pc = 0
            for cell_units in units:  # cells in the fixed order
                for _d in range(n):  # 100 draws per cell
                    u = cell_units[rng.randrange(100)]
                    ob += u[0]; pb += u[1]; oc += u[2]; pc += u[3]
            if ob == 0 or oc == 0:
                diffs.append(0.0)
                zero_reps += 1
            else:
                diffs.append(pc / oc - pb / ob)
        diffs.sort()
        lo = pct(diffs, 0.025)
        hi = pct(diffs, 0.975)
        w("paired percentile bootstrap: %d replicates, random.Random(%d), 100 draws per cell per replicate" % (REPS, L["seed"]))
        w("  indices used: lower = sorted[%d], upper = sorted[%d]" % (
            min(REPS - 1, max(0, int(0.025 * REPS))), min(REPS - 1, max(0, int(0.975 * REPS)))))
        w("  replicates with an arm's offered sum 0 (difference set to 0.0): %d" % zero_reps)
        w("  point difference R_km3 - R_kta3 (float of exact): %r" % (float(R_cand - R_base) if T is not None else None))
        w("  lower bound: %r   (float.hex %s)" % (lo, float.hex(lo)))
        w("  upper bound: %r   (float.hex %s)" % (hi, float.hex(hi)))
        w("  mean of replicates (reported only): %r" % (sum(diffs) / len(diffs)))
        if not (lo > 0):
            cannot.append("lower bound %r is not above zero" % lo)
        if cannot:
            w("RESULT %s: CANNOT PASS (%s). Recorded with its counts, rates, interval and midpoint;" % (L["name"], "; ".join(cannot)))
            w("  the midpoint is not used, adjusted or replaced; no other sample.")
        else:
            w("RESULT %s: lower bound above zero -> the line CAN PASS; T%s = %s (%s) is the threshold for km3's rate on deals 0-199." % (
                L["name"], L["name"][-1], T, fmt_pct(T)))
        w("")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
