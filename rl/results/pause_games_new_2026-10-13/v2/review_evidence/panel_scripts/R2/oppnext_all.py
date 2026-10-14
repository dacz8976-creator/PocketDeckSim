"""For every position of the 14 games: was the opponent's energy_next read from the ledger, or did the converter fall back to HIS deck's Energy
(o_next = zone next or zone this_turn at the start of his turn, else decks_energy)? Compare with the previous opponent row's board_after zone next."""
import json, re
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
POS = json.load(open(V2 + "positions_all.json"))
META = json.load(open(V2 + "games_meta.json"))
led_cache = {}
def etype(x):
    return x if x else None
for p in POS:
    g = p["game"]
    if g not in led_cache:
        led_cache[g] = json.load(open(QA + META[g]["folder"] + "/TURN_LEDGER.json", encoding="utf-8"))
    L = led_cache[g]
    tn = p["turn_count"]
    T = {t["turn_number"]: t for t in L["turns"]}
    t = T.get(tn)
    oz = ((t.get("board_at_start") or {}).get("opponent") or {}).get("energy_zone") or {}
    start_next = (oz.get("next") or {}).get("type")
    start_now = (oz.get("this_turn") or {}).get("type")
    prev = T.get(tn - 1)
    prev_next = None
    if prev:
        pz = ((prev.get("board_after") or {}).get("opponent") or {}).get("energy_zone") or {}
        prev_next = (pz.get("next") or {}).get("type")
    nxt = T.get(tn + 1)
    next_now = None
    if nxt:
        nz = ((nxt.get("board_at_start") or {}).get("opponent") or {}).get("energy_zone") or {}
        next_now = (nz.get("this_turn") or {}).get("type")
    val = p["opp"].get("energy_next")
    src = "start.next" if start_next else ("start.now" if start_now else "FALLBACK(his deck)")
    flag = ""
    if src.startswith("FALLBACK"):
        flag = "<-- fallback"
    if (prev_next and val != prev_next) or (next_now and val != next_now):
        flag += " <-- differs from ledger neighbours"
    if flag or "203719" in p["id"] or "225319" in p["id"]:
        print(f"{p['id']}: opp energy_next={val} | src={src} | start.next={start_next} start.now={start_now} | prev opp row after.next={prev_next} | next opp row start.now={next_now} {flag}")
