import json, re
from collections import Counter
from vsk_stats import binom_two_sided, fisher_two_sided, test

F = json.load(open("vsk_feat.json"))
ONE = {"Shuckle ex", "Combee"}
MAIN = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def wb(pred, rows=F):
    w = [r for r in rows if r["kind"] == "worse" and pred(r)]
    b = [r for r in rows if r["kind"] == "better" and pred(r)]
    return w, b


def show(label, pred, rows=F, ex=0):
    w, b = wb(pred, rows)
    n = len(w) + len(b)
    print(f"{label:70s} {len(w):3d}/{len(b):3d}  binom p={binom_two_sided(len(w), n):.3f}  fisher p={test(len(w), len(b)):.3f}")
    if ex:
        print("    worse ex:", [r["seed"] for r in w[:ex]], " better ex:", [r["seed"] for r in b[:ex]])
    return w, b


def cls(g):
    a = g["attach"]
    if not a:
        return "none"
    where = a.get("where_end", "?")
    h = g.get("holder_end", a["name"])
    c = "1c" if h in ONE else ("GG" if h in MAIN else h)
    return f"{where}-{c}"


atk = lambda g: g["attack"] is not None
print("== attack at the divergence turn (kp3, kpf)")
for k in [(True, False), (False, True), (True, True), (False, False)]:
    show(f"kp3 attack={k[0]} kpf attack={k[1]}", lambda r, k=k: (atk(r["kp3"]), atk(r["kpf"])) == k)
print("== zone at turn start")
show("zone Some at divergence turn", lambda r: r["kp3"]["zone"] != "None")

print("\n== P1: kp3 attacks, kpf does not, kpf's Zone Energy on Vespiquen ex/Ogerpon ex")
p1 = lambda r: atk(r["kp3"]) and not atk(r["kpf"]) and r["kpf"]["attach"] and r["kpf"].get("holder_end", r["kpf"]["attach"]["name"]) in MAIN
show("P1 (holder at end of turn in MAIN)", p1, ex=8)
show("P1 variant: attach-time name in MAIN", lambda r: atk(r["kp3"]) and not atk(r["kpf"]) and r["kpf"]["attach"] and r["kpf"]["attach"]["name"] in MAIN)
show("P1 variant: holder MAIN or Combee evolving", lambda r: atk(r["kp3"]) and not atk(r["kpf"]) and r["kpf"]["attach"] and (r["kpf"].get("holder_end") in MAIN or r["kpf"]["attach"]["name"] in MAIN))
show("  P1 kpf holder Active at end", lambda r: p1(r) and r["kpf"]["attach"].get("where_end") == "active")
show("  P1 kpf holder Bench at end", lambda r: p1(r) and r["kpf"]["attach"].get("where_end") == "bench")
show("  P1 kpf attach slot 0 at attach time", lambda r: p1(r) and r["kpf"]["attach"]["slot"] == 0)
show("kp3 attacks & kpf not, kpf no attach", lambda r: atk(r["kp3"]) and not atk(r["kpf"]) and not r["kpf"]["attach"])
show("kp3 attacks & kpf not, kpf attach 1-cost", lambda r: atk(r["kp3"]) and not atk(r["kpf"]) and r["kpf"]["attach"] and r["kpf"].get("holder_end") in ONE)

print("\n== Zone table: kp3 class -> kpf class")
tab = Counter((cls(r["kp3"]), cls(r["kpf"]), r["kind"]) for r in F)
keys = sorted({(a, b) for a, b, _ in tab}, key=lambda k: -(tab[(k[0], k[1], 'worse')] + tab[(k[0], k[1], 'better')]))
for k in keys:
    w, b = tab[(k[0], k[1], "worse")], tab[(k[0], k[1], "better")]
    print(f"   {k[0]:12s} -> {k[1]:12s} {w:3d}/{b:3d}  p={test(w, b):.3f}")

print("\n== P2: kp3 attacks with Shuckle ex, Zone on bench MAIN/Shuckle; kpf retreats, feeds MAIN in Active, no attack")
def p2(r):
    k, f = r["kp3"], r["kpf"]
    return (atk(k) and k.get("attacker") == "Shuckle ex" and k["attach"] and k["attach"].get("where_end") == "bench"
            and k.get("holder_end") in MAIN | {"Shuckle ex"} and not atk(f) and f["retreats"] > 0 and f["attach"]
            and f["attach"].get("where_end") == "active" and f.get("holder_end") in MAIN)
w2, b2 = show("P2", p2, ex=10)
show("P2 loose: kp3 Zone ends bench, kpf Zone ends Active on MAIN", lambda r: r["kp3"]["attach"] and r["kpf"]["attach"] and r["kp3"]["attach"].get("where_end") == "bench" and r["kpf"]["attach"].get("where_end") == "active" and r["kpf"].get("holder_end") in MAIN)
show("commit: kp3 Zone ends bench, kpf Zone ends Active (any)", lambda r: r["kp3"]["attach"] and r["kpf"]["attach"] and r["kp3"]["attach"].get("where_end") == "bench" and r["kpf"]["attach"].get("where_end") == "active")
show("reverse: kp3 Zone ends Active, kpf Zone ends bench", lambda r: r["kp3"]["attach"] and r["kpf"]["attach"] and r["kp3"]["attach"].get("where_end") == "active" and r["kpf"]["attach"].get("where_end") == "bench")

print("\n== P3: kp3 feeds a 0-Energy Shuckle ex/Combee in the Active and attacks; kpf feeds MAIN in the Active")
def p3(r):
    k, f = r["kp3"], r["kpf"]
    return (atk(k) and k["attach"] and k["attach"]["slot"] == 0 and k["attach"]["name"] in ONE and k["attach"]["E_before"] == 0
            and f["attach"] and f["attach"].get("where_end") == "active" and f.get("holder_end") in MAIN)
w3, b3 = show("P3", p3, ex=10)
show("P3 and kpf no attack", lambda r: p3(r) and not atk(r["kpf"]))
print("   P2 vs P3 Fisher:", round(fisher_two_sided(len(w2), len(b2), len(w3), len(b3)), 3))

print("\n== P4: no Zone Energy this turn; kpf ends with Shuckle ex Active, kp3 does not")
p4 = lambda r: r["kp3"]["zone"] == "None" and r["kpf"]["end_active"] == "Shuckle ex" and r["kp3"]["end_active"] != "Shuckle ex"
show("P4", p4, ex=8)
show("zone None at divergence turn (all)", lambda r: r["kp3"]["zone"] == "None")
show("zone None & turn 1", lambda r: r["kp3"]["zone"] == "None" and r["turn"] <= 2)

print("\n== P5: Zone turn; kpf ends Combee Active + Reckless Charge; kp3 X Speed + retreat into Shuckle ex + Triple Slap")
p5 = lambda r: (r["kp3"]["zone"] != "None" and r["kpf"]["end_active"] == "Combee" and r["kpf"]["attack"] == "Reckless Charge"
                and r["kp3"]["xspeed"] > 0 and r["kp3"]["retreats"] > 0 and r["kp3"]["attack"] == "Triple Slap")
show("P5", p5, ex=10)
show("P5 loose: kpf Reckless Charge, kp3 Triple Slap", lambda r: r["kpf"]["attack"] == "Reckless Charge" and r["kp3"]["attack"] == "Triple Slap")
show("any kpf Reckless Charge (not in kp3 turn)", lambda r: r["kpf"]["attack"] == "Reckless Charge" and r["kp3"]["attack"] != "Reckless Charge")
show("any kp3 Reckless Charge (not in kpf turn)", lambda r: r["kp3"]["attack"] == "Reckless Charge" and r["kpf"]["attack"] != "Reckless Charge")

print("\n== P7: pure reorder (same multiset of rest-of-turn actions, same end board)")
p7 = lambda r: Counter(r["kp3"]["rest"]) == Counter(r["kpf"]["rest"]) and r["kp3"]["end_board"] == r["kpf"]["end_board"]
show("P7", p7, ex=8)
show("P7 loose: same end board only", lambda r: r["kp3"]["end_board"] == r["kpf"]["end_board"])
show("P7 loose: same multiset only", lambda r: Counter(r["kp3"]["rest"]) == Counter(r["kpf"]["rest"]))

print("\n== P6: both feed a 1-cost Active and attack, differ in more than order")
def p6(r):
    k, f = r["kp3"], r["kpf"]
    return (atk(k) and atk(f) and k["attach"] and f["attach"] and k["attach"]["slot"] == 0 and f["attach"]["slot"] == 0
            and k["attach"]["name"] in ONE and f["attach"]["name"] in ONE and not p7(r))
show("P6", p6, ex=8)
show("P6 minus P5-like Combee", lambda r: p6(r) and not (r["kpf"]["attack"] == "Reckless Charge" and r["kp3"]["attack"] != "Reckless Charge"))
show("Sabrina in either turn", lambda r: r["kp3"]["sabrina"] + r["kpf"]["sabrina"] > 0)
show("Sabrina in exactly one", lambda r: (r["kp3"]["sabrina"] > 0) != (r["kpf"]["sabrina"] > 0))

print("\n== overlaps")
for name, p in (("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4), ("P5", p5), ("P6", p6), ("P7", p7)):
    print(name, "in P1:", sum(1 for r in F if p(r) and p1(r)), " total:", sum(1 for r in F if p(r)))
cov = lambda r: any(p(r) for p in (p1, p4, p5, p6, p7))
show("covered by P1|P4|P5|P6|P7", cov)
