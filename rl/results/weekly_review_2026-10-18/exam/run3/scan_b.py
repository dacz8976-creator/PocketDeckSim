"""Rule B scan: accepted alternatives that move a deterministic action before the chance step his line played earlier (loose multiset, slots ignored)."""
import json, re, sys
sys.path.insert(0, '/home/dacz8976/exam_v2/build')
import v2_helpers as H
from label_adapter import to_judge
d = json.load(open(sys.argv[1]))


def loose(l):
    j = to_judge(l).split('#')[0]
    return re.sub(r'@\d+', '', re.sub(r'^Retreat:\d+', 'Retreat', j))


for p in d['points']:
    a, pos = p['answer'], p['position']
    try:
        hc = H.chance_steps(a['his_move'], pos)
    except H.Uncertain:
        continue
    if not hc:
        continue
    h0 = min(hc)
    for x in a['acceptable']:
        if x.get('source') == 'chance-first rule':
            continue
        try:
            ac = H.chance_steps(x['line'], pos)
        except H.Uncertain:
            continue
        if not ac:
            continue
        a0 = min(ac)
        same = sorted(map(loose, x['line'])) == sorted(map(loose, a['his_move']))
        if same and a0 > h0:
            print('CANDIDATE', p['id'], '| his', a['his_move'], '| alt', x['line'], '|', x.get('source', 'first pass'), '|', (x.get('reason') or '')[:150])
