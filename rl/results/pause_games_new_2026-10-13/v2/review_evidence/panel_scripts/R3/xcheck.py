import json, re, unicodedata
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "261012_210041000": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
 "261012_230258000": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
}
POS = json.load(open(V2 + "positions_all.json", encoding='utf-8'))

def nm(s):
    s = str(s).replace('’', "'")
    return s

def strip_id(c):
    return re.sub(r'\s+[A-Za-z0-9\-]+ \d{3}$', '', c)

def ledger_side(side):
    out = []
    for p in [side.get('active')] + list(side.get('bench_in_position_order') or []):
        if not p or not p.get('name') or str(p['name']).lower() in ('none', 'empty'):
            continue
        e = (p.get('attached_energy') or {}).get('by_type') or {}
        out.append((nm(p['name']), p.get('hp_now'), sorted([k for k, v in e.items() for _ in range(int(v))]),
                    (p.get('tool') if p.get('tool') not in (None, 'none') else None), sorted(p.get('special_conditions') or [])))
    return out

def pos_side(board):
    out = []
    for b in board:
        out.append((strip_id(b['card']), b.get('hp'), sorted(b.get('energy') or []), (strip_id(b['tools'][0]) if b.get('tools') else None), sorted(b.get('conditions') or [])))
    return out

for g, path in paths.items():
    led = json.load(open(path, encoding='utf-8'))
    T = {t['turn_number']: t for t in led['turns']}
    for p in POS:
        if not p['id'].startswith('KW-' + g + '-t'):
            continue
        tn = p['turn_count']
        t = T[tn]
        b = t['board_at_start']
        print('=' * 20, p['id'])
        lh = [nm(c['name']) for c in (t.get('owner_hand_start') or t.get('hand_at_start'))['cards_left_to_right']]
        ph = [strip_id(c) for c in p['me']['hand']]
        print(' hand', 'OK' if sorted(lh) == sorted(ph) else f'DIFF ledger {lh} pos {ph}')
        lo, po = ledger_side(b['owner']), pos_side(p['me']['board'])
        print(' myboard', 'OK' if lo == po else f'DIFF\n   ledger {lo}\n   pos    {po}')
        lo, po = ledger_side(b['opponent']), pos_side(p['opp']['board'])
        print(' oppboard', 'OK' if lo == po else f'DIFF\n   ledger {lo}\n   pos    {po}')
        lp = [b['owner'].get('points'), b['opponent'].get('points')]
        print(' points', 'OK' if lp == p['points'] else f'DIFF ledger {lp} pos {p["points"]}')
        oc = (t.get('opponent_hand_at_owner_turn_start') or {}).get('count')
        print(' opphand', 'OK' if oc == p['opp']['hand_count'] else f'DIFF ledger {oc} pos {p["opp"]["hand_count"]}')
        st = b.get('stadium')
        ps = p['stadium']['card'] if p.get('stadium') else None
        print(' stadium ledger', st, 'pos', ps, p['stadium']['owner'] if p.get('stadium') else None)
        # implied deck count
        n = len(p['me']['hand']) + len(p['me']['discard'])
        for x in p['me']['board']:
            n += 1 + len(x.get('behind', [])) + len(x.get('tools', []))
        if p.get('stadium') and p['stadium']['owner'] == 0:
            n += 1
        print(' implied deck', 20 - n, '| knockouts', p['me']['knockouts'], '| disc_energy', len(p['me']['discard_energy']), '| deck_count key', p['me'].get('deck_count'))
