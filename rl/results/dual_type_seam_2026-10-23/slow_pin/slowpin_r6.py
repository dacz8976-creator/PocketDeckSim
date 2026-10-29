#!/usr/bin/env python3
"""The slow report's re-pin ON MAIN for R6, after its replay check passed: kx3's frozen files on main-affe56e's engine (VARS["f_commit"] = S).

  slowpin_r6.py VARS.json [--replace] [--dry-run]

Dustin, Oct 21 (verbatim, relayed by the coordinator): "Move the slow-report program only after its replay check passes. Until then, its
reports must clearly identify the old engine." The replay check's record (rl/results/kx3_on_r6_2026-10-29/: SPEC.md, the registrations, the
games, COMPARE_DEV.txt, LANE_RECORD.txt, and READING.md with "**Verdict: pass.**") must be on VARS["check_branch"] at VARS["check_commit"],
on origin, with the reviewed pre-game commit PREGAME (b3de3e28, fixed here; VARS["check_pregame"], if given, must name it) in its history,
holding no registration, game or result, and none of its files changed since. This refuses unless READING.md says the check passed AND
COMPARE_DEV.txt shows SPEC.md section 4's pass condition (202 of 202 kx3 and 202 of 202 km3 games equal, nothing missing, compare_dev.py's
RESULT line, each header exactly this check's registration) AND the record is the lane's, in the lane's order: after PREGAME, one line of
commits: the three registrations alone (each manifest.json: both self-checks equal to the pin's texts and run by strength_prereg.py, this
program and its sha256, K and its engine tree, the planned games, the pre-game commit, the 14 files' development-run sha256, and its
manifest.sha256), then the games with COMPARE_DEV.txt and LANE_RECORD.txt (each games.jsonl holding the games its header counts;
LANE_RECORD.txt ending in the lane's own lines: this program, its build record, compare_dev.py's exit status 0), then READING.md alone.
The counts the texts quote are the ones read from COMPARE_DEV.txt. The night job's self-checks are tied to this program by night.log
(the build's "RECORD OK <program sha256>" line, then both self-check lines).

One merge commit from a private index, nothing checked out, main and every working tree untouched, nothing pushed: first parent VARS["base"]
(main; it must be origin/main), second parent the check's commit (its branch starts on main and adds only its folder, so the merge brings
exactly that folder). It also changes rl/strength/slow_report_pin.json (program, its sha256 twice, harness_source_sha256 (R6 changed the
harness: c4f7da21, main's), engine_ref, engine_tree, pilot_label, engine, pilot_provenance, reference_provenance; the self-check texts and
every other field stay), make_predictions.py's CURRENT_ENGINE (the new harness tree), and turns R6's "until the re-pin" texts into the
re-pin's: rl/strength/README.md, rl/RUN5.md, CLAUDE.md, START_HERE.md, project_manifest.json (available_release.purpose, one sentence),
rl/engine-2026-10-29/README.md, and dated pointers in the release's RELEASE_NOTES.md and RELEASE_CHECKLIST.md. It adds
rl/results/dual_type_seam_2026-10-23/slow_pin/ (CERT.md, the build record, the self-check lines, this generator). Every old text is
matched exactly (once(), or a whole span by its sha256), so any drift refuses.

Lazy fetches are off in every run (GIT_NO_LAZY_FETCH=1): a missing object in this blob:none clone refuses instead of fetching.
--dry-run makes no ref and writes nothing into the repository: its objects and index go to a temporary folder (GIT_OBJECT_DIRECTORY, with
the repository's objects as an alternate). It reports what a real run would refuse and goes on, writes every new or changed text file, a
unified diff of each against the base, the diff list and the commit message to VARS["dump"] (default /home/dacz8976/relplan/slowpin_dump/,
emptied first), and prints the diff list. Every guard is an explicit exit or need(), never an assert (python -O would drop those).
Adapted from the Oct 22 generator rl/results/engine_candidate_2026-10-20/release/tools/slowpin_main.py."""
import datetime, difflib, hashlib, json, os, re, shutil, subprocess, sys, tempfile, textwrap

REPO = '/home/dacz8976/pincand'
REL = 'rl/results/dual_type_seam_2026-10-23'
REC = REL + '/slow_pin'
CHECK = 'rl/results/kx3_on_r6_2026-10-29'
PREGAME = 'b3de3e2841f9bc0a655d440d523c39ee2b38c277'  # the reviewed pre-game commit: SPEC.md, rows, reach, configs and scripts (before any game)
DEV = 'rl/results/strength_2026-10-03_kx3_dev'  # the development run the check replays (its manifest.json: the 14 files' sha256)
HARN ='c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149'  # rl/strength/src/*.rs + Cargo.toml at S (and main since R6)
PSHA = '23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378'  # SPEC.md section 1: any other program is a stop
REC_SHA = '0b0b07fa8e4e621ae0c736f0b622d02b563608633becfa27f57ccd3d5b09cdd1'  # SPEC.md section 1: the build record's sha256
OLD = dict(program='/home/dacz8976/kx_r3/strength', sha='7d046b6f9c1dcd9a9a834c2995bad256bc784e804ea08d351878e035cb24d319',
           ref='87a7f3404263e1bfe76e8765ba8dd94695e19cfe', tree='64de03e2c3c25b8371e9b87c5727d1f93ec70c30',
           harn='bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e', label='kx3 (d513e37b, on main-4d48844)')
PILOT = 'd513e37b'  # claude/playout-pilot, the frozen kx3
KX3_FILES = ('engine/examples/playout_smoke.rs', 'engine/src/players/mod.rs', 'engine/src/players/playout_player.rs',
             'engine/src/players/playout_pool.rs', 'engine/tests/playout_pilot_extra_lists_test.rs', 'engine/tests/playout_pilot_test.rs')
SC = dict(km3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1',
          kx3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')
EXPECT_GAMES = 202  # SPEC.md section 4: every one of the 202 kx3 and 202 km3 games equals the development run's
REGS = {'replay_a': 192, 'replay_b': 192, 'replay_c': 20}  # SPEC.md section 2: planned games (kx3 + km3) per registration
# the slow reports on main; the texts below say none was made on the main-4d48844 program (Oct 22 to the re-pin)
KNOWN_REPORTS = ('2026-10-08_draft-A-wallace', '2026-10-09_brew-08-entei-rainbow-cave', '2026-10-12_13-a-ninetales-raticate',
                 '2026-10-12_brew-07-hoopa-darkrai-sableye', '2026-10-12_brew-09-sableye-obstagoon', '2026-10-12_draft-D-entei-grimhound',
                 '2026-10-13_12-ariados-whimsicott-ogerpon', '2026-10-13_brew-10-diancie-giratina', '2026-10-14_brew-08-entei-rainbow-cave',
                 '2026-10-14_draft-A-wallace')
SLOW_REPORTS_SINCE = '2026-10-22'  # the old program's pin: no commit on any ref may touch rl/results/slow_reports/ from then on
DRY = '--dry-run' in sys.argv
GENV = {'GIT_NO_LAZY_FETCH': '1'}  # extra environment for every git call: no lazy fetch ever (and the dry run's private object folder)


def git(*a, env=None, inp=None, ok=False):
    e = dict(os.environ, **GENV, **(env or {}))
    r = subprocess.run(['git', '-C', REPO, *a], capture_output=True, input=inp, env=e)
    if ok:
        return r
    if r.returncode:
        sys.exit(f'git {" ".join(a)} failed: {r.stderr.decode()}')
    return r.stdout


def gs(*a, **k):
    return git(*a, **k).decode().strip()


def need(cond, why):  # a dry run reports what a real run would refuse, and goes on
    if not cond:
        if DRY:
            print(f'DRY RUN: a real run would refuse here: {why}')
        else:
            sys.exit(why)


def must(cond, why):  # an explicit refusal in every run (not an assert: python -O would drop it)
    if not cond:
        sys.exit(why)


def once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f'{what}: the old text occurs {n} times, not once: {old[:90]!r}')
    return text.replace(old, new)


def swap(text, start, end, sha, new, what):
    """Replace the one span that starts with `start` and ends with the first `end` after it; the span must be the text this was written
    for (its sha256), so any drift refuses."""
    n = text.count(start)
    if n != 1:
        sys.exit(f'{what}: the start occurs {n} times, not once: {start[:90]!r}')
    i = text.index(start)
    j = text.find(end, i + len(start))
    if j < 0:
        sys.exit(f'{what}: no end {end[:40]!r} after the start')
    j += len(end)
    got = hashlib.sha256(text[i:j].encode('utf-8')).hexdigest()
    if got != sha:
        sys.exit(f'{what}: the old text is not the one this was written for (sha256 {got[:16]}, want {sha[:16]})')
    return text[:i] + new + text[j:]


def compare_counts(text, check=CHECK):
    """COMPARE_DEV.txt (compare_dev.py's output): per arm, games / equal / anything else, summed over the three registrations. Each
    registration's header must be exactly compare_dev.py's for this check's folder: '=== <check>/replay_<s>: N games (planned N)'."""
    arms = {a: [0, 0, 0] for a in ('kx3', 'km3')}
    lines = re.findall(r'^  (kx3|km3): (\d+) games; equal (\d+); differ (\d+); not in the development run (\d+); seed differs (\d+)$', text, re.M)
    for a, g, e, d, ni, sd in lines:
        arms[a][0] += int(g)
        arms[a][1] += int(e)
        arms[a][2] += int(d) + int(ni) + int(sd)
    heads = re.findall(r'^=== .*$', text, re.M)
    want = [f'=== {check}/{r}: {n} games (planned {n})' for r, n in REGS.items()]
    ok = (len(lines) == 6 and heads == want
          and 'MISSING' not in text and 'changed row' not in text
          and text.rstrip().splitlines()[-1:] == ['RESULT: every changed game is in a named row']
          and all(arms[a][0] == arms[a][1] == EXPECT_GAMES and arms[a][2] == 0 for a in arms))
    return arms, ok


def pregame_problems(pre, check=CHECK):
    """The pre-game commit holds the spec and no registration, game, comparison, lane record or reading."""
    names = gs('ls-tree', '-r', '--name-only', pre, '--', check + '/').splitlines()
    late = [p for p in names if re.match(rf'{re.escape(check)}/(replay_|COMPARE_DEV\.txt$|LANE_RECORD\.txt$|READING\.md$)', p)]
    out = []
    if f'{check}/SPEC.md' not in names:
        out.append(f'the pre-game commit {pre[:8]} has no {check}/SPEC.md')
    if late:
        out.append(f'the pre-game commit {pre[:8]} already holds what comes after the games start: {late[:5]}')
    return out


def lane_problems(lane, prog, psha, recfile, rec_sha):
    """LANE_RECORD.txt: no STOP first line, and it ends exactly in write_record's own lines (the program, its build record, exit 0)."""
    lines = lane.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    want = ['== the program', f'{psha}  {prog}', '== its build record', f'{rec_sha}  {recfile}', '== compare_dev.py exit status: 0']
    out = []
    if not lane.startswith("The lane's record"):
        out.append("LANE_RECORD.txt is missing or its first line is not \"The lane's record\" (a STOP is written first)")
    if lines[-5:] != want:
        out.append(f'LANE_RECORD.txt does not end with the lane\'s own lines {want}: {lines[-5:]}')
    return out


def night_problems(text, psha):
    """night.log: the build's 'RECORD OK <program sha256>' line, then the km3 self-check line, then the kx3 one (rc 0), in that order.
    Returns (problems, the kx3 self-check's seconds)."""
    rows = text.split('\n')
    rec = [i for i, l in enumerate(rows) if re.fullmatch(r'\S+ strength rc=0 in \d+ s; RECORD OK ' + psha, l)]
    if not rec:
        return [f'night.log has no "strength rc=0 ...; RECORD OK {psha[:12]}…" line'], None
    km = [i for i, l in enumerate(rows) if i > rec[-1] and re.fullmatch(r'\S+ sc_km3: ' + re.escape(SC['km3']), l)]
    if not km:
        return ['night.log has no "sc_km3: <the pin text>" line after the build\'s RECORD OK line'], None
    for i, l in enumerate(rows):
        g = re.fullmatch(r'\S+ sc_kx3: rc/secs 0 (\d+): ' + re.escape(SC['kx3']), l)
        if g and i > km[0]:
            return [], g.group(1)
    return ['night.log has no "sc_kx3: rc/secs 0 <s>: <the pin text>" line after the km3 one'], None


def record_problems(C, pre, check, prog, psha, kref, tree):
    """The check's record at C is the lane's, in the lane's order (lane_kxr_r6.sh steps 1 and 4, then READING.md by the session):
    after the pre-game commit, one line of commits: the three registrations alone, then the games with COMPARE_DEV.txt and
    LANE_RECORD.txt, then READING.md alone (later commits may only change READING.md). Each registration's manifest.json: both
    self-checks equal to the pin's texts and run by strength_prereg.py, this program and its sha256, the engine ref and tree, the planned
    games, the pre-game commit, the 14 files' development-run sha256; its manifest.sha256 names it; its games.jsonl holds the planned
    games. Returns (problems, {'reg': commit, 'games': commit, 'reading': commit} as found)."""
    out, found = [], {}
    rp = re.compile(rf'{re.escape(check)}/replay_[abc]/[^/]+')
    revs = [r for r in gs('rev-list', '--reverse', f'{pre}..{C}').split() if r]
    seq, prev = [], pre
    for r in revs:
        if gs('log', '-1', '--format=%P', r).split() != [prev]:
            out.append(f'{r[:8]} is not a single-parent commit on {prev[:8]}: the check branch must be one line of commits after {pre[:8]}')
        seq.append((r, [tuple(l.split('\t', 1)) for l in gs('diff-tree', '-r', '--no-renames', '--no-commit-id', '--name-status', r).splitlines()]))
        prev = r
    roles = ('the registrations', 'the games, COMPARE_DEV.txt and LANE_RECORD.txt', 'READING.md alone')
    if len(seq) < 3:
        out.append(f'after the pre-game commit {pre[:8]} the check branch has {len(seq)} commit(s), not the lane\'s two and READING.md\'s: '
                   f'missing {", ".join(roles[len(seq):])}')
    if len(seq) >= 1:
        r, ch = seq[0]
        need_reg = {f'{check}/replay_{s}/{f}' for s in 'abc' for f in ('manifest.json', 'manifest.sha256')}
        bad = [c for c in ch if c[0] != 'A' or not rp.fullmatch(c[1]) or c[1].endswith('/games.jsonl')]
        if bad or not need_reg <= {c[1] for c in ch}:
            out.append(f'the first commit after {pre[:8]} ({r[:8]}) is not the three registrations alone (added manifest.json and manifest.sha256 '
                       f'in replay_a/b/c, no games.jsonl, nothing else): {bad[:4] or sorted(need_reg - {c[1] for c in ch})[:4]}')
        else:
            found['reg'] = r
    if len(seq) >= 2:
        r, ch = seq[1]
        need_g = {f'{check}/replay_{s}/games.jsonl' for s in 'abc'} | {f'{check}/COMPARE_DEV.txt', f'{check}/LANE_RECORD.txt'}
        bad = [c for c in ch if c[0] != 'A' or not (rp.fullmatch(c[1]) or c[1] in need_g)]
        if bad or not need_g <= {c[1] for c in ch}:
            out.append(f'the second commit after {pre[:8]} ({r[:8]}) is not the lane\'s record alone (added games.jsonl in replay_a/b/c, '
                       f'COMPARE_DEV.txt, LANE_RECORD.txt, nothing changed): {bad[:4] or sorted(need_g - {c[1] for c in ch})[:4]}')
        else:
            found['games'] = r
    if len(seq) >= 3:
        r, ch = seq[2]
        if ch != [('A', f'{check}/READING.md')]:
            out.append(f'the third commit after {pre[:8]} ({r[:8]}) is not "A {check}/READING.md" alone: {ch[:4]}')
        else:
            found['reading'] = r
        for r, ch in seq[3:]:
            if ch != [('M', f'{check}/READING.md')]:
                out.append(f'{r[:8]}, after READING.md was added, changes more than READING.md: {ch[:4]}')

    def at(path):
        x = git('show', f'{C}:{path}', ok=True)
        return x.stdout if x.returncode == 0 else None

    dt = at(f'{DEV}/manifest.json')
    if dt is None:
        out.append(f'the development run\'s {DEV}/manifest.json is not readable at {C[:8]}')
    dev = json.loads(dt or b'{}')
    devfiles = {x['name']: (x['path'], x['sha256']) for x in dev.get('decks', []) + dev.get('opponents', [])}
    for s in 'abc':
        reg = f'replay_{s}'
        mt = at(f'{check}/{reg}/manifest.json')
        if mt is None:
            out.append(f'{reg}/manifest.json is not at {C[:8]}')
            continue
        try:
            m = json.loads(mt)
        except ValueError as e:
            out.append(f'{reg}/manifest.json is not JSON: {e}')
            continue
        bad = []
        if m.get('selfcheck') != SC:
            bad.append(('selfcheck', m.get('selfcheck')))
        src = m.get('selfcheck_source') or {}
        if set(src) != set(SC) or set(src.values()) != {'run by strength_prereg.py'}:
            bad.append(('selfcheck_source', src))
        if m.get('program') != prog or m.get('program_sha256') != psha:
            bad.append(('program', m.get('program'), str(m.get('program_sha256'))[:12]))
        if m.get('planned_games') != REGS[reg]:
            bad.append(('planned_games', m.get('planned_games')))
        if f'{kref} engine tree {tree}' not in (m.get('engine') or ''):
            bad.append(('engine', str(m.get('engine'))[:80]))
        if m.get('repo_commit') != pre:
            bad.append(('repo_commit', m.get('repo_commit')))
        files = (m.get('decks') or []) + (m.get('opponents') or [])
        if not files or any(devfiles.get(x.get('name')) != (x.get('path'), x.get('sha256')) for x in files):
            bad.append(('a deck or list file is not the development run\'s', len(files)))
        st = at(f'{check}/{reg}/manifest.sha256')
        if st is None or st.decode('utf-8', 'replace') != f'{hashlib.sha256(mt).hexdigest()}  manifest.json\n':
            bad.append(('manifest.sha256', None if st is None else st[:20]))
        gt = at(f'{check}/{reg}/games.jsonl')
        rows = [l for l in (gt or b'').decode('utf-8', 'replace').split('\n') if l.strip()]
        if gt is None or len(rows) != REGS[reg] or any(not l.rstrip().endswith('}') for l in rows):
            bad.append(('games.jsonl', None if gt is None else len(rows), f'planned {REGS[reg]}'))
        if bad:
            out.append(f'{reg} at {C[:8]}: {bad}')
    return out, found


def today_names():
    out = set()
    now = datetime.datetime.now(datetime.timezone.utc)
    out.add(f'{now:%b} {now.day}')
    try:
        from zoneinfo import ZoneInfo
        loc = now.astimezone(ZoneInfo('America/Chicago'))
        out.add(f'{loc:%b} {loc.day}')
    except Exception:
        pass
    return out


def main():
    V = json.load(open(sys.argv[1]))
    tmp_objects = None
    if DRY:
        tmp_objects = tempfile.mkdtemp(prefix='slowpin_dry_objects_')
        objects = gs('rev-parse', '--path-format=absolute', '--git-path', 'objects')
        GENV.update(GIT_OBJECT_DIRECTORY=tmp_objects, GIT_ALTERNATE_OBJECT_DIRECTORIES=objects)
    try:
        run(V)
    finally:
        if tmp_objects:
            shutil.rmtree(tmp_objects, ignore_errors=True)


def run(V):
    base = gs('rev-parse', V['base'] + '^{commit}')
    need(gs('rev-parse', 'refs/remotes/origin/main') == base, f'origin/main is not the base {base[:8]}: the re-pin is one merge onto main as it is')
    K = gs('rev-parse', V['K'] + '^{commit}')
    kbr = V['kbranch']
    if gs('rev-parse', f'refs/heads/{kbr}') != K:
        sys.exit(f'{kbr} is not {K[:8]}')
    need(git('rev-parse', '-q', '--verify', f'refs/remotes/origin/{kbr}', ok=True).stdout.decode().strip() == K, f'origin/{kbr} is not {K[:8]}')
    F = gs('rev-parse', V['f_commit'] + '^{commit}')
    NAME = 'main-' + F[:7]
    FB, FTREE = F[:8], gs('rev-parse', F + ':engine')[:8]
    if sorted(gs('log', '-1', '--format=%P', K).split()) != sorted([OLD['ref'], F]):
        sys.exit(f'K is not the merge of the old kx3 build {OLD["ref"][:8]} and the built commit {FB}')
    if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', F, base], env=dict(os.environ, **GENV)).returncode:
        sys.exit(f'{NAME} is not on the base {base[:8]}: the engine is not adopted there')
    if gs('rev-parse', f'{base}:engine') != gs('rev-parse', f'{F}:engine'):
        sys.exit(f"main's engine/ is not {FB}'s: the re-pin needs main to carry S's engine (SPEC.md section 4)")
    T = gs('rev-parse', f'{K}:engine')
    # K = S + kx3's six files, each d513e37b's (and the old pin's) blob; rl/strength is S's
    if sorted(gs('diff', '--no-renames', '--name-only', F, K).splitlines()) != sorted(KX3_FILES):
        sys.exit(f'K differs from {FB} in more or other files than kx3\'s six')
    for f in KX3_FILES:
        b = gs('rev-parse', f'{K}:{f}')
        if b != gs('rev-parse', f'{OLD["ref"]}:{f}') or b != gs('rev-parse', f'{PILOT}:{f}'):
            sys.exit(f'{f}: K\'s blob is not {PILOT}\'s and the old pin\'s')
    if gs('rev-parse', f'{K}:rl/strength') != gs('rev-parse', f'{F}:rl/strength'):
        sys.exit(f"K's rl/strength is not {FB}'s")
    # the harness source the pin records must be main's own (build.sh's recipe: src/*.rs sorted the C way, then Cargo.toml)
    rs = sorted((p for p in gs('ls-tree', '--name-only', base, 'rl/strength/src/').splitlines() if p.endswith('.rs')), key=lambda p: p.encode())
    hsrc = hashlib.sha256(b''.join(git('cat-file', 'blob', f'{base}:{p}') for p in rs + ['rl/strength/Cargo.toml'])).hexdigest()
    if hsrc != HARN:
        sys.exit(f'the harness source on the base hashes to {hsrc[:12]}, not {HARN[:8]}')

    # ---- the replay check: its commits, its folder only, the comparison and READING.md's verdict ---------------------------------------
    C = gs('rev-parse', V['check_commit'] + '^{commit}')
    PRE = gs('rev-parse', PREGAME + '^{commit}')  # fixed here, never taken from VARS: a copy slip there must not move it
    if 'check_pregame' in V and gs('rev-parse', V['check_pregame'] + '^{commit}') != PRE:
        sys.exit(f"VARS check_pregame {V['check_pregame'][:12]} is not the reviewed pre-game commit {PRE[:8]}")
    pg = pregame_problems(PRE)
    if pg:
        sys.exit('; '.join(pg))
    need(git('rev-parse', '-q', '--verify', f"refs/remotes/origin/{V['check_branch']}", ok=True).stdout.decode().strip() == C,
         f"origin/{V['check_branch']} is not {C[:8]} (push the check's record first)")
    if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', PRE, C], env=dict(os.environ, **GENV)).returncode:
        sys.exit(f'the reviewed pre-game commit {PRE[:8]} is not in the check commit {C[:8]}\'s history')
    changed_after = gs('diff', '--no-renames', '--name-only', '--diff-filter=MDRT', PRE, C)
    if changed_after:
        sys.exit(f'files of the pre-game commit changed after it: {changed_after.splitlines()[:5]}')
    mb = gs('merge-base', base, C)
    touched = gs('diff', '--no-renames', '--name-only', mb, C).splitlines()
    if not touched or any(not p.startswith(CHECK + '/') for p in touched):
        sys.exit(f'the check branch touches more than its folder: {[p for p in touched if not p.startswith(CHECK + "/")][:5]}')
    if git('cat-file', '-e', f'{base}:{CHECK}', ok=True).returncode == 0:
        sys.exit(f'{CHECK} already exists on the base')

    def at_check(name):
        r = git('show', f'{C}:{CHECK}/{name}', ok=True)
        return r.stdout.decode('utf-8') if r.returncode == 0 else None

    prog = V['program']
    recfile = prog + '.build.json'
    reading = at_check('READING.md') or ''
    need(re.search(r'^\*\*Verdict: pass\.\*\*', reading, re.M), 'READING.md is missing or does not say "**Verdict: pass.**": no re-pin')
    comp = at_check('COMPARE_DEV.txt')
    arms, comp_ok = compare_counts(comp or '')
    need(comp is not None and comp_ok, 'COMPARE_DEV.txt is missing or does not show the pass condition of SPEC.md section 4 '
         f'({EXPECT_GAMES} of {EXPECT_GAMES} games equal in each arm, nothing missing or changed, each header exactly '
         f'"=== {CHECK}/replay_<s>: N games (planned N)"): {arms}')
    for why in lane_problems(at_check('LANE_RECORD.txt') or '', prog, PSHA, recfile, REC_SHA):
        need(False, why)
    # the registrations (self-checks, program, planned games), committed before any game; READING.md alone after the lane's record
    rprobs, found = record_problems(C, PRE, CHECK, prog, PSHA, K, T)
    for why in rprobs:
        need(False, f'the check\'s record: {why}')
    if comp_ok:
        (kx_n, kx_eq, _), (km_n, km_eq, _) = arms['kx3'], arms['km3']
    else:  # the dry run before the games: the texts show SPEC.md section 4's pass condition, the only counts a real run accepts
        kx_n = kx_eq = km_n = km_eq = EXPECT_GAMES
        print(f'DRY RUN: the texts quote the pass condition ({EXPECT_GAMES} of {EXPECT_GAMES} in each arm), not counts read from COMPARE_DEV.txt')
    GAMES = f'{kx_eq} of {kx_n} kx3 and {km_eq} of {km_n} km3 development games identical'

    # ---- the date the texts carry ---------------------------------------------------------------------------------------------------
    PD = V['pin_date']
    if not re.fullmatch(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [1-9]\d?', PD):
        sys.exit(f'pin_date {PD!r} is not like "Oct 30"')
    need(PD in today_names(), f'pin_date {PD!r} is not today ({sorted(today_names())}): set VARS["pin_date"] to the day of the commit')

    # ---- the slow reports on main: the texts say none was made on the old program --------------------------------------------------
    reports = tuple(sorted(os.path.basename(p) for p in gs('ls-tree', '--name-only', base, 'rl/results/slow_reports/').splitlines()))
    if reports != KNOWN_REPORTS:
        sys.exit(f'rl/results/slow_reports/ on the base is not the 10 known reports (the texts say none was made since Oct 14): {reports}')
    # ... and on any ref: the texts say no slow report was made on the Oct 22 program or since main-affe56e's pin
    recent = gs('log', '--all', f'--since={SLOW_REPORTS_SINCE}', '--format=%h', '--', 'rl/results/slow_reports/')
    if recent:
        sys.exit(f'commits on some ref touch rl/results/slow_reports/ since {SLOW_REPORTS_SINCE} (the texts say no slow report was made): '
                 f'{recent.split()[:5]}')

    # ---- the program, its build record and the self-checks --------------------------------------------------------------------------
    rec_text = open(recfile, encoding='utf-8').read()
    if hashlib.sha256(rec_text.encode('utf-8')).hexdigest() != REC_SHA or hashlib.sha256(open(recfile, 'rb').read()).hexdigest() != REC_SHA:
        sys.exit(f'{recfile} is not the build record SPEC.md section 1 names (sha256 {REC_SHA[:12]})')
    rec = json.loads(rec_text)
    psha = hashlib.sha256(open(prog, 'rb').read()).hexdigest()
    if psha != PSHA:
        sys.exit(f'{prog} has sha256 {psha[:12]}, not {PSHA[:12]} (SPEC.md section 1)')
    want = dict(engine_ref=K, engine_tree_archived=T, harness_source_sha256=HARN, jobs='2', program_sha256=psha, program=prog)
    bad = {k: (rec.get(k), v) for k, v in want.items() if rec.get(k) != v}
    if bad:
        sys.exit(f'build record: {bad}')
    cd = V['cert_dir']
    sc = {p: open(os.path.join(cd, f'sc_{p}.out')).read().strip() for p in ('km3', 'kx3')}
    if sc != SC:
        sys.exit(f'self-checks differ from the pin texts: {sc}')
    if not all(os.path.exists(os.path.join(cd, f'sc_{p}.done')) for p in ('km3', 'kx3')):
        sys.exit('self-check .done markers missing')
    kxrc = open(os.path.join(cd, 'sc_kx3.rc')).read().split()
    if not kxrc or kxrc[0] != '0':
        sys.exit(f'sc_kx3.rc says {kxrc}: the kx3 self-check did not exit 0')
    # the self-checks were measured on this program: night.log has the build's RECORD OK <program sha256>, then both self-check lines
    nprobs, nsecs = night_problems(open(os.path.join(cd, 'night.log'), encoding='utf-8').read(), PSHA)
    if nprobs:
        sys.exit('; '.join(nprobs))
    if kxrc[1:2] != [nsecs]:
        sys.exit(f'sc_kx3.rc ({kxrc}) and night.log ({nsecs} s) disagree on the kx3 self-check')
    K8, T12, P8, C8, H8 = K[:8], T[:12], psha[:8], C[:8], HARN[:8]
    built = rec['built_at']
    show = lambda p: git('show', f'{base}:{p}').decode('utf-8')
    LABEL = f"kx3 ({PILOT}'s files, on {NAME})"
    SPAN = ("main-affe56e's pin to the slow report's re-pin (both Oct 29)" if PD == 'Oct 29' else
            f"main-affe56e's pin (Oct 29) to the slow report's re-pin ({PD})")
    # what the commit can show about the red pin test: the hash it records, not the test's result (that is run on this commit before main
    # moves and recorded outside it)
    RECORDS = f"the re-pin records `{H8}…`, the hash this test compares"
    PINTESTS = ("the pin tests run on the re-pin's commit before main moves (their result goes to the coordinator's review and a later "
                "PIN_TESTS.txt commit)")
    NOREPORT = "no commit on any branch touched `rl/results/slow_reports/` from Oct 22 to the re-pin"  # checked above (git log --all)
    files = {}

    # ---- the pin ------------------------------------------------------------------------------------------------------------------
    p = 'rl/strength/slow_report_pin.json'
    t0 = t = show(p)
    old_pin = json.loads(t0)
    if old_pin['selfcheck'] != SC or old_pin['harness_source_sha256'] != OLD['harn']:
        sys.exit('the pin on the base does not carry the self-check texts and harness hash this was written for')
    t = once(t, f'"pilot_label": "{OLD["label"]}"', f'"pilot_label": "{LABEL}"', 'pilot_label')
    t = once(t, f'"program": "{OLD["program"]}"', f'"program": "{prog}"', 'program')
    t = once(t, f'"program_sha256": "{OLD["sha"]}"', f'"program_sha256": "{psha}"', 'program_sha256')
    t = once(t, f'"selfcheck_measured_on_sha256": "{OLD["sha"]}"', f'"selfcheck_measured_on_sha256": "{psha}"', 'measured_on')
    t = once(t, f'"harness_source_sha256": "{OLD["harn"]}"', f'"harness_source_sha256": "{HARN}"', 'harness_source_sha256')
    t = once(t, f'"engine_ref": "{OLD["ref"]}"', f'"engine_ref": "{K}"', 'engine_ref')
    t = once(t, f'"engine_tree": "{OLD["tree"]}"', f'"engine_tree": "{T}"', 'engine_tree')
    t = swap(t, ' "engine": "laptop/kx3-on-engine-candidate-2026-10-20 87a7f340', '\n',
             '6f7d2fb6a09fefac1718eaffdc364e9f9118915173848b3a4ee2f444f6db8216', (
                 f' "engine": "{kbr} {K8} engine tree {T12}: the frozen kx3\'s six engine files (claude/playout-pilot {PILOT}, byte for byte) on '
                 f'{NAME}\'s engine (main-4d48844\'s engine plus the Dual Fusion release, a partial compatibility update, with R6\'s card-support '
                 f'refusal and the held tests-only fixes; built commit {FB}), built on the laptop {built[:10]} with rl/strength/build.sh (harness '
                 f'{H8}, STRENGTH_JOBS=2); gate 1: km3\'s self-check 81b572198c04d5d1, the pinned km3; kx3\'s self-check 31d638dbc818b0fa, equal to '
                 f'the old pin\'s; KX_EXTRA_LISTS unset; the replay check: {GAMES} ({CHECK}/READING.md). Replaces the Oct 21 build (pinned '
                 f'Oct 22; 87a7f340 on main-4d48844\'s engine, tree 64de03e2c3c2, program 7d046b6f); record {REC}/CERT.md",\n'), 'pin engine')
    t = swap(t, ' "pilot_provenance": "kx3 from claude/playout-pilot@d513e37b', '\n',
             '90d9b0cfbdf5f78ea559a24a00a1b124e00c4a853d4099720460cd483b54d2f5', (
                 f' "pilot_provenance": "kx3 from claude/playout-pilot@{PILOT}, frozen Oct 4-5; on rules switch 2\'s engine Oct 12 '
                 f'(laptop/kx3-on-rules2 cd20a97a); on main-4d48844\'s engine from 2026-10-21 (laptop/kx3-on-engine-candidate-2026-10-20 87a7f340); '
                 f'its six engine files on {NAME}\'s engine since {built[:10]} ({kbr} {K8})",\n'), 'pin pilot_provenance')
    t = swap(t, ' "reference_provenance": "km3 in the same build;', '\n',
             '3ea68f936e93d62b670903c3dcc72340abd1b023535f2ed7e0247354c4b556fd', (
                 f' "reference_provenance": "km3 in the same build ({NAME}\'s km3: the Dual Fusion release, main-4d48844 to S {FB}, changed '
                 f'engine/src/players only so that the bots read the new cards); its self-check is the pinned km3\'s 81b572198c04d5d1, and the replay check\'s {km_n} km3 games equal the development run\'s '
                 f'(the 240-game field-for-field check of Oct 12 was on main-c045ede\'s engine and is not repeated)",\n'), 'pin reference_provenance')
    pin = json.loads(t)
    changed = {'pilot_label', 'program', 'program_sha256', 'selfcheck_measured_on_sha256', 'harness_source_sha256', 'engine_ref', 'engine_tree',
               'engine', 'pilot_provenance', 'reference_provenance'}
    must(list(pin) == list(old_pin) and all(pin[k] == old_pin[k] for k in pin if k not in changed), 'pin: a field outside the re-pin changed')
    must(all(pin[k] != old_pin[k] for k in changed), 'pin: a re-pin field did not change')
    # what CommittedPin and test_slow_report check, worked out here too (the tests themselves run on the commit before main moves)
    et = re.search(r'engine tree ([0-9a-f]{12})\b', pin['engine'])
    must(et is not None and et.group(1) == T12 and pin['engine_tree'].startswith(T12), 'pin: "engine tree <12 hex>" is not the engine tree')
    must(pin['engine'].startswith(kbr + ' ') and K8 in pin['engine'] and K8 in pin['pilot_provenance'], 'pin: the ref is not in engine and provenance')
    at_ = re.search(r'@([0-9a-f]{8})\b', pin['pilot_provenance'])
    must(at_ is not None and at_.group(1) == PILOT and PILOT in pin['pilot_label'], f'pin: the provenance\'s @commit is not {PILOT}')
    must(pin['selfcheck'] == SC and pin['harness_source_sha256'] == HARN == hsrc and pin['program'].endswith('/strength'),
         'pin: the self-checks, the harness source or the program path')
    must(pin['selfcheck_measured_on_sha256'] == pin['program_sha256'] == psha and pin['pilot_label'] == LABEL,
         'pin: measured_on, program_sha256 or the label')
    files[p] = t

    # ---- rl/strength/README.md: step 1, the engine notices, the unsupported-cards note, the cloud route -------------------------------
    p = 'rl/strength/README.md'
    t = show(p)
    t = once(t, "the slow report's pinned program stays kx3's frozen players on the previous engine, main-4d48844 (re-pinned Oct 22: that engine "
                "plus kx3's player files, tree `64de03e2c3c2`), until its re-pin on main-affe56e, see \"The slow report\" below",
             f"the slow report's pinned program has been kx3's frozen files on this engine since its re-pin ({PD}; tree `{T12}`), see "
             f"\"The slow report\" below", 'README step 1')
    t = once(t, "(main from R6 on; not the pinned kx3 commit 87a7f340)",
             f"(main from R6 on, and the pinned kx3 commit {K8} since the slow report's re-pin, {PD}; not 87a7f340, the one pinned before it)",
             'README unsupported cards')
    t = swap(t, "**Engine (since main-affe56e's pin, Oct 29, until the slow report's re-pin):**", '\n',
             '0ea0c1a8cd075ff29f31392c1d2e5becad1e5dd6e06f559221aacd1cdaadec4d', (
                 f"**Engine (since the slow report's re-pin, {PD}):** the pinned program below, built from `{kbr}` {K8}, is kx3's frozen files "
                 f"({PILOT}'s six engine files) on {NAME}'s engine, the official one, for kx3 and its km3 baseline alike; its pages say "
                 f"\"{LABEL}\" in the headline, and `make_predictions.py` counts them as current. The re-pin came after its replay check: {GAMES} "
                 f"(`{CHECK}/READING.md`). Like `deckgym simulate` and `goldfish`, it refuses a deck that holds one of the 55 unsupported "
                 f"printings (\"Unsupported cards\" above). kx3's play on the new cards is unmeasured: the check's games hold old cards only, "
                 f"and kx3's play-outs guess the opponent from 16 lists that hold none (`{CHECK}/SPEC.md` section 3).\n"), 'README engine notice')
    t = swap(t, '**Until the re-pin, two things to avoid:**\n', "The laptop's pinned binary is unaffected.\n",
             '41d9a35dd566dea2b6a1b215c07e34728ce070b07ecd3cc78a2c77bb4466fcbd', (
                 f"**From {SPAN}** the pinned program was still kx3 on main-4d48844 "
                 f"(next paragraph), which knows none of the B4b, P-B 095-103, C1, SP1 or P-C printings: a slow report of a deck holding one "
                 f"would have registered and then stopped at its first sitting. No slow report was made in that time: {NOREPORT}, and the "
                 f"newest report on main is of Oct 14. Main's harness source already hashed to `{H8}…` while the pin said `bf9c5d68…`, "
                 f"so the cloud route below could not rebuild from main, and `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source"
                 f"_the_pin_was_made_on` failed on main. {RECORDS[0].upper() + RECORDS[1:]}; {PINTESTS}.\n"), 'README two things to avoid')
    t = swap(t, "**Engine (since the slow report's Oct 22 re-pin):**", '\n',
             'ef36499a473e77115047f5b7ffb79ff028aab719b3057b4692f22824b015fa93', (
                 f"**Engine (from the slow report's Oct 22 re-pin to its {PD} re-pin):** the pinned program was kx3's frozen players on "
                 f"main-4d48844's engine (`laptop/kx3-on-engine-candidate-2026-10-20` 87a7f340; `/home/dacz8976/kx_r3/strength`, sha256 "
                 f"`7d046b6f…`), for kx3 and its km3 baseline alike; its pages would say \"kx3 (d513e37b, on main-4d48844)\" in the headline. "
                 f"No report was made on it ({NOREPORT}). The reports made before the Oct 22 re-pin (`rl/results/slow_reports/2026-10-12_*` to "
                 f"`2026-10-14_*`) ran on main-c045ede's engine and say so in theirs; the 2 of Oct 8-9 ran on the earlier development build "
                 f"(engine tree 31dbd2e6e8ec). All 10 are complete (320 of 320 games each), so `--dir` has nothing left to play in them, and "
                 f"none can be the base of a `--paired-with` variant on the current pin (`slow_report_paired.py` refuses another program or "
                 f"pin). The Oct 22 re-pin came after its replay check: 202 of 202 games identical in each arm "
                 f"(`rl/results/kx3_on_engine_2026-10-21/READING.md`).\n"), 'README Oct 22 paragraph')
    t = once(t, '("kx3 (d513e37b, on main-4d48844) on your deck v km3', f'("{LABEL} on your deck v km3', 'README label')
    t = once(t, f"(`{OLD['program']}`, sha256 `7d046b6f…`,", f"(`{prog}`, sha256 `{P8}…`,", 'README exact tested version')
    t = swap(t, "**Until the slow report's re-pin on main-affe56e, don't use this route from main**", '\n',
             'f1cf20171bf51a2537d7a86b4d4564d94e4e957d8f12c1c3d7eb5b2ee537c723', (
                 f"**Since the slow report's re-pin ({PD}), main's harness source is the pinned build's again** (`{H8}…`; \"Engine\" "
                 f"above). From main-affe56e's pin (Oct 29) until then it was not, and `slow_report.py` refused a rebuild from a main "
                 f"checkout.\n"), 'README cloud caveat')
    t = once(t, "The commit `87a7f3404263e1bfe76e8765ba8dd94695e19cfe` is on the branch `origin/laptop/kx3-on-engine-candidate-2026-10-20` (the "
                "frozen kx3 players, `claude/playout-pilot` d513e37b, on main-4d48844's engine: the Growl-to-0 rule, the hit back as attack "
                "damage and upstream fixes)",
             f"The commit `{K}` is on the branch `origin/{kbr}` (the frozen kx3's six engine files, `claude/playout-pilot` {PILOT}'s, on "
             f"{NAME}'s engine, the official one since Oct 29)", 'README cloud commit')
    t = once(t, "(`git fetch origin laptop/kx3-on-engine-candidate-2026-10-20`), and", f"(`git fetch origin {kbr}`), and", 'README cloud fetch')
    t = once(t, "`mkdir -p /tmp/87a7 && git archive 87a7f340 engine | tar -x -C /tmp/87a7 && (cd /tmp/87a7/engine && env",
             f"`mkdir -p /tmp/{K[:4]} && git archive {K8} engine | tar -x -C /tmp/{K[:4]} && (cd /tmp/{K[:4]}/engine && env", 'README cloud archive')
    t = once(t, f"(`{OLD['program']}` on the laptop:", f"(`{prog}` on the laptop:", 'README cloud path')
    t = once(t, f"bash rl/strength/build.sh {OLD['ref']} $HOME/slow_report_kx3/strength", f"bash rl/strength/build.sh {K} $HOME/slow_report_kx3/strength",
             'README cloud build')
    t = once(t, "**The engine tree must be `64de03e2c3c2…` and the harness source hash `bf9c5d68…`**",
             f"**The engine tree must be `{T12}…` and the harness source hash `{H8}…`**", 'README cloud tree and harness')
    t = once(t, "the laptop's `7d046b6f…`", f"the laptop's `{P8}…`", 'README cloud sha')
    t = once(t, "(`git fetch origin laptop/kx3-on-engine-candidate-2026-10-20` for the pinned commit", f"(`git fetch origin {kbr}` for the pinned commit",
             'README cloud restart')
    # what is left of the old program may stand only in the past-tense paragraphs and the unsupported-cards note
    past = ("- **Unsupported cards.**", "**From main-affe56e's pin", "**Engine (from the slow report's Oct 22 re-pin", "**Since the slow report's re-pin")
    for i, line in enumerate(t.splitlines(), 1):
        for s in ('kx_r3', '7d046b6f', '87a7f340', '64de03e2', 'kx3-on-engine-candidate', 'bf9c5d68', 'main-4d48844', 'until its re-pin',
                  'until the re-pin', "until the slow report's re-pin", 'Until the re-pin', "Until the slow report's re-pin"):
            if s in line and not line.startswith(past):
                sys.exit(f'README line {i} still says {s!r} outside the past-tense paragraphs: {line[:120]!r}')
    files[p] = t

    # ---- rl/RUN5.md, the status authority: the Oct 29 pin's slow-report bullet --------------------------------------------------------
    p = 'rl/RUN5.md'
    t = show(p)
    t = swap(t, '    - The slow report: not moved by this pin.', '\n', 'e0a501b547ef50d29540575fe9196004171de96100142943a3cde4fd391e519a', (
        f"    - The slow report: re-pinned {PD}, after its kx3 replay check on this engine (`{CHECK}/READING.md`: {GAMES}). Dustin, Oct 21, "
        f"via coordinator-072 (verbatim): \"Move the slow-report program only after its replay check passes. Until then, its reports must "
        f"clearly identify the old engine.\" The program is `{prog}` (sha256 {P8}…): kx3's frozen files (`claude/playout-pilot` {PILOT}'s six "
        f"engine files) on this engine, `{kbr}` {K8}, engine tree {T12}, harness source `{H8}…` (main's since this engine pin); its pages say "
        f"\"{LABEL}\" and count as current (`make_predictions.py`). From this pin (Oct 29) to the re-pin the program was still "
        f"`/home/dacz8976/kx_r3/strength` (kx3 on main-4d48844, sha256 7d046b6f…, pages \"kx3 (d513e37b, on main-4d48844)\"): no slow report "
        f"counted as current, none was made ({NOREPORT}), and `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was"
        f"_made_on` failed on main (the pin said `bf9c5d68…`); {RECORDS}, and {PINTESTS}. Record: `{REC}/CERT.md`.\n"), 'RUN5 slow-report bullet')
    # the Oct 21 pin's bullet: its program sentence was the present tense until now (the rest of the bullet is history and stays)
    t = once(t, "The program is `/home/dacz8976/kx_r3/strength` (sha256 7d046b6f…): kx3's frozen players (`claude/playout-pilot` d513e37b) on "
                "this engine, `laptop/kx3-on-engine-candidate-2026-10-20` 87a7f340, engine tree 64de03e2c3c2; its pages say \"kx3 (d513e37b, on "
                "main-4d48844)\" and counted as current (`make_predictions.py`) until main-affe56e's pin (Oct 29).",
             f"The program was `/home/dacz8976/kx_r3/strength` (sha256 7d046b6f…) until the slow report's {PD} re-pin (the Oct 29 pin's bullet "
             f"above): kx3's frozen players (`claude/playout-pilot` d513e37b) on this engine, `laptop/kx3-on-engine-candidate-2026-10-20` "
             f"87a7f340, engine tree 64de03e2c3c2; its pages would say \"kx3 (d513e37b, on main-4d48844)\" and would have counted as current "
             f"(`make_predictions.py`) until main-affe56e's pin (Oct 29).", 'RUN5 Oct 21 bullet')
    files[p] = t

    # ---- make_predictions: the new harness tree is current --------------------------------------------------------------------------
    p = 'rl/results/ladder_validation/make_predictions.py'
    t = show(p)
    t = once(t, '    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until '
                'the slow report\'s re-pin on main-affe56e)\n',
             f'    "harness_engine_trees": ["{T12}"],           # slow reports / exams: "engine tree <12 hex>" in manifest.json (kx3 on {NAME}, '
             f're-pinned {PD})\n', 'CURRENT_ENGINE harness tree')
    files[p] = t

    # ---- CLAUDE.md, START_HERE.md and the manifest's purpose: one sentence each ------------------------------------------------------
    p = 'CLAUDE.md'
    # the file is hard-wrapped (about 100-120 characters): the changed sentence and the rest of its line and the next are re-wrapped into
    # the fewest lines of at most 120 characters, as even as they come (the narrowest width that still gives that many lines)
    old2 = ("  report stays kx3 on main-4d48844 until its re-pin (`rl/strength/README.md`): say so when you hand one over. The working pilot\n"
            "  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets\n")
    body = (f"report has been kx3 on this engine since its re-pin ({PD}; `rl/strength/README.md`); one made before then ran on an older "
            f"engine: say so when you hand it over. The working pilot is km3, on both sides of the screen and the floor. Since Sept 30, "
            f"kt3/kta3/ktb3/ktc3 name the kog-based presets")
    wrap = lambda w: textwrap.wrap(body, w, initial_indent='  ', subsequent_indent='  ', break_long_words=False, break_on_hyphens=False)
    n = len(wrap(120))
    w = min(x for x in range(60, 121) if len(wrap(x)) == n)
    t = once(show(p), old2, '\n'.join(wrap(w)) + '\n', 'CLAUDE.md engine line')
    must(max(len(l) for l in wrap(w)) <= 120 and ' '.join(l.strip() for l in wrap(w)) == body, 'CLAUDE.md: the re-wrap')
    files[p] = t
    p = 'START_HERE.md'
    t = once(show(p), "The slow report stays kx3 on main-4d48844 until its re-pin (`rl/strength/README.md`).",
             f"The slow report has been kx3 on this engine since its re-pin ({PD}, after its replay check; `rl/strength/README.md`); its reports "
             f"from before then ran on older engines and say so.", 'START_HERE engine line')
    files[p] = t
    p = 'project_manifest.json'
    t0 = show(p)
    t = once(t0, "The slow report's program stays kx3 on main-4d48844's engine until its re-pin (Dustin, Oct 21).",
             f"The slow report's program stayed kx3 on main-4d48844's engine until its re-pin (Dustin, Oct 21): re-pinned {PD} after its "
             f"replay check, kx3's frozen files on this engine (rl/strength/slow_report_pin.json, {REC}/CERT.md).", 'manifest purpose')
    m0, m1 = json.loads(t0), json.loads(t)
    m0['available_release'].pop('purpose'), m1['available_release'].pop('purpose')
    must(m0 == m1, 'the manifest changed outside available_release.purpose')
    files[p] = t

    # ---- rl/engine-2026-10-29/README.md ----------------------------------------------------------------------------------------------
    p = 'rl/engine-2026-10-29/README.md'
    t = show(p)
    t = once(t, "The slow report's harness refuses through the same check once the slow report is re-pinned on this engine (coordinator-071 and -072).",
             f"The slow report's harness refuses through the same check since the slow report's re-pin on this engine ({PD}; coordinator-071 "
             f"and -072).", 'engine README R6 refusal')
    t = swap(t, '  - **The slow report, until its re-pin.**', '\n', '1718ff029ce2dde181216bd56428d2dde6deb5d50c16a75a3de23e73b91e6d7c', (
        f"  - **The slow report, until its re-pin ({PD}).** Until then its program was kx3 on main-4d48844's engine (`/home/dacz8976/kx_r3/strength`, "
        f"sha256 7d046b6f…), its pages would name it (\"kx3 (d513e37b, on main-4d48844)\"), and `make_predictions.py` counted no slow report "
        f"as current; that engine has none of the B4b, P-B 095-103, C1, SP1 or P-C printings, so a slow report of a deck holding one would "
        f"have registered and then stopped at its first sitting. No slow report was made in that time. Re-pinned {PD} after its kx3 replay check on this engine passed (Dustin, Oct 21): {GAMES} "
        f"(`../results/kx3_on_r6_2026-10-29/READING.md`). The program is now kx3's frozen files on this engine (`{prog}`, sha256 {P8}…; "
        f"`../results/dual_type_seam_2026-10-23/slow_pin/CERT.md`). The reports made before the re-pin stay on their older engines.\n"),
        'engine README slow report')
    files[p] = t

    # ---- the release's notes and checklist: dated pointers ---------------------------------------------------------------------------
    p = f'{REL}/RELEASE_NOTES.md'
    t = show(p)
    t = once(t, "The slow report still plays on it until its own re-pin, after its kx3 replay check (section \"R6\").",
             f"The slow report played on it until its own re-pin ({PD}), after its kx3 replay check (section \"R6\").", 'NOTES until R6')
    t = once(t, "Its pinned build (kx3 on main-4d48844) does not know the new cards; the build for its re-pin on main-affe56e does.",
             f"Its pinned build until the re-pin (kx3 on main-4d48844) did not know the new cards; the build it was re-pinned to on {PD}, on "
             f"main-affe56e, does.", 'NOTES no preflight')
    t = once(t, "Until the re-pin, the pinned program has no such check: it stops at the first sitting with a panic, `deck <file>: Card ID not "
                "found for id: <id>`, because it cannot load the deck (section \"R6\").",
             f"Until the re-pin ({PD}), the pinned program had no such check: a slow report of such a deck would have registered and then "
             f"stopped at its first sitting, with a panic, `deck <file>: Card ID not found for id: <id>`, because the program cannot load the "
             f"deck (section \"R6\").", 'NOTES opt-out')
    t = once(t, "`test_slow_report_registration.py` is run again after the re-pin.",
             f"`test_slow_report_registration.py` is run again after the re-pin. **{PD}: {RECORDS}** (`slow_pin/CERT.md`); {PINTESTS}. This "
             f"paragraph is the state before the re-pin.", 'NOTES one test red')
    t = swap(t, '- The slow report stays on the old engine (main-4d48844) until its own check on the new engine passes', '\n',
             '8f0729ced5d1d880228cd49dab8608f7bd43f1b8ebb5ce0f54c17bed5f5cb4e3', (
                 f"- The slow report stayed on the old engine (main-4d48844) until its own check on the new engine passed; no slow report was "
                 f"made in that time (a slow report of a deck holding any card printed in B4b, P-B 095-103, C1, SP1 or P-C would have registered "
                 f"and then stopped at its first sitting: the old engine cannot load them). It was re-pinned {PD} after that check passed (section "
                 f"\"R6\"): it now plays on main-affe56e and, like `deckgym simulate` and `goldfish`, refuses a deck that holds one of the 55 "
                 f"unsupported printings (exit 2).\n"), 'NOTES in plain words')
    t = once(t, "and no slow report does until the slow report's re-pin.",
             f"and no slow report did until the slow report's re-pin ({PD}), which added its harness tree {T12}.", 'NOTES selector')
    t = once(t, "the folder keeps its seed slot until it is removed.\n- **The harness source moves with S, so one test is red until the re-pin.**",
             f"the folder keeps its seed slot until it is removed. **{PD}: re-pinned on main after its replay check** (`slow_pin/CERT.md`, "
             f"`../kx3_on_r6_2026-10-29/READING.md`): the program is `{prog}`; this paragraph is the state at the switch.\n"
             f"- **The harness source moves with S, so one test is red until the re-pin.**", 'NOTES slow-report program')
    t = once(t, "so it lands with the engine (accepted, coordinator-076).\n",
             f"so it lands with the engine (accepted, coordinator-076). **{PD}: {RECORDS}** (`slow_pin/CERT.md`); {PINTESTS}. This "
             f"paragraph is the state at the switch.\n", 'NOTES harness moves')
    t = once(t, "1. **The slow report and kx3's recorded games**, until the re-pin (above). The reports so far and kx3's replay games of Oct 22 "
                "stay main-4d48844's, or older.",
             f"1. **The slow report and kx3's recorded games**, until the re-pin ({PD}, above). The reports made before it and kx3's replay "
             f"games of Oct 22 stay main-4d48844's, or older.", 'NOTES tied to the old engine')
    t = once(t, "It stays red until the slow report's re-pin.",
             f"**{PD}:** the slow report's re-pin records `{H8}…`, the hash this test compares; {PINTESTS}.", 'NOTES draft checks')
    t = once(t, "- The laptop's `pincand_work` (programs/R, the RR archive, the replay games) stays until the slow report's re-pin.",
             f"- The laptop's `pincand_work` (programs/R, the RR archive, the replay games) stayed until the slow report's re-pin ({PD}); "
             f"removing it is a separate cleanup step on its own word, not part of the re-pin.", 'NOTES pincand_work')
    t = once(t, "- **R6:** the engine programs switched Oct 29 (section \"R6\" above); the slow-report re-pin follows its kx3 replay check.",
             f"- **R6:** the engine programs switched Oct 29 (section \"R6\" above), and the slow report was re-pinned {PD} after its kx3 "
             f"replay check (`slow_pin/CERT.md`); {PINTESTS}.", 'NOTES still to do')
    files[p] = t
    p = f'{REL}/RELEASE_CHECKLIST.md'
    cell = (f"**The slow-report re-pin: made {PD}**, after its kx3 replay check passed (two-step pin, coordinator-072; "
            f"`{CHECK}/READING.md`: {GAMES}): K {K8}, `{prog}`, self-checks equal to the pin; the pin's harness hash is now "
            f"`{H8}…`, main's (`slow_pin/CERT.md`). From the switch until then the pinned slow report (kx3 on main-4d48844) had no "
            f"card-support refusal and knew none of the new printings, `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source"
            f"_the_pin_was_made_on` (`rl/strength/test_slow_report_registration.py`, 1 of 244) failed on main, and the cloud `--program` "
            f"route could not rebuild from main. {RECORDS[0].upper() + RECORDS[1:]}; {PINTESTS}.")
    if '|' in cell or '\n' in cell:
        sys.exit('CHECKLIST: the new R6 text would break the table row')
    t = swap(show(p), '**Still to do: the slow-report re-pin**', 'route must not rebuild from main.',
             '3de2a5112842cfbddf88836e089d6184c16f575883971732d4b9ea5dd17530e0', cell, 'CHECKLIST R6 still to do')
    t = once(t, "the slow report's harness refuses once it is re-pinned (`rl/strength/test_strength_card_support.py`",
             f"the slow report's harness refuses since its re-pin, {PD} (`rl/strength/test_strength_card_support.py`", 'CHECKLIST R6 refusal')
    files[p] = t

    # ---- the certification record and the generator -----------------------------------------------------------------------------------
    files[f'{REC}/strength.build.json'] = rec_text
    files[f'{REC}/selfchecks.txt'] = ''.join(f'{q} {psha} {sc[q]}\n' for q in ('km3', 'kx3'))
    files[f'{REC}/CERT.md'] = CERT.format(
        K=K, K8=K8, KBR=kbr, T=T, T12=T12, NAME=NAME, FB=FB, FTREE=FTREE, PROG=prog, PSHA=psha, P8=P8, BUILT=built, PD=PD, LABEL=LABEL,
        REBUILD=rec['rebuild_command'], BUILD_DIR=rec['build_dir'], TARGET_DIR=rec['target_dir'], RECSHA8=REC_SHA[:12], HARN=HARN, H8=H8,
        BASE8=base[:8], SCKM3=sc['km3'], SCKX3=sc['kx3'], KXSECS=nsecs, CHECK=CHECK, C8=C8,
        CBR=V['check_branch'], PRE8=PRE[:8], GAMES=GAMES, KXN=kx_n, KMN=km_n, SINCE=SLOW_REPORTS_SINCE,
        REG8=found.get('reg', 'none yet')[:8], GAM8=found.get('games', 'none yet')[:8], RD8=found.get('reading', 'none yet')[:8])
    with open(os.path.abspath(__file__), encoding='utf-8') as fh:
        files[f'{REC}/slowpin_r6.py'] = fh.read().replace('\r\n', '\n')
    for path in files:
        if path.startswith(CHECK + '/'):
            sys.exit(f'{path}: the pin would write into the check folder')
        if git('cat-file', '-e', f'{base}:{path}', ok=True).returncode == 0 and path.startswith(REC + '/'):
            sys.exit(f'{path} already exists on the base')

    paras = [
        f"Dustin, Oct 21: \"Move the slow-report program only after its replay check passes.\" The check passed: {CHECK}/READING.md "
        f"(merged here from {V['check_branch']} {C8}: the spec, the registrations committed before any game, the games, COMPARE_DEV.txt: "
        f"{GAMES}). The counts are read from COMPARE_DEV.txt; the generator refuses any other than {EXPECT_GAMES} of {EXPECT_GAMES} in each "
        f"arm, and checks the registrations' self-checks and program and the order of the check's commits.",
        f"The pin's harness_source_sha256 becomes {H8} (main's harness source since R6), the hash CommittedPin compares. The pin tests "
        f"run on this commit before main moves; their result goes to the coordinator's review and a later PIN_TESTS.txt commit.",
        f"The build record, both self-checks and the pin's other fields: {REC}/CERT.md. make_predictions.py's CURRENT_ENGINE lists the new "
        f"harness tree {T12}. rl/strength/README.md, rl/RUN5.md, CLAUDE.md, START_HERE.md, project_manifest.json's available_release "
        f"purpose and rl/engine-2026-10-29/README.md name the new program; dated pointers in {REL}/RELEASE_NOTES.md and "
        f"RELEASE_CHECKLIST.md. The generator is committed as {REC}/slowpin_r6.py."]
    msg = (f"The slow report's re-pin: kx3 ({PILOT}'s files) on {NAME}'s engine, program {P8} ({kbr} {K8})\n\n"
           + '\n\n'.join(textwrap.fill(x, 110, break_long_words=False, break_on_hyphens=False) for x in paras)
           + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")

    # ---- the tree: base + the check's folder (merge) + the pin's files -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        env = dict(GIT_INDEX_FILE=os.path.join(td, 'index'))
        git('read-tree', base, env=env)
        for line in gs('ls-tree', '-r', C, '--', CHECK + '/').splitlines():
            meta, path = line.split('\t', 1)
            mode, _, blob = meta.split()
            git('update-index', '--add', '--cacheinfo', f'{mode},{blob},{path}', env=env)
        for path, text in files.items():
            if '\r' in text:
                sys.exit(f'{path}: CR')
            blob = gs('hash-object', '-w', '--stdin', inp=text.encode('utf-8'))
            git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
        tree = gs('write-tree', env=env)
        diff = gs('diff-tree', '-r', '--name-status', base, tree).splitlines()
    exists = lambda q: git('cat-file', '-e', f'{base}:{q}', ok=True).returncode == 0
    want_diff = sorted([('M' if exists(q) else 'A') + '\t' + q for q in files] + ['A\t' + q for q in gs('ls-tree', '-r', '--name-only', C, '--', CHECK + '/').splitlines()])
    if sorted(diff) != want_diff:
        sys.exit('unexpected diff:\n' + '\n'.join(sorted(set(diff) ^ set(want_diff))))
    listing = '\n'.join(d for d in diff if not d.split('\t')[1].startswith(CHECK + '/')) + \
        f'\n(+ {sum(1 for d in diff if d.split(chr(9))[1].startswith(CHECK + "/"))} files of {CHECK}/ from {C8})'
    if DRY:
        dump(V, base, files, show, listing, msg, tree)
        print(f'DRY RUN: tree {tree} on {base[:8]} + {C8} (objects in a temporary folder, removed; no ref)\n' + listing)
        return
    commit = gs('-c', 'user.name=dacz8976-creator', '-c', 'user.email=dacz8976@gmail.com', 'commit-tree', tree, '-p', base, '-p', C, '-F', '-', inp=msg.encode())
    ref = f"refs/heads/{V['branch']}"
    cur = git('rev-parse', '-q', '--verify', ref, ok=True).stdout.decode().strip()
    if cur and '--replace' not in sys.argv:
        sys.exit(f"{V['branch']} exists ({cur[:8]}); pass --replace")
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    print(f"re-pin {commit} on {V['branch']} (parents {base[:8]} {C8}, tree {tree[:8]})\n" + listing)


def dump(V, base, files, show, listing, msg, tree):
    """The dry run's review copy: every new or changed text file at its path, a unified diff of each against the base, the list, the message."""
    d = V.get('dump', '/home/dacz8976/relplan/slowpin_dump')
    if not (d.rstrip('/').endswith('slowpin_dump') and d.startswith('/home/dacz8976/relplan/')):
        sys.exit(f'the dump folder {d} is not a slowpin_dump folder under /home/dacz8976/relplan/')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, 'diffs'))
    for path, text in files.items():
        out = os.path.join(d, 'files', path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
        r = git('show', f'{base}:{path}', ok=True)
        old = r.stdout.decode('utf-8') if r.returncode == 0 else ''
        lines = list(difflib.unified_diff(old.splitlines(keepends=True), text.splitlines(keepends=True), f'a/{path}', f'b/{path}', n=0))
        with open(os.path.join(d, 'diffs', path.replace('/', '__') + '.diff'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.writelines(l if l.endswith('\n') else l + '\n' for l in lines)
    with open(os.path.join(d, 'DIFF_LIST.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(f'tree {tree} = base {base} + the check folder + these files\n{listing}\n')
    with open(os.path.join(d, 'COMMIT_MESSAGE.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(msg)


CERT = """# The slow report's re-pin on {NAME}: certification

Dustin, Oct 21 (verbatim, relayed by the coordinator): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." His Oct 28 "Yes" to the Dual Fusion adoption covers R6 as listed, which includes "the slow-report pin, the kx3 rebuild and the self-check digests" (`../RELEASE_CHECKLIST.md`, R6; `../RELEASE_NOTES.md`). The check passed (`{CHECK}/READING.md`, merged with this commit from `{CBR}` {C8}), so the program moves here, on {PD}.

- **The engine ref:** `{K}` on `{KBR}` (on origin). It is the built commit S, {FB}, plus the frozen kx3's six engine files: a merge of the old pin's commit 87a7f340 and S, and `git diff --name-only {FB} {K8}` lists exactly those six files, each the blob of `claude/playout-pilot` d513e37b and of 87a7f340. Its `engine/` is tree {T12} (`{T}`): {FB}'s {FTREE} plus kx3's six files. `rl/strength` is {FB}'s.
- **The build** ({BUILT}): `{REBUILD}` (the build record's `rebuild_command`), with the build folder `{BUILD_DIR}` and the shared target folder `{TARGET_DIR}` (reused, not a fresh folder as on Oct 21). Its record (`strength.build.json` here, sha256 {RECSHA8}…, as `{CHECK}/SPEC.md` section 1 names it) says engine_ref {K8}, engine_tree_archived {T12}, harness {H8}, jobs "2", program sha256 `{PSHA}`.
- **The harness source:** `{HARN}`, the Oct 22 pin's source (bf9c5d68…) plus R6's card-support refusal in `rl/strength/src/main.rs` (`{CHECK}/SPEC.md` section 1). It is main's own: this generator worked out build.sh's hash (`rl/strength/src/*.rs` sorted the C way, then `Cargo.toml`) on the base {BASE8} and got the same value. So the pin's `harness_source_sha256` is the hash `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` works out on main.
- **The gate: both self-checks, measured on {P8} itself** in R6's night job (`../r6_release/tools/night_r6.sh`, step 4: 12 games, t-altaria v t-suicune, with every KX_*, PDL_*, DECKGYM_*, JEV_* and PG_* variable removed). The night's log ties them to the program: its build line `RECORD OK {PSHA}` comes first, then both self-check lines; the generator checks that order and the texts.
  - km3: `{SCKM3}`, equal to the pin's text.
  - kx3: `{SCKX3}`, equal to the pin's text ({KXSECS} s, exit status 0).
  - The check's three registrations replayed both again: each `{CHECK}/replay_{{a,b,c}}/manifest.json` records both texts, equal to the pin's, "run by strength_prereg.py", with this program and its sha256, K and its engine tree, the planned games, the pre-game commit {PRE8} and the development run's file hashes, and its `manifest.sha256` names it (the generator checks each; `{CHECK}/SPEC.md` section 4).
- **The replay check:** the development run's {KXN} kx3 and {KMN} km3 games replayed on {P8} at their own seeds, against the reading fixed before any game (`{CHECK}/SPEC.md` section 4, committed at {PRE8}, which holds no registration, game or result; none of its files changed after it): {GAMES} (`{CHECK}/COMPARE_DEV.txt`, compare_dev.py's exit status 0 in `LANE_RECORD.txt`), and `READING.md` says "Verdict: pass." The counts here are read from COMPARE_DEV.txt by the generator, which refuses any other, and each registration's header there matches its committed `games.jsonl`. The order is the lane's, checked by the generator: the registrations alone ({REG8}), then the games with COMPARE_DEV.txt and LANE_RECORD.txt ({GAM8}), then READING.md alone ({RD8}).
- **The pin's changes:** program, program_sha256, selfcheck_measured_on_sha256, harness_source_sha256 (bf9c5d68… to {H8}…), engine_ref, engine_tree, pilot_label ("{LABEL}", coordinator-072), engine, pilot_provenance and reference_provenance. The self-check texts, the seed block and slots and every other field are unchanged (the generator compares them).
- **Why "d513e37b's files":** the Dual Fusion release, main-4d48844 to S {FB}, changed `engine/src/players/` only so that the bots read the new cards (km3's type checks among them), so the players are not all d513e37b's; kx3's own six files are, byte for byte (`{CHECK}/SPEC.md` section 1).
- **The docs:** `rl/strength/README.md` (step 1, the engine notices, the unsupported-cards note, and the cloud route's ref, branch, tree, harness and program), `rl/RUN5.md` (the Oct 29 pin's slow-report bullet, and the Oct 21 pin's program sentence, now past tense), `make_predictions.py`'s CURRENT_ENGINE (the harness tree {T12}), the engine lines of `CLAUDE.md` and `START_HERE.md`, one sentence of `project_manifest.json`'s available_release purpose, `rl/engine-2026-10-29/README.md`, and dated pointers in `../RELEASE_NOTES.md` and `../RELEASE_CHECKLIST.md` (R6). Their "until the re-pin" texts are now past tense or carry this date.
- **The generator:** `slowpin_r6.py`, committed here: the Oct 22 generator (`../../engine_candidate_2026-10-20/release/tools/slowpin_main.py`) adapted to R6, written as a merge with the check's record onto main, and refused unless the check's READING.md says pass, its COMPARE_DEV.txt shows the pass condition, and its registrations and order are the lane's (above).
- **The pin tests:** `rl/strength/test_slow_report_registration.py` (244 tests, `CommittedPin` among them), `test_slow_report.py` and `make_predictions.py --selftest` run on this commit before main moves (`{CHECK}/SPEC.md` section 4: "then the pin tests run"); their result goes to the coordinator's review and a later PIN_TESTS.txt commit, as on Oct 22, and is not part of this commit. This commit records `{H8}…`, the hash `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` compares; the generator works out what CommittedPin checks about the pin, but runs no test.
- **What it replaces:** the Oct 21 build (pinned Oct 22; 87a7f340 on main-4d48844's engine, tree 64de03e2c3c2, program 7d046b6f). No slow report was made on it: no commit on any branch touched `rl/results/slow_reports/` from Oct 22 to this re-pin (`git log --all --since={SINCE} -- rl/results/slow_reports/` on the laptop's clone was empty when this was made), and the newest report on main is of Oct 14. The 10 on main: the 8 of Oct 12-14 ran on main-c045ede's engine and the 2 of Oct 8-9 on an earlier development build, and each says so in its own page.
"""

if __name__ == '__main__':
    main()
