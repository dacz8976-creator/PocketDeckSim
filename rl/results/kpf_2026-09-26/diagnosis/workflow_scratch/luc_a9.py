import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import two_prop
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
WALL = ("Bonsly", "Hitmonlee")
endA = lambda st: st["end_active"][0] if st["end_active"] else None
cls = lambda n: "main" if n in MAIN else ("wall" if n in WALL else "other")
pat = lambda r: cls(endA(r["ks"])) == "main" and cls(endA(r["bs"])) == "wall"
rev = lambda r: cls(endA(r["ks"])) == "wall" and cls(endA(r["bs"])) == "main"
for opp in sorted({r["opp"] for r in rows}):
    w = [r for r in rows if r["opp"] == opp and r["kind"] == "worse"]
    b = [r for r in rows if r["opp"] == opp and r["kind"] == "better"]
    print(f"{opp:10} main-in-front: worse {sum(map(pat, w)):2}/20 better {sum(map(pat, b)):2}/20 | wall-in-front: worse {sum(map(rev, w)):2} better {sum(map(rev, b)):2}")
# split by what kpf's front Pokemon is
for nm in MAIN:
    a = sum(1 for r in rows if r["kind"] == "worse" and pat(r) and endA(r["ks"]) == nm)
    c = sum(1 for r in rows if r["kind"] == "better" and pat(r) and endA(r["ks"]) == nm)
    print(nm, a, c, "z=%.2f" % two_prop(a, 140, c, 140)[2])
a = sum(1 for r in rows if r["kind"] == "worse" and pat(r) and endA(r["ks"]) != "Riolu")
c = sum(1 for r in rows if r["kind"] == "better" and pat(r) and endA(r["ks"]) != "Riolu")
print("evolved (MLex/Lucario)", a, c, "z=%.2f" % two_prop(a, 140, c, 140)[2])
for k in ("worse", "better"):
    R = [r for r in rows if r["kind"] == k and pat(r)]
    print(k, "pattern seeds:", [ (r["seed"], r["turn"]) for r in R][:12])
    R = [r for r in rows if r["kind"] == k and rev(r)]
    print(k, "reverse seeds:", [ (r["seed"], r["turn"]) for r in R][:12])
# X Speed used by kpf in divergence turn
for k in ("worse", "better"):
    print(k, "kpf X Speed in turn", sum(1 for r in rows if r["kind"] == k and "PLAY P-A 002 X Speed" in r["ks"]["acts"]),
          "kp3", sum(1 for r in rows if r["kind"] == k and "PLAY P-A 002 X Speed" in r["bs"]["acts"]))
