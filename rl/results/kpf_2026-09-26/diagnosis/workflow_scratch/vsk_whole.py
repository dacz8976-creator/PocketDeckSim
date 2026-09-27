"""Whole-game Vespiquen-turn statistics, kp3 vs kpf traces, split by worse/better."""
import json, pickle, re
from collections import Counter, defaultdict
from vsk_slots import simulate
from vsk_lib import parse_board
from vsk_stats import fisher_two_sided

T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
div = json.load(open("vsk_div.json"))
MAIN = {"Vespiquen ex", "Teal Mask Ogerpon ex"}
COST = {"Vespiquen ex": 2, "Teal Mask Ogerpon ex": 2, "Shuckle ex": 1, "Combee": 1}

agg = defaultdict(Counter)
per_game = []
for r in div:
    seat = r["seat"]
    pg = {"kind": r["kind"], "seed": r["seed"]}
    for key in ("base", "kpf"):
        tr = T[key][r["seed"]][r["trace"]]
        turns = sorted({L["turn"] for L in tr if L["tomove"] == seat and L["turn"] > 0})
        c = Counter()
        for t in turns:
            idx = [n for n, L in enumerate(tr) if L["turn"] == t]
            if tr[idx[0]]["tomove"] != seat:
                continue
            b0 = parse_board(tr[idx[0]]["s"][seat])
            if b0["zc"] == "None":
                continue
            c["zone_turns"] += 1
            acts = [tr[n]["act"] for n in idx if tr[n]["actor"] == seat]
            atk = [re.search(r'title: "([^"]+)"', a).group(1) for a in acts if a.startswith("Attack(")]
            if atk:
                c["attack_turns"] += 1
                c["atk_" + atk[0]] += 1
            later = [n for n in range(idx[-1], len(tr)) if tr[n]["turn"] > t]
            if later:
                be = parse_board(tr[later[0]]["s"][seat])
                a = be["active"]
                if a:
                    c["end_" + a["name"]] += 1
                    if a["name"] in MAIN and len(a["E"]) < 2 and not atk:
                        c["unready_main_front_noatk"] += 1
                    c["end_turns"] += 1
        pg[key] = c
        for k, v in c.items():
            agg[(key, r["kind"])][k] += v
            agg[(key, "all")][k] += v
    per_game.append(pg)

for kind in ("all", "worse", "better"):
    print(f"== {kind}")
    for key in ("base", "kpf"):
        c = agg[(key, kind)]
        z = c["zone_turns"]; e = c["end_turns"]
        print(f"  {key:4s} zone turns {z:4d} attack rate {c['attack_turns'] / z:.3f}  TripleSlap {c['atk_Triple Slap']:4d} ChaseOrder {c['atk_Chase Order']:4d} "
              f"EnergizedLeaves {c['atk_Energized Leaves']:4d} Reckless {c['atk_Reckless Charge']:4d} | end Shuckle {c['end_Shuckle ex'] / e:.3f} "
              f"unready main front no atk {c['unready_main_front_noatk'] / e:.3f}")
# per game difference in attack rate, worse vs better
import statistics as st
for kind in ("worse", "better"):
    d = [ (g["kpf"]["attack_turns"] / max(1, g["kpf"]["zone_turns"])) - (g["base"]["attack_turns"] / max(1, g["base"]["zone_turns"])) for g in per_game if g["kind"] == kind]
    d2 = [g["kpf"]["atk_Triple Slap"] - g["base"]["atk_Triple Slap"] for g in per_game if g["kind"] == kind]
    d3 = [g["kpf"]["unready_main_front_noatk"] - g["base"]["unready_main_front_noatk"] for g in per_game if g["kind"] == kind]
    print(f"{kind}: mean per-game change in attack rate {st.mean(d):+.3f} (sd {st.stdev(d):.3f}); TripleSlap change {st.mean(d2):+.2f}; unready-front change {st.mean(d3):+.2f}; "
          f"games with fewer TS {sum(x < 0 for x in d2)}, more {sum(x > 0 for x in d2)}")
