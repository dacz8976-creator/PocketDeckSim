import io
import json
import os
import socket
import sys
import unittest
import urllib.request
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
sys.path.insert(0, HERE)
import budget_judge  # noqa: E402
import game_call  # noqa: E402
import game_kit  # noqa: E402
import judge  # noqa: E402
import providers  # noqa: E402
import test_game_lister as TL  # noqa: E402

TMP = os.environ['TMPDIR']
_SAVED = {}


class _BlockedOpener:
    def open(self, *a, **k):
        raise RuntimeError('NETWORK_BLOCKED')


def _blocked(*a, **k):
    raise RuntimeError('NETWORK_BLOCKED')


def setUpModule():
    _SAVED['opener'] = providers._OPENER
    providers._OPENER = _BlockedOpener()
    _SAVED['patches'] = [mock.patch.object(socket.socket, 'connect', _blocked), mock.patch.object(socket, 'create_connection', _blocked),
                         mock.patch.object(socket, 'getaddrinfo', _blocked)]
    for p in _SAVED['patches']:
        p.start()


def tearDownModule():
    for p in _SAVED['patches']:
        p.stop()
    providers._OPENER = _SAVED['opener']


class Clock:
    def __init__(self):
        self.t = 1000.0
        self.waits = []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.waits.append(s)
        self.t += s


_CASE = []


def case():
    """(pid, original pos, positions-mode rec, decks_dir) from the first fixture with a list of at least 2 plans"""
    if not _CASE:
        label, f, decks, only = TL.pos_files()[0]
        out = TL.run(TL.pos_argv(TL.JP, f, decks, only)).stdout.decode().splitlines()
        with open(f) as fh:
            by_id = {p['id']: p for p in json.load(fh)}
        for l in out:
            r = json.loads(l)
            if r['kind'] == 'plans' and r['n_plans'] >= 2 and not r['capped']:
                _CASE.append((r['id'], by_id[r['id']], r, decks))
                break
    return _CASE[0]


class CallBase(unittest.TestCase):
    def setUp(self):
        self.saved = (providers._post_json, providers.load_key, providers._OPENER, providers.call_vertex, providers._VERTEX_PROJECT[0], game_call.open_ledger)
        self.ledger = os.path.join(TMP, 'call_ledger_%s.json' % self.id().split('.')[-1])
        for p in (self.ledger, self.ledger + '.lock', self.ledger + '.tmp'):
            if os.path.exists(p):
                os.remove(p)
        self.clk = Clock()
        self.instances = []
        real_open = game_call.open_ledger

        def spy(path, total):
            led = real_open(path, total)
            self.instances.append(led)
            return led
        game_call.open_ledger = spy

    def tearDown(self):
        providers._post_json, providers.load_key, providers._OPENER, providers.call_vertex, providers._VERTEX_PROJECT[0], game_call.open_ledger = self.saved
        for p in (self.ledger, self.ledger + '.lock', self.ledger + '.tmp'):
            if os.path.exists(p):
                os.remove(p)

    def start(self, mode, seed=1, deadline=None, total=1000):
        self.mock = game_call.install_mock(mode, seed)
        game_call.install_recorder()
        dl = deadline if deadline is not None else self.clk() + 100000
        self.gv = game_call.GatedVertex(self.ledger, total, dl, clock=self.clk, sleep=self.clk.sleep)
        return self.gv

    def decide(self):
        pid, pos, rec, decks = case()
        return game_call.judge_decision(pid, pos, rec, decks, self.gv, True)

    def worst(self):
        pid, pos, rec, decks = case()
        system, user, shown = judge.render_prompt(pos, rec, 'shuffle-id', decks, 80, 'v1')
        return budget_judge.worst_case_usd(system, user, 'gemini-vertex', 'gemini-4-argon', 32768)

    def accrued(self):
        with open(self.ledger) as f:
            return json.load(f)['accrued_usd']


class Calls(CallBase):
    def test_N1_network_blocked(self):
        with self.assertRaises(RuntimeError):
            urllib.request.urlopen('http://192.0.2.1/')
        with self.assertRaises(RuntimeError):
            providers._OPENER.open('http://192.0.2.1/')

    def test_C1_ok(self):
        self.start('random')
        row = self.decide()
        n = row['n_plans']
        self.assertTrue(1 <= row['plan_number'] <= n)
        self.assertTrue(row['mock'])
        self.assertTrue(row['frozen'])
        self.assertEqual(row['model_returned'], 'gemini-4-argon-mock')
        self.assertEqual(len(self.gv.tries), 1)
        self.assertGreater(self.accrued(), 0)
        self.assertLess(self.accrued(), self.worst())
        self.assertFalse(os.path.exists(self.ledger + '.lock'))
        with open(self.ledger) as f:
            self.assertEqual(json.load(f)['in_flight_usd'], 0)

    def test_C2_429_then_ok(self):
        self.start('seq:429,ok')
        self.decide()
        t = self.gv.tries
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0]['http_status'], 429)
        self.assertEqual(t[0]['charged_usd'], 0.0)
        self.assertEqual(t[0]['outcome'], 'http_429')
        self.assertEqual(t[1]['outcome'], 'ok')
        self.assertEqual(self.gv.waits, [150])
        self.assertEqual(self.clk.waits, [150])
        self.assertAlmostEqual(self.accrued(), t[1]['charged_usd'], places=5)

    def test_C3_three_429(self):
        self.start('seq:429,429,429')
        with self.assertRaises(game_call.CallFailed) as cm:
            self.decide()
        self.assertEqual(len(cm.exception.tries), 3)
        self.assertTrue(all(t['charged_usd'] == 0.0 for t in cm.exception.tries))
        self.assertEqual(sum(i.failed_calls for i in self.instances), 3)
        self.assertTrue(all(i.halted is None for i in self.instances))
        self.assertEqual(self.accrued(), 0.0)
        self.assertEqual(self.gv.waits, [150, 300])

    def test_C3b_bound_check_raises_ledger_bound(self):
        for mode in ('seq:ok', 'seq:429u,ok', 'seq:500u'):
            with self.subTest(mode=mode):
                for pth in (self.ledger, self.ledger + '.lock'):
                    if os.path.exists(pth):
                        os.remove(pth)
                self.instances.clear()
                self.start(mode)
                w = self.worst()
                with mock.patch.object(budget_judge, 'actual_usd', lambda provider, out, worst: 2 * worst + 0.01):
                    with self.assertRaises(game_call.LedgerBound) as cm:
                        self.decide()
                self.assertIsInstance(cm.exception, game_call.LedgerStop)
                self.assertEqual(self.mock.calls, 1)
                self.assertEqual(len(self.gv.tries), 1)
                self.assertEqual(len(cm.exception.tries), 1)
                self.assertAlmostEqual(self.accrued(), 2 * w + 0.01, delta=1e-6)
                self.assertFalse(os.path.exists(self.ledger + '.lock'))

    def test_C4_500(self):
        w = self.worst()
        self.start('seq:500')
        with self.assertRaises(game_call.CallFailed) as cm:
            self.decide()
        t = cm.exception.tries
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]['http_status'], 500)
        self.assertAlmostEqual(t[0]['charged_usd'], w, places=9)
        self.assertEqual(self.mock.calls, 1)
        self.assertAlmostEqual(self.accrued(), w, places=5)
        self.assertIsNone(self.instances[0].halted)
        os.remove(self.ledger)
        self.start('seq:500u')
        with self.assertRaises(game_call.CallFailed) as cm:
            self.decide()
        t = cm.exception.tries
        self.assertEqual(len(t), 1)
        self.assertTrue(t[0]['usage_seen'])
        self.assertTrue(0 < t[0]['charged_usd'] < w)
        self.assertEqual(self.mock.calls, 1)

    def test_C5_timeout(self):
        w = self.worst()
        self.start('seq:timeout,timeout,ok')
        self.decide()
        t = self.gv.tries
        self.assertEqual(len(t), 3)
        for x in t[:2]:
            self.assertAlmostEqual(x['charged_usd'], w, places=9)
            self.assertEqual(x['outcome'], 'transport:TimeoutError')
            self.assertIsNone(x['http_status'])
        os.remove(self.ledger)
        self.clk.t = 1000.0
        self.start('seq:timeout,ok', deadline=1000.0 + game_kit.VERTEX_TIMEOUT_S + game_kit.SHADOW_RESERVE_S + 100)
        with self.assertRaises(game_call.CallFailed) as cm:
            self.decide()
        self.assertEqual(len(cm.exception.tries), 1)
        self.assertEqual(cm.exception.detail, 'no_time')
        self.assertEqual(self.mock.calls, 1)

    def test_C6_returned_never_resent(self):
        for mode in ('seq:max_tokens', 'seq:noplan'):
            if os.path.exists(self.ledger):
                os.remove(self.ledger)
            self.start(mode)
            row = self.decide()
            self.assertIsNone(row['plan_number'])
            self.assertEqual(len(self.gv.tries), 1)
            self.assertEqual(self.mock.calls, 1)
            self.assertGreater(self.accrued(), 0)
            self.assertFalse(os.path.exists(self.ledger + '.lock'))

    def test_C7_window(self):
        self.start('seq:timeout,timeout,timeout')
        self.mock.hook = lambda: setattr(self.clk, 't', self.clk.t + 300)
        with self.assertRaises(game_call.CallFailed) as cm:
            self.decide()
        self.assertEqual(len(cm.exception.tries), 2)
        self.assertEqual(self.mock.calls, 2)
        os.remove(self.ledger)
        self.clk.t = 1000.0
        with mock.patch.object(game_kit, 'RETRY_WAITS_S', (150, 500)):
            self.start('seq:timeout,timeout,timeout')
            with self.assertRaises(game_call.CallFailed) as cm:
                self.decide()
        self.assertEqual(len(cm.exception.tries), 2)
        self.assertEqual(self.clk.waits[-1], 150)

    def test_C8_ledger_refusals(self):
        self.start('random')
        open(self.ledger + '.lock', 'w').close()
        with self.assertRaises(game_call.LedgerStop):
            self.decide()
        os.remove(self.ledger + '.lock')
        with open(self.ledger, 'w') as f:
            json.dump({'accrued_usd': 0, 'in_flight_usd': 0, 'total_usd': 5.0, 'label': game_kit.LEDGER_LABEL}, f)
        with self.assertRaises(game_call.LedgerStop):
            self.decide()
        self.assertFalse(os.path.exists(self.ledger + '.lock'))
        with open(self.ledger, 'w') as f:
            json.dump({'accrued_usd': 0, 'in_flight_usd': 0, 'total_usd': 1000.0, 'label': 'other'}, f)
        with self.assertRaises(game_call.LedgerStop):
            self.decide()
        os.remove(self.ledger)
        self.start('random', total=0.01)  # a worst case that can never fit
        with self.assertRaises(game_call.LedgerStop):
            self.decide()
        self.assertEqual(self.mock.calls, 0)
        self.assertFalse(os.path.exists(self.ledger + '.lock'))

    def test_C9_env_never_read_in_mock_and_live_setup(self):
        fake = 'fake' + '-' * 3 + '0' * 24
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': fake, 'VERTEX_PROJECT': 'mock-project-0'}):
            self.start('random')
            self.decide()
            self.assertEqual(self.mock.last_headers['x-goog-api-key'], 'MOCK-KEY')
            self.assertEqual(providers.load_key('VERTEX_API_KEY'), 'MOCK-KEY')
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': fake, 'VERTEX_PROJECT': 'mock-project-0'}):
            providers._VERTEX_PROJECT[0] = None
            with self.assertRaises(game_call.LiveSetupError) as cm:
                game_call.install_live()
            self.assertNotIn(fake, str(cm.exception))
        shaped = 'AI' + 'za' + 'x' * 30
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': shaped, 'VERTEX_PROJECT': ''}):
            providers._VERTEX_PROJECT[0] = None
            with self.assertRaises(game_call.LiveSetupError) as cm:
                game_call.install_live()
            self.assertNotIn(shaped, str(cm.exception))
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': shaped, 'VERTEX_PROJECT': 'mock-project-0'}):
            providers._VERTEX_PROJECT[0] = None
            game_call.install_live()
            self.assertEqual(providers.load_key('VERTEX_API_KEY'), shaped)

    def test_C10_429_with_usage(self):
        w = self.worst()
        self.start('seq:429u,ok')
        self.decide()
        t = self.gv.tries[0]
        self.assertEqual(t['http_status'], 429)
        self.assertTrue(t['usage_seen'])
        self.assertTrue(0 < t['charged_usd'] < w)

    def test_C11_not_sent(self):
        for exc in (SystemExit('no'), ValueError('no')):
            if os.path.exists(self.ledger):
                os.remove(self.ledger)
            self.start('random')
            with mock.patch.object(providers, 'vertex_url', side_effect=exc):
                with self.assertRaises(game_call.CallNotSent):
                    self.decide()
            self.assertEqual(self.accrued(), 0.0)
            self.assertEqual(sum(t['charged_usd'] for t in self.gv.tries), 0.0)
            self.assertEqual(self.mock.calls, 0)
            self.assertFalse(os.path.exists(self.ledger + '.lock'))


if __name__ == '__main__':
    unittest.main()
