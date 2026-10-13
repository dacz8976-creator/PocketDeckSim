#!/usr/bin/env python3
"""before_after.py OLD.json NEW.json > before_after.json: for every position that differs, the fields that differ with their old and new values (notes as the sentences that differ)"""
import json, sys

a = {p['id']: p for p in json.load(open(sys.argv[1], encoding='utf-8'))}
b = {p['id']: p for p in json.load(open(sys.argv[2], encoding='utf-8'))}
out = {}
for pid in sorted(set(a) & set(b)):
    x, y = a[pid], b[pid]
    rec = {}
    for k in sorted(set(x) | set(y)):
        if k in ('me', 'opp') and isinstance(x.get(k), dict) and isinstance(y.get(k), dict):
            for kk in sorted(set(x[k]) | set(y[k])):
                if x[k].get(kk) != y[k].get(kk):
                    rec[f'{k}.{kk}'] = {'old': x[k].get(kk), 'new': y[k].get(kk)}
        elif k == 'notes' and x.get(k) != y.get(k):
            sa, sb = set(str(x.get(k)).split('; ')), set(str(y.get(k)).split('; '))
            rec['notes'] = {'only_old': sorted(sa - sb), 'only_new': sorted(sb - sa)}
        elif x.get(k) != y.get(k):
            rec[k] = {'old': x.get(k), 'new': y.get(k)}
    if rec:
        out[pid] = rec
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
