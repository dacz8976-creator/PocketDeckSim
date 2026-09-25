#!/usr/bin/env python3
"""Chase Order discards (Vespiquen ex discarding a benched Basic [G] Pokemon for +70), kp3 v kq3, on the table deals.

    python3 tally_chase_order.py

Reads {kp3,kq3}_vespiquen.jsonl (legality_scan at b7c0ace, pairings 5, 11, 16, 20, 23, 25, 27, i < 500). First checks
that every game replays its table game move for move (same fingerprint as ../public_pricing_2026-09-25/kp3_500_*.jsonl
and ../kq_2026-09-25/kq3_500.jsonl), then counts per bot: choices offered, discards, and what was discarded.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent
REF = {
    "kp3": [RES / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", RES / "public_pricing_2026-09-25/kp3_500_rest.jsonl"],
    "kq3": [RES / "kq_2026-09-25/kq3_500.jsonl"],
}


def load(paths):
    games = {}
    for p in paths:
        for line in open(p):
            if line.strip():
                g = json.loads(line)
                games[(g["pairing"], g["i"])] = g
    return games


def main():
    rows = {}
    for bot in ("kp3", "kq3"):
        new = load([HERE / f"{bot}_vespiquen.jsonl"])
        ref = load(REF[bot])
        same = sum(new[k]["moves"] == ref[k]["moves"] for k in new)
        assert same == len(new), f"{bot}: {len(new) - same} games differ from the table"
        offered = discarded = games_offered = 0
        names = Counter()
        per_pairing = {}
        for (p, i), g in sorted(new.items()):
            c = g.get("chase_order")
            if not c:
                continue
            games_offered += 1
            offered += c["offered"]
            discarded += c["discarded"]
            names.update(c["names"])
            pp = per_pairing.setdefault(p, [0, 0, Counter()])
            pp[0] += c["offered"]
            pp[1] += c["discarded"]
            pp[2].update(c["names"])
        rows[bot] = (len(new), games_offered, offered, discarded, names, per_pairing)
        print(f"{bot}: {len(new)} games, all identical to the table's. Chase Order offered in {games_offered} games, "
              f"{offered} choices, {discarded} discards ({100 * discarded / offered:.1f}%): "
              + ", ".join(f"{n} {k} ({100 * k / offered:.1f}% of choices)" for n, k in sorted(names.items())))
    print("\nPer pairing (discards of choices; Combee discards):")
    for p in sorted(rows["kp3"][5]):
        line = f"  pairing {p:2}:"
        for bot in ("kp3", "kq3"):
            o, d, n = rows[bot][5].get(p, [0, 0, Counter()])
            line += f"  {bot} {d}/{o} ({100 * d / max(o, 1):.0f}%), Combee {n['Combee']}"
        print(line)


if __name__ == "__main__":
    main()
