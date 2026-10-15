import json, glob, os
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/runs_forced/"
for f in sorted(glob.glob(P + "forced_KW-26101[23]_0[11]*")):
    if "010706" not in f and "015011" not in f:
        continue
    d = json.load(open(f))
    r = d[0]
    forced = [s.get("forced") for s in r["steps"] if "forced" in s]
    last = r["steps"][-1]
    oks = set(x.get("ok") for x in d)
    print(os.path.basename(f), "ok:", oks, "| forced:", forced, "| last:", json.dumps({k: v for k, v in last.items() if k != "step"})[:300])
    for x in d:
        if x.get("error") or x.get("problems"):
            print("   ", x.get("error"), x.get("problems"))
            break
