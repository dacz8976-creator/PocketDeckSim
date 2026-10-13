import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
instances = C['instances']
g = [x for x in GAMES if short_of(x).endswith('021629000')][0]
T = {t['turn_number']: t for t in led(g)['turns']}
for p in POS:
    if p['game'][3:] != short_of(g):
        continue
    insts = instances(T[p['turn_count']]['board_at_start']['owner'])
    row = []
    for inst, b in zip(insts, p['me']['board']):
        if 'Kingdra' in b['card']:
            row.append((inst.get('instance_id'), b['card'].split(' A')[0], [x.split(' ')[0] for x in b.get('behind', [])], b['hp'], len(b.get('energy', []))))
    print(p['id'], row)
