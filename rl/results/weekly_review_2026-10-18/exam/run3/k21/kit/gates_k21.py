#!/usr/bin/env python3
"""K21's gates (the dry run), on DEVELOPMENT positions only (pause games, heldout false; never an exam position). Every gate must pass, or no exam
row is played. Writes K/gates/GATES.json; exit 0 only if all pass.
  (a) Same engine and printer: km3 on the K21 binary prints byte-identical output to frozen-7's baseline f35a1a99, on 6 positions, seeds 1-3 and 25,101,900,101-103.
  (b) Same kx3: the K21 binary's kx3 reproduces the frozen pilot's recorded lines on 3 positions where kx3 differs from km3:
      KW-261005_003547000-t11 and -t13 (pause-positions study, PF3 runs_B; seeds 1-3) and KW-261013_015659000-t05 (P8_v3 runs_F, made with
      pg_pos_F_cond2 on cd20a97a and the same pg_pos.rs; seeds 3 and 9). Labels: short labels compared as printed; frozen-7's `Name#JSON` compared by
      its name where the old printer gave a bare name; the old `RetreatPay:<slot>` compared as ChooseRetreatEnergy.
  (c) The row runner: kx3_rows.py with frozen-7's baseline and km3 equals `judge.py run --bot km3` field for field (3 positions, seeds 25,101,900,101-103); and every
      kx3 line of (b) maps to exactly one listed plan.
  (d) The timing: kx3's seconds per position and seed in (b).
usage: gates_k21.py K_DIR NEW_BIN"""
import json, os, subprocess, sys, time

K, NEW = sys.argv[1], sys.argv[2]
J = '/home/dacz8976/judge7_w/rl/ai_judge'
BASE = '/home/dacz8976/ai_judge_pgpos/bin/pg_pos_target_preserving'
REPO = '/home/dacz8976/exam_034_w'
G = os.path.join(K, 'gates')
os.makedirs(G, exist_ok=True)
sys.path.insert(0, J)
import judge  # noqa: E402

if judge.file_sha256(BASE) != 'f35a1a99188806c7713cc40dd8fff65172c21a15d5449174f1cd3c1cfc40ad36':
    sys.exit('the frozen baseline is not f35a1a99: stop')
if os.environ.get('KX_EXTRA_LISTS'):
    sys.exit('KX_EXTRA_LISTS is set: stop')
MAIN = subprocess.run(['git', '-C', REPO, 'rev-parse', 'origin/main'], capture_output=True, text=True, check=True).stdout.strip()


def show(path, dest):
    b = subprocess.run(['git', '-C', REPO, 'show', f'{MAIN}:{path}'], capture_output=True, check=True).stdout
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'wb').write(b)
    return b


def dev_set(name, folder):
    """A development positions file and its decks, from main."""
    d = os.path.join(G, name)
    show(f'{folder}/positions_all.json', os.path.join(d, 'positions_all.json'))
    names = subprocess.run(['git', '-C', REPO, 'ls-tree', '--name-only', f'{MAIN}:{folder}/decks'], capture_output=True, text=True, check=True).stdout.split()
    for n in names:
        if n.endswith('.txt'):
            show(f'{folder}/decks/{n}', os.path.join(d, 'decks', n))
    pos = {p['id']: p for p in json.load(open(os.path.join(d, 'positions_all.json'), encoding='utf-8'))}
    return d, pos


A, posA = dev_set('A', 'rl/results/pause_games_new_2026-10-12')
B, posB = dev_set('B', 'rl/results/pause_games_new_2026-10-13/v2')
SETS = {'A': A, 'B': B}
GATE_A = [('A', 'KW-261005_003547000-t11'), ('A', 'KW-261005_003547000-t13'), ('A', 'KW-261005_034953000-t02'),
          ('B', 'KW-261013_015659000-t05'), ('B', 'KW-261012_203719000-t13'), ('B', 'KW-261012_210823000-t04')]
for s, pid in GATE_A:
    if pid not in (posA if s == 'A' else posB) or (posA if s == 'A' else posB)[pid].get('heldout'):
        sys.exit(f'{pid}: not a development position of set {s}: stop')
res = {'what': "K21's gates on development positions only", 'main': MAIN, 'new_binary_sha256': judge.file_sha256(NEW)}


def pg(binary, s, pid, seeds, bot):
    d = SETS[s]
    cmd = [binary, '--positions', os.path.join(d, 'positions_all.json')] + judge.deck_args(os.path.join(d, 'decks')) + ['--seeds', seeds, '--bot', bot, '--only', pid]
    t = time.time()
    r = subprocess.run(['nice', '-n', '19'] + cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, time.time() - t


GATE_SEEDS = '25101900101,25101900102,25101900103'  # K21 section 4: the gates use the positions' recorded seeds plus 25,101,900,101 and up
# (a) km3: byte-identical stdout, seeds 1-3 (section 2) and the gate seeds
a = []
for s, pid in GATE_A:
    rc1, o1, _ = pg(BASE, s, pid, '1,2,3,' + GATE_SEEDS, 'km3')
    rc2, o2, _ = pg(NEW, s, pid, '1,2,3,' + GATE_SEEDS, 'km3')
    a.append({'position': pid, 'equal': rc1 == 0 and rc2 == 0 and o1 == o2 and o1.strip() != ''})
res['a_km3_identical'] = a
ok_a = all(x['equal'] for x in a)


# (b) + (c-kx3) + (d): kx3 through kx3_rows.py, against the recorded frozen-pilot lines
def norm(labels):
    out = []
    for l in labels or []:
        if l.startswith('RetreatPay:'):
            out.append('ChooseRetreatEnergy')
        elif '#' in l:
            out.append(l.split('#', 1)[0])
        else:
            out.append(l)
    return out


REC = {'KW-261005_003547000-t11': 'rl/results/pause_positions_kx3_2026-10/workers/PF3/runs_B/out_KW-261005_003547000-t11.jsonl',
       'KW-261005_003547000-t13': 'rl/results/pause_positions_kx3_2026-10/workers/PF3/runs_B/out_KW-261005_003547000-t13.jsonl',
       'KW-261013_015659000-t05': 'rl/results/pause_positions_kx3_2026-10/workers/P8_v3/runs_F/out_KW-261013_015659000-t05.jsonl'}
recorded = {}
for pid, path in REC.items():
    b = show(path, os.path.join(G, 'recorded', os.path.basename(path)))
    for line in b.decode().splitlines():
        j = json.loads(line)
        if j.get('kind') == 'free':
            recorded[(pid, j['seed'])] = j.get('plan')
RUNS = [('A', ['KW-261005_003547000-t11', 'KW-261005_003547000-t13'], '1,2,3'), ('B', ['KW-261013_015659000-t05'], '3,9')]
b_rows, timing = [], []
here = os.path.dirname(os.path.abspath(__file__))
for s, ids, seeds in RUNS:
    d = SETS[s]
    idf = os.path.join(G, f'ids_{s}.txt')
    open(idf, 'w').write('\n'.join(ids) + '\n')
    out = os.path.join(G, f'kx3_{s}')
    r = subprocess.run([sys.executable, '-B', os.path.join(here, 'kx3_rows.py'), '--judge-dir', J, '--bin', NEW, '--bot', 'kx3',
                        '--positions', os.path.join(d, 'positions_all.json'), '--decks', os.path.join(d, 'decks'), '--ids', idf, '--seeds', seeds,
                        '--out-dir', out], capture_output=True, text=True)
    open(os.path.join(G, f'kx3_{s}.log'), 'w').write(r.stdout + r.stderr)
    if r.returncode:
        b_rows.append({'set': s, 'error': (r.stdout + r.stderr)[-600:]})
        continue
    for seed in seeds.split(','):
        for line in open(os.path.join(out, f'rows_{seed}.jsonl')):
            row = json.loads(line)
            want = recorded.get((row['position'], row['seed']))
            b_rows.append({'position': row['position'], 'seed': row['seed'], 'got': row['plan_full'], 'recorded': want,
                           'reproduced': want is not None and norm(row['plan_full']) == norm(want),
                           'maps_to_one_plan': row['plan_number'] is not None and not row['match_error'], 'match_error': row['match_error']})
    for line in open(os.path.join(out, 'timing.tsv')):
        seed, pid, secs, *_ = line.rstrip('\n').split('\t')
        timing.append({'position': pid, 'seed': int(seed), 'seconds': float(secs)})
res['b_kx3_reproduced'] = b_rows
res['d_timing'] = timing
ok_b = bool(b_rows) and all(x.get('reproduced') for x in b_rows)
ok_c2 = bool(b_rows) and all(x.get('maps_to_one_plan') for x in b_rows)

# (c) the runner: kx3_rows.py (frozen-7's baseline, km3) equals judge.py run --bot km3, field for field
ids_c = ['KW-261013_015659000-t05', 'KW-261012_203719000-t13', 'KW-261012_210823000-t04']
idf = os.path.join(G, 'ids_c.txt')
open(idf, 'w').write('\n'.join(ids_c) + '\n')
ref = os.path.join(G, 'c_judge_run_km3.jsonl')
r1 = subprocess.run([sys.executable, '-B', 'judge.py', 'run', '--bot', 'km3', '--positions', os.path.join(B, 'positions_all.json'), '--decks', os.path.join(B, 'decks'),
                     '--ids', *ids_c, '--seeds', GATE_SEEDS, '--out', ref], cwd=J, capture_output=True, text=True)
outc = os.path.join(G, 'c_rows_km3')
r2 = subprocess.run([sys.executable, '-B', os.path.join(here, 'kx3_rows.py'), '--judge-dir', J, '--bin', BASE, '--bot', 'km3', '--positions', os.path.join(B, 'positions_all.json'),
                     '--decks', os.path.join(B, 'decks'), '--ids', idf, '--seeds', GATE_SEEDS, '--out-dir', outc], capture_output=True, text=True)
c = {'judge_run_rc': r1.returncode, 'rows_rc': r2.returncode, 'judge_run_tail': (r1.stdout + r1.stderr)[-400:], 'rows_tail': (r2.stdout + r2.stderr)[-400:]}
ok_c1 = False
if r1.returncode == 0 and r2.returncode == 0 and os.path.exists(ref):
    want = {}
    for line in open(ref):
        if line.strip():
            j = json.loads(line)
            want[(j['position'], j['seed'])] = j
    got = {}
    for seed in (int(x) for x in GATE_SEEDS.split(',')):
        for line in open(os.path.join(outc, f'rows_{seed}.jsonl')):
            j = json.loads(line)
            got[(j['position'], j['seed'])] = j
    diffs = [(k, sorted(f for f in set(want[k]) | set(got.get(k, {})) if want[k].get(f) != got.get(k, {}).get(f))) for k in want if want[k] != got.get(k)]
    c.update({'rows': len(want), 'equal': len(want) - len(diffs), 'diffs': diffs[:5], 'same_keys': set(want) == set(got)})
    ok_c1 = not diffs and set(want) == set(got) and len(want) == 9
res['c_runner'] = c
res['pass'] = {'a': ok_a, 'b': ok_b, 'c': ok_c1 and ok_c2, 'd': bool(timing)}
res['all_pass'] = all(res['pass'].values())
json.dump(res, open(os.path.join(G, 'GATES.json'), 'w'), indent=1)
print(json.dumps(res['pass']), '| all pass:', res['all_pass'])
print('timing (kx3 s per position-seed):', [(t['position'][-12:], t['seed'], round(t['seconds'])) for t in timing])
sys.exit(0 if res['all_pass'] else 1)
