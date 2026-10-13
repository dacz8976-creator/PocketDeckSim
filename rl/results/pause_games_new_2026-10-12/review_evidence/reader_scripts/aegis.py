import json, re
QA = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
R = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/'
P = json.load(open(R + 'positions_all.json', encoding='utf-8'))
NAMES = ('Aegislash', 'Honedge', 'Doublade')
for g in ['20261005_033529000_iOS', '20261005_034953000_iOS']:
    led = json.load(open(QA + g + '/TURN_LEDGER.json', encoding='utf-8'))
    print('#####', g)
    d = json.load(open(QA + g + '/DECK_USED.json', encoding='utf-8'))
    for k, v in d.items():
        if isinstance(v, list):
            for x in v:
                if isinstance(x, dict) and any(n in str(x.get('name')) for n in NAMES):
                    print('  DECK', k, {kk: x.get(kk) for kk in ('name', 'variant', 'count', 'entity_id', 'printing_aliases')})
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, list):
                    for x in v2:
                        if isinstance(x, dict) and any(n in str(x.get('name')) for n in NAMES):
                            print('  DECK', k + '.' + k2, {kk: x.get(kk) for kk in ('name', 'variant', 'count', 'entity_id', 'printing_aliases')})
    for t in led['turns']:
        who = str(t.get('who_played'))
        tn = t.get('turn_number')
        if who.startswith('owner'):
            hs = t.get('hand_at_start') or {}
            for c in hs.get('cards_left_to_right') or []:
                nm = c.get('name') if isinstance(c, dict) else c
                vr = c.get('variant') if isinstance(c, dict) else None
                if any(n in str(nm) for n in NAMES):
                    print('  t', tn, 'HAND', nm, '|', vr)
        b = (t.get('board_at_start') or {}).get('owner') or {}
        ps = [b.get('active')] + list(b.get('bench_in_position_order') or [])
        for p in ps:
            if p and any(n in str(p.get('name')) for n in NAMES):
                print('  t', tn, who[:5], 'BOARD', p.get('name'), '|', p.get('variant'), '| hp', p.get('hp_now'), '/', p.get('hp_max'))
        if who.startswith('owner'):
            for i, p in enumerate(t.get('plays_in_order') or []):
                s = json.dumps(p, ensure_ascii=False)
                if any(n in s for n in NAMES) or 'Superb' in s or 'Slicing' in s or 'Cursed' in s or 'Pierce' in s or 'Cut Up' in s or 'Dual Blades' in s or 'Slash' in s:
                    print('  t', tn, 'PLAY', i, p.get('kind'), '|', p.get('card_name'), '|', p.get('target'), '|', str(p.get('result'))[:200])
    short = g.replace('_iOS', '')[2:]
    for p in P:
        if p['deck'] == 'KW' + short:
            allc = [('hand', x) for x in p['me']['hand']] + [('board', b['card']) for b in p['me']['board']] + [('behind', x) for b in p['me']['board'] for x in b.get('behind', [])] + [('disc', x) for x in p['me']['discard']]
            c = [x for x in allc if any(n in x[1] for n in NAMES)]
            print('  POS', p['id'], c, 'plan', p['his_plan'])
