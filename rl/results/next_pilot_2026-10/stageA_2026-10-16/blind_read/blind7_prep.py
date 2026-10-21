"""Prepare the blind second reader's folder for item 7's seven pending turns: the positions, his recorded moves, km3's 12 plans, the card
texts of every card that appears, and his plan in his own words. No first read, no EXPECTED classes, no case labels: the turns are T1-T7
in an order that is not the case order, and the folder holds nothing else."""
import json, os, random, subprocess, sys

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
OUT = "/home/dacz8976/blind7"
V = f"{REPO}/rl/results/pause_games_new_2026-10-13/v2"
TURNS = ["KW-261012_210041000-t06", "KW-261012_203719000-t07", "KW-261012_210823000-t08", "KW-261012_010706000-t11",
         "KW-261013_010837000-t05", "KW-261013_014423000-t03", "KW-261012_203719000-t11"]
order = TURNS[:]
random.Random(20_000_000_917).shuffle(order)          # a fixed shuffle, so the case order does not show through
os.makedirs(OUT, exist_ok=True)
P = {p["id"]: p for p in json.load(open(f"{V}/positions_all.json"))}
KEEP = ["me", "opp", "points", "stadium", "turn_count", "turn_effects", "his_plan", "his_plan_ended", "his_turn", "approximate", "approximate_reason"]
names = set()
packet = []
for k, tid in enumerate(order, 1):
    p = P[tid]
    pos = {key: p[key] for key in KEEP if key in p}
    km = []
    for line in open(f"{V}/runs_km3/out_{tid}.jsonl"):
        j = json.loads(line)
        if j.get("kind") == "free":
            km.append({"seed": j["seed"], "plan": j.get("plan"), "cut": j.get("cut")})
    packet.append({"turn": f"T{k}", "position": pos, "km3_plans_12_seeds": km})
    def walk(o):
        if isinstance(o, dict):
            for key, v in o.items():
                if key in ("card",) and isinstance(v, str):
                    names.add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, str) and any(ch.isdigit() for ch in v[-4:]) and " " in v:
                    names.add(v)
                walk(v)
    walk(pos)
json.dump(packet, open(f"{OUT}/turns.json", "w"), indent=1)
# card texts: every card string seen (with its set id), through lib/card.py
texts = []
import re
for n in sorted(names):
    m = re.fullmatch(r"(.+?) (\S+ \d+)", n)
    if not m or ":" in n or "@" in n:          # move labels such as "Tool:Heavy Helmet@1" are not cards
        continue
    r = subprocess.run([sys.executable, f"{REPO}/lib/card.py", m.group(2)], capture_output=True, text=True, cwd=REPO)
    out_text = (r.stdout or r.stderr).strip()
    if "0 printings" in out_text:
        r = subprocess.run([sys.executable, f"{REPO}/lib/card.py", m.group(1)], capture_output=True, text=True, cwd=REPO)
        out_text = (r.stdout or r.stderr).strip()
    texts.append(f"### {n}\n{out_text}\n")
for n in ["Kingambit", "Pawniard", "Bisharp", "Glimmora", "Glimmet", "Alolan Muk", "Alolan Grimer", "Regigigas", "Ilima", "Lucky Ice Pop",
          "Heavy Helmet", "Rare Candy", "Copycat", "Mesagoza", "Poké Ball", "Professor's Research"]:
    r = subprocess.run([sys.executable, f"{REPO}/lib/card.py", n], capture_output=True, text=True, cwd=REPO)
    texts.append(f"### {n}\n{(r.stdout or r.stderr).strip()}\n")
open(f"{OUT}/cards.md", "w").write("\n".join(texts))
open(f"{OUT}/his_list.txt", "w").write(open(f"{REPO}/decks/dustin/01-kingambit-as-played.txt", encoding="utf-8").read())
print("order (kept by the laptop, not in the folder):", {f"T{k}": t for k, t in enumerate(order, 1)})
print(len(names), "card strings;", os.listdir(OUT))
