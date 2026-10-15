import json, os, re, glob
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
meta = json.load(open(R + "games_meta.json", encoding="utf-8"))
P = json.load(open(R + "positions_all.json", encoding="utf-8"))
items = P if isinstance(P, list) else P.get("positions", P)
pos = {p["id"]: p for p in items}
known = {'card_play', 'item', 'supporter', 'trainer', 'card_play_attempt', 'energy_attachment', 'energy', 'attach_energy', 'bench', 'bench_basic', 'bench_pokemon',
         'evolution', 'evolve', 'tool', 'tool_attachment', 'stadium', 'item_evolution', 'retreat', 'attack', 'prompt_response', 'ability', 'stadium_ability', 'stadium_effect',
         'end_turn', 'end_turn_request'}
kinds_all = {}
for g, m in meta.items():
    f = B + m["folder"] + "/TURN_LEDGER.json"
    L = json.load(open(f, encoding="utf-8"))
    gid = "KW" + g[2:]
    for t in L["turns"]:
        if not str(t.get("who_played", "")).startswith("owner"):
            continue
        tn = t["turn_number"]
        pid = f"{gid}-t{tn:02d}"
        for p in t.get("plays_in_order") or []:
            k = str(p.get("kind") or "").strip().lower().replace(" ", "_")
            kinds_all[k] = kinds_all.get(k, 0) + 1
            if k not in known or 'stadium' in k:
                pp = pos.get(pid)
                plan = pp["his_plan"] if pp else None
                print(pid, "| order", p.get("order"), "| kind", k, "| card", p.get("card_name"), "| res", str(p.get("result") or p.get("details"))[:110])
                print("     in positions:", pp is not None, "| plan:", plan, "| trunc:", pp.get("plan_truncated_at") if pp else None)
print(sorted(kinds_all.items()))
