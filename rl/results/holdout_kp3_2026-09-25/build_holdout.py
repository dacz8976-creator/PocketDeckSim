#!/usr/bin/env python3
"""The frozen holdout half's 28 Limitless cells, for the one-time confirmation of kp3 (readings index, rule
pre-registered at 10c4e66). Counted exactly as ../scoreboard_v2_2026-09-25/build_v2.py counts the development half
(analyze.py lines 75-76: panel v panel, different archetypes, decisive or tie; one pairing entry = one match).

    python3 build_holdout.py --check-development    # safe before opening: rebuilds the development cells from
                                                     # matches.csv and checks them against limitless_v2_dev.json
    python3 build_holdout.py --open-holdout          # reads the holdout rows; run once, after Dustin's go-ahead

Writes (with --open-holdout): limitless_holdout.json, limitless_holdout_events.json (the holdout's cells and its
per-event cells) and limitless_pooled.json, limitless_pooled_events.json (development + holdout), all in the shapes
score.py's --limitless and --limitless-events take.
"""
import argparse
import csv
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", "limitless_skill_model_2026-09-25")
V2 = os.path.join(HERE, "..", "scoreboard_v2_2026-09-25")
PANEL = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
RULE = "analyze.py lines 75-76: panel v panel, different archetypes, decisive or tie; one pairing = one match"


def count(split):
    cells = {k: [0, 0, 0] for k in combinations(PANEL, 2)}
    per_event = {}
    with open(os.path.join(SKILL, "matches.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["split"] != split:
                continue
            a, b = r["archetype1"], r["archetype2"]
            if a not in PANEL or b not in PANEL or a == b or r["result_status"] not in ("tie", "decisive"):
                continue
            key = tuple(sorted((a, b)))
            idx = 2 if r["result_status"] == "tie" else (0 if (r["winner"] == r["player1"]) == (a == key[0]) else 1)
            cells[key][idx] += 1
            per_event.setdefault(r["event_id"], {}).setdefault(key, [0, 0, 0])[idx] += 1
    return cells, per_event


def as_json(cells):
    return {f"{a}|{b}": v for (a, b), v in cells.items()}


def events_json(per_event, note):
    return {"rule": RULE, "note": note, "events": [{"event_id": e, "cells": {f"{a}|{b}": v for (a, b), v in sorted(c.items())}}
                                                   for e, c in sorted(per_event.items())]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check-development", action="store_true")
    g.add_argument("--open-holdout", action="store_true")
    a = ap.parse_args()
    dev, dev_ev = count("development")
    ref = json.load(open(os.path.join(V2, "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
    if as_json(dev) != ref:
        raise SystemExit("matches.csv's development rows do not rebuild limitless_v2_dev.json; stop")
    print(f"development check: matches.csv rebuilds the v2 development cells exactly ({sum(map(sum, dev.values()))} "
          f"matches, {len(dev_ev)} events)")
    if a.check_development:
        return
    hold, hold_ev = count("holdout")
    empty = [f"{x} v {y}" for (x, y), v in hold.items() if not sum(v)]
    pooled = {k: [dev[k][j] + hold[k][j] for j in range(3)] for k in dev}
    pooled_ev = {**{f"dev:{e}": c for e, c in dev_ev.items()}, **{f"holdout:{e}": c for e, c in hold_ev.items()}}
    src = "rl/results/limitless_skill_model_2026-09-25/matches.csv"
    for name, obj in (("limitless_holdout.json", {"source": src, "split": "holdout", "rule": RULE, "cells": as_json(hold),
                                                  "events_with_panel_matches": len(hold_ev), "matches": sum(map(sum, hold.values()))}),
                      ("limitless_holdout_events.json", events_json(hold_ev, "holdout half, per event")),
                      ("limitless_pooled.json", {"source": src, "split": "development + holdout", "rule": RULE,
                                                 "cells": as_json(pooled), "events_with_panel_matches": len(pooled_ev),
                                                 "matches": sum(map(sum, pooled.values()))}),
                      ("limitless_pooled_events.json", events_json(pooled_ev, "development + holdout, per event"))):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)
    print(f"holdout: {sum(map(sum, hold.values()))} matches in {len(hold_ev)} events; cells with no match: "
          f"{', '.join(empty) or 'none'}")
    print("Written: limitless_holdout.json, limitless_holdout_events.json, limitless_pooled.json, limitless_pooled_events.json")
    if empty:
        sys.exit(2)


if __name__ == "__main__":
    main()
