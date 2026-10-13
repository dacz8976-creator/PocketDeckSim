import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, load_deck, convert_game = C['BYNAME'], C['nname'], C['cid'], C['load_deck'], C['convert_game']


def fsem(cardid):
    n = cardid.rsplit(' ', 2)[0]
    c = [x for x in BYNAME.get(n, []) if cid(x) == cardid]
    if not c:
        return None
    c = c[0]
    return json.dumps([c.get('hp'), c.get('attacks'), c.get('ability'), c.get('energy_type'), c.get('retreat_cost'), c.get('evolves_from')], sort_keys=True)


def walk(o, path=''):
    if isinstance(o, dict):
        yield path, o
        for k, v in o.items():
            yield from walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f'[{i}]')


bad_total = collections.Counter()
for g in GAMES:
    d = deck(g)
    try:
        pos, skip, dk = convert_game(g)
    except Exception:
        continue
    MINE = {c['name']: c['name'] + ' ' + c['variant'] for c in dk['counts_by_name_and_variant']}
    COUNT = {c['name']: c['count'] for c in dk['counts_by_name_and_variant']}
    # any dict in DECK_USED that names a card and gives printing aliases / a printing list
    ents = collections.OrderedDict()
    for path, o in walk(d):
        nm = o.get('name')
        if not isinstance(nm, str):
            continue
        al = o.get('printing_aliases') or o.get('printings') or o.get('variant')
        if isinstance(al, str):
            al = [a.strip() for a in re.split(r'[/,;]', al)]
        if isinstance(al, list) and al and all(isinstance(a, str) for a in al):
            al = [a for a in al if re.fullmatch(r'[A-Za-z0-9\-]+ \d{3}', a)]
            if al:
                key = (nname(nm), o.get('entity_id') or o.get('semantic_entity_id'), tuple(al))
                ents.setdefault(key, (path, o.get('count')))
    out = []
    for (n, eid, al), (path, cnt) in ents.items():
        if n not in MINE:
            continue
        mine_sem = fsem(MINE[n])
        al_sems = {fsem(f'{n} {a}') for a in al} - {None}
        if mine_sem not in al_sems:
            out.append((n, eid, al, cnt, path.split('[')[0], 'MINE=' + MINE[n]))
    print('##', short_of(g), 'deck source', dk['source_key'], '| alias entries found', len(ents))
    for x in out:
        print('    WRONG', x)
