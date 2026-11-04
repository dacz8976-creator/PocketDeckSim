#!/usr/bin/env python3
"""The re-pin check's comparison (SPEC.md section 4): each game of a replay registration against the development run's game on the
same key, content without timing (split_collect.content), per arm and per row; a changed game's first differing logged decision
(the deck seat's log: turn, action, Active, points, legal-action count; the milliseconds left out) and whether its row is one SPEC.md
section 3 names (rows.json). Run from the repository root:  compare_dev.py REG [REG ...]  (prints; exit 1 when a game changed outside
a named row, or a game is missing or unreadable)."""
import importlib.util, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("split_collect", "rl/strength/split_collect.py")
SC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SC)
DEV = "rl/results/strength_2026-10-03_kx3_dev/games.jsonl"
ROWS = json.load(open(os.path.join(HERE, "rows.json")))  # {"deck|opp": ["C2", ...]} for the rows a change can reach
LOGKEYS = ("t", "o", "a", "act", "b", "n", "p")


def load(path):
    out = {}
    for line in open(path):
        line = line.strip()
        if line.endswith("}"):
            g = json.loads(line)
            out[(g["deck"], g["opp"], g["deal"], g["seat"], g["arm"])] = g
    return out


def first_diff(a, b):
    la, lb = a.get("log") or [], b.get("log") or []
    for i, (x, y) in enumerate(zip(la, lb)):
        if any(x.get(k) != y.get(k) for k in LOGKEYS):
            return f"decision {i}: turn {x.get('t')}: dev {x.get('a')} ({x.get('act')}) v new {y.get('a')} ({y.get('act')})"
    if len(la) != len(lb):
        return f"logs equal for {min(len(la), len(lb))} decisions, then dev has {len(la)} and new {len(lb)}"
    keys = [k for k in a if k not in SC.TIMING and k not in ("log", "moves_deck", "moves_opp") and a.get(k) != b.get(k)]
    return f"logs equal; fields differ: {keys}" if keys else "only the opponent's moves differ (not in the deck seat's log)"


dev = load(DEV)
bad = 0
for reg in sys.argv[1:]:
    new = load(os.path.join(reg, "games.jsonl"))
    man = json.load(open(os.path.join(reg, "manifest.json")))
    expected = man.get("planned_games")
    print(f"=== {reg}: {len(new)} games (planned {expected})")
    if expected is not None and len(new) != expected:
        print(f"  MISSING: {expected - len(new)} games not played")
        bad += 1
    per_arm = defaultdict(Counter)
    changed_rows = defaultdict(list)
    for k, g in sorted(new.items()):
        arm = "kx3" if k[4] == "X" else "km3"
        d = dev.get(k)
        if d is None:
            per_arm[arm]["not in the development run"] += 1
            bad += 1
            continue
        if d["seed"] != g["seed"]:
            per_arm[arm]["seed differs"] += 1
            bad += 1
            continue
        if SC.content(d) == SC.content(g):
            per_arm[arm]["equal"] += 1
        else:
            per_arm[arm]["differ"] += 1
            row = f"{k[0]}|{k[1]}"
            changed_rows[row].append((k, d.get("winner"), g.get("winner"), first_diff(d, g)))
    for arm in ("kx3", "km3"):
        c = per_arm[arm]
        print(f"  {arm}: {sum(c.values())} games; equal {c['equal']}; differ {c['differ']}; not in the development run "
              f"{c['not in the development run']}; seed differs {c['seed differs']}")
    for row, items in sorted(changed_rows.items()):
        named = ROWS.get(row)
        verdict = f"named row ({', '.join(named)})" if named else "NOT A NAMED ROW: a stop"
        if not named:
            bad += 1
        print(f"  changed row {row}: {len(items)} games; {verdict}")
        for k, wd, wn, fd in items:
            print(f"    {k[2]}/{k[3]}/{k[4]}: winner dev {wd} new {wn}; {fd}")
print("RESULT:", "every changed game is in a named row" if bad == 0 else f"{bad} problem(s): see above")
sys.exit(1 if bad else 0)
