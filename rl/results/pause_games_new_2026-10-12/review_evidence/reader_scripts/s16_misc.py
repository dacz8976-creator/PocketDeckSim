import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
etype, ebt, instances, bpos, nname = C['etype'], C['ebt'], C['instances'], C['bpos'], C['nname']
out = collections.defaultdict(list)
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    b = t['board_at_start']
    for side, key in (('owner', 'me'), ('opponent', 'opp')):
        s = b[side]
        raw_bench = s.get('bench_in_position_order') or []
        for inst, pb in zip(instances(s), p[key]['board']):
            ae = inst.get('attached_energy') or {}
            tot = ae.get('total')
            n_pos = len(pb.get('energy') or [])
            if tot is not None and tot != n_pos:
                out['energy total != carried count'].append((p['id'], side, inst['name'], tot, ae.get('by_type'), pb.get('energy')))
            if tot is None and ae:
                out['energy total missing'].append((p['id'], side, inst['name'], ae))
            st = str(inst.get('status'))
            if st not in ('observed',):
                out['pokemon status not observed: ' + st[:40]].append((p['id'], side, inst['name'], str(inst.get('limit_reason'))[:100]))
            if inst.get('active_effects'):
                out['active_effects dropped'].append((p['id'], side, inst['name'], json.dumps(inst['active_effects'], ensure_ascii=False)[:200]))
            tl = inst.get('tool')
            if tl and str(tl).lower() not in ('none', 'null') and not pb.get('tools'):
                out['tool not carried'].append((p['id'], side, inst['name'], tl))
            if (not tl or str(tl).lower() in ('none', 'null')) and (inst.get('tool_status') or inst.get('tool_observation')):
                out['tool none but tool_status/observation present'].append((p['id'], side, inst['name'], inst.get('tool_status'), str(inst.get('tool_observation'))[:100]))
        # bench order: ledger list order vs sorted order
        names_list = [x.get('name') for x in raw_bench if C['_real'](x)]
        names_sorted = [x.get('name') for x in instances(s)[1 if C['_real'](s.get('active')) else 0:]]
        if names_list != names_sorted:
            out['bench list order != bench_position order'].append((p['id'], side, [(x.get('name'), x.get('bench_position')) for x in raw_bench]))
        bps = [x.get('bench_position') for x in raw_bench if C['_real'](x)]
        if any(bpos(x) is None for x in raw_bench if C['_real'](x)):
            out['bench_position unparsed'].append((p['id'], side, bps))
        if any(not isinstance(v, int) for v in bps):
            out['bench_position non-int forms'].append((p['id'], side, bps))
        if not C['_real'](s.get('active')):
            out['no active'].append((p['id'], side, s.get('active')))
        for x in raw_bench:
            if not C['_real'](x) and x:
                out['bench entry dropped as not real'].append((p['id'], side, json.dumps(x, ensure_ascii=False)[:150]))
        if s.get('board_effects'):
            out['board_effects dropped'].append((p['id'], side, json.dumps(s['board_effects'], ensure_ascii=False)[:200]))
        if s.get('status') not in ('observed', None):
            out['side status: ' + str(s.get('status'))[:40]].append((p['id'], side))
    if b.get('shared_effects'):
        out['shared_effects dropped'].append((p['id'], json.dumps(b['shared_effects'], ensure_ascii=False)[:200]))
    ph = str(b.get('phase'))
    if not re.search(r'after draw', ph, re.I):
        out['phase does not say after draw'].append((p['id'], ph[:140]))
    hs = t.get('hand_at_start') or {}
    if hs.get('status') != 'observed':
        out['hand status: ' + str(hs.get('status'))].append((p['id'], str(hs.get('basis'))[:100], str(hs.get('limit_reason'))[:120]))
    oh = t.get('owner_hand_start') or {}
    if [c.get('name') if isinstance(c, dict) else c for c in oh.get('cards_left_to_right') or []] != [c.get('name') if isinstance(c, dict) else c for c in hs.get('cards_left_to_right') or []]:
        out['owner_hand_start != hand_at_start'].append((p['id'], [c.get('name') for c in oh.get('cards_left_to_right') or []], [c.get('name') for c in hs.get('cards_left_to_right') or []]))
    o = t.get('opponent_hand_at_owner_turn_start') or {}
    if o.get('supported_range'):
        out['opp hand has a range'].append((p['id'], o.get('count'), o.get('supported_range'), p['opp']['hand_count'], str(o.get('limit_reason'))[:100]))
    if t.get('limits'):
        out['turn limits non-empty'].append((p['id'], json.dumps(t['limits'], ensure_ascii=False)[:250]))
for k, v in out.items():
    print('==', k, len(v), 'items in', len({x[0] for x in v}), 'positions')
    for x in v[:12]:
        print('    ', x)
