import json, re, collections
POS = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-11_NEW_PAUSE_GAMES/'
pos = [p for p in json.load(open(POS, encoding='utf-8')) if p['id'].startswith('KW-261012')]

def nm(s):
    return str(s).replace('’', "'").strip() if s is not None else None

def strip_id(c):
    return re.sub(r' [A-Za-z0-9\-]+ \d{3}$', '', c)

def real(p):
    return isinstance(p, dict) and p.get('name') and str(p['name']).lower() not in ('none', 'empty', 'null')

def side_list(s):
    out = []
    if real(s.get('active')):
        out.append(s['active'])
    bench = [p for p in s.get('bench_in_position_order') or [] if real(p)]
    bench.sort(key=lambda p: p.get('bench_position') or 99)
    return out + bench

def energies(p):
    bt = (p.get('attached_energy') or {}).get('by_type') or {}
    out = []
    for t, n in bt.items():
        out += [t] * int(n)
    return sorted(out)

for p in pos:
    g = '20' + p['game'][3:] + '_iOS'
    led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
    t = next(x for x in led['turns'] if x['turn_number'] == p['turn_count'])
    issues = []
    if not str(t['who_played']).startswith('owner'):
        issues.append('not an owner turn')
    hand_l = [nm(c['name'] if isinstance(c, dict) else c) for c in t['hand_at_start']['cards_left_to_right']]
    hand_p = [strip_id(c) for c in p['me']['hand']]
    if hand_l != hand_p:
        issues.append(f'hand {hand_p} vs ledger {hand_l}')
    b = t['board_at_start']
    for who, key in (('me', 'owner'), ('opp', 'opponent')):
        L = side_list(b[key])
        P = p[who]['board']
        if len(L) != len(P):
            issues.append(f'{who} board size {len(P)} vs {len(L)}')
        for lp, pp in zip(L, P):
            if nm(lp['name']) != strip_id(pp['card']):
                issues.append(f"{who} card {pp['card']} vs {lp['name']}")
            if lp.get('hp_now') != pp['hp']:
                issues.append(f"{who} {lp['name']} hp {pp['hp']} vs {lp.get('hp_now')}")
            if energies(lp) != sorted(pp.get('energy', [])):
                issues.append(f"{who} {lp['name']} energy {pp.get('energy')} vs {energies(lp)}")
            lt = lp.get('tool')
            lt = None if lt is None or str(lt).lower() in ('none', 'null') else nm(lt)
            pt = [strip_id(x) for x in pp.get('tools', [])]
            if (lt is None and pt) or (lt is not None and pt != [lt]):
                issues.append(f"{who} {lp['name']} tool {pt} vs {lt}")
            if lp.get('special_conditions'):
                issues.append(f"{who} {lp['name']} conditions {lp['special_conditions']} (not representable)")
    if [b['owner']['points'], b['opponent']['points']] != p['points']:
        issues.append(f"points {p['points']} vs {[b['owner']['points'], b['opponent']['points']]}")
    oh = t['opponent_hand_at_owner_turn_start'].get('count')
    if oh != p['opp']['hand_count']:
        issues.append(f"opp hand {p['opp']['hand_count']} vs {oh}")
    st = b.get('stadium')
    st = None if st is None or str(st).lower() in ('none', 'null') else nm(st)
    ps = strip_id(p['stadium']['card']) if p['stadium'] else None
    if st != ps:
        issues.append(f'stadium {ps} vs {st}')
    oz = (b['opponent'].get('energy_zone') or {}).get('next', {}).get('type')
    if oz != p['opp']['energy_next']:
        issues.append(f"opp energy_next {p['opp']['energy_next']} vs ledger next {oz}")
    mz = (b['owner'].get('energy_zone') or {})
    if (mz.get('next') or {}).get('type') != p['me']['energy_next']:
        issues.append(f"my energy_next {p['me']['energy_next']} vs {(mz.get('next') or {}).get('type')}")
    if (mz.get('this_turn') or {}).get('type') != p['me']['energy_now']:
        issues.append(f"my energy_now {p['me']['energy_now']} vs ledger this_turn {(mz.get('this_turn') or {}).get('type')} (available={(mz.get('this_turn') or {}).get('available')})")
    nested = [(x.get('order'), x.get('kind'), x.get('card_name'), x.get('nested_events_in_order')) for x in t.get('plays_in_order') or [] if x.get('nested_events_in_order')]
    kinds = [(x.get('kind'), nm(x.get('card_name'))) for x in t.get('plays_in_order') or []]
    print(p['id'], 'turn', p['turn_count'])
    print('   plan  :', ' > '.join(p['his_plan']))
    print('   ledger:', kinds)
    for n in nested:
        print('   nested:', json.dumps(n, ensure_ascii=False)[:300])
    for i in issues:
        print('   ISSUE', i)
