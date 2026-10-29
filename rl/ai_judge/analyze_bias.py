#!/usr/bin/env python3
"""Position-bias summary of judge runs: does the chosen plan change when the plans are shown in another order?

  python3 analyze_bias.py runs/bias1_diag14.jsonl [more result files]

Records are grouped by position. A run is (order, repeat). "Same plan" means the same listed plan number (the lister's, not the number shown), so
reversed or shuffled lists are comparable. The yardstick is the judge's own variability: the same prompt asked twice (repeat 0 vs repeat 1).
Old positions only: the agreement with the recorded plan is a development check, not evidence.
"""
import collections, json, sys
import judge


def main(files):
    rows = []
    for fn in files:
        rows += [json.loads(l) for l in open(fn, encoding='utf-8') if l.strip()]
    rows = [r for r in rows if r['bot'] == 'judge' and not r.get('dry_run')]
    by = collections.defaultdict(dict)  # position -> (order, repeat) -> record
    for r in rows:
        by[r['position']][(r['order'], r.get('repeat', 0))] = r
    failed = [r for r in rows if r['plan_number'] is None]
    print(f'{len(rows)} calls on {len(by)} positions; {len(failed)} without a usable answer')
    for r in failed:
        print('  failed:', r['position'], r['order'], r.get('parse_error'))

    def pair(a, b):
        same = tot = 0
        for pid, d in by.items():
            if a in d and b in d and d[a]['plan_number'] is not None and d[b]['plan_number'] is not None:
                tot += 1
                same += d[a]['plan_number'] == d[b]['plan_number']
        return same, tot

    orders = sorted({k for d in by.values() for k in d})
    print('\nSame listed plan, pair by pair (positions where both runs answered):')
    print(f"{'':22}" + ''.join(f'{o[0]}#{o[1]:<4}' for o in orders))
    for a in orders:
        line = f'{a[0] + "#" + str(a[1]):22}'
        for b in orders:
            s, t = pair(a, b)
            line += f'{s}/{t}  ' if t else '-     '
        print(line)

    print('\nBy kind of comparison:')
    kinds = collections.defaultdict(lambda: [0, 0])
    for pid, d in by.items():
        keys = sorted(d)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if d[a]['plan_number'] is None or d[b]['plan_number'] is None:
                    continue
                kind = 'same order again (the judge against itself)' if a[0] == b[0] else 'different order'
                kinds[kind][1] += 1
                kinds[kind][0] += d[a]['plan_number'] == d[b]['plan_number']
    for k, (s, t) in kinds.items():
        print(f'  {k}: {s}/{t} = {s / t:.0%}' if t else f'  {k}: none')

    print('\nPositions where the choice changes (listed plan numbers by run):')
    n_changed = 0
    for pid, d in sorted(by.items()):
        picks = {k: v['plan_number'] for k, v in sorted(d.items())}
        if len(set(picks.values())) > 1:
            n_changed += 1
            print(f'  {pid} ({next(iter(d.values()))["n_plans"]} plans): ' + ', '.join(f'{k[0]}#{k[1]}={n}' for k, n in picks.items()))
    print(f'  {n_changed} of {len(by)} positions have more than one distinct choice')

    print('\nWhere in the shown list the choice falls (0 = first shown, 1 = last shown), by order; no position bias would give a mean near 0.5:')
    pos_by_order = collections.defaultdict(list)
    for r in rows:
        if r['shown_number'] and r['n_plans'] > 1:
            pos_by_order[r['order']].append((r['shown_number'] - 1) / (r['n_plans'] - 1))
    for o, v in sorted(pos_by_order.items()):
        print(f'  {o:12} mean {sum(v) / len(v):.2f} over {len(v)} calls; chose the first shown {sum(x == 0 for x in v)} times, the last shown {sum(x == 1 for x in v)} times')


if __name__ == '__main__':
    main(sys.argv[1:] or ['runs/bias1_diag14.jsonl'])
