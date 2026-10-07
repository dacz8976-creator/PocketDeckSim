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
  * refusals that write nothing: an unpinned program, a bad deck, a deck outside the repository (symlinks followed), a registration that changed.
"""
import contextlib, datetime, fcntl, hashlib, io, json, math, os, re, shutil, signal, statistics, subprocess, sys, tempfile, textwrap, time, unittest, zoneinfo
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
        pin['program_sha256'] = sha(self.program)
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
        self.make()

    def set_program(self, text):
        write(self.program, text, mode=0o755)
        pin = json.loads(read(self.pin_path))
        pin['program_sha256'] = sha(self.program)
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

    def register(self, *extra):
        code, out, err = self.cli('--deals', '1', '--register-only', *extra)
        self.assertEqual(code, 0, out + err)
        return self.rundir()


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
        self.assertEqual(man['selfcheck_source']['kx3'], 'given in the config (copied from the pin; the program sha256 is the one named there)')
        games = jsonl(os.path.join(d, 'games.jsonl'))
        self.assertEqual(len(games), 64)
        self.assertEqual({g['arm'] for g in games}, {'X', 'ref'})
        self.assertEqual({g['pilot_deck'] for g in games if g['arm'] == 'X'}, {'kx3'})
        self.assertEqual({g['pilot_opp'] for g in games}, {'km3'})
        self.assertEqual(man['slow_report']['deck_file'], self.deck_rel)
        self.assertEqual(man['slow_report']['deck_file_sha256'], sha(self.deck))
        self.assertEqual(man['slow_report']['resume_command'], f'python3 rl/strength/slow_report.py --dir {d}')
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
        code, out, err = self.cli('--deals', '5', '--dry-run')
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.exists(self.out_root))
        self.assertIn('80 kx3 games', out)
        self.assertIn('hours', out)
        self.assertIn('my-list', out)
        self.assertIn('5 deals', out)
        self.assertIn('school-morning', out, 'the plan mentions that the calendar time is longer on school days')

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
        write(self.program, FAKE_PROGRAM + '\n# a rebuilt binary\n', mode=0o755)
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertNotEqual(code, 0)
        self.assertIn('not the program', str(code) + err)
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
        self.assertIn('not the program', str(code) + err)
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
        for extra in (('--deals', '3'), ('--no-paired',), ('--date', '2026-10-11'), ('--seed-base', str(BLOCK[0])), ('--selfcheck',), ('--register-only',)):
            code, out, err = self.cli('--dir', d, *extra, deck=False)
            self.assertNotEqual(code, 0, extra)
            self.assertIn('--dir', str(code) + err, extra)
            self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')), extra)

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
        self.assertIn('6 of 32', out)
        self.assertIn('26 games to go', out)
        after = {n: read(os.path.join(d, n)) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}
        self.assertEqual(before, after)

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
        for flag, left_out, stage_clause in ((None, '', 'with the comparison with km3 on the same deals in the page'),
                                             ('--no-paired', '; with --no-paired they are still played and the page leaves them out', 'without the comparison with km3 on the same deals in the page')):
            with self.subTest(flag):
                code, out, err = self.cli('--deals', '3', *([flag] if flag else []), '--dry-run')
                self.assertEqual(code, 0, out + err)
                lines = [l.split('] ', 1)[1] for l in out.splitlines()]  # without the headline that starts every line
                self.assertEqual(len(lines), 5, lines)
                self.assertEqual(lines[1], 'size: 48 kx3 games + 48 cheap km3 baseline games on the same deals (96 games in all; the km3 games take about a second each' + left_out + '); '
                                 'the time is for the 48 kx3 games: about 72 minutes to 2.4 hours if the deck plays like most of his, '
                                 'about 4.8 hours if it plays like the Wailord wall (measured with 2 games at a time)')
                self.assertTrue(lines[3].endswith(f'), {stage_clause}, no pass or fail line'), lines[3])

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
        self.assertEqual(man['selfcheck_source']['kx3'], 'replayed by slow_report.py just before registration (equal to the pin)')
        self.assertNotIn('not replayed', read(os.path.join(d, 'PREREGISTRATION.md')))

    def test_the_default_does_not_replay_the_self_check(self):
        d = self.register()
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_env.json')), 'registering must not play a single game')


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
        d = self.register()
        code, out, err = self.cli('--dir', d, school=None, spawn=spawn, deck=False)  # no --school-rule option at all
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
        self.assertIn(f'give or take {100 * half:.1f} points (95% interval; this range refers to those {n} paired games)', sec)
        self.assertIn('km3 on this deck', sec)
        self.assertIn(f'over {n} paired games: each a deal and seat played by both pilots, so {n} kx3 games + {n} cheap km3 baseline games)', sec)
        self.assertNotIn('played both ways', sec, 'the gain is counted in paired games now')
        lo, hi = m - half, m + half
        self.assertIn(f'That range runs from {100 * lo:+.1f} to {100 * hi:+.1f} points', sec)
        if lo <= 0 <= hi:
            self.assertIn('which includes no gain at all', sec)
            self.assertIn(f'these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse', sec)
        else:
            self.assertIn('which does not include no gain', sec)

    def test_a_gain_with_no_spread_is_not_dressed_up_as_certain(self):
        t, man, games, text = self.build(deals=3, paired=True, win=lambda o, d, s: 'deck', ref_win=lambda o, d, s: 'deck')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertNotIn('give or take 0.0', sec)
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
        for s in ('same deals', 'km3 on this deck', 'How much better', 'played both ways', 'paired game', 'That range runs'):
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
        width = f'{100 * (wilson95(x_scores(games))[2] - wilson95(x_scores(games))[1]):.1f} points here'
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

    def test_a_gain_range_that_excludes_zero_says_so_and_does_not_overreach(self):
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'deck' if (o + d) % 5 else 'opp', ref_win=lambda o, d, s: 'opp' if (o + d + s) % 4 else 'deck')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertIn('which does not include no gain', sec)
        self.assertIn('on these 48 paired games kx3 did better than km3', sec)
        self.assertNotIn('which includes no gain at all', sec)
        t, man, games, text = self.build(deals=3, win=lambda o, d, s: 'opp' if (o + d) % 5 else 'deck', ref_win=lambda o, d, s: 'deck' if (o + d + s) % 4 else 'opp')
        sec = text.split('### How much better')[1].split('\n## ')[0]
        self.assertIn('which does not include no gain', sec)
        self.assertIn('on these 48 paired games kx3 did worse than km3', sec)

    def test_a_partial_run_says_so_near_the_top_and_describes_what_it_has(self):
        t, man, games, text = self.build(deals=2, complete=False)
        self.assertIn('PARTIAL', '\n'.join(text.splitlines()[:8]))
        self.assertRegex(text, r'\d+ of 64 games')
        sec = text.split('## What it says')[1].split('\n## ')[0]
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
        self.assertIn(f'**PARTIAL: {len(keep)} of 64 games played so far ({nx} kx3 games + {nr} cheap km3 baseline games; both count in the 64). ', text)
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
        for source, want in (('given in the config (copied from the pin; the program sha256 is the one named there)', 'copied from the pin, not replayed'),
                             ('replayed by slow_report.py just before registration (equal to the pin)', 'replayed just before registration, equal to the pin'),
                             ('run by strength_prereg.py', 'replayed at registration')):
            t = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, t, True)
            man, games = synth_run(t, selfcheck_source={'kx3': source, 'km3': source})
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
