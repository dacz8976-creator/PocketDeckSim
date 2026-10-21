import json
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
S = json.load(open(R + "runs_forced/forced_summary.json", encoding="utf-8"))
print(type(S), list(S.keys())[:10] if isinstance(S, dict) else len(S))
found = []
def walk(o):
    if isinstance(o, dict):
        if o.get("id") in ("KW-261012_210823000-t08", "KW-261013_020824000-t11"):
            found.append(o)
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(S)
for o in found:
    print(json.dumps(o, ensure_ascii=False, indent=1)[:2500])
