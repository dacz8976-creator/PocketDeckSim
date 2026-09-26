"""Limitless cells for "Jumpluff ex Team Rocket's Electrode" against the eight panel archetypes.

Adapted from rl/results/b2e_card_check_2026-09-26/cells.py (same counting rules, one archetype), plus the
equal-weight band from panel_bands.py. Reads rl/results/limitless_skill_model_2026-09-25/matches.csv and
split.json; writes cells_c-jumpluff_ex_team_rocket_s_electrode.md and .csv next to this script.

Rules (the scoreboard's, B2e README section 3):
  * the held side is identified by exact deck_name, the panel side by archetype label (each label maps to
    exactly one deck_name);
  * every match record is one unit (BO1 and BO3 alike);
  * "decisive" -> win or loss from the held side; "tie" (winner=0) -> half a point, counted in T and n;
    "double_loss" (winner=-1) -> excluded from W-L-T and n, reported in DL;
    "bye_or_automatic_loss" has no opponent side and never forms a pair; mirrors excluded;
  * score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points (collapses to 0 at 0% or 100%);
  * equal-weight average = mean of the cell scores with n > 0; its band = 1.96 sqrt(sum p(1-p)/n) / K.
Holdout discipline: holdout rows of matches.csv are used ONLY inside the pooled cells; no holdout-only
table is written and no holdout standings file is opened.

Run from anywhere with Windows python:  python cells_c-jumpluff_ex_team_rocket_s_electrode.py
"""
import csv
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "limitless_skill_model_2026-09-25"))
STEM = "c-jumpluff_ex_team_rocket_s_electrode"
OUT_MD = os.path.join(HERE, f"cells_{STEM}.md")
OUT_CSV = os.path.join(HERE, f"cells_{STEM}.csv")

HELD_NAME = "Jumpluff ex Team Rocket's Electrode"
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

    panel_names = {}
    for r in rows:
        for k in ("1", "2"):
            if r["archetype" + k] in PANEL:
                panel_names.setdefault(r["archetype" + k], set()).add(r["deck" + k + "_name"])

    cells = {ds: {p: Cell() for p in PANEL} for ds, _ in DATASETS}
    totals = {ds: Counter() for ds, _ in DATASETS}
    label_ids = Counter()
    opp_names = Counter()  # every opponent deck_name the held deck met (pooled), for context
    n_rows = Counter()
    for r in rows:
        n_rows[r["split"]] += 1
        ds_members = [ds for ds, members in DATASETS if r["split"] in members]
        for side, other in ((1, 2), (2, 1)):
            if r[f"deck{side}_name"] != HELD_NAME:
                continue
            label_ids[(r[f"deck{side}_id"], r[f"archetype{side}"] or "(no label)")] += 1
            res = outcome(r, side)
            for ds in ds_members:
                t = totals[ds]
                t["records"] += 1
                if res in ("W", "L", "T"):
                    t["scored"] += 1
                    t[res] += 1
                elif res == "DL":
                    t["double_loss"] += 1
                else:
                    t["bye"] += 1
            if res != "BYE":
                opp_names[r[f"deck{other}_name"]] += 1
            if r[f"deck{other}_name"] == HELD_NAME:
                continue  # mirror
            opp_lab = r[f"archetype{other}"]
            if opp_lab not in PANEL or res == "BYE":
                continue
            for ds in ds_members:
                cells[ds][opp_lab].add(res, r["mode"])

    # ---------- CSV ----------
    fields = ["dataset", "archetype", "opponent", "opponent_deck_name", "W", "L", "T", "DL", "n",
              "score_pct", "band95_pts", "W_bo1", "L_bo1", "T_bo1", "n_bo1", "score_bo1_pct"]
    summary = {}
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
                w.writerow({"dataset": ds, "archetype": HELD_NAME, "opponent": p,
                            "opponent_deck_name": "/".join(sorted(panel_names.get(p, []))),
                            "W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(),
                            "score_pct": pct(c.score()), "band95_pts": pct(c.band()),
                            "W_bo1": c.W("_bo1"), "L_bo1": c.L("_bo1"), "T_bo1": c.T("_bo1"),
                            "n_bo1": c.n("_bo1"), "score_bo1_pct": pct(c.score("_bo1"))})
            k = len(scores)
            avg = sum(scores) / k if k else None
            avg_band = (1.96 * math.sqrt(var) / k) if k else None
            w.writerow({"dataset": ds, "archetype": HELD_NAME, "opponent": "panel_equal_weight",
                        "opponent_deck_name": f"{k} of {len(PANEL)} opponents with n>0",
                        "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                        "score_pct": pct(avg), "band95_pts": pct(avg_band),
                        "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                        "n_bo1": pooled.n("_bo1"), "score_bo1_pct": ""})
            w.writerow({"dataset": ds, "archetype": HELD_NAME, "opponent": "panel_pooled",
                        "opponent_deck_name": "all panel matches pooled (match-weighted)",
                        "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                        "score_pct": pct(pooled.score()), "band95_pts": pct(pooled.band()),
                        "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                        "n_bo1": pooled.n("_bo1"), "score_bo1_pct": pct(pooled.score("_bo1"))})
            summary[ds] = {"pooled": pooled, "avg": avg, "avg_band": avg_band, "k": k}

    # ---------- Markdown ----------
    md = []
    md.append(f"# Limitless cells: {HELD_NAME} against the eight panel decks\n")
    md.append(f"Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` ({len(rows):,} match records; "
              f"development {n_rows['development']:,}, holdout {n_rows['holdout']:,}). Window {split['start_date_utc']} to "
              f"{split['end_date_utc']} (UTC event start dates), {len(dev_ids)} development and {len(hold_ids)} holdout events "
              f"(split seed {split['seed']}). Script: `cells_{STEM}.py` (adapted from B2e's `cells.py`, same rules). "
              f"Machine-readable: `cells_{STEM}.csv`.\n")
    md.append("Counting rules: the held side is identified by exact deck_name, the panel side by archetype label; a tie is half a "
              "point and counts in n; a double loss (winner = -1) is excluded from W-L-T and n and shown as DL; byes have no "
              "opponent side and never form a pair; mirrors are excluded; every record is one unit, BO1 and BO3 alike (BO1-only "
              "figures are in the CSV); score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% "
              "or 100% (read those cells as no information). Equal-weight = unweighted mean of the cell scores with n > 0, band "
              "= 1.96 sqrt(sum p(1-p)/n) / K, as B2e's `panel_bands.py`. Holdout rows are used only inside the pooled cells; no "
              "holdout-only table is written and no holdout standings file was opened. Pooled is the reference, as in B2e; "
              "development is reported beside it.\n")
    md.append("Panel labels: " + ", ".join(f"{p} = {'/'.join(sorted(panel_names[p]))}" for p in PANEL) + ".\n")
    md.append("Held side deck ids and labels found under this name (all records in the window, any opponent): " +
              "; ".join(f"`{i}` [{lab}]: {c}" for (i, lab), c in sorted(label_ids.items())) + ".\n")
    md.append("## The cells\n")
    md.append("Cell format: W-L-T, n, score %, +/- 95% band. DL = double losses excluded.\n")
    md.append("| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |")
    md.append("|---|---|---:|---:|---:|---|---:|---:|---:|")
    for p in PANEL:
        d, q = cells["development"][p], cells["pooled"][p]
        ds_ = ("no games" if d.n() == 0 else f"{d.W()}-{d.L()}-{d.T()}" + (f" (DL {d.DL()})" if d.DL() else ""))
        qs_ = ("no games" if q.n() == 0 else f"{q.W()}-{q.L()}-{q.T()}" + (f" (DL {q.DL()})" if q.DL() else ""))
        md.append(f"| {p} | {ds_} | {d.n()} | {pct(d.score())} | {pct(d.band())} | {qs_} | {q.n()} | {pct(q.score())} | {pct(q.band())} |")
    sd, sp = summary["development"], summary["pooled"]
    md.append(f"| **Equal-weight average** | {sd['k']} opp. | | **{pct(sd['avg'])}** | {pct(sd['avg_band'])} | {sp['k']} opp. | | **{pct(sp['avg'])}** | {pct(sp['avg_band'])} |")
    pd_, pp_ = sd["pooled"], sp["pooled"]
    md.append(f"| Match-weighted | {pd_.W()}-{pd_.L()}-{pd_.T()} (DL {pd_.DL()}) | {pd_.n()} | {pct(pd_.score())} | {pct(pd_.band())} | "
              f"{pp_.W()}-{pp_.L()}-{pp_.T()} (DL {pp_.DL()}) | {pp_.n()} | {pct(pp_.score())} | {pct(pp_.band())} |")
    md.append("")
    md.append("## Totals for this archetype (all opponents, any status)\n")
    md.append("| Data set | records | scored (W/L/T) | W | L | T | double loss | bye | vs panel (scored) | thinnest panel cell n |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for ds, _ in DATASETS:
        t = totals[ds]
        md.append(f"| {ds} | {t['records']} | {t['scored']} | {t['W']} | {t['L']} | {t['T']} | {t['double_loss']} | {t['bye']} | "
                  f"{sum(cells[ds][p].n() for p in PANEL)} | {min(cells[ds][p].n() for p in PANEL)} |")
    md.append("")
    md.append("Opponent deck names met most often (pooled, scored or double-loss records, for context only): " +
              "; ".join(f"{n} ({c})" for n, c in opp_names.most_common(12)) + ".\n")
    md.append("## Reading\n")
    thin = [p for p in PANEL if cells["pooled"][p].n() < 20]
    zero = [p for p in PANEL if cells["pooled"][p].n() == 0]
    md.append(f"- Pooled cells under 20 matches: {', '.join(thin) if thin else 'none'}"
              + (f"; with no games at all: {', '.join(zero)}" if zero else "") + ".")
    md.append("- These are descriptive baselines, not a test; the holdout half was spent on Sept 25 (B2e README section 3). "
              "Nothing here decides anything about the kt candidate.")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nwrote {OUT_MD}\nwrote {OUT_CSV}")


if __name__ == "__main__":
    main()
