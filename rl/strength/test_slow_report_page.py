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
  * the words: the question first (on the page, on the terminal, in the plan and in the dry run of a folder), then a PARTIAL banner and the error paragraph when there are
    any, then the size, then the numbers; every interval saying which games it refers to, the held-out sentence ("the held-out lock is unchanged"), the section of what
    the numbers can and cannot say, whole and word for word;
  * the ranges: every 95% interval is written "probably between A and B" (range_points: both ends rounded once from the unrounded numbers, signed, never "-0.0", cut at
    -100 and +100 with a clause that says so) and never as "give or take", on both pages and in every case; the note under the gain's range (gain_range_note) says what
    the range does and does not include without repeating its numbers, case by case: too wide for the scale, cut at its ends, "only just" (a nearer end less than 0.05
    points from no gain), wholly above or below zero, including zero;
  * the counts: every count names whose games it counts and is singular at one ("1 kx3 game", "80 cheap km3 baseline games", "1 paired game", "2 tries"), the gain is
    counted in paired games (a deal and seat played by both pilots), a banner or a running time says what the total is made of (kx3 games + baseline games), and the
    dry run of a folder says how many games of each pilot are played, planned and to go;
  * what was run: the program (one that is not the pinned binary is said to be NOT the pinned binary: it names the pinned binary and the registering machine, says that its build
    record says it is a rebuild, that the record is not signed and that what stands behind the program is the replayed self-checks, equal to the committed pin's digests or, for a pin
    let through for a test, to the pin file in use), its build record (an entry it does not have is "not recorded", and a toolchain it does not have "rustc not recorded", never None),
    the pin and whether it is the committed one, each program change of the run with the games started before and after it (only a line that reverify_program could have written
    for a run registered on the rebuilt route: a pinned run shows none, a forged or foreign line is left out), each self-check and how its text was obtained, the harness source,
    the school-morning choice, checked on synthetic manifests and on real registrations (WhatWasRunEndToEnd);
  * the registration time: "before any game" only when no game started before the registration, on both pages (a game that started earlier is named);
  * the standing rule that nothing it prints or writes says pass or fail, in the words of a verdict or in plain sentences, on the page and on every line of the terminal;
  * the registered question, with each pilot in its own role, and each pilot's provenance beside that pilot;
  * what the terminal says: the plan lines (the school days, the pin line), the stop after --max-games (and that the limit counts games of both arms), a failed engineering report, a
    partial page, the same headline on a resumed run;
  * the log: every step is recorded, with both pilots and a UTC time, including what each call that plays games was asked to do (sitting_call, after the lock, before its sittings;
    its school choice is an override only when it differs from the registered one, and the program it ran with);
  * the line that ends a --register-only (how to play what was registered) and the words for what an old manifest does not say (no harness source, no school days).
It ends with the same kind of checks on the page built from games that already exist (slow_report_existing.py): the order of registration is claimed only for the games
that were read (this deck's), the gain's range is given with its whole width in points (worked out from the two ends as printed, RangeWidth), and the pairs, kx3 games and decks
gate 3 pooled are counted from the gate-3 run.
"""
import contextlib, fcntl, io, json, math, os, re, select, shlex, shutil, signal, socket, statistics, subprocess, sys, tempfile, time, unittest
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
PAGE_QUESTION = 'Question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?'
PAGE_QUESTION_ALONE = 'Question: how does my-list do when kx3 plays it against the 8 public lists?'
CUT_NOTE = ' (games across both arms, about half of them kx3 games)'  # what the line that says --max-games stopped the call adds to the count it names


def printed_width(lo, hi):
    """The width of a Wilson range in points as a reader gets it from the two ends the page prints (each rounded to a tenth of a percent): their difference, to a tenth."""
    return f'{float(pc(hi)[:-1]) - float(pc(lo)[:-1]):.1f}'


def bypassed_pin_line(world):
    """The pin line of the plan for a World fixture: its temporary repository has no commit of the pin, World lets the hand-made pin through with the test-only variable, and the line says so."""
    return (f'pin committed: bypassed (rl/strength/slow_report_pin.json sha256 {T.sha(world.pin_path)[:12]}; HEAD has no rl/strength/slow_report_pin.json in {world.repo} '
            f'(not a git repository, no commit, or the file is not committed){T.git_said(world.repo)}; allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use))')


def banner(counts, played, planned=64):
    """The PARTIAL banner of the page, word for word: the pilots' counts first, then how many of the planned games they make up. Its one wording is pinned here."""
    return (f"**PARTIAL: {counts} so far ({played} of the {planned} games planned; both pilots' games count in the {planned}). "
            'The numbers below will move; read them as a snapshot.**')


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
    """The seven lines a dry run prints (the question first), word for word, with the pin's rates replaced by round ones so the hours can be written down."""
    QUESTION = 'question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?'
    QUESTION_ALONE = 'question: how does my-list do when kx3 plays it against the 8 public lists?'
    SCHOOL_ON = 'on school days (mon,tue,wed,thu,fri) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer'
    SCHOOL_OFF = ('school-morning rule: OFF for this run (it never pauses for school mornings; the choice is recorded in the registration and carried by the resume command)')

    def pin_line(self):
        return bypassed_pin_line(self)

    def with_rates(self, **rates):
        pin = json.loads(read(self.pin_path))
        pin['games_per_hour'] = rates
        write(self.pin_path, json.dumps(pin))

    def plan(self, *extra, school='on'):
        code, out, err = self.cli(*extra, '--dry-run', school=school)
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

    def test_the_dry_run_prints_exactly_these_seven_lines(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        lines = self.plan('--deals', '3')
        self.assertEqual(len(lines), 7, lines)
        self.assertEqual(lines[0], self.QUESTION)
        self.assertTrue(lines[1].startswith('plan: my-list (decks/events/my-list.txt, ') and lines[1].endswith('), 3 deals x 2 seats against the 8 public lists'), lines[1])
        self.assertEqual(lines[2], self.expected_time_line(48, '72 minutes', '2.4 hours', '4.8 hours'))
        self.assertEqual(lines[3], self.SCHOOL_ON)
        self.assertEqual(lines[4], self.pin_line())
        slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
        seed = BLOCK[0] + (int(T.sha(self.deck)[:8], 16) % slots) * STEP
        self.assertEqual(lines[5], f"stage use (not development evidence; the held-out lock is untouched), seeds from {seed}, program {self.pin['program']} (pinned, sha256 "
                                   f"{self.pin['program_sha256'][:12]}), with the comparison with km3 on the same deals in the page, no pass or fail line")
        self.assertEqual(lines[6], 'dry run: nothing written')

    def test_the_question_comes_first_with_the_comparison_and_without_it(self):
        """The reporting rule is the question, then the size: the first line a new run prints is the question, in the words of the page's own, and it follows --no-paired."""
        self.assertEqual(self.plan('--deals', '3')[0], self.QUESTION)
        self.assertEqual(self.plan('--deals', '3', '--no-paired')[0], self.QUESTION_ALONE)
        for lines in (self.plan('--deals', '3'), self.plan('--deals', '3', '--no-paired')):
            first = {kind: min(i for i, l in enumerate(lines) if l.startswith(kind)) for kind in ('question: ', 'plan: ', 'size: ', 'stage use')}
            self.assertEqual(sorted(first, key=first.get), ['question: ', 'plan: ', 'size: ', 'stage use'])
            self.assertEqual(sum(1 for l in lines if l.startswith('question: ')), 1)

    def test_the_question_names_the_deck_and_the_pilots_the_pin_gives(self):
        pin = json.loads(read(self.pin_path))
        pin.update(pilot='kz9', reference='kr1', pilot_label='kz9 (abc)', reference_label='kr1 (def)', panel_label='the test panel')
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--dry-run', school='on')
        self.assertEqual(code, 0, out + err)
        first = out.splitlines()[0]
        self.assertEqual(first, '[kz9 (abc) on my-list v kr1 (def) on the test panel] question: how does my-list do when kz9 plays it against the 8 public lists, '
                                'and is that better than when kr1 plays the same deck on the same deals?')
        self.assertNotIn('kx3', first)
        self.assertNotIn('km3', first)

    def test_the_school_morning_rule_line_says_whether_the_rule_is_on_or_off(self):
        on, off = self.plan('--deals', '1', school='on'), self.plan('--deals', '1', school='off')
        self.assertEqual([l for l in on if 'school' in l], [self.SCHOOL_ON])
        self.assertEqual([l for l in off if 'school' in l], [self.SCHOOL_OFF])
        self.assertEqual(len(on), len(off), 'one line either way, in the same place')
        self.assertEqual(on.index(self.SCHOOL_ON), off.index(self.SCHOOL_OFF))
        self.assertNotIn('OFF', ' '.join(on))
        self.assertNotIn('pauses from 5:15', ' '.join(off))

    def test_the_school_line_names_the_school_days_or_says_there_are_none(self):
        """The line follows the days of this registration (the default Monday to Friday, or the ones given), and with no school days it says the rule never pauses the run."""
        for days, want in (('mon,tue', 'on school days (mon,tue) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer'),
                           ('sat', 'on school days (sat) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer'),
                           ('', 'school-morning rule: on, but with no school days set it never pauses the run')):
            with self.subTest(days=days):
                lines = self.plan('--deals', '1', '--school-days', days, school='on')
                self.assertEqual([l for l in lines if 'school' in l], [want])
                self.assertEqual(lines.index(want), 3, 'in the same place as the other two forms of the line')
        self.assertNotIn('pauses from 5:15', ' '.join(self.plan('--deals', '1', '--school-days', '', school='on')))

    def test_without_the_baseline_the_stage_line_says_without_and_the_size_line_says_the_games_are_still_played(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        lines = self.plan('--deals', '3', '--no-paired')
        self.assertEqual(len(lines), 7, lines)
        self.assertTrue(lines[5].endswith('), without the comparison with km3 on the same deals in the page, no pass or fail line'), lines[5])
        self.assertNotIn('with the comparison', lines[5])
        self.assertEqual(lines[2], self.expected_time_line(48, '72 minutes', '2.4 hours', '4.8 hours', no_paired=True))
        paired = self.plan('--deals', '3')
        self.assertNotIn('--no-paired', paired[2], 'the note is only for a run without the comparison')
        self.assertTrue(paired[5].endswith('), with the comparison with km3 on the same deals in the page, no pass or fail line'), paired[5])

    def test_the_size_line_counts_both_pilots_games_and_says_the_time_is_for_the_kx3_games(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        for deals in (1, 2, 7):
            line = self.plan('--deals', str(deals))[2]
            g = 16 * deals
            self.assertTrue(line.startswith(f'size: {g} kx3 games + {g} cheap km3 baseline games on the same deals ({2 * g} games in all; '), line)
            self.assertIn(f'the time is for the {g} kx3 games: about ', line)
        self.assertEqual(self.plan('--deals', '1')[1].rsplit('), ', 1)[1], '1 deal x 2 seats against the 8 public lists', 'one deal is not pluralised')

    def test_the_expected_time_is_in_minutes_below_two_hours_and_in_hours_from_two(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        self.assertEqual(self.plan('--deals', '1')[2], self.expected_time_line(16, '24 minutes', '48 minutes', '96 minutes'))
        self.assertEqual(self.plan('--deals', '5')[2], self.expected_time_line(80, '2.0 hours', '4.0 hours', '8.0 hours'))

    def test_the_default_is_five_deals(self):
        lines = self.plan()
        self.assertTrue(lines[1].endswith('), 5 deals x 2 seats against the 8 public lists'), lines[1])
        self.assertTrue(lines[2].startswith('size: 80 kx3 games + 80 cheap km3 baseline games on the same deals (160 games in all; '), lines[2])


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

    def test_a_finished_run_has_no_partial_banner_and_a_partial_one_has_it_right_below_the_question(self):
        t, man, games, text = self.build(deals=2)
        self.assertNotIn('PARTIAL', text)
        t, man, games = self.run_dir(deals=2)
        text = self.rewrite(t, games[:37])
        lines = text.splitlines()
        self.assertEqual(lines[4], '## What it says')
        self.assertEqual(lines[6], PAGE_QUESTION, 'the question is the first thing the section says')
        self.assertEqual(lines[8], banner('18 kx3 games + 19 cheap km3 baseline games', 37), 'the banner comes right after it')
        self.assertTrue(lines[10].startswith('Size: '), 'and the size after the banner')
        self.assertEqual(text.count('PARTIAL'), 1)

    def test_the_partial_banner_counts_each_pilots_games_in_the_singular_and_at_zero(self):
        t, man, games = self.run_dir(deals=2)
        both = [games[0], games[1]]  # a km3 baseline game, then the kx3 game of the same deal and seat
        self.assertEqual([g['arm'] for g in both], ['ref', 'X'])
        for keep, counts in (([games[1]], '1 kx3 game + 0 cheap km3 baseline games'), ([games[0]], '0 kx3 games + 1 cheap km3 baseline game'),
                             (both, '1 kx3 game + 1 cheap km3 baseline game'), (games[:3], '1 kx3 game + 2 cheap km3 baseline games')):
            text = self.rewrite(t, keep)
            self.assertEqual(text.splitlines()[8], banner(counts, len(keep)), counts)

    def test_a_run_without_the_comparison_still_counts_the_baseline_games_in_its_banner(self):
        """The program plays the km3 games whether or not the page reports the comparison, and they are in the total, so the banner says what the total is made of."""
        t, man, games = self.run_dir(deals=2, paired=False)
        text = self.rewrite(t, games[:37])
        self.assertEqual(text.splitlines()[6], PAGE_QUESTION_ALONE)
        self.assertEqual(text.splitlines()[8], banner('18 kx3 games + 19 cheap km3 baseline games', 37))

    def test_the_question_comes_first_then_the_banner_then_the_error_note_then_the_size_then_any_number(self):
        """The order of 'What it says', on the page and on the terminal: the question, a PARTIAL banner, the note about games that failed, the size, and only then a number."""
        k2 = 'my-list|t-altaria|0|0|X'
        cases = (('a finished run', dict(), 64, [], ['question', 'size', 'number']),
                 ('a cut run', dict(), 37, [], ['question', 'banner', 'size', 'number']),
                 ('a cut run without the comparison', dict(paired=False), 37, [], ['question', 'banner', 'size', 'number']),
                 ('a cut run with a game that failed', dict(errors=[(k2, 'x'), (k2, 'y')]), 37, [k2], ['question', 'banner', 'errors', 'size', 'number']),
                 ('a run with no kx3 game yet', dict(), -16, [], ['question', 'banner', 'size', 'none yet']))
        for label, kw, keep, drop, order in cases:
            t, man, games = self.run_dir(deals=2, **kw)
            if keep < 0:
                text = self.rewrite(t, [g for g in games if g['arm'] == 'ref'][:-keep])
            else:
                text = self.rewrite(t, [g for g in games[:keep] if g['key'] not in drop])
            sec = self.part(text, '## What it says')

            def kind(line):
                return ('question' if line.startswith('Question: ') else 'banner' if line.lstrip('*').startswith('PARTIAL: ') else 'errors' if 'could not be finished' in line
                        else 'size' if line.startswith('Size: ') else 'none yet' if line.startswith('No kx3 game has finished yet') else 'number' if re.search(r'\d+\.\d%', line) else None)
            kinds = [kind(l) for l in sec.splitlines() if l.strip() and not l.startswith('#')]
            self.assertEqual([k for k in kinds if k][:len(order)], order, label)
            self.assertEqual([kind(l) for l in sr.console_lines(text)][:len(order)], order, label + ' (the terminal)')
            self.assertEqual(kinds.count('question'), 1, label)

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
    def head(self, games, ends=None, cut=False):
        """The gain paragraph, word for word: the figure, who scored what over how many paired games, then the range as `probably between A and B points` (A and B as
        given in `ends`, or rounded once from m -+ half), `(cut at the ends of the possible scale)` when `cut`, and which games the 95% interval refers to."""
        n, m, half, sx, sref = gain(games)
        lo, hi = ends or (points(m - half), points(m + half))
        return (f'On the same deals, kx3 scored **{points(m)} points** compared with km3 piloting this deck (kx3 {pc(sx)}, km3 on this deck {pc(sref)}, over {n} paired games: '
                f'each a deal and seat played by both pilots, so {n} kx3 games + {n} cheap km3 baseline games), '
                f"probably between {lo} and {hi} points{' (cut at the ends of the possible scale)' if cut else ''} (95% interval; this range refers to those {n} paired games).")

    def range_ends(self, games):
        n, m, half, sx, sref = gain(games)
        return n, m - half, m + half

    def gain_section(self, text):
        return text.split('### How much better')[1].split('\n## ')[0]

    def note_after_head(self, text, head):
        """The line two lines below the gain paragraph (a blank line between them): the note about what the range does and does not include."""
        lines = text.splitlines()
        self.assertEqual(lines.count(head), 1, head)
        i = lines.index(head)
        self.assertEqual(lines[i + 1], '')
        return lines[i + 2]

    def test_a_range_that_includes_no_gain_says_what_the_games_do_and_do_not_show(self):
        t, man, games, text = self.build(deals=3)
        n, lo, hi = self.range_ends(games)
        self.assertTrue(lo <= 0 <= hi, 'this data is meant to include no gain')
        self.assertEqual(self.note_after_head(text, self.head(games)),
                         f'That range includes no gain at all: these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                         f'They do argue against a gain much larger than {100 * hi:.1f} points or a loss much larger than {100 * abs(lo):.1f} points; a smaller difference needs more deals.')
        self.assertNotIn('give or take', text)

    def test_a_range_wholly_above_zero_says_better_and_does_not_say_by_how_much(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', ref_win=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')
        n, lo, hi = self.range_ends(games)
        self.assertTrue(lo > 0, 'this data is meant to be a clear gain')
        self.assertEqual(self.note_after_head(text, self.head(games)),
                         f'That range does not include no gain: on these {n} paired games kx3 did better than km3. '
                         f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.')

    def test_a_range_wholly_below_zero_says_worse(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'opp' if (o + d) % 5 else 'deck', ref_win=lambda o, d, s: 'deck' if (o + d + s) % 4 else 'opp')
        n, lo, hi = self.range_ends(games)
        self.assertTrue(hi < 0, 'this data is meant to be a clear loss')
        self.assertEqual(self.note_after_head(text, self.head(games)),
                         f'That range does not include no gain: on these {n} paired games kx3 did worse than km3. '
                         f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.')

    def test_a_range_wider_than_the_whole_scale_says_the_paired_games_are_too_few_and_the_range_is_the_whole_scale(self):
        t, man, games = self.run_dir(deals=1, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if s == 0 else 'opp')
        two = [g for g in games if g['opp'] == PANEL[0]]  # both seats, both arms: two paired games, the differences 0 and +1
        text = self.rewrite(t, two)
        n, m, half, sx, sref = gain(two)
        self.assertEqual((n, m), (2, 0.5))
        self.assertGreater(2 * half, 2, 'this data is meant to give a range wider than the whole possible scale')
        sec = self.gain_section(text)
        self.assertIn(self.head(two, ends=('-100.0', '+100.0'), cut=True), sec.splitlines(), 'the figure is still shown, its range cut at the ends of the scale')
        self.assertEqual([l for l in sec.splitlines() if l.startswith('That range')],
                         ['That range is wider than the whole possible scale (-100 to +100 points): 2 paired games are too few to say anything about the gain yet.'])
        for s in ('That range runs', 'includes no gain', 'does not include', 'argue against', 'did better', 'did worse', 'give or take'):
            self.assertNotIn(s, sec)

    def test_a_range_that_runs_past_the_top_of_the_scale_is_cut_there_and_says_so(self):
        # kx3 wins everything; km3 wins the first game of three lists and loses the rest: 13 differences of +1 and 3 of 0, a range that ends at +102.7 and is cut at +100
        t, man, games, text = self.build(deals=1, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if (o < 3 and s == 0) else 'opp')
        n, m, half, sx, sref = gain(games)
        self.assertEqual(n, 16)
        self.assertTrue(m + half > 1 and 2 * half < 2, 'this data is meant to run past +100 without being wider than the whole scale')
        head = self.head(games, ends=(points(m - half), '+100.0'), cut=True)
        self.assertEqual(self.note_after_head(text, head), 'That range does not include no gain: on these 16 paired games kx3 did better than km3. '
                                                           'It does not say by exactly how much: that part of the range is as wide as 16 paired games make it.')
        self.assertEqual(text.count('(cut at the ends of the possible scale)'), 1, 'said once, beside the range it cuts')
        self.assertNotIn('+102', text)

    def test_a_range_that_runs_past_the_bottom_of_the_scale_is_cut_there_and_says_so(self):
        t, man, games, text = self.build(deals=1, win=lambda o, d, s: 'opp', ref_win=lambda o, d, s: 'opp' if (o < 3 and s == 0) else 'deck')
        n, m, half, sx, sref = gain(games)
        self.assertEqual(n, 16)
        self.assertTrue(m - half < -1 and 2 * half < 2)
        head = self.head(games, ends=('-100.0', points(m + half)), cut=True)
        self.assertEqual(self.note_after_head(text, head), 'That range does not include no gain: on these 16 paired games kx3 did worse than km3. '
                                                           'It does not say by exactly how much: that part of the range is as wide as 16 paired games make it.')
        self.assertEqual(text.count('(cut at the ends of the possible scale)'), 1)
        self.assertNotIn('-102', text)

    def test_a_range_inside_the_scale_is_not_said_to_be_cut_nor_too_wide(self):
        t, man, games, text = self.build(deals=3)
        n, lo, hi = self.range_ends(games)
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
        self.assertNotIn('give or take', text)
        self.assertNotIn('probably between', self.gain_section(text), 'one comparison gives no range at all')
        self.assertNotIn('That range', text)

    def test_no_spread_at_all_is_said_as_such_and_gets_no_range(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck')
        line = [l for l in text.splitlines() if l.startswith('On the same deals')]
        self.assertEqual(line, ['On the same deals, kx3 scored **+0.0 points** compared with km3 piloting this deck (kx3 100.0%, km3 on this deck 100.0%, over 48 paired games: '
                                'each a deal and seat played by both pilots, so 48 kx3 games + 48 cheap km3 baseline games); '
                                'every one of the 48 comparisons gave the same difference, so no spread can be estimated from them.'])
        self.assertNotIn('That range', text)
        self.assertNotIn('probably between', self.gain_section(text), 'no spread, no range')
        self.assertNotIn('give or take', text)

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
    range is mean +- half, in fractions of a score, over n paired games), with round numbers so that each case can be written down. The note does not repeat the range's
    numbers: range_points prints them just before (RangePoints below), and the note says only what that range does and does not include."""

    def note(self, n, m, half):
        return sr.gain_range_note('kx3', 'km3', n, m, half)

    BETTER = 'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.'
    ONLY_JUST = ' (only just: its nearer end is less than 0.05 points from no gain)'

    def test_a_range_that_includes_zero_says_the_games_show_neither_a_gain_nor_a_loss(self):
        self.assertEqual(self.note(50, 0.05, 0.25),
                         'That range includes no gain at all: these 50 paired games do not show that kx3 plays this deck better than km3, '
                         'and do not show that it plays it worse. They do argue against a gain much larger than 30.0 points or a loss much larger than 20.0 points; '
                         'a smaller difference needs more deals.')

    def test_a_range_wholly_above_zero_says_better_and_one_wholly_below_says_worse(self):
        self.assertEqual(self.note(50, 0.3, 0.1), 'That range does not include no gain: on these 50 paired games kx3 did better than km3. ' + self.BETTER.format(n=50))
        self.assertEqual(self.note(50, -0.3, 0.1), 'That range does not include no gain: on these 50 paired games kx3 did worse than km3. ' + self.BETTER.format(n=50))

    def test_the_note_never_repeats_the_numbers_of_the_range_it_follows(self):
        for n, m, half in ((50, 0.3, 0.1), (50, -0.3, 0.1), (16, 0.8, 0.3), (50, 0.05, 0.25), (7, 0.0, 0.999)):
            text = self.note(n, m, half)
            self.assertNotIn('runs from', text, (n, m, half))
            self.assertNotIn('give or take', text, (n, m, half))
            self.assertNotIn('probably between', text, (n, m, half))
        for n, m, half in ((50, 0.3, 0.1), (50, -0.3, 0.1), (16, 0.8, 0.3)):
            self.assertEqual(re.findall(r'\d+\.\d', self.note(n, m, half)), [], 'a range that excludes no gain has no figure in its note')
        self.assertEqual(re.findall(r'\d+\.\d', self.note(50, 0.05, 0.25)), ['30.0', '20.0'], 'only the two bounds of "argue against" (a gain larger than, a loss larger than)')

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
        self.assertTrue(just_inside.startswith('That range includes no gain at all'), just_inside)
        self.assertIn('a gain much larger than 99.9 points or a loss much larger than 99.9 points', just_inside)
        self.assertNotIn('wider than', just_inside)

    def test_a_range_past_an_end_of_the_scale_is_cut_there_and_the_note_takes_its_figures_from_the_cut_end(self):
        top = self.note(16, 0.8, 0.3)
        self.assertEqual(top, 'That range does not include no gain: on these 16 paired games kx3 did better than km3. ' + self.BETTER.format(n=16))
        bottom = self.note(16, -0.8, 0.3)
        self.assertEqual(bottom, 'That range does not include no gain: on these 16 paired games kx3 did worse than km3. ' + self.BETTER.format(n=16))
        across = self.note(16, 0.5, 0.6)  # the range is -10 to +110 points: the cut end (+100) is what the "argue against" figure is taken from
        self.assertEqual(across, 'That range includes no gain at all: these 16 paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                                 'They do argue against a gain much larger than 100.0 points or a loss much larger than 10.0 points; a smaller difference needs more deals.')
        below = self.note(16, -0.5, 0.6)
        self.assertEqual(below, 'That range includes no gain at all: these 16 paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                                'They do argue against a gain much larger than 10.0 points or a loss much larger than 100.0 points; a smaller difference needs more deals.')

    def test_a_range_that_ends_exactly_at_an_end_of_the_scale_is_not_too_wide_and_includes_no_gain(self):
        text = self.note(16, 0.5, 0.5)  # 0 to +100 points
        self.assertTrue(text.startswith('That range includes no gain at all'), text)
        self.assertIn('a gain much larger than 100.0 points or a loss much larger than 0.0 points', text)
        text = self.note(16, -0.5, 0.5)  # -100 to 0 points
        self.assertTrue(text.startswith('That range includes no gain at all'), text)
        self.assertIn('a gain much larger than 0.0 points or a loss much larger than 100.0 points', text)

    def test_a_lower_bound_that_rounds_to_plus_zero_is_called_only_just_above_no_gain(self):
        text = self.note(50, 0.0203, 0.02)  # the range starts at +0.03 points
        self.assertEqual(text, f'That range does not include no gain{self.ONLY_JUST}: on these 50 paired games kx3 did better than km3. ' + self.BETTER.format(n=50))
        near = self.note(50, 0.0212, 0.02)  # +0.12 points rounds to +0.1, which is a number and is printed as one
        self.assertEqual(near, 'That range does not include no gain: on these 50 paired games kx3 did better than km3. ' + self.BETTER.format(n=50))
        self.assertNotIn('only just', near)

    def test_an_upper_bound_that_rounds_to_plus_zero_is_called_only_just_below_no_gain(self):
        text = self.note(50, -0.0203, 0.02)  # the range ends at -0.03 points
        self.assertEqual(text, f'That range does not include no gain{self.ONLY_JUST}: on these 50 paired games kx3 did worse than km3. ' + self.BETTER.format(n=50))
        near = self.note(50, -0.0212, 0.02)
        self.assertEqual(near, 'That range does not include no gain: on these 50 paired games kx3 did worse than km3. ' + self.BETTER.format(n=50))
        self.assertNotIn('only just', near)

    def test_only_just_starts_at_five_hundredths_of_a_point_from_no_gain(self):
        for m, only_just in ((0.02049, True), (0.02051, False)):  # the nearer end is +0.049 points and +0.051 points: the second prints as +0.1
            self.assertEqual('only just' in self.note(50, m, 0.02), only_just, m)
            self.assertEqual('only just' in self.note(50, -m, 0.02), only_just, -m)
        self.assertNotIn('only just', self.note(50, 0.3, 0.1), 'a range far from no gain is not "only just"')
        self.assertNotIn('only just', self.note(50, 0.0197, 0.02), 'a range that includes no gain has no nearer end to speak of')

    def test_the_note_says_only_just_exactly_when_the_printed_range_ends_at_plus_zero(self):
        """The note and the figure printed just before it never disagree: 'only just' where the nearer end prints as +0.0, and never where it prints as a number."""
        for hundredths in range(1, 41):  # the nearer end 0.01 .. 0.40 points from no gain
            end = hundredths / 10000
            above = sr.range_points(end + 0.02, 0.02)  # 'probably between +0.0 and +4.0 points'
            below = sr.range_points(-end - 0.02, 0.02)
            self.assertEqual('only just' in self.note(50, end + 0.02, 0.02), above.split(' and ')[0].endswith('+0.0'), (hundredths, above))
            self.assertEqual('only just' in self.note(50, -end - 0.02, 0.02), below.split(' and ')[1].startswith('+0.0'), (hundredths, below))

    def test_a_range_that_just_includes_zero_is_not_called_only_just_and_never_prints_minus_zero(self):
        text = self.note(50, 0.0197, 0.02)  # the range starts at -0.03 points
        self.assertTrue(text.startswith('That range includes no gain at all'), text)
        self.assertIn('a loss much larger than 0.0 points', text)
        self.assertNotIn('-0.0', text)
        self.assertNotIn('only just', text)
        text = self.note(50, -0.0197, 0.02)
        self.assertTrue(text.startswith('That range includes no gain at all'), text)
        self.assertIn('a gain much larger than 0.0 points', text)
        self.assertNotIn('-0.0', text)


class RangePoints(T.Timed):
    """range_points(m, half): the range m -+ half (fractions of a score) as `probably between A and B points`, A and B signed with one decimal, rounded ONCE from the
    unrounded ends, and cut at the ends of the possible scale (-100 to +100 points) with a clause that says so."""

    def test_the_two_ends_are_signed_and_written_with_one_decimal(self):
        self.assertEqual(sr.range_points(0.0625, 0.0815), 'probably between -1.9 and +14.4 points')
        self.assertEqual(sr.range_points(0.3, 0.1), 'probably between +20.0 and +40.0 points')
        self.assertEqual(sr.range_points(-0.3, 0.1), 'probably between -40.0 and -20.0 points')
        self.assertEqual(sr.range_points(0.05, 0.25), 'probably between -20.0 and +30.0 points')

    def test_the_ends_are_rounded_once_from_the_unrounded_numbers_not_from_a_rounded_figure_and_a_rounded_half(self):
        m, half = 0.04449, 0.03051  # the figure prints as +4.4 and the half as 3.1, whose difference (+1.3) is not the lower end (0.01398: +1.4)
        self.assertEqual(sr.signed_points(m), '+4.4')
        self.assertEqual(f'{100 * half:.1f}', '3.1')
        self.assertEqual(sr.range_points(m, half), 'probably between +1.4 and +7.5 points')
        m, half = 0.0446, 0.0306  # the figure prints as +4.5 and the half as 3.1, whose sum (+7.6) is not the upper end (0.0752: +7.5)
        self.assertEqual(sr.signed_points(m), '+4.5')
        self.assertEqual(f'{100 * half:.1f}', '3.1')
        self.assertEqual(sr.range_points(m, half), 'probably between +1.4 and +7.5 points')

    def test_no_end_ever_prints_as_minus_zero_and_zero_is_plus_zero(self):
        self.assertEqual(sr.range_points(0.0, 0.0), 'probably between +0.0 and +0.0 points')
        self.assertEqual(sr.range_points(-0.00001, 0.0002), 'probably between +0.0 and +0.0 points')  # -0.021 and +0.019 points
        self.assertEqual(sr.range_points(0.0, 0.1), 'probably between -10.0 and +10.0 points')
        self.assertEqual(sr.range_points(0.0197, 0.02), 'probably between +0.0 and +4.0 points')  # the lower end is -0.03 points
        self.assertEqual(sr.range_points(-0.0197, 0.02), 'probably between -4.0 and +0.0 points')
        for m in (x / 1000 for x in range(-300, 301, 7)):
            self.assertNotIn('-0.0 ', sr.range_points(m, 0.0123) + ' ', m)

    def test_an_end_past_the_scale_is_cut_at_it_and_the_clause_says_so_once(self):
        cut = ' (cut at the ends of the possible scale)'
        self.assertEqual(sr.range_points(0.8, 0.3), 'probably between +50.0 and +100.0 points' + cut)
        self.assertEqual(sr.range_points(-0.8, 0.3), 'probably between -100.0 and -50.0 points' + cut)
        self.assertEqual(sr.range_points(0.5, 0.6), 'probably between -10.0 and +100.0 points' + cut)
        self.assertEqual(sr.range_points(0.5, 6.35), 'probably between -100.0 and +100.0 points' + cut, 'both ends past the scale: one clause')
        self.assertEqual(sr.range_points(0.0, 3.0).count('(cut at the ends'), 1)

    def test_a_range_that_ends_exactly_at_an_end_of_the_scale_is_not_called_cut(self):
        self.assertEqual(sr.range_points(0.5, 0.5), 'probably between +0.0 and +100.0 points')
        self.assertEqual(sr.range_points(-0.5, 0.5), 'probably between -100.0 and +0.0 points')
        self.assertEqual(sr.range_points(0.0, 1.0), 'probably between -100.0 and +100.0 points')
        self.assertEqual(sr.range_points(0.0, 1.0001), 'probably between -100.0 and +100.0 points (cut at the ends of the possible scale)', 'a hundredth of a point past is past')

    def test_a_range_inside_the_scale_has_no_clause_and_no_give_or_take(self):
        text = sr.range_points(0.1, 0.2)
        self.assertEqual(text, 'probably between -10.0 and +30.0 points')
        self.assertNotIn('cut', text)
        self.assertNotIn('give or take', text)


class RangeWidth(T.Timed):
    """range_width_points(m, half): the width of the range range_points prints, worked out from the two ends as printed (each rounded once, cut at the scale), so a sentence
    about the width never disagrees with the ends printed beside it."""

    def test_the_width_is_the_difference_of_the_two_printed_ends(self):
        for m, half in ((0.0625, 0.0815), (0.3, 0.1), (-0.3, 0.1), (0.05, 0.25), (0.04449, 0.03051), (0.0, 0.0), (0.1, 0.2), (0.0197, 0.02), (0.8, 0.3), (-0.8, 0.3), (0.5, 6.35)):
            a, b = re.search(r'between ([+-]\d+\.\d) and ([+-]\d+\.\d) points', sr.range_points(m, half)).groups()
            self.assertAlmostEqual(sr.range_width_points(m, half), float(b) - float(a), places=9, msg=(m, half))

    def test_it_is_not_twice_the_unrounded_half_when_the_two_differ_at_the_first_decimal(self):
        m, half = 0.045, 0.0306  # the ends are 1.44 and 7.56: they print as +1.4 and +7.6, 6.2 apart, where twice the half is 6.12 (6.1)
        self.assertEqual(sr.range_points(m, half), 'probably between +1.4 and +7.6 points')
        self.assertAlmostEqual(sr.range_width_points(m, half), 6.2, places=9)
        self.assertEqual(f'{200 * half:.1f}', '6.1', 'the width the page used to print')

    def test_a_range_cut_at_the_scale_is_as_wide_as_what_is_left_of_it(self):
        self.assertAlmostEqual(sr.range_width_points(0.8, 0.3), 50.0, places=9)
        self.assertAlmostEqual(sr.range_width_points(-0.8, 0.3), 50.0, places=9)
        self.assertAlmostEqual(sr.range_width_points(0.5, 6.35), 200.0, places=9, msg='both ends past the scale: the whole scale')
        self.assertAlmostEqual(sr.range_width_points(0.0, 1.0), 200.0, places=9)


SYMMETRIC_RANGE_WORDS = ('give or take', 'plus or minus', '±', '+/-', '+-')  # a range that is cut at the scale, or built from a Wilson or a t interval, is not symmetric


class NoGiveOrTake(Pages):
    """No page says 'give or take' (or any other symmetric spelling) in any of its cases: every range is 'probably between A and B'."""

    def check(self, text, label):
        for words in SYMMETRIC_RANGE_WORDS:
            self.assertNotIn(words, text, f'{label}: {words!r}')
        self.assertIn('probably between', text, label)
        ranged = re.findall(r'probably between [+-]?\d+\.\d%? and [+-]?\d+\.\d%?(?: points)?(?: \(cut at the ends of the possible scale\))? \(95% interval', text)
        self.assertEqual(len(ranged), text.count('(95% interval'), f'{label}: every 95% interval is written as "probably between A and B"')

    def test_a_finished_page_of_every_size_and_every_kind_of_result(self):
        for deals in (1, 2, 3, 5):
            for label, kw in (('mixed', {}), ('all ties', dict(win=lambda o, d, s: 'tie')), ('wins', dict(win=lambda o, d, s: 'deck')), ('losses', dict(win=lambda o, d, s: 'opp')),
                              ('no baseline', dict(paired=False)), ('no spread', dict(win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck')),
                              ('a clear gain', dict(win=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', ref_win=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')),
                              ('a clear loss', dict(win=lambda o, d, s: 'opp' if (o + d) % 5 else 'deck', ref_win=lambda o, d, s: 'deck' if (o + d + s) % 4 else 'opp')),
                              ('cut at the top', dict(win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if (o < 3 and s == 0) else 'opp'))):
                t, man, games, text = self.build(deals=deals, **kw)
                self.check(text, f'{deals} deals, {label}')

    def test_a_partial_page_with_few_games_and_with_a_game_that_failed(self):
        k2 = 'my-list|t-altaria|0|0|X'
        t, man, games = self.run_dir(deals=2, errors=[(k2, 'x'), (k2, 'y')])
        for keep in (4, 5, 9, 17, 37, 63):  # (the first kx3 game, k2, is the one that failed)
            self.check(self.rewrite(t, [g for g in games[:keep] if g['key'] != k2]), f'{keep} games')

    def test_the_gain_in_every_one_of_its_cases(self):
        t, man, games = self.run_dir(deals=1, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck' if s == 0 else 'opp')
        one = [g for g in games if g['opp'] == PANEL[0] and g['seat'] == 0]
        for label, keep in (('one comparison', one), ('too wide for the scale', [g for g in games if g['opp'] == PANEL[0]]), ('no games of the baseline', [g for g in games if g['arm'] == 'X'])):
            text = self.rewrite(t, keep)
            for words in SYMMETRIC_RANGE_WORDS:
                self.assertNotIn(words, text, f'{label}: {words!r}')


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

    def test_the_note_is_the_first_thing_the_console_shows_after_the_question_and_the_banner(self):
        text = self.with_errors([(self.K2, 'x'), (self.K2, 'y')], {self.K2})
        lines = sr.console_lines(text)
        self.assertEqual(lines[0], PAGE_QUESTION)
        self.assertTrue(lines[1].startswith('PARTIAL: 31 kx3 games + 32 cheap km3 baseline games so far (63 of the 64 games planned; '), lines[1])
        self.assertTrue(lines[2].startswith('1 game could not be finished and is left out of every number below (first: ' + self.K2), lines[2])
        self.assertTrue(lines[3].startswith('Size: '), lines[3])
        self.assertNotIn('`', lines[2])

    def test_the_note_sits_between_the_banner_and_the_size_on_the_page_too(self):
        text = self.with_errors([(self.K2, 'x'), (self.K2, 'y')], {self.K2})
        sec = self.part(text, '## What it says').strip().split('\n\n')
        self.assertEqual(sec[0], PAGE_QUESTION)
        self.assertEqual(sec[1], banner('31 kx3 games + 32 cheap km3 baseline games', 63))
        self.assertTrue(sec[2].startswith('1 game could not be finished and is left out of every number below'), sec[2])
        self.assertTrue(sec[3].startswith('Size: 31 kx3 games + 32 cheap km3 baseline games so far, of 32 kx3 games + 32 cheap km3 baseline games planned.'), sec[3])


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


PIN_SHA = '5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2'
HARNESS_SHA = 'bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e'
GIVEN = 'given in the config (copied from the pin, which says it was measured on this exact program sha256)'
REPLAYED = 'replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)'
HOW_GIVEN = 'copied from the pin, not replayed: the pin says it was measured on this exact binary'
HOW_REPLAYED = 'replayed on the registering machine just before registration, equal to the committed pin'
HOW_REPLAYED_FILE = 'replayed on the registering machine just before registration, equal to the pin file in use (NOT the committed pin: test use)'  # for a pin let through for a test
COMMITTED_DIGESTS, FILE_DIGESTS = T.COMMITTED_DIGESTS, T.FILE_DIGESTS
ENGINE_REF = 'd513e37b473f2819075e1eb2439075a8a1e65c42'
ENGINE_TREE = '31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588'
# the build record a rebuilt run carries in its slow_report block (what read_build_record returned at the registration)
BUILD_RECORD = dict(schema=1, program='/cloud/build/strength', program_sha256='f' * 64, engine_arg=ENGINE_REF, engine=f'{ENGINE_REF} engine tree {ENGINE_TREE}', engine_ref=ENGINE_REF,
                    engine_tree_archived=ENGINE_TREE, harness_source_sha256=HARNESS_SHA, rustc='rustc 1.90.0 (fake 2026-01-01)\nbinary: rustc\nhost: x86_64-unknown-linux-gnu',
                    cargo='cargo 1.90.0 (fake 2026-01-01)', machine='Linux 6.1.0 x86_64', host='cloud-box-1', built_at='2026-10-09T22:00:00Z',
                    rebuild_command='env HOME=/home/cloud STRENGTH_BUILD_DIR=/home/cloud/sb bash /home/cloud/repo/rl/strength/build.sh d513e37b /cloud/build/strength',
                    record_file='/cloud/build/strength.build.json', record_sha256='b' * 64)
REBUILD_PARAGRAPH = ("- The program is NOT the pinned binary (`{pinned}`, sha256 `{sha12}`): its build record says it is a rebuild of the pinned source, and it was accepted only "
                     "because that record has the pinned engine tree and harness source and both self-checks were replayed on the registering machine{host} and equal {digests}, and the "
                     "harness source in the checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those "
                     "replayed self-checks (12 fixed games per pilot), not the record.")


def rebuild_paragraph(host='', digests=COMMITTED_DIGESTS, pinned='/home/dacz8976/kx/strength', sha12='5a8f5c83a791'):
    """The paragraph of the page for a program that is not the pinned binary: `host` is ' (name)' of the registering machine or empty, `digests` what the self-checks were equal to."""
    return REBUILD_PARAGRAPH.format(host=host, digests=digests, pinned=pinned, sha12=sha12)
BUILD_RECORD_LINE = ('- Build record `strength.build.json` sha256 `bbbbbbbbbbbb`: engine d513e37b473f2819075e1eb2439075a8a1e65c42 -> tree as archived `31dbd2e6e8ec` (the pin\'s is `31dbd2e6e8ec`), '
                     'harness source `bf9c5d681400`, rustc 1.90.0 (fake 2026-01-01), cargo 1.90.0 (fake 2026-01-01), built 2026-10-09T22:00:00Z on cloud-box-1 (Linux 6.1.0 x86_64); '
                     'to rebuild the same bytes after a restart: `env HOME=/home/cloud STRENGTH_BUILD_DIR=/home/cloud/sb bash /home/cloud/repo/rl/strength/build.sh d513e37b /cloud/build/strength`.')
PIN_COMMITTED_LINE = "- Pin `rl/strength/slow_report_pin.json` sha256 `eeeeeeeeeeee`: committed (byte-equal to HEAD's file in the repository this run was registered from)."


class WhatWasRunLines(Pages):
    """The lines of 'What was run' that say which program, which source and which school-morning choice a run had: the whole section, word for word, for the pinned
    program and for a rebuild, and each line on its own for the cases around it."""
    KEYS = dict(program_route='pinned', pinned_program='/home/dacz8976/kx/strength', pinned_program_sha256=PIN_SHA, harness_source_sha256=HARNESS_SHA,
                harness_source_checkout_sha256=HARNESS_SHA, engine_ref='d513e37b473f2819075e1eb2439075a8a1e65c42', engine_tree='31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588',
                school_rule='on', school_days='mon,tue,wed,thu,fri')

    def page_with(self, source=GIVEN, program=None, **slow):
        """The page of a run whose slow_report block carries the registration's facts (KEYS, changed by `slow`; a value None drops the key)."""
        t, man, games = self.run_dir(deals=1, selfcheck_source={'kx3': source, 'km3': source})
        block = dict(self.KEYS, **slow)
        man['slow_report'].update({k: v for k, v in block.items() if v is not None})
        for k, v in block.items():
            if v is None:
                man['slow_report'].pop(k, None)
        if program:
            man['program'], man['program_sha256'] = program
        T.rewrite_manifest(t, man)
        return t, sr.write_slow_report(t)

    def section(self, text):
        return self.part(text, '## What was run').strip().splitlines()

    def test_the_whole_section_for_the_pinned_program_in_these_words(self):
        t, text = self.page_with()
        msha = T.sha(os.path.join(t, 'manifest.json'))[:16]
        self.assertEqual(self.section(text), [
            '- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `/home/dacz8976/kx/strength` sha256 `5a8f5c83a791`.',
            f'- Self-check of `kx3`: `selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({HOW_GIVEN})',
            f'- Self-check of `km3`: `selfcheck pilot=km3 digest=81b572198c04d5d1` ({HOW_GIVEN})',
            '- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec',
            '- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.',
            '- School-morning rule: on (mon,tue,wed,thu,fri).',
            '- Deck file `decks/events/my-list.txt` sha256 `cccccccccccc`; the file is committed.',
            f'- Registered 2026-10-10T10:00:00Z, before any game; manifest sha256 `{msha}`; repository commit `abc123`; pin `rl/strength/slow_report_pin.json`.',
            '- 1 deal x 2 seats; seeds `24601000000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.'])

    def test_the_whole_section_for_a_rebuild_names_the_rebuild_the_pinned_binary_and_what_was_replayed(self):
        t, text = self.page_with(source=REPLAYED, program=('/cloud/build/strength', 'f' * 64), program_route='rebuilt', registered_on='cloud-box-1', build_record=BUILD_RECORD,
                                 pin_committed='yes')
        msha = T.sha(os.path.join(t, 'manifest.json'))[:16]
        self.assertEqual(self.section(text), [
            '- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `/cloud/build/strength` sha256 `ffffffffffff`.',
            rebuild_paragraph(host=' (cloud-box-1)', digests=COMMITTED_DIGESTS),
            BUILD_RECORD_LINE,
            PIN_COMMITTED_LINE,
            f'- Self-check of `kx3`: `selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({HOW_REPLAYED})',
            f'- Self-check of `km3`: `selfcheck pilot=km3 digest=81b572198c04d5d1` ({HOW_REPLAYED})',
            '- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec',
            '- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.',
            '- School-morning rule: on (mon,tue,wed,thu,fri).',
            '- Deck file `decks/events/my-list.txt` sha256 `cccccccccccc`; the file is committed.',
            f'- Registered 2026-10-10T10:00:00Z, before any game; manifest sha256 `{msha}`; repository commit `abc123`; pin `rl/strength/slow_report_pin.json`.',
            '- 1 deal x 2 seats; seeds `24601000000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.'])

    def test_the_rebuild_paragraph_is_there_only_for_a_rebuild(self):
        for route in ('pinned', None):  # a run registered before the route was recorded is not called a rebuild either
            t, text = self.page_with(program_route=route)
            self.assertNotIn('REBUILD', text, route)
            self.assertNotIn('NOT the pinned binary', text, route)
            self.assertNotIn('pinned source', text, route)
        t, text = self.page_with(program_route='rebuilt')
        self.assertEqual(text.count('The program is NOT the pinned binary'), 1)
        self.assertEqual(text.count('its build record says it is a rebuild of the pinned source'), 1)
        self.assertNotIn('REBUILD', text, 'the page does not claim that the program IS a rebuild: the record says so, and the record is not signed')
        self.assertIn('The record is written by the builder\'s own script and is not signed: what stands behind the program is those replayed self-checks (12 fixed games per pilot), not the record.', text)

    def test_the_rebuild_paragraph_names_the_pinned_binary_it_stands_in_for_not_the_program_it_used(self):
        t, text = self.page_with(program_route='rebuilt', program=('/cloud/build/strength', 'f' * 64), pinned_program='/pinned/elsewhere/strength', pinned_program_sha256='7' * 64)
        line = [l for l in text.splitlines() if l.startswith('- The program is NOT the pinned binary')][0]
        self.assertIn('is NOT the pinned binary (`/pinned/elsewhere/strength`, sha256 `777777777777`)', line)
        self.assertNotIn('/cloud/build/strength', line)
        self.assertIn('Program `/cloud/build/strength` sha256 `ffffffffffff`.', text)

    def test_each_self_check_line_says_how_its_text_was_obtained_in_these_words(self):
        for source, how in ((GIVEN, HOW_GIVEN), (REPLAYED, HOW_REPLAYED), ('run by strength_prereg.py', 'replayed at registration'), ('something else', 'recorded at registration'), (None, 'recorded at registration')):
            t, text = self.page_with(source=source, pin_committed='yes')  # (a replay is said to be equal to the committed pin only of a pin recorded as committed)
            self.assertEqual([l for l in text.splitlines() if l.startswith('- Self-check of `kx3`')],
                             [f'- Self-check of `kx3`: `selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({how})'], source)
        t, man, games = self.run_dir(deals=1, selfcheck_source={'kx3': GIVEN, 'km3': REPLAYED})
        man['slow_report']['pin_committed'] = 'yes'
        T.rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        self.assertIn(f'`selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({HOW_GIVEN})', text, 'each pilot has its own source')
        self.assertIn(f'`selfcheck pilot=km3 digest=81b572198c04d5d1` ({HOW_REPLAYED})', text)

    def test_the_harness_line_says_whether_the_checkout_has_the_pinned_source(self):
        same = '- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.'
        t, text = self.page_with()
        self.assertIn(same, text.splitlines())
        t, text = self.page_with(harness_source_checkout_sha256='0123456789abcdef' * 4)
        self.assertIn('- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has `0123456789ab` '
                      '(so the pinned binary was not built from exactly that source).', text.splitlines())
        self.assertNotIn('has the same', text)
        t, text = self.page_with(harness_source_sha256=None, harness_source_checkout_sha256=None)
        self.assertNotIn('Harness source', text, 'a run registered before the source hash was recorded has no such line')

    def test_the_school_morning_rule_line_says_on_with_its_days_or_off_and_that_it_was_chosen(self):
        t, text = self.page_with(school_rule='on', school_days='mon,tue')
        self.assertEqual([l for l in text.splitlines() if l.startswith('- School-morning rule')], ['- School-morning rule: on (mon,tue).'])
        t, text = self.page_with(school_rule='off')
        self.assertEqual([l for l in text.splitlines() if l.startswith('- School-morning rule')],
                         ['- School-morning rule: off (chosen at registration, for a machine that is not the laptop).'])
        self.assertNotIn('mon,tue,wed,thu,fri', ' '.join(self.section(text)), 'the days mean nothing with the rule off')
        t, text = self.page_with(school_rule=None, school_days=None)
        self.assertNotIn('School-morning', text, 'a run registered before the choice was recorded has no such line')

    def test_the_school_morning_rule_line_for_a_run_with_no_school_days_and_for_a_manifest_that_does_not_say(self):
        def rule_line(text):
            return [l for l in text.splitlines() if l.startswith('- School-morning rule')]
        t, text = self.page_with(school_rule='on', school_days='')
        self.assertEqual(rule_line(text), ['- School-morning rule: on (no school days, so it never pauses).'], 'no school days is a choice, said as one')
        t, text = self.page_with(school_rule='on', school_days=None)  # an old manifest: no days recorded
        self.assertEqual(rule_line(text), ['- School-morning rule: on.'], 'nothing in parentheses when the manifest does not say')
        man = json.loads(read(os.path.join(t, 'manifest.json')))
        man['slow_report']['school_days'] = None
        T.rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        self.assertEqual(rule_line(text), ['- School-morning rule: on.'], 'and the same when it says null')
        self.assertNotIn('None', text)
        for days in ('', None):
            t, text = self.page_with(school_rule='off', school_days=days)
            self.assertEqual(rule_line(text), ['- School-morning rule: off (chosen at registration, for a machine that is not the laptop).'], 'the days mean nothing with the rule off')

    def test_the_harness_line_says_in_words_that_the_checkout_had_no_harness_source_and_never_prints_none(self):
        want = ('- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has no harness source (rl/strength/src), '
                'so this could not be compared.')
        t, text = self.page_with(harness_source_checkout_sha256=None)  # the key is missing
        pages = {'a missing hash': text}
        man = json.loads(read(os.path.join(t, 'manifest.json')))
        man['slow_report']['harness_source_checkout_sha256'] = None  # or null
        T.rewrite_manifest(t, man)
        pages['a null hash'] = sr.write_slow_report(t)
        pages['an empty hash'] = self.page_with(harness_source_checkout_sha256='')[1]
        for label, text in pages.items():
            with self.subTest(label):
                self.assertIn(want, text.splitlines())
                self.assertNotIn('None', text)
                self.assertNotIn('has the same', text)
                self.assertNotIn('so the pinned binary was not built', text)

    def test_a_rebuild_page_without_the_machine_or_the_build_record_says_only_what_it_knows(self):
        """A run registered before the record existed (no registered_on, no build_record, no pin_committed) is still described, without a gap or a None: the self-checks are said to be
        equal to the pin file in use (a state that was not recorded is not "committed"), and the missing build record is flagged by the provenance line."""
        t, text = self.page_with(program_route='rebuilt')
        self.assertEqual([l for l in text.splitlines() if 'NOT the pinned binary' in l], [rebuild_paragraph(digests=FILE_DIGESTS)])
        for absent in ('Build record', '- Pin ', 'None', '()'):
            self.assertNotIn(absent, text)

    def test_the_lines_come_in_this_order_program_rebuild_record_pin_self_checks_build_harness_school_deck_registration(self):
        t, text = self.page_with(program_route='rebuilt', school_rule='off', source=REPLAYED, registered_on='cloud-box-1', build_record=BUILD_RECORD, pin_committed='yes',
                                 program=('/cloud/build/strength', 'f' * 64))  # (the record is for this program: nothing for the provenance line to flag)
        sec = self.section(text)
        starts = ('- Pilots:', '- The program is NOT the pinned binary', '- Build record', '- Pin ', '- Self-check of `kx3`', '- Self-check of `km3`', '- Build:', '- Harness source',
                  '- School-morning rule', '- Deck file', '- Registered', '- 1 deal')
        self.assertEqual([next(i for i, l in enumerate(sec) if l.startswith(s)) for s in starts], list(range(len(starts))))

    def test_the_pin_line_says_committed_or_not_in_these_words_and_only_when_the_registration_recorded_it(self):
        t, text = self.page_with(pin_committed='yes')
        self.assertEqual([l for l in text.splitlines() if l.startswith('- Pin ')], [PIN_COMMITTED_LINE])
        self.assertNotIn('NOT the committed pin', text)
        detail = 'HEAD has no rl/strength/slow_report_pin.json in /tmp/x/repo (not a git repository, no commit, or the file is not committed); allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)'
        t, text = self.page_with(pin_committed='bypassed', pin_committed_detail=detail)
        self.assertEqual([l for l in text.splitlines() if l.startswith('- Pin ')],
                         [f'- Pin `rl/strength/slow_report_pin.json` sha256 `eeeeeeeeeeee`: **NOT the committed pin** ({detail}): what this page says about the program rests on a pin that is not '
                          'the committed one.'])
        self.assertNotIn('byte-equal', text)
        t, text = self.page_with(pin_committed='bypassed')  # no detail recorded: the state itself is named
        self.assertIn('**NOT the committed pin** (bypassed): what this page says', text)
        for value in (None, ''):
            t, text = self.page_with(pin_committed=value)  # a manifest from before the check: no claim either way
            self.assertNotIn('- Pin ', text)
            self.assertNotIn('committed pin**', text)

    def rebuilt_run(self, **kw):
        """A run directory (32 games, every one started at 10:05:00) registered on the rebuilt route, with the facts reverify_program compares a program change with: the pin's engine tree
        and harness source (KEYS) and the self-check texts of the manifest. Returns (folder, manifest, games)."""
        t, man, games = self.run_dir(deals=1, **kw)
        man['slow_report'].update(self.KEYS, program_route='rebuilt')
        T.rewrite_manifest(t, man)
        return t, man, games

    @staticmethod
    def put_log(t, *events, torn=None):
        """The run's log as these events, one per line, then, if given, a last line torn by a kill."""
        with open(os.path.join(t, 'slow_report_log.jsonl'), 'w', encoding='utf-8') as f:
            f.write(''.join(json.dumps(e) + '\n' for e in events))
            if torn:
                f.write(torn)

    def test_each_program_change_in_the_log_is_a_line_with_the_games_started_before_and_after_it(self):
        t, man, games = self.rebuilt_run()
        change = lambda new, **over: T.change_event_for(man, new, pin_committed='yes', old_sha256='a' * 64, **over)
        events = [change('b' * 64, at='2026-10-10T10:05:01Z', record_sha256='c' * 64, replayed_on='cloud-box-2'),
                  dict(at='2026-10-10T10:05:00Z', event='slice_end', returncode=0),
                  change('d' * 64, at='2026-10-10T10:05:00Z', record_sha256='e' * 64, replayed_on='cloud-box-3')]
        self.put_log(t, *events, torn='{"event": "program_changed", "at": "2026-10-1')  # a line torn by a kill
        text = sr.write_slow_report(t)
        changes = [l for l in self.section(text) if 'The program changed mid-run' in l]
        self.assertEqual(changes, [
            '- **The program changed mid-run** (2026-10-10T10:05:01Z): sha256 `aaaaaaaaaaaa` -> `bbbbbbbbbbbb` after a restart or rebuild; its build record has the pinned engine tree and '
            "harness source (record `cccccccccccc`) and both self-checks were replayed again on cloud-box-2 and equal the committed pin's digests. 32 games of the 32 played so far were started before "
            'this change and 0 after; the numbers above pool them.',
            '- **The program changed mid-run** (2026-10-10T10:05:00Z): sha256 `aaaaaaaaaaaa` -> `dddddddddddd` after a restart or rebuild; its build record has the pinned engine tree and '
            "harness source (record `eeeeeeeeeeee`) and both self-checks were replayed again on cloud-box-3 and equal the committed pin's digests. 0 games of the 32 played so far were started before "
            'this change and 32 after; the numbers above pool them.'], 'in the order of the log, a game that started in the very second of the change is after it, other events and a torn line are not changes')
        self.assertEqual(self.section(text)[3:5], changes, 'right after the pilots, the line that flags the missing build record and the rebuild paragraph, there being no build record line and no pin line here')
        t, man, games = self.rebuilt_run()
        self.assertNotIn('program changed', sr.write_slow_report(t).lower(), 'a run with no change in its log says nothing of one')

    def test_a_program_changed_line_that_the_run_could_not_have_written_is_not_shown_as_a_change(self):
        """The log is not covered by manifest.sha256, and the page shows a 'program_changed' line only by the test accepted_program_shas and program_in_use_before use (is_program_change): a
        run registered on the rebuilt route and a line that reverify_program could have written for it. A line it could not have written is left out, and no None is printed for what it lacks."""
        t, man, games = self.run_dir(deals=1)  # a run on the pinned route: reverify_program never ran on it
        man['slow_report'].update(self.KEYS, program_route='pinned')
        T.rewrite_manifest(t, man)
        self.put_log(t, {'event': 'program_changed'})
        text = sr.write_slow_report(t)
        self.assertNotIn('The program changed mid-run', text)
        self.assertNotIn('None', text)

    def test_a_consistent_program_changed_line_without_the_entries_that_only_describe_it_is_shown_without_none(self):
        """program_change_valid asks for the entries that tie a line to the registration (the program, its record, the self-check texts) and for 'at' (the games before and after are counted
        from it); a line without 'old_sha256' or 'replayed_on' or the record's sha256 is still a program change, and the page says 'not recorded' for each of those, never the text None.
        A line without 'at' is not a program change at all and is not shown."""
        t, man, games = self.rebuilt_run()
        self.put_log(t, T.change_event_for(man, 'c' * 64, pin_committed=T.DROP, replayed_on=T.DROP, old_sha256=T.DROP))
        text = sr.write_slow_report(t)
        self.assertNotIn('None', text)
        line = next(l for l in text.splitlines() if 'The program changed mid-run' in l)
        self.assertIn('sha256 `not recorded` -> `cccccccccccc`', line)
        self.assertIn('replayed again on a machine not recorded', line)
        t2, man2, games2 = self.rebuilt_run()
        self.put_log(t2, T.change_event_for(man2, 'c' * 64, pin_committed=T.DROP, replayed_on=T.DROP, at=T.DROP, old_sha256=T.DROP))
        text2 = sr.write_slow_report(t2)
        self.assertNotIn('The program changed mid-run', text2)
        self.assertNotIn('None', text2)

    def test_the_page_of_a_pinned_run_shows_no_program_change_whatever_the_log_says_even_a_line_that_looks_just_right(self):
        t, man, games = self.run_dir(deals=1)
        for route in ('pinned', None, 'something else'):
            with self.subTest(route):
                block = dict(man['slow_report'], **{k: v for k, v in self.KEYS.items() if k != 'program_route'})
                if route:
                    block['program_route'] = route
                ran = dict(man, slow_report=block)
                T.rewrite_manifest(t, ran)
                self.put_log(t, T.change_event_for(ran, 'b' * 64), {'event': 'program_changed'}, {'event': 'program_changed', 'new_sha256': 'c' * 64})
                text = sr.write_slow_report(t)
                self.assertNotIn('The program changed mid-run', text)
                self.assertNotIn('changed mid-run', text)
                self.assertNotIn('None', text)
                self.assertNotIn('NOT the pinned binary', text, 'the page is that of a run that is not a rebuild, with or without a log line saying otherwise')

    def test_the_page_of_a_rebuilt_run_shows_the_lines_the_run_could_have_written_and_no_others(self):
        t, man, games = self.rebuilt_run()
        good = lambda new, **over: T.change_event_for(man, new, pin_committed=T.DROP, old_sha256='a' * 64, record_sha256=new[:1] * 64, **over)
        forged = [good('1' * 64, **over) for label, over in T.forged_overrides(man, '1' * 64)]
        self.assertGreaterEqual(len(forged), 18)
        events = forged[:9] + [good('2' * 64, at='2026-10-10T10:05:01Z', replayed_on='cloud-box-2')] + forged[9:] + [{'event': 'program_changed'}, dict(good('3' * 64), event='slice_end'),
                                                                                                                    good('4' * 64, at='2026-10-10T10:05:02Z', replayed_on='cloud-box-3')]
        self.put_log(t, *events, torn='{"event": "program_changed", "new_sha25')
        text = sr.write_slow_report(t)
        changes = [l for l in self.section(text) if 'The program changed mid-run' in l]
        self.assertEqual(len(changes), 2, changes)
        self.assertEqual([re.search(r'sha256 `(\w+)` -> `(\w+)`', l).groups() for l in changes], [('aaaaaaaaaaaa', '222222222222'), ('aaaaaaaaaaaa', '444444444444')])
        self.assertIn('(record `222222222222`)', changes[0])
        self.assertIn('(record `444444444444`)', changes[1])
        self.assertNotIn('None', text)
        self.assertEqual(text.count('changed mid-run'), 2)

    def test_the_rebuild_paragraph_and_the_self_check_lines_say_what_the_pin_was(self):
        """What the self-checks were equal to is the committed pin's digests only for a pin recorded as committed; for a pin let through for a test, or for a run whose registration did
        not record the state (which is not "committed" either), it is the pin file in use, said not to be the committed one."""
        detail = 'HEAD has no rl/strength/slow_report_pin.json in /tmp/x/repo (not a git repository, no commit, or the file is not committed); allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)'
        for state, digests, how in ((None, FILE_DIGESTS, HOW_REPLAYED_FILE), ('yes', COMMITTED_DIGESTS, HOW_REPLAYED), ('bypassed', FILE_DIGESTS, HOW_REPLAYED_FILE),
                                    ('no', FILE_DIGESTS, HOW_REPLAYED_FILE)):
            with self.subTest(state):
                t, text = self.page_with(program_route='rebuilt', source=REPLAYED, pin_committed=state, pin_committed_detail=detail if state in ('bypassed', 'no') else None)
                lines = text.splitlines()
                self.assertEqual(lines.count(rebuild_paragraph(digests=digests)), 1)
                self.assertEqual([l for l in lines if l.startswith('- Self-check of')],
                                 [f'- Self-check of `kx3`: `selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({how})', f'- Self-check of `km3`: `selfcheck pilot=km3 digest=81b572198c04d5d1` ({how})'])
                if digests == COMMITTED_DIGESTS:
                    self.assertNotIn('NOT the committed pin', text)
                else:
                    self.assertIn('equal to the pin file in use (NOT the committed pin: test use)', text)
        t, text = self.page_with(source=GIVEN, pin_committed='bypassed', pin_committed_detail=detail)
        self.assertEqual([l.rsplit(' (', 1)[1] for l in text.splitlines() if l.startswith('- Self-check of')], [HOW_GIVEN + ')'] * 2, 'a text copied from the pin does not claim a replay, whatever the pin was')

    def test_a_program_change_says_what_the_replay_was_equal_to_by_the_pin_it_was_accepted_under(self):
        t, man, games = self.run_dir(deals=1)
        man['slow_report'].update(self.KEYS, program_route='rebuilt', pin_committed='yes')  # registered with a committed pin ...
        T.rewrite_manifest(t, man)
        events = [T.change_event_for(man, str(i) * 64, at=f'2026-10-10T10:05:0{i}Z', old_sha256='a' * 64, record_sha256='c' * 64, replayed_on='cloud-box-2', pin_committed=state)
                  for i, state in ((1, 'yes'), (2, 'bypassed'), (3, T.DROP), (4, 'no'), (5, None))]
        self.put_log(t, *events)
        text = sr.write_slow_report(t)  # ... and the changes are each judged by the pin of their own replay
        changes = [l for l in text.splitlines() if l.startswith('- **The program changed mid-run**')]
        self.assertEqual([re.search(r' and equal (.*)\. \d+ games? of the \d+ played so far', l).group(1) for l in changes],
                         [COMMITTED_DIGESTS, FILE_DIGESTS, FILE_DIGESTS, FILE_DIGESTS, FILE_DIGESTS], 'only a replay recorded as made under the committed pin says so; a replay with no state recorded does not')

    def test_record_text_is_the_text_of_an_entry_or_not_recorded(self):
        rec = dict(a='text', b='', c=None, d=5, e=['x'], f={}, g=True, h='two\nlines')
        self.assertEqual([sr.record_text(rec, k) for k in 'abcdefgh'], ['text', 'not recorded', 'not recorded', 'not recorded', 'not recorded', 'not recorded', 'not recorded', 'two\nlines'])
        self.assertEqual(sr.record_text(rec, 'missing'), 'not recorded')
        self.assertEqual(sr.record_text({}, 'rustc'), 'not recorded')

    def test_a_build_record_with_only_the_entries_that_were_checked_says_not_recorded_and_never_none(self):
        checked = ('schema', 'program_sha256', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'record_file', 'record_sha256')
        bare = {k: v for k, v in BUILD_RECORD.items() if k in checked}
        want = ("- Build record `strength.build.json` sha256 `bbbbbbbbbbbb`: engine not recorded -> tree as archived `31dbd2e6e8ec` (the pin's is `31dbd2e6e8ec`), harness source `bf9c5d681400`, "
                "rustc not recorded, not recorded, built not recorded on not recorded (not recorded); to rebuild the same bytes after a restart: `not recorded`.")
        t, text = self.page_with(program_route='rebuilt', source=REPLAYED, pin_committed='yes', registered_on='cloud-box-1', build_record=bare)
        self.assertEqual([l for l in text.splitlines() if l.startswith('- Build record')], [want])
        self.assertNotIn('None', text)
        self.assertNotIn('built with', text, 'the page says "rustc not recorded" for the toolchain, not the plan\'s "built with ..."')
        self.assertNotIn(', not recorded)', text)
        texts = ('engine_arg', 'engine', 'rustc', 'cargo', 'machine', 'host', 'built_at', 'rebuild_command')
        for value in (None, '', 5, 1.5, True, [], ['x'], {}, {'a': 'b'}):  # (a manifest nobody should have edited, or a registration that predates the checks: said in words all the same)
            with self.subTest(value=value):
                t, text = self.page_with(program_route='rebuilt', source=REPLAYED, pin_committed='yes', registered_on='cloud-box-1', build_record=dict(BUILD_RECORD, **{k: value for k in texts}))
                self.assertEqual([l for l in text.splitlines() if l.startswith('- Build record')], [want])
                self.assertNotIn('None', text)
        t, text = self.page_with(program_route='rebuilt', source=REPLAYED, build_record={k: v for k, v in BUILD_RECORD.items() if k != 'record_file'})
        self.assertIn('- Build record `not recorded` sha256 `bbbbbbbbbbbb`:', text, 'a record whose file name is not known')
        self.assertNotIn('None', text)

    def test_the_pin_line_comes_after_the_program_lines_and_before_the_self_checks_on_the_pinned_route_too(self):
        t, text = self.page_with(pin_committed='yes')
        sec = self.section(text)
        self.assertEqual(sec.index(PIN_COMMITTED_LINE), 1, 'right after the pilots and the program, there being no rebuild paragraph')
        self.assertTrue(sec[2].startswith('- Self-check of `kx3`'))


class WhatWasRunEndToEnd(T.World):
    """The facts the page prints are the ones the registration wrote: a real registration (the fake program, a synthetic repository with harness source) and the page
    read back. The rebuilt route takes `--program` and replays both self-checks, which the fake program answers the way the pin says."""
    FAKE_CHECKS = {'kx3': 'selfcheck pilot=kx3 games=12 digest=fakefakefakefake', 'km3': 'selfcheck pilot=km3 games=12 digest=fakefakefakefake'}

    def with_harness_source(self):
        for name, text in (('src/main.rs', 'fn main() {}\n'), ('src/lib.rs', '// lib\n'), ('Cargo.toml', '[package]\nname = "x"\n')):
            write(os.path.join(self.repo, 'rl', 'strength', *name.split('/')), text)
        return sr.harness_source_sha256(self.repo)

    def set_pin(self, **kw):
        pin = json.loads(read(self.pin_path))
        pin.update(kw)
        write(self.pin_path, json.dumps(pin))
        return pin

    def page(self):
        return read(os.path.join(self.rundir(), 'SLOW_REPORT.md'))

    def write_record(self, program, pin, harness):
        """The build record build.sh would have written beside `program`: a good rebuild of the pin's engine tree and the checkout's harness source. Returns it."""
        rec = dict(schema=1, program=program, program_sha256=T.sha(program), engine_arg=pin['engine_ref'], engine=f"{pin['engine_ref']} engine tree {pin['engine_tree']}", engine_ref=pin['engine_ref'],
                   engine_tree_archived=pin['engine_tree'], harness_source_sha256=harness, rustc='rustc 1.90.0 (fake)\nbinary: rustc', cargo='cargo 1.90.0 (fake)', machine='Linux 6.1.0 x86_64',
                   host='cloud-box-1', built_at='2026-10-09T22:00:00Z', rebuild_command=f"env HOME=/home/cloud bash /home/cloud/repo/rl/strength/build.sh {pin['engine_ref']} {program}")
        write(program + '.build.json', json.dumps(rec, indent=1) + '\n')
        return rec

    def test_the_pinned_program_has_no_rebuild_paragraph_and_its_self_checks_were_copied_from_the_pin(self):
        here = self.with_harness_source()
        self.set_pin(harness_source_sha256=here)
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        lines = self.page().splitlines()
        self.assertNotIn('REBUILD', '\n'.join(lines))
        self.assertEqual(sum(1 for l in lines if l.startswith('- Self-check of') and f'({HOW_GIVEN})' in l), 2, lines)
        self.assertIn(f'- Harness source sha256 `{here[:12]}` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.', lines)
        self.assertIn('- School-morning rule: off (chosen at registration, for a machine that is not the laptop).', lines)
        self.assertIn(f"- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `{self.program}` sha256 `{self.pin['program_sha256'][:12]}`.", lines)
        self.assertEqual([l for l in lines if l.startswith('- Pin ')],
                         [f"- Pin `{self.pin_path}` sha256 `{T.sha(self.pin_path)[:12]}`: **NOT the committed pin** (HEAD has no rl/strength/slow_report_pin.json in {self.repo} (not a git repository, "
                          f'no commit, or the file is not committed){T.git_said(self.repo)}; allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)): what this page says about the program rests on '
                          'a pin that is not the committed one.'], 'this fixture\'s hand-made pin got through only by the test-only variable, and the page says so')
        self.assertEqual(sum(1 for l in lines if l.startswith('- Build record')), 0, 'the pinned binary has no build record')

    def test_a_checkout_that_is_not_the_pinned_source_is_said_so_on_the_page_of_a_pinned_run(self):
        here = self.with_harness_source()
        self.set_pin(harness_source_sha256='9' * 64)
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'- Harness source sha256 `999999999999` (what rl/strength/build.sh prints); the checkout this run was registered from has `{here[:12]}` '
                      '(so the pinned binary was not built from exactly that source).', self.page().splitlines())

    def test_a_checkout_with_no_harness_source_is_said_so_on_the_page_of_a_pinned_run(self):
        self.assertIsNone(sr.harness_source_sha256(self.repo), 'the fixture\'s checkout has no rl/strength/src')
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        self.assertIn(f"- Harness source sha256 `{self.pin['harness_source_sha256'][:12]}` (what rl/strength/build.sh prints); the checkout this run was registered from has no harness source "
                      '(rl/strength/src), so this could not be compared.', self.page().splitlines())
        self.assertNotIn('None', ' '.join(l for l in self.page().splitlines() if 'Harness source' in l))

    def test_a_replayed_self_check_on_the_pinned_program_is_said_to_be_replayed(self):
        here = self.with_harness_source()
        self.set_pin(harness_source_sha256=here, selfcheck=self.FAKE_CHECKS)
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertEqual(code, 0, out + err)
        lines = self.page().splitlines()
        self.assertEqual(sum(1 for l in lines if l.startswith('- Self-check of') and f'({HOW_REPLAYED_FILE})' in l), 2, lines)  # (the fixture's hand-made pin is let through by the test-only variable)
        self.assertNotIn('REBUILD', '\n'.join(lines), 'replaying the self-checks on the pinned binary does not make it a rebuild')
        self.assertNotIn('NOT the pinned binary', '\n'.join(lines))

    def test_the_school_morning_choice_on_the_page_is_the_one_registered_with_its_days(self):
        code, out, err = self.cli('--deals', '1', school='on')
        self.assertEqual(code, 0, out + err)
        self.assertIn('- School-morning rule: on (mon,tue,wed,thu,fri).', self.page().splitlines())
        shutil.rmtree(self.out_root)
        code, out, err = self.cli('--deals', '1', '--school-days', 'mon,tue', school='on')  # (the fixture's clock is a Saturday: no wait)
        self.assertEqual(code, 0, out + err)
        self.assertIn('- School-morning rule: on (mon,tue).', self.page().splitlines())
        shutil.rmtree(self.out_root)
        code, out, err = self.cli('--deals', '1', school='off')
        self.assertEqual(code, 0, out + err)
        self.assertIn('- School-morning rule: off (chosen at registration, for a machine that is not the laptop).', self.page().splitlines())

    def test_a_rebuild_is_named_as_one_with_both_self_checks_replayed_and_the_program_it_ran(self):
        here = self.with_harness_source()
        pin = self.set_pin(program='/cloud/pinned/strength', program_sha256='5' * 64, harness_source_sha256=here, selfcheck=self.FAKE_CHECKS)
        rec = self.write_record(self.program, pin, here)
        code, out, err = self.cli('--deals', '1', '--program', self.program)
        self.assertEqual(code, 0, out + err)
        lines = self.page().splitlines()
        host = socket.gethostname()
        self.assertIn(f"- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `{self.program}` sha256 `{T.sha(self.program)[:12]}`.", lines)
        self.assertIn(rebuild_paragraph(host=f' ({host})', digests=FILE_DIGESTS, pinned='/cloud/pinned/strength', sha12='555555555555'), lines)
        self.assertIn(f"- Build record `fake_kx3_strength.build.json` sha256 `{T.sha(self.program + '.build.json')[:12]}`: engine {rec['engine_arg']} -> tree as archived "
                      f"`{pin['engine_tree'][:12]}` (the pin's is `{pin['engine_tree'][:12]}`), harness source `{here[:12]}`, rustc 1.90.0 (fake), cargo 1.90.0 (fake), built 2026-10-09T22:00:00Z "
                      f"on cloud-box-1 (Linux 6.1.0 x86_64); to rebuild the same bytes after a restart: `{rec['rebuild_command']}`.", lines)
        self.assertEqual(sum(1 for l in lines if l.startswith('- Self-check of') and f'({HOW_REPLAYED_FILE})' in l), 2, lines)
        self.assertIn(f'- Harness source sha256 `{here[:12]}` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.', lines)
        self.assertNotIn(pin['program'], '\n'.join(l for l in lines if l.startswith('- Pilots')))


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
        self.assertTrue(lines[4].startswith('That range includes no gain at all') or lines[4].startswith('That range does not include no gain'), lines[4])
        for l in lines:
            self.assertNotIn('**', l)
            self.assertNotIn('`', l)
            self.assertFalse(l.startswith(('#', '|', '- ')), l)

    def test_a_partial_page_starts_with_its_question_then_its_banner_and_echoes_nothing_from_the_tables(self):
        t, man, games = self.run_dir(deals=2)
        lines = sr.console_lines(self.rewrite(t, games[:37]))
        self.assertEqual(lines[0], PAGE_QUESTION)
        self.assertEqual(lines[1], banner('18 kx3 games + 19 cheap km3 baseline games', 37).replace('**', ''))
        self.assertTrue(lines[2].startswith('Size: 18 kx3 games + 19 cheap km3 baseline games so far, of 32 kx3 games'), lines[2])
        self.assertEqual(len(lines), 6, lines)
        self.assertEqual([l for l in lines if l.startswith('|') or 'When my-list' in l or 'took' in l], [])

    def test_the_terminal_gets_exactly_the_lines_of_what_it_says_and_nothing_else(self):
        """console_lines is the lines of the section '## What it says' (the sub-heading dropped, markdown removed), whole or partial, with an error note or without."""
        k2 = 'my-list|t-altaria|0|0|X'
        for kw, keep in ((dict(), 64), (dict(paired=False), 64), (dict(), 37), (dict(paired=False), 37), (dict(errors=[(k2, 'x')]), 37)):
            t, man, games = self.run_dir(deals=2, **kw)
            text = self.rewrite(t, [g for g in games[:keep] if g['key'] != k2] if 'errors' in kw else games[:keep])
            sec = self.part(text, '## What it says')
            want = [l.replace('**', '').replace('`', '').strip() for l in sec.splitlines() if l.strip() and not l.startswith('#')]
            self.assertEqual(sr.console_lines(text), want, (kw, keep))
        self.assertEqual(sr.console_lines('# no such section\n\nonly text\n'), [])

    def test_a_run_that_stops_early_writes_the_partial_page_and_says_so(self):
        t, man, games = self.run_dir(deals=2, complete=False)
        quiet = os.path.join(tempfile.mkdtemp(), 'quiet_report.py')
        self.addCleanup(shutil.rmtree, os.path.dirname(quiet), True)
        write(quiet, 'pass\n')
        said = []
        with mock.patch.object(sr, 'REPORT', quiet):
            sr.best_effort_pages(t, said.append)
        self.assertEqual(said, ['SLOW_REPORT.md (partial) written before stopping'])
        self.assertIn(banner('16 kx3 games + 16 cheap km3 baseline games', 32), read(os.path.join(t, 'SLOW_REPORT.md')).splitlines())

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
                f"less than the width of such a range ({printed_width(lo, hi)} points here), and more deals narrow it.\n"
                "- There is no pass or fail line: whether my-list is worth playing is a call for the player.")
        self.assertEqual(self.part(text, "## What these numbers can and can't say").strip(), want)

    def test_the_width_in_that_section_is_the_whole_width_of_the_range_in_points_not_half(self):
        for kw in (dict(deals=1), dict(deals=5, win=lambda o, d, s: 'deck')):  # a symmetric range and a lopsided one clipped at 100%
            t, man, games, text = self.build(**kw)
            p, lo, hi = wilson95(T.x_scores(games))
            width = printed_width(lo, hi)
            self.assertIn(f'less than the width of such a range ({width} points here)', text)
            self.assertNotIn(f'({100 * (hi - lo) / 2:.1f} points here)', text)

    def test_the_width_is_worked_out_from_the_two_ends_the_page_prints_so_it_never_disagrees_with_them(self):
        """The ends are printed rounded to a tenth; a width from the unrounded numbers can differ from the difference of the printed ones by a tenth (30.449 and 50.451 print as 30.4%
        and 50.5%, 20.0 apart before rounding and 20.1 as printed). The page says the width a reader gets from the two numbers in front of them."""
        t, man, games, text = self.build(deals=2)
        with mock.patch.object(sr, 'wilson_range', lambda xs: (0.4, 0.30449, 0.50451)):
            text = sr.write_slow_report(t)
        self.assertIn('probably between 30.4% and 50.5%', text)
        self.assertIn('less than the width of such a range (20.1 points here), and more deals narrow it.', text)
        self.assertNotIn('(20.0 points here)', text)
        self.assertEqual(sr.wilson_width_points(0.30449, 0.50451), '20.1')
        for lo, hi, want in ((0.0, 1.0, '100.0'), (0.7061, 0.8782, '17.2'), (0.2, 0.2, '0.0'), (0.0, 0.3641, '36.4'), (0.28, 0.72, '44.0')):
            self.assertEqual(sr.wilson_width_points(lo, hi), want, (lo, hi))


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
        self.assertEqual(len(lines), 11 + len(sr.console_lines(page)), lines)
        self.assertEqual(lines[0], PlanLines.QUESTION, 'the question is the very first line a new run prints')
        self.assertTrue(lines[1].startswith('plan: my-list ('))
        self.assertTrue(lines[2].startswith('size: 16 kx3 games + 16 cheap km3 baseline games on the same deals (32 games in all; the km3 games take about a second each); '
                                            'the time is for the 16 kx3 games: about '), lines[2])
        self.assertEqual(lines[3], PlanLines.SCHOOL_OFF, 'the fixture registers with the rule off')
        self.assertEqual(lines[4], bypassed_pin_line(self), 'the pin line: the fixture\'s hand-made pin is let through by the test-only variable, and the plan says so')
        self.assertTrue(lines[5].startswith('stage use (not development evidence; the held-out lock is untouched), seeds from '))
        self.assertTrue(lines[5].endswith(', with the comparison with km3 on the same deals in the page, no pass or fail line'), lines[5])
        self.assertEqual(lines[6], f'pre-registered 32 games (8 pairs, 1 deal x 2 seats x 2 arms) in {d}', 'one deal is "1 deal", not "1 deals"')
        self.assertRegex(lines[7], r'^manifest sha256 [0-9a-f]{64}$')
        self.assertEqual(lines[8:11], [f'registered in {d} before any game', 'running: 32 games to go, 2 at a time', f'SLOW_REPORT.md written in {d}'])
        self.assertEqual(lines[11:], sr.console_lines(page))
        self.assertEqual(lines[11], PAGE_QUESTION, 'and the page it wrote starts with its question again')

    def test_where_a_cut_run_stands_says_the_question_then_how_many_games_of_each_pilot_are_played_and_how_to_resume(self):
        outs, pages = self.session()
        self.assertEqual(outs['where the run stands'].splitlines(),
                         [TAG + PlanLines.QUESTION,
                          TAG + 'played so far: 5 kx3 games + 5 cheap km3 baseline games of 32 kx3 games + 32 cheap km3 baseline games planned; '
                                '27 kx3 games + 27 cheap km3 baseline games to go '
                                f'(resume with: python3 rl/strength/slow_report.py --dir {self.rundir()} --school-rule off)',
                          TAG + 'dry run: nothing written'])

    def test_a_cut_run_echoes_its_question_and_its_banner_and_a_finished_one_echoes_the_page_it_wrote(self):
        outs, pages = self.session()
        cut = outs['a registration and the first games'].splitlines()
        self.assertIn(TAG + banner('5 kx3 games + 5 cheap km3 baseline games', 10).replace('**', ''), cut)
        self.assertLess(cut.index(TAG + PAGE_QUESTION), cut.index(TAG + banner('5 kx3 games + 5 cheap km3 baseline games', 10).replace('**', '')))
        self.assertIn(TAG + f'pre-registered 64 games (8 pairs, 2 deals x 2 seats x 2 arms) in {self.rundir()}', cut)
        done = outs['the rest of the games'].splitlines()
        tail = done[done.index(TAG + f'SLOW_REPORT.md written in {self.rundir()}') + 1:]
        self.assertEqual(tail, [TAG + l for l in sr.console_lines(pages['the rest of the games'])])
        self.assertEqual(tail[0], TAG + PAGE_QUESTION)
        self.assertNotIn('PARTIAL', outs['the rest of the games'])


class PlayItWith(T.World):
    """`--register-only` ends by saying how to play what it registered: the resume command of the registration (carrying the school-morning choice, quoted for the shell), and that
    --max-games plays it in slices."""
    CASES = [  # (--school-rule given, other options), what the command adds
        (('off', ()), ' --school-rule off'),
        ((None, ()), ''),
        (('on', ('--school-days', 'sat,sun')), ' --school-days sat,sun'),
        (('on', ('--school-days', '')), " --school-days ''"),
        (('on', ('--school-days', 'mon, tue')), " --school-days 'mon, tue'"),
    ]

    def last_lines(self, school, extra):
        code, out, err = self.cli('--deals', '1', '--register-only', *extra, school=school)
        self.assertEqual(code, 0, out + err)
        return out.splitlines()

    def test_a_registration_only_ends_with_the_command_that_plays_it_with_the_school_choice_in_it(self):
        for (school, extra), added in self.CASES:
            with self.subTest(school=school, extra=extra):
                self.make()
                lines = self.last_lines(school, extra)
                d = self.rundir()
                self.assertEqual(lines[-2:], [TAG + f'registered in {d} before any game',
                                              TAG + f'play it with: python3 rl/strength/slow_report.py --dir {d}{added} (add --max-games N to play in slices)'])
                self.assertEqual(sum(1 for l in lines if 'play it with' in l), 1)
                command = lines[-1][len(TAG + 'play it with: '):-len(' (add --max-games N to play in slices)')]
                self.assertEqual(command, json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command'], 'the registered command, word for word')

    def test_the_folder_of_a_registration_is_quoted_for_the_shell_in_that_line(self):
        self.out_root = os.path.join(self.tmp, 'results with a space')
        lines = self.last_lines('off', ())
        d = self.rundir()
        self.assertEqual(lines[-1], TAG + f"play it with: python3 rl/strength/slow_report.py --dir {shlex.quote(d)} --school-rule off (add --max-games N to play in slices)")
        self.assertTrue(shlex.quote(d).startswith("'"), 'the path really needed quoting')

    def test_a_registration_without_a_recorded_command_is_given_one_made_from_the_choice_it_registered(self):
        real = sr.build_config
        with mock.patch.object(sr, 'build_config', lambda **kw: real(**dict(kw, resume_command=None))):
            lines = self.last_lines('off', ())
        d = self.rundir()
        self.assertIsNone(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command'])
        self.assertEqual(lines[-1], TAG + f'play it with: python3 rl/strength/slow_report.py --dir {d} --school-rule off (add --max-games N to play in slices)')

    def test_only_a_registration_that_stops_there_says_how_to_play_it(self):
        for label, extra in (('a plan', ('--dry-run',)), ('a run', ()), ('a run in slices', ('--max-games', '3'))):
            with self.subTest(label):
                self.make()
                code, out, err = self.cli('--deals', '1', *extra)
                self.assertEqual(code, 0, out + err)
                self.assertNotIn('play it with', out)
        d = self.rundir()
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertNotIn('play it with', out)


class WhereARunStands(T.World):
    """`--dir RUNDIR --dry-run`: the question, then how many games of each pilot are played against what was planned, how many are left, and what a resume would do."""
    RESUME = 'python3 rl/strength/slow_report.py --dir {d} --school-rule off'

    def stands(self, d):
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False, school=None)
        self.assertEqual(code, 0, out + err)
        lines = out.splitlines()
        for l in lines:
            self.assertTrue(l.startswith(TAG), l)
        self.assertEqual(lines[-1], TAG + 'dry run: nothing written')
        return [l[len(TAG):] for l in lines[:-1]]

    def played_so_far(self, played, to_go, status, planned='16 kx3 games + 16 cheap km3 baseline games'):
        return f'played so far: {played} of {planned} planned; {to_go} to go ({status})'

    def test_before_any_game_it_says_the_question_then_nothing_played_and_everything_to_go(self):
        d = self.register()
        self.assertEqual(self.stands(d), [PlanLines.QUESTION, self.played_so_far('0 kx3 games + 0 cheap km3 baseline games', '16 kx3 games + 16 cheap km3 baseline games',
                                                                                  'resume with: ' + self.RESUME.format(d=d))])

    def test_each_pilots_games_are_counted_by_themselves_and_singular_at_one(self):
        d = self.register()
        code, out, err = self.cli('--dir', d, '--max-games', '3', deck=False)  # the program plays a km3 game, then the kx3 game of that deal and seat, then the next km3 game
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.stands(d), [PlanLines.QUESTION, self.played_so_far('1 kx3 game + 2 cheap km3 baseline games', '15 kx3 games + 14 cheap km3 baseline games',
                                                                                  'resume with: ' + self.RESUME.format(d=d))])
        code, out, err = self.cli('--dir', d, '--max-games', '28', deck=False)  # 31 in all: all 16 km3 games and 15 of the kx3 games
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.stands(d), [PlanLines.QUESTION, self.played_so_far('15 kx3 games + 16 cheap km3 baseline games', '1 kx3 game + 0 cheap km3 baseline games',
                                                                                  'resume with: ' + self.RESUME.format(d=d))])

    def test_a_finished_run_says_complete_and_nothing_to_go(self):
        d = self.register()
        self.assertEqual(self.cli('--dir', d, deck=False)[0], 0)
        self.assertEqual(self.stands(d), [PlanLines.QUESTION, self.played_so_far('16 kx3 games + 16 cheap km3 baseline games', '0 kx3 games + 0 cheap km3 baseline games', 'complete')])

    def test_all_the_kx3_games_without_the_baseline_games_is_not_complete(self):
        """Complete is every planned game of both pilots: the cheap km3 games are in the plan whether or not the page reports the comparison."""
        d = self.register()
        self.assertEqual(self.cli('--dir', d, deck=False)[0], 0)
        games = os.path.join(d, 'games.jsonl')
        kept = [l for l in read(games).splitlines() if json.loads(l)['arm'] == 'X']
        self.assertEqual(len(kept), 16)
        write(games, ''.join(l + '\n' for l in kept))
        self.assertEqual(self.stands(d), [PlanLines.QUESTION, self.played_so_far('16 kx3 games + 0 cheap km3 baseline games', '0 kx3 games + 16 cheap km3 baseline games',
                                                                                  'resume with: ' + self.RESUME.format(d=d))])

    def test_a_run_whose_inputs_changed_says_it_would_be_refused_and_why_instead_of_how_to_resume(self):
        d = self.register()
        write(self.deck, T.DECK_TEXT + '\n')
        lines = self.stands(d)
        self.assertEqual(lines[0], PlanLines.QUESTION)
        self.assertTrue(lines[1].startswith('played so far: 0 kx3 games + 0 cheap km3 baseline games of 16 kx3 games + 16 cheap km3 baseline games planned; '
                                            '16 kx3 games + 16 cheap km3 baseline games to go (it would be refused: my-list ('), lines[1])
        self.assertIn(') has changed since registration (sha256 ', lines[1])
        self.assertNotIn('resume with', lines[1])

    def test_a_run_registered_without_the_comparison_asks_the_shorter_question_and_still_counts_both_pilots(self):
        shutil.rmtree(self.out_root, ignore_errors=True)
        code, out, err = self.cli('--deals', '1', '--no-paired', '--register-only')
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        self.assertEqual(self.stands(d), [PlanLines.QUESTION_ALONE, self.played_so_far('0 kx3 games + 0 cheap km3 baseline games', '16 kx3 games + 16 cheap km3 baseline games',
                                                                                        'resume with: ' + self.RESUME.format(d=d))])

    def test_the_question_names_the_pilots_the_run_was_registered_with_not_the_pins_today(self):
        d = self.register()
        pin = json.loads(read(self.pin_path))
        pin.update(pilot='kz9', reference='kr1', pilot_label='kz9 (abc)', reference_label='kr1 (def)')
        write(self.pin_path, json.dumps(pin))
        lines = self.stands(d)
        self.assertEqual(lines[0], PlanLines.QUESTION)
        self.assertTrue(lines[1].startswith('played so far: 0 kx3 games + 0 cheap km3 baseline games of 16 kx3 games'), lines[1])

    def test_the_resume_command_is_the_registered_one_so_a_default_school_rule_adds_no_flag(self):
        shutil.rmtree(self.out_root, ignore_errors=True)
        code, out, err = self.cli('--deals', '1', '--register-only', school='on')
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        self.assertTrue(self.stands(d)[1].endswith(f'(resume with: python3 rl/strength/slow_report.py --dir {d})'))


class ConsoleMessages(T.World):
    def test_a_run_cut_by_max_games_says_how_to_resume(self):
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(out.splitlines().count(f'{TAG}stopped after --max-games 10{CUT_NOTE}; resume with: python3 rl/strength/slow_report.py --dir {self.rundir()} --school-rule off'), 1)

    def test_a_run_cut_by_max_games_says_that_the_limit_counts_games_of_both_pilots(self):
        """--max-games 10 is ten games of the two arms together, about five of them kx3 games: the line says so, so nobody reads it as ten kx3 games."""
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, out + err)
        line = [l for l in out.splitlines() if 'stopped after --max-games' in l]
        self.assertEqual(len(line), 1, out)
        self.assertIn(' (games across both arms, about half of them kx3 games); resume with: ', line[0])
        played = jsonl(os.path.join(self.rundir(), 'games.jsonl'))
        self.assertEqual((len(played), len([g for g in played if g['arm'] == 'X'])), (10, 5), 'ten games in all, five of them kx3 games')

    def test_a_run_cut_by_max_games_says_the_command_it_registered_with_the_school_choice_in_it(self):
        """The line is the registered resume command (the same as the dry run of the folder prints), not a made-up one: the school-morning choice is in it only when it was not the default."""
        code, out, err = self.cli('--deals', '2', '--max-games', '10', school='on')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(out.splitlines().count(f'{TAG}stopped after --max-games 10{CUT_NOTE}; resume with: python3 rl/strength/slow_report.py --dir {self.rundir()}'), 1, out)
        code, out, err = self.cli('--dir', self.rundir(), '--dry-run', deck=False, school=None)
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'(resume with: python3 rl/strength/slow_report.py --dir {self.rundir()})', out)
        shutil.rmtree(self.out_root)
        code, out, err = self.cli('--deals', '2', '--max-games', '10', '--school-days', 'mon,tue', school='on')  # (the fixture's clock is a Saturday: no wait)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(out.splitlines().count(f'{TAG}stopped after --max-games 10{CUT_NOTE}; resume with: python3 rl/strength/slow_report.py --dir {self.rundir()} --school-days mon,tue'), 1, out)

    def test_a_run_folder_with_a_space_in_its_path_is_quoted_in_the_line_that_says_how_to_resume(self):
        self.out_root = os.path.join(self.repo, 'rl', 'results', 'slow reports')
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, out + err)
        folder = self.rundir()
        self.assertIn(' ', folder)
        self.assertEqual(out.splitlines().count(f"{TAG}stopped after --max-games 10{CUT_NOTE}; resume with: python3 rl/strength/slow_report.py --dir '{folder}' --school-rule off"), 1, out)
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

    def events(self, d=None):
        return jsonl(os.path.join(d or self.rundir(), 'slow_report_log.jsonl'))

    def names(self, d=None, skip=('env_scrubbed',)):
        return [e['event'] for e in self.events(d) if e['event'] not in skip]

    def sitting_calls(self, d=None):
        return [e for e in self.events(d) if e['event'] == 'sitting_call']

    @staticmethod
    def asked_for(call):
        """What a sitting_call event says about the call, in this order: the school-morning rule and days, the threads, the game limit, whether the school choice was overridden."""
        return (call['school_rule'], call['school_days'], call['threads'], call['max_games'], call['school_choice_overridden'])

    def test_a_full_run_logs_each_step_in_order_with_both_pilots_and_a_utc_time(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        events = jsonl(os.path.join(d, 'slow_report_log.jsonl'))
        self.assertEqual([e['event'] for e in events if e['event'] != 'env_scrubbed'], ['registered', 'sitting_call', 'slice_start', 'slice_end', 'complete', 'report_written'])
        for e in events:
            self.assertEqual((e['pilot'], e['reference']), ('kx3', 'km3'), e)
            self.assertRegex(e['at'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        by = {e['event']: e for e in events}
        self.assertEqual({k: v for k, v in by['sitting_call'].items() if k != 'at'},
                         {'event': 'sitting_call', 'pilot': 'kx3', 'reference': 'km3', 'school_rule': 'off', 'school_days': 'mon,tue,wed,thu,fri', 'threads': 2, 'max_games': None,
                          'school_choice_overridden': False, 'program_sha256': T.sha(self.program)}, 'what the call was given, and the program it ran with, and nothing else')
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

    def test_each_call_that_plays_logs_one_sitting_call_before_its_sittings_saying_what_it_was_given(self):
        d = self.register('--threads', '3', '--school-days', 'mon,tue', school='on')  # (the fixture's clock is a Saturday: no school wait)
        self.assertEqual(self.names(d), ['registered'], 'registering alone plays nothing and logs no sitting')
        calls = (('plain, with a limit', ('--max-games', '4'), None, ('on', 'mon,tue', 3, 4, False)),
                 ('other threads and the rule off', ('--max-games', '4', '--threads', '5'), 'off', ('off', 'mon,tue', 5, 4, True)),
                 ('no school days', ('--max-games', '4', '--school-days', ''), None, ('on', '', 3, 4, True)),
                 ('the registered rule spelled out is not an override', ('--max-games', '4'), 'on', ('on', 'mon,tue', 3, 4, False)),
                 ('the registered days spelled out are not an override either', ('--max-games', '4', '--school-days', 'mon,tue'), None, ('on', 'mon,tue', 3, 4, False)),
                 ('plain, to the end', (), None, ('on', 'mon,tue', 3, None, False)))
        for label, extra, school, want in calls:
            with self.subTest(label):
                code, out, err = self.cli('--dir', d, *extra, deck=False, school=school)
                self.assertEqual(code, 0, out + err)
                self.assertEqual(self.asked_for(self.sitting_calls(d)[-1]), want)
        self.assertEqual([self.asked_for(c) for c in self.sitting_calls(d)], [c[3] for c in calls])
        self.assertEqual(self.names(d, skip=('env_scrubbed', 'report_written')),
                         ['registered'] + ['sitting_call', 'slice_start', 'slice_end'] * 6 + ['complete'], 'one per call, each before the sitting it asks for')

    def test_running_exactly_the_printed_resume_command_is_not_an_override_and_any_other_school_choice_is(self):
        """The resume command a registration prints (and --max-games, the dry run and the page say again) carries the registered school choice: running it as it stands is not an
        override, whatever the choice was. A choice that differs from the registered one is."""
        for school, extra in (('off', ()), (None, ()), ('on', ('--school-days', 'sat,sun')), ('on', ('--school-days', '')), ('on', ('--school-days', 'mon, tue'))):
            with self.subTest(school=school, extra=extra):
                self.make()
                d = self.register(*extra, school=school)
                cmd = shlex.split(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command'])
                self.assertEqual(cmd[:4], ['python3', 'rl/strength/slow_report.py', '--dir', d])
                code, out, err = self.cli(*cmd[2:], '--max-games', '2', deck=False, school=None)
                self.assertEqual(code, 0, out + err)
                self.assertIs(self.sitting_calls(d)[-1]['school_choice_overridden'], False, cmd)
                other = 'off' if school != 'off' else 'on'
                code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False, school=other)
                self.assertEqual(code, 0, out + err)
                self.assertIs(self.sitting_calls(d)[-1]['school_choice_overridden'], True, other)

    def test_the_options_of_a_registration_that_goes_on_to_play_are_its_choice_and_not_an_override(self):
        code, out, err = self.cli('--deals', '1', '--threads', '3', '--max-games', '5', '--school-days', 'mon,tue', school='on')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.names(), ['registered', 'sitting_call', 'slice_start', 'slice_end', 'report_written'])
        self.assertEqual([self.asked_for(c) for c in self.sitting_calls()], [('on', 'mon,tue', 3, 5, False)])

    def test_a_call_that_finds_nothing_left_to_play_still_logs_the_sitting_call_before_complete(self):
        self.assertEqual(self.cli('--deals', '1')[0], 0)
        d = self.rundir()
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.names(d, skip=('env_scrubbed', 'report_written'))[-2:], ['sitting_call', 'complete'])
        self.assertEqual(len(self.sitting_calls(d)), 2)

    def test_no_sitting_call_is_logged_by_a_call_that_plays_nothing_or_is_refused_before_it_may_play(self):
        d = self.register()
        for extra in (('--dry-run',), ('--report-only',)):
            self.assertEqual(self.cli('--dir', d, *extra, deck=False)[0], 0, extra)
        self.assertEqual(self.names(d), ['registered', 'report_written'], 'only the page was written')
        original = read(self.deck)
        write(self.deck, original + '\n')  # the deck is no longer the registered one: refused before the lock
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertIn('REFUSED: the files this run was registered with are not the ones on disk', str(code))
        write(self.deck, original)
        lock = os.path.join(d, 'slow_report.lock')
        fd = os.open(lock, os.O_CREAT | os.O_RDWR)  # another wrapper holds the run
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertIn('REFUSED: another slow_report.py', str(code))
        self.assertEqual(self.names(d), ['registered', 'report_written'], 'the call that was refused the lock logged no sitting')
        self.assertEqual(self.sitting_calls(d), [])

    def test_the_sitting_call_is_logged_with_the_lock_already_held_and_before_the_first_sitting(self):
        d = self.register()
        seen = []
        real = sr.log_event

        def spy(rundir, event, **kw):
            if event in ('sitting_call', 'slice_start'):
                probe = os.open(os.path.join(rundir, 'slow_report.lock'), os.O_RDWR)
                try:
                    fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    held = False
                except BlockingIOError:
                    held = True
                finally:
                    os.close(probe)
                seen.append((event, held))
            return real(rundir, event, **kw)
        with mock.patch.object(sr, 'log_event', spy):
            self.assertEqual(self.cli('--dir', d, '--max-games', '2', deck=False)[0], 0)
        self.assertEqual(seen, [('sitting_call', True), ('slice_start', True)])


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


def processes_running_from(folder):
    """The pids (Linux /proc) of the processes, other than this one, whose command line names `folder`: what a test left running from its own temporary folder."""
    out = []
    for p in os.listdir('/proc'):
        if p.isdigit() and int(p) != os.getpid():
            try:
                with open(f'/proc/{p}/cmdline', 'rb') as f:
                    if folder.encode() in f.read():
                        out.append(int(p))
            except OSError:
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
            self.assertEqual(lines[0], TAG + PlanLines.QUESTION, lines)
            self.assertTrue(lines[1].startswith(TAG + 'plan: my-list ('), lines)
            self.assertIn(TAG + 'running: 32 games to go, 2 at a time', lines)
        finally:
            proc.terminate()  # SIGTERM: the wrapper stops the program, writes the partial page and exits
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            proc.stdout.close()
            left = processes_running_from(self.tmp)  # the program the wrapper started may not have been a child yet when `kids` was read: anything still running from this test's own folder
            for pid in set(kids) | set(left):  # only what this wrapper started, and only if it is somehow still there
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.assertEqual(left, [], 'SIGTERM stopped the program the wrapper had started: nothing of this test is left running')


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

    def build(self, win_x=None, win_ref=None, dev=None, tool=None, dev_decks=(TE.DECK, TE.OTHER), tool_decks=(TE.DECK,)):
        """dev(rows) and tool(rows) edit the game records of that run before they are written (in place: rows[:] = ... may drop games); the gate-3 run is made from the
        edited development games. dev_decks and tool_decks are the decks each run holds (the gate-3 run's decks are among the development run's)."""
        with mock.patch.object(TE, 'win_x', win_x or TE.win_x), mock.patch.object(TE, 'win_ref', win_ref or TE.win_ref):
            self.dev, _ = TE.make_run(self.tmp, 'strength_dev', pilot='kx3', decks=dev_decks)
        rows = self.rows(self.dev)
        if dev:
            dev(rows)
            self.put_rows(self.dev, rows)
        self.dev_games = {r['key']: r for r in rows}
        self.tool, _ = TE.make_run(self.tmp, 'strength_tool', pilot='kx3_r16_c12_z2_real_t0_poolmeta_tools', program='/home/dacz8976/kx/strength_tools',
                                   program_sha='cf73b2a4e858' + '0' * 52, decks=tool_decks, base=self.dev_games)
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
    @staticmethod
    def printed_width(m, half):
        """The width of the gain's range as its two printed ends give it (each end rounded once from the unrounded number, cut at the ends of the scale), worked out here by hand."""
        return f'{float(points(min(1.0, m + half))) - float(points(max(-1.0, m - half))):.1f}'

    def can_tell_paragraph(self):
        """What the 80-game range can tell and cannot tell, word for word, from the numbers worked out here: ((low, high) of the gain, the paragraph found, the paragraph wanted)."""
        text = self.page()
        xs = [SC[g['winner']] for g in self.deck_x(self.dev_games)]
        p, lo, hi = wilson95(xs)
        n, m, sd, half = self.stats(self.gain_over_km3())
        glo, ghi = m - half, m + half
        if glo <= 0 <= ghi:
            note = (f'That range includes no gain at all: these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. '
                    f'They do argue against a gain much larger than {100 * ghi:.1f} points or a loss much larger than {100 * abs(glo):.1f} points; a smaller difference needs more deals. ')
        else:
            note = (f"That range does not include no gain: on these {n} paired games kx3 did {'better' if glo > 0 else 'worse'} than km3. "
                    f'It does not say by exactly how much: that part of the range is as wide as {n} paired games make it. ')
        want = (f"What the {len(xs)}-game range can tell and cannot tell: it can tell whether kx3 plays this deck near, clearly above or clearly below an even score against these 8 lists "
                f"({pc(lo)} to {pc(hi)} here), and it can tell a large gain over km3 from none at all (the gain's range is {self.printed_width(m, half)} points wide). {note}"
                f'It cannot tell a gain of a point or two from a gain of ten: {len(xs)} games decide only that much, and a wide range is a statement of how much {len(xs)} games decide, '
                f'not an answer of "nothing". More deals narrow it (the cost table in the slow-report plan gives the hours).')
        return (glo, ghi), [l for l in text.splitlines() if l.startswith('What the ')], want

    def test_a_gain_range_wholly_above_zero_says_better(self):
        self.build()
        (glo, ghi), found, want = self.can_tell_paragraph()
        self.assertGreater(glo, 0)
        self.assertEqual(found, [want])
        n, m, sd, half = self.stats(self.gain_over_km3())
        self.assertIn(f'- The gain: kx3 scored **{points(m)} points** compared with km3 on the same deals, probably between {points(m - half)} and {points(m + half)} points '
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
        self.assertIn(f'- The gain: kx3 scored **{points(m)} points** compared with km3 on the same deals, probably between {points(m - half)} and {points(m + half)} points '
                      f'(95% interval). That range refers to the {n} paired games, each a deal and seat played by both pilots: {n} kx3 games + {n} cheap km3 baseline games.', lines)
        self.assertEqual([l for l in lines if l.startswith('- The gain:') and ('more than' in l or 'less than' in l)], [],
                         'a negative gain is "compared with km3" too: never "more than" or "less than" it')

    def test_a_gain_range_that_includes_zero_says_what_the_deals_do_and_do_not_show(self):
        self.build(win_x=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp', win_ref=lambda o, d, s: 'deck' if (o + d + 2 * s) % 3 else 'opp')
        (glo, ghi), found, want = self.can_tell_paragraph()
        self.assertTrue(glo <= 0 <= ghi and abs(glo) != ghi)
        self.assertEqual(found, [want])

    def test_the_width_of_the_gain_range_is_the_whole_width_in_points_not_half_of_it(self):
        for kw in (dict(), dict(win_x=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck', win_ref=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp')):
            self.build(**kw)
            n, m, sd, half = self.stats(self.gain_over_km3())
            paragraph = [l for l in self.page().splitlines() if l.startswith('What the ')][0]
            self.assertIn(f"(the gain's range is {self.printed_width(m, half)} points wide)", paragraph)
            self.assertNotIn(f'{100 * half:.1f} points wide', paragraph)
            self.assertNotIn('plus or minus', paragraph)

    def test_the_width_agrees_with_the_two_ends_printed_on_the_same_page(self):
        """The width is worked out from the ends as printed (each rounded once), so 'between A and B points' and 'B minus A points wide' never disagree by a rounding step."""
        for kw in (dict(), dict(win_x=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck', win_ref=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp'),
                   dict(win_x=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp', win_ref=lambda o, d, s: 'deck' if (o + d + 2 * s) % 3 else 'opp')):
            self.build(**kw)
            text = self.page()
            a, b = re.search(r'^- The gain: .*? probably between ([+-]\d+\.\d) and ([+-]\d+\.\d) points \(95% interval\)', text, re.M).groups()
            width = float(re.search(r"the gain's range is (\d+\.\d) points wide", text).group(1))
            self.assertAlmostEqual(width, float(b) - float(a), places=6, msg=(a, b, width))

    def test_a_gain_that_is_the_same_in_every_paired_game_gets_no_range_no_width_and_no_note(self):
        same = lambda o, d, s: 'deck' if (o + d) % 2 else 'opp'
        self.build(win_x=same, win_ref=same)
        lines = self.page().splitlines()
        self.assertIn('- The gain: kx3 scored **+0.0 points** compared with km3 on the same deals; every one of the 80 paired games gave the same difference, '
                      'so no spread can be estimated from them.', lines)
        paragraph = [l for l in lines if l.startswith('What the ')]
        self.assertEqual(len(paragraph), 1)
        self.assertIn('and it can tell a large gain over km3 from none at all. It cannot tell a gain of a point or two from a gain of ten:', paragraph[0])
        for s in ('points wide', 'That range', 'includes no gain', 'does not include', 'argue against'):
            self.assertNotIn(s, paragraph[0])
        self.assertEqual([l for l in lines if l.startswith('- The gain') and 'probably between' in l], [])


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
        self.assertNotIn("registered before the first of this deck's games", dev_line)
        self.assertIn("2026-10-03T12:00:00Z (registered before the first of this deck's games); games.jsonl sha256", tool_line)

    HEAD = ('**Existing development evidence, not a fresh test.** Nothing was played for this page: it reads games that were already played, by the kx3 development run (2026-10-03) '
            'and by gate 3 of the Tool tie-break (2026-10-03), ')
    BOTH_ON_TIME = "both registered before the first of this deck's games (only 03-wailord-indeedee-wall's games were read, so that is all that was checked)."

    def test_the_top_of_the_page_says_both_registered_before_the_first_of_this_decks_games_only_when_both_were(self):
        self.build()
        self.assertEqual(self.page().splitlines()[2], self.HEAD + self.BOTH_ON_TIME)
        self.put_manifest(self.dev, created_at='2026-10-03T12:00:00Z')  # the very second the first game started: still before it
        self.assertEqual(self.page().splitlines()[2], self.HEAD + self.BOTH_ON_TIME)
        self.put_manifest(self.dev, created_at='2026-10-03T12:00:01Z')  # one second after
        text = self.page()
        self.assertEqual(text.splitlines()[2], self.HEAD + '**but not both were registered before their games: see "Where these games come from".**')
        self.assertNotIn('both registered before', text)

    def test_the_page_says_the_registration_check_covers_only_this_decks_games_and_never_claims_every_game(self):
        """The runs hold other decks' games, which this page does not read, so 'before any game' would say more than was checked: it is 'before the first of this deck's games'
        wherever the page speaks of the order, at the top and below, whichever way the order came out."""
        self.build()
        for label, edit in (('both on time', lambda: None), ('the development run late', lambda: self.put_manifest(self.dev, created_at='2026-10-03T13:00:00Z')),
                            ('no start times', lambda: [self.put_rows(d, [{k: v for k, v in r.items() if k != 'started_at'} for r in self.rows(d)]) for d in (self.dev, self.tool)])):
            edit()
            text = self.page()
            self.assertNotIn('before any game', text, label)
            self.assertNotIn('registered before any', text, label)
        self.build()
        text = self.page()
        self.assertEqual(text.count("registered before the first of this deck's games"), 3, 'once at the top and once for each run below')
        self.assertEqual(text.count("only 03-wailord-indeedee-wall's games were read, so that is all that was checked"), 1)
        self.assertIn('only deck 03-wailord-indeedee-wall was read (160 games).', text)

    def test_either_run_registered_late_is_enough_to_say_so_at_the_top_and_only_that_run_is_named_below(self):
        self.build()
        self.put_manifest(self.tool, created_at='2026-10-03T12:30:00Z')
        text = self.page()
        self.assertEqual(text.splitlines()[2], self.HEAD + '**but not both were registered before their games: see "Where these games come from".**')
        dev_line, tool_line = [l for l in text.split('## Where these games come from')[1].splitlines() if l.startswith(('- Development run', '- Gate 3'))]
        self.assertIn("2026-10-03T12:00:00Z (registered before the first of this deck's games); games.jsonl sha256", dev_line)
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
        self.assertIn(f'- On minus off: **{points(m)} points**, probably between {points(m - half)} and {points(m + half)} points '
                      '(95% interval; this range refers to the 80 paired games played with the Tool tie-break on and off).', lines)
        refs = {k: SC[self.dev_games[k[:-1] + 'ref']['winner']] for k in keys}
        _, m_on, _, h_on = self.stats([SC[self.tool_games[k]['winner']] - refs[k] for k in keys])
        _, m_off, _, h_off = self.stats([SC[self.dev_games[k]['winner']] - refs[k] for k in keys])
        self.assertNotEqual(points(m_on), points(m_off), 'the rule must make a difference to the context line, or a swap of on and off cannot show')
        self.assertIn(f'- For context, kx3 minus km3 on the same deals: with the Tool tie-break on {points(m_on)} points (probably between {points(m_on - h_on)} and {points(m_on + h_on)} points), '
                      f'off {points(m_off)} points (probably between {points(m_off - h_off)} and {points(m_off + h_off)} points); each range refers to the 80 paired games.', lines)
        p, wlo, whi = wilson95([1.0] * 3 + [0.0] * 77)
        closing = ('What this can tell and cannot tell: it can tell what the rule did on these 80 paired games (4 had a changed decision, 3 a changed winner), and it can put a bound on '
                   f'how often it changes a winner: 3 of 80 winners changed, which puts the share of deals whose winner the rule changes between about {100 * wlo:.1f} and {100 * whi:.1f} '
                   'in 100 (95% Wilson range on 3 of 80). It cannot tell what the rule does on other deals or other decks (gate 3 pooled 80 paired games, 80 kx3 games with the rule on '
                   'against the same deals with it off, over 1 deck on its own page), '
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
                   '(95% Wilson bound on 0 of 80). It cannot tell what the rule does on other deals or other decks (gate 3 pooled 80 paired games, 80 kx3 games with the rule on '
                   'against the same deals with it off, over 1 deck on its own page), '
                   'and a rule that acts in 3 of 80 games but changes no winner has not been shown to be harmless or useful: whether it would ever change a result on a deck like this is '
                   'a question for more deals.')
        self.assertEqual([l for l in lines if l.startswith('What this can tell and cannot tell')], [closing])
        self.assertNotIn('changed winners are what', closing)

    def test_the_pooled_pairs_and_decks_of_the_closing_sentence_are_counted_from_the_gate_3_run(self):
        third = '12-third-deck'

        def drop_thirty(rows):  # gate 3 holds all of the development run's decks, the third one with 30 of its 80 kx3 games gone: 80 + 80 + 50 pairs
            gone = [r['key'] for r in rows if r['deck'] == third and r['arm'] == 'X'][:30]
            rows[:] = [r for r in rows if r['key'] not in gone]
        self.build(dev_decks=(TE.DECK, TE.OTHER, third), tool_decks=(TE.DECK, TE.OTHER, third), tool=drop_thirty)
        closing = [l for l in self.page().splitlines() if l.startswith('What this can tell and cannot tell')]
        self.assertEqual(len(closing), 1)
        self.assertIn('It cannot tell what the rule does on other deals or other decks (gate 3 pooled 210 paired games, 210 kx3 games with the rule on against the same deals with it off, '
                      'over 3 decks on its own page), ', closing[0])
        self.assertNotIn('400 ', closing[0])
        self.assertNotIn('5 decks', closing[0])
        self.assertIn('on these 80 paired games', closing[0], 'the pairs the page itself reports are this deck\'s 80, not the pooled ones')

    def test_the_pooled_sentence_is_singular_for_one_deck_and_plural_for_two(self):
        self.build()
        self.assertIn('(gate 3 pooled 80 paired games, 80 kx3 games with the rule on against the same deals with it off, over 1 deck on its own page)', self.page())
        self.build(tool_decks=(TE.DECK, TE.OTHER))
        text = self.page()
        self.assertIn('(gate 3 pooled 160 paired games, 160 kx3 games with the rule on against the same deals with it off, over 2 decks on its own page)', text)
        self.assertNotIn('1 decks', text)

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
        self.assertEqual(context, [f'- For context, kx3 minus km3 on the same deals: with the Tool tie-break on {points(m_on)} points '
                                   f'(probably between {points(m_on - h_on)} and {points(m_on + h_on)} points), '
                                   'off +0.0 points (no spread to give: every difference is the same); each range refers to the 80 paired games.'])

    def test_the_context_line_gives_its_ranges_when_the_differences_vary(self):
        self.build(tool=gate_3_changes)
        context = [l for l in self.page().splitlines() if l.startswith('- For context')]
        self.assertEqual(len(context), 1)
        end = r'[+-]\d+\.\d'
        self.assertRegex(context[0], r'^- For context, kx3 minus km3 on the same deals: with the Tool tie-break on [+-]\d+\.\d points \(probably between ' + end + ' and ' + end
                         + r' points\), off [+-]\d+\.\d points \(probably between ' + end + ' and ' + end + r' points\); each range refers to the 80 paired games\.$')
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


class ExistingNoGiveOrTake(ExistingRuns):
    def test_no_variant_of_the_page_or_of_the_terminal_says_give_or_take_and_every_range_is_probably_between(self):
        def all_lost(rows):
            for r in rows:
                if r['deck'] == TE.DECK:
                    r['winner'] = 'opp'

        def all_won_with_the_rule(rows):
            for r in rows:
                if r['arm'] == 'X':
                    r['winner'] = 'deck'

        def every_third_won(rows):
            for i, r in enumerate([r for r in rows if r['arm'] == 'X']):
                r['winner'] = 'deck' if i % 3 == 0 else 'opp'
        same = lambda o, d, s: 'deck' if (o + d) % 2 else 'opp'
        cases = (('the default', {}), ('some decisions, winners and turns changed', dict(tool=gate_3_changes)),
                 ('the gain clearly positive', dict(win_x=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', win_ref=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')),
                 ('the gain clearly negative', dict(win_x=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck', win_ref=lambda o, d, s: 'deck' if (o + d + s) % 3 else 'opp')),
                 ('no spread in the gain', dict(win_x=same, win_ref=same)), ('no spread anywhere but the rule', dict(dev=all_lost, tool=all_won_with_the_rule)),
                 ('spread with the rule on only', dict(dev=all_lost, tool=every_third_won)),
                 ('three decks in gate 3', dict(dev_decks=(TE.DECK, TE.OTHER, '12-third-deck'), tool_decks=(TE.DECK, TE.OTHER, '12-third-deck'))))
        for label, kw in cases:
            self.build(**kw)
            code, out, err = self.go()
            self.assertEqual(code, 0, label + err)
            text = read(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md'))
            for words in SYMMETRIC_RANGE_WORDS:
                self.assertNotIn(words, text + out, f'{label}: {words!r}')
            self.assertIn('probably between', text, label)
            ranged = re.findall(r'probably between [+-]?\d+\.\d%? and [+-]?\d+\.\d%?(?: points)?(?: \(cut at the ends of the possible scale\))? \(95% interval', text)
            self.assertEqual(len(ranged), text.count('(95% interval'), f'{label}: every 95% interval is written as "probably between A and B"')
