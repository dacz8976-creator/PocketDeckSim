#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
python3 - <<'EOF'
import sys
sys.path.insert(0, ".")
exec(open("alt_procr.py").read().split("agg = defaultdict(Counter)")[0])
out = []
for r in recs:
    gb, gk = base[r["seed"]][0], kpf[r["seed"]][0]
    seat = r["kpf_seat"]
    k = next(n for n in range(min(len(gb), len(gk))) if gb[n]["act"] != gk[n]["act"])
    t0 = gb[k]["turn"]
    for t, start, zone, atk in turns(gk, seat, t0):
        a = start["active"]
        if not a or start["zc"] == "None": continue
        need = COST.get(a["name"])
        if need is None or need - len(a["e"]) != 1: continue
        if zone == "B" and not atk:
            out.append((r["seed"], r["kind"][0], t, a["name"], start["bench"] and [m["name"]+"/"+m["e"] for m in start["bench"]]))
for o in out: print(o)
EOF