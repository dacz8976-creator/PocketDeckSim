#!/usr/bin/env python3
"""Draft A v the fixed computer deck: the two agreement tables (km3 v Auto on the Auto positions, km3 v Dustin on his), split by milestone, same columns as TABLES.md.
Decision agreement only, not strength. The two groups are different games: they are never paired position by position, only compared as rates by situation type.
usage: pgd_cmp_tables.py SUMMARY.json OUT.md"""
import json, sys, collections

rows = [r for r in json.load(open(sys.argv[1], encoding='utf-8')) if r['id'].startswith('B-')]
MS = ['preparing an attacker', 'managing a sacrifice', 'adapting when the plan fails', 'recognising an immediate win']


def verdict(r):
    k = r['same_first'] / r['n']
    return 'agree' if k >= 10 / 12 else ('differ' if k <= 2 / 12 else 'split')


def plan_ok(r):
    return r['same_plan'] / r['n'] >= 10 / 12


def fmt(plan):
    return ' → '.join(plan) if plan else '(nothing)'


def rates(rs):
    n = len(rs)
    c = collections.Counter(verdict(r) for r in rs)
    p = sum(1 for r in rs if plan_ok(r))
    pct = lambda x: f'{100 * x / n:.0f}%' if n else '-'
    return n, c['agree'], c['split'], c['differ'], p, pct


def rate_cells(rs):
    n, a, s, d, p, pct = rates(rs)
    return f'{n} | {a} ({pct(a)}) | {s} ({pct(s)}) | {d} ({pct(d)}) | {p} ({pct(p)})'


def row_line(r):
    fa = ', '.join(f"{k} ×{v}" for k, v in sorted(r['first'].items(), key=lambda kv: -kv[1]))
    gap = '' if r['gap'] is None else f"{r['gap']:.0f}"
    hs = f"{r['hand_source']} · {r['decision_maker']} · exact list" + (' · HELD OUT' if r['heldout'] else '')
    other = ' (also: ' + ', '.join(t for t in r['tags'] if t != r['cat']) + ')' if len(r['tags']) > 1 else ''
    return (f"| {r['game'][-9:-3]} t{r['turn_count']} | {r['turn_count']} | {hs} | {fmt(r['his'])} | {fa} | {r['same_first']}/{r['n']} ({verdict(r)}) | {r['same_plan']}/{r['n']} | "
            f"{fmt(r['modal'])} ({r['modal_n']}/{r['n']}) | {r['cat']}{other} | {r['desc']} | {gap} | {', '.join(r['milestones'])} |")


HEAD = ('| game, turn | game turn | hand | his plan (to the first draw) | km3 first action over 12 seeds | same first action | same plan to first draw | km3 modal plan (seeds) | '
        'category (all tags) | what differs | km3 root gap (his first action) | milestones |\n|---|---|---|---|---|---|---|---|---|---|---|---|')
out = ['# Draft A against the fixed computer deck: km3 v the decision maker (decision agreement only)\n']
out.append('**What this is.** At the start of each owner turn of eight recordings (Mega Blastoise ex & Wailord ex computer deck, Step-Up Battle: Advanced; both 20-card lists exact), km3 on the pinned engine (main-8626a35) is asked what it plays from the rebuilt position, 12 seeds, and its plan is compared with what the decision maker did: the game\'s **Auto** in 5 recordings, **Dustin** in 3. '
           'This is **decision agreement only, not strength**: "agree" says km3 chose the same first action, not that either choice was better. '
           'The two groups are **different games and are never paired position by position**; the last table compares only their rates by situation type. '
           'Agree = km3\'s first action equals the decision maker\'s in at least 10 of 12 seeds; differ = in at most 2 of 12; split = in between. "Same plan" = the whole plan up to and including the first draw card (Research, Poké Ball, Copycat, Lisia ...) matches in at least 10 of 12 seeds. '
           'Milestones are mechanical tags (README): a position can carry several and then appears under each. Held-out positions (a fixed hash of the game id) are marked; km3 is the reference pilot and was run on everything.\n')
groups = {'Auto': [r for r in rows if r['decision_maker'] == 'Auto'], 'Dustin': [r for r in rows if r['decision_maker'] == 'Dustin']}
for who, rs in groups.items():
    gs = sorted({r['game'] for r in rs})
    ho = sum(1 for r in rs if r['heldout'])
    out.append(f"\n## km3 v {who}: {len(rs)} positions from {len(gs)} recordings ({ho} held out)\n")
    out.append('| situation (milestone) | positions | km3 first action = his | split | differs | whole plan to the first draw = his |\n|---|---|---|---|---|---|')
    out.append('| all positions | ' + rate_cells(rs) + ' |')
    for m in MS:
        sub = [r for r in rs if m in r['milestones']]
        out.append(f'| {m} | ' + rate_cells(sub) + ' |')
    sub = [r for r in rs if not r['milestones']]
    out.append('| (no milestone) | ' + rate_cells(sub) + ' |')
    cats = collections.Counter(r['cat'] for r in rs)
    out.append('\nWhat differs, by the report\'s primary category (a position counts once): ' + '; '.join(f'{c}: {n}' for c, n in cats.most_common()) + '.\n')

    def attacks(plan):
        return [s for s in plan if s.startswith('Attack:')]
    both = [r for r in rs if attacks(r['his']) and attacks(r['modal'])]
    same_att = [r for r in both if attacks(r['his'])[-1] == attacks(r['modal'])[-1]]
    only_his = [r for r in rs if attacks(r['his']) and not attacks(r['modal'])]
    only_km = [r for r in rs if attacks(r['modal']) and not attacks(r['his'])]
    wins = [r for r in rs if 'recognising an immediate win' in r['milestones']]
    win_att = [r for r in wins if attacks(r['modal'])]
    out.append(f"Attacks (km3's modal plan against the decision maker's whole turn): both plans reach an attack in {len(both)} positions and use the same attack in {len(same_att)} of them; "
               f"he attacks and km3's modal plan does not in {len(only_his)}; km3's modal plan attacks and he does not in {len(only_km)}. "
               f"On the {len(wins)} immediate-win positions km3's modal plan reaches an attack in {len(win_att)} (the first-action column undercounts these: km3 often attacks at once without the preparatory attachment or evolution he made first).\n")
    for m in MS + ['(no milestone)']:
        sub = [r for r in rs if (m in r['milestones'] if m != '(no milestone)' else not r['milestones'])]
        if not sub:
            continue
        out.append(f'\n### km3 v {who}: {m} ({len(sub)} positions)\n')
        out.append(HEAD)
        for r in sorted(sub, key=lambda r: (r['game'], r['turn_count'])):
            out.append(row_line(r))
out.append('\n## Rates by situation type, side by side (different games: not a paired comparison)\n')
out.append('| situation (milestone) | Auto: positions | Auto: first action agrees | Auto: whole plan agrees | Dustin: positions | Dustin: first action agrees | Dustin: whole plan agrees |\n|---|---|---|---|---|---|---|')
for m in ['all positions'] + MS + ['(no milestone)']:
    cells = []
    for who in ('Auto', 'Dustin'):
        rs = groups[who]
        sub = rs if m == 'all positions' else ([r for r in rs if m in r['milestones']] if m != '(no milestone)' else [r for r in rs if not r['milestones']])
        n, a, s, d, p, pct = rates(sub)
        cells += [str(n), f'{a} ({pct(a)})', f'{p} ({pct(p)})']
    out.append(f'| {m} | ' + ' | '.join(cells) + ' |')
out.append('\nSmall counts: 39 Auto positions and 26 of Dustin\'s; the rates by milestone rest on a handful of positions each. Nothing here says who played better.')
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written', sys.argv[2], {w: len(r) for w, r in groups.items()})
for who, rs in groups.items():
    print(who, 'all:', rates(rs)[:5])
    for m in MS + ['(no milestone)']:
        sub = [r for r in rs if (m in r['milestones'] if m != '(no milestone)' else not r['milestones'])]
        print('   ', m, rates(sub)[:5])
