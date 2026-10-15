import json
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/runs_forced/"
S = json.load(open(R + "forced_summary.json", encoding="utf-8"))
def find(o):
    if isinstance(o, dict):
        if any("203719000-t07" in str(v) for v in o.values() if isinstance(v, str)):
            return o
        for k, v in o.items():
            if "203719000-t07" in str(k):
                return {k: v}
            r = find(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = find(v)
            if r: return r
    return None
print(json.dumps(find(S), ensure_ascii=False, indent=1)[:6000])
print("##### forced file")
F = json.load(open(R + "forced_KW-261012_203719000-t07.json", encoding="utf-8"))
print(json.dumps(F, ensure_ascii=False, indent=1)[:8000])
# how many positions in summary were cut, and do any have plan_truncated_at
P = json.load(open("/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json", encoding="utf-8"))
if isinstance(P, dict): P = P.get("positions") or list(P.values())
print("positions with plan_truncated_at not null:", [(p["id"], p["plan_truncated_at"]) for p in P if p.get("plan_truncated_at") is not None])
