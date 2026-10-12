#!/usr/bin/env python3
"""New pause games v a pilot: his turn start as a position, the pilot's plan (to the first draw card) against his, by kind of difference.
Same comparison rules as pgd_report.py of the Oct 2 reading (bare Ability labels normalised, EndTurn ignored, a plan is cut after its first draw card,
a Place slot is not compared), without that script's game table.
usage: kw_report.py POSITIONS.json RUNS_DIR OUT_PREFIX BOT_NAME [GAMES_META.json]"""
import json, os, re, sys, difflib, collections

POS = json.load(open(sys.argv[1], encoding='utf-8'))
RUNS, OUT, BOT = sys.argv[2], sys.argv[3], sys.argv[4]
META = json.load(open(sys.argv[5], encoding='utf-8')) if len(sys.argv) > 5 else {}

DRAW = ("Play:Professor's Research", "Play:Copycat", "Play:Lisia", "Play:Clemont", "Play:Sightseer", "Play:Order Pad", "Play:Team Rocket's Researcher",
        "Play:Quick-Grow Extract")
IGNORE = ('EndTurn', 'ResolveAttackRetaliation')


def is_draw(l):
    return l in DRAW or l.startswith('Play:Poké Ball') or l.startswith('Play:Poke Ball')


def norm(l):
    l = re.sub(r'^Ability(:[^@]+)?@\d+$', 'Ability', l)
    return re.sub(r'^(Place:[^@]+)@\d+$', r'\1', l)


STOP = ("Play:Sabrina",)  # the opponent chooses his new Active: the harness's play-out stops there (pg_pos breaks at the opponent's frame)


def cut(plan):
    out = []
    for l in plan:
        if l in IGNORE:
            continue
        out.append(norm(l))
        if is_draw(l) or l in STOP:
            break
    if not out and plan:
        return ['EndTurn']
    return out


def same(a, b):
    return len(a) == len(b) and all(x == y or '?' in x or '?' in y for x, y in zip(a, b))


def tags_of(his_items, km_items):
    items = his_items + km_items
    tags = []
    if any(x.startswith('Play:') for x in items):
        tags.append('Supporter/Item choice or order')
    if any(x.startswith('Tool:') for x in items):
        tags.append('Tool placement')
    if any(x.startswith('Evolve') for x in items):
        tags.append('evolution timing/target')
    if any(x.startswith('Attack') for x in items):
        tags.append('attack choice' if (any(x.startswith('Attack') for x in his_items) and any(x.startswith('Attack') for x in km_items)) else 'attack vs another action')
    if any(x.startswith('Retreat') or x.startswith('Activate') or x.startswith('Promote') for x in items):
        tags.append('retreat/promotion')
    att = [x for x in items if x.startswith('Attach')]
    if att:
        tags.append('Energy attachment target' if (any(x.startswith('Attach') for x in his_items) and any(x.startswith('Attach') for x in km_items)) else 'Energy attachment timing')
    if any(x.startswith('Place') for x in items):
        tags.append('bench development')
    if any(x.startswith('Ability') for x in items):
        tags.append('ability use')
    return tags


def category(his, km):
    if same(his, km):
        return 'same plan', [], ''
    if sorted(his) == sorted(km):
        return 'same actions, different order', [], 'order: his ' + ' → '.join(his) + ' | ' + BOT + ' ' + ' → '.join(km)
    sm = difflib.SequenceMatcher(a=his, b=km, autojunk=False)
    all_tags, desc, primary = [], [], None
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        h, k = his[i1:i2], km[j1:j2]
        t = tags_of(h, k)
        if primary is None and t:
            primary = t[0]
        all_tags.extend(x for x in t if x not in all_tags)
        desc.append(f"his [{', '.join(h) or '-'}] ↔ {BOT} [{', '.join(k) or '-'}]")
    return (primary or 'other'), all_tags, '; '.join(desc)


def kind(l):
    if l is None:
        return 'end'
    for k in ('Attack', 'Attach', 'Evolve', 'Play', 'Tool', 'Retreat', 'RetreatPay', 'Activate', 'Promote', 'Place', 'Heal', 'UseStadium', 'Ability', 'EndTurn'):
        if l.startswith(k):
            return k
    return 'other'


def runs(pid):
    f = f'{RUNS}/out_{pid}.jsonl'
    if not os.path.exists(f):
        return None
    lines = [json.loads(l) for l in open(f, encoding='utf-8') if l.strip()]
    return [l for l in lines if l['kind'] == 'free'], [l for l in lines if l['kind'] == 'position'][0]


rows = []
for p in POS:
    r = runs(p['id'])
    if r is None:
        continue
    free, posline = r
    if not free:
        print('NO RUN OUTPUT (position problems):', p['id'], posline.get('problems'))
        continue
    plan_raw = [l for l in p['his_plan'] if not l.startswith('(')]
    comparable = bool(plan_raw)
    his = cut(plan_raw) if comparable else []
    kms = [tuple(cut(x['plan'])) for x in free]
    if p.get('plan_truncated_at') is not None and his:
        kms = [k[:len(his)] for k in kms]   # his plan is known only up to an unresolved step: compare that stretch only
    n = len(kms)
    first = collections.Counter(k[0] if k else 'EndTurn' for k in kms)
    same_first = sum(1 for k in kms if k and his and (k[0] == his[0] or '?' in his[0]))
    same_plan = sum(1 for k in kms if same(list(k), his))
    modal, mcount = collections.Counter(kms).most_common(1)[0]
    cat, tags, desc = category(his, list(modal)) if comparable else ('no plan recorded (the game ended first)', [], '')
    # first point where the two plans part, and whether both plans run to the end of the turn (neither cut by a draw card / Sabrina / an unresolved step)
    first_div = None
    if comparable:
        a, b2 = his, list(modal)
        k_ = 0
        while k_ < min(len(a), len(b2)) and (a[k_] == b2[k_] or '?' in a[k_] or '?' in b2[k_]):
            k_ += 1
        if k_ < max(len(a), len(b2)):
            first_div = (kind(a[k_]) if k_ < len(a) else 'end', kind(b2[k_]) if k_ < len(b2) else 'end', a[k_] if k_ < len(a) else None, b2[k_] if k_ < len(b2) else None, k_)
    his_whole = comparable and not p.get('plan_truncated_at') and not (his and (is_draw(his[-1]) or his[-1] in STOP))
    km_whole = bool(modal) and not (is_draw(modal[-1]) or modal[-1] in STOP)
    atk_h = next((x for x in his if x.startswith('Attack')), None)
    atk_k = next((x for x in modal if x.startswith('Attack')), None)
    if comparable and his_whole and km_whole:
        attack_cmp = 'same attack' if atk_h and atk_h == atk_k else ('different attack' if atk_h and atk_k else ('he attacks, km3 does not' if atk_h else ('km3 attacks, he does not' if atk_k else 'neither attacks')))
    else:
        attack_cmp = 'unknown (a plan is cut before its end)'
    rows.append(dict(id=p['id'], game=p['game'], his_turn=p['his_turn'], turn_count=p['turn_count'], hand=[h.rsplit(' ', 2)[0] for h in p['me']['hand']],
                     his=his, comparable=comparable, n=n, first=dict(first), same_first=same_first, same_plan=same_plan, modal=list(modal), modal_n=mcount,
                     plans=[(list(k), c) for k, c in collections.Counter(kms).most_common()], cat=cat, tags=tags, desc=desc,
                     first_div=first_div, attack_cmp=attack_cmp,
                     approximate_reason=p.get('approximate_reason'), notes=p.get('notes', ''), problems=posline.get('problems', [])))

json.dump(rows, open(OUT + '_summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def fmt(plan):
    return ' → '.join(plan) if plan else '(nothing)'


def verdict(r):
    k = r['same_first'] / r['n']
    return 'agree' if k >= 10 / 12 else ('differ' if k <= 2 / 12 else 'split')


md = []
for g in dict.fromkeys(r['game'] for r in rows):
    m = META.get(g, {})
    md.append(f"## Game {g}{': ' + m.get('title', '') if m else ''}\n")
    md.append(f'| his turn | game turn | hand | his plan (to the first draw) | {BOT} first action over {rows[0]["n"]} seeds | same first | same plan | {BOT} modal plan (seeds) | category | what differs |')
    md.append('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        if r['game'] != g:
            continue
        fa = ', '.join(f"{k} ×{v}" for k, v in sorted(r['first'].items(), key=lambda kv: -kv[1]))
        md.append(f"| {r['his_turn']} | {r['turn_count']} | {', '.join(r['hand'])} | {fmt(r['his']) if r['comparable'] else '(none: ' + r['cat'] + ')'} | {fa} | {r['same_first']}/{r['n']} ({verdict(r)}) | {r['same_plan']}/{r['n']} | {fmt(r['modal'])} ({r['modal_n']}/{r['n']}) | {r['cat']}{' (also: ' + ', '.join(t for t in r['tags'] if t != r['cat']) + ')' if len(r['tags']) > 1 else ''} | {r['desc']} |")
    md.append('')
open(OUT + '_TABLES.md', 'w', encoding='utf-8').write('\n'.join(md))

comp = [r for r in rows if r['comparable']]
cnt = collections.Counter(verdict(r) for r in comp)
print(len(rows), 'positions;', len(comp), 'with a recorded plan;', dict(cnt), '; same plan in >=10/12:', sum(1 for r in comp if r['same_plan'] / r['n'] >= 10 / 12))
cats = collections.Counter(r['cat'] for r in comp)
for c, v in cats.most_common():
    print(f'  {v:>2}  {c}')
tagcount = collections.Counter()
for r in comp:
    for t in set(r['tags']):
        tagcount[t] += 1
print('by kind (a position can carry several):')
for t, v in tagcount.most_common():
    print(f'  {v:>2}  {t}')
print('first point where the modal plan parts from his (his step kind -> km3 step kind):')
fd = collections.Counter((r['first_div'][0], r['first_div'][1]) for r in comp if r['first_div'])
for (a, b), v in fd.most_common():
    print(f'  {v:>2}  his {a:<9} -> {BOT} {b}')
print('positions where the plans agree entirely (modal):', sum(1 for r in comp if not r['first_div']))
print('attack, where both plans run to the end of the turn:')
for k, v in collections.Counter(r['attack_cmp'] for r in comp).most_common():
    print(f'  {v:>2}  {k}')
print('first action, his kind -> km3 modal first kind (positions where the first actions differ in more than 2/12 seeds of agreement):')
mx = collections.Counter()
for r in comp:
    if verdict(r) != 'agree':
        mx[(kind(r['his'][0] if r['his'] else None), kind(r['modal'][0] if r['modal'] else None))] += 1
for (a, b), v in mx.most_common():
    print(f'  {v:>2}  his {a:<9} -> {BOT} {b}')
for r in comp:
    print(f"{r['id']:<28} {verdict(r):<7} first {r['same_first']:>2}/{r['n']} plan {r['same_plan']:>2}/{r['n']} | {r['cat']} | {r['desc'][:160]}")
