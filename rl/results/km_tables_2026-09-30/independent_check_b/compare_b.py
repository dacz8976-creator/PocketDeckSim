#!/usr/bin/env python3
"""checker-b, step 2: compare check_b.txt's numbers (already written) with thresholds.json.

Reads only check_b.txt's RESULTS_JSON line (it does not recompute) and ../thresholds.json,
then appends the comparison to check_b.txt. Exact comparisons: integers ==, fractions as
Fraction ==, bounds as Python floats == and as repr strings ==.
"""
import datetime
import hashlib
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
MINE = os.path.join(HERE, "check_b.txt")
THEIRS = os.path.join(os.path.dirname(HERE), "thresholds.json")


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def disp(frac_str):
    # the same one-decimal, half-up display check_b.py prints first in its "display" column
    fr = Fraction(frac_str)
    d = Decimal(fr.numerator) * 100 / Decimal(fr.denominator)
    return "%s%%" % d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


with open(MINE) as f:
    text = f.read()
if "== Comparison with thresholds.json" in text:
    raise SystemExit("comparison already appended")
mine_sha = hashlib.sha256(text.encode()).hexdigest()
mine = {m["line"]: m for m in json.loads(
    [l for l in text.splitlines() if l.startswith("RESULTS_JSON: ")][0][len("RESULTS_JSON: "):])}
with open(THEIRS) as f:
    theirs = json.load(f)
# the "cells, in the fixed order:" lines of check_b.txt, M1's section first, then M2's
_cell_lines = [l.split(": ", 1)[1] for l in text.splitlines() if l.startswith("cells, in the fixed order: ")]
mine_cells = {name: ",".join(c.replace(" ", ":") for c in cl.split(", "))
              for name, cl in zip(("M1", "M2"), _cell_lines)}

out = []
w = out.append
n_agree = n_dis = 0


def cmp(label, a, b, eq=None):
    global n_agree, n_dis
    same = (a == b) if eq is None else eq(a, b)
    if same:
        n_agree += 1
    else:
        n_dis += 1
    w("  %-9s %-34s mine %-26s thresholds.json %s" % ("AGREE" if same else "DISAGREE", label, a, b))


w("")
w("== Comparison with thresholds.json (appended after the numbers above were written) ==")
w("written %s UTC; check_b.txt before this section sha256 %s" %
  (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), mine_sha))
w("thresholds.json sha256 %s (km_thresholds.py sha256 %s, Python %s)" %
  (sha256(THEIRS), theirs.get("km_thresholds_py_sha256"), theirs.get("python")))
for arm in ("kta3", "km3"):
    inp = theirs["inputs"][arm]
    mine_line = [l for l in text.splitlines() if l.startswith("input %-5s" % arm)][0]
    cmp("input %s sha256" % arm, mine_line.split("sha256 ")[1].strip(), inp["sha256"])

for name in ("M1", "M2"):
    m, t = mine[name], theirs["lines"][name]
    w("%s, %s:" % (name, m["card"]))
    cmp("owner side", m["owner"], t["owner_side"])
    cmp("cells, in order", mine_cells[name], ",".join(t["cells"]))
    for arm in ("kta3", "km3"):
        cmp("%s offered" % arm, m["offered_" + arm], t[arm]["offered"])
        cmp("%s played" % arm, m["played_" + arm], t[arm]["played"])
    cmp("R_kta3 (exact fraction)", m["R_b"], t["kta3"]["rate"], lambda a, b: Fraction(a) == Fraction(b))
    cmp("R_km3 (exact fraction)", m["R_c"], t["km3"]["rate"], lambda a, b: Fraction(a) == Fraction(b))
    cmp("T (exact fraction)", m["T"], t["T"], lambda a, b: Fraction(a) == Fraction(b))
    cmp("R_kta3 display", disp(m["R_b"]), t["kta3"]["rate_display"])
    cmp("R_km3 display", disp(m["R_c"]), t["km3"]["rate_display"])
    cmp("T display", disp(m["T"]), t["T_display"])
    cmp("resampling seed", m["seed"], t["interval_detail"]["resampling_seed"])
    cmp("zero-offered replicates", m["zero_replicates"], t["interval_detail"]["zero_offered_replicates"])
    cmp("lower bound (float ==)", repr(m["lower"]), repr(t["interval"][0]))
    cmp("lower bound (repr string)", repr(m["lower"]), t["interval_detail"]["lower_repr"])
    cmp("upper bound (float ==)", repr(m["upper"]), repr(t["interval"][1]))
    cmp("upper bound (repr string)", repr(m["upper"]), t["interval_detail"]["upper_repr"])
    their_pass = (t["status"] == "threshold")
    cmp("result (can pass / cannot pass)", "can pass" if m["can_pass"] else "cannot pass",
        "can pass" if their_pass else "cannot pass (status %s)" % t["status"])
w("TOTAL: %d AGREE, %d DISAGREE" % (n_agree, n_dis))

with open(MINE, "a") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
