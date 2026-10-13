#!/usr/bin/env python3
"""compare_engines.py: km3's plans on the official engine (runs_km3/) and on the older engine (runs_km3_older_engine/) for the positions flagged for rules switch 2 (run_ids_switch2.txt), seed by seed.
The older engine's plan list ends in `EndTurn` after an attack where the official one stops at the attack; a trailing EndTurn is dropped before comparing. Run in the v2 folder."""
import json

ids = [l.strip() for l in open('run_ids_switch2.txt') if l.strip()]


def load(path):
    out = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get('kind') != 'free':
            continue
        plan = list(rec['plan'])
        while plan and plan[-1] == 'EndTurn':
            plan.pop()
        out[rec['seed']] = plan
    return out


same = 0
for pid in ids:
    a = load(f'runs_km3/out_{pid}.jsonl')
    b = load(f'runs_km3_older_engine/out_{pid}.jsonl')
    diff = [s for s in sorted(set(a) | set(b)) if a.get(s) != b.get(s)]
    print(pid, len(a), len(b), 'IDENTICAL' if not diff else f'DIFFERS seeds {diff}')
    if diff:
        print('   official:', a.get(diff[0]))
        print('   older   :', b.get(diff[0]))
    else:
        same += 1
print(f'identical {same} of {len(ids)}')
