"""Limitless cells for the kt carrier census list c-mega_lucario_ex_lucario (archetype
"Mega Lucario ex Lucario") against the eight panel archetypes, development half and pooled.

Adapted from rl/results/b2e_card_check_2026-09-26/cells.py (same counting rules, README section 3):
  * a match record counts for held archetype A vs panel archetype B when one side's deck_name is
    exactly A and the other side's archetype label is B (panel labels are 1:1 with panel deck_names);
  * every match record is one unit (BO1 and BO3 alike);
  * result_status "decisive" -> win or loss from A's side; "tie" (winner=0) -> half a point;
    "double_loss" (winner=-1) is excluded from W-L-T and n and reported in DL;
    "bye_or_automatic_loss" has no opponent side and never forms a pair;
  * mirrors (same deck_name on both sides) are excluded. The held archetype here IS the panel's
    lucario deck_name, so the lucario cell is a mirror by construction and has no games;
  * score = (W + 0.5*T) / n, band = 1.96*sqrt(p(1-p)/n) in points;
  * equal-weight average = mean of the per-opponent scores over opponents with n > 0, with band
    1.96*sqrt(sum p(1-p)/n)/K (rl/results/b2e_card_check_2026-09-26/panel_bands.py).

Holdout discipline: only matches.csv is read here (never a standings file); holdout rows enter the
pooled cells only, as B2e section 3 did. Development-only cells are reported beside them.

Run from anywhere with Windows python:  python cells_c-mega_lucario_ex_lucario.py
Writes cells_c-mega_lucario_ex_lucario.csv / .md / .json next to this script.
"""
import csv
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "limitless_skill_model_2026-09-25"))
STEM = "c-mega_lucario_ex_lucario"
OUT_CSV = os.path.join(HERE, f"cells_{STEM}.csv")
OUT_MD = os.path.join(HERE, f"cells_{STEM}.md")
OUT_JSON = os.path.join(HERE, f"cells_{STEM}.json")

HELD_KEY = "mega_lucario_ex_lucario"
HELD_NAME = "Mega Lucario ex Lucario"
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
    with open(os.path.join(SRC, "matches.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(SRC, "split.json"), encoding="utf-8") as f:
        split = json.load(f)
    dev_ids = set(split["development_event_ids"])
    hold_ids = set(split["holdout_event_ids"])
    assert not dev_ids & hold_ids

    panel_names = {}
    for r in rows:
        for k in ("1", "2"):
            if r["archetype" + k] in PANEL:
                panel_names.setdefault(r["archetype" + k], set()).add(r["deck" + k + "_name"])

    cells = {ds: {p: Cell() for p in PANEL} for ds, _ in DATASETS}
    totals = {ds: Counter() for ds, _ in DATASETS}
    ids_labels = Counter()
    mirrors = {ds: 0 for ds, _ in DATASETS}
    split_check = Counter()

    for r in rows:
        # consistency: the row's split must agree with split.json
        if r["event_id"] in dev_ids:
            split_check["dev_ok" if r["split"] == "development" else "dev_MISMATCH"] += 1
        elif r["event_id"] in hold_ids:
            split_check["hold_ok" if r["split"] == "holdout" else "hold_MISMATCH"] += 1
        else:
            split_check["unknown_event"] += 1
        ds_members = [ds for ds, members in DATASETS if r["split"] in members]
        for side, other in ((1, 2), (2, 1)):
            name = r[f"deck{side}_name"]
            if name != HELD_NAME:
                continue
            lab = r[f"archetype{side}"]
            ids_labels[(r[f"deck{side}_id"], lab or "(no label)")] += 1
            res = outcome(r, side)
            for ds in ds_members:
                t = totals[ds]
                t["records"] += 1
                t["labeled" if lab else "unlabeled"] += 1
                if res in ("W", "L", "T"):
                    t["scored"] += 1
                elif res == "DL":
                    t["double_loss"] += 1
                else:
                    t["bye"] += 1
            opp_name = r[f"deck{other}_name"]
            opp_lab = r[f"archetype{other}"]
            if opp_name == name:  # mirror: excluded (this is the whole lucario cell)
                if res != "BYE":
                    for ds in ds_members:
                        mirrors[ds] += 1
                continue
            if opp_lab not in PANEL or res == "BYE":
                continue
            for ds in ds_members:
                cells[ds][opp_lab].add(res, r["mode"])
                totals[ds]["vs_panel_records"] += 1

    # mirrors are counted twice above (once per side); report per record
    for ds in mirrors:
        mirrors[ds] //= 2

    # ---------------- CSV ----------------
    fields = ["dataset", "archetype", "deck_name", "opponent", "opponent_deck_name",
              "W", "L", "T", "DL", "n", "score_pct", "band95_pts", "lo_pct", "hi_pct",
              "W_bo1", "L_bo1", "T_bo1", "DL_bo1", "n_bo1", "score_bo1_pct", "band95_bo1_pts"]
    summary = {"archetype": HELD_KEY, "deck_name": HELD_NAME, "source": "rl/results/limitless_skill_model_2026-09-25/matches.csv",
               "records_total": len(rows), "split_consistency": dict(split_check),
               "deck_ids_and_labels": {f"{i} [{lab}]": c for (i, lab), c in sorted(ids_labels.items())},
               "panel_deck_names": {p: sorted(panel_names.get(p, [])) for p in PANEL},
               "mirror_records_excluded": mirrors, "datasets": {}}
    md_tables = {}
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for ds, _ in DATASETS:
            pooled = Cell()
            scores, var = [], 0.0
            for p in PANEL:
                c = cells[ds][p]
                pooled.c.update(c.c)
                if c.n() > 0:
                    scores.append(c.score())
                    var += c.score() * (1 - c.score()) / c.n()
                w.writerow({
                    "dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": p,
                    "opponent_deck_name": "/".join(sorted(panel_names.get(p, []))),
                    "W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(),
                    "score_pct": pct(c.score()), "band95_pts": pct(c.band()),
                    "lo_pct": "" if c.score() is None else f"{100 * max(0.0, c.score() - c.band()):.1f}",
                    "hi_pct": "" if c.score() is None else f"{100 * min(1.0, c.score() + c.band()):.1f}",
                    "W_bo1": c.W("_bo1"), "L_bo1": c.L("_bo1"), "T_bo1": c.T("_bo1"), "DL_bo1": c.DL("_bo1"),
                    "n_bo1": c.n("_bo1"), "score_bo1_pct": pct(c.score("_bo1")), "band95_bo1_pts": pct(c.band("_bo1")),
                })
            K = len(scores)
            avg = sum(scores) / K if K else None
            avg_band = 1.96 * math.sqrt(var) / K if K else None
            w.writerow({"dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": "panel_equal_weight",
                        "opponent_deck_name": f"{K} of {len(PANEL)} opponents with n>0",
                        "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                        "score_pct": pct(avg), "band95_pts": pct(avg_band),
                        "lo_pct": "" if avg is None else f"{100 * max(0.0, avg - avg_band):.1f}",
                        "hi_pct": "" if avg is None else f"{100 * min(1.0, avg + avg_band):.1f}",
                        "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                        "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": "", "band95_bo1_pts": ""})
            w.writerow({"dataset": ds, "archetype": HELD_KEY, "deck_name": HELD_NAME, "opponent": "panel_pooled",
                        "opponent_deck_name": "all panel matches pooled (match-weighted)",
                        "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                        "score_pct": pct(pooled.score()), "band95_pts": pct(pooled.band()),
                        "lo_pct": "" if pooled.score() is None else f"{100 * max(0.0, pooled.score() - pooled.band()):.1f}",
                        "hi_pct": "" if pooled.score() is None else f"{100 * min(1.0, pooled.score() + pooled.band()):.1f}",
                        "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                        "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": pct(pooled.score("_bo1")),
                        "band95_bo1_pts": pct(pooled.band("_bo1"))})
            summary["datasets"][ds] = {
                "equal_weight_avg_pct": None if avg is None else round(100 * avg, 1),
                "equal_weight_band95_pts": None if avg_band is None else round(100 * avg_band, 1),
                "opponents_with_data": K,
                "panel_pooled": {"W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                                 "n_bo1": pooled.n("_bo1"),
                                 "score_pct": None if pooled.score() is None else round(100 * pooled.score(), 1),
                                 "band95_pts": None if pooled.band() is None else round(100 * pooled.band(), 1)},
                "thinnest_cell_n_excluding_mirror": min(cells[ds][p].n() for p in PANEL if p != "lucario"),
                "records_in_window": totals[ds]["records"], "records_labeled": totals[ds]["labeled"],
                "records_unlabeled": totals[ds]["unlabeled"], "records_scored": totals[ds]["scored"],
                "records_double_loss": totals[ds]["double_loss"], "records_bye": totals[ds]["bye"],
                "cells": {p: {"W": cells[ds][p].W(), "L": cells[ds][p].L(), "T": cells[ds][p].T(), "DL": cells[ds][p].DL(),
                              "n": cells[ds][p].n(), "n_bo1": cells[ds][p].n("_bo1"),
                              "score_pct": None if cells[ds][p].score() is None else round(100 * cells[ds][p].score(), 1),
                              "band95_pts": None if cells[ds][p].band() is None else round(100 * cells[ds][p].band(), 1)}
                          for p in PANEL},
            }
            md_tables[ds] = (cells[ds], pooled, avg, avg_band, K)

    # ---------------- Markdown ----------------
    dev_cells, dev_pooled, dev_avg, dev_band, dev_K = md_tables["development"]
    po_cells, po_pooled, po_avg, po_band, po_K = md_tables["pooled"]
    md = []
    md.append(f"# Limitless cells: Mega Lucario ex Lucario against the eight panel decks\n")
    md.append(f"List: `decks/{STEM}.txt` (kt carrier census, Sept 26, 2026). Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` "
              f"({len(rows):,} match records), window 2026-08-26 to 2026-09-24, 63 development and 63 holdout events (split.json). "
              f"Script: `cells_{STEM}.py`; machine-readable: `cells_{STEM}.csv`, `cells_{STEM}.json`. "
              f"Counting rules are B2e's (`rl/results/b2e_card_check_2026-09-26/README.md` section 3, `cells.py`): the held side by exact deck_name, "
              f"the panel side by archetype label; a tie is half a point and counts in n; double losses are excluded and shown as DL; byes never form a pair; "
              f"every record is one unit (BO1 and BO3 alike); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points. "
              f"Only matches.csv was read; no standings file. Holdout rows enter the pooled cells only.\n")
    md.append("**The lucario cell is a mirror.** The archetype under review is the panel's own lucario deck (deck_name \"Mega Lucario ex Lucario\" on both "
              "sides), and the rules exclude mirrors, so that cell has no games and the equal-weight average is over the other seven opponents. "
              f"Mirror records set aside: development {mirrors['development']}, pooled {mirrors['pooled']}.\n")
    md.append("Cell format: W-L-T, n, score %, +/- 95% band. Equal-weight = unweighted mean of the cell scores (opponents with n > 0), band "
              "1.96 sqrt(sum p(1-p)/n)/K (`panel_bands.py` formula). Match-weighted = all panel matches pooled. DL = double losses excluded.\n")
    md.append("| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |")
    md.append("|---|---|---:|---:|---:|---|---:|---:|---:|")
    for p in PANEL:
        d, q = dev_cells[p], po_cells[p]
        if p == "lucario":
            md.append(f"| {p} | mirror, excluded | 0 | | | mirror, excluded | 0 | | |")
            continue
        md.append(f"| {p} | {d.W()}-{d.L()}-{d.T()} | {d.n()} | {pct(d.score())} | {pct(d.band())} | "
                  f"{q.W()}-{q.L()}-{q.T()} | {q.n()} | {pct(q.score())} | {pct(q.band())} |")
    md.append(f"| **Equal-weight average** | {dev_K} opp. | | **{pct(dev_avg)}** | {pct(dev_band)} | {po_K} opp. | | **{pct(po_avg)}** | {pct(po_band)} |")
    md.append(f"| Match-weighted | {dev_pooled.W()}-{dev_pooled.L()}-{dev_pooled.T()} (DL {dev_pooled.DL()}) | {dev_pooled.n()} | {pct(dev_pooled.score())} | {pct(dev_pooled.band())} | "
              f"{po_pooled.W()}-{po_pooled.L()}-{po_pooled.T()} (DL {po_pooled.DL()}) | {po_pooled.n()} | {pct(po_pooled.score())} | {pct(po_pooled.band())} |")
    md.append("")
    md.append("## Identification\n")
    md.append("Held side identified by exact deck_name. Deck ids and labels found under that name (all records in the window, any opponent):\n")
    md.append("| deck_id [label] | records |")
    md.append("|---|---:|")
    for (i, lab), c in sorted(ids_labels.items()):
        md.append(f"| `{i}` [{lab}] | {c} |")
    md.append("")
    md.append("Panel opponents by archetype label; each label maps to exactly one deck_name: " +
              ", ".join(f"{p} = {'/'.join(sorted(panel_names[p]))}" for p in PANEL) + ".\n")
    md.append("## Totals per data set (all opponents, any status)\n")
    md.append("| data set | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | mirror records set aside | thinnest non-mirror cell n |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for ds, _ in DATASETS:
        t = totals[ds]
        thin = min(cells[ds][p].n() for p in PANEL if p != "lucario")
        md.append(f"| {ds} | {t['records']} | {t['labeled']} | {t['unlabeled']} | {t['scored']} | {t['double_loss']} | {t['bye']} | "
                  f"{sum(cells[ds][p].n() for p in PANEL)} | {mirrors[ds]} | {thin} |")
    md.append("")
    md.append("## Notes\n")
    md.append("- These cells are descriptive baselines, not a test: the holdout half was spent on Sept 25 (B2e README section 3, \"How to read these cells\"). "
              "Pooled has twice the matches and is the reference figure; development is reported beside it.")
    md.append("- A cell at exactly 0% or 100% shows a +/-0.0 band; read it as no information, not as certain.")
    md.append("- BO1-only figures are in the CSV for readers who want single-game units.")
    md.append(f"- Split consistency check (matches.csv split column against split.json): {dict(split_check)}.")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}\nwrote {OUT_JSON}")
    print("\n".join(md))


if __name__ == "__main__":
    main()
