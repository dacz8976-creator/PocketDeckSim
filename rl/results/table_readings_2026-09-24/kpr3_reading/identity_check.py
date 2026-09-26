#!/usr/bin/env python3
"""The cloud's identity files for kpr (branch aa87fa3, copied out with git show into <dir>) against the laptop's
reference tables, field by field. Read-only; prints to stdout.  Usage: identity_check.py <dir with the branch copies>"""
import json, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
B = Path(sys.argv[1])
F = ["seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score"]


def load(*paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[(r["a"], r["b"], r["i"])] = r
    return out


ref = {"k3": load(R / "per_game_table_2026-09-25/k3_500.jsonl"),
       "kp3": load(R / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", R / "public_pricing_2026-09-25/kp3_500_rest.jsonl"),
       "kq3": load(R / "kq_2026-09-25/kq3_500.jsonl"),
       # kd3's table is on the cloud branch only (rl/results/kd_2026-09-25/kd3_500.jsonl), copied into <dir> too
       "kd3": load(B / "kd3_500.jsonl") if (B / "kd3_500.jsonl").exists() else None}
for f, bot in (("identity_k3_500.jsonl", "k3"), ("identity_kp3_500.jsonl", "kp3"), ("identity_kq3_500.jsonl", "kq3"),
               ("identity_kd3_40.jsonl", "kd3"), ("table_commit_identity_k3_40.jsonl", "k3"),
               ("table_commit_identity_kp3_40.jsonl", "kp3"), ("table_commit_identity_kq3_40.jsonl", "kq3")):
    new = load(B / f)
    if ref[bot] is None:
        print(f"  {f}: no local {bot} reference table")
        continue
    same = sum(1 for k, r in new.items() if k in ref[bot] and all(r[x] == ref[bot][k][x] for x in F))
    bots = {(r["bot_a"], r["bot_b"]) for r in new.values()}
    print(f"  {f:38} {same:6,} of {len(new):6,} identical to the {bot} table on {', '.join(F)} (bots {sorted(bots)})")
