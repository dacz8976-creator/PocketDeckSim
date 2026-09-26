"""95% bands for each held-out archetype's equal-weight panel average, from limitless_cells.csv.

The CSV gives a band for every cell and for the match-weighted pooled record, but leaves the
equal-weight average's band blank. This fills it in with the same binomial approximation the cells use:

    average = mean of the K per-opponent scores (opponents with n > 0)
    band    = 1.96 * sqrt( sum_o p_o (1 - p_o) / n_o ) / K     (in points)

A cell at exactly 0% or 100% contributes nothing to the sum (its own band collapses the same way), so the
bands for Whimsicott and Garchomp understate the real uncertainty. Read them with that in mind.

Run from this folder with Windows python:  python panel_bands.py
Writes panel_intervals.csv beside the script and prints the table.
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "limitless_cells.csv")
OUT = os.path.join(HERE, "panel_intervals.csv")
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
ARCHES = ["manectric_heliolisk", "raticate_ninetales", "hoopa_absol", "garchomp", "whimsicott_ariados", "charizardy_entei"]

rows = list(csv.DictReader(open(SRC, encoding="utf-8", newline="")))
out = []
for dataset in ("development", "pooled"):
    for arch in ARCHES:
        cells = {r["opponent"]: r for r in rows if r["dataset"] == dataset and r["archetype"] == arch}
        var = 0.0
        scores = []
        for opp in PANEL:
            c = cells[opp]
            n = int(c["n"])
            if n == 0:
                continue
            p = (int(c["W"]) + 0.5 * int(c["T"])) / n
            scores.append(100.0 * p)
            var += p * (1 - p) / n
        k = len(scores)
        avg = sum(scores) / k
        band = 100.0 * 1.96 * math.sqrt(var) / k
        pooled = cells["panel_pooled"]
        out.append({
            "dataset": dataset,
            "archetype": arch,
            "opponents": k,
            "equal_weight_avg_pct": round(avg, 1),
            "equal_weight_band95_pts": round(band, 1),
            "equal_weight_lo_pct": round(max(0.0, avg - band), 1),
            "equal_weight_hi_pct": round(min(100.0, avg + band), 1),
            "match_weighted_pct": pooled["score_pct"],
            "match_weighted_band95_pts": pooled["band95_pts"],
            "n": pooled["n"],
        })

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

for r in out:
    print("{dataset:11s} {archetype:20s} K={opponents} avg {equal_weight_avg_pct:5.1f} +/-{equal_weight_band95_pts:4.1f} "
          "[{equal_weight_lo_pct}, {equal_weight_hi_pct}]   match-weighted {match_weighted_pct} +/-{match_weighted_band95_pts} n={n}".format(**r))
