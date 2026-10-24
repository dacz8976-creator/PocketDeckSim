#!/usr/bin/env python3
"""The pooling script's reproduction test (PREREG_RUN3 section 4): on run 2 alone at 95% it must give run 2's report_primary.json prefix contrast and
rates to the printed digits; and its refusals hold. TwoSyntheticRuns pools two DISTINCT runs built here from made-up rows (no real run's file is read):
the pooled numbers checked by hand, the interval against frozen-7's own game_bootstrap on the hand-pooled clusters and against analysis.analyse on one
batch of both runs, a degenerate case whose interval must collapse, and the cross-run refusals. usage (from the exam folder): python3 run3/test_pool_runs.py ANALYSIS_PY"""
import copy, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXAM = os.path.dirname(HERE)
RUN2 = os.path.join(EXAM, 'run2', 'live-20261021T2000Z')
REPORT, ELIG = os.path.join(RUN2, 'report_primary.json'), os.path.join(RUN2, 'in', 'eligibility.json')
ANALYSIS = sys.argv.pop(1) if len(sys.argv) > 1 else None


def pool(*args):
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as t:
        out = t.name
    r = subprocess.run([sys.executable, os.path.join(HERE, 'pool_runs.py'), '--analysis', ANALYSIS, *args, '--out', out], capture_output=True, text=True)
    res = None
    if os.path.getsize(out):
        with open(out) as f:
            res = json.load(f)
    os.unlink(out)
    return r, res


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class Reproduces(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, obj):
        d = os.path.join(self.tmp, name)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, 'file.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f)
        return path

    def report_variant(self, name, fn):
        rep = copy.deepcopy(load(REPORT))
        fn(rep)
        return self.write(name, rep)

    def refused(self, *args, why):
        r, _ = pool(*args)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotEqual(r.returncode, 3)
        self.assertIn(why, r.stdout + r.stderr)

    def test_run2_alone_at_95_equals_its_report(self):
        r, res = pool('--run', REPORT, ELIG, '--confidence', '0.95')
        self.assertEqual(r.returncode, 0, r.stderr)
        rep = load(REPORT)
        want = rep['analysis']['prefix']['contrasts'][0]
        got = res['primary']['contrast']
        for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games', 'sign_flip_p', 'sign_flip', 'verdict'):
            self.assertEqual(got[k], want[k], k)
        self.assertEqual((got['estimate'], got['ci_low'], got['ci_high'], got['sign_flip_p']), (0.163265, -0.014184, 0.346939, 0.108869))
        for b in ('km3', 'judge'):
            w = rep['analysis']['prefix']['rates'][b]
            for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games'):
                self.assertEqual(res['primary']['rates'][b][k], w[k], (b, k))
        self.assertEqual(res['judge_models'], ['gemini-4-argon'])
        self.assertIsNone(res['primary']['pass'])
        self.assertEqual(res['primary']['failed_replies'], {'n': 0, 'share': 0.0, 'over_20pct': False})
        self.assertEqual(res['per_run'][0]['alone_at_0.95_equals_its_report']['verdict'], 'inconclusive')

    def test_the_975_interval_is_wider(self):
        r, res = pool('--run', REPORT, ELIG)
        self.assertEqual(r.returncode, 0, r.stderr)
        c = res['primary']['contrast']
        self.assertEqual(res['confidence'], 0.975)
        self.assertEqual((c['ci_low'], c['ci_high']), (-0.039683, 0.371795))
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIs(res['primary']['pass'], False)

    def test_another_analysis_is_refused(self):
        bad = os.path.join(self.tmp, 'analysis.py')
        with open(ANALYSIS) as src, open(bad, 'w') as t:
            t.write(src.read() + '\n# changed\n')
        r = subprocess.run([sys.executable, os.path.join(HERE, 'pool_runs.py'), '--analysis', bad, '--run', REPORT, ELIG, '--out', os.devnull],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('refused', r.stdout + r.stderr)

    def test_the_same_run_twice_is_refused(self):
        self.refused('--run', REPORT, ELIG, '--run', REPORT, ELIG, why='appears in two runs')

    def test_another_model_turns_pooling_off(self):
        for name, fn in (('model', lambda rep: rep['run'].update(judge_models_returned=['gemini-4-argon-002'])),
                         ('two', lambda rep: rep['run'].update(judge_models_returned=['gemini-4-argon', 'gemini-4-argon-002'])),
                         ('warn', lambda rep: rep['run'].update(warnings=['the judge model version changed during the run']))):
            r, res = pool('--run', self.report_variant(name, fn), ELIG)
            self.assertEqual(r.returncode, 3, (name, r.stderr))
            self.assertIn('OFF', res['pooling'])
            self.assertNotIn('primary', res)
        r, res = pool('--run', REPORT, ELIG, '--run', self.report_variant('run3', lambda rep: rep['run'].update(judge_models_returned=['gemini-4-argon-002'])),
                      ELIG)
        self.assertEqual(r.returncode, 3, r.stderr)

    def test_an_eligibility_not_the_reports_is_refused(self):
        e = load(ELIG)
        regrouped = dict(e, games={p: f'G{i}' for i, p in enumerate(e['primary_ids'])})
        path = self.write('regrouped', regrouped)
        self.refused('--run', REPORT, path, why='is not the eligibility file the report was made from')
        with open(path, 'rb') as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        rep = self.report_variant('regrouped_rep', lambda rep: rep['run']['inputs'].update(eligibility_sha256=sha))
        self.refused('--run', rep, path, why="is not the eligibility's")

    def test_a_primary_subset_is_refused(self):
        e = load(ELIG)
        path = self.write('subset', dict(e, primary_ids=e['primary_ids'][:40]))
        with open(path, 'rb') as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        rep = self.report_variant('subset_rep', lambda rep: rep['run']['inputs'].update(eligibility_sha256=sha))
        self.refused('--run', rep, path, why="row positions are not exactly the eligibility's primary_ids")

    def test_request_drift_is_refused(self):
        for name, fn in (('seeds', lambda rep: rep['run']['request'].update(seeds=rep['run']['request']['seeds'][:1])),
                         ('policy', lambda rep: rep['run']['request'].update(failed_judge_rows='exclude')),
                         ('resamples', lambda rep: rep['run']['request'].update(resamples=5000)),
                         ('tag', lambda rep: rep['run']['freeze'].update(tag='judge-prompt-frozen-6'))):
            self.refused('--run', self.report_variant(name, fn), ELIG, why='refused')

    def test_a_report_number_the_script_does_not_give_is_refused(self):
        rep = self.report_variant('num', lambda rep: rep['analysis']['prefix']['contrasts'][0].update(estimate=0.2))
        self.refused('--run', rep, ELIG, why="does not give the report's own numbers")

    def test_failed_replies_are_counted(self):
        def fn(rep):
            n = 0
            for r in rep['rows']:
                if r['bot'] == 'judge' and r['agrees'] is False and n < 11:
                    r['state'], n = 'no_choice', n + 1
            rep['failed_judge_rows']['n_primary_decisions'] = 11
        r, res = pool('--run', self.report_variant('failed', fn), ELIG)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(res['primary']['failed_replies'], {'n': 11, 'share': round(11 / 49, 6), 'over_20pct': True})
        self.assertEqual(res['primary']['contrast']['ci_low'], -0.039683)
        wrong = self.report_variant('failed_wrong', lambda rep: (fn(rep), rep['failed_judge_rows'].update(n_primary_decisions=0)))
        self.refused('--run', wrong, ELIG, why='failed primary judge replies')

    def test_the_stratum_is_a_subset_and_has_no_verdict(self):
        ids = load(ELIG)['primary_ids']
        good = os.path.join(self.tmp, 'stratum.txt')
        with open(good, 'w') as f:
            f.write('\n'.join(ids[:20]) + '\n')
        r, res = pool('--run', REPORT, ELIG, '--stratum', good)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('verdict', res['stratum']['contrast'])
        self.assertEqual(res['stratum']['population']['n_decisions'], 20)
        bad = os.path.join(self.tmp, 'stratum_bad.txt')
        with open(bad, 'w') as f:
            f.write('\n'.join(ids[:5] + ['LAD-nosuchgame-t1']) + '\n')
        self.refused('--run', REPORT, ELIG, '--stratum', bad, why='non-empty subset')

    def test_a_confidence_typo_is_refused(self):
        self.refused('--run', REPORT, ELIG, '--confidence', '0.0975', why='outside')

    def test_float_noise_at_zero_does_not_exclude_zero(self):
        # run 2's points, each its own game, at 0.95: the bootstrap's lower bound is 0 exactly in thirds but about +4.5e-18 as floats
        sys.path.insert(0, HERE)
        import pool_runs
        A = pool_runs.load_analysis(ANALYSIS)
        rep, e, prim, _ = pool_runs.load_run(A, 'run2', REPORT, ELIG)
        vals, _ = pool_runs.run_values(A, 'run2', rep, e, prim)
        c = pool_runs.contrast(A, vals, {p: p for p in prim}, prim, 0.95)['contrast']
        self.assertEqual(c['ci_low'], 0.0)
        self.assertEqual((c['verdict'], c['reason']), ('inconclusive', 'the interval includes 0'))


# ---------------------------------------------------------------------------------------------------------- two DISTINCT runs, all synthetic (F7)
# Every row below is made up for these tests; no real run's file is read. A point is (point id, game id, judge, km3 by seed): judge 1 = agrees,
# 0 = disagrees, 'failed' = a failed reply (state no_choice, which the policy 'miss' scores as a disagreement); km3 = one 0/1 per seed, in seed order.
# The comment after each point is its difference judge - (km3 mean over its 3 seeds).
RUN_A = [
    ('SYN-A-g1-t1', 'SYN-A-g1', 1, (1, 1, 1)),          # 1 - 1   = 0
    ('SYN-A-g1-t2', 'SYN-A-g1', 1, (0, 0, 0)),          # 1 - 0   = 1
    ('SYN-A-g2-t1', 'SYN-A-g2', 1, (1, 0, 0)),          # 1 - 1/3 = 2/3
    ('SYN-A-g3-t1', 'SYN-A-g3', 'failed', (1, 1, 0)),   # 0 - 2/3 = -2/3  (a failed reply)
    ('SYN-A-g4-t1', 'SYN-A-g4', 1, (0, 0, 0)),          # 1 - 0   = 1
    ('SYN-A-g5-t1', 'SYN-A-g5', 0, (0, 0, 0)),          # 0 - 0   = 0
    ('SYN-A-g5-t2', 'SYN-A-g5', 1, (1, 1, 1)),          # 1 - 1   = 0
]
RUN_B = [
    ('SYN-B-g1-t1', 'SYN-B-g1', 1, (0, 1, 1)),          # 1 - 2/3 = 1/3
    ('SYN-B-g2-t1', 'SYN-B-g2', 0, (1, 1, 1)),          # 0 - 1   = -1
    ('SYN-B-g2-t2', 'SYN-B-g2', 1, (0, 0, 1)),          # 1 - 1/3 = 2/3
    ('SYN-B-g3-t1', 'SYN-B-g3', 'failed', (0, 0, 0)),   # 0 - 0   = 0     (a failed reply)
    ('SYN-B-g4-t1', 'SYN-B-g4', 1, (1, 0, 0)),          # 1 - 1/3 = 2/3
    ('SYN-B-g5-t1', 'SYN-B-g5', 1, (0, 0, 0)),          # 1 - 0   = 1
]
SEEDS_A, SEEDS_B = [101, 102, 103], [201, 202, 203]
# The hand-pooled difference clusters: one (sum over the game's points, number of points) per game, in sorted game order (SYN-A-g1 .. g5, SYN-B-g1 .. g5).
# Each sum is written as the float expression pool_runs evaluates (judge value - km3 mean, added point by point), so the floats agree bit for bit.
POOLED_DIFF_SUMS = [(1 - 1) + (1 - 0), 1 - 1/3, 0 - 2/3, 1 - 0, (0 - 0) + (1 - 1), 1 - 2/3, (0 - 1) + (1 - 1/3), 0 - 0, 1 - 1/3, 1 - 0]
POOLED_COUNTS = [2, 1, 1, 1, 2, 1, 2, 1, 1, 1]
# Degenerate runs: every game of both has difference sum 2/3 over 2 points, reached two different ways (run C: (1 - 1/3) + (0 - 0); run D: (1 - 1) + (1 - 1/3)).
SAME_C = [p for i in range(1, 6) for p in ((f'SYN-C-g{i}-t1', f'SYN-C-g{i}', 1, (0, 0, 1)), (f'SYN-C-g{i}-t2', f'SYN-C-g{i}', 0, (0, 0, 0)))]
SAME_D = [p for i in range(1, 8) for p in ((f'SYN-D-g{i}-t1', f'SYN-D-g{i}', 1, (1, 1, 1)), (f'SYN-D-g{i}-t2', f'SYN-D-g{i}', 1, (0, 0, 1)))]


def load_frozen_analysis():
    """frozen-7's analysis.py, loaded here on its own (not through pool_runs), to build the synthetic reports and to recompute the pooled interval."""
    spec = importlib.util.spec_from_file_location('analysis_frozen7_for_tests', ANALYSIS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TwoSyntheticRuns(unittest.TestCase):
    """Two DISTINCT runs pooled: each with its own games, point ids, km3 seeds and a self-consistent formal report (its analysis block made by frozen-7's
    analysis.analyse on its rows, as the formal compare makes it, policy 'miss')."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, HERE)
        import pool_runs
        cls.P = pool_runs
        cls.A = load_frozen_analysis()

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def make_run(self, name, points, seeds, tamper=None):
        """Writes NAME/in/eligibility.json and NAME/report_primary.json (so pool_runs labels the run NAME) and returns (report, eligibility, rows, eligibility dict).
        `tamper(rep)` changes the report after it is built, before it is written."""
        A, P = self.A, self.P
        rows, games = [], {}
        for pid, game, judge, km3 in points:
            games[pid] = game
            failed = judge == 'failed'
            rows.append({'position': pid, 'game': game, 'bot': 'judge', 'run': A.PRIMARY_JUDGE_RUN, 'state': 'no_choice' if failed else 'ok',
                         'plan_number': None if failed else 1, 'agrees': judge == 1})
            for seed, k in zip(seeds, km3):
                rows.append({'position': pid, 'game': game, 'bot': 'km3', 'run': seed, 'state': 'ok', 'plan_number': 1 if k else 2, 'agrees': k == 1})
        elig = {'schema': A.ELIGIBILITY_SCHEMA, 'primary_ids': [p[0] for p in points], 'full_scope_ids': [], 'games': games, 'excluded_reasons': {}}
        self.assertEqual(A.eligibility_shape_problems(elig), [])
        os.makedirs(os.path.join(self.tmp, name, 'in'), exist_ok=True)
        elig_path, rep_path = os.path.join(self.tmp, name, 'in', 'eligibility.json'), os.path.join(self.tmp, name, 'report_primary.json')
        with open(elig_path, 'w', encoding='utf-8') as f:
            json.dump(elig, f)
        with open(elig_path, 'rb') as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        rep = {'status': 'complete', 'formal': True, 'problems': [],
               'run': {'freeze': {'tag': P.FROZEN7_TAG, 'fingerprint_now': P.FROZEN7_FINGERPRINT, 'fingerprint_frozen': P.FROZEN7_FINGERPRINT},
                       'request': {'bots': 'km3,judge', 'seeds': list(seeds), 'failed_judge_rows': 'miss', 'resamples': A.RESAMPLES, 'min_games': A.MIN_GAMES},
                       'inputs': {'eligibility_sha256': sha}, 'judge_models_returned': ['gemini-4-argon'], 'warnings': []},
               'rows': rows,
               'failed_judge_rows': {'policy': 'miss', 'n_primary_decisions': sum(1 for p in points if p[2] == 'failed')},
               'analysis': A.analyse(rows, elig, ['km3', 'judge'], 1, failed_judge_rows='miss')}
        if tamper:
            tamper(rep)
        with open(rep_path, 'w', encoding='utf-8') as f:
            json.dump(rep, f)
        return rep_path, elig_path, rows, elig

    def refused(self, *args, why):
        r, res = pool(*args)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertNotEqual(r.returncode, 3, r.stdout)
        self.assertIn(why, r.stdout + r.stderr)
        self.assertIsNone(res)  # nothing was written
        return r.stdout + r.stderr

    def test_the_hand_clusters_are_the_runs(self):
        # the literal clusters above, checked against the point lists: same games in sorted order, same counts, same sums to the last bit
        pts = RUN_A + RUN_B
        order = sorted({g for _, g, _, _ in pts})
        self.assertEqual(order, [f'SYN-{r}-g{i}' for r in 'AB' for i in range(1, 6)])
        diff = lambda j, k: (1 if j == 1 else 0) - sum(k) / 3
        sums = [sum(diff(j, k) for _, g2, j, k in pts if g2 == g) for g in order]
        self.assertEqual(sums, POOLED_DIFF_SUMS)
        self.assertEqual([sum(1 for _, g2, _, _ in pts if g2 == g) for g in order], POOLED_COUNTS)
        self.assertEqual((sum(POOLED_COUNTS), round(sum(POOLED_DIFF_SUMS) * 3, 9)), (13, 11.0))  # 13 points, differences add to 11/3

    def test_two_runs_pooled_by_hand(self):
        A = self.A
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        rb, eb, _, _ = self.make_run('synB', RUN_B, SEEDS_B)
        stratum = os.path.join(self.tmp, 'stratum.txt')
        with open(stratum, 'w') as f:
            f.write('SYN-A-g1-t2\nSYN-B-g2-t1\nSYN-B-g5-t1\n')
        r, res = pool('--run', ra, ea, '--run', rb, eb, '--stratum', stratum)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((res['confidence'], res['judge_models']), (0.975, ['gemini-4-argon']))
        pr = res['primary']
        c = pr['contrast']
        self.assertEqual(pr['population'], {'n_decisions': 13, 'n_games': 10})  # 7 + 6 points, 5 + 5 games
        # judge - km3 by hand: run A's differences add to 0 + 1 + 2/3 - 2/3 + 1 + 0 + 0 = 2, run B's to 1/3 - 1 + 2/3 + 0 + 2/3 + 1 = 5/3;
        # every decision weighs the same: (2 + 5/3) / 13 = 11/39 = 0.2820513
        self.assertEqual((c['a'], c['b'], c['estimate'], c['n_decisions'], c['n_games'], c['n_pairs_dropped']), ('judge', 'km3', 0.282051, 13, 10, 0))
        # rates by hand: the judge agrees at 5 of run A's 7 points (SYN-A-g3-t1 is a failed reply = a miss, SYN-A-g5-t1 disagrees) and 4 of run B's 6:
        # 9/13 = 0.6923077. km3's seed means: run A 1 + 0 + 1/3 + 2/3 + 0 + 0 + 1 = 3, run B 2/3 + 1 + 1/3 + 0 + 1/3 + 0 = 7/3: (16/3) / 13 = 16/39 = 0.4102564
        # (and 9/13 - 16/39 = 27/39 - 16/39 = 11/39, the contrast)
        self.assertEqual({b: (pr['rates'][b]['estimate'], pr['rates'][b]['n_decisions'], pr['rates'][b]['n_games']) for b in ('judge', 'km3')},
                         {'judge': (0.692308, 13, 10), 'km3': (0.410256, 13, 10)})
        # the interval: frozen-7's own game_bootstrap called directly on the hand-pooled clusters, with analysis.RESAMPLES draws, seed analysis.SEED and
        # the level 0.975 (one draw of games serves every series, so a bootstrap of the difference series alone makes the same draws)
        point, lo, hi = A.game_bootstrap({'diff': (POOLED_DIFF_SUMS, POOLED_COUNTS)}, A.RESAMPLES, A.SEED, 0.975)['diff']
        self.assertEqual(round(point, 6), 0.282051)
        self.assertEqual((c['ci_low'], c['ci_high']), (round(lo, 6), round(hi, 6)))
        self.assertLess(c['ci_low'], c['estimate'])  # a real interval here, not a collapsed one
        self.assertLess(c['estimate'], c['ci_high'])
        # the sign-flip p by hand (exact: 10 games <= 16). In thirds the game sums are 3, 2, -2, 3, 0 | 1, -1, 0, 2, 3, observed |11|. The non-zero sizes
        # 3,3,3,2,2,2,1,1 add to 17; flipping a set of total size N gives 17 - 2N, and |17 - 2N| >= 11 iff N <= 3 or N >= 14 (its complement <= 3).
        # Sets of size <= 3: {} 1, {1} 2, {2} 3 + {1,1} 1, {3} 3 + {2,1} 6 = 16; twice (the complements) = 32 of 2^8; times 2^2 for the two zero games:
        # 128 / 1024 = 0.125
        self.assertEqual((c['sign_flip_p'], c['sign_flip']), (0.125, 'exact'))
        self.assertEqual(A.sign_flip_p(POOLED_DIFF_SUMS, A.SEED), (0.125, 'exact'))
        # 10 games = analysis.MIN_GAMES, so pooled the gate is open (alone each run has 5); p = 0.125 is not < 0.025, so no direction either way: no PASS
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIn(c['reason'], ('the interval includes 0', 'the interval excludes 0 but the sign-flip p = 0.125000 is not < 0.025'))
        self.assertIs(pr['pass'], False)
        # failed replies: SYN-A-g3-t1 and SYN-B-g3-t1, pooled 2 / 13 = 0.1538462 (under 20%); per run 1 / 7 = 0.1428571 and 1 / 6 = 0.1666667
        self.assertEqual(pr['failed_replies'], {'n': 2, 'share': 0.153846, 'over_20pct': False})
        run_a, run_b = res['per_run']
        self.assertEqual((run_a['label'], run_a['n_decisions'], run_a['n_games'], run_a['km3_seeds']), ('synA (#1)', 7, 5, SEEDS_A))
        self.assertEqual((run_b['label'], run_b['n_decisions'], run_b['n_games'], run_b['km3_seeds']), ('synB (#2)', 6, 5, SEEDS_B))
        self.assertEqual(run_a['failed_replies'], {'n': 1, 'share': 0.142857, 'over_20pct': False})
        self.assertEqual(run_b['failed_replies'], {'n': 1, 'share': 0.166667, 'over_20pct': False})
        # each run alone at 0.95 (its own report, which the script reproduced): run A 2 / 7 = 0.2857143, run B (5/3) / 6 = 5/18 = 0.2777778; 5 games < 10.
        # Sign-flip by hand, in thirds: A's 3, 2, -2, 3, 0 (observed 6, sizes add to 10, N <= 2 or N >= 8: {}, {2}, {2} = 3, twice, times 2 for the zero
        # game = 12/32 = 0.375); B's 1, -1, 0, 2, 3 (observed 5, sizes add to 7, N <= 1 or N >= 6: {}, {1}, {1} = 3, twice, times 2 = 12/32 = 0.375)
        keys = ('estimate', 'n_decisions', 'n_games', 'sign_flip_p', 'sign_flip', 'verdict')
        self.assertEqual(tuple(run_a['alone_at_0.95_equals_its_report'][k] for k in keys), (0.285714, 7, 5, 0.375, 'exact', 'inconclusive'))
        self.assertEqual(tuple(run_b['alone_at_0.95_equals_its_report'][k] for k in keys), (0.277778, 6, 5, 0.375, 'exact', 'inconclusive'))
        # the stratum spans both runs: SYN-A-g1-t2 (1), SYN-B-g2-t1 (-1), SYN-B-g5-t1 (1): (1 - 1 + 1) / 3 = 0.333333 over 3 games; no verdict
        s = res['stratum']
        self.assertEqual(s['n_by_run'], {'synA (#1)': 1, 'synB (#2)': 2})
        self.assertEqual((s['contrast']['estimate'], s['contrast']['n_decisions'], s['contrast']['n_games']), (0.333333, 3, 3))
        self.assertNotIn('verdict', s['contrast'])

    def test_pooled_equals_one_batch_of_both_runs_in_either_order(self):
        # at 0.95 pooling must give what frozen-7's analysis.analyse gives on ONE batch holding both runs' rows (the formal compare's own computation),
        # whichever run is named first; and the interval is again game_bootstrap's on the hand clusters, now at 0.95
        A = self.A
        ra, ea, rows_a, el_a = self.make_run('synA', RUN_A, SEEDS_A)
        rb, eb, rows_b, el_b = self.make_run('synB', RUN_B, SEEDS_B)
        one = {'schema': A.ELIGIBILITY_SCHEMA, 'primary_ids': el_a['primary_ids'] + el_b['primary_ids'], 'full_scope_ids': [],
               'games': {**el_a['games'], **el_b['games']}, 'excluded_reasons': {}}
        want = A.analyse(rows_a + rows_b, one, ['km3', 'judge'], 1, failed_judge_rows='miss')['prefix']
        wc = want['contrasts'][0]
        self.assertEqual((wc['a'], wc['b'], wc['estimate'], wc['n_games']), ('judge', 'km3', 0.282051, 10))
        _, lo, hi = A.game_bootstrap({'diff': (POOLED_DIFF_SUMS, POOLED_COUNTS)}, A.RESAMPLES, A.SEED, 0.95)['diff']
        self.assertEqual((wc['ci_low'], wc['ci_high']), (round(lo, 6), round(hi, 6)))
        for first, second in (((ra, ea), (rb, eb)), ((rb, eb), (ra, ea))):
            r, res = pool('--run', *first, '--run', *second, '--confidence', '0.95')
            self.assertEqual(r.returncode, 0, r.stderr)
            got = res['primary']
            for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games', 'n_pairs_dropped', 'sign_flip_p', 'sign_flip', 'verdict'):
                self.assertEqual(got['contrast'][k], wc[k], (first, k))
            for b in ('km3', 'judge'):
                for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games'):
                    self.assertEqual(got['rates'][b][k], want['rates'][b][k], (first, b, k))
            self.assertIsNone(got['pass'])

    def test_every_game_the_same_difference_collapses_the_interval(self):
        rc_, ec, _, _ = self.make_run('synC', SAME_C, [301, 302, 303])
        rd, ed, _, _ = self.make_run('synD', SAME_D, [401, 402, 403])
        r, res = pool('--run', rc_, ec, '--run', rd, ed)
        self.assertEqual(r.returncode, 0, r.stderr)
        c = res['primary']['contrast']
        # every game of both runs: difference sum 2/3 over 2 points, so every bootstrap draw of k games is (k * 2/3) / (2k) = 1/3, and so is the point:
        # 12 games * 2/3 / 24 points = 1/3. The interval must be the point.
        self.assertEqual((c['estimate'], c['ci_low'], c['ci_high'], c['n_decisions'], c['n_games']), (0.333333, 0.333333, 0.333333, 24, 12))
        # exact sign-flip over 12 equal game sums: only all-plus and all-minus reach |12 * 2/3|: 2 / 2^12 = 0.00048828
        self.assertEqual((c['sign_flip_p'], c['sign_flip']), (0.000488, 'exact'))
        # 12 games >= 10, the interval excludes 0, p < 0.025: a direction, and at 0.975 a PASS
        self.assertEqual((c['verdict'], c['reason']), ('judge higher', 'the interval excludes 0 and the sign-flip test agrees (every game gave the same difference)'))
        self.assertIs(res['primary']['pass'], True)
        # the rates differ between the runs' games (judge 1 of 2 in run C's, 2 of 2 in run D's), so only the difference collapses:
        # judge (5 * 1 + 7 * 2) / 24 = 19/24 = 0.7916667; km3 (5 * 1/3 + 7 * 4/3) / 24 = 11/24 = 0.4583333; 19/24 - 11/24 = 8/24 = 1/3
        j, k = res['primary']['rates']['judge'], res['primary']['rates']['km3']
        self.assertEqual((j['estimate'], k['estimate']), (0.791667, 0.458333))
        self.assertLess(j['ci_low'], j['ci_high'])
        self.assertLess(k['ci_low'], k['ci_high'])
        # each run alone: 5 and 7 equal game sums, 2 / 2^5 = 0.0625 and 2 / 2^7 = 0.015625; no failed replies
        self.assertEqual([x['alone_at_0.95_equals_its_report']['sign_flip_p'] for x in res['per_run']], [0.0625, 0.015625])
        self.assertEqual(res['primary']['failed_replies'], {'n': 0, 'share': 0.0, 'over_20pct': False})

    def test_the_same_game_in_both_runs_is_refused(self):
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        for name, game in (('synB_same', 'SYN-A-g1'), ('synB_case', 'syn-a-g1')):
            # run B's first game renamed to run A's first game (exactly, then in other letter case); run B's point ids and seeds stay its own
            pts = [(p, game if g == 'SYN-B-g1' else g, j, k) for p, g, j, k in RUN_B]
            rb, eb, _, _ = self.make_run(name, pts, SEEDS_B)
            self.refused('--run', ra, ea, '--run', rb, eb, why=f'game {game} appears in runs synA (#1) and {name} (#2): the runs must be different games')

    def test_the_same_point_in_both_runs_is_refused(self):
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        pts = [('SYN-A-g1-t1' if p == 'SYN-B-g1-t1' else p, g, j, k) for p, g, j, k in RUN_B]  # run B's own game, but one of run A's point ids
        rb, eb, _, _ = self.make_run('synB', pts, SEEDS_B)
        self.refused('--run', ra, ea, '--run', rb, eb, why='point SYN-A-g1-t1 appears in two runs')

    def test_a_km3_seed_shared_by_the_two_runs_is_refused(self):
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        rb, eb, _, _ = self.make_run('synB', RUN_B, [201, 202, 103])
        self.refused('--run', ra, ea, '--run', rb, eb, why='km3 seed 103 appears in two runs (synA (#1) and synB (#2))')

    def test_a_judge_model_mismatch_between_the_runs_turns_pooling_off(self):
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        for name, fn, models in (('synB_model', lambda rep: rep['run'].update(judge_models_returned=['gemini-4-argon-002']), ['gemini-4-argon', 'gemini-4-argon-002']),
                                 ('synB_nomodel', lambda rep: rep['run'].pop('judge_models_returned'), [None, 'gemini-4-argon']),
                                 ('synB_warn', lambda rep: rep['run'].update(warnings=['the judge model version changed during the run']), ['gemini-4-argon'])):
            rb, eb, _, _ = self.make_run(name, RUN_B, SEEDS_B, tamper=fn)
            r, res = pool('--run', ra, ea, '--run', rb, eb)
            self.assertEqual(r.returncode, 3, (name, r.stderr))
            self.assertTrue(res['pooling'].startswith('OFF'), name)
            self.assertEqual(res['judge_models'], models, name)
            self.assertNotIn('primary', res)
            self.assertNotIn('per_run', res)
            if name == 'synB_warn':
                self.assertEqual(res['model_warnings'], ['synB_warn (#2): the judge model version changed during the run'])

    def test_the_second_run_is_checked_like_the_first(self):
        ra, ea, _, _ = self.make_run('synA', RUN_A, SEEDS_A)
        for name, fn, why in (('synB_tag', lambda rep: rep['run']['freeze'].update(tag='judge-prompt-frozen-6'), 'not made under judge-prompt-frozen-7'),
                              ('synB_own', lambda rep: rep['analysis']['prefix']['contrasts'][0].update(estimate=0.5),
                               "synB_own (#2): alone at 0.95 this script does not give the report's own numbers (estimate)"),
                              ('synB_failed', lambda rep: rep['failed_judge_rows'].update(n_primary_decisions=0),
                               'synB_failed (#2): 1 failed primary judge replies in the rows, the report says 0')):
            rb, eb, _, _ = self.make_run(name, RUN_B, SEEDS_B, tamper=fn)
            self.assertIn(f'{name} (#2)', self.refused('--run', ra, ea, '--run', rb, eb, why=why))
        rb, eb, _, _ = self.make_run('synB', RUN_B, SEEDS_B)
        self.refused('--run', ra, ea, '--run', rb, ea, why='is not the eligibility file the report was made from')  # run A's eligibility given for run B


if __name__ == '__main__':
    if not ANALYSIS:
        sys.exit('usage: test_pool_runs.py PATH/TO/frozen-7/analysis.py')
    unittest.main()
