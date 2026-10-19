#!/usr/bin/env python3
"""The judge prompt and settings are frozen (FROZEN.json, tag judge-prompt-frozen-1). This fails when the prompt texts, the code that lays a prompt out or
the settings change. After the freeze nothing may change until the exam is scored; if a change is ever made on purpose it needs a new freeze:
run `python3 judge.py fingerprint`, update FROZEN.json, and say so in FROZEN.md.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests
"""
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import judge  # noqa: E402


class Frozen(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, 'FROZEN.json'), encoding='utf-8') as f:
            self.frozen = json.load(f)

    def test_the_prompt_and_its_layout_code_are_the_frozen_ones(self):
        self.assertEqual(judge.fingerprint(), self.frozen['fingerprint'],
                         'the judge prompt or its layout code changed after the freeze: see this file\'s docstring')

    def test_the_settings_are_the_frozen_ones(self):
        self.assertEqual(judge.FROZEN, self.frozen['settings'])

    def test_one_fixed_model_id_is_recorded(self):
        self.assertEqual(judge.MODEL, 'claude-sonnet-5-5')
        self.assertEqual(self.frozen['settings']['model'], 'claude-sonnet-5-5')

    def test_the_command_line_defaults_are_the_frozen_settings(self):
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            judge.main(['fingerprint'])
        self.assertEqual(json.loads(buf.getvalue())['settings'], judge.FROZEN)
        # the argparse defaults for --order and --prompt come from FROZEN
        src = open(os.path.join(ROOT, 'judge.py'), encoding='utf-8').read()
        self.assertEqual(src.count("default=FROZEN['order']"), 3)

    def test_a_record_says_whether_it_ran_under_the_frozen_settings(self):
        from unittest import mock
        positions = judge.load_positions()
        pid = 'KW-261013_010837000-t07'
        mk = lambda n: {'n': n, 'key': f'k{n}', 'labels': [f'Retreat:{n}', 'EndTurn'], 'steps': [f'Retreat to slot {n}', 'End the turn'], 'n_steps': 2, 'end': 'end_turn',
                        'final': {'kind': 'end_turn'}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}}
        rec = {pid: {'capped': False, 'total_found': 8, 'plans': [mk(n) for n in range(1, 9)], 'start': {
            'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
            'me': {'board': [], 'hand': [], 'discard': [], 'discard_energy': [], 'deck_size': 9, 'unseen_deck': {'Glimmet': 1}},
            'opp': {'board': [], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}}}}
        reply = ('PLAN: 1\nREASON: x', {'input_tokens': 10, 'output_tokens': 5}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})
        with mock.patch.object(judge, 'call_claude', return_value=reply):
            r_frozen, _, _ = judge.judge_one(pid, positions, rec, judge.FROZEN['order'], True, judge.MODEL)
            r_other, _, _ = judge.judge_one(pid, positions, rec, 'forward', True, judge.MODEL)
        self.assertTrue(r_frozen['frozen'])
        self.assertFalse(r_other['frozen'])
        self.assertEqual(len(r_frozen['prompt_sha256']), 16)
        self.assertNotEqual(r_frozen['prompt_sha256'], r_other['prompt_sha256'])


class OrderPolicy(unittest.TestCase):
    def test_the_frozen_shuffle_is_the_same_every_time_and_differs_between_positions(self):
        ps = [{'n': i} for i in range(1, 30)]
        a = judge.order_plans(ps, 'shuffle-id', 'KW-A')
        self.assertEqual(a, judge.order_plans(ps, 'shuffle-id', 'KW-A'))
        self.assertNotEqual(a, judge.order_plans(ps, 'shuffle-id', 'KW-B'))
        self.assertNotEqual(a, ps)

    def test_v2_grouping_numbers_the_plans_in_the_order_shown(self):
        rec = {'capped': False, 'total_found': 3, 'start': {
            'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
            'me': {'board': [], 'hand': [], 'discard': [], 'discard_energy': [], 'deck_size': 9, 'unseen_deck': {'Glimmet': 1}},
            'opp': {'board': [], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}},
            'plans': [{'n': 1, 'labels': ['Attack:A'], 'steps': ['Attack'], 'n_steps': 1, 'end': 'attack', 'final': {'outcomes': []}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}},
                      {'n': 2, 'labels': ['EndTurn'], 'steps': ['End'], 'n_steps': 1, 'end': 'end_turn', 'final': {}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}},
                      {'n': 3, 'labels': ['Play:X'], 'steps': ['Play X'], 'n_steps': 1, 'end': 'chance', 'final': {'kind': 'your_deck', 'deck_size_before': 9, 'deck_size_after': 7,
                       'hand_size_before': 3, 'hand_size_after': 4}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}}]}
        pos = judge.load_positions()['KW-261013_010837000-t07']
        _, user, shown = judge.render_prompt(pos, rec, 'forward', version='v2')
        self.assertEqual([shown[i]['end'] for i in (1, 2, 3)], ['attack', 'chance', 'end_turn'])
        self.assertLess(user.index('PLANS THAT END WITH AN ATTACK'), user.index('PLANS THAT STOP AT A CHANCE EVENT'))
        _, user_r, shown_r = judge.render_prompt(pos, rec, 'reverse', version='v2')
        self.assertEqual([shown_r[i]['end'] for i in (1, 2, 3)], ['end_turn', 'chance', 'attack'])


if __name__ == '__main__':
    unittest.main()
