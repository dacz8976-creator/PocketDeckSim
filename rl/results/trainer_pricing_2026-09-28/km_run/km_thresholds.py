#!/usr/bin/env python3
"""km_thresholds.py: M1's and M2's thresholds by km's registered procedure.

Written from ../REGISTRATION_DRAFT.md (km, registered Sept 29 at 55e5d95 with Dustin's word; its top block
"Registration (Sept 29, Dustin's word)" governs), step 3, "The threshold rule for T1 and T2", line for line, read with
Amendment 1 (Sept 30), which re-issues km on kta: the baseline arm is kta3 wherever step 3 names km's base ((b) item 2:
"T = (R_kta3 + R_km3) / 2, exact. The frozen bootstrap's replicate difference is sum_played_km3 / sum_offered_km3 -
sum_played_kta3 / sum_offered_kta3. The guard reads kta3's own rate on the gating deals against the same exact T").
The comments marked "Reg:" quote the text each part implements, with that substitution made. The registration names
this file (section 4.0 step 5; step 3): it is committed, with its sha256 and the Python version, before the sample's
first game, and it does not change after that (run_km.sh part T refuses to play the sample unless this file is
committed and unchanged).

  km_thresholds.py sample --kta3 ROWS --km3 ROWS --json OUT.json --txt OUT.txt
                          [--tool-source-sha H] [--tool-program-sha H] [--base-code kta3] [--cand-code km3]
      The development sample: the counter tool's rows (one file per arm; deals 200-299 of the 14 gating cells).
      Per line: both arms' offered and played sums (owner's side), both rates as exact fractions, T = the exact
      midpoint, the frozen paired-noise interval, and the label ("threshold" or "cannot pass"). Writes OUT.json and
      OUT.txt and prints the text. It reports only these (Reg: "The sample's run reports only the counts, the two
      rates per card, the interval and T"). The record's arms are keyed "kta3" and "km3", the registered arms.

  km_thresholds.py gate --thresholds OUT.json --kta3 ROWS --km3 ROWS
      The comparison step 3 makes on the gating deals 0-199 (M1 and M2 and the guard), exactly against T. It is here
      so the rule and its exact comparison sit beside the threshold; the registered reading (read_km.py) owns the
      mechanism test and may call or re-derive it. run_km.sh never calls it.

Exit 0 when the calculation was made (whatever the labels say); 2 on a malformed or incomplete input.
"""
import argparse, hashlib, json, math, os, random, sys
from fractions import Fraction

# Seeds of the table's deals (step 3, "The 17 named cells"): 72,000,000 + pairing x 10,000 + i for the table cells
# (legality_scan's pairing numbers, decks/research lists); 21,108,000,000 + pairing x 10,000 + i for new_decks.tsv's.
# Even i puts the first-named deck in seat 0.
BASES = {"table": 72_000_000, "new_decks.tsv": 21_108_000_000}
# The named cells a line can read, with their first-named and second decks (the counter tool's names).
CELL_DECKS = {
    ("table", 0): ("altaria", "blaziken"), ("table", 1): ("altaria", "hydreigon"), ("table", 2): ("altaria", "lucario"),
    ("table", 3): ("altaria", "sceptile"), ("table", 4): ("altaria", "suicune"), ("table", 5): ("altaria", "vespiquen"),
    ("table", 6): ("altaria", "weezing"), ("table", 8): ("blaziken", "lucario"), ("table", 13): ("hydreigon", "lucario"),
    ("table", 18): ("lucario", "sceptile"), ("table", 19): ("lucario", "suicune"), ("table", 20): ("lucario", "vespiquen"),
    ("table", 21): ("lucario", "weezing"), ("new_decks.tsv", 8): ("rayquaza", "lucario"),
    ("new_decks.tsv", 9): ("rayquaza", "altaria"), ("new_decks.tsv", 16): ("altaria_greninja", "lucario"),
    ("new_decks.tsv", 17): ("altaria_greninja", "altaria"),
}

# Reg (paired-noise calculation, 1. Units): "The line's cells, in this fixed order. Arena: table pairings 2, 8, 13, 18,
# 19, 20, 21, then new_decks.tsv pairings 8, 16 (9 cells). Training Area: table pairings 0, 1, 3, 4, then
# new_decks.tsv pairing 9 (5 cells)."
# Reg (2. Generator): "random.Random(20260929) for Arena and random.Random(20260930) for Training Area."
# Reg (The rates): "counting the card owner's side only (Lucario's for Arena, Altaria's for Training Area)."
LINES = (
    {"line": "M1", "card": "Arena of Antiquity", "owner": "lucario", "seed": 20260929,
     "cells": (("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21),
               ("new_decks.tsv", 8), ("new_decks.tsv", 16))},
    {"line": "M2", "card": "Training Area", "owner": "altaria", "seed": 20260930,
     "cells": (("table", 0), ("table", 1), ("table", 3), ("table", 4), ("new_decks.tsv", 9))},
)
# Reg (The development sample): "Deals 200 to 299 (i = 200 to 299 ...) of the gating cells ... 14 cells in all."
SAMPLE_DEALS = range(200, 300)
# Reg (M1, M2): the gating rates are read "on deals 0 to 199".
GATING_DEALS = range(0, 200)
# Reg (3. Replicates): "10,000, one after another."
REPLICATES = 10_000
DRAWS_PER_CELL = 100
# The registered arms (Amendment 1 (b) items 1-2): the baseline arm kta3 and the candidate arm km3. The record keys the
# arms by these names; --base-code / --cand-code name the code each arm's rows must be played by (a smoke may stand
# kta3 in for km3; the record then names it).
BASE, CAND = "kta3", "km3"


def stop(msg):
    print(f"km_thresholds: STOP: {msg}", file=sys.stderr)
    sys.exit(2)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pct(sorted_vals, q):
    """score.py's pct (rl/results/table_readings_2026-09-24/score.py, lines 143-144), unchanged."""
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]


def load_rows(path, code, deals, cells_needed, exact):
    """The counter tool's rows for one arm. Every row is checked to be the game its deal names (seed, seats, decks,
    both seats played by `code`) and to carry counts. Returns {(source, pairing, i): row}. With exact, the file must
    hold exactly cells_needed x deals, each once; otherwise it must hold at least those (other named cells ignored)."""
    rows = {}
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            key = (r.get("source"), r.get("pairing"), r.get("i"))
            cell = key[:2]
            if cell not in CELL_DECKS:
                stop(f"{path} line {n}: {cell} is not one of the 17 named cells")
            if key in rows:
                stop(f"{path}: deal {key} appears twice")
            a, b = CELL_DECKS[cell]
            i = key[2]
            if (r.get("a"), r.get("b")) != (a, b):
                stop(f"{path}: deal {key} has decks {r.get('a')} v {r.get('b')}, not {a} v {b}")
            if r.get("bots") != [code, code]:
                stop(f"{path}: deal {key} is played by {r.get('bots')}, not {code} on both sides")
            if r.get("seed") != BASES[cell[0]] + 10_000 * cell[1] + i:
                stop(f"{path}: deal {key} has seed {r.get('seed')}, not the table's {BASES[cell[0]] + 10_000 * cell[1] + i}")
            if r.get("first_seat") != i % 2 or r.get("seat_decks") != ([a, b] if i % 2 == 0 else [b, a]):
                stop(f"{path}: deal {key} has seats {r.get('first_seat')} {r.get('seat_decks')}; even i puts {a} in seat 0")
            counts = r.get("counts")
            if not isinstance(counts, list) or len(counts) != 2 or any(
                    counts[s].get("seat") != s or counts[s].get("deck") != r["seat_decks"][s] for s in (0, 1)):
                stop(f"{path}: deal {key} carries no per-seat counts (a --no-counts file is not a measuring file)")
            rows[key] = r
    want = {(s, p, i) for s, p in cells_needed for i in deals}
    missing = want - set(rows)
    if missing:
        stop(f"{path}: {len(missing)} deals of the line's cells are missing, e.g. {sorted(missing)[0]}")
    if exact and set(rows) != want:
        stop(f"{path}: {len(set(rows) - want)} rows outside the {len(cells_needed)} cells x deals "
             f"{deals.start}-{deals.stop - 1} the sample is")
    return {k: r for k, r in rows.items() if k in want}


def owner_counts(row, owner, card):
    """(turns offered, turns played) of `card` on the owner's side of one game."""
    seats = [s for s in (0, 1) if row["seat_decks"][s] == owner]
    if len(seats) != 1:
        stop(f"deal {(row['source'], row['pairing'], row['i'])}: {owner} is in {len(seats)} seats, not 1")
    c = row["counts"][seats[0]]["cards"].get(card, {})
    offered, played = c.get("offered", 0), c.get("played", 0)
    if not (isinstance(offered, int) and isinstance(played, int) and 0 <= played <= offered):
        stop(f"deal {(row['source'], row['pairing'], row['i'])}: {card} offered {offered}, played {played}")
    return offered, played


def rate(played, offered):
    # Reg (The rates): "R = (turns played, added up) / (turns offered, added up) ... kept as an exact fraction of the
    # two integer sums (Python's fractions.Fraction). If an arm's offered sum on the sample is 0, the line cannot pass."
    return Fraction(played, offered) if offered > 0 else None


def show_pct(x):
    """A fraction as a percentage to one decimal place, rounded half up from the exact value. Display only: no
    comparison ever uses it (Reg: "Rounding is for display only")."""
    if x is None:
        return "undefined (no offered turn)"
    tenths = math.floor(x * 1000 + Fraction(1, 2))
    return f"{tenths // 10}.{tenths % 10}%"


def show_frac(x):
    return "undefined" if x is None else f"{x.numerator}/{x.denominator}"


def frac_str(x):
    """An exact fraction as "numerator/denominator" in the record (never a float); None when undefined."""
    return None if x is None else f"{x.numerator}/{x.denominator}"


def paired_interval(units, seed):
    """Reg (the paired-noise calculation, frozen), steps 2 to 4. `units` holds, per cell in the fixed order, the
    list of its deals' units in increasing i; a unit is (kta3 offered, kta3 played, km3 offered, km3 played)."""
    # 2. Generator: "Each generator is created fresh for its line and used for nothing else."
    rng = random.Random(seed)
    diffs, zero = [], 0
    # 3. Replicates: "10,000, one after another. In each replicate, for each cell in the fixed order, 100 draws, each
    #    deals[rng.randrange(100)] from that cell's list of deals, each draw taking that unit's counts for both arms."
    for _ in range(REPLICATES):
        off_base = pl_base = off_km = pl_km = 0
        for deals in units:
            for _ in range(DRAWS_PER_CELL):
                u = deals[rng.randrange(100)]
                # "Each arm's played and offered counts are first added up over all the replicate's drawn units (a
                #  unit drawn twice counts twice)."
                off_base += u[0]
                pl_base += u[1]
                off_km += u[2]
                pl_km += u[3]
        # "The replicate's difference is then sum_played_km3 / sum_offered_km3 - sum_played_kta3 / sum_offered_kta3,
        #  in Python floats. A replicate in which either arm's offered sum is 0 has difference 0.0, and the number of
        #  such replicates is printed." (the arithmetic and its order are the frozen procedure's, unchanged)
        if off_km == 0 or off_base == 0:
            diffs.append(0.0)
            zero += 1
        else:
            diffs.append(pl_km / off_km - pl_base / off_base)
    # 4. Interval: "The 10,000 differences sorted ascending. The lower bound is element int(0.025 * 10000) = 250 and the
    #    upper bound element int(0.975 * 10000) = 9,750 (counting from 0), as score.py's pct takes them."
    diffs.sort()
    assert min(len(diffs) - 1, max(0, int(0.025 * len(diffs)))) == 250
    assert min(len(diffs) - 1, max(0, int(0.975 * len(diffs)))) == 9750
    return pct(diffs, 0.025), pct(diffs, 0.975), zero


def measure_line(spec, base_rows, km_rows):
    card, owner = spec["card"], spec["owner"]
    units, sums = [], {BASE: [0, 0], CAND: [0, 0]}
    for cell in spec["cells"]:
        a, b = CELL_DECKS[cell]
        if owner not in (a, b):
            stop(f"{cell} ({a} v {b}) does not hold {owner}")
        deals = []
        for i in SAMPLE_DEALS:  # "In each cell, the deals i = 200, 201, ..., 299, in increasing order."
            o0, p0 = owner_counts(base_rows[cell + (i,)], owner, card)
            o1, p1 = owner_counts(km_rows[cell + (i,)], owner, card)
            deals.append((o0, p0, o1, p1))
            sums[BASE][0] += o0
            sums[BASE][1] += p0
            sums[CAND][0] += o1
            sums[CAND][1] += p1
        assert len(deals) == DRAWS_PER_CELL
        units.append(deals)
    r_base = rate(sums[BASE][1], sums[BASE][0])
    r_km = rate(sums[CAND][1], sums[CAND][0])
    # Reg (The threshold: the exact midpoint; Amendment 1 (b) item 2): "T = (R_kta3 + R_km3) / 2, exact", kept as an
    # exact fraction and never rounded.
    t = (r_base + r_km) / 2 if r_base is not None and r_km is not None else None
    lo, hi, zero = paired_interval(units, spec["seed"])
    # Reg (5. Test): "The line can pass only if the lower bound is above zero. If it is zero or below, km3's development
    # rate doesn't exceed kta3's beyond paired noise, and the line cannot pass."
    if r_base is None or r_km is None:
        label = "cannot pass"
        reason = ("an arm's offered sum on the sample is 0 (Reg, The rates: \"If an arm's offered sum on the sample is 0, "
                  "the line cannot pass.\")")
    elif lo > 0.0:
        label = "threshold"
        reason = "the paired-noise interval's lower bound is above zero"
    else:
        label = "cannot pass"
        reason = (f"the paired-noise interval's lower bound is zero or below: {CAND}'s development rate doesn't exceed "
                  f"{BASE}'s beyond paired noise")
    return {
        "line": spec["line"], "card": card, "owner_side": owner,
        "cells": [f"{s}:{p}" for s, p in spec["cells"]], "deals": f"{SAMPLE_DEALS.start}-{SAMPLE_DEALS.stop - 1}",
        BASE: {"offered": sums[BASE][0], "played": sums[BASE][1], "rate": frac_str(r_base), "rate_display": show_pct(r_base)},
        CAND: {"offered": sums[CAND][0], "played": sums[CAND][1], "rate": frac_str(r_km), "rate_display": show_pct(r_km)},
        "T": frac_str(t), "T_display": show_pct(t),
        # The bounds as Python floats (JSON keeps a float's shortest repr, so they read back exactly) and as repr text.
        "interval": [lo, hi],
        "interval_detail": {"lower_repr": repr(lo), "upper_repr": repr(hi), "sorted_elements": [250, 9750],
                            "resampling_seed": spec["seed"], "replicates": REPLICATES, "zero_offered_replicates": zero},
        "status": label, "reason": reason,
    }


def text_of(record):
    out = [f"km's M1 and M2 thresholds: the development sample (REGISTRATION_DRAFT.md step 3, the threshold rule, "
           f"read with Amendment 1: {CAND} against {BASE})",
           f"km_thresholds.py sha256 {record['km_thresholds_py_sha256']}; Python {record['python']}",
           f"counter tool: source sha256 {record['counter_tool']['source_sha256']}, program sha256 "
           f"{record['counter_tool']['program_sha256']}"]
    for arm in (BASE, CAND):
        x = record["inputs"][arm]
        out.append(f"{arm} rows: {x['file']} ({x['rows']} rows, sha256 {x['sha256']})")
    out.append("Rates and T are exact fractions; the percentages are for display only (rounded half up to one "
               "decimal place) and no comparison uses them.")
    for ln in record["lines"].values():
        iv = ln["interval_detail"]
        undef = lambda s: "undefined" if s is None else s
        out += ["",
                f"{ln['line']}, {ln['card']} ({ln['owner_side']}'s side), deals {ln['deals']} of {len(ln['cells'])} cells: "
                f"{', '.join(ln['cells'])}",
                f"  {BASE}: played on {ln[BASE]['played']} of {ln[BASE]['offered']} offered turns = "
                f"{undef(ln[BASE]['rate'])} = {ln[BASE]['rate_display']}",
                f"  {CAND}:  played on {ln[CAND]['played']} of {ln[CAND]['offered']} offered turns = "
                f"{undef(ln[CAND]['rate'])} = {ln[CAND]['rate_display']}",
                f"  T, the exact midpoint (R_{BASE} + R_{CAND}) / 2 = {undef(ln['T'])} = {ln['T_display']}",
                f"  paired 95% interval of {CAND}'s rate minus {BASE}'s (random.Random({iv['resampling_seed']}), "
                f"{iv['replicates']:,} replicates, sorted elements 250 and 9750):",
                f"      lower {iv['lower_repr']}, upper {iv['upper_repr']}",
                f"      replicates with no offered turn in an arm (difference 0.0): {iv['zero_offered_replicates']}"]
        if ln["status"] == "threshold":
            out.append(f"  RESULT {ln['line']}: THRESHOLD T = {ln['T']} ({ln['T_display']} displayed); {ln['reason']}")
        else:
            out.append(f"  RESULT {ln['line']}: CANNOT PASS; {ln['reason']}. The midpoint above is recorded, not used, "
                       f"and not adjusted; no other sample is tried.")
    return "\n".join(out) + "\n"


def cmd_sample(a):
    needed = [c for spec in LINES for c in spec["cells"]]
    base = load_rows(a.kta3, a.base_code, SAMPLE_DEALS, needed, exact=True)
    km = load_rows(a.km3, a.cand_code, SAMPLE_DEALS, needed, exact=True)
    record = {
        "procedure": "REGISTRATION_DRAFT.md step 3, 'The threshold rule for T1 and T2' (registered Sept 29, 55e5d95), "
                     "read with Amendment 1 (Sept 30): km re-issued on kta, the sample kta3 then km3",
        "km_thresholds_py_sha256": sha256(os.path.abspath(__file__)),
        "python": sys.version.split()[0],
        "tool_source_sha256": a.tool_source_sha,
        "counter_tool": {"source_sha256": a.tool_source_sha, "program_sha256": a.tool_program_sha},
        "arms": [BASE, CAND],
        "kta3_arm_code": a.base_code,
        "km3_arm_code": a.cand_code,
        "inputs": {BASE: {"file": os.path.basename(a.kta3), "sha256": sha256(a.kta3), "rows": len(base)},
                   CAND: {"file": os.path.basename(a.km3), "sha256": sha256(a.km3), "rows": len(km)}},
        "lines": {spec["line"]: measure_line(spec, base, km) for spec in LINES},
    }
    text = text_of(record)
    for path, body in ((a.json, json.dumps(record, indent=1) + "\n"), (a.txt, text)):
        with open(path + ".part", "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        os.replace(path + ".part", path)
    print(text, end="")


def parse_frac(s):
    if s in (None, "undefined"):
        return None
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def cmd_gate(a):
    rec = json.load(open(a.thresholds, encoding="utf-8"))
    needed = [c for spec in LINES for c in spec["cells"]]
    base = load_rows(a.kta3, a.base_code, GATING_DEALS, needed, exact=False)
    km = load_rows(a.km3, a.cand_code, GATING_DEALS, needed, exact=False)
    print(f"km's M1 and M2 on the gating deals {GATING_DEALS.start}-{GATING_DEALS.stop - 1}, compared exactly with T "
          f"from {os.path.basename(a.thresholds)} (sha256 {sha256(a.thresholds)})")
    for spec in LINES:
        ln = rec["lines"][spec["line"]]
        s = {BASE: [0, 0], CAND: [0, 0]}
        for cell in spec["cells"]:
            for i in GATING_DEALS:
                for arm, rows in ((BASE, base), (CAND, km)):
                    o, p = owner_counts(rows[cell + (i,)], spec["owner"], spec["card"])
                    s[arm][0] += o
                    s[arm][1] += p
        r_base, r_km = rate(s[BASE][1], s[BASE][0]), rate(s[CAND][1], s[CAND][0])
        t = parse_frac(ln["T"])
        # Reg (M1, M2; Amendment 1 (b) item 2): "the line passes if km3's rate >= T", and "The guard reads kta3's own
        # rate on the gating deals against the same exact T": if it is already at or above T, "that line cannot show
        # the mechanism and reads 'not shown at this size'." "Cannot pass" is final (Reg, block item 5): the midpoint
        # is then not used.
        if ln["status"] != "threshold" or t is None:
            result = "CANNOT PASS (recorded at the sample; the midpoint is not used)"
        elif r_base is not None and r_base >= t:
            result = f"NOT SHOWN AT THIS SIZE (the guard: {BASE}'s own gating rate is at or above T)"
        elif r_km is not None and r_km >= t:
            result = f"PASSES ({CAND}'s gating rate is at or above T)"
        else:
            result = f"NOT SHOWN AT THIS SIZE ({CAND}'s gating rate is below T)"
        print(f"{spec['line']} {spec['card']}: {BASE} {s[BASE][1]}/{s[BASE][0]} = {show_frac(r_base)} "
              f"({show_pct(r_base)}); {CAND} {s[CAND][1]}/{s[CAND][0]} = {show_frac(r_km)} ({show_pct(r_km)}); "
              f"T = {show_frac(t)} ({ln['T_display']}): {result}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sample")
    p.add_argument("--kta3", required=True, help="the baseline arm's rows (kta3 on both sides)")
    p.add_argument("--km3", required=True, help="the candidate arm's rows (km3 on both sides)")
    p.add_argument("--json", required=True)
    p.add_argument("--txt", required=True)
    p.add_argument("--tool-source-sha", default="not given")
    p.add_argument("--tool-program-sha", default="not given")
    p.add_argument("--base-code", default=BASE, help="the code the kta3 arm's rows must be played by: kta3")
    p.add_argument("--cand-code", default=CAND, help="the code the km3 arm's rows must be played by: km3 (a smoke "
                   "with kta3 standing in passes kta3; the record names it)")
    p = sub.add_parser("gate")
    p.add_argument("--thresholds", required=True)
    p.add_argument("--kta3", required=True)
    p.add_argument("--km3", required=True)
    p.add_argument("--base-code", default=BASE)
    p.add_argument("--cand-code", default=CAND)
    a = ap.parse_args()
    {"sample": cmd_sample, "gate": cmd_gate}[a.cmd](a)


if __name__ == "__main__":
    main()
