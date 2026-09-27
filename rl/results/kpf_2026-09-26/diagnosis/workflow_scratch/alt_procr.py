"""'One short' Active at the start of an own turn: where does the Zone go, and does it attack? kpf vs kp3 traces,
from the divergence turn on (altaria)."""
import json, sys
from collections import Counter, defaultdict
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import *

recs, base, kpf = load_all("altaria")
COST = {"Espeon": 1, "Mega Altaria ex": 2, "Darkrai": 3}


def turns(game, seat, from_turn):
    """yield (turn, start_side, zone_target_side, attacked, attack_name) for each own turn >= from_turn"""
    by = defaultdict(list)
    for ln in game:
        if ln["actor"] == seat and ln["tomove"] == seat:
            by[ln["turn"]].append(ln)
    for t in sorted(by):
        if t < from_turn:
            continue
        lns = by[t]
        start = parse_side(lns[0]["raw"][seat])
        zone, atk = None, None
        for ln in lns:
            c = cat(ln["act"])
            if c.startswith("ATTACH") and "is_turn_energy: true" in ln["act"]:
                zone = "A" if c == "ATTACH->ACTIVE" else "B"
            if c.startswith("ATTACK"):
                atk = c[7:]
        yield t, start, zone, atk


agg = defaultdict(Counter)
for r in recs:
    gb, gk = base[r["seed"]][0], kpf[r["seed"]][0]
    seat = r["kpf_seat"]
    k = next(n for n in range(min(len(gb), len(gk))) if gb[n]["act"] != gk[n]["act"])
    t0 = gb[k]["turn"]
    for name, g in (("kp3", gb), ("kpf", gk)):
        for t, start, zone, atk in turns(g, seat, t0):
            a = start["active"]
            if not a or start["zc"] == "None":
                continue
            need = COST.get(a["name"])
            if need is None:
                continue
            short = need - len(a["e"])
            if short != 1:
                continue
            key = (r["kind"], name)
            agg[key]["turns"] += 1
            agg[key]["zone->" + str(zone)] += 1
            agg[key]["attacked" if atk else "no attack"] += 1
            if zone == "B" and not atk:
                agg[key]["BENCH & NO ATTACK"] += 1
            agg[key]["active:" + a["name"]] += 1
            if zone == "B" and not atk:
                agg[key]["idle:" + a["name"]] += 1

for kind in ("worse", "better"):
    for name in ("kp3", "kpf"):
        c = agg[(kind, name)]
        n = c["turns"]
        print(f"{kind:6} {name}: one-short Active own turns n={n:4}  zone->A {c['zone->A']:3} ({c['zone->A']/max(n,1):.0%})  "
              f"zone->B {c['zone->B']:3} ({c['zone->B']/max(n,1):.0%})  attacked {c['attacked']:3} ({c['attacked']/max(n,1):.0%})  "
              f"Bench&no-attack {c['BENCH & NO ATTACK']:3} ({c['BENCH & NO ATTACK']/max(n,1):.0%})")
        print("         ", {k: v for k, v in c.items() if k.startswith(("active:", "idle:"))})
