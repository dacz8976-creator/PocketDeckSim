"""The Sept 26 repair replays against the references and against each other, by cell with seeds.

For each run: the games whose moves ("moves", every step) differ from the reference table files, and, against the run
before it in the order given, the games whose moves differ and those whose choices ("decisions", moves picked from two
or more options; present from af8489f's scan on) differ, with how many results differ.
Usage: python3 compare.py <commit> [<commit> ...]   (in fix order, e.g. 07927e2 3c2250f ... e935f42)."""
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


def report(label, base, run, field):
    keys = [k for k in run if k in base and field in base[k] and field in run[k]]
    if not keys:
        return
    differ = [k for k in keys if base[k][field] != run[k][field]]
    results = [k for k in differ if (base[k]['winner_seat'], base[k]['points']) != (run[k]['winner_seat'], run[k]['points'])]
    print(f"  {field} vs {label}: {len(differ)} of {len(keys)} games differ, results in {len(results)}")
    cells = Counter(f"{run[k]['a']} v {run[k]['b']}" for k in differ)
    for cell, n in sorted(cells.items()):
        r = sum(1 for k in results if f"{run[k]['a']} v {run[k]['b']}" == cell)
        seeds = [str(run[k]['seed']) for k in sorted(differ) if f"{run[k]['a']} v {run[k]['b']}" == cell]
        print(f"    {cell}: {n} differ, {r} results; seeds {', '.join(seeds[:30])}{' ...' if len(seeds) > 30 else ''}")


commits = sys.argv[1:]
for bot in ('k3', 'kp3'):
    ref = load(REF[bot])
    prev_name, prev = None, None
    for c in commits:
        path = D / f'{c}_{bot}_500.jsonl'
        if not path.exists():
            continue
        run = load([path])
        print(f"{bot} at {c}: {len(run)} games{'' if len(run) == len(ref) else ' (partial)'}")
        report('the reference table', ref, run, 'moves')
        if prev is not None:
            report(prev_name, prev, run, 'moves')
            report(prev_name, prev, run, 'decisions')
        prev_name, prev = c, run
