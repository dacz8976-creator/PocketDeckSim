#!/usr/bin/env python3
"""m64's replay check (SPEC.md section 3), written before any game: each merged slice (replay_a, replay_b, replay_c: games.jsonl) against
the combined run's games on the same keys, content without timing (split_collect.py's content()); and the 4 keys played in both replay_a
and replay_c (deck 10 v t-weezing, deals 0-1) against each other. Prints, per slice and arm, equal / different keys; exit 0 only when every
km3 game is equal and every m64 game is equal outside Will's row (10-xatu-oricorio-tr-weezing v t-weezing); differing m64 games on Will's
row are listed for the revert check. Run from the repository root."""
import json, sys
sys.path.insert(0, "rl/strength")
from split_collect import content

D = "rl/results/m64_on_rules2_2026-10"
SRC = "rl/results/strength_2026-10-08_kx3_combined/games.jsonl"
WILL = ("10-xatu-oricorio-tr-weezing", "t-weezing")


def load(p):
    out = {}
    for l in open(p):
        if l.strip().endswith("}"):
            g = json.loads(l)
            k = (g["deck"], g["opp"], g["deal"], g["seat"], g["arm"])
            assert k not in out, f"{p}: {k} twice"
            out[k] = g
    return out


src = load(SRC)
ok, slices = True, {}
for s in ("a", "b", "c"):
    new = load(f"{D}/replay_{s}/games.jsonl")
    slices[s] = new
    for arm in ("ref", "X"):
        keys = sorted(k for k in new if k[4] == arm)
        diff = [k for k in keys if k not in src or content(new[k]) != content(src[k])]
        will = [k for k in diff if (k[0], k[1]) == WILL]
        other = [k for k in diff if (k[0], k[1]) != WILL]
        name = "km3" if arm == "ref" else "m64"
        print(f"replay_{s} {name}: {len(keys) - len(diff)} of {len(keys)} equal" + (f"; Will's row differs: {will}" if will else "")
              + (f"; OTHER DIFFERENCES: {other}" if other else ""))
        if other or (arm == "ref" and will):
            ok = False
twice = [k for k in slices["a"] if k in slices["c"]]
same = [k for k in twice if content(slices["a"][k]) == content(slices["c"][k])]
print(f"keys played twice (replay_a and replay_c): {len(same)} of {len(twice)} identical")
if len(same) != len(twice) or len(twice) != 8:
    ok = False
print("READING:", "PASS (Will's-row differences, if any, go to the revert check)" if ok else "STOP: see above")
sys.exit(0 if ok else 1)
