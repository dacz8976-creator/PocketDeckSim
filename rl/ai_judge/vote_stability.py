#!/usr/bin/env python3
"""How reproducible is a majority vote over three orders, compared with one call?

  python3 vote_stability.py

Two independent triples of prompt v1 on the 30 shaping positions:
  triple A: forward, reverse, shuffle:1   (diag14: runs/bias1 repeat 0 and shuffle:1; the 16 others: runs/shape1_v1)
  triple B: forward, reverse, shuffle:2   (diag14: runs/bias1 forward#1, reverse#1, shuffle:2; the 16 others: runs/shape2)
The vote is the plan chosen by at least two of the three; with three different plans there is no majority (reported as a tie).
Compared: A's majority against B's majority; and, for one call, how often A's single forward call equals B's single forward call
(same order, same prompt: the judge against itself) and equals B's reverse call (another order).
"""
import collections, json


def load(fn):
    return [json.loads(l) for l in open('runs/' + fn, encoding='utf-8') if l.strip()]


def maj(plans):
    c = collections.Counter(plans).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return None
    return c[0][0]


A, B = collections.defaultdict(dict), collections.defaultdict(dict)
for r in load('bias1_diag14.jsonl'):
    key = (r['order'], r.get('repeat', 0))
    if key in [('forward', 0), ('reverse', 0), ('shuffle:1', 0)]:
        A[r['position']][r['order']] = r['plan_number']
    if key in [('forward', 1), ('reverse', 1), ('shuffle:2', 0)]:
        B[r['position']][r['order'] if r['order'] != 'shuffle:2' else 'shuffle'] = r['plan_number']
for r in load('shape1_v1_shaping16.jsonl'):
    A[r['position']][r['order']] = r['plan_number']
for r in load('shape2_v1_shaping16_tripleB.jsonl'):
    B[r['position']][r['order'] if r['order'] != 'shuffle:2' else 'shuffle'] = r['plan_number']
for d in A.values():
    if 'shuffle:1' in d:
        d['shuffle'] = d.pop('shuffle:1')

pos = sorted(p for p in A if p in B and len(A[p]) == 3 and len(B[p]) == 3)
same_vote = tie = 0
rows = []
for p in pos:
    a, b = maj(list(A[p].values())), maj(list(B[p].values()))
    tie += (a is None) + (b is None)
    ok = a is not None and a == b
    same_vote += ok
    rows.append((p, a, b, ok))
print(f'{len(pos)} positions with two full triples')
print(f'majority of A = majority of B on {same_vote} positions ({same_vote / len(pos):.0%}); {tie} of {2 * len(pos)} majorities were ties')
same_order = sum(A[p]['forward'] == B[p]['forward'] for p in pos)
cross = sum(A[p]['forward'] == B[p]['reverse'] for p in pos)
print(f'one call: forward vs forward again: {same_order}/{len(pos)} ({same_order / len(pos):.0%});  forward vs reverse: {cross}/{len(pos)} ({cross / len(pos):.0%})')
for p, a, b, ok in rows:
    if not ok:
        print('  differs:', p, 'A', dict(A[p]), 'B', dict(B[p]))
