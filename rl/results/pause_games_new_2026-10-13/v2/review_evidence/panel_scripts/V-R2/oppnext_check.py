import json, collections
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
POS = json.load(open(R + "positions_all.json", encoding="utf-8"))
if isinstance(POS, dict):
    POS = POS.get("positions") or list(POS.values())
META = json.load(open(R + "games_meta.json", encoding="utf-8"))
ET = {"fire": "Fire", "lightning": "Lightning", "darkness": "Darkness", "water": "Water", "grass": "Grass",
      "psychic": "Psychic", "fighting": "Fighting", "metal": "Metal", "colorless": None}
def et(x):
    if not x:
        return None
    return ET.get(str(x).strip().lower(), str(x))
def zone(row, when, side):
    z = (((row or {}).get(when) or {}).get(side) or {}).get("energy_zone") or {}
    return et((z.get("this_turn") or {}).get("type")), et((z.get("next") or {}).get("type")), (z.get("this_turn") or {}).get("visibility"), (z.get("next") or {}).get("visibility")
ledgers = {}
stats = collections.Counter()
for p in POS:
    g = p["game"]
    if g not in ledgers:
        L = json.load(open(Q + META[g]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
        ledgers[g] = {t["turn_number"]: t for t in L["turns"]}
    T = ledgers[g]
    tn = p["turn_count"]
    row = T.get(tn)
    s_this, s_next, v1, v2 = zone(row, "board_at_start", "opponent")
    fallback = not s_next and not s_this
    prev_after = zone(T.get(tn - 1), "board_after", "opponent") if T.get(tn - 1) else None
    own_after = zone(row, "board_after", "opponent")
    nxt_start = zone(T.get(tn + 1), "board_at_start", "opponent") if T.get(tn + 1) else None
    # opp attachments in tn+1
    att = []
    for pl in (T.get(tn + 1) or {}).get("plays_in_order") or []:
        if str(pl.get("kind")).lower().startswith("energy") and (pl.get("energy") or {}).get("type"):
            att.append(et(pl["energy"]["type"]))
    truth_cands = [x for x in [prev_after[1] if prev_after else None, own_after[1], nxt_start[0] if nxt_start else None] if x]
    val = p["opp"]["energy_next"]
    flag = ""
    if truth_cands and val not in truth_cands:
        flag = "MISMATCH"
    if fallback:
        stats["fallback"] += 1
    stats[flag or "ok"] += 1
    if fallback or flag:
        print(p["id"], "pos:", val, "| start this/next:", s_this, s_next, v1, v2, "| prev_after next:", prev_after[1] if prev_after else "-",
              "| own_after next:", own_after[1], "| next_start this:", nxt_start[0] if nxt_start else "-", "| opp attaches t+1:", att, flag)
print(stats)
