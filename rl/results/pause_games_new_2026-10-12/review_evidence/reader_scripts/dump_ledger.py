import json, sys

def pk(p):
    if not p or not isinstance(p, dict):
        return str(p)
    e = (p.get('attached_energy') or {})
    return (f"{p.get('name')} [{p.get('variant')}] bp={p.get('bench_position')} hp={p.get('hp_now')}/{p.get('hp_max')}({p.get('hp_max_basis')}) "
            f"dmg={p.get('damage')} E={e.get('total')}:{json.dumps(e.get('by_type'), ensure_ascii=False)} tool={p.get('tool')} cond={p.get('special_conditions')} "
            f"eff={p.get('active_effects')} stack={p.get('evolution_stack') or p.get('evolution_stack_under_top') or p.get('evolution_stack_bottom_to_top')} "
            f"ids={p.get('instance_id')}/{p.get('physical_instance')} st={p.get('status')} lim={p.get('limit_reason')}")

def side(s, label):
    out = [f"  {label}: points={s.get('points')} status={s.get('status')} lim={s.get('limit_reason')}"]
    out.append(f"    A: {pk(s.get('active'))}")
    for b in s.get('bench_in_position_order') or []:
        out.append(f"    B: {pk(b)}")
    ez = s.get('energy_zone') or {}
    out.append(f"    zone: this={ez.get('this_turn')} next={ez.get('next')} lim={ez.get('limit_reason')}")
    if s.get('board_effects'):
        out.append(f"    board_effects={s.get('board_effects')}")
    return '\n'.join(out)

def board(b, label):
    if not b:
        return f" {label}: none"
    out = [f" {label}: displayed_turn={b.get('turn_number_displayed')} stadium={json.dumps(b.get('stadium'), ensure_ascii=False)} shared={b.get('shared_effects')}"]
    out.append(side(b.get('owner') or {}, 'owner'))
    out.append(side(b.get('opponent') or {}, 'opponent'))
    return '\n'.join(out)

led = json.load(open(sys.argv[1], encoding='utf-8'))
turns_sel = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
print('top keys:', [k for k in led if k != 'turns'])
for t in led['turns']:
    tn = t['turn_number']
    if turns_sel and tn not in turns_sel:
        continue
    print('=' * 100)
    print(f"TURN {tn} who={t.get('who_played')} keys={list(t.keys())}")
    for hk in ('hand_at_start', 'owner_hand_start'):
        hs = t.get(hk)
        if hs:
            cards = [(c.get('position'), c.get('name'), c.get('variant'), c.get('limit_reason')) if isinstance(c, dict) else c for c in hs.get('cards_left_to_right') or []]
            print(f" {hk}: count={hs.get('count')} status={hs.get('status')} lim={hs.get('limit_reason')} cards={cards}")
    oh = t.get('opponent_hand_at_owner_turn_start')
    print(f" opp_hand_at_owner_start: {json.dumps(oh, ensure_ascii=False)[:400]}")
    for d in t.get('draws_and_searches') or []:
        print(f" draw: kind={d.get('kind')} by={d.get('caused_by')} cards={[c.get('name') for c in d.get('cards_in_reveal_order') or []]} hc {d.get('hand_count_before')}->{d.get('hand_count_after')} ret={d.get('returned_or_discarded_cards')} lim={d.get('limit_reason')}")
    for p in t.get('plays_in_order') or []:
        print(f" play {p.get('order')}: kind={p.get('kind')} card={p.get('card_name')} target={p.get('target')} energy={json.dumps(p.get('energy'), ensure_ascii=False)} result={p.get('result')} prompt={p.get('prompt_text')} resp={p.get('response')} nested={p.get('nested_events_in_order')} hc={p.get('hand_count_after')} t={p.get('timestamp_seconds')} lim={p.get('limit_reason')}")
    for a in t.get('automatic_events_in_order') or []:
        print(f" auto: {json.dumps(a, ensure_ascii=False)[:300]}")
    print(board(t.get('board_at_start'), 'board_at_start'))
    print(board(t.get('board_after'), 'board_after'))
    other = {k: v for k, v in t.items() if k not in ('turn_number', 'who_played', 'source_video', 'timing', 'hand_at_start', 'owner_hand_start', 'opponent_hand_at_owner_turn_start', 'draws_and_searches', 'plays_in_order', 'automatic_events_in_order', 'board_at_start', 'board_after')}
    if other:
        print(' other:', json.dumps(other, ensure_ascii=False)[:1500])
