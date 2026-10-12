import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, sys
g, tn = sys.argv[1], int(sys.argv[2])
base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES'
d = json.load(open(base + '\\' + g + '\\TURN_LEDGER.json', encoding='utf-8'))
P = json.load(open(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\rl\results\pause_games_new_2026-10-12\positions_all.json', encoding='utf-8'))
pid = 'KW-' + g.replace('_iOS', '')[2:] + '-t%02d' % tn
pos = next((p for p in P if p['id'] == pid), None)
def pk(p):
    if not p or not isinstance(p, dict):
        return str(p)
    e = (p.get('attached_energy') or {})
    s = f"{p.get('name')} [{p.get('variant')}] slot={p.get('bench_position')} hp={p.get('hp_now')}/{p.get('hp_max')} dmg={p.get('damage')} E={e.get('by_type')} tot={e.get('total')} tool={p.get('tool')} cond={p.get('special_conditions')} eff={p.get('active_effects')}"
    for k in ('status', 'limit_reason', 'evolution_stack', 'evolution_stack_under_top', 'evolution_stack_bottom_to_top', 'instance_id', 'physical_instance'):
        if p.get(k) not in (None, 'observed', [], {}):
            s += f" {k}={p.get(k)}"
    extra = set(p.keys()) - {'name','variant','bench_position','hp_now','hp_max','hp_max_basis','damage','attached_energy','tool','special_conditions','active_effects','evidence_ids','status','limit_reason','evolution_stack','evolution_stack_under_top','evolution_stack_bottom_to_top','instance_id','physical_instance'}
    if extra:
        s += ' EXTRA=' + json.dumps({k: p[k] for k in extra}, ensure_ascii=False)
    return s
for t in d['turns']:
    if t['turn_number'] != tn:
        continue
    print('#### LEDGER', g, 'turn', tn, t['who_played'])
    for k in ('hand_at_start', 'owner_hand_start'):
        h = t.get(k) or {}
        print(k, h.get('cards_left_to_right'), 'count', h.get('count'), 'status', h.get('status'), 'limit', h.get('limit_reason'), 'basis', h.get('basis'))
    oh = t.get('opponent_hand_at_owner_turn_start') or {}
    print('opp hand', oh.get('count'), oh.get('supported_range'), oh.get('limit_reason'))
    print('draws', json.dumps([(x.get('kind'), [c.get('name') if isinstance(c, dict) else c for c in x.get('cards_in_reveal_order') or []], x.get('limit_reason')) for x in t.get('draws_and_searches') or []], ensure_ascii=False))
    b = t['board_at_start']
    print('phase', b.get('phase'), '| stadium', b.get('stadium'), '| shared', b.get('shared_effects'), '| turn_displayed', b.get('turn_number_displayed'))
    for side in ('owner', 'opponent'):
        s = b[side]
        print(' --', side, 'points', s.get('points'), 'status', s.get('status'), 'limit', s.get('limit_reason'))
        print('   A:', pk(s.get('active')))
        for x in s.get('bench_in_position_order') or []:
            print('   B:', pk(x))
        print('   zone', json.dumps({k: v for k, v in (s.get('energy_zone') or {}).items() if k in ('this_turn', 'next', 'limit_reason')}, ensure_ascii=False))
        print('   board_effects', s.get('board_effects'))
        extra = set(s.keys()) - {'active','bench_in_position_order','energy_zone','points','board_effects','evidence_ids','status','limit_reason'}
        if extra:
            print('   EXTRA', json.dumps({k: s[k] for k in extra}, ensure_ascii=False)[:800])
    print(' plays:')
    for p in t.get('plays_in_order') or []:
        print('   ', p.get('order'), '|', p.get('kind'), '|', p.get('card_name'), '| tgt=', p.get('target'), '| E=', (p.get('energy') or {}).get('type') if isinstance(p.get('energy'), dict) else p.get('energy'), '| res=', p.get('result'), '| prompt=', p.get('prompt_text'), '| resp=', p.get('response'), '| nested=', p.get('nested_events_in_order'), '| limit=', p.get('limit_reason'))
    print(' auto:', [((e.get('order'), e.get('event')) if isinstance(e, dict) else e) for e in t.get('automatic_events_in_order') or []])
    print(' limits:', t.get('limits'))
    for k in t:
        if k not in ('turn_number','who_played','source_video','timing','hand_at_start','owner_hand_start','opponent_hand_at_owner_turn_start','draws_and_searches','plays_in_order','automatic_events_in_order','board_at_start','board_after','owner_hand_end','discard_snapshot_ids','turn_evidence_ids','limits'):
            print(' EXTRA KEY', k, json.dumps(t[k], ensure_ascii=False)[:1000])
print('#### POSITION', pid)
if pos:
    q = dict(pos); q.pop('notes', None)
    print(json.dumps(q, ensure_ascii=False))
    print('NOTES', pos['notes'])
