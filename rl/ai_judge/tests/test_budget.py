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
from test_gemini import PID, fake_rec, generate_content, interaction  # noqa: E402

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

    def test_the_vertex_reservation_at_32768_output_tokens_and_how_many_workers_fit(self):
        for provider in ('gemini', 'gemini-vertex'):
            self.assertEqual(bj.reservation_price(provider, 'gemini-4-argon'), (4.0, 20.0))
        w = bj.worst_case_usd(SYS, USER, 'gemini-vertex', 'gemini-4-argon', 32768)  # a 10,000-byte prompt
        self.assertAlmostEqual(w, (10000 + bj.OVERHEAD_TOKENS) * 4 / 1e6 + 32768 * 20 / 1e6)
        self.assertGreater(w, 0.70)  # the output cap alone reserves $0.655
        self.assertLess(w, 0.75)
        for nbytes in (2400, 15000, 40000, 77000, 243500):  # the old positions: the smallest prompt, a typical one, a full-form 80-plan list, the 479-plan list, the 1,203-plan list
            w = bj.worst_case_usd('S' * (nbytes // 2), 'U' * (nbytes - nbytes // 2), 'gemini-vertex', 'gemini-4-argon', 32768)
            self.assertLess(4 * w, 15.0, nbytes)  # four workers always fit in the $15 ledger (the reservation of the largest is about $1.64)

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
        self.assertFalse(led.reserve(0.4, block=False))  # 0.8 reserved + 0.4 > 1.0: not now (with block=True it would wait for the calls in flight)
        led.settle(0.4, 0.05)
        self.assertTrue(led.reserve(0.4))  # 0.05 accrued + 0.4 reserved + 0.4 = 0.85
        self.assertEqual(led.refused, 1)
        led.close()

    def test_the_run_cap_binds_separately_from_the_total(self):
        led, _ = self.ledger(10.0, 0.5)
        self.assertTrue(led.reserve(0.3))
        self.assertFalse(led.reserve(0.3, block=False))
        led.close()

    def test_a_call_that_fits_once_the_others_settle_waits_and_one_that_never_fits_is_refused(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.4))
        self.assertTrue(led.reserve(0.4))
        got = []
        t = threading.Thread(target=lambda: got.append(led.reserve(0.4)))
        t.start()
        t.join(0.3)
        self.assertTrue(t.is_alive())  # 0.8 in flight: it waits, it is not dropped
        self.assertEqual(got, [])
        led.settle(0.4, 0.05)  # one call returns: now 0.05 + 0.4 + 0.4 fits
        t.join(5)
        self.assertEqual(got, [True])
        self.assertEqual(led.refused, 0)
        led.settle(0.4, 0.05)
        led.settle(0.4, 0.05)
        self.assertFalse(led.reserve(0.95))  # 0.15 accrued + 0.95 > 1.0 even with nothing in flight: refused at once, no waiting
        self.assertEqual(led.refused, 1)
        led.close()

    def test_a_waiting_call_is_refused_when_a_failure_halts_the_run(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.4))
        self.assertTrue(led.reserve(0.4))
        got = []
        t = threading.Thread(target=lambda: got.append(led.reserve(0.4)))
        t.start()
        t.join(0.2)
        led.charge_failed(0.4)
        t.join(5)
        self.assertEqual(got, [False])
        led.close()

    def test_four_workers_and_51_calls_all_fit_under_the_readme_caps_and_under_a_tighter_run_cap(self):
        # the review's simulation: median old prompt (13,151 bytes: reservation $0.716), 6,200 input and 10,000 output tokens per call ($0.112), 4 workers; the README's $15 total with
        # the run cap equal to the total, and the tighter $8 cap that used to drop the tail of the batch
        from concurrent.futures import ThreadPoolExecutor
        for cap in (15.0, 8.0):
            led, _ = self.ledger(15.0, cap)
            sys_, usr = 'S' * 5000, 'U' * 8151
            sent, refused = [], []

            def call(_):
                w = bj.worst_case_usd(sys_, usr, 'gemini-vertex', 'gemini-4-argon', 32768)
                if not led.reserve(w):
                    refused.append(1)
                    return
                sent.append(1)
                led.settle(w, 6200 * 2 / 1e6 + 10000 * 10 / 1e6)
            with ThreadPoolExecutor(4) as ex:
                list(ex.map(call, range(51)))
            self.assertEqual((len(sent), len(refused)), (51, 0), cap)  # a call that fits once the others settle waits instead of being dropped
            self.assertLessEqual(led.peak, cap + 1e-9)
            self.assertAlmostEqual(led.accrued, 51 * (6200 * 2 / 1e6 + 10000 * 10 / 1e6))
            led.close()

    def test_a_failing_ledger_file_never_leaves_a_call_waiting_for_ever(self):
        led, _ = self.ledger(1.0)
        self.assertTrue(led.reserve(0.6))
        got = []
        t = threading.Thread(target=lambda: got.append(led.reserve(0.6)))
        t.start()
        t.join(0.2)
        self.assertTrue(t.is_alive())  # 0.6 in flight: the second call waits
        with mock.patch('os.replace', side_effect=OSError(28, 'No space left on device')), contextlib.redirect_stderr(io.StringIO()) as err:
            led.settle(0.6, 0.1)  # the write fails: no exception, the state is settled in memory and the run is halted
        t.join(5)
        self.assertFalse(t.is_alive())  # the waiter was woken, saw the halt and was refused
        self.assertEqual(got, [False])
        self.assertIn('cannot be written', led.halted)
        self.assertIn('cannot be written', err.getvalue())
        self.assertEqual((round(led.accrued, 6), round(led.reserved, 6)), (0.1, 0.0))
        led.close()

    def test_a_reservation_whose_save_fails_is_given_back_and_refused(self):
        led, _ = self.ledger(1.0)
        with mock.patch('os.replace', side_effect=OSError(28, 'No space left on device')), contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(led.reserve(0.6))
        self.assertEqual(led.reserved, 0)  # not left reserved for a call that will never be sent
        self.assertEqual(led.refused, 1)
        led.close()

    def test_a_call_that_cannot_wait_for_anything_is_refused_not_left_waiting(self):
        led, _ = self.ledger(1.0)
        led.accrued = 0.5
        done = []
        t = threading.Thread(target=lambda: done.append(led.reserve(0.6)))  # 0.5 + 0.6 > 1.0 and nothing is in flight
        t.start()
        t.join(5)
        self.assertFalse(t.is_alive())
        self.assertEqual(done, [False])
        led.close()

    def test_a_ledger_needs_a_finite_positive_total_and_run_cap(self):
        for total, cap in (('nan', 5.0), (float('inf'), 5.0), (15.0, float('nan')), (15.0, float('inf')), (0, 5.0), (-1, 5.0), (15.0, 0)):
            with self.assertRaises(SystemExit):
                bj.Ledger(os.path.join(tmp(), 'l.json'), total, cap, 'x')

    def test_a_ledger_file_that_cannot_be_written_at_the_start_stops_the_run_and_frees_the_lock(self):
        d = tmp()
        with mock.patch('os.replace', side_effect=OSError(13, 'Permission denied')), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')
        self.assertFalse(os.path.exists(os.path.join(d, 'l.json.lock')))

    def test_calls_in_flight_are_on_the_file_and_a_killed_run_is_charged_for_them(self):
        d = tmp()
        path = os.path.join(d, 'l.json')
        a = bj.Ledger(path, 15.0, 15.0, 'x')
        a.reserve(0.7)
        a.reserve(0.7)
        with open(path) as f:
            self.assertAlmostEqual(json.load(f)['in_flight_usd'], 1.4)
        a.settle(0.7, 0.1)
        with open(path) as f:
            data = json.load(f)
        self.assertEqual((round(data['accrued_usd'], 6), round(data['in_flight_usd'], 6)), (0.1, 0.7))
        os.remove(path + '.lock')  # the run is killed (no close, no settle): its lock is removed by hand
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            b = bj.Ledger(path, 15.0, 15.0, 'x')
        self.assertAlmostEqual(b.accrued, 0.8)  # 0.1 settled + the 0.7 call that was still out, at its worst case
        self.assertIn('in flight', err.getvalue())
        b.close()
        c = bj.Ledger(path, 15.0, 15.0, 'x')  # the notice is given once: the charge is now part of accrued
        self.assertAlmostEqual(c.accrued, 0.8)
        c.close()

    def test_a_ledger_that_finished_has_nothing_in_flight(self):
        led, d = self.ledger(1.0)
        led.reserve(0.4)
        led.settle(0.4, 0.1)
        led.close()
        with open(os.path.join(d, 'l.json')) as f:
            self.assertEqual(json.load(f)['in_flight_usd'], 0)

    def test_the_total_is_shared_by_the_primary_and_the_repeat_run(self):
        d = tmp()
        a = bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')
        self.assertTrue(a.reserve(0.3))
        a.settle(0.3, 0.3)
        a.close()
        b = bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'x')  # the repeat run continues from the file
        self.assertAlmostEqual(b.accrued, 0.3)
        self.assertTrue(b.reserve(0.7))
        self.assertFalse(b.reserve(0.01, block=False))  # 0.3 + 0.7 reserved + 0.01 > 1.0
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
        with self.assertRaises(SystemExit) as cm:
            bj.Ledger(os.path.join(d, 'l.json'), 1.0, 1.0, 'gemini:gemini-4-argon')  # the same total AND the same label: only the lock can refuse it
        self.assertIn('lock', str(cm.exception))
        self.assertTrue(os.path.exists(os.path.join(d, 'l.json.lock')))  # the refused run did not delete the first run's lock
        led.close()

    def test_settled_spending_counts_against_the_run_cap(self):
        led, _ = self.ledger(10.0, 0.5)
        self.assertTrue(led.reserve(0.3))
        led.settle(0.3, 0.3)
        self.assertAlmostEqual(led.run_accrued, 0.3)
        self.assertFalse(led.reserve(0.3))  # 0.3 spent in this run + 0.3 > the 0.5 run cap, though the total of 10 has room: refused at once (nothing in flight to wait for)
        self.assertEqual(led.refused, 1)
        led.close()

    def test_a_failed_call_counts_against_the_run_cap_and_gives_back_its_reservation(self):
        led, _ = self.ledger(10.0, 0.5)
        self.assertTrue(led.reserve(0.3))
        led.charge_failed(0.3)
        self.assertAlmostEqual(led.run_accrued, 0.3)
        self.assertAlmostEqual(led.accrued, 0.3)
        self.assertEqual(led.reserved, 0)
        led.close()

    def test_a_second_run_starts_its_own_run_count_but_continues_the_total(self):
        d = tmp()
        a = bj.Ledger(os.path.join(d, 'l.json'), 10.0, 0.5, 'x')
        a.reserve(0.3)
        a.settle(0.3, 0.3)
        a.close()
        b = bj.Ledger(os.path.join(d, 'l.json'), 10.0, 0.5, 'x')
        self.assertEqual((b.run_accrued, round(b.accrued, 6)), (0.0, 0.3))
        self.assertTrue(b.reserve(0.4))
        b.close()

    def test_the_peak_is_what_was_reserved(self):
        led, _ = self.ledger(1.0)
        led.reserve(0.4)
        led.reserve(0.4)
        self.assertAlmostEqual(led.peak, 0.8)
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
        for obj, name in ((providers, 'call_gemini'), (providers, 'call_vertex'), (judge, 'call_claude'), (providers, 'load_key'), (judge, 'load_key')):
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

    def test_a_reply_the_costing_cannot_read_is_charged_at_its_worst_case_and_never_left_reserved(self):
        def weird(system, user, model=None, max_tokens=8000, temperature=None, thinking=None, timeout=300):
            return 'PLAN: 1', {'input_tokens': 10 ** 400, 'output_tokens': 1}, 0.0, model, {'usage_missing': False}  # an int no float can hold
        bj.install_gate(self.led, weird, 'gemini')
        with self.assertRaises(OverflowError):
            providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})
        self.assertEqual((self.led.reserved, self.led.failed_calls), (0, 1))
        self.assertAlmostEqual(self.led.accrued, bj.worst_case_usd(SYS, USER, 'gemini', 'm', 8000))
        self.assertIn('failed', self.led.halted)

    def test_a_reply_without_usage_is_charged_its_worst_case(self):
        bj.install_gate(self.led, self.gemini_call(usage_missing=True), 'gemini')
        providers.call_gemini(SYS, USER, 'm', max_tokens=8000, temperature=None, thinking={})
        self.assertAlmostEqual(self.led.accrued, bj.worst_case_usd(SYS, USER, 'gemini', 'm', 8000))
        self.assertIsNone(self.led.halted)  # exactly its worst case is not "above" it

    def test_the_vertex_gate_patches_the_vertex_call_only_and_reserves_32768_tokens(self):
        before = (providers.call_gemini, judge.call_claude)
        bj.install_gate(self.led, self.gemini_call(), 'gemini-vertex')
        self.assertEqual((providers.call_gemini, judge.call_claude), before)
        with mock.patch.object(providers, 'gemini_price', return_value=INTRO):
            providers.call_vertex(SYS, USER, 'gemini-4-argon', max_tokens=32768, temperature=None, thinking={'thinking_level': 'HIGH'})
        self.assertAlmostEqual(self.led.accrued, 10000 * 2 / 1e6 + 2000 * 10 / 1e6)
        self.assertEqual((self.led.reserved, self.led.calls), (0, 1))
        w = bj.worst_case_usd(SYS, USER, 'gemini-vertex', 'gemini-4-argon', 32768)
        self.led.accrued = 0
        self.assertTrue(self.led.reserve(w))
        self.assertFalse(self.led.reserve(w, block=False))  # two of them do not fit in a $1 ledger (they fit in $2: three do not, so a $2 smoke test runs one or two workers)

    def test_the_anthropic_gate_patches_the_anthropic_call_only(self):
        gemini_before = providers.call_gemini

        def claude(system, user, model, max_tokens, temperature, timeout=300):
            return 't', {'input_tokens': 1000, 'output_tokens': 100}, 0.0, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']}
        bj.install_gate(self.led, claude, 'anthropic')
        self.assertIs(providers.call_gemini, gemini_before)
        judge.call_claude(SYS, USER, judge.MODEL, max_tokens=8000, temperature=None)
        self.assertAlmostEqual(self.led.accrued, 1000 * 3 / 1e6 + 100 * 15 / 1e6)


class Wrapper(unittest.TestCase):
    """budget_judge.main end to end with --mock (the plan lister is replaced by a fake plan list; the positions and decks are the real ones). Run for the Developer API provider
    here and for Vertex AI (the provider of the current freeze) in WrapperVertex."""
    PROVIDER, KEY_VAR, OTHER_KEY_VAR, LEVEL, MAX_TOKENS, CALL = 'gemini', 'GEMINI_API_KEY', 'VERTEX_API_KEY', 'high', 8000, 'call_gemini'

    def live_json(self):
        return interaction()

    def setUp(self):
        for obj, name in ((providers, 'call_gemini'), (providers, 'call_vertex'), (judge, 'call_claude'), (providers, 'load_key'), (judge, 'load_key')):
            p = mock.patch.object(obj, name, getattr(obj, name))
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(judge, 'list_plans', side_effect=lambda ids, *a, **k: {i: fake_rec() for i in ids})
        p.start()
        self.addCleanup(p.stop)
        self.d = tmp()

    def argv(self, *extra, total='15', cap='8', mode='--mock', out='rows.jsonl', ledger='ledger.json', repeat='1'):
        return ['--positions', judge.DEFAULT_POSITIONS, '--decks', judge.DEFAULT_DECKS, '--ids', PID, '--max-calls', '3', '--repeat', repeat, '--workers', '1', '--tag', 'T',
                '--out', os.path.join(self.d, out), '--ledger', os.path.join(self.d, ledger), '--total-usd', total, '--run-cap-usd', cap, '--provider', self.PROVIDER, mode, *extra]

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
            self.assertEqual((r['tag'], r['provider'], r['model'], r['thinking_level'], r['max_tokens'], r['frozen'], r['bot']),
                             ('T', self.PROVIDER, 'gemini-4-argon', self.LEVEL, self.MAX_TOKENS, True, 'judge'))
            self.assertIsNotNone(r['plan_number'])
        with open(os.path.join(self.d, 'ledger.json')) as f:
            led = json.load(f)
        self.assertEqual((led['total_usd'], led['label']), (15.0, f'{self.PROVIDER}:gemini-4-argon'))
        self.assertAlmostEqual(led['accrued_usd'], sum(r['cost']['usd'] for r in rows), places=4)  # each row's cost is rounded to 5 places, the ledger's total to 6
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))
        with self.assertRaises(SystemExit):
            providers.load_key()  # the mock replaced the key readers: a key was never read

    def test_the_wrapper_makes_the_rows_judge_one_makes(self):
        self.run_main(self.argv())
        row = self.rows()[0]
        with mock.patch.object(providers, self.CALL, bj.mock_call(self.PROVIDER)):
            own, _, _ = judge.judge_one(PID, judge.load_positions(), {PID: fake_rec()}, judge.FROZEN['order'], True, 'gemini-4-argon', None, judge.DEFAULT_DECKS,
                                        judge.FROZEN['compact_above'], self.MAX_TOKENS, 'v1', False, self.PROVIDER, self.LEVEL)
        self.assertIs(row.pop('mock'), True)  # the one difference: a mock row says so, and formal.py refuses it
        for r in (row, own):
            r.pop('repeat', None), r.pop('tag', None), r.pop('seconds')
        self.assertEqual(row, own)

    def test_the_run_cap_stops_calls_and_the_batch_is_incomplete(self):
        code, err = self.run_main(self.argv(cap='0.05'))
        self.assertEqual(code, 2)
        self.assertIn('NOT SENT', err)
        self.assertEqual(self.rows(), [])

    def test_the_second_run_continues_the_ledger_and_the_total_holds_across_runs(self):
        w = bj.worst_case_usd(*self._prompt(), self.PROVIDER, 'gemini-4-argon', self.MAX_TOKENS)
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
        with mock.patch.dict(os.environ, {'HOME': home, self.OTHER_KEY_VAR: 'the-other-providers-key'}), mock.patch.object(providers, '_post_json') as post:
            os.environ.pop(self.KEY_VAR, None)
            with self.assertRaises(SystemExit) as cm:
                self.run_main(self.argv(mode='--live'))
        self.assertIn(self.KEY_VAR, str(cm.exception))  # the other provider's key variable does not stand in for it
        self.assertNotIn('the-other-providers-key', str(cm.exception))
        post.assert_not_called()
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json')))
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))

    def test_a_live_run_goes_through_the_gate(self):
        with mock.patch.dict(os.environ, {self.KEY_VAR: 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', return_value=self.live_json()) as post:
            code, err = self.run_main(self.argv(mode='--live', total='2', cap='2'))
        self.assertEqual(code, 0, err)
        self.assertEqual(post.call_count, 1)
        self.assertNotIn('k-not-a-real-key', err)
        self.assertNotIn('k-not-a-real-key', json.dumps(self.rows()))
        self.assertGreater(self.rows()[0]['cost']['usd'], 0)
        self.assertEqual(post.call_args.args[1]['x-goog-api-key'], 'k-not-a-real-key')  # the key goes in the header
        self.assertNotIn('k-not-a-real-key', post.call_args.args[0])  # never in the URL

    def test_a_failed_live_call_charges_its_worst_case_and_leaves_no_lock(self):
        import urllib.error
        err = urllib.error.HTTPError('u', 500, 'x', {}, io.BytesIO(b'{"error": "boom"}'))
        with mock.patch.dict(os.environ, {self.KEY_VAR: 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', side_effect=err):
            code, stderr = self.run_main(self.argv(mode='--live', total='2', cap='2', repeat='3'))
        self.assertEqual(code, 2)  # an incomplete batch, not a traceback
        self.assertIn('TASK FAILED', stderr)
        self.assertIn('INCOMPLETE BATCH', stderr)
        self.assertNotIn('k-not-a-real-key', stderr)
        self.assertEqual(self.rows(), [])
        with open(os.path.join(self.d, 'ledger.json')) as f:
            data = json.load(f)
        self.assertGreater(data['accrued_usd'], 0.1)  # the failed call at its worst case, and nothing more was sent after it
        self.assertEqual(data['in_flight_usd'], 0)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))

    def test_any_exception_out_of_a_task_ends_the_batch_as_incomplete_not_a_traceback(self):
        with mock.patch.dict(os.environ, {self.KEY_VAR: 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', side_effect=KeyError('unexpected')):
            code, err = self.run_main(self.argv(mode='--live', total='2', cap='2', repeat='3'))
        self.assertEqual(code, 2)
        self.assertIn('TASK FAILED', err)
        self.assertIn('KeyError', err)
        self.assertIn('INCOMPLETE BATCH', err)
        with open(os.path.join(self.d, 'ledger.json')) as f:
            data = json.load(f)
        self.assertGreater(data['accrued_usd'], 0.1)  # the call that raised is charged at its worst case
        self.assertEqual(data['in_flight_usd'], 0)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json.lock')))

    def test_a_refusal_of_judge_one_itself_is_reported_and_costs_nothing(self):
        capped = lambda ids, *a, **k: {i: {**fake_rec(), 'capped': True, 'n_plans': 8} for i in ids}
        with mock.patch.object(judge, 'list_plans', side_effect=capped):
            code, err = self.run_main(self.argv())
        self.assertEqual(code, 2)
        self.assertIn('TASK FAILED', err)
        self.assertIn('capped', err)
        with open(os.path.join(self.d, 'ledger.json')) as f:
            data = json.load(f)
        self.assertEqual((data['accrued_usd'], data['in_flight_usd']), (0.0, 0.0))  # nothing was sent, so nothing is charged

    def test_a_key_the_http_library_refuses_stops_the_run_without_showing_it(self):
        # a key with a control character cannot pass load_key; this is the same refusal one level down (the preflight sees only a present key in the old code)
        with mock.patch.dict(os.environ, {self.KEY_VAR: 'AQ.Ab8RN6exampleexampleexampleexample\rX'}):
            code_msg = None
            with self.assertRaises(SystemExit) as cm:
                self.run_main(self.argv(mode='--live', total='2', cap='2'))
            code_msg = str(cm.exception)
        self.assertIn(self.KEY_VAR, code_msg)
        self.assertNotIn('AQ.Ab8', code_msg)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'ledger.json')))  # stopped before any ledger or reservation exists

    def test_usage_errors_exit_before_anything_runs(self):
        with self.assertRaises(SystemExit):
            self.run_main(self.argv(repeat='9'))  # 9 tasks > --max-calls 3
        open(os.path.join(self.d, 'rows.jsonl'), 'w').close()
        with self.assertRaises(SystemExit):
            self.run_main(self.argv())  # --out exists


class WrapperVertex(Wrapper):
    """The same end-to-end tests for the provider of the current freeze: Vertex AI, 32,768 output tokens, level HIGH, key in VERTEX_API_KEY."""
    PROVIDER, KEY_VAR, OTHER_KEY_VAR, LEVEL, MAX_TOKENS, CALL = 'gemini-vertex', 'VERTEX_API_KEY', 'GEMINI_API_KEY', 'HIGH', 32768, 'call_vertex'

    def live_json(self):
        return generate_content()

    def test_the_default_provider_is_vertex_and_the_mock_run_needs_no_flag(self):
        argv = self.argv()
        del argv[argv.index('--provider'):argv.index('--provider') + 2]
        code, err = self.run_main(argv)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.rows()[0]['provider'], 'gemini-vertex')

    def test_a_reply_cut_at_the_cap_is_written_without_a_choice_and_the_batch_is_incomplete(self):
        cut = generate_content(finish='MAX_TOKENS')
        with mock.patch.dict(os.environ, {self.KEY_VAR: 'k-not-a-real-key'}), mock.patch.object(providers, '_post_json', return_value=cut):
            code, err = self.run_main(self.argv(mode='--live', total='2', cap='2'))
        self.assertEqual(code, 2)
        self.assertIn('INCOMPLETE BATCH', err)
        row = self.rows()[0]
        self.assertEqual((row['plan_number'], row['stop_reason']), (None, 'vertex:MAX_TOKENS'))
        self.assertGreater(row['cost']['usd'], 0)  # the call was billed: it is on the ledger at its actual cost


if __name__ == '__main__':
    unittest.main()
