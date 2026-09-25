#!/usr/bin/env python3
"""Vespiquen's seven cells under four pilotings, all on the same table deals (i < 500):
k3 v k3, kp3 v kp3, kp3 Vespiquen v k3 opponent, k3 Vespiquen v kp3 opponent.

    python3 mixed_rows_vespiquen.py

Same readout as ../per_game_table_2026-09-25/mixed_rows.py (Hydreigon, b3n1). Vespiquen's score per cell, and
the paired changes from k3 v k3 (95% ranges from per-deal differences): "Vespiquen's pilot" = kp3 Vespiquen v k3
opponent minus k3 v k3; "the opponent's pilot" = k3 Vespiquen v kp3 opponent minus k3 v k3. Limitless (Sept 23)
is shown for Vespiquen's side of each cell.
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent
sys.path.insert(0, str(RESULTS / "per_game_table_2026-09-25"))
from analyze_tables import limitless  # noqa: E402

DECK = "vespiquen"


def load(*paths):
    games = {}
    for p in paths:
        for line in open(p):
            if line.strip():
                g = json.loads(line)
                games[(g["pairing"], g["i"])] = g
    return games


def score(g):
    s = g["first_deck_score"]
    return s if g["a"] == DECK else 1 - s


def paired(x, y):
    d = [b - a for a, b in zip(x, y)]
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in d) / max(n - 1, 1))
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n)


def main():
    kk = load(RESULTS / "per_game_table_2026-09-25/k3_500.jsonl")
    pp = load(RESULTS / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", RESULTS / "public_pricing_2026-09-25/kp3_500_rest.jsonl")
    vp = load(HERE / "mixed_vesp-kp3_second.jsonl", HERE / "mixed_vesp-kp3_first.jsonl")
    vk = load(HERE / "mixed_vesp-k3_second.jsonl", HERE / "mixed_vesp-k3_first.jsonl")
    for games, want in ((vp, "kp3"), (vk, "k3")):
        for g in games.values():
            bot = g["bot_a"] if g["a"] == DECK else g["bot_b"]
            other = g["bot_b"] if g["a"] == DECK else g["bot_a"]
            assert bot == want and other == ("k3" if want == "kp3" else "kp3"), (g["pairing"], g["i"], bot, other)
    lim = limitless()
    cells = sorted({p for p, _ in vp})
    tot = {k: [] for k in ("kk", "pp", "vp", "vk")}
    print("Vespiquen's score, %, on the table deals i < 500 (paired changes from k3 v k3, 95% range)\n")
    print(f"{'cell':26} {'Limitless':>9} {'k3 v k3':>8} {'kp3 v kp3':>16} {'Vespiquen kp3':>24} {'opponent kp3':>24}")
    for p in cells:
        keys = sorted(k for k in vp if k[0] == p and k in vk and k in kk and k in pp)
        g0 = vp[keys[0]]
        opp = g0["b"] if g0["a"] == DECK else g0["a"]
        L = lim[(g0["a"], g0["b"])][0]
        L = L if g0["a"] == DECK else 100 - L
        v = {n: [score(src[k]) for k in keys] for n, src in (("kk", kk), ("pp", pp), ("vp", vp), ("vk", vk))}
        for n in tot:
            tot[n] += v[n]
        m = lambda x: 100 * sum(x) / len(x)  # noqa: E731
        dp, hp = paired(v["kk"], v["pp"])
        dv, hv = paired(v["kk"], v["vp"])
        do, ho = paired(v["kk"], v["vk"])
        print(f"{p:2} vespiquen v {opp:10} {L:9.1f} {m(v['kk']):8.1f} {m(v['pp']):6.1f} ({dp:+5.1f} ± {hp:3.1f}) "
              f"{m(v['vp']):7.1f} ({dv:+5.1f} ± {hv:3.1f}) {m(v['vk']):7.1f} ({do:+5.1f} ± {ho:3.1f})")
    m = lambda x: 100 * sum(x) / len(x)  # noqa: E731
    dp, hp = paired(tot["kk"], tot["pp"])
    dv, hv = paired(tot["kk"], tot["vp"])
    do, ho = paired(tot["kk"], tot["vk"])
    print(f"\nall 7 cells ({len(tot['kk'])} deals): k3 v k3 {m(tot['kk']):.1f}, kp3 v kp3 {m(tot['pp']):.1f} "
          f"({dp:+.1f} ± {hp:.1f}); Vespiquen's pilot kp3 {m(tot['vp']):.1f} ({dv:+.1f} ± {hv:.1f}); "
          f"the opponent's pilot kp3 {m(tot['vk']):.1f} ({do:+.1f} ± {ho:.1f})")


if __name__ == "__main__":
    main()
