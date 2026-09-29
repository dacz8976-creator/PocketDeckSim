#!/usr/bin/env python3
"""kt's reading on kog (Sept 28 night), written blind: before any kt outcome was seen, and it reads nothing until
footprint.txt exists. It follows amendment 2 (the re-issue on kog, which holds over the text) over the original
registration and amendment 1, in the registered order:
   1. the footprint (fixes each code's route: under 15% the reserve route, otherwise the ordinary adoption rule; decided
      from the COUNTS, and stopped on if footprint.txt's own route text disagrees), then 1b, item 7's identity record and
      item 4's timing line restated from the runner's files (stopped on if absent or failed);
   2. the 45 cells, by score45.py (rules v2, with the code's mixed rows), read on the route the footprint chose;
   3. reserve route only: clause (c), the mixed rows of the cells where the footprint is not zero;
   4. clause (d), the census Rayquaza list's eight rows (gates on the reserve route; reported otherwise);
   5. coverage (item 4; Dustin, Sept 28: "coverage rows count for the mixed-row veto and are reported for accuracy"):
      B2e (0-47 counted, 48-95 reported), the Scizor row, the four second lists;
   6. reported beside, gating nothing: Suicune's and Rayquaza's real cells before and after, Suicune's own-side rows,
      the ktb3 / ktc3 attribution (real error only), pointers to the Dustin-deck A/B, the counters and the traces;
   7. a verdict block per code, and the outcome the registration fixes for the pair.
Every input is checked for its full game count and for the same deals as its baseline (STOP, naming the file, if not).
A file that is not in yet is printed as "not in yet" and the verdict says PROVISIONAL. Nothing is skipped silently.

Usage (WSL):  python3 read_kt.py > READING_numbers.txt
  --kt-dir DIR      where the kt runner's files are (default: this folder)     --build ec7e1a8 (file-name prefix)
  --pages-dir DIR   where score45's full pages are written (default: kt-dir)   --reps N (score45 bootstrap; default 4000)
  --kog-dir / --cov-dir / --b2e-kog3   the kog3 baselines (defaults: the committed ones, see below)
  --reuse-45        reuse a score45 page only if it is newer than all its inputs AND was made by the same command at the
                    same --reps (a sidecar <page>.reps records both)           --no-attribution  skip ktb3 / ktc3
  --footprint-only  print sections 1 and 1b (footprint, routes, identity, timing) and stop (the process step "read and
                    commit footprint.txt alone")
  --parse-page F    parse one score45 page (reads no kt file), print what was parsed, and stop (a test aid)
  --selftest        run the gate-logic self-tests (reads no file) and stop
The real reading is run with the default --reps 4000 (the header warns loudly otherwise). A bound that lies within a
hair of a registered line is not called: it is PENDING, with the rerun it needs (--reps 20000) named (N9).
The kog3 baselines: kog_composition_2026-09-27/table_kog3.jsonl and new17_kog3.jsonl; the cloud's
koh_2026-09-28/reading/b2e_kog3.jsonl (or /tmp/kt_ref_b2e_kog3.jsonl, /tmp/koh_cloud/b2e_kog3.jsonl, or read from the
cloud branch by git); koh_2026-09-28/laptop_runs/scizor_kog3.jsonl and var_<list>_kog3.jsonl. kog3 on the Rayquaza
list (clause (d)) is kt's own file, <build>_d_kog3.jsonl.
"""
import argparse, csv, hashlib, json, math, os, re, subprocess, sys, tempfile, textwrap
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)  # rl/results

ap = argparse.ArgumentParser(description="kt's reading on kog (see the module docstring)")
ap.add_argument("--kt-dir", default=HERE)
ap.add_argument("--build", default="ec7e1a8")
ap.add_argument("--pages-dir", default=None)
ap.add_argument("--kog-dir", default=os.path.join(RES, "kog_composition_2026-09-27"))
ap.add_argument("--cov-dir", default=os.path.join(RES, "koh_2026-09-28", "laptop_runs"))
ap.add_argument("--b2e-kog3", default=None)
ap.add_argument("--reps", type=int, default=None)
ap.add_argument("--reuse-45", action="store_true")
ap.add_argument("--no-attribution", action="store_true")
ap.add_argument("--footprint-only", action="store_true")
ap.add_argument("--parse-page", default=None)
ap.add_argument("--selftest", action="store_true")
args = ap.parse_args()
DEFAULT_REPS, DECISIVE_REPS = 4000, 20000  # score.py's own default; the rerun a near-the-line bound asks for
REPS = args.reps or DEFAULT_REPS
args.kog_dir, args.cov_dir = os.path.abspath(args.kog_dir), os.path.abspath(args.cov_dir)  # score45 runs from its own folder
KT, S = os.path.abspath(args.kt_dir), args.build
PAGES = os.path.abspath(args.pages_dir or KT)
K45 = os.path.join(RES, "kpf_2026-09-26", "reading")
TSV = os.path.join(RES, "gauntlet_runs_2026-09-26", "tsv")
B2E_DIR = os.path.join(RES, "b2e_card_check_2026-09-26")
CODES = ("kt3", "kta3")
FIRST_ARM = "kog3"
P = print


def die(msg):
    sys.exit("STOP: " + msg)


def path(name):
    return os.path.join(KT, name)


NOT_IN = {c: [] for c in CODES}  # per code: files that are not in yet (=> PROVISIONAL)


def opt(name, *codes):
    """The path of a kt file if it is in; otherwise it is recorded as not in yet for the codes named (only files a
    verdict really waits for are named: with no code named the file is reported-only and holds nothing) and None."""
    p = path(name)
    if os.path.exists(p):
        return p
    for c in codes:
        if name not in NOT_IN[c]:
            NOT_IN[c].append(name)
    P(f"   not in yet: {name}" + ("" if codes else " (reported only: it holds no verdict)"))
    return None


# ---------------------------------------------------------------------------------------------------------------
# Loading with the completeness guards (item 5 of the job: full game count, the baseline's deals, the right bots).
# ---------------------------------------------------------------------------------------------------------------
KEEP = ("a", "b", "bot_a", "bot_b", "i", "pairing", "seed", "moves", "first_deck_score")


def load(p, n, bots, mode):
    """{key: record}; mode 'abi' keys by (a, b, i) (the table and the new cells share pairing numbers), 'pi' by
    (pairing, i). STOP unless the file has exactly n games, no repeated deal, and only the bots named."""
    rows, cnt = {}, 0
    with open(p, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            cnt += 1
            key = (g["a"], g["b"], g["i"]) if mode == "abi" else (g["pairing"], g["i"])
            if key in rows:
                die(f"{p}: game {key} appears twice")
            rows[key] = {k: g[k] for k in KEEP if k in g}
    if cnt != n:
        die(f"{p}: {cnt} games, expected {n}: an incomplete or wrong file, nothing read from it")
    got = {(r["bot_a"], r["bot_b"]) for r in rows.values()}
    if got != {bots}:
        die(f"{p}: pilots {sorted(got)}, expected {bots}")
    return rows


def same_deals(p, rows, base, what):
    if rows.keys() != base.keys():
        die(f"{p}: its games are not {what}'s deals ({len(rows.keys() ^ base.keys())} games in only one of the two)")
    bad = [k for k in rows if rows[k]["seed"] != base[k]["seed"]]
    if bad:
        die(f"{p}: {len(bad)} games have a different seed from {what}'s, e.g. {bad[0]}")
    # A seed encodes its pairing (seed = base + pairing x 10,000 + i), but a run made from the wrong list would still pass
    # that; the deck names of every game must also be the baseline's (both come from the same TSV column values).
    bad = [k for k in rows if (rows[k]["a"], rows[k]["b"]) != (base[k]["a"], base[k]["b"])]
    if bad:
        die(f"{p}: {len(bad)} games are between different decks from {what}'s, e.g. {bad[0]}: "
            f"{(rows[bad[0]]['a'], rows[bad[0]]['b'])} against {(base[bad[0]]['a'], base[bad[0]]['b'])}")


# ---------------------------------------------------------------------------------------------------------------
# Pure gate logic (no file is read here; --selftest exercises it).
# ---------------------------------------------------------------------------------------------------------------
def route_of(d, n):
    """The route from the INTEGERS: under 15% (d/n < 0.15, that is 100 d < 15 n) is 'reserve'; 15% or more is 'ordinary'.
    Never from a printed, rounded percentage: 3,374 of 22,500 is 14.9956%, which prints as 15.00."""
    return "reserve" if 100 * d < 15 * n else "ordinary"


def tau_gate(lo, ev_lo, reps):
    """Clause (b)'s "tau margin 90% lower bound at -1.0 or above". `lo` is score.py's printed bound (two decimals), `ev_lo`
    the by-event bound (beside, gates nothing: N2). Returns (status, [notes]). A bound printed as -1.00 may be truly
    -1.004 (a fail) or -0.996 (a pass): not called. A bound within 0.10 of the line at fewer than DECISIVE_REPS is not
    called either (its Monte-Carlo error is about 0.03; score.py's seeds are fixed, so the answer moves with --reps)."""
    notes, gap = [], abs(lo + 1.0)
    status = "PASS" if lo >= -1.0 else "FAIL"
    if gap < 0.005:
        status = "PENDING"
        notes.append("BOUNDARY: printed -1.00, so the true bound is within +/-0.005 of the registered line; not called, "
                     "read it by hand at more digits (N9)")
    elif gap < 0.10:
        if reps < DECISIVE_REPS:
            status = "PENDING"
            notes.append(f"MC-BOUNDARY: within 0.10 of the -1.0 line at --reps {reps} (Monte-Carlo error about 0.03); rerun "
                         f"the reader with --reps {DECISIVE_REPS} and read that run, the larger run decides (N9)")
        else:
            notes.append(f"near the -1.0 line; this --reps {reps} run is the decisive one (N9)")
    if (ev_lo >= -1.0) != (lo >= -1.0):
        notes.append(("by-event lower bound %+.2f is BELOW -1.0 while the match-level bound is not" if lo >= -1.0 else
                      "by-event lower bound %+.2f is at or above -1.0 while the match-level bound is below it") % ev_lo
                     + " (beside, gates nothing, N2)")
    return status, notes


def dmse_gate(below0, lo, hi, reps):
    """The ordinary rule's "whole 95% interval below zero". score.py's own 'below 0' compares the unrounded bound, so it
    decides; a bound within 5% of the interval's width of 0 is inside the bootstrap's Monte-Carlo noise (a 97.5th
    percentile of 4,000 draws) and is not called below DECISIVE_REPS. Returns (status, [notes])."""
    notes, status = [], ("PASS" if below0 else "FAIL")
    if hi - lo > 0 and abs(hi) < 0.05 * (hi - lo):
        if reps < DECISIVE_REPS:
            status = "PENDING"
            notes.append(f"MC-BOUNDARY: the upper bound {hi:+.1f} is within 5% of the interval's width of 0 at --reps {reps}; "
                         f"rerun the reader with --reps {DECISIVE_REPS} and read that run, the larger run decides (N9)")
        else:
            notes.append(f"the upper bound is near 0; this --reps {reps} run is the decisive one (N9)")
    return status, notes


NUM = r"([+-][\d.]+)"


def _summary_entries(s, what):
    """score.py's 'cell veto (...)' / 'deck veto (...)' summary line, after the colon: [(who, gain)]. 'none' is empty; the
    ' [INDICATIVE...' tag of an unpaired page is cut."""
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
    """Parse a score45 page. `lenient` (the --parse-page test aid only) lets an older page lack the event-resampled lines,
    which score45 has printed since Sept 28; the real reading is never lenient."""
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
                d["dmse"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4) == "below 0")
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
            m = re.match(r"^\s+(\w+):\s+([\d.]+)\s*/\s*([\d.]+)\s*/\s*([\d.]+)\s+([+-][\d.]+)\s*$", ln)  # Deck averages rows
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
        # Backstop: the veto gates rest on the veto LINES; score.py's own summary lines say how many there are. A line the
        # regex missed would otherwise read as "no veto" (the derived-verdict check below sees it only when dMSE is below 0).
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
    """The gate logic, on canned numbers. Reads no file."""
    assert route_of(3374, 22500) == "reserve" and route_of(3375, 22500) == "ordinary"
    assert route_of(0, 22500) == "reserve" and route_of(22500, 22500) == "ordinary"
    assert 100 * 3374 / 22500 < 15 and f"{100 * 3374 / 22500:.2f}" == "15.00"  # why the integers decide, not the printout
    T = lambda lo, ev, reps: tau_gate(lo, ev, reps)  # noqa: E731
    assert T(-1.00, -1.5, 4000)[0] == "PENDING" and T(-1.00, -1.0, 20000)[0] == "PENDING"      # printed -1.00: never called
    assert T(-0.95, -0.9, 4000)[0] == "PENDING" and T(-1.05, -1.2, 4000)[0] == "PENDING"       # within 0.10, few reps
    assert T(-0.95, -0.9, 20000)[0] == "PASS" and T(-1.05, -1.2, 20000)[0] == "FAIL"            # the decisive run calls it
    assert T(-0.85, -0.9, 4000)[0] == "PASS" and T(-1.20, -1.3, 4000)[0] == "FAIL"              # clear of the line
    assert T(-0.50, -1.30, 4000)[0] == "PASS" and any("BELOW -1.0" in x for x in T(-0.50, -1.30, 4000)[1])
    assert any("at or above -1.0" in x for x in T(-1.30, -0.50, 4000)[1]) and T(0.0, 0.0, 100)[0] == "PASS"
    D = dmse_gate
    assert D(False, -100.0, 10.0, 4000)[0] == "FAIL" and D(True, -100.0, -20.0, 4000)[0] == "PASS"
    assert D(True, -100.0, -3.0, 4000)[0] == "PENDING" and D(True, -100.0, -3.0, 20000)[0] == "PASS"
    assert D(False, 0.0, 0.0, 100)[0] == "FAIL"                                                # a zero-width interval on zero
    page = """== all cells: 45 pairings
  dMSE new - current: -1.0 points^2, 95% interval -2.0 to +1.0 (not below 0) [Limitless side binomial]
  dMSE, Limitless side resampled by event: 95% interval -2.0 to +1.0 (not below 0; 0 of 4000 event draws redrawn because a cell had no match)
  real error, current minus new: +0.10 points, 90% interval -0.10 to +0.30 (margin rule)
  real error, Limitless side resampled by event: 90% interval -0.10 to +0.30
  cell veto (miss grows > 6): a v b +7.0, c_d v e +8.5
  deck veto (gap grows > 2): x +3.1
    a v b +7.0: COUNTS: kt3 pilots a worse (a's side -9.0 +/- 3.0; b's side +1.0 +/- 3.0)
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
    r = parse45(page)
    assert [v[2] for v in r["all"]["veto"]] == ["COUNTS", "investigation item", "AWAITS"] and r["dec"]["veto"] == []
    assert r["all"]["deck_avg"]["hydreigon"] == (51.2, 54.9, 43.9, 3.7)
    for bad in (page.replace("    deck x +3.1: AWAITS mixed rows: 3 of 18 cell sides missing\n", ""),        # a veto line dropped
                page.replace("COUNTS:", "COUNTED:"),                                                         # a status renamed
                page.replace("deck veto (gap grows > 2): x +3.1", "deck veto (gap grows > 2): x +3.1, y +4.0")):  # a line added
        try:
            parse45(bad)
        except SystemExit as e:
            assert "STOP" in str(e.code)
        else:
            raise AssertionError("parse45 accepted a page whose veto lines and summary lines disagree")
    print("selftest ok: route from integers, tau and dMSE boundary logic, veto-line backstop")


if args.selftest:
    selftest()
    sys.exit(0)
if args.parse_page:
    _r = parse45(open(args.parse_page, encoding="utf-8").read(), lenient=True)
    for _nm, _d in _r.items():
        P(f"PARSED {_nm}: cell vetoes {len(_d['sum_cell'])}, deck vetoes {len(_d['sum_deck'])}, "
          f"COUNTS {len(_d['counts'])}, AWAITS {len(_d['awaits'])}, deck-average rows {len(_d['deck_avg'])}, verdict {_d['verdict']!r}")
    sys.exit(0)


# ---------------------------------------------------------------------------------------------------------------
# The kog3 baselines (required: STOP if absent, they are the repo's own).
# ---------------------------------------------------------------------------------------------------------------
def need(p):
    if not os.path.exists(p):
        die(f"baseline file {p} is missing")
    return p


P("kt's reading on kog (amendment 2 of ../kt_2026-09-26/README.md over the text); build " + S)
if REPS == DEFAULT_REPS:
    P(f"score45 bootstrap: --reps {REPS} (score.py's default; its seeds are fixed, so a rerun is identical).")
elif REPS < DEFAULT_REPS:
    P(f"WARNING: --reps {REPS} is BELOW score45's default {DEFAULT_REPS}. The dMSE 95% and tau 90% bounds that gate move with "
      f"--reps. This is a test setting: DO NOT READ THIS OUTPUT AS THE REGISTERED READING.")
else:
    P(f"NOTE: --reps {REPS} is above score45's default {DEFAULT_REPS} (the more precise rerun that a bound near a registered "
      f"line asks for; N9). The bounds below are this run's.")
# Amendment 2, item 2: "**Footprint:** the share of the 45 cells' 22,500 paired games whose moves differ from kog3's. It is read
# first and fixes the route for kt3 and kta3 alike: under 15%, the reserve route; otherwise, the ordinary adoption rule."
# Amendment 1: "Each code's route is fixed by its measured footprint, read before anything else: under 15%, the reserve route;
# 15% or more, the ordinary adoption rule." (Predictions never choose the route; the measured footprint does.)
FPFILE = path("footprint.txt")
if not os.path.exists(FPFILE):
    die(f"{FPFILE} does not exist. kt's four tables are not finished; the footprint fixes each code's route and is "
        f"read first. Nothing else is read.")
FPTXT = open(FPFILE, encoding="utf-8").read()
P("\n1. THE FOOTPRINT (footprint.txt, read first; it fixes each code's route):")
FPL = {}
for ln in FPTXT.splitlines():
    if ln.startswith("FOOTPRINT"):
        P("   " + ln)
        m = re.match(r"^FOOTPRINT (\w+): (\d+) of (\d+) paired games on the 45 cells differ from kog3's = ([\d.]+)% -> (.*)$", ln)
        if not m:
            die(f"footprint.txt line not in the runner's format: {ln!r}")
        FPL[m.group(1)] = (int(m.group(2)), int(m.group(3)), float(m.group(4)), m.group(5))
ROUTE = {}
for c in CODES:
    if c not in FPL:
        die(f"footprint.txt has no FOOTPRINT line for {c}")
    d_, n_, pc_, rt_ = FPL[c]
    if n_ != 22500 or abs(100 * d_ / n_ - pc_) > 0.006:
        die(f"footprint.txt's {c} line is inconsistent ({d_} of {n_} = {pc_}%; the 45 cells have 22,500 paired games)")
    # The route comes from the counts, never from the two-decimal percentage (3,374 of 22,500 prints as 15.00 and is
    # still under 15%); the runner's own route text must agree with it, or the reading stops.
    ROUTE[c] = route_of(d_, n_)
    if not rt_.startswith(("reserve", "ordinary")) or rt_.startswith("reserve") != (ROUTE[c] == "reserve"):
        die(f"footprint.txt's route text for {c} ({rt_!r}) disagrees with the route its counts give ({ROUTE[c]}: {d_} of {n_}; "
            f"15% of {n_} is {15 * n_ // 100} games). Stop and write it down.")

BASE_T = load(need(os.path.join(args.kog_dir, "table_kog3.jsonl")), 14000, ("kog3", "kog3"), "abi")
BASE_N = load(need(os.path.join(args.kog_dir, "new17_kog3.jsonl")), 8500, ("kog3", "kog3"), "abi")
if BASE_T.keys() & BASE_N.keys():
    die("kog3's table and new-cell baselines overlap")
BASE = {**BASE_T, **BASE_N}
CELLS = list(dict.fromkeys((a, b) for a, b, _ in BASE))
if len(CELLS) != 45:
    die(f"the kog3 baseline has {len(CELLS)} cells, not 45")
ICELL = {c: sorted(i for a, b, i in BASE if (a, b) == c) for c in CELLS}
if any(len(v) != 500 for v in ICELL.values()):
    die("a kog3 baseline cell does not have 500 deals")
DECKS = sorted({d for c in CELLS for d in c})


def get45(bot, kind, *codes):
    """The 45 cells' games of `bot` (kind 'both' = the bot on both sides; 'first' / 'second' = the mixed rows with the
    bot on the first-named / second-named deck, kog3 on the other), table + new cells, or None if not in yet."""
    tag = {"both": (f"{S}_{bot}_table.jsonl", f"{S}_{bot}_new17.jsonl", (bot, bot)),
           "first": (f"{S}_mixed_table_{bot}_first.jsonl", f"{S}_mixed_new17_{bot}_first.jsonl", (bot, "kog3")),
           "second": (f"{S}_mixed_table_{bot}_second.jsonl", f"{S}_mixed_new17_{bot}_second.jsonl", ("kog3", bot))}[kind]
    ps = [opt(tag[0], *codes), opt(tag[1], *codes)]
    if not all(ps):
        return None
    rows = {}
    for p, n, base in ((ps[0], 14000, BASE_T), (ps[1], 8500, BASE_N)):
        r = load(p, n, tag[2], "abi")
        same_deals(p, r, base, "kog3")
        rows.update(r)
    return rows, ps


# ---------------------------------------------------------------------------------------------------------------
# 1. Footprint, recomputed from the moves fields only as a cross-check of footprint.txt; per-cell counts feed (c).
# ---------------------------------------------------------------------------------------------------------------
BOTH, FPC = {}, {}
for c in ("kt3", "kta3", "ktb3", "ktc3"):
    r = get45(c, "both", *((c,) if c in CODES else ()))
    if r is None:
        if c in CODES:
            die(f"{c}'s tables are not in although footprint.txt exists")
        continue
    BOTH[c] = r[0]
    diff = [k for k in BASE if BASE[k]["moves"] != r[0][k]["moves"]]
    if c in FPL and len(diff) != FPL[c][0]:
        die(f"footprint.txt says {FPL[c][0]} games differ for {c}; the files give {len(diff)}: stop and write it down")
    FPC[c] = Counter((a, b) for a, b, _ in diff)
P("   cross-check: the moves fields of the files reproduce footprint.txt's counts for " + ", ".join(sorted(BOTH)) + ".")
for c in CODES:
    d_, n_, _pc, _rt = FPL[c]
    P(f"   {c}: {d_:,} of {n_:,} = {100 * d_ / n_:.4f}% (15% is {15 * n_ // 100:,} games) -> "
      f"{'RESERVE ROUTE, clauses (a)-(e)' if ROUTE[c] == 'reserve' else 'ORDINARY ADOPTION RULE (15% or more)'}"
      f"; {len(FPC[c])} of 45 cells have a changed game; the route was decided from the counts and agrees with footprint.txt's own route text")


def preconditions():
    """Item 7's identity and item 4's timing are enforced by run_kt.sh (it dies before any table if either fails). Restated
    here, from the files it left, so the reading records that they passed. identity_check.txt holds only kog3, k3, kp3,
    kq3, kd3 and kpr3 replays (no kt outcome); the timing files hold wall and CPU seconds."""
    P("\n1b. PRECONDITIONS (item 7 identity; item 4 timing). run_kt.sh dies before the tables if either fails; restated from its files:")
    ip = path("identity_check.txt")
    if not os.path.exists(ip):
        die(f"{ip} does not exist: item 7's identity replays are not recorded, so no kt game is read")
    seen, lines = [], [ln.strip() for ln in open(ip, encoding="utf-8") if ln.strip()]
    for ln in lines:
        m = re.match(r"^(.+): (\d+) of (\d+) equal on ", ln)
        if not m:
            die(f"identity_check.txt line not in the runner's format: {ln!r}")
        if m.group(2) != m.group(3) or int(m.group(3)) == 0:
            die(f"IDENTITY FAILED in identity_check.txt: {ln!r}. Item 7 needs every replay equal; nothing is read.")
        if m.group(1) not in [x[0] for x in seen]:
            seen.append((m.group(1), int(m.group(3))))
    if len(seen) < 13:
        die(f"identity_check.txt records {len(seen)} distinct replays; item 7's list has 13 (k3, kp3, kog3 table and new cells, "
            f"kq3, kd3, kpr3, kog3 on B2e, on Scizor and on the four second lists)")
    P(textwrap.fill(f"identity: {len(seen)} distinct replays, every one equal (games equal / games): " +
                    "; ".join(f"{k} {n:,}" for k, n in seen), width=118, initial_indent="   ", subsequent_indent="      "))
    tp = next((p for p in (path(f"{S}_timing_2.txt"), path(f"{S}_timing_1.txt")) if os.path.exists(p)), None)
    if tp is None:
        die(f"neither {S}_timing_1.txt nor {S}_timing_2.txt exists: item 4's timing run is not recorded")
    tl = " ".join(open(tp, encoding="utf-8").read().split())
    P(f"   timing ({os.path.basename(tp)}" + ("; the second pair decides" if tp.endswith("_2.txt") else "") + f"): {tl}")
    if "limit 1.25: within" not in tl:
        die(f"timing line is not 'within' the 1.25x limit ({tl!r}): item 4 says the per-leaf Tool classification is rewritten "
            f"before the table, so nothing is read")


preconditions()
if args.footprint_only:
    P("\n(--footprint-only: stopped after sections 1 and 1b.)")
    sys.exit(0)

# Limitless development-half cells of the 45 (as score45.py builds them).
_v2 = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
LIM = {tuple(k.split("|")): tuple(v) for k, v in _v2.items()}
_PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
_new17 = [(d, o) for d in ("rayquaza", "altaria_greninja") for o in _PANEL] + [("rayquaza", "altaria_greninja")]
with open(os.path.join(RES, "gauntlet_runs_2026-09-26", "gauntlet_cells.csv"), encoding="utf-8", newline="") as _f:
    _gc = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(_f)}
for _a, _b in _new17:
    _r = _gc[("development", _a, _b)]
    LIM[(_a, _b)] = (int(_r["W"]), int(_r["L"]), int(_r["T"]))
if any(c not in LIM for c in CELLS):
    die("a cell of the kog3 baseline has no Limitless development cell: " + str([c for c in CELLS if c not in LIM]))


def limit(c):
    w, l, t = LIM[c]
    n = w + l + t
    L = (w + 0.5 * t) / n
    return 100 * L, n, 196 * math.sqrt(L * (1 - L) / n)


NOTES = """
NOTES: where the registration's text is ambiguous, and the reading coded (the conservative one where they differ)
 N1  Frame. Amendment 2 item 2 reads the 45 cells with Altaria v Sceptile included. score45.py prints that block ("all
     cells: 45 pairings") and score.py's own 44-cell decision set beside it. The 45-cell block gates. Beside it, the
     44-cell block is compared on the CHOSEN route's tests only (reserve: the tau lower bound against -1.0 and the vetoes
     that count; ordinary: dMSE below 0 and the vetoes that count); a difference is a NOTE and gates nothing. The other
     route's number is never printed here (N11).
 N2  Event-resampled intervals. The registration says "beside the match-level one, as the standing column requires";
     they are printed beside and gate nothing. The match-level interval gates. A by-event tau bound on the other side of
     -1.0 from the match-level one is flagged in b1's detail and gates nothing.
 N3  Clause (b)'s "no rule-v2 veto" is coded as: no cell or deck veto COUNTS on the 45 cells through the code's mixed
     rows (score45.py's v2), plus the B2e held-out veto (item 4: "on the reserve route its (b) includes the held-out
     veto"). The Scizor and second-list vetoes (Dustin's coverage ruling; "a veto there blocks the takeover") are
     separate coverage gates that adoption needs; they are not folded into (b).
 N4  A B2e held-out veto is own-side harm in the mixed rows (the 95% interval wholly below zero), as amendment 4 / RUN5
     and read_koh.py 6d read it. Item 4's older text ("more than 2 points further ... is a veto, through mixed rows")
     would need both; the stricter reading (harm alone) is coded. "More than 2 further" without harm is an
     investigation item and is printed. Dustin's files (48-95) are reported, never counted. The gate's detail counts the
     held-out decks with harm but not more than 2 further, and with more than 2 further but no harm, so a reader can
     see which reading would flip the gate.
 N5  Clause (c), "no meta deck's own side worse beyond noise": coded per deck, pooled over the deck's cells where the
     code's footprint is not zero (both seat orders), worse = the pooled 95% interval wholly below zero (koa's clause (c)
     shape). Single cell-sides beyond noise are listed and gate nothing (rule v2's cell veto covers cells). The mixed
     rows of a cell whose footprint IS zero must equal kog3's games (a pilot's choice is a function of the position); a
     difference there is an INTEGRITY line, status PENDING, never a registered FAIL: the registration has no such clause,
     and what it would mean (that clause (c)'s cell set is incomplete) is a human read.
 N6  Clause (d), "gain beyond paired noise": the code on the Rayquaza list against kog3 on it, kog3 on the panel in both
     arms, pooled over the 8 rows (mean of row means; half-width 1.96 x sqrt(sum of row variances) / 8, the variation
     check's); a gain = mean minus half-width above zero. kt3's (d) gates when kt3 is on the reserve route (item 2:
     "kt3's own test, not a second chance for kta3's"); kta3's gates on the reserve route; at 15% or more (d) is reported
     and gates nothing (item 2), and a d file that is not in yet then holds no verdict.
 N7  Suicune's rows. Amendment 1 says seven, amendment 2 item 3 says nine (7 table + 2 new cells). Both the nine and
     the table seven are printed as a report. On the reserve route the same rows enter clause (c) (Suicune's own side
     pooled over its cells where the footprint is not zero); the (d) gate is Rayquaza's rows only.
 N8  Clause (e), "adoption for the screen and the table together", is not a test: it is the pair's joint outcome below.
 N9  Printed precision and Monte-Carlo noise. A tau margin lower bound is printed to two decimals: one printed as -1.00
     is not called (PENDING; read at more digits). A bound within 0.10 of -1.0 (tau), or a dMSE upper bound within 5% of
     the interval's width of 0, is inside the bootstrap's Monte-Carlo error (score.py's seeds are fixed, so the answer
     moves with --reps): below --reps 20000 it is PENDING, and the --reps 20000 rerun decides. Fixed here, before any
     kt outcome is seen, so the rerun is a rule and not a choice.
 N10 Coverage "beyond paired noise": Scizor's and the second lists' pooled interval is the variation check's (1.96 x
     sqrt(sum of per-cell variances of the mean difference) / cells), as read_koh.py uses it. Their accuracy is reported.
 N11 Only the route the footprint chose gets a verdict. score45's full page (which also holds the other route's numbers)
     is saved to the pages folder and is not read into this report.
 N12 Coverage gates on the reserve route. Item 4's sentence puts the held-out veto into (b) on the reserve route, and
     names the Scizor and second-list no-harm tests only for the ordinary rule (item 2). Here all three gate on both
     routes: "a veto there blocks the takeover" (item 4), RUN5, and Dustin's "no deck hurt". If the only failure of a
     reserve-route code is the Scizor or a second-list test, the verdict line says so, so the reading that decided is
     visible. Each coverage test is one own-side test at a one-sided 2.5% false-veto chance (roughly a fifth to a quarter
     over all 11 for a neutral code with a big footprint); a coverage veto that is the only failure is reported with that
     count.
 N13 Preconditions (item 7 identity, item 4 timing) are enforced by run_kt.sh; the reader restates them from the files it
     left (section 1b) and stops if either is absent or failed. The B2e kog3 baseline's sha256 is printed (section 5).
"""
P(NOTES)

# ---------------------------------------------------------------------------------------------------------------
# Statistics shared by the clauses (score.py's own definitions, restated).
# ---------------------------------------------------------------------------------------------------------------


def mv(d):
    """Mean of per-deal differences and the variance of that mean (score.py mean_var)."""
    n = len(d)
    m = sum(d) / n
    return m, sum((x - m) ** 2 for x in d) / max(n - 1, 1) / n


def pool(parts):
    """Stratified pool over cells (score.py side_change): (mean of cell means, 95% half-width, deals)."""
    q = [mv(d) for d in parts]
    return sum(m for m, _ in q) / len(q), 1.96 * math.sqrt(sum(v for _, v in q)) / len(q), sum(len(d) for d in parts)


def fmt(m, h):
    return f"{m:+.2f} +/- {h:.2f}"


GATES = {c: [] for c in CODES}  # (id, label, status, detail); status PASS / FAIL / PENDING


def gate(code, gid, label, status, detail):
    GATES[code].append((gid, label, status, detail))


# ---------------------------------------------------------------------------------------------------------------
# 2. The 45 cells: score45.py, rules v2, with the code's mixed rows.
# ---------------------------------------------------------------------------------------------------------------
BASE_TABLE_P, BASE_N17_P = os.path.join(args.kog_dir, "table_kog3.jsonl"), os.path.join(args.kog_dir, "new17_kog3.jsonl")
MIX = {}  # code -> {'first': rows, 'second': rows}


def run_score45(bot, with_mixed):
    both_p = [path(f"{S}_{bot}_table.jsonl"), path(f"{S}_{bot}_new17.jsonl")]
    mixed = []
    if with_mixed:
        for kind in ("first", "second"):
            r = get45(bot, kind, bot) if bot in CODES else None
            if r:
                MIX.setdefault(bot, {})[kind] = r[0]
                mixed += r[1]
    page = os.path.join(PAGES, f"score45_{bot}_vs_kog3.txt")
    inputs = [BASE_TABLE_P, BASE_N17_P] + both_p + mixed
    cmd = [sys.executable, os.path.join(K45, "score45.py"), "--rules", "v2", "--old-games", BASE_TABLE_P, BASE_N17_P,
           "--new-games"] + both_p + ["--old", "kog3", "--new", bot]
    if mixed:
        cmd += ["--mixed"] + mixed
    cmd += ["--reps", str(REPS)]  # always explicit, so the page records which run it is
    # The page itself does not record --reps, and both gating bounds move with it: a sidecar records the command (inputs
    # and --reps) that made the page, and a page is reused only if it was made by exactly this command.
    sig, side = json.dumps({"reps": REPS, "cmd": cmd[1:]}, sort_keys=True), page + ".reps"
    same_cmd = os.path.exists(side) and open(side, encoding="utf-8").read() == sig
    if (args.reuse_45 and same_cmd and os.path.exists(page)
            and os.path.getmtime(page) > max(os.path.getmtime(p) for p in inputs)):
        text, tag = open(page, encoding="utf-8").read(), f"reused: newer than every input, made by this same command, --reps {REPS}"
    else:
        if args.reuse_45 and os.path.exists(page):
            P(f"   (--reuse-45: {os.path.basename(page)} is not reusable"
              f" ({'a different command or --reps, or no sidecar' if not same_cmd else 'an input is newer'}); scoring afresh)")
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=K45)
        text, tag = out.stdout + out.stderr, f"freshly scored, --reps {REPS}"
        os.makedirs(PAGES, exist_ok=True)
        with open(page, "w", encoding="utf-8") as f:
            f.write(text)
        if out.returncode:
            die(f"score45.py failed for {bot} (exit {out.returncode}); nothing read from it:\n{text[-600:]}")
        with open(side, "w", encoding="utf-8") as f:
            f.write(sig)
    if "45 common pairings" not in text:
        die(f"score45.py did not read 45 common pairings for {bot} (see {page})")
    return parse45(text), page, tag, bool(mixed)


R45 = {}
P("\n2. THE 45 CELLS (score45.py --rules v2, kog3 current against the code new, paired by deal, with the code's mixed rows).")
P("   Only the route the footprint chose is read below; the full page, with everything, is saved as score45_<code>_vs_kog3.txt.")
for c in CODES:
    P(f"\n   [{c}] route: {ROUTE[c].upper()}")
    r, page, tag, had_mixed = run_score45(c, True)
    R45[c] = r
    A, Dn = r["all"], r["dec"]
    P(f"   page: {os.path.basename(page)} ({tag}); mixed rows given to score45: "
      f"{', '.join(k for k in ('first', 'second') if k in MIX.get(c, {})) or 'none in yet'}")
    P(f"   real error on the 45 cells: kog3 {A['real']['kog3']:.1f} -> {c} {A['real'][c]:.1f}")
    t = A["tau"]
    P(f"   tau margin (kog3 minus {c}): {t[0]:+.2f}, 90% interval {t[1]:+.2f} to {t[2]:+.2f}; "
      f"by event (beside): {A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f}")
    veto_txt = "; ".join(f"{w} (+{g:.1f}) {txt[:200]}" for w, g, k, txt in A["veto"] if k in ("COUNTS", "AWAITS")) or "none"
    P(f"   rule-v2 vetoes that count or await mixed rows (45 cells): {veto_txt}")
    inv = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "investigation item"]
    nev = [f"{w} (+{g:.1f})" for w, g, k, _ in A["veto"] if k == "never counts"]
    P(f"   investigation items (neither side worse): {', '.join(inv) or 'none'}; never count (band over +/-15): {', '.join(nev) or 'none'}")
    if ROUTE[c] == "reserve":
        # Clause (a): "(a) footprint under 15% on the same paired files".
        gate(c, "a", "footprint under 15%", "PASS", f"{FPL[c][0]:,} of {FPL[c][1]:,} = {100 * FPL[c][0] / FPL[c][1]:.4f}%")
        # Clause (b), first half: "(b) the tau margin (kog3 minus kt3), 90% lower bound at -1.0 or above" (kt3, item 2);
        # "tau margin (kp3 minus kta3) 90% lower bound at -1.0 or above" (original (b), kp3 read as kog3).
        lo = t[1]
        st, notes = tau_gate(lo, A["tau_ev"][0], REPS)
        gate(c, "b1", "tau margin 90% lower bound >= -1.0", st,
             f"{lo:+.2f} (margin {t[0]:+.2f}, interval {t[1]:+.2f} to {t[2]:+.2f}; by event {A['tau_ev'][0]:+.2f} to {A['tau_ev'][1]:+.2f})"
             + "".join("; " + x for x in notes))
        # Clause (b), second half: "and no rule-v2 veto" (rule v2: a veto counts only through mixed rows).
        if A["counts"]:
            st, dt = "FAIL", "counts: " + "; ".join(v[0] for v in A["counts"])
        elif A["awaits"]:
            st, dt = "PENDING", "awaits mixed rows: " + "; ".join(v[0] for v in A["awaits"])
        else:
            st, dt = "PASS", "none counts" + (f" ({len(A['veto'])} veto candidates, all investigation items or never-count)" if A["veto"] else "")
        gate(c, "b2", "no rule-v2 veto on the 45 cells", st, dt)
    else:
        # The ordinary rule: "paired dMSE against kog3 on the 45 cells, with the whole 95% interval below zero.
        # Vetoes are rule v2's, counting only through mixed rows against kog3 on the same deals."
        dm = A["dmse"]
        P(f"   dMSE ({c} - kog3): {dm[0]:+.1f} points^2, 95% interval {dm[1]:+.1f} to {dm[2]:+.1f} "
          f"({'below 0' if dm[3] else 'NOT below 0'}); by event (beside): {A['dmse_ev'][0]:+.1f} to {A['dmse_ev'][1]:+.1f} "
          f"({'below 0' if A['dmse_ev'][2] else 'not below 0'})")
        # Reported beside, gating nothing (Sept 29, after the eval-power check ../eval_power_2026-09-29/, added before
        # any kt result was read): the smallest true dMSE this reading's own interval could detect. sd from the 95%
        # interval's width; clearing zero half the time needs 1.96 sd, 80% of the time 2.80 sd (Normal rule).
        sd45 = (dm[2] - dm[1]) / 3.92
        P(f"   power (reported beside, gating nothing): sd {sd45:.1f}; this reading detects a true dMSE of about "
          f"{-1.96 * sd45:+.1f} half the time and {-2.80 * sd45:+.1f} 80% of the time (../eval_power_2026-09-29/)")
        st, notes = dmse_gate(dm[3], dm[1], dm[2], REPS)
        gate(c, "o1", "dMSE 95% interval wholly below 0", st,
             f"{dm[0]:+.1f} ({dm[1]:+.1f} to {dm[2]:+.1f}); by event {A['dmse_ev'][0]:+.1f} to {A['dmse_ev'][1]:+.1f} "
             f"({'below' if A['dmse_ev'][2] else 'NOT below'} 0, beside)" + "".join("; " + x for x in notes))
        if A["counts"]:
            st, dt = "FAIL", "counts: " + "; ".join(v[0] for v in A["counts"])
        elif A["awaits"]:
            st, dt = "PENDING", "awaits mixed rows: " + "; ".join(v[0] for v in A["awaits"])
        else:
            st, dt = "PASS", "none counts"
        gate(c, "o2", "no rule-v2 veto on the 45 cells", st, dt)
        P(f"   tau margin (kog3 minus {c}), reported beside: {t[0]:+.2f}, 90% interval {t[1]:+.2f} to {t[2]:+.2f}")
    # N1: the 44-cell decision set beside, on the chosen route's tests only (never the other route's number).
    dd = Dn
    diffs = []
    if ROUTE[c] == "ordinary" and dd["dmse"][3] != A["dmse"][3]:
        diffs.append(f"dMSE below 0: 45 cells {A['dmse'][3]}, 44 cells {dd['dmse'][3]}")
    if ROUTE[c] == "reserve" and (dd["tau"][1] >= -1.0) != (A["tau"][1] >= -1.0):
        diffs.append(f"tau lower bound vs -1.0: 45 cells {A['tau'][1]:+.2f}, 44 cells {dd['tau'][1]:+.2f}")
    if {v[0] for v in dd["counts"]} != {v[0] for v in A["counts"]}:
        diffs.append(f"vetoes that count: 45 cells {[v[0] for v in A['counts']]}, 44 cells {[v[0] for v in dd['counts']]}")
    P("   NOTE (N1): the 44-cell decision set (Altaria v Sceptile quarantined) " +
      ("reads differently: " + "; ".join(diffs) + ". The 45-cell block gates." if diffs else "gives the same gate outcomes."))

# ---------------------------------------------------------------------------------------------------------------
# 3. Clause (c) (reserve route): mixed rows on the cells where the footprint is not zero, both directions.
# ---------------------------------------------------------------------------------------------------------------


def own_deltas(code, deck, cell):
    """Per-deal change of `deck`'s own score in `cell` with the code on that deck only, kog3 on the other, against
    kog3 on both (points; a positive number is better)."""
    a, b = cell
    kind, sign = ("first", 1) if deck == a else ("second", -1)
    rows = MIX[code][kind]
    return [sign * 100 * (rows[(a, b, i)]["first_deck_score"] - BASE[(a, b, i)]["first_deck_score"]) for i in ICELL[cell]]


def deck_report(code, deck, cells, indent="   "):
    parts = [own_deltas(code, deck, c) for c in cells]
    m, h, n = pool(parts)
    return m, h, n, {c: (mv(p)[0], 1.96 * math.sqrt(mv(p)[1])) for c, p in zip(cells, parts)}


for c in CODES:
    if ROUTE[c] != "reserve":
        continue
    P(f"\n3. [{c}] CLAUSE (c), the mixed rows of the cells where {c}'s footprint is not zero, both directions, 500 deals.")
    # Clause (c): "(c) the 45 cells' mixed rows wherever kt3's footprint isn't zero, both directions, 500 deals"
    # (kta3: "mixed rows for the pairings where kta3's footprint is non-zero ... no meta deck's own side worse beyond noise").
    if set(MIX.get(c, {})) != {"first", "second"}:
        gate(c, "c", "no deck's own side worse beyond noise (mixed rows)", "PENDING", "mixed rows not all in yet")
        P("   mixed rows not all in yet: clause (c) waits.")
        continue
    active = [cell for cell in CELLS if FPC[c][cell] > 0]
    worse, lines = [], []
    for deck in DECKS:
        cells = [cell for cell in active if deck in cell]
        if not cells:
            continue
        m, h, n, per = deck_report(c, deck, cells)
        bad = m + h < 0
        if bad:
            worse.append(deck)
        lines.append(f"   {deck:>17}: own side {fmt(m, h)} over {len(cells)} cells ({n:,} deals)" + ("  <- WORSE beyond noise" if bad else ""))
        for cell, (mm, hh) in per.items():
            if mm + hh < 0:
                lines.append(f"{'':21}(listed, gates nothing) {cell[0]} v {cell[1]}: {fmt(mm, hh)}")
    P(f"   cells with a changed game: {len(active)} of 45 " + (f"({', '.join(f'{a} v {b}' for a, b in active)})" if active and len(active) <= 12 else ""))
    P("\n".join(lines) if lines else "   no cell has a changed game: nothing to read (every mixed row is an identity).")
    zero = [(kind, k) for kind in ("first", "second") for k in MIX[c][kind] if FPC[c][(k[0], k[1])] == 0 and MIX[c][kind][k]["moves"] != BASE[k]["moves"]]
    if zero:
        zc = sorted({f"{k[0]} v {k[1]}" for _, k in zero})
        P(f"   INTEGRITY (not a registered clause; PENDING, never a FAIL): {len(zero)} mixed-row games in {len(zc)} zero-footprint "
          f"cells differ from kog3's moves (expected 0): {', '.join(zc[:8])}{' ...' if len(zc) > 8 else ''}. A pilot's choice "
          f"is a function of the position, so this means the footprint set clause (c) reads is incomplete or a file is wrong: "
          f"STOP and read it by hand before any verdict is written down (N5).")
        gate(c, "c0", "INTEGRITY (unregistered): mixed rows in unchanged cells equal kog3's games", "PENDING",
             f"{len(zero)} games in {len(zc)} cells differ: needs a human read; this can never be a registered FAIL")
    else:
        P("   integrity: every mixed-row game in a zero-footprint cell equals kog3's moves.")
    gate(c, "c", "no deck's own side worse beyond noise (mixed rows)", "FAIL" if worse else "PASS",
         ("worse: " + ", ".join(worse)) if worse else f"{len(active)} cells read, no deck worse")

# ---------------------------------------------------------------------------------------------------------------
# 4. Clause (d): the census Rayquaza list's eight rows, on the 22,700,000,000 block.
# ---------------------------------------------------------------------------------------------------------------
P("\n4. CLAUSE (d), the census Rayquaza list v the eight table lists (8 x 500 deals per arm; seeds 22,700,000,000 + panel index x 10,000 + i).")
# Amendment 1: "The test: kta3's own-side gain beyond paired noise on the Dragonair Mega Rayquaza ex list, pooled over its
# eight rows against the panel lists. One arm has kta3 on the Rayquaza list, the other kp3 [kog3]; kp3 [kog3] plays the panel
# list in both. 8 x 500 deals per arm (8,000 games)." (kt3: "kt3's own-side gain beyond paired noise on the census Rayquaza
# list's eight rows, on the same seeds and at the same size as kta3's (kt3's own test, not a second chance for kta3's)".)
D_OPP = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
RES_CODES = tuple(c for c in CODES if ROUTE[c] == "reserve")  # only these codes' verdicts wait for (d)'s files (N6)
_dbp = opt(f"{S}_d_kog3.jsonl", *RES_CODES)
DBASE = None
if _dbp:
    DBASE = load(_dbp, 4000, ("kog3", "kog3"), "pi")
    if {k for k in DBASE} != {(p, i) for p in range(8) for i in range(500)}:
        die(f"{_dbp}: not pairings 0-7 x deals 0-499")
    if any(g["seed"] != 22_700_000_000 + 10_000 * p + i for (p, i), g in DBASE.items()):
        die(f"{_dbp}: seeds are not 22,700,000,000 + pairing x 10,000 + i")
_cens = None
_cp = os.path.join(RES, "kt_carrier_census_2026-09-26", "cells_c-dragonair_mega_rayquaza_ex.csv")
if os.path.exists(_cp):
    _cens = {r["opponent"]: float(r["score_pct"]) for r in csv.DictReader(open(_cp, encoding="utf-8")) if r["dataset"] == "pooled"}
DROWS = {}
for c in CODES:
    _p = opt(f"{S}_d_{c}.jsonl", *((c,) if ROUTE[c] == "reserve" else ()))
    if not _p or DBASE is None:
        if ROUTE[c] == "reserve":
            gate(c, "d", "Rayquaza own-side gain beyond paired noise", "PENDING", "the d rows are not all in yet")
        else:
            P(f"   [{c}] (d) rows not all in yet: reported only on the ordinary route, they hold no verdict.")
        continue
    X = load(_p, 4000, (c, "kog3"), "pi")
    same_deals(_p, X, DBASE, "kog3 on the Rayquaza list")
    parts = [[100 * (X[(p, i)]["first_deck_score"] - DBASE[(p, i)]["first_deck_score"]) for i in range(500)] for p in range(8)]
    m, h, n = pool(parts)
    DROWS[c] = (m, h)
    P(f"\n   [{c}] on the Rayquaza list (side a) against kog3 on it, kog3 on the panel in both arms:")
    for p, o in enumerate(D_OPP):
        sb = 100 * sum(DBASE[(p, i)]["first_deck_score"] for i in range(500)) / 500
        sx = 100 * sum(X[(p, i)]["first_deck_score"] for i in range(500)) / 500
        rm, rv = mv(parts[p])
        lim_txt = f"; Limitless (census list, pooled) {_cens[o]:.1f}" if _cens and o in _cens else ""
        P(f"     v {o:9}: kog3 {sb:5.1f} -> {c} {sx:5.1f} ({rm:+.2f} +/- {1.96 * math.sqrt(rv):.2f}){lim_txt}")
    gain = m - h > 0
    if _cens:
        P(f"     (census Limitless, equal-weight over the eight, pooled: 46.3 +/- 4.8 over 606 matches; the before/after figures above "
          f"are the simulator's on that list, reported, gating nothing)")
    P(f"   pooled over 8 rows ({n:,} deals): {fmt(m, h)} points -> {'a GAIN beyond paired noise' if gain else 'NO gain beyond paired noise'}"
      f" ({'gates' if ROUTE[c] == 'reserve' else 'reported, gates nothing on the ordinary route'})")
    if ROUTE[c] == "reserve":
        gate(c, "d", "Rayquaza own-side gain beyond paired noise", "PASS" if gain else "FAIL", fmt(m, h) + " points, pooled over 8 rows")

# ---------------------------------------------------------------------------------------------------------------
# 5. Coverage (item 4; Dustin: "coverage rows count for the mixed-row veto and are reported for accuracy").
# ---------------------------------------------------------------------------------------------------------------
P("\n5. COVERAGE (item 4; own-side mixed rows worse beyond paired noise = a veto that blocks the takeover; accuracy is reported).")
# Item 4: "Coverage is run for kt3, and for kta3 by either route ... every B2e held-out deck ... every Scizor and second-list
# row"; "B2e's held-out archetypes (pairings 0-47): one moving more than 2 points further from its Limitless pooled
# equal-weight average is a veto, through mixed rows as above. The development half's figure is printed beside ... Dustin's
# files (48-95) are reported beside."
B2E_TSV = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(B2E_DIR, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
LIMB = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E_DIR, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        LIMB[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
ARCH = sorted({k for k, _ in LIMB["pooled"]})


def _b2e_default():
    cands = [os.path.join(RES, "koh_2026-09-28", "reading", "b2e_kog3.jsonl"), "/tmp/kt_ref_b2e_kog3.jsonl", "/tmp/koh_cloud/b2e_kog3.jsonl"]
    for p in cands:
        if os.path.exists(p):
            return p
    tmp = os.path.join(tempfile.gettempdir(), "kt_read_b2e_kog3.jsonl")
    out = subprocess.run(["git", "-C", os.path.dirname(os.path.dirname(RES)), "show",
                          "origin/claude/pensive-ptolemy-spwc0b:rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl"], capture_output=True)
    if out.returncode:
        die("b2e_kog3.jsonl (the cloud's kog3 baseline for B2e) is nowhere: pass --b2e-kog3")
    open(tmp, "wb").write(out.stdout)
    return tmp


B2E_BASE_P = args.b2e_kog3 or _b2e_default()
B2E_BASE = load(need(B2E_BASE_P), 48000, ("kog3", "kog3"), "pi")
P(f"   B2e kog3 baseline used: {B2E_BASE_P}\n     sha256 {hashlib.sha256(open(B2E_BASE_P, 'rb').read()).hexdigest()} "
  f"(the runner's i<40 identity check read /tmp/kt_ref_b2e_kog3.jsonl; a /tmp file or a branch can move, so the hash is printed; "
  f"copy the file into the results folder before the real run if it is not there)")


def panel(rows):
    by = defaultdict(list)
    for (p, i), g in rows.items():
        r = B2E_TSV[p]
        by[(r["block"], r["held_key"], r["opponent"])].append(g["first_deck_score"])
    res = defaultdict(dict)
    for (block, k, o), s in by.items():
        res[(block, k)][o] = 100 * sum(s) / len(s)
    return res


def arch_of(k):
    base = k.replace("dustin_", "")
    return next((n for n in ARCH if n == base), None) or next((n for n in ARCH if n.startswith(base)), None)


COV = {c: {} for c in CODES}


def pooled_by_group(base, new, keys_by_group, own):
    return pool([[100 * (own(new[k]) - own(base[k])) for k in ks] for ks in keys_by_group])


fds = lambda g: g["first_deck_score"]  # noqa: E731

for c in CODES:
    P(f"\n   [{c}] 5a. B2e's held-out archetypes (panel average, equal-weight over 8 opponents; Limitless pooled, development beside):")
    pb = opt(f"{S}_b2e_{c}.jsonl", c)
    pm = opt(f"{S}_mixed_b2e_{c}_first.jsonl", c)
    FUR = {}
    if pb:
        NEW = load(pb, 48000, (c, c), "pi")
        same_deals(pb, NEW, B2E_BASE, "b2e_kog3")
        a_, b_ = panel(B2E_BASE), panel(NEW)
        for (block, k) in sorted(a_):
            x, y = sum(a_[(block, k)].values()) / 8, sum(b_[(block, k)].values()) / 8
            arch = arch_of(k)
            cells = [o for o in a_[(block, k)] if (arch, o) in LIMB["pooled"]]
            L = sum(LIMB["pooled"][(arch, o)] for o in cells) / len(cells)
            Ld = [LIMB["development"][(arch, o)] for o in cells if (arch, o) in LIMB["development"]]
            fur = abs(y - L) - abs(x - L)
            FUR[k] = (block, fur)
            P(f"     {block} {k:24} kog3 {x:5.1f} -> {c} {y:5.1f}; Limitless {L:5.1f} (dev {sum(Ld) / len(Ld):5.1f}); further by {fur:+.1f}"
              + (" (MORE THAN 2 further)" if fur > 2 and block.startswith("A") else ""))
    if pm:
        MB = load(pm, 48000, (c, "kog3"), "pi")
        same_deals(pm, MB, B2E_BASE, "b2e_kog3")
        P(f"   [{c}] 5a'. B2e's own side in the mixed rows ({c} on the held deck, kog3 on the panel, against kog3 on both):")
        held = sorted({B2E_TSV[p]["held_key"] for p in range(96)}, key=lambda k: min(p for p in range(96) if B2E_TSV[p]["held_key"] == k))
        vetoes, harm_only, fur_only, n_ho = [], [], [], 0
        for k in held:
            ps = [p for p in range(96) if B2E_TSV[p]["held_key"] == k]
            m, h, n = pooled_by_group(B2E_BASE, MB, [[(p, i) for i in range(500)] for p in ps], fds)
            block = B2E_TSV[ps[0]]["block"]
            harm = m + h < 0
            fur = FUR.get(k, (block, None))[1]
            if block.startswith("A"):
                n_ho += 1
                further = fur is not None and fur > 2
                tag = "VETO (own side worse beyond paired noise)" if harm else \
                    ("investigation item (more than 2 further, own side not worse)" if further else "no harm")
                if harm:
                    vetoes.append(k)
                    if fur is not None and not further:
                        harm_only.append(k)   # harm, but not more than 2 further: the stricter reading vetoes it (N4)
                elif further:
                    fur_only.append(k)        # more than 2 further, no harm: the literal wording would veto it (N4)
            else:
                tag = "reported (Dustin's file)" + ("; own side worse beyond paired noise" if harm else "")
            P(f"     {block} {k:24} own side {fmt(m, h)} over {len(ps)} rows" + (f"; further by {fur:+.1f}" if fur is not None else "") + f" -> {tag}")
        P(f"   B2e held-out veto: {'none' if not vetoes else ', '.join(vetoes)}")
        cnt = (f"{n_ho} held-out decks read; harm but not more than 2 further: {', '.join(harm_only) or 'none'}; "
               f"more than 2 further but no harm: {', '.join(fur_only) or 'none'}" + ("" if FUR else "; further-by not known, the both-sides file is not in yet"))
        P(f"   (N4) {cnt}")
        COV[c]["n_b2e"] = n_ho
        COV[c]["b2e"] = ("FAIL", "B2e held-out veto: " + ", ".join(vetoes) + f" ({cnt})") if vetoes else ("PASS", f"no held-out deck's own side worse beyond noise ({cnt})")
    else:
        COV[c]["b2e"] = ("PENDING", "B2e own-side mixed rows not in yet")
    # 5b. Scizor.
    # Item 4: "A veto: Scizor's own-side average over its 8 rows falls by more than 2 points, and its paired 95% interval lies
    # wholly below zero" -- read under Dustin's ruling as own-side harm alone (interval wholly below zero); accuracy reported.
    P(f"\n   [{c}] 5b. The Scizor row (8 rows x 500; own side = {c} on Scizor, kog3 on the panel list, against kog3 on both):")
    SB = load(need(os.path.join(args.cov_dir, "scizor_kog3.jsonl")), 4000, ("kog3", "kog3"), "pi")
    # s2 (the other direction) is reported only, so it holds no verdict: no code is named for it.
    sp, s1, s2 = opt(f"{S}_scizor_{c}.jsonl", c), opt(f"{S}_mixed_scizor_{c}_first.jsonl", c), opt(f"{S}_mixed_scizor_{c}_second.jsonl")
    if sp:
        SX = load(sp, 4000, (c, c), "pi")
        same_deals(sp, SX, SB, "scizor_kog3")
        P(f"     Scizor's panel average, both sides: kog3 {100 * sum(map(fds, SB.values())) / 4000:.1f} -> {c} {100 * sum(map(fds, SX.values())) / 4000:.1f}"
          f" (reported; Scizor's real figure 32.2 +/- 10.2 pooled, 25.7 +/- 11.7 development, gates nothing)")
    if s1:
        M1 = load(s1, 4000, (c, "kog3"), "pi")
        same_deals(s1, M1, SB, "scizor_kog3")
        m, h, n = pooled_by_group(SB, M1, [[(p, i) for i in range(500)] for p in range(8)], fds)
        harm = m + h < 0
        # Item 4 words the veto as a fall of more than 2 points AND an interval wholly below zero; read here as harm alone
        # (Dustin's ruling, N4/N10). When the fall is not over 2 points the difference is stated, so the reading that decided is visible.
        soft = harm and m > -2
        P(f"     own side: {fmt(m, h)} over 8 rows -> {'VETO (own side worse beyond paired noise)' if harm else 'no harm'}"
          + (f" (the fall, {-m:.2f}, is NOT more than item 4's 2 points: vetoed as harm alone)" if soft else ""))
        COV[c]["scizor"] = (("FAIL", f"Scizor own side {fmt(m, h)}" + ("; the fall is not more than item 4's 2 points (harm alone)" if soft else ""))
                            if harm else ("PASS", f"Scizor own side {fmt(m, h)}"))
    else:
        COV[c]["scizor"] = ("PENDING", "Scizor own-side mixed rows not in yet")
    if s2:
        M2 = load(s2, 4000, ("kog3", c), "pi")
        same_deals(s2, M2, SB, "scizor_kog3")
        m, h, n = pool([[-100 * (M2[(p, i)]["first_deck_score"] - SB[(p, i)]["first_deck_score"]) for i in range(500)] for p in range(8)])
        P(f"     the other direction ({c} on the panel list, kog3 on Scizor), the panel's side: {fmt(m, h)} (reported only)")
    # 5c. The second lists.
    P(f"\n   [{c}] 5c. The four second lists (own side = {c} on the list, kog3 on the other deck, against kog3 on both; accuracy reported):")
    v2dev = _v2
    lists_bad, lists_pending, lists_soft, lists_fur = [], [], [], []
    for v in ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy"):
        rows = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(TSV, f"var_{v}.tsv"), encoding="utf-8"), delimiter="\t")}
        side = {p: r["variant_side"] for p, r in rows.items()}
        sa = sorted(p for p, s in side.items() if s == "a")
        sb_ = sorted(p for p, s in side.items() if s == "b")
        own = lambda g: g["first_deck_score"] if side[g["pairing"]] == "a" else 1 - g["first_deck_score"]  # noqa: E731
        GB = load(need(os.path.join(args.cov_dir, f"var_{v}_kog3.jsonl")), 500 * len(rows), ("kog3", "kog3"), "pi")
        vp = opt(f"{S}_var_{v}_{c}.jsonl", c)
        pa = opt(f"{S}_var_{v}_{c}_mixed_a.jsonl", c) if sa else None
        pb_ = opt(f"{S}_var_{v}_{c}_mixed_b.jsonl", c) if sb_ else None
        acc, fur_l = "accuracy: both-sides file not in yet", None
        if vp:
            GX = load(vp, 500 * len(rows), (c, c), "pi")
            same_deals(vp, GX, GB, f"var_{v}_kog3")
            avg = lambda rs: 100 * sum(own(g) for g in rs.values()) / len(rs)  # noqa: E731
            deck = rows[next(iter(rows))]["deck"]
            if deck == "charizardy":
                cs = [LIMB["pooled"].get(("charizardy_entei", o)) for o in {r["opponent"] for r in rows.values()}]
                Lf = sum(x for x in cs if x is not None) / sum(1 for x in cs if x is not None)
                src = "B2e pooled, charizardy_entei"
            else:
                vals = []
                for p, r in rows.items():
                    # the version stands in for its deck on its side; the other deck is 'opponent' (side a) or 'held_key' (side b)
                    da, db = (deck, r["opponent"]) if r["variant_side"] == "a" else (r["held_key"], deck)
                    w, l, t = v2dev[f"{min(da, db)}|{max(da, db)}"]
                    s = (w + 0.5 * t) / (w + l + t)
                    vals.append(100 * (s if min(da, db) == deck else 1 - s))
                Lf, src = sum(vals) / len(vals), "development half, the same opponents"
            x, y = avg(GB), avg(GX)
            fur_l = abs(y - Lf) - abs(x - Lf)
            acc = f"opponent average kog3 {x:5.1f} -> {c} {y:5.1f}; figure {Lf:5.1f} ({src}); further by {fur_l:+.1f} (reported)"
        mixed_ok = (pa or not sa) and (pb_ or not sb_)
        if mixed_ok:
            MX = {}
            if pa:
                r_ = load(pa, 500 * len(sa), (c, "kog3"), "pi")
                same_deals(pa, r_, {k: g for k, g in GB.items() if k[0] in sa}, f"var_{v}_kog3")
                MX.update(r_)
            if pb_:
                r_ = load(pb_, 500 * len(sb_), ("kog3", c), "pi")
                same_deals(pb_, r_, {k: g for k, g in GB.items() if k[0] in sb_}, f"var_{v}_kog3")
                MX.update(r_)
            m, h, n = pool([[100 * (own(MX[(p, i)]) - own(GB[(p, i)])) for i in range(500)] for p in sorted(rows)])
            harm = m + h < 0
            P(f"     {v:13} {acc}; own side (mixed) {fmt(m, h)} over {len(rows)} rows -> {'VETO (own side worse beyond paired noise)' if harm else 'no harm'}")
            if harm:
                lists_bad.append(f"{v} {fmt(m, h)}")
                if fur_l is not None and fur_l <= 2:
                    lists_soft.append(v)   # harm, but the opponent average is not more than 2 further (item 4's wording asks for both)
            elif fur_l is not None and fur_l > 2:
                lists_fur.append(v)        # more than 2 further, own side not worse: not a veto (counts only when own side is worse)
        else:
            P(f"     {v:13} {acc}; own-side mixed rows not in yet")
            lists_pending.append(v)
    _lc = (f"harm but not more than 2 further: {', '.join(lists_soft) or 'none'}; "
           f"more than 2 further but no harm: {', '.join(lists_fur) or 'none'}")
    P(f"   (N4) second lists: {_lc}")
    if lists_bad:
        COV[c]["lists"] = ("FAIL", "second-list veto: " + "; ".join(lists_bad) + f" ({_lc})")
    elif lists_pending:
        COV[c]["lists"] = ("PENDING", "mixed rows not in yet for " + ", ".join(lists_pending))
    else:
        COV[c]["lists"] = ("PASS", f"no second list's own side worse beyond noise ({_lc})")
    if c in CODES:
        # Item 4: "on the reserve route its (b) includes the held-out veto, and at 15% or more its ordinary rule includes rule v2's
        # held-out veto and the no-harm tests below" (the tests: Scizor's own side, the second lists' own side).
        gate(c, "cov_b2e", "(b, held-out part) no B2e held-out deck's own side hurt" if ROUTE[c] == "reserve"
             else "(rule v2's held-out veto) no B2e held-out deck's own side hurt", *COV[c]["b2e"])
        gate(c, "cov_scz", "coverage: Scizor's own side not hurt", *COV[c]["scizor"])
        gate(c, "cov_lst", "coverage: no second list's own side hurt", *COV[c]["lists"])

# ---------------------------------------------------------------------------------------------------------------
# 6. Reported beside, gating nothing.
# ---------------------------------------------------------------------------------------------------------------
P("\n6. REPORTED BESIDE (these gate nothing).")


def real_cells(deck):
    rows = []
    for cell in CELLS:
        if deck not in cell:
            continue
        a, b = cell
        flip = deck == b
        L, n, band = limit(cell)
        r = {"cell": cell, "L": 100 - L if flip else L, "n": n, "band": band}
        for name, src in (("kog3", BASE),) + tuple((c, BOTH[c]) for c in ("kt3", "kta3") if c in BOTH):
            s = 100 * sum(src[(a, b, i)]["first_deck_score"] for i in ICELL[cell]) / len(ICELL[cell])
            r[name] = 100 - s if flip else s
        rows.append(r)
    return rows


def show_real(deck, title):
    rows = real_cells(deck)
    P(f"   {title} (its own score; Limitless development half; miss = |sim - Limitless|):")
    names = [n for n in ("kog3", "kt3", "kta3") if n in rows[0]]
    for r in rows:
        opp = r["cell"][1] if r["cell"][0] == deck else r["cell"][0]
        P(f"     {deck} v {opp:17}" + " ".join(f"{n} {r[n]:5.1f}" for n in names) + f" | Limitless {r['L']:5.1f} +/- {r['band']:4.1f} (n {r['n']})"
          + " | miss " + " -> ".join(f"{abs(r[n] - r['L']):4.1f}" for n in names))
    avg = {n: sum(r[n] for r in rows) / len(rows) for n in names}
    La = sum(r["L"] for r in rows) / len(rows)
    P(f"     {'equal-weight average over ' + str(len(rows)) + ' cells':>34}: " + " ".join(f"{n} {avg[n]:5.1f}" for n in names) + f" | Limitless {La:5.1f} | miss "
      + " -> ".join(f"{abs(avg[n] - La):4.1f}" for n in names))


P("\n   6a. Suicune's real Limitless cells, before (kog3) and after (kt3, kta3), both sides played by the code:")
show_real("suicune", "Suicune's nine real cells")
P("\n   6b. Rayquaza's real Limitless cells (the scoreboard's Rayquaza list; they count in the 45 cells like any other), before and after:")
show_real("rayquaza", "Rayquaza's nine real cells")
P("\n   6c. Suicune's own side in the mixed rows (the code on Suicune, kog3 on the other deck, against kog3 on both):")
P("       (Reported beside (d), per Dustin: a finding to write down, not a gate that fired. The (d) gate is Rayquaza's rows only. "
  "On the reserve route the same rows still gate through clause (c), pooled over Suicune's cells where the footprint is not "
  "zero, when Suicune's own side is worse beyond noise; a (c) FAIL names the deck.)")
for c in CODES:
    if set(MIX.get(c, {})) != {"first", "second"}:
        P(f"     [{c}] mixed rows not all in yet")
        continue
    cells9 = [cell for cell in CELLS if "suicune" in cell]
    cells7 = [cell for cell in cells9 if cell in set(CELLS[:28])]  # the table's cells come first in the baseline
    m9, h9, n9, per = deck_report(c, "suicune", cells9)
    m7, h7, n7, _ = deck_report(c, "suicune", cells7)
    P(f"     [{c}] nine rows (7 table + 2 new): {fmt(m9, h9)} ({n9:,} deals); the table's seven: {fmt(m7, h7)} ({n7:,} deals)")
    for cell, (mm, hh) in per.items():
        opp = cell[1] if cell[0] == "suicune" else cell[0]
        P(f"        Suicune v {opp:17} {fmt(mm, hh)}")
P("\n   6d. The single-switch attribution codes against kog3 on the 45 cells (real error only; attribution, never adoption):")
if args.no_attribution:
    P("     skipped (--no-attribution)")
else:
    for c in ("ktb3", "ktc3"):
        if c not in BOTH:
            P(f"     {c}: not in yet ({S}_{c}_table.jsonl / _new17.jsonl)")
            continue
        r, page, tag, _ = run_score45(c, False)
        A = r["all"]
        P(f"     {c}: real error kog3 {A['real']['kog3']:.1f} -> {c} {A['real'][c]:.1f}; tau margin (kog3 minus {c}) {A['tau'][0]:+.2f}, "
          f"90% interval {A['tau'][1]:+.2f} to {A['tau'][2]:+.2f} (page {os.path.basename(page)}; footprint "
          f"{100 * FPL[c][0] / FPL[c][1]:.2f}%)")
P("\n   6e. Read separately (pointers, not read here): the Dustin-deck A/B is read_kt_ab.py's table (outputs "
  f"{S}_ab_d<deck>_<arm>.jsonl; kt3 and kta3 v kog3 on decks 07, 05, 11, 01, 03; the Skarmory deck is the motivation, not a gate);")
P(f"       the readout counters are run_kt_counters.sh's; the Rayquaza traces are {S}_trace_rayquaza_kta3_pergame.jsonl and "
  f"{S}_trace_rayquaza_kog3_pergame.jsonl (reported only).")
for nm in (f"{S}_trace_rayquaza_kta3_pergame.jsonl", f"{S}_trace_rayquaza_kog3_pergame.jsonl"):
    P(f"       {nm}: {'in' if os.path.exists(path(nm)) else 'not in yet'}")
# 6f. Amendment 2 item 9 (F7): "the 'before' for switch 2's expected Hydreigon deck-gap veto is kog3's on the 45 cells, 51.2 against
# 43.9 (+7.3)". The veto lines above show only a veto that FIRES (a gap that grows by more than 2); this row shows where the gap
# went either way. It is score45's own 'Deck averages' row from the 45-cell block, reported only.
P("\n   6f. Hydreigon's deck gap (item 9, F7; reported only). Registered 'before': kog3 51.2 against Limitless 43.9, a gap of +7.3. "
  "score45's 'Deck averages' row over Hydreigon's cells (45-cell block; change in miss, + = further from Limitless):")
for c in CODES:
    hy = R45[c]["all"]["deck_avg"].get("hydreigon")
    if hy is None:
        P(f"     [{c}] no Hydreigon row in score45's deck averages")
        continue
    cur, new, lim_, chg = hy
    P(f"     [{c}] kog3 {cur:.1f} -> {c} {new:.1f}; Limitless {lim_:.1f}; gap {abs(cur - lim_):.1f} -> {abs(new - lim_):.1f}; change in miss {chg:+.1f}"
      + ("  (the deck-gap veto threshold is +2.0)" if chg > 2 else "")
      + ("" if abs(cur - 51.2) < 0.06 and abs(lim_ - 43.9) < 0.06 else
         "  NOTE: this run's kog3 / Limitless differ from the registered 51.2 / 43.9: read why before using the 'before'"))

# ---------------------------------------------------------------------------------------------------------------
# 7. Verdicts.
# ---------------------------------------------------------------------------------------------------------------
P("\n7. VERDICT (plain language; the registration's own outcomes decide, read from the numbers above).")
RES_OF = {}
for c in CODES:
    g = GATES[c]
    fails = [x for x in g if x[2] == "FAIL"]
    pend = [x for x in g if x[2] == "PENDING"]
    missing = NOT_IN[c]
    if fails:
        res = "FAIL"
    elif pend or missing:
        res = "PENDING"
    else:
        res = "PASS"
    RES_OF[c] = res
    P(f"\n   {c} ({'all three switches' if c == 'kt3' else 'switch 1 alone, the Tool/turn-effect cut'}); footprint "
      f"{FPL[c][0]:,} of {FPL[c][1]:,} = {100 * FPL[c][0] / FPL[c][1]:.4f}% -> "
      f"{'RESERVE ROUTE (a)-(e)' if ROUTE[c] == 'reserve' else 'ORDINARY ADOPTION RULE v2'}")
    for gid, label, st, dt in g:
        P(f"     {st:8} {label}: {dt}")
    if ROUTE[c] == "ordinary":
        dmark = "reported only" if c == "kta3" else "not part of the ordinary rule"
        dr = DROWS.get(c)
        P(f"     reported  Rayquaza clause (d) ({dmark}): " + (f"{fmt(*dr)}" if dr else "not in yet"))
        tt = R45[c]["all"]["tau"]
        P(f"     reported  tau margin (kog3 minus {c}): {tt[0]:+.2f}, 90% interval {tt[1]:+.2f} to {tt[2]:+.2f}")
    if ROUTE[c] == "reserve":
        P("     (e)      adoption for the screen and the table together: not a test, decided by the pair's outcome below")
    if missing:
        P(f"     not in yet ({len(missing)}): " + ", ".join(missing))
    if res == "PASS":
        P(f"     => {c} PASSES its route (adopt, together with the other code: see the outcome below).")
    elif res == "FAIL":
        why = "; ".join(f"{x[1]} ({x[3]})" for x in fails)
        n_missing = len(NOT_IN["kt3"]) + len(NOT_IN["kta3"])
        tail = (f" That 'not adopted' is PROVISIONAL until kt3 and kta3 are read on every coverage row ({n_missing} input(s) not in yet, both codes together)."
                if n_missing else
                " Every input of both codes is in, so this 'not adopted' stands (a new reading under the rules in force could reopen it).")
        fids = {x[0] for x in fails}
        if ROUTE[c] == "reserve" and fids and fids <= {"cov_scz", "cov_lst"}:
            tail += (f" WHICH READING DECIDED (N12): on the reserve route this fails ONLY through the coverage no-harm test(s) "
                     f"({', '.join(sorted(fids))}), which item 4 words for the ordinary rule; the reserve route's own (b) names only the "
                     f"held-out veto. It is gated here on item 4's 'a veto there blocks the takeover', RUN5 and Dustin's 'no deck hurt'. "
                     f"Under the literal reading of item 4's sentence this code would not fail on it.")
        if fids and fids <= {"cov_b2e", "cov_scz", "cov_lst"}:
            _nt = COV[c].get("n_b2e", 0) + 1 + 4
            tail += (f" (N12: a coverage veto is the only failure. It is one of {_nt} own-side coverage tests, each with a one-sided 2.5% "
                     f"chance of vetoing a neutral code; the veto's size is in its line above.)")
        P(f"     => {c} FAILS: DO NOT ADOPT. Failed: {why}.{tail}")
    else:
        why = "; ".join([f"{x[1]}: {x[3]}" for x in pend] + [f"{len(missing)} file(s) not in yet"] * bool(missing))
        P(f"     => {c} is PROVISIONAL: nothing has failed yet, but it cannot pass until: {why}.")

# Clause (e): "(e) adoption for the screen and the table together". The registration's "Outcomes fixed now":
#   "kt3 passes and kta3 passes: kt adopted (screen and table).
#    kt3 passes and kta3 fails or is closed: nothing adopted as built. Switches 2 and 3 are re-registered as a new code with a new
#    table, unless Dustin overrides for kt as a whole.
#    kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh."
# ("kta3 passes" at 15% or more means passing the ordinary rule, amendment 2 item 2.)
k3, ka = RES_OF["kt3"], RES_OF["kta3"]
P("\n   THE OUTCOME THE REGISTRATION FIXES FOR THE PAIR (FOOTPRINT AND ROUTES, 'Outcomes fixed now'):")
if k3 == "PASS" and ka == "PASS":
    out = "kt3 passes and kta3 passes -> kt is ADOPTED (screen and table together, clause (e)), as the working pilot 'unconfirmed'."
elif k3 == "FAIL":
    out = ("kt3 fails -> DO NOT ADOPT: nothing is adopted. The diagnostic codes are read for attribution only, and the next "
           "candidate is registered afresh." + (" (Provisional until every coverage row is in.)" if NOT_IN["kt3"] or NOT_IN["kta3"] else ""))
elif k3 == "PASS" and ka == "FAIL":
    out = ("kt3 passes and kta3 fails -> DO NOT ADOPT as built. Switches 2 and 3 are re-registered as a new code with a new "
           "table, unless Dustin overrides for kt as a whole." + (" (Provisional until every coverage row is in.)" if NOT_IN["kt3"] or NOT_IN["kta3"] else ""))
else:
    _w = {"PENDING": "provisional", "PASS": "passes", "FAIL": "fails"}
    out = f"PROVISIONAL: kt3 {_w[k3]}, kta3 {_w[ka]}; the outcome needs both read in full (files not in yet are named above)."
P("   " + out)
P("\n   WHAT STAYS PROVISIONAL, whatever the numbers say:")
P("     - Confirmation at the post-freeze pull (RUN5 'When post-freeze data is read'; item 6): an adopted kt is the working pilot 'unconfirmed'.")
P("         kt3 by the reserve route: the no-harm re-check (tau margin 90% lower bound -1.0 or above, no veto), its own real cells reported;")
P("         kt3 by the ordinary rule: on the post-freeze events alone the tau margin at least half its development margin, own 90% interval above zero;")
P("         kta3 by the reserve route: the same no-harm re-check, Suicune's and Rayquaza's real cells reported.")
P("     - kog's own row (and kpg's and koa's that kog inherits) has not passed its confirmation: kt stays 'unconfirmed' until those rows pass (item 6).")
P("     - A 'not adopted' stands only once kt3 and kta3 are read on all the coverage rows (item 4): B2e's 96 pairings, the Scizor row, the four second lists.")
P("     - The Dustin-deck A/B, the readout counters and the Rayquaza traces are motivation and mechanism, read separately, and gate nothing here.")
P("     - This reading is the laptop's first reader; the registration's second reader is still owed.")
