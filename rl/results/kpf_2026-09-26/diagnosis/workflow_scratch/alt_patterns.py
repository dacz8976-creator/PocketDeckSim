"""Named patterns at the decision turn, worse vs better (altaria)."""
import json, sys, math, re
from collections import Counter, defaultdict
from math import comb
HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
G = [json.loads(l) for l in open(f"{HERE}/altaria_games.jsonl")]


def binom_p(k, n):
    if n == 0:
        return 1.0
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def side(z):
    return (z or "n")[0]


def first_idx(acts, pred):
    for i, a in enumerate(acts):
        if pred(a):
            return i
    return None


def classify(g):
    b, f = g["base"][0], g["kpf"][0]
    zb, zf = side(b["zone"]), side(f["zone"])
    fa, ba = f["acts"], b["acts"]
    f_ret = first_idx(fa, lambda a: a.startswith("RETREAT"))
    f_zone = first_idx(fa, lambda a: "zone)" in a)
    b_ret = first_idx(ba, lambda a: a.startswith("RETREAT"))
    pats = []
    if not g["own_turn"]:
        pats.append("P0 promotion/forced-switch choice (opp turn)")
    # A: kpf retreats (kp3 doesn't) and the Zone goes to the new Active; kp3 zone to Bench
    if f_ret is not None and b_ret is None and zb == "B" and zf == "A" and f_zone is not None and f_zone > f_ret:
        pats.append("PA retreat-up then attach to new Active (kp3 attaches Bench)")
    # B: kpf attaches Zone to the Active it started with (no retreat before), kp3 attaches Bench
    if zb == "B" and zf == "A" and (f_ret is None or f_zone < f_ret):
        if f_ret is not None and b_ret is None:
            pats.append("PB2 attach Zone to Active then retreat it (Zone as retreat fuel); kp3 Bench")
        else:
            pats.append("PB attach Zone to Active instead of Bench")
    if zb == "A" and zf == "B":
        pats.append("PR kp3 Active, kpf Bench (reverse)")
    if b["attack"] and not f["attack"]:
        pats.append("X kp3 attacks, kpf doesn't")
    if f["attack"] and not b["attack"]:
        pats.append("X kpf attacks, kp3 doesn't")
    if b["attack"] and f["attack"] and b["attack"] != f["attack"]:
        pats.append("X different attacker/attack")
    if b["attack"] and b["attack"].startswith("Sleepy Lullaby") and f_ret is not None and b_ret is None:
        pats.append("PI kp3 Lullabies with Igglybuff; kpf retreats Igglybuff")
    if f_ret is not None and b_ret is None:
        pats.append("R kpf retreats, kp3 doesn't (any)")
    if b_ret is not None and f_ret is None:
        pats.append("R kp3 retreats, kpf doesn't (any)")
    return pats


c = defaultdict(Counter)
ex = defaultdict(lambda: defaultdict(list))
for g in G:
    for p in classify(g):
        c[p][g["kind"]] += 1
        ex[p][g["kind"]].append(g["seed"])
print("pattern (decision turn)                                                     worse better  p")
for p in sorted(c):
    w, b = c[p]["worse"], c[p]["better"]
    print(f"  {p:75} {w:4} {b:5}  {binom_p(w, w + b):.3f}   eg W {ex[p]['worse'][:6]} B {ex[p]['better'][:4]}")

# union: kpf commits Zone to the Active spot (by attach or retreat-up) while kp3 builds Bench
def commit(g):
    return any(p.startswith(("PA", "PB")) for p in classify(g))
w = sum(commit(g) for g in G if g["kind"] == "worse"); b = sum(commit(g) for g in G if g["kind"] == "better")
print(f"\n  UNION PA+PB+PB2 (kpf puts turn's Zone on the Active spot, kp3 on Bench): worse {w} better {b} p={binom_p(w, w+b):.3f}")
# per opponent
print("\n  by opponent: UNION worse/better ; X kp3 attacks kpf not worse/better")
for opp in sorted({g['opp'] for g in G}):
    gs = [g for g in G if g['opp'] == opp]
    w = sum(commit(g) for g in gs if g['kind'] == 'worse'); b = sum(commit(g) for g in gs if g['kind'] == 'better')
    print(f"   {opp:10} union {w:2}/{b:2}")

# next own turn: do kp3 and kpf have an attack; zone side
print("\n  next own turn (t0+2) after UNION games: attack present kp3/kpf")
for kind in ("worse", "better"):
    gs = [g for g in G if g["kind"] == kind and commit(g)]
    ab = sum(1 for g in gs if g["base"][1]["attack"]); af = sum(1 for g in gs if g["kpf"][1]["attack"])
    a0b = sum(1 for g in gs if g["base"][0]["attack"]); a0f = sum(1 for g in gs if g["kpf"][0]["attack"])
    dmg = lambda a: a and not a.startswith(("Sing", "Sleepy"))
    print(f"   {kind}: n={len(gs)} t0 attacks kp3 {a0b} kpf {a0f}; t0+2 attacks kp3 {ab} kpf {af}; "
          f"t0 damaging attack (not Sing/Lullaby) kp3 {sum(1 for g in gs if dmg(g['base'][0]['attack']))} kpf {sum(1 for g in gs if dmg(g['kpf'][0]['attack']))}")
