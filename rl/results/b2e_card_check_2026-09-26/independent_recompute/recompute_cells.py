"""Independent recompute of the B2e Limitless cells.

Written without reading rl/results/b2e_card_check_2026-09-26/cells.py.

Rules (from the task statement / README 'Draw handling'):
  - held side identified by exact deck_name (so unlabeled same-name variants such as
    garchomp-a2 and heliolisk-b1a count); panel side identified by archetype label
    (1:1 with the panel deck_names).
  - 'decisive' (winner == a player id): W or L for the held side.
  - 'tie' (winner == '0'): half a point; counted in T and n.
  - 'double_loss' (winner == '-1'): excluded from W-L-T and n; reported in DL; an
    alternate score_incl_dl_pct treats it as a tie.
  - 'bye_or_automatic_loss': one side empty, so it never forms a held-vs-panel pair.
  - mirrors excluded (impossible here since held and panel sets are disjoint, but checked).
  - every record is one unit (BO1, BO3, BO5 alike); BO1-only numbers reported alongside.
  - score = (W + 0.5 T) / n; band = 1.96 * sqrt(p (1-p) / n) in points; lo/hi clipped to [0, 100].
  - panel_equal_weight: sums over opponents plus the unweighted mean of the per-opponent
    scores over opponents with n > 0 (no band, no BO1 score, no incl-DL score).
  - panel_pooled: sums over opponents, score/band from the sums.
Datasets: development, holdout, pooled (holdout is computed only so that every row of
limitless_cells.csv can be compared; pooled = development + holdout).
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict, OrderedDict

REPO = r"C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim"
MATCHES = os.path.join(REPO, r"rl\results\limitless_skill_model_2026-09-25\matches.csv")
HELD_RECORDS = os.path.join(REPO, r"rl\results\limitless_skill_model_2026-09-25\held_archetype_records.csv")
THEIRS = os.path.join(REPO, r"rl\results\b2e_card_check_2026-09-26\limitless_cells.csv")
SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(SCRATCH, "recomputed_cells.csv")
OUT_DIFF = os.path.join(SCRATCH, "recompute_diff.json")

HELD = OrderedDict([
    ("manectric_heliolisk", "Mega Manectric ex Heliolisk"),
    ("raticate_ninetales", "Team Rocket's Raticate ex Alolan Ninetales ex"),
    ("hoopa_absol", "Hoopa ex Mega Absol ex"),
    ("garchomp", "Garchomp"),
    ("whimsicott_ariados", "Whimsicott ex Ariados"),
    ("charizardy_entei", "Mega Charizard Y ex Entei ex"),
])
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
DATASETS = ["development", "holdout", "pooled"]


def new_cell():
    return {"W": 0, "L": 0, "T": 0, "DL": 0, "W_bo1": 0, "L_bo1": 0, "T_bo1": 0, "DL_bo1": 0}


def add(cell, outcome, bo1):
    cell[outcome] += 1
    if bo1:
        cell[outcome + "_bo1"] += 1


def main():
    rows = list(csv.DictReader(open(MATCHES, encoding="utf-8", newline="")))
    status_counts = defaultdict(int)
    for r in rows:
        status_counts[r["result_status"]] += 1

    # panel label -> deck_name (must be 1:1)
    panel_names = defaultdict(set)
    for r in rows:
        for s in ("1", "2"):
            if r["archetype" + s] in PANEL:
                panel_names[r["archetype" + s]].add(r["deck" + s + "_name"])
    for lab in PANEL:
        assert len(panel_names[lab]) == 1, (lab, panel_names[lab])
    panel_deck_name = {lab: next(iter(panel_names[lab])) for lab in PANEL}

    # cells[dataset][held_key][panel_label] -> counts; also a label-keyed variant for the
    # held_archetype_records.csv verification.
    cells = {ds: {h: {p: new_cell() for p in PANEL} for h in HELD} for ds in DATASETS}
    cells_by_label = {h: {p: new_cell() for p in PANEL} for h in HELD}
    name_to_key = {v: k for k, v in HELD.items()}
    skipped = defaultdict(int)
    variant_ids = defaultdict(int)

    for r in rows:
        st = r["result_status"]
        if st == "bye_or_automatic_loss":
            # one side empty; confirm it can never pair a held deck with a panel label
            assert r["player1"] == "" or r["player2"] == "", r
            skipped["bye"] += 1
            continue
        bo1 = r["mode"] == "BO1"
        split = r["split"]
        assert split in ("development", "holdout"), split
        for hs, ps in (("1", "2"), ("2", "1")):
            hname = r["deck" + hs + "_name"]
            plab = r["archetype" + ps]
            if hname not in name_to_key or plab not in PANEL:
                continue
            hk = name_to_key[hname]
            if r["deck" + hs + "_name"] == r["deck" + ps + "_name"]:
                skipped["mirror"] += 1
                continue
            if r["archetype" + hs] != hk:
                variant_ids[(hname, r["deck" + hs + "_id"], r["archetype" + hs])] += 1
            w = r["winner"]
            if st == "decisive":
                assert w in (r["player1"], r["player2"]) and w != "", r
                outcome = "W" if w == r["player" + hs] else "L"
            elif st == "tie":
                assert w == "0", r
                outcome = "T"
            elif st == "double_loss":
                assert w == "-1", r
                outcome = "DL"
            else:
                raise ValueError(st)
            add(cells[split][hk][plab], outcome, bo1)
            add(cells["pooled"][hk][plab], outcome, bo1)
            if r["archetype" + hs] == hk and split == "development":
                add(cells_by_label[hk][plab], outcome, bo1)

    # ---- verification against held_archetype_records.csv (development only) ----
    held_rec = {}
    for r in csv.DictReader(open(HELD_RECORDS, encoding="utf-8", newline="")):
        held_rec[(r["archetype"], r["opponent"])] = tuple(int(r[k]) for k in ("W", "L", "T", "n"))
    ver = {"by_label": {"match": 0, "diff": []}, "by_deck_name": {"match": 0, "diff": []}}
    for h in HELD:
        for p in PANEL:
            ref = held_rec[(h, p)]
            for mode, c in (("by_label", cells_by_label[h][p]), ("by_deck_name", cells["development"][h][p])):
                mine = (c["W"], c["L"], c["T"], c["W"] + c["L"] + c["T"])
                if mine == ref:
                    ver[mode]["match"] += 1
                else:
                    ver[mode]["diff"].append({"archetype": h, "opponent": p, "scoreboard": ref, "mine": mine})

    # ---- build the output rows ----
    def stats(W, L, T, DL):
        n = W + L + T
        out = {"W": W, "L": L, "T": T, "DL": DL, "n": n}
        if n > 0:
            p = (W + 0.5 * T) / n
            band = 1.96 * math.sqrt(p * (1 - p) / n)
            out["score"] = 100 * p
            out["band"] = 100 * band
            out["lo"] = max(0.0, 100 * (p - band))
            out["hi"] = min(100.0, 100 * (p + band))
        else:
            out["score"] = out["band"] = out["lo"] = out["hi"] = None
        n_dl = n + DL
        out["n_incl_dl"] = n_dl
        out["score_incl_dl"] = 100 * (W + 0.5 * (T + DL)) / n_dl if n_dl > 0 else None
        return out

    def fmt(x, nd=1):
        return "" if x is None else f"{x:.{nd}f}"

    header = ["dataset", "archetype", "deck_name", "opponent", "opponent_deck_name", "W", "L", "T", "DL", "n",
              "score_pct", "band95_pts", "lo_pct", "hi_pct", "W_bo1", "L_bo1", "T_bo1", "DL_bo1", "n_bo1",
              "score_bo1_pct", "band95_bo1_pts", "n_incl_dl", "score_incl_dl_pct"]
    out_rows = []
    for ds in DATASETS:
        for h, hname in HELD.items():
            per_opp = []
            tot = new_cell()
            for p in PANEL:
                c = cells[ds][h][p]
                s = stats(c["W"], c["L"], c["T"], c["DL"])
                s1 = stats(c["W_bo1"], c["L_bo1"], c["T_bo1"], c["DL_bo1"])
                per_opp.append(s)
                for k in tot:
                    tot[k] += c[k]
                out_rows.append([ds, h, hname, p, panel_deck_name[p], c["W"], c["L"], c["T"], c["DL"], s["n"],
                                 fmt(s["score"]), fmt(s["band"]), fmt(s["lo"]), fmt(s["hi"]),
                                 c["W_bo1"], c["L_bo1"], c["T_bo1"], c["DL_bo1"], s1["n"],
                                 fmt(s1["score"]), fmt(s1["band"]), s["n_incl_dl"], fmt(s["score_incl_dl"])])
            # equal weight
            with_n = [s for s in per_opp if s["n"] > 0]
            eq = sum(s["score"] for s in with_n) / len(with_n) if with_n else None
            ts = stats(tot["W"], tot["L"], tot["T"], tot["DL"])
            ts1 = stats(tot["W_bo1"], tot["L_bo1"], tot["T_bo1"], tot["DL_bo1"])
            out_rows.append([ds, h, hname, "panel_equal_weight", f"{len(with_n)} of 8 opponents with n>0",
                             tot["W"], tot["L"], tot["T"], tot["DL"], ts["n"], fmt(eq), "", "", "",
                             tot["W_bo1"], tot["L_bo1"], tot["T_bo1"], tot["DL_bo1"], ts1["n"], "", "",
                             ts["n_incl_dl"], ""])
            out_rows.append([ds, h, hname, "panel_pooled", "all panel matches pooled (match-weighted)",
                             tot["W"], tot["L"], tot["T"], tot["DL"], ts["n"], fmt(ts["score"]), fmt(ts["band"]),
                             fmt(ts["lo"]), fmt(ts["hi"]), tot["W_bo1"], tot["L_bo1"], tot["T_bo1"], tot["DL_bo1"],
                             ts1["n"], fmt(ts1["score"]), fmt(ts1["band"]), ts["n_incl_dl"], fmt(ts["score_incl_dl"])])

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(out_rows)

    # ---- compare with limitless_cells.csv ----
    theirs = list(csv.DictReader(open(THEIRS, encoding="utf-8", newline="")))
    their_cols = list(theirs[0].keys())
    mine_by_key = {(r[0], r[1], r[3]): dict(zip(header, [str(x) for x in r])) for r in out_rows}
    their_by_key = {(r["dataset"], r["archetype"], r["opponent"]): r for r in theirs}
    diffs = []
    if their_cols != header:
        diffs.append(f"column header differs: theirs={their_cols} mine={header}")
    for k in their_by_key:
        if k not in mine_by_key:
            diffs.append(f"row {k} present in limitless_cells.csv but not recomputed")
    for k in mine_by_key:
        if k not in their_by_key:
            diffs.append(f"row {k} recomputed but absent from limitless_cells.csv")
    order_theirs = [(r["dataset"], r["archetype"], r["opponent"]) for r in theirs]
    order_mine = [k for k in mine_by_key]
    if order_theirs != order_mine:
        diffs.append("row order differs (content compared by key regardless)")

    def same(a, b):
        if a == b:
            return True
        try:
            return abs(float(a) - float(b)) < 1e-9
        except ValueError:
            return False

    ncells = 0
    for k, mine in mine_by_key.items():
        th = their_by_key.get(k)
        if th is None:
            continue
        for col in header:
            if col in ("dataset", "archetype", "opponent"):
                continue
            ncells += 1
            a, b = th.get(col, "<missing>"), mine[col]
            if not same(a, b):
                diffs.append(f"{k[0]} / {k[1]} vs {k[2]} / {col}: theirs={a!r} mine={b!r}")

    summary = {
        "matches_rows": len(rows),
        "result_status_counts": dict(status_counts),
        "skipped": dict(skipped),
        "unlabeled_same_name_variants_used": {f"{k[0]} | {k[1]} | label={k[2]!r}": v for k, v in variant_ids.items()},
        "held_archetype_records_verification": {
            "by_label": {"match": ver["by_label"]["match"], "of": 48, "diff": ver["by_label"]["diff"]},
            "by_deck_name": {"match": ver["by_deck_name"]["match"], "of": 48, "diff": ver["by_deck_name"]["diff"]},
        },
        "rows_compared": len(set(mine_by_key) & set(their_by_key)),
        "value_cells_compared": ncells,
        "differences": diffs,
        "agree": not diffs,
        "outputs": {"recomputed_csv": OUT_CSV, "diff_json": OUT_DIFF},
    }
    with open(OUT_DIFF, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
