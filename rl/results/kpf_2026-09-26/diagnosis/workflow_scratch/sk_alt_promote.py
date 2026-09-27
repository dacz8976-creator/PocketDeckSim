import re, pickle, importlib.util
from collections import Counter
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
spec = importlib.util.spec_from_file_location("rc", D + "workflow_scratch/sk_alt_side.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
side = rc.side


def promoted(game, k, seat):
    """name of the Active right after the promote at k, plus where the next own-turn Mega Altaria evolve goes"""
    nxt = side(game[k + 1]["s"][seat])
    name = nxt["a"][0] if nxt["a"] else None
    # next own turn
    t = game[k]["turn"] + 1
    L = [ln for ln in game if ln["turn"] == t and ln["tomove"] == seat and ln["actor"] == seat]
    ev = None
    for ln in L:
        m = re.match(r"Evolve \{ evolution: Pokemon\(\S+ \S+ Mega Altaria ex\), in_play_idx: (\d+)", ln["act"])
        if m:
            ev = "A" if m.group(1) == "0" else "B"
    return name, ev


ct = Counter()
for r in alt:
    s, k, seat = r["seed"], r["k"], r["kpf_seat"]
    x, y = base[s][0], kpf[s][0]
    if x[k]["tomove"] == seat:
        continue
    c3, cf = promoted(x, k, seat), promoted(y, k, seat)
    print(s, r["kind"], "kp3:", r["kp3_act"][:40], c3, "| kpf:", r["kpf_act"][:40], cf)
    isprom = r["kp3_act"].startswith("Promote") and r["kpf_act"].startswith("Promote")
    ct[(r["kind"], isprom, cf[0] == "Swablu", cf[1] == "A", c3[1] == "B")] += 1
for k, v in sorted(ct.items()):
    print(k, v)
