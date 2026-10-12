"""Compare the d513e37b replay with run A (b96296a5) game for game and decision for decision. Run from the repo root."""
import json
A = "rl/results/strength_2026-10-04_kx3_v_k3/games.jsonl"
R = "rl/results/strength_2026-10-05_kx3_replay_d513/games.jsonl"
def load(p):
    return {(x["arm"], x["deck"], x["opp"], x["seed"], x["seat"]): x for x in (json.loads(l) for l in open(p) if l.strip())}
a, r = load(A), load(R)
keys = [k for k in r if k[0] == "X"]
same = diff = missing = 0
for k in sorted(keys):
    if k not in a: missing += 1; continue
    x, y = a[k], r[k]
    fx = (x["winner"], x["points"], x["turns"], x["plies"], [d.get("act") for d in (x.get("log") or [])])
    fy = (y["winner"], y["points"], y["turns"], y["plies"], [d.get("act") for d in (y.get("log") or [])])
    if fx == fy: same += 1
    else:
        diff += 1; print("DIFFERS:", k, fx[:4], fy[:4])
nd = sum(len(r[k].get("log") or []) for k in keys if k in a)
print(f"replayed kx3 games {len(keys)}: equal {same}, different {diff}, missing in run A {missing}; logged decisions compared {nd}")
print("BUILDS PLAY IDENTICALLY ON THIS SAMPLE" if diff == 0 and missing == 0 and same == len(keys) else "HOLD: the builds differ")