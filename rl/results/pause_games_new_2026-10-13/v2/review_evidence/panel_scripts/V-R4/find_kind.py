import json, sys, glob
for f in sys.argv[1:]:
    led = json.load(open(f, encoding='utf-8'))
    for t in led['turns']:
        for p in t.get('plays_in_order') or []:
            if str(p.get('kind')) == 'stadium_activation':
                print(f.split('/')[-2], 'turn', t.get('turn_number'), t.get('who_played'), 'order', p.get('order'), p.get('card_name'), '|', p.get('result'))
        if str(t.get('who_played', '')).startswith('owner') and t.get('turn_number') in (13, 14, 15):
            pass
