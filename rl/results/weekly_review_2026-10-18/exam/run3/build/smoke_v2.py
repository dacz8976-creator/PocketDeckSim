"""Smoke check of the v2 deck files in v1.6's frozen legal tool (pg_legal_v14, --legal-only: no bot): one synthetic position per deck (a Basic of the
deck Active on both sides, empty hands, turn 3, the line ['EndTurn']); every deck must load and give no position problem. usage: smoke_v2.py DB_JSON"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_helpers as H

E2 = os.path.expanduser('~/exam_v2')
with open(sys.argv[1], encoding='utf-8') as f:
    db = {c['id']: c for e in json.load(f) for c in e.values()}
with open(H.DECKS_JSON, encoding='utf-8') as f:
    decks = json.load(f)['decks']
qs = []
for key, v in sorted(decks.items()):
    with open(os.path.join(E2, 'decks', v['file']), encoding='utf-8') as f:
        names = [l.split(None, 1)[1].strip() for l in f if l[:1].isdigit()]
    basic = next(n for n in names if db.get(' '.join(n.split()[-2:]), {}).get('stage') == 0)
    hp = db[' '.join(basic.split()[-2:])]['hp']
    t = H.deck_energy(key)
    p = H.P('SMOKE', 3, 2, [0, 0], {'hand': [], 'board': [H.B(basic, hp)]}, {'hand_count': 5, 'board': [H.B(basic, hp)]}, ['EndTurn'], key, 'smoke',
            ez_now=t[0], ez_next=t[-1])
    p['id'] = f'SMOKE-{key}'
    for k in ('_draws', '_vpatch'):
        p.pop(k)
    qs.append(p)
tmp = os.path.join(E2, 'build', 'smoke_in.json')
with open(tmp, 'w') as f:
    json.dump(qs, f, ensure_ascii=False)
with open(os.path.join(E2, 'bin', 'decks.args')) as f:
    args = f.read().split()
r = subprocess.run([os.path.expanduser('~/exam/bin/pg_legal_v14'), '--positions', tmp, '--legal-only'] + args, capture_output=True, text=True)
assert 'PGDUMP' not in r.stderr, 'a search ran!'
if r.returncode:
    sys.exit(r.stderr[-2000:])
out = {}
for line in r.stdout.splitlines():
    j = json.loads(line)
    out.setdefault(j['id'], {})[j['kind']] = j
bad = 0
for q in qs:
    o = out.get(q['id'], {})
    probs = o.get('position', {}).get('problems')
    st = o.get('legal', {}).get('stopped')
    ok = o and not probs
    bad += not ok
    print(f"{q['deck']}: {'OK' if ok else 'PROBLEM'} problems={probs} stopped={st!r} energy_zone={o.get('position', {}).get('summary', {}).get('me', {}).get('energy_zone')}")
os.remove(tmp)
sys.exit(1 if bad else 0)
