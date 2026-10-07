#!/usr/bin/env python3
"""Tests for the run loop of slow_report.py and for the school-morning rule on the real command line (the third review round).

  cd rl/strength && python3 -B -m unittest -v test_slow_report_runloop

test_slow_report.py pins the arithmetic of the rule (school_action) and a few runs against a real fake program. This file pins what the loop does with it, so that it
is fast and cannot race a child process: the program is pretended by a script (Sittings: each start plays what the script says into games.jsonl, then ends at once or
keeps "playing" a game that never finishes until the wrapper stops it) and the clock never really waits (QuickClock: a night of 13 hours of polling takes
milliseconds). One test runs the real fake program on the same clock, gated on the program being in flight. Every test has a 10 s alarm, and a clock that is slept on
20,000 times fails (the longest honest test sleeps about 9,400 times), so a loop guard that stops working fails the suite at once instead of waiting for minutes.

Fast versions of what test_slow_report.py does slowly (those stay as they are): CutsWithoutProgress.test_three_cuts_in_a_row... (0.1 s; the old one 36 s),
RealProgramCut (0.2 s, a real program on the same clock; the old one 9 s), WaitingForFivePm (the old ones 8 s, 4 s and 4 s).

What is pinned:
  * the school days of the command line (Monday to Friday, not Saturday or Sunday) and the poll interval, the kill at 6:30 am and not later, the part-minute
    --stop-after-min, the last minute before 5:15 am;
  * the count of cuts with no game finished (reset by progress and by a sitting that was not cut), the no-progress guard of a resumed run, --max-games as a budget for
    the whole call (cuts included, the exact finish logged as complete, the message that says how to resume);
  * what is checked before every sitting: the program, the deck and the panel files, manifest.json; what a resume keeps from the registration (threads, headline,
    scrub list) and what a changed pin only gets a note; what `--dir --dry-run` says; a moved checkout;
  * the environment scrub on every sitting, a prefix and not a substring;
  * what a stop leaves behind (the partial page and its console note) for Ctrl-C and for a failing program, a failing engineering report;
  * the lock file during a run: the process group of the program playing now is noted in it after every start, it is gone when the run is over, and it stays
    (with that group in it) when the wrapper leaves while a program it started is still running;
  * the self-check under the school rule (refused in school hours, bound by the morning cut, stopped on Ctrl-C, low priority, its own process group).
"""
import contextlib, datetime, io, json, os, shutil, signal, subprocess, sys, tempfile, threading, time, types, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402
import test_slow_report as T  # noqa: E402  (World: a temporary repository with a fake pinned program; Timed; the file helpers)

UTC = datetime.timezone.utc
ALARM_S = 10
HEADLINE = '[kx3 (d513e37b) on my-list v km3 on the public panel]'


def at(day, hour, minute=0, second=0, month=10):
    """A Chicago time in October 2026: the 5th is a Monday, the 7th a Wednesday, the 10th a Saturday."""
    return datetime.datetime(2026, month, day, hour, minute, second, tzinfo=T.CHI)


def flag(cmd, name):
    return cmd[cmd.index(name) + 1] if name in cmd else None


class Enough(Exception):
    """Raised by a spawn that only wants to see when and how the program would have been started."""


class QuickClock:
    """A local clock for the run loop that never really waits: sleep(s) moves now() forward by s seconds. hooks run once when the clock first reaches their time;
    a gate (time, predicate) holds the clock back, in real time, from passing `time` until the predicate is true (a real program must be in flight, or done)."""
    MAX_SLEEPS = 20_000

    def __init__(self, start):
        self.t = start
        self.slept = []
        self.hooks = []
        self.gates = []

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        if len(self.slept) > self.MAX_SLEEPS:
            raise AssertionError(f'the run loop slept {self.MAX_SLEEPS} times and is still going: it is spinning')
        new = (self.t.astimezone(UTC) + datetime.timedelta(seconds=seconds)).astimezone(T.CHI)
        for when, ready in self.gates:
            if new >= when:
                deadline = time.time() + 10
                while not ready() and time.time() < deadline:
                    time.sleep(0.005)
        self.t = new
        for hook in [h for h in self.hooks if self.t >= h[0]]:
            self.hooks.remove(hook)
            hook[1]()


class FakeProc:
    """The part of a Popen the run loop uses. Its pid is no real process, and every test that cuts a sitting replaces stop_group (Sittings.stop)."""
    pid = 2 ** 22 + 1
    _logfh = None

    def __init__(self, returncode):
        self.returncode = returncode

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


def game_record(man, key):
    """A finished game in the format of the real program (the same shape the fake program in test_slow_report writes)."""
    dn, on, deal, seat, arm = key.split('|')
    deal, seat = int(deal), int(seat)
    seed = man['seed_base'] + [o['name'] for o in man['opponents']].index(on) * man['pair_stride'] + deal
    h = (seed * 7 + seat * 3 + (5 if arm == 'X' else 0)) % 10
    return {'key': key, 'deck': dn, 'opp': on, 'deal': deal, 'seat': seat, 'arm': arm, 'seed': seed,
            'pilot_deck': man['pilot'] if arm == 'X' else man['reference'], 'pilot_opp': man['reference'], 'first': 'deck' if seat == 0 else 'opp',
            'winner': 'deck' if h < 5 else ('tie' if h == 5 else 'opp'), 'points': [3, 1], 'turns': 9, 'plies': 40, 'wall_s': 100.0 if arm == 'X' else 1.0,
            'moves_deck': {'n': 2, 'total_s': 0.02, 'ms': [10.0, 10.0]}, 'moves_opp': {'n': 1, 'total_s': 0.01, 'ms': [10.0]}, 'started_at': '2026-10-10T10:00:00Z'}


class Sittings:
    """The program, pretended. Each start follows the next step of the script:
      ('exit', n)      plays n games and ends at once with return code 0 ('exit', n, rc) with that return code;
      ('hang', n)      plays n games and then keeps running on a game that never finishes, until the wrapper stops it;
      ('rest',)        plays every game still missing and ends.
    A step never plays more than --max-games, as the real program does. A start beyond the script fails the test."""

    def __init__(self, test, rundir, *steps, on_spawn=None):
        self.test, self.rundir, self.steps, self.on_spawn = test, rundir, steps, on_spawn
        self.man = sr.load_registered(rundir)[0]
        self.calls = []  # one per start: at, cmd, env, max_games, stop_after, played
        self.stops = []  # the clock times at which the wrapper stopped the program

    def __call__(self, cmd, env, logfile):
        n = len(self.calls)
        self.test.assertLess(n, len(self.steps), f'sitting {n + 1} was started, but the script has only {len(self.steps)}')
        step = self.steps[n]
        kind, count = step[0], (step[1] if len(step) > 1 else None)
        path = os.path.join(self.rundir, 'games.jsonl')
        have = {g['key'] for g in T.jsonl(path)}
        todo = [k for k in sr.planned_keys(self.man) if k not in have]
        play = todo if count is None else todo[:count]
        cap = flag(cmd, '--max-games')
        if cap is not None:
            play = play[:int(cap)]
        with open(path, 'a', encoding='utf-8') as f:
            for k in play:
                f.write(json.dumps(game_record(self.man, k)) + '\n')
        self.calls.append(types.SimpleNamespace(at=self.test.clock.now(), cmd=cmd, env=env, max_games=cap, stop_after=flag(cmd, '--stop-after-min'),
                                                threads=flag(cmd, '--threads'), played=len(play)))
        if self.on_spawn:
            self.on_spawn(len(self.calls))
        return FakeProc(None if kind == 'hang' else (step[2] if len(step) > 2 else 0))

    def stop(self, proc, grace_s=30):
        self.stops.append(self.test.clock.now())
        proc.returncode = -15


def arm_alarm(test):
    def too_slow(signum, frame):
        raise AssertionError(f'the test did not finish in {ALARM_S} s: the run loop is waiting or spinning')
    signal.signal(signal.SIGALRM, too_slow)  # T.Timed.tearDown puts its own handler back and cancels the alarm
    signal.alarm(ALARM_S)


class Quick(T.Timed):
    def setUp(self):
        super().setUp()
        arm_alarm(self)


class RunLoop(T.World):
    """A temporary repository with the fake pinned program, a registered-run helper and a clock that never waits, set to Wednesday 5:00 am."""

    def setUp(self):
        super().setUp()
        arm_alarm(self)
        self.clock = QuickClock(at(7, 5, 0))

    def sittings(self, rundir, *steps, **kw):
        s = Sittings(self, rundir, *steps, **kw)
        p = mock.patch.object(sr, 'stop_group', s.stop)
        p.start()
        self.addCleanup(p.stop)
        return s

    def go(self, rundir, spawn, *extra, school='on'):
        """Resume a registered run with the pretended program, polling once a minute."""
        return self.cli('--dir', rundir, '--poll-s', '60', *extra, school=school, spawn=spawn, deck=False)

    def raw(self, argv, spawn):
        """sr.main with exactly this command line (no options added)."""
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, spawn=spawn, deck_check=lambda p, r: [])
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def page(self, d):
        return T.read(os.path.join(d, 'SLOW_REPORT.md'))

    def games(self, d):
        return T.jsonl(os.path.join(d, 'games.jsonl'))

    def events(self, d):
        return [e['event'] for e in T.jsonl(os.path.join(d, 'slow_report_log.jsonl'))]

    def first_start(self, d, when, school=None):
        """(the time the program is first started, its command) for a resume at `when`; school=None leaves --school-rule and --school-days at their defaults."""
        self.clock = QuickClock(when)
        seen = []

        def spawn(cmd, env, logfile):
            seen.append((self.clock.now(), cmd))
            raise Enough
        with self.assertRaises(Enough):
            self.cli('--dir', d, school=school, spawn=spawn, deck=False)
        return seen[0]

    def set_env(self, **kw):
        old = {k: os.environ.get(k) for k in kw}
        os.environ.update(kw)

        def restore():
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.addCleanup(restore)


# ---------------------------------------------------------------------------------------------------------- the school days of the command line
class DefaultSchoolDays(RunLoop):
    """The school options left at their defaults (the rule's own tests pass the days in by hand): Monday to Friday are school days, the weekend is free."""

    def test_every_weekday_waits_for_5pm_and_the_weekend_does_not(self):
        d = self.register()
        for day, name in ((5, 'Monday'), (6, 'Tuesday'), (7, 'Wednesday'), (8, 'Thursday'), (9, 'Friday')):
            with self.subTest(name):
                started, cmd = self.first_start(d, at(day, 12))
                self.assertEqual(started, at(day, 17))
        for day, name in ((10, 'Saturday'), (11, 'Sunday')):
            with self.subTest(name):
                started, cmd = self.first_start(d, at(day, 12))
                self.assertEqual(started, at(day, 12), 'a weekend is free')

    def test_the_evenings_of_the_weekend_run_until_monday_morning(self):
        d = self.register()
        for day, name, minutes in ((9, 'Friday', 2 * 24 * 60 + 11 * 60 + 15), (10, 'Saturday', 24 * 60 + 11 * 60 + 15), (11, 'Sunday', 11 * 60 + 15)):
            with self.subTest(name):
                started, cmd = self.first_start(d, at(day, 18))
                self.assertEqual(started, at(day, 18))
                self.assertAlmostEqual(float(flag(cmd, '--stop-after-min')), minutes, msg='no new game after Monday 5:15 am, and not before')


# ---------------------------------------------------------------------------------------------------------- the cut at 6:30
class HalfPastSixCut(RunLoop):
    def test_a_program_still_running_at_630_is_stopped_then_and_not_later(self):
        self.clock = QuickClock(at(7, 5, 0, 30))
        d = self.register()
        s = self.sittings(d, ('hang', 3), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        cut = at(7, 6, 30)
        self.assertEqual(len(s.stops), 1)
        self.assertGreaterEqual(s.stops[0], cut)
        self.assertLess(s.stops[0], cut + datetime.timedelta(seconds=60), 'at most one poll after 6:30')
        self.assertAlmostEqual(float(s.calls[0].stop_after), 14.5, msg='told to start no game after 5:15 am (5:00:30 is 14.5 minutes before)')
        self.assertEqual(s.calls[1].at, at(7, 17, 0), 'the second sitting starts at 5 pm sharp')
        self.assertAlmostEqual(float(s.calls[1].stop_after), 12 * 60 + 15)
        log = T.jsonl(os.path.join(d, 'slow_report_log.jsonl'))
        logged = [e for e in log if e['event'] == 'stopped_for_school']
        self.assertEqual(len(logged), 1)
        self.assertEqual(datetime.datetime.fromisoformat(logged[0]['at_local']), s.stops[0], 'the log says when it was stopped')
        self.assertEqual([(e['killed_for_school'], e['new_games']) for e in log if e['event'] == 'slice_end'], [(True, 3), (False, 29)])
        self.assertEqual([(e['remaining_games'], e['hard_stop']) for e in log if e['event'] == 'slice_start'],
                         [(32, at(7, 6, 30).isoformat()), (29, at(8, 6, 30).isoformat())], 'each sitting is logged with what was left and when it will be cut')
        self.assertEqual(len(self.games(d)), 32)

    def test_with_the_default_poll_the_cut_comes_within_half_a_minute(self):
        self.clock = QuickClock(at(7, 5, 3, 10))
        d = self.register()
        s = self.sittings(d, ('hang', 0), ('rest',))
        argv = ['--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'on']  # no --poll-s
        code, out, err = self.raw(argv, s)
        self.assertEqual(code, 0, out + err)
        late = (s.stops[0] - at(7, 6, 30)).total_seconds()
        self.assertGreaterEqual(late, 0)
        self.assertLess(late, 30, 'RUN5: a program still running at 6:30 am is stopped; the default poll must keep that to seconds, not minutes')


class LastMinuteBeforeTheSoftStop(RunLoop):
    def start_at(self, when):
        self.make()
        d = self.register()
        self.clock = QuickClock(when)
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        return s

    def test_the_stop_after_value_keeps_its_fraction_of_a_minute(self):
        s = self.start_at(at(7, 4, 59, 40))
        self.assertEqual(s.calls[0].at, at(7, 4, 59, 40))
        self.assertLess(abs(float(s.calls[0].stop_after) - (15 + 20 / 60)), 1 / 60, 'told within a second of 5:15 am')

    def test_with_a_whole_minute_left_a_sitting_still_starts(self):
        s = self.start_at(at(7, 5, 14, 0))
        self.assertEqual(s.calls[0].at, at(7, 5, 14, 0))
        self.assertAlmostEqual(float(s.calls[0].stop_after), 1.0)

    def test_with_less_than_a_minute_left_nothing_starts_until_5pm(self):
        for left in (59, 30, 1):
            with self.subTest(seconds_left=left):
                s = self.start_at(at(7, 5, 15) - datetime.timedelta(seconds=left))
                self.assertEqual(s.calls[0].at, at(7, 17), 'no game could finish before the cut')
                self.assertAlmostEqual(self.clock.slept[0], left, msg='it waits for the cut itself first')
                self.assertAlmostEqual(float(s.calls[0].stop_after), 12 * 60 + 15)


class WhatTheRunLoopSays(RunLoop):
    """The lines a person reads at the terminal at 5 am, once, whole (the wording is the rule: what is about to happen, when, and how many games are left)."""

    def test_a_school_night_in_four_lines(self):
        d = self.register()
        s = self.sittings(d, ('hang', 3), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        lines = out.splitlines()
        want = [f'{HEADLINE} running: 32 games to go, 2 at a time, no new game after the school-morning cut (15 min from now)',
                f'{HEADLINE} school-morning rule: the program was stopped at 6:30; the game it was in the middle of will be played again',
                f'{HEADLINE} school-morning rule: waiting until Wed 17:00 Chicago time to start again (29 games to go)',
                f'{HEADLINE} running: 29 games to go, 2 at a time, no new game after the school-morning cut (735 min from now)']
        for line in want:
            self.assertIn(line, lines)
        self.assertEqual([lines.index(l) for l in want], sorted(lines.index(l) for l in want), 'in the order they happen')
        waiting = [e for e in T.jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'waiting_for_school']
        self.assertEqual([(e['until'], e['remaining_games']) for e in waiting], [(at(7, 17).isoformat(), 29)])

    def test_a_run_without_the_school_rule_says_no_cut_is_coming(self):
        d = self.register()
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s, school='off')
        self.assertIn(f'{HEADLINE} running: 32 games to go, 2 at a time', out.splitlines())

    def test_the_tuning_variables_taken_out_of_the_environment_are_named(self):
        self.set_env(KX_EXTRA_LISTS='sneaky=/tmp/x.txt', PDL_EQUIV_DEALS='3')
        d = self.register()
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s, school='off')
        names = sorted(k for k in os.environ if k.startswith(('KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_')))
        self.assertIn('KX_EXTRA_LISTS', names)
        self.assertIn(f"{HEADLINE} removed from the program's environment (they would change the pilot or the rules): {', '.join(names)}", out.splitlines())


# ---------------------------------------------------------------------------------------------------------- cuts without progress
class CutsWithoutProgress(RunLoop):
    def test_three_cuts_in_a_row_with_no_game_finished_stop_the_run(self):
        d = self.register()
        s = self.sittings(d, ('hang', 0), ('hang', 0), ('hang', 0), ('rest',))
        code, out, err = self.go(d, s)
        self.assertIn('no game finished in 3 sittings in a row', str(code))
        self.assertIn('--school-rule off', str(code), 'the way out is named')
        self.assertEqual(len(s.calls), 3, 'the fourth sitting must not start')
        self.assertEqual(len(s.stops), 3)
        self.assertEqual(self.events(d).count('stopped_for_school'), 3)
        self.assertIn('PARTIAL', self.page(d), 'the page is written before the run gives up')

    def test_two_cuts_with_no_game_are_forgiven_when_a_later_cut_sitting_played_some(self):
        d = self.register()
        s = self.sittings(d, ('hang', 0), ('hang', 0), ('hang', 1), ('hang', 0), ('hang', 0), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.calls), 6)
        self.assertEqual(len(s.stops), 5)
        self.assertEqual(len(self.games(d)), 32)
        self.assertEqual(self.events(d)[-1:], ['report_written'])
        self.assertIn('complete', self.events(d))

    def test_a_healthy_run_that_is_cut_every_morning_but_plays_games_every_night_finishes(self):
        d = self.register()
        s = self.sittings(d, ('hang', 1), ('hang', 1), ('hang', 1), ('hang', 1), ('hang', 1), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.stops), 5)
        self.assertEqual(len(self.games(d)), 32)
        self.assertNotIn('PARTIAL', self.page(d))

    def test_a_sitting_that_was_not_cut_starts_the_count_again(self):
        d = self.register()
        s = self.sittings(d, ('hang', 0), ('hang', 0), ('exit', 1), ('hang', 0), ('hang', 0), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.calls), 6)
        self.assertEqual(len(s.stops), 4)
        self.assertEqual(len(self.games(d)), 32)

    def test_a_resumed_program_that_plays_nothing_stops_the_run_after_one_sitting(self):
        d = self.register()
        first = self.sittings(d, ('exit', 5))
        self.assertEqual(self.go(d, first, '--max-games', '5', school='off')[0], 0)
        self.assertEqual(len(self.games(d)), 5)
        second = self.sittings(d, ('exit', 0))
        code, out, err = self.go(d, second, school='off')
        self.assertIn('no game finished in this sitting', str(code))
        self.assertEqual(len(second.calls), 1, 'the games already played are not this sitting\'s progress')
        self.assertIn('PARTIAL: 5 of 32', self.page(d))


# ---------------------------------------------------------------------------------------------------------- waiting for 5 pm, fast
class WaitingForFivePm(RunLoop):
    def test_a_wait_for_5pm_is_taken_in_steps_of_at_most_a_minute(self):
        self.clock = QuickClock(at(7, 6, 0))
        d = self.register()
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(s.calls[0].at, at(7, 17), 'sharp at 5 pm')
        self.assertLessEqual(max(self.clock.slept), 60, 'a laptop that slept must not oversleep by hours')
        self.assertAlmostEqual(sum(self.clock.slept), 11 * 3600)
        self.assertIn('waiting_for_school', self.events(d))

    def test_a_laptop_that_slept_through_the_wait_starts_at_5pm_and_not_later(self):
        self.clock = QuickClock(at(7, 6, 0))
        d = self.register()
        self.clock.hooks.append((at(7, 9), lambda: setattr(self.clock, 't', self.clock.t + datetime.timedelta(hours=4))))  # suspended for four hours
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(s.calls[0].at, at(7, 17))
        self.assertAlmostEqual(sum(self.clock.slept), 7 * 3600, msg='the four hours it slept are not slept again')

    def test_a_weekday_afternoon_starts_nothing_until_5pm_and_a_free_day_starts_at_once(self):
        d = self.register()
        for label, when, expected in (('Wednesday noon', at(7, 12), at(7, 17)), ('Wednesday 5:15 am', at(7, 5, 15), at(7, 17)), ('Wednesday 5 pm', at(7, 17), at(7, 17)),
                                      ('Saturday noon', at(10, 12), at(10, 12))):
            with self.subTest(label):
                started, cmd = self.first_start(d, when, school='on')
                self.assertEqual(started, expected)

    def test_school_days_can_be_changed_on_the_command_line(self):
        self.clock = QuickClock(at(7, 12))
        d = self.register()
        s = self.sittings(d, ('rest',))
        self.assertEqual(self.go(d, s, '--school-days', 'mon,tue,thu,fri')[0], 0)
        self.assertEqual(s.calls[0].at, at(7, 12), 'a Wednesday is free when it is not a school day')

    def test_with_the_rule_off_there_is_no_wait_and_no_stop_after_flag(self):
        self.clock = QuickClock(at(7, 12))
        d = self.register()
        s = self.sittings(d, ('rest',))
        self.assertEqual(self.go(d, s, school='off')[0], 0)
        self.assertEqual(s.calls[0].at, at(7, 12))
        self.assertIsNone(s.calls[0].stop_after)


# ---------------------------------------------------------------------------------------------------------- --max-games
class MaxGamesBudget(RunLoop):
    def test_games_played_in_a_sitting_cut_at_630_are_spent_from_the_budget(self):
        d = self.register()
        s = self.sittings(d, ('hang', 3), ('rest',))
        code, out, err = self.go(d, s, '--max-games', '5')
        self.assertEqual(code, 0, out + err)
        self.assertEqual([c.max_games for c in s.calls], ['5', '2'], 'the second sitting gets what is left of the 5')
        self.assertEqual(len(self.games(d)), 5, '--max-games 5 plays 5 games in total, not 5 a sitting')
        self.assertIn(f'{HEADLINE} stopped after --max-games 5; resume with --dir {d}', out.splitlines())
        self.assertIn('PARTIAL: 5 of 32', self.page(d))

    def test_a_cut_sitting_that_used_up_the_budget_ends_the_call(self):
        d = self.register()
        s = self.sittings(d, ('hang', 5))
        code, out, err = self.go(d, s, '--max-games', '5')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.calls), 1, 'no second sitting with an empty budget')
        self.assertEqual(len(s.stops), 1)
        self.assertIn('stopped after --max-games 5', out)
        self.assertEqual(len(self.games(d)), 5)

    def test_a_program_that_played_every_game_but_was_still_running_at_630_leaves_a_complete_run(self):
        d = self.register()
        s = self.sittings(d, ('hang', 32))
        code, out, err = self.go(d, s, '--max-games', '32')
        self.assertEqual(code, 0, out + err)
        self.assertEqual((len(s.calls), len(s.stops)), (1, 1))
        self.assertNotIn('stopped after', out, 'nothing is left to resume')
        self.assertIn('complete', self.events(d))
        self.assertNotIn('PARTIAL', self.page(d))

    def test_a_budget_is_spent_across_sittings_that_end_early(self):
        d = self.register()
        s = self.sittings(d, ('exit', 4), ('rest',))
        code, out, err = self.go(d, s, '--max-games', '10', school='off')
        self.assertEqual(code, 0, out + err)
        self.assertEqual([c.max_games for c in s.calls], ['10', '6'])
        self.assertEqual(len(self.games(d)), 10)
        self.assertIn('stopped after --max-games 10', out)

    def test_a_run_that_finishes_exactly_on_the_budget_is_complete_not_stopped(self):
        d = self.register()
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s, '--max-games', '32', school='off')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(s.calls[0].max_games, '32')
        self.assertNotIn('stopped after', out)
        self.assertIn('complete', self.events(d))
        self.assertEqual([e['games'] for e in T.jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'complete'], [32])
        self.assertNotIn('PARTIAL', self.page(d))

    def test_a_run_without_a_budget_that_finishes_does_not_say_it_stopped(self):
        d = self.register()
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s, school='off')
        self.assertEqual(code, 0, out + err)
        self.assertNotIn('stopped after', out)
        self.assertIsNone(s.calls[0].max_games)


# ---------------------------------------------------------------------------------------------------------- what is checked before every sitting
class CheckedBeforeEverySitting(RunLoop):
    def cut_then_change(self, change, when=None, steps=None):
        """Resume with the school rule on, change something in the middle of the first sitting (when=None) or while the wrapper waits for 5 pm, and return the
        outcome of the call."""
        d = self.register()
        s = self.sittings(d, *(steps or (('hang', 2), ('rest',))), on_spawn=(lambda n: change(d) if n == 1 else None) if when is None else None)
        if when is not None:
            self.clock.hooks.append((when, lambda: change(d)))
        code, out, err = self.go(d, s)
        return d, s, str(code) + err

    def test_a_deck_file_edited_during_a_sitting_is_refused_before_the_next_one(self):
        d, s, msg = self.cut_then_change(lambda d: T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko')))
        self.assertIn('my-list', msg)
        self.assertIn('has changed since registration', msg)
        self.assertEqual(len(s.calls), 1, 'the second sitting must not start')
        self.assertIn('PARTIAL: 2 of 32', self.page(d), 'what was played is not lost')

    def test_a_panel_file_edited_while_the_wrapper_waits_for_5pm_is_refused_before_it_starts(self):
        panel = os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-weezing.txt')
        d, s, msg = self.cut_then_change(lambda d: T.write(panel, T.read(panel) + '# edited\n'), when=at(7, 12))
        self.assertIn('t-weezing', msg)
        self.assertIn('has changed since registration', msg)
        self.assertEqual(len(s.calls), 1, 'nothing may start at 5 pm on a changed panel list')

    def test_the_program_replaced_during_a_sitting_is_refused_before_the_next_one(self):
        d, s, msg = self.cut_then_change(lambda d: T.write(self.program, T.FAKE_PROGRAM + '\n# rebuilt\n', mode=0o755))
        self.assertIn('is not the program this run was registered with', msg)
        self.assertEqual(len(s.calls), 1)

    def test_manifest_json_edited_without_its_hash_is_refused_before_the_next_sitting(self):
        def edit(d):
            man = json.loads(T.read(os.path.join(d, 'manifest.json')))
            man['deals'] = 3
            T.write(os.path.join(d, 'manifest.json'), json.dumps(man, indent=1))
        d, s, msg = self.cut_then_change(edit, when=at(7, 12))
        self.assertIn('the registration has changed', msg)
        self.assertEqual(len(s.calls), 1)

    def test_manifest_json_rewritten_together_with_its_hash_is_refused_before_the_next_sitting(self):
        def rewrite(d):
            man = json.loads(T.read(os.path.join(d, 'manifest.json')))
            man['created_at'] = '2026-10-08T00:00:00Z'
            T.rewrite_manifest(d, man)
        d, s, msg = self.cut_then_change(rewrite, when=at(7, 12))
        self.assertIn('manifest.json is not the one this run started with', msg)
        self.assertEqual(len(s.calls), 1)

    def test_a_refusal_for_a_changed_input_before_the_first_sitting_writes_no_page(self):
        d = self.register()
        T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko'))
        s = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s, school='off')
        self.assertIn('has changed since registration', str(code))
        self.assertEqual(s.calls, [])
        self.assertFalse(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')), 'a refusal before anything ran leaves no page')
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_a_moved_checkout_is_named_instead_of_listing_every_file_as_missing(self):
        d = self.register()
        moved = os.path.join(self.tmp, 'moved')
        shutil.move(self.repo, moved)
        d2 = os.path.join(moved, 'rl', 'results', 'slow_reports', '2026-10-10_my-list')
        s = self.sittings(d2, ('rest',))
        code, out, err = self.go(d2, s, school='off')
        self.assertIn('the repository this run was registered in', str(code))
        self.assertIn(self.repo, str(code))
        self.assertNotIn('is missing', str(code), 'one clear message, not nine lines of missing files')
        self.assertEqual(s.calls, [])
        code, out, err = self.cli('--dir', d2, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertIn('it would be refused: the repository this run was registered in', out)


class ReportOnlyPlaysNothing(RunLoop):
    def test_report_only_writes_the_page_from_the_games_so_far_even_when_a_file_changed_since(self):
        d = self.register()
        first = self.sittings(d, ('exit', 6))
        self.assertEqual(self.go(d, first, '--max-games', '6', school='off')[0], 0)
        T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko'))
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        second = self.sittings(d, ('rest',))
        code, out, err = self.go(d, second, '--report-only', school='off')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(second.calls, [], 'a report-only call starts no program')
        self.assertEqual(len(self.games(d)), 6)
        self.assertIn('PARTIAL: 6 of 32', self.page(d))


class DryRunOfARegisteredRun(RunLoop):
    def test_it_says_how_to_resume_when_the_inputs_are_as_registered(self):
        d = self.register()
        s = self.sittings(d, ('exit', 6))
        self.assertEqual(self.go(d, s, '--max-games', '6', school='off')[0], 0)
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertIn(f'6 of 32 games played; 26 games to go (resume with: python3 rl/strength/slow_report.py --dir {d})', out)
        self.assertNotIn('refused', out)

    def test_it_says_it_would_be_refused_when_an_input_changed_and_changes_nothing(self):
        d = self.register()
        T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko'))
        before = {n: T.read(os.path.join(d, n)) for n in os.listdir(d)}
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertIn('0 of 32 games played; 32 games to go (it would be refused: my-list', out)
        self.assertIn('has changed since registration', out)
        self.assertNotIn('resume with', out)
        self.assertEqual({n: T.read(os.path.join(d, n)) for n in os.listdir(d)}, before, 'a dry run writes nothing')

    def test_a_finished_run_is_complete_whatever_happened_to_the_files_since(self):
        d = self.register()
        s = self.sittings(d, ('rest',))
        self.assertEqual(self.go(d, s, school='off')[0], 0)
        T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko'))
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertIn('32 of 32 games played; 0 games to go (complete)', out)


# ---------------------------------------------------------------------------------------------------------- what a resume keeps from the registration
class ResumeKeepsTheRegistration(RunLoop):
    def test_the_thread_count_is_registered_and_a_resume_uses_it_unless_told_otherwise(self):
        d = self.register('--threads', '3')
        self.assertEqual(json.loads(T.read(os.path.join(d, 'manifest.json')))['threads'], 3)
        self.assertEqual([e['threads'] for e in T.jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'registered'], [3])
        first = self.sittings(d, ('exit', 2))
        self.assertEqual(self.go(d, first, '--max-games', '2', school='off')[0], 0)
        self.assertEqual(first.calls[0].threads, '3', 'the registered count, not the pin\'s 2')
        second = self.sittings(d, ('exit', 2))
        self.assertEqual(self.go(d, second, '--max-games', '2', '--threads', '5', school='off')[0], 0)
        self.assertEqual(second.calls[0].threads, '5', 'an explicit --threads wins')

    def test_a_changed_pin_file_is_only_noted_and_every_line_keeps_the_registered_headline(self):
        d = self.register()
        code, out, err = self.cli('--dir', d, '--report-only', deck=False)
        self.assertEqual(code, 0, err)
        self.assertNotIn('the pin file has changed', out)
        pin = json.loads(T.read(self.pin_path))
        pin.update(program='/nonexistent/another_build', pilot_label='kz9 (abc)', reference_label='kr1', threads=7)
        T.write(self.pin_path, json.dumps(pin))
        s = self.sittings(d, ('exit', 2))
        code, out, err = self.go(d, s, '--max-games', '2', school='off')
        self.assertEqual(code, 0, err + out)
        self.assertIn('note: the pin file has changed since this run was registered', out)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines)
        for l in lines:
            self.assertTrue(l.startswith(HEADLINE + ' '), l)
        program = s.calls[0].cmd[len(sr.nice_prefix()):]
        self.assertEqual(program[:2], [self.program, 'run'], 'the registered program, not the new pin\'s')
        self.assertEqual(s.calls[0].threads, '2', 'the registered thread count, not the new pin\'s 7')

    def test_a_refusal_on_a_resume_carries_the_registered_headline_too(self):
        d = self.register()
        pin = json.loads(T.read(self.pin_path))
        pin.update(pilot_label='kz9 (abc)', reference_label='kr1')
        T.write(self.pin_path, json.dumps(pin))
        T.write(self.deck, T.read(self.deck).replace('Torchic', 'Treecko'))
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertTrue(str(code).startswith(HEADLINE + ' REFUSED'), code)

    def test_a_run_registered_without_a_scrub_list_is_scrubbed_with_the_pins(self):
        self.set_env(KX_EXTRA_LISTS='sneaky=/tmp/x.txt')
        d = self.register()
        man = json.loads(T.read(os.path.join(d, 'manifest.json')))
        del man['slow_report']['scrub_env_prefixes']
        T.rewrite_manifest(d, man)
        s = self.sittings(d, ('exit', 2))
        code, out, err = self.go(d, s, '--max-games', '2', school='off')
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('KX_EXTRA_LISTS', s.calls[0].env, 'no list in the registration means the pin\'s list, never none')

    def test_a_run_that_is_not_a_slow_report_is_refused_cleanly_by_every_option(self):
        d = self.register()
        man = json.loads(T.read(os.path.join(d, 'manifest.json')))
        del man['slow_report']
        T.rewrite_manifest(d, man)
        for extra in ((), ('--dry-run',), ('--report-only',)):
            with self.subTest(extra=extra):
                s = self.sittings(d, ('rest',))
                code, out, err = self.cli('--dir', d, *extra, deck=False, spawn=s)
                self.assertIn('is not a slow report run', str(code))
                self.assertEqual(s.calls, [])


# ---------------------------------------------------------------------------------------------------------- the environment scrub
class ScrubbedOnEverySitting(RunLoop):
    def test_no_sitting_sees_a_tuning_variable_and_a_lookalike_name_is_kept(self):
        self.set_env(KX_EXTRA_LISTS='sneaky=/tmp/x.txt', PDL_EQUIV_DEALS='3', GPG_AGENT_INFO='kept', XKX_NOT_A_PREFIX='kept')
        d = self.register()
        s = self.sittings(d, ('hang', 1), ('hang', 1), ('rest',))
        code, out, err = self.go(d, s)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.calls), 3)
        for i, c in enumerate(s.calls, 1):
            with self.subTest(sitting=i):
                self.assertNotIn('KX_EXTRA_LISTS', c.env)
                self.assertNotIn('PDL_EQUIV_DEALS', c.env)
                self.assertEqual(c.env.get('GPG_AGENT_INFO'), 'kept', 'a prefix is a prefix: GPG_ contains PG_ but does not start with it')
                self.assertEqual(c.env.get('XKX_NOT_A_PREFIX'), 'kept')
                self.assertIn('PATH', c.env)

    def test_a_name_that_only_contains_a_prefix_is_kept_by_the_scrub(self):
        clean, removed = sr.scrub_env({'GPG_AGENT_INFO': 'a', 'XKX_THING': 'b', 'MY_PDL_X': 'c', 'KX_THING': 'd', 'PG_DUMP': 'e'}, ['KX_', 'PDL_', 'PG_'])
        self.assertEqual(sorted(clean), ['GPG_AGENT_INFO', 'MY_PDL_X', 'XKX_THING'])
        self.assertEqual(removed, ['KX_THING', 'PG_DUMP'])


# ---------------------------------------------------------------------------------------------------------- what a stop leaves behind
class StoppedEarlyKeepsThePage(RunLoop):
    def test_ctrl_c_stops_the_program_logs_it_and_still_writes_the_partial_page(self):
        d = self.register()
        s = self.sittings(d, ('hang', 4))
        polls = [0]
        real_sleep = self.clock.sleep

        def sleep(seconds):
            polls[0] += 1
            if polls[0] == 3:
                raise KeyboardInterrupt
            real_sleep(seconds)
        self.clock.sleep = sleep
        with self.assertRaises(KeyboardInterrupt):
            self.cli('--dir', d, school='off', spawn=s, deck=False)
        self.assertEqual(len(s.stops), 1, 'the program is stopped')
        self.assertIn('interrupted', self.events(d))
        self.assertIn('PARTIAL: 4 of 32', self.page(d), 'Ctrl-C leaves the page, as a SIGTERM does')
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_ctrl_c_during_the_wait_for_5pm_leaves_the_page_and_starts_nothing(self):
        self.clock = QuickClock(at(7, 12))
        d = self.register()
        s = self.sittings(d, ('rest',))

        def ctrl_c():
            raise KeyboardInterrupt
        self.clock.hooks.append((at(7, 13), ctrl_c))
        with self.assertRaises(KeyboardInterrupt):
            self.go(d, s)
        self.assertEqual(s.calls, [])
        self.assertIn('PARTIAL: 0 of 32', self.page(d))
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_a_console_note_says_the_page_was_written_before_stopping(self):
        d = self.register()
        s = self.sittings(d, ('exit', 2, 101))
        code, out, err = self.go(d, s, school='off')
        self.assertIn('the program stopped with exit code 101', str(code))
        self.assertIn(f'{HEADLINE} SLOW_REPORT.md (partial) written before stopping', out.splitlines())
        self.assertIn('PARTIAL: 2 of 32', self.page(d))
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_a_page_that_cannot_be_written_never_hides_why_the_run_stopped(self):
        d = self.register()
        s = self.sittings(d, ('exit', 2, 101))
        with mock.patch.object(sr, 'write_slow_report', side_effect=OSError('disk full')):
            code, out, err = self.go(d, s, school='off')
        self.assertIn('the program stopped with exit code 101', str(code))
        self.assertIn('could not write the page before stopping: disk full', out)

    def test_a_second_ctrl_c_while_the_page_is_written_is_not_swallowed(self):
        d = self.register()
        s = self.sittings(d, ('exit', 2, 101))
        with mock.patch.object(sr, 'write_slow_report', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.go(d, s, school='off')
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_a_failing_engineering_report_is_named_on_the_console_and_never_blocks_the_page(self):
        d = self.register()
        for stderr, want in (("Traceback (most recent call last):\\nValueError: no games to report\\n", 'ValueError: no games to report'), ('', 'no message')):
            with self.subTest(stderr=stderr):
                bad = os.path.join(self.tmp, 'bad_report.py')
                T.write(bad, f"import sys\nsys.stderr.write('{stderr}')\nsys.exit(1)\n")
                with mock.patch.object(sr, 'REPORT', bad):
                    code, out, err = self.cli('--dir', d, '--report-only', deck=False)
                self.assertEqual(code, 0, err)
                self.assertIn(f'{HEADLINE} REPORT.md (the engineering report) could not be written: {want}', out.splitlines())
                self.assertTrue(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')))
                self.assertNotIn('beside this page', self.page(d), 'no pointer to a REPORT.md that does not exist')


# ---------------------------------------------------------------------------------------------------------- the lock file while a program plays
class TheLockDuringARun(RunLoop):
    """The lock file is a note for a refusal: it names the wrapper and, after every start, the program's process group (so a second wrapper can say which group to
    stop when the first one was killed). The program here is pretended and holds no real lock, so these tests look at the note and at the file; the flock itself is
    pinned with real processes in test_slow_report_process.py and test_slow_report.py."""

    def lock_of(self, d):
        return os.path.join(d, 'slow_report.lock')

    def test_every_sitting_notes_its_programs_process_group_in_the_lock_file_and_the_file_is_gone_at_the_end(self):
        d = self.register()
        s = self.sittings(d, ('hang', 3), ('hang', 3), ('rest',))
        pids = iter([40001, 40002, 40003])

        def spawn(cmd, env, logfile):
            proc = s(cmd, env, logfile)
            proc.pid = next(pids)
            return proc
        notes = []
        for when in (at(7, 5, 5), at(7, 17, 5)):  # inside the first morning's sitting, and inside the evening's, which runs through the night
            self.clock.hooks.append((when, lambda: notes.append(sr.read_lock_info(self.lock_of(d)))))
        code, out, err = self.go(d, spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(s.calls), 3)
        self.assertEqual(len(notes), 2)
        for note, pgid in zip(notes, (40001, 40002)):
            self.assertEqual(sorted(note), ['pid', 'program_pgid', 'started'])
            self.assertEqual((note['pid'], note['program_pgid']), (os.getpid(), pgid), 'the group of the program that is playing now')
            datetime.datetime.strptime(note['started'], '%Y-%m-%dT%H:%M:%SZ')
        self.assertFalse(os.path.exists(self.lock_of(d)), 'a run that is over leaves no lock file')

    def test_a_program_that_could_not_be_stopped_keeps_the_lock_file_with_its_group_until_it_has_ended(self):
        d = self.register()
        s = self.sittings(d, ('hang', 2))
        before = list(sr._PROGRAMS)  # (a program left on this list would stop every later release in the suite from removing its file)
        self.addCleanup(lambda: sr._PROGRAMS.__setitem__(slice(None), before))
        started = []

        def spawn(cmd, env, logfile):
            proc = s(cmd, env, logfile)
            proc.pid = 40001
            started.append(proc)
            return proc

        def ctrl_c():
            raise KeyboardInterrupt
        self.clock.hooks.append((at(7, 5, 5), ctrl_c))
        with mock.patch.object(sr, 'stop_group', lambda proc, grace_s=30: None):  # a program that ignores the stop and plays on
            with self.assertRaises(KeyboardInterrupt):
                self.go(d, spawn)
        proc = started[0]
        self.assertIsNone(proc.poll(), 'the program is still running')
        self.assertTrue(os.path.exists(self.lock_of(d)), 'so the lock file stays')
        self.assertEqual(sr.read_lock_info(self.lock_of(d))['program_pgid'], 40001, 'and says which group to stop')
        self.assertEqual(sr._PROGRAMS[len(before):], [proc])
        proc.returncode = -9  # it ends
        s2 = self.sittings(d, ('rest',))
        code, out, err = self.go(d, s2, school='off')
        self.assertEqual(code, 0, out + err)
        self.assertFalse(os.path.exists(self.lock_of(d)), 'with the program gone, the next run leaves no file')
        self.assertEqual(sr._PROGRAMS, before)


class UtcTimestamps(Quick):
    def test_a_time_is_written_in_utc_whatever_zone_it_comes_from(self):
        self.assertEqual(sr.utc_iso(at(7, 5, 0)), '2026-10-07T10:00:00Z')  # Chicago is five hours behind in October
        self.assertEqual(sr.utc_iso(at(7, 5, 0, month=1)), '2026-01-07T11:00:00Z')  # and six in January

    def test_the_log_stamps_the_current_utc_time(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        sr.log_event(d, 'probe')
        stamp = T.jsonl(os.path.join(d, 'slow_report_log.jsonl'))[0]['at']
        written = datetime.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
        self.assertLess(abs((datetime.datetime.now(UTC) - written).total_seconds()), 120, stamp)


# ---------------------------------------------------------------------------------------------------------- a real program, on the same clock
class RealProgramCut(RunLoop):
    def test_a_real_program_in_flight_at_630_is_stopped_and_its_game_played_again_after_5pm(self):
        d = self.register()
        T.write(os.path.join(d, 'hang.flag'), '3')  # three games, then one that never finishes
        in_flight = os.path.join(d, 'hanging.flag')
        started = []

        def spawn(cmd, env, logfile):
            started.append(sr.default_spawn(cmd, env, logfile))
            return started[-1]
        # the clock may not reach a 6:30 before the program has really done what the test needs: the first morning, a game in flight; the second, finished
        self.clock.gates = [(at(7, 6, 30), lambda: os.path.exists(in_flight)), (at(8, 6, 30), lambda: len(started) > 1 and started[1].poll() is not None)]
        code, out, err = self.cli('--dir', d, '--poll-s', '60', school='on', spawn=spawn, deck=False)
        self.assertEqual(code, 0, err + out)
        games = self.games(d)
        self.assertEqual(len(games), 32)
        self.assertEqual(len({g['key'] for g in games}), 32, 'the cut-off game is played again, once')
        calls = T.jsonl(os.path.join(d, 'fake_calls.jsonl'))
        self.assertEqual(len(calls), 2)
        with self.assertRaises(ProcessLookupError):
            os.kill(calls[0]['pid'], 0)  # the stopped program is gone
        self.assertIn('stopped_for_school', self.events(d))


# ---------------------------------------------------------------------------------------------------------- the self-check under the school rule
SELFCHECK_PROGRAM = r'''#!/usr/bin/env python3
import os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'selfcheck_seen.txt'), 'w') as f:
    f.write('%d %d %d\n' % (os.getpid(), os.getpgid(0), os.nice(0)))
if os.path.exists(os.path.join(here, 'selfcheck_hang')):
    time.sleep(3600)
print('selfcheck pilot=%s games=12 digest=fakefakefakefake' % sys.argv[sys.argv.index('--pilot') + 1])
'''


class SelfcheckAndTheSchoolRule(RunLoop):
    def selfcheck_world(self, hang=False):
        """The program replaced by one that records how it was started; returns a pin dict whose self-check text it matches."""
        self.set_program(SELFCHECK_PROGRAM)
        if hang:
            T.write(os.path.join(self.tmp, 'selfcheck_hang'), '')
        pin = json.loads(T.read(self.pin_path))
        pin['selfcheck'] = {s: f'selfcheck pilot={s} games=12 digest=fakefakefakefake' for s in ('kx3', 'km3')}
        return pin

    def watched_children(self):
        """(the programs started, a context in which they are recorded, killed at the end of the test whatever happens, and stop_group refuses to signal the process
        group of the test run itself, which a program that shares it would put in danger)."""
        started = []
        real_popen, real_stop = subprocess.Popen, sr.stop_group

        def spy(*a, **k):
            p = real_popen(*a, **k)
            started.append(p)
            self.addCleanup(lambda: p.poll() is None and p.kill())
            return p

        def careful_stop(proc, grace_s=30):
            self.assertNotEqual(os.getpgid(proc.pid), os.getpgrp(), 'stop_group would signal the test run itself: the program shares its process group')
            return real_stop(proc, grace_s)
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch.object(sr.subprocess, 'Popen', spy))
        stack.enter_context(mock.patch.object(sr, 'stop_group', careful_stop))
        return started, stack

    def test_the_selfcheck_runs_at_low_priority_in_its_own_process_group(self):
        pin = self.selfcheck_world()
        got = sr.run_selfcheck(pin, self.repo, 'kx3', lambda m: None)
        self.assertEqual(got, pin['selfcheck']['kx3'])
        pid, pgid, niceness = map(int, T.read(os.path.join(self.tmp, 'selfcheck_seen.txt')).split())
        self.assertEqual(pgid, pid, 'its own process group, so one signal stops it and everything it started')
        self.assertNotEqual(pgid, os.getpgrp())
        if shutil.which('nice'):
            self.assertEqual(niceness, 19)

    def test_a_selfcheck_still_running_at_the_morning_cut_is_stopped_and_refused(self):
        pin = self.selfcheck_world(hang=True)
        started, spy = self.watched_children()
        almost = at(7, 6, 29, 59) + datetime.timedelta(milliseconds=800)
        with spy:
            with self.assertRaises(SystemExit) as cm:
                sr.run_selfcheck(pin, self.repo, 'kx3', lambda m: None, deadline=at(7, 6, 30), now=lambda: almost)
        self.assertIn('did not finish before the school-morning cut at Wed 06:30', str(cm.exception))
        self.assertIn('nothing was written', str(cm.exception))
        self.assertIsNotNone(started[0].poll(), 'the program was stopped and reaped')
        with self.assertRaises(ProcessLookupError):
            os.killpg(started[0].pid, 0)

    def test_ctrl_c_during_the_selfcheck_stops_the_program(self):
        if signal.getsignal(signal.SIGINT) is not signal.default_int_handler:
            self.skipTest('SIGINT is not delivered as KeyboardInterrupt here')
        pin = self.selfcheck_world(hang=True)
        started, spy = self.watched_children()

        def interrupt_once_it_runs():
            running = os.path.join(self.tmp, 'selfcheck_seen.txt')  # written by the program as its first act: it runs, and the wrapper has long been waiting for it
            deadline = time.time() + 8
            while not os.path.exists(running) and time.time() < deadline:
                time.sleep(0.005)
            time.sleep(0.02)
            os.kill(os.getpid(), signal.SIGINT)
        threading.Thread(target=interrupt_once_it_runs, daemon=True).start()
        with spy:
            with self.assertRaises(KeyboardInterrupt):
                sr.run_selfcheck(pin, self.repo, 'kx3', lambda m: None)
        self.assertIsNotNone(started[0].poll(), 'the program must not be left running')
        with self.assertRaises(ProcessLookupError):
            os.killpg(started[0].pid, 0)

    def test_a_selfcheck_is_refused_in_school_hours_and_allowed_at_other_times(self):
        for label, when, school, refused in (('Wednesday noon', at(7, 12), 'on', True), ('Wednesday 5:15 am', at(7, 5, 15), 'on', True),
                                             ('Wednesday 4 am', at(7, 4), 'on', False), ('Wednesday 5 pm', at(7, 17), 'on', False), ('Saturday noon', at(10, 12), 'on', False),
                                             ('Wednesday noon with the rule off', at(7, 12), 'off', False)):
            with self.subTest(label):
                self.clock = QuickClock(when)
                code, out, err = self.cli('--deals', '1', '--selfcheck', school=school)
                self.assertNotEqual(code, 0)
                if refused:
                    self.assertIn('school time', str(code))
                    self.assertIn('Wed 17:00', str(code))
                    self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')), 'the self-check must not even start')
                else:
                    self.assertNotIn('school time', str(code))
                    self.assertIn('does not match the pin', str(code), 'it ran (the fake\'s digest is not the pin\'s)')
                self.assertFalse(os.path.exists(self.out_root))
                if os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')):
                    os.remove(os.path.join(self.tmp, 'selfcheck_env.json'))

    def test_the_selfcheck_is_given_the_next_morning_cut_as_its_deadline(self):
        for label, when, school, extra, want in (('Wednesday 8 pm', at(7, 20), 'on', (), at(8, 6, 30)), ('Wednesday 4 am', at(7, 4), 'on', (), at(7, 6, 30)),
                                                 ('Friday 8 pm', at(9, 20), 'on', (), at(12, 6, 30)), ('Saturday noon', at(10, 12), 'on', (), at(12, 6, 30)),
                                                 ('rule off', at(7, 20), 'off', (), None), ('no school days', at(7, 20), 'on', ('--school-days', ''), None)):
            with self.subTest(label):
                self.clock = QuickClock(when)
                seen = []

                def spy(pin, repo, spec, say, deadline=None, now=None):
                    seen.append(deadline)
                    raise Enough
                with mock.patch.object(sr, 'run_selfcheck', spy):
                    with self.assertRaises(Enough):
                        self.cli('--deals', '1', '--selfcheck', *extra, school=school)
                self.assertEqual(seen, [want])


if __name__ == '__main__':
    unittest.main()
