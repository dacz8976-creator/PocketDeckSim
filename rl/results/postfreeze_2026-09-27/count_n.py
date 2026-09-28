#!/usr/bin/env python3
"""Outcome-blind size count of the post-freeze pull: matches per scoreboard cell (n only; no winner, no W-L-T).
The 28 cells count build_v2.py's matches (two different panel labels, decisive or tie); the 17 new cells count B2e's
records (new deck by exact deck_name v a panel label, or Rayquaza v Altaria/Greninja by name; mirrors and byes out;
ties and decisive only, to stay outcome-blind; B2e's double losses are left out of n there too).
Usage: python3 count_n.py"""
import csv, itertools, pathlib
HERE = pathlib.Path(__file__).resolve().parent
PANEL = sorted(["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"])
NEW = {"Dragonair Mega Rayquaza ex": "rayquaza", "Mega Altaria ex Greninja": "altaria_greninja"}
rows = list(csv.DictReader(open(HERE / "matches.csv", encoding="utf-8")))
n = {k: 0 for k in itertools.combinations(PANEL, 2)}
n.update({(d, p): 0 for d in NEW.values() for p in PANEL}); n[("rayquaza", "altaria_greninja")] = 0
for r in rows:
    if r["result_status"] not in ("tie", "decisive"):
        continue
    a, b = r["archetype1"], r["archetype2"]
    if a in PANEL and b in PANEL and a != b:
        n[tuple(sorted((a, b)))] += 1
        continue
    na, nb = NEW.get(r["deck1_name"]), NEW.get(r["deck2_name"])
    if na and nb and na != nb:
        n[("rayquaza", "altaria_greninja")] += 1
    elif na and b in PANEL:
        n[(na, b)] += 1
    elif nb and a in PANEL:
        n[(nb, a)] += 1
t28 = sum(v for k, v in n.items() if k[0] in PANEL)
t17 = sum(v for k, v in n.items() if k[0] not in PANEL)
print(f"events: {len({r['event_id'] for r in rows})}; pairing rows {len(rows)}")
print(f"the 28 panel cells: {t28} matches (development half: 1,608 from 58 events); cells with n = 0: "
      f"{sum(1 for k, v in n.items() if k[0] in PANEL and v == 0)}")
print(f"the 17 new cells: {t17} matches; cells with n = 0: {sum(1 for k, v in n.items() if k[0] not in PANEL and v == 0)}")
print("per cell n: " + ", ".join(f"{a} v {b} {v}" for (a, b), v in n.items()))
