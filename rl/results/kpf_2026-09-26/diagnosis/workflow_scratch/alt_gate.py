"""End-of-decision-turn boards under each bot; would Dustin's gate (project the Active only when it is the side's
best attacker by the clock's own unprojected pick) have applied? Also a position-independent variant."""
import json, sys, re
from collections import Counter, defaultdict
from math import comb
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import *
ROLE = {"Espeon": "main", "Mega Altaria ex": "main", "Darkrai": "darkrai(CCC)", "Swablu": "pre-evo", "Eevee": "pre-evo",
        "Igglybuff": "pivot"}


def binom_p(k, n):
    if n == 0:
        return 1.0
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def threat(side):
    """Approximate unprojected clock threat pick: (missing incl. evolution steps, -damage, slot, name)."""
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

recs, base, kpf = load_all("altaria")
T = {json.loads(l)["seed"]: json.loads(l) for l in open(HERE + "/workflow_scratch/altaria_games.jsonl")}


def end_board(game, seat, t0):
    """Own side right after the seat's turn t0 ends (first line after turn t0)."""
    for ln in game:
        if ln["turn"] > t0:
            return parse_side(ln["raw"][seat]), ln["slots"][seat] if "slots" in ln else None
    return None, None


def cand_list(side):
    mons = [(0, side["active"])] + [(i + 1, m) for i, m in enumerate(side["bench"])]
    return [(s, m) for s, m in mons if m]


def active_best_proj(side, zone_next=1):
    """Active's best candidate projected by next turn's Zone (+1 Energy)."""
    a = side["active"]
    if not a:
        return None
    s2 = json.loads(json.dumps(side))
    s2["active"]["e"] += "P" * zone_next
    s2["bench"] = []  # only the active's candidates, but keep bench count for Mega Harmony
    nb = len(side["bench"])
    th = threat({"active": s2["active"], "bench": [{"name": "x", "e": "", "hp": 0, "st": ""}] * nb})
    return th


def bench_reachable_best(side):
    """Best benched candidate if it took next turn's Zone (+1) and the Active can retreat into it (retreat cost payable)."""
    a = side["active"]
    if not a:
        return None
    rc = {"Igglybuff": 0, "Darkrai": 2, "Swablu": 1, "Eevee": 1, "Espeon": 1, "Mega Altaria ex": 1}.get(a["name"], 1)
    if len(a["e"]) < rc:
        return None
    best = None
    nb = len(side["bench"])
    for i, m in enumerate(side["bench"]):
        m2 = dict(m); m2["e"] = m["e"] + "P"
        th = threat({"active": m2, "bench": [{"name": "x", "e": "", "hp": 0, "st": ""}] * nb})
        if th and (best is None or th[:2] < best[:2]):
            best = th
    return best


out = []
for r in recs:
    g = T[r["seed"]]
    if not g["own_turn"]:
        continue
    gb, gk = annotate(base[r["seed"]][0]), annotate(kpf[r["seed"]][0])
    seat, t0 = r["kpf_seat"], g["t0"]
    eb, _ = end_board(gb, seat, t0)
    ek, _ = end_board(gk, seat, t0)
    if not eb or not ek:
        continue
    row = {"seed": r["seed"], "kind": r["kind"], "zb": (g["base"][0]["zone"] or "n")[0], "zf": (g["kpf"][0]["zone"] or "n")[0],
           "kf_tgt": (g["kpf"][0]["zone"] or "n:-").split(":")[1],
           "pa": bool(g["kpf"][0]["retreats"]) and not g["base"][0]["retreats"]}
    for name, eside in (("b", eb), ("k", ek)):
        th = threat(eside)  # unprojected pick
        row[name + "_active"] = eside["active"]["name"] if eside["active"] else None
        row[name + "_active_best"] = th is not None and th[2] == 0
        row[name + "_threat"] = th
        row[name + "_proj"] = active_best_proj(eside)
        row[name + "_bench_reach"] = bench_reachable_best(eside)
    out.append(row)

print("own-turn decisions with end boards:", len(out))


def show(title, sel):
    print(f"\n== {title}")
    for kind in ("worse", "better"):
        rs = [r for r in out if sel(r) and r["kind"] == kind]
        gate_k = sum(1 for r in rs if not r["k_active_best"])
        gate_b = sum(1 for r in rs if not r["b_active_best"])
        print(f"   {kind:6} n={len(rs):3}  kpf's end board: Active NOT the unprojected best attacker in {gate_k:3}"
              f"  | kp3's end board: Active not best in {gate_b:3}")
        c = Counter((r["k_active"], r["k_threat"][3] if r["k_threat"] else None) for r in rs)
        print(f"          kpf end (Active, threat pick): {c.most_common(6)}")


show("kp3 Zone->Bench, kpf Zone->Active spot (B->A)", lambda r: r["zb"] == "B" and r["zf"] == "A")
show("  of which kpf retreated first (PA)", lambda r: r["zb"] == "B" and r["zf"] == "A" and r["pa"])
show("  of which recipient is a pre-evolution", lambda r: r["zb"] == "B" and r["zf"] == "A" and ROLE.get(r["kf_tgt"]) == "pre-evo")
show("  of which recipient is Darkrai", lambda r: r["zb"] == "B" and r["zf"] == "A" and r["kf_tgt"] == "Darkrai")
show("  of which recipient is Espeon/Mega Altaria", lambda r: r["zb"] == "B" and r["zf"] == "A" and ROLE.get(r["kf_tgt"]) == "main")
show("both Zone->Active (A->A)", lambda r: r["zb"] == "A" and r["zf"] == "A")

# Would gating remove the projection's advantage for kpf's line? Count B->A games where the gate blocks kpf-line projection
print("\n== B->A: gate blocks projection in kpf's line (Active not best) AND kp3 line's Active also not best/neutral")
for kind in ("worse", "better"):
    rs = [r for r in out if r["zb"] == "B" and r["zf"] == "A" and r["kind"] == kind]
    blocked = [r for r in rs if not r["k_active_best"]]
    print(f"   {kind}: blocked {len(blocked)}/{len(rs)} seeds {[r['seed'] for r in blocked][:12]}")
    print(f"          not blocked seeds {[r['seed'] for r in rs if r['k_active_best']][:14]}")

# Igglybuff in play at end of kpf's line
print("\n== B->A: Igglybuff in play on kpf's end board")
for kind in ("worse", "better"):
    rs = [r for r in out if r["zb"] == "B" and r["zf"] == "A" and r["kind"] == kind]
    print(f"   {kind}: {sum(1 for r in rs if r['k_threat'] and r['k_threat'][3] == 'Igglybuff')}/{len(rs)} have Igglybuff as the unprojected threat pick")
