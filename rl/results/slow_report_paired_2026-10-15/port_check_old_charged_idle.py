import json, sys
from collections import Counter, defaultdict
P = "/home/dacz8976/pgfix/rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate/games.jsonl"
rows = [json.loads(l) for l in open(P, encoding='utf-8')]
NT, RT, VU, RA = 'Alolan Ninetales ex', "Team Rocket's Raticate ex", 'Alolan Vulpix', "Team Rocket's Rattata"
COST = {NT: 2, RT: 2, VU: 1, RA: 1}
RET = {NT: 2, RT: 0, VU: 1, RA: 1}
SHORT = {NT: 'NT', RT: 'RT', VU: 'Vu', RA: 'Ra', '': '-'}
ATK = {'Binding Snow': 'BS', 'Boost Dash': 'BD', 'Gnaw': 'Gn', 'Ambush': 'Am'}

def find_bench(slots, name):
    c = [k for k in (1, 2, 3) if k in slots and slots[k][0] == name]
    if not c:
        # maybe the bench holds the pre-evolution name? not possible for act; unknown bench card
        return None
    return max(c, key=lambda k: slots[k][1])

def analyse(g):
    first = g['first'] == 'deck'
    own_parity = 1 if first else 0
    slots = {}
    turns = defaultdict(list)
    for e in g['log']:
        turns[e['t']].append(e)
    T = g['turns']
    last_p = [0, 0]
    ko_pending = False
    events = []
    recs = {}
    warn = []
    for t in sorted(set(list(turns.keys()) + list(range(1, T + 1)))):
        es = turns.get(t, [])
        own = (t % 2 == own_parity) and t >= 1
        rec = {'t': t, 'logged': bool(es), 'attack': None}
        for e in es:
            a = e['a']
            if e['p'][1] > last_p[1]:
                events.append((t, 'opp+%d' % (e['p'][1] - last_p[1]), SHORT.get(slots.get(0, [''])[0], '?')))
                ko_pending = True
            if e['p'][0] > last_p[0]:
                events.append((t, 'deck+%d' % (e['p'][0] - last_p[0])))
            last_p = list(e['p'])
            act = e['act']
            if ko_pending and not a.startswith('Promote:'):
                if act:
                    slots.pop(0, None)
                    k = find_bench(slots, act)
                    if k is not None:
                        slots[0] = slots.pop(k)
                    else:
                        slots[0] = [act, 0]; warn.append((t, 'unknown promoted', act))
                    ko_pending = False
            elif act and t > 0 and (0 not in slots or slots[0][0] != act) and not a.startswith('Promote:'):
                # active changed without a KO we saw: opponent's switch, or unknown setup
                if 0 not in slots:
                    slots[0] = [act, 0]
                else:
                    k = find_bench(slots, act)
                    if k is not None:
                        old = slots[0]; slots[0] = slots[k]; slots[k] = old
                    else:
                        warn.append((t, 'active mismatch', slots[0][0], act)); slots[0] = [act, 0]
            if 'act0' not in rec:
                rec['act0'] = slots.get(0, [''])[0]
                rec['e0'] = slots.get(0, ['', 0])[1]
            if a.startswith('Place:'):
                nm, k = a[6:].rsplit('@', 1)
                slots[int(k)] = [nm, 0]
            elif a.startswith('Attach:'):
                k = int(a.split('@')[1].split()[0])
                if k in slots:
                    slots[k][1] += 1
                else:
                    warn.append((t, 'attach unknown slot', k))
            elif a.startswith('Evolve:'):
                nm, k = a[7:].rsplit('@', 1); k = int(k)
                if k in slots:
                    slots[k][0] = nm
                else:
                    slots[k] = [nm, 0]; warn.append((t, 'evolve unknown slot', k))
                if k == 0:
                    rec['ev0'] = True
            elif a.startswith('Ability:Thieving'):
                k = int(a.split('@')[1])
                if k in slots:
                    slots[k][1] += 1
                rec['ti'] = True
            elif a.startswith('Retreat:'):
                k = int(a.split(':')[1])
                old = slots.get(0)
                if old:
                    old[1] = max(0, old[1] - RET.get(old[0], 0))
                if k in slots:
                    slots[0] = slots[k]
                else:
                    warn.append((t, 'retreat unknown slot', k)); slots.pop(0, None)
                if old:
                    slots[k] = old
                rec['ret'] = True
            elif a.startswith('Promote:'):
                k = int(a.split('@')[1])
                slots.pop(0, None)
                if k in slots:
                    slots[0] = slots.pop(k)
                else:
                    warn.append((t, 'promote unknown slot', k))
                ko_pending = False
            elif a.startswith('Activate:'):
                k = int(a.split('@')[1])
                old = slots.get(0)
                if k in slots:
                    slots[0] = slots[k]
                if old:
                    slots[k] = old
            elif a.startswith('Attack:'):
                rec['attack'] = a[7:]
            elif a == 'ReturnPokemonToHand':
                rec['ilima'] = True
                warn.append((t, 'ilima'))
            elif a.startswith('Play:'):
                rec.setdefault('plays', []).append(a[5:])
        if es:
            rec['act_end'] = slots.get(0, [''])[0]
            rec['e_end'] = slots.get(0, ['', 0])[1]
            rec['bench'] = sorted((SHORT.get(v[0], '?') + str(v[1])) for k, v in slots.items() if k != 0)
        if own:
            recs[t] = rec
    fp = g['points']
    if fp[1] > last_p[1]:
        events.append((T, 'opp+%d(final)' % (fp[1] - last_p[1]), SHORT.get(slots.get(0, [''])[0], '?')))
    if fp[0] > last_p[0]:
        events.append((T, 'deck+%d(final)' % (fp[0] - last_p[0])))
    ended_on_own = (T % 2 == own_parity)
    return [recs[t] for t in sorted(recs)], events, ended_on_own, warn

def classify(r):
    if not r['logged']:
        return 'pass'
    if r['attack']:
        return 'atk'
    ok = r.get('e_end', 0) >= COST.get(r.get('act_end', ''), 9)
    if ok and not r.get('ret'):
        return 'NOATK'
    return 'noen'

def summarise(sel, label, verbose):
    tot = Counter()
    for g in sel:
        out, events, eoo, warn = analyse(g)
        cl = [classify(r) for r in out]
        tot['games'] += 1
        tot['win'] += g['winner'] == 'deck'
        tot['own_turns'] += len(out)
        for c in cl:
            tot[c] += 1
        # charged no-attack turns on the main attackers only
        tot['NOATK_ex'] += sum(1 for r, c in zip(out, cl) if c == 'NOATK' and r.get('act_end') in (NT, RT))
        tot['opp_win_on_own_turn'] += (eoo and g['winner'] == 'opp')
        tot['deck+3'] += sum(1 for ev in events if ev[1].startswith('deck+3'))
        tot['warn'] += len(warn)
        if verbose:
            line = []
            for r, c in zip(out, cl):
                if c == 'pass':
                    line.append('%d:--' % r['t']); continue
                s = SHORT.get(r.get('act_end', ''), '?') + str(r.get('e_end'))
                if c == 'atk':
                    s += '>' + ATK[r['attack']]
                elif c == 'NOATK':
                    s += '!NOATK'
                if r.get('ev0'): s = 'ev,' + s
                if r.get('ret'): s = 'ret,' + s
                if r.get('ilima'): s = 'IL,' + s
                pl = [x for x in r.get('plays', []) if x in ('Sabrina', 'Cyrus', 'Ilima', 'Field Blower', 'Soothing Shore', 'Elegant Cape')]
                if pl: s += '{' + ','.join(p[:3] for p in pl) + '}'
                line.append('%d:%s' % (r['t'], s))
            print('%-3s d%d s%d %-4s %-4s %s T%-2d%s | %s' % (g['arm'], g['deal'], g['seat'], g['first'], g['winner'][:4], g['points'], g['turns'], ' OWN-END' if eoo else '        ', ' '.join(line)))
            print('      ev:', events, (' WARN ' + str(warn)) if warn else '')
    print(label, dict(tot))
    return tot

if __name__ == '__main__':
    alt = [g for g in rows if g['opp'] == 't-altaria']
    for arm in ('X', 'ref'):
        sel = sorted([g for g in alt if g['arm'] == arm], key=lambda g: (g['deal'], g['seat']))
        print('########## arm', arm)
        summarise(sel, 'altaria ' + arm, True)
    print()
    for arm in ('X', 'ref'):
        for opp in sorted(set(g['opp'] for g in rows)):
            sel = [g for g in rows if g['opp'] == opp and g['arm'] == arm]
            summarise(sel, '%s %s' % (opp, arm), False)
