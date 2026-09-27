"""Skeptic: does the exposure claim (kpf's front attacker gets hit/KO'd) discriminate worse from better? Also the
direction-of-swap summary and the opponent split test."""
from collections import Counter, defaultdict
from sk_luc_lib import load_cached, z2, binom_split, RIOLU_LINE, WALLS
out, _ = load_cached()
name = lambda p: p["name"] if p else None
endA = lambda r, who: name(r[who]["end"]["active"])
P1 = lambda r: endA(r, "kpf") in RIOLU_LINE and endA(r, "kp3") in WALLS
P6 = lambda r: endA(r, "kpf") in WALLS and endA(r, "kp3") in RIOLU_LINE


def fate(r, who):
    e = r[who]["end"]["active"]
    nb = r[f"{who}_next_start"]
    if nb is None or e is None:
        return None
    a = nb["active"]
    ko = a is None or a["name"] != e["name"] and not any(p["name"] == e["name"] for p in nb["bench"])
    if ko:
        return "KO"
    cur = a if a and a["name"] == e["name"] else next(p for p in nb["bench"] if p["name"] == e["name"])
    return "hit" if cur["hp"] < e["hp"] else "unhurt"


def opp_pts_gain(r, who):
    nb = r[f"{who}_next_start"]
    if nb is None:
        return None
    return None


for lab, pred in (("P1", P1), ("P6", P6)):
    for who in ("kpf", "kp3"):
        c = {k: Counter(fate(r, who) for r in out if r["kind"] == k and pred(r)) for k in ("worse", "better")}
        print(lab, who, "end-Active fate before next own turn:", {k: dict(v) for k, v in c.items()})
        for tag in ("KO",):
            a = c["worse"][tag]; n1 = sum(v for kk, v in c["worse"].items() if kk)
            b = c["better"][tag]; n2 = sum(v for kk, v in c["better"].items() if kk)
            z, p = z2(a, n1, b, n2)
            hw = c["worse"]["KO"] + c["worse"]["hit"]; hb = c["better"]["KO"] + c["better"]["hit"]
            z2_, p2_ = z2(hw, n1, hb, n2)
            print(f"      KO worse {a}/{n1} better {b}/{n2} z={z:+.2f} p={p:.3f} | hit-or-KO worse {hw}/{n1} better {hb}/{n2} z={z2_:+.2f} p={p2_:.3f}")

# direction of the front-line swap
w1 = sum(1 for r in out if r["kind"] == "worse" and P1(r)); w6 = sum(1 for r in out if r["kind"] == "worse" and P6(r))
b1 = sum(1 for r in out if r["kind"] == "better" and P1(r)); b6 = sum(1 for r in out if r["kind"] == "better" and P6(r))
z, p = z2(w1, w1 + w6, b1, b1 + b6)
print(f"swap direction: worse fwd {w1} back {w6}; better fwd {b1} back {b6}; share fwd z={z:+.2f} p={p:.4f}")
# opponent split among P1 games: hard hitters (hydreigon, sceptile, suicune) vs others
hard = {"hydreigon", "sceptile", "suicune"}
hw = sum(1 for r in out if P1(r) and r["kind"] == "worse" and r["opp"] in hard)
hb = sum(1 for r in out if P1(r) and r["kind"] == "better" and r["opp"] in hard)
ow = sum(1 for r in out if P1(r) and r["kind"] == "worse" and r["opp"] not in hard)
ob = sum(1 for r in out if P1(r) and r["kind"] == "better" and r["opp"] not in hard)
z, p = z2(hw, hw + hb, ow, ow + ob)
print(f"P1 worse share: hard-hitters {hw}/{hw+hb}, others {ow}/{ow+ob}; z={z:+.2f} p={p:.3f} (post hoc grouping)")
# kpf end active split by what kpf retreated INTO vs end name
c = defaultdict(Counter)
for r in out:
    if P1(r):
        into = [x["to"] for x in r["kpf"]["retreats"] if x["from"] in WALLS]
        c[r["kind"]][(into[0] if into else "no-retreat", endA(r, "kpf"))] += 1
print({k: dict(v) for k, v in c.items()})
# evolved vs bare
for k in ("worse", "better"):
    ev = sum(1 for r in out if r["kind"] == k and P1(r) and endA(r, "kpf") != "Riolu")
    ba = sum(1 for r in out if r["kind"] == k and P1(r) and endA(r, "kpf") == "Riolu")
    print(k, "P1 evolved in front", ev, "bare Riolu in front", ba)
print("evolved: sign p", binom_split(34, 24), " bare: sign p", binom_split(24, 11))
