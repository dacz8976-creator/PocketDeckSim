"""Direct test of Dustin's hypothesis at the decision turn (altaria)."""
import json, sys, re
from collections import Counter, defaultdict
from math import comb
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import parse_side
HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
G = [json.loads(l) for l in open(f"{HERE}/altaria_games.jsonl")]


def binom_p(k, n):
    if n == 0:
        return 1.0
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


ROLE = {"Espeon": "main", "Mega Altaria ex": "main", "Darkrai": "darkrai(CCC)", "Swablu": "pre-evo", "Eevee": "pre-evo",
        "Igglybuff": "pivot"}


def threat(side):
    """Approximate unprojected clock threat pick: (missing incl. evolution steps, -damage, slot)."""
    mons = [(0, side["active"])] + [(i + 1, m) for i, m in enumerate(side["bench"])]
    mons = [(s, m) for s, m in mons if m]
    names = [m["name"] for _, m in mons]
    nb = len(side["bench"])
    alt_avail = "Mega Altaria ex" not in names
    cands = []
    for s, m in mons:
        e = len(m["e"]); n = m["name"]
        if n == "Swablu" and alt_avail:
            cands.append((max(0, 2 - e) + 1, -(40 + 30 * nb), s, "Mega Altaria ex(evo)"))
        if n == "Eevee":
            cands.append((max(0, 1 - e), -10, s, "Eevee"))
            cands.append((max(0, 1 - e) + 1, -40, s, "Espeon(evo)"))
        if n == "Espeon":
            cands.append((max(0, 1 - e), -40, s, n))
        if n == "Mega Altaria ex":
            cands.append((max(0, 2 - e), -(40 + 30 * nb), s, n))
        if n == "Darkrai":
            cands.append((max(0, 3 - e), -40, s, n))
        if n == "Igglybuff":
            cands.append((0, -10, s, n))
    return min(cands) if cands else None


def side_of(z):
    return (z or "n")[0]


rows = []
for g in G:
    if not g["own_turn"]:
        continue
    b, f = g["base"][0], g["kpf"][0]
    start = parse_side(b["board"])  # own board at the start of the decision turn (same in both traces)
    act = start["active"]["name"] if start["active"] else None
    th = threat(start)
    rows.append({"kind": g["kind"], "zb": side_of(b["zone"]), "zf": side_of(f["zone"]),
                 "kf_tgt": (f["zone"] or "n:-").split(":")[1], "kb_tgt": (b["zone"] or "n:-").split(":")[1],
                 "active": act, "role": ROLE.get(act, "?"), "active_is_threat": th is not None and th[2] == 0,
                 "threat": th, "seed": g["seed"]})

print("decision turns on own turn:", len(rows))
print("\n(1) Where does the turn's Zone Energy go? (kp3 side, kpf side) x kind")
c = Counter((r["zb"], r["zf"], r["kind"]) for r in rows)
for zb in "ABn":
    for zf in "ABn":
        w, bb = c[(zb, zf, "worse")], c[(zb, zf, "better")]
        if w + bb:
            print(f"   kp3 {zb} kpf {zf}: worse {w:3} better {bb:3}  p={binom_p(w, w + bb):.3f}")

print("\n(2) When kp3 puts the Zone on the Bench, what does kpf do, by role of the Active at the start of the turn")
for role in ("main", "darkrai(CCC)", "pre-evo", "pivot"):
    for kind in ("worse", "better"):
        rs = [r for r in rows if r["zb"] == "B" and r["role"] == role and r["kind"] == kind]
        cc = Counter(r["zf"] for r in rs)
        print(f"   Active role {role:13} {kind:6}: n={len(rs):3}  kpf->Active {cc['A']:3}  kpf->Bench {cc['B']:3}  none {cc['n']:2}")

print("\n(3) kpf moves Zone to the Active spot while kp3 builds Bench, split by whether the Active is the (approx.) clock threat")
for flag in (True, False):
    w = sum(1 for r in rows if r["zb"] == "B" and r["zf"] == "A" and r["active_is_threat"] == flag and r["kind"] == "worse")
    b = sum(1 for r in rows if r["zb"] == "B" and r["zf"] == "A" and r["active_is_threat"] == flag and r["kind"] == "better")
    nw = sum(1 for r in rows if r["zb"] == "B" and r["active_is_threat"] == flag and r["kind"] == "worse")
    nb = sum(1 for r in rows if r["zb"] == "B" and r["active_is_threat"] == flag and r["kind"] == "better")
    print(f"   Active is threat={flag}: B->A worse {w}/{nw} better {b}/{nb}  p(w vs b)={binom_p(w, w + b):.3f}")

print("\n(4) kpf's Zone target species when kp3 -> Bench and kpf -> Active")
cc = Counter((r["kf_tgt"], r["kind"]) for r in rows if r["zb"] == "B" and r["zf"] == "A")
for t in sorted({k[0] for k in cc}):
    print(f"   kpf feeds Active {t:18} worse {cc[(t, 'worse')]:3} better {cc[(t, 'better')]:3}  p={binom_p(cc[(t, 'worse')], cc[(t, 'worse')] + cc[(t, 'better')]):.3f}")
print("   (kp3's Bench target in those games)")
cc = Counter((r["kb_tgt"], r["kind"]) for r in rows if r["zb"] == "B" and r["zf"] == "A")
for t in sorted({k[0] for k in cc}):
    print(f"   kp3 feeds Bench {t:18} worse {cc[(t, 'worse')]:3} better {cc[(t, 'better')]:3}")
print("\n(5) main-attacker role of kpf's Zone recipient (B->A games)")
cc = Counter((ROLE.get(r["kf_tgt"], "?"), r["kind"]) for r in rows if r["zb"] == "B" and r["zf"] == "A")
for t in sorted({k[0] for k in cc}):
    print(f"   {t:15} worse {cc[(t, 'worse')]:3} better {cc[(t, 'better')]:3}  p={binom_p(cc[(t, 'worse')], cc[(t, 'worse')] + cc[(t, 'better')]):.3f}")
