import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
WALL = ("Bonsly", "Hitmonlee")


def endA(st):
    return st["end_active"][0] if st["end_active"] else None


def cls(n):
    return "main" if n in MAIN else ("wall" if n in WALL else "other")


pat = lambda r: cls(endA(r["ks"])) == "main" and cls(endA(r["bs"])) == "wall"
for kind in ("worse", "better"):
    R = [r for r in rows if r["kind"] == kind and pat(r)]
    print(kind, len(R))
    print("  kpf end Active:", Counter(endA(r["ks"]) for r in R))
    print("  kpf end Active energy count:", Counter(len(r["ks"]["end_active"][1]) for r in R))
    print("  kp3 end Active:", Counter(endA(r["bs"]) for r in R))
    print("  kp3 attack:", Counter((r["bs"]["attack"] or ["none"])[0] for r in R))
    print("  kpf attack:", Counter((r["ks"]["attack"] or ["none"])[0] for r in R))
    print("  kp3 zone:", Counter(tuple(r["bs"]["attach"]) if r["bs"]["attach"] else None for r in R))
    print("  kpf zone:", Counter(tuple(r["ks"]["attach"]) if r["ks"]["attach"] else None for r in R))
    # what happened during the opponent's following turn: our Active at our next turn start
    outc = Counter()
    for r in R:
        g = games[r["seed"]]
        seat = r["seat"]
        res = []
        for lab, mv, st in (("kp3", g["base"], r["bs"]), ("kpf", g["kpf"], r["ks"])):
            n = st["end_n"]
            # find our next own move
            while n < len(mv) and not (mv[n]["actor"] == seat and mv[n]["tomove"] == seat and mv[n]["turn"] > r["turn"]):
                n += 1
            if n >= len(mv):
                res.append("gameover")
                continue
            b = parse_board(mv[n]["s"][seat])
            o = parse_board(mv[n]["s"][1 - seat])
            ea = st["end_active"]
            a = b["active"]
            if a is None:
                res.append("noactive")
            elif a["name"] != ea[0]:
                res.append(f"{ea[0]} gone(P opp {o['P']})")
            else:
                res.append(f"{ea[0]} dmg {ea[2]-a['hp']}")
        outc[tuple(res)] += 1
    for k, v in outc.most_common(25):
        print("   ", v, k)
