#!/usr/bin/env python3
"""A dry run of the G2 lister check on his recorded lines only (no labels exist yet): candidate views of every built point (G1 drops left out)
and references {point id: [{"id": "his", "labels": his move in the judge's label form}]}. Output in ~/exam_v2/build/lister_pre/ (local; holds
his moves). Prints counts and the point ids per problem type only."""
import collections, glob, importlib.util, json, os, subprocess, sys
E2 = '/home/dacz8976/exam_v2'
RUN3 = '/home/dacz8976/exam_034_w/rl/results/weekly_review_2026-10-18/exam/run3'
sys.path.insert(0, f'{E2}/build')
import v2_helpers as H
from label_adapter import to_judge
O = f'{E2}/build/lister_pre'
os.makedirs(O, exist_ok=True)
built = {}
for fn in sorted(glob.glob(f'{E2}/build/g/g*.py')):
    sp = importlib.util.spec_from_file_location('g', fn); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    for q in m.POS:
        built[q['id']] = q
drops = {os.path.basename(p)[:-4] for p in glob.glob(f'{E2}/build/drops/*.txt')}
pos, refs = [], {}
for pid, b in sorted(built.items()):
    if pid in drops:
        continue
    pos.append(H.candidate_view(b))
    refs[pid] = [{'id': 'his', 'labels': [to_judge(l) for l in b['force']]}]
json.dump(pos, open(f'{O}/positions.json', 'w'), ensure_ascii=False)
json.dump(refs, open(f'{O}/references.json', 'w'), ensure_ascii=False)
r = subprocess.run([sys.executable, '-B', f'{RUN3}/check_lister_v2.py', '/home/dacz8976/judge7_w', f'{O}/positions.json', f'{E2}/decks',
                    f'{O}/references.json', '--out', f'{O}/report.json', '--drops-out', f'{O}/drops'], capture_output=True, text=True)
print('exit', r.returncode)
print(r.stderr[-1500:])
print('\n'.join(r.stdout.splitlines()[-15:]))
rep = json.load(open(f'{O}/report.json'))
rows = rep.get('rows') or rep.get('lines') or []
print('report keys', list(rep)[:12], 'rows', len(rows))
by = collections.defaultdict(list)
for x in rows:
    by[x.get('verdict') or x.get('status')].append(x.get('point') or x.get('pid') or x.get('id'))
for k, v in by.items():
    print(k, len(v), v[:40] if k not in ('pass',) else '')
