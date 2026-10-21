import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME = C['BYNAME']
for p in POS:
    pl = p['his_plan']
    for i, s in enumerate(pl):
        if s == 'Play:Rare Candy':
            nx = pl[i + 1] if i + 1 < len(pl) else None
            ok = None
            if nx and nx.startswith('Evolve:'):
                nm = nx.split(':', 1)[1].rsplit('@', 1)[0]
                st = {c.get('stage') for c in BYNAME.get(nm, []) if 'hp' in c}
                ok = st == {2}
            print(p['id'], 'Rare Candy ->', nx, 'stage2' if ok else ('NOT STAGE 2' if ok is False else '(cut)'))
