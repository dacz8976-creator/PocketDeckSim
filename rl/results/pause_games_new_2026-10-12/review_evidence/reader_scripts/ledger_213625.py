import json, sys
p = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/20261004_213625000_iOS/TURN_LEDGER.json'
d = json.load(open(p, encoding='utf-8'))

def mon(m):
    if not m:
        return str(m)
    e = m.get('attached_energy') or {}
    return '%s [%s] hp %s/%s E=%s tool=%s cond=%s pos=%s' % (m.get('name'), m.get('variant'), m.get('hp_now'), m.get('hp_max'), e.get('by_type') if isinstance(e, dict) else e, m.get('tool'), m.get('special_conditions'), m.get('bench_position'))

def board(b, label):
    if not b:
        print('  ', label, None); return
    for side in ['owner', 'opponent']:
        s = b.get(side) or {}
        print('  ', label, side, 'pts', s.get('points'), 'stadium', b.get('stadium'))
        print('     A:', mon(s.get('active')))
        for x in s.get('bench_in_position_order') or []:
            print('     B:', mon(x))

for t in d['turns']:
    print('##### TURN', t['turn_number'], t['who_played'])
    board(t.get('board_at_start'), 'start')
    for pl in t.get('plays_in_order') or []:
        print('   PLAY', pl.get('order'), pl.get('kind'), '|', pl.get('card_name'), '|', pl.get('target'), '|', pl.get('result'), '| prompt', pl.get('prompt_text'), '| resp', pl.get('response'), '| nested', json.dumps(pl.get('nested_events_in_order'), ensure_ascii=False)[:400])
    for ev in t.get('automatic_events_in_order') or []:
        print('   AUTO', json.dumps(ev, ensure_ascii=False)[:500])
    board(t.get('board_after'), 'after')
    h = t.get('owner_hand_start') or t.get('hand_at_start')
    if h and isinstance(h, dict):
        print('   HAND', [c.get('name') + ('/' + c['variant'] if c.get('variant') else '') for c in h.get('cards_left_to_right') or []])
    if t.get('draws_and_searches'):
        print('   DRAWS', json.dumps(t['draws_and_searches'], ensure_ascii=False)[:800])
    if t.get('limits'):
        print('   LIMITS', json.dumps(t['limits'], ensure_ascii=False)[:800])
