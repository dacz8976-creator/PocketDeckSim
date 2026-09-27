import json, math
from collections import Counter

rows = json.load(open("v_rows.json"))
W = [r for r in rows if r["kind"] == "worse"]
B = [r for r in rows if r["kind"] == "better"]


def z(a, n1, b, n2):
    p = (a + b) / (n1 + n2)
    if p in (0, 1):
        return 0.0
    return (a / n1 - b / n2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))


def show(title, key):
    cw, cb = Counter(map(key, W)), Counter(map(key, B))
    print(f"\n== {title}")
    for k in sorted(set(cw) | set(cb), key=lambda k: -(cw[k] + cb[k])):
        print(f"  {str(k):70} worse {cw[k]:3}  better {cb[k]:3}   z={z(cw[k], len(W), cb[k], len(B)):+.2f}")


def zkind(zs):
    return "none" if zs is None else zs[0]


def coarse(d):
    return d.split(" ")[0].split("@")[0].split("->")[0]


show("pure reorder (same multiset of kpf-side actions over the rest of the turn, same end board)",
     lambda r: (r["same_multiset"], r["same_end"]))
show("first decision coarse kp3 -> kpf", lambda r: coarse(r["kp3"]) + " -> " + coarse(r["kpf"]))
show("zone attach target this turn kp3 -> kpf", lambda r: zkind(r["b_zone"]) + " -> " + zkind(r["f_zone"]))
show("attack this turn kp3 -> kpf", lambda r: ("atk" if r["b_attack"] else "no") + " -> " + ("atk" if r["f_attack"] else "no"))
show("retreat this turn kp3 -> kpf", lambda r: (len(r["b_retreat"]) > 0, len(r["f_retreat"]) > 0))
show("end-of-turn Active same?", lambda r: r["b_end_active"] == r["f_end_active"])
show("turn number bucket", lambda r: "t1-2" if r["turn"] <= 2 else ("t3-4" if r["turn"] <= 4 else ("t5-8" if r["turn"] <= 8 else "t9+")))
show("opponent deck", lambda r: r["opp"])
show("X Speed use kp3 -> kpf", lambda r: (r["b_plays"].count("P-A 002 X Speed"), r["f_plays"].count("P-A 002 X Speed")))
show("Sabrina use kp3 -> kpf", lambda r: ("Sabrina" in r["b_plays"], "Sabrina" in r["f_plays"]))
show("Leaf Cape target kp3 -> kpf", lambda r: (tuple(r["b_tools"]), tuple(r["f_tools"])) if r["b_tools"] != r["f_tools"] else "same")
