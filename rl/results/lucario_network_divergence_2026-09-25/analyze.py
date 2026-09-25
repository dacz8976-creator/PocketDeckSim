#!/usr/bin/env python3
"""B2c step 3: group the positions where the Lucario network and k3 choose differently by card-agnostic
mechanism, and say which choice wins more when k3 plays on.

    python3 analyze.py [--min 20]

Reads decisions.jsonl (net_divergence: every network decision with both moves' kinds and the board, and at each
position where the moves differ, 8 paired play-outs of each move). A position's value is the mean over its paired play-outs of (Lucario score after the
network's move - after k3's move), with k3 piloting both decks afterwards. Groups are pairs of move kinds:
"network: energy to bench / k3: energy to active", "network: play item / k3: end turn", and so on. The 95%
range treats positions as independent (positions from one game are not, so it is a little narrow).
"""
import argparse, json, math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def kind(d):
    k = d["kind"]
    if k == "play":
        return f"play {d['trainer']}"
    if k in ("energy", "tool", "evolve", "ability"):
        return f"{k} to {d['target']}" if k in ("energy", "tool") else f"{k} ({d['target']})"
    if k == "attack":
        return "attack (knocks out)" if d.get("printed_ko") else "attack"
    return k


def stats(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / max(n - 1, 1))
    return n, m, 1.96 * sd / math.sqrt(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=20, help="smallest group to list")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(HERE / "decisions.jsonl")]
    games = len({r["i"] for r in rows})
    n_dec = len(rows)
    same = sum(1 for r in rows if not r["differs"])
    order = sum(1 for r in rows if r["differs"] and r["order_only"])
    rolled = [r for r in rows if "net_minus_k3" in r]
    selfagree = sum(1 for r in rows if r["k3_agrees_with_itself"])
    print(f"{games} games, {n_dec} network decisions: same move as k3 {same} ({100 * same / n_dec:.0f}%), "
          f"differs only in move order {order} ({100 * order / n_dec:.0f}%), differs {len(rolled)} "
          f"({100 * len(rolled) / n_dec:.0f}%). k3 chose the same move under all 3 probe seeds at "
          f"{100 * selfagree / n_dec:.0f}% of decisions.")
    n, m, h = stats([r["net_minus_k3"] for r in rolled])
    print(f"Over the {n} differing positions, the network's move scores {100 * m:+.1f} points (± {100 * h:.1f}) "
          "for Lucario against k3's move, with k3 piloting both decks afterwards.\n")
    groups = defaultdict(list)
    for r in rolled:
        groups[(kind(r["net_detail"]), kind(r["k3_detail"]))].append(r)
    print(f"{'network':26} {'k3':26} {'positions':>9} {'network - k3, points (95%)':>28} {'total/game':>10}")
    for (nk, kk), rs in sorted(groups.items(), key=lambda kv: -sum(r["net_minus_k3"] for r in kv[1])):
        if len(rs) < a.min:
            continue
        n, m, h = stats([r["net_minus_k3"] for r in rs])
        total = 100 * sum(r["net_minus_k3"] for r in rs) / games
        print(f"{nk:26} {kk:26} {n:9} {100 * m:+10.1f} ({100 * (m - h):+.1f}, {100 * (m + h):+.1f}) {total:+10.2f}")
    small = [rs for rs in groups.values() if len(rs) < a.min]
    if small:
        v = [r["net_minus_k3"] for rs in small for r in rs]
        n, m, h = stats(v)
        print(f"{'(smaller groups)':53} {n:9} {100 * m:+10.1f} ({100 * (m - h):+.1f}, {100 * (m + h):+.1f}) "
              f"{100 * sum(v) / games:+10.2f}")
    print("\n'total/game': the group's summed difference per game, in points of Lucario's score; a rough size of "
          "what k3 would gain by making the network's move in that kind of position (gains don't simply add).")
    return rows


if __name__ == "__main__":
    main()
