import json
A = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
B = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R6/repro/positions.json"
a = {p["id"]: p for p in json.load(open(A, encoding="utf-8"))}
b = {p["id"]: p for p in json.load(open(B, encoding="utf-8"))}
for k, pb in b.items():
    pa = a.get(k)
    if pa is None:
        print(k, "missing in v2")
        continue
    diffs = [x for x in set(pa) | set(pb) if pa.get(x) != pb.get(x)]
    print(k, "diff keys:", diffs)
    for x in diffs:
        if x not in ("unresolved",):
            print("   v2:", json.dumps(pa.get(x), ensure_ascii=False)[:300])
            print("   re:", json.dumps(pb.get(x), ensure_ascii=False)[:300])
