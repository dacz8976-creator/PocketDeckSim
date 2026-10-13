import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, instances, MINEX = C['BYNAME'], C['nname'], C['cid'], C['instances'], None


def card_of(cardid):
    n = cardid.rsplit(' ', 2)[0]
    return [c for c in BYNAME[n] if cid(c) == cardid][0]


iss = collections.defaultdict(list)
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    b = t['board_at_start']
    for side, key in (('owner', 'me'), ('opponent', 'opp')):
        for inst, pb in zip(instances(b[side]), p[key]['board']):
            c = card_of(pb['card'])
            hpn, hpm, dmg = inst.get('hp_now'), inst.get('hp_max'), inst.get('damage')
            if hpn is None:
                iss['hp_now None'].append((p['id'], side, inst['name']))
            if hpm is not None and hpn is not None and dmg is not None and hpm - dmg != hpn:
                iss['hp_max - damage != hp_now'].append((p['id'], side, inst['name'], hpm, dmg, hpn))
            if hpm is not None and c.get('hp') != hpm:
                iss[f'{side}: printed HP of the chosen card != ledger hp_max'].append((p['id'], inst['name'], pb['card'], c.get('hp'), hpm, hpn, 'tool=' + str(inst.get('tool')), 'pos tools=' + str(pb.get('tools')), 'effects=' + str(inst.get('active_effects'))[:100]))
            if hpn is not None and hpn > (c.get('hp') or 0) and not pb.get('tools'):
                iss[f'{side}: hp in position above printed HP and no tool carried'].append((p['id'], inst['name'], pb['card'], c.get('hp'), hpn, str(inst.get('active_effects'))[:150], str(b[side].get('board_effects'))[:100]))
            if hpm is None:
                iss['hp_max None'].append((p['id'], side, inst['name']))
for k, v in iss.items():
    print('==', k, len(v), 'instances in', len({x[0] for x in v}), 'positions')
    for x in v[:40]:
        print('   ', x)
