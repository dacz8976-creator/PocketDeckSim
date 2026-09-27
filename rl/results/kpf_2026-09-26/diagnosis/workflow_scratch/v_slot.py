"""The slot contrast: kpf moves a GG attacker into the Active and feeds it the Zone Energy there, (a) where kp3 fed the
Zone Energy to a benched Pokemon (same Energy plan, different slot: the move gains no tempo), vs (b) where kp3 fed it to
a 1-cost Active (Shuckle/Combee) to attack with (the move trades this turn's chip for a turn of GG tempo)."""
import json
from math import comb
rows = {r["seed"]: r for r in json.load(open("v_rows.json"))}
cls = json.load(open("v_cls.json"))
GG = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def fisher(a, b, c, d):
    n1, n2, m1, n = a + b, c + d, a + c, a + b + c + d
    def p(x):
        return comb(m1, x) * comb(n - m1, n1 - x) / comb(n, n1)
    obs = p(a)
    lo, hi = max(0, m1 - n2), min(m1, n1)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs + 1e-12)


A, B = [], []
for c in cls:
    b, f = c["b"], c["f"]
    if not b["own_turn"] or f["zone"] != "A" or f["zone_name"] not in GG:
        continue
    if b["zone"] == "B":
        A.append(c)
    elif b["zone"] == "A" and b["zone_name"] not in GG:
        B.append(c)
for name, grp in (("(a) kp3 fed the Bench; kpf moved a GG attacker forward and fed it", A),
                  ("(b) kp3 fed a 1-cost Active to attack; kpf fed a GG Active instead", B)):
    w = sum(1 for c in grp if c["kind"] == "worse")
    print(f"{name}: worse {w} / better {len(grp) - w}")
    print("   kp3 attacked in:", sum(1 for c in grp if c["b"]["attack"]), " kpf attacked in:", sum(1 for c in grp if c["f"]["attack"]))
wa, ba = sum(c["kind"] == "worse" for c in A), sum(c["kind"] == "better" for c in A)
wb, bb = sum(c["kind"] == "worse" for c in B), sum(c["kind"] == "better" for c in B)
print(f"Fisher exact, (a) vs (b) worse share: p = {fisher(wa, ba, wb, bb):.3f}")
for c in A:
    r = rows[c["seed"]]
    print(f"--- {c['kind']} {c['seed']} t{c['turn']} v {c['opp']}")
    print(f"   own: {r['own']}")
    print(f"   opp: {r['opp_board']}")
    print(f"   kp3: {' ; '.join(r['seq_b'])}")
    print(f"   kpf: {' ; '.join(r['seq_f'])}")
    print(f"   end kp3: {r['b_end']}")
    print(f"   end kpf: {r['f_end']}")
