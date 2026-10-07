#!/usr/bin/env python3
"""The opt-in slow report: how does one deck do with the strong, slow pilot kx3?  (plan: rl/results/kx3_slow_report_plan_2026-10-06/PLAN.md)

  slow_report.py DECKFILE [--deals N] [--no-paired] [--threads T]    register, run and report on one deck
  slow_report.py --dir RUNDIR [--report-only | --dry-run]            resume a registered run, or just rewrite its page, or say where it stands

DECKFILE is a deck file inside the repository (`Energy: <Type>` and one `N Name SET NNN` line per card). The deck is played by kx3 against the 8
public panel lists played by km3, N deals (default 5) x 2 seats per opponent, so 16 x N kx3 games; the frozen program also plays km3 on the deck
on the same deals, about a second a game, and the page says "how much better kx3 plays this deck than km3" from them (`--no-paired` leaves that out). The run is pre-registered
(through strength_prereg.py, stage `use`) into rl/results/slow_reports/<date>_<deck>/ before any game, then run with checkpoint and resume, then
reported in SLOW_REPORT.md: the deck's score overall and against each list with 95% ranges, both pilots and the build, the time it took, and a plain
statement of what the numbers can and cannot say. There is no pass or fail line anywhere, and every line printed names both pilots.

What it keeps (the plan):
  * opt-in only: nothing here changes the screen, the floor or any default (those stay km3 and have their own cutoffs);
  * the exact tested version: the program must be the one in slow_report_pin.json (sha256 checked before a file is written, and again before every
    sitting, with the deck and panel files against the registration); a later version replaces it only by a new pin;
  * realistic knowledge: kx3 plays the deck knowing its own cards, it is never an opponent's guessing pool entry, and the panel side is never handed the
    deck, so every variable that adds lists to the pool or changes the rules (KX_*, PDL_*, DECKGYM_*, JEV_*, PG_*) is removed from the program's
    environment (the list registered with the run is the one used), and the log says which were removed;
  * the school-morning rule (rl/RUN5.md, Oct 4): on school days no new game after 5:15 am, a program still running at 6:30 am is stopped (the game it was
    in replays), and the run resumes from 5 pm; weekends are free. Committing and pushing the result is the runner's job: this script never touches git.

One wrapper per run directory (a kernel lock, flock, that the program inherits, so it holds even if the wrapper is killed outright while the program plays on);
a SIGTERM or SIGHUP stops the program before the wrapper exits, except a SIGHUP that was ignored at launch (`nohup`), which stays ignored. Pure standard
library; it calls strength_prereg.py, the pinned program and strength_report.py (for REPORT.md, the engineering numbers).
"""
import sys
sys.dont_write_bytecode = True  # a dry run must leave nothing behind in the repository
import argparse, datetime, fcntl, hashlib, importlib.util, json, math, os, re, shlex, shutil, signal, statistics, subprocess, time, zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import strength_report as R  # noqa: E402  (mean_ci, wilson, registration_problems, Z: the report's own arithmetic)
import strength_prereg as PRE  # noqa: E402  (deck_signature: what a deck file says, not how it was saved)

DEFAULT_PIN = os.path.join(HERE, 'slow_report_pin.json')
PREREG = os.path.join(HERE, 'strength_prereg.py')
REPORT = os.path.join(HERE, 'strength_report.py')
CHICAGO = zoneinfo.ZoneInfo('America/Chicago')
UTC = datetime.timezone.utc
SCHOOL_DAYS = (0, 1, 2, 3, 4)  # Monday to Friday (datetime.weekday)
SOFT_STOP, HARD_STOP, RESUME = (5, 15), (6, 30), (17, 0)
NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
DAY_NAMES = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
PAIR_STRIDE = 10_000
MAX_DEALS = PAIR_STRIDE - 1
SCORE = {'deck': 1.0, 'tie': 0.5, 'opp': 0.0}
WAIT_STEP_S = 60  # a school wait is taken in steps of this many seconds, so a laptop that slept does not oversleep by hours
MAX_CUTS_WITHOUT_PROGRESS = 3
_LOG_EXTRA = {}  # pilot and reference, added to every log event


def die(msg):
    raise SystemExit(msg)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(path):
    """The records of a JSON-lines file, skipping blank and torn lines (a game cut off at 6:30 can leave a half line)."""
    out = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict):
                    out.append(r)
    return out


def utc_iso(t=None):
    return (t or datetime.datetime.now(UTC)).astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def plural(n, word):
    return f'{n} {word}' + ('' if n == 1 else 's')


# ------------------------------------------------------------------------------------------------------------------ the pin
def load_pin(path):
    try:
        pin = load_json(path)
    except (OSError, ValueError) as e:
        die(f'cannot read the pin {path}: {e}')
    if not isinstance(pin, dict):
        die(f'the pin {path} is not a JSON object')
    for k in ('pilot', 'reference', 'pilot_label', 'reference_label', 'panel_label', 'panel_group', 'program', 'program_sha256', 'selfcheck', 'engine',
              'pilot_provenance', 'reference_provenance', 'seed_block', 'seed_step', 'games_per_hour', 'scrub_env_prefixes', 'threads'):
        if k not in pin:
            die(f'the pin {path} has no {k!r}')
    return pin


def check_program(pin):
    """Refuse (before anything is written) a program that is not the pinned build."""
    p = pin['program']
    if not os.path.isfile(p):
        die(f'REFUSED: the pinned program {p} does not exist, so no slow report can run. A different build needs a new pin (rl/strength/slow_report_pin.json), after its own gate.')
    actual = sha(p)
    if actual != pin['program_sha256']:
        die(f'REFUSED: {p} (sha256 {actual[:12]}) is not the pinned build (sha256 {pin["program_sha256"][:12]}). A slow report uses only the exact tested version; '
            'a later version replaces it by a new pin, after its own gate.')


# ------------------------------------------------------------------------------------------------------------------ the deck
def deck_name_of(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    if not NAME_RE.match(stem):
        die(f"REFUSED: the deck file name {stem!r} must use only letters, digits, '.', '_' and '-', and start with a letter or digit (it names the deck and the run folder)")
    return stem


def default_deck_check(deck_abs, root):
    """Error messages from the repository's own deck validator (lib/deck_check.py): 20 cards, at most 2 per name, every id known, a Basic."""
    lib = os.path.join(root, 'lib', 'deck_check.py')
    if not os.path.isfile(lib):
        return [f'lib/deck_check.py not found under {root}, so the deck cannot be validated (a check that silently skips is the failure it exists to prevent)']
    spec = importlib.util.spec_from_file_location('slow_report_deck_check', lib)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        energy, cards = mod.parse(deck_abs)
    except Exception as e:  # a malformed line
        return [f'{deck_abs} could not be read as a deck: {e}']
    errs = [] if energy else ['no `Energy: <Type>` line']
    errs += [m for s, m in mod.check(os.path.basename(deck_abs), cards) if s == 'ERROR']
    return errs


def deck_state(repo, rel):
    """Whether the deck file is committed as it is: 'committed', 'not committed', or 'unknown (...)'."""
    def git(*a):  # only commands that never write .git/index (git diff would refresh it): a dry run writes nothing
        return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    try:
        if git('rev-parse', '--is-inside-work-tree').returncode != 0:
            return 'unknown (not a git repository)'
        if git('ls-files', '--error-unmatch', '--', rel).returncode != 0:
            return 'not committed'
        head = git('rev-parse', '--verify', '-q', f'HEAD:./{rel}')  # ./ : relative to the folder given to -C, like the two calls around it (HEAD:<path> is from the work tree root)
        if head.returncode != 0:
            return 'not committed'  # in the index but not in the last commit
        now = git('hash-object', '--', rel)
        return 'committed' if now.returncode == 0 and now.stdout.strip() == head.stdout.strip() else 'not committed'
    except OSError:
        return 'unknown (git not available)'


def panel_signatures(repo, pin):
    """{signature: panel list name} for the public lists present in the repository (a missing file is left for strength_prereg.py to refuse)."""
    registry = load_json(os.path.join(HERE, 'decks.json'))['decks']
    out = {}
    for n in load_json(os.path.join(HERE, 'groups.json'))[pin['panel_group']]:
        try:
            out[PRE.deck_signature(os.path.join(repo, registry[n]))] = n
        except OSError:
            pass
    return out


# ------------------------------------------------------------------------------------------------------------------ seeds
def pick_seed_base(deck_sha, out_root, block, step, explicit=None):
    """A seed base from the registered block (24,601,000,000 - 24,699,999,999; the exam's seeds spill past its own block up to 24,600,070,002, so slot 0 starts
    above that): the deck's own slot, the next free one if another slow report took it. An explicit base must be the start of a slot inside the block."""
    lo, hi = block
    slots = (hi - lo + 1) // step
    used = {}  # slot -> the run folder that holds it
    if os.path.isdir(out_root):
        for n in sorted(os.listdir(out_root)):
            mp = os.path.join(out_root, n, 'manifest.json')
            if os.path.isfile(mp):
                try:
                    m = load_json(mp)
                except (OSError, ValueError):
                    continue
                b = m.get('seed_base') if isinstance(m, dict) else None
                if isinstance(b, int) and lo <= b <= hi:
                    used.setdefault((b - lo) // step, n)
    if explicit is not None:
        if not (lo <= explicit and explicit + step - 1 <= hi and (explicit - lo) % step == 0):
            die(f'REFUSED: --seed-base {explicit} is not the start of a seed slot inside the registered block {lo}-{hi} (slots are {step} wide: {lo} + k x {step})')
        if (explicit - lo) // step in used:
            die(f'REFUSED: --seed-base {explicit} is the seed slot of {used[(explicit - lo) // step]} in {out_root}; two reports would play the same deals')
        return explicit
    start = int(deck_sha[:8], 16) % slots
    for k in range(slots):
        s = (start + k) % slots
        if s not in used:
            return lo + s * step
    die(f'REFUSED: every seed slot in {lo}-{hi} is already used by a slow report')


# ------------------------------------------------------------------------------------------------------------------ the school-morning rule
def school_action(now, school_days=SCHOOL_DAYS, soft=SOFT_STOP, hard=HARD_STOP, resume=RESUME):
    """What the runner may do at `now` (an aware datetime; read as Chicago time):
    {'kind': 'wait', 'until': dt}  on a school day from the soft stop to the resume time;
    {'kind': 'run', 'stop_after_min': minutes, 'hard_stop': dt}  otherwise: stop starting games at the next school morning's 5:15, kill at its 6:30
    (real minutes, so a clock change is counted); with no school days there is no limit."""
    if not school_days:
        return {'kind': 'run', 'stop_after_min': None, 'hard_stop': None}
    local = now.astimezone(CHICAGO)

    def at(d, hm):
        return datetime.datetime(d.year, d.month, d.day, hm[0], hm[1], tzinfo=CHICAGO)

    today = local.date()
    if local.weekday() in school_days and at(today, soft) <= local < at(today, resume):
        return {'kind': 'wait', 'until': at(today, resume)}
    d = today
    for _ in range(9):
        if d.weekday() in school_days and at(d, soft) > local:
            return {'kind': 'run', 'stop_after_min': (at(d, soft).astimezone(UTC) - local.astimezone(UTC)).total_seconds() / 60, 'hard_stop': at(d, hard)}
        d += datetime.timedelta(days=1)
    return {'kind': 'run', 'stop_after_min': None, 'hard_stop': None}


def parse_days(s):
    out = []
    for p in [x.strip().lower() for x in s.split(',') if x.strip()]:
        if p not in DAY_NAMES:
            die(f'unknown day {p!r} in --school-days (use mon,tue,wed,thu,fri,sat,sun)')
        out.append(DAY_NAMES.index(p))
    return tuple(out)


def wait_until(until, now, sleep, step=WAIT_STEP_S):
    """Sleep until `until`, in steps, re-reading the clock each time (a suspended laptop wakes up late by at most a step)."""
    while True:
        remaining = (until.astimezone(UTC) - now().astimezone(UTC)).total_seconds()
        if remaining <= 0:
            return
        sleep(min(step, remaining))


# ------------------------------------------------------------------------------------------------------------------ the program's process
def scrub_env(env, prefixes):
    """The environment without the variables that would tune the pilot or change the rules, and the sorted names removed. `env` is not modified."""
    removed = sorted(k for k in env if any(k.startswith(p) for p in prefixes))
    return {k: v for k, v in env.items() if k not in removed}, removed


def nice_prefix(which=shutil.which):
    p = which('nice')
    return [p, '-n', '19'] if p else []


_LOCK_FDS = []   # the run lock's file descriptor while this wrapper holds it: the program inherits it, so the lock outlives a wrapper killed with SIGKILL
_LOCK_PATHS = {}  # fd -> the lock file's path (to record the program's process group in it)
_PROGRAMS = []   # programs this wrapper started: the lock file is not removed while one of them is still alive


def default_spawn(cmd, env, logfile):
    fh = open(logfile, 'ab')
    proc = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=fh, stderr=fh, start_new_session=True, pass_fds=tuple(_LOCK_FDS))
    proc._logfh = fh
    return proc


def stop_group(proc, grace_s=30):
    """SIGTERM the program's whole process group (it leads its own: start_new_session), SIGKILL it after `grace_s`. A program that has ended is left alone, and a
    process that does not lead its own group (never this wrapper's group) is signalled on its own."""
    if proc.poll() is not None:
        return
    try:
        pgid = os.getpgid(proc.pid)
    except (ProcessLookupError, PermissionError):
        return

    def send(sig):
        try:
            if pgid == os.getpgrp():
                proc.send_signal(sig)
            else:
                os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            pass
    send(signal.SIGTERM)
    try:
        proc.wait(timeout=grace_s)
    except subprocess.TimeoutExpired:
        send(signal.SIGKILL)
        proc.wait()


def tail_text(path, n=400):
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - n))
            return f.read().decode('utf-8', 'replace').strip()
    except OSError:
        return ''


def read_lock_info(path):
    """{'pid', 'started'} written by the wrapper that holds the lock, or {} (a lock file is only a note; the flock is the lock)."""
    try:
        with open(path, encoding='utf-8') as f:
            info = json.load(f)
        return info if isinstance(info, dict) else {}
    except (OSError, ValueError):
        return {}


def acquire_lock(rundir, say):
    """One wrapper per run directory: two would play the same games twice. The lock is a kernel flock on slow_report.lock, held until release_lock and inherited by
    the program (default_spawn), so nothing needs to be judged stale: the kernel frees it when the last holder is gone, even after a SIGKILL. Returns the open file
    descriptor, whose file says who holds it (for the refusal message only)."""
    path = os.path.join(rundir, 'slow_report.lock')
    for _ in range(5):
        try:
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
        except OSError as e:
            die(f'REFUSED: cannot open the lock file {path} ({e.strerror or e}); if no other slow_report.py is running on this folder, remove it')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            info = read_lock_info(path)
            os.close(fd)
            pg = info.get('program_pgid')
            die(f'REFUSED: another slow_report.py (pid {info.get("pid", "unknown")}, started {info.get("started", "unknown")}) or the program it started is already running {rundir}; '
                'two wrappers on one run would play the same games twice. If its wrapper was killed, the program plays on until its sitting ends or you stop it'
                + (f' (kill -TERM -{pg}).' if isinstance(pg, int) else '.'))
        except OSError as e:
            os.close(fd)
            die(f'REFUSED: cannot lock {path} ({e.strerror or e}); this file system may not support flock')
        try:  # a holder that finished may have removed the file between our open and our lock: the lock on a deleted file is no lock
            if os.fstat(fd).st_ino == os.stat(path).st_ino:
                break
        except FileNotFoundError:
            pass
        os.close(fd)
    else:
        die(f'REFUSED: could not take the lock {path}')
    if fd < 3:  # descriptors 0-2 are the program's stdin, stdout and stderr, which Popen replaces, so a lock held there would not reach it
        moved = fcntl.fcntl(fd, fcntl.F_DUPFD, 3)  # the same open file description, so the same lock
        os.close(fd)
        fd = moved
    os.ftruncate(fd, 0)
    os.pwrite(fd, json.dumps({'pid': os.getpid(), 'started': utc_iso()}).encode('utf-8'), 0)
    _LOCK_FDS.append(fd)
    _LOCK_PATHS[fd] = path
    return fd, path


def note_program(proc):
    """Record the program's process group in the lock note, so a refusal can say which group to stop if the wrapper was killed. `None` (the program has ended)
    removes it: the number could be reused by an unrelated process by the next sitting."""
    pid = getattr(proc, 'pid', None)
    for fd in _LOCK_FDS:
        path = _LOCK_PATHS.get(fd)
        try:
            info = read_lock_info(path)
            if isinstance(pid, int):
                info['program_pgid'] = pid
            else:
                info.pop('program_pgid', None)
            os.ftruncate(fd, 0)
            os.pwrite(fd, json.dumps(info).encode('utf-8'), 0)
        except (OSError, TypeError):
            pass


def release_lock(lock):
    """Give the lock up. The file is removed (while we still hold the flock, so nobody locks the deleted file) unless a program this wrapper started is still
    alive: it keeps the lock through the descriptor it inherited, and the file stays so the next wrapper is refused until it ends."""
    fd, path = lock
    _PROGRAMS[:] = [p for p in _PROGRAMS if getattr(p, 'poll', lambda: 0)() is None]
    try:
        if not _PROGRAMS:
            os.remove(path)
    except OSError:
        pass
    if fd in _LOCK_FDS:
        _LOCK_FDS.remove(fd)
    _LOCK_PATHS.pop(fd, None)
    try:
        os.close(fd)
    except OSError:
        pass


class signals_stop_the_program:
    """SIGTERM and SIGHUP raise SystemExit, so the run loop's cleanup stops the program (and the lock is released) instead of orphaning it. A SIGHUP that was
    ignored when the wrapper started (`nohup`) stays ignored: the launcher asked for the run to outlive its terminal."""

    def __enter__(self):
        self.old = {}
        for sig in (signal.SIGTERM, signal.SIGHUP):
            try:
                if sig == signal.SIGHUP and signal.getsignal(sig) == signal.SIG_IGN:
                    continue
                self.old[sig] = signal.signal(sig, self.handler)
            except ValueError:  # not the main thread
                pass

    @staticmethod
    def handler(signum, frame):
        raise SystemExit(128 + signum)

    def __exit__(self, *a):
        for sig, h in self.old.items():
            signal.signal(sig, h)


# ------------------------------------------------------------------------------------------------------------------ the plan
def expected_time(deals, pin):
    g = 16 * deals
    r = pin['games_per_hour']
    return dict(kx3_games=g, typical_hours=(g / r['typical_high'], g / r['typical_low']), wall_hours=g / r['wall'])


def hours_text(h):
    return f'{h:.1f} hours' if h >= 1.95 else f'{round(h * 60)} minutes'


def headline_of(pin, deck_name):
    return f"{pin['pilot_label']} on {deck_name} v {pin['reference_label']} on {pin['panel_label']}"


def build_config(*, pin, pin_path, deck_rel, deck_name, deck_sha, deck_state, deals, paired, seed_base, threads, program_sha, selfcheck_given='pin', selfcheck_how='pin',
                 resume_command=None):
    headline = headline_of(pin, deck_name)
    et = expected_time(deals, pin)
    pilot, ref = pin['pilot'], pin['reference']
    baseline = (f'and how much better {pilot} plays this deck than {ref} on the same deals' if paired else
                f'without the comparison with {ref} on the same deals (--no-paired: the {ref} games are still played, about a second each, and left out of the page)')
    cfg = dict(
        name=f'slow_report_{deck_name}',
        question=(f'{headline}. A slow report on one deck, not development: how does {deck_name} do when the strong, slow pilot {pilot} plays it against the eight public panel '
                  f'lists played by {ref}, {plural(deals, "deal")} x 2 seats each? Primary: the deck\'s score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; '
                  f'{baseline}. Realistic knowledge: {pilot} plays the deck knowing its own cards; '
                  f'the deck is never one of the lists {pilot} guesses its opponent from, and the panel side is never handed it. '
                  f'No pass or fail line; time per game is reported as a fact.'),
        pilot=pilot, reference=ref, stage='use',
        deck_files=[deck_rel], opponent_groups=[pin['panel_group']], deals=deals, seats=[0, 1], seed_base=seed_base, pair_stride=PAIR_STRIDE, threads=threads, log_level='deck',
        program=pin['program'], program_sha256=program_sha, engine=pin['engine'], pilot_provenance=pin['pilot_provenance'], reference_provenance=pin['reference_provenance'],
        slow_report=dict(version=1, headline=headline, summary=f'Stage use. {plural(deals, "deal")} x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.',
                         deck_name=deck_name, deck_file=deck_rel, deck_file_sha256=deck_sha, deck_file_state=deck_state, deals=deals, paired=bool(paired),
                         pin=dict(path=os.path.relpath(pin_path, ROOT).replace(os.sep, '/') if os.path.abspath(pin_path).startswith(ROOT + os.sep) else pin_path, sha256=sha(pin_path)),
                         pilot_label=pin['pilot_label'], reference_label=pin['reference_label'], panel_label=pin['panel_label'],
                         scrub_env_prefixes=list(pin['scrub_env_prefixes']), resume_command=resume_command,
                         expected_hours=dict(typical_low=et['typical_hours'][0], typical_high=et['typical_hours'][1], wall=et['wall_hours'])),
    )
    if selfcheck_given == 'pin':
        cfg['selfcheck_given'] = dict(pin['selfcheck'])
    elif selfcheck_given:
        cfg['selfcheck_given'] = dict(selfcheck_given)
        cfg['selfcheck_how'] = selfcheck_how
    return cfg


def run_prereg(cfg_path, rundir, repo):
    return subprocess.run([sys.executable, '-B', PREREG, '--config', cfg_path, '--out', rundir, '--repo', repo], capture_output=True, text=True)


def run_selfcheck(pin, repo, spec, say, deadline=None, now=None):
    """Replay the 12 fixed self-check games on the pinned program (scrubbed environment, low priority) and refuse on any difference from the pin. The program
    runs in its own process group, which is stopped if this wrapper is interrupted or if `deadline` (the school-morning 6:30 cut) comes first."""
    reg = load_json(os.path.join(HERE, 'decks.json'))['decks']
    env, _ = scrub_env(dict(os.environ), pin['scrub_env_prefixes'])
    say(f'self-check of {spec}: 12 fixed games on the pinned program (this takes a while for kx3; run it when the laptop is free)')
    cmd = nice_prefix() + [pin['program'], 'selfcheck', '--root', repo, '--pilot', spec, '--deck-a', reg['t-altaria'], '--deck-b', reg['t-suicune'], '--games', '12']
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='replace', env=env, start_new_session=True)
    try:
        timeout = None if deadline is None else max(0.0, (deadline.astimezone(UTC) - now().astimezone(UTC)).total_seconds())
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_group(proc)
        die(f'REFUSED: the self-check of {spec} did not finish before the school-morning cut at {deadline.astimezone(CHICAGO).strftime("%a %H:%M")} Chicago time; nothing was written. '
            'Start it earlier in the evening or on a weekend (or with --school-rule off).')
    except BaseException:
        stop_group(proc)
        raise
    finally:
        for pipe in (proc.stdout, proc.stderr):
            if pipe:
                pipe.close()
    got = out.strip()
    if got != pin['selfcheck'][spec]:
        die(f'REFUSED: the self-check of {spec} does not match the pin.\n  pinned: {pin["selfcheck"][spec]}\n  got:    {got[-300:] or err.strip()[-200:]}\n'
            'The program is not behaving as the pinned build did; nothing was written.')
    return got


# ------------------------------------------------------------------------------------------------------------------ a registered run
def load_registered(rundir):
    """manifest.json of a run, refused unless it is the pre-registered file."""
    mp = os.path.join(rundir, 'manifest.json')
    if not os.path.isfile(mp):
        die(f'{rundir} has no manifest.json: it is not a registered run')
    msha = sha(mp)
    sp = os.path.join(rundir, 'manifest.sha256')
    reg = None
    if os.path.exists(sp):
        with open(sp, encoding='utf-8') as f:
            reg = (f.read().split() or [None])[0]
    problems = R.registration_problems(msha, reg)
    if problems:
        die('REFUSED: the registration has changed, so nothing is run or reported.\n  ' + '\n  '.join(problems)
            + '\nRead manifest.json against PREREGISTRATION.md; a changed run is a new run, with a new pre-registration.')
    return load_json(mp), msha


def verify_inputs(man):
    """Problems with the files this run was registered with: the program, the deck and the panel lists (exactly as the program will read them)."""
    problems = []
    prog = man['program']
    if not os.path.isfile(prog) or sha(prog) != man.get('program_sha256'):
        problems.append(f'{prog} is not the program this run was registered with (sha256 {str(man.get("program_sha256"))[:12]})')
    root = man.get('repo_root') or '.'
    if man.get('repo_root') and not os.path.isdir(root):
        problems.append(f'the repository this run was registered in ({root}) is not there: the run records the path of its checkout, so a moved or renamed checkout cannot resume it '
                        '(put the checkout back at that path, or link it there)')
        return problems
    for d in man['decks'] + man['opponents']:
        p = d['path'] if os.path.isabs(d['path']) else os.path.join(root, d['path'])
        if not os.path.isfile(p):
            problems.append(f"{d['name']} ({p}) is missing")
        elif sha(p) != d['sha256']:
            problems.append(f"{d['name']} ({p}) has changed since registration (sha256 {sha(p)[:12]} instead of {d['sha256'][:12]})")
    return problems


def planned_keys(man):
    keys = []
    for d in man['decks']:
        for o in man['opponents']:
            if o['name'] == d['name']:
                continue
            for deal in range(man['deals']):
                for seat in man['seats']:
                    for arm in ('ref', 'X'):
                        keys.append(f"{d['name']}|{o['name']}|{deal}|{seat}|{arm}")
    return keys


def load_games(rundir):
    games, seen = [], set()
    for r in load_jsonl(os.path.join(rundir, 'games.jsonl')):
        if 'key' in r and r['key'] not in seen:
            seen.add(r['key'])
            games.append(r)
    return games


def log_event(rundir, event, **kw):
    with open(os.path.join(rundir, 'slow_report_log.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(dict(at=utc_iso(), event=event, **_LOG_EXTRA, **kw), default=str) + '\n')


def run_games(rundir, man, scrub_prefixes, *, threads, max_games, school_on, school_days, now, sleep, spawn, poll_s, say):
    """Play the games still missing, in sittings. With the school rule on, a sitting is told to start no new game after the next school morning's 5:15,
    is killed at 6:30 if a game is still going, and the run waits for 5 pm. The program, the deck and the panel files are checked before every sitting.
    Returns 'complete' or 'limit' (max_games reached); raises SystemExit on a failing program, changed inputs, or repeated cuts with no progress."""
    env, removed = scrub_env(dict(os.environ), scrub_prefixes)
    if removed:
        log_event(rundir, 'env_scrubbed', names=removed)
        say("removed from the program's environment (they would change the pilot or the rules): " + ', '.join(removed))
    planned = planned_keys(man)
    out_log = os.path.join(rundir, 'run_output.log')
    budget = max_games
    cuts_without_progress = 0
    while True:
        if load_registered(rundir)[0] != man:  # the program re-reads manifest.json every sitting, so it is checked every sitting (a changed one refuses inside)
            die('REFUSED: manifest.json is not the one this run started with, so nothing is run.')
        problems = verify_inputs(man)
        if problems:
            die('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  ' + '\n  '.join(problems))
        have = {g['key'] for g in load_games(rundir)}
        remaining = len([k for k in planned if k not in have])
        if remaining == 0:
            log_event(rundir, 'complete', games=len(have))
            return 'complete'
        soft, hard = None, None
        if school_on:
            act = school_action(now(), school_days)
            if act['kind'] == 'wait':
                log_event(rundir, 'waiting_for_school', until=act['until'].isoformat(), remaining_games=remaining)
                say(f"school-morning rule: waiting until {act['until'].strftime('%a %H:%M')} Chicago time to start again ({plural(remaining, 'game')} to go)")
                wait_until(act['until'], now, sleep)
                continue
            soft, hard = act['stop_after_min'], act['hard_stop']
            if soft is not None and soft < 1.0:  # less than a minute left: no game would finish, so let the cut come first
                sleep(soft * 60)
                continue
        cmd = nice_prefix() + [man['program'], 'run', '--manifest', os.path.join(rundir, 'manifest.json'), '--out', rundir, '--threads', str(threads)]
        if soft is not None:
            cmd += ['--stop-after-min', f'{soft:.3f}']
        if budget is not None:
            cmd += ['--max-games', str(budget)]
        log_event(rundir, 'slice_start', remaining_games=remaining, stop_after_min=soft, hard_stop=hard.isoformat() if hard else None, threads=threads)
        say(f"running: {plural(remaining, 'game')} to go, {threads} at a time" + (f', no new game after the school-morning cut ({soft:.0f} min from now)' if soft is not None else ''))
        proc = spawn(cmd, env, out_log)
        _PROGRAMS.append(proc)
        note_program(proc)
        killed = False
        try:
            while proc.poll() is None:
                if hard is not None and now() >= hard:
                    stop_group(proc)
                    killed = True
                    break
                sleep(poll_s)
        except BaseException:
            stop_group(proc)
            log_event(rundir, 'interrupted')
            raise
        finally:
            fh = getattr(proc, '_logfh', None)
            if fh:
                fh.close()
            if getattr(proc, 'poll', lambda: 0)() is not None:
                note_program(None)  # the program has ended: its process group is no longer worth naming in a refusal
        rc = proc.returncode
        have_after = {g['key'] for g in load_games(rundir)}
        new = len(have_after - have)
        log_event(rundir, 'slice_end', returncode=rc, killed_for_school=killed, new_games=new)
        if budget is not None:  # --max-games is for the whole call: games played in a sitting that was cut at 6:30 count too
            budget -= new
        left_over = remaining - new
        if killed:
            log_event(rundir, 'stopped_for_school', at_local=now().isoformat())
            say('school-morning rule: the program was stopped at 6:30; the game it was in the middle of will be played again')
            cuts_without_progress = 0 if new else cuts_without_progress + 1
            if cuts_without_progress >= MAX_CUTS_WITHOUT_PROGRESS:
                die(f'no game finished in {MAX_CUTS_WITHOUT_PROGRESS} sittings in a row that were each cut off at 6:30: a game takes longer than the time the school-morning rule leaves, '
                    'so it can never finish. Stopping rather than trying forever (run it with --school-rule off at a time that suits, or on a weekend).')
            if budget is not None and budget <= 0 and left_over > 0:
                return 'limit'
            continue
        cuts_without_progress = 0
        if rc != 0:
            die(f'the program stopped with exit code {rc}; the end of its output ({out_log}):\n{tail_text(out_log)}')
        if budget is not None and budget <= 0 and left_over > 0:
            return 'limit'
        if new == 0:
            die(f'no game finished in this sitting (games that end in an error are listed in {os.path.join(rundir, "errors.jsonl")}); stopping rather than trying forever')


# ------------------------------------------------------------------------------------------------------------------ the page
T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074,
       2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def t_crit(df):
    """Two-sided 95% Student t value: the table up to 30 degrees of freedom, the Cornish-Fisher expansion of the normal value beyond."""
    if df < 1:
        return float('nan')
    if df <= 30:
        return T95[df - 1]
    z = R.Z
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df * df)


def wilson_range(scores):
    """(mean, low, high): the Wilson 95% range of the mean score (a tie counts half), clipped to 0..1. Valid at 0% and 100% and for few games."""
    n = len(scores)
    p, lo, hi = R.wilson(sum(scores), n)
    return p, max(0.0, lo), min(1.0, hi)


def signed_points(x):
    """A score difference (a fraction) as signed percentage points with one decimal, never '-0.0'."""
    s = f'{round(100 * x, 1):+.1f}'
    return '+0.0' if s in ('-0.0', '+0.0') else s


def human_time(sec):
    if sec != sec:
        return 'n/a'
    if sec < 90:
        return f'{sec:.0f} s'
    if sec < 5400:
        return f'{sec / 60:.0f} min'
    if sec < 172800:
        return f'{sec / 3600:.1f} h'
    return f'{sec / 86400:.1f} days'


def fmt_s(x):
    """Seconds to the whole second, or to a tenth below ten seconds (a cheap pilot's games last about a second)."""
    return f'{x:.0f} s' if x >= 10 else f'{x:.1f} s'


def pct1(x):
    return f'{100 * x:.1f}%'


def games_word(n):
    return plural(n, 'game')


def gain_range_note(pilot, ref, n, m, half):
    """In plain words what the paired-gain range m +- half (fractions of a score, over n paired games) does and does not include; never waves a wide range away."""
    glo, ghi = m - half, m + half
    if ghi - glo >= 2:
        return f"That range is wider than the whole possible scale (-100 to +100 points): {plural(n, 'paired game')} are too few to say anything about the gain yet."
    clipped = glo < -1 or ghi > 1
    glo, ghi = max(-1.0, glo), min(1.0, ghi)
    lo_txt = 'just above +0.0' if glo > 0 and signed_points(glo) == '+0.0' else signed_points(glo)
    hi_txt = 'just below +0.0' if ghi < 0 and signed_points(ghi) == '+0.0' else signed_points(ghi)
    cut = ' (cut at the ends of the possible scale)' if clipped else ''
    if glo <= 0 <= ghi:
        return (f"That range runs from {lo_txt} to {hi_txt} points{cut}, which includes no gain at all: these {n} paired games do not show that {pilot} plays this deck "
                f"better than {ref}, and do not show that it plays it worse. They do argue against a gain much larger than {100 * ghi:.1f} points or a loss much larger "
                f"than {100 * abs(glo):.1f} points; a smaller difference needs more deals.")
    return (f"That range runs from {lo_txt} to {hi_txt} points{cut}, which does not include no gain: on these {n} paired games {pilot} did "
            f"{'better' if glo > 0 else 'worse'} than {ref}. It does not say by exactly how much: that part of the range is as wide as {n} paired games make it.")


def kg(n, who, cheap=False):
    """'1 kx3 game', '80 kx3 games', '80 cheap km3 baseline games': the pilot named in every count (the reporting rule: kx3 games v total games)."""
    return f"{n} {'cheap ' if cheap else ''}{who}{' baseline' if cheap else ''} game{'' if n == 1 else 's'}"


def join_numbers(xs):
    xs = [str(x) for x in xs]
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def unfinished_errors(rundir, finished_keys):
    """[(key, attempts, first message)] for games that failed and are still not in games.jsonl, by game (the program appends a line on every try)."""
    attempts, first = {}, {}
    for e in load_jsonl(os.path.join(rundir, 'errors.jsonl')):
        k = e.get('key')
        if k is None:
            continue
        attempts[k] = attempts.get(k, 0) + 1
        first.setdefault(k, str(e.get('error', ''))[:200])
    return [(k, attempts[k], first[k]) for k in first if k not in finished_keys]


SELFCHECK_HOW = (('given', 'copied from the pin, not replayed'), ('replayed by slow_report', 'replayed just before registration, equal to the pin'),
                 ('run by strength_prereg', 'replayed at registration'))


def selfcheck_how(source):
    for prefix, text in SELFCHECK_HOW:
        if (source or '').startswith(prefix):
            return text
    return 'recorded at registration'


def write_slow_report(rundir, out=None):
    man, msha = load_registered(rundir)
    sr = man.get('slow_report')
    if not sr:
        die(f'{rundir} is not a slow report run (its manifest has no slow_report block)')
    games = load_games(rundir)
    finished = {g['key'] for g in games}
    errors = unfinished_errors(rundir, finished)
    deck, deals = sr['deck_name'], sr['deals']
    pilot, ref = man['pilot'], man['reference']
    panel = [o['name'] for o in man['opponents']]
    k = len(panel)
    xg = [g for g in games if g['arm'] == 'X']
    rg = [g for g in games if g['arm'] == 'ref']
    planned = man['planned_games']
    partial = len(games) < planned
    L = []
    P = L.append
    P(f'# Slow report: {deck}\n')
    P(f'**{sr["headline"]}** ({k} public lists: {", ".join(panel)}). Stage `use`: a report on one deck, not development evidence.\n')
    if partial:
        P(f"**PARTIAL: {len(games)} of {planned} games played so far ({kg(len(xg), pilot)} + {kg(len(rg), ref, True)}; both count in the {planned}). "
          f"The numbers below will move; read them as a snapshot.**\n")
    if errors:
        n = len(errors)
        every = any(a >= 2 for _, a, _ in errors)
        key, att, msg = errors[0]
        P(f"{n} game{'' if n == 1 else 's'} could not be finished and {'is' if n == 1 else 'are'} left out of every number below (first: `{key}`, {att} {'try' if att == 1 else 'tries'}: {msg}). "
          f"A game that crashes is not a loss, so if the same card crashes {'them' if n > 1 else 'it'} the score leans towards games without it. "
          + ('At least one failed every time it was tried, so resuming will not fix it.' if every else f"A resumed run tries {'them' if n > 1 else 'it'} again.") + '\n')

    P('## What it says\n')
    paired_on = bool(sr.get('paired'))
    planned_x = len(panel) * deals * 2
    if paired_on:
        P(f'Question: how does {deck} do when {pilot} plays it against the {k} public lists, and is that better than when {ref} plays the same deck on the same deals?')
    else:
        P(f'Question: how does {deck} do when {pilot} plays it against the {k} public lists?')
    size = kg(len(xg), pilot) + (f' + {kg(len(rg), ref, True)}' if paired_on else '')
    if partial:
        P(f'Size: {size} so far, of {kg(planned_x, pilot)}' + (f' + {kg(planned_x, ref, True)}' if paired_on else '') + ' planned.\n')
    else:
        P(f'Size: {size} ({plural(deals, "deal")} x 2 seats against each of the {k} public lists' + (f'; the baseline games are the same deals with {ref} on the deck' if paired_on else '') + ').\n')
    xs = [SCORE[g['winner']] for g in xg]
    p = lo = hi = None
    if not xs:
        P(f'No {pilot} game has finished yet.\n')
    else:
        p, lo, hi = wilson_range(xs)
        lists_with = len({g['opp'] for g in xg})
        shape = (f'{plural(deals, "deal")} x 2 seats against each of the {k} public lists' if not partial else f'games from {lists_with} of the {k} public lists so far')
        P(f"{deck} scored **{pct1(p)}** over **{games_word(len(xs))}** ({shape}): probably between {pct1(lo)} and {pct1(hi)} "
          f"(95% interval; this range refers to {'this' if len(xs) == 1 else 'these'} {kg(len(xs), pilot)}). A win counts 1, a tie 1/2, a loss 0.\n")
    pairs = {}
    for g in games:
        pairs.setdefault((g['opp'], g['deal'], g['seat']), {})[g['arm']] = SCORE[g['winner']]
    both = [v for v in pairs.values() if 'X' in v and 'ref' in v]
    if paired_on:
        P(f'### How much better {pilot} plays this deck than {ref}\n')
        if not both:
            P('No deal has been played both ways yet.\n')
        else:
            d = [v['X'] - v['ref'] for v in both]
            n, m = len(d), statistics.mean(d)
            sx, sref = statistics.mean(v['X'] for v in both), statistics.mean(v['ref'] for v in both)
            head = (f"On the same deals, {pilot} scored **{signed_points(m)} points** compared with {ref} piloting this deck "
                    f"({pilot} {pct1(sx)}, {ref} on this deck {pct1(sref)}, over {plural(n, 'paired game')}: each a deal and seat played by both pilots, so {kg(n, pilot)} + {kg(n, ref, True)})")
            sd = statistics.stdev(d) if n > 1 else 0.0
            if n < 2:
                P(head + '; with one comparison no interval can be given.\n')
            elif sd == 0:
                P(head + f'; every one of the {n} comparisons gave the same difference, so no spread can be estimated from them.\n')
            else:
                half = t_crit(n - 1) * sd / math.sqrt(n)
                P(head + f', give or take {100 * half:.1f} points (95% interval; this range refers to {"that" if n == 1 else "those"} {plural(n, "paired game")}).\n')
                P(gain_range_note(pilot, ref, n, m, half) + '\n')

    P('## Against each public list\n')
    P(f'| opponent ({ref}) | {pilot} games | score | 95% range |')
    P('|---|---|---|---|')
    for opp in panel:
        s = [SCORE[g['winner']] for g in xg if g['opp'] == opp]
        if not s:
            P(f'| {opp} | 0 | n/a | n/a |')
            continue
        pp, l1, h1 = wilson_range(s)
        P(f'| {opp} | {len(s)} | {pct1(pp)} | {pct1(l1)} to {pct1(h1)} |')
    P(f"\nEach row's range refers only to the {pilot} games against that list (the row's games column); with so few games it can tell a very easy or a very hard list "
      f'from an even one, not two similar lists from each other.\n')

    P('## Who went first\n')
    for label, which in (('went first', 'deck'), ('went second', 'opp')):
        s = [SCORE[g['winner']] for g in xg if g['first'] == which]
        if s:
            pp, l1, h1 = wilson_range(s)
            P(f'- When {deck} {label}: {pct1(pp)} over {games_word(len(s))} ({pct1(l1)} to {pct1(h1)})')
        else:
            P(f'- When {deck} {label}: no games yet')
    P(f'\nEach range refers only to the {pilot} games on its line; a few dozen games can show a large first-or-second difference, not a small one.\n')

    P('## The time it took\n')
    rl = load_jsonl(os.path.join(rundir, 'run_log.jsonl'))
    starts = [e for e in rl if e.get('event') == 'start']
    stops = [e for e in rl if e.get('event') == 'stop']
    used = sorted({int(e['threads']) for e in starts if isinstance(e.get('threads'), (int, float))}) or [max(1, int(man.get('threads', 1)))]
    tword = f"{join_numbers(used)} thread{'' if used == [1] else 's'}"
    walls = [g['wall_s'] for g in xg]
    if walls:
        mean_w = statistics.mean(walls)
        line = (f"{pilot} took {fmt_s(mean_w)} a game on average" + (f" (about {human_time(mean_w)})" if mean_w >= 90 else '')
                + f", median {fmt_s(statistics.median(walls))}, slowest {fmt_s(max(walls))}, with {tword} going at once.")
        if sr.get('paired') and rg:
            line += f" {ref} playing this deck took {statistics.mean([g['wall_s'] for g in rg]):.1f} s a game."
        P(line)
    else:
        P(f'No {pilot} game has finished yet.')
    in_all = f'{games_word(len(games))} in all: {kg(len(xg), pilot)} + {kg(len(rg), ref, True)}'
    if starts and len(starts) == len(stops):
        P(f"Running time from the run log: {human_time(sum(e['elapsed_s'] for e in stops))} over {plural(len(stops), 'sitting')}, for {in_all}.")
    elif games:
        est = sum(g['wall_s'] for g in games) / max(used)
        why = ('There is no run log, so the running time is' if not rl else
               'The run log has a sitting that did not close (for example the program was stopped by the 6:30 school-morning cut, or the run was interrupted), so the running time is')
        P(f'{why} estimated from the game times and the thread count: {human_time(est)}, for {in_all}.')
    P('')

    P("## What these numbers can and can't say\n")
    if not xs:
        P(f'**Nothing to say yet: no {pilot} game has finished.**\n')
    else:
        P(f"**These numbers say how {deck} did in simulated games with {pilot} playing it against the {k} public lists, probably between {pct1(lo)} and {pct1(hi)}; "
          f"they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**\n")
        P('In more detail:\n')
        P(f"- {pilot}, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the {k} public lists it faces, but its opponent is always one of them "
          f"and always plays like the program {pilot} imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside "
          f"the {k} lists. Read the score as the optimistic end.")
        P(f"- The {k} lists count equally here, not by how common they are on the ladder.")
        P(f"- The range covers only the luck of the shuffles and coin flips in these {games_word(len(xs))}; it does not cover how true to the real game the simulator is. "
          f"It can tell whether {pilot} plays {deck} clearly above or clearly below an even score against these {k} lists; it cannot tell two decks apart whose scores differ by "
          f"less than the width of such a range ({100 * (hi - lo):.1f} points here), and more deals narrow it.")
        P(f"- There is no pass or fail line: whether {deck} is worth playing is a call for the player.\n")

    P('## What was run\n')
    P(f"- Pilots: {sr['pilot_label']} on the deck, {sr['reference_label']} on {sr['panel_label']}. Program `{man.get('program')}` sha256 `{str(man.get('program_sha256'))[:12]}`.")
    for spec, txt in (man.get('selfcheck') or {}).items():
        P(f"- Self-check of `{spec}`: `{txt}` ({selfcheck_how((man.get('selfcheck_source') or {}).get(spec))})")
    if man.get('engine'):
        P(f"- Build: {man['engine']}")
    P(f"- Deck file `{sr['deck_file']}` sha256 `{sr['deck_file_sha256'][:12]}`; the file is {sr['deck_file_state']}.")
    if man.get('heldout_in_run'):
        P(f"- Held-out decks in this run: {', '.join(man['heldout_in_run'])}. Allowed because this is a `use` report, not development evidence; the held-out lock is unchanged.")
    first_start = min((g.get('started_at') for g in games if g.get('started_at')), default=None)
    order = ('before any game' if first_start is None or first_start >= (man.get('created_at') or '') else f"**but a game started at {first_start}, BEFORE the registration time**")
    P(f"- Registered {man.get('created_at')}, {order}; manifest sha256 `{msha[:16]}`; repository commit `{man.get('repo_commit')}`; pin `{sr['pin']['path']}`.")
    P(f"- {plural(deals, 'deal')} x 2 seats; seeds `{man['seed_base']} + p x {man['pair_stride']} + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.")
    if os.path.exists(os.path.join(rundir, 'REPORT.md')):
        P('- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.')
    text = '\n'.join(L).rstrip() + '\n'
    path = out or os.path.join(rundir, 'SLOW_REPORT.md')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return text


def console_lines(text):
    """The lines worth echoing to the terminal: the PARTIAL banner, the error note and 'What it says', without markdown."""
    out = []
    for line in text.splitlines():
        if line.startswith('**PARTIAL') or ('could not be finished' in line and line[:1].isdigit()):
            out.append(line)
    if '## What it says' in text:
        sec = text.split('## What it says')[1].split('\n## ')[0]
        out += [l for l in sec.splitlines() if l.strip() and not l.startswith('#')]
    return [l.replace('**', '').replace('`', '').strip() for l in out]


# ------------------------------------------------------------------------------------------------------------------ main
def best_effort_pages(rundir, say):
    """The engineering report and the page from the games so far (never raises): used when a run stops early so what exists is not lost."""
    try:
        subprocess.run([sys.executable, '-B', REPORT, '--dir', rundir], capture_output=True, text=True)
        write_slow_report(rundir)
        say('SLOW_REPORT.md (partial) written before stopping')
    except BaseException as e:  # noqa: B902
        if isinstance(e, KeyboardInterrupt):
            raise
        say(f'could not write the page before stopping: {e}')


def main(argv=None, *, now=None, sleep=None, spawn=None, deck_check=None):
    ctx = {'tag': 'slow report'}
    try:
        with signals_stop_the_program():  # over the whole call: the self-check, the registration and the run all stop their child process (and clean up) on SIGTERM / SIGHUP
            return _main(argv, ctx, now=now, sleep=sleep, spawn=spawn, deck_check=deck_check)
    except SystemExit as e:
        if isinstance(e.code, str) and not e.code.startswith('['):
            raise SystemExit(f"[{ctx['tag']}] {e.code}") from None
        raise


def _main(argv, ctx, *, now, sleep, spawn, deck_check):
    ap = argparse.ArgumentParser(description='The opt-in slow report: kx3 on one deck v km3 on the public panel (see the module docstring).')
    ap.add_argument('deckfile', nargs='?', help='a deck file inside the repository')
    ap.add_argument('--dir', help='resume (or just report on) a registered run directory')
    ap.add_argument('--deals', type=int, help='deals per opponent (default 5; 16 x N kx3 games)')
    ap.add_argument('--no-paired', action='store_true', help='leave out "how much better kx3 plays this deck than km3 on the same deals" (reported by default: the program plays km3 on the deck anyway, a second a game)')
    ap.add_argument('--threads', type=int, help="games at a time (default: the pin's, 2)")
    ap.add_argument('--repo', default=ROOT)
    ap.add_argument('--pin', default=DEFAULT_PIN)
    ap.add_argument('--out-root', help='where run directories go (default: <repo>/rl/results/slow_reports)')
    ap.add_argument('--date', help="YYYY-MM-DD for the run directory name (default: today in Chicago)")
    ap.add_argument('--seed-base', type=int)
    ap.add_argument('--selfcheck', action='store_true', help='replay the pinned self-check games instead of recording the pinned text (hours for kx3)')
    ap.add_argument('--register-only', action='store_true')
    ap.add_argument('--report-only', action='store_true', help='with --dir: write the page from the games so far and play nothing')
    ap.add_argument('--dry-run', action='store_true', help='print the plan (or, with --dir, where the run stands); write nothing')
    ap.add_argument('--school-rule', choices=('on', 'off'), default='on')
    ap.add_argument('--school-days', default='mon,tue,wed,thu,fri')
    ap.add_argument('--max-games', type=int, help='play at most this many games in this call, then write the page and stop')
    ap.add_argument('--poll-s', type=float, default=20.0)
    a = ap.parse_args(argv)
    now = now or (lambda: datetime.datetime.now(CHICAGO))
    sleep = sleep or time.sleep
    spawn = spawn or default_spawn
    deck_check = deck_check or default_deck_check
    repo = os.path.abspath(a.repo)
    pin = load_pin(a.pin)
    _LOG_EXTRA.update(pilot=pin['pilot'], reference=pin['reference'])
    ctx['tag'] = f"{pin['pilot_label']} v {pin['reference_label']}"
    school_days = parse_days(a.school_days)

    if a.dir and a.deckfile:
        die('give a deck file or --dir, not both')
    if not a.dir and not a.deckfile:
        die('give a deck file to report on, or --dir RUNDIR to resume a registered run')

    def say(msg):
        print(f"[{ctx['tag']}] {msg}", flush=True)

    if a.dir:
        for flag, given in (('--deals', a.deals is not None), ('--no-paired', a.no_paired), ('--date', a.date is not None), ('--seed-base', a.seed_base is not None),
                            ('--selfcheck', a.selfcheck), ('--register-only', a.register_only)):
            if given:
                die(f'{flag} belongs to a new registration; a run that is already registered keeps what it was registered with, so it cannot be used with --dir')
        rundir = os.path.abspath(a.dir)
        man, msha = load_registered(rundir)
        if not man.get('slow_report'):
            die(f'{rundir} is not a slow report run (its manifest has no slow_report block)')
        ctx['tag'] = man['slow_report']['headline']
        _LOG_EXTRA.update(pilot=man['pilot'], reference=man['reference'])
    else:
        if a.report_only:
            die('--report-only needs --dir RUNDIR (a run that is already registered)')
        check_program(pin)
        deck_abs = os.path.abspath(a.deckfile)
        name = deck_name_of(deck_abs)
        ctx['tag'] = headline_of(pin, name)
        deals = 5 if a.deals is None else a.deals
        if not 1 <= deals <= MAX_DEALS:
            die(f'REFUSED: --deals must be between 1 and {MAX_DEALS}')

    if a.threads is not None and a.threads < 1:
        die('REFUSED: --threads must be at least 1')
    if a.max_games is not None and a.max_games < 1:
        die('REFUSED: --max-games must be at least 1')
    if not a.poll_s > 0:
        die('REFUSED: --poll-s must be greater than 0')

    if not a.dir:
        if not os.path.isfile(deck_abs):
            die(f'REFUSED: deck file {a.deckfile} not found')
        errs = deck_check(deck_abs, repo)
        if errs:
            die('REFUSED: the deck is not a valid 20-card list:\n  ' + '\n  '.join(errs))
        if os.path.commonpath([os.path.realpath(deck_abs), os.path.realpath(repo)]) != os.path.realpath(repo):
            die(f'REFUSED: the deck file must be inside the repository ({repo}) (a symlink is followed): the run hashes and records its decks at a commit, so copy the file in first')
        rel = os.path.relpath(deck_abs, repo).replace(os.sep, '/')
        registry = load_json(os.path.join(HERE, 'decks.json'))['decks']
        panel_names = load_json(os.path.join(HERE, 'groups.json'))[pin['panel_group']]
        if name in registry and os.path.normpath(registry[name]) != os.path.normpath(rel):
            die(f'REFUSED: the deck name {name!r} is already a different registered deck ({registry[name]}); rename the file')
        same = panel_signatures(repo, pin).get(PRE.deck_signature(deck_abs))
        if same:
            die(f'REFUSED: this deck is {same} (or a copy of it), one of the {len(panel_names)} public lists {pin["pilot"]} already knows, so a report on it would not be realistic')
        dsha = sha(deck_abs)
        state = deck_state(repo, rel)
        out_root = os.path.abspath(a.out_root) if a.out_root else os.path.join(repo, 'rl', 'results', 'slow_reports')
        seed_base = pick_seed_base(dsha, out_root, tuple(pin['seed_block']), pin['seed_step'], a.seed_base)
        date = a.date if a.date is not None else now().astimezone(CHICAGO).strftime('%Y-%m-%d')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                raise ValueError(date)
            datetime.date.fromisoformat(date)
        except ValueError:
            die(f'REFUSED: --date must be a real date written YYYY-MM-DD, not {date!r}')
        rundir = os.path.join(out_root, f'{date}_{name}')
        if os.path.exists(rundir):
            die(f'REFUSED: the run directory {rundir} already exists; resume it with --dir {shlex.quote(rundir)} (or pick another --date)')
        threads = a.threads or pin['threads']
        et = expected_time(deals, pin)
        say(f"plan: {name} ({rel}, {state}), {plural(deals, 'deal')} x 2 seats against the {len(panel_names)} public lists")
        say(f"size: {kg(et['kx3_games'], pin['pilot'])} + {kg(et['kx3_games'], pin['reference'], True)} on the same deals ({2 * et['kx3_games']} games in all; the {pin['reference']} games take about "
            f"a second each{'; with --no-paired they are still played and the page leaves them out' if a.no_paired else ''}); "
            f"the time is for the {kg(et['kx3_games'], pin['pilot'])}: about {hours_text(et['typical_hours'][0])} to "
            f"{hours_text(et['typical_hours'][1])} if the deck plays like most of his, about {hours_text(et['wall_hours'])} if it plays like the Wailord wall (measured with 2 games at a time)")
        say('on school days the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer')
        say(f"stage use (not development evidence; the held-out lock is untouched), seeds from {seed_base}, program {pin['program']} (pinned, sha256 {pin['program_sha256'][:12]}), "
            f"{'without' if a.no_paired else 'with'} the comparison with {pin['reference']} on the same deals in the page, no pass or fail line")
        if a.dry_run:
            say('dry run: nothing written')
            return 0
        given, how = 'pin', 'pin'
        if a.selfcheck:
            deadline = None
            if a.school_rule == 'on' and school_days:
                act = school_action(now(), school_days)
                if act['kind'] == 'wait':
                    die(f"REFUSED: the self-check runs for hours and it is school time (the school-morning rule waits until {act['until'].strftime('%a %H:%M')} Chicago time); "
                        'start it after that, or with --school-rule off')
                deadline = act['hard_stop']
            given, how = {spec: run_selfcheck(pin, repo, spec, say, deadline=deadline, now=now) for spec in sorted({pin['pilot'], pin['reference']})}, 'replayed'
            if os.path.exists(rundir):  # hours may have passed: what was decided before the self-check is decided again
                die(f'REFUSED: the run directory {rundir} appeared while the self-check ran; resume it with --dir {shlex.quote(rundir)} (or pick another --date)')
            again = pick_seed_base(dsha, out_root, tuple(pin['seed_block']), pin['seed_step'], a.seed_base)
            if again != seed_base:
                say(f'note: seed slot {seed_base} was taken while the self-check ran; using {again}')
                seed_base = again
        cfg = build_config(pin=pin, pin_path=a.pin, deck_rel=rel, deck_name=name, deck_sha=dsha, deck_state=state, deals=deals, paired=not a.no_paired, seed_base=seed_base,
                           threads=threads, program_sha=pin['program_sha256'], selfcheck_given=given, selfcheck_how=how,
                           resume_command=shlex.join(['python3', 'rl/strength/slow_report.py', '--dir', rundir]))
        made_root = not os.path.exists(out_root)

        def cleanup():
            shutil.rmtree(rundir, ignore_errors=True)
            if made_root:
                try:
                    os.rmdir(out_root)
                except OSError:
                    pass
        os.makedirs(rundir)
        try:
            cfg_path = os.path.join(rundir, 'config.json')
            with open(cfg_path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(cfg, f, indent=1, ensure_ascii=False)
                f.write('\n')
            r = run_prereg(cfg_path, rundir, repo)
            if r.returncode != 0:
                cleanup()
                die('REFUSED by strength_prereg.py (nothing was written):\n' + (r.stderr.strip() or r.stdout.strip()))
            for line in r.stdout.splitlines():
                if line.strip():
                    say(line.strip())
            man, msha = load_registered(rundir)
            log_event(rundir, 'registered', manifest_sha256=msha, seed_base=seed_base, deals=deals, paired=not a.no_paired, threads=threads, deck_file=rel, deck_sha256=dsha)
        except BaseException:
            if not os.path.exists(os.path.join(rundir, 'manifest.sha256')):
                cleanup()  # an interrupt (or a refusal) before the registration was written leaves nothing behind
            raise
        say(f'registered in {rundir} before any game')
        if a.register_only:
            return 0

    sr_block = man['slow_report']
    if a.dir and a.dry_run:
        planned = len(planned_keys(man))
        have = len({g['key'] for g in load_games(rundir)})
        problems = verify_inputs(man)
        if have >= planned:
            status = 'complete'
        elif problems:
            status = 'it would be refused: ' + '; '.join(problems)
        else:
            status = 'resume with: ' + (sr_block.get('resume_command') or shlex.join(['python3', 'rl/strength/slow_report.py', '--dir', rundir]))
        say(f"{have} of {planned} games played; {plural(planned - have, 'game')} to go ({status})")
        say('dry run: nothing written')
        return 0

    if a.dir and sr_block.get('pin', {}).get('sha256') and os.path.isfile(a.pin) and sha(a.pin) != sr_block['pin']['sha256']:
        say('note: the pin file has changed since this run was registered; the run continues with the program, settings and scrub list it was registered with')
    if not a.report_only:
        problems = verify_inputs(man)
        if problems:
            die('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  ' + '\n  '.join(problems))
        lock = acquire_lock(rundir, say)
        try:
            try:
                status = run_games(rundir, man, sr_block.get('scrub_env_prefixes') or pin['scrub_env_prefixes'],
                                   threads=a.threads or man.get('threads') or pin['threads'], max_games=a.max_games,
                                   school_on=a.school_rule == 'on', school_days=school_days, now=now, sleep=sleep, spawn=spawn, poll_s=a.poll_s, say=say)
            except (SystemExit, KeyboardInterrupt):
                best_effort_pages(rundir, say)
                raise
        finally:
            release_lock(lock)
        if status == 'limit':
            say(f'stopped after --max-games {a.max_games}; resume with --dir {shlex.quote(rundir)}')
    # the engineering report (REPORT.md) first, so the page can point at it; a failure there never blocks the page
    rr = subprocess.run([sys.executable, '-B', REPORT, '--dir', rundir], capture_output=True, text=True)
    if rr.returncode != 0:
        say('REPORT.md (the engineering report) could not be written: ' + (rr.stderr.strip().splitlines() or ['no message'])[-1])
    text = write_slow_report(rundir)
    log_event(rundir, 'report_written', path=os.path.join(rundir, 'SLOW_REPORT.md'))
    say(f'SLOW_REPORT.md written in {rundir}')
    for line in console_lines(text):
        say(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
