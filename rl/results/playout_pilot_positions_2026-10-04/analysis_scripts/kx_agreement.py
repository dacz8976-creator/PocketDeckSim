#!/usr/bin/env python3
"""kx3 (play-out pilot) v the decision maker, v km3, on the pause-games positions: agreement tables and the KX_TRACE change counts.
Read-only: reads positions_kx.json (repo), the kx3 run (runs_kx3_trace), km3's reference runs (runs_km3, cross-checked with runs and
report_km3/summary.json), and writes markdown + JSON into the scratchpad only.
usage: python3 kx_agreement.py [OUTDIR]"""
import json, glob, re, os, sys, collections, statistics

REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
PDIR = f'{REPO}/rl/results/pause_games_decisions_2026-10-02'
POSF = f'{PDIR}/positions_kx.json'
D = '/home/dacz8976/pgd'
KX = f'{D}/runs_kx3_trace'
KM = f'{D}/runs_km3'
KMREF = f'{D}/runs'           # the original 12-seed reference (cross-check only)
KXREP = f'{D}/report_kx3_trace/summary.json'
KMREP = f'{D}/report_km3/summary.json'
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

# ---------------- the report's own grading (pgd_report.py, unchanged) ----------------
DRAW = ("Play:Professor's Research", "Play:Copycat", "Play:Lisia", "Play:Clemont", "Play:Sightseer", "Play:Order Pad",
        "Play:Team Rocket's Researcher", "Play:Quick-Grow Extract")
IGNORE = ('EndTurn', 'ResolveAttackRetaliation')


def is_draw(l):
    return l in DRAW or l.startswith('Play:Poké Ball') or l.startswith('Play:Poke Ball')


def norm(l):
    l = re.sub(r'^Ability(:[^@]+)?@\d+$', 'Ability', l)
    return re.sub(r'^(Place:[^@]+)@\d+$', r'\1', l)


def cut(plan):
    out = []
    for l in plan:
        if l in IGNORE:
            continue
        out.append(norm(l))
        if is_draw(l):
            break
    if not out and plan:
        return ['EndTurn']
    return out


def his_plan(p):
    return cut([l for l in p['his_plan'] if not l.startswith('(')])


def same(a, b):
    return len(a) == len(b) and all(x == y or '?' in x or '?' in y for x, y in zip(a, b))


def eq1(a, b):
    return a == b or '?' in a or '?' in b


def strip_fn(p):
    if p.get('noop_ability', False):
        return lambda pl: [x for x in pl if x != 'Ability'] or ['EndTurn']
    return lambda pl: pl


# ---------------- engine Debug form (KX_TRACE) -> the harness label (pg_label in pgd_patch.py) ----------------
def label(mv):
    mv = mv.strip()
    if mv == 'EndTurn':
        return 'EndTurn'
    m = re.match(r'^Play \{ trainer_card: \S+ \d+ (.+) \}$', mv)
    if m:
        return f'Play:{m.group(1)}'
    m = re.match(r'^Place\((?:Pokemon|Trainer)\(\S+ \d+ (.+)\), (\d+)\)$', mv)
    if m:
        return f'Place:{m.group(1)}@{m.group(2)}'
    m = re.match(r'^Evolve \{ evolution: (?:Pokemon|Trainer)\(\S+ \d+ (.+)\), in_play_idx: (\d+)', mv)
    if m:
        return f'Evolve:{m.group(1)}@{m.group(2)}'
    m = re.match(r'^UseAbility \{ in_play_idx: (\d+) \}$', mv)
    if m:
        return f'Ability@{m.group(1)}'
    m = re.match(r'^Attack\(Attack \{.*?title: "([^"]*)"', mv)
    if m:
        return f'Attack:{m.group(1)}'
    m = re.match(r'^Retreat\((\d+)\)$', mv)
    if m:
        return f'Retreat:{m.group(1)}'
    m = re.match(r'^Attach \{ attachments: \[(.*)\], is_turn_energy: (true|false) \}$', mv)
    if m:
        parts = re.findall(r'\((\d+), (\w+), (\d+)\)', m.group(1))
        return 'Attach:' + '+'.join(f'{n}{e}@{i}' for n, e, i in parts) + (' zone' if m.group(2) == 'true' else ' fx')
    m = re.match(r'^AttachTool \{ in_play_idx: (\d+), tool_card: (?:Trainer|Pokemon)\(\S+ \d+ (.+)\) \}$', mv)
    if m:
        return f'Tool:{m.group(2)}@{m.group(1)}'
    m = re.match(r'^Heal \{ in_play_idx: (\d+), amount: (\d+)', mv)
    if m:
        return f'Heal:{m.group(2)}@{m.group(1)}'
    m = re.match(r'^(Activate|Promote) \{ player: (\d+), in_play_idx: (\d+) \}$', mv)
    if m:
        return f'{m.group(1)}:{m.group(2)}@{m.group(3)}'
    m = re.match(r'^ChooseMistyTarget \{ in_play_idx: (\d+) \}$', mv)
    if m:
        return f'MistyTarget@{m.group(1)}'
    m = re.match(r'^ChooseRetreatEnergy \{ to_in_play_idx: (\d+)', mv)
    if m:
        return f'RetreatPay:{m.group(1)}'
    return re.split(r'[ {(]', mv)[0]


KINDS = ['Supporter/Item play', 'attach Energy', 'retreat/promote', 'attack', 'evolve', 'ability', 'end turn', 'other']


def kind(l):
    if l.startswith('Play:'):
        return 'Supporter/Item play'
    if l.startswith('Attach:'):
        return 'attach Energy'
    if l.startswith(('Retreat', 'Activate', 'Promote', 'RetreatPay')):
        return 'retreat/promote'
    if l.startswith('Attack:'):
        return 'attack'
    if l.startswith('Evolve:'):
        return 'evolve'
    if l.startswith('Ability'):
        return 'ability'
    if l == 'EndTurn':
        return 'end turn'
    return 'other'


def other_sub(l):
    return {'Place': 'bench a Basic Pokémon', 'Tool': 'which Pokémon gets the Tool', 'UseStadium': 'use the Stadium',
            'Heal': 'which Pokémon to heal', 'MistyTarget': "Misty's target"}.get(re.split(r'[:@]', l)[0], re.split(r'[:@]', l)[0])


# ---------------- plain-language rendering on a tracked board ----------------
def board_of(summary):
    me = {b['slot']: b['card'] for b in summary['me']['board']}
    opp = {b['slot']: b['card'] for b in summary['opp']['board']}
    return me, opp


def where(board, i):
    nm = board.get(i, f'slot {i}')
    return f'{nm} (Active)' if i == 0 else f'{nm} (Bench {i})'


def pretty(l, me, opp):
    if l in ('EndTurn', 'end of turn'):
        return 'end the turn'
    if l.startswith('Play:'):
        return 'play ' + l[5:]
    m = re.match(r'^Place:([^@]+)(?:@(\d+))?$', l)
    if m:
        return 'bench ' + m.group(1)
    m = re.match(r'^Evolve:(.+)@(\d+)$', l)
    if m:
        return f"evolve {where(me, int(m.group(2)))} into {m.group(1)}"
    m = re.match(r'^Attach:(\d+)(\w+)@(\d+) (zone|fx)$', l)
    if m:
        who = where(me, int(m.group(3)))
        return (f"attach {m.group(2)} to {who}" if m.group(4) == 'zone' else f"the attack's {m.group(2)} Energy to {who}")
    m = re.match(r'^Retreat:(\d+)$', l)
    if m:
        return f"retreat {me.get(0, 'the Active')} into {where(me, int(m.group(1)))}"
    if l.startswith('Attack:'):
        return 'attack with ' + l[7:]
    m = re.match(r'^Tool:(.+)@(\d+)$', l)
    if m:
        return f"put {m.group(1)} on {where(me, int(m.group(2)))}"
    m = re.match(r'^Activate:1@(\d+)$', l)
    if m:
        return f"bring the opponent's {opp.get(int(m.group(1)), 'Benched Pokémon')} Active"
    m = re.match(r'^MistyTarget@(\d+|\?)$', l)
    if m:
        return 'Misty on ' + (where(me, int(m.group(1))) if m.group(1).isdigit() else 'a Water Pokémon (target not recorded)')
    m = re.match(r'^Ability(?:@(\d+))?$', l)
    if m:
        return f"use {me.get(int(m.group(1)), 'a Pokémon')}'s Ability" if m.group(1) else 'use an Ability'
    m = re.match(r'^Heal:(\d+)@(\d+)$', l)
    if m:
        return f"heal {m.group(1)} from {where(me, int(m.group(2)))}"
    if l == 'UseStadium':
        return 'use the Stadium'
    return l


def step_board(me, opp, l):
    me, opp = dict(me), dict(opp)
    m = re.match(r'^Place:([^@]+)@(\d+)$', l)
    if m:
        me[int(m.group(2))] = m.group(1)
    m = re.match(r'^Evolve:(.+)@(\d+)$', l)
    if m:
        me[int(m.group(2))] = m.group(1)
    m = re.match(r'^Retreat:(\d+)$', l)
    if m:
        i = int(m.group(1))
        me[0], me[i] = me.get(i), me.get(0)
    m = re.match(r'^Activate:1@(\d+)$', l)
    if m:
        i = int(m.group(1))
        opp[0], opp[i] = opp.get(i), opp.get(0)
    return me, opp


# ---------------- loading ----------------
def load_out(runs, pid):
    free, posline = {}, None
    for l in open(f'{runs}/out_{pid}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        j = json.loads(l)
        if j['kind'] == 'free':
            free[j['seed']] = j
        elif j['kind'] == 'position':
            posline = j
    return free, posline


def load_traces(pid):
    tr, cur = {}, None
    for line in open(f'{KX}/err_{pid}.txt', encoding='utf-8', errors='replace'):
        if line.startswith('PGSTEP'):
            m = re.match(r'PGSTEP (\S+) seed (\d+) (free|forced) (\d+)', line)
            cur = (int(m.group(2)), m.group(3), int(m.group(4)))
        elif line.startswith('KX_TRACE'):
            t = json.loads(line[len('KX_TRACE '):])
            assert cur not in tr, (pid, cur)
            tr[cur] = t
    return tr


POS = json.load(open(POSF, encoding='utf-8'))
BYID = {p['id']: p for p in POS}
RUNIDS = [p['id'] for p in json.load(open(f'{KX}/positions_run.json', encoding='utf-8'))]
MS = ['preparing an attacker', 'managing a sacrifice', 'adapting when the plan fails', 'recognising an immediate win']


def group_of(pid):
    return pid.split('-')[0]


rows, decisions, checks = [], [], collections.Counter()
for k in ('km3 runs_km3 != runs (seed plans)', 'traced step: chosen label != plan label', 'changed flag inconsistent',
          "step 0: kx's km3 proposal != km3 reference run's first action (same seed)", 'kx row != report_kx3_trace/summary.json',
          'km3 row != report_km3/summary.json'):
    checks[k] = 0
mism = []
for pid in RUNIDS:
    p = BYID[pid]
    strip = strip_fn(p)
    his = strip(his_plan(p))
    kxf, kxpos = load_out(KX, pid)
    kmf, _ = load_out(KM, pid)
    kmref, _ = load_out(KMREF, pid)
    tr = load_traces(pid)
    me0, opp0 = board_of(kxpos['summary'])
    kx_seeds = sorted(kxf)
    km_seeds = sorted(kmf)
    kxp = {s: strip(cut(kxf[s]['plan'])) for s in kx_seeds}
    kmp = {s: strip(cut(kmf[s]['plan'])) for s in km_seeds}
    # cross-check km3: runs_km3 = the original reference run, seed by seed
    for s in km_seeds:
        checks['km3 runs_km3 = runs (seed plans)'] += 1
        if kmref.get(s, {}).get('plan') != kmf[s]['plan']:
            checks['km3 runs_km3 != runs (seed plans)'] += 1
    kx_first = sum(1 for s in kx_seeds if kxp[s] and his and eq1(kxp[s][0], his[0]))
    kx_plan = sum(1 for s in kx_seeds if same(kxp[s], his))
    km_first = sum(1 for s in km_seeds if kmp[s] and his and eq1(kmp[s][0], his[0]))
    km_plan = sum(1 for s in km_seeds if same(kmp[s], his))
    km3_first = sum(1 for s in kx_seeds if kmp[s] and his and eq1(kmp[s][0], his[0]))   # km3 on the same 3 seeds (same deal)
    km3_plan = sum(1 for s in kx_seeds if same(kmp[s], his))
    kx_eq_km_first = sum(1 for s in kx_seeds if kxp[s][:1] == kmp[s][:1])
    kx_eq_km_plan = sum(1 for s in kx_seeds if kxp[s] == kmp[s])

    # ---- traces of the free runs: one per step that offered 2+ moves
    H = [norm(l) for l in p['his_plan'] if not l.startswith('(') and l not in IGNORE]
    nchanged = 0
    for s in kx_seeds:
        plan = kxf[s]['plan']
        me, opp = me0, opp0
        for k, lab in enumerate(plan):
            t = tr.get((s, 'free', k))
            if t is not None:
                ch_l, km_l = label(t['chosen']), label(t['km_move'])
                checks['traced steps'] += 1
                if ch_l != lab:
                    checks['traced step: chosen label != plan label'] += 1
                    mism.append((pid, s, k, ch_l, lab))
                if t['changed'] != (t['chosen'] != t['km_move']):
                    checks['changed flag inconsistent'] += 1
                if k == 0:
                    checks['step 0 traced'] += 1
                    if km_l != kmf[s]['plan'][0]:
                        checks["step 0: kx's km3 proposal != km3 reference run's first action (same seed)"] += 1
                # the decision maker's choice at this state: only when kx's line so far equals his recorded line
                prefix = [norm(x) for x in plan[:k] if x not in IGNORE]
                if len(prefix) <= len(H) and same(prefix, H[:len(prefix)]):
                    if len(prefix) < len(H):
                        h = H[len(prefix)]
                    else:
                        h = 'EndTurn' if not (H and (H[-1].startswith('Attack:') or is_draw(H[-1]))) else None
                else:
                    h = None
                chosen_c = next((c for c in t['candidates'] if c['move'] == t['chosen']), None)
                best = max(t['candidates'], key=lambda c: c['score'] if c['score'] is not None else -1)
                rel = None
                if t['changed'] and h is not None:
                    a, b = eq1(norm(ch_l), h), eq1(norm(km_l), h)
                    rel = 'toward' if a and not b else ('away' if b and not a else ('neither' if not a and not b else 'both?'))
                elif t['changed']:
                    rel = 'not comparable'
                decisions.append(dict(id=pid, group=group_of(pid), decision_maker=p.get('decision_maker'), exact=bool(p.get('exact_list')),
                                      seed=s, step=k, kind=kind(km_l), kx_kind=kind(ch_l), km=km_l, kx=ch_l, his=h,
                                      km_pretty=pretty(km_l, me, opp), kx_pretty=pretty(ch_l, me, opp),
                                      his_pretty=(pretty(h, me, opp) if h else None),
                                      changed=t['changed'], reason=t['reason'],
                                      within_noise=t['reason'].startswith('within the noise'),
                                      kept_best=t['reason'].startswith("km's move has the best"),
                                      lead=(chosen_c['diff'] if t['changed'] else (best['diff'] if t['reason'].startswith('within') else 0.0)),
                                      se=(chosen_c['se'] if t['changed'] else (best['se'] if t['reason'].startswith('within') else None)),
                                      n_moves=len(t['candidates']), dropped=len(t['dropped']), failed_rounds=t['failed_rounds'],
                                      lists=t['lists'], ms=t['ms'], rel=rel, mid_turn=k > 0))
                nchanged += t['changed']
            me, opp = step_board(me, opp, lab)
    rows.append(dict(id=pid, group=group_of(pid), game=p['game'], decision_maker=p.get('decision_maker'), exact=bool(p.get('exact_list')),
                     approximate=bool(p.get('approximate')), milestones=p.get('milestones', []), his=his,
                     his_first_pretty=(pretty(his[0], me0, opp0) if his else 'ended the turn with no play (an empty plan never counts as agreeing)'),
                     kx_first=kx_first, kx_plan=kx_plan, n_kx=len(kx_seeds), km_first=km_first, km_plan=km_plan, n_km=len(km_seeds),
                     km3_first=km3_first, km3_plan=km3_plan, kx_eq_km_first=kx_eq_km_first, kx_eq_km_plan=kx_eq_km_plan,
                     kx_firsts=[kxp[s][0] if kxp[s] else '' for s in kx_seeds],
                     kx_firsts_pretty=[pretty(kxp[s][0], me0, opp0) if kxp[s] else '' for s in kx_seeds],
                     km_firsts=dict(collections.Counter(kmp[s][0] if kmp[s] else '' for s in km_seeds)),
                     km_firsts_pretty=dict(collections.Counter(pretty(kmp[s][0], me0, opp0) if kmp[s] else '' for s in km_seeds)),
                     kx_plans=[kxp[s] for s in kx_seeds], km_plans_s123=[kmp[s] for s in kx_seeds], kx_changes=nchanged))

# forced-replay traces (A- positions with a recorded "force" line): kx asked along his own line
forced = []
for pid in RUNIDS:
    for (s, kd, k), t in load_traces(pid).items():
        if kd == 'forced':
            forced.append(dict(id=pid, seed=s, step=k, changed=t['changed'], within=t['reason'].startswith('within')))

# ---- cross-check with the runner's own reports
kxrep = {r['id']: r for r in json.load(open(KXREP, encoding='utf-8'))}
kmrep = {r['id']: r for r in json.load(open(KMREP, encoding='utf-8'))}
for r in rows:
    a = kxrep.get(r['id'])
    if a is None or (a['same_first'], a['same_plan'], a['n']) != (r['kx_first'], r['kx_plan'], r['n_kx']):
        checks['kx row != report_kx3_trace/summary.json'] += 1
    b = kmrep.get(r['id'])
    if b is None or (b['same_first'], b['same_plan'], b['n']) != (r['km_first'], r['km_plan'], r['n_km']):
        checks['km3 row != report_km3/summary.json'] += 1
        mism.append(('kmrep', r['id'], (r['km_first'], r['km_plan'], r['n_km']), (b or {}).get('same_first'), (b or {}).get('same_plan')))


# ---------------- tables ----------------
def c3(rs, key):
    """all 3 / some / none over kx's 3 seeds"""
    return (sum(1 for r in rs if r[key] == 3), sum(1 for r in rs if 0 < r[key] < 3), sum(1 for r in rs if r[key] == 0))


def c12(rs, key):
    return (sum(1 for r in rs if r[key] >= 10), sum(1 for r in rs if 2 < r[key] < 10), sum(1 for r in rs if r[key] <= 2))


def cell(t):
    return ' / '.join(str(x) for x in t)


def table(rs_by_label, title_col='situation'):
    out = [f'| {title_col} | positions | kx first action = his: all 3 / some / none | km3 first action (12 seeds): agree / split / differ | '
           'km3 on the same 3 seeds: all 3 / some / none | kx whole plan = his: all 3 / some / none | km3 whole plan (12 seeds): agree / split / differ | '
           'km3 whole plan, same 3 seeds: all 3 / some / none |', '|---|---|---|---|---|---|---|---|']
    for lab, rs in rs_by_label:
        if not rs:
            continue
        out.append(f"| {lab} | {len(rs)} | {cell(c3(rs, 'kx_first'))} | {cell(c12(rs, 'km_first'))} | {cell(c3(rs, 'km3_first'))} | "
                   f"{cell(c3(rs, 'kx_plan'))} | {cell(c12(rs, 'km_plan'))} | {cell(c3(rs, 'km3_plan'))} |")
    return out


def by_ms(rs):
    lst = [('all positions', rs)] + [(m, [r for r in rs if m in r['milestones']]) for m in MS]
    lst.append(('(no milestone)', [r for r in rs if not r['milestones']]))
    return lst


def seed_pairs(rs, a='kx_first', b='km3_first'):
    """seed by seed, kx v km3 on the same deal: both agree with him / only kx / only km3 / neither"""
    both = only_kx = only_km = neither = 0
    for r in rs:
        for i in range(r['n_kx']):
            his0 = r['his'][0] if r['his'] else None
            kxa = r['kx_plans'][i][:1] and his0 and eq1(r['kx_plans'][i][0], his0)
            kma = r['km_plans_s123'][i][:1] and his0 and eq1(r['km_plans_s123'][i][0], his0)
            if a == 'kx_plan':
                kxa, kma = same(r['kx_plans'][i], r['his']), same(r['km_plans_s123'][i], r['his'])
            both += bool(kxa and kma); only_kx += bool(kxa and not kma); only_km += bool(kma and not kxa); neither += bool(not kxa and not kma)
    return both, only_kx, only_km, neither


md = ['# kx3 v the decision maker and v km3: agreement tables (pause-games positions, development set)\n']
B = [r for r in rows if r['group'] == 'B']
md.append('## 1. Exact lists: draft A v the computer deck (B- positions), by decision maker\n')
for who in ('Auto', 'Dustin'):
    rs = [r for r in B if r['decision_maker'] == who]
    md.append(f'### Decision maker: {who} ({len(rs)} positions, {len({r["game"] for r in rs})} games)\n')
    md += table(by_ms(rs))
    fp, pp = seed_pairs(rs), seed_pairs(rs, 'kx_plan')
    md.append(f'\nSeed by seed on the same deals ({sum(fp)} position-seeds): first action = his for both kx and km3 {fp[0]}, kx only {fp[1]}, km3 only {fp[2]}, neither {fp[3]}. '
              f'Whole plan: both {pp[0]}, kx only {pp[1]}, km3 only {pp[2]}, neither {pp[3]}.\n')

md.append('\n## 2. Descriptive only (the opponent\'s list unknown to the runner; A-, D3-, L8-; LR- added for completeness, reconstructed own list)\n')
GN = (('A', 'A- (draft A v humans)'), ('D3', 'D3- (deck 03)'), ('L8', 'L8- (brew 8)'), ('LR', 'LR- (reconstructed list)'))
md += table([(f'{name}: {lab}', rs) for g, name in GN for lab, rs in by_ms([r for r in rows if r['group'] == g])], 'group: situation')
for g, name in GN:
    fp = seed_pairs([r for r in rows if r['group'] == g])
    md.append(f'\n{name}, seed by seed ({sum(fp)} position-seeds), first action = his: both {fp[0]}, kx only {fp[1]}, km3 only {fp[2]}, neither {fp[3]}.')

# ---- 3. the trace
free = decisions
md.append('\n## 3. Every kx decision traced (free runs: the pilot playing its own turn up to the first draw; steps with 2+ legal moves)\n')
md.append('| kind of decision (km3\'s proposed move) | decisions | kx changed km3\'s move | kept: km3\'s move scored best | kept: another move led, within the noise |')
md.append('|---|---|---|---|---|')
for k in KINDS + ['all']:
    ds = free if k == 'all' else [d for d in free if d['kind'] == k]
    md.append(f"| {k} | {len(ds)} | {sum(d['changed'] for d in ds)} | {sum(d['kept_best'] for d in ds)} | {sum(d['within_noise'] for d in ds)} |")
oth = collections.Counter(other_sub(d['km']) for d in free if d['kind'] == 'other')
md.append('\n"other" holds: ' + '; '.join(f'{k} {v}' for k, v in oth.most_common()) + '.\n')
md.append('| group | decisions | changed | within the noise | first-action decisions | changed there |')
md.append('|---|---|---|---|---|---|')
for g in ('B', 'A', 'D3', 'L8', 'LR'):
    ds = [d for d in free if d['group'] == g]
    f0 = [d for d in ds if d['step'] == 0]
    md.append(f"| {g}- | {len(ds)} | {sum(d['changed'] for d in ds)} | {sum(d['within_noise'] for d in ds)} | {len(f0)} | {sum(d['changed'] for d in f0)} |")
ch = [d for d in free if d['changed']]
wn = [d for d in free if d['within_noise']]


def med(xs):
    return statistics.median(xs) if xs else float('nan')


lead_ch = [d['lead'] for d in ch]
se_ch = [d['se'] for d in ch]
z_ch = [d['lead'] / d['se'] for d in ch if d['se']]
md.append(f"\nChanged: {len(ch)} of {len(free)}. Median lead {med(lead_ch):+.3f} (share of play-outs won; 16 play-outs, so 0.0625 = one more win), "
          f"median standard error {med(se_ch):.3f}, median lead / SE {med(z_ch):.2f}; lead range {min(lead_ch):+.3f} to {max(lead_ch):+.3f}.")
md.append(f"Within the noise (another move led, km3's kept): {len(wn)}; median lead of the best other move {med([d['lead'] for d in wn]):+.3f}, median SE {med([d['se'] for d in wn if d['se'] is not None]):.3f}.")
md.append(f"Changes by closeness to the 2-SE threshold: lead/SE 2.0-2.5: {sum(1 for z in z_ch if z < 2.5)}; 2.5-3: {sum(1 for z in z_ch if 2.5 <= z < 3)}; 3 or more: {sum(1 for z in z_ch if z >= 3)}. "
          f"Median number of moves compared on a changed decision: {med([d['n_moves'] for d in ch])}.")
et = [d for d in ch if d['kx'] == 'EndTurn']
kmrow = {r['id']: r for r in rows}
skipped_attack = [d for d in et if any(x.startswith('Attack:') for x in kmrow[d['id']]['km_plans_s123'][d['seed'] - 1])]
md.append(f"Changes where kx ends the turn: {len(et)} ({', '.join(sorted(set(d['id'] for d in et)))}); on {len(skipped_attack)} of them km3's plan on the same seed attacks and kx's turn has no attack.")
cross = collections.Counter((d['kind'], d['kx_kind']) for d in ch)
md.append('\nChanges, km3\'s move kind -> kx\'s move kind: ' + '; '.join(f'{a} -> {b}: {n}' for (a, b), n in cross.most_common()) + '.')
md.append(f"\nForced replays (kx asked along his recorded line; 5 A- positions): {len(forced)} decisions traced, {sum(f['changed'] for f in forced)} changed, {sum(f['within'] for f in forced)} within the noise (not in the table above).")
md.append(f"Decisions with more than 12 legal moves (some dropped by the cap): {sum(1 for d in free if d['dropped'])}; play-out rounds lost to engine panics: {sum(d['failed_rounds'] for d in free)}.")
md.append(f"Time per traced decision: median {med([d['ms'] for d in free]) / 1000:.1f} s.")
lists = collections.Counter()
for d in free:
    for k in d['lists']:
        lists[(d['group'], re.sub(r' \(.*', '', k))] += d['lists'][k]
md.append('Opponent lists drawn in the play-outs (group, list: play-outs): ' + '; '.join(f'{g} {k}: {v}' for (g, k), v in sorted(lists.items())) + '.')

# ---- 4. toward / away, exact lists only
md.append('\n## 4. Where kx changed km3\'s move on an exact-list (B-) position: toward or away from the decision maker\'s choice\n')
bch = [d for d in ch if d['group'] == 'B']
for who in ('Auto', 'Dustin', None):
    ds = [d for d in bch if who is None or d['decision_maker'] == who]
    c = collections.Counter(d['rel'] for d in ds)
    md.append(f"- {'all' if who is None else who}: {len(ds)} changes; toward {c['toward']}, away {c['away']}, neither {c['neither']}, "
              f"not comparable (kx's line had already left his) {c['not comparable']}" + (f", both? {c['both?']}" if c['both?'] else ''))
md.append('\n| position | decision maker | seed | step | km3 proposed | kx played | his choice there | lead (SE) | change |')
md.append('|---|---|---|---|---|---|---|---|---|')
for d in sorted(bch, key=lambda d: (d['id'], d['seed'], d['step'])):
    md.append(f"| {d['id']} | {d['decision_maker']} | {d['seed']} | {d['step'] + 1} | {d['km_pretty']} | {d['kx_pretty']} | {d['his_pretty'] or '(not the same state)'} | "
              f"{d['lead']:+.3f} ({d['se']:.3f}) | {d['rel']} |")
nb = [d for d in ch if d['group'] != 'B']
c = collections.Counter(d['rel'] for d in nb)
md.append(f"\nDescriptive only, the other groups: {len(nb)} changes; toward {c['toward']}, away {c['away']}, neither {c['neither']}, not comparable {c['not comparable']}.")
md.append('\n| position | seed | step | km3 proposed | kx played | his choice there | lead (SE) | change |')
md.append('|---|---|---|---|---|---|---|---|')
for d in sorted(nb, key=lambda d: (d['id'], d['seed'], d['step'])):
    md.append(f"| {d['id']} | {d['seed']} | {d['step'] + 1} | {d['km_pretty']} | {d['kx_pretty']} | {d['his_pretty'] or '(not the same state)'} | "
              f"{d['lead']:+.3f} ({d['se']:.3f}) | {d['rel']} |")

# ---- per-position, B- (every row) and the rows where kx and km3 part
md.append('\n## Per position, exact lists (B-)\n')
md.append('| position | decision maker | milestones | his first action | kx first action, seeds 1/2/3 | km3 first action (12 seeds) | kx first = his | km3 first = his (12) | kx plan = his | km3 plan = his (12) | kx changes |')
md.append('|---|---|---|---|---|---|---|---|---|---|---|')
for r in sorted(B, key=lambda r: (r['decision_maker'], r['id'])):
    kmf = ', '.join(f'{k} ×{v}' for k, v in sorted(r['km_firsts_pretty'].items(), key=lambda kv: -kv[1]))
    md.append(f"| {r['id']} | {r['decision_maker']} | {', '.join(r['milestones']) or '-'} | {r['his_first_pretty']} | {' / '.join(r['kx_firsts_pretty'])} | {kmf} | "
              f"{r['kx_first']}/3 | {r['km_first']}/12 | {r['kx_plan']}/3 | {r['km_plan']}/12 | {r['kx_changes']} |")

md.append('\n## Checks\n')
for k, v in sorted(checks.items()):
    md.append(f'- {k}: {v}')
md.append(f'- mismatches listed: {mism[:20]}')

os.makedirs(OUT, exist_ok=True)
open(f'{OUT}/kx_agreement_tables.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
json.dump(dict(rows=rows, decisions=decisions, forced=forced, checks=dict(checks)), open(f'{OUT}/kx_agreement_rows.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n'.join(md))
