import json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from kx_scan import positions, read_out, read_trace, KX, KM
from kx_detail import norm

tot = collections.Counter()
for pid, p in positions.items():
    tr = read_trace(f'{KX}/err_{pid}.txt')
    if not tr:
        continue
    _, kxp = read_out(f'{KX}/out_{pid}.jsonl')
    his = p.get('his_plan', [])
    for s in sorted(tr):
        for step, t in tr[s]:
            tot['decisions'] += 1
            if t['changed']:
                tot['changed'] += 1
                cands = {norm(c['move']): c for c in t['candidates']}
                ch = cands.get(norm(t['chosen']))
                plan = kxp.get(s, ([], ''))[0]
                print(f"{pid:15s} s{s} step{step} km={norm(t['km_move'])} -> {norm(t['chosen'])} lead={ch['diff']:+.3f} se={ch['se']:.3f} z={ch['diff']/ch['se'] if ch['se'] else 0:.1f} score={ch['score']:.3f} | his={his[:4]} | approx={p.get('approximate')} exact={p.get('exact_list')}")
print(tot)
