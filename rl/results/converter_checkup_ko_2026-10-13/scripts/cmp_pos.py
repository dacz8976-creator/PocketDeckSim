#!/usr/bin/env python3
"""cmp_pos.py A.json B.json LABEL [--show]: the positions that differ between two converter runs, and which fields (me.* / opp.* one level down)"""
import collections, json, sys

a = {p['id']: p for p in json.load(open(sys.argv[1], encoding='utf-8'))}
b = {p['id']: p for p in json.load(open(sys.argv[2], encoding='utf-8'))}
label = sys.argv[3] if len(sys.argv) > 3 else ''
print(f'[{label}]\n  positions: A {len(a)}  B {len(b)}  only in A: {sorted(set(a) - set(b))[:5]}  only in B: {sorted(set(b) - set(a))[:5]}')
fields = collections.Counter()
changed = []
for pid in sorted(set(a) & set(b)):
    x, y = a[pid], b[pid]
    diffs = []
    for k in sorted(set(x) | set(y)):
        if k in ('me', 'opp') and isinstance(x.get(k), dict) and isinstance(y.get(k), dict):
            diffs += [f'{k}.{kk}' for kk in sorted(set(x[k]) | set(y[k])) if x[k].get(kk) != y[k].get(kk)]
        elif x.get(k) != y.get(k):
            diffs.append(k)
    if diffs:
        changed.append((pid, diffs))
        fields.update(diffs)
print(f'  positions that differ: {len(changed)} of {len(set(a) & set(b))}; fields: {dict(fields)}')
for pid, diffs in changed:
    print('   ', pid, diffs)
