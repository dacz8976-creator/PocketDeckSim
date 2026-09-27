import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
WALL = ("Bonsly", "Hitmonlee")
endA = lambda st: st["end_active"][0] if st["end_active"] else None
cls = lambda n: "main" if n in MAIN else ("wall" if n in WALL else "other")
pat = lambda r: cls(endA(r["ks"])) == "main" and cls(endA(r["bs"])) == "wall"


def hit(r, lab):
    g = games[r["seed"]]
    seat = r["seat"]
    mv, st = (g["base"], r["bs"]) if lab == "kp3" else (g["kpf"], r["ks"])
    n = st["end_n"]
    while n < len(mv) and not (mv[n]["actor"] == seat and mv[n]["tomove"] == seat and mv[n]["turn"] > r["turn"]):
        n += 1
    if n >= len(mv):
        return "gameover"
    a = parse_board(mv[n]["s"][seat])["active"]
    ea = st["end_active"]
    if a is None or a["name"] != ea[0]:
        return "KO"
    return "hit" if a["hp"] < ea[2] else "clean"


for kind in ("worse", "better"):
    R = [r for r in rows if r["kind"] == kind and pat(r)]
    print(kind, len(R), "kpf's main-line Active:", Counter(hit(r, "kpf") for r in R), " kp3's wall:", Counter(hit(r, "kp3") for r in R))
# points outcome: final points of lucario side in pattern games
for kind in ("worse", "better"):
    R = [r for r in rows if r["kind"] == kind and pat(r)]
    print(kind, "final own points kp3 vs kpf avg", sum(r["res_b"][0] for r in R) / len(R), sum(r["res_k"][0] for r in R) / len(R))
