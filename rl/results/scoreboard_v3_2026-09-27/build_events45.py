"""The 45 development cells per tournament event, so every 45-cell reading carries the event-resampled interval beside
the match-level one (Fable and Astra, Sept 28: a standing column, not an analysis on request).
- The 28 table cells per event: scoreboard v2's own file (../scoreboard_v2_2026-09-25/limitless_v2_dev_events.json,
  written by build_v2.py), unchanged.
- The 17 new cells per event: the gauntlet's rule (../gauntlet_runs_2026-09-26/gauntlet_cells.py, whose held_v_panel
  and name_v_name are imported and run on one development event's rows at a time; B2e's Cell counting), from the
  development half only (../limitless_skill_model_2026-09-25/development_matches.csv).
Check: summed over events, every one of the 45 cells equals the development cells score45.py reads (limitless_v2_dev.json
and gauntlet_cells.csv's development rows). Exit 1 otherwise.
Writes limitless_45_dev_events.json beside this script. Usage: python3 build_events45.py"""
import collections, csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RES, "gauntlet_runs_2026-09-26"))
import gauntlet_cells as G  # noqa: E402

v2_events = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev_events.json"), encoding="utf-8"))
v2_cells = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
rows = list(csv.DictReader(open(os.path.join(RES, "limitless_skill_model_2026-09-25", "development_matches.csv"), encoding="utf-8")))
assert {r["split"] for r in rows} == {"development"}, "development rows only"
by_event = collections.defaultdict(list)
for r in rows:
    by_event[r["event_id"]].append(r)
NEWDECKS = [(k, n) for k, n, role in G.NEW if role == "scoreboard"]
new17 = [(k, p) for k, _ in NEWDECKS for p in G.PANEL] + [("rayquaza", "altaria_greninja")]

events = {e["event_id"]: dict(e["cells"]) for e in v2_events["events"]}
G.DATASETS[:] = [("development", {"development"})]
for eid, ers in by_event.items():
    cells = G.held_v_panel(ers, NEWDECKS)
    rq = G.name_v_name(ers, "Dragonair Mega Rayquaza ex", "Mega Altaria ex Greninja")["development"]
    got = {}
    for k, p in new17[:-1]:
        c = cells[("development", k, p)]
        if c.W() + c.L() + c.T():
            got[f"{k}|{p}"] = [c.W(), c.L(), c.T()]
    if rq.W() + rq.L() + rq.T():
        got["rayquaza|altaria_greninja"] = [rq.W(), rq.L(), rq.T()]
    if got:
        events.setdefault(eid, {}).update(got)

# The check against the cells score45.py reads.
target = {k: list(v) for k, v in v2_cells.items()}
for r in csv.DictReader(open(os.path.join(RES, "gauntlet_runs_2026-09-26", "gauntlet_cells.csv"), encoding="utf-8")):
    if r["dataset"] == "development" and r["cell_set"] == "new_scoreboard":
        target[f"{r['a']}|{r['b']}"] = [int(r["W"]), int(r["L"]), int(r["T"])]
assert len(target) == 45, len(target)
total = {k: [0, 0, 0] for k in target}
for cells in events.values():
    for k, v in cells.items():
        if k in total:
            total[k] = [a + b for a, b in zip(total[k], v)]
bad = [k for k in target if total[k] != target[k]]
if bad:
    raise SystemExit(f"per-event cells don't sum to the 45 development cells: {[(k, total[k], target[k]) for k in bad[:5]]}")
out = {"source": "28 cells: limitless_v2_dev_events.json (build_v2.py); 17 new cells: gauntlet_cells.py's rule per development event",
       "rule": "each event's W-L-T per cell; summed over events they equal the 45 development cells exactly (checked)",
       "events": [{"event_id": eid, "cells": cells} for eid, cells in sorted(events.items())]}
json.dump(out, open(os.path.join(HERE, "limitless_45_dev_events.json"), "w", encoding="utf-8"), indent=1)
print(f"wrote limitless_45_dev_events.json: {len(events)} events; all 45 cells sum exactly")
