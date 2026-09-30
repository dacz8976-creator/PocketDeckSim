#!/usr/bin/env python3
"""checker-b: independent re-computation of km's M1/M2 threshold numbers.

Written from the text only: rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md,
the registration block items 1-5, section 5 step 3 ("The rates", "The threshold: the exact
midpoint", "The paired-noise calculation, frozen") and Amendment 1 (b) item 2's M1/M2 line
(kta3 is the baseline; T = (R_kta3 + R_km3) / 2 exact; replicate difference =
sum_played_km3/sum_offered_km3 - sum_played_kta3/sum_offered_kta3).
The percentile rule is score.py's pct (rl/results/table_readings_2026-09-24/score.py, 143-144).
km_thresholds.py, its tests and its outputs were not read.

Inputs: the committed raw counter rows of both arms (deals 200-299 of the 14 gating cells).
Output: check_b.txt next to this file (and the same text on stdout).
"""
import hashlib
import json
import os
import platform
import random
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.dirname(HERE)  # rl/results/km_tables_2026-09-30
FILES = {
    "kta3": os.path.join(TABLES, "1f6319e_sample_kta3_rows.jsonl"),
    "km3": os.path.join(TABLES, "1f6319e_sample_km3_rows.jsonl"),
}
BASELINE, CANDIDATE = "kta3", "km3"   # Amendment 1 (b) item 2: kog3 reads kta3

REPLICATES = 10000
DEALS = list(range(200, 300))        # i = 200 .. 299, increasing
SEED_BASE = {"table": 72_000_000, "new_decks.tsv": 21_108_000_000}

# Step 3, "The paired-noise calculation, frozen", item 1: cells in this fixed order.
# (source, pairing, first-named deck, second-named deck)
LINES = [
    {
        "name": "M1",
        "card": "Arena of Antiquity",
        "owner": "lucario",
        "seed": 20260929,
        "cells": [
            ("table", 2, "altaria", "lucario"),
            ("table", 8, "blaziken", "lucario"),
            ("table", 13, "hydreigon", "lucario"),
            ("table", 18, "lucario", "sceptile"),
            ("table", 19, "lucario", "suicune"),
            ("table", 20, "lucario", "vespiquen"),
            ("table", 21, "lucario", "weezing"),
            ("new_decks.tsv", 8, "rayquaza", "lucario"),
            ("new_decks.tsv", 16, "altaria_greninja", "lucario"),
        ],
    },
    {
        "name": "M2",
        "card": "Training Area",
        "owner": "altaria",
        "seed": 20260930,
        "cells": [
            ("table", 0, "altaria", "blaziken"),
            ("table", 1, "altaria", "hydreigon"),
            ("table", 3, "altaria", "sceptile"),
            ("table", 4, "altaria", "suicune"),
            ("new_decks.tsv", 9, "rayquaza", "altaria"),
        ],
    },
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pct(sorted_vals, q):
    # score.py's rule: element int(q * n), clamped to [0, n - 1], counting from 0.
    n = len(sorted_vals)
    return sorted_vals[min(n - 1, max(0, int(q * n)))]


def load(arm):
    rows = {}
    with open(FILES[arm]) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            key = (r["source"], r["pairing"], r["i"])
            if key in rows:
                raise SystemExit("duplicate row %r in %s" % (key, arm))
            if r["bots"] != [arm, arm]:
                raise SystemExit("row %r of %s has bots %r" % (key, arm, r["bots"]))
            rows[key] = r
    return rows


def owner_counts(r, owner, card):
    """(offered, played) of `card` on the owner's side of one game."""
    sides = [c for c in r["counts"] if c["deck"] == owner]
    if len(sides) != 1:
        raise SystemExit("row %r: %d sides named %s" % ((r["source"], r["pairing"], r["i"]), len(sides), owner))
    entry = sides[0]["cards"].get(card)
    if entry is None:
        return 0, 0
    off, pl = entry["offered"], entry["played"]
    if not (isinstance(off, int) and isinstance(pl, int) and 0 <= pl <= off):
        raise SystemExit("row %r: bad counts %r" % ((r["source"], r["pairing"], r["i"]), entry))
    return off, pl


def check_row(r, cell, i):
    source, pairing, a, b = cell
    key = (source, pairing, i)
    if (r["a"], r["b"]) != (a, b):
        raise SystemExit("row %r: decks %r %r, expected %r %r" % (key, r["a"], r["b"], a, b))
    if r["seed"] != SEED_BASE[source] + pairing * 10_000 + i:
        raise SystemExit("row %r: seed %r" % (key, r["seed"]))
    want = [a, b] if i % 2 == 0 else [b, a]   # even i puts the first-named deck in seat 0
    if r["seat_decks"] != want:
        raise SystemExit("row %r: seat_decks %r, expected %r" % (key, r["seat_decks"], want))
    if sorted(c["seat"] for c in r["counts"]) != [0, 1]:
        raise SystemExit("row %r: counts seats" % (key,))
    for c in r["counts"]:
        if r["seat_decks"][c["seat"]] != c["deck"]:
            raise SystemExit("row %r: counts deck/seat mismatch" % (key,))


def fmt_pct(fr):
    """One-decimal display (half up), plus 4 decimals for reference; display only."""
    d = Decimal(fr.numerator) * 100 / Decimal(fr.denominator)
    return "%s%% (%s%%)" % (d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
                            d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def run_line(line, rows):
    card, owner = line["card"], line["owner"]
    cell_units = []   # per cell, the 100 units in increasing i: (off_b, pl_b, off_c, pl_c)
    per_cell = []
    for cell in line["cells"]:
        source, pairing = cell[0], cell[1]
        units = []
        for i in DEALS:
            key = (source, pairing, i)
            rb, rc = rows[BASELINE].get(key), rows[CANDIDATE].get(key)
            if rb is None or rc is None:
                raise SystemExit("missing deal %r" % (key,))
            check_row(rb, cell, i)
            check_row(rc, cell, i)
            for f in ("seed", "a", "b", "a_file", "b_file", "seat_decks", "first_seat"):
                if rb[f] != rc[f]:
                    raise SystemExit("deal %r: arms differ on %s" % (key, f))
            ob, pb = owner_counts(rb, owner, card)
            oc, pc = owner_counts(rc, owner, card)
            units.append((ob, pb, oc, pc))
        cell_units.append(units)
        per_cell.append((cell, [sum(u[k] for u in units) for k in range(4)]))

    tot = [sum(u[k] for units in cell_units for u in units) for k in range(4)]
    off_b, pl_b, off_c, pl_c = tot
    out = {"line": line["name"], "card": card, "owner": owner, "seed": line["seed"],
           "cells": [list(c[:2]) for c in line["cells"]],
           "baseline": BASELINE, "candidate": CANDIDATE,
           "offered_" + BASELINE: off_b, "played_" + BASELINE: pl_b,
           "offered_" + CANDIDATE: off_c, "played_" + CANDIDATE: pl_c,
           "per_cell": per_cell}

    # "If an arm's offered sum on the sample is 0, the line cannot pass."
    if off_b == 0 or off_c == 0:
        out.update(result="cannot pass (an arm's offered sum is 0)", R_b=None, R_c=None, T=None,
                   lower=None, upper=None, zero_replicates=None)
        return out

    R_b = Fraction(pl_b, off_b)
    R_c = Fraction(pl_c, off_c)
    T = (R_b + R_c) / 2

    # The frozen bootstrap: one fresh generator for this line, used for nothing else.
    rng = random.Random(line["seed"])
    diffs = []
    zero_reps = 0
    for _ in range(REPLICATES):
        s_ob = s_pb = s_oc = s_pc = 0
        for units in cell_units:                 # cells in the fixed order
            n = len(units)                       # 100
            for _d in range(n):                  # 100 draws per cell
                ob, pb, oc, pc = units[rng.randrange(n)]
                s_ob += ob
                s_pb += pb
                s_oc += oc
                s_pc += pc
        if s_ob == 0 or s_oc == 0:
            zero_reps += 1
            diffs.append(0.0)
        else:
            diffs.append(s_pc / s_oc - s_pb / s_ob)
    diffs.sort()
    assert min(len(diffs) - 1, max(0, int(0.025 * len(diffs)))) == 250
    assert min(len(diffs) - 1, max(0, int(0.975 * len(diffs)))) == 9750
    lower, upper = pct(diffs, 0.025), pct(diffs, 0.975)
    result = ("lower bound above zero: the line can pass; T stands" if lower > 0
              else "cannot pass (lower bound is zero or below)")
    out.update(R_b=R_b, R_c=R_c, T=T, lower=lower, upper=upper, zero_replicates=zero_reps,
               result=result, point_diff=float(R_c - R_b))
    return out


def main():
    lines_out = []
    w = lines_out.append
    w("checker-b: independent check of km's M1/M2 thresholds (deals 200-299, 14 gating cells)")
    w("Text: rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md (registration block 1-5;")
    w("  section 5 step 3; Amendment 1 (b) item 2: baseline kta3, candidate km3). pct: score.py 143-144.")
    w("Python: %s (%s)" % (sys.version.replace("\n", " "), platform.python_implementation()))
    w("check_b.py sha256: %s" % sha256(os.path.abspath(__file__)))
    for arm in (BASELINE, CANDIDATE):
        w("input %-5s %s  sha256 %s" % (arm, os.path.basename(FILES[arm]), sha256(FILES[arm])))
    rows = {arm: load(arm) for arm in (BASELINE, CANDIDATE)}
    w("rows: %s %d, %s %d" % (BASELINE, len(rows[BASELINE]), CANDIDATE, len(rows[CANDIDATE])))
    w("")

    results = []
    for line in LINES:
        r = run_line(line, rows)
        results.append(r)
        w("== %s, %s (%s's side), bootstrap seed %d, %d replicates ==" %
          (r["line"], r["card"], r["owner"], r["seed"], REPLICATES))
        w("cells, in the fixed order: %s" % ", ".join("%s %d" % (c[0], c[1]) for c in line["cells"]))
        w("per cell (offered/played): %s | %s" % (BASELINE, CANDIDATE))
        for cell, s in r["per_cell"]:
            w("  %-14s %2d %-17s v %-10s  %4d / %4d  |  %4d / %4d" %
              (cell[0], cell[1], cell[2], cell[3], s[0], s[1], s[2], s[3]))
        w("%s: offered %d, played %d" % (BASELINE, r["offered_" + BASELINE], r["played_" + BASELINE]))
        w("%s: offered %d, played %d" % (CANDIDATE, r["offered_" + CANDIDATE], r["played_" + CANDIDATE]))
        if r["T"] is None:
            w("RESULT: %s" % r["result"])
            w("")
            continue
        w("R_%s = %d/%d = %s (reduced)  display %s" %
          (BASELINE, r["played_" + BASELINE], r["offered_" + BASELINE], r["R_b"], fmt_pct(r["R_b"])))
        w("R_%s = %d/%d = %s (reduced)  display %s" %
          (CANDIDATE, r["played_" + CANDIDATE], r["offered_" + CANDIDATE], r["R_c"], fmt_pct(r["R_c"])))
        w("T = (R_%s + R_%s)/2 = %s (exact)  display %s" % (BASELINE, CANDIDATE, r["T"], fmt_pct(r["T"])))
        w("point difference R_%s - R_%s (float, reported only) = %r" % (CANDIDATE, BASELINE, r["point_diff"]))
        w("replicates with an arm's offered sum 0: %d" % r["zero_replicates"])
        w("lower bound (sorted[250])  = %r   (%.17g, hex %s)" % (r["lower"], r["lower"], float.hex(r["lower"])))
        w("upper bound (sorted[9750]) = %r   (%.17g, hex %s)" % (r["upper"], r["upper"], float.hex(r["upper"])))
        w("RESULT: %s" % r["result"])
        w("")

    machine = []
    for r in results:
        m = {k: r[k] for k in ("line", "card", "owner", "seed", "baseline", "candidate",
                               "offered_" + BASELINE, "played_" + BASELINE,
                               "offered_" + CANDIDATE, "played_" + CANDIDATE, "zero_replicates", "result")}
        for k in ("R_b", "R_c", "T"):
            m[k] = None if r[k] is None else "%d/%d" % (r[k].numerator, r[k].denominator)
        m["lower"] = r["lower"]
        m["upper"] = r["upper"]
        m["can_pass"] = r["lower"] is not None and r["lower"] > 0
        machine.append(m)
    w("RESULTS_JSON: " + json.dumps(machine, sort_keys=True))
    text = "\n".join(lines_out) + "\n"
    with open(os.path.join(HERE, "check_b.txt"), "w") as f:
        f.write(text)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
