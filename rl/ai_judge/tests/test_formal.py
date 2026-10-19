#!/usr/bin/env python3
"""The formal paired comparison path (formal.py and `judge.py compare`): nothing unresolved is ever left out of a comparison.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests

The pure-Python classes need nothing built. The classes that run the CLI on the fixtures need the judge_plans binary (skipped without it).
Everything here uses synthetic rows and the small fixtures in tests/fixtures: no exam data, no API, no bot binaries.
"""
import contextlib, io, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import formal  # noqa: E402
import judge  # noqa: E402

POS = os.path.join(HERE, 'fixtures', 'mini_positions.json')
DECKS = os.path.join(HERE, 'fixtures', 'decks')
HAVE_BIN = os.path.exists(judge.PLANS_BIN)


def step_row(pid, bot, seed, n, **kw):
    r = {'position': pid, 'bot': bot, 'seed': seed, 'plan': ['x'], 'plan_number': n, 'match_error': None}
    r.update(kw)
    return r


def judge_row(pid, repeat, n, **kw):
    r = {'position': pid, 'bot': 'judge', 'seed': None, 'repeat': repeat, 'plan': ['x'], 'plan_number': n, 'frozen': True, 'dry_run': False, 'capped': False, 'parse_error': None}
    r.update(kw)
    return r


RECS = {'P1': {'capped': False, 'plans': [{'n': 1, 'key': 'a'}, {'n': 2, 'key': 'b'}]}, 'P2': {'capped': False, 'plans': [{'n': 1, 'key': 'c'}, {'n': 2, 'key': 'd'}]}}
REFS = {'P1': [{'id': 'recorded', 'labels': ['m']}], 'P2': [{'id': 'recorded', 'labels': ['n']}]}


def match_stub(answers):
    """A stand-in for judge.match_plans: answers {(position, ref id): (plan number, error)}."""
    def match(items, recs):
        return {tag: answers[tuple(tag.split('|'))] for _, tag, _ in items}
    return match


GOOD = match_stub({('P1', 'recorded'): (1, None), ('P2', 'recorded'): (2, None)})


def complete_rows():
    return [step_row('P1', 'km3', 1, 1), step_row('P1', 'km3', 2, 2), step_row('P2', 'km3', 1, 2), step_row('P2', 'km3', 2, 2),
            judge_row('P1', 0, 1), judge_row('P2', 0, 1)]


def run(rows, refs=REFS, match=GOOD, on_problem='fail', recs=RECS, require_frozen=True):
    return formal.compare(rows, ['P1', 'P2'], ['km3', 'judge'], [1, 2], 1, refs, recs, match, {'P1': 'g1', 'P2': 'g2'}, on_problem, require_frozen)


class FormalPath(unittest.TestCase):
    def test_a_clean_batch_is_complete_and_counts_every_row(self):
        rep = run(complete_rows())
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual((rep['n_expected_rows'], rep['n_present_rows'], rep['n_resolved_rows']), (6, 6, 6))
        self.assertEqual(rep['agreement'], {'km3': {'rows': 4, 'agree': 3}, 'judge': {'rows': 2, 'agree': 1}})
        self.assertEqual(formal.exit_code(rep), 0)
        self.assertEqual({r['game'] for r in rep['rows']}, {'g1', 'g2'})  # the game is kept for clustered uncertainty later

    def test_an_ambiguous_row_fails_the_batch_instead_of_dropping_out_of_a_denominator(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, None, match_error='ambiguous: the move list fits 2 different listed plans [1, 2]: name the target')
        with self.assertRaises(formal.BatchFailed) as cm:
            run(rows)
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual([p['kind'] for p in cm.exception.problems], ['ambiguous'])
        self.assertEqual(cm.exception.report['status'], 'failed')
        self.assertIsNone(cm.exception.report['agreement'])  # no numbers at all

    def test_inconclusive_mode_accounts_for_every_expected_row_and_reports_no_numbers(self):
        rows = complete_rows()
        rows[0] = step_row('P1', 'km3', 1, None, match_error='ambiguous: two targets')
        del rows[3]  # a missing row as well
        rep = run(rows, on_problem='inconclusive')
        self.assertEqual(rep['status'], 'inconclusive')
        self.assertEqual(len(rep['rows']), rep['n_expected_rows'])  # nothing left out of the account
        self.assertEqual((rep['n_expected_rows'], rep['n_present_rows'], rep['n_resolved_rows']), (6, 5, 4))
        states = collections_counter([r['state'] for r in rep['rows']])
        self.assertEqual(states, {'ok': 4, 'unresolved': 1, 'missing': 1})
        self.assertIsNone(rep['agreement'])
        self.assertEqual(formal.exit_code(rep), 3)
        self.assertEqual(sorted(p['kind'] for p in rep['problems']), ['ambiguous', 'missing'])

    def test_missing_duplicate_and_unexpected_rows_are_problems(self):
        rows = complete_rows()
        rows.append(step_row('P1', 'km3', 1, 1))  # the same key twice
        rows.append(step_row('P1', 'km3', 9, 1))  # a seed nobody asked for
        del rows[1]
        rep = run(rows, on_problem='inconclusive')
        kinds = sorted(p['kind'] for p in rep['problems'])
        self.assertEqual(kinds, ['duplicate', 'missing', 'unexpected'])
        self.assertEqual(rep['n_resolved_rows'], rep['n_expected_rows'] - 2)

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

    def test_a_capped_plan_list_stops_the_comparison(self):
        recs = {**RECS, 'P2': {**RECS['P2'], 'capped': True}}
        rep = run(complete_rows(), recs=recs, on_problem='inconclusive')
        self.assertIn('capped_list', [p['kind'] for p in rep['problems']])

    def test_an_ambiguous_or_unfollowable_reference_is_a_problem_too(self):
        amb = match_stub({('P1', 'recorded'): (None, 'ambiguous: the move list fits 2 different listed plans [1, 2]'), ('P2', 'recorded'): (2, None)})
        rep = run(complete_rows(), match=amb, on_problem='inconclusive')
        self.assertEqual([p['kind'] for p in rep['problems']], ['reference_ambiguous'])
        self.assertIsNone(rep['agreement'])
        bad = match_stub({('P1', 'recorded'): (1, None), ('P2', 'recorded'): (None, 'no legal action labelled "Play:Mesagoza"')})
        rep = run(complete_rows(), match=bad, on_problem='inconclusive')
        self.assertEqual([p['kind'] for p in rep['problems']], ['reference_unresolved'])
        rep = run(complete_rows(), refs={'P1': REFS['P1']}, match=GOOD, on_problem='inconclusive')
        self.assertIn('reference_missing', [p['kind'] for p in rep['problems']])

    def test_a_row_agrees_when_its_plan_is_any_accepted_move(self):
        refs = {'P1': [{'id': 'recorded', 'labels': ['m']}, {'id': 'alternative', 'labels': ['m2']}], 'P2': REFS['P2']}
        match = match_stub({('P1', 'recorded'): (1, None), ('P1', 'alternative'): (2, None), ('P2', 'recorded'): (2, None)})
        rep = run(complete_rows(), refs=refs, match=match)
        p1 = [r for r in rep['rows'] if r['position'] == 'P1' and r['bot'] == 'km3']
        self.assertEqual([(r['plan_number'], r['accepted'], r['agrees']) for r in p1], [(1, ['recorded'], True), (2, ['alternative'], True)])


def collections_counter(xs):
    out = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


@unittest.skipUnless(HAVE_BIN, 'judge_plans is not built')
class CommandLinePath(unittest.TestCase):
    """The CLI itself (judge.py compare / score) on the fixtures: exit codes, report files, no silent drops."""

    def cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = judge.main(argv)
        return code, out.getvalue(), err.getvalue()

    def files(self, rows, refs):
        d = tempfile.mkdtemp()
        rf, qf = os.path.join(d, 'rows.jsonl'), os.path.join(d, 'refs.json')
        with open(rf, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in rows) + '\n')
        json.dump(refs, open(qf, 'w'))
        return d, rf, qf

    def plans(self, pid):
        return judge.list_plans([pid], POS, DECKS)[pid]

    def base_argv(self, rf, qf, extra=()):
        return ['compare', '--positions', POS, '--decks', DECKS, '--ids', 'MINI-BLOWER', '--results', rf, '--bots', 'km3,judge', '--seeds', '1,2', '--references', qf, *extra]

    def blower_rows(self):
        rec = self.plans('MINI-BLOWER')
        # the two plans "play Field Blower on target A / on target B, then end the turn" (the other plans add an Energy attach or an attack)
        blow = [p for p in rec['plans'] if p['end'] == 'end_turn' and len(p['labels']) == 3 and p['labels'][0] == 'Play:Field Blower']
        self.assertEqual(len(blow), 2, [p['labels'] for p in rec['plans']])
        rows = [step_row('MINI-BLOWER', 'km3', 1, blow[0]['n']), step_row('MINI-BLOWER', 'km3', 2, blow[1]['n']), judge_row('MINI-BLOWER', 0, blow[0]['n'])]
        full = sorted({l for p in blow for l in p['labels'] if l.startswith('DiscardToolFromPokemon')})
        return rows, full, blow

    def test_a_complete_batch_passes_with_exit_code_0_and_writes_a_report(self):
        rows, full, _ = self.blower_rows()
        d, rf, qf = self.files(rows, {'MINI-BLOWER': [{'id': 'recorded', 'labels': ['Play:Field Blower', full[0]]}, {'id': 'other', 'labels': ['Play:Field Blower', full[1]]}]})
        code, out, err = self.cli(self.base_argv(rf, qf, ['--out', os.path.join(d, 'rep.json')]))
        self.assertEqual(code, 0, err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual(rep['status'], 'complete')
        self.assertEqual(rep['agreement'], {'km3': {'rows': 2, 'agree': 2}, 'judge': {'rows': 1, 'agree': 1}})
        self.assertEqual([r['accepted'] for r in rep['rows'] if r['bot'] == 'km3'], [['recorded'], ['other']])

    def test_an_ambiguous_reference_name_fails_the_command(self):
        rows, full, _ = self.blower_rows()
        # the bare recorded name 'DiscardToolFromPokemon' fits both targets: it must not be resolved to the first one
        d, rf, qf = self.files(rows, {'MINI-BLOWER': [{'id': 'recorded', 'labels': ['Play:Field Blower', 'DiscardToolFromPokemon']}]})
        code, out, err = self.cli(self.base_argv(rf, qf, ['--out', os.path.join(d, 'rep.json')]))
        self.assertEqual(code, 2)
        self.assertIn('COMPARISON FAILED', err)
        self.assertIn('reference_ambiguous', err)
        rep = json.load(open(os.path.join(d, 'rep.json')))
        self.assertEqual(rep['status'], 'failed')
        self.assertIsNone(rep['agreement'])
        self.assertEqual(len(rep['rows']), 3)  # every expected row is still listed
        # inconclusive mode: exit code 3, same account, still no numbers
        code, out, err = self.cli(self.base_argv(rf, qf, ['--on-problem', 'inconclusive', '--out', os.path.join(d, 'rep2.json')]))
        self.assertEqual(code, 3)
        rep = json.load(open(os.path.join(d, 'rep2.json')))
        self.assertEqual((rep['status'], rep['agreement'], len(rep['rows'])), ('inconclusive', None, 3))

    def test_a_row_with_no_listed_plan_fails_the_command(self):
        rows, full, _ = self.blower_rows()
        rows[1] = step_row('MINI-BLOWER', 'km3', 2, None, match_error='ambiguous: the move list fits 2 different listed plans [3, 4]')
        d, rf, qf = self.files(rows, {'MINI-BLOWER': [{'id': 'recorded', 'labels': ['Play:Field Blower', full[0]]}]})
        code, out, err = self.cli(self.base_argv(rf, qf))
        self.assertEqual(code, 2)
        self.assertIn('ambiguous', err)

    def fake_pg_pos(self, plan):
        d = tempfile.mkdtemp()
        path = os.path.join(d, 'fake_pg_pos')
        row = {'kind': 'free', 'id': 'MINI-BLOWER', 'seed': 1, 'plan': plan, 'cut': 'end of turn'}
        with open(path, 'w') as f:
            f.write("#!/bin/bash\necho '" + json.dumps(row) + "'\n")
        os.chmod(path, 0o755)
        return d, path

    def test_the_run_command_fails_when_a_row_cannot_be_mapped_to_one_plan(self):
        full = sorted({l for p in self.plans('MINI-BLOWER')['plans'] for l in p['labels'] if l.startswith('DiscardToolFromPokemon#')})
        argv = lambda path, out: ['run', '--bot', 'km3', '--positions', POS, '--decks', DECKS, '--ids', 'MINI-BLOWER', '--seeds', '1', '--pg-pos-bin', path, '--out', out]
        d, path = self.fake_pg_pos(['Play:Field Blower', 'DiscardToolFromPokemon'])  # the bare name fits both targets
        out = os.path.join(d, 'rows.jsonl')
        code, _, err = self.cli(argv(path, out))
        self.assertEqual(code, 2)
        self.assertIn('could not be mapped to ONE listed plan', err)
        row = json.loads(open(out).read().splitlines()[0])  # the row is still written, so the failure is visible in the file
        self.assertIsNone(row['plan_number'])
        self.assertTrue(row['match_error'].startswith('ambiguous'))
        d, path = self.fake_pg_pos(['Play:Field Blower', full[0]])  # the full label names the target
        out = os.path.join(d, 'rows.jsonl')
        code, _, err = self.cli(argv(path, out))
        self.assertEqual(code, 0, err)
        self.assertIsNotNone(json.loads(open(out).read().splitlines()[0])['plan_number'])

    def test_score_fails_on_an_unmapped_row_instead_of_dropping_it(self):
        rows, full, _ = self.blower_rows()
        rows[1] = step_row('MINI-BLOWER', 'km3', 2, None, match_error='ambiguous: two targets')
        d, rf, qf = self.files(rows, {})
        argv = ['score', '--positions', POS, '--decks', DECKS, '--results', rf]
        code, out, err = self.cli(argv)
        # the recorded plan of MINI-BLOWER is the bare 'Play:Field Blower' (a chance-free plan with a pending choice): whatever the reference maps to,
        # the unmapped km3 row must make the command fail and be named
        self.assertEqual(code, 2, (out, err))
        self.assertIn('score FAILS', err)
        code, out, err = self.cli(argv + ['--lenient'])
        self.assertEqual(code, 0)
        self.assertIn('could not be scored', err)


if __name__ == '__main__':
    unittest.main()
