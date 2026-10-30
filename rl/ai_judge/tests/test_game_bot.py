import builtins
import hashlib
import io
import json
import os
import re
import socket
import sys
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
sys.path.insert(0, HERE)
import budget_judge  # noqa: E402
import game_bot  # noqa: E402
import game_call  # noqa: E402
import game_kit  # noqa: E402
import game_lister  # noqa: E402
import game_obs  # noqa: E402
import game_shadow  # noqa: E402
import providers  # noqa: E402
import test_game_call as TC  # noqa: E402
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


KEY_RES = [re.compile(p) for p in game_call.KEY_PATTERNS]


def act(step, n=None):
    inner = {'step': step}
    if n is not None:
        inner['n'] = n
    return {'actor': 0, 'action': {'Fake': inner}, 'is_stack': False}


LEGAL = [act(i) for i in range(6)] + [act(99)]


class FakeLister:
    def __init__(self, forced=(False, False, False), per_plan=False, fail_at=(), reason=('a', 'lister_error'), root=None, trace_ok=True, illegal_first=False,
                 plan_key_override=None, raise_exc=None, hash_fail=False):
        self.pid_case = TC.case()
        _, self.pos, self.rec, self.decks = self.pid_case
        self.forced, self.per_plan, self.fail_at, self.reason, self.root_extra = list(forced), per_plan, set(fail_at), reason, root or {}
        self.trace_ok, self.illegal_first, self.raise_exc, self.hash_fail = trace_ok, illegal_first, raise_exc, hash_fail
        self.pids, self.traces, self.n_list, self.hash_calls = [], [], 0, 0

    def acts(self, n):
        out = [act(i, n if self.per_plan else None) for i in range(len(self.forced))]
        if self.illegal_first:
            out[0] = act(500)
        return out

    def list(self, pid, obs, legal):
        self.n_list += 1
        self.pids.append(pid)
        if self.raise_exc:
            raise self.raise_exc
        if self.n_list in self.fail_at:
            return game_lister.ListResult(False, self.reason, 'x', None, {}, None, None, None, 0.01, 0, '')
        actions = {p['n']: (self.acts(p['n']), list(self.forced)) for p in self.rec['plans']}
        root = {'ok': True, 'n_legal': len(legal), 'n_root': len(legal), 'n_plan': len(legal), 'n_noop': 0, 'n_dup_of': 0, 'n_no_plan': 0, 'missing_in_lister': [], 'extra_in_lister': []}
        root.update(self.root_extra)
        return game_lister.ListResult(True, None, '', self.rec, actions, root, self.pos, {'vmhwm_kb': 1000, 'secs': 0.01}, 0.01, 0, '')

    def trace(self, pid, obs, actions):
        self.traces.append(actions)
        if not self.trace_ok:
            return {'ok': False, 'error': 'bad', 'steps': []}
        return {'ok': True, 'error': None, 'steps': [{'forced': self.forced[i], 'end': 'child', 'actor_after': 0, 'hash_after': 'h_%d' % i} for i in range(len(actions))]}

    def obs_hash(self, pid, obs):
        self.hash_calls += 1
        if self.hash_fail:
            raise game_lister.ListerError('lister_error rc=1')
        return obs['tag']


class FakeShadow:
    def __init__(self, k=0, fail_start=False, fail_new_game=False, fail_ask=False):
        self.k, self.fail_start, self.fail_new_game, self.fail_ask = k, fail_start, fail_new_game, fail_ask
        self.asks, self.closed, self.new_games = [], False, []

    def factory(self, protocol_bot, env, log_path, deal_tag):
        self.env, self.log_path, self.deal_tag = env, log_path, deal_tag
        return self

    def start(self):
        if self.fail_start:
            raise game_shadow.ShadowError('start')

    def new_game(self, line):
        self.new_games.append(line)
        if self.fail_new_game:
            raise game_shadow.ShadowError('new_game')

    def ask(self, line, deadline, n, ply):
        if self.fail_ask:
            raise game_shadow.ShadowError('ask')
        self.asks.append(ply)
        return self.k, 0.5

    def close(self):
        self.closed = True


def hello_line():
    return json.dumps({'type': 'hello', 'protocol': 1})


def new_game_line(deck_file, pad=True):
    c = game_obs.deck_counter(deck_file)
    deck = [k for k, v in c.items() for _ in range(v)]
    return json.dumps({'type': 'new_game', 'game_id': 'g', 'you': 0, 'deck': deck, 'deck_definition': {}})


def decide_line(ply, tc=3, cp=0, actor=0, tag='h_x', since=None, legal=None):
    legal = legal if legal is not None else LEGAL
    s = {'opponent_choices': 0, 'chance_events': 0, 'cards_left_deck_mine': 0, 'cards_left_deck_opponent': 0}
    s.update(since or {})
    obs = {'actor': actor, 'tag': tag, 'template': {'turn_count': tc, 'current_player': cp}}
    return json.dumps({'type': 'decide', 'ply': ply, 'state': {}, 'actions': [{'i': i, 'text': 't', 'action': a['action']} for i, a in enumerate(legal)], 'actor': actor, 'agent_snapshot': None,
                       'legal_actions': legal, 'pdl_observation': obs, 'pdl_search_seed': 1, 'pdl_since_last': s})


class BotBase(unittest.TestCase):
    def setUp(self):
        self.saved = (providers._post_json, providers.load_key, providers._OPENER, providers.call_vertex, providers._VERTEX_PROJECT[0], providers.vertex_project, providers.vertex_url,
                      game_call.install_live, game_call.open_ledger)
        self.name = self.id().split('.')[-1]
        self.dir = os.path.join(TMP, 'bot_' + self.name)
        os.system('rm -rf %s && mkdir -p %s' % (self.dir, self.dir))
        self.clk = TC.Clock()
        _, self.pos, self.rec, self.decks = TC.case()
        self.deck_file = os.path.join(self.decks, self.pos['deck'] + '.txt')

    def tearDown(self):
        (providers._post_json, providers.load_key, providers._OPENER, providers.call_vertex, providers._VERTEX_PROJECT[0], providers.vertex_project, providers.vertex_url,
         game_call.install_live, game_call.open_ledger) = self.saved

    def p(self, n):
        return os.path.join(self.dir, n)

    def argv(self, extra=(), mock_seed='7', live=False, call_cap=None, ledger_total='1000'):
        a = ['--deck-file', self.deck_file, '--plans-bin', 'JP', '--protocol-bot', 'PB', '--pid-prefix', 'P0', '--deal-tag', 'T', '--rows', self.p('rows.jsonl'), '--shadow-log', self.p('sh.jsonl'),
             '--ledger', self.p('ledger.json'), '--ledger-total-usd', ledger_total, '--stop-file', self.p('STOP'), '--bot-timeout-s', '2700']
        if call_cap is not None:
            a += ['--call-cap', str(call_cap)]
        if not live:
            a += ['--mock-judge', 'random', '--mock-seed', mock_seed]
        return a + list(extra)

    def run_bot(self, lines, lister=None, shadow=None, extra=(), environ=None, mock_mode=None, hello=True, ng=True, call_cap=None, live=False):
        lister = lister or FakeLister()
        shadow = shadow or FakeShadow()
        pre = ([hello_line()] if hello else []) + ([new_game_line(self.deck_file)] if ng else [])
        stdin = io.StringIO('\n'.join(pre + list(lines)) + '\n')
        out, err = io.StringIO(), io.StringIO()
        env = {'PATH': '/usr/bin', 'TMPDIR': self.dir}
        env.update(environ or {})
        code = game_bot.main(self.argv(extra, live=live, call_cap=call_cap), stdin=stdin, stdout=out, stderr=err, environ=env, lister=lister, shadow_factory=shadow.factory,
                             clock=self.clk, sleep=self.clk.sleep, mock_mode=mock_mode)
        self.lister, self.shadow, self.err = lister, shadow, err.getvalue()
        self.replies = [json.loads(l) for l in out.getvalue().splitlines() if l.strip()]
        self.rows = self.read(self.p('rows.jsonl'))
        self.decisions = [r for r in self.rows if r.get('schema') == 'gemini_game_decision_v1']
        self.plans = [r for r in self.rows if r.get('schema') == 'gemini_game_plan_v1']
        self.fatal = [r for r in self.rows if 'fatal' in r]
        self.stop = json.load(open(self.p('STOP'))) if os.path.exists(self.p('STOP')) else None
        return code

    @staticmethod
    def read(path):
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [json.loads(l) for l in f if l.strip()]


class Bot(BotBase):
    def test_P1_reask_reason_order(self):
        cr = game_bot.counter_reason
        z = {'opponent_choices': 0, 'chance_events': 0, 'cards_left_deck_mine': 0, 'cards_left_deck_opponent': 0}
        self.assertIsNone(cr(z))
        self.assertEqual(cr(dict(z, chance_events=1, cards_left_deck_opponent=2, opponent_choices=1)), 'opponent_choice')
        self.assertEqual(cr(dict(z, chance_events=1, cards_left_deck_mine=1)), 'chance')
        self.assertEqual(cr(dict(z, cards_left_deck_mine=1, cards_left_deck_opponent=1)), 'draw_mine')
        self.assertEqual(cr(dict(z, cards_left_deck_opponent=1)), 'draw_opponent')
        code = self.run_bot([decide_line(1), decide_line(2, since={'chance_events': 1, 'cards_left_deck_mine': 3})])
        self.assertEqual(code, 0)
        self.assertEqual([d['mode'] for d in self.decisions], ['intervene', 'intervene'])
        self.assertEqual(self.decisions[1]['reask_reason'], 'chance')
        self.assertEqual(self.plans[0]['ended'], 'reask:chance')

    def test_P2_follow_skips_forced(self):
        lister = FakeLister(forced=(False, True, False))
        code = self.run_bot([decide_line(1), decide_line(2, tag='h_1')], lister=lister)
        self.assertEqual(code, 0)
        d1, d2 = self.decisions
        self.assertEqual(d1['mode'], 'intervene')
        self.assertEqual(d2['mode'], 'follow')
        self.assertEqual(d2['follow']['step'], 2)
        self.assertEqual(d2['follow']['skipped_forced'], 1)
        self.assertTrue(d2['follow']['hash_ok'])
        self.assertEqual(self.replies[1:], [{'i': 0}, {'i': 2}])
        self.assertEqual([p['ended'] for p in self.plans], ['completed'])
        self.assertEqual(self.shadow.asks, [])
        self.assertEqual(lister.n_list, 1)

    def test_P3_stale(self):
        lister = FakeLister(forced=(False, True, False))
        code = self.run_bot([decide_line(1), decide_line(2, tag='h_WRONG')], lister=lister)
        self.assertEqual(code, 0)
        d2 = self.decisions[1]
        self.assertEqual((d2['mode'], d2['reask_reason']), ('intervene', 'stale'))
        self.assertEqual(self.plans[0]['ended'], 'stale')
        f = os.path.join(self.dir, 'stale_T_2.json')
        self.assertTrue(os.path.exists(f))
        s = json.load(open(f))
        self.assertEqual(sorted(s), ['c', 'cprime', 'decide', 'plan_id'])
        self.assertEqual((s['c'], s['cprime']), (1, 2))
        self.assertEqual(json.loads(s['decide'])['ply'], 2)
        self.assertEqual(lister.n_list, 2)
        self.assertTrue(any(os.path.exists(os.path.join(self.dir, x)) for x in os.listdir(self.dir) if x.startswith('plan_T_')))

    def test_P12b_obs_hash_lister_error(self):
        lister = FakeLister(forced=(False, True, False), hash_fail=True)
        code = self.run_bot([decide_line(1), decide_line(2, tag='h_1')], lister=lister)
        self.assertEqual(code, 0)
        d1, d2 = self.decisions
        self.assertEqual(d1['mode'], 'intervene')
        self.assertEqual(d2['mode'], 'intervene')
        self.assertEqual((d2['fallback']['reason'], d2['fallback']['detail']), ('a', 'lister_error'))
        self.assertEqual(self.shadow.asks, [2])
        self.assertEqual(d2['n_list_runs'], 0)
        self.assertEqual(lister.n_list, 1)
        self.assertEqual([p['ended'] for p in self.plans], ['reask:lister_error'])
        self.assertEqual(lister.hash_calls, 1)
        self.assertEqual(self.fatal, [])

    def test_P4_fallback_reasons(self):
        cases = [(FakeLister(fail_at={1}, reason=('a', 'lister_error')), {}, 'a', 'lister_error'), (FakeLister(fail_at={1}, reason=('b', 'memory_cap')), {}, 'b', 'memory_cap'),
                 (FakeLister(), {'mock_mode': 'seq:500'}, 'c', 'http_500'), (FakeLister(trace_ok=False), {}, 'a', 'trace_error'),
                 (FakeLister(illegal_first=True), {}, 'a', 'first_step_illegal')]
        for lister, kw, reason, detail in cases:
            os.system('rm -f %s %s* ' % (self.p('rows.jsonl'), self.p('ledger.json')))
            code = self.run_bot([decide_line(1)], lister=lister, **kw)
            self.assertEqual(code, 0, detail)
            fb = self.decisions[0]['fallback']
            self.assertEqual((fb['reason'], fb['detail']), (reason, detail))
            self.assertEqual(self.replies[-1], {'i': 0})
            self.assertEqual(self.shadow.asks, [1])
            self.assertEqual(fb['shadow_i'], 0)
        # (d): the cap
        os.system('rm -f %s %s*' % (self.p('rows.jsonl'), self.p('ledger.json')))
        lister = FakeLister(forced=(False,))
        self.run_bot([decide_line(1), decide_line(2)], lister=lister, call_cap=1)
        self.assertIsNone(self.decisions[0]['fallback'])
        self.assertEqual((self.decisions[1]['fallback']['reason'], self.decisions[1]['fallback']['detail']), ('d', 'call_cap'))
        self.assertEqual(self.shadow.asks, [2])
        self.assertEqual(lister.n_list, 1)
        # the dev fallback
        os.system('rm -f %s %s*' % (self.p('rows.jsonl'), self.p('ledger.json')))
        lister = FakeLister(forced=(False,))
        self.run_bot([decide_line(1), decide_line(2)], lister=lister, extra=['--force-fallback-every', '2'])
        self.assertEqual((self.decisions[1]['fallback']['reason'], self.decisions[1]['fallback']['detail']), ('dev', 'forced_dev'))

    def test_P5_illegal_first_step(self):
        lister = FakeLister(illegal_first=True)
        self.run_bot([decide_line(1)], lister=lister)
        d = self.decisions[0]
        self.assertEqual(d['fallback']['detail'], 'first_step_illegal')
        self.assertEqual((d['n_list_runs'], d['n_judge_calls']), (1, 1))
        self.assertEqual(lister.n_list, 1)
        self.assertEqual(self.shadow.asks, [1])
        self.assertIsNone(d['plan'])

    def test_P6_ledger_stop(self):
        open(self.p('ledger.json.lock'), 'w').close()
        code = self.run_bot([decide_line(1)])
        self.assertEqual(code, 3)
        self.assertEqual(self.stop['reason'], 'ledger')
        self.assertEqual(sorted(self.stop), ['deal_tag', 'detail', 'reason', 'utc'])
        self.assertEqual(len(self.replies), 1)  # the hello reply only: no decide reply

    def test_P6b_ledger_bound(self):
        with mock.patch.object(budget_judge, 'actual_usd', lambda provider, out, worst: 2 * worst + 0.01):
            code = self.run_bot([decide_line(1)], lister=FakeLister(forced=(False,)))
        self.assertEqual(code, 5)
        self.assertEqual(self.stop['reason'], 'ledger_bound')
        self.assertEqual(len(self.fatal), 1)
        self.assertEqual(self.fatal[0]['fatal'], 'LedgerBound')
        self.assertEqual(len(self.fatal[0]['tries']), 1)
        self.assertEqual(len(self.replies), 1)  # the hello reply only
        self.assertFalse(os.path.exists(self.p('ledger.json.lock')))

    def test_P7_kinds_and_setup(self):
        lines = [decide_line(1, tc=0, cp=0), decide_line(2, tc=0, cp=0), decide_line(3, tc=3, cp=0), decide_line(4, tc=3, cp=1, tag='h_other')]
        lister = FakeLister(forced=(False,))
        code = self.run_bot(lines, lister=lister)
        self.assertEqual(code, 0)
        self.assertEqual([d['kind'] for d in self.decisions], ['setup', 'setup', 'own_turn', 'opponent_turn'])
        s = self.decisions[0]
        self.assertEqual((s['mode'], s['lister'], s['judge'], s['plan'], s['fallback'], s['tries']), ('setup', None, None, None, None, []))
        self.assertEqual(lister.n_list, 2)
        self.assertEqual(self.shadow.asks, [1, 2])
        self.assertEqual(self.decisions[2]['reask_reason'], 'first')
        self.assertEqual(self.decisions[3]['reask_reason'], 'plan_done')
        self.assertEqual(self.decisions[2]['calls_this_game'], 1)

    def test_P8_pid_scheme(self):
        lister = FakeLister(forced=(False,))
        self.run_bot([decide_line(7), decide_line(9)], lister=lister)
        self.assertEqual(lister.pids, ['P0-p7', 'P0-p9'])

    def test_P9_live_start_no_key(self):
        real_open = builtins.open

        def guarded(path, *a, **k):
            if str(path).endswith('rc'):
                raise AssertionError('the shell rc file was opened')
            return real_open(path, *a, **k)
        with mock.patch.object(builtins, 'open', guarded):
            code = self.run_bot([decide_line(1)], live=True, hello=True)
        self.assertEqual(code, 2)
        self.assertEqual(self.stop['reason'], 'no_key_env')
        self.assertEqual(self.replies, [])

    def test_P9_env_stops(self):
        code = self.run_bot([decide_line(1)], environ={'PDL_DB': 'x'})
        self.assertEqual((code, self.stop['reason']), (2, 'env'))
        code = self.run_bot([decide_line(1)], environ={'VERTEX_PROJECT': 'x'})
        self.assertEqual((code, self.stop['reason']), (2, 'env'))
        code = game_bot.main(self.argv(['--force-fallback-every', '2'], live=True), stdin=io.StringIO(''), stdout=io.StringIO(), stderr=io.StringIO(), environ={})
        self.assertEqual(code, 2)

    def test_P10_no_keys_in_rows_or_stderr(self):
        shaped = 'AI' + 'za' + 'x' * 30
        lister = FakeLister(raise_exc=RuntimeError('boom ' + shaped))
        code = self.run_bot([decide_line(1)], lister=lister)
        self.assertEqual(code, 5)
        self.assertEqual(self.fatal[0]['fatal'], 'RuntimeError')
        text = open(self.p('rows.jsonl')).read()
        for r in KEY_RES:
            self.assertIsNone(r.search(text))
            self.assertIsNone(r.search(self.err))
        self.assertTrue('***' in text or '[redacted]' in text)
        self.assertIsNone(self.stop)
        self.assertEqual(game_bot.scrub_row({'a': ['x' + shaped, {'b': 'AQ' + '.' + 'y' * 30}]}, 'MOCK-KEY'), {'a': ['x***', {'b': '***'}]})

    def _no_cut_key(self, *texts):
        for t in texts:
            self.assertNotIn('AI' + 'za', t)
            self.assertNotIn('AQ' + '.', t)

    def _all_text(self):
        parts = [self.err]
        for n in ('rows.jsonl', 'STOP'):
            if os.path.exists(self.p(n)):
                parts.append(open(self.p(n)).read())
        return parts

    def test_P10b_scrub_before_cut(self):
        text = 'x' * 290 + 'AI' + 'za' + 'y' * 30
        # (i) the lister raises
        code = self.run_bot([decide_line(1)], lister=FakeLister(raise_exc=RuntimeError(text)))
        self.assertEqual(code, 5)
        self.assertEqual(self.fatal[0]['fatal'], 'RuntimeError')
        self._no_cut_key(*self._all_text())
        # (ii) the shadow fails to start
        os.system('rm -f %s %s' % (self.p('rows.jsonl'), self.p('STOP')))

        class BadShadow(FakeShadow):
            def start(self):
                raise game_shadow.ShadowError(text)
        code = self.run_bot([decide_line(1)], shadow=BadShadow())
        self.assertEqual(code, 4)
        self.assertEqual(self.fatal[0]['fatal'], 'shadow')
        self._no_cut_key(*self._all_text())
        # (iii) the ledger open raises SystemExit
        os.system('rm -f %s %s' % (self.p('rows.jsonl'), self.p('STOP')))
        with mock.patch.object(game_call, 'GameLedger', side_effect=SystemExit(text)):
            with self.assertRaises(game_call.LedgerStop) as cm:
                game_call.open_ledger(self.p('l2.json'), 10)
            self._no_cut_key(str(cm.exception))
            code = self.run_bot([decide_line(1)])
        self.assertEqual((code, self.stop['reason']), (3, 'ledger'))
        self._no_cut_key(*self._all_text())
        # (iv) open_ledger raises LedgerStop directly
        os.system('rm -f %s %s' % (self.p('rows.jsonl'), self.p('STOP')))
        with mock.patch.object(game_call, 'open_ledger', side_effect=game_call.LedgerStop(text)):
            code = self.run_bot([decide_line(1)])
        self.assertEqual((code, self.stop['reason']), (3, 'ledger'))
        self._no_cut_key(*self._all_text())

    def _cap_run(self, fail_at, n_lines):
        lister = FakeLister(forced=(False,), fail_at=fail_at)
        mode = 'seq:' + ','.join(['429', 'ok'] * 75)
        self.run_bot([decide_line(i + 1) for i in range(n_lines)], lister=lister, mock_mode=mode, call_cap=75)
        return lister

    def test_P11_call_cap(self):
        lister = self._cap_run(set(), 76)
        self.assertEqual(len(self.decisions), 76)
        self.assertTrue(all(d['fallback'] is None for d in self.decisions[:75]))
        self.assertEqual(self.decisions[74]['calls_this_game'], 75)
        self.assertEqual(self.decisions[74]['tries_this_game'], 150)
        last = self.decisions[75]
        self.assertEqual((last['fallback']['reason'], last['fallback']['detail']), ('d', 'call_cap'))
        self.assertEqual((last['n_list_runs'], last['n_judge_calls']), (0, 0))
        self.assertEqual(lister.n_list, 75)

    def test_P11_call_cap_after_lister_failures(self):
        lister = self._cap_run({2, 5, 9}, 79)
        self.assertEqual(len(self.decisions), 79)
        fb = [(i, d['fallback']['detail']) for i, d in enumerate(self.decisions) if d['fallback']]
        self.assertEqual(fb, [(1, 'lister_error'), (4, 'lister_error'), (8, 'lister_error'), (78, 'call_cap')])
        self.assertEqual(self.decisions[77]['calls_this_game'], 75)
        self.assertEqual(lister.n_list, 78)

    def test_P12_one_step_and_forced_tail(self):
        for forced in ((False,), (False, True, True)):
            os.system('rm -f %s %s*' % (self.p('rows.jsonl'), self.p('ledger.json')))
            self.run_bot([decide_line(1)], lister=FakeLister(forced=forced))
            self.assertEqual([p['ended'] for p in self.plans], ['completed'], forced)
            self.assertEqual(self.plans[0]['n_steps'], len(forced))
            self.assertEqual(self.plans[0]['steps_played'], len(forced))

    def test_P13_dup_of_noop_accepted(self):
        lister = FakeLister(forced=(False,), root={'n_dup_of': 2, 'n_noop': 1})
        self.run_bot([decide_line(1)], lister=lister)
        d = self.decisions[0]
        self.assertIsNone(d['fallback'])
        self.assertEqual((d['root_check']['n_dup_of'], d['root_check']['n_noop'], d['root_check']['ok']), (2, 1, True))

    def test_P14_deck_check(self):
        deck = self.p('deck.txt')
        with open(deck, 'w') as f:
            f.write('Pokemon: 2\n2 Foo A1 5\n18 Bar B2a 12\n')
        self.deck_file = deck
        padded = ['A1 005'] * 2 + ['B2a 012'] * 18
        ng = json.dumps({'type': 'new_game', 'game_id': 'g', 'you': 0, 'deck': padded, 'deck_definition': {}})
        stdin = io.StringIO('\n'.join([hello_line(), ng]) + '\n')
        out = io.StringIO()
        code = game_bot.main(self.argv(), stdin=stdin, stdout=out, stderr=io.StringIO(), environ={'TMPDIR': self.dir}, lister=FakeLister(), shadow_factory=FakeShadow().factory,
                             clock=self.clk, sleep=self.clk.sleep)
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(self.p('STOP')))
        bad = json.dumps({'type': 'new_game', 'game_id': 'g', 'you': 0, 'deck': padded[1:] + ['C1 001'], 'deck_definition': {}})
        stdin = io.StringIO('\n'.join([hello_line(), bad]) + '\n')
        code = game_bot.main(self.argv(), stdin=stdin, stdout=io.StringIO(), stderr=io.StringIO(), environ={'TMPDIR': self.dir}, lister=FakeLister(), shadow_factory=FakeShadow().factory,
                             clock=self.clk, sleep=self.clk.sleep)
        self.assertEqual(code, 6)
        self.assertEqual(json.load(open(self.p('STOP')))['reason'], 'deck')

    def test_P15_call_not_sent(self):
        with mock.patch.object(providers, 'vertex_url', side_effect=SystemExit('x')):
            code = self.run_bot([decide_line(1)])
        self.assertEqual(code, 5)
        self.assertEqual(self.fatal[0]['fatal'], 'CallNotSent')
        self.assertEqual(self.stop['reason'], 'not_sent')

    def test_P16_live_429_classified(self):
        calls = []

        def post(url, headers, body, timeout):
            calls.append(1)
            raise urllib.error.HTTPError(url, 429, 'Too Many Requests', None, io.BytesIO(b'{"error":{"code":429}}'))
        providers._post_json = post
        providers.load_key = lambda *a, **k: 'k'
        providers.vertex_project = lambda *a, **k: 'mock-project-0'
        game_call.install_live = lambda: None
        code = self.run_bot([decide_line(1)], live=True)
        self.assertEqual(code, 0)
        d = self.decisions[0]
        self.assertEqual((d['fallback']['reason'], d['fallback']['detail']), ('c', 'http_429'))
        self.assertEqual(len(d['tries']), 3)
        self.assertTrue(all(t['outcome'] == 'http_429' and t['charged_usd'] == 0.0 and t['http_status'] == 429 for t in d['tries']))
        self.assertEqual(len(calls), 3)
        self.assertIsNone(self.stop)
        self.assertEqual(self.fatal, [])

    def test_P17_shown_vs_plan_number(self):
        lister = FakeLister(forced=(False,), per_plan=True)
        legal = LEGAL + [act(0, p['n']) for p in lister.rec['plans']]
        lines = [decide_line(i, legal=legal) for i in range(1, 41)]
        self.run_bot(lines, lister=lister)
        by_n = {p['n']: p for p in lister.rec['plans']}
        differ = 0
        for d, tr in zip(self.decisions, lister.traces):
            j = d['judge']
            if j['shown_number'] != j['plan_number']:
                differ += 1
            self.assertEqual(d['plan']['key'], j['plan_key'])
            self.assertEqual(by_n[j['plan_number']]['key'], j['plan_key'])
            self.assertEqual(tr, lister.acts(j['plan_number']))
        self.assertGreater(differ, 0)

    def test_P18_shadow_failures(self):
        code = self.run_bot([decide_line(1)], shadow=FakeShadow(fail_start=True))
        self.assertEqual(code, 4)
        self.assertEqual(self.replies, [])
        self.assertEqual([f['fatal'] for f in self.fatal], ['shadow'])
        self.assertIsNone(self.stop)
        os.system('rm -f %s' % self.p('rows.jsonl'))
        code = self.run_bot([decide_line(1)], shadow=FakeShadow(fail_new_game=True))
        self.assertEqual(code, 4)
        self.assertEqual([f['fatal'] for f in self.fatal], ['shadow'])
        self.assertIsNone(self.stop)
        os.system('rm -f %s' % self.p('rows.jsonl'))
        code = self.run_bot([decide_line(1, tc=0)], shadow=FakeShadow(fail_ask=True))
        self.assertEqual(code, 4)
        self.assertEqual([f['fatal'] for f in self.fatal], ['shadow'])


if __name__ == '__main__':
    unittest.main()
