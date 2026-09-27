"""Skeptic's recount of the Altaria patterns, from the dumps (own code)."""
import json, re, pickle
from collections import Counter, defaultdict
from math import comb
import importlib.util, sys

D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
spec = importlib.util.spec_from_file_location("rc", D + "workflow_scratch/sk_alt_side.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
side = rc.side


def fisher(a, n1, b, n2):
    """two-sided Fisher exact p for a/n1 vs b/n2"""
    K = a + b; N = n1 + n2
    def p(x):
        return comb(n1, x) * comb(n2, K - x) / comb(N, K)
    p0 = p(a)
    lo, hi = max(0, K - n2), min(K, n1)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9))


def binom_split(a, b):
    """two-sided exact binomial p that a of a+b are in 'worse' under p=0.5"""
    n = a + b
    pa = comb(n, a) / 2 ** n
    return min(1.0, sum(comb(n, x) / 2 ** n for x in range(n + 1) if comb(n, x) / 2 ** n <= pa * (1 + 1e-9)))


def turn_lines(game, k, seat):
    """all lines of the seat's turn containing index k (lines by the seat with tomove == seat, same turn)."""
    t = game[k]["turn"]
    return [(n, ln) for n, ln in enumerate(game) if ln["turn"] == t and ln["tomove"] == seat and ln["actor"] == seat]


def summarize(game, k, seat):
    L = turn_lines(game, k, seat)
    acts = [ln["act"] for _, ln in L]
    start = side(L[0][1]["s"][seat])
    res = {"acts": acts, "start_active": start["a"][0] if start["a"] else None, "zone": start["zc"]}
    att = None
    retreats = []
    attack = None
    for j, (n, ln) in enumerate(L):
        a = ln["act"]
        m = re.match(r"Attach \{ attachments: \[\((\d+), (\w+), (\d+)\)\], is_turn_energy: true", a)
        if m and att is None:
            idx = int(m.group(3))
            before = side(ln["s"][seat])
            after = side(game[n + 1]["s"][seat]) if n + 1 < len(game) else before
            # recipient by energy diff
            name = None
            if idx == 0:
                name = before["a"][0]
            else:
                for x, y in zip(before["b"], after["b"]):
                    if len(y[3]) > len(x[3]) and x[0] == y[0]:
                        name = x[0]
                        break
            att = {"pos": j, "idx": idx, "name": name}
        m = re.match(r"Retreat\((\d+)\)", a)
        if m:
            retreats.append((j, int(m.group(1))))
        if a.startswith("Attack(") and attack is None:
            attack = re.search(r'title: "([^"]+)"', a).group(1)
    res["attach"] = att
    res["retreats"] = retreats
    res["attack"] = attack
    # end-of-turn destination of the turn energy
    if att:
        pos = att["idx"]
        for j, i in retreats:
            if j > att["pos"]:
                if pos == 0:
                    pos = i
                elif pos == i:
                    pos = 0
        res["dest_attach"] = "A" if att["idx"] == 0 else "B"
        res["dest_end"] = "A" if pos == 0 else "B"
        res["retreat_before_attach"] = any(j < att["pos"] for j, _ in retreats)
    else:
        res["dest_attach"] = res["dest_end"] = "N"
        res["retreat_before_attach"] = False
    # end-of-turn active: board on last line of turn (EndTurn line shows state before EndTurn)
    endb = side(L[-1][1]["s"][seat])
    res["end_active"] = endb["a"][0] if endb["a"] else None
    res["end_active_e"] = endb["a"][3] if endb["a"] else None
    # active at the divergence
    db = side(game[k]["s"][seat])
    res["div_active"] = db["a"][0] if db["a"] else None
    res["div_board"] = game[k]["s"][seat]
    return res


rows = []
for r in alt:
    s, k, seat = r["seed"], r["k"], r["kpf_seat"]
    x, y = base[s][0], kpf[s][0]
    own_turn = x[k]["tomove"] == seat
    row = {"seed": s, "kind": r["kind"], "opp": r["b"], "own_turn": own_turn, "turn": x[k]["turn"],
           "kp3_act": r["kp3_act"], "kpf_act": r["kpf_act"]}
    if own_turn:
        row["kp3"] = summarize(x, k, seat)
        row["kpf"] = summarize(y, k, seat)
    rows.append(row)
pickle.dump(rows, open(D + "workflow_scratch/sk_alt_rows.pkl", "wb"))

W = [r for r in rows if r["kind"] == "worse"]
B = [r for r in rows if r["kind"] == "better"]
Wo = [r for r in W if r["own_turn"]]
Bo = [r for r in B if r["own_turn"]]
print("own-turn divergences: worse", len(Wo), "better", len(Bo), "; opp-turn:", len(W) - len(Wo), len(B) - len(Bo))


def rep(label, f, pool_w=Wo, pool_b=Bo):
    a = sum(1 for r in pool_w if f(r)); b = sum(1 for r in pool_b if f(r))
    print(f"{label:70s} {a:3d}/{len(pool_w)} vs {b:3d}/{len(pool_b)}  fisher p={fisher(a, len(pool_w), b, len(pool_b)):.3f}"
          f"  binom(split) p={binom_split(a, b):.3f}")
    return a, b


for dk in ("dest_attach", "dest_end"):
    print(f"\n== 5-way table using {dk}")
    ct = Counter()
    for r in Wo + Bo:
        ct[(r["kind"], r["kp3"][dk], r["kpf"][dk])] += 1
    cells = [("A", "A"), ("B", "A"), ("A", "B"), ("B", "B")]
    for c in cells:
        print(f"  kp3 {c[0]} -> kpf {c[1]}: worse {ct[('worse',) + c]:3d}  better {ct[('better',) + c]:3d}")
    nw = sum(v for (kd, a, b), v in ct.items() if kd == "worse" and "N" in (a, b))
    nb = sum(v for (kd, a, b), v in ct.items() if kd == "better" and "N" in (a, b))
    print(f"  either N: worse {nw} better {nb}")
    # chi-square 5x2
    tab = [[ct[("worse",) + c], ct[("better",) + c]] for c in cells] + [[nw, nb]]
    tw, tb = sum(t[0] for t in tab), sum(t[1] for t in tab)
    chi = 0
    for t in tab:
        n = t[0] + t[1]
        ew, eb = n * tw / (tw + tb), n * tb / (tw + tb)
        chi += (t[0] - ew) ** 2 / ew + (t[1] - eb) ** 2 / eb
    print(f"  chi-square (4 df) = {chi:.2f}  (5% crit 9.49)")
    rep(f"[{dk}] kp3 Bench -> kpf Active", lambda r: r["kp3"][dk] == "B" and r["kpf"][dk] == "A")

dk = "dest_end"
BA = lambda r: r["kp3"][dk] == "B" and r["kpf"][dk] == "A"
print()
rep("BA & kpf retreat before attach", lambda r: BA(r) and r["kpf"]["retreat_before_attach"])
rep("BA & kpf retreat before attach & kp3 no retreat", lambda r: BA(r) and r["kpf"]["retreat_before_attach"] and not r["kp3"]["retreats"])
rep("BA & kpf no retreat at all", lambda r: BA(r) and not r["kpf"]["retreats"])
rep("BA & kpf any retreat", lambda r: BA(r) and r["kpf"]["retreats"])
for nm in ("Swablu", "Eevee", "Darkrai", "Espeon", "Mega Altaria ex", "Igglybuff"):
    rep(f"BA & kpf recipient {nm}", lambda r, nm=nm: BA(r) and r["kpf"]["attach"]["name"] == nm)
rep("BA & kpf recipient Swablu/Eevee", lambda r: BA(r) and r["kpf"]["attach"]["name"] in ("Swablu", "Eevee"))
rep("BA & kpf end-active Swablu/Eevee", lambda r: BA(r) and r["kpf"]["end_active"] in ("Swablu", "Eevee"))
rep("BA & kpf recip Swablu/Eevee & Sing/Stampede", lambda r: BA(r) and r["kpf"]["attach"]["name"] in ("Swablu", "Eevee") and r["kpf"]["attack"] in ("Sing", "Stampede"))
rep("ANY own turn: kpf end-active Swablu/Eevee with zone on it, kp3 not", lambda r: r["kpf"][dk] == "A" and r["kpf"]["attach"]["name"] in ("Swablu", "Eevee") and not (r["kp3"][dk] == "A" and r["kp3"]["attach"]["name"] in ("Swablu", "Eevee")))
rep("ANY: kpf Sings at div turn, kp3 not", lambda r: r["kpf"]["attack"] == "Sing" and r["kp3"]["attack"] != "Sing")
rep("Darkrai fed by kpf in Active (any route), kp3 not feeding Active Darkrai", lambda r: r["kpf"][dk] == "A" and r["kpf"]["attach"]["name"] == "Darkrai" and not (r["kp3"][dk] == "A" and r["kp3"]["attach"]["name"] == "Darkrai"))
rep("BA & kpf recipient Darkrai (any route)", lambda r: BA(r) and r["kpf"]["attach"]["name"] == "Darkrai")
print()
rep("Pattern5: kp3 Igglybuff Active at end + Sleepy Lullaby; kpf end Active != Igglybuff",
    lambda r: r["kp3"]["end_active"] == "Igglybuff" and r["kp3"]["attack"] == "Sleepy Lullaby" and r["kpf"]["end_active"] != "Igglybuff")
rep("  ... and kpf end Active Mega Altaria ex",
    lambda r: r["kp3"]["end_active"] == "Igglybuff" and r["kp3"]["attack"] == "Sleepy Lullaby" and r["kpf"]["end_active"] == "Mega Altaria ex")
rep("kp3 used Sleepy Lullaby, kpf did not", lambda r: r["kp3"]["attack"] == "Sleepy Lullaby" and r["kpf"]["attack"] != "Sleepy Lullaby")
rep("kp3 attacked, kpf did not", lambda r: r["kp3"]["attack"] and not r["kpf"]["attack"])
rep("kpf attacked, kp3 did not", lambda r: r["kpf"]["attack"] and not r["kp3"]["attack"])
rep("start Active Igglybuff (at div)", lambda r: r["kp3"]["div_active"] == "Igglybuff")
rep("start Active Igglybuff & BA", lambda r: r["kp3"]["div_active"] == "Igglybuff" and BA(r))
rep("start Active Igglybuff & kpf retreats (any)", lambda r: r["kp3"]["div_active"] == "Igglybuff" and r["kpf"]["retreats"] and not r["kp3"]["retreats"])
rep("start Active Darkrai & BA", lambda r: r["kp3"]["div_active"] == "Darkrai" and BA(r))
rep("start Active Swablu/Eevee & BA", lambda r: r["kp3"]["div_active"] in ("Swablu", "Eevee") and BA(r))
rep("kpf retreats in turn, kp3 doesn't (any)", lambda r: r["kpf"]["retreats"] and not r["kp3"]["retreats"])

# Opp-turn divergences (promotes)
Wp = [r for r in W if not r["own_turn"]]; Bp = [r for r in B if not r["own_turn"]]
print("\nopp-turn divergences:", len(Wp), len(Bp))
def prom_name(r, which):
    return r[which]
for r in Wp + Bp:
    pass
json.dump([{k: v for k, v in r.items()} for r in rows], open(D + "workflow_scratch/sk_alt_rows.json", "w"), default=str)
