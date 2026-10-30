import contextlib
import datetime
import io
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
import game_kit  # noqa: E402
import game_runner as gr  # noqa: E402
import providers  # noqa: E402

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


FAKE_DG = r'''#!/usr/bin/env python3
import json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.realpath(__file__))
args = sys.argv[1:]
flags = {}
i = 3
while i < len(args):
    if args[i].startswith('--'):
        flags[args[i]] = args[i + 1]
        i += 2
    else:
        i += 1
arm_dir = os.path.dirname(flags['--results-output'].rstrip('/'))
key = '/'.join(arm_dir.split('/')[-3:])
sc_all = json.load(open(os.path.join(HERE, 'scenario.json')))
sc = dict(sc_all.get('default', {}))
sc.update(sc_all.get(key, {}))
json.dump(args, open(os.path.join(arm_dir, 'argv.json'), 'w'))
if sc.get('pidfile'):
    json.dump({'pid': os.getpid(), 'sid': os.getsid(0)}, open(sc['pidfile'], 'w'))
def cmd_arg(name):
    for f in ('--bot-a', '--bot-b'):
        m = re.search(name + r' (\S+)', flags.get(f, ''))
        if m:
            return m.group(1)
if sc.get('sigkill_self'):
    os.kill(os.getpid(), signal.SIGKILL)
os.makedirs(flags['--bot-log'], exist_ok=True)
inst = 0
for seat, f in ((0, '--bot-a'), (1, '--bot-b')):
    if f in flags:
        lines = [{'instance': inst, 'ply': 1, 'secs': 1.5, 'startup_secs': 0.2, 'fallback': False, 'error': None}]
        fb = sc.get('fallbacks', {}).get(str(seat), 0)
        lines.append({'summary': True, 'decisions': 1, 'fallbacks': fb, 'errors': sc.get('errors', {}).get(str(seat), 0), 'child_pid': 1})
        with open(os.path.join(flags['--bot-log'], 'protocol_%d_%d.jsonl' % (os.getpid(), inst)), 'w') as fh:
            for l in lines:
                fh.write(json.dumps(l) + '\n')
        inst += 1
if 'rows' in sc and cmd_arg('--rows'):
    with open(cmd_arg('--rows'), 'w') as fh:
        for r in sc['rows']:
            fh.write(json.dumps(r) + '\n')
if 'stop' in sc:
    json.dump({'reason': sc['stop'], 'detail': 'x', 'deal_tag': 't', 'utc': 'u'}, open(cmd_arg('--stop-file'), 'w'))
if sc.get('lock'):
    open(cmd_arg('--ledger') + '.lock', 'w').close()
if sc.get('orphan'):
    ch = subprocess.Popen([sys.executable, '-c', 'import signal,time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\nsignal.signal(signal.SIGHUP, signal.SIG_IGN)\ntime.sleep(600)'], preexec_fn=os.setpgrp)
    open(os.path.join(arm_dir, 'orphan.pid'), 'w').write(str(ch.pid))
if sc.get('sleep'):
    time.sleep(sc['sleep'])
for ln in sc.get('stderr', []):
    sys.stderr.write(ln + '\n')
    sys.stderr.flush()
if not sc.get('no_result'):
    os.makedirs(flags['--results-output'], exist_ok=True)
    json.dump({'schema': 'pdl-game-result/v1', 'game_id': 'x', 'completion': sc.get('completion', 'completed'), 'lifecycle_errors': sc.get('lifecycle_errors', []), 'plies': 10, 'final_turn': 7,
               'outcome': {'Win': 0}, 'state_winner': 0, 'final_points': [3, 1]}, open(os.path.join(flags['--results-output'], 'game_x.json'), 'w'))
sys.exit(sc.get('exit', 0))
'''


def dec_row(tag, tc=3, cp=0, mode='intervene', plan_id=None, model='m1', fallback=None, **kw):
    r = {'schema': 'gemini_game_decision_v1', 'deal_tag': tag, 'ply': 1, 'actor': 0, 'turn_count': tc, 'current_player': cp, 'kind': 'own_turn', 'mode': mode, 'reask_reason': 'first',
         'n_judge_calls': 1, 'tries': [{'outcome': 'ok', 'charged_usd': 0.1}], 'ledger_charge_usd': 0.1, 'fallback': fallback, 'root_check': {'n_dup_of': 0, 'n_noop': 0},
         'judge': {'model_returned': model, 'frozen': True, 'mock': True, 'plan_number': 1, 'cost': {'usd': 0.05}, 'vertex_project': 'p-12345'},
         'plan': {'plan_id': plan_id, 'n_steps': 2} if plan_id else None}
    r.update(kw)
    return r


class Clock:
    def __init__(self, mono_step=5, wall_step=5, schedule=None, on_call=None):
        self.m, self.w, self.n = 1000.0, 1.7e9, 0
        self.mono_step, self.wall_step, self.schedule, self.on_call = mono_step, wall_step, schedule or {}, on_call

    def mono(self):
        return self.m

    def wall(self):
        return self.w

    def sleep(self, s):
        self.n += 1
        time.sleep(0.02)
        if self.on_call:
            self.on_call(self.n)
        dm, dw = self.schedule.get(self.n, (self.mono_step, self.wall_step))
        self.m += dm
        self.w += dw


class Env:
    def __init__(self, name, scenario=None):
        self.root = os.path.join(TMP, 'r_' + name)
        subprocess.run(['rm', '-rf', self.root])
        self.eng, self.jb, self.repo, self.D = (os.path.join(self.root, x) for x in ('eng', 'jb', 'repo', 'run'))
        for d in (self.eng, self.jb, self.repo):
            os.makedirs(d)
        with open(os.path.join(self.eng, 'deckgym'), 'w') as f:
            f.write(FAKE_DG)
        os.chmod(os.path.join(self.eng, 'deckgym'), 0o755)
        self.scenario(scenario or {})
        self.ledger = os.path.join(self.root, 'ledger.json')
        self.plan_path = os.path.join(self.root, 'plan.json')
        self.env = {'PATH': os.environ['PATH'], 'HOME': os.environ.get('HOME', '/'), 'TMPDIR': TMP, 'RAYON_NUM_THREADS': '2'}

    def scenario(self, sc):
        with open(os.path.join(self.eng, 'scenario.json'), 'w') as f:
            json.dump(sc, f)

    def plan(self, stage='dev', k='90', cells='0,1'):
        argv = ['plan', '--stage', stage, '--cells', cells, '--out', self.plan_path] + (['--k', k] if k else [])
        return gr.main(argv)

    def argv(self, extra=(), stage='dev', mock=True):
        a = ['run', '--plan', self.plan_path, '--run-dir', self.D, '--repo', self.repo, '--engine-bins', self.eng, '--judge-bins', self.jb, '--ledger', self.ledger, '--ledger-total-usd', '1000',
             '--stage', stage]
        if mock:
            a += ['--mock-judge', 'random', '--mock-seed', '7']
        return a + list(extra)

    def run(self, extra=(), clock=None, stage='dev', mock=True, utcnow=None, environ=None):
        clock = clock or Clock()
        buf = io.StringIO()
        kw = {}
        if utcnow:
            kw['utcnow'] = utcnow
        with contextlib.redirect_stdout(buf):
            rc = gr.main(self.argv(extra, stage, mock), environ=environ or self.env, mono=clock.mono, wall=clock.wall, sleep=clock.sleep, **kw)
        self.out = buf.getvalue()
        return rc

    def jl(self, name):
        return gr.read_jsonl(os.path.join(self.D, name))

    def end(self):
        return json.load(open(os.path.join(self.D, 'run_end.json')))


def ns_for(env, extra=(), stage='dev', mock=True):
    a = gr.build_parser().parse_args(env.argv(extra, stage, mock))
    a.call_cap_given = a.call_cap is not None
    if a.call_cap is None:
        a.call_cap = game_kit.CALL_CAP
    return a


class Runner(unittest.TestCase):
    def test_R1_seats_and_commands(self):
        e = Env('r1')
        r = gr.Runner(ns_for(e), environ=e.env)
        for cell in range(16):
            bits = game_kit.cell_bits(cell)
            deal = gr.build_plan('dev', [90], [cell])[0]
            for arm in ('G', 'K'):
                tag = r.tag(deal, 1, arm)
                argv, seats, proto = r.arm_argv(deal, arm, tag, '/x/arm')
                a = {argv[i]: argv[i + 1] for i in range(len(argv)) if argv[i].startswith('--')}
                pilot_deck, opp = os.path.join(e.repo, game_kit.DECKS[bits['deck']]), os.path.join(e.repo, game_kit.LISTS[bits['list']])
                deck_a, deck_b = argv[argv.index('simulate') + 1], argv[argv.index('simulate') + 2]
                self.assertEqual((deck_a, deck_b), (pilot_deck, opp) if bits['seat'] == 0 else (opp, pilot_deck), (cell, arm))
                codes = a['--players'].split(',')
                self.assertEqual(codes[bits['seat']], 'proto')
                self.assertEqual(codes[1 - bits['seat']], 'km3' if bits['policy'] == 0 else 'proto')
                flags = {0: a.get('--bot-a'), 1: a.get('--bot-b')}
                pc = flags[bits['seat']]
                if arm == 'G':
                    self.assertIn('game_bot.py', pc)
                    self.assertIn('--pid-prefix ' + game_kit.pid_prefix(deal['seed'], cell, 'G'), pc)
                    self.assertIn('--mock-judge random', pc)
                else:
                    self.assertIn('env -u VERTEX_API_KEY -u VERTEX_PROJECT', pc)
                    self.assertTrue(pc.endswith('--bot kx3'))
                if bits['policy'] == 1:
                    self.assertIn('--bot kx3', flags[1 - bits['seat']])
                    self.assertIn('-u VERTEX_API_KEY', flags[1 - bits['seat']])
                else:
                    self.assertIsNone(flags[1 - bits['seat']])
                self.assertEqual((a['--bot-timeout-ms'], a['--num'], a['--seed']), ('2700000', '1', str(game_kit.seed(cell, 90))))
                self.assertEqual(argv[:3], ['nice', '-n', '19'])
                self.assertEqual(seats[bits['seat']], 'pilot')

    def test_R2_no_vertex_in_env(self):
        e = Env('r2')
        parent = {'PATH': '/usr/bin', 'HOME': '/h', 'LANG': 'C', 'TMPDIR': '/t', 'RAYON_NUM_THREADS': '2', 'VERTEX_API_KEY': 'fake' + '-' * 3 + '0' * 24, 'VERTEX_PROJECT': 'proj-12345', 'PDL_DB': 'x'}
        r = gr.Runner(ns_for(e), environ=parent)
        for arm in ('G', 'K'):
            env = r.dg_env(arm)
            self.assertFalse([k for k in env if k.startswith('VERTEX_') or k == 'PDL_DB'])
            self.assertEqual(sorted(env), sorted(k for k in game_kit.SHADOW_ENV_KEEP if k in parent))
        live = gr.Runner(ns_for(e, stage='dev', mock=False), environ=parent)
        self.assertIn('VERTEX_API_KEY', live.dg_env('G'))
        self.assertNotIn('VERTEX_API_KEY', live.dg_env('K'))
        self.assertIn('-u VERTEX_API_KEY -u VERTEX_PROJECT', live.kx3_cmd())

    def test_R3_plan_and_refusals(self):
        e = Env('r3')
        self.assertEqual(e.plan('1', '80', '0-15'), 0)
        d = json.load(open(e.plan_path))
        self.assertEqual([x['cell'] for x in d['deals']], list(game_kit.STAGE1_ORDER))
        self.assertEqual(d['stage'], 1)
        self.assertEqual(d['deals'][0]['seed'], game_kit.seed(0, 80))
        self.assertEqual(sorted(d['deals'][0]), ['bits', 'cell', 'deal_idx', 'k', 'opp_list', 'pilot_deck', 'policy', 'seat', 'seed'])
        self.assertEqual(e.plan('2', None, '0,3-4'), 2)
        self.assertEqual(gr.main(['plan', '--stage', '2', '--k-range', '0-1', '--cells', '0,3-4', '--out', e.plan_path]), 0)
        d = json.load(open(e.plan_path))
        self.assertEqual([(x['k'], x['cell']) for x in d['deals']], [(0, 0), (0, 3), (0, 4), (1, 0), (1, 3), (1, 4)])
        self.assertEqual(gr.main(['plan', '--stage', '2', '--k-list', '0,2', '--out', e.plan_path]), 2)
        self.assertEqual(gr.main(['plan', '--stage', '2', '--k-range', '0-8', '--out', e.plan_path]), 2)
        self.assertEqual(gr.main(['plan', '--stage', '1', '--k', '79', '--out', e.plan_path]), 2)
        self.assertEqual(gr.main(['plan', '--stage', '1', '--k', '85', '--out', e.plan_path]), 0)
        self.assertEqual(gr.main(['plan', '--stage', 'dev', '--k', '89', '--out', e.plan_path]), 2)
        # run refusals
        e.plan('dev', '90', '0')
        base = ['--stage', 'dev']
        for stage, extra, mock in (('1', [], True), ('2', [], True), ('dev', [], True)):
            pass
        self.assertEqual(e.run(stage='2'), 2)  # the plan is a dev plan
        e.plan('1', '80', '0')
        self.assertEqual(e.run(stage='1', mock=True), 2)
        self.assertEqual(e.run(['--force-fallback-every', '2'], stage='1', mock=False), 2)
        self.assertEqual(e.run(['--arms', 'G'], stage='1', mock=False), 2)
        gr.main(['plan', '--stage', '2', '--k', '0', '--cells', '0', '--out', e.plan_path])
        for extra in ([], ['--call-cap', '10'], ['--call-cap', '10', '--stage1-max-game-charge', '1'], ['--stage1-max-game-charge', '1', '--expect-model-version', 'm']):
            self.assertEqual(e.run(extra, stage='2', mock=False), 2, extra)
        e.plan('dev', '90', '0')
        self.assertEqual(e.run(['--force-fallback-every', '2'], mock=False), 2)

    def test_R4_resume(self):
        e = Env('r4')
        e.plan('dev', '90', '0,1')
        self.assertEqual(e.run(['--arms', 'G', '--max-deals', '1']), 0)
        self.assertEqual(len(e.jl('games.jsonl')), 1)
        self.assertEqual(e.run(['--arms', 'G']), 2)  # a folder with deals needs --resume
        self.assertEqual(e.run(['--arms', 'G', '--resume']), 0)
        g = e.jl('games.jsonl')
        self.assertEqual([x['deal_tag'] for x in g], ['0000-k90-c00-a1-G', '0001-k90-c01-a1-G'])
        self.assertEqual(e.end()['complete_deals'], 2)

    def test_R5_headroom(self):
        self.assertTrue(gr.headroom_ok(1, 10, 0, 0, 1))
        self.assertTrue(gr.headroom_ok(1, 10, 4, 0, 1))
        self.assertFalse(gr.headroom_ok(1, 10, 6.5, 0, 1))
        self.assertFalse(gr.headroom_ok(1, 10, 5, 2, 1))
        self.assertTrue(gr.headroom_ok(2, 10, 0, 0, 9, 5))
        self.assertFalse(gr.headroom_ok(2, 10, 1, 0, 0, 5))

    def test_R6_rows_outcome_blind_and_status(self):
        e = Env('r6')
        e.plan('dev', '90', '0')
        self.assertEqual(e.run(['--arms', 'G,K']), 0)
        text = open(os.path.join(e.D, 'games.jsonl')).read() + open(os.path.join(e.D, 'deals.jsonl')).read()
        for w in ('"outcome"', 'state_winner', 'final_points'):
            self.assertNotIn(w, text)
        real_open = open

        def guarded(path, *a, **k):
            if 'result/' in str(path) or str(path).endswith('/result'):
                raise AssertionError('a result file was opened: ' + str(path))
            return real_open(path, *a, **k)
        buf = io.StringIO()
        with mock.patch('builtins.open', guarded), contextlib.redirect_stdout(buf):
            self.assertEqual(gr.main(['status', '--run-dir', e.D]), 0)
        self.assertIn('deals complete 1 of 1', buf.getvalue())
        self.assertIn('failures by class: {}', buf.getvalue())

    def _arm(self, name, scenario, cell='0', extra=('--arms', 'G,K'), stage='dev', use_mock=True, plan_k='90'):
        e = Env(name, scenario)
        e.plan(stage, plan_k, cell)
        with mock.patch.object(gr, 'live_start_checks', lambda r: None):
            e.run(list(extra), stage=stage, mock=use_mock)
        return e, {(g['arm'], g['attempt']): g for g in e.jl('games.jsonl')}

    def test_R6_stderr_tail_outcome_blind(self):
        scen = {'0000-k90-c00/a1/G': {'fallbacks': {'0': 1}, 'stderr': ['Ran 1 simulations in 1s (1s per game)!', 'Average number of turns per game: 7.00', 'Player 0 won: 1 (100.00%)',
                                                                      'Player 1 won: 0 (0.00%)', 'Draws: 0 (0.00%)']},
                '0000-k90-c00/a1/K': {'fallbacks': {'0': 1}, 'stderr': ['Average number of turns per game: 7.00', 'the winner is player 0']}}
        e, a = self._arm('r6c1', scen)
        g, k = a[('G', 1)], a[('K', 1)]
        self.assertEqual(g['failure'], 'pilot_side')
        self.assertEqual(g['stderr_tail'].strip(), 'Average number of turns per game: 7.00')
        self.assertEqual(k['failure'], 'kx3_route')
        self.assertEqual(k['stderr_tail'], '[withheld: outcome-like text]')
        text = open(os.path.join(e.D, 'games.jsonl')).read()
        for w in ('won:', 'Draws:', 'winner', 'simulations'):
            self.assertNotIn(w, text)

    def test_R7_classification(self):
        e, a = self._arm('r7a', {'default': {'exit': 2}})
        self.assertEqual(a[('G', 1)]['failure'], 'config')
        self.assertEqual(e.end()['stop_reason'], 'config')
        self.assertEqual(len(a), 1)
        # K pilot seat (cell 0: pilot seat 0, km3 opponent)
        e, a = self._arm('r7b', {'0000-k90-c00/a1/K': {'fallbacks': {'0': 1}}})
        self.assertEqual((a[('K', 1)]['failure'], a[('K', 1)]['failure_detail']), ('kx3_route', 'K:pilot'))
        self.assertTrue(e.jl('deals.jsonl')[0]['dropped'])
        # kx3 opponent seat (cell 2: seat 0, kx3 opponent in seat 1), G arm and K arm
        e, a = self._arm('r7c', {'0000-k90-c02/a1/G': {'fallbacks': {'1': 1}}}, cell='2')
        self.assertEqual((a[('G', 1)]['failure'], a[('G', 1)]['failure_detail']), ('kx3_route', 'G:opponent'))
        e, a = self._arm('r7d', {'0000-k90-c02/a1/K': {'fallbacks': {'1': 2}}}, cell='2')
        self.assertEqual((a[('K', 1)]['failure'], a[('K', 1)]['failure_detail']), ('kx3_route', 'K:opponent'))
        # g_shadow: rows hold a shadow fatal row (bot exit 4)
        e, a = self._arm('r7e', {'0000-k90-c00/a1/G': {'rows': [dec_row('t'), {'fatal': 'shadow', 'detail': 'x'}]}})
        self.assertEqual((a[('G', 1)]['failure'], a[('G', 1)]['failure_detail']), ('kx3_route', 'g_shadow'))
        # only row is the shadow fatal and the pilot seat shows fallbacks: g_shadow, not pilot_side
        e, a = self._arm('r7f', {'0000-k90-c00/a1/G': {'rows': [{'fatal': 'shadow', 'detail': 'x'}], 'fallbacks': {'0': 1}}})
        self.assertEqual((a[('G', 1)]['failure'], a[('G', 1)]['failure_detail']), ('kx3_route', 'g_shadow'))
        # pilot_side: the G pilot seat only
        e, a = self._arm('r7g', {'0000-k90-c00/a1/G': {'fallbacks': {'0': 1}}})
        self.assertEqual(a[('G', 1)]['failure'], 'pilot_side')
        self.assertFalse(e.jl('deals.jsonl')[0]['dropped'])
        e, a = self._arm('r7h', {'0000-k90-c00/a1/G': {'exit': 101}})
        self.assertEqual(a[('G', 1)]['failure'], 'engine_error')
        e, a = self._arm('r7i', {'0000-k90-c00/a1/K': {'completion': 'incomplete'}})
        self.assertEqual(a[('K', 1)]['failure'], 'engine_error')

    def test_R8_scan_keys(self):
        d = os.path.join(TMP, 'r8')
        os.makedirs(d, exist_ok=True)
        literal = 'zz' + 'q' * 20 + '-literal'
        shaped = 'AI' + 'za' + 'x' * 30
        with open(os.path.join(d, 'a.txt'), 'w') as f:
            f.write('nothing\nhere is ' + literal + ' ok\n')
        with open(os.path.join(d, 'b.txt'), 'w') as f:
            f.write('x\ny\nkey=' + shaped + '\n')
        with open(os.path.join(d, 'c.txt'), 'w') as f:
            f.write('clean line\n')
        hits = gr.scan_paths([d], literal)
        self.assertEqual(sorted((os.path.basename(f), n) for f, n in hits), [('a.txt', 2), ('b.txt', 3)])
        self.assertEqual(gr.scan_paths([d]), [(os.path.join(d, 'b.txt'), 3)])
        buf = io.StringIO()
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': literal}), contextlib.redirect_stdout(buf):
            rc = gr.main(['scan-keys', d])
        self.assertEqual(rc, 1)
        self.assertNotIn(literal, buf.getvalue())
        self.assertNotIn(shaped, buf.getvalue())
        self.assertIn('a.txt', buf.getvalue())
        # no committed file of this job holds a key-shaped string
        mine = [os.path.join(AIJ, n) for n in os.listdir(AIJ) if n.startswith('game_') and n.endswith('.py')] + [os.path.join(HERE, n) for n in os.listdir(HERE) if n.startswith('test_game_') or n == 'test_freeze8.py']
        self.assertEqual(gr.scan_paths(mine), [])

    def test_R9_session_kill_then_lock(self):
        e = Env('r9', {'default': {'orphan': True, 'lock': True, 'pidfile': None}})
        e.plan('dev', '90', '0')
        seen = []
        real = gr.kill_session

        def spy(sid, *a):
            seen.append(os.path.exists(e.ledger + '.lock'))
            return real(sid, *a)
        with mock.patch.object(gr, 'kill_session', spy):
            e.run(['--arms', 'G'])
        g = e.jl('games.jsonl')[0]
        self.assertEqual(seen[0], True)  # the lock was still there when the session kill ran
        self.assertTrue(g['ledger_lock_removed'])
        self.assertFalse(os.path.exists(e.ledger + '.lock'))
        arm_dir = os.path.join(e.D, 'deals', '0000-k90-c00', 'a1', 'G')
        pid = int(open(os.path.join(arm_dir, 'orphan.pid')).read())
        t0 = time.time()
        while time.time() - t0 < 30 and gr.sid_of(pid)[1] not in (None, 'Z'):
            time.sleep(0.2)
        self.assertIn(gr.sid_of(pid)[1], (None, 'Z'))

    def test_R10_pause_to_infra(self):
        sc = {'default': {'sleep': 0.6}}
        for kind, step, infra in (('mono', 66, True), ('wall', 66, True), ('mono', 64, False), ('wall', 64, False)):
            e = Env('r10_%s_%d' % (kind, step), sc)
            e.plan('dev', '90', '0')
            sched = {2: (step, 5) if kind == 'mono' else (5, step)}
            e.run(['--arms', 'G', '--max-deals', '1'], clock=Clock(schedule=sched))
            g = e.jl('games.jsonl')
            if infra:
                self.assertEqual([(x['attempt'], x['failure']) for x in g], [(1, 'infra'), (2, None)], (kind, step))
                self.assertIn('pause_gap', g[0]['failure_detail'])
                self.assertEqual(g[0]['exit_code'], -9)
                self.assertEqual(e.jl('deals.jsonl')[0]['complete'], False)
            else:
                self.assertEqual([(x['attempt'], x['failure']) for x in g], [(1, None)])
        # the pause marker
        e = Env('r10_marker', sc)
        e.plan('dev', '90', '0')

        def hook(n):
            if n == 2:
                open(os.path.join(e.D, 'PAUSE'), 'w').close()
            if n == 3:
                os.remove(os.path.join(e.D, 'PAUSE'))
        e.run(['--arms', 'G', '--max-deals', '1'], clock=Clock(on_call=hook))
        g = e.jl('games.jsonl')
        self.assertEqual((g[0]['failure'], g[0]['failure_detail']), ('infra', 'pause_marker'))
        self.assertEqual((g[1]['attempt'], g[1]['failure']), (2, None))
        # a third infra attempt stops the run
        e = Env('r10_repeat', {'default': {'sleep': 0.6}})
        e.plan('dev', '90', '0')
        e.run(['--arms', 'G,K'], clock=Clock(mono_step=70))
        g = e.jl('games.jsonl')
        self.assertEqual([(x['arm'], x['attempt'], x['failure']) for x in g], [('G', 1, 'infra'), ('G', 2, 'infra'), ('G', 3, 'infra')])
        self.assertEqual(e.end()['stop_reason'], 'infra_repeat')
        self.assertEqual(e.end()['complete_deals'], 0)

    def test_R11_stop_leaves_deal_incomplete(self):
        for reason, code in (('ledger', 3), ('deck', 6), ('not_sent', 5)):
            e, a = self._arm('r11_' + reason, {'0000-k90-c00/a1/G': {'stop': reason, 'exit': 0}}, cell='0,1')
            self.assertEqual([(x['arm'], x['failure']) for x in e.jl('games.jsonl')], [('G', 'stop:' + reason)])
            self.assertFalse([d for d in e.jl('deals.jsonl') if d['complete']])
            self.assertEqual(e.end()['stop_reason'], 'stop:' + reason)
            self.assertEqual(e.end()['complete_deals'], 0)

    def test_R12_stop_date(self):
        stop = datetime.datetime.strptime(game_kit.STOP_AT_UTC, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
        e = Env('r12a')
        e.plan('dev', '90', '0')
        e.run(['--arms', 'G'], utcnow=lambda: stop)
        self.assertEqual((e.end()['stop_reason'], e.end()['complete_deals']), ('stop_date', 0))
        self.assertEqual(e.jl('games.jsonl'), [])
        e = Env('r12b')
        e.plan('dev', '90', '0')
        e.run(['--arms', 'G'], utcnow=lambda: stop - datetime.timedelta(seconds=1))
        self.assertEqual((e.end()['stop_reason'], e.end()['complete_deals']), (None, 1))

    def test_R13_went_first(self):
        setup = [dec_row('t', tc=0, cp=0, mode='setup'), dec_row('t', tc=0, cp=1, mode='setup')]
        self.assertEqual(gr.went_first_of(setup + [dec_row('t', tc=1, cp=1)]), 1)
        self.assertEqual(gr.went_first_of(setup + [dec_row('t', tc=2, cp=0)]), 1)
        self.assertEqual(gr.went_first_of(setup + [dec_row('t', tc=1, cp=0)]), 0)
        self.assertEqual(gr.went_first_of(setup + [dec_row('t', tc=2, cp=1)]), 0)
        self.assertIsNone(gr.went_first_of(setup))
        e, a = self._arm('r13', {'0000-k90-c00/a1/G': {'rows': setup + [dec_row('t', tc=2, cp=0)]}}, extra=('--arms', 'G'))
        self.assertEqual(a[('G', 1)]['judge']['went_first'], 1)
        self.assertEqual(a[('G', 1)]['judge']['setup_decisions'], 2)
        self.assertEqual(a[('G', 1)]['judge']['interventions'], 1)

    def test_R14_wall_limit(self):
        e = Env('r14', {'default': {'sleep': 5, 'orphan': True}})
        e.plan('dev', '90', '0')
        e.run(['--arms', 'G', '--max-deals', '1', '--game-wall-s', '100'])
        g = e.jl('games.jsonl')
        self.assertEqual((g[0]['failure'], g[0]['failure_detail']), ('infra', 'wall_limit'))
        for x in g:
            arm_dir = os.path.join(e.D, 'deals', '0000-k90-c00', 'a%d' % x['attempt'], 'G')
            pid = int(open(os.path.join(arm_dir, 'orphan.pid')).read())
            self.assertIn(gr.sid_of(pid)[1], (None, 'Z'))

    def test_R15_kill_helper_refuses(self):
        for sid in (0, 1, -5, os.getsid(0), os.getpgid(0)):
            with self.assertRaises(ValueError):
                gr.kill_session(sid)

    def test_R16_signals(self):
        e = Env('r16', {'default': {'sleep': 120, 'orphan': True}})
        pidfile = os.path.join(e.root, 'dg.json')
        e.scenario({'default': {'sleep': 120, 'orphan': True, 'pidfile': pidfile}})
        e.plan('dev', '90', '0')
        argv = ['python3', '-I', '-B', os.path.join(AIJ, 'game_runner.py')] + e.argv(['--arms', 'G'])
        p = subprocess.Popen(argv, env=e.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < 20 and not (os.path.exists(pidfile) and os.path.getsize(pidfile) > 0 and os.path.exists(os.path.join(e.D, 'deals', '0000-k90-c00', 'a1', 'G', 'orphan.pid'))):
            time.sleep(0.1)
        time.sleep(0.3)
        info = json.load(open(pidfile))
        p.send_signal(signal.SIGINT)
        self.assertEqual(p.wait(timeout=60), 130)
        t0 = time.time()
        while time.time() - t0 < 30 and gr.session_members(info['sid']):
            time.sleep(0.2)
        self.assertEqual(gr.session_members(info['sid']), [])
        self.assertEqual(e.end()['stop_reason'], 'signal')

    def _model_rows(self, tag, model):
        return {'rows': [dec_row(tag, model=model)]}

    def test_R17_model_version(self):
        e = Env('r17a', {'default': self._model_rows('t', 'm2')})
        e.plan('dev', '90', '0')
        e.run(['--arms', 'G', '--expect-model-version', 'm1'])
        self.assertEqual((e.end()['stop_reason'], e.end()['complete_deals']), ('model_version', 1))
        e = Env('r17b', {'0000-k90-c00/a1/G': self._model_rows('t', 'm1'), '0001-k90-c01/a1/G': self._model_rows('t', 'm2')})
        e.plan('dev', '90', '0,1')
        e.run(['--arms', 'G'])
        self.assertEqual(e.end()['stop_reason'], 'model_version')
        self.assertEqual(e.end()['model_returned'], 'm1')
        # resume reads the first value back from games.jsonl
        e = Env('r17c', {'0000-k90-c00/a1/G': self._model_rows('t', 'm1'), '0001-k90-c01/a1/G': self._model_rows('t', 'm2')})
        e.plan('dev', '90', '0,1')
        e.run(['--arms', 'G', '--max-deals', '1'])
        self.assertIsNone(e.end()['stop_reason'])
        e.run(['--arms', 'G', '--resume'])
        self.assertEqual(e.end()['stop_reason'], 'model_version')

    def test_R18_drop_guard(self):
        sc = {'0000-k80-c00/a1/G': {'sigkill_self': True},
              '0001-k80-c15/a1/K': {'fallbacks': {'1': 1}},
              '0002-k80-c06/a1/G': {'exit': 101},
              '0003-k80-c09/a1/G': {'rows': [{'fatal': 'shadow', 'detail': 'x'}]}}
        e = Env('r18', sc)
        e.plan('1', '80', '0,15,6,9,3')
        with mock.patch.object(gr, 'live_start_checks', lambda r: None):
            e.run(stage='1', mock=False)
        end = e.end()
        self.assertEqual(end['stop_reason'], 'drops')
        rec = {d['deal_idx']: d for d in e.jl('deals.jsonl') if d['complete']}
        self.assertEqual(sorted(rec), [0, 1, 2, 3])  # the fifth deal (cell 3) never started
        self.assertEqual([rec[i]['dropped'] for i in range(4)], [False, True, True, True])
        self.assertEqual(rec[0]['attempt'], 2)
        self.assertFalse(os.path.exists(os.path.join(e.D, 'deals', '0004-k80-c03')))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gr.main(['status', '--run-dir', e.D])
        out = buf.getvalue()
        self.assertIn('dropped deals 3 (limit 2)', out)
        for tag in ('0001-k80-c15-a1-K', '0002-k80-c06-a1-G', '0003-k80-c09-a1-G'):
            self.assertIn(tag, out)
        self.assertIn('kx3_route', out)
        self.assertIn('g_shadow', out)
        self.assertIn('engine_error', out)
        self.assertIn('infra attempts by reason: {"signal 9": 1}', out)

    def test_R18b_two_drops_go_on(self):
        sc = {'0000-k80-c00/a1/G': {'exit': 101}, '0001-k80-c15/a1/K': {'fallbacks': {'1': 1}}}
        e = Env('r18b', sc)
        e.plan('1', '80', '0,15,6')
        with mock.patch.object(gr, 'live_start_checks', lambda r: None):
            e.run(stage='1', mock=False)
        self.assertIsNone(e.end()['stop_reason'])
        self.assertEqual(e.end()['complete_deals'], 3)


if __name__ == '__main__':
    unittest.main()
