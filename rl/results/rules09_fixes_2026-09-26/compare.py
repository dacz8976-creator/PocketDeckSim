"""The rules/09 fix replays against the references and against each other: games whose moves or results differ,
by cell. Usage: python3 compare.py <commit> [<commit> ...] (in fix order; each is compared with the reference and
with the commit before it)."""
import json, sys
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
REF = {'k3': [D / '../per_game_table_2026-09-25/k3_500.jsonl'],
       'kp3': [D / '../public_pricing_2026-09-25/kp3_500_worst5.jsonl', D / '../public_pricing_2026-09-25/kp3_500_rest.jsonl']}

def load(paths):
    games = {}
    for path in paths:
        for line in open(path):
            g = json.loads(line)
            games[(g['pairing'], g['i'])] = g
    return games

def diff(a, b):
    moves = [k for k in b if k in a and a[k]['moves'] != b[k]['moves']]
    results = [k for k in moves if (a[k]['winner_seat'], a[k]['points']) != (b[k]['winner_seat'], b[k]['points'])]
    return moves, results

def cells(keys, games):
    return Counter(f"{games[k]['a']} v {games[k]['b']}" for k in keys)

commits = sys.argv[1:]
for bot in ('k3', 'kp3'):
    ref = load(REF[bot])
    prev_name, prev = 'reference', ref
    for c in commits:
        path = D / f'{c}_{bot}_500.jsonl'
        if not path.exists():
            continue
        run = load([path])
        complete = len(run) == len(ref)
        for label, base in (('reference', ref), (prev_name, prev)) if prev_name != 'reference' else (('reference', ref),):
            moves, results = diff(base, run)
            print(f"{bot} at {c} vs {label}: {len(run)} games{'' if complete else ' (partial)'}; "
                  f"moves differ in {len(moves)}, results in {len(results)}")
            for cell, n in sorted(cells(moves, run).items()):
                r = sum(1 for k in results if f"{run[k]['a']} v {run[k]['b']}" == cell)
                print(f"    {cell}: {n} games differ, {r} results differ; seeds "
                      + ', '.join(str(run[k]['seed']) for k in sorted(moves) if f"{run[k]['a']} v {run[k]['b']}" == cell)[:400])
        prev_name, prev = c, run
