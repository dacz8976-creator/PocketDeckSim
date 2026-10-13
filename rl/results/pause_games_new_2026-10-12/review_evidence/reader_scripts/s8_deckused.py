import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
load_deck = C['load_deck']
for gs in sys.argv[1:]:
    g = [x for x in GAMES if short_of(x).endswith(gs)][0]
    d = deck(g)
    cards, energy, src = load_deck(d)
    print('######', short_of(g), 'src', src, 'energy', repr(energy))
    print('top keys', list(d.keys()))
    for k, v in d.items():
        s = json.dumps(v, ensure_ascii=False)
        if 'energy' in k.lower() or isinstance(v, (str, int)) or k == src or k.startswith('counts_by'):
            print('  ', k, ':', s[:1500])
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                s2 = json.dumps(v2, ensure_ascii=False)
                if 'energy' in k2.lower() or isinstance(v2, (str, int)):
                    print('  ', k + '.' + k2, ':', s2[:300])
    print('   parsed cards', collections.Counter(cards))
