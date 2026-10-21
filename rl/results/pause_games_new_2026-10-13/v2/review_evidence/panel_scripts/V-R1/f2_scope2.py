import json, collections
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
meta = json.load(open(V2 + 'games_meta.json', encoding='utf-8'))
pos = {p['id']: p for p in json.load(open(V2 + 'positions_all.json', encoding='utf-8'))}
for g in ('kw-261012_203719000', 'kw-261013_010003000', 'kw-261012_010706000'):
    L = json.load(open(QA + meta[g]['folder'] + '/TURN_LEDGER.json', encoding='utf-8'))
    print('#' * 20, g)
    for t in L['turns']:
        tn = t.get('turn_number')
        who = str(t.get('who_played'))
        oz = (((t.get('board_at_start') or {}).get('opponent') or {}).get('energy_zone') or {})
        oza = (((t.get('board_after') or {}).get('opponent') or {}).get('energy_zone') or {})
        pid = 'KW-' + g[3:] + '-t%02d' % tn
        pv = pos[pid]['opp']['energy_next'] if pid in pos else '-'
        print(tn, who[:8], '| start this', (oz.get('this_turn') or {}).get('type'), 'next', (oz.get('next') or {}).get('type'),
              '| after this', (oza.get('this_turn') or {}).get('type'), 'next', (oza.get('next') or {}).get('type'), '| pos opp.energy_next', pv if who.startswith('owner') else '')
