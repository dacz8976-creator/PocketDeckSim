import json, sys
from collections import Counter
from math import comb
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import parse_side
HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
G = [json.loads(l) for l in open(f"{HERE}/altaria_games.jsonl")]


def bp(k, n):
    if n == 0:
        return 1.0
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


PRE = {"Swablu", "Eevee"}
rows = []
for g in G:
    if not g["own_turn"]:
        continue
    b, f = g["base"][0], g["kpf"][0]
    zb, zf = (b["zone"] or "n")[0], (f["zone"] or "n")[0]
    tgt = (f["zone"] or "n:-").split(":")[1]
    start = parse_side(b["board"])
    pa = bool(f["retreats"]) and not b["retreats"]
    # did the kpf recipient evolve this turn in the Active? (evolved name appears as target)
    rows.append(dict(kind=g["kind"], seed=g["seed"], BA=(zb == "B" and zf == "A"), pa=pa, tgt=tgt,
                     start_active=start["active"]["name"] if start["active"] else None,
                     start_hp=start["active"]["hp"] if start["active"] else None,
                     katk=f["attack"], batk=b["attack"], opp=g["opp_board"]))


def cnt(pred, label):
    w = sum(1 for r in rows if pred(r) and r["kind"] == "worse")
    b = sum(1 for r in rows if pred(r) and r["kind"] == "better")
    print(f"  {label:95} worse {w:3} better {b:3}  p={bp(w, w + b):.3f}")


print("Own-turn decisions:", len(rows))
cnt(lambda r: r["BA"], "B->A (kpf Zone to Active spot, kp3 Bench)")
cnt(lambda r: r["BA"] and r["pa"], "  B->A with kpf retreat first (PA)")
cnt(lambda r: r["BA"] and not r["pa"], "  B->A without retreat first")
cnt(lambda r: r["BA"] and r["tgt"] in PRE, "  B->A recipient pre-evolution (Swablu/Eevee, not evolved this turn)")
cnt(lambda r: r["BA"] and r["tgt"] in PRE and r["pa"], "    ... and PA")
cnt(lambda r: r["BA"] and r["tgt"] in PRE and not r["pa"], "    ... not PA")
cnt(lambda r: r["BA"] and r["pa"] and r["tgt"] not in PRE, "  PA with recipient not a pre-evolution")
cnt(lambda r: r["BA"] and r["pa"] and r["tgt"] == "Darkrai", "    PA recipient Darkrai")
cnt(lambda r: r["BA"] and r["pa"] and r["tgt"] in ("Espeon", "Mega Altaria ex"), "    PA recipient Espeon/Mega Altaria ex (evolved in Active)")
cnt(lambda r: r["start_active"] == "Igglybuff", "start-of-turn Active is Igglybuff (all own-turn decisions)")
cnt(lambda r: r["start_active"] == "Igglybuff" and r["BA"], "  Igglybuff Active and B->A")
cnt(lambda r: r["start_active"] == "Igglybuff" and r["BA"] and r["tgt"] in PRE, "  Igglybuff Active, B->A, recipient pre-evo")
cnt(lambda r: r["start_active"] == "Igglybuff" and r["BA"] and r["tgt"] == "Darkrai", "  Igglybuff Active, B->A, recipient Darkrai")
cnt(lambda r: r["start_active"] == "Igglybuff" and r["BA"] and r["tgt"] in ("Espeon", "Mega Altaria ex"), "  Igglybuff Active, B->A, recipient Espeon/Mega Altaria")
cnt(lambda r: r["start_active"] == "Igglybuff" and not r["BA"], "  Igglybuff Active, not B->A")
cnt(lambda r: r["BA"] and r["batk"] and r["batk"].startswith("Sleepy") and (not r["katk"] or r["katk"].split("@")[0] in ("Sing", "Stampede")),
    "  B->A and kp3 Lullabies while kpf does no attack / Sing / Stampede")
print("\nIgglybuff HP at start when kpf retreats it (PA) worse vs better:")
for kind in ("worse", "better"):
    print("  ", kind, sorted(r["start_hp"] for r in rows if r["kind"] == kind and r["pa"] and r["start_active"] == "Igglybuff" and r["BA"]))
print("\nkpf attack at decision turn in B->A games with pre-evo recipient:")
for kind in ("worse", "better"):
    print("  ", kind, Counter(r["katk"] for r in rows if r["kind"] == kind and r["BA"] and r["tgt"] in PRE))
print("\nseeds: B->A & pre-evo recipient", [(r["seed"], r["kind"][0]) for r in rows if r["BA"] and r["tgt"] in PRE])
