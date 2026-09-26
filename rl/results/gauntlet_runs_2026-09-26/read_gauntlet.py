#!/usr/bin/env python3
"""The gauntlet reading: (a) the new decks against the panel and the 45-cell view, (b) the variation check.
Descriptive only: no adoption, ranking or tuning decision is taken here. Every number is pre-repair (engine 7fc6ccb):
re-run at the repaired engine when it becomes the baseline.

    python3 read_gauntlet.py [--part a|b|all]       the full reading (500 deals), after run_gauntlet_new.sh (a) and
                                                    run_gauntlet_variation.sh (b); writes gauntlet_tables.md and
                                                    gauntlet_summary.json here (--part a or b writes only that part)
    python3 read_gauntlet.py --test                 the same code on the smokes and identity replays in identity/
                                                    (2 and 20 deals); writes identity/reader_test.md and .json.
                                                    Numbers from 2 deals mean nothing; this tests the reader only.
    python3 read_gauntlet.py --dir <folder> --games N   a dry run's files (GAUNTLET_DRY_RUN of the run scripts)

Run (a) plays tsv/new_decks_run.tsv; a deck left out (tsv/not_run.json, with the reason) is reported as "not run".

Refuses to read unless: identity/identity_check.txt ends in GAUNTLET IDENTITY PASS for the B2e scan; every run file
passes gauntlet_checks.check_rows against its TSV (re-run here); in the full reading, STATUS_new.txt (a) or
STATUS_variation.txt (b) ends in a line starting "RUN DONE"; and the frozen 28 cells reproduce scoreboard v2's own
figures (a). A pairing with a RULE finding under a pilot is withheld, and so is every average that needs it.

(a) Definitions (B2e's, ../b2e_rows_2026-09-26/read_b2e.py):
  cell score  = the new (held) deck's (wins + ties/2) / deals x 100; ties = winner_seat -1, counted per cell.
  sim band    = 1.96 sqrt(p(1-p)/n). Limitless cells: gauntlet_cells.csv (gauntlet_cells.py, B2e's cells.py rules),
                development half (the scoreboard's half) and pooled (both halves; B2e's reference). Both are shown.
  miss        = sim - Limitless; "beyond" when |miss| > sqrt(band_L^2 + band_S^2). A Limitless cell at 0% or 100%
                is "no information"; n = 0 is "no games"; a band over 15 points is "wide".
  panel score = equal-weight mean of the 8 cells; +/- 1.96 sqrt(sum p(1-p)/n) / 8. Limitless equal-weight average
                over the opponents with matches, band by panel_bands.py's formula. Gap = panel score - that average.
  kp3 - k3    = paired by deal, the mean over cells of the per-deal differences, +/- from their spread.
  Mega Scizor ex Revavroom is a COVERAGE row: reported, never in an accuracy total (Dustin, Sept 26).
  The 45-cell view: the 28 frozen table cells (k3 ../per_game_table_2026-09-25/k3_500.jsonl, kp3
  ../public_pricing_2026-09-25/kp3_500_*.jsonl, Limitless = scoreboard v2's development cells; pooled beside) and
  the 17 new scoreboard cells (Rayquaza x 8, Altaria/Greninja x 8, Rayquaza v Altaria/Greninja). Per set (28, 27
  without the quarantined Altaria v Sceptile, 17, 45, 44): real error tau = sqrt(mean[(S-L)^2 - SE_L^2 - SE_S^2])
  (score.py), average miss, favourites right, clear ones right, beyond chance, cells over by >10 beyond noise,
  correlation (deep_table.py's definitions). The frozen 28/27 figures must equal scoreboard v2's (kp3_vs_k3_v2.txt).
(b) Definitions:
  version score = the deck's own side's score per deal (first_deck_score, or 1 - it when the version is the second
  named deck), the main list's score on the SAME deal from the reference (table: ../public_pricing_2026-09-25/
  kp3_500_*.jsonl; Charizard Y: ../b2e_rows_2026-09-26/b2e_kp3_arch.jsonl); seeds must match deal by deal.
  version average = mean over its 7 (8 for Charizard Y) opponents; difference = version average - main average =
  mean over opponents of the per-cell mean paired differences; 95% interval 1.96 sqrt(sum_cells var_cell) / K, with
  var_cell the per-deal differences' sample variance / n (stratified, as score.py's side_change).
  RULE, set in advance (Proposal B): a version whose opponent-average difference is 3 points or more (either way)
  puts its deck's second list into the big gauntlet. It reads the opponent average ONLY; per-cell numbers are shown
  for information (a single-Trainer swap is about +/-4 per cell at 500 deals) and never trigger it.
"""
import csv
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(RES, "b2e_rows_2026-09-26"))
sys.dont_write_bytecode = True
import b2e_checks as B  # noqa: E402
import gauntlet_checks as GC  # noqa: E402

LABEL = "pre-repair (engine 7fc6ccb); re-run at the repaired engine when it becomes the baseline"
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
TABLE = sorted(PANEL)
NEW = [("scizor", "Mega Scizor ex Revavroom", "coverage"),
       ("rayquaza", "Dragonair Mega Rayquaza ex", "scoreboard"),
       ("altaria_greninja", "Mega Altaria ex Greninja", "scoreboard")]
NAME = {k: n for k, n, _ in NEW}
QUARANTINE = ("altaria", "sceptile")
WIDE = 15.0
PILOTS = ("k3", "kp3")
REF = {"k3": [os.path.join(RES, "per_game_table_2026-09-25", "k3_500.jsonl")],
       "kp3": [os.path.join(RES, "public_pricing_2026-09-25", f) for f in ("kp3_500_worst5.jsonl", "kp3_500_rest.jsonl")]}
REF_B2E_KP3 = os.path.join(RES, "b2e_rows_2026-09-26", "b2e_kp3_arch.jsonl")
# Scoreboard v2's own figures for the frozen cells (../scoreboard_v2_2026-09-25/kp3_vs_k3_v2.txt): pilot, cells ->
# real error, average miss, favourites right, correlation. The reader must reproduce them.
V2 = {("k3", 28): (10.8, 10.3, 23, 0.64), ("k3", 27): (10.9, 10.4, 22, 0.64),
      ("kp3", 28): (8.4, 9.0, 21, 0.72), ("kp3", 27): (8.6, 9.3, 20, 0.71)}
DECKS_B = ["lucario", "suicune", "weezing", "charizardy"]
VERSIONS = {"lucario": ["v-lucario_2", "v-lucario_swap1", "v-lucario_swap2"],
            "suicune": ["v-suicune_2", "v-suicune_swap1", "v-suicune_swap2"],
            "weezing": ["v-weezing_2", "v-weezing_swap1", "v-weezing_swap2"],
            "charizardy": ["l-charizardy", "v-charizardy_swap1", "v-charizardy_swap2"]}
WHAT = {"v-lucario_2": "second list: 2 Riolu A2 091 and Lucky Ice Pop for 2 Riolu B3 079 and Protective Poncho",
        "v-lucario_swap1": "Lucky Ice Pop for Protective Poncho", "v-lucario_swap2": "Sabrina for Pokémon Center Lady",
        "v-suicune_2": "second list (the most common): 2nd Giant Cape, Mars, 2nd Frigibax B2a 034 for Team Rocket's "
                       "Boss, Field Blower, Frigibax P-B 037",
        "v-suicune_swap1": "2nd Giant Cape for Team Rocket's Boss", "v-suicune_swap2": "Mars for Field Blower",
        "v-weezing_2": "second list (the most common): Mega Absol ex, Pokémon Center Lady, 2 Lucky Ice Pop for "
                       "Darkrai ex, Mars, 2nd Copycat, Field Blower",
        "v-weezing_swap1": "Lucky Ice Pop for Mars", "v-weezing_swap2": "Pokémon Center Lady for the 2nd Copycat",
        "l-charizardy": "second list (l-charizardy.txt): Protective Poncho and 2nd Rainbow Cave for Pokémon Center "
                        "Lady and Lucky Ice Pop",
        "v-charizardy_swap1": "2nd Rainbow Cave for the 2nd Copycat", "v-charizardy_swap2": "Sabrina for Lucky Ice Pop"}
DECK_NAME = {"lucario": "Mega Lucario ex Lucario (t-lucario)", "suicune": "Suicune ex Baxcalibur (t-suicune)",
             "weezing": "Team Rocket's Weezing ex Hoopa ex (t-weezing)",
             "charizardy": "Mega Charizard Y ex Entei ex (h-charizardy_entei)"}
RULE_POINTS = 3.0


def refuse(msg):
    raise SystemExit(f"read_gauntlet.py refuses: {msg}")


def last_line(path):
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    return lines[-1] if lines else ""


def binom(p, n):
    return 100.0 * p, 196.0 * math.sqrt(p * (1 - p) / n)


def fmt(x, signed=False):
    if x is None:
        return "n/a"
    return f"{x:+.1f}" if signed else f"{x:.1f}"


def pm(x, signed=False):
    return "n/a" if x is None else f"{fmt(x['pct'], signed)} +/- {x['band']:.1f}"


def load_cells():
    out = {}
    with open(os.path.join(HERE, "gauntlet_cells.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            w, l, t, n = (int(r[k]) for k in ("W", "L", "T", "n"))
            c = {"W": w, "L": l, "T": t, "n": n, "DL": r["DL"]}
            if n:
                p = (w + 0.5 * t) / n
                c.update(p=p, pct=100 * p, band=196 * math.sqrt(p * (1 - p) / n), one_sided=p in (0.0, 1.0))
                c["wide"] = c["band"] > WIDE
            out[(r["dataset"], r["a"], r["b"])] = c
    return out


def games_by_key(paths, expect_bot=None):
    out = {}
    for path in paths:
        for g in B.load_games(path):
            k = (g["pairing"], g["i"])
            if k in out:
                refuse(f"{path}: pairing {k[0]} deal {k[1]} twice")
            if expect_bot and (g.get("bot_a"), g.get("bot_b")) != (expect_bot, expect_bot):
                refuse(f"{path}: pairing {k[0]} deal {k[1]} bots {g.get('bot_a')}/{g.get('bot_b')}")
            out[k] = g
    return out


def withheld_pairings(findings_by_file):
    return {name: {p for p, c in f.items() if any(k.startswith("RULE") for k in c)} for name, f in findings_by_file.items()}


def cell_stats(scores):
    n = len(scores)
    m = sum(scores) / n
    pct, band = binom(m, n)
    return {"n": n, "W": scores.count(1.0), "T": scores.count(0.5), "L": scores.count(0.0), "p": m, "pct": pct,
            "band": band, "var": m * (1 - m) / n}


def paired(diff_lists):
    """Stratified mean of per-cell mean differences (points) and its 95% half-width."""
    means, var = [], 0.0
    for d in diff_lists:
        n = len(d)
        m = sum(d) / n
        means.append(m)
        var += (sum((x - m) ** 2 for x in d) / max(n - 1, 1)) / n
    return {"pct": 100.0 * sum(means) / len(means), "band": 196.0 * math.sqrt(var) / len(means)}


def pearson(x, y):
    if len(x) < 3:
        return float("nan")
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    return float("nan") if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def metrics(cells):
    """cells: [{"S", "nS", "L", "nL"}] (proportions). score.py's tau and deep_table.py's reported figures."""
    cells = [c for c in cells if c["nL"] > 0]
    k = len(cells)
    acc = sum((c["S"] - c["L"]) ** 2 - c["L"] * (1 - c["L"]) / c["nL"] - c["S"] * (1 - c["S"]) / c["nS"] for c in cells)
    fav = sum(1 for c in cells if (c["S"] - 0.5) * (c["L"] - 0.5) > 0)
    clear = [c for c in cells if abs(c["L"] - 0.5) > 1.96 * math.sqrt(c["L"] * (1 - c["L"]) / c["nL"])]
    beyond, over10 = 0, 0
    for c in cells:
        noise = 1.96 * math.sqrt(c["S"] * (1 - c["S"]) / c["nS"] + c["L"] * (1 - c["L"]) / c["nL"])
        beyond += abs(c["S"] - c["L"]) > noise
        over10 += 100 * (abs(c["S"] - c["L"]) - noise) > 10
    return {"cells": k, "tau": 100 * math.sqrt(max(0.0, acc / k)),
            "average_miss": 100 * sum(abs(c["S"] - c["L"]) for c in cells) / k, "favorite_right": fav,
            "clear": len(clear), "clear_right": sum(1 for c in clear if (c["S"] - 0.5) * (c["L"] - 0.5) > 0),
            "beyond_chance": beyond, "over_10_beyond_noise": over10,
            "correlation": pearson([c["S"] for c in cells], [c["L"] for c in cells])}


# ------------------------------------------------------------------------------------------------ (a)
def read_a(test, md, summary, folder, games):
    # Run (a) plays tsv/new_decks_run.tsv: new_decks.tsv without the decks in tsv/not_run.json (a card deviation that
    # changes play); their pairing numbers stay reserved. The smokes were played from the full new_decks.tsv.
    full_tsv = os.path.join(HERE, "tsv", "new_decks.tsv")
    run_tsv = os.path.join(HERE, "tsv", "new_decks_run.tsv")
    with open(os.path.join(HERE, "tsv", "not_run.json"), encoding="utf-8") as f:
        not_run = json.load(f)
    rows = {int(r["pairing"]): r for r in GC.read_tsv(run_tsv)}
    files = {pl: os.path.join(HERE, "identity", f"smoke_new_{pl}.jsonl") if test else os.path.join(folder, f"new_{pl}.jsonl")
             for pl in PILOTS}
    if not test:
        st = os.path.join(folder, "STATUS_new.txt")
        if not os.path.exists(st) or not last_line(st).startswith("RUN DONE"):
            refuse("STATUS_new.txt does not end in a RUN DONE line (run (a) not finished)")
    log = []
    ok, findings = GC.check_rows([(full_tsv if test else run_tsv, 21_108_000_000, games, pl, files[pl]) for pl in PILOTS],
                                 out=log.append)
    if not ok:
        refuse("the (a) rows check fails: " + log[-1])
    withheld = {pl: withheld_pairings(findings)[os.path.basename(files[pl])] for pl in PILOTS}
    g = {pl: games_by_key([files[pl]], pl) for pl in PILOTS}
    sim = {pl: {p: dict(cell_stats([g[pl][(p, i)]["first_deck_score"] for i in range(games)]),
                        withheld=p in withheld[pl]) for p in rows} for pl in PILOTS}
    L = load_cells()

    def lim_avg(ds, key):
        cs = [L[(ds, key, o)] for o in PANEL if L[(ds, key, o)]["n"] > 0]
        avg = sum(c["pct"] for c in cs) / len(cs)
        band = 196.0 * math.sqrt(sum(c["p"] * (1 - c["p"]) / c["n"] for c in cs)) / len(cs)
        return {"pct": avg, "band": band, "opponents": len(cs)}

    def panel(pl, ps):
        if any(p not in rows or sim[pl][p]["withheld"] for p in ps):
            return None
        cs = [sim[pl][p] for p in ps]
        return {"pct": sum(c["pct"] for c in cs) / len(cs), "band": 196.0 * math.sqrt(sum(c["var"] for c in cs)) / len(cs)}

    def kp3_minus_k3(ps):
        if any(p not in rows or sim[pl][p]["withheld"] for pl in PILOTS for p in ps):
            return None
        return paired([[g["kp3"][(p, i)]["first_deck_score"] - g["k3"][(p, i)]["first_deck_score"] for i in range(games)]
                       for p in ps])

    out = md.append
    out(f"## (a) The new decks against the panel ({LABEL})")
    out("")
    out(f"{games} deals per pairing, both seats, k3 on both sides and kp3 on both sides on the same deals; seeds "
        f"21,108,000,000 + 10,000 x pairing + i. Limitless cells from `gauntlet_cells.csv` (B2e's rules): development "
        "half (the scoreboard's half) and pooled (both halves; B2e's reference). **Mega Scizor ex Revavroom is a "
        "COVERAGE row**: it is reported, never counted in an accuracy total; its real cells hold 0 to 13 matches.")
    out("")
    out("| Deck | Row | k3 panel % | kp3 panel % | kp3 - k3 | Limitless dev % (opp.) | Gap dev k3 | Gap dev kp3 "
        "| Limitless pooled % | Gap pooled k3 | Gap pooled kp3 |")
    out("|---|---|---|---|---|---|---:|---:|---|---:|---:|")
    sa = {"games": games, "decks": {}, "cells_new17": {}, "view45": {}}
    for d, (key, name, role) in enumerate(NEW):
        ps = [8 * d + o for o in range(8)]
        ld, lp = lim_avg("development", key), lim_avg("pooled", key)
        e = {"name": name, "role": role, "limitless_dev": ld, "limitless_pooled": lp, "pilots": {}}
        for pl in PILOTS:
            a = panel(pl, ps)
            e["pilots"][pl] = {"panel": a, "gap_dev": None if a is None else a["pct"] - ld["pct"],
                               "gap_pooled": None if a is None else a["pct"] - lp["pct"]}
        e["kp3_minus_k3"] = kp3_minus_k3(ps)
        e["not_run"] = not_run.get(key)
        sa["decks"][key] = e
        k_, q_ = e["pilots"]["k3"], e["pilots"]["kp3"]
        if key in not_run:
            out(f"| {name} | {'COVERAGE (not accuracy)' if role == 'coverage' else 'scoreboard'} | **not run** | "
                f"**not run** | | {ld['pct']:.1f} +/- {ld['band']:.1f} ({ld['opponents']}) | | "
                f"| {lp['pct']:.1f} +/- {lp['band']:.1f} ({lp['opponents']}) | | |")
            continue
        out(f"| {name} | {'COVERAGE (not accuracy)' if role == 'coverage' else 'scoreboard'} | {pm(k_['panel'])} "
            f"| {pm(q_['panel'])} | {pm(e['kp3_minus_k3'], True)} | {ld['pct']:.1f} +/- {ld['band']:.1f} "
            f"({ld['opponents']}) | {fmt(k_['gap_dev'], True)} | {fmt(q_['gap_dev'], True)} "
            f"| {lp['pct']:.1f} +/- {lp['band']:.1f} ({lp['opponents']}) | {fmt(k_['gap_pooled'], True)} "
            f"| {fmt(q_['gap_pooled'], True)} |")
    out("")
    out("Panel +/- is 95% binomial over the simulator's 8 cells; kp3 - k3 is paired by deal. Limitless averages are "
        "equal-weight over the opponents with matches (band as `panel_bands.py`).")
    for key, why in not_run.items():
        out(f"- **{NAME[key]} was not run:** {why}")
    out("")

    def cell_row(p, key, opp):
        cd, cp = L[("development", key, opp)], L[("pooled", key, opp)]
        cols, beyond = [], []
        for pl in PILOTS:
            if p not in rows:
                cols += ["not run", "", ""]
                continue
            s = sim[pl][p]
            if s["withheld"]:
                cols += ["RULE (withheld)", "n/a", "n/a"]
                beyond.append(f"{pl} withheld")
                continue
            cols.append(f"{s['pct']:.1f} ({s['T']} ties)")
            for c, tag in ((cd, "dev"), (cp, "pooled")):
                if c["n"] == 0:
                    cols.append("no games")
                    continue
                miss = s["pct"] - c["pct"]
                cols.append(f"{miss:+.1f}")
                if c["one_sided"]:
                    beyond.append(f"{pl} {tag}: no information")
                elif abs(miss) > math.hypot(c["band"], s["band"]):
                    beyond.append(f"{pl} {tag}: beyond")
        lim = []
        for c in (cd, cp):
            if c["n"] == 0:
                lim.append("no games")
            else:
                lim.append(f"{c['pct']:.1f} +/- {c['band']:.1f}, {c['W']}-{c['L']}-{c['T']} n {c['n']}"
                           + (" (one-sided)" if c["one_sided"] else "") + (" (wide)" if c["wide"] else ""))
        return lim, cols, beyond

    header = ("| Opponent | Limitless dev (W-L-T, n) | Limitless pooled | k3 % | miss k3 dev | miss k3 pooled | kp3 % "
              "| miss kp3 dev | miss kp3 pooled | beyond the band |")
    for d, (key, name, role) in enumerate(NEW):
        out(f"### {name}: per cell ({'COVERAGE row, not an accuracy claim' if role == 'coverage' else 'scoreboard row'};"
            f" pairings {8 * d} to {8 * d + 7})")
        out("")
        out(header)
        out("|---|---|---|---:|---:|---:|---:|---:|---:|---|")
        for o, opp in enumerate(PANEL):
            p = 8 * d + o
            lim, cols, beyond = cell_row(p, key, opp)
            out(f"| {opp} | {lim[0]} | {lim[1]} | " + " | ".join(cols) + f" | {', '.join(beyond) or 'no'} |")
        out("")
    lim, cols, beyond = cell_row(24, "rayquaza", "altaria_greninja")
    out("### Dragonair Mega Rayquaza ex v Mega Altaria ex Greninja (pairing 24, the 17th new cell; Rayquaza's score)")
    out("")
    out(header)
    out("|---|---|---|---:|---:|---:|---:|---:|---:|---|")
    out(f"| altaria_greninja | {lim[0]} | {lim[1]} | " + " | ".join(cols) + f" | {', '.join(beyond) or 'no'} |")
    out("")

    # The 45-cell view.
    ref = {pl: games_by_key(REF[pl], pl) for pl in PILOTS}
    frozen = {}
    for p, (a, b) in enumerate(itertools.combinations(TABLE, 2)):
        for pl in PILOTS:
            sc = []
            for i in range(500):
                r = ref[pl].get((p, i))
                if r is None or (r["a"], r["b"]) != (a, b) or r["seed"] != 72_000_000 + 10_000 * p + i:
                    refuse(f"frozen reference {pl}: pairing {p} deal {i} missing or not {a} v {b} on the table's seed")
                sc.append(r["first_deck_score"])
            frozen.setdefault((a, b), {})[pl] = cell_stats(sc)
    new17 = [(8 + o, "rayquaza", opp) for o, opp in enumerate(PANEL)] + \
            [(16 + o, "altaria_greninja", opp) for o, opp in enumerate(PANEL)] + [(24, "rayquaza", "altaria_greninja")]
    if any(p not in rows for p, _, _ in new17):
        out("## The 45-cell view: not available (a scoreboard deck was not run; see tsv/not_run.json)")
        out("")
        sa["view45"] = None
        summary["a"] = sa
        return sim, g
    sets = {}
    for ds in ("development", "pooled"):
        for pl in PILOTS:
            fz = [{"key": (a, b), "S": frozen[(a, b)][pl]["p"], "nS": 500, "L": L[(ds, a, b)]["p"],
                   "nL": L[(ds, a, b)]["n"]} for (a, b) in frozen]
            nw = [{"key": (key, opp), "S": sim[pl][p]["p"], "nS": games, "L": L[(ds, key, opp)]["p"],
                   "nL": L[(ds, key, opp)]["n"], "withheld": sim[pl][p]["withheld"]} for p, key, opp in new17]
            nw_ok = None if any(c["withheld"] for c in nw) else nw
            fz27 = [c for c in fz if c["key"] != QUARANTINE]
            sets[(ds, pl)] = {"frozen 28": metrics(fz), "frozen 27 (decision set)": metrics(fz27),
                              "new 17": None if nw_ok is None else metrics(nw_ok),
                              "all 45": None if nw_ok is None else metrics(fz + nw_ok),
                              "all 44 (decision set)": None if nw_ok is None else metrics(fz27 + nw_ok)}
    for (pl, k), (tau, avg, fav, corr) in V2.items():
        m = sets[("development", pl)]["frozen 28" if k == 28 else "frozen 27 (decision set)"]
        got = (round(m["tau"], 1), round(m["average_miss"], 1), m["favorite_right"], round(m["correlation"], 2))
        if got != (tau, avg, fav, corr):
            refuse(f"the frozen {k} cells under {pl} give {got}, scoreboard v2 says {(tau, avg, fav, corr)}")
    out("## The 45-cell view (the accuracy scoreboard: 28 frozen cells + 17 new)")
    out("")
    out("The 28 table cells stay frozen: their simulator numbers are the table's reference games and their Limitless "
        "numbers scoreboard v2's development cells (reproduced here: k3 real error 10.8 on 28 cells and 10.9 on the "
        "27-cell decision set, kp3 8.4 and 8.6, as `kp3_vs_k3_v2.txt`). The 17 new cells are Rayquaza and "
        "Altaria/Greninja against the panel and against each other. Mega Scizor ex Revavroom is not in any set. "
        "Development half = the scoreboard's half; pooled (both halves) beside it, descriptive (the holdout was spent "
        "on Sept 25)." + (" TEST: the new cells rest on 2 deals each, so their numbers mean nothing." if test else ""))
    out("")
    out("| Limitless half | Pilot | Set | Cells | Real error | Average miss | Favourite right | Clear ones right "
        "| Beyond chance | Over by >10 beyond noise | Correlation |")
    out("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for ds in ("development", "pooled"):
        for pl in PILOTS:
            for name, m in sets[(ds, pl)].items():
                if m is None:
                    out(f"| {ds} | {pl} | {name} | withheld (RULE) | | | | | | | |")
                    continue
                out(f"| {ds} | {pl} | {name} | {m['cells']} | {m['tau']:.1f} | {m['average_miss']:.1f} "
                    f"| {m['favorite_right']}/{m['cells']} | {m['clear_right']}/{m['clear']} | {m['beyond_chance']} "
                    f"| {m['over_10_beyond_noise']} | {m['correlation']:.2f} |")
    out("")
    out("### All 45 cells (first-named deck's score; the new deck is first-named in the 17 new cells)")
    out("")
    out("| Cell | Set | k3 % | kp3 % | Limitless dev % (n) | Limitless pooled % (n) | miss dev k3 | miss dev kp3 |")
    out("|---|---|---:|---:|---|---|---:|---:|")
    for (a, b) in frozen:
        cd, cp = L[("development", a, b)], L[("pooled", a, b)]
        s = {pl: frozen[(a, b)][pl]["pct"] for pl in PILOTS}
        out(f"| {a} v {b} | frozen{' (quarantined)' if (a, b) == QUARANTINE else ''} | {s['k3']:.1f} | {s['kp3']:.1f} "
            f"| {cd['pct']:.1f} ({cd['n']}) | {cp['pct']:.1f} ({cp['n']}) | {s['k3'] - cd['pct']:+.1f} "
            f"| {s['kp3'] - cd['pct']:+.1f} |")
    for p, key, opp in new17:
        cd, cp = L[("development", key, opp)], L[("pooled", key, opp)]
        s = {pl: None if sim[pl][p]["withheld"] else sim[pl][p]["pct"] for pl in PILOTS}
        out(f"| {key} v {opp} | new | {fmt(s['k3'])} | {fmt(s['kp3'])} | {cd['pct']:.1f} ({cd['n']}) "
            f"| {cp['pct']:.1f} ({cp['n']}) | {fmt(None if s['k3'] is None else s['k3'] - cd['pct'], True)} "
            f"| {fmt(None if s['kp3'] is None else s['kp3'] - cd['pct'], True)} |")
        sa["cells_new17"][f"{key} v {opp}"] = {"pairing": p, "sim": {pl: sim[pl][p] for pl in PILOTS},
                                               "limitless_dev": cd, "limitless_pooled": cp}
    out("")
    sa["view45"] = {f"{ds}|{pl}": v for (ds, pl), v in sets.items()}
    sa["rows_check"] = log
    sa["withheld"] = {pl: sorted(withheld[pl]) for pl in PILOTS}
    out("### Rows check and legality findings, run (a)")
    out("")
    out("```")
    md.extend(log)
    out("```")
    out("")
    summary["a"] = sa
    return sim, g


# ------------------------------------------------------------------------------------------------ (b)
def main_scores(deck):
    return games_by_key([REF_B2E_KP3] if deck == "charizardy" else REF["kp3"], "kp3")


def compare_version(rows, vg, mg, games):
    """rows: TSV rows by pairing; vg: version games; mg: main games. Per-cell and average paired numbers."""
    cells, diffs = [], []
    for p in sorted(rows):
        r = rows[p]
        side = r["variant_side"]
        vs, ms, d = [], [], []
        for i in range(games):
            v, m = vg.get((p, i)), mg.get((p, i))
            if v is None or m is None:
                refuse(f"pairing {p} deal {i}: missing in the version's or the main list's games")
            if v["seed"] != m["seed"] or v["first_seat"] != m["first_seat"]:
                refuse(f"pairing {p} deal {i}: seed/seat {v['seed']}/{v['first_seat']} v main {m['seed']}/{m['first_seat']}")
            other_v = v["a"] if side == "b" else v["b"]
            other_m = m["a"] if side == "b" else m["b"]
            if other_v != other_m:
                refuse(f"pairing {p}: the opponent is {other_v} in the version's games and {other_m} in the main list's")
            fv = v["first_deck_score"] if side == "a" else 1 - v["first_deck_score"]
            fm = m["first_deck_score"] if side == "a" else 1 - m["first_deck_score"]
            vs.append(fv)
            ms.append(fm)
            d.append(fv - fm)
        cv, cm = cell_stats(vs), cell_stats(ms)
        pc = paired([d])
        cells.append({"pairing": p, "opponent": other_v, "version_pct": cv["pct"], "main_pct": cm["pct"],
                      "diff": pc["pct"], "diff_band": pc["band"], "version_ties": cv["T"], "main_ties": cm["T"]})
        diffs.append(d)
    k = len(cells)
    avg = paired(diffs)
    return {"cells": cells, "opponents": k, "version_avg": sum(c["version_pct"] for c in cells) / k,
            "main_avg": sum(c["main_pct"] for c in cells) / k, "diff": avg["pct"], "diff_band": avg["band"],
            "moves_3": abs(avg["pct"]) >= RULE_POINTS}


def read_b(test, md, summary, folder, games):
    if not test:
        st = os.path.join(folder, "STATUS_variation.txt")
        if not os.path.exists(st) or not last_line(st).startswith("RUN DONE"):
            refuse("STATUS_variation.txt does not end in a RUN DONE line (run (b) not finished)")
    specs, files = [], {}
    for deck in DECKS_B:
        for v in VERSIONS[deck]:
            tsv = os.path.join(HERE, "tsv", f"var_{v}.tsv")
            path = os.path.join(HERE, "identity", f"smoke_var_{v}_kp3.jsonl") if test else os.path.join(folder, f"var_{v}_kp3.jsonl")
            base = 21_106_000_000 if deck == "charizardy" else 72_000_000
            specs.append((tsv, base, games, "kp3", path))
            files[v] = (tsv, path)
    log = []
    ok, findings = GC.check_rows(specs, out=log.append)
    if not ok:
        refuse("the (b) rows check fails: " + log[-1])
    withheld = withheld_pairings(findings)
    out = md.append
    sb = {"games": games, "rule_points": RULE_POINTS, "decks": {}}
    out(f"## (b) The variation check, kp3 ({LABEL})")
    out("")
    out(f"Each version plays its deck's {games} deals per pairing exactly as the main list did (same seeds, same "
        "seats), so every difference is paired deal by deal. **The rule, set in advance (Proposal B): a version whose "
        "average over its opponents (7, or 8 for Charizard Y) moves by 3 points or more puts that deck's second list "
        "into the big gauntlet.** It reads the opponent average only. Per-cell numbers are for information: a "
        "single-Trainer swap is about +/-4 points per cell at 500 deals, so single cells never trigger it.")
    out("")
    out("| Deck | Version | What changes | Version avg % | Main avg % (same deals) | Difference (95%) | 3 points or more? |")
    out("|---|---|---|---:|---:|---:|---|")
    for deck in DECKS_B:
        mg = main_scores(deck)
        e = {"versions": {}}
        for v in VERSIONS[deck]:
            tsv, path = files[v]
            if withheld.get(os.path.basename(path)):
                e["versions"][v] = None
                out(f"| {DECK_NAME[deck]} | {v} | {WHAT[v]} | withheld (RULE) | | | |")
                continue
            rows = {int(r["pairing"]): r for r in GC.read_tsv(tsv)}
            c = compare_version(rows, games_by_key([path], "kp3"), mg, games)
            e["versions"][v] = c
            out(f"| {DECK_NAME[deck]} | {v} | {WHAT[v]} | {c['version_avg']:.1f} | {c['main_avg']:.1f} "
                f"| {c['diff']:+.1f} +/- {c['diff_band']:.1f} | {'**yes**' if c['moves_3'] else 'no'} |")
        e["second_list_joins_big_gauntlet"] = any(c and c["moves_3"] for c in e["versions"].values())
        e["decided_on"] = [v for v, c in e["versions"].items() if c and c["moves_3"]]
        sb["decks"][deck] = e
    out("")
    out("Verdict per deck (the rule above, applied as set):" + (
        " **TEST: 2 deals per pairing; these verdicts only exercise the code and mean nothing.**" if test else ""))
    out("")
    for deck in DECKS_B:
        e = sb["decks"][deck]
        if any(c is None for c in e["versions"].values()):
            out(f"- {DECK_NAME[deck]}: not read (a version is withheld by a RULE finding).")
        elif e["second_list_joins_big_gauntlet"]:
            out(f"- {DECK_NAME[deck]}: **its second list joins the big gauntlet** (Proposal A for this deck): "
                + ", ".join(e["decided_on"]) + " moved 3 points or more.")
        else:
            out(f"- {DECK_NAME[deck]}: one list is enough; no version moved its opponent average by 3 points.")
    out("")
    out("### Per cell, for information only (never read against the 3-point rule)")
    for deck in DECKS_B:
        out("")
        out(f"#### {DECK_NAME[deck]}")
        out("")
        out("| Version | " + " | ".join(f"v {c['opponent']} (p{c['pairing']})"
                                      for c in next(x for x in sb['decks'][deck]['versions'].values() if x)['cells']) + " |")
        n_opp = len(next(x for x in sb["decks"][deck]["versions"].values() if x)["cells"])
        out("|---|" + "---:|" * n_opp)
        first = next(x for x in sb["decks"][deck]["versions"].values() if x)
        out("| main list, % | " + " | ".join(f"{c['main_pct']:.1f}" for c in first["cells"]) + " |")
        for v, c in sb["decks"][deck]["versions"].items():
            if c is None:
                continue
            out(f"| {v}, difference | " + " | ".join(f"{x['diff']:+.1f} +/- {x['diff_band']:.1f}" for x in c["cells"]) + " |")
    out("")
    out("### Rows check and legality findings, run (b)")
    out("")
    out("```")
    md.extend(log)
    out("```")
    out("")
    sb["rows_check"] = log
    summary["b"] = sb


# ------------------------------------------------------------------------------------------------ checks
def smoke_replayed(md, folder):
    """Full reading: the big runs must replay the smokes' games (same seeds) line for line."""
    pairs = [(f"smoke_new_{pl}.jsonl", f"new_{pl}.jsonl") for pl in PILOTS] + \
            [(f"smoke_var_{v}_kp3.jsonl", f"var_{v}_kp3.jsonl") for d in DECKS_B for v in VERSIONS[d]]
    lines = []
    for sm, full in pairs:
        a, b = os.path.join(HERE, "identity", sm), os.path.join(folder, full)
        if not (os.path.exists(a) and os.path.exists(b)):
            continue
        s, _ = B._raw_games(a)
        f, _ = B._raw_games(b)
        bad = [k for k in s if k in f and s[k][0] != f[k][0]]
        if bad:
            refuse(f"{full} does not replay {sm}: first differing (pairing, deal) {bad[0]}")
        both = sum(1 for k in s if k in f)
        lines.append(f"- {full} replays {sm} line for line ({both} games in both"
                     + (f"; {len(s) - both} smoke games are of pairings the run did not play" if both < len(s) else "") + ")")
    if lines:
        md += ["### Determinism: the big runs replay the smokes", ""] + lines + [""]


def zero_difference_test(md, summary):
    """Test mode: the identity replays are the MAIN lists, so as a 'version' each must differ by exactly 0."""
    out = md.append
    out("## Reader test on the identity replays (main list as its own version: every difference must be 0.0)")
    out("")
    res = {}
    for deck, ps in (("lucario", "2,18"), ("suicune", "4,25"), ("weezing", "6,27"), ("charizardy", "40,47")):
        tsv = os.path.join(HERE, "tsv", f"id_{deck}_main.tsv")
        want = {int(x) for x in ps.split(",")}
        rows = {int(r["pairing"]): r for r in GC.read_tsv(tsv) if int(r["pairing"]) in want}
        c = compare_version(rows, games_by_key([os.path.join(HERE, "identity", f"id_{deck}_kp3.jsonl")], "kp3"),
                            main_scores(deck), 20)
        ok = all(x["diff"] == 0 and x["diff_band"] == 0 for x in c["cells"]) and c["diff"] == 0
        res[deck] = {"pairings": ps, "difference": c["diff"], "cells": c["cells"], "ok": ok}
        out(f"- {deck}: pairings {ps} x 20 deals: main list {c['main_avg']:.1f}%, replay {c['version_avg']:.1f}%, "
            f"difference {c['diff']:+.1f} +/- {c['diff_band']:.1f}: {'OK (exactly 0)' if ok else 'NOT ZERO'}")
        if not ok:
            refuse(f"zero-difference test fails for {deck}")
    out("")
    summary["zero_difference_test"] = res


def main():
    test = "--test" in sys.argv
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "all"
    if part not in ("a", "b", "all"):
        refuse("--part must be a, b or all")
    # --dir and --games are for dry runs of the whole flow on scratch copies (the default is this folder, 500 deals).
    folder = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1]) if "--dir" in sys.argv else HERE
    games = 2 if test else (int(sys.argv[sys.argv.index("--games") + 1]) if "--games" in sys.argv else 500)
    idc = os.path.join(HERE, "identity", "identity_check.txt")
    if not os.path.exists(idc) or not last_line(idc).startswith("GAUNTLET IDENTITY PASS "):
        refuse("identity/identity_check.txt does not end in GAUNTLET IDENTITY PASS")
    md, summary = [], {"label": LABEL, "identity": last_line(idc), "test": test}
    title = "Gauntlet reading: READER TEST on the smokes (2 deals) and identity replays" if test else "Gauntlet reading"
    md += [f"# {title} (generated by read_gauntlet.py; descriptive only)", "", f"**{LABEL}.**", "",
           f"- {last_line(idc)}", ""]
    if test:
        md += ["> TEST OUTPUT. Every simulator number below rests on 2 deals per pairing (the smokes) and means "
               "nothing; this file only shows that the reader runs end to end on real scan files.", ""]
        zero_difference_test(md, summary)
    if not test and games != 500:
        md += [f"> DRY RUN: {games} deals per pairing in `{folder}`; not a reading.", ""]
    if part in ("a", "all"):
        read_a(test, md, summary, folder, games)
    if part in ("b", "all"):
        read_b(test, md, summary, folder, games)
    if not test:
        smoke_replayed(md, folder)
    folder = os.path.join(HERE, "identity") if test else folder
    stem = "reader_test" if test else "gauntlet_tables" + ("" if part == "all" else f"_{part}")
    with open(os.path.join(folder, stem + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(folder, (stem if test else stem.replace("tables", "summary")) + ".json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(md))
    print(f"written: {os.path.join(folder, stem + '.md')} and its .json")


if __name__ == "__main__":
    main()
