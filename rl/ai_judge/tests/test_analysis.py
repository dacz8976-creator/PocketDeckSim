#!/usr/bin/env python3
"""The game-clustered paired analysis (analysis.py): pure Python, synthetic data only.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests
"""
import os, random, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import analysis  # noqa: E402

RES = 3000  # resamples in the tests (the formal default is 20,000)


def make_rows(spec):
    """spec: {game: [ {'judge': [agree per repeat], 'km3': [agree per seed]}, ... one dict per decision ]} -> (report rows, {position: game})."""
    rows, games = [], {}
    for g, decisions in spec.items():
        for k, d in enumerate(decisions):
            pid = f'{g}-d{k}'
            games[pid] = g
            for bot, agrees in d.items():
                for run, a in enumerate(agrees, start=(0 if bot == 'judge' else 1)):
                    rows.append({'position': pid, 'game': g, 'bot': bot, 'run': run, 'state': 'ok', 'plan_number': 1 if a else 2, 'accepted': ['r'] if a else [], 'agrees': bool(a)})
    return rows, games


def elig(spec, excluded=()):
    return {'eligible_games': [g for g in spec if g not in dict(excluded)], 'excluded_games': [{'game': g, 'reason': r} for g, r in excluded]}


def analyse(spec, judge_repeats=1, excluded=(), **kw):
    rows, games = make_rows(spec)
    return analysis.analyse(rows, games, elig(spec, excluded), ['km3', 'judge'], judge_repeats, resamples=kw.pop('resamples', RES), **kw)


def games_of(n, per_game, judge, km3):
    """n games, `per_game` decisions each; judge(g, k) / km3(g, k) -> list of agreement flags (repeats / seeds)."""
    return {f'g{g:02d}': [{'judge': judge(g, k), 'km3': km3(g, k)} for k in range(per_game)] for g in range(n)}


class Estimates(unittest.TestCase):
    def test_every_decision_weighs_the_same_and_the_estimate_is_the_plain_ratio(self):
        # game a has 1 decision (agrees), game b has 3 (none agree): the rate is 1/4, not the mean of the game means (0.5)
        spec = {'a': [{'judge': [1], 'km3': [0]}], 'b': [{'judge': [0], 'km3': [0]}] * 3}
        a = analyse(spec, min_games=1)
        self.assertAlmostEqual(a['rates']['judge']['estimate'], 0.25, places=5)
        self.assertAlmostEqual(a['contrasts'][0]['estimate'], 0.25, places=5)
        self.assertEqual(a['population']['decisions_per_game'], {'a': 1, 'b': 3})

    def test_a_unanimous_advantage_is_a_direction_and_says_why(self):
        a = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0]))
        c = a['contrasts'][0]
        self.assertEqual((c['estimate'], c['ci_low'], c['ci_high']), (1.0, 1.0, 1.0))
        self.assertEqual((c['verdict'], c['sign_flip'], c['sign_flip_p']), ('judge higher', 'exact', round(2 / 4096, 6)))
        self.assertIn('every game gave the same difference', c['reason'])
        self.assertEqual(c['discordant'], {'both': 0, 'judge_only': 24, 'km3_only': 0, 'neither': 0})

    def test_no_difference_is_inconclusive(self):
        a = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [1]))
        c = a['contrasts'][0]
        self.assertEqual((c['estimate'], c['verdict']), (0.0, 'inconclusive'))
        self.assertIn('includes 0', c['reason'])

    def test_an_interval_that_includes_zero_is_inconclusive_even_when_one_bot_leads(self):
        # judge better in 7 games, km3 in 5: the interval includes 0
        a = analyse(games_of(12, 2, lambda g, k: [1 if g < 7 else 0], lambda g, k: [0 if g < 7 else 1]))
        c = a['contrasts'][0]
        self.assertAlmostEqual(c['estimate'], 4 / 24, places=5)  # +1 on 14 decisions, -1 on 10
        self.assertLess(c['ci_low'], 0)
        self.assertGreater(c['ci_high'], 0)
        self.assertEqual(c['verdict'], 'inconclusive')

    def test_the_direction_works_both_ways(self):
        a = analyse(games_of(12, 2, lambda g, k: [0], lambda g, k: [1]))
        self.assertEqual(a['contrasts'][0]['verdict'], 'km3 higher')

    def test_too_few_games_is_inconclusive_whatever_the_effect(self):
        a = analyse(games_of(5, 4, lambda g, k: [1], lambda g, k: [0]), min_games=analysis.MIN_GAMES)
        c = a['contrasts'][0]
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIn('5 games < 10', c['reason'])

    def test_a_direction_needs_the_sign_flip_test_to_agree(self):
        # the verdict function on numbers where the interval excludes 0 but the randomisation test over games does not support it
        v, why = analysis.verdict('judge', 'km3', 0.2, 0.01, 0.4, 0.2, 12)
        self.assertEqual(v, 'inconclusive')
        self.assertIn('sign-flip', why)
        self.assertEqual(analysis.verdict('judge', 'km3', 0.2, 0.01, 0.4, 0.01, 12)[0], 'judge higher')
        self.assertEqual(analysis.verdict('judge', 'km3', -0.2, -0.4, -0.01, 0.01, 12)[0], 'km3 higher')


class Clustering(unittest.TestCase):
    def test_correlated_decisions_in_one_game_widen_the_interval(self):
        # 10 games x 4 decisions, all-or-nothing within a game: 6 of 10 games agree; a naive position-level bootstrap would treat the 40 decisions as independent
        spec = games_of(10, 4, lambda g, k: [1 if g < 6 else 0], lambda g, k: [0])
        a = analyse(spec, resamples=4000)
        c = a['rates']['judge']
        clustered = c['ci_high'] - c['ci_low']
        rows, games = make_rows(spec)
        rng = random.Random(1)
        vals = [1.0 if r['agrees'] else 0.0 for r in rows if r['bot'] == 'judge']
        naive = sorted(sum(vals[int(rng.random() * 40)] for _ in range(40)) / 40 for _ in range(4000))
        lo, hi = analysis.percentile_interval(naive)
        self.assertGreater(clustered, 1.6 * (hi - lo))

    def test_the_interval_matches_the_binomial_for_one_decision_per_game(self):
        # 20 games, 10 agree, one decision each: the game bootstrap is the ordinary bootstrap of a proportion; Binomial(20, 0.5)/20 has 2.5% / 97.5% points near 0.30 / 0.70
        a = analyse(games_of(20, 1, lambda g, k: [1 if g < 10 else 0], lambda g, k: [0]), resamples=6000)
        r = a['rates']['judge']
        self.assertAlmostEqual(r['estimate'], 0.5, places=5)
        self.assertTrue(0.25 <= r['ci_low'] <= 0.35, r)
        self.assertTrue(0.65 <= r['ci_high'] <= 0.75, r)

    def test_the_interval_function_takes_the_right_order_statistics(self):
        draws = [i / 1000 for i in range(1000)]
        self.assertEqual(analysis.percentile_interval(draws), (0.025, 0.974))  # floor(25) and ceil(975) - 1


class RepeatsAreASensitivityEstimateNotExtraSamples(unittest.TestCase):
    def test_the_primary_result_is_the_one_predefined_call(self):
        # repeat 0 is wrong everywhere, repeats 1 and 2 are right: the primary result is repeat 0, whatever the others did
        spec = games_of(12, 2, lambda g, k: [0, 1, 1], lambda g, k: [1])
        a = analyse(spec, judge_repeats=3)
        self.assertAlmostEqual(a['rates']['judge']['estimate'], 0.0, places=5)
        self.assertEqual(a['contrasts'][0]['verdict'], 'km3 higher')
        s = a['sensitivity']
        self.assertAlmostEqual(s['judge_rate']['estimate'], 2 / 3, places=5)
        self.assertEqual(a['population']['n_decisions'], 24)  # a decision counts once, not once per repeat
        # and the other way round: the better repeat is not picked up either
        spec = games_of(12, 2, lambda g, k: [1, 0, 0], lambda g, k: [0])
        b = analyse(spec, judge_repeats=3)
        self.assertAlmostEqual(b['rates']['judge']['estimate'], 1.0, places=5)
        self.assertAlmostEqual(b['sensitivity']['judge_rate']['estimate'], 1 / 3, places=5)

    def test_the_sensitivity_estimate_is_reported_apart_and_with_the_repeat_consistency(self):
        spec = games_of(12, 2, lambda g, k: [1, 1, 0] if k == 0 else [1, 1, 1], lambda g, k: [0])
        a = analyse(spec, judge_repeats=3)
        s = a['sensitivity']
        self.assertEqual([c['a'] for c in s['contrasts']], ['judge'])
        rc = s['repeat_consistency']
        self.assertEqual(rc['of_decisions'], 24)
        self.assertEqual(rc['decisions_with_the_same_plan_in_every_repeat'], 12)  # plan numbers: [1,1,2] differs, [1,1,1] is the same
        self.assertAlmostEqual(rc['pairwise_same_plan'], (12 * 1 + 12 * 3) / 72, places=5)
        self.assertIsNone(analyse(spec, judge_repeats=1)['sensitivity'])  # one call per decision: nothing to report apart

    def test_a_step_bots_value_is_the_mean_over_all_its_predefined_seeds(self):
        spec = games_of(12, 1, lambda g, k: [1], lambda g, k: [1, 0])  # km3: seed 1 agrees, seed 2 does not
        a = analyse(spec)
        self.assertAlmostEqual(a['rates']['km3']['estimate'], 0.5, places=5)
        self.assertNotIn('discordant', a['contrasts'][0])  # fractional values: no 2x2 table

    def test_a_missing_primary_call_is_an_error_not_a_silent_fallback(self):
        spec = games_of(12, 1, lambda g, k: [1], lambda g, k: [0])
        rows, games = make_rows(spec)
        rows = [r for r in rows if not (r['bot'] == 'judge' and r['position'] == 'g00-d0')]
        with self.assertRaises(ValueError):
            analysis.analyse(rows, games, elig(spec), ['km3', 'judge'], 1, resamples=50)
        # a judge decision that has repeats but no repeat 0 is refused too
        rows, games = make_rows(games_of(12, 1, lambda g, k: [1, 1], lambda g, k: [0]))
        rows = [r for r in rows if not (r['bot'] == 'judge' and r['run'] == 0 and r['position'] == 'g00-d0')]
        with self.assertRaises(ValueError):
            analysis.analyse(rows, games, elig(spec), ['km3', 'judge'], 2, resamples=50)


class Population(unittest.TestCase):
    def test_an_excluded_game_is_named_with_its_reason_and_changes_the_estimates(self):
        spec = games_of(12, 1, lambda g, k: [1 if g != 11 else 0], lambda g, k: [0])
        with_ex = analyse(spec, excluded=[('g11', 'synthetic exposure')])
        without = analyse(spec)
        self.assertEqual(with_ex['population']['excluded_games'], [{'game': 'g11', 'reason': 'synthetic exposure', 'n_decisions': 1}])
        self.assertEqual(with_ex['population']['n_games'], 11)
        self.assertAlmostEqual(with_ex['rates']['judge']['estimate'], 1.0, places=5)
        self.assertAlmostEqual(without['rates']['judge']['estimate'], 11 / 12, places=5)

    def test_the_eligibility_block_is_checked_for_shape(self):
        ok = {'eligible_games': ['a', 'b'], 'excluded_games': [{'game': 'c', 'reason': 'exposure'}]}
        self.assertEqual(analysis.check_eligibility(ok), [])
        for bad in (None, [], {}, {'eligible_games': []}, {'eligible_games': ['a', 'a']}, {'eligible_games': ['a'], 'excluded_games': [{'game': 'a', 'reason': 'x'}]},
                    {'eligible_games': ['a'], 'excluded_games': [{'game': 'c'}]}, {'eligible_games': ['a'], 'excluded_games': [{'game': 'c', 'reason': '  '}]},
                    {'eligible_games': ['a'], 'excluded_games': 'c'}, {'eligible_games': ['a'], 'excluded_games': [{'game': 'c', 'reason': 'x'}, {'game': 'c', 'reason': 'y'}]}):
            self.assertTrue(analysis.check_eligibility(bad), bad)

    def test_population_problems_name_each_failure_kind(self):
        ids = ['p1', 'p2', 'p3']
        games = {'p1': 'a', 'p2': 'b', 'p3': 'c'}
        elig_ok = {'eligible_games': ['a', 'b', 'c']}
        kinds = lambda **kw: sorted(p['kind'] for p in analysis.population_problems(**kw))
        self.assertEqual(kinds(ids=ids, games=games, eligibility=elig_ok, min_games=3), [])
        self.assertEqual(kinds(ids=ids, games=games, eligibility=None), ['no_eligibility'])
        self.assertEqual(kinds(ids=ids, games={**games, 'p3': None}, eligibility=elig_ok, min_games=1), ['eligible_game_uncovered', 'no_game'])
        self.assertEqual(kinds(ids=ids, games=games, eligibility={'eligible_games': ['a', 'b']}, min_games=1), ['game_not_listed'])
        self.assertEqual(kinds(ids=ids, games=games, eligibility={'eligible_games': ['a', 'b', 'c', 'd']}, min_games=1), ['eligible_game_uncovered'])
        self.assertEqual(kinds(ids=ids, games=games, eligibility=elig_ok, min_games=4), ['too_few_games'])


class Reproducibility(unittest.TestCase):
    def test_the_same_seed_gives_the_same_report_bit_for_bit(self):
        spec = games_of(12, 2, lambda g, k: [1 if (g + k) % 3 else 0], lambda g, k: [1 if (g * k) % 2 else 0])
        a, b = analyse(spec), analyse(spec)
        self.assertEqual(a, b)
        self.assertEqual(a['method']['seed'], analysis.SEED)
        self.assertEqual(analyse(spec, seed=7)['method']['seed'], 7)  # the seed used is part of the report

    def test_sign_flip_is_exact_for_small_samples_and_seeded_beyond(self):
        self.assertEqual(analysis.sign_flip_p([1.0, 1.0, 1.0]), (0.25, 'exact'))  # 2 of 8 sign patterns reach |sum| = 3
        self.assertEqual(analysis.sign_flip_p([1.0, -1.0]), (1.0, 'exact'))  # |sum| = 0: every pattern is at least as extreme
        self.assertEqual(analysis.sign_flip_p([0.0] * 5), (1.0, 'exact'))
        p, how = analysis.sign_flip_p([1.0] * 17)
        self.assertEqual(how, 'monte-carlo')
        self.assertLess(p, 0.001)
        self.assertEqual(analysis.sign_flip_p([1.0] * 17), (p, how))  # seeded


if __name__ == '__main__':
    unittest.main()
