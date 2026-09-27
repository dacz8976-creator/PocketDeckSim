import json
from collections import Counter, defaultdict
K = "../../reading"
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f"{K}/{f}"))}
base, first, second = load("table_kp3.jsonl"), load("mixed_table_kpf3_first.jsonl"), load("mixed_table_kpf3_second.jsonl")
deck = "vespiquen"
tot = Counter(); net = 0.0; n = 0
per = defaultdict(float)
for p in sorted({k[0] for k in base}):
    g0 = base[(p, 0)]
    if deck not in (g0["a"], g0["b"]):
        continue
    rows, cfg = (first, "first") if g0["a"] == deck else (second, "second")
    own = (lambda g: g["first_deck_score"]) if cfg == "first" else (lambda g: 1 - g["first_deck_score"])
    for i in range(500):
        if (p, i) not in rows:
            continue
        d = own(rows[(p, i)]) - own(base[(p, i)])
        n += 1; net += d; per[p] += d
        tot["worse" if d < 0 else "better" if d > 0 else "same"] += 1
print("games", n, tot, "net", net, "points", round(100 * net / n, 2))
print({p: round(100 * v / 500, 1) for p, v in per.items()})
