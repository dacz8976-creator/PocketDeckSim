import json, sys, re
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
P = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
g = sys.argv[1]
tns = [int(x) for x in sys.argv[2].split(',')]
short = g.replace('_iOS', '')[2:]
ALL = json.load(open(P, encoding='utf-8'))
led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
turns = led['turns']


def unc(o, path=''):
    """every non-null limit_reason / status not 'observed' / uncertainty-like key"""
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            p = f'{path}.{k}'
            if k in ('limit_reason', 'uncertainty', 'uncertain', 'confidence', 'status', 'basis_limit') and v not in (None, 'observed', [], ''):
                out.append(f'{p} = {json.dumps(v, ensure_ascii=False)[:300]}')
            elif isinstance(v, (dict, list)):
                out += unc(v, p)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += unc(v, f'{path}[{i}]')
    return out


def pk(p):
    if not p or not isinstance(p, dict) or not p.get('name'):
        return str(p)
    ae = (p.get('attached_energy') or {})
    st = p.get('evolution_stack') or p.get('evolution_stack_under_top') or p.get('evolution_stack_bottom_to_top')
    extra = {k: v for k, v in p.items() if k not in ('name', 'variant', 'bench_position', 'hp_now', 'hp_max', 'hp_max_basis', 'damage', 'attached_energy', 'tool', 'special_conditions', 'active_effects', 'status', 'limit_reason', 'evolution_stack', 'evolution_stack_under_top', 'evolution_stack_bottom_to_top') and not k.endswith('evidence_ids')}
    return (f"{p.get('name')} [{p.get('variant')}] slot={p.get('bench_position')} hp={p.get('hp_now')}/{p.get('hp_max')} dmg={p.get('damage')} "
            f"E={json.dumps(ae.get('by_type'), ensure_ascii=False)} tot={ae.get('total')} tool={p.get('tool')} cond={p.get('special_conditions')} eff={p.get('active_effects')} "
            f"stack={json.dumps(st, ensure_ascii=False)} status={p.get('status')} lim={p.get('limit_reason')} extra={json.dumps(extra, ensure_ascii=False)[:300]}")


def side(s, label):
    print(f'  [{label}] points={s.get("points")} status={s.get("status")} lim={s.get("limit_reason")} effects={s.get("board_effects")}')
    print('    A:', pk(s.get('active')))
    for b in s.get('bench_in_position_order') or []:
        print('    B:', pk(b))
    print('    zone:', json.dumps(s.get('energy_zone'), ensure_ascii=False)[:500])


for tn in tns:
    pid = f'KW-{short}-t{tn:02d}'
    pos = [p for p in ALL if p['id'] == pid]
    print('=' * 30, pid)
    if pos:
        p = pos[0]
        print('POS turn_count', p['turn_count'], 'his_turn', p['his_turn'], 'points', p['points'], 'stadium', p['stadium'])
        print('POS me.hand', p['me']['hand'])
        print('POS me.discard', p['me']['discard'], 'disc_energy', p['me']['discard_energy'])
        for i, b in enumerate(p['me']['board']):
            print(f'POS me[{i}]', json.dumps(b, ensure_ascii=False))
        print('POS me energy_now', p['me']['energy_now'], 'next', p['me']['energy_next'])
        print('POS opp hand', p['opp']['hand_count'], 'energy_next', p['opp']['energy_next'])
        for i, b in enumerate(p['opp']['board']):
            print(f'POS opp[{i}]', json.dumps(b, ensure_ascii=False))
        print('POS plan', p['his_plan'], 'trunc', p['plan_truncated_at'])
        print('POS notes', p['notes'])
    else:
        print('NO POSITION')
    t = [x for x in turns if x['turn_number'] == tn][0]
    print('LED who', t.get('who_played'))
    hs = t.get('hand_at_start') or {}
    print('LED hand', hs.get('count'), [(c.get('name'), c.get('variant')) if isinstance(c, dict) else c for c in hs.get('cards_left_to_right') or []], 'status', hs.get('status'), 'lim', hs.get('limit_reason'))
    ohs = t.get('owner_hand_start')
    if ohs and ohs != hs:
        print('LED owner_hand_start DIFFERS', json.dumps(ohs, ensure_ascii=False)[:800])
    print('LED opp hand', json.dumps(t.get('opponent_hand_at_owner_turn_start'), ensure_ascii=False))
    b = t.get('board_at_start') or {}
    print('LED stadium', json.dumps(b.get('stadium'), ensure_ascii=False), 'turn_displayed', b.get('turn_number_displayed'), 'phase', b.get('phase'), 'shared', b.get('shared_effects'))
    side(b.get('owner') or {}, 'owner')
    side(b.get('opponent') or {}, 'opp')
    print('LED plays:')
    for pl in t.get('plays_in_order') or []:
        e = pl.get('energy') or {}
        print(f"   {pl.get('order')} {pl.get('kind')} card={pl.get('card_name')} tgt={pl.get('target')} E={e.get('type')}x{e.get('count')}->{e.get('destination')} pay={e.get('retreat_payment_by_type')} | {pl.get('result')} | prompt={pl.get('prompt_text')} resp={pl.get('response')} lim={pl.get('limit_reason')}")
    print('LED draws:', json.dumps([(d.get('kind'), [c.get('name') for c in d.get('cards_in_reveal_order') or []], d.get('limit_reason')) for d in t.get('draws_and_searches') or []], ensure_ascii=False))
    print('LED limits:', json.dumps(t.get('limits'), ensure_ascii=False)[:1500])
    for k in t:
        if k not in ('turn_number', 'who_played', 'source_video', 'timing', 'hand_at_start', 'owner_hand_start', 'opponent_hand_at_owner_turn_start', 'draws_and_searches', 'plays_in_order', 'automatic_events_in_order', 'board_at_start', 'board_after', 'owner_hand_end', 'discard_snapshot_ids', 'turn_evidence_ids', 'limits'):
            print('LED extra key', k, json.dumps(t[k], ensure_ascii=False)[:800])
    u = unc({'hand': hs, 'board': b, 'plays': t.get('plays_in_order'), 'opp_hand': t.get('opponent_hand_at_owner_turn_start')})
    u = [x for x in u if 'Exact printing not required' not in x]
    print('LED uncertain/limit fields:')
    for x in u:
        print('   ', x)
