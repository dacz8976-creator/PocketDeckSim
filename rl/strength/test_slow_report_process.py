#!/usr/bin/env python3
"""Tests for the process hygiene of slow_report.py: signals, the run lock, the program's process group, the self-check run, and the clean refusals.

  cd rl/strength && python3 -B -m unittest -v test_slow_report_process

Written after a mutation review of test_slow_report.py: every behaviour here is one that a small deliberate fault in slow_report.py (or in the torn-line
handling of strength_report.py) left unnoticed. They use the same fixtures as test_slow_report.py (the World with a fake pinned program, the FakeClock) and
real, short-lived child processes; nothing plays a game, nothing sleeps beyond a third of a second, and every child a test starts is killed when the test
ends, pass or fail.

What is pinned:
  * stop_group: the polite stop reaches the whole process group, a program that ignores it is killed once the grace period is over, one that needs a moment
    gets it, a program that has already gone is not an error and is not signalled at all, and a process that shares the wrapper's own group is signalled alone
    (never the group, which holds the wrapper and whoever started it);
  * the stop signals: SIGTERM and SIGHUP end the whole call (self-check, registration, the replay of a changed program on a resume, and run alike) with 128 + the signal number,
    the handlers that were there before are back afterwards, and a thread other than the main one leaves the signals alone;
  * the program's process: no standard input, its log file closed when a sitting ends or is interrupted, a second Ctrl-C while the partial page is written is
    not swallowed and a failure to write it never hides the real error;
  * the run lock: what a refusal says when the holder's note is unreadable, a note nobody holds is replaced, a lock file that vanished or was replaced
    between open and lock is not the lock, release of a vanished file is quiet; the file is kept while a program this wrapper started is alive (and says which
    group to stop), removed when none is, and a failed remove is no error; a lock file that cannot be opened or locked is refused in words; a lock that was
    opened on descriptor 0, 1 or 2 is moved up so the program inherits it;
  * the self-check run: its own process group, stopped on interrupt or at the school-morning cut, refused in school hours, a mismatch writes nothing (and shows
    at most the end of what was printed, in any bytes), an exit with an error code is no match even when the pinned text was printed (and shows the end of the error
    stream, else of the output, else a word), its pipes are closed however it ends, and what was decided before the hours-long replay (run folder,
    seed slot) is decided again after it;
  * clean refusals instead of tracebacks: a missing deck file, a folder with no manifest, a pin without a key (or that cannot be read, or is not an object),
    a moved checkout, a file that has gone, a log file that does not exist, a seed picker with unreadable folders around it (or a manifest that is no object)
    and one with every slot taken, an explicit seed base on a slot in use;
  * whether the deck file is committed as it is, asked without ever touching .git/index, of the folder given and not of the repository a git hook has exported in GIT_DIR (and the
    other variables that choose a repository: every git call is made with git_env());
  * the resume command (and the run folder in the other messages that name it) is quoted for the shell; the engineering report reads past a torn last line;
  * the log of a run after a torn last line: the next event is written on a line of its own (and a log that ends with a newline, an empty one and a missing one get no blank line).
"""
import contextlib, datetime, errno, fcntl, io, json, os, shlex, shutil, signal, subprocess, sys, tempfile, textwrap, threading, time, types, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_slow_report as T  # noqa: E402  (World, FakeClock and the helpers: the same fixtures)
import test_strength_report as TR  # noqa: E402  (a minimal registered run for strength_report.py)

sr = T.sr
read, write, jsonl, sha = T.read, T.write, T.jsonl, T.sha
BLOCK, STEP = T.BLOCK, T.STEP
SELFCHECK_TEXT = 'selfcheck pilot=%s games=12 digest=fakefakefakefake'
STOP_SIGNALS = (signal.SIGTERM, signal.SIGHUP)


def alive(pid):
    """Whether the process exists and is not a zombie (a zombie is dead; it only waits to be collected)."""
    try:
        with open(f'/proc/{pid}/stat') as f:
            return f.read().rsplit(')', 1)[1].split()[0] != 'Z'
    except OSError:
        return False


def wait_for(predicate, seconds=10.0):
    end = time.time() + seconds
    while time.time() < end:
        if predicate():
            return True
        time.sleep(0.01)
    return bool(predicate())


def open_descriptors():
    return len(os.listdir('/proc/self/fd'))


def stray_signal(signum, frame):
    raise AssertionError(f'signal {signum} reached the handler that was there before the call')


@contextlib.contextmanager
def pipe_as_stdin():
    """This process's own stdin is a pipe inside the block, so that only a deliberate /dev/null can show in a program started there."""
    reading = os.pipe()
    try:
        saved = os.dup(0)
    except OSError:  # stdin was closed
        saved = None
    os.dup2(reading[0], 0)
    try:
        yield
    finally:
        if saved is None:
            os.close(0)
        else:
            os.dup2(saved, 0)
            os.close(saved)
        for fd in reading:
            os.close(fd)


class Leftovers:
    """Mixin: whatever process group a test started is killed when the test ends, so a failing test never leaves a child sleeping. A wrapper that tried to
    signal its own process group (the one this test run is in) fails the test instead of ending the run."""

    def setUp(self):
        super().setUp()
        real = os.killpg
        self.own_group_signals = []  # a stop that runs in a helper thread cannot fail the test by raising, so the attempt is also kept and checked at the end

        def killpg(pgid, sig):
            if pgid == os.getpgrp():
                self.own_group_signals.append((pgid, sig))
                raise AssertionError(f'the wrapper tried to signal its own process group ({pgid}), which holds this whole test run')
            return real(pgid, sig)
        patcher = mock.patch.object(os, 'killpg', killpg)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: self.assertEqual(self.own_group_signals, [], 'the wrapper signalled its own process group'))

    def kill_at_end(self, pid):
        def kill():
            try:
                os.killpg(pid, signal.SIGKILL)
            except OSError:
                pass
        self.addCleanup(kill)

    def plant_stray_handlers(self):
        old = {s: signal.signal(s, stray_signal) for s in STOP_SIGNALS}
        self.addCleanup(lambda: [signal.signal(s, h) for s, h in old.items()])

    def give_up_after(self, seconds, why):
        """A test that waits on a child that should have been stopped fails after `seconds` instead of after two minutes."""
        def too_slow(signum, frame):
            raise AssertionError(f'did not finish within {seconds} s: {why}')
        signal.signal(signal.SIGALRM, too_slow)  # Timed.tearDown puts the original handler back
        signal.alarm(seconds)


# ---------------------------------------------------------------------------------------------------------- stop_group
IGNORES_THE_STOP = '''
import signal, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
print('ready', flush=True)
time.sleep(60)
'''

FINISHES_ITS_GAME = '''
import signal, sys, time
def polite(signum, frame):
    time.sleep(0.25)
    open(sys.argv[1], 'w').write('finished cleanly')
    sys.exit(0)
signal.signal(signal.SIGTERM, polite)
print('ready', flush=True)
time.sleep(60)
'''

HAS_A_CHILD = '''
import os, sys, time
pid = os.fork()
if pid == 0:
    time.sleep(60)
    os._exit(0)
open(sys.argv[1], 'w').write(str(pid))
print('ready', flush=True)
time.sleep(60)
'''

LEAVES_A_CHILD_AND_ENDS = '''
import os, sys, time
pid = os.fork()
if pid == 0:
    time.sleep(60)
    os._exit(0)
open(sys.argv[1], 'w').write(str(pid))
print('ready', flush=True)
'''

JUST_WAITS = '''
import time
print('ready', flush=True)
time.sleep(60)
'''


class StopTheProgram(Leftovers, T.Timed):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def start(self, script, *args):
        """The way the wrapper starts the program (default_spawn), once it has said it is ready."""
        log = os.path.join(self.tmp, 'program.log')
        proc = sr.default_spawn([sys.executable, '-c', script, *args], dict(os.environ), log)
        self.addCleanup(proc._logfh.close)
        self.kill_at_end(proc.pid)
        self.assertTrue(wait_for(lambda: 'ready' in read(log)), 'the program never got ready: ' + read(log))
        return proc

    def stop(self, proc, **kw):
        """stop_group in a helper thread, so a stop that never returns fails the test instead of hanging it. Returns the seconds it took."""
        t0 = time.time()
        t = threading.Thread(target=sr.stop_group, args=(proc,), kwargs=kw, daemon=True)
        t.start()
        t.join(10)
        self.assertFalse(t.is_alive(), 'stop_group never returned')
        return time.time() - t0

    def test_a_program_that_ignores_the_stop_is_killed_once_the_grace_period_is_over(self):
        proc = self.start(IGNORES_THE_STOP)
        took = self.stop(proc, grace_s=0.3)
        self.assertEqual(proc.returncode, -signal.SIGKILL)
        self.assertGreaterEqual(took, 0.25, 'the polite stop comes first and is given its grace period')
        self.assertFalse(alive(proc.pid))

    def test_a_program_that_needs_a_moment_to_finish_is_given_one_by_default(self):
        done = os.path.join(self.tmp, 'done.txt')
        proc = self.start(FINISHES_ITS_GAME, done)
        self.stop(proc)
        self.assertEqual(proc.returncode, 0, 'it was not killed in the middle of finishing')
        self.assertEqual(read(done), 'finished cleanly')

    def test_the_polite_stop_reaches_every_process_of_the_group_and_is_a_sigterm_first(self):
        pidfile = os.path.join(self.tmp, 'grandchild.pid')
        proc = self.start(HAS_A_CHILD, pidfile)
        grandchild = int(read(pidfile))
        self.assertTrue(alive(grandchild))
        self.stop(proc)
        self.assertEqual(proc.returncode, -signal.SIGTERM, 'a program that stops when asked is not killed')
        self.assertTrue(wait_for(lambda: not alive(grandchild), 5), 'a process the program started was left running')

    def test_a_program_that_vanishes_between_the_polite_stop_and_the_kill_is_not_an_error(self):
        proc = self.start(IGNORES_THE_STOP)
        real = os.killpg

        def killpg(pgid, sig):
            real(pgid, sig)
            if sig == signal.SIGKILL:
                raise ProcessLookupError  # the group was gone by the time the kill was delivered
        with mock.patch.object(os, 'killpg', killpg):
            self.stop(proc, grace_s=0.2)
        self.assertEqual(proc.returncode, -signal.SIGKILL)

    def test_a_program_that_has_already_gone_is_not_an_error(self):
        proc = sr.default_spawn([sys.executable, '-c', 'pass'], dict(os.environ), os.path.join(self.tmp, 'gone.log'))
        self.addCleanup(proc._logfh.close)
        self.assertEqual(proc.wait(timeout=20), 0)
        sr.stop_group(proc)
        self.assertEqual(proc.returncode, 0)

    def test_a_program_that_ended_but_was_not_collected_yet_is_collected_not_killed(self):
        proc = sr.default_spawn([sys.executable, '-c', 'import sys; sys.exit(7)'], dict(os.environ), os.path.join(self.tmp, 'ended.log'))
        self.addCleanup(proc._logfh.close)
        self.assertTrue(wait_for(lambda: not alive(proc.pid)), 'the program should have ended by now')
        self.assertIsNone(proc.returncode, 'it has not been collected')
        sr.stop_group(proc)
        self.assertEqual(proc.returncode, 7)

    def test_a_program_that_has_ended_is_not_signalled_at_all_even_with_a_process_left_in_its_group(self):
        pidfile = os.path.join(self.tmp, 'left.pid')
        proc = self.start(LEAVES_A_CHILD_AND_ENDS, pidfile)
        left = int(read(pidfile))
        self.assertTrue(wait_for(lambda: not alive(proc.pid)), 'the program should have ended by now')
        self.assertTrue(alive(left), 'the process it left behind is still running')
        signalled = []
        with mock.patch.object(os, 'killpg', lambda pgid, sig: signalled.append(('killpg', pgid, sig))), \
                mock.patch.object(subprocess.Popen, 'send_signal', lambda p, sig: signalled.append(('send_signal', sig))):
            sr.stop_group(proc)
        self.assertEqual(signalled, [], 'an ended program is collected and left alone: nothing is sent to its group')
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(alive(left), 'and what it left behind was not touched')

    def start_in_my_group(self, script):
        """A process that shares THIS process's group (no new session), as a program started by some other launcher would, once it has said it is ready."""
        log = os.path.join(self.tmp, f'mine{len(os.listdir(self.tmp))}.log')
        fh = open(log, 'ab')
        self.addCleanup(fh.close)
        proc = subprocess.Popen([sys.executable, '-c', script], stdin=subprocess.DEVNULL, stdout=fh, stderr=fh)
        self.addCleanup(proc.wait)  # (cleanups run last in, first out: the kill comes first, then the wait)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        self.assertTrue(wait_for(lambda: 'ready' in read(log)), 'the process never got ready: ' + read(log))
        self.assertEqual(os.getpgid(proc.pid), os.getpgrp(), 'it is in the same group as this test run')
        return proc

    def test_a_process_in_the_wrappers_own_group_is_signalled_alone_and_never_the_whole_group(self):
        bystander = self.start_in_my_group(JUST_WAITS)
        proc = self.start_in_my_group(JUST_WAITS)
        self.stop(proc)
        self.assertEqual(proc.returncode, -signal.SIGTERM, 'it was asked to stop and stopped')
        self.assertIsNone(bystander.poll(), 'another process of the same group was not touched')
        self.assertEqual(self.own_group_signals, [])

    def test_a_process_in_the_wrappers_own_group_that_ignores_the_stop_is_killed_alone_after_the_grace_period(self):
        bystander = self.start_in_my_group(JUST_WAITS)
        proc = self.start_in_my_group(IGNORES_THE_STOP)
        took = self.stop(proc, grace_s=0.3)
        self.assertEqual(proc.returncode, -signal.SIGKILL)
        self.assertGreaterEqual(took, 0.25, 'the polite stop comes first here too')
        self.assertIsNone(bystander.poll(), 'another process of the same group was not touched')
        self.assertEqual(self.own_group_signals, [])


# ---------------------------------------------------------------------------------------------------------- signals
class WrapperSignals(Leftovers, T.World):
    def setUp(self):
        super().setUp()
        self.plant_stray_handlers()

    def handlers(self):
        return {s: signal.getsignal(s) for s in STOP_SIGNALS}

    def test_a_stop_signal_ends_the_call_with_128_plus_the_signal_number(self):
        for sig, want in ((signal.SIGTERM, 143), (signal.SIGHUP, 129)):
            with self.subTest(sig=sig.name):
                with sr.signals_stop_the_program():
                    with self.assertRaises(SystemExit) as cm:
                        os.kill(os.getpid(), sig)
                        time.sleep(2)
                self.assertEqual(cm.exception.code, want)

    def test_the_wrappers_handlers_are_in_place_during_the_call_and_the_old_ones_are_back_after_every_way_out(self):
        during = []
        ours = {s: sr.signals_stop_the_program.handler for s in STOP_SIGNALS}
        was = {s: stray_signal for s in STOP_SIGNALS}
        code, out, err = self.cli('--deals', '1', '--dry-run', deck_check=lambda p, r: during.append(self.handlers()) or [])
        self.assertEqual(code, 0, err)
        self.assertEqual(during, [ours], 'in place from the start of the call')
        self.assertEqual(self.handlers(), was, 'back after a normal return')
        code, out, err = self.cli('--deals', '0')
        self.assertIn('--deals must be between', str(code))
        self.assertEqual(self.handlers(), was, 'back after a refusal')
        with self.assertRaises(ZeroDivisionError):
            with sr.signals_stop_the_program():
                1 / 0
        self.assertEqual(self.handlers(), was, 'back after an exception')

    def test_outside_the_main_thread_the_signals_are_left_alone(self):
        errors = []

        def go():
            try:
                with sr.signals_stop_the_program():
                    pass
            except BaseException as e:  # noqa: B902
                errors.append(e)
        t = threading.Thread(target=go)
        t.start()
        t.join(10)
        self.assertEqual(errors, [])
        self.assertEqual(self.handlers(), {s: stray_signal for s in STOP_SIGNALS})


# ---------------------------------------------------------------------------------------------------------- a pinned program that records how it was started
SELFCHECK_PROGRAM = r'''#!/usr/bin/env python3
import json, os, signal, sys, time
here = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1] == 'selfcheck':
    spec = sys.argv[sys.argv.index('--pilot') + 1]
    mine = os.path.join(here, 'seen_' + spec + '.json')
    with open(mine + '.tmp', 'w') as f:
        json.dump({'pid': os.getpid(), 'pgid': os.getpgrp(), 'stdin': os.readlink('/proc/self/fd/0'), 'argv': sys.argv[1:]}, f)
    os.replace(mine + '.tmp', mine)
    todo = os.path.join(here, 'while_selfchecking.json')  # things that happen meanwhile: directories made, files written
    if os.path.exists(todo):
        for action in json.load(open(todo)):
            if action[0] == 'mkdir':
                os.makedirs(action[1], exist_ok=True)
            else:
                os.makedirs(os.path.dirname(action[1]), exist_ok=True)
                open(action[1], 'w').write(action[2])
    if os.path.exists(os.path.join(here, 'selfcheck_hangs')):
        time.sleep(3600)
    if os.path.exists(os.path.join(here, 'selfcheck_crashes')):
        sys.stderr.write('boom: the engine could not start\n')
        sys.exit(1)
    exit_file = os.path.join(here, 'selfcheck_exit')  # the exit code to end with, whatever was printed (a flag file: the code in it)
    final = int(open(exit_file).read()) if os.path.exists(exit_file) else None

    def finish(code):
        err_file = os.path.join(here, 'selfcheck_stderr')  # bytes for the error stream, next to whatever was printed
        if os.path.exists(err_file):
            sys.stderr.flush()
            sys.stderr.buffer.write(open(err_file, 'rb').read())
            sys.stderr.buffer.flush()
        if os.path.exists(os.path.join(here, 'selfcheck_killed')):  # killed by a signal after printing
            os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(code if final is None else final)
    for name, stream, code in (('selfcheck_says', sys.stdout, 0), ('selfcheck_crash_says', sys.stderr, 1)):  # exactly these bytes, whatever they are
        if os.path.exists(os.path.join(here, name)):
            stream.flush()
            stream.buffer.write(open(os.path.join(here, name), 'rb').read())
            stream.buffer.flush()
            finish(code)
    print('selfcheck pilot=%s games=12 digest=fakefakefakefake' % spec, flush=True)
    finish(0)
'''


class SelfcheckWorld(Leftovers, T.World):
    """A World whose pinned program is SELFCHECK_PROGRAM and whose pin holds the text it prints."""

    def setUp(self):
        super().setUp()
        self.set_program(SELFCHECK_PROGRAM)
        pin = json.loads(read(self.pin_path))
        pin['selfcheck'] = {s: SELFCHECK_TEXT % s for s in ('km3', 'kx3')}
        write(self.pin_path, json.dumps(pin))
        self.pin = pin

        def kill_what_is_left():
            for spec in ('km3', 'kx3'):
                try:
                    os.killpg(self.seen(spec)['pid'], signal.SIGKILL)
                except (OSError, ValueError, KeyError):
                    pass
        self.addCleanup(kill_what_is_left)

    def seen_path(self, spec):
        return os.path.join(self.tmp, f'seen_{spec}.json')

    def seen(self, spec):
        return json.loads(read(self.seen_path(spec)))

    def meanwhile(self, *actions):
        write(os.path.join(self.tmp, 'while_selfchecking.json'), json.dumps(list(actions)))

    def flag(self, name):
        write(os.path.join(self.tmp, name), '')

    def flag_with(self, name, text):
        write(os.path.join(self.tmp, name), text)

    def exits_with(self, code):
        """The program ends with this exit code, whatever else it does (and prints the pinned text unless told otherwise)."""
        self.flag_with('selfcheck_exit', str(code))

    def failed(self, spec, code, shown):
        """What a self-check that exited with an error code is refused with, whatever it printed."""
        return (f'REFUSED: the self-check of {spec} on {self.pin["program"]} exited with code {code} ({shown}); a self-check that fails is not a match, whatever it printed. '
                'Nothing was written.')

    def says(self, data, name='selfcheck_says'):
        """The program prints exactly these bytes (to its output, or with name='selfcheck_crash_says' to its error stream and exits with 1)."""
        T.write_bytes(os.path.join(self.tmp, name), data)

    def aim_at(self, spec, sig):
        """In a helper thread: once the program has started its self-check, send `sig` to the main thread. The list says whether it had started."""
        started = []

        def go():
            started.append(wait_for(lambda: os.path.exists(self.seen_path(spec)), 30))
            signal.pthread_kill(threading.main_thread().ident, sig)
        t = threading.Thread(target=go, daemon=True)
        t.start()
        self.addCleanup(t.join, 5)
        return started


class SelfcheckProcess(SelfcheckWorld):
    """run_selfcheck called directly."""

    def setUp(self):
        super().setUp()
        self.give_up_after(20, 'a self-check that should have been stopped kept running')

    def selfcheck(self, spec='kx3', **kw):
        said = []
        text = sr.run_selfcheck(dict(self.pin), self.repo, spec, said.append, **kw)
        return text, said

    def test_the_program_runs_in_a_group_of_its_own_with_no_stdin_and_the_documented_command(self):
        with pipe_as_stdin():
            text, said = self.selfcheck('kx3')
        seen = self.seen('kx3')
        reg = json.loads(read(os.path.join(HERE, 'decks.json')))['decks']
        self.assertEqual(text, SELFCHECK_TEXT % 'kx3')
        self.assertEqual(seen['pgid'], seen['pid'], 'it leads its own process group, so stopping the group can never touch the wrapper')
        self.assertNotEqual(seen['pgid'], os.getpgrp())
        self.assertEqual(seen['stdin'], '/dev/null')
        self.assertEqual(seen['argv'], ['selfcheck', '--root', self.repo, '--pilot', 'kx3', '--deck-a', reg['t-altaria'], '--deck-b', reg['t-suicune'], '--games', '12'])
        self.assertTrue(said[0].startswith('self-check of kx3'), said)

    def test_a_self_check_that_finishes_before_the_cut_is_left_alone(self):
        cut = T.chi(2026, 10, 12, 6, 30)
        text, said = self.selfcheck('km3', deadline=cut, now=lambda: T.chi(2026, 10, 11, 20, 0))
        self.assertEqual(text, SELFCHECK_TEXT % 'km3')

    def test_a_self_check_still_running_at_the_school_morning_cut_is_stopped_and_refused(self):
        self.flag('selfcheck_hangs')
        cut = T.chi(2026, 10, 12, 6, 30)

        def now():
            self.assertTrue(wait_for(lambda: os.path.exists(self.seen_path('km3'))), 'the self-check never started')
            return cut  # the program is running, and the cut has come
        with self.assertRaises(SystemExit) as cm:
            self.selfcheck('km3', deadline=cut, now=now)
        msg = str(cm.exception.code)
        self.assertTrue(msg.startswith('REFUSED: the self-check of km3 did not finish before the school-morning cut at Mon 06:30 Chicago time; nothing was written.'), msg)
        self.assertIn('Start it earlier in the evening or on a weekend (or with --school-rule off).', msg)
        self.assertTrue(wait_for(lambda: not alive(self.seen('km3')['pid'])), 'the program must not be left running')

    def test_an_interrupted_self_check_stops_its_program_and_passes_the_interrupt_on(self):
        self.flag('selfcheck_hangs')
        self.plant_stray_handlers()
        started = self.aim_at('km3', signal.SIGTERM)
        with sr.signals_stop_the_program():
            with self.assertRaises(SystemExit) as cm:
                self.selfcheck('km3')
        self.assertEqual(started, [True])
        self.assertEqual(cm.exception.code, 128 + signal.SIGTERM, 'the interrupt is passed on, not turned into a refusal')
        self.assertTrue(wait_for(lambda: not alive(self.seen('km3')['pid'])), 'the program must not be left running')

    @staticmethod
    def refusal(spec, pinned, shown):
        return (f'REFUSED: the self-check of {spec} does not match the pin.\n  pinned: {pinned}\n  got:    {shown}\n'
                'The program is not behaving as the pinned build did; nothing was written.')

    def refused(self, spec='kx3'):
        with self.assertRaises(SystemExit) as cm:
            self.selfcheck(spec)
        return cm.exception.code

    def test_output_that_is_not_text_is_read_with_replacement_characters_and_never_crashes(self):
        bad = b'selfcheck pilot=kx3 \xff\xfe digest=1'
        shown = 'selfcheck pilot=kx3 �� digest=1'
        self.says(bad)
        self.pin['selfcheck']['kx3'] = shown
        text, said = self.selfcheck('kx3')
        self.assertEqual(text, shown, 'the same bytes read the same way twice are the same text')
        self.pin['selfcheck']['kx3'] = 'selfcheck pilot=kx3 digest=0123456789abcdef'
        self.assertEqual(self.refused('kx3'), self.refusal('kx3', self.pin['selfcheck']['kx3'], shown), 'a mismatch is a refusal in words, not a UnicodeDecodeError')

    def test_error_text_that_is_not_text_is_shown_with_replacement_characters_when_nothing_was_printed(self):
        self.says(b'boom \xff\xfe at the end', name='selfcheck_crash_says')
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 1, 'boom �� at the end'))

    def test_a_self_check_that_prints_the_pinned_text_and_then_exits_with_an_error_is_not_a_match(self):
        self.exits_with(3)
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 3, SELFCHECK_TEXT % 'kx3'), 'with nothing on the error stream, the end of what it printed is shown')
        self.assertTrue(os.path.exists(self.seen_path('kx3')), 'it did run')
        self.exits_with(1)
        self.says((SELFCHECK_TEXT % 'kx3').encode())
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 1, SELFCHECK_TEXT % 'kx3'), 'the same through the other way of printing the text')
        self.flag_with('selfcheck_stderr', 'warning: the engine exited badly\n')
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 1, 'warning: the engine exited badly'), 'the error stream comes first when it has something to say')

    def test_what_is_shown_of_a_failed_self_check_is_the_end_of_its_error_stream_else_of_its_output_else_a_word(self):
        self.exits_with(2)
        for n in (1, 199, 200, 201, 700):
            with self.subTest(printed=n):
                printed = ''.join(chr(ord('a') + i % 26) for i in range(n))
                self.says(printed.encode())
                self.flag_with('selfcheck_stderr', '')
                self.assertEqual(self.refused('kx3'), self.failed('kx3', 2, printed[-200:]), 'nothing on the error stream: the last 200 characters of what was printed')
                self.flag_with('selfcheck_stderr', '\n  ' + printed + '  \n')
                self.assertEqual(self.refused('kx3'), self.failed('kx3', 2, printed[-200:]), 'the last 200 characters of the error stream, which come first, without the blank space around them')
        self.says(b'')
        self.flag_with('selfcheck_stderr', '')
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 2, 'no output'))
        self.flag_with('selfcheck_stderr', ' \n\n')
        self.assertEqual(self.refused('kx3'), self.failed('kx3', 2, 'no output'), 'blank space is no output')

    def test_a_self_check_killed_by_a_signal_after_printing_the_pinned_text_is_not_a_match(self):
        self.flag('selfcheck_killed')
        self.assertEqual(self.refused('kx3'), self.failed('kx3', -signal.SIGKILL, SELFCHECK_TEXT % 'kx3'))

    def test_a_self_check_that_exits_cleanly_is_a_match_whatever_it_wrote_to_the_error_stream(self):
        self.flag_with('selfcheck_stderr', 'warning: a deprecated option\n')
        text, said = self.selfcheck('kx3')
        self.assertEqual(text, SELFCHECK_TEXT % 'kx3')
        self.exits_with(0)
        self.assertEqual(self.selfcheck('km3')[0], SELFCHECK_TEXT % 'km3')

    def test_a_mismatch_shows_at_most_the_last_300_characters_of_what_was_printed(self):
        for n in (1, 299, 300, 301, 1000):
            with self.subTest(printed=n):
                printed = ''.join(chr(ord('a') + i % 26) for i in range(n))  # every position is told apart by its letter
                self.says(printed.encode())
                self.assertEqual(self.refused('kx3'), self.refusal('kx3', SELFCHECK_TEXT % 'kx3', printed[-300:]))
        self.says(b'\n\n  ' + b'x' * 400 + b'  \n')
        self.assertEqual(self.refused('kx3'), self.refusal('kx3', SELFCHECK_TEXT % 'kx3', 'x' * 300), 'the blank space around the output is not part of it')

    def test_a_self_check_that_crashes_shows_at_most_the_last_200_characters_of_its_error_stream(self):
        for n in (199, 200, 201, 800):
            with self.subTest(written=n):
                written = ''.join(chr(ord('a') + i % 26) for i in range(n))
                self.says(written.encode() + b'\n', name='selfcheck_crash_says')
                self.assertEqual(self.refused('kx3'), self.failed('kx3', 1, written[-200:]))

    def popen_recorder(self):
        """Every process run_selfcheck starts, kept so that the test can look at its pipes afterwards."""
        made = []
        real = subprocess.Popen

        def popen(*a, **kw):
            p = real(*a, **kw)
            made.append(p)
            return p
        patcher = mock.patch.object(sr.subprocess, 'Popen', popen)
        patcher.start()
        self.addCleanup(patcher.stop)
        return made

    def assert_pipes_closed(self, made, how):
        self.assertEqual(len(made), 1, how + ': one program was started')
        self.assertTrue(made[0].stdout.closed, how + ': the output pipe is closed')
        self.assertTrue(made[0].stderr.closed, how + ': the error pipe is closed')

    def test_the_pipes_are_closed_after_a_self_check_that_matched_and_after_one_that_was_refused(self):
        made = self.popen_recorder()
        self.selfcheck('kx3')
        self.assert_pipes_closed(made, 'a match')
        made.clear()
        self.says(b'something else')
        self.refused('kx3')
        self.assert_pipes_closed(made, 'a refusal')

    def test_the_pipes_are_closed_after_a_self_check_that_was_stopped_at_the_school_morning_cut(self):
        made = self.popen_recorder()
        self.flag('selfcheck_hangs')
        cut = T.chi(2026, 10, 12, 6, 30)

        def now():
            self.assertTrue(wait_for(lambda: os.path.exists(self.seen_path('km3'))), 'the self-check never started')
            return cut
        with self.assertRaises(SystemExit):
            self.selfcheck('km3', deadline=cut, now=now)
        self.assert_pipes_closed(made, 'the cut')
        self.assertTrue(wait_for(lambda: not alive(self.seen('km3')['pid'])), 'the program must not be left running')

    def test_the_pipes_are_closed_after_an_interrupted_self_check(self):
        made = self.popen_recorder()
        self.flag('selfcheck_hangs')
        self.plant_stray_handlers()
        started = self.aim_at('km3', signal.SIGTERM)
        with sr.signals_stop_the_program():
            with self.assertRaises(SystemExit):
                self.selfcheck('km3')
        self.assertEqual(started, [True])
        self.assert_pipes_closed(made, 'an interrupt')

    def test_a_clock_that_fails_while_the_cut_is_worked_out_still_stops_the_program_and_closes_its_pipes(self):
        made = self.popen_recorder()
        self.flag('selfcheck_hangs')

        def now():
            self.assertTrue(wait_for(lambda: os.path.exists(self.seen_path('km3'))), 'the self-check never started')
            raise RuntimeError('the clock broke')
        with self.assertRaises(RuntimeError):
            self.selfcheck('km3', deadline=T.chi(2026, 10, 12, 6, 30), now=now)
        self.assert_pipes_closed(made, 'a failing clock')
        self.assertTrue(wait_for(lambda: not alive(self.seen('km3')['pid'])), 'the program must not be left running')


class SelfcheckOnTheCommandLine(SelfcheckWorld):
    def setUp(self):
        super().setUp()
        self.plant_stray_handlers()
        self.give_up_after(20, 'a self-check that should have been stopped kept running')

    def slot_of_the_deck(self):
        slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
        return (int(sha(self.deck)[:8], 16) % slots), slots

    def test_a_self_check_that_differs_from_the_pin_refuses_and_writes_nothing(self):
        pin = json.loads(read(self.pin_path))
        pin['selfcheck']['kx3'] = 'selfcheck pilot=kx3 games=12 digest=0123456789abcdef'
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        msg = str(code)
        self.assertIn('REFUSED: the self-check of kx3 does not match the pin.', msg)
        self.assertIn('pinned: selfcheck pilot=kx3 games=12 digest=0123456789abcdef', msg)
        self.assertIn('got:    ' + SELFCHECK_TEXT % 'kx3', msg)
        self.assertTrue(msg.endswith('nothing was written.'), msg)
        self.assertTrue(os.path.exists(self.seen_path('km3')) and os.path.exists(self.seen_path('kx3')), 'both pilots are replayed, km3 first')
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_self_check_that_crashes_refuses_with_the_end_of_its_message_and_writes_nothing(self):
        self.flag('selfcheck_crashes')
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertEqual(code, f'{T.HEADLINE_START}my-list v km3 on the public panel] ' + self.failed('km3', 1, 'boom: the engine could not start'))
        self.assertFalse(os.path.exists(self.seen_path('kx3')), 'and the next pilot is not tried')
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_self_check_that_prints_the_pinned_text_but_exits_with_an_error_refuses_and_writes_nothing(self):
        self.exits_with(1)
        for extra in (('--selfcheck',), ('--selfcheck', '--register-only')):
            code, out, err = self.cli('--deals', '1', *extra)
            self.assertEqual(code, f'{T.HEADLINE_START}my-list v km3 on the public panel] ' + self.failed('km3', 1, SELFCHECK_TEXT % 'km3'), 'the text matched; the exit code did not')
            self.assertFalse(os.path.exists(self.seen_path('kx3')), 'km3 first, and it stops there')
            self.assertFalse(os.path.exists(self.out_root), 'nothing was written')
        os.remove(os.path.join(self.tmp, 'selfcheck_exit'))
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')  # without the error the same replay is accepted
        self.assertEqual(code, 0, err + out)

    def test_a_matching_self_check_changes_nothing_else(self):
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
        self.assertEqual(code, 0, err + out)
        slot, slots = self.slot_of_the_deck()
        self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['seed_base'], BLOCK[0] + slot * STEP)
        self.assertNotIn('note:', out)

    def test_a_stop_signal_during_the_self_check_stops_the_program_and_writes_nothing(self):
        self.flag('selfcheck_hangs')
        started = self.aim_at('km3', signal.SIGTERM)
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertEqual(started, [True])
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertTrue(wait_for(lambda: not alive(self.seen('km3')['pid'])), 'the program must not be left running')
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_self_check_is_refused_in_school_hours_and_nothing_is_started(self):
        self.clock = T.FakeClock(T.chi(2026, 10, 7, 10, 0))  # a Wednesday morning
        code, out, err = self.cli('--deals', '1', '--selfcheck', school='on')
        msg = str(code)
        self.assertIn('REFUSED: the self-check runs for hours and it is school time (the school-morning rule waits until Wed 17:00 Chicago time)', msg)
        self.assertIn('start it after that, or with --school-rule off', msg)
        self.assertFalse(os.path.exists(self.seen_path('km3')), 'the program was not started')
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_self_check_is_given_the_next_school_morning_cut_as_its_deadline(self):
        refused, none = 'refused', 'no deadline'
        wed, thu, mon = [T.chi(2026, 10, d, 6, 30) for d in (7, 8, 12)]
        cases = [(T.chi(2026, 10, 7, 17, 0), (), 'on', thu), (T.chi(2026, 10, 7, 20, 0), (), 'on', thu), (T.chi(2026, 10, 9, 20, 0), (), 'on', mon),
                 (T.chi(2026, 10, 10, 10, 0), (), 'on', mon), (T.chi(2026, 10, 7, 4, 0), (), 'on', wed),
                 (T.chi(2026, 10, 7, 10, 0), (), 'off', none), (T.chi(2026, 10, 7, 10, 0), ('--school-days', ''), 'on', none),
                 (T.chi(2026, 10, 7, 10, 0), ('--school-days', 'thu,fri'), 'on', thu),
                 (T.chi(2026, 10, 7, 5, 15), (), 'on', refused), (T.chi(2026, 10, 7, 10, 0), (), 'on', refused), (T.chi(2026, 10, 7, 16, 59), (), 'on', refused)]
        for at, extra, rule, want in cases:
            with self.subTest(at=at.strftime('%a %H:%M'), extra=extra, rule=rule):
                self.clock = T.FakeClock(at)
                calls = []

                def stop_here(pin, repo, spec, say, deadline=None, now=None):
                    calls.append((spec, deadline, now()))
                    raise SystemExit('stop here')
                with mock.patch.object(sr, 'run_selfcheck', stop_here):
                    code, out, err = self.cli('--deals', '1', '--selfcheck', *extra, school=rule)
                if want == refused:
                    self.assertEqual(calls, [], 'refused before the self-check started')
                    self.assertIn('school time', str(code))
                else:
                    self.assertEqual(len(calls), 1, (code, calls))
                    self.assertEqual(calls[0][1], None if want == none else want)
                    self.assertEqual(calls[0][2], at, 'the self-check reads the same clock')
                self.assertFalse(os.path.exists(self.out_root))

    def test_a_run_folder_that_appeared_while_the_self_check_ran_is_not_written_into(self):
        self.meanwhile(['mkdir', self.rundir()])
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertIn('REFUSED: the run directory', str(code))
        self.assertIn('appeared while the self-check ran', str(code))
        self.assertIn('--dir ' + self.rundir(), str(code))
        self.assertEqual(os.listdir(self.rundir()), [], 'nothing was written into it')

    def test_the_run_folder_in_that_refusal_is_quoted_for_the_shell_when_it_has_a_space(self):
        self.out_root = os.path.join(self.tmp, 'results with a space')
        self.meanwhile(['mkdir', self.rundir()])
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        d = self.rundir()
        self.assertEqual(code, f'{T.HEADLINE_START}my-list v km3 on the public panel] REFUSED: the run directory {d} appeared while the self-check ran; '
                               f'resume it with --dir {shlex.quote(d)} (or pick another --date)')
        self.assertTrue(shlex.quote(d).startswith("'"), 'the path really needed quoting')
        self.assertEqual(shlex.split(str(code).split('resume it with --dir ', 1)[1].split(' (or pick', 1)[0]), [d], 'a shell reads it back as the one folder')

    def test_a_seed_slot_taken_while_the_self_check_ran_is_replaced_by_the_next_free_one(self):
        slot, slots = self.slot_of_the_deck()
        taken = BLOCK[0] + slot * STEP
        self.meanwhile(['write', os.path.join(self.out_root, '2026-10-09_other', 'manifest.json'), json.dumps({'seed_base': taken})])
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
        self.assertEqual(code, 0, err + out)
        later = BLOCK[0] + ((slot + 1) % slots) * STEP
        self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['seed_base'], later)
        self.assertIn(f'note: seed slot {taken} was taken while the self-check ran; using {later}', out)

    def test_an_explicit_seed_base_taken_while_the_self_check_ran_is_refused(self):
        slot, slots = self.slot_of_the_deck()
        taken = BLOCK[0] + slot * STEP
        self.meanwhile(['write', os.path.join(self.out_root, '2026-10-09_other', 'manifest.json'), json.dumps({'seed_base': taken})])
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--seed-base', str(taken))
        self.assertIn(f'REFUSED: --seed-base {taken} is a seed slot that is already used (2026-10-09_other); two reports would play the same deals', str(code))
        self.assertFalse(os.path.exists(self.rundir()))

    def test_a_reserved_slot_stays_reserved_when_the_seed_is_decided_again_after_the_self_check(self):
        for slot in (684, 685, 686):
            with self.subTest(slot=slot):
                write(self.deck, T.deck_text_in_slot(slot))  # a deck that would land in a slot the pin reserves
                shutil.rmtree(self.out_root, ignore_errors=True)
                code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
                self.assertEqual(code, 0, err + out)
                self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['seed_base'], BLOCK[0] + 687 * STEP)
                self.assertNotIn('note:', out, 'the slot decided before the self-check is the one decided after it')


class ReplayOnResumeIsStoppable(Leftovers, T.RebuiltFixture):
    """A resume whose program is another file replays both self-checks on it (hours for kx3) before the run goes on. That replay is stopped by SIGTERM and SIGHUP like the one at
    the registration: the program it started goes, the run lock is let go, the call ends with 128 + the signal, and nothing is logged as accepted (the run can be resumed again)."""

    def setUp(self):
        super().setUp()
        self.plant_stray_handlers()
        self.give_up_after(30, 'a replay that should have been stopped kept running')

    def test_a_stop_signal_during_the_replay_of_a_changed_program_stops_it_and_releases_the_lock(self):
        for sig in STOP_SIGNALS:
            with self.subTest(sig=sig.name):
                self.make()
                self.lay_out_harness()
                code, out, err = self.cli('--deals', '1', '--max-games', '4', '--program', self.cloud)
                self.assertEqual(code, 0, out + err)
                d = self.rundir()
                there = os.path.dirname(self.cloud)
                self.put_program(self.cloud, SELFCHECK_PROGRAM)  # the rebuild after the restart: its self-check records itself and hangs
                write(os.path.join(there, 'selfcheck_hangs'), '')
                seen = os.path.join(there, 'seen_km3.json')
                started = []

                def go():
                    started.append(wait_for(lambda: os.path.exists(seen), 30))
                    signal.pthread_kill(threading.main_thread().ident, sig)
                t = threading.Thread(target=go, daemon=True)
                t.start()
                self.addCleanup(t.join, 5)
                events = [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))]
                games = len(jsonl(os.path.join(d, 'games.jsonl')))
                code, out, err = self.cli('--dir', d, deck=False)
                self.assertEqual(started, [True], 'the replay really started')
                self.kill_at_end(json.loads(read(seen))['pid'])  # (so that nothing is left sleeping when an assertion below fails)
                self.assertEqual(code, 128 + sig)
                self.assertTrue(wait_for(lambda: not alive(json.loads(read(seen))['pid'])), 'the program of the replay must not be left running')
                self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'the lock is released')
                self.assertEqual([e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))], events, 'nothing was logged: not as accepted, not as a sitting')
                self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), games, 'and no game was played')
                self.assertFalse(os.path.exists(os.path.join(there, 'seen_kx3.json')), 'the second self-check was never started')


# ---------------------------------------------------------------------------------------------------------- stop signals reach the whole call
class StopSignalsReachTheWholeCall(Leftovers, T.World):
    def setUp(self):
        super().setUp()
        self.plant_stray_handlers()
        self.give_up_after(30, 'a program that should have been stopped kept running')

    def test_a_stop_signal_during_the_registration_leaves_nothing_behind(self):
        for sig in STOP_SIGNALS:
            with self.subTest(sig=sig.name):
                self.assertFalse(os.path.exists(self.out_root))
                registering = []

                def prereg(cfg_path, rundir, repo):
                    registering.append(sorted(os.listdir(rundir)))
                    os.kill(os.getpid(), sig)
                    time.sleep(2)
                    raise AssertionError('the signal did not stop the registration')
                with mock.patch.object(sr, 'run_prereg', prereg):
                    code, out, err = self.cli('--deals', '1')
                self.assertEqual(registering, [['config.json']], 'the signal arrived with a half-made run folder on disk')
                self.assertEqual(code, 128 + sig)
                self.assertFalse(os.path.exists(self.rundir()))
                self.assertFalse(os.path.exists(self.out_root), 'the results folder this call made is removed too')

    def test_a_stop_signal_while_waiting_for_5_pm_ends_the_call_with_no_program_started_and_the_lock_released(self):
        d = self.register()
        self.clock = T.FakeClock(T.chi(2026, 10, 7, 12, 0))  # a Wednesday afternoon: the school-morning rule makes the run wait for 5 pm

        def sleep(seconds):
            os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(2)
        self.clock.sleep = sleep
        code, out, err = self.cli('--dir', d, deck=False, school='on', spawn=lambda cmd, env, logfile: self.fail('no program may start while waiting'))
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertIn('school-morning rule: waiting until Wed 17:00 Chicago time to start again (32 games to go)', out)
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'the lock is released')
        self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')))

    def test_a_stop_signal_during_a_run_stops_the_program_and_leaves_the_lock_the_log_and_a_page_in_order(self):
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')  # the first game never finishes
        procs, n = [], [0]

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            procs.append(p)
            self.kill_at_end(p.pid)
            return p

        def sleep(seconds):
            n[0] += 1
            if n[0] == 3:
                os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(0.05)
        self.clock.sleep = sleep
        code, out, err = self.cli('--dir', d, deck=False, spawn=spawn)
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertEqual(len(procs), 1)
        self.assertEqual(procs[0].returncode, -signal.SIGTERM, 'the program was stopped politely, and is gone')
        self.assertTrue(procs[0]._logfh.closed, "the program's log file is closed after an interrupt")
        self.assertIn('interrupted', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))])
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'the lock is released')
        self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')), 'what exists is not lost')


# ---------------------------------------------------------------------------------------------------------- the program's process and the partial page
class ProgramProcess(Leftovers, T.World):
    def test_the_program_gets_no_standard_input(self):
        log = os.path.join(self.tmp, 'stdin.log')
        with pipe_as_stdin():
            proc = sr.default_spawn([sys.executable, '-c', 'import os; print(os.readlink("/proc/self/fd/0"))'], dict(os.environ), log)
            self.addCleanup(proc._logfh.close)
            proc.wait(timeout=20)
        self.assertEqual(read(log).strip(), '/dev/null')

    def test_the_programs_log_file_is_closed_when_a_sitting_ends_and_when_it_is_interrupted(self):
        procs = []

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            procs.append(p)
            self.kill_at_end(p.pid)
            return p
        code, out, err = self.cli('--deals', '1', '--max-games', '2', spawn=spawn)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(len(procs), 1)
        self.assertTrue(procs[0]._logfh.closed, 'closed after a sitting that ended')
        d = self.rundir()
        write(os.path.join(d, 'hang.flag'), '2')  # two more games, then one that never finishes
        n = [0]

        def sleep(seconds):
            n[0] += 1
            if n[0] == 3:
                raise KeyboardInterrupt
            time.sleep(0.05)
        self.clock.sleep = sleep
        with self.assertRaises(KeyboardInterrupt):
            self.cli('--dir', d, '--max-games', '5', deck=False, spawn=spawn)
        self.assertEqual(len(procs), 2)
        self.assertIsNotNone(procs[1].poll(), 'the program is not left running')
        self.assertTrue(procs[1]._logfh.closed, 'closed after an interrupted sitting')

    def test_a_second_ctrl_c_while_the_partial_page_is_written_is_not_swallowed(self):
        self.set_program("#!/usr/bin/env python3\nimport sys\nsys.exit(3)\n")
        with mock.patch.object(sr, 'write_slow_report', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.cli('--deals', '1')
        self.assertFalse(os.path.exists(os.path.join(self.rundir(), 'slow_report.lock')), 'and the lock is released on the way out')

    def test_a_page_that_cannot_be_written_does_not_hide_why_the_run_stopped(self):
        self.set_program("#!/usr/bin/env python3\nimport sys\nsys.exit(3)\n")
        with mock.patch.object(sr, 'write_slow_report', side_effect=OSError('disk full')):
            code, out, err = self.cli('--deals', '1')
        self.assertIn('the program stopped with exit code 3', str(code))
        self.assertIn('could not write the page before stopping: disk full', out)


class PartialPageWriter(T.Timed):
    def run_it(self, effect):
        said = []
        with mock.patch.object(sr.subprocess, 'run'), mock.patch.object(sr, 'write_slow_report', side_effect=effect):
            sr.best_effort_pages('/nowhere', said.append)
        return said

    def test_a_page_that_is_written_is_announced(self):
        self.assertEqual(self.run_it(None), ['SLOW_REPORT.md (partial) written before stopping'])

    def test_whatever_goes_wrong_is_said_not_raised_so_the_real_error_comes_through(self):
        self.assertEqual(self.run_it(OSError('disk full')), ['could not write the page before stopping: disk full'])
        self.assertEqual(self.run_it(SystemExit('/x has no manifest.json: it is not a registered run')),
                         ['could not write the page before stopping: /x has no manifest.json: it is not a registered run'], 'a refusal inside the writer too')

    def test_a_ctrl_c_is_never_swallowed(self):
        said = []
        with mock.patch.object(sr.subprocess, 'run'), mock.patch.object(sr, 'write_slow_report', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                sr.best_effort_pages('/nowhere', said.append)
        self.assertEqual(said, [])


# ---------------------------------------------------------------------------------------------------------- the run lock
class RunLockDetails(T.World):
    def setUp(self):
        super().setUp()
        self.before = list(sr._LOCK_FDS)
        self.addCleanup(lambda: sr._LOCK_FDS.__setitem__(slice(None), self.before))
        self.programs_before = list(sr._PROGRAMS)  # the programs a wrapper started: a test that adds one must not leave it for the next test's release
        self.addCleanup(lambda: sr._PROGRAMS.__setitem__(slice(None), self.programs_before))
        self.dir = self.fresh_dir('rundir')
        self.path = os.path.join(self.dir, 'slow_report.lock')

    def fresh_dir(self, name):
        d = os.path.join(self.tmp, name)
        os.makedirs(d)
        return d

    def test_a_lock_whose_note_nobody_can_read_is_still_refused_and_the_note_is_left_alone(self):
        for note in (b'', b'{not json', b'\xff\xfe\x00{', b'[1, 2]', b'null', b'"text"', b'3'):
            with self.subTest(note=note):
                fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_TRUNC)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                os.write(fd, note)
                try:
                    open_before = open_descriptors()
                    with self.assertRaises(SystemExit) as cm:
                        sr.acquire_lock(self.dir, lambda m: None)
                    self.assertEqual(open_descriptors(), open_before, 'the refusal closes the descriptor it opened')
                    self.assertEqual(sr._LOCK_FDS, self.before)
                    with open(self.path, 'rb') as f:
                        self.assertEqual(f.read(), note, "somebody else's note is not touched")
                finally:
                    os.close(fd)
                msg = str(cm.exception.code)
                self.assertTrue(msg.startswith('REFUSED: another slow_report.py (pid unknown, started unknown) or the program it started is already running '), msg)

    def test_a_note_with_no_holder_is_replaced_whatever_it_says(self):
        for junk in (b'', b'{not json', b'\xff\xfe\x00{', b'[1, 2]', b'null', b'x' * 500):
            with self.subTest(junk=junk[:12]):
                with open(self.path, 'wb') as f:
                    f.write(junk)
                lock = sr.acquire_lock(self.dir, lambda m: None)
                try:
                    with open(self.path, 'rb') as f:
                        raw = f.read()
                    note = json.loads(raw)
                    self.assertEqual(sorted(note), ['pid', 'started'], raw)
                    self.assertEqual(note['pid'], os.getpid())
                    datetime.datetime.strptime(note['started'], '%Y-%m-%dT%H:%M:%SZ')
                    self.assertEqual(sr.read_lock_info(self.path), note)
                finally:
                    sr.release_lock(lock)
                self.assertFalse(os.path.exists(self.path))
                self.assertEqual(sr._LOCK_FDS, self.before)

    def test_what_a_lock_file_says_is_read_without_ever_failing(self):
        note = {'pid': 4242, 'started': '2026-10-10T10:00:00Z'}
        for label, content, want in (('a note', json.dumps(note).encode(), note), ('nothing', b'', {}), ('not json', b'{not json', {}), ('not text', b'\xff\xfe\x00{', {}),
                                     ('a list', b'[1]', {}), ('null', b'null', {}), ('a number', b'7', {})):
            with self.subTest(label):
                with open(self.path, 'wb') as f:
                    f.write(content)
                self.assertEqual(sr.read_lock_info(self.path), want)
        os.remove(self.path)
        self.assertEqual(sr.read_lock_info(self.path), {}, 'no file')
        os.mkdir(self.path)
        self.assertEqual(sr.read_lock_info(self.path), {}, 'a directory')
        os.rmdir(self.path)
        if os.geteuid() != 0:
            write(self.path, json.dumps(note))
            os.chmod(self.path, 0)
            self.assertEqual(sr.read_lock_info(self.path), {}, 'a file nobody here may read')

    def test_releasing_a_lock_whose_file_has_vanished_is_quiet_and_still_frees_the_descriptor(self):
        fd, path = sr.acquire_lock(self.dir, lambda m: None)
        os.remove(path)
        sr.release_lock((fd, path))
        self.assertNotIn(fd, sr._LOCK_FDS)
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_a_release_removes_the_file_and_the_next_wrapper_can_take_it(self):
        lock = sr.acquire_lock(self.dir, lambda m: None)
        self.assertTrue(os.path.exists(self.path))
        sr.release_lock(lock)
        self.assertFalse(os.path.exists(self.path))
        sr.release_lock(sr.acquire_lock(self.dir, lambda m: None))

    def a_program_that_keeps_running(self):
        """A program started the way the wrapper starts it (it inherits the lock descriptor), still running once it has said so."""
        log = os.path.join(self.tmp, 'program.log')
        proc = sr.default_spawn([sys.executable, '-c', 'import time\nprint("up", flush=True)\ntime.sleep(60)'], dict(os.environ), log)
        self.addCleanup(proc._logfh.close)
        self.addCleanup(proc.wait)  # (cleanups run last in, first out: the kill comes first, then the wait)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        self.assertTrue(wait_for(lambda: 'up' in read(log)), 'the program never got going')
        return proc

    def test_the_lock_file_stays_while_a_program_this_wrapper_started_is_still_running_and_goes_when_it_has_ended(self):
        lock = sr.acquire_lock(self.dir, lambda m: None)
        proc = self.a_program_that_keeps_running()
        sr._PROGRAMS.append(proc)
        sr.note_program(proc)
        sr.release_lock(lock)
        self.assertTrue(os.path.exists(self.path), 'the file stays, so that the next wrapper is refused while the program plays on')
        self.assertNotIn(lock[0], sr._LOCK_FDS)
        with self.assertRaises(OSError):
            os.fstat(lock[0])
        self.assertEqual(sr._PROGRAMS, [proc], 'a program that is still running stays on the list')
        with self.assertRaises(SystemExit) as cm:
            sr.acquire_lock(self.dir, lambda m: None)
        self.assertTrue(str(cm.exception.code).endswith(f'(kill -TERM -{proc.pid}).'), 'the program holds the lock through the descriptor it inherited: ' + str(cm.exception.code))
        proc.kill()
        proc.wait()
        second = sr.acquire_lock(self.dir, lambda m: None)
        self.assertEqual(sorted(sr.read_lock_info(self.path)), ['pid', 'started'], 'the note of the program before is not kept')
        sr.release_lock(second)
        self.assertFalse(os.path.exists(self.path), 'with the program gone the file goes with the release')
        self.assertEqual(sr._PROGRAMS, [], 'a program that has ended is forgotten')

    def test_only_programs_that_are_still_running_keep_the_file_and_the_others_are_forgotten(self):
        class Proc:
            def __init__(self, rc):
                self.rc = rc

            def poll(self):
                return self.rc
        ended, running = Proc(0), Proc(None)
        for label, programs, kept, left in (('none', [], False, []), ('one that has ended', [ended], False, []), ('one that failed', [Proc(-9)], False, []),
                                            ('one ended, one running', [ended, running], True, [running]), ('one running, two ended', [running, ended, Proc(-9)], True, [running])):
            with self.subTest(label):
                sr._PROGRAMS[:] = programs
                sr.release_lock(sr.acquire_lock(self.dir, lambda m: None))
                self.assertEqual(os.path.exists(self.path), kept)
                self.assertEqual(sr._PROGRAMS, left)
                if kept:
                    os.remove(self.path)

    def test_a_lock_file_that_cannot_be_removed_is_no_error_whatever_the_reason(self):
        for exc in (PermissionError(errno.EACCES, 'Permission denied'), IsADirectoryError(errno.EISDIR, 'Is a directory'), OSError(errno.EIO, 'Input/output error')):
            with self.subTest(type(exc).__name__):
                lock = sr.acquire_lock(self.dir, lambda m: None)
                with mock.patch.object(sr.os, 'remove', side_effect=exc):
                    sr.release_lock(lock)
                self.assertTrue(os.path.exists(self.path), 'nothing removed it')
                self.assertNotIn(lock[0], sr._LOCK_FDS)
                with self.assertRaises(OSError):
                    os.fstat(lock[0])
                os.remove(self.path)

    def test_a_lock_file_that_cannot_be_opened_is_refused_in_words(self):
        os.mkdir(self.path)  # a folder where the file should be
        missing = os.path.join(self.tmp, 'no-such-folder')
        for rundir, why in ((self.dir, 'Is a directory'), (missing, 'No such file or directory')):
            with self.subTest(why):
                before = open_descriptors()
                with self.assertRaises(SystemExit) as cm:
                    sr.acquire_lock(rundir, lambda m: None)
                self.assertEqual(cm.exception.code, f"REFUSED: cannot open the lock file {os.path.join(rundir, 'slow_report.lock')} ({why}); "
                                                    'if no other slow_report.py is running on this folder, remove it')
                self.assertEqual(open_descriptors(), before)
                self.assertEqual(sr._LOCK_FDS, self.before)
        self.assertTrue(os.path.isdir(self.path), 'the folder in the way was not touched')

    def test_a_file_system_that_cannot_lock_is_refused_in_words_and_is_not_taken_for_a_running_wrapper(self):
        for code in (errno.ENOLCK, errno.EACCES, errno.EOPNOTSUPP):
            with self.subTest(errno.errorcode[code]):
                before = open_descriptors()
                with mock.patch.object(sr.fcntl, 'flock', side_effect=OSError(code, os.strerror(code))):
                    with self.assertRaises(SystemExit) as cm:
                        sr.acquire_lock(self.dir, lambda m: None)
                self.assertEqual(cm.exception.code, f'REFUSED: cannot lock {self.path} ({os.strerror(code)}); this file system may not support flock')
                self.assertNotIn('already running', cm.exception.code)
                self.assertEqual(open_descriptors(), before, 'the descriptor it opened is closed')
                self.assertEqual(sr._LOCK_FDS, self.before)
        sr.release_lock(sr.acquire_lock(self.dir, lambda m: None))  # and the file left behind is no lock: the next wrapper takes it

    def hold_with_note(self, note):
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_TRUNC)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, json.dumps(note).encode())
        self.addCleanup(os.close, fd)

    def test_a_refusal_names_the_group_to_stop_when_the_note_has_one_and_ends_there_when_it_has_not(self):
        started = '2026-10-10T10:00:00Z'
        head = f'REFUSED: another slow_report.py (pid 4242, started {started}) or the program it started is already running {self.dir}; '
        tail = 'two wrappers on one run would play the same games twice. If its wrapper was killed, the program plays on until its sitting ends or you stop it'
        self.hold_with_note({'pid': 4242, 'started': started, 'program_pgid': 31337})
        with self.assertRaises(SystemExit) as cm:
            sr.acquire_lock(self.dir, lambda m: None)
        self.assertEqual(cm.exception.code, head + tail + ' (kill -TERM -31337).')
        for label, extra in (('no group', {}), ('a group as text', {'program_pgid': '31337'}), ('a group that is null', {'program_pgid': None}), ('a fraction', {'program_pgid': 12.5})):
            with self.subTest(label):
                with open(self.path, 'r+b') as f:  # the holder's descriptor is another one on the same file: rewrite the note through this one
                    f.truncate(0)
                    f.write(json.dumps(dict({'pid': 4242, 'started': started}, **extra)).encode())
                with self.assertRaises(SystemExit) as cm:
                    sr.acquire_lock(self.dir, lambda m: None)
                self.assertEqual(cm.exception.code, head + tail + '.')

    def test_a_lock_opened_on_descriptor_0_1_or_2_is_moved_up_so_the_program_can_inherit_it(self):
        child = textwrap.dedent('''
            import fcntl, json, os, sys, traceback
            sys.path.insert(0, %r)
            import slow_report as sr
            rundir, result, logfile = sys.argv[1:4]
            out = {}
            try:
                for n in (0, 1, 2):
                    os.close(n)  # as a wrapper started with its standard streams closed would have
                fd, path = sr.acquire_lock(rundir, lambda m: None)
                real = os.path.realpath(path)
                out['fd'] = fd
                out['lock_fds'] = list(sr._LOCK_FDS)
                out['on_the_file'] = sorted(int(n) for n in os.listdir('/proc/self/fd') if os.path.realpath('/proc/self/fd/' + n) == real)
                other = os.open(path, os.O_RDWR)  # another open of the file: the lock must be held through the moved descriptor
                try:
                    fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    out['held'] = False
                except BlockingIOError:
                    out['held'] = True
                os.close(other)
                for n in range(3):
                    os.open(os.devnull, os.O_RDWR)  # standard streams again, as the program is started from a normal process
                p = sr.default_spawn([sys.executable, '-c', 'import os, sys; print(os.path.realpath("/proc/self/fd/" + sys.argv[1]))', str(fd)], dict(os.environ), logfile)
                p.wait()
                with open(logfile) as f:
                    out['inherited'] = f.read().strip()
                out['real'] = real
            except BaseException:
                out['error'] = traceback.format_exc()
            with open(result, 'w') as f:
                json.dump(out, f)
        ''' % HERE)
        result, logfile = os.path.join(self.tmp, 'result.json'), os.path.join(self.tmp, 'child.log')
        r = subprocess.run([sys.executable, '-B', '-c', child, self.dir, result, logfile], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
        self.assertTrue(os.path.exists(result), r.stderr)
        out = json.loads(read(result))
        self.assertNotIn('error', out, out.get('error'))
        self.assertGreaterEqual(out['fd'], 3, 'descriptors 0, 1 and 2 are the program\'s standard streams, which a lock held there would not reach')
        self.assertEqual(out['lock_fds'], [out['fd']])
        self.assertEqual(out['on_the_file'], [out['fd']], 'the descriptor it first got is closed: one descriptor holds the file')
        self.assertTrue(out['held'], 'the lock is held through the moved descriptor')
        self.assertEqual(out['inherited'], out['real'], 'the program has the lock file open at that number')

    def test_the_program_group_is_added_to_the_note_and_the_rest_of_the_note_is_kept(self):
        lock = sr.acquire_lock(self.dir, lambda m: None)
        self.addCleanup(sr.release_lock, lock)
        first = sr.read_lock_info(self.path)
        self.assertEqual(sorted(first), ['pid', 'started'])
        sr.note_program(types.SimpleNamespace(pid=31337))
        self.assertEqual(sr.read_lock_info(self.path), dict(first, program_pgid=31337))
        sr.note_program(types.SimpleNamespace(pid=4242))
        self.assertEqual(sr.read_lock_info(self.path), dict(first, program_pgid=4242), 'the next program replaces the one before, and a shorter note leaves nothing of the longer one')

    def test_noting_a_program_without_a_lock_or_with_a_lock_that_cannot_be_written_is_no_error(self):
        with mock.patch.object(sr, '_LOCK_FDS', []):
            sr.note_program(types.SimpleNamespace(pid=31337))  # no lock held
        self.assertFalse(os.path.exists(self.path))
        fd, path = sr.acquire_lock(self.dir, lambda m: None)
        os.close(fd)  # gone behind its back
        sr.note_program(types.SimpleNamespace(pid=31337))
        sr.release_lock((fd, path))  # and the release of it is quiet too

    def lock_that_changes_under_us(self, rundir, how, times):
        """acquire_lock with the file changed between its open and its flock, as a holder that is finishing would: `how` is 'removed' or 'replaced'.
        Returns (what acquire_lock returned or its refusal message, the descriptors flock was called with, the open descriptors before)."""
        path = os.path.join(rundir, 'slow_report.lock')
        real = fcntl.flock
        calls = []

        def flock(fd, op):
            calls.append(fd)
            if len(calls) <= times:
                if how == 'replaced':
                    write(path + '.new', '')
                    os.rename(path + '.new', path)
                else:
                    os.remove(path)
            return real(fd, op)
        before = open_descriptors()
        with mock.patch.object(sr.fcntl, 'flock', flock):
            try:
                return sr.acquire_lock(rundir, lambda m: None), calls, before
            except SystemExit as e:
                return str(e.code), calls, before

    def test_a_lock_file_that_was_removed_or_replaced_before_we_locked_it_is_not_the_lock(self):
        for how in ('removed', 'replaced'):
            with self.subTest(how):
                rundir = self.fresh_dir('once-' + how)
                lock, calls, before = self.lock_that_changes_under_us(rundir, how, 1)
                self.assertIsInstance(lock, tuple, lock)
                self.addCleanup(sr.release_lock, lock)
                fd, path = lock
                self.assertEqual(len(calls), 2, 'the first lock was on a file that is no longer the lock file, so it tried again')
                self.assertEqual(os.fstat(fd).st_ino, os.stat(path).st_ino, 'the lock we hold is on the file on disk')
                self.assertEqual(open_descriptors(), before + 1, 'the descriptor of the first try was closed')
                with self.assertRaises(SystemExit):
                    sr.acquire_lock(rundir, lambda m: None)  # the lock is really held: a second wrapper is refused

    def test_a_lock_file_that_keeps_changing_is_given_up_on_after_a_few_tries(self):
        for how in ('removed', 'replaced'):
            with self.subTest(how):
                rundir = self.fresh_dir('always-' + how)
                msg, calls, before = self.lock_that_changes_under_us(rundir, how, 100)
                self.assertEqual(msg, f"REFUSED: could not take the lock {os.path.join(rundir, 'slow_report.lock')}")
                self.assertEqual(len(calls), 5)
                self.assertEqual(open_descriptors(), before, 'no descriptor is left open')
                self.assertEqual(sr._LOCK_FDS, self.before)


# ---------------------------------------------------------------------------------------------------------- clean refusals
class CleanRefusals(T.World):
    def cli_with_deck(self, deck, *extra):
        """sr.main on a deck path of the test's choosing (cli() always uses self.deck)."""
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sr.main([deck] + self.argv(*extra, deck=False, school='off') + ['--out-root', self.out_root, '--date', '2026-10-10'],
                               now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def test_a_deck_file_that_does_not_exist_is_refused_by_name_and_nothing_is_written(self):
        gone = os.path.join(self.repo, 'decks', 'events', 'nothing-here.txt')
        code, out, err = self.cli_with_deck(gone, '--deals', '1')
        self.assertEqual(code, f'[kx3 (d513e37b) on nothing-here v km3 on the public panel] REFUSED: deck file {gone} not found')
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_deck_file_name_that_is_not_filename_safe_is_refused_by_the_wrapper(self):
        for bad in ('my list (v2).txt', '.hidden.txt', '-dash.txt', 'a;b.txt', 'two words.txt', 'd' + chr(0xE9) + '.txt'):  # the last one has an accent
            with self.subTest(bad):
                path = os.path.join(self.repo, 'decks', 'events', bad)
                write(path, T.DECK_TEXT)
                code, out, err = self.cli_with_deck(path, '--deals', '1', '--register-only')
                self.assertIn('REFUSED: the deck file name', str(code))
                self.assertIn(repr(os.path.splitext(bad)[0]), str(code))
                self.assertFalse(os.path.exists(self.out_root), 'nothing is written for a name that cannot name a folder')

    def test_a_folder_that_is_not_a_registered_run_is_refused_by_name(self):
        empty = os.path.join(self.tmp, 'not-a-run')
        os.makedirs(empty)
        for where in (empty, os.path.join(self.tmp, 'no-such-folder')):
            for extra in ((), ('--report-only',), ('--dry-run',)):
                with self.subTest(where=os.path.basename(where), extra=extra):
                    code, out, err = self.cli('--dir', where, *extra, deck=False)
                    self.assertIn(f'{where} has no manifest.json: it is not a registered run', str(code))
        self.assertEqual(os.listdir(empty), [])

    def test_a_pin_without_a_required_key_is_refused_naming_the_key(self):
        committed = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        keys = ['pilot', 'reference', 'pilot_label', 'reference_label', 'panel_label', 'panel_group', 'program', 'program_sha256', 'selfcheck', 'selfcheck_measured_on_sha256',
                'harness_source_sha256', 'engine', 'pilot_provenance', 'reference_provenance', 'seed_block', 'seed_step', 'games_per_hour', 'scrub_env_prefixes', 'threads',
                'seed_reserved']
        path = os.path.join(self.tmp, 'one-key-short.json')
        self.assertEqual(sr.load_pin(sr.DEFAULT_PIN)['pilot'], 'kx3', 'the committed pin has every key')
        for key in keys:
            with self.subTest(key):
                write(path, json.dumps({k: v for k, v in committed.items() if k != key}))
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(path)
                self.assertEqual(cm.exception.code, f'the pin {path} has no {key!r}')

    def test_a_pin_without_a_key_stops_the_call_before_anything_is_written(self):
        pin = json.loads(read(self.pin_path))
        del pin['seed_block']
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, f"[slow report] the pin {self.pin_path} has no 'seed_block'")
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_pin_that_cannot_be_read_is_refused_with_the_reason(self):
        gone = os.path.join(self.tmp, 'no-such-pin.json')
        folder = os.path.join(self.tmp, 'a-folder')
        os.makedirs(folder)
        torn = os.path.join(self.tmp, 'torn.json')
        write(torn, '{"pilot": "kx3", ')
        empty = os.path.join(self.tmp, 'empty.json')
        write(empty, '')
        binary = os.path.join(self.tmp, 'binary.json')
        T.write_bytes(binary, b'\xff\xfe\x00{')
        for label, path, why in (('no such file', gone, 'No such file or directory'), ('a folder', folder, 'Is a directory'), ('torn JSON', torn, 'Expecting'),
                                 ('an empty file', empty, 'Expecting value'), ('bytes that are not text', binary, "'utf-8' codec can't decode")):
            with self.subTest(label):
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(path)
                msg = cm.exception.code
                self.assertTrue(msg.startswith(f'cannot read the pin {path}: '), msg)
                self.assertIn(why, msg)
                code, out, err = self.cli('--deals', '1', '--dry-run', '--pin', path)  # the last --pin wins
                self.assertTrue(str(code).startswith(f'[slow report] cannot read the pin {path}: '), code)
                self.assertFalse(os.path.exists(self.out_root))

    def test_a_pin_that_is_not_a_json_object_is_refused_as_such(self):
        path = os.path.join(self.tmp, 'not-an-object.json')
        for text in ('null', '[]', '[{"pilot": "kx3"}]', '7', '"kx3"', 'true', '1.5'):
            with self.subTest(text):
                write(path, text)
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(path)
                self.assertEqual(cm.exception.code, f'the pin {path} is not a JSON object')
                code, out, err = self.cli('--deals', '1', '--dry-run', '--pin', path)
                self.assertEqual(code, f'[slow report] the pin {path} is not a JSON object')

    def test_each_pilots_provenance_is_required_in_the_pin_and_the_committed_pin_has_both(self):
        committed = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        path = os.path.join(self.tmp, 'pin-without-provenance.json')
        for key in ('pilot_provenance', 'reference_provenance'):
            with self.subTest(key):
                self.assertIsInstance(committed[key], str)
                self.assertTrue(committed[key].strip(), 'the committed pin says where each pilot came from')
                write(path, json.dumps({k: v for k, v in committed.items() if k != key}))
                code, out, err = self.cli('--deals', '1', '--dry-run', '--pin', path)
                self.assertEqual(code, f'[slow report] the pin {path} has no {key!r}')
                self.assertFalse(os.path.exists(self.out_root))

    def test_a_deck_or_panel_file_that_has_gone_is_a_refusal_not_a_crash(self):
        d = self.register()
        panel = os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-weezing.txt')
        for gone, name in ((self.deck, 'my-list'), (panel, 't-weezing')):
            with self.subTest(name):
                os.rename(gone, gone + '.away')
                try:
                    code, out, err = self.cli('--dir', d, deck=False)
                    dry = self.cli('--dir', d, '--dry-run', deck=False)
                finally:
                    os.rename(gone + '.away', gone)
                self.assertIn('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:', str(code))
                self.assertIn(f'{name} ({gone}) is missing', str(code))
                self.assertIn(f'it would be refused: {name} ({gone}) is missing', dry[1])
                self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')), 'nothing was run')

    def test_a_moved_checkout_cannot_resume_a_run_and_the_message_says_so(self):
        d = self.register()
        moved = self.repo + '-moved'
        os.rename(self.repo, moved)
        d2 = moved + d[len(self.repo):]
        code, out, err = self.cli('--dir', d2, deck=False)
        self.assertIn('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:', str(code))
        self.assertIn(f'the repository this run was registered in ({self.repo}) is not there: the run records the path of its checkout, so a moved or renamed checkout '
                      'cannot resume it (put the checkout back at that path, or link it there)', str(code))
        self.assertFalse(os.path.exists(os.path.join(d2, 'fake_calls.jsonl')))
        code, out, err = self.cli('--dir', d2, '--dry-run', deck=False)
        self.assertEqual(code, 0)
        self.assertIn(f'it would be refused: the repository this run was registered in ({self.repo}) is not there', out)

    def test_a_moved_checkout_is_one_problem_not_a_list_of_every_file_missing(self):
        d = self.register()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual(sr.verify_inputs(man), [])
        man['repo_root'] = os.path.join(self.tmp, 'not-there')
        problems = sr.verify_inputs(man)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(f"({man['repo_root']}) is not there", problems[0])
        man['program_sha256'] = '0' * 64
        self.assertEqual(len(sr.verify_inputs(man)), 2, 'a changed program is reported as well')

    def test_a_program_that_failed_without_leaving_any_output_still_gets_its_exit_code_reported(self):
        d = self.register()

        class Failed:
            pid = 2 ** 22 + 1  # the wrapper notes its process group in the lock file after every start, so a started program has a pid (this one is no real process)
            returncode = 3

            def poll(self):
                return 3
        code, out, err = self.cli('--dir', d, deck=False, spawn=lambda cmd, env, logfile: Failed())
        self.assertIn('the program stopped with exit code 3; the end of its output', str(code))
        self.assertFalse(os.path.exists(os.path.join(d, 'run_output.log')))

    def test_the_end_of_a_log_is_read_whatever_state_the_file_is_in(self):
        path = os.path.join(self.tmp, 'out.log')
        self.assertEqual(sr.tail_text(path), '', 'no file')
        write(path, '')
        self.assertEqual(sr.tail_text(path), '')
        write(path, '  short log  \n')
        self.assertEqual(sr.tail_text(path), 'short log')
        write(path, 'x' * 1000 + 'THE END\n')
        self.assertEqual(sr.tail_text(path), 'x' * 392 + 'THE END', 'the last 400 bytes')
        self.assertEqual(sr.tail_text(path, 5), 'END', 'the last 5 bytes are " END" and a newline')
        with open(path, 'wb') as f:
            f.write(chr(0xE9).encode() * 300)  # an accented letter, two bytes each
        tail = sr.tail_text(path, 401)  # starts in the middle of a character
        self.assertTrue(tail.endswith(chr(0xE9) * 200), tail[:5])


class SeedPickerRefusals(T.Timed):
    HEAD = '00000001' + '0' * 56

    def folder(self, root, name, manifest):
        os.makedirs(os.path.join(root, name))
        with open(os.path.join(root, name, 'manifest.json'), 'wb') as f:
            f.write(manifest if isinstance(manifest, bytes) else manifest.encode())

    def test_folders_that_cannot_be_read_as_a_registered_run_are_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            alone = sr.pick_seed_base(self.HEAD, t, BLOCK, STEP)
            odd = ['{not json', '', b'\xff\xfe\x00{', '{"seed_base": "x"}', '{"seed_base": 1.5}', '{"seed_base": true}', '{"other": 1}',
                   json.dumps({'seed_base': BLOCK[1] + 5}), json.dumps({'seed_base': BLOCK[0] - 1})]
            for n, content in enumerate(odd):
                self.folder(t, f'run{n}', content)
            os.makedirs(os.path.join(t, 'no-manifest-here'))
            write(os.path.join(t, 'a-file-not-a-folder'), 'x')
            self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP), alone)
            self.folder(t, 'taken', json.dumps({'seed_base': alone}))
            self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP), alone + STEP, 'the readable one still counts')
            if os.geteuid() != 0:
                self.folder(t, 'locked', json.dumps({'seed_base': alone + STEP}))
                os.chmod(os.path.join(t, 'locked', 'manifest.json'), 0)
                self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP), alone + STEP, 'a manifest nobody here may read is ignored too')

    def test_a_manifest_that_is_valid_json_but_not_an_object_is_ignored_and_never_crashes(self):
        with tempfile.TemporaryDirectory() as t:
            alone = sr.pick_seed_base(self.HEAD, t, BLOCK, STEP)
            for n, content in enumerate(['[]', 'null', '7', '1.5', '"text"', 'true', json.dumps([{'seed_base': alone}]), json.dumps([alone]), json.dumps(alone)]):
                self.folder(t, f'run{n}', content)
            self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP), alone, 'none of them takes a slot, not even a list that holds a seed_base')
            self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP, explicit=alone), alone, 'and an explicit base on that slot is free')
            self.folder(t, 'taken', json.dumps({'seed_base': alone}))
            self.assertEqual(sr.pick_seed_base(self.HEAD, t, BLOCK, STEP), alone + STEP, 'an object next to them still counts')

    def test_with_every_slot_in_use_it_refuses_and_with_one_free_it_finds_that_one(self):
        lo, step = 1000, 10
        block = (lo, lo + 3 * step - 1)
        for head in ('00000000', '00000001', '00000002', '00000003', 'ffffffff'):
            for free in range(3):
                with self.subTest(head=head, free=free), tempfile.TemporaryDirectory() as t:
                    for k in range(3):
                        if k != free:
                            self.folder(t, f'run{k}', json.dumps({'seed_base': lo + k * step}))
                    self.assertEqual(sr.pick_seed_base(head + '0' * 56, t, block, step), lo + free * step)
            with self.subTest(head=head, free='none'), tempfile.TemporaryDirectory() as t:
                for k in range(3):
                    self.folder(t, f'run{k}', json.dumps({'seed_base': lo + k * step + 3}))  # anywhere inside a slot takes it
                with self.assertRaises(SystemExit) as cm:
                    sr.pick_seed_base(head + '0' * 56, t, block, step)
                self.assertEqual(cm.exception.code, 'REFUSED: every seed slot in 1000-1029 is already used by a slow report')

    def test_an_explicit_seed_base_on_a_slot_in_use_is_refused_naming_the_run_that_has_it(self):
        with tempfile.TemporaryDirectory() as t:
            mine = BLOCK[0] + 5 * STEP
            self.folder(t, '2026-10-09_older', json.dumps({'seed_base': mine}))
            with self.assertRaises(SystemExit) as cm:
                sr.pick_seed_base('ab' * 32, t, BLOCK, STEP, explicit=mine)
            self.assertEqual(cm.exception.code, f'REFUSED: --seed-base {mine} is a seed slot that is already used (2026-10-09_older); two reports would play the same deals')
            self.assertEqual(sr.pick_seed_base('ab' * 32, t, BLOCK, STEP, explicit=mine + STEP), mine + STEP, 'the next slot is free')


class ExplicitSeedBaseOnTheCommandLine(T.World):
    def test_a_slot_that_another_report_holds_is_refused_and_nothing_is_written(self):
        slot = BLOCK[0] + 7 * STEP
        first = self.register('--seed-base', str(slot))
        before = sorted(os.listdir(self.out_root))
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-11', '--seed-base', str(slot), date=False)
        self.assertIn(f'REFUSED: --seed-base {slot} is a seed slot that is already used ({os.path.basename(first)}); two reports would play the same deals', str(code))
        self.assertEqual(sorted(os.listdir(self.out_root)), before)
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-11', '--seed-base', str(slot + STEP), date=False)
        self.assertEqual(code, 0, err + out)


# ---------------------------------------------------------------------------------------------------------- the deck validator and the git state
class DeckValidatorAndGitState(T.World):
    def test_a_deck_line_that_cannot_be_read_is_an_error_not_a_pass(self):
        path = os.path.join(self.tmp, 'bad.txt')
        for label, data in (('a name where the count belongs', b'Energy: Fire\nTorchic B1 033\n'), ('bytes that are not text', b'Energy: Fire\n\xff\xfe 2 Torchic B1 033\n'),
                            ('a count that is not a number', b'Energy: Fire\ntwo Torchic B1 033\n')):
            with self.subTest(label):
                with open(path, 'wb') as f:
                    f.write(data)
                errs = sr.default_deck_check(path, T.ROOT)
                self.assertEqual(len(errs), 1, errs)
                self.assertTrue(errs[0].startswith(f'{path} could not be read as a deck: '), errs)
        errs = sr.default_deck_check(os.path.join(self.tmp, 'missing.txt'), T.ROOT)
        self.assertEqual(len(errs), 1)
        self.assertIn('could not be read as a deck', errs[0])

    def test_the_wrapper_refuses_a_deck_with_a_line_it_cannot_read_and_writes_nothing(self):
        write(self.deck, 'Energy: Fire\nTorchic B1 033\n')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                sr.main([self.deck, '--repo', T.ROOT, '--pin', self.pin_path, '--out-root', self.out_root, '--date', '2026-10-10', '--school-rule', 'off'],
                        now=self.clock.now, sleep=self.clock.sleep)
        self.assertIn('REFUSED: the deck is not a valid 20-card list:', str(cm.exception.code))
        self.assertIn('could not be read as a deck', str(cm.exception.code))
        self.assertFalse(os.path.exists(self.out_root))

    def git(self, repo, *a):
        subprocess.run(['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', *a], check=True, capture_output=True)

    def test_a_deck_file_is_committed_only_when_it_is_tracked_and_unchanged(self):
        repo = os.path.join(self.tmp, 'r')
        write(os.path.join(repo, 'a.txt'), 'x\n')
        self.git(repo, 'init', '-q')
        self.git(repo, 'add', 'a.txt')
        self.git(repo, 'commit', '-q', '-m', 'first')
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'committed')
        write(os.path.join(repo, 'b.txt'), 'new\n')
        self.assertEqual(sr.deck_state(repo, 'b.txt'), 'not committed', 'a file git has never seen, in a repository that has history')
        self.git(repo, 'add', 'b.txt')
        self.assertEqual(sr.deck_state(repo, 'b.txt'), 'not committed', 'staged is not committed')
        self.git(repo, 'commit', '-q', '-m', 'second')
        self.assertEqual(sr.deck_state(repo, 'b.txt'), 'committed')
        write(os.path.join(repo, 'a.txt'), 'y\n')
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'not committed', 'changed since the commit')
        self.assertEqual(sr.deck_state(repo, 'b.txt'), 'committed', 'one file changing does not change another')
        self.assertEqual(sr.deck_state(repo, 'no-such-file.txt'), 'not committed')

    def committed_repo(self, name='r'):
        repo = os.path.join(self.tmp, name)
        write(os.path.join(repo, 'decks', 'events', 'a.txt'), 'x\n')
        write(os.path.join(repo, 'decks', 'events', 'two words.txt'), 'y\n')
        write(os.path.join(repo, 'decks', 'events', 'other.txt'), 'z\n')
        self.git(repo, 'init', '-q')
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-q', '-m', 'first')
        return repo

    @staticmethod
    def index_of(repo):
        path = os.path.join(repo, '.git', 'index')
        with open(path, 'rb') as f:
            return f.read(), os.stat(path).st_mtime_ns

    def test_asking_never_rewrites_the_git_index_whatever_state_the_file_is_in(self):
        """`git diff` and `git status` refresh .git/index when a file's time changed, which a dry run must not do to somebody's repository."""
        repo = self.committed_repo()
        rel = 'decks/events/a.txt'
        path = os.path.join(repo, *rel.split('/'))
        later = time.time() + 100
        os.utime(path, (later, later))  # the same content with a newer time: git's cached file information is out of date now
        for label, want, change in (('touched only', 'committed', lambda: None),
                                    ('modified', 'not committed', lambda: write(path, 'changed\n')),
                                    ('deleted', 'not committed', lambda: os.remove(path)),
                                    ('untracked', 'not committed', lambda: write(os.path.join(repo, 'decks', 'events', 'new.txt'), 'n\n')),
                                    ('staged but not committed', 'not committed', lambda: (write(os.path.join(repo, 'decks', 'events', 'staged.txt'), 's\n'),
                                                                                         self.git(repo, 'add', 'decks/events/staged.txt')))):
            with self.subTest(label):
                change()
                target = {'untracked': 'decks/events/new.txt', 'staged but not committed': 'decks/events/staged.txt'}.get(label, rel)
                before = self.index_of(repo)
                self.assertEqual(sr.deck_state(repo, target), want)
                self.assertEqual(self.index_of(repo), before, 'the index is byte for byte what it was, and was not even written again')

    def test_a_repository_with_no_commit_yet_and_a_path_with_a_space_are_answered_too(self):
        empty = os.path.join(self.tmp, 'no-commits')
        write(os.path.join(empty, 'a.txt'), 'x\n')
        self.git(empty, 'init', '-q')
        self.assertEqual(sr.deck_state(empty, 'a.txt'), 'not committed', 'untracked')
        self.git(empty, 'add', 'a.txt')
        self.assertEqual(sr.deck_state(empty, 'a.txt'), 'not committed', 'in the index, but there is no commit to be in')
        repo = self.committed_repo()
        rel = 'decks/events/two words.txt'
        self.assertEqual(sr.deck_state(repo, rel), 'committed')
        write(os.path.join(repo, *rel.split('/')), 'changed\n')
        self.assertEqual(sr.deck_state(repo, rel), 'not committed')
        self.assertEqual(sr.deck_state(repo, 'decks/events/other.txt'), 'committed', 'the neighbour is still as committed')

    def test_a_folder_that_is_not_a_repository_and_a_machine_without_git_are_both_unknown(self):
        plain = os.path.join(self.tmp, 'plain')
        write(os.path.join(plain, 'a.txt'), 'x\n')
        self.assertEqual(sr.deck_state(plain, 'a.txt'), 'unknown (not a git repository)')
        nowhere = os.path.join(self.tmp, 'empty-path')
        os.makedirs(nowhere)
        with mock.patch.dict(os.environ, {'PATH': nowhere}):
            self.assertEqual(sr.deck_state(plain, 'a.txt'), 'unknown (git not available)')

    # ------------------------------------------------------------------------------------------------ the repository we were told about, whatever a git hook exported
    def other_repo(self, content):
        """Another repository holding decks/events/a.txt with `content`, committed: the one a git hook or `rebase --exec` leaves exported in GIT_DIR."""
        other = os.path.join(self.tmp, 'other')
        write(os.path.join(other, 'decks', 'events', 'a.txt'), content)
        self.git(other, 'init', '-q')
        self.git(other, 'add', '.')
        self.git(other, 'commit', '-q', '-m', 'other')
        return other

    def test_a_deck_committed_in_the_repository_given_is_committed_whatever_a_git_hook_exported(self):
        repo = self.committed_repo()
        rel = 'decks/events/a.txt'
        every = T.exported_git_variables(self.tmp, self.other_repo('something else\n'))
        self.assertEqual(set(every), set(T.GIT_REPO_VARS), 'every one of the variables is exported in turn')
        self.assertEqual(sr.deck_state(repo, rel), 'committed')
        for name, value in every.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(sr.deck_state(repo, rel), 'committed')
                self.assertEqual(sr.deck_state(repo, 'decks/events/two words.txt'), 'committed')
        with mock.patch.dict(os.environ, every):
            self.assertEqual(sr.deck_state(repo, rel), 'committed', 'all of them at once')

    def test_a_deck_that_is_committed_only_in_the_repository_a_hook_exported_is_not_committed_in_the_one_given(self):
        """The dangerous direction: the deck file here was edited after the commit, the exported repository has it exactly as edited."""
        repo = self.committed_repo()
        rel = 'decks/events/a.txt'
        write(os.path.join(repo, *rel.split('/')), 'edited since\n')
        every = T.exported_git_variables(self.tmp, self.other_repo('edited since\n'))
        self.assertEqual(sr.deck_state(repo, rel), 'not committed')
        for name, value in every.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(sr.deck_state(repo, rel), 'not committed')
        with mock.patch.dict(os.environ, every):
            self.assertEqual(sr.deck_state(repo, rel), 'not committed')
            plain = os.path.join(self.tmp, 'not-a-repository')
            write(os.path.join(plain, 'a.txt'), 'x\n')
            self.assertEqual(sr.deck_state(plain, 'a.txt'), 'unknown (not a git repository)', 'a folder that is no repository is not the exported one either')

    def test_every_git_call_for_a_deck_is_made_with_git_env_whatever_the_process_has_exported(self):
        repo = self.committed_repo()
        stub, calls = T.recording_git(self.tmp)
        every = T.exported_git_variables(self.tmp, self.other_repo('x\n'))
        with mock.patch.dict(os.environ, dict(stub, **every, GIT_OPTIONAL_LOCKS='1', GIT_AUTHOR_NAME='someone')):
            self.assertEqual(sr.deck_state(repo, 'decks/events/a.txt'), 'committed', 'a git that answers the same everywhere')
        made = calls()
        self.assertEqual([args.split()[2] for args, env in made], ['rev-parse', 'ls-files', 'rev-parse', 'hash-object'])
        for args, env in made:
            for name in T.GIT_REPO_VARS:
                self.assertNotIn(name, env, (args, name))
            self.assertEqual((env['GIT_OPTIONAL_LOCKS'], env['GIT_AUTHOR_NAME']), ('0', 'someone'), args)


# ---------------------------------------------------------------------------------------------------------- the resume command
class ResumeCommandIsQuoted(T.World):
    def setUp(self):
        super().setUp()
        self.out_root = os.path.join(self.tmp, 'results with a space')

    def command_in(self, text):
        line = [l for l in text.splitlines() if '(resume with: ' in l][0]
        return shlex.split(line.split('(resume with: ', 1)[1].rstrip(')'))

    def test_the_command_recorded_at_registration_works_in_a_shell_for_a_folder_with_a_space(self):
        d = self.register(school=None)
        self.assertIn(' ', d)
        cmd = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command']
        self.assertEqual(cmd, f"python3 rl/strength/slow_report.py --dir {shlex.quote(d)}")
        self.assertEqual(shlex.split(cmd), ['python3', 'rl/strength/slow_report.py', '--dir', d])
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False, school=None)
        self.assertEqual(code, 0)
        self.assertEqual(self.command_in(out), ['python3', 'rl/strength/slow_report.py', '--dir', d])

    def test_the_school_choice_the_command_carries_is_quoted_for_the_shell_too(self):
        d = self.register('--school-days', 'mon, tue', school='on')  # (the spaces are allowed in the list)
        cmd = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command']
        self.assertEqual(cmd, f"python3 rl/strength/slow_report.py --dir {shlex.quote(d)} --school-days 'mon, tue'")
        self.assertEqual(shlex.split(cmd), ['python3', 'rl/strength/slow_report.py', '--dir', d, '--school-days', 'mon, tue'])
        self.make()
        self.out_root = os.path.join(self.tmp, 'results with a space')
        d = self.register(school='off')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False, school=None)
        self.assertEqual(self.command_in(out), ['python3', 'rl/strength/slow_report.py', '--dir', d, '--school-rule', 'off'])

    def test_the_message_that_a_run_was_cut_by_max_games_quotes_the_folder_for_the_shell(self):
        code, out, err = self.cli('--deals', '1', '--max-games', '2', school=None)
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        self.assertIn(' ', d)
        line = [l for l in out.splitlines() if 'stopped after --max-games' in l]
        self.assertEqual(line, [f'{T.HEADLINE_START}my-list v km3 on the public panel] stopped after --max-games 2 (games across both arms, about half of them kx3 games); '
                                f'resume with: python3 rl/strength/slow_report.py --dir {shlex.quote(d)}'])
        self.assertTrue(shlex.quote(d).startswith("'"), 'the path really needed quoting')
        self.assertEqual(shlex.split(line[0].split('resume with: ', 1)[1]), ['python3', 'rl/strength/slow_report.py', '--dir', d], 'a shell reads it back as the one folder')

    def test_the_refusal_to_register_over_an_existing_run_quotes_the_folder_for_the_shell(self):
        d = self.register()
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, f'{T.HEADLINE_START}my-list v km3 on the public panel] REFUSED: the run directory {d} already exists; '
                               f'resume it with --dir {shlex.quote(d)} (or pick another --date)')
        self.assertTrue(shlex.quote(d).startswith("'"), 'the path really needed quoting')
        self.assertEqual(shlex.split(str(code).split('resume it with --dir ', 1)[1].split(' (or pick', 1)[0]), [d], 'a shell reads it back as the one folder')

    def test_a_folder_that_needs_no_quoting_is_printed_as_it_is(self):
        self.out_root = os.path.join(self.tmp, 'results')
        d = self.register()
        self.assertEqual(shlex.quote(d), d)
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertTrue(str(code).endswith(f'already exists; resume it with --dir {d} (or pick another --date)'), code)

    def test_a_run_registered_without_a_recorded_command_is_given_a_quoted_one(self):
        d = self.register(school=None)
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        del man['slow_report']['resume_command']
        T.rewrite_manifest(d, man)
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False, school=None)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.command_in(out), ['python3', 'rl/strength/slow_report.py', '--dir', d])


# ---------------------------------------------------------------------------------------------------------- the engineering report reads past a torn last line
class TornLastLines(unittest.TestCase):
    def test_a_torn_last_line_of_the_games_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            TR.make_run(d, 'match')
            self.assertEqual(TR.run_report(d).returncode, 0)
            clean = json.loads(TR.read(os.path.join(d, 'report.json')))
            with open(os.path.join(d, 'games.jsonl'), 'a', encoding='utf-8') as f:
                f.write('{"key": "d1|o1|1|0|X", "deck": "d1", "opp": "o1", "dea')  # a game cut off by the 6:30 stop
            r = TR.run_report(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('Traceback', r.stderr)
            self.assertEqual(json.loads(TR.read(os.path.join(d, 'report.json'))), clean, 'the same numbers as without the torn line')
            self.assertEqual(clean['paired_games'], 1)

    def test_a_torn_last_line_of_the_errors_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            TR.make_run(d, 'match')
            err = json.dumps(dict(key='d1|o1|1|0|X', error='boom', at='2026-10-03T12:30:00Z')) + '\n'
            TR.write(os.path.join(d, 'errors.jsonl'), err + '{"key": "d1|o1|2|0|X", "error": "bo')
            r = TR.run_report(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('Traceback', r.stderr)
            text = TR.read(os.path.join(d, 'REPORT.md'))
            self.assertIn('1 game failed', text)
            self.assertIn('d1|o1|1|0|X', text)
            self.assertNotIn('d1|o1|2|0|X', text)


# ---------------------------------------------------------------------------------------------------------- the log of a run after a line that was cut off
class LogAfterATornLine(T.Timed):
    """log_event appends one JSON line to slow_report_log.jsonl. A last line that lost its newline (a write cut short by a kill, a full disk) must not swallow the event that follows it: the
    torn line stays what it was, unreadable, and the new event is on a line of its own."""
    TORN = '{"at": "2026-10-10T10:00:00Z", "event": "slice_st'

    def setUp(self):
        super().setUp()
        self.old = dict(sr._LOG_EXTRA)
        sr._LOG_EXTRA.clear()
        sr._LOG_EXTRA.update(pilot='kx3', reference='km3')
        self.addCleanup(lambda: (sr._LOG_EXTRA.clear(), sr._LOG_EXTRA.update(self.old)))
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.path = os.path.join(self.dir, 'slow_report_log.jsonl')

    def raw(self):
        with open(self.path, 'rb') as f:
            return f.read().decode('utf-8')

    def put(self, text):
        with open(self.path, 'wb') as f:
            f.write(text.encode('utf-8'))

    GOOD = '{"at": "2026-10-10T09:00:00Z", "event": "registered"}\n'

    def test_an_event_after_a_torn_last_line_is_on_a_line_of_its_own_and_the_torn_line_is_left_as_it_was(self):
        self.put(self.GOOD + self.TORN)
        sr.log_event(self.dir, 'slice_end', returncode=0, new_games=3)
        lines = self.raw().split('\n')
        self.assertEqual(lines[:2], [self.GOOD.rstrip('\n'), self.TORN], 'the torn line is unchanged and has no more text on it')
        self.assertEqual(len(lines), 4, 'the good line, the torn line, the new event, and the end of the file')
        self.assertEqual(lines[3], '')
        event = json.loads(lines[2])
        self.assertEqual((event['event'], event['returncode'], event['new_games'], event['pilot'], event['reference']), ('slice_end', 0, 3, 'kx3', 'km3'))
        self.assertEqual([e['event'] for e in sr.load_jsonl(self.path)], ['registered', 'slice_end'], 'the torn line is skipped, the new event is read')
        self.assertEqual([e['event'] for e in T.jsonl(self.path)], ['registered', 'slice_end'])

    def test_a_last_line_that_is_whole_but_has_no_newline_is_not_joined_to_the_event_either(self):
        self.put(self.GOOD + '{"at": "2026-10-10T09:30:00Z", "event": "slice_start"}')
        sr.log_event(self.dir, 'slice_end')
        self.assertEqual([e['event'] for e in sr.load_jsonl(self.path)], ['registered', 'slice_start', 'slice_end'], 'a whole line is still read')
        self.assertEqual(len(self.raw().split('\n')), 4)

    def test_a_file_that_is_only_a_torn_line_gets_the_event_after_a_newline(self):
        self.put(self.TORN)
        sr.log_event(self.dir, 'registered')
        lines = self.raw().split('\n')
        self.assertEqual((lines[0], len(lines), lines[2]), (self.TORN, 3, ''))
        self.assertEqual(json.loads(lines[1])['event'], 'registered')

    def test_a_log_that_ends_with_a_newline_gets_no_blank_line(self):
        self.put(self.GOOD)
        sr.log_event(self.dir, 'slice_start')
        sr.log_event(self.dir, 'slice_end')
        lines = self.raw().split('\n')
        self.assertEqual(len(lines), 4, lines)
        self.assertEqual((lines[0] + '\n', lines[3]), (self.GOOD, ''))
        self.assertNotIn('\n\n', self.raw(), 'no blank line anywhere')
        self.assertEqual([json.loads(l)['event'] for l in lines[:3]], ['registered', 'slice_start', 'slice_end'])

    def test_an_empty_file_and_a_missing_file_get_the_event_as_the_first_line_with_nothing_before_it(self):
        self.put('')
        sr.log_event(self.dir, 'registered')
        self.assertTrue(self.raw().startswith('{'), repr(self.raw()[:20]))
        self.assertEqual(self.raw().count('\n'), 1)
        os.remove(self.path)
        sr.log_event(self.dir, 'registered')
        self.assertTrue(self.raw().startswith('{'), repr(self.raw()[:20]))
        self.assertEqual((self.raw().count('\n'), len(sr.load_jsonl(self.path))), (1, 1))

    def test_only_the_first_event_after_a_torn_line_needs_the_newline_the_next_ones_are_ordinary(self):
        self.put(self.TORN)
        for name in ('registered', 'sitting_call', 'slice_start'):
            sr.log_event(self.dir, name)
        lines = self.raw().split('\n')
        self.assertEqual((lines[0], len(lines)), (self.TORN, 5))
        self.assertEqual([json.loads(l)['event'] for l in lines[1:4]], ['registered', 'sitting_call', 'slice_start'])
        self.assertNotIn('\n\n', self.raw())


class LogAfterATornLineOnAResume(T.World):
    def test_a_torn_last_line_of_a_run_log_does_not_hide_the_events_the_next_call_logs(self):
        """End to end, through the command line: the torn line is what a kill in the middle of a write leaves; the resume that follows logs its events after it, and every one of them is read."""
        d = self.register()
        log = os.path.join(d, 'slow_report_log.jsonl')
        with open(log, 'a', encoding='utf-8') as f:
            f.write(LogAfterATornLine.TORN)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, out + err)
        self.assertEqual([e['event'] for e in T.jsonl(log) if e['event'] != 'env_scrubbed'], ['registered', 'sitting_call', 'slice_start', 'slice_end', 'complete', 'report_written'])
        self.assertEqual([l for l in T.read(log).splitlines() if 'slice_st' in l and not l.endswith('}')], [LogAfterATornLine.TORN], 'the torn line is still there, as it was, alone on its line')


if __name__ == '__main__':
    unittest.main()
