"""Real Limitless cells for the kt carrier census list c-magnezone_ex_magnezone (Limitless archetype
"Magnezone ex Magnezone") against the eight panel archetypes.

Adapted from rl/results/b2e_card_check_2026-09-26/cells.py (the B2e specification, README section 3);
the counting rules are unchanged:
  * a match record counts for held archetype A vs panel archetype B when one side's deck_name is
    exactly A and the other side's archetype label is B (panel labels are 1:1 with panel deck_names);
  * every match record is one unit (BO1 and BO3 alike);
  * result_status "decisive" -> win or loss from A's side; "tie" (winner=0) -> half a point;
    "double_loss" (winner=-1) is NOT a tie: excluded from W-L-T and n, counted separately (DL);
    "bye_or_automatic_loss" has an empty opponent side and never forms an A-vs-B pair;
  * mirrors (same deck_name on both sides) are excluded;
  * score = (W + 0.5*T) / n, band = 1.96*sqrt(p(1-p)/n) in percentage points;
  * equal-weight average = mean of the K per-opponent scores (n > 0), band = 1.96*sqrt(sum p(1-p)/n)/K
    (the B2e panel_bands.py formula).

Holdout discipline: only matches.csv is read here (no standings file). Holdout-split rows feed the
POOLED cells only, exactly as B2e section 3 did; the development-half figure is reported beside them.
No holdout-only table is written.

Run from anywhere with Windows python:  python cells_c-magnezone_ex_magnezone.py
Writes cells_c-magnezone_ex_magnezone.csv / .md / .json next to this script.
"""
import csv
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "limitless_skill_model_2026-09-25"))
STEM = "c-magnezone_ex_magnezone"
OUT_CSV = os.path.join(HERE, "cells_%s.csv" % STEM)
OUT_MD = os.path.join(HERE, "cells_%s.md" % STEM)
OUT_JSON = os.path.join(HERE, "cells_%s.json" % STEM)

HELD = [(STEM, "Magnezone ex Magnezone")]
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
DATASETS = [("development", {"development"}), ("pooled", {"development", "holdout"})]


def load_rows():
    with open(os.path.join(SRC, "matches.csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def outcome(row, side):
    """Return 'W', 'L', 'T', 'DL' or 'BYE' from the point of view of side 1 or 2."""
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
        self.c = Counter()  # keys: W, L, T, DL and W_bo1, L_bo1, T_bo1, DL_bo1

    def add(self, res, mode):
        self.c[res] += 1
        if mode == "BO1":
            self.c[res + "_bo1"] += 1

    def W(self, s=""): return self.c["W" + s]
    def L(self, s=""): return self.c["L" + s]
    def T(self, s=""): return self.c["T" + s]
    def DL(self, s=""): return self.c["DL" + s]
    def n(self, s=""): return self.W(s) + self.L(s) + self.T(s)

    def score(self, s="", incl_dl=False):
        n = self.n(s) + (self.DL(s) if incl_dl else 0)
        if n == 0:
            return None
        return (self.W(s) + 0.5 * (self.T(s) + (self.DL(s) if incl_dl else 0))) / n

    def band(self, s=""):
        p, n = self.score(s), self.n(s)
        if p is None:
            return None
        return 1.96 * math.sqrt(p * (1 - p) / n)


def fmt_pct(x):
    return "" if x is None else "%.1f" % (100 * x)


def equal_weight(cells_for_arch):
    """(avg, band, K) over opponents with n > 0; panel_bands.py formula."""
    var = 0.0
    scores = []
    for p in PANEL:
        c = cells_for_arch[p]
        if c.n() == 0:
            continue
        s = c.score()
        scores.append(s)
        var += s * (1 - s) / c.n()
    k = len(scores)
    if k == 0:
        return None, None, 0
    return sum(scores) / k, 1.96 * math.sqrt(var) / k, k


def main():
    rows = load_rows()
    with open(os.path.join(SRC, "split.json"), encoding="utf-8") as f:
        split = json.load(f)
    with open(os.path.join(SRC, "events.json"), encoding="utf-8") as f:
        events = json.load(f)
    ev_split = Counter(e["split"] for e in events)
    ev_dates = sorted(e["date"] for e in events)

    status_counts = Counter(r["result_status"] for r in rows)
    mode_counts = Counter(r["mode"] for r in rows)
    held_names = {name: key for key, name in HELD}
    panel_names = {}
    for r in rows:
        for k in ("1", "2"):
            if r["archetype" + k] in PANEL:
                panel_names.setdefault(r["archetype" + k], set()).add(r["deck" + k + "_name"])

    cells = {ds: {k: {p: Cell() for p in PANEL} for k, _ in HELD} for ds, _ in DATASETS}
    totals = {k: {ds: Counter() for ds, _ in DATASETS} for k, _ in HELD}
    label_ids = {k: Counter() for k, _ in HELD}
    bo5_touching = 0

    for r in rows:
        ds_members = [ds for ds, members in DATASETS if r["split"] in members]
        for side, other in ((1, 2), (2, 1)):
            name = r["deck%d_name" % side]
            if name not in held_names:
                continue
            k = held_names[name]
            lab = r["archetype%d" % side]
            label_ids[k][(r["deck%d_id" % side], lab or "(no label)")] += 1
            res = outcome(r, side)
            for ds in ds_members:
                t = totals[k][ds]
                t["records"] += 1
                t["labeled" if lab else "unlabeled"] += 1
                if res in ("W", "L", "T"):
                    t["scored"] += 1
                elif res == "DL":
                    t["double_loss"] += 1
                else:
                    t["bye"] += 1
            if r["mode"] == "BO5":
                bo5_touching += 1
            opp_name = r["deck%d_name" % other]
            opp_lab = r["archetype%d" % other]
            if opp_name == name:  # mirror guard
                continue
            if opp_lab not in PANEL or res == "BYE":
                continue
            for ds in ds_members:
                cells[ds][k][opp_lab].add(res, r["mode"])
                totals[k][ds]["vs_panel_records"] += 1

    # ---------------- CSV ----------------
    fields = ["dataset", "archetype", "deck_name", "opponent", "opponent_deck_name",
              "W", "L", "T", "DL", "n", "score_pct", "band95_pts", "lo_pct", "hi_pct",
              "W_bo1", "L_bo1", "T_bo1", "DL_bo1", "n_bo1", "score_bo1_pct", "band95_bo1_pts",
              "n_incl_dl", "score_incl_dl_pct"]
    n_dev_rows = sum(1 for r in rows if r["split"] == "development")
    n_hold_rows = sum(1 for r in rows if r["split"] == "holdout")
    summary = {"window": {"start_date_utc": split["start_date_utc"], "end_date_utc": split["end_date_utc"],
                          "first_event_start": ev_dates[0], "last_event_start": ev_dates[-1],
                          "events_development": ev_split["development"], "events_holdout": ev_split["holdout"],
                          "events_total": len(events)},
               "records_total": len(rows), "records_development": n_dev_rows, "records_holdout": n_hold_rows,
               "result_status_counts": dict(status_counts),
               "mode_counts": dict(mode_counts), "bo5_records_touching_held": bo5_touching,
               "tie_treatment": ("tie -> 0.5 point (counted in T and n); double_loss -> excluded from W-L-T and n "
                                 "(reported in DL, alternate score_incl_dl treats it as a tie); "
                                 "bye_or_automatic_loss -> no opponent side, never forms an A-vs-B pair; "
                                 "mirrors excluded; every record (BO1 and BO3) is one unit; holdout rows feed "
                                 "the pooled cells only"),
               "archetypes": {}}
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for ds, _ in DATASETS:
            for k, name in HELD:
                pooled = Cell()
                for p in PANEL:
                    c = cells[ds][k][p]
                    pooled.c.update(c.c)
                    w.writerow({
                        "dataset": ds, "archetype": k, "deck_name": name, "opponent": p,
                        "opponent_deck_name": "/".join(sorted(panel_names.get(p, []))),
                        "W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(),
                        "score_pct": fmt_pct(c.score()), "band95_pts": fmt_pct(c.band()),
                        "lo_pct": "" if c.score() is None else "%.1f" % (100 * max(0.0, c.score() - c.band())),
                        "hi_pct": "" if c.score() is None else "%.1f" % (100 * min(1.0, c.score() + c.band())),
                        "W_bo1": c.W("_bo1"), "L_bo1": c.L("_bo1"), "T_bo1": c.T("_bo1"), "DL_bo1": c.DL("_bo1"),
                        "n_bo1": c.n("_bo1"), "score_bo1_pct": fmt_pct(c.score("_bo1")),
                        "band95_bo1_pts": fmt_pct(c.band("_bo1")),
                        "n_incl_dl": c.n() + c.DL(), "score_incl_dl_pct": fmt_pct(c.score(incl_dl=True)),
                    })
                avg, avg_band, kk = equal_weight(cells[ds][k])
                w.writerow({
                    "dataset": ds, "archetype": k, "deck_name": name, "opponent": "panel_equal_weight",
                    "opponent_deck_name": "%d of %d opponents with n>0" % (kk, len(PANEL)),
                    "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                    "score_pct": fmt_pct(avg), "band95_pts": fmt_pct(avg_band),
                    "lo_pct": "" if avg is None else "%.1f" % (100 * max(0.0, avg - avg_band)),
                    "hi_pct": "" if avg is None else "%.1f" % (100 * min(1.0, avg + avg_band)),
                    "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                    "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": "", "band95_bo1_pts": "",
                    "n_incl_dl": pooled.n() + pooled.DL(), "score_incl_dl_pct": "",
                })
                w.writerow({
                    "dataset": ds, "archetype": k, "deck_name": name, "opponent": "panel_pooled",
                    "opponent_deck_name": "all panel matches pooled (match-weighted)",
                    "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                    "score_pct": fmt_pct(pooled.score()), "band95_pts": fmt_pct(pooled.band()),
                    "lo_pct": "" if pooled.score() is None else "%.1f" % (100 * max(0.0, pooled.score() - pooled.band())),
                    "hi_pct": "" if pooled.score() is None else "%.1f" % (100 * min(1.0, pooled.score() + pooled.band())),
                    "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                    "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": fmt_pct(pooled.score("_bo1")),
                    "band95_bo1_pts": fmt_pct(pooled.band("_bo1")),
                    "n_incl_dl": pooled.n() + pooled.DL(), "score_incl_dl_pct": fmt_pct(pooled.score(incl_dl=True)),
                })
                a = summary["archetypes"].setdefault(k, {"deck_name": name})
                a[ds] = {
                    "equal_weight_avg_pct": None if avg is None else round(100 * avg, 1),
                    "equal_weight_band95_pts": None if avg_band is None else round(100 * avg_band, 1),
                    "opponents_with_data": kk,
                    "panel_pooled": {"W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(),
                                     "n": pooled.n(), "n_bo1": pooled.n("_bo1"),
                                     "score_pct": None if pooled.score() is None else round(100 * pooled.score(), 1),
                                     "band95_pts": None if pooled.band() is None else round(100 * pooled.band(), 1)},
                    "thinnest_cell_n": min(cells[ds][k][p].n() for p in PANEL),
                    "records_in_window": totals[k][ds]["records"],
                    "records_labeled": totals[k][ds]["labeled"],
                    "records_unlabeled": totals[k][ds]["unlabeled"],
                    "records_scored": totals[k][ds]["scored"],
                    "records_double_loss": totals[k][ds]["double_loss"],
                    "records_bye": totals[k][ds]["bye"],
                    "cells": {p: {"W": cells[ds][k][p].W(), "L": cells[ds][k][p].L(), "T": cells[ds][k][p].T(),
                                  "DL": cells[ds][k][p].DL(), "n": cells[ds][k][p].n(),
                                  "n_bo1": cells[ds][k][p].n("_bo1"),
                                  "score_pct": None if cells[ds][k][p].score() is None else round(100 * cells[ds][k][p].score(), 1),
                                  "band95_pts": None if cells[ds][k][p].band() is None else round(100 * cells[ds][k][p].band(), 1)}
                              for p in PANEL},
                }
                a["deck_ids_and_labels"] = {"%s [%s]" % (i, lab): c for (i, lab), c in sorted(label_ids[k].items())}

    # ---------------- Markdown ----------------
    md = []
    md.append("# Limitless cells: Magnezone ex Magnezone against the eight panel decks (kt carrier census)\n")
    md.append("Descriptive only; this file reports and decides nothing. Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` "
              "(%s match records). Script: `cells_%s.py` in this folder (adapted from B2e's `cells.py`, same counting rules). "
              "Machine-readable: `cells_%s.csv`, `cells_%s.json`.\n" % (format(len(rows), ","), STEM, STEM, STEM))
    md.append("## Window and data sets\n")
    md.append("- Event window (split.json): **%s to %s** (UTC event start dates). First event start %s, last %s."
              % (split["start_date_utc"], split["end_date_utc"], ev_dates[0], ev_dates[-1]))
    md.append("- Events (events.json): **%d** total, **%d development**, **%d holdout** (random half split, seed %s)."
              % (len(events), ev_split["development"], ev_split["holdout"], split["seed"]))
    md.append("- Records by split: development %s, holdout %s. Pooled = both halves. Holdout rows are used for the "
              "pooled cells only (B2e README section 3); no holdout standings file was opened and no holdout-only "
              "table is written." % (format(n_dev_rows, ","), format(n_hold_rows, ",")))
    md.append("- Records by mode: " + ", ".join("%s %s" % (m, format(c, ",")) for m, c in mode_counts.most_common()) +
              ". Every record is one unit (a BO3 set is one record). BO5 records touching this archetype: %d." % bo5_touching)
    md.append("")
    md.append("## Counting rules (B2e's, unchanged)\n")
    md.append("The held side is identified by exact deck_name (\"Magnezone ex Magnezone\"), the panel side by archetype label "
              "(each label maps to exactly one deck_name); a tie is half a point and counts in n; a double loss (winner = -1) "
              "is excluded from W-L-T and n and reported as DL; byes never form a pair; mirrors are excluded; every record is "
              "one unit; score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points (0 at 0% or 100%: read those cells as "
              "\"no information\"). Equal-weight = mean of the eight cell scores (opponents with n > 0), band from the same "
              "binomial formula divided by the number of opponents (B2e `panel_bands.py`); match-weighted = all panel matches pooled.\n")
    md.append("Panel opponents identified by archetype label; each label maps to exactly one deck_name: " +
              ", ".join("%s = %s" % (p, "/".join(sorted(panel_names[p]))) for p in PANEL) + ".\n")
    for k, name in HELD:
        md.append("## Identification of the held archetype\n")
        md.append("Held side identified by exact deck_name. Deck ids and labels found under the name (all records in the window, any opponent):\n")
        md.append("| deck_name | deck_id [label] : records | labeled | unlabeled |")
        md.append("|---|---|---:|---:|")
        ids = "; ".join("`%s` [%s]: %d" % (i, lab, c) for (i, lab), c in sorted(label_ids[k].items()))
        md.append("| %s | %s | %d | %d |" % (name, ids, totals[k]["pooled"]["labeled"], totals[k]["pooled"]["unlabeled"]))
        md.append("")
        md.append("## The cells\n")
        md.append("Cell format: W-L-T, n, score %, +/- 95% band. DL = double losses excluded.\n")
        md.append("| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |")
        md.append("|---|---|---:|---:|---:|---|---:|---:|---:|")
        for p in PANEL:
            d = cells["development"][k][p]
            q = cells["pooled"][k][p]

            def part(c):
                if c.n() == 0:
                    return "no games | 0 | | "
                return "%d-%d-%d%s | %d | %.1f | %.1f" % (c.W(), c.L(), c.T(), (" (DL %d)" % c.DL()) if c.DL() else "",
                                                          c.n(), 100 * c.score(), 100 * c.band())
            md.append("| %s | %s | %s |" % (p, part(d), part(q)))
        da, db, dk = equal_weight(cells["development"][k])
        pa, pb, pk = equal_weight(cells["pooled"][k])
        md.append("| **Equal-weight average** | %d opp. | | **%.1f** | %.1f | %d opp. | | **%.1f** | %.1f |"
                  % (dk, 100 * da, 100 * db, pk, 100 * pa, 100 * pb))
        dp = Cell(); pp = Cell()
        for p in PANEL:
            dp.c.update(cells["development"][k][p].c)
            pp.c.update(cells["pooled"][k][p].c)
        md.append("| Match-weighted | %d-%d-%d (DL %d) | %d | %.1f | %.1f | %d-%d-%d (DL %d) | %d | %.1f | %.1f |"
                  % (dp.W(), dp.L(), dp.T(), dp.DL(), dp.n(), 100 * dp.score(), 100 * dp.band(),
                     pp.W(), pp.L(), pp.T(), pp.DL(), pp.n(), 100 * pp.score(), 100 * pp.band()))
        md.append("")
        md.append("Pooled equal-weight interval: **%.1f to %.1f** (development %.1f to %.1f). Thinnest pooled cell: n = %d; "
                  "thinnest development cell: n = %d.\n"
                  % (100 * max(0, pa - pb), 100 * min(1, pa + pb), 100 * max(0, da - db), 100 * min(1, da + db),
                     min(cells["pooled"][k][p].n() for p in PANEL), min(cells["development"][k][p].n() for p in PANEL)))
        md.append("BO1-only figures (single-game units), pooled: " + "; ".join(
            "%s %d-%d-%d n=%d%s" % (p, cells["pooled"][k][p].W("_bo1"), cells["pooled"][k][p].L("_bo1"),
                                    cells["pooled"][k][p].T("_bo1"), cells["pooled"][k][p].n("_bo1"),
                                    (" (%.1f%%)" % (100 * cells["pooled"][k][p].score("_bo1"))) if cells["pooled"][k][p].n("_bo1") else "")
            for p in PANEL) + ".\n")
        md.append("Totals for this archetype (all opponents, any status):\n")
        md.append("| data set | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |")
        md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for ds, _ in DATASETS:
            t = totals[k][ds]
            md.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" % (
                ds, t["records"], t["labeled"], t["unlabeled"], t["scored"], t["double_loss"], t["bye"],
                sum(cells[ds][k][p].n() for p in PANEL), min(cells[ds][k][p].n() for p in PANEL)))
        md.append("")
    md.append("## Notes\n")
    md.append("- Thin cells (n under about 20) have bands of 20+ points; a cell at exactly 0% or 100% shows a +/-0.0 band and carries no real information.")
    md.append("- The pooled equal-weight average is the average of the pooled cells, not the average of the two halves' averages.")
    md.append("- A BO3 record is one match unit, the same convention as the scoreboard; the BO1-only numbers are for readers who want single-game units.")
    md.append("- The holdout half was spent once on Sept 25 (kp3 confirmation), so nothing here is a fresh test; development and pooled alike are descriptive baselines. Pooled is the reference figure, as in B2e.")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("wrote %s\nwrote %s\nwrote %s" % (OUT_CSV, OUT_MD, OUT_JSON))
    print("\n".join(md))


if __name__ == "__main__":
    main()
