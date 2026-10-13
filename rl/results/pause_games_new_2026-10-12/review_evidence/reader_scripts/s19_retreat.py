import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
nk, retreat_pay, instances, nname = C['nk'], C['retreat_pay'], C['instances'], C['nname']
# every owner retreat in every game: what the converter reads as paid, vs the energy the active lost (board before vs after)
for g in GAMES:
    if short_of(g) not in {p['game'][3:] for p in POS}:
        continue
    for t in led(g)['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for pl in t.get('plays_in_order') or []:
            if nk(pl.get('kind')) != 'retreat':
                continue
            paid = retreat_pay(pl)
            e = pl.get('energy')
            print(short_of(g), 't%02d' % t['turn_number'], '| parsed paid', paid, '| energy field', json.dumps(e, ensure_ascii=False)[:150], '| result', str(pl.get('result'))[:150])
