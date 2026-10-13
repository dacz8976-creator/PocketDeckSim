import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
etype, nk = C['etype'], C['nk']
stats = collections.Counter()
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    T = {t['turn_number']: t for t in led(g)['turns']}
    t = T[p['turn_count']]
    oz = t['board_at_start']['opponent'].get('energy_zone') or {}
    nxt = T.get(p['turn_count'] + 1)
    truth = None
    if nxt:
        z = (nxt.get('board_at_start') or {}).get('opponent', {}).get('energy_zone') or {}
        truth = etype((z.get('this_turn') or {}).get('type'))
        if truth is None:
            # the type the opponent attaches from the zone in that turn
            for pl in nxt.get('plays_in_order') or []:
                if nk(pl.get('kind')) == 'energy_attachment' and etype((pl.get('energy') or {}).get('type')):
                    truth = etype(pl['energy']['type'])
                    break
    o_this, o_next = etype((oz.get('this_turn') or {}).get('type')), etype((oz.get('next') or {}).get('type'))
    if truth is None:
        stats['no truth'] += 1
        continue
    stats[('pos==truth' if p['opp']['energy_next'] == truth else 'pos!=truth')] += 1
    if p['opp']['energy_next'] != truth:
        print(p['id'], 'pos opp energy_next', p['opp']['energy_next'], '| zone this/next', o_this, o_next, '| opponent then got', truth)
    # my energy_next vs what I get next turn
    me_n = T.get(p['turn_count'] + 2)
    if me_n:
        z = (me_n.get('board_at_start') or {}).get('owner', {}).get('energy_zone') or {}
        tr = etype((z.get('this_turn') or {}).get('type'))
        if tr and tr != p['me']['energy_next']:
            print(p['id'], 'MY energy_next', p['me']['energy_next'], 'but next own turn zone shows', tr)
print(stats)
