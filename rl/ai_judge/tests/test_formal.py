#!/usr/bin/env python3
"""The formal paired comparison path (formal.py and `judge.py compare`): nothing unresolved is ever left out of a comparison, and no plan number is believed
without being checked against the current plan list.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests

The pure-Python classes need nothing built. The classes that run the CLI on the fixtures need the judge_plans binary (skipped without it).
Everything here uses synthetic rows and the small fixtures in tests/fixtures: no exam data, no API, no bot binaries.
"""
import contextlib, io, json, os, stat, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import formal  # noqa: E402
import judge  # noqa: E402

POS = os.path.join(HERE, 'fixtures', 'mini_positions.json')
DECKS = os.path.join(HERE, 'fixtures', 'decks')
HAVE_BIN = os.path.exists(judge.PLANS_BIN)


# ---------------------------------------------------------------------------------------------------------------------------------- pure logic
def mk_rec(pid, n=2):
    return {'id': pid, 'capped': False, 'start': {'position': pid}, 'plans': [{'n': i, 'key': f'{pid}-key{i}', 'labels': [f'{pid}-move{i}'], 'end': 'end_turn'} for i in range(1, n + 1)]}


RECS = {'P1': mk_rec('P1'), 'P2': mk_rec('P2')}
GAMES = {'P1': 'g1', 'P2': 'g2'}
ELIG = {'eligible_games': ['g1', 'g2'], 'excluded_games': []}
REFS = {'P1': [{'id': 'recorded', 'labels': ['m']}], 'P2': [{'id': 'recorded', 'labels': ['n']}]}
GOOD_ANSWERS = {('P1', 'recorded'): (1, None), ('P2', 'recorded'): (2, None)}


def valid(n, recs, pid):
    return isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= len(recs[pid]['plans'])


def step_row(pid, bot, seed, n, recs=RECS, **kw):
    r = {'position': pid, 'bot': bot, 'seed': seed, 'plan': ['x'], 'plan_full': [f'{pid}-full-{seed}'], 'plan_number': n, 'match_error': None,
         'plan_key': recs[pid]['plans'][n - 1]['key'] if valid(n, recs, pid) else None, 'plan_list_sha256': formal.plan_list_sha256(recs[pid])}
    r.update(kw)
    return r


def judge_row(pid, repeat, n, recs=RECS, **kw):
    r = {'position': pid, 'bot': 'judge', 'seed': None, 'repeat': repeat, 'plan': recs[pid]['plans'][n - 1]['labels'] if valid(n, recs, pid) else ['x'], 'plan_number': n,
         'shown_number': n, 'frozen': True, 'dry_run': False, 'capped': False, 'parse_error': None, 'prompt_sha256': f'prompt-{pid}',
         'plan_key': recs[pid]['plans'][n - 1]['key'] if valid(n, recs, pid) else None, 'plan_list_sha256': formal.plan_list_sha256(recs[pid])}
    r.update(kw)
    return r


def expect_identity(pid, row):
    """What the prompt re-rendered now would give: the hash, and the plan number behind every number printed in the prompt (here: the identity order)."""
    return {'prompt_sha256': f'prompt-{pid}', 'shown': {1: 1, 2: 2}}


def match_stub(answers, replays=None, claims=None):
    """A stand-in for judge.match_plans. Two-part tags (position|reference) are answered from `answers`; three-part tags (position|bot|run: a row's recorded
    full move list) replay to what the row claims unless `replays` says otherwise."""
    def match(items, recs):
        out = {}
        for _, tag, _ in items:
            parts = tag.split('|')
            out[tag] = answers[tuple(parts)] if len(parts) == 2 else (replays or {}).get(tag, (claims.get(tag), None))
        return out
    return match


def complete_rows():
    return [step_row('P1', 'km3', 1, 1), step_row('P1', 'km3', 2, 2), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2),
            judge_row('P1', 0, 1), judge_row('P2', 0, 1)]


def run(rows, refs=REFS, answers=GOOD_ANSWERS, replays=None, on_problem='fail', recs=RECS, require_frozen=True, elig=ELIG, games=GAMES, expect_judge=expect_identity,
        min_games=2, ids=('P1', 'P2'), bots=('km3', 'judge'), seeds=(1, 2), judge_repeats=1, baseline_sha256=None):
    claims = {f"{r['position']}|{r['bot']}|{r['seed']}": r['plan_number'] for r in rows if r['bot'] != 'judge'}
    return formal.compare(rows, list(ids), list(bots), list(seeds), judge_repeats, refs, recs, match_stub(answers, replays, claims), games, on_problem, require_frozen, baseline_sha256,
                          elig, expect_judge, None, min_games, 200)


def kinds(rep_or_exc):
    return sorted(p['kind'] for p in (rep_or_exc['problems'] if isinstance(rep_or_exc, dict) else rep_or_exc.problems))


class FormalPath(unittest.TestCase):
    def failed(self, rows, **kw):
        """Runs the formal path in the default 'fail' mode: it must raise BatchFailed(2); returns the exception."""
        with self.assertRaises(formal.BatchFailed) as cm:
            run(rows, **kw)
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(cm.exception.report['status'], 'failed')
        self.assertIsNone(cm.exception.report['agreement'])  # no numbers at all
        self.assertIsNone(cm.exception.report['analysis'])
        return cm.exception

    def test_a_clean_batch_is_complete_and_counts_every_row(self):
        rep = run(complete_rows())
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual((rep['n_expected_rows'], rep['n_present_rows'], rep['n_resolved_rows']), (6, 6, 6))
        self.assertEqual(rep['agreement'], {'km3': {'rows': 4, 'agree': 3}, 'judge': {'rows': 2, 'agree': 1}})
        self.assertEqual(formal.exit_code(rep), 0)
        self.assertEqual({r['game'] for r in rep['rows']}, {'g1', 'g2'})  # the game is kept for clustered uncertainty
        self.assertEqual(rep['analysis']['population']['n_games'], 2)

    def test_a_missing_reason_line_is_a_warning_not_an_error(self):
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, parse_warning='no REASON line (choice kept)'), judge_row('P2', 0, 1)]
        self.assertEqual(run(rows)['status'], 'complete')

    # --- unresolved rows (Astra's first finding)
    def test_an_ambiguous_row_fails_the_batch_instead_of_dropping_out_of_a_denominator(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, None, match_error='ambiguous: the move list fits 2 different listed plans [1, 2]: name the target')
        exc = self.failed(rows)
        self.assertEqual([p['kind'] for p in exc.problems], ['ambiguous'])

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
        self.assertIsNone(rep['agreement'])
        self.assertIsNone(rep['analysis'])
        self.assertEqual(formal.exit_code(rep), 3)
        self.assertEqual(sorted(p['kind'] for p in rep['problems']), ['ambiguous', 'missing'])

    def test_missing_duplicate_and_unexpected_rows_are_problems(self):
        rows = complete_rows()
        rows.append(step_row('P1', 'km3', 1, 1))  # the same key twice
        rows.append(step_row('P1', 'km3', 9, 1))  # a seed nobody asked for
        del rows[1]
        rep = run(rows, on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['duplicate', 'missing', 'unexpected'])
        self.assertEqual(rep['n_resolved_rows'], rep['n_expected_rows'] - 2)

    # --- the plan-number hole (Astra's second finding): a number is checked against the CURRENT plan list
    def test_a_plan_number_outside_the_plan_list_is_refused_not_scored(self):
        for bad in (999, 3, 0, -1):
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', 1, bad)
            exc = self.failed(rows)
            self.assertEqual([p['kind'] for p in exc.problems], ['bad_number'], bad)
            self.assertIn('from 1 to 2', exc.problems[0]['detail'])  # the size of the current two-plan list is named
        # the judge's row too
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 999), judge_row('P2', 0, 1)]
        self.assertIn('bad_number', kinds(self.failed(rows)))

    def test_a_number_that_is_not_a_whole_number_is_refused(self):
        # Python would happily compare True == 1 and 1.0 == 1: a row with such a number must never be scored as agreeing with plan 1
        for bad in (True, 1.0, '1', [1], {'n': 1}):
            rows = complete_rows()
            rows[0] = step_row('P1', 'km3', 1, bad, plan_key=RECS['P1']['plans'][0]['key'])
            exc = self.failed(rows)
            self.assertIn('bad_number', kinds(exc), repr(bad))

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
        exc = self.failed(rows)
        self.assertEqual(kinds(exc), ['list_mismatch'])
        rows = complete_rows()
        del rows[0]['plan_list_sha256']  # a row with no identity cannot be tied to anything
        self.assertEqual(kinds(self.failed(rows)), ['list_mismatch'])
        # a row made from a list that had a different plan 1 (same number, different plan): the identity hash differs
        other = {**RECS, 'P1': {**RECS['P1'], 'plans': [dict(RECS['P1']['plans'][0], key='another-key')] + RECS['P1']['plans'][1:]}}
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 1, recs=other)
        self.assertIn('list_mismatch', kinds(self.failed(rows)))
        self.assertIn('key_mismatch', kinds(self.failed(rows)))

    def test_a_row_whose_plan_key_is_not_the_keyed_plan_is_refused(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, 2, plan_key=RECS['P1']['plans'][0]['key'])  # claims plan 2 but carries plan 1's key
        self.assertIn('key_mismatch', kinds(self.failed(rows)))

    def test_a_step_bot_row_must_replay_to_its_numbered_plan(self):
        # the recorded moves reach plan 2 but the row says plan 1 (a hand-edited number, or a list that changed under it)
        exc = self.failed(complete_rows(), replays={'P1|km3|1': (2, None)})
        self.assertEqual(kinds(exc), ['replay_mismatch'])
        self.assertIn('plan 2', exc.problems[0]['detail'])
        # the moves cannot be followed any more / are ambiguous
        self.assertEqual(kinds(self.failed(complete_rows(), replays={'P1|km3|1': (None, 'no legal action labelled "x" at step 2')})), ['replay_mismatch'])
        self.assertEqual(kinds(self.failed(complete_rows(), replays={'P2|km3|2': (None, 'ambiguous: the move list fits 2 different listed plans [1, 2]')})), ['replay_mismatch'])
        # a row with no recorded move list cannot be replayed
        rows = complete_rows()
        del rows[0]['plan_full']
        self.assertEqual(kinds(self.failed(rows)), ['no_move_list'])

    def test_a_judge_row_must_match_the_prompt_it_was_answered_from(self):
        def with_judge(**kw):
            return complete_rows()[:-2] + [judge_row('P1', 0, 1, **kw), judge_row('P2', 0, 1)]
        # the answer's number maps to another plan in the prompt as re-rendered
        swapped = lambda pid, row: {'prompt_sha256': f'prompt-{pid}', 'shown': {1: 2, 2: 1}}
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(), expect_judge=swapped)))
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(shown_number=7))))
        self.assertIn('shown_mismatch', kinds(self.failed(with_judge(shown_number=None))))
        # the prompt hash is not the hash of the prompt rendered now
        self.assertEqual(kinds(self.failed(with_judge(prompt_sha256='other'))), ['prompt_mismatch'])
        # the recorded moves are not the labels of that plan
        self.assertEqual(kinds(self.failed(with_judge(plan=['something else']))), ['labels_mismatch'])
        # the prompt cannot be re-rendered at all
        broken = lambda pid, row: {'error': 'unknown order'}
        self.assertIn('prompt_mismatch', kinds(self.failed(with_judge(), expect_judge=broken)))
        # the judge can only be compared with an expectation of its prompt
        with self.assertRaises(ValueError):
            formal.compare(complete_rows(), ['P1', 'P2'], ['km3', 'judge'], [1, 2], 1, REFS, RECS, match_stub(GOOD_ANSWERS, claims={}), GAMES, 'fail', True, None, ELIG, None, None, 2, 50)

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
        self.assertIsNone(rep['agreement'])

    # --- requests that would double or empty a denominator
    def test_a_request_that_would_double_a_denominator_is_refused(self):
        for kw, word in [(dict(ids=('P1', 'P1', 'P2')), 'positions'), (dict(bots=('km3', 'km3', 'judge')), 'bots'), (dict(seeds=(1, 1, 2)), 'seeds')]:
            exc = self.failed(complete_rows(), **kw)
            self.assertEqual(kinds(exc), ['bad_request'])
            self.assertIn(word, exc.problems[0]['detail'])
        self.assertEqual(kinds(self.failed(complete_rows(), judge_repeats=0)), ['bad_request'])
        self.assertEqual(kinds(self.failed(complete_rows(), seeds=())), ['bad_request'])
        rep = run(complete_rows(), seeds=(), on_problem='inconclusive')
        self.assertEqual((rep['status'], formal.exit_code(rep)), ('inconclusive', 3))

    # --- earlier requirements
    def test_judge_rows_must_be_real_frozen_and_complete(self):
        for bad, kind in [(judge_row('P1', 0, 1, dry_run=True), 'dry_run'), (judge_row('P1', 0, 1, frozen=False), 'not_frozen'), (judge_row('P1', 0, 1, capped=True), 'capped'),
                          (judge_row('P1', 0, None, parse_error='no PLAN line'), 'unresolved')]:
            rows = complete_rows()[:-2] + [bad, judge_row('P2', 0, 1)]
            rep = run(rows, on_problem='inconclusive')
            self.assertIn(kind, [p['kind'] for p in rep['problems']], kind)
            self.assertEqual(rep['status'], 'inconclusive')
        # --allow-unfrozen is the only way an experiment row passes
        rows = complete_rows()[:-2] + [judge_row('P1', 0, 1, frozen=False), judge_row('P2', 0, 1)]
        self.assertEqual(run(rows, require_frozen=False)['status'], 'complete')

    def test_step_bot_rows_must_come_from_the_frozen_baseline_executable(self):
        rows = [dict(r, pg_pos_sha256='aaa') if r['bot'] == 'km3' else r for r in complete_rows()]
        self.assertEqual(run(rows, baseline_sha256='aaa')['status'], 'complete')
        rep = run(rows, baseline_sha256='bbb', on_problem='inconclusive')
        self.assertEqual(sorted({p['kind'] for p in rep['problems']}), ['baseline_binary'])
        self.assertEqual(len(rep['problems']), 4)  # every km3 row; the judge rows carry no baseline identity
        self.assertEqual(rep['status'], 'inconclusive')

    def test_a_capped_plan_list_stops_the_comparison(self):
        recs = {**RECS, 'P2': {**RECS['P2'], 'capped': True}}
        rows = [step_row(r['position'], r['bot'], r['seed'], r['plan_number'], recs=recs) if r['bot'] != 'judge' else judge_row(r['position'], 0, r['plan_number'], recs=recs) for r in complete_rows()]
        rep = run(rows, recs=recs, on_problem='inconclusive')
        self.assertIn('capped_list', kinds(rep))

    def test_an_ambiguous_or_unfollowable_reference_is_a_problem_too(self):
        amb = {('P1', 'recorded'): (None, 'ambiguous: the move list fits 2 different listed plans [1, 2]'), ('P2', 'recorded'): (2, None)}
        rep = run(complete_rows(), answers=amb, on_problem='inconclusive')
        self.assertEqual(kinds(rep), ['reference_ambiguous'])
        self.assertIsNone(rep['agreement'])
        bad = {('P1', 'recorded'): (1, None), ('P2', 'recorded'): (None, 'no legal action labelled "Play:Mesagoza"')}
        self.assertEqual(kinds(run(complete_rows(), answers=bad, on_problem='inconclusive')), ['reference_unresolved'])
        rep = run(complete_rows(), refs={'P1': REFS['P1']}, on_problem='inconclusive')
        self.assertIn('reference_missing', kinds(rep))

    def test_references_must_cover_the_batch_exactly_and_be_well_formed(self):
        extra = {**REFS, 'P3': [{'id': 'recorded', 'labels': ['q']}]}  # a position that is not in this batch
        self.assertEqual(kinds(run(complete_rows(), refs=extra, on_problem='inconclusive')), ['reference_unused'])
        for bad in ({'id': 'r'}, {'labels': ['m']}, {'id': 'r', 'labels': []}, {'id': 'r', 'labels': [1]}, 'm', {'id': 5, 'labels': ['m']}):
            refs = {**REFS, 'P1': [bad]}
            self.assertEqual(kinds(run(complete_rows(), refs=refs, on_problem='inconclusive')), ['reference_malformed'], bad)
        twice = {**REFS, 'P1': [{'id': 'r', 'labels': ['m']}, {'id': 'r', 'labels': ['m2']}]}
        self.assertEqual(kinds(run(complete_rows(), refs=twice, on_problem='inconclusive')), ['reference_malformed'])

    def test_a_row_agrees_when_its_plan_is_any_accepted_move(self):
        refs = {'P1': [{'id': 'recorded', 'labels': ['m']}, {'id': 'alternative', 'labels': ['m2']}], 'P2': REFS['P2']}
        answers = {('P1', 'recorded'): (1, None), ('P1', 'alternative'): (2, None), ('P2', 'recorded'): (2, None)}
        rep = run(complete_rows(), refs=refs, answers=answers)
        p1 = [r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'km3']
        self.assertEqual([(r['plan_number'], r['accepted'], r['agrees']) for r in p1], [(1, ['recorded'], True), (2, ['alternative'], True)])

    # --- the population
    def test_the_comparison_needs_the_games_it_is_over(self):
        self.assertEqual(kinds(self.failed(complete_rows(), elig=None)), ['no_eligibility'])
        self.assertEqual(kinds(self.failed(complete_rows(), elig={'eligible_games': ['g1']})), ['game_not_listed'])  # g2 is neither eligible nor excluded
        self.assertEqual(kinds(self.failed(complete_rows(), elig={'eligible_games': ['g1', 'g2', 'g3']})), ['eligible_game_uncovered'])
        self.assertEqual(kinds(self.failed(complete_rows(), games={'P1': 'g1', 'P2': None})), ['eligible_game_uncovered', 'no_game'])  # P2 sits in no cluster, so g2 is empty
        self.assertEqual(kinds(self.failed(complete_rows(), min_games=3)), ['too_few_games'])
        for bad in ({'eligible_games': []}, {'eligible_games': ['g1', 'g2'], 'excluded_games': [{'game': 'g1', 'reason': 'x'}]},
                    {'eligible_games': ['g1', 'g2'], 'excluded_games': [{'game': 'g3'}]}, {'eligible_games': 'g1'}):
            self.assertEqual(kinds(self.failed(complete_rows(), elig=bad))[0], 'eligibility_malformed', bad)

    def test_an_excluded_game_leaves_the_primary_comparison_but_not_the_account(self):
        elig = {'eligible_games': ['g1'], 'excluded_games': [{'game': 'g2', 'reason': 'synthetic exposure'}]}
        rep = run(complete_rows(), elig=elig, min_games=1)
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual(rep['agreement']['km3']['rows'], 4)  # the row account still covers every expected row
        pop = rep['analysis']['population']
        self.assertEqual((pop['eligible_games'], pop['n_decisions']), (['g1'], 1))
        self.assertEqual(pop['excluded_games'], [{'game': 'g2', 'reason': 'synthetic exposure', 'n_decisions': 1}])

    def test_a_references_file_without_the_envelope_has_no_eligibility(self):
        d = tempfile.mkdtemp()
        flat, env = os.path.join(d, 'flat.json'), os.path.join(d, 'env.json')
        with open(flat, 'w') as f:
            json.dump(REFS, f)
        with open(env, 'w') as f:
            json.dump({'schema': formal.REFERENCES_SCHEMA, 'references': REFS, **ELIG}, f)
        self.assertEqual(formal.load_references(flat), (REFS, None))
        self.assertEqual(formal.load_references(env), (REFS, ELIG))


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
    row writers (judge_one, run_pg_pos with a stand-in executable), so the writers and the checker are tested against each other."""

    N = 12
    EXPOSED = 'game-11'

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
        json.dump(clones, open(cls.positions_path, 'w'))
        cls.ids = [c['id'] for c in clones]
        cls.positions = judge.load_positions(cls.positions_path)
        cls.recs = judge.list_plans(cls.ids, cls.positions_path, DECKS)
        plans = cls.recs[cls.ids[0]]['plans']
        # the two plans "play Field Blower on target A / on target B, then end the turn"
        cls.blow = [p for p in plans if p['end'] == 'end_turn' and len(p['labels']) == 3 and p['labels'][0] == 'Play:Field Blower']
        assert len(cls.blow) == 2, [p['labels'] for p in plans]
        cls.judge_rows_ok = cls.make_judge_rows(lambda i: cls.blow[1 if i in (2, 5, 8) else 0]['n'])
        cls.km3_rows_ok = cls.make_step_rows('km3', lambda i: cls.blow[0 if i in (0, 1) else 1]['labels'])

    @classmethod
    def make_judge_rows(cls, choose):
        rows = []
        for i, pid in enumerate(cls.ids):
            n = choose(i)
            shown = {p['n']: k for k, p in judge.render_prompt(cls.positions[pid], cls.recs[pid], judge.FROZEN['order'], DECKS)[2].items()}
            reply = (f'PLAN: {shown[n]}\nREASON: x', {'input_tokens': 1, 'output_tokens': 1}, 0.1, judge.MODEL, {'stop_reason': 'end_turn', 'content_types': ['text']})
            with mock.patch.object(judge, 'call_claude', return_value=reply):
                r, _, _ = judge.judge_one(pid, cls.positions, cls.recs, judge.FROZEN['order'], True, judge.MODEL, decks_dir=DECKS)
            r['repeat'], r['tag'] = 0, None
            rows.append(json.loads(json.dumps(r)))
        return rows

    @classmethod
    def make_step_rows(cls, bot, choose_labels):
        d = tempfile.mkdtemp()
        plan_file, path = os.path.join(d, 'plans.json'), os.path.join(d, 'fake_pg_pos')
        json.dump({pid: choose_labels(i) for i, pid in enumerate(cls.ids)}, open(plan_file, 'w'))
        with open(path, 'w') as f:
            f.write(FAKE_PG_POS % plan_file)
        os.chmod(path, 0o755)
        return json.loads(json.dumps(judge.run_pg_pos(bot, cls.ids, [1], cls.recs, cls.positions_path, DECKS, bin_path=path)))

    def cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = judge.main(argv)
        return code, out.getvalue(), err.getvalue()

    def files(self, rows, eligible=None, excluded=None, envelope=True, refs=None):
        d = tempfile.mkdtemp()
        rf, qf = os.path.join(d, 'rows.jsonl'), os.path.join(d, 'refs.json')
        with open(rf, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in rows) + '\n')
        refs = refs if refs is not None else {pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in self.ids}
        games = [f'game-{i:02d}' for i in range(self.N)]
        eligible = eligible if eligible is not None else [g for g in games if g != self.EXPOSED]
        excluded = excluded if excluded is not None else [{'game': self.EXPOSED, 'reason': 'developer exposure to one answer-key example (synthetic)'}]
        with open(qf, 'w') as f:
            json.dump({'schema': formal.REFERENCES_SCHEMA, 'references': refs, 'eligible_games': eligible, 'excluded_games': excluded} if envelope else refs, f)
        return d, rf, qf

    def argv(self, rf, qf, ids=None, extra=()):
        return ['compare', '--positions', self.positions_path, '--decks', DECKS, '--ids', *(ids or self.ids), '--results', rf, '--bots', 'km3,judge', '--seeds', '1',
                '--references', qf, '--allow-other-binaries', *extra]  # the fixtures' rows were not made by the frozen executables

    def good_rows(self):
        return [dict(r) for r in self.km3_rows_ok + self.judge_rows_ok]

    # --- the complete batch
    def test_a_complete_batch_passes_with_exit_code_0_and_the_clustered_analysis(self):
        d, rf, qf = self.files(self.good_rows())
        code, out, err = self.cli(self.argv(rf, qf, extra=['--out', os.path.join(self.tmp, 'rep_ok.json'), '--resamples', '2000']))
        self.assertEqual(code, 0, err)
        rep = json.load(open(os.path.join(self.tmp, 'rep_ok.json')))
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual(rep['agreement'], {'km3': {'rows': 12, 'agree': 2}, 'judge': {'rows': 12, 'agree': 9}})  # every row accounted for, the exposed game included
        an = rep['analysis']
        self.assertEqual((an['population']['n_games'], an['population']['n_decisions']), (11, 11))
        self.assertEqual(an['population']['excluded_games'][0]['game'], self.EXPOSED)
        self.assertAlmostEqual(an['rates']['judge']['estimate'], 8 / 11, places=5)  # the exposed game is not in the primary comparison
        self.assertAlmostEqual(an['rates']['km3']['estimate'], 2 / 11, places=5)
        c = an['contrasts'][0]
        self.assertAlmostEqual(c['estimate'], 6 / 11, places=5)
        self.assertEqual((c['a'], c['b'], c['verdict']), ('judge', 'km3', 'judge higher'))
        self.assertEqual(c['sign_flip'], 'exact')
        self.assertIn('judge higher', out)

    # --- the plan-number hole, on the real writers' rows
    def run_bad(self, mutate, expect_kind, **extra):
        rows = self.good_rows()
        mutate(rows)
        d, rf, qf = self.files(rows)
        code, out, err = self.cli(self.argv(rf, qf, extra=['--out', os.path.join(d, 'rep.json'), '--resamples', '200', *extra]))
        self.assertEqual(code, 2, err)
        self.assertIn('COMPARISON FAILED', err)
        self.assertIn(expect_kind, err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual((rep['status'], rep['agreement'], rep['analysis']), ('failed', None, None))
        self.assertEqual(len(rep['rows']), 24)  # every expected row is still listed
        code, out, err = self.cli(self.argv(rf, qf, extra=['--on-problem', 'inconclusive', '--resamples', '200', *extra]))
        self.assertEqual(code, 3, err)
        return rows

    def km3(self, rows, i):
        return [r for r in rows if r['bot'] == 'km3'][i]

    def jdg(self, rows, i):
        return [r for r in rows if r['bot'] == 'judge'][i]

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
        # the row says plan b, with b's key, but its recorded moves are plan a's: replay disagrees (the identity fields alone would pass)
        def retarget(rows):
            r = self.km3(rows, 0)
            assert r['plan_number'] == a
            r.update(plan_number=b, plan_key=self.blow[1]['key'])
        self.run_bad(retarget, 'replay_mismatch')
        # a changed number with the old key is caught by the key check
        self.run_bad(lambda rows: self.km3(rows, 0).update(plan_number=b), 'key_mismatch')

    def test_a_row_made_from_another_plan_list_fails_the_command(self):
        self.run_bad(lambda rows: self.km3(rows, 1).update(plan_list_sha256='f' * 64), 'list_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 1).update(plan_list_sha256=None), 'list_mismatch')

    def test_a_judge_row_not_tied_to_its_prompt_fails_the_command(self):
        def shift_shown(rows):
            r = self.jdg(rows, 0)
            r['shown_number'] = r['shown_number'] % self.recs[self.ids[0]]['n_plans'] + 1
        self.run_bad(shift_shown, 'shown_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(prompt_sha256='0' * 16), 'prompt_mismatch')
        self.run_bad(lambda rows: self.jdg(rows, 0).update(plan=['Play:Field Blower']), 'labels_mismatch')

    # --- the population, on the command line
    def test_the_references_must_carry_the_eligibility_list(self):
        d, rf, qf = self.files(self.good_rows(), envelope=False)
        code, out, err = self.cli(self.argv(rf, qf))
        self.assertEqual(code, 2)
        self.assertIn('no_eligibility', err)

    def test_a_game_that_is_neither_eligible_nor_excluded_fails_the_command(self):
        d, rf, qf = self.files(self.good_rows(), excluded=[])  # the exposed game dropped from the exclusion list without being made eligible
        code, out, err = self.cli(self.argv(rf, qf))
        self.assertEqual(code, 2)
        self.assertIn('game_not_listed', err)

    def test_too_few_games_fails_the_command_unless_the_minimum_is_lowered_on_purpose(self):
        ids = self.ids[:5]
        games = [f'game-{i:02d}' for i in range(5)]
        d, rf, qf = self.files([r for r in self.good_rows() if r['position'] in ids], eligible=games, excluded=[],
                               refs={pid: [{'id': 'recorded', 'labels': self.blow[0]['labels']}] for pid in ids})
        code, out, err = self.cli(self.argv(rf, qf, ids=ids))
        self.assertEqual(code, 2)
        self.assertIn('too_few_games', err)
        code, out, err = self.cli(self.argv(rf, qf, ids=ids, extra=['--min-games', '5', '--resamples', '200']))
        self.assertEqual(code, 0, err)

    # --- earlier requirements, on the command line
    def test_an_ambiguous_reference_name_fails_the_command(self):
        # the bare recorded name 'DiscardToolFromPokemon' fits both targets: it must not be resolved to the first one
        refs = {pid: [{'id': 'recorded', 'labels': ['Play:Field Blower', 'DiscardToolFromPokemon']}] for pid in self.ids}
        d, rf, qf = self.files(self.good_rows(), refs=refs)
        code, out, err = self.cli(self.argv(rf, qf, extra=['--out', os.path.join(d, 'rep.json')]))
        self.assertEqual(code, 2)
        self.assertIn('reference_ambiguous', err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual((rep['status'], rep['agreement'], len(rep['rows'])), ('failed', None, 24))
        code, out, err = self.cli(self.argv(rf, qf, extra=['--on-problem', 'inconclusive', '--out', os.path.join(d, 'rep2.json')]))
        self.assertEqual(code, 3)
        rep = json.load(open(os.path.join(d, 'rep2.json')))
        self.assertEqual((rep['status'], rep['agreement'], len(rep['rows'])), ('inconclusive', None, 24))

    def test_a_row_with_no_listed_plan_fails_the_command(self):
        def drop(rows):
            r = self.km3(rows, 1)
            r.update(plan_number=None, plan_key=None, match_error='ambiguous: the move list fits 2 different listed plans [3, 4]')
        self.run_bad(drop, 'ambiguous')

    def test_the_run_command_fails_when_a_row_cannot_be_mapped_to_one_plan(self):
        full = sorted({l for p in self.recs[self.ids[0]]['plans'] for l in p['labels'] if l.startswith('DiscardToolFromPokemon#')})

        def argv(path, out):
            return ['run', '--bot', 'km3', '--positions', self.positions_path, '--decks', DECKS, '--ids', self.ids[0], '--seeds', '1', '--pg-pos-bin', path, '--out', out]

        def fake(plan):
            d = tempfile.mkdtemp()
            pf, path = os.path.join(d, 'plans.json'), os.path.join(d, 'fake_pg_pos')
            json.dump({self.ids[0]: plan}, open(pf, 'w'))
            open(path, 'w').write(FAKE_PG_POS % pf)
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

    def test_the_frozen_plan_lister_executable_is_enforced_unless_an_experiment_says_otherwise(self):
        d, rf, qf = self.files(self.good_rows())
        argv = [a for a in self.argv(rf, qf) if a != '--allow-other-binaries']
        wrong = {'tag': 'judge-prompt-frozen-X', 'plans_binary_sha256': '0' * 64, 'baseline': {'binary_sha256': '1' * 64}}
        with mock.patch.object(judge, 'frozen_identity', return_value=wrong):
            with self.assertRaises(SystemExit) as cm:
                self.cli(argv)
        self.assertIn('not the frozen executable', str(cm.exception))
        right = {'tag': 'judge-prompt-frozen-X', 'plans_binary_sha256': judge.file_sha256(judge.PLANS_BIN), 'baseline': {'binary_sha256': '1' * 64}}
        with mock.patch.object(judge, 'frozen_identity', return_value=right):
            code, out, err = self.cli(argv)
        self.assertEqual(code, 2)  # the km3 rows carry another baseline identity (the stand-in executable): every one is a problem
        self.assertIn('baseline_binary', err)

    def test_score_fails_on_an_unmapped_row_instead_of_dropping_it(self):
        rows = self.good_rows()
        self.km3(rows, 1).update(plan_number=None, match_error='ambiguous: two targets')
        d, rf, qf = self.files(rows)
        argv = ['score', '--positions', self.positions_path, '--decks', DECKS, '--results', rf]
        code, out, err = self.cli(argv)
        self.assertEqual(code, 2, (out, err))
        self.assertIn('score FAILS', err)
        code, out, err = self.cli(argv + ['--lenient'])
        self.assertEqual(code, 0)
        self.assertIn('could not be scored', err)


if __name__ == '__main__':
    unittest.main()
