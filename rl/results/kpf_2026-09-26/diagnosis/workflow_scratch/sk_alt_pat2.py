"""Skeptic's recount, v2: attach-time destination (as the analyst apparently used) and a corrected end-of-turn
destination (Energy spent on a retreat counted as spent, not moved)."""
import re, pickle, importlib.util
from collections import Counter
from math import comb

D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
spec = importlib.util.spec_from_file_location("rc", D + "workflow_scratch/sk_alt_side.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
side = rc.side


def fisher(a, n1, b, n2):
    K = a + b; N = n1 + n2
    p = lambda x: comb(n1, x) * comb(n2, K - x) / comb(N, K)
    p0 = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, K - n2), min(K, n1) + 1) if p(x) <= p0 * (1 + 1e-9)))


def binom_split(a, b):
    n = a + b
    if n == 0:
        return 1.0
    pa = comb(n, a) / 2 ** n
    return min(1.0, sum(comb(n, x) / 2 ** n for x in range(n + 1) if comb(n, x) / 2 ** n <= pa * (1 + 1e-9)))


def tot_energy(sd):
    return (len(sd["a"][3]) if sd["a"] else 0) + sum(len(m[3]) for m in sd["b"])


def summarize(game, k, seat):
    t = game[k]["turn"]
    L = [(n, ln) for n, ln in enumerate(game) if ln["turn"] == t and ln["tomove"] == seat and ln["actor"] == seat]
    res = {"acts": [ln["act"] for _, ln in L]}
    att, retreats, attack = None, [], None
    for j, (n, ln) in enumerate(L):
        a = ln["act"]
        m = re.match(r"Attach \{ attachments: \[\((\d+), (\w+), (\d+)\)\], is_turn_energy: true", a)
        if m and att is None:
            idx = int(m.group(3))
            before, after = side(ln["s"][seat]), side(game[n + 1]["s"][seat])
            name, e = None, None
            if idx == 0:
                name, e = before["a"][0], len(after["a"][3])
            else:
                for x, y in zip(before["b"], after["b"]):
                    if len(y[3]) > len(x[3]) and x[0] == y[0]:
                        name, e = x[0], len(y[3])
                        break
            att = {"pos": j, "idx": idx, "name": name, "e": e}
        m = re.match(r"Retreat\((\d+)\)", a)
        if m:
            paid = tot_energy(side(ln["s"][seat])) - tot_energy(side(game[n + 1]["s"][seat]))
            retreats.append((j, int(m.group(1)), paid))
        if a.startswith("Attack(") and attack is None:
            attack = re.search(r'title: "([^"]+)"', a).group(1)
    res.update(attach=att, retreats=retreats, attack=attack)
    if att:
        pos, e, spent = att["idx"], att["e"], False
        for j, i, paid in retreats:
            if j <= att["pos"]:
                continue
            if pos == 0:
                e -= paid
                if e <= 0:
                    spent = True
                    break
                pos = i
            elif pos == i:
                pos = 0
        res["d_att"] = "A" if att["idx"] == 0 else "B"
        res["d_end"] = "R" if spent else ("A" if pos == 0 else "B")
        res["rb4"] = any(j < att["pos"] for j, _, _ in retreats)
    else:
        res["d_att"] = res["d_end"] = "N"
        res["rb4"] = False
    endb = side(L[-1][1]["s"][seat])
    res["end_active"] = endb["a"][0] if endb["a"] else None
    db = side(game[k]["s"][seat])
    res["div_active"] = db["a"][0] if db["a"] else None
    st = side(L[0][1]["s"][seat])
    res["start_active"] = st["a"][0] if st["a"] else None
    res["board"] = game[k]["s"][seat]
    return res


rows = []
for r in alt:
    s, k, seat = r["seed"], r["k"], r["kpf_seat"]
    x, y = base[s][0], kpf[s][0]
    if x[k]["tomove"] != seat:
        continue
    rows.append({"seed": s, "kind": r["kind"], "opp": r["b"], "turn": x[k]["turn"], "kp3": summarize(x, k, seat),
                 "kpf": summarize(y, k, seat)})
pickle.dump(rows, open(D + "workflow_scratch/sk_alt_rows2.pkl", "wb"))
Wo = [r for r in rows if r["kind"] == "worse"]; Bo = [r for r in rows if r["kind"] == "better"]
print("own-turn:", len(Wo), len(Bo))


def rep(label, f, show=False):
    a = [r for r in Wo if f(r)]; b = [r for r in Bo if f(r)]
    print(f"{label:78s} {len(a):3d} vs {len(b):3d}  fisher p={fisher(len(a), len(Wo), len(b), len(Bo)):.3f}  split p={binom_split(len(a), len(b)):.3f}")
    if show:
        print("     worse:", [r["seed"] for r in a]); print("     better:", [r["seed"] for r in b])
    return a, b


print("\n== end-of-turn destination (corrected): kp3 -> kpf")
ct = Counter((r["kind"], r["kp3"]["d_end"], r["kpf"]["d_end"]) for r in rows)
for c in sorted({(a, b) for (_, a, b) in ct}):
    print(f"   {c[0]} -> {c[1]}: worse {ct[('worse',) + c]:3d} better {ct[('better',) + c]:3d}")

for dk in ("d_att", "d_end"):
    print(f"\n######## BA defined with {dk}")
    BA = lambda r, dk=dk: r["kp3"][dk] == "B" and r["kpf"][dk] == "A"
    rep("BA", BA, show=(dk == "d_att"))
    rep("BA & kpf retreated before attach", lambda r: BA(r) and r["kpf"]["rb4"], show=(dk == "d_att"))
    rep("BA & kpf retreated before attach & kp3 no retreat", lambda r: BA(r) and r["kpf"]["rb4"] and not r["kp3"]["retreats"])
    rep("BA & kpf no retreat before attach", lambda r: BA(r) and not r["kpf"]["rb4"], show=(dk == "d_att"))
    rep("BA & kpf no retreat in whole turn", lambda r: BA(r) and not r["kpf"]["retreats"])
    for nm in (("Swablu", "Eevee"), ("Swablu",), ("Eevee",), ("Darkrai",), ("Espeon", "Mega Altaria ex")):
        rep(f"BA & kpf recipient {nm}", lambda r, nm=nm: BA(r) and r["kpf"]["attach"]["name"] in nm, show=(dk == "d_att" and nm == ("Swablu", "Eevee")))
    rep("BA & recipient Swablu/Eevee & kpf used Sing/Stampede", lambda r: BA(r) and r["kpf"]["attach"]["name"] in ("Swablu", "Eevee") and r["kpf"]["attack"] in ("Sing", "Stampede"))
    rep("BA & rb4 & start Active Igglybuff", lambda r: BA(r) and r["kpf"]["rb4"] and r["kpf"]["div_active"] == "Igglybuff")
    rep("BA & start Active Igglybuff", lambda r: BA(r) and r["kp3"]["div_active"] == "Igglybuff")
    rep("BA & start Active Darkrai", lambda r: BA(r) and r["kp3"]["div_active"] == "Darkrai")
    rep("BA & start Active Swablu/Eevee", lambda r: BA(r) and r["kp3"]["div_active"] in ("Swablu", "Eevee"))
    rep("BA & no rb4 & kpf recipient Darkrai", lambda r: BA(r) and not r["kpf"]["rb4"] and r["kpf"]["attach"]["name"] == "Darkrai")

print("\n######## other")
rep("kp3 ends with Igglybuff Active + Sleepy Lullaby; kpf ends with another Active",
    lambda r: r["kp3"]["end_active"] == "Igglybuff" and r["kp3"]["attack"] == "Sleepy Lullaby" and r["kpf"]["end_active"] != "Igglybuff")
for nm in ("Espeon", "Swablu", "Eevee", "Darkrai", "Mega Altaria ex"):
    rep(f"   ... kpf end Active {nm}", lambda r, nm=nm: r["kp3"]["end_active"] == "Igglybuff" and r["kp3"]["attack"] == "Sleepy Lullaby" and r["kpf"]["end_active"] == nm)
rep("kp3 attacked, kpf did not", lambda r: r["kp3"]["attack"] and not r["kpf"]["attack"])
rep("kpf attacked, kp3 did not", lambda r: r["kpf"]["attack"] and not r["kp3"]["attack"])
rep("kpf Sing at div turn, kp3 not", lambda r: r["kpf"]["attack"] == "Sing" and r["kp3"]["attack"] != "Sing")
rep("kpf Sing/Stampede at div turn, kp3 not", lambda r: r["kpf"]["attack"] in ("Sing", "Stampede") and r["kp3"]["attack"] not in ("Sing", "Stampede"))
rep("div Active Igglybuff", lambda r: r["kp3"]["div_active"] == "Igglybuff")
rep("div Active Igglybuff & kpf retreats, kp3 not", lambda r: r["kp3"]["div_active"] == "Igglybuff" and r["kpf"]["retreats"] and not r["kp3"]["retreats"])
rep("kpf retreats, kp3 not", lambda r: r["kpf"]["retreats"] and not r["kp3"]["retreats"])
rep("kpf retreat-then-attach-to-Active (any kp3)", lambda r: r["kpf"]["rb4"] and r["kpf"]["d_att"] == "A")
rep("kp3 retreat-then-attach-to-Active (any kpf)", lambda r: r["kp3"]["rb4"] and r["kp3"]["d_att"] == "A")
