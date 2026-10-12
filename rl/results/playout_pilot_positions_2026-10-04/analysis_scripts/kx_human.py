import json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from kx_scan import positions, read_out, read_trace, KX, KM
from kx_detail import norm

def same(a, b):
    # loose match: ignore bench slot on Place
    a2 = re.sub(r'(Place:[^@]+)@\d+', r'\1', a)
    b2 = re.sub(r'(Place:[^@]+)@\d+', r'\1', b)
    return a2 == b2

pref = sys.argv[1].split(',') if len(sys.argv) > 1 else ['B-']
for pid, p in positions.items():
    if not any(pid.startswith(x) for x in pref):
        continue
    tr = read_trace(f'{KX}/err_{pid}.txt')
    if not tr:
        continue
    his = p.get('his_plan', [])
    if not his:
        continue
    h0 = his[0]
    rows = []
    for s in sorted(tr):
        st0 = [t for st, t in tr[s] if st == 0]
        if not st0:
            continue
        t = st0[0]
        km = norm(t['km_move']); ch = norm(t['chosen'])
        hc = [c for c in t['candidates'] if same(norm(c['move']), h0)]
        kmc = [c for c in t['candidates'] if c['diff'] == 0.0 and c['se'] == 0.0 and same(norm(c['move']), km)]
        kms = kmc[0]['score'] if kmc else None
        if hc:
            c = hc[0]
            rows.append(f"s{s}: his {h0} {c['score']:.3f} (vs km {c['diff']:+.3f} se {c['se']:.3f}) km={km} {kms} chosen={ch}")
        else:
            rows.append(f"s{s}: his {h0} NOT AMONG CANDIDATES; km={km} chosen={ch} n={len(t['candidates'])}")
    print(pid, p.get('decision_maker'))
    for r in rows:
        print('   ', r)
