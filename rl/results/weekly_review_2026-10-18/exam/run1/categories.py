#!/usr/bin/env python3
"""DESCRIPTIVE breakdown of the primary comparison by deck kind and answer kind (no interval, no verdict: the formal result is report_primary.json).
usage: categories.py REPORT CATEGORIES OUT. Reads the per-decision rows the formal report carries (prefix agreement per decision and bot; for km3 the
mean over its seeds, for the judge the primary call), groups them by the exam's deck kinds (a point counts in each of its kinds) and answer kind."""
import json, sys, collections

rep_path, cat_path, out_path = sys.argv[1:4]
rep = json.load(open(rep_path))
cats = json.load(open(cat_path))


def find_rows(x, path=''):
    """Yield (path, list) for every list of dicts that carry a position and a bot."""
    if isinstance(x, dict):
        for k, v in x.items():
            yield from find_rows(v, f'{path}/{k}')
    elif isinstance(x, list) and x and all(isinstance(e, dict) for e in x) and {'position', 'bot'} <= set(x[0]):
        yield path, x


cands = list(find_rows(rep))
if not cands:
    print('categories: no per-row list in the report; top-level keys:', list(rep), file=sys.stderr)
    sys.exit(1)
path, rows = max(cands, key=lambda c: len(c[1]))
keys = sorted(rows[0])
flag = next((k for k in ('agrees', 'prefix_agrees', 'agree', 'prefix') if k in rows[0]), None)
if flag is None:
    print(f'categories: rows at {path} have no agreement field: {keys}', file=sys.stderr)
    sys.exit(1)
per = collections.defaultdict(list)  # (point, bot) -> values
for r in rows:
    if r['position'] in cats and cats[r['position']]['primary'] and r.get(flag) is not None:
        if r['bot'] == 'judge' and r.get('repeat', r.get('run', 0)) not in (0, None):
            continue
        per[(r['position'], r['bot'])].append(1.0 if r[flag] else 0.0)
dec = {k: sum(v) / len(v) for k, v in per.items()}
bots = sorted({b for _, b in dec})
table = {}
for group in ('deck_kinds', 'answer_kind', 'deck'):
    t = collections.defaultdict(lambda: collections.defaultdict(list))
    for (pid, bot), v in dec.items():
        vals = cats[pid][group] if group == 'deck_kinds' else [cats[pid][group]]
        for g in vals:
            t[g][bot].append(v)
    table[group] = {g: {b: {'n_decisions': len(t[g][b]), 'agreement': round(sum(t[g][b]) / len(t[g][b]), 3) if t[g][b] else None} for b in bots} for g in sorted(t)}
out = {'what': 'DESCRIPTIVE: prefix agreement per decision on the 49 primary points, grouped; points of one game are not independent and a point counts in each of '
               'its deck kinds; no interval or verdict here (see report_primary.json)', 'source_rows': path, 'agreement_field': flag, 'bots': bots, 'table': table}
json.dump(out, open(out_path, 'w'), indent=1)
for group, t in table.items():
    print(group)
    for g, bb in t.items():
        print(f"  {g:28}" + '  '.join(f"{b}: {bb[b]['agreement']} (n={bb[b]['n_decisions']})" for b in bots))
