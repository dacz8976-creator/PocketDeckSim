"""Group the final build's differing floor games by opponent (F v C, the Oct 20 build).

usage: python3 diff_by_opp.py PIECE GAMES_NAME
"""
import json
import sys
from collections import Counter, defaultdict

FIELDS = ["conceded", "could", "dead", "did", "draw", "flagged", "opponent",
          "points", "seat", "seed", "stage2", "turns", "went_first", "won"]

piece, name = sys.argv[1], sys.argv[2]
f_path = f"/home/dacz8976/pincand_work/floor2F/{piece}/{name}"
c_path = f"/home/dacz8976/pincand_work/floor2/{piece}/{name}"


def load(p):
    out = []
    with open(p) as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


f_games, c_games = load(f_path), load(c_path)
assert len(f_games) == len(c_games), (len(f_games), len(c_games))
by_opp_all = Counter(g["opponent"] for g in c_games)
diff_by_opp = Counter()
won_c, won_f = defaultdict(int), defaultdict(int)
fields_changed = Counter()
for i, (f, c) in enumerate(zip(f_games, c_games)):
    assert (f["opponent"], f["seed"], f["seat"]) == (c["opponent"], c["seed"], c["seat"]), i
    won_c[c["opponent"]] += bool(c.get("won"))
    won_f[f["opponent"]] += bool(f.get("won"))
    changed = [k for k in FIELDS if f.get(k) != c.get(k)]
    if changed:
        diff_by_opp[c["opponent"]] += 1
        for k in changed:
            fields_changed[k] += 1
print(f"{piece}: {sum(diff_by_opp.values())} of {len(f_games)} games differ (F v C)")
for opp in sorted(by_opp_all):
    print(f"  {opp:28s} games {by_opp_all[opp]:4d}  differ {diff_by_opp[opp]:3d}  "
          f"wins C {won_c[opp]:4d}  F {won_f[opp]:4d}  ({won_f[opp] - won_c[opp]:+d})")
print("  fields changed:", dict(fields_changed))
