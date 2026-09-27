import re, pickle, importlib.util
from collections import Counter
from math import comb
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
rows = pickle.load(open(D + "workflow_scratch/sk_alt_rows2.pkl", "rb"))
spec = importlib.util.spec_from_file_location("rc", D + "workflow_scratch/sk_alt_side.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
side = rc.side


def fisher(a, n1, b, n2):
    K = a + b; N = n1 + n2
    p = lambda x: comb(n1, x) * comb(n2, K - x) / comb(N, K)
    p0 = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, K - n2), min(K, n1) + 1) if p(x) <= p0 * (1 + 1e-9)))


# Espeon-only one-short turns
def espeon_turns(game, seat, k0):
    out = []
    for t in sorted({ln["turn"] for ln in game[k0:] if ln["tomove"] == seat}):
        L = [ln for ln in game if ln["turn"] == t and ln["tomove"] == seat and ln["actor"] == seat]
        first = next((ln for ln in L if not ln["act"].startswith("DrawCard")), None)
        if not first:
            continue
        sd = side(first["s"][seat])
        if not sd["a"] or sd["zc"] == "None" or sd["a"][0] != "Espeon" or sd["a"][3] != "" or "SLP" in sd["a"][2] or "PAR" in sd["a"][2]:
            continue
        zb = any(re.match(r"Attach \{ attachments: \[\(\d+, \w+, [123]\)\]", ln["act"]) for ln in L)
        att = any(ln["act"].startswith("Attack(") for ln in L)
        out.append((zb and not att))
    return out


for kind in ("worse", "better"):
    for w, G in (("kpf", kpf), ("kp3", base)):
        v = []
        for r in alt:
            if r["kind"] == kind:
                v += espeon_turns(G[r["seed"]][0], r["kpf_seat"], r["k"])
        print(f"Espeon 0E Active, zone has E: {kind} {w}: bench-attach & no attack {sum(v)}/{len(v)}")

Wo = [r for r in rows if r["kind"] == "worse"]; Bo = [r for r in rows if r["kind"] == "better"]
print()
f = lambda r: r["kp3"]["div_active"] == "Igglybuff" and r["kp3"]["end_active"] == "Igglybuff" and r["kpf"]["end_active"] != "Igglybuff"
for kind, P in (("worse", Wo), ("better", Bo)):
    c = Counter(r["kpf"]["end_active"] for r in P if f(r))
    print(kind, "kp3 keeps Igglybuff, kpf moves off it:", sum(c.values()), dict(c))
a = sum(f(r) for r in Wo); b = sum(f(r) for r in Bo)
print("fisher", a, b, round(fisher(a, len(Wo), b, len(Bo)), 3))
g = lambda r: f(r) and r["kpf"]["end_active"] in ("Swablu", "Eevee")
a = sum(g(r) for r in Wo); b = sum(g(r) for r in Bo)
print("  ... to Swablu/Eevee:", a, b, round(fisher(a, len(Wo), b, len(Bo)), 3))
g = lambda r: f(r) and r["kpf"]["end_active"] not in ("Swablu", "Eevee")
a = sum(g(r) for r in Wo); b = sum(g(r) for r in Bo)
print("  ... to others:", a, b, round(fisher(a, len(Wo), b, len(Bo)), 3))
# kpf ends turn with an unevolved Swablu/Eevee Active that kp3 did not have
g = lambda r: r["kpf"]["end_active"] in ("Swablu", "Eevee") and r["kp3"]["end_active"] not in ("Swablu", "Eevee")
a = sum(g(r) for r in Wo); b = sum(g(r) for r in Bo)
print("kpf ends with Swablu/Eevee Active, kp3 not:", a, b, round(fisher(a, len(Wo), b, len(Bo)), 3))
g = lambda r: r["kp3"]["end_active"] in ("Swablu", "Eevee") and r["kpf"]["end_active"] not in ("Swablu", "Eevee")
a = sum(g(r) for r in Wo); b = sum(g(r) for r in Bo)
print("kp3 ends with Swablu/Eevee Active, kpf not:", a, b, round(fisher(a, len(Wo), b, len(Bo)), 3))
