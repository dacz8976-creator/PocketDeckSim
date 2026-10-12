import json, os, sys, re
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_decisions_2026-10-02/positions_kx.json"
R = "/home/dacz8976/pgd/runs_kx3_trace"
pos = {p['id']: p for p in json.load(open(P))}

def short(m):
    m = m.replace('Play { trainer_card: ', 'Play ').replace(' }', '')
    mm = re.match(r'Attack\(Attack \{ energy_required: .*?title: "(.*?)"', m)
    if mm:
        return 'Attack ' + mm.group(1)
    m = m.replace('Attach { attachments: ', 'Attach ').replace(', is_turn_energy: true', ' turn')
    m = m.replace('is_turn_energy: false', 'fx')
    return m[:90]

def board(side):
    out = []
    for b in side['board']:
        s = b['card'] + '(%s' % b.get('hp')
        if b.get('energy'):
            s += ' ' + ''.join(e[0] for e in b['energy'])
        if b.get('tools'):
            s += ' +' + ','.join(b['tools'])
        s += ')'
        out.append(s)
    return ' | '.join(out)

ids = sys.argv[1:]
for pid in ids:
    p = pos[pid]
    print('#' * 100)
    print(pid, p.get('decision_maker'), 'exact' if p.get('exact_list') else '', 'approx' if p.get('approximate') else '', p.get('milestones'), 'result:', p.get('pilot_result'))
    print('points', p['points'], 'turn', p['turn_count'])
    print('his_plan:', p.get('his_plan'))
    if p.get('notes'):
        print('notes:', p['notes'][:1500])
    outf = os.path.join(R, 'out_%s.jsonl' % pid)
    if not os.path.exists(outf):
        print('NOT RUN'); continue
    for line in open(outf):
        j = json.loads(line)
        if j['kind'] == 'position':
            s = j['summary']
            print('ME  :', board(s['me']), ' hand:', s['me']['hand'], 'deck', s['me']['deck'])
            print('OPP :', board(s['opp']), ' hand', s['opp']['hand'], 'deck', s['opp']['deck'])
        else:
            print('kx seed', j.get('seed'), j.get('cut'), ':', j.get('plan'))
    errf = os.path.join(R, 'err_%s.txt' % pid)
    seed = None
    for line in open(errf):
        if line.startswith('PGSTEP'):
            seed = line.strip()
        elif line.startswith('KX_TRACE'):
            t = json.loads(line[len('KX_TRACE '):])
            c = sorted(t['candidates'], key=lambda x: -x['score'])
            print('  [%s] km=%s chosen=%s changed=%s rounds=%s reason=%s' % (seed.replace('PGSTEP ' + pid + ' ', ''), short(t['km_move']), short(t['chosen']), t['changed'], t['rounds'], t['reason']))
            for x in c:
                print('      %6.3f diff %+6.3f se %5.3f  %s' % (x['score'], x['diff'], x['se'], short(x['move'])))
