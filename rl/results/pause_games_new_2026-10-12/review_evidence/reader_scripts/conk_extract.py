import json, sys, re
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES/'
for g in ['20261010_012303000_iOS', '20261010_013009000_iOS']:
    led = json.load(open(BASE + g + '/TURN_LEDGER.json', encoding='utf-8'))
    print('#####', g, 'turns', len(led['turns']))
    for t in led['turns']:
        who = t.get('who_played')
        tn = t.get('turn_number')
        print('--- turn', tn, who)
        if str(who).startswith('owner'):
            hs = t.get('hand_at_start') or {}
            print('  hand_at_start count', hs.get('count'), 'cards', hs.get('cards_left_to_right'))
        for side in ('owner', 'opponent'):
            b = (t.get('board_at_start') or {}).get(side) or {}
            act = b.get('active')
            def s(p):
                if not p: return None
                return (p.get('name'), p.get('variant'), p.get('hp_now'), p.get('hp_max'), (p.get('attached_energy') or {}).get('by_type'), p.get('tool'))
            print('  start', side, 'pts', b.get('points'), 'active', s(act))
            for p in b.get('bench_in_position_order') or []:
                print('     bench', p.get('bench_position'), s(p))
        st = (t.get('board_at_start') or {}).get('stadium')
        print('  stadium', st)
        for i, p in enumerate(t.get('plays_in_order') or []):
            print('  play', i, p.get('kind'), '|', p.get('card_name'), '|', p.get('target'), '|', str(p.get('result'))[:300])
