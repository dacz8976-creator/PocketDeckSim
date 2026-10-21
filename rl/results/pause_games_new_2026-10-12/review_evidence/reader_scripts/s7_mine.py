import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, instances, load_deck = C['BYNAME'], C['nname'], C['cid'], C['instances'], C['load_deck']


def desc(c):
    ab = c.get('ability')
    ab = ab.get('title') if isinstance(ab, dict) else None
    return f"{c['id']} hp{c.get('hp')} {c.get('energy_type')} st{c.get('stage')} from={c.get('evolves_from')} ab={ab} atk=" + ' | '.join(f"{a.get('title')}[{''.join(x[0] for x in a.get('energy_required') or [])}]{a.get('fixed_damage')}" for a in c.get('attacks', [])) + f" ret={len(c.get('retreat_cost') or [])}"


for n in sys.argv[1:]:
    print('##', n)
    for c in BYNAME.get(n, []):
        print('   ', desc(c) if 'hp' in c else c)
