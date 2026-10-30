import contextlib
import hashlib
import io
import json
import os
import socket
import subprocess
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
sys.path.insert(0, HERE)
import game_gates  # noqa: E402
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
    _SAVED['saved'] = (providers.load_key, providers.call_vertex, providers._post_json)
    providers._OPENER = _BlockedOpener()
    _SAVED['patches'] = [mock.patch.object(socket.socket, 'connect', _blocked), mock.patch.object(socket, 'create_connection', _blocked),
                         mock.patch.object(socket, 'getaddrinfo', _blocked)]
    for p in _SAVED['patches']:
        p.start()


def tearDownModule():
    for p in _SAVED['patches']:
        p.stop()
    providers._OPENER = _SAVED['opener']
    providers.load_key, providers.call_vertex, providers._post_json = _SAVED['saved']


def call(argv):
    """game_gates.main(argv) -> (exit code, stdout lines)"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = game_gates.main(argv)
    return rc, buf.getvalue().splitlines()


def fresh(name):
    d = os.path.join(TMP, 'gg_' + name)
    subprocess.run(['rm', '-rf', d])
    return d


def plan(labels, key='k', end='attack'):
    return {'key': key, 'labels': labels, 'steps': ['s ' + l for l in labels], 'n_steps': len(labels), 'end': end, 'final': {'kind': 'x'}, 'result': {'r': 1}, 'n': 1}


def rec_of(plans, **kw):
    r = {'kind': 'plans', 'id': 'x', 'world_seed': 1, 'limits': dict(game_kit.LISTER_LIMITS), 'plans_hash': 'h', 'plans': plans, 'n_plans': len(plans), 'capped': False}
    r.update(kw)
    return r


def write_ref(path, recs):
    with open(path, 'w') as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n')
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class Gate1(unittest.TestCase):
    def test_G1_exclusions_written_before_comparison(self):
        d = fresh('g1')
        os.makedirs(d)
        pos = os.path.join(d, 'pos.json')
        with open(pos, 'w') as f:
            json.dump([{'id': i, 'deck': 'dk', 'turn_count': 1, 'his_turn': 1, 'turn_effects': [], 'me': {'knockouts': 0}, 'opp': {}} for i in ('p1', 'p2')], f)
        ref = os.path.join(d, 'ref.jsonl')
        sha = write_ref(ref, [rec_of([plan(['A'])], id='p1'), rec_of([plan(['B'])], id='p2')])
        new = {i: {'pos_rec': rec_of([plan(['A'])], id=i), 'obs_rec': rec_of([plan(['A'])], id=i), 'plan_actions': {}, 'root_check': {'ok': True}, 'pos_like': {}} for i in ('p1', 'p2')}
        order = []

        def fake_compare(*a, **k):
            path = os.path.join(d, 'out', 'gate1_excluded.json')
            order.append(('compare', os.path.exists(path)))
            with open(path) as fh:
                self.assertEqual(sorted(e['id'] for e in json.load(fh)), ['p2'])
            return []
        real_write = game_gates.write_exclusions

        def spy_write(path, excl):
            order.append('write')
            return real_write(path, excl)
        with mock.patch.object(game_gates, 'new_path', return_value=new), mock.patch.object(game_gates, 'compare_rows', fake_compare), \
                mock.patch.object(game_gates, 'write_exclusions', spy_write):
            call(['gate1', '--positions', pos, '--decks-dir', d, '--new-bin', 'x', '--ref', ref, '--ref-sha256', sha, '--out', os.path.join(d, 'out')])
        self.assertEqual(order, ['write', ('compare', True)])

    def test_G2_keyfree(self):
        a = rec_of([plan(['A', 'B'], key='k1'), plan(['C'], key='k2')])
        b = rec_of([plan(['A', 'B'], key='zz'), plan(['C'], key='yy')], plans_hash='other')
        self.assertEqual(game_gates.keyfree(a), game_gates.keyfree(b))
        self.assertEqual(game_gates.keyfree(a)[0], {'labels': ['A', 'B'], 'steps': ['s A', 's B'], 'end': 'attack', 'final': {'kind': 'x'}, 'result': {'r': 1}})
        self.assertEqual(sorted(game_gates.keyfree(a)[0]), ['end', 'final', 'labels', 'result', 'steps'])
        for field, val in (('labels', ['Z']), ('steps', ['q']), ('end', 'chance'), ('final', {'kind': 'y'}), ('result', {'r': 2})):
            c = rec_of([plan(['A', 'B']), plan(['C'])])
            c['plans'][0][field] = val
            self.assertNotEqual(game_gates.keyfree(a), game_gates.keyfree(c), field)
        d = rec_of([plan(['C']), plan(['A', 'B'])])
        self.assertNotEqual(game_gates.keyfree(a), game_gates.keyfree(d))

    def _row(self, i, ref_labels, new_labels, key='k', root_ok=True):
        ref = rec_of([plan(ref_labels, key='REF')], id=i)
        obs = rec_of([plan(new_labels, key=key)], id=i)
        new = {'pos_rec': obs, 'obs_rec': obs, 'plan_actions': {}, 'root_check': {'ok': root_ok, 'n_dup_of': 1, 'n_noop': 2},
               'pos_like': {'turn_count': 1, 'me': {'hand': [], 'discard': [], 'board': [], 'knockouts': 0}, 'opp': {'board': [], 'discard': []}, 'stadium': None, 'turn_effects': []}}
        with mock.patch.object(game_gates, 'prompt_sha', lambda pos, rec, dd: json.dumps(game_gates.keyfree(rec))):
            return game_gates.make_row(i, {'id': i, 'deck': 'dk', 'turn_count': 1}, ref, new, 'dd', None, True)

    def _rows(self, n_total, n_compared, **kw):
        rows = []
        for j in range(n_total):
            r = self._row('i%d' % j, ['A'], ['A'])
            if j >= n_compared:
                r['excluded'], r['compared'] = 'root_first_step_labels_differ', False
            rows.append(r)
        return rows

    def test_G3_verdicts(self):
        r = self._row('a', ['A'], ['B'])
        self.assertFalse(r['keyfree_eq_ref'])
        self.assertFalse(r['prompt_game_eq_ref'])
        self.assertIn('FAIL', game_gates.gate1_decide([r], 1, True)[0][-1])
        r = self._row('a', ['A'], ['A'], key='different')
        self.assertTrue(r['keyfree_eq_ref'] and r['prompt_game_eq_ref'])
        self.assertFalse(r['full_sha_eq_ref'])
        self.assertEqual((r['n_dup_of'], r['n_noop']), (1, 2))
        lines, rc = game_gates.gate1_decide([r], 1, True)
        self.assertEqual(lines[-1], 'GATE1 PASS')
        self.assertEqual(rc, 0)
        rows = self._rows(92, 92)
        rows[5]['excluded'], rows[5]['compared'], rows[5]['root_ok'] = 'root_first_step_labels_differ', False, False
        lines, rc = game_gates.gate1_decide(rows, 92, True)
        self.assertTrue(lines[-1].startswith('GATE1 FAIL'))
        self.assertEqual(rc, 1)
        lines, rc = game_gates.gate1_decide(self._rows(92, 82), 92, True)
        self.assertTrue(lines[-1].startswith('GATE1 INCOMPLETE (82 of 92 compared; 83 needed)'), lines[-1])
        self.assertEqual(rc, 3)
        lines, rc = game_gates.gate1_decide(self._rows(92, 83), 92, True)
        self.assertEqual((lines[-1], rc), ('GATE1 PASS', 0))
        self.assertEqual(lines[0], 'PROMPT BYTES: 83/83 equal')
        lines, rc = game_gates.gate1_decide(self._rows(3, 3), 3, False)
        self.assertEqual((lines[-1], rc), ('GATE1 INCOMPLETE (no reference)', 3))

    def test_G3_refusals(self):
        d = fresh('g3r')
        os.makedirs(d)
        ids = ['p1', 'p2']
        good = [rec_of([plan(['A'])], id='p1'), rec_of([plan(['A'])], id='p2')]
        ref = os.path.join(d, 'ref.jsonl')
        sha = write_ref(ref, good)
        self.assertEqual(sorted(game_gates.check_reference(ref, sha, ids)), ids)
        cases = {'sha': (good, '0' * 64), 'missing': (good[:1], None), 'extra': (good + [rec_of([plan(['A'])], id='p3')], None),
                 'seed': ([good[0], rec_of([plan(['A'])], id='p2', world_seed=2)], None),
                 'limits': ([good[0], rec_of([plan(['A'])], id='p2', limits={'max_plans': 1, 'max_nodes': 2, 'max_steps': 3})], None)}
        for name, (recs, bad_sha) in cases.items():
            s = write_ref(ref, recs)
            with self.assertRaises(game_gates.Refused, msg=name):
                game_gates.check_reference(ref, bad_sha or s, ids)
        # through the CLI: REFUSED exit 2
        pos = os.path.join(d, 'pos.json')
        with open(pos, 'w') as f:
            json.dump([{'id': i, 'deck': 'dk'} for i in ids], f)
        write_ref(ref, good)
        rc, out = call(['gate1', '--positions', pos, '--decks-dir', d, '--new-bin', 'x', '--ref', ref, '--ref-sha256', '1' * 64, '--out', os.path.join(d, 'o')])
        self.assertEqual(rc, 2)
        self.assertTrue(out[-1].startswith('GATE1 REFUSED'))


class Gate2(unittest.TestCase):
    def test_G4_gate2_positions_fixtures(self):
        for f in TL.FIXTURES:
            rc, out = call(['gate2-positions', '--positions', f, '--decks-dir', TL.FIXD, '--bin', TL.JP, '--out', fresh('g4_' + os.path.basename(f))])
            self.assertEqual(out[-1], 'GATE2a PASS', out[-5:])
            self.assertEqual(rc, 0)

    def _res(self, plans_line=None, prompt=('S', 'U'), pos_like=None, obs=None):
        return {'plans': plans_line or rec_of([plan(['A'], key='k1')]), 'pos_like': pos_like or {'t': 1}, 'prompt': prompt, 'obs': obs or {'o': 1}}

    def test_G5_compare_and_verdicts(self):
        base = {'a': self._res(), 'f2': self._res(rec_of([plan(['A'], key='kk')], plans_hash='zz')), 'f99': self._res(rec_of([plan(['A'], key='k9')], plans_hash='z9')),
                'b': self._res(), 'c': self._res()}
        eq, keys, fd = game_gates.compare_record(base, False)
        self.assertTrue(eq, fd)
        self.assertEqual(sorted(keys), ['fill2', 'fill99', 'obs_b', 'obs_c'])
        self.assertEqual((keys['fill2'], keys['fill99'], keys['obs_b'], keys['obs_c']), (False, False, True, True))
        for v in ('f2', 'f99', 'b', 'c'):
            bad = dict(base)
            bad[v] = self._res(prompt=('S', 'U!'))
            self.assertFalse(game_gates.compare_record(bad, False)[0], v)
        bad = dict(base)
        bad['f2'] = self._res(rec_of([plan(['Z'], key='kk')]))
        self.assertFalse(game_gates.compare_record(bad, False)[0])
        bad = dict(base)
        bad['b'] = self._res(rec_of([plan(['A'], key='other')]))
        self.assertFalse(game_gates.compare_record(bad, False)[0])  # obs_b must match plans line byte for byte, keys included
        sk = {'a': base['a'], 'f2': base['f2'], 'f99': base['f99']}
        eq, keys, fd = game_gates.compare_record(sk, True)
        self.assertTrue(eq)
        self.assertEqual((keys['obs_b'], keys['obs_c']), (None, None))
        sk['f99'] = self._res(prompt=('S', 'X'))
        self.assertFalse(game_gates.compare_record(sk, True)[0])

        def rows(n, a0, a1, c):
            out = []
            for j in range(n):
                actor = 0 if j < a0 else 1 if j < a0 + a1 else 0
                out.append({'id': str(j), 'actor': actor, 'skipped': False, 'has_obs_c': j < c, 'equal': True})
            return out
        lines, rc = game_gates.gate2b_decide(rows(200, 100, 100, 60))
        self.assertEqual((lines[-1], rc), ('GATE2b PASS', 0))
        for r in (rows(199, 100, 99, 60), rows(200, 151, 49, 60), rows(200, 100, 100, 49)):
            lines, rc = game_gates.gate2b_decide(r)
            self.assertTrue(lines[-1].startswith('GATE2b INCOMPLETE'), lines[-1])
            self.assertEqual(rc, 3)
        r = rows(200, 100, 100, 60)
        r += [{'id': 's%d' % j, 'actor': 0, 'skipped': True, 'has_obs_c': False, 'equal': True} for j in range(30)]
        lines, rc = game_gates.gate2b_decide(r)
        self.assertEqual(lines[-1], 'GATE2b PASS')
        self.assertTrue(any('skipped share' in l for l in lines))
        r[-1]['equal'] = False
        self.assertEqual(game_gates.gate2b_decide(r)[0][-1], 'GATE2b FAIL')
        r = rows(199, 100, 99, 60)
        r[3]['equal'] = False
        self.assertEqual(game_gates.gate2b_decide(r)[0][-1], 'GATE2b FAIL')

    def test_G5_problem_rows_fail(self):
        prob = {'problem': 'lister_error rc=1'}
        res = {'a': dict(prob), 'f2': dict(prob), 'f99': dict(prob)}
        eq, keys, fd = game_gates.compare_record(res, True)
        self.assertFalse(eq)
        self.assertEqual((fd['what'], fd['variant']), ('problem', 'f2'))
        self.assertEqual((fd['a'], fd['b']), (prob['problem'], prob['problem']))
        # a problem in a compared variant only
        res = {'a': self._res(), 'f2': self._res(), 'f99': dict(prob)}
        eq, keys, fd = game_gates.compare_record(res, True)
        self.assertFalse(eq)
        self.assertEqual((fd['variant'], fd['what']), ('f99', 'problem'))
        # an identical prompt-render exception
        class FakeObs:
            problems = {}
            kinds = {'plans': {'x': rec_of([plan(['A'], key='k1')])}, 'pos_like': {'x': {'pos': {'t': 1}}}}
        with mock.patch.object(game_gates, 'prompt_for', side_effect=ValueError('boom')):
            r = game_gates._variant_result(FakeObs, 'x', '/x/dk.txt')
        self.assertIn('problem', r)
        eq, keys, fd = game_gates.compare_record({'a': r, 'f2': dict(r), 'f99': dict(r)}, True)
        self.assertFalse(eq)
        self.assertEqual(fd['what'], 'problem')

    def test_G5_skipped_record_excluded_from_b_and_c(self):
        seen = {}

        class FakeObs:
            def __init__(self, ids):
                self.kinds = {'plans': {i: rec_of([plan(['A'], key='k1')]) for i in ids}, 'pos_like': {i: {'pos': {'t': 1}} for i in ids}}
                self.problems, self.stats = {}, []

        def fake_obs(jp, records, workdir, name, extra=()):
            seen[name.rsplit('_', 1)[-1]] = [r['id'] for r in records]
            return FakeObs([r['id'] for r in records])
        recs = []
        for i, sk in (('r0', False), ('r1', True)):
            recs.append({'id': i, 'actor': 0, 'skipped': sk, 'obs_a': {'o': 1}, 'obs_b': {'o': 1}, 'obs_c': {'o': 1}, 'legal_actions': [], 'deck_file': '/x/dk.txt'})
        d = fresh('g5skip')
        os.makedirs(d)
        f = os.path.join(d, 'leak.jsonl')
        with open(f, 'w') as fh:
            for r in recs:
                fh.write(json.dumps(r) + '\n')
        with mock.patch.object(game_gates, 'obs_mode', fake_obs), mock.patch.object(game_gates, 'prompt_for', lambda *a: ('S', 'U')):
            rc, out = call(['gate2-games', '--leak', f, '--bin', 'x', '--out', os.path.join(d, 'o')])
        self.assertEqual(seen['b'], ['r0'])
        self.assertEqual(seen['c'], ['r0'])
        self.assertEqual(sorted(seen['a']), ['r0', 'r1'])
        self.assertEqual(seen['f2'], seen['a'])
        self.assertNotEqual(out[-1], 'GATE2b FAIL', out[-6:])

    def test_G5_real_leak_and_append(self):
        files = []
        for name, deck, lst, seat, seed in (('c00', 0, 0, 0, 25103000090), ('c12', 1, 1, 0, 25103001290)):
            out = os.path.join(TMP, 'g5_%s.jsonl' % name)
            if not os.path.exists(out):
                TL.run(['nice', '-n', '19', TL.LS, '--pilot-deck', os.path.join(TL.REPO, game_kit.DECKS[deck]), '--opp-deck', os.path.join(TL.REPO, game_kit.LISTS[lst]),
                        '--seat', str(seat), '--seeds', str(seed), '--every', '5', '--out', out])
            files.append(out)
        d = fresh('g5')
        rc, out = call(['gate2-games', '--leak', files[0], '--bin', TL.JP, '--out', d])
        self.assertNotEqual(out[-1], 'GATE2b FAIL', out[-12:])
        self.assertTrue(out[-1].startswith('GATE2b INCOMPLETE'), out[-1])
        self.assertEqual(rc, 3)
        self.assertTrue(any(l.startswith('OBS_SECS_MEAN ') for l in out))
        self.assertTrue(any('skipped share' in l for l in out))
        rows1 = [json.loads(l) for l in open(os.path.join(d, 'gate2b_rows.jsonl'))]
        self.assertTrue(rows1)
        for r in rows1:
            self.assertEqual(sorted(r['keys_equal']), ['fill2', 'fill99', 'obs_b', 'obs_c'])
        rc, out = call(['gate2-games', '--leak', files[0], '--bin', TL.JP, '--out', d])
        self.assertEqual(rc, 2)
        rc, out = call(['gate2-games', '--leak', files[1], '--bin', TL.JP, '--out', d, '--append'])
        self.assertNotEqual(out[-1], 'GATE2b FAIL', out[-12:])
        rows2 = [json.loads(l) for l in open(os.path.join(d, 'gate2b_rows.jsonl'))]
        self.assertGreater(len(rows2), len(rows1))
        self.assertTrue(any(('records %d' % len(rows2)) in l for l in out), out[:8])


class Seat1(unittest.TestCase):
    ACT_P = {'actor': 1, 'action': {'Promote': {'player': 1, 'in_play_idx': 2}}, 'is_stack': False}
    ACT_J = {'actor': 1, 'action': {'ApplyDamage': {'attacking_ref': [1, 0], 'targets': [[10, 0, 0]], 'is_from_active_to_active': True}}, 'is_stack': False}

    def _leak(self, n_opp, n_own, setup=0):
        recs = []
        for j in range(n_opp + n_own + setup):
            opp_turn = j < n_opp
            tc = 0 if j >= n_opp + n_own else 3
            recs.append({'id': 'r%d' % j, 'actor': 1, 'turn_count': tc, 'current_player': 0 if opp_turn else 1, 'deck_file': '/x/dk.txt',
                         'obs_a': {'template': {'current_player': 0 if opp_turn else 1}}, 'legal_actions': []})
        d = fresh('s1_%d_%d_%d' % (n_opp, n_own, setup))
        os.makedirs(d)
        f = os.path.join(d, 'leak.jsonl')
        with open(f, 'w') as fh:
            for r in recs:
                fh.write(json.dumps(r) + '\n')
        return f, d

    class FakeObs:
        def __init__(self, ids, label, act):
            self.kinds = {'plans': {i: {'plans': [{'n': 1, 'labels': [label], 'key': 'k'}], 'n_plans': 1} for i in ids},
                          'plan_actions': {i: {'plans': [{'n': 1, 'actions': [act], 'forced': [False]}]} for i in ids},
                          'pos_like': {i: {'pos': {'turn_count': 3}} for i in ids}}
            self.problems, self.stats = {}, []

    def _run(self, f, d, label, act, text='You are the player on the move. x'):
        def fake_obs(jp, records, workdir, name, extra=()):
            return Seat1.FakeObs([r['id'] for r in records], label, act)
        with mock.patch.object(game_gates, 'obs_mode', fake_obs), mock.patch.object(game_gates, 'prompt_for', lambda *a: (text, 'user')):
            return call(['seat1', '--leak', f, '--bin', 'x', '--out', os.path.join(d, 'o')])

    def test_G6_seat1(self):
        f, d = self._leak(3, 6)
        rc, out = self._run(f, d, 'Promote:0@2', self.ACT_P)
        self.assertEqual((out[-1], rc), ('SEAT1 PASS', 0), out)
        rows = [json.loads(l) for l in open(os.path.join(d, 'o', 'seat1_rows.jsonl'))]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(r['n_numbers'] == 1 and r['has_you_line'] for r in rows))
        self.assertEqual(sum(1 for r in rows if r['opponent_turn']), 3)
        rc, out = self._run(f, d, 'Promote:1@2', self.ACT_P)
        self.assertEqual((out[-1], rc), ('SEAT1 STOP: label seat', 1))
        rc, out = self._run(f, d, 'ApplyDamage#{"attacking_ref":[0,0],"is_from_active_to_active":true,"targets":[[10,1,0]]}', self.ACT_J)
        self.assertEqual(out[-1], 'SEAT1 PASS', out)
        rows = [json.loads(l) for l in open(os.path.join(d, 'o', 'seat1_rows.jsonl'))]
        self.assertEqual(rows[0]['n_numbers'], 2)
        rc, out = self._run(f, d, 'ApplyDamage#{"attacking_ref":[1,0],"is_from_active_to_active":true,"targets":[[10,1,0]]}', self.ACT_J)
        self.assertEqual((out[-1], rc), ('SEAT1 STOP: label seat', 1))
        rc, out = self._run(f, d, 'Promote:0@2', self.ACT_P, text='no such line')
        self.assertEqual((out[-1], rc), ('SEAT1 STOP: no \'you\' line', 1))
        f7, d7 = self._leak(3, 4)
        rc, out = self._run(f7, d7, 'Promote:0@2', self.ACT_P)
        self.assertEqual((rc, out[-1].startswith('SEAT1 INCOMPLETE')), (3, True), out)
        f8, d8 = self._leak(1, 7)
        rc, out = self._run(f8, d8, 'Promote:0@2', self.ACT_P)
        self.assertEqual((rc, out[-1].startswith('SEAT1 INCOMPLETE')), (3, True), out)
        # setup states are never selected: 7 usable + 5 setup states is still INCOMPLETE
        f9, d9 = self._leak(3, 4, setup=5)
        rc, out = self._run(f9, d9, 'Promote:0@2', self.ACT_P)
        self.assertEqual(rc, 3, out)



# ------------------------------------------------------------------------------------------------ B7: gate 3 and the gate-4 tools
import time  # noqa: E402

import game_runner  # noqa: E402


def drow(tag, mode='intervene', tc=3, cp=0, **kw):
    r = {'schema': 'gemini_game_decision_v1', 'deal_tag': tag, 'ply': 1, 'actor': 0, 'turn_count': tc, 'current_player': cp, 'kind': 'setup' if mode == 'setup' else 'own_turn', 'mode': mode,
         'follow': None, 'reask_reason': 'first', 'judge': None, 'tries': [], 'n_list_runs': 0, 'n_judge_calls': 0, 'plan': None, 'fallback': None, 'root_check': {'n_dup_of': 1, 'n_noop': 0}}
    r.update(kw)
    return r


def prow(tag, plan_id, n_steps=3, steps_played=3, ended='completed'):
    return {'schema': 'gemini_game_plan_v1', 'deal_tag': tag, 'plan_id': plan_id, 'n_steps': n_steps, 'steps_played': steps_played, 'ended': ended}


def mkgame(tag, n_int=10, n_fb=0, n_follow=5, n_setup=2):
    rows = [drow(tag, 'setup', tc=0) for _ in range(n_setup)]
    for i in range(n_int):
        if i < n_fb:
            rows.append(drow(tag, fallback={'reason': 'a', 'detail': 'lister_error', 'shadow_i': 0, 'shadow_secs': 1.0}, n_list_runs=1))
        else:
            pid = '%s-p%d' % (tag, i)
            rows.append(drow(tag, n_list_runs=1, n_judge_calls=1, judge={'plan_key': 'k%d' % i, 'mock': True}, plan={'plan_id': pid, 'n': 1, 'key': 'k%d' % i, 'n_steps': 3, 'end': 'attack'}))
            rows.append(prow(tag, pid))
    for _ in range(n_follow):
        rows.append(drow(tag, 'follow', follow={'plan_id': 'x', 'step': 2, 'skipped_forced': 0, 'hash_ok': True}))
    return rows


class Run3:
    def __init__(self, name, n_games=8, **gk):
        self.D = os.path.join(TMP, 'g3_' + name)
        subprocess.run(['rm', '-rf', self.D])
        os.makedirs(self.D)
        self.games = []
        for i in range(n_games):
            tag = '%04d-k90-c%02d-a1-G' % (i, i)
            self.games.append({'idx': i, 'cell': i, 'tag': tag, 'rows': mkgame(tag, **gk), 'completion': 'completed', 'lifecycle': 0, 'errors': 0, 'fallbacks': 0})

    def write(self):
        for g in self.games:
            adir = os.path.join(self.D, 'deals', '%04d-k90-c%02d' % (g['idx'], g['cell']), 'a1', 'G')
            os.makedirs(adir, exist_ok=True)
            with open(os.path.join(adir, 'rows.jsonl'), 'w') as f:
                for r in g['rows']:
                    f.write(json.dumps(r) + '\n')
            bits = game_kit.cell_bits(g['cell'])
            arm = {'deal_tag': g['tag'], 'arm': 'G', 'bits': bits, 'cell': g['cell'], 'completion': g['completion'], 'lifecycle_errors': g['lifecycle'], 'failure': None,
                   'protocol': [{'seat': bits['seat'], 'role': 'pilot', 'decisions': 5, 'fallbacks': g['fallbacks'], 'errors': g['errors']}], 'judge': {}}
            with open(os.path.join(self.D, 'games.jsonl'), 'a') as f:
                f.write(json.dumps(arm) + '\n')
            with open(os.path.join(self.D, 'deals.jsonl'), 'a') as f:
                f.write(json.dumps({'deal_idx': g['idx'], 'attempt': 1, 'complete': True, 'g_deal_tag': g['tag'], 'k_deal_tag': None}) + '\n')
        return self

    def run(self, extra=()):
        return call(['gate3', '--run-dir', self.D, '--min-games', '8', '--min-follow', '20'] + list(extra))


class Gate3(unittest.TestCase):
    def verdict(self, run, extra=()):
        rc, out = run.write().run(extra)
        return rc, out

    def test_G7b_missing_rows_and_setup_rate(self):
        r = Run3('norows')
        r.write()
        g = r.games[0]
        os.remove(os.path.join(r.D, 'deals', '%04d-k90-c%02d' % (g['idx'], g['cell']), 'a1', 'G', 'rows.jsonl'))
        rc, out = r.run()
        self.assertEqual((rc, out[-1]), (1, 'GATE3 FAIL'), out[-4:])
        self.assertTrue(any(l.startswith('FAILED: ') and g['tag'] in l and 'rows.jsonl missing' in l for l in out), out[-6:])
        # an 11% fallback rate with many setup rows still fails (setup rows are outside the denominator)
        r = Run3('r11setup', n_int=100, n_fb=11, n_setup=40)
        rc, out = self.verdict(r)
        self.assertEqual((rc, out[-1]), (1, 'GATE3 FAIL'), out[-4:])

    def test_G7_gate3(self):
        rc, out = self.verdict(Run3('clean'))
        self.assertEqual((rc, out[-1]), (0, 'GATE3 PASS'), out)
        self.assertTrue(any(l.startswith('ILLEGAL 0') for l in out))
        # a 9% fallback rate with many setup rows passes
        r = Run3('nine', n_int=100, n_fb=9, n_setup=40)
        self.assertEqual(self.verdict(r)[1][-1], 'GATE3 PASS')
        bad = {}
        r = Run3('forced')
        r.games[0]['rows'].append(drow(r.games[0]['tag'], fallback={'reason': 'dev', 'detail': 'forced_dev'}, n_list_runs=0))
        bad['forced_dev'] = r
        bad['rate11'] = Run3('rate', n_int=100, n_fb=11)
        r = Run3('f19', n_follow=0)
        r.games[0]['rows'] += [drow(r.games[0]['tag'], 'follow', follow={'plan_id': 'x', 'step': 2, 'skipped_forced': 0, 'hash_ok': True}) for _ in range(19)]
        bad['follow19'] = r
        r = Run3('stale')
        r.games[0]['rows'].append(prow(r.games[0]['tag'], 'zz', ended='stale'))
        bad['stale'] = r
        r = Run3('two')
        r.games[0]['rows'][4]['n_list_runs'] = 2
        bad['two_list_runs'] = r
        r = Run3('loop')
        t = r.games[0]['tag']
        for i in range(3):
            r.games[0]['rows'].append(drow(t, tc=5, reask_reason='stale', judge={'plan_key': 'same', 'mock': True}, plan={'plan_id': 'q%d' % i, 'n': 1, 'key': 'same', 'n_steps': 2, 'end': 'attack'}, n_list_runs=1, n_judge_calls=1))
            r.games[0]['rows'].append(prow(t, 'q%d' % i, 2, 2))
        bad['loop3'] = r
        r = Run3('past')
        r.games[0]['rows'][-1:] = [prow(r.games[0]['tag'], 'over', 3, 4)]
        bad['past_n_steps'] = r
        r = Run3('noend')
        r.games[0]['rows'] = [x for x in r.games[0]['rows'] if x.get('schema') != 'gemini_game_plan_v1' or x['plan_id'] != '%s-p3' % r.games[0]['tag']]
        bad['no_end_row'] = r
        r = Run3('lifecycle')
        r.games[0]['lifecycle'] = 1
        bad['lifecycle'] = r
        r = Run3('plankey')
        for x in r.games[0]['rows']:
            if x.get('plan'):
                x['plan']['key'] = 'different'
                break
        bad['plan_key'] = r
        r = Run3('notmock')
        for x in r.games[0]['rows']:
            if x.get('judge'):
                x['judge']['mock'] = False
                break
        bad['not_mock'] = r
        r = Run3('fb')
        r.games[0]['fallbacks'] = 1
        bad['pilot_fallback'] = r
        for name, run in bad.items():
            rc, out = self.verdict(run)
            self.assertEqual((name, rc, out[-1]), (name, 1, 'GATE3 FAIL'), out[-6:])
        # a fallback (a) after the judge call leaves plan null: not a plan.key failure
        r = Run3('nullplan')
        t = r.games[0]['tag']
        r.games[0]['rows'].append(drow(t, n_list_runs=1, n_judge_calls=1, judge={'plan_key': 'k', 'mock': True}, plan=None, fallback={'reason': 'a', 'detail': 'plan_key_missing', 'shadow_i': 0, 'shadow_secs': 1}))
        self.assertEqual(self.verdict(r)[1][-1], 'GATE3 PASS')
        # --smoke passes forced_dev rows and a small run
        r = Run3('smoke', n_games=1)
        r.games[0]['rows'].append(drow(r.games[0]['tag'], fallback={'reason': 'dev', 'detail': 'forced_dev'}, n_list_runs=0))
        rc, out = call(['gate3', '--run-dir', r.write().D, '--smoke'])
        self.assertEqual((rc, out[-1]), (0, 'GATE3 PASS'), out)


def fake_bin(path, body):
    with open(path, 'w') as f:
        f.write('#!/usr/bin/env python3\nimport json, os, sys, time, subprocess\n' + body)
    os.chmod(path, 0o755)


FAKE_KP = r"""
args = sys.argv[1:]
a = {args[i]: args[i + 1] for i in range(len(args)) if args[i].startswith('--')}
seed = int(a['--seeds'])
HERE = os.path.dirname(os.path.realpath(__file__))
sc = json.load(open(os.path.join(HERE, 'kp_scenario.json')))
s = dict(sc.get('default', {}))
s.update(sc.get(str(seed), {}))
json.dump(args, open(os.path.join(HERE, 'argv_%d.json' % seed), 'w'))
json.dump({'sid': os.getsid(0), 'rayon': os.environ.get('RAYON_NUM_THREADS')}, open(os.path.join(HERE, 'env_%d.json' % seed), 'w'))
if s.get('hang'):
    ch = subprocess.Popen([sys.executable, '-c', 'import time\ntime.sleep(300)'], preexec_fn=os.setpgrp)
    open(os.path.join(HERE, 'child_%d.pid' % seed), 'w').write(str(ch.pid))
    time.sleep(300)
print(json.dumps({'seed': seed, 'seat': int(a['--seat']), 'code': 'kx3', 'opp_code': a.get('--opp-code', 'km3'), 'decisions_compared': 4, 'pilot_decisions_compared': s.get('pilot', 2),
                  'identical': s.get('identical', True), 'first_diff': None, 'secs_direct': 1.0, 'secs_protocol': 1.0, 'protocol_fallbacks': s.get('fb', 0), 'proto_threads': a.get('--proto-threads')}))
sys.exit(0 if s.get('identical', True) and not s.get('fb') else 1)
"""

FAKE_KR = r"""
args = sys.argv[1:]
a = {args[i]: args[i + 1] for i in range(len(args)) if args[i].startswith('--')}
HERE = os.path.dirname(os.path.realpath(__file__))
bad = os.path.exists(os.path.join(HERE, 'kr_mismatch'))
n = eq = 0
for l in open(a['--shadow-log']):
    r = json.loads(l)
    n += 1
    ok = not bad
    eq += ok
    print(json.dumps({'deal_tag': r['deal_tag'], 'equal': ok, 'ply': r['ply'], 'replay_i': r['shadow_i'], 'shadow_i': r['shadow_i']}))
    open(os.path.join(HERE, 'kr_decks.txt'), 'a').write(a['--opp-deck'] + '\n')
print(json.dumps({'checked': n, 'equal': eq, 'mismatches': n - eq, 'summary': True}))
sys.exit(0 if eq == n else 1)
"""


class Gate4(unittest.TestCase):
    def kp_env(self, name, scenario=None):
        root = os.path.join(TMP, 'g4_' + name)
        subprocess.run(['rm', '-rf', root])
        os.makedirs(os.path.join(root, 'eng'))
        os.makedirs(os.path.join(root, 'jb'))
        fake_bin(os.path.join(root, 'jb', 'kx3_parity'), FAKE_KP)
        fake_bin(os.path.join(root, 'jb', 'kx3_replay'), FAKE_KR)
        with open(os.path.join(root, 'jb', 'kp_scenario.json'), 'w') as f:
            json.dump(scenario or {}, f)
        return root

    def par(self, root, extra=(), cells='0,1', ks='90'):
        return call(['gate4-parity', '--engine-bins', os.path.join(root, 'eng'), '--judge-bins', os.path.join(root, 'jb'), '--repo', TL.REPO, '--k-list', ks, '--cells', cells, '--out',
                     os.path.join(root, 'out'), '--min-per-seat', '1'] + list(extra))

    def test_G8_parity(self):
        root = self.kp_env('ok')
        rc, out = self.par(root, ['--max-decisions', '2', '--pb-threads', '2'])
        self.assertEqual((rc, out[-1]), (0, 'GATE4a PASS'), out)
        argv = json.load(open(os.path.join(root, 'jb', 'argv_%d.json' % game_kit.seed(0, 90))))
        self.assertIn('--protocol-bot', argv)
        self.assertEqual(argv[argv.index('--protocol-bot') + 1], os.path.join(root, 'eng', 'protocol_bot'))
        self.assertEqual(argv[argv.index('--proto-threads') + 1], '2')
        self.assertNotIn('--proto-cmd', argv)
        self.assertEqual(argv[argv.index('--max-decisions') + 1], '2')
        env = json.load(open(os.path.join(root, 'jb', 'env_%d.json' % game_kit.seed(0, 90))))
        self.assertEqual(env['rayon'], '2')
        # a resume skips finished seeds
        rc, out = self.par(root, ['--resume', '--pb-threads', '2'])
        self.assertEqual(rc, 0)
        self.assertEqual(len(game_gates.read_jsonl(os.path.join(root, 'out', 'gate4a_rows.jsonl'))), 2)
        for name, sc in (('zero', {'pilot': 0}), ('notident', {'identical': False}), ('fb', {'fb': 1})):
            root = self.kp_env(name, {'default': {}, str(game_kit.seed(1, 90)): sc})
            rc, out = self.par(root, ['--pb-threads', '8'])
            self.assertEqual((name, rc, out[-1]), (name, 1, 'GATE4a FAIL'), out)
        root = self.kp_env('few')
        rc, out = self.par(root, ['--min-per-seat', '2'] if False else [], cells='0,2')
        self.assertEqual(out[-1], 'GATE4a INCOMPLETE')  # both cells are seat 0: seat 1 has no finished seed
        self.assertEqual(rc, 3)

    def test_G8_timeout_kills_session(self):
        root = self.kp_env('to', {str(game_kit.seed(0, 90)): {'hang': True}})
        rc, out = self.par(root, ['--timeout-s', '2', '--pb-threads', '2'], cells='0,1')
        self.assertEqual((rc, out[-1]), (3, 'GATE4a INCOMPLETE'), out)
        rows = game_gates.read_jsonl(os.path.join(root, 'out', 'gate4a_rows.jsonl'))
        self.assertTrue(any(r.get('timeout') for r in rows))
        sid = json.load(open(os.path.join(root, 'jb', 'env_%d.json' % game_kit.seed(0, 90))))['sid']
        t0 = time.time()
        while time.time() - t0 < 30 and game_runner.session_members(sid):
            time.sleep(0.2)
        self.assertEqual(game_runner.session_members(sid), [])

    def shadow_run(self, name, n_setup=3, n_fb=4, extra=(), mismatch=False, cell=0, arm_row=True, bad_decide=False):
        root = self.kp_env(name)
        if mismatch:
            open(os.path.join(root, 'jb', 'kr_mismatch'), 'w').close()
        D = os.path.join(root, 'run')
        adir = os.path.join(D, 'deals', '0000-k90-c%02d' % cell, 'a1', 'G')
        os.makedirs(adir)
        tag = '0000-k90-c%02d-a1-G' % cell
        recs = []
        for i in range(n_setup + n_fb):
            tc = 0 if i < n_setup else 3
            recs.append({'deal_tag': tag, 'ply': i + 1, 'new_game': '{}', 'decide': json.dumps({'pdl_observation': {'template': {'turn_count': tc}}}), 'shadow_i': 0, 'secs': 1.0})
        if bad_decide:
            recs[0]['decide'] = 'not json {'
        with open(os.path.join(adir, 'shadow.jsonl'), 'w') as f:
            for r in recs:
                f.write(json.dumps(r) + '\n')
        with open(os.path.join(D, 'games.jsonl'), 'w') as f:
            if arm_row:
                f.write(json.dumps({'deal_tag': tag, 'arm': 'G', 'bits': {'deck': 0, 'list': 0, 'policy': 0, 'seat': 0}}) + '\n')  # deliberately wrong list: the tag's cell decides
        os.makedirs(os.path.join(root, 'tmp'))
        self.root = root
        return call(['gate4-shadow', '--run-dir', D, '--repo', TL.REPO, '--judge-bins', os.path.join(root, 'jb'), '--sample-fallback', '2', '--sample-setup', '1', '--sample-seed', '25103008',
                     '--out', os.path.join(root, 'out')] + list(extra))

    def test_G9_shadow(self):
        rc, out = self.shadow_run('ok')
        self.assertEqual((rc, out[-1]), (0, 'GATE4b PASS'), out)
        self.assertTrue(any('setup' in l and 'checked 1' in l for l in out), out)
        self.assertTrue(any('fallback' in l and 'checked 2' in l for l in out), out)
        decks = open(os.path.join(self.root, 'jb', 'kr_decks.txt')).read().split()
        self.assertTrue(all(d.endswith('t-lucario.txt') for d in decks))
        rc, out = self.shadow_run('few_fb', n_fb=1)
        self.assertEqual((rc, out[-1]), (3, 'GATE4b INCOMPLETE'), out)
        rc, out = self.shadow_run('zero_fb', n_fb=0)
        self.assertEqual((rc, out[-1]), (3, 'GATE4b INCOMPLETE'), out)
        rc, out = self.shadow_run('few_setup', n_setup=0)
        self.assertEqual((rc, out[-1]), (3, 'GATE4b INCOMPLETE'), out)
        rc, out = self.shadow_run('bad', mismatch=True)
        self.assertEqual((rc, out[-1]), (1, 'GATE4b FAIL'), out)
        # the same seed gives the same sample
        a = game_gates.sample_records(list(range(20)), 5, 25103008)
        self.assertEqual(a, game_gates.sample_records(list(range(20)), 5, 25103008))
        self.assertNotEqual(a, game_gates.sample_records(list(range(20)), 5, 1))
        rc, out = self.shadow_run('list2', cell=4)
        decks = open(os.path.join(self.root, 'jb', 'kr_decks.txt')).read().split()
        self.assertTrue(all(d.endswith('t-suicune.txt') for d in decks))
        # the list comes from the tag's cell, never from the arm row and never a default
        rc, out = self.shadow_run('nocell', cell=4, arm_row=False)
        decks = open(os.path.join(self.root, 'jb', 'kr_decks.txt')).read().split()
        self.assertTrue(decks and all(d.endswith('t-suicune.txt') for d in decks), decks)
        # the per-list logs and KR's stdout are under --out
        outdir = os.path.join(self.root, 'out')
        names = os.listdir(outdir)
        self.assertTrue(any(n.startswith('shadow_') for n in names), names)
        self.assertTrue(any(n.startswith('kr_') for n in names), names)
        # an unparsable decide line is a FAILED line, not a fallback
        rc, out = self.shadow_run('unparse', bad_decide=True)
        self.assertEqual((rc, out[-1]), (1, 'GATE4b FAIL'), out)
        self.assertTrue(any(l.startswith('FAILED') and 'unparsable decide line' in l for l in out), out)

    def pin_run(self, name, arms, pin=None):
        root = os.path.join(TMP, 'g10_' + name)
        subprocess.run(['rm', '-rf', root])
        D = os.path.join(root, 'run')
        base = {'budget_ms': 0, 'cap': 12, 'code': game_kit.KX3_CANONICAL, 'depth': 3, 'extra_lists': [], 'knowledge': 'REALISTIC', 'rollouts': 16, 'z': 2.0}
        pin = pin or dict(base, seat=0)
        with open(os.path.join(root, 'pin.json') if os.path.isdir(root) else (os.makedirs(root) or os.path.join(root, 'pin.json')), 'w') as f:
            json.dump(pin, f)
        for i, (arm, policy, lines) in enumerate(arms):
            tag = '%04d-k90-c00-a1-%s' % (i, arm)
            adir = os.path.join(D, 'deals', '%04d-k90-c00' % i, 'a1', arm)
            os.makedirs(adir)
            if lines is not None:
                with open(os.path.join(adir, 'stderr.txt'), 'w') as f:
                    f.write('noise\n')
                    for l in lines:
                        f.write('KX_PARAMS ' + json.dumps(l) + '\n')
            with open(os.path.join(D, 'games.jsonl'), 'a') as f:
                f.write(json.dumps({'deal_tag': tag, 'arm': arm, 'bits': {'deck': 0, 'list': 0, 'policy': policy, 'seat': 0}}) + '\n')
        return call(['gate4-pin', '--run-dir', D, '--pin', os.path.join(root, 'pin.json')]), base

    def test_G10_pin(self):
        base = {'budget_ms': 0, 'cap': 12, 'code': game_kit.KX3_CANONICAL, 'depth': 3, 'extra_lists': [], 'knowledge': 'REALISTIC', 'rollouts': 16, 'z': 2.0}
        ok_lines = [dict(base, seat=0)]
        (rc, out), _ = self.pin_run('ok', [('K', 0, ok_lines), ('G', 0, ok_lines), ('G', 1, [dict(base, seat=1)])])
        self.assertEqual(rc, 0, out)
        self.assertTrue(out[-1].startswith('GATE4c PASS'), out)
        for name, arms in (('nok', [('K', 0, [])]), ('noopp', [('G', 1, [])]), ('code', [('K', 0, [dict(base, seat=0, code='kx3_r16_c12_z2_real_t0_trace')])]),
                           ('differs', [('K', 0, [dict(base, seat=0, depth=4)])])):
            (rc, out), _ = self.pin_run(name, arms)
            self.assertEqual(rc, 1, name)
            self.assertTrue(out[-1].startswith('GATE4c FAIL'), (name, out))
        (rc, out), _ = self.pin_run('seat', [('K', 0, [dict(base, seat=1)])])
        self.assertEqual(rc, 0, out)
        # a K arm and a kx3-opponent arm without stderr.txt fail; so does arms checked 0
        for name, arms in (('nofile_k', [('K', 0, None), ('G', 0, ok_lines)]), ('nofile_opp', [('G', 1, None), ('K', 0, ok_lines)]), ('zero', [('K', 0, None)])):
            (rc, out), _ = self.pin_run(name, arms)
            self.assertEqual(rc, 1, (name, out))
            self.assertTrue(out[-1].startswith('GATE4c FAIL'), (name, out))
            self.assertTrue(any('stderr.txt missing' in l or 'arms checked 0' in l for l in out), (name, out))
        (rc, out), _ = self.pin_run('zero_arms', [])
        self.assertEqual(rc, 1, out)
        self.assertIn('arms checked 0', out[-1])
        # the pin carries the non-canonical code: only the code check can fail it
        trace = dict(base, code=game_kit.KX3_CANONICAL + '_trace')
        (rc, out), _ = self.pin_run('pincode', [('K', 0, [dict(trace, seat=0)])], pin=dict(trace, seat=0))
        self.assertEqual(rc, 1, out)
        self.assertTrue(any('non-canonical code' in l for l in out), out)
        self.assertFalse(any('differs from the pin' in l for l in out), out)


if __name__ == '__main__':
    unittest.main()
