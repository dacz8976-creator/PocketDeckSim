#!/usr/bin/env python3
"""K21 section 5: the scoring. No Gemini call is made: Gemini's saved run 3 primary rows are reused (live-20261026T020013Z at e159551d).
  1. frozen-7's own checks: the tag checkout, `freeze_identity.py --check`, the plans binary = FROZEN.json's (the switch --allow-other-binaries skips
     these inside compare, so they run here first), and the card database = run 3's.
  2. the inputs: positions, references, eligibility and decks have the sha256 run 3's formal report recorded; Gemini's and km3's row files have the
     sha256 run 3's manifest recorded.
  3. kx3's rows: the seeds complete on all 258 decisions, seed-major (seed 1, then 2, then 3); every row is bot kx3, played by the K21 binary
     (pg_pos_sha256), maps to exactly one listed plan. A row that maps to no single plan stops it (section 5's stop).
  4. the PRIMARY: frozen-7's `judge.py compare --bots kx3,judge --contrasts judge:kx3 --seeds <complete> --judge-repeats 1 --on-problem fail
     --failed-judge-rows miss --allow-other-binaries`, the frozen references and eligibility. Its prefix contrast is the registered result.
  5. descriptive, no verdict: kx3 v km3 (km3's run 3 rows on the same seeds), the chance-ending stratum (168 points, computed as run 3's was: run 3's
     pool_runs.py contrast on the primary report's rows, kx3 in km3's place), the categories, the full-scope block (inside each report).
usage: compare_k21.py --live LIVE --rows ROWS_DIR --kx3-sha SHA --out OUT [--test-km3-as-kx3]
  --test-km3-as-kx3: a PATH TEST only (never a result): km3's run 3 rows renamed kx3 stand in for kx3's; the primary must then give run 3's own
  judge - km3 contrast to the printed digits, and the stratum run 3's own stratum contrast."""
import argparse, hashlib, json, os, subprocess, sys

J = '/home/dacz8976/judge7_w/rl/ai_judge'
TAG_COMMIT = '712593a1b77b203ec23fb15589c158c6bddb2bf2'
SEEDS = [25101000001, 25101000002, 25101000003]
ap = argparse.ArgumentParser()
ap.add_argument('--live', required=True)
ap.add_argument('--rows')
ap.add_argument('--kx3-sha', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--launch-commit')
ap.add_argument('--test-km3-as-kx3', action='store_true')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
LIVE, OUT = a.live, a.out
summary = {'what': 'K21 scoring' + (' -- PATH TEST: km3 rows renamed kx3, NOT a result' if a.test_km3_as_kx3 else ''), 'gemini_calls': 0}


def stop(msg):
    summary['status'] = 'STOP'
    summary['stop'] = msg
    json.dump(summary, open(os.path.join(OUT, 'SUMMARY_K21.json'), 'w'), indent=1)
    sys.exit('STOP: ' + msg)


# 1. frozen-7's checks that --allow-other-binaries skips (K21a): S1 and S2 item by item (freeze_checks_k21.py), S3 per row below
if subprocess.run(['git', '-C', J, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() != TAG_COMMIT:
    stop(f'{J} is not the frozen-7 tag')
fc = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freeze_checks_k21.py'), os.path.join(OUT, 'freeze_checks.json')],
                    capture_output=True, text=True)
open(os.path.join(OUT, 'freeze_checks.txt'), 'w').write(fc.stdout + fc.stderr)
if fc.returncode:
    stop('the restored freeze checks did not all pass: ' + (fc.stdout + fc.stderr).strip()[-400:])
sys.path.insert(0, J)
import judge  # noqa: E402
ident = judge.frozen_identity()
if judge.file_sha256(judge.PLANS_BIN) != ident['plans_binary_sha256']:
    stop('the plans binary is not FROZEN.json\'s')
BASELINE_SHA = ident['baseline']['binary_sha256']
if a.launch_commit:  # the K21 binary's sha256 must be the one committed in the launch line before any row
    lj = subprocess.run(['git', '-C', '/home/dacz8976/exam_034_w', 'show', f'{a.launch_commit}:rl/results/weekly_review_2026-10-18/exam/run3/k21/launch/LAUNCH_K21.json'],
                        capture_output=True, text=True)
    if lj.returncode or json.loads(lj.stdout).get('binary_sha256') != a.kx3_sha:
        stop(f'--kx3-sha is not the binary sha256 committed in the launch line {a.launch_commit}')
elif not a.test_km3_as_kx3:
    stop('a real scoring needs --launch-commit (the committed launch line)')
summary['freeze_checks'] = {'restored': json.load(open(os.path.join(OUT, 'freeze_checks.json')))['skipped_by_the_switch'], 'result': fc.stdout.strip()}
rep3 = json.load(open(os.path.join(LIVE, 'report_primary.json')))
inp = rep3['run']['inputs']
db = judge.card_database_path()
if not db or judge.file_sha256(db) != inp['card_database']['sha256']:
    stop(f'the card database {db} is not run 3\'s')
summary['frozen7'] = {'tag_commit': TAG_COMMIT, 'freeze_identity_check': 'pass', 'plans_binary_sha256': ident['plans_binary_sha256'], 'card_database_sha256': inp['card_database']['sha256']}

# 2. the inputs and the reused rows
I = os.path.join(LIVE, 'in')
P, D, R, E = (os.path.join(I, f) for f in ('positions.json', 'decks', 'references.json', 'eligibility.json'))
for path, key in ((P, 'positions_sha256'), (R, 'references_sha256'), (E, 'eligibility_sha256')):
    if h(path) != inp[key]:
        stop(f'{path} is not the file run 3 compared with')
if judge.dir_sha256(D) != inp['decks_sha256']:
    stop('the decks are not run 3\'s')
man = json.load(open(os.path.join(LIVE, 'run_manifest.json')))['files']
JUDGE_FILES = [os.path.join(LIVE, os.path.basename(f)) for f in open(os.path.join(LIVE, 'judge_primary.files')).read().split()]
KM3 = os.path.join(LIVE, 'km3.jsonl')
for f in JUDGE_FILES + [KM3]:
    if h(f) != man[os.path.basename(f)]:
        stop(f'{f} is not the file run 3 recorded')
ids = open(os.path.join(I, 'ids.txt')).read().split()
if len(ids) != 258 or len(set(ids)) != 258:
    stop(f'{len(ids)} ids, not 258')
summary['inputs'] = {'positions': inp['positions_sha256'], 'references': inp['references_sha256'], 'eligibility': inp['eligibility_sha256'], 'decks': inp['decks_sha256'],
                     'judge_rows': {os.path.basename(f): man[os.path.basename(f)] for f in JUDGE_FILES}, 'km3_rows': man['km3.jsonl']}

# 3. kx3's rows: the complete seeds, in order
km3_rows = [json.loads(l) for l in open(KM3) if l.strip()]
if a.test_km3_as_kx3:
    by_seed = {s: [dict(r, bot='kx3') for r in km3_rows if r['seed'] == s] for s in SEEDS}
else:
    by_seed = {}
    for s in SEEDS:
        p = os.path.join(a.rows, f'rows_{s}.jsonl')
        by_seed[s] = [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
complete, rows = [], []
for s in SEEDS:
    rs = by_seed[s]
    got = sorted(r['position'] for r in rs)
    if got != sorted(ids):
        summary.setdefault('incomplete_seeds', {})[str(s)] = f'{len(set(got) & set(ids))} of 258 decisions'
        break  # seed-major: a later seed counts only if every earlier one is complete
    for r in rs:
        if r.get('bot') != 'kx3' or r.get('seed') != s or r.get('pg_pos_sha256') != a.kx3_sha:
            stop(f'a row of seed {s} ({r.get("position")}) is not kx3 on seed {s} from the K21 binary {a.kx3_sha[:16]}')
        if r.get('plan_number') is None or r.get('match_error'):
            stop(f'kx3\'s line on {r["position"]} seed {s} maps to no single listed plan ({r.get("match_error")}): section 5\'s stop, for the coordinator')
    complete.append(s)
    rows += rs
summary['complete_seeds'] = complete
if not complete:
    stop('no seed is complete on all 258 decisions: no result (section 4)')
KX3 = os.path.join(OUT, 'kx3.jsonl')
with open(KX3, 'w') as f:
    for r in rows:
        f.write(json.dumps(r) + '\n')
KM3S = os.path.join(OUT, 'km3_same_seeds.jsonl')
with open(KM3S, 'w') as f:
    for r in km3_rows:
        if r['seed'] in complete:
            if r.get('bot') != 'km3' or r.get('pg_pos_sha256') != BASELINE_SHA:  # S3 restored for km3: the frozen baseline played every km3 row
                stop(f'a km3 row ({r.get("position")}, seed {r.get("seed")}) was not played by the frozen baseline {BASELINE_SHA[:16]}')
            f.write(json.dumps(r) + '\n')
summary['row_binaries'] = {'kx3': a.kx3_sha, 'km3': BASELINE_SHA, 'judge': 'not a step bot (its rows are checked by require_frozen, which stays on)'}
SEEDARG = ','.join(str(s) for s in complete)


def compare(name, bots, contrasts, results, id_list):
    out = os.path.join(OUT, name + '.json')
    cmd = [sys.executable, '-B', 'judge.py', 'compare', '--positions', P, '--decks', D, '--results', *results, '--ids', *id_list, '--bots', bots,
           '--contrasts', contrasts, '--seeds', SEEDARG, '--judge-repeats', '1', '--references', R, '--eligibility', E, '--on-problem', 'fail',
           '--failed-judge-rows', 'miss', '--allow-other-binaries', '--out', out]
    r = subprocess.run(cmd, cwd=J, capture_output=True, text=True)
    open(out + '.stdout', 'w').write(r.stdout + r.stderr)
    rep = json.load(open(out)) if os.path.exists(out) else {}
    run = rep.get('run') or {}
    fz = run.get('freeze') or {}
    if rep and (rep.get('formal') is not False or run.get('experiment_switches') != ['--allow-other-binaries']
                or (run.get('executables') or {}).get('plans_binary_sha256') != ident['plans_binary_sha256']
                or fz.get('fingerprint_now') != ident['fingerprint'] or fz.get('fingerprint_frozen') != ident['fingerprint'] or fz.get('tag') != 'judge-prompt-frozen-7'
                or fz.get('judge_settings') != dict(judge.judge_expectation(ident)[1])):
        stop(f'{name}: the report is not an --allow-other-binaries report on the frozen settings alone '
             f'(formal {rep.get("formal")}, switches {run.get("experiment_switches")}, fingerprint {str(fz.get("fingerprint_now"))[:12]})')
    pre = (rep.get('analysis') or {}).get('prefix') or {}
    return {'exit': r.returncode, 'status': rep.get('status'), 'formal_flag': rep.get('formal'), 'experiment_switches': (rep.get('run') or {}).get('experiment_switches'),
            'n_problems': len(rep.get('problems') or []), 'rates': pre.get('rates'), 'contrasts': pre.get('contrasts'),
            'full_scope': {k: v for k, v in ((rep.get('analysis') or {}).get('full_scope') or {}).items() if k != 'population'}}


# 4. the primary
prim = compare('report_primary_k21', 'kx3,judge', 'judge:kx3', [KX3] + JUDGE_FILES, ids)
summary['primary'] = prim
if prim['exit'] != 0:
    stop(f'the primary compare exited {prim["exit"]}: see report_primary_k21.json(.stdout)')
# 5. descriptive
summary['kx3_v_km3'] = compare('report_kx3_v_km3', 'kx3,km3', 'kx3:km3', [KX3, KM3S], ids)
# the chance-ending stratum, computed as run 3's was: run 3's own pool_runs.py (its contrast, run 3 alone, 0.95, no verdict) on the primary report's
# rows, with kx3 in km3's place (frozen compare refuses a batch that leaves out primary points, so `--ids` cannot restrict it)
import importlib.util  # noqa: E402
if h(os.path.join(LIVE, 'pool_runs.py')) != man['pool_runs.py']:
    stop('pool_runs.py is not the file run 3 used')
spec = importlib.util.spec_from_file_location('pool_runs_run3', os.path.join(LIVE, 'pool_runs.py'))
PR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PR)
AN = PR.load_analysis(os.path.join(J, 'analysis.py'))
PR.BOTS, PR.A_NAME, PR.B_NAME = ['kx3', 'judge'], 'judge', 'kx3'
elig = json.load(open(E))
prim_ids = list(elig['primary_ids'])
vals, games = PR.run_values(AN, 'K21', json.load(open(os.path.join(OUT, 'report_primary_k21.json'))), elig, prim_ids)
strat = open(os.path.join(I, 'stratum_chance_run3.txt')).read().split()
if not strat or set(strat) - set(prim_ids):
    stop('the chance stratum is not a subset of the primary points')
sp = [x for x in prim_ids if x in set(strat)]
summary['chance_stratum'] = {'what': 'descriptive only, no verdict: judge - kx3 on the chance-ending stratum (run 3 pool_runs.py contrast, 0.95)', 'n_ids': len(sp),
                             **PR.contrast(AN, vals, games, sp, 0.95, verdict=False)}
cat = subprocess.run([sys.executable, '-B', os.path.join(LIVE, 'categories.py'), os.path.join(OUT, 'report_primary_k21.json'), os.path.join(I, 'categories.json'),
                      os.path.join(OUT, 'by_category_k21.json')], capture_output=True, text=True)
open(os.path.join(OUT, 'categories_k21.txt'), 'w').write(cat.stdout + cat.stderr)
summary['categories_exit'] = cat.returncode

if a.test_km3_as_kx3:  # the path test's own check: run 3's numbers back, to the printed digits
    keys = ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games', 'sign_flip_p', 'verdict')
    want = rep3['analysis']['prefix']['contrasts'][0]
    got = (prim['contrasts'] or [{}])[0]
    sw = json.load(open(os.path.join(LIVE, 'run3_chance_stratum.json')))['stratum']['contrast']
    sg = summary['chance_stratum']['contrast']
    summary['path_test'] = {'primary_equal': all(got.get(k) == want.get(k) for k in keys), 'primary_got': {k: got.get(k) for k in keys}, 'primary_want': {k: want.get(k) for k in keys},
                            'stratum_equal': all(sg.get(k) == sw.get(k) for k in keys[:6]), 'stratum_got': {k: sg.get(k) for k in keys[:6]}, 'stratum_want': {k: sw.get(k) for k in keys[:6]}}
summary['label'] = ("EXPERIMENT: frozen-7's own label for a compare run with --allow-other-binaries (report formal: false). K21 makes it the registered kx3 "
                    "result. What replaced each check the switch skips (K21a): S1 the lister sha256 and S2 freeze_identity.check, item by item, in "
                    "freeze_checks.json (all passed, before the rows and again before the compare); S3 per row: kx3 rows = the launch line's K21 binary, "
                    "km3 rows = f35a1a99; each report checked to carry exactly that one switch, the frozen fingerprint, lister and judge settings.")
summary['status'] = 'DONE'
json.dump(summary, open(os.path.join(OUT, 'SUMMARY_K21.json'), 'w'), indent=1)
c = (prim['contrasts'] or [{}])[0]
print(f"primary (seeds {SEEDARG}): {c.get('a')} - {c.get('b')} = {c.get('estimate')} [{c.get('ci_low')}, {c.get('ci_high')}], p {c.get('sign_flip_p')}: {c.get('verdict')}")
if a.test_km3_as_kx3:
    print('PATH TEST:', json.dumps({k: summary['path_test'][k] for k in ('primary_equal', 'stratum_equal')}), '| kx3 v km3 exit', summary['kx3_v_km3']['exit'],
          '| categories exit', cat.returncode)
