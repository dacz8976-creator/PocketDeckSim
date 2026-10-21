#!/usr/bin/env python3
"""The pooling script's reproduction test (PREREG_RUN3 section 4): on run 2 alone at 95% it must give run 2's report_primary.json prefix contrast and
rates to the printed digits; and its refusals hold. usage (from the exam folder): python3 run3/test_pool_runs.py ANALYSIS_PY"""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile, unittest

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


if __name__ == '__main__':
    if not ANALYSIS:
        sys.exit('usage: test_pool_runs.py PATH/TO/frozen-7/analysis.py')
    unittest.main()
