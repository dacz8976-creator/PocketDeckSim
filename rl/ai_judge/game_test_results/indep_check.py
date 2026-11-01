"""Independent re-computation of stage 2's score, written apart from game_analysis.py (shares no code with it).
Reads the run dir only. Checks: one complete attempt per deal, result-file hashes, outcomes parsed afresh,
an EXACT sign-flip p (binomial), a separate stratified bootstrap (own RNG and seed), the label rules of
registration section 6, and descriptive splits. Usage: python3 -I indep_check.py <run_dir> <registered analysis.json>"""
import hashlib
import json
import math
import os
import random
import sys

run_dir, reg_path = sys.argv[1], sys.argv[2]


def jl(p):
    with open(p, encoding='utf-8') as f:
        return [json.loads(x) for x in f if x.strip()]


deals = jl(os.path.join(run_dir, 'deals.jsonl'))
arms = {a['deal_tag']: a for a in jl(os.path.join(run_dir, 'games.jsonl'))}
end = json.load(open(os.path.join(run_dir, 'run_end.json')))
reg = json.load(open(reg_path))

problems = []
by_idx = {}
for r in deals:
    by_idx.setdefault(r['deal_idx'], []).append(r)
attempts = sorted({len(v) for v in by_idx.values()})
print('deal rows %d, deal_idx values %d, rows per deal %s' % (len(deals), len(by_idx), attempts))
if sorted(by_idx) != list(range(128)):
    problems.append('deal_idx is not exactly 0..127')

rows = []
for idx in sorted(by_idx):
    done = [r for r in by_idx[idx] if r.get('complete')]
    if not done:
        problems.append('deal %d has no complete attempt' % idx)
        continue
    r = max(done, key=lambda x: x['attempt'])
    cell, k = r['cell'], r['k']
    b = r['bits']
    if cell != 8 * b['deck'] + 4 * b['list'] + 2 * b['policy'] + b['seat']:
        problems.append('deal %d: cell %d does not match its bits %s' % (idx, cell, b))
    if r.get('dropped'):
        problems.append('deal %d is marked dropped (%s)' % (idx, r.get('drop_reason')))
    res = {}
    for arm_name, tag in (('G', r['g_deal_tag']), ('K', r['k_deal_tag'])):
        a = arms.get(tag)
        if a is None:
            problems.append('deal %d: arm row %s missing' % (idx, tag))
            continue
        if a.get('arm') != arm_name:
            problems.append('deal %d: arm row %s says arm %r' % (idx, tag, a.get('arm')))
        rf = a.get('result_file')
        path = rf if (rf and os.path.isabs(rf)) else os.path.join(run_dir, rf or '')
        raw = open(path, 'rb').read()
        if hashlib.sha256(raw).hexdigest() != a.get('result_sha256'):
            problems.append('deal %d arm %s: result hash differs' % (idx, arm_name))
        out = json.loads(raw).get('outcome')
        if out == 'Tie':
            w = 0
        elif isinstance(out, dict) and set(out) == {'Win'} and out['Win'] in (0, 1):
            w = 1 if out['Win'] == b['seat'] else 0
        else:
            problems.append('deal %d arm %s: unexpected outcome %r' % (idx, arm_name, out))
            w = 0
        res[arm_name] = (w, out, a)
    if len(res) != 2:
        continue
    gf, kf = r.get('g_failure'), r.get('k_failure')
    g = 0 if gf == 'pilot_side' else res['G'][0]
    j = res['G'][2].get('judge') or {}
    if j.get('mock'):
        problems.append('deal %d: G arm is a mock' % idx)
    rows.append({'idx': idx, 'k': k, 'cell': cell, 'deck': b['deck'], 'list': b['list'], 'policy': b['policy'], 'seat': b['seat'],
                 'g': g, 'kw': res['K'][0], 'D': g - res['K'][0], 'gf': gf, 'kf': kf,
                 'iv': j.get('interventions', 0), 'fb': j.get('fallbacks', 0), 'model': json.dumps(j.get('model_returned')),
                 'tie_g': res['G'][1] == 'Tie', 'tie_k': res['K'][1] == 'Tie'})

n = len(rows)
D = [x['D'] for x in rows]
S = sum(D)
fails = {}
for x in rows:
    for a, f in (('G', x['gf']), ('K', x['kf'])):
        if f:
            fails['%s:%s' % (a, f)] = fails.get('%s:%s' % (a, f), 0) + 1
cells = {}
for x in rows:
    cells.setdefault(x['cell'], []).append(x['D'])
print('scored pairs %d; failures by arm:class %s; pairs per cell %s' % (n, fails or '{}', sorted({len(v) for v in cells.values()})))
print('ties: G %d, K %d' % (sum(x['tie_g'] for x in rows), sum(x['tie_k'] for x in rows)))
gw, kw = sum(x['g'] for x in rows), sum(x['kw'] for x in rows)
print('wins: G arm %d of %d (%.3f), K arm %d of %d (%.3f)' % (gw, n, gw / n, kw, n, kw / n))
plus, minus = D.count(1), D.count(-1)
print('pairs: G won K lost %d; K won G lost %d; same result %d (both won %d, both lost %d)'
      % (plus, minus, D.count(0), sum(1 for x in rows if x['g'] == 1 and x['kw'] == 1), sum(1 for x in rows if x['g'] == 0 and x['kw'] == 0)))
mean_d = S / n
print('mean D %.6f (sum %d)' % (mean_d, S))

# exact two-sided sign-flip p: each nonzero pair is +-1 with prob 1/2, so the flipped sum is 2B - m, B ~ Bin(m, 1/2)
m = plus + minus
p_exact = sum(math.comb(m, b) for b in range(m + 1) if abs(2 * b - m) >= abs(S)) / 2 ** m
print('exact sign-flip p %.6f (m = %d nonzero pairs)' % (p_exact, m))

# separate stratified bootstrap: own RNG and seed, 20,000 draws, resampling within each of the 16 cells
rng = random.Random(777001)
keys = sorted(cells)
bm = []
for _ in range(20000):
    t = 0
    for c in keys:
        v = cells[c]
        t += sum(v[rng.randrange(len(v))] for _ in range(len(v)))
    bm.append(t / n)
bm.sort()
lo, hi = bm[int(0.025 * len(bm))], bm[int(math.ceil(0.975 * len(bm))) - 1]
print('independent bootstrap 95%% CI [%.4f, %.4f]' % (lo, hi))

pol = {}
for code, name in ((0, 'km3'), (1, 'kx3')):
    v = [x['D'] for x in rows if x['policy'] == code]
    pol[name] = sum(v) / len(v)
print('policy means: km3 %.4f, kx3 %.4f' % (pol['km3'], pol['kx3']))
iv, fb = sum(x['iv'] for x in rows), sum(x['fb'] for x in rows)
rate = fb / iv if iv else 0.0
print('fallback rate %d / %d = %.4f' % (fb, iv, rate))
print('model versions seen: %s' % sorted({str(x['model']) for x in rows}))


drop_n = sum(1 for x in rows if x['gf'] in ('engine_error', 'kx3_route') or x['kf'] in ('engine_error', 'kx3_route'))


def label(ci, p):
    # section 6's order: not testable, pilot not tested, too few deals, PASS, kx3 higher, inconclusive (no early stop here)
    if drop_n / 128 > 0.05:
        return 'not testable'
    if rate > 0.10:
        return 'pilot not tested'
    if n < 64:
        return 'too few deals'
    if ci[0] > 0 and p < 0.05 and pol['km3'] > 0 and pol['kx3'] > 0:
        return 'PASS / judge higher'
    if ci[1] < 0 and p < 0.05:
        return 'kx3 higher'
    return 'inconclusive'


if drop_n:
    problems.append('%d pairs would be dropped; this checker does not handle drops' % drop_n)
lab_reg_inputs = label(reg['ci'], reg['p'])
lab_mine = label((lo, hi), p_exact)
print('label from the registered CI and p: %s' % lab_reg_inputs)
print('label from this check\'s CI and exact p: %s' % lab_mine)

print('--- compare with the registered analysis.json')
cmp = [('label', reg['label'], lab_reg_inputs, reg['label'] == lab_reg_inputs),
       ('scored', reg['scored'], n, reg['scored'] == n),
       ('dropped', reg['dropped'], drop_n, reg['dropped'] == drop_n),
       ('mean_d', reg['mean_d'], mean_d, abs(reg['mean_d'] - mean_d) < 1e-12),
       ('p (MC v exact)', reg['p'], p_exact, abs(reg['p'] - p_exact) < 0.005),
       ('ci low', reg['ci'][0], lo, abs(reg['ci'][0] - lo) < 0.02),
       ('ci high', reg['ci'][1], hi, abs(reg['ci'][1] - hi) < 0.02),
       ('km3 mean', reg['policy_means']['km3'], pol['km3'], abs(reg['policy_means']['km3'] - pol['km3']) < 1e-12),
       ('kx3 mean', reg['policy_means']['kx3'], pol['kx3'], abs(reg['policy_means']['kx3'] - pol['kx3']) < 1e-12),
       ('fallback rate', reg['fallback_rate'], rate, abs(reg['fallback_rate'] - rate) < 1e-12),
       ('label (own CI, exact p)', reg['label'], lab_mine, reg['label'] == lab_mine)]
for name, a, b2, ok in cmp:
    print('%-24s registered %-22s check %-22s %s' % (name, a, b2, 'AGREE' if ok else 'DIFFER'))
    if not ok:
        problems.append('%s differs' % name)

print('--- descriptive (registered as descriptive only; 64 pairs per split value, 8 per cell, very noisy)')
names = {'deck': {0: 'A 09-mega-manectric-heliolisk', 1: 'B 11-archaludon-haxorus-dragonair'}, 'list': {0: 't-lucario', 1: 't-suicune'},
         'policy': {0: 'km3', 1: 'kx3'}, 'seat': {0: 'seat 0', 1: 'seat 1'}}
for key in ('deck', 'list', 'policy', 'seat'):
    for v in (0, 1):
        s = [x for x in rows if x[key] == v]
        print('%-7s %-34s n %3d  G wins %3d  K wins %3d  mean D %+.4f'
              % (key, names[key][v], len(s), sum(x['g'] for x in s), sum(x['kw'] for x in s), sum(x['D'] for x in s) / len(s)))
print('per cell (cell = 8 deck + 4 list + 2 policy + seat): ' + ', '.join('%d:%+d' % (c, sum(cells[c])) for c in keys))
print('per k block: ' + ', '.join('k%d:%+d' % (kk, sum(x['D'] for x in rows if x['k'] == kk)) for kk in range(8)))

print('PROBLEMS: %s' % (problems if problems else 'none'))
print('INDEP CHECK %s' % ('AGREES' if not problems else 'DISAGREES'))
