import sys, json, collections
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
g = [x for x in GAMES if short_of(x).endswith(sys.argv[1])][0]
d = deck(g)
for k in sys.argv[2:]:
    v = d
    for part in k.split('.'):
        v = v.get(part) if isinstance(v, dict) else None
    if isinstance(v, list):
        c = collections.Counter(json.dumps({kk: x.get(kk) for kk in ('name', 'variant', 'entity_id', 'semantic_entity_id', 'printing_aliases', 'printing') if isinstance(x, dict) and x.get(kk) is not None}, ensure_ascii=False) if isinstance(x, dict) else x for x in v)
        print('##', k, sum(c.values()))
        for kk, n in c.items():
            print('   ', n, kk)
    else:
        print('##', k, json.dumps(v, ensure_ascii=False)[:1500])
