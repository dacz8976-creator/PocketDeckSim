import json
R = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/'
P = json.load(open(R + 'positions_all.json', encoding='utf-8'))
for p in P:
    if '012303' in p['id'] or '013009' in p['id']:
        print('=====', p['id'], 'deck', p['deck'], 'points', p['points'])
        print('  hand', p['me']['hand'])
        print('  board', [(b['card'], b['hp'], b.get('energy'), b.get('behind')) for b in p['me']['board']])
        print('  opp', [(b['card'], b['hp'], b.get('energy'), b.get('tools')) for b in p['opp']['board']])
        print('  discard', p['me']['discard'])
        print('  stadium', p['stadium'])
        print('  plan', p['his_plan'])
        print('  notes', p['notes'][:400])
rep = json.load(open(R + 'report_convert.json', encoding='utf-8'))
for k in ('left_out', 'plans_with_unresolved_targets'):
    for s in rep[k]:
        if '012303' in str(s['game']) or '013009' in str(s['game']):
            print(k, s)
# any other position with Conkeldurr
print('---- other positions holding Conkeldurr')
for p in P:
    allc = p['me']['hand'] + [b['card'] for b in p['me']['board']] + [x for b in p['me']['board'] for x in b.get('behind', [])] + p['me']['discard']
    c = [x for x in allc if 'Conkeldurr' in x]
    if c:
        print(p['id'], p['deck'], c)
