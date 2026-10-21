import json, os, re
REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
V = f"{REPO}/rl/results/pause_games_new_2026-10-13/v2"
O = "/home/dacz8976/stageA/out/pos_km3"
ids = [l.strip() for l in open(f"{V}/run_ids.txt") if l.strip()]
norm = lambda m: re.sub(r"^(AttachTypedFromDiscard)(:.*)?$", r"\1", m)
def plans(p):
    out = {}
    for line in open(p):
        j = json.loads(line)
        if j.get("kind") == "free":
            out[j["seed"]] = j.get("plan") or []
    return out
raw = norm_diff = 0
games = set()
for i in ids:
    a, b = plans(f"{V}/runs_km3/out_{i}.jsonl"), plans(f"{O}/out_{i}.jsonl")
    for s in a:
        if a[s] != b.get(s):
            raw += 1
            games.add(i)
            if [norm(m) for m in a[s]] != [norm(m) for m in (b.get(s) or [])]:
                norm_diff += 1
                print("REAL difference:", i, s, a[s], b.get(s))
print(f"raw differences {raw} in {sorted(games)}; after normalising the AttachTypedFromDiscard label: {norm_diff}")
