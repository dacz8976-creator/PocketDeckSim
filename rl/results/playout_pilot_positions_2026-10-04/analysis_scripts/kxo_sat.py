import json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from kx_scan import positions, read_trace, KX

agg = collections.defaultdict(collections.Counter)
for pid, p in positions.items():
    tr = read_trace(f'{KX}/err_{pid}.txt')
    if not tr:
        continue
    grp = pid.split('-')[0]
    if grp == 'B':
        grp = 'B-' + p.get('decision_maker', '?') + ('-210952' if '210952' in pid else '')
    for s in tr:
        for st, t in tr[s]:
            sc = [c['score'] for c in t['candidates']]
            agg[grp]['dec'] += 1
            if len(sc) > 1 and min(sc) == max(sc):
                agg[grp]['all_equal'] += 1
            km = [c for c in t['candidates'] if c['se'] == 0.0 and c['diff'] == 0.0]
            kms = km[0]['score'] if km else None
            if kms is not None and kms >= 0.999:
                agg[grp]['km_move_16of16'] += 1
            if kms is not None and kms <= 0.001:
                agg[grp]['km_move_0of16'] += 1
            if t['changed']:
                agg[grp]['changed'] += 1
for g, c in sorted(agg.items()):
    print(g, dict(c))
