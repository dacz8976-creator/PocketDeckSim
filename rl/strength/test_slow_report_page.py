#!/usr/bin/env python3
"""Tests for what slow_report.py says: the page SLOW_REPORT.md, the lines it prints, the question it registers and the plan it shows.

  cd rl/strength && python3 -B -m unittest -v test_slow_report_page

Written after the second adversarial review, which showed that wrong numbers, swapped labels, a dropped sentence and a verdict in plain words could all pass the
first suite. Nothing here plays a game: the pages are written from synthetic registered runs (synth_run of test_slow_report: a manifest, its sha256 and game
records in a temporary folder) and the end-to-end checks use that file's fake program and temporary repository. The arithmetic the page is compared with is written
out again here (a Student t value integrated from the density, Wilson and paired differences) and not taken from the code under test; the page tests use the t table
only after StudentT has checked it against the true values.

What is pinned:
  * the numbers: the t table (all 30 values and the expansion beyond), the lengths of time, the gain and its range in each of its three cases, who went first,
    the median and the mean of the game times, the counts of a partial run, the width of a range in points;
  * the words: the question first, then the size, every interval saying which games it refers to, the error paragraph, the held-out sentence ("the held-out lock is
    unchanged"), the section of what the numbers can and cannot say, whole and word for word;
  * the counts: every count names whose games it counts and is singular at one ("1 kx3 game", "80 cheap km3 baseline games", "1 paired game", "2 tries"), the gain is
    counted in paired games (a deal and seat played by both pilots), a banner or a running time says what the total is made of (kx3 games + baseline games), and the
    sentences about the gain's range are checked case by case: too wide for the scale, cut at its ends, "just above +0.0", wholly above or below zero, including zero;
  * the registration time: "before any game" only when no game started before the registration, on both pages (a game that started earlier is named);
  * the standing rule that nothing it prints or writes says pass or fail, in the words of a verdict or in plain sentences, on the page and on every line of the terminal;
  * the registered question, with each pilot in its own role, and each pilot's provenance beside that pilot;
  * what the terminal says: the plan lines, the stop after --max-games, a failed engineering report, a partial page, the same headline on a resumed run;
  * the log: every step is recorded, with both pilots and a UTC time.
It ends with the same kind of checks on the page built from games that already exist (slow_report_existing.py).
"""
import json, math, os, re, select, shutil, signal, statistics, subprocess, sys, tempfile, time, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402
import test_slow_report as T  # noqa: E402  (the fake program, the World fixture, synth_run and the reference Wilson arithmetic)
import test_slow_report_existing as TE  # noqa: E402  (synthetic development and gate-3 runs for the page built from games that already exist)

PANEL, SC, BLOCK, STEP = T.PANEL, T.SC, T.BLOCK, T.STEP
read, write, jsonl, wilson95, pc = T.read, T.write, T.jsonl, T.wilson95, T.pc
TAG = '[kx3 (d513e37b) on my-list v km3 on the public panel] '
PASS_OR_FAIL = 'no pass or fail line'  # the one way the word pass may appear: saying there is none


def student_t_95(df, steps=200):
    """The two-sided 95% point of Student's t with df degrees of freedom: the density is integrated (Simpson) and the point found by bisection, so the table in
    slow_report.py is compared with the true values and not with itself."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)

    def f(t):
        return c * (1 + t * t / df) ** (-(df + 1) / 2)

    def area(x):
        h = x / steps
        return (f(0.0) + f(x) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, steps))) * h / 3
    lo, hi = 0.0, 20.0
    for _ in range(45):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if area(mid) < 0.475 else (lo, mid)
    return (lo + hi) / 2


def points(x):
    return f'{100 * x:+.1f}'


def gain(games):
    """(n, mean, half, kx3's mean score, km3's mean score) over the paired games (a deal and seat played by both pilots), the t value from slow_report's table (checked by StudentT)."""
    by = {}
    for g in games:
        by.setdefault((g['opp'], g['deal'], g['seat']), {})[g['arm']] = SC[g['winner']]
    both = [v for v in by.values() if 'X' in v and 'ref' in v]
    d = [v['X'] - v['ref'] for v in both]
    n, m, sd = len(d), statistics.mean(d), statistics.stdev(d)
    return n, m, sr.t_crit(n - 1) * sd / math.sqrt(n), statistics.mean(v['X'] for v in both), statistics.mean(v['ref'] for v in both)


def verdict_words(text):
    """The ways of saying pass or fail, in words and in a plain sentence, found in `text` once the one allowed phrase is taken out."""
    text = text.replace(PASS_OR_FAIL, '').replace('No pass or fail line', '').replace('not a ranking', '')
    found = []
    for pattern in (r'\bpass(es|ed|ing)?\b', r'\bfail(s|ed|ing|ure)?\b', r'\bverdict\b', r'\bcut-?off', r'\bgood enough\b', r'\bthreshold\b', r'\bfloor\b', r'\bclears?\b',
                    r'\bborderline\b', r'\branking\b', r'\bworth\b', r'\brecommend', r'\bshould\b', r'\bdeserves?\b', r'\bplayable\b', r'\bviable\b', r'\bcompetitive\b',
                    r'\bgood\b', r'\bbad\b',
                    r'\b(above|below|under|over|at least|at most|more than|less than)\s+\d+(\.\d+)?\s*%'):  # a score said to be above or below a mark
        if re.search(pattern, text, re.I):
            found.append(pattern)
    return found


class Pages(T.Timed):
    """A registered run directory of synthetic games, and the page written from it."""

    def run_dir(self, **kw):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = T.synth_run(t, **kw)
        return t, man, games

    def build(self, **kw):
        t, man, games = self.run_dir(**kw)
        return t, man, games, sr.write_slow_report(t)

    def rewrite(self, t, games):
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games))
        return sr.write_slow_report(t)

    @staticmethod
    def part(text, title):
        return text.split(title)[1].split('\n## ')[0]


# ---------------------------------------------------------------------------------------------------------- the numbers
class StudentT(T.Timed):
    def test_every_value_up_to_30_degrees_of_freedom_is_the_true_two_sided_95_percent_point(self):
        for df in range(1, 31):
            self.assertAlmostEqual(sr.t_crit(df), student_t_95(df), delta=0.0006, msg=f'df {df}')

    def test_beyond_30_the_expansion_is_within_three_ten_thousandths_of_the_true_value(self):
        for df in (31, 32, 35, 40, 47, 60, 100, 120, 500, 1000):
            self.assertAlmostEqual(sr.t_crit(df), student_t_95(df), delta=0.0003, msg=f'df {df}')

    def test_with_no_degrees_of_freedom_there_is_no_value(self):
        self.assertTrue(math.isnan(sr.t_crit(0)))


class PlainTimes(T.Timed):
    def test_a_duration_is_in_seconds_minutes_hours_or_days_by_its_size(self):
        for sec, want in ((0, '0 s'), (89, '89 s'), (100, '2 min'), (5399, '90 min'), (5400, '1.5 h'), (7200, '2.0 h'), (172799, '48.0 h'), (172800, '2.0 days'),
                          (3 * 86400, '3.0 days'), (float('nan'), 'n/a')):
            self.assertEqual(sr.human_time(sec), want, sec)

    def test_the_expected_hours_of_the_plan_are_minutes_below_two_hours_and_hours_from_two(self):
        for h, want in ((0.4, '24 minutes'), (1.9, '114 minutes'), (2.0, '2.0 hours'), (3.0, '3.0 hours'), (8.9, '8.9 hours')):
            self.assertEqual(sr.hours_text(h), want, h)

    def test_a_log_time_is_utc_whatever_zone_it_was_read_in(self):
        self.assertEqual(sr.utc_iso(T.chi(2026, 10, 10, 10, 0)), '2026-10-10T15:00:00Z')  # Chicago is five hours behind UTC in October
        self.assertEqual(sr.utc_iso(T.chi(2026, 1, 10, 10, 0)), '2026-01-10T16:00:00Z')  # and six in winter
        self.assertRegex(sr.utc_iso(), r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')


class PlanLines(T.World):
    """The five lines a dry run prints, word for word, with the pin's rates replaced by round ones so the hours can be written down."""

    def with_rates(self, **rates):
        pin = json.loads(read(self.pin_path))
        pin['games_per_hour'] = rates
        write(self.pin_path, json.dumps(pin))

    def plan(self, *extra):
        code, out, err = self.cli(*extra, '--dry-run')
        self.assertEqual(code, 0, out + err)
        lines = out.splitlines()
        for l in lines:
            self.assertTrue(l.startswith(TAG), l)
        return [l[len(TAG):] for l in lines]

    def expected_time_line(self, games, low, high, wall, no_paired=False):
        """The size line: both pilots' games counted (kx3 games v all games), then the time, which is for the kx3 games only."""
        left_out = '; with --no-paired they are still played and the page leaves them out' if no_paired else ''
        return (f'size: {games} kx3 games + {games} cheap km3 baseline games on the same deals ({2 * games} games in all; the km3 games take about a second each{left_out}); '
                f'the time is for the {games} kx3 games: about {low} to {high} if the deck plays like most of his, '
                f'about {wall} if it plays like the Wailord wall (measured with 2 games at a time)')

    def test_the_dry_run_prints_exactly_these_five_lines(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        lines = self.plan('--deals', '3')
        self.assertEqual(len(lines), 5, lines)
        self.assertTrue(lines[0].startswith('plan: my-list (decks/events/my-list.txt, ') and lines[0].endswith('), 3 deals x 2 seats against the 8 public lists'), lines[0])
        self.assertEqual(lines[1], self.expected_time_line(48, '72 minutes', '2.4 hours', '4.8 hours'))
        self.assertEqual(lines[2], 'on school days the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer')
        slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
        seed = BLOCK[0] + (int(T.sha(self.deck)[:8], 16) % slots) * STEP
        self.assertEqual(lines[3], f"stage use (not development evidence; the held-out lock is untouched), seeds from {seed}, program {self.pin['program']} (pinned, sha256 "
                                   f"{self.pin['program_sha256'][:12]}), with the comparison with km3 on the same deals in the page, no pass or fail line")
        self.assertEqual(lines[4], 'dry run: nothing written')

    def test_without_the_baseline_the_stage_line_says_without_and_the_size_line_says_the_games_are_still_played(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        lines = self.plan('--deals', '3', '--no-paired')
        self.assertEqual(len(lines), 5, lines)
        self.assertTrue(lines[3].endswith('), without the comparison with km3 on the same deals in the page, no pass or fail line'), lines[3])
        self.assertNotIn('with the comparison', lines[3])
        self.assertEqual(lines[1], self.expected_time_line(48, '72 minutes', '2.4 hours', '4.8 hours', no_paired=True))
        paired = self.plan('--deals', '3')
        self.assertNotIn('--no-paired', paired[1], 'the note is only for a run without the comparison')
        self.assertTrue(paired[3].endswith('), with the comparison with km3 on the same deals in the page, no pass or fail line'), paired[3])

    def test_the_size_line_counts_both_pilots_games_and_says_the_time_is_for_the_kx3_games(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        for deals in (1, 2, 7):
            line = self.plan('--deals', str(deals))[1]
            g = 16 * deals
            self.assertTrue(line.startswith(f'size: {g} kx3 games + {g} cheap km3 baseline games on the same deals ({2 * g} games in all; '), line)
            self.assertIn(f'the time is for the {g} kx3 games: about ', line)
        self.assertEqual(self.plan('--deals', '1')[0].rsplit('), ', 1)[1], '1 deal x 2 seats against the 8 public lists', 'one deal is not pluralised')

    def test_the_expected_time_is_in_minutes_below_two_hours_and_in_hours_from_two(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        self.assertEqual(self.plan('--deals', '1')[1], self.expected_time_line(16, '24 minutes', '48 minutes', '96 minutes'))
        self.assertEqual(self.plan('--deals', '5')[1], self.expected_time_line(80, '2.0 hours', '4.0 hours', '8.0 hours'))

    def test_the_default_is_five_deals(self):
        lines = self.plan()
        self.assertTrue(lines[0].endswith('), 5 deals x 2 seats against the 8 public lists'), lines[0])
        self.assertTrue(lines[1].startswith('size: 80 kx3 games + 80 cheap km3 baseline games on the same deals (160 games in all; '), lines[1])


# ---------------------------------------------------------------------------------------------------------- the registered question
QUESTION = ("{headline}. A slow report on one deck, not development: how does {deck} do when the strong, slow pilot {pilot} plays it against the eight public panel lists "
            "played by {ref}, {deals} x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; "
            "{baseline}. "
            "Realistic knowledge: {pilot} plays the deck knowing its own cards; the deck is never one of the lists {pilot} guesses its opponent from, "
            "and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.")
# What the registered question says about the comparison with the reference: it depends on whether the page will carry it (--no-paired leaves it out, the games are still played).
BASELINE_ON = 'and how much better {pilot} plays this deck than {ref} on the same deals'
BASELINE_OFF = 'without the comparison with {ref} on the same deals (--no-paired: the {ref} games are still played, about a second each, and left out of the page)'


def question(paired=True, headline='kx3 (d513e37b) on my-list v km3 on the public panel', deck='my-list', pilot='kx3', ref='km3', deals=5):
    """The registered question, word for word, as the registration must carry it (the number of deals pluralised: 1 deal, 5 deals)."""
    baseline = (BASELINE_ON if paired else BASELINE_OFF).format(pilot=pilot, ref=ref)
    return QUESTION.format(headline=headline, deck=deck, pilot=pilot, ref=ref, deals=f'{deals} deal' + ('' if deals == 1 else 's'), baseline=baseline)


class RegisteredQuestion(T.World):
    def config(self, pin, deck_name='my-list', deals=5, paired=True):
        return sr.build_config(pin=pin, pin_path=self.pin_path, deck_rel=self.deck_rel, deck_name=deck_name, deck_sha='a' * 64, deck_state='committed', deals=deals, paired=paired,
                               seed_base=BLOCK[0], threads=2, program_sha=pin['program_sha256'])

    def test_the_question_is_this_text_with_each_pilot_in_its_own_role(self):
        pin = json.loads(read(self.pin_path))
        for paired in (True, False):
            self.assertEqual(self.config(pin, paired=paired)['question'], question(paired=paired), paired)

    def test_the_question_asks_for_the_comparison_only_when_the_page_carries_it(self):
        pin = json.loads(read(self.pin_path))
        on, off = self.config(pin, paired=True)['question'], self.config(pin, paired=False)['question']
        self.assertNotEqual(on, off)
        self.assertIn('and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge:', on)
        self.assertNotIn('--no-paired', on)
        self.assertNotIn('how much better', off, 'a page without the comparison does not register the question of how much better')
        self.assertIn('with 95% ranges; without the comparison with km3 on the same deals (--no-paired: the km3 games are still played, about a second each, and left out of the page). '
                      'Realistic knowledge:', off)
        self.assertNotIn('unless', on + off, 'the question no longer says "(unless --no-paired)": it says which of the two it is')

    def test_other_names_and_other_deals_change_the_names_and_the_deals_and_nothing_else(self):
        pin = json.loads(read(self.pin_path))
        pin.update(pilot='kz9', reference='kr1', pilot_label='kz9 (abc)', reference_label='kr1 (def)', panel_label='the test panel')
        for paired in (True, False):
            want = question(paired=paired, headline='kz9 (abc) on other-deck v kr1 (def) on the test panel', deck='other-deck', pilot='kz9', ref='kr1', deals=3)
            self.assertEqual(self.config(pin, deck_name='other-deck', deals=3, paired=paired)['question'], want, paired)
        self.assertNotIn('km3', want)
        self.assertNotIn('kx3', want)

    def test_one_deal_is_not_pluralised_in_the_question_nor_in_the_summary(self):
        pin = json.loads(read(self.pin_path))
        one, five = self.config(pin, deals=1), self.config(pin, deals=5)
        self.assertIn('played by km3, 1 deal x 2 seats each? Primary:', one['question'])
        self.assertIn('played by km3, 5 deals x 2 seats each? Primary:', five['question'])
        self.assertNotIn('1 deals', one['question'] + one['slow_report']['summary'])
        self.assertEqual(one['slow_report']['summary'], 'Stage use. 1 deal x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.')
        self.assertEqual(five['slow_report']['summary'], 'Stage use. 5 deals x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.')

    def test_the_registration_keeps_the_question_in_the_manifest_and_the_preregistration(self):
        for deals, extra, paired in ((2, (), True), (1, ('--no-paired',), False)):
            shutil.rmtree(self.out_root, ignore_errors=True)
            code, out, err = self.cli('--deals', str(deals), '--register-only', *extra)
            self.assertEqual(code, 0, out + err)
            want = question(paired=paired, deals=deals)
            man = json.loads(read(os.path.join(self.rundir(), 'manifest.json')))
            self.assertEqual(man['question'], want)
            self.assertEqual(man['slow_report']['paired'], paired)
            self.assertIn('\n' + want + '\n', read(os.path.join(self.rundir(), 'PREREGISTRATION.md')))
            self.assertIn(f"**kx3 (d513e37b) on my-list v km3 on the public panel**. Stage use. {deals} deal" + ('' if deals == 1 else 's')
                          + ' x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.\n', read(os.path.join(self.rundir(), 'PREREGISTRATION.md')))

    def test_each_pilots_provenance_text_stays_with_that_pilot(self):
        pin = json.loads(read(self.pin_path))
        pin.update(pilot_provenance='the pilot came from here', reference_provenance='the reference came from there')
        cfg = self.config(pin)
        self.assertEqual((cfg['pilot_provenance'], cfg['reference_provenance']), ('the pilot came from here', 'the reference came from there'))

    def test_the_preregistration_puts_each_provenance_beside_its_pilot(self):
        d = self.register()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual((man['pilot_provenance'], man['reference_provenance']), (self.pin['pilot_provenance'], self.pin['reference_provenance']))
        text = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertIn(f"- **Pilot under test (arm X):** `kx3` ({self.pin['pilot_provenance']})", text)
        self.assertIn(f"- **Reference (arm ref, and the opponent in both arms):** `km3` ({self.pin['reference_provenance']})", text)


# ---------------------------------------------------------------------------------------------------------- the top of the page, the question and the size
class TopOfThePage(Pages):
    def test_the_title_the_headline_with_the_panel_in_its_registered_order_and_the_stage(self):
        t, man, games = self.run_dir(deals=1)
        order = PANEL[3:] + PANEL[:3]  # not alphabetical, not reversed: the order of the registration
        man['opponents'] = [next(o for o in man['opponents'] if o['name'] == n) for n in order]
        T.rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        lines = text.splitlines()
        self.assertEqual(lines[0], '# Slow report: my-list')
        self.assertEqual(lines[2], '**kx3 (d513e37b) on my-list v km3 on the public panel** (8 public lists: ' + ', '.join(order) + '). Stage `use`: a report on one deck, not development evidence.')
        self.assertEqual(lines[4], '## What it says')
        rows = [l.split(' | ')[0][2:] for l in lines if l.startswith('| t-')]
        self.assertEqual(rows, order, 'the table follows the registered order too')

    def test_a_finished_run_has_no_partial_banner_and_a_partial_one_has_it_right_below_the_headline(self):
        t, man, games, text = self.build(deals=2)
        self.assertNotIn('PARTIAL', text)
        t, man, games = self.run_dir(deals=2)
        text = self.rewrite(t, games[:37])
        banner = ('**PARTIAL: 37 of 64 games played so far (18 kx3 games + 19 cheap km3 baseline games; both count in the 64). '
                  'The numbers below will move; read them as a snapshot.**')
        self.assertEqual(text.splitlines()[4], banner)
        self.assertEqual(text.count('PARTIAL'), 1)

    def test_the_partial_banner_counts_each_pilots_games_in_the_singular_and_at_zero(self):
        t, man, games = self.run_dir(deals=2)
        both = [games[0], games[1]]  # a km3 baseline game, then the kx3 game of the same deal and seat
        self.assertEqual([g['arm'] for g in both], ['ref', 'X'])
        for keep, counts in (([games[1]], '1 kx3 game + 0 cheap km3 baseline games'), ([games[0]], '0 kx3 games + 1 cheap km3 baseline game'),
                             (both, '1 kx3 game + 1 cheap km3 baseline game'), (games[:3], '1 kx3 game + 2 cheap km3 baseline games')):
            text = self.rewrite(t, keep)
            self.assertEqual(text.splitlines()[4], f'**PARTIAL: {len(keep)} of 64 games played so far ({counts}; both count in the 64). '
                                                    'The numbers below will move; read them as a snapshot.**', counts)

    def test_a_run_without_the_comparison_still_counts_the_baseline_games_in_its_banner(self):
        """The program plays the km3 games whether or not the page reports the comparison, and they are in the total, so the banner says what the total is made of."""
        t, man, games = self.run_dir(deals=2, paired=False)
        text = self.rewrite(t, games[:37])
        self.assertEqual(text.splitlines()[4], '**PARTIAL: 37 of 64 games played so far (18 kx3 games + 19 cheap km3 baseline games; both count in the 64). '
                                               'The numbers below will move; read them as a snapshot.**')

    def test_the_question_and_the_size_each_appear_once_in_every_case(self):
        q_paired = 'Question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?'
        q_alone = 'Question: how does my-list do when kx3 plays it against the 8 public lists?'
        cases = (
            (dict(paired=True), 64, q_paired, 'Size: 32 kx3 games + 32 cheap km3 baseline games (2 deals x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck).'),
            (dict(paired=False), 64, q_alone, 'Size: 32 kx3 games (2 deals x 2 seats against each of the 8 public lists).'),
            (dict(paired=True), 37, q_paired, 'Size: 18 kx3 games + 19 cheap km3 baseline games so far, of 32 kx3 games + 32 cheap km3 baseline games planned.'),
            (dict(paired=False), 37, q_alone, 'Size: 18 kx3 games so far, of 32 kx3 games planned.'),
            (dict(paired=True), 2, q_paired, 'Size: 1 kx3 game + 1 cheap km3 baseline game so far, of 32 kx3 games + 32 cheap km3 baseline games planned.'),
            (dict(paired=False), 2, q_alone, 'Size: 1 kx3 game so far, of 32 kx3 games planned.'))
        for kw, keep, q, size in cases:
            t, man, games = self.run_dir(deals=2, **kw)
            text = self.rewrite(t, games[:keep])
            lines = text.splitlines()
            self.assertEqual([l for l in lines if l.startswith('Question: ')], [q], (kw, keep))
            self.assertEqual([l for l in lines if l.startswith('Size: ')], [size], (kw, keep))
            self.assertLess(lines.index(q), lines.index(size))
            self.assertLess(lines.index(size), min(i for i, l in enumerate(lines) if '%' in l and not l.startswith('|')), 'no number before the size')

    def test_every_list_has_one_row_with_its_games_its_score_and_its_range(self):
        for kw in (dict(deals=2), dict(deals=5, win=lambda o, d, s: 'deck')):  # the second has a range clipped at 100%
            t, man, games, text = self.build(**kw)
            for opp in PANEL:
                s = T.x_scores(games, lambda g, o=opp: g['opp'] == o)
                p, lo, hi = wilson95(s)
                self.assertEqual([l for l in text.splitlines() if l.startswith(f'| {opp} ')], [f'| {opp} | {len(s)} | {pc(p)} | {pc(lo)} to {pc(hi)} |'], opp)
        self.assertIn('| t-altaria | 10 | 100.0% | 72.2% to 100.0% |', text.splitlines())

    def test_a_single_game_is_one_game_and_not_one_games(self):
        t, man, games = self.run_dir(deals=1)
        one = [g for g in games if g['arm'] == 'X'][:1]
        text = self.rewrite(t, one)
        p, lo, hi = wilson95(T.x_scores(one))
        self.assertEqual([l[:len(f'my-list scored **{pc(p)}** over **1 game** (')] for l in text.splitlines() if l.startswith('my-list scored **')],
                         [f'my-list scored **{pc(p)}** over **1 game** ('])
        self.assertEqual([l for l in text.splitlines() if l.startswith('my-list scored **')],
                         [f'my-list scored **{pc(p)}** over **1 game** (games from 1 of the 8 public lists so far): probably between {pc(lo)} and {pc(hi)} '
                          '(95% interval; this range refers to this 1 kx3 game). A win counts 1, a tie 1/2, a loss 0.'])
        self.assertIn('Size: 1 kx3 game + 0 cheap km3 baseline games so far, of 16 kx3 games + 16 cheap km3 baseline games planned.', text)
        self.assertIn('in these 1 game;', text)
        self.assertIn(f'- When my-list went first: {pc(p)} over 1 game (', text)

    def test_the_score_line_has_the_mean_the_games_the_shape_and_the_range_it_refers_to(self):
        t, man, games, text = self.build(deals=2)
        p, lo, hi = wilson95(T.x_scores(games))
        self.assertEqual([l for l in text.splitlines() if ' scored **' in l and l.startswith('my-list')],
                         [f'my-list scored **{pc(p)}** over **32 games** (2 deals x 2 seats against each of the 8 public lists): probably between {pc(lo)} and {pc(hi)} '
                          f'(95% interval; this range refers to these 32 kx3 games). A win counts 1, a tie 1/2, a loss 0.'])

    def test_a_partial_run_counts_what_is_there_and_names_the_lists_it_has_games_from(self):
        t, man, games = self.run_dir(deals=2)
        text = self.rewrite(t, games[:37])  # four lists complete and two kx3 games from the fifth
        xs = T.x_scores(games[:37])
        self.assertEqual(len(xs), 18)
        p, lo, hi = wilson95(xs)
        self.assertIn(f'my-list scored **{pc(p)}** over **18 games** (games from 5 of the 8 public lists so far): probably between {pc(lo)} and {pc(hi)} '
                      f'(95% interval; this range refers to these 18 kx3 games). A win counts 1, a tie 1/2, a loss 0.', text.splitlines())
        rows = [l for l in text.splitlines() if l.startswith('| t-')]
        self.assertEqual(rows[4].split(' | ')[:2], ['| t-sceptile', '2'])
        self.assertEqual(rows[5:], ['| t-suicune | 0 | n/a | n/a |', '| t-vespiquen | 0 | n/a | n/a |', '| t-weezing | 0 | n/a | n/a |'])

    def test_before_any_kx3_game_the_section_says_so_and_prints_no_score(self):
        t, man, games = self.run_dir(deals=1)
        text = self.rewrite(t, [g for g in games if g['arm'] == 'ref'])
        sec = self.part(text, '## What it says')
        self.assertIn('Size: 0 kx3 games + 16 cheap km3 baseline games so far, of 16 kx3 games + 16 cheap km3 baseline games planned.', sec)
        self.assertIn('\nNo kx3 game has finished yet.\n', sec)
        self.assertNotIn('scored', sec)
        self.assertNotIn('nan', text.lower())
        self.assertIn('No deal has been played both ways yet.', sec)
        self.assertIn('**Nothing to say yet: no kx3 game has finished.**', self.part(text, "## What these numbers can and can't say"))
        self.assertIn('- When my-list went first: no games yet', text)
        self.assertIn('- When my-list went second: no games yet', text)


# ---------------------------------------------------------------------------------------------------------- the gain over km3
class TheGain(Pages):
    def head(self, games):
        n, m, half, sx, sref = gain(games)
        return (f'On the same deals, kx3 scored **{points(m)} points** compared with km3 piloting this deck (kx3 {pc(sx)}, km3 on this deck {pc(sref)}, over {n} paired games: '
                f'each a deal and seat played by both pilots, so {n} kx3 games + {n} cheap km3 baseline games), '
                f'give or take {100 * half:.1f} points (95% interval; this range refers to those {n} paired games).')

    def range_runs(self, games):
        n, m, half, sx, sref = gain(games)
        return n, m - half, m + half, f'That range runs from {points(m - half)} to {points(m + half)} points, '

    def gain_section(self, text):
        return text.split('### How much better')[1].split('\n## ')[0]

    def test_a_range_that_includes_no_gain_says_what_the_games_do_and_do_not_show(self):
        t, man, games, text = self.build(deals=3)
        n, lo, hi, run = self.range_runs(games)
        self.assertTrue(lo <= 0 <= hi, 'this data is meant to include no gain')
        self.assertEqual(text.splitlines().count(self.head(games)), 1)
        self.assertEqual(text.splitlines().count(
            run + f'which includes no gain at all: these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                  f'They do argue against a gain much larger than {100 * hi:.1f} points or a loss much larger than {100 * abs(lo):.1f} points; a smaller difference needs more deals.'), 1)

    def test_a_range_wholly_above_zero_says_better_and_does_not_say_by_how_much(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', ref_win=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')
        n, lo, hi, run = self.range_runs(games)
        self.assertTrue(lo > 0, 'this data is meant to be a clear gain')
        self.assertEqual(text.splitlines().count(self.head(games)), 1)
        self.assertEqual(text.splitlines().count(run + f'which does not include no gain: on these {n} paired games kx3 did better than km3. '
                                                       f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.'), 1)

    def test_a_range_wholly_below_zero_says_worse(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'opp' if (o + d) % 5 else 'deck', ref_win=lambda o, d, s: 'deck' if (o + d + s) % 4 else 'opp')
        n, lo, hi, run = self.range_runs(games)
        self.assertTrue(hi < 0, 'this data is meant to be a clear loss')
        self.assertEqual(text.splitlines().count(self.head(games)), 1)
        self.assertEqual(text.splitlines().count(run + f'which does not include no gain: on these {n} paired games kx3 did worse than km3. '
                                                       f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.'), 1)

    def test_a_range_wider_than_the_whole_scale_says_the_paired_games_are_too_few_and_prints_no_range(self):
        t, man, games = self.run_dir(deals=1, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if s == 0 else 'opp')
        two = [g for g in games if g['opp'] == PANEL[0]]  # both seats, both arms: two paired games, the differences 0 and +1
        text = self.rewrite(t, two)
        n, m, half, sx, sref = gain(two)
        self.assertEqual((n, m), (2, 0.5))
        self.assertGreater(2 * half, 2, 'this data is meant to give a range wider than the whole possible scale')
        sec = self.gain_section(text)
        self.assertIn(self.head(two), sec.splitlines(), 'the figure and its give-or-take are still shown')
        self.assertEqual([l for l in sec.splitlines() if l.startswith('That range')],
                         ['That range is wider than the whole possible scale (-100 to +100 points): 2 paired games are too few to say anything about the gain yet.'])
        for s in ('That range runs', 'includes no gain', 'does not include', 'cut at the ends', 'argue against', 'did better', 'did worse'):
            self.assertNotIn(s, sec)

    def test_a_range_that_runs_past_the_top_of_the_scale_is_cut_there_and_says_so(self):
        # kx3 wins everything; km3 wins the first game of three lists and loses the rest: 13 differences of +1 and 3 of 0, a range that ends at +102.7 and is cut at +100
        t, man, games, text = self.build(deals=1, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if (o < 3 and s == 0) else 'opp')
        n, m, half, sx, sref = gain(games)
        self.assertEqual(n, 16)
        self.assertTrue(m + half > 1 and 2 * half < 2, 'this data is meant to run past +100 without being wider than the whole scale')
        self.assertEqual([l for l in self.gain_section(text).splitlines() if l.startswith('That range')],
                         [f'That range runs from {points(m - half)} to +100.0 points (cut at the ends of the possible scale), which does not include no gain: on these 16 paired games '
                          'kx3 did better than km3. It does not say by exactly how much: that part of the range is as wide as 16 paired games make it.'])
        self.assertNotIn('+102', text)

    def test_a_range_that_runs_past_the_bottom_of_the_scale_is_cut_there_and_says_so(self):
        t, man, games, text = self.build(deals=1, win=lambda o, d, s: 'opp', ref_win=lambda o, d, s: 'opp' if (o < 3 and s == 0) else 'deck')
        n, m, half, sx, sref = gain(games)
        self.assertEqual(n, 16)
        self.assertTrue(m - half < -1 and 2 * half < 2)
        self.assertEqual([l for l in self.gain_section(text).splitlines() if l.startswith('That range')],
                         [f'That range runs from -100.0 to {points(m + half)} points (cut at the ends of the possible scale), which does not include no gain: on these 16 paired games '
                          'kx3 did worse than km3. It does not say by exactly how much: that part of the range is as wide as 16 paired games make it.'])
        self.assertNotIn('-102', text)

    def test_a_range_inside_the_scale_is_not_said_to_be_cut_nor_too_wide(self):
        t, man, games, text = self.build(deals=3)
        n, lo, hi, run = self.range_runs(games)
        self.assertTrue(-1 < lo < hi < 1)
        self.assertNotIn('cut at the ends', text)
        self.assertNotIn('wider than the whole', text)

    def test_one_comparison_gets_no_range_and_is_not_called_the_same_difference_every_time(self):
        t, man, games = self.run_dir(deals=1)
        one = [g for g in games if g['opp'] == PANEL[0] and g['seat'] == 0]
        text = self.rewrite(t, one)
        n, m = 1, SC[one[1]['winner']] - SC[one[0]['winner']]
        self.assertEqual({g['arm'] for g in one}, {'X', 'ref'})
        line = [l for l in text.splitlines() if l.startswith('On the same deals')]
        self.assertEqual(line, [f"On the same deals, kx3 scored **{points(m)} points** compared with km3 piloting this deck (kx3 {pc(SC[one[1]['winner']])}, "
                                f"km3 on this deck {pc(SC[one[0]['winner']])}, over 1 paired game: each a deal and seat played by both pilots, so 1 kx3 game + 1 cheap km3 baseline game); "
                                'with one comparison no interval can be given.'])
        self.assertNotIn('every one of the', text)
        self.assertNotIn('give or take', text.split('### How much better')[1].split('\n## ')[0])
        self.assertNotIn('That range', text)

    def test_no_spread_at_all_is_said_as_such_and_gets_no_range(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck')
        line = [l for l in text.splitlines() if l.startswith('On the same deals')]
        self.assertEqual(line, ['On the same deals, kx3 scored **+0.0 points** compared with km3 piloting this deck (kx3 100.0%, km3 on this deck 100.0%, over 48 paired games: '
                                'each a deal and seat played by both pilots, so 48 kx3 games + 48 cheap km3 baseline games); '
                                'every one of the 48 comparisons gave the same difference, so no spread can be estimated from them.'])
        self.assertNotIn('That range runs', text)

    def test_without_the_baseline_the_gain_is_not_mentioned_at_all(self):
        t, man, games, text = self.build(deals=3, paired=False)
        for s in ('same deals', 'km3 on this deck', 'How much better', 'played both ways', 'paired game', 'That range'):
            self.assertNotIn(s, text)

    def test_every_interval_on_the_page_says_which_games_it_refers_to_exactly_once(self):
        t, man, games, text = self.build(deals=3)
        for sentence in ('(95% interval; this range refers to these 48 kx3 games)', '(95% interval; this range refers to those 48 paired games)',
                         "Each row's range refers only to the kx3 games against that list (the row's games column)", 'Each range refers only to the kx3 games on its line',
                         'A win counts 1, a tie 1/2, a loss 0.'):
            self.assertEqual(text.count(sentence), 1, sentence)
        self.assertEqual(text.count('(95% interval'), 2)
        self.assertEqual(text.count('refers'), 4)

    def test_the_two_sentences_under_the_tables_say_what_a_row_and_a_line_can_and_cannot_tell(self):
        t, man, games, text = self.build(deals=3)
        self.assertIn("\nEach row's range refers only to the kx3 games against that list (the row's games column); with so few games it can tell a very easy or a very hard list "
                      "from an even one, not two similar lists from each other.\n", text)
        self.assertIn('\nEach range refers only to the kx3 games on its line; a few dozen games can show a large first-or-second difference, not a small one.\n', text)


class GainRangeNote(T.Timed):
    """The sentences about the paired-gain range, word for word, from the one function that writes them for both pages (gain_range_note(pilot, ref, n, mean, half): the
    range is mean +- half, in fractions of a score, over n paired games), with round numbers so that each case can be written down."""

    def note(self, n, m, half):
        return sr.gain_range_note('kx3', 'km3', n, m, half)

    BETTER = 'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.'

    def test_a_range_that_includes_zero_says_the_games_show_neither_a_gain_nor_a_loss(self):
        self.assertEqual(self.note(50, 0.05, 0.25),
                         'That range runs from -20.0 to +30.0 points, which includes no gain at all: these 50 paired games do not show that kx3 plays this deck better than km3, '
                         'and do not show that it plays it worse. They do argue against a gain much larger than 30.0 points or a loss much larger than 20.0 points; '
                         'a smaller difference needs more deals.')

    def test_a_range_wholly_above_zero_says_better_and_one_wholly_below_says_worse(self):
        self.assertEqual(self.note(50, 0.3, 0.1), 'That range runs from +20.0 to +40.0 points, which does not include no gain: on these 50 paired games kx3 did better than km3. '
                                                  + self.BETTER.format(n=50))
        self.assertEqual(self.note(50, -0.3, 0.1), 'That range runs from -40.0 to -20.0 points, which does not include no gain: on these 50 paired games kx3 did worse than km3. '
                                                   + self.BETTER.format(n=50))

    def test_the_pilots_in_the_sentence_are_the_ones_given(self):
        text = sr.gain_range_note('kz9', 'kr1', 12, 0.3, 0.1)
        self.assertIn('kz9 did better than kr1', text)
        self.assertNotIn('kx3', text)
        self.assertNotIn('km3', text)
        text = sr.gain_range_note('kz9', 'kr1', 12, 0.0, 0.1)
        self.assertIn('do not show that kz9 plays this deck better than kr1, and do not show that it plays it worse', text)

    def test_a_range_as_wide_as_the_whole_scale_or_wider_says_the_paired_games_are_too_few(self):
        wider = 'That range is wider than the whole possible scale (-100 to +100 points): {n} paired games are too few to say anything about the gain yet.'
        self.assertEqual(self.note(2, 0.5, 6.35), wider.format(n=2))
        self.assertEqual(self.note(7, 0.0, 1.0), wider.format(n=7), 'a range exactly as wide as the scale is already too wide to say anything')
        self.assertEqual(self.note(3, -0.4, 3.0), wider.format(n=3), 'wherever it sits')
        just_inside = self.note(7, 0.0, 0.999)
        self.assertTrue(just_inside.startswith('That range runs from -99.9 to +99.9 points, which includes no gain at all'), just_inside)
        self.assertNotIn('wider than', just_inside)
        self.assertNotIn('cut at the ends', just_inside)

    def test_a_range_past_an_end_of_the_scale_is_cut_there_and_says_so(self):
        top = self.note(16, 0.8, 0.3)
        self.assertEqual(top, 'That range runs from +50.0 to +100.0 points (cut at the ends of the possible scale), which does not include no gain: on these 16 paired games '
                              'kx3 did better than km3. ' + self.BETTER.format(n=16))
        bottom = self.note(16, -0.8, 0.3)
        self.assertEqual(bottom, 'That range runs from -100.0 to -50.0 points (cut at the ends of the possible scale), which does not include no gain: on these 16 paired games '
                                 'kx3 did worse than km3. ' + self.BETTER.format(n=16))
        across = self.note(16, 0.5, 0.6)  # the cut end is also what the "argue against" figure is taken from
        self.assertEqual(across, 'That range runs from -10.0 to +100.0 points (cut at the ends of the possible scale), which includes no gain at all: these 16 paired games '
                                 'do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. They do argue against a gain much larger than '
                                 '100.0 points or a loss much larger than 10.0 points; a smaller difference needs more deals.')

    def test_a_range_that_ends_exactly_at_an_end_of_the_scale_is_not_called_cut(self):
        text = self.note(16, 0.5, 0.5)
        self.assertTrue(text.startswith('That range runs from +0.0 to +100.0 points, which includes no gain at all'), text)
        self.assertNotIn('cut at the ends', text)
        text = self.note(16, -0.5, 0.5)
        self.assertTrue(text.startswith('That range runs from -100.0 to +0.0 points, which includes no gain at all'), text)
        self.assertNotIn('cut at the ends', text)

    def test_a_lower_bound_that_rounds_to_plus_zero_is_called_just_above_it(self):
        text = self.note(50, 0.0203, 0.02)  # the range starts at +0.03 points
        self.assertEqual(text, 'That range runs from just above +0.0 to +4.0 points, which does not include no gain: on these 50 paired games kx3 did better than km3. '
                               + self.BETTER.format(n=50))
        near = self.note(50, 0.0212, 0.02)  # +0.12 points rounds to +0.1, which is a number and is printed as one
        self.assertTrue(near.startswith('That range runs from +0.1 to +4.1 points, which does not include no gain'), near)
        self.assertNotIn('just above', near)

    def test_an_upper_bound_that_rounds_to_plus_zero_is_called_just_below_it(self):
        text = self.note(50, -0.0203, 0.02)
        self.assertEqual(text, 'That range runs from -4.0 to just below +0.0 points, which does not include no gain: on these 50 paired games kx3 did worse than km3. '
                               + self.BETTER.format(n=50))
        near = self.note(50, -0.0212, 0.02)
        self.assertTrue(near.startswith('That range runs from -4.1 to -0.1 points, which does not include no gain'), near)
        self.assertNotIn('just below', near)

    def test_a_range_that_just_includes_zero_never_prints_minus_zero(self):
        text = self.note(50, 0.0197, 0.02)  # the range starts at -0.03 points
        self.assertTrue(text.startswith('That range runs from +0.0 to +4.0 points, which includes no gain at all'), text)
        self.assertNotIn('-0.0', text)
        self.assertNotIn('just above', text)
        text = self.note(50, -0.0197, 0.02)
        self.assertTrue(text.startswith('That range runs from -4.0 to +0.0 points, which includes no gain at all'), text)
        self.assertNotIn('-0.0 ', text)


class CountsNameTheirPilot(T.Timed):
    """Every count on a page says whose games it counts, in the singular at one: the reporting rule is kx3 games v all games, never a bare number."""

    def test_a_count_of_games_names_its_pilot_and_is_singular_only_at_one(self):
        for n, want in ((0, '0 kx3 games'), (1, '1 kx3 game'), (2, '2 kx3 games'), (80, '80 kx3 games')):
            self.assertEqual(sr.kg(n, 'kx3'), want)
        for n, want in ((0, '0 cheap km3 baseline games'), (1, '1 cheap km3 baseline game'), (2, '2 cheap km3 baseline games'), (80, '80 cheap km3 baseline games')):
            self.assertEqual(sr.kg(n, 'km3', True), want)

    def test_the_name_is_the_pilots_whatever_it_is(self):
        self.assertEqual(sr.kg(1, 'kz9'), '1 kz9 game')
        self.assertEqual(sr.kg(3, 'kr1', True), '3 cheap kr1 baseline games')

    def test_other_counts_are_singular_at_one_too(self):
        self.assertEqual([sr.plural(n, 'paired game') for n in (0, 1, 2)], ['0 paired games', '1 paired game', '2 paired games'])
        self.assertEqual([sr.plural(n, 'deal') for n in (1, 5)], ['1 deal', '5 deals'])
        self.assertEqual([sr.games_word(n) for n in (1, 32)], ['1 game', '32 games'])


# ---------------------------------------------------------------------------------------------------------- who went first
class WhoWentFirst(Pages):
    def first_apart_from_seat(self):
        """Games whose first player has nothing to do with the seat and whose results depend on who went first."""
        t, man, games = self.run_dir(deals=2)
        for g in games:
            if g['arm'] == 'X':
                k = PANEL.index(g['opp']) + g['seat']
                g['first'] = 'deck' if (PANEL.index(g['opp']) + g['deal']) % 2 == 0 else 'opp'
                if g['first'] == 'deck':
                    g['winner'] = 'opp' if k % 4 == 0 else 'deck'
                else:
                    g['winner'] = 'tie' if k % 4 == 0 else ('deck' if k % 4 == 1 else 'opp')
        return t, games

    def line(self, label, scores):
        p, lo, hi = wilson95(scores)
        return f'- When my-list {label}: {pc(p)} over {len(scores)} games ({pc(lo)} to {pc(hi)})'

    def test_the_two_lines_split_the_games_by_who_went_first_and_not_by_seat(self):
        t, games = self.first_apart_from_seat()
        first = T.x_scores(games, lambda g: g['first'] == 'deck')
        second = T.x_scores(games, lambda g: g['first'] == 'opp')
        seat0 = T.x_scores(games, lambda g: g['seat'] == 0)
        self.assertNotEqual((sum(first), len(first)), (sum(second), len(second)), 'the two halves must differ, or a swap of the labels cannot show')
        self.assertNotEqual((sum(first), len(first)), (sum(seat0), len(seat0)), 'the first player must differ from the seat, or a split by seat cannot show')
        text = self.rewrite(t, games)
        sec = self.part(text, '## Who went first')
        self.assertEqual([l for l in sec.splitlines() if l.startswith('- ')], [self.line('went first', first), self.line('went second', second)])

    def test_a_side_with_no_games_says_so(self):
        t, games = self.first_apart_from_seat()
        for g in games:
            g['first'] = 'deck'
        sec = self.part(self.rewrite(t, games), '## Who went first')
        self.assertEqual([l for l in sec.splitlines() if l.startswith('- ')],
                         [self.line('went first', T.x_scores(games)), '- When my-list went second: no games yet'])


# ---------------------------------------------------------------------------------------------------------- the time it took
class TimeSection(Pages):
    def time_lines(self, walls, **kw):
        t, man, games = self.run_dir(deals=2, **kw)
        for g, w in zip([g for g in games if g['arm'] == 'X'], walls):
            g['wall_s'] = w
        return t, self.part(self.rewrite(t, games), '## The time it took').strip().splitlines()

    def test_the_median_is_the_median_and_a_short_mean_has_no_about(self):
        t, lines = self.time_lines([20.0] * 31 + [1000.0])  # mean 50.625, median 20
        self.assertEqual(lines[0], 'kx3 took 51 s a game on average, median 20 s, slowest 1000 s, with 2 threads going at once. km3 playing this deck took 1.0 s a game.')

    def test_a_long_mean_is_also_said_in_minutes_and_the_median_stays_the_median(self):
        t, lines = self.time_lines([100.0] * 20 + [400.0] * 11 + [1000.0])  # mean 231.25, median 100
        self.assertEqual(lines[0], 'kx3 took 231 s a game on average (about 4 min), median 100 s, slowest 1000 s, with 2 threads going at once. km3 playing this deck took 1.0 s a game.')

    def test_about_starts_at_a_mean_of_ninety_seconds(self):
        self.assertTrue(self.time_lines([89.0] * 32)[1][0].startswith('kx3 took 89 s a game on average, median'))
        self.assertTrue(self.time_lines([90.0] * 32)[1][0].startswith('kx3 took 90 s a game on average (about 2 min), median'))

    def test_without_the_baseline_the_time_line_does_not_mention_km3_games(self):
        t, lines = self.time_lines([20.0] * 32, paired=False)
        self.assertEqual(lines[0], 'kx3 took 20 s a game on average, median 20 s, slowest 20 s, with 2 threads going at once.')

    def test_a_running_time_of_days_is_in_days(self):
        t, man, games = self.run_dir(deals=1)
        write(os.path.join(t, 'run_log.jsonl'), '\n'.join(json.dumps(e) for e in (dict(event='start', threads=2), dict(event='stop', elapsed_s=3 * 86400.0))) + '\n')
        self.assertIn('Running time from the run log: 3.0 days over 1 sitting, for 32 games in all: 16 kx3 games + 16 cheap km3 baseline games.\n', sr.write_slow_report(t))

    def test_the_running_time_adds_up_the_sittings_and_the_estimate_divides_by_the_most_threads_used(self):
        t, man, games = self.run_dir(deals=1)
        log = [dict(event='start', threads=2), dict(event='stop', elapsed_s=3600.0), dict(event='start', threads=3), dict(event='stop', elapsed_s=7200.0)]
        write(os.path.join(t, 'run_log.jsonl'), ''.join(json.dumps(e) + '\n' for e in log))
        self.assertIn('Running time from the run log: 3.0 h over 2 sittings, for 32 games in all: 16 kx3 games + 16 cheap km3 baseline games.\n', sr.write_slow_report(t))
        write(os.path.join(t, 'run_log.jsonl'), ''.join(json.dumps(e) + '\n' for e in log[:3]))  # the last sitting never closed
        total = sum(g['wall_s'] for g in games)
        self.assertEqual(total, 16 * 200.0 + 16 * 1.0)
        self.assertIn('estimated from the game times and the thread count: 18 min, for 32 games in all: 16 kx3 games + 16 cheap km3 baseline games.\n',
                      sr.write_slow_report(t))  # 3216 s on 3 threads: 1072 s; on 2 it would be 27 min

    def test_the_running_time_names_each_pilots_games_in_the_total_whatever_has_been_played(self):
        t, man, games = self.run_dir(deals=1)
        for keep, want in (([games[1]], 'for 1 game in all: 1 kx3 game + 0 cheap km3 baseline games.'), (games[:3], 'for 3 games in all: 1 kx3 game + 2 cheap km3 baseline games.'),
                           (games[:2], 'for 2 games in all: 1 kx3 game + 1 cheap km3 baseline game.')):
            text = self.rewrite(t, keep)
            self.assertIn(f'Running time from the run log: 2.0 h over 1 sitting, {want}\n', text, want)
        write(os.path.join(t, 'run_log.jsonl'), json.dumps(dict(event='start', threads=2)) + '\n')  # and the same words when the time is only an estimate
        self.assertIn('estimated from the game times and the thread count: 2 min, for 2 games in all: 1 kx3 game + 1 cheap km3 baseline game.\n', self.rewrite(t, games[:2]))  # 201 s on 2 threads

    def test_a_run_without_the_comparison_still_counts_the_baseline_games_it_played_in_the_total(self):
        t, man, games, text = self.build(deals=1, paired=False)
        self.assertIn('Running time from the run log: 2.0 h over 1 sitting, for 32 games in all: 16 kx3 games + 16 cheap km3 baseline games.\n', text)

    def test_with_no_kx3_game_the_time_section_says_so_too(self):
        t, man, games = self.run_dir(deals=1)
        text = self.rewrite(t, [g for g in games if g['arm'] == 'ref'])
        self.assertEqual(self.part(text, '## The time it took').strip().splitlines()[0], 'No kx3 game has finished yet.')


# ---------------------------------------------------------------------------------------------------------- games that failed
class ErrorParagraph(Pages):
    K2, K1, K3 = 'my-list|t-altaria|0|0|X', 'my-list|t-blaziken|0|0|X', 'my-list|t-hydreigon|0|0|X'

    def with_errors(self, errors, unfinished, keyless=False):
        t, man, games = self.run_dir(deals=2, errors=errors)
        if keyless:
            with open(os.path.join(t, 'errors.jsonl'), 'a', encoding='utf-8') as f:
                f.write(json.dumps({'error': 'a line with no key'}) + '\n')
        return self.rewrite(t, [g for g in games if g['key'] not in unfinished])

    def paragraph(self, text):
        return [l for l in text.splitlines() if 'could not be finished' in l]

    def test_several_failing_games_are_counted_by_game_and_the_first_message_of_the_first_one_is_shown(self):
        text = self.with_errors([(self.K2, 'first-msg'), (self.K1, 'once-msg'), (self.K3, 'flaky'), (self.K2, 'second-msg')], {self.K2, self.K1}, keyless=True)
        para = self.paragraph(text)
        self.assertEqual(len(para), 1)
        self.assertEqual(para[0], '2 games could not be finished and are left out of every number below (first: `' + self.K2 + '`, 2 tries: first-msg). '
                                  'A game that crashes is not a loss, so if the same card crashes them the score leans towards games without it. '
                                  'At least one failed every time it was tried, so resuming will not fix it.')
        self.assertNotIn('trys', text)
        self.assertNotIn('second-msg', text)
        self.assertNotIn('flaky', text, 'a game that was played on a later try is not listed')
        self.assertNotIn('no key', text)

    def test_games_each_tried_once_may_still_be_fixed_by_resuming(self):
        text = self.with_errors([(self.K2, 'one'), (self.K1, 'two')], {self.K2, self.K1})
        self.assertRegex(self.paragraph(text)[0], re.escape('2 games could not be finished and are left out of every number below (first: `' + self.K2 + '`, 1 try: one). ')
                         + r'A game that crashes.*games without it\. A resumed run tries them again\.$')
        self.assertNotIn('every time it was tried', text)

    def test_a_game_tried_twice_is_enough_to_say_resuming_will_not_fix_it(self):
        text = self.with_errors([(self.K1, 'a'), (self.K1, 'b')], {self.K1})
        self.assertTrue(self.paragraph(text)[0].endswith('At least one failed every time it was tried, so resuming will not fix it.'))
        self.assertTrue(self.paragraph(text)[0].startswith('1 game could not be finished and is left out of every number below (first: `' + self.K1 + '`, 2 tries: a). '))
        text = self.with_errors([(self.K1, 'a'), (self.K1, 'b'), (self.K1, 'c')], {self.K1})
        self.assertIn('`, 3 tries: a). ', self.paragraph(text)[0])
        text = self.with_errors([(self.K1, 'a')], {self.K1})
        self.assertIn('`, 1 try: a). ', self.paragraph(text)[0], 'one try is "1 try", not "1 tries"')
        self.assertNotIn('1 tries', text)

    def test_a_message_is_cut_at_two_hundred_characters(self):
        text = self.with_errors([(self.K1, 'a' * 150 + 'b' * 150)], {self.K1})
        self.assertIn('a' * 150 + 'b' * 50 + ')', text)
        self.assertNotIn('b' * 51, text)

    def test_the_note_is_the_first_thing_the_console_shows_after_the_banner(self):
        text = self.with_errors([(self.K2, 'x'), (self.K2, 'y')], {self.K2})
        lines = sr.console_lines(text)
        self.assertTrue(lines[0].startswith('PARTIAL: 63 of 64 games played so far'), lines[0])
        self.assertTrue(lines[1].startswith('1 game could not be finished and is left out of every number below (first: ' + self.K2), lines[1])
        self.assertNotIn('`', lines[1])


class DuplicatesAndTornLines(Pages):
    def test_a_kx3_game_written_twice_is_counted_once_and_its_first_record_stands(self):
        t, man, games, clean = self.build(deals=2)
        x = next(g for g in games if g['arm'] == 'X')
        again = dict(x, winner='opp' if x['winner'] != 'opp' else 'deck')
        with open(os.path.join(t, 'games.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(again) + '\n')
            f.write('{"key": "my-list|t-weezing|1|1|X", "deck": "my-')  # torn by the 6:30 stop
        self.assertEqual(sr.write_slow_report(t), clean)
        kept = {g['key']: g for g in sr.load_games(t)}
        self.assertEqual(len(kept), 64)
        self.assertEqual(kept[x['key']]['winner'], x['winner'])

    def test_a_record_without_a_key_is_not_a_game(self):
        t, man, games, clean = self.build(deals=2)
        with open(os.path.join(t, 'games.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'deck': 'my-list', 'winner': 'deck'}) + '\n')
        self.assertEqual(sr.write_slow_report(t), clean)


# ---------------------------------------------------------------------------------------------------------- what was run, held-out decks, the engineering report
class WhatWasRun(Pages):
    def test_the_seed_line_shows_the_registered_base_and_stride(self):
        t, man, games = self.run_dir(deals=1)
        man.update(seed_base=24_637_100_000, pair_stride=12_345)
        T.rewrite_manifest(t, man)
        self.assertIn('- 1 deal x 2 seats; seeds `24637100000 + p x 12345 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.',
                      sr.write_slow_report(t).splitlines())

    def test_the_pilots_the_build_the_deck_file_and_the_registration_are_named_in_these_words(self):
        t, man, games, text = self.build(deals=1)
        lines = text.splitlines()
        for want in ('- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `/home/dacz8976/kx/strength` sha256 `5a8f5c83a791`.',
                     '- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec',
                     '- Deck file `decks/events/my-list.txt` sha256 `cccccccccccc`; the file is committed.',
                     f'- Registered 2026-10-10T10:00:00Z, before any game; manifest sha256 `{T.sha(os.path.join(t, "manifest.json"))[:16]}`; repository commit `abc123`; '
                     'pin `rl/strength/slow_report_pin.json`.'):
            self.assertEqual(lines.count(want), 1, want)
        self.assertTrue(text.endswith('from one seed.\n') and not text.endswith('\n\n'), 'one newline at the end of the page')

    def test_the_engineering_report_is_pointed_at_only_when_it_exists(self):
        t, man, games = self.run_dir(deals=1)
        self.assertNotIn('REPORT.md', sr.write_slow_report(t))
        write(os.path.join(t, 'REPORT.md'), '# the engineering report\n')
        self.assertEqual(sr.write_slow_report(t).splitlines().count(
            '- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.'), 1)

    def test_a_held_out_deck_is_named_with_the_sentence_that_the_lock_is_unchanged(self):
        t, man, games = self.run_dir()
        man['heldout_in_run'] = ['03-wailord', 'my-list']
        T.rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        self.assertEqual(text.splitlines().count('- Held-out decks in this run: 03-wailord, my-list. Allowed because this is a `use` report, not development evidence; '
                                                  'the held-out lock is unchanged.'), 1)
        for word in ('lifted', 'unlock', 'opened', 'released', 'removed'):
            self.assertNotIn(word, text.lower())

    def test_a_run_with_no_held_out_deck_does_not_mention_the_lock(self):
        t, man, games, text = self.build()
        self.assertNotIn('eld-out', text)
        self.assertNotIn('lock', text)

    def registered_line(self, t, text):
        msha = T.sha(os.path.join(t, 'manifest.json'))[:16]
        tail = f'; manifest sha256 `{msha}`; repository commit `abc123`; pin `rl/strength/slow_report_pin.json`.'
        lines = [l for l in text.splitlines() if l.startswith('- Registered ')]
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].endswith(tail), lines[0])
        return lines[0][:-len(tail)]

    def test_a_game_that_started_before_the_registration_time_is_said_to_have_done_so(self):
        t, man, games = self.run_dir(deals=1)
        self.assertEqual(man['created_at'], '2026-10-10T10:00:00Z')
        games[3]['started_at'] = '2026-10-10T09:58:00Z'
        games[5]['started_at'] = '2026-10-10T09:59:59Z'  # two games before the registration: the earliest is the one named
        text = self.rewrite(t, games)
        self.assertEqual(self.registered_line(t, text), '- Registered 2026-10-10T10:00:00Z, **but a game started at 2026-10-10T09:58:00Z, BEFORE the registration time**')
        self.assertNotIn('before any game', text)

    def test_one_second_before_the_registration_is_before_it_and_the_same_second_is_not(self):
        t, man, games = self.run_dir(deals=1)
        for g in games:
            g['started_at'] = '2026-10-10T10:00:00Z'
        text = self.rewrite(t, games)
        self.assertEqual(self.registered_line(t, text), '- Registered 2026-10-10T10:00:00Z, before any game')
        games[0]['started_at'] = '2026-10-10T09:59:59Z'
        text = self.rewrite(t, games)
        self.assertEqual(self.registered_line(t, text), '- Registered 2026-10-10T10:00:00Z, **but a game started at 2026-10-10T09:59:59Z, BEFORE the registration time**')

    def test_games_with_no_start_time_cannot_show_a_game_before_the_registration(self):
        t, man, games = self.run_dir(deals=1)
        for g in games:
            del g['started_at']
        text = self.rewrite(t, games)
        self.assertEqual(self.registered_line(t, text), '- Registered 2026-10-10T10:00:00Z, before any game')
        games[2]['started_at'] = ''  # an empty one is no start time either; a later real one is read as it is
        games[4]['started_at'] = '2026-10-10T10:30:00Z'
        text = self.rewrite(t, games)
        self.assertEqual(self.registered_line(t, text), '- Registered 2026-10-10T10:00:00Z, before any game')
        self.assertEqual(self.registered_line(t, self.rewrite(t, [])), '- Registered 2026-10-10T10:00:00Z, before any game', 'no game at all')

    def test_the_time_of_a_game_from_a_partial_run_that_started_early_is_found_too(self):
        t, man, games = self.run_dir(deals=2)
        games[30]['started_at'] = '2026-10-09T23:00:00Z'
        text = self.rewrite(t, games[:37])
        self.assertIn('PARTIAL', text)
        self.assertIn('**but a game started at 2026-10-09T23:00:00Z, BEFORE the registration time**', self.registered_line(t, text))


class HeldOutRunEndToEnd(T.LiveWorld):
    """With the real registry and copies of the real lists (LiveWorld): the synthetic registry of World holds made-up held-out decks, which the real held-out deck is not."""

    def test_a_real_held_out_registration_is_reported_as_used_and_leaves_the_lock_file_as_it_was(self):
        held = json.loads(read(os.path.join(HERE, 'heldout.json')))['decks'][0]
        registry = json.loads(read(os.path.join(HERE, 'decks.json')))['decks']
        self.make(deck_text=read(os.path.join(ROOT, *registry[held].split('/'))))
        lock = os.path.join(HERE, 'heldout.json')

        def state():
            st = os.stat(lock)
            return st.st_mtime_ns, st.st_size, read(lock)
        before = state()
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        self.assertIn('- Held-out decks in this run: my-list. Allowed because this is a `use` report, not development evidence; the held-out lock is unchanged.',
                      read(os.path.join(self.rundir(), 'SLOW_REPORT.md')).splitlines())
        self.assertEqual(state(), before)


# ---------------------------------------------------------------------------------------------------------- the lines echoed to the terminal
class ConsoleEcho(Pages):
    def test_a_finished_page_echoes_the_question_the_size_and_the_numbers_as_plain_text(self):
        t, man, games, text = self.build(deals=2)
        lines = sr.console_lines(text)
        p, lo, hi = wilson95(T.x_scores(games))
        self.assertEqual(len(lines), 5, lines)
        self.assertTrue(lines[0].startswith('Question: how does my-list do when kx3 plays it against the 8 public lists'), lines[0])
        self.assertTrue(lines[1].startswith('Size: 32 kx3 games + 32 cheap km3 baseline games ('), lines[1])
        self.assertTrue(lines[2].startswith(f'my-list scored {pc(p)} over 32 games (2 deals x 2 seats against each of the 8 public lists): probably between {pc(lo)} and {pc(hi)} ('), lines[2])
        self.assertTrue(lines[3].startswith('On the same deals, kx3 scored +'), lines[3])
        self.assertTrue(lines[4].startswith('That range runs from '), lines[4])
        for l in lines:
            self.assertNotIn('**', l)
            self.assertNotIn('`', l)
            self.assertFalse(l.startswith(('#', '|', '- ')), l)

    def test_a_partial_page_starts_with_its_banner_and_echoes_nothing_from_the_tables(self):
        t, man, games = self.run_dir(deals=2)
        lines = sr.console_lines(self.rewrite(t, games[:37]))
        self.assertEqual(lines[0], 'PARTIAL: 37 of 64 games played so far (18 kx3 games + 19 cheap km3 baseline games; both count in the 64). '
                                   'The numbers below will move; read them as a snapshot.')
        self.assertTrue(lines[1].startswith('Question: '))
        self.assertEqual(len(lines), 6, lines)
        self.assertEqual([l for l in lines if l.startswith('|') or 'When my-list' in l or 'took' in l], [])

    def test_a_run_that_stops_early_writes_the_partial_page_and_says_so(self):
        t, man, games = self.run_dir(deals=2, complete=False)
        quiet = os.path.join(tempfile.mkdtemp(), 'quiet_report.py')
        self.addCleanup(shutil.rmtree, os.path.dirname(quiet), True)
        write(quiet, 'pass\n')
        said = []
        with mock.patch.object(sr, 'REPORT', quiet):
            sr.best_effort_pages(t, said.append)
        self.assertEqual(said, ['SLOW_REPORT.md (partial) written before stopping'])
        self.assertIn('**PARTIAL: 32 of 64 games played so far (16 kx3 games + 16 cheap km3 baseline games; both count in the 64).', read(os.path.join(t, 'SLOW_REPORT.md')))

    def test_when_even_the_partial_page_cannot_be_written_it_says_why_and_does_not_raise(self):
        empty = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty, True)
        said = []
        sr.best_effort_pages(empty, said.append)
        self.assertEqual(len(said), 1, said)
        self.assertTrue(said[0].startswith('could not write the page before stopping: '), said[0])
        self.assertIn('not a registered run', said[0])


# ---------------------------------------------------------------------------------------------------------- nothing it says is a verdict
class NothingSaysPassOrFail(Pages):
    def test_the_words_of_a_verdict_are_found_when_they_are_there(self):
        for said in ('pass mark 50%', 'a deck scoring under 50% fails', 'A score above 50% means the deck is worth playing.', 'it clears the bar', 'a good enough deck', 'borderline'):
            self.assertNotEqual(verdict_words(said), [], said)
        self.assertEqual(verdict_words('probably between 28.0% and 72.0%; there is no pass or fail line, and they are not a ranking'), [])

    def test_the_page_has_no_verdict_in_words_or_in_a_plain_sentence(self):
        for kw in (dict(deals=2), dict(deals=2, paired=False), dict(deals=3, win=lambda o, d, s: 'deck'), dict(deals=3, win=lambda o, d, s: 'opp'), dict(deals=2, complete=False)):
            t, man, games, text = self.build(**kw)
            self.assertEqual(verdict_words(re.sub(r'whether my-list is worth playing is a call for the player', '', text)), [], kw)
            self.assertEqual(text.count('worth playing'), 1, 'the one sentence that hands the call to the player')

    def test_the_section_of_what_the_numbers_can_and_cannot_say_is_exactly_this(self):
        t, man, games, text = self.build(deals=2)
        p, lo, hi = wilson95(T.x_scores(games))
        want = (f"**These numbers say how my-list did in simulated games with kx3 playing it against the 8 public lists, probably between {pc(lo)} and {pc(hi)}; "
                f"they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**\n"
                "\n"
                "In more detail:\n"
                "\n"
                "- kx3, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the 8 public lists it faces, but its opponent is always one of them "
                "and always plays like the program kx3 imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside "
                "the 8 lists. Read the score as the optimistic end.\n"
                "- The 8 lists count equally here, not by how common they are on the ladder.\n"
                "- The range covers only the luck of the shuffles and coin flips in these 32 games; it does not cover how true to the real game the simulator is. "
                "It can tell whether kx3 plays my-list clearly above or clearly below an even score against these 8 lists; it cannot tell two decks apart whose scores differ by "
                f"less than the width of such a range ({100 * (hi - lo):.1f} points here), and more deals narrow it.\n"
                "- There is no pass or fail line: whether my-list is worth playing is a call for the player.")
        self.assertEqual(self.part(text, "## What these numbers can and can't say").strip(), want)

    def test_the_width_in_that_section_is_the_whole_width_of_the_range_in_points_not_half(self):
        for kw in (dict(deals=1), dict(deals=5, win=lambda o, d, s: 'deck')):  # a symmetric range and a lopsided one clipped at 100%
            t, man, games, text = self.build(**kw)
            p, lo, hi = wilson95(T.x_scores(games))
            width = f'{100 * (hi - lo):.1f}'
            self.assertIn(f'less than the width of such a range ({width} points here)', text)
            self.assertNotIn(f'({100 * (hi - lo) / 2:.1f} points here)', text)


class WhatTheTerminalSays(T.World):
    def session(self):
        """Every kind of run: the plan, the same without the baseline, a registration with its first games, where it stands, the rest, the page again."""
        outs, pages = {}, {}

        def go(label, *extra, **kw):
            code, out, err = self.cli(*extra, **kw)
            self.assertEqual(code, 0, label + '\n' + out + err)
            outs[label] = out + err
            if os.path.exists(os.path.join(self.rundir(), 'SLOW_REPORT.md')):
                pages[label] = read(os.path.join(self.rundir(), 'SLOW_REPORT.md'))
        go('a dry run', '--deals', '5', '--dry-run')
        go('a dry run without the baseline', '--deals', '5', '--no-paired', '--dry-run')
        go('a registration and the first games', '--deals', '2', '--max-games', '10')
        go('where the run stands', '--dir', self.rundir(), '--dry-run', deck=False)
        go('the rest of the games', '--dir', self.rundir(), deck=False)
        go('the page again', '--dir', self.rundir(), '--report-only', deck=False)
        return outs, pages

    def test_no_line_printed_by_any_kind_of_run_says_pass_or_fail_or_names_a_mark(self):
        outs, pages = self.session()
        self.assertEqual(len(outs), 6)
        for label, out in outs.items():
            self.assertTrue(out.strip(), label)
            self.assertEqual(verdict_words(out), [], label + '\n' + out)

    def test_the_plan_line_says_there_is_no_pass_or_fail_line(self):
        outs, pages = self.session()
        for label in ('a dry run', 'a dry run without the baseline'):
            self.assertEqual(sum(1 for l in outs[label].splitlines() if l.endswith(', no pass or fail line')), 1, label)

    def test_a_full_run_prints_the_plan_the_registration_the_run_and_the_page_in_that_order(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        self.assertTrue(all(l.startswith(TAG) for l in out.splitlines()))
        lines = [l[len(TAG):] for l in out.splitlines()]
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertEqual(len(lines), 9 + len(sr.console_lines(page)), lines)
        self.assertTrue(lines[0].startswith('plan: my-list ('))
        self.assertTrue(lines[1].startswith('size: 16 kx3 games + 16 cheap km3 baseline games on the same deals (32 games in all; the km3 games take about a second each); '
                                            'the time is for the 16 kx3 games: about '), lines[1])
        self.assertTrue(lines[2].startswith('on school days the run pauses from 5:15 am to 5 pm'))
        self.assertTrue(lines[3].startswith('stage use (not development evidence; the held-out lock is untouched), seeds from '))
        self.assertTrue(lines[3].endswith(', with the comparison with km3 on the same deals in the page, no pass or fail line'), lines[3])
        self.assertEqual(lines[4], f'pre-registered 32 games (8 pairs, 1 deal x 2 seats x 2 arms) in {d}', 'one deal is "1 deal", not "1 deals"')
        self.assertRegex(lines[5], r'^manifest sha256 [0-9a-f]{64}$')
        self.assertEqual(lines[6:9], [f'registered in {d} before any game', 'running: 32 games to go, 2 at a time', f'SLOW_REPORT.md written in {d}'])
        self.assertEqual(lines[9:], sr.console_lines(page))

    def test_where_a_cut_run_stands_says_how_many_games_are_played_and_how_to_resume(self):
        outs, pages = self.session()
        self.assertEqual(outs['where the run stands'].splitlines(),
                         [TAG + f'10 of 64 games played; 54 games to go (resume with: python3 rl/strength/slow_report.py --dir {self.rundir()})', TAG + 'dry run: nothing written'])

    def test_a_cut_run_echoes_its_banner_and_a_finished_one_echoes_the_page_it_wrote(self):
        outs, pages = self.session()
        cut = outs['a registration and the first games'].splitlines()
        self.assertIn(TAG + 'PARTIAL: 10 of 64 games played so far (5 kx3 games + 5 cheap km3 baseline games; both count in the 64). '
                            'The numbers below will move; read them as a snapshot.', cut)
        self.assertIn(TAG + f'pre-registered 64 games (8 pairs, 2 deals x 2 seats x 2 arms) in {self.rundir()}', cut)
        done = outs['the rest of the games'].splitlines()
        tail = done[done.index(TAG + f'SLOW_REPORT.md written in {self.rundir()}') + 1:]
        self.assertEqual(tail, [TAG + l for l in sr.console_lines(pages['the rest of the games'])])
        self.assertTrue(tail[0].startswith(TAG + 'Question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3'), tail[0])
        self.assertNotIn('PARTIAL', outs['the rest of the games'])


class ConsoleMessages(T.World):
    def test_a_run_cut_by_max_games_says_how_to_resume(self):
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(out.splitlines().count(f'{TAG}stopped after --max-games 10; resume with --dir {self.rundir()}'), 1)

    def test_a_run_folder_with_a_space_in_its_path_is_quoted_in_the_line_that_says_how_to_resume(self):
        self.out_root = os.path.join(self.repo, 'rl', 'results', 'slow reports')
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, out + err)
        folder = self.rundir()
        self.assertIn(' ', folder)
        self.assertEqual(out.splitlines().count(f"{TAG}stopped after --max-games 10; resume with --dir '{folder}'"), 1, out)
        self.assertNotIn(f'--dir {folder}', out)

    def test_a_run_that_finishes_never_says_it_stopped_after_max_games(self):
        for extra in ((), ('--max-games', '32'), ('--max-games', '100')):  # no budget; a budget used up by the very last game; a budget that is not used up
            shutil.rmtree(self.out_root, ignore_errors=True)
            code, out, err = self.cli('--deals', '1', *extra)
            self.assertEqual(code, 0, out + err)
            self.assertNotIn('stopped after', out, extra)
            self.assertNotIn('PARTIAL', out, extra)
            self.assertEqual([e['event'] for e in jsonl(os.path.join(self.rundir(), 'slow_report_log.jsonl')) if e['event'] == 'complete'], ['complete'], extra)

    def test_a_failing_engineering_report_is_said_in_one_line_and_never_blocks_the_page(self):
        self.assertEqual(self.cli('--deals', '1')[0], 0)
        d = self.rundir()
        failing = os.path.join(self.tmp, 'failing_report.py')
        for script, message in (("import sys\nsys.stderr.write('Traceback (most recent call last):\\nValueError: the last line\\n')\nsys.exit(3)\n", 'ValueError: the last line'),
                                ('import sys\nsys.exit(1)\n', 'no message')):
            write(failing, script)
            for name in ('REPORT.md', 'SLOW_REPORT.md'):
                if os.path.exists(os.path.join(d, name)):
                    os.remove(os.path.join(d, name))
            with mock.patch.object(sr, 'REPORT', failing):
                code, out, err = self.cli('--dir', d, '--report-only', deck=False)
            self.assertEqual(code, 0, out + err)
            self.assertEqual(out.splitlines().count(f'{TAG}REPORT.md (the engineering report) could not be written: {message}'), 1, out)
            self.assertNotIn('REPORT.md', read(os.path.join(d, 'SLOW_REPORT.md')), 'no pointer to a report that was not written')


class ResumedRunHeadline(T.World):
    def test_every_line_and_refusal_of_a_resumed_run_carries_the_registered_headline(self):
        d = self.register()
        for label, extra in (('where it stands', ('--dry-run',)), ('the run', ()), ('the page again', ('--report-only',)), ('where it stands when finished', ('--dry-run',))):
            code, out, err = self.cli('--dir', d, *extra, deck=False)
            self.assertEqual(code, 0, label + out + err)
            self.assertTrue(out.splitlines(), label)
            for l in out.splitlines():
                self.assertTrue(l.startswith(TAG), (label, l))
        write(self.deck, T.DECK_TEXT + '\n')  # the deck is no longer the registered one
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertTrue(str(code).startswith(TAG + 'REFUSED: the files this run was registered with are not the ones on disk'), code)


class LogEvents(T.World):
    def setUp(self):
        super().setUp()
        saved = dict(sr._LOG_EXTRA)
        sr._LOG_EXTRA.clear()  # the pilot names of the log are a module global: this test must not borrow them from an earlier one

        def restore():
            sr._LOG_EXTRA.clear()
            sr._LOG_EXTRA.update(saved)
        self.addCleanup(restore)

    def test_a_full_run_logs_each_step_in_order_with_both_pilots_and_a_utc_time(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        events = jsonl(os.path.join(d, 'slow_report_log.jsonl'))
        self.assertEqual([e['event'] for e in events if e['event'] != 'env_scrubbed'], ['registered', 'slice_start', 'slice_end', 'complete', 'report_written'])
        for e in events:
            self.assertEqual((e['pilot'], e['reference']), ('kx3', 'km3'), e)
            self.assertRegex(e['at'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        by = {e['event']: e for e in events}
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        reg = by['registered']
        self.assertEqual((reg['deals'], reg['paired'], reg['threads'], reg['deck_file'], reg['deck_sha256'], reg['seed_base'], reg['manifest_sha256']),
                         (1, True, 2, self.deck_rel, T.sha(self.deck), man['seed_base'], T.sha(os.path.join(d, 'manifest.json'))))
        self.assertEqual((by['slice_start']['remaining_games'], by['slice_start']['stop_after_min'], by['slice_start']['threads']), (32, None, 2))
        self.assertEqual((by['slice_end']['returncode'], by['slice_end']['killed_for_school'], by['slice_end']['new_games']), (0, False, 32))
        self.assertEqual(by['complete']['games'], 32)
        self.assertEqual(by['report_written']['path'], os.path.join(d, 'SLOW_REPORT.md'))

    def test_without_the_baseline_the_registration_event_says_so(self):
        self.assertEqual(self.cli('--deals', '1', '--no-paired', '--register-only')[0], 0)
        reg = [e for e in jsonl(os.path.join(self.rundir(), 'slow_report_log.jsonl')) if e['event'] == 'registered']
        self.assertEqual([e['paired'] for e in reg], [False])


def children_of(pid):
    """The pids whose parent is `pid` (Linux /proc), so a test can clean up exactly the processes its own wrapper started."""
    out = []
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                with open(f'/proc/{p}/stat') as f:
                    if f.read().rsplit(')', 1)[1].split()[1] == str(pid):
                        out.append(int(p))
            except (OSError, IndexError):
                pass
    return out


class LinesComeAsTheyAreSaid(T.World):
    def test_each_line_reaches_the_terminal_while_the_run_is_still_going(self):
        """A report runs for hours under nohup and its log is read while it plays: a line must not wait in a buffer until the wrapper ends."""
        self.set_program(T.HANG_PROGRAM)  # a program that never finishes a sitting, so the wrapper stays alive and waits
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONUNBUFFERED'}
        driver = os.path.join(self.tmp, 'driver.py')  # the real main, with the repository's deck validator (not part of this temporary repository) replaced
        write(driver, f'import sys\nsys.path.insert(0, {HERE!r})\nimport slow_report\nsys.exit(slow_report.main(sys.argv[1:], deck_check=lambda p, r: []))\n')
        cmd = [sys.executable, '-B', driver, self.deck, '--repo', self.repo, '--pin', self.pin_path, '--out-root', self.out_root,
               '--date', '2026-10-10', '--deals', '1', '--school-rule', 'off', '--poll-s', '1']
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        got, kids = b'', []
        try:
            deadline = time.time() + 10
            while time.time() < deadline and b'running: 32 games to go' not in got:
                if select.select([proc.stdout], [], [], 0.1)[0]:
                    chunk = os.read(proc.stdout.fileno(), 4096)
                    if not chunk:
                        break
                    got += chunk
            kids = children_of(proc.pid)
            self.assertIn(b'running: 32 games to go', got, 'the lines of a run that is still going must already be on the terminal')
            self.assertIsNone(proc.poll(), 'the wrapper is still running, waiting for the program')
            lines = got.decode('utf-8').splitlines()
            self.assertTrue(lines[0].startswith(TAG + 'plan: my-list ('), lines)
            self.assertIn(TAG + 'running: 32 games to go, 2 at a time', lines)
        finally:
            proc.terminate()  # SIGTERM: the wrapper stops the program, writes the partial page and exits
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            proc.stdout.close()
            for pid in kids:  # only what this wrapper started, and only if it is somehow still there
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


# ---------------------------------------------------------------------------------------------------------- the page built from games that already exist
def gate_3_changes(rows):
    """Gate 3 against the development run, pair by pair: 4 pairs with a decision added, 3 with the winner changed, 2 with the turns changed, 3 with the points
    changed and 1 with only the number of plies changed (13 that differ in some way)."""
    for i, r in enumerate(r for r in rows if r['arm'] == 'X'):
        if i < 4:
            r['log'] = r['log'] + [dict(t=2, o=2, a='Retreat', n=3, act='X', b=1, p=[0, 0], ms=7.0)]
            r['moves_deck'] = dict(r['moves_deck'], n=r['moves_deck']['n'] + 1)
        elif i < 7:
            r['winner'] = 'deck' if r['winner'] != 'deck' else 'opp'
        elif i < 9:
            r['turns'] += 1
        elif i < 12:
            r['points'] = [r['points'][0] + 1, r['points'][1]]
        elif i < 13:
            r['plies'] += 1


class ExistingRuns(TE.Sources):
    """The two source runs of slow_report_existing, rebuilt with whatever data a test asks for (Sources.go and Sources.page then work as they do in test_slow_report_existing)."""
    TAG = '[kx3 (d513e37b) on 03-wailord-indeedee-wall v km3 on the public panel; existing development evidence, not a fresh test] '

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out = os.path.join(self.tmp, 'out')

    def rows(self, d):
        return [json.loads(l) for l in read(os.path.join(d, 'games.jsonl')).splitlines()]

    def put_rows(self, d, rows):
        write(os.path.join(d, 'games.jsonl'), ''.join(json.dumps(r) + '\n' for r in rows))

    def put_manifest(self, d, **kw):
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        man.update(kw)
        write(os.path.join(d, 'manifest.json'), json.dumps(man, indent=1))
        write(os.path.join(d, 'manifest.sha256'), T.sha(os.path.join(d, 'manifest.json')) + '  manifest.json\n')

    def build(self, win_x=None, win_ref=None, dev=None, tool=None):
        """dev(rows) and tool(rows) edit the game records of that run before they are written; the gate-3 run is made from the edited development games."""
        with mock.patch.object(TE, 'win_x', win_x or TE.win_x), mock.patch.object(TE, 'win_ref', win_ref or TE.win_ref):
            self.dev, _ = TE.make_run(self.tmp, 'strength_dev', pilot='kx3')
        rows = self.rows(self.dev)
        if dev:
            dev(rows)
            self.put_rows(self.dev, rows)
        self.dev_games = {r['key']: r for r in rows}
        self.tool, _ = TE.make_run(self.tmp, 'strength_tool', pilot='kx3_r16_c12_z2_real_t0_poolmeta_tools', program='/home/dacz8976/kx/strength_tools',
                                   program_sha='cf73b2a4e858' + '0' * 52, decks=(TE.DECK,), base=self.dev_games)
        rows = self.rows(self.tool)
        if tool:
            tool(rows)
            self.put_rows(self.tool, rows)
        self.tool_games = {r['key']: r for r in rows}
        return self

    def deck_x(self, games):
        return [g for g in games.values() if g['deck'] == TE.DECK and g['arm'] == 'X']

    def stats(self, diffs):
        n, m, sd = len(diffs), statistics.mean(diffs), statistics.stdev(diffs)
        return n, m, sd, sr.t_crit(n - 1) * sd / math.sqrt(n)

    def gain_over_km3(self):
        return [SC[g['winner']] - SC[self.dev_games[g['key'][:-1] + 'ref']['winner']] for g in self.deck_x(self.dev_games)]


class ExistingGainRange(ExistingRuns):
    def can_tell_paragraph(self):
        """What the 80-game range can tell and cannot tell, word for word, from the numbers worked out here: ((low, high) of the gain, the paragraph found, the paragraph wanted)."""
        text = self.page()
        xs = [SC[g['winner']] for g in self.deck_x(self.dev_games)]
        p, lo, hi = wilson95(xs)
        n, m, sd, half = self.stats(self.gain_over_km3())
        glo, ghi = m - half, m + half
        run = f"That range runs from {points(glo)} to {points(ghi)} points, which "
        if glo <= 0 <= ghi:
            note = (run + f'includes no gain at all: these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                          f'They do argue against a gain much larger than {100 * ghi:.1f} points or a loss much larger than {100 * abs(glo):.1f} points; a smaller difference needs more deals. ')
        else:
            note = (run + f"does not include no gain: on these {n} paired games kx3 did {'better' if glo > 0 else 'worse'} than km3. "
                          f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it. ')
        want = (f"What the {len(xs)}-game range can tell and cannot tell: it can tell whether kx3 plays this deck near, clearly above or clearly below an even score against these 8 lists "
                f"({pc(lo)} to {pc(hi)} here), and it can tell a large gain over km3 from none at all (the gain's range is plus or minus {100 * half:.1f} points). {note}"
                f'It cannot tell a gain of a point or two from a gain of ten: {len(xs)} games decide only that much, and a wide range is a statement of how much {len(xs)} games decide, '
                f'not an answer of "nothing". More deals narrow it (the cost table in the slow-report plan gives the hours).')
        return (glo, ghi), [l for l in text.splitlines() if l.startswith('What the ')], want

    def test_a_gain_range_wholly_above_zero_says_better(self):
        self.build()
        (glo, ghi), found, want = self.can_tell_paragraph()
        self.assertGreater(glo, 0)
        self.assertEqual(found, [want])
        n, m, sd, half = self.stats(self.gain_over_km3())
        self.assertIn(f'- The gain: kx3 scored **{points(m)} points** compared with km3 on the same deals, give or take {100 * half:.1f} points '
                      f'(95% interval). That range refers to the {n} paired games, each a deal and seat played by both pilots: {n} kx3 games + {n} cheap km3 baseline games.',
                      self.page().splitlines())

    def test_a_gain_range_wholly_below_zero_says_worse(self):
        self.build(win_x=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck', win_ref=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp')
        (glo, ghi), found, want = self.can_tell_paragraph()
        self.assertLess(ghi, 0)
        self.assertEqual(found, [want])
        n, m, sd, half = self.stats(self.gain_over_km3())
        self.assertLess(m, 0)
        lines = self.page().splitlines()
        self.assertIn(f'- The gain: kx3 scored **{points(m)} points** compared with km3 on the same deals, give or take {100 * half:.1f} points '
                      f'(95% interval). That range refers to the {n} paired games, each a deal and seat played by both pilots: {n} kx3 games + {n} cheap km3 baseline games.', lines)
        self.assertEqual([l for l in lines if l.startswith('- The gain:') and ('more than' in l or 'less than' in l)], [],
                         'a negative gain is "compared with km3" too: never "more than" or "less than" it')

    def test_a_gain_range_that_includes_zero_says_what_the_deals_do_and_do_not_show(self):
        self.build(win_x=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp', win_ref=lambda o, d, s: 'deck' if (o + d + 2 * s) % 3 else 'opp')
        (glo, ghi), found, want = self.can_tell_paragraph()
        self.assertTrue(glo <= 0 <= ghi and abs(glo) != ghi)
        self.assertEqual(found, [want])


class ExistingSizeTimeAndRegistration(ExistingRuns):
    def test_question_1_gives_its_size_and_its_source_in_one_line(self):
        self.build()
        lines = self.page().splitlines()
        self.assertEqual([l for l in lines if l.startswith('Size: 80 kx3 games + ')],
                         ['Size: 80 kx3 games + 80 cheap km3 baseline games (5 deals x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck). '
                          'Source: the development run.'])

    def test_question_2_gives_its_size_with_the_pilot_named_in_every_count(self):
        self.build()
        lines = self.page().splitlines()
        self.assertEqual([l for l in lines if l.startswith('Size: 80 kx3 games with')],
                         ['Size: 80 kx3 games with the Tool tie-break on + the 80 existing kx3 games with it off, paired by deal and seat '
                          '(80 paired games; and 80 cheap km3 baseline games, which the gate-3 build replays exactly).'])
        self.assertEqual([l for l in lines if l.startswith('Build check:')],
                         ["Build check: 80 of the 80 km3 baseline games in the gate-3 run replay the development run exactly (same deals, same moves, same results), and all 80 kx3 games "
                          "in the gate-3 run start from the development run's own deal (same seed, same first player), so the two runs are the same deals played by the same km3."])

    def test_the_headings_the_two_scores_and_the_row_sentence_of_question_1(self):
        self.build()
        lines = self.page().splitlines()
        xs = [SC[g['winner']] for g in self.deck_x(self.dev_games)]
        rs = [SC[g['winner']] for g in self.dev_games.values() if g['deck'] == TE.DECK and g['arm'] == 'ref']
        p, lo, hi = wilson95(xs)
        self.assertNotEqual(pc(p), pc(sum(rs) / len(rs)), 'the two scores must differ, or a mix-up of the two cannot show')
        for want in ('## Question 1: how does 03-wailord-indeedee-wall do with kx3, and is that better than with km3?',
                     '## Question 2: does the Tool tie-break change what kx3 does with this deck?',
                     f'- With kx3, 03-wailord-indeedee-wall scored **{pc(p)}** over the 80 kx3 games: probably between {pc(lo)} and {pc(hi)} '
                     '(95% interval; this range refers to the 80 kx3 games). A win counts 1, a tie 1/2, a loss 0.',
                     f'- With km3, on the same deals, it scored {pc(sum(rs) / len(rs))} over the 80 cheap km3 baseline games.',
                     "Each row's range refers to the 10 kx3 games against that list; with so few games it can separate a very easy or very hard list from an even one, "
                     'not two similar lists from each other.'):
            self.assertEqual(lines.count(want), 1, want)
        wilson_line = [l for l in lines if l.startswith('- With kx3,')][0]
        self.assertNotIn('give or take', wilson_line, 'a Wilson range is not symmetric, so it is not given as give-or-take')

    def test_the_time_line_is_the_mean_the_slowest_and_the_threads_the_run_used(self):
        def dev(rows):
            x = [r for r in rows if r['deck'] == TE.DECK and r['arm'] == 'X']
            ref = [r for r in rows if r['deck'] == TE.DECK and r['arm'] == 'ref']
            for i, r in enumerate(x):
                r['wall_s'] = 700.0 + 10 * i  # 700 .. 1490: mean 1095
            for i, r in enumerate(ref):
                r['wall_s'] = (1.0, 2.0, 3.0)[i % 3]  # mean 1.9875, slowest 3
        self.build(dev=dev)
        self.put_manifest(self.dev, threads=3)
        self.assertIn('- Time: kx3 took 1095 s a game on average on this deck (about 18 min; slowest 1490 s), 3 games at a time; the km3 baseline games took 2.0 s each.',
                      self.page().splitlines())

    def test_a_run_registered_after_its_first_game_is_said_not_to_be_registered_before_the_games(self):
        self.build()
        self.put_manifest(self.dev, created_at='2026-10-03T13:00:00Z')  # the games in the run started at 12:00
        sec = self.page().split('## Where these games come from')[1]
        dev_line, tool_line = [l for l in sec.splitlines() if l.startswith(('- Development run', '- Gate 3'))]
        self.assertIn('first 03-wailord-indeedee-wall game started 2026-10-03T12:00:00Z (**NOT registered before the games**); games.jsonl sha256', dev_line)
        self.assertNotIn('registered before any game', dev_line)
        self.assertIn('2026-10-03T12:00:00Z (registered before any game); games.jsonl sha256', tool_line)

    HEAD = ('**Existing development evidence, not a fresh test.** Nothing was played for this page: it reads games that were already played, by the kx3 development run (2026-10-03) '
            'and by gate 3 of the Tool tie-break (2026-10-03), ')

    def test_the_top_of_the_page_says_both_registered_before_any_game_only_when_both_were(self):
        self.build()
        self.assertEqual(self.page().splitlines()[2], self.HEAD + 'both registered before any game.')
        self.put_manifest(self.dev, created_at='2026-10-03T12:00:00Z')  # the very second the first game started: still before it
        self.assertEqual(self.page().splitlines()[2], self.HEAD + 'both registered before any game.')
        self.put_manifest(self.dev, created_at='2026-10-03T12:00:01Z')  # one second after
        text = self.page()
        self.assertEqual(text.splitlines()[2], self.HEAD + '**but not both were registered before their games: see "Where these games come from".**')
        self.assertNotIn('both registered before any game', text)

    def test_either_run_registered_late_is_enough_to_say_so_at_the_top_and_only_that_run_is_named_below(self):
        self.build()
        self.put_manifest(self.tool, created_at='2026-10-03T12:30:00Z')
        text = self.page()
        self.assertEqual(text.splitlines()[2], self.HEAD + '**but not both were registered before their games: see "Where these games come from".**')
        dev_line, tool_line = [l for l in text.split('## Where these games come from')[1].splitlines() if l.startswith(('- Development run', '- Gate 3'))]
        self.assertIn('2026-10-03T12:00:00Z (registered before any game); games.jsonl sha256', dev_line)
        self.assertIn('registered 2026-10-03T12:30:00Z, first 03-wailord-indeedee-wall game started 2026-10-03T12:00:00Z (**NOT registered before the games**); games.jsonl sha256', tool_line)

    def test_games_with_no_start_time_are_said_to_be_unconfirmed_at_the_top_and_below_never_as_on_time(self):
        self.build()
        for d in (self.dev, self.tool):
            rows = self.rows(d)
            for r in rows:
                r.pop('started_at', None)
            self.put_rows(d, rows)
        text = self.page()
        self.assertEqual(text.splitlines()[2], self.HEAD + '**but the order of registration and games could not be confirmed for both (a game has no start time): see "Where these games come from".**')
        lines = [l for l in text.split('## Where these games come from')[1].splitlines() if l.startswith(('- Development run', '- Gate 3'))]
        self.assertEqual(len(lines), 2)
        for line in lines:
            self.assertIn('first 03-wailord-indeedee-wall game started at a time that is not recorded (**order of registration and games not confirmed**)', line)
            self.assertNotIn('None', line)
            self.assertNotIn('(registered before any game)', line)


class ExistingQuestionTwo(ExistingRuns):
    def test_each_kind_of_difference_is_counted_by_itself(self):
        self.build(tool=gate_3_changes)
        lines = self.page().splitlines()
        for want in ('- 4 of the 80 pairs had a logged decision that differed (the rule acted).', '- 3 of the 80 pairs had a different winner.',
                     '- 5 of the 80 pairs ended with different points or a different number of turns.',
                     "- 13 of the 80 pairs differed in some way at all (gate 3's own count: any logged decision, the points, the turns, the number of plies)."):
            self.assertEqual(lines.count(want), 1, want)

    def test_on_minus_off_the_context_and_the_share_of_changed_winners_are_worked_out_from_the_pairs(self):
        self.build(tool=gate_3_changes)
        lines = self.page().splitlines()
        keys = [k for k in self.tool_games if k.endswith('|X')]
        n, m, sd, half = self.stats([SC[self.tool_games[k]['winner']] - SC[self.dev_games[k]['winner']] for k in keys])
        self.assertEqual(n, 80)
        self.assertGreater(sd, 0)
        self.assertIn(f'- On minus off: **{points(m)} points**, give or take {100 * half:.1f} points '
                      '(95% interval; this range refers to the 80 paired games played with the Tool tie-break on and off).', lines)
        refs = {k: SC[self.dev_games[k[:-1] + 'ref']['winner']] for k in keys}
        _, m_on, _, h_on = self.stats([SC[self.tool_games[k]['winner']] - refs[k] for k in keys])
        _, m_off, _, h_off = self.stats([SC[self.dev_games[k]['winner']] - refs[k] for k in keys])
        self.assertNotEqual(points(m_on), points(m_off), 'the rule must make a difference to the context line, or a swap of on and off cannot show')
        self.assertIn(f'- For context, kx3 minus km3 on the same deals: with the Tool tie-break on {points(m_on)} points (give or take {100 * h_on:.1f}), off {points(m_off)} points '
                      f'(give or take {100 * h_off:.1f}); each range refers to the 80 paired games.', lines)
        p, wlo, whi = wilson95([1.0] * 3 + [0.0] * 77)
        closing = ('What this can tell and cannot tell: it can tell what the rule did on these 80 paired games (4 had a changed decision, 3 a changed winner), and it can put a bound on '
                   f'how often it changes a winner: 3 of 80 winners changed, which puts the share of deals whose winner the rule changes between about {100 * wlo:.1f} and {100 * whi:.1f} '
                   'in 100 (95% Wilson range on 3 of 80). It cannot tell what the rule does on other deals or other decks (gate 3 pooled 400 pairs over 5 decks on its own page), '
                   'and the 3 changed winners are what the on-minus-off figure above counts, for or against the rule; they are too few to say more.')
        self.assertIn(closing, lines)
        self.assertNotIn('changes no winner', closing, 'winners did change here, so the sentence for "no winner changed" must not be on the page')
        self.assertEqual([l for l in lines if 'changes no winner' in l or 'harmless or useful' in l], [])

    def test_when_no_winner_changed_the_closing_sentence_is_a_bound_and_says_the_rule_has_not_been_shown_harmless_or_useful(self):
        def tool(rows):  # the rule acts in the first three pairs and changes nobody's result
            for r in [r for r in rows if r['arm'] == 'X'][:3]:
                r['log'] = r['log'] + [dict(t=2, o=2, a='Retreat', n=3, act='X', b=1, p=[0, 0], ms=7.0)]
                r['moves_deck'] = dict(r['moves_deck'], n=r['moves_deck']['n'] + 1)
        self.build(tool=tool)
        lines = self.page().splitlines()
        p, wlo, whi = wilson95([0.0] * 80)
        closing = ('What this can tell and cannot tell: it can tell what the rule did on these 80 paired games (3 had a changed decision, 0 a changed winner), and it can put a bound on '
                   f'how often it changes a winner: no winner changed in 80 pairs, so the share of deals whose winner the rule changes is probably no more than about {100 * whi:.1f} in 100 '
                   '(95% Wilson bound on 0 of 80). It cannot tell what the rule does on other deals or other decks (gate 3 pooled 400 pairs over 5 decks on its own page), '
                   'and a rule that acts in 3 of 80 games but changes no winner has not been shown to be harmless or useful: whether it would ever change a result on a deck like this is '
                   'a question for more deals.')
        self.assertEqual([l for l in lines if l.startswith('What this can tell and cannot tell')], [closing])
        self.assertNotIn('changed winners are what', closing)

    def test_one_changed_winner_is_still_counted_as_a_winner_changed_not_as_none(self):
        def tool(rows):
            next(r for r in rows if r['arm'] == 'X' and r['winner'] == 'opp')['winner'] = 'deck'
        self.build(tool=tool)
        closing = [l for l in self.page().splitlines() if l.startswith('What this can tell and cannot tell')]
        p, wlo, whi = wilson95([1.0] + [0.0] * 79)
        self.assertEqual(len(closing), 1)
        self.assertIn('(0 had a changed decision, 1 a changed winner)', closing[0])
        self.assertIn(f'1 of 80 winners changed, which puts the share of deals whose winner the rule changes between about {100 * wlo:.1f} and {100 * whi:.1f} in 100 (95% Wilson range on 1 of 80).',
                      closing[0])
        self.assertTrue(closing[0].endswith('and the one changed winner is what the on-minus-off figure above counts, for or against the rule; one is too few to say more.'), closing[0])
        self.assertNotIn('1 changed winners', closing[0])
        self.assertNotIn('changes no winner', closing[0])
        self.assertNotIn('harmless or useful', closing[0])

    def test_an_identical_shift_in_every_pair_is_not_called_exactly_zero_and_gets_no_range(self):
        def dev(rows):
            for r in rows:
                if r['arm'] == 'X':
                    r['winner'] = 'opp'

        def tool(rows):
            for r in rows:
                if r['arm'] == 'X':
                    r['winner'] = 'deck'
        self.build(dev=dev, tool=tool)
        lines = self.page().splitlines()
        self.assertIn('- On minus off: **+100.0 points** over the 80 paired games played with the Tool tie-break on and off; no spread can be estimated from them.', lines)
        self.assertEqual([l for l in lines if 'exactly 0' in l or ('On minus off' in l and 'give or take' in l)], [])

    def test_no_change_at_all_in_any_pair_is_said_to_be_exactly_zero_with_the_games_it_refers_to(self):
        self.build()
        lines = self.page().splitlines()
        self.assertIn('- On minus off: **+0.0 points**: every one of the 80 on-minus-off differences was exactly 0, so no spread can be estimated from them '
                      '(this refers to the 80 paired games played with the Tool tie-break on and off).', lines)

    def test_the_context_line_gives_no_spread_when_the_differences_do_not_vary(self):
        def dev(rows):  # km3 and kx3 both lose every game of the development run: the difference between them never varies
            for r in rows:
                if r['deck'] == TE.DECK:
                    r['winner'] = 'opp'

        def tool(rows):  # and with the rule on kx3 wins every game, so that difference never varies either
            for r in rows:
                if r['arm'] == 'X':
                    r['winner'] = 'deck'
        self.build(dev=dev, tool=tool)
        lines = self.page().splitlines()
        context = [l for l in lines if l.startswith('- For context')]
        self.assertEqual(context, ['- For context, kx3 minus km3 on the same deals: with the Tool tie-break on +100.0 points (no spread to give: every difference is the same), '
                                   'off +0.0 points (no spread to give: every difference is the same); each range refers to the 80 paired games.'])
        self.assertNotIn('give or take', context[0])

    def test_the_context_line_gives_the_range_only_for_the_side_whose_differences_vary(self):
        def dev(rows):  # kx3 and km3 both lose every game of the development run: the off difference never varies
            for r in rows:
                if r['deck'] == TE.DECK:
                    r['winner'] = 'opp'

        def tool(rows):  # with the rule on kx3 wins every third game: the on difference does vary
            for i, r in enumerate([r for r in rows if r['arm'] == 'X']):
                r['winner'] = 'deck' if i % 3 == 0 else 'opp'
        self.build(dev=dev, tool=tool)
        keys = [k for k in self.tool_games if k.endswith('|X')]
        refs = {k: SC[self.dev_games[k[:-1] + 'ref']['winner']] for k in keys}
        n, m_on, sd, h_on = self.stats([SC[self.tool_games[k]['winner']] - refs[k] for k in keys])
        self.assertGreater(sd, 0)
        context = [l for l in self.page().splitlines() if l.startswith('- For context')]
        self.assertEqual(context, [f'- For context, kx3 minus km3 on the same deals: with the Tool tie-break on {points(m_on)} points (give or take {100 * h_on:.1f}), '
                                   'off +0.0 points (no spread to give: every difference is the same); each range refers to the 80 paired games.'])

    def test_the_context_line_gives_its_ranges_when_the_differences_vary(self):
        self.build(tool=gate_3_changes)
        context = [l for l in self.page().splitlines() if l.startswith('- For context')]
        self.assertEqual(len(context), 1)
        self.assertRegex(context[0], r'^- For context, kx3 minus km3 on the same deals: with the Tool tie-break on [+-]\d+\.\d points \(give or take \d+\.\d\), off [+-]\d+\.\d points '
                                     r'\(give or take \d+\.\d\); each range refers to the 80 paired games\.$')
        self.assertNotIn('no spread to give', context[0])


class ExistingTable(ExistingRuns):
    def move_list(self, d, src, dst, deal_shift):
        """Every game of the deck against `src` becomes a game against `dst` (the deals numbered on from `deal_shift`): the same 80 + 80 games, none of them against `src`."""
        rows = self.rows(d)
        for r in rows:
            if r['deck'] == TE.DECK and r['opp'] == src:
                r['opp'], r['deal'] = dst, r['deal'] + deal_shift
                r['key'] = f"{r['deck']}|{dst}|{r['deal']}|{r['seat']}|{r['arm']}"
        self.put_rows(d, rows)

    def test_a_run_whose_lists_do_not_each_have_their_games_is_refused_not_written_with_a_wrong_row_sentence(self):
        self.build()
        for d in (self.dev, self.tool):
            self.move_list(d, 't-weezing', 't-lucario', 5)  # the totals stay 80 + 80, but one list has none and another has twenty
        code, out, err = self.go()
        self.assertNotEqual(code, 0)
        self.assertIn('the development run has 20 kx3 games for 03-wailord-indeedee-wall against t-lucario where 10 are planned', str(code) + err)  # the first list, in panel order, that is off
        self.assertIn('Nothing was written', str(code) + err)
        self.assertFalse(os.path.exists(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md')))


class ExistingConsole(ExistingRuns):
    def test_the_terminal_gets_the_scores_the_gain_the_decisions_the_winners_and_on_minus_off(self):
        self.build(tool=gate_3_changes)
        code, out, err = self.go()
        self.assertEqual(code, 0, err)
        page = read(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md')).splitlines()
        required = [l[2:].replace('**', '').replace('`', '') for l in page
                    if l.startswith(('- With kx3,', '- With km3,', '- The gain:', '- 4 of the 80 pairs had a logged decision', '- 3 of the 80 pairs had a different winner', '- On minus off:'))]
        self.assertEqual(len(required), 6)
        got = out.splitlines()
        self.assertEqual(got[0], self.TAG + f'SLOW_REPORT_EXISTING.md written in {self.out}')
        at = [got.index(self.TAG + l) for l in required]
        self.assertEqual(at, sorted(at), 'in the order of the page')
        self.assertEqual([l for l in got if 'For context' in l or 'Time:' in l or 'ended with different points' in l], [])
