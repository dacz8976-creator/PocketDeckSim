#!/usr/bin/env python3
"""The B2e reading: section 5 of ../b2e_card_check_2026-09-26/README.md. Descriptive only: no ranking, adoption,
tuning or hold decision is taken from it.

    python3 read_b2e.py [--dir <folder>]      (default folder: this script's; --dir is for dry runs on test files)

Refuses to read anything unless
  1. identity_check.txt ends in the IDENTITY PASS line for the binary on identity.txt's first line,
  2. rows_check.txt names that same binary on its first line and carries a ROWS PASS line, and
  3. the rows check (b2e_checks.check_rows), re-run here on b2e_k3.jsonl and b2e_kp3.jsonl, passes.
A pairing with a RULE finding under a pilot is withheld under that pilot (README section 4: RULE stops the
reading of that pairing until explained), and so is every panel score that needs it.

Definitions (README section 5):
  cell score    = mean of first_deck_score over the pairing's 500 deals, x 100 (held deck's wins + half its ties);
                  ties = winner_seat -1, counted per cell.
  sim band      = 1.96 sqrt(p(1-p)/500), in points (4.4 at 50%), the same binomial formula as the Limitless cells.
  panel score   = equal-weight mean of the eight cell scores; its +/- is 1.96 sqrt(sum p(1-p)/n) / 8
                  (panel_bands.py's formula).
  gap           = panel score - the Limitless equal-weight average: pooled (the reference) and development (beside
                  it, over the opponents with development matches: seven for Whimsicott, no blaziken).
  per-cell miss = sim cell - Limitless pooled cell; "beyond" when |miss| > sqrt(band_L^2 + band_S^2). A Limitless
                  cell at 0% or 100% has band 0 and is read as "no information" (README section 3), not tested.
                  A Limitless band wider than 15 points is marked "wide" (rule v2 never counts a veto there).
  list difference = archetype list's panel score - Dustin's file's, per pilot (independent deals: +/- adds the
                  two panel variances).
  kp3 - k3      = paired by deal (same seeds): mean over the eight cells of the per-deal differences, +/- from
                  their spread.
  A2 bar        = kp3 on both sides, archetype lists (block A): each panel score inside its pooled equal-weight
                  interval of README section 3.7 (panel_intervals.csv). Stated, not applied: the hold stays as
                  Dustin set it on Sept 25.
  veto baseline = |kp3 panel - L| per archetype, L the pooled equal-weight average (development beside it);
                  k3's is kept as the reproduction reference.
The Limitless cells are recomputed from W-L-T-n in limitless_cells.csv and checked against its rounded score and
band columns; the equal-weight averages are checked against panel_intervals.csv, whose lo/hi are the intervals.
Writes b2e_tables.md and b2e_summary.json in the folder and prints the tables. b2e_tables.md ends with the rows
check, the scan logs' own findings sections (so each CHECK is listed with its example games, README section 4),
deck_check.txt and timing.txt.
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.normpath(os.path.join(HERE, "..", "b2e_card_check_2026-09-26"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True  # no __pycache__ in the results folder
import b2e_checks  # noqa: E402

PILOTS = ("k3", "kp3")
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
# (TSV key of the archetype list; Dustin's key is "dustin_" + it), Limitless archetype key, Limitless deck name,
# "untrusted-prone" per README section 6 (archetype list, Dustin's file).
DECKS = [
    ("manectric", "manectric_heliolisk", "Mega Manectric ex Heliolisk", ("no", "no")),
    ("raticate", "raticate_ninetales", "Team Rocket's Raticate ex Alolan Ninetales ex", ("yes", "yes")),
    ("hoopa_absol", "hoopa_absol", "Hoopa ex Mega Absol ex", ("yes", "yes")),
    ("garchomp", "garchomp", "Garchomp", ("yes", "yes")),
    ("whimsicott", "whimsicott_ariados", "Whimsicott ex Ariados", ("yes", "yes")),
    ("charizardy_entei", "charizardy_entei", "Mega Charizard Y ex Entei ex", ("no", "no")),
]
KNOWN_PANEL_MISS = {
    "sceptile": "the 28-cell table overrates Sceptile by about 12",
    "vespiquen": "underrates Vespiquen by about 11",
    "altaria": "underrates Altaria by about 4 under kp3",
}
BASE, GAMES, WIDE = 21_106_000_000, 500, 15.0


def refuse(msg):
    raise SystemExit(f"read_b2e.py refuses: {msg}")


def lines(path):
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f if l.strip()]


def gate(folder):
    for name in ("identity.txt", "identity_check.txt", "rows_check.txt", "b2e_k3.jsonl", "b2e_kp3.jsonl"):
        if not os.path.exists(os.path.join(folder, name)):
            refuse(f"{name} is missing")
    sha = lines(os.path.join(folder, "identity.txt"))[0].split()[0]
    last = lines(os.path.join(folder, "identity_check.txt"))[-1]
    if not last.startswith(f"IDENTITY PASS {sha}:"):
        refuse(f"identity_check.txt does not end in the IDENTITY PASS line for {sha} (last line: {last!r})")
    rows = lines(os.path.join(folder, "rows_check.txt"))
    if rows[0] != f"scan binary {sha}":
        refuse(f"rows_check.txt's first line is {rows[0]!r}, not the identity-checked binary {sha}")
    passed = [l for l in rows if l.startswith("ROWS PASS")]
    if not passed:
        refuse("rows_check.txt has no ROWS PASS line")
    return sha, last, passed[-1]


def findings_section(path):
    """The log's 'Findings (occurrences / games affected):' section to the end, examples included."""
    text = lines(path)
    for n, line in enumerate(text):
        if line.startswith("Findings (occurrences / games affected):"):
            return text[n:]
    refuse(f"{path} has no findings section")


def pct(p, n):
    return 100.0 * p, 196.0 * math.sqrt(p * (1 - p) / n)


def limitless():
    cells = {}
    with open(os.path.join(SPEC, "limitless_cells.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["dataset"] not in ("pooled", "development") or r["opponent"] not in PANEL:
                continue
            w, l, t, n = (int(r[k]) for k in ("W", "L", "T", "n"))
            key = (r["dataset"], r["archetype"], r["opponent"])
            if n == 0:
                cells[key] = None
                continue
            p = (w + 0.5 * t) / n
            score, band = pct(p, n)
            if abs(score - float(r["score_pct"])) > 0.051 or abs(band - float(r["band95_pts"])) > 0.051:
                refuse(f"limitless_cells.csv {key}: recomputed {score:.2f} +/- {band:.2f}, file says "
                       f"{r['score_pct']} +/- {r['band95_pts']}")
            cells[key] = {"W": w, "L": l, "T": t, "n": n, "pct": score, "band": band,
                          "one_sided": p in (0.0, 1.0), "wide": band > WIDE}
    intervals = {}
    with open(os.path.join(SPEC, "panel_intervals.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            intervals[(r["dataset"], r["archetype"])] = {k: float(r[k]) for k in (
                "equal_weight_avg_pct", "equal_weight_band95_pts", "equal_weight_lo_pct", "equal_weight_hi_pct")}
    for _, arch, _, _ in DECKS:
        for o in PANEL:
            if cells.get(("pooled", arch, o)) is None:
                refuse(f"limitless_cells.csv has no pooled matches for {arch} v {o}")
    averages = {}
    for dataset in ("pooled", "development"):
        for _, arch, _, _ in DECKS:
            have = [o for o in PANEL if cells[(dataset, arch, o)] is not None]
            avg = sum(cells[(dataset, arch, o)]["pct"] for o in have) / len(have)
            iv = intervals[(dataset, arch)]
            if abs(avg - iv["equal_weight_avg_pct"]) > 0.051:
                refuse(f"panel_intervals.csv {dataset} {arch}: recomputed {avg:.2f}, file {iv['equal_weight_avg_pct']}")
            averages[(dataset, arch)] = {"avg": avg, "opponents": have, "band": iv["equal_weight_band95_pts"],
                                         "lo": iv["equal_weight_lo_pct"], "hi": iv["equal_weight_hi_pct"]}
    return cells, averages


def check_layout(rows):
    """The TSV must be README section 4's order: p = 8d + o (block A), 48 + 8d + o (block B)."""
    if sorted(rows) != list(range(96)):
        refuse("the TSV does not list pairings 0 to 95")
    for p, r in rows.items():
        d, o = (p % 48) // 8, p % 8
        key = DECKS[d][0] if p < 48 else "dustin_" + DECKS[d][0]
        if r["held_key"] != key or r["opponent"] != PANEL[o]:
            refuse(f"TSV pairing {p} is {r['held_key']} v {r['opponent']}, expected {key} v {PANEL[o]}")


def main():
    folder = HERE
    if "--dir" in sys.argv:
        folder = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1])
    sha, id_line, rows_line = gate(folder)
    tsv = os.path.join(SPEC, "b2e_pairings.tsv")
    rows = b2e_checks.load_tsv(tsv)
    check_layout(rows)
    files = {pilot: os.path.join(folder, f"b2e_{pilot}.jsonl") for pilot in PILOTS}
    check_log = []
    ok, findings = b2e_checks.check_rows(tsv, BASE, GAMES, files, out=check_log.append)
    if not ok:
        refuse("the rows check fails on re-run: " + check_log[-1])
    withheld = {pilot: {p for p, c in findings[pilot].items() if any(k.startswith("RULE") for k in c)}
                for pilot in PILOTS}

    # Per-deal scores and per-cell statistics.
    score = {pilot: {p: [None] * GAMES for p in rows} for pilot in PILOTS}
    for pilot in PILOTS:
        for g in b2e_checks.load_games(files[pilot]):
            score[pilot][g["pairing"]][g["i"]] = g["first_deck_score"]
    sim = {pilot: {} for pilot in PILOTS}
    for pilot in PILOTS:
        for p in rows:
            s = score[pilot][p]
            n = len(s)
            m = sum(s) / n
            value, band = pct(m, n)
            sim[pilot][p] = {"n": n, "W": s.count(1.0), "T": s.count(0.5), "L": s.count(0.0), "pct": value,
                             "band": band, "var": m * (1 - m) / n, "withheld": p in withheld[pilot]}

    cells, averages = limitless()

    def panel(pilot, ps):
        if any(sim[pilot][p]["withheld"] for p in ps):
            return None
        cs = [sim[pilot][p] for p in ps]
        return {"pct": sum(c["pct"] for c in cs) / len(cs),
                "band": 196.0 * math.sqrt(sum(c["var"] for c in cs)) / len(cs), "cells": len(cs)}

    def paired(ps):
        if any(sim[pl][p]["withheld"] for pl in PILOTS for p in ps):
            return None
        means, var = [], 0.0
        for p in ps:
            diffs = [b - a for a, b in zip(score["k3"][p], score["kp3"][p])]
            m = sum(diffs) / len(diffs)
            means.append(m)
            var += sum((x - m) ** 2 for x in diffs) / len(diffs) / len(diffs)
        return {"pct": 100.0 * sum(means) / len(means), "band": 196.0 * math.sqrt(var) / len(means)}

    summary = {"binary_sha256": sha, "identity": id_line, "rows_check": rows_line, "seed_base": BASE,
               "games_per_pairing": GAMES, "withheld_pairings": {pl: sorted(withheld[pl]) for pl in PILOTS},
               "decks": {}}
    md = []
    out = md.append
    out("# B2e reading tables (generated by read_b2e.py; descriptive only)")
    out("")
    out(f"Specification: `../b2e_card_check_2026-09-26/README.md` sections 4 and 5. Scan binary sha256 `{sha}`.")
    out(f"- {id_line}")
    out(f"- {rows_line}")
    for pilot in PILOTS:
        out(f"- {pilot}: RULE findings in pairings {sorted(withheld[pilot]) or 'none'}"
            + (" (withheld below until explained)" if withheld[pilot] else ""))
    out("")

    def fmt(x):
        return "n/a" if x is None else f"{x:.1f}"

    def sgn(x):
        return "n/a" if x is None else f"{x:+.1f}"

    def pv(x):
        """The value of a {"pct", "band"} result, or None."""
        return None if x is None else x["pct"]

    def pm(x, signed=False):
        """A {"pct", "band"} result as 'value +/- band'."""
        if x is None:
            return "n/a"
        return (f"{x['pct']:+.1f}" if signed else f"{x['pct']:.1f}") + f" +/- {x['band']:.1f}"

    def cell_txt(pilot, p):
        c = sim[pilot][p]
        return "RULE (withheld)" if c["withheld"] else f"{c['pct']:.1f} ({c['T']} ties)"

    # Per-deck numbers: panel scores, gaps, list difference, beyond-band cells, A2, veto baseline, kp3 - k3.
    for d,(key, arch, name, prone) in enumerate(DECKS):
        pa = [8 * d + o for o in range(8)]
        pb = [48 + 8 * d + o for o in range(8)]
        lp, ld = averages[("pooled", arch)], averages[("development", arch)]
        dev_idx = [PANEL.index(o) for o in ld["opponents"]]
        entry = {"name": name, "limitless_pooled": lp, "limitless_development": ld, "pilots": {}}
        for pilot in PILOTS:
            a, b = panel(pilot, pa), panel(pilot, pb)
            a_dev = panel(pilot, [pa[o] for o in dev_idx])
            gap = None if a is None else a["pct"] - lp["avg"]
            gap_dev = None if a_dev is None else a_dev["pct"] - ld["avg"]
            listdiff = None
            if a is not None and b is not None:
                va = sum(sim[pilot][p]["var"] for p in pa)
                vb = sum(sim[pilot][p]["var"] for p in pb)
                listdiff = {"pct": a["pct"] - b["pct"], "band": 196.0 * math.sqrt(va + vb) / 8}
            beyond, noinfo = [], []
            for o, opp in enumerate(PANEL):
                c, s = cells[("pooled", arch, opp)], sim[pilot][pa[o]]
                if s["withheld"]:
                    continue
                if c["one_sided"]:
                    noinfo.append(opp)
                elif abs(s["pct"] - c["pct"]) > math.hypot(c["band"], s["band"]):
                    beyond.append(opp)
            entry["pilots"][pilot] = {
                "archetype_list_panel": a, "dustin_file_panel": b, "archetype_list_panel_dev_opponents": a_dev,
                "gap_pooled": gap, "gap_development": gap_dev, "list_difference": listdiff,
                "abs_gap_pooled": None if gap is None else abs(gap),
                "abs_gap_development": None if gap_dev is None else abs(gap_dev),
                "cells_beyond_band": beyond, "cells_no_information": noinfo,
                "a2_inside_pooled_interval": None if a is None else lp["lo"] <= a["pct"] <= lp["hi"],
            }
        entry["kp3_minus_k3"] = {"archetype_list": paired(pa), "dustin_file": paired(pb)}
        entry["untrusted_prone"] = {"archetype_list": prone[0], "dustin_file": prone[1]}
        entry["cells"] = {opp: {"limitless_pooled": cells[("pooled", arch, opp)],
                                "limitless_development": cells[("development", arch, opp)],
                                "archetype_list": {pl: sim[pl][pa[o]] for pl in PILOTS},
                                "dustin_file": {pl: sim[pl][pb[o]] for pl in PILOTS}}
                          for o, opp in enumerate(PANEL)}
        summary["decks"][key] = entry

    out("## Panel scores (equal-weight over the eight panel decks)")
    out("")
    out("| Deck | List | k3 % | kp3 % | kp3 - k3 (paired by deal) | Limitless pooled % (interval) | Gap k3 "
        "| Gap kp3 | Limitless dev % | Gap dev k3 | Gap dev kp3 | Untrusted-prone |")
    out("|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|")
    for key, arch, name, _ in DECKS:
        e = summary["decks"][key]
        lp, ld = e["limitless_pooled"], e["limitless_development"]
        k, q = e["pilots"]["k3"], e["pilots"]["kp3"]
        dev_note = "" if len(ld["opponents"]) == 8 else f" ({len(ld['opponents'])} opp.)"
        out(f"| {name} | archetype list | {pm(k['archetype_list_panel'])} | {pm(q['archetype_list_panel'])} "
            f"| {pm(e['kp3_minus_k3']['archetype_list'], signed=True)} "
            f"| {lp['avg']:.1f} ({lp['lo']:.1f} to {lp['hi']:.1f}) | {sgn(k['gap_pooled'])} | {sgn(q['gap_pooled'])} "
            f"| {ld['avg']:.1f}{dev_note} | {sgn(k['gap_development'])} | {sgn(q['gap_development'])} "
            f"| {e['untrusted_prone']['archetype_list']} |")
        out(f"| | Dustin's file | {pm(k['dustin_file_panel'])} | {pm(q['dustin_file_panel'])} "
            f"| {pm(e['kp3_minus_k3']['dustin_file'], signed=True)} "
            f"| (no Limitless cells of its own) | | | | | | {e['untrusted_prone']['dustin_file']} |")
    out("")
    out("+/- is 95%: binomial over the simulator's 8 x 500 games for a panel score; from the per-deal differences for "
        "kp3 - k3 (same deals). The Limitless intervals are README section 3.7's. Gap = panel score minus the "
        "Limitless equal-weight average; the development gap uses the opponents with development matches.")
    out("")

    out("## The list difference (archetype list minus Dustin's file, per pilot)")
    out("")
    out("| Deck | k3 | kp3 |")
    out("|---|---:|---:|")
    for key, _, name, _ in DECKS:
        cols = []
        for pilot in PILOTS:
            ld_ = summary["decks"][key]["pilots"][pilot]["list_difference"]
            cols.append("n/a" if ld_ is None else f"{ld_['pct']:+.1f} +/- {ld_['band']:.1f}")
        out(f"| {name} | {cols[0]} | {cols[1]} |")
    out("")
    out("Dustin's files have no Limitless cells of their own; this only says how much the list, rather than the "
        "pilot, moves the deck.")
    out("")

    out("## A2's bar (kp3 on both sides, archetype lists, pooled equal-weight intervals of README 3.7)")
    out("")
    inside = []
    for key, arch, name, _ in DECKS:
        e = summary["decks"][key]
        a = e["pilots"]["kp3"]["archetype_list_panel"]
        lp = e["limitless_pooled"]
        verdict = "not read (RULE)" if a is None else ("inside" if e["pilots"]["kp3"]["a2_inside_pooled_interval"] else "outside")
        inside.append(verdict)
        k3a = e["pilots"]["k3"]["archetype_list_panel"]
        out(f"- {name}: kp3 {fmt(pv(a))} against {lp['lo']:.1f} to {lp['hi']:.1f}: **{verdict}** "
            f"(k3, context: {fmt(pv(k3a))})")
    n_in = inside.count("inside")
    bar = f"A2 bar line: {n_in} of 6 archetype lists inside their pooled interval under kp3; " + (
        "each lands inside." if n_in == 6 else "not every one lands inside.")
    out("")
    out(f"**{bar}** This states the bar; it does not lift or apply the screen's hold, which stays as Dustin set it.")
    summary["a2_bar"] = {"inside": n_in, "of": 6, "verdicts": dict(zip([d[0] for d in DECKS], inside)), "line": bar}
    out("")

    out("## Baseline for RUN5's held-out veto (reference row kp3; k3 is the reproduction reference)")
    out("")
    out("| Archetype | L pooled % | abs(kp3 - L) | abs(k3 - L) | L dev % | abs(kp3 - L dev) | abs(k3 - L dev) |")
    out("|---|---:|---:|---:|---:|---:|---:|")
    for key, _, name, _ in DECKS:
        e = summary["decks"][key]
        q, k = e["pilots"]["kp3"], e["pilots"]["k3"]
        out(f"| {name} | {e['limitless_pooled']['avg']:.1f} | {fmt(q['abs_gap_pooled'])} | {fmt(k['abs_gap_pooled'])} "
            f"| {e['limitless_development']['avg']:.1f} | {fmt(q['abs_gap_development'])} | {fmt(k['abs_gap_development'])} |")
    out("")
    out("A later candidate C vetoes on a deck if abs(C - L) - abs(kp3 - L) > 2 (pooled L), under rule v2 as "
        "pre-registered. Whimsicott's L rests on 60 matches with three one-sided cells.")
    out("")

    out("## Per deck, per cell")
    for d, (key, arch, name, _) in enumerate(DECKS):
        e = summary["decks"][key]
        out("")
        out(f"### {name}: archetype list (pairings {8 * d} to {8 * d + 7})")
        out("")
        out("| Opponent | Limitless pooled % (+/-) | Limitless dev % (+/-) | k3 % | kp3 % | Miss k3 | Miss kp3 "
            "| Beyond the band? | Note |")
        out("|---|---|---|---:|---:|---:|---:|---|---|")
        for o, opp in enumerate(PANEL):
            p = 8 * d + o
            c, cd = cells[("pooled", arch, opp)], cells[("development", arch, opp)]
            misses, beyond = [], []
            for pilot in PILOTS:
                s = sim[pilot][p]
                if s["withheld"]:
                    misses.append("n/a")
                    beyond.append(f"{pilot} withheld")
                    continue
                miss = s["pct"] - c["pct"]
                misses.append(f"{miss:+.1f}")
                if c["one_sided"]:
                    beyond.append(f"{pilot} no information")
                else:
                    beyond.append(f"{pilot} {'yes' if abs(miss) > math.hypot(c['band'], s['band']) else 'no'}")
            notes = []
            if c["one_sided"]:
                notes.append(f"Limitless cell one-sided ({c['W']}-{c['L']}-{c['T']})")
            if c["wide"]:
                notes.append("Limitless band wide (> 15)")
            if opp in KNOWN_PANEL_MISS:
                notes.append("panel's known miss: " + KNOWN_PANEL_MISS[opp])
            dev = "no games" if cd is None else f"{cd['pct']:.1f} ({cd['band']:.1f})"
            out(f"| {opp} | {c['pct']:.1f} ({c['band']:.1f}), n {c['n']} | {dev} | {cell_txt('k3', p)} "
                f"| {cell_txt('kp3', p)} | {misses[0]} | {misses[1]} | {', '.join(beyond)} | {'; '.join(notes)} |")
        k, q = e["pilots"]["k3"], e["pilots"]["kp3"]
        out(f"| **Panel score** | **{e['limitless_pooled']['avg']:.1f}** (+/- {e['limitless_pooled']['band']:.1f}) "
            f"| **{e['limitless_development']['avg']:.1f}** | **{fmt(pv(k['archetype_list_panel']))}** "
            f"| **{fmt(pv(q['archetype_list_panel']))}** | {sgn(k['gap_pooled'])} "
            f"| {sgn(q['gap_pooled'])} | beyond: k3 {len(k['cells_beyond_band'])}, kp3 {len(q['cells_beyond_band'])} "
            f"of the cells with information | |")
        out("")
        out(f"### {name}: Dustin's file (pairings {48 + 8 * d} to {48 + 8 * d + 7})")
        out("")
        out("| Opponent | k3 % | kp3 % | Archetype list k3 % | Archetype list kp3 % | List difference k3 | List difference kp3 |")
        out("|---|---:|---:|---:|---:|---:|---:|")
        for o, opp in enumerate(PANEL):
            pa_, pb_ = 8 * d + o, 48 + 8 * d + o
            diffs = []
            for pilot in PILOTS:
                if sim[pilot][pa_]["withheld"] or sim[pilot][pb_]["withheld"]:
                    diffs.append("n/a")
                else:
                    diffs.append(f"{sim[pilot][pa_]['pct'] - sim[pilot][pb_]['pct']:+.1f}")
            out(f"| {opp} | {cell_txt('k3', pb_)} | {cell_txt('kp3', pb_)} | {cell_txt('k3', pa_)} "
                f"| {cell_txt('kp3', pa_)} | {diffs[0]} | {diffs[1]} |")
        out(f"| **Panel score** | **{fmt(pv(k['dustin_file_panel']))}** | **{fmt(pv(q['dustin_file_panel']))}** "
            f"| {fmt(pv(k['archetype_list_panel']))} | {fmt(pv(q['archetype_list_panel']))} "
            f"| {pm(k['list_difference'], signed=True)} | {pm(q['list_difference'], signed=True)} |")
    out("")
    out("## Rows check and legality findings (b2e_checks.py, re-run by this script)")
    out("")
    out("```")
    md.extend(check_log)
    out("```")
    out("")
    out("## The scan's own findings sections, with its examples (README section 4: CHECK is listed with its "
        "example and the card that may allow it; the card is for whoever writes READING.md)")
    for pilot in PILOTS:
        out("")
        out(f"### {pilot} (`b2e_{pilot}.txt`)")
        out("")
        out("```")
        md.extend(findings_section(os.path.join(folder, f"b2e_{pilot}.txt")))
        out("```")
    for name in ("deck_check.txt", "timing.txt"):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            out("")
            out(f"## {name}")
            out("")
            out("```")
            md.extend(lines(path))
            out("```")

    text = "\n".join(md) + "\n"
    with open(os.path.join(folder, "b2e_tables.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(os.path.join(folder, "b2e_summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
        f.write("\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
