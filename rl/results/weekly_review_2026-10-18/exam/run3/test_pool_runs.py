#!/usr/bin/env python3
"""The pooling script's reproduction test (PREREG_RUN3 section 4): on run 2 alone at 95% it must give run 2's report_primary.json prefix contrast and
rates to the printed digits; and its refusals hold. usage (from the exam folder): python3 run3/test_pool_runs.py ANALYSIS_PY"""
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXAM = os.path.dirname(HERE)
RUN2 = os.path.join(EXAM, 'run2', 'live-20261021T2000Z')
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


class Reproduces(unittest.TestCase):
    def test_run2_alone_at_95_equals_its_report(self):
        r, res = pool('--run', os.path.join(RUN2, 'report_primary.json'), os.path.join(RUN2, 'in', 'eligibility.json'), '--confidence', '0.95',
                      '--judge-rows', os.path.join(RUN2, 'judge_primary.jsonl'), os.path.join(RUN2, 'judge_primary_resend.jsonl'))
        self.assertEqual(r.returncode, 0, r.stderr)
        rep = json.load(open(os.path.join(RUN2, 'report_primary.json')))
        want = rep['analysis']['prefix']['contrasts'][0]
        got = res['primary']['contrast']
        for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games', 'sign_flip_p', 'sign_flip', 'verdict'):
            self.assertEqual(got[k], want[k], k)
        self.assertEqual((got['estimate'], got['ci_low'], got['ci_high'], got['sign_flip_p']), (0.163265, -0.014184, 0.346939, 0.108869))
        for b in ('km3', 'judge'):
            w = rep['analysis']['prefix']['rates'][b]
            for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games'):
                self.assertEqual(res['primary']['rates'][b][k], w[k], (b, k))
        self.assertEqual(res['judge_models'], {'gemini-4-argon': 51})

    def test_the_975_interval_is_wider(self):
        r, res = pool('--run', os.path.join(RUN2, 'report_primary.json'), os.path.join(RUN2, 'in', 'eligibility.json'))
        self.assertEqual(r.returncode, 0, r.stderr)
        c = res['primary']['contrast']
        self.assertEqual(res['confidence'], 0.975)
        self.assertLess(c['ci_low'], -0.014184)
        self.assertGreater(c['ci_high'], 0.346939)
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertFalse(res['primary']['pass'])

    def test_another_analysis_is_refused(self):
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as t, open(ANALYSIS) as src:
            t.write(src.read() + '\n# changed\n')
            bad = t.name
        r = subprocess.run([sys.executable, os.path.join(HERE, 'pool_runs.py'), '--analysis', bad, '--run', os.path.join(RUN2, 'report_primary.json'),
                            os.path.join(RUN2, 'in', 'eligibility.json'), '--out', os.devnull], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('refused', r.stdout + r.stderr)

    def test_the_same_run_twice_is_refused(self):
        rp, el = os.path.join(RUN2, 'report_primary.json'), os.path.join(RUN2, 'in', 'eligibility.json')
        r, _ = pool('--run', rp, el, '--run', rp, el)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('appears in two runs', r.stdout + r.stderr)

    def test_two_models_turn_pooling_off(self):
        rows = os.path.join(RUN2, 'judge_primary.jsonl')
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as t:
            other = t.name
        with open(rows) as f, open(other, 'w') as g:
            line = json.loads(f.readline())
            line['model_returned'] = 'gemini-4-argon-002'
            g.write(json.dumps(line) + '\n')
        r, res = pool('--run', os.path.join(RUN2, 'report_primary.json'), os.path.join(RUN2, 'in', 'eligibility.json'), '--judge-rows', rows, other)
        self.assertEqual(r.returncode, 3)
        self.assertIn('OFF', res['pooling'])
        self.assertNotIn('primary', res)


if __name__ == '__main__':
    if not ANALYSIS:
        sys.exit('usage: test_pool_runs.py PATH/TO/frozen-7/analysis.py')
    unittest.main()
