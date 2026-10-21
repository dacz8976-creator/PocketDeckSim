#!/usr/bin/env python3
"""The Vertex AI provider (frozen-6): GenerateContent request, response parsing, the key, judge_one's rows, how `compare` sees them, the command line, the shared request error
handling. Mocks only: no key that matters is read and nothing touches the network.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests
"""
import contextlib, http.server, io, json, os, sys, tempfile, threading, unittest, urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import formal, judge, providers  # noqa: E402
from test_gemini import FAKE_KEY, FINGERPRINT, PID, PROJECT, fake_rec, generate_content, interaction  # noqa: E402

URL = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/gemini-4-argon:generateContent'


class Parsing(unittest.TestCase):
    def test_a_finished_reply_gives_the_answer_text_and_skips_thought_parts(self):
        text, usage, model, extra = providers.parse_generate_content(generate_content(), 'gemini-4-argon')
        self.assertEqual(text, 'PLAN: 1\nREASON: x')
        self.assertNotIn('THOUGHT', text)
        self.assertEqual((extra['stop_reason'], extra['finish_reason'], extra['content_types'], extra['n_candidates'], extra['usage_missing']), ('end_turn', 'STOP', ['thought', 'text'], 1, False))
        self.assertEqual((usage['input_tokens'], usage['output_tokens'], usage['thought_tokens'], usage['answer_tokens']), (10000, 2000, 1700, 300))

    def test_only_a_part_flagged_thought_true_is_skipped(self):
        parts = [{'text': 'PLAN: 2\n', 'thought': False}, {'text': 'hidden', 'thought': True}, {'inlineData': {'data': 'x'}}, {'text': 'REASON: y'}]
        text, _, _, extra = providers.parse_generate_content(generate_content(parts=parts), 'm')
        self.assertEqual(text, 'PLAN: 2\nREASON: y')
        self.assertEqual(extra['content_types'], ['text', 'thought', 'other', 'text'])

    def test_any_finish_reason_but_stop_is_never_an_intact_answer(self):
        for reason in ('MAX_TOKENS', 'SAFETY', 'CONTINUATION', 'OTHER', 'FINISH_REASON_UNSPECIFIED', 'RECITATION', 'PROHIBITED_CONTENT'):
            self.assertEqual(providers.parse_generate_content(generate_content(finish=reason), 'm')[3]['stop_reason'], f'vertex:{reason}', reason)

    def test_no_finish_reason_no_candidate_and_a_blocked_prompt_are_not_answers(self):
        text, _, _, extra = providers.parse_generate_content(generate_content(finish=None), 'm')  # a candidate that has not stopped: its text is kept, but it is not a finished answer
        self.assertEqual((extra['stop_reason'], extra['finish_reason'], text), ('vertex:NO_FINISH_REASON', None, 'PLAN: 1\nREASON: x'))
        self.assertEqual(providers.parse_generate_content({'candidates': []}, 'm')[3]['stop_reason'], 'vertex:NO_CANDIDATE')
        blocked = {'promptFeedback': {'blockReason': 'SAFETY'}, 'usageMetadata': {'promptTokenCount': 5000}}
        text, usage, _, extra = providers.parse_generate_content(blocked, 'm')
        self.assertEqual((text, extra['stop_reason'], extra['block_reason'], extra['n_candidates']), ('', 'vertex:BLOCKED_SAFETY', 'SAFETY', 0))
        self.assertTrue(extra['usage_missing'])  # no output count: the cost is charged at its worst case, not as a free call

    def test_the_first_candidate_is_used_and_the_count_is_recorded(self):
        j = generate_content(text='PLAN: 1\nREASON: a')
        j['candidates'].append({'content': {'parts': [{'text': 'PLAN: 2'}]}, 'finishReason': 'STOP'})
        text, _, _, extra = providers.parse_generate_content(j, 'm')
        self.assertEqual((text, extra['n_candidates']), ('PLAN: 1\nREASON: a', 2))

    def test_the_providers_total_decides_what_was_billed_as_output(self):
        j = generate_content(tin=10000, tcand=2000, tthought=1700, total=12000)  # the candidate count already holds the thinking
        self.assertEqual(providers.parse_generate_content(j, 'm')[1]['output_tokens'], 2000)
        j = generate_content(tin=10000, tcand=300, tthought=1700)  # the usual shape: answer and thinking counted apart
        self.assertEqual(providers.parse_generate_content(j, 'm')[1]['output_tokens'], 2000)
        j = generate_content(tin=10000, tcand=2000, tthought=1700, total=100)  # a total below its own parts cannot be trusted: the sum of the parts
        self.assertEqual(providers.parse_generate_content(j, 'm')[1]['output_tokens'], 3700)
        j = generate_content(tin=10000, tcand=2000, tthought=1700)
        del j['usageMetadata']['totalTokenCount']
        self.assertEqual(providers.parse_generate_content(j, 'm')[1]['output_tokens'], 3700)

    def test_a_missing_or_unusable_usage_block_is_flagged(self):
        j = generate_content()
        del j['usageMetadata']
        self.assertTrue(providers.parse_generate_content(j, 'm')[3]['usage_missing'])
        for bad in (None, True, '10', -5, 1.5, [1]):
            j = generate_content()
            j['usageMetadata']['promptTokenCount'] = bad
            _, usage, _, extra = providers.parse_generate_content(j, 'm')
            self.assertTrue(extra['usage_missing'], bad)
            self.assertIsNone(usage['input_tokens'], bad)
        j = generate_content()
        j['usageMetadata'].pop('candidatesTokenCount')
        j['usageMetadata'].pop('thoughtsTokenCount')
        self.assertTrue(providers.parse_generate_content(j, 'm')[3]['usage_missing'])

    def test_cached_input_is_not_discounted_and_is_recorded(self):
        j = generate_content()
        j['usageMetadata']['cachedContentTokenCount'] = 4096
        usage = providers.parse_generate_content(j, 'm')[1]
        self.assertEqual((usage['input_tokens'], usage['cached_tokens']), (10000, 4096))

    def test_odd_bodies_give_empty_text_not_a_crash(self):
        for j in ({}, {'candidates': None}, {'candidates': []}, {'candidates': ['x']}, {'candidates': [{}]}, {'candidates': [{'content': None}]}, {'candidates': [{'content': {'parts': None}}]},
                  {'candidates': [{'content': {'parts': ['x', {'text': None}]}}]}, {'promptFeedback': 'x', 'usageMetadata': 'y'}):
            text, usage, model, extra = providers.parse_generate_content(j, 'gemini-4-argon')
            self.assertEqual((text, model), ('', 'gemini-4-argon'))
            self.assertTrue(extra['stop_reason'].startswith('vertex:'), j)
            self.assertTrue(extra['usage_missing'])

    def test_the_model_version_the_service_reports_is_returned(self):
        j = generate_content()
        j['modelVersion'] = 'gemini-4-argon-001'
        self.assertEqual(providers.parse_generate_content(j, 'gemini-4-argon')[2], 'gemini-4-argon-001')
        j['modelVersion'] = 7
        self.assertEqual(providers.parse_generate_content(j, 'gemini-4-argon')[2], 'gemini-4-argon')


class Request(unittest.TestCase):
    def test_the_body_is_the_frozen_prompt_and_only_the_frozen_settings(self):
        body = providers.build_vertex_request('SYS', 'USER', 32768, 'HIGH')
        self.assertEqual(body, {'systemInstruction': {'parts': [{'text': 'SYS'}]}, 'contents': [{'role': 'user', 'parts': [{'text': 'USER'}]}],
                                'generationConfig': {'maxOutputTokens': 32768, 'thinkingConfig': {'thinkingLevel': 'HIGH'}}})
        text = json.dumps(body)
        for absent in ('temperature', 'topP', 'topK', 'includeThoughts', 'safetySettings', 'candidateCount', 'thinkingBudget', 'seed', 'stopSequences'):
            self.assertNotIn(absent, text)

    def test_the_url_is_the_documented_endpoint_and_a_model_id_cannot_change_the_path(self):
        self.assertEqual(providers.vertex_url('gemini-4-argon', PROJECT, 'global'), URL)
        self.assertEqual(providers.vertex_url('gemini-4-argon', PROJECT), URL)  # the location defaults to the frozen one
        self.assertEqual(providers.VERTEX_URL.format(project=PROJECT, location='global', model='gemini-4-argon'), URL)
        for bad in ('', None, 'a/b', '../x', 'a:b', 'A', 'a b', 'a?b', 7, 'a\n'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                providers.vertex_url(bad, PROJECT)
        for bad in ('', None, 'a/b', '../x', 'p:1', 'UPPER', 'a b', 'x?y', 'short', 7, 'project-ab12cd34-ef56-7890-abc\n', '12345', 'p' * 31, 'ends-with-', '-starts'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                providers.vertex_url('gemini-4-argon', bad)  # nothing but a project id or number can reach the path
        for bad in ('a/b', '../x', 'US', 'a b', 'x?y', 7, '-x', 'a\n'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                providers.vertex_url('gemini-4-argon', PROJECT, bad)
        self.assertEqual(providers.vertex_url('gemini-4-argon', 'project-ab12cd34-ef56-7890-abc', 'global').split('/')[4:7], ['projects', 'project-ab12cd34-ef56-7890-abc', 'locations'])
        self.assertTrue(providers.vertex_url('gemini-4-argon', '123456789012', 'us').endswith('/projects/123456789012/locations/us/publishers/google/models/gemini-4-argon:generateContent'))

    def test_an_invalid_project_setting_never_stops_a_dry_run_and_its_value_is_never_echoed(self):
        key = 'AQ.Ab8RN6exampleexampleexampleexample'  # an API key pasted into the project setting by mistake
        for bad in ('My First Project', key):
            with mock.patch.dict(os.environ, {'VERTEX_PROJECT': bad}):
                self.assertIsNone(providers.vertex_project(required=False, strict=False))
                r, _, _ = judge.judge_one(PID, judge.load_positions(), {PID: fake_rec()}, judge.FROZEN['order'], False, 'gemini-4-argon', provider='gemini-vertex', max_tokens=32768)
                self.assertIsNone(r['vertex_project'])  # a dry run (and a mock run) needs no project: an unusable value is treated as not set
                for call in (providers.vertex_project, lambda: providers.call_vertex('S', 'U')):
                    with self.assertRaises(SystemExit) as cm:
                        call()  # a live call does stop, and says which setting, never what it held
                    self.assertIn('VERTEX_PROJECT', str(cm.exception))
                    self.assertNotIn(bad[:8], str(cm.exception))
            with self.assertRaises(SystemExit) as cm:
                providers.set_vertex_project(bad)
            self.assertNotIn(bad[:8], str(cm.exception))
            with self.assertRaises(ValueError) as cm:
                providers.vertex_url('gemini-4-argon', bad)
            self.assertNotIn(bad[:8], str(cm.exception))
        providers.set_vertex_project(None)

    def test_the_project_comes_from_the_flag_then_the_environment_and_a_missing_one_stops_the_run(self):
        try:
            with mock.patch.dict(os.environ, {'VERTEX_PROJECT': 'from-env-12345'}):
                self.assertEqual(providers.vertex_project(), 'from-env-12345')
                providers.set_vertex_project('from-flag-12345')
                self.assertEqual(providers.vertex_project(), 'from-flag-12345')  # the run kit's flag wins over the environment
                providers.set_vertex_project(None)
                self.assertEqual(providers.vertex_project(), 'from-env-12345')
            with mock.patch.dict(os.environ, {}):
                os.environ.pop('VERTEX_PROJECT', None)
                self.assertIsNone(providers.vertex_project(required=False))
                with self.assertRaises(SystemExit) as cm:
                    providers.vertex_project()
                self.assertIn('VERTEX_PROJECT', str(cm.exception))
                with self.assertRaises(SystemExit):
                    providers.call_vertex('S', 'U')  # no project: no call (and no key needed to find that out)
            with mock.patch.dict(os.environ, {'VERTEX_PROJECT': 'NOT A PROJECT'}), self.assertRaises(SystemExit):
                providers.vertex_project()
            with self.assertRaises(SystemExit):
                providers.set_vertex_project('bad/project')
        finally:
            providers.set_vertex_project(None)

    def test_one_request_the_key_in_the_header_only_and_nothing_else_sent(self):
        seen = {}

        def post(url, headers, body, timeout):
            seen.update(url=url, headers=headers, body=body, timeout=timeout)
            return generate_content()
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', side_effect=post) as m:
            text, usage, secs, model, extra = providers.call_vertex('SYS', 'USER')
        self.assertEqual(m.call_count, 1)  # no retry
        self.assertEqual(seen['url'], URL)
        self.assertNotIn(FAKE_KEY, seen['url'])
        self.assertNotIn(FAKE_KEY, json.dumps(seen['body']))
        self.assertEqual(seen['headers']['x-goog-api-key'], FAKE_KEY)
        self.assertEqual(seen['body'], providers.build_vertex_request('SYS', 'USER', 32768, 'HIGH'))
        self.assertGreaterEqual(seen['timeout'], 600)  # a call that thinks up to 32,768 tokens takes minutes
        self.assertEqual((text, model, extra['stop_reason']), ('PLAN: 1\nREASON: x', 'gemini-4-argon', 'end_turn'))
        self.assertEqual(usage['output_tokens'], 2000)

    def test_a_temperature_is_refused(self):
        with self.assertRaises(ValueError):
            providers.call_vertex('S', 'U', temperature=0.5)

    def test_the_frozen_settings_are_the_ones_the_coordinator_pre_registered(self):
        self.assertEqual(providers.VERTEX_FROZEN, {'provider': 'gemini-vertex', 'model': 'gemini-4-argon', 'location': 'global', 'max_tokens': 32768, 'temperature': None, 'thinking_level': 'HIGH'})
        self.assertEqual((providers.VERTEX_KEY_VAR, providers.VERTEX_PROJECT_VAR), ('VERTEX_API_KEY', 'VERTEX_PROJECT'))
        self.assertEqual(providers.GEMINI_FROZEN['max_tokens'], 8000)  # frozen-5's cap is untouched

    def test_an_http_error_stops_the_call_once_and_never_shows_the_key(self):
        err = urllib.error.HTTPError('u', 429, 'quota', {}, io.BytesIO(json.dumps({'error': {'message': f'key {FAKE_KEY} is over quota'}}).encode()))
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', side_effect=err) as m:
            with self.assertRaises(SystemExit) as cm:
                providers.call_vertex('S', 'U')
        self.assertEqual(m.call_count, 1)  # a 429 is not retried
        self.assertIn('API error 429', str(cm.exception))
        self.assertNotIn(FAKE_KEY, str(cm.exception))


class SharedRequestHandling(unittest.TestCase):
    """_send serves both Gemini providers: a failure never shows the key and never leaves a half result."""

    def call(self, effect, which):
        fn = providers.call_vertex if which == 'vertex' else providers.call_gemini
        var = 'VERTEX_API_KEY' if which == 'vertex' else 'GEMINI_API_KEY'
        with mock.patch.dict(os.environ, {var: FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', side_effect=effect if isinstance(effect, BaseException) else None,
                                                                              return_value=None if isinstance(effect, BaseException) else effect):
            with self.assertRaises(SystemExit) as cm:
                fn('S', 'U')
        return str(cm.exception)

    def test_a_timeout_a_broken_connection_and_a_non_json_body_stop_the_call_without_the_key(self):
        import http.client
        for which in ('vertex', 'gemini'):
            for effect in (TimeoutError(f'timed out talking to {FAKE_KEY}'), ConnectionResetError(f'reset {FAKE_KEY}'), json.JSONDecodeError(f'bad {FAKE_KEY}', 'x', 0),
                           UnicodeDecodeError('utf-8', b'\xff', 0, 1, f'bad {FAKE_KEY}'), urllib.error.URLError(f'no route {FAKE_KEY}'),
                           http.client.IncompleteRead(b'abc', 985), http.client.RemoteDisconnected(f'closed {FAKE_KEY}')):
                msg = self.call(effect, which)
                self.assertTrue(msg.startswith('API error'), (which, effect, msg))
                self.assertNotIn(FAKE_KEY, msg)

    def test_a_value_error_shows_only_its_type_because_its_message_can_quote_the_header(self):
        # http.client's "Invalid header value b'<KEY>\r'" quotes the header with the control character escaped, so an exact replace of the key would not match it
        key = 'AQ.Ab8RN6exampleexampleexampleexampleexample'
        for bad_key in (key + '\r', key + '\n', key[:10] + '\r\n' + key[10:]):
            with self.assertRaises(SystemExit) as cm:
                providers._send('http://127.0.0.1:9/x', bad_key, {}, 1)  # refused by the HTTP library before any connection
            self.assertTrue(str(cm.exception).startswith('API error (no usable answer): ValueError'), str(cm.exception))
            self.assertNotIn('AQ.Ab8', str(cm.exception))
            self.assertNotIn(key[10:], str(cm.exception))

    def test_an_error_body_is_scrubbed_before_it_is_cut(self):
        key = 'AQ.Ab8RN6exampleexampleexampleexampleexample'
        body = ('x' * 480) + f' key was {key} end'
        err = urllib.error.HTTPError('u', 400, 'bad', {}, io.BytesIO(body.encode()))
        with mock.patch.object(providers, '_post_json', side_effect=err), self.assertRaises(SystemExit) as cm:
            providers._send('http://127.0.0.1:9/x', key, {}, 1)
        self.assertNotIn('AQ.', str(cm.exception))
        self.assertNotIn('Ab8RN6', str(cm.exception))  # the key straddles character 500: no prefix of it survives

    def test_an_error_body_that_cannot_be_read_still_stops_the_call(self):
        class Broken(io.BytesIO):
            def read(self, *a):
                raise OSError('the body broke')
        err = urllib.error.HTTPError('u', 502, 'bad gateway', {}, Broken(b'x'))
        with mock.patch.object(providers, '_post_json', side_effect=err), self.assertRaises(SystemExit) as cm:
            providers._send('http://127.0.0.1:9/x', 'k', {}, 1)
        self.assertEqual(str(cm.exception), 'API error 502: ')

    def test_a_body_that_is_not_a_json_object_stops_the_call(self):
        for which in ('vertex', 'gemini'):
            for body in ([1, 2], 'text', 7, None):
                self.assertIn('not a JSON object', self.call(body, which), (which, body))


class Key(unittest.TestCase):
    def load(self, text, env=None):
        d = tempfile.mkdtemp()
        if text is not None:
            with open(os.path.join(d, '.bashrc'), 'w') as f:
                f.write(text)
        with mock.patch.dict(os.environ, {'HOME': d, **(env or {})}):
            for var in ('VERTEX_API_KEY', 'GEMINI_API_KEY'):
                if var not in (env or {}):
                    os.environ.pop(var, None)
            return providers.load_key(providers.VERTEX_KEY_VAR)

    def test_the_environment_wins_then_the_last_export_line_as_text(self):
        self.assertEqual(self.load('export VERTEX_API_KEY=fromfile\n', {'VERTEX_API_KEY': 'fromenv'}), 'fromenv')
        self.assertEqual(self.load('export VERTEX_API_KEY=old\nexport VERTEX_API_KEY="new.key-1"\n'), 'new.key-1')
        self.assertEqual(self.load("  export VERTEX_API_KEY='single'  \n"), 'single')
        self.assertEqual(self.load('export VERTEX_API_KEY=plain # comment\n'), 'plain')

    def test_it_is_a_separate_variable_from_the_developer_api_key(self):
        self.assertEqual(self.load('export GEMINI_API_KEY=studio\nexport VERTEX_API_KEY=vertex\n'), 'vertex')
        for text, env in (('export GEMINI_API_KEY=studio\n', None), (None, {'GEMINI_API_KEY': 'studio'})):
            with self.assertRaises(SystemExit) as cm:
                self.load(text, env)
            self.assertIn('VERTEX_API_KEY', str(cm.exception))
            self.assertNotIn('studio', str(cm.exception))

    def test_a_line_is_never_executed_and_shell_syntax_is_refused_not_taken_for_the_key(self):
        marker = os.path.join(tempfile.mkdtemp(), 'executed')
        with self.assertRaises(SystemExit) as cm:
            self.load(f'export VERTEX_API_KEY=$(touch {marker})\n')
        self.assertFalse(os.path.exists(marker))  # not executed
        self.assertIn('VERTEX_API_KEY', str(cm.exception))
        self.assertIn('shell expression', str(cm.exception))  # and refused, so a charged call is not spent on the literal text '$(touch'
        for text in ('export VERTEX_API_KEY=$(cat ~/.vertex_key)', 'export VERTEX_API_KEY=${VERTEX_KEY_FILE}', 'export VERTEX_API_KEY=$OTHER', 'export VERTEX_API_KEY=`cat k`',
                     'export VERTEX_API_KEY=AQ.abc;', 'export VERTEX_API_KEY=AQ.abc\\', 'export VERTEX_API_KEY=~/key', 'export VERTEX_API_KEY="AQ.q\\"uote"'):
            with self.assertRaises(SystemExit, msg=text):
                self.load(text + '\n')

    def test_scrub_hides_a_service_account_bound_key_too_when_it_is_the_key_in_use_and_when_it_is_not(self):
        key = 'AQ.Ab8RN6exampleexampleexampleexampleexample'
        self.assertNotIn(key, providers.scrub(f'the key {key} is invalid', key))
        self.assertNotIn('Ab8RN6', providers.scrub(f'another key {key} appeared', None))
        self.assertNotIn('AIzaSy', providers.scrub('x AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAA y', None))
        # a key can no longer contain a quote or a backslash (load_key refuses them), so no JSON- or repr-escaped form of a key exists to slip past an exact replace
        for k in ('AQ.Ab8RN6exampleexampleexample', 'AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'plain-key_1.x'):
            self.assertEqual(json.dumps(k)[1:-1], k)
            self.assertEqual(repr(k)[1:-1], k)

    def test_a_trailing_cr_or_lf_is_stripped_and_a_key_that_is_not_printable_ascii_is_refused_without_showing_it(self):
        self.assertEqual(self.load(None, {'VERTEX_API_KEY': 'AQ.good-key_1\r\n'}), 'AQ.good-key_1')
        self.assertEqual(self.load('export VERTEX_API_KEY=AQ.fromfile\r\n'), 'AQ.fromfile')  # a CRLF-saved .bashrc
        for bad in ('AQ.in\rside', 'AQ.in\nside', 'AQ.with space', 'AQ.tab\there', 'AQ.curly”quote', 'AQ.zero​width', 'AQ.café'):
            with self.assertRaises(SystemExit) as cm:
                self.load(None, {'VERTEX_API_KEY': bad})
            self.assertIn('VERTEX_API_KEY', str(cm.exception))
            self.assertNotIn('AQ.', str(cm.exception))

    def test_an_empty_last_export_retires_an_earlier_key_and_a_blank_environment_falls_back_to_the_file(self):
        with self.assertRaises(SystemExit):
            self.load('export VERTEX_API_KEY=oldkey\nexport VERTEX_API_KEY=\n')
        with self.assertRaises(SystemExit):
            self.load('export VERTEX_API_KEY=oldkey\nexport VERTEX_API_KEY=""\n')
        self.assertEqual(self.load('export VERTEX_API_KEY=fromfile\n', {'VERTEX_API_KEY': '  \r\n'}), 'fromfile')


class JudgeRows(unittest.TestCase):
    def setUp(self):
        self.positions = judge.load_positions()
        self.rec = {PID: fake_rec()}

    def run_one(self, body=None, **kw):
        args = dict(provider='gemini-vertex', thinking_level=None, max_tokens=32768)
        args.update(kw)
        model = args.pop('model', 'gemini-4-argon')
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', return_value=body or generate_content()):
            return judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, model, **args)

    def test_a_frozen_row_records_its_settings_and_the_prompt_is_unchanged(self):
        self.assertEqual(judge.fingerprint(), FINGERPRINT)
        r, system, user = self.run_one()
        self.assertTrue(r['frozen'])
        self.assertEqual({k: r[k] for k in ('provider', 'model', 'location', 'max_tokens', 'temperature', 'thinking_level')}, judge.judge_settings('gemini-vertex'))
        self.assertEqual(r['vertex_project'], PROJECT)  # provenance: the project that answered (not a secret, not part of the freeze)
        self.assertNotIn('thinking_summaries', r)
        self.assertEqual((r['stop_reason'], r['finish_reason'], r['parse_error']), ('end_turn', 'STOP', None))
        self.assertIsNotNone(r['plan_number'])
        self.assertEqual(r['raw'], 'PLAN: 1\nREASON: x')
        self.assertNotIn('THOUGHT', json.dumps(r))
        self.assertNotIn(FAKE_KEY, json.dumps(r))
        with mock.patch.object(judge, 'call_claude', return_value=('PLAN: 1\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})):
            anthropic_row, asystem, auser = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, judge.MODEL)
        self.assertEqual((system, user, r['prompt_sha256']), (asystem, auser, anthropic_row['prompt_sha256']))  # byte-identical prompt

    def test_the_cost_is_priced_at_the_day_and_carries_the_vertex_note(self):
        r, _, _ = self.run_one()
        c = r['cost']
        self.assertEqual((c['input_tokens'], c['output_tokens'], c['thought_tokens'], c['answer_tokens']), (10000, 2000, 1700, 300))
        self.assertAlmostEqual(c['usd'], 10000 * c['price_per_mtok'][0] / 1e6 + 2000 * c['price_per_mtok'][1] / 1e6, places=5)
        self.assertIn('Vertex AI', c['price_note'])
        self.assertFalse(c['usd_is_worst_case'])

    def test_any_other_setting_makes_the_row_not_frozen(self):
        for kw in ({'thinking_level': 'LOW'}, {'thinking_level': 'high'}, {'model': 'gemini-4-other'}, {'max_tokens': 8000}, {'max_tokens': 65536}):
            r, _, _ = self.run_one(**kw)
            self.assertFalse(r['frozen'], kw)

    def test_a_reply_cut_at_the_cap_keeps_no_choice_even_with_a_plan_line(self):
        r, _, _ = self.run_one(generate_content(finish='MAX_TOKENS', text='PLAN: 2\nREASON: cut'))
        self.assertIsNone(r['plan_number'])
        self.assertIn('cut at max_tokens=32768', r['parse_error'])
        self.assertEqual((r['stop_reason'], r['finish_reason']), ('vertex:MAX_TOKENS', 'MAX_TOKENS'))
        self.assertGreater(r['cost']['usd'], 0)  # a cut call is billed

    def test_any_other_unfinished_reply_keeps_no_choice(self):
        for reason in ('SAFETY', 'CONTINUATION', 'OTHER'):
            r, _, _ = self.run_one(generate_content(finish=reason, text='PLAN: 2\nREASON: x'))
            self.assertIsNone(r['plan_number'], reason)
            self.assertIn(f'did not finish (vertex:{reason})', r['parse_error'])

    def test_a_blocked_prompt_keeps_no_choice(self):
        r, _, _ = self.run_one({'promptFeedback': {'blockReason': 'SAFETY'}, 'usageMetadata': {'promptTokenCount': 5000, 'totalTokenCount': 5000}})
        self.assertEqual((r['plan_number'], r['stop_reason'], r['block_reason']), (None, 'vertex:BLOCKED_SAFETY', 'SAFETY'))

    def test_the_same_parser_and_invalid_label_handling_apply(self):
        for text, ok in (('PLAN: 3\nREASON: fine', True), ('PLAN: 4 or 7\nREASON: x', False), ('PLAN: 99\nREASON: x', False), ('I choose plan 2', False), ('PLAN: 2', True), ('', False)):
            r, _, _ = self.run_one(generate_content(text=text))
            self.assertEqual(r['plan_number'] is not None, ok, text)
        r, _, _ = self.run_one(generate_content(text='PLAN: 2'))
        self.assertEqual(r['parse_warning'], 'no REASON line (choice kept)')

    def test_a_reply_without_usage_is_costed_at_its_worst_case(self):
        j = generate_content()
        del j['usageMetadata']
        r, _, _ = self.run_one(j)
        self.assertTrue(r['cost']['usd_is_worst_case'])
        self.assertTrue(r['usage_missing'])
        self.assertAlmostEqual(r['cost']['usd'], r['prompt_tokens_estimate'] * 4 / 1e6 + 32768 * 20 / 1e6, places=4)

    def test_a_dry_run_sends_nothing_and_names_the_provider(self):
        with mock.patch.object(providers, '_post_json') as m:
            r, _, _ = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], False, 'gemini-4-argon', provider='gemini-vertex', max_tokens=32768)
        m.assert_not_called()
        self.assertEqual((r['provider'], r['thinking_level'], r['dry_run'], r['frozen']), ('gemini-vertex', 'HIGH', True, True))

    def test_the_developer_api_provider_is_unchanged_by_the_vertex_one(self):
        with mock.patch.dict(os.environ, {'GEMINI_API_KEY': FAKE_KEY}), mock.patch.object(providers, '_post_json', return_value=interaction()):
            r, _, _ = judge.judge_one(PID, self.positions, self.rec, judge.FROZEN['order'], True, 'gemini-4-argon', provider='gemini')
        self.assertTrue(r['frozen'])
        self.assertEqual((r['provider'], r['max_tokens'], r['thinking_level'], r['thinking_summaries']), ('gemini', 8000, 'high', 'none'))


class CompareSeesVertexRows(unittest.TestCase):
    def check(self, row_extra, settings=None):
        rec = {'plans': [{'key': 'k1', 'labels': ['EndTurn'], 'end': 'end_turn'}]}
        row = {'position': 'P', 'bot': 'judge', 'plan_number': 1, 'shown_number': 1, 'plan_list_sha256': 'h', 'plan_key': 'k1', 'plan': ['EndTurn'], 'cut': 'end_turn',
               'prompt_sha256': 'ph', 'raw': 'PLAN: 1\nREASON: x', 'frozen': True, 'stop_reason': 'end_turn', **judge.judge_settings('gemini-vertex'), **row_extra}
        exp = lambda pid, r: {'prompt_sha256': 'ph', 'shown': {1: 1}, 'parse': lambda raw: 1, 'settings': settings or judge.judge_settings('gemini-vertex')}
        return [k for k, _ in formal.check_chosen_plan(row, 'judge', rec, 'h', exp, True)]

    def test_a_good_vertex_row_passes(self):
        self.assertEqual(self.check({}), [])

    def test_a_row_with_other_settings_is_not_frozen(self):
        for extra in ({'thinking_level': 'LOW'}, {'thinking_level': 'high'}, {'max_tokens': 8000}, {'model': 'gemini-4-other'}, {'provider': 'gemini'}, {'temperature': 0.7}, {'location': 'us'}):
            self.assertEqual(self.check(extra), ['not_frozen'], extra)

    def test_frozen_5_rows_of_the_developer_api_are_refused_under_the_vertex_freeze(self):
        old = {k: v for k, v in judge.judge_settings('gemini').items()}
        old['thinking_summaries'] = 'none'
        row_kinds = self.check(old)
        self.assertEqual(row_kinds, ['not_frozen'] * 3)  # provider, max_tokens, thinking_level

    def test_an_unfinished_vertex_reply_is_a_truncated_reply_if_a_choice_somehow_survived(self):
        for sr in ('vertex:MAX_TOKENS', 'vertex:SAFETY', 'vertex:CONTINUATION', 'vertex:NO_CANDIDATE'):
            self.assertEqual(self.check({'stop_reason': sr}), ['truncated_reply'], sr)


class CommandLine(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(judge, 'list_plans', return_value={PID: fake_rec()}), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = judge.main(argv)
        return code, out.getvalue(), err.getvalue()

    def row(self, argv):
        code, out, _ = self.run_main(argv)
        self.assertEqual(code, 0)
        return json.loads([l for l in out.splitlines() if l.startswith('{')][0])

    def test_a_vertex_dry_run_defaults_to_the_frozen_settings(self):
        with mock.patch.dict(os.environ, {}):
            os.environ.pop('VERTEX_PROJECT', None)
            r = self.row(['judge', '--ids', PID, '--provider', 'gemini-vertex'])
        self.assertEqual((r['provider'], r['model'], r['location'], r['max_tokens'], r['thinking_level'], r['temperature'], r['frozen']),
                         ('gemini-vertex', 'gemini-4-argon', 'global', 32768, 'HIGH', None, True))
        self.assertIsNone(r['vertex_project'])  # a dry run needs no project
        try:
            r = self.row(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--vertex-project', 'project-test-1234'])
            self.assertEqual(r['vertex_project'], 'project-test-1234')
        finally:
            providers.set_vertex_project(None)
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--vertex-project', 'project-test-1234'])  # a Vertex setting on another provider
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--vertex-project', 'bad/one'])

    def test_the_other_defaults_are_unchanged(self):
        self.assertEqual((lambda r: (r['model'], r['max_tokens'], 'provider' in r))(self.row(['judge', '--ids', PID])), (judge.MODEL, 8000, False))
        r = self.row(['judge', '--ids', PID, '--provider', 'gemini'])
        self.assertEqual((r['provider'], r['max_tokens'], r['thinking_level']), ('gemini', 8000, 'high'))

    def test_an_explicit_cap_or_level_makes_the_vertex_row_not_frozen(self):
        self.assertFalse(self.row(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--max-tokens', '8000'])['frozen'])
        r = self.row(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--thinking-level', 'low'])
        self.assertEqual((r['thinking_level'], r['frozen']), ('LOW', False))  # the level is written the way Vertex writes it

    def test_a_temperature_or_a_thinking_level_on_the_wrong_provider_exits(self):
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--temperature', '0.5'])
        with self.assertRaises(SystemExit):
            self.run_main(['judge', '--ids', PID, '--thinking-level', 'high'])

    def test_a_live_vertex_call_through_the_cli_uses_the_provider_and_its_price_note(self):
        reply = ('PLAN: 1\nREASON: x', {'input_tokens': 1000, 'output_tokens': 500, 'thought_tokens': 400, 'answer_tokens': 100, 'cached_tokens': 0}, 0.1, 'gemini-4-argon',
                 {'stop_reason': 'end_turn', 'content_types': ['text'], 'finish_reason': 'STOP', 'usage_missing': False, 'n_candidates': 1})
        with mock.patch.object(providers, 'call_vertex', return_value=reply) as m:
            code, out, err = self.run_main(['judge', '--ids', PID, '--provider', 'gemini-vertex', '--live', '--max-calls', '1'])
        self.assertEqual(code, 0)
        self.assertEqual(m.call_count, 1)
        self.assertEqual((m.call_args.args[2], m.call_args.kwargs['max_tokens'], m.call_args.kwargs['thinking']), ('gemini-4-argon', 32768, {'thinking_level': 'HIGH'}))
        self.assertIn('Vertex AI', err)


class Wire(unittest.TestCase):
    """The real _post_json against a server on 127.0.0.1 (nothing leaves the machine): every other test mocks it, so the method, the headers urllib really sends and the body encoding
    were untested."""

    def serve(self, status=200, payload=None, redirect_to=None, truncate=False):
        seen = {'methods': [], 'headers': []}

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get('content-length', 0))
                seen.update(path=self.path, body=self.rfile.read(n))
                seen['methods'].append('POST')
                seen['headers'].append({k.lower(): v for k, v in self.headers.items()})
                if redirect_to:
                    self.send_response(302)
                    self.send_header('location', redirect_to)
                    self.send_header('content-length', '0')
                    self.end_headers()
                    return
                data = json.dumps(payload if payload is not None else generate_content()).encode()
                self.send_response(status)
                self.send_header('content-type', 'application/json')
                self.send_header('content-length', str(len(data) + (500 if truncate else 0)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                seen['methods'].append(self.command)
                seen['headers'].append({k.lower(): v for k, v in self.headers.items()})
                self.send_response(405)
                self.send_header('content-length', '0')
                self.end_headers()
            do_PUT = do_GET

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(('127.0.0.1', 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return srv, seen

    def env(self, srv):
        url = f'http://127.0.0.1:{srv.server_port}/v1/projects/{{project}}/locations/{{location}}/publishers/google/models/{{model}}:generateContent'
        return mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT, 'no_proxy': '127.0.0.1', 'NO_PROXY': '127.0.0.1'}), mock.patch.object(providers, 'VERTEX_URL', url)

    def test_the_real_request_is_a_json_post_with_the_key_in_the_header_and_the_given_settings(self):
        srv, seen = self.serve()
        e1, e2 = self.env(srv)
        with e1, e2:
            text, usage, secs, model, extra = providers.call_vertex('SYS é中', 'USER', max_tokens=8000, thinking={'thinking_level': 'LOW'})
        self.assertEqual(seen['methods'], ['POST'])
        self.assertEqual(seen['path'], f'/v1/projects/{PROJECT}/locations/global/publishers/google/models/gemini-4-argon:generateContent')
        h = seen['headers'][0]
        self.assertEqual(h['x-goog-api-key'], FAKE_KEY)
        self.assertEqual(h['content-type'], 'application/json')  # urllib's default for a POST body is x-www-form-urlencoded
        self.assertNotIn('authorization', h)
        self.assertNotIn(FAKE_KEY.encode(), seen['body'])
        self.assertEqual(json.loads(seen['body'].decode('utf-8')), providers.build_vertex_request('SYS é中', 'USER', 8000, 'LOW'))  # the settings given are the settings sent
        self.assertEqual((text, extra['stop_reason'], usage['output_tokens']), ('PLAN: 1\nREASON: x', 'end_turn', 2000))

    def test_the_real_request_at_the_frozen_defaults(self):
        srv, seen = self.serve()
        e1, e2 = self.env(srv)
        with e1, e2:
            providers.call_vertex('S', 'U')
        self.assertEqual(json.loads(seen['body'])['generationConfig'], {'maxOutputTokens': 32768, 'thinkingConfig': {'thinkingLevel': 'HIGH'}})

    def test_an_http_error_on_the_wire_stops_the_call_and_does_not_show_the_key(self):
        srv, seen = self.serve(status=429, payload={'error': {'message': f'quota for key {FAKE_KEY}'}})
        e1, e2 = self.env(srv)
        with e1, e2, self.assertRaises(SystemExit) as cm:
            providers.call_vertex('S', 'U')
        self.assertIn('API error 429', str(cm.exception))
        self.assertNotIn(FAKE_KEY, str(cm.exception))
        self.assertEqual(seen['methods'], ['POST'])  # one request: no retry

    def test_a_redirect_is_an_error_and_the_key_is_not_sent_on(self):
        second, seen2 = self.serve()
        first, seen1 = self.serve(redirect_to=f'http://127.0.0.1:{second.server_port}/elsewhere')
        e1, e2 = self.env(first)
        with e1, e2, self.assertRaises(SystemExit) as cm:
            providers.call_vertex('S', 'U')
        self.assertIn('API error 302', str(cm.exception))
        self.assertEqual(seen1['methods'], ['POST'])
        self.assertEqual(seen2['methods'], [])  # urllib's default opener would have re-sent the x-goog-api-key header to this host
        self.assertNotIn(FAKE_KEY, str(cm.exception))

    def test_a_body_that_ends_early_stops_the_call_cleanly(self):
        srv, seen = self.serve(truncate=True)
        e1, e2 = self.env(srv)
        with e1, e2, self.assertRaises(SystemExit) as cm:
            providers.call_vertex('S', 'U')
        self.assertTrue(str(cm.exception).startswith('API error (no usable answer)'), str(cm.exception))
        self.assertNotIn(FAKE_KEY, str(cm.exception))


class SettingsGivenAreSettingsSent(unittest.TestCase):
    """call_vertex(max_tokens=, thinking=) must send what judge_one recorded (a non-frozen experiment would otherwise record one setting and send another)."""

    def test_a_non_frozen_cap_and_level_reach_the_body(self):
        seen = {}

        def post(url, headers, body, timeout):
            seen['body'] = body
            return generate_content()
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', side_effect=post):
            r, _, _ = judge.judge_one(PID, judge.load_positions(), {PID: fake_rec()}, judge.FROZEN['order'], True, 'gemini-4-argon', provider='gemini-vertex', max_tokens=8000, thinking_level='LOW')
        self.assertFalse(r['frozen'])
        self.assertEqual((r['max_tokens'], r['thinking_level']), (8000, 'LOW'))
        self.assertEqual(seen['body']['generationConfig'], {'maxOutputTokens': 8000, 'thinkingConfig': {'thinkingLevel': 'LOW'}})


class RowFlags(unittest.TestCase):
    def setUp(self):
        self.positions = judge.load_positions()

    def test_a_temperature_makes_a_dry_run_row_not_frozen_for_both_gemini_providers(self):
        for provider in ('gemini-vertex', 'gemini'):
            r, _, _ = judge.judge_one(PID, self.positions, {PID: fake_rec()}, judge.FROZEN['order'], False, 'gemini-4-argon', temperature=0.5, provider=provider,
                                      max_tokens=judge.judge_settings(provider)['max_tokens'])
            self.assertEqual((r['temperature'], r['frozen']), (0.5, False), provider)

    def test_a_reply_with_an_input_count_but_no_output_count_is_a_worst_case_row(self):
        j = generate_content()
        j['usageMetadata'] = {'promptTokenCount': 5000}
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', return_value=j):
            r, _, _ = judge.judge_one(PID, self.positions, {PID: fake_rec()}, judge.FROZEN['order'], True, 'gemini-4-argon', provider='gemini-vertex', max_tokens=32768)
        self.assertTrue(r['usage_missing'])
        self.assertTrue(r['cost']['usd_is_worst_case'])
        self.assertAlmostEqual(r['cost']['usd'], r['prompt_tokens_estimate'] * 4 / 1e6 + 32768 * 20 / 1e6, places=4)

    def test_a_gemini_row_records_the_model_the_service_says_answered(self):
        j = generate_content()
        j['modelVersion'] = 'gemini-4-argon-20261013'
        with mock.patch.dict(os.environ, {'VERTEX_API_KEY': FAKE_KEY, 'VERTEX_PROJECT': PROJECT}), mock.patch.object(providers, '_post_json', return_value=j):
            r, _, _ = judge.judge_one(PID, self.positions, {PID: fake_rec()}, judge.FROZEN['order'], True, 'gemini-4-argon', provider='gemini-vertex', max_tokens=32768)
        self.assertEqual((r['model'], r['model_returned']), ('gemini-4-argon', 'gemini-4-argon-20261013'))
        self.assertTrue(r['frozen'])  # the freeze names the alias; the version is the evidence, not part of the comparison
        with mock.patch.object(judge, 'call_claude', return_value=('PLAN: 1\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})):
            a, _, _ = judge.judge_one(PID, self.positions, {PID: fake_rec()}, judge.FROZEN['order'], True, judge.MODEL)
        self.assertNotIn('model_returned', a)  # the Anthropic row keeps the frozen-4 shape


class PartialUsage(unittest.TestCase):
    def usage(self, **drop):
        j = generate_content()
        for k in drop:
            j['usageMetadata'].pop(k)
        return providers.parse_generate_content(j, 'm')

    def test_one_missing_output_part_is_not_a_missing_usage_block(self):
        # proto3 JSON leaves out a zero: a reply with no thinking has no thoughtsTokenCount, a reply cut while thinking has no candidatesTokenCount
        _, usage, _, extra = self.usage(thoughtsTokenCount=1, totalTokenCount=1)
        self.assertFalse(extra['usage_missing'])
        self.assertEqual((usage['input_tokens'], usage['output_tokens'], usage['answer_tokens'], usage['thought_tokens']), (10000, 300, 300, 0))
        _, usage, _, extra = self.usage(candidatesTokenCount=1, totalTokenCount=1)
        self.assertFalse(extra['usage_missing'])
        self.assertEqual((usage['output_tokens'], usage['answer_tokens'], usage['thought_tokens']), (1700, 0, 1700))

    def test_such_a_reply_is_settled_at_its_real_cost_not_its_worst_case(self):
        import budget_judge as bj
        _, usage, secs, extra = self.usage(thoughtsTokenCount=1)
        out = ('PLAN: 1', usage, 0.0, 'm', extra)
        with mock.patch.object(providers, 'gemini_price', return_value=(2.0, 10.0)):
            self.assertAlmostEqual(bj.actual_usd('gemini-vertex', out, 0.7), 10000 * 2 / 1e6 + 2000 * 10 / 1e6)


class UnfinishedPrefixes(unittest.TestCase):
    def test_every_unfinished_stop_reason_the_parsers_make_starts_with_a_prefix_formal_flags(self):
        for status in ('incomplete', 'failed', 'cancelled', None):
            sr = providers.parse_interaction(interaction(status=status), 'm')[3]['stop_reason']
            self.assertTrue(sr.startswith(formal.UNFINISHED_PREFIXES), sr)
        for finish in ('MAX_TOKENS', 'SAFETY', 'CONTINUATION', None):
            sr = providers.parse_generate_content(generate_content(finish=finish), 'm')[3]['stop_reason']
            self.assertTrue(sr.startswith(formal.UNFINISHED_PREFIXES), sr)
        self.assertEqual(providers.parse_generate_content({}, 'm')[3]['stop_reason'].split(':')[0] + ':', 'vertex:')

    def test_formal_flags_every_listed_prefix(self):
        rec = {'plans': [{'key': 'k1', 'labels': ['EndTurn'], 'end': 'end_turn'}]}
        for prefix in formal.UNFINISHED_PREFIXES:
            row = {'position': 'P', 'bot': 'judge', 'plan_number': 1, 'shown_number': 1, 'plan_list_sha256': 'h', 'plan_key': 'k1', 'plan': ['EndTurn'], 'cut': 'end_turn',
                   'prompt_sha256': 'ph', 'raw': 'PLAN: 1', 'frozen': True, 'stop_reason': prefix + 'X'}
            exp = lambda pid, r: {'prompt_sha256': 'ph', 'shown': {1: 1}, 'parse': lambda raw: 1, 'settings': {}}
            self.assertIn('truncated_reply', [k for k, _ in formal.check_chosen_plan(row, 'judge', rec, 'h', exp, True)], prefix)


class MockRowsAreNeverResults(unittest.TestCase):
    def test_a_row_from_a_mock_run_is_a_problem_for_the_formal_path(self):
        rec = {'id': 'P', 'capped': False, 'start': {'position': 'P'}, 'plans': [{'n': 1, 'key': 'k1', 'labels': ['EndTurn'], 'end': 'end_turn'}]}
        row = {'position': 'P', 'bot': 'judge', 'seed': None, 'repeat': 0, 'plan_number': 1, 'shown_number': 1, 'plan_list_sha256': formal.plan_list_sha256(rec), 'plan_key': 'k1',
               'plan': ['EndTurn'], 'cut': 'end_turn', 'prompt_sha256': 'ph', 'raw': 'PLAN: 1\nREASON: MOCK reply', 'frozen': True, 'dry_run': False, 'capped': False,
               'stop_reason': 'end_turn', **judge.judge_settings('gemini-vertex')}
        exp = lambda pid, r: {'prompt_sha256': 'ph', 'shown': {1: 1}, 'parse': lambda raw: 1, 'settings': judge.judge_settings('gemini-vertex')}
        _, problems = formal.check_rows([dict(row)], [('P', 'judge', 0)], {'P': rec}, True, None, exp)
        self.assertEqual([p['kind'] for p in problems], [])
        _, problems = formal.check_rows([{**row, 'mock': True}], [('P', 'judge', 0)], {'P': rec}, True, None, exp)
        self.assertEqual([p['kind'] for p in problems], ['mock_row'])


class Identity(unittest.TestCase):
    def test_the_freeze_judge_is_vertex_and_the_block_says_everything(self):
        self.assertEqual(judge.FREEZE_JUDGE_PROVIDER, 'gemini-vertex')
        b = judge.frozen_judge_block()
        self.assertEqual(b, judge.frozen_judge_block('gemini-vertex'))
        self.assertEqual((b['provider'], b['settings']), ('gemini-vertex', {'provider': 'gemini-vertex', 'model': 'gemini-4-argon', 'location': 'global', 'max_tokens': 32768, 'temperature': None,
                                                                          'thinking_level': 'HIGH'}))
        self.assertEqual((b['key_variable'], b['project_variable']), ('VERTEX_API_KEY', 'VERTEX_PROJECT'))
        self.assertEqual(b['endpoint'], 'https://aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent')  # the project value is NOT in the freeze
        self.assertEqual(b['failed_judge_rows'], formal.FAILED_JUDGE_ROWS_DOC)
        self.assertEqual((b['failed_judge_rows']['default'], b['failed_judge_rows']['preregistered_for_run_2'], b['failed_judge_rows']['values']), ('abort', 'miss', ['abort', 'miss']))
        self.assertEqual(b['price_per_mtok'], {'through_2026-11-30': [2.0, 10.0], 'from_2026-12-01': [4.0, 20.0], 'reservation': [4.0, 20.0]})
        self.assertTrue(all(u.startswith(('https://docs.cloud.google.com/', 'https://cloud.google.com/', 'https://ai.google.dev/')) for u in b['sources']))
        for k in ('prompt', 'output cap', 'reasoning', 'thought text', 'temperature', 'retries', 'serving', 'location', 'project', 'price', 'finish', 'usage', 'key'):
            self.assertIn(k, b['mapping'])
        self.assertIn('CANNOT MATCH', b['mapping']['output cap'])
        self.assertIn('32,768', b['mapping']['output cap'])
        json.dumps(b)  # it goes in FROZEN.json

    def test_the_frozen_5_block_is_still_producible_and_an_unknown_provider_is_refused(self):
        self.assertEqual(judge.frozen_judge_block('gemini')['settings'], judge.judge_settings('gemini'))
        with self.assertRaises(ValueError):
            judge.frozen_judge_block('openai')

    def test_the_prompt_the_lister_and_the_anthropic_settings_are_untouched(self):
        self.assertEqual(judge.fingerprint(), FINGERPRINT)
        self.assertEqual((judge.FROZEN['model'], judge.FROZEN['max_tokens'], judge.FROZEN['temperature']), ('claude-sonnet-5-5', 8000, None))


if __name__ == '__main__':
    unittest.main()
