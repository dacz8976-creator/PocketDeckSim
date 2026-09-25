#!/usr/bin/env python3
"""Hydreigon's seven cells under four pilotings, all on the same table deals (i < 500):
k3 v k3, b3n1 v b3n1, b3n1 Hydreigon v k3 opponent, k3 Hydreigon v b3n1 opponent.

    python3 mixed_rows.py

Hydreigon's score per cell, and the paired changes from k3 v k3 (95% ranges from per-deal differences):
"Hydreigon's pilot" = b3n1 Hydreigon v k3 opponent minus k3 v k3; "the opponent's pilot" = k3 Hydreigon v
b3n1 opponent minus k3 v k3. If b3n1's gain in these cells came from Hydreigon playing better, the first
carries it; if from the opponents playing worse, the second does.
"""
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = "hydreigon"


def load(*names):
    games = {}
    for n in names:
        for line in open(HERE / n):
            if line.strip():
                g = json.loads(line)
                games[(g["pairing"], g["i"])] = g
    return games


def hyd(g):
    s = g["first_deck_score"]
    return s if g["a"] == DECK else 1 - s


def paired(x, y):
    d = [b - a for a, b in zip(x, y)]
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in d) / max(n - 1, 1))
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n)


def main():
    kk = load("k3_500.jsonl")
    bb = load("b3n1_500.jsonl")
    hb = load("mixed_hyd-b3n1_first.jsonl", "mixed_hyd-b3n1_second.jsonl")
    hk = load("mixed_hyd-k3_first.jsonl", "mixed_hyd-k3_second.jsonl")
    for games, want in ((hb, "b3n1"), (hk, "k3")):
        for g in games.values():
            bot = g["bot_a"] if g["a"] == DECK else g["bot_b"]
            assert bot == want, (g, want)
    cells = sorted({p for p, _ in hb})
    tot = {k: [] for k in ("kk", "bb", "hb", "hk")}
    print(f"Hydreigon's score, %, on the table deals i < 500 (paired changes from k3 v k3, 95% range)\n")
    print(f"{'cell':24} {'k3 v k3':>8} {'b3n1 v b3n1':>12} {'Hydreigon b3n1':>26} {'opponent b3n1':>26}")
    for p in cells:
        keys = sorted(k for k in hb if k[0] == p and k in hk and k in kk and k in bb)
        g0 = hb[keys[0]]
        opp = g0["b"] if g0["a"] == DECK else g0["a"]
        v = {name: [hyd(src[k]) for k in keys] for name, src in (("kk", kk), ("bb", bb), ("hb", hb), ("hk", hk))}
        for name in tot:
            tot[name] += v[name]
        dh, hh = paired(v["kk"], v["hb"])
        do, ho = paired(v["kk"], v["hk"])
        db, hbb = paired(v["kk"], v["bb"])
        m = lambda x: 100 * sum(x) / len(x)  # noqa: E731
        print(f"{p:2} hydreigon v {opp:10} {m(v['kk']):8.1f} {m(v['bb']):6.1f} ({db:+5.1f}) "
              f"{m(v['hb']):8.1f} ({dh:+5.1f} ± {hh:4.1f}) {m(v['hk']):8.1f} ({do:+5.1f} ± {ho:4.1f})")
    dh, hh = paired(tot["kk"], tot["hb"])
    do, ho = paired(tot["kk"], tot["hk"])
    db, hbb = paired(tot["kk"], tot["bb"])
    m = lambda x: 100 * sum(x) / len(x)  # noqa: E731
    print(f"\nall 7 cells ({len(tot['kk'])} deals): k3 v k3 {m(tot['kk']):.1f}, b3n1 v b3n1 {m(tot['bb']):.1f} "
          f"({db:+.1f} ± {hbb:.1f}); Hydreigon's pilot b3n1 {m(tot['hb']):.1f} ({dh:+.1f} ± {hh:.1f}); "
          f"the opponent's pilot b3n1 {m(tot['hk']):.1f} ({do:+.1f} ± {ho:.1f})")


if __name__ == "__main__":
    main()
