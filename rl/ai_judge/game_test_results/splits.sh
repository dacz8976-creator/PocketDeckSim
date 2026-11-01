#!/bin/bash
# Descriptive splits as paired counts (Gemini-only wins, kx3-only wins, same result, mean D), for RESULTS.md.
Z=/home/dacz8976/relplan/gemini/stage2
python3 -I - "$Z/run" > "$Z/score/splits.txt" 2>&1 <<'PY'
import json, os, sys
d = sys.argv[1]
arms = {}
for l in open(os.path.join(d, 'games.jsonl')):
    if l.strip():
        a = json.loads(l); arms[a['deal_tag']] = a
rows = []
for l in open(os.path.join(d, 'deals.jsonl')):
    if not l.strip():
        continue
    dl = json.loads(l)
    seat = dl['bits']['seat']
    w = {}
    for arm, tag in (('G', dl['g_deal_tag']), ('K', dl['k_deal_tag'])):
        r = json.load(open(os.path.join(d, arms[tag]['result_file'])))
        o = r['outcome']
        w[arm] = 1 if isinstance(o, dict) and o.get('Win') == seat else 0
    wf = arms[dl['g_deal_tag']]['judge']['went_first']
    rows.append(dict(dl['bits'], D=w['G'] - w['K'], first=int(wf == seat)))
names = {'deck': ('A, 09-mega-manectric-heliolisk', 'B, 11-archaludon-haxorus-dragonair'), 'list': ('t-lucario', 't-suicune'),
         'policy': ('km3 opponent', 'kx3 opponent'), 'seat': ('pilot in seat 0', 'pilot in seat 1'), 'first': ('pilot went second', 'pilot went first')}
print('split | value | pairs | Gemini-only wins | kx3-only wins | same result | mean D')
for key in ('deck', 'list', 'policy', 'seat', 'first'):
    for v in (0, 1):
        s = [x for x in rows if x[key] == v]
        print('%s | %s | %d | %d | %d | %d | %+.3f' % (key, names[key][v], len(s), sum(1 for x in s if x['D'] == 1),
              sum(1 for x in s if x['D'] == -1), sum(1 for x in s if x['D'] == 0), sum(x['D'] for x in s) / len(s)))
PY
cat "$Z/score/splits.txt"
