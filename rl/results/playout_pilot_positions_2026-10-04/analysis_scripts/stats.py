import json, os, re, collections
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_decisions_2026-10-02/positions_kx.json"
R = "/home/dacz8976/pgd/runs_kx3_trace"
pos = {p['id']: p for p in json.load(open(P))}

def traces(pid):
    out = []; seed = None
    f = os.path.join(R, 'err_%s.txt' % pid)
    if not os.path.exists(f): return []
    for line in open(f):
        if line.startswith('PGSTEP'):
            seed = line.split()[3] + '/' + line.split()[5]
        elif line.startswith('KX_TRACE'):
            t = json.loads(line[9:]); t['_seed'] = seed; out.append(t)
    return out

def grp(pid):
    p = pos[pid]
    if pid.startswith('B-'): return 'B'
    if p.get('approximate'): return 'approx'
    return 'other-exact-own'

tot = collections.Counter()
sat = collections.Counter()
att = collections.Counter()
changed = []
for pid in pos:
    for t in traces(pid):
        g = grp(pid)
        tot[g] += 1
        sc = [c['score'] for c in t['candidates']]
        if max(sc) - min(sc) < 1e-9: sat[g, 'all-equal'] += 1
        if min(sc) >= 0.999 or max(sc) <= 0.001: sat[g, 'all-1-or-0'] += 1
        km = t['km_move']
        kmsc = [c for c in t['candidates'] if c['move'] == km][0]['score']
        if kmsc >= 0.999: sat[g, 'km=1.0'] += 1
        if t['changed']:
            changed.append((pid, t['_seed'], t['turn'], km[:60], t['chosen'][:60], t['reason'][:90]))
        # attack without attaching
        if km.startswith('Attack('):
            atts = [c for c in t['candidates'] if c['move'].startswith('Attach {') and 'is_turn_energy: true' in c['move']]
            if atts:
                b = max(atts, key=lambda c: c['diff'])
                att[g, 'n'] += 1
                if all(abs(c['diff']) < 1e-9 and c['se'] < 1e-9 for c in atts): att[g, 'identical'] += 1
                elif b['diff'] > 2 * b['se'] and b['se'] > 0: att[g, '>2se'] += 1
                elif b['diff'] > 0: att[g, 'above-noise'] += 1
                else: att[g, 'equal-or-below'] += 1
print('decisions', dict(tot))
print('saturation', dict(sat))
print('attack-without-attach decisions', dict(att))
print('changed', len(changed))
for c in changed: print('  ', c)
