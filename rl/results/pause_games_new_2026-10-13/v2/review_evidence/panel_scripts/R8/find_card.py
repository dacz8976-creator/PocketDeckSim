"""find_card.py SUBSTR [GAME]: positions where a card string (his hand/board/stack/discard, opp board) contains SUBSTR"""
import json, sys
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
q = sys.argv[1]
g = sys.argv[2] if len(sys.argv) > 2 else ''
for p in P:
    if g not in p['id']:
        continue
    hits = []
    for c in p['me']['hand']:
        if q in c:
            hits.append(('hand', c))
    for c in p['me']['discard']:
        if q in c:
            hits.append(('discard', c))
    for i, b in enumerate(p['me']['board']):
        for c in [b['card']] + b.get('behind', []) + b.get('tools', []):
            if q in c:
                hits.append((f'me[{i}]', c))
    for i, b in enumerate(p['opp']['board']):
        for c in [b['card']] + b.get('behind', []) + b.get('tools', []):
            if q in c:
                hits.append((f'opp[{i}]', c))
    if any(q in s for s in p['his_plan']):
        hits.append(('plan', [s for s in p['his_plan'] if q in s]))
    if hits:
        print(p['id'], hits)
