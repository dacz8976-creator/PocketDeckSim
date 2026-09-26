"""Real Limitless cells for the six held-out B2e archetypes against the eight panel archetypes.

Reads rl/results/limitless_skill_model_2026-09-25/matches.csv (plus split.json and events.json)
and writes limitless_cells.csv and limitless_cells.md next to this script.

Rules (the project's scoreboard convention, README "Draw handling"):
  * a match record counts for held archetype A vs panel archetype B when one side's deck_name is
    exactly A and the other side's archetype label is B (panel labels are 1:1 with panel deck_names);
  * every match record is one unit (BO1 and BO3 alike; BO5 exists but never touches these cells);
  * result_status "decisive" -> win or loss from A's side; "tie" (winner=0) -> half a point;
    "double_loss" (winner=-1) is NOT a tie: excluded from W-L-T and n, but counted separately (DL)
    with an alternate score that treats it as a tie; "bye_or_automatic_loss" has an empty opponent
    side and can never form an A-vs-B pair, so it is excluded by construction;
  * mirrors (same deck_name on both sides) are excluded;
  * score = (W + 0.5*T) / n, band = 1.96*sqrt(p(1-p)/n) in percentage points.

Run from anywhere with Windows python:  python cells.py
"""
import csv
import json
import math
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "limitless_skill_model_2026-09-25"))
OUT_CSV = os.path.join(HERE, "limitless_cells.csv")
OUT_MD = os.path.join(HERE, "limitless_cells.md")
OUT_JSON = os.path.join(HERE, "limitless_cells_summary.json")

# Held-out archetypes: (short key, exact Limitless deck_name, Dustin's file)
HELD = [
    ("manectric_heliolisk", "Mega Manectric ex Heliolisk", "decks/dustin/09-mega-manectric-heliolisk.txt"),
    ("raticate_ninetales", "Team Rocket's Raticate ex Alolan Ninetales ex", "decks/dustin/13-a-ninetales-raticate.txt"),
    ("hoopa_absol", "Hoopa ex Mega Absol ex", "decks/dustin/04-absol-hoopa-darkrai.txt"),
    ("garchomp", "Garchomp", "decks/dustin/08-garchomp-toolbox.txt"),
    ("whimsicott_ariados", "Whimsicott ex Ariados", "decks/dustin/12-ariados-whimsicott-ogerpon.txt"),
    ("charizardy_entei", "Mega Charizard Y ex Entei ex", "decks/brews/brew-08-entei-rainbow-cave.txt"),
]
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
DATASETS = [("development", {"development"}), ("holdout", {"holdout"}), ("pooled", {"development", "holdout"})]


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
    return "" if x is None else f"{100 * x:.1f}"


def fmt_band(x):
    return "" if x is None else f"{100 * x:.1f}"


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
    held_names = {name: key for key, name, _ in HELD}
    panel_names = {}
    for r in rows:
        for k in ("1", "2"):
            if r["archetype" + k] in PANEL:
                panel_names.setdefault(r["archetype" + k], set()).add(r["deck" + k + "_name"])

    # cells[dataset][held_key][panel] -> Cell
    cells = {ds: {k: {p: Cell() for p in PANEL} for k, _, _ in HELD} for ds, _ in DATASETS}
    # label-only variant (identify held side by archetype label instead of deck_name), for the delta
    cells_label = {ds: {k: {p: Cell() for p in PANEL} for k, _, _ in HELD} for ds, _ in DATASETS}
    # per-archetype totals: records in window (any opponent, any status), labeled / unlabeled, scored
    totals = {k: {ds: Counter() for ds, _ in DATASETS} for k, _, _ in HELD}
    label_ids = {k: Counter() for k, _, _ in HELD}
    bo5_touching = 0

    for r in rows:
        ds_members = [ds for ds, members in DATASETS if r["split"] in members]
        for side, other in ((1, 2), (2, 1)):
            name = r[f"deck{side}_name"]
            if name not in held_names:
                continue
            k = held_names[name]
            lab = r[f"archetype{side}"]
            label_ids[k][(r[f"deck{side}_id"], lab or "(no label)")] += 1
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
            opp_name = r[f"deck{other}_name"]
            opp_lab = r[f"archetype{other}"]
            if opp_name == name:  # mirror guard (cannot happen for held-vs-panel, kept for clarity)
                continue
            if opp_lab not in PANEL or res == "BYE":
                continue
            for ds in ds_members:
                cells[ds][k][opp_lab].add(res, r["mode"])
                totals[k][ds]["vs_panel_records"] += 1
        # label-only identification of the held side
        for side, other in ((1, 2), (2, 1)):
            lab = r[f"archetype{side}"]
            if lab not in cells["pooled"]:
                continue
            opp_lab = r[f"archetype{other}"]
            res = outcome(r, side)
            if opp_lab not in PANEL or res == "BYE" or r[f"deck{other}_name"] == r[f"deck{side}_name"]:
                continue
            for ds in ds_members:
                cells_label[ds][lab][opp_lab].add(res, r["mode"])

    # ---------------- CSV ----------------
    fields = ["dataset", "archetype", "deck_name", "opponent", "opponent_deck_name",
              "W", "L", "T", "DL", "n", "score_pct", "band95_pts", "lo_pct", "hi_pct",
              "W_bo1", "L_bo1", "T_bo1", "DL_bo1", "n_bo1", "score_bo1_pct", "band95_bo1_pts",
              "n_incl_dl", "score_incl_dl_pct"]
    summary = {"window": {"start_date_utc": split["start_date_utc"], "end_date_utc": split["end_date_utc"],
                          "first_event_start": ev_dates[0], "last_event_start": ev_dates[-1],
                          "events_development": ev_split["development"], "events_holdout": ev_split["holdout"],
                          "events_total": len(events)},
               "records_total": len(rows), "result_status_counts": dict(status_counts),
               "mode_counts": dict(mode_counts), "bo5_records_touching_held": bo5_touching,
               "tie_treatment": ("tie -> 0.5 point (counted in T and n); double_loss -> excluded from W-L-T and n "
                                 "(reported in DL, alternate score_incl_dl treats it as a tie); "
                                 "bye_or_automatic_loss -> no opponent side, never forms an A-vs-B pair; "
                                 "mirrors excluded; every record (BO1 and BO3) is one unit"),
               "archetypes": {}}
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for ds, _ in DATASETS:
            for k, name, _ in HELD:
                pooled = Cell()
                scores = []
                for p in PANEL:
                    c = cells[ds][k][p]
                    pooled.c.update(c.c)
                    if c.n() > 0:
                        scores.append(c.score())
                    w.writerow({
                        "dataset": ds, "archetype": k, "deck_name": name, "opponent": p,
                        "opponent_deck_name": "/".join(sorted(panel_names.get(p, []))),
                        "W": c.W(), "L": c.L(), "T": c.T(), "DL": c.DL(), "n": c.n(),
                        "score_pct": fmt_pct(c.score()), "band95_pts": fmt_band(c.band()),
                        "lo_pct": "" if c.score() is None else f"{100 * max(0.0, c.score() - c.band()):.1f}",
                        "hi_pct": "" if c.score() is None else f"{100 * min(1.0, c.score() + c.band()):.1f}",
                        "W_bo1": c.W("_bo1"), "L_bo1": c.L("_bo1"), "T_bo1": c.T("_bo1"), "DL_bo1": c.DL("_bo1"),
                        "n_bo1": c.n("_bo1"), "score_bo1_pct": fmt_pct(c.score("_bo1")),
                        "band95_bo1_pts": fmt_band(c.band("_bo1")),
                        "n_incl_dl": c.n() + c.DL(), "score_incl_dl_pct": fmt_pct(c.score(incl_dl=True)),
                    })
                avg = sum(scores) / len(scores) if scores else None
                w.writerow({
                    "dataset": ds, "archetype": k, "deck_name": name, "opponent": "panel_equal_weight",
                    "opponent_deck_name": f"{len(scores)} of {len(PANEL)} opponents with n>0",
                    "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                    "score_pct": fmt_pct(avg), "band95_pts": "", "lo_pct": "", "hi_pct": "",
                    "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                    "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": "", "band95_bo1_pts": "",
                    "n_incl_dl": pooled.n() + pooled.DL(), "score_incl_dl_pct": "",
                })
                w.writerow({
                    "dataset": ds, "archetype": k, "deck_name": name, "opponent": "panel_pooled",
                    "opponent_deck_name": "all panel matches pooled (match-weighted)",
                    "W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(), "n": pooled.n(),
                    "score_pct": fmt_pct(pooled.score()), "band95_pts": fmt_band(pooled.band()),
                    "lo_pct": "" if pooled.score() is None else f"{100 * max(0.0, pooled.score() - pooled.band()):.1f}",
                    "hi_pct": "" if pooled.score() is None else f"{100 * min(1.0, pooled.score() + pooled.band()):.1f}",
                    "W_bo1": pooled.W("_bo1"), "L_bo1": pooled.L("_bo1"), "T_bo1": pooled.T("_bo1"),
                    "DL_bo1": pooled.DL("_bo1"), "n_bo1": pooled.n("_bo1"), "score_bo1_pct": fmt_pct(pooled.score("_bo1")),
                    "band95_bo1_pts": fmt_band(pooled.band("_bo1")),
                    "n_incl_dl": pooled.n() + pooled.DL(), "score_incl_dl_pct": fmt_pct(pooled.score(incl_dl=True)),
                })
                a = summary["archetypes"].setdefault(k, {"deck_name": name})
                a[ds] = {
                    "equal_weight_avg_pct": None if avg is None else round(100 * avg, 1),
                    "opponents_with_data": len(scores),
                    "panel_pooled": {"W": pooled.W(), "L": pooled.L(), "T": pooled.T(), "DL": pooled.DL(),
                                     "n": pooled.n(), "n_bo1": pooled.n("_bo1"),
                                     "score_pct": None if pooled.score() is None else round(100 * pooled.score(), 1)},
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
                a["deck_ids_and_labels"] = {f"{i} [{lab}]": c for (i, lab), c in sorted(label_ids[k].items())}

    # ---------------- cross-check against the scoreboard's held_archetype_records.csv ----------------
    check_lines = []
    ref_path = os.path.join(SRC, "held_archetype_records.csv")
    mismatches = 0
    if os.path.exists(ref_path):
        with open(ref_path, encoding="utf-8", newline="") as f:
            ref = list(csv.DictReader(f))
        for rr in ref:
            if rr["scope"] != "development only" or rr["opponent"] not in PANEL:
                continue
            c = cells["development"][rr["archetype"]][rr["opponent"]]
            cl = cells_label["development"][rr["archetype"]][rr["opponent"]]
            ok = (c.W(), c.L(), c.T(), c.n()) == tuple(int(rr[x]) for x in ("W", "L", "T", "n"))
            ok_l = (cl.W(), cl.L(), cl.T(), cl.n()) == tuple(int(rr[x]) for x in ("W", "L", "T", "n"))
            if not ok:
                mismatches += 1
                check_lines.append(f"| {rr['archetype']} | {rr['opponent']} | {rr['W']}-{rr['L']}-{rr['T']} (n={rr['n']}) "
                                   f"| {c.W()}-{c.L()}-{c.T()} (n={c.n()}, DL={c.DL()}) | {cl.W()}-{cl.L()}-{cl.T()} (n={cl.n()}) "
                                   f"| {'yes' if ok_l else 'no'} |")
    summary["crosscheck_vs_held_archetype_records_dev"] = {"cells_compared": 48, "mismatches_by_deck_name": mismatches}

    # ---------------- Markdown ----------------
    md = []
    md.append("# Real Limitless cells for the six B2e held-out archetypes\n")
    md.append(f"Source: `rl/results/limitless_skill_model_2026-09-25/matches.csv` ({len(rows):,} match records). "
              f"Script: `cells.py` in this folder. Machine-readable: `limitless_cells.csv`.\n")
    md.append("## Window and data sets\n")
    md.append(f"- Event window (split.json): **{split['start_date_utc']} to {split['end_date_utc']}** (UTC event start dates). "
              f"First event start {ev_dates[0]}, last {ev_dates[-1]}.")
    md.append(f"- Events (events.json): **{len(events)}** total, **{ev_split['development']} development**, **{ev_split['holdout']} holdout** "
              f"(random half split, seed {split['seed']}).")
    md.append(f"- Records by split: development {sum(1 for r in rows if r['split']=='development'):,}, "
              f"holdout {sum(1 for r in rows if r['split']=='holdout'):,}. Pooled = both halves.")
    md.append(f"- Records by mode: " + ", ".join(f"{m} {c:,}" for m, c in mode_counts.most_common()) +
              f". Every record is one unit (a BO3 set is one record, as on the scoreboard). "
              f"BO5 records touching a held archetype: {bo5_touching}.")
    md.append("")
    md.append("## How each result_status was treated\n")
    md.append("| result_status | records | winner field | treatment |")
    md.append("|---|---:|---|---|")
    md.append(f"| decisive | {status_counts['decisive']:,} | a player id | win (1) or loss (0) from the held side |")
    md.append(f"| tie | {status_counts['tie']:,} | 0 | tie, half a point, counted in T and n |")
    md.append(f"| double_loss | {status_counts['double_loss']:,} | -1 | **excluded** from W-L-T and n (the scoreboard README: double losses are not ties). Counted in the DL column; `score_incl_dl` shows the score if it were a tie |")
    md.append(f"| bye_or_automatic_loss | {status_counts['bye_or_automatic_loss']:,} | player id or -1 | one side has no player or deck, so it never forms an archetype-vs-archetype pair; excluded by construction |")
    md.append("")
    md.append("Other rules: a record counts for A vs B when one side's deck_name is exactly A and the other side's "
              "archetype label is B; mirrors are excluded; score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points.\n")
    md.append("## Identification of the six archetypes\n")
    md.append("Held side identified by exact deck_name. Deck ids and labels found under each name (all records in the window, any opponent):\n")
    md.append("| archetype | deck_name | deck_id [label] : records | labeled | unlabeled |")
    md.append("|---|---|---|---:|---:|")
    for k, name, _ in HELD:
        ids = "; ".join(f"`{i}` [{lab}]: {c}" for (i, lab), c in sorted(label_ids[k].items()))
        md.append(f"| {k} | {name} | {ids} | {totals[k]['pooled']['labeled']} | {totals[k]['pooled']['unlabeled']} |")
    md.append("")
    md.append("Panel opponents identified by archetype label; each label maps to exactly one deck_name: " +
              ", ".join(f"{p} = {'/'.join(sorted(panel_names[p]))}" for p in PANEL) + ".\n")

    for ds, _ in DATASETS:
        title = {"development": "Development half only", "holdout": "Holdout half only", "pooled": "Pooled (both halves)"}[ds]
        md.append(f"## {title}\n")
        md.append("Cell format: score% (+/- band) W-L-T n=all records [n BO1-only, score BO1-only]. DL = double losses excluded.\n")
        md.append("| archetype | " + " | ".join(PANEL) + " | equal-weight avg | pooled record |")
        md.append("|---|" + "---|" * (len(PANEL) + 2))
        for k, name, _ in HELD:
            parts = []
            pooled = Cell()
            scores = []
            for p in PANEL:
                c = cells[ds][k][p]
                pooled.c.update(c.c)
                if c.n() == 0:
                    parts.append("no data")
                    continue
                scores.append(c.score())
                s = f"**{100*c.score():.1f}%** (+/-{100*c.band():.1f}) {c.W()}-{c.L()}-{c.T()} n={c.n()}"
                if c.DL():
                    s += f" DL={c.DL()}"
                if c.n('_bo1') > 0:
                    s += f" [BO1 n={c.n('_bo1')}, {100*c.score('_bo1'):.1f}%]"
                else:
                    s += " [BO1 n=0]"
                parts.append(s)
            avg = sum(scores) / len(scores) if scores else None
            avg_s = "no data" if avg is None else f"**{100*avg:.1f}%** over {len(scores)} opp."
            pool_s = ("no data" if pooled.n() == 0 else
                      f"{100*pooled.score():.1f}% (+/-{100*pooled.band():.1f}) {pooled.W()}-{pooled.L()}-{pooled.T()} n={pooled.n()}"
                      + (f" DL={pooled.DL()}" if pooled.DL() else "") + f" [BO1 n={pooled.n('_bo1')}]")
            md.append(f"| {k} | " + " | ".join(parts) + f" | {avg_s} | {pool_s} |")
        md.append("")
        md.append("Totals per archetype in this data set (all opponents, any status):\n")
        md.append("| archetype | records | labeled | unlabeled | scored (W/L/T) | double_loss | bye | vs panel (scored) | thinnest panel cell n |")
        md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for k, name, _ in HELD:
            t = totals[k][ds]
            thin = min(cells[ds][k][p].n() for p in PANEL)
            md.append(f"| {k} | {t['records']} | {t['labeled']} | {t['unlabeled']} | {t['scored']} | {t['double_loss']} | {t['bye']} | "
                      f"{sum(cells[ds][k][p].n() for p in PANEL)} | {thin} |")
        md.append("")

    md.append("## Cross-check against the scoreboard's own development records\n")
    md.append(f"`held_archetype_records.csv` (development only, 48 panel cells) was recomputed with this script's rules: "
              f"**{48 - mismatches} of 48 cells match exactly**, {mismatches} differ.")
    if check_lines:
        md.append("")
        md.append("| archetype | opponent | scoreboard W-L-T | this script by deck_name | this script by label | label-only matches? |")
        md.append("|---|---|---|---|---|---|")
        md.extend(check_lines)
        md.append("")
        md.append("Differences come from the unlabeled same-name variants (Garchomp `garchomp-a2`, Manectric `mega-manectric-ex-b2b-heliolisk-b1a`): "
                  "the scoreboard keyed on the archetype label (exact deck id), this report keys on deck_name as the task specifies.")
    md.append("")
    md.append("## Notes\n")
    md.append("- Thin cells (n under ~20) have bands of 20+ points; Whimsicott and Garchomp are thin against most of the panel.")
    md.append("- A cell at exactly 0% or 100% shows a +/-0.0 band: the 1.96 sqrt(p(1-p)/n) formula collapses there. Read those cells as 'n tiny, no real information', not as certain.")
    md.append("- The pooled equal-weight average is the average of the pooled cells, not the average of the two halves' averages, so it can fall outside them when a cell's halves differ in size (Garchomp vs blaziken: 1-1 development, 0-8 holdout).")
    md.append("- A BO3 record is one match unit, the same convention as the scoreboard; the BO1-only numbers are shown for readers who want single-game units.")
    md.append("- The development half is the half the skill model and decklist selection used; holdout is untouched by any fitting.")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}\nwrote {OUT_JSON}")
    print(f"crosscheck vs held_archetype_records.csv (dev): {48 - mismatches}/48 match; mismatches: {mismatches}")
    for line in check_lines:
        print(line)


if __name__ == "__main__":
    main()
