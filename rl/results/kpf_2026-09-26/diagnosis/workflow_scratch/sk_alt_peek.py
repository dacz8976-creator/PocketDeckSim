import json
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
recs = [json.loads(l) for l in open(D + "divergences.jsonl", encoding="utf-8")]
alt = [r for r in recs if r["deck"] == "altaria"]
print(len(alt), sum(r["kind"] == "worse" for r in alt), sum(r["kind"] == "better" for r in alt))
print(sum(r["actor_is_kpf"] for r in alt if r["kind"] == "worse"), sum(r["actor_is_kpf"] for r in alt if r["kind"] == "better"))
print(json.dumps(alt[0], indent=1))
print(json.dumps(alt[1], indent=1))
from collections import Counter
print(Counter((r["a"], r["b"], r["config"]) for r in alt))
