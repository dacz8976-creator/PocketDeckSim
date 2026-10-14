import json
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
d = json.load(open(P, encoding="utf-8"))
DRAW = ("Play:Professor's Research", "Play:Copycat", "Play:Lisia", "Play:Clemont", "Play:Sightseer", "Play:Order Pad", "Play:Team Rocket's Researcher", "Play:Quick-Grow Extract")
def is_draw(l):
    return l in DRAW or l.startswith('Play:Poké Ball') or l.startswith('Play:Poke Ball') or l == 'Play:Sabrina'
print("== Giga Turbo plans")
for p in d:
    plan = p.get("his_plan") or []
    if any("Giga Turbo" in s for s in plan):
        gi = [i for i, s in enumerate(plan) if "Giga Turbo" in s][0]
        before_draw = not any(is_draw(s) for s in plan[:gi])
        print(p["id"], plan, "| attack before any draw:", before_draw, "| next:", plan[gi + 1:gi + 2])
print("== Starting Plains positions")
for p in d:
    st = p.get("stadium") or {}
    if st and "Starting Plains" in st.get("card", ""):
        dmg = []
        for side in ("me", "opp"):
            for i, b in enumerate(p[side]["board"]):
                dmg.append((side, i, b["card"], b["hp"]))
        print(p["id"], dmg)
# also older Oct 12 positions
import os, glob
for f in glob.glob("/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/**/positions*.json", recursive=True):
    try:
        dd = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        continue
    if not isinstance(dd, list):
        continue
    n = [p["id"] for p in dd if isinstance(p, dict) and "Starting Plains" in json.dumps(p.get("stadium"), ensure_ascii=False)]
    g = [p["id"] for p in dd if isinstance(p, dict) and any("Giga Turbo" in s for s in (p.get("his_plan") or []))]
    print(f, "SP:", n, "GT:", g)
