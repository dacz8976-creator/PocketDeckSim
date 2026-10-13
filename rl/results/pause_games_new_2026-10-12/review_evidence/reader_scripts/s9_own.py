import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, instances, load_deck = C['BYNAME'], C['nname'], C['cid'], C['instances'], C['load_deck']


def fsem(c):
    return json.dumps([c.get('hp'), c.get('attacks'), c.get('ability'), c.get('energy_type'), c.get('retreat_cost'), c.get('weakness'), c.get('evolves_from'), c.get('stage')], sort_keys=True)


def words(c):
    out = [a.get('title') for a in c.get('attacks', []) if a.get('title')]
    ab = c.get('ability')
    if isinstance(ab, dict) and ab.get('title'):
        out.append(ab['title'])
    return out


# (b) per deck: names with more than one entity id / variant in the source list
print('== names listed with more than one id in DECK_USED (source key used by the converter)')
for g in GAMES:
    try:
        d = deck(g)
        cards, energy, src = load_deck(d)
    except Exception as e:
        continue
    if cards is None:
        continue
    # find the raw list
    raw = None
    if src in d:
        raw = d[src]
    else:
        k1, k2 = src.split('.', 1)
        raw = d[k1][k2]
    ids = collections.defaultdict(collections.Counter)
    for x in raw:
        if isinstance(x, dict):
            key = tuple(str(x.get(k)) for k in ('variant', 'semantic_entity_id', 'entity_id', 'functional_ids', 'printing', 'id') if x.get(k) is not None)
            ids[nname(x.get('name'))][key] += int(x['count']) if isinstance(x.get('count'), int) and 'position' not in x else 1
    for n, c in ids.items():
        if len(c) > 1:
            print('  ', short_of(g), src, n, dict(c))

# (c) every own Pokemon instance in every position vs the ledger's hp_max and variant text
print('\n== own Pokemon whose position card disagrees with the ledger (hp_max, or a title in the variant text that the chosen card lacks and another printing has)')
bad = collections.defaultdict(list)
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    for inst, pb in zip(instances(t['board_at_start']['owner']), p['me']['board']):
        n = pb['card'].rsplit(' ', 2)[0]
        ch = [c for c in BYNAME[n] if cid(c) == pb['card']][0]
        cands = [c for c in BYNAME[n] if 'hp' in c]
        why = []
        if inst.get('hp_max') is not None and ch.get('hp') != inst['hp_max'] and any(c.get('hp') == inst['hp_max'] for c in cands):
            why.append(f"hp_max {inst['hp_max']} != printed {ch.get('hp')}")
        vt = ' '.join(str(inst.get(k) or '') for k in ('variant', 'printing', 'pokemon_id')).replace('’', "'").lower()
        others = {w for c in cands if fsem(c) != fsem(ch) for w in words(c)} - set(words(ch))
        hitw = [w for w in others if re.search(r'(?<![a-z])' + re.escape(w.lower()) + r'(?![a-z])', vt)]
        if hitw:
            why.append(f'variant names {hitw}')
        if why:
            bad[(short, n, pb['card'], '; '.join(why), str(inst.get('variant'))[:60])].append(p['id'])
for k, v in bad.items():
    print('  ', k, len(v), v)
print('positions touched', len({i for v in bad.values() for i in v}))
