#!/usr/bin/env python3
"""make_turns.py on synthetic inputs (no exam data): the turn list keeps only point_id, game, global_turn and clip; every bad shape stops.
  test_make_turns.py   (make_turns.py beside it)"""
import json, os, shutil, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
G1, G2 = '20261016_184635000_SR', '20261021_020059000_SR'


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, 'inv_in_p1'))
        os.makedirs(os.path.join(self.d, 'inv_out_p1'))
        os.makedirs(os.path.join(self.d, 'selcode_in_p1'))
        with open(os.path.join(self.d, 'inv_in_p1', 'window.json'), 'w') as f:
            json.dump({'games': [{'game': G1, 'clips': 1}, {'game': G2, 'clips': 2}]}, f)
        os.chmod(os.path.join(self.d, 'selcode_in_p1'), 0o555)

    def tearDown(self):
        os.chmod(os.path.join(self.d, 'selcode_in_p1'), 0o755)
        shutil.rmtree(self.d)

    def turn(self, g, n, clip=None, **coded):
        t = {'point_id': f'LAD-{g}-t{n}', 'global_turn': n, 'board_known': 'yes', 'hand_known': 'partly', 'move_known': 'yes',
             'real_choice': 'yes', 'usable': False, 'kind': 'prepare', 'one_line': 'x', 'reason': 'y'}
        if clip is not None:
            t['clip'] = clip
        t.update(coded)
        return t

    def run_mt(self, inv, *flags):
        with open(os.path.join(self.d, 'inv_out_p1', 'inventory.json'), 'w') as f:
            json.dump(inv, f)
        return subprocess.run([sys.executable, '-B', os.path.join(HERE, 'make_turns.py'), self.d, '1', *flags], capture_output=True, text=True)

    def good(self):
        return [{'game': G1, 'turns': [self.turn(G1, 2), self.turn(G1, 4)]},
                {'game_id': G2, 'turns': [self.turn(G2, 1, clip=1), self.turn(G2, 9, clip='clip02')]}]

    def test_ok_strips_every_coded_field(self):
        r = self.run_mt(self.good())
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.load(open(os.path.join(self.d, 'selcode_in_p1', 'turns.json')))
        self.assertEqual([sorted(t) for t in out['turns']], [['clip', 'game', 'global_turn', 'point_id']] * 4)
        self.assertEqual([(t['point_id'], t['clip']) for t in out['turns']],
                         [(f'LAD-{G1}-t2', 1), (f'LAD-{G1}-t4', 1), (f'LAD-{G2}-t1', 1), (f'LAD-{G2}-t9', 2)])
        txt = open(os.path.join(self.d, 'selcode_in_p1', 'turns.json')).read()
        for w in ('known', 'real_choice', 'usable', 'kind', 'one_line', 'reason', 'partly', 'prepare'):
            self.assertNotIn(w, txt)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.d, 'selcode_in_p1')).st_mode), 0o555)
        self.assertTrue(os.path.exists(os.path.join(self.d, 'TURNS_RECORD_p1.json')))

    def test_dict_keyed_by_game(self):
        g = self.good()
        r = self.run_mt({'games': {G1: {'turns': g[0]['turns']}, G2: {'turns': g[1]['turns']}}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def stops(self, inv, words):
        r = self.run_mt(inv)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(words, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'selcode_in_p1', 'turns.json')))

    def test_missing_game(self):
        self.stops(self.good()[:1], 'missing from the inventory')

    def test_foreign_game(self):
        g = self.good() + [{'game': '20261099_000000000_SR', 'turns': []}]
        self.stops(g, 'not a game of part 1')

    def test_bad_point_id(self):
        g = self.good()
        g[0]['turns'][0]['point_id'] = f'LAD-{G1}-t3'
        self.stops(g, 'not LAD-')

    def test_duplicate(self):
        g = self.good()
        g[0]['turns'].append(self.turn(G1, 2))
        self.stops(g, 'twice')

    def test_linked_turn_without_clip(self):
        g = self.good()
        del g[1]['turns'][0]['clip']
        self.stops(g, 'none of')

    def test_clip_out_of_range(self):
        g = self.good()
        g[1]['turns'][1]['clip'] = 3
        self.stops(g, 'outside 1..2')

    def test_clip_in_one_clip_game(self):
        g = self.good()
        g[0]['turns'][0]['clip'] = 2
        self.stops(g, 'one-clip game')

    def test_unknown_field_names(self):
        g = self.good()
        g[0]['turns'][0] = {'pid': f'LAD-{G1}-t2', 'turn': 2}
        self.stops(g, 'none of')

    def test_two_conflicting_keys(self):
        g = self.good()
        g[0]['turns'][0]['global_turn_count'] = 5
        self.stops(g, 'two different values')

    def test_gt_alias(self):
        """INV p1's shape (addendum 7): the point id under 'id', the global turn under 'gt'."""
        g = self.good()
        for gm in g:
            for t in gm['turns']:
                t['id'] = t.pop('point_id')
                t['gt'] = t.pop('global_turn')
        r = self.run_mt(g)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.load(open(os.path.join(self.d, 'selcode_in_p1', 'turns.json')))
        self.assertEqual([(t['point_id'], t['global_turn']) for t in out['turns']],
                         [(f'LAD-{G1}-t2', 2), (f'LAD-{G1}-t4', 4), (f'LAD-{G2}-t1', 1), (f'LAD-{G2}-t9', 9)])
        self.assertNotIn('"gt"', open(os.path.join(self.d, 'selcode_in_p1', 'turns.json')).read())

    def test_gt_conflicting_with_global_turn(self):
        g = self.good()
        g[0]['turns'][0]['gt'] = 3
        self.stops(g, 'two different values')

    def test_gt_agreeing_with_global_turn(self):
        g = self.good()
        g[0]['turns'][0]['gt'] = 2
        self.assertEqual(self.run_mt(g).returncode, 0)

    def test_null_clip_in_linked_battle_stops_by_default(self):
        g = self.good()
        g[1]['turns'][0]['clip'] = None
        self.stops(g, 'null clip')

    def test_null_clip_passed_through_with_the_flag(self):
        g = self.good()
        g[1]['turns'][0]['clip'] = None
        r = self.run_mt(g, '--null-clip')
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.load(open(os.path.join(self.d, 'selcode_in_p1', 'turns.json')))
        self.assertEqual([t['clip'] for t in out['turns'] if t['game'] == G2], [None, 2])
        rec = json.load(open(os.path.join(self.d, 'TURNS_RECORD_p1.json')))
        self.assertEqual(rec['null_clip_passed_through'], [f'LAD-{G2}-t1'])

    def test_null_clip_flag_keeps_other_checks(self):
        g = self.good()
        g[1]['turns'][1]['clip'] = 3
        r = self.run_mt(g, '--null-clip')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('outside 1..2', r.stderr)

    def test_null_clip_in_one_clip_game_is_clip_1(self):
        g = self.good()
        g[0]['turns'][0]['clip'] = None
        r = self.run_mt(g)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_refuses_existing(self):
        self.assertEqual(self.run_mt(self.good()).returncode, 0)
        p = os.path.join(self.d, 'selcode_in_p1', 'turns.json')
        before = open(p).read()
        r = self.run_mt(self.good()[:1])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('exists already', r.stderr)
        self.assertEqual(open(p).read(), before)


if __name__ == '__main__':
    unittest.main(verbosity=1)
