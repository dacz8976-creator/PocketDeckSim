#!/usr/bin/env python3
"""Real Limitless cells for the gauntlet's new decks, by B2e's method, plus the frozen 28 for the 45-cell view.
Run from anywhere (WSL python3):  python3 gauntlet_cells.py      Writes gauntlet_cells.csv beside this script.

Source: rl/results/limitless_skill_model_2026-09-25/matches.csv (30,216 records, 63 development + 63 holdout events).

1. The new cells (B2e's rules, ../b2e_card_check_2026-09-26/cells.py, whose Cell and outcome() are imported here):
   the new deck's side is its exact Limitless deck_name, the panel side its archetype label (1:1 with a deck_name);
   a tie is half a point and counts in n; a double loss is out of W-L-T and n (its own DL column); byes never pair;
   mirrors are out; every record (BO1 or BO3) is one unit; score = (W + T/2)/n, band = 1.96 sqrt(p(1-p)/n).
   - 8 cells per new deck v the panel: Dragonair Mega Rayquaza ex and Mega Altaria ex Greninja (SCOREBOARD rows,
     16 cells) and Mega Scizor ex Revavroom (COVERAGE row, 8 cells, never in an accuracy total).
   - The 17th scoreboard cell, Dragonair Mega Rayquaza ex v Mega Altaria ex Greninja: exact deck_name on both sides
     (neither has an archetype label in matches.csv; each has one deck id).
   - Development half, holdout half and pooled. The holdout was spent once (kp3's confirmation, Sept 25), so
     pooled is descriptive, as in B2e; the development half is the scoreboard's half (scoreboard v2).
2. The frozen 28 (scoreboard v2, ../scoreboard_v2_2026-09-25/build_v2.py's rule: both sides by panel label,
   decisive or tie, one pairing = one match, first-named deck alphabetically). The development cells are recomputed
   from matches.csv and must equal limitless_v2_dev.json exactly (they are frozen; this only proves the rule is the
   same); pooled is added beside them for the 45-cell view.
3. Cross-check of this script's loop: B2e's 6 archetypes x 8 panel cells, development and pooled, must reproduce
   ../b2e_card_check_2026-09-26/limitless_cells.csv's W, L, T, DL and n exactly.
Exit 1 if a check fails.
"""
import csv
import json
import math
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(RES, "b2e_card_check_2026-09-26"))
sys.dont_write_bytecode = True
from cells import Cell, outcome  # noqa: E402  (B2e's own counting)

SRC = os.path.join(RES, "limitless_skill_model_2026-09-25", "matches.csv")
V2 = os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json")
B2E_CSV = os.path.join(RES, "b2e_card_check_2026-09-26", "limitless_cells.csv")
OUT = os.path.join(HERE, "gauntlet_cells.csv")

PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
TABLE = sorted(PANEL)  # the table's (and scoreboard v2's) alphabetical order
# key, exact Limitless deck_name, role
NEW = [("scizor", "Mega Scizor ex Revavroom", "coverage"),
       ("rayquaza", "Dragonair Mega Rayquaza ex", "scoreboard"),
       ("altaria_greninja", "Mega Altaria ex Greninja", "scoreboard")]
B2E = [("manectric_heliolisk", "Mega Manectric ex Heliolisk"),
       ("raticate_ninetales", "Team Rocket's Raticate ex Alolan Ninetales ex"), ("hoopa_absol", "Hoopa ex Mega Absol ex"),
       ("garchomp", "Garchomp"), ("whimsicott_ariados", "Whimsicott ex Ariados"),
       ("charizardy_entei", "Mega Charizard Y ex Entei ex")]
DATASETS = [("development", {"development"}), ("holdout", {"holdout"}), ("pooled", {"development", "holdout"})]


def held_v_panel(rows, held):
    """B2e's rule: {(dataset, key, panel label): Cell} for held = [(key, deck_name)]."""
    names = {n: k for k, n in held}
    cells = {(ds, k, p): Cell() for ds, _ in DATASETS for k, _ in held for p in PANEL}
    for r in rows:
        dss = [ds for ds, m in DATASETS if r["split"] in m]
        for side, other in ((1, 2), (2, 1)):
            k = names.get(r[f"deck{side}_name"])
            if k is None or r[f"deck{other}_name"] == r[f"deck{side}_name"]:
                continue
            res, opp = outcome(r, side), r[f"archetype{other}"]
            if opp not in PANEL or res == "BYE":
                continue
            for ds in dss:
                cells[(ds, k, opp)].add(res, r["mode"])
    return cells


def name_v_name(rows, a_name, b_name):
    """Exact deck_name on both sides: {dataset: Cell} from a's side."""
    cells = {ds: Cell() for ds, _ in DATASETS}
    for r in rows:
        dss = [ds for ds, m in DATASETS if r["split"] in m]
        for side, other in ((1, 2), (2, 1)):
            if r[f"deck{side}_name"] == a_name and r[f"deck{other}_name"] == b_name:
                res = outcome(r, side)
                if res != "BYE":
                    for ds in dss:
                        cells[ds].add(res, r["mode"])
    return cells


def panel_v_panel(rows):
    """build_v2.py's rule, for development and pooled: {(dataset, (a, b)): [W, L, T]} for a < b."""
    out = {(ds, k): [0, 0, 0] for ds, _ in DATASETS for k in combinations(TABLE, 2)}
    for r in rows:
        a, b = r["archetype1"], r["archetype2"]
        if a not in PANEL or b not in PANEL or a == b or r["result_status"] not in ("tie", "decisive"):
            continue
        key = tuple(sorted((a, b)))
        idx = 2 if r["result_status"] == "tie" else (0 if (r["winner"] == r["player1"]) == (a == key[0]) else 1)
        for ds, m in DATASETS:
            if r["split"] in m:
                out[(ds, key)][idx] += 1
    return out


def row(ds, cell_set, a, a_name, b, b_name, w, l, t, dl):
    n = w + l + t
    p = (w + 0.5 * t) / n if n else None
    return {"dataset": ds, "cell_set": cell_set, "a": a, "a_deck_name": a_name, "b": b, "b_deck_name": b_name,
            "W": w, "L": l, "T": t, "DL": "" if dl is None else dl, "n": n,
            "score_pct": "" if p is None else f"{100 * p:.2f}",
            "band95_pts": "" if p is None else f"{196 * math.sqrt(p * (1 - p) / n):.2f}"}


def main():
    with open(SRC, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    problems = []
    panel_names = {}
    for r in rows:
        for s in "12":
            if r[f"archetype{s}"] in PANEL:
                panel_names.setdefault(r[f"archetype{s}"], set()).add(r[f"deck{s}_name"])
    if any(len(v) != 1 for v in panel_names.values()) or set(panel_names) != set(PANEL):
        problems.append(f"panel labels are not 1:1 with deck names: {panel_names}")
    pname = {p: next(iter(v)) for p, v in panel_names.items()}
    new_names = {n for _, n, _ in NEW}
    for r in rows:  # the new decks carry no label and one deck id each
        for s in "12":
            if r[f"deck{s}_name"] in new_names and r[f"archetype{s}"]:
                problems.append(f"{r[f'deck{s}_name']} carries label {r[f'archetype{s}']!r}")
                break

    out = []
    # 1. New cells.
    cells = held_v_panel(rows, [(k, n) for k, n, _ in NEW])
    for ds, _ in DATASETS:
        for k, n, role in NEW:
            for p in PANEL:
                c = cells[(ds, k, p)]
                out.append(row(ds, "new_scoreboard" if role == "scoreboard" else "coverage", k, n, p, pname[p],
                               c.W(), c.L(), c.T(), c.DL()))
    rq = name_v_name(rows, "Dragonair Mega Rayquaza ex", "Mega Altaria ex Greninja")
    for ds, _ in DATASETS:
        c = rq[ds]
        out.append(row(ds, "new_scoreboard", "rayquaza", "Dragonair Mega Rayquaza ex", "altaria_greninja",
                       "Mega Altaria ex Greninja", c.W(), c.L(), c.T(), c.DL()))
    # 2. The frozen 28.
    v2 = json.load(open(V2, encoding="utf-8"))["cells"]
    pv = panel_v_panel(rows)
    for (a, b) in combinations(TABLE, 2):
        if pv[("development", (a, b))] != v2[f"{a}|{b}"]:
            problems.append(f"frozen cell {a} v {b}: recomputed development {pv[('development', (a, b))]} "
                            f"!= limitless_v2_dev.json {v2[f'{a}|{b}']}")
        for ds, _ in DATASETS:
            w, l, t = v2[f"{a}|{b}"] if ds == "development" else pv[(ds, (a, b))]
            out.append(row(ds, "frozen28", a, pname[a], b, pname[b], w, l, t, None))
    # 3. Cross-check against B2e's file.
    mine = held_v_panel(rows, B2E)
    n_checked = 0
    with open(B2E_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["opponent"] not in PANEL:
                continue
            c = mine[(r["dataset"], r["archetype"], r["opponent"])]
            if (c.W(), c.L(), c.T(), c.DL(), c.n()) != tuple(int(r[x]) for x in ("W", "L", "T", "DL", "n")):
                problems.append(f"B2e cell {r['dataset']} {r['archetype']} v {r['opponent']} not reproduced")
            n_checked += 1
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for ds in ("development", "pooled"):
        print(f"--- {ds}")
        for r in out:
            if r["dataset"] == ds and r["cell_set"] != "frozen28":
                print(f"  {r['cell_set']:15} {r['a']:17} v {r['b']:17} {r['W']}-{r['L']}-{r['T']} DL {r['DL']} "
                      f"n {r['n']:>4} {r['score_pct']:>6} +/- {r['band95_pts']}")
    print(f"B2e cross-check: {n_checked} cells compared (6 archetypes x 8 x 3 datasets)")
    print(f"frozen 28: development recomputed = limitless_v2_dev.json: "
          f"{'yes' if not any('frozen' in p for p in problems) else 'NO'}")
    if problems:
        print("CELLS FAIL:", *problems[:10], sep="\n  ")
        sys.exit(1)
    print(f"CELLS OK: wrote {OUT} ({len(out)} rows)")


if __name__ == "__main__":
    main()
