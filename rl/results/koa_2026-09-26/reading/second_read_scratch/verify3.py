import json, math
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O = R + "/rl/results/koa_2026-09-26/reading"
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f, encoding="utf-8"))}
koa, kob = load(O + "/mixed_koa3_first.jsonl"), load(O + "/mixed_kob3_first.jsonl")
kp3 = load(R + "/rl/results/kpf_2026-09-26/reading/table_kp3.jsonl")
d = [koa[k]["first_deck_score"] - kob[k]["first_deck_score"] for k in koa]
mu = sum(d) / len(d); var = sum((x - mu) ** 2 for x in d) / (len(d) - 1) / len(d)
print(f"koa minus kob on Altaria (paired, 3500 deals): {100*mu:+.2f} +/- {100*1.96*math.sqrt(var):.2f} (95%)")
e = [kob[k]["first_deck_score"] - kp3[k]["first_deck_score"] for k in kob]
m2 = sum(e) / len(e); v2 = sum((x - m2) ** 2 for x in e) / (len(e) - 1) / len(e)
print(f"kob minus kp3 pooled over deals: {100*m2:+.2f} +/- {100*1.96*math.sqrt(v2):.2f}")
# by transition class for koa: gains in Darkrai->Eevee vs Swablu->Eevee games
from collections import defaultdict
acc = defaultdict(list)
for k in koa:
    if koa[k]["openings"][0] != kp3[k]["openings"][0]:
        acc[(kp3[k]["openings"][0], koa[k]["openings"][0])].append(koa[k]["first_deck_score"] - kp3[k]["first_deck_score"])
for t, v in acc.items():
    m = sum(v) / len(v); s = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1) / len(v))
    print(f"koa {t}: {len(v)} games, {100*m:+.1f} +/- {100*1.96*s:.1f} per changed game")
