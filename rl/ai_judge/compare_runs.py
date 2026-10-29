#!/usr/bin/env python3
"""Compare prompt versions (or forms) on the same positions: order stability, agreement with the recorded plan, tokens and cost.

  python3 compare_runs.py --a v1 --b v2 runs/bias1_diag14.jsonl runs/shape1_v1_shaping16.jsonl runs/shape1_v2_shaping30.jsonl
  python3 compare_runs.py --by form runs/big4_*.jsonl

Groups the records by --by (prompt_version, default; or prompt_form) and, within a group, by position and order (repeat 0 only unless --all-repeats).
Order stability = on positions where the group has answers for the orders in --orders: how often all answers are the same listed plan, and the mean
pairwise agreement. Agreement with the recorded plan is a development check on old positions (not evidence).
"""
import argparse, collections, itertools, json, sys
import judge


def load(files):
    rows = []
    for fn in files:
        rows += [json.loads(l) for l in open(fn, encoding='utf-8') if l.strip()]
    return [r for r in rows if r['bot'] == 'judge' and not r.get('dry_run')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--by', default='prompt_version')
    ap.add_argument('--orders', default='forward,reverse,shuffle:1')
    ap.add_argument('--positions-only', help='comma list of position ids to restrict to')
    ap.add_argument('--all-repeats', action='store_true')
    a = ap.parse_args()
    orders = a.orders.split(',')
    rows = load(a.files)
    if a.positions_only:
        keep = set(a.positions_only.split(','))
        rows = [r for r in rows if r['position'] in keep]
    for r in rows:
        r.setdefault('prompt_version', 'v1')
    positions = judge.load_positions()
    pids = sorted({r['position'] for r in rows})
    recs = judge.list_plans(pids)
    his = judge.match_plans([(i, i, positions[i]['his_plan']) for i in pids if positions[i].get('his_plan')], recs)
    groups = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        if not a.all_repeats and r.get('repeat', 0) != 0:
            continue
        groups[r[a.by]][r['position']][r['order']] = r
    for g, bypos in sorted(groups.items()):
        full = {p: d for p, d in bypos.items() if all(o in d and d[o]['plan_number'] is not None for o in orders)}
        allsame = sum(len({d[o]['plan_number'] for o in orders}) == 1 for d in full.values())
        pair = [d[x]['plan_number'] == d[y]['plan_number'] for d in full.values() for x, y in itertools.combinations(orders, 2)]
        calls = [r for d in bypos.values() for r in d.values()]
        failed = sum(r['plan_number'] is None for r in calls)
        agree = [r['plan_number'] == his[r['position']][0] for r in calls if r['plan_number'] is not None and his.get(r['position'], (None,))[0] is not None]
        cin = sum(r['cost']['input_tokens'] for r in calls) / len(calls)
        cout = sum(r['cost']['output_tokens'] for r in calls) / len(calls)
        usd = sum(r['cost']['usd'] for r in calls) / len(calls)
        print(f'[{a.by} = {g}] {len(bypos)} positions, {len(calls)} calls, {failed} without an answer')
        print(f'   order stability over {len(full)} positions answered in all of {orders}: all the same plan in {allsame} ({allsame / max(1, len(full)):.0%}); mean pairwise agreement {sum(pair) / max(1, len(pair)):.0%}')
        print(f'   same listed plan as the recorded one: {sum(agree)}/{len(agree)} ({sum(agree) / max(1, len(agree)):.0%})   [old positions: a development check]')
        print(f'   per call: {cin:,.0f} input tokens, {cout:,.0f} output tokens, ${usd:.3f} (assumed prices); total ${sum(r["cost"]["usd"] for r in calls):.2f}')
        unstable = [p for p, d in full.items() if len({d[o]['plan_number'] for o in orders}) > 1]
        print('   unstable positions:', ', '.join(f'{p[-18:]}({"/".join(str(d[o]["plan_number"]) for o in orders)})' for p, d in ((p, full[p]) for p in unstable)))


if __name__ == '__main__':
    main()
