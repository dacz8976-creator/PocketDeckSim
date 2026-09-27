import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import two_prop, parse_board
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
WALL = ("Bonsly", "Hitmonlee")
endA = lambda st: st["end_active"][0] if st["end_active"] else None
cls = lambda n: "main" if n in MAIN else ("wall" if n in WALL else "other")


def zone_fate(st):
    """where the turn's Zone Energy ended relative to the end-of-turn Active"""
    if not st["attach"]:
        return "unused"
    side, name = st["attach"]
    # attach target is Active at attach time; did a retreat happen after? approximate: compare names
    if side == "A" and name == endA(st):
        return "Active(end)"
    if side == "A":
        return "Active then left"
    return "Bench"


for lab, key in (("kp3", "bs"), ("kpf", "ks")):
    for kind in ("worse", "better"):
        R = [r for r in rows if r["kind"] == kind and parse_board(r["own"])["zcur"] != "None"]
        print(lab, kind, "zone unused at divergence:", len(R), Counter(zone_fate(r[key]) for r in R))
# the direct test: zone unused at divergence, kpf's first divergent action commits to Active (retreat or attach to Active),
# and the zone does NOT end on kpf's end-of-turn Active
def direct(r):
    if parse_board(r["own"])["zcur"] == "None":
        return False
    return r["kpf_cat"] == "RETREAT" and zone_fate(r["ks"]) != "Active(end)"
def direct_any(r):
    return parse_board(r["own"])["zcur"] != "None" and r["ks"]["retreat"] is not None and zone_fate(r["ks"]) != "Active(end)"
for f, t in ((direct, "kpf's first move is a retreat, zone then NOT on its end Active"), (direct_any, "kpf retreats this turn, zone NOT on its end Active")):
    a = sum(1 for r in rows if r["kind"] == "worse" and f(r)); b = sum(1 for r in rows if r["kind"] == "better" and f(r))
    print(t, a, b, "z=%.2f" % two_prop(a, 140, b, 140)[2])
    print("   worse seeds", [(r["seed"], r["turn"], r["ks"]["retreat"], r["ks"]["attach"]) for r in rows if r["kind"] == "worse" and f(r)][:14])
    print("   better seeds", [(r["seed"], r["turn"], r["ks"]["retreat"], r["ks"]["attach"]) for r in rows if r["kind"] == "better" and f(r)][:14])
