import json, collections, re, math
F = "/home/dacz8976/pgfix/rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate/games.jsonl"
G = [json.loads(l) for l in open(F, encoding='utf-8') if l.strip()]
BASIC = {'Alolan Vulpix': 'Vulpix', "Team Rocket's Rattata": 'Rattata'}
EX = {'Alolan Ninetales ex', "Team Rocket's Raticate ex"}
ARMNAME = {'X': 'kx3', 'ref': 'km3'}

def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * (c - h), 1), round(100 * (c + h), 1))

def opp_turn(g, t):
    # global turn t (1-based) -> opponent's own turn number
    return (t + 1) // 2 if g['first'] == 'opp' else t // 2

def analyse(g):
    log = g['log']
    slots = [None] * 4
    opening = None
    setup_bench = []
    # setup choices at t=0
    for e in log:
        if e['t'] != 0:
            break
        m = re.match(r'Place:(.+)@(\d)$', e['a'])
        if m:
            slots[int(m.group(2))] = m.group(1)
    if slots[0] is None:
        # forced setup: Active = act of first entry
        slots[0] = log[0]['act'] if log else None
    opening = slots[0]
    opening_intact = True       # opening Basic still Active, unevolved, never left slot 0
    first = None                # dict about the opponent's first score
    prev_p1 = 0
    incs = []
    prev = None
    desync = 0
    for i, e in enumerate(log):
        p1 = e['p'][1]
        # resync active from 'act' when the model disagrees (opponent switch, forced promote)
        if p1 > prev_p1:
            inc = p1 - prev_p1
            incs.append(inc)
            if first is None:
                kod = None; where = None
                if e['a'].startswith('Promote'):
                    kod = slots[0]; where = 'active'
                elif e['act'] and e['act'] != slots[0]:
                    kod = slots[0]; where = 'active(forced promote or switch)'
                else:
                    where = 'bench'
                    kod = 'bench?'
                first = dict(inc=inc, t=e['t'], kod=kod, where=where,
                             opening_intact=opening_intact, oppturn=opp_turn(g, e['t']))
            prev_p1 = p1
            # remove KO'd active from model
            if e['a'].startswith('Promote') or (e['act'] and e['act'] != slots[0]):
                slots[0] = None
        if e['act'] and slots[0] != e['act']:
            # find in bench
            js = [j for j in (1, 2, 3) if slots[j] == e['act']]
            if slots[0] is not None and opening_intact and i > 0:
                opening_intact = False if slots[0] != opening or True else opening_intact
            if js:
                j = js[0]
                slots[0], slots[j] = slots[j], slots[0]
            else:
                slots[0] = e['act']
                desync += 1
            if i > 0:
                opening_intact = False
        a = e['a']
        m = re.match(r'Place:(.+)@(\d)$', a)
        if m and e['t'] != 0:
            slots[int(m.group(2))] = m.group(1)
        m = re.match(r'Evolve:(.+)@(\d)$', a)
        if m:
            slots[int(m.group(2))] = m.group(1)
            if m.group(2) == '0':
                opening_intact = False
        m = re.match(r'Retreat:(\d)$', a)
        if m:
            k = int(m.group(1)); slots[0], slots[k] = slots[k], slots[0]; opening_intact = False
        m = re.match(r'(Promote|Activate):\d@(\d)$', a)
        if m:
            k = int(m.group(2))
            if m.group(1) == 'Promote':
                slots[0] = slots[k]; slots[k] = None
            else:
                slots[0], slots[k] = slots[k], slots[0]
            opening_intact = False
        if a.startswith('ReturnPokemonToHand'):
            opening_intact = False if True else opening_intact
        prev = e
    fin = g['points'][1]
    if fin > prev_p1:
        inc = fin - prev_p1
        incs.append(inc)
        if first is None:
            first = dict(inc=inc, t=None, kod=slots[0], where='active(end of game)',
                         opening_intact=opening_intact, oppturn=None)
    return dict(opening=opening, first=first, incs=incs, desync=desync)

rows = []
for g in G:
    r = analyse(g)
    r.update(arm=ARMNAME[g['arm']], seat='first' if g['first'] == 'deck' else 'second', opp=g['opp'],
             win=g['winner'] == 'deck', loss=g['winner'] == 'opp', pts=tuple(g['points']), deal=g['deal'], s=g['seat'])
    rows.append(r)

print('winner labels', collections.Counter(g['winner'] for g in G))
print('desync games', sum(1 for r in rows if r['desync']), 'total desyncs', sum(r['desync'] for r in rows))
print('first-score where', collections.Counter((r['first'] or {}).get('where') for r in rows))
print('opening species', collections.Counter((r['arm'], r['opening']) for r in rows))

def is_open_basic_first(r):
    f = r['first']
    return bool(f) and f['inc'] == 1 and f['where'].startswith('active') and f['opening_intact'] and f['kod'] in BASIC

def is_basic_front_first(r):
    f = r['first']
    return bool(f) and f['inc'] == 1 and f['where'].startswith('active') and f['kod'] in BASIC

def comp(r):
    # composition of opp points: number of +1 and +2 increments
    c = collections.Counter(r['incs'])
    return c

for arm in ('kx3', 'km3'):
    A = [r for r in rows if r['arm'] == arm]
    print('\n==========', arm, len(A), 'games; wins', sum(r['win'] for r in A), 'losses', sum(r['loss'] for r in A))
    for seat in ('all', 'first', 'second'):
        S = A if seat == 'all' else [r for r in A if r['seat'] == seat]
        scored = [r for r in S if r['pts'][1] > 0]
        ob = [r for r in scored if is_open_basic_first(r)]
        bf = [r for r in scored if is_basic_front_first(r)]
        exfirst = [r for r in scored if r['first']['inc'] >= 2]
        bench1 = [r for r in scored if r['first']['inc'] == 1 and r['first']['where'] == 'bench']
        print(f"  seat={seat}: games {len(S)}, opp scored {len(scored)}; first point = opening Basic KO'd in front {len(ob)} ({len(ob)}/{len(scored)} = {100*len(ob)/max(1,len(scored)):.1f}% of scoring games, {100*len(ob)/len(S):.1f}% of all games, Wilson {wilson(len(ob), len(scored))}); any Basic in front {len(bf)}; first score an ex (+2) {len(exfirst)}; first point a benched Basic {len(bench1)}")
        sp = collections.Counter(BASIC[r['first']['kod']] for r in ob)
        opens = collections.Counter(BASIC.get(r['opening'], r['opening']) for r in S)
        print(f"     by Basic: {dict(sp)}; openings {dict(opens)}; rate per opening: " + ', '.join(f"{k} {sp.get(k,0)}/{v}" for k, v in opens.items()))
        tt = collections.Counter(r['first']['oppturn'] for r in ob)
        print(f"     opp own turn of that KO: {dict(sorted((k if k is not None else 99, v) for k, v in tt.items()))}")
        # outcomes
        w_ob = sum(r['win'] for r in ob); l_ob = sum(r['loss'] for r in ob)
        notob = [r for r in S if r not in ob]
        print(f"     deck result when first point = opening Basic: W {w_ob} L {l_ob} T {len(ob)-w_ob-l_ob} of {len(ob)} (win {100*w_ob/max(1,len(ob)):.1f}%); other games: W {sum(r['win'] for r in notob)} of {len(notob)} ({100*sum(r['win'] for r in notob)/max(1,len(notob)):.1f}%)")
        lost_ob = [r for r in ob if r['loss']]
        exact = [r for r in lost_ob if r['pts'][1] == 3 and comp(r)[1] == 1 and comp(r)[2] == 1 and sum(r['incs']) == 3]
        three = [r for r in lost_ob if r['pts'][1] == 3]
        under3 = [r for r in lost_ob if r['pts'][1] < 3]
        print(f"     losses with first point = opening Basic: {len(lost_ob)}; final opp exactly 1 + one ex = 3: {len(exact)}; opp final exactly 3 (any mix) {len(three)}; opp final < 3 (no Pokemon left or other) {len(under3)}; opp final >3: {len(lost_ob)-len(three)-len(under3)}")
        print(f"        deck's own points in the exact-1+ex losses: {dict(collections.Counter(r['pts'][0] for r in exact))}")
        allloss = [r for r in S if r['loss']]
        print(f"     all losses {len(allloss)}: exact 1(opening Basic)+ex = {len(exact)} ({100*len(exact)/max(1,len(allloss)):.1f}% of losses)")
        # composition of all losses
        cm = collections.Counter(tuple(sorted(r['incs'])) for r in allloss)
        print(f"     loss point compositions: {dict(cm.most_common())}")

# per opponent list
print('\nper opponent: opening Basic as first point / opp scored / games, and wins in those games')
for arm in ('kx3', 'km3'):
    A = [r for r in rows if r['arm'] == arm]
    out = []
    for opp in sorted(set(r['opp'] for r in A)):
        S = [r for r in A if r['opp'] == opp]
        sc = [r for r in S if r['pts'][1] > 0]
        ob = [r for r in sc if is_open_basic_first(r)]
        out.append(f"{opp} {len(ob)}/{len(sc)}/{len(S)} (W {sum(r['win'] for r in ob)})")
    print(' ', arm, '; '.join(out))


