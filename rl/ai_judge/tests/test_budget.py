#!/usr/bin/env python3
"""budget_judge.py: the hard spend bound around the judge's API calls (reservations at the conservative price, settlement at the price in force, failed calls charged in full,
the ledger shared by the primary and the repeat run). Mocks only: no key is read, nothing is sent.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests
"""
import contextlib, io, json, os, sys, tempfile, threading, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import budget_judge as bj, judge, providers  # noqa: E402
from test_gemini import PID, fake_rec, interaction  # noqa: E402

SYS, USER = 'S' * 1000, 'U' * 9000
INTRO = (2.0, 10.0)


def tmp():
    return tempfile.mkdtemp()


class WorstCase(unittest.TestCase):
    def test_gemini_is_reserved_at_the_higher_price_whatever_the_date(self):
        w = bj.worst_case_usd(SYS, USER, 'gemini', 'gemini-4-argon', 8000)
        self.assertAlmostEqual(w, (10000 + bj.OVERHEAD_TOKENS) * 4 / 1e6 + 8000 * 20 / 1e6)
        with mock.patch.object(providers, 'gemini_price', return_value=INTRO):  # the price in force does not change the reservation
            self.assertAlmostEqual(bj.worst_case_usd(SYS, USER, 'gemini', 'gemini-4-argon', 8000), w)

    def test_anthropic_is_reserved_at_the_assumed_list_price(self):
        self.assertAlmostEqual(bj.worst_case_usd(SYS, USER, 'anthropic', judge.MODEL, 8000), (10000 + bj.OVERHEAD_TOKENS) * 3 / 1e6 + 8000 * 15 / 1e6)

    def test_the_bytes_not_the_characters_bound_the_input(self):
        w1 = bj.worst_case_usd('é' * 1000, '', 'gemini', 'm', 0)
        self.assertAlmostEqual(w1, (2000 + bj.OVERHEAD_TOKENS) * 4 / 1e6)

    def test_the_worst_case_is_never_below_the_actual_cost_of_any_possible_reply(self):
        w = bj.worst_case_usd(SYS, USER, 'gemini', 'm', 8000)
        for price in (INTRO, (4.0, 20.0)):
            with mock.patch.object(providers, 'gemini_price', return_value=price):
                out = ('', {'input_tokens': 10000, 'output_tokens': 8000}, 0, 'm', {'usage_missing': False})
                self.assertLessEqual(bj.actual_usd('gemini', out, w), w + 1e-12)


class ActualCost(unittest.TestCase):
    def test_gemini_is_settled_at_the_price_in_force(self):
        out = ('', {'input_tokens': 10000, 'output_tokens': 2000}, 0, 'm', {'usage_missing': False})
        with mock.patch.object(providers, 'gemini_price', return_value=INTRO):
            self.assertAlmostEqual(bj.actual_usd('gemini', out, 1.0), 10000 * 2 / 1e6 + 2000 * 10 / 1e6)
        with mock.patch.object(providers, 'gemini_price', return_value=(4.0, 20.0)):
            self.assertAlmostEqual(bj.actual_usd('gemini', out, 1.0), 10000 * 4 / 1e6 + 2000 * 20 / 1e6)

    def test_a_reply_without_usage_is_charged_the_whole_worst_case(self):
        self.assertEqual(bj.actual_usd('gemini', ('', {'input_tokens': None, 'output_tokens': 0}, 0, 'm', {'usage_missing': True}), 0.2), 0.2)
        self.assertEqual(bj.actual_usd('gemini', ('', {'input_tokens': 5, 'output_tokens': 0}, 0, 'm', {'usage_missing': True}), 0.2), 0.2)


class LedgerTests(unittest.TestCase):
    def ledger(self, total=1.0, cap=None, label='gemini:gemini-4-argon', d=None):
        d = d or tmp()
        return bj.Ledger(os.path.join(d, 'l.json'), total, cap, label), d

    def test_a_call_is_sent_only_if_accrued_plus_reserved_plus_its_worst_case_fits(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.4))
        self.assertTrue(led.reserve(0.4))
        self.assertFalse(led.reserve(0.4))  # 0.8 reserved + 0.4 > 1.0
        led.settle(0.4, 0.05)
        self.assertTrue(led.reserve(0.4))  # 0.05 accrued + 0.4 reserved + 0.4 = 0.85
        self.assertEqual(led.refused, 1)
        led.close()

    def test_the_run_cap_binds_separately_from_the_total(self):
        led, _ = self.ledger(10.0, 0.5)
        self.assertTrue(led.reserve(0.3))
        self.assertFalse(led.reserve(0.3))
        led.close()

    def test_the_total_is_shared_by_the_primary_and_the_repeat_run(self):
        d = tmp()
        a = bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')
        self.assertTrue(a.reserve(0.3))
        a.settle(0.3, 0.3)
        a.close()
        b = bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')  # the repeat run continues from the file
        self.assertAlmostEqual(b.accrued, 0.3)
        self.assertTrue(b.reserve(0.7))
        self.assertFalse(b.reserve(0.01 + 0.0))  # 0.3 + 0.7 reserved + 0.01 > 1.0
        b.close()

    def test_a_different_total_or_label_is_refused_and_the_lock_is_released(self):
        d = tmp()
        bj.Ledger(os.path.join(d, 'l.json'), 15.0, 8.0, 'gemini:m').close()
        with self.assertRaises(SystemExit):
            bj.Ledger(os.path.join(d, 'l.json'), 10.0, 8.0, 'gemini:m')
        with self.assertRaises(SystemExit):
            bj.Ledger(os.path.join(d, 'l.json'), 15.0, 8.0, 'anthropic:claude')
        self.assertFalse(os.path.exists(os.path.join(d, 'l.json.lock')))
        bj.Ledger(os.path.join(d, 'l.json'), 15.0, 8.0, 'gemini:m').close()  # still opens

    def test_two_runs_cannot_hold_one_ledger(self):
        led, d = self.ledger()
        with self.assertRaises(SystemExit):
            bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')
        led.close()

    def test_a_failed_call_is_charged_in_full_and_stops_everything_after_it(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.2))
        led.charge_failed(0.2)
        self.assertAlmostEqual(led.accrued, 0.2)
        self.assertFalse(led.reserve(0.01))
        self.assertIn('failed', led.halted)
        led.close()

    def test_a_call_that_costs_more_than_its_reservation_halts_further_calls(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.1))
        with contextlib.redirect_stderr(io.StringIO()):
            led.settle(0.1, 0.2)
        self.assertAlmostEqual(led.accrued, 0.2)  # still counted
        self.assertFalse(led.reserve(0.01))
        led.close()

    def test_the_file_holds_the_accrued_total_and_the_label(self):
        led, d = self.ledger(15.0, 8.0)
        led.reserve(0.1)
        led.settle(0.1, 0.07)
        with open(os.path.join(d, 'l.json')) as f:
            data = json.load(f)
        self.assertEqual((data['total_usd'], data['accrued_usd'], data['label']), (15.0, 0.07, 'gemini:gemini-4-argon'))
        led.close()

    def test_under_concurrency_accrued_plus_reserved_never_passes_the_total(self):
        led, _ = self.ledger(1.0)
        sent = []

        def call():
            if led.reserve(0.12):
                sent.append(1)
                led.settle(0.12, 0.1)
        ts = [threading.Thread(target=call) for _ in range(40)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        self.assertLessEqual(led.peak, 1.0 + 1e-9)
        self.assertLessEqual(led.accrued, 1.0 + 1e-9)
        self.assertGreater(len(sent), 0)
        self.assertEqual(led.reserved, 0)
        led.close()


class Gate(unittest.TestCase):
    """install_gate around a fake call: the real network function is never reached."""

    def setUp(self):
        for obj, name in ((providers, 'call_gemini'), (judge, 'call_claude'), (providers, 'load_key'), (judge, 'load_key')):
            p = mock.patch.object(obj, name, getattr(obj, name))  # patched with itself: the gate's replacement is undone on cleanup
            p.start()
            self.addCleanup(p.stop)
        self.led = bj.Ledger(os.path.join(tmp(), 'l.json'), 1.0, 1.0, 'x')
        self.addCleanup(self.led.close)

    def gemini_call(self, tin=10000, tout=2000, usage_missing=False, status='completed'):
        def call(system, user, model=None, max_tokens=8000, temperature=None, thinking=None, timeout=300):
            self.sent = getattr(self, 'sent', 0) + 1
            usage = {'input_tokens': None if usage_missing else tin, 'output_tokens': tout}
            return 'PLAN: 1', usage, 0.0, model, {'stop_reason': 'end_turn', 'usage_missing': usage_missing}
        return call

    def test_a_call_reserves_then_settles_at_its_actual_cost(self):
        bj.install_gate(self.led, self.gemini_call(), 'gemini')
        with mock.patch.object(providers, 'gemini_price', return_value=INTRO):
            out = providers.call_gemini(SYS, USER, 'gemini-4-argon', max_tokens=8000, temperature=None, thinking={'thinking_level': 'high', 'thinking_summaries': 'none'})
        self.assertEqual(out[0], 'PLAN: 1')
        self.assertAlmostEqual(self.led.accrued, 10000 * 2 / 1e6 + 2000 * 10 / 1e6)
        self.assertEqual((self.led.reserved, self.led.calls), (0, 1))

    def test_a_call_that_would_pass_the_bound_is_not_sent(self):
        self.led.total = 0.1
        bj.install_gate(self.led, self.gemini_call(), 'gemini')
        with self.assertRaises(bj.BudgetRefused):
            providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})
        self.assertFalse(hasattr(self, 'sent'))
        self.assertEqual(self.led.accrued, 0)

    def test_a_failing_call_is_charged_in_full_and_the_next_is_refused(self):
        def boom(*a, **k):
            raise SystemExit('API error 500')
        bj.install_gate(self.led, boom, 'gemini')
        w = bj.worst_case_usd(SYS, USER, 'gemini', 'm', 8000)
        with self.assertRaises(SystemExit):
            providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})
        self.assertAlmostEqual(self.led.accrued, w)
        with self.assertRaises(bj.BudgetRefused):
            providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})

    def test_a_reply_without_usage_is_charged_its_worst_case(self):
        bj.install_gate(self.led, self.gemini_call(usage_missing=True), 'gemini')
        providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})
        self.assertAlmostEqual(self.led.accrued, bj.worst_case_usd(SYS, USER, 'gemini', 'm', 8000))
        self.assertIsNone(self.led.halted)  # exactly its worst case is not "above" it

    def test_the_anthropic_gate_patches_the_anthropic_call_only(self):
        gemini_before = providers.call_gemini

        def claude(system, user, model, max_tokens, temperature, timeout=300):
            return 't', {'input_tokens': 1000, 'output_tokens': 100}, 0.0, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']}
        bj.install_gate(self.led, claude, 'anthropic')
        self.assertIs(providers.call_gemini, gemini_before)
        judge.call_claude(SYS, USER, judge.MODEL, max_tokens=8000, temperature=None)
        self.assertAlmostEqual(self.led.accrued, 1000 * 3 / 1e6 + 100 * 15 / 1e6)


class Wrapper(unittest.TestCase):
    """budget_judge.main end to end with --mock (the plan lister is replaced by a fake plan list; the positions and decks are the real ones)."""

    def setUp(self):
        for obj, name in ((providers, 'call_gemini'), (judge, 'call_claude'), (providers, 'load_key'), (judge, 'load_key')):
            p = mock.patch.object(obj, name, getattr(obj, name))
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(judge, 'list_plans', side_effect=lambda ids, *a, **k: {i: fake_rec() for i in ids})
        p.start()
        self.addCleanup(p.stop)
        self.d = tmp()

    def argv(self, *extra, total='15', cap='8', mode='--mock', out='rows.jsonl', ledger='ledger.json', repeat='1'):
        return ['--positions', judge.DEFAULT_POSITIONS, '--decks', judge.DEFAULT_DECKS, '--ids', PID, '--max-calls', '3', '--repeat', repeat, '--workers', '1', '--tag', 'T',
                '--out', os.path.join(self.d, out), '--ledger', os.path.join(self.d, ledger), '--total-usd', total, '--run-cap-usd', cap, mode, *extra]

    def run_main(self, argv):
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = bj.main(argv)
        return code, err.getvalue()

    def rows(self, out='rows.jsonl'):
        with open(os.path.join(self.d, out)) as f:
            return [json.loads(l) for l in f if l.strip()]

    def test_a_mock_run_writes_frozen_gemini_rows_with_repeat_and_tag_and_reads_no_key(self):
        code, err = self.run_main(self.argv(repeat='3'))
        self.assertEqual(code, 0, err)
        rows = self.rows()
        self.assertEqual([r['repeat'] for r in rows], [0, 1, 2])
        for r in rows:
            self.assertEqual((r['tag'], r['provider'], r['model'], r['thinking_level'], r['frozen'], r['bot']), ('T', 'gemini', 'gemini-4-argon', 'high', True, 'judge'))
            self.assertIsNotNone(r['plan_number'])
        with open(os.path.join(self.d, 'ledger.json')) as f:
            led = json.load(f)
        self.assertEqual((led['total_usd'], led['label']), (15.0, 'gemini:gemini-4-argon'))
        self.assertAlmostEqual(led['accrued_usd'], sum(r['cost']['usd'] for r in rows), places=4)  # each row's cost is rounded to 5 places, the ledger's total to 6
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))
        with self.assertRaises(SystemExit):
            providers.load_key()  # the mock replaced the key readers: a key was never read

    def test_the_wrapper_makes_the_rows_judge_one_makes(self):
        self.run_main(self.argv())
        row = self.rows()[0]
        with mock.patch.object(providers, 'call_gemini', bj.mock_call('gemini')):
            own, _, _ = judge.judge_one(PID, judge.load_positions(), {PID: fake_rec()}, judge.FROZEN['order'], True, 'gemini-4-argon', None, judge.DEFAULT_DECKS,
                                        judge.FROZEN['compact_above'], 8000, 'v1', False, 'gemini', 'high')
        for r in (row, own):
            r.pop('repeat', None), r.pop('tag', None), r.pop('seconds')
        self.assertEqual(row, own)

    def test_the_run_cap_stops_calls_and_the_batch_is_incomplete(self):
        code, err = self.run_main(self.argv(cap='0.05'))
        self.assertEqual(code, 2)
        self.assertIn('NOT SENT', err)
        self.assertEqual(self.rows(), [])

    def test_the_second_run_continues_the_ledger_and_the_total_holds_across_runs(self):
        w = bj.worst_case_usd(*self._prompt(), 'gemini', 'gemini-4-argon', 8000)
        total = f'{w * 2.5:.6f}'  # room for two reservations but not three
        code, _ = self.run_main(self.argv(total=total, cap=total))
        self.assertEqual(code, 0)
        code, err = self.run_main(self.argv(total=total, cap=total, out='rows2.jsonl'))
        self.assertIn('ledger $', err)
        with open(os.path.join(self.d, 'ledger.json')) as f:
            self.assertGreater(json.load(f)['accrued_usd'], 0.01)  # the second run began with the first's accrual
        total_spent = sum(r['cost']['usd'] for r in self.rows()) + (sum(r['cost']['usd'] for r in self.rows('rows2.jsonl')) if os.path.exists(os.path.join(self.d, 'rows2.jsonl')) else 0)
        self.assertLessEqual(total_spent, float(total))

    def _prompt(self):
        system, user, _ = judge.render_prompt(judge.load_positions()[PID], fake_rec(), judge.FROZEN['order'], judge.DEFAULT_DECKS, judge.FROZEN['compact_above'], 'v1')
        return system, user

    def test_a_missing_key_stops_a_live_run_before_any_ledger_or_call(self):
        home = tmp()
        with mock.patch.dict(os.environ, {'HOME': home}), mock.patch.object(providers, '_post_json') as post:
            os.environ.pop('GEMINI_API_KEY', None)
            with self.assertRaises(SystemExit) as cm:
                self.run_main(self.argv(mode='--live'))
        self.assertIn('GEMINI_API_KEY', str(cm.exception))
        post.assert_not_called()
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json')))
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))

    def test_a_live_run_goes_through_the_gate(self):
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', return_value=interaction()) as post:
            code, err = self.run_main(self.argv(mode='--live', total='0.5', cap='0.5'))
        self.assertEqual(code, 0, err)
        self.assertEqual(post.call_count, 1)
        self.assertNotIn('k-not-a-real-key', err)
        self.assertGreater(self.rows()[0]['cost']['usd'], 0)

    def test_a_failed_live_call_charges_its_worst_case_and_leaves_no_lock(self):
        import urllib.error
        err = urllib.error.HTTPError('u', 500, 'x', {}, io.BytesIO(b'{"error": "boom"}'))
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', side_effect=err):
            with self.assertRaises(SystemExit):
                self.run_main(self.argv(mode='--live', total='0.5', cap='0.5'))
        with open(os.path.join(self.d, 'ledger.json')) as f:
            self.assertGreater(json.load(f)['accrued_usd'], 0.1)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))

    def test_usage_errors_exit_before_anything_runs(self):
        with self.assertRaises(SystemExit):
            self.run_main(self.argv(repeat='9'))  # 9 tasks > --max-calls 3
        open(os.path.join(self.d, 'rows.jsonl'), 'w').close()
        with self.assertRaises(SystemExit):
            self.run_main(self.argv())  # --out exists


if __name__ == '__main__':
    unittest.main()
