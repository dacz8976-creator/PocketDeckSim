"""End-of-decision-turn Active under each bot (altaria), worse vs better."""
import json, sys
from collections import Counter
from math import comb
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import *

recs, base, kpf = load_all("altaria")
T = {json.loads(l)["seed"]: json.loads(l) for l in open(HERE + "/workflow_scratch/altaria_games.jsonl")}


def bp(k, n):
    if n == 0:
        return 1.0
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def end_side(game, seat, t0):
    for ln in game:
        if ln["turn"] > t0:
            return parse_side(ln["raw"][seat])
    return None


rows = []
for r in recs:
    g = T[r["seed"]]
    if not g["own_turn"]:
        continue
    seat, t0 = r["kpf_seat"], g["t0"]
    eb, ek = end_side(base[r["seed"]][0], seat, t0), end_side(kpf[r["seed"]][0], seat, t0)
    if not eb or not ek or not eb["active"] or not ek["active"]:
        continue
    rows.append(dict(kind=r["kind"], seed=r["seed"], b=eb["active"], k=ek["active"], batk=g["base"][0]["attack"],
                     katk=g["kpf"][0]["attack"]))

print("n", len(rows))
c = Counter()
for x in rows:
    c[(x["b"]["name"], x["k"]["name"], x["kind"])] += 1
pairs = sorted({(a, b) for a, b, _ in c}, key=lambda p: -(c[p + ("worse",)] + c[p + ("better",)]))
print("(kp3 end Active, kpf end Active): worse better")
for p in pairs:
    w, b = c[p + ("worse",)], c[p + ("better",)]
    if w + b >= 3:
        print(f"   {str(p):45} {w:3} {b:3}  p={bp(w, w + b):.3f}")

PRE = {"Swablu", "Eevee"}
def show(label, pred):
    w = sum(1 for x in rows if pred(x) and x["kind"] == "worse"); b = sum(1 for x in rows if pred(x) and x["kind"] == "better")
    print(f"  {label:90} worse {w:3} better {b:3} p={bp(w, w + b):.3f}")

print()
show("different end Active", lambda x: x["b"]["name"] != x["k"]["name"])
show("kp3 ends with Igglybuff Active, kpf with something else", lambda x: x["b"]["name"] == "Igglybuff" and x["k"]["name"] != "Igglybuff")
show("kpf ends with an energy-holding unevolved Swablu/Eevee Active; kp3 doesn't",
     lambda x: x["k"]["name"] in PRE and len(x["k"]["e"]) >= 1 and not (x["b"]["name"] in PRE and len(x["b"]["e"]) >= 1))
show("kp3 ends with an energy-holding unevolved Swablu/Eevee Active; kpf doesn't",
     lambda x: x["b"]["name"] in PRE and len(x["b"]["e"]) >= 1 and not (x["k"]["name"] in PRE and len(x["k"]["e"]) >= 1))
show("kpf end Active holds more Energy than kp3's end Active",
     lambda x: len(x["k"]["e"]) > len(x["b"]["e"]))
show("kpf end Active holds less Energy than kp3's end Active",
     lambda x: len(x["k"]["e"]) < len(x["b"]["e"]))
show("kpf ends with Espeon/Mega Altaria Active, kp3 not",
     lambda x: x["k"]["name"] in ("Espeon", "Mega Altaria ex") and x["b"]["name"] not in ("Espeon", "Mega Altaria ex"))
show("kp3 ends with Espeon/Mega Altaria Active, kpf not",
     lambda x: x["b"]["name"] in ("Espeon", "Mega Altaria ex") and x["k"]["name"] not in ("Espeon", "Mega Altaria ex"))
print("\n seeds kp3 Igglybuff / kpf other:", [(x["seed"], x["kind"][0], x["k"]["name"], x["batk"], x["katk"]) for x in rows
                                            if x["b"]["name"] == "Igglybuff" and x["k"]["name"] != "Igglybuff"])
