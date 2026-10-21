import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, opp_card, instances = C['BYNAME'], C['nname'], C['cid'], C['opp_card'], C['instances']


def desc(c):
    ab = c.get('ability')
    ab = ab.get('title') if isinstance(ab, dict) else None
    return f"{c['id']} hp{c.get('hp')} {c.get('energy_type')} ab={ab} atk=" + ' | '.join(f"{a.get('title')}[{''.join(x[0] for x in a.get('energy_required') or [])}]{a.get('fixed_damage')}" for a in c.get('attacks', [])) + f" ret={len(c.get('retreat_cost') or [])} weak={c.get('weakness')}"


def words(c):
    out = [a.get('title') for a in c.get('attacks', []) if a.get('title')]
    ab = c.get('ability')
    if isinstance(ab, dict) and ab.get('title'):
        out.append(ab['title'])
    return out


wrong = collections.defaultdict(list)
undecided = collections.defaultdict(list)
seen_case = set()
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    for inst, b in zip(instances(t['board_at_start']['opponent']), p['opp']['board']):
        name = nname(inst['name'])
        cands = [c for c in BYNAME.get(name, []) if 'hp' in c]
        if len({json.dumps([c.get('hp'), c.get('attacks'), c.get('ability'), c.get('energy_type'), c.get('retreat_cost'), c.get('weakness')], sort_keys=True) for c in cands}) < 2:
            continue
        vtxt = ' '.join(str(inst.get(k) or '') for k in ('variant', 'printing', 'pokemon_id')).replace('’', "'").lower()
        # better tie-break: printed HP, then any attack/ability title anywhere in the variant text
        pool = [c for c in cands if c.get('hp') == inst.get('hp_max')] or cands
        sc = [(sum(1 for w in words(c) if w.replace('’', "'").lower() in vtxt), c) for c in pool]
        best = max(s for s, _ in sc)
        top = [c for s, c in sc if s == best and best > 0]
        chosen = b['card']
        key = (p['id'], name)
        topsem = {json.dumps([c.get('hp'), c.get('attacks'), c.get('ability'), c.get('energy_type')], sort_keys=True) for c in top}
        chosen_c = [c for c in cands if cid(c) == chosen]
        chosen_sem = json.dumps([chosen_c[0].get('hp'), chosen_c[0].get('attacks'), chosen_c[0].get('ability'), chosen_c[0].get('energy_type')], sort_keys=True) if chosen_c else None
        case = (name, inst.get('hp_max'), str(inst.get('variant')))
        if top and chosen_sem not in topsem:
            wrong[case].append(p['id'])
        elif not top:
            undecided[case].append(p['id'])
        if case not in seen_case:
            seen_case.add(case)
            if (top and chosen_sem not in topsem) or not top or len(topsem) > 1:
                print('CASE', case, 'chosen', chosen, 'printing/pokemon_id', inst.get('printing'), inst.get('pokemon_id'))
                for c in pool:
                    print('    ', desc(c))
print('\n== opponent printing contradicted by the ledger text (another printing names its attack/ability):', sum(len(v) for v in wrong.values()), 'instances,', len({i for v in wrong.values() for i in v}), 'positions')
for k, v in wrong.items():
    print(k, len(v), v)
print('\n== undecidable from the text (no title in the variant):', sum(len(v) for v in undecided.values()), 'instances,', len({i for v in undecided.values() for i in v}), 'positions')
for k, v in undecided.items():
    print(k, len(v), v)
