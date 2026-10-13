import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
instances = C['instances']
seen = collections.Counter()
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    t = [t for t in led(g)['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    for side, key in (('owner', 'me'), ('opponent', 'opp')):
        for inst, pb in zip(instances(t['board_at_start'][side]), p[key]['board']):
            for k in ('printing', 'pokemon_id', 'instance_id', 'physical_instance'):
                if inst.get(k) is not None:
                    seen[(short, side, inst['name'], k, str(inst.get(k))[:60], pb['card'])] += 1
for k, v in seen.items():
    print(v, k)
