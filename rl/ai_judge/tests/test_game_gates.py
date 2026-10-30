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


if __name__ == '__main__':
    unittest.main()
