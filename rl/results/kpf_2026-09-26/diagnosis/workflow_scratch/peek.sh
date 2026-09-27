#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
python3 - <<'EOF'
import json, collections
sel = json.load(open("selected.json"))
print(len(sel), sel[0])
seeds = collections.Counter(g["seed"] for g in sel)
print("dup seeds", sum(1 for s,c in seeds.items() if c>1))
alt = [g for g in sel if g["deck"]=="altaria"]
print(len(alt))
print(collections.Counter((g["b"] if g["a"]=="altaria" else g["a"], g["kind"]) for g in alt))
print(collections.Counter((g["kind"], g["change"]) for g in alt))
print(collections.Counter((g["kind"], g["config"]) for g in alt))
EOF
grep -o ':: [A-Za-z]*' dump_base.txt | sort | uniq -c
grep -m3 ':: Evolve' dump_base.txt
grep -m3 ':: Retreat' dump_base.txt
grep -m3 ':: Promote' dump_base.txt
grep -m3 ':: Attack' dump_base.txt
grep -m3 ':: UseAbility' dump_base.txt