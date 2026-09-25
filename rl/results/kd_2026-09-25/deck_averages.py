#!/usr/bin/env python3
"""Deck averages and the fit to Limitless for k3, kp3, kq3 and kd3 on the table deals (i < 500).

    python3 deck_averages.py            # the table below
    python3 deck_averages.py --paired   # each deck's kd3 - kp3 change, deal by deal, with a 95% range

Each deck's score averaged over its seven opponents, for each bot and for Limitless (Sept 23), and each bot's mean
absolute and mean squared miss over the 28 cells. Per-cell detail with paired ranges:
../per_game_table_2026-09-25/analyze_tables.py --base <kp3 or k3 file> --other kd3_500.jsonl.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent
sys.path.insert(0, str(RES / "per_game_table_2026-09-25"))
from analyze_tables import limitless  # noqa: E402

BOTS = {
    "k3": [RES / "per_game_table_2026-09-25/k3_500.jsonl"],
    "kp3": [RES / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", RES / "public_pricing_2026-09-25/kp3_500_rest.jsonl"],
    "kq3": [RES / "kq_2026-09-25/kq3_500.jsonl"],
    "kd3": [HERE / "kd3_500.jsonl"],
}


def cells(paths):
    """(a, b) -> the first-named deck's score, %."""
    sums = {}
    for p in paths:
        for line in open(p):
            if line.strip():
                g = json.loads(line)
                s = sums.setdefault((g["a"], g["b"]), [0.0, 0])
                s[0] += g["first_deck_score"]
                s[1] += 1
    return {k: 100 * v[0] / v[1] for k, v in sums.items()}


def main():
    lim = {k: v[0] for k, v in limitless().items()}
    table = {bot: cells(paths) for bot, paths in BOTS.items()}
    decks = sorted({d for pair in lim for d in pair})
    print(f"{'deck':10} {'Limitless':>9} " + " ".join(f"{b:>6}" for b in BOTS) + "   kd3-kp3")
    for deck in decks:
        def avg(scores):
            vals = [v if a == deck else 100 - v for (a, b), v in scores.items() if deck in (a, b)]
            return sum(vals) / len(vals)
        row = {b: avg(table[b]) for b in BOTS}
        print(f"{deck:10} {avg(lim):9.1f} " + " ".join(f"{row[b]:6.1f}" for b in BOTS) + f"   {row['kd3'] - row['kp3']:+.1f}")
    print()
    for bot in BOTS:
        misses = [table[bot][k] - lim[k] for k in lim]
        print(f"{bot}: mean |miss| {sum(abs(m) for m in misses) / len(misses):.2f}, "
              f"mean squared miss {sum(m * m for m in misses) / len(misses):.1f}")


if __name__ == "__main__" and "--paired" not in sys.argv:
    main()


def paired_deck_change(deck, base="kp3", other="kd3"):
    """The deck's paired change over its seven cells, deal by deal, with a 95% range: (mean, half-width), %."""
    def per_game(paths):
        out = {}
        for p in paths:
            for line in open(p):
                if line.strip():
                    g = json.loads(line)
                    if deck in (g["a"], g["b"]):
                        s = g["first_deck_score"]
                        out[(g["pairing"], g["i"])] = s if g["a"] == deck else 1 - s
        return out
    a, b = per_game(BOTS[base]), per_game(BOTS[other])
    d = [b[k] - a[k] for k in a]
    m = sum(d) / len(d)
    sd = (sum((x - m) ** 2 for x in d) / (len(d) - 1)) ** 0.5
    return 100 * m, 100 * 1.96 * sd / len(d) ** 0.5


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--paired":
    for deck in ("altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"):
        m, h = paired_deck_change(deck)
        print(f"{deck:10} kd3 - kp3 {m:+.1f} ± {h:.1f}")
