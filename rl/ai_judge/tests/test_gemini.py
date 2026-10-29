#!/usr/bin/env python3
"""The Gemini provider (frozen-5): request, parsing, prices, the key, judge_one's rows and how `compare` sees them. Mocks only: nothing here reads a key that matters or touches
the network.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests
"""
import datetime, io, json, os, sys, tempfile, unittest, urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import formal, judge, providers  # noqa: E402

FINGERPRINT = '0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762'  # the prompt fingerprint of frozen-2, -3, -4: the prompt did not change for Gemini
FAKE_KEY = 'AIzaFAKEFAKEFAKEFAKEFAKEFAKE1234567'
PROJECT = 'project-test-1234'  # a Vertex project id for the tests (not a secret)
PID = 'KW-261013_010837000-t07'


def fake_rec(n=8):
    mk = lambda i: {'n': i, 'key': f'k{i}', 'labels': [f'Retreat:{i}', 'EndTurn'], 'steps': [f'Retreat to slot {i}', 'End the turn'], 'n_steps': 2, 'end': 'end_turn',
                    'final': {'kind': 'end_turn'}, 'result': {'board': [], 'hand': [], 'points': [0, 0], 'deck_size': 9}}
    return {'capped': False, 'total_found': n, 'world_seed': 1, 'limits': {'max_plans': 2000, 'max_nodes': 200000, 'max_steps': 30}, 'plans': [mk(i) for i in range(1, n + 1)], 'start': {
        'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
        'me': {'board': [], 'hand': [], 'discard': [], 'discard_energy': [], 'deck_size': 9, 'unseen_deck': {'Glimmet': 1}},
        'opp': {'board': [], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}}}


def interaction(text='PLAN: 1\nREASON: x', status='completed', tin=10000, tout=300, tthought=1700, steps=None):
    return {'id': 'int_1', 'model': 'gemini-4-argon', 'status': status,
            'steps': steps if steps is not None else [{'type': 'user_input', 'content': [{'type': 'text', 'text': 'prompt'}]},
                                                      {'type': 'thought', 'summary': [{'type': 'text', 'text': 'THOUGHT SUMMARY must not be in the reply'}]},
                                                      {'type': 'model_output', 'content': [{'type': 'text', 'text': text}]}],
            'usage': {'total_input_tokens': tin, 'total_output_tokens': tout, 'total_thought_tokens': tthought, 'total_tokens': tin + tout + tthought, 'total_cached_tokens': 0}}


def generate_content(text='PLAN: 1\nREASON: x', finish='STOP', tin=10000, tcand=300, tthought=1700, parts=None, total='auto'):
    """A Vertex AI GenerateContentResponse as the documented message family has it (field names from ai.google.dev/api/generate-content; the first part is a thought)."""
    parts = parts if parts is not None else [{'text': 'THOUGHT SUMMARY must not be in the reply', 'thought': True}, {'text': text}]
    cand = {'content': {'role': 'model', 'parts': parts}}
    if finish is not None:
        cand['finishReason'] = finish
    return {'candidates': [cand], 'modelVersion': 'gemini-4-argon',
            'usageMetadata': {'promptTokenCount': tin, 'candidatesTokenCount': tcand, 'thoughtsTokenCount': tthought, 'totalTokenCount': tin + tcand + tthought if total == 'auto' else total}}


class Parsing(unittest.TestCase):
    def test_a_completed_reply_gives_the_model_output_text_only(self):
        text, usage, model, extra = providers.parse_interaction(interaction(), 'gemini-4-argon')
        self.assertEqual(text, 'PLAN: 1\nREASON: x')
        self.assertNotIn('THOUGHT', text)
        self.assertEqual(extra['stop_reason'], 'end_turn')
        self.assertEqual(extra['content_types'], ['user_input', 'thought', 'model_output'])
        self.assertFalse(extra['usage_missing'])

    def test_thinking_tokens_are_billed_as_output(self):
        _, usage, _, _ = providers.parse_interaction(interaction(tin=10000, tout=300, tthought=1700), 'm')
        self.assertEqual((usage['input_tokens'], usage['output_tokens'], usage['thought_tokens'], usage['answer_tokens']), (10000, 2000, 1700, 300))

    def test_the_providers_total_decides_what_was_billed_as_output(self):
        j = interaction(tin=10000, tout=2000, tthought=1700)
        j['usage']['total_tokens'] = 12000  # the output count already holds the thinking: 10,000 in + 2,000 out in all
        self.assertEqual(providers.parse_interaction(j, 'm')[1]['output_tokens'], 2000)
        j['usage']['total_tokens'] = 100  # a total smaller than the parts it should contain cannot be trusted: fall back to the sum of the parts
        self.assertEqual(providers.parse_interaction(j, 'm')[1]['output_tokens'], 3700)
        del j['usage']['total_tokens']
        self.assertEqual(providers.parse_interaction(j, 'm')[1]['output_tokens'], 3700)

    def test_a_text_content_given_as_a_string_is_read(self):
        steps = [{'type': 'model_output', 'content': 'PLAN: 4\nREASON: s'}]
        self.assertEqual(providers.parse_interaction(interaction(steps=steps), 'm')[0], 'PLAN: 4\nREASON: s')

    def test_a_reply_that_is_not_completed_is_never_an_intact_answer(self):
        for status in ('incomplete', 'failed', 'cancelled', 'in_progress', None):
            _, _, _, extra = providers.parse_interaction(interaction(status=status), 'm')
            self.assertEqual(extra['stop_reason'], f'gemini:{status}', status)

    def test_a_missing_usage_block_is_flagged(self):
        j = interaction()
        del j['usage']
        _, usage, _, extra = providers.parse_interaction(j, 'm')
        self.assertTrue(extra['usage_missing'])
        self.assertIsNone(usage['input_tokens'])
        j = interaction()
        j['usage'] = {'total_tokens': 5}
        self.assertTrue(providers.parse_interaction(j, 'm')[3]['usage_missing'])

    def test_the_text_of_several_parts_and_steps_is_joined_and_other_parts_are_ignored(self):
        steps = [{'type': 'model_output', 'content': [{'type': 'text', 'text': 'PLAN: 2\n'}, {'type': 'image', 'data': 'x'}, {'type': 'text', 'text': 'REASON: y'}]},
                 {'type': 'function_call', 'name': 'f'}, 'not a dict']
        text, _, _, extra = providers.parse_interaction(interaction(steps=steps), 'm')
        self.assertEqual(text, 'PLAN: 2\nREASON: y')
        self.assertIn('function_call', extra['content_types'])

    def test_the_flat_outputs_shape_of_the_beta_is_read_too(self):
        j = {'status': 'completed', 'outputs': [{'type': 'thought', 'text': 'no'}, {'type': 'text', 'text': 'PLAN: 3\nREASON: z'}], 'usage': interaction()['usage']}
        self.assertEqual(providers.parse_interaction(j, 'm')[0], 'PLAN: 3\nREASON: z')

    def test_an_empty_or_odd_body_gives_empty_text_not_a_crash(self):
        for j in ({}, {'steps': []}, {'steps': None, 'outputs': None}, {'steps': [{'type': 'model_output'}]}, {'steps': [{'type': 'model_output', 'content': [{'type': 'text', 'text': None}]}]}):
            text, usage, _, extra = providers.parse_interaction(j, 'm')
            self.assertEqual(text, '')
            self.assertTrue(extra['usage_missing'])

    def test_errors_in_the_body_are_kept(self):
        j = interaction(status='failed')
        j['errors'] = [{'code': 'X'}]
        self.assertEqual(providers.parse_interaction(j, 'm')[3]['errors'], [{'code': 'X'}])


class Request(unittest.TestCase):
    def test_the_frozen_prompt_goes_out_exactly_and_only_the_frozen_settings(self):
        body = providers.build_gemini_request('SYS', 'USER', 'gemini-4-argon', 8000, {'thinking_level': 'high', 'thinking_summaries': 'none'})
        self.assertEqual(body, {'model': 'gemini-4-argon', 'input': 'USER', 'system_instruction': 'SYS', 'store': False,
                                'generation_config': {'max_output_tokens': 8000, 'thinking_level': 'high', 'thinking_summaries': 'none'}})
        self.assertNotIn('temperature', json.dumps(body))

    def test_one_request_with_the_key_in_the_header_and_nothing_else_sent(self):
        seen = {}

        def post(url, headers, body, timeout):
            seen.update(url=url, headers=headers, body=body, timeout=timeout)
            return interaction()
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': FAKE_KEY}), mock.patch.object(providers, '_post_json', side_effect=post) as m:
            text, usage, secs, model, extra = providers.call_gemini('SYS', 'USER')
        self.assertEqual(m.call_count, 1)  # no retry
        self.assertEqual(seen['url'], 'https://generativelanguage.googleapis.com/v1beta/interactions')
        self.assertEqual(seen['headers']['x-goog-api-key'], FAKE_KEY)
        self.assertEqual(seen['body']['generation_config'], {'max_output_tokens': 8000, 'thinking_level': 'high', 'thinking_summaries': 'none'})
        self.assertEqual((text, model, extra['stop_reason']), ('PLAN: 1\nREASON: x', 'gemini-4-argon', 'end_turn'))
        self.assertEqual(usage['output_tokens'], 2000)

    def test_a_temperature_is_refused(self):
        with self.assertRaises(ValueError):
            providers.call_gemini('S', 'U', temperature=0.5)

    def test_an_http_error_stops_the_call_and_never_shows_the_key(self):
        err = urllib.error.HTTPError('u', 400, 'bad', {}, io.BytesIO(json.dumps({'error': {'message': f'API key {FAKE_KEY} not valid'}}).encode()))
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': FAKE_KEY}), mock.patch.object(providers, '_post_json', side_effect=err) as m:
            with self.assertRaises(SystemExit) as cm:
                providers.call_gemini('S', 'U')
        self.assertEqual(m.call_count, 1)
        self.assertIn('API error 400', str(cm.exception))
        self.assertNotIn(FAKE_KEY, str(cm.exception))
        self.assertNotIn('AIza', str(cm.exception))

    def test_a_network_failure_stops_the_call(self):
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': FAKE_KEY}), mock.patch.object(providers, '_post_json', side_effect=urllib.error.URLError('timed out')):
            with self.assertRaises(SystemExit) as cm:
                providers.call_gemini('S', 'U')
        self.assertIn('API error', str(cm.exception))


class Key(unittest.TestCase):
    def home_with(self, text):
        d = tempfile.mkdtemp()
        if text is not None:
            with open(os.path.join(d, '.bashrc'), 'w') as f:
                f.write(text)
        return d

    def load(self, text, env=None):
        with mock.patch.dict(os.environ, {'HOME': self.home_with(text), **(env or {})}):
            if not env:
                os.environ.pop('GEMINI_API_KEY', None)
            return providers.load_key()

    def test_the_environment_wins(self):
        self.assertEqual(self.load('export GEMINI_API_KEY=fromfile\n', {'GEMINI_API_KEY': 'fromenv'}), 'fromenv')

    def test_the_last_export_line_of_bashrc_is_used_as_text(self):
        self.assertEqual(self.load('export GEMINI_API_KEY=old\nalias x=y\nexport GEMINI_API_KEY="new-key"\n'), 'new-key')  # (a key with a blank in it is refused: see test_vertex.Key)
        self.assertEqual(self.load("  export GEMINI_API_KEY='single'  \n"), 'single')
        self.assertEqual(self.load('export GEMINI_API_KEY=plain # a comment\n'), 'plain')
        self.assertEqual(self.load('export ANTHROPIC_API_KEY=other\nexport GEMINI_API_KEY=right\n'), 'right')

    def test_a_line_is_never_executed(self):
        d = tempfile.mkdtemp()
        marker = os.path.join(d, 'executed')
        with self.assertRaises(SystemExit):  # refused as shell syntax (the literal text '$(touch' is not a key), never executed
            self.load(f'export GEMINI_API_KEY=$(touch {marker})\n')
        self.assertFalse(os.path.exists(marker))

    def test_no_key_exits_naming_the_variable_only(self):
        for text in (None, '# nothing\nexport ANTHROPIC_API_KEY=a\n', 'GEMINI_API_KEY=notexported\n'):
            with self.assertRaises(SystemExit) as cm:
                self.load(text)
            self.assertIn('GEMINI_API_KEY', str(cm.exception))

    def test_scrub_removes_the_key_and_key_shaped_text(self):
        self.assertNotIn(FAKE_KEY, providers.scrub(f'bad key {FAKE_KEY}', FAKE_KEY))
        self.assertNotIn('AIza', providers.scrub('x AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAA y', None))
        self.assertEqual(providers.scrub('plain', 'k'), 'plain')


class Prices(unittest.TestCase):
    def test_the_price_in_force_changes_after_2026_11_30(self):
        self.assertEqual(providers.gemini_price(datetime.date(2026, 10, 21)), (2.0, 10.0))
        self.assertEqual(providers.gemini_price(datetime.date(2026, 11, 30)), (2.0, 10.0))
        self.assertEqual(providers.gemini_price(datetime.date(2026, 12, 1)), (4.0, 20.0))

    def test_the_reservation_is_the_higher_price_whatever_the_date(self):
        self.assertEqual(providers.gemini_reserve_price(), (4.0, 20.0))
        self.assertTrue(all(r >= a for r, a in zip(providers.gemini_reserve_price(), providers.gemini_price(datetime.date(2026, 10, 21)))))

    def test_cost_counts_input_in_full_and_thinking_as_output(self):
        usage = {'input_tokens': 10000, 'output_tokens': 2000, 'thought_tokens': 1700, 'answer_tokens': 300, 'cached_tokens': 5000}
        c = judge.gemini_cost_of(usage, 9999, 8000, datetime.date(2026, 10, 21))
        self.assertAlmostEqual(c['usd'], 10000 * 2 / 1e6 + 2000 * 10 / 1e6)  # the cached part is NOT discounted
        self.assertFalse(c['usd_is_worst_case'])
        c = judge.gemini_cost_of(usage, 9999, 8000, datetime.date(2026, 12, 1))
        self.assertAlmostEqual(c['usd'], 10000 * 4 / 1e6 + 2000 * 20 / 1e6)

    def test_a_reply_without_usage_is_charged_its_worst_case(self):
        c = judge.gemini_cost_of({'input_tokens': None, 'output_tokens': 0}, 12000, 8000, datetime.date(2026, 10, 21))
        self.assertTrue(c['usd_is_worst_case'])
        self.assertAlmostEqual(c['usd'], 12000 * 4 / 1e6 + 8000 * 20 / 1e6)

    def test_a_reply_whose_output_count_is_missing_is_charged_its_worst_case_too(self):
        # an input count with no output count at all (usage_missing from the parser) would otherwise be costed as a free answer
        c = judge.gemini_cost_of({'input_tokens': 5000, 'output_tokens': 0}, 12000, 8000, datetime.date(2026, 10, 21), usage_missing=True)
        self.assertTrue(c['usd_is_worst_case'])
        self.assertAlmostEqual(c['usd'], 12000 * 4 / 1e6 + 8000 * 20 / 1e6)
        j = interaction()
        j['usage'] = {'total_input_tokens': 5000}
        _, usage, _, extra = providers.parse_interaction(j, 'm')
        self.assertTrue(extra['usage_missing'])
        self.assertTrue(judge.gemini_cost_of(usage, 12000, 8000, usage_missing=extra['usage_missing'])['usd_is_worst_case'])


class JudgeRows(unittest.TestCase):
    def setUp(self):
        self.positions = judge.load_positions()
        self.rec = {PID: fake_rec()}

    def run_one(self, interaction_json=None, **kw):
        j = interaction_json or interaction()
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': FAKE_KEY}), mock.patch.object(providers, '_post_json', return_value=j):
            args = dict(provider='gemini', thinking_level=None)
            args.update(kw)
            model = args.pop('model', 'gemini-4-argon')
            return judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, model, **args)

    def test_the_prompt_is_the_frozen_prompt_and_the_fingerprint_did_not_change(self):
        self.assertEqual(judge.fingerprint(), FINGERPRINT)
        with mock.patch.object(judge, 'call_claude', return_value=('PLAN: 1\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})):
            anthropic_row, system, user = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, judge.MODEL)
        gemini_row, gsystem, guser = self.run_one()
        self.assertEqual((gsystem, guser), (system, user))
        self.assertEqual(gemini_row['prompt_sha256'], anthropic_row['prompt_sha256'])
        self.assertEqual(gemini_row['plan_list_sha256'], anthropic_row['plan_list_sha256'])

    def test_a_frozen_gemini_row_records_its_settings_and_costs_its_tokens(self):
        r, _, _ = self.run_one()
        self.assertTrue(r['frozen'])
        self.assertEqual({k: r[k] for k in ('provider', 'model', 'max_tokens', 'temperature', 'thinking_level', 'thinking_summaries')}, judge.judge_settings('gemini'))
        self.assertEqual(judge.judge_settings('gemini')['model'], 'gemini-4-argon')
        self.assertEqual((r['stop_reason'], r['parse_error']), ('end_turn', None))
        self.assertIsNotNone(r['plan_number'])
        self.assertEqual(r['cost']['output_tokens'], 2000)
        self.assertEqual(r['raw'], 'PLAN: 1\nREASON: x')
        self.assertNotIn('THOUGHT', json.dumps(r))

    def test_anthropic_rows_keep_the_frozen_4_shape(self):
        with mock.patch.object(judge, 'call_claude', return_value=('PLAN: 1\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})):
            r, _, _ = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, judge.MODEL)
        self.assertNotIn('provider', r)
        self.assertNotIn('thinking_level', r)
        self.assertTrue(r['frozen'])

    def test_any_other_setting_makes_the_row_not_frozen(self):
        for kw in ({'thinking_level': 'medium'}, {'thinking_level': 'low'}, {'model': 'gemini-4-other'}, {'max_tokens': 4000}):
            r, _, _ = self.run_one(**kw)
            self.assertFalse(r['frozen'], kw)

    def test_the_anthropic_model_is_not_the_gemini_freeze(self):
        r, _, _ = self.run_one(model='claude-sonnet-5-5')
        self.assertFalse(r['frozen'])

    def test_a_reply_cut_by_the_cap_keeps_no_choice_even_with_a_plan_line(self):
        r, _, _ = self.run_one(interaction(status='incomplete', text='PLAN: 2\nREASON: cut'))
        self.assertIsNone(r['plan_number'])
        self.assertIn('cut at max_tokens=8000', r['parse_error'])
        self.assertEqual(r['stop_reason'], 'gemini:incomplete')

    def test_any_other_unfinished_status_keeps_no_choice(self):
        r, _, _ = self.run_one(interaction(status='failed', text='PLAN: 2\nREASON: x'))
        self.assertIsNone(r['plan_number'])
        self.assertIn('did not finish (gemini:failed)', r['parse_error'])

    def test_the_same_parser_and_invalid_label_handling_apply(self):
        for text, ok in (('PLAN: 3\nREASON: fine', True), ('PLAN: 4 or 7\nREASON: x', False), ('PLAN: 99\nREASON: x', False), ('I choose plan 2', False), ('PLAN: 2', True)):
            r, _, _ = self.run_one(interaction(text=text))
            self.assertEqual(r['plan_number'] is not None, ok, text)
        r, _, _ = self.run_one(interaction(text='PLAN: 2'))
        self.assertEqual(r['parse_warning'], 'no REASON line (choice kept)')

    def test_a_reply_without_usage_is_costed_at_its_worst_case(self):
        j = interaction()
        del j['usage']
        r, _, _ = self.run_one(j)
        self.assertTrue(r['cost']['usd_is_worst_case'])
        self.assertTrue(r['usage_missing'])

    def test_a_dry_run_sends_nothing_and_names_the_provider(self):
        with mock.patch.object(providers, '_post_json') as m:
            r, _, _ = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], False, 'gemini-4-argon', provider='gemini')
        m.assert_not_called()
        self.assertEqual((r['provider'], r['thinking_level'], r['dry_run']), ('gemini', 'high', True))

    def test_a_thinking_level_for_anthropic_or_an_unknown_provider_is_refused(self):
        with self.assertRaises(ValueError):
            judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], False, judge.MODEL, thinking_level='high')
        with self.assertRaises(ValueError):
            judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], False, judge.MODEL, provider='openai')


class Identity(unittest.TestCase):
    def test_frozen_settings_and_the_prompt_fingerprint_are_untouched(self):
        self.assertEqual(judge.fingerprint(), FINGERPRINT)
        self.assertEqual(judge.FROZEN['model'], 'claude-sonnet-5-5')
        self.assertEqual(set(judge.FROZEN), {'model', 'prompt_version', 'order', 'compact_above', 'max_tokens', 'temperature', 'plan_world_seed', 'max_plans', 'max_nodes', 'max_steps'})

    def test_the_judge_block_records_provider_model_settings_prices_mapping_and_sources(self):
        b = judge.frozen_judge_block('gemini')  # the frozen-5 block (the AI Studio provider is still in the code)
        self.assertEqual((b['provider'], b['settings']['model'], b['settings']['thinking_level'], b['settings']['max_tokens']), ('gemini', 'gemini-4-argon', 'high', 8000))
        self.assertEqual(b['price_per_mtok'], {'through_2026-11-30': [2.0, 10.0], 'from_2026-12-01': [4.0, 20.0], 'reservation': [4.0, 20.0]})
        self.assertTrue(all(u.startswith('https://ai.google.dev/') for u in b['sources']))
        for k in ('prompt', 'output cap', 'reasoning', 'temperature', 'retries'):
            self.assertIn(k, b['mapping'])
        self.assertIn('CANNOT MATCH', b['mapping']['output cap'])
        json.dumps(b)  # it goes in FROZEN.json

    def test_a_freeze_record_without_a_judge_block_is_the_anthropic_freeze(self):
        provider, settings = judge.judge_expectation({})
        self.assertEqual((provider, settings), ('anthropic', {'model': 'claude-sonnet-5-5', 'max_tokens': 8000, 'temperature': None}))
        provider, settings = judge.judge_expectation({'judge': judge.frozen_judge_block('gemini')})
        self.assertEqual((provider, settings), ('gemini', judge.judge_settings('gemini')))
        provider, settings = judge.judge_expectation({'judge': judge.frozen_judge_block('gemini-vertex')})
        self.assertEqual((provider, settings), ('gemini-vertex', judge.judge_settings('gemini-vertex')))

    def test_the_current_freeze_record_carries_the_judge_block_it_was_made_from(self):
        with open(os.path.join(ROOT, 'FROZEN.json'), encoding='utf-8') as f:
            frozen = json.load(f)
        if 'judge' in frozen:  # frozen-5 on
            self.assertEqual(frozen['judge'], json.loads(json.dumps(judge.frozen_judge_block())))
        else:
            self.skipTest('the record is an Anthropic freeze (no judge block)')

    def test_an_unknown_provider_has_no_settings(self):
        with self.assertRaises(ValueError):
            judge.judge_settings('openai')


class CompareSeesGeminiRows(unittest.TestCase):
    """formal.check_chosen_plan with the settings a frozen-5 freeze expects."""

    def check(self, row_extra, settings=None, **kw):
        rec = {'plans': [{'key': 'k1', 'labels': ['EndTurn'], 'end': 'end_turn'}]}
        row = {'position': 'P', 'bot': 'judge', 'plan_number': 1, 'shown_number': 1, 'plan_list_sha256': 'h', 'plan_key': 'k1', 'plan': ['EndTurn'], 'cut': 'end_turn',
               'prompt_sha256': 'ph', 'raw': 'PLAN: 1\nREASON: x', 'frozen': True, 'stop_reason': 'end_turn', **judge.judge_settings('gemini'), **row_extra}
        exp = lambda pid, r: {'prompt_sha256': 'ph', 'shown': {1: 1}, 'parse': lambda raw: 1, 'settings': settings or judge.judge_settings('gemini')}
        return [k for k, _ in formal.check_chosen_plan(row, 'judge', rec, 'h', exp, True)]

    def test_a_good_gemini_row_passes(self):
        self.assertEqual(self.check({}), [])

    def test_a_row_with_other_settings_or_a_missing_setting_is_not_frozen(self):
        self.assertEqual(self.check({'thinking_level': 'medium'}), ['not_frozen'])
        self.assertEqual(self.check({'model': 'gemini-4-other'}), ['not_frozen'])
        self.assertEqual(self.check({'max_tokens': 4000}), ['not_frozen'])
        row_missing = self.check({'provider': 'anthropic'})
        self.assertEqual(row_missing, ['not_frozen'])

    def test_an_anthropic_row_against_the_gemini_freeze_fails_every_setting(self):
        kinds = self.check({'provider': None, 'model': judge.MODEL, 'thinking_level': None, 'thinking_summaries': None})
        self.assertEqual(kinds, ['not_frozen'] * 4)

    def test_an_unfinished_gemini_reply_is_a_truncated_reply(self):
        self.assertEqual(self.check({'stop_reason': 'gemini:incomplete'}), ['truncated_reply'])
        self.assertEqual(self.check({'stop_reason': 'gemini:failed'}), ['truncated_reply'])
        self.assertEqual(self.check({'stop_reason': 'max_tokens'}), ['truncated_reply'])

    def test_the_anthropic_expectation_is_unchanged(self):
        self.assertEqual(self.check({'model': judge.MODEL}, settings=judge.judge_settings('anthropic')), [])  # a frozen-4 row (Anthropic model) against the Anthropic expectation
        self.assertEqual(self.check({}, settings=judge.judge_settings('anthropic')), ['not_frozen'])  # a Gemini row against it: another model


class CommandLine(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(judge, 'list_plans', return_value={PID: fake_rec()}), mock.patch('sys.stdout', out), mock.patch('sys.stderr', err):
            code = judge.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_a_gemini_dry_run_defaults_to_the_frozen_gemini_model(self):
        code, out, _ = self.run_main(['judge', '--ids', PID, '--provider', 'gemini'])
        self.assertEqual(code, 0)
        self.assertIn('[dry run]', out)
        row = json.loads([l for l in out.splitlines() if l.startswith('{')][0])
        self.assertEqual((row['provider'], row['model'], row['thinking_level'], row['frozen'], row['dry_run']), ('gemini', 'gemini-4-argon', 'high', True, True))

    def test_the_default_provider_is_still_anthropic(self):
        code, out, _ = self.run_main(['judge', '--ids', PID])
        row = json.loads([l for l in out.splitlines() if l.startswith('{')][0])
        self.assertEqual((row['model'], 'provider' in row), (judge.MODEL, False))

    def test_a_temperature_or_a_thinking_level_on_the_wrong_provider_exits(self):
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--provider', 'gemini', '--temperature', '0.5'])
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--thinking-level', 'high'])

    def test_a_live_gemini_call_through_the_cli_uses_the_provider_and_prices_at_the_day(self):
        reply = ('PLAN: 1\nREASON: x', {'input_tokens': 1000, 'output_tokens': 500, 'thought_tokens': 400, 'answer_tokens': 100, 'cached_tokens': 0}, 0.1, 'gemini-4-argon',
                 {'stop_reason': 'end_turn', 'content_types': ['model_output'], 'status': 'completed', 'usage_missing': False})
        with mock.patch.object(providers, 'call_gemini', return_value=reply) as m:
            code, out, err = self.run_main(['judge', '--ids', PID, '--provider', 'gemini', '--live', '--max-calls', '1'])
        self.assertEqual(code, 0)
        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.call_args.kwargs['thinking'], {'thinking_level': 'high', 'thinking_summaries': 'none'})
        self.assertIn('Gemini 4 Argon', err)  # the price note of the provider, not the Anthropic one


if __name__ == '__main__':
    unittest.main()
