"""Skeptic: whole-game counts, the Espeon-one-short turns, and rb4 recipients."""
import re, pickle, importlib.util
from collections import Counter, defaultdict
from math import comb, sqrt

D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
rows = pickle.load(open(D + "workflow_scratch/sk_alt_rows2.pkl", "rb"))
spec = importlib.util.spec_from_file_location("rc", D + "workflow_scratch/sk_alt_side.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
side = rc.side

# rb4 recipients
print("BA(att) & rb4 recipients:")
for kind in ("worse", "better"):
    c = Counter((r["kpf"]["attach"]["name"], r["kpf"]["div_active"]) for r in rows
                if r["kind"] == kind and r["kp3"]["d_att"] == "B" and r["kpf"]["d_att"] == "A" and r["kpf"]["rb4"])
    print("  ", kind, dict(c))

# whole game counts
def count(game, seat, k0=0):
    zA = zB = sing = mh = hyp = ds = lull = 0
    for ln in game[k0:]:
        if ln["actor"] != seat or ln["tomove"] != seat:
            continue
        a = ln["act"]
        m = re.match(r"Attach \{ attachments: \[\((\d+), (\w+), (\d+)\)\], is_turn_energy: true", a)
        if m:
            if m.group(3) == "0":
                zA += 1
            else:
                zB += 1
        t = re.search(r'title: "([^"]+)"', a) if a.startswith("Attack(") else None
        if t:
            n = t.group(1)
            sing += n == "Sing"; mh += n == "Mega Harmony"; hyp += n == "Hypnoblast"; ds += n == "Dark Slumber"
            lull += n == "Sleepy Lullaby"
    return dict(zA=zA, zB=zB, sing=sing, mh=mh, hyp=hyp, ds=ds, lull=lull)


agg = {k: defaultdict(list) for k in ("worse", "better")}
for r in alt:
    s, seat = r["seed"], r["kpf_seat"]
    cb, ck = count(base[s][0], seat), count(kpf[s][0], seat)
    for key in cb:
        agg[r["kind"]][key].append(ck[key] - cb[key])
print("\nwhole game, kpf minus kp3, mean per game (sd of mean):")
for kind in ("worse", "better"):
    out = []
    for key, v in agg[kind].items():
        m = sum(v) / len(v)
        sd = sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / sqrt(len(v))
        out.append(f"{key} {m:+.2f}({sd:.2f})")
    print("  ", kind, len(agg[kind]["zA"]), " ".join(out))

# Espeon/one-short turns
COST = {"Espeon": (1, 40), "Darkrai": (3, 40), "Mega Altaria ex": (2, 40), "Eevee": (1, 10), "Igglybuff": (0, 10)}


def one_short_turns(game, seat, k0):
    res = []
    turns = sorted({ln["turn"] for ln in game[k0:] if ln["tomove"] == seat})
    for t in turns:
        L = [(n, ln) for n, ln in enumerate(game) if ln["turn"] == t and ln["tomove"] == seat and ln["actor"] == seat]
        if not L:
            continue
        # first line after the draw
        first = next(((n, ln) for n, ln in L if not ln["act"].startswith("DrawCard")), None)
        if first is None:
            continue
        sd = side(first[1]["s"][seat])
        if not sd["a"] or sd["zc"] == "None":
            continue
        nm, e = sd["a"][0], len(sd["a"][3])
        if nm not in COST:
            continue
        if COST[nm][0] - e != 1:
            continue
        zb = any(re.match(r"Attach \{ attachments: \[\(\d+, \w+, [123]\)\], is_turn_energy: true", ln["act"]) for _, ln in L)
        attacked = any(ln["act"].startswith("Attack(") for _, ln in L)
        res.append((t, nm, zb, attacked))
    return res


print("\nActive one Energy short at turn start, Zone has Energy; turns from the divergence on:")
for kind in ("worse", "better"):
    for which, G in (("kpf", kpf), ("kp3", base)):
        tot = skip = 0
        names = Counter()
        for r in alt:
            if r["kind"] != kind:
                continue
            for t, nm, zb, att in one_short_turns(G[r["seed"]][0], r["kpf_seat"], r["k"]):
                tot += 1
                names[nm] += 1
                if zb and not att:
                    skip += 1
        print(f"   {kind:6s} {which}: {skip}/{tot} turns bench-attach & no attack; actives {dict(names)}")
