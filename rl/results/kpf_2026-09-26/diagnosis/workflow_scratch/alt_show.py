"""Print readable per-game detail. Usage: alt_show.py deck filter_expr [limit]"""
import json, sys
deck = sys.argv[1]
expr = sys.argv[2] if len(sys.argv) > 2 else "True"
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 999
HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/workflow_scratch"
G = [json.loads(l) for l in open(f"{HERE}/{deck}_games.jsonl")]


def side(z):
    return (z or "n")[0]


n = 0
for g in G:
    b0, f0 = g["base"][0], g["kpf"][0]
    zs = (side(b0["zone"]), side(f0["zone"]))
    if not eval(expr):
        continue
    n += 1
    if n > limit:
        break
    print(f"--- seed {g['seed']} {g['kind'].upper()} vs {g['opp']} deal {g['i']} div t{g['turn']} (own turn {g['own_turn']}, t0={g['t0']})"
          f" final kp3 {g['pts_base']} kpf {g['pts_kpf']}")
    print(f"   own: {g['own_board']}   slots {g['slots']}")
    print(f"   opp: {g['opp_board']}")
    print(f"   kp3: {g['k3']:35} | turn: {' '.join(b0['acts'])}")
    print(f"   kpf: {g['kf']:35} | turn: {' '.join(f0['acts'])}")
    for j in (1, 2):
        b, f = g["base"][j], g["kpf"][j]
        print(f"   t0+{2*j}: kp3 zone={b['zone']} atk={b['attack']} ret={b['retreats']} ev={b['evolves']} | "
              f"kpf zone={f['zone']} atk={f['attack']} ret={f['retreats']} ev={f['evolves']}")
        print(f"          kp3 board {b['board']}")
        print(f"          kpf board {f['board']}")
print("shown", min(n, limit))
