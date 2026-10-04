import json, os, sys, re, collections
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_decisions_2026-10-02/positions_kx.json"
R = "/home/dacz8976/pgd/runs_kx3_trace"
pos = {p['id']: p for p in json.load(open(P))}

def matches(step, move):
    k, _, rest = step.partition(':')
    if k == 'Play':
        return move.startswith('Play {') and move.rstrip(' }').endswith(rest)
    if k == 'Attach':
        m = re.match(r'1(\w+)@(\d+) (zone|fx)', rest)
        if not m: return False
        typ, idx, src = m.groups()
        te = 'true' if src == 'zone' else 'false'
        return move == 'Attach { attachments: [(1, %s, %s)], is_turn_energy: %s }' % (typ, idx, te)
    if k == 'Retreat':
        return move == 'Retreat(%s)' % rest
    if k == 'Evolve':
        name, _, idx = rest.partition('@')
        return move.startswith('Evolve {') and (name + ')') in move and ('in_play_idx: %s,' % idx) in move
    if k == 'Place':
        return move.startswith('Place(Pokemon(') and (rest + ')') in move
    if k == 'Attack':
        return move.startswith('Attack(') and ('title: "%s"' % rest) in move
    if k == 'AttachTool':
        name, _, idx = rest.partition('@')
        return move.startswith('AttachTool') and name in move and ('in_play_idx: %s,' % idx) in move
    if k == 'Ability' or k == 'UseAbility':
        return move.startswith('UseAbility')
    return False

def short(m):
    m = m.replace('Play { trainer_card: ', 'Play ').replace(' }', '')
    mm = re.match(r'Attack\(Attack \{ energy_required: .*?title: "(.*?)"', m)
    if mm: return 'Attack ' + mm.group(1)
    m = re.sub(r'Attach \{ attachments: \[\(1, (\w+), (\d+)\)\], is_turn_energy: true', r'Attach \1@\2', m)
    m = re.sub(r'Attach \{ attachments: \[\(1, (\w+), (\d+)\)\], is_turn_energy: false', r'AttachFx \1@\2', m)
    m = re.sub(r'Evolve \{ evolution: Pokemon\(\S+ \S+ (.*?)\), in_play_idx: (\d+), from_deck: false', r'Evolve \1@\2', m)
    m = re.sub(r'Place\(Pokemon\(\S+ \S+ (.*?)\), (\d+)\)', r'Place \1@\2', m)
    m = re.sub(r'Play [A-Z0-9-]+[a-z]? \d+ ', 'Play ', m)
    return m[:60]

def traces(pid):
    out = []
    seed = None
    f = os.path.join(R, 'err_%s.txt' % pid)
    if not os.path.exists(f): return None
    for line in open(f):
        if line.startswith('PGSTEP'):
            seed = line.split()[3] + '/' + line.split()[5]
        elif line.startswith('KX_TRACE'):
            t = json.loads(line[9:]); t['_seed'] = seed; out.append(t)
    return out

ids = sys.argv[1:] if len(sys.argv) > 1 else [k for k in pos if k.startswith('B-')]
for pid in ids:
    p = pos[pid]
    tr = traces(pid)
    if tr is None: continue
    print('=' * 110)
    print(pid, p.get('decision_maker'), p.get('milestones'), 'pts', p['points'], 'res', p.get('pilot_result'))
    print('  human:', ' > '.join(p.get('his_plan') or []))
    for line in open(os.path.join(R, 'out_%s.jsonl' % pid)):
        j = json.loads(line)
        if j['kind'] != 'position':
            print('  kx s%s: %s' % (j.get('seed'), ' > '.join(j['plan']) if 'plan' in j else json.dumps(j)[:300]))
    # first decision per seed: human first step vs km
    hp = p.get('his_plan') or []
    for t in tr:
        c = {x['move']: x for x in t['candidates']}
        best = max(t['candidates'], key=lambda x: x['score'])
        km = c.get(t['km_move'])
        # which human step matches any candidate
        hm = [x for x in t['candidates'] if any(matches(s, x['move']) for s in hp[:1])]
        hs = ''
        if hm:
            x = hm[0]; hs = 'H1st %s %.3f (%+.3f se %.3f)' % (short(x['move']), x['score'], x['diff'], x['se'])
        spread = max(x['score'] for x in t['candidates']) - min(x['score'] for x in t['candidates'])
        print('   %-6s km=%-28s %.3f | best=%-28s %+.3f se %.3f | n=%d spread %.2f %s %s' % (
            t['_seed'], short(t['km_move']), km['score'] if km else float('nan'), short(best['move']), best['diff'], best['se'],
            len(t['candidates']), spread, 'CHANGED->' + short(t['chosen']) if t['changed'] else '', hs))
