import json, re, glob, os
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
P = Q + "BATCH_2026-10-13_NEWEST_TWO/20261013_022530000_iOS/"
led = json.load(open(P + "TURN_LEDGER.json", encoding="utf-8"))
for t in led['turns']:
    tn = t.get('turn_number'); who = t.get('who_played')
    for key in ('board_at_start', 'board_after'):
        sd = ((t.get(key) or {}).get('opponent') or {})
        for p in [sd.get('active')] + list(sd.get('bench_in_position_order') or []):
            if isinstance(p, dict) and re.search(r'Scyther|Scizor', str(p.get('name'))):
                print(tn, who, key, {k: p.get(k) for k in ('name', 'bench_position', 'hp_now', 'hp_max', 'hp_max_basis', 'tool', 'damage')})
    for p in t.get('plays_in_order') or []:
        s = json.dumps(p, ensure_ascii=False)
        if re.search(r'Cape|Scizor', s):
            print(tn, who, 'PLAY', {k: p.get(k) for k in ('kind', 'card_name', 'target', 'result', 'details')})
    for ev in t.get('automatic_events_in_order') or []:
        s = json.dumps(ev, ensure_ascii=False)
        if re.search(r'Cape', s):
            print(tn, who, 'EVENT', s[:400])
s = json.dumps(led, ensure_ascii=False)
print('Elegant in ledger:', 'Elegant' in s, '| Giant Cape count:', s.count('Giant Cape'))
for f in ('REVIEW.md', 'UNCERTAINTIES.json', 'turn_table.txt', 'TURN_EVIDENCE.json', 'SUMMARY.json'):
    try:
        x = open(P + f, encoding='utf-8').read()
    except Exception as e:
        print(f, 'missing'); continue
    for m in re.finditer(r'.{0,150}(Elegant|Cape).{0,150}', x):
        print(f, '::', m.group(0).replace('\n', ' ')[:300])
