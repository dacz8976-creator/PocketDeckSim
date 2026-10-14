import json, os, sys
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
for pid in sys.argv[1:]:
    f = V2 + "runs_forced/forced_%s.json" % pid
    recs = json.load(open(f, encoding="utf-8"))
    print("#" * 60, pid, len(recs))
    if recs:
        print(json.dumps(recs[0], ensure_ascii=False, indent=0)[:4000])
# km3 free runs listing
d = V2 + "runs_km3"
print(os.listdir(d)[:20])
