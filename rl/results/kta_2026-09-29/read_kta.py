#!/usr/bin/env python3
"""kta's reading (REGISTRATION.md in this folder; registered Sept 29 with Dustin's word, commit 363b6b7). Written BLIND:
before any fresh kta game was played or read. It reads nothing until footprint.txt exists. It is read_kt.py (committed
b33a96c, reviewed twice, run unchanged on kt) adapted to this registration: one code, kta3, against kog3 only, on the
fresh deals of section 3.2 (23,000,000,000 - 23,009,999,999), with kog3's baselines re-run on those same deals by the
same binary (no development file serves as a baseline). The top block "Registration (Sept 29, Dustin's word)" governs.

The order (registration section 5):
  1. the footprint (5.1): kta3 on both sides of the 45 cells against kog3, paired by (a, b, i), on `moves`. The route is
     decided from the COUNTS (under 15%: the reserve route, 5.2; 15% or more: the ordinary rule, 5.3); the reading stops
     if footprint.txt's own route text disagrees. 1b: the preconditions (section 4): the programs' sha256 (read from
     disk here), identity_check.txt, the timing line, every scan page free of RULE findings. 1c (ordinary route only):
     the hashes, the pairs files (every game's seed) and the integrity line are checked before anything else is read.
  2. the 45 cells by score45.py (rules v2, kta3's mixed rows): the ΔMSE with RUN5's three-outcome label and its
     detectable size, on BOTH routes; the τ̂ margin (no harm only, 3.3); the rule-v2 vetoes. A ΔMSE bound near 0 at
     either edge, or a τ̂ bound near -1.0, is PENDING below --reps 20000 (5.4, "Near-zero bounds").
  3. clause (c): the mixed rows of the cells with a changed game, both directions; the other cells' i<40 sample.
  4. clause (d): the census Rayquaza list's 8 rows x 2,000 fresh deals per arm, pooled, with the per-row column (5.9).
  5. coverage (5.5): B2e (0-47 counted, 48-95 reported), the Scizor row, the four second lists; mixed rows only where
     kta3's both-sides games differ, by Dustin's rule, read against coverage_skip.txt, whose skips the reader re-checks.
     The held-out direction (RUN5), reported.
  6. the Dustin-deck A/B (5.6), reported; deck 07's Jasmine rate with the kog3 guard gates, in the fallback only (5.5).
  7. reported beside: Suicune, Rayquaza's real cells, Hydreigon's deck gap and the deck averages, the counters, traces.
  8. which condition carried the verdict (5.8); the verdict; the outcome section 6 fixes; what stays provisional.
Every input is checked for its full game count, its deals (the fresh seed formula, the decks, the seat rule "even i puts
the first-named deck in seat 0") and its pilots: a wrong file STOPS the reading, naming it. A file not in yet holds only
the clauses that need it (they read PENDING). Nothing is skipped silently.

INPUT CONTRACT (in --dir; P = --prefix, default ec7e1a8_fresh; the runner writes these, this script only reads them):
  footprint.txt      "FOOTPRINT kta3: <d> of 22500 paired games on the 45 cells differ from kog3's = <x.xx>% -> <reserve
                     route ...|ordinary adoption rule>"  (run_kt.sh's format)
  identity_check.txt "<label>: <n> of <n> equal on [...]" per replay (section 4.2 and 4.3: 7,920 games in all)
  P_timing_1.txt (P_timing_2.txt if the first pair was over)   "... (limit 1.25: within) ..."  (run_kt.sh's format)
  both sides, kog3 and kta3 (<c>):  P_<c>_table.jsonl (14,000; 23,000,000,000 + pairing x 10,000 + i)
                     P_<c>_new17.jsonl (8,500; pairings 8-24; 23,001,000,000 + ...)   P_scizor_<c>.jsonl (4,000; 0-7;
                     23,001,000,000 + ...)   P_b2e_<c>.jsonl (48,000; 23,002,000,000 + ...)   P_var_<list>_<c>.jsonl
                     (500 x rows; Lucario's, Suicune's, Weezing's second lists on 23,000,000,000 + table pairing x 10,000
                     + i; Charizard Y's on B2e pairings 40-47, 23,002,000,000 + ...)
  mixed rows (kta3 on one side, kog3 on the other; any number of files per glob, merged):
                     P_mixed_table_kta3_first*.jsonl, P_mixed_new17_kta3_first*.jsonl (kta3 on the first-named deck),
                     P_mixed_table_kta3_second*.jsonl, P_mixed_new17_kta3_second*.jsonl (kta3 on the second-named deck):
                     the cells with a changed game at 500 deals, the other cells at least i < 40 (5.2 (c)); on the
                     ordinary route every cell at 500 (5.3).
                     P_mixed_b2e_kta3_first*.jsonl; P_mixed_scizor_kta3_first*.jsonl (and _second*, reported only);
                     P_var_<list>_kta3_mixed_a*.jsonl / _mixed_b*.jsonl (kta3 on side a / side b rows): on the pairings
                     whose both-sides games differ, 500 deals each.
  coverage_skip.txt  the committed comparison (registration, top block 3): one line per coverage pairing,
                     "SKIP <group> <pairing>: <n> of <n> deals equal on moves, a, b, seed, first_seat" or
                     "RUN <group> <pairing>: <m> of <n> deals equal on ...", group b2e, scizor, var_<list> (table and
                     new17 lines are optional and are checked if present); other lines are ignored.
  clause (d):        P_d_kog3.jsonl (kog3 on both sides) and P_d_kta3.jsonl (kta3 on the Rayquaza list, kog3 on the
                     panel), 16,000 each: pairing = panel index 0-7 (altaria ... weezing), i < 2,000,
                     seed 23,003,000,000 + index x 10,000 + i
  the A/B:           P_ab_d<NN>_<kog3|kta3>.jsonl, decks 07 05 11 01 03, 1,920 each (kt_ab_play.py's rows),
                     seed 23,004,000,000 + 10,000 x deck + 1,000 x opponent index (+500 seat 1) + i, i < 120
  scan pages:        <file>.txt beside every legality_scan .jsonl (its "Findings" block); every *.txt with a Findings
                     block is scanned for RULE findings.
Reported only (missing ones hold nothing): P_census_<kog3|kta3>*.txt (tool_census's table; its "attack Stiffen" row is
read); the traces P_trace_rayquaza_<lucario|vespiquen>_<kta3|kog3>_pergame.jsonl (trace_pilot.py's per-game rows:
Scorching Interruption offered/used, wins) and _moves.jsonl (kta_trace_moves.py's rows, with per-ply `decisions`), 200
games per arm on seeds 23,005,000,000 (Lucario) / 23,005,001,000 (Vespiquen) + i, checked complete like the rest (a
wrong trace file STOPS); over the games whose moves differ, the first differing decision is tallied by kind (5.5).

Usage (WSL):  python3 read_kta.py --dir ../kta_tables_<date> > ../kta_tables_<date>/READING_numbers.txt
  --pages-dir DIR   where score45's page and its composite mixed-row inputs go (default: --dir)
  --reps N          score45's bootstrap (default 4000); the 20,000-rep rerun is what a near-the-line bound asks for
  --reuse-45        reuse score45's page only if made by the same command at the same --reps on inputs with the same
                    sha256 (a sidecar <page>.reps records them)
  --footprint-only  sections 1, 1b (and 1c) only: the step "footprint read and committed alone" (5.1)
  --engine-dir DIR  the ec7e1a8 programs (default /home/dacz8976/engine-kt-ec7e1a8/engine/target/release)
  --integrity-explained FILE  a human's written explanation of an integrity line (registration section 4: such a line
                    "holds the reading ... until it is explained"); printed in full, and the integrity lines then hold
                    nothing. Never needed for a clean reading.
  --parse-page F    parse one score45 page and stop (reads no kta file; a test aid)
  --selftest        the gate logic on canned numbers (reads no file) and stop
"""
import argparse, csv, glob, hashlib, json, math, os, re, subprocess, sys, textwrap
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)  # rl/results
REPO = os.path.dirname(os.path.dirname(RES))

ap = argparse.ArgumentParser(description="kta's reading (see the module docstring)")
ap.add_argument("--dir", default=None)
ap.add_argument("--prefix", default="ec7e1a8_fresh")
ap.add_argument("--pages-dir", default=None)
ap.add_argument("--reps", type=int, default=None)
ap.add_argument("--reuse-45", action="store_true")
ap.add_argument("--footprint-only", action="store_true")
ap.add_argument("--engine-dir", default="/home/dacz8976/engine-kt-ec7e1a8/engine/target/release")
ap.add_argument("--integrity-explained", default=None)
ap.add_argument("--parse-page", default=None)
ap.add_argument("--selftest", action="store_true")
args = ap.parse_args()

DEFAULT_REPS, DECISIVE_REPS = 4000, 20000
REPS = args.reps or DEFAULT_REPS
CODE, BASE = "kta3", "kog3"
FRESH_LO, FRESH_HI = 23_000_000_000, 23_009_999_999
SEED_TABLE, SEED_NEW, SEED_B2E, SEED_D, SEED_AB = 23_000_000_000, 23_001_000_000, 23_002_000_000, 23_003_000_000, 23_004_000_000
D_DEALS, D_OPP = 2000, ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
D_LIST = "rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt"
AB_DECKS, AB_GAMES = ("07", "05", "11", "01", "03"), 1920
SAMPLE_I = 40            # 5.2 (c): the zero-footprint cells' integrity sample, i < 40, both directions
IDENTITY_GAMES = 7920    # 4.2 (7,440) + 4.3 (480)
PROGRAMS = {  # section 4: name -> (path under --engine-dir, sha256, gates)
    "deckgym": ("deckgym", "407976366fa2104ee1f2663c94fe31b1c503466defe9d6154b7e60659cb0991c", True),
    "legality_scan": ("examples/legality_scan", "924751ba0926993eaee87ecc8fb8301ffd0b7eee8490bfb3369427794328f938", True),
    "tool_census": ("examples/tool_census", "d9799c96015f74b952889a7f7d9820bbc12d5d97e4d267ad8acc2b63cdcc720b", False),
}
VARS = ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy")
# Section 2's reach lists (the only places switch 1 can act): the 45 cells with Suicune's or Rayquaza's list (17 cells);
# B2e pairings against the panel's Suicune (4, 12, ..., 92); every Scizor row; the second lists' rows against Suicune.
REACH_DECKS = ("suicune", "rayquaza")
REACH_B2E = frozenset(p for p in range(96) if p % 8 == 4)
REACH_VAR = {"v-lucario_2": {19}, "v-suicune_2": set(), "v-weezing_2": {26}, "l-charizardy": {44}}
P = print


def die(msg):
    sys.exit("STOP: " + msg)


# ---------------------------------------------------------------------------------------------------------------
# Pure logic (no file is read here; --selftest exercises it).
# ---------------------------------------------------------------------------------------------------------------
def route_of(d, n):
    """Under 15% (100 d < 15 n) is 'reserve'; 15% or more is 'ordinary'. From the integers, never a rounded printout."""
    return "reserve" if 100 * d < 15 * n else "ordinary"


def tau_gate(lo, ev_lo, reps):
    """(b)'s "τ̂ margin 90% lower bound at -1.0 or above" (read_kt.py's). -1.00 as printed is never called; within 0.10
    of the line below DECISIVE_REPS is PENDING (N9). The bound is printed to two decimals, so the test is done in whole
    hundredths of the printout and is inclusive: a printed -1.10 or -0.90 is within 0.10 (its true value may be as close
    as 0.095), never decided by float rounding. Returns (status, notes)."""
    notes, n = [], round(lo * 100)
    gap = abs(n + 100)                     # hundredths of a point from the -1.0 line, as printed
    status = "PASS" if n >= -100 else "FAIL"
    if gap == 0:
        status = "PENDING"
        notes.append("BOUNDARY: printed -1.00, so the true bound is within +/-0.005 of the registered line; not called, "
                     "read it by hand at more digits (N9)")
    elif gap <= 10:
        if reps < DECISIVE_REPS:
            status = "PENDING"
            notes.append(f"MC-BOUNDARY: within 0.10 of the -1.0 line at --reps {reps}; rerun the reader with --reps "
                         f"{DECISIVE_REPS}, and that run decides (5.4, near-zero bounds)")
        else:
            notes.append(f"near the -1.0 line; this --reps {reps} run is the decisive one (5.4)")
    if (ev_lo >= -1.0) != (lo >= -1.0):
        notes.append(("by-event lower bound %+.2f is BELOW -1.0 while the match-level bound is not" if lo >= -1.0 else
                      "by-event lower bound %+.2f is at or above -1.0 while the match-level bound is below it") % ev_lo
                     + " (beside, gates nothing)")
    return status, notes


def dmse_label(lo_s, hi_s, below0, reps, exact_zero=False):
    """RUN5's three outcomes for ΔMSE (kta3 minus kog3): 'below' (wholly below zero: the accuracy clause passes),
    'above' (wholly above zero: fails, no fallback), 'spans' (inconclusive at this size: the fallback). Returns
    (possible labels, the label as printed, notes). More than one possible label means the label is PENDING.
      - The upper edge is decided by score.py's own 'below 0', which compares the unrounded bound.
      - The lower edge exists only as printed (one decimal): a printed '+0.0' may be exactly 0 (spans) or up to +0.049
        (above), so it is never called from the page.
      - A bound within 5% of the interval's width of 0 is PENDING below --reps 20000, at either edge (5.4); the 20,000-rep
        rerun decides. The test is done in whole units of the printout's last digit and is inclusive (20 x |bound| <=
        width), so a bound at exactly 5% of the width (-1.9 to +0.1) is near, never decided by float rounding.
      - exact_zero: no game on the 45 cells changed its result, so every bootstrap draw is exactly 0 and the interval is
        the single point 0: it spans zero."""
    lo, hi = float(lo_s), float(hi_s)
    if exact_zero:
        if lo != 0 or hi != 0:
            die(f"no result changed on the 45 cells, but score45's ΔMSE interval is {lo_s} to {hi_s}, not 0 to 0")
        return {"spans"}, "spans", ["no game on the 45 cells changed its result: every bootstrap draw of ΔMSE is exactly 0, "
                                    "so the interval is the point 0, which spans zero"]
    if below0 and hi > 0:
        die(f"score45 says the ΔMSE interval is below 0 but prints its upper bound as {hi_s} (format changed?)")
    if not below0 and hi < 0:
        die(f"score45 says the ΔMSE interval is not below 0 but prints its upper bound as {hi_s} (format changed?)")
    if lo > hi:
        die(f"score45's ΔMSE interval {lo_s} to {hi_s} has its bounds reversed")
    base = "below" if below0 else ("above" if lo > 0 else "spans")
    dec = max((len(s.split(".")[1]) if "." in s else 0) for s in (lo_s, hi_s))   # the printout's digits (one decimal today)
    lo_u, hi_u = round(lo * 10 ** dec), round(hi * 10 ** dec)                    # the bounds in whole units of the last digit
    labels, notes, w_u = {base}, [], hi_u - lo_u
    if w_u > 0 and 20 * abs(hi_u) <= w_u:
        if reps < DECISIVE_REPS:
            labels |= {"below", "spans"}
            notes.append(f"MC-BOUNDARY (upper edge): {hi_s} is within 5% of the interval's width of 0 at --reps {reps}; it "
                         f"decides whether outcome 1 (wholly below zero) applies: rerun with --reps {DECISIVE_REPS}, and that run decides")
        else:
            notes.append(f"the upper bound is near 0; this --reps {reps} run is the decisive one")
    if w_u > 0 and 20 * abs(lo_u) <= w_u:
        if reps < DECISIVE_REPS:
            labels |= {"spans", "above"}
            notes.append(f"MC-BOUNDARY (lower edge): {lo_s} is within 5% of the interval's width of 0 at --reps {reps}; it "
                         f"decides whether outcome 2 (wholly above zero, fails with no fallback) applies: rerun with --reps "
                         f"{DECISIVE_REPS}, and that run decides")
        else:
            notes.append(f"the lower bound is near 0; this --reps {reps} run is the decisive one")
    if lo_s == "+0.0":
        labels |= {"spans", "above"}
        notes.append("BOUNDARY: the lower bound prints as +0.0 (true value 0 to +0.049): whether the interval is wholly above "
                     "zero cannot be read from the page; read it at more digits")
    return labels, base, notes


LABEL_TEXT = {"below": "wholly BELOW zero (outcome 1: demonstrated on the simulator side; the accuracy clause passes)",
              "above": "wholly ABOVE zero (outcome 2: demonstrated worsening; fails on accuracy with no fallback)",
              "spans": "SPANS zero (outcome 3: inconclusive at this size; the fallback)"}


def jas_gate(k_off, k_pl, g_off, g_pl):
    """5.5: kta3 plays Jasmine on at least 20% of the turns she is offered on deck 07 (pooled over its 1,920 games), and
    the guard: if kog3's own rate on the same deals already reaches 20%, the footprint test counts as not passed. Integers
    decide (a rate reaches 20% when 5 x played >= offered). Returns (status, text)."""
    reach = lambda off, pl: off > 0 and 5 * pl >= off  # noqa: E731
    k_txt = f"kta3 {k_pl:,} of {k_off:,}" + (f" = {100 * k_pl / k_off:.2f}%" if k_off else " (never offered)")
    g_txt = f"kog3 {g_pl:,} of {g_off:,}" + (f" = {100 * g_pl / g_off:.2f}%" if g_off else " (never offered)")
    if reach(g_off, g_pl):
        return "FAIL", (f"GUARD: kog3's own rate on the same fresh deals already reaches 20% ({g_txt}; {k_txt}): the line "
                        f"cannot show the mechanism, 'not shown at this size', so the footprint test is not passed")
    if k_off == 0:
        return "FAIL", f"kta3 was never offered Jasmine on deck 07 ({k_txt}; {g_txt}): the rate cannot reach 20%, 'not shown at this size'"
    if reach(k_off, k_pl):
        return "PASS", f"{k_txt} reaches 20%; guard: {g_txt}, below 20%"
    return "FAIL", f"{k_txt} is below 20% ({g_txt}): 'mechanism not shown at this size'"


def d_shares(means):
    """5.9: each row's share of the pooled sum (row mean / sum of row means); None when the sum is not positive."""
    s = sum(means)
    return None if s <= 0 else [m / s for m in means]


# Which gate applies under which ΔMSE label (sections 5.2-5.5 and 6): with 'above' kta3 fails on accuracy whatever else
# says; the Jasmine threshold gates only when the interval spans zero (the fallback); every other test gates on every
# label that does not fail on accuracy (5.2: "(b), (c), coverage and (d) gate on every outcome that doesn't fail on
# accuracy"; 5.3 and section 6 for the ordinary rule, K11).
CATEGORY = {"b1": "harm", "b2": "harm", "c": "harm", "cov_b2e": "coverage", "cov_scz": "coverage", "cov_lst": "coverage",
            "d": "gain", "jas": "mechanism"}


def applies(gid, label):
    return label == "spans" if gid == "jas" else label != "above"


HOLDING = ("scan",)   # besides the integrity lines: a file read without its scan page (4.5) holds the reading too


def holding_lines(gates):
    """The open lines that hold the reading whatever the ΔMSE label: an integrity line (section 4: it 'holds the reading
    (status PENDING, never a registered fail) until it is explained') and a missing scan page (4.5: a RULE finding would
    stop the reading, so a page not in yet leaves the games unchecked). They are read before anything that decides."""
    return [g for g in gates if g[2] == "PENDING" and (g[4] == "integrity" or g[0] in HOLDING)]


def decide(gates, label):
    """gates: [(gid, text, status, detail, kind)], kind 'gate' or 'integrity'. Returns (result, [the deciding gates]);
    result HOLD / FAIL / PENDING / PASS. A holding line is checked first, before the 'above' shortcut and before any
    FAIL: while one is open no verdict is recorded, not even NOT ADOPTED (the games might not be kta3's)."""
    h = holding_lines(gates)
    if h:
        return "HOLD", h
    if label == "above":
        return "FAIL", [("acc", "ΔMSE (kta3 minus kog3) wholly above zero", "FAIL",
                         "accuracy-worsening: fails on accuracy with no fallback, whatever (b) to (d) say", "gate")]
    gs = [g for g in gates if applies(g[0], label)]
    fails = [g for g in gs if g[2] == "FAIL"]
    if fails:
        return "FAIL", fails
    pend = [g for g in gs if g[2] == "PENDING"]
    if pend:
        return "PENDING", pend
    return "PASS", []


def overall(gates, labels):
    """(the verdict, {label: decide()}). HELD while a holding line is open (on every label alike); the verdict the other
    lines would give once it is explained is overall() of the gates without the holding lines."""
    res = {L: decide(gates, L) for L in sorted(labels)}
    kinds = {r[0] for r in res.values()}
    if "HOLD" in kinds:
        return "HELD", res
    if kinds == {"FAIL"}:
        return "NOT ADOPTED", res
    if kinds == {"PASS"}:
        return "ADOPTED", res
    return "PENDING", res


def once_explained(gates, labels):
    """What the other lines give once every holding line is explained (or its scan page is in)."""
    h = holding_lines(gates)
    return overall([g for g in gates if g not in h], labels)


def fail_names(bylab):
    """{label: [the failure names, in the registration's words]} for every label whose result is FAIL."""
    out = {}
    for L, (res, gs) in bylab.items():
        if res == "FAIL":
            out[L] = list(dict.fromkeys("accuracy-worsening" if g[0] == "acc" else CATEGORY.get(g[0], g[0]) for g in gs))
    return out


def verdict_words(result, bylab, labels):
    """A one-line verdict: 'ADOPTED', 'NOT ADOPTED (harm, coverage)', with one label; with several open labels the names
    under each ('[spans] gain; [above] accuracy-worsening'), since the rerun decides which is recorded."""
    if result != "NOT ADOPTED":
        return result
    fn = fail_names(bylab)
    if len(labels) == 1:
        return f"NOT ADOPTED ({', '.join(fn[next(iter(labels))])})"
    return ("NOT ADOPTED (settled under every open label; the name waits for the rerun: "
            + "; ".join(f"[{L}] {', '.join(fn[L])}" for L in sorted(labels)) + ")")


SKIP_RE = re.compile(r"^(SKIP|RUN) (\S+) (\d+): (\d+) of (\d+) deals equal\b")


def parse_skip_report(text):
    """coverage_skip.txt -> {group: {pairing: (verdict, equal, deals)}}. A line starting SKIP or RUN must match the
    format (else STOP: the format changed); other lines (headers, notes) are ignored."""
    out = defaultdict(dict)
    for ln in text.splitlines():
        if not ln.startswith(("SKIP", "RUN")):
            continue
        m = SKIP_RE.match(ln)
        if not m:
            die(f"coverage_skip.txt line not in the documented format: {ln!r}")
        g, p = m.group(2), int(m.group(3))
        if p in out[g]:
            die(f"coverage_skip.txt names {g} pairing {p} twice")
        out[g][p] = (m.group(1), int(m.group(4)), int(m.group(5)))
    return out


FIVE = ("moves", "a", "b", "seed", "first_seat")


def equal5(r, s):
    """Dustin's rule: the complete move fingerprint, both decks (with the deck files where both records carry them), the
    seed and the seats. Matching winners alone is not enough."""
    if any(r.get(k) != s.get(k) for k in FIVE) or not r.get("moves"):
        return False
    return all(r[k] == s[k] for k in ("a_file", "b_file") if k in r and k in s)


def mv(d):
    n = len(d)
    m = sum(d) / n
    return m, sum((x - m) ** 2 for x in d) / max(n - 1, 1) / n


def pool(parts):
    """Stratified pool over rows (score.py side_change): (mean of row means, 95% half-width, deals)."""
    q = [mv(d) for d in parts]
    return sum(m for m, _ in q) / len(q), 1.96 * math.sqrt(sum(v for _, v in q)) / len(q), sum(len(d) for d in parts)


def fmt(m, h):
    return f"{m:+.2f} +/- {h:.2f}"


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(min(b, c) + 1)) / 2 ** n)


NUM = r"([+-][\d.]+)"


def _summary_entries(s, what):
    s = s.split(" [INDICATIVE")[0].strip()
    if s == "none":
        return []
    out = []
    for e in s.split(", "):
        m = re.match(r"^(?:(\S+) v (\S+)|(\S+)) \+([\d.]+)$", e.strip())
        if not m:
            die(f"score45.py's {what} summary entry {e!r} is not in the format read (format changed?)")
        out.append((f"{m.group(1)} v {m.group(2)}" if m.group(1) else m.group(3), float(m.group(4))))
    return sorted(out)


def parse45(text, lenient=False):
    """read_kt.py's parser, with the ΔMSE bounds kept as printed (the lower edge is read from its printout)."""
    blocks, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r"== (all cells|decision set)[^:]*: (\d+) pairings", ln)
        if m:
            cur = "all" if m.group(1) == "all cells" else "dec"
            blocks[cur] = {"n": int(m.group(2)), "lines": []}
            continue
        if ln.startswith("Per cell") or ln.startswith("Mixed rows"):
            cur = None
        if cur:
            blocks[cur]["lines"].append(ln)
    if blocks.get("all", {}).get("n") != 45 or blocks.get("dec", {}).get("n") != 44:
        die("score45.py's page does not have the 45-cell and 44-cell blocks (format changed?)")
    out = {}
    for name, b in blocks.items():
        d = {"real": {}, "veto": [], "verdict": None, "deck_avg": {}}
        for ln in b["lines"]:
            m = re.match(r"\s*(\S+): real error\s+([\d.]+) \|", ln)
            if m:
                d["real"][m.group(1)] = float(m.group(2))
                continue
            m = re.match(rf"\s*dMSE new - current: {NUM} points\^2, 95% interval {NUM} to {NUM} \((not below 0|below 0)\)", ln)
            if m:
                d["dmse"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4) == "below 0", m.group(2), m.group(3))
                continue
            m = re.match(rf"\s*dMSE, Limitless side resampled by event: 95% interval {NUM} to {NUM} \((not below 0|below 0)", ln)
            if m:
                d["dmse_ev"] = (float(m.group(1)), float(m.group(2)), m.group(3) == "below 0")
                continue
            m = re.match(rf"\s*real error, current minus new: {NUM} points, 90% interval {NUM} to {NUM}", ln)
            if m:
                d["tau"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                continue
            m = re.match(rf"\s*real error, Limitless side resampled by event: 90% interval {NUM} to {NUM}", ln)
            if m:
                d["tau_ev"] = (float(m.group(1)), float(m.group(2)))
                continue
            m = re.match(r"\s*cell veto \(miss grows > 6\): (.*)$", ln)
            if m:
                d["sum_cell"] = _summary_entries(m.group(1), "cell veto")
                continue
            m = re.match(r"\s*deck veto \(gap grows > 2\): (.*)$", ln)
            if m:
                d["sum_deck"] = _summary_entries(m.group(1), "deck veto")
                continue
            m = re.match(r"^\s{4}(deck )?(\S+?)(?: v (\S+))? \+([\d.]+): (COUNTS|AWAITS|never counts|investigation item)(.*)$", ln)
            if m:
                who = ("deck " + m.group(2)) if m.group(1) else f"{m.group(2)} v {m.group(3)}"
                d["veto"].append((who, float(m.group(4)), m.group(5), (m.group(5) + m.group(6)).strip()))
                continue
            m = re.match(r"^\s+(\w+):\s+([\d.]+)\s*/\s*([\d.]+)\s*/\s*([\d.]+)\s+([+-][\d.]+)\s*$", ln)
            if m:
                d["deck_avg"][m.group(1)] = tuple(float(m.group(i)) for i in range(2, 6))
                continue
            m = re.match(r"\s*ADOPTION RULE \(v2\): (.*?)(?: \(held-out-deck veto checked separately\))?$", ln)
            if m:
                d["verdict"] = m.group(1)
        if lenient:
            d.setdefault("dmse_ev", (0.0, 0.0, False))
            d.setdefault("tau_ev", (0.0, 0.0))
        for key in ("dmse", "dmse_ev", "tau", "tau_ev", "verdict", "sum_cell", "sum_deck"):
            if key not in d or d[key] is None:
                die(f"score45.py's {name} block has no '{key}' line (format changed?)")
        if not d["deck_avg"]:
            die(f"score45.py's {name} block has no 'Deck averages' rows (format changed?)")
        d["counts"] = [v for v in d["veto"] if v[2] == "COUNTS"]
        d["awaits"] = [v for v in d["veto"] if v[2] == "AWAITS"]
        got_cell = sorted((v[0], v[1]) for v in d["veto"] if not v[0].startswith("deck "))
        got_deck = sorted((v[0][5:], v[1]) for v in d["veto"] if v[0].startswith("deck "))
        if got_cell != d["sum_cell"] or got_deck != d["sum_deck"]:
            die(f"score45.py's {name} block: its summary lines list {len(d['sum_cell'])} cell vetoes and {len(d['sum_deck'])} deck "
                f"vetoes, the veto lines read give {len(got_cell)} and {len(got_deck)} (or different ones): the parse missed "
                f"or invented a veto line (format changed?). Nothing is read.")
        derived = d["dmse"][3] and not d["counts"] and not d["awaits"]
        if d["verdict"].startswith("adopt") != derived:
            die(f"score45.py's verdict ({d['verdict']!r}) disagrees with its own numbers in the {name} block")
        out[name] = d
    return out


def selftest():
    assert route_of(3374, 22500) == "reserve" and route_of(3375, 22500) == "ordinary" and route_of(0, 22500) == "reserve"
    assert f"{100 * 3374 / 22500:.2f}" == "15.00"  # why the integers decide
    T = tau_gate
    assert T(-1.00, -1.5, 4000)[0] == "PENDING" and T(-1.00, -1.0, 20000)[0] == "PENDING"
    assert T(-0.95, -0.9, 4000)[0] == "PENDING" and T(-1.05, -1.2, 4000)[0] == "PENDING"
    assert T(-0.95, -0.9, 20000)[0] == "PASS" and T(-1.05, -1.2, 20000)[0] == "FAIL"
    assert T(-0.85, -0.9, 4000)[0] == "PASS" and T(-1.20, -1.3, 4000)[0] == "FAIL"
    assert T(-1.10, -1.2, 4000)[0] == "PENDING" and T(-0.90, -0.9, 4000)[0] == "PENDING"   # exactly 0.10 as printed: within
    assert T(-1.10, -1.2, 20000)[0] == "FAIL" and T(-0.90, -0.9, 20000)[0] == "PASS"
    assert T(-1.11, -1.2, 4000)[0] == "FAIL" and T(-0.89, -0.9, 4000)[0] == "PASS"         # 0.11: outside, called
    L = lambda lo, hi, reps=4000, ez=False: dmse_label(lo, hi, float(hi) < 0, reps, ez)[0]  # noqa: E731
    assert L("-1.9", "+0.1") == {"below", "spans"} and L("-0.1", "+1.9") == {"spans", "above"}   # exactly 5% of the width
    assert L("-2.0", "+0.1") == {"below", "spans"} and L("-1.8", "+0.1") == {"spans"}           # under 5% / over 5%
    assert L("-2.1", "-0.1") == {"below", "spans"} and L("-2.0", "-0.1") == {"below"}           # 0.1 of 2.0 / of 1.9
    assert L("+0.1", "+2.1") == {"spans", "above"} and L("+0.1", "+2.0") == {"above"}
    assert L("-11.0", "-1.4") == {"below"} and L("+2.0", "+9.0") == {"above"} and L("-4.0", "+6.0") == {"spans"}
    assert L("-20.0", "-0.4") == {"below", "spans"} and L("-20.0", "-0.4", 20000) == {"below"}      # upper edge near 0
    assert L("-20.0", "+0.4") == {"below", "spans"} and L("-20.0", "+0.4", 20000) == {"spans"}
    assert L("+0.4", "+20.0") == {"spans", "above"} and L("+0.4", "+20.0", 20000) == {"above"}      # lower edge near 0
    assert L("-0.4", "+20.0") == {"spans", "above"} and L("-0.4", "+20.0", 20000) == {"spans"}
    assert L("+0.0", "+0.9", 20000) == {"spans", "above"}           # printed +0.0 is never called, whatever --reps
    assert L("-0.0", "+0.9", 20000) == {"spans"}                    # printed -0.0: the true bound is below zero
    assert L("+0.0", "+0.0", 100, True) == {"spans"}                # no result changed: the point 0, which spans
    assert L("-3.0", "+3.0", 100) == {"spans"}                      # 3.0 is not within 5% of 6.0 of 0
    J = jas_gate
    assert J(5669, 1711, 8597, 36)[0] == "PASS"                     # development: 30.2% against 0.4%
    assert J(5000, 1000, 8000, 30)[0] == "PASS" and J(5000, 999, 8000, 30)[0] == "FAIL"   # exactly 20% reaches it
    assert J(5669, 1711, 1000, 200)[0] == "FAIL" and "GUARD" in J(5669, 1711, 1000, 200)[1]  # kog3 at exactly 20%: guard
    assert J(5669, 1711, 1000, 199)[0] == "PASS" and J(0, 0, 8597, 36)[0] == "FAIL"
    assert d_shares([1.0, 3.0]) == [0.25, 0.75] and d_shares([-1.0, 1.0]) is None
    g = lambda gid, st, kind="gate": (gid, gid, st, "", kind)  # noqa: E731
    ok = [g(x, "PASS") for x in ("b1", "b2", "c", "d", "cov_b2e", "cov_scz", "cov_lst")]
    assert overall(ok + [g("jas", "FAIL")], {"below"})[0] == "ADOPTED"          # Jasmine reported only when below
    assert overall(ok + [g("jas", "FAIL")], {"spans"})[0] == "NOT ADOPTED"      # ... and gates in the fallback
    assert overall(ok + [g("jas", "PASS")], {"spans"})[0] == "ADOPTED"
    assert overall(ok + [g("jas", "PASS")], {"above"})[0] == "NOT ADOPTED"      # no fallback, whatever else says
    assert overall(ok + [g("jas", "FAIL")], {"below", "spans"})[0] == "PENDING" # the rerun decides
    assert overall(ok + [g("jas", "PASS")], {"spans", "above"})[0] == "PENDING"
    assert overall([g("d", "FAIL")] + ok[:2] + [g("jas", "PASS")], {"spans", "above"})[0] == "NOT ADOPTED"  # settled either way
    assert overall(ok + [g("jas", "PENDING")], {"below"})[0] == "ADOPTED"       # a missing A/B holds only the fallback
    assert overall(ok + [g("int_reach", "PENDING", "integrity")], {"below"})[0] == "HELD"
    # an open integrity line or a missing scan page holds the reading before any FAIL and before the 'above' shortcut;
    # the verdict once explained is printed beside
    held = ok + [g("int_reach", "PENDING", "integrity"), g("c", "FAIL")]
    assert overall(held, {"below"})[0] == "HELD" and once_explained(held, {"below"})[0] == "NOT ADOPTED"
    assert verdict_words(*once_explained(held, {"below"}), {"below"}) == "NOT ADOPTED (harm)"
    assert overall(ok + [g("jas", "PASS"), g("int_reach", "PENDING", "integrity")], {"above"})[0] == "HELD"
    assert overall(ok + [g("scan", "PENDING"), g("d", "FAIL")], {"spans"})[0] == "HELD"
    assert overall(ok + [g("jas", "PASS"), g("scan", "PENDING")], {"below", "spans"})[0] == "HELD"
    assert once_explained(ok + [g("jas", "PASS"), g("scan", "PENDING")], {"below", "spans"})[0] == "ADOPTED"
    assert overall(ok + [g("int", "PASS", "integrity"), g("scan", "PASS")], {"below"})[0] == "ADOPTED"
    # NOT ADOPTED under more than one open label: the names stay per label until the rerun decides which is recorded
    two = [g("d", "FAIL")] + ok[:2] + [g("jas", "PASS")]
    r2 = overall(two, {"spans", "above"})
    assert fail_names(r2[1]) == {"above": ["accuracy-worsening"], "spans": ["gain"]}
    assert verdict_words(*r2, {"spans", "above"}).endswith("[above] accuracy-worsening; [spans] gain)")
    rep = parse_skip_report("coverage_skip v1\nSKIP b2e 0: 500 of 500 deals equal on moves, a, b, seed, first_seat\n"
                            "RUN b2e 4: 497 of 500 deals equal on moves, a, b, seed, first_seat\n")
    assert rep["b2e"] == {0: ("SKIP", 500, 500), 4: ("RUN", 497, 500)}
    r = {"moves": "ab", "a": "x", "b": "y", "seed": 1, "first_seat": 0, "first_deck_score": 1.0}
    assert equal5(r, dict(r)) and not equal5(r, {**r, "first_seat": 1}) and not equal5(r, {**r, "moves": "ac"})
    assert not equal5(r, {**r, "b": "z"}) and not equal5(r, {**r, "seed": 2})
    assert not equal5(r, {**r, "moves": "ac", "first_deck_score": 1.0})       # the same winner is not enough
    page = """== all cells: 45 pairings
  dMSE new - current: -1.0 points^2, 95% interval -2.0 to +1.0 (not below 0) [Limitless side binomial]
  dMSE, Limitless side resampled by event: 95% interval -2.0 to +1.0 (not below 0; 0 of 4000 event draws redrawn because a cell had no match)
  real error, current minus new: +0.10 points, 90% interval -0.10 to +0.30 (margin rule)
  real error, Limitless side resampled by event: 90% interval -0.10 to +0.30
  cell veto (miss grows > 6): a v b +7.0, c_d v e +8.5
  deck veto (gap grows > 2): x +3.1
    a v b +7.0: COUNTS: kta3 pilots a worse (a's side -9.0 +/- 3.0; b's side +1.0 +/- 3.0)
    c_d v e +8.5: investigation item: neither side worse (c_d's side +1.0 +/- 3.0; e's side +1.0 +/- 3.0)
    deck x +3.1: AWAITS mixed rows: 3 of 18 cell sides missing
  ADOPTION RULE (v2): do not adopt (dMSE interval not below 0) (held-out-deck veto checked separately)
  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
    hydreigon:  51.2 /  54.9 /  43.9   +3.7
== decision set (Altaria v Sceptile quarantined): 44 pairings
  dMSE new - current: -1.0 points^2, 95% interval -2.0 to +1.0 (not below 0) [Limitless side binomial]
  dMSE, Limitless side resampled by event: 95% interval -2.0 to +1.0 (not below 0; 0 of 4000 event draws redrawn)
  real error, current minus new: +0.10 points, 90% interval -0.10 to +0.30 (margin rule)
  real error, Limitless side resampled by event: 90% interval -0.10 to +0.30
  cell veto (miss grows > 6): none
  deck veto (gap grows > 2): none
  ADOPTION RULE (v2): do not adopt (dMSE interval not below 0) (held-out-deck veto checked separately)
  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
    hydreigon:  51.2 /  54.9 /  43.9   +3.7
"""
    r45 = parse45(page)
    assert [v[2] for v in r45["all"]["veto"]] == ["COUNTS", "investigation item", "AWAITS"] and r45["dec"]["veto"] == []
    assert r45["all"]["dmse"][4:] == ("-2.0", "+1.0")
    for bad in (page.replace("    deck x +3.1: AWAITS mixed rows: 3 of 18 cell sides missing\n", ""),
                page.replace("COUNTS:", "COUNTED:"),
                page.replace("deck veto (gap grows > 2): x +3.1", "deck veto (gap grows > 2): x +3.1, y +4.0")):
        try:
            parse45(bad)
        except SystemExit as e:
            assert "STOP" in str(e.code)
        else:
            raise AssertionError("parse45 accepted a page whose veto lines and summary lines disagree")
    print("selftest ok: route from integers; tau and dMSE boundary logic at both edges (+0.0, exact zero, --reps, exactly "
          "0.10 / 5% as printed); the Jasmine threshold and guard in integers; the gating table by label; holding lines "
          "before any FAIL or 'above'; per-label failure names; the skip report; the five-field match; the veto-line backstop")


if args.selftest:
    selftest()
    sys.exit(0)
if args.parse_page:
    _r = parse45(open(args.parse_page, encoding="utf-8").read(), lenient=True)
    for _nm, _d in _r.items():
        P(f"PARSED {_nm}: dMSE {_d['dmse'][4]} to {_d['dmse'][5]} ({'below 0' if _d['dmse'][3] else 'not below 0'}), "
          f"cell vetoes {len(_d['sum_cell'])}, deck vetoes {len(_d['sum_deck'])}, COUNTS {len(_d['counts'])}, "
          f"AWAITS {len(_d['awaits'])}, verdict {_d['verdict']!r}")
    sys.exit(0)
if not args.dir:
    die("pass --dir, the kta tables folder (the runner's output)")

DIR, PX = os.path.abspath(args.dir), args.prefix
PAGES = os.path.abspath(args.pages_dir or DIR)
K45 = os.path.join(RES, "kpf_2026-09-26", "reading")
TSV = os.path.join(RES, "gauntlet_runs_2026-09-26", "tsv")
B2E_DIR = os.path.join(RES, "b2e_card_check_2026-09-26")
DEVKOG = os.path.join(RES, "kog_composition_2026-09-27")


def path(name):
    return os.path.join(DIR, name)


GATES = []           # (gid, text, status, detail, kind)
SCANNED = []         # legality_scan outputs read: their .txt page must exist
REPORTED_MISSING = []


def gate(gid, text, status, detail, kind="gate"):
    GATES.append((gid, text, status, detail, kind))


def have(name, holds):
    """The path of a file if it is in; otherwise None, printed as not in yet with what it holds."""
    p = path(name)
    if os.path.exists(p):
        return p
    P(f"   not in yet: {name} ({holds})")
    if holds.startswith("reported"):
        REPORTED_MISSING.append(name)
    return None


# ---------------------------------------------------------------------------------------------------------------
# Loading, with the completeness guards: the full game count, no repeated deal, the pilots named, every game on its fresh
# deal (the seed formula of section 3.2), the seat rule, the decks of its pairs file.
# ---------------------------------------------------------------------------------------------------------------
KEEP = ("a", "b", "a_file", "b_file", "bot_a", "bot_b", "i", "pairing", "seed", "moves", "first_deck_score", "first_seat")
NEEDED = ("a", "b", "bot_a", "bot_b", "i", "pairing", "seed", "moves", "first_deck_score", "first_seat")


def read_games(p, mode):
    rows = {}
    with open(p, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            miss = [k for k in NEEDED if k not in g]
            if miss:
                die(f"{p}: a game has no {miss} field(s)")
            key = (g["a"], g["b"], g["i"]) if mode == "abi" else (g["pairing"], g["i"])
            if key in rows:
                die(f"{p}: game {key} appears twice")
            if not g["moves"]:
                die(f"{p}: game {key} has an empty move fingerprint")
            rows[key] = {k: g[k] for k in KEEP if k in g}
    return rows


def check_deals(p, rows, seed_of, decks_of, max_i):
    bad = [k for k, r in rows.items() if r["seed"] != seed_of(r)]
    if bad:
        r = rows[bad[0]]
        die(f"{p}: {len(bad)} games are not on kta's fresh deals, e.g. {bad[0]} has seed {r['seed']:,}, expected "
            f"{seed_of(r):,} (section 3.2): a development base or a wrong pairs file; nothing read from it")
    bad = [k for k, r in rows.items() if not FRESH_LO <= r["seed"] <= FRESH_HI or not 0 <= r["i"] < max_i]
    if bad:
        die(f"{p}: {len(bad)} games outside the fresh block or with i >= {max_i}, e.g. {bad[0]}")
    bad = [k for k, r in rows.items() if r["first_seat"] != r["i"] % 2]
    if bad:
        die(f"{p}: {len(bad)} games break the seat rule (even i puts the first-named deck in seat 0), e.g. {bad[0]}")
    if decks_of:
        bad = [k for k, r in rows.items() if (r["a"], r["b"]) != decks_of(r)]
        if bad:
            r = rows[bad[0]]
            die(f"{p}: {len(bad)} games are between other decks than the pairs file's, e.g. {bad[0]}: {(r['a'], r['b'])} "
                f"against {decks_of(r)}")


def load(p, n, bots, mode, seed_of, decks_of=None, max_i=500):
    """{key: record}; mode 'abi' keys by (a, b, i), 'pi' by (pairing, i). STOP unless exactly n games, the pilots named,
    every game on its fresh deal, the seat rule, the pairs file's decks."""
    rows = read_games(p, mode)
    if len(rows) != n:
        die(f"{p}: {len(rows)} games, expected {n}: an incomplete or wrong file, nothing read from it")
    got = {(r["bot_a"], r["bot_b"]) for r in rows.values()}
    if got != {bots}:
        die(f"{p}: pilots {sorted(got)}, expected {bots}")
    check_deals(p, rows, seed_of, decks_of, max_i)
    SCANNED.append(p)
    return rows


def same_deals(p, rows, base, what, subset=False):
    """Every game of `rows` is the same deal as `base`'s game with its key: seed, both decks (and deck files where both
    record them) and the seats. With subset=False the two files must also hold exactly the same keys."""
    if not subset and rows.keys() != base.keys():
        die(f"{p}: its games are not {what}'s deals ({len(rows.keys() ^ base.keys())} games in only one of the two)")
    extra = [k for k in rows if k not in base]
    if extra:
        die(f"{p}: {len(extra)} games are on deals {what} does not have, e.g. {extra[0]}")
    for fld in ("seed", "a", "b", "first_seat", "a_file", "b_file"):
        bad = [k for k in rows if fld in rows[k] and fld in base[k] and rows[k][fld] != base[k][fld]]
        if bad:
            die(f"{p}: {len(bad)} games differ from {what}'s on '{fld}', e.g. {bad[0]}: {rows[bad[0]][fld]!r} against "
                f"{base[bad[0]][fld]!r}: not the same deals")


def load_mixed(patterns, bots, mode, base, what):
    """The runner's mixed rows for one direction: every file matching the globs, merged (a deal twice is a STOP). Each game
    must be on a deal of `base` (seed, decks, seats). Returns (rows, files); rows None when no file is in."""
    files = sorted({f for pat in patterns for f in glob.glob(path(pat))})
    files = [f for f in files if f.endswith(".jsonl")]
    if not files:
        return None, []
    rows = {}
    for f in files:
        r = read_games(f, mode)
        got = {(g["bot_a"], g["bot_b"]) for g in r.values()}
        if r and got != {bots}:
            die(f"{f}: pilots {sorted(got)}, expected {bots}")
        dup = rows.keys() & r.keys()
        if dup:
            die(f"{f}: {len(dup)} deals also appear in another mixed-row file of the same direction, e.g. {min(dup)}")
        same_deals(f, r, base, what, subset=True)
        rows.update(r)
        SCANNED.append(f)
    return rows, files


# ---------------------------------------------------------------------------------------------------------------
# 1. The footprint, read first.
# ---------------------------------------------------------------------------------------------------------------
P(f"kta's reading (rl/results/kta_2026-09-29/REGISTRATION.md, registered Sept 29 with Dustin's word); files {DIR}/{PX}_*")
if REPS == DEFAULT_REPS:
    P(f"score45 bootstrap: --reps {REPS} (score.py's default; its seeds are fixed, so a rerun is identical).")
elif REPS < DEFAULT_REPS:
    P(f"WARNING: --reps {REPS} is BELOW score45's default {DEFAULT_REPS}. The ΔMSE 95% and τ̂ 90% bounds that gate move with "
      f"--reps. This is a test setting: DO NOT READ THIS OUTPUT AS THE REGISTERED READING.")
else:
    P(f"NOTE: --reps {REPS} is above score45's default {DEFAULT_REPS} (the rerun a bound near a registered line asks for; "
      f"5.4). The bounds below are this run's.")
FPFILE = path("footprint.txt")
if not os.path.exists(FPFILE):
    die(f"{FPFILE} does not exist. The 45 cells are not finished; the footprint fixes the route and is read first (5.1). "
        f"Nothing else is read.")
P("\n1. THE FOOTPRINT (5.1; footprint.txt, read first; it fixes the route):")
FPL = None
for ln in open(FPFILE, encoding="utf-8").read().splitlines():
    if ln.startswith("FOOTPRINT"):
        P("   " + ln)
        m = re.match(r"^FOOTPRINT (\w+): (\d+) of (\d+) paired games on the 45 cells differ from kog3's = ([\d.]+)% -> (.*)$", ln)
        if not m:
            die(f"footprint.txt line not in the runner's format: {ln!r}")
        if m.group(1) == CODE:
            if FPL:
                die("footprint.txt has two FOOTPRINT lines for kta3")
            FPL = (int(m.group(2)), int(m.group(3)), float(m.group(4)), m.group(5))
if FPL is None:
    die("footprint.txt has no FOOTPRINT line for kta3")
FP_D, FP_N, FP_PC, FP_RT = FPL
if FP_N != 22500 or abs(100 * FP_D / FP_N - FP_PC) > 0.006:
    die(f"footprint.txt's kta3 line is inconsistent ({FP_D} of {FP_N} = {FP_PC}%; the 45 cells have 22,500 paired games)")
ROUTE = route_of(FP_D, FP_N)
if not FP_RT.startswith(("reserve", "ordinary")) or FP_RT.startswith("reserve") != (ROUTE == "reserve"):
    die(f"footprint.txt's route text ({FP_RT!r}) disagrees with the route its counts give ({ROUTE}: {FP_D} of {FP_N}; 15% of "
        f"{FP_N} is {15 * FP_N // 100} games). Stop and write it down.")

# The 45 cells' structure (pairing numbers and decks) is the development table's (3.2: "same lists, same pairing numbers").
_dev_struct = {}
for _f, _grp in (("table_kog3.jsonl", "table"), ("new17_kog3.jsonl", "new17")):
    for _ln in open(os.path.join(DEVKOG, _f), encoding="utf-8"):
        _g = json.loads(_ln)
        _dev_struct[(_grp, _g["pairing"], _g["i"])] = (_g["a"], _g["b"])
seed_table = lambda r: SEED_TABLE + 10_000 * r["pairing"] + r["i"]  # noqa: E731
seed_new = lambda r: SEED_NEW + 10_000 * r["pairing"] + r["i"]  # noqa: E731
seed_b2e = lambda r: SEED_B2E + 10_000 * r["pairing"] + r["i"]  # noqa: E731
seed_d = lambda r: SEED_D + 10_000 * r["pairing"] + r["i"]  # noqa: E731


def load45(code, bots):
    t = load(path(f"{PX}_{code}_table.jsonl"), 14000, bots, "abi", seed_table, lambda r: _dev_struct.get(("table", r["pairing"], r["i"])))
    n = load(path(f"{PX}_{code}_new17.jsonl"), 8500, bots, "abi", seed_new, lambda r: _dev_struct.get(("new17", r["pairing"], r["i"])))
    if t.keys() & n.keys():
        die(f"{code}'s table and new-cell files overlap")
    return t, n


for _nm in (f"{PX}_kog3_table.jsonl", f"{PX}_kog3_new17.jsonl", f"{PX}_kta3_table.jsonl", f"{PX}_kta3_new17.jsonl"):
    if not os.path.exists(path(_nm)):
        die(f"{_nm} is not in although footprint.txt exists")
BASE_T, BASE_N = load45(BASE, (BASE, BASE))
BASE45 = {**BASE_T, **BASE_N}
NEW_T, NEW_N = load45(CODE, (CODE, CODE))
NEW45 = {**NEW_T, **NEW_N}
same_deals(f"{PX}_kta3_table/new17", NEW45, BASE45, "kog3's fresh 45 cells")
CELLS = list(dict.fromkeys((a, b) for a, b, _ in BASE45))
TABLE_CELLS = set(dict.fromkeys((a, b) for a, b, _ in BASE_T))
if len(CELLS) != 45:
    die(f"kog3's fresh 45-cell files hold {len(CELLS)} cells, not 45")
ICELL = {c: sorted(i for a, b, i in BASE45 if (a, b) == c) for c in CELLS}
if any(v != list(range(500)) for v in ICELL.values()):
    die("a cell of kog3's fresh files does not have deals 0-499")
DECKS = sorted({d for c in CELLS for d in c})
REACH_CELLS = {c for c in CELLS if set(c) & set(REACH_DECKS)}
if len(REACH_CELLS) != 17:
    die(f"section 2's reach on the 45 cells is 17 cells (Suicune's and Rayquaza's lists); the files give {len(REACH_CELLS)}")
DIFF45 = [k for k in BASE45 if BASE45[k]["moves"] != NEW45[k]["moves"]]
if len(DIFF45) != FP_D:
    die(f"footprint.txt says {FP_D} games differ; kta3's and kog3's fresh files give {len(DIFF45)}: stop and write it down")
FPC = Counter((a, b) for a, b, _ in DIFF45)
RES45 = sum(1 for k in BASE45 if BASE45[k]["first_deck_score"] != NEW45[k]["first_deck_score"])
ACTIVE = [c for c in CELLS if FPC[c] > 0]
P(f"   cross-check: the moves fields of the fresh files reproduce footprint.txt's count ({FP_D:,}); {RES45:,} of those games "
  f"changed their result.")
P(f"   kta3: {FP_D:,} of {FP_N:,} = {100 * FP_D / FP_N:.4f}% (15% is {15 * FP_N // 100:,} games) -> "
  f"{'THE RESERVE ROUTE (5.2)' if ROUTE == 'reserve' else 'THE ORDINARY RULE (5.3; 15% or more)'}; decided from the counts, "
  f"and footprint.txt's own route text agrees.")
P(f"   predicted, not chosen (5.1): about 2.5% (development 559 of 22,500 = 2.48%), all in the 17 cells of section 2. "
  f"The prediction never picks the route.")
P(f"   cells with a changed game: {len(ACTIVE)} of 45" + (": " + ", ".join(f"{a} v {b} ({FPC[(a, b)]})" for a, b in ACTIVE) if ACTIVE else ""))
OUT_REACH = [c for c in ACTIVE if c not in REACH_CELLS]
INTEG = {}   # integrity lines: id -> text (a line here holds the reading; never a registered fail)
if OUT_REACH:
    INTEG["int_reach45"] = (f"{sum(FPC[c] for c in OUT_REACH)} changed games in {len(OUT_REACH)} cells whose lists carry no "
                            f"switch-1 card: {', '.join(f'{a} v {b}' for a, b in OUT_REACH[:8])}{' ...' if len(OUT_REACH) > 8 else ''}")
    P(f"   INTEGRITY LINE (section 4; holds the reading, never a registered fail): {INTEG['int_reach45']}. kta3 would be "
      f"doing more than switch 1.")
else:
    P("   integrity line (section 4): every changed game sits in the 17 cells whose lists carry a switch-1 card.")


# ---------------------------------------------------------------------------------------------------------------
# 1b. Preconditions (section 4).
# ---------------------------------------------------------------------------------------------------------------
def preconditions():
    P("\n1b. PRECONDITIONS (section 4: the programs, identity, timing, RULE findings). The runner stops before any table if "
      "one fails; restated here from the disk and its files:")
    for name, (rel, want, gates_) in PROGRAMS.items():
        f = os.path.join(args.engine_dir, rel)
        if not os.path.exists(f):
            if gates_:
                die(f"the program {f} is missing: section 4.7 (rebuild ec7e1a8 and replay 45,000 games) before anything is read")
            P(f"   {name}: {f} not found (it plays only the counters, which are reported; gates nothing)")
            continue
        got = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if got != want:
            if gates_:
                die(f"{name} sha256 {got} is not the registered {want} (section 4): every kta game must be played by these "
                    f"programs; nothing is read")
            P(f"   {name} sha256 {got[:16]}... differs from the section 4 hash {want[:16]}...: expected if 4.6's --seed-base "
              f"option was added (its own sha256); the counters are reported and gate nothing")
        else:
            P(f"   {name} sha256 {got} = the registered hash")
    ip = path("identity_check.txt")
    if not os.path.exists(ip):
        die(f"{ip} does not exist: section 4's identity replays are not recorded, so no kta game is read")
    seen, total = [], 0
    for ln in (x.strip() for x in open(ip, encoding="utf-8")):
        if not ln:
            continue
        m = re.match(r"^(.+): (\d+) of (\d+) equal on ", ln)
        if not m:
            die(f"identity_check.txt line not in the runner's format: {ln!r}")
        if m.group(2) != m.group(3) or int(m.group(3)) == 0:
            die(f"IDENTITY FAILED in identity_check.txt: {ln!r}. Section 4 needs every replay equal; nothing is read.")
        seen.append((m.group(1), int(m.group(3))))
        total += int(m.group(3))
    labels = " ".join(k for k, _ in seen)
    if total < IDENTITY_GAMES or "kog3" not in labels or "kta3" not in labels:
        die(f"identity_check.txt records {total:,} equal games over {len(seen)} replays; section 4.2 and 4.3 name {IDENTITY_GAMES:,} "
            f"(kog3 and kta3 on every group at i < 20, and the A/B tool on deck 07)")
    P(textwrap.fill(f"identity: {len(seen)} replays, every one equal, {total:,} games (section 4 names {IDENTITY_GAMES:,}): " +
                    "; ".join(f"{k} {n:,}" for k, n in seen), width=118, initial_indent="   ", subsequent_indent="      "))
    tp = next((p for p in (path(f"{PX}_timing_2.txt"), path(f"{PX}_timing_1.txt")) if os.path.exists(p)), None)
    if tp is None:
        die(f"neither {PX}_timing_1.txt nor {PX}_timing_2.txt exists: section 4.4's timing run is not recorded")
    tl = " ".join(open(tp, encoding="utf-8").read().split())
    P(f"   timing ({os.path.basename(tp)}" + ("; the second pair decides" if tp.endswith("_2.txt") else "") + f"): {tl}")
    if "limit 1.25: within" not in tl:
        die(f"the timing line is not 'within' the 1.25x limit ({tl!r}): section 4.4; nothing is read")
    rule, pages = [], 0
    for f in sorted(glob.glob(path("*.txt"))):
        lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        if "Findings (occurrences / games affected):" not in lines:
            continue
        pages += 1
        j = lines.index("Findings (occurrences / games affected):")
        for ln in lines[j + 1:]:
            if re.match(r"^  RULE\b", ln):
                rule.append(f"{os.path.basename(f)}: {ln.strip()}")
    if rule:
        die(f"a RULE finding in a scan page (section 4.5: it stops the reading): {rule[0]}" + (f" (and {len(rule) - 1} more)" if len(rule) > 1 else ""))
    P(f"   RULE findings: none in the {pages} scan pages in the folder (each page beside a file read is checked below).")


preconditions()


def integrity_note():
    if args.integrity_explained:
        if not os.path.exists(args.integrity_explained) or not open(args.integrity_explained, encoding="utf-8").read().strip():
            die(f"--integrity-explained {args.integrity_explained}: no such file, or it is empty")
        return open(args.integrity_explained, encoding="utf-8").read().strip()
    return None


EXPLAINED = integrity_note()
if ROUTE == "ordinary":
    P("\n1c. THE ORDINARY ROUTE'S FIRST CHECK (5.1: 'nothing else is read until the program hashes, the pairs files and the "
      "integrity line are checked'; development was 2.48%):")
    P("   program hashes: checked above. pairs files: every game of the four 45-cell files is on its fresh deal (the seed "
      "formula), with the development table's decks and pairing numbers, and the seat rule.")
    if OUT_REACH and not EXPLAINED:
        die(f"the footprint is {100 * FP_D / FP_N:.2f}% and the integrity line is not clean ({INTEG['int_reach45']}): a wiring or "
            f"identity fault is the first reading (5.1). Nothing else is read until it is explained (--integrity-explained FILE).")
    P("   integrity line on the 45 cells: " + ("clean." if not OUT_REACH else f"NOT clean, explained by a human "
      f"({args.integrity_explained}), below.") + " (Its coverage part is checked in section 5 and holds the reading there.)")
    P("   The ordinary rule applies as written in 5.3.")
if args.footprint_only:
    P("\n(--footprint-only: stopped after the footprint and its preconditions, as 5.1 has it: read and committed alone.)")
    sys.exit(0)

NOTES = """
NOTES: where the registration's text needs a coding, and the one coded (the conservative one where they differ)
 K1  Frame. The 45-cell block of score45.py gates; its 44-cell decision set (Altaria v Sceptile quarantined) is compared
     beside on the ΔMSE label, the τ̂ bound and the vetoes that count; a difference is a note and gates nothing (N1).
 K2  The event-resampled intervals are printed beside and gate nothing; the match-level ones gate (N2, 5.4).
 K3  (b)'s "no veto counts (including B2e's held-out veto)": the 45-cell rule-v2 vetoes through mixed rows plus the B2e
     held-out veto (N3). The held-out veto is also section 6 item 7's coverage test, so it is one gate, named "coverage
     (B2e held-out, part of (b))" when it fails.
 K4  A held-out veto is own-side harm in the mixed rows alone (the 95% interval wholly below zero) (N4); "more than 2
     further" without harm is printed as an investigation item.
 K5  (c): per meta deck, pooled over its cells where kta3's footprint is not zero, both seat orders, worse = the pooled
     95% interval wholly below zero (N5). A cell whose footprint is zero has mixed rows equal to kog3's games (a pilot's
     choice is a function of the position): the reading reads them as kog3's games and checks the i<40 sample of both
     directions that 5.2 (c) runs there (an INTEGRITY line if a sampled game differs). On the ordinary route every cell
     needs its 500 deals in both directions (5.3), and they are read as run.
 K6  (d) (5.2 (d)): kta3 on the census Rayquaza list against kog3 on it, kog3 on the panel in both arms, 8 rows x 2,000
     fresh deals; the equal-weight mean of the per-row mean differences; half-width 1.96 x sqrt(sum of per-row variances
     of the mean difference) / 8; passes when mean minus half-width is above zero. The per-row share is the row's mean
     over the sum of the row means (not shown when that sum is not positive); a passing gain more than half of which is
     one row is said beside the verdict (5.9; gates nothing).
 K7  The ΔMSE label (5.4). score.py prints the bounds to one decimal. The upper edge is read from its own "below 0",
     which compares the unrounded bound; the lower edge only as printed: "+0.0" is not called. When no game on the 45
     cells changed its result, every draw is exactly 0: the interval is the point 0, which spans zero.
 K8  Near-zero bounds (5.4; N9 extended): a ΔMSE bound within 5% of the interval's width of 0 (either edge) and a τ̂
     bound within 0.10 of -1.0 are PENDING below --reps 20000; the 20,000-rep rerun (the same games) decides. "Within"
     is inclusive and is tested in whole units of the printout (a printed -1.10, or -1.9 to +0.1, is within).
 K9  Coverage mixed rows (top block 3, Dustin's words): a pairing may be skipped only when every one of its deals has
     kta3's both-sides game equal to kog3's on the move fingerprint, both decks (and deck files), the seed and the seats.
     The reader checks that itself for every pairing. A skipped pairing counts as no change (its mixed rows are read
     as kog3's games) and must be named in coverage_skip.txt. A pairing named as skipped whose deals differ, a skipped
     pairing the report does not name, or a pairing whose deals differ without its mixed rows, holds its coverage test
     (PENDING, named). A mixed-row game that differs in a pairing whose both-sides games all matched is an INTEGRITY line.
 K10 Jasmine (5.5): pooled over deck 07's 1,920 games per arm (turns played summed over turns offered summed, the
     census's denominator, kt_ab_play.py's per-game `plays`); a point value; it reaches 20% when 5 x played >= offered.
     The guard: kog3's own rate on the same deals at 20% or more counts as not passed. Never offered: not passed.
 K11 What gates on which ΔMSE label (5.2-5.5, section 6): wholly above zero fails with no fallback; the Jasmine line gates
     only when the interval spans zero; every other test gates whenever the label does not fail on accuracy. On the
     ordinary route with the interval wholly below zero, 5.3 names the vetoes, coverage and (d); section 6 items 4-5 name
     the τ̂ bound and (c) as well, and they are gated (the conservative reading); a verdict that fails only on them says so.
 K12 Integrity lines (section 4 and N5): a changed game where switch 1 cannot reach, or a mixed-row game that differs
     where the both-sides games all matched. They hold the reading (HELD), never fail it; the verdict they would allow is
     printed beside. They are read before anything that decides, the 'wholly above zero' label and every FAIL included
     (section 4: such a line "holds the reading ... until it is explained"; 5.1 stops on it on the ordinary route), so no
     verdict, NOT ADOPTED included, is recorded while one is open. A file read without its scan page (4.5) holds the same
     way until the page is in. --integrity-explained FILE records a human's explanation, printed in full.
 K13 Preconditions: the programs are hashed here from the disk (deckgym and legality_scan gate; tool_census is reported,
     since 4.6's --seed-base option gives it its own sha256); identity_check.txt (every replay equal, 7,920 games); the
     timing line within 1.25x; every scan page in the folder free of RULE findings (a RULE finding STOPs), and every
     legality_scan file read has its page.
 K14 Section 5.5's count: every own-side no-harm test with a changed game behind it is counted, and the chance that a
     harmless candidate trips at least one (1 - 0.975^n) is printed.
"""
P(NOTES)
if EXPLAINED:
    P("INTEGRITY LINES EXPLAINED BY A HUMAN (--integrity-explained " + args.integrity_explained + "), in full:")
    P(textwrap.indent(EXPLAINED, "   | "))

# ---------------------------------------------------------------------------------------------------------------
# 2. The 45 cells: score45.py (rules v2), with kta3's mixed rows.
# ---------------------------------------------------------------------------------------------------------------
P("\n2. THE 45 CELLS (score45.py --rules v2; kog3 current, kta3 new; paired by deal; fresh deals; kta3's mixed rows).")
MIXR = {}      # direction -> the runner's mixed rows (or None)
MIX_FILES = {}
for dr, bots in (("first", (CODE, BASE)), ("second", (BASE, CODE))):
    MIXR[dr], MIX_FILES[dr] = load_mixed([f"{PX}_mixed_table_kta3_{dr}*.jsonl", f"{PX}_mixed_new17_kta3_{dr}*.jsonl"],
                                         bots, "abi", BASE45, "kog3's fresh 45 cells")
    P(f"   mixed rows, kta3 on the {dr}-named deck: " + (f"{len(MIXR[dr]):,} games in {len(MIX_FILES[dr])} file(s)" if MIXR[dr] is not None else "not in yet"))
NEED_ALL = ROUTE == "ordinary"
EFF45, SRC45 = {}, {}   # direction -> {key: record} read by (c), Suicune's rows and score45; and where each came from
C_MISSING, ZERO_DIFF, MIX_CHANGED45 = [], [], 0
for dr in ("first", "second"):
    rows = MIXR[dr] or {}
    eff, src = {}, {}
    present = defaultdict(set)
    for (a, b, i) in rows:
        present[(a, b)].add(i)
    for c in CELLS:
        keys = [(c[0], c[1], i) for i in range(500)]
        if present[c] == set(range(500)):                 # run in full: read as run
            eff.update({k: rows[k] for k in keys})
            src.update({k: "run" for k in keys})
        elif FPC[c] > 0 or NEED_ALL:                      # needed in full and not in
            C_MISSING.append(f"{c[0]} v {c[1]} ({dr}: {len(present[c])} of 500 deals)")
        else:                                             # zero footprint: kog3's games, the i<40 sample checks them (K5)
            if not set(range(SAMPLE_I)) <= present[c]:
                C_MISSING.append(f"{c[0]} v {c[1]} ({dr}: the i<{SAMPLE_I} integrity sample has "
                                 f"{len(present[c] & set(range(SAMPLE_I)))} of {SAMPLE_I})")
            eff.update({k: BASE45[k] for k in keys})
            src.update({k: "kog3 (zero-footprint cell, K5)" for k in keys})
        for i in present[c]:
            k = (c[0], c[1], i)
            if rows[k]["moves"] != BASE45[k]["moves"]:
                MIX_CHANGED45 += 1
                if FPC[c] == 0:
                    ZERO_DIFF.append((dr, k))
    EFF45[dr], SRC45[dr] = eff, src
if ZERO_DIFF:
    zc = sorted({f"{k[0]} v {k[1]}" for _, k in ZERO_DIFF})
    INTEG["int_zero45"] = (f"{len(ZERO_DIFF)} mixed-row games in {len(zc)} zero-footprint cells differ from kog3's moves: "
                           f"{', '.join(zc[:8])}{' ...' if len(zc) > 8 else ''}")
    P(f"   INTEGRITY LINE (holds the reading, never a registered fail): {INTEG['int_zero45']}. A pilot's choice is a function "
      f"of the position, so the footprint set (c) reads is incomplete or a file is wrong: a human read (K5, K12).")
elif any(MIXR[d] is not None for d in MIXR):
    P("   integrity: every mixed-row game run in a zero-footprint cell equals kog3's moves.")
if C_MISSING:
    P(f"   the mixed rows the registration needs are not all in ({len(C_MISSING)}): " + "; ".join(C_MISSING[:6]) + (" ..." if len(C_MISSING) > 6 else ""))


def write_composite(dr, bots):
    """score45's --mixed input for one direction: the runner's games in the cells it had to run, kog3's games (relabelled,
    marked) in a zero-footprint cell (K5). Cells still missing are left out (score45 then says AWAITS)."""
    os.makedirs(os.path.join(PAGES, "score45_inputs"), exist_ok=True)
    out = os.path.join(PAGES, "score45_inputs", f"{PX}_kta3_mixed_{dr}_composite.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for k in sorted(EFF45[dr]):
            r = dict(EFF45[dr][k])
            r["bot_a"], r["bot_b"], r["mixed_source"] = bots[0], bots[1], SRC45[dr][k]
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return out


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run_score45(with_mixed):
    old_p = [path(f"{PX}_kog3_table.jsonl"), path(f"{PX}_kog3_new17.jsonl")]
    new_p = [path(f"{PX}_kta3_table.jsonl"), path(f"{PX}_kta3_new17.jsonl")]
    mixed = [write_composite(dr, bots) for dr, bots in (("first", (CODE, BASE)), ("second", (BASE, CODE)))
             if with_mixed and MIXR[dr] is not None]
    page = os.path.join(PAGES, "score45_kta3_vs_kog3.txt")
    cmd = [sys.executable, os.path.join(K45, "score45.py"), "--rules", "v2", "--old-games"] + old_p + ["--new-games"] + new_p + \
          ["--old", BASE, "--new", CODE] + (["--mixed"] + mixed if mixed else []) + ["--reps", str(REPS)]
    sig = json.dumps({"reps": REPS, "args": [os.path.basename(x) for x in cmd[2:]],
                      "inputs": {os.path.basename(p): sha(p) for p in old_p + new_p + mixed}}, sort_keys=True)
    side = page + ".reps"
    same = os.path.exists(side) and open(side, encoding="utf-8").read() == sig
    if args.reuse_45 and same and os.path.exists(page):
        text, tag = open(page, encoding="utf-8").read(), f"reused: made by this same command on inputs with the same sha256, --reps {REPS}"
    else:
        if args.reuse_45 and os.path.exists(page):
            P(f"   (--reuse-45: {os.path.basename(page)} is not reusable (a different command, inputs or --reps, or no sidecar); scoring afresh)")
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=K45)
        text, tag = out.stdout + out.stderr, f"freshly scored, --reps {REPS}"
        os.makedirs(PAGES, exist_ok=True)
        with open(page, "w", encoding="utf-8") as f:
            f.write(text)
        if out.returncode:
            die(f"score45.py failed (exit {out.returncode}); nothing read from it:\n{text[-600:]}")
        with open(side, "w", encoding="utf-8") as f:
            f.write(sig)
    if "45 common pairings" not in text:
        die(f"score45.py did not read 45 common pairings (see {page})")
    return parse45(text), page, tag, mixed


R45, PAGE45, TAG45, MIXED_IN = run_score45(True)
A, Dn = R45["all"], R45["dec"]
P(f"   page: {os.path.basename(PAGE45)} ({TAG45}); mixed rows given to score45: "
  + (", ".join(os.path.basename(m) for m in MIXED_IN) or "none in yet") + " (the runner's games in the cells it ran; kog3's in a zero-footprint cell, K5)")
TAU_K = A["real"][BASE]
P(f"   real error on the 45 cells: kog3 {TAU_K:.1f} -> kta3 {A['real'][CODE]:.1f}  (kog3's own figure on the fresh deals "
  f"replicates the development 14.0: printed beside, 5.4)")
dm = A["dmse"]
LABELS, LABEL, LNOTES = dmse_label(dm[4], dm[5], dm[3], REPS, exact_zero=(RES45 == 0))
P(f"   ΔMSE (kta3 minus kog3): {dm[0]:+.1f} points^2, 95% interval {dm[4]} to {dm[5]}; by event (beside): "
  f"{A['dmse_ev'][0]:+.1f} to {A['dmse_ev'][1]:+.1f}")
P(f"   LABEL (RUN5's three outcomes): {LABEL_TEXT[LABEL]}" + ("" if len(LABELS) == 1 else
  f"  -- PENDING: the label can still be {' or '.join(sorted(LABELS))}"))
for x in LNOTES:
    P("     " + x)
SD45 = (dm[2] - dm[1]) / 3.92


def as_real(delta):
    v = TAU_K ** 2 + delta
    return math.sqrt(v) if v > 0 else float("nan")


P(f"   detectable size (5.4, RUN5): the interval's sd {SD45:.1f}; MDE50 (1.96 sd) {1.96 * SD45:.1f} points^2, as real error "
  f"{TAU_K:.2f} -> {as_real(-1.96 * SD45):.2f}; MDE80 (2.80 sd) {2.80 * SD45:.1f}, as real error {TAU_K:.2f} -> "
  f"{as_real(-2.80 * SD45):.2f} (real error after = sqrt(kog3's^2 - δ), the eval-power check's conversion)")
t = A["tau"]
SDT = (t[2] - t[1]) / (2 * 1.645)
P(f"   τ̂ margin (kog3 minus kta3): {t[0]:+.2f}, 90% interval {t[1]:+.2f} to {t[2]:+.2f}; by event (beside) "
  f"{A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f}; sd {SDT:.3f}: (b) fails half the time only if the true margin is near "
  f"{-1.0 + 1.645 * SDT:+.2f} or worse (a guard, not a measurement). Read as no harm only: a positive margin 'replicates on "
  f"the simulator side' and is never credited as accuracy (3.3).")
P("   development, for scale (not evidence): ΔMSE -5.9 (95% -11.0 to -1.4), τ̂ margin +0.21 (90% +0.06 to +0.31). score45's "
  "own 'ADOPTION RULE' line is the ordinary rule's view and is not read or quoted as an adoption here.")
veto_txt = "; ".join(f"{w} (+{g:.1f}) {txt[:200]}" for w, g, k, txt in A["veto"] if k in ("COUNTS", "AWAITS")) or "none"
P(f"   rule-v2 vetoes that count or await mixed rows: {veto_txt}")
inv = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "investigation item"]
nev = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "never counts"]
P(f"   investigation items (neither side worse): {', '.join(inv) or 'none'}; never count (band over +/-15): {', '.join(nev) or 'none'}")
st, notes = tau_gate(t[1], A["tau_ev"][0], REPS)
gate("b1", "(b) τ̂ margin (kog3 minus kta3) 90% lower bound at -1.0 or above", st,
     f"{t[1]:+.2f} (margin {t[0]:+.2f}, interval {t[1]:+.2f} to {t[2]:+.2f}; by event {A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f})"
     + "".join("; " + x for x in notes))
if A["counts"]:
    st, dt = "FAIL", "counts: " + "; ".join(v[0] for v in A["counts"])
elif A["awaits"]:
    st, dt = "PENDING", "awaits mixed rows: " + "; ".join(v[0] for v in A["awaits"])
else:
    st, dt = "PASS", "none counts" + (f" ({len(A['veto'])} veto candidates, all investigation items or never-count)" if A["veto"] else "")
gate("b2", "(b) no rule-v2 veto counts on the 45 cells", st, dt)
_dl = dmse_label(Dn["dmse"][4], Dn["dmse"][5], Dn["dmse"][3], REPS, exact_zero=(RES45 == 0))[1]
diffs = []
if _dl != LABEL:
    diffs.append(f"ΔMSE label: 45 cells {LABEL}, 44 cells {_dl}")
if (Dn["tau"][1] >= -1.0) != (A["tau"][1] >= -1.0):
    diffs.append(f"τ̂ lower bound against -1.0: 45 cells {A['tau'][1]:+.2f}, 44 cells {Dn['tau'][1]:+.2f}")
if {v[0] for v in Dn["counts"]} != {v[0] for v in A["counts"]}:
    diffs.append(f"vetoes that count: 45 cells {[v[0] for v in A['counts']]}, 44 cells {[v[0] for v in Dn['counts']]}")
P("   NOTE (K1): the 44-cell decision set " + ("reads differently: " + "; ".join(diffs) + ". The 45-cell block gates." if diffs else "gives the same label, τ̂ gate and vetoes."))

# ---------------------------------------------------------------------------------------------------------------
# 3. Clause (c).
# ---------------------------------------------------------------------------------------------------------------
P(f"\n3. CLAUSE (c), no meta deck's own side worse beyond paired noise: the mixed rows of the cells with a changed game, "
  f"both directions, 500 deals, pooled per deck (K5).")


def own_deltas(deck, cell):
    a, b = cell
    dr, sign = ("first", 1) if deck == a else ("second", -1)
    return [sign * 100 * (EFF45[dr][(a, b, i)]["first_deck_score"] - BASE45[(a, b, i)]["first_deck_score"]) for i in range(500)]


def deck_report(deck, cells):
    parts = [own_deltas(deck, c) for c in cells]
    m, h, n = pool(parts)
    return m, h, n, {c: (mv(p)[0], 1.96 * math.sqrt(mv(p)[1])) for c, p in zip(cells, parts)}


C_TESTS = []   # (deck, changed mixed-row games behind it)
if MIXR["first"] is None or MIXR["second"] is None:
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "PENDING", "the 45 cells' mixed rows are not in yet")
    P("   the mixed rows are not in yet: (c) waits.")
elif [x for x in C_MISSING if "integrity sample" not in x]:
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "PENDING",
         "mixed rows needed and not in: " + "; ".join(x for x in C_MISSING if "integrity sample" not in x)[:300])
    P("   (c) waits: " + "; ".join(x for x in C_MISSING if "integrity sample" not in x)[:600])
else:
    worse, lines = [], []
    for deck in DECKS:
        cells = [c for c in ACTIVE if deck in c]
        if not cells:
            continue
        m, h, n, per = deck_report(deck, cells)
        ch = sum(1 for c in cells for dr, who in (("first", c[0]), ("second", c[1])) if who == deck
                 for i in range(500) if EFF45[dr][(c[0], c[1], i)]["moves"] != BASE45[(c[0], c[1], i)]["moves"])
        C_TESTS.append((deck, ch))
        bad = m + h < 0
        if bad:
            worse.append(deck)
        lines.append(f"   {deck:>17}: own side {fmt(m, h)} over {len(cells)} cells ({n:,} deals; {ch:,} mixed-row games changed)"
                     + ("  <- WORSE beyond noise" if bad else ""))
        for cell, (mm, hh) in per.items():
            if mm + hh < 0:
                lines.append(f"{'':21}(listed, gates nothing) {cell[0]} v {cell[1]}: {fmt(mm, hh)}")
    P("\n".join(lines) if lines else "   no cell has a changed game: nothing to read (every mixed row is kog3's game).")
    smp = [x for x in C_MISSING if "integrity sample" in x]
    if smp:
        INTEG["int_sample45"] = "the i<40 integrity sample of the zero-footprint cells is not all in: " + "; ".join(smp[:4])
        P("   " + INTEG["int_sample45"] + " (holds the reading until it is in).")
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "FAIL" if worse else "PASS",
         ("worse: " + ", ".join(worse)) if worse else f"{len(ACTIVE)} cells with a changed game read, no deck worse")

# ---------------------------------------------------------------------------------------------------------------
# 4. Clause (d).
# ---------------------------------------------------------------------------------------------------------------
P(f"\n4. CLAUSE (d), the census Rayquaza list v the eight panel lists: 8 rows x {D_DEALS:,} fresh deals per arm (seeds "
  f"23,003,000,000 + panel index x 10,000 + i), kog3 on the panel in both arms; read once (5.2 (d)).")
D_RES = None
_dk, _dt = have(f"{PX}_d_kog3.jsonl", "holds (d)"), have(f"{PX}_d_kta3.jsonl", "holds (d)")
_d_decks = lambda r: ("c-rayquaza", D_OPP[r["pairing"]]) if 0 <= r["pairing"] < 8 else (None, None)  # noqa: E731
_cens = None
_cp = os.path.join(RES, "kt_carrier_census_2026-09-26", "cells_c-dragonair_mega_rayquaza_ex.csv")
if os.path.exists(_cp):
    _cens = {r["opponent"]: float(r["score_pct"]) for r in csv.DictReader(open(_cp, encoding="utf-8")) if r["dataset"] == "pooled"}
if not (_dk and _dt):
    gate("d", "(d) Rayquaza's pooled own-side gain, whole 95% interval above zero", "PENDING", "the (d) rows are not all in yet")
else:
    DB = load(_dk, 8 * D_DEALS, (BASE, BASE), "pi", seed_d, _d_decks, max_i=D_DEALS)
    DX = load(_dt, 8 * D_DEALS, (CODE, BASE), "pi", seed_d, _d_decks, max_i=D_DEALS)
    for nm, rows in ((_dk, DB), (_dt, DX)):
        if {k for k in rows} != {(p, i) for p in range(8) for i in range(D_DEALS)}:
            die(f"{nm}: not pairings 0-7 x deals 0-{D_DEALS - 1}")
        bad = [k for k, r in rows.items() if r.get("a_file") not in (None, D_LIST)]
        if bad:
            die(f"{nm}: side a is not the census Rayquaza list ({D_LIST}), e.g. {bad[0]}: {rows[bad[0]].get('a_file')}")
    same_deals(_dt, DX, DB, "kog3 on the Rayquaza list")
    parts = [[100 * (DX[(p, i)]["first_deck_score"] - DB[(p, i)]["first_deck_score"]) for i in range(D_DEALS)] for p in range(8)]
    m, h, n = pool(parts)
    rows_mv = [mv(x) for x in parts]
    shares = d_shares([x[0] for x in rows_mv])
    CH_D = sum(1 for k in DB if DB[k]["moves"] != DX[k]["moves"])
    P(f"   kta3 on the Rayquaza list (side a, seat 0 on even i) against kog3 on it; {CH_D:,} of {8 * D_DEALS:,} kta3-arm games "
      f"differ from kog3's. Per row (5.9, beside the pooled number; each row's share of the pooled sum):")
    for p, o in enumerate(D_OPP):
        sb = 100 * sum(DB[(p, i)]["first_deck_score"] for i in range(D_DEALS)) / D_DEALS
        sx = 100 * sum(DX[(p, i)]["first_deck_score"] for i in range(D_DEALS)) / D_DEALS
        rm, rv = rows_mv[p]
        lim_txt = f"; Limitless (census list, pooled) {_cens[o]:.1f}" if _cens and o in _cens else ""
        sh = f"; share {100 * shares[p]:+.0f}%" if shares else ""
        P(f"     v {o:9}: kog3 {sb:5.1f} -> kta3 {sx:5.1f} ({rm:+.2f} +/- {1.96 * math.sqrt(rv):.2f}){sh}{lim_txt}")
    if not shares:
        P("     (the row means sum to zero or less, so no share is shown)")
    sd_d = h / 1.96
    gain = m - h > 0
    P(f"   pooled over 8 rows ({n:,} deals per arm): {fmt(m, h)} points -> {'a GAIN: the whole 95% interval is above zero' if gain else 'NO gain shown at this size'}")
    P(f"   detectable size: sd {sd_d:.3f}; MDE50 (1.96 sd) {1.96 * sd_d:.2f} points, MDE80 (2.80 sd) {2.80 * sd_d:.2f} points "
      f"(registered estimate at 2,000: half-width about 0.195, MDE50 about 0.20, MDE80 about 0.28). Development, for scale: "
      f"+1.00 +/- 0.39 at 500 deals, Vespiquen +3.8 about half of it.")
    if _cens:
        P("   (census Limitless, equal-weight over the eight, pooled: 46.3 +/- 4.8 over 606 matches; the figures above are the "
          "simulator's on that list, reported, gating nothing)")
    ONE_ROW = None
    if gain and shares and max(shares) > 0.5:
        ONE_ROW = f"{D_OPP[shares.index(max(shares))]} supplies {100 * max(shares):.0f}% of the pooled gain"
        P(f"   NOTE (5.9, gates nothing): one row supplies more than half of this passing gain: {ONE_ROW}.")
    D_RES = (m, h, sd_d, CH_D, ONE_ROW, [x[0] for x in rows_mv])
    gate("d", "(d) Rayquaza's pooled own-side gain, whole 95% interval above zero", "PASS" if gain else "FAIL",
         f"{fmt(m, h)} points pooled over 8 rows x {D_DEALS:,}" + ("" if gain else
         f"; 'gain not shown at this size on Rayquaza' (MDE50 {1.96 * sd_d:.2f}, MDE80 {2.80 * sd_d:.2f} points); not "
         f"evidence that switch 1 does nothing"))

# ---------------------------------------------------------------------------------------------------------------
# 5. Coverage.
# ---------------------------------------------------------------------------------------------------------------
P("\n5. COVERAGE (5.5; RUN5 'How coverage rows count': own-side harm in the mixed rows is a veto that blocks the takeover; "
  "accuracy is reported). Mixed rows only where kta3's both-sides games differ (K9).")
SKIPF = path("coverage_skip.txt")
REPORT = parse_skip_report(open(SKIPF, encoding="utf-8").read()) if os.path.exists(SKIPF) else None
P(f"   coverage_skip.txt: " + ("in; it names " + ", ".join(f"{g} {sum(v[0] == 'SKIP' for v in d.values())} skipped / "
                                                          f"{sum(v[0] == 'RUN' for v in d.values())} run" for g, d in sorted(REPORT.items()))
                              if REPORT is not None else "NOT in yet (every skipped pairing is then unnamed and holds its test)"))
B2E_TSV = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(B2E_DIR, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
if {p for p in range(96) if B2E_TSV[p]["opponent"] == "suicune"} != REACH_B2E:
    die("b2e_pairings.tsv's Suicune pairings are not section 2's reach list (4, 12, ..., 92)")
NEWD_TSV = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(TSV, "new_decks.tsv"), encoding="utf-8"), delimiter="\t")}
LIMB = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E_DIR, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        LIMB[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
ARCH = sorted({k for k, _ in LIMB["pooled"]})
COV_TESTS = []  # (test name, changed mixed-row games behind it)
COV_CH = {}     # group -> (both-sides changed games, mixed-row changed games on its own-side rows)
SKIP_PROBLEMS = defaultdict(list)


def arch_of(k):
    base = k.replace("dustin_", "")
    return next((n for n in ARCH if n == base), None) or next((n for n in ARCH if n.startswith(base)), None)


def coverage_rows(group, base, new, dirs, reach):
    """One coverage group's own-side rows (K9). base/new: both-sides {(p, i)}; dirs: {direction: (pairings of that
    direction, runner rows or None, files)}. Returns ({direction: {(p, i): record}} for the pairings available,
    {pairing: status text}, changed both-sides games, changed mixed-row games)."""
    deals = defaultdict(list)
    for (p, i) in sorted(base):
        deals[p].append(i)
    pairings = sorted(deals)
    match = {p: all(equal5(base[(p, i)], new[(p, i)]) for i in deals[p]) for p in pairings}
    ndiff = {p: sum(1 for i in deals[p] if not equal5(base[(p, i)], new[(p, i)])) for p in pairings}
    out_reach = [p for p in pairings if ndiff[p] and p not in reach]
    if out_reach:
        INTEG[f"int_reach_{group}"] = (f"{group}: {sum(ndiff[p] for p in out_reach)} changed both-sides games in pairings whose "
                                       f"lists carry no switch-1 card: {out_reach[:10]}")
        P(f"     INTEGRITY LINE (holds the reading, never a fail): {INTEG[f'int_reach_{group}']}")
    rep = (REPORT or {}).get(group, {})
    eff, status, mix_changed = {}, {}, 0
    for dr, (dps, rows, files) in dirs.items():
        e = {}
        present = defaultdict(set)
        for (p, i) in (rows or {}):
            present[p].add(i)
        for p in dps:
            full = present[p] == set(deals[p])
            said = rep.get(p, (None,))[0]
            if full:
                e.update({(p, i): rows[(p, i)] for i in deals[p]})
                ch = sum(1 for i in deals[p] if rows[(p, i)]["moves"] != base[(p, i)]["moves"])
                mix_changed += ch
                status[(dr, p)] = f"run ({ch} changed)"
                if match[p] and ch:
                    INTEG[f"int_zero_{group}_{dr}_{p}"] = (f"{group} pairing {p} ({dr}): {ch} mixed-row games differ from kog3's "
                                                           f"although every both-sides deal matched")
                if said == "SKIP" and not match[p]:
                    SKIP_PROBLEMS[group].append((p, f"pairing {p}: coverage_skip.txt says SKIP but {ndiff[p]} deals differ (its rows were run anyway)"))
            elif present[p]:
                status[(dr, p)] = f"INCOMPLETE ({len(present[p])} of {len(deals[p])} deals)"
                SKIP_PROBLEMS[group].append((p, f"pairing {p} ({dr}): mixed rows incomplete, {len(present[p])} of {len(deals[p])} deals"))
            elif match[p]:
                e.update({(p, i): base[(p, i)] for i in deals[p]})
                if REPORT is None:
                    status[(dr, p)] = "skipped (no change); coverage_skip.txt not in"
                    SKIP_PROBLEMS[group].append((p, f"pairing {p}: skipped, and coverage_skip.txt is not in to name it"))
                elif said == "SKIP":
                    status[(dr, p)] = "skipped (named; re-checked: every deal equal)"
                else:
                    status[(dr, p)] = "skipped (no change) but NOT named in coverage_skip.txt"
                    SKIP_PROBLEMS[group].append((p, f"pairing {p}: skipped without being named in coverage_skip.txt"))
            else:
                if said == "SKIP":
                    status[(dr, p)] = f"BAD SKIP: named as skipped, but {ndiff[p]} deals differ"
                    SKIP_PROBLEMS[group].append((p, f"pairing {p}: coverage_skip.txt says SKIP, but {ndiff[p]} of {len(deals[p])} deals "
                                                f"differ on moves, decks, seed or seats (matching winners alone is not enough): "
                                                f"its mixed rows must be run"))
                elif rows is None:
                    status[(dr, p)] = f"not in yet ({ndiff[p]} deals differ)"
                    SKIP_PROBLEMS[group].append((p, f"pairing {p} ({dr}): {ndiff[p]} deals differ and its mixed rows are not in yet"))
                else:
                    status[(dr, p)] = f"MISSING ({ndiff[p]} deals differ; no mixed rows)"
                    SKIP_PROBLEMS[group].append((p, f"pairing {p} ({dr}): {ndiff[p]} deals differ and the mixed-row file has no rows for it"))
        eff[dr] = e
    for p, (said, eq, n_) in rep.items():
        if p not in match:
            die(f"coverage_skip.txt names {group} pairing {p}, which the group does not have")
        if said == "SKIP" and eq != n_:
            SKIP_PROBLEMS[group].append((p, f"pairing {p}: coverage_skip.txt says SKIP with {eq} of {n_} deals equal"))
        if (said == "RUN") == match[p]:
            P(f"     note: coverage_skip.txt says {said} for {group} pairing {p}; the reader finds every deal "
              f"{'equal' if match[p] else 'not equal'} ({ndiff[p]} differ)" + (" (running a skippable pairing only costs games)" if said == "RUN" else ""))
    n_run = sum(1 for (dr, p), s in status.items() if s.startswith("run"))
    n_skip = sum(1 for s in status.values() if s.startswith("skipped"))
    P(f"     {group}: {sum(ndiff.values()):,} both-sides games differ, in {sum(1 for p in pairings if ndiff[p])} of {len(pairings)} "
      f"pairings; own-side rows: {n_run} run, {n_skip} skipped as unchanged"
      + (f"; PROBLEMS: " + probs(group, n=4) if SKIP_PROBLEMS[group] else ""))
    COV_CH[group] = (sum(ndiff.values()), mix_changed)
    return eff, status, sum(ndiff.values()), mix_changed


def probs(group, counted=None, n=3):
    """The coverage-shortcut problems of a group as text; `counted` limits them to the pairings that gate (B2e: 0-47)."""
    ps = [t_ for p, t_ in SKIP_PROBLEMS[group] if counted is None or p in counted]
    return "; ".join(ps[:n]) + (" ..." if len(ps) > n else "")


def own_pool(eff_dr, base, rows_of, own):
    """Pooled own side over pairings (500 deals each); None if any pairing's rows are not available."""
    parts = []
    for p in rows_of:
        ks = [(p, i) for i in range(500)]
        if any(k not in base for k in ks):
            die(f"a coverage pairing {p} does not have deals 0-499 in kog3's file")
        if any(k not in eff_dr for k in ks):
            return None
        parts.append([100 * (own(eff_dr[k]) - own(base[k])) for k in ks])
    return pool(parts)


fds = lambda g: g["first_deck_score"]  # noqa: E731

# 5a. B2e.
P("\n   5a. B2e (96 pairings; the held-out archetypes 0-47 count, Dustin's files 48-95 are reported):")
_bk, _bt = have(f"{PX}_b2e_kog3.jsonl", "holds coverage (B2e)"), have(f"{PX}_b2e_kta3.jsonl", "holds coverage (B2e)")
b2e_decks = lambda r: (B2E_TSV[r["pairing"]]["held_key"], B2E_TSV[r["pairing"]]["opponent"])  # noqa: E731
B2E_B = B2E_X = None
if not (_bk and _bt):
    gate("cov_b2e", "coverage (B2e held-out, part of (b)): no held-out deck's own side hurt", "PENDING", "the B2e both-sides files are not in yet")
else:
    B2E_B = load(_bk, 48000, (BASE, BASE), "pi", seed_b2e, b2e_decks)
    B2E_X = load(_bt, 48000, (CODE, CODE), "pi", seed_b2e, b2e_decks)
    same_deals(_bt, B2E_X, B2E_B, "kog3's fresh B2e")
    rows, files = load_mixed([f"{PX}_mixed_b2e_kta3_first*.jsonl"], (CODE, BASE), "pi", B2E_B, "kog3's fresh B2e")
    eff, stat, _, _ = coverage_rows("b2e", B2E_B, B2E_X, {"first": (list(range(96)), rows, files)}, REACH_B2E)

    def panel(rs):
        by = defaultdict(list)
        for (p, i), g in rs.items():
            r = B2E_TSV[p]
            by[(r["block"], r["held_key"], r["opponent"])].append(g["first_deck_score"])
        res = defaultdict(dict)
        for (block, k, o), s in by.items():
            res[(block, k)][o] = 100 * sum(s) / len(s)
        return res
    a_, b_ = panel(B2E_B), panel(B2E_X)
    FUR = {}
    for (block, k) in sorted(a_):
        x, y = sum(a_[(block, k)].values()) / 8, sum(b_[(block, k)].values()) / 8
        arch = arch_of(k)
        cells = [o for o in a_[(block, k)] if (arch, o) in LIMB["pooled"]]
        L = sum(LIMB["pooled"][(arch, o)] for o in cells) / len(cells)
        FUR[k] = y - x, abs(y - L) - abs(x - L)
        P(f"     {block} {k:24} kog3 {x:5.1f} -> kta3 {y:5.1f}; Limitless {L:5.1f}; further by {FUR[k][1]:+.1f} (accuracy reported)")
    held = sorted({B2E_TSV[p]["held_key"] for p in range(96)}, key=lambda k: min(p for p in range(96) if B2E_TSV[p]["held_key"] == k))
    vetoes, waits, harm_only, fur_only = [], [], [], []
    P("     own side in the mixed rows (kta3 on the held deck, kog3 on the panel, against kog3 on both; a skipped pairing is no change):")
    for k in held:
        ps = [p for p in range(96) if B2E_TSV[p]["held_key"] == k]
        block = B2E_TSV[ps[0]]["block"]
        res = own_pool(eff["first"], B2E_B, ps, fds)
        ch = sum(1 for p in ps for i in range(500) if (p, i) in eff["first"] and eff["first"][(p, i)]["moves"] != B2E_B[(p, i)]["moves"])
        if block.startswith("A"):
            COV_TESTS.append((f"B2e {k}", ch))
        if res is None:
            if block.startswith("A"):
                waits.append(k)
            P(f"     {block} {k:24} own side: waits ({', '.join(stat[('first', p)] for p in ps if not stat[('first', p)].startswith(('run', 'skipped')))})")
            continue
        m, h, n = res
        harm = m + h < 0
        fur = FUR[k][1]
        if block.startswith("A"):
            tag = "VETO (own side worse beyond paired noise)" if harm else ("investigation item (more than 2 further, own side not worse)" if fur > 2 else "no harm")
            if harm:
                vetoes.append(k)
                if fur <= 2:
                    harm_only.append(k)
            elif fur > 2:
                fur_only.append(k)
        else:
            tag = "reported (Dustin's file)" + ("; own side worse beyond paired noise: a finding to write down" if harm else "")
        P(f"     {block} {k:24} own side {fmt(m, h)} over {len(ps)} rows ({ch} changed); further by {fur:+.1f} -> {tag}")
    cnt = f"harm but not more than 2 further: {', '.join(harm_only) or 'none'}; more than 2 further but no harm: {', '.join(fur_only) or 'none'}"
    P(f"   B2e held-out veto: {', '.join(vetoes) or 'none'}  (K4: {cnt})")
    bprobs = probs("b2e", counted=set(range(48)))   # Dustin's files (48-95) are reported: their rows hold nothing
    if vetoes:
        gate("cov_b2e", "coverage (B2e held-out, part of (b)): no held-out deck's own side hurt", "FAIL", "veto: " + ", ".join(vetoes) + f" ({cnt})")
    elif waits or bprobs:
        gate("cov_b2e", "coverage (B2e held-out, part of (b)): no held-out deck's own side hurt", "PENDING",
             "; ".join((["waits: " + ", ".join(waits)] if waits else []) + ([bprobs] if bprobs else [])))
    else:
        gate("cov_b2e", "coverage (B2e held-out, part of (b)): no held-out deck's own side hurt", "PASS", f"no held-out deck's own side worse ({cnt})")
    P("\n   The held-out direction (RUN5, Sept 29; reported beside every verdict, gates nothing):")
    sys.path.insert(0, K45)
    import heldout_direction as HD  # noqa: E402
    _bn, _cn, _rows = HD.compute(_bk, _bt, B2E_DIR)
    HD.show(_bn, _cn, [r for r in _rows if r[0].startswith("A")], None, "held-out direction")
    HD.show(_bn, _cn, [r for r in _rows if r[0].startswith("B")], "   Dustin's files (48-95), beside, not in the line above:", "Dustin's files")
    P("   (development, kta3: all six held-out decks within 0.1 point.)")

# 5b. Scizor.
P("\n   5b. The Scizor row (8 rows x 500; own side = kta3 on Scizor, kog3 on the panel list, against kog3 on both):")
_sk, _sx = have(f"{PX}_scizor_kog3.jsonl", "holds coverage (Scizor)"), have(f"{PX}_scizor_kta3.jsonl", "holds coverage (Scizor)")
scz_decks = lambda r: (NEWD_TSV[r["pairing"]]["held_key"], NEWD_TSV[r["pairing"]]["opponent"])  # noqa: E731
if not (_sk and _sx):
    gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", "the Scizor both-sides files are not in yet")
else:
    SB = load(_sk, 4000, (BASE, BASE), "pi", seed_new, scz_decks)
    SX = load(_sx, 4000, (CODE, CODE), "pi", seed_new, scz_decks)
    same_deals(_sx, SX, SB, "kog3's fresh Scizor rows")
    if sorted({p for p, _ in SB}) != list(range(8)):
        die(f"{_sk}: not pairings 0-7")
    r1, f1 = load_mixed([f"{PX}_mixed_scizor_kta3_first*.jsonl"], (CODE, BASE), "pi", SB, "kog3's fresh Scizor rows")
    r2, f2 = load_mixed([f"{PX}_mixed_scizor_kta3_second*.jsonl"], (BASE, CODE), "pi", SB, "kog3's fresh Scizor rows")
    eff, stat, _, _ = coverage_rows("scizor", SB, SX, {"first": (list(range(8)), r1, f1)}, set(range(8)))
    P(f"     Scizor's panel average, both sides: kog3 {100 * sum(map(fds, SB.values())) / 4000:.1f} -> kta3 "
      f"{100 * sum(map(fds, SX.values())) / 4000:.1f} (reported; Scizor's real figure 32.2 +/- 10.2 pooled; gates nothing)")
    res = own_pool(eff["first"], SB, range(8), fds)
    ch = sum(1 for k, g in eff["first"].items() if g["moves"] != SB[k]["moves"])
    COV_TESTS.append(("Scizor", ch))
    if res is None:
        gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", probs("scizor") or "mixed rows not in")
        P("     own side: waits")
    else:
        m, h, n = res
        harm = m + h < 0
        soft = harm and m > -2
        P(f"     own side: {fmt(m, h)} over 8 rows ({ch} changed) -> {'VETO (own side worse beyond paired noise)' if harm else 'no harm'}"
          + (f" (the fall, {-m:.2f}, is under 2 points: vetoed as harm alone, K4)" if soft else ""))
        if harm:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "FAIL", f"Scizor own side {fmt(m, h)}" + ("; the fall is under 2 points (harm alone)" if soft else ""))
        elif SKIP_PROBLEMS["scizor"]:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", probs("scizor"))
        else:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "PASS", f"Scizor own side {fmt(m, h)}")
    if r2 is not None:
        full = {k: g for k, g in r2.items()}
        ps = [p for p in range(8) if all((p, i) in full for i in range(500))]
        if ps:
            m2, h2, _ = pool([[-100 * (full[(p, i)]["first_deck_score"] - SB[(p, i)]["first_deck_score"]) for i in range(500)] for p in ps])
            P(f"     the other direction (kta3 on the panel list, kog3 on Scizor), the panel's side over {len(ps)} run rows: {fmt(m2, h2)} (reported only)")
    else:
        P("     the other direction: no rows in (reported only; holds nothing)")

# 5c. The second lists.
P("\n   5c. The four second lists (own side = kta3 on the list, kog3 on the other deck, against kog3 on both; accuracy reported):")
_v2 = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
lists_bad, lists_wait = [], []
for v in VARS:
    trows = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(TSV, f"var_{v}.tsv"), encoding="utf-8"), delimiter="\t")}
    other = {p: (r["opponent"] if r["variant_side"] == "a" else r["held_key"]) for p, r in trows.items()}
    if {p for p, o in other.items() if o == "suicune"} != REACH_VAR[v]:
        die(f"var_{v}.tsv's rows against Suicune are not section 2's reach list {sorted(REACH_VAR[v])}")
    side = {p: r["variant_side"] for p, r in trows.items()}
    sa, sb_ = sorted(p for p in trows if side[p] == "a"), sorted(p for p in trows if side[p] == "b")
    base_seed = SEED_B2E if v == "l-charizardy" else SEED_TABLE
    seed_v = lambda r, s0=base_seed: s0 + 10_000 * r["pairing"] + r["i"]  # noqa: E731
    dec_v = lambda r, t=trows: (t[r["pairing"]]["held_key"], t[r["pairing"]]["opponent"])  # noqa: E731
    own = lambda g, s=side: g["first_deck_score"] if s[g["pairing"]] == "a" else 1 - g["first_deck_score"]  # noqa: E731
    _gk, _gx = have(f"{PX}_var_{v}_kog3.jsonl", f"holds coverage ({v})"), have(f"{PX}_var_{v}_kta3.jsonl", f"holds coverage ({v})")
    if not (_gk and _gx):
        lists_wait.append(f"{v} both-sides files not in")
        continue
    GB = load(_gk, 500 * len(trows), (BASE, BASE), "pi", seed_v, dec_v)
    GX = load(_gx, 500 * len(trows), (CODE, CODE), "pi", seed_v, dec_v)
    same_deals(_gx, GX, GB, f"kog3's fresh {v}")
    dirs = {}
    if sa:
        ra, fa = load_mixed([f"{PX}_var_{v}_kta3_mixed_a*.jsonl"], (CODE, BASE), "pi", {k: g for k, g in GB.items() if k[0] in sa}, f"kog3's fresh {v} (side a)")
        dirs["a"] = (sa, ra, fa)
    if sb_:
        rb, fb = load_mixed([f"{PX}_var_{v}_kta3_mixed_b*.jsonl"], (BASE, CODE), "pi", {k: g for k, g in GB.items() if k[0] in sb_}, f"kog3's fresh {v} (side b)")
        dirs["b"] = (sb_, rb, fb)
    eff, stat, _, _ = coverage_rows(f"var_{v}", GB, GX, dirs, REACH_VAR[v])
    merged = {**eff.get("a", {}), **eff.get("b", {})}
    avg = lambda rs: 100 * sum(own(g) for g in rs.values()) / len(rs)  # noqa: E731
    deck = trows[next(iter(trows))]["deck"]
    if deck == "charizardy":
        cs = [LIMB["pooled"].get(("charizardy_entei", o)) for o in {r["opponent"] for r in trows.values()}]
        Lf, src = sum(x for x in cs if x is not None) / sum(1 for x in cs if x is not None), "B2e pooled, charizardy_entei"
    else:
        vals = []
        for p, r in trows.items():
            da, db = (deck, r["opponent"]) if r["variant_side"] == "a" else (r["held_key"], deck)
            w, l, t_ = _v2[f"{min(da, db)}|{max(da, db)}"]
            s = (w + 0.5 * t_) / (w + l + t_)
            vals.append(100 * (s if min(da, db) == deck else 1 - s))
        Lf, src = sum(vals) / len(vals), "development half, the same opponents"
    x, y = avg(GB), avg(GX)
    acc = f"opponent average kog3 {x:5.1f} -> kta3 {y:5.1f}; figure {Lf:5.1f} ({src}); further by {abs(y - Lf) - abs(x - Lf):+.1f} (reported)"
    res = own_pool(merged, GB, sorted(trows), own)
    ch = sum(1 for k, g in merged.items() if g["moves"] != GB[k]["moves"])
    COV_TESTS.append((v, ch))
    if res is None:
        lists_wait.append(f"{v}: " + probs(f"var_{v}", n=2))
        P(f"     {v:13} {acc}; own side: waits")
        continue
    m, h, n = res
    harm = m + h < 0
    P(f"     {v:13} {acc}; own side (mixed) {fmt(m, h)} over {len(trows)} rows ({ch} changed) -> {'VETO (own side worse beyond paired noise)' if harm else 'no harm'}")
    if harm:
        lists_bad.append(f"{v} {fmt(m, h)}")
    elif SKIP_PROBLEMS[f"var_{v}"]:
        lists_wait.append(f"{v}: " + probs(f"var_{v}", n=2))
if lists_bad:
    gate("cov_lst", "coverage: no second list's own side hurt", "FAIL", "veto: " + "; ".join(lists_bad))
elif lists_wait:
    gate("cov_lst", "coverage: no second list's own side hurt", "PENDING", "; ".join(lists_wait)[:400])
else:
    gate("cov_lst", "coverage: no second list's own side hurt", "PASS", "no second list's own side worse beyond noise")
for g_, pr in SKIP_PROBLEMS.items():
    for p_, x in pr:
        P(f"   COVERAGE SHORTCUT (K9): {g_} {x}" + (" (a Dustin file: reported, holds nothing)" if g_ == "b2e" and p_ >= 48 else " (holds its test)"))
if REPORT is not None:
    for g_ in REPORT:
        if g_ not in ("b2e", "scizor", "table", "new17") and g_ not in {f"var_{v}" for v in VARS}:
            die(f"coverage_skip.txt names a group the reading does not know: {g_!r}")
    for g_ in ("table", "new17"):
        for p, (said, eq, n_) in REPORT.get(g_, {}).items():
            cells = [c for c in (TABLE_CELLS if g_ == "table" else set(CELLS) - TABLE_CELLS)
                     if (BASE_T if g_ == "table" else BASE_N).get((c[0], c[1], 0), {}).get("pairing") == p]
            ok = cells and all(equal5(BASE45[(c[0], c[1], i)], NEW45[(c[0], c[1], i)]) for c in cells for i in range(500))
            if said == "SKIP" and not ok:
                INTEG[f"int_skip45_{g_}_{p}"] = f"coverage_skip.txt says SKIP for {g_} pairing {p}, whose games are not all equal"
                P(f"   INTEGRITY LINE: {INTEG[f'int_skip45_{g_}_{p}']}")
_n_tests = sum(1 for _, ch in COV_TESTS + C_TESTS if ch > 0)
P(f"\n   5.5's count: {len(C_TESTS) + len(COV_TESTS)} own-side no-harm tests ((c) per deck, B2e held-out, Scizor, second lists); "
  f"{_n_tests} have a changed game behind them; the chance a harmless candidate trips at least one of those: "
  f"1 - 0.975^{_n_tests} = {1 - 0.975 ** _n_tests:.3f}.")

# ---------------------------------------------------------------------------------------------------------------
# 6. The Dustin-deck A/B and the Jasmine line.
# ---------------------------------------------------------------------------------------------------------------
P("\n6. THE DUSTIN-DECK A/B, fresh (5.6; reported, gating nothing except through the Jasmine line, which gates only in the "
  "fallback). kog3 on the opponent's seat in both arms; paired by (opponent, seat, seed).")
TOOLS = ("Metal Core Barrier", "Steel Apron", "Heavy Helmet")


def load_ab(p, deck, pilot):
    rows = [json.loads(ln) for ln in open(p, encoding="utf-8") if ln.strip()]
    d = {(r["opp"], r["seat"], r["seed"]): r for r in rows}
    if len(d) != len(rows):
        die(f"{p}: {len(rows) - len(d)} repeated deals")
    if len(d) != AB_GAMES:
        die(f"{p}: {len(d)} games, expected {AB_GAMES}: an incomplete or wrong file, nothing read from it")
    bad = [r for r in rows if r.get("pilot") != pilot or r.get("opp_pilot") != BASE or r.get("deck") != int(deck)]
    if bad:
        die(f"{p}: pilots or deck are not ({pilot} on deck {deck}, kog3 on the lists), e.g. {bad[0].get('pilot')}/{bad[0].get('opp_pilot')}")
    opps = sorted({r["opp"] for r in rows})
    if len(opps) != 8:
        die(f"{p}: {len(opps)} opponents, not the panel's 8")
    for r in rows:
        want = SEED_AB + 10_000 * int(deck) + 1_000 * opps.index(r["opp"]) + (500 if r["seat"] else 0) + r["i"]
        if r["seed"] != want or not 0 <= r["i"] < 120:
            die(f"{p}: a game is not on the A/B's fresh deal (seed {r['seed']:,}, expected {want:,}; 23,004,000,000 + 10,000 x deck + "
                f"1,000 x opponent (+500 seat 1) + i, i < 120)")
    if Counter((r["opp"], r["seat"]) for r in rows) != Counter({(o, s): 120 for o in opps for s in (0, 1)}):
        die(f"{p}: not 120 games per opponent and seat")
    return d


def offered_played(data, name):
    off = pl = 0
    for r in data.values():
        o, q = r["plays"].get(name, (0, 0))
        off, pl = off + o, pl + q
    return off, pl


AB = {}
JAS = None
for deck in AB_DECKS:
    holds = "holds the Jasmine line (fallback only)" if deck == "07" else "reported only"
    pk, px = have(f"{PX}_ab_d{deck}_kog3.jsonl", holds), have(f"{PX}_ab_d{deck}_kta3.jsonl", holds)
    if not (pk and px):
        continue
    bk, bx = load_ab(pk, deck, BASE), load_ab(px, deck, CODE)
    if bk.keys() != bx.keys():
        die(f"{px}: its games are not kog3's A/B deals for deck {deck}")
    keys = sorted(bk)
    dd = [int(bx[k]["won"]) - int(bk[k]["won"]) for k in keys]
    n = len(dd)
    mean = sum(dd) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in dd) / (n - 1))
    half = 1.96 * sd / math.sqrt(n)
    b_, c_ = sum(x == 1 for x in dd), sum(x == -1 for x in dd)
    differ = sum(bk[k]["moves"] != bx[k]["moves"] for k in keys)
    wk, wx = sum(r["won"] for r in bk.values()), sum(r["won"] for r in bx.values())
    AB[deck] = (bk, bx, mean, half, differ)
    tag = ""
    if mean + half < 0:
        tag = "  <- a Dustin deck hurt beyond noise: a finding to write down, not a veto"
    P(f"   deck {deck}: kog3 {100 * wk / n:5.1f}% -> kta3 {100 * wx / n:5.1f}%; paired {100 * mean:+.1f} points "
      f"({100 * (mean - half):+.1f} to {100 * (mean + half):+.1f}); McNemar p {mcnemar_exact(b_, c_):.3f} ({b_} / {c_}); "
      f"moves differ {100 * differ / n:.1f}%{tag}")
    for name in ("Jasmine",) + TOOLS:
        cells = []
        for arm, data in (("kog3", bk), ("kta3", bx)):
            off, pl = offered_played(data, name)
            tl = [t_ for r in data.values() for t_ in r.get("tools", []) if t_[0] == name]
            if not (off or tl):
                continue
            q = sum(bool(t_[6]) for t_ in tl)
            cells.append(f"{arm} played {pl:,} of {off:,} offered turns" + (f" ({100 * pl / off:.1f}%)" if off else "")
                         + (f", attached {len(tl)}, on a qualifying holder {q} ({100 * q / len(tl):.0f}%)" if tl else ""))
        if cells:
            P(f"     {name}: " + "; ".join(cells))
    if deck == "07":
        JAS = (offered_played(bx, "Jasmine"), offered_played(bk, "Jasmine"), differ)
P("   Predictions written before the games (reported; a wrong-direction move beyond its interval is a finding to write down, "
  "not a gate that fired): Metal Core Barrier on a qualifying holder unchanged (development 80% against 79%); Steel Apron "
  "70.8% -> 84.7%, Heavy Helmet 86.6% -> 90.2% (deck 01), 68.7% -> 73.4% (deck 03); Jasmine 'well below the flat +10's 82%'.")
if JAS is None:
    gate("jas", "Jasmine on deck 07: at least 20% of offered turns, with the kog3 guard (the fallback only)", "PENDING",
         "deck 07's A/B files are not in yet")
    P("   JASMINE LINE: deck 07's files are not in yet (it gates only in the fallback).")
else:
    (ko, kp), (go, gp), _ = JAS
    st, txt = jas_gate(ko, kp, go, gp)
    gate("jas", "Jasmine on deck 07: at least 20% of offered turns, with the kog3 guard (the fallback only)", st, txt)
    P(f"   JASMINE LINE (5.5): {txt}. Development: kog3 0.4% (36 of 8,597), kta3 30.2% (1,711 of 5,669).")
if "07" in AB:
    _, _, m7, h7, _ = AB["07"]
    AB07 = (m7, h7)
    P(f"   deck 07 (the reason the candidate exists; development +8.5, +6.7 to +10.4): {100 * m7:+.1f} points "
      f"({100 * (m7 - h7):+.1f} to {100 * (m7 + h7):+.1f}) -> "
      + ("REPLICATED on fresh deals (reported; it isn't the gate)" if m7 - h7 > 0 else
         "the reason the candidate exists DID NOT REPLICATE on fresh deals (reported; gates nothing: Dustin, 'it isn't the gate')"))
else:
    AB07 = None


def census_row(arm, card):
    """The counters' row for a card (tool_census's table: deck, card, turns offered, turns played, %), with the file's
    first line (which deals it counted); None if no counter file of that arm has the row."""
    for f in sorted(glob.glob(path(f"{PX}_census_{arm}*.txt"))):
        lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        for ln in lines:
            m = re.match(rf"^(\S+)\s+{re.escape(card)}\s+(\d+)\s+(\d+)\s+[\d.]+", ln)
            if m:
                return m.group(1), int(m.group(2)), int(m.group(3)), os.path.basename(f), (lines[0] if lines else "")
    return None


P("   The counters (4.6; reported, gate nothing). Stiffen played per offered turn, predicted to rise (development kog3 45.7%, "
  "58 of 127 -> kta3 55.3%, 84 of 152; the interval is wide, about +/-12 points, so a miss reads 'not shown at this size'):")
_ck, _cx = census_row(BASE, "attack Stiffen"), census_row(CODE, "attack Stiffen")
if _ck and _cx:
    p1, p2 = _ck[2] / _ck[1], _cx[2] / _cx[1]
    dd_, hh_ = p2 - p1, 1.96 * math.sqrt(p1 * (1 - p1) / _ck[1] + p2 * (1 - p2) / _cx[1])
    tag = ("rose, as predicted" if dd_ - hh_ > 0 else
           "fell beyond its interval: a finding to write down, not a gate that fired" if dd_ + hh_ < 0 else "not shown at this size")
    P(f"     kog3 {_ck[2]} of {_ck[1]} ({100 * p1:.1f}%) -> kta3 {_cx[2]} of {_cx[1]} ({100 * p2:.1f}%): {100 * dd_:+.1f} points "
      f"(+/- {100 * hh_:.1f}) -> {tag}")
    P(f"     counted on: {_ck[3]}: '{_ck[4][:110]}'; {_cx[3]}: '{_cx[4][:110]}' (development deals if the counter tool has no "
      f"--seed-base option: then labelled development-only, 4.6)")
else:
    P("     not in yet (reported only; holds nothing)")
TRACE_SEED = {"lucario": 23_005_000_000, "vespiquen": 23_005_001_000}   # section 3.2's trace seeds (run_kta.sh step 7)
TRACE_GAMES, SI = 200, "Scorching Interruption"


def load_trace(opp, arm):
    """One trace arm: trace_pilot.py's per-game rows and kta_trace_moves.py's rows, each exactly the seeds S .. S+199 once
    (kta_check.py trace-complete's test), the pilots named, the winners equal per seed. Returns ((pergame, moves) by
    seed, []) or (None, [the files not in yet]). A wrong file STOPS the reading, as every other input does."""
    names = [f"{PX}_trace_rayquaza_{opp}_{arm}_{k}.jsonl" for k in ("pergame", "moves")]
    miss = [n for n in names if not os.path.exists(path(n))]
    if miss:
        return None, miss
    want = list(range(TRACE_SEED[opp], TRACE_SEED[opp] + TRACE_GAMES))
    got = []
    for n in names:
        rows = [json.loads(ln) for ln in open(path(n), encoding="utf-8") if ln.strip()]
        if sorted(r.get("seed", -1) for r in rows) != want:
            die(f"{n}: {len(rows)} games, not the seeds {want[0]:,} to {want[-1]:,} once each (a trace arm is {TRACE_GAMES} "
                f"games on its fresh seeds, run_kta.sh step 7): an incomplete or wrong file")
        got.append({r["seed"]: r for r in rows})
    pg, mf = got
    bad = [s for s, r in mf.items() if r.get("pilot") != arm or r.get("opp_pilot") != BASE or not r.get("moves")
           or not isinstance(r.get("decisions"), list)]
    if bad:
        die(f"{names[1]}: the game at seed {bad[0]:,} is not {arm} on Rayquaza against kog3 with its moves and decisions")
    bad = [s for s in want if bool(pg[s]["won"]) != bool(mf[s]["won"])]
    if bad:
        die(f"{names[0]} and {names[1]}: the winner differs at seed {bad[0]:,} ({len(bad)} games): not the same games")
    return (pg, mf), []


def si_counts(pg):
    """Scorching Interruption's own turns offered and used (trace_pilot.py's per-game 'attacks' rows), and seat 0's wins."""
    off = used = 0
    for r in pg.values():
        for k, v in (r.get("attacks") or {}).items():
            if k.endswith(":" + SI):
                off, used = off + v[0], used + v[1]
    return off, used, sum(bool(r["won"]) for r in pg.values())


def dec_txt(d):   # a decision row [ply, actor, turn, n_legal, kind, label, h] as "kind label"
    return str(d[4]) + (f" {d[5]}" if d[5] else "")


P("   The Rayquaza traces (5.5; reported only, gate nothing): the census list in seat 0, 200 games per arm on the same seeds, "
  "kta3 then kog3 on Rayquaza, kog3 on the other side; Scorching Interruption: no prediction. Development (v Lucario, the "
  "scoreboard's list): offered 220 and used 151 under kta3, 223 and 150 under kog3; wins 60 and 59.")
for _opp in TRACE_SEED:
    _tx, _mx = load_trace(_opp, CODE)
    _tk, _mk = load_trace(_opp, BASE)
    if _mx or _mk:
        P(f"     v {_opp}: not in yet ({', '.join(_mx + _mk)}; holds nothing)")
        REPORTED_MISSING.extend(_mx + _mk)
        continue
    (_xpg, _xmf), (_kpg, _kmf) = _tx, _tk
    _ox, _ux, _wx = si_counts(_xpg)
    _ok, _uk, _wk = si_counts(_kpg)
    _chg = [s for s in sorted(_xmf) if _xmf[s]["moves"] != _kmf[s]["moves"]]
    _kind, _pair, _seat1, _nleg, _ended = Counter(), Counter(), 0, 0, 0
    for s in _chg:
        dx, dk = _xmf[s]["decisions"], _kmf[s]["decisions"]
        j = next((j for j in range(min(len(dx), len(dk))) if dx[j][6] != dk[j][6]), None)
        if j is None:          # every choice equal until one arm's game ended
            _ended += 1
            continue
        _kind[dx[j][4]] += 1
        _pair[(dec_txt(dx[j]), dec_txt(dk[j]))] += 1
        _seat1 += dx[j][1] != 0
        _nleg += dx[j][3] != dk[j][3]
    P(f"     v {_opp}: Scorching Interruption turns offered / used: kta3 {_ox} / {_ux}, kog3 {_ok} / {_uk}; Rayquaza's wins: "
      f"kta3 {_wx}, kog3 {_wk} of {TRACE_GAMES}; games whose moves differ: {len(_chg)} of {TRACE_GAMES}")
    if _chg:
        P("       the first decision that differs, by kind (kta3's choice), over those games: "
          + ", ".join(f"{k} {n}" for k, n in _kind.most_common()) + (f", none (one arm's game ended first) {_ended}" if _ended else ""))
        P("       in detail (kta3's choice / kog3's at the same ply): "
          + "; ".join(f"{a} / {b}: {n}" for (a, b), n in _pair.most_common(8)) + (" ..." if len(_pair) > 8 else ""))
        _nt = ([f"{_seat1} fall on the kog3 side's decision (seat 1)"] if _seat1 else []) + \
              ([f"{_nleg} have a different number of legal moves at that ply"] if _nleg else [])
        if _nt:
            P("       (of those first differences, " + "; ".join(_nt) + ")")

# ---------------------------------------------------------------------------------------------------------------
# 7. Reported beside.
# ---------------------------------------------------------------------------------------------------------------
P("\n7. REPORTED BESIDE (these gate nothing).")
_lim = {tuple(k.split("|")): tuple(v) for k, v in _v2.items()}
with open(os.path.join(RES, "gauntlet_runs_2026-09-26", "gauntlet_cells.csv"), encoding="utf-8", newline="") as _f:
    _gc = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(_f)}
for _c in CELLS:
    if _c not in _lim:
        _r = _gc[("development", _c[0], _c[1])]
        _lim[_c] = (int(_r["W"]), int(_r["L"]), int(_r["T"]))


def show_real(deck, title):
    P(f"   {title} (its own score; Limitless development half; miss = |sim - Limitless|):")
    rows = []
    for cell in CELLS:
        if deck not in cell:
            continue
        a, b = cell
        flip = deck == b
        w, l, t_ = _lim[cell]
        n_ = w + l + t_
        Lc = (w + 0.5 * t_) / n_
        band = 196 * math.sqrt(Lc * (1 - Lc) / n_)
        s0 = 100 * sum(BASE45[(a, b, i)]["first_deck_score"] for i in range(500)) / 500
        s1 = 100 * sum(NEW45[(a, b, i)]["first_deck_score"] for i in range(500)) / 500
        L_ = 100 * Lc
        r = (b if not flip else a, 100 - s0 if flip else s0, 100 - s1 if flip else s1, 100 - L_ if flip else L_, band, n_)
        rows.append(r)
        P(f"     {deck} v {r[0]:17} kog3 {r[1]:5.1f} kta3 {r[2]:5.1f} | Limitless {r[3]:5.1f} +/- {r[4]:4.1f} (n {r[5]}) | miss {abs(r[1] - r[3]):4.1f} -> {abs(r[2] - r[3]):4.1f}")
    a0, a1, La = (sum(r[j] for r in rows) / len(rows) for j in (1, 2, 3))
    P(f"     {'equal-weight average over ' + str(len(rows)) + ' cells':>34}: kog3 {a0:5.1f} kta3 {a1:5.1f} | Limitless {La:5.1f} | miss {abs(a0 - La):4.1f} -> {abs(a1 - La):4.1f}")


P("\n   7a. Suicune (Dustin, Sept 28: reported beside; the same direction as Rayquaza is supporting evidence, the other a "
  "finding to write down, not a gate that fired). Its real cells, before and after:")
show_real("suicune", "Suicune's nine real cells")
if MIXR["first"] is not None and MIXR["second"] is not None and not [x for x in C_MISSING if "integrity sample" not in x]:
    cells9 = [c for c in CELLS if "suicune" in c]
    cells7 = [c for c in cells9 if c in TABLE_CELLS]
    m9, h9, n9, per = deck_report("suicune", cells9)
    m7, h7, n7, _ = deck_report("suicune", cells7)
    P(f"   Suicune's own side in the mixed rows: nine rows {fmt(m9, h9)} ({n9:,} deals); the table's seven {fmt(m7, h7)} "
      f"(development -0.00 +/- 0.25 and +0.06 +/- 0.30)")
    for cell, (mm, hh) in per.items():
        P(f"        Suicune v {(cell[1] if cell[0] == 'suicune' else cell[0]):17} {fmt(mm, hh)}")
else:
    P("   Suicune's own side in the mixed rows: waits for the mixed rows.")
P("\n   7b. Rayquaza's real cells (the scoreboard's list; they count in the 45 cells like any other), before and after:")
show_real("rayquaza", "Rayquaza's nine real cells")
P("   The census list's cells against the eight are in section 4 (census Limitless pooled 46.3 +/- 4.8 over 606 matches).")
P("\n   7c. Deck averages over the 45 cells (score45's rows; current / new / Limitless; change in miss, + = further). "
  "Hydreigon's gap: development 7.3 -> 7.1:")
for dk, (cur, new, lim_, chg) in sorted(A["deck_avg"].items()):
    P(f"     {dk:>17}: kog3 {cur:5.1f} -> kta3 {new:5.1f}; Limitless {lim_:5.1f}; gap {abs(cur - lim_):4.1f} -> {abs(new - lim_):4.1f} ({chg:+.1f})")

# ---------------------------------------------------------------------------------------------------------------
# 8. The verdict.
# ---------------------------------------------------------------------------------------------------------------
for f in SCANNED:
    pg = f[:-len(".jsonl")] + ".txt"
    if not os.path.exists(pg) or "Findings (occurrences / games affected):" not in open(pg, encoding="utf-8", errors="replace").read():
        gate("scan", "every file read has its scan page (section 4.5; a page not in holds the reading)", "PENDING",
             f"no scan page with a Findings block beside {os.path.basename(f)}")
        break
else:
    gate("scan", "every file read has its scan page (section 4.5)", "PASS", f"{len(SCANNED)} files, each with its page; no RULE finding")
for iid, txt in INTEG.items():
    gate(iid, "INTEGRITY LINE (holds the reading; never a registered fail)", "PASS" if EXPLAINED else "PENDING",
         txt + (" -- explained by a human (--integrity-explained)" if EXPLAINED else ""), "integrity")
if not INTEG:
    gate("int", "integrity lines (section 4, K12)", "PASS", "none: every changed game sits where switch 1 reaches, and no "
         "mixed-row game differs where the both-sides games all matched", "integrity")

P("\n8. WHICH CONDITION CARRIED THE VERDICT (5.8; Dustin's column, not a rule): each condition, its result, the changed "
  "games behind it.")
GS = {g[0]: g for g in GATES}


def st_of(gid):
    return GS[gid][2] if gid in GS else "-"


_b2e_ch = COV_CH.get("b2e", (0, 0))
_scz_ch = COV_CH.get("scizor", (0, 0))
_lst_ch = tuple(sum(COV_CH.get(f"var_{v}", (0, 0))[j] for v in VARS) for j in (0, 1))
_lab = LABEL if len(LABELS) == 1 else "PENDING (" + "/".join(sorted(LABELS)) + ")"
rows8 = [("(a) footprint under 15%", ROUTE, f"{FP_D:,} of 22,500 both-sides games on the 45 cells"),
         ("ΔMSE label (5.4)", _lab, f"the same {FP_D:,} games, {RES45:,} of them with a changed result"),
         ("(b) no harm on the 45 cells", f"{st_of('b1')}/{st_of('b2')}", f"{FP_D:,} both-sides games; {MIX_CHANGED45:,} mixed-row games"),
         ("(c) no meta deck worse", st_of("c"), f"{MIX_CHANGED45:,} mixed-row games changed on the 45 cells, both directions"),
         ("coverage: B2e held-out", st_of("cov_b2e"), f"{_b2e_ch[0]:,} both-sides games; {_b2e_ch[1]:,} own-side mixed-row games"),
         ("coverage: Scizor", st_of("cov_scz"), f"{_scz_ch[0]:,} both-sides games; {_scz_ch[1]:,} own-side mixed-row games"),
         ("coverage: second lists", st_of("cov_lst"), f"{_lst_ch[0]:,} both-sides games; {_lst_ch[1]:,} own-side mixed-row games"),
         ("(d) the gain on Rayquaza", st_of("d"), (f"{D_RES[3]:,} of {8 * D_DEALS:,} kta3-arm games differ" if D_RES else "not in yet")),
         ("Jasmine on deck 07", st_of("jas") + (" (gates)" if "spans" in LABELS else " (reported)"),
          (f"{JAS[2]:,} of {AB_GAMES:,} deck-07 games differ" if JAS else "not in yet"))]
for c_, r_, ch_ in rows8:
    P(f"   {c_:32} {r_:22} {ch_}")
P("   'No harm with almost no changed games' is the reserve route working as designed and says little; the informative parts "
  "are the gain on the pre-named deck and the mechanism.")

P("\n9. VERDICT (the registration's section 6, read from the numbers above).")
P(f"   route: {'the reserve route (5.2)' if ROUTE == 'reserve' else 'the ordinary rule (5.3)'}; ΔMSE label: "
  + (LABEL_TEXT[LABEL] if len(LABELS) == 1 else f"PENDING between {' and '.join(sorted(LABELS))} (the --reps {DECISIVE_REPS} rerun decides)"))
for gid, text, st, dt, kind in GATES:
    tag = st
    if gid == "jas" and "spans" not in LABELS:
        tag = f"{st} (reported)"
    P(f"     {tag:18} {text}: {dt}")
RESULT, BYLAB = overall(GATES, LABELS)
FN = fail_names(BYLAB)                                           # {label: failure names} for the labels that FAIL
ALLN = list(dict.fromkeys(n for L in sorted(FN) for n in FN[L]))


def under(name):
    """'' when a failure name holds under every open label; otherwise which label it depends on."""
    ls = [L for L in sorted(LABELS) if name in FN.get(L, [])]
    return "" if len(ls) == len(LABELS) else " (if the label is " + " or ".join(f"'{L}'" for L in ls) + ")"


if RESULT == "ADOPTED":
    how = ("the accuracy clause passed (outcome 1: 'demonstrated on the simulator side; the real side is development data', "
           "3.3) and every clause that gates held" if LABELS == {"below"} else
           "the ΔMSE interval spans zero ('inconclusive at this size') and the fallback's four tests all held: no harm, the "
           "coverage decks, (d) on Rayquaza and the Jasmine line" if LABELS == {"spans"} else
           "every test that gates held under each ΔMSE label still open (" + " and ".join(sorted(LABELS)) + "), so the "
           f"--reps {DECISIVE_REPS} rerun cannot change the outcome; it still fixes which label is recorded")
    P(f"\n   => kta3 is ADOPTED as the working pilot, 'unconfirmed' (section 6): {how}.")
    if ROUTE == "ordinary" and LABELS == {"below"}:
        P("      Confirmation is the ordinary one (5.3 outcome 1): the post-freeze τ̂ margin at least half the margin measured "
          "here, its own 90% interval above zero.")
    else:
        P("      Confirmation is the no-harm re-check at the post-freeze pull (5.7): τ̂ margin 90% lower bound at -1.0 or above on "
          "post-freeze events alone, and no veto.")
    P("      It joins the post-freeze list by a commit to rl/results/postfreeze_2026-09-27/README.md before that data is opened "
      "(5.7). An engine switch (RUN5's procedure) must carry the preset, and settle the name clash with the official "
      "program's kp-based 'kta3', before the screen or the floor use it (section 4, 'Pinning').")
elif RESULT == "NOT ADOPTED":
    if len(LABELS) == 1:
        P(f"\n   => kta3 is NOT ADOPTED; kog stays the working pilot. The test(s) that failed: {', '.join(ALLN)}.")
    else:
        # 5.4: the rerun "decides the label ... The verdict waits for it"; section 6: never an accuracy negative for a
        # result that is only inconclusive. The outcome is settled; the label and the failure name recorded are not.
        P(f"\n   => kta3 is NOT ADOPTED (settled under every open label: {' and '.join(sorted(LABELS))}); kog stays the working "
          f"pilot. The recorded label and failure name wait for the --reps {DECISIVE_REPS} rerun (5.4: that run decides the "
          f"label, and the verdict waits for it). The test(s) that fail under each open label:")
        for L in sorted(LABELS):
            P(f"        [{L}] {', '.join(FN[L])}")
    for L, (res, gs) in BYLAB.items():
        for g in gs:
            P(f"        [{L}] {g[1]}: {g[3]}")
    if "accuracy-worsening" not in ALLN:
        P("      This is never an accuracy negative: the ΔMSE result is " + (
          "'inconclusive at this size'" if LABELS == {"spans"} else "a pass of the accuracy clause" if LABELS == {"below"} else
          "a pass of the accuracy clause or 'inconclusive at this size', whichever the rerun gives")
          + ", and the failure is named by the test that failed.")
    elif len(LABELS) > 1:
        P("      No accuracy negative is recorded: 'accuracy-worsening' is the name only if the rerun gives 'wholly above zero'; "
          "if it gives 'spans zero', the result is 'inconclusive at this size', never an accuracy negative (section 6), and "
          "the failure is named by the test that failed under that label.")
    if "gain" in ALLN and D_RES:
        P(f"      (d){under('gain')} reads 'gain not shown at this size on Rayquaza': {fmt(D_RES[0], D_RES[1])} points, MDE50 "
          f"{1.96 * D_RES[2]:.2f}, MDE80 {2.80 * D_RES[2]:.2f}. It is not evidence that switch 1 does nothing; the Skarmory A/B "
          f"stays a simulator finding about that deck. No override route is created here: any override is Dustin's, recorded as his.")
    if "mechanism" in ALLN:
        P(f"      The Jasmine line{under('mechanism')} reads 'mechanism not shown at this size' (section 7 item 4: the Skarmory "
          "result did not come from the mechanism named, or the deals can't show it).")
    fids = {g[0] for _, (res, gs) in BYLAB.items() if res == "FAIL" for g in gs}
    if ROUTE == "ordinary" and LABELS == {"below"} and fids and fids <= {"b1", "c"}:
        P("      WHICH READING DECIDED (K11): on the ordinary route with ΔMSE wholly below zero this fails only through the τ̂ "
          "bound or (c), which 5.3 outcome 1 does not name and section 6 items 4-5 do; gated here as the conservative reading.")
    if fids and fids <= {"cov_b2e", "cov_scz", "cov_lst"}:
        P(f"      (K14: a coverage veto is the only failure; each own-side test has a one-sided 2.5% chance of vetoing a harmless "
          f"code: {_n_tests} tests with a changed game, 1 - 0.975^{_n_tests} = {1 - 0.975 ** _n_tests:.3f}.)")
    pend_else = [g for g in GATES if g[2] == "PENDING"]
    if pend_else:
        P(f"      Settled whatever is still pending ({len(pend_else)} line(s) above read PENDING): more failed tests may be added to "
          f"the list, but the verdict cannot turn into an adoption.")
elif RESULT == "HELD":
    THEN, THEN_BY = once_explained(GATES, LABELS)
    P(f"\n   => HELD; once explained: {verdict_words(THEN, THEN_BY, LABELS)}. No verdict is recorded, NOT ADOPTED included, "
      f"while a holding line is open (section 4: such a line 'holds the reading (status PENDING, never a registered fail) "
      f"until it is explained'; K12).")
    P("      Held by (an integrity line is released by a human's written explanation, --integrity-explained FILE; a missing "
      "scan page by the page itself, 4.5):")
    for g in holding_lines(GATES):
        P(f"        {g[1]}: {g[3]}")
    if THEN == "ADOPTED":
        P("      Once explained, every other clause as read above gives: kta3 ADOPTED as the working pilot, 'unconfirmed'.")
    else:
        P("      Once explained, every other clause as read above gives:")
        for L, (res, gs) in THEN_BY.items():
            P(f"        if the ΔMSE label is '{L}': {res}" + (": " + "; ".join(f"{g[1]} ({g[3][:160]})" for g in gs) if gs else ""))
else:
    P("\n   => PENDING: nothing that decides has failed on every open label, but the verdict cannot be written yet:")
    for L, (res, gs) in BYLAB.items():
        P(f"        if the ΔMSE label is '{L}': {res}" + (": " + "; ".join(f"{g[1]} ({g[3][:160]})" for g in gs) if gs else ""))
    if len(LABELS) > 1:
        P(f"      The label waits for the --reps {DECISIVE_REPS} rerun of these same games (5.4, fixed before any fresh result).")
if D_RES and D_RES[4] and RESULT == "ADOPTED":
    P(f"   Beside the verdict (5.9, gates nothing): one row supplies more than half of the passing (d) gain: {D_RES[4]}.")
if AB07 is not None:
    m7, h7 = AB07
    if m7 - h7 <= 0:
        P(f"   Beside the verdict (5.6): deck 07's fresh interval ({100 * (m7 - h7):+.1f} to {100 * (m7 + h7):+.1f} points) is not above "
          f"zero, so the reason the candidate exists did not replicate. Reported; it gates nothing. Adoption rests on section 6's "
          f"tests (Rayquaza's gain, no harm, coverage, and Jasmine only in the fallback).")
    else:
        P(f"   Beside the verdict (5.6): deck 07's fresh A/B replicates the reason the candidate exists ({100 * m7:+.1f} points, "
          f"{100 * (m7 - h7):+.1f} to {100 * (m7 + h7):+.1f}). It isn't the gate.")
else:
    P("   Beside the verdict (5.6): deck 07's fresh A/B is not in yet (reported; gates nothing).")
if REPORTED_MISSING:
    P(f"   Reported-only inputs not in yet (they hold nothing): {', '.join(REPORTED_MISSING)}")

P("\n   THE OUTCOMES THE REGISTRATION FIXES (section 6):")
P("     - Adopted only if every applicable test holds: identity (section 4, timing, RULE-free pages, a clean integrity line), "
  "(a) or the ordinary rule's form, ΔMSE not wholly above zero, (b), (c), (d), coverage, and the Jasmine line only when the "
  "ΔMSE interval spans zero; (e) for the screen and the table together.")
P("     - Not adopted if any that applies fails: kog stays the working pilot; the reading names the test that failed (harm, "
  "coverage, gain, mechanism, or accuracy-worsening) and never records an accuracy negative for an inconclusive result.")
P("     - Unchanged by this registration: kt3's 'not adopted, as registered' stands; kt3, ktb3 and ktc3 are not run. A spec "
  "change after any reading is a new code. This registration offers no second fresh round on the same spec.")
P("\n   WHAT STAYS PROVISIONAL, whatever the numbers say:")
P("     - Confirmation at the post-freeze pull (5.7): an adopted kta is the working pilot 'unconfirmed'. The check is read once, "
  "at 804 panel matches and 303 on the new cells, or at the last pull before Mega Garchomp ex, with the size printed; "
  "Rayquaza's and Suicune's post-freeze real cells are reported. A failed check reads 'not confirmed at this size'.")
P("     - The lapse clause (kt item 6): kta carries kog's A and F; until kog's row (and kpg's and koa's) has passed, kta is not "
  "confirmed even if its own check passes.")
P("     - What no number here can show (section 7 item 10): that kta plays closer to the real game. The real side of the 45 "
  "cells is the development half that kta3 was chosen against (3.3).")
P("     - The second reader (RUN5 tier 1) and an outcome audit against the registration are still owed; this is the "
  "laptop's first reader.")
P("     - The footprint is committed alone before the rest is read (5.1); an adoption needs an engine switch before the "
  "screen or the floor use kta (section 4, 'Pinning').")
