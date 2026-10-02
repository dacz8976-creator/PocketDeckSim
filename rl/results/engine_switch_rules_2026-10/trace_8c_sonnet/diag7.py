#!/usr/bin/env python3
"""A closer look at the games the classifier left UNEXPLAINED: re-traces each one (old and R, one deal at a time), prints the hand-off row's fields,
the first difference with both sides' choices, and for a prefix game how each side ended. Read-only; writes nothing but its output file."""
import csv, gzip, json, subprocess, sys, tempfile
from pathlib import Path

W = Path("/home/dacz8976/c8c")
sys.path.insert(0, str(W / "tools"))
from tightened_rule import load_trace, first_difference  # noqa: E402

GAMES = [("k3", 4, 7), ("k3", 31, 81), ("km3", 1, 399), ("km3", 4, 7), ("km3", 4, 360), ("km3", 21, 310), ("km3", 31, 12)]
rows = {(r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t") if r["step"] == "8"}


def trace(engine, r, deal):
    out = subprocess.run(["nice", "-n", "19", str(W / f"bin_{engine}_vs_trace"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                          "--seed-base", "23100000000", "--pairing", r["pairing"], "--bot", r["bot"], "--deals", str(deal)],
                         cwd=W / engine / "engine", capture_output=True, text=True, check=True).stdout
    p = Path(tempfile.mkdtemp()) / "t.jsonl.gz"
    with gzip.open(p, "wt") as f:
        f.write(out)
    return load_trace(p), out


def short(o, n=700):
    s = json.dumps(o, sort_keys=True, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f"...(+{len(s) - n} chars)"


for key in GAMES:
    r = rows[key]
    bot, pairing, deal = key
    print("=" * 100)
    print(f"{bot} pairing {pairing} deal {deal}: {Path(r['held_file']).stem} v {Path(r['panel_file']).stem}")
    for f in ("old_moves", "new_moves", "differing_fields", "old_winner", "new_winner", "old_points", "new_points", "exact_counters", "superset_counters",
              "vs_confused_choice", "offgate_counters", "no_reach_counter", "full_prevention_only"):
        print(f"  row.{f} = {r[f][:300]}")
    (og, od), _ = trace("old", r, deal)
    (ng, nd), _ = trace("new", r, deal)
    g_old, g_new = og[deal], ng[deal]
    d = first_difference(g_old, g_new)
    print(f"  ticks old {len(g_old)} new {len(g_new)}; done old {short(od[deal], 300)}; done new {short(nd[deal], 300)}")
    print(f"  first_difference: kind={d['kind']} k={d.get('k')} cause={d.get('cause')} detail={d.get('detail')}")
    if d["kind"] == "lookahead":
        k = d["k"]
        x, y = d["x"], d["y"]
        print(f"  tick-record keys: {sorted(x.keys())}")
        print(f"  OLD chose: {x.get('chosen')}")
        print(f"  R   chose: {y.get('chosen')}")
        for name in sorted(set(x) | set(y)):
            if name in ("chosen",):
                continue
            if x.get(name) != y.get(name):
                print(f"  field differs at tick {k}: {name}: old {short(x.get(name), 300)} | new {short(y.get(name), 300)}")
        print(f"  offered (old) {short(x.get('moves'), 600)}")
        for t in range(max(0, k - 2), min(len(g_old), len(g_new), k + 3)):
            print(f"  tick {t}: old chosen {g_old[t].get('chosen')!r:.140} | new chosen {g_new[t].get('chosen')!r:.140}")
    elif d["kind"] == "length":
        shorter, longer, tag = (g_old, g_new, "R") if len(g_old) < len(g_new) else (g_new, g_old, "old")
        print(f"  the {tag} game is the longer one; its extra tick(s):")
        for t in range(len(shorter) - 2, len(longer)):
            print(f"  tick {t}: {short(longer[t], 900)}")
        print(f"  the shorter game's last tick: {short(shorter[-1], 900)}")
