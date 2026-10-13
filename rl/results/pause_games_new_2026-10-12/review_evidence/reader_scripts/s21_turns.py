import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
ids = collections.Counter(p['id'] for p in POS)
print('duplicate ids', [k for k, v in ids.items() if v > 1])
for g in GAMES:
    L = led(g)
    tns = [(t['turn_number'], str(t.get('who_played'))[:8]) for t in L['turns']]
    dup = [k for k, v in collections.Counter(t['turn_number'] for t in L['turns']).items() if v > 1]
    who = collections.Counter(str(t.get('who_played')) for t in L['turns'])
    own = [t['turn_number'] for t in L['turns'] if str(t.get('who_played', '')).startswith('owner')]
    alt = all((a % 2) == (own[0] % 2) for a in own) if own else None
    gaps = sorted(set(range(1, max([t[0] for t in tns] or [0]) + 1)) - {t[0] for t in tns})
    ps = [p for p in POS if p['game'][3:] == short_of(g)]
    en_none = [p['id'] for p in ps if p['me']['energy_now'] is None]
    empty = [p['id'] for p in ps if not p['his_plan']]
    print(short_of(g), 'turns', len(tns), 'who', dict(who), 'dup', dup, 'gaps', gaps, 'owner turns', own, 'same parity', alt, '| energy_now None', en_none, '| empty plans', empty)
