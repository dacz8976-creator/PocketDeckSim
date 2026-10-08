#!/usr/bin/env python3
"""Tests for slow_report.py, the opt-in "slow report" (kx3 on one deck v km3 on the public panel; rl/results/kx3_slow_report_plan_2026-10-06/PLAN.md).

  cd rl/strength && python3 -B -m unittest -v test_slow_report

Written before the code, and extended after an independent adversarial review (every gap the review found has a test here). Nothing here plays a real
game: the program is a small fake that obeys the real program's command line (`run --manifest --out --threads --stop-after-min --max-games`, `selfcheck`),
writes game records in the real format and records what it was called with. Every repository, run directory and clock is synthetic and temporary, and so is the
registry: World gives each test its own decks.json, groups.json and heldout.json (a copy of strength_prereg.py beside them, slow_report.HERE and PREREG pointing at
that folder while the test runs), the 8 panel lists and 3 held-out decks as synthetic files, so a change to the real registry or the real lists cannot break a test.
What still reads live data, on purpose: the committed pin (the template of every test pin, and test_the_committed_pin_names_the_frozen_program), the real deck
validator lib/deck_check.py with its card database (the "real validator" tests), the NAMES and PATHS (not the content) of the real registry, to lay out placeholder
files for the tests that start the real script in a subprocess to register a new run (World.lay_out_registry), and the tests that use the LiveWorld fixture or sit in
LiveRepositoryData in test_slow_report_registration.py (START_HERE.md, the real groups, the real panel and held-out files).

What is pinned:
  * the pin: the frozen kx3 program (sha256, self-check digests, provenance) is the only one a report may use, checked before any file is written, again
    before every sitting, and the deck and panel files are checked against the registration before every sitting;
  * the `use` stage and the registration: before any game, through strength_prereg.py, with the deck file by path, the public panel as the opponents, kx3 on the
    deck and km3 on the panel, N deals x 2 seats, seeds from the registered block, a deck that is itself a panel list refused;
  * the school-morning rule: no new game after 5:15 am on a school day, the run stopped by 6:30, resumed from 5 pm, nothing on weekends; waits are taken in
    short steps; a game cut off replays; repeated cuts with no progress stop the run;
  * the run: checkpoint and resume, one wrapper per run directory, a signal stops the program, the program never sees KX_EXTRA_LISTS or any other tuning variable;
  * the page: the deck's score with Wilson 95% ranges (never a zero-width interval), plain words, never pass or fail, both pilots named in every line printed and in
    the page, honest about partial runs, errors, ties and what the interval covers;
  * refusals that write nothing: an unpinned program, a bad deck, a deck outside the repository (symlinks followed), a registration that changed;
  * the school-morning choice (rule on or off, school days) is made at the registration and recorded in the manifest, PREREGISTRATION.md, the page and the resume command, and a
    run with the rule off needs no time zone database (SchoolChoiceIsRegistered, NoTimeZoneDatabase; the resume side is in test_slow_report_runloop.py);
  * the pin's reserved seed slots (the km3 smoke) are used slots, and registering a deck with an unfinished report of it already registered warns, without refusing
    (ReservedSeedSlots, UnfinishedRuns);
  * the cloud route: `--program PATH`, a rebuild of the pinned source, accepted only with the committed pin, the pinned harness source, its build record (PROGRAM.build.json, written
    by rl/strength/build.sh) with the pinned engine tree (as archived) and harness source, and both self-checks replayed on it equal to the committed pin's; the pinned binary's own
    path with other bytes is the overwritten frozen binary, never a rebuild; a replay that exits with an error is not a match even when it printed the pinned text (CloudRoute,
    RebuiltFixture);
  * the committed pin: the pin in use must be byte-equal to HEAD's rl/strength/slow_report_pin.json in the repository the run is made from, or a new registration, a dry run and a
    register-only call are refused before anything is written; the test-only variable SLOW_REPORT_ALLOW_UNCOMMITTED_PIN lets a hand-made pin through and the plan, the registration
    and the page say so (World sets it for every fixture; CommittedPin takes it away); a resume does not need it (CommittedPin); when git cannot find the pin the detail says what git
    said (its first line, at most 200 characters) and, when git calls the folder unsafe (a checkout owned by another user), that this is not the pin being uncommitted, with the folder
    quoted for the shell in the advice to trust it (CommittedPin, with a stub git on the PATH); git is read with git_env(), without the variables a git hook exports that choose another
    repository (GIT_REPO_VARS) and with optional locks off, so the pin of the folder given is judged by that folder's HEAD (CommittedPin; the same for a deck file in
    test_slow_report_process.py);
  * the words follow the state of the pin: "the committed pin's digests" for a committed pin, "the digests of the pin file in use (NOT the committed pin: test use)" for a pin let
    through, in the registered engine text, the plan, the console lines of a resume, the dry run of a folder, the page's paragraph on a program that is not the pinned binary, its
    program-changed lines (by the pin each replay was made under) and its Self-check lines (Pin, CommittedPin, CloudRoute);
  * the build record: every shape of refusal of read_build_record (a schema that is not the whole number 1, an entry that has to be text and is not), and that the registration carries
    the record it read; a record with only the entries that are checked is described in words, never as None: "toolchain not recorded" in the engine text, "built with an unrecorded
    toolchain" in the plan, "rustc not recorded" on the page (rustc_line gives the first non-empty line of the record's rustc or the words it is given) (BuildRecord, CloudRoute);
  * a program that is another file when a rebuilt run is resumed (a container restart): judged by the pin the run was REGISTERED under (engine tree, harness hash, engine ref, self-check
    texts: every difference refused, in the resume and in the dry run), then accepted only after the committed pin, the new program's record and both self-checks replayed again, logged as
    'program_changed' (its old sha256 the program the previous sitting ran with: a second change reads B -> C, A -> B -> A -> C reads A -> C) and shown on the page, the accepted hashes
    kept for the later calls and for the check before each sitting; only the lines of the log that reverify_program could have written for this run count (is_program_change: the event, the
    rebuilt route, and a line consistent with the registration), in the accepted hashes, in the old program a later change is logged from and on the page, and only for a run registered
    on the rebuilt route; a run with every game played writes its page and replays nothing; refused for a pinned run (in the pinned run's words: byte for byte or a new run), with
    another problem too, without a record, with a replay that differs (ProgramChangedOnResume, and the stop signals in test_slow_report_process.py);
  * the dry run of a folder (and the resume it stands for) with every game played: "complete" when the files are as registered, or when the only difference is a rebuilt run's program that
    is there (nothing is replayed); "it would be refused: ..." with the report-only hint when a deck or panel list changed, a program of a pinned run changed or a program is missing; the
    real resume's refusal gets its own report-only line then, and neither says it with games still to play; program_only_problem is the one test both make, and the dry run's refusal of
    the replay is worded without a second "REFUSED:" (ProgramChangedOnResume, DryRunOfARegisteredRun in test_slow_report_runloop.py);
  * the time zone database: a missing one is a clear refusal at the registration and at the resume with the rule on and school days, and no problem without (NoTimeZoneDatabase);
  * a pin must list its reserved slots, and a typo in the list is refused (ReservedSeedSlots); an earlier unfinished report of the deck is warned about with its own resume
    command (UnfinishedRuns).
"""
import contextlib, datetime, fcntl, hashlib, inspect, io, json, math, os, re, shlex, shutil, signal, socket, statistics, subprocess, sys, tempfile, textwrap, time, unittest, zoneinfo
from unittest import mock
import builtins, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402

CHI = zoneinfo.ZoneInfo('America/Chicago')
PANEL = ['t-altaria', 't-blaziken', 't-hydreigon', 't-lucario', 't-sceptile', 't-suicune', 't-vespiquen', 't-weezing']
HEADLINE_START = '[kx3 (d513e37b) on '
BLOCK = (24_601_000_000, 24_699_999_999)
STEP = 100_000
ALLOW_PIN_VAR = 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN'  # the test-only switch that lets a hand-made pin through (World sets it; CommittedPin takes it away)
DROP = object()  # in a build record made by a test: leave this field out
# what the refusal of a program of another sha256 tells a person to do, after "<path> has sha256 A, but this run was registered with the program at that path with sha256 B. ":
# for a run registered on the rebuilt route (it may go on with a rebuild) and for a run registered on the pinned route (byte for byte or a new run)
RESUME_NEEDS = ('A resume needs the same program, byte for byte, or a rebuild from the same pinned source whose build record (PROGRAM.build.json, written by rl/strength/build.sh) '
                'has the same engine tree and harness hash and whose two self-checks are replayed again against the committed pin; rebuild with the "rebuild_command" in the '
                "registration's build record (same toolchain, HOME, CARGO_HOME and build folders) to get the same bytes, or register a new run")
RESUME_NEEDS_PINNED = ('A resume needs the same program, byte for byte (this run was registered on the pinned route, which has no build record and no rebuild; only a run registered with '
                       '--program can go on with a rebuild), or a new run')
# what the self-checks are said to be equal to, by the state of the pin (pin_digests): the committed pin's digests, or, for a hand-made pin let through by the test-only variable,
# what it really is
# the variables that make git read another repository, however `git -C repo` is spelled (a git hook or `rebase --exec` exports them): the tests' own list, not the code's
GIT_REPO_VARS = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX')
COMMITTED_DIGESTS = "the committed pin's digests"
FILE_DIGESTS = 'the digests of the pin file in use (NOT the committed pin: test use)'


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def jsonl(path):
    out = []
    if os.path.exists(path):
        for l in read(path).splitlines():
            if l.strip():
                try:
                    out.append(json.loads(l))
                except ValueError:
                    pass
    return out


def chi(y, mo, d, h=0, mi=0):
    return datetime.datetime(y, mo, d, h, mi, tzinfo=CHI)


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def manifest_text_sha256(man):
    """The sha256 of manifest.json as strength_prereg.py writes `man` (indent 1, not ASCII-only, no final newline): the run a 'program_changed' line is written for. A test that
    rewrote the manifest some other way passes the real file's sha256 itself (sha of the file)."""
    return hashlib.sha256(json.dumps(man, indent=1, ensure_ascii=False).encode('utf-8')).hexdigest()


def change_event_for(man, new_sha, record_sha256='e' * 64, **over):
    """A 'program_changed' log event as reverify_program writes it for the run `man` (a manifest registered on the rebuilt route): the program it names, its build record (for that file,
    with the registered engine tree and harness hash, and the sha256 `record_sha256` for the record file) and the self-check texts the run was registered with. `over` replaces entries
    (a value of DROP removes one). Whether the run is on the rebuilt route is up to `man`: the page and the accepted hashes count the event only for a run that is."""
    block = man['slow_report']
    e = {'at': '2026-10-10T10:00:10Z', 'event': 'program_changed', 'pilot': man['pilot'], 'reference': man['reference'], 'old_sha256': man['program_sha256'], 'new_sha256': new_sha,
         'manifest_sha256': manifest_text_sha256(man),
         'build_record': {'schema': 1, 'program_sha256': new_sha, 'engine_tree_archived': block['engine_tree'], 'harness_source_sha256': block['harness_source_sha256'],
                          'record_file': '/x/strength.build.json', 'record_sha256': record_sha256},
         'selfcheck': dict(man['selfcheck']), 'pin_committed': 'bypassed', 'replayed_on': 'cloud-box-2'}
    e.update(over)
    return {k: v for k, v in e.items() if v is not DROP}


def exported_git_variables(tmp, other):
    """The variables that make git read ANOTHER repository (or fail), as a git hook or `rebase --exec` leaves them exported, set to values that send a read to the repository at `other` or to
    a folder in `tmp` that does not exist: {name: value}, one for each of slow_report.GIT_REPO_VARS."""
    return {'GIT_DIR': os.path.join(other, '.git'), 'GIT_WORK_TREE': other, 'GIT_INDEX_FILE': os.path.join(other, '.git', 'index'),
            'GIT_OBJECT_DIRECTORY': os.path.join(tmp, 'no-objects-here'), 'GIT_ALTERNATE_OBJECT_DIRECTORIES': os.path.join(other, '.git', 'objects'),
            'GIT_COMMON_DIR': os.path.join(other, '.git'), 'GIT_NAMESPACE': 'elsewhere', 'GIT_PREFIX': 'sub/'}


def recording_git(tmp):
    """A `git` found before the real one that appends the arguments and the environment of every call to seen.txt (one block per call, ended by a line '--') and prints abc, exit 0. Returns
    (the PATH patch for mock.patch.dict(os.environ, ...), a function that gives the calls so far as [(arguments, {variable: value})])."""
    folder = os.path.join(tmp, 'recording-git')
    os.makedirs(folder, exist_ok=True)
    seen = os.path.join(folder, 'seen.txt')
    write(os.path.join(folder, 'git'), f'#!/bin/sh\n{{ echo "ARGS $*"; env; echo --; }} >> "{seen}"\nprintf abc\nexit 0\n', mode=0o755)

    def calls():
        out = []
        for block in (read(seen) if os.path.exists(seen) else '').split('\n--\n'):
            lines = block.splitlines()
            if lines:
                out.append((lines[0][len('ARGS '):], dict(l.split('=', 1) for l in lines[1:] if '=' in l)))
        return out
    return {'PATH': folder + os.pathsep + os.environ.get('PATH', '')}, calls


def forged_overrides(man, new):
    """(label, entries to replace in change_event_for(man, new)) for the lines of a log that the run could not have written: wrong, missing or foreign build record, other self-check
    texts, no program hash. The log is not covered by manifest.sha256, so none of these may count as a change of the program, or be shown as one."""
    record = change_event_for(man, new)['build_record']
    sc = dict(man['selfcheck'])
    return (('another engine tree', dict(build_record=dict(record, engine_tree_archived='1' * 40))),
            ('no engine tree', dict(build_record={k: v for k, v in record.items() if k != 'engine_tree_archived'})),
            ('another harness source', dict(build_record=dict(record, harness_source_sha256='2' * 64))),
            ('no harness source', dict(build_record={k: v for k, v in record.items() if k != 'harness_source_sha256'})),
            ('a record for another file', dict(build_record=dict(record, program_sha256='3' * 64))),
            ('a record that does not say which file it is for', dict(build_record={k: v for k, v in record.items() if k != 'program_sha256'})),
            ('no record', dict(build_record=DROP)), ('a record that is null', dict(build_record=None)), ('a record that is a list', dict(build_record=[record])),
            ('a record that is text', dict(build_record='the record')),
            ('another km3 self-check text', dict(selfcheck=dict(sc, km3='selfcheck pilot=km3 games=12 digest=0000'))),
            ('another kx3 self-check text', dict(selfcheck=dict(sc, kx3='selfcheck pilot=kx3 games=12 digest=0000'))),
            ('only one self-check', dict(selfcheck={'kx3': sc['kx3']})), ('a self-check more', dict(selfcheck=dict(sc, ext='selfcheck pilot=ext'))),
            ('no self-checks', dict(selfcheck=DROP)), ('empty self-checks', dict(selfcheck={})),
            ('a line written for another run', dict(manifest_sha256='9' * 64)), ('a run that is null', dict(manifest_sha256=None)),
            ('a run that is a number', dict(manifest_sha256=12345)),  # (a line with no manifest_sha256 at all is the format of the earlier version: see the tests of that)
            ('no program hash', dict(new_sha256=DROP)), ('a program hash that is null', dict(new_sha256=None)),
            ('a program hash that is a number', dict(new_sha256=7, build_record=dict(record, program_sha256=7))))


# The synthetic registry of every World: the 8 panel lists and 3 held-out decks are made-up 20-card lists, each with Pokémon ids no other list has and the common Trainer
# cards under their accented printed names (the accents are what an ASCII re-export loses), so no test depends on the real lists.
HELD = ['held-one', 'held-two', 'held-three']
ENERGY_TYPES = ['Fire', 'Water', 'Grass', 'Psychic', 'Fighting', 'Darkness', 'Lightning', 'Metal', 'Dragon']


def synthetic_list(k):
    return (f'Energy: {ENERGY_TYPES[k % len(ENERGY_TYPES)]}\n'
            f'2 Alpha{k} A1 {100 + 4 * k:03d}\n2 Beta{k} A1 {101 + 4 * k:03d}\n2 Gamma{k} B2 {102 + 4 * k:03d}\n1 Delta{k} B3 {103 + 4 * k:03d}\n'
            '2 Poké Ball P-A 005\n1 Pokémon Center Lady A2b 070\n2 Professor\'s Research P-A 007\n1 Cyrus A2 150\n'
            f'7 Filler X1 {k + 2:03d}\n')


PANEL_TEXT = {n: synthetic_list(i) for i, n in enumerate(PANEL)}
HELD_TEXT = {n: synthetic_list(len(PANEL) + i) for i, n in enumerate(HELD)}


class Timed(unittest.TestCase):
    """Every test gets two minutes: a regression that makes the run loop spin or wait must fail the suite, not hang it."""

    def setUp(self):
        def boom(signum, frame):
            raise AssertionError('test timed out after 120 s')
        self._old = signal.signal(signal.SIGALRM, boom)
        signal.alarm(120)

    def tearDown(self):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self._old)


# ---------------------------------------------------------------------------------------------------------- the fake program
FAKE_PROGRAM = r'''#!/usr/bin/env python3
import json, os, sys, time, datetime

def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default

here = os.path.dirname(os.path.abspath(__file__))
watched = ('KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_')
envrec = {k: v for k, v in os.environ.items() if k.startswith(watched) or k in ('PATH', 'HOME', 'RAYON_NUM_THREADS')}
cmd = sys.argv[1]
if cmd == 'selfcheck':
    with open(os.path.join(here, 'selfcheck_env.json'), 'w') as f:
        json.dump(envrec, f)
    print('selfcheck pilot=%s games=12 digest=fakefakefakefake' % arg('--pilot'))
    sys.exit(0)
man = json.load(open(arg('--manifest')))
out = arg('--out')
max_games = int(arg('--max-games', '1000000000'))
stop_after = arg('--stop-after-min')
with open(os.path.join(out, 'fake_calls.jsonl'), 'a') as f:
    f.write(json.dumps({'pid': os.getpid(), 'argv': sys.argv[1:], 'env': envrec}) + '\n')
decks = [(d['name'], d['path']) for d in man['decks']]
opps = [(d['name'], d['path']) for d in man['opponents']]
jobs = []
for di, (dn, _) in enumerate(decks):
    for oi, (on, _) in enumerate(opps):
        if on == dn:
            continue
        pair = di * 1000 + oi
        for deal in range(man['deals']):
            for seat in man['seats']:
                for arm in ('ref', 'X'):
                    jobs.append((dn, on, deal, seat, arm, man['seed_base'] + pair * man['pair_stride'] + deal))
gp = os.path.join(out, 'games.jsonl')
done = set()
if os.path.exists(gp):
    for l in open(gp):
        try:
            done.add(json.loads(l)['key'])
        except Exception:
            pass
todo = [j for j in jobs if '|'.join([j[0], j[1], str(j[2]), str(j[3]), j[4]]) not in done][:max_games]
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
with open(os.path.join(out, 'run_log.jsonl'), 'a') as f:
    f.write(json.dumps({'event': 'start', 'at': now(), 'threads': int(arg('--threads', '2')), 'planned': len(jobs), 'already_done': len(done), 'to_play': len(todo), 'pilot': man['pilot'], 'reference': man['reference']}) + '\n')
t0 = time.time()
played = 0
hang_flag = os.path.join(out, 'hang.flag')
for dn, on, deal, seat, arm, seed in todo:
    if stop_after is not None and time.time() - t0 > float(stop_after) * 60:
        break
    if os.path.exists(hang_flag) and played >= int(open(hang_flag).read().strip() or '0'):
        os.remove(hang_flag)
        with open(os.path.join(out, 'hanging.flag'), 'w') as f:
            f.write(str(os.getpid()))
        time.sleep(3600)  # a game in flight that never finishes
    h = (seed * 7 + seat * 3 + (5 if arm == 'X' else 0)) % 10
    winner = 'deck' if h < 5 else ('tie' if h == 5 else 'opp')
    rec = {'key': '|'.join([dn, on, str(deal), str(seat), arm]), 'deck': dn, 'opp': on, 'deal': deal, 'seat': seat, 'arm': arm, 'seed': seed,
           'pilot_deck': man['pilot'] if arm == 'X' else man['reference'], 'pilot_opp': man['reference'], 'first': 'deck' if seat == 0 else 'opp',
           'winner': winner, 'points': [3, 1], 'turns': 9, 'plies': 40, 'wall_s': 100.0 if arm == 'X' else 1.0,
           'moves_deck': {'n': 2, 'total_s': 0.02, 'ms': [10.0, 10.0]}, 'moves_opp': {'n': 1, 'total_s': 0.01, 'ms': [10.0]}, 'started_at': now()}
    with open(gp, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    played += 1
with open(os.path.join(out, 'run_log.jsonl'), 'a') as f:
    f.write(json.dumps({'event': 'stop', 'at': now(), 'played': played, 'elapsed_s': time.time() - t0}) + '\n')
'''

HANG_PROGRAM = '#!/usr/bin/env python3\nimport sys, time\nif sys.argv[1] == "run":\n    time.sleep(3600)\n'

DECK_TEXT = "Energy: Fire\n2 Torchic B1 033\n2 Combusken B1 034\n16 Filler X1 002\n"
_IN_SLOT = {}


def deck_text_in_slot(slot):
    """A deck text (not one of the panel lists) whose sha256 puts it in this seed slot: the first 8 hex digits of the file's sha256, modulo the number of slots, is the slot
    the deck gets (found by trying other set codes for the Filler card; about a thousand tries)."""
    slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
    if slot not in _IN_SLOT:
        for n in range(1, 500_000):
            text = f'Energy: Fire\n2 Torchic B1 033\n2 Combusken B1 034\n16 Filler Z{n} 002\n'
            if int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) % slots == slot:
                _IN_SLOT[slot] = text
                break
        else:
            raise AssertionError(f'no deck text lands in slot {slot}')
    return _IN_SLOT[slot]


class FakeClock:
    """A controllable local clock: now() is a timezone-aware time in America/Chicago, sleep() moves it forward (and barely waits)."""

    def __init__(self, start):
        self.t = start
        self.slept = []
        self.gate = None  # optional: a callable that must be true before the clock may pass `gate_until`
        self.gate_until = None

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        new = (self.t.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)).astimezone(CHI)
        if self.gate is not None and self.gate_until is not None and new >= self.gate_until:
            deadline = time.time() + 60
            while not self.gate() and time.time() < deadline:
                time.sleep(0.01)
        self.t = new
        time.sleep(min(0.05, seconds / 5000.0))


class World(Timed):
    """A temporary repository with its own synthetic registry (the 8 panel lists, PANEL_TEXT, and 3 held-out decks, HELD_TEXT, at the paths its decks.json names), one deck
    of his, a copy of strength_prereg.py beside synthetic decks.json / groups.json / heldout.json (slow_report.HERE and PREREG point at that folder, self.harness, while
    the test runs), a fake pinned program and a pin that names it. Subclasses call self.make(...). self.registry maps a deck name to its path in self.repo.

    What still reads live data: the pin (the template of every test pin), and, only to lay out placeholder files, the NAMES and PATHS (never the content) of the real
    registry. The placeholders exist for the tests that start the real script in a subprocess to register a new run: that process reads the real registry beside the
    real script, and finds the real panel and held-out files at their real paths, with made-up lists in them. A test that wants the real registry and the real lists
    in-process uses LiveWorld."""

    def lay_out_registry(self):
        self.registry = {n: f'decks/screen/opponents/{n}.txt' for n in PANEL}
        self.registry.update({n: f'decks/dustin/{n}.txt' for n in HELD})
        for n, text in list(PANEL_TEXT.items()) + list(HELD_TEXT.items()):
            write(os.path.join(self.repo, *self.registry[n].split('/')), text)
        template = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        try:  # placeholders at the paths the REAL registry names (see the class docstring); the synthetic files above win where the paths are the same
            live = json.loads(read(os.path.join(HERE, 'decks.json')))['decks']
            names = json.loads(read(os.path.join(HERE, 'groups.json')))[template['panel_group']] + json.loads(read(os.path.join(HERE, 'heldout.json')))['decks']
            for i, n in enumerate(names):
                if n in live and not os.path.exists(os.path.join(self.repo, *live[n].split('/'))):
                    write(os.path.join(self.repo, *live[n].split('/')), synthetic_list(50 + i))
        except (OSError, KeyError, ValueError):
            pass  # a convenience for subprocess tests: the fixture never fails because the real registry looks different
        # strength_prereg.py reads decks.json, groups.json and heldout.json beside itself, and hashes every held-out deck's file (the content guard)
        write(os.path.join(self.harness, 'decks.json'), json.dumps({'decks': self.registry}))
        write(os.path.join(self.harness, 'groups.json'), json.dumps({template['panel_group']: PANEL}))
        write(os.path.join(self.harness, 'heldout.json'), json.dumps({'locked': True, 'unlocked_by': None, 'decks': HELD}))
        shutil.copy(os.path.join(HERE, 'strength_prereg.py'), os.path.join(self.harness, 'strength_prereg.py'))
        patch = mock.patch.multiple(sr, HERE=self.harness, PREREG=os.path.join(self.harness, 'strength_prereg.py'))
        patch.start()
        self.addCleanup(patch.stop)

    def make(self, deck_text=DECK_TEXT, deck_name='my-list'):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = os.path.join(self.tmp, 'repo')
        self.harness = os.path.join(self.tmp, 'harness')
        self.lay_out_registry()
        self.deck_rel = f'decks/events/{deck_name}.txt'
        self.deck = os.path.join(self.repo, *self.deck_rel.split('/'))
        write(self.deck, deck_text)
        self.program = os.path.join(self.tmp, 'fake_kx3_strength')
        write(self.program, FAKE_PROGRAM, mode=0o755)
        pin = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        pin['program'] = self.program
        pin['program_sha256'] = pin['selfcheck_measured_on_sha256'] = sha(self.program)  # the fake program is "the pinned binary" the self-check texts were measured on
        self.pin_path = os.path.join(self.tmp, 'pin.json')
        write(self.pin_path, json.dumps(pin, indent=1))
        self.pin = pin
        self.out_root = os.path.join(self.repo, 'rl', 'results', 'slow_reports')
        self.clock = FakeClock(chi(2026, 10, 10, 10, 0))  # a Saturday morning: nothing blocks
        return self

    def setUp(self):
        super().setUp()
        old = dict(sr._LOG_EXTRA)  # a process-wide dict the log events draw their pilot names from: every test starts from an empty one
        sr._LOG_EXTRA.clear()
        self.addCleanup(lambda: (sr._LOG_EXTRA.clear(), sr._LOG_EXTRA.update(old)))
        # a hand-made pin in a temporary folder (and a temporary repository with no commit of it) is not the committed pin: the test-only variable lets it through, and the
        # tests of the committed-pin check itself (CommittedPin) take it away again. The subprocesses these tests start inherit it.
        env = mock.patch.dict(os.environ, {ALLOW_PIN_VAR: '1'})
        env.start()
        self.addCleanup(env.stop)
        self.make()

    def set_program(self, text):
        write(self.program, text, mode=0o755)
        pin = json.loads(read(self.pin_path))
        pin['program_sha256'] = pin['selfcheck_measured_on_sha256'] = sha(self.program)
        write(self.pin_path, json.dumps(pin))

    def argv(self, *extra, deck=True, school='off', date=True):
        """The command line: the deck (or none, for --dir), the temporary repository and pin, the school rule ('off', 'on' or None for the default)."""
        a = [self.deck] if deck else []
        a += ['--repo', self.repo, '--pin', self.pin_path, '--poll-s', '1']
        if deck:
            a += ['--out-root', self.out_root]
            if date:
                a += ['--date', '2026-10-10']
        if school is not None:
            a += ['--school-rule', school]
        return a + list(extra)

    def cli(self, *extra, deck=True, school='off', spawn=None, deck_check=lambda p, r: [], date=True):
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sr.main(self.argv(*extra, deck=deck, school=school, date=date), now=self.clock.now, sleep=self.clock.sleep, spawn=spawn, deck_check=deck_check)
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def cli_path(self, path, *extra, school='off'):
        """Like cli() for a deck file given by its path (anywhere: a symlink, a file outside the repository), with the same repository, pin, out-root and date."""
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sr.main([path] + self.argv(deck=False, school=school) + ['--out-root', self.out_root, '--date', '2026-10-10'] + list(extra),
                               now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def rundir(self, name='2026-10-10_my-list'):
        return os.path.join(self.out_root, name)

    def register(self, *extra, school='off'):
        """Register (only) the deck with one deal. school is the --school-rule given ('off' by default, so a registered run does not pause for school mornings; None gives
        no option at all, which registers the default: the rule on, Monday to Friday)."""
        code, out, err = self.cli('--deals', '1', '--register-only', *extra, school=school)
        self.assertEqual(code, 0, out + err)
        return self.rundir()

    def without_tzdata(self):
        """zoneinfo.ZoneInfo fails the way it does on a machine with no time zone database, and the zone cached by earlier tests is forgotten (and put back at the end).
        Returns the list of keys asked for."""
        asked = []

        def missing(key, *a, **kw):
            asked.append(key)
            raise zoneinfo.ZoneInfoNotFoundError(f'No time zone found with key {key}')
        old = dict(sr._TZ)
        sr._TZ.clear()
        self.addCleanup(lambda: (sr._TZ.clear(), sr._TZ.update(old)))
        patcher = mock.patch.object(zoneinfo, 'ZoneInfo', missing)
        patcher.start()
        self.addCleanup(patcher.stop)
        return asked


class LiveWorld(World):
    """The first version of the fixture, for the few tests whose point is the real data: slow_report.HERE is not changed, so the real decks.json, groups.json and
    heldout.json are the registry, and the temporary repository holds copies of the real panel lists and the real held-out decks (read from ROOT). Such a test breaks
    when the real lists or the registry change, which is what it is for."""

    def lay_out_registry(self):
        self.harness = HERE
        self.registry = json.loads(read(os.path.join(HERE, 'decks.json')))['decks']
        panel = json.loads(read(os.path.join(HERE, 'groups.json')))[json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))['panel_group']]
        for n in panel + json.loads(read(os.path.join(HERE, 'heldout.json')))['decks']:
            write(os.path.join(self.repo, *self.registry[n].split('/')), read(os.path.join(ROOT, *self.registry[n].split('/'))))


# ---------------------------------------------------------------------------------------------------------- the pin
class Pin(World):
    def test_the_committed_pin_names_the_frozen_program(self):
        pin = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        self.assertEqual(pin['pilot'], 'kx3')
        self.assertEqual(pin['reference'], 'km3')
        self.assertEqual(pin['program'], '/home/dacz8976/kx/strength')
        self.assertEqual(pin['program_sha256'], '5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2')
        self.assertIn('digest=31d638dbc818b0fa', pin['selfcheck']['kx3'])
        self.assertIn('digest=81b572198c04d5d1', pin['selfcheck']['km3'])
        self.assertIn('d513e37b', pin['pilot_label'])
        self.assertEqual(pin['panel_group'], 'panel8')
        self.assertEqual(pin['seed_block'], list(BLOCK))
        self.assertEqual(pin['seed_step'], STEP)
        self.assertEqual(pin['threads'], 2)
        self.assertEqual(pin['games_per_hour'], {'typical_low': 26, 'typical_high': 34, 'wall': 9})

    def test_the_pin_scrubs_every_prefix_the_frozen_engine_can_read(self):
        pin = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        self.assertEqual(sorted(pin['scrub_env_prefixes']), ['DECKGYM_', 'JEV_', 'KX_', 'PDL_', 'PG_'])

    def test_a_program_that_is_not_the_pinned_build_is_refused_before_anything_is_written(self):
        write(self.program, FAKE_PROGRAM + '\n# changed\n', mode=0o755)
        code, out, err = self.cli()
        self.assertNotEqual(code, 0)
        self.assertIn('pinned', str(code) + err)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_missing_program_is_refused(self):
        os.remove(self.program)
        code, out, err = self.cli()
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(self.out_root))

    def test_what_the_self_checks_are_equal_to_is_the_committed_pins_digests_unless_the_pin_was_let_through_for_a_test(self):
        """pin_digests(state): the words every place that names the pin's digests uses. A pin that is not the committed one (let through by the test-only variable) is described as what
        it is, so a report made on one never claims the committed pin."""
        self.assertEqual(sr.pin_digests('yes'), COMMITTED_DIGESTS)
        for state in (None, 'bypassed', 'no', '', 'something else'):
            self.assertEqual(sr.pin_digests(state), FILE_DIGESTS, f'{state!r}: only a state of "yes" is the committed pin; a state that is missing is not recorded as committed')
        self.assertEqual(FILE_DIGESTS, 'the digests of the pin file in use (NOT the committed pin: test use)')

    def test_how_a_self_check_text_was_obtained_follows_the_state_of_the_pin_too(self):
        committed = {'given in the config (copied from the pin, which says it was measured on this exact program sha256)': 'copied from the pin, not replayed: the pin says it was measured on this exact binary',
                     'given anyhow': 'copied from the pin, not replayed: the pin says it was measured on this exact binary',
                     'replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)':
                         'replayed on the registering machine just before registration, equal to the committed pin',
                     'run by strength_prereg.py': 'replayed at registration', 'something else': 'recorded at registration', '': 'recorded at registration', None: 'recorded at registration'}
        for source, how in committed.items():
            self.assertEqual(sr.selfcheck_how(source, 'yes'), how, (source, 'yes'))
        for state in ('bypassed', 'no', None, '', 'maybe'):  # (a state that is missing, or none of the known ones, is not "yes": the committed pin is claimed only of a pin recorded as committed)
            for source, how in committed.items():
                want = 'replayed on the registering machine just before registration, equal to the pin file in use (NOT the committed pin: test use)' if (source or '').startswith('replayed by') else how
                self.assertEqual(sr.selfcheck_how(source, state), want, (source, state))


# ---------------------------------------------------------------------------------------------------------- seeds
class Seeds(Timed):
    def test_the_seed_base_is_in_the_block_aligned_and_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            a = sr.pick_seed_base('ab' * 32, t, BLOCK, STEP)
            self.assertEqual(a, sr.pick_seed_base('ab' * 32, t, BLOCK, STEP))
            self.assertTrue(BLOCK[0] <= a and a + 9 * 10_000 + 9_999 <= BLOCK[1])
            self.assertEqual((a - BLOCK[0]) % STEP, 0)

    def test_the_slot_comes_from_the_decks_sha256(self):
        with tempfile.TemporaryDirectory() as t:
            slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
            self.assertEqual(slots, 990)
            for hexhead in ('00000000', '00000001', '000003de', '000003df', 'ffffffff'):
                self.assertEqual(sr.pick_seed_base(hexhead + '0' * 56, t, BLOCK, STEP), BLOCK[0] + (int(hexhead, 16) % slots) * STEP)

    def test_a_slot_another_report_took_is_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            first = sr.pick_seed_base('00000001' + '0' * 56, t, BLOCK, STEP)
            os.makedirs(os.path.join(t, 'older'))
            write(os.path.join(t, 'older', 'manifest.json'), json.dumps({'seed_base': first}))
            second = sr.pick_seed_base('00000001' + '0' * 56, t, BLOCK, STEP)
            self.assertEqual(second, first + STEP)

    def test_an_explicit_base_must_be_in_the_block_and_on_a_slot_boundary(self):
        with tempfile.TemporaryDirectory() as t:
            ok = BLOCK[0] + 5 * STEP
            self.assertEqual(sr.pick_seed_base('ab' * 32, t, BLOCK, STEP, explicit=ok), ok)
            for bad in (BLOCK[0] - 1, BLOCK[0] - STEP, 24_700_000_000, 24_400_000_000, BLOCK[1] - 1000, ok + 50_000, ok + 1, 24_600_000_000):
                with self.assertRaises(SystemExit, msg=str(bad)):
                    sr.pick_seed_base('ab' * 32, t, BLOCK, STEP, explicit=bad)

    # (the check that START_HERE.md records the block reads a live document, so it lives in LiveRepositoryData, test_slow_report_registration.py)


# ---------------------------------------------------------------------------------------------------------- the school-morning rule
class SchoolRule(Timed):
    def act(self, *a, **kw):
        return sr.school_action(chi(*a), **kw)

    def test_every_weekday_evening_runs_to_the_next_school_morning(self):
        days = {6: 7, 7: 8, 8: 9, 9: 12}  # Tue->Wed, Wed->Thu, Thu->Fri, Fri->Mon of Oct 2026 (the 5th is a Monday)
        for d, nxt in {5: 6, 6: 7, 7: 8, 8: 9, 9: 12}.items():
            a = self.act(2026, 10, d, 20, 0)
            self.assertEqual(a['kind'], 'run', d)
            self.assertEqual(a['hard_stop'], chi(2026, 10, nxt, 6, 30), d)
            gap_days = nxt - d
            self.assertEqual(a['stop_after_min'], (gap_days * 24 - 20) * 60 + 5 * 60 + 15, d)

    def test_every_weekday_between_515_and_5pm_waits_for_5pm(self):
        for d in (5, 6, 7, 8, 9):
            for h, m in ((5, 15), (5, 20), (6, 29), (6, 30), (9, 0), (12, 0), (16, 59)):
                a = self.act(2026, 10, d, h, m)
                self.assertEqual(a['kind'], 'wait', (d, h, m))
                self.assertEqual(a['until'], chi(2026, 10, d, 17, 0))

    def test_every_weekday_at_5pm_runs_again(self):
        for d, nxt in {5: 6, 6: 7, 7: 8, 8: 9}.items():
            a = self.act(2026, 10, d, 17, 0)
            self.assertEqual(a['kind'], 'run', d)
            self.assertEqual(a['stop_after_min'], 12 * 60 + 15)
            self.assertEqual(a['hard_stop'], chi(2026, 10, nxt, 6, 30))

    def test_five_minutes_before_the_cut_it_still_starts(self):
        a = self.act(2026, 10, 7, 5, 10)
        self.assertEqual(a['kind'], 'run')
        self.assertAlmostEqual(a['stop_after_min'], 5.0)
        self.assertEqual(a['hard_stop'], chi(2026, 10, 7, 6, 30))

    def test_every_weekday_before_dawn_stops_at_that_mornings_515(self):
        for d in (5, 6, 7, 8, 9):
            a = self.act(2026, 10, d, 4, 0)
            self.assertEqual(a['kind'], 'run', d)
            self.assertEqual(a['stop_after_min'], 75, d)
            self.assertEqual(a['hard_stop'], chi(2026, 10, d, 6, 30))

    def test_friday_evening_runs_through_the_weekend_to_monday_515(self):
        a = self.act(2026, 10, 9, 18, 0)
        self.assertEqual(a['kind'], 'run')
        self.assertEqual(a['stop_after_min'], (2 * 24 + 11) * 60 + 15)
        self.assertEqual(a['hard_stop'], chi(2026, 10, 12, 6, 30))

    def test_saturday_and_sunday_run_without_a_wait(self):
        for d, h in ((10, 10), (11, 5), (11, 12), (10, 6), (11, 23)):
            a = self.act(2026, 10, d, h, 0)
            self.assertEqual(a['kind'], 'run', (d, h))
            self.assertEqual(a['hard_stop'], chi(2026, 10, 12, 6, 30))

    def test_clock_change_is_counted_in_real_minutes(self):
        a = self.act(2026, 10, 31, 23, 0)  # the clocks go back on Sunday Nov 1: 30 h 15 min on the wall, 31 h 15 min really
        self.assertEqual(a['stop_after_min'], 30 * 60 + 15 + 60)
        self.assertEqual(a['hard_stop'], chi(2026, 11, 2, 6, 30))
        b = self.act(2027, 3, 13, 23, 0)  # and forward on Sunday Mar 14, 2027: one hour less
        self.assertEqual(b['stop_after_min'], 30 * 60 + 15 - 60)

    def test_a_utc_clock_is_read_as_local_time(self):
        utc = chi(2026, 10, 7, 5, 20).astimezone(datetime.timezone.utc)
        self.assertEqual(sr.school_action(utc)['kind'], 'wait')

    def test_custom_school_days(self):
        a = sr.school_action(chi(2026, 10, 7, 9, 0), school_days=(0, 1, 3, 4))  # no school on Wednesdays
        self.assertEqual(a['kind'], 'run')
        self.assertEqual(a['hard_stop'], chi(2026, 10, 8, 6, 30))

    def test_no_school_days_means_no_limit(self):
        self.assertEqual(sr.school_action(chi(2026, 10, 7, 9, 0), school_days=()), {'kind': 'run', 'stop_after_min': None, 'hard_stop': None})

    def test_school_days_are_parsed_by_name(self):
        self.assertEqual(sr.parse_days('mon,wed'), (0, 2))
        self.assertEqual(sr.parse_days(' Mon , FRI '), (0, 4))
        self.assertEqual(sr.parse_days(''), ())
        with self.assertRaises(SystemExit):
            sr.parse_days('mon,funday')

    def test_the_defaults_are_the_rule_as_run5_states_it(self):
        self.assertEqual(sr.SCHOOL_DAYS, (0, 1, 2, 3, 4))
        self.assertEqual((sr.SOFT_STOP, sr.HARD_STOP, sr.RESUME), ((5, 15), (6, 30), (17, 0)))
        self.assertEqual(str(sr.CHICAGO), 'America/Chicago')


# ---------------------------------------------------------------------------------------------------------- environment
class Environment(World):
    def test_scrub_removes_every_tuning_prefix_and_keeps_the_rest(self):
        env = {'PATH': '/bin', 'HOME': '/h', 'KX_EXTRA_LISTS': 'x=/y', 'KX_TRACE': '1', 'DECKGYM_UNBOUNDED_ENERGY_MOVES': '1', 'PDL_EQUIV_DEALS': '3',
               'PG_DUMP': '/tmp/z', 'JEV_MODEL': 'm', 'RAYON_NUM_THREADS': '4', 'PGDATA_NOT_OURS': 'kept'}
        clean, removed = sr.scrub_env(env, ['KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_'])
        self.assertEqual(sorted(clean), ['HOME', 'PATH', 'PGDATA_NOT_OURS', 'RAYON_NUM_THREADS'], 'a prefix is a prefix: PGDATA_ does not start with PG_')
        self.assertEqual(removed, ['DECKGYM_UNBOUNDED_ENERGY_MOVES', 'JEV_MODEL', 'KX_EXTRA_LISTS', 'KX_TRACE', 'PDL_EQUIV_DEALS', 'PG_DUMP'])
        self.assertEqual(env['KX_EXTRA_LISTS'], 'x=/y', "the caller's environment is not modified")
        for prefix in ('KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_'):
            c, r = sr.scrub_env({'PATH': '/bin', prefix + 'X': '1'}, [prefix])
            self.assertEqual((sorted(c), r), (['PATH'], [prefix + 'X']), prefix)

    def with_env(self, **kw):
        old = {k: os.environ.get(k) for k in kw}
        os.environ.update(kw)

        def restore():
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.addCleanup(restore)

    def test_the_program_never_sees_a_tuning_variable_of_any_prefix(self):
        names = {'KX_EXTRA_LISTS': 'sneaky=/tmp/my-list.txt', 'DECKGYM_UNBOUNDED_ENERGY_MOVES': '1', 'PDL_EQUIV_DEALS': '3', 'JEV_MODEL': 'x', 'PG_DUMP': '/tmp/d'}
        self.with_env(**names)
        code, out, err = self.cli('--deals', '1', '--max-games', '4')
        self.assertEqual(code, 0, err)
        calls = jsonl(os.path.join(self.rundir(), 'fake_calls.jsonl'))
        self.assertTrue(calls)
        for c in calls:
            for k in names:
                self.assertNotIn(k, c['env'])
            self.assertIn('PATH', c['env'])
        scrubbed = [e for e in jsonl(os.path.join(self.rundir(), 'slow_report_log.jsonl')) if e['event'] == 'env_scrubbed']
        self.assertTrue(scrubbed)
        self.assertEqual(sorted(set(names) & set(scrubbed[0]['names'])), sorted(names))

    def test_the_self_check_replay_is_scrubbed_too(self):
        self.with_env(KX_EXTRA_LISTS='sneaky=/tmp/x.txt')
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)  # the fake's digest differs from the real pin's: refused, but the program was run
        seen = json.loads(read(os.path.join(self.tmp, 'selfcheck_env.json')))
        self.assertNotIn('KX_EXTRA_LISTS', seen)

    def test_the_registered_scrub_list_is_used_when_the_pin_changes_later(self):
        self.with_env(KX_EXTRA_LISTS='sneaky=/tmp/x.txt')
        d = self.register()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['scrub_env_prefixes'], ['KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_'])
        pin = json.loads(read(self.pin_path))
        pin['scrub_env_prefixes'] = []  # a later pin that (wrongly) scrubs nothing
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False)
        self.assertEqual(code, 0, err + out)
        for c in jsonl(os.path.join(d, 'fake_calls.jsonl')):
            self.assertNotIn('KX_EXTRA_LISTS', c['env'], 'the run was registered with the full scrub list; a changed pin file must not weaken it')


# ---------------------------------------------------------------------------------------------------------- the deck
class Deck(World):
    def test_the_name_is_the_file_stem(self):
        self.assertEqual(sr.deck_name_of('/x/decks/events/my-list.txt'), 'my-list')

    def test_a_name_that_is_not_filename_safe_is_refused(self):
        for bad in ('my list (v2).txt', '.hidden.txt', '-dash.txt', 'a;b.txt'):
            with self.assertRaises(SystemExit, msg=bad):
                sr.deck_name_of('/x/decks/events/' + bad)

    def test_a_panel_name_is_refused_for_his_deck(self):
        self.make(deck_name='t-altaria')
        code, out, err = self.cli()
        self.assertNotEqual(code, 0)
        self.assertIn('t-altaria', str(code) + err)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_copy_of_a_panel_list_under_another_name_is_refused(self):
        self.make(deck_text=PANEL_TEXT['t-lucario'].replace('\n', '\r\n'), deck_name='my-lucario')
        code, out, err = self.cli()
        self.assertNotEqual(code, 0)
        self.assertIn('t-lucario', str(code) + err)
        self.assertIn('public', str(code) + err)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_deck_outside_the_repository_is_refused_and_nothing_is_written(self):
        outside = os.path.join(self.tmp, 'elsewhere', 'my-list.txt')
        write(outside, DECK_TEXT)
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                sr.main([outside] + self.argv(deck=False, school='off') + ['--out-root', self.out_root, '--date', '2026-10-10'], now=self.clock.now, sleep=self.clock.sleep,
                        deck_check=lambda p, r: [])
        self.assertIn('inside the repository', str(cm.exception.code) + err.getvalue())
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_symlink_that_leaves_the_repository_is_refused(self):
        outside = os.path.join(self.tmp, 'elsewhere', 'real.txt')
        write(outside, DECK_TEXT)
        link = os.path.join(self.repo, 'decks', 'events', 'sneaky.txt')
        os.symlink(outside, link)
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                sr.main([link] + self.argv(deck=False, school='off') + ['--out-root', self.out_root, '--date', '2026-10-10'], now=self.clock.now, sleep=self.clock.sleep,
                        deck_check=lambda p, r: [])
        self.assertIn('inside the repository', str(cm.exception.code) + err.getvalue())
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_bad_deck_is_refused_by_the_real_validator_before_anything_is_written(self):
        self.make(deck_text="Energy: Fire\n2 Torchic B1 033\n")  # 2 cards, not 20
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                sr.main([self.deck, '--repo', ROOT, '--pin', self.pin_path, '--out-root', self.out_root, '--date', '2026-10-10', '--school-rule', 'off'],
                        now=self.clock.now, sleep=self.clock.sleep)
        self.assertIn('20', str(cm.exception.code) + err.getvalue())
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_real_validator_accepts_a_real_deck_of_his(self):
        """Live data on purpose: the first of his registered lists, found through the real decks.json and groups.json, checked by the real lib/deck_check.py."""
        registry = json.loads(read(os.path.join(HERE, 'decks.json')))['decks']
        first = json.loads(read(os.path.join(HERE, 'groups.json')))['dustin_all'][0]
        self.assertEqual(sr.default_deck_check(os.path.join(ROOT, *registry[first].split('/')), ROOT), [])

    def test_a_missing_validator_is_an_error_not_a_skip(self):
        errs = sr.default_deck_check(os.path.join(self.tmp, 'x.txt'), self.tmp)
        self.assertTrue(errs and 'deck_check' in errs[0])

    def test_deck_state_is_committed_changed_or_unknown(self):
        repo = os.path.join(self.tmp, 'r')
        os.makedirs(repo)
        f = os.path.join(repo, 'a.txt')
        write(f, 'x\n')
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'unknown (not a git repository)')
        g = ['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t']
        subprocess.run(g + ['init', '-q'], check=True)
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'not committed')
        subprocess.run(g + ['add', 'a.txt'], check=True)
        subprocess.run(g + ['commit', '-q', '-m', 'x'], check=True)
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'committed')
        write(f, 'y\n')
        self.assertEqual(sr.deck_state(repo, 'a.txt'), 'not committed')


# ---------------------------------------------------------------------------------------------------------- the config
class Config(World):
    def cfg(self, **kw):
        pin = json.loads(read(self.pin_path))
        args = dict(pin=pin, pin_path=self.pin_path, deck_rel=self.deck_rel, deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=5, paired=True,
                    seed_base=BLOCK[0], threads=2, program_sha=pin['program_sha256'], resume_command='python3 rl/strength/slow_report.py --dir X')
        args.update(kw)
        return pin, sr.build_config(**args)

    def test_the_config_follows_the_plan(self):
        pin, cfg = self.cfg()
        self.assertEqual(cfg['stage'], 'use')
        self.assertEqual((cfg['pilot'], cfg['reference']), ('kx3', 'km3'))
        self.assertEqual(cfg['deck_files'], [self.deck_rel])
        self.assertEqual(cfg.get('decks', []), [])
        self.assertEqual(cfg['opponent_groups'], ['panel8'])
        self.assertEqual((cfg['deals'], cfg['seats'], cfg['seed_base'], cfg['pair_stride'], cfg['threads']), (5, [0, 1], BLOCK[0], 10_000, 2))
        self.assertEqual((cfg['program'], cfg['program_sha256']), (pin['program'], pin['program_sha256']))
        self.assertEqual(cfg['selfcheck_given'], pin['selfcheck'])
        self.assertEqual(cfg['engine'], pin['engine'])
        block = cfg['slow_report']
        self.assertEqual(block['paired'], True)
        self.assertEqual(block['headline'], 'kx3 (d513e37b) on my-list v km3 on the public panel')
        self.assertEqual(block['scrub_env_prefixes'], pin['scrub_env_prefixes'])
        self.assertEqual(block['resume_command'], 'python3 rl/strength/slow_report.py --dir X')
        self.assertTrue(block['pin']['sha256'])
        for word in ('kx3', 'km3'):
            self.assertIn(word, cfg['question'])

    def test_the_question_is_precise_about_what_kx3_knows(self):
        pin, cfg = self.cfg()
        q = cfg['question']
        self.assertNotIn('never told', q)
        self.assertIn('knowing its own cards', q)
        self.assertIn('no pass or fail', q.lower())
        self.assertNotRegex(q.lower().replace('no pass or fail', ''), r'\bpass\b|\bfail\b')

    def test_the_names_come_from_the_pin_not_from_literals(self):
        pin = json.loads(read(self.pin_path))
        pin.update(pilot='kz9', reference='kr1', pilot_label='kz9 (abc)', reference_label='kr1')
        cfg = sr.build_config(pin=pin, pin_path=self.pin_path, deck_rel=self.deck_rel, deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=5, paired=False,
                              seed_base=BLOCK[0], threads=2, program_sha=pin['program_sha256'])
        self.assertEqual((cfg['pilot'], cfg['reference']), ('kz9', 'kr1'))
        self.assertIn('kz9', cfg['question'])
        self.assertNotIn('kx3', cfg['question'])
        self.assertNotIn('km3', cfg['question'])
        self.assertEqual(cfg['slow_report']['headline'], 'kz9 (abc) on my-list v kr1 on the public panel')

    def test_selfcheck_how_is_recorded_and_the_text_is_not_given_when_it_is_to_be_run(self):
        pin, cfg = self.cfg(selfcheck_given=None)
        self.assertNotIn('selfcheck_given', cfg)
        pin, cfg = self.cfg(selfcheck_given=dict(self.pin['selfcheck']), selfcheck_how='replayed')
        self.assertEqual(cfg['selfcheck_how'], 'replayed')

    def test_expected_time_follows_the_plans_measured_rates(self):
        pin = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        e = sr.expected_time(5, pin)
        self.assertEqual(e['kx3_games'], 80)
        self.assertAlmostEqual(e['typical_hours'][0], 80 / 34)
        self.assertAlmostEqual(e['typical_hours'][1], 80 / 26)
        self.assertAlmostEqual(e['wall_hours'], 80 / 9)
        self.assertEqual(sr.expected_time(10, pin)['kx3_games'], 160)


# ---------------------------------------------------------------------------------------------------------- registration and the run, end to end with the fake program
class RegisterAndRun(World):
    def test_a_full_report_end_to_end(self):
        code, out, err = self.cli('--deals', '2')
        self.assertEqual(code, 0, err + out)
        d = self.rundir()
        for n in ('config.json', 'manifest.json', 'manifest.sha256', 'PREREGISTRATION.md', 'games.jsonl', 'SLOW_REPORT.md', 'REPORT.md', 'slow_report_log.jsonl', 'run_log.jsonl'):
            self.assertTrue(os.path.exists(os.path.join(d, n)), n)
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual(man['stage'], 'use')
        self.assertEqual([x['name'] for x in man['decks']], ['my-list'])
        self.assertEqual([x['name'] for x in man['opponents']], PANEL)
        self.assertEqual(man['planned_games'], 8 * 2 * 2 * 2)
        self.assertEqual((man['pilot'], man['reference']), ('kx3', 'km3'))
        self.assertTrue(BLOCK[0] <= man['seed_base'] <= BLOCK[1])
        self.assertEqual(man['program_sha256'], self.pin['program_sha256'])
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'])
        self.assertEqual(man['selfcheck_source']['kx3'], 'given in the config (copied from the pin, which says it was measured on this exact program sha256)')
        self.assertEqual((man['program'], man['slow_report']['program_route']), (self.program, 'pinned'))
        self.assertEqual((man['slow_report']['school_rule'], man['slow_report']['school_days']), ('off', 'mon,tue,wed,thu,fri'))
        games = jsonl(os.path.join(d, 'games.jsonl'))
        self.assertEqual(len(games), 64)
        self.assertEqual({g['arm'] for g in games}, {'X', 'ref'})
        self.assertEqual({g['pilot_deck'] for g in games if g['arm'] == 'X'}, {'kx3'})
        self.assertEqual({g['pilot_opp'] for g in games}, {'km3'})
        self.assertEqual(man['slow_report']['deck_file'], self.deck_rel)
        self.assertEqual(man['slow_report']['deck_file_sha256'], sha(self.deck))
        self.assertEqual(man['slow_report']['resume_command'], f'python3 rl/strength/slow_report.py --dir {d} --school-rule off', 'a run registered with the rule off resumes with it off')
        self.assertIn('REPORT.md', read(os.path.join(d, 'SLOW_REPORT.md')))
        rep = json.loads(read(os.path.join(d, 'report.json')))
        self.assertEqual((rep['pilot'], rep['reference']), ('kx3', 'km3'))
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'the lock is released when the run ends')

    def test_registration_comes_before_any_game(self):
        d = self.register()
        self.assertTrue(os.path.exists(os.path.join(d, 'manifest.json')))
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))
        self.assertFalse(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')))
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertNotEqual(code, 0, 'the same run directory is never registered twice')

    def test_a_second_registration_of_the_same_deck_and_day_is_refused_and_changes_nothing(self):
        self.assertEqual(self.cli('--deals', '1')[0], 0)
        before = read(os.path.join(self.rundir(), 'manifest.json'))
        code, out, err = self.cli('--deals', '1')
        self.assertNotEqual(code, 0)
        self.assertIn('exists', str(code) + err)
        self.assertEqual(read(os.path.join(self.rundir(), 'manifest.json')), before)

    def test_dry_run_writes_nothing_and_prints_the_plan_and_the_expected_time(self):
        code, out, err = self.cli('--deals', '5', '--dry-run', school=None)
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.exists(self.out_root))
        self.assertIn('80 kx3 games', out)
        self.assertIn('hours', out)
        self.assertIn('my-list', out)
        self.assertIn('5 deals', out)
        self.assertIn('on school days (mon,tue,wed,thu,fri) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer', out,
                      'the plan names the school days and says that the calendar time is longer on them')
        self.assertNotIn('OFF for this run', out)

    def test_dry_run_with_the_rule_off_says_so_and_that_the_choice_is_recorded(self):
        code, out, err = self.cli('--deals', '5', '--dry-run', school='off')
        self.assertEqual(code, 0, err)
        self.assertIn('school-morning rule: OFF for this run (it never pauses for school mornings; the choice is recorded in the registration and carried by the resume command)', out)
        self.assertNotIn('on school days the run pauses', out)
        self.assertFalse(os.path.exists(self.out_root))

    def test_resume_continues_a_stopped_run_without_repeating_games(self):
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, err + out)
        d = self.rundir()
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 10)
        self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')), 'a run stopped early still leaves a page, marked as partial')
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, err + out)
        games = jsonl(os.path.join(d, 'games.jsonl'))
        self.assertEqual(len(games), 64)
        self.assertEqual(len({g['key'] for g in games}), 64, 'no game is played twice')
        self.assertNotIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')))
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 64, 'a finished run just rewrites the page')

    def test_resume_refuses_a_manifest_that_is_not_the_registered_file(self):
        d = self.register()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        man['deals'] = 1000
        write(os.path.join(d, 'manifest.json'), json.dumps(man, indent=1))
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('registered', str(code) + err)
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))

    def test_resume_refuses_a_missing_or_empty_manifest_sha256(self):
        for how in ('missing', 'empty'):
            with self.subTest(how=how):
                self.make()
                d = self.register()
                p = os.path.join(d, 'manifest.sha256')
                if how == 'missing':
                    os.remove(p)
                else:
                    write(p, '')
                code, out, err = self.cli('--dir', d, deck=False)
                self.assertNotEqual(code, 0)
                self.assertIn('registered', str(code) + err)
                self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))

    def test_resume_refuses_a_deck_file_that_changed_since_registration(self):
        d = self.register()
        write(self.deck, DECK_TEXT.replace('Torchic', 'Treecko'))
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('my-list', str(code) + err)
        self.assertIn('changed', str(code) + err)
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')), 'nothing may be run')

    def test_resume_refuses_a_panel_file_that_changed_since_registration(self):
        d = self.register()
        p = os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-weezing.txt')
        write(p, read(p) + '# edited\n')
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('t-weezing', str(code) + err)
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))

    def test_resume_refuses_a_program_that_changed_since_registration(self):
        d = self.register()
        registered = sha(self.program)
        write(self.program, FAKE_PROGRAM + '\n# a rebuilt binary\n', mode=0o755)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n'
                               f'  {self.program} has sha256 {sha(self.program)[:12]}, but this run was registered with the program at that path with sha256 {registered[:12]}. '
                               + RESUME_NEEDS_PINNED)
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))

    def test_resume_refuses_a_program_that_is_gone_and_says_so(self):
        d = self.register()
        registered = sha(self.program)
        os.remove(self.program)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertTrue(str(code).endswith(f'\n  {self.program} is missing, but this run was registered with the program at that path with sha256 {registered[:12]}. ' + RESUME_NEEDS_PINNED), code)
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))

    def test_the_program_is_checked_again_before_every_sitting(self):
        self.make()
        self.clock = FakeClock(chi(2026, 10, 7, 5, 0))
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '2')
        swapped = []

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            if not swapped:
                swapped.append(1)
                write(self.program, FAKE_PROGRAM + '\n# swapped while the first sitting was running\n', mode=0o755)
            return p
        code, out, err = self.cli('--dir', d, '--poll-s', '60', school='on', spawn=spawn, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('A resume needs the same program, byte for byte', str(code) + err)
        self.assertEqual(len(jsonl(os.path.join(d, 'fake_calls.jsonl'))), 1, 'the second sitting must not start')

    def test_report_only_writes_a_partial_page_from_the_games_so_far_and_says_so_on_the_console(self):
        self.assertEqual(self.cli('--deals', '2', '--max-games', '24')[0], 0)
        d = self.rundir()
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        games_before = read(os.path.join(d, 'games.jsonl'))
        code, out, err = self.cli('--dir', d, '--report-only', deck=False)
        self.assertEqual(code, 0, err)
        self.assertEqual(read(os.path.join(d, 'games.jsonl')), games_before, 'a report-only call plays nothing')
        self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')))
        self.assertIn('PARTIAL', out, 'the console must not show partial numbers without saying so')
        self.assertNotIn('**', out)
        self.assertNotIn('`', out)

    def test_report_only_needs_a_run_directory(self):
        code, out, err = self.cli('--report-only')
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_resume_refuses_every_option_that_belongs_to_a_new_registration(self):
        d = self.register()
        for extra in (('--deals', '3'), ('--no-paired',), ('--date', '2026-10-11'), ('--seed-base', str(BLOCK[0])), ('--selfcheck',), ('--register-only',),
                      ('--program', self.program)):
            code, out, err = self.cli('--dir', d, *extra, deck=False)
            self.assertNotEqual(code, 0, extra)
            self.assertIn('--dir', str(code) + err, extra)
            self.assertIn(f'{extra[0]} belongs to a new registration; a run that is already registered keeps what it was registered with', str(code) + err, extra)
            self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')), extra)
            self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')), extra)

    def test_a_deck_file_and_a_run_directory_together_are_refused(self):
        d = self.register()
        before = {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}
        argv = [self.deck, '--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'off', '--poll-s', '1']  # nothing else that --dir refuses: only the two together are wrong
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
        self.assertIn('give a deck file or --dir, not both', str(cm.exception.code))
        self.assertEqual(out.getvalue(), '', 'nothing is printed as if a plan were made')
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')), 'the run must not be played')
        self.assertEqual({n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}, before)

    def test_dry_run_on_a_registered_run_prints_where_it_stands_and_writes_nothing(self):
        self.assertEqual(self.cli('--deals', '1', '--max-games', '6')[0], 0)
        d = self.rundir()
        before = {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]  # without the headline that starts every line
        self.assertEqual(lines[0], 'question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?',
                         'the question comes first, then the size')
        self.assertEqual(lines[1], 'played so far: 3 kx3 games + 3 cheap km3 baseline games of 16 kx3 games + 16 cheap km3 baseline games planned; '
                                   f'13 kx3 games + 13 cheap km3 baseline games to go (resume with: python3 rl/strength/slow_report.py --dir {d} --school-rule off)')
        self.assertEqual(lines[2:], ['dry run: nothing written'])
        self.assertNotIn('6 of 32', out, 'the count names the pilots; "x of y games" does not say whose games')
        after = {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}
        self.assertEqual(before, after)

    def test_dry_run_on_a_registered_run_without_the_comparison_asks_the_shorter_question(self):
        d = self.register('--no-paired')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0].split('] ', 1)[1], 'question: how does my-list do when kx3 plays it against the 8 public lists?')

    def test_threads_default_to_two_and_can_be_set_and_zero_is_refused(self):
        self.assertEqual(self.cli('--deals', '1', '--max-games', '2')[0], 0)
        call = jsonl(os.path.join(self.rundir(), 'fake_calls.jsonl'))[0]['argv']
        self.assertEqual(call[call.index('--threads') + 1], '2')
        self.make()
        self.assertEqual(self.cli('--deals', '1', '--max-games', '2', '--threads', '3')[0], 0)
        call = jsonl(os.path.join(self.rundir(), 'fake_calls.jsonl'))[0]['argv']
        self.assertEqual(call[call.index('--threads') + 1], '3')
        self.make()
        code, out, err = self.cli('--deals', '1', '--threads', '0')
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_program_is_run_at_low_priority_when_nice_exists(self):
        self.assertEqual(sr.nice_prefix(lambda name: '/usr/bin/nice'), ['/usr/bin/nice', '-n', '19'])
        self.assertEqual(sr.nice_prefix(lambda name: None), [])

    def test_a_program_that_fails_stops_the_run_with_its_message_and_leaves_a_partial_page(self):
        self.set_program("#!/usr/bin/env python3\nimport sys\nsys.stderr.write('boom: deck is not a valid 20-card list\\n')\nsys.exit(101)\n")
        code, out, err = self.cli('--deals', '1')
        self.assertNotEqual(code, 0)
        self.assertIn('boom', str(code) + err + out)
        page = read(os.path.join(self.rundir(), 'SLOW_REPORT.md'))
        self.assertIn('PARTIAL', page)

    def test_a_program_that_plays_nothing_does_not_loop_forever(self):
        self.set_program('#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n')
        code, out, err = self.cli('--deals', '1')
        self.assertNotEqual(code, 0)
        self.assertIn('no game finished', str(code) + err)
        self.assertTrue(os.path.exists(os.path.join(self.rundir(), 'SLOW_REPORT.md')), 'the page is written before the run gives up')

    def test_a_refusal_by_the_preregistration_leaves_nothing_behind(self):
        os.remove(os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-altaria.txt'))
        code, out, err = self.cli('--deals', '1')
        self.assertNotEqual(code, 0)
        self.assertIn('strength_prereg.py', str(code) + err)
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertFalse(os.path.exists(self.out_root), 'an empty slow_reports folder made by this call is removed too')

    def test_an_interrupt_during_registration_leaves_nothing_behind(self):
        from unittest import mock
        with mock.patch.object(sr, 'run_prereg', side_effect=KeyboardInterrupt):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(KeyboardInterrupt):
                    sr.main(self.argv('--deals', '1'), now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_held_out_deck_is_accepted_end_to_end_and_flagged(self):
        self.make(deck_text=HELD_TEXT[HELD[0]])
        lock_before = read(os.path.join(self.harness, 'heldout.json'))
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, err + out)
        man = json.loads(read(os.path.join(self.rundir(), 'manifest.json')))
        self.assertEqual((man['stage'], man['heldout_in_run'], man['heldout_decks']), ('use', ['my-list'], []))
        page = read(os.path.join(self.rundir(), 'SLOW_REPORT.md'))
        self.assertIn('Held-out decks in this run: my-list', page)
        self.assertIn('the held-out lock is unchanged', page)
        self.assertNotIn('lifted', page)
        self.assertEqual(read(os.path.join(self.harness, 'heldout.json')), lock_before, 'the lock file is untouched')

    def with_rates(self, **rates):
        pin = json.loads(read(self.pin_path))
        pin['games_per_hour'] = rates
        write(self.pin_path, json.dumps(pin))

    def test_the_size_line_counts_both_pilots_games_and_the_time_is_only_for_the_slow_pilots_games(self):
        self.with_rates(typical_low=20, typical_high=40, wall=10)
        for flag, question_end, left_out, stage_clause in ((None, ', and is that better than when km3 plays the same deck on the same deals?', '',
                                                            'with the comparison with km3 on the same deals in the page'),
                                                           ('--no-paired', '?', '; with --no-paired they are still played and the page leaves them out',
                                                            'without the comparison with km3 on the same deals in the page')):
            with self.subTest(flag):
                code, out, err = self.cli('--deals', '3', *([flag] if flag else []), '--dry-run')
                self.assertEqual(code, 0, out + err)
                lines = [l.split('] ', 1)[1] for l in out.splitlines()]  # without the headline that starts every line
                self.assertEqual(len(lines), 7, lines)
                self.assertEqual(lines[0], 'question: how does my-list do when kx3 plays it against the 8 public lists' + question_end, 'the question comes before the plan and the size')
                self.assertTrue(lines[1].startswith('plan: my-list ('), lines[1])
                self.assertEqual(lines[2], 'size: 48 kx3 games + 48 cheap km3 baseline games on the same deals (96 games in all; the km3 games take about a second each' + left_out + '); '
                                 'the time is for the 48 kx3 games: about 72 minutes to 2.4 hours if the deck plays like most of his, '
                                 'about 4.8 hours if it plays like the Wailord wall (measured with 2 games at a time)')
                self.assertTrue(lines[3].startswith('school-morning rule: OFF for this run'), lines[3])
                self.assertTrue(lines[4].startswith('pin committed: bypassed (rl/strength/slow_report_pin.json sha256 '), lines[4])
                self.assertTrue(lines[5].endswith(f'), {stage_clause}, no pass or fail line'), lines[5])
                self.assertEqual(lines[6], 'dry run: nothing written')

    def test_the_registered_question_says_whether_the_comparison_with_km3_is_part_of_the_page(self):
        paired_clause = 'with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: '
        unpaired_clause = ('with 95% ranges; without the comparison with km3 on the same deals (--no-paired: the km3 games are still played, about a second each, '
                           'and left out of the page). Realistic knowledge: ')
        asked, plans = {}, {}
        for paired in (True, False):
            self.make()
            d = self.register() if paired else self.register('--no-paired')
            man = json.loads(read(os.path.join(d, 'manifest.json')))
            prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
            self.assertEqual(man['slow_report']['paired'], paired)
            self.assertIn('\n' + man['question'] + '\n', prereg, 'the preregistration shows the question as registered')
            asked[paired] = man['question']
            plans[paired] = prereg.split('## Analysis plan')[1].split('\n## ')[0]
        self.assertIn(paired_clause, asked[True])
        self.assertNotIn('without the comparison', asked[True])
        self.assertNotIn('--no-paired', asked[True])
        self.assertIn(unpaired_clause, asked[False])
        self.assertNotIn('how much better', asked[False])
        self.assertEqual(asked[True].replace(paired_clause, '#'), asked[False].replace(unpaired_clause, '#'), 'the clause about the comparison is the only difference')
        self.assertIn('- The baseline comparison is **on** (the default): the **paired difference**', plans[True])
        self.assertNotIn('baseline comparison is **off**', plans[True])
        self.assertIn('- The baseline comparison is **off** (`--no-paired`): the reference still plays the deck on the same deals', plans[False])
        self.assertIn('but the page leaves the paired difference out.', plans[False])
        self.assertNotIn('baseline comparison is **on**', plans[False])

    def test_one_deal_is_not_two_deals_in_the_question_the_summary_and_the_console(self):
        for deals, deal_text, games in ((1, '1 deal', 32), (2, '2 deals', 64)):
            with self.subTest(deals):
                self.make()
                code, out, err = self.cli('--deals', str(deals), '--register-only')
                self.assertEqual(code, 0, out + err)
                d = self.rundir()
                man = json.loads(read(os.path.join(d, 'manifest.json')))
                self.assertIn(f'played by km3, {deal_text} x 2 seats each? Primary:', man['question'])
                self.assertEqual(man['slow_report']['summary'], f'Stage use. {deal_text} x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.')
                self.assertIn(f'plan: my-list (decks/events/my-list.txt, ', out)
                self.assertIn(f'), {deal_text} x 2 seats against the 8 public lists', out)
                self.assertIn(f'size: {8 * 2 * deals} kx3 games + {8 * 2 * deals} cheap km3 baseline games on the same deals ({8 * 4 * deals} games in all; ', out, 'a registration says it too')
                self.assertIn(f'pre-registered {games} games (8 pairs, {deal_text} x 2 seats x 2 arms) in {d}', out)

    def prereg_in_this_process(self, opened, interrupt_on=None):
        """A stand-in for sr.run_prereg that runs the registry copy of strength_prereg.py in this process and notes, in order, every file it opens for writing in the run
        folder, with the files that were there at that moment; opening `interrupt_on` raises KeyboardInterrupt instead (a Ctrl-C at that point)."""
        def run_prereg(cfg_path, rundir, repo):
            spec = importlib.util.spec_from_file_location('strength_prereg_under_test', sr.PREREG)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            real_open = builtins.open

            def recording_open(file, mode='r', *a, **kw):
                if isinstance(file, str) and os.path.dirname(file) == rundir and any(c in mode for c in 'wax'):
                    opened.append((os.path.basename(file), sorted(os.listdir(rundir))))
                    if os.path.basename(file) == interrupt_on:
                        raise KeyboardInterrupt
                return real_open(file, mode, *a, **kw)
            out = io.StringIO()
            with mock.patch.object(builtins, 'open', recording_open), mock.patch.object(sys, 'argv', ['strength_prereg.py', '--config', cfg_path, '--out', rundir, '--repo', repo]):
                with contextlib.redirect_stdout(out):
                    mod.main()
            return subprocess.CompletedProcess([], 0, out.getvalue(), '')
        return run_prereg

    def test_manifest_sha256_is_written_last_after_the_preregistration_text(self):
        opened = []
        with mock.patch.object(sr, 'run_prereg', self.prereg_in_this_process(opened)):
            code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, out + err)
        self.assertEqual([name for name, _ in opened], ['manifest.json', 'PREREGISTRATION.md', 'manifest.sha256'])
        there = dict(opened)
        self.assertNotIn('manifest.sha256', there['PREREGISTRATION.md'], 'the hash file comes after the text: a folder with it is a finished registration')
        self.assertEqual(there['manifest.sha256'], ['PREREGISTRATION.md', 'config.json', 'manifest.json'])

    def test_a_registration_cut_off_before_manifest_sha256_exists_is_unfinished_and_leaves_nothing_behind(self):
        for stage in ('PREREGISTRATION.md', 'manifest.sha256'):
            with self.subTest(cut_when_opening=stage):
                self.make()
                opened = []
                with mock.patch.object(sr, 'run_prereg', self.prereg_in_this_process(opened, interrupt_on=stage)):
                    with self.assertRaises(KeyboardInterrupt):
                        self.cli('--deals', '1', '--register-only')
                self.assertEqual(opened[-1][0], stage, 'the Ctrl-C came at that file')
                self.assertTrue(any(n == 'manifest.json' for n, _ in opened), 'and after the manifest was written')
                self.assertFalse(os.path.exists(self.rundir()), 'a folder without manifest.sha256 is an unfinished registration, and is cleared')
                self.assertFalse(os.path.exists(self.out_root))


class SeedBaseAndDefaults(World):
    def test_an_explicit_seed_base_is_used_and_recorded_and_a_bad_one_refused(self):
        ok = BLOCK[0] + 7 * STEP
        d = self.register('--seed-base', str(ok))
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], ok)
        self.make()
        for bad in (ok + 1, BLOCK[0] - STEP, 24_650_050_000):
            code, out, err = self.cli('--deals', '1', '--seed-base', str(bad))
            self.assertNotEqual(code, 0, bad)
            self.assertFalse(os.path.exists(self.out_root), bad)

    def test_the_seed_slot_follows_the_decks_sha256_end_to_end(self):
        d = self.register()
        slots = (BLOCK[1] - BLOCK[0] + 1) // STEP
        want = BLOCK[0] + (int(sha(self.deck)[:8], 16) % slots) * STEP
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], want)

    def test_a_second_deck_gets_a_different_slot_than_the_first_when_they_collide(self):
        d = self.register()
        first = json.loads(read(os.path.join(d, 'manifest.json')))['seed_base']
        # a second report of the very same deck on another date takes the next free slot, not the same seeds
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-11', date=False)
        self.assertEqual(code, 0, err + out)
        second = json.loads(read(os.path.join(self.rundir('2026-10-11_my-list'), 'manifest.json')))['seed_base']
        self.assertNotEqual(first, second)
        self.assertEqual(second, first + STEP)

    def test_the_default_run_folder_is_under_the_repository_results(self):
        argv = [self.deck, '--repo', self.repo, '--pin', self.pin_path, '--date', '2026-10-10', '--school-rule', 'off', '--deals', '1', '--register-only']
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: []), 0)
        self.assertTrue(os.path.isfile(os.path.join(self.repo, 'rl', 'results', 'slow_reports', '2026-10-10_my-list', 'manifest.json')))

    def test_the_command_is_run_at_low_priority(self):
        seen = []

        def spawn(cmd, env, logfile):
            seen.append(cmd)
            return sr.default_spawn(cmd, env, logfile)
        code, out, err = self.cli('--deals', '1', '--max-games', '2', spawn=spawn)
        self.assertEqual(code, 0, err + out)
        nice = shutil.which('nice')
        if nice:
            self.assertEqual(seen[0][:3], [nice, '-n', '19'])
        self.assertEqual(seen[0][len(sr.nice_prefix()):][:2], [self.program, 'run'])


class SelfcheckOption(World):
    def test_a_selfcheck_that_differs_from_the_pin_is_refused_and_nothing_is_written(self):
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)
        self.assertIn('self-check', str(code) + err)
        self.assertIn('pin', str(code) + err)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_selfcheck_that_matches_the_pin_is_recorded_as_replayed(self):
        pin = json.loads(read(self.pin_path))
        pin['selfcheck'] = {s: f'selfcheck pilot={s} games=12 digest=fakefakefakefake' for s in ('km3', 'kx3')}
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
        self.assertEqual(code, 0, err + out)
        d = self.rundir()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual(man['selfcheck'], pin['selfcheck'])
        for spec in ('km3', 'kx3'):  # (the fixture's hand-made pin is let through by the test-only variable, and the words say what it is)
            self.assertEqual(man['selfcheck_source'][spec], 'replayed by slow_report.py on the registering machine just before registration '
                                                            '(equal to the pin file in use, which is NOT the committed pin: test use)')
        prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertEqual(prereg.count('(replayed by slow_report.py on the registering machine just before registration and equal to the pin file in use, which is NOT the committed pin: test use)'), 2)
        self.assertNotIn('equal to the committed pin', prereg)
        self.assertNotIn('not replayed', prereg)
        self.assertEqual(json.loads(read(os.path.join(d, 'config.json')))['selfcheck_given_program_sha256'], sha(self.program),
                         'a replayed text was measured just now, on this program')

    def test_texts_the_pin_says_were_measured_on_another_binary_are_not_recorded_for_this_one(self):
        self.edit_pin(selfcheck_measured_on_sha256='a' * 64)
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertIn('REFUSED by strength_prereg.py (nothing was written):', str(code))
        self.assertIn(f'the self-check text was measured on a program with sha256 aaaaaaaaaaaa, but the program at {self.program} has sha256 {sha(self.program)[:12]}', str(code))
        self.assertFalse(os.path.exists(self.out_root))
        pin = json.loads(read(self.pin_path))
        pin['selfcheck'] = {s: f'selfcheck pilot={s} games=12 digest=fakefakefakefake' for s in ('km3', 'kx3')}
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--register-only', '--selfcheck')
        self.assertEqual(code, 0, 'a replayed text needs no claim about another binary: ' + str(code) + err)

    def edit_pin(self, **kw):
        pin = json.loads(read(self.pin_path))
        pin.update(kw)
        write(self.pin_path, json.dumps(pin))

    def test_the_default_does_not_replay_the_self_check(self):
        d = self.register()
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')), 'registering must not play a single game')
        for spec in ('km3', 'kx3'):
            self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['selfcheck_source'][spec],
                             'given in the config (copied from the pin, which says it was measured on this exact program sha256)')
        prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertEqual(prereg.count('(given in the config, copied from the pin and not replayed: the pin says it was measured on this exact program, whose sha256 is named above)'), 2)
        self.assertNotIn('replayed by slow_report', prereg)
        cfg = json.loads(read(os.path.join(d, 'config.json')))
        self.assertEqual(cfg['selfcheck_given_program_sha256'], self.pin['selfcheck_measured_on_sha256'], 'the config names the program the texts were measured on')
        self.assertNotIn('selfcheck_how', cfg)


# ---------------------------------------------------------------------------------------------------------- the school-morning run, the lock, signals
class SchoolMorningRun(World):
    def test_the_program_is_told_to_stop_at_515_and_a_hung_game_is_killed_at_630_then_replayed_after_5pm(self):
        self.clock = FakeClock(chi(2026, 10, 7, 5, 0))  # Wednesday 5:00 am
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '3')  # three games, then one that never finishes
        self.clock.gate = lambda: os.path.exists(os.path.join(d, 'hanging.flag'))  # do not let the fake clock reach 6:30 before the game is really "in flight"
        self.clock.gate_until = chi(2026, 10, 7, 6, 30)
        spawned = []

        def spawn(cmd, env, logfile):
            spawned.append((self.clock.now(), cmd))
            return sr.default_spawn(cmd, env, logfile)
        with unittest_patch(sr, 'nice_prefix', lambda *a: []):
            code, out, err = self.cli('--dir', d, '--poll-s', '60', school='on', spawn=spawn, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(len(spawned), 2, 'a first sitting cut off at 6:30 and a second one after 5 pm')
        (first_at, first_cmd), (second_at, second_cmd) = spawned
        self.assertEqual(first_at, chi(2026, 10, 7, 5, 0))
        self.assertAlmostEqual(float(first_cmd[first_cmd.index('--stop-after-min') + 1]), 15.0)
        self.assertGreaterEqual(second_at, chi(2026, 10, 7, 17, 0))
        self.assertLess(second_at, chi(2026, 10, 7, 17, 10))
        games = jsonl(os.path.join(d, 'games.jsonl'))
        self.assertEqual(len(games), 32)
        self.assertEqual(len({g['key'] for g in games}), 32, 'the cut-off game is played again, once')
        calls = jsonl(os.path.join(d, 'fake_calls.jsonl'))
        self.assertEqual(len(calls), 2)
        self.assertEqual(sum(1 for g in games), 32)
        events = [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))]
        for want in ('slice_start', 'stopped_for_school', 'waiting_for_school', 'complete'):
            self.assertIn(want, events)
        self.assertLessEqual(max(self.clock.slept), 60 * 60, 'waits are taken in steps, not one long sleep')

    def test_a_long_wait_is_taken_in_short_steps(self):
        self.clock = FakeClock(chi(2026, 10, 7, 6, 0))
        d = self.register()
        code, out, err = self.cli('--dir', d, school='on', deck=False)
        self.assertEqual(code, 0, err + out)
        waits = [s for s in self.clock.slept if s >= 30]
        self.assertTrue(waits)
        self.assertLessEqual(max(self.clock.slept), 60, 'a suspended laptop must not oversleep by hours')
        self.assertGreater(len(self.clock.slept), 600)  # 6:00 to 17:00 in minutes

    def test_with_the_rule_on_a_weekday_afternoon_nothing_starts_until_5pm(self):
        self.clock = FakeClock(chi(2026, 10, 7, 12, 0))
        spawned = []

        def spawn(cmd, env, logfile):
            spawned.append(self.clock.now())
            return sr.default_spawn(cmd, env, logfile)
        d = self.register()
        code, out, err = self.cli('--dir', d, school='on', spawn=spawn, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(spawned[0], chi(2026, 10, 7, 17, 0))

    def test_the_school_rule_is_on_by_default(self):
        self.clock = FakeClock(chi(2026, 10, 7, 12, 0))
        spawned = []

        def spawn(cmd, env, logfile):
            spawned.append(self.clock.now())
            return sr.default_spawn(cmd, env, logfile)
        d = self.register(school=None)  # registered with no --school-rule option at all: the default is the rule on
        code, out, err = self.cli('--dir', d, school=None, spawn=spawn, deck=False)  # and resumed with none: the registered choice
        self.assertEqual(code, 0, err + out)
        self.assertEqual(spawned[0], chi(2026, 10, 7, 17, 0))

    def test_school_days_can_be_changed_on_the_command_line(self):
        self.clock = FakeClock(chi(2026, 10, 7, 12, 0))  # a Wednesday
        spawned = []

        def spawn(cmd, env, logfile):
            spawned.append(self.clock.now())
            return sr.default_spawn(cmd, env, logfile)
        d = self.register()
        code, out, err = self.cli('--dir', d, '--school-days', 'mon,tue,thu,fri', school='on', spawn=spawn, deck=False)  # no school on Wednesdays
        self.assertEqual(code, 0, err + out)
        self.assertEqual(spawned[0], chi(2026, 10, 7, 12, 0), 'a Wednesday is free when it is not a school day')

    def test_with_the_rule_off_there_is_no_stop_after_flag(self):
        self.assertEqual(self.cli('--deals', '1', '--max-games', '2')[0], 0)
        self.assertNotIn('--stop-after-min', jsonl(os.path.join(self.rundir(), 'fake_calls.jsonl'))[0]['argv'])

    def test_three_cuts_in_a_row_with_no_game_finished_stop_the_run(self):
        self.set_program(HANG_PROGRAM)
        self.clock = FakeClock(chi(2026, 10, 7, 5, 0))
        d = self.register()
        with unittest_patch(sr, 'nice_prefix', lambda *a: []):
            code, out, err = self.cli('--dir', d, '--poll-s', '60', school='on', deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('longer than', str(code) + err)
        kills = [e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'stopped_for_school']
        self.assertEqual(len(kills), 3)

    def test_max_games_is_a_budget_for_the_whole_call_and_must_be_positive(self):
        for bad in ('0', '-3'):
            code, out, err = self.cli('--deals', '1', '--max-games', bad)
            self.assertNotEqual(code, 0, bad)
            self.assertFalse(os.path.exists(self.out_root), bad)
        self.make()
        self.assertEqual(self.cli('--deals', '1', '--max-games', '5')[0], 0)
        self.assertEqual(len(jsonl(os.path.join(self.rundir(), 'games.jsonl'))), 5)


class SchoolChoiceIsRegistered(World):
    """The school-morning choice (the rule on or off, and the school days) is made when a run is registered and then kept: in the manifest, in PREREGISTRATION.md, on the page
    and in the resume command. (test_slow_report_runloop.py pins what a resume does with it.)"""
    CASES = [  # (--school-rule given, other options), (rule, days) recorded, what the resume command adds
        ((None, ()), ('on', 'mon,tue,wed,thu,fri'), []),
        (('off', ()), ('off', 'mon,tue,wed,thu,fri'), ['--school-rule', 'off']),
        (('on', ('--school-days', 'sat,sun')), ('on', 'sat,sun'), ['--school-days', 'sat,sun']),
        (('off', ('--school-days', 'sat,sun')), ('off', 'sat,sun'), ['--school-rule', 'off']),  # nothing to say about days when the rule is off
        (('on', ('--school-days', 'mon,tue,wed,thu,fri')), ('on', 'mon,tue,wed,thu,fri'), []),  # the default spelled out is still the default
        (('on', ('--school-days', '')), ('on', ''), ['--school-days', '']),  # no school days at all is a choice, not the default: recorded, and carried by the resume command
        (('off', ('--school-days', '')), ('off', ''), ['--school-rule', 'off']),
    ]

    def test_the_choice_is_recorded_in_the_manifest_the_preregistration_the_page_and_the_resume_command(self):
        for (school, extra), (rule, days), added in self.CASES:
            with self.subTest(school=school, extra=extra):
                self.make()
                d = self.register(*extra, school=school)
                block = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']
                self.assertEqual((block['school_rule'], block['school_days']), (rule, days))
                self.assertEqual(shlex.split(block['resume_command']), ['python3', 'rl/strength/slow_report.py', '--dir', d] + added)
                prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
                self.assertIn(f'- school_rule: `{rule}`\n- school_days: `{days}`\n', prereg)
                self.assertIn('```\n' + block['resume_command'] + '\n```', prereg.split('## Run')[1], 'the registration shows the command that carries the choice')
                self.assertIn('applies the school-morning rule as registered (' + (days or 'no school days') + ')' if rule == 'on'
                              else 'does NOT apply the school-morning rule (chosen at registration: it never pauses for school mornings)', prereg.split('## Run')[1])
                code, out, err = self.cli('--dir', d, '--report-only', deck=False, school=None)
                self.assertEqual(code, 0, err + out)
                page = read(os.path.join(d, 'SLOW_REPORT.md'))
                want = (('- School-morning rule: on (no school days, so it never pauses).' if days == '' else f'- School-morning rule: on ({days}).') if rule == 'on'
                        else '- School-morning rule: off (chosen at registration, for a machine that is not the laptop).')
                self.assertIn('\n' + want + '\n', page)

    def test_resume_command_for_adds_only_what_is_not_the_default(self):
        f = sr.resume_command_for
        base = 'python3 rl/strength/slow_report.py --dir '
        self.assertEqual(f('/r/x', 'on', 'mon,tue,wed,thu,fri'), base + '/r/x')
        self.assertEqual(f('/r/x', 'off', 'mon,tue,wed,thu,fri'), base + '/r/x --school-rule off')
        self.assertEqual(f('/r/x', 'off', 'sat,sun'), base + '/r/x --school-rule off', 'with the rule off the days do not matter')
        self.assertEqual(f('/r/x', 'on', 'sat,sun'), base + '/r/x --school-days sat,sun')
        self.assertEqual(f('/r/x', 'on', 'mon,tue,thu,fri'), base + '/r/x --school-days mon,tue,thu,fri')
        self.assertEqual(f('/r/x', 'on', ''), base + "/r/x --school-days ''", 'no school days at all is a choice too, quoted so that a shell hands it over as an empty word')
        self.assertEqual(f('/r/a b', 'on', 'mon, tue'), base + "'/r/a b' --school-days 'mon, tue'", 'every word is quoted for the shell')
        self.assertEqual(shlex.split(f('/r/a b', 'off', 'mon')), ['python3', 'rl/strength/slow_report.py', '--dir', '/r/a b', '--school-rule', 'off'])

    def test_the_default_days_are_monday_to_friday(self):
        self.assertEqual(sr.DEFAULT_SCHOOL_DAYS, 'mon,tue,wed,thu,fri')
        self.assertEqual(sr.parse_days(sr.DEFAULT_SCHOOL_DAYS), sr.SCHOOL_DAYS)
        self.assertEqual(sr.parse_days(sr.DEFAULT_SCHOOL_DAYS), (0, 1, 2, 3, 4))
        self.assertEqual(sr.parse_days(' SAT , sun,'), (5, 6), 'spaces, capitals and a trailing comma do not matter')
        self.assertEqual(sr.parse_days(''), ())
        with self.assertRaises(SystemExit):
            sr.parse_days('mon,someday')

    def test_a_bad_day_name_is_refused_before_anything_is_written(self):
        for extra in (('--deals', '1'), ('--deals', '1', '--dry-run')):
            code, out, err = self.cli(*extra, '--school-days', 'mon,funday')
            self.assertIn("unknown day 'funday' in --school-days", str(code))
            self.assertFalse(os.path.exists(self.out_root))


class NoTimeZoneDatabase(World):
    """A run with --school-rule off needs nothing from the time zone database (a machine without tzdata, for example a slim cloud image): the zone is loaded the first time it
    is asked for, and the run folder's date falls back to the UTC date."""

    def test_a_self_check_replay_with_the_rule_off_never_asks_for_the_zone(self):
        asked = self.without_tzdata()
        pin = json.loads(read(self.pin_path))
        pin['selfcheck'] = {s: f'selfcheck pilot={s} games=12 digest=fakefakefakefake' for s in ('km3', 'kx3')}
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only', school='off')
        self.assertEqual(code, 0, err + out)
        self.assertEqual(asked, [], 'the replay is bound by the morning cut only when the rule is on')
        self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['selfcheck_source']['kx3'],
                         'replayed by slow_report.py on the registering machine just before registration (equal to the pin file in use, which is NOT the committed pin: test use)')

    def test_a_whole_registration_and_run_with_the_rule_off_never_asks_for_the_zone(self):
        asked = self.without_tzdata()
        code, out, err = self.cli('--deals', '1', school='off')
        self.assertEqual(code, 0, err + out)
        self.assertEqual(asked, [], 'with --date given and the rule off the time zone is not needed anywhere')
        d = self.rundir()
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        self.assertTrue(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')))

    def test_without_the_database_the_run_folder_is_named_by_the_utc_date(self):
        asked = self.without_tzdata()
        self.clock = FakeClock(datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc).astimezone(CHI))  # Oct 10, 22:00 in Chicago; Oct 11 in UTC
        code, out, err = self.cli('--deals', '1', '--register-only', date=False)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(os.listdir(self.out_root), ['2026-10-11_my-list'])
        self.assertIn('America/Chicago', asked, 'it did try the database first')

    def test_local_date_is_the_chicago_date_and_falls_back_to_the_utc_date(self):
        late = datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(sr.local_date(late), '2026-10-10', 'Chicago is five hours behind UTC in October')
        self.assertEqual(sr.local_date(late.astimezone(CHI)), '2026-10-10')
        self.assertEqual(sr.local_date(datetime.datetime(2026, 10, 11, 6, 0, tzinfo=datetime.timezone.utc)), '2026-10-11')
        self.assertEqual(sr.local_date(datetime.datetime(2027, 1, 1, 5, 59, tzinfo=datetime.timezone.utc)), '2026-12-31', 'and six in winter')
        self.without_tzdata()
        self.assertEqual(sr.local_date(late), '2026-10-11')
        self.assertEqual(sr.local_date(late.astimezone(CHI)), '2026-10-11', 'the UTC date of the same moment, whatever zone it comes in')

    def test_the_zone_is_loaded_when_first_asked_for_and_the_old_name_still_works(self):
        old = dict(sr._TZ)
        sr._TZ.clear()
        self.addCleanup(lambda: (sr._TZ.clear(), sr._TZ.update(old)))
        self.assertNotIn('chicago', sr._TZ)
        zone = sr.CHICAGO
        self.assertEqual(str(zone), 'America/Chicago')
        self.assertIn('chicago', sr._TZ)
        self.assertIs(sr.chicago(), zone, 'loaded once')
        self.assertIs(sr.CHICAGO, zone)
        self.assertTrue(hasattr(sr, 'CHICAGO'))
        with self.assertRaises(AttributeError):
            sr.NO_SUCH_THING
        self.assertFalse(hasattr(sr, 'NO_SUCH_THING'))

    def test_the_rule_with_no_school_days_never_needs_the_zone_and_with_days_it_does(self):
        asked = self.without_tzdata()
        self.assertEqual(sr.school_action(chi(2026, 10, 7, 12, 0), ()), {'kind': 'run', 'stop_after_min': None, 'hard_stop': None})
        self.assertEqual(asked, [])
        with self.assertRaises(sr.NoTimeZoneDatabase):
            sr.school_action(chi(2026, 10, 7, 12, 0), (0, 1, 2, 3, 4))
        self.assertEqual(asked, ['America/Chicago'])

    # (what a missing database does on the command line: registration, resume, --report-only, main's REFUSED line)
    TAG = '[kx3 (d513e37b) on my-list v km3 on the public panel] '
    MISSING = ('REFUSED: the time zone database (America/Chicago) is not available here (ZoneInfoNotFoundError): install tzdata, or turn the school-morning rule off with '
               '--school-rule off')

    def test_the_missing_database_is_a_clear_runtime_error_in_words_whatever_went_wrong_loading_it(self):
        self.assertTrue(issubclass(sr.NoTimeZoneDatabase, RuntimeError))
        self.assertFalse(issubclass(sr.NoTimeZoneDatabase, SystemExit), 'a refusal is made of it only by main')
        asked = self.without_tzdata()
        with self.assertRaises(sr.NoTimeZoneDatabase) as cm:
            sr.chicago()
        self.assertEqual(str(cm.exception), self.MISSING[len('REFUSED: '):])
        self.assertEqual(asked, ['America/Chicago'])
        self.assertNotIn('chicago', sr._TZ, 'a failure is not remembered as a zone')
        with mock.patch.dict(sys.modules, {'zoneinfo': None}):  # a machine where the module itself cannot be imported
            with self.assertRaises(sr.NoTimeZoneDatabase) as cm:
                sr.chicago()
        self.assertRegex(str(cm.exception), r'\((ImportError|ModuleNotFoundError)\): install tzdata')
        with mock.patch.object(zoneinfo, 'ZoneInfo', mock.Mock(side_effect=ValueError('a broken tzdata file'))):  # whatever else can go wrong reading it
            with self.assertRaises(sr.NoTimeZoneDatabase) as cm:
                sr.chicago()
        self.assertIn('(ValueError)', str(cm.exception))
        with mock.patch.object(zoneinfo, 'ZoneInfo', type(CHI)):
            self.assertEqual(str(sr.chicago()), 'America/Chicago', 'and with the database back it works')

    def test_a_registration_with_the_rule_on_and_school_days_is_refused_in_words_before_anything_is_written(self):
        self.without_tzdata()
        for label, extra, school in (('the default rule', (), None), ('the rule on', (), 'on'), ('only registering', ('--register-only',), 'on'),
                                     ('other school days', ('--school-days', 'sat,sun'), 'on')):
            with self.subTest(label):
                with mock.patch.object(sr, 'run_prereg', side_effect=AssertionError('nothing may be registered')):
                    code, out, err = self.cli('--deals', '1', *extra, school=school)
                self.assertEqual(code, self.TAG + self.MISSING)
                self.assertFalse(os.path.exists(self.out_root), 'nothing was written')
        with mock.patch.object(sr, 'run_selfcheck', side_effect=AssertionError('no self-check may start')):  # before the hours of a replay, not after
            code, out, err = self.cli('--deals', '1', '--selfcheck', school='on')
        self.assertEqual(code, self.TAG + self.MISSING)
        self.assertEqual(out, '', 'and before the first line of the plan')

    def test_a_registration_that_needs_no_zone_goes_through_where_the_database_is_missing(self):
        asked = self.without_tzdata()
        for label, extra, school in (('the rule off', (), 'off'), ('the rule on and no school days', ('--school-days', ''), 'on')):
            with self.subTest(label):
                self.make()
                code, out, err = self.cli('--deals', '1', '--register-only', *extra, school=school)
                self.assertEqual(code, 0, err + out)
                self.assertEqual(asked, [], 'with --date given, nothing asks for the time zone')
                self.assertTrue(os.path.exists(os.path.join(self.rundir(), 'manifest.sha256')))
        self.make()
        self.clock = FakeClock(datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc).astimezone(CHI))
        code, out, err = self.cli('--deals', '1', '--register-only', '--school-days', '', date=False, school='on')
        self.assertEqual(code, 0, err + out)
        self.assertEqual(os.listdir(self.out_root), ['2026-10-11_my-list'], 'only the name of the folder asks for the zone, and falls back to the UTC date')

    def test_a_resume_with_the_rule_on_and_school_days_is_refused_in_words_and_starts_nothing(self):
        d = self.register(school='on')
        self.without_tzdata()
        started = []
        for label, extra in (('as registered', ()), ('other days', ('--school-days', 'mon,tue')), ('the rule turned on again', ('--school-rule', 'on'))):
            with self.subTest(label):
                code, out, err = self.cli('--dir', d, *extra, deck=False, school=None, spawn=lambda cmd, env, logfile: started.append(cmd))
                self.assertEqual(code, self.TAG + self.MISSING)
                self.assertEqual(started, [], 'no program was started')
                self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'no lock was taken')
                self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
                self.assertNotIn('sitting_call', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))], 'and no sitting was logged')

    def test_a_resume_that_needs_no_zone_plays_where_the_database_is_missing(self):
        d = self.register(school='on')
        asked = self.without_tzdata()
        played = 0
        for label, extra, more in (('the rule turned off', ('--school-rule', 'off'), 4), ('no school days', ('--school-days', ''), 4),
                                   ('only the page, with the rule on', ('--report-only',), 0)):
            with self.subTest(label):
                code, out, err = self.cli('--dir', d, '--max-games', '4', *extra, deck=False, school=None)
                self.assertEqual(code, 0, err + out)
                played += more
                self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), played)
                self.assertTrue(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')))
        self.assertEqual(asked, [])
        self.make()
        d = self.register(school='off')  # and a run registered with the rule off is resumed with no option
        code, out, err = self.cli('--dir', d, '--max-games', '4', deck=False, school=None)
        self.assertEqual((code, len(jsonl(os.path.join(d, 'games.jsonl')))), (0, 4), err + out)
        self.assertEqual(asked, [])

    def test_main_makes_a_refusal_of_a_missing_database_wherever_it_comes_up(self):
        def lost(argv, ctx, **kw):
            ctx['tag'] = 'kx3 on a deck'
            raise sr.NoTimeZoneDatabase('the zone is gone')
        with mock.patch.object(sr, '_main', lost):
            with self.assertRaises(SystemExit) as cm:
                sr.main([])
        self.assertEqual(cm.exception.code, '[kx3 on a deck] REFUSED: the zone is gone', 'with the headline the call had reached, not a traceback')
        with mock.patch.object(sr, '_main', side_effect=RuntimeError('some other failure')):
            with self.assertRaises(RuntimeError):
                sr.main([])

    def test_the_utc_date_stands_in_only_for_a_missing_database(self):
        late = datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc)
        with mock.patch.object(sr, 'chicago', side_effect=sr.NoTimeZoneDatabase('gone')):
            self.assertEqual(sr.local_date(late), '2026-10-11')
        with mock.patch.object(sr, 'chicago', side_effect=RuntimeError('a different failure')):
            with self.assertRaises(RuntimeError):
                sr.local_date(late)
        with mock.patch.object(sr, 'chicago', side_effect=ValueError('and a different one')):
            with self.assertRaises(ValueError):
                sr.local_date(late)

    def test_importing_the_module_works_where_zoneinfo_cannot_be_imported(self):
        code = ("import sys\nsys.modules['zoneinfo'] = None\nsys.path.insert(0, %r)\nimport datetime\nimport slow_report as sr\nprint('imported')\n"
                "print(sr.local_date(datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc)))\n"
                "print(sr.school_action(datetime.datetime(2026, 10, 7, 12, 0, tzinfo=datetime.timezone.utc), ())['kind'])\n" % HERE)
        r = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split(), ['imported', '2026-10-11', 'run'])

    def test_the_real_script_makes_its_plan_with_the_rule_off_where_zoneinfo_cannot_be_imported(self):
        write(os.path.join(self.repo, 'lib', 'deck_check.py'), 'def parse(path):\n    return "Fire", []\n\n\ndef check(name, cards):\n    return []\n')
        runner = "import runpy, sys\nsys.modules['zoneinfo'] = None\nsys.argv = sys.argv[1:]\nrunpy.run_path(sys.argv[0], run_name='__main__')\n"
        r = subprocess.run([sys.executable, '-B', '-c', runner, os.path.join(HERE, 'slow_report.py'), self.deck, '--repo', self.repo, '--pin', self.pin_path,
                            '--out-root', self.out_root, '--school-rule', 'off', '--dry-run'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('school-morning rule: OFF for this run', r.stdout)
        self.assertTrue(r.stdout.rstrip().endswith('dry run: nothing written'), r.stdout)
        self.assertFalse(os.path.exists(self.out_root))


class ReservedSeedSlots(World):
    """The pin's seed_reserved slots (committed runs outside rl/results/slow_reports, the km3 smoke) are used slots: the automatic pick skips them and an explicit base on one
    is refused with the pin's note."""
    RESERVED = [{'base': BLOCK[0] + 684 * STEP, 'note': 'slot 684: a smoke run'}, {'base': BLOCK[0] + 685 * STEP, 'note': 'slot 685: another smoke run'}]

    @staticmethod
    def head(slot):
        return f'{slot:08x}' + '0' * 56  # int(head[:8], 16) % 990 == slot for every slot below 990

    def pick(self, slot, reserved=(), explicit=None, folders=()):
        with tempfile.TemporaryDirectory() as t:
            for base in folders:
                write(os.path.join(t, f'run{base}', 'manifest.json'), json.dumps({'seed_base': base}))
            return sr.pick_seed_base(self.head(slot), t, BLOCK, STEP, explicit=explicit, reserved=reserved)

    def test_the_automatic_pick_skips_a_reserved_slot_and_the_next_free_one_is_taken(self):
        for slot, want in ((684, 686), (685, 686), (683, 683), (686, 686), (0, 0)):
            self.assertEqual(self.pick(slot, self.RESERVED), BLOCK[0] + want * STEP, slot)
        self.assertEqual(self.pick(684), BLOCK[0] + 684 * STEP, 'without the reservation the deck would have had it')
        self.assertEqual(self.pick(684, self.RESERVED, folders=[BLOCK[0] + 686 * STEP]), BLOCK[0] + 687 * STEP, 'a reserved slot and a used folder both count')
        self.assertEqual(self.pick(989, [{'base': BLOCK[0] + 989 * STEP}]), BLOCK[0], 'past the last slot it starts again at the first')

    def test_an_explicit_base_on_a_reserved_slot_is_refused_with_its_note(self):
        for r in self.RESERVED:
            with self.assertRaises(SystemExit, msg=r['note']) as cm:
                self.pick(5, self.RESERVED, explicit=r['base'])
            self.assertEqual(cm.exception.code, f"REFUSED: --seed-base {r['base']} is a seed slot that is already used ({r['note']}); two reports would play the same deals")
        self.assertEqual(self.pick(5, self.RESERVED, explicit=BLOCK[0] + 686 * STEP), BLOCK[0] + 686 * STEP, 'its neighbour is free')
        self.assertEqual(self.pick(5, self.RESERVED, explicit=BLOCK[0] + 683 * STEP), BLOCK[0] + 683 * STEP)

    def test_a_reserved_slot_without_a_note_is_still_named_and_a_base_inside_the_slot_reserves_it(self):
        with self.assertRaises(SystemExit) as cm:
            self.pick(5, [{'base': BLOCK[0] + 10 * STEP}], explicit=BLOCK[0] + 10 * STEP)
        self.assertIn('is a seed slot that is already used (a reserved slot);', cm.exception.code)
        with self.assertRaises(SystemExit):
            self.pick(5, [{'base': BLOCK[0] + 10 * STEP + 777, 'note': 'inside'}], explicit=BLOCK[0] + 10 * STEP)
        self.assertEqual(self.pick(10, [{'base': BLOCK[0] + 10 * STEP + 777}]), BLOCK[0] + 11 * STEP)

    def test_entries_that_are_not_slots_of_the_block_are_ignored(self):
        junk = [{'base': 'x', 'note': 'text'}, {'base': 1.5}, {'base': True}, {'note': 'no base'}, 5, 'text', None, [], {'base': BLOCK[1] + 1, 'note': 'above'},
                {'base': BLOCK[0] - 1, 'note': 'below'}]
        self.assertEqual(self.pick(10, junk), BLOCK[0] + 10 * STEP)
        self.assertEqual(self.pick(5, junk, explicit=BLOCK[0]), BLOCK[0])
        self.assertEqual(self.pick(5, explicit=BLOCK[0]), BLOCK[0])

    def test_a_deck_that_lands_on_a_reserved_slot_gets_the_next_free_one_end_to_end(self):
        for slot in (684, 685, 686):
            with self.subTest(slot=slot):
                self.make(deck_text=deck_text_in_slot(slot))
                self.assertEqual(self.pin['seed_reserved'][slot - 684]['base'], BLOCK[0] + slot * STEP, 'the pin of this test is the committed one')
                d = self.register()
                self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], BLOCK[0] + 687 * STEP, 'the first slot after the three the smoke used')
                shutil.rmtree(self.out_root)
                pin = json.loads(read(self.pin_path))
                pin['seed_reserved'] = []  # a pin that reserves nothing: the deck's own slot
                write(self.pin_path, json.dumps(pin))
                d = self.register()
                self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], BLOCK[0] + slot * STEP)
                shutil.rmtree(self.out_root)

    def test_a_pin_must_list_its_reserved_slots_and_a_typo_in_the_list_is_refused_not_ignored(self):
        """A reservation that was left out or mistyped would hand out a slot a committed run already used (the pin's seed_reserved is required and checked as a list of slots)."""
        good = BLOCK[0] + 684 * STEP
        refusal = 'seed_reserved must be a list of {"base": the first seed of a slot inside the seed block, "note": text}; a typo there would hand out a slot a committed run already used'
        pin = json.loads(read(self.pin_path))
        del pin['seed_reserved']
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, f"[slow report] the pin {self.pin_path} has no 'seed_reserved'", 'an older pin is not a pin with nothing reserved')
        self.assertFalse(os.path.exists(self.out_root))
        bad = [('null', None), ('a number', 5), ('text', 'slots'), ('an object', {'base': good, 'note': 'x'}), ('an entry that is no object', [good]), ('no base', [{'note': 'x'}]),
               ('no note', [{'base': good}]), ('a base in text', [{'base': str(good), 'note': 'x'}]), ('a base with a fraction', [{'base': good + 0.5, 'note': 'x'}]),
               ('a base that is true', [{'base': True, 'note': 'x'}]), ('a note that is no text', [{'base': good, 'note': 5}]), ('a base inside a slot', [{'base': good + 1, 'note': 'x'}]),
               ('a base below the block', [{'base': BLOCK[0] - STEP, 'note': 'x'}]), ('a base past the last slot', [{'base': BLOCK[1] + 1, 'note': 'x'}]),
               ('one good and one bad', [{'base': good, 'note': 'x'}, {'base': good + 7, 'note': 'y'}])]
        for label, value in bad:
            with self.subTest(label):
                pin['seed_reserved'] = value
                write(self.pin_path, json.dumps(pin))
                code, out, err = self.cli('--deals', '1', '--register-only')
                self.assertEqual(code, f'[slow report] the pin {self.pin_path}: {refusal}')
                self.assertFalse(os.path.exists(self.out_root), 'nothing was written')
        tiny = os.path.join(self.tmp, 'tiny-block-pin.json')  # in a block that starts at 0 the number True (which is 1 to Python) would be a slot, and is still no number
        for label, value, loads in (('true', True, False), ('one', 1, True)):
            with self.subTest('a tiny block: ' + label):
                write(tiny, json.dumps(dict(pin, seed_block=[0, 9], seed_step=1, seed_reserved=[{'base': value, 'note': 'x'}])))
                if loads:
                    self.assertEqual(sr.load_pin(tiny)['seed_reserved'], [{'base': 1, 'note': 'x'}])
                else:
                    with self.assertRaises(SystemExit) as cm:
                        sr.load_pin(tiny)
                    self.assertEqual(cm.exception.code, f'the pin {tiny}: {refusal}')
        last = BLOCK[0] + (BLOCK[1] - BLOCK[0] + 1) // STEP * STEP - STEP
        for label, value in (('none', []), ('two', self.RESERVED), ('the last slot', [{'base': last, 'note': 'the last one'}]), ('the first slot', [{'base': BLOCK[0], 'note': 'the first one'}])):
            with self.subTest('good: ' + label):
                pin['seed_reserved'] = value
                write(self.pin_path, json.dumps(pin))
                self.assertEqual(sr.load_pin(self.pin_path)['seed_reserved'], value)

    def test_an_explicit_seed_base_on_a_reserved_slot_is_refused_on_the_command_line_and_nothing_is_written(self):
        for r in self.pin['seed_reserved']:
            code, out, err = self.cli('--deals', '1', '--register-only', '--seed-base', str(r['base']))
            self.assertEqual(code, f"{HEADLINE_START}my-list v km3 on the public panel] REFUSED: --seed-base {r['base']} is a seed slot that is already used ({r['note']}); "
                                   'two reports would play the same deals')
            self.assertFalse(os.path.exists(self.out_root))
        free = self.pin['seed_reserved'][-1]['base'] + STEP
        d = self.register('--seed-base', str(free))
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], free)

    def test_the_committed_pin_reserves_the_three_smoke_slots(self):
        pin = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))
        self.assertEqual([r['base'] for r in pin['seed_reserved']], [24669400000, 24669500000, 24669600000])
        for r in pin['seed_reserved']:
            self.assertTrue(r['note'].strip())
            self.assertTrue(BLOCK[0] <= r['base'] and (r['base'] - BLOCK[0]) % STEP == 0)


class UnfinishedRuns(World):
    """Registering a deck while an earlier slow report of it still has games to play prints a WARNING that names the run and how to resume it; it does not refuse."""

    def warning(self, d, played=0, planned=32, deck='my-list', command=None):
        return (f'WARNING: an unfinished slow report of {deck} already exists: {d} ({played} of {planned} games played). '
                f'Resume it ({command or "python3 rl/strength/slow_report.py --dir " + d}) instead of registering a second one, unless you mean to.')

    def lines(self, out):
        return [l.split('] ', 1)[1] for l in out.splitlines()]

    def second(self, *extra, date='2026-10-11'):
        return self.cli('--deals', '1', *extra, '--date', date, date=False, school=None)

    def other_deck(self):
        path = os.path.join(self.repo, 'decks', 'events', 'other-list.txt')
        write(path, DECK_TEXT.replace('Torchic', 'Treecko'))
        return path

    def test_a_second_registration_of_an_unfinished_deck_warns_after_the_question_and_still_registers(self):
        first = self.register(school=None)
        code, out, err = self.second('--register-only')
        self.assertEqual(code, 0, err + out)
        lines = self.lines(out)
        self.assertEqual(lines.count(self.warning(first)), 1)
        i = lines.index(self.warning(first))
        self.assertTrue(lines[i - 1].startswith('question: '), 'the question is first')
        self.assertTrue(lines[i + 1].startswith('plan: '), 'the plan follows')
        self.assertTrue(os.path.exists(os.path.join(self.rundir('2026-10-11_my-list'), 'manifest.sha256')), 'a warning is not a refusal')
        self.assertEqual(sorted(os.listdir(self.out_root)), ['2026-10-10_my-list', '2026-10-11_my-list'])

    def test_the_fallback_command_of_a_manifest_without_one_keeps_an_empty_list_of_school_days(self):
        """'' is a choice (no school days), only a missing entry means the default: the command rebuilt for an old manifest says so (found by a test writer)."""
        d = os.path.join(self.out_root, '2026-10-01_my-list')
        write(os.path.join(d, 'manifest.json'), json.dumps({'planned_games': 4, 'slow_report': {'deck_name': 'my-list', 'school_rule': 'on', 'school_days': ''}}))
        write(os.path.join(d, 'games.jsonl'), '')
        self.assertEqual(sr.unfinished_runs(self.out_root, 'my-list'), [(d, 0, 4, sr.resume_command_for(d, 'on', ''))])
        self.assertIn("--school-days ''", sr.unfinished_runs(self.out_root, 'my-list')[0][3])
        write(os.path.join(d, 'manifest.json'), json.dumps({'planned_games': 4, 'slow_report': {'deck_name': 'my-list'}}))  # an entry that is missing is the default
        self.assertEqual(sr.unfinished_runs(self.out_root, 'my-list'), [(d, 0, 4, sr.resume_command_for(d, 'on', sr.DEFAULT_SCHOOL_DAYS))])
        self.assertNotIn('--school-days', sr.unfinished_runs(self.out_root, 'my-list')[0][3])

    def test_a_dry_run_warns_too_and_writes_nothing(self):
        first = self.register(school=None)
        before = sorted(os.listdir(first))
        code, out, err = self.second('--dry-run')
        self.assertEqual(code, 0, err + out)
        self.assertIn(self.warning(first), self.lines(out))
        self.assertEqual(os.listdir(self.out_root), ['2026-10-10_my-list'])
        self.assertEqual(sorted(os.listdir(first)), before)

    def test_the_warning_counts_the_games_played_so_far(self):
        self.assertEqual(self.cli('--deals', '1', '--max-games', '5', school=None)[0], 0)
        first = self.rundir()
        code, out, err = self.second('--register-only')
        self.assertEqual(code, 0, err + out)
        self.assertIn(self.warning(first, played=5), self.lines(out))

    def test_every_unfinished_run_of_the_deck_gets_its_own_line_in_folder_order(self):
        older = self.register(school=None)
        code, out, err = self.second('--register-only', date='2026-10-11')
        self.assertEqual(code, 0, err + out)
        newer = self.rundir('2026-10-11_my-list')
        code, out, err = self.second('--register-only', date='2026-10-12')
        self.assertEqual(code, 0, err + out)
        warnings = [l for l in self.lines(out) if l.startswith('WARNING')]
        self.assertEqual(warnings, [self.warning(older), self.warning(newer)])

    def test_there_is_no_warning_for_a_finished_run(self):
        self.assertEqual(self.cli('--deals', '1', school=None)[0], 0)
        self.assertEqual(len(jsonl(os.path.join(self.rundir(), 'games.jsonl'))), 32)
        code, out, err = self.second('--register-only')
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('WARNING', out)

    def test_there_is_no_warning_for_another_decks_run_either_way_round(self):
        other = self.other_deck()
        code, out, err = self.cli_path(other, '--deals', '1', '--register-only', school=None)
        self.assertEqual(code, 0, err + out)
        code, out, err = self.cli('--deals', '1', '--register-only', school=None)
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('WARNING', out)
        code, out, err = self.cli_path(other, '--deals', '1', '--register-only', '--date', '2026-10-11', school=None)
        self.assertEqual(code, 0, err + out)
        self.assertEqual([l for l in self.lines(out) if l.startswith('WARNING')], [self.warning(self.rundir('2026-10-10_other-list'), deck='other-list')])

    def test_there_is_no_warning_for_a_folder_that_is_not_a_slow_report(self):
        first = self.register(school=None)
        man = json.loads(read(os.path.join(first, 'manifest.json')))
        del man['slow_report']
        rewrite_manifest(first, man)
        code, out, err = self.second('--register-only')
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('WARNING', out)

    def test_a_warning_names_the_command_that_resumes_that_run_as_it_was_registered_not_one_built_from_this_calls_options(self):
        a = self.register(school='off')  # registered with the rule off: its command says so
        a_cmd = f'python3 rl/strength/slow_report.py --dir {a} --school-rule off'
        self.assertEqual(json.loads(read(os.path.join(a, 'manifest.json')))['slow_report']['resume_command'], a_cmd)
        code, out, err = self.second('--register-only', '--school-days', 'sat,sun', date='2026-10-11')  # this call: the rule on (the default), other days
        self.assertEqual(code, 0, err + out)
        self.assertEqual([l for l in self.lines(out) if l.startswith('WARNING')], [self.warning(a, command=a_cmd)], 'not the plain command, not one with sat,sun')
        b = self.rundir('2026-10-11_my-list')
        b_cmd = f'python3 rl/strength/slow_report.py --dir {b} --school-days sat,sun'
        self.assertEqual(json.loads(read(os.path.join(b, 'manifest.json')))['slow_report']['resume_command'], b_cmd)
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-12', date=False, school='off')  # this call: the rule off
        self.assertEqual(code, 0, err + out)
        self.assertEqual([l for l in self.lines(out) if l.startswith('WARNING')], [self.warning(a, command=a_cmd), self.warning(b, command=b_cmd)],
                         "each run's own command: the second one is not told --school-rule off")

    def test_a_run_with_no_recorded_command_gets_one_made_from_the_school_choice_it_recorded(self):
        def folder(name, block):
            write(os.path.join(t, name, 'manifest.json'), json.dumps({'planned_games': 8, 'slow_report': dict({'deck_name': 'my-list'}, **block)}))
        base = 'python3 rl/strength/slow_report.py --dir '
        with tempfile.TemporaryDirectory() as t:
            for name, block, added in (('a-nothing-recorded', {}, ''), ('b-the-rule-off', {'school_rule': 'off', 'school_days': 'mon'}, ' --school-rule off'),
                                       ('c-other-days', {'school_rule': 'on', 'school_days': 'sat,sun'}, ' --school-days sat,sun'),
                                       ('d-the-default-spelled-out', {'school_rule': 'on', 'school_days': 'mon,tue,wed,thu,fri'}, ''),
                                       ('e-only-the-rule', {'school_rule': 'off'}, ' --school-rule off'),
                                       ('f-a-null-command', {'resume_command': None, 'school_rule': 'off'}, ' --school-rule off'),
                                       ('g-its-own-command', {'resume_command': 'python3 somewhere/else.py --dir g', 'school_rule': 'off'}, None)):
                folder(name, block)
            got = {os.path.basename(d): (played, planned, cmd) for d, played, planned, cmd in sr.unfinished_runs(t, 'my-list')}
            self.assertEqual(len(got), 7)
            for name, added in (('a-nothing-recorded', ''), ('b-the-rule-off', ' --school-rule off'), ('c-other-days', ' --school-days sat,sun'), ('d-the-default-spelled-out', ''),
                                ('e-only-the-rule', ' --school-rule off'), ('f-a-null-command', ' --school-rule off')):
                self.assertEqual(got[name], (0, 8, base + os.path.join(t, name) + added), name)
            self.assertEqual(got['g-its-own-command'], (0, 8, 'python3 somewhere/else.py --dir g'), 'the command the registration recorded is the one given')

    def test_unfinished_runs_lists_the_registered_runs_of_the_deck_that_still_have_games_to_go(self):
        def folder(root, name, manifest, keys=(), raw=None):
            if isinstance(manifest, bytes):
                write_bytes(os.path.join(root, name, 'manifest.json'), manifest)
            else:
                write(os.path.join(root, name, 'manifest.json'), manifest if isinstance(manifest, str) else json.dumps(manifest))
            if keys or raw:
                write(os.path.join(root, name, 'games.jsonl'), ''.join(json.dumps({'key': k}) + '\n' for k in keys) + (raw or ''))
        mine = {'deck_name': 'my-list'}
        resume = 'python3 rl/strength/slow_report.py --dir '
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(sr.unfinished_runs(os.path.join(t, 'nothing-here'), 'my-list'), [])
            self.assertEqual(sr.unfinished_runs(t, 'my-list'), [])
            write(os.path.join(t, 'a-file-not-a-folder'), 'x')
            self.assertEqual(sr.unfinished_runs(os.path.join(t, 'a-file-not-a-folder'), 'my-list'), [], 'an output folder that is a file')
            folder(t, 'c-three-of-32', {'planned_games': 32, 'slow_report': mine}, ['k1', 'k2', 'k2', 'k3'], raw='{"key": "k4", "de')  # a repeated key and a torn line count for nothing
            folder(t, 'a-none-of-8', {'planned_games': 8, 'slow_report': mine})
            folder(t, 'b-finished', {'planned_games': 3, 'slow_report': mine}, ['k1', 'k2', 'k3'])
            folder(t, 'd-more-than-planned', {'planned_games': 2, 'slow_report': mine}, ['k1', 'k2', 'k3'])
            folder(t, 'e-another-deck', {'planned_games': 8, 'slow_report': {'deck_name': 'other'}})
            folder(t, 'f-no-block', {'planned_games': 8})
            folder(t, 'g-null-block', {'planned_games': 8, 'slow_report': None})
            folder(t, 'h-no-plan', {'slow_report': mine})
            folder(t, 'i-plan-is-text', {'planned_games': '8', 'slow_report': mine})
            folder(t, 'j-not-json', '{not json')
            folder(t, 'k-a-list', '[]')
            folder(t, 'l-null', 'null')
            os.makedirs(os.path.join(t, 'm-no-manifest'))
            write(os.path.join(t, 'n-a-file'), 'x')
            folder(t, 'o-half-written', '{"planned_games": 8, "slow_report": {"deck_name": "my-li')  # the manifest of a registration that was cut off
            folder(t, 'p-not-text', b'\xff\xfe{"planned_games": 8}')
            os.makedirs(os.path.join(t, 'q-manifest-is-a-folder', 'manifest.json'))
            folder(t, 'r-block-is-a-list', {'planned_games': 8, 'slow_report': ['my-list']})
            folder(t, 's-block-is-text', {'planned_games': 8, 'slow_report': 'my-list'})
            folder(t, 't-plan-is-a-fraction', {'planned_games': 8.0, 'slow_report': mine})
            folder(t, 'u-plan-is-null', {'planned_games': None, 'slow_report': mine})
            folder(t, 'v-deck-name-is-a-list', {'planned_games': 8, 'slow_report': {'deck_name': ['my-list']}})
            folder(t, 'w-school-days-is-a-number', {'planned_games': 8, 'slow_report': dict(mine, school_days=5)})  # no command can be made from it
            write(os.path.join(t, 'x-key-is-a-list', 'games.jsonl'), '{"key": ["a"]}\n')
            folder(t, 'x-key-is-a-list', {'planned_games': 8, 'slow_report': mine})
            self.assertEqual(sr.unfinished_runs(t, 'my-list'), [(os.path.join(t, 'a-none-of-8'), 0, 8, resume + os.path.join(t, 'a-none-of-8')),
                                                                (os.path.join(t, 'c-three-of-32'), 3, 32, resume + os.path.join(t, 'c-three-of-32'))])
            self.assertEqual(sr.unfinished_runs(t, 'other'), [(os.path.join(t, 'e-another-deck'), 0, 8, resume + os.path.join(t, 'e-another-deck'))])


class RebuiltFixture(World):
    """The fixture of the cloud route (no tests of its own): the pin of this class holds the texts the fake programs print, a harness source (src/*.rs and Cargo.toml) is laid
    out in the temporary repository and hashed in the pin, and the rebuilt copy self.cloud has the build record rl/strength/build.sh writes beside a program (PROGRAM.build.json:
    the pin's engine tree and harness source, this file's sha256), so it is a good rebuild of the pinned source. self.replayed lists the self-checks that were replayed."""
    TEXT = 'selfcheck pilot=%s games=12 digest=fakefakefakefake'
    PRINT = "print('selfcheck pilot=%s games=12 digest=fakefakefakefake' % arg('--pilot'))"
    # the paragraph of the page for a rebuild; {digests} is what the self-checks were equal to (pin_digests of the registered state of the pin)
    REBUILD_LINE = ('The program is NOT the pinned binary (`{pinned}`, sha256 `{sha12}`): its build record says it is a rebuild of the pinned source, and it was accepted only because that record '
                    'has the pinned engine tree and harness source and both self-checks were replayed on the registering machine ({host}) and equal {digests}, and the harness source in the '
                    "checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those replayed self-checks "
                    '(12 fixed games per pilot), not the record.')
    RUSTC = 'rustc 1.90.0 (fake 2026-01-01)'

    def rebuilt_engine_text(self, program, rec, digests=FILE_DIGESTS):
        """The engine text the registration of a rebuild carries: the pin's, then what this program is, why it is not the pinned binary and what it was accepted on. The fixture's hand-made pin
        is let through by the test-only variable, so `digests` is by default what pin_digests says of that; a test with a committed pin passes COMMITTED_DIGESTS."""
        lines = [l for l in rec['rustc'].splitlines() if l.strip()] if isinstance(rec.get('rustc'), str) else []
        rustc = lines[0] if lines else 'toolchain not recorded'  # (the first line of `rustc -vV` that says anything, or the engine text's own words for a record that has none)
        return (self.pin['engine'] + f"; THIS PROGRAM ({program}, sha256 {sha(program)[:12]}) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) "
                f"says it is a rebuild of that source (build record sha256 {rec['record_sha256'][:12]}: engine tree as archived {rec['engine_tree_archived'][:12]}, harness source "
                f"{rec['harness_source_sha256'][:12]}, {rustc}), accepted because both self-checks were replayed on the registering machine and equal {digests}")

    def setUp(self):
        super().setUp()
        self.lay_out_harness()
        self.replayed, self.deadlines = [], []
        real = sr.run_selfcheck

        def spy(pin, repo, spec, say, **kw):
            self.replayed.append((spec, pin['program']))
            self.deadlines.append(kw.get('deadline'))
            return real(pin, repo, spec, say, **kw)
        patcher = mock.patch.object(sr, 'run_selfcheck', spy)
        patcher.start()
        self.addCleanup(patcher.stop)

    def lay_out_harness(self):
        """A harness source in the temporary repository, a pin that names its hash and the fake programs' self-check texts, and the rebuilt copy self.cloud."""
        for name, text in (('src/main.rs', 'fn main() {}\n'), ('src/lib.rs', '// the library\n'), ('src/notes.txt', 'not Rust: left out of the hash\n'),
                           ('Cargo.toml', '[package]\nname = "strength"\n')):
            write(os.path.join(self.repo, 'rl', 'strength', name), text)
        self.edit_pin(harness_source_sha256=self.harness_hash(), selfcheck={s: self.TEXT % s for s in ('km3', 'kx3')})
        self.cloud = os.path.join(self.tmp, 'cloud', 'strength')
        self.rebuild_at(self.cloud)

    def edit_pin(self, **kw):
        pin = json.loads(read(self.pin_path))
        pin.update(kw)
        write(self.pin_path, json.dumps(pin, indent=1))
        self.pin = pin

    def harness_hash(self):
        """The hash build.sh prints, worked out here by hand: sha256 of src/*.rs in name order, then Cargo.toml."""
        d = os.path.join(self.repo, 'rl', 'strength')
        data = b''
        for n in sorted(os.listdir(os.path.join(d, 'src'))):
            if n.endswith('.rs'):
                with open(os.path.join(d, 'src', n), 'rb') as f:
                    data += f.read()
        with open(os.path.join(d, 'Cargo.toml'), 'rb') as f:
            data += f.read()
        return hashlib.sha256(data).hexdigest()

    def build_record(self, path, **over):
        """The record build.sh writes beside the program at `path`, for a good rebuild of the pinned source: schema 1, this file's sha256, the pin's engine ref, engine tree (as
        archived) and harness source hash, and the toolchain and build paths of a made-up cloud machine. `over` replaces fields; a value of DROP removes the field (None stays: JSON null,
        as build.sh writes for the engine ref of a folder and the CARGO_HOME it was not given)."""
        ref, tree = self.pin['engine_ref'], self.pin['engine_tree']
        rec = dict(schema=1, program=path, program_sha256=sha(path), engine_arg=ref, engine=f'{ref} engine tree {tree}', engine_ref=ref, engine_tree_archived=tree,
                   harness_source_sha256=self.pin['harness_source_sha256'], rustc=f'{self.RUSTC}\nbinary: rustc\nhost: x86_64-unknown-linux-gnu', cargo='cargo 1.90.0 (fake 2026-01-01)',
                   machine='Linux 6.1.0 x86_64', libc='ldd (Debian GLIBC 2.36-9) 2.36', host='cloud-box-1', home='/home/cloud', cargo_home=None, build_dir='/home/cloud/strength_build',
                   target_dir='/home/cloud/strength_build/target', jobs='8', built_at='2026-10-09T22:00:00Z',
                   rebuild_command=f'env HOME=/home/cloud CARGO_HOME=/home/cloud/.cargo STRENGTH_BUILD_DIR=/home/cloud/strength_build STRENGTH_TARGET_DIR=/home/cloud/strength_build/target '
                                   f'STRENGTH_JOBS=8 STRENGTH_REPO=/home/cloud/repo bash /home/cloud/repo/rl/strength/build.sh {ref} {path}')
        rec.update(over)
        return {k: v for k, v in rec.items() if v is not DROP}

    def write_record(self, path, **over):
        """Write build_record(path, **over) beside the program, the way build.sh does (indented JSON, a final newline). Returns the record."""
        rec = self.build_record(path, **over)
        write(path + '.build.json', json.dumps(rec, indent=1) + '\n')
        return rec

    def put_program(self, path, text, **over):
        """Write a program with its good build record (`over` as in build_record)."""
        write(path, text, mode=0o755)
        return self.write_record(path, **over)

    def rebuild_at(self, path, differs_for=None, **over):
        """A program at `path` that is not the pinned binary (other bytes), plays like it, and prints the pin's self-check texts, except, with differs_for='km3' or 'kx3', for
        that pilot; its build record beside it (`over` as in build_record)."""
        text = FAKE_PROGRAM + '\n# built on the cloud\n'
        if differs_for:
            self.assertEqual(text.count(self.PRINT), 1)
            text = text.replace(self.PRINT, "print('selfcheck pilot=%s games=12 digest=%s' % (arg('--pilot'), 'changedchanged00' if arg('--pilot') == " + repr(differs_for) + " else 'fakefakefakefake'))")
        return self.put_program(path, text, **over)

    def spawned(self):
        """A spawn that notes the program each sitting is started with."""
        seen = []

        def spawn(cmd, env, logfile):
            seen.append(cmd[len(sr.nice_prefix())])
            return sr.default_spawn(cmd, env, logfile)
        spawn.seen = seen
        return spawn

    def manifest(self, d):
        return json.loads(read(os.path.join(d, 'manifest.json')))

    def git(self, *a, repo=None):
        r = subprocess.run(['git', '-C', repo or self.repo, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', *a], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def bytes_of(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def commit_pin(self, data=None, repo=None):
        """Commit a pin as rl/strength/slow_report_pin.json in `repo` (the temporary repository; made a git repository first unless it is inside one): the bytes of the fixture's pin
        file as it is now, or `data`. Returns the committed file."""
        repo = repo or self.repo
        path = os.path.join(repo, 'rl', 'strength', 'slow_report_pin.json')
        write_bytes(path, self.bytes_of(self.pin_path) if data is None else data)
        if subprocess.run(['git', '-C', repo, 'rev-parse', '--git-dir'], capture_output=True).returncode != 0:
            self.git('init', '-q', repo=repo)
        self.git('add', 'rl/strength/slow_report_pin.json', repo=repo)
        self.git('commit', '-q', '-m', 'the pin', repo=repo)
        return path


class CloudRoute(RebuiltFixture):
    """--program PATH: a REBUILD of the pinned source (for example made on the cloud with rl/strength/build.sh) instead of the pinned binary. It is accepted only when the pin in use
    is the committed one, this checkout's harness source is the pinned build's, the program has its build record (PROGRAM.build.json) with the pinned engine tree and harness source
    and BOTH self-checks, replayed on it, equal the committed pin's digests; otherwise nothing is written. (The build record's refusals are in BuildRecord, a resume with a changed
    program in ProgramChangedOnResume, the committed pin in CommittedPin.)"""

    def test_the_pinned_binary_under_another_path_takes_the_pinned_route_and_replays_nothing(self):
        copy = os.path.join(self.tmp, 'copy', 'strength')
        write(copy, FAKE_PROGRAM, mode=0o755)
        self.assertEqual(sha(copy), sha(self.program))
        self.assertFalse(os.path.exists(copy + '.build.json'), 'a copy of the pinned bytes needs no build record')
        spawn = self.spawned()
        code, out, err = self.cli('--deals', '1', '--program', copy, spawn=spawn)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.replayed, [])
        for here in (self.tmp, os.path.dirname(copy)):
            self.assertFalse(os.path.exists(os.path.join(here, 'selfcheck_env.json')), 'no self-check was run')
        d = self.rundir()
        man = self.manifest(d)
        b = man['slow_report']
        self.assertEqual((man['program'], man['program_sha256']), (copy, sha(self.program)))
        self.assertEqual((b['program_route'], b['pinned_program'], b['pinned_program_sha256']), ('pinned', self.program, sha(self.program)))
        self.assertIsNone(b['build_record'], 'the pinned bytes have no build record to carry')
        self.assertNotIn('engine_tree_in_checkout', b, 'the checkout-based engine tree check is gone')
        self.assertNotIn('- build_record: `{', read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertEqual(man['engine'], self.pin['engine'], 'the pinned program is described as the pin describes it, with nothing added')
        prereg_run = read(os.path.join(d, 'PREREGISTRATION.md')).split('## Run')[1]
        self.assertIn('and checks the registration, the deck files and the pinned program before every sitting:', prereg_run)
        self.assertNotIn('REBUILD', prereg_run)
        self.assertNotIn('rebuild of the pinned source', prereg_run, 'the pinned binary is not called a rebuild, in either wording')
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'])
        self.assertEqual(set(man['selfcheck_source'].values()), {'given in the config (copied from the pin, which says it was measured on this exact program sha256)'})
        self.assertEqual(set(spawn.seen), {copy}, 'the games are played by the program that was given')
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertNotIn('REBUILD', page)
        self.assertNotIn('NOT the pinned binary', page)
        self.assertIn('(copied from the pin, not replayed: the pin says it was measured on this exact binary)', page)
        self.assertIn(f'Program `{copy}` sha256 `{sha(copy)[:12]}`.', page)

    def test_a_rebuild_is_accepted_when_both_self_checks_equal_the_pin_and_is_recorded_as_a_rebuild(self):
        spawn = self.spawned()
        code, out, err = self.cli('--deals', '1', '--program', self.cloud, spawn=spawn)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'both pilots, on the rebuilt copy, km3 first')
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(self.cloud), 'selfcheck_env.json')), 'the rebuilt copy ran the self-check')
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')), 'and the pinned binary did not')
        d = self.rundir()
        man = self.manifest(d)
        b = man['slow_report']
        self.assertNotEqual(sha(self.cloud), sha(self.program))
        self.assertEqual((man['program'], man['program_sha256']), (self.cloud, sha(self.cloud)), 'the manifest names the rebuilt copy, not the pin')
        self.assertEqual((b['program_route'], b['pinned_program'], b['pinned_program_sha256']), ('rebuilt', self.program, sha(self.program)))
        self.assertEqual((b['harness_source_sha256'], b['harness_source_checkout_sha256']), (self.pin['harness_source_sha256'],) * 2)
        self.assertEqual((b['engine_ref'], b['engine_tree']), (self.pin['engine_ref'], self.pin['engine_tree']))
        self.assertNotIn('engine_tree_in_checkout', b, 'the temporary checkout is no git repository, and the checkout-based engine tree check is gone: the build record says what was built')
        rec = dict(self.build_record(self.cloud), record_file=self.cloud + '.build.json', record_sha256=sha(self.cloud + '.build.json'))
        self.assertEqual(b['build_record'], rec, 'the registration carries the build record as it was read, with the record file and its sha256')
        self.assertEqual(man['engine'], self.rebuilt_engine_text(self.cloud, rec))
        self.assertIn('is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source', man['engine'])
        self.assertNotIn('IS A REBUILD', man['engine'], 'the claim that the program IS a rebuild is gone: the record says so, and it is not signed')
        self.assertEqual(man['selfcheck'], {s: self.TEXT % s for s in ('km3', 'kx3')})
        self.assertEqual(man['selfcheck_source'], {s: 'replayed by slow_report.py on the registering machine just before registration (equal to the pin file in use, which is NOT the committed pin: test use)'
                                                   for s in ('km3', 'kx3')})
        cfg = json.loads(read(os.path.join(d, 'config.json')))
        self.assertEqual((cfg['program'], cfg['program_sha256'], cfg['selfcheck_given_program_sha256'], cfg['selfcheck_how']), (self.cloud, sha(self.cloud), sha(self.cloud), 'replayed'))
        self.assertEqual(set(spawn.seen), {self.cloud}, 'the games are played by the rebuilt copy')
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        self.assertEqual(out.splitlines().count(f'{HEADLINE_START}my-list v km3 on the public panel] self-check of km3: 12 fixed games on {self.cloud} '
                                                '(this takes a while for kx3; run it when the machine is free)'), 1)
        prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
        for line in (f'- program_route: `rebuilt`', f'- pinned_program: `{self.program}`', f'- pinned_program_sha256: `{sha(self.program)}`',
                     f"- harness_source_sha256: `{self.pin['harness_source_sha256']}`", f"- harness_source_checkout_sha256: `{self.pin['harness_source_sha256']}`",
                     f"- engine_ref: `{self.pin['engine_ref']}`", f"- engine_tree: `{self.pin['engine_tree']}`", '- school_rule: `off`', '- school_days: `mon,tue,wed,thu,fri`',
                     f'- build_record: `{json.dumps(rec, sort_keys=True, ensure_ascii=False)}`', f'- registered_on: `{socket.gethostname()}`'):
            self.assertIn('\n' + line + '\n', prereg)
        self.assertNotIn('engine_tree_in_checkout', prereg)
        self.assertIn(f'Program: `{self.cloud}` sha256 `{sha(self.cloud)}`', prereg)
        self.assertIn('and checks the registration, the deck files and the program it was registered with, a rebuild of the pinned source by its build record (accepted after both '
                      'self-checks were replayed on the registering machine; a resume needs the same sha256, or a rebuild whose build record has the same engine tree and harness hash and '
                      'whose two self-checks are replayed again) before every sitting:', prereg.split('## Run')[1])
        self.assertNotIn('REBUILD', prereg, 'the registration does not claim the program IS a rebuild either: its build record says so')
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertIn('\n- ' + self.REBUILD_LINE.format(pinned=self.program, sha12=sha(self.program)[:12], host=socket.gethostname(), digests=FILE_DIGESTS) + '\n', page)
        self.assertNotIn('REBUILD', page, 'the page does not say the program IS a rebuild: it says what the record says and what was replayed')
        self.assertIn(f"\n- Build record `strength.build.json` sha256 `{rec['record_sha256'][:12]}`: engine {rec['engine_arg']} -> tree as archived `{self.pin['engine_tree'][:12]}` "
                      f"(the pin's is `{self.pin['engine_tree'][:12]}`), harness source `{self.pin['harness_source_sha256'][:12]}`, {self.RUSTC}, {rec['cargo']}, built 2026-10-09T22:00:00Z on "
                      f"cloud-box-1 (Linux 6.1.0 x86_64); to rebuild the same bytes after a restart: `{rec['rebuild_command']}`.\n", page)
        self.assertIn(f'Program `{self.cloud}` sha256 `{sha(self.cloud)[:12]}`.', page)
        self.assertIn('\n- Build: ' + man['engine'] + '\n', page, 'the page says the build is a rebuild, in the registered words')
        self.assertEqual(page.count('(replayed on the registering machine just before registration, equal to the pin file in use (NOT the committed pin: test use))'), 2)
        self.assertNotIn('equal to the committed pin', page)
        self.assertIn(f"- Harness source sha256 `{self.pin['harness_source_sha256'][:12]}` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.", page)

    def test_the_whole_cloud_route_with_the_rule_off_needs_no_time_zone_database(self):
        asked = self.without_tzdata()
        code, out, err = self.cli('--deals', '1', '--program', self.cloud, school='off')
        self.assertEqual(code, 0, err + out)
        self.assertEqual(asked, [])
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)])
        self.assertEqual(len(jsonl(os.path.join(self.rundir(), 'games.jsonl'))), 32)

    def test_a_relative_program_path_is_recorded_as_an_absolute_one(self):
        old = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, old)
        d = self.register('--program', os.path.join('cloud', 'strength'))
        man = self.manifest(d)
        self.assertEqual(man['program'], self.cloud, 'a resume from another folder must still find it')
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)])

    def test_a_rebuild_whose_self_check_differs_for_either_pilot_is_refused_and_nothing_is_written(self):
        for pilot, tried in (('km3', ['km3']), ('kx3', ['km3', 'kx3'])):
            with self.subTest(differs_for=pilot):
                self.replayed.clear()
                self.rebuild_at(self.cloud, differs_for=pilot)
                code, out, err = self.cli('--deals', '1', '--program', self.cloud)
                self.assertIn(f'REFUSED: the self-check of {pilot} does not match the pin.', str(code))
                self.assertIn(f"  pinned: {self.TEXT % pilot}\n  got:    selfcheck pilot={pilot} games=12 digest=changedchanged00\n", str(code))
                self.assertTrue(str(code).endswith('nothing was written.'), code)
                self.assertEqual([s for s, p in self.replayed], tried, 'km3 first, and it stops at the first difference')
                self.assertEqual({p for s, p in self.replayed}, {self.cloud})
                self.assertFalse(os.path.exists(self.out_root), 'nothing was written')

    def test_a_rebuild_whose_self_check_crashes_is_refused_with_its_exit_code_and_nothing_is_written(self):
        self.put_program(self.cloud, "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('boom: no engine\\n')\nsys.exit(1)\n")
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the self-check of km3 on {self.cloud} exited with code 1 (boom: no engine); '
                               'a self-check that fails is not a match, whatever it printed. Nothing was written.')
        self.assertEqual([s for s, p in self.replayed], ['km3'], 'and it stops there')
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_rebuild_whose_self_check_prints_the_pinned_text_but_exits_with_an_error_is_refused_too(self):
        text = FAKE_PROGRAM + '\n# built on the cloud\n'
        self.assertEqual(text.count("    sys.exit(0)\nman = json"), 1)
        self.put_program(self.cloud, text.replace("    sys.exit(0)\nman = json", "    sys.exit(3)\nman = json"))
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the self-check of km3 on {self.cloud} exited with code 3 ({self.TEXT % "km3"}); '
                               'a self-check that fails is not a match, whatever it printed. Nothing was written.')
        self.assertFalse(os.path.exists(self.out_root))
        self.put_program(self.cloud, "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")  # and one that exits cleanly and prints nothing does not match either
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertIn(f"REFUSED: the self-check of km3 does not match the pin.\n  pinned: {self.TEXT % 'km3'}\n  got:    \nThe program is not behaving as the pinned build did; nothing was written.", str(code))
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_rebuild_from_another_harness_source_is_refused_before_any_replay(self):
        edits = (('a source file changed', lambda: write(os.path.join(self.repo, 'rl', 'strength', 'src', 'main.rs'), 'fn main() { 1; }\n')),
                 ('Cargo.toml changed', lambda: write(os.path.join(self.repo, 'rl', 'strength', 'Cargo.toml'), '[package]\nname = "other"\n')),
                 ('another Rust file added', lambda: write(os.path.join(self.repo, 'rl', 'strength', 'src', 'extra.rs'), '// new\n')),
                 ('a Rust file removed', lambda: os.remove(os.path.join(self.repo, 'rl', 'strength', 'src', 'lib.rs'))),
                 ('no harness source at all', lambda: shutil.rmtree(os.path.join(self.repo, 'rl', 'strength'))))
        for label, edit in edits:
            with self.subTest(label):
                self.make()  # a fresh world each time, with the harness source laid out again
                self.lay_out_harness()
                edit()
                here = sr.harness_source_sha256(self.repo)
                self.assertNotEqual(here, self.pin['harness_source_sha256'])
                code, out, err = self.cli('--deals', '1', '--program', self.cloud)
                self.assertEqual(code, f"[kx3 (d513e37b) v km3] REFUSED: {self.cloud} has sha256 {sha(self.cloud)[:12]}, not the pinned {sha(self.program)[:12]}, "
                                       'so it would have to be a rebuild of the pinned source; but the harness source in this checkout '
                                       f"({(here or 'not found')[:12]}) is not the pinned build's ({self.pin['harness_source_sha256'][:12]}), so a build from here is not that program. "
                                       'Check out the commit the pin was made on, or make a new pin after its own gate.')
                self.assertEqual(self.replayed, [], 'refused before the hours-long replay')
                self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.cloud), 'selfcheck_env.json')))
                self.assertFalse(os.path.exists(self.out_root))

    def test_the_pinned_route_records_the_checkouts_harness_source_but_does_not_depend_on_it(self):
        write(os.path.join(self.repo, 'rl', 'strength', 'src', 'main.rs'), 'fn main() { 2; }\n')
        here = self.harness_hash()
        self.assertNotEqual(here, self.pin['harness_source_sha256'])
        d = self.register()
        b = self.manifest(d)['slow_report']
        self.assertEqual((b['program_route'], b['harness_source_sha256'], b['harness_source_checkout_sha256']), ('pinned', self.pin['harness_source_sha256'], here))
        self.assertIn(f"- harness_source_checkout_sha256: `{here}`\n", read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
        self.assertIn(f"the checkout this run was registered from has `{here[:12]}` (so the pinned binary was not built from exactly that source).", read(os.path.join(d, 'SLOW_REPORT.md')))

    def test_a_different_program_without_the_program_option_is_refused_and_the_message_points_to_it(self):
        write(self.program, FAKE_PROGRAM + '\n# a rebuild at the pinned path\n', mode=0o755)
        code, out, err = self.cli('--deals', '1')
        msg = str(code)
        self.assertIn(f'REFUSED: {self.program} (sha256 {sha(self.program)[:12]}) is not the pinned build (sha256 {self.pin["program_sha256"][:12]}). A slow report uses only the exact tested version.', msg)
        self.assertIn(f'If this is a rebuild of {self.pin["engine_ref"][:8]} (for example on the cloud, with rl/strength/build.sh), pass it with --program PATH', msg)
        self.assertIn("both self-checks are then replayed on this machine and must equal the committed pin's digests.", msg)
        self.assertEqual(self.replayed, [])
        self.assertFalse(os.path.exists(self.out_root))

    def test_program_with_a_run_directory_is_refused(self):
        d = self.register()
        code, out, err = self.cli('--dir', d, '--program', self.cloud, deck=False)
        self.assertEqual(code, '[kx3 (d513e37b) v km3] --program belongs to a new registration; a run that is already registered keeps what it was registered with, '
                               'so it cannot be used with --dir')
        self.assertEqual(self.replayed, [])
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')))

    def test_a_program_file_that_is_not_there_is_refused(self):
        gone = os.path.join(self.tmp, 'cloud', 'not-built-yet')
        code, out, err = self.cli('--deals', '1', '--program', gone)
        self.assertEqual(code, f'[kx3 (d513e37b) v km3] REFUSED: the program {gone} does not exist, so no slow report can run. A different build needs a new pin '
                               '(rl/strength/slow_report_pin.json), after its own gate; a REBUILD of d513e37b (for example on the cloud, with rl/strength/build.sh) goes through --program PATH.')
        self.assertFalse(os.path.exists(self.out_root))
        os.remove(self.program)
        code, out, err = self.cli('--deals', '1')
        self.assertIn(f'the program {self.program} does not exist', str(code), 'the pinned path is checked the same way')
        self.assertIn('goes through --program PATH.', str(code), 'and says how a rebuild is given')

    def test_the_pinned_source_is_named_by_the_first_8_characters_of_its_ref_or_in_words_when_the_pin_has_none(self):
        gone = os.path.join(self.tmp, 'cloud', 'not-built-yet')
        write(self.program, FAKE_PROGRAM + '\n# changed\n', mode=0o755)
        for label, pin, named in (('a ref', dict(self.pin, engine_ref='0123456789abcdef0123456789abcdef01234567'), '01234567'), ('a short ref', dict(self.pin, engine_ref='abc'), 'abc'),
                                  ('no ref', {k: v for k, v in self.pin.items() if k != 'engine_ref'}, 'the pinned source'), ('a ref that is null', dict(self.pin, engine_ref=None), 'the pinned source'),
                                  ('an empty ref', dict(self.pin, engine_ref=''), 'the pinned source')):
            with self.subTest(label):
                with self.assertRaises(SystemExit) as cm:
                    sr.check_program(pin, gone, self.repo)
                self.assertTrue(cm.exception.code.endswith(f'after its own gate; a REBUILD of {named} (for example on the cloud, with rl/strength/build.sh) goes through --program PATH.'), cm.exception.code)
                with self.assertRaises(SystemExit) as cm:
                    sr.check_program(pin, None, self.repo)
                self.assertIn(f'If this is a rebuild of {named} (for example on the cloud, with rl/strength/build.sh), pass it with --program PATH:', cm.exception.code)
                self.assertNotIn('None', cm.exception.code)

    def test_a_dry_run_on_the_rebuilt_route_says_it_is_a_rebuild_and_replays_nothing(self):
        code, out, err = self.cli('--deals', '1', '--program', self.cloud, '--dry-run')
        self.assertEqual(code, 0, err + out)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertEqual(lines[-3], f'program {self.cloud} (sha256 {sha(self.cloud)[:12]}) is NOT the pinned binary (sha256 {sha(self.program)[:12]}): its build record '
                                    f"(strength.build.json, sha256 {sha(self.cloud + '.build.json')[:12]}) says it is a rebuild of the pinned source (engine tree as archived {self.pin['engine_tree'][:12]}, "
                                    f"harness source {self.pin['harness_source_sha256'][:12]}, built with {self.RUSTC}); both self-checks will be replayed on this machine against {FILE_DIGESTS} "
                                    "before anything is registered (hours for kx3), and the checkout's harness source equals the pinned build's")
        self.assertTrue(lines[-4].startswith('pin committed: bypassed ('), 'the pin line comes first, then what the program is')
        self.assertTrue(lines[-2].startswith('stage use'), lines[-2])
        self.assertIn(f'program {self.cloud} (rebuilt, sha256 {sha(self.cloud)[:12]})', lines[-2])
        self.assertEqual(lines[-1], 'dry run: nothing written')
        self.assertEqual(self.replayed, [], 'a dry run replays nothing')
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.cloud), 'selfcheck_env.json')))
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_dry_run_on_the_pinned_route_does_not_talk_of_a_rebuild(self):
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('REBUILD', out)
        self.assertNotIn('NOT the pinned binary', out)
        self.assertNotIn('rebuild of the pinned source', out)
        self.assertIn(f'program {self.program} (pinned, sha256 {sha(self.program)[:12]})', out)

    def test_a_dry_run_on_the_rebuilt_route_refuses_a_foreign_harness_source_too(self):
        write(os.path.join(self.repo, 'rl', 'strength', 'Cargo.toml'), '[package]\nname = "other"\n')
        code, out, err = self.cli('--deals', '1', '--program', self.cloud, '--dry-run')
        self.assertIn('is not the pinned build\'s', str(code))
        self.assertEqual(out, '')

    def test_a_rebuild_run_is_resumed_with_the_rebuilt_copy_and_replays_nothing_again(self):
        d = self.register('--program', self.cloud)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)])
        spawn = self.spawned()
        code, out, err = self.cli('--dir', d, deck=False, spawn=spawn)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'a resume does not replay the self-checks')
        self.assertEqual(set(spawn.seen), {self.cloud})
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        self.assertIn('The program is NOT the pinned binary (', read(os.path.join(d, 'SLOW_REPORT.md')))

    def test_a_rebuilt_run_is_played_in_slices_with_the_command_each_slice_prints(self):
        d = self.register('--program', self.cloud)
        command = f'python3 rl/strength/slow_report.py --dir {d} --school-rule off'
        self.assertEqual(self.manifest(d)['slow_report']['resume_command'], command, 'the command PREREGISTRATION.md shows carries the choice for a machine that is not the laptop')
        spawn = self.spawned()
        for played in (10, 20, 30):
            code, out, err = self.cli('--dir', d, '--max-games', '10', deck=False, school=None, spawn=spawn)
            self.assertEqual(code, 0, err + out)
            self.assertIn(f'{HEADLINE_START}my-list v km3 on the public panel] stopped after --max-games 10 (games across both arms, about half of them kx3 games); resume with: {command}',
                          out.splitlines())
            self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), played)
            self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')))
        code, out, err = self.cli('--dir', d, '--max-games', '10', deck=False, school=None, spawn=spawn)
        self.assertEqual(code, 0, err + out)
        self.assertNotIn('stopped after', out)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertNotIn('PARTIAL', page)
        self.assertIn('its build record says it is a rebuild of the pinned source', page)
        self.assertEqual(set(spawn.seen), {self.cloud}, 'every slice is played by the rebuilt copy')
        self.assertEqual(len(spawn.seen), 4)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'the self-checks were replayed once, at the registration')

    def test_the_games_of_a_run_whose_rebuilt_copy_changed_can_still_be_reported_on(self):
        self.assertEqual(self.cli('--deals', '1', '--max-games', '6', '--program', self.cloud)[0], 0)
        d = self.rundir()
        write(self.cloud, FAKE_PROGRAM + '\n# another rebuild, other bytes\n', mode=0o755)
        calls = len(jsonl(os.path.join(d, 'fake_calls.jsonl')))
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        code, out, err = self.cli('--dir', d, '--report-only', deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertIn('PARTIAL', read(os.path.join(d, 'SLOW_REPORT.md')))
        self.assertEqual(len(jsonl(os.path.join(d, 'fake_calls.jsonl'))), calls, 'a report-only call starts no program')

    def test_a_resume_of_a_rebuilt_run_whose_program_is_gone_is_refused_and_explained(self):
        d = self.register('--program', self.cloud)
        registered = sha(self.cloud)
        os.remove(self.cloud)  # the rebuilt copy is gone (its record is still beside it): there is nothing to replay the self-checks on, so a resume cannot take the program-changed route
        self.assertTrue(os.path.exists(self.cloud + '.build.json'))
        problem = f'{self.cloud} is missing, but this run was registered with the program at that path with sha256 {registered[:12]}. ' + RESUME_NEEDS
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  ' + problem)
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'nothing was replayed again')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0)
        self.assertIn('(it would be refused: ' + problem + ')', out)

    def test_selfcheck_and_program_together_replay_once_and_the_replay_is_bounded_by_the_school_morning(self):
        self.clock = FakeClock(chi(2026, 10, 7, 20, 0))  # a Wednesday evening
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.cloud, '--selfcheck', school='on')
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'forced by --program: once each, not twice')
        self.assertEqual(self.deadlines, [chi(2026, 10, 8, 6, 30)] * 2, "both replays must end by the next morning's 6:30 cut")

    def test_a_rebuild_is_not_replayed_in_school_hours(self):
        self.clock = FakeClock(chi(2026, 10, 7, 10, 0))  # a Wednesday morning
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.cloud, school='on')
        self.assertIn('REFUSED: the self-check runs for hours and it is school time (the school-morning rule waits until Wed 17:00 Chicago time)', str(code))
        self.assertEqual(self.replayed, [])
        self.assertFalse(os.path.exists(self.out_root))
        code, out, err = self.cli('--deals', '1', '--register-only', school='on')
        self.assertEqual(code, 0, 'the pinned binary needs no replay, so school hours do not matter for it' + str(code) + err)

    def test_harness_source_sha256_is_the_hash_build_sh_prints(self):
        self.assertEqual(sr.harness_source_sha256(self.repo), self.harness_hash())
        by_hand = hashlib.sha256(b'// the library\n' + b'fn main() {}\n' + b'[package]\nname = "strength"\n').hexdigest()
        self.assertEqual(sr.harness_source_sha256(self.repo), by_hand, 'src/*.rs in name order (lib.rs before main.rs), then Cargo.toml, no separators')
        write(os.path.join(self.repo, 'rl', 'strength', 'src', 'notes.txt'), 'changed, but not Rust\n')
        self.assertEqual(sr.harness_source_sha256(self.repo), by_hand, 'only .rs files')
        write(os.path.join(self.repo, 'rl', 'strength', 'src', 'a.rs'), '// first by name\n')
        self.assertEqual(sr.harness_source_sha256(self.repo), hashlib.sha256(b'// first by name\n' + b'// the library\n' + b'fn main() {}\n' + b'[package]\nname = "strength"\n').hexdigest())
        os.remove(os.path.join(self.repo, 'rl', 'strength', 'Cargo.toml'))
        self.assertIsNone(sr.harness_source_sha256(self.repo), 'no Cargo.toml: no harness source')
        self.assertIsNone(sr.harness_source_sha256(os.path.join(self.tmp, 'nowhere')))

    def test_check_program_says_which_route_a_program_takes(self):
        pin = dict(self.pin)
        same_bytes = os.path.join(self.tmp, 'copy', 'strength')
        write(same_bytes, FAKE_PROGRAM, mode=0o755)
        pinned = ('pinned', sha(self.program))
        self.assertEqual(sr.check_program(pin), pinned)
        self.assertEqual(sr.check_program(pin, None, self.repo), pinned)
        self.assertEqual(sr.check_program(pin, self.program, self.repo), pinned)
        self.assertEqual(sr.check_program(pin, same_bytes, self.repo), pinned, 'the pinned bytes under another path are the pinned program')
        self.assertEqual(sr.check_program(pin, same_bytes), pinned, 'and need no checkout to compare')
        self.assertEqual(sr.check_program(pin, self.cloud, self.repo), ('rebuilt', sha(self.cloud)))
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(pin, self.cloud)
        self.assertIn('the harness source in this checkout (not found) is not the pinned build\'s', cm.exception.code, 'a rebuild is not accepted without a checkout to compare')
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(dict(pin, harness_source_sha256='0' * 64), self.cloud, self.repo)
        self.assertIn(f'({sr.harness_source_sha256(self.repo)[:12]}) is not the pinned build\'s (000000000000)', cm.exception.code)
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(pin, os.path.join(self.tmp, 'nowhere'), self.repo)
        self.assertEqual(cm.exception.code, f'REFUSED: the program {os.path.join(self.tmp, "nowhere")} does not exist, so no slow report can run. A different build needs a new pin '
                                            '(rl/strength/slow_report_pin.json), after its own gate; a REBUILD of d513e37b (for example on the cloud, with rl/strength/build.sh) goes through '
                                            '--program PATH.')
        write(self.program, FAKE_PROGRAM + '\n# changed\n', mode=0o755)
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(pin, None, self.repo)
        self.assertIn('--program PATH', cm.exception.code)
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(pin, self.program, self.repo)
        self.assertIn('the frozen binary has been overwritten (do not build over it; build.sh to another path)', cm.exception.code, 'the same path given explicitly is not a rebuild either')
        os.remove(self.program)
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(pin, None, self.repo)
        self.assertIn(f'the program {self.program} does not exist', cm.exception.code)

    # ------------------------------------------------------------------------------------------------ the pinned binary's own path
    def overwritten(self, path, sha12):
        return (f"{path} is the pinned binary's own path, but the file there has sha256 {sha12}, not the pinned {self.pin['program_sha256'][:12]}: the frozen binary has been "
                'overwritten (do not build over it; build.sh to another path). A rebuild is accepted at any other path, after its self-checks are replayed.')

    def test_a_program_at_the_pinned_path_with_other_bytes_is_the_overwritten_frozen_binary_and_never_a_rebuild(self):
        write(self.program, FAKE_PROGRAM + '\n# built over the frozen binary\n', mode=0o755)
        other12 = sha(self.program)[:12]
        self.assertNotEqual(other12, self.pin['program_sha256'][:12])
        for extra in ((), ('--dry-run',), ('--register-only',)):
            code, out, err = self.cli('--deals', '1', '--program', self.program, *extra)
            self.assertEqual(code, '[kx3 (d513e37b) v km3] REFUSED: ' + self.overwritten(self.program, other12), extra)
            self.assertEqual(out, '', 'refused before the first line of the plan')
            self.assertFalse(os.path.exists(self.out_root), 'nothing was written')
        self.assertEqual(self.replayed, [], 'and refused before the hours-long replay, not after it')
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')))
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(self.pin, self.program)
        self.assertEqual(cm.exception.code, 'REFUSED: ' + self.overwritten(self.program, other12), 'refused without a checkout to look at too, ahead of the harness source')
        code, out, err = self.cli('--deals', '1')  # and no --program at all: the plain refusal, not the rebuild route
        self.assertIn('is not the pinned build (sha256 ', str(code))
        self.assertNotIn('overwritten', str(code))

    def test_the_pinned_path_is_the_pinned_path_however_it_is_spelled(self):
        write(self.program, FAKE_PROGRAM + '\n# built over the frozen binary\n', mode=0o755)
        other12 = sha(self.program)[:12]
        link = os.path.join(self.tmp, 'cloud', 'looks-like-a-rebuild')
        os.symlink(self.program, link)
        dotted = os.path.join(self.tmp, 'cloud', '..', os.path.basename(self.program))
        for label, spelled, shown in (('a symlink to it', link, link), ('a path with ..', dotted, self.program)):
            with self.subTest(label):
                code, out, err = self.cli('--deals', '1', '--program', spelled)
                self.assertEqual(code, '[kx3 (d513e37b) v km3] REFUSED: ' + self.overwritten(shown, other12))
                self.assertFalse(os.path.exists(self.out_root))
        os.remove(self.program)  # the pinned path is itself a link to the rebuilt copy: it is the same file, whichever way round it is named
        os.symlink(self.cloud, self.program)
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertEqual(code, '[kx3 (d513e37b) v km3] REFUSED: ' + self.overwritten(self.cloud, sha(self.cloud)[:12]))
        self.assertEqual(self.replayed, [])
        self.assertFalse(os.path.exists(self.out_root))

    def test_where_the_pinned_binary_does_not_exist_at_all_a_rebuild_at_another_path_is_accepted(self):
        os.remove(self.program)  # a cloud machine: the laptop's path is not there
        self.assertEqual(sr.check_program(self.pin, self.cloud, self.repo), ('rebuilt', sha(self.cloud)))
        d = self.register('--program', self.cloud)
        self.assertEqual(self.manifest(d)['slow_report']['program_route'], 'rebuilt')
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)])

    def test_the_pinned_binary_itself_is_the_pinned_route_even_when_named_by_its_own_path(self):
        d = self.register('--program', self.program)
        b = self.manifest(d)['slow_report']
        self.assertEqual((b['program_route'], self.manifest(d)['program']), ('pinned', self.program))
        self.assertEqual(self.replayed, [], 'the pinned bytes need no replay')

    # ------------------------------------------------------------------------------------------------ the checkout's git state no longer matters
    def commit_folder(self, folder, text):
        """Commit `text` in a file of `folder` in the temporary repository (made a git checkout the first time). Returns (the commit, the tree of its engine folder as `git ls-tree` prints it,
        or None when the commit has no engine folder)."""
        write(os.path.join(self.repo, folder, 'src', 'lib.rs'), text)
        if not os.path.isdir(os.path.join(self.repo, '.git')):
            self.git('init', '-q')
        self.git('add', folder)
        self.git('commit', '-q', '-m', f'{folder} {text}')
        commit = self.git('rev-parse', 'HEAD')
        line = self.git('ls-tree', commit, 'engine')
        return commit, (line.split()[2] if line else None)

    def test_the_checkout_based_engine_tree_check_is_gone(self):
        self.assertFalse(hasattr(sr, 'engine_tree_in_checkout'), 'what was archived and compiled is what the build record says, not what a git checkout holds')
        self.assertNotIn('engine_tree_checkout', inspect.signature(sr.build_config).parameters)
        d = self.register('--program', self.cloud)
        self.assertNotIn('engine_tree_in_checkout', self.manifest(d)['slow_report'])
        self.assertNotIn('engine_tree_in_checkout', read(os.path.join(d, 'PREREGISTRATION.md')))

    def test_a_rebuild_is_accepted_whatever_the_git_state_of_the_checkout_is_when_its_build_record_is_good(self):
        def no_git_repository():
            return {}

        def git_checkout_whose_engine_folder_is_another_tree_than_the_pins():
            first, tree1 = self.commit_folder('engine', 'fn engine() {}\n')
            second, tree2 = self.commit_folder('engine', 'fn engine() { changed(); }\n')
            self.assertNotEqual(tree2, 'ab' * 20)
            return {'engine_ref': second, 'engine_tree': 'ab' * 20}  # the pin names a commit whose engine folder is not the tree it pins: the old check refused this

        def git_checkout_without_the_pinned_commit():
            self.commit_folder('engine', 'fn engine() {}\n')  # (the pin's engine_ref is not a commit of this repository)
            return {}

        def commit_with_no_engine_folder():
            return {'engine_ref': self.commit_folder('other', 'fn other() {}\n')[0]}

        def pin_with_no_engine_ref():
            return {'engine_ref': None}
        for prepare in (no_git_repository, git_checkout_whose_engine_folder_is_another_tree_than_the_pins, git_checkout_without_the_pinned_commit, commit_with_no_engine_folder,
                        pin_with_no_engine_ref):
            with self.subTest(prepare.__name__):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.edit_pin(**prepare())
                self.write_record(self.cloud)  # (the record is for the pin as it is now)
                self.assertEqual(sr.check_program(self.pin, self.cloud, self.repo), ('rebuilt', sha(self.cloud)))
                d = self.register('--program', self.cloud)
                b = self.manifest(d)['slow_report']
                self.assertEqual((b['program_route'], b['engine_ref'], b['engine_tree']), ('rebuilt', self.pin['engine_ref'], self.pin['engine_tree']))
                self.assertEqual(b['build_record']['engine_tree_archived'], self.pin['engine_tree'])
                self.assertNotIn('engine_tree_in_checkout', b)
                self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)])

    def test_the_pinned_binary_needs_no_build_record_and_never_reads_one(self):
        copy = os.path.join(self.tmp, 'copy', 'strength')
        write(copy, FAKE_PROGRAM, mode=0o755)
        write(copy + '.build.json', '{this is not json at all')  # not read: the pinned bytes are what the pin pins
        d = self.register('--program', copy)
        b = self.manifest(d)['slow_report']
        self.assertEqual((b['program_route'], b['build_record']), ('pinned', None))
        self.assertEqual(sr.check_program(self.pin, None, self.repo), ('pinned', sha(self.program)))
        self.assertEqual(self.replayed, [])

    def test_a_foreign_harness_source_is_refused_before_the_build_record_is_looked_at(self):
        os.remove(self.cloud + '.build.json')
        write(os.path.join(self.repo, 'rl', 'strength', 'Cargo.toml'), '[package]\nname = "other"\n')
        with self.assertRaises(SystemExit) as cm:
            sr.check_program(self.pin, self.cloud, self.repo)
        self.assertIn('the harness source in this checkout', cm.exception.code)
        self.assertNotIn('build record', cm.exception.code)
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertIn('the harness source in this checkout', str(code))
        self.assertNotIn('build record', str(code), 'the same order on the command line: the harness source first')
        self.assertFalse(os.path.exists(self.out_root))

    def test_build_config_describes_a_rebuild_in_the_engine_string_and_carries_the_build_record_and_the_pin_state(self):
        kw = dict(pin=self.pin, pin_path=self.pin_path, deck_rel='decks/events/my-list.txt', deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=1, paired=True,
                  seed_base=BLOCK[0], threads=2, program_sha='b' * 64)
        pinned = sr.build_config(**kw)
        self.assertEqual(pinned['engine'], self.pin['engine'])
        self.assertNotIn('engine_tree_in_checkout', pinned['slow_report'])
        self.assertEqual([pinned['slow_report'][k] for k in ('build_record', 'pin_committed', 'pin_committed_detail', 'registered_on')], [None] * 4, 'nothing was passed, nothing is claimed')
        rec = dict(self.build_record(self.cloud, rustc=f'{self.RUSTC}\nbinary: rustc\nhost: elsewhere'), record_file=self.cloud + '.build.json', record_sha256='d' * 64)
        yes = dict(state='yes', sha256=sha(self.pin_path), detail='')
        rebuilt = sr.build_config(**kw, route='rebuilt', program='/cloud/strength', build_record=rec, pin_state=yes, registered_on='cloud-box-9')

        def engine_text(digests):
            return (self.pin['engine'] + f"; THIS PROGRAM (/cloud/strength, sha256 bbbbbbbbbbbb) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a "
                                         f"rebuild of that source (build record sha256 dddddddddddd: engine tree as archived {self.pin['engine_tree'][:12]}, harness source "
                                         f"{self.pin['harness_source_sha256'][:12]}, {self.RUSTC}), accepted because both self-checks were replayed on the registering machine and equal {digests}")
        self.assertEqual(rebuilt['engine'], engine_text(COMMITTED_DIGESTS))
        b = rebuilt['slow_report']
        self.assertEqual((b['build_record'], b['pin_committed'], b['pin_committed_detail'], b['registered_on']), (rec, 'yes', None, 'cloud-box-9'), 'no detail when the pin is the committed one')
        no_head = dict(state='bypassed', sha256=sha(self.pin_path), detail='HEAD has no pin; allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)')
        b = sr.build_config(**kw, pin_state=no_head)['slow_report']
        self.assertEqual((b['pin_committed'], b['pin_committed_detail']), ('bypassed', no_head['detail']))
        self.assertEqual(sr.build_config(**kw, route='rebuilt')['engine'].split('THIS PROGRAM (')[1].split(',')[0], self.pin['program'], 'with no program given, the pin\'s path')
        # the words for what the self-checks were equal to follow the state of the pin: the committed pin's digests, or the pin file in use when it was let through for a test
        for label, state, digests in (('a committed pin', yes, COMMITTED_DIGESTS), ('a pin let through', no_head, FILE_DIGESTS), ('no state recorded', None, FILE_DIGESTS)):  # (not "committed" either)
            with self.subTest(label):
                engine = sr.build_config(**kw, route='rebuilt', program='/cloud/strength', build_record=rec, pin_state=state)['engine']
                self.assertEqual(engine, engine_text(digests))
                self.assertEqual(engine.count('NOT the committed pin'), 0 if digests == COMMITTED_DIGESTS else 1)
        self.assertEqual(sr.build_config(**kw, route='pinned', pin_state=no_head)['engine'], self.pin['engine'], 'the pinned binary is described as the pin describes it, whatever the state')

    def test_a_record_with_only_the_checked_entries_never_prints_none_in_the_engine_text_or_the_config(self):
        """The engine text says what the record says of the toolchain; a record that leaves it out (a hand-made one, or one from before the entry existed) says 'toolchain not recorded', and
        never ', not recorded)' (a clause with no subject)."""
        kw = dict(pin=self.pin, pin_path=self.pin_path, deck_rel='decks/events/my-list.txt', deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=1, paired=True,
                  seed_base=BLOCK[0], threads=2, program_sha='b' * 64, route='rebuilt', program='/cloud/strength')
        bare = dict(schema=1, program_sha256='b' * 64, engine_ref=self.pin['engine_ref'], engine_tree_archived=self.pin['engine_tree'], harness_source_sha256=self.pin['harness_source_sha256'],
                    record_file='/cloud/strength.build.json', record_sha256='d' * 64)
        for label, rec in (('only the checked entries', bare), ('null where text is expected', dict(bare, rustc=None, cargo=None, host=None)), ('an empty rustc', dict(bare, rustc='')),
                           ('a rustc of blank lines only', dict(bare, rustc='\n  \n\t\n')), ('a rustc that is a number', dict(bare, rustc=5)), ('a rustc that is a list', dict(bare, rustc=['rustc 1.90.0']))):
            with self.subTest(label):
                engine = sr.build_config(**kw, build_record=rec)['engine']
                self.assertNotIn('None', engine)
                self.assertIn(f"harness source {self.pin['harness_source_sha256'][:12]}, toolchain not recorded), accepted because", engine)
                self.assertNotIn(', not recorded)', engine)
                self.assertNotIn('built with', engine, 'that is the wording of the plan line, not of the engine text')
        full = sr.build_config(**kw, build_record=dict(bare, rustc='rustc 1.90.0 (fake)\nbinary: rustc'))['engine']
        self.assertIn(f"harness source {self.pin['harness_source_sha256'][:12]}, rustc 1.90.0 (fake)), accepted because", full)
        self.assertNotIn('not recorded', full, 'a recorded toolchain is printed, its first line')
        blank_first = sr.build_config(**kw, build_record=dict(bare, rustc='\n   \nrustc 1.90.0 (fake)\nbinary: rustc'))['engine']
        self.assertIn(f"harness source {self.pin['harness_source_sha256'][:12]}, rustc 1.90.0 (fake)), accepted because", blank_first, 'the first line that says anything, not an empty first line')
        self.assertNotIn('not recorded', blank_first)

    def test_a_rebuild_whose_record_has_only_the_checked_entries_is_described_with_not_recorded_in_the_plan_the_engine_text_and_the_page_and_never_as_none(self):
        text_keys = ('engine_arg', 'engine', 'rustc', 'cargo', 'machine', 'host', 'built_at', 'rebuild_command')
        everything_else = ('program', 'libc', 'home', 'cargo_home', 'build_dir', 'target_dir', 'jobs')
        for label, over in (('entries left out', {k: DROP for k in text_keys + everything_else}), ('entries null', {k: None for k in text_keys}),
                            ('entries empty', {k: '' for k in text_keys})):
            with self.subTest(label):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.write_record(self.cloud, **over)
                code, out, err = self.cli('--deals', '1', '--program', self.cloud, '--register-only')
                self.assertEqual(code, 0, out + err)
                d = self.rundir()
                man = self.manifest(d)
                rec = man['slow_report']['build_record']
                self.assertEqual(man['engine'], self.rebuilt_engine_text(self.cloud, rec))
                self.assertIn(f"harness source {self.pin['harness_source_sha256'][:12]}, toolchain not recorded), accepted because", man['engine'])
                lines = [l.split('] ', 1)[1] for l in out.splitlines()]
                (plan,) = [l for l in lines if l.startswith(f'program {self.cloud} (sha256 ') and 'is NOT the pinned binary' in l]
                self.assertIn(f"harness source {self.pin['harness_source_sha256'][:12]}, built with an unrecorded toolchain); both self-checks will be replayed", plan)
                self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
                page = read(os.path.join(d, 'SLOW_REPORT.md'))
                self.assertIn(f"\n- Build record `strength.build.json` sha256 `{rec['record_sha256'][:12]}`: engine not recorded -> tree as archived `{self.pin['engine_tree'][:12]}` "
                              f"(the pin's is `{self.pin['engine_tree'][:12]}`), harness source `{self.pin['harness_source_sha256'][:12]}`, rustc not recorded, not recorded, built not recorded on "
                              "not recorded (not recorded); to rebuild the same bytes after a restart: `not recorded`.\n", page)
                for what, text in (('the engine text', man['engine']), ('the plan', '\n'.join(lines)), ('the page', page.replace('repository commit `None`', ''))):  # (the fixture's repository has no commit)
                    self.assertNotIn('None', text, what)
                    self.assertNotIn('built with not recorded', text, what)
                    self.assertNotIn(', not recorded)', text, what)
                self.assertNotIn('built with', page, 'the plan\'s "built with ..." is not the page\'s wording')


PIN_REL = 'rl/strength/slow_report_pin.json'  # where the committed pin lives in a checkout (the pin file of a real run is that file)
RECORD_HINT = 'rl/strength/build.sh writes it beside the program it builds (build with it, to the path you pass here)'


def git_said(repo):
    """What follows the fixed words of the detail of a pin that git could not find in `repo` ('; git said: <the first line git printed>'), worked out by asking the installed git the
    same question pin_commit_state asks (`git -C repo cat-file blob HEAD:./rl/strength/slow_report_pin.json`), so the line is git's own whatever its version. Empty when git printed
    nothing. The folders of these tests are made by this user, so a safe.directory complaint is no part of it (the test says so instead of guessing)."""
    r = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], capture_output=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    said = r.stderr.decode('utf-8', 'replace').strip()
    assert 'safe.directory' not in said, f'git itself calls {repo} unsafe: {said}'
    return f'; git said: {said.splitlines()[0][:200]}' if said else ''


class CommittedPin(RebuiltFixture):
    """The pin in use must be the pin that is committed: byte-equal to HEAD's rl/strength/slow_report_pin.json in the repository the run is made from (pin_commit_state,
    require_committed_pin). A hand-edited pin, `--pin copy.json`, a pin that was never committed, a folder that is no git repository and a machine without git are all refused before
    anything is written, because everything a report says about the program rests on the pin. The test-only variable SLOW_REPORT_ALLOW_UNCOMMITTED_PIN lets a hand-made pin through,
    and the plan, the registration and the page say so. World sets that variable for every test; the tests of this class take it away (except where it is the thing under test)."""
    BYPASS = f'; allowed by {ALLOW_PIN_VAR} (test use)'

    def setUp(self):
        super().setUp()
        os.environ.pop(ALLOW_PIN_VAR, None)  # (World's patch of os.environ puts it back as it was when the test ends)
        self.original_pin = self.pin_path

    def state(self, pin=None, repo=None):
        return sr.pin_commit_state(repo or self.repo, pin or self.pin_path)

    def not_in_head(self, repo=None):
        """The detail of a pin git cannot find: the fixed words, then what git said (git_said: the installed git's own first line)."""
        return f'HEAD has no {PIN_REL} in {repo or self.repo} (not a git repository, no commit, or the file is not committed)' + git_said(repo or self.repo)

    def differs(self, pin, head_bytes):
        return f'the pin file (sha256 {sha(pin)[:12]}) differs from the {PIN_REL} committed at HEAD (sha256 {hashlib.sha256(head_bytes).hexdigest()[:12]})'

    def refusal(self, detail):
        return (f'REFUSED: the pin is not the committed one: {detail}. A slow report trusts the pin for what the program is, so it uses only {PIN_REL} as committed at HEAD '
                '(commit the pin, in the repository you run from; a hand-edited or copied pin is refused). Nothing was written.')

    def tree(self):
        """Every file and folder under the test's temporary folder, with size and modification time: a run that must write nothing leaves this as it was."""
        out = []
        for dp, dn, fn in os.walk(self.tmp):
            for n in dn + fn:
                st = os.lstat(os.path.join(dp, n))
                out.append((os.path.relpath(os.path.join(dp, n), self.tmp), st.st_size, st.st_mtime_ns))
        return sorted(out)

    def scenarios(self):
        """(label, repository, pin file, the detail of why it is not the committed pin): the ways a pin fails to be the committed one, each in a folder of its own."""
        out = []

        def place(name):
            repo = os.path.join(self.tmp, 'scenario', name)
            os.makedirs(repo)
            return repo
        a = place('no-git')
        out.append(('not a git repository', a, self.original_pin, self.not_in_head(a)))
        b = place('no-commit')
        self.git('init', '-q', repo=b)
        out.append(('a git repository with no commit', b, self.original_pin, self.not_in_head(b)))
        c = place('other-file')
        self.git('init', '-q', repo=c)
        write(os.path.join(c, 'other.txt'), 'x\n')
        self.git('add', 'other.txt', repo=c)
        self.git('commit', '-q', '-m', 'x', repo=c)
        out.append(('a commit without the pin', c, self.original_pin, self.not_in_head(c)))
        d = place('staged-only')
        self.git('init', '-q', repo=d)
        write(os.path.join(d, 'other.txt'), 'x\n')
        self.git('add', 'other.txt', repo=d)
        self.git('commit', '-q', '-m', 'x', repo=d)
        write_bytes(os.path.join(d, *PIN_REL.split('/')), self.bytes_of(self.original_pin))
        self.git('add', PIN_REL, repo=d)
        out.append(('the pin added but not committed', d, os.path.join(d, *PIN_REL.split('/')), self.not_in_head(d)))
        e = place('edited')
        head = self.bytes_of(self.original_pin)
        path = self.commit_pin(repo=e)
        edited = json.loads(head)
        edited['threads'] = 7
        write(path, json.dumps(edited, indent=1))
        out.append(('the committed pin edited by hand', e, path, self.differs(path, head)))
        gone = os.path.join(self.tmp, 'scenario', 'no-such-folder')
        out.append(('a repository folder that does not exist', gone, self.original_pin, self.not_in_head(gone)))
        return out

    # ------------------------------------------------------------------------------------------------ pin_commit_state and require_committed_pin
    def test_the_names_the_check_goes_by(self):
        self.assertEqual(sr.ALLOW_UNCOMMITTED_PIN, ALLOW_PIN_VAR)
        self.assertEqual(sr.PIN_REL, PIN_REL)
        self.assertEqual(os.path.abspath(sr.DEFAULT_PIN), os.path.join(ROOT, *PIN_REL.split('/')), 'the default pin is the committed file')

    def test_a_pin_byte_equal_to_the_committed_one_is_yes_whatever_its_path(self):
        committed = self.commit_pin()
        want = {'state': 'yes', 'sha256': sha(self.original_pin), 'detail': ''}
        self.assertEqual(self.state(), want)
        self.assertEqual(self.state(committed), want, 'the committed file itself, which is the pin of a real run')
        copy = os.path.join(self.tmp, 'elsewhere', 'copy.json')
        write_bytes(copy, self.bytes_of(self.original_pin))
        self.assertEqual(self.state(copy), want, 'a byte-identical copy elsewhere: the bytes decide, not the path')
        self.assertEqual(sr.require_committed_pin(self.repo, copy), want)

    def test_one_changed_byte_makes_the_pin_not_the_committed_one(self):
        self.commit_pin()
        head = self.bytes_of(self.original_pin)
        edited = json.loads(head)
        edited['program_sha256'] = '1' * 64  # the edit that would make any program look pinned
        copy = os.path.join(self.tmp, 'elsewhere', 'copy.json')
        for label, data in (('a changed value', json.dumps(edited, indent=1).encode()), ('a trailing newline', head + b'\n'), ('Windows line ends', head.replace(b'\n', b'\r\n')),
                            ('one byte less', head[:-1]), ('a space after the first brace', head.replace(b'{', b'{ ', 1))):
            write_bytes(copy, data)
            self.assertEqual(self.state(copy), {'state': 'no', 'sha256': sha(copy), 'detail': self.differs(copy, head)}, label)

    def test_the_pin_is_compared_with_head_not_with_the_work_tree_or_the_index(self):
        committed = self.commit_pin()
        head = self.bytes_of(committed)
        edited = json.loads(head)
        edited['threads'] = 7
        write(committed, json.dumps(edited, indent=1))
        self.assertEqual(self.state(committed)['state'], 'no', 'edited in the work tree')
        self.git('add', PIN_REL)
        self.assertEqual(self.state(committed), {'state': 'no', 'sha256': sha(committed), 'detail': self.differs(committed, head)}, 'and staged: HEAD is what counts')
        self.git('commit', '-q', '-m', 'the edit is committed')
        self.assertEqual(self.state(committed), {'state': 'yes', 'sha256': sha(committed), 'detail': ''}, 'committed: now it is the one')

    def test_a_pin_that_was_never_committed_is_no_in_every_shape_of_that(self):
        for label, repo, pin, detail in self.scenarios():
            with self.subTest(label):
                self.assertEqual(self.state(pin, repo), {'state': 'no', 'sha256': sha(pin), 'detail': detail})
                with self.assertRaises(SystemExit) as cm:
                    sr.require_committed_pin(repo, pin)
                self.assertEqual(cm.exception.code, self.refusal(detail))

    def test_the_pin_is_looked_for_at_its_path_inside_the_folder_given_not_at_the_top_of_the_checkout(self):
        top = os.path.join(self.tmp, 'top')
        sub = os.path.join(top, 'sub')
        os.makedirs(sub)
        self.git('init', '-q', repo=top)
        self.commit_pin(repo=sub)
        self.assertEqual(self.state(repo=sub)['state'], 'yes', 'the checkout of a run can be a folder inside a larger repository')
        self.assertEqual(self.state(repo=top), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': self.not_in_head(top)}, 'the same pin is not committed at the top')

    def test_without_git_the_committed_pin_cannot_be_read_and_the_pin_is_not_accepted(self):
        self.commit_pin()
        nowhere = os.path.join(self.tmp, 'empty-path')
        os.makedirs(nowhere)
        detail = 'git is not available, so the committed pin cannot be read'
        with mock.patch.dict(os.environ, {'PATH': nowhere}):
            self.assertEqual(self.state(), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': detail})
            with self.assertRaises(SystemExit) as cm:
                sr.require_committed_pin(self.repo, self.original_pin)
        self.assertEqual(cm.exception.code, self.refusal(detail))
        with mock.patch.dict(os.environ, {'PATH': nowhere, ALLOW_PIN_VAR: '1'}):
            self.assertEqual(self.state(), {'state': 'bypassed', 'sha256': sha(self.original_pin), 'detail': detail + self.BYPASS})

    # ------------------------------------------------------------------------------------------------ what git said
    def git_stub(self, stderr, code=128, stdout=b''):
        """A `git` that is found before the real one (PATH of the returned environment patch): it prints `stdout`, then `stderr` on the error stream, and exits with `code`. Use it as
        `with mock.patch.dict(os.environ, self.git_stub(...)):`."""
        folder = os.path.join(self.tmp, 'stub-git')
        os.makedirs(folder, exist_ok=True)
        write_bytes(os.path.join(folder, 'said_out.bin'), stdout)
        write_bytes(os.path.join(folder, 'said_err.txt'), stderr if isinstance(stderr, bytes) else stderr.encode('utf-8'))
        write(os.path.join(folder, 'git'), f'#!/bin/sh\ncat "${{0%/*}}/said_out.bin"\ncat "${{0%/*}}/said_err.txt" >&2\nexit {code}\n', mode=0o755)
        return {'PATH': folder + os.pathsep + os.environ.get('PATH', '')}

    def dubious(self, repo=None):
        repo = repo or self.repo
        return (f"fatal: detected dubious ownership in repository at '{repo}'\nTo add an exception for this directory, call:\n\n\tgit config --global --add safe.directory {repo}\n")

    def unsafe_detail(self, repo=None):
        """The detail git's refusal of a folder owned by another user gets: git's own first line, then the explanation that this is not the pin being uncommitted."""
        repo = repo or self.repo
        return (f"HEAD has no {PIN_REL} in {repo} (not a git repository, no commit, or the file is not committed); git said: fatal: detected dubious ownership in repository at '{repo}' "
                f'(git refuses this folder as unsafe, which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory {repo})')

    def test_a_folder_git_refuses_as_unsafe_is_said_to_be_unsafe_and_not_uncommitted(self):
        """A checkout owned by another user (a root container on the cloud): git exits non-zero for the pin that may well be committed, and the detail says what git said and that it is not the same."""
        self.commit_pin()
        with mock.patch.dict(os.environ, self.git_stub(self.dubious())):
            self.assertEqual(self.state(), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': self.unsafe_detail()})
            with self.assertRaises(SystemExit) as cm:
                sr.require_committed_pin(self.repo, self.original_pin)
            self.assertEqual(cm.exception.code, self.refusal(self.unsafe_detail()))
            self.assertIn(f'if you trust it: git config --global --add safe.directory {self.repo})', cm.exception.code)
        with mock.patch.dict(os.environ, dict(self.git_stub(self.dubious()), **{ALLOW_PIN_VAR: '1'})):
            self.assertEqual(self.state(), {'state': 'bypassed', 'sha256': sha(self.original_pin), 'detail': self.unsafe_detail() + self.BYPASS})
        self.assertEqual(self.state()['state'], 'yes', 'with the real git the same folder and pin are fine')

    def test_the_command_line_refuses_an_unsafe_folder_with_the_advice_and_writes_nothing(self):
        with mock.patch.dict(os.environ, self.git_stub(self.dubious())):
            before = self.tree()
            for extra in ((), ('--dry-run',), ('--register-only',)):
                code, out, err = self.cli('--deals', '1', *extra)
                self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.unsafe_detail()), extra)
                self.assertEqual((out, err), ('', ''))
                self.assertFalse(os.path.exists(self.out_root))
            self.assertEqual(self.tree(), before, 'nothing was written')

    def test_the_advice_for_an_unsafe_folder_quotes_a_folder_name_with_a_space_so_it_can_be_pasted(self):
        """The advice 'git config --global --add safe.directory <repo>' is a command to paste: a checkout under a path with a space (the laptop's 'Pocket Deck Sim' folder) is quoted for the
        shell (shlex.quote), so git gets one argument; the folder is named unquoted in the words around it, and a path that needs no quoting is printed as it is."""
        repo = os.path.join(self.tmp, 'a folder with spaces')
        with mock.patch.dict(os.environ, self.git_stub(self.dubious(repo))):
            detail = sr.pin_commit_state(repo, self.original_pin)['detail']
        self.assertIn(f'git config --global --add safe.directory {shlex.quote(repo)})', detail)
        self.assertEqual(detail, f"HEAD has no {PIN_REL} in {repo} (not a git repository, no commit, or the file is not committed); git said: fatal: detected dubious ownership in repository "
                                 f"at '{repo}' (git refuses this folder as unsafe, which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory "
                                 f"'{repo}')")
        self.assertNotIn(f'safe.directory {repo})', detail, 'not the bare path, which git would read as several arguments')
        self.assertEqual(shlex.quote(self.repo), self.repo, 'the folders of the other tests of this class need no quoting, and are printed as they are')

    def test_the_advice_for_an_unsafe_folder_survives_a_shell_for_every_kind_of_name(self):
        """Whatever the folder is called, the shell reads the end of the advice back as that one folder."""
        for label, name in (('a space', 'my repo'), ('a single quote', "it's here"), ('a dollar sign', 'cost$HOME'), ('a semicolon', 'a;b'), ('a backtick', 'a`b'), ('an accent', 'café'),
                            ('a leading dash', '-x'), ('two spaces and a tab', 'a  b\tc')):
            repo = os.path.join(self.tmp, name)
            with self.subTest(label), mock.patch.dict(os.environ, self.git_stub(self.dubious(repo))):
                detail = sr.pin_commit_state(repo, self.original_pin)['detail']
                tail = detail.split('git config --global --add safe.directory ', 1)[1]
                self.assertTrue(tail.endswith(')'), tail)
                self.assertEqual(shlex.split(tail[:-1]), [repo])

    def test_a_folder_that_is_not_a_git_repository_gets_git_s_line_but_not_the_unsafe_advice(self):
        said = 'fatal: not a git repository (or any of the parent directories): .git\n'
        with mock.patch.dict(os.environ, self.git_stub(said)):
            st = self.state()
        self.assertEqual(st['detail'], f'HEAD has no {PIN_REL} in {self.repo} (not a git repository, no commit, or the file is not committed); git said: fatal: not a git repository '
                                       '(or any of the parent directories): .git')
        self.assertNotIn('unsafe', st['detail'])
        self.assertNotIn('safe.directory', st['detail'])

    def test_a_git_that_prints_nothing_adds_nothing(self):
        for label, said in (('nothing', ''), ('only spaces and line ends', '  \n\n \t\n')):
            with self.subTest(label), mock.patch.dict(os.environ, self.git_stub(said, code=1)):
                self.assertEqual(self.state(), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': self.not_in_head_words()})

    def not_in_head_words(self, repo=None):
        """The fixed words of the detail alone."""
        return f'HEAD has no {PIN_REL} in {repo or self.repo} (not a git repository, no commit, or the file is not committed)'

    def test_only_the_first_line_git_printed_is_said_and_at_most_200_characters_of_it(self):
        words = self.not_in_head_words()
        with mock.patch.dict(os.environ, self.git_stub('\n\nfatal: the first line\nand a second one\nand a third\n')):
            self.assertEqual(self.state()['detail'], words + '; git said: fatal: the first line', 'blank lines before it are not counted, the lines after it are left out')
        with mock.patch.dict(os.environ, self.git_stub('fatal: ' + 'x' * 300 + '\n')):
            self.assertEqual(self.state()['detail'], words + '; git said: fatal: ' + 'x' * 193, 'cut at 200 characters of the line')
        with mock.patch.dict(os.environ, self.git_stub('y' * 200 + '\n')):
            self.assertEqual(self.state()['detail'], words + '; git said: ' + 'y' * 200, '200 characters are kept whole')
        with mock.patch.dict(os.environ, self.git_stub('fatal: café – not here\n')):
            self.assertEqual(self.state()['detail'], words + '; git said: fatal: café – not here', 'any text git prints is kept as it is')
        with mock.patch.dict(os.environ, self.git_stub(b'fatal: \xff\xfe bytes\n')):
            self.assertEqual(self.state()['detail'], words + '; git said: fatal: �� bytes', 'bytes that are not UTF-8 are read with replacement characters and never stop the check')

    def test_the_unsafe_advice_is_added_when_the_word_is_anywhere_in_what_git_printed(self):
        """Git puts the name of the setting on a later line than its first complaint: the advice follows the whole of what it printed, not its first line."""
        repo = self.repo
        advice = (f' (git refuses this folder as unsafe, which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory {repo})')
        for label, said, first in (('on a later line', "fatal: detected dubious ownership in repository\nuse safe.directory to allow it\n", 'fatal: detected dubious ownership in repository'),
                                   ('on the first line', 'fatal: add this folder to safe.directory\n', 'fatal: add this folder to safe.directory'),
                                   ('beyond the 200 characters that are shown', 'fatal: ' + 'z' * 250 + ' safe.directory\n', 'fatal: ' + 'z' * 193)):
            with self.subTest(label), mock.patch.dict(os.environ, self.git_stub(said)):
                self.assertEqual(self.state()['detail'], self.not_in_head_words() + f'; git said: {first}' + advice)
        with mock.patch.dict(os.environ, self.git_stub('fatal: detected dubious ownership in repository\nfatal: something else\n')):
            self.assertNotIn('unsafe', self.state()['detail'], 'dubious ownership alone, without the name of the setting, is not the advice: git did not offer one')

    def test_what_a_git_that_succeeds_printed_on_the_error_stream_is_not_said(self):
        self.commit_pin()
        with mock.patch.dict(os.environ, self.git_stub('warning: safe.directory is set oddly here\n', code=0, stdout=self.bytes_of(self.original_pin))):
            self.assertEqual(self.state(), {'state': 'yes', 'sha256': sha(self.original_pin), 'detail': ''})
        with mock.patch.dict(os.environ, self.git_stub('warning: safe.directory is set oddly here\n', code=0, stdout=b'another pin\n')):
            st = self.state()
        self.assertEqual(st['state'], 'no')
        self.assertTrue(st['detail'].startswith(f'the pin file (sha256 {sha(self.original_pin)[:12]}) differs from the {PIN_REL} committed at HEAD (sha256 '), st['detail'])
        self.assertNotIn('git said', st['detail'])
        self.assertNotIn('safe.directory', st['detail'])

    def test_the_test_only_variable_turns_every_no_into_bypassed_and_says_why(self):
        scenarios = self.scenarios()
        for value in ('1', 'yes', 'any text at all'):
            with mock.patch.dict(os.environ, {ALLOW_PIN_VAR: value}):
                for label, repo, pin, detail in scenarios:
                    with self.subTest(label=label, value=value):
                        st = self.state(pin, repo)
                        self.assertEqual(st, {'state': 'bypassed', 'sha256': sha(pin), 'detail': detail + self.BYPASS})
                        self.assertEqual(sr.require_committed_pin(repo, pin), st, 'a bypassed pin goes on (and is recorded as bypassed)')
        with mock.patch.dict(os.environ, {ALLOW_PIN_VAR: ''}):
            for label, repo, pin, detail in scenarios:
                with self.subTest(label=label, value='empty'):
                    self.assertEqual(self.state(pin, repo)['state'], 'no', 'an empty value is not a switch')

    def test_the_variable_changes_nothing_for_a_pin_that_is_the_committed_one(self):
        self.commit_pin()
        with mock.patch.dict(os.environ, {ALLOW_PIN_VAR: '1'}):
            self.assertEqual(self.state(), {'state': 'yes', 'sha256': sha(self.original_pin), 'detail': ''})

    def test_the_refusal_is_in_these_words_and_only_a_no_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            sr.require_committed_pin(self.repo, self.original_pin)
        self.assertEqual(cm.exception.code, self.refusal(self.not_in_head()))
        self.commit_pin()
        self.assertEqual(sr.require_committed_pin(self.repo, self.original_pin)['state'], 'yes')

    # ------------------------------------------------------------------------------------------------ on the command line
    def test_a_new_registration_a_dry_run_and_register_only_are_refused_when_the_pin_is_not_committed_and_nothing_is_written(self):
        before = self.tree()
        for extra in ((), ('--dry-run',), ('--register-only',)):
            code, out, err = self.cli('--deals', '1', *extra)
            self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.not_in_head()), extra)
            self.assertEqual((out, err), ('', ''), 'refused before the first line of the plan')
            self.assertFalse(os.path.exists(self.out_root), extra)
        self.assertEqual(self.tree(), before, 'nothing was written anywhere')
        self.assertEqual(self.replayed, [])

    def test_the_pin_is_checked_before_the_program_is_looked_at(self):
        write(self.program, FAKE_PROGRAM + '\n# changed\n', mode=0o755)  # not the pinned build: check_program would refuse it
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.not_in_head()))
        os.remove(self.program)
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.not_in_head()), 'and before the build record, the harness source and the self-check replays')
        os.remove(self.cloud + '.build.json')
        code, out, err = self.cli('--deals', '1', '--program', self.cloud)
        self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.not_in_head()))
        self.assertEqual(self.replayed, [])
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_hand_edited_pin_and_a_pin_copy_are_refused_and_a_byte_identical_copy_is_not(self):
        self.commit_pin()
        head = self.bytes_of(self.original_pin)
        edited = json.loads(head)
        edited['program_sha256'] = sha(self.program)  # (the edit that makes this program look pinned)
        edited['threads'] = 3
        hand = os.path.join(self.tmp, 'mine', 'pin.json')
        write(hand, json.dumps(edited, indent=1))
        self.pin_path = hand
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(self.differs(hand, head)))
        self.assertFalse(os.path.exists(self.out_root))
        same = os.path.join(self.tmp, 'mine', 'copy.json')
        write_bytes(same, head)
        self.pin_path = same
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'pin committed: yes ({PIN_REL} sha256 {sha(same)[:12]}; byte-equal to HEAD)', out)

    def test_a_committed_pin_registers_and_the_plan_the_manifest_the_preregistration_and_the_page_say_so(self):
        self.commit_pin()
        psha = sha(self.original_pin)
        with mock.patch.object(socket, 'gethostname', return_value='registering-box'):
            code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        want = f'pin committed: yes ({PIN_REL} sha256 {psha[:12]}; byte-equal to HEAD)'
        self.assertEqual(lines.count(want), 1)
        i = lines.index(want)
        self.assertTrue(lines[i - 1].startswith('school-morning rule: OFF') and lines[i + 1].startswith('stage use'), 'after the size and school lines, before the stage line')
        d = self.rundir()
        b = self.manifest(d)['slow_report']
        self.assertEqual((b['pin_committed'], b['pin_committed_detail'], b['registered_on']), ('yes', None, 'registering-box'), 'no detail for a pin that is the committed one')
        self.assertEqual(b['pin'], {'path': self.original_pin, 'sha256': psha})
        prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertIn('\n- pin_committed: `yes`\n', prereg)
        self.assertIn('\n- registered_on: `registering-box`\n', prereg)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertIn(f"\n- Pin `{self.original_pin}` sha256 `{psha[:12]}`: committed (byte-equal to HEAD's file in the repository this run was registered from).\n", page)
        self.assertNotIn('NOT the committed pin', page)

    def test_a_pin_let_through_by_the_variable_is_registered_as_bypassed_and_the_plan_the_preregistration_and_the_page_say_so(self):
        os.environ[ALLOW_PIN_VAR] = '1'
        psha = sha(self.original_pin)
        detail = self.not_in_head() + self.BYPASS
        with mock.patch.object(socket, 'gethostname', return_value='registering-box'):
            code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertEqual(lines.count(f'pin committed: bypassed ({PIN_REL} sha256 {psha[:12]}; {detail})'), 1, lines)
        d = self.rundir()
        b = self.manifest(d)['slow_report']
        self.assertEqual((b['pin_committed'], b['pin_committed_detail'], b['registered_on']), ('bypassed', detail, 'registering-box'))
        prereg = read(os.path.join(d, 'PREREGISTRATION.md'))
        for line in ('- pin_committed: `bypassed`', f'- pin_committed_detail: `{detail}`', '- registered_on: `registering-box`'):
            self.assertIn('\n' + line + '\n', prereg)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertIn(f'\n- Pin `{self.original_pin}` sha256 `{psha[:12]}`: **NOT the committed pin** ({detail}): what this page says about the program rests on a pin that is not the committed one.\n', page)
        self.assertNotIn('byte-equal', page)

    def test_a_rebuild_registered_with_the_committed_pin_says_the_committed_pins_digests_in_every_place_and_a_bypassed_pin_does_not(self):
        """The engine text, the registered source of the self-check texts, PREREGISTRATION.md, the plan and the page all name what the self-checks were equal to by the state of the pin."""
        for state, digests, committed in (('yes', COMMITTED_DIGESTS, True), ('bypassed', FILE_DIGESTS, False)):
            with self.subTest(state):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                if state == 'yes':
                    self.commit_pin()
                    os.environ.pop(ALLOW_PIN_VAR, None)
                else:
                    os.environ[ALLOW_PIN_VAR] = '1'
                with mock.patch.object(socket, 'gethostname', return_value='registering-box'):
                    code, out, err = self.cli('--deals', '1', '--program', self.cloud)
                self.assertEqual(code, 0, (state, out + err))
                d = self.rundir()
                man = self.manifest(d)
                rec = dict(self.build_record(self.cloud), record_file=self.cloud + '.build.json', record_sha256=sha(self.cloud + '.build.json'))
                lines, prereg, page = [l.split('] ', 1)[1] for l in out.splitlines()], read(os.path.join(d, 'PREREGISTRATION.md')), read(os.path.join(d, 'SLOW_REPORT.md'))
                self.assertEqual(man['slow_report']['pin_committed'], state)
                self.assertEqual(man['engine'], self.rebuilt_engine_text(self.cloud, rec, digests))
                phrase = 'the committed pin' if committed else 'the pin file in use, which is NOT the committed pin: test use'
                self.assertEqual(man['selfcheck_source'], {s: f'replayed by slow_report.py on the registering machine just before registration (equal to {phrase})' for s in ('km3', 'kx3')})
                self.assertEqual(prereg.count(f'(replayed by slow_report.py on the registering machine just before registration and equal to {phrase})'), 2, 'PREREGISTRATION.md')
                plan = (f'program {self.cloud} (sha256 {sha(self.cloud)[:12]}) is NOT the pinned binary (sha256 {sha(self.program)[:12]}): its build record '
                        f"(strength.build.json, sha256 {rec['record_sha256'][:12]}) says it is a rebuild of the pinned source (engine tree as archived {self.pin['engine_tree'][:12]}, "
                        f"harness source {self.pin['harness_source_sha256'][:12]}, built with {self.RUSTC}); both self-checks will be replayed on this machine against {digests} "
                        "before anything is registered (hours for kx3), and the checkout's harness source equals the pinned build's")
                self.assertEqual(lines.count(plan), 1, 'the plan names what the replay will be compared with')
                self.assertIn('\n- ' + self.REBUILD_LINE.format(pinned=self.program, sha12=sha(self.program)[:12], host='registering-box', digests=digests) + '\n', page)
                how = 'replayed on the registering machine just before registration, equal to ' + ('the committed pin' if committed else 'the pin file in use (NOT the committed pin: test use)')
                self.assertEqual(page.count(f'({how})'), 2, 'the Self-check lines')
                self.assertNotIn('None', page.replace('repository commit `None`', ''), 'a repository with no commit has none to name: that line is the only place for the word')
                for text in (man['engine'], prereg, page, '\n'.join(lines)):
                    if committed:
                        self.assertNotIn('NOT the committed pin', text)
                    else:
                        self.assertIn('NOT the committed pin', text)

    def test_a_resume_a_report_only_and_a_dry_run_of_a_registered_run_do_not_need_the_committed_pin(self):
        self.commit_pin()
        self.assertEqual(self.cli('--deals', '1', '--max-games', '6')[0], 0)
        d = self.rundir()
        edited = json.loads(read(self.original_pin))
        edited['threads'] = 5
        write(self.original_pin, json.dumps(edited, indent=1))  # the pin on disk is no longer the committed one
        self.assertEqual(self.state()['state'], 'no')
        for extra in (('--dry-run',), ('--report-only',), ('--max-games', '6'), ()):
            code, out, err = self.cli('--dir', d, *extra, deck=False)
            self.assertEqual(code, 0, (extra, out, err))
            self.assertNotIn('not the committed one', out + err)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)

    def test_the_check_reads_the_repository_and_writes_nothing_into_it(self):
        self.commit_pin()
        before = self.tree()
        self.state()
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.tree(), before, 'git was asked to read and nothing was written, in .git or outside it')

    # ------------------------------------------------------------------------------------------------ the repository we were told about, whatever a git hook exported
    def other_repo_with(self, data):
        """A second repository (the one a git hook or `rebase --exec` leaves exported in GIT_DIR) with `data` committed as its pin."""
        other = os.path.join(self.tmp, 'other-repo')
        os.makedirs(other)
        self.commit_pin(data=data, repo=other)
        return other

    def exported(self, other):
        return exported_git_variables(self.tmp, other)

    def test_git_env_has_none_of_the_variables_that_choose_a_repository_and_has_optional_locks_off(self):
        self.assertEqual(sr.GIT_REPO_VARS, GIT_REPO_VARS)
        self.assertEqual(set(self.exported(self.tmp)), set(GIT_REPO_VARS), 'this test sets every one of them')
        polluted = dict(self.exported(self.tmp), GIT_OPTIONAL_LOCKS='1', GIT_AUTHOR_NAME='someone', GIT_CONFIG_NOSYSTEM='1', KEEP_ME='yes')
        with mock.patch.dict(os.environ, polluted):
            env = sr.git_env()
            for name in GIT_REPO_VARS:
                self.assertNotIn(name, env, name)
                self.assertIn(name, os.environ, f'{name}: the environment of this process itself is not changed')
            self.assertEqual(env['GIT_OPTIONAL_LOCKS'], '0', 'optional locks are off, whatever the process had')
            self.assertEqual(os.environ['GIT_OPTIONAL_LOCKS'], '1')
            self.assertEqual({k: env.get(k) for k in ('GIT_AUTHOR_NAME', 'GIT_CONFIG_NOSYSTEM', 'KEEP_ME')}, {'GIT_AUTHOR_NAME': 'someone', 'GIT_CONFIG_NOSYSTEM': '1', 'KEEP_ME': 'yes'},
                             'the other GIT_ variables and everything else are passed on')
            self.assertEqual(env, dict({k: v for k, v in os.environ.items() if k not in GIT_REPO_VARS}, GIT_OPTIONAL_LOCKS='0'), 'nothing else is added or taken away')
            env['KEEP_ME'] = 'changed'
            self.assertEqual(os.environ['KEEP_ME'], 'yes', 'a copy: changing it changes nothing here')

    def test_git_env_of_a_plain_environment_is_the_environment_and_optional_locks_off(self):
        with mock.patch.dict(os.environ):
            for name in GIT_REPO_VARS + ('GIT_OPTIONAL_LOCKS',):
                os.environ.pop(name, None)
            self.assertEqual(sr.git_env(), dict(os.environ, GIT_OPTIONAL_LOCKS='0'))

    def recording_git(self):
        return recording_git(self.tmp)

    def test_the_pin_is_read_with_git_env_whatever_the_process_has_exported(self):
        stub, calls = self.recording_git()
        other = self.other_repo_with(b'{"another": "pin"}\n')
        with mock.patch.dict(os.environ, dict(stub, **self.exported(other), GIT_OPTIONAL_LOCKS='1', GIT_AUTHOR_NAME='someone')):
            self.state()
        ((args, env),) = calls()
        self.assertEqual(args, f'-C {self.repo} cat-file blob HEAD:./{PIN_REL}')
        for name in GIT_REPO_VARS:
            self.assertNotIn(name, env, name)
        self.assertEqual((env['GIT_OPTIONAL_LOCKS'], env['GIT_AUTHOR_NAME']), ('0', 'someone'))

    def test_the_variables_a_git_hook_exports_do_not_move_the_check_to_another_repository(self):
        """`git -C repo` does not help when GIT_DIR is exported: a pin committed in this repository is judged by this repository's HEAD, not by the other one's."""
        self.commit_pin()
        other = self.other_repo_with(b'{"another": "pin"}\n')
        want = {'state': 'yes', 'sha256': sha(self.original_pin), 'detail': ''}
        self.assertEqual(self.state(), want)
        every = self.exported(other)
        for name, value in every.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(self.state(), want)
        with mock.patch.dict(os.environ, every):
            self.assertEqual(self.state(), want, 'all of them at once')
            self.assertEqual(sr.require_committed_pin(self.repo, self.original_pin), want)

    def test_a_pin_committed_only_in_the_repository_a_hook_exported_is_not_committed_here(self):
        """The dangerous direction: the pin is not committed in the repository given, but it is in the one GIT_DIR points to; it must not be taken as committed."""
        other = self.other_repo_with(self.bytes_of(self.original_pin))
        detail = self.not_in_head()  # (asked of the real git before anything is exported)
        every = self.exported(other)
        self.assertEqual(self.state(), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': detail})
        for name, value in every.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(self.state(), {'state': 'no', 'sha256': sha(self.original_pin), 'detail': detail})
        with mock.patch.dict(os.environ, every):
            with self.assertRaises(SystemExit) as cm:
                sr.require_committed_pin(self.repo, self.original_pin)
            self.assertEqual(cm.exception.code, self.refusal(detail))

    def test_the_command_line_judges_the_pin_by_the_repository_given_not_by_the_one_exported(self):
        other = self.other_repo_with(self.bytes_of(self.original_pin))
        detail = self.not_in_head()
        with mock.patch.dict(os.environ, {'GIT_DIR': os.path.join(other, '.git')}):
            before = self.tree()
            for extra in ((), ('--dry-run',), ('--register-only',)):
                code, out, err = self.cli('--deals', '1', *extra)
                self.assertEqual(code, '[kx3 (d513e37b) v km3] ' + self.refusal(detail), extra)
                self.assertEqual((out, err), ('', ''))
            self.assertEqual(self.tree(), before, 'nothing was written')
        self.commit_pin()  # and now the pin is committed here, while the exported repository holds another one: the one committed here is the one that counts
        elsewhere = os.path.join(self.tmp, 'elsewhere-repo')
        os.makedirs(elsewhere)
        self.commit_pin(data=b'{"another": "pin"}\n', repo=elsewhere)
        with mock.patch.dict(os.environ, {'GIT_DIR': os.path.join(elsewhere, '.git')}):
            code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'pin committed: yes ({PIN_REL} sha256 {sha(self.original_pin)[:12]}; byte-equal to HEAD)', out)


class BuildRecord(RebuiltFixture):
    """read_build_record(program, pin): the record rl/strength/build.sh writes beside a program (PROGRAM.build.json) must exist, be a schema 1 object, be for this exact file
    (program_sha256), and carry the pin's engine tree (as archived), the pin's harness source and, when both name one, the pin's engine commit; every refusal says so in words and
    ends 'Nothing was written.'. A rebuild without that record, or with another, is not the pinned source whatever its self-check says."""

    def path(self):
        return self.cloud + '.build.json'

    def refusal(self, program=None, pin=None):
        with self.assertRaises(SystemExit) as cm:
            sr.read_build_record(program or self.cloud, pin or self.pin)
        return cm.exception.code

    def test_a_good_record_is_accepted_and_returned_with_its_file_and_its_sha256(self):
        rec = self.build_record(self.cloud)
        got = sr.read_build_record(self.cloud, self.pin)
        self.assertEqual(got, dict(rec, record_file=self.path(), record_sha256=sha(self.path())))
        self.write_record(self.cloud, host='another-host')  # the record file is another file now
        again = sr.read_build_record(self.cloud, self.pin)
        self.assertEqual((again['host'], again['record_sha256']), ('another-host', sha(self.path())))
        self.assertNotEqual(again['record_sha256'], got['record_sha256'])

    def test_only_the_fields_it_checks_are_needed(self):
        drop = ('program', 'engine_arg', 'engine', 'rustc', 'cargo', 'machine', 'libc', 'host', 'home', 'cargo_home', 'build_dir', 'target_dir', 'jobs', 'built_at', 'rebuild_command')
        self.write_record(self.cloud, **{k: DROP for k in drop})
        got = sr.read_build_record(self.cloud, self.pin)
        self.assertEqual(sorted(got), ['engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'program_sha256', 'record_file', 'record_sha256', 'schema'])

    def test_rustc_line_is_the_first_line_of_the_toolchain_that_says_anything_or_else_the_words_given(self):
        """rustc_line(rec, missing): the first non-empty line of the record's `rustc -vV`, or `missing`, the words that fit the sentence it goes in (the registered engine text, the plan and
        the page each word a record without a toolchain in their own way, and none of them prints 'None')."""
        text = 'rustc 1.90.0 (fake 2026-01-01)\nbinary: rustc\nhost: x86_64-unknown-linux-gnu'
        for rec, want in ((dict(rustc=text), 'rustc 1.90.0 (fake 2026-01-01)'), (dict(rustc='rustc 1.90.0 (one line)'), 'rustc 1.90.0 (one line)'),
                          (dict(rustc='\n\n \nrustc 1.90.0 (late)\nbinary: rustc'), 'rustc 1.90.0 (late)'), (dict(rustc='rustc 1.90.0 (dos)\r\nbinary: rustc\r\n'), 'rustc 1.90.0 (dos)')):
            for missing in ('toolchain not recorded', 'rustc not recorded', 'an unrecorded toolchain'):
                self.assertEqual(sr.rustc_line(rec, missing), want, (rec, missing))
        for label, rec in (('no entry', {}), ('null', dict(rustc=None)), ('empty', dict(rustc='')), ('only blank lines', dict(rustc='\n  \n\t\n')), ('a number', dict(rustc=5)),
                           ('true', dict(rustc=True)), ('a list', dict(rustc=['rustc 1.90.0'])), ('an object', dict(rustc={'a': 'b'})), ('another entry only', dict(cargo='cargo 1.90.0'))):
            for missing in ('toolchain not recorded', 'rustc not recorded', 'an unrecorded toolchain', 'x'):
                self.assertEqual(sr.rustc_line(rec, missing), missing, (label, missing))

    def test_a_program_without_a_record_is_refused_and_so_is_a_folder_in_its_place(self):
        os.remove(self.path())
        want = f'REFUSED: {self.cloud} has no build record ({self.path()}); {RECORD_HINT}. Nothing was written.'
        self.assertEqual(self.refusal(), want)
        os.makedirs(self.path())
        self.assertEqual(self.refusal(), want)

    def test_a_record_that_cannot_be_read_is_refused(self):
        for label, data in (('half a file', b'{"schema": 1,'), ('an empty file', b''), ('bytes that are not UTF-8', b'\xff\xfe\x00{')):
            write_bytes(self.path(), data)
            msg = self.refusal()
            self.assertTrue(msg.startswith(f'REFUSED: the build record {self.path()} cannot be read ('), (label, msg))
            self.assertTrue(msg.endswith(f'); {RECORD_HINT}. Nothing was written.'), (label, msg))

    def test_a_record_that_is_not_a_schema_1_object_is_refused(self):
        rec = self.build_record(self.cloud)
        for label, text in (('a list', '[1]'), ('null', 'null'), ('a string', '"schema 1"'), ('a number', '1'), ('schema 2', json.dumps(dict(rec, schema=2))),
                            ('no schema', json.dumps({k: v for k, v in rec.items() if k != 'schema'})), ('schema as text', json.dumps(dict(rec, schema='1'))),
                            ('schema true', json.dumps(dict(rec, schema=True))), ('schema 1.0', json.dumps(dict(rec, schema=1.0))), ('schema null', json.dumps(dict(rec, schema=None))),
                            ('schema a list', json.dumps(dict(rec, schema=[1]))), ('schema 0', json.dumps(dict(rec, schema=0))), ('schema -1', json.dumps(dict(rec, schema=-1)))):
            write(self.path(), text)
            self.assertEqual(self.refusal(), f'REFUSED: the build record {self.path()} is not a schema 1 record; {RECORD_HINT}. Nothing was written.', label)
        write(self.path(), json.dumps(dict(rec, schema=1)))
        self.assertEqual(sr.read_build_record(self.cloud, self.pin)['schema'], 1, 'the whole number 1 is the schema')

    def test_an_entry_that_the_page_prints_as_text_must_be_text_when_it_is_there(self):
        """The page, the plan and the registered engine text print these entries as words: a record in which one is a number, a list or an object is damaged, not a build record. Null
        means 'not recorded' and an empty text is text."""
        path = self.path()
        self.assertEqual(sr.BUILD_RECORD_TEXT_KEYS, ('program_sha256', 'engine_arg', 'engine', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'rustc', 'cargo', 'machine', 'host',
                                                    'built_at', 'rebuild_command'))
        for key in sr.BUILD_RECORD_TEXT_KEYS:
            for value in (5, 1.5, True, False, [], ['x'], {}, {'a': 'b'}):
                with self.subTest(key=key, value=value):
                    self.write_record(self.cloud, **{key: value})
                    self.assertEqual(self.refusal(), f'REFUSED: the build record {path} has an entry {key} that is not text; {RECORD_HINT}. Nothing was written.')
        for key in ('engine_arg', 'engine', 'engine_ref', 'rustc', 'cargo', 'machine', 'host', 'built_at', 'rebuild_command'):
            for value in (None, '') if key == 'engine_ref' else (None, '', 'text'):  # (an engine ref that is text has to be the pin's)
                with self.subTest(key=key, value=value):
                    self.write_record(self.cloud, **{key: value})
                    self.assertEqual(sr.read_build_record(self.cloud, self.pin)[key], value, 'null, an empty text and a text are all accepted')

    def test_the_text_of_the_entries_is_judged_after_the_schema_and_before_the_file_it_is_for(self):
        rec = self.build_record(self.cloud, rustc=['x'], program_sha256='0' * 64)
        write(self.path(), json.dumps(dict(rec, schema=2)))
        self.assertIn('is not a schema 1 record', self.refusal())
        write(self.path(), json.dumps(rec))
        self.assertIn('has an entry rustc that is not text', self.refusal(), 'a damaged record is refused as damaged, whatever file it says it is for')
        write(self.path(), json.dumps(dict(rec, rustc='rustc 1.90.0')))
        self.assertIn('is for a program with sha256 000000000000', self.refusal())

    def test_a_record_for_another_file_is_refused_and_names_both_hashes(self):
        other = os.path.join(self.tmp, 'other', 'strength')
        write(other, FAKE_PROGRAM + '\n# another program\n', mode=0o755)
        write(self.path(), json.dumps(self.build_record(other)))  # the record of another program, copied beside this one
        want = (f'REFUSED: the build record {self.path()} is for a program with sha256 {sha(other)[:12]}, but {self.cloud} has sha256 {sha(self.cloud)[:12]}: the record belongs to the '
                'file it was written for. Nothing was written.')
        self.assertEqual(self.refusal(), want)
        self.write_record(self.cloud)
        built12 = sha(self.cloud)[:12]
        write(self.cloud, FAKE_PROGRAM + '\n# edited after it was built\n', mode=0o755)  # or the program was changed after its record was written
        self.assertEqual(self.refusal(), f'REFUSED: the build record {self.path()} is for a program with sha256 {built12}, but {self.cloud} has sha256 {sha(self.cloud)[:12]}: '
                                         'the record belongs to the file it was written for. Nothing was written.')
        write(self.path(), json.dumps({k: v for k, v in self.build_record(self.cloud).items() if k != 'program_sha256'}))
        self.assertIn('is for a program with sha256 None, but', self.refusal(), 'a record that does not say which file it is for is not for this one')

    def test_a_record_with_another_engine_tree_harness_source_or_commit_is_refused_naming_both(self):
        p = self.cloud
        tree12, harness12, ref12 = self.pin['engine_tree'][:12], self.pin['harness_source_sha256'][:12], self.pin['engine_ref'][:12]
        cases = (('another engine tree', dict(engine_tree_archived='1' * 40), f'REFUSED: the build record says the engine tree that went into {p} is 111111111111, not the pinned {tree12}, '
                                                                                'so it is not a build of the pinned source. Nothing was written.'),
                 ('no engine tree', dict(engine_tree_archived=DROP), f'REFUSED: the build record says the engine tree that went into {p} is None, not the pinned {tree12}, '
                                                                     'so it is not a build of the pinned source. Nothing was written.'),
                 ('another harness source', dict(harness_source_sha256='2' * 64), f'REFUSED: the build record says the harness source that went into {p} is 222222222222, not the pinned {harness12}, '
                                                                                  'so it is not a build of the pinned source. Nothing was written.'),
                 ('no harness source', dict(harness_source_sha256=DROP), f'REFUSED: the build record says the harness source that went into {p} is None, not the pinned {harness12}, '
                                                                         'so it is not a build of the pinned source. Nothing was written.'),
                 ('another engine commit', dict(engine_ref='3' * 40), f'REFUSED: the build record says the engine ref was 333333333333, not the pinned {ref12}. Nothing was written.'))
        for label, over, want in cases:
            with self.subTest(label):
                self.write_record(self.cloud, **over)
                self.assertEqual(self.refusal(), want)

    def test_the_checks_are_made_in_this_order_file_schema_program_tree_harness_commit(self):
        faults = dict(program_sha256='0' * 64, engine_tree_archived='1' * 40, harness_source_sha256='2' * 64, engine_ref='3' * 40)
        rec = self.build_record(self.cloud, **faults)
        write(self.path(), json.dumps(dict(rec, schema=2)))
        self.assertIn('is not a schema 1 record', self.refusal())
        write(self.path(), json.dumps(rec))
        self.assertIn('is for a program with sha256 000000000000', self.refusal())
        rec['program_sha256'] = sha(self.cloud)
        write(self.path(), json.dumps(rec))
        self.assertIn('the engine tree that went into', self.refusal())
        rec['engine_tree_archived'] = self.pin['engine_tree']
        write(self.path(), json.dumps(rec))
        self.assertIn('the harness source that went into', self.refusal())
        rec['harness_source_sha256'] = self.pin['harness_source_sha256']
        write(self.path(), json.dumps(rec))
        self.assertIn('the engine ref was 333333333333', self.refusal())
        rec['engine_ref'] = self.pin['engine_ref']
        write(self.path(), json.dumps(rec))
        self.assertEqual(sr.read_build_record(self.cloud, self.pin)['engine_ref'], self.pin['engine_ref'])

    def test_the_engine_commit_is_compared_only_when_the_record_and_the_pin_both_name_one(self):
        for label, over in (('a build of a folder (null)', dict(engine_ref=None)), ('no engine_ref in the record', dict(engine_ref=DROP)), ('an empty one', dict(engine_ref=''))):
            self.write_record(self.cloud, **over)
            self.assertEqual(sr.read_build_record(self.cloud, self.pin)['program_sha256'], sha(self.cloud), label)
        self.write_record(self.cloud, engine_ref='3' * 40)
        for label, pin in (('a pin with none', {k: v for k, v in self.pin.items() if k != 'engine_ref'}), ('a null one', dict(self.pin, engine_ref=None)), ('an empty one', dict(self.pin, engine_ref=''))):
            self.assertEqual(sr.read_build_record(self.cloud, pin)['engine_ref'], '3' * 40, label)

    def test_a_pin_without_an_engine_tree_or_a_harness_hash_cannot_check_a_rebuild(self):
        for key in ('engine_tree', 'harness_source_sha256'):
            for label, pin in (('missing', {k: v for k, v in self.pin.items() if k != key}), ('null', dict(self.pin, **{key: None})), ('empty', dict(self.pin, **{key: ''}))):
                self.assertEqual(self.refusal(pin=pin), f'REFUSED: the pin has no {key}, so a rebuild cannot be checked against it. Nothing was written.', (key, label))
        bare = {k: v for k, v in self.pin.items() if k not in ('engine_tree', 'harness_source_sha256')}
        self.assertIn('the pin has no engine_tree', self.refusal(pin=bare), 'the engine tree is asked for first')
        self.write_record(self.cloud, engine_tree_archived='1' * 40)
        self.assertIn('the build record says the engine tree that went into', self.refusal(pin={k: v for k, v in self.pin.items() if k != 'harness_source_sha256'}),
                      'the engine tree is judged before the harness source is asked for')

    def test_the_command_line_refuses_a_rebuild_with_a_bad_record_before_any_replay_and_writes_nothing(self):
        cases = (('no record', lambda: os.remove(self.path()), lambda: f'REFUSED: {self.cloud} has no build record ({self.path()});'),
                 ('another engine tree', lambda: self.write_record(self.cloud, engine_tree_archived='1' * 40), lambda: f'REFUSED: the build record says the engine tree that went into {self.cloud}'),
                 ('another harness source', lambda: self.write_record(self.cloud, harness_source_sha256='2' * 64), lambda: f'REFUSED: the build record says the harness source that went into {self.cloud}'),
                 ('the record of another file', lambda: self.write_record(self.cloud, program_sha256='4' * 64), lambda: f'REFUSED: the build record {self.path()} is for a program with sha256 444444444444'))
        for label, prepare, want in cases:
            with self.subTest(label):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                prepare()
                for extra in ((), ('--dry-run',), ('--register-only',)):
                    code, out, err = self.cli('--deals', '1', '--program', self.cloud, *extra)
                    self.assertTrue(str(code).startswith('[kx3 (d513e37b) v km3] ' + want()), (label, extra, code))
                    self.assertTrue(str(code).endswith('Nothing was written.'), code)
                    self.assertEqual(out, '', 'refused before the first line of the plan')
                    self.assertFalse(os.path.exists(self.out_root), 'nothing was written')
                self.assertEqual(self.replayed, [], 'refused before the hours-long replay')
                self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.cloud), 'selfcheck_env.json')))


class ProgramChangedOnResume(RebuiltFixture):
    """A run registered on the rebuilt route whose program is another file when it is resumed (a container restart: the rebuild is a new file): the resume goes on only when the pin is
    the committed one, the new program's build record is for it and has the pinned engine tree and harness source, and both self-checks are replayed again on it and equal the
    committed pin; then a 'program_changed' event is logged, the page shows it, and the run goes on with the new sha256 accepted (a third one is refused by the check before each
    sitting). A run registered on the pinned route, or with another problem too, is refused as before."""
    NEW = FAKE_PROGRAM + '\n# built again after the restart, other bytes\n'

    def setUp(self):
        super().setUp()
        self.spawn = self.spawned()

    def started(self, max_games='10', *extra, **kw):
        """Register on the rebuilt route (the fixture's rebuilt copy) and play `max_games` games; the folder, with the program still the registered one."""
        code, out, err = self.cli('--deals', '1', '--max-games', max_games, '--program', self.cloud, *extra, spawn=self.spawn, **kw)
        self.assertEqual(code, 0, out + err)
        return self.rundir()

    def rebuild_again(self, text=None, **over):
        """The rebuild after the restart: other bytes at the same path, with its own build record. Returns the record."""
        return self.put_program(self.cloud, text or self.NEW, **over)

    def events(self, d, name=None):
        ev = jsonl(os.path.join(d, 'slow_report_log.jsonl'))
        return [e for e in ev if e['event'] == name] if name else ev

    def snapshot(self, d):
        return dict(calls=len(jsonl(os.path.join(d, 'fake_calls.jsonl'))), games=len(jsonl(os.path.join(d, 'games.jsonl'))), events=[e['event'] for e in self.events(d)],
                    lock=os.path.exists(os.path.join(d, 'slow_report.lock')))

    def refused_resume(self, d, *extra, **kw):
        """Resume `d` and check that it is refused before a thing happens: no program started, no game, no event, no lock left. Returns the refusal."""
        before, replayed = self.snapshot(d), list(self.replayed)
        code, out, err = self.cli('--dir', d, *extra, deck=False, spawn=self.spawn, **kw)
        self.assertIsInstance(code, str, out + err)
        self.assertTrue(code.startswith(f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: '), code)
        self.assertEqual(self.snapshot(d), before, 'nothing was played, logged or left locked')
        self.last_replays = self.replayed[len(replayed):]
        return code

    def pin_down_times(self, d, before):
        """The fake program stamps a game with the second it was played in and the event is stamped when it is logged: set them (the first `before` games 10:00:01, the rest 10:00:30,
        the change 10:00:10) so that the page's count of games before and after it is certain."""
        games = jsonl(os.path.join(d, 'games.jsonl'))
        for i, g in enumerate(games):
            g['started_at'] = '2026-10-10T10:00:01Z' if i < before else '2026-10-10T10:00:30Z'
        write(os.path.join(d, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games))
        log = self.events(d)
        for e in log:
            if e['event'] == 'program_changed':
                e['at'] = '2026-10-10T10:00:10Z'
        write(os.path.join(d, 'slow_report_log.jsonl'), ''.join(json.dumps(e) + '\n' for e in log))

    # ------------------------------------------------------------------------------------------------ accepted
    def test_a_rebuilt_copy_with_the_pinned_record_and_both_self_checks_equal_to_the_pin_is_accepted_and_logged(self):
        d = self.started()
        registered = sha(self.cloud)
        manifest_before = (read(os.path.join(d, 'manifest.json')), read(os.path.join(d, 'manifest.sha256')))
        rec = self.rebuild_again()
        new = sha(self.cloud)
        self.assertNotEqual(new, registered)
        self.replayed.clear()
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'both self-checks again, on the new file, km3 first')
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        said = [f'the program at {self.cloud} has sha256 {new[:12]}, not the {registered[:12]} this run was registered with; its build record has the pinned engine tree and harness source, '
                f'so both self-checks are replayed again against {FILE_DIGESTS} before the run goes on (hours for kx3)',
                f'self-check of km3: 12 fixed games on {self.cloud} (this takes a while for kx3; run it when the machine is free)',
                f'self-check of kx3: 12 fixed games on {self.cloud} (this takes a while for kx3; run it when the machine is free)',
                f'program changed mid-run, accepted: both self-checks equal {FILE_DIGESTS}; logged as program_changed in slow_report_log.jsonl and shown on the page']
        at = [lines.index(s) for s in said]
        self.assertEqual(at, sorted(at), 'said in this order')
        self.assertLess(at[3], lines.index('running: 22 games to go, 2 at a time'), 'and then the run goes on')
        changed = self.events(d, 'program_changed')
        self.assertEqual(len(changed), 1)
        self.assertRegex(changed[0]['at'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        self.assertEqual({k: v for k, v in changed[0].items() if k != 'at'},
                         {'event': 'program_changed', 'pilot': 'kx3', 'reference': 'km3', 'old_sha256': registered, 'new_sha256': new,
                          'manifest_sha256': hashlib.sha256(manifest_before[0].encode('utf-8')).hexdigest(),
                          'build_record': dict(rec, record_file=self.cloud + '.build.json', record_sha256=sha(self.cloud + '.build.json')),
                          'selfcheck': {s: self.TEXT % s for s in ('km3', 'kx3')}, 'pin_committed': 'bypassed', 'replayed_on': socket.gethostname()})
        self.assertEqual([e['event'] for e in self.events(d) if e['event'] != 'env_scrubbed'],
                         ['registered', 'sitting_call', 'slice_start', 'slice_end', 'report_written', 'program_changed', 'sitting_call', 'slice_start', 'slice_end', 'complete', 'report_written'],
                         'the change is logged after the replay and before the sitting that runs the new program')
        self.assertEqual((read(os.path.join(d, 'manifest.json')), read(os.path.join(d, 'manifest.sha256'))), manifest_before, 'the registration is not touched')
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(self.cloud), 'selfcheck_env.json')))
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_the_page_shows_the_change_with_the_games_started_before_and_after_it(self):
        d = self.started()
        registered = sha(self.cloud)
        self.rebuild_again()
        new = sha(self.cloud)
        record12 = sha(self.cloud + '.build.json')[:12]
        self.assertEqual(self.cli('--dir', d, deck=False, spawn=self.spawn)[0], 0)
        for before in (10, 0, 1, 32):
            with self.subTest(before=before):
                self.pin_down_times(d, before)
                code, out, err = self.cli('--dir', d, '--report-only', deck=False)
                self.assertEqual(code, 0, out + err)
                lines = read(os.path.join(d, 'SLOW_REPORT.md')).splitlines()
                games = f"{before} game{'' if before == 1 else 's'}"
                want = (f'- **The program changed mid-run** (2026-10-10T10:00:10Z): sha256 `{registered[:12]}` -> `{new[:12]}` after a restart or rebuild; its build record has the pinned engine '
                        f'tree and harness source (record `{record12}`) and both self-checks were replayed again on {socket.gethostname()} and equal {FILE_DIGESTS}. '
                        f'{games} of the 32 played so far were started before this change and {32 - before} after; the numbers above pool them.')
                self.assertEqual(lines.count(want), 1)
                first_self_check = next(i for i, l in enumerate(lines) if l.startswith('- Self-check of'))
                self.assertEqual(lines.index(want), first_self_check - 1, 'right before the self-checks, after the pin line')
                self.assertTrue(lines[lines.index(want) - 1].startswith('- Pin '))

    def test_the_accepted_program_is_accepted_by_every_later_call_without_another_replay(self):
        d = self.started()
        reg = sha(self.cloud)
        self.rebuild_again()
        new = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '10', deck=False, spawn=self.spawn)[0], 0)
        replays = list(self.replayed)
        self.assertEqual(len(replays), 4, 'two at the registration, two for the change')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn(f'(resume with: python3 rl/strength/slow_report.py --dir {d} --school-rule off)', out, 'the dry run now sees nothing to replay')
        self.assertNotIn('replay', out)
        for played in (30, 32):
            code, out, err = self.cli('--dir', d, '--max-games', '10', deck=False, spawn=self.spawn)
            self.assertEqual(code, 0, out + err)
            self.assertNotIn('has sha256', out)
            self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), played)
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
        self.assertEqual(self.replayed, replays, 'no later call replays anything')
        self.assertEqual([e['new_sha256'] for e in self.events(d, 'program_changed')], [new], 'and none logs the change again')
        self.assertEqual(sr.accepted_program_shas(d, self.manifest(d)), {reg, new})

    def test_a_second_change_is_replayed_and_logged_again_and_the_first_one_stays_accepted(self):
        d = self.started('6')
        reg = sha(self.cloud)
        self.rebuild_again()
        b = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.rebuild_again(FAKE_PROGRAM + '\n# a third build\n')
        c = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual(len(self.replayed), 6, 'a replay of both self-checks for each of the two changes')
        self.assertEqual([e['new_sha256'] for e in self.events(d, 'program_changed')], [b, c])
        self.assertEqual(sr.accepted_program_shas(d, self.manifest(d)), {reg, b, c})
        self.assertEqual(read(os.path.join(d, 'SLOW_REPORT.md')).count('**The program changed mid-run**'), 2)
        self.rebuild_again()  # back to the second build, which was accepted: no replay
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(self.replayed), 6)
        self.assertEqual(len(self.events(d, 'program_changed')), 2)

    ORIGINAL = FAKE_PROGRAM + '\n# built on the cloud\n'  # the text of the rebuilt copy the fixture registers with (rebuild_at)

    def swapping_during_replay(self, after_spec, action):
        """Run `action` once the self-check of `after_spec` has been replayed (hours into a real replay, the program or its record is replaced)."""
        real = sr.run_selfcheck  # (the spy of the fixture, which notes the replay)

        def swap(pin, repo, spec, say, **kw):
            out = real(pin, repo, spec, say, **kw)
            if spec == after_spec:
                action()
            return out
        patcher = mock.patch.object(sr, 'run_selfcheck', swap)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_program_replaced_while_the_self_checks_ran_is_refused_and_the_change_is_not_logged(self):
        """The sha256 and the record are read before the replay (hours for kx3) and read again after it: what the self-checks checked must be what is there now."""
        d = self.started()
        self.rebuild_again()
        first = sha(self.cloud)
        self.swapping_during_replay('kx3', lambda: self.rebuild_again(FAKE_PROGRAM + '\n# swapped in during the replay\n'))
        code = self.refused_resume(d)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the program at {self.cloud} changed while the self-checks were replayed '
                               f'(sha256 {first[:12]} -> {sha(self.cloud)[:12]}): what they checked is not what is there now. Nothing was played.')
        self.assertEqual(self.events(d, 'program_changed'), [])
        self.assertEqual(sr.accepted_program_shas(d, self.manifest(d)), {self.manifest(d)['program_sha256']})

    def test_a_build_record_rewritten_while_the_self_checks_ran_is_refused_too(self):
        d = self.started()
        rec = self.rebuild_again()
        self.swapping_during_replay('km3', lambda: write(self.cloud + '.build.json', json.dumps(dict(rec, built_at='2031-01-01T00:00:00Z'), indent=1) + '\n'))
        code = self.refused_resume(d)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the build record {self.cloud}.build.json changed while the self-checks were replayed: '
                               'what was checked is not what is there now. Nothing was played.')
        self.assertEqual(self.events(d, 'program_changed'), [])

    def test_a_program_that_stays_put_during_the_replay_is_accepted_as_before(self):
        d = self.started()
        self.rebuild_again()
        self.swapping_during_replay('kx3', lambda: write(self.cloud + '.unrelated', 'a file beside the program that is none of its business'))
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(self.events(d, 'program_changed')), 1)

    def test_a_line_copied_from_the_log_of_another_run_is_not_this_runs_change(self):
        """The change is logged with the sha256 of the manifest.json of the run it is for: the same line in the log of another run (a copied folder, a pasted log) is not a change of
        that run, even when its program, record and self-check texts are what that run could have."""
        a = self.started('6')
        self.rebuild_again()
        self.assertEqual(self.cli('--dir', a, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        line = self.events(a, 'program_changed')[0]
        self.assertEqual(line['manifest_sha256'], sha(os.path.join(a, 'manifest.json')))
        self.put_program(self.cloud, self.ORIGINAL)  # the run B is registered with the original rebuild, like A was
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.cloud, '--date', '2026-10-11', date=False)
        self.assertEqual(code, 0, out + err)
        b = self.rundir('2026-10-11_my-list')
        man_b = self.manifest(b)
        self.assertNotEqual(sha(os.path.join(b, 'manifest.json')), line['manifest_sha256'])
        self.append_log(b, line)
        self.assertEqual(sr.accepted_program_shas(b, man_b), {man_b['program_sha256']}, "A's line names A's run")
        self.assertEqual(sr.accepted_program_shas(a, self.manifest(a)), {self.manifest(a)['program_sha256'], line['new_sha256']}, 'and it is still A\'s')
        self.rebuild_again()  # B's program is now the program A changed to: B has not replayed anything for it
        code, out, err = self.cli('--dir', b, '--dry-run', deck=False)
        self.assertIn('so a resume would replay both self-checks again', out, "B still has to replay: A's line did not accept the program for B")

    def test_the_page_shows_a_return_to_an_earlier_accepted_build_once(self):
        """A sitting that runs a build accepted earlier (the registered one, or an earlier change) needs no replay and logs no change; the page says the program went back, at which
        sitting, with the games before and after."""
        d = self.started('6')
        reg = sha(self.cloud)
        self.rebuild_again()
        b = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        replays = len(self.replayed)
        self.put_program(self.cloud, self.ORIGINAL)
        self.assertEqual(sha(self.cloud), reg, 'the registered build again')
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual(len(self.replayed), replays, 'an accepted build needs no replay')
        self.assertEqual(len(self.events(d, 'program_changed')), 1)
        self.assertEqual([e.get('program_sha256') for e in self.events(d, 'sitting_call')], [reg, b, reg], 'each sitting says which program it ran')
        back = re.compile(r'^- \*\*The program went back to an earlier accepted build\*\* \((\S+)\): sha256 `([0-9a-f]{12})` -> `([0-9a-f]{12})` '
                          r'\(the registered program or one accepted before, so no new replay was needed\); (\d+) games? of the (\d+) played so far were started before this and (\d+) after\.$')
        lines = read(os.path.join(d, 'SLOW_REPORT.md')).splitlines()
        found = [back.match(l) for l in lines if 'went back to an earlier accepted build' in l]
        self.assertEqual(len(found), 1, lines)
        at, was, now, before, played, after = found[0].groups()
        self.assertEqual((was, now), (b[:12], reg[:12]))
        self.assertEqual((int(before) + int(after), int(played)), (int(played), 18), 'the games of the three sittings')
        change = next(i for i, l in enumerate(lines) if 'The program changed mid-run' in l)
        self.assertLess(change, next(i for i, l in enumerate(lines) if 'went back to an earlier accepted build' in l), 'in the order it happened')
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)  # one more sitting on the same build: nothing new to say
        self.assertEqual(read(os.path.join(d, 'SLOW_REPORT.md')).count('went back to an earlier accepted build'), 1)
        self.assertEqual(read(os.path.join(d, 'SLOW_REPORT.md')).count('**The program changed mid-run**'), 1)

    def test_a_run_that_never_changed_its_program_says_nothing_about_one(self):
        d = self.started('6')
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertNotIn('went back to an earlier accepted build', page)
        self.assertNotIn('changed mid-run', page)

    def rewrite_log(self, d, edit):
        """The log of `d` with its events passed through edit(list of dicts) -> list of dicts."""
        events = self.events(d)
        write(os.path.join(d, 'slow_report_log.jsonl'), ''.join(json.dumps(e) + '\n' for e in edit(events)))

    def test_a_line_of_an_earlier_version_that_does_not_name_its_run_counts_when_the_log_was_started_for_this_run(self):
        """c28dfb8a wrote 'program_changed' lines without manifest_sha256. They are still this run's own when the first line of the log, 'registered', names this run's manifest (a log
        pasted from another run names another one), so the committed runs of that version keep their change on a regenerated page and a resume does not replay it again."""
        d = self.started('6')
        man = self.manifest(d)
        reg = man['program_sha256']
        legacy = self.change_event(man, 'b' * 64, manifest_sha256=DROP)
        self.assertNotIn('manifest_sha256', legacy)
        self.append_log(d, legacy)
        self.assertEqual(self.events(d)[0]['manifest_sha256'], sha(os.path.join(d, 'manifest.json')), 'the registered line names the run')
        self.assertEqual(sr.accepted_program_shas(d, man), {reg, 'b' * 64})
        self.assertEqual(sr.program_in_use_before(d, man), 'b' * 64)
        page = sr.write_slow_report(d)
        self.assertEqual(page.count('**The program changed mid-run**'), 1)
        self.assertIn(f'sha256 `{reg[:12]}` -> `{"b" * 12}`', page)
        original = self.events(d)
        for how, edit in (('the registered line names another run', lambda ev: [dict(e, manifest_sha256='9' * 64) if e['event'] == 'registered' else e for e in ev]),
                          ('the registered line names no run', lambda ev: [{k: v for k, v in e.items() if k != 'manifest_sha256'} if e['event'] == 'registered' else e for e in ev]),
                          ('there is no registered line', lambda ev: [e for e in ev if e['event'] != 'registered'])):
            with self.subTest(how):
                self.rewrite_log(d, edit)
                self.assertEqual(sr.accepted_program_shas(d, man), {reg}, 'a line that cannot be tied to this run is left out')
                self.assertNotIn('The program changed mid-run', sr.write_slow_report(d))
                self.rewrite_log(d, lambda ev: original)
        self.rewrite_log(d, lambda ev: [e for e in original if e['event'] != 'program_changed'] + [self.change_event(man, 'c' * 64, manifest_sha256='9' * 64)])
        self.assertEqual(sr.accepted_program_shas(d, man), {reg}, 'a line that names ANOTHER run is not this run\'s, whatever the log says')
        self.rewrite_log(d, lambda ev: [e for e in original if e['event'] != 'program_changed'] + [self.change_event(man, 'c' * 64, manifest_sha256=None)])
        self.assertEqual(sr.accepted_program_shas(d, man), {reg}, 'and a line that names no run because the name is null is not an old line either')

    def test_a_resume_after_a_change_logged_by_the_earlier_version_does_not_replay_it_again(self):
        d = self.started('6')
        man = self.manifest(d)
        self.rebuild_again()
        new = sha(self.cloud)
        # the change as the earlier version logged it: no manifest_sha256
        self.append_log(d, self.change_event(man, new, manifest_sha256=DROP))
        replays = len(self.replayed)
        code, out, err = self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(self.replayed), replays, 'the accepted program needs no new replay')
        self.assertEqual(len(self.events(d, 'program_changed')), 1, 'and no change is logged twice')

    def change_event(self, man, new_sha, **over):
        """A 'program_changed' event as reverify_program writes it for the run `man`: the program it names, its build record (for that file, with the registered engine tree and
        harness hash), the self-check texts the run was registered with. `over` replaces entries (a value of DROP removes one)."""
        return change_event_for(man, new_sha, **over)

    def forgeries(self, man, new):
        return forged_overrides(man, new)

    def append_log(self, d, *events, torn=None):
        """Add lines to the run's log, as a person (or a program with a bug) could: the events as JSON lines, then, if given, a last line torn by a kill."""
        with open(os.path.join(d, 'slow_report_log.jsonl'), 'a', encoding='utf-8') as f:
            for e in events:
                f.write(json.dumps(e) + '\n')
            if torn:
                f.write(torn)

    def test_accepted_program_shas_are_the_registered_one_and_each_logged_change(self):
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        self.assertEqual(sr.accepted_program_shas(d, man), {reg})
        self.append_log(d, self.change_event(man, 'a' * 64), self.change_event(man, 'b' * 64, at='2026-10-10T10:00:20Z'), {'event': 'program_changed'},
                        self.change_event(man, 5), dict(self.change_event(man, 'c' * 64), event='slice_end'), torn='{"event": "program_changed", "new_sha2')
        self.assertEqual(sr.accepted_program_shas(d, man), {reg, 'a' * 64, 'b' * 64}, 'only a program_changed event that names a program, with its record and self-checks, counts')
        os.remove(os.path.join(d, 'slow_report_log.jsonl'))
        self.assertEqual(sr.accepted_program_shas(d, man), {reg}, 'no log: the registered one')

    def test_verify_inputs_takes_the_set_of_program_hashes_the_run_may_continue_with(self):
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        self.assertEqual(sr.verify_inputs(man), [])
        self.assertEqual(sr.verify_inputs(man, {reg}), [])
        self.rebuild_again()
        new = sha(self.cloud)
        for accepted in (None, set(), {reg}):
            problems = sr.verify_inputs(man, accepted)
            self.assertEqual(problems, [f'{self.cloud} has sha256 {new[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS], accepted)
        self.assertEqual(sr.verify_inputs(man, {reg, new}), [], 'the new one is accepted once it is in the set')

    # ------------------------------------------------------------------------------------------------ refused
    def test_a_resume_without_a_build_record_is_refused_and_replays_nothing(self):
        d = self.started()
        self.rebuild_again()
        os.remove(self.cloud + '.build.json')
        msg = self.refused_resume(d)
        self.assertTrue(msg.endswith(f'REFUSED: {self.cloud} has no build record ({self.cloud}.build.json); {RECORD_HINT}. Nothing was written.'), msg)
        self.assertEqual(self.last_replays, [])

    def test_a_resume_with_a_record_that_is_not_the_pinned_source_or_not_for_the_file_is_refused_and_replays_nothing(self):
        for label, over, want in (('another engine tree', dict(engine_tree_archived='1' * 40), 'the build record says the engine tree that went into'),
                                  ('another harness source', dict(harness_source_sha256='2' * 64), 'the build record says the harness source that went into'),
                                  ('another engine commit', dict(engine_ref='3' * 40), 'the build record says the engine ref was 333333333333'),
                                  ('the record of the program it replaces', dict(program_sha256='5' * 64), 'is for a program with sha256 555555555555')):
            with self.subTest(label):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.spawn = self.spawned()
                d = self.started()
                self.rebuild_again(**over)
                msg = self.refused_resume(d)
                self.assertIn(want, msg)
                self.assertTrue(msg.endswith('Nothing was written.'), msg)
                self.assertEqual(self.last_replays, [])

    def test_the_old_record_beside_a_rebuilt_program_is_not_the_record_of_the_new_file(self):
        d = self.started()
        old_record = read(self.cloud + '.build.json')
        registered = sha(self.cloud)
        write(self.cloud, self.NEW, mode=0o755)  # rebuilt, but the record beside it is still the old program's
        self.assertEqual(read(self.cloud + '.build.json'), old_record)
        msg = self.refused_resume(d)
        self.assertTrue(msg.endswith(f'is for a program with sha256 {registered[:12]}, but {self.cloud} has sha256 {sha(self.cloud)[:12]}: the record belongs to the file it was written for. '
                                     'Nothing was written.'), msg)
        self.assertEqual(self.last_replays, [])

    def test_a_replay_that_differs_from_the_pin_for_either_pilot_is_refused_and_logs_nothing(self):
        for pilot, tried in (('km3', ['km3']), ('kx3', ['km3', 'kx3'])):
            with self.subTest(differs_for=pilot):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.spawn = self.spawned()
                d = self.started()
                self.rebuild_at(self.cloud, differs_for=pilot)
                msg = self.refused_resume(d)
                self.assertTrue(msg.endswith(f'REFUSED: the self-check of {pilot} does not match the pin.\n  pinned: {self.TEXT % pilot}\n  got:    selfcheck pilot={pilot} games=12 '
                                             'digest=changedchanged00\nThe program is not behaving as the pinned build did; nothing was written.'), msg)
                self.assertEqual([s for s, p in self.last_replays], tried, 'km3 first, and it stops at the first difference')
                self.assertEqual(self.events(d, 'program_changed'), [])

    def test_a_refused_resume_can_be_tried_again_after_a_good_rebuild(self):
        d = self.started()
        self.rebuild_at(self.cloud, differs_for='kx3')
        self.refused_resume(d)
        self.rebuild_again()
        new = sha(self.cloud)
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual([e['new_sha256'] for e in self.events(d, 'program_changed')], [new], 'the refused one left nothing behind')

    def test_a_run_registered_on_the_pinned_route_is_refused_as_before_even_with_a_record_beside_the_new_program(self):
        code, out, err = self.cli('--deals', '1', '--max-games', '10', spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        registered = sha(self.program)
        write(self.program, FAKE_PROGRAM + '\n# a rebuild at the pinned path\n', mode=0o755)
        self.write_record(self.program)
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n'
                              f'  {self.program} has sha256 {sha(self.program)[:12]}, but this run was registered with the program at that path with sha256 {registered[:12]}. ' + RESUME_NEEDS_PINNED)
        self.assertEqual((self.last_replays, self.replayed), ([], []), 'no self-check is replayed for a pinned run')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0)
        self.assertIn('(it would be refused: ' + f'{self.program} has sha256 {sha(self.program)[:12]}, {sr.PROGRAM_PROBLEM} {registered[:12]}. ' + RESUME_NEEDS_PINNED + ')', out)
        self.assertNotIn('a resume would replay', out, 'a pinned run is never offered the replay')

    def test_a_changed_program_with_another_problem_too_is_refused_with_both_and_replays_nothing(self):
        for label, change, line in (('the deck file', lambda: write(self.deck, DECK_TEXT.replace('Torchic', 'Treecko')), 'my-list ('),
                                    ('a panel list', lambda: write(os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-weezing.txt'),
                                                                   read(os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-weezing.txt')) + '# edited\n'), 't-weezing (')):
            with self.subTest(label):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.spawn = self.spawned()
                d = self.started()
                self.rebuild_again()
                change()
                msg = self.refused_resume(d)
                problems = msg.split('so nothing is run:\n', 1)[1].split('\n  ')
                self.assertEqual(len(problems), 2, problems)
                self.assertIn(sr.PROGRAM_PROBLEM, problems[0])
                self.assertIn(line, problems[1])
                self.assertIn('has changed since registration', problems[1])
                self.assertEqual(self.last_replays, [])
                code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
                self.assertIn('(it would be refused: ' + problems[0].strip() + '; ', out)
                self.assertNotIn('a resume would replay', out, 'with another problem the replay is not on offer')

    def test_a_changed_program_whose_file_is_gone_is_refused_and_not_replayed(self):
        d = self.started()
        os.remove(self.cloud)
        msg = self.refused_resume(d)
        self.assertIn(f'{self.cloud} is missing, {sr.PROGRAM_PROBLEM}', msg)
        self.assertEqual(self.last_replays, [])

    def test_when_the_pin_is_not_the_committed_one_the_resume_is_refused_before_the_replay(self):
        d = self.started()
        registered = sha(self.cloud)
        self.rebuild_again()
        os.environ.pop(ALLOW_PIN_VAR, None)
        msg = self.refused_resume(d)
        self.assertTrue(msg.endswith('REFUSED: the pin is not the committed one: ' + f'HEAD has no {PIN_REL} in {self.repo} (not a git repository, no commit, or the file is not committed){git_said(self.repo)}. '
                                     f'A slow report trusts the pin for what the program is, so it uses only {PIN_REL} as committed at HEAD (commit the pin, in the repository you run from; '
                                     'a hand-edited or copied pin is refused). Nothing was written.'), msg)
        self.assertEqual(self.last_replays, [])
        # the same run, once the pin is committed in the repository it is resumed from: accepted, and the event says the pin was the committed one
        self.commit_pin()
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual([e['pin_committed'] for e in self.events(d, 'program_changed')], ['yes'])
        said = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertIn(f"the program at {self.cloud} has sha256 {sha(self.cloud)[:12]}, not the {registered[:12]} this run was registered with; its build record has the pinned engine "
                      f'tree and harness source, so both self-checks are replayed again against {COMMITTED_DIGESTS} before the run goes on (hours for kx3)', said)
        self.assertIn(f'program changed mid-run, accepted: both self-checks equal {COMMITTED_DIGESTS}; logged as program_changed in slow_report_log.jsonl and shown on the page', said)
        self.assertNotIn('NOT the committed pin', out, 'a committed pin is not described as a test pin')
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertIn(f'and both self-checks were replayed again on {socket.gethostname()} and equal {COMMITTED_DIGESTS}. ', page, 'the page follows the pin the change was accepted under (the event), not the registered one')
        self.assertNotIn(FILE_DIGESTS, page.split('The program changed mid-run')[1].split('\n')[0])

    def test_an_unrelated_change_of_the_pin_file_does_not_stop_a_changed_program_from_being_accepted(self):
        """The pin file changes for reasons that say nothing about the program (a new entry in seed_reserved after every smoke run): the engine tree, harness source and self-check
        texts the run was registered with are still the pin's, so the replay goes through, with the note that the pin file changed."""
        d = self.started()
        self.edit_pin(seed_reserved=self.pin['seed_reserved'] + [{'base': 24_601_000_000 + 99 * STEP, 'note': 'slot 99: a later smoke run'}])
        self.rebuild_again()
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertIn('note: the pin file has changed since this run was registered', out)
        self.assertEqual(len(self.events(d, 'program_changed')), 1)

    def test_a_later_pin_does_not_judge_the_changed_program_of_a_run_registered_under_an_earlier_one(self):
        """A changed program is judged by the pin the run was REGISTERED under (the manifest's engine tree, harness hash, engine ref and self-check texts), not by whatever pin file is
        there now: a run registered under one pin must not go on with a build of whatever a later pin names and pool its games with the first build's."""
        d = self.started()
        registered_tree = self.manifest(d)['slow_report']['engine_tree']
        self.edit_pin(engine_tree='77' * 20)  # a later pin: another engine tree ...
        self.rebuild_again()  # ... and a rebuild of that other source, with its own good record
        self.assertNotEqual(json.loads(read(self.cloud + '.build.json'))['engine_tree_archived'], registered_tree)
        msg = self.refused_resume(d)
        self.assertIn(f'REFUSED: the pin in use is not the pin this run was registered under (engine_tree: registered {registered_tree[:12]}, pin now {"77" * 6})', msg)
        self.assertEqual(self.last_replays, [])
        self.assertEqual(self.events(d, 'program_changed'), [])

    # ------------------------------------------------------------------------------------------------ the pin the run was registered under
    PIN_CHANGES = ('the engine tree', 'the harness source', 'the engine ref', 'the km3 self-check text', 'the kx3 self-check text')

    def pin_change(self, d, label):
        """(an edit of the pin file, the words registered_vs_pin names it with) for one difference between the pin the run `d` was registered under and the pin in use."""
        man, pin = self.manifest(d), self.pin
        block, other = man['slow_report'], 'selfcheck pilot=%s games=12 digest=otherotherother0'
        return {'the engine tree': (dict(engine_tree='77' * 20), f"engine_tree: registered {block['engine_tree'][:12]}, pin now {'77' * 6}"),
                'the harness source': (dict(harness_source_sha256='88' * 32), f"harness_source_sha256: registered {block['harness_source_sha256'][:12]}, pin now {'88' * 6}"),
                'the engine ref': (dict(engine_ref='99' * 20), f"engine_ref: registered {block['engine_ref'][:12]}, pin now {'99' * 6}"),
                'the km3 self-check text': (dict(selfcheck=dict(pin['selfcheck'], km3=other % 'km3')),
                                            f"the km3 self-check text differs (registered: {man['selfcheck']['km3']}; pin now: {other % 'km3'})"),
                'the kx3 self-check text': (dict(selfcheck=dict(pin['selfcheck'], kx3=other % 'kx3')),
                                            f"the kx3 self-check text differs (registered: {man['selfcheck']['kx3']}; pin now: {other % 'kx3'})")}[label]

    def not_registered_under(self, *diffs):
        return ('REFUSED: the pin in use is not the pin this run was registered under (' + '; '.join(diffs) + '), so a changed program cannot be judged by it: games of two builds would be '
                'pooled. Make the pin the run was registered with the committed one again (for example revert the commit that changed rl/strength/slow_report_pin.json) and use a program '
                'built for it, or register a new run.')

    def would_be_refused(self, refusal):
        """What the dry run of a folder says in the place of a refusal the real resume would give: 'it would be refused: ' and the message without its own 'REFUSED: ' (never the doubled
        'refused: REFUSED:')."""
        self.assertTrue(refusal.startswith('REFUSED: '), refusal)
        return 'it would be refused: ' + refusal[len('REFUSED: '):]

    def files_of(self, d):
        return {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}

    def test_every_difference_from_the_pin_a_run_was_registered_under_refuses_a_changed_program_and_the_dry_run_says_so(self):
        for label in self.PIN_CHANGES:
            with self.subTest(label):
                self.make()
                self.lay_out_harness()
                self.replayed.clear()
                self.spawn = self.spawned()
                d = self.started()
                original = dict(self.pin)
                change, words = self.pin_change(d, label)
                self.edit_pin(**change)
                self.rebuild_again()  # a rebuild of what the pin in use names, with its own good record: the program is fine, the pin is not the one the run was registered under
                msg = self.refused_resume(d)
                self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] ' + self.not_registered_under(words))
                self.assertEqual(self.last_replays, [], 'refused before the hours-long replay')
                self.assertEqual(self.events(d, 'program_changed'), [])
                before = self.files_of(d)
                code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
                self.assertEqual(code, 0, out + err)
                lines = [l.split('] ', 1)[1] for l in out.splitlines()]
                self.assertEqual(lines[1], self.played_line(self.would_be_refused(self.not_registered_under(words))), 'the dry run says what the resume would')
                self.assertNotIn('REFUSED', out, 'in the dry run it is "it would be refused: ...", with no second "REFUSED:" inside')
                self.assertNotIn('replay', out)
                self.assertEqual(self.files_of(d), before, 'a dry run writes nothing')
                self.assertEqual(len(self.replayed), 2, 'and replays nothing')
                self.edit_pin(**{k: original[k] for k in change})  # the pin put back, with a rebuild of its source: the same run goes on
                self.rebuild_again()
                code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
                self.assertEqual(code, 0, out + err)
                self.assertEqual(len(self.events(d, 'program_changed')), 1)

    def test_all_the_differences_are_named_together_in_the_order_tree_harness_ref_then_the_self_checks(self):
        d = self.started()
        everything = {}
        words = []
        for label in self.PIN_CHANGES[:3]:
            change, said = self.pin_change(d, label)
            everything.update(change)
            words.append(said)
        everything['selfcheck'] = {s: 'selfcheck pilot=%s games=12 digest=otherotherother0' % s for s in ('km3', 'kx3')}
        self.edit_pin(**everything)
        self.rebuild_again()
        msg = self.refused_resume(d)
        registered = self.manifest(d)['selfcheck']
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] ' + self.not_registered_under(
            *words, *(f"the {s} self-check text differs (registered: {registered[s]}; pin now: selfcheck pilot={s} games=12 digest=otherotherother0)" for s in ('km3', 'kx3'))))

    def test_an_empty_entry_and_a_missing_one_are_the_same_not_recorded_on_both_sides(self):
        d = self.started()
        man, pin = self.manifest(d), dict(self.pin)
        blank = dict(man, slow_report=dict(man['slow_report'], engine_ref=''))
        self.assertIsNone(sr.registered_vs_pin(blank, {k: v for k, v in pin.items() if k != 'engine_ref'}), 'blank registered, missing in the pin: no difference')
        self.assertIsNone(sr.registered_vs_pin(blank, dict(pin, engine_ref=None)), 'blank registered, null in the pin: no difference')
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(blank, pin)
        self.assertEqual(cm.exception.code, self.not_registered_under(f"engine_ref: registered not recorded, pin now {pin['engine_ref'][:12]}"), 'a real value against a blank one is still a difference')

    def test_registered_vs_pin_names_the_differences_and_ignores_every_other_part_of_the_pin(self):
        d = self.started()
        man, pin = self.manifest(d), dict(self.pin)
        self.assertIsNone(sr.registered_vs_pin(man, pin))
        other_things = dict(program='/elsewhere/strength', program_sha256='0' * 64, selfcheck_measured_on_sha256='1' * 64, threads=9, games_per_hour={'typical_low': 1, 'typical_high': 2, 'wall': 1},
                            pilot_label='kz9 (abc)', reference_label='kr1', panel_label='other', scrub_env_prefixes=['ZZ_'], seed_reserved=pin['seed_reserved'] + [{'base': 24_601_000_000 + 98 * STEP, 'note': 'slot 98'}],
                            pilot_provenance='another', engine='another engine text')
        self.assertIsNone(sr.registered_vs_pin(man, dict(pin, **other_things)), 'nothing about the program, the labels, the rates or the reserved seeds is judged')
        for key, other in (('engine_tree', '5' * 40), ('harness_source_sha256', '6' * 64), ('engine_ref', '7' * 40)):
            with self.assertRaises(SystemExit) as cm:
                sr.registered_vs_pin(man, dict(pin, **{key: other}))
            self.assertEqual(cm.exception.code, self.not_registered_under(f"{key}: registered {str(man['slow_report'][key])[:12]}, pin now {other[:12]}"), key)
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(man, {k: v for k, v in pin.items() if k not in ('engine_tree', 'engine_ref')})
        self.assertEqual(cm.exception.code, self.not_registered_under(f"engine_tree: registered {man['slow_report']['engine_tree'][:12]}, pin now not recorded",
                                                                      f"engine_ref: registered {man['slow_report']['engine_ref'][:12]}, pin now not recorded"), 'a pin without the entry is a different pin')
        for label, gone in (('null', None), ('empty', '')):
            with self.subTest(f'a pin whose entries are {label}'), self.assertRaises(SystemExit) as cm:
                sr.registered_vs_pin(man, dict(pin, engine_tree=gone, harness_source_sha256=gone, engine_ref=gone))
            self.assertEqual(cm.exception.code, self.not_registered_under(
                *(f"{k}: registered {man['slow_report'][k][:12]}, pin now not recorded" for k in ('engine_tree', 'harness_source_sha256', 'engine_ref'))))
            self.assertNotIn('None', cm.exception.code)
        km3, kx3 = man['selfcheck']['km3'], man['selfcheck']['kx3']
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(man, dict(pin, selfcheck={'kx3': pin['selfcheck']['kx3']}))
        self.assertEqual(cm.exception.code, self.not_registered_under(f'the km3 self-check text differs (registered: {km3}; pin now: none)'),
                         'a pin that has no text for a pilot has another text than the registered one')
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(man, {k: v for k, v in pin.items() if k != 'selfcheck'})
        self.assertEqual(cm.exception.code, self.not_registered_under(f'the km3 self-check text differs (registered: {km3}; pin now: none)',
                                                                      f'the kx3 self-check text differs (registered: {kx3}; pin now: none)'))
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(man, dict(pin, selfcheck=None))
        self.assertEqual(cm.exception.code, self.not_registered_under(f'the km3 self-check text differs (registered: {km3}; pin now: none)',
                                                                      f'the kx3 self-check text differs (registered: {kx3}; pin now: none)'), 'a pin whose self-check entry is null has none either')
        long_text = 'selfcheck pilot=kx3 games=12 digest=' + 'f' * 300
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(dict(man, selfcheck=dict(man['selfcheck'], kx3=long_text)), pin)
        self.assertEqual(cm.exception.code, self.not_registered_under(f"the kx3 self-check text differs (registered: {long_text}; pin now: {pin['selfcheck']['kx3']})"), 'both texts whole, none cut short')
        self.assertIsNone(sr.registered_vs_pin(dict(man, selfcheck={}), {k: v for k, v in pin.items() if k != 'selfcheck'}), 'a run with no registered self-check texts has none to compare')
        self.assertIsNone(sr.registered_vs_pin(dict(man, selfcheck=None), pin))

    def test_a_registration_that_did_not_record_an_entry_is_said_to_have_recorded_nothing_and_never_none(self):
        """An old registration has no engine tree, harness hash or engine ref in its slow_report block (or no block at all): against a pin that has them, the difference reads 'registered not
        recorded, pin now <12 characters>'; against a pin that has none either there is none."""
        d = self.started()
        man, pin = self.manifest(d), dict(self.pin)
        keys = ('engine_tree', 'harness_source_sha256', 'engine_ref')
        words = {k: f'{k}: registered not recorded, pin now {pin[k][:12]}' for k in keys}
        for label, block, said in (('one entry left out', {k: v for k, v in man['slow_report'].items() if k != 'engine_tree'}, ['engine_tree']),
                                   ('one entry null', dict(man['slow_report'], harness_source_sha256=None), ['harness_source_sha256']),
                                   ('one entry empty', dict(man['slow_report'], engine_ref=''), ['engine_ref']),
                                   ('all three left out', {k: v for k, v in man['slow_report'].items() if k not in keys}, list(keys)),
                                   ('no block', None, list(keys))):
            with self.subTest(label), self.assertRaises(SystemExit) as cm:
                sr.registered_vs_pin({k: v for k, v in man.items() if k != 'slow_report'} if block is None else dict(man, slow_report=block), pin)
            self.assertEqual(cm.exception.code, self.not_registered_under(*(words[k] for k in said)))
            self.assertNotIn('None', cm.exception.code)
        bare = {k: v for k, v in pin.items() if k not in keys}
        self.assertIsNone(sr.registered_vs_pin(dict(man, slow_report={k: v for k, v in man['slow_report'].items() if k not in keys}), bare), 'nothing recorded and nothing in the pin: no difference')
        with self.assertRaises(SystemExit) as cm:
            sr.registered_vs_pin(man, bare)
        self.assertEqual(cm.exception.code, self.not_registered_under(*(f"{k}: registered {man['slow_report'][k][:12]}, pin now not recorded" for k in keys)))

    def test_an_unrelated_change_of_the_pin_file_does_not_stop_the_dry_run_from_offering_the_replay(self):
        d = self.started()
        self.edit_pin(seed_reserved=self.pin['seed_reserved'] + [{'base': 24_601_000_000 + 99 * STEP, 'note': 'slot 99: a later smoke run'}], threads=5)
        self.rebuild_again()
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, out + err)
        self.assertIn('so a resume would replay both self-checks again against', out)
        self.assertNotIn('it would be refused', out)

    def test_the_pin_the_run_was_registered_under_is_judged_before_the_pin_is_asked_to_be_committed_or_the_record_is_read(self):
        d = self.started()
        change, words = self.pin_change(d, 'the engine tree')
        self.edit_pin(**change)
        self.rebuild_again()
        os.remove(self.cloud + '.build.json')
        os.environ.pop(ALLOW_PIN_VAR, None)  # the pin is not committed either, and the program has no record
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] ' + self.not_registered_under(words))
        self.assertEqual(self.last_replays, [])
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn(self.would_be_refused(self.not_registered_under(words)), out)

    def test_check_program_change_judges_the_pin_the_committed_pin_and_the_record_and_hands_back_the_state_the_record_and_the_deadline(self):
        d = self.started()
        man = self.manifest(d)
        rec = self.rebuild_again()
        want_record = dict(rec, record_file=self.cloud + '.build.json', record_sha256=sha(self.cloud + '.build.json'))

        def check(rule='off', days=(), clock=None, pin=None, pin_path=None):
            return sr.check_program_change(man, pin or self.pin, pin_path or self.pin_path, self.repo, rule, days, (clock or self.clock).now)
        state, got, deadline = check()
        self.assertEqual((state['state'], got, deadline), ('bypassed', want_record, None))
        self.assertEqual(check('on', sr.SCHOOL_DAYS, FakeClock(chi(2026, 10, 7, 20, 0)))[2], chi(2026, 10, 8, 6, 30), "the next school morning's 6:30 cut")
        self.assertIsNone(check('on', (), FakeClock(chi(2026, 10, 7, 12, 0)))[2], 'no school days: no cut')
        with self.assertRaises(SystemExit) as cm:
            check('on', sr.SCHOOL_DAYS, FakeClock(chi(2026, 10, 7, 10, 0)))
        self.assertIn('REFUSED: the self-check runs for hours and it is school time', cm.exception.code)
        with self.assertRaises(SystemExit) as cm:
            check(pin=dict(self.pin, engine_tree='77' * 20))
        self.assertIn('the pin in use is not the pin this run was registered under (engine_tree:', cm.exception.code)
        os.remove(self.cloud + '.build.json')
        with self.assertRaises(SystemExit) as cm:
            check()
        self.assertIn('has no build record', cm.exception.code)
        os.environ.pop(ALLOW_PIN_VAR, None)
        with self.assertRaises(SystemExit) as cm:
            check()
        self.assertIn('REFUSED: the pin is not the committed one:', cm.exception.code, 'the committed pin is asked for before the record is read')

    def test_a_dry_run_at_school_time_with_the_rule_on_says_the_resume_would_be_refused_for_the_replay(self):
        d = self.started()
        self.rebuild_again()
        self.clock = FakeClock(chi(2026, 10, 7, 10, 0))  # a Wednesday morning, the rule turned on for this call
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False, school='on')
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertTrue(lines[1].endswith('(it would be refused: the self-check runs for hours and it is school time (the school-morning rule waits until Wed 17:00 Chicago time); '
                                          'start it after that, or with --school-rule off)'), lines[1])
        self.assertNotIn('REFUSED', out, 'one "refused", not "refused: REFUSED:"')
        self.assertNotIn('a resume would replay', out)

    def test_a_dry_run_says_it_would_be_refused_when_the_pin_is_not_the_committed_one(self):
        d = self.started()
        self.rebuild_again()
        os.environ.pop(ALLOW_PIN_VAR, None)
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertIn('(it would be refused: the pin is not the committed one: ' + f'HEAD has no {PIN_REL} in {self.repo} (not a git repository, no commit, or the file is not committed)', lines[1])
        self.assertNotIn('REFUSED', out)
        self.commit_pin()
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn(f'so a resume would replay both self-checks again against {COMMITTED_DIGESTS} (hours for kx3)', out, 'with the committed pin the dry run offers the replay in the committed pin\'s words')

    # ------------------------------------------------------------------------------------------------ which program the previous sitting ran with
    def test_a_second_change_reads_from_the_build_the_first_one_went_to(self):
        d = self.started('6')
        a = sha(self.cloud)
        self.rebuild_again()
        b = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.rebuild_again(FAKE_PROGRAM + '\n# a third build\n')
        c = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual([(e['old_sha256'], e['new_sha256']) for e in self.events(d, 'program_changed')], [(a, b), (b, c)], 'A -> B, then B -> C (not A -> C)')
        self.assertEqual([e['program_sha256'] for e in self.events(d, 'sitting_call')], [a, b, c], 'each sitting call says which program it ran with')
        lines = read(os.path.join(d, 'SLOW_REPORT.md')).splitlines()
        self.assertEqual([l.split(' after a restart', 1)[0].split('): ', 1)[1] for l in lines if l.startswith('- **The program changed mid-run**')],
                         [f'sha256 `{a[:12]}` -> `{b[:12]}`', f'sha256 `{b[:12]}` -> `{c[:12]}`'], 'the page prints each')

    def test_going_back_to_an_earlier_build_and_on_to_a_new_one_reads_from_the_one_it_went_back_to(self):
        d = self.started('6')
        a = sha(self.cloud)
        self.rebuild_again()
        b = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.put_program(self.cloud, FAKE_PROGRAM + '\n# built on the cloud\n')  # the registered build again, byte for byte
        self.assertEqual(sha(self.cloud), a)
        replays = len(self.replayed)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual(len(self.replayed), replays, 'the registered build needs no replay')
        self.assertEqual(len(self.events(d, 'program_changed')), 1, 'and is no change')
        self.rebuild_again(FAKE_PROGRAM + '\n# a third build\n')
        c = sha(self.cloud)
        self.assertEqual(self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual([(e['old_sha256'], e['new_sha256']) for e in self.events(d, 'program_changed')], [(a, b), (a, c)], 'A -> B, back to A, then A -> C (not B -> C)')
        self.assertEqual([e['program_sha256'] for e in self.events(d, 'sitting_call')], [a, b, a, c])
        lines = read(os.path.join(d, 'SLOW_REPORT.md')).splitlines()
        self.assertEqual([l.split(' after a restart', 1)[0].split('): ', 1)[1] for l in lines if l.startswith('- **The program changed mid-run**')],
                         [f'sha256 `{a[:12]}` -> `{b[:12]}`', f'sha256 `{a[:12]}` -> `{c[:12]}`'])

    def test_program_in_use_before_follows_the_log_the_last_change_or_sitting_wins(self):
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        log = os.path.join(d, 'slow_report_log.jsonl')
        os.remove(log)
        self.assertEqual(sr.program_in_use_before(d, man), reg, 'no log: the registered program')
        self.assertEqual(sr.program_in_use_before(d, dict(man, program_sha256=None)), None)
        change = lambda new: self.change_event(man, new)  # (a change as reverify_program writes it for this run: only such a line counts)
        for label, events, want in (('a sitting that ran the registered build', [{'event': 'sitting_call', 'program_sha256': reg}], reg),
                                    ('a change', [change('b' * 64)], 'b' * 64),
                                    ('a sitting after a change', [change('b' * 64), {'event': 'sitting_call', 'program_sha256': 'c' * 64}], 'c' * 64),
                                    ('a change after a sitting', [{'event': 'sitting_call', 'program_sha256': 'c' * 64}, change('b' * 64)], 'b' * 64),
                                    ('a sitting that had no program (missing file)', [change('b' * 64), {'event': 'sitting_call', 'program_sha256': None}], 'b' * 64),
                                    ('a sitting call from before the entry existed', [change('b' * 64), {'event': 'sitting_call', 'threads': 2}], 'b' * 64),
                                    ('values that are not text', [{'event': 'sitting_call', 'program_sha256': 7}, change(['x'])], reg),
                                    ('other events', [{'event': 'slice_end', 'program_sha256': 'd' * 64, 'new_sha256': 'e' * 64}], reg)):
            with self.subTest(label):
                write(log, ''.join(json.dumps(e) + '\n' for e in events) + '{"event": "sitting_call", "program_sha2')  # (and a last line torn by a kill)
                self.assertEqual(sr.program_in_use_before(d, man), want)

    def test_program_in_use_before_does_not_take_a_forged_or_foreign_line_for_a_change(self):
        """The log is not covered by manifest.sha256: a 'program_changed' line the run could not have written (another engine tree, a record for another file, other self-check texts, on a
        run that is not on the rebuilt route ...) must not set the 'old_sha256' the next real change is logged with, which the page prints."""
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        log = os.path.join(d, 'slow_report_log.jsonl')
        for label, over in self.forgeries(man, 'f' * 64):
            with self.subTest(label):
                write(log, json.dumps({'event': 'sitting_call', 'program_sha256': 'c' * 64}) + '\n' + json.dumps(self.change_event(man, 'f' * 64, **over)) + '\n')
                self.assertEqual(sr.program_in_use_before(d, man), 'c' * 64, 'the sitting before it is still the last word')
                write(log, json.dumps(self.change_event(man, 'f' * 64, **over)) + '\n')
                self.assertEqual(sr.program_in_use_before(d, man), reg, 'and with nothing before it, the registered program')
        write(log, json.dumps({'event': 'program_changed'}) + '\n' + json.dumps({'event': 'program_changed', 'new_sha256': 'f' * 64}) + '\n')
        self.assertEqual(sr.program_in_use_before(d, man), reg, 'a line with nothing but the name of the event, or only the new hash, is no change')
        write(log, json.dumps(self.change_event(man, 'f' * 64)) + '\n')
        self.assertEqual(sr.program_in_use_before(d, man), 'f' * 64, 'while the line a replay writes is one')
        for route in ('pinned', None, 'something else'):  # a run that is not on the rebuilt route has no change at all, however good the line looks
            block = {k: v for k, v in man['slow_report'].items() if k != 'program_route'}
            other = dict(man, slow_report=dict(block, program_route=route) if route else block)
            self.assertEqual(sr.program_in_use_before(d, other), reg, route)

    # ------------------------------------------------------------------------------------------------ which lines of the log count
    def test_a_program_changed_line_in_the_log_of_a_pinned_run_is_ignored_and_the_resume_is_refused_as_before(self):
        code, out, err = self.cli('--deals', '1', '--max-games', '10', spawn=self.spawn)  # registered on the pinned route
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        man = self.manifest(d)
        registered = sha(self.program)
        write(self.program, FAKE_PROGRAM + '\n# a rebuild at the pinned path\n', mode=0o755)
        self.write_record(self.program)
        new = sha(self.program)
        self.append_log(d, self.change_event(man, new))  # a line that reverify_program could have written, in the log of a run that can never have one
        self.assertEqual(man['slow_report']['program_route'], 'pinned')
        self.assertEqual(sr.accepted_program_shas(d, man), {registered})
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n'
                              f'  {self.program} has sha256 {new[:12]}, but this run was registered with the program at that path with sha256 {registered[:12]}. ' + RESUME_NEEDS_PINNED)
        self.assertEqual(self.replayed, [], 'no self-check is replayed for a pinned run')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn('(it would be refused: ' + f'{self.program} has sha256 {new[:12]}, {sr.PROGRAM_PROBLEM} {registered[:12]}. ' + RESUME_NEEDS_PINNED + ')', out)

    def test_forged_or_foreign_program_changed_lines_of_a_rebuilt_run_are_ignored_and_a_good_one_is_honoured(self):
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        new = 'b' * 64
        good = self.change_event(man, new)
        log = os.path.join(d, 'slow_report_log.jsonl')
        self.append_log(d, good)
        self.assertEqual(sr.accepted_program_shas(d, man), {reg, new}, 'the line a replay writes counts')
        os.remove(log)
        record = good['build_record']
        for label, over in self.forgeries(man, new):
            with self.subTest(label):
                write(log, '')  # (a log of this line alone)
                self.append_log(d, self.change_event(man, new, **over))
                self.assertEqual(sr.accepted_program_shas(d, man), {reg})
        write(log, '')
        self.append_log(d, self.change_event(man, 'c' * 64, build_record=dict(record, program_sha256='c' * 64)), self.change_event(man, 'd' * 64, selfcheck={}),
                        self.change_event(man, 'e' * 64, build_record=dict(record, program_sha256='e' * 64), pin_committed=DROP, replayed_on=DROP, old_sha256=DROP),
                        self.change_event(man, 'f' * 64, build_record=dict(record, program_sha256='f' * 64), at=DROP))
        self.assertEqual(sr.accepted_program_shas(d, man), {reg, 'c' * 64, 'e' * 64},
                         'one bad line does not spoil the good ones around it; the entries that only describe the change are not needed, the time it was written is (the page counts games before and after it)')

    def test_is_program_change_is_the_one_test_of_the_event_the_rebuilt_route_and_a_consistent_line(self):
        """accepted_program_shas, program_in_use_before and the page all ask is_program_change: it needs the event 'program_changed', a run registered on the rebuilt route, and a line that
        program_change_valid finds consistent with the registration (which says nothing of who wrote it)."""
        d = self.started()
        man = self.manifest(d)
        ms = sha(os.path.join(d, 'manifest.json'))  # (the run a line is written for: the sha256 of its manifest.json)
        self.assertEqual(ms, manifest_text_sha256(man), 'the helper that writes the lines of these tests names the run the way the log does')
        self.assertEqual(man['slow_report']['program_route'], 'rebuilt')
        good = self.change_event(man, 'b' * 64)
        self.assertTrue(sr.is_program_change(good, man, ms))
        self.assertTrue(sr.program_change_valid(good, man, ms))
        self.assertFalse(sr.is_program_change(dict(good, event='slice_end'), man, ms), 'another event, however much it looks like a change')
        self.assertFalse(sr.is_program_change({k: v for k, v in good.items() if k != 'event'}, man, ms), 'no event at all')
        self.assertFalse(sr.is_program_change(dict(good, event=None), man, ms))
        for route in ('pinned', 'something else', None):
            block = dict(man['slow_report'], program_route=route)
            self.assertFalse(sr.is_program_change(good, dict(man, slow_report=block), ms), f'the route {route}: the run is byte for byte or nothing')
            self.assertTrue(sr.program_change_valid(good, dict(man, slow_report=block), ms), 'whether the line is consistent does not depend on the route')
        self.assertFalse(sr.is_program_change(good, {k: v for k, v in man.items() if k != 'slow_report'}, ms), 'a manifest with no slow_report block has no route')
        for label, over in self.forgeries(man, 'b' * 64):
            with self.subTest(label):
                line = self.change_event(man, 'b' * 64, **over)
                self.assertFalse(sr.is_program_change(line, man, ms))
                self.assertFalse(sr.program_change_valid(line, man, ms))
        lean = self.change_event(man, 'c' * 64, pin_committed=DROP, replayed_on=DROP, old_sha256=DROP, pilot=DROP, reference=DROP)
        self.assertTrue(sr.is_program_change(lean, man, ms), 'what only describes the change is not needed')
        for at in (DROP, None, '', 5):
            with self.subTest(at=at):
                self.assertFalse(sr.is_program_change(self.change_event(man, 'c' * 64, at=at), man, ms), "without the time it was written the games before and after it cannot be counted: not a change")
        self.assertFalse(sr.program_change_valid(good, man, None), 'a caller that does not know the run cannot vouch for a line')
        self.assertFalse(sr.program_change_valid(good, man, '9' * 64), 'a line is for one run: the sha256 of its manifest.json')
        self.assertIn('NOT authentication', sr.program_change_valid.__doc__, 'the check keeps stray lines out; it does not say who wrote one')

    def test_a_forged_line_does_not_let_a_changed_program_skip_the_replay(self):
        d = self.started('6')
        man = self.manifest(d)
        self.rebuild_again()
        new = sha(self.cloud)
        self.append_log(d, self.change_event(man, new, selfcheck={'km3': 'selfcheck pilot=km3 games=12 digest=0000', 'kx3': 'selfcheck pilot=kx3 games=12 digest=0000'}))
        replays = len(self.replayed)
        code, out, err = self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(self.replayed) - replays, 2, 'both self-checks were replayed: the forged line accepted nothing')
        real = [e for e in self.events(d, 'program_changed') if e['selfcheck'] == man['selfcheck']]
        self.assertEqual(len(real), 1)

    def test_a_forged_line_does_not_become_the_old_program_of_the_next_real_change_or_a_line_on_the_page(self):
        """The 'old' program of a change is the one the last sitting ran with. A line the run could not have written must not set it, and the page does not show it."""
        d = self.started('6')
        man = self.manifest(d)
        reg = man['program_sha256']
        forged = [self.change_event(man, 'f' * 64, **over) for label, over in self.forgeries(man, 'f' * 64)]
        self.append_log(d, *forged, {'event': 'program_changed', 'new_sha256': 'e' * 64})
        self.rebuild_again()
        new = sha(self.cloud)
        code, out, err = self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        (change,) = self.events(d, 'program_changed')[len(forged) + 1:]
        self.assertEqual((change['old_sha256'], change['new_sha256']), (reg, new), 'from the registered program, not from a program a forged line named')
        lines = [l for l in read(os.path.join(d, 'SLOW_REPORT.md')).splitlines() if l.startswith('- **The program changed mid-run**')]
        self.assertEqual(len(lines), 1, lines)
        self.assertIn(f'sha256 `{reg[:12]}` -> `{new[:12]}`', lines[0])
        self.assertNotIn('None', read(os.path.join(d, 'SLOW_REPORT.md')).replace('repository commit `None`', ''))

    def test_a_good_line_in_the_log_lets_the_program_it_names_go_on_without_a_replay(self):
        d = self.started('6')
        man = self.manifest(d)
        rec = self.rebuild_again()
        new = sha(self.cloud)
        self.append_log(d, self.change_event(man, new, build_record=dict(rec, record_file=self.cloud + '.build.json', record_sha256=sha(self.cloud + '.build.json'))))
        replays = len(self.replayed)
        code, out, err = self.cli('--dir', d, '--max-games', '6', deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(len(self.replayed), replays, 'a program that was accepted in the log is not replayed again')
        self.assertEqual(len(self.events(d, 'program_changed')), 1, 'and is not logged again')
        self.assertEqual(self.events(d, 'sitting_call')[-1]['program_sha256'], new)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 12)

    # ------------------------------------------------------------------------------------------------ nothing left to play
    def test_a_run_with_every_game_played_is_not_replayed_for_a_changed_program_and_still_gets_its_page(self):
        d = self.started('32')
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        registered = sha(self.cloud)
        self.rebuild_again()
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        before_manifest = (read(os.path.join(d, 'manifest.json')), read(os.path.join(d, 'manifest.sha256')))
        before = self.snapshot(d)
        replays, started = list(self.replayed), len(self.spawn.seen)
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertIn(f'all 32 games are played, so nothing is run: the program at {self.cloud} has another sha256 than registered, which the page does not depend on '
                      '(no self-check is replayed and no program change is logged)', lines)
        self.assertEqual(self.replayed, replays, 'no self-check was replayed')
        self.assertEqual(self.events(d, 'program_changed'), [], 'and no program change was logged')
        self.assertEqual(len(self.spawn.seen), started, 'no program was started')
        after = self.snapshot(d)
        self.assertEqual((after['calls'], after['games'], after['lock']), (before['calls'], before['games'], False))
        self.assertEqual(after['events'], before['events'] + ['report_written'], 'no sitting was called, nothing was run: the page was written')
        self.assertIn(f'SLOW_REPORT.md written in {d}', lines)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertNotIn('PARTIAL', page)
        self.assertNotIn('The program changed mid-run', page)
        self.assertIn(f'Program `{self.cloud}` sha256 `{registered[:12]}`.', page, 'the page names the program the run was registered with')
        self.assertEqual((read(os.path.join(d, 'manifest.json')), read(os.path.join(d, 'manifest.sha256'))), before_manifest)
        self.assertFalse(any('running:' in l for l in lines))

    def test_a_run_with_one_game_left_is_replayed_for_a_changed_program_before_the_last_game(self):
        d = self.started('31')
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 31)
        self.rebuild_again()
        new = sha(self.cloud)
        replays = len(self.replayed)
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertNotIn('so nothing is run', out)
        self.assertEqual(len(self.replayed) - replays, 2, 'one game to go: both self-checks are replayed')
        self.assertEqual([e['new_sha256'] for e in self.events(d, 'program_changed')], [new])
        self.assertIn('running: 1 game to go, 2 at a time', out)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)

    # ------------------------------------------------------------------------------------------------ what a refusal tells a person to do
    def test_the_refusal_of_a_changed_program_says_a_pinned_run_cannot_go_on_with_a_rebuild_and_a_rebuilt_run_how_to_get_one(self):
        self.assertEqual(sr.PROGRAM_PROBLEM, 'but this run was registered with the program at that path with sha256', 'the words every caller looks for are unchanged')
        d = self.started()
        man = self.manifest(d)
        reg = man['program_sha256']
        self.assertEqual(man['slow_report']['program_route'], 'rebuilt')
        self.rebuild_again()
        new = sha(self.cloud)
        want_rebuilt = [f'{self.cloud} has sha256 {new[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS]
        self.assertEqual(sr.verify_inputs(man), want_rebuilt)
        self.assertIn('rebuild with the "rebuild_command" in the registration\'s build record', want_rebuilt[0])
        self.assertNotIn('registered on the pinned route', want_rebuilt[0])
        pinned_words = ('(this run was registered on the pinned route, which has no build record and no rebuild; only a run registered with --program can go on with a rebuild)')
        for label, block in (('the pinned route', dict(man['slow_report'], program_route='pinned')), ('no route recorded', {k: v for k, v in man['slow_report'].items() if k != 'program_route'}),
                             ('a route that is not known', dict(man['slow_report'], program_route='something else')), ('no slow report block', None)):
            with self.subTest(label):
                other = dict(man, slow_report=block) if block is not None else {k: v for k, v in man.items() if k != 'slow_report'}
                (problem,) = sr.verify_inputs(other)
                self.assertEqual(problem, f'{self.cloud} has sha256 {new[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS_PINNED)
                self.assertIn(pinned_words, problem)
                self.assertNotIn('rebuild_command', problem)
                self.assertNotIn('PROGRAM.build.json', problem, 'no rebuild record is on offer')
        os.remove(self.cloud)
        self.assertEqual(sr.verify_inputs(man), [f'{self.cloud} is missing, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS])
        self.assertEqual(sr.verify_inputs(dict(man, slow_report=dict(man['slow_report'], program_route='pinned'))), [f'{self.cloud} is missing, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS_PINNED])

    def test_a_resume_that_is_locked_out_replays_nothing(self):
        d = self.started()
        self.rebuild_again()
        fd = os.open(os.path.join(d, 'slow_report.lock'), os.O_CREAT | os.O_RDWR, 0o644)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # another wrapper is on this run
        replayed = list(self.replayed)
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertIn('REFUSED: another slow_report.py', str(code))
        self.assertEqual(self.replayed, replayed, 'the hours-long replay is not started by a wrapper that does not hold the lock')
        self.assertEqual(self.events(d, 'program_changed'), [])

    def test_the_replay_is_bounded_by_the_school_morning_and_refused_at_school_time_like_the_one_at_registration(self):
        d = self.started()
        self.rebuild_again()
        self.clock = FakeClock(chi(2026, 10, 7, 10, 0))  # a Wednesday morning, the rule turned on for this call (it was registered off)
        msg = self.refused_resume(d, school='on')
        self.assertIn('REFUSED: the self-check runs for hours and it is school time (the school-morning rule waits until Wed 17:00 Chicago time); start it after that, or with --school-rule off', msg)
        self.assertEqual(self.last_replays, [])
        self.clock = FakeClock(chi(2026, 10, 7, 20, 0))  # Wednesday evening: allowed, and over by the morning cut
        self.deadlines.clear()
        code, out, err = self.cli('--dir', d, '--max-games', '4', deck=False, school='on', spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.deadlines, [chi(2026, 10, 8, 6, 30)] * 2)
        self.rebuild_again(FAKE_PROGRAM + '\n# once more\n')
        self.deadlines.clear()
        self.clock = FakeClock(chi(2026, 10, 7, 10, 0))
        code, out, err = self.cli('--dir', d, '--max-games', '4', deck=False, school=None, spawn=self.spawn)  # the registered rule: off
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.deadlines, [None, None], 'with the rule off there is no cut to bound the replay by')

    def test_a_third_program_during_the_resumed_run_is_still_refused_by_the_check_before_each_sitting(self):
        self.clock = FakeClock(chi(2026, 10, 7, 5, 0))  # Wednesday 5:00 am: a sitting may start, and is cut at 6:30
        d = self.started()
        registered = sha(self.cloud)
        self.rebuild_again()
        b = sha(self.cloud)
        swapped = []

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            if not swapped:
                swapped.append(1)
                self.rebuild_again(FAKE_PROGRAM + '\n# a third build, swapped in while the first resumed sitting ran\n')
            return p
        write(os.path.join(d, 'hang.flag'), '2')  # the program plays 2 games and then hangs on a third until the 6:30 cut
        self.clock.gate, self.clock.gate_until = (lambda: os.path.exists(os.path.join(d, 'hanging.flag'))), chi(2026, 10, 7, 6, 30)  # the cut waits until the program is really hanging
        calls = len(jsonl(os.path.join(d, 'fake_calls.jsonl')))
        code, out, err = self.cli('--dir', d, '--poll-s', '60', school='on', spawn=spawn, deck=False)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n'
                               f'  {self.cloud} has sha256 {sha(self.cloud)[:12]}, but this run was registered with the program at that path with sha256 {registered[:12]}. ' + RESUME_NEEDS)
        self.assertNotEqual(sha(self.cloud), b)
        self.assertEqual(len(jsonl(os.path.join(d, 'fake_calls.jsonl'))), calls + 1, 'the second sitting was not started')
        self.assertEqual([e['new_sha256'] for e in self.events(d, 'program_changed')], [b], 'the second change was never accepted, so it was never logged')
        self.assertEqual(sr.accepted_program_shas(d, self.manifest(d)), {registered, b})

    # ------------------------------------------------------------------------------------------------ the dry run of the folder
    def played_line(self, status):
        return ('played so far: 5 kx3 games + 5 cheap km3 baseline games of 16 kx3 games + 16 cheap km3 baseline games planned; '
                f'11 kx3 games + 11 cheap km3 baseline games to go ({status})')

    def test_the_dry_run_says_what_a_resume_would_do_with_a_changed_program_and_writes_and_replays_nothing(self):
        d = self.started()
        self.rebuild_again()
        resume = f'python3 rl/strength/slow_report.py --dir {d} --school-rule off'
        before = {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}
        replayed = list(self.replayed)
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        status = (f"the program at {self.cloud} has another sha256 than registered; its build record is for the pinned source, so a resume would replay both self-checks again against "
                  f"{FILE_DIGESTS} (hours for kx3) and, if they match, go on and log it as 'program changed mid-run'; resume with: {resume}")
        self.assertEqual(lines[1], self.played_line(status))
        self.assertEqual(lines[2:], ['dry run: nothing written'])
        self.assertEqual(self.replayed, replayed)
        self.assertEqual({n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}, before)

    def test_the_dry_run_says_it_would_be_refused_when_the_record_of_the_changed_program_is_not_good(self):
        d = self.started()
        self.rebuild_again()
        os.remove(self.cloud + '.build.json')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, out + err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertEqual(lines[1], self.played_line(f'it would be refused: {self.cloud} has no build record ({self.cloud}.build.json); {RECORD_HINT}. Nothing was written.'))
        self.rebuild_again(engine_tree_archived='1' * 40)
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn(f"(it would be refused: the build record says the engine tree that went into {self.cloud} is 111111111111, not the pinned {self.pin['engine_tree'][:12]}, "
                      'so it is not a build of the pinned source. Nothing was written.)', out)
        self.assertNotIn('REFUSED', out)

    def test_the_dry_run_of_a_complete_run_says_complete_whatever_the_program(self):
        d = self.started('32')
        self.rebuild_again()
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, out + err)
        self.assertIn('0 kx3 games + 0 cheap km3 baseline games to go (complete)', out)

    # ------------------------------------------------------------------------------------------------ a run whose games are all played: the dry run, the resume and --report-only
    DRY_HINT = '; every game is played, so --report-only writes the page from them'
    RESUME_HINT = '\n  Every game is played: --report-only writes the page from them without these files.'

    def dry_status(self, d):
        """The status in brackets that ends the second line of `--dir D --dry-run` (the line that says how many games are played, planned and to go), after checking the shape of the whole
        output: the question, that line, 'dry run: nothing written'."""
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual((code, err), (0, ''), out)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        self.assertEqual(len(lines), 3, lines)
        self.assertTrue(lines[0].startswith('question: '), lines[0])
        self.assertEqual(lines[2], 'dry run: nothing written')
        self.assertTrue(lines[1].startswith('played so far: ') and lines[1].endswith(')'), lines[1])
        return lines[1].split(' to go (', 1)[1][:-1]

    def deck_problem(self, was):
        return f'my-list ({self.deck}) has changed since registration (sha256 {sha(self.deck)[:12]} instead of {was[:12]})'

    def edit_deck(self):
        was = sha(self.deck)
        write(self.deck, DECK_TEXT.replace('Torchic', 'Treecko'))
        return was

    def test_the_dry_run_of_a_finished_run_whose_deck_changed_says_it_would_be_refused_and_that_report_only_writes_the_page(self):
        d = self.started('32')
        self.assertEqual(self.manifest(d)['slow_report']['program_route'], 'rebuilt')
        was = self.edit_deck()
        status = self.dry_status(d)
        self.assertEqual(status, 'it would be refused: ' + self.deck_problem(was) + self.DRY_HINT)
        self.assertNotIn('complete', status)

    def test_the_dry_run_of_a_run_with_games_to_go_whose_deck_changed_says_it_would_be_refused_without_the_report_only_hint(self):
        d = self.started('10')
        was = self.edit_deck()
        self.assertEqual(self.dry_status(d), 'it would be refused: ' + self.deck_problem(was))

    def test_a_finished_pinned_run_with_a_changed_program_is_refused_by_the_dry_run_and_the_resume_and_both_say_report_only_writes_the_page(self):
        code, out, err = self.cli('--deals', '1', spawn=self.spawn)  # registered on the pinned route, every game played
        self.assertEqual(code, 0, out + err)
        d = self.rundir()
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        reg = sha(self.program)
        write(self.program, FAKE_PROGRAM + '\n# a rebuild at the pinned path\n', mode=0o755)
        problem = f'{self.program} has sha256 {sha(self.program)[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS_PINNED
        self.assertEqual(self.dry_status(d), 'it would be refused: ' + problem + self.DRY_HINT, 'a pinned run is never "complete" with another program, and no replay is on offer')
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  {problem}'
                              + self.RESUME_HINT)
        self.assertEqual(self.replayed, [])
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        code, out, err = self.cli('--dir', d, '--report-only', deck=False)
        self.assertEqual(code, 0, out + err)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertNotIn('PARTIAL', page)
        self.assertIn(f'Program `{self.program}` sha256 `{reg[:12]}`.', page, 'the page of the games, from the program the run was registered with')

    def test_a_finished_rebuilt_run_whose_program_is_gone_is_refused_by_the_dry_run_and_the_resume_and_both_say_report_only_writes_the_page(self):
        d = self.started('32')
        reg = sha(self.cloud)
        os.remove(self.cloud)
        problem = f'{self.cloud} is missing, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS
        self.assertEqual(self.dry_status(d), 'it would be refused: ' + problem + self.DRY_HINT)
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  {problem}'
                              + self.RESUME_HINT)
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
        self.assertTrue(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')))

    def test_a_finished_rebuilt_run_with_a_changed_program_and_a_changed_deck_lists_both_and_then_the_report_only_hint(self):
        d = self.started('32')
        reg = sha(self.cloud)
        self.rebuild_again()
        was = self.edit_deck()
        program = f'{self.cloud} has sha256 {sha(self.cloud)[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS
        self.assertEqual(self.dry_status(d), 'it would be refused: ' + program + '; ' + self.deck_problem(was) + self.DRY_HINT, 'the problems joined by "; ", the hint once, at the end')
        msg = self.refused_resume(d)
        self.assertEqual(msg, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n'
                              f'  {program}\n  {self.deck_problem(was)}' + self.RESUME_HINT)
        self.assertEqual(self.last_replays, [], 'nothing is replayed for a program when the deck is wrong too')

    def test_the_report_only_hint_is_for_a_finished_run_only(self):
        """With games still to play, --report-only would write a PARTIAL page and the run still has to be fixed or registered again: the refusal and the dry run say no more than the problems."""
        d = self.started('10')
        reg = sha(self.cloud)
        self.rebuild_again()
        was = self.edit_deck()
        program = f'{self.cloud} has sha256 {sha(self.cloud)[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS
        self.assertEqual(self.dry_status(d), 'it would be refused: ' + program + '; ' + self.deck_problem(was))
        msg = self.refused_resume(d)
        self.assertTrue(msg.endswith(f'nothing is run:\n  {program}\n  {self.deck_problem(was)}'), msg)
        self.assertNotIn('--report-only', msg)
        os.remove(self.cloud)
        self.assertNotIn('--report-only', self.dry_status(d))
        self.assertNotIn('--report-only', self.refused_resume(d))

    def test_a_finished_rebuilt_run_with_a_changed_program_that_is_there_is_complete_whatever_else_is_wrong_with_the_record_and_the_pin(self):
        d = self.started('32')
        self.rebuild_again()
        os.remove(self.cloud + '.build.json')  # no record,
        os.environ.pop(ALLOW_PIN_VAR, None)  # a pin that is not committed,
        change, words = self.pin_change(d, 'the engine tree')
        self.edit_pin(**change)  # and a pin that is not the one the run was registered under: nothing is replayed, so none of it matters
        self.assertEqual(self.dry_status(d), 'complete')
        os.remove(os.path.join(d, 'SLOW_REPORT.md'))
        before = self.snapshot(d)
        code, out, err = self.cli('--dir', d, deck=False, spawn=self.spawn)
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'all 32 games are played, so nothing is run: the program at {self.cloud} has another sha256 than registered', out)
        self.assertEqual(self.replayed, [('km3', self.cloud), ('kx3', self.cloud)], 'only the two of the registration')
        self.assertEqual(self.snapshot(d)['events'], before['events'] + ['report_written'])

    def test_program_only_problem_is_true_for_a_program_that_is_there_on_a_rebuilt_run_and_for_nothing_else(self):
        """The one test the resume and `--dir --dry-run` both make for 'the only problem is a program of another sha256 that is there, on a run registered on the rebuilt route'."""
        d = self.started()
        man = self.manifest(d)
        self.rebuild_again()
        (program,) = sr.verify_inputs(man)
        self.assertIn(sr.PROGRAM_PROBLEM, program)
        deck = f'my-list ({self.deck}) has changed since registration (sha256 aaaaaaaaaaaa instead of bbbbbbbbbbbb)'
        self.assertTrue(sr.program_only_problem(man, [program]))
        self.assertTrue(sr.program_only_problem(man, [program, program]), 'every problem is that one')
        for label, problems in (('no problem at all', []), ('the deck only', [deck]), ('the program and the deck', [program, deck]), ('the deck and the program', [deck, program])):
            self.assertFalse(sr.program_only_problem(man, problems), label)
        block = {k: v for k, v in man['slow_report'].items() if k != 'program_route'}
        for route in ('pinned', 'something else', None):
            self.assertFalse(sr.program_only_problem(dict(man, slow_report=dict(block, program_route=route)), [program]), f'a run registered on the route {route} has no rebuild to go on with')
        self.assertFalse(sr.program_only_problem(dict(man, slow_report=block), [program]), 'no route recorded')
        self.assertFalse(sr.program_only_problem({k: v for k, v in man.items() if k != 'slow_report'}, [program]), 'no slow_report block')
        self.assertTrue(sr.program_only_problem(man, [program]))
        os.remove(self.cloud)
        (gone,) = sr.verify_inputs(man)
        self.assertIn(sr.PROGRAM_PROBLEM, gone)
        self.assertFalse(sr.program_only_problem(man, [gone]), 'a program that is not there cannot be replayed on')
        os.makedirs(self.cloud)
        self.assertFalse(sr.program_only_problem(man, [gone]), 'and a folder in its place is not a program either')

    def test_the_dry_run_and_the_resume_both_ask_program_only_problem_and_do_what_it_says(self):
        d = self.started()
        reg = sha(self.cloud)
        self.rebuild_again()
        real = sr.program_only_problem
        asked = []

        def spy(man, problems):
            asked.append(list(problems))
            return real(man, problems)
        with mock.patch.object(sr, 'program_only_problem', spy):
            self.assertTrue(self.dry_status(d).startswith(f'the program at {self.cloud} has another sha256 than registered'))
            self.assertEqual(len(asked), 1, 'the dry run asked once')
            self.assertEqual(self.cli('--dir', d, '--max-games', '2', deck=False, spawn=self.spawn)[0], 0)
        self.assertEqual(len(asked), 2, 'and the resume once')
        self.assertEqual(asked[0], asked[1], 'about the same problems')
        self.assertEqual(len(asked[0]), 1)
        # told "no", both treat the changed program as a refusal like any other (and neither replays anything)
        self.rebuild_again(FAKE_PROGRAM + '\n# once more\n')  # a third build: the first resume accepted the second
        replays = list(self.replayed)
        problem = f'{self.cloud} has sha256 {sha(self.cloud)[:12]}, {sr.PROGRAM_PROBLEM} {reg[:12]}. ' + RESUME_NEEDS
        with mock.patch.object(sr, 'program_only_problem', lambda man, problems: False):
            self.assertEqual(self.dry_status(d), 'it would be refused: ' + problem)
            msg = self.refused_resume(d)
        self.assertTrue(msg.endswith(f'nothing is run:\n  {problem}'), msg)
        self.assertEqual(self.replayed, replays)
        self.assertTrue(self.dry_status(d).startswith(f'the program at {self.cloud} has another sha256 than registered'), 'and told the truth again, it is the replay that is on offer')


class ManifestProvenance(RebuiltFixture):
    """What a registration says about the program has to agree with itself whenever the run is read again (--dir): a manifest that says the run used the pinned binary must carry that
    binary's sha256, and one that says it used a rebuild must carry a build record for that very program with the engine tree and harness source the registration names. A manifest that
    does not (written by hand with a matching manifest.sha256, or by an older version) is refused for a resume or a dry run and flagged on the page of a --report-only; a manifest with no
    route at all makes no claim and passes. The check reads the manifest alone, so it holds whatever pin is in use now."""

    def registered(self, rebuilt):
        code, out, err = self.cli('--deals', '1', '--register-only', *(('--program', self.cloud) if rebuilt else ()))
        self.assertEqual(code, 0, out + err)
        return self.rundir()

    def tampered(self, d, block=None, **top):
        """Rewrite the manifest of `d` (with its matching sha256) with these slow_report entries changed (DROP removes one) and these top-level entries changed."""
        man = self.manifest(d)
        entries = dict(man['slow_report'], **(block or {}))
        man['slow_report'] = {k: v for k, v in entries.items() if v is not DROP}
        man.update(top)
        rewrite_manifest(d, man)
        return man

    def test_a_registration_made_by_this_code_agrees_with_itself_on_either_route(self):
        for rebuilt in (False, True):
            with self.subTest(rebuilt=rebuilt):
                shutil.rmtree(self.out_root, ignore_errors=True)
                d = self.registered(rebuilt)
                self.assertEqual(sr.manifest_provenance_problems(self.manifest(d)), [])
                self.assertEqual(self.manifest(d)['slow_report']['program_route'], 'rebuilt' if rebuilt else 'pinned')

    def pinned_claim(self, prog12, pin12):
        return f'the registration says the run used the pinned binary (sha256 {pin12}), but its program has sha256 {prog12}'

    def test_a_pinned_route_manifest_must_carry_the_pinned_programs_sha256(self):
        d = self.registered(False)
        pinned = self.manifest(d)['slow_report']['pinned_program_sha256']
        self.assertEqual(pinned, self.manifest(d)['program_sha256'])
        man = self.tampered(d, program_sha256='f' * 64)  # (the top-level program hash only: the registration now names a program that is not the pinned one)
        self.assertEqual(sr.manifest_provenance_problems(man), [self.pinned_claim('f' * 12, pinned[:12])])
        man = self.tampered(d, block=dict(pinned_program_sha256='e' * 64), program_sha256=pinned)
        self.assertEqual(sr.manifest_provenance_problems(man), [self.pinned_claim(pinned[:12], 'e' * 12)])
        for how, gone in (('no entry', DROP), ('null', None), ('empty', '')):
            man = self.tampered(d, block=dict(pinned_program_sha256=gone), program_sha256=pinned)
            self.assertEqual(sr.manifest_provenance_problems(man), ['the registration says the run used the pinned binary but does not name the pinned program\'s sha256'], how)

    def test_a_rebuilt_route_manifest_must_carry_the_build_record_of_that_program(self):
        d = self.registered(True)
        man = self.manifest(d)
        rec, block = man['slow_report']['build_record'], man['slow_report']
        prog = man['program_sha256']
        want = {
            'no record': (dict(build_record=DROP), 'the registration says the run used a rebuild but carries no build record'),
            'a null record': (dict(build_record=None), 'the registration says the run used a rebuild but carries no build record'),
            'a record that is a list': (dict(build_record=[rec]), 'the registration says the run used a rebuild but carries no build record'),
            'a record for another program': (dict(build_record=dict(rec, program_sha256='d' * 64)),
                                             f'the build record in the registration is for a program with sha256 {"d" * 12}, not the {prog[:12]} of the run'),
            'a record that does not say which': (dict(build_record={k: v for k, v in rec.items() if k != 'program_sha256'}),
                                                 f'the build record in the registration is for a program with sha256 None, not the {prog[:12]} of the run'),
            'another engine tree': (dict(build_record=dict(rec, engine_tree_archived='c' * 40)),
                                    f"the build record in the registration has the engine tree {'c' * 12} as archived, but the registration names {block['engine_tree'][:12]} as the pinned one"),
            'another harness source': (dict(build_record=dict(rec, harness_source_sha256='b' * 64)),
                                       f"the build record in the registration has the harness source {'b' * 12}, but the registration names {block['harness_source_sha256'][:12]} as the pinned one"),
        }
        for how, (change, problem) in want.items():
            with self.subTest(how):
                self.assertEqual(sr.manifest_provenance_problems(self.tampered(d, block=change)), [problem])
        both = sr.manifest_provenance_problems(self.tampered(d, block=dict(build_record=dict(rec, engine_tree_archived='c' * 40, harness_source_sha256='b' * 64))))
        self.assertEqual(len(both), 2, 'both differences are named, the tree first')
        self.assertTrue(both[0].startswith('the build record in the registration has the engine tree'))
        self.assertTrue(both[1].startswith('the build record in the registration has the harness source'))

    def test_a_route_that_is_not_one_of_ours_is_a_problem_and_no_route_makes_no_claim(self):
        d = self.registered(False)
        for route in ('mystery', '', 5, ['pinned']):
            with self.subTest(route=route):
                self.assertEqual(sr.manifest_provenance_problems(self.tampered(d, block=dict(program_route=route))), [f'the registration names no known program route ({route!r})'])
        for how, gone in (('no entry', DROP), ('null', None)):
            with self.subTest(route=how):
                self.assertEqual(sr.manifest_provenance_problems(self.tampered(d, block=dict(program_route=gone))), [], 'a registration from before the route was recorded claims nothing about it')

    def test_a_manifest_with_no_slow_report_block_has_nothing_to_check(self):
        self.assertEqual(sr.manifest_provenance_problems({'program_sha256': 'a' * 64}), [])
        self.assertEqual(sr.manifest_provenance_problems({'slow_report': None}), [])

    def test_a_resume_and_a_dry_run_refuse_a_manifest_whose_claims_do_not_hold_and_nothing_is_played_or_written(self):
        d = self.registered(True)
        rec = self.manifest(d)['slow_report']['build_record']
        self.tampered(d, block=dict(build_record=dict(rec, engine_tree_archived='c' * 40)))
        problem = f"the build record in the registration has the engine tree {'c' * 12} as archived, but the registration names {self.manifest(d)['slow_report']['engine_tree'][:12]} as the pinned one"
        before = (sorted(os.listdir(d)), read(os.path.join(d, 'manifest.json')))
        for extra in ((), ('--dry-run',), ('--max-games', '4')):
            with self.subTest(extra=extra):
                code, out, err = self.cli('--dir', d, *extra, deck=False, spawn=self.spawned())
                self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: what the registration says about the program does not hold, so nothing is run: '
                                       f'{problem}. This is not a slow report of the pinned build; register a new run.')
                self.assertEqual((sorted(os.listdir(d)), read(os.path.join(d, 'manifest.json'))), before, 'not a file made, not a line logged')
        self.assertEqual(self.replayed[2:], [], 'and no self-check was replayed')

    def test_the_page_of_a_report_only_flags_each_problem_and_a_good_run_has_no_such_line(self):
        d = self.registered(False)
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
        self.assertNotIn('does not hold', read(os.path.join(d, 'SLOW_REPORT.md')))
        pinned = self.manifest(d)['slow_report']['pinned_program_sha256']
        self.tampered(d, program_sha256='f' * 64)
        code, out, err = self.cli('--dir', d, '--report-only', deck=False)
        self.assertEqual(code, 0, out + err)
        page = read(os.path.join(d, 'SLOW_REPORT.md'))
        want = (f"- **What the registration says about the program does not hold**: {self.pinned_claim('f' * 12, pinned[:12])}. "
                'This page reports whatever program ran; it is not a report on the pinned build.')
        self.assertEqual(page.splitlines().count(want), 1)
        self.assertIn(want, page.split('## What was run')[1], 'in the section that says what was run')
        self.assertEqual(sr.write_slow_report(d).count('does not hold'), 1)

    def test_the_pin_the_registration_was_made_under_is_asked_too_while_it_is_still_in_use(self):
        """A registration can agree with itself and still name a pinned program, engine tree or harness source that is not the pin's: while the pin file in use is the one the manifest names
        (same sha256) its entries are the registration's to match; a later pin (another file) is not asked, a run keeps the pin it was registered under."""
        d = self.registered(False)
        self.tampered(d, block=dict(pinned_program_sha256='f' * 64), program_sha256='f' * 64)  # (consistent: the program is the one the registration calls pinned)
        man = self.manifest(d)
        self.assertEqual(sr.manifest_provenance_problems(man), [])
        want = f"the registration names {'f' * 12} as the pinned program sha256, but the pin it was made under (still in use) says {self.pin['program_sha256'][:12]}"
        self.assertEqual(sr.pin_provenance_problems(man, self.pin, self.pin_path), [want])
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: what the registration says about the program does not hold, so nothing is run: {want}. '
                               'This is not a slow report of the pinned build; register a new run.')
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False)[0], 0)
        self.assertIn(f'- **What the registration says about the program does not hold**: {want}. This page reports whatever program ran; it is not a report on the pinned build.',
                      read(os.path.join(d, 'SLOW_REPORT.md')).splitlines())
        later = dict(self.pin, program_sha256='1' * 64, engine_tree='2' * 40, harness_source_sha256='3' * 64)
        write(self.pin_path, json.dumps(later))  # a later pin: another file than the one the manifest names
        self.assertEqual(sr.pin_provenance_problems(man, later, self.pin_path), [], 'not asked')
        self.assertEqual(self.cli('--dir', d, '--dry-run', deck=False)[0], 0, 'and a resume is not refused for it')

    def test_the_self_check_texts_the_registration_records_must_be_the_pins_while_that_pin_is_in_use(self):
        d = self.registered(True)
        man = self.manifest(d)
        self.assertEqual(sr.pin_provenance_problems(man, self.pin, self.pin_path), [], 'a registration made by this code records the pin\'s own texts')
        self.tampered(d, selfcheck=dict(man['selfcheck'], km3='selfcheck pilot=km3 games=12 digest=0000000000000000'))
        man = self.manifest(d)
        want = (f"the registration records the km3 self-check text selfcheck pilot=km3 games=12 digest=0000000000000000, but the pin it was made under (still in use) says "
                f"{self.pin['selfcheck']['km3']}")
        self.assertEqual(sr.pin_provenance_problems(man, self.pin, self.pin_path), [want])
        self.assertEqual(sr.manifest_provenance_problems(man), [], 'the manifest alone cannot tell: it is the pin that knows the texts')
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertIn(want, str(code))
        self.assertIn('REFUSED: what the registration says about the program does not hold', str(code))
        self.tampered(d, selfcheck=dict(man['selfcheck'], ext='selfcheck pilot=ext'))  # a text for a pilot the pin has none for
        self.assertTrue(any('the registration records the ext self-check text' in p and 'says none' in p for p in sr.pin_provenance_problems(self.manifest(d), self.pin, self.pin_path)))
        later = dict(self.pin, selfcheck={'km3': 'x', 'kx3': 'y'})
        write(self.pin_path, json.dumps(later))  # a later pin: another file
        self.assertEqual(sr.pin_provenance_problems(self.manifest(d), later, self.pin_path), [], 'not asked')

    def test_the_pin_is_asked_for_the_engine_tree_and_the_harness_source_of_a_rebuild_too(self):
        d = self.registered(True)
        rec = self.manifest(d)['slow_report']['build_record']
        self.tampered(d, block=dict(engine_tree='c' * 40, harness_source_sha256='b' * 64, build_record=dict(rec, engine_tree_archived='c' * 40, harness_source_sha256='b' * 64)))
        man = self.manifest(d)
        self.assertEqual(sr.manifest_provenance_problems(man), [], 'the registration agrees with itself')
        self.assertEqual(sr.pin_provenance_problems(man, self.pin, self.pin_path),
                         [f"the registration names {'c' * 12} as the pinned engine tree, but the pin it was made under (still in use) says {self.pin['engine_tree'][:12]}",
                          f"the registration names {'b' * 12} as the pinned harness source, but the pin it was made under (still in use) says {self.pin['harness_source_sha256'][:12]}"])
        self.assertTrue(str(self.cli('--dir', d, '--max-games', '4', deck=False, spawn=self.spawned())[0]).startswith(
            f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: what the registration says about the program does not hold, so nothing is run: the registration names'))

    def test_a_registration_made_by_this_code_agrees_with_its_pin_on_either_route(self):
        for rebuilt in (False, True):
            with self.subTest(rebuilt=rebuilt):
                shutil.rmtree(self.out_root, ignore_errors=True)
                d = self.registered(rebuilt)
                self.assertEqual(sr.pin_provenance_problems(self.manifest(d), self.pin, self.pin_path), [])
        self.assertEqual(sr.pin_provenance_problems({'slow_report': {'program_route': None, 'pin': {'sha256': 'a' * 64}}}, self.pin, self.pin_path), [], 'a route that claims nothing is not asked')
        self.assertEqual(sr.pin_provenance_problems({'slow_report': {'program_route': 'pinned'}}, self.pin, self.pin_path), [], 'a registration that names no pin cannot be asked of it')
        self.assertEqual(sr.pin_provenance_problems({}, self.pin, self.pin_path), [])
        self.assertEqual(sr.pin_provenance_problems({'slow_report': {'program_route': 'pinned', 'pin': {'sha256': 'a' * 64}}}, self.pin, os.path.join(self.tmp, 'no-such-pin.json')), [])

    def test_two_problems_are_two_lines(self):
        d = self.registered(True)
        rec = self.manifest(d)['slow_report']['build_record']
        self.tampered(d, block=dict(build_record=dict(rec, engine_tree_archived='c' * 40, harness_source_sha256='b' * 64)))
        page = sr.write_slow_report(d)
        self.assertEqual(len([l for l in page.splitlines() if l.startswith('- **What the registration says about the program does not hold**')]), 2)


class unittest_patch:
    """mock.patch.object as a tiny context manager (kept local so the file reads top to bottom)."""

    def __init__(self, obj, name, value):
        self.obj, self.name, self.value = obj, name, value

    def __enter__(self):
        self.old = getattr(self.obj, self.name)
        setattr(self.obj, self.name, self.value)

    def __exit__(self, *a):
        setattr(self.obj, self.name, self.old)


class LockAndSignals(World):
    def hold(self, path, note=None):
        """Hold the run lock as another wrapper would: an flock on the lock file, with a note saying who."""
        fd = os.open(path, os.O_CREAT | os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, json.dumps(note or {'pid': os.getpid(), 'started': '2026-10-10T10:00:00Z'}).encode())
        self.addCleanup(os.close, fd)
        return fd

    def test_a_second_wrapper_on_the_same_run_directory_is_refused(self):
        d = self.register()
        lock = os.path.join(d, 'slow_report.lock')
        self.hold(lock)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('already running', str(code) + err)
        self.assertIn(f'pid {os.getpid()}', str(code) + err, 'the refusal says who holds the lock')
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
        self.assertTrue(os.path.exists(lock), "the other wrapper's lock is not removed")

    def test_a_lock_file_left_by_a_wrapper_that_is_gone_is_just_taken(self):
        d = self.register()
        dead = subprocess.Popen([sys.executable, '-c', 'pass'])
        dead.wait()
        write(os.path.join(d, 'slow_report.lock'), json.dumps({'pid': dead.pid, 'started': '2026-10-09T10:00:00Z'}))  # nobody holds the flock
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_an_empty_or_unreadable_lock_file_is_a_free_lock_and_a_held_one_is_refused_without_a_note(self):
        d = self.register()
        lock = os.path.join(d, 'slow_report.lock')
        for junk in ('', '{not json', '[1, 2]', json.dumps({'pid': 0}), json.dumps({'pid': -1})):
            write(lock, junk)
            fd, path = sr.acquire_lock(d, lambda m: None)
            self.assertEqual(path, lock)
            sr.release_lock((fd, path))
            self.assertFalse(os.path.exists(lock))
        write(lock, '')
        self.hold(lock, note=['not', 'a', 'dict'])
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('already running', str(code) + err)

    def test_two_wrappers_starting_at_the_same_instant_cannot_both_hold_the_lock(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        child = textwrap.dedent('''
            import sys, time
            sys.path.insert(0, %r)
            import slow_report as sr
            while time.time() < float(sys.argv[2]):
                pass
            try:
                sr.acquire_lock(sys.argv[1], lambda m: None)
            except SystemExit:
                print('refused')
                sys.exit(0)
            print('got', flush=True)
            time.sleep(1.0)  # exits without releasing, as a killed wrapper would: the next round finds a used file and a free lock
        ''' % HERE)
        for round_ in range(5):
            start = time.time() + 1.0
            procs = [subprocess.Popen([sys.executable, '-c', child, d, str(start)], stdout=subprocess.PIPE, text=True) for _ in range(4)]
            outs = sorted(p.communicate()[0].strip() for p in procs)
            self.assertEqual(outs, ['got', 'refused', 'refused', 'refused'], (round_, outs))

    def test_the_program_inherits_the_lock_descriptor_and_a_release_removes_the_file_and_the_descriptor(self):
        d = self.register()
        fd, path = sr.acquire_lock(d, lambda m: None)
        p = None
        try:
            self.assertIn(fd, sr._LOCK_FDS)
            p = sr.default_spawn([sys.executable, '-c', 'import os,sys,time\nos.fstat(%d)\nprint("inherited", flush=True)\ntime.sleep(30)' % fd], dict(os.environ), os.path.join(d, 'child.log'))
            self.addCleanup(lambda: p.poll() is None and p.kill())
            deadline = time.time() + 20
            while 'inherited' not in read(os.path.join(d, 'child.log')) and time.time() < deadline:
                time.sleep(0.05)
            self.assertIn('inherited', read(os.path.join(d, 'child.log')), 'the program got the lock descriptor')
        finally:
            sr.release_lock((fd, path))
            if p is not None:
                p.kill()
                p.wait()
                p._logfh.close()
        self.assertNotIn(fd, sr._LOCK_FDS)
        self.assertFalse(os.path.exists(path))

    def test_a_wrapper_killed_outright_leaves_its_program_holding_the_lock_until_the_program_ends(self):
        self.make()
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')
        cmd = [sys.executable, '-B', os.path.join(HERE, 'slow_report.py'), '--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'off', '--poll-s', '1']
        wrapper = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda w=wrapper: w.poll() is None and w.kill())
        hanging = os.path.join(d, 'hanging.flag')
        deadline = time.time() + 40
        while not os.path.exists(hanging) and time.time() < deadline:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(hanging), 'the program never started a game')
        child_pid = int(read(hanging))
        self.addCleanup(lambda: self.alive(child_pid) and os.kill(child_pid, signal.SIGKILL))
        wrapper.kill()  # SIGKILL: no cleanup runs
        wrapper.wait(timeout=20)
        self.assertTrue(self.alive(child_pid), 'the program outlives a wrapper killed with SIGKILL')
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('already running', str(code) + err, 'a second wrapper must not start a second program on the same run')
        os.kill(child_pid, signal.SIGKILL)
        deadline = time.time() + 20
        while self.alive(child_pid) and time.time() < deadline:
            try:
                os.waitpid(child_pid, os.WNOHANG)
            except ChildProcessError:
                pass
            time.sleep(0.05)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def test_a_signal_that_arrives_while_the_program_is_being_started_still_stops_it(self):
        """The container is stopped just as a sitting starts: SIGTERM must not raise between the start of the program and the code that stops it (that left the program running,
        holding the lock, after its wrapper had gone). The signal waits until the loop that watches the program can stop it."""
        self.set_program(HANG_PROGRAM)
        d = self.register()
        started = []

        def spawn(cmd, env, logfile):
            proc = sr.default_spawn(cmd, env, logfile)
            started.append(proc)
            os.kill(os.getpid(), signal.SIGTERM)  # arrives right after the program was started, before spawn has even returned it
            return proc
        try:
            code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False, spawn=spawn)
            self.assertEqual(code, 128 + signal.SIGTERM, out + err)
            self.assertEqual(len(started), 1)
            self.assertIsNotNone(started[0].poll(), 'the program the wrapper started is stopped, not left running')
            self.assertIn('interrupted', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))])
            self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'and the lock is released')
        finally:
            for p in started:
                if p.poll() is None:
                    p.kill()
                    p.wait()

    def test_the_program_does_not_inherit_the_signals_the_wrapper_holds_while_it_starts_it(self):
        """A child inherits the signal mask of the process that starts it: a program started while SIGTERM is held would never hear the SIGTERM that stops it (it would be killed only after
        the grace period). default_spawn gives the program an empty mask."""
        d = self.register()
        held = signal.pthread_sigmask(signal.SIG_BLOCK, (signal.SIGTERM, signal.SIGHUP, signal.SIGINT))
        try:
            self.assertNotEqual(signal.pthread_sigmask(signal.SIG_BLOCK, ()), set(), 'the test holds the signals, as run_games does while it starts a program')
            log = os.path.join(d, 'mask.log')
            p = sr.default_spawn([sys.executable, '-c', 'print(open("/proc/self/status").read())'], dict(os.environ), log)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, held)
        p.wait(timeout=30)
        p._logfh.close()
        self.assertIn('\nSigBlk:\t0000000000000000\n', read(log), 'nothing is blocked in the program')

    def test_the_signals_are_not_left_blocked_after_a_sitting_is_started(self):
        before = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        d = self.register()
        self.assertEqual(self.cli('--dir', d, '--max-games', '2', deck=False)[0], 0)
        self.assertEqual(signal.pthread_sigmask(signal.SIG_BLOCK, ()), before, 'the signal mask is what it was')
        def failing(cmd, env, logfile):
            raise OSError('no such program')
        with self.assertRaises(OSError):
            self.cli('--dir', d, deck=False, spawn=failing)
        self.assertEqual(signal.pthread_sigmask(signal.SIG_BLOCK, ()), before, 'also when the program could not be started')
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'and the lock is released')

    def test_two_different_stop_signals_that_come_while_the_program_is_being_started_still_stop_it(self):
        """SIGHUP and SIGTERM, held together, arrive together when they are let in. The second handler used to raise at the entry of stop_group, before the program had been signalled,
        and the program was left running with the lock held. Only the first signal raises; the later one is noted."""
        self.set_program(HANG_PROGRAM)
        d = self.register()
        started = []

        def spawn(cmd, env, logfile):
            proc = sr.default_spawn(cmd, env, logfile)
            started.append(proc)
            os.kill(os.getpid(), signal.SIGHUP)
            os.kill(os.getpid(), signal.SIGTERM)
            return proc
        try:
            code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False, spawn=spawn)
            self.assertEqual(code, 128 + signal.SIGHUP, 'the first signal ends the call, the second one does not replace it: ' + out + err)
            self.assertEqual(len(started), 1)
            self.assertIsNotNone(started[0].poll(), 'the program the wrapper started is stopped, not left running')
            self.assertIn('interrupted', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))])
            self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'and the lock is released')
        finally:
            for p in started:
                if p.poll() is None:
                    p.kill()
                    p.wait()

    def test_the_signals_are_not_left_blocked_when_the_call_that_blocks_them_fails_and_a_program_started_after_it_is_stopped(self):
        before = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        real = signal.pthread_sigmask
        self.set_program(HANG_PROGRAM)
        d = self.register()
        spawned = []

        def blocks_then_fails(how, mask):
            old = real(how, mask)
            if how == signal.SIG_BLOCK and mask:
                raise OSError('the signals were blocked, and then the call failed')
            return old
        with mock.patch.object(sr.signal, 'pthread_sigmask', blocks_then_fails):
            with self.assertRaises(OSError):
                self.cli('--dir', d, deck=False, spawn=lambda *a: spawned.append(a))
        self.assertEqual(real(signal.SIG_BLOCK, ()), before, 'the signals are not left blocked')
        self.assertEqual(spawned, [], 'and no program was started')
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'the lock is released')
        started = []

        def spawn(cmd, env, logfile):
            started.append(sr.default_spawn(cmd, env, logfile))
            return started[-1]

        def cannot_note(proc):
            if proc is not None:
                raise RuntimeError('the program was started, and then something failed')
        try:
            with mock.patch.object(sr, 'note_program', cannot_note):
                with self.assertRaises(RuntimeError):
                    self.cli('--dir', d, '--max-games', '2', deck=False, spawn=spawn)
            self.assertEqual(real(signal.SIG_BLOCK, ()), before, 'the signals are let in again')
            self.assertEqual(len(started), 1)
            self.assertIsNotNone(started[0].poll(), 'a program that was started and then failed is not left running')
            self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')), 'and the lock is released')
        finally:
            for p in started:
                if p.poll() is None:
                    p.kill()
                    p.wait()

    def has_ended(self, pid):
        """Whether the process no longer runs (a zombie that waits to be collected has ended too, and its descriptors, the lock among them, are closed)."""
        try:
            with open(f'/proc/{pid}/stat') as f:
                return f.read().rsplit(')', 1)[1].split()[0] == 'Z'
        except OSError:
            return True

    def test_a_second_wrapper_is_refused_after_the_first_was_killed_and_is_told_which_group_stops_the_program(self):
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')
        cmd = [sys.executable, '-B', os.path.join(HERE, 'slow_report.py'), '--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'off', '--poll-s', '1']
        wrapper = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda w=wrapper: w.poll() is None and w.kill())
        hanging = os.path.join(d, 'hanging.flag')
        deadline = time.time() + 40
        while not os.path.exists(hanging) and time.time() < deadline:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(hanging), 'the program never started a game')
        child_pid = int(read(hanging))
        self.addCleanup(lambda: not self.has_ended(child_pid) and os.kill(child_pid, signal.SIGKILL))
        wrapper.kill()  # SIGKILL: no cleanup runs
        wrapper.wait(timeout=20)
        self.assertFalse(self.has_ended(child_pid), 'the program outlives a wrapper killed with SIGKILL')
        lock = os.path.join(d, 'slow_report.lock')
        note = sr.read_lock_info(lock)
        self.assertEqual((note['pid'], note['program_pgid']), (wrapper.pid, child_pid), 'the note names the wrapper and the group of the program it started')
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertTrue(str(code).startswith(f'{HEADLINE_START}my-list v km3 on the public panel] REFUSED: another slow_report.py (pid {wrapper.pid}, started {note["started"]}) '
                                             f'or the program it started is already running {d}; '), code)
        self.assertTrue(str(code).endswith(f'or you stop it (kill -TERM -{child_pid}).'), code)
        self.assertEqual(len(jsonl(os.path.join(d, 'fake_calls.jsonl'))), 1, 'the refused wrapper started no second program')
        self.assertFalse(os.path.exists(os.path.join(d, 'SLOW_REPORT.md')), 'and wrote no page into the run of the one that is still playing')
        pgid = int(re.search(r'kill -TERM -(\d+)', str(code)).group(1))
        self.assertEqual(pgid, child_pid)
        self.assertNotEqual(pgid, os.getpgrp(), 'the group in the message is the program\'s own, never the one holding the person who reads it')
        os.killpg(pgid, signal.SIGTERM)  # exactly what the message says to do
        deadline = time.time() + 20
        while not self.has_ended(child_pid) and time.time() < deadline:
            time.sleep(0.05)
        self.assertTrue(self.has_ended(child_pid), 'the program stopped when asked')
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertEqual(len(jsonl(os.path.join(d, 'games.jsonl'))), 32)
        self.assertFalse(os.path.exists(lock), 'the lock file of the next run is removed at its end')

    def test_a_wrapper_that_leaves_while_its_program_plays_on_keeps_the_lock_file_and_the_next_wrapper_is_refused_until_it_ends(self):
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')
        before = list(sr._PROGRAMS)
        self.addCleanup(lambda: sr._PROGRAMS.__setitem__(slice(None), before))
        procs = []

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            procs.append(p)
            self.addCleanup(lambda: p.poll() is None and os.killpg(p.pid, signal.SIGKILL))
            return p
        n, hanging = [0], os.path.join(d, 'hanging.flag')

        def sleep(s):
            n[0] += 1
            if n[0] == 3:
                deadline = time.time() + 20
                while not os.path.exists(hanging) and time.time() < deadline:
                    time.sleep(0.02)
                raise KeyboardInterrupt
            time.sleep(0.05)
        with mock.patch.object(sr, 'stop_group', lambda proc, grace_s=30: None):  # a program that ignores the stop
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(KeyboardInterrupt):
                    sr.main(self.argv('--dir', d, deck=False), now=self.clock.now, sleep=sleep, spawn=spawn, deck_check=lambda p, r: [])
        self.assertTrue(os.path.exists(hanging), 'the program was in the middle of a game')
        self.assertEqual(len(procs), 1)
        self.assertIsNone(procs[0].poll(), 'the program is still running')
        lock = os.path.join(d, 'slow_report.lock')
        self.assertTrue(os.path.exists(lock), 'the lock file was left, because a program the wrapper started is still running')
        self.assertEqual(sr.read_lock_info(lock)['program_pgid'], procs[0].pid)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertIn('already running', str(code))
        self.assertTrue(str(code).endswith(f'(kill -TERM -{procs[0].pid}).'), code)
        os.killpg(procs[0].pid, signal.SIGTERM)
        procs[0].wait(timeout=20)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertEqual(code, 0, err + out)
        self.assertFalse(os.path.exists(lock), 'once the program has ended, the next run removes the file again')
        self.assertEqual(sr._PROGRAMS, before)

    def test_an_ignored_sighup_stays_ignored_and_a_normal_one_is_caught_and_restored(self):
        old = signal.signal(signal.SIGHUP, signal.SIG_IGN)  # what `nohup` does before it starts the program
        try:
            with sr.signals_stop_the_program():
                self.assertEqual(signal.getsignal(signal.SIGHUP), signal.SIG_IGN)
                self.assertEqual(signal.getsignal(signal.SIGTERM), sr.signals_stop_the_program.handler)
            self.assertEqual(signal.getsignal(signal.SIGHUP), signal.SIG_IGN)
            signal.signal(signal.SIGHUP, signal.SIG_DFL)
            with sr.signals_stop_the_program():
                self.assertEqual(signal.getsignal(signal.SIGHUP), sr.signals_stop_the_program.handler)
            self.assertEqual(signal.getsignal(signal.SIGHUP), signal.SIG_DFL)
        finally:
            signal.signal(signal.SIGHUP, old)

    def test_a_wrapper_started_under_nohup_survives_the_terminal_closing(self):
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')
        cmd = [sys.executable, '-B', os.path.join(HERE, 'slow_report.py'), '--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'off', '--poll-s', '1']
        wrapper = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=lambda: signal.signal(signal.SIGHUP, signal.SIG_IGN))
        self.addCleanup(lambda w=wrapper: w.poll() is None and w.kill())
        hanging = os.path.join(d, 'hanging.flag')
        deadline = time.time() + 40
        while not os.path.exists(hanging) and time.time() < deadline:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(hanging), 'the program never started a game')
        child_pid = int(read(hanging))
        wrapper.send_signal(signal.SIGHUP)
        time.sleep(1.5)
        self.assertIsNone(wrapper.poll(), 'the wrapper must keep running when SIGHUP was ignored at launch')
        self.assertTrue(self.alive(child_pid))
        wrapper.send_signal(signal.SIGTERM)  # a real stop still works
        wrapper.wait(timeout=40)
        time.sleep(0.2)
        self.assertFalse(self.alive(child_pid))

    def test_the_lock_is_released_when_the_run_fails(self):
        self.set_program("#!/usr/bin/env python3\nimport sys\nsys.exit(3)\n")
        code, out, err = self.cli('--deals', '1')
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(os.path.join(self.rundir(), 'slow_report.lock')))

    def test_an_interrupt_stops_the_program_and_is_logged(self):
        d = self.register()
        write(os.path.join(d, 'hang.flag'), '0')  # the first game never finishes
        procs, n = [], [0]

        def spawn(cmd, env, logfile):
            p = sr.default_spawn(cmd, env, logfile)
            procs.append(p)
            return p

        def sleep(s):
            n[0] += 1
            if n[0] == 3:
                raise KeyboardInterrupt
            time.sleep(0.05)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                sr.main(self.argv('--dir', d, deck=False), now=self.clock.now, sleep=sleep, spawn=spawn, deck_check=lambda p, r: [])
        self.assertEqual(len(procs), 1)
        self.assertIsNotNone(procs[0].poll(), 'the program must not be left running')
        self.assertIn('interrupted', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))])
        self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))

    def alive(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False

    def test_sigterm_and_sighup_to_the_wrapper_stop_the_program_too(self):
        for sig in (signal.SIGTERM, signal.SIGHUP):
            with self.subTest(sig=sig.name):
                self.make()
                d = self.register()
                write(os.path.join(d, 'hang.flag'), '0')
                cmd = [sys.executable, '-B', os.path.join(HERE, 'slow_report.py'), '--dir', d, '--repo', self.repo, '--pin', self.pin_path, '--school-rule', 'off', '--poll-s', '1']
                wrapper = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.addCleanup(lambda w=wrapper: w.poll() is None and w.kill())
                hanging = os.path.join(d, 'hanging.flag')
                deadline = time.time() + 40
                while not os.path.exists(hanging) and time.time() < deadline:
                    time.sleep(0.05)
                self.assertTrue(os.path.exists(hanging), 'the program never started a game')
                child_pid = int(read(hanging))
                self.assertTrue(self.alive(child_pid))
                wrapper.send_signal(sig)
                wrapper.wait(timeout=40)
                time.sleep(0.2)
                self.assertFalse(self.alive(child_pid), 'the program must not outlive the wrapper')
                self.assertIn('interrupted', [e['event'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))])
                self.assertFalse(os.path.exists(os.path.join(d, 'slow_report.lock')))


# ---------------------------------------------------------------------------------------------------------- the page
def synth_run(tmp, deals=2, paired=True, stage='use', win=None, ref_win=None, errors=None, threads=2, complete=True, headline=None, deck='my-list', run_log='closed',
              selfcheck_source=None, pilot='kx3', ref='km3'):
    """A registered run directory with synthetic games. win(opp_index, deal, seat) -> 'deck' | 'tie' | 'opp' for arm X; ref_win likewise for arm ref."""
    win = win or (lambda o, d, s: 'deck' if (o + d + s) % 2 == 0 else 'opp')
    ref_win = ref_win or (lambda o, d, s: 'opp' if (o + d + s) % 3 else 'deck')
    headline = headline or f'{pilot} (d513e37b) on {deck} v {ref} on the public panel'
    man = dict(name=f'slow_report_{deck}', stage=stage, pilot=pilot, reference=ref, created_at='2026-10-10T10:00:00Z', threads=threads, deals=deals, seats=[0, 1],
               seed_base=24_601_000_000, pair_stride=10_000, planned_games=8 * deals * 2 * 2, planned_pairs=8,
               decks=[dict(name=deck, path=f'decks/events/{deck}.txt', sha256='c' * 64)], opponents=[dict(name=n, path=f'decks/screen/opponents/{n}.txt', sha256='d' * 64) for n in PANEL],
               program='/home/dacz8976/kx/strength', program_sha256='5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2',
               selfcheck={'kx3': 'selfcheck pilot=kx3 digest=31d638dbc818b0fa', 'km3': 'selfcheck pilot=km3 digest=81b572198c04d5d1'},
               engine='claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec', repo_commit='abc123',
               slow_report=dict(version=1, headline=headline, deck_name=deck, deck_file=f'decks/events/{deck}.txt', deck_file_sha256='c' * 64, deck_file_state='committed',
                                deals=deals, paired=paired, pin=dict(path='rl/strength/slow_report_pin.json', sha256='e' * 64),
                                pilot_label=f'{pilot} (d513e37b)', reference_label=ref, panel_label='the public panel', scrub_env_prefixes=['KX_'],
                                expected_hours=dict(typical_low=0.1, typical_high=0.2, wall=0.5)))
    if selfcheck_source:
        man['selfcheck_source'] = selfcheck_source
    rewrite_manifest(tmp, man)
    games = []
    for oi, opp in enumerate(PANEL):
        for deal in range(deals):
            for seat in (0, 1):
                for arm in ('ref', 'X'):
                    w = (win if arm == 'X' else ref_win)(oi, deal, seat)
                    games.append(dict(key=f'{deck}|{opp}|{deal}|{seat}|{arm}', deck=deck, opp=opp, deal=deal, seat=seat, arm=arm, seed=24_601_000_000 + oi * 10_000 + deal,
                                      pilot_deck=pilot if arm == 'X' else ref, pilot_opp=ref, first='deck' if seat == 0 else 'opp', winner=w, points=[3, 1], turns=9, plies=40,
                                      wall_s=200.0 if arm == 'X' else 1.0, moves_deck=dict(n=2, total_s=0.02, ms=[10.0, 10.0]), moves_opp=dict(n=1, total_s=0.01, ms=[10.0]),
                                      started_at='2026-10-10T10:05:00Z'))
    if not complete:
        games = games[: len(games) // 2]
    write(os.path.join(tmp, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games))
    for k, (key, msg) in enumerate(errors or []):
        with open(os.path.join(tmp, 'errors.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(key=key, error=msg, at='2026-10-10T11:00:00Z')) + '\n')
    if run_log == 'closed':
        write(os.path.join(tmp, 'run_log.jsonl'), json.dumps(dict(event='start', at='2026-10-10T10:00:00Z', threads=threads)) + '\n'
              + json.dumps(dict(event='stop', at='2026-10-10T12:00:00Z', played=len(games), elapsed_s=7200.0)) + '\n')
    elif run_log == 'unclosed':
        write(os.path.join(tmp, 'run_log.jsonl'), json.dumps(dict(event='start', at='2026-10-10T10:00:00Z', threads=threads)) + '\n')
    return man, games


def rewrite_manifest(tmp, man):
    """Write a manifest AND its matching sha256, so that only the change under test differs."""
    write(os.path.join(tmp, 'manifest.json'), json.dumps(man, indent=1))
    write(os.path.join(tmp, 'manifest.sha256'), hashlib.sha256(read(os.path.join(tmp, 'manifest.json')).encode()).hexdigest() + '  manifest.json\n')


def wilson95(scores):
    """The reference arithmetic, written independently of the code under test: Wilson score interval on the mean score, clipped to [0, 1]."""
    n = len(scores)
    k = sum(scores)
    p = k / n
    z = 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def pc(x):
    return f'{100 * x:.1f}%'


SC = {'deck': 1.0, 'tie': 0.5, 'opp': 0.0}


def x_scores(games, key=lambda g: True):
    return [SC[g['winner']] for g in games if g['arm'] == 'X' and key(g)]


class TCrit(Timed):
    def test_the_two_sided_95_percent_t_values(self):
        for df, want in ((1, 12.706), (2, 4.303), (5, 2.571), (10, 2.228), (30, 2.042)):
            self.assertAlmostEqual(sr.t_crit(df), want, places=3, msg=df)
        for df, want in ((47, 2.0117), (60, 2.0003), (120, 1.9799), (1000, 1.9623)):
            self.assertAlmostEqual(sr.t_crit(df), want, delta=0.006, msg=df)


class Page(Timed):
    def build(self, **kw):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, **kw)
        return t, man, games, sr.write_slow_report(t)

    def test_the_page_is_written_beside_the_run_and_names_both_pilots_first(self):
        t, man, games, text = self.build()
        self.assertEqual(read(os.path.join(t, 'SLOW_REPORT.md')), text)
        self.assertTrue(text.startswith('# Slow report: my-list'))
        self.assertIn('**kx3 (d513e37b) on my-list v km3 on the public panel**', '\n'.join(text.splitlines()[:6]))
        self.assertIn('Stage `use`', text)
        self.assertIn('not development evidence', text)

    def test_the_overall_score_is_the_mean_and_the_range_is_wilson(self):
        for deals in (1, 3, 5):
            t, man, games, text = self.build(deals=deals)
            p, lo, hi = wilson95(x_scores(games))
            self.assertIn(pc(p), text)
            self.assertIn(f'probably between {pc(lo)} and {pc(hi)}', text)
            self.assertIn(f'(95% interval; this range refers to these {8 * deals * 2} kx3 games)', text)
            self.assertNotIn('give or take about', text, 'a Wilson range is not symmetric, so it is not given as give-or-take')
            self.assertIn(f'{8 * deals * 2} games', text)
            self.assertIn(f'{deals} deal' + ('' if deals == 1 else 's') + ' x 2 seats', text)

    def test_ties_count_half_and_the_numbers_show_it(self):
        t, man, games, text = self.build(deals=2, win=lambda o, d, s: 'tie' if (o + d + s) % 2 == 0 else 'deck')
        sc = x_scores(games)
        self.assertEqual(set(sc), {0.5, 1.0})
        p, lo, hi = wilson95(sc)
        self.assertIn(pc(p), text)  # 75.0%
        self.assertEqual(pc(p), '75.0%')
        self.assertIn(f'probably between {pc(lo)} and {pc(hi)}', text)
        t2, m2, g2, text2 = self.build(deals=2, win=lambda o, d, s: 'tie')
        self.assertIn('50.0%', text2)

    def test_a_unanimous_result_never_prints_a_zero_width_or_a_range_past_100(self):
        for result, label in (('deck', '100.0%'), ('opp', '0.0%')):
            t, man, games, text = self.build(deals=5, win=lambda o, d, s, r=result: r)
            p, lo, hi = wilson95(x_scores(games))
            self.assertIn(f'probably between {pc(lo)} and {pc(hi)}', text)
            self.assertNotIn('give or take about 0.0 points', text)
            self.assertIn(f'| t-altaria | 10 | {label} | {pc(wilson95([SC[result]] * 10)[1])} to {pc(wilson95([SC[result]] * 10)[2])} |', text)
            for m in re.finditer(r'(-?\d+\.\d)%', text):
                self.assertTrue(0.0 <= float(m.group(1)) <= 100.0, m.group(0))
            self.assertNotIn('-0.0%', text)
        t, man, games, text = self.build(deals=5, win=lambda o, d, s: 'deck')
        self.assertIn('| t-altaria | 10 | 100.0% | 72.2% to 100.0% |', text)

    def test_every_opponent_has_a_row_with_its_own_games_score_and_range(self):
        t, man, games, text = self.build(deals=2)
        for opp in PANEL:
            s = x_scores(games, lambda g, o=opp: g['opp'] == o)
            p, lo, hi = wilson95(s)
            row = [l for l in text.splitlines() if l.startswith(f'| {opp} ')]
            self.assertEqual(len(row), 1, opp)
            self.assertEqual(row[0], f'| {opp} | 4 | {pc(p)} | {pc(lo)} to {pc(hi)} |')

    def test_with_paired_it_reports_the_gain_over_km3_on_the_same_deals(self):
        t, man, games, text = self.build(deals=3, paired=True)
        by = {}
        for g in games:
            by.setdefault((g['opp'], g['deal'], g['seat']), {})[g['arm']] = SC[g['winner']]
        d = [v['X'] - v['ref'] for v in by.values()]
        n, m, sd = len(d), statistics.mean(d), statistics.stdev(d)
        half = sr.t_crit(n - 1) * sd / n ** 0.5
        self.assertIn('### How much better kx3 plays this deck than km3', text)
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertIn('On the same deals', sec)
        self.assertIn(f'{100 * m:+.1f} points', sec)
        lo, hi = m - half, m + half
        self.assertIn(f'probably between {100 * lo:+.1f} and {100 * hi:+.1f} points (95% interval; this range refers to those {n} paired games).', sec)
        self.assertNotIn('give or take', sec, 'the t range is not symmetric once it is cut at the scale, so it is never given as give-or-take')
        self.assertIn('km3 on this deck', sec)
        self.assertIn(f'over {n} paired games: each a deal and seat played by both pilots, so {n} kx3 games + {n} cheap km3 baseline games)', sec)
        self.assertNotIn('played both ways', sec, 'the gain is counted in paired games now')
        self.assertNotIn('That range runs', sec, 'the note under the range does not repeat its numbers')
        if lo <= 0 <= hi:
            self.assertIn('That range includes no gain at all', sec)
            self.assertIn(f'these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse', sec)
        else:
            self.assertIn('That range does not include no gain', sec)

    def test_a_gain_with_no_spread_is_not_dressed_up_as_certain(self):
        t, man, games, text = self.build(deals=3, paired=True, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertNotIn('give or take', sec)
        self.assertNotIn('probably between', sec, 'with no spread there is no range to print')
        self.assertNotIn('That range', sec)
        self.assertIn('every one of the 48 comparisons', sec)
        self.assertIn('+0.0 points', sec)

    def test_seconds_are_shown_to_a_tenth_below_ten_and_whole_above(self):
        self.assertEqual((sr.fmt_s(0.4), sr.fmt_s(9.96), sr.fmt_s(10.2), sr.fmt_s(255.0)), ('0.4 s', '10.0 s', '10 s', '255 s'))

    def test_a_tiny_negative_gain_prints_as_zero_not_minus_zero(self):
        self.assertEqual(sr.signed_points(-0.00001), '+0.0')
        self.assertEqual(sr.signed_points(0.0), '+0.0')
        self.assertEqual(sr.signed_points(-0.062), '-6.2')
        self.assertEqual(sr.signed_points(0.062), '+6.2')

    def test_without_paired_the_page_does_not_report_the_gain(self):
        t, man, games, text = self.build(deals=3, paired=False)
        for s in ('same deals', 'km3 on this deck', 'How much better', 'played both ways', 'paired game', 'That range'):
            self.assertNotIn(s, text)

    def test_who_went_first_is_split_out_with_ranges_and_a_caution(self):
        t, man, games, text = self.build(deals=2)
        for which, label in (('deck', 'went first'), ('opp', 'went second')):
            s = x_scores(games, lambda g, w=which: g['first'] == w)
            p, lo, hi = wilson95(s)
            self.assertIn(f'When my-list {label}: {pc(p)} over {len(s)} games ({pc(lo)} to {pc(hi)})', text)
        self.assertIn('Each range refers only to the kx3 games on its line', text.split('## Who went first')[1].split('\n## ')[0])

    def test_the_time_lines_use_distinct_numbers_and_the_run_log(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=2, threads=2)
        for i, g in enumerate([g for g in games if g['arm'] == 'X']):
            g['wall_s'] = 100.0 + i * 10.0  # 100 .. 410: mean 255, median 255, max 410
        for g in games:
            if g['arm'] == 'ref':
                g['wall_s'] = 1.5
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games))
        text = sr.write_slow_report(t)
        sec = text.split('## The time it took')[1].split('\n## ')[0]
        self.assertIn('kx3 took 255 s a game on average (about 4 min)', sec)
        self.assertIn('median 255 s', sec)
        self.assertIn('slowest 410 s', sec)
        self.assertIn('2 threads', sec)
        self.assertIn('km3 playing this deck took 1.5 s a game', sec)
        self.assertIn('2.0 h over 1 sitting', sec)

    def test_a_sitting_that_did_not_close_falls_back_to_an_estimate_and_says_why(self):
        t, man, games, text = self.build(deals=2, run_log='unclosed')
        sec = text.split('## The time it took')[1].split('\n## ')[0]
        total = sum(g['wall_s'] for g in games) / 2
        self.assertIn(f'estimated from the game times and the thread count: {sr.human_time(total)}', sec)
        self.assertIn('did not close', sec)
        t2, m2, g2, text2 = self.build(deals=2, run_log='none')
        sec2 = text2.split('## The time it took')[1].split('\n## ')[0]
        self.assertIn('no run log', sec2)
        self.assertNotIn('did not close', sec2)

    def test_the_thread_count_comes_from_what_each_sitting_used(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=1, threads=2)
        write(os.path.join(t, 'run_log.jsonl'), '\n'.join(json.dumps(e) for e in (
            dict(event='start', at='2026-10-10T10:00:00Z', threads=2), dict(event='stop', at='2026-10-10T11:00:00Z', played=5, elapsed_s=3600.0),
            dict(event='start', at='2026-10-10T12:00:00Z', threads=3), dict(event='stop', at='2026-10-10T13:00:00Z', played=5, elapsed_s=3600.0))) + '\n')
        text = sr.write_slow_report(t)
        self.assertIn('2 and 3 threads', text)
        self.assertIn('over 2 sittings', text)

    def test_the_can_and_cannot_say_section_is_one_plain_sentence_and_then_the_details(self):
        t, man, games, text = self.build()
        section = text.split("## What these numbers can and can't say")[1].split('\n## ')[0].strip()
        first = section.splitlines()[0]
        self.assertTrue(first.startswith('**') and first.endswith('**'))
        self.assertEqual(first.count('. '), 0, 'one sentence')
        for needle in ('no pass or fail', 'not a ranking', 'public'):
            self.assertIn(needle, first)
        for needle in ('simulated', 'knowing its own cards', 'optimistic', 'ladder', 'count equally', 'luck of the shuffles', 'a call for the player'):
            self.assertIn(needle, section)
        self.assertNotIn('never told', section)
        self.assertNotIn('within the noise', text, 'a wide range is explained, never waved away')
        _p, _lo, _hi = wilson95(x_scores(games))
        width = f'{float(pc(_hi)[:-1]) - float(pc(_lo)[:-1]):.1f} points here'  # (from the two ends as printed)
        self.assertIn('It can tell whether kx3 plays my-list clearly above or clearly below an even score against these 8 lists', section)
        self.assertIn(f'it cannot tell two decks apart whose scores differ by less than the width of such a range ({width}), and more deals narrow it', section)

    def test_no_cutoff_or_verdict_words_anywhere_on_the_page(self):
        for paired in (True, False):
            t, man, games, text = self.build(deals=2, paired=paired)
            scrubbed = re.sub(r'no pass or fail|not a ranking', '', text)
            for bad in (r'\bPASS\b', r'\bFAIL\b', r'\bpass(es|ed)?\b', r'\bfail(s|ed|ure)?\b', r'\bclears?\b', r'borderline', r'verdict', r'\bfloor\b', r'cutoff', r'\bbar of\b',
                        r'good enough', r'\branking\b', r'\bthreshold\b'):
                self.assertIsNone(re.search(bad, scrubbed, re.I if bad.islower() or bad.startswith(r'\bpass') or bad.startswith(r'\bfail') else 0), bad)

    def test_the_question_comes_first_then_the_size_then_any_number(self):
        t, man, games, text = self.build(deals=2)
        sec = text.split('## What it says')[1].split('\n## ')[0]
        q = sec.index('Question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?')
        s = sec.index('Size: 32 kx3 games + 32 cheap km3 baseline games (2 deals x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck).')
        first_number = re.search(r'\d+\.\d%', sec).start()
        self.assertLess(q, s)
        self.assertLess(s, first_number, 'no result is quoted before the size')
        t, man, games, text = self.build(deals=2, paired=False)
        sec = text.split('## What it says')[1].split('\n## ')[0]
        self.assertIn('Question: how does my-list do when kx3 plays it against the 8 public lists?', sec)
        self.assertIn('Size: 32 kx3 games (2 deals x 2 seats against each of the 8 public lists).', sec)
        self.assertNotIn('baseline', sec)

    def test_every_interval_says_which_games_it_refers_to(self):
        t, man, games, text = self.build(deals=3)
        self.assertIn('this range refers to these 48 kx3 games', text)
        self.assertIn('this range refers to those 48 paired games', text)
        self.assertIn("Each row's range refers only to the kx3 games against that list", text)
        self.assertIn('Each range refers only to the kx3 games on its line', text)
        self.assertNotIn('give or take', text)

    def test_a_gain_range_that_excludes_zero_says_so_and_does_not_overreach(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', ref_win=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertIn('That range does not include no gain', sec)
        self.assertIn('on these 48 paired games kx3 did better than km3', sec)
        self.assertNotIn('includes no gain at all', sec)
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'opp' if (o + d) % 5 else 'deck', ref_win=lambda o, d, s: 'deck' if (o + d + s) % 4 else 'opp')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertIn('That range does not include no gain', sec)
        self.assertIn('on these 48 paired games kx3 did worse than km3', sec)

    def test_a_partial_run_says_so_near_the_top_and_describes_what_it_has(self):
        t, man, games, text = self.build(deals=2, complete=False)
        self.assertIn('PARTIAL', '\n'.join(text.splitlines()[:10]))
        self.assertRegex(text, r'\d+ of the 64 games planned')
        sec = text.split('## What it says')[1].split('\n## ')[0]
        self.assertLess(sec.index('Question: '), sec.index('PARTIAL'), 'the question first')
        self.assertLess(sec.index('PARTIAL'), sec.index('Size: '), 'then the banner, then the size')
        shape = [l for l in sec.splitlines() if 'scored' in l][0]
        self.assertNotIn('against each of the 8 public lists', shape)
        self.assertRegex(shape, r'games from \d of the 8 public lists so far')
        self.assertRegex(sec, r'Size: \d+ kx3 games \+ \d+ cheap km3 baseline games so far, of 32 kx3 games \+ 32 cheap km3 baseline games planned\.')

    def test_a_partial_run_with_an_incomplete_pair_or_a_missing_arm_still_reads_cleanly(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=2, paired=True)
        keep = [g for g in games if not (g['arm'] == 'ref' and g['opp'] in PANEL[:3])]  # no km3 games for three lists
        keep = [g for g in keep if not (g['arm'] == 'X' and g['opp'] == PANEL[7] and g['deal'] == 1)]  # a hole on the X side
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in keep))
        text = sr.write_slow_report(t)
        self.assertIn('PARTIAL', text)
        nx, nr = sum(1 for g in keep if g['arm'] == 'X'), sum(1 for g in keep if g['arm'] == 'ref')
        self.assertIn(f"**PARTIAL: {nx} kx3 games + {nr} cheap km3 baseline games so far ({len(keep)} of the 64 games planned; both pilots' games count in the 64). ", text)
        both = {(g['opp'], g['deal'], g['seat']) for g in keep if g['arm'] == 'X'} & {(g['opp'], g['deal'], g['seat']) for g in keep if g['arm'] == 'ref'}
        self.assertIn(f'over {len(both)} paired games: each a deal and seat played by both pilots, so {len(both)} kx3 games + {len(both)} cheap km3 baseline games)', text)
        self.assertNotIn('nan', text.lower())
        self.assertNotIn('None', text)

    def test_only_km3_games_so_far_says_so_without_inventing_numbers(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=1)
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games if g['arm'] == 'ref'))
        text = sr.write_slow_report(t)
        self.assertIn('No kx3 game has finished yet', text)
        sec = text.split("## What these numbers can and can't say")[1]
        self.assertIn('nothing to say yet', sec.lower())
        self.assertNotIn('over 0 games', text)

    def test_a_single_game_gets_a_wide_honest_range(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=1)
        keep = [g for g in games if g['opp'] == PANEL[0] and g['seat'] == 0]
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in keep))
        text = sr.write_slow_report(t)
        p, lo, hi = wilson95(x_scores(keep))
        self.assertIn('1 game', text)
        self.assertIn(f'probably between {pc(lo)} and {pc(hi)}', text)
        self.assertNotIn('nan', text.lower())

    def test_errors_are_counted_by_game_and_described_honestly(self):
        errs = [('my-list|t-altaria|0|0|X', 'panic: boom')] * 3 + [('my-list|t-blaziken|0|0|X', 'panic: flaky')]
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=2, errors=errs)
        # the first game is not in games.jsonl (it kept failing); the second was played on a later try, so it is in games.jsonl already
        keep = [g for g in games if g['key'] != 'my-list|t-altaria|0|0|X']
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in keep))
        text = sr.write_slow_report(t)
        self.assertIn('1 game could not be finished and is left out of every number', text)
        self.assertIn('my-list|t-altaria|0|0|X', text)
        self.assertIn('panic: boom', text)
        self.assertNotIn('flaky', text)
        self.assertIn('failed every time it was tried', text)
        self.assertIn('leans towards games without it', text)

    def test_an_error_seen_once_is_described_as_worth_a_retry(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=2, errors=[('my-list|t-altaria|0|0|X', 'panic: once')])
        write(os.path.join(t, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games if g['key'] != 'my-list|t-altaria|0|0|X'))
        text = sr.write_slow_report(t)
        self.assertIn('A resumed run tries it again', text)
        self.assertNotIn('every time it was tried', text)

    def test_torn_and_duplicate_lines_are_tolerated_everywhere(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, deals=2, errors=[('my-list|t-altaria|0|0|X', 'panic: boom')], run_log='closed')
        with open(os.path.join(t, 'games.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(games[0]) + '\n')  # a duplicate of the first game
            f.write('{"key": "my-list|t-weezing|1|1|X", "deck": "my-')  # torn by the 6:30 kill
        for n in ('errors.jsonl', 'run_log.jsonl'):
            with open(os.path.join(t, n), 'a', encoding='utf-8') as f:
                f.write('{"event": "sta')
        text = sr.write_slow_report(t)
        self.assertIn('32 games', text, 'the duplicate is not counted twice and the torn line is not counted at all')

    def test_the_self_check_lines_say_how_the_text_was_obtained(self):
        for source, want in (('given in the config (copied from the pin, which says it was measured on this exact program sha256)',
                              'copied from the pin, not replayed: the pin says it was measured on this exact binary'),
                             ('replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)',
                              'replayed on the registering machine just before registration, equal to the committed pin'),
                             ('run by strength_prereg.py', 'replayed at registration')):
            t = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, t, True)
            man, games = synth_run(t, selfcheck_source={'kx3': source, 'km3': source})
            man['slow_report']['pin_committed'] = 'yes'  # (a replay is said to be equal to the committed pin only of a pin recorded as committed)
            rewrite_manifest(t, man)
            text = sr.write_slow_report(t)
            self.assertIn(f'Self-check of `kx3`: `selfcheck pilot=kx3 digest=31d638dbc818b0fa` ({want})', text)
        t, man, games, text = self.build()
        self.assertIn('recorded at registration', text)

    def test_provenance_is_on_the_page(self):
        t, man, games, text = self.build()
        for needle in ('5a8f5c83a791', 'digest=31d638dbc818b0fa', 'digest=81b572198c04d5d1', 'decks/events/my-list.txt', 'cccccccccccc', 'committed', 'abc123', '24601000000',
                       'rl/strength/slow_report_pin.json', 'claude/playout-pilot d513e37b'):
            self.assertIn(needle, text)

    def test_a_not_committed_deck_is_flagged(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t)
        man['slow_report']['deck_file_state'] = 'not committed'
        rewrite_manifest(t, man)
        self.assertIn('not committed', sr.write_slow_report(t))

    def test_the_page_refuses_a_run_that_is_not_a_slow_report_or_whose_manifest_changed(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t)
        copy = dict(man)
        del copy['slow_report']
        rewrite_manifest(t, copy)
        with self.assertRaises(SystemExit) as cm:
            sr.write_slow_report(t)
        self.assertIn('slow report', str(cm.exception.code))
        write(os.path.join(t, 'manifest.json'), json.dumps(dict(man, deals=99), indent=1))  # sha256 left as registered
        with self.assertRaises(SystemExit) as cm:
            sr.write_slow_report(t)
        self.assertIn('registered', str(cm.exception.code))
        self.assertFalse(os.path.exists(os.path.join(t, 'SLOW_REPORT.md')))

    def test_a_held_out_deck_is_noted_as_used_not_unlocked(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t)
        man['heldout_in_run'] = ['my-list']
        rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        self.assertIn('Held-out decks in this run: my-list', text)
        self.assertIn('not development evidence', text)

    def test_the_pilot_names_come_from_the_manifest_not_from_literals(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        man, games = synth_run(t, pilot='kz9', ref='kr1', selfcheck_source={'kz9': 'x'})
        man['selfcheck'] = {}
        rewrite_manifest(t, man)
        text = sr.write_slow_report(t)
        self.assertNotIn('kx3', text)
        self.assertNotIn('km3', text)
        self.assertIn('kz9', text)
        self.assertIn('kr1', text)

    def test_the_deck_is_called_your_deck_and_the_panel_the_public_lists(self):
        t, man, games, text = self.build()
        self.assertNotIn('this list', text)
        self.assertIn('## Against each public list', text)
        self.assertIn('| opponent (km3) | kx3 games | score | 95% range |', text)
        self.assertIn("Each row's range refers only to the kx3 games against that list", text)

    def test_one_deal_is_not_pluralised(self):
        t, man, games, text = self.build(deals=1)
        self.assertIn('(1 deal x 2 seats against each of the 8 public lists)', text)
        self.assertNotIn('1 deals', text)

    def test_the_interval_is_said_to_cover_only_the_luck_of_the_deals(self):
        t, man, games, text = self.build()
        self.assertIn('luck of the shuffles and coin flips in these', text)

    def test_the_page_name_and_the_manifest_pilots_match_even_with_markdown_characters_in_the_deck_name(self):
        t, man, games, text = self.build(deck='a_b-c.d')
        self.assertIn('# Slow report: a_b-c.d', text)


# ---------------------------------------------------------------------------------------------------------- what is printed
class BothPilotsEverywhere(World):
    def test_every_line_printed_names_both_pilots(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, err)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines)
        for l in lines:
            self.assertTrue(l.startswith(HEADLINE_START + 'my-list v km3 on the public panel]'), l)

    def test_dry_run_and_register_only_lines_too(self):
        for extra in (('--dry-run',), ('--register-only',)):
            code, out, err = self.cli('--deals', '1', *extra)
            self.assertEqual(code, 0, err)
            for l in [l for l in out.splitlines() if l.strip()]:
                self.assertTrue(l.startswith(HEADLINE_START), l)
            shutil.rmtree(self.out_root, ignore_errors=True)

    def test_refusals_name_both_pilots_too(self):
        os.remove(self.program)
        code, out, err = self.cli('--deals', '1')
        self.assertTrue(str(code).startswith('[kx3 (d513e37b) v km3]'), code)
        self.make()
        code, out, err = self.cli('--deals', '1', '--threads', '0')
        self.assertTrue(str(code).startswith(HEADLINE_START + 'my-list v km3 on the public panel]'), code)

    def test_the_preregistration_the_log_and_report_json_name_both_pilots(self):
        d = self.register()
        text = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertIn('kx3 (d513e37b) on my-list v km3 on the public panel', text)
        self.assertIn('Stage `use`', text)
        self.assertIn('no pass or fail', text.lower())
        events = jsonl(os.path.join(d, 'slow_report_log.jsonl'))
        self.assertEqual([e['event'] for e in events], ['registered'], 'a registration logs one event, and it carries the pilots')
        for e in events:
            self.assertEqual((e.get('pilot'), e.get('reference')), ('kx3', 'km3'), e)
        self.assertIn('slow_report.py --dir', text.split('## Run')[1])
        self.assertNotIn('strength run --manifest', text.split('## Run')[1])

    def test_no_pass_fail_or_cutoff_words_in_anything_it_writes(self):
        self.assertEqual(self.cli('--deals', '2')[0], 0)
        d = self.rundir()
        for name in ('SLOW_REPORT.md', 'PREREGISTRATION.md', 'REPORT.md', 'config.json'):
            text = re.sub(r'no pass or fail|No pass or fail|no pass/fail|No pass/fail|not a ranking', '', read(os.path.join(d, name)))
            for bad in (r'\bpass(es|ed)?\b', r'\bfail(s|ed|ure)?\b', r'\bverdict\b', r'\bcutoff', r'\bgood enough\b'):
                self.assertIsNone(re.search(bad, text, re.I), (name, bad))

    def test_the_paired_baseline_is_on_by_default_and_off_with_no_paired(self):
        d = self.register()
        self.assertTrue(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['paired'])
        shutil.rmtree(self.out_root)
        d = self.register('--no-paired')
        self.assertFalse(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['paired'])
        self.assertFalse([e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'registered'][0]['paired'])

    def test_the_old_paired_flag_is_gone(self):
        code, out, err = self.cli('--deals', '1', '--paired')
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_console_shows_a_partial_banner_and_plain_numbers(self):
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, err)
        self.assertIn('PARTIAL', out)
        self.assertNotIn('**', out)

    def test_the_console_of_a_partial_run_gives_the_question_then_the_banner_then_the_size(self):
        code, out, err = self.cli('--deals', '2', '--max-games', '10')
        self.assertEqual(code, 0, err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        written = lines.index(f'SLOW_REPORT.md written in {self.rundir()}')
        page = lines[written + 1:]
        self.assertEqual(page[0], 'Question: how does my-list do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?')
        self.assertEqual(page[1], "PARTIAL: 5 kx3 games + 5 cheap km3 baseline games so far (10 of the 64 games planned; both pilots' games count in the 64). "
                                  'The numbers below will move; read them as a snapshot.')
        self.assertEqual(page[2], 'Size: 5 kx3 games + 5 cheap km3 baseline games so far, of 32 kx3 games + 32 cheap km3 baseline games planned.')
        self.assertTrue(page[3].startswith('my-list scored '), page[3])
        text = read(os.path.join(self.rundir(), 'SLOW_REPORT.md'))
        self.assertEqual(page, [l.replace('**', '').replace('`', '').strip() for l in text.split('## What it says')[1].split('\n## ')[0].splitlines()
                               if l.strip() and not l.startswith('#')], 'the console shows the lines of "What it says" and nothing else')

    def test_the_console_of_a_finished_run_has_the_question_and_the_size_and_no_banner(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, err)
        lines = [l.split('] ', 1)[1] for l in out.splitlines()]
        page = lines[lines.index(f'SLOW_REPORT.md written in {self.rundir()}') + 1:]
        self.assertEqual(page[0][:10], 'Question: ')
        self.assertEqual(page[1], 'Size: 16 kx3 games + 16 cheap km3 baseline games (1 deal x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck).')
        self.assertNotIn('PARTIAL', out)


class Arguments(World):
    def test_deals_must_be_between_1_and_9999(self):
        for bad in ('0', '-1', '10000', 'many'):
            code, out, err = self.cli('--deals', bad)
            self.assertNotEqual(code, 0, bad)
            self.assertFalse(os.path.exists(self.out_root), bad)

    def test_the_default_page_is_five_deals(self):
        code, out, err = self.cli('--dry-run')
        self.assertEqual(code, 0, err)
        self.assertIn('80 kx3 games', out)
        self.assertIn('5 deals', out)

    def test_a_deck_file_or_a_run_directory_is_needed(self):
        code, out, err = self.cli(deck=False)
        self.assertNotEqual(code, 0)

    def test_dates_must_be_real_iso_dates(self):
        for bad in ('2026-10-10\n', '2026-13-01', '2026-02-30', '20261010', 'today', '2026-1-1'):
            argv = self.argv('--deals', '1', '--dry-run', date=False) + ['--date', bad]
            e = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(e):
                with self.assertRaises(SystemExit, msg=repr(bad)) as cm:
                    sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
            self.assertNotEqual(cm.exception.code, 0)
            self.assertFalse(os.path.exists(self.out_root))

    def test_the_default_date_is_todays_chicago_date(self):
        self.clock = FakeClock(datetime.datetime(2026, 10, 11, 3, 0, tzinfo=datetime.timezone.utc).astimezone(CHI))  # Oct 10, 22:00 in Chicago, Oct 11 in UTC
        code, out, err = self.cli('--deals', '1', '--register-only', date=False)
        self.assertEqual(code, 0, err + out)
        self.assertTrue(os.path.isdir(self.rundir('2026-10-10_my-list')), os.listdir(self.out_root))

    def help_text(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {'COLUMNS': '10000'}), contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:  # (a wide terminal: no word is split at a line end)
            sr.main(['--help'])
        self.assertEqual(cm.exception.code, 0)
        return ' '.join(out.getvalue().split())

    def test_the_date_option_says_the_default_is_chicago_with_the_utc_date_as_the_fallback(self):
        self.assertIn('--date DATE YYYY-MM-DD for the run directory name (default: today in Chicago, or the UTC date on a machine without the time zone database)', self.help_text())

    def test_the_max_games_option_says_the_limit_counts_games_of_both_arms(self):
        self.assertIn('--max-games MAX_GAMES play at most this many games in this call (counted across both arms: about half of them kx3 games), then write the page and stop', self.help_text())

    def test_the_program_option_says_a_rebuild_needs_its_build_record_and_both_self_checks(self):
        text = self.help_text()
        for words in ('a REBUILD of the pinned build made with rl/strength/build.sh', 'it must have its build record (PROGRAM.build.json, written by build.sh) with the pinned engine tree and harness source',
                      "both self-checks are replayed on this machine and must equal the committed pin's digests (this forces --selfcheck)"):
            self.assertIn(words, text)

    def test_poll_seconds_must_be_positive(self):
        for bad in ('0', '-5'):
            argv = [x for x in self.argv('--deals', '1')]
            i = argv.index('--poll-s')
            argv[i + 1] = bad
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
            self.assertFalse(os.path.exists(self.out_root))

    def test_a_panel_list_is_refused_even_at_its_registered_path(self):
        p = os.path.join(self.repo, 'decks', 'screen', 'opponents', 't-hydreigon.txt')
        argv = [p] + self.argv(deck=False) + ['--out-root', self.out_root, '--date', '2026-10-10']
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                sr.main(argv, now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])
        self.assertIn('t-hydreigon', str(cm.exception.code))
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_default_pin_is_the_committed_one(self):
        self.assertEqual(os.path.abspath(sr.DEFAULT_PIN), os.path.join(HERE, 'slow_report_pin.json'))

    def test_a_dry_run_leaves_no_bytecode_in_the_repository(self):
        """Python writes a .pyc for each module it imports unless told not to, and an existing __pycache__ already holds the names, so a before-and-after comparison of
        names cannot fail. All bytecode is sent to an empty PYTHONPYCACHEPREFIX instead (a script that forgets sys.dont_write_bytecode fills it with the bytecode of its
        siblings; the in-tree __pycache__ is not touched at all while it is set). The interpreter's own start-up may write bytecode of site-wide modules there before
        the script's first line runs, so only the harness's own modules are looked for."""
        prefix = os.path.join(self.tmp, 'pycache')
        os.makedirs(prefix)
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONDONTWRITEBYTECODE'}
        env['PYTHONPYCACHEPREFIX'] = prefix
        script = os.path.join(HERE, 'slow_report.py')
        r = subprocess.run([sys.executable, script, '--help'], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('usage', r.stdout, 'the script really ran (and imported its siblings)')
        subprocess.run([sys.executable, script, self.deck, '--repo', self.repo, '--pin', self.pin_path, '--out-root', self.out_root, '--dry-run'], capture_output=True, text=True, env=env)
        ours = sorted(f for dp, dn, fn in os.walk(prefix) for f in fn if f.split('.')[0] in ('slow_report', 'strength_prereg', 'strength_report'))
        self.assertEqual(ours, [], 'importing the script and its siblings must not write bytecode')


if __name__ == '__main__':
    unittest.main()
