"""Vespiquen: per cell, how many games got worse / better under kpf on the vespiquen side (same deals), and the net."""
import json
K = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/reading"
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f"{K}/{f}"))}
base, first, second = load("table_kp3.jsonl"), load("mixed_table_kpf3_first.jsonl"), load("mixed_table_kpf3_second.jsonl")
print(list(next(iter(base.values())).keys()))
tot = [0, 0, 0, 0, 0.0]
for p in sorted({k[0] for k in base}):
    g0 = base[(p, 0)]
    if "vespiquen" not in (g0["a"], g0["b"]):
        continue
    rows, cfg = (first, "first") if g0["a"] == "vespiquen" else (second, "second")
    own = (lambda g: g["first_deck_score"]) if cfg == "first" else (lambda g: 1 - g["first_deck_score"])
    n = sum(1 for k in base if k[0] == p)
    ch = [own(rows[(p, i)]) - own(base[(p, i)]) for i in range(n)]
    w = sum(1 for d in ch if d < 0); b = sum(1 for d in ch if d > 0)
    same_moves = sum(1 for i in range(n) if rows[(p, i)].get("moves") == base[(p, i)].get("moves"))
    net = sum(ch)
    print(f"pairing {p:2} {g0['a']:>10} v {g0['b']:<10} n={n} worse={w} better={b} unchanged={n-w-b} net={net:+.1f} ({100*net/n:+.1f} pts) identical-move-games={same_moves}")
    tot[0] += n; tot[1] += w; tot[2] += b; tot[3] += same_moves; tot[4] += net
print("total", tot, f"{100*tot[4]/tot[0]:+.2f} pts")
