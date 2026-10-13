import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
instances = C['instances']
print('== hand vs the turn-start draw')
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    t = [t for t in led(g)['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    hs = t.get('hand_at_start') or {}
    nd = [d for d in t.get('draws_and_searches') or [] if 'normal' in str(d.get('kind')) or 'turn start' in str(d.get('caused_by'))]
    n = len(p['me']['hand'])
    if not nd:
        print(p['id'], 'no normal draw row; hand', n, '| draws kinds', [d.get('kind') for d in t.get('draws_and_searches') or []])
        continue
    d = nd[0]
    drawn = [c.get('name') for c in d.get('cards_in_reveal_order') or []]
    if d.get('hand_count_after') is not None and d['hand_count_after'] != n:
        print(p['id'], 'hand', n, '!= normal draw hand_count_after', d.get('hand_count_after'), 'before', d.get('hand_count_before'), 'drawn', drawn, '| hand basis', str(hs.get('basis'))[:80], '| count_phase', hs.get('count_phase'))
print('\n== effects on either board at his turn start (active_effects, board_effects), by name')
eff = collections.defaultdict(list)
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    t = [t for t in led(g)['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    b = t['board_at_start']
    for side in ('owner', 'opponent'):
        for inst in instances(b[side]):
            for e in inst.get('active_effects') or []:
                nm = e.get('name') if isinstance(e, dict) else str(e)[:60]
                eff[(side, 'mon:' + str(inst['name']), str(nm), json.dumps(e, ensure_ascii=False)[:230])].append(p['id'])
        for e in b[side].get('board_effects') or []:
            nm = e.get('name') if isinstance(e, dict) else str(e)[:60]
            eff[(side, 'board', str(nm), json.dumps(e, ensure_ascii=False)[:230])].append(p['id'])
for k, v in sorted(eff.items(), key=lambda kv: kv[0][2]):
    print(k[0], '|', k[1], '|', k[2], '|', len(v), v[:4], '\n      ', k[3])
