"""Vespiquen: classify each game's divergence turn (kp3 vs kpf on the same board) into turn-level plans, and test
Dustin's hypothesis (where the turn's Zone Energy ends up, and who is Active)."""
import json, math, re
from collections import Counter, defaultdict
from v_lib import game_pairs, first_div, parse_side, cat

COST = {"Vespiquen ex": 2, "Teal Mask Ogerpon ex": 2, "Shuckle ex": 1, "Combee": 1}
GG = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def window(tr, k):
    T = tr[k]["turn"]
    s = k
    while s > 0 and tr[s - 1]["turn"] == T:
        s -= 1
    e = k
    while e + 1 < len(tr) and tr[e + 1]["turn"] == T:
        e += 1
    return s, e


def plan(tr, k, seat):
    """The rest of the turn from tick k for `seat`: zone attach (slot-tracked to the end of the turn), attack, retreats."""
    s, e = window(tr, k)
    zone_slot, zone_name, attack, attacker, retreats, evolves = None, None, None, None, [], []
    for n in range(s, e + 1):
        t = tr[n]
        if t["actor"] != seat:
            continue
        a = t["act"]
        c = cat(a)
        side = parse_side(t["s"][seat])
        if c.startswith("ATTACH") and "is_turn_energy: true" in a:
            idx = int(re.search(r"\(\d+, \w+, (\d+)\)", a).group(1))
            zone_slot = idx
            if idx == 0:
                zone_name = side["active"]["name"]
            else:
                nxt = parse_side(tr[n + 1]["s"][seat]) if n + 1 < len(tr) else None
                zone_name = "?"
                if nxt:
                    for i, m in enumerate(nxt["bench"]):
                        if i < len(side["bench"]) and len(m["e"]) > len(side["bench"][i]["e"]):
                            zone_name = m["name"]
        elif c == "RETREAT":
            kk = int(re.search(r"Retreat\((\d+)\)", a).group(1))
            nxt = parse_side(tr[n + 1]["s"][seat]) if n + 1 < len(tr) else None
            retreats.append((side["active"]["name"], nxt["active"]["name"] if nxt and nxt["active"] else "?", n >= k))
            if zone_slot is not None:
                zone_slot = kk if zone_slot == 0 else (0 if zone_slot == kk else zone_slot)
        elif c.startswith("ATTACK"):
            attack = c[7:]
            attacker = side["active"]["name"] if side["active"] else "?"
        elif c == "EVOLVE":
            evolves.append(a)
    end = parse_side(tr[e]["s"][seat])
    ea = end["active"]
    return {"zone": None if zone_slot is None else ("A" if zone_slot == 0 else "B"), "zone_name": zone_name,
            "attack": attack, "attacker": attacker, "retreats": retreats,
            "end_active": ea["name"] if ea else None, "end_e": len(ea["e"]) if ea else 0,
            "end_ready": bool(ea) and len(ea["e"]) >= COST.get(ea["name"], 9),
            "P": end["P"], "own_turn": tr[k]["tomove"] == seat}


def classify(b, f):
    if not b["own_turn"]:
        return "0 promotion/choice on the opponent's turn"
    if b["attack"] and not f["attack"]:
        if f["end_active"] in GG and f["zone"] == "A":
            return "1 kp3 attacks; kpf skips it, powers a GG attacker in the Active"
        if f["zone"] == "B":
            return "2 kp3 attacks; kpf skips it, powers the Bench"
        return "3 kp3 attacks; kpf skips it, other"
    if f["attack"] and not b["attack"]:
        return "4 kpf attacks, kp3 doesn't"
    if b["attack"] and f["attack"]:
        if (b["attack"], b["attacker"]) != (f["attack"], f["attacker"]):
            return "5 both attack, different attacker"
        return "6 both attack, same attacker (trainers/order/tool/bench differ)"
    if b["end_active"] != f["end_active"]:
        return "7 neither attacks, different Active at end of turn"
    if b["zone"] != f["zone"]:
        return "8 neither attacks, same Active, Zone Energy placed differently"
    return "9 neither attacks, same Active and Zone target (trainers/order/tool/bench differ)"


def binom_p(k, n):
    """two-sided exact binomial p for k of n at 0.5"""
    from math import comb
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(p for p in pk if p <= obs + 1e-12))


rows = []
for g, bt, ft, seat, nb, nf in game_pairs():
    k = first_div(bt, ft)
    b, f = plan(bt, k, seat), plan(ft, k, seat)
    rows.append({"seed": g["seed"], "kind": g["kind"], "turn": bt[k]["turn"], "opp": g["a"] if g["b"] == "vespiquen" else g["b"],
                 "cls": classify(b, f), "b": b, "f": f,
                 "own": bt[k]["s"][seat], "oppb": bt[k]["s"][1 - seat]})
json.dump(rows, open("v_cls.json", "w"))

print("== turn-level class at the first divergence (worse / better; exact binomial p of worse share vs 1/2)")
cw, cb = Counter(r["cls"] for r in rows if r["kind"] == "worse"), Counter(r["cls"] for r in rows if r["kind"] == "better")
for c in sorted(set(cw) | set(cb)):
    n = cw[c] + cb[c]
    print(f"  {c:75} {cw[c]:3} / {cb[c]:3}   worse share {cw[c]/n:.2f}  p={binom_p(cw[c], n):.3f}")

print("\n== Dustin's hypothesis, own-turn divergences only: where the turn's Zone Energy ends (kp3 -> kpf)")
own = [r for r in rows if r["b"]["own_turn"]]
def zlab(p):
    if p["zone"] is None:
        return "none"
    return p["zone"] + (":GG" if p["zone_name"] in GG else ":1E")
cw = Counter((zlab(r["b"]), zlab(r["f"])) for r in own if r["kind"] == "worse")
cb = Counter((zlab(r["b"]), zlab(r["f"])) for r in own if r["kind"] == "better")
for c in sorted(set(cw) | set(cb), key=lambda c: -(cw[c] + cb[c])):
    n = cw[c] + cb[c]
    print(f"  {str(c):40} {cw[c]:3} / {cb[c]:3}   p={binom_p(cw[c], n):.3f}")

print("\n== committed to the Active (attacked, or Zone Energy ends on the Active) vs built (Zone Energy ends on the Bench, no attack)")
def commit(p):
    if p["attack"]:
        return "attack"
    if p["zone"] == "A":
        return "attach-Active"
    if p["zone"] == "B":
        return "attach-Bench"
    return "no attach"
cw = Counter((commit(r["b"]), commit(r["f"])) for r in own if r["kind"] == "worse")
cb = Counter((commit(r["b"]), commit(r["f"])) for r in own if r["kind"] == "better")
for c in sorted(set(cw) | set(cb), key=lambda c: -(cw[c] + cb[c])):
    n = cw[c] + cb[c]
    print(f"  {str(c):40} {cw[c]:3} / {cb[c]:3}   p={binom_p(cw[c], n):.3f}")

print("\n== end-of-turn Active (kp3 -> kpf), own-turn divergences where it differs")
cw = Counter((r["b"]["end_active"], r["f"]["end_active"]) for r in own if r["kind"] == "worse" and r["b"]["end_active"] != r["f"]["end_active"])
cb = Counter((r["b"]["end_active"], r["f"]["end_active"]) for r in own if r["kind"] == "better" and r["b"]["end_active"] != r["f"]["end_active"])
for c in sorted(set(cw) | set(cb), key=lambda c: -(cw[c] + cb[c])):
    n = cw[c] + cb[c]
    print(f"  {str(c):55} {cw[c]:3} / {cb[c]:3}   p={binom_p(cw[c], n):.3f}")

print("\n== points taken this turn (end P) kp3 vs kpf")
cw = Counter((r["b"]["P"] > r["f"]["P"]) - (r["b"]["P"] < r["f"]["P"]) for r in own if r["kind"] == "worse")
cb = Counter((r["b"]["P"] > r["f"]["P"]) - (r["b"]["P"] < r["f"]["P"]) for r in own if r["kind"] == "better")
print("  kp3 more / equal / kpf more  worse:", cw[1], cw[0], cw[-1], " better:", cb[1], cb[0], cb[-1])

print("\n== class by turn bucket (worse/better)")
for lo, hi in ((1, 2), (3, 4), (5, 99)):
    sub = [r for r in rows if lo <= r["turn"] <= hi]
    c2 = defaultdict(lambda: [0, 0])
    for r in sub:
        c2[r["cls"][:1]][0 if r["kind"] == "worse" else 1] += 1
    print(f"  t{lo}-{hi}: " + "  ".join(f"{c}:{v[0]}/{v[1]}" for c, v in sorted(c2.items())))
