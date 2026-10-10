#!/usr/bin/env python3
"""The opt-in slow report: how does one deck do with the strong, slow pilot kx3?  (plan: rl/results/kx3_slow_report_plan_2026-10-06/PLAN.md)

  slow_report.py DECKFILE [--deals N] [--no-paired] [--threads T]    register, run and report on one deck
  slow_report.py --dir RUNDIR [--report-only | --dry-run]            resume a registered run, or just rewrite its page, or say where it stands
  slow_report.py --selfcheck-only --program PATH                     replay both self-checks of a rebuilt program (a game at a time, resumable) and write their record

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

The self-check replay of a rebuilt program (--program PATH; hours for kx3 if it is one run of 12 games) is played a game at a time: `strength selfcheck --games 1 --seed-base 24900000000+i`,
each game kept as it ends in <out-root>/.selfcheck_state/ (a run's own .selfcheck_state when a resume replays it; a .gitignore of `*` inside), keyed by the program's sha256, the pilot, the seed,
the whole command and the two deck files, so that a restart goes on from the next game. A game alone prints the digest of its own string, which is recovered (the one outcome and points whose
FNV-1a equals it) and the twelve are chained into the 12-game line, which must equal the committed pin's text character for character; a game that cannot be taken apart again falls back to
the 12-game replay (--whole-selfcheck asks for it), and a line that differs is refused, as before. A successful replay of a rebuilt program writes a record, rl/results/slow_report_selfcheck_records/
selfcheck_<sha12>_<time>.json (program path and sha256, both texts, the checkout's commit, the time, the host and boot id), for the runner to commit: a registration of a program with that very sha256, from
a checkout whose HEAD has the record unedited and with the pin's two texts, replays nothing and names the record (--selfcheck replays regardless).

One wrapper per run directory (a kernel lock, flock, that the program inherits, so it holds even if the wrapper is killed outright while the program plays on);
a SIGTERM or SIGHUP stops the program before the wrapper exits, except a SIGHUP that was ignored at launch (`nohup`), which stays ignored. Pure standard
library; it calls strength_prereg.py, the pinned program and strength_report.py (for REPORT.md, the engineering numbers).
"""
import sys
sys.dont_write_bytecode = True  # a dry run must leave nothing behind in the repository
import argparse, datetime, fcntl, hashlib, importlib.util, json, math, os, re, shlex, shutil, signal, socket, statistics, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import strength_report as R  # noqa: E402  (mean_ci, wilson, registration_problems, Z: the report's own arithmetic)
import strength_prereg as PRE  # noqa: E402  (deck_signature: what a deck file says, not how it was saved)

DEFAULT_PIN = os.path.join(HERE, 'slow_report_pin.json')
PREREG = os.path.join(HERE, 'strength_prereg.py')
REPORT = os.path.join(HERE, 'strength_report.py')
UTC = datetime.timezone.utc
_TZ = {}


class NoTimeZoneDatabase(RuntimeError):
    pass


def chicago():
    """America/Chicago, loaded on first use: importing this module never needs the time zone database, and a run with --school-rule off needs it only to date its folder
    (local_date falls back to the UTC date without it)."""
    if 'chicago' not in _TZ:
        try:
            import zoneinfo
            _TZ['chicago'] = zoneinfo.ZoneInfo('America/Chicago')
        except Exception as e:  # ZoneInfoNotFoundError (no tzdata on a slim image), ModuleNotFoundError
            raise NoTimeZoneDatabase(f'the time zone database (America/Chicago) is not available here ({type(e).__name__}): install tzdata, or turn the school-morning rule off with --school-rule off') from None
    return _TZ['chicago']


def __getattr__(name):  # sr.CHICAGO still works for callers, loaded when first asked for
    if name == 'CHICAGO':
        return chicago()
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def local_date(t):
    """The date for a run folder's name: today in Chicago, or the UTC date on a machine without the time zone database (a run with --school-rule off needs nothing else from it)."""
    try:
        return t.astimezone(chicago()).strftime('%Y-%m-%d')
    except NoTimeZoneDatabase:
        return t.astimezone(UTC).strftime('%Y-%m-%d')


SCHOOL_DAYS = (0, 1, 2, 3, 4)  # Monday to Friday (datetime.weekday)
DEFAULT_SCHOOL_DAYS = 'mon,tue,wed,thu,fri'
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
    for k in ('pilot', 'reference', 'pilot_label', 'reference_label', 'panel_label', 'panel_group', 'program', 'program_sha256', 'selfcheck', 'selfcheck_measured_on_sha256',
              'harness_source_sha256', 'engine', 'pilot_provenance', 'reference_provenance', 'seed_block', 'seed_step', 'games_per_hour', 'scrub_env_prefixes', 'threads',
              'seed_reserved'):
        if k not in pin:
            die(f'the pin {path} has no {k!r}')
    block, step, reserved = pin['seed_block'], pin['seed_step'], pin['seed_reserved']
    if not (isinstance(block, list) and len(block) == 2 and all(type(x) is int for x in block) and block[0] <= block[1] and type(step) is int and step >= 1):
        die(f'the pin {path}: seed_block must be [first seed, last seed] (two whole numbers) and seed_step a whole number of at least 1')
    lo, hi = block
    if not isinstance(reserved, list) or not all(isinstance(r, dict) and type(r.get('base')) is int and isinstance(r.get('note'), str) and lo <= r['base'] and r['base'] + step - 1 <= hi
                                                 and (r['base'] - lo) % step == 0 for r in reserved):
        die(f'the pin {path}: seed_reserved must be a list of {{"base": the first seed of a slot inside the seed block, "note": text}}; a typo there would hand out a slot a committed run already used')
    return pin


def harness_source_sha256(repo):
    """What rl/strength/build.sh prints as the harness source hash: sha256 of rl/strength/src/*.rs (in name order) followed by Cargo.toml, or None when the checkout has no
    harness source (a test repository)."""
    d = os.path.join(repo, 'rl', 'strength')
    try:
        names = sorted(n for n in os.listdir(os.path.join(d, 'src')) if n.endswith('.rs'))
        data = b''
        for n in names:
            with open(os.path.join(d, 'src', n), 'rb') as f:
                data += f.read()
        with open(os.path.join(d, 'Cargo.toml'), 'rb') as f:
            data += f.read()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


def check_program(pin, program=None, repo=None):
    """Refuse (before anything is written) a program that is not the pinned build, and say which route it takes: ('pinned', sha) for the pinned binary, or, when a
    `program` path was given and its sha256 differs, ('rebuilt', sha): a rebuild of the pinned source (for example on the cloud with build.sh), accepted only because the
    caller then replays BOTH self-checks on it against the committed pin's digests, and only when this checkout's harness source is the pinned build's."""
    p = program or pin['program']
    ref8 = (pin.get('engine_ref') or '')[:8] or 'the pinned source'
    if not os.path.isfile(p):
        die(f'REFUSED: the program {p} does not exist, so no slow report can run. A different build needs a new pin (rl/strength/slow_report_pin.json), after its own gate; a REBUILD of '
            f'{ref8} (for example on the cloud, with rl/strength/build.sh) goes through --program PATH.')
    actual = sha(p)
    if actual == pin['program_sha256']:
        return 'pinned', actual
    if not program:
        die(f'REFUSED: {p} (sha256 {actual[:12]}) is not the pinned build (sha256 {pin["program_sha256"][:12]}). A slow report uses only the exact tested version. If this is a rebuild of '
            f'{ref8} (for example on the cloud, with rl/strength/build.sh), pass it with --program PATH: both self-checks are then replayed on this machine '
            'and must equal the committed pin\'s digests. A later version replaces the pin only after its own gate.')
    if os.path.realpath(p) == os.path.realpath(pin['program']):
        die(f'REFUSED: {p} is the pinned binary\'s own path, but the file there has sha256 {actual[:12]}, not the pinned {pin["program_sha256"][:12]}: the frozen binary has been overwritten '
            '(do not build over it; build.sh to another path). A rebuild is accepted at any other path, after its self-checks are replayed.')
    here = harness_source_sha256(repo) if repo else None
    if here != pin['harness_source_sha256']:
        die(f'REFUSED: {p} has sha256 {actual[:12]}, not the pinned {pin["program_sha256"][:12]}, so it would have to be a rebuild of the pinned source; but the harness source in this checkout '
            f'({(here or "not found")[:12]}) is not the pinned build\'s ({pin["harness_source_sha256"][:12]}), so a build from here is not that program. Check out the commit the pin was made on, '
            'or make a new pin after its own gate.')
    return 'rebuilt', actual


GIT_REPO_VARS = PRE.GIT_REPO_VARS


def git_env():
    """The environment for a read of the repository we were told about: without the variables (a git hook or `rebase --exec` exports them) that make git read ANOTHER repository
    whatever `git -C` says, and without optional locks, so a dry run writes nothing."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_REPO_VARS}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    return env


PIN_REL = 'rl/strength/slow_report_pin.json'
ALLOW_UNCOMMITTED_PIN = 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN'  # test only: lets a hand-made pin through, and the registration says so


def pin_commit_state(repo, pin_path):
    """Whether the pin in use is the pin that is committed: byte-equal to HEAD's rl/strength/slow_report_pin.json in `repo`. Everything a report says about the program (it is
    the pinned binary, its self-check texts were measured on it, a rebuild must replay them) rests on the pin, so a hand-edited pin, or `--pin copy.json`, could make any
    program look pinned. Returns {'state': 'yes' | 'no' | 'bypassed', 'sha256': the pin file's, 'detail': why not}."""
    psha = sha(pin_path)
    detail = ''
    try:
        r = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], capture_output=True, env=git_env())
        if r.returncode != 0:
            said = r.stderr.decode('utf-8', 'replace').strip()
            detail = f'HEAD has no {PIN_REL} in {repo} (not a git repository, no commit, or the file is not committed)'
            if said:
                detail += f'; git said: {said.splitlines()[0][:200]}'
                if 'safe.directory' in said:  # a checkout made by another user (a root container on the cloud): git refuses it, the pin may well be committed
                    detail += f' (git refuses this folder as unsafe, which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory {shlex.quote(repo)})'
        elif hashlib.sha256(r.stdout).hexdigest() != psha:
            detail = f'the pin file (sha256 {psha[:12]}) differs from the {PIN_REL} committed at HEAD (sha256 {hashlib.sha256(r.stdout).hexdigest()[:12]})'
    except OSError:
        detail = 'git is not available, so the committed pin cannot be read'
    if not detail:
        return {'state': 'yes', 'sha256': psha, 'detail': ''}
    if os.environ.get(ALLOW_UNCOMMITTED_PIN):
        return {'state': 'bypassed', 'sha256': psha, 'detail': f'{detail}; allowed by {ALLOW_UNCOMMITTED_PIN} (test use)'}
    return {'state': 'no', 'sha256': psha, 'detail': detail}


def require_committed_pin(repo, pin_path):
    st = pin_commit_state(repo, pin_path)
    if st['state'] == 'no':
        die(f'REFUSED: the pin is not the committed one: {st["detail"]}. A slow report trusts the pin for what the program is, so it uses only {PIN_REL} as committed at HEAD '
            '(commit the pin, in the repository you run from; a hand-edited or copied pin is refused). Nothing was written.')
    return st


BUILD_RECORD_TEXT_KEYS = ('program_sha256', 'engine_arg', 'engine', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'rustc', 'cargo', 'machine', 'host', 'built_at', 'rebuild_command')


def record_text(rec, key):
    """A build record field as text for the page; the fields build.sh always writes can be missing only in a hand-made record, which then says 'not recorded'."""
    v = rec.get(key)
    return v if isinstance(v, str) and v else 'not recorded'


def rustc_line(rec, missing):
    """The first non-empty line of the record's `rustc -vV`, or `missing` (worded for the sentence it goes in)."""
    t = rec.get('rustc')
    return next((l for l in t.splitlines() if l.strip()), missing) if isinstance(t, str) else missing


def read_build_record(program, pin):
    """The record rl/strength/build.sh writes beside a program (PROGRAM.build.json), checked against the file and the pin: it must be for this exact file (program sha256), and the
    engine tree it ARCHIVED (git's tree id of the extracted files, not read back from the ref), the harness source it compiled and, when it is a git ref, the commit must be the pin's. A
    rebuild without that record, or with one that differs, is not the pinned source whatever its self-check says. Returns the record plus the record file's sha256."""
    path = program + '.build.json'
    hint = 'rl/strength/build.sh writes it beside the program it builds (build with it, to the path you pass here)'
    if not os.path.isfile(path):
        die(f'REFUSED: {program} has no build record ({path}); {hint}. Nothing was written.')
    try:
        rec = load_json(path)
    except (OSError, ValueError) as e:
        die(f'REFUSED: the build record {path} cannot be read ({e}); {hint}. Nothing was written.')
    if not isinstance(rec, dict) or type(rec.get('schema')) is not int or rec['schema'] != 1:
        die(f'REFUSED: the build record {path} is not a schema 1 record; {hint}. Nothing was written.')
    for key in BUILD_RECORD_TEXT_KEYS:  # the page and the plan print these as text: a record with another type is damaged, not a build record
        if rec.get(key) is not None and not isinstance(rec[key], str):
            die(f'REFUSED: the build record {path} has an entry {key} that is not text; {hint}. Nothing was written.')
    actual = sha(program)
    if rec.get('program_sha256') != actual:
        die(f'REFUSED: the build record {path} is for a program with sha256 {str(rec.get("program_sha256"))[:12]}, but {program} has sha256 {actual[:12]}: the record belongs to the file it was '
            'written for. Nothing was written.')
    for key, want, what in (('engine_tree_archived', pin.get('engine_tree'), 'engine tree'), ('harness_source_sha256', pin.get('harness_source_sha256'), 'harness source')):
        if not want:
            die(f'REFUSED: the pin has no {key if key != "engine_tree_archived" else "engine_tree"}, so a rebuild cannot be checked against it. Nothing was written.')
        if rec.get(key) != want:
            die(f'REFUSED: the build record says the {what} that went into {program} is {str(rec.get(key))[:12]}, not the pinned {want[:12]}, so it is not a build of the pinned source. Nothing was written.')
    if rec.get('engine_ref') and pin.get('engine_ref') and rec['engine_ref'] != pin['engine_ref']:
        die(f'REFUSED: the build record says the engine ref was {rec["engine_ref"][:12]}, not the pinned {pin["engine_ref"][:12]}. Nothing was written.')
    return dict(rec, record_file=path, record_sha256=sha(path))


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
        return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, env=git_env())
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
def pick_seed_base(deck_sha, out_root, block, step, explicit=None, reserved=()):
    """A seed base from the registered block (24,601,000,000 - 24,699,999,999; the exam's seeds spill past its own block up to 24,600,070,002, so slot 0 starts
    above that): the deck's own slot, the next free one if another slow report took it. An explicit base must be the start of a slot inside the block. `reserved` is
    the pin's list of slots already used by committed runs that are not in out_root (the km3 smoke), [{'base': ..., 'note': ...}]."""
    lo, hi = block
    slots = (hi - lo + 1) // step
    used = {}  # slot -> the run folder (or the reserved note) that holds it
    for r in reserved:
        b = r.get('base') if isinstance(r, dict) else None
        if isinstance(b, int) and lo <= b <= hi:
            used.setdefault((b - lo) // step, r.get('note') or 'a reserved slot')
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
            die(f'REFUSED: --seed-base {explicit} is a seed slot that is already used ({used[(explicit - lo) // step]}); two reports would play the same deals')
        return explicit
    start = int(deck_sha[:8], 16) % slots
    for k in range(slots):
        s = (start + k) % slots
        if s not in used:
            return lo + s * step
    die(f'REFUSED: every seed slot in {lo}-{hi} is already used by a slow report')


def resume_command_for(rundir, school_rule, school_days_text):
    """The command that continues a run as it was registered: it carries the school-morning choice, so a cloud resume does not silently idle 5:15 am to 5 pm Chicago time."""
    cmd = ['python3', 'rl/strength/slow_report.py', '--dir', rundir]
    if school_rule == 'off':
        cmd += ['--school-rule', 'off']
    elif school_days_text != DEFAULT_SCHOOL_DAYS:
        cmd += ['--school-days', school_days_text]
    return shlex.join(cmd)


def unfinished_runs(out_root, deck_name):
    """[(folder, games played, games planned, the command that resumes it as it was registered)] for registered slow reports of this deck in out_root that have not played
    all their games: registering a new one next to them is usually a mistake (resume the old one). An odd folder (a stray file, a half-written manifest) is skipped."""
    out = []
    try:
        names = sorted(os.listdir(out_root))
    except OSError:
        return out
    for n in names:
        d = os.path.join(out_root, n)
        try:
            m = load_json(os.path.join(d, 'manifest.json'))
            block = m.get('slow_report') if isinstance(m, dict) else None
            if not isinstance(block, dict) or block.get('deck_name') != deck_name or not isinstance(m.get('planned_games'), int):
                continue
            played = len({g['key'] for g in load_games(d)})
            if played < m['planned_games']:
                days = block.get('school_days')  # '' is a choice (no school days), only a missing entry means the default
                out.append((d, played, m['planned_games'], block.get('resume_command') or resume_command_for(d, block.get('school_rule') or 'on', days if days is not None else DEFAULT_SCHOOL_DAYS)))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return out


# ------------------------------------------------------------------------------------------------------------------ the school-morning rule
def school_action(now, school_days=SCHOOL_DAYS, soft=SOFT_STOP, hard=HARD_STOP, resume=RESUME):
    """What the runner may do at `now` (an aware datetime; read as Chicago time):
    {'kind': 'wait', 'until': dt}  on a school day from the soft stop to the resume time;
    {'kind': 'run', 'stop_after_min': minutes, 'hard_stop': dt}  otherwise: stop starting games at the next school morning's 5:15, kill at its 6:30
    (real minutes, so a clock change is counted); with no school days there is no limit."""
    if not school_days:
        return {'kind': 'run', 'stop_after_min': None, 'hard_stop': None}
    tz = chicago()
    local = now.astimezone(tz)

    def at(d, hm):
        return datetime.datetime(d.year, d.month, d.day, hm[0], hm[1], tzinfo=tz)

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


def _clear_signal_mask():
    """In the new program, between fork and exec: no signal blocked. The wrapper holds SIGTERM, SIGHUP and SIGINT while it starts a program (run_games), and a child inherits the
    mask, so without this the program would not hear the SIGTERM that stops it."""
    signal.pthread_sigmask(signal.SIG_SETMASK, ())


def default_spawn(cmd, env, logfile):
    fh = open(logfile, 'ab')
    proc = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=fh, stderr=fh, start_new_session=True, pass_fds=tuple(_LOCK_FDS), preexec_fn=_clear_signal_mask)
    proc._logfh = fh
    return proc


STOP_SIGNALS = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)  # held while a program is started (see run_games and run_selfcheck)


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
    ignored when the wrapper started (`nohup`) stays ignored: the launcher asked for the run to outlive its terminal.
    Only the first stop signal raises. Two different signals that were held together (while a program is started) arrive together when they are released: the second handler
    would raise at the entry of stop_group, before the program had been signalled, and leave it running. A later signal is recorded in `later` and does nothing: the run is already stopping."""
    stopping = None  # the signal that is stopping the run (class-level: the handler is one function for every signal)
    later = []

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
        cls = signals_stop_the_program
        if cls.stopping is not None:
            cls.later.append(signum)
            return
        cls.stopping = signum
        raise SystemExit(128 + signum)

    def __exit__(self, *a):
        try:
            for sig, h in self.old.items():
                signal.signal(sig, h)
        finally:
            if self.old:  # the next call starts afresh (a call that installed nothing, off the main thread, has nothing to forget and must not wipe the state of one that did)
                signals_stop_the_program.stopping = None
                signals_stop_the_program.later = []


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
                 resume_command=None, program=None, route='pinned', harness_checkout=None, school_rule='on', school_days=DEFAULT_SCHOOL_DAYS, pin_state=None, build_record=None,
                 registered_on=None, selfcheck_record=None):
    """`selfcheck_record` (committed_selfcheck_record's answer) says the texts in `selfcheck_given` were not replayed for this registration but accepted from a committed record of an earlier
    replay; strength_prereg.py is still told they are 'replayed' (the only way it takes a rebuild's texts), and the record is named here: in the engine text, the summary and two entries of the
    slow_report block (selfcheck_how 'record <path> <commit>', selfcheck_record)."""
    headline = headline_of(pin, deck_name)
    rec = build_record or {}
    digests = pin_digests((pin_state or {}).get('state'))
    how_checked = (f"were replayed on the registering machine and equal {digests}" if not selfcheck_record else
                   f"equal {digests}: replayed by slow_report.py on {selfcheck_record.get('host') or 'a machine not recorded'} and recorded in {selfcheck_record['path']} "
                   f"(commit {selfcheck_record['commit'][:12]}), for a program with this same sha256; the record is a committed file, not signed, and this registration did not replay them again. "
                   "Where this document, manifest.json (selfcheck_source) and REPORT.md say \"replayed by slow_report.py on the registering machine just before registration\" (strength_prereg.py's "
                   "fixed wording for a rebuild), that means the earlier replay named here, not a replay at this registration")
    engine = pin['engine'] + (f"; THIS PROGRAM ({(program or pin['program'])}, sha256 {program_sha[:12]}) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) "
                              f"says it is a rebuild of that source (build record sha256 {str(rec.get('record_sha256'))[:12]}: engine tree as archived {str(rec.get('engine_tree_archived'))[:12]}, harness source "
                              f"{str(rec.get('harness_source_sha256'))[:12]}, {rustc_line(rec, 'toolchain not recorded')}), accepted because both self-checks "
                              f"{how_checked}" if route == 'rebuilt' else '')
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
        program=program or pin['program'], program_sha256=program_sha, engine=engine, pilot_provenance=pin['pilot_provenance'], reference_provenance=pin['reference_provenance'],
        slow_report=dict(version=1, headline=headline, summary=f'Stage use. {plural(deals, "deal")} x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.'
                         + (f" Self-check: accepted from the committed record {selfcheck_record['path']} (commit {selfcheck_record['commit'][:12]}), not replayed at registration."
                            if selfcheck_record else ''),
                         deck_name=deck_name, deck_file=deck_rel, deck_file_sha256=deck_sha, deck_file_state=deck_state, deals=deals, paired=bool(paired),
                         pin=dict(path=os.path.relpath(pin_path, ROOT).replace(os.sep, '/') if os.path.abspath(pin_path).startswith(ROOT + os.sep) else pin_path, sha256=sha(pin_path)),
                         pilot_label=pin['pilot_label'], reference_label=pin['reference_label'], panel_label=pin['panel_label'],
                         scrub_env_prefixes=list(pin['scrub_env_prefixes']), resume_command=resume_command,
                         program_route=route, pinned_program=pin['program'], pinned_program_sha256=pin['program_sha256'],
                         harness_source_sha256=pin['harness_source_sha256'], harness_source_checkout_sha256=harness_checkout,
                         engine_ref=pin.get('engine_ref'), engine_tree=pin.get('engine_tree'),
                         pin_committed=pin_state['state'] if pin_state else None, pin_committed_detail=(pin_state or {}).get('detail') or None, registered_on=registered_on,
                         build_record=build_record,
                         school_rule=school_rule, school_days=school_days,
                         expected_hours=dict(typical_low=et['typical_hours'][0], typical_high=et['typical_hours'][1], wall=et['wall_hours'])),
    )
    if selfcheck_given == 'pin':
        cfg['selfcheck_given'] = dict(pin['selfcheck'])
        cfg['selfcheck_given_program_sha256'] = pin['selfcheck_measured_on_sha256']  # the binary these texts were measured on: strength_prereg checks it is the program
    elif selfcheck_given:
        cfg['selfcheck_given'] = dict(selfcheck_given)
        cfg['selfcheck_given_program_sha256'] = program_sha  # measured just now, on this program
        cfg['selfcheck_how'] = selfcheck_how
    if selfcheck_record:
        cfg['slow_report']['selfcheck_how'] = f"record {selfcheck_record['path']} {selfcheck_record['commit']}"
        cfg['slow_report']['selfcheck_record'] = dict(selfcheck_record)
    return cfg


def run_prereg(cfg_path, rundir, repo):
    return subprocess.run([sys.executable, '-B', PREREG, '--config', cfg_path, '--out', rundir, '--repo', repo], capture_output=True, text=True)


class SelfcheckLate(Exception):
    """The school-morning cut came before a self-check program ended; the program has been stopped."""


def run_held(cmd, env, deadline, now):
    """Run one self-check program to its end in its own process group and return (exit code, stdout, stderr). The group is stopped if this wrapper is interrupted, and if `deadline`
    (the school-morning 6:30 cut) comes first, which raises SelfcheckLate."""
    # the stop signals are held while the program is started (a replay is hours for kx3): a SIGTERM that comes between the start of the program and the try that stops it must not leave it running
    held = signal.pthread_sigmask(signal.SIG_BLOCK, ())
    proc = None
    try:
        signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='replace', env=env, start_new_session=True,
                                preexec_fn=_clear_signal_mask)
    except BaseException:
        try:
            if proc is not None:
                stop_group(proc)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, held)
        raise
    try:
        signal.pthread_sigmask(signal.SIG_SETMASK, held)  # (inside this try: a signal that waited is delivered here, and the program is stopped)
        timeout = None if deadline is None else max(0.0, (deadline.astimezone(UTC) - now().astimezone(UTC)).total_seconds())
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_group(proc)
        raise SelfcheckLate() from None
    except BaseException:
        stop_group(proc)
        raise
    finally:
        for pipe in (proc.stdout, proc.stderr):
            if pipe:
                pipe.close()
    return proc.returncode, out, err


# ------------------------------------------------------------------------------------------------------------------ the self-check, a game at a time
# rl/strength/src/main.rs `selfcheck --games N --seed-base B` plays game i with seed B + i (B defaults to 24_900_000_000) and chains FNV-1a 64 (basis 0xcbf29ce484222325) over one string
# per game, "{seed}|{outcome:?}|{points:?}|{turn count}", printing `selfcheck pilot=P games=N seat0_wins=A seat1_wins=B ties=T turns=S digest=H` (a tie and a game without a
# result both count as a tie). A game played alone prints the digest of its own string, so the string can be recovered from that line, and twelve of them chained are the 12-game line.
SELFCHECK_GAMES = 12
SELFCHECK_SEED_BASE = 24_900_000_000
SELFCHECK_FNV_BASIS = 0xcbf29ce484222325
SELFCHECK_FNV_PRIME = 0x100000001b3
SELFCHECK_MAX_POINTS = 20  # a game's two point totals are looked for from 0 to this
SELFCHECK_LINE = re.compile(r'selfcheck pilot=(\S+) games=(\d+) seat0_wins=(\d+) seat1_wins=(\d+) ties=(\d+) turns=(\d+) digest=([0-9a-f]{16})')
STATE_DIR_NAME = '.selfcheck_state'
CHECKPOINT_VERSION = 1


def fnv1a(h, data):
    """FNV-1a 64 of `data` (bytes), continuing from the hash `h` (the harness's `fnv`)."""
    for b in data:
        h ^= b
        h = (h * SELFCHECK_FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


def parse_selfcheck_line(text):
    """The parts of a self-check line, or None when `text` is not exactly one."""
    m = SELFCHECK_LINE.fullmatch(text) if isinstance(text, str) else None
    if not m:
        return None
    pilot, games, w0, w1, ties, turns, digest = m.groups()
    return dict(pilot=pilot, games=int(games), seat0_wins=int(w0), seat1_wins=int(w1), ties=int(ties), turns=int(turns), digest=int(digest, 16))


def recover_game_string(seed, text):
    """(game, None) for the line a single self-check game printed, or (None, why). The game is the string the harness hashed for it ('{seed}|{outcome}|[{a}, {b}]|{turns}'), found as
    the one candidate (outcome, points) whose FNV-1a equals the printed digest, with the counts and the pilot as printed. No candidate, or more than one, is no answer: the caller then
    replays the 12 games in one run."""
    p = parse_selfcheck_line(text)
    if p is None:
        return None, 'its output is not one self-check line'
    if p['games'] != 1:
        return None, f"its output is for {p['games']} games, not one"
    counts = (p['seat0_wins'], p['seat1_wins'], p['ties'])
    outcomes = {(1, 0, 0): ['Some(Win(0))'], (0, 1, 0): ['Some(Win(1))'], (0, 0, 1): ['Some(Tie)', 'None']}.get(counts)
    if outcomes is None:
        return None, 'its counts are not those of one game'
    if p['turns'] > 255:
        return None, 'its turn count does not fit the harness\'s one byte'
    found = [s for s in (f"{seed}|{out}|[{a}, {b}]|{p['turns']}" for out in outcomes for a in range(SELFCHECK_MAX_POINTS + 1) for b in range(SELFCHECK_MAX_POINTS + 1))
             if fnv1a(SELFCHECK_FNV_BASIS, s.encode()) == p['digest']]
    if not found:
        return None, f'no (outcome, points) up to {SELFCHECK_MAX_POINTS} points makes its digest'
    if len(found) > 1:
        return None, 'more than one (outcome, points) makes its digest'
    return dict(string=found[0], pilot=p['pilot'], seat0_wins=counts[0], seat1_wins=counts[1], ties=counts[2], turns=p['turns']), None


def chain_selfcheck_line(pilot, games):
    """The line the harness prints for these games (as recover_game_string gives them, in order) played in one run."""
    h = SELFCHECK_FNV_BASIS
    for g in games:
        h = fnv1a(h, g['string'].encode())
    return (f"selfcheck pilot={pilot} games={len(games)} seat0_wins={sum(g['seat0_wins'] for g in games)} seat1_wins={sum(g['seat1_wins'] for g in games)} "
            f"ties={sum(g['ties'] for g in games)} turns={sum(g['turns'] for g in games)} digest={h:016x}")


def write_atomic(path, data):
    """Write `data` (bytes) to `path` so that the file is the old one or the whole new one, never half: a temporary file in the same folder, forced to disk, renamed over the target, and the
    folder forced to disk."""
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    tmp = f'{path}.tmp{os.getpid()}'
    try:
        with open(tmp, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    try:
        fd = os.open(folder, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass


def ensure_state_dir(state_dir):
    """The checkpoint folder, made on first use with a .gitignore of `*`: what is kept there is working state, never something a `git add` of the folder around it should pick up."""
    os.makedirs(state_dir, exist_ok=True)
    ignore = os.path.join(state_dir, '.gitignore')
    if not os.path.exists(ignore):
        write_atomic(ignore, b'*\n')


def selfcheck_command(pin, repo, spec, deck_a, deck_b):
    return [pin['program'], 'selfcheck', '--root', repo, '--pilot', spec, '--deck-a', deck_a, '--deck-b', deck_b]


def checkpoint_name(spec, program_sha, i):
    return f"{re.sub(r'[^A-Za-z0-9._-]', '_', spec)}_{program_sha[:16]}_{i:02d}.json"


def load_checkpoint(path, key, seed, spec):
    """The recovered game of a checkpoint file, or None: the file must be JSON, its key must equal `key` exactly (program sha256, pilot, game, seed, the whole command, the deck files), and its
    output must make its own digest again (it is read afresh, the stored string is not trusted)."""
    try:
        data = load_json(path)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get('key') != key or not isinstance(data.get('output'), str):
        return None
    game, _why = recover_game_string(seed, data['output'])
    return game if game is not None and game['pilot'] == spec else None


def file_sha_or_none(path):
    try:
        return sha(path)
    except OSError:
        return None


def selfcheck_per_game(pin, repo, spec, say, deadline, now, state_dir, env, deck_a, deck_b):
    """The 12 self-check games one at a time (`--games 1 --seed-base 24900000000+i`), each kept in `state_dir` as it ends (a stop or a restart loses at most the game in flight), rebuilt into
    the 12-game line. Returns the pin's text when the rebuilt line equals it, character for character; refuses when it does not (the 12-game replay would too: the games do not depend on each
    other); returns None, after saying why, when a game's output cannot be taken apart again, and the caller replays the 12 games in one run."""
    program = pin['program']
    program_sha = sha(program)
    deck_files = (os.path.join(repo, deck_a), os.path.join(repo, deck_b))
    decks = tuple(file_sha_or_none(p) for p in deck_files)
    base_cmd = selfcheck_command(pin, repo, spec, deck_a, deck_b)
    games, kept = [], 0  # (`kept`: the games that are in the folder, taken from it or written to it; a write that fails is said and not counted)

    def kept_note():
        if kept == len(games):
            return f'{kept} of the {SELFCHECK_GAMES} games are kept in {state_dir}, so starting it again goes on from game {kept + 1}'
        return f'only {kept} of the {len(games)} games played could be kept in {state_dir}, so starting it again takes those and plays the others again'
    for i in range(SELFCHECK_GAMES):
        seed = SELFCHECK_SEED_BASE + i
        command = base_cmd + ['--games', '1', '--seed-base', str(seed)]
        key = dict(version=CHECKPOINT_VERSION, program_sha256=program_sha, spec=spec, game=i, games=SELFCHECK_GAMES, seed=seed, command=command, deck_a_sha256=decks[0], deck_b_sha256=decks[1])
        path = os.path.join(state_dir, checkpoint_name(spec, program_sha, i))
        game = load_checkpoint(path, key, seed, spec)
        if game is not None:
            say(f'self-check of {spec}: game {i + 1} of {SELFCHECK_GAMES} taken from the checkpoint ({os.path.basename(path)})')
            games.append(game)
            kept += 1
            continue
        started = time.monotonic()
        try:
            code, out, err = run_held(nice_prefix() + command, env, deadline, now)
        except SelfcheckLate:
            die(f'REFUSED: the self-check of {spec} did not finish before the school-morning cut at {deadline.astimezone(chicago()).strftime("%a %H:%M")} Chicago time; '
                f'{kept_note()}. Nothing was registered. Start it earlier in the evening or on a weekend (or with --school-rule off).')
        got = out.strip()
        if code != 0:
            die(f'REFUSED: the self-check of {spec} on {program} exited with code {code} ({(err.strip()[-200:] or got[-200:] or "no output")}); a self-check that fails is not a match, '
                f'whatever it printed. Nothing was registered; {kept_note()}.')
        # the key names the program and the decks by their sha256, read before the first game: a game is kept only when they are still what the key says (hours pass over the 12 games)
        after = (file_sha_or_none(program),) + tuple(file_sha_or_none(p) for p in deck_files)
        if after != (program_sha,) + decks:
            die(f'REFUSED: the program at {program} or a self-check deck changed while game {i + 1} of the self-check of {spec} was played (sha256 of the program {program_sha[:12]} -> '
                f'{after[0][:12] if after[0] else "gone"}): that game is not kept, because what it checked is not what the checkpoint would name. Nothing was registered; {kept_note()}.')
        game, why = recover_game_string(seed, got)
        if game is None or game['pilot'] != spec:
            say(f'self-check of {spec}: game {i + 1}: {why or "its output names another pilot"}; the {SELFCHECK_GAMES} games are replayed in one run instead (not resumable)')
            return None
        games.append(game)
        try:
            ensure_state_dir(state_dir)
            write_atomic(path, (json.dumps(dict(key=key, output=got, at=utc_iso(), host=socket.gethostname()), indent=1) + '\n').encode('utf-8'))
            kept += 1
        except OSError as e:
            say(f'self-check of {spec}: game {i + 1} could not be kept in {state_dir} ({e.strerror or e}); the replay goes on, but a restart would play it again')
        say(f'self-check of {spec}: game {i + 1} of {SELFCHECK_GAMES} played ({time.monotonic() - started:.0f} s)')
    line = chain_selfcheck_line(spec, games)
    if line != pin['selfcheck'][spec]:
        die(f'REFUSED: the self-check of {spec} does not match the pin.\n  pinned: {pin["selfcheck"][spec]}\n  got:    {line}\n'
            f'The program is not behaving as the pinned build did; nothing was registered. (Rebuilt from the {SELFCHECK_GAMES} games played one at a time, {kept} of them kept in {state_dir}; '
            f'--whole-selfcheck replays all {SELFCHECK_GAMES} in one run, as before.)')
    return line


def selfcheck_whole(pin, spec, deadline, now, env, command):
    """The 12 self-check games in one run of the program (hours for kx3, and lost if the run is): the text it printed, refused on any difference from the pin's."""
    try:
        code, out, err = run_held(nice_prefix() + command, env, deadline, now)
    except SelfcheckLate:
        die(f'REFUSED: the self-check of {spec} did not finish before the school-morning cut at {deadline.astimezone(chicago()).strftime("%a %H:%M")} Chicago time; nothing was written. '
            'Start it earlier in the evening or on a weekend (or with --school-rule off).')
    got = out.strip()
    if code != 0:
        die(f'REFUSED: the self-check of {spec} on {pin["program"]} exited with code {code} ({(err.strip()[-200:] or got[-200:] or "no output")}); a self-check that fails is not a match, '
            'whatever it printed. Nothing was written.')
    if got != pin['selfcheck'][spec]:
        die(f'REFUSED: the self-check of {spec} does not match the pin.\n  pinned: {pin["selfcheck"][spec]}\n  got:    {got[-300:] or err.strip()[-200:]}\n'
            'The program is not behaving as the pinned build did; nothing was written.')
    return got


class ReplayPin(dict):
    """The pin as a replay uses it: the pin's entries, with `program` set to the file to replay, and how the replay is played. `state_dir` is the folder where the games are kept as they end
    (None: nothing is kept and the 12 games are one run), `whole` plays the 12 games in one run even so, and `routes` (a dict) is told which route each pilot's replay took. They ride on the
    pin, so that run_selfcheck keeps its call (pin, repo, spec, say, deadline, now) and the tests that stand in for it by that call keep working."""
    state_dir = None
    whole = False
    routes = None


def run_selfcheck(pin, repo, spec, say, deadline=None, now=None):
    """Replay the 12 fixed self-check games on the program (pin['program'], which the caller sets to the rebuilt copy's path on the --program route) in a scrubbed environment at low
    priority, and refuse on any difference from the committed pin's text. The program runs in its own process group, which is stopped if this wrapper is interrupted or if `deadline` (the
    school-morning 6:30 cut) comes first.

    A pin that is a ReplayPin with a `state_dir` has the games played one at a time and kept as they end, so that a restart goes on from the next game (selfcheck_per_game); that needs the
    pin's text for `spec` to be a 12-game line of that pilot. Any other pin, a ReplayPin with `whole`, or a game whose output cannot be taken apart again, has the 12 games run as one run
    of the program (selfcheck_whole). The pin's `routes` (a dict) is told which was used, per pilot: 'per-game' or 'whole'."""
    state_dir, whole, routes = getattr(pin, 'state_dir', None), getattr(pin, 'whole', False), getattr(pin, 'routes', None)
    reg = load_json(os.path.join(HERE, 'decks.json'))['decks']
    env, _ = scrub_env(dict(os.environ), pin['scrub_env_prefixes'])
    say(f'self-check of {spec}: 12 fixed games on {pin["program"]} (this takes a while for kx3; run it when the machine is free)')
    deck_a, deck_b = reg['t-altaria'], reg['t-suicune']
    pinned = parse_selfcheck_line((pin.get('selfcheck') or {}).get(spec))
    if state_dir and not whole and pinned is not None and pinned['games'] == SELFCHECK_GAMES and pinned['pilot'] == spec:
        got = selfcheck_per_game(pin, repo, spec, say, deadline, now, state_dir, env, deck_a, deck_b)
        if got is not None:
            if routes is not None:
                routes[spec] = 'per-game'
            return got
    if routes is not None:
        routes[spec] = 'whole'
    return selfcheck_whole(pin, spec, deadline, now, env, selfcheck_command(pin, repo, spec, deck_a, deck_b) + ['--games', str(SELFCHECK_GAMES)])


# ------------------------------------------------------------------------------------------------------------------ the record of a replay
RECORDS_REL = 'rl/results/slow_report_selfcheck_records'
RECORD_KIND = 'slow_report_selfcheck_record'


def read_boot_id():
    try:
        with open('/proc/sys/kernel/random/boot_id', encoding='utf-8') as f:
            return f.read().strip() or None
    except OSError:
        return None


def head_commit(repo):
    """The commit at HEAD of `repo`, or None (not a git repository, no commit, no git)."""
    try:
        r = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=git_env())
    except OSError:
        return None
    out = r.stdout.strip()
    return out if r.returncode == 0 and re.fullmatch(r'[0-9a-f]{40}', out) else None


def write_selfcheck_record(repo, program, program_sha, texts, routes, now):
    """After a successful replay of the self-checks on `program`: the record file rl/results/slow_report_selfcheck_records/selfcheck_<sha12>_<time>.json (a new file every time) with the
    program's path and sha256, both texts, the checkout's commit (the tool's), the time, the host and the boot id, and how each pilot was replayed. The runner commits it to its branch;
    once committed, a registration of a program with this sha256 replays nothing (committed_selfcheck_record). Returns the path."""
    t = now()
    folder = os.path.join(repo, *RECORDS_REL.split('/'))
    stamp = t.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')
    path, n = os.path.join(folder, f'selfcheck_{program_sha[:12]}_{stamp}.json'), 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(folder, f'selfcheck_{program_sha[:12]}_{stamp}-{n}.json')
    rec = dict(schema=1, kind=RECORD_KIND, program=program, program_sha256=program_sha, selfcheck=dict(texts), tool_commit=head_commit(repo), replayed_at=utc_iso(t),
               host=socket.gethostname(), boot_id=read_boot_id(), routes=dict(routes))
    write_atomic(path, (json.dumps(rec, indent=1, ensure_ascii=False) + '\n').encode('utf-8'))
    return path


def record_fits(rec, program_sha, pin_texts, specs):
    """Whether a parsed record file says: schema 1, of this kind, made for a program with exactly this sha256, with both self-check texts (for `specs`) equal to the pin's."""
    if not isinstance(rec, dict) or type(rec.get('schema')) is not int or rec['schema'] != 1 or rec.get('kind') != RECORD_KIND:
        return False
    if not isinstance(rec.get('program_sha256'), str) or rec['program_sha256'] != program_sha or not isinstance(rec.get('selfcheck'), dict):
        return False
    return all(isinstance(pin_texts.get(s), str) and rec['selfcheck'].get(s) == pin_texts[s] for s in specs)


def commit_with_file(repo, rel, raw):
    """The commit that last changed `rel` when HEAD of `repo` has the file with exactly the bytes `raw` (so it is committed and unedited), else None. Git is read with git_env()."""
    try:
        r = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', f'HEAD:./{rel}'], capture_output=True, env=git_env())
        if r.returncode != 0 or r.stdout != raw:
            return None
        log = subprocess.run(['git', '-C', repo, 'log', '-n', '1', '--format=%H', 'HEAD', '--', rel], capture_output=True, text=True, env=git_env())
    except OSError:
        return None
    out = log.stdout.strip()
    return out if log.returncode == 0 and re.fullmatch(r'[0-9a-f]{40}', out) else None


def committed_selfcheck_record(repo, program_sha, pin, specs):
    """The record to accept in place of replaying the self-checks: a COMMITTED file in rl/results/slow_report_selfcheck_records/ of `repo` (byte-equal to HEAD's), made for a program with
    exactly this sha256 and carrying the pin's text for each of `specs`. Keyed by the sha256 alone: the path the program was at, or the build record beside it, play no part. Of several, the
    latest replay. Returns {'path', 'commit', 'file_sha256', 'program_sha256', 'replayed_at', 'host', 'boot_id', 'tool_commit'} or None."""
    folder = os.path.join(repo, *RECORDS_REL.split('/'))
    try:
        names = sorted(n for n in os.listdir(folder) if n.endswith('.json'))
    except OSError:
        return None
    texts = pin.get('selfcheck') if isinstance(pin.get('selfcheck'), dict) else {}
    best = None
    for name in names:
        rel = f'{RECORDS_REL}/{name}'
        try:
            with open(os.path.join(folder, name), 'rb') as f:
                raw = f.read()
            rec = json.loads(raw.decode('utf-8'))
        except (OSError, ValueError):
            continue
        if not record_fits(rec, program_sha, texts, specs):
            continue
        commit = commit_with_file(repo, rel, raw)
        if commit is None:
            continue
        when = rec.get('replayed_at') if isinstance(rec.get('replayed_at'), str) else ''
        if best is None or (when, name) > best[0]:
            best = ((when, name), dict(path=rel, commit=commit, file_sha256=hashlib.sha256(raw).hexdigest(), program_sha256=program_sha, replayed_at=rec.get('replayed_at'),
                                       host=rec.get('host'), boot_id=rec.get('boot_id'), tool_commit=rec.get('tool_commit')))
    return best[1] if best else None


def keep_record(repo, program, program_sha, texts, routes, now, say):
    """write_selfcheck_record for a replay that succeeded; a record that cannot be written is said, never fatal (the replay is what counts)."""
    try:
        path = write_selfcheck_record(repo, program, program_sha, texts, routes, now)
    except OSError as e:
        say(f'note: the record of this replay could not be written ({e.strerror or e}); a later registration of this program will replay the self-checks again')
        return None
    rel = os.path.relpath(path, repo).replace(os.sep, '/')
    say(f'the replay is recorded in {rel}: commit that file to your branch, and a registration of this exact program (sha256 {program_sha[:12]}) from a checkout that has it replays nothing')
    return rel


def refuse_if_program_changed(program, expected_sha, nothing_done):
    """After a replay (hours for kx3): what the self-checks checked must be what is there now. Refuses, with `nothing_done` as its last sentence, when `program` is gone or has another sha256."""
    after = sha(program) if os.path.isfile(program) else None
    if after != expected_sha:
        die(f'REFUSED: the program at {program} changed while the self-checks were replayed (sha256 {expected_sha[:12]} -> {after[:12] if after else "gone"}): what they checked is not '
            f'what is there now. {nothing_done}')


def selfcheck_deadline(school_rule, school_days, now):
    """When a self-check replay (hours for kx3) must be over: the next school morning's 6:30 cut, or None with the rule off / no school days. Refuses at school time."""
    if school_rule != 'on' or not school_days:
        return None
    act = school_action(now(), school_days)
    if act['kind'] == 'wait':
        die(f"REFUSED: the self-check runs for hours and it is school time (the school-morning rule waits until {act['until'].astimezone(chicago()).strftime('%a %H:%M')} Chicago time); "
            'start it after that, or with --school-rule off')
    return act['hard_stop']


def pin_digests(state):
    """'the committed pin's digests', or, for a pin that was let through by the test-only variable, what it really is."""
    return "the committed pin's digests" if state == 'yes' else 'the digests of the pin file in use (NOT the committed pin: test use)'  # (a state that is missing is not "yes" either)


def registered_vs_pin(man, pin):
    """A changed program is judged by the pin the run was REGISTERED under, not by whatever pin file is there now: a later pin (another build, another digest) must not let a run
    go on with a program of a different pilot version, which would pool games of two builds in one report. Refuses when the registered engine tree, harness hash, engine ref or
    self-check texts are not the pin's."""
    sr = man.get('slow_report') or {}
    diffs = []
    for key in ('engine_tree', 'harness_source_sha256', 'engine_ref'):
        if (sr.get(key) or None) != (pin.get(key) or None):  # '' and a missing entry are both "not recorded"
            diffs.append(f'{key}: registered {str(sr.get(key))[:12] if sr.get(key) else "not recorded"}, pin now {str(pin.get(key))[:12] if pin.get(key) else "not recorded"}')
    for spec, text in (man.get('selfcheck') or {}).items():
        if (pin.get('selfcheck') or {}).get(spec) != text:
            diffs.append(f"the {spec} self-check text differs (registered: {text}; pin now: {(pin.get('selfcheck') or {}).get(spec, 'none')})")
    if diffs:
        die('REFUSED: the pin in use is not the pin this run was registered under (' + '; '.join(diffs) + '), so a changed program cannot be judged by it: games of two builds would be pooled. '
            'Make the pin the run was registered with the committed one again (for example revert the commit that changed rl/strength/slow_report_pin.json) and use a program built for it, '
            'or register a new run.')


def check_program_change(man, pin, pin_path, repo, school_rule, school_days, now):
    """Everything that is checked before the self-checks are replayed on a program of another sha256 (the real resume and --dry-run both use it, so the dry run does not promise what
    the resume refuses): the pin is the one the run was registered under and is the committed one, the program's build record has the pinned tree and harness, and the school-morning
    rule leaves time. Returns (committed-pin state, the build record, the replay deadline)."""
    registered_vs_pin(man, pin)
    st = require_committed_pin(repo, pin_path)
    rec = read_build_record(man['program'], pin)
    return st, rec, selfcheck_deadline(school_rule, school_days, now)


def program_in_use_before(rundir, man):
    """The sha256 of the program the last sitting ran with: the registered one, then each accepted change and each sitting's own record (a run can go back to an earlier accepted build)."""
    cur = man.get('program_sha256')
    msha = manifest_sha256(rundir)
    events = load_jsonl(os.path.join(rundir, 'slow_report_log.jsonl'))
    legacy = log_started_for(events, msha)
    for e in events:
        if e.get('event') == 'program_changed' and is_program_change(e, man, msha, legacy):
            cur = e['new_sha256']
        elif e.get('event') == 'sitting_call' and isinstance(e.get('program_sha256'), str):
            cur = e['program_sha256']
    return cur


def reverify_program(rundir, man, pin, pin_path, repo, say, school_rule, school_days, now, whole=False):
    """A resume (a container restart) finds a program of another sha256 than the run was registered with. Only a run registered on the rebuilt route may go on, and only because
    (0) the pin in use is the pin it was registered under, (1) that pin is the committed one, (2) the program's build record (PROGRAM.build.json) has the pinned engine tree and harness
    source, and (3) both self-checks are replayed again on it (a game at a time, kept in the run's .selfcheck_state, unless `whole`) and equal the committed pin's digests. The change is
    logged as a 'program_changed' event (the page shows it); the registration is not touched. The replay is recorded (keep_record). Returns the new sha256."""
    prog = man['program']
    new = sha(prog)
    st, rec, deadline = check_program_change(man, pin, pin_path, repo, school_rule, school_days, now)
    say(f"the program at {prog} has sha256 {new[:12]}, not the {str(man.get('program_sha256'))[:12]} this run was registered with; its build record has the pinned engine tree and harness source, "
        f"so both self-checks are replayed again against {pin_digests(st['state'])} before the run goes on (hours for kx3)")
    pin_run = ReplayPin(pin, program=prog)
    routes = pin_run.routes = {}
    pin_run.state_dir, pin_run.whole = os.path.join(rundir, STATE_DIR_NAME), whole
    texts = {spec: run_selfcheck(pin_run, repo, spec, say, deadline=deadline, now=now)
             for spec in sorted({man['pilot'], man['reference']})}
    # the replay took hours for kx3: what was checked must be what is there now (the program and its record are read again, as they were before the replay)
    refuse_if_program_changed(prog, new, 'Nothing was played.')
    if not os.path.isfile(rec['record_file']) or sha(rec['record_file']) != rec['record_sha256']:
        die(f'REFUSED: the build record {rec["record_file"]} changed while the self-checks were replayed: what was checked is not what is there now. Nothing was played.')
    keep_record(repo, prog, new, texts, routes, now, say)
    log_event(rundir, 'program_changed', old_sha256=program_in_use_before(rundir, man), new_sha256=new, manifest_sha256=manifest_sha256(rundir), build_record=rec, selfcheck=texts,
              pin_committed=st['state'], replayed_on=socket.gethostname())
    say(f"program changed mid-run, accepted: both self-checks equal {pin_digests(st['state'])}; logged as program_changed in slow_report_log.jsonl and shown on the page")
    return new


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


PROGRAM_PROBLEM = 'but this run was registered with the program at that path with sha256'


def manifest_sha256(rundir):
    """The sha256 of the run's manifest.json: what names a run (a line of its log that was written for it says so)."""
    return sha(os.path.join(rundir, 'manifest.json'))


def log_started_for(events, msha):
    """Whether the log was started for the run whose manifest.json has sha256 `msha`: its 'registered' event (the first thing logged, with the manifest's sha256 since the first version)
    names it. A log pasted from another run names another manifest."""
    first = next((e for e in events if e.get('event') == 'registered'), None)
    return bool(first) and first.get('manifest_sha256') == msha


def program_change_valid(e, man, msha, legacy=False):
    """Whether a 'program_changed' event of the (unprotected) log is what reverify_program writes for THIS run (`msha`: the sha256 of its manifest.json, which the line names): for the
    program it names, a build record with the registered engine tree and harness hash, and the self-check texts the run was registered with. This keeps a stray, stale or foreign line
    out (a log pasted from another run names another manifest); it is NOT authentication: every value it compares is public in the manifest, and
    whoever can write to the run folder can also rewrite manifest.json and manifest.sha256 (the pushed commit of the registration is the tamper evidence). Lines written before they
    named their run (the version of c28dfb8a) have no manifest_sha256: with `legacy` (the log was started for this run, log_started_for) they count too."""
    sr = man.get('slow_report') or {}
    rec = e.get('build_record')
    return (isinstance(msha, str) and (e.get('manifest_sha256') == msha or (legacy and 'manifest_sha256' not in e)) and isinstance(e.get('new_sha256'), str) and isinstance(e.get('at'), str) and e['at'] != ''
            and isinstance(rec, dict) and rec.get('program_sha256') == e['new_sha256']
            and rec.get('engine_tree_archived') == sr.get('engine_tree') and rec.get('harness_source_sha256') == sr.get('harness_source_sha256')
            and e.get('selfcheck') == man.get('selfcheck'))


def is_program_change(e, man, msha, legacy=False):
    """A 'program_changed' log line this run honours and shows: only a run registered on the rebuilt route has any (a pinned-route run is byte for byte or nothing), and it must pass
    program_change_valid for this run (`legacy`: see there)."""
    return e.get('event') == 'program_changed' and (man.get('slow_report') or {}).get('program_route') == 'rebuilt' and program_change_valid(e, man, msha, legacy)


def accepted_program_shas(rundir, man):
    """The program sha256 values this run may continue with: the registered one, plus, on a run registered on the rebuilt route only, any later one that was accepted after both
    self-checks were replayed again (the 'program_changed' events of slow_report_log.jsonl, written by reverify_program, each checked against the registration: the log is not
    covered by manifest.sha256, and a run registered on the pinned route is byte for byte or nothing)."""
    shas = {man.get('program_sha256')}
    msha = manifest_sha256(rundir)
    events = load_jsonl(os.path.join(rundir, 'slow_report_log.jsonl'))
    legacy = log_started_for(events, msha)
    for e in events:
        if is_program_change(e, man, msha, legacy):
            shas.add(e['new_sha256'])
    return shas


def pin_provenance_problems(man, pin, pin_path):
    """The same claims against the PIN, when the pin file in use is the one the registration was made under (its sha256 is the one the manifest names): the pinned program's sha256, the
    engine tree and the harness source the registration names, and each self-check text it records, must be the pin's. A later pin (another file) is not asked: a run keeps the pin it
    was registered under. [problem, ...]"""
    sr = man.get('slow_report') if isinstance(man.get('slow_report'), dict) else None
    named = (sr.get('pin') or {}).get('sha256') if sr and isinstance(sr.get('pin'), dict) else None
    if not sr or sr.get('program_route') not in ('pinned', 'rebuilt') or not named or not os.path.isfile(pin_path) or sha(pin_path) != named:
        return []
    problems = []
    for key, what in (('pinned_program_sha256', 'pinned program sha256'), ('engine_tree', 'pinned engine tree'), ('harness_source_sha256', 'pinned harness source')):
        pin_key = 'program_sha256' if key == 'pinned_program_sha256' else key
        if sr.get(key) != pin.get(pin_key):
            problems.append(f'the registration names {str(sr.get(key))[:12]} as the {what}, but the pin it was made under (still in use) says {str(pin.get(pin_key))[:12]}')
    pin_texts = pin.get('selfcheck') if isinstance(pin.get('selfcheck'), dict) else {}
    for spec, text in (man.get('selfcheck') or {}).items():
        if pin_texts.get(spec) != text:
            problems.append(f"the registration records the {spec} self-check text {text}, but the pin it was made under (still in use) says {pin_texts.get(spec, 'none')}")
    return problems


def manifest_provenance_problems(man):
    """What the registration says about the program that does not hold, from the manifest alone (so whatever pin is in use now): a pinned-route manifest must carry the pinned
    binary's sha256 as its program's, and a rebuilt-route one a build record for that very program with the engine tree as archived and the harness source the registration names.
    A manifest with no route (from before it was recorded) or no slow_report block claims nothing and has none. [problem text, ...]"""
    sr = man.get('slow_report') if isinstance(man.get('slow_report'), dict) else None
    if not sr or sr.get('program_route') is None:
        return []
    route, prog = sr['program_route'], man.get('program_sha256')
    problems = []
    if route == 'pinned':
        pinned = sr.get('pinned_program_sha256')
        if not pinned:
            problems.append("the registration says the run used the pinned binary but does not name the pinned program's sha256")
        elif prog != pinned:
            problems.append(f'the registration says the run used the pinned binary (sha256 {str(pinned)[:12]}), but its program has sha256 {str(prog)[:12]}')
    elif route == 'rebuilt':
        rec = sr.get('build_record')
        if not isinstance(rec, dict):
            problems.append('the registration says the run used a rebuild but carries no build record')
        else:
            if rec.get('program_sha256') != prog:
                problems.append(f'the build record in the registration is for a program with sha256 {str(rec.get("program_sha256"))[:12]}, not the {str(prog)[:12]} of the run')
            if rec.get('engine_tree_archived') != sr.get('engine_tree'):
                problems.append(f'the build record in the registration has the engine tree {str(rec.get("engine_tree_archived"))[:12]} as archived, '
                                f'but the registration names {str(sr.get("engine_tree"))[:12]} as the pinned one')
            if rec.get('harness_source_sha256') != sr.get('harness_source_sha256'):
                problems.append(f'the build record in the registration has the harness source {str(rec.get("harness_source_sha256"))[:12]}, '
                                f'but the registration names {str(sr.get("harness_source_sha256"))[:12]} as the pinned one')
    else:
        problems.append(f'the registration names no known program route ({route!r})')
    how = sr.get('selfcheck_how')
    if (isinstance(how, str) and how.startswith('record ')) or 'selfcheck_record' in sr:  # texts said to come from a committed record of a replay: it has to be a record for this very program
        rec = sr.get('selfcheck_record')
        if not isinstance(rec, dict):
            problems.append('the registration says its self-checks were accepted from a record but carries none')
        elif rec.get('program_sha256') != prog:
            problems.append(f'the registration says its self-checks were accepted from a record for a program with sha256 {str(rec.get("program_sha256"))[:12]}, not the {str(prog)[:12]} of the run')
    return problems


def program_only_problem(man, problems):
    """Whether the only thing wrong with the inputs is a program of another sha256 that is there, on a run registered on the rebuilt route: the one case a resume may go on with (after
    the checks and the replay of reverify_program). Used by the real resume and by --dry-run, so that they cannot drift apart."""
    return (bool(problems) and all(PROGRAM_PROBLEM in p for p in problems) and (man.get('slow_report') or {}).get('program_route') == 'rebuilt'
            and os.path.isfile(man['program']))


def verify_inputs(man, accepted=None):
    """Problems with the files this run was registered with: the program, the deck and the panel lists (exactly as the program will read them). `accepted` is the set of
    program sha256 values the run may continue with (default: the registered one only)."""
    problems = []
    prog = man['program']
    ok_shas = set(accepted) if accepted else {man.get('program_sha256')}
    if not os.path.isfile(prog) or sha(prog) not in ok_shas:
        how = ('A resume needs the same program, byte for byte (this run was registered on the pinned route, which has no build record and no rebuild; only a run registered with --program '
               'can go on with a rebuild), or a new run' if (man.get('slow_report') or {}).get('program_route') != 'rebuilt' else
               'A resume needs the same program, byte for byte, or a rebuild from the same pinned source whose build record (PROGRAM.build.json, written by rl/strength/build.sh) has the same '
               'engine tree and harness hash and whose two self-checks are replayed again against the committed pin; rebuild with the "rebuild_command" in the registration\'s build record '
               '(same toolchain, HOME, CARGO_HOME and build folders) to get the same bytes, or register a new run')
        problems.append(f'{prog} {"is missing" if not os.path.isfile(prog) else f"has sha256 {sha(prog)[:12]}"}, {PROGRAM_PROBLEM} {str(man.get("program_sha256"))[:12]}. {how}')
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
    path = os.path.join(rundir, 'slow_report_log.jsonl')
    lead = ''
    try:  # a last line that lost its newline (a write cut short) must not swallow the event that follows it
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(-1, os.SEEK_END)
                lead = '' if f.read(1) == b'\n' else '\n'
    except OSError:
        pass
    with open(path, 'a', encoding='utf-8') as f:
        f.write(lead + json.dumps(dict(at=utc_iso(), event=event, **_LOG_EXTRA, **kw), default=str) + '\n')


def run_games(rundir, man, scrub_prefixes, *, threads, max_games, school_on, school_days, now, sleep, spawn, poll_s, say, accepted_shas=None):
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
        problems = verify_inputs(man, accepted_shas)
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
        # a SIGTERM / SIGHUP / SIGINT that comes while the program is being started waits until the loop below can stop it: it must not raise between the start of the program and the
        # try that stops it, which would leave the program running (holding the lock) after its wrapper has gone
        held = signal.pthread_sigmask(signal.SIG_BLOCK, ())  # the mask as it is, read first: the try below restores it, whatever happens to the call that blocks
        proc = None
        try:
            signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
            proc = spawn(cmd, env, out_log)
            _PROGRAMS.append(proc)
            note_program(proc)
        except BaseException:
            try:
                if proc is not None:  # the program was started and what came after failed: it is not left running (stopped before the signals are let in again)
                    stop_group(proc)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, held)
            raise
        killed = False
        try:
            signal.pthread_sigmask(signal.SIG_SETMASK, held)  # (inside this try: a signal that waited is delivered here, and the program is stopped)
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
            log_event(rundir, 'stopped_for_school', at_local=now().astimezone(chicago()).isoformat())  # the clock is UTC by default: the field is Chicago time
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


def wilson_width_points(lo, hi):
    """The width of a Wilson range in points as a reader gets it from the two ends the page prints (each rounded once, to a tenth of a percent): their difference, to a tenth. Worked
    out from the unrounded numbers it can differ from the printed ends by a tenth (30.449% and 50.451% print as 30.4% and 50.5%: 20.0 apart before rounding, 20.1 as printed)."""
    return f'{float(f"{100 * hi:.1f}") - float(f"{100 * lo:.1f}"):.1f}'


def games_word(n):
    return plural(n, 'game')


def range_points(m, half):
    """'probably between -1.9 and +14.4 points' for a difference of scores m +- half (fractions), cut at the ends of the possible scale (-100 to +100 points). The two
    ends are rounded once, from the unrounded numbers, so the sentence never disagrees with itself."""
    lo, hi = m - half, m + half
    cut = ' (cut at the ends of the possible scale)' if lo < -1 or hi > 1 else ''
    return f'probably between {signed_points(max(-1.0, lo))} and {signed_points(min(1.0, hi))} points{cut}'


def range_width_points(m, half):
    """The width of the range range_points prints, worked out from the two ends as printed (each rounded once), so a sentence about the width never disagrees with them."""
    return round(100 * min(1.0, m + half), 1) - round(100 * max(-1.0, m - half), 1)


def gain_range_note(pilot, ref, n, m, half):
    """In plain words what the paired-gain range m +- half (fractions of a score, over n paired games; the range itself is printed by range_points just before) does
    and does not include; never waves a wide range away."""
    glo, ghi = m - half, m + half
    if ghi - glo >= 2:
        return f"That range is wider than the whole possible scale (-100 to +100 points): {plural(n, 'paired game')} are too few to say anything about the gain yet."
    glo, ghi = max(-1.0, glo), min(1.0, ghi)
    if glo <= 0 <= ghi:
        return (f"That range includes no gain at all: these {n} paired games do not show that {pilot} plays this deck "
                f"better than {ref}, and do not show that it plays it worse. They do argue against a gain much larger than {100 * ghi:.1f} points or a loss much larger "
                f"than {100 * abs(glo):.1f} points; a smaller difference needs more deals.")
    only_just = (' (only just: its nearer end is less than 0.05 points from no gain)' if 0 <= round(100 * min(abs(glo), abs(ghi)), 1) < 0.1 else '')
    return (f"That range does not include no gain{only_just}: on these {n} paired games {pilot} did "
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


SELFCHECK_HOW = (('given', 'copied from the pin, not replayed: the pin says it was measured on this exact binary'),
                 ('replayed by slow_report', 'replayed on the registering machine just before registration, equal to the committed pin'),
                 ('run by strength_prereg', 'replayed at registration'))


def selfcheck_how(source, pin_state=None, record=None):
    """How a self-check text came to be in the registration, for the page. `record` (the registration's selfcheck_record) says it was accepted from a committed record of an earlier replay, and
    then the manifest's own source line ('replayed ... just before registration', which strength_prereg.py writes for every text it is told was replayed) is not what happened."""
    if isinstance(record, dict) and record.get('path'):
        text = (f"accepted from the committed record `{record['path']}` (commit {str(record.get('commit'))[:12]}): replayed there by slow_report.py on "
                f"{record.get('host') or 'a machine not recorded'} at {record.get('replayed_at') or 'a time not recorded'} on a program with this sha256, equal to the committed pin; "
                'the record is a committed file, not signed, and this registration did not replay them again')
        return text if pin_state == 'yes' else text.replace('the committed pin', 'the pin file in use (NOT the committed pin: test use)')
    for prefix, text in SELFCHECK_HOW:
        if (source or '').startswith(prefix):
            return text if pin_state == 'yes' else text.replace('the committed pin', 'the pin file in use (NOT the committed pin: test use)')  # (a state that is missing is not "yes" either)
    return 'recorded at registration'


def write_slow_report(rundir, out=None, pin_check=None):
    """The page SLOW_REPORT.md of a registered run. `pin_check` = (pin, pin_path) also asks the pin in use whether the registration's claims about the program are its own (see
    pin_provenance_problems); the page flags what does not hold."""
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
    P('## What it says\n')
    paired_on = bool(sr.get('paired'))
    planned_x = len(panel) * deals * 2
    if paired_on:
        P(f'Question: how does {deck} do when {pilot} plays it against the {k} public lists, and is that better than when {ref} plays the same deck on the same deals?\n')
    else:
        P(f'Question: how does {deck} do when {pilot} plays it against the {k} public lists?\n')
    if partial:  # after the question, before any size or number
        P(f"**PARTIAL: {kg(len(xg), pilot)} + {kg(len(rg), ref, True)} so far ({len(games)} of the {planned} games planned; both pilots' games count in the {planned}). "
          f"The numbers below will move; read them as a snapshot.**\n")
    if errors:
        n = len(errors)
        every = any(a >= 2 for _, a, _ in errors)
        key, att, msg = errors[0]
        P(f"{n} game{'' if n == 1 else 's'} could not be finished and {'is' if n == 1 else 'are'} left out of every number below (first: `{key}`, {att} {'try' if att == 1 else 'tries'}: {msg}). "
          f"A game that crashes is not a loss, so if the same card crashes {'them' if n > 1 else 'it'} the score leans towards games without it. "
          + ('At least one failed every time it was tried, so resuming will not fix it.' if every else f"A resumed run tries {'them' if n > 1 else 'it'} again.") + '\n')
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
                P(head + f', {range_points(m, half)} (95% interval; this range refers to those {plural(n, "paired game")}).\n')
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
          f"less than the width of such a range ({wilson_width_points(lo, hi)} points here), and more deals narrow it.")
        P(f"- There is no pass or fail line: whether {deck} is worth playing is a call for the player.\n")

    P('## What was run\n')
    P(f"- Pilots: {sr['pilot_label']} on the deck, {sr['reference_label']} on {sr['panel_label']}. Program `{man.get('program')}` sha256 `{str(man.get('program_sha256'))[:12]}`.")
    for problem in manifest_provenance_problems(man) + (pin_provenance_problems(man, *pin_check) if pin_check else []):  # (a resume refuses such a registration; a page made of it says so)
        P(f"- **What the registration says about the program does not hold**: {problem}. This page reports whatever program ran; it is not a report on the pinned build.")
    if sr.get('program_route') == 'rebuilt':
        host_ = f" ({sr['registered_on']})" if sr.get('registered_on') else ''
        rr_ = sr.get('selfcheck_record') if isinstance(sr.get('selfcheck_record'), dict) else None
        replayed_ = (f"were replayed earlier by slow_report.py (committed record `{rr_.get('path')}`, commit {str(rr_.get('commit'))[:12]}, on {rr_.get('host') or 'a machine not recorded'})" if rr_
                     else f"were replayed on the registering machine{host_}")
        P(f"- The program is NOT the pinned binary (`{sr.get('pinned_program')}`, sha256 `{str(sr.get('pinned_program_sha256'))[:12]}`): its build record says it is a rebuild of the pinned source, and it was accepted only because "
          f"that record has the pinned engine tree and harness source and both self-checks {replayed_} and equal {pin_digests(sr.get('pin_committed'))}, "
          f"and the harness source in the checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those replayed self-checks "
          f"(12 fixed games per pilot), not the record.")
        rec_ = sr.get('build_record') or {}
        if rec_:
            P(f"- Build record `{os.path.basename(record_text(rec_, 'record_file'))}` sha256 `{str(rec_.get('record_sha256'))[:12]}`: engine {record_text(rec_, 'engine_arg')} -> tree as archived "
              f"`{str(rec_.get('engine_tree_archived'))[:12]}` (the pin's is `{str(sr.get('engine_tree'))[:12]}`), harness source `{str(rec_.get('harness_source_sha256'))[:12]}`, "
              f"{rustc_line(rec_, 'rustc not recorded')}, {record_text(rec_, 'cargo')}, built {record_text(rec_, 'built_at')} on {record_text(rec_, 'host')} ({record_text(rec_, 'machine')}); "
              f"to rebuild the same bytes after a restart: `{record_text(rec_, 'rebuild_command')}`.")
    if sr.get('pin_committed'):
        P(f"- Pin `{sr['pin']['path']}` sha256 `{sr['pin']['sha256'][:12]}`: " + (
            'committed (byte-equal to HEAD\'s file in the repository this run was registered from).' if sr['pin_committed'] == 'yes' else
            f"**NOT the committed pin** ({sr.get('pin_committed_detail') or sr['pin_committed']}): what this page says about the program rests on a pin that is not the committed one."))
    nr = lambda v: str(v)[:12] if v else 'not recorded'  # a line without these entries (hand-made, or from an older version) never prints the text None
    in_use, accepted = man.get('program_sha256'), {man.get('program_sha256')}
    log = load_jsonl(os.path.join(rundir, 'slow_report_log.jsonl'))
    legacy = log_started_for(log, msha)
    for e in log:  # in the order it happened; a line the run could not have written is not shown as a fact
        before = sum(1 for g in games if (g.get('started_at') or '') < (e.get('at') or ''))
        if is_program_change(e, man, msha, legacy):
            P(f"- **The program changed mid-run** ({e['at']}): sha256 `{nr(e.get('old_sha256'))}` -> `{nr(e.get('new_sha256'))}` after a restart or rebuild; its build record has the pinned engine tree and harness source "
              f"(record `{nr(e['build_record'].get('record_sha256'))}`) and both self-checks were replayed again on {e.get('replayed_on') or 'a machine not recorded'} and equal {pin_digests(e.get('pin_committed'))}. "
              f"{plural(before, 'game')} of the {len(games)} played so far were started before this change and {len(games) - before} after; the numbers above pool them.")
            in_use = e['new_sha256']
            accepted.add(in_use)
        elif (sr.get('program_route') == 'rebuilt' and e.get('event') == 'sitting_call' and isinstance(e.get('at'), str) and e['at'] and e.get('program_sha256') in accepted
              and e['program_sha256'] != in_use):  # a sitting that ran a build accepted before (no replay, no change logged)
            P(f"- **The program went back to an earlier accepted build** ({e['at']}): sha256 `{nr(in_use)}` -> `{nr(e['program_sha256'])}` (the registered program or one accepted before, so no new replay was needed); "
              f"{plural(before, 'game')} of the {len(games)} played so far were started before this and {len(games) - before} after.")
            in_use = e['program_sha256']
    for spec, txt in (man.get('selfcheck') or {}).items():
        P(f"- Self-check of `{spec}`: `{txt}` ({selfcheck_how((man.get('selfcheck_source') or {}).get(spec), sr.get('pin_committed'), sr.get('selfcheck_record'))})")
    if man.get('engine'):
        P(f"- Build: {man['engine']}")
    if sr.get('harness_source_sha256'):
        here_ = sr.get('harness_source_checkout_sha256')
        P(f"- Harness source sha256 `{sr['harness_source_sha256'][:12]}` (what rl/strength/build.sh prints); " + (
            'the checkout this run was registered from has the same.' if here_ == sr['harness_source_sha256'] else
            'the checkout this run was registered from has no harness source (rl/strength/src), so this could not be compared.' if not here_ else
            f"the checkout this run was registered from has `{here_[:12]}` (so the pinned binary was not built from exactly that source)."))
    if sr.get('school_rule'):
        days_ = sr.get('school_days')
        P(f"- School-morning rule: {sr['school_rule']}" + ((f" ({days_})" if days_ else ' (no school days, so it never pauses)' if days_ == '' else '') if sr['school_rule'] == 'on' else ' (chosen at registration, for a machine that is not the laptop)') + '.')
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
    """The lines worth echoing to the terminal: 'What it says' (the question first, then the PARTIAL banner and the error note when there are any, then the size and the
    numbers), without markdown."""
    out = []
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
    except NoTimeZoneDatabase as e:
        raise SystemExit(f"[{ctx['tag']}] REFUSED: {e}") from None
    except SystemExit as e:
        if isinstance(e.code, str) and not e.code.startswith('['):
            raise SystemExit(f"[{ctx['tag']}] {e.code}") from None
        raise


def selfcheck_only(a, pin, repo, say, now):
    """--selfcheck-only [--program PATH]: the replay of both self-checks on a rebuild of the pinned build, and nothing else is registered or played. Every checked thing a registration checks
    first is checked here (the committed pin, the build record, the harness source), the games are played one at a time and kept (run_selfcheck with a state folder), and when both texts equal the
    committed pin's the record of the replay is written for the runner to commit (keep_record): a registration of this exact program from a checkout that has the committed record then
    replays nothing. The pinned binary has nothing to replay. A committed record of this program that is already there is said, and nothing is replayed unless --selfcheck is given."""
    pin_state = require_committed_pin(repo, a.pin)
    program_path = os.path.abspath(a.program) if a.program else None
    route, program_sha = check_program(pin, program_path, repo)
    pin_run = ReplayPin(pin, program=program_path or pin['program'])
    if route == 'pinned':
        say(f"{pin_run['program']} (sha256 {program_sha[:12]}) is the pinned binary: its self-check texts are the pin's, measured on exactly this file, so there is nothing to replay and no record "
            'is needed (a registration with --selfcheck replays them anyway)')
        return 0
    build_rec = read_build_record(program_path, pin)
    specs = sorted({pin['pilot'], pin['reference']})
    school_rule = a.school_rule or 'on'
    school_days = parse_days(a.school_days if a.school_days is not None else DEFAULT_SCHOOL_DAYS)
    if school_rule == 'on' and school_days:
        chicago()  # fail now, with the clear message, not hours in (NoTimeZoneDatabase becomes a REFUSED in main)
    existing = None if a.selfcheck else committed_selfcheck_record(repo, program_sha, pin, specs)
    if existing:
        say(f"already recorded: the committed record `{existing['path']}` (commit {existing['commit'][:12]}) is for a program with this sha256 ({program_sha[:12]}) and has both self-check texts of "
            f"{pin_digests(pin_state['state'])}, so a registration of {pin_run['program']} replays nothing; nothing was replayed here (--selfcheck replays anyway)")
        return 0
    say(f"program {pin_run['program']} (sha256 {program_sha[:12]}) is NOT the pinned binary (sha256 {pin['program_sha256'][:12]}): its build record "
        f"({os.path.basename(build_rec['record_file'])}, sha256 {build_rec['record_sha256'][:12]}) says it is a rebuild of the pinned source; both self-checks "
        + ('would be' if a.dry_run else 'will be') + f" replayed on this machine against {pin_digests(pin_state['state'])} (hours for kx3), a game at a time unless --whole-selfcheck, and "
        f"recorded in {RECORDS_REL}/ when both equal it")
    if a.dry_run:
        say('dry run: nothing written')
        return 0
    deadline = selfcheck_deadline(school_rule, school_days, now)
    out_root = os.path.abspath(a.out_root) if a.out_root else os.path.join(repo, 'rl', 'results', 'slow_reports')
    routes = pin_run.routes = {}
    pin_run.state_dir, pin_run.whole = os.path.join(out_root, STATE_DIR_NAME), a.whole_selfcheck
    texts = {spec: run_selfcheck(pin_run, repo, spec, say, deadline=deadline, now=now)
             for spec in specs}
    refuse_if_program_changed(pin_run['program'], program_sha, 'Nothing was recorded.')
    say(f"both self-checks equal {pin_digests(pin_state['state'])}")
    return 0 if keep_record(repo, pin_run['program'], program_sha, texts, routes, now, say) else 1


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
    ap.add_argument('--date', help="YYYY-MM-DD for the run directory name (default: today in Chicago, or the UTC date on a machine without the time zone database)")
    ap.add_argument('--seed-base', type=int)
    ap.add_argument('--selfcheck', action='store_true', help='replay the pinned self-check games instead of recording the pinned text (hours for kx3), even when a committed record of the program has them')
    ap.add_argument('--program', help='a REBUILD of the pinned build made with rl/strength/build.sh (for example on the cloud), used instead of the pin\'s path; when its sha256 is not the pinned '
                                      'one it must have its build record (PROGRAM.build.json, written by build.sh) with the pinned engine tree and harness source, and both self-checks are '
                                      'replayed on this machine and must equal the committed pin\'s digests (this forces --selfcheck), unless a COMMITTED record of such a replay of a program '
                                      f'with this very sha256 is in {RECORDS_REL}/ (written by --selfcheck-only, or by any replay): then they are not replayed again')
    ap.add_argument('--selfcheck-only', action='store_true',
                    help=f'replay both self-checks of --program PATH (a rebuild of the pinned build) and register nothing: a game at a time, kept as it ends (a restart goes on from the next game), and, '
                         f'when both equal the committed pin, write their record in {RECORDS_REL}/ for the runner to commit; a registration of that exact program (sha256) from a checkout that has the '
                         f'committed record then replays nothing. Takes no deck file and no --dir')
    ap.add_argument('--whole-selfcheck', action='store_true',
                    help='replay the 12 self-check games of each pilot in one run of the program, as before (not resumable), instead of a game at a time; a game that cannot be taken apart again '
                         'falls back to this by itself. Says how, not whether: a committed record of the program is still taken (--selfcheck replays regardless)')
    ap.add_argument('--register-only', action='store_true')
    ap.add_argument('--report-only', action='store_true', help='with --dir: write the page from the games so far and play nothing')
    ap.add_argument('--dry-run', action='store_true', help='print the plan (or, with --dir, where the run stands); write nothing')
    ap.add_argument('--school-rule', choices=('on', 'off'), help='the school-morning rule (default on at registration; a resume keeps the registered choice). Off for a machine that is not the laptop, e.g. the cloud')
    ap.add_argument('--school-days', help=f'the school days (default {DEFAULT_SCHOOL_DAYS} at registration; a resume keeps the registered choice)')
    ap.add_argument('--max-games', type=int, help='play at most this many games in this call (counted across both arms: about half of them kx3 games), then write the page and stop')
    ap.add_argument('--poll-s', type=float, default=20.0)
    a = ap.parse_args(argv)
    now = now or (lambda: datetime.datetime.now(UTC))
    sleep = sleep or time.sleep
    spawn = spawn or default_spawn
    deck_check = deck_check or default_deck_check
    repo = os.path.abspath(a.repo)
    pin = load_pin(a.pin)
    _LOG_EXTRA.update(pilot=pin['pilot'], reference=pin['reference'])
    ctx['tag'] = f"{pin['pilot_label']} v {pin['reference_label']}"
    if a.school_days is not None:
        parse_days(a.school_days)  # refuse a bad day name before anything else

    def say(msg):
        print(f"[{ctx['tag']}] {msg}", flush=True)

    if a.selfcheck_only:
        if a.deckfile or a.dir or a.register_only or a.report_only:
            die('--selfcheck-only replays the self-checks of a program and writes their record; it takes no deck file, no --dir and no --register-only or --report-only')
        return selfcheck_only(a, pin, repo, say, now)
    if a.dir and a.deckfile:
        die('give a deck file or --dir, not both')
    if not a.dir and not a.deckfile:
        die('give a deck file to report on, or --dir RUNDIR to resume a registered run')

    if a.dir:
        for flag, given in (('--deals', a.deals is not None), ('--no-paired', a.no_paired), ('--date', a.date is not None), ('--seed-base', a.seed_base is not None),
                            ('--selfcheck', a.selfcheck), ('--register-only', a.register_only), ('--program', a.program is not None)):
            if given:
                die(f'{flag} belongs to a new registration; a run that is already registered keeps what it was registered with, so it cannot be used with --dir')
        rundir = os.path.abspath(a.dir)
        man, msha = load_registered(rundir)
        if not man.get('slow_report'):
            die(f'{rundir} is not a slow report run (its manifest has no slow_report block)')
        ctx['tag'] = man['slow_report']['headline']
        _LOG_EXTRA.update(pilot=man['pilot'], reference=man['reference'])
        claims = manifest_provenance_problems(man) + pin_provenance_problems(man, pin, a.pin)  # what the registration says about the program must agree with itself and with its pin (a --report-only writes the page and flags it instead)
        if claims and not a.report_only:
            die('REFUSED: what the registration says about the program does not hold, so nothing is run: ' + '; '.join(claims) + '. This is not a slow report of the pinned build; register a new run.')
        reg_days = man['slow_report'].get('school_days')
        reg_rule = man['slow_report'].get('school_rule') or 'on'
        reg_days_text = reg_days if reg_days is not None else DEFAULT_SCHOOL_DAYS
        school_rule = a.school_rule or reg_rule
        school_days_text = a.school_days if a.school_days is not None else reg_days_text  # '' is a choice (no school days), not "unset"
        # logged as an override only when it differs from what was registered: running exactly the printed resume command is not one
        school_choice_overridden = school_rule != reg_rule or set(parse_days(school_days_text)) != set(parse_days(reg_days_text))  # the days, not their spelling or order (MON, TUE = tue,mon)
    else:
        if a.report_only:
            die('--report-only needs --dir RUNDIR (a run that is already registered)')
        school_rule = a.school_rule or 'on'
        school_days_text = a.school_days if a.school_days is not None else DEFAULT_SCHOOL_DAYS
        school_choice_overridden = False
        pin_state = require_committed_pin(repo, a.pin)  # before anything below trusts the pin
        program_path = os.path.abspath(a.program) if a.program else None
        route, program_sha = check_program(pin, program_path, repo)
        build_rec = read_build_record(program_path, pin) if route == 'rebuilt' else None  # a rebuild must come with the record of what was archived and compiled
        pin_run = ReplayPin(pin, program=program_path or pin['program'])  # the pin as this run uses it: the program's path may be a rebuilt copy's
        harness_here = harness_source_sha256(repo)
        deck_abs = os.path.abspath(a.deckfile)
        name = deck_name_of(deck_abs)
        ctx['tag'] = headline_of(pin, name)
        deals = 5 if a.deals is None else a.deals
        if not 1 <= deals <= MAX_DEALS:
            die(f'REFUSED: --deals must be between 1 and {MAX_DEALS}')

    school_days = parse_days(school_days_text)
    if school_rule == 'on' and school_days and not a.report_only:
        chicago()  # fail now, with the clear message, not on the first school-morning check hours into a run (NoTimeZoneDatabase becomes a REFUSED in main)
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
        reserved = pin.get('seed_reserved') or []
        seed_base = pick_seed_base(dsha, out_root, tuple(pin['seed_block']), pin['seed_step'], a.seed_base, reserved)
        date = a.date if a.date is not None else local_date(now())
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
        pilot_, ref_ = pin['pilot'], pin['reference']
        say(f"question: how does {name} do when {pilot_} plays it against the {len(panel_names)} public lists" + (f', and is that better than when {ref_} plays the same deck on the same deals?' if not a.no_paired else '?'))
        for d_, played_, planned_, cmd_ in unfinished_runs(out_root, name):
            say(f"WARNING: an unfinished slow report of {name} already exists: {d_} ({played_} of {planned_} games played). Resume it ({cmd_}) "
                'instead of registering a second one, unless you mean to.')
        say(f"plan: {name} ({rel}, {state}), {plural(deals, 'deal')} x 2 seats against the {len(panel_names)} public lists")
        say(f"size: {kg(et['kx3_games'], pilot_)} + {kg(et['kx3_games'], ref_, True)} on the same deals ({2 * et['kx3_games']} games in all; the {ref_} games take about "
            f"a second each{'; with --no-paired they are still played and the page leaves them out' if a.no_paired else ''}); "
            f"the time is for the {kg(et['kx3_games'], pilot_)}: about {hours_text(et['typical_hours'][0])} to "
            f"{hours_text(et['typical_hours'][1])} if the deck plays like most of his, about {hours_text(et['wall_hours'])} if it plays like the Wailord wall (measured with 2 games at a time)")
        if school_rule == 'on' and school_days:
            say(f'on school days ({school_days_text}) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer')
        elif school_rule == 'on':
            say('school-morning rule: on, but with no school days set it never pauses the run')
        else:
            say('school-morning rule: OFF for this run (it never pauses for school mornings; the choice is recorded in the registration and carried by the resume command)')
        specs = sorted({pin['pilot'], pin['reference']})
        # a rebuild whose very sha256 has a COMMITTED record of both self-checks replayed, equal to the committed pin's texts, is not replayed again (--selfcheck replays regardless)
        record = committed_selfcheck_record(repo, program_sha, pin, specs) if route == 'rebuilt' and not a.selfcheck else None
        replay = (a.selfcheck or route == 'rebuilt') and record is None
        say(f"pin committed: {pin_state['state']} (rl/strength/slow_report_pin.json sha256 {pin_state['sha256'][:12]}" + ('; byte-equal to HEAD' if pin_state['state'] == 'yes' else f"; {pin_state['detail']}") + ')')
        if route == 'rebuilt':
            checked = (f"both self-checks will be accepted from the committed record {record['path']} (commit {record['commit'][:12]}), made for a program with this sha256: nothing is replayed"
                       if record else
                       f"both self-checks will be replayed on this machine against {pin_digests(pin_state['state'])} before anything is registered (hours for kx3)")
            say(f"program {pin_run['program']} (sha256 {program_sha[:12]}) is NOT the pinned binary (sha256 {pin['program_sha256'][:12]}): its build record "
                f"({os.path.basename(build_rec['record_file'])}, sha256 {build_rec['record_sha256'][:12]}) says it is a rebuild of the pinned source (engine tree as archived {build_rec['engine_tree_archived'][:12]}, "
                f"harness source {build_rec['harness_source_sha256'][:12]}, built with {rustc_line(build_rec, 'an unrecorded toolchain')}); {checked}, "
                f"and the checkout's harness source equals the pinned build's")
        say(f"stage use (not development evidence; the held-out lock is untouched), seeds from {seed_base}, program {pin_run['program']} "
            f"({'pinned' if route == 'pinned' else 'rebuilt'}, sha256 {program_sha[:12]}), "
            f"{'without' if a.no_paired else 'with'} the comparison with {ref_} on the same deals in the page, no pass or fail line")
        if a.dry_run:
            say('dry run: nothing written')
            return 0
        given, how = 'pin', 'pin'
        made_root = not os.path.exists(out_root)
        if record:
            given, how = {spec: pin['selfcheck'][spec] for spec in specs}, 'replayed'  # (strength_prereg.py takes a rebuild's texts only so; build_config names the record)
            say(f"self-check: accepted from the committed record `{record['path']}` (commit {record['commit'][:12]}): replayed by slow_report.py on {record.get('host') or 'a machine not recorded'} "
                f"at {record.get('replayed_at') or 'a time not recorded'} on a program with this sha256, and equal to {pin_digests(pin_state['state'])}; not replayed again")
        elif replay:
            deadline = selfcheck_deadline(school_rule, school_days, now)
            routes = pin_run.routes = {}
            pin_run.state_dir, pin_run.whole = os.path.join(out_root, STATE_DIR_NAME), a.whole_selfcheck
            given, how = {spec: run_selfcheck(pin_run, repo, spec, say, deadline=deadline, now=now)
                          for spec in specs}, 'replayed'
            if route == 'rebuilt':
                refuse_if_program_changed(pin_run['program'], program_sha, 'Nothing was recorded or registered.')  # (a record names the program by its sha256: it is written only for the bytes that were replayed)
                keep_record(repo, pin_run['program'], program_sha, given, routes, now, say)
            if os.path.exists(rundir):  # hours may have passed: what was decided before the self-check is decided again
                die(f'REFUSED: the run directory {rundir} appeared while the self-check ran; resume it with --dir {shlex.quote(rundir)} (or pick another --date)')
            again = pick_seed_base(dsha, out_root, tuple(pin['seed_block']), pin['seed_step'], a.seed_base, reserved)
            if again != seed_base:
                say(f'note: seed slot {seed_base} was taken while the self-check ran; using {again}')
                seed_base = again
        cfg = build_config(pin=pin, pin_path=a.pin, deck_rel=rel, deck_name=name, deck_sha=dsha, deck_state=state, deals=deals, paired=not a.no_paired, seed_base=seed_base,
                           threads=threads, program_sha=program_sha, selfcheck_given=given, selfcheck_how=how,
                           resume_command=resume_command_for(rundir, school_rule, school_days_text), program=pin_run['program'], route=route,
                           harness_checkout=harness_here, school_rule=school_rule, school_days=school_days_text, pin_state=pin_state, build_record=build_rec,
                           registered_on=socket.gethostname(), selfcheck_record=record)

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
            say(f"play it with: {man['slow_report'].get('resume_command') or resume_command_for(rundir, school_rule, school_days_text)} (add --max-games N to play in slices)")
            return 0

    sr_block = man['slow_report']
    resume_cmd = sr_block.get('resume_command') or resume_command_for(rundir, school_rule, school_days_text)
    if a.dir and a.dry_run:
        keys = planned_keys(man)
        planned_x, planned_r = sum(1 for k in keys if k.endswith('|X')), sum(1 for k in keys if k.endswith('|ref'))
        done = {g['key'] for g in load_games(rundir)}
        have_x, have_r = sum(1 for k in done if k.endswith('|X')), sum(1 for k in done if k.endswith('|ref'))
        problems = verify_inputs(man, accepted_program_shas(rundir, man))
        program_only = program_only_problem(man, problems)  # the same test the real resume makes below
        finished = have_x + have_r >= len(keys)
        if problems and not program_only:
            status = 'it would be refused: ' + '; '.join(problems) + ('; every game is played, so --report-only writes the page from them' if finished else '')
        elif finished:
            status = 'complete'
        elif program_only:
            try:
                st_, _rec, _deadline = check_program_change(man, pin, a.pin, repo, school_rule, school_days, now)  # the checks the real resume makes before it replays anything
                status = (f"the program at {man['program']} has another sha256 than registered; its build record is for the pinned source, so a resume would replay both self-checks again "
                          f"against {pin_digests(st_['state'])} (hours for kx3) and, if they match, go on and log it as 'program changed mid-run'; resume with: {resume_cmd}")
            except SystemExit as e:
                status = 'it would be refused: ' + re.sub(r'^REFUSED: ', '', str(e.code))
        else:
            status = 'resume with: ' + resume_cmd
        say(f"question: how does {sr_block['deck_name']} do when {man['pilot']} plays it against the {len(man['opponents'])} public lists" + (f", and is that better than when {man['reference']} plays the same deck on the same deals?" if sr_block.get('paired') else '?'))
        say(f"played so far: {kg(have_x, man['pilot'])} + {kg(have_r, man['reference'], True)} of {kg(planned_x, man['pilot'])} + {kg(planned_r, man['reference'], True)} planned; "
            f"{kg(planned_x - have_x, man['pilot'])} + {kg(planned_r - have_r, man['reference'], True)} to go ({status})")
        say('dry run: nothing written')
        return 0

    if a.dir and sr_block.get('pin', {}).get('sha256') and os.path.isfile(a.pin) and sha(a.pin) != sr_block['pin']['sha256']:
        say('note: the pin file has changed since this run was registered; the run continues with the program, settings and scrub list it was registered with')
    if not a.report_only:
        accepted = accepted_program_shas(rundir, man)
        problems = verify_inputs(man, accepted)
        # a program of another sha256 is not fatal on a run registered on the rebuilt route (below, once this call holds the lock); anything else wrong is
        program_only = program_only_problem(man, problems)
        keys_, done_ = planned_keys(man), {g['key'] for g in load_games(rundir)}
        finished = sum(1 for k in done_ if k.endswith('|X')) + sum(1 for k in done_ if k.endswith('|ref')) >= len(keys_)
        if problems and not program_only:
            die('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  ' + '\n  '.join(problems)
                + ('\n  Every game is played: --report-only writes the page from them without these files.' if finished else ''))
        if program_only and finished:
            # nothing is left to play: the page is written from the games, so a replay of both self-checks (hours for kx3) and a 'program changed' note would be for nothing
            say(f"all {len(keys_)} games are played, so nothing is run: the program at {man['program']} has another sha256 than registered, which the page does not depend on "
                '(no self-check is replayed and no program change is logged)')
        else:
            lock = acquire_lock(rundir, say)
            try:
                if program_only:
                    accepted = set(accepted) | {reverify_program(rundir, man, pin, a.pin, repo, say, school_rule, school_days, now, whole=a.whole_selfcheck)}
                    problems = verify_inputs(man, accepted)
                    if problems:
                        die('REFUSED: the files this run was registered with are not the ones on disk, so nothing is run:\n  ' + '\n  '.join(problems))
                log_event(rundir, 'sitting_call', school_rule=school_rule, school_days=school_days_text, threads=a.threads or man.get('threads') or pin['threads'], max_games=a.max_games,
                          school_choice_overridden=school_choice_overridden, program_sha256=sha(man['program']) if os.path.isfile(man['program']) else None)
                try:
                    status = run_games(rundir, man, sr_block.get('scrub_env_prefixes') or pin['scrub_env_prefixes'],
                                       threads=a.threads or man.get('threads') or pin['threads'], max_games=a.max_games, accepted_shas=accepted,
                                       school_on=school_rule == 'on', school_days=school_days, now=now, sleep=sleep, spawn=spawn, poll_s=a.poll_s, say=say)
                except (SystemExit, KeyboardInterrupt):
                    best_effort_pages(rundir, say)
                    raise
            finally:
                release_lock(lock)
            if status == 'limit':
                say(f'stopped after --max-games {a.max_games} (games across both arms, about half of them kx3 games); resume with: {resume_cmd}')
    # the engineering report (REPORT.md) first, so the page can point at it; a failure there never blocks the page
    rr = subprocess.run([sys.executable, '-B', REPORT, '--dir', rundir], capture_output=True, text=True)
    if rr.returncode != 0:
        say('REPORT.md (the engineering report) could not be written: ' + (rr.stderr.strip().splitlines() or ['no message'])[-1])
    text = write_slow_report(rundir, pin_check=(pin, a.pin))
    log_event(rundir, 'report_written', path=os.path.join(rundir, 'SLOW_REPORT.md'))
    say(f'SLOW_REPORT.md written in {rundir}')
    for line in console_lines(text):
        say(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
