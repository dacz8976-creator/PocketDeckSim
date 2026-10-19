#!/usr/bin/env python3
"""The formal paired comparison path (formal.py and `judge.py compare`): nothing unresolved is ever left out of a comparison, no plan number is believed
without being checked against the current plan list, and the references are FILTERED to the explicit selection.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests

The pure-Python classes need nothing built. The classes that run the CLI on the fixtures need the judge_plans binary (skipped without it).
Everything here uses synthetic rows and the small fixtures in tests/fixtures: no exam data, no API, no bot binaries.
"""
import contextlib, io, json, os, re, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import analysis  # noqa: E402
import formal  # noqa: E402
import judge  # noqa: E402

POS = os.path.join(HERE, 'fixtures', 'mini_positions.json')
DECKS = os.path.join(HERE, 'fixtures', 'decks')
HAVE_BIN = os.path.exists(judge.PLANS_BIN)


# ---------------------------------------------------------------------------------------------------------------------------------- pure logic
def mk_rec(pid, n=2):
    return {'id': pid, 'capped': False, 'start': {'position': pid}, 'plans': [{'n': i, 'key': f'{pid}-key{i}', 'labels': [f'{pid}-move{i}'], 'end': 'end_turn'} for i in range(1, n + 1)]}


# P1, P2 are primary (P1 also full-scope), P3 is in the batch but outside the selection (a diagnostic point), P4 is only in the references file
RECS = {'P1': mk_rec('P1'), 'P2': mk_rec('P2'), 'P3': mk_rec('P3')}
ELIG = {'primary_ids': ['P1', 'P2'], 'full_scope_ids': ['P1'], 'games': {'P1': 'g1', 'P2': 'g2', 'P3': 'g3'}, 'excluded_reasons': {'P3': 'synthetic exposure'}}
REFS = {'P1': [{'id': 'recorded', 'labels': ['P1-full-1']}, {'id': 'alt', 'labels': ['P1-move1']}], 'P2': [{'id': 'recorded', 'labels': ['n']}],
        'P3': [{'id': 'recorded', 'labels': ['q']}], 'P4': 'junk that no comparison may ever read'}
ANSWERS = {('P1', 'recorded'): (1, None), ('P1', 'alt'): (1, None), ('P2', 'recorded'): (2, None), ('P3', 'recorded'): (1, None)}
SETTINGS = {'model': 'm', 'max_tokens': 8000, 'temperature': None}


def valid(n, recs, pid):
    return isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= len(recs[pid]['plans'])


def step_row(pid, bot, seed, n, recs=RECS, **kw):
    r = {'position': pid, 'bot': bot, 'seed': seed, 'plan': ['x'], 'plan_full': [f'{pid}-full-{seed}'], 'plan_number': n, 'match_error': None, 'dry_run': False,
         'pg_pos_cut': 'end of turn', 'plan_key': recs[pid]['plans'][n - 1]['key'] if valid(n, recs, pid) else None, 'plan_list_sha256': formal.plan_list_sha256(recs[pid])}
    r.update(kw)
    return r


def judge_row(pid, repeat, n, recs=RECS, **kw):
    r = {'position': pid, 'bot': 'judge', 'seed': None, 'repeat': repeat, 'plan': recs[pid]['plans'][n - 1]['labels'] if valid(n, recs, pid) else ['x'],
         'cut': recs[pid]['plans'][n - 1]['end'] if valid(n, recs, pid) else 'end_turn', 'stop_reason': 'end_turn',
         'plan_number': n, 'shown_number': n, 'raw': f'PLAN: {n}\nREASON: x', 'frozen': True, 'dry_run': False, 'capped': False, 'parse_error': None, 'prompt_sha256': f'prompt-{pid}',
         'model': 'm', 'max_tokens': 8000, 'temperature': None,
         'plan_key': recs[pid]['plans'][n - 1]['key'] if valid(n, recs, pid) else None, 'plan_list_sha256': formal.plan_list_sha256(recs[pid])}
    r.update(kw)
    return r


def expect_identity(pid, row):
    """What the prompt re-rendered now would give: its hash, the plan behind every number printed in it (here the identity order), how a stored reply parses, the
    frozen settings."""
    def parse(raw):
        m = re.search(r'PLAN: (\d+)', raw)
        return int(m.group(1)) if m else None
    return {'prompt_sha256': f'prompt-{pid}', 'shown': {1: 1, 2: 2}, 'parse': parse, 'settings': SETTINGS}


def full_match(row_labels, ref_labels):
    return [str(l) for l in row_labels] == [str(l) for l in ref_labels]


class Matcher:
    """A stand-in for judge.match_plans that records every item it is asked about. Two-part tags (position|reference) are answered from `answers`; three-part tags
    (position|bot|run: a row's recorded full move list) replay to what the row claims unless `replays` says otherwise."""
    def __init__(self, answers=ANSWERS, replays=None, claims=None):
        self.answers, self.replays, self.claims, self.asked = answers, replays or {}, claims or {}, []

    def __call__(self, items, recs):
        out = {}
        for pid, tag, labels in items:
            self.asked.append((pid, tag))
            parts = tag.split('|')
            out[tag] = self.answers[tuple(parts)] if len(parts) == 2 else self.replays.get(tag, (self.claims.get(tag), None))
        return out


def complete_rows(with_p3=False):
    rows = [step_row('P1', 'km3', 1, 1), step_row('P1', 'km3', 2, 2), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2), judge_row('P1', 0, 1), judge_row('P2', 0, 1)]
    if with_p3:
        rows += [step_row('P3', 'km3', 1, 1), step_row('P3', 'km3', 2, 1), judge_row('P3', 0, 1)]
    return rows


def run(rows, refs=REFS, answers=ANSWERS, replays=None, on_problem='fail', recs=RECS, require_frozen=True, elig=ELIG, expect_judge=expect_identity, min_games=2,
        ids=('P1', 'P2'), bots=('km3', 'judge'), seeds=(1, 2), judge_repeats=1, baseline_sha256=None, contrasts=None, resamples=200, matcher=None, fmatch=full_match,
        position_games=None):
    claims = {f"{r.get('position')}|{r.get('bot')}|{r.get('seed')}": r.get('plan_number') for r in rows if isinstance(r, dict) and r.get('bot') != 'judge'}
    m = matcher or Matcher(answers, replays, claims)
    return formal.compare(rows, list(ids), list(bots), list(seeds), judge_repeats, refs, recs, m, elig, on_problem, require_frozen, baseline_sha256, expect_judge, contrasts,
                          min_games, resamples, fmatch, None, (), (), position_games)


def kinds(rep_or_exc):
    return sorted(p['kind'] for p in (rep_or_exc['problems'] if isinstance(rep_or_exc, dict) else rep_or_exc.problems))


class FormalPath(unittest.TestCase):
    def failed(self, rows, **kw):
        """Runs the formal path in the default 'fail' mode: it must raise BatchFailed(2) with a report that carries no numbers; returns the exception."""
        with self.assertRaises(formal.BatchFailed) as cm:
            run(rows, **kw)
        self.assertEqual(cm.exception.code, 2)
        rep = cm.exception.report
        self.assertEqual(rep['status'], 'failed')
        self.assertIsNone(rep['analysis'])  # no numbers at all
        self.assertTrue(all(r['agrees'] is None and r['accepted'] == [] and r['full_agrees'] is None for r in rep['rows']))
        return cm.exception

    def test_a_clean_batch_is_complete_and_counts_every_row(self):
        rep = run(complete_rows())
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual((rep['n_expected_rows'], rep['n_present_rows'], rep['n_resolved_rows']), (6, 6, 6))
        self.assertEqual(formal.exit_code(rep), 0)
        self.assertEqual({r['game'] for r in rep['rows']}, {'g1', 'g2'})  # the game is kept for clustered uncertainty
        self.assertEqual(rep['analysis']['prefix']['population']['n_games'], 2)
        # the row account is a count of rows, not an agreement figure; there is no pooled `agreement` block
        self.assertNotIn('agreement', rep)
        self.assertEqual(rep['row_account']['per_bot_state_counts'], {'km3': {'ok': 4}, 'judge': {'ok': 2}})
        # prefix agreement per decision: km3 averages its seeds (P1: 1 and 0 -> 0.5, P2: 1 and 1 -> 1), the judge's one call is P1 yes, P2 no
        self.assertAlmostEqual(rep['analysis']['prefix']['rates']['km3']['estimate'], 0.75, places=5)
        self.assertAlmostEqual(rep['analysis']['prefix']['rates']['judge']['estimate'], 0.5, places=5)

    def test_a_missing_reason_line_is_a_warning_not_an_error(self):
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, parse_warning='no REASON line (choice kept)'), judge_row('P2', 0, 1)]
        self.assertEqual(run(rows)['status'], 'complete')

    # --- unresolved rows
    def test_an_ambiguous_row_fails_the_batch_instead_of_dropping_out_of_a_denominator(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, None, match_error='ambiguous: the move list fits 2 different listed plans [1, 2]: name the target')
        self.assertEqual([p['kind'] for p in self.failed(rows).problems], ['ambiguous'])

    def test_inconclusive_mode_accounts_for_every_expected_row_and_reports_no_numbers(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, None, match_error='ambiguous: two targets')
        del rows[3]  # a missing row as well
        rep = run(rows, on_problem='inconclusive')
        self.assertEqual(rep['status'], 'inconclusive')
        self.assertEqual(len(rep['rows']), rep['n_expected_rows'])  # nothing left out of the account
        self.assertEqual((rep['n_expected_rows'], rep['n_present_rows'], rep['n_resolved_rows']), (6, 5, 4))
        states = {}
        for r in rep['rows']:
            states[r['state']] = states.get(r['state'], 0) + 1
        self.assertEqual(states, {'ok': 4, 'unresolved': 1, 'missing': 1})
        self.assertIsNone(rep['analysis'])
        self.assertTrue(all(r['agrees'] is None for r in rep['rows']))
        self.assertEqual(formal.exit_code(rep), 3)
        self.assertEqual(kinds(rep), ['ambiguous', 'missing'])

    def test_a_problem_that_belongs_to_a_whole_position_takes_every_row_numbers_away(self):
        # P1's only unusable reference: the report may not show 'ok' rows with an agreement verdict at P1 (nor anywhere: with any problem there are no numbers)
        answers = {**ANSWERS, ('P1', 'recorded'): (None, 'no legal action labelled "x"'), ('P1', 'alt'): (None, 'no legal action labelled "y"')}
        rep = run(complete_rows(), answers=answers, on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['reference_unresolved', 'reference_unresolved'])
        p1 = [r for r in rep['rows'] if r['position'] == 'P1']
        self.assertTrue(all(r['state'] == 'unresolved' and r['agrees'] is None and r['accepted'] == [] for r in p1))
        self.assertTrue(all(r['agrees'] is None for r in rep['rows']))
        self.assertEqual(rep['n_resolved_rows'], 3)  # only P2's three rows: nothing is wrong at their position

    def test_missing_duplicate_and_unexpected_rows_are_problems_and_a_duplicate_says_so(self):
        rows = complete_rows()
        rows.append(step_row('P1', 'km3', 1, 1))  # the same key twice
        rows.append(step_row('P1', 'km3', 9, 1))  # a seed nobody asked for
        del rows[1]
        rep = run(rows, on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['duplicate', 'missing', 'unexpected'])
        self.assertEqual(rep['n_resolved_rows'], rep['n_expected_rows'] - 2)
        self.assertEqual({r['state'] for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'km3' and r['run'] == 1}, {'duplicate'})

    # --- the plan-number hole: a number is checked against the CURRENT plan list
    def test_a_plan_number_outside_the_plan_list_is_refused_not_scored(self):
        for bad in (999, 3, 0, -1):
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', 1, bad)
            exc = self.failed(rows)
            self.assertEqual([p['kind'] for p in exc.problems], ['bad_number'], bad)
            self.assertIn('from 1 to 2', exc.problems[0]['detail'])  # the size of the current two-plan list is named
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 999), judge_row('P2', 0, 1)]  # the judge's row too
        self.assertIn('bad_number', kinds(self.failed(rows)))

    def test_a_number_that_is_not_a_whole_number_is_refused(self):
        # Python would happily compare True == 1 and 1.0 == 1: a row with such a number must never be scored as agreeing with plan 1
        for bad in (True, 1.0, '1', [1], {'n': 1}):
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', 1, bad, plan_key=RECS['P1']['plans'][0]['key'])
            self.assertIn('bad_number', kinds(self.failed(rows)), repr(bad))

    def test_a_row_with_a_plan_number_and_an_error_contradicts_itself(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, match_error='ambiguous: the move list fits 2 different listed plans [1, 2]')
        self.assertEqual(kinds(self.failed(rows)), ['contradictory'])
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, parse_error='several different PLAN lines [1, 2]'), judge_row('P2', 0, 1)]
        self.assertEqual(kinds(self.failed(rows)), ['contradictory'])
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, match_error='no legal action labelled "x"')
        self.assertEqual(kinds(self.failed(rows)), ['contradictory'])

    def test_a_row_from_another_plan_list_is_refused(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, plan_list_sha256='0' * 64)
        self.assertEqual(kinds(self.failed(rows)), ['list_mismatch'])
        # a row made from a list that had a different plan 1 (same number, different plan): the identity hash differs
        other = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], key='another-key')] + RECS['P1']['plans'][1:]}}
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, recs=other)
        self.assertEqual(kinds(self.failed(rows)), ['key_mismatch', 'list_mismatch'])

    def test_what_the_identity_hash_covers(self):
        base = formal.plan_list_sha256(RECS['P1'])
        changed = [{**RECS['P1'], 'start': {'position': 'P1', 'extra': 1}}, {**RECS['P1'], 'world_seed': 2}, {**RECS['P1'], 'limits': {'max_plans': 5}},
                   {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], labels=['z'])] + RECS['P1']['plans'][1:]}, {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], end='attack')] + RECS['P1']['plans'][1:]},
                   {**RECS['P1'], 'plans': RECS['P1']['plans'][:1]}]
        for c in changed:
            self.assertNotEqual(formal.plan_list_sha256(c), base)
        # and a row made from a list with another start state / world seed / limit is refused by the formal path
        for c in changed[:3]:
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', 1, 1, plan_list_sha256=formal.plan_list_sha256(c))
            self.assertEqual(kinds(self.failed(rows)), ['list_mismatch'])

    def test_a_row_without_any_identity_says_it_predates_the_fields_once(self):
        rows = complete_rows()
        for k in ('plan_list_sha256', 'plan_key'):
            del rows[0][k]
        exc = self.failed(rows)
        self.assertEqual(kinds(exc), ['predates_identity'])
        self.assertIn('regenerate', exc.problems[0]['detail'])

    def test_a_row_whose_plan_key_is_not_the_keyed_plan_is_refused(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 2, plan_key=RECS['P1']['plans'][0]['key'])  # claims plan 2 but carries plan 1's key
        self.assertIn('key_mismatch', kinds(self.failed(rows)))

    def test_a_step_bot_row_must_replay_to_its_numbered_plan(self):
        exc = self.failed(complete_rows(), replays={'P1|km3|1': (2, None)})  # the recorded moves reach plan 2 but the row says plan 1
        self.assertEqual(kinds(exc), ['replay_mismatch'])
        self.assertIn('plan 2', exc.problems[0]['detail'])
        self.assertEqual(kinds(self.failed(complete_rows(), replays={'P1|km3|1': (None, 'no legal action labelled "x" at step 2')})), ['replay_mismatch'])
        self.assertEqual(kinds(self.failed(complete_rows(), replays={'P2|km3|2': (None, 'ambiguous: the move list fits 2 different listed plans [1, 2]')})), ['replay_mismatch'])
        rows = complete_rows()
        del rows[0]['plan_full']  # no recorded move list: it cannot be replayed
        self.assertEqual(kinds(self.failed(rows)), ['no_move_list'])
        for bad in ([1, 2], [None], 'P1-full-1', []):
            rows = complete_rows()
            rows[0]['plan_full'] = bad  # a move list that is not a list of text labels
            self.assertEqual(kinds(self.failed(rows)), ['no_move_list'], bad)

    def test_a_judge_row_must_match_the_prompt_and_reply_it_was_answered_from(self):
        def with_judge(**kw):
            return complete_rows()[:-2] + [judge_row('P1', 0, 1, **kw), judge_row('P2', 0, 1)]
        swapped = lambda pid, row: {**expect_identity(pid, row), 'shown': {1: 2, 2: 1}}  # the answer's number maps to another plan in the prompt as re-rendered
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(), expect_judge=swapped)))
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(shown_number=7))))
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(shown_number=None))))
        self.assertEqual(kinds(self.failed(with_judge(prompt_sha256='other'))), ['prompt_mismatch'])  # not the hash of the prompt rendered now
        self.assertEqual(kinds(self.failed(with_judge(plan=['something else']))), ['labels_mismatch'])  # not the labels of that plan
        broken = lambda pid, row: {'error': 'unknown order'}  # the prompt cannot be re-rendered at all
        self.assertIn('prompt_mismatch', kinds(self.failed(with_judge(), expect_judge=broken)))
        with self.assertRaises(ValueError):  # the judge can only be compared with an expectation of its prompt
            formal.compare(complete_rows(), ['P1', 'P2'], ['km3', 'judge'], [1, 2], 1, REFS, RECS, Matcher(), ELIG, 'fail', True, None, None, None, 2, 50, full_match)

    def test_a_judge_choice_is_re_derived_from_its_stored_reply(self):
        def with_judge(**kw):
            return complete_rows()[:-2] + [judge_row('P1', 0, 1, **kw), judge_row('P2', 0, 1)]
        # every field the checker compares agrees with every other (an edited row), but the stored reply says something else
        self.assertEqual(kinds(self.failed(with_judge(raw='PLAN: 2\nREASON: x'))), ['reply_mismatch'])
        self.assertEqual(kinds(self.failed(with_judge(raw='I cannot decide.'))), ['reply_mismatch'])
        self.assertEqual(kinds(self.failed(with_judge(raw=None))), ['reply_mismatch'])
        rows = with_judge()
        del rows[-2]['raw']
        self.assertEqual(kinds(self.failed(rows)), ['reply_mismatch'])
        self.assertEqual(run(with_judge(raw='PLAN: 1'))['status'], 'complete')  # a reply without a REASON line still says plan 1

    def test_the_run_of_a_row_is_its_whole_number_seed_or_repeat_never_a_mixture(self):
        # the run decides which call is the PRIMARY one: bool / float / text / both fields are refused (a True or 1.0 would otherwise hash like 1)
        for seed in (True, 1.0, '1', [1]):
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', seed, 1)
            self.assertIn('bad_run_id', kinds(self.failed(rows)), repr(seed))
        rows = complete_rows()
        rows[0]['repeat'] = 3  # a step-bot row with a repeat
        self.assertIn('bad_run_id', kinds(self.failed(rows)))
        for repeat in (True, 0.0, None, '0'):
            rows = complete_rows()[:-2] + [judge_row('P1', repeat, 1), judge_row('P2', 0, 1)]
            self.assertIn('bad_run_id', kinds(self.failed(rows)), repr(repeat))
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, seed=0), judge_row('P2', 0, 1)]  # a judge row that also carries a seed
        self.assertIn('bad_run_id', kinds(self.failed(rows)))

    def test_rows_that_are_not_objects_are_a_problem_not_a_crash(self):
        for junk in ([], 5, None, {}, {'position': 'P1'}, {'bot': 'km3'}, {'position': ['P1'], 'bot': 'km3'}, {'position': 'P1', 'bot': ['km3']}):
            rep = run(complete_rows() + [junk], on_problem='inconclusive')
            self.assertIn('bad_row', kinds(rep), repr(junk))
            self.assertEqual(formal.exit_code(rep), 3)

    def test_flags_are_exact_not_truthy(self):
        def with_judge(**kw):
            return complete_rows()[:-2] + [judge_row('P1', 0, 1, **kw), judge_row('P2', 0, 1)]
        for frozen in ('no', 'false', 'yes', 1, [], None, 0):
            self.assertIn('not_frozen', kinds(self.failed(with_judge(frozen=frozen))), repr(frozen))
        for dry in ('false', 0, None, True, 1):
            self.assertIn('dry_run', kinds(self.failed(with_judge(dry_run=dry))), repr(dry))
        rows = complete_rows()
        del rows[0]['dry_run']
        self.assertEqual(kinds(self.failed(rows)), ['dry_run'])  # a step-bot row too
        self.assertEqual(run(with_judge(frozen=False), require_frozen=False)['status'], 'complete')  # --allow-unfrozen is the only way an experiment row passes

    def test_the_settings_a_judge_row_records_must_be_the_frozen_ones(self):
        for k, v in (('model', 'claude-haiku-5-5'), ('max_tokens', 1500), ('temperature', 0.7)):
            rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, **{k: v}), judge_row('P2', 0, 1)]
            exc = self.failed(rows)
            self.assertEqual(kinds(exc), ['not_frozen'], k)
            self.assertIn(k, exc.problems[0]['detail'])
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, model='claude-haiku-5-5'), judge_row('P2', 0, 1)]
        self.assertEqual(run(rows, require_frozen=False)['status'], 'complete')

    def test_the_plan_list_must_be_something_a_number_can_point_into(self):
        bad_numbering = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], n=2), dict(RECS['P1']['plans'][1], n=1)]}}
        self.assertIn('list_integrity', kinds(run(complete_rows(), recs=bad_numbering, on_problem='inconclusive')))
        dup = {**RECS, 'P1': {**RECS['P1'], 'plans': [RECS['P1']['plans'][0], dict(RECS['P1']['plans'][1], key=RECS['P1']['plans'][0]['key'])]}}
        self.assertIn('list_integrity', kinds(run(complete_rows(), recs=dup, on_problem='inconclusive')))

    def test_an_invalid_row_is_never_counted_as_agreeing_even_when_its_number_equals_an_accepted_one(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, plan_list_sha256='0' * 64)  # claims the accepted plan 1, but is not tied to this list
        rep = run(rows, on_problem='inconclusive')
        self.assertEqual(rep['status'], 'inconclusive')
        bad = [r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'km3' and r['run'] == 1][0]
        self.assertEqual((bad['state'], bad['accepted'], bad['agrees']), ('unresolved', [], None))
        self.assertIsNone(rep['analysis'])

    # --- requests that would double or empty a denominator, or name something nobody asked for
    def test_a_request_that_would_double_a_denominator_is_refused(self):
        for kw, word in [(dict(ids=('P1', 'P1', 'P2')), 'points'), (dict(bots=('km3', 'km3', 'judge')), 'bots'), (dict(seeds=(1, 1, 2)), 'seeds')]:
            exc = self.failed(complete_rows(), **kw)
            self.assertEqual(kinds(exc), ['bad_request'])
            self.assertIn(word, exc.problems[0]['detail'])
        self.assertEqual(kinds(self.failed(complete_rows(), judge_repeats=0)), ['bad_request'])
        self.assertEqual(kinds(self.failed(complete_rows(), seeds=())), ['bad_request'])
        rep = run(complete_rows(), seeds=(), on_problem='inconclusive')
        self.assertEqual((rep['status'], formal.exit_code(rep)), ('inconclusive', 3))

    def test_contrasts_and_analysis_parameters_are_validated_before_anything_is_read(self):
        for c in ([('judge', 'nobody')], [('judge', 'judge')], [('judge',)], [('judge', 'km3'), ('judge', 'km3')], [('judge', 5)]):
            self.assertIn('bad_request', kinds(self.failed(complete_rows(), contrasts=c)), c)
        for kw in (dict(min_games=0), dict(min_games=-1), dict(resamples=0), dict(resamples=-5), dict(resamples=True), dict(resamples=1.5)):
            self.assertIn('bad_request', kinds(self.failed(complete_rows(), **kw)), kw)

    # --- earlier requirements
    def test_judge_rows_must_be_real_and_complete(self):
        for bad, kind in [(judge_row('P1', 0, 1, dry_run=True), 'dry_run'), (judge_row('P1', 0, 1, capped=True), 'capped'), (judge_row('P1', 0, None, parse_error='no PLAN line'), 'unresolved')]:
            rows = complete_rows()[:-2] + [bad, judge_row('P2', 0, 1)]
            rep = run(rows, on_problem='inconclusive')
            self.assertIn(kind, kinds(rep), kind)
            self.assertEqual(rep['status'], 'inconclusive')

    def test_step_bot_rows_must_come_from_the_frozen_baseline_executable(self):
        rows = [dict(r, pg_pos_sha256='aaa') if r['bot'] == 'km3' else r for r in complete_rows()]
        self.assertEqual(run(rows, baseline_sha256='aaa')['status'], 'complete')
        rep = run(rows, baseline_sha256='bbb', on_problem='inconclusive')
        self.assertEqual(sorted({p['kind'] for p in rep['problems']}), ['baseline_binary'])
        self.assertEqual(len(rep['problems']), 4)  # every km3 row; the judge rows carry no baseline identity

    def test_a_capped_plan_list_stops_the_comparison(self):
        recs = {**RECS, 'P2': {**RECS['P2'], 'capped': True}}
        rows = [step_row(r['position'], r['bot'], r['seed'], r['plan_number'], recs=recs) if r['bot'] != 'judge' else judge_row(r['position'], 0, r['plan_number'], recs=recs) for r in complete_rows()]
        rep = run(rows, recs=recs, on_problem='inconclusive')
        self.assertIn('capped_list', kinds(rep))
        self.assertTrue(all(r['state'] == 'unresolved' for r in rep['rows'] if r['position'] == 'P2'))

    def test_an_ambiguous_or_unfollowable_reference_is_a_problem_too(self):
        amb = {**ANSWERS, ('P2', 'recorded'): (None, 'ambiguous: the move list fits 2 different listed plans [1, 2]')}
        rep = run(complete_rows(), answers=amb, on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['reference_ambiguous'])
        self.assertIsNone(rep['analysis'])
        bad = {**ANSWERS, ('P2', 'recorded'): (None, 'no legal action labelled "Play:Mesagoza"')}
        self.assertEqual(kinds(run(complete_rows(), answers=bad, on_problem='inconclusive')), ['reference_unresolved'])

    def test_a_row_agrees_when_its_plan_is_any_accepted_move(self):
        refs = {**REFS, 'P1': [{'id': 'recorded', 'labels': ['m']}, {'id': 'alternative', 'labels': ['m2']}]}
        answers = {**ANSWERS, ('P1', 'recorded'): (1, None), ('P1', 'alternative'): (2, None)}
        rep = run(complete_rows(), refs=refs, answers=answers, ids=('P1', 'P2'), elig={**ELIG, 'full_scope_ids': []})
        p1 = [r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'km3']
        self.assertEqual([(r['plan_number'], r['accepted'], r['agrees']) for r in p1], [(1, ['recorded'], True), (2, ['alternative'], True)])

    def test_the_judge_repeats_are_expected_rows_and_the_primary_is_repeat_zero(self):
        rows = complete_rows() + [judge_row('P1', 1, 2), judge_row('P2', 1, 2)]
        rep = run(rows, judge_repeats=2)
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual(rep['row_account']['per_bot_state_counts']['judge'], {'ok': 4})  # four rows for two decisions: a row account, not a sample size
        a = rep['analysis']['prefix']
        self.assertEqual(a['population']['n_decisions'], 2)
        self.assertAlmostEqual(a['rates']['judge']['estimate'], 0.5, places=5)  # repeat 0 only: P1 yes, P2 no
        self.assertAlmostEqual(a['sensitivity']['judge_rate']['estimate'], 0.5, places=5)  # repeat 1: P1 no, P2 yes -> the mean over both repeats is 0.5 too
        self.assertEqual(a['sensitivity']['repeat_consistency']['decisions_with_the_same_plan_in_every_repeat'], 0)
        short = run(complete_rows(), judge_repeats=2, on_problem='inconclusive')  # the second repeat is expected and missing
        self.assertEqual(kinds(short), ['missing', 'missing'])
        rep = run(rows, judge_repeats=1, on_problem='inconclusive')  # rows nobody asked for
        self.assertEqual(kinds(rep), ['unexpected', 'unexpected'])

    # --- the explicit selection (Astra's exam-side requirement)
    def test_the_comparison_needs_an_explicit_selection(self):
        self.assertEqual(kinds(self.failed(complete_rows(), elig=None)), ['no_eligibility'])
        self.assertEqual(kinds(self.failed(complete_rows(), elig={**ELIG, 'primary_ids': ['P1', 'P9']})), ['primary_not_in_batch'])
        self.assertEqual(kinds(self.failed(complete_rows(), elig={**ELIG, 'games': {'P1': 'g1'}})), ['no_game'])
        self.assertEqual(kinds(self.failed(complete_rows(), min_games=3)), ['too_few_games'])
        self.assertEqual(kinds(self.failed(complete_rows(), elig={**ELIG, 'games': {'P1': 'g1', 'P2': 'g1'}})), ['too_few_games'])  # two points of ONE game are one cluster
        for bad in ({**ELIG, 'primary_ids': []}, {**ELIG, 'full_scope_ids': ['P2', 'P3']}, {**ELIG, 'games': {'P1': ''}}, {**ELIG, 'primary_ids': 'P1'}):
            self.assertIn('eligibility_malformed', kinds(self.failed(complete_rows(), elig=bad)), bad)

    def test_every_selected_point_must_have_references(self):
        no_p2 = {k: v for k, v in REFS.items() if k != 'P2'}
        self.assertEqual(kinds(self.failed(complete_rows(), refs=no_p2)), ['reference_missing'])
        self.assertEqual(kinds(self.failed(complete_rows(), refs={**REFS, 'P2': []})), ['reference_missing'])
        for bad in ({'id': 'r'}, {'labels': ['m']}, {'id': 'r', 'labels': []}, {'id': 'r', 'labels': [1]}, 'm', {'id': 5, 'labels': ['m']}):
            self.assertEqual(kinds(run(complete_rows(), refs={**REFS, 'P1': [bad]}, on_problem='inconclusive')), ['reference_malformed'], bad)
        twice = {**REFS, 'P1': [{'id': 'r', 'labels': ['m']}, {'id': 'r', 'labels': ['m2']}]}
        self.assertEqual(kinds(run(complete_rows(), refs=twice, on_problem='inconclusive')), ['reference_malformed'])
        self.assertEqual(kinds(self.failed(complete_rows(), refs=['not', 'an', 'object'])), ['reference_malformed'])

    def test_the_references_are_filtered_to_the_batch_and_the_rest_is_never_read(self):
        m = Matcher(ANSWERS, claims={'P1|km3|1': 1, 'P1|km3|2': 2, 'P2|km3|1': 2, 'P2|km3|2': 2})
        rep = run(complete_rows(), matcher=m)  # REFS holds P3 (not in this batch) and P4 (malformed junk, only in the file)
        self.assertEqual(rep['status'], 'complete')
        asked_points = {pid for pid, _ in m.asked}
        self.assertEqual(asked_points, {'P1', 'P2'})  # P3 and P4 were never replayed or validated
        self.assertEqual(rep['selection']['references_in_file'], 4)
        self.assertEqual(rep['selection']['references_used'], 2)
        self.assertEqual(rep['selection']['references_ignored'], 2)

    def test_points_outside_the_selection_are_a_separate_diagnostic_block_and_never_reach_a_primary_number(self):
        def case(p3_agrees):
            n = 1 if p3_agrees else 2
            rows = complete_rows() + [step_row('P3', 'km3', 1, n), step_row('P3', 'km3', 2, n), judge_row('P3', 0, n)]
            return run(rows, ids=('P1', 'P2', 'P3'))
        agree, disagree = case(True), case(False)
        for rep in (agree, disagree):
            self.assertEqual(rep['status'], 'complete')
            self.assertEqual({r['position'] for r in rep['rows']}, {'P1', 'P2'})  # the report's rows are the primary rows only
            self.assertEqual(rep['n_expected_rows'], 6)
            self.assertEqual(rep['selection']['diagnostic_ids'], ['P3'])
            self.assertEqual(rep['analysis']['prefix']['population']['n_decisions'], 2)
        self.assertEqual(agree['analysis'], disagree['analysis'])  # extreme unselected rows change nothing in the analysis
        self.assertEqual(agree['rows'], disagree['rows'])
        self.assertEqual(agree['row_account'], disagree['row_account'])
        dx_a, dx_d = agree['diagnostic_excluded'], disagree['diagnostic_excluded']
        self.assertEqual(dx_a['points'], [{'position': 'P3', 'reason': 'synthetic exposure'}])
        self.assertEqual(dx_a['per_bot']['judge'], {'decisions_resolved': 1, 'agreement_sum': 1.0})
        self.assertEqual(dx_d['per_bot']['judge'], {'decisions_resolved': 1, 'agreement_sum': 0.0})
        self.assertEqual(dx_a['n_expected_rows'], 3)

    def test_a_problem_at_an_unselected_point_is_diagnostic_and_does_not_stop_the_primary_comparison(self):
        rows = complete_rows() + [step_row('P3', 'km3', 1, 999), step_row('P3', 'km3', 2, 1), judge_row('P3', 0, 1, raw='PLAN: 2')]
        rep = run(rows, ids=('P1', 'P2', 'P3'))
        self.assertEqual((rep['status'], rep['problems']), ('complete', []))
        self.assertIsNotNone(rep['analysis'])
        self.assertEqual(sorted(p['kind'] for p in rep['diagnostic_excluded']['problems']), ['bad_number', 'reply_mismatch'])
        states = {(r['bot'], r['run']): r['state'] for r in rep['diagnostic_excluded']['rows']}
        self.assertEqual(states[('km3', 1)], 'unresolved')
        # an unselected point whose reference is missing or unreadable is diagnostic too
        rep = run(complete_rows() + [step_row('P3', 'km3', 1, 1), step_row('P3', 'km3', 2, 1), judge_row('P3', 0, 1)], ids=('P1', 'P2', 'P3'), refs={k: v for k, v in REFS.items() if k != 'P3'})
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual([p['kind'] for p in rep['diagnostic_excluded']['problems']], ['reference_missing'])
        # but a row at a point the request does not name at all is a batch problem
        rep = run(complete_rows() + [step_row('P3', 'km3', 1, 1)], on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['unexpected'])

    def test_full_plan_agreement_is_reported_apart_and_only_for_the_full_scope_subset(self):
        rep = run(complete_rows())
        full = {(r['bot'], r['run']): r['full_agrees'] for r in rep['rows'] if r['position'] == 'P1'}
        # km3 seed 1 played exactly the recorded complete line; seed 2 did not; the judge's complete plan equals the accepted alternative
        self.assertEqual(full, {('km3', 1): True, ('km3', 2): False, ('judge', 0): True})
        self.assertTrue(all(r['full_agrees'] is None for r in rep['rows'] if r['position'] == 'P2'))  # P2 is not in the full-scope subset
        fs = rep['analysis']['full_scope']
        self.assertEqual(fs['population']['n_decisions'], 1)
        self.assertAlmostEqual(fs['rates']['km3']['estimate'], 0.5, places=5)
        self.assertAlmostEqual(fs['rates']['judge']['estimate'], 1.0, places=5)
        self.assertEqual(rep['analysis']['prefix']['population']['n_decisions'], 2)
        self.assertEqual(run(complete_rows(), elig={**ELIG, 'full_scope_ids': []})['analysis']['full_scope'], None)

    def test_a_judge_plan_that_stops_at_a_chance_event_has_no_complete_plan_and_is_counted_apart(self):
        chance = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], end='chance')] + RECS['P1']['plans'][1:]}}
        rows = [step_row('P1', 'km3', 1, 1, recs=chance), step_row('P1', 'km3', 2, 2, recs=chance), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2),
                judge_row('P1', 0, 1, recs=chance), judge_row('P2', 0, 1)]
        rep = run(rows, recs=chance)
        self.assertEqual(rep['status'], 'complete')
        self.assertIsNone([r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'judge'][0]['full_agrees'])
        fs = rep['analysis']['full_scope']
        self.assertEqual(fs['not_comparable'], {'km3': [], 'judge': ['P1']})
        self.assertIsNone(fs['rates']['judge']['estimate'])
        self.assertEqual(fs['contrasts'][0]['n_pairs_dropped'], 1)
        self.assertEqual(fs['contrasts'][0]['verdict'], 'inconclusive')

    def test_a_judge_plan_that_ends_at_an_attack_or_the_end_of_the_turn_is_a_complete_plan(self):
        for end in ('attack', 'end_turn'):
            recs = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], end=end)] + RECS['P1']['plans'][1:]}}
            rows = [step_row('P1', 'km3', 1, 1, recs=recs), step_row('P1', 'km3', 2, 2, recs=recs), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2),
                    judge_row('P1', 0, 1, recs=recs), judge_row('P2', 0, 1)]
            rep = run(rows, recs=recs)
            self.assertTrue([r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'judge'][0]['full_agrees'], end)

    def test_the_row_cannot_decide_whether_its_plan_is_complete(self):
        # the judge's `cut` is checked against the numbered plan's end in the CURRENT list; editing it alone must not move a decision in or out of the full-plan block
        for cut in ('chance', 'attack', 'opponent_choice', None):
            rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, cut=cut), judge_row('P2', 0, 1)]
            exc = self.failed(rows)
            self.assertEqual(kinds(exc), ['cut_mismatch'], cut)
        # a real chance plan with a row that claims the plan is complete
        chance = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], end='chance')] + RECS['P1']['plans'][1:]}}
        rows = [step_row('P1', 'km3', 1, 1, recs=chance), step_row('P1', 'km3', 2, 2, recs=chance), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2),
                judge_row('P1', 0, 1, recs=chance, cut='end_turn'), judge_row('P2', 0, 1)]
        self.assertEqual(kinds(self.failed(rows, recs=chance)), ['cut_mismatch'])

    def test_a_step_bot_turn_that_pg_pos_cut_at_a_draw_card_is_not_a_complete_plan(self):
        rows = complete_rows()
        rows[0]['pg_pos_cut'] = 'first draw'  # km3 seed 1 at P1 (full-scope): pg_pos stopped at the first draw card
        rep = run(rows)
        full = {(r['bot'], r['run']): r['full_agrees'] for r in rep['rows'] if r['position'] == 'P1'}
        self.assertIsNone(full[('km3', 1)])
        self.assertIs(full[('km3', 2)], False)
        # a bot's value at a decision is the mean over ALL its seeds: with one seed not comparable the decision has no full-plan value (nothing is averaged over a subset)
        self.assertEqual(rep['analysis']['full_scope']['not_comparable']['km3'], ['P1'])
        rows = complete_rows()
        del rows[0]['pg_pos_cut']  # a step row that does not say how its turn ended is not complete either
        self.assertIsNone([r for r in run(rows)['rows'] if r['position'] == 'P1' and r['bot'] == 'km3' and r['run'] == 1][0]['full_agrees'])

    def test_a_reply_cut_at_the_output_cap_is_not_an_intact_answer(self):
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, stop_reason='max_tokens'), judge_row('P2', 0, 1)]
        self.assertEqual(kinds(self.failed(rows)), ['truncated_reply'])

    def test_an_unreadable_label_in_a_full_scope_row_is_a_problem_not_a_crash(self):
        def boom(a, b):
            raise ValueError('cannot read this label')
        self.assertIn('full_plan_unreadable', kinds(run(complete_rows(), fmatch=boom, on_problem='inconclusive')))

    def test_a_broken_plan_list_at_an_unselected_point_never_switches_off_the_replay_of_primary_rows(self):
        broken = {**RECS, 'P3': {**RECS['P3'], 'plans': [RECS['P3']['plans'][0], dict(RECS['P3']['plans'][1], key=RECS['P3']['plans'][0]['key'])]}}  # two plans share a key
        rows = complete_rows() + [step_row('P3', 'km3', 1, 1, recs=RECS), step_row('P3', 'km3', 2, 1, recs=RECS), judge_row('P3', 0, 1, recs=RECS)]
        rep = run(rows, recs=broken, ids=('P1', 'P2', 'P3'))
        self.assertEqual(rep['status'], 'complete')  # the diagnostic point's problem does not stop the primary comparison...
        self.assertIn('list_integrity', [p['kind'] for p in rep['diagnostic_excluded']['problems']])
        # ... but it does not weaken any check on primary rows either: a primary row whose recorded moves replay to another plan still fails
        exc = self.failed(rows, recs=broken, ids=('P1', 'P2', 'P3'), replays={'P1|km3|1': (2, None)})
        self.assertEqual(kinds(exc), ['replay_mismatch'])

    def test_the_games_of_the_eligibility_file_and_of_the_positions_file_must_group_the_points_alike(self):
        same_partition = {'P1': 'kw-A', 'P2': 'kw-B', 'P3': 'kw-C'}  # other names, same grouping: fine
        self.assertEqual(run(complete_rows(), position_games=same_partition)['status'], 'complete')
        merged = {'P1': 'kw-A', 'P2': 'kw-A', 'P3': 'kw-C'}  # the positions file puts P1 and P2 in ONE game: the clusters (and the 10-game gate) would differ
        exc = self.failed(complete_rows(), position_games=merged)
        self.assertEqual(kinds(exc), ['game_conflict'])
        elig_one = {**ELIG, 'games': {'P1': 'g1', 'P2': 'g1', 'P3': 'g3'}}
        self.assertEqual(kinds(self.failed(complete_rows(), elig=elig_one, position_games=same_partition, min_games=1)), ['game_conflict'])
        self.assertEqual(run(complete_rows(), position_games={'P1': None, 'P2': ''})['status'], 'complete')  # a position file without games has nothing to contradict

    def test_the_eligibility_file_is_strict(self):
        for bad in ({k: v for k, v in ELIG.items() if k != 'full_scope_ids'}, {**ELIG, 'full_scope_id': ['P1']}, {**ELIG, 'schema': 'something else'}, {**ELIG, 'extra': 1}):
            self.assertIn('eligibility_malformed', kinds(self.failed(complete_rows(), elig=bad)), bad)
        self.assertEqual(run(complete_rows(), elig={**ELIG, 'schema': analysis.ELIGIBILITY_SCHEMA})['status'], 'complete')
        # game ids that differ only in case or spacing are different games to the machine and probably the same game to the author
        for games in ({'P1': 'g1', 'P2': 'G1'}, {'P1': 'g1', 'P2': 'g1 '}, {'P1': 'g1', 'P2': 'g​2'}):
            self.assertIn('eligibility_malformed', kinds(self.failed(complete_rows(), elig={**ELIG, 'games': {**games, 'P3': 'g3'}}, min_games=1)), games)

    def test_point_ids_and_bot_names_may_not_contain_the_tag_separator(self):
        recs = {**RECS, 'P|1': mk_rec('P|1')}
        exc = self.failed(complete_rows(), ids=('P1', 'P|1'), recs=recs)
        self.assertEqual(kinds(exc), ['bad_request'])
        self.assertEqual(kinds(self.failed(complete_rows(), bots=('km|3', 'judge'))), ['bad_request'])

    def test_the_report_does_not_depend_on_the_order_the_points_were_named_in(self):
        a = run(complete_rows(), ids=('P1', 'P2'))
        b = run(list(reversed(complete_rows())), ids=('P2', 'P1'))
        self.assertEqual(a, b)

    def test_a_failed_report_shows_no_numbers_for_the_unselected_points_either(self):
        rows = complete_rows() + [step_row('P3', 'km3', 1, 1), step_row('P3', 'km3', 2, 1), judge_row('P3', 0, 1)]
        rows[0] = step_row('P1', 'km3', 1, 999)
        rep = run(rows, ids=('P1', 'P2', 'P3'), on_problem='inconclusive')
        dx = rep['diagnostic_excluded']
        self.assertIsNone(dx['per_bot'])
        self.assertTrue(all(r['agrees'] is None and r['accepted'] == [] for r in dx['rows']))
        self.assertEqual(dx['shares_a_game_with_a_primary_point'], [])
        shared = run(complete_rows() + [step_row('P3', 'km3', 1, 1), step_row('P3', 'km3', 2, 1), judge_row('P3', 0, 1)], ids=('P1', 'P2', 'P3'),
                     elig={**ELIG, 'games': {'P1': 'g1', 'P2': 'g2', 'P3': 'g2'}})
        self.assertEqual(shared['diagnostic_excluded']['shares_a_game_with_a_primary_point'], ['P3'])  # exposure is per game: say so

    def test_the_analysis_gets_the_requested_parameters(self):
        with mock.patch.object(analysis, 'analyse', wraps=analysis.analyse) as spy:
            run(complete_rows(), contrasts=[('judge', 'km3')], min_games=2, resamples=123)
        args, kwargs = spy.call_args
        self.assertEqual(args[4], [('judge', 'km3')])  # contrasts
        self.assertEqual(args[5], 123)  # resamples
        self.assertEqual(kwargs.get('min_games'), 2)


# ---------------------------------------------------------------------------------------------------------------------------------- helpers in judge.py
@unittest.skipUnless(HAVE_BIN, 'judge_plans is not built')
class JudgeHelpers(unittest.TestCase):
    def test_read_rows_turns_a_bad_line_into_a_problem_with_its_place(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'rows.jsonl')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('﻿{"position": "a", "bot": "km3"}\n\n{"truncated": \n[1, 2]\n{"position": "a", "position": "b"}\n{"s": "line separator"}\n')  # BOM, blank, truncated, non-object, repeated key, U+2028 in a string
        rows, problems, hashes = judge.read_rows([p])
        self.assertEqual(len(rows), 3)  # the first object, the list (a non-object is the formal path's problem) and the U+2028 line (not split)
        self.assertEqual([x['kind'] for x in problems], ['unreadable_row', 'unreadable_row'])
        self.assertIn('line 3', problems[0]['detail'])
        self.assertIn('duplicate key', problems[1]['detail'])
        self.assertEqual(hashes[p], judge.file_sha256(p))  # the hash is of the bytes the rows were read from
        bad = os.path.join(d, 'latin.jsonl')
        with open(bad, 'wb') as f:
            f.write(b'{"position": "caf\xe9"}\n')
        rows, problems, _ = judge.read_rows([bad])
        self.assertEqual((rows, [x['kind'] for x in problems]), ([], ['unreadable_row']))  # not UTF-8: a problem, not a crash

    def test_seeds_and_contrasts_are_parsed_without_crashing(self):
        self.assertEqual(judge.parse_seeds('1, 2,,3,'), ([1, 2, 3], []))
        seeds, problems = judge.parse_seeds('1,a,1.0')
        self.assertEqual((seeds, len(problems)), ([1], 2))
        self.assertIsNone(judge.parse_contrasts(None))
        self.assertEqual(judge.parse_contrasts('judge:km3, judge:kx3'), [('judge', 'km3'), ('judge', 'kx3')])
        self.assertEqual(judge.parse_contrasts('judge,a:b:c'), [('judge',), ('a:b:c',)])  # kept as pieces the request check names

    def test_match_plans_answers_an_unreadable_move_list_for_that_item_alone(self):
        recs = judge.list_plans(['MINI-BLOWER'], POS, DECKS)
        good = recs['MINI-BLOWER']['plans'][0]['labels']
        out = judge.match_plans([('MINI-BLOWER', 't-good', good), ('MINI-BLOWER', 't-badjson', ['Foo#{oops']), ('MINI-BLOWER', 't-nonstr', [1, None]),
                                 ('MINI-BLOWER', 't-empty', []), ('MINI-BLOWER', 't-legacy', ['Foo{a:1.5}'])], recs, POS, DECKS)
        self.assertIsNotNone(out['t-good'][0])
        for tag in ('t-badjson', 't-nonstr', 't-empty', 't-legacy'):
            self.assertIsNone(out[tag][0], tag)
            self.assertIn('unreadable move list', out[tag][1])

    def test_normalize_full_is_a_canonical_comparable_form_that_keeps_slots(self):
        a = judge.normalize_full(['Place:Axew@3', 'Ability@2', 'Foo#{"b": 1, "a": 2}', 'EndTurn'])
        self.assertEqual(a, ['Place:Axew@3', 'Ability@2', 'Foo#{"a":2,"b":1}'])
        self.assertEqual(judge.normalize_full(['Attack:Slam']), ['Attack:Slam'])
        self.assertEqual(judge.normalize_full(['EndTurn', 'EndTurn']), ['EndTurn'])  # only the closing End the turn is dropped
        with self.assertRaises(ValueError):
            judge.normalize_full(['Foo#{oops'])

    def test_energy_lists_are_a_multiset_in_every_canonical_label(self):
        a = judge.concrete_label('ChooseRetreatEnergy#{"to_in_play_idx": 1, "energies": ["Water", "Fire"]}')
        self.assertEqual(a, 'ChooseRetreatEnergy#{"energies":["Fire","Water"],"to_in_play_idx":1}')
        self.assertEqual(judge.concrete_label('ChooseRetreatEnergy#{"energies":["Fire","Water"],"to_in_play_idx":1}'), a)
        self.assertNotEqual(judge.concrete_label('ChooseRetreatEnergy#{"energies":["Fire","Fire"],"to_in_play_idx":1}'), a)

    def test_full_match_is_label_by_label_in_order_with_slotless_references(self):
        fm = judge.full_match
        row = ['Place:Axew@3', 'Attach:1Fire@0 zone', 'Ability@2', 'Attack:Slam']
        self.assertTrue(fm(row, ['Place:Axew@3', 'Attach:1Fire@0 zone', 'Ability@2', 'Attack:Slam']))
        self.assertTrue(fm(row, ['Place:Axew', 'Attach:1Fire@0 zone', 'Ability', 'Attack:Slam']))  # a reference that names no slot fits any slot (as in the replay)
        self.assertFalse(fm(row, ['Place:Axew@1', 'Attach:1Fire@0 zone', 'Ability@2', 'Attack:Slam']))  # a slot that is named must be the slot
        self.assertFalse(fm(row, ['Place:Axew@3', 'Attach:1Fire@0 zone', 'Ability@1', 'Attack:Slam']))  # Ability@1 and Ability@2 are different Pokémon
        self.assertFalse(fm(['Ability@2'], ['Place:Axew@3']))
        self.assertFalse(fm(['Ability@2', 'Attack:Slam'], ['Attack:Slam', 'Ability@2']))  # the order of the moves is part of a complete plan
        self.assertFalse(fm(row, row[:-1]))  # a reference that is a prefix is not the complete plan
        self.assertTrue(fm(row + ['EndTurn'], row))  # the closing End the turn is not a move that matters

    def test_resolve_ids_refuses_a_repeated_point(self):
        class A:
            ids, id, set = ['MINI-BLOWER', 'MINI-BLOWER'], None, None
        with self.assertRaises(SystemExit) as cm:
            judge.resolve_ids(A, judge.load_positions(POS))
        self.assertIn('more than once', str(cm.exception))

    def test_duplicate_keys_in_a_json_input_are_refused(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'refs.json')
        with open(p, 'w') as f:
            f.write('{"P1": [{"id": "keep-me", "labels": ["a"]}], "P1": [{"id": "other", "labels": ["z"]}]}')
        with self.assertRaises(ValueError) as cm:
            formal.load_json(p)
        self.assertIn('duplicate key', str(cm.exception))

    def test_the_plan_lists_of_the_fixtures_are_named_by_their_own_labels(self):
        # every listed plan's own labels must replay to exactly that plan (a label table that drops information would show up here)
        pids = [p['id'] for p in json.load(open(POS))]
        recs = judge.list_plans(pids, POS, DECKS)
        check = judge.label_roundtrip(recs, POS, DECKS)
        for pid, v in check.items():
            self.assertEqual((v['ambiguous'], v['unfollowable'], v['unique']), (0, 0, v['n_plans']), pid)


# ---------------------------------------------------------------------------------------------------------------------------------- the command line
FAKE_PG_POS = '''#!/usr/bin/env python3
import json, sys
a = sys.argv
pid = a[a.index('--only') + 1]
seeds = [int(x) for x in a[a.index('--seeds') + 1].split(',')]
plan = json.load(open(%r))[pid]
for s in seeds:
    print(json.dumps({'kind': 'free', 'id': pid, 'seed': s, 'plan': plan, 'cut': 'end of turn'}))
'''


@unittest.skipUnless(HAVE_BIN, 'judge_plans is not built')
class CommandLinePath(unittest.TestCase):
    """The CLI itself (judge.py compare / score / run) on the fixtures: twelve copies of the Field Blower position, one game each; rows are written by the real
    row writers (judge_one, run_pg_pos with a stand-in executable), so the writers and the checker are tested against each other. BLW-11 is a point OUTSIDE the
    primary selection (a diagnostic point); the references file also names a point that is not in the batch."""

    N = 12
    EXPOSED = 'BLW-11'

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        blower = next(p for p in json.load(open(POS)) if p['id'] == 'MINI-BLOWER')
        clones = []
        for i in range(cls.N):
            c = json.loads(json.dumps(blower))
            c['id'], c['game'] = f'BLW-{i:02d}', f'game-{i:02d}'
            clones.append(c)
        cls.positions_path = os.path.join(cls.tmp, 'positions.json')
        with open(cls.positions_path, 'w') as f:
            json.dump(clones, f)
        cls.ids = [c['id'] for c in clones]
        cls.primary = [i for i in cls.ids if i != cls.EXPOSED]
        cls.positions = judge.load_positions(cls.positions_path)
        cls.recs = judge.list_plans(cls.ids, cls.positions_path, DECKS)
        plans = cls.recs[cls.ids[0]]['plans']
        # the two plans "play Field Blower on target A / on target B, then end the turn"
        cls.blow = [p for p in plans if p['end'] == 'end_turn' and len(p['labels']) == 3 and p['labels'][0] == 'Play:Field Blower']
        assert len(cls.blow) == 2, [p['labels'] for p in plans]
        cls.judge_rows_ok = cls.make_judge_rows(lambda i: cls.blow[1 if i in (2, 5, 8) else 0]['n'])
        cls.km3_rows_ok = cls.make_step_rows('km3', [1], lambda i, s: cls.blow[0 if i in (0, 1) else 1]['labels'])

    @classmethod
    def make_judge_rows(cls, choose, repeat=0, model=None):
        rows = []
        for i, pid in enumerate(cls.ids):
            n = choose(i)
            shown = {p['n']: k for k, p in judge.render_prompt(cls.positions[pid], cls.recs[pid], judge.FROZEN['order'], DECKS)[2].items()}
            reply = (f'PLAN: {shown[n]}\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})
            with mock.patch.object(judge, 'call_claude', return_value=reply):
                r, _, _ = judge.judge_one(pid, cls.positions, cls.recs, judge.FROZEN['order'], True, model or judge.MODEL, decks_dir=DECKS)
            r['repeat'], r['tag'] = repeat, None
            rows.append(json.loads(json.dumps(r)))
        return rows

    @classmethod
    def make_step_rows(cls, bot, seeds, choose_labels):
        rows = []
        for s in seeds:
            d = tempfile.mkdtemp()
            plan_file, path = os.path.join(d, 'plans.json'), os.path.join(d, 'fake_pg_pos')
            with open(plan_file, 'w') as f:
                json.dump({pid: choose_labels(i, s) for i, pid in enumerate(cls.ids)}, f)
            with open(path, 'w') as f:
                f.write(FAKE_PG_POS % plan_file)
            os.chmod(path, 0o755)
            rows += json.loads(json.dumps(judge.run_pg_pos(bot, cls.ids, [s], cls.recs, cls.positions_path, DECKS, bin_path=path)))
        return rows

    def cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = judge.main(argv)
        return code, out.getvalue(), err.getvalue()

    def files(self, rows, refs=None, elig=None, raw_lines=None):
        d = tempfile.mkdtemp()
        rf, qf, ef = os.path.join(d, 'rows.jsonl'), os.path.join(d, 'refs.json'), os.path.join(d, 'elig.json')
        with open(rf, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in rows) + '\n' + (raw_lines or ''))
        full = {pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in self.ids}
        full['NOT-IN-THE-BATCH'] = 'junk that no comparison may read'
        with open(qf, 'w') as f:
            json.dump(refs if refs is not None else full, f)
        default = {'schema': analysis.ELIGIBILITY_SCHEMA, 'primary_ids': self.primary, 'full_scope_ids': self.primary[:4], 'games': {c['id']: c['game'] for c in self.positions.values()},
                   'excluded_reasons': {self.EXPOSED: 'developer exposure to one answer-key example (synthetic)'}}
        with open(ef, 'w') as f:
            json.dump(elig if elig is not None else default, f)
        return d, rf, qf, ef

    def argv(self, rf, qf, ef, ids=None, extra=(), bots='km3,judge', seeds='1'):
        return ['compare', '--positions', self.positions_path, '--decks', DECKS, '--ids', *(ids or self.ids), '--results', rf, '--bots', bots, '--seeds', seeds,
                '--references', qf, '--eligibility', ef, '--allow-other-binaries', *extra]  # the fixtures' rows were not made by the frozen executables

    def good_rows(self):
        return [dict(r) for r in self.km3_rows_ok + self.judge_rows_ok]

    def km3(self, rows, i):
        return [r for r in rows if r['bot'] == 'km3'][i]

    def jdg(self, rows, i):
        return [r for r in rows if r['bot'] == 'judge'][i]

    def good_report(self, extra=()):
        d, rf, qf, ef = self.files(self.good_rows())
        out = os.path.join(d, 'rep.json')
        code, o, err = self.cli(self.argv(rf, qf, ef, extra=['--out', out, '--resamples', '2000', *extra]))
        self.assertEqual(code, 0, err)
        with open(out) as f:
            return json.load(f), o, err

    # --- the complete batch
    def test_a_complete_batch_passes_with_exit_code_0_and_the_clustered_analysis(self):
        rep, out, err = self.good_report()
        self.assertEqual(rep['status'], 'complete')
        self.assertNotIn('agreement', rep)
        self.assertEqual(rep['row_account']['per_bot_state_counts'], {'km3': {'ok': 11}, 'judge': {'ok': 11}})  # the 11 primary points; BLW-11 is not in the account
        an = rep['analysis']
        self.assertEqual((an['prefix']['population']['n_games'], an['prefix']['population']['n_decisions']), (11, 11))
        self.assertAlmostEqual(an['prefix']['rates']['judge']['estimate'], 8 / 11, places=5)  # BLW-11 is not in the primary comparison
        self.assertAlmostEqual(an['prefix']['rates']['km3']['estimate'], 2 / 11, places=5)
        c = an['prefix']['contrasts'][0]
        self.assertAlmostEqual(c['estimate'], 6 / 11, places=5)
        self.assertEqual((c['a'], c['b'], c['verdict'], c['sign_flip']), ('judge', 'km3', 'judge higher', 'exact'))
        # full-plan agreement: only the first four primary points; the judge's complete plan equals the accepted one except at BLW-02, km3 played it at BLW-00 and -01
        fs = an['full_scope']
        self.assertEqual(fs['population']['n_decisions'], 4)
        self.assertAlmostEqual(fs['rates']['judge']['estimate'], 3 / 4, places=5)
        self.assertAlmostEqual(fs['rates']['km3']['estimate'], 2 / 4, places=5)
        self.assertEqual(fs['contrasts'][0]['verdict'], 'inconclusive')  # four games
        self.assertEqual(rep['diagnostic_excluded']['points'], [{'position': self.EXPOSED, 'reason': 'developer exposure to one answer-key example (synthetic)'}])
        self.assertEqual(rep['selection']['references_in_file'], 13)
        self.assertEqual(rep['selection']['references_ignored'], 1)
        self.assertIn('PREFIX agreement', out)
        self.assertIn('judge higher', out)
        self.assertIn('diagnostic only', out)
        self.assertIn('EXPERIMENT RUN', err)  # --allow-other-binaries is an experiment switch and says so
        self.assertIn('EXPERIMENT RESULT (not the formal result', out)
        self.assertIs(rep['formal'], False)

    def test_the_report_records_what_it_was_made_from_and_which_switches_were_on(self):
        rep, out, err = self.good_report()
        run_info = rep['run']
        self.assertFalse(run_info['formal'])
        self.assertEqual(run_info['experiment_switches'], ['--allow-other-binaries', '--resamples 2000 (< 5000)'])  # the test's small resample count is an experiment setting too
        self.assertEqual(set(run_info['inputs']), {'positions_sha256', 'references_sha256', 'eligibility_sha256', 'results_sha256', 'decks_sha256', 'card_database'})
        self.assertEqual(run_info['inputs']['card_database']['sha256'], judge.file_sha256(judge.card_database_path()))
        self.assertEqual(run_info['inputs']['decks_sha256'], judge.dir_sha256(DECKS))
        self.assertEqual(rep['formal'], False)
        self.assertEqual(run_info['plan_list_sha256'][self.ids[0]], formal.plan_list_sha256(self.recs[self.ids[0]]))
        self.assertEqual(run_info['request']['seeds'], [1])
        self.assertEqual(run_info['freeze']['fingerprint_now'], judge.fingerprint())
        self.assertEqual(run_info['plan_list_label_check']['positions'], {})  # the Field Blower lists are named by their own labels
        self.assertEqual(rep['analysis']['method']['judge_repeats'], 1)
        self.assertEqual(rep['analysis']['method']['bots'], ['km3', 'judge'])

    def test_unselected_points_cannot_change_a_primary_number_even_when_their_rows_are_garbage(self):
        base, _, _ = self.good_report()
        rows = self.good_rows()
        for r in rows:
            if r['position'] == self.EXPOSED:
                r.update(plan_number=999) if r['bot'] == 'km3' else r.update(plan_number=0, shown_number=77)
        d, rf, qf, ef = self.files(rows)
        out = os.path.join(d, 'rep.json')
        code, _, err = self.cli(self.argv(rf, qf, ef, extra=['--out', out, '--resamples', '2000']))
        self.assertEqual(code, 0, err)  # a problem at the unselected point does not stop the primary comparison
        rep = json.load(open(out))
        self.assertEqual(rep['analysis'], base['analysis'])
        self.assertEqual(rep['rows'], base['rows'])
        kinds_ = {p['kind'] for p in rep['diagnostic_excluded']['problems']}
        self.assertIn('bad_number', kinds_)

    def test_a_selected_point_without_references_fails_and_unselected_ones_are_not_needed(self):
        refs = {pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in self.ids if pid != 'BLW-05'}
        d, rf, qf, ef = self.files(self.good_rows(), refs=refs)
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('reference_missing', err)
        refs = {pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in self.primary}  # no references at all for the unselected BLW-11
        d, rf, qf, ef = self.files(self.good_rows(), refs=refs)
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--resamples', '200']))
        self.assertEqual(code, 0, err)

    def test_the_selection_is_required_and_checked_on_the_command_line(self):
        d, rf, qf, ef = self.files(self.good_rows(), elig={'primary_ids': ['BLW-00', 'NOPE'], 'full_scope_ids': [], 'games': {'BLW-00': 'game-00'}})
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('primary_not_in_batch', err)
        d, rf, qf, ef = self.files(self.good_rows(), elig={'primary_ids': self.primary[:5], 'full_scope_ids': [], 'games': {c: self.positions[c]['game'] for c in self.primary[:5]}})
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('too_few_games', err)
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--min-games', '5', '--resamples', '200']))
        self.assertEqual(code, 0, err)
        self.assertIn('EXPERIMENT RUN', err)

    # --- the plan-number hole, on the real writers' rows
    def run_bad(self, mutate, expect_kind, extra=(), rows_expected=22):
        rows = self.good_rows()
        mutate(rows)
        d, rf, qf, ef = self.files(rows)
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--out', os.path.join(d, 'rep.json'), '--resamples', '200', *extra]))
        self.assertEqual(code, 2, err)
        self.assertIn('COMPARISON FAILED', err)
        self.assertIn(expect_kind, err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual((rep['status'], rep['analysis']), ('failed', None))
        self.assertEqual(len(rep['rows']), rows_expected)  # every expected primary row is still listed
        self.assertTrue(all(r['agrees'] is None for r in rep['rows']))
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--on-problem', 'inconclusive', '--resamples', '200', *extra]))
        self.assertEqual(code, 3, err)
        return rows

    def test_a_plan_number_outside_the_list_fails_the_command(self):
        n_plans = self.recs[self.ids[0]]['n_plans']
        self.run_bad(lambda rows: self.km3(rows, 0).update(plan_number=999), 'bad_number')
        self.run_bad(lambda rows: self.jdg(rows, 3).update(plan_number=n_plans + 1), 'bad_number')
        self.run_bad(lambda rows: self.km3(rows, 0).update(plan_number=float(self.km3(rows, 0)['plan_number'])), 'bad_number')

    def test_a_plan_number_with_an_error_fails_the_command(self):
        self.run_bad(lambda rows: self.km3(rows, 0).update(match_error='ambiguous: the move list fits 2 different listed plans'), 'contradictory')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(parse_error='several different PLAN lines [1, 2]'), 'contradictory')

    def test_a_row_that_does_not_replay_to_its_number_fails_the_command(self):
        a, b = self.blow[0]['n'], self.blow[1]['n']

        def retarget(rows):  # the row says plan b, with b's key, but its recorded moves are plan a's: replay disagrees (the identity fields alone would pass)
            r = self.km3(rows, 0)
            assert r['plan_number'] == a
            r.update(plan_number=b, plan_key=self.blow[1]['key'])
        self.run_bad(retarget, 'replay_mismatch')
        self.run_bad(lambda rows: self.km3(rows, 0).update(plan_number=b), 'key_mismatch')  # a changed number with the old key

    def test_a_row_made_from_another_plan_list_fails_the_command(self):
        self.run_bad(lambda rows: self.km3(rows, 1).update(plan_list_sha256='f' * 64), 'list_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 1).update(plan_list_sha256=None), 'list_mismatch')

    def test_a_judge_row_not_tied_to_its_prompt_and_reply_fails_the_command(self):
        def shift_shown(rows):
            r = self.jdg(rows, 0)
            r['shown_number'] = r['shown_number'] % self.recs[self.ids[0]]['n_plans'] + 1
        self.run_bad(shift_shown, 'shown_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(prompt_sha256='0' * 16), 'prompt_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(plan=['Play:Field Blower']), 'labels_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(raw='PLAN: 1\nREASON: edited'), 'reply_mismatch')

    def test_a_forged_frozen_flag_or_model_fails_the_command(self):
        # a row the writer made under other settings, with `frozen` flipped to true by hand: the recorded settings give it away
        bad = self.make_judge_rows(lambda i: self.blow[0]['n'], model='claude-haiku-5-5')
        self.assertFalse(bad[0]['frozen'])
        forged = [dict(r, frozen=True) for r in bad]
        d, rf, qf, ef = self.files([dict(r) for r in self.km3_rows_ok] + forged)
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('not_frozen', err)
        self.assertIn("model='claude-haiku-5-5'", err)
        self.run_bad(lambda rows: self.jdg(rows, 0).update(frozen='no'), 'not_frozen')

    def test_unfrozen_judge_rows_are_refused_without_the_switch_and_pass_with_it(self):
        other = self.make_judge_rows(lambda i: self.blow[0]['n'], model='claude-haiku-5-5')
        d, rf, qf, ef = self.files([dict(r) for r in self.km3_rows_ok] + other)
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--resamples', '200']))
        self.assertEqual(code, 2)
        out_path = os.path.join(d, 'rep.json')
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--allow-unfrozen', '--resamples', '200', '--out', out_path]))
        self.assertEqual(code, 0, err)
        rep = json.load(open(out_path))
        self.assertFalse(rep['run']['formal'])
        self.assertIn('--allow-unfrozen', rep['run']['experiment_switches'])

    def test_a_row_made_under_another_order_is_refused_even_with_a_hand_set_frozen_flag(self):
        # the prompt is re-rendered under the FROZEN order: a row answered from a forward-ordered prompt fails on the prompt hash whatever `frozen` says
        fwd = self.make_judge_rows(lambda i: self.blow[0]['n'])
        shown_forward = {p['n']: k for k, p in judge.render_prompt(self.positions[self.ids[0]], self.recs[self.ids[0]], 'forward', DECKS)[2].items()}
        reply = (f"PLAN: {shown_forward[self.blow[0]['n']]}\nREASON: x", {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})
        with mock.patch.object(judge, 'call_claude', return_value=reply):
            r, _, _ = judge.judge_one(self.ids[0], self.positions, self.recs, 'forward', True, judge.MODEL, decks_dir=DECKS)
        r['repeat'], r['tag'], r['frozen'] = 0, None, True
        fwd[0] = json.loads(json.dumps(r))
        d, rf, qf, ef = self.files([dict(x) for x in self.km3_rows_ok] + fwd)
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertTrue('prompt_mismatch' in err or 'shown_mismatch' in err, err)

    # --- request options and malformed inputs: clean failures, never a traceback
    def test_judge_repeats_and_seeds_and_contrasts_are_wired_through(self):
        second_judge = self.make_judge_rows(lambda i: self.blow[0]['n'], repeat=1)
        km3_two = self.make_step_rows('km3', [1, 2], lambda i, s: self.blow[0 if i in (0, 1) else 1]['labels'])
        d, rf, qf, ef = self.files(km3_two + self.judge_rows_ok + second_judge)
        out = os.path.join(d, 'rep.json')
        code, o, err = self.cli(self.argv(rf, qf, ef, seeds='1,2', extra=['--judge-repeats', '2', '--contrasts', 'judge:km3', '--resamples', '300', '--out', out]))
        self.assertEqual(code, 0, err)
        rep = json.load(open(out))
        self.assertEqual(rep['row_account']['per_bot_state_counts'], {'km3': {'ok': 22}, 'judge': {'ok': 22}})  # rows: 11 points x 2 seeds / x 2 repeats
        a = rep['analysis']['prefix']
        self.assertEqual(a['population']['n_decisions'], 11)  # a decision counts once
        self.assertAlmostEqual(a['rates']['judge']['estimate'], 8 / 11, places=5)  # the primary is repeat 0
        self.assertAlmostEqual(a['sensitivity']['judge_rate']['estimate'], 9.5 / 11, places=5)  # repeat 1 agrees at all 11 points: (8 x 1 + 3 x 0.5) / 11
        self.assertEqual(rep['analysis']['method']['contrasts'], ['judge:km3'])
        self.assertEqual(rep['run']['request']['seeds'], [1, 2])
        # the second repeat is expected: without it the batch fails
        d, rf, qf, ef = self.files(km3_two + self.judge_rows_ok)
        code, o, err = self.cli(self.argv(rf, qf, ef, seeds='1,2', extra=['--judge-repeats', '2']))
        self.assertEqual(code, 2)
        self.assertIn('missing', err)

    def test_bad_request_options_are_clean_failures_with_a_report(self):
        d, rf, qf, ef = self.files(self.good_rows())
        for extra, kind in ((['--contrasts', 'judge'], 'bad_request'), (['--contrasts', 'judge:nobody'], 'bad_request'), (['--contrasts', 'judge:judge'], 'bad_request'),
                            (['--resamples', '0'], 'bad_request'), (['--resamples', '-5'], 'bad_request'), (['--min-games', '0'], 'bad_request'), (['--judge-repeats', '0'], 'bad_request')):
            out = os.path.join(d, 'rep.json')
            code, o, err = self.cli(self.argv(rf, qf, ef, extra=['--out', out, *extra]))
            self.assertEqual(code, 2, (extra, err))
            self.assertIn(kind, err)
            self.assertEqual(json.load(open(out))['status'], 'failed')
            code, o, err = self.cli(self.argv(rf, qf, ef, extra=['--on-problem', 'inconclusive', *extra]))
            self.assertEqual(code, 3, (extra, err))
        code, o, err = self.cli(self.argv(rf, qf, ef, seeds='1,a'))
        self.assertEqual(code, 2)
        self.assertIn('not a whole number', err)

    def test_malformed_inputs_are_problems_with_a_report_not_tracebacks(self):
        d, rf, qf, ef = self.files(self.good_rows(), raw_lines='{"truncated": \n[1, 2]\n')
        out = os.path.join(d, 'rep.json')
        code, o, err = self.cli(self.argv(rf, qf, ef, extra=['--out', out]))
        self.assertEqual(code, 2)
        self.assertIn('unreadable_row', err)
        self.assertIn('bad_row', err)
        self.assertEqual(json.load(open(out))['status'], 'failed')
        # a damaged label in a row's move list or in a reference is that item's problem
        rows = self.good_rows()
        self.km3(rows, 0)['plan_full'] = ['Play:Field Blower', 'DiscardToolFromPokemon#{oops', 'EndTurn']
        d, rf, qf, ef = self.files(rows)
        code, o, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('replay_mismatch', err)
        self.assertIn('unreadable move list', err)
        refs = {pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in self.ids}
        refs['BLW-03'] = [{'id': 'recorded', 'labels': ['Foo#{oops']}]
        d, rf, qf, ef = self.files(self.good_rows(), refs=refs)
        code, o, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('reference_unresolved', err)

    def test_the_report_is_never_written_over_an_input_file(self):
        d, rf, qf, ef = self.files(self.good_rows())
        before = judge.file_sha256(rf)
        for target in (rf, qf, ef, self.positions_path):
            with self.assertRaises(SystemExit) as cm:
                self.cli(self.argv(rf, qf, ef, extra=['--out', target]))
            self.assertIn('one of the input files', str(cm.exception))
        self.assertEqual(judge.file_sha256(rf), before)
        alias = os.path.join(d, '.', 'rows.jsonl')  # an aliased path to the same file
        with self.assertRaises(SystemExit):
            self.cli(self.argv(rf, qf, ef, extra=['--out', alias]))

    def test_compare_does_not_take_a_prompt_version(self):
        d, rf, qf, ef = self.files(self.good_rows())
        with self.assertRaises(SystemExit) as cm:
            self.cli(self.argv(rf, qf, ef, extra=['--prompt', 'v2']))
        self.assertIn('does not take --prompt', str(cm.exception))

    # --- earlier requirements, on the command line
    def test_an_ambiguous_reference_name_fails_the_command(self):
        # the bare recorded name 'DiscardToolFromPokemon' fits both targets: it must not be resolved to the first one
        refs = {pid: [{'id': 'recorded', 'labels': ['Play:Field Blower', 'DiscardToolFromPokemon']}] for pid in self.ids}
        d, rf, qf, ef = self.files(self.good_rows(), refs=refs)
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--out', os.path.join(d, 'rep.json')]))
        self.assertEqual(code, 2)
        self.assertIn('reference_ambiguous', err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual((rep['status'], rep['analysis'], len(rep['rows'])), ('failed', None, 22))
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--on-problem', 'inconclusive', '--out', os.path.join(d, 'rep2.json')]))
        self.assertEqual(code, 3)
        rep = json.load(open(os.path.join(d, 'rep2.json')))
        self.assertEqual((rep['status'], rep['analysis'], len(rep['rows'])), ('inconclusive', None, 22))
        self.assertTrue(all(r['agrees'] is None for r in rep['rows']))

    def test_a_row_with_no_listed_plan_fails_the_command(self):
        def drop(rows):
            r = self.km3(rows, 1)
            r.update(plan_number=None, plan_key=None, match_error='ambiguous: the move list fits 2 different listed plans [3, 4]')
        self.run_bad(drop, 'ambiguous')

    def test_rows_written_before_the_identity_fields_say_so(self):
        def strip(rows):
            for r in rows:
                if r['bot'] == 'judge':
                    r.pop('plan_list_sha256', None)
                    r.pop('plan_key', None)
        d, rf, qf, ef = self.files([dict(r) for r in self.km3_rows_ok] + [{k: v for k, v in r.items() if k not in ('plan_list_sha256', 'plan_key')} for r in self.judge_rows_ok])
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('predates_identity', err)
        self.assertNotIn('key_mismatch', err)

    def test_the_run_command_fails_when_a_row_cannot_be_mapped_to_one_plan(self):
        full = sorted({l for p in self.recs[self.ids[0]]['plans'] for l in p['labels'] if l.startswith('DiscardToolFromPokemon#')})

        def argv(path, out):
            return ['run', '--bot', 'km3', '--positions', self.positions_path, '--decks', DECKS, '--ids', self.ids[0], '--seeds', '1', '--pg-pos-bin', path, '--out', out]

        def fake(plan):
            d = tempfile.mkdtemp()
            pf, path = os.path.join(d, 'plans.json'), os.path.join(d, 'fake_pg_pos')
            with open(pf, 'w') as f:
                json.dump({self.ids[0]: plan}, f)
            with open(path, 'w') as f:
                f.write(FAKE_PG_POS % pf)
            os.chmod(path, 0o755)
            return d, path

        d, path = fake(['Play:Field Blower', 'DiscardToolFromPokemon'])  # the bare name fits both targets
        out = os.path.join(d, 'rows.jsonl')
        code, _, err = self.cli(argv(path, out))
        self.assertEqual(code, 2)
        self.assertIn('could not be mapped to ONE listed plan', err)
        row = json.loads(open(out).read().splitlines()[0])  # the row is still written, so the failure is visible in the file
        self.assertIsNone(row['plan_number'])
        self.assertTrue(row['match_error'].startswith('ambiguous'))
        d, path = fake(['Play:Field Blower', full[0]])  # the full label names the target
        out = os.path.join(d, 'rows.jsonl')
        code, _, err = self.cli(argv(path, out))
        self.assertEqual(code, 0, err)
        row = json.loads(open(out).read().splitlines()[0])
        self.assertIsNotNone(row['plan_number'])
        self.assertEqual(row['plan_key'], self.recs[self.ids[0]]['plans'][row['plan_number'] - 1]['key'])  # the writer records what the checker needs
        self.assertEqual(row['plan_list_sha256'], formal.plan_list_sha256(self.recs[self.ids[0]]))
        for bad in ('1,1', 'a', ''):
            with self.assertRaises(SystemExit):
                self.cli(argv(path, out) + ['--seeds', bad])

    def test_the_frozen_executables_and_sources_are_enforced_unless_an_experiment_says_otherwise(self):
        d, rf, qf, ef = self.files(self.good_rows())
        argv = [a for a in self.argv(rf, qf, ef) if a != '--allow-other-binaries']
        real = dict(judge.frozen_identity())
        wrong = {**real, 'plans_binary_sha256': '0' * 64}
        with mock.patch.object(judge, 'frozen_identity', return_value=wrong):
            with self.assertRaises(SystemExit) as cm:
                self.cli(argv)
        self.assertIn('not the frozen executable', str(cm.exception))
        right = {**real, 'plans_binary_sha256': judge.file_sha256(judge.PLANS_BIN), 'baseline': {**real['baseline'], 'binary_sha256': '1' * 64}}
        import freeze_identity
        with mock.patch.object(judge, 'frozen_identity', return_value=right), mock.patch.object(freeze_identity, 'check', return_value=[]):
            code, out, err = self.cli(argv)
        self.assertEqual(code, 2)  # the km3 rows carry another baseline identity (the stand-in executable): every one is a problem
        self.assertIn('baseline_binary', err)
        # the code or prompt differing from the freeze (here: a fingerprint that is not the recorded one) stops the run before any row is read
        with mock.patch.object(judge, 'frozen_identity', return_value={**right, 'fingerprint': '0' * 64}):
            with self.assertRaises(SystemExit) as cm:
                self.cli(argv)
        self.assertIn('not the frozen ones', str(cm.exception))
        self.assertIn('prompt fingerprint differs', str(cm.exception))

    def test_score_is_marked_unchecked_and_refuses_an_empty_or_unreadable_file(self):
        rows = self.good_rows()
        self.km3(rows, 1).update(plan_number=None, match_error='ambiguous: two targets')
        d, rf, qf, ef = self.files(rows)
        argv = ['score', '--positions', self.positions_path, '--decks', DECKS, '--results', rf]
        code, out, err = self.cli(argv)
        self.assertEqual(code, 2, (out, err))
        self.assertIn('score FAILS', err)
        self.assertIn('UNCHECKED development figure', err)
        code, out, err = self.cli(argv + ['--lenient'])
        self.assertEqual(code, 0)
        self.assertIn('could not be scored', err)
        empty = os.path.join(d, 'empty.jsonl')
        open(empty, 'w').close()
        with self.assertRaises(SystemExit):
            self.cli(['score', '--positions', self.positions_path, '--decks', DECKS, '--results', empty])

    def test_a_run_with_no_experiment_switch_is_the_formal_result(self):
        import freeze_identity
        rows = self.good_rows()
        km3_sha = [r for r in rows if r['bot'] == 'km3'][0]['pg_pos_sha256']
        real = dict(judge.frozen_identity())
        ident = {**real, 'plans_binary_sha256': judge.file_sha256(judge.PLANS_BIN), 'baseline': {**real['baseline'], 'binary_sha256': km3_sha}}
        d, rf, qf, ef = self.files(rows)
        out = os.path.join(d, 'rep.json')
        argv = [a for a in self.argv(rf, qf, ef, extra=['--out', out]) if a != '--allow-other-binaries']
        with mock.patch.object(judge, 'frozen_identity', return_value=ident), mock.patch.object(freeze_identity, 'check', return_value=[]):
            code, o, err = self.cli(argv)  # the default 20,000 resamples and the 10-game minimum
        self.assertEqual(code, 0, err)
        rep = json.load(open(out))
        self.assertIs(rep['formal'], True)
        self.assertEqual(rep['run']['experiment_switches'], [])
        self.assertEqual(rep['analysis']['method']['resamples'], analysis.RESAMPLES)
        self.assertIn('FORMAL RESULT', o)
        self.assertNotIn('EXPERIMENT', err + o)

    def test_an_internal_error_or_an_early_exit_never_leaves_an_older_result_in_place(self):
        d, rf, qf, ef = self.files(self.good_rows())
        out = os.path.join(d, 'rep.json')
        with open(out, 'w') as f:
            json.dump({'status': 'complete', 'old': True}, f)
        with mock.patch.object(judge, '_run_compare', side_effect=RuntimeError('boom')):
            code, o, err = self.cli(self.argv(rf, qf, ef, extra=['--out', out]))
        self.assertEqual(code, 1)
        self.assertIn('boom', err)
        rep = json.load(open(out))
        self.assertEqual((rep['status'], rep['problems'][0]['kind']), ('failed', 'internal_error'))
        with open(out, 'w') as f:
            json.dump({'status': 'complete', 'old': True}, f)
        real = dict(judge.frozen_identity())
        with mock.patch.object(judge, 'frozen_identity', return_value={**real, 'plans_binary_sha256': '0' * 64}):
            with self.assertRaises(SystemExit):
                self.cli([a for a in self.argv(rf, qf, ef, extra=['--out', out]) if a != '--allow-other-binaries'])
        self.assertEqual(json.load(open(out))['status'], 'did_not_finish')  # replaced at the start: a run that died is never mistaken for the earlier result

    def test_the_games_of_the_eligibility_file_must_group_the_points_like_the_positions_file(self):
        games = {c['id']: c['game'] for c in self.positions.values()}
        games['BLW-01'] = games['BLW-00']  # the eligibility file calls two points one game; the positions file keeps them apart
        d, rf, qf, ef = self.files(self.good_rows(), elig={'primary_ids': self.primary, 'full_scope_ids': [], 'games': games})
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('game_conflict', err)
        renamed = {pid: g.replace('game-', 'G') for pid, g in {c['id']: c['game'] for c in self.positions.values()}.items()}  # other names, same grouping: fine
        d, rf, qf, ef = self.files(self.good_rows(), elig={'primary_ids': self.primary, 'full_scope_ids': [], 'games': renamed})
        code, out, err = self.cli(self.argv(rf, qf, ef, extra=['--resamples', '200']))
        self.assertEqual(code, 0, err)

    def test_a_row_that_repeats_a_json_key_is_a_problem(self):
        d, rf, qf, ef = self.files(self.good_rows(), raw_lines='{"position": "BLW-00", "position": "BLW-01"}\n')
        code, out, err = self.cli(self.argv(rf, qf, ef))
        self.assertEqual(code, 2)
        self.assertIn('duplicate key', err)

    def test_a_cut_reply_with_a_plan_line_is_not_a_choice(self):
        pid = self.ids[0]
        shown = {p['n']: k for k, p in judge.render_prompt(self.positions[pid], self.recs[pid], judge.FROZEN['order'], DECKS)[2].items()}
        reply = (f"PLAN: {shown[self.blow[0]['n']]}\nREASON: x", {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'max_tokens', 'content_types': ['text']})
        with mock.patch.object(judge, 'call_claude', return_value=reply):
            r, _, _ = judge.judge_one(pid, self.positions, self.recs, judge.FROZEN['order'], True, judge.MODEL, decks_dir=DECKS)
        self.assertIsNone(r['plan_number'])
        self.assertIn('cut at max_tokens', r['parse_error'])

    def test_the_preflight_command_names_the_positions_whose_labels_do_not_name_their_plans(self):
        code, out, err = self.cli(['preflight', '--positions', self.positions_path, '--decks', DECKS, '--ids', *self.ids[:3]])
        self.assertEqual(code, 0, err)
        self.assertIn('0 of 3 position(s)', out)


if __name__ == '__main__':
    unittest.main()
