#!/usr/bin/env python3
"""km's reading (../REGISTRATION_DRAFT.md: registered Sept 29 with Dustin's word; its top block "Registration (Sept 29,
Dustin's word)" governs, with the dated amendments after it; Amendment 1 (Sept 30) re-issues km on kta). Written BLIND:
before any registered km game was played or read. It reads nothing until footprint.txt exists. It is kta's read_kta.py
(rl/results/kta_2026-09-29/, reviewed and passing its stand-ins) adapted to km: one code, km3 (kta + N2: the lasting
Stadium damage bonus, Training Area and Arena of Antiquity, in kta's threat clock), against kta3, the adopted working
pilot (kog + kt's switch 1 as ec7e1a8 defines it), on the table's own deals (development deals, step 6), paired against
kta3's ec7e1a8 reference files, which the identity at B licenses (Amendment 1 (b) item 3, (c) item 4, (e)).

ONE SET: the candidate and baseline codes, B (and so the file prefix, its first 7 characters), the counter tool's source
sha256, and every reference file with its sha256, pairings, deals and seed base come from km_config.json (read through
km_config.py, --config), the set the runner uses too (Amendment 1 (b) item 3: "The runner and the reader use this set
and no other"). A null required value in it stops the reading. The laptop's program hashes are read from the runner's
programs.txt and its "KM PART B DONE" line in STATUS.txt, which must agree, and from the programs on the disk.
THE ONE LIST ((b) item 4): before anything else is read, the runner's km_inputs.sha256 in --dir is checked by
km_check.py's own code (list_check): its sha256 is the one STATUS.txt's last "KM INPUTS WRITTEN|CHANGED P" line records,
its set (candidate, baseline, B, the tool's source sha256, the eight reference files and the cloud's outputs with their
sha256, the programs) is the config's entry by entry, the config given here is the one it lists (so the reader's config
is the runner's), and every file it lists has its sha256 on the disk. In section 1b, programs.txt must name exactly the
list's three programs. When --dir lies in rl/results (a registered folder), the config must also be committed and
unchanged from HEAD.

The order (section 5; "the baseline" below is kta3, "the candidate" km3):
  1. the footprint (step 1): km3 on both sides of the 45 cells against kta3's reference files, paired by (a, b, i), on
     `moves`. The route comes from the COUNTS (under 15%: the reserve route; 15% or more: the ordinary rule); the reading
     stops if footprint.txt's own route text disagrees. Both routes are written out. 1b: the preconditions (section 4.0):
     the programs, the counter tool's source, the laptop's own identity games at B, the timing line, RULE-free scan
     pages, and thresholds.json with the dated amendment that writes M1's and M2's thresholds in.
  2. the 45 cells by score45.py (rules v2, km3's mixed rows): ΔMSE (km3 minus kta3) with RUN5's three-outcome label and
     its detectable size, on BOTH routes; the τ̂ margin (kta3 minus km3); the rule-v2 vetoes. A ΔMSE bound near 0 at
     either edge, or a τ̂ bound near -1.0, is PENDING below --reps 20000 (step 4, "Near-zero bounds").
  3. clause (c) (gates on the reserve route; reported on the ordinary route): the mixed rows of the cells with a changed
     game, pooled per deck.
  4. clause (d), on BOTH routes: Lucario's 9 rows x 2,000 deals (the table's deals 0-499 plus D2's block 22,900,000,000 -
     22,900,081,499), km3 on Lucario with kta3 on the other deck against kta3 on both, pooled, with the per-row column.
  5. coverage (step 5): B2e (0-47 counted, 48-95 reported), Scizor, the four second lists; own-side mixed rows only where
     km3's both-sides games differ from kta3's (Dustin's rule), read against coverage_skip.txt, whose skips the reader
     re-checks. The held-out direction (step 5b item 4), reported.
  6. the mechanism (step 3): M1 (Arena of Antiquity, Lucario's side, 9 cells) and M2 (Training Area, Altaria's side, the
     five named cells) on deals 0-199, compared exactly with thresholds.json's T, with the kta3 guard; they gate only when
     the ΔMSE interval spans zero (the fallback), on either route. M3 and the sentinels, reported.
  7. reported beside: Altaria (the beside deck), Lucario's and Altaria's real cells, the deck averages.
  8. which condition carried the verdict (step 5b item 2); 9. the verdict, the outcomes section 6 fixes, and what stays
     provisional.
Every input is checked for its full game count, its deals (the seed formulas, the decks, the seat rules) and its pilots:
a wrong file STOPS the reading, naming it. A file not in yet holds only the clauses that need it (they read PENDING).

INPUT CONTRACT (in --dir; P = B's short hash, from the config; C = the candidate, km3; K = the baseline, kta3; the runner
writes these, this only reads):
  footprint.txt      footprint_km.py's output: "FOOTPRINT[ C]: <d> of 22500 paired games on the 45 cells differ from K's[
                     moves] = <x.xx>%" and its route, either after " -> " on that line or on a "ROUTE ...:" line ("RESERVE
                     route ..." / "ORDINARY adoption rule ...").
  km_inputs.sha256   the runner's one list (run_km.sh part I, km_check.py one-list write), with STATUS.txt's "KM INPUTS
                     WRITTEN P <time> km_inputs.sha256 <sha256>" line (or a later dated "KM INPUTS CHANGED P ..." line).
  programs.txt       sha256sum lines "<sha256>  <path>" for the laptop's deckgym, legality_scan and tool_census built from
                     B (each path is hashed here, and lies in a build folder whose COMMIT file is B, outside rl/: never a
                     historical program); STATUS.txt's last "KM PART B DONE P ..." line must give the same three sha256,
                     and km_inputs.sha256 must name the same three programs with the same sha256.
  tool_census.rs     the counter tool's source as built (else --tool-source; else the repo's copy): the config's sha256.
  identity_check.txt the laptop's own identity games at B, "<k> <label>: <n> of <n> [games|deals|files|outputs] equal
                     on ..." per line, checks 1 to 8 of Amendment 1 (e) item 3 (a line with FAIL, or n != m, stops; lines
                     starting "(" or "#" are notes).
  P_timing_1.txt (P_timing_2.txt if the first pair was over)   "... (limit 1.25: within) ..."
  thresholds.json    (or --thresholds FILE) km_thresholds.py's result, as the dated amendment wrote it in:
                     {"tool_source_sha256": "...", "counter_tool": {"program_sha256": ...}, "lines": {"M1": {...}, "M2":
                     {...}}} (the "lines" level may be left out; a line may also be keyed m1 / m2 / its card), each line
                     {"card": ..., "K": {"offered": int, "played": int}, "C": {...}, "interval": [lower, upper], "T":
                     "<num>/<den>" (or {"num","den"} or [num, den]; never a float), "status": "threshold" | "cannot pass"}.
  P_sample_K*.jsonl, P_sample_C*.jsonl  (optional) the threshold sample's raw rows (the counter tool's --rows-out,
                     deals 200-299 of the 14 gating cells); when in, the sums of thresholds.json are recomputed from them.
  both sides, C:     P_C_table.jsonl (14,000; 72,000,000 + pairing x 10,000 + i) and P_C_new17.jsonl (8,500; pairings
                     8-24 of new_decks.tsv; 21,108,000,000 + pairing x 10,000 + i); P_b2e_C.jsonl (48,000; 21,106,000,000
                     + ...); P_scizor_C.jsonl (4,000; 21,108,000,000 + pairing x 10,000 + i, pairings 0-7);
                     P_var_<list>_C.jsonl (500 x rows; each row's seed_first in var_<list>.tsv + i).
  K (not in --dir):  kta3's ec7e1a8 reference files as the config names them, each checked against the config's sha256:
                     table, new17, b2e, scizor and the four var_<list> groups (all on main).
  mixed rows (C on one side, K on the other; any number of files per glob, merged):
                     P_mixed_table_C_first*.jsonl, P_mixed_new17_C_first*.jsonl (C on the first-named deck),
                     P_mixed_table_C_second*.jsonl, P_mixed_new17_C_second*.jsonl (C on the second-named deck):
                     500 deals in every cell with a changed game (both routes);
                     P_mixed_b2e_C_first*.jsonl; P_mixed_scizor_C_first*.jsonl (and _second*, reported only);
                     P_var_<list>_C_mixed_a*.jsonl / _mixed_b*.jsonl: on the pairings whose both-sides games differ.
  coverage_skip.txt  "SKIP|RUN <group> <pairing>: <n> of <n> deals equal on moves, a, b, seed, first_seat" per coverage
                     pairing (groups b2e, scizor, var_<list>; table / new17 lines are optional and checked if present).
  clause (d):        P_d_K*.jsonl (K on both sides) and P_d_C*.jsonl (C on Lucario, K on the other deck),
                     18,000 games each: row r = 0-6 the table pairings 2, 8, 13, 18, 19, 20, 21, r = 7 new_decks 8
                     (Rayquaza v Lucario), r = 8 new_decks 16 (Altaria/Greninja v Lucario). Deals n < 500: the cell's own
                     seed (72,000,000 or 21,108,000,000 + pairing x 10,000 + n), the first-named deck in seat 0 on even n,
                     i = n. Deals n = 500 + j (j < 1,500): seed 22,900,000,000 + r x 10,000 + j, Lucario in seat 0 on even
                     j, i = j (or n). A game's row and deal are read from its seed; its decks must be the row's.
  the counters:      P_counters_K*.jsonl and P_counters_C*.jsonl: the counter tool's --rows-out rows (with counts),
                     deals 0-199 of all 17 named cells (3,400 rows per arm), `--cells km17`.
  scan pages:        <file>.txt beside every legality_scan .jsonl read (its "Findings" block); every *.txt in --dir with a
                     Findings block is scanned for RULE findings.

Usage (WSL):  python3 read_km.py --dir ../../km_tables_<date> > ../../km_tables_<date>/READING_numbers.txt
  --config F        the one set (default: km_config.json beside this file)
  --pages-dir DIR   where score45's page and its composite mixed-row inputs go (default: --dir)
  --reps N          score45's bootstrap (default 4000); the 20,000-rep rerun is what a near-the-line bound asks for
  --reuse-45        reuse score45's page only if made by the same command at the same --reps on inputs with the same
                    sha256 (a sidecar <page>.reps records them)
  --footprint-only  sections 1 and 1b only: the step "the footprint, the first result read, committed alone" (step 1)
  --thresholds F    thresholds.json (default: --dir/thresholds.json)   --registration F  the registration text (default:
                    ../REGISTRATION_DRAFT.md), searched for the dated amendment's numbers
  --tool-source F   the counter tool's source
  --m-reps N        replicates of the REPORTED paired intervals of step 3 (default 2000; they gate nothing)
  --integrity-explained FILE  a human's written explanation of an integrity line; printed in full, and the integrity
                    lines then hold nothing. Never needed for a clean reading.
  --parse-page F    parse one score45 page and stop (reads no km file; a test aid)
  --selftest        the gate logic on canned numbers (reads no file) and stop
"""
import argparse, csv, glob, hashlib, json, math, os, random, re, subprocess, sys, textwrap
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))   # rl/results/trainer_pricing_2026-09-28/km_run
TP = os.path.dirname(HERE)                           # rl/results/trainer_pricing_2026-09-28
RES = os.path.dirname(TP)                            # rl/results
REPO = os.path.dirname(os.path.dirname(RES))

ap = argparse.ArgumentParser(description="km's reading (see the module docstring)")
ap.add_argument("--dir", default=None)
ap.add_argument("--config", default=os.path.join(HERE, "km_config.json"))
ap.add_argument("--pages-dir", default=None)
ap.add_argument("--reps", type=int, default=None)
ap.add_argument("--reuse-45", action="store_true")
ap.add_argument("--footprint-only", action="store_true")
ap.add_argument("--thresholds", default=None)
ap.add_argument("--registration", default=os.path.join(TP, "REGISTRATION_DRAFT.md"))
ap.add_argument("--tool-source", default=None)
ap.add_argument("--m-reps", type=int, default=2000)
ap.add_argument("--integrity-explained", default=None)
ap.add_argument("--parse-page", default=None)
ap.add_argument("--selftest", action="store_true")
args = ap.parse_args()

# The one set (Amendment 1 (b) item 3), read through km_config.py: its names always; its required values (B, the
# cloud's outputs) before any km file is read (below, after the file-free modes).
sys.path.insert(0, HERE)
import km_config  # noqa: E402
try:
    CFG = km_config.load(args.config, require=False)
except km_config.ConfigError as _e:
    sys.exit(f"STOP: the config: {_e}")
DEFAULT_REPS, DECISIVE_REPS = 4000, 20000
REPS = args.reps or DEFAULT_REPS
CODE, BASE = CFG["comparison"]["candidate"], CFG["comparison"]["baseline"]
SEED_TABLE, SEED_NEW, SEED_B2E = (CFG["refs"][g]["seed_base"] for g in ("table", "new17", "b2e"))
D_BLOCK = 22_900_000_000
D_TABLE, D_BLOCKN = 500, 1500
D_DEALS = D_TABLE + D_BLOCKN
# Amendment 1 (e) item 3's sizes: 4,240 games through the scan and 420 counter-tool rows, plus tool tests 3 and 1 (two
# byte-for-byte comparisons each); checks 1 to 8, the baseline and the candidate both in them.
IDENTITY_MIN, IDENTITY_CHECKS = 4240 + 420 + 2 + 2, {"1", "2", "3", "4", "5", "6", "7", "8"}
TOOL_SOURCE_SHA = CFG["counter_tool"]["source_sha256"]   # the config's (Amendment 1 (e) item 2)
PROGRAMS = ("deckgym", "legality_scan", "tool_census")   # the laptop's three programs built from B, pinned by part B
REFS = CFG["refs"]                                       # kta3's ec7e1a8 reference files, by group
VARS = ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy")
# N2's cards, by the ids the lists use (decks/research lists carry ids only): Training Area B2 153, Arena of Antiquity B3 154.
STADIUM_IDS = {"B2 153": "Training Area", "B3 154": "Arena of Antiquity"}
REACH_COUNTS = {"45": 17, "b2e": 42, "scizor": 8, "var": 13}   # section 7 and step 5 (counted from the lists by script)
# clause (d)'s nine rows (step 4 (d)): rows 0-6 Lucario's table cells in increasing pairing number, 7 and 8 the new cells.
D_ROWS = [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21),
          ("new17", 8), ("new17", 16)]
# The counter tool's 17 named cells (--cells km17): source, pairing, first-named, second-named.
KM17 = [("table", 0, "altaria", "blaziken"), ("table", 1, "altaria", "hydreigon"), ("table", 2, "altaria", "lucario"),
        ("table", 3, "altaria", "sceptile"), ("table", 4, "altaria", "suicune"), ("table", 5, "altaria", "vespiquen"),
        ("table", 6, "altaria", "weezing"), ("table", 8, "blaziken", "lucario"), ("table", 13, "hydreigon", "lucario"),
        ("table", 18, "lucario", "sceptile"), ("table", 19, "lucario", "suicune"), ("table", 20, "lucario", "vespiquen"),
        ("table", 21, "lucario", "weezing"), ("new_decks.tsv", 8, "rayquaza", "lucario"),
        ("new_decks.tsv", 9, "rayquaza", "altaria"), ("new_decks.tsv", 16, "altaria_greninja", "lucario"),
        ("new_decks.tsv", 17, "altaria_greninja", "altaria")]
KM17_NAMES = {(s, p): (a, b) for s, p, a, b in KM17}
M = {  # step 3's two lines
    "m1": {"name": "M1", "card": "Arena of Antiquity", "owner": "lucario", "seed": 20260929,
           "cells": [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21),
                     ("new_decks.tsv", 8), ("new_decks.tsv", 16)], "rest": []},
    "m2": {"name": "M2", "card": "Training Area", "owner": "altaria", "seed": 20260930,
           "cells": [("table", 0), ("table", 1), ("table", 3), ("table", 4), ("new_decks.tsv", 9)],
           "rest": [("table", 2), ("table", 5), ("table", 6), ("new_decks.tsv", 17)]},
}
GATE_DEALS, SAMPLE_DEALS = range(0, 200), range(200, 300)
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
    """The τ̂ margin's "90% lower bound at -1.0 or above" (read_kta.py's). -1.00 as printed is never called; within 0.10
    of the line below DECISIVE_REPS is PENDING (step 4, near-zero bounds). Done in whole hundredths of the printout,
    inclusive. Returns (status, notes)."""
    notes, n = [], round(lo * 100)
    gap = abs(n + 100)
    status = "PASS" if n >= -100 else "FAIL"
    if gap == 0:
        status = "PENDING"
        notes.append("BOUNDARY: printed -1.00, so the true bound is within +/-0.005 of the registered line; not called, "
                     "read it by hand at more digits (step 4)")
    elif gap <= 10:
        if reps < DECISIVE_REPS:
            status = "PENDING"
            notes.append(f"MC-BOUNDARY: within 0.10 of the -1.0 line at --reps {reps}; rerun the reader with --reps "
                         f"{DECISIVE_REPS}, and that run decides (step 4, near-zero bounds)")
        else:
            notes.append(f"near the -1.0 line; this --reps {reps} run is the decisive one (step 4)")
    if (ev_lo >= -1.0) != (lo >= -1.0):
        notes.append(("by-event lower bound %+.2f is BELOW -1.0 while the match-level bound is not" if lo >= -1.0 else
                      "by-event lower bound %+.2f is at or above -1.0 while the match-level bound is below it") % ev_lo
                     + " (beside, gates nothing)")
    return status, notes


def dmse_label(lo_s, hi_s, below0, reps, exact_zero=False):
    """RUN5's three outcomes for ΔMSE (the candidate minus the baseline): 'below' (outcome 1: the accuracy clause passes), 'above' (outcome
    2: fails, no fallback), 'spans' (outcome 3: 'undetectable at this size', the fallback). Returns (possible labels, the
    label as printed, notes); more than one possible label means PENDING. read_kta.py's rule, unchanged:
      - the upper edge is decided by score.py's own 'below 0' (the unrounded bound); the lower edge only as printed, and
        a printed '+0.0' is never called;
      - a bound within 5% of the interval's width of 0 is PENDING below --reps 20000, at either edge, tested in whole
        units of the printout's last digit, inclusive; the 20,000-rep rerun decides;
      - exact_zero: no game on the 45 cells changed its result: the interval is the point 0, which spans zero."""
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
    dec = max((len(s.split(".")[1]) if "." in s else 0) for s in (lo_s, hi_s))
    lo_u, hi_u = round(lo * 10 ** dec), round(hi * 10 ** dec)
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


LABEL_TEXT = {"below": "wholly BELOW zero (outcome 1: demonstrated improvement; the accuracy clause passes)",
              "above": "wholly ABOVE zero (outcome 2: demonstrated worsening; km fails on accuracy with no fallback)",
              "spans": "SPANS zero (outcome 3: 'undetectable at this size'; the fallback, with its four tests)"}


def pc(pl, off):
    return f"{100 * pl / off:.1f}%" if off else "n/a"


def fr(T):
    return f"{T.numerator}/{T.denominator}"


def m_gate(line, T, status, k_off, k_pl, g_off, g_pl):
    """Step 3's gate for one line, on the gating deals: km3's rate (played / offered, summed, an exact Fraction) against
    the amendment's exact T; PASS when km3's rate >= T. Not passed: the amendment recorded 'cannot pass'; the guard
    (the baseline's own rate on the same deals already >= T); km3 never offered the card; km3's rate < T. Displayed
    figures are never compared. Returns (status, text)."""
    name, card = M[line]["name"], M[line]["card"]
    ktxt = f"{CODE} {k_pl:,} of {k_off:,}" + (f" = {pc(k_pl, k_off)}" if k_off else " (never offered)")
    gtxt = f"{BASE} {g_pl:,} of {g_off:,}" + (f" = {pc(g_pl, g_off)}" if g_off else " (never offered)")
    if status == "cannot pass":
        return "FAIL", (f"the dated amendment records 'cannot pass' for {name}: {CODE}'s development rate did not exceed "
                        f"{BASE}'s beyond paired noise, so the line cannot pass; its midpoint is not used, adjusted or replaced "
                        f"('mechanism not shown at this size'; on the gating deals {ktxt}; {gtxt})")
    ttxt = f"T = {fr(T)} (= {100 * float(T):.1f}%, displayed only)"
    if g_off > 0 and Fraction(g_pl, g_off) >= T:
        return "FAIL", (f"GUARD: {BASE}'s own rate on the same deals is already at or above {ttxt} ({gtxt}; {ktxt}): the line "
                        f"cannot show the mechanism, 'not shown at this size', so the footprint test is not passed")
    if k_off == 0:
        return "FAIL", f"{CODE} was never offered {card} on these deals ({ktxt}; {gtxt}): 'mechanism not shown at this size'"
    guard = f"guard: {gtxt}, below T" if g_off else f"guard: {BASE} never offered the card, so it cannot be at T"
    if Fraction(k_pl, k_off) >= T:
        return "PASS", f"{ktxt} is at or above {ttxt}, compared exactly; {guard}"
    return "FAIL", f"{ktxt} is below {ttxt}, compared exactly ({gtxt}): 'mechanism not shown at this size'"


def parse_T(x, where):
    """An exact fraction: 'num/den', {'num','den'} / {'numerator','denominator'}, [num, den], or an int. A float is refused
    (Dustin's correction 1: the exact midpoint; round only for display)."""
    if isinstance(x, bool) or x is None:
        die(f"{where}: T is {x!r}, not an exact fraction")
    if isinstance(x, float):
        die(f"{where}: T is the float {x!r}; the registration keeps T as an exact fraction (Dustin's correction 1)")
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        m = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", x.replace(",", ""))
        if not m:
            die(f"{where}: T {x!r} is not 'numerator/denominator'")
        return Fraction(int(m.group(1)), int(m.group(2)))
    if isinstance(x, dict):
        n, d = x.get("num", x.get("numerator")), x.get("den", x.get("denominator"))
    elif isinstance(x, (list, tuple)) and len(x) == 2:
        n, d = x
    else:
        n = d = None
    if not (isinstance(n, int) and isinstance(d, int)) or isinstance(n, bool) or d <= 0:
        die(f"{where}: T {x!r} is not an exact fraction of two integers")
    return Fraction(n, d)


def midpoint(g_pl, g_off, k_pl, k_off):
    return (Fraction(g_pl, g_off) + Fraction(k_pl, k_off)) / 2


def num_re(n):
    return "(?:" + re.escape(str(n)) + "|" + re.escape(f"{n:,}") + ")"


def amendment_has(text, e):
    """The dated amendment's numbers in the registration text: for a threshold line, T's exact fraction (reduced, or as
    the unreduced midpoint of the two sums); for 'cannot pass', one line with the card, 'cannot pass' and km3's offered
    sum. e's arms are keyed "base" (the baseline, kta3) and "cand" (km3), each (offered, played). Returns the form
    found, or None."""
    if e["status"] == "threshold":
        g_pl, g_off, k_pl, k_off = e["base"][1], e["base"][0], e["cand"][1], e["cand"][0]
        forms = [(e["T"].numerator, e["T"].denominator), (g_pl * k_off + k_pl * g_off, 2 * g_off * k_off)]
        for n, d in forms:
            if re.search(rf"(?<![\d,]){num_re(n)}\s*/\s*{num_re(d)}(?![\d,])", text):
                return f"{n}/{d}"
        return None
    k_off = e["cand"][0]
    for ln in text.splitlines():
        if e["card"] in ln and "cannot pass" in ln.lower() and re.search(rf"(?<![\d,]){num_re(k_off)}(?![\d,])", ln):
            return "cannot pass"
    return None


# Which gate applies under which route and ΔMSE label (step 4 and section 6, "Outcomes fixed now"):
#   'above': km fails on accuracy, whatever else says (outcome 2, both routes; handled in decide()).
#   reserve route: (b) [b1 the τ̂ bound, b2 no veto], (c), coverage and (d) gate on 'below' and 'spans'; M1 and M2 only on
#                  'spans' (the fallback's behavioural footprint).
#   ordinary rule: the vetoes (b2), coverage and (d) gate on 'below' and 'spans'; the τ̂ bound (b1) gates only on 'spans'
#                  (the fallback's no-harm test (1)); (c) is reported (section 6 item 3: "route (c) or the vetoes");
#                  M1 and M2 only on 'spans'.
CATEGORY = {"b1": "harm", "b2": "harm", "c": "harm", "cov_b2e": "coverage", "cov_scz": "coverage", "cov_lst": "coverage",
            "d": "gain", "m1": "mechanism", "m2": "mechanism"}


def applies(gid, label, route):
    if gid in ("m1", "m2"):
        return label == "spans"
    if gid == "b1":
        return route == "reserve" or label == "spans"
    if gid == "c":
        return route == "reserve"
    return True


HOLDING = ("scan",)


def holding_lines(gates):
    """The open lines that hold the reading whatever the label: an integrity line and a missing scan page."""
    return [g for g in gates if g[2] == "PENDING" and (g[4] == "integrity" or g[0] in HOLDING)]


def decide(gates, label, route):
    """gates: [(gid, text, status, detail, kind)]. Returns (result, [the deciding gates]); HOLD / FAIL / PENDING / PASS.
    A holding line is checked first, before the 'above' shortcut and before any FAIL."""
    h = holding_lines(gates)
    if h:
        return "HOLD", h
    if label == "above":
        return "FAIL", [("acc", f"ΔMSE ({CODE} minus {BASE}) wholly above zero", "FAIL",
                         "accuracy-worsening: fails on accuracy with no fallback, whatever else passes (outcome 2)", "gate")]
    gs = [g for g in gates if g[4] == "gate" and applies(g[0], label, route)]
    fails = [g for g in gs if g[2] == "FAIL"]
    if fails:
        return "FAIL", fails
    pend = [g for g in gs if g[2] == "PENDING"]
    if pend:
        return "PENDING", pend
    return "PASS", []


def overall(gates, labels, route):
    res = {L: decide(gates, L, route) for L in sorted(labels)}
    kinds = {r[0] for r in res.values()}
    if "HOLD" in kinds:
        return "HELD", res
    if kinds == {"FAIL"}:
        return "NOT ADOPTED", res
    if kinds == {"PASS"}:
        return "ADOPTED", res
    return "PENDING", res


def once_explained(gates, labels, route):
    h = holding_lines(gates)
    return overall([g for g in gates if g not in h], labels, route)


def fail_names(bylab):
    out = {}
    for L, (res, gs) in bylab.items():
        if res == "FAIL":
            out[L] = list(dict.fromkeys("accuracy-worsening" if g[0] == "acc" else CATEGORY.get(g[0], g[0]) for g in gs))
    return out


def verdict_words(result, bylab, labels):
    if result != "NOT ADOPTED":
        return result
    fn = fail_names(bylab)
    if len(labels) == 1:
        return f"NOT ADOPTED ({', '.join(fn[next(iter(labels))])})"
    return ("NOT ADOPTED (settled under every open label; the name waits for the rerun: "
            + "; ".join(f"[{L}] {', '.join(fn[L])}" for L in sorted(labels)) + ")")


SKIP_RE = re.compile(r"^(SKIP|RUN) (\S+) (\d+): (\d+) of (\d+) deals equal\b")


def parse_skip_report(text):
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


def nf(f):
    """A deck file as a comparable path: '../decks/x.txt' and 'decks/x.txt' are the same file."""
    f = f.replace("\\", "/")
    while f.startswith(("../", "./")):
        f = f[3:] if f.startswith("../") else f[2:]
    return f


def equal5(r, s):
    """Dustin's rule: the complete move fingerprint, both decks (and the deck files where both records carry them), the
    seed and the seats. Matching winners alone is not enough."""
    if any(r.get(k) != s.get(k) for k in FIVE) or not r.get("moves"):
        return False
    return all(nf(r[k]) == nf(s[k]) for k in ("a_file", "b_file") if k in r and k in s)


def mv(d):
    n = len(d)
    m = sum(d) / n
    return m, sum((x - m) ** 2 for x in d) / max(n - 1, 1) / n


def pool(parts):
    """Stratified pool over rows (read_koh.py's paired(), score.py side_change): (mean of row means, 95% half-width,
    deals)."""
    q = [mv(d) for d in parts]
    return sum(m for m, _ in q) / len(q), 1.96 * math.sqrt(sum(v for _, v in q)) / len(q), sum(len(d) for d in parts)


def fmt(m, h):
    return f"{m:+.2f} +/- {h:.2f}"


def d_shares(means):
    s = sum(means)
    return None if s <= 0 else [m / s for m in means]


def boot_rate_change(cells_units, reps, seed):
    """REPORTED only: the frozen procedure's paired per-cell resampling (step 3) applied to other deals. cells_units: per
    cell, a list of (baseline offered, baseline played, km3 offered, km3 played). Returns (lower, upper, zero-offered
    replicates)."""
    rng, out, zero = random.Random(seed), [], 0
    for _ in range(reps):
        ko = kp = mo = mp = 0
        for units in cells_units:
            n = len(units)
            for _ in range(n):
                u = units[rng.randrange(n)]
                ko += u[0]
                kp += u[1]
                mo += u[2]
                mp += u[3]
        if ko == 0 or mo == 0:
            out.append(0.0)
            zero += 1
        else:
            out.append(mp / mo - kp / ko)
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps)], zero


def boot_contrast(first, last, reps, seed):
    """REPORTED only: (mean per-cell change over `first`) - (mean per-cell change over `last`), per-cell resampled deals.
    A cell whose arm has no offered turn in a replicate is left out of that replicate's mean."""
    rng, out = random.Random(seed), []

    def change(units):
        ko = kp = mo = mp = 0
        n = len(units)
        for _ in range(n):
            u = units[rng.randrange(n)]
            ko += u[0]
            kp += u[1]
            mo += u[2]
            mp += u[3]
        return None if ko == 0 or mo == 0 else mp / mo - kp / ko
    for _ in range(reps):
        a = [x for x in (change(u) for u in first) if x is not None]
        b = [x for x in (change(u) for u in last) if x is not None]
        out.append((sum(a) / len(a) if a else 0.0) - (sum(b) / len(b) if b else 0.0))
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps)]


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
    """read_kta.py's parser, unchanged: the ΔMSE bounds kept as printed; the veto lines checked against their summary."""
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
    assert f"{100 * 3374 / 22500:.2f}" == "15.00"
    T = tau_gate
    assert T(-1.00, -1.5, 4000)[0] == "PENDING" and T(-1.00, -1.0, 20000)[0] == "PENDING"
    assert T(-0.95, -0.9, 4000)[0] == "PENDING" and T(-1.05, -1.2, 4000)[0] == "PENDING"
    assert T(-0.95, -0.9, 20000)[0] == "PASS" and T(-1.05, -1.2, 20000)[0] == "FAIL"
    assert T(-1.10, -1.2, 4000)[0] == "PENDING" and T(-0.90, -0.9, 4000)[0] == "PENDING"
    assert T(-1.11, -1.2, 4000)[0] == "FAIL" and T(-0.89, -0.9, 4000)[0] == "PASS"
    L = lambda lo, hi, reps=4000, ez=False: dmse_label(lo, hi, float(hi) < 0, reps, ez)[0]  # noqa: E731
    assert L("-1.9", "+0.1") == {"below", "spans"} and L("-0.1", "+1.9") == {"spans", "above"}
    assert L("-1.8", "+0.1") == {"spans"} and L("-2.0", "-0.1") == {"below"} and L("+0.1", "+2.0") == {"above"}
    assert L("-11.0", "-1.4") == {"below"} and L("+2.0", "+9.0") == {"above"} and L("-4.0", "+6.0") == {"spans"}
    assert L("-20.0", "-0.4") == {"below", "spans"} and L("-20.0", "-0.4", 20000) == {"below"}   # ΔMSE upper edge near 0
    assert L("+0.4", "+20.0") == {"spans", "above"} and L("+0.4", "+20.0", 20000) == {"above"}   # ΔMSE lower edge near 0
    assert L("+0.0", "+0.9", 20000) == {"spans", "above"} and L("+0.0", "+0.0", 100, True) == {"spans"}
    # the mechanism lines: exact comparison with T, the guard, 'cannot pass'
    T4 = Fraction(1, 4)
    assert m_gate("m1", T4, "threshold", 100, 25, 100, 20)[0] == "PASS"      # exactly T passes (">= T")
    assert m_gate("m1", T4, "threshold", 100, 24, 100, 20)[0] == "FAIL"
    assert "GUARD" in m_gate("m1", T4, "threshold", 100, 40, 100, 25)[1]    # the baseline exactly at T: the guard
    assert m_gate("m1", T4, "threshold", 100, 40, 100, 24)[0] == "PASS"
    assert m_gate("m1", T4, "threshold", 0, 0, 100, 10)[0] == "FAIL"        # never offered
    assert m_gate("m1", T4, "threshold", 100, 40, 0, 0)[0] == "PASS"        # the baseline never offered: no guard
    assert "cannot pass" in m_gate("m2", None, "cannot pass", 100, 90, 100, 10)[1]
    assert m_gate("m2", None, "cannot pass", 100, 90, 100, 10)[0] == "FAIL"
    T28 = midpoint(22, 100, 34, 100)                                         # 28/100 exactly
    assert T28 == Fraction(7, 25)
    assert f"{100 * 279_999 / 1_000_000:.1f}" == "28.0" and m_gate("m1", T28, "threshold", 1_000_000, 279_999, 100, 22)[0] == "FAIL"
    assert m_gate("m1", T28, "threshold", 1_000_000, 280_000, 100, 22)[0] == "PASS"   # displayed 28.0% either way; exact decides
    assert parse_T("7/25", "t") == T28 and parse_T({"num": 14, "den": 50}, "t") == T28 and parse_T([7, 25], "t") == T28
    for bad in (0.28, "0.28", True):
        try:
            parse_T(bad, "t")
        except SystemExit as e:
            assert "STOP" in str(e.code)
        else:
            raise AssertionError(f"parse_T accepted {bad!r}")
    e = {"status": "threshold", "T": Fraction(7, 25), "base": (100, 22), "cand": (100, 34), "card": "Arena of Antiquity"}
    assert amendment_has("M1: T = 7/25 (28.0%)", e) == "7/25" and amendment_has("T = 5,600/20,000", e) == "5600/20000"
    assert amendment_has("T = 17/25", e) is None and amendment_has("T = 7/250", e) is None
    c = {"status": "cannot pass", "cand": (1234, 300), "base": (1200, 290), "card": "Training Area"}
    assert amendment_has("M2, Training Area: km3 300 of 1,234; cannot pass.", c) == "cannot pass"
    assert amendment_has("M2, Training Area: km3 300 of 1,235; cannot pass.", c) is None
    # the gating table: route x label
    g = lambda gid, st, kind="gate": (gid, gid, st, "", kind)  # noqa: E731
    ok = [g(x, "PASS") for x in ("b1", "b2", "c", "d", "cov_b2e", "cov_scz", "cov_lst")]
    for rt in ("reserve", "ordinary"):
        assert overall(ok + [g("m1", "FAIL"), g("m2", "PASS")], {"below"}, rt)[0] == "ADOPTED"      # M1 reported when below
        assert overall(ok + [g("m1", "FAIL"), g("m2", "PASS")], {"spans"}, rt)[0] == "NOT ADOPTED"  # ... gates in the fallback
        assert overall(ok + [g("m1", "PASS"), g("m2", "PASS")], {"spans"}, rt)[0] == "ADOPTED"
        assert overall(ok + [g("m1", "PASS"), g("m2", "PASS")], {"above"}, rt)[0] == "NOT ADOPTED"  # no fallback
        assert overall([g("d", "FAIL")] + ok[:3] + ok[4:] + [g("m1", "PASS"), g("m2", "PASS")], {"below"}, rt)[0] == "NOT ADOPTED"
        assert overall(ok + [g("m1", "PENDING"), g("m2", "PASS")], {"below"}, rt)[0] == "ADOPTED"
        assert overall(ok + [g("m1", "PENDING"), g("m2", "PASS")], {"spans"}, rt)[0] == "PENDING"
    notau = [g("b1", "FAIL")] + ok[1:] + [g("m1", "PASS"), g("m2", "PASS")]
    assert overall(notau, {"below"}, "reserve")[0] == "NOT ADOPTED" and overall(notau, {"below"}, "ordinary")[0] == "ADOPTED"
    assert overall(notau, {"spans"}, "ordinary")[0] == "NOT ADOPTED"      # τ̂ is the fallback's no-harm test (1)
    noc = ok[:2] + [g("c", "FAIL")] + ok[3:] + [g("m1", "PASS"), g("m2", "PASS")]
    assert overall(noc, {"below"}, "reserve")[0] == "NOT ADOPTED" and overall(noc, {"spans"}, "ordinary")[0] == "ADOPTED"
    held = ok + [g("m1", "PASS"), g("m2", "PASS"), g("int_reach", "PENDING", "integrity"), g("c", "FAIL")]
    assert overall(held, {"below"}, "reserve")[0] == "HELD" and once_explained(held, {"below"}, "reserve")[0] == "NOT ADOPTED"
    assert overall(ok + [g("scan", "PENDING"), g("int", "PASS", "integrity")], {"above"}, "reserve")[0] == "HELD"
    two = [g("d", "FAIL")] + ok[:3] + ok[4:] + [g("m1", "PASS"), g("m2", "PASS")]
    r2 = overall(two, {"spans", "above"}, "reserve")
    assert r2[0] == "NOT ADOPTED" and fail_names(r2[1]) == {"above": ["accuracy-worsening"], "spans": ["gain"]}
    rep = parse_skip_report("x\nSKIP b2e 0: 500 of 500 deals equal on moves, a, b, seed, first_seat\n"
                            "RUN b2e 4: 497 of 500 deals equal on moves, a, b, seed, first_seat\n")
    assert rep["b2e"] == {0: ("SKIP", 500, 500), 4: ("RUN", 497, 500)}
    r = {"moves": "ab", "a": "x", "b": "y", "seed": 1, "first_seat": 0, "first_deck_score": 1.0, "a_file": "../decks/x.txt"}
    assert equal5(r, dict(r)) and equal5(r, {**r, "a_file": "decks/x.txt"}) and not equal5(r, {**r, "first_seat": 1})
    assert not equal5(r, {**r, "moves": "ac"}) and not equal5(r, {**r, "a_file": "decks/z.txt"})
    lo, hi, _ = boot_rate_change([[(2, 1, 2, 2)] * 10], 200, 1)
    assert abs(lo - 0.5) < 1e-12 and abs(hi - 0.5) < 1e-12
    print("selftest ok: route from integers; tau and dMSE boundary logic at both edges; M1/M2 compared with the exact T "
          f"(a rate displayed as T but below it fails), the {BASE} guard at exactly T, 'cannot pass', never offered; T parsed "
          "only as an exact fraction; the amendment's numbers found in the text; the gating table by route and label "
          "(M lines only in the fallback, τ̂ on the ordinary route only in the fallback, (c) only on the reserve route); "
          "holding lines first; per-label failure names; the skip report; the five-field match with deck files")


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
    die("pass --dir, the km tables folder (the runner's output)")

if km_config.missing(CFG):
    die(f"the config {CFG['_path']} has required values not set yet ({', '.join(km_config.missing(CFG))}): B and its "
        f"round are not known, so no km file can be tied to them; nothing is read")
DIR, PX = os.path.abspath(args.dir), CFG["prefix"]
PAGES = os.path.abspath(args.pages_dir or DIR)
# km's one list (Amendment 1 (b) item 4), checked before anything else is read: "every runner and read_km.py take the
# candidate, the baseline, the reference files and the program hashes from that file and from nowhere else, and check it
# before their first game or read ... any other file or hash stops them". The check is km_check.py's (the runner's).
import km_check  # noqa: E402
_ok, LIST_MSG = km_check.list_check(CFG, REPO, DIR)
if not _ok:
    die(f"km's one list: {LIST_MSG}")
LIST_SET = km_check.parse_list(os.path.join(DIR, km_check.LIST_NAME))[0]
if DIR.startswith(os.path.join(RES, "")):   # a registered folder: the config read is the committed one
    _cr = os.path.relpath(os.path.abspath(CFG["_path"]), REPO)
    if _cr.startswith(".."):
        die(f"{DIR} is a registered folder, and the config {CFG['_path']} lies outside the repository: read it with the "
            f"committed km_config.json")
    if (subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch", "--", _cr], capture_output=True).returncode != 0
            or subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--", _cr], capture_output=True).returncode != 0):
        die(f"the config {_cr} is not committed, or differs from HEAD: a registered folder is read with the committed config "
            f"(section 4.0, 'Reading code')")
K45 = os.path.join(RES, "kpf_2026-09-26", "reading")
B2E_DIR = os.path.dirname(os.path.join(REPO, REFS["b2e"]["pairs"]))   # B2e's pairs file's folder (its Limitless cells too)


def path(name):
    return os.path.join(DIR, name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


GATES = []
SCANNED = []
REPORTED_MISSING = []


def gate(gid, text, status, detail, kind="gate"):
    GATES.append((gid, text, status, detail, kind))


def have(name, holds):
    p = path(name)
    if os.path.exists(p):
        return p
    P(f"   not in yet: {name} ({holds})")
    if holds.startswith("reported"):
        REPORTED_MISSING.append(name)
    return None


def globbed(pattern):
    return sorted(f for f in glob.glob(path(pattern)) if f.endswith(".jsonl"))


# ---------------------------------------------------------------------------------------------------------------
# Loading, with the completeness guards.
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
        die(f"{p}: {len(bad)} games are not on their registered deal, e.g. {bad[0]} has seed {r['seed']:,}, expected "
            f"{seed_of(r):,}: a wrong seed base or a wrong pairs file; nothing read from it")
    bad = [k for k, r in rows.items() if not 0 <= r["i"] < max_i]
    if bad:
        die(f"{p}: {len(bad)} games with i outside 0-{max_i - 1}, e.g. {bad[0]}")
    bad = [k for k, r in rows.items() if r["first_seat"] != r["i"] % 2]
    if bad:
        die(f"{p}: {len(bad)} games break the seat rule (even i puts the first-named deck in seat 0), e.g. {bad[0]}")
    if decks_of:
        bad = [k for k, r in rows.items() if (r["a"], r["b"]) != decks_of(r)]
        if bad:
            r = rows[bad[0]]
            die(f"{p}: {len(bad)} games are between other decks than the pairs file's, e.g. {bad[0]}: {(r['a'], r['b'])} "
                f"against {decks_of(r)}")


def load(p, n, bots, mode, seed_of, decks_of=None, max_i=500, scanned=True):
    rows = read_games(p, mode)
    if len(rows) != n:
        die(f"{p}: {len(rows)} games, expected {n}: an incomplete or wrong file, nothing read from it")
    got = {(r["bot_a"], r["bot_b"]) for r in rows.values()}
    if got != {bots}:
        die(f"{p}: pilots {sorted(got)}, expected {bots}")
    check_deals(p, rows, seed_of, decks_of, max_i)
    if scanned:
        SCANNED.append(p)
    return rows


def pinned(group):
    """A baseline reference file (kta3's ec7e1a8 games) by its config group: its sha256 must be the config's, the file the
    identity at B covers (Amendment 1 (b) item 3)."""
    p = os.path.join(REPO, REFS[group]["path"])
    if not os.path.exists(p):
        die(f"{BASE}'s reference file {p} ({group}) is missing")
    got = sha(p)
    if got != REFS[group]["sha256"]:
        die(f"{BASE}'s reference file {p} ({group}) has sha256 {got}, not the config's {REFS[group]['sha256']}: nothing is read")
    return p


def same_deals(p, rows, base, what, subset=False):
    if not subset and rows.keys() != base.keys():
        die(f"{p}: its games are not {what}'s deals ({len(rows.keys() ^ base.keys())} games in only one of the two)")
    extra = [k for k in rows if k not in base]
    if extra:
        die(f"{p}: {len(extra)} games are on deals {what} does not have, e.g. {extra[0]}")
    for fld in ("seed", "a", "b", "first_seat", "a_file", "b_file"):
        bad = [k for k in rows if fld in rows[k] and fld in base[k] and
               (nf(rows[k][fld]) != nf(base[k][fld]) if fld.endswith("_file") else rows[k][fld] != base[k][fld])]
        if bad:
            die(f"{p}: {len(bad)} games differ from {what}'s on '{fld}', e.g. {bad[0]}: {rows[bad[0]][fld]!r} against "
                f"{base[bad[0]][fld]!r}: not the same deals")


def load_mixed(patterns, bots, mode, base, what):
    files = sorted({f for pat in patterns for f in globbed(pat)})
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


def carries(deck_file):
    """The N2 cards a list carries (by id), read from the list itself."""
    p = os.path.join(REPO, nf(deck_file))
    if not os.path.exists(p):
        die(f"deck list {deck_file} not found (needed to know whether N2 can reach its games)")
    txt = open(p, encoding="utf-8", errors="replace").read()
    return {name for cid, name in STADIUM_IDS.items() if re.search(rf"(?<![\w]){re.escape(cid)}(?!\d)", txt)}


# ---------------------------------------------------------------------------------------------------------------
# 1. The footprint, read first.
# ---------------------------------------------------------------------------------------------------------------
P(f"km's reading (rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md, registered Sept 29 with Dustin's word; "
  f"Amendment 1, Sept 30: km re-issued on kta): {CODE} against {BASE}; files {DIR}/{PX}_*; B {CFG['build']['commit']}; "
  f"the config {CFG['_path']} (sha256 {sha(CFG['_path'])[:16]}...)")
P(f"km's one list (Amendment 1 (b) item 4), checked before anything else was read: {LIST_MSG}")
if REPS == DEFAULT_REPS:
    P(f"score45 bootstrap: --reps {REPS} (score.py's default; its seeds are fixed, so a rerun is identical).")
elif REPS < DEFAULT_REPS:
    P(f"WARNING: --reps {REPS} is BELOW score45's default {DEFAULT_REPS}. The ΔMSE 95% and τ̂ 90% bounds that gate move with "
      f"--reps. This is a test setting: DO NOT READ THIS OUTPUT AS THE REGISTERED READING.")
else:
    P(f"NOTE: --reps {REPS} is above score45's default {DEFAULT_REPS} (the rerun a bound near a registered line asks for; "
      f"step 4). The bounds below are this run's.")
FPFILE = path("footprint.txt")
if not os.path.exists(FPFILE):
    die(f"{FPFILE} does not exist. The 45 cells are not finished; the footprint fixes the route and is read first (step 1). "
        f"Nothing else is read.")
P("\n1. THE FOOTPRINT (step 1; footprint.txt, read first; it fixes the route):")
FPL, ROUTE_TXT = None, []
for ln in open(FPFILE, encoding="utf-8").read().splitlines():
    if ln.startswith("FOOTPRINT"):
        P("   " + ln)
        m = re.match(rf"^FOOTPRINT(?: (\w+))?: (\d+) of (\d+) paired games on the 45 cells differ from {re.escape(BASE)}'s(?: moves)? = "
                     r"([\d.]+)%(?: -> (.*))?$", ln)
        if not m:
            die(f"footprint.txt line not in footprint_km.py's format (against {BASE}'s moves): {ln!r}")
        if m.group(1) not in (None, CODE):
            continue
        if FPL:
            die(f"footprint.txt has two FOOTPRINT lines for {CODE}")
        FPL = (int(m.group(2)), int(m.group(3)), float(m.group(4)))
        if m.group(5):
            ROUTE_TXT.append(m.group(5))
    elif ln.startswith("ROUTE"):
        P("   " + ln)
        ROUTE_TXT.append(ln.split(":", 1)[1] if ":" in ln else ln)
    elif ln.startswith("by cell"):
        P("   " + ln[:300] + (" ..." if len(ln) > 300 else ""))
if FPL is None:
    die(f"footprint.txt has no FOOTPRINT line for {CODE}")
FP_D, FP_N, FP_PC = FPL
if FP_N != 22500 or abs(100 * FP_D / FP_N - FP_PC) > 0.006:
    die(f"footprint.txt's {CODE} line is inconsistent ({FP_D} of {FP_N} = {FP_PC}%; the 45 cells have 22,500 paired games)")
ROUTE = route_of(FP_D, FP_N)
if len(ROUTE_TXT) != 1:
    die(f"footprint.txt states its route {len(ROUTE_TXT)} times (expected once, after ' -> ' or on a ROUTE line)")
_rt = ROUTE_TXT[0].strip().lower()
if not _rt.startswith(("reserve", "ordinary")) or _rt.startswith("reserve") != (ROUTE == "reserve"):
    die(f"footprint.txt's route text ({ROUTE_TXT[0].strip()!r}) disagrees with the route its counts give ({ROUTE}: {FP_D} of "
        f"{FP_N}; 15% of {FP_N} is {15 * FP_N // 100} games). Stop and write it down.")

# kta3's reference files (the pairing's baseline; the identity at B licenses them: Amendment 1 (c) item 4, identity 1;
# (e) item 3), as the config names them.
_tk = pinned("table")
_nk = pinned("new17")
_struct = {}
for _f, _grp in ((_tk, "table"), (_nk, "new17")):
    for _ln in open(_f, encoding="utf-8"):
        _g = json.loads(_ln)
        _struct[(_grp, _g["pairing"], _g["i"])] = (_g["a"], _g["b"])
seed_table = lambda r: SEED_TABLE + 10_000 * r["pairing"] + r["i"]  # noqa: E731
seed_new = lambda r: SEED_NEW + 10_000 * r["pairing"] + r["i"]  # noqa: E731
seed_b2e = lambda r: SEED_B2E + 10_000 * r["pairing"] + r["i"]  # noqa: E731


def load45(t_path, n_path, bots, scanned):
    t = load(t_path, REFS["table"]["games"], bots, "abi", seed_table, lambda r: _struct.get(("table", r["pairing"], r["i"])), scanned=scanned)
    n = load(n_path, REFS["new17"]["games"], bots, "abi", seed_new, lambda r: _struct.get(("new17", r["pairing"], r["i"])), scanned=scanned)
    if t.keys() & n.keys():
        die(f"{t_path} and {n_path} overlap")
    return t, n


for _nm in (f"{PX}_{CODE}_table.jsonl", f"{PX}_{CODE}_new17.jsonl"):
    if not os.path.exists(path(_nm)):
        die(f"{_nm} is not in although footprint.txt exists")
BASE_T, BASE_N = load45(_tk, _nk, (BASE, BASE), False)
BASE45 = {**BASE_T, **BASE_N}
NEW_T, NEW_N = load45(path(f"{PX}_{CODE}_table.jsonl"), path(f"{PX}_{CODE}_new17.jsonl"), (CODE, CODE), True)
NEW45 = {**NEW_T, **NEW_N}
same_deals(f"{PX}_{CODE}_table/new17", NEW45, BASE45, f"{BASE}'s 45-cell reference files")
CELLS = list(dict.fromkeys((a, b) for a, b, _ in BASE45))
TABLE_CELLS = set(dict.fromkeys((a, b) for a, b, _ in BASE_T))
if len(CELLS) != 45:
    die(f"{BASE}'s 45-cell reference files hold {len(CELLS)} cells, not 45")
DECKS = sorted({d for c in CELLS for d in c})
CELL_PAIRING = {(r["a"], r["b"]): (("table" if (r["a"], r["b"]) in TABLE_CELLS else "new17"), r["pairing"]) for r in BASE45.values()}
CELL_FILES = {}
for (a, b, i), r in BASE45.items():
    if (a, b) not in CELL_FILES:
        CELL_FILES[(a, b)] = (r.get("a_file") or f"decks/research/{a}.txt", r.get("b_file") or f"decks/research/{b}.txt")
REACH_CELLS = {c for c in CELLS if carries(CELL_FILES[c][0]) or carries(CELL_FILES[c][1])}
if len(REACH_CELLS) != REACH_COUNTS["45"] or any("lucario" not in c and "altaria" not in c for c in REACH_CELLS):
    die(f"N2's reach on the 45 cells is the 17 cells with the panel Altaria or Lucario list (section 7); the lists give "
        f"{len(REACH_CELLS)}")
DIFF45 = [k for k in BASE45 if BASE45[k]["moves"] != NEW45[k]["moves"]]
if len(DIFF45) != FP_D:
    die(f"footprint.txt says {FP_D} games differ; {CODE}'s files and {BASE}'s reference files give {len(DIFF45)}: stop and write it down")
FPC = Counter((a, b) for a, b, _ in DIFF45)
RES45 = sum(1 for k in BASE45 if BASE45[k]["first_deck_score"] != NEW45[k]["first_deck_score"])
ACTIVE = [c for c in CELLS if FPC[c] > 0]
P(f"   cross-check: the moves fields of {CODE}'s files against {BASE}'s reference files reproduce footprint.txt's count ({FP_D:,}); "
  f"{RES45:,} of those games changed their result.")
P(f"   {CODE}: {FP_D:,} of {FP_N:,} = {100 * FP_D / FP_N:.4f}% (15% is {15 * FP_N // 100:,} games) -> "
  f"{'THE RESERVE ROUTE (step 4; under 15%)' if ROUTE == 'reserve' else 'THE ORDINARY RULE (step 4; 15% or more)'}; decided "
  f"from the counts, and footprint.txt's own route text agrees.")
P("   predicted, not chosen (section 7): between about 3% and 17%, no reliable centre, all in the 17 cells that hold the "
  "panel Altaria or Lucario list. Both routes are registered in full; the prediction never picks the route.")
P(f"   cells with a changed game: {len(ACTIVE)} of 45" + (": " + ", ".join(f"{a} v {b} ({FPC[(a, b)]})" for a, b in ACTIVE) if ACTIVE else ""))
OUT_REACH = [c for c in ACTIVE if c not in REACH_CELLS]
INTEG = {}
if OUT_REACH:
    INTEG["int_reach45"] = (f"{sum(FPC[c] for c in OUT_REACH)} changed games in {len(OUT_REACH)} cells whose lists carry no "
                            f"Training Area or Arena of Antiquity: {', '.join(f'{a} v {b}' for a, b in OUT_REACH[:8])}"
                            f"{' ...' if len(OUT_REACH) > 8 else ''}")
    P(f"   INTEGRITY LINE (holds the reading, never a registered fail): {INTEG['int_reach45']}. {CODE} would be doing more "
      f"than N2 (the identity at B, item 5, finds {CODE} equal to {BASE} on these 28 cells).")
else:
    P("   integrity line: every changed game sits in the 17 cells whose lists carry Training Area or Arena of Antiquity.")


# ---------------------------------------------------------------------------------------------------------------
# 1b. Preconditions (section 4.0, "Gate and order"; section 4.1).
# ---------------------------------------------------------------------------------------------------------------
def counter_rows(files, arm, deals, cells, what):
    """The counter tool's rows (--rows-out, with counts): {(source, pairing, i): row}. STOP unless every row is one of the
    named cells' deals exactly once (seed, decks, seats, the tool's own seat order) and carries both seats' counts."""
    rows = {}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for ln in fh:
                if not ln.strip():
                    continue
                r = json.loads(ln)
                miss = [k for k in ("source", "pairing", "a", "b", "i", "seed", "first_seat", "seat_decks", "bots", "moves", "counts")
                        if k not in r]
                if miss:
                    die(f"{f}: a counter row has no {miss} field(s) (a --no-counts run, or not the counter tool's rows?)")
                key = (r["source"], r["pairing"], r["i"])
                if key in rows:
                    die(f"{f}: counter row {key} appears twice ({what})")
                if (r["source"], r["pairing"]) not in cells or KM17_NAMES.get((r["source"], r["pairing"])) != (r["a"], r["b"]):
                    die(f"{f}: counter row {key} ({r['a']} v {r['b']}) is not one of {what}'s cells")
                if r["i"] not in deals:
                    die(f"{f}: counter row {key} is outside {what}'s deals {deals.start}-{deals.stop - 1}")
                base = (SEED_TABLE if r["source"] == "table" else SEED_NEW) + 10_000 * r["pairing"]
                if r["seed"] != base + r["i"]:
                    die(f"{f}: counter row {key} has seed {r['seed']:,}, not {base + r['i']:,} (the cell's registered seed base)")
                if r["first_seat"] != r["i"] % 2 or r["seat_decks"] != ([r["a"], r["b"]] if r["first_seat"] == 0 else [r["b"], r["a"]]):
                    die(f"{f}: counter row {key} breaks the seat rule (even i puts the first-named deck in seat 0)")
                if list(r["bots"]) != [arm, arm]:
                    die(f"{f}: counter row {key} was played by {r['bots']}, not {arm} on both sides")
                if (not isinstance(r["counts"], list) or len(r["counts"]) != 2
                        or [c.get("seat") for c in r["counts"]] != [0, 1] or [c.get("deck") for c in r["counts"]] != r["seat_decks"]):
                    die(f"{f}: counter row {key} does not carry both seats' counts in seat order")
                rows[key] = r
    want = len(cells) * len(deals)
    if len(rows) != want:
        die(f"{what} ({arm}): {len(rows)} rows, expected {want} ({len(cells)} cells x deals {deals.start}-{deals.stop - 1}): "
            f"an incomplete or wrong file, nothing read from it")
    return rows


def rows_against(rows, games, arm_file_what, ref_what):
    """Step 3: a measuring run's rows against a pilot's games, deal by deal, on the move fingerprint, both decks (and the
    deck files where both carry them), the seed and the seats. Any difference STOPS the reading."""
    bad, missing = [], []
    for (src, p, i), r in rows.items():
        k = (r["a"], r["b"], i)
        g = games.get(k)
        if g is None or CELL_PAIRING.get((r["a"], r["b"])) != ("table" if src == "table" else "new17", p):
            missing.append((src, p, i))
            continue
        same = (r["moves"] == g["moves"] and r["seed"] == g["seed"] and r["first_seat"] == g["first_seat"]
                and all(nf(r[f]) == nf(g[f]) for f in ("a_file", "b_file") if f in r and f in g))
        if not same:
            bad.append((src, p, i))
    if bad or missing:
        die(f"{arm_file_what}: {len(bad)} rows differ from {ref_what} on the move fingerprint, decks, seed or seats and "
            f"{len(missing)} have no game there (e.g. {(bad + missing)[0]}): step 3, 'Any difference stops the reading'")


def owner_counts(r, owner, card):
    ent = [c for c in r["counts"] if c.get("deck") == owner]
    if len(ent) != 1:
        die(f"counter row {(r['source'], r['pairing'], r['i'])}: {len(ent)} seats hold {owner}'s list")
    c = ent[0].get("cards", {}).get(card) or {}
    off, pl = c.get("offered", 0), c.get("played", 0)
    if not (isinstance(off, int) and isinstance(pl, int)) or not 0 <= pl <= off:
        die(f"counter row {(r['source'], r['pairing'], r['i'])}: {card} offered {off!r}, played {pl!r}")
    return off, pl


def line_sums(rows, line, deals, cells=None):
    off = pl = 0
    for (src, p) in (cells or M[line]["cells"]):
        for i in deals:
            o, q = owner_counts(rows[(src, p, i)], M[line]["owner"], M[line]["card"])
            off, pl = off + o, pl + q
    return off, pl


def read_thresholds(p):
    try:
        j = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"{p} cannot be read as JSON ({e})")
    lines = j.get("lines", j) if isinstance(j, dict) else None
    if not isinstance(lines, dict):
        die(f"{p}: no 'lines' object")
    out = {}
    for key, spec in M.items():
        e = lines.get(spec["name"], lines.get(key, lines.get(spec["card"])))
        where = f"{os.path.basename(p)} {spec['name']}"
        if not isinstance(e, dict):
            die(f"{where}: the line is not in the file")
        if e.get("card", spec["card"]) != spec["card"]:
            die(f"{where}: card {e.get('card')!r}, not {spec['card']!r}")
        if "cells" in e:
            got = [(c.split(":")[0], int(c.split(":")[1])) if isinstance(c, str) else (c[0], int(c[1])) for c in e["cells"]]
            if got != spec["cells"]:
                die(f"{where}: cells {e['cells']}, not the registration's {[f'{s}:{q}' for s, q in spec['cells']]} in order")
        arms = {}
        for arm in (BASE, CODE):
            a = e.get(arm)
            if not isinstance(a, dict) or not all(isinstance(a.get(k), int) and not isinstance(a.get(k), bool) for k in ("offered", "played")):
                die(f"{where}: no integer offered and played sums for {arm}")
            if not 0 <= a["played"] <= a["offered"]:
                die(f"{where}: {arm} played {a['played']} of {a['offered']}")
            arms[arm] = (a["offered"], a["played"])
        iv = e.get("interval", [e.get("lower"), e.get("upper")])
        if not (isinstance(iv, (list, tuple)) and len(iv) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in iv)):
            die(f"{where}: no numeric interval [lower, upper]")
        status = str(e.get("status", "")).strip().lower().replace("_", " ").replace("can't", "cannot")
        if status not in ("threshold", "cannot pass"):
            die(f"{where}: status {e.get('status')!r}, not 'threshold' or 'cannot pass'")
        (go, gp), (ko, kp) = arms[BASE], arms[CODE]
        T = parse_T(e["T"], where) if e.get("T") is not None else None
        cannot = go == 0 or ko == 0 or not iv[0] > 0
        if status == "threshold":
            if cannot:
                die(f"{where}: says 'threshold' but its lower bound is {iv[0]} (or an offered sum is 0): by the frozen "
                    f"procedure that line 'cannot pass' (step 3, item 5)")
            if T is None:
                die(f"{where}: says 'threshold' but gives no T")
        elif not cannot:
            die(f"{where}: says 'cannot pass' but its lower bound {iv[0]} is above zero and both arms were offered the card")
        if T is not None and go and ko and T != midpoint(gp, go, kp, ko):
            die(f"{where}: T = {fr(T)} is not the exact midpoint of its two rates ({gp}/{go} and {kp}/{ko} give "
                f"{fr(midpoint(gp, go, kp, ko))}): Dustin's correction 1, the exact midpoint")
        out[key] = {"status": status, "T": T, "base": arms[BASE], "cand": arms[CODE], "interval": tuple(iv), "card": spec["card"]}
    ts = j.get("tool_source_sha256")
    if ts is not None and ts != TOOL_SOURCE_SHA:
        die(f"{os.path.basename(p)}: its counter tool's source sha256 {ts} is not the config's {TOOL_SOURCE_SHA}")
    tp_ = (j.get("counter_tool") or {}).get("program_sha256")
    if tp_ not in (None, "not given") and tp_ != PINNED.get("tool_census"):
        die(f"{os.path.basename(p)}: the sample's counter tool was sha256 {tp_}, not the pinned {PINNED.get('tool_census')} "
            f"(programs.txt): the sample and the registered games are not played by the same program")
    return out, j


PINNED = {}   # the laptop's program sha256 by name, from programs.txt (filled by preconditions())


def build_commit_of(p):
    """The COMMIT file of the build folder a program lies in (the runner's <build>/COMMIT), or None."""
    d = os.path.dirname(os.path.abspath(p))
    while d and d != os.path.dirname(d):
        c = os.path.join(d, "COMMIT")
        if os.path.isfile(c):
            return open(c, encoding="utf-8").read().strip()
        d = os.path.dirname(d)
    return None


def preconditions():
    P("\n1b. PRECONDITIONS (section 4.0, 'Gate and order', and section 4.1, as Amendment 1 (e) and (g) re-base them). "
      "Restated from the disk and the runner's files:")
    P("   (not checkable here: Dustin's word on the build, (g) step 3, and his separate go-ahead for the tables; the runner holds them)")
    # programs: programs.txt, the programs on the disk, the build they come from, and part B's STATUS line
    pp = path(CFG["programs"]["pins"])
    if not os.path.exists(pp):
        die(f"{pp} does not exist: the laptop's programs built from B are not recorded, so no km game can be tied to them")
    b_commit = CFG["build"]["commit"]
    for ln in (x.strip() for x in open(pp, encoding="utf-8")):
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^([0-9a-f]{64})\s+\*?(.+)$", ln)
        if not m:
            die(f"programs.txt line not in sha256sum's format: {ln!r}")
        prog, name = m.group(2).strip(), os.path.basename(m.group(2).strip())
        if name not in PROGRAMS:
            continue
        if not os.path.exists(prog):
            die(f"programs.txt names {prog}, which is not on the disk")
        if os.path.abspath(prog).startswith(os.path.join(REPO, "rl") + os.sep):
            die(f"programs.txt names {prog}, a program under rl/ (the official and historical programs live there; their "
                f"kta<N> is the kp-based preset): km is played only by the laptop's build of B (Amendment 1 (d) items 3-4)")
        bc = build_commit_of(prog)
        if bc != b_commit:
            die(f"{prog} lies in a build folder whose COMMIT is {bc!r}, not B {b_commit} (the config's): km's games must "
                f"all be played by the laptop's build of B (Amendment 1 (d) item 3)")
        got = sha(prog)
        if got != m.group(1):
            die(f"{name}: the program on the disk has sha256 {got}, not the {m.group(1)} programs.txt recorded: km's games "
                f"must all be played by the same programs (Amendment 1 (e) item 5); nothing is read")
        PINNED[name] = got
    if set(PINNED) != set(PROGRAMS):
        die(f"programs.txt records {sorted(PINNED)}; it must record {sorted(PROGRAMS)}")
    stp = path("STATUS.txt")
    bl = [ln for ln in (open(stp, encoding="utf-8").read().splitlines() if os.path.exists(stp) else [])
          if ln.startswith(f"KM PART B DONE {PX} ")]
    if not bl:
        die(f"STATUS.txt has no 'KM PART B DONE {PX}' line: the program hashes recorded before the first game ((e) item 3) "
            f"are not there to check programs.txt against")
    mb = re.search(r" deckgym ([0-9a-f]{64}) legality_scan ([0-9a-f]{64}) tool_census ([0-9a-f]{64})", bl[-1])
    if not mb or dict(zip(PROGRAMS, mb.groups())) != PINNED:
        die(f"STATUS.txt's 'KM PART B DONE {PX}' line does not give programs.txt's three sha256: {bl[-1][:300]!r}")
    _pr = km_check.read_programs(pp)
    _pl = {n: tuple(LIST_SET.get(f"program {n}", " ").split(" ", 1)) for n in PROGRAMS}
    if isinstance(_pr, str) or {n: (s, os.path.normpath(os.path.abspath(p))) for n, (s, p) in _pr.items()} != _pl:
        die(f"programs.txt does not name km_inputs.sha256's three programs with their sha256 (the one list, Amendment 1 (b) "
            f"item 4: the program hashes come from it and from nowhere else): {_pr if isinstance(_pr, str) else ''}"
            f"{'' if isinstance(_pr, str) else {n: s[:16] for n, (s, _p) in _pr.items()}} against the list's "
            f"{ {n: v[0][:16] for n, v in _pl.items()} }")
    for name in PROGRAMS:
        P(f"   {name}: {PINNED[name]} (on the disk = programs.txt = STATUS.txt's 'KM PART B DONE {PX}' line = km_inputs.sha256; built from B {b_commit[:7]})")
    P("   The cloud's programs differ by machine (a Rust build embeds its paths); what carries across is B, the counter "
      "tool's source, the games and the tool's outputs, checked as agreement on the tested games (Amendment 1 (e)).")
    ts = args.tool_source or (path("tool_census.rs") if os.path.exists(path("tool_census.rs")) else
                              os.path.join(REPO, CFG["counter_tool"]["source_path"]))
    if not os.path.exists(ts):
        die(f"the counter tool's source {ts} is not found")
    got = sha(ts)
    if got != TOOL_SOURCE_SHA:
        die(f"the counter tool's source {ts} has sha256 {got}, not the config's {TOOL_SOURCE_SHA}: the counts would not be "
            f"the checked tool's (identity 8a); nothing is read")
    P(f"   counter tool source: {os.path.relpath(ts, DIR) if ts.startswith(DIR) else ts}: sha256 = the config's {TOOL_SOURCE_SHA[:16]}...")
    # identity
    ip = path("identity_check.txt")
    if not os.path.exists(ip):
        die(f"{ip} does not exist: the laptop's own identity games at B are not recorded, so no km game is read")
    seen_id, total = [], 0
    for ln in (x.strip() for x in open(ip, encoding="utf-8")):
        if not ln or ln.startswith(("(", "#")):
            continue
        m = re.match(r"^(.+?): (\d+) of (\d+) (?:\w+ )?equal\b", ln)
        if not m:
            die(f"identity_check.txt line not in the runner's format: {ln!r}")
        if m.group(2) != m.group(3) or int(m.group(3)) == 0 or re.search(r"\bFAIL\b", ln):
            die(f"IDENTITY FAILED in identity_check.txt: {ln!r}. Amendment 1 (e) item 4: any difference stops the reading.")
        seen_id.append((m.group(1), int(m.group(3))))
        total += int(m.group(3))
    labels = " ".join(k for k, _ in seen_id)
    checks = {k.split(" ", 1)[0] for k, _ in seen_id}
    if total < IDENTITY_MIN or not IDENTITY_CHECKS <= checks or BASE not in labels or CODE not in labels:
        die(f"identity_check.txt records {total:,} equal games, rows and files over {len(seen_id)} lines, checks "
            f"{sorted(checks)}; the laptop's own identity games at B must be Amendment 1 (e) item 3's checks 1 to 8, "
            f"covering {BASE} and {CODE}, at least {IDENTITY_MIN:,} (4,240 scan games, 420 counter-tool rows, tool tests 3 and 1)")
    P(textwrap.fill(f"identity (the laptop's own games at B, recorded as agreement on the tested games, Amendment 1 (e)): "
                    f"{len(seen_id)} lines, every one equal, {total:,} games, rows and files: " +
                    "; ".join(f"{k} {n:,}" for k, n in seen_id), width=118, initial_indent="   ", subsequent_indent="      "))
    tp = next((q for q in (path(f"{PX}_timing_2.txt"), path(f"{PX}_timing_1.txt")) if os.path.exists(q)), None)
    if tp is None:
        die(f"neither {PX}_timing_1.txt nor {PX}_timing_2.txt exists: section 4.1's timing run is not recorded")
    tl = " ".join(open(tp, encoding="utf-8").read().split())
    P(f"   timing ({os.path.basename(tp)}" + ("; the second pair decides" if tp.endswith("_2.txt") else "") + f"): {tl}")
    if "limit 1.25: within" not in tl:
        die(f"the timing line is not 'within' the 1.25x limit ({tl!r}): section 4.1, 'Timing (gates, as in kt)'; nothing is read")
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
        die(f"a RULE finding in a scan page (it stops the reading): {rule[0]}" + (f" (and {len(rule) - 1} more)" if len(rule) > 1 else ""))
    P(f"   RULE findings: none in the {pages} scan pages in the folder (each page beside a file read is checked in section 9).")


preconditions()

# The thresholds (step 3; section 4.0 steps 5-8: written in by a dated amendment before any registered km game).
THP = os.path.abspath(args.thresholds or path("thresholds.json"))
if not os.path.exists(THP):
    die(f"{THP} does not exist: M1's and M2's thresholds are written in by a dated amendment before any registered km game "
        f"(section 4.0 step 8); a km game read without them was played out of order")
TH, TH_RAW = read_thresholds(THP)
REG_TEXT = open(args.registration, encoding="utf-8").read() if os.path.exists(args.registration) else die(
    f"the registration {args.registration} is not found")
P(f"   thresholds.json ({THP}): km_thresholds.py sha256 {str(TH_RAW.get('km_thresholds_py_sha256', TH_RAW.get('km_thresholds_sha256', 'not given')))[:16]}...; the "
  f"counter tool's source " + ("= the config's" if TH_RAW.get("tool_source_sha256") else "not given") + "; its program "
  + ("= the pinned tool_census" if (TH_RAW.get("counter_tool") or {}).get("program_sha256") not in (None, "not given") else "not given"))
for key, e in TH.items():
    (go, gp), (ko, kp), iv = e["base"], e["cand"], e["interval"]
    found = amendment_has(REG_TEXT, e)
    if found is None:
        die(f"thresholds.json's {M[key]['name']} ({e['status']}" + (f", T = {fr(e['T'])}" if e["T"] is not None else "") +
            f") is not in the registration text ({args.registration}): the dated amendment that writes it in is not there "
            f"(section 4.0 step 8); no registered km game should have been played")
    P(f"   {M[key]['name']} ({e['card']}): sample {BASE} {gp:,} of {go:,} = {pc(gp, go)}, {CODE} {kp:,} of {ko:,} = {pc(kp, ko)}; "
      f"paired interval {iv[0]:+.4f} to {iv[1]:+.4f}; " + (f"T = {fr(e['T'])} = {100 * float(e['T']):.1f}% (displayed; "
      f"compared exactly)" if e["status"] == "threshold" else "CANNOT PASS (recorded; the midpoint is not used)")
      + f"; in the amendment ({found})")
# The sample's raw rows, when in: the sums are recomputed from them (the independent check is its own committed file).
_sk, _sx = globbed(f"{PX}_sample_{BASE}*.jsonl"), globbed(f"{PX}_sample_{CODE}*.jsonl")
SAMPLE_CELLS = set(M["m1"]["cells"] + M["m2"]["cells"])
if bool(_sk) != bool(_sx):
    die(f"only one arm of the threshold sample's rows is in ({BASE if _sk else CODE}): both or neither")
if _sk:
    SK = counter_rows(_sk, BASE, SAMPLE_DEALS, SAMPLE_CELLS, "the threshold sample")
    SX = counter_rows(_sx, CODE, SAMPLE_DEALS, SAMPLE_CELLS, "the threshold sample")
    rows_against(SK, BASE45, f"the threshold sample's {BASE} arm", f"{BASE}'s reference files")
    rows_against(SX, NEW45, f"the threshold sample's {CODE} arm", f"{CODE}'s own games on the same deals (the footprint run)")
    for key, e in TH.items():
        g_ = line_sums(SK, key, SAMPLE_DEALS)
        k_ = line_sums(SX, key, SAMPLE_DEALS)
        if (g_, k_) != (e["base"], e["cand"]):
            die(f"thresholds.json's {M[key]['name']} sums ({BASE} {e['base'][1]}/{e['base'][0]}, {CODE} {e['cand'][1]}/{e['cand'][0]}) are "
                f"not the sample rows' ({BASE} {g_[1]}/{g_[0]}, {CODE} {k_[1]}/{k_[0]}): stop and write it down")
    P(f"   the threshold sample's rows are in: both arms checked deal by deal ({BASE} against its reference files, {CODE} against its "
      f"footprint games) and every sum of thresholds.json recomputed from them, equal. (The interval is the independent "
      f"check's to recompute, not this reader's.)")
else:
    P("   the threshold sample's rows are not in this folder: thresholds.json is read as the amendment wrote it in (its sums, "
      "T and label checked for consistency above; the independent check is its own committed file).")

if args.footprint_only:
    P("\n(--footprint-only: stopped after the footprint and its preconditions, as step 1 has it: read and committed alone.)")
    sys.exit(0)


def integrity_note():
    if args.integrity_explained:
        if not os.path.exists(args.integrity_explained) or not open(args.integrity_explained, encoding="utf-8").read().strip():
            die(f"--integrity-explained {args.integrity_explained}: no such file, or it is empty")
        return open(args.integrity_explained, encoding="utf-8").read().strip()
    return None


EXPLAINED = integrity_note()

NOTES = f"""
NOTES: where the registration's text needs a coding, and the one coded ({CODE} against {BASE}, Amendment 1 (b) item 2)
 K1  Frame. The 45-cell block of score45.py gates; its 44-cell decision set (Altaria v Sceptile quarantined) is compared
     beside on the ΔMSE label, the τ̂ bound and the vetoes that count; a difference is a note and gates nothing.
 K2  The event-resampled intervals are printed beside and gate nothing; the match-level ones gate.
 K3  The route comes from the integers of footprint.txt (100 d < 15 n is the reserve route) and its own route text must
     agree; the files themselves must reproduce its count.
 K4  What gates under which route and ΔMSE label (step 4; section 6, "Outcomes fixed now"): wholly above zero fails on
     accuracy, no fallback, both routes. Reserve route: (b) (the τ̂ bound and no veto), (c), coverage and (d) gate when
     the label is 'below' or 'spans'; M1 and M2 only on 'spans'. Ordinary rule: the vetoes, coverage and (d) gate on
     'below' and 'spans'; the τ̂ bound gates only on 'spans' (the fallback's no-harm test (1)); (c) is reported (section
     6 item 3: harm is "route (c) or the vetoes"); M1 and M2 only on 'spans'.
 K5  (c): per meta deck, pooled over its cells where km3's footprint is not zero, both seat orders, worse = the pooled 95%
     interval wholly below zero. A zero-footprint cell's mixed rows are read as {BASE}'s games (a pilot's choice is a
     function of the position; the identity at B, item 5, finds km3 = {BASE} on the 28 cells without either Stadium); a
     mixed-row game run there that differs from {BASE}'s is an INTEGRITY line. km's registration names no i<40 sample.
 K6  (d) (step 4 (d)): Lucario's 9 rows, 2,000 deals each (500 on the table's seeds + 1,500 on D2's block), km3 on
     Lucario with {BASE} on the other deck against {BASE} on both; Lucario's own-side score whichever seat; the equal-weight
     mean of the per-row mean differences, half-width 1.96 x sqrt(sum of per-row variances of the mean difference) / 9
     (read_koh.py's paired()); passes when mean minus half-width is above zero; read once, on both routes. Each game's row
     and deal are read from its seed; the block's seat rule is Lucario in seat 0 on even j. (d)'s {BASE} arm on deals 0-499
     must replay {BASE}'s reference games (moves, seed, seats): a difference STOPS (section 4.1 item 9).
 K7  The ΔMSE label: the upper edge from score.py's own "below 0"; the lower edge only as printed ("+0.0" is not called);
     no changed result on the 45 cells: the interval is the point 0, which spans zero.
 K8  Near-zero bounds (step 4): a ΔMSE bound within 5% of the interval's width of 0 (either edge) and a τ̂ bound within
     0.10 of -1.0 are PENDING below --reps 20000; the 20,000-rep rerun (the same games) decides. Inclusive, in whole units
     of the printout.
 K9  Coverage mixed rows (Dustin's rule, registration item 7): a pairing may be skipped only when every one of its deals
     has km3's both-sides game equal to {BASE}'s on the move fingerprint, both decks (and deck files), the seed and the
     seats. The reader checks that itself for every pairing; a skipped pairing counts as no change and must be named in
     coverage_skip.txt. A pairing named as skipped whose deals differ, a skipped pairing not named, or a pairing whose
     deals differ without its mixed rows holds its coverage test (PENDING, named). A mixed-row game that differs in a
     pairing whose both-sides games all matched is an INTEGRITY line.
 K10 M1 and M2 (step 3): pooled over the line's cells on deals 0-199, the owner's side only (Lucario's for Arena,
     Altaria's for Training Area): turns played summed over turns offered summed, an exact Fraction, compared with
     thresholds.json's exact T (Fraction against Fraction, never rounded; displayed to one decimal only); PASS when km3's
     rate >= T. Not passed: 'cannot pass' in the amendment (the midpoint is then not used), the guard ({BASE}'s own rate on
     the same deals >= T, 'not shown at this size'), km3 never offered the card, or km3's rate < T. thresholds.json must
     agree with itself (T is the exact midpoint of its two sample rates; 'cannot pass' exactly when its lower bound is not
     above zero or an offered sum is 0), with the registration's dated amendment (T's fraction, or 'cannot pass' with the
     card and km3's offered sum, in the text), and with the sample's raw rows when they are in the folder.
 K11 Counter rows (step 3): every measuring run's {BASE} arm is checked deal by deal against {REFS['table']['file']} and
     {REFS['new17']['file']} (moves, both decks, seed, seats) and its km3 arm against km3's own 45-cell games; any
     difference STOPS. A km3 row whose moves equal {BASE}'s on the same deal but whose counts differ is an INTEGRITY line
     (the counts are a function of the game).
 K12 Integrity lines hold the reading (HELD), never fail it, and are read before anything that decides, 'wholly above
     zero' and every FAIL included; the verdict they would allow is printed beside. A file read without its scan page
     holds the same way. --integrity-explained FILE records a human's explanation, printed in full.
 K13 Preconditions (Amendment 1 (e)): programs.txt (the laptop's hashes; every program on the disk equal to them, in a
     build folder of B, outside rl/; STATUS.txt's part B line giving the same three); the counter tool's source sha256 =
     the config's; identity_check.txt (the laptop's own identity games at B, (e) item 3's checks 1 to 8, every line
     equal, {BASE} and km3, at least {IDENTITY_MIN:,}: agreement on the tested games); the timing line within 1.25x;
     every scan page RULE-free; thresholds.json and its amendment (its counter-tool program = the pinned one). {BASE}'s
     reference files are checked against the config's sha256. Before any of it, km's one list (km_inputs.sha256,
     (b) item 4): recorded by STATUS.txt, its set the config's, the config read the one it lists, every file it lists
     unchanged; programs.txt names its three programs.
 K14 Step 5's count: every own-side no-harm test with a changed game behind it is counted, and 1 - 0.975^n printed.
"""
P(NOTES)
if EXPLAINED:
    P("INTEGRITY LINES EXPLAINED BY A HUMAN (--integrity-explained " + args.integrity_explained + "), in full:")
    P(textwrap.indent(EXPLAINED, "   | "))

# ---------------------------------------------------------------------------------------------------------------
# 2. The 45 cells: score45.py (rules v2), with km3's mixed rows.
# ---------------------------------------------------------------------------------------------------------------
P(f"\n2. THE 45 CELLS (score45.py --rules v2; {BASE} current (its reference files), {CODE} new; paired by deal; {CODE}'s mixed rows).")
MIXR, MIX_FILES = {}, {}
for dr, bots in (("first", (CODE, BASE)), ("second", (BASE, CODE))):
    MIXR[dr], MIX_FILES[dr] = load_mixed([f"{PX}_mixed_table_{CODE}_{dr}*.jsonl", f"{PX}_mixed_new17_{CODE}_{dr}*.jsonl"],
                                         bots, "abi", BASE45, f"{BASE}'s 45-cell reference files")
    P(f"   mixed rows, {CODE} on the {dr}-named deck: " + (f"{len(MIXR[dr]):,} games in {len(MIX_FILES[dr])} file(s)" if MIXR[dr] is not None else "not in yet"))
EFF45, SRC45 = {}, {}
C_MISSING, ZERO_DIFF, MIX_CHANGED45 = [], [], 0
for dr in ("first", "second"):
    rows = MIXR[dr] or {}
    eff, src = {}, {}
    present = defaultdict(set)
    for (a, b, i) in rows:
        present[(a, b)].add(i)
    for c in CELLS:
        keys = [(c[0], c[1], i) for i in range(500)]
        if present[c] == set(range(500)):
            eff.update({k: rows[k] for k in keys})
            src.update({k: "run" for k in keys})
        elif FPC[c] > 0:
            C_MISSING.append(f"{c[0]} v {c[1]} ({dr}: {len(present[c])} of 500 deals)")
        else:
            eff.update({k: BASE45[k] for k in keys})
            src.update({k: f"{BASE} (zero-footprint cell, K5)" for k in keys})
        for i in present[c]:
            k = (c[0], c[1], i)
            if rows[k]["moves"] != BASE45[k]["moves"]:
                MIX_CHANGED45 += 1
                if FPC[c] == 0:
                    ZERO_DIFF.append((dr, k))
    EFF45[dr], SRC45[dr] = eff, src
if ZERO_DIFF:
    zc = sorted({f"{k[0]} v {k[1]}" for _, k in ZERO_DIFF})
    INTEG["int_zero45"] = (f"{len(ZERO_DIFF)} mixed-row games in {len(zc)} zero-footprint cells differ from {BASE}'s moves: "
                           f"{', '.join(zc[:8])}{' ...' if len(zc) > 8 else ''}")
    P(f"   INTEGRITY LINE (holds the reading, never a registered fail): {INTEG['int_zero45']} (K5, K12).")
elif any(MIXR[d] is not None for d in MIXR):
    P(f"   integrity: every mixed-row game run in a zero-footprint cell equals {BASE}'s moves.")
if C_MISSING:
    P(f"   the mixed rows the registration needs are not all in ({len(C_MISSING)}): " + "; ".join(C_MISSING[:6]) + (" ..." if len(C_MISSING) > 6 else ""))


def write_composite(dr, bots):
    os.makedirs(os.path.join(PAGES, "score45_inputs"), exist_ok=True)
    out = os.path.join(PAGES, "score45_inputs", f"{PX}_{CODE}_mixed_{dr}_composite.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for k in sorted(EFF45[dr]):
            r = dict(EFF45[dr][k])
            r["bot_a"], r["bot_b"], r["mixed_source"] = bots[0], bots[1], SRC45[dr][k]
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return out


def run_score45(with_mixed):
    old_p = [_tk, _nk]
    new_p = [path(f"{PX}_{CODE}_table.jsonl"), path(f"{PX}_{CODE}_new17.jsonl")]
    mixed = [write_composite(dr, bots) for dr, bots in (("first", (CODE, BASE)), ("second", (BASE, CODE)))
             if with_mixed and MIXR[dr] is not None]
    page = os.path.join(PAGES, f"score45_{CODE}_vs_{BASE}.txt")
    cmd = [sys.executable, os.path.join(K45, "score45.py"), "--rules", "v2", "--old-games"] + old_p + ["--new-games"] + new_p + \
          ["--old", BASE, "--new", CODE] + (["--mixed"] + mixed if mixed else []) + ["--reps", str(REPS)]
    sig = json.dumps({"reps": REPS, "args": [os.path.basename(x) for x in cmd[2:]],
                      "inputs": {os.path.basename(q): sha(q) for q in old_p + new_p + mixed}}, sort_keys=True)
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
  + (", ".join(os.path.basename(m) for m in MIXED_IN) or "none in yet") + f" (the runner's games in the cells it ran; {BASE}'s in a zero-footprint cell, K5)")
TAU_K = A["real"][BASE]
P(f"   real error on the 45 cells: {BASE} {TAU_K:.1f} -> {CODE} {A['real'][CODE]:.1f}")
dm = A["dmse"]
LABELS, LABEL, LNOTES = dmse_label(dm[4], dm[5], dm[3], REPS, exact_zero=(RES45 == 0))
P(f"   ΔMSE ({CODE} minus {BASE}): {dm[0]:+.1f} points^2, 95% interval {dm[4]} to {dm[5]}; by event (beside): "
  f"{A['dmse_ev'][0]:+.1f} to {A['dmse_ev'][1]:+.1f}")
P(f"   LABEL (RUN5's three outcomes, on the {ROUTE} route): {LABEL_TEXT[LABEL]}" + ("" if len(LABELS) == 1 else
  f"  -- PENDING: the label can still be {' or '.join(sorted(LABELS))}"))
for x in LNOTES:
    P("     " + x)
SD45 = (dm[2] - dm[1]) / 3.92


def as_real(delta):
    v = TAU_K ** 2 + delta
    return math.sqrt(v) if v > 0 else float("nan")


P(f"   detectable size (step 5b item 1): the interval's sd {SD45:.1f}; MDE50 (1.96 sd) {1.96 * SD45:.1f} points^2, as real "
  f"error {TAU_K:.2f} -> {as_real(-1.96 * SD45):.2f}; MDE80 (2.80 sd) {2.80 * SD45:.1f}, as real error {TAU_K:.2f} -> "
  f"{as_real(-2.80 * SD45):.2f} (real error after = sqrt({BASE}'s^2 - δ)). A gain below it reads 'undetectable at this size'.")
P("   expected sign (step 4, stated before any game): ΔMSE is expected POSITIVE if N2 gains on Lucario (the simulator already "
  "over-rates Lucario, 52.2 against 45.6 real, the same at the printed precision on either base: Amendment 1 (b) item 5); "
  "outcome 2 applies to km's own mechanism on both routes.")
t = A["tau"]
SDT = (t[2] - t[1]) / (2 * 1.645)
P(f"   τ̂ margin ({BASE} minus {CODE}): {t[0]:+.2f}, 90% interval {t[1]:+.2f} to {t[2]:+.2f}; by event (beside) "
  f"{A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f}; sd {SDT:.3f}. " + ("It is (b)'s no-harm test on the reserve route."
  if ROUTE == "reserve" else "On the ordinary rule it gates only in the fallback (test (1), no harm)."))
veto_txt = "; ".join(f"{w} (+{g:.1f}) {txt[:200]}" for w, g, k, txt in A["veto"] if k in ("COUNTS", "AWAITS")) or "none"
P(f"   rule-v2 vetoes that count or await mixed rows: {veto_txt}")
inv = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "investigation item"]
nev = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "never counts"]
P(f"   investigation items (neither side worse): {', '.join(inv) or 'none'}; never count (band over +/-15): {', '.join(nev) or 'none'}")
st, notes = tau_gate(t[1], A["tau_ev"][0], REPS)
gate("b1", f"no harm: the τ̂ margin ({BASE} minus {CODE}) 90% lower bound at -1.0 or above", st,
     f"{t[1]:+.2f} (margin {t[0]:+.2f}, interval {t[1]:+.2f} to {t[2]:+.2f}; by event {A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f})"
     + "".join("; " + x for x in notes))
if A["counts"]:
    st, dt = "FAIL", "counts: " + "; ".join(v[0] for v in A["counts"])
elif A["awaits"]:
    st, dt = "PENDING", "awaits mixed rows: " + "; ".join(v[0] for v in A["awaits"])
else:
    st, dt = "PASS", "none counts" + (f" ({len(A['veto'])} veto candidates, all investigation items or never-count)" if A["veto"] else "")
gate("b2", "no harm: no rule-v2 veto counts on the 45 cells (through the mixed rows)", st, dt)
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
  f"both directions, 500 deals, pooled per deck (K5). " + ("It gates on the reserve route." if ROUTE == "reserve" else
  "On the ordinary rule it is REPORTED: the harm test there is the vetoes (K4)."))


def own_deltas(deck, cell):
    a, b = cell
    dr, sign = ("first", 1) if deck == a else ("second", -1)
    return [sign * 100 * (EFF45[dr][(a, b, i)]["first_deck_score"] - BASE45[(a, b, i)]["first_deck_score"]) for i in range(500)]


def deck_report(deck, cells):
    parts = [own_deltas(deck, c) for c in cells]
    m, h, n = pool(parts)
    return m, h, n, {c: (mv(p)[0], 1.96 * math.sqrt(mv(p)[1])) for c, p in zip(cells, parts)}


C_TESTS = []
MIX_READY = MIXR["first"] is not None and MIXR["second"] is not None and not C_MISSING
if MIXR["first"] is None or MIXR["second"] is None:
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "PENDING", "the 45 cells' mixed rows are not in yet")
    P("   the mixed rows are not in yet: (c) waits.")
elif C_MISSING:
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "PENDING", "mixed rows needed and not in: " + "; ".join(C_MISSING)[:300])
    P("   (c) waits: " + "; ".join(C_MISSING)[:600])
else:
    worse, lines = [], []
    for deck in DECKS:
        cells = [c for c in ACTIVE if deck in c]
        if not cells:
            continue
        m, h, n, per = deck_report(deck, cells)
        ch = sum(1 for c in cells for dr, who in (("first", c[0]), ("second", c[1])) if who == deck
                 for i in range(500) if EFF45[dr][(c[0], c[1], i)]["moves"] != BASE45[(c[0], c[1], i)]["moves"])
        if ROUTE == "reserve":
            C_TESTS.append((deck, ch))
        bad = m + h < 0
        if bad:
            worse.append(deck)
        lines.append(f"   {deck:>17}: own side {fmt(m, h)} over {len(cells)} cells ({n:,} deals; {ch:,} mixed-row games changed)"
                     + ("  <- WORSE beyond noise" if bad else ""))
        for cell, (mm, hh) in per.items():
            if mm + hh < 0:
                lines.append(f"{'':21}(listed, gates nothing) {cell[0]} v {cell[1]}: {fmt(mm, hh)}")
    P("\n".join(lines) if lines else f"   no cell has a changed game: nothing to read (every mixed row is {BASE}'s game).")
    gate("c", "(c) no meta deck's own side worse beyond paired noise", "FAIL" if worse else "PASS",
         ("worse: " + ", ".join(worse)) if worse else f"{len(ACTIVE)} cells with a changed game read, no deck worse")

# ---------------------------------------------------------------------------------------------------------------
# 4. Clause (d): Lucario, 9 rows x 2,000 deals, on both routes.
# ---------------------------------------------------------------------------------------------------------------
P(f"\n4. CLAUSE (d), the gain on the pre-named deck, Mega Lucario ex Lucario: 9 rows x {D_DEALS:,} deals per arm (the table's "
  f"deals 0-499 plus D2's block 22,900,000,000 - 22,900,081,499), {CODE} on Lucario with {BASE} on the other deck against {BASE} "
  f"on both; gates on BOTH routes; read once (step 4 (d)).")
D_CELL = []
for grp, p_ in D_ROWS:
    ab = _struct.get((grp, p_, 0))
    if ab is None or "lucario" not in ab:
        die(f"clause (d)'s row {grp} pairing {p_} is not a Lucario cell in {BASE}'s reference files")
    D_CELL.append(ab)
D_OTHER = [a if b == "lucario" else b for a, b in D_CELL]


def d_locate(f, g):
    """(row, deal n) of one (d) game from its seed; STOP unless its decks, seats and i are the row's (K6)."""
    s, key = g["seed"], (g.get("pairing"), g.get("i"))
    if D_BLOCK <= s < D_BLOCK + 10_000 * len(D_ROWS):
        r, j = divmod(s - D_BLOCK, 10_000)
        if j >= D_BLOCKN:
            die(f"{f}: game {key} has seed {s:,}, past the block's 1,500 deals of row {r}")
        if {g["a"], g["b"]} != {"lucario", D_OTHER[r]}:
            die(f"{f}: game {key} (seed {s:,}, row {r}) is {g['a']} v {g['b']}, not Lucario v {D_OTHER[r]}")
        lseat = g["first_seat"] if g["a"] == "lucario" else 1 - g["first_seat"]
        if lseat != j % 2:
            die(f"{f}: game {key} (seed {s:,}) has Lucario in seat {lseat}; the block puts Lucario in seat 0 on even j (D2)")
        if g["i"] not in (j, D_TABLE + j):
            die(f"{f}: game at seed {s:,} has i {g['i']}, not the block's j = {j} (or {D_TABLE + j})")
        return r, D_TABLE + j
    for r, (grp, p_) in enumerate(D_ROWS):
        lo = (SEED_TABLE if grp == "table" else SEED_NEW) + 10_000 * p_
        if lo <= s < lo + D_TABLE:
            n = s - lo
            first, second = D_CELL[r]
            if {g["a"], g["b"]} != {first, second}:
                die(f"{f}: game {key} (seed {s:,}) is {g['a']} v {g['b']}, not row {r}'s {first} v {second}")
            fseat = g["first_seat"] if g["a"] == first else 1 - g["first_seat"]
            if fseat != n % 2 or g["i"] != n:
                die(f"{f}: game {key} (seed {s:,}) breaks the table's seat rule or its i (first-named deck in seat 0 on even i)")
            return r, n
    die(f"{f}: a game at seed {s:,} ({g['a']} v {g['b']}) is on none of (d)'s deals (the 9 rows' table deals 0-499 or D2's block)")


def own_luc(g):
    return g["first_deck_score"] if g["a"] == "lucario" else 1 - g["first_deck_score"]


def allowed_files(r):
    first, second = D_CELL[r]
    other = D_OTHER[r]
    of = {os.path.basename(nf(x)) for x in CELL_FILES[(first, second)]} | {f"{other}.txt", f"t-{other}.txt"}
    return {"lucario.txt", "t-lucario.txt"}, of


def load_d(files, arm):
    rows, filesets = {}, defaultdict(set)
    for f in files:
        for ln in open(f, encoding="utf-8"):
            if not ln.strip():
                continue
            g = json.loads(ln)
            miss = [k for k in NEEDED if k not in g]
            if miss:
                die(f"{f}: a (d) game has no {miss} field(s)")
            r, n = d_locate(f, g)
            if (r, n) in rows:
                die(f"{f}: (d) row {r} deal {n} appears twice")
            lb = g["bot_a"] if g["a"] == "lucario" else g["bot_b"]
            ob = g["bot_b"] if g["a"] == "lucario" else g["bot_a"]
            want = (CODE, BASE) if arm == CODE else (BASE, BASE)
            if (lb, ob) != want:
                die(f"{f}: (d) row {r} deal {n}: Lucario's pilot {lb}, the other's {ob}; expected {want}")
            if "a_file" in g and "b_file" in g:
                lf, of_ = (g["a_file"], g["b_file"]) if g["a"] == "lucario" else (g["b_file"], g["a_file"])
                al, ao = allowed_files(r)
                if os.path.basename(nf(lf)) not in al or os.path.basename(nf(of_)) not in ao:
                    die(f"{f}: (d) row {r} deal {n} is played with {lf} v {of_}, not the row's lists")
                filesets[r].add((nf(lf), nf(of_)))
            if not g["moves"]:
                die(f"{f}: (d) row {r} deal {n} has an empty move fingerprint")
            rows[(r, n)] = {k: g[k] for k in KEEP if k in g}
        SCANNED.append(f)
    for r, fs in filesets.items():
        if len(fs) > 1:
            die(f"(d) {arm}: row {r} is played with more than one pair of lists: {sorted(fs)}")
    if len(rows) != len(D_ROWS) * D_DEALS:
        die(f"(d) {arm}: {len(rows):,} games, expected {len(D_ROWS) * D_DEALS:,} (9 rows x {D_DEALS:,}): an incomplete or "
            f"wrong set of files, nothing read from it (D2 fixes 2,000 deals per row)")
    return rows


D_RES = None
_dkf, _dxf = globbed(f"{PX}_d_{BASE}*.jsonl"), globbed(f"{PX}_d_{CODE}*.jsonl")
if not (_dkf and _dxf):
    P(f"   not in yet: {PX}_d_{BASE}*.jsonl / {PX}_d_{CODE}*.jsonl (holds (d))")
    gate("d", "(d) Lucario's pooled own-side gain, whole 95% interval above zero", "PENDING", "the (d) rows are not all in yet")
else:
    DB, DX = load_d(_dkf, BASE), load_d(_dxf, CODE)
    for (r, n), g in DB.items():
        if n < D_TABLE:
            first, second = D_CELL[r]
            s = BASE45[(first, second, n)]
            fseat = g["first_seat"] if g["a"] == first else 1 - g["first_seat"]
            if g["moves"] != s["moves"] or g["seed"] != s["seed"] or fseat != s["first_seat"]:
                die(f"(d)'s {BASE} arm, row {r} ({first} v {second}) deal {n}: not {BASE}'s reference game on that deal (moves, seed or "
                    f"seats): the laptop's program does not replay {BASE}'s games (section 4.1 item 9: any difference stops the reading)")
    for k in DB:
        if (DB[k]["seed"], {DB[k]["a"], DB[k]["b"]}) != (DX[k]["seed"], {DX[k]["a"], DX[k]["b"]}):
            die(f"(d): the two arms' row {k[0]} deal {k[1]} are not the same deal")
        lsb = DB[k]["first_seat"] if DB[k]["a"] == "lucario" else 1 - DB[k]["first_seat"]
        lsx = DX[k]["first_seat"] if DX[k]["a"] == "lucario" else 1 - DX[k]["first_seat"]
        if lsb != lsx:
            die(f"(d): the two arms seat Lucario differently on row {k[0]} deal {k[1]}")
    parts = [[100 * (own_luc(DX[(r, n)]) - own_luc(DB[(r, n)])) for n in range(D_DEALS)] for r in range(len(D_ROWS))]
    m, h, n = pool(parts)
    rows_mv = [mv(x) for x in parts]
    shares = d_shares([x[0] for x in rows_mv])
    CH_D = sum(1 for k in DB if DB[k]["moves"] != DX[k]["moves"])
    P(f"   {CH_D:,} of {len(DX):,} {CODE}-arm games differ from {BASE}'s. Per row (step 5b item 3, beside the pooled figure; each "
      f"row's share of the pooled sum; the pooled interval is the gate):")
    for r, (a_, b_) in enumerate(D_CELL):
        sb = 100 * sum(own_luc(DB[(r, q)]) for q in range(D_DEALS)) / D_DEALS
        sx = 100 * sum(own_luc(DX[(r, q)]) for q in range(D_DEALS)) / D_DEALS
        rm, rv = rows_mv[r]
        sh = f"; share {100 * shares[r]:+.0f}%" if shares else ""
        P(f"     row {r} Lucario v {D_OTHER[r]:17}: {BASE} {sb:5.1f} -> {CODE} {sx:5.1f} ({rm:+.2f} +/- {1.96 * math.sqrt(rv):.2f}){sh}")
    if not shares:
        P("     (the row means sum to zero or less, so no share is shown)")
    sd_d = h / 1.96
    gain = m - h > 0
    P(f"   pooled over 9 rows ({n:,} deals per arm): {fmt(m, h)} points -> {'a GAIN: the whole 95% interval is above zero' if gain else 'NO gain shown at this size'}")
    P(f"   detectable size: sd {sd_d:.3f}; MDE50 (1.96 sd) {1.96 * sd_d:.2f} points, MDE80 (2.80 sd) {2.80 * sd_d:.2f} points "
      f"(the registration's model: half-width about 0.4 to 0.8 points at 2,000 deals).")
    ONE_ROW = None
    if gain and shares and max(shares) > 0.5:
        ONE_ROW = f"Lucario v {D_OTHER[shares.index(max(shares))]} supplies {100 * max(shares):.0f}% of the pooled gain"
        P(f"   NOTE (step 5b item 3, gates nothing): one row supplies more than half of this passing gain: {ONE_ROW}.")
    D_RES = (m, h, sd_d, CH_D, ONE_ROW)
    gate("d", "(d) Lucario's pooled own-side gain, whole 95% interval above zero", "PASS" if gain else "FAIL",
         f"{fmt(m, h)} points pooled over 9 rows x {D_DEALS:,}" + ("" if gain else
         f"; 'no Lucario gain of about {1.96 * sd_d:.2f} (MDE50) to {2.80 * sd_d:.2f} (MDE80) points or more at this size'"))

# ---------------------------------------------------------------------------------------------------------------
# 5. Coverage.
# ---------------------------------------------------------------------------------------------------------------
P("\n5. COVERAGE (step 5; RUN5 'How coverage rows count': own-side harm in the mixed rows blocks the takeover; accuracy is "
  f"reported). Mixed rows only where {CODE}'s both-sides games differ from {BASE}'s reference files (K9).")
SKIPF = path("coverage_skip.txt")
REPORT = parse_skip_report(open(SKIPF, encoding="utf-8").read()) if os.path.exists(SKIPF) else None
P(f"   coverage_skip.txt: " + ("in; it names " + ", ".join(f"{g} {sum(v[0] == 'SKIP' for v in d.values())} skipped / "
                                                          f"{sum(v[0] == 'RUN' for v in d.values())} run" for g, d in sorted(REPORT.items()))
                              if REPORT is not None else "NOT in yet (every skipped pairing is then unnamed and holds its test)"))
B2E_TSV = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(REPO, REFS["b2e"]["pairs"]), encoding="utf-8"), delimiter="\t")}
NEWD_TSV = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(REPO, REFS["new17"]["pairs"]), encoding="utf-8"), delimiter="\t")}
REACH_B2E = frozenset(p for p, r in B2E_TSV.items() if carries(r["held_file"]) or carries(r["panel_file"]))
if len(REACH_B2E) != REACH_COUNTS["b2e"]:
    die(f"step 5's reach in B2e is 42 of the 96 pairings; the lists give {len(REACH_B2E)}")
LIMB = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E_DIR, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        LIMB[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
ARCH = sorted({k for k, _ in LIMB["pooled"]})
COV_TESTS, COV_CH = [], {}
SKIP_PROBLEMS = defaultdict(list)


def arch_of(k):
    b = k.replace("dustin_", "")
    return next((n for n in ARCH if n == b), None) or next((n for n in ARCH if n.startswith(b)), None)


def probs(group, counted=None, n=3):
    ps = [t_ for p, t_ in SKIP_PROBLEMS[group] if counted is None or p in counted]
    return "; ".join(ps[:n]) + (" ..." if len(ps) > n else "")


def coverage_rows(group, base, new, dirs, reach):
    """read_kta.py's, unchanged in its logic (K9)."""
    deals = defaultdict(list)
    for (p, i) in sorted(base):
        deals[p].append(i)
    pairings = sorted(deals)
    match = {p: all(equal5(base[(p, i)], new[(p, i)]) for i in deals[p]) for p in pairings}
    ndiff = {p: sum(1 for i in deals[p] if not equal5(base[(p, i)], new[(p, i)])) for p in pairings}
    out_reach = [p for p in pairings if ndiff[p] and p not in reach]
    if out_reach:
        INTEG[f"int_reach_{group}"] = (f"{group}: {sum(ndiff[p] for p in out_reach)} changed both-sides games in pairings whose "
                                       f"lists carry neither Stadium: {out_reach[:10]}")
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
                    INTEG[f"int_zero_{group}_{dr}_{p}"] = (f"{group} pairing {p} ({dr}): {ch} mixed-row games differ from {BASE}'s "
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
    n_run = sum(1 for s in status.values() if s.startswith("run"))
    n_skip = sum(1 for s in status.values() if s.startswith("skipped"))
    P(f"     {group}: {sum(ndiff.values()):,} both-sides games differ, in {sum(1 for p in pairings if ndiff[p])} of {len(pairings)} "
      f"pairings; own-side rows: {n_run} run, {n_skip} skipped as unchanged"
      + (f"; PROBLEMS: " + probs(group, n=4) if SKIP_PROBLEMS[group] else ""))
    COV_CH[group] = (sum(ndiff.values()), mix_changed)
    return eff, status


def own_pool(eff_dr, base, rows_of, own):
    parts = []
    for p in rows_of:
        ks = [(p, i) for i in range(500)]
        if any(k not in base for k in ks):
            die(f"a coverage pairing {p} does not have deals 0-499 in {BASE}'s reference file")
        if any(k not in eff_dr for k in ks):
            return None
        parts.append([100 * (own(eff_dr[k]) - own(base[k])) for k in ks])
    return pool(parts)


fds = lambda g: g["first_deck_score"]  # noqa: E731


# 5a. B2e.
P("\n   5a. B2e (96 pairings; the held-out archetypes 0-47 count, Dustin's files 48-95 are reported):")
_bt = have(f"{PX}_b2e_{CODE}.jsonl", "holds coverage (B2e)")
b2e_decks = lambda r: (B2E_TSV[r["pairing"]]["held_key"], B2E_TSV[r["pairing"]]["opponent"])  # noqa: E731
B2E_BASE_P = None
if not _bt:
    gate("cov_b2e", "coverage (B2e held-out): no held-out deck's own side hurt", "PENDING", f"{CODE}'s B2e both-sides file is not in yet")
else:
    B2E_BASE_P = pinned("b2e")
    P(f"     {BASE} baseline: {B2E_BASE_P} (sha256 = the config's {REFS['b2e']['sha256'][:16]}...)")
    B2E_B = load(B2E_BASE_P, REFS["b2e"]["games"], (BASE, BASE), "pi", seed_b2e, b2e_decks, scanned=False)
    B2E_X = load(_bt, REFS["b2e"]["games"], (CODE, CODE), "pi", seed_b2e, b2e_decks)
    same_deals(_bt, B2E_X, B2E_B, f"{BASE}'s B2e reference file")
    rows, files = load_mixed([f"{PX}_mixed_b2e_{CODE}_first*.jsonl"], (CODE, BASE), "pi", B2E_B, f"{BASE}'s B2e reference file")
    eff, stat = coverage_rows("b2e", B2E_B, B2E_X, {"first": (list(range(96)), rows, files)}, REACH_B2E)

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
        P(f"     {block} {k:24} {BASE} {x:5.1f} -> {CODE} {y:5.1f}; Limitless {L:5.1f}; further by {FUR[k][1]:+.1f} (accuracy reported)")
    held = sorted({B2E_TSV[p]["held_key"] for p in range(96)}, key=lambda k: min(p for p in range(96) if B2E_TSV[p]["held_key"] == k))
    vetoes, waits, harm_only, fur_only = [], [], [], []
    P(f"     own side in the mixed rows ({CODE} on the held deck, {BASE} on the panel, against {BASE} on both; a skipped pairing is no change):")
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
    P(f"   B2e: harm or held-out veto: {', '.join(vetoes) or 'none'}  ({cnt})")
    bprobs = probs("b2e", counted=set(range(48)))
    if vetoes:
        gate("cov_b2e", "coverage (B2e held-out): no held-out deck's own side hurt", "FAIL", "harm: " + ", ".join(vetoes) + f" ({cnt})")
    elif waits or bprobs:
        gate("cov_b2e", "coverage (B2e held-out): no held-out deck's own side hurt", "PENDING",
             "; ".join((["waits: " + ", ".join(waits)] if waits else []) + ([bprobs] if bprobs else [])))
    else:
        gate("cov_b2e", "coverage (B2e held-out): no held-out deck's own side hurt", "PASS", f"no held-out deck's own side worse ({cnt})")
    P("\n   The held-out direction (step 5b item 4; RUN5, Sept 29; reported beside every verdict, gates nothing):")
    sys.path.insert(0, K45)
    import heldout_direction as HD  # noqa: E402
    _bn, _cn, _hrows = HD.compute(B2E_BASE_P, _bt, B2E_DIR)
    HD.show(_bn, _cn, [r for r in _hrows if r[0].startswith("A")], None, "held-out direction")
    HD.show(_bn, _cn, [r for r in _hrows if r[0].startswith("B")], "   Dustin's files (48-95; deck 09 carries Training Area), beside, not in the line above:", "Dustin's files")

# 5b. Scizor.
P(f"\n   5b. The Scizor row (carries Training Area; 8 rows x 500; own side = {CODE} on Scizor, {BASE} on the panel list, against {BASE} on both):")
_sx = have(f"{PX}_scizor_{CODE}.jsonl", "holds coverage (Scizor)")
scz_decks = lambda r: (NEWD_TSV[r["pairing"]]["held_key"], NEWD_TSV[r["pairing"]]["opponent"])  # noqa: E731
REACH_SCZ = frozenset(p for p in range(8) if carries(NEWD_TSV[p]["held_file"]) or carries(NEWD_TSV[p]["panel_file"]))
if len(REACH_SCZ) != REACH_COUNTS["scizor"]:
    die(f"step 5's reach: all 8 Scizor rows; the lists give {len(REACH_SCZ)}")
if not _sx:
    gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", f"{CODE}'s Scizor both-sides file is not in yet")
else:
    SB = load(pinned("scizor"), REFS["scizor"]["games"], (BASE, BASE), "pi", seed_new, scz_decks, scanned=False)
    SX = load(_sx, REFS["scizor"]["games"], (CODE, CODE), "pi", seed_new, scz_decks)
    same_deals(_sx, SX, SB, f"{BASE}'s Scizor reference file")
    if sorted({p for p, _ in SB}) != list(range(8)):
        die(f"{BASE}'s Scizor reference file: not pairings 0-7")
    r1, f1 = load_mixed([f"{PX}_mixed_scizor_{CODE}_first*.jsonl"], (CODE, BASE), "pi", SB, f"{BASE}'s Scizor reference file")
    r2, f2 = load_mixed([f"{PX}_mixed_scizor_{CODE}_second*.jsonl"], (BASE, CODE), "pi", SB, f"{BASE}'s Scizor reference file")
    eff, stat = coverage_rows("scizor", SB, SX, {"first": (list(range(8)), r1, f1)}, REACH_SCZ)
    P(f"     Scizor's panel average, both sides: {BASE} {100 * sum(map(fds, SB.values())) / 4000:.1f} -> {CODE} "
      f"{100 * sum(map(fds, SX.values())) / 4000:.1f} (reported; gates nothing)")
    res = own_pool(eff["first"], SB, range(8), fds)
    ch = sum(1 for k, g in eff["first"].items() if g["moves"] != SB[k]["moves"])
    COV_TESTS.append(("Scizor", ch))
    if res is None:
        gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", probs("scizor") or "mixed rows not in")
        P("     own side: waits")
    else:
        m, h, n = res
        harm = m + h < 0
        P(f"     own side: {fmt(m, h)} over 8 rows ({ch} changed) -> {'VETO (own side worse beyond paired noise)' if harm else 'no harm'}")
        if harm:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "FAIL", f"Scizor own side {fmt(m, h)}")
        elif SKIP_PROBLEMS["scizor"]:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "PENDING", probs("scizor"))
        else:
            gate("cov_scz", "coverage: Scizor's own side not hurt", "PASS", f"Scizor own side {fmt(m, h)}")
    if r2 is not None:
        ps = [p for p in range(8) if all((p, i) in r2 for i in range(500))]
        if ps:
            m2, h2, _ = pool([[-100 * (r2[(p, i)]["first_deck_score"] - SB[(p, i)]["first_deck_score"]) for i in range(500)] for p in ps])
            P(f"     the other direction ({CODE} on the panel list, {BASE} on Scizor), the panel's side over {len(ps)} run rows: {fmt(m2, h2)} (reported only)")

# 5c. The second lists.
P(f"\n   5c. The four second lists (own side = {CODE} on the list, {BASE} on the other deck, against {BASE} on both; accuracy reported):")
_v2 = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
lists_bad, lists_wait, reach_var_total = [], [], 0
for v in VARS:
    trows = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(REPO, REFS[f"var_{v}"]["pairs"]), encoding="utf-8"), delimiter="\t")}
    reach_v = frozenset(p for p, r in trows.items() if carries(r["held_file"]) or carries(r["panel_file"]))
    reach_var_total += len(reach_v)
    side = {p: r["variant_side"] for p, r in trows.items()}
    sa, sb_ = sorted(p for p in trows if side[p] == "a"), sorted(p for p in trows if side[p] == "b")
    seed_v = lambda r, t=trows: int(t[r["pairing"]]["seed_first"]) + r["i"]  # noqa: E731
    dec_v = lambda r, t=trows: (t[r["pairing"]]["held_key"], t[r["pairing"]]["opponent"])  # noqa: E731
    own = lambda g, s=side: g["first_deck_score"] if s[g["pairing"]] == "a" else 1 - g["first_deck_score"]  # noqa: E731
    _gx = have(f"{PX}_var_{v}_{CODE}.jsonl", f"holds coverage ({v})")
    if not _gx:
        lists_wait.append(f"{v} both-sides file not in")
        continue
    if sorted(trows) != sorted(REFS[f"var_{v}"]["pairings"]) or REFS[f"var_{v}"]["games"] != 500 * len(trows):
        die(f"var_{v}.tsv's pairings are not the config's var_{v} group")
    GB = load(pinned(f"var_{v}"), 500 * len(trows), (BASE, BASE), "pi", seed_v, dec_v, scanned=False)
    GX = load(_gx, 500 * len(trows), (CODE, CODE), "pi", seed_v, dec_v)
    same_deals(_gx, GX, GB, f"{BASE}'s {v} reference file")
    dirs = {}
    if sa:
        ra, fa = load_mixed([f"{PX}_var_{v}_{CODE}_mixed_a*.jsonl"], (CODE, BASE), "pi", {k: g for k, g in GB.items() if k[0] in sa}, f"{BASE}'s {v} (side a)")
        dirs["a"] = (sa, ra, fa)
    if sb_:
        rb, fb = load_mixed([f"{PX}_var_{v}_{CODE}_mixed_b*.jsonl"], (BASE, CODE), "pi", {k: g for k, g in GB.items() if k[0] in sb_}, f"{BASE}'s {v} (side b)")
        dirs["b"] = (sb_, rb, fb)
    eff, stat = coverage_rows(f"var_{v}", GB, GX, dirs, reach_v)
    merged = {**eff.get("a", {}), **eff.get("b", {})}
    avg = lambda rs: 100 * sum(own(g) for g in rs.values()) / len(rs)  # noqa: E731
    deck = trows[next(iter(trows))]["deck"]
    if deck == "charizardy":
        cs = [LIMB["pooled"].get(("charizardy_entei", o)) for o in {r["opponent"] for r in trows.values()}]
        Lf, srcn = sum(x for x in cs if x is not None) / sum(1 for x in cs if x is not None), "B2e pooled, charizardy_entei"
    else:
        vals = []
        for p, r in trows.items():
            da, db = (deck, r["opponent"]) if r["variant_side"] == "a" else (r["held_key"], deck)
            w, l, t_ = _v2[f"{min(da, db)}|{max(da, db)}"]
            s = (w + 0.5 * t_) / (w + l + t_)
            vals.append(100 * (s if min(da, db) == deck else 1 - s))
        Lf, srcn = sum(vals) / len(vals), "development half, the same opponents"
    x, y = avg(GB), avg(GX)
    acc = f"opponent average {BASE} {x:5.1f} -> {CODE} {y:5.1f}; figure {Lf:5.1f} ({srcn}); further by {abs(y - Lf) - abs(x - Lf):+.1f} (reported)"
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
if reach_var_total != REACH_COUNTS["var"]:
    die(f"step 5's reach in the second lists is 13 of the 29 rows; the lists give {reach_var_total}")
if lists_bad:
    gate("cov_lst", "coverage: no second list's own side hurt", "FAIL", "harm: " + "; ".join(lists_bad))
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
            cells = [c for c in CELLS if CELL_PAIRING[c] == (g_, p)]
            ok = cells and all(equal5(BASE45[(c[0], c[1], i)], NEW45[(c[0], c[1], i)]) for c in cells for i in range(500))
            if said == "SKIP" and not ok:
                INTEG[f"int_skip45_{g_}_{p}"] = f"coverage_skip.txt says SKIP for {g_} pairing {p}, whose games are not all equal"
                P(f"   INTEGRITY LINE: {INTEG[f'int_skip45_{g_}_{p}']}")
_n_tests = sum(1 for _, ch in COV_TESTS + C_TESTS if ch > 0)
P(f"\n   Step 5's count: {len(C_TESTS) + len(COV_TESTS)} own-side no-harm tests ((c) per deck on the reserve route, B2e "
  f"held-out, Scizor, second lists); {_n_tests} have a changed game behind them; the chance a harmless candidate trips at "
  f"least one of those: 1 - 0.975^{_n_tests} = {1 - 0.975 ** _n_tests:.3f}.")

# ---------------------------------------------------------------------------------------------------------------
# 6. The mechanism (step 3): M1 and M2 against the amendment's exact thresholds.
# ---------------------------------------------------------------------------------------------------------------
P(f"\n6. THE MECHANISM (step 3; the counter tool's rows, deals 0-199 of the 17 named cells, {CODE} and {BASE} on both sides). M1 "
  "and M2 gate only when the ΔMSE interval spans zero (the fallback's behavioural footprint), on either route; otherwise "
  "they are reported with their thresholds beside (K10).")
_ck, _cx = globbed(f"{PX}_counters_{BASE}*.jsonl"), globbed(f"{PX}_counters_{CODE}*.jsonl")
CK = CX = None
M_RES = {}
KM17_SET = {(s, p) for s, p, _, _ in KM17}
if not (_ck and _cx):
    P(f"   not in yet: {PX}_counters_{BASE}*.jsonl / {PX}_counters_{CODE}*.jsonl (holds M1 and M2, which gate in the fallback only)")
    for key in M:
        gate(key, f"{M[key]['name']}: {CODE} plays {M[key]['card']} on at least T of its offered turns (the fallback only)",
             "PENDING", "the counter rows are not in yet")
else:
    CK = counter_rows(_ck, BASE, GATE_DEALS, KM17_SET, "the counters (deals 0-199, 17 cells)")
    CX = counter_rows(_cx, CODE, GATE_DEALS, KM17_SET, "the counters (deals 0-199, 17 cells)")
    rows_against(CK, BASE45, f"the counters' {BASE} arm", f"{BASE}'s reference files ({REFS['table']['file']}, {REFS['new17']['file']})")
    rows_against(CX, NEW45, f"the counters' {CODE} arm", f"{CODE}'s own games on the same deals (the footprint run)")
    P(f"   both arms checked deal by deal (moves, decks, seed, seats): {BASE} against its reference files, {CODE} against its footprint "
      "games, all 3,400 deals each: equal.")
    same_moves_diff = [k for k in CK if CK[k]["moves"] == CX[k]["moves"]
                       and (CK[k]["counts"] != CX[k]["counts"] or CK[k].get("xspeed") != CX[k].get("xspeed"))]
    if same_moves_diff:
        INTEG["int_counts"] = (f"{len(same_moves_diff)} counter deals where {CODE}'s game has {BASE}'s moves but other counts, e.g. "
                               f"{same_moves_diff[0]}: the counts are a function of the game (K11)")
        P(f"   INTEGRITY LINE (holds the reading): {INTEG['int_counts']}")
    for key, spec in M.items():
        e = TH[key]
        go, gp = line_sums(CK, key, GATE_DEALS)
        ko, kp = line_sums(CX, key, GATE_DEALS)
        st, txt = m_gate(key, e["T"], e["status"], ko, kp, go, gp)
        M_RES[key] = (st, go, gp, ko, kp)
        tag = "(gates: the fallback)" if "spans" in LABELS else "(reported: the ΔMSE label is not 'spans')"
        P(f"   {spec['name']} {tag}, {spec['card']} on {spec['owner'].capitalize()}'s side, pooled over {len(spec['cells'])} cells, "
          f"deals 0-199: {st}: {txt}")
        per = []
        units = []
        for (src, p) in spec["cells"]:
            u = []
            for i in GATE_DEALS:
                a1 = owner_counts(CK[(src, p, i)], spec["owner"], spec["card"])
                a2 = owner_counts(CX[(src, p, i)], spec["owner"], spec["card"])
                u.append((a1[0], a1[1], a2[0], a2[1]))
            units.append(u)
            g0, g1 = sum(x[0] for x in u), sum(x[1] for x in u)
            k0, k1 = sum(x[2] for x in u), sum(x[3] for x in u)
            per.append(((src, p), g1, g0, k1, k0))
        lo, hi, zero = boot_rate_change(units, args.m_reps, spec["seed"])
        rises = sum(1 for _, g1, g0, k1, k0 in per if g0 and k0 and Fraction(k1, k0) > Fraction(g1, g0))
        P(f"      reported beside: {BASE} {pc(gp, go)} -> {CODE} {pc(kp, ko)}; paired change {100 * ((kp / ko if ko else 0) - (gp / go if go else 0)):+.1f} "
          f"points, 95% interval {100 * lo:+.1f} to {100 * hi:+.1f} ({args.m_reps} replicates of step 3's per-cell resampling "
          f"on these deals; reported{'; ' + str(zero) + ' replicates with no offered turn' if zero else ''}); it rises in "
          f"{rises} of {len(per)} cells")
        P("      per cell: " + "; ".join(f"{s}:{p} {pc(g1, g0)} -> {pc(k1, k0)}" for (s, p), g1, g0, k1, k0 in per))
        if spec["rest"]:
            r_go, r_gp = line_sums(CK, key, GATE_DEALS, spec["rest"])
            r_ko, r_kp = line_sums(CX, key, GATE_DEALS, spec["rest"])
            rest_units = [[(*owner_counts(CK[(s, p, i)], spec["owner"], spec["card"]), *owner_counts(CX[(s, p, i)], spec["owner"], spec["card"]))
                           for i in GATE_DEALS] for (s, p) in spec["rest"]]
            clo, chi = boot_contrast(units, rest_units, args.m_reps, spec["seed"] + 1)
            P(f"      the last four cells (v Lucario, Vespiquen, Weezing; Altaria/Greninja v Altaria: Stage 1 attackers, no "
              f"rise predicted): {BASE} {pc(r_gp, r_go)} -> {CODE} {pc(r_kp, r_ko)}; the contrast (mean change over the five) - "
              f"(mean change over the four): 95% interval {100 * clo:+.1f} to {100 * chi:+.1f} points (reported)")
        gate(key, f"{spec['name']}: {CODE} plays {spec['card']} on at least T of its offered turns (the fallback only)", st, txt)

    # M3 and the sentinels, reported.
    def tally(rows, decks, card):
        off = pl = 0
        for r in rows.values():
            for c in r["counts"]:
                if c["deck"] in decks:
                    x = c.get("cards", {}).get(card) or {}
                    off, pl = off + x.get("offered", 0), pl + x.get("played", 0)
        return off, pl

    def blower_stadium(rows):
        n = 0
        for r in rows.values():
            for c in r["counts"]:
                x = c.get("cards", {}).get("Field Blower") or {}
                n += sum(v for t_, v in (x.get("targets") or {}).items() if "stadium" in t_.lower())
        return n

    def xs(rows, decks):
        tot = noret = trail = 0
        for r in rows.values():
            for e in r.get("xspeed") or []:
                if r["seat_decks"][e["seat"]] in decks:
                    tot += 1
                    noret += not e.get("retreated", False)
                    trail += bool(e.get("hiking_trail", False))
        return tot, noret, trail
    P(f"   Reported (gate nothing): M3, Field Blower's Stadium targets: {BASE} " + str(blower_stadium(CK)) + f", {CODE} " + str(blower_stadium(CX)) + ".")
    for card, decks, what in (("X Speed", {"lucario", "vespiquen", "weezing"}, "Lucario, Vespiquen, Weezing"),
                              ("Team Rocket's Boss", {"suicune"}, "Suicune"), ("Copycat", {d for c in KM17 for d in c[2:]}, "all 17 cells")):
        o1, p1 = tally(CK, decks, card)
        o2, p2 = tally(CX, decks, card)
        P(f"     sentinel {card} ({what}): {BASE} {p1:,} of {o1:,} ({pc(p1, o1)}) -> {CODE} {p2:,} of {o2:,} ({pc(p2, o2)}); "
          f"expected unchanged within paired noise (N2 touches none of these cards)")
    t1, n1, h1 = xs(CK, {"lucario", "vespiquen", "weezing"})
    t2, n2, h2 = xs(CX, {"lucario", "vespiquen", "weezing"})
    P(f"     X Speed plays with no retreat after them: {BASE} {n1} of {t1}, {CODE} {n2} of {t2}; with Hiking Trail in play: {BASE} "
      f"{h1}, {CODE} {h2} (the registration's 96-turn upper bound of 1.2 is settled by this column)")

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
        P(f"     {deck} v {r[0]:17} {BASE} {r[1]:5.1f} {CODE} {r[2]:5.1f} | Limitless {r[3]:5.1f} +/- {r[4]:4.1f} (n {r[5]}) | miss {abs(r[1] - r[3]):4.1f} -> {abs(r[2] - r[3]):4.1f}")
    a0, a1, La = (sum(r[j] for r in rows) / len(rows) for j in (1, 2, 3))
    P(f"     {'equal-weight average over ' + str(len(rows)) + ' cells':>34}: {BASE} {a0:5.1f} {CODE} {a1:5.1f} | Limitless {La:5.1f} | miss {abs(a0 - La):4.1f} -> {abs(a1 - La):4.1f}")


P("\n   7a. Lucario (the pre-named deck) and Altaria (reported beside, gating nothing: the same direction is supporting "
  "evidence, the other a finding to write down). Their real cells, before and after:")
show_real("lucario", "Lucario's nine real cells")
show_real("altaria", "Altaria's nine real cells")
if MIX_READY:
    for dk in ("altaria", "lucario"):
        cells9 = [c for c in CELLS if dk in c]
        m9, h9, n9, per = deck_report(dk, cells9)
        P(f"   {dk.capitalize()}'s own side in the mixed rows over its nine cells: {fmt(m9, h9)} ({n9:,} deals; zero-footprint "
          f"cells read as {BASE}'s games, K5)")
else:
    P("   Altaria's and Lucario's own side in the mixed rows: waits for the mixed rows.")
P("\n   7b. Deck averages over the 45 cells (score45's rows; current / new / Limitless; change in miss, + = further). "
  f"Lucario's gap under {BASE}: 52.2 against 45.6 real (+6.6; Amendment 1 (b) item 5), stated before any game:")
for dk, (cur, new, lim_, chg) in sorted(A["deck_avg"].items()):
    P(f"     {dk:>17}: {BASE} {cur:5.1f} -> {CODE} {new:5.1f}; Limitless {lim_:5.1f}; gap {abs(cur - lim_):4.1f} -> {abs(new - lim_):4.1f} ({chg:+.1f})")
P("   Closure sentence (step 4 (e); 'Stadium damage bonuses count as the relevant cards'): the carrier count found two "
  "archetypes (Lucario with Arena, Altaria with Training Area), so the route is open on the count.")

# ---------------------------------------------------------------------------------------------------------------
# 8. Which condition carried the verdict; 9. the verdict.
# ---------------------------------------------------------------------------------------------------------------
for f in SCANNED:
    pg = f[:-len(".jsonl")] + ".txt"
    if not os.path.exists(pg) or "Findings (occurrences / games affected):" not in open(pg, encoding="utf-8", errors="replace").read():
        gate("scan", "every file read has its scan page (a page not in holds the reading)", "PENDING",
             f"no scan page with a Findings block beside {os.path.basename(f)}")
        break
else:
    gate("scan", "every file read has its scan page", "PASS", f"{len(SCANNED)} files, each with its page; no RULE finding")
for iid, txt in INTEG.items():
    gate(iid, "INTEGRITY LINE (holds the reading; never a registered fail)", "PASS" if EXPLAINED else "PENDING",
         txt + (" -- explained by a human (--integrity-explained)" if EXPLAINED else ""), "integrity")
if not INTEG:
    gate("int", "integrity lines (K12)", "PASS", "none: every changed game sits where N2 reaches, no mixed-row game differs "
         "where the both-sides games all matched, and the counts follow the games", "integrity")

P("\n8. WHICH CONDITION CARRIED THE VERDICT (step 5b item 2; a column, not a rule): each condition, its result, whether it "
  "gates here, and the changed games behind it.")
GS = {g[0]: g for g in GATES}


def st_of(gid):
    return GS[gid][2] if gid in GS else "-"


def gates_here(gid):
    ls = [L for L in sorted(LABELS) if L != "above" and applies(gid, L, ROUTE)]
    if not ls:
        return "(reported)"
    return "(gates)" if len(ls) == len([L for L in LABELS if L != "above"]) else "(gates if " + "/".join(ls) + ")"


_b2e_ch, _scz_ch = COV_CH.get("b2e", (0, 0)), COV_CH.get("scizor", (0, 0))
_lst_ch = tuple(sum(COV_CH.get(f"var_{v}", (0, 0))[j] for v in VARS) for j in (0, 1))
_lab = LABEL if len(LABELS) == 1 else "PENDING (" + "/".join(sorted(LABELS)) + ")"
rows8 = [("step 1: the footprint", ROUTE + (" (under 15%)" if ROUTE == "reserve" else " (15% or more)"), f"{FP_D:,} of 22,500 both-sides games on the 45 cells"),
         ("ΔMSE label (step 4)", _lab, f"the same {FP_D:,} games, {RES45:,} of them with a changed result"),
         ("no harm: τ̂ bound", f"{st_of('b1')} {gates_here('b1')}", f"{FP_D:,} both-sides games"),
         ("no harm: rule-v2 vetoes", f"{st_of('b2')} {gates_here('b2')}", f"{MIX_CHANGED45:,} mixed-row games changed"),
         ("(c) no meta deck worse", f"{st_of('c')} {gates_here('c')}", f"{MIX_CHANGED45:,} mixed-row games changed on the 45 cells"),
         ("coverage: B2e held-out", f"{st_of('cov_b2e')} {gates_here('cov_b2e')}", f"{_b2e_ch[0]:,} both-sides; {_b2e_ch[1]:,} own-side mixed-row games changed"),
         ("coverage: Scizor", f"{st_of('cov_scz')} {gates_here('cov_scz')}", f"{_scz_ch[0]:,} both-sides; {_scz_ch[1]:,} own-side mixed-row games changed"),
         ("coverage: second lists", f"{st_of('cov_lst')} {gates_here('cov_lst')}", f"{_lst_ch[0]:,} both-sides; {_lst_ch[1]:,} own-side mixed-row games changed"),
         ("(d) the gain on Lucario", f"{st_of('d')} {gates_here('d')}", (f"{D_RES[3]:,} of {len(D_ROWS) * D_DEALS:,} {CODE}-arm games differ" if D_RES else "not in yet")),
         ("M1 Arena of Antiquity", f"{st_of('m1')} {gates_here('m1')}", (f"{CODE} {M_RES['m1'][4]:,} of {M_RES['m1'][3]:,}, {BASE} {M_RES['m1'][2]:,} of {M_RES['m1'][1]:,}" if "m1" in M_RES else "not in yet")),
         ("M2 Training Area", f"{st_of('m2')} {gates_here('m2')}", (f"{CODE} {M_RES['m2'][4]:,} of {M_RES['m2'][3]:,}, {BASE} {M_RES['m2'][2]:,} of {M_RES['m2'][1]:,}" if "m2" in M_RES else "not in yet"))]
for c_, r_, ch_ in rows8:
    P(f"   {c_:28} {r_:30} {ch_}")
P("   'No harm with almost no changed games' is the reserve route working as designed and says little; the informative parts "
  "are the gain on the pre-named deck (Lucario) and the footprint (M1, M2).")

P("\n9. VERDICT (section 6, 'Outcomes fixed now', read from the numbers above).")
P(f"   route: {'the reserve route (footprint under 15%)' if ROUTE == 'reserve' else 'the ordinary rule (footprint 15% or more)'}; "
  f"ΔMSE label: " + (LABEL_TEXT[LABEL] if len(LABELS) == 1 else f"PENDING between {' and '.join(sorted(LABELS))} (the --reps {DECISIVE_REPS} rerun decides)"))
for gid, text, st, dt, kind in GATES:
    tag = st if kind != "gate" else f"{st} {gates_here(gid)}"
    P(f"     {tag:26} {text}: {dt}")
RESULT, BYLAB = overall(GATES, LABELS, ROUTE)
FN = fail_names(BYLAB)
ALLN = list(dict.fromkeys(n for L in sorted(FN) for n in FN[L]))


def under(name):
    ls = [L for L in sorted(LABELS) if name in FN.get(L, [])]
    return "" if len(ls) == len(LABELS) else " (if the label is " + " or ".join(f"'{L}'" for L in ls) + ")"


COV_PENDING = [g for g in GATES if g[0].startswith("cov_") and g[2] == "PENDING"]
if RESULT == "ADOPTED":
    how = ("the accuracy clause passed (outcome 1: 'demonstrated improvement') and every clause that gates on this route "
           "held; M1 and M2 are reported with their thresholds beside" if LABELS == {"below"} else
           "the ΔMSE interval spans zero ('undetectable at this size') and the fallback's four tests all held: no harm, the "
           "coverage decks, (d) on Lucario and M1's and M2's thresholds" if LABELS == {"spans"} else
           "every test that gates held under each ΔMSE label still open (" + " and ".join(sorted(LABELS)) + "), so the "
           f"--reps {DECISIVE_REPS} rerun cannot change the outcome; it still fixes which label is recorded")
    P(f"\n   => {CODE} is ADOPTED as the working pilot in the tables, replacing {BASE}, 'unconfirmed': {how}. Its use in the "
      f"screen and the floor waits for the official engine switch, as {BASE}'s does (Amendment 1 (g)).")
    if LABELS == {"below"} and ROUTE == "ordinary":
        P("      Confirmation (step 7): on the post-freeze events alone, at least half the development margin with its own 90% "
          "interval above zero.")
    else:
        P("      Confirmation (step 7): the no-harm re-check at the post-freeze pull: τ̂ margin 90% lower bound at -1.0 or above "
          "and no veto, with Lucario's and Altaria's post-freeze cells reported.")
    P("      km joins the post-freeze list by a commit to rl/results/postfreeze_2026-09-27/README.md before that data is opened.")
elif RESULT == "NOT ADOPTED":
    if len(LABELS) == 1:
        P(f"\n   => {CODE} is NOT ADOPTED; {BASE} stays the working pilot. The test(s) that failed: {', '.join(ALLN)}.")
    else:
        P(f"\n   => {CODE} is NOT ADOPTED (settled under every open label: {' and '.join(sorted(LABELS))}); {BASE} stays the working "
          f"pilot. The recorded label and failure name wait for the --reps {DECISIVE_REPS} rerun (step 4: that run decides "
          f"the label, and the verdict waits for it). The test(s) that fail under each open label:")
        for L in sorted(LABELS):
            P(f"        [{L}] {', '.join(FN[L])}")
    for L, (res, gs) in BYLAB.items():
        for g in gs:
            P(f"        [{L}] {g[1]}: {g[3]}")
    if "accuracy-worsening" not in ALLN:
        P("      This is never an accuracy negative: the ΔMSE result is " + (
          "'undetectable at this size'" if LABELS == {"spans"} else "a pass of the accuracy clause" if LABELS == {"below"} else
          "a pass of the accuracy clause or 'undetectable at this size', whichever the rerun gives")
          + ", and the failure is named by the test that failed.")
    elif len(LABELS) > 1:
        P("      No accuracy negative is recorded yet: 'accuracy-worsening' is the name only if the rerun gives 'wholly above "
          "zero'; if it gives 'spans zero', the result is 'undetectable at this size', never an accuracy negative.")
    if "gain" in ALLN and D_RES:
        P(f"      (d){under('gain')}: no Lucario gain of about {1.96 * D_RES[2]:.2f} (MDE50) to {2.80 * D_RES[2]:.2f} (MDE80) "
          f"points or more at this size ({fmt(D_RES[0], D_RES[1])}). km is then adoptable only by Dustin's explicit override, "
          f"recorded as such (section 6 item 4). Section 6 item 7 (diagnostic): what is left of the Trainer gap may be search "
          f"cost and information, not board numbers.")
    if "mechanism" in ALLN:
        P(f"      The behavioural footprint{under('mechanism')} reads 'not adopted: mechanism not shown at this size', never an "
          f"accuracy negative (step 3).")
    if COV_PENDING:
        P("      Provisional until step 5 is read (RUN5: a 'not adopted' is provisional until the coverage decks are read): "
          + "; ".join(g[1] for g in COV_PENDING) + ".")
    pend_else = [g for g in GATES if g[2] == "PENDING"]
    if pend_else:
        P(f"      Settled whatever is still pending ({len(pend_else)} line(s) above read PENDING): more failed tests may be added "
          f"to the list, but the verdict cannot turn into an adoption.")
elif RESULT == "HELD":
    THEN, THEN_BY = once_explained(GATES, LABELS, ROUTE)
    P(f"\n   => HELD; once explained: {verdict_words(THEN, THEN_BY, LABELS)}. No verdict is recorded, NOT ADOPTED included, "
      f"while a holding line is open (K12).")
    P("      Held by (an integrity line is released by a human's written explanation, --integrity-explained FILE; a missing "
      "scan page by the page itself):")
    for g in holding_lines(GATES):
        P(f"        {g[1]}: {g[3]}")
    if THEN != "ADOPTED":
        for L, (res, gs) in THEN_BY.items():
            P(f"        if the ΔMSE label is '{L}': {res}" + (": " + "; ".join(f"{g[1]} ({g[3][:160]})" for g in gs) if gs else ""))
else:
    P("\n   => PENDING: nothing that decides has failed on every open label, but the verdict cannot be written yet:")
    for L, (res, gs) in BYLAB.items():
        P(f"        if the ΔMSE label is '{L}': {res}" + (": " + "; ".join(f"{g[1]} ({g[3][:160]})" for g in gs) if gs else ""))
    if len(LABELS) > 1:
        P(f"      The label waits for the --reps {DECISIVE_REPS} rerun of these same games (step 4, fixed before any km result).")
_ungated = [g for g in GATES if g[4] == "gate" and g[0] in ("b1", "c") and g[2] == "FAIL"
            and not any(applies(g[0], L, ROUTE) for L in LABELS if L != "above")]
if _ungated and RESULT != "NOT ADOPTED":
    P("      WHICH READING DECIDED (K4): " + "; ".join(f"{g[1]} FAILED ({g[3][:120]})" for g in _ungated) + ". On the ordinary "
      "rule it does not gate under this label: section 6's ordinary-rule outcomes name the vetoes, step 5 and (d), and the "
      "τ̂ bound only in the fallback; section 6 item 3 reads harm as 'route (c) or the vetoes'. A reading that gated it "
      "would give NOT ADOPTED (harm). Written down for Dustin; this reading applies the text as registered.")
if D_RES and D_RES[4] and RESULT == "ADOPTED":
    P(f"   Beside the verdict (step 5b item 3, gates nothing): one row supplies more than half of the passing (d) gain: {D_RES[4]}.")
if REPORTED_MISSING:
    P(f"   Reported-only inputs not in yet (they hold nothing): {', '.join(REPORTED_MISSING)}")

P("\n   THE OUTCOMES THE REGISTRATION FIXES (section 6):")
P("     - On either route, ΔMSE interval wholly above zero: not adopted, on accuracy, whatever else passes (no fallback).")
P(f"     - Reserve route: wholly below zero and (b), (c), (d) and step 5 pass: adopted (in the tables, replacing {BASE}; the "
  "screen and the floor wait for the official engine switch, Amendment 1 (g)); spanning zero ('undetectable at this "
  "size'): (b), (c), step 5, (d) and M1's and M2's thresholds all pass: adopted, 'unconfirmed'.")
P("     - Ordinary rule: wholly below zero and the vetoes, step 5 and (d) pass: adopted; spanning zero: all four fallback "
  "tests pass (no harm, the coverage decks, (d), M1 and M2): adopted, 'unconfirmed'.")
P("     - Any test that applies fails: not adopted, recorded by that test (harm, coverage, gain or mechanism), never as an "
  "accuracy negative for an interval that spans zero. If (d) fails or the route is closed, adoption comes only by "
  "Dustin's explicit override, recorded as such. A spec change after any reading is a new code. N1 is not in km.")
P("\n   WHAT STAYS PROVISIONAL, whatever the numbers say:")
P("     - A 'not adopted' is provisional until step 5 (the coverage decks) is read.")
P("     - Confirmation at the post-freeze pull (step 7): an adopted km is the working pilot 'unconfirmed'; a failed check reads "
  "'not confirmed at this size'. The lapse clause (as Amendment 1 (b) item 5 restates it): km carries kta's switch 1 and, "
  "through kta, kog's A and F, so until kta's row, kog's, and the kpg and koa rows kog inherits have passed, km is not "
  "confirmed even if its own check passes.")
P(f"     - The base-change rule (section 2), applied by Amendment 1 (Sept 30): km is re-issued on kta; this reading is "
  f"{CODE} against {BASE}, at B {CFG['build']['commit'][:7]}.")
P("     - The 45 cells are development evidence for km (step 6); the Sept 25 holdout is spent. The confirmation is the "
  "post-freeze read.")
P("     - The second reader (RUN5 tier 1) and an outcome audit against the registration are still owed; this is the laptop's "
  "first reader. The footprint is committed alone before the rest is read (step 1).")
