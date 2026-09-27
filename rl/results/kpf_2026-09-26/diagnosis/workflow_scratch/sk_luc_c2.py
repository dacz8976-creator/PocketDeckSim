"""Skeptic: print both bots' divergence turn for given seeds (raw lines from the correct runs)."""
import sys, json, os
from collections import defaultdict
from sk_luc_lib import load_runs, D, cat
seeds = [int(x) for x in sys.argv[1:]]
sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
by_seed = defaultdict(list)
for g in sel:
    by_seed[g["seed"]].append(g)
want = set(seeds)
base, kpf = load_runs("dump_base.txt", want), load_runs("dump_kpf.txt", want)


def short(b):
    return b.split(" | ", 1)[1] if " | " in b else b


for s in seeds:
    entries = sorted(by_seed[s], key=lambda e: (str(e["pairing"]), e["config"]))
    g = [e for e in entries if e["deck"] == "lucario"][0]
    occ = [e["deck"] for e in entries].index("lucario")
    B, K = base[s][min(occ, len(base[s]) - 1)], kpf[s][occ]
    k = next(n for n in range(min(len(B), len(K))) if B[n]["act"] != K[n]["act"])
    first_seat = 0 if g["i"] % 2 == 0 else 1
    seat = first_seat if g["deck"] == g["a"] else 1 - first_seat
    t = B[k]["turn"]
    print(f"===== seed {s} {g['kind']} change {g['change']} pairing {g['a']}-{g['b']} lucario seat {seat} div turn {t}")
    print("   own @div :", B[k]["s"][seat])
    print("   opp @div :", B[k]["s"][1 - seat])
    for lab, R in (("kp3", B), ("kpf", K)):
        print(f"  -- {lab}")
        n = k
        stop_turn = t + 2
        while n < len(R) and R[n]["turn"] <= stop_turn:
            x = R[n]
            if x["turn"] == t or x["turn"] == t + 1 and x["actor"] == seat or x["turn"] == t + 1 and n == k:
                print(f"     t{x['turn']} a{x['actor']} {cat(x['act']):30} {x['act'][:70]}")
            n += 1
        # end of turn t board and start of t+2
        ends = [m for m in range(len(R)) if R[m]["turn"] == t and R[m]["act"].startswith("EndTurn")]
        if ends:
            print("     end t own :", short(R[ends[-1]]["s"][seat]))
        nx = [m for m in range(len(R)) if R[m]["turn"] == t + 2]
        if nx:
            print("     start t+2 own:", short(R[nx[0]]["s"][seat]), "|| opp:", short(R[nx[0]]["s"][1 - seat]))
