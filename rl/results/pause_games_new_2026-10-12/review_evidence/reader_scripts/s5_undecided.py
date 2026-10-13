import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid = C['BYNAME'], C['nname'], C['cid']
cases = [('033529000', 'Hitmonlee'), ('033529000', 'Riolu'), ('032023000', 'Wiglett'), ('015452000', 'Hoppip'), ('015821000', 'Frigibax'),
         ('020258000', 'Lechonk'), ('004435000', 'Magikarp'), ('004435000', 'Feebas'), ('014541000', 'Feebas'), ('015452000', 'Goomy'), ('004435000', 'Pyukumuku'),
         ('013009000', 'Revavroom'), ('003547000', 'Oricorio'), ('124532000', 'Charmeleon'), ('003458000', 'Dragonair')]
for gs, name in cases:
    g = [x for x in GAMES if short_of(x).endswith(gs)][0]
    L = led(g)
    titles = collections.OrderedDict()
    for c in BYNAME[name]:
        for a in c.get('attacks', []):
            titles.setdefault(a['title'], set()).add(c['id'])
        if isinstance(c.get('ability'), dict):
            titles.setdefault(c['ability']['title'], set()).add(c['id'])
    hits = collections.Counter()
    ctx = {}
    for t in L['turns']:
        if str(t.get('who_played', '')).startswith('owner'):
            continue
        for p in t.get('plays_in_order') or []:
            s = json.dumps(p, ensure_ascii=False).replace('’', "'")
            if name.lower() not in s.lower():
                continue
            for ti in titles:
                if ti.lower() in s.lower():
                    hits[ti] += 1
                    ctx.setdefault(ti, (t['turn_number'], p.get('kind'), p.get('card_name'), str(p.get('result'))[:120]))
    print(short_of(g), name, '| titles used by the opponent with that name in the text:', dict(hits), {k: sorted(titles[k]) for k in hits}, ctx)
