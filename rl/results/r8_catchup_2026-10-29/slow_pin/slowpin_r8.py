#!/usr/bin/env python3
"""The slow report's re-pin for R8 (step 8 of plan 113, coordinator-158 §3): kx3's frozen files on main-543dad0's engine (K8 b5f15351).

  slowpin_r8.py      (run from anywhere; writes into the worktree WT, commits nothing)

Dustin, Oct 21 (verbatim, via coordinator-072): "Move the slow-report program only after its replay check passes. Until then, its
reports must clearly identify the old engine." The check (rl/results/kx3_on_r8_2026-11-04/) passed with a timing note; Dustin, Nov 5,
quoted in coordinator-158: "Yes finish". The re-pin goes on top of the check's branch (one line of commits carries R8 steps 1-8), so
this writes the changed files into the worktree WT, which must be on that branch at the check's last commit, clean; the commit is made
afterwards by the session (after reading the diff). It changes rl/strength/slow_report_pin.json (program, its sha256 twice, engine_ref,
engine_tree, pilot_label, engine, pilot_provenance, reference_provenance; the self-check texts, the harness hash c4f7da21 (unchanged since
R6) and every other field stay), make_predictions.py's harness_engine_trees, and turns step 6's "until the re-pin" texts into the
re-pin's: CLAUDE.md and START_HERE.md (the pin lines Dustin's Nov 4 yes covers), project_manifest.json (available_release.purpose, one
sentence), rl/strength/README.md, rl/RUN5.md, rl/engine-2026-11-04/README.md, and dated pointers in R8's RELEASE_NOTES.md. It adds
rl/results/r8_catchup_2026-10-29/slow_pin/ (CERT.md, the build record, the self-check lines, this generator). Every old text is matched
exactly (once()), so any drift refuses. Adapted from R6's rl/results/dual_type_seam_2026-10-23/slow_pin/slowpin_r6.py."""
import hashlib, json, os, re, subprocess, sys, textwrap

WT = '/home/dacz8976/r5_w'
BR = 'laptop/kx3-replay-r8-2026-11-04'
TIP = '3e157ff5ff1c01158195815e095d76fe7d8f6341'  # the check's last commit (READING.md and the re-time), on origin
REL = 'rl/results/r8_catchup_2026-10-29'
REC = REL + '/slow_pin'
CHECK = 'rl/results/kx3_on_r8_2026-11-04'
DEV = 'rl/results/strength_2026-10-03_kx3_dev'
HARN = 'c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149'
S8 = '543dad0007a345128ec95e9c2698699c8b5493ce'
LANE = '48dec4f5361992b2788401333b2f1cc4531f073a'
K = 'b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0'
KBR = 'laptop/kx3-on-r8-2026-11-04'
T = 'f33d2c49baf432d4bd1e407b96a6c243471fa9b6'
PROG = '/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength'
PSHA = 'd4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d'
OLD = dict(program='/home/dacz8976/kx_r4/strength', sha='23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378',
           ref='e3ddc0149bb9d35fda1becbb17ab5f71d9461609', tree='cd970db60aa5df7e9db9d7479e88f87190dab2c3',
           label="kx3 (d513e37b's files, on main-affe56e)")
PILOT = 'd513e37b'
KX3_FILES = ('engine/examples/playout_smoke.rs', 'engine/src/players/mod.rs', 'engine/src/players/playout_player.rs',
             'engine/src/players/playout_pool.rs', 'engine/tests/playout_pilot_extra_lists_test.rs', 'engine/tests/playout_pilot_test.rs')
SC = dict(km3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1',
          kx3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')
REGS = {'replay_a': 192, 'replay_b': 192, 'replay_c': 20}
EXPECT_GAMES = 202
KNOWN_REPORTS = ('2026-10-08_draft-A-wallace', '2026-10-09_brew-08-entei-rainbow-cave', '2026-10-12_13-a-ninetales-raticate',
                 '2026-10-12_brew-07-hoopa-darkrai-sableye', '2026-10-12_brew-09-sableye-obstagoon', '2026-10-12_draft-D-entei-grimhound',
                 '2026-10-13_12-ariados-whimsicott-ogerpon', '2026-10-13_brew-10-diancie-giratina', '2026-10-14_brew-08-entei-rainbow-cave',
                 '2026-10-14_draft-A-wallace')
SINCE = '2026-10-29'  # the old program's pin: no commit on any ref may touch rl/results/slow_reports/ from then on
PD = 'Nov 5'
NAME = 'main-543dad0'
GENV = dict(os.environ, GIT_NO_LAZY_FETCH='1')


def git(*a, ok=False):
    r = subprocess.run(['git', '-C', WT, *a], capture_output=True, env=GENV)
    if ok:
        return r
    if r.returncode:
        sys.exit(f'git {" ".join(a)} failed: {r.stderr.decode()}')
    return r.stdout


def gs(*a):
    return git(*a).decode().strip()


def must(cond, why):
    if not cond:
        sys.exit('REFUSED: ' + why)


def once(text, old, new, what):
    n = text.count(old)
    must(n == 1, f'{what}: the old text occurs {n} times, not once: {old[:100]!r}')
    return text.replace(old, new)


def line_starting(text, prefix, what):
    """The one whole line (with its newline) that starts with prefix."""
    ls = [l for l in text.splitlines(keepends=True) if l.startswith(prefix)]
    must(len(ls) == 1, f'{what}: {len(ls)} lines start with {prefix[:80]!r}, not one')
    must(ls[0].endswith('\n'), f'{what}: the line has no newline')
    return ls[0]


def replace_line(text, prefix, new_line, what):
    return once(text, line_starting(text, prefix, what), new_line, what)


def append_to_line(text, prefix, addition, what):
    l = line_starting(text, prefix, what)
    return once(text, l, l[:-1] + addition + '\n', what)


def compare_counts(text):
    arms = {a: [0, 0, 0] for a in ('kx3', 'km3')}
    lines = re.findall(r'^  (kx3|km3): (\d+) games; equal (\d+); differ (\d+); not in the development run (\d+); seed differs (\d+)$', text, re.M)
    for a, g, e, d, ni, sd in lines:
        arms[a][0] += int(g); arms[a][1] += int(e); arms[a][2] += int(d) + int(ni) + int(sd)
    heads = re.findall(r'^=== .*$', text, re.M)
    want = [f'=== {CHECK}/{r}: {n} games (planned {n})' for r, n in REGS.items()]
    ok = (len(lines) == 6 and heads == want and 'MISSING' not in text and 'changed row' not in text
          and text.rstrip().splitlines()[-1:] == ['RESULT: every changed game is in a named row']
          and all(arms[a][0] == arms[a][1] == EXPECT_GAMES and arms[a][2] == 0 for a in arms))
    return arms, ok


def main():
    # ---- the worktree, the branch, the engine -------------------------------------------------------------------------------------
    must(gs('rev-parse', '--abbrev-ref', 'HEAD') == BR, f'{WT} is not on {BR}')
    must(gs('rev-parse', 'HEAD') == TIP, f'HEAD is not {TIP[:8]}')
    must(gs('status', '--porcelain', '--untracked-files=all') == '', 'the worktree is not clean')
    must(gs('rev-parse', f'refs/remotes/origin/{BR}') == TIP, f'origin/{BR} is not {TIP[:8]} (push the check first)')
    must(gs('rev-parse', 'HEAD:engine') == gs('rev-parse', f'{S8}:engine') == gs('rev-parse', f'{LANE}:engine'),
         "the branch's engine/ is not S8's (and the lane commit's)")
    for anc in ('e6a20c73', S8):
        must(git('merge-base', '--is-ancestor', anc, 'HEAD', ok=True).returncode == 0, f'{anc[:8]} is not an ancestor of HEAD')
    must(gs('rev-parse', f'refs/heads/{KBR}') == K and gs('rev-parse', f'refs/remotes/origin/{KBR}') == K, f'{KBR} (local and origin) is not {K[:8]}')
    must(gs('log', '-1', '--format=%P', K).split() == [LANE, OLD['ref']], f'K8 is not the merge of {LANE[:8]} and the old pin {OLD["ref"][:8]}')
    must(sorted(gs('diff', '--no-renames', '--name-only', LANE, K).splitlines()) == sorted(KX3_FILES), "K8 differs from 48dec4f5 in other files than kx3's six")
    for f in KX3_FILES:
        b = gs('rev-parse', f'{K}:{f}')
        if f == 'engine/src/players/mod.rs':
            must(b != gs('rev-parse', f'{PILOT}:{f}'), 'mod.rs: expected d513e37b\'s plus the adapter lines, found d513e37b\'s blob')
            d = gs('diff', '--no-renames', '--numstat', f'{PILOT}:{f}', f'{K}:{f}').split()
            must(d[:2] == ['8', '0'], f'mod.rs: K8 v d513e37b is not 8 added lines and 0 removed: {d[:2]}')
        else:
            must(b == gs('rev-parse', f'{PILOT}:{f}'), f"{f}: K8's blob is not d513e37b's")
    must(gs('rev-parse', f'{K}:engine') == T, f"K8's engine tree is not {T[:12]}")
    rs = sorted((p for p in gs('ls-tree', '--name-only', 'HEAD', 'rl/strength/src/').splitlines() if p.endswith('.rs')), key=lambda p: p.encode())
    hsrc = hashlib.sha256(b''.join(git('cat-file', 'blob', f'HEAD:{p}') for p in rs + ['rl/strength/Cargo.toml'])).hexdigest()
    must(hsrc == HARN, f'the harness source at HEAD hashes to {hsrc[:12]}, not {HARN[:8]}')

    # ---- the program and its build record -------------------------------------------------------------------------------------------
    must(hashlib.sha256(open(PROG, 'rb').read()).hexdigest() == PSHA, f'{PROG} is not {PSHA[:12]}')
    rec_text = open(PROG + '.build.json', encoding='utf-8').read()
    rec = json.loads(rec_text)
    want = dict(engine_ref=K, engine_tree_archived=T, harness_source_sha256=HARN, jobs='2', program_sha256=PSHA, program=PROG)
    bad = {k: (rec.get(k), v) for k, v in want.items() if rec.get(k) != v}
    must(not bad, f'build record: {bad}')
    rec_sha = hashlib.sha256(rec_text.encode('utf-8')).hexdigest()

    # ---- the check: READING.md's verdict, COMPARE_DEV.txt, the registrations ---------------------------------------------------------
    rd = gs('show', f'HEAD:{CHECK}/READING.md')
    must(re.search(r'^\*\*Verdict: pass, with a timing note\*\*', rd, re.M), 'READING.md does not say "Verdict: pass, with a timing note"')
    must('"Yes finish"' in rd, "READING.md does not quote Dustin's \"Yes finish\"")
    arms, cok = compare_counts(gs('show', f'HEAD:{CHECK}/COMPARE_DEV.txt') + '\n')
    must(cok, f'COMPARE_DEV.txt does not show the pass condition: {arms}')
    lane = gs('show', f'HEAD:{CHECK}/LANE_RECORD.txt')
    must(lane.startswith("The lane's record") and lane.rstrip().endswith('== compare_dev.py exit status: 0'), 'LANE_RECORD.txt')
    dev = json.loads(git('show', f'HEAD:{DEV}/manifest.json'))
    devfiles = {x['name']: (x['path'], x['sha256']) for x in dev['decks'] + dev['opponents']}
    for reg, n in REGS.items():
        mt = git('show', f'HEAD:{CHECK}/{reg}/manifest.json')
        m = json.loads(mt)
        must(m.get('selfcheck') == SC, f'{reg}: self-checks')
        must(set((m.get('selfcheck_source') or {}).values()) == {'run by strength_prereg.py'} and set(m['selfcheck_source']) == set(SC), f'{reg}: selfcheck_source')
        must(m.get('program') == PROG and m.get('program_sha256') == PSHA, f'{reg}: program')
        must(m.get('planned_games') == n, f'{reg}: planned games')
        must(f'{K} engine tree {T}' in (m.get('engine') or ''), f'{reg}: engine')
        files = m['decks'] + m['opponents']
        must(files and all(devfiles.get(x['name']) == (x['path'], x['sha256']) for x in files), f'{reg}: a deck or list file is not the development run\'s')
        must(gs('show', f'HEAD:{CHECK}/{reg}/manifest.sha256') == f'{hashlib.sha256(mt).hexdigest()}  manifest.json', f'{reg}: manifest.sha256')
        rows = [l for l in gs('show', f'HEAD:{CHECK}/{reg}/games.jsonl').split('\n') if l.strip()]
        must(len(rows) == n, f'{reg}: games.jsonl has {len(rows)} games, not {n}')
    GAMES = f"{arms['kx3'][1]} of {arms['kx3'][0]} kx3 and {arms['km3'][1]} of {arms['km3'][0]} km3 development games identical"

    # ---- the slow reports: none made since the old program's pin ----------------------------------------------------------------------
    reports = tuple(sorted(os.path.basename(p) for p in gs('ls-tree', '--name-only', 'HEAD', 'rl/results/slow_reports/').splitlines()))
    must(reports == KNOWN_REPORTS, f'rl/results/slow_reports/ is not the 10 known reports: {reports}')
    must(gs('log', '--all', f'--since={SINCE}', '--format=%h', '--', 'rl/results/slow_reports/') == '',
         f'a commit on some ref touches rl/results/slow_reports/ since {SINCE}')

    K8, T12, P8, H8 = K[:8], T[:12], PSHA[:8], HARN[:8]
    LABEL = f"kx3 ({PILOT}'s files, on {NAME})"
    TIMING = ('pass, with a timing note: one kx3 decision at 188,311 ms crossed the check\'s 120 s stop line; a quiet re-time put this '
              'program at 0.994x the old one on it; Dustin, Nov 5, via coordinator-158 (verbatim): "Yes finish"')
    PINTESTS = ("the pin tests run on the re-pin's commit before main moves (their result goes to the coordinator's review and a "
                "PIN_TESTS.txt commit beside CERT.md)")
    NOREPORT = f"no commit on any branch touched `rl/results/slow_reports/` from Oct 29 to the re-pin"
    show = lambda p: git('show', f'HEAD:{p}').decode('utf-8')
    files = {}

    # ---- the pin ------------------------------------------------------------------------------------------------------------------
    p = 'rl/strength/slow_report_pin.json'
    t0 = t = show(p)
    old_pin = json.loads(t0)
    must(old_pin['selfcheck'] == SC and old_pin['harness_source_sha256'] == HARN and old_pin['program_sha256'] == OLD['sha'], 'the pin is not the one this was written for')
    t = once(t, f'"pilot_label": "{OLD["label"]}"', f'"pilot_label": "{LABEL}"', 'pilot_label')
    t = once(t, f'"program": "{OLD["program"]}"', f'"program": "{PROG}"', 'program')
    t = once(t, f'"program_sha256": "{OLD["sha"]}"', f'"program_sha256": "{PSHA}"', 'program_sha256')
    t = once(t, f'"selfcheck_measured_on_sha256": "{OLD["sha"]}"', f'"selfcheck_measured_on_sha256": "{PSHA}"', 'measured_on')
    t = once(t, f'"engine_ref": "{OLD["ref"]}"', f'"engine_ref": "{K}"', 'engine_ref')
    t = once(t, f'"engine_tree": "{OLD["tree"]}"', f'"engine_tree": "{T}"', 'engine_tree')
    jl = lambda key, val: f' "{key}": {json.dumps(val, ensure_ascii=False)},\n'  # one pin line, the value JSON-escaped
    t = replace_line(t, ' "engine": "laptop/kx3-on-r6-2026-10-29 e3ddc014 ', jl('engine',
        f'{KBR} {K8} engine tree {T12}: the frozen kx3\'s six engine files (claude/playout-pilot {PILOT}; five byte for byte, '
        f'and engine/src/players/mod.rs {PILOT}\'s plus R8\'s 8 protocol-adapter lines) on {NAME}\'s engine (main-affe56e\'s engine plus R8, '
        f'upstream\'s card code through #439; built on the R8 lane commit {LANE[:8]}, whose engine tree is that of R8\'s release commit '
        f'{S8[:8]}), built on the laptop {rec["built_at"][:10]} with rl/strength/build.sh (harness {H8}, STRENGTH_JOBS=2); gate: km3\'s '
        f'self-check 81b572198c04d5d1 and kx3\'s 31d638dbc818b0fa, equal to the old pin\'s, replayed on this program in each of the replay '
        f'check\'s three registrations; KX_EXTRA_LISTS unset; the replay check: {GAMES} ({CHECK}/READING.md, with a timing note '
        f'Dustin accepted on {PD}). Replaces the '
        f'Oct 29 build (e3ddc014 on main-affe56e\'s engine, tree cd970db60aa5, program 23d8a9b5); record {REC}/CERT.md'), 'pin engine')
    t = replace_line(t, ' "pilot_provenance": "kx3 from claude/playout-pilot@d513e37b', jl('pilot_provenance',
        f'kx3 from claude/playout-pilot@{PILOT}, frozen Oct 4-5; on rules switch 2\'s engine Oct 12 '
        f'(laptop/kx3-on-rules2 cd20a97a); on main-4d48844\'s engine from 2026-10-21 (laptop/kx3-on-engine-candidate-2026-10-20 87a7f340); '
        f'its six engine files on main-affe56e\'s engine from 2026-10-29 (laptop/kx3-on-r6-2026-10-29 e3ddc014); on {NAME}\'s engine since '
        f'2026-11-05 ({KBR} {K8}, built 2026-11-04; players/mod.rs carries R8\'s 8 protocol-adapter lines)'), 'pin pilot_provenance')
    t = replace_line(t, ' "reference_provenance": "km3 in the same build', jl('reference_provenance',
        f'km3 in the same build ({NAME}\'s km3: R8 changed engine/src/players in 4 files, for the protocol '
        f'adapter and the new cards); its self-check is the pinned km3\'s 81b572198c04d5d1, and the replay check\'s {arms["km3"][0]} km3 '
        f'games equal the development run\'s (the 240-game field-for-field check of Oct 12 was on main-c045ede\'s engine and is not '
        f'repeated)'), 'pin reference_provenance')
    pin = json.loads(t)
    changed = {'pilot_label', 'program', 'program_sha256', 'selfcheck_measured_on_sha256', 'engine_ref', 'engine_tree', 'engine',
               'pilot_provenance', 'reference_provenance'}
    must(list(pin) == list(old_pin) and all(pin[k] == old_pin[k] for k in pin if k not in changed), 'pin: a field outside the re-pin changed')
    must(all(pin[k] != old_pin[k] for k in changed), 'pin: a re-pin field did not change')
    et = re.search(r'engine tree ([0-9a-f]{12})\b', pin['engine'])
    must(et is not None and et.group(1) == T12 and pin['engine_tree'].startswith(T12), 'pin: "engine tree <12 hex>"')
    must(pin['engine'].startswith(KBR + ' ') and K8 in pin['engine'] and K8 in pin['pilot_provenance'], 'pin: the ref in engine and provenance')
    at_ = re.search(r'@([0-9a-f]{8})\b', pin['pilot_provenance'])
    must(at_ is not None and at_.group(1) == PILOT and PILOT in pin['pilot_label'], 'pin: the provenance @commit')
    must(pin['selfcheck'] == SC and pin['harness_source_sha256'] == HARN and pin['program'].endswith('/strength'), 'pin: self-checks, harness, path')
    must(pin['selfcheck_measured_on_sha256'] == pin['program_sha256'] == PSHA and pin['pilot_label'] == LABEL, 'pin: measured_on, sha, label')
    # the pages a slow report writes quote the pin's texts, and test_slow_report's BothPilotsEverywhere refuses these words in them
    # (the first run of this generator put "pass" in the engine text, and that test failed; 08109819, never pushed)
    for k in changed:
        for bad in (r'\bpass(es|ed)?\b', r'\bfail(s|ed|ure)?\b', r'\bverdict\b', r'\bcutoff', r'\bgood enough\b'):
            must(re.search(bad, str(pin[k]), re.I) is None, f'pin {k}: the word {bad} would reach the pages')
    files[p] = t

    # ---- make_predictions.py: the new harness tree is current ---------------------------------------------------------------------
    p = 'rl/results/ladder_validation/make_predictions.py'
    files[p] = once(show(p),
        '    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until '
        'the slow report\'s re-pin onto main-543dad0\'s engine; it stays kx3 on main-affe56e until then)\n',
        f'    "harness_engine_trees": ["{T12}"],           # slow reports / exams: "engine tree <12 hex>" in manifest.json (kx3 on {NAME}, '
        f're-pinned {PD})\n', 'make_predictions harness tree')

    # ---- CLAUDE.md: the slow-report sentence of the engine paragraph (re-wrapped, at most 120 characters a line) ----------------------
    p = 'CLAUDE.md'
    old3 = ("  stays kx3 on main-affe56e until its re-pin onto main-543dad0's engine, after kx3's replay check on it\n"
            "  (`rl/strength/README.md`); until then it refuses (exit 2) a deck that holds one of the 55 printings main-affe56e could\n"
            "  not play. Every slow report so far ran on main-affe56e or an older engine: say which when you hand one over.\n")
    body = (f"has been kx3 on this engine since its re-pin ({PD}, after kx3's replay check on it; `rl/strength/README.md`). Every "
            f"slow report made before then ran on main-affe56e or an older engine: say which when you hand one over.")
    wrap = lambda w: textwrap.wrap(body, w, initial_indent='  ', subsequent_indent='  ', break_long_words=False, break_on_hyphens=False)
    n = len(wrap(120))
    w = min(x for x in range(60, 121) if len(wrap(x)) == n)
    must(max(len(l) for l in wrap(w)) <= 120 and ' '.join(l.strip() for l in wrap(w)) == body, 'CLAUDE.md: the re-wrap')
    files[p] = once(show(p), old3, '\n'.join(wrap(w)) + '\n', 'CLAUDE.md slow-report sentence')

    # ---- START_HERE.md and the manifest's purpose: one sentence each --------------------------------------------------------------
    p = 'START_HERE.md'
    files[p] = once(show(p),
        "The slow report stays kx3 on main-affe56e (its re-pin of Oct 29) until its re-pin on main-543dad0, after kx3's replay check on "
        "it (`rl/strength/README.md`); until then it refuses a deck that holds one of the 55 printings main-affe56e could not play; every "
        "slow report so far ran on main-affe56e or an older engine, and its pages say which.",
        f"The slow report has been kx3 on {NAME}'s engine since its re-pin ({PD}, after kx3's replay check on it; `rl/strength/README.md`); "
        f"every slow report made before then ran on main-affe56e or an older engine, and its pages say which.", 'START_HERE slow report')
    p = 'project_manifest.json'
    t0 = show(p)
    t = once(t0,
        "The slow report's program stays kx3 on main-affe56e's engine (/home/dacz8976/kx_r4/strength) until its re-pin onto main-543dad0's "
        "engine, after its kx3 replay check (Dustin, Oct 21; rl/strength/README.md); until then that program refuses (exit 2, the "
        "card-support message, after the slow report's registration) a deck that holds one of the 55 printings main-affe56e could not "
        "play, which the official programs now play (rl/strength/README.md, \\\"Unsupported cards\\\").",
        f"The slow report's program stayed kx3 on main-affe56e's engine (/home/dacz8976/kx_r4/strength) until its re-pin (Dustin, Oct 21): "
        f"re-pinned {PD} after its kx3 replay check on this engine, kx3's frozen files on this engine (rl/strength/slow_report_pin.json, "
        f"{REC}/CERT.md).", 'manifest purpose')
    m0, m1 = json.loads(t0), json.loads(t)
    m0['available_release'].pop('purpose'); m1['available_release'].pop('purpose')
    must(m0 == m1, 'the manifest changed outside available_release.purpose')
    files[p] = t

    # ---- rl/engine-2026-11-04/README.md -----------------------------------------------------------------------------------------
    p = 'rl/engine-2026-11-04/README.md'
    files[p] = replace_line(show(p), '  - **The slow report, until its re-pin.**', (
        f"  - **The slow report, until its re-pin ({PD}).** Until then its program was kx3 on main-affe56e's engine "
        f"(`/home/dacz8976/kx_r4/strength`, sha256 23d8a9b5…, built from `laptop/kx3-on-r6-2026-10-29` e3ddc014, engine tree cd970db6), its "
        f"pages said \"kx3 ({PILOT}'s files, on main-affe56e)\", and `make_predictions.py` counted no slow report as current; a slow report of "
        f"a deck holding one of the 55 printings main-affe56e left unimplemented would have registered and then stopped with that program's "
        f"card-support message (exit 2). No slow report was made in that time. Re-pinned {PD} after kx3's replay check on this engine "
        f"passed (Dustin, Oct 21): {GAMES} (`../results/kx3_on_r8_2026-11-04/READING.md`; {TIMING}). The program is now K8's "
        f"(`{PROG}`, sha256 {P8}…; `../results/r8_catchup_2026-10-29/slow_pin/CERT.md`). The reports made before the re-pin stay on their "
        f"older engines.\n"), 'engine README slow report')

    # ---- rl/RUN5.md: the Nov 4 pin's slow-report bullet, and the Oct 29 pin's program sentence (now past tense) ---------------------
    p = 'rl/RUN5.md'
    t = replace_line(show(p), '    - The slow report: not moved by this pin. Dustin, Oct 21, via coordinator-072', (
        f"    - The slow report: re-pinned {PD}, after its kx3 replay check on this engine (`{CHECK}/READING.md`: {GAMES}; {TIMING}). "
        f"Dustin, Oct 21, via coordinator-072 (verbatim): \"Move the slow-report program only after its replay check passes. Until then, "
        f"its reports must clearly identify the old engine.\" The program is `{PROG}` (sha256 {P8}…): kx3's frozen files "
        f"(`claude/playout-pilot` {PILOT}'s six engine files, `players/mod.rs` with R8's 8 protocol-adapter lines) on this engine, `{KBR}` "
        f"{K8}, engine tree {T12}, harness source `{H8}…` (unchanged since R6); its pages say \"{LABEL}\" and count as current "
        f"(`make_predictions.py`). From this pin (Nov 4) to the re-pin the program was still `/home/dacz8976/kx_r4/strength` (kx3 on "
        f"main-affe56e, sha256 23d8a9b5…, pages \"{OLD['label']}\"): no slow report counted as current, and none was made ({NOREPORT}); "
        f"{PINTESTS}. Record: `{REC}/CERT.md`.\n"), 'RUN5 Nov 4 bullet')
    t = once(t, "The program is `/home/dacz8976/kx_r4/strength` (sha256 23d8a9b5…): kx3's frozen files",
             f"The program was `/home/dacz8976/kx_r4/strength` (sha256 23d8a9b5…) until the slow report's {PD} re-pin (the Nov 4 pin's bullet "
             f"above): kx3's frozen files", 'RUN5 Oct 29 bullet')
    files[p] = t

    # ---- rl/strength/README.md -------------------------------------------------------------------------------------------------
    p = 'rl/strength/README.md'
    t = show(p)
    t = once(t, "the slow report's pinned program stays kx3's frozen files on the previous engine, main-affe56e (re-pinned Oct 29: that "
                "engine plus kx3's files, tree `cd970db60aa5`), until its re-pin onto main-543dad0's engine, see \"The slow report\" below",
             f"the slow report's pinned program has been kx3's frozen files on this engine since its re-pin ({PD}; tree `{T12}`), see "
             f"\"The slow report\" below", 'README step 1')
    t = once(t, "(main from R6 on, and the pinned kx3 commit e3ddc014 since the slow report's re-pin, Oct 29; not 87a7f340, the one pinned before it)",
             f"(main from R6 on, and the pinned kx3 commit {K8} since the slow report's re-pin, {PD}, as e3ddc014 was from Oct 29; not "
             f"87a7f340, the one pinned before them)", 'README unsupported cards')
    t = replace_line(t, "**Engine (since main-543dad0's pin, Nov 4, until the slow report's re-pin):**", (
        f"**Engine (since the slow report's re-pin, {PD}):** the pinned program below, built from `{KBR}` {K8}, is kx3's frozen files "
        f"({PILOT}'s six engine files; `players/mod.rs` with R8's 8 protocol-adapter lines) on {NAME}'s engine, the official one, for kx3 "
        f"and its km3 baseline alike; its pages say \"{LABEL}\" in the headline, and `make_predictions.py` counts them as current. The "
        f"re-pin came after its replay check: {GAMES} (`{CHECK}/READING.md`; {TIMING}). Like `deckgym simulate` and `goldfish`, it refuses "
        f"a deck that holds a card the engine cannot play (\"Unsupported cards\" above); no printing in the card list is such a card now. "
        f"kx3's play on the newer cards is unmeasured: the check's games hold old cards only, and kx3's play-outs guess the opponent from "
        f"16 lists that hold none (`{CHECK}/SPEC.md` section 3).\n"), 'README engine notice')
    old_block = ("**Until the re-pin, one thing to avoid:**\n"
                 "- **Don't start a slow report of a deck that holds one of the 55 printings main-affe56e could not play** (C1, SP1 and P-C "
                 "printings that main-543dad0's `deckgym simulate`, `optimize` and `goldfish` now play). The pinned program still refuses "
                 "them (exit 2, the card-support message; \"Unsupported cards\" above), so a slow report of such a deck stops with the "
                 "program's message after its registration (with `--register-only`, at its first sitting), and the registered folder keeps "
                 "its seed slot until it is removed.\n"
                 "- Nothing else changes for the slow report: main's harness source still hashes to `c4f7da21…`, the pin's, so the cloud "
                 "route below and the pin tests are not affected by main-543dad0's pin, and the laptop's pinned binary is unaffected.\n")
    t = once(t, old_block, (
        f"**From main-543dad0's pin (Nov 4) to the slow report's re-pin ({PD})** the pinned program was still kx3 on main-affe56e (next "
        f"paragraph), which could not play 55 of the C1, SP1 and P-C printings that main-543dad0's `deckgym simulate`, `optimize` and "
        f"`goldfish` play: a slow report of a deck holding one would have registered and then stopped with the program's card-support "
        f"message (exit 2). No slow report was made in that time: {NOREPORT}, and the newest report on main is of Oct 14. Main's harness "
        f"source hashed to `{H8}…`, the pin's, throughout, so the cloud route and the pin tests were not affected; {PINTESTS}.\n"), 'README avoid block')
    t = once(t, "**Engine (the pinned program since the slow report's Oct 29 re-pin):** the pinned program below, built from "
                "`laptop/kx3-on-r6-2026-10-29` e3ddc014, is kx3's frozen files",
             f"**Engine (from the slow report's Oct 29 re-pin to its {PD} re-pin):** the pinned program (`/home/dacz8976/kx_r4/strength`, "
             f"sha256 `23d8a9b5…`), built from `laptop/kx3-on-r6-2026-10-29` e3ddc014, was kx3's frozen files", 'README Oct 29 heading')
    t = once(t, "Like main-affe56e's `deckgym simulate` and `goldfish`, it refuses a deck that holds one of the 55 printings that engine could not play",
             "Like main-affe56e's `deckgym simulate` and `goldfish`, it refused a deck that holds one of the 55 printings that engine could not play",
             'README Oct 29 refusal')
    t = once(t, f'("{OLD["label"]} on your deck v km3', f'("{LABEL} on your deck v km3', 'README label')
    t = once(t, "(`/home/dacz8976/kx_r4/strength`, sha256 `23d8a9b5…`, self-check digests", f"(`{PROG}`, sha256 `{P8}…`, self-check digests",
             'README exact tested version')
    t = once(t, "The commit `e3ddc0149bb9d35fda1becbb17ab5f71d9461609` is on the branch `origin/laptop/kx3-on-r6-2026-10-29` (the frozen kx3's "
                "six engine files, `claude/playout-pilot` d513e37b's, on main-affe56e's engine, the official one from Oct 29 to Nov 4)",
             f"The commit `{K}` is on the branch `origin/{KBR}` (the frozen kx3's six engine files, `claude/playout-pilot` {PILOT}'s, "
             f"`players/mod.rs` with R8's 8 protocol-adapter lines, on {NAME}'s engine, the official one since Nov 4)", 'README cloud commit')
    t = once(t, "(`git fetch origin laptop/kx3-on-r6-2026-10-29`), and", f"(`git fetch origin {KBR}`), and", 'README cloud fetch')
    t = once(t, "`mkdir -p /tmp/e3dd && git archive e3ddc014 engine | tar -x -C /tmp/e3dd && (cd /tmp/e3dd/engine && env",
             f"`mkdir -p /tmp/{K[:4]} && git archive {K8} engine | tar -x -C /tmp/{K[:4]} && (cd /tmp/{K[:4]}/engine && env", 'README cloud archive')
    t = once(t, "(`/home/dacz8976/kx_r4/strength` on the laptop:", f"(`{PROG}` on the laptop:", 'README cloud path')
    t = once(t, "bash rl/strength/build.sh e3ddc0149bb9d35fda1becbb17ab5f71d9461609 $HOME/slow_report_kx3/strength",
             f"bash rl/strength/build.sh {K} $HOME/slow_report_kx3/strength", 'README cloud build')
    t = once(t, "**The engine tree must be `cd970db60aa5…` and the harness source hash `c4f7da21…`**",
             f"**The engine tree must be `{T12}…` and the harness source hash `{H8}…`**", 'README cloud tree')
    t = once(t, "the laptop's `23d8a9b5…`", f"the laptop's `{P8}…`", 'README cloud sha')
    t = once(t, "(`git fetch origin laptop/kx3-on-r6-2026-10-29` for the pinned commit", f"(`git fetch origin {KBR}` for the pinned commit",
             'README cloud restart')
    past = ("- **Unsupported cards.**", "**From main-543dad0's pin", "**Engine (from the slow report's Oct 29", "**From main-affe56e's pin",
            "**Engine (from the slow report's Oct 22", "**Since the slow report's re-pin")
    for i, line in enumerate(t.splitlines(), 1):
        for s in ('kx_r4', '23d8a9b5', 'e3ddc014', 'cd970db6', 'kx3-on-r6', 'until its re-pin', 'until the re-pin',
                  "until the slow report's re-pin", 'Until the re-pin', "Until the slow report's re-pin"):
            must(not (s in line and not line.startswith(past)), f'README line {i} still says {s!r} outside the past-tense paragraphs: {line[:120]!r}')
    files[p] = t

    # ---- R8's release notes: dated pointers -------------------------------------------------------------------------------------
    p = f'{REL}/RELEASE_NOTES.md'
    t = show(p)
    t = append_to_line(t, '- The slow report stays on the old engine (main-affe56e) until its own check on the new engine passes',
                       f" **{PD}:** its check passed, and it was re-pinned onto {NAME}'s engine (`slow_pin/CERT.md`).", 'NOTES plain words')
    t = append_to_line(t, '- **The current-engine selector.**',
                       f" **{PD}:** the slow report's re-pin added its harness tree {T12}.", 'NOTES selector')
    t = append_to_line(t, '- **The slow-report program: not moved by this commit.**',
                       f" **{PD}: re-pinned** after its kx3 replay check passed (`../kx3_on_r8_2026-11-04/READING.md`: {GAMES}; {TIMING}); "
                       f"the program is K8's (`slow_pin/CERT.md`); this paragraph is the state at the switch.", 'NOTES program')
    t = once(t, "1. **The slow report and kx3's recorded games**, until the re-pin (above). The reports so far stay main-affe56e's, or older.",
             f"1. **The slow report and kx3's recorded games**, until the re-pin ({PD}, above). The reports made before it stay main-affe56e's, "
             f"or older.", 'NOTES tied to the old engine')
    t = once(t, "- kx3's rebuild on R8 (K8) stays on its branch and on the laptop until the slow report's re-pin.",
             f"- kx3's rebuild on R8 (K8) stayed on its branch and on the laptop until the slow report's re-pin ({PD}); since then its program "
             f"is the pinned one, so its folder (`/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/`) stays: a cleanup of "
             f"`pincand_work` must leave it.", 'NOTES K8')
    files[p] = t

    # ---- the record --------------------------------------------------------------------------------------------------------------
    for q in files:
        must(not q.startswith(CHECK + '/'), f'{q}: the pin would write into the check folder')
    files[f'{REC}/strength.build.json'] = rec_text
    files[f'{REC}/selfchecks.txt'] = ''.join(f'{q} {PSHA} {SC[q]}\n' for q in ('km3', 'kx3'))
    files[f'{REC}/CERT.md'] = CERT.format(
        K=K, K8=K8, KBR=KBR, T=T, T12=T12, NAME=NAME, LANE8=LANE[:8], S88=S8[:8], PROG=PROG, PSHA=PSHA, P8=P8, BUILT=rec['built_at'],
        PD=PD, LABEL=LABEL, REBUILD=rec['rebuild_command'], RECSHA=rec_sha[:12], HARN=HARN, H8=H8, CHECK=CHECK, GAMES=GAMES,
        TIP8=TIP[:8], SINCE=SINCE)
    for q in files:
        must(not (q.startswith(REC + '/') and git('cat-file', '-e', f'HEAD:{q}', ok=True).returncode == 0), f'{q} already exists')
    files[f'{REC}/slowpin_r8.py'] = open(os.path.abspath(__file__), encoding='utf-8').read().replace('\r\n', '\n')

    for q, text in files.items():
        must('\r' not in text, f'{q}: CR')
        out = os.path.join(WT, q)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    print('\n'.join(sorted(files)))
    print(f'WROTE {len(files)} files into {WT} (nothing committed). The games: {GAMES}.')


CERT = """# The slow report's re-pin on {NAME} (R8): certification

Dustin, Oct 21 (verbatim, via coordinator-072): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." His Nov 4 "Adopt all three" covers R8 as the approval page laid it out, the replay check and this re-pin among its after-yes steps. The check (`{CHECK}/READING.md`, on this branch at {TIP8}) passed with a timing note: every game identical, and one kx3 decision at 188,311 ms crossed the check's 120 s stop line; a quiet re-time put this program at 0.994x the old one on that decision (`{CHECK}/retime/`). It went to Dustin as a stop, and he answered "Yes finish" (Nov 5, quoted in coordinator-158). So the program moves here, on {PD}.

- **The engine ref:** `{K}` on `{KBR}` (on origin). It is a merge of the R8 lane commit {LANE8} (whose engine tree is that of R8's release commit {S88}, the official main-543dad0's) and the old pin's commit e3ddc014; `git diff --name-only {LANE8} {K8}` lists exactly kx3's six engine files. Five are the blobs of `claude/playout-pilot` d513e37b; `engine/src/players/mod.rs` is d513e37b's plus R8's 8 protocol-adapter lines (8 added, 0 removed; the generator checks both). Its `engine/` is tree {T12} (`{T}`).
- **The build** ({BUILT}): `{REBUILD}` (the build record's `rebuild_command`). Its record (`strength.build.json` here, sha256 {RECSHA}…) says engine_ref {K8}, engine_tree_archived {T12}, harness {H8}, jobs "2", program sha256 `{PSHA}`.
- **The harness source:** `{HARN}`, unchanged since R6's re-pin. The generator worked out build.sh's hash (`rl/strength/src/*.rs` sorted the C way, then `Cargo.toml`) on this branch and got the same value, which is the hash `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` compares.
- **The self-checks, measured on {P8} itself:** each of the check's three registrations (`{CHECK}/replay_{{a,b,c}}/manifest.json`) records both texts, equal to the pin's, "run by strength_prereg.py", with this program and its sha256 and K8's engine tree; the generator checks each, and each `manifest.sha256`. kx3's was also measured on this program in R8's switch (`../RELEASE_NOTES.md`). `selfchecks.txt` here lists both with the program's sha256.
- **The replay check:** the development run's games replayed on {P8} at their own seeds: {GAMES} (`{CHECK}/COMPARE_DEV.txt`; compare_dev.py's exit status 0 in `LANE_RECORD.txt`). The generator reads the counts from COMPARE_DEV.txt and refuses any other than 202 of 202 in each arm.
- **The pin's changes:** program, program_sha256, selfcheck_measured_on_sha256, engine_ref, engine_tree, pilot_label ("{LABEL}", the check's SPEC.md section 1), engine, pilot_provenance and reference_provenance. The self-check texts, the harness hash, the seed block and slots and every other field are unchanged (the generator compares them).
- **The program's path** is the build's own, `{PROG}` (the registrations name it). Its folder must be kept: a cleanup of `pincand_work` leaves `RR_R8_48dec4f5/strength/K8/`.
- **The docs:** `rl/strength/README.md` (step 1, the unsupported-cards note, the engine notices, the label, the tested version, and the cloud route's ref, branch, tree and program), `rl/RUN5.md` (the Nov 4 pin's slow-report bullet, and the Oct 29 pin's program sentence, now past tense), `make_predictions.py`'s CURRENT_ENGINE (the harness tree {T12}), the slow-report sentences of `CLAUDE.md` and `START_HERE.md`, one sentence of `project_manifest.json`'s available_release purpose, `rl/engine-2026-11-04/README.md`, and dated pointers in `../RELEASE_NOTES.md`. Their "until the re-pin" texts are now past tense or carry this date.
- **The generator:** `slowpin_r8.py`, committed here: R6's `../../dual_type_seam_2026-10-23/slow_pin/slowpin_r6.py` adapted to R8 and written onto the check's branch (one line of commits carries R8's steps), refused unless READING.md says "pass, with a timing note" and quotes his answer, COMPARE_DEV.txt shows the pass condition, and the registrations are as above.
- **The pin tests** run on this commit before main moves; their result is `PIN_TESTS.txt` here, in a later commit.
- **What it replaces:** the Oct 29 build (e3ddc014 on main-affe56e's engine, tree cd970db60aa5, program 23d8a9b5, `/home/dacz8976/kx_r4/strength`). No slow report was made on it: no commit on any branch touched `rl/results/slow_reports/` from Oct 29 to this re-pin (`git log --all --since={SINCE} -- rl/results/slow_reports/` on the laptop's clone was empty when this was made), and the newest report on main is of Oct 14.
"""

if __name__ == '__main__':
    main()
