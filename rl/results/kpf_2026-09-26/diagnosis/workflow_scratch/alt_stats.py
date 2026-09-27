"""Group the turn-level differences and compare worse vs better (altaria)."""
import json, sys, math
from collections import Counter, defaultdict
deck = sys.argv[1] if len(sys.argv) > 1 else "altaria"
HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
G = [json.loads(l) for l in open(f"{HERE}/{deck}_games.jsonl")]
print("games", len(G), Counter(g["kind"] for g in G))
NW = sum(g["kind"] == "worse" for g in G); NB = sum(g["kind"] == "better" for g in G)


def z2(a, b, na=NW, nb=NB):
    p1, p2 = a / na, b / nb
    p = (a + b) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb)) if 0 < p < 1 else 1
    return (p1 - p2) / se


def binom_p(k, n):
    # two-sided exact binomial p for k of n at 0.5
    from math import comb
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(p for p in pk if p <= obs + 1e-12))


def table(title, keyf, min_total=4):
    c = defaultdict(Counter)
    for g in G:
        c[keyf(g)][g["kind"]] += 1
    print(f"\n== {title}")
    rows = sorted(c.items(), key=lambda kv: -(kv[1]["worse"] + kv[1]["better"]))
    for k, v in rows:
        w, b = v["worse"], v["better"]
        if w + b < min_total:
            continue
        print(f"  {str(k):70} worse {w:3} better {b:3}  z={z2(w, b):+.2f}  p(binom)={binom_p(w, w + b):.3f}")


GROUP = {
    "ATTACH->ACTIVE": "commit:attach-active", "RETREAT": "commit:retreat",
    "ATTACH->BENCH": "build:attach-bench", "EVOLVE": "build:evolve", "PLACE": "build:place",
    "END": "end", "PROMOTE": "promote", "TOOL": "tool", "ABILITY": "ability",
}


def grp(c):
    if c.startswith("ATTACK"):
        return "commit:attack"
    if c in GROUP:
        return GROUP[c]
    if c.startswith("PLAY"):
        n = c[5:]
        if "Research" in n or "Poké Ball" in n or "Copycat" in n:
            return "draw/search"
        if "Sabrina" in n:
            return "sabrina"
        return "trainer:" + n
    return c


table("kpf_seat acts at divergence", lambda g: g["actor_is_kpf"], 0)
table("own turn vs opp turn divergence", lambda g: g["own_turn"], 0)
table("kpf group at first divergence", lambda g: grp(g["kpf_cat"]))
table("kp3 group at first divergence", lambda g: grp(g["kp3_cat"]))
table("(kp3 group -> kpf group)", lambda g: (grp(g["kp3_cat"]), grp(g["kpf_cat"])))


def zone_cls(z):
    if z is None:
        return "none"
    return z


def turn_diff(g, j=0):
    b, f = g["base"][j], g["kpf"][j]
    return b, f


table("zone target at decision turn: (kp3, kpf)", lambda g: (g["base"][0]["zone"], g["kpf"][0]["zone"]), 3)
table("zone side at decision turn: (kp3, kpf)",
      lambda g: ((g["base"][0]["zone"] or "none")[0], (g["kpf"][0]["zone"] or "none")[0]), 0)
table("attack at decision turn: (kp3, kpf)",
      lambda g: (g["base"][0]["attack"] is not None, g["kpf"][0]["attack"] is not None), 0)
table("attack name decision turn: (kp3, kpf)", lambda g: (g["base"][0]["attack"], g["kpf"][0]["attack"]), 3)
table("retreat at decision turn: (kp3, kpf)",
      lambda g: (len(g["base"][0]["retreats"]) > 0, len(g["kpf"][0]["retreats"]) > 0), 0)
table("retreat detail: kpf retreats but kp3 doesn't",
      lambda g: tuple(g["kpf"][0]["retreats"]) if g["kpf"][0]["retreats"] and not g["base"][0]["retreats"] else "-", 2)
table("same multiset of acts in decision turn (reorder)", lambda g: sorted(g["base"][0]["acts"]) == sorted(g["kpf"][0]["acts"]), 0)


def turn_class(b, f):
    if sorted(b["acts"]) == sorted(f["acts"]):
        return "reorder-only"
    bits = []
    if b["zone"] != f["zone"]:
        bs = (b["zone"] or "n")[0]; fs = (f["zone"] or "n")[0]
        bits.append(f"zone {bs}->{fs}" if bs != fs else "zone same-side other-mon")
    if (b["attack"] is None) != (f["attack"] is None):
        bits.append("kpf attacks, kp3 not" if f["attack"] else "kp3 attacks, kpf not")
    elif b["attack"] != f["attack"]:
        bits.append("different attack")
    if bool(b["retreats"]) != bool(f["retreats"]):
        bits.append("kpf retreats, kp3 not" if f["retreats"] else "kp3 retreats, kpf not")
    elif b["retreats"] != f["retreats"]:
        bits.append("different retreat")
    if not bits:
        bits.append("other (places/evolves/trainers)")
    return " & ".join(bits)


table("decision-turn class", lambda g: turn_class(g["base"][0], g["kpf"][0]), 3)
print()
# each component separately
for comp in ("zone A->B", "zone B->A", "zone A->n", "zone n->A", "zone B->n", "zone n->B", "zone same-side other-mon",
             "kpf attacks, kp3 not", "kp3 attacks, kpf not", "different attack", "kpf retreats, kp3 not",
             "kp3 retreats, kpf not", "different retreat", "reorder-only"):
    w = sum(comp in turn_class(g["base"][0], g["kpf"][0]) for g in G if g["kind"] == "worse")
    b = sum(comp in turn_class(g["base"][0], g["kpf"][0]) for g in G if g["kind"] == "better")
    print(f"  component {comp:30} worse {w:3} better {b:3} z={z2(w, b):+.2f} p={binom_p(w, w + b) if w + b else 1:.3f}")

# whole-game totals difference
print("\n== whole-game totals (kpf - kp3) for the deck's seat, mean over games")
keys = sorted({k for g in G for k in list(g["tot_base"]) + list(g["tot_kpf"])})
for key in keys:
    for kind in ("worse", "better"):
        xs = [g["tot_kpf"].get(key, 0) - g["tot_base"].get(key, 0) for g in G if g["kind"] == kind]
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
        print(f"  {key:30} {kind:6} mean diff {m:+.2f} (se {sd / len(xs) ** 0.5:.2f})  base mean "
              f"{sum(g['tot_base'].get(key, 0) for g in G if g['kind'] == kind) / len(xs):.2f}")
