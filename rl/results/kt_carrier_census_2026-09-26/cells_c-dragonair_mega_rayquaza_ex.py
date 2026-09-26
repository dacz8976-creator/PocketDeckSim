"""Real Limitless cells for the kt-census carrier archetype "Dragonair Mega Rayquaza ex" against the
eight panel archetypes. Adapted from cells_c-mega_altaria_ex_igglybuff.py, itself adapted from
rl/results/b2e_card_check_2026-09-26/cells.py (same counting rules) with the equal-weight band from
panel_bands.py folded in.

Reads rl/results/limitless_skill_model_2026-09-25/matches.csv (plus split.json and events.json) and writes
cells_c-dragonair_mega_rayquaza_ex.{csv,md,json} next to this script.

Rules (the project's scoreboard convention, B2e README section 3):
  * a match record counts for held archetype A vs panel archetype B when one side's deck_name is
    exactly A and the other side's archetype label is B (panel labels are 1:1 with panel deck_names);
  * every match record is one unit (BO1 and BO3 alike);
  * result_status "decisive" -> win or loss from A's side; "tie" (winner=0) -> half a point, counted in n;
    "double_loss" (winner=-1) is excluded from W-L-T and n and reported in DL;
    "bye_or_automatic_loss" has no opponent side and never forms a pair; mirrors cannot occur, because
    the held deck_name is not one of the eight panel deck_names (a mirror guard is kept anyway);
  * score = (W + 0.5*T) / n, band = 1.96*sqrt(p(1-p)/n) in points (collapses to 0 at 0% or 100%);
  * equal-weight average = mean of the K cell scores with n > 0; its band =
    1.96 * sqrt(sum_o p_o(1-p_o)/n_o) / K (panel_bands.py).
Holdout discipline: only matches.csv rows are read here (development rows for the development cells,
both halves for the pooled cells, exactly as B2e section 3 did); no holdout standings file is opened.

Run from anywhere with Windows python:  python cells_c-dragonair_mega_rayquaza_ex.py
"""
import csv
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "limitless_skill_model_2026-09-25"))
STEM = "c-dragonair_mega_rayquaza_ex"
OUT_CSV = os.path.join(HERE, f"cells_{STEM}.csv")
OUT_MD = os.path.join(HERE, f"cells_{STEM}.md")
OUT_JSON = os.path.join(HERE, f"cells_{STEM}.json")

HELD_KEY = "dragonair_mega_rayquaza_ex"
HELD_NAME = "Dragonair Mega Rayquaza ex"
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
DATASETS = [("development", {"development"}), ("pooled", {"development", "holdout"})]


def outcome(row, side):
    st = row["result_status"]
    if st == "decisive":
        me = row["player1"] if side == 1 else row["player2"]
        return "W" if row["winner"] == me else "L"
    if st == "tie":
        return "T"
    if st == "double_loss":
        return "DL"
    return "BYE"


class Cell:
    def __init__(self):
        self.c = Counter()

    def add(self, res, mode):
        self.c[res] += 1
        if mode == "BO1":
            self.c[res + "_bo1"] += 1

    def W(self, s=""): return self.c["W" + s]
    def L(self, s=""): return self.c["L" + s]
    def T(self, s=""): return self.c["T" + s]
    def DL(self, s=""): return self.c["DL" + s]
    def n(self, s=""): return self.W(s) + self.L(s) + self.T(s)

    def score(self, s=""):
        n = self.n(s)
        return None if n == 0 else (self.W(s) + 0.5 * self.T(s)) / n

    def band(self, s=""):
        p, n = self.score(s), self.n(s)
        return None if p is None else 1.96 * math.sqrt(p * (1 - p) / n)


def pct(x):
    return "" if x is None else f"{100 * x:.1f}"


def main():
    csv.field_size_limit(10 ** 9)
    with open(os.path.join(SRC, "matches.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(SRC, "split.json"), encoding="utf-8") as f:
        split = json.load(f)
    with open(os.path.join(SRC, "events.json"), encoding="utf-8") as f:
        events = json.load(f)
    ev_split = Counter(e["split"] for e in events)
    dev_ids = set(split["development_event_ids"])
    hold_ids = set(split["holdout_event_ids"])
    assert not dev_ids & hold_ids

    panel_names = {}
    for r in rows:
        for k in ("1", "2"):
            if r["archetype" + k] in PANEL:
                panel_names.setdefault(r["archetype" + k], set()).add(r["deck" + k + "_name"])
    assert HELD_NAME not in {n for s in panel_names.values() for n in s}, "held name is a panel deck_name"

    cells = {ds: {p: Cell() for p in PANEL} for ds, _ in DATASETS}
    totals = {ds: Counter() for ds, _ in DATASETS}
    ids_seen = Counter()
    mirrors = {ds: 0 for ds, _ in DATASETS}
    split_check = Counter()
    for r in rows:
        if r["event_id"] in dev_ids:
            split_check["dev_ok" if r["split"] == "development" else "dev_MISMATCH"] += 1
        elif r["event_id"] in hold_ids:
            split_check["hold_ok" if r["split"] == "holdout" else "hold_MISMATCH"] += 1
        else:
            split_check["unknown_event"] += 1
        ds_members = [ds for ds, members in DATASETS if r["split"] in members]
        for side, other in ((1, 2), (2, 1)):
            if r[f"deck{side}_name"] != HELD_NAME:
                continue
            ids_seen[(r[f"deck{side}_id"], r[f"archetype{side}"] or "(no label)")] += 1
            res = outcome(r, side)
            for ds in ds_members:
                totals[ds]["records"] += 1
                totals[ds]["scored" if res in ("W", "L", "T") else res.lower()] += 1
            opp_lab = r[f"archetype{other}"]
            if r[f"deck{other}_name"] == HELD_NAME:
                for ds in ds_members:
                    mirrors[ds] += 1
                continue  # mirror guard (cannot fire for a panel cell; kept for the record)
            if opp_lab not in PANEL or res == "BYE":
                continue
            for ds in ds_members:
                cells[ds][opp_lab].add(res, r["mode"])
                totals[ds]["vs_panel_records"] += 1
    for ds in mirrors:
        mirrors[ds] //= 2  # counted once per side above

    # ---- aggregate per data set
    summary = {"archetype": HELD_NAME, "key": HELD_KEY, "source": os.path.join(SRC, "matches.csv"),
               "records_total": len(rows), "split_consistency": dict(split_check),
               "window": {"start_date_utc": split["start_date_utc"], "end_date_utc": split["end_date_utc"],
                          "events_development": ev_split["development"], "events_holdout": ev_split["holdout"]},
               "held_deck_ids_and_labels": {f"{i} [{lab}]": c for (i, lab), c in sorted(ids_seen.items())},
               "panel_deck_names": {p: sorted(panel_names.get(p, [])) for p in PANEL},
               "mirror_records_set_aside": mirrors, "datasets": {}}
    csv_rows = []
    md = []
    md.append(f"# Limitless cells: {HELD_NAME} against the eight panel decks\n")
    md.append(f"List: `decks/{STEM}.txt` (kt carrier census, Sept 26, 2026; thefossilman, 1st of 219, Umbreon99's Aura Sphere #4, "
              f"2026-09-11; provenance in `provenance/{STEM}.json`). The cells are for the Limitless archetype (exact deck_name "
              f"\"{HELD_NAME}\"), not for this one list: every list under that deck_name counts, whether or not it carries Gouging Fire "
              f"(135 of the 143 development-half lists do; census.csv).\n")
    md.append(f"Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` ({len(rows):,} match records), window "
              f"{split['start_date_utc']} to {split['end_date_utc']} (UTC event start dates), {ev_split['development']} development "
              f"and {ev_split['holdout']} holdout events. Script: `cells_{STEM}.py` (adapted from `cells_c-mega_altaria_ex_igglybuff.py`, "
              f"itself from B2e's `cells.py`; same counting rules). Machine-readable: `cells_{STEM}.csv`, `cells_{STEM}.json`.\n")
    md.append("Counting rules (B2e README section 3): the held side is identified by exact deck_name, the panel side by archetype label; "
              "a tie is half a point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and shown as DL; byes never "
              "form a pair; the held name is not a panel deck_name, so no panel cell is a mirror (Rayquaza-vs-Rayquaza records are set "
              "aside and counted below); every record is one unit, BO1 and BO3 alike (BO1-only figures in the CSV); "
              "score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% or 100% (read those as "
              "'no information'). Equal-weight average = unweighted mean of the cell scores with n > 0; its band = "
              "1.96 sqrt(sum p(1-p)/n) / K (`panel_bands.py`). Match-weighted = all panel matches pooled. Holdout discipline: only "
              "matches.csv rows are read (development rows for the development cells, both halves for the pooled cells, exactly as "
              "B2e section 3 did); no holdout standings file was opened.\n")
    md.append("Held deck ids under this name (all records in the window, any opponent): " +
              "; ".join(f"`{i}` [{lab}]: {c}" for (i, lab), c in sorted(ids_seen.items())) + ".\n")
    md.append("Panel labels: " + ", ".join(f"{p} = {'/'.join(sorted(panel_names.get(p, [])))}" for p in PANEL) + ".\n")

    per_ds = {}
    for ds, _ in DATASETS:
        pooled = Cell()
        scores, var = [], 0.0
        dsd = {"cells": {}}
        for p in PANEL:
            c = cells[ds][p]
            pooled.c.update(c.c)
            if c.n() > 0:
                s = c.score()
                scores.append(s)
                var += s * (1 - s) / c.n()
            dsd["cells"][p] = {"W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(), "n_bo1": c.n("_bo1"),
                               "score_pct": None if c.score() is None else round(100 * c.score(), 1),
                               "band95_pts": None if c.band() is None else round(100 * c.band(), 1),
                               "score_bo1_pct": None if c.score("_bo1") is None else round(100 * c.score("_bo1"), 1)}
            csv_rows.append({"dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": p,
                             "opponent_deck_name": "/".join(sorted(panel_names.get(p, []))),
                             "W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(),
                             "score_pct": pct(c.score()), "band95_pts": pct(c.band()),
                             "lo_pct": "" if c.score() is None else f"{100 * max(0.0, c.score() - c.band()):.1f}",
                             "hi_pct": "" if c.score() is None else f"{100 * min(1.0, c.score() + c.band()):.1f}",
                             "W_bo1": c.W("_bo1"), "L_bo1": c.L("_bo1"), "T_bo1": c.T("_bo1"), "DL_bo1": c.DL("_bo1"),
                             "n_bo1": c.n("_bo1"), "score_bo1_pct": pct(c.score("_bo1")), "band95_bo1_pts": pct(c.band("_bo1"))})
        K = len(scores)
        avg = sum(scores) / K if K else None
        avg_band = 1.96 * math.sqrt(var) / K if K else None
        dsd["equal_weight"] = {"opponents": K, "avg_pct": None if avg is None else round(100 * avg, 1),
                               "band95_pts": None if avg_band is None else round(100 * avg_band, 1),
                               "lo_pct": None if avg is None else round(100 * max(0.0, avg - avg_band), 1),
                               "hi_pct": None if avg is None else round(100 * min(1.0, avg + avg_band), 1)}
        dsd["match_weighted"] = {"W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                                 "n_bo1": pooled.n("_bo1"),
                                 "score_pct": None if pooled.score() is None else round(100 * pooled.score(), 1),
                                 "band95_pts": None if pooled.band() is None else round(100 * pooled.band(), 1)}
        dsd["totals"] = dict(totals[ds])
        dsd["mirror_records_set_aside"] = mirrors[ds]
        dsd["thinnest_cell_n"] = min(cells[ds][p].n() for p in PANEL)
        per_ds[ds] = dsd
        summary["datasets"][ds] = dsd
        csv_rows.append({"dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": "panel_equal_weight",
                         "opponent_deck_name": f"{K} of {len(PANEL)} opponents with n>0",
                         "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                         "score_pct": pct(avg), "band95_pts": pct(avg_band),
                         "lo_pct": "" if avg is None else f"{100 * max(0.0, avg - avg_band):.1f}",
                         "hi_pct": "" if avg is None else f"{100 * min(1.0, avg + avg_band):.1f}",
                         "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"), "DL_bo1": pooled.DL("_bo1"),
                         "n_bo1": pooled.n("_bo1"), "score_bo1_pct": "", "band95_bo1_pts": ""})
        csv_rows.append({"dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": "panel_pooled",
                         "opponent_deck_name": "all panel matches pooled (match-weighted)",
                         "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                         "score_pct": pct(pooled.score()), "band95_pts": pct(pooled.band()),
                         "lo_pct": "" if pooled.score() is None else f"{100 * max(0.0, pooled.score() - pooled.band()):.1f}",
                         "hi_pct": "" if pooled.score() is None else f"{100 * min(1.0, pooled.score() + pooled.band()):.1f}",
                         "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"), "DL_bo1": pooled.DL("_bo1"),
                         "n_bo1": pooled.n("_bo1"), "score_bo1_pct": pct(pooled.score("_bo1")), "band95_bo1_pts": pct(pooled.band("_bo1"))})

    # ---- the B2e-style side-by-side table (development beside pooled)
    md.append(f"## {HELD_NAME}\n")
    md.append("Cell format: W-L-T, n, score %, +/- 95% band (points). DL = double losses excluded.\n")
    md.append("| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |")
    md.append("|---|---|---:|---:|---:|---|---:|---:|---:|")
    for p in PANEL:
        d, q = per_ds["development"]["cells"][p], per_ds["pooled"]["cells"][p]

        def part(c):
            if c["n"] == 0:
                return "no games | 0 | | "
            wlt = f"{c['W']}-{c['L']}-{c['T']}" + (f" (DL {c['DL']})" if c["DL"] else "")
            return f"{wlt} | {c['n']} | {c['score_pct']:.1f} | {c['band95_pts']:.1f}"
        md.append(f"| {p} | {part(d)} | {part(q)} |")
    de, pe = per_ds["development"]["equal_weight"], per_ds["pooled"]["equal_weight"]
    md.append(f"| **Equal-weight average** | {de['opponents']} opp. | | **{de['avg_pct']}** | {de['band95_pts']} "
              f"| {pe['opponents']} opp. | | **{pe['avg_pct']}** | {pe['band95_pts']} |")
    dm, pm = per_ds["development"]["match_weighted"], per_ds["pooled"]["match_weighted"]
    md.append(f"| Match-weighted | {dm['W']}-{dm['L']}-{dm['T']} (DL {dm['DL']}) | {dm['n']} | {dm['score_pct']} | {dm['band95_pts']} "
              f"| {pm['W']}-{pm['L']}-{pm['T']} (DL {pm['DL']}) | {pm['n']} | {pm['score_pct']} | {pm['band95_pts']} |")
    md.append("")
    md.append("### The intervals in one place\n")
    md.append("| Data set | Equal-weight % | +/- | Interval | Opponents with data | Matches vs panel | Thinnest cell n | Records in window (any opponent) | Mirror records set aside |")
    md.append("|---|---:|---:|---|---:|---:|---:|---:|---:|")
    for ds, _ in DATASETS:
        e, m, t = per_ds[ds]["equal_weight"], per_ds[ds]["match_weighted"], per_ds[ds]["totals"]
        md.append(f"| {ds} | {e['avg_pct']} | {e['band95_pts']} | {e['lo_pct']} to {e['hi_pct']} | {e['opponents']} of 8 | {m['n']} "
                  f"| {per_ds[ds]['thinnest_cell_n']} | {t.get('records', 0)} (scored {t.get('scored', 0)}, DL {t.get('dl', 0)}, bye {t.get('bye', 0)}) "
                  f"| {mirrors[ds]} |")
    md.append("")
    thin = [p for p in PANEL if per_ds["pooled"]["cells"][p]["n"] < 20]
    md.append("### Notes\n")
    md.append(f"- Pooled cells under 20 matches (bands of 20+ points): {', '.join(thin) if thin else 'none'}. "
              "A cell at exactly 0% or 100% shows a +/-0.0 band and contributes nothing to the equal-weight band, which then "
              "understates the real uncertainty.")
    md.append("- Pooled (both halves) is the reference figure the B2e README uses for its veto rule; the development-half figure "
              "is reported beside it. These are descriptive cells, not a test: the holdout half was spent on Sept 25.")
    md.append("- The archetype's window rank by development matches is 6 (census.csv), so its cells are among the thickest of the "
              "census lists; none of the eight panel cells is thin.")
    md.append(f"- Split consistency check (matches.csv split column against split.json): {dict(split_check)}.")
    md.append("- This file reports; it decides nothing and changes no rule.")

    fields = list(csv_rows[0].keys())
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(csv_rows)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("\n".join(md))
    print(f"\nwrote {OUT_CSV}\nwrote {OUT_MD}\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
