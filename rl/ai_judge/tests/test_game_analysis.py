import contextlib
import io
import itertools
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
import game_analysis as ga  # noqa: E402
import game_kit  # noqa: E402

TMP = os.environ['TMPDIR']


def deal(k, cell, D, **kw):
    g, kk = (1, 0) if D == 1 else (0, 1) if D == -1 else (0, 0)
    d = {'deal_idx': 16 * k + cell, 'k': k, 'cell': cell, 'g_win': g, 'k_win': kk, 'g_failure': None, 'k_failure': None, 'g_interventions': 20, 'g_fallbacks': 0}
    d.update(kw)
    return d


def run_cli(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ga.main(argv)
    return rc, buf.getvalue().splitlines()


def fresh(name):
    d = os.path.join(TMP, 'ga_' + name)
    subprocess.run(['rm', '-rf', d])
    os.makedirs(d)
    return d


def exact_p(n_nonzero, obs_sum):
    hits = sum(math.comb(n_nonzero, x) for x in range(n_nonzero + 1) if abs(2 * x - n_nonzero) >= abs(obs_sum))
    return hits / 2 ** n_nonzero


class Analysis(unittest.TestCase):
    def sets(self):
        return ga.self_test_sets()

    def label_of(self, name):
        deals, planned, stopped, expect = self.sets()[name]
        r = ga.analyse(deals, planned, stopped)
        self.assertEqual(r['label'], expect, name)
        return r

    def test_Y1_all_plus(self):
        r = self.label_of('Y1')
        self.assertEqual(r['label'], 'PASS / judge higher')

    def test_Y2_all_zero(self):
        self.label_of('Y2')

    def test_Y3_all_minus(self):
        self.label_of('Y3')

    def test_Y4_one_policy_not_positive(self):
        r = self.label_of('Y4')
        self.assertGreater(r['mean_d'], 0)
        self.assertEqual(r['policy_means']['kx3'], 0)
        self.assertEqual(r['policy_means']['km3'], 1)

    def test_Y5_drop_limit(self):
        r = self.label_of('Y5a')
        self.assertEqual(r['dropped'], 5)
        self.assertEqual(r['dropped_by'], {'G:engine_error': 3, 'K:kx3_route': 2})
        r = self.sets()['Y5b']
        r = ga.analyse(r[0], r[1], r[2])
        self.assertEqual(r['dropped'], 4)
        self.assertEqual(r['label'], 'PASS / judge higher')

    def test_Y6_fallback_rate(self):
        r = self.label_of('Y6')
        self.assertAlmostEqual(r['fallback_rate'], 0.11)

    def test_Y7_too_few_and_early_stop(self):
        self.label_of('Y7a')
        self.label_of('Y7b')

    def test_Y8_bootstrap_keeps_cell_counts(self):
        cv = {0: [1, 0, -1], 1: [1], 5: [0, 0, 1, 1, 1]}
        rng = random.Random(1)
        for _ in range(50):
            out = ga.resample(rng, cv)
            self.assertEqual([len(x) for x in out], [3, 1, 5])
            for got, src in zip(out, [cv[0], cv[1], cv[5]]):
                self.assertTrue(set(got) <= set(src))

    def test_Y9_mc_p_matches_exact(self):
        rng = random.Random(5)
        for _ in range(3):
            D = [rng.choice([-1, 0, 1, 1]) for _ in range(12)]
            obs = sum(D)
            n = len(D)
            hits = 0
            for bits in itertools.product((1, -1), repeat=n):
                if abs(sum(s * d for s, d in zip(bits, D))) >= abs(obs):
                    hits += 1
            exact = hits / 2 ** n
            self.assertAlmostEqual(ga.signflip_p(D, 100000, 20261031), exact, delta=0.01)

    def test_Y10_deterministic(self):
        deals, planned, stopped, _ = self.sets()['Y15']
        a = json.dumps(ga.analyse(deals, planned, stopped), sort_keys=True)
        b = json.dumps(ga.analyse(deals, planned, stopped), sort_keys=True)
        self.assertEqual(a, b)

    def test_Y11_power_line(self):
        for n, rough, exact in ((80, 0.22, 0.22148), (96, 0.20, 0.20219), (128, 0.175, 0.17510)):
            self.assertAlmostEqual(ga.power_line(n), rough, delta=0.0025)
            self.assertAlmostEqual(ga.power_line(n), exact, delta=0.0001)

    def test_Y12_label_order(self):
        self.label_of('Y12')

    def _stage2_dir(self, name, stage=2, k2=0, mock=False):
        d = fresh(name)
        os.makedirs(os.path.join(d, 'res'))
        with open(os.path.join(d, 'run_end.json'), 'w') as f:
            json.dump({'stage': stage, 'planned_deals': 2, 'complete_deals': 2, 'stopped_early': False, 'stop_reason': None, 'finished_utc': 'x', 'model_returned': 'm'}, f)
        outcomes = {'G0': {'Win': 0}, 'K0': 'Tie', 'G1': {'Win': 1}, 'K1': 'Tie'}
        finals = {'K1': 31}
        deals, games = [], []
        for idx, cell in enumerate((0, 1)):
            bits = game_kit.cell_bits(cell)
            tags = {}
            for arm in ('G', 'K'):
                tag = '%04d-k%d-c%02d-a1-%s' % (idx, k2, cell, arm)
                tags[arm] = tag
                rf = 'res/%s.json' % tag
                with open(os.path.join(d, rf), 'w') as f:
                    json.dump({'schema': 'pdl-game-result/v1', 'outcome': outcomes[arm + str(idx)], 'completion': 'completed', 'final_turn': finals.get(arm + str(idx), 12), 'lifecycle_errors': []}, f)
                with open(os.path.join(d, rf), 'rb') as f:
                    sha = hashlib.sha256(f.read()).hexdigest()
                row = {'deal_tag': tag, 'arm': arm, 'bits': bits, 'cell': cell, 'k': k2, 'result_file': rf, 'result_sha256': sha, 'failure': None, 'seconds': 10.0}
                if arm == 'G':
                    row['judge'] = {'decisions': 30, 'setup_decisions': 5, 'interventions': 20, 'fallbacks': 1, 'fallbacks_by_reason': {'a': 1}, 'reasks_by_reason': {'first': 1},
                                    'calls': 19, 'tries': 20, 'ledger_charge_usd': 0.5, 'actual_usd': 0.4, 'mock': mock, 'went_first': 0}
                games.append(row)
            deals.append({'stage': 2, 'deal_idx': idx, 'k': k2, 'cell': cell, 'bits': bits, 'seed': 1, 'attempt': 1, 'complete': True, 'g_deal_tag': tags['G'], 'k_deal_tag': tags['K'],
                          'g_failure': None, 'k_failure': None, 'dropped': False, 'drop_reason': None})
        for name_, rows in (('deals.jsonl', deals), ('games.jsonl', games)):
            with open(os.path.join(d, name_), 'w') as f:
                for r in rows:
                    f.write(json.dumps(r) + '\n')
        return d

    def test_Y13_refusals_and_run(self):
        d = fresh('y13_none')
        rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
        self.assertEqual(rc, 2)
        self.assertTrue(out[-1].startswith('REFUSED'))
        for stage in (1, 'dev'):
            d = self._stage2_dir('y13_s%s' % stage, stage=stage)
            rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
            self.assertEqual((rc, out[-1].startswith('REFUSED')), (2, True), out)
        d = self._stage2_dir('y13_k8', k2=8)
        rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
        self.assertEqual((rc, out[-1].startswith('REFUSED')), (2, True), out)
        d = self._stage2_dir('y13_mock', mock=True)
        rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
        self.assertEqual((rc, out[-1].startswith('REFUSED')), (2, True), out)
        d = self._stage2_dir('y13_ok')
        rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
        self.assertEqual(rc, 0, out)
        self.assertTrue(out[-1].startswith('LABEL: '))
        self.assertTrue(os.path.exists(os.path.join(d, 'a.json')))

    def _append(self, d, name, rows):
        with open(os.path.join(d, name), 'a') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    def test_Y13b_result_file_checks(self):
        def refused(d):
            rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
            self.assertEqual((rc, out[-1].startswith('REFUSED')), (2, True), out)
        d = self._stage2_dir('y13b_missing')
        os.remove(os.path.join(d, 'res', '0000-k0-c00-a1-G.json'))
        refused(d)
        d = self._stage2_dir('y13b_changed')
        with open(os.path.join(d, 'res', '0001-k0-c01-a1-K.json'), 'ab') as f:
            f.write(b' ')
        refused(d)
        d = self._stage2_dir('y13b_nullfile')
        rows = [json.loads(l) for l in open(os.path.join(d, 'games.jsonl'))]
        rows[1]['result_file'] = None
        with open(os.path.join(d, 'games.jsonl'), 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        refused(d)
        d = self._stage2_dir('y13b_superseded_k8')
        self._append(d, 'deals.jsonl', [{'stage': 2, 'deal_idx': 0, 'k': 8, 'cell': 0, 'attempt': 0, 'complete': False, 'g_deal_tag': None, 'k_deal_tag': None}])
        refused(d)
        d = self._stage2_dir('y13b_stray_mock')
        self._append(d, 'games.jsonl', [{'deal_tag': 'zz-a1-G', 'arm': 'G', 'judge': {'mock': True}, 'failure': 'infra'}])
        refused(d)
        # an infra attempt then a clean one, and a stop:* arm row, none with a result file and none named by a row of record: no refusal
        d = self._stage2_dir('y13b_infra_ok')
        self._append(d, 'games.jsonl', [{'deal_tag': '0000-k0-c00-a0-G', 'arm': 'G', 'bits': game_kit.cell_bits(0), 'result_file': None, 'failure': 'infra', 'judge': {'mock': False}},
                                        {'deal_tag': '0001-k0-c01-a0-G', 'arm': 'G', 'bits': game_kit.cell_bits(1), 'result_file': None, 'failure': 'stop:ledger'}])
        self._append(d, 'deals.jsonl', [{'stage': 2, 'deal_idx': 0, 'k': 0, 'cell': 0, 'attempt': 0, 'complete': False, 'g_deal_tag': '0000-k0-c00-a0-G', 'k_deal_tag': None}])
        deals, planned, stopped = ga.read_run_dir(d)
        self.assertEqual([x['g_win'] for x in deals], [1, 1])
        rc, out = run_cli(['--run-dir', d, '--out', os.path.join(d, 'a.json')])
        self.assertEqual(rc, 0, out)

    def test_Y14_pilot_side_is_loss(self):
        deals, planned, stopped, expect = self.sets()['Y14']
        r = ga.analyse(deals, planned, stopped)
        self.assertEqual(r['mean_d'], 0)
        self.assertEqual(r['label'], expect)
        one = ga.analyse([deal(0, 0, 1, g_failure='pilot_side')], 1, False)
        self.assertEqual(one['mean_d'], 0)

    def test_Y15_F_plus(self):
        deals, planned, stopped, _ = self.sets()['Y15']
        r = ga.analyse(deals, planned, stopped)
        self.assertEqual(r['mean_d'], 0.3)
        self.assertAlmostEqual(r['policy_means']['km3'], 0.3)
        self.assertAlmostEqual(r['policy_means']['kx3'], 0.3)
        exact = exact_p(56, 24)
        self.assertAlmostEqual(exact, 0.0018, delta=0.0002)
        self.assertAlmostEqual(r['p'], exact, delta=0.001)
        self.assertTrue(0.10 <= r['ci'][0] <= 0.20, r['ci'])
        self.assertTrue(0.40 <= r['ci'][1] <= 0.50, r['ci'])
        self.assertEqual(r['label'], 'PASS / judge higher')

    def test_Y16_F_null(self):
        deals, planned, stopped, _ = self.sets()['Y16']
        r = ga.analyse(deals, planned, stopped)
        self.assertEqual(r['mean_d'], 0)
        self.assertEqual(r['p'], 1.0)
        self.assertTrue(r['ci'][0] < 0 < r['ci'][1], r['ci'])
        self.assertEqual(r['label'], 'inconclusive')

    def test_Y17_F_minus(self):
        deals, planned, stopped, _ = self.sets()['Y17']
        r = ga.analyse(deals, planned, stopped)
        p_plus = ga.analyse(*self.sets()['Y15'][:3])['p']
        self.assertAlmostEqual(r['mean_d'], -0.3)
        self.assertEqual(r['p'], p_plus)
        self.assertEqual(r['label'], 'kx3 higher')

    def test_Y18_setup_outside_rate(self):
        deals, planned, stopped, _ = self.sets()['Y18']
        self.assertTrue(all(d.get('setup_decisions') == 5 for d in deals))
        r = ga.analyse(deals, planned, stopped)
        self.assertAlmostEqual(r['fallback_rate'], 0.09)
        self.assertNotEqual(r['label'], 'pilot not tested')

    def test_Y19_run_dir_mapping(self):
        d = self._stage2_dir('y19')
        deals, planned, stopped = ga.read_run_dir(d)
        self.assertEqual([x['g_win'] for x in deals], [1, 1])
        self.assertEqual([x['k_win'] for x in deals], [0, 0])
        self.assertEqual((planned, stopped), (2, False))
        self.assertEqual([x['g_interventions'] for x in deals], [20, 20])
        self.assertEqual([x['g_fallbacks'] for x in deals], [1, 1])
        self.assertEqual([x['went_first'] for x in deals], [1, 0])
        bwf = ga.analyse(deals, planned, stopped)['descriptive']['by_went_first']
        self.assertEqual(sorted(bwf), ['0', '1'])
        self.assertEqual((bwf['0']['n'], bwf['1']['n']), (1, 1))
        for outcome, seat, want in (({'Win': 0}, 0, 1), ({'Win': 1}, 0, 0), ({'Win': 1}, 1, 1), ({'Win': 0}, 1, 0), ('Tie', 0, 0), ('Tie', 1, 0)):
            self.assertEqual(ga.win_for(outcome, seat), want)

    def test_selftest_cli(self):
        rc, out = run_cli(['--self-test'])
        self.assertEqual(out[-1], 'GATE6 PASS')
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
