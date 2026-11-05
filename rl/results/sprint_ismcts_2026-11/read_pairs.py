"""Reads run_pairs.sh output: CAND v km3 against km3 v km3, game by game on the same seed.
  python3 read_pairs.py <out dir> <cand code>
Win share for the first-named deck's pilot (outcome Win == 0); a tie counts a half. Paired difference per game, with its
standard error over games; by deck, by group (fast: 06, 09, 10; setup: 01, 05, 11) and overall."""
import json, os, sys, math
from collections import defaultdict

out, cand = sys.argv[1], sys.argv[2]
FAST, SETUP = ("06", "09", "10"), ("01", "05", "11")

def load(code):
    res = {}
    root = os.path.join(out, f"{code}__km3")
    for tag in sorted(os.listdir(root)):
        p = os.path.join(root, tag)
        if not os.path.isdir(p):
            continue
        for f in os.listdir(p):
            g = json.load(open(os.path.join(p, f)))
            o = g["outcome"]
            score = 1.0 if o == {"Win": 0} else 0.0 if o == {"Win": 1} else 0.5
            res[(tag, g["randomness"]["game_seed"])] = (score, g.get("final_turn"))
    return res

c, b = load(cand), load("km3")
keys = sorted(set(c) & set(b))
def summary(ks):
    if not ks:
        return None
    d = [c[k][0] - b[k][0] for k in ks]
    n = len(d); m = sum(d) / n
    se = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1) / n) if n > 1 else float("nan")
    return n, sum(c[k][0] for k in ks) / n, sum(b[k][0] for k in ks) / n, m, se
def row(name, ks):
    s = summary(ks)
    if s:
        n, cw, bw, m, se = s
        print(f"| {name} | {n} | {100*cw:.1f} | {100*bw:.1f} | {100*m:+.1f} ± {100*1.96*se:.1f} |")
print(f"| rows | games | {cand} wins % | km3 wins % | difference, points (±1.96 SE) |\n|---|---:|---:|---:|---:|")
row("all", keys)
row("fast group (06, 09, 10)", [k for k in keys if k[0][:2] in FAST])
row("setup group (01, 05, 11)", [k for k in keys if k[0][:2] in SETUP])
decks = sorted({k[0].split("__")[0] for k in keys})
for d in decks:
    row(f"deck {d}", [k for k in keys if k[0].split("__")[0] == d])
print(f"\nunpaired: {len(set(c) ^ set(b))} games without a partner")
