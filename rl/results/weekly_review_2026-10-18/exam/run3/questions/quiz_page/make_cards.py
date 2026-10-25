"""Card text for the quiz page: every printing in play, plus Tools, Stadiums and hand cards by name.
Reads the engine's card database (main) and QUESTIONS.json; writes a compact map for the page."""
import json, re, sys, hashlib
dbp, qp, out = sys.argv[1], sys.argv[2], sys.argv[3]
db = json.load(open(dbp, encoding='utf-8'))
q = json.load(open(qp, encoding='utf-8'))

def compact(entry):
    if 'Pokemon' in entry:
        p = entry['Pokemon']
        return {'kind': 'Pokemon', 'name': p['name'], 'type': p.get('energy_type'), 'hp': p.get('hp'), 'stage': p.get('stage'),
                'from': p.get('evolves_from'), 'weak': p.get('weakness'), 'retreat': p.get('retreat_cost') or [],
                'ability': p.get('ability'),
                'attacks': [{'cost': a.get('energy_required') or [], 'name': a.get('title'), 'dmg': a.get('fixed_damage'), 'text': a.get('effect')}
                            for a in (p.get('attacks') or [])]}
    t = entry.get('Trainer')
    if t:
        return {'kind': t.get('trainer_card_type'), 'name': t['name'], 'text': t.get('effect')}
    return None

by_id, by_name = {}, {}
for e in db:
    c = compact(e)
    if not c:
        continue
    inner = e.get('Pokemon') or e.get('Trainer')
    by_id[inner['id']] = c
    key = json.dumps({k: v for k, v in c.items()}, sort_keys=True, ensure_ascii=False)
    by_name.setdefault(c['name'], {})[key] = c

def norm(n):
    return n.replace('’', "'").strip()

ids, names, missing = set(), set(), []
def mons(pos):
    for side in ('dustin', 'opponent'):
        s = pos.get(side) or {}
        for m in [s.get('active')] + list(s.get('bench') or []):
            if m:
                yield m

def take(pos):
    for m in mons(pos):
        pr = str(m.get('printing') or '')
        mm = re.search(r'(\S+ \d+)$', pr)
        if mm and mm.group(1) in by_id:
            ids.add(mm.group(1))
        else:
            missing.append(('printing', pr))
            names.add(norm(m.get('card', '')))
        for t in m.get('tools') or []:
            names.add(norm(str(t)))
    st = pos.get('stadium')
    if isinstance(st, dict):
        names.add(norm(str(st.get('card') or st.get('name') or '')))
    elif st:
        names.add(norm(str(st)))
    for h in (pos.get('dustin') or {}).get('hand') or []:
        names.add(norm(re.sub(r'\s*\([^)]*\)\s*$', '', str(h))))

for x in q['questions']:
    take(x['position'])
    for a in x.get('also_applies_to') or []:
        take(a['position'])

cards = {'by_id': {i: by_id[i] for i in sorted(ids)}, 'by_name': {}}
ambiguous = []
for n in sorted(names):
    if not n:
        continue
    vs = list(by_name.get(n, {}).values())
    if len(vs) == 1:
        cards['by_name'][n] = vs[0]
    elif not vs:
        missing.append(('name', n))
    else:
        inplay = [by_id[i] for i in ids if by_id[i]['name'] == n]
        if inplay:
            cards['by_name'][n] = inplay[0]
        else:
            ambiguous.append((n, len(vs)))
blob = json.dumps(cards, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
open(out, 'w', encoding='utf-8', newline='\n').write(blob)
print('printings', len(cards['by_id']), '| names', len(cards['by_name']), '| bytes', len(blob))
print('missing', missing)
print('ambiguous (no text shown)', ambiguous)
print('cards sha256', hashlib.sha256(blob.encode('utf-8')).hexdigest())
