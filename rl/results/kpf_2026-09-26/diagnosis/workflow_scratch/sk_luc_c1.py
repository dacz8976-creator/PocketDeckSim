"""Skeptic: recount the analyst's patterns from the independent records."""
from collections import Counter, defaultdict
from sk_luc_lib import load_cached, z2, binom_split, RIOLU_LINE, WALLS
out, _ = load_cached()
W = [r for r in out if r["kind"] == "worse"]
Bt = [r for r in out if r["kind"] == "better"]
NW, NB = len(W), len(Bt)


def name(p):
    return p["name"] if p else None


def report(label, pred, pool=None, show=0):
    w = [r for r in (pool[0] if pool else W) if pred(r)]
    b = [r for r in (pool[1] if pool else Bt) if pred(r)]
    nw = len(pool[0]) if pool else NW
    nb = len(pool[1]) if pool else NB
    z, p = z2(len(w), nw, len(b), nb)
    print(f"{label:78} worse {len(w):3}/{nw}  better {len(b):3}/{nb}  z={z:+.2f} p={p:.3f}  sign-test p={binom_split(len(w), len(b)):.3f}")
    if show:
        print("     worse seeds:", [r["seed"] for r in w][:show])
        print("     better seeds:", [r["seed"] for r in b][:show])
    return w, b


endA = lambda r, who: name(r[who]["end"]["active"])
# P1
p1 = lambda r: endA(r, "kpf") in RIOLU_LINE and endA(r, "kp3") in WALLS
w1, b1 = report("P1 kpf end Active Riolu-line, kp3 end Active wall", p1, show=10)
# P1 by opponent
byo = defaultdict(lambda: [0, 0])
for r in w1:
    byo[r["opp"]][0] += 1
for r in b1:
    byo[r["opp"]][1] += 1
print("   by opponent:", dict(byo))
byp = defaultdict(lambda: [0, 0])
for r in w1:
    byp[endA(r, "kpf")][0] += 1
for r in b1:
    byp[endA(r, "kpf")][1] += 1
print("   by kpf end Active:", dict(byp))


def hit(r):
    """kpf's end-of-turn Active: hit or knocked out before kpf's next turn."""
    e = r["kpf"]["end"]["active"]
    nb = r["kpf_next_start"]
    if nb is None:
        return None
    a = nb["active"]
    if a is None or a["name"] != e["name"]:
        # replaced: KO (or switched by the opponent) - check bench for it
        still = [p for p in nb["bench"] if p["name"] == e["name"] and p["hp"] is not None]
        if still:
            return still[0]["hp"] < e["hp"]
        return True
    return a["hp"] < e["hp"]


hw = [hit(r) for r in w1]
hb = [hit(r) for r in b1]
a, n1 = sum(1 for x in hw if x), sum(1 for x in hw if x is not None)
b, n2 = sum(1 for x in hb if x), sum(1 for x in hb if x is not None)
z, p = z2(a, n1, b, n2)
print(f"   P1 kpf's exposed Active hit/KO'd before next own turn: worse {a}/{n1}  better {b}/{n2}  z={z:+.2f} p={p:.3f}")


# P2: kpf retreats wall -> Bonsly/Hitmonlee into Riolu/Mega (from k on), kp3 doesn't
def wall_to_riolu(f, targets=("Riolu", "Mega Lucario ex")):
    return any(x["from"] in WALLS and x["to"] in targets for x in f["retreats"])


report("P2 kpf retreats wall into Riolu/Mega this turn, kp3 doesn't",
       lambda r: wall_to_riolu(r["kpf"]) and not wall_to_riolu(r["kp3"]), show=8)
report("P2 (any Riolu-line target) kpf retreats wall into Riolu line, kp3 doesn't",
       lambda r: wall_to_riolu(r["kpf"], tuple(RIOLU_LINE)) and not wall_to_riolu(r["kp3"], tuple(RIOLU_LINE)))
report("P2 kp3 makes that retreat", lambda r: wall_to_riolu(r["kp3"]))
report("P2 kpf's raw first differing move is RETREAT", lambda r: r["kpf_cat"] == "RETREAT")
report("P2 kp3's raw first differing move is RETREAT", lambda r: r["kp3_cat"] == "RETREAT")
report("P2 kpf plays X Speed in the turn (from k), kp3 doesn't",
       lambda r: any("X Speed" in c for c in r["kpf"]["plays"]) and not any("X Speed" in c for c in r["kp3"]["plays"]), show=8)

# P3
teary = lambda f: "ATTACK Teary Attack" in f["attacks"]
report("P3 kp3 uses Teary Attack in the turn, kpf doesn't", lambda r: teary(r["kp3"]) and not teary(r["kpf"]), show=6)
report("P3 kp3 attacks, kpf doesn't", lambda r: r["kp3"]["attacks"] and not r["kpf"]["attacks"])
report("P3 kpf attacks, kp3 doesn't", lambda r: r["kpf"]["attacks"] and not r["kp3"]["attacks"])
report("P3 Bonsly is Active at divergence", lambda r: name(r["div_board"]["active"]) == "Bonsly")
report("    Hitmonlee is Active at divergence", lambda r: name(r["div_board"]["active"]) == "Hitmonlee")
report("    Riolu line is Active at divergence", lambda r: name(r["div_board"]["active"]) in RIOLU_LINE)


# P4 zone destination, games with zone unused at divergence (own turn)
def zcat(f):
    z = f["zone"]
    if z is None:
        return "none"
    if z["pos"] == 0:
        return "endActive"
    if z["slot"] == 0:
        return "active_then_retreated"
    return "bench"


unused = lambda r: r["div_in_own_turn"] and r["div_board"]["zone"].startswith("Some")
UW = [r for r in W if unused(r)]
UB = [r for r in Bt if unused(r)]
print(f"\nzone unused at divergence: worse {len(UW)}, better {len(UB)}")
for who in ("kp3", "kpf"):
    cw, cb = Counter(zcat(r[who]) for r in UW), Counter(zcat(r[who]) for r in UB)
    print(f"   {who} zone destination worse {dict(cw)}  better {dict(cb)}")
report("P4 kpf zone on end Active, kp3's elsewhere", lambda r: zcat(r["kpf"]) == "endActive" and zcat(r["kp3"]) != "endActive",
       pool=(UW, UB), show=6)
report("P4 reverse: kp3 zone on end Active, kpf's elsewhere", lambda r: zcat(r["kp3"]) == "endActive" and zcat(r["kpf"]) != "endActive",
       pool=(UW, UB))
report("P4b kpf zone to Riolu-line end Active, kp3 zone to benched Riolu line",
       lambda r: zcat(r["kpf"]) == "endActive" and endA(r, "kpf") in RIOLU_LINE and zcat(r["kp3"]) == "bench"
       and r["kp3"]["zone"]["target"] in RIOLU_LINE, pool=(UW, UB))


# P5 Dustin's exact failure
def p5(r, strict_kp3=True):
    if not unused(r):
        return False
    if r["kpf_cat"] != "RETREAT":
        return False
    rt = r["kpf"]["retreats"]
    if not rt or rt[0]["n"] != r["k"] or rt[0]["from"] not in WALLS or rt[0]["to"] != "Riolu":
        return False
    z = r["kpf"]["zone"]
    if z is None or z["before_k"] or z["slot"] == 0:
        return False
    ea = r["kpf"]["end"]["active"]
    if not ea or ea["name"] != "Riolu" or ea["e"] != "":
        return False
    if strict_kp3 and wall_to_riolu(r["kp3"], ("Riolu",)):
        return False
    return True


print()
report("P5 (strict: Riolu ends with no Energy, kp3 did not make same retreat)", p5, show=10)
report("P5 (without kp3 exclusion)", lambda r: p5(r, False), show=10)


def p5loose(r):
    if not unused(r) or r["kpf_cat"] != "RETREAT":
        return False
    rt = r["kpf"]["retreats"]
    if not rt or rt[0]["from"] not in WALLS or rt[0]["to"] not in RIOLU_LINE:
        return False
    z = r["kpf"]["zone"]
    return z is not None and not z["before_k"] and z["pos"] != 0


report("P5 loose: first move retreat wall->Riolu line, zone later ends off the Active", p5loose, show=12)

# P6 reverse
p6 = lambda r: endA(r, "kpf") in WALLS and endA(r, "kp3") in RIOLU_LINE
w6, b6 = report("P6 kpf end Active wall, kp3 end Active Riolu line", p6, show=8)
sub = lambda r: bool(r["kpf"]["zone"] is not None and r["kpf"]["zone"]["slot"] == 0 and r["kpf"]["zone"].get("retreated_from_active") \
    and name(r["div_board"]["active"]) == "Riolu")
print("   P6 of which kpf attached zone to Active Riolu then retreated it:", sum(map(sub, w6)), sum(map(sub, b6)))

# P7
za = lambda f: f["zone"] is not None and not f["zone"]["before_k"]
report("P7 kpf zone attach to Active (at attach), kp3's to Bench",
       lambda r: za(r["kpf"]) and za(r["kp3"]) and r["kpf"]["zone"]["slot"] == 0 and r["kp3"]["zone"]["slot"] != 0, show=4)


# P8 Hitmonlee spots
def p8(r):
    a = r["div_board"]["active"]
    if not a or a["name"] != "Hitmonlee" or a["e"] != "":
        return False
    k3, kf = r["kp3"], r["kpf"]
    return (za(k3) and k3["zone"]["slot"] == 0 and "ATTACK Stretch Kick" in k3["attacks"]
            and za(kf) and kf["zone"]["slot"] != 0 and kf["zone"]["target"] in RIOLU_LINE and not kf["attacks"])


report("P8 Hitmonlee 0E Active; kp3 attach+Stretch Kick; kpf attach to benched Riolu line, no attack", p8, show=6)
