import json, re
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/TURN_LEDGER.json"
L = json.load(open(P, encoding='utf-8'))
turns = L['turns']
print('top keys', list(L.keys()))
for t in turns:
    tn = t.get('turn_number')
    who = t.get('who_played')
    print('=' * 90)
    print('TURN', tn, who)
    for bk in ('board_at_start', 'board_after'):
        b = t.get(bk) or {}
        for side in ('owner', 'opponent'):
            s = b.get(side) or {}
            print(f'  {bk}.{side}.energy_zone:', json.dumps(s.get('energy_zone'), ensure_ascii=False))
    for i, p in enumerate(t.get('plays_in_order') or []):
        txt = json.dumps(p, ensure_ascii=False)
        if re.search(r'energy|psychic|darkness|attach|attack', txt, re.I):
            print('  PLAY', i + 1, 'kind', p.get('kind'), '| card', p.get('card_name'), '| target', p.get('target'), '| energy', json.dumps(p.get('energy'), ensure_ascii=False), '| result', p.get('result'), '| nested', p.get('nested_events_in_order'))
    for ev in t.get('automatic_events_in_order') or []:
        print('  AUTO', json.dumps(ev, ensure_ascii=False)[:300])
