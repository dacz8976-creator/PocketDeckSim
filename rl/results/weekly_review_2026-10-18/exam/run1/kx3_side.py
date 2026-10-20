#!/usr/bin/env python3
"""NON-FORMAL kx3 side run (run1/PREREG_DEVIATION.md): stage A's pg_pos_blade plays kx3_r16_c12_z2_real_t0_poolmeta on the exam's candidate view, AFTER the
formal run. Its move lists are mapped to the frozen plan lists with the harness's own replay; a row that maps to no single listed plan is UNSCORED (never a
miss, never dropped). Descriptive only: no interval, no verdict, not comparable to the formal judge-vs-km3 result (different engine, bare action names,
not verified equal to the frozen pilot).

Run from the judge tag's rl/ai_judge (the formal run's clone): python3 kx3_side.py RUN_OUT_DIR [SEEDS] [TIME_CAP_SECONDS]"""
import collections, json, os, subprocess, sys, time

sys.path.insert(0, os.getcwd())
import judge, formal  # noqa: E402

OUT = sys.argv[1]
SEEDS = sys.argv[2] if len(sys.argv) > 2 else '25100000001,25100000002,25100000003'
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 3 * 3600 - 600
BIN = os.path.expanduser('~/stageA/bin/pg_pos_blade')
CODE = 'kx3_r16_c12_z2_real_t0_poolmeta'
IN = os.path.join(OUT, 'in')
P, D = os.path.join(IN, 'positions.json'), os.path.join(IN, 'decks')
ids = [x.strip() for x in open(os.path.join(IN, 'ids.txt')) if x.strip()]
refs = json.load(open(os.path.join(IN, 'references.json')))
cats = json.load(open(os.path.join(IN, 'categories.json')))
K = os.path.join(OUT, 'kx3_side'); os.makedirs(K, exist_ok=True)
seeds = [int(s) for s in SEEDS.split(',')]

# 1. play (one position at a time: kx3 uses many threads), within the time cap
t0, played, skipped = time.time(), {}, []
for pid in ids:
    if time.time() - t0 > CAP:
        skipped.append(pid); continue
    cmd = [BIN, '--positions', P] + judge.deck_args(D) + ['--seeds', SEEDS, '--bot', CODE, '--only', pid]
    with open(os.path.join(K, f'out_{pid}.jsonl'), 'w') as fo, open(os.path.join(K, f'err_{pid}.txt'), 'w') as fe:
        r = subprocess.run(['nice', '-n', '19'] + cmd, stdout=fo, stderr=fe)
    plans = {}
    for line in open(os.path.join(K, f'out_{pid}.jsonl')):
        j = json.loads(line)
        if j.get('kind') == 'free':
            plans[j['seed']] = j.get('plan') or []
    played[pid] = {'rc': r.returncode, 'plans': plans}
    print(f'{pid}: rc {r.returncode}, {len(plans)} seeds, {time.time() - t0:.0f}s', flush=True)

# 2. map to the frozen plan lists; the accepted moves the same way
recs = judge.list_plans(ids, P, D)
match = lambda items, r: judge.match_plans(items, r, P, D)
items = [(pid, f'{pid}|kx3|{s}', pl) for pid, v in played.items() for s, pl in v['plans'].items() if pl]
got = match(items, recs) if items else {}
accepted, ref_problems, _ = formal.map_references(refs, recs, match, ids)

# 3. agreement per row and decision (descriptive)
rows = []
for pid in ids:
    acc = set(accepted.get(pid, {}).values())
    for s in seeds:
        if pid not in played:
            rows.append({'position': pid, 'seed': s, 'state': 'not run (time cap)'}); continue
        pl = played[pid]['plans'].get(s)
        if not pl:
            rows.append({'position': pid, 'seed': s, 'state': 'no plan printed'}); continue
        n, err = got.get(f'{pid}|kx3|{s}', (None, 'no answer'))
        if n is None:
            rows.append({'position': pid, 'seed': s, 'state': 'unscored', 'why': err, 'plan': pl}); continue
        rows.append({'position': pid, 'seed': s, 'state': 'scored', 'plan_number': n, 'agrees': n in acc, 'plan': pl})
dec = {}
for pid in ids:
    xs = [r['agrees'] for r in rows if r['position'] == pid and r['state'] == 'scored']
    dec[pid] = sum(xs) / len(xs) if xs else None
prim = [p for p in ids if cats[p]['primary']]
scored_prim = [p for p in prim if dec[p] is not None]
summary = {
    'what': 'NOT FORMAL: kx3 side run (PREREG_DEVIATION.md). Different engine (ky3-blade 0f5f234d), bare action names, not verified equal to the frozen '
            'pilot; unscored rows are neither hits nor misses; no interval or verdict.',
    'binary': BIN, 'binary_sha256': judge.file_sha256(BIN), 'code': CODE, 'seeds': seeds, 'time_cap_s': CAP,
    'elapsed_s': round(time.time() - t0), 'not_run': skipped,
    'rows': dict(collections.Counter(r['state'] for r in rows)),
    'primary': {'points': len(prim), 'points_with_a_scored_row': len(scored_prim),
                'prefix_agreement_mean_over_points': round(sum(dec[p] for p in scored_prim) / len(scored_prim), 3) if scored_prim else None},
    'full_scope_subset': {'points_with_a_scored_row': sum(1 for p in scored_prim if cats[p]['scope'] == 'full'),
                          'prefix_agreement_mean': (lambda xs: round(sum(xs) / len(xs), 3) if xs else None)([dec[p] for p in scored_prim if cats[p]['scope'] == 'full'])},
    'diagnostic': {p: dec[p] for p in ids if not cats[p]['primary']},
    'reference_problems': ref_problems,
}
table = {}
for group in ('deck_kinds', 'answer_kind', 'deck'):
    t = collections.defaultdict(list)
    for p in scored_prim:
        for g in (cats[p][group] if group == 'deck_kinds' else [cats[p][group]]):
            t[g].append(dec[p])
    table[group] = {g: {'n_points': len(v), 'agreement': round(sum(v) / len(v), 3)} for g, v in sorted(t.items())}
summary['by_category'] = table
json.dump({'summary': summary, 'rows': rows, 'per_decision': dec}, open(os.path.join(OUT, 'kx3_side.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1)[:3000])
