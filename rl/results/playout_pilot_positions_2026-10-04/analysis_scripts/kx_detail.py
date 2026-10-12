import json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from kx_scan import positions, read_out, read_trace, KX, KM

def norm(mv):
    m = re.match(r'Play \{ trainer_card: \S+ \S+ (.+?) \}$', mv)
    if m: return 'Play:' + m.group(1)
    m = re.match(r'Attach \{ attachments: \[\(1, (\w+), (\d+)\)\], is_turn_energy: true \}', mv)
    if m: return f'Attach:1{m.group(1)}@{m.group(2)} zone'
    m = re.match(r'Attach \{ attachments: \[\(1, (\w+), (\d+)\)\], is_turn_energy: false \}', mv)
    if m: return f'Attach:1{m.group(1)}@{m.group(2)} fx'
    m = re.match(r'Place\(Pokemon\(\S+ \S+ (.+?)\), (\d+)\)', mv)
    if m: return f'Place:{m.group(1)}@{m.group(2)}'
    m = re.match(r'Evolve \{ evolution: Pokemon\(\S+ \S+ (.+?)\), in_play_idx: (\d+)', mv)
    if m: return f'Evolve:{m.group(1)}@{m.group(2)}'
    m = re.match(r'Retreat\((\d+)\)', mv)
    if m: return f'Retreat:{m.group(1)}'
    m = re.search(r'title: "([^"]+)"', mv)
    if mv.startswith('Attack') and m: return 'Attack:' + m.group(1)
    m = re.match(r'AttachTool \{ in_play_idx: (\d+), tool_card: Trainer\(\S+ \S+ (.+?)\)', mv)
    if m: return f'Tool:{m.group(2)}@{m.group(1)}'
    m = re.match(r'UseAbility\D*(\d+)', mv)
    if m: return f'Ability@{m.group(1)}'
    return mv[:60]

def board(side):
    out = []
    for i, b in enumerate(side.get('board', [])):
        s = f"[{i}] {b['card']} {b.get('hp')}hp"
        if b.get('energy'): s += f" E={b['energy']}"
        if b.get('tool') or b.get('tools'): s += f" T={b.get('tool') or b.get('tools')}"
        if b.get('behind'): s += f" under={b['behind']}"
        if b.get('effects'): s += f" fx={b['effects']}"
        out.append(s)
    return out

def main(ids):
    for pid in ids:
        p = positions[pid]
        print('=' * 110)
        print(pid, 'maker', p.get('decision_maker'), 'game turn', p.get('turn_count'), 'points', p.get('points'), 'stadium', p.get('stadium'), 'fx', p.get('turn_effects'), 'ms', p.get('milestones'), 'result', p.get('pilot_result'))
        me, op = p['me'], p['opp']
        print(' ME hand:', me['hand'])
        print(' ME board:', board(me))
        print(' ME discard:', me.get('discard'), 'denergy', me.get('discard_energy'), 'E now/next', me.get('energy_now'), me.get('energy_next'))
        print(' OPP board:', board(op))
        print(' OPP hand', op.get('hand_count'), 'discard_n', op.get('discard_n'), 'E next', op.get('energy_next'))
        print(' HIS plan:', p.get('his_plan'))
        print(' notes:', p.get('notes'))
        summ, kxp = read_out(f'{KX}/out_{pid}.jsonl')
        if summ:
            print(' engine summary me:', json.dumps(summ['me'])[:900])
            print(' engine summary opp:', json.dumps(summ['opp'])[:700])
        _, kmp = read_out(f'{KM}/out_{pid}.jsonl')
        kmplans = collections.Counter(' > '.join(v[0]) for v in kmp.values())
        print(' KM3 plans (12):')
        for k, c in kmplans.most_common():
            print(f'    {c}x {k}')
        tr = read_trace(f'{KX}/err_{pid}.txt')
        for s in sorted(kxp):
            print(f' KX seed {s}: {" > ".join(kxp[s][0])}  [{kxp[s][1]}]')
            for step, t in tr.get(s, []):
                cands = sorted(t['candidates'], key=lambda c: -c['score'])
                km = norm(t['km_move']); ch = norm(t['chosen'])
                cs = ', '.join(f"{norm(c['move'])}={c['score']:.3f}({c['diff']:+.3f}/se{c['se']:.3f})" for c in cands)
                print(f'    step{step} {"CHANGED" if t["changed"] else "kept"} km={km} chosen={ch} lists={t.get("lists")} rounds={t["rounds"]} turn={t.get("turn")}')
                print(f'       {cs}')

if __name__ == '__main__':
    main(sys.argv[1].split(','))
