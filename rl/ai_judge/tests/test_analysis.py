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
    """spec: {game: [ decision, ... ]}, a decision = {'judge': [agree per repeat], 'km3': [agree per seed], 'full': {bot: [full-plan agree or None per run]} (optional)}.
    -> (report rows, eligibility file for ALL the points: every point primary, those with a 'full' entry also full-scope)."""
    rows, games, primary, full_ids = [], {}, [], []
    for g, decisions in spec.items():
        for k, d in enumerate(decisions):
            pid = f'{g}-d{k}'
            games[pid] = g
            primary.append(pid)
            if 'full' in d:
                full_ids.append(pid)
            for bot in ('judge', 'km3'):
                if bot not in d:
                    continue
                for i, a in enumerate(d[bot]):
                    fa = d['full'][bot][i] if 'full' in d else a
                    rows.append({'position': pid, 'game': g, 'bot': bot, 'run': i + (0 if bot == 'judge' else 1), 'state': 'ok', 'plan_number': 1 if a else 2,
                                 'accepted': ['r'] if a else [], 'agrees': bool(a), 'full_scope': pid in full_ids, 'full_agrees': fa})
    return rows, {'primary_ids': primary, 'full_scope_ids': full_ids, 'games': games}


def analyse(spec, judge_repeats=1, **kw):
    rows, elig = make_rows(spec)
    return analysis.analyse(rows, elig, ['km3', 'judge'], judge_repeats, resamples=kw.pop('resamples', RES), **kw)


def games_of(n, per_game, judge, km3, full=None):
    """n games, `per_game` decisions each; judge(g, k) / km3(g, k) -> list of agreement flags (repeats / seeds); full(g, k) -> {bot: [...]} or None."""
    out = {}
    for g in range(n):
        out[f'g{g:02d}'] = []
        for k in range(per_game):
            d = {'judge': judge(g, k), 'km3': km3(g, k)}
            if full is not None and full(g, k) is not None:
                d['full'] = full(g, k)
            out[f'g{g:02d}'].append(d)
    return out


def prefix(a, i=0):
    return a['prefix']['contrasts'][i]


class Estimates(unittest.TestCase):
    def test_every_decision_weighs_the_same_and_the_estimate_is_the_plain_ratio(self):
        # game a has 1 decision (agrees), game b has 3 (none agree): the rate is 1/4, not the mean of the game means (0.5)
        spec = {'a': [{'judge': [1], 'km3': [0]}], 'b': [{'judge': [0], 'km3': [0]}] * 3}
        a = analyse(spec, min_games=1)
        self.assertAlmostEqual(a['prefix']['rates']['judge']['estimate'], 0.25, places=5)
        self.assertAlmostEqual(prefix(a)['estimate'], 0.25, places=5)
        self.assertEqual(a['prefix']['population']['decisions_per_game'], {'a': 1, 'b': 3})

    def test_a_unanimous_advantage_is_a_direction_and_says_why(self):
        a = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0]))
        c = prefix(a)
        self.assertEqual((c['estimate'], c['ci_low'], c['ci_high']), (1.0, 1.0, 1.0))
        self.assertEqual((c['verdict'], c['sign_flip'], c['sign_flip_p']), ('judge higher', 'exact', round(2 / 4096, 6)))
        self.assertIn('every game gave the same difference', c['reason'])
        self.assertEqual(c['discordant'], {'both': 0, 'judge_only': 24, 'km3_only': 0, 'neither': 0})

    def test_the_same_difference_note_needs_every_game_to_agree_not_a_collapsed_interval(self):
        # games differ (differences 1,1,...,0): a collapsed interval (a single resample) must not say 'every game gave the same difference'
        a = analyse(games_of(12, 1, lambda g, k: [1 if g < 8 else 0], lambda g, k: [0]), resamples=1)
        self.assertNotIn('every game gave the same difference', prefix(a)['reason'])

    def test_no_difference_is_inconclusive(self):
        c = prefix(analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [1])))
        self.assertEqual((c['estimate'], c['verdict']), (0.0, 'inconclusive'))
        self.assertIn('includes 0', c['reason'])

    def test_an_interval_that_includes_zero_is_inconclusive_even_when_one_bot_leads(self):
        c = prefix(analyse(games_of(12, 2, lambda g, k: [1 if g < 7 else 0], lambda g, k: [0 if g < 7 else 1])))
        self.assertAlmostEqual(c['estimate'], 4 / 24, places=5)  # +1 on 14 decisions, -1 on 10
        self.assertLess(c['ci_low'], 0)
        self.assertGreater(c['ci_high'], 0)
        self.assertEqual(c['verdict'], 'inconclusive')

    def test_the_direction_works_both_ways(self):
        self.assertEqual(prefix(analyse(games_of(12, 2, lambda g, k: [0], lambda g, k: [1])))['verdict'], 'km3 higher')

    def test_too_few_games_is_inconclusive_whatever_the_effect_and_exactly_min_games_is_enough(self):
        c = prefix(analyse(games_of(5, 4, lambda g, k: [1], lambda g, k: [0])))
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIn('5 games < 10', c['reason'])
        self.assertEqual(prefix(analyse(games_of(10, 2, lambda g, k: [1], lambda g, k: [0])))['verdict'], 'judge higher')
        self.assertEqual(prefix(analyse(games_of(9, 2, lambda g, k: [1], lambda g, k: [0])))['verdict'], 'inconclusive')

    def test_a_direction_needs_the_sign_flip_test_to_agree(self):
        v, why = analysis.verdict('judge', 'km3', 0.2, 0.01, 0.4, 0.2, 12)
        self.assertEqual(v, 'inconclusive')
        self.assertIn('sign-flip', why)
        self.assertEqual(analysis.verdict('judge', 'km3', 0.2, 0.01, 0.4, 0.01, 12)[0], 'judge higher')
        self.assertEqual(analysis.verdict('judge', 'km3', -0.2, -0.4, -0.01, 0.01, 12)[0], 'km3 higher')
        # an interval that excludes 0 with p between 0.05 and 0.10 is not a direction
        self.assertEqual(analysis.verdict('judge', 'km3', 0.2, 0.01, 0.4, 0.07, 12)[0], 'inconclusive')
        # an interval through zero is inconclusive even when the sign-flip test is tiny
        self.assertEqual(analysis.verdict('judge', 'km3', 0.2, -0.01, 0.4, 0.001, 12)[0], 'inconclusive')

    def test_an_unusable_interval_is_inconclusive(self):
        self.assertEqual(analysis.verdict('judge', 'km3', 0.2, None, None, 0.01, 12)[0], 'inconclusive')

    def test_a_direction_needs_the_real_sign_flip_p_not_only_the_interval(self):
        # 10 games: the judge agrees (and km3 never does) in 5 of them, the other 5 are even. The interval excludes 0 (a resample without a favourable game has
        # probability 1/1024) but all 5 non-zero games point one way, which a randomisation test over games calls p = 2/32 = 0.0625: not a direction
        c = prefix(analyse(games_of(10, 1, lambda g, k: [1 if g < 5 else 0], lambda g, k: [0]), resamples=4000))
        self.assertGreater(c['ci_low'], 0)
        self.assertAlmostEqual(c['sign_flip_p'], 0.0625, places=4)
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIn('sign-flip', c['reason'])
        # six favourable games out of ten: p = 2/64 = 0.031: a direction
        c = prefix(analyse(games_of(10, 1, lambda g, k: [1 if g < 6 else 0], lambda g, k: [0]), resamples=4000))
        self.assertAlmostEqual(c['sign_flip_p'], 0.03125, places=4)
        self.assertEqual(c['verdict'], 'judge higher')

    def test_the_minimum_counts_the_games_with_data_not_the_games_in_the_population(self):
        def full(n_with_data):
            return lambda g, k: {'judge': [None if g >= n_with_data else 1], 'km3': [0]} if k == 0 else None
        f9 = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full(9)))['full_scope']
        self.assertEqual(f9['population']['n_games'], 12)  # twelve games hold full-scope points ...
        self.assertEqual(f9['contrasts'][0]['verdict'], 'inconclusive')  # ... but only nine of them have a value for both bots
        self.assertIn('9 games < 10', f9['contrasts'][0]['reason'])
        f10 = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full(10)))['full_scope']
        self.assertEqual(f10['contrasts'][0]['verdict'], 'judge higher')

    def test_a_rate_with_data_in_one_game_of_many_gets_no_interval(self):
        # the judge has a comparable full-plan value in ONE of twelve games: its rate has no interval (the games without data are not clusters of that rate)
        def full(g, k):
            return {'judge': [1 if g == 0 else None], 'km3': [0]} if k == 0 else None
        f = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full))['full_scope']
        r = f['rates']['judge']
        self.assertEqual((r['n_decisions'], r['n_games'], r['ci_low'], r['ci_high']), (1, 1, None, None))
        self.assertEqual(f['rates']['km3']['n_games'], 12)
        self.assertIsNotNone(f['rates']['km3']['ci_low'])

    def test_the_exact_sign_flip_limit_and_the_documented_constants(self):
        self.assertEqual(analysis.SIGN_FLIP_EXACT_MAX_GAMES, 16)
        self.assertEqual(analysis.sign_flip_p([1.0] * 16)[1], 'exact')
        self.assertEqual(analysis.sign_flip_p([1.0] * 16)[0], 2 / 65536)
        self.assertEqual(analysis.sign_flip_p([1.0] * 17)[1], 'monte-carlo')
        self.assertEqual((analysis.MIN_GAMES, analysis.RESAMPLES, analysis.MIN_FORMAL_RESAMPLES, analysis.CONFIDENCE, analysis.SEED), (10, 20000, 5000, 0.95, 20261019))
        self.assertEqual(analysis.PRIMARY_JUDGE_RUN, 0)

    def test_an_interval_from_one_game_is_not_reported(self):
        a = analyse(games_of(1, 3, lambda g, k: [1], lambda g, k: [0]), min_games=1)
        r = a['prefix']['rates']['judge']
        self.assertEqual((r['n_games'], r['ci_low'], r['ci_high']), (1, None, None))
        self.assertEqual(r['estimate'], 1.0)
        self.assertIsNone(prefix(a)['ci_low'])
        self.assertEqual(prefix(a)['verdict'], 'inconclusive')

    def test_dropped_pairs_are_shown_with_matched_rates_and_named_in_the_reason(self):
        # the judge's plan is not comparable at three decisions where km3 agrees: dropping them is conditional, so the contrast says on which decisions it was computed
        def full(g, k):
            return {'judge': [None if g < 3 else 1], 'km3': [1 if g < 3 else 0]} if k == 0 else None
        f = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full))['full_scope']
        c = f['contrasts'][0]
        self.assertEqual(c['n_pairs_dropped'], 3)
        self.assertEqual(c['matched_rates'], {'judge': 1.0, 'km3': 0.0})
        self.assertIn('computed on 9 of 12 decisions, 3 not comparable', c['reason'])
        self.assertAlmostEqual(f['rates']['km3']['estimate'], 3 / 12, places=5)  # km3's own rate covers all twelve decisions

    def test_the_report_does_not_depend_on_the_process_hash_seed(self):
        import subprocess
        code = ("import sys, json; sys.path.insert(0, %r); sys.path.insert(0, %r); import test_analysis as T; "
                "print(json.dumps(T.analyse(T.games_of(12, 2, lambda g, k: [1 if (g + k) %% 3 else 0], lambda g, k: [1 if g %% 2 else 0]), resamples=300), sort_keys=True))" % (os.path.dirname(HERE), HERE))
        outs = [subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True, env={**os.environ, 'PYTHONHASHSEED': s}).stdout for s in ('1', '2', '3')]
        self.assertTrue(outs[0] and outs[0] == outs[1] == outs[2])


class Clustering(unittest.TestCase):
    def test_correlated_decisions_in_one_game_widen_the_interval(self):
        # 10 games x 4 decisions, all-or-nothing within a game: 6 of 10 games agree; a naive point-level bootstrap would treat the 40 decisions as independent
        spec = games_of(10, 4, lambda g, k: [1 if g < 6 else 0], lambda g, k: [0])
        a = analyse(spec, resamples=4000)
        c = a['prefix']['rates']['judge']
        clustered = c['ci_high'] - c['ci_low']
        rows, _ = make_rows(spec)
        rng = random.Random(1)
        vals = [1.0 if r['agrees'] else 0.0 for r in rows if r['bot'] == 'judge']
        naive = sorted(sum(vals[int(rng.random() * 40)] for _ in range(40)) / 40 for _ in range(4000))
        lo, hi = analysis.percentile_interval(naive)
        self.assertGreater(clustered, 1.6 * (hi - lo))

    def test_the_interval_matches_the_binomial_for_one_decision_per_game(self):
        # 20 games, 10 agree, one decision each: Binomial(20, 0.5)/20 has 2.5% / 97.5% points near 0.30 / 0.70
        r = analyse(games_of(20, 1, lambda g, k: [1 if g < 10 else 0], lambda g, k: [0]), resamples=6000)['prefix']['rates']['judge']
        self.assertAlmostEqual(r['estimate'], 0.5, places=5)
        self.assertTrue(0.25 <= r['ci_low'] <= 0.35, r)
        self.assertTrue(0.65 <= r['ci_high'] <= 0.75, r)

    def test_unequal_game_sizes_use_the_ratio_bootstrap_not_the_mean_of_game_means(self):
        # one game with 12 decisions (9 favourable), eleven with 1 (3 favourable): the exact ratio bootstrap gives this golden interval (checked by enumeration)
        counts = [12] + [1] * 11
        sums = [9.0] + [1.0] * 3 + [0.0] * 8
        point, lo, hi = analysis.game_bootstrap({'diff': (sums, counts)}, resamples=20000)['diff']
        self.assertEqual((round(point, 3), round(lo, 3), round(hi, 3)), (0.522, 0.083, 0.689))

    def test_the_interval_function_takes_the_right_order_statistics(self):
        draws = [i / 1000 for i in range(1000)]
        self.assertEqual(analysis.percentile_interval(draws), (0.025, 0.974))  # floor(25) and ceil(975) - 1
        self.assertEqual(analysis.percentile_interval(list(range(1500)))[0], 37)  # 0.025 * 1500 = 37.5: floored
        self.assertEqual(analysis.percentile_interval(list(range(20000))), (500, 19499))
        with self.assertRaises(ValueError):
            analysis.percentile_interval([])

    def test_the_resample_count_is_honoured_and_validated(self):
        calls = []

        class Counting(random.Random):
            def random(self):
                calls.append(1)
                return super().random()
        orig = analysis.random.Random
        analysis.random.Random = Counting
        try:
            analysis.game_bootstrap({'x': ([1.0] * 12, [1] * 12)}, resamples=2500)
        finally:
            analysis.random.Random = orig
        self.assertEqual(len(calls), 2500 * 12)  # one draw per game per resample
        for bad in (0, -5, 1.5, True, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                analysis.game_bootstrap({'x': ([1.0] * 12, [1] * 12)}, resamples=bad)

    def test_all_series_share_one_set_of_draws(self):
        # a rate and a difference built from the same data must move together: a = rate, d = a - 0 is the same series, so the same interval
        s = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0]
        est = analysis.game_bootstrap({'rate': (s, [1] * 12), 'diff': (list(s), [1] * 12)}, resamples=2000)
        self.assertEqual(est['rate'], est['diff'])


class RepeatsAreASensitivityEstimateNotExtraSamples(unittest.TestCase):
    def test_the_primary_result_is_the_one_predefined_call(self):
        # repeat 0 is wrong everywhere, repeats 1 and 2 are right: the primary result is repeat 0, whatever the others did
        a = analyse(games_of(12, 2, lambda g, k: [0, 1, 1], lambda g, k: [1]), judge_repeats=3)
        self.assertAlmostEqual(a['prefix']['rates']['judge']['estimate'], 0.0, places=5)
        self.assertEqual(prefix(a)['verdict'], 'km3 higher')
        self.assertAlmostEqual(a['prefix']['sensitivity']['judge_rate']['estimate'], 2 / 3, places=5)
        self.assertEqual(a['prefix']['population']['n_decisions'], 24)  # a decision counts once, not once per repeat
        # and the other way round: the better repeat is not picked up either
        b = analyse(games_of(12, 2, lambda g, k: [1, 0, 0], lambda g, k: [0]), judge_repeats=3)
        self.assertAlmostEqual(b['prefix']['rates']['judge']['estimate'], 1.0, places=5)
        self.assertAlmostEqual(b['prefix']['sensitivity']['judge_rate']['estimate'], 1 / 3, places=5)

    def test_the_sensitivity_estimate_is_reported_apart_with_no_verdict_and_the_repeat_consistency(self):
        spec = games_of(12, 2, lambda g, k: [1, 1, 0] if k == 0 else [1, 1, 1], lambda g, k: [0])
        s = analyse(spec, judge_repeats=3)['prefix']['sensitivity']
        self.assertEqual([c['a'] for c in s['contrasts']], ['judge'])
        self.assertNotIn('verdict', s['contrasts'][0])  # the primary contrast is the only one that draws a direction
        self.assertAlmostEqual(s['contrasts'][0]['estimate'], 5 / 6, places=5)  # the contrast uses the repeat mean, not the primary call (1.0)
        rc = s['repeat_consistency']
        self.assertEqual(rc['of_decisions'], 24)
        self.assertEqual(rc['decisions_with_the_same_plan_in_every_repeat'], 12)  # plan numbers: [1,1,2] differs, [1,1,1] is the same
        self.assertAlmostEqual(rc['pairwise_same_plan'], (12 * 1 + 12 * 3) / 72, places=5)
        self.assertIsNone(analyse(spec, judge_repeats=1)['prefix']['sensitivity'])  # one call per decision: nothing to report apart

    def test_a_contrast_with_the_judge_second_gets_its_sensitivity_version_too(self):
        spec = games_of(12, 1, lambda g, k: [1, 0], lambda g, k: [1])
        s = analyse(spec, judge_repeats=2, contrasts=[('km3', 'judge')])['prefix']['sensitivity']
        self.assertEqual([(c['a'], c['b']) for c in s['contrasts']], [('km3', 'judge')])
        self.assertAlmostEqual(s['contrasts'][0]['estimate'], 0.5, places=5)

    def test_a_step_bots_value_is_the_mean_over_all_its_predefined_seeds(self):
        a = analyse(games_of(12, 1, lambda g, k: [1], lambda g, k: [1, 0]))  # km3: seed 1 agrees, seed 2 does not
        self.assertAlmostEqual(a['prefix']['rates']['km3']['estimate'], 0.5, places=5)
        self.assertNotIn('discordant', prefix(a))  # fractional values: no 2x2 table

    def test_a_missing_primary_call_is_an_error_not_a_silent_fallback(self):
        rows, elig = make_rows(games_of(12, 1, lambda g, k: [1], lambda g, k: [0]))
        with self.assertRaises(ValueError):
            analysis.analyse([r for r in rows if not (r['bot'] == 'judge' and r['position'] == 'g00-d0')], elig, ['km3', 'judge'], 1, resamples=50)
        rows, elig = make_rows(games_of(12, 1, lambda g, k: [1, 1], lambda g, k: [0]))
        with self.assertRaises(ValueError):  # a judge decision that has repeats but no repeat 0
            analysis.analyse([r for r in rows if not (r['bot'] == 'judge' and r['run'] == 0 and r['position'] == 'g00-d0')], elig, ['km3', 'judge'], 2, resamples=50)

    def test_contrasts_must_name_two_different_bots_of_the_batch(self):
        rows, elig = make_rows(games_of(12, 1, lambda g, k: [1], lambda g, k: [0]))
        for bad in ([('judge', 'nobody')], [('judge', 'judge')], [('km3', 'judge'), ('x', 'y')]):
            with self.assertRaises(ValueError):
                analysis.analyse(rows, elig, ['km3', 'judge'], 1, contrasts=bad, resamples=50)


class SelectionAndScopes(unittest.TestCase):
    def full(self, g, k):
        return {'judge': [1], 'km3': [0]} if k == 0 else None  # the first decision of each game is full-scope: the judge's complete plan agrees, km3's does not

    def test_analyse_refuses_rows_of_points_outside_the_primary_selection(self):
        rows, elig = make_rows(games_of(12, 2, lambda g, k: [1], lambda g, k: [0]))
        rows.append({**rows[0], 'position': 'stranger', 'game': 'gX'})
        with self.assertRaises(ValueError) as cm:
            analysis.analyse(rows, elig, ['km3', 'judge'], 1, resamples=50)
        self.assertIn('outside the primary selection', str(cm.exception))

    def test_a_point_outside_the_selection_changes_no_primary_number_even_when_its_rows_are_extreme(self):
        spec = games_of(12, 2, lambda g, k: [1 if (g + k) % 3 else 0], lambda g, k: [1 if (g * k) % 2 else 0])
        rows, elig = make_rows(spec)
        base = analysis.analyse(rows, elig, ['km3', 'judge'], 1, resamples=500)
        # the same selection, plus a whole game of unselected rows that all agree for the judge and none for km3: handing them to analyse is refused, and filtering
        # them out (the caller's job) leaves every primary number identical
        extra = [{**r, 'position': r['position'] + 'x', 'game': 'gX', 'agrees': r['bot'] == 'judge', 'full_agrees': r['bot'] == 'judge'} for r in rows[:8]]
        again = analysis.analyse([r for r in rows + extra if r['position'] in set(elig['primary_ids'])], elig, ['km3', 'judge'], 1, resamples=500)
        self.assertEqual(base, again)

    def test_full_plan_agreement_is_a_separate_block_over_the_full_scope_subset_only(self):
        spec = games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=self.full)
        a = analyse(spec)
        self.assertEqual(a['prefix']['population']['n_decisions'], 24)
        self.assertEqual(a['full_scope']['population']['n_decisions'], 12)  # the first decision of each game
        self.assertAlmostEqual(a['full_scope']['rates']['judge']['estimate'], 1.0, places=5)
        self.assertAlmostEqual(a['full_scope']['rates']['km3']['estimate'], 0.0, places=5)
        self.assertEqual(a['full_scope']['contrasts'][0]['verdict'], 'judge higher')
        self.assertIsNone(analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0]))['full_scope'])  # no full-scope subset: no block

    def test_a_judge_plan_that_stops_at_a_chance_event_is_not_comparable_and_is_counted_not_dropped(self):
        def full(g, k):
            return {'judge': [None if g < 4 else 1], 'km3': [1]} if k == 0 else None
        a = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full))
        f = a['full_scope']
        self.assertEqual(f['not_comparable']['judge'], [f'g{g:02d}-d0' for g in range(4)])
        self.assertEqual(f['not_comparable']['km3'], [])
        self.assertEqual(f['rates']['judge']['n_decisions'], 8)
        c = f['contrasts'][0]
        self.assertEqual((c['n_decisions'], c['n_pairs_dropped']), (8, 4))  # the pairs without a comparable judge value are named, not silently gone
        self.assertEqual(f['rates']['km3']['n_decisions'], 12)

    def test_the_full_scope_block_never_fails_the_batch_but_says_inconclusive_with_too_few_games(self):
        def full(g, k):
            return {'judge': [1], 'km3': [0]} if (k == 0 and g < 3) else None
        a = analyse(games_of(12, 2, lambda g, k: [1], lambda g, k: [0], full=full))
        c = a['full_scope']['contrasts'][0]
        self.assertEqual(c['verdict'], 'inconclusive')
        self.assertIn('3 games < 10', c['reason'])

    def test_the_diagnostic_block_is_descriptive_only(self):
        rows, elig = make_rows(games_of(2, 2, lambda g, k: [1 if k == 0 else 0], lambda g, k: [0]))
        ids = elig['primary_ids']
        d = analysis.diagnostic_block(rows, ids, {ids[0]: 'developer exposure (synthetic)'}, ['km3', 'judge'], 1)
        self.assertEqual(d['per_bot']['judge'], {'decisions_resolved': 4, 'agreement_sum': 2.0})
        self.assertEqual(d['points'][0], {'position': ids[0], 'reason': 'developer exposure (synthetic)'})
        self.assertEqual(set(d), {'what', 'points', 'per_bot'})  # counts only: no interval, no contrast, no verdict field
        self.assertEqual(set(d['per_bot']['judge']), {'decisions_resolved', 'agreement_sum'})

    def test_the_eligibility_file_is_checked_for_shape(self):
        ok = {'primary_ids': ['a', 'b'], 'full_scope_ids': ['a'], 'games': {'a': 'g1', 'b': 'g2'}, 'excluded_reasons': {'c': 'exposure'}}
        self.assertEqual(analysis.eligibility_shape_problems(ok), [])
        self.assertEqual(analysis.eligibility_shape_problems({**ok, 'full_scope_ids': []}), [])
        bad_cases = [None, [], {}, {**ok, 'primary_ids': []}, {**ok, 'primary_ids': ['a', 'a']}, {**ok, 'full_scope_ids': ['z']}, {**ok, 'games': ['g']},
                     {**ok, 'games': {'a': ''}}, {**ok, 'excluded_reasons': {'c': '  '}}, {**ok, 'excluded_reasons': {'a': 'x'}}, {**ok, 'primary_ids': 'a'},
                     {k: v for k, v in ok.items() if k != 'full_scope_ids'},  # a missing key would silently mean "no full-scope subset"
                     {**ok, 'full_scope_id': ['a']}, {**ok, 'schema': 'other'},  # a misspelt key / the wrong schema
                     {**ok, 'games': {'a': 'g1 ', 'b': 'g2'}}, {**ok, 'games': {'a': 'G1', 'b': 'g1'}}, {**ok, 'games': {'a': 'g​1', 'b': 'g2'}}]
        for bad in bad_cases:
            self.assertTrue(analysis.eligibility_shape_problems(bad), bad)

    def test_eligibility_problems_name_each_failure_kind(self):
        ids = ['p1', 'p2', 'p3']
        refs = {'p1': [1], 'p2': [1], 'p3': [1], 'p4': 'junk never read'}
        ok = {'primary_ids': ['p1', 'p2'], 'full_scope_ids': [], 'games': {'p1': 'a', 'p2': 'b', 'p3': 'c'}}
        kinds = lambda **kw: sorted(p['kind'] for p in analysis.eligibility_problems(**kw))
        self.assertEqual(kinds(ids=ids, references=refs, e=ok, min_games=2), [])
        self.assertEqual(kinds(ids=ids, references=refs, e=None), ['no_eligibility'])
        self.assertEqual(kinds(ids=ids, references=refs, e={**ok, 'primary_ids': ['p1', 'p9']}, min_games=1), ['primary_not_in_batch'])
        self.assertEqual(kinds(ids=ids, references=refs, e={**ok, 'games': {'p1': 'a'}}, min_games=1), ['no_game'])
        self.assertEqual(kinds(ids=ids, references={'p1': [1]}, e=ok, min_games=1), ['reference_missing'])
        self.assertEqual(kinds(ids=ids, references={**refs, 'p2': []}, e=ok, min_games=1), ['reference_missing'])
        self.assertEqual(kinds(ids=ids, references=refs, e=ok, min_games=3), ['too_few_games'])
        self.assertEqual(set(kinds(ids=ids, references=refs, e={'primary_ids': 'p1'})), {'eligibility_malformed'})
        # two selected points in ONE game are one cluster
        self.assertEqual(kinds(ids=ids, references=refs, e={**ok, 'games': {'p1': 'a', 'p2': 'a'}}, min_games=2), ['too_few_games'])


class Reproducibility(unittest.TestCase):
    def test_the_same_seed_gives_the_same_report_bit_for_bit(self):
        spec = games_of(12, 2, lambda g, k: [1 if (g + k) % 3 else 0], lambda g, k: [1 if (g * k) % 2 else 0])
        a, b = analyse(spec), analyse(spec)
        self.assertEqual(a, b)
        self.assertEqual(a['method']['seed'], analysis.SEED)
        self.assertEqual(analyse(spec, seed=7)['method']['seed'], 7)  # the seed used is part of the report
        self.assertEqual(a['method']['bots'], ['km3', 'judge'])
        self.assertEqual((a['method']['judge_repeats'], a['method']['contrasts']), (1, ['judge:km3']))

    def test_sign_flip_is_exact_for_small_samples_and_seeded_beyond(self):
        self.assertEqual(analysis.sign_flip_p([1.0, 1.0, 1.0]), (0.25, 'exact'))  # 2 of 8 sign patterns reach |sum| = 3
        self.assertEqual(analysis.sign_flip_p([1.0, -1.0]), (1.0, 'exact'))  # |sum| = 0: every pattern is at least as extreme
        self.assertEqual(analysis.sign_flip_p([0.0] * 5), (1.0, 'exact'))
        p, how = analysis.sign_flip_p([1.0] * 17)
        self.assertEqual(how, 'monte-carlo')
        self.assertLess(p, 0.001)
        self.assertGreater(analysis.sign_flip_p([1.0] * 30)[0], 0.0)  # the +1: a Monte Carlo p is never exactly 0
        self.assertEqual(analysis.sign_flip_p([1.0] * 17), (p, how))  # seeded


if __name__ == '__main__':
    unittest.main()
