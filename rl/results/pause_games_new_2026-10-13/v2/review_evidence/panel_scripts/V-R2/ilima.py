import json, re
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
POS = json.load(open(R + "positions_all.json", encoding="utf-8"))
if isinstance(POS, dict): POS = POS.get("positions") or list(POS.values())
META = json.load(open(R + "games_meta.json", encoding="utf-8"))
S = json.load(open(R + "runs_forced/forced_summary.json", encoding="utf-8"))
items = S if isinstance(S, list) else (S.get("positions") or S.get("rows") or list(S.values()))
notes = {}
def walk(o):
    if isinstance(o, dict):
        if "id" in o and "note" in o:
            notes[o["id"]] = (o.get("note"), o.get("next_choice_km3"), len(o.get("force") or []))
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(S)
print("forced notes (cuts):")
for k, v in notes.items():
    if v[0]:
        print("  ", k, v)
LED = {}
print()
# every position whose turn has a play of his that mentions promote (own) mid-turn, before the attack
for p in POS:
    g = p["game"]
    if g not in LED:
        L = json.load(open(Q + META[g]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
        LED[g] = {t["turn_number"]: t for t in L["turns"]}
    t = LED[g].get(p["turn_count"])
    hits = []
    for pl in (t or {}).get("plays_in_order") or []:
        txt = " ".join(str(pl.get(k) or "") for k in ("kind", "card_name", "target", "result", "response"))
        if re.search(r"promot", txt, re.I) and str(pl.get("kind")) != "attack":
            hits.append((pl.get("order"), pl.get("kind"), pl.get("card_name"), pl.get("target"), pl.get("result")))
    if hits:
        print(p["id"], "plan:", " > ".join(p["his_plan"]), "| truncated_at:", p["plan_truncated_at"])
        for h in hits:
            print("     ", h)
