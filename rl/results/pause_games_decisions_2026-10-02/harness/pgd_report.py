#!/usr/bin/env python3
"""Pause games vs km3, draft A turns 1-4: the tables. Reads positions_A.json and runs/out_*.jsonl, err_*.txt; writes markdown + a compact JSON.
usage: pgd_report.py OUTDIR"""
import json, glob, os, re, sys, collections, statistics

D = os.environ.get('PGD_DIR', '/home/dacz8976/pgd')
RUNS = os.environ.get('PGD_RUNS', f'{D}/runs')  # where the pg_pos output of the pilot being reported lives
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
POS = json.load(open(os.environ.get('PGD_POSITIONS', f'{D}/positions_A.json'), encoding='utf-8'))
BYID = {p['id']: p for p in POS}
GAMES = {  # game stem -> (result, order, opponent, review folder)
    '143309': ('won 3-0 (normal win)', 'second', 'もつ (Psychic: Sigilyph, Ralts line, Mewtwo ex)'),
    '115323': ('lost 2-3', 'first', '草根 (Fighting: Snorlax, Skull Fossil, Rampardos, Arena of Antiquity)'),
    '143837': ('won 2-1 by opponent concession (a full win)', 'first', '限界社会人 (Grass: Ogerpon ex, Meowscarada ex)'),
    '114458': ('won 3-2', 'second', 'PlumaDeArticun (Fire: Chingling, Aerodactyl, Chandelure)'),
    '132311': ('won 2-0 (opponent timed out)', 'first', 'hk2 (Grass/Fighting: Shaymin, Furfrou, Flygon ex)'),
    '020315': ('deck 03 (Wailord / Indeedee wall): lost 1-3', 'second', 'るか (Water: Feebas, Frigibax / Baxcalibur, Palkia ex, Milotic ex)'),
    '020920': ('deck 03 (Wailord / Indeedee wall): won by opponent concession (a full win), 0-0 on points', 'second', 'おさるの上司 (Fire: Charmander line, Entei ex)'),
    '023418': ('deck 03 (Wailord / Indeedee wall): won by opponent concession (a full win), 0-1 on points', 'first', 'KO歐~YOU (Fighting: Bonsly, Riolu / Lucario / Mega Lucario ex, Hitmonchan)'),
    '021402': ('deck 03 (Wailord / Indeedee wall): lost 0-3', 'first', 'Psychic (Meloetta, Giratina ex, Mega Gardevoir ex, Mega Diancie ex)'),
    '022135': ('deck 03 (Wailord / Indeedee wall): lost 1-3 after 30 turns', 'first', 'だんくしゅー (Swablu / Mega Altaria ex, Froakie)'),
}
DRAW = ("Play:Professor's Research", "Play:Copycat")
IGNORE = ('EndTurn', 'ResolveAttackRetaliation')


def is_draw(l):
    return l in DRAW or l.startswith('Play:Poké Ball') or l.startswith('Play:Poke Ball')


def norm(l):
    l = re.sub(r'^Ability(:[^@]+)?@\d+$', 'Ability', l)  # the dump's labels carry no ability title; which of two identical users (Indeedee ex) is not compared
    return re.sub(r'^(Place:[^@]+)@\d+$', r'\1', l)  # the empty Bench slot he used is not recorded


def cut(plan, keep_endturn_only=True):
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


def kind(l):
    if l is None:
        return 'end'
    for k in ('Attack', 'Attach', 'Evolve', 'Play', 'Tool', 'Retreat', 'RetreatPay', 'Activate', 'Promote', 'Place', 'Heal', 'MistyTarget', 'UseStadium', 'Ability', 'EndTurn'):
        if l.startswith(k):
            return k
    return 'other'


import difflib

PRIORITY = ['Supporter/Item choice or order', 'Tool placement', 'evolution timing/target', 'attack choice', 'retreat/promotion',
            'Energy attachment target', 'Energy attachment timing', 'bench development']


def tags_of(his_items, km_items):
    items = his_items + km_items
    tags = []
    if any(x.startswith('Play:') for x in items):
        tags.append('Supporter/Item choice or order' + (' (a draw card)' if any(is_draw(x) for x in items) else ''))
    if any(x.startswith('Tool:') or 'Elegant Cape' in x for x in items):
        tags.append('Tool placement')
    if any(x.startswith('Evolve') for x in items):
        tags.append('evolution timing/target')
    if any(x.startswith('Attack') for x in items):
        tags.append('attack choice' if (any(x.startswith('Attack') for x in his_items) and any(x.startswith('Attack') for x in km_items)) else 'attack vs another action')
    if any(x.split('@')[0] in ('Retreat', 'Activate', 'Promote') or x.startswith('Retreat') or x.startswith('RetreatPay') for x in items):
        tags.append('retreat/promotion')
    att = [x for x in items if x.startswith('Attach')]
    if att:
        if any(x.endswith('fx') for x in att):
            tags.append('Turbo Shark Bench target')
        elif any(x.startswith('Attach') for x in his_items) and any(x.startswith('Attach') for x in km_items):
            tags.append('Energy attachment target')
        else:
            tags.append('Energy attachment timing')
    if any(x.startswith('Place') for x in items):
        tags.append('bench development')
    if any(x.startswith('Ability') for x in items):
        tags.append('ability use')
    return tags


def category(his, km):
    """Align his plan with km3's (difflib), tag every unmatched stretch. Returns (primary, all tags, a short description)."""
    if same(his, km):
        return 'same plan', [], ''
    if sorted(his) == sorted(km):
        return 'same actions, different order', [], 'order: his ' + ' → '.join(his) + ' | km3 ' + ' → '.join(km)
    sm = difflib.SequenceMatcher(a=his, b=km, autojunk=False)
    all_tags, desc, primary = [], [], None
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        h, k = his[i1:i2], km[j1:j2]
        # a wildcard Misty target
        if h and k and all('?' in x for x in h + k if x.startswith('MistyTarget')):
            pass
        t = tags_of(h, k)
        if primary is None and t:
            primary = t[0]
        all_tags.extend(x for x in t if x not in all_tags)
        desc.append(f"his [{', '.join(h) or '-'}] ↔ km3 [{', '.join(k) or '-'}]")
    return (primary or 'other'), all_tags, '; '.join(desc)


def runs(pid):
    f = f'{RUNS}/out_{pid}.jsonl'
    lines = [json.loads(l) for l in open(f, encoding='utf-8') if l.strip()]
    return ([l for l in lines if l['kind'] == 'free'], [l for l in lines if l['kind'] == 'forced'], [l for l in lines if l['kind'] == 'position'][0])


def blocks(pid):
    out, cur = {}, None
    for line in open(f'{RUNS}/err_{pid}.txt', encoding='utf-8', errors='replace'):
        if line.startswith('PGSTEP'):
            m = re.match(r'PGSTEP (\S+) seed (\d+) (free|forced) (\d+)', line)
            cur = (int(m.group(2)), m.group(3), int(m.group(4)))
            out[cur] = {}
        elif line.startswith('PGDUMP') and cur and not line.startswith('PGDUMP actor='):
            m = re.match(r'PGDUMP\s+(-?[\d.]+) (.*)$', line.rstrip('\n'))
            if m:
                out[cur][m.group(2)] = float(m.group(1))
    return out


def fmt(plan):
    return ' → '.join(plan) if plan else '(nothing)'


rows = []
for p in POS:
    pid = p['id']
    free, forced, posline = runs(pid)
    # Watch Over (Indeedee ex) is offered by the engine even with nothing damaged, where it does nothing: a position that says `noop_ability`
    # (no Pokemon of his is damaged at the start of the turn) has the bare `Ability` entries dropped from both plans, so a no-op is not a difference
    drop = p.get('noop_ability', False)
    strip = (lambda pl: [x for x in pl if x != 'Ability'] or ['EndTurn']) if drop else (lambda pl: pl)
    his = strip(his_plan(p))
    kms = [tuple(strip(cut(r['plan']))) for r in free]
    n = len(kms)
    first = collections.Counter(k[0] for k in kms)
    same_first = sum(1 for k in kms if k and his and (k[0] == his[0] or '?' in his[0]))
    same_plan = sum(1 for k in kms if same(list(k), his))
    modal, mcount = collections.Counter(kms).most_common(1)[0]
    bl = blocks(pid)
    # km3's own score for his first action vs its best, at the root (mean over seeds)
    gaps, hs = [], []
    for r in free:
        sc = bl.get((r['seed'], 'free', 0), {})
        # his first action's label as the engine prints it (Place slot unknown -> any slot)
        cand = [v for k2, v in sc.items() if norm(k2) == his[0]] if his else []
        if sc and cand:
            hs.append(max(cand))
            gaps.append(max(sc.values()) - max(cand))
    rows.append(dict(id=pid, game=p['game'], his_turn=p['his_turn'], turn_count=p['turn_count'], hand_source=p['hand_source'], his=his, n=n,
                     first=dict(first), same_first=same_first, same_plan=same_plan, modal=list(modal), modal_n=mcount,
                     cat=category(his, list(modal))[0], tags=category(his, list(modal))[1],
                     desc=category(his, list(modal))[2] + (' [Watch Over with nothing damaged does nothing: ignored in both plans]' if drop else ''),
                     gap=(statistics.mean(gaps) if gaps else None),
                     plans=[(list(k), c) for k, c in collections.Counter(kms).most_common()], summary=posline['summary'], notes=p['notes'],
                     mid_turn=pid.endswith('b'), forced=bool(forced), milestones=p.get('milestones', []), heldout=p.get('heldout', False)))

json.dump(rows, open(f'{OUT}/summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def verdict(r):
    k = r['same_first'] / r['n']
    if k >= 10 / 12: return 'agree'
    if k <= 2 / 12: return 'differ'
    return 'split'


md = []
for g, (res, order, opp) in GAMES.items():
    md.append(f"## Game {g}: {res}; he went {order}; opponent {opp}\n")
    md.append('| his turn | game turn | hand | his plan (to the first draw) | km3 first action over 12 seeds | same first action | same plan to first draw | km3 modal plan (seeds) | category (all tags) | what differs | km3 root gap (his first action) | milestones |')
    md.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        if r['game'] != g:
            continue
        label = f"{r['his_turn']}{' (mid-turn)' if r['mid_turn'] else ''}"
        fa = ', '.join(f"{k} ×{v}" for k, v in sorted(r['first'].items(), key=lambda kv: -kv[1]))
        gap = '' if r['gap'] is None else f"{r['gap']:.0f}"
        md.append(f"| {label} | {r['turn_count']} | {r['hand_source']} | {fmt(r['his'])} | {fa} | {r['same_first']}/{r['n']} ({verdict(r)}) | {r['same_plan']}/{r['n']} | {fmt(r['modal'])} ({r['modal_n']}/{r['n']}) | {r['cat']}{' (also: ' + ', '.join(t for t in r['tags'] if t != r['cat']) + ')' if len(r['tags']) > 1 else ''} | {r['desc']} | {gap} | {', '.join(r['milestones'])} |")
    md.append('')
open(f'{OUT}/TABLES.md', 'w', encoding='utf-8').write('\n'.join(md))

# the 20 turn-start positions only (not the mid-turn ones) for the totals
MAXTURN = int(os.environ.get('PGD_MAXTURN', '99'))
ts = [r for r in rows if not r['mid_turn'] and r['his_turn'] <= MAXTURN and not r['id'].startswith('D3-')]  # the draft A turn starts; deck 03 has its own totals below
d3 = [r for r in rows if r['id'].startswith('D3-') and not r['mid_turn']]
cnt = collections.Counter(verdict(r) for r in ts)
plan_same = sum(1 for r in ts if r['same_plan'] / r['n'] >= 10 / 12)
cats = collections.Counter(r['cat'] for r in ts)
print(len(ts), 'turn-start positions;', dict(cnt), '; same plan (>=10/12):', plan_same)
for c, v in cats.most_common():
    print(f'  {v:>2}  {c}')
for r in rows:
    print(f"{r['id']:<16} {verdict(r):<7} first {r['same_first']:>2}/12 plan {r['same_plan']:>2}/12  | {r['cat']}")

# ---- totals for the summary page (the 20 turn-start positions)
tagcount = collections.Counter()
for r in ts:
    for t in set(r['tags']):
        tagcount[re.sub(r' \(a draw card\)$', '', t)] += 1
drawtag = sum(1 for r in ts if any('draw card' in t for t in r['tags']))
irida_extra = [r['id'] for r in ts if 'Play:Irida' in r['modal'] and not any('Irida' in x for x in r['his'])]
equal_modal = [r['id'] for r in ts if same(r['modal'], r['his'])]
equal10 = [r['id'] for r in ts if r['same_plan'] >= 10]
first_same_plan_differs = [r['id'] for r in ts if r['same_first'] >= 10 and r['same_plan'] < 10]
print('\nposition counts by tag (a position can carry several):')
for t, v in tagcount.most_common():
    print(f'  {v:>2}  {t}')
print('  of which involve a draw card:', drawtag)
print('km3 plays Irida where his plan does not:', len(irida_extra), irida_extra)
print('modal km3 plan equals his:', len(equal_modal), equal_modal)
print('same plan in >=10/12 seeds:', len(equal10), equal10)
print('first action agrees (>=10/12) but the plan differs later:', len(first_same_plan_differs), first_same_plan_differs)
deck03 = dict(positions=len(d3), verdicts=dict(collections.Counter(verdict(r) for r in d3)),
              first_action_agrees=[r['id'] for r in d3 if r['same_first'] / r['n'] >= 10 / 12],
              same_plan_10=[r['id'] for r in d3 if r['same_plan'] / r['n'] >= 10 / 12],
              categories={c: [r['id'] for r in d3 if r['cat'] == c] for c in sorted({r['cat'] for r in d3})}) if d3 else {}
json.dump(dict(verdicts=dict(cnt), tags=dict(tagcount), draw_tag=drawtag, irida_extra=irida_extra, equal_modal=equal_modal, equal10=equal10,
               first_same_plan_differs=first_same_plan_differs, deck03=deck03), open(f'{OUT}/totals.json', 'w'), indent=1)
