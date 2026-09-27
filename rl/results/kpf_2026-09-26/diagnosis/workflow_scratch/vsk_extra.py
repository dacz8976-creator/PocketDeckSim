import json
from collections import Counter
from vsk_stats import test, binom_two_sided
F = json.load(open("vsk_feat.json"))
ONE = {"Shuckle ex", "Combee"}
MAIN = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def cls(g):
    a = g["attach"]
    if not a:
        return "none"
    h = g.get("holder_end", a["name"])
    return f"{a.get('where_end')}-" + ("1c" if h in ONE else "GG" if h in MAIN else h)


def show(label, pred):
    w = sum(1 for r in F if r["kind"] == "worse" and pred(r)); b = sum(1 for r in F if r["kind"] == "better" and pred(r))
    print(f"{label:72s} {w:3d}/{b:3d}  fisher p={test(w, b):.3f} binom p={binom_two_sided(w, w + b):.3f}")


c11 = lambda r: (cls(r["kp3"]), cls(r["kpf"])) == ("active-1c", "active-1c")
print("1c->1c by pairing:", sorted(Counter((r["pairing"], r["kind"]) for r in F if c11(r)).items()))
print("1c->1c by turn:", sorted(Counter((r["turn"], r["kind"]) for r in F if c11(r)).items()))
print("all by turn:", sorted(Counter((min(r["turn"], 6), r["kind"]) for r in F).items()))
show("1c->1c", c11)
same_ms = lambda r: Counter(r["kp3"]["rest"]) == Counter(r["kpf"]["rest"])
show("1c->1c excluding pure reorders", lambda r: c11(r) and not same_ms(r))
show("kp3 X Speed, kpf none (div turn)", lambda r: r["kp3"]["xspeed"] > 0 and r["kpf"]["xspeed"] == 0)
show("kpf X Speed, kp3 none (div turn)", lambda r: r["kpf"]["xspeed"] > 0 and r["kp3"]["xspeed"] == 0)
show("kpf ends with Combee Active, kp3 not", lambda r: r["kpf"]["end_active"] == "Combee" and r["kp3"]["end_active"] != "Combee")
show("kp3 ends with Combee Active, kpf not", lambda r: r["kp3"]["end_active"] == "Combee" and r["kpf"]["end_active"] != "Combee")
show("kpf ends Shuckle Active, kp3 not", lambda r: r["kpf"]["end_active"] == "Shuckle ex" and r["kp3"]["end_active"] != "Shuckle ex")
show("kp3 ends Shuckle Active, kpf not", lambda r: r["kp3"]["end_active"] == "Shuckle ex" and r["kpf"]["end_active"] != "Shuckle ex")
show("kpf ends MAIN Active, kp3 not", lambda r: r["kpf"]["end_active"] in MAIN and r["kp3"]["end_active"] not in MAIN)
show("kp3 ends MAIN Active, kpf not", lambda r: r["kp3"]["end_active"] in MAIN and r["kpf"]["end_active"] not in MAIN)
show("same end Active name", lambda r: r["kp3"]["end_active"] == r["kpf"]["end_active"])
show("divergence turn <= 2", lambda r: r["turn"] <= 2)
show("divergence turn >= 5", lambda r: r["turn"] >= 5)
show("both attack, same attack", lambda r: r["kp3"]["attack"] and r["kp3"]["attack"] == r["kpf"]["attack"])
show("both attack, same attack, not pure reorder", lambda r: r["kp3"]["attack"] and r["kp3"]["attack"] == r["kpf"]["attack"] and not same_ms(r))
show("kp3 Sabrina, kpf not", lambda r: r["kp3"]["sabrina"] > 0 and r["kpf"]["sabrina"] == 0)
show("kpf Sabrina, kp3 not", lambda r: r["kpf"]["sabrina"] > 0 and r["kp3"]["sabrina"] == 0)
