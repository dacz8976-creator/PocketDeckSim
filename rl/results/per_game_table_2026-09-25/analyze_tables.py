#!/usr/bin/env python3
"""Compare per-game table files (legality_scan --games-out) cell by cell against k3 on the same deals and
against Limitless (rl/results/limitless_check_2026-09-23.md, "Rules4, every pairing").

    python3 analyze_tables.py --base k3_500.jsonl --other b3n1_500.jsonl [--other-label b3n1] [--focus hydreigon]

For every pairing in both files: the first-named deck's score for each bot, the paired change (other - base,
deal by deal; 95% range from the per-deal differences), the Limitless score, and how far each bot's cell is
from it. Summary: mean absolute miss and mean squared miss over the shared pairings, for each bot.
`--focus DECK` reports that deck's score (not the first-named deck's) in every line.
This is a plain readout; the adoption rule (ΔMSE bootstrap with vetoes) is scored on the laptop.
"""
import argparse, json, math, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMITLESS_MD = HERE.parents[0] / "limitless_check_2026-09-23.md"


def limitless():
    out = {}
    text = LIMITLESS_MD.read_text(encoding="utf-8").split("### Rules4, every pairing")[1].split("## Part 2")[0]
    for line in text.splitlines():
        m = re.match(r"\|\s*(\w+) v (\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+) ± ([\d.]+)\s*\|", line)
        if m:
            out[(m.group(1), m.group(2))] = (float(m.group(4)), float(m.group(5)))
    return out


def load(path):
    games = {}
    for line in open(path):
        if line.strip():
            g = json.loads(line)
            games[(g["pairing"], g["i"])] = g
    return games


def score_for(g, deck):
    """Score of `deck` in game g: 1 win, 0.5 tie, 0 loss."""
    s = g["first_deck_score"]
    return s if deck == g["a"] else 1 - s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--other", required=True)
    ap.add_argument("--base-label", default="k3")
    ap.add_argument("--other-label", default=None)
    ap.add_argument("--focus", default=None)
    a = ap.parse_args()
    other_label = a.other_label or Path(a.other).stem
    base, other = load(a.base), load(a.other)
    lim = limitless()
    pairings = sorted({p for p, _ in other})
    rows, miss_b, miss_o = [], [], []
    print(f"{'pairing':22} {'deck':10} {a.base_label:>7} {other_label:>9} {'change (95%)':>18} {'Limitless':>10} "
          f"{'miss ' + a.base_label:>9} {'miss ' + other_label:>12}  games")
    for p in pairings:
        keys = sorted(k for k in other if k[0] == p and k in base)
        if not keys:
            continue
        g0 = other[keys[0]]
        deck = a.focus if a.focus in (g0["a"], g0["b"]) else g0["a"]
        sb = [score_for(base[k], deck) for k in keys]
        so = [score_for(other[k], deck) for k in keys]
        d = [y - x for x, y in zip(sb, so)]
        n = len(d)
        mb, mo, md = sum(sb) / n, sum(so) / n, sum(d) / n
        sd = math.sqrt(sum((x - md) ** 2 for x in d) / max(n - 1, 1))
        half = 1.96 * sd / math.sqrt(n)
        same = sum(1 for k in keys if base[k].get("moves") == other[k].get("moves"))
        L = lim.get((g0["a"], g0["b"]))
        Lf = None if L is None else (L[0] if deck == g0["a"] else 100 - L[0])
        mbx = None if Lf is None else 100 * mb - Lf
        mox = None if Lf is None else 100 * mo - Lf
        if Lf is not None:
            miss_b.append(mbx)
            miss_o.append(mox)
        rows.append(dict(pairing=p, a=g0["a"], b=g0["b"], deck=deck, n=n, base=100 * mb, other=100 * mo,
                         change=100 * md, half=100 * half, limitless=Lf, identical_games=same))
        lf = "" if Lf is None else f"{Lf:10.1f} {mbx:+9.1f} {mox:+12.1f}"
        print(f"{p:2} {g0['a'][:9]:>9} v {g0['b'][:9]:9} {deck[:10]:10} {100 * mb:7.1f} {100 * mo:9.1f} "
              f"{100 * md:+8.1f} ({100 * (md - half):+.1f}, {100 * (md + half):+.1f}) {lf}  {n} ({same} identical)")
    if miss_b:
        k = len(miss_b)
        mae = lambda v: sum(abs(x) for x in v) / k  # noqa: E731
        mse = lambda v: sum(x * x for x in v) / k  # noqa: E731
        print(f"\n{k} pairings with a Limitless cell: mean |miss| {a.base_label} {mae(miss_b):.2f}, {other_label} "
              f"{mae(miss_o):.2f}; mean squared miss {a.base_label} {mse(miss_b):.1f}, {other_label} {mse(miss_o):.1f}")
    return rows


if __name__ == "__main__":
    main()
