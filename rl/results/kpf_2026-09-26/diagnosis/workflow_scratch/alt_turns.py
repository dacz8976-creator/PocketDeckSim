"""Per-game turn-level comparison at the first divergence (altaria)."""
import json, sys, re
from collections import Counter, defaultdict
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch")
from alt_lib import *

deck = sys.argv[1] if len(sys.argv) > 1 else "altaria"
recs, base, kpf = load_all(deck)
OUT = HERE + f"/workflow_scratch/{deck}_games.jsonl"


def own_turn_summary(game, seat, turn):
    lines = [ln for ln in game if ln["turn"] == turn and ln["actor"] == seat]
    zone = None
    attack = None
    retreats, evolves, places, plays, others = [], [], [], [], []
    for ln in lines:
        d = describe(ln, seat)
        c = cat(ln["act"])
        if c.startswith("ATTACH") and "zone" in d:
            zone = ("A" if c == "ATTACH->ACTIVE" else "B") + ":" + str(d.split("(")[1].split(",")[0])
        elif c.startswith("ATTACK"):
            attack = c[7:] + "@" + str(ln["slots"][seat][0])
        elif c == "RETREAT":
            retreats.append(d)
        elif c == "EVOLVE":
            evolves.append(d)
        elif c == "PLACE":
            places.append(d)
        elif c.startswith("PLAY") or c == "TOOL":
            plays.append(d)
    first = lines[0] if lines else None
    return {"zone": zone, "attack": attack, "retreats": retreats, "evolves": evolves, "places": places, "plays": plays,
            "acts": [describe(ln, seat) for ln in lines],
            "board": first["raw"][seat] if first else None, "opp": first["raw"][1 - seat] if first else None}


def game_totals(game, seat):
    t = Counter()
    for ln in game:
        if ln["actor"] != seat:
            continue
        c = cat(ln["act"])
        d = describe(ln, seat)
        if c.startswith("ATTACH") and "zone" in d:
            t["zone_" + c[8:]] += 1
        if c == "RETREAT":
            t["retreat"] += 1
        if c.startswith("ATTACK"):
            t["attack"] += 1
            t["atk:" + c[7:]] += 1
        if c == "EVOLVE":
            t["evolve"] += 1
    last = game[-1]
    t["turns"] = last["turn"]
    return t


out = []
bad = 0
for r in recs:
    gb, gk = base.get(r["seed"]), kpf.get(r["seed"])
    if not gb or not gk:
        bad += 1; continue
    gb, gk = annotate(gb[0]), annotate(gk[0])
    k = next((n for n in range(min(len(gb), len(gk))) if gb[n]["act"] != gk[n]["act"]), None)
    if k is None or gb[k]["act"] != r["kp3_act"] or gk[k]["act"] != r["kpf_act"]:
        bad += 1; continue
    seat = r["kpf_seat"]
    t = gb[k]["turn"]
    own_turn = gb[k]["tomove"] == seat
    t0 = t if own_turn else t + 1
    rec = {k2: r[k2] for k2 in ("seed", "kind", "pairing", "a", "b", "i", "turn", "actor_is_kpf", "kp3_cat", "kpf_cat",
                                "own_board", "opp_board")}
    rec["opp"] = r["b"] if r["a"] == deck else r["a"]
    rec["k3"] = describe(gb[k], seat)
    rec["kf"] = describe(gk[k], seat)
    rec["own_turn"] = own_turn
    rec["t0"] = t0
    rec["slots"] = gb[k]["slots"][seat]
    rec["base"] = [own_turn_summary(gb, seat, t0 + 2 * j) for j in range(3)]
    rec["kpf"] = [own_turn_summary(gk, seat, t0 + 2 * j) for j in range(3)]
    rec["tot_base"] = game_totals(gb, seat)
    rec["tot_kpf"] = game_totals(gk, seat)
    # final points
    rec["pts_base"] = (gb[-1]["side"][seat]["P"], gb[-1]["side"][1 - seat]["P"])
    rec["pts_kpf"] = (gk[-1]["side"][seat]["P"], gk[-1]["side"][1 - seat]["P"])
    rec["kp3_seq"] = [describe(ln, seat) + ("" if ln["actor"] == seat else "[opp]") for ln in gb[k:k + 8]]
    rec["kpf_seq"] = [describe(ln, seat) + ("" if ln["actor"] == seat else "[opp]") for ln in gk[k:k + 8]]
    out.append(rec)
print("records", len(out), "bad", bad)
with open(OUT, "w") as f:
    for x in out:
        f.write(json.dumps(x) + "\n")
