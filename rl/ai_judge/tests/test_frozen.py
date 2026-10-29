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

    def test_the_sources_and_executables_are_the_frozen_ones(self):
        import freeze_identity
        self.assertEqual(self.frozen['tag'], 'judge-prompt-frozen-7')
        # the sources, the engine tree and (where built) the lister and baseline executables must equal FROZEN.json
        self.assertEqual(freeze_identity.check(self.frozen), [])

    def test_earlier_freezes_are_recorded_as_superseded_not_rewritten(self):
        tags = [s['tag'] for s in self.frozen['supersedes']]
        self.assertEqual(tags, ['judge-prompt-frozen-6', 'judge-prompt-frozen-5', 'judge-prompt-frozen-4', 'judge-prompt-frozen-3', 'judge-prompt-frozen-2', 'judge-prompt-frozen-1'])
        for s in self.frozen['supersedes'][:5]:  # the prompt is the one frozen-2 to -6 froze
            self.assertEqual(s['fingerprint'], self.frozen['fingerprint'])
        self.assertEqual(self.frozen['supersedes'][0]['commit'], '3783c9ab16d27cd9ff9dcc071bea20bada5a8fe0')
        self.assertEqual(self.frozen['supersedes'][1]['commit'], '544d80ff891b8277aa5eb8f189b10e3a56ac86e6')
        self.assertEqual(self.frozen['supersedes'][2]['commit'], '72eea776ea745be837be94320068402eb81fa11a')
        self.assertEqual(self.frozen['supersedes'][3]['commit'], '316f3577142238083c8c0ca222d2cc06afdd67ff')

    def test_frozen_7_changes_the_judge_not_the_lister_the_baseline_or_the_prompt(self):
        self.assertEqual(self.frozen['fingerprint'], '0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762')
        self.assertEqual(self.frozen['plans_binary_sha256'], 'bd4eeb6e4579f88c12b5a889178af2f34071a1bca9b1675552b4e47b418ea00b')
        self.assertEqual(self.frozen['baseline']['binary_sha256'], 'f35a1a99188806c7713cc40dd8fff65172c21a15d5449174f1cd3c1cfc40ad36')
        self.assertEqual(self.frozen['baseline']['engine_tree'], '70652fff03af511e32a169e16209e158a998dda6')
        block = self.frozen['judge']
        self.assertEqual((block['provider'], block['settings']['model'], block['settings']['thinking_level'], block['settings']['max_tokens']), ('gemini-vertex', 'gemini-4-argon', 'HIGH', 32768))
        self.assertEqual((block['key_variable'], block['project_variable'], block['settings']['location']), ('VERTEX_API_KEY', 'VERTEX_PROJECT', 'global'))
        self.assertEqual(block['failed_judge_rows']['default'], 'abort')  # run 1's behaviour is the default; 'miss' is an explicit, recorded setting
        self.assertEqual(block['failed_judge_rows']['preregistered_for_run_2'], 'miss')
        self.assertEqual(block, json.loads(json.dumps(judge.frozen_judge_block())))

    def test_a_gemini_freeze_record_must_carry_its_judge_block(self):
        import copy, freeze_identity
        rec = copy.deepcopy(self.frozen)
        del rec['judge']
        self.assertTrue(any('no judge block' in d for d in freeze_identity.check(rec)))  # without it `compare` would silently expect the Anthropic judge
        rec = copy.deepcopy(self.frozen)
        rec['judge']['settings']['max_tokens'] = 8000
        self.assertTrue(any('judge block' in d and 'differs' in d for d in freeze_identity.check(rec)))
        old = copy.deepcopy(self.frozen)
        del old['judge']
        old['tag'] = 'judge-prompt-frozen-4'  # the Anthropic freezes never had one
        self.assertFalse(any('judge block' in d for d in freeze_identity.check(old)))

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
        rec = {pid: {'capped': False, 'total_found': 8, 'world_seed': 1, 'limits': {'max_plans': 2000, 'max_nodes': 200000, 'max_steps': 30}, 'plans': [mk(n) for n in range(1, 9)], 'start': {
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


class GenerationInputsAreChecked(unittest.TestCase):
    def test_a_different_world_seed_or_limit_makes_the_record_not_frozen(self):
        from unittest import mock
        pid = 'KW-261013_010837000-t07'
        positions = judge.load_positions()
        mk = lambda n: {'n': n, 'key': f'k{n}', 'labels': [f'Retreat:{n}', 'EndTurn'], 'steps': [f'Retreat {n}', 'End the turn'], 'n_steps': 2, 'end': 'end_turn',
                        'final': {'kind': 'end_turn'}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}}
        start = {'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
                 'me': {'board': [], 'hand': [], 'discard': [], 'discard_energy': [], 'deck_size': 9, 'unseen_deck': {'Glimmet': 1}},
                 'opp': {'board': [], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}}
        good = {'capped': False, 'total_found': 3, 'world_seed': 1, 'limits': {'max_plans': 2000, 'max_nodes': 200000, 'max_steps': 30},
                'plans': [mk(1), mk(2), mk(3)], 'start': start}
        reply = ('PLAN: 1\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})
        flags = []
        for rec in (good, {**good, 'world_seed': 2}, {**good, 'limits': {**good['limits'], 'max_plans': 5}}, {**good, 'limits': {**good['limits'], 'max_steps': 9}}):
            with mock.patch.object(judge, 'call_claude', return_value=reply):
                flags.append(judge.judge_one(pid, positions, {pid: rec}, judge.FROZEN['order'], True, judge.MODEL)[0]['frozen'])
        self.assertEqual(flags, [True, False, False, False])

    def test_baseline_runner_fails_loudly_on_a_failed_or_short_run(self):
        import subprocess, tempfile, stat
        d = tempfile.mkdtemp()
        bad = os.path.join(d, 'fake_pg_pos.sh')
        open(bad, 'w').write('#!/bin/bash\necho \'{"kind":"free","id":"KW-261013_010837000-t07","seed":1,"plan":[],"cut":"end of turn"}\'\nexit 3\n')
        os.chmod(bad, 0o755)
        with self.assertRaises(SystemExit) as cm:
            judge.run_pg_pos('km3', ['KW-261013_010837000-t07'], [1], {}, bin_path=bad)
        self.assertIn('failed', str(cm.exception))
        short = os.path.join(d, 'short.sh')
        open(short, 'w').write('#!/bin/bash\necho \'{"kind":"free","id":"KW-261013_010837000-t07","seed":1,"plan":[],"cut":"x"}\'\n')
        os.chmod(short, 0o755)
        with self.assertRaises(SystemExit) as cm:
            judge.run_pg_pos('km3', ['KW-261013_010837000-t07'], [1, 2], {}, bin_path=short)  # seed 2 missing
        self.assertIn('expected exactly one', str(cm.exception))
