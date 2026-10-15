import json, re, sys
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness")
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
P = Q + "BATCH_2026-10-13_NEWEST_TWO/20261013_030351000_iOS/"
led = json.load(open(P + "TURN_LEDGER.json", encoding="utf-8"))
print(led.keys() if isinstance(led, dict) else type(led))
def opp_side(b):
    return (b or {}).get('opponent') or (b or {}).get('opp') or {}
for t in led['turns']:
    tn = t.get('turn_number'); who = t.get('who_played')
    # opponent's board Darkrai entries
    for key in ('board_at_start', 'board_after'):
        b = t.get(key) or {}
        for side in b:
            sd = b[side]
            if not isinstance(sd, dict):
                continue
            pk = [sd.get('active')] + list(sd.get('bench_in_position_order') or [])
            for p in pk:
                if isinstance(p, dict) and 'Darkrai' in str(p.get('name')):
                    print(tn, who, key, side, {k: p.get(k) for k in ('name', 'variant', 'hp_now', 'hp_max', 'hp_max_basis', 'tool', 'special_conditions')})
    for p in t.get('plays_in_order') or []:
        s = json.dumps(p, ensure_ascii=False)
        if re.search(r'Darkrai|Bad Dreams|Dark Slumber|Shadow Cage|Starting Plains', s):
            print(tn, who, 'PLAY', {k: p.get(k) for k in ('kind', 'card_name', 'target', 'result', 'details')})
    for ev in t.get('automatic_events_in_order') or []:
        s = json.dumps(ev, ensure_ascii=False)
        if re.search(r'Darkrai|Bad Dreams|Dark Slumber|Shadow Cage|Druddigon', s):
            print(tn, who, 'EVENT', s[:600])
import cardlib as C
print([ (c['id'], c.get('hp')) for c in C.BYNAME.get('Darkrai', [])])
print(C.BYID.get('B2 154'))
