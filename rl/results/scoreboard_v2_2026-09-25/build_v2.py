#!/usr/bin/env python3
"""Scoreboard v2: the 28 Limitless cells rebuilt from the pairings of the development half only (B6's split; the
frozen holdout half is not read). Run from anywhere:
    python build_v2.py
Writes limitless_v2_dev.json (the cells, in the shape score.py's --limitless takes), limitless_v2_dev_events.json
(the same cells split by tournament event, for score.py's --limitless-events: matches in one event share players,
lists and a field, so resampling events gives the Limitless side's clustered uncertainty) and cells_v2.txt (every
cell against the Sept 23 table).

Source: ../limitless_skill_model_2026-09-25/development_matches.csv (63 development events, split fixed in its
split.json before any outcome was read). A match is counted exactly as that folder's analyze.py counts a cell
(lines 75-76): both players' exact deck IDs map to two different panel archetypes, and the pairing is decisive or a
tie (byes, automatic losses, double losses and unresolved entries are out). One pairing entry = one match, as in the
Sept 23 table (a BO3 series counts once). Score = (W + T/2) / n for the alphabetically first deck.

The comparison with the Sept 23 table is descriptive. The two samples overlap (the development events are part of
what the Sept 23 pull saw), so 'outside noise' uses the Sept 23 cell's own binomial band at the v2 cell's n,
p23 +/- 1.96 sqrt(p23 (1 - p23) / n_v2), the same kind of tolerance as the B6 integrity check. It flags cells to look
at; it proves nothing about either table.
"""
import csv
import json
import math
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "limitless_skill_model_2026-09-25", "development_matches.csv")
sys.path.insert(0, os.path.join(HERE, "..", "deep_search_table"))
import deep_table as D  # noqa: E402

PANEL = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]


def main():
    cells = {k: [0, 0, 0] for k in combinations(PANEL, 2)}
    per_event = {}
    events, rows_used, splits = set(), 0, set()
    with open(SRC, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            splits.add(r["split"])
            if r["split"] != "development":
                continue
            a, b = r["archetype1"], r["archetype2"]
            if a not in PANEL or b not in PANEL or a == b or r["result_status"] not in ("tie", "decisive"):
                continue
            key = tuple(sorted((a, b)))
            idx = 2 if r["result_status"] == "tie" else (0 if (r["winner"] == r["player1"]) == (a == key[0]) else 1)
            cells[key][idx] += 1
            per_event.setdefault(r["event_id"], {}).setdefault(key, [0, 0, 0])[idx] += 1
            events.add(r["event_id"])
            rows_used += 1
    if splits != {"development"}:
        raise SystemExit(f"development_matches.csv holds splits {splits}; expected development only")
    out = {"source": "rl/results/limitless_skill_model_2026-09-25/development_matches.csv",
           "rule": "analyze.py lines 75-76: panel v panel, different archetypes, decisive or tie; one pairing = one match",
           "events_with_panel_matches": len(events), "matches": rows_used,
           "cells": {f"{a}|{b}": v for (a, b), v in cells.items()}}
    with open(os.path.join(HERE, "limitless_v2_dev.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    ev = {"source": out["source"], "rule": out["rule"], "note": "per event; summed over events these are "
          "limitless_v2_dev.json's cells", "events": [{"event_id": e, "cells": {f"{a}|{b}": v for (a, b), v in
          sorted(c.items())}} for e, c in sorted(per_event.items())]}
    with open(os.path.join(HERE, "limitless_v2_dev_events.json"), "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=1)

    L = ["Scoreboard v2: the 28 cells from the development half's pairings, against the Sept 23 table", "",
         f"{rows_used:,} panel matches from {len(events)} development events (split.json; holdout not read).",
         "Score = first deck's (W + T/2)/n. 'band' = the Sept 23 score's own 95% binomial band at v2's n.",
         "'outside' = the v2 score falls outside that band (descriptive: the samples overlap).", "",
         f"  {'pair':<24}{'Sept 23 W-L-T':>16}{'n':>6}{'score':>8}   {'v2 W-L-T':>14}{'n':>6}{'score':>8}"
         f"{'v2 - Sept23':>13}{'band':>9}  outside"]
    flagged = []
    for k in D.PAIRS:
        w0, l0, t0 = D.LIMITLESS[k]
        n0 = w0 + l0 + t0
        p0 = (w0 + 0.5 * t0) / n0
        w1, l1, t1 = cells[k]
        n1 = w1 + l1 + t1
        p1 = (w1 + 0.5 * t1) / n1 if n1 else float("nan")
        band = 1.96 * math.sqrt(p0 * (1 - p0) / n1) if n1 else float("nan")
        outside = n1 > 0 and abs(p1 - p0) > band
        if outside:
            flagged.append(k)
        L.append(f"  {k[0] + ' v ' + k[1]:<24}{f'{w0}-{l0}-{t0}':>16}{n0:>6}{100 * p0:>8.1f}   {f'{w1}-{l1}-{t1}':>14}"
                 f"{n1:>6}{100 * p1:>8.1f}{100 * (p1 - p0):>+13.1f}{100 * band:>9.1f}  {'OUTSIDE' if outside else ''}")
    L += ["", f"Cells outside the band: {len(flagged)} of 28" + (": " + ", ".join(f"{a} v {b}" for a, b in flagged) if flagged else ""),
          "Written: limitless_v2_dev.json, limitless_v2_dev_events.json, cells_v2.txt"]
    text = "\n".join(L) + "\n"
    print(text)
    with open(os.path.join(HERE, "cells_v2.txt"), "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
