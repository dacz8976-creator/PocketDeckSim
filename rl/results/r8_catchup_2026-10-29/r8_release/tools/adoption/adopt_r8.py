#!/usr/bin/env python3
"""R8 switch step 6 (plan 113 §6 as amended by 151-155): the adoption commit that switches the official engine programs from
main-affe56e (rl/engine-2026-10-29/) to main-543dad0 (rl/engine-2026-11-04/). Adapted from R6's adopt_r6.py.

  adopt_r8.py VARS.json [--dry-run] [--replace]          the draft (its release notes keep @@DRAFT_CHECKS@@)
  adopt_r8.py VARS.json --final [--dry-run] [--replace]  the final commit: the draft plus the checks text, nothing else

One commit on top of VARS["base"], the build-record commit (933f2790 on laptop/r8-catchup-2026-10-29: one parent, S8, adding only
r8_release/), built from a private index: nothing checked out, no ref but the draft/final branch touched, nothing pushed. The
programs are the blobs already committed in r8_release/programs_final/. The texts are adopt_r8_texts.json (beside this file): the
reviewed drafts (workflow wf_f2ba0a62-59d) with the verifiers' accepted fixes (fix_texts.py); every edit of an existing text
replaces text that must occur exactly once. Every number the switch produced is read from the record commit (record.json, the
programs' blobs), never typed. Any outcome other than the expected one stops the script: that goes to the coordinator.
VARS: base, base_sha, s_commit, main, pin_date, pin_short, branch, final_branch; for --final also verified_draft and draft_checks."""
import hashlib, json, os, re, subprocess, sys, tempfile

REPO = '/home/dacz8976/pincand'
HERE = os.path.dirname(os.path.abspath(__file__))
S_EXPECT = '543dad0007a345128ec95e9c2698699c8b5493ce'
K_EXPECT = 'b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0'
LANE = '48dec4f5361992b2788401333b2f1cc4531f073a'
OLD = dict(name='main-affe56e', dir='rl/engine-2026-10-29', commit='affe56e88985e2997a66beb85efaca0c487617bd',
           deckgym='6a2617f4f9e91c9ca4bb4cb3227fdd8e29ff100bbcfd8e0b1fee8273f866f6f8',
           legality_scan='d9805aaaa10a2a70a40cffa4858efd5baf15deff183d144981856ac4d5dca702',
           goldfish='ea787a4ed5b6bb9771ffefecf2737a76335efd918ad4138befe888df3322f342')
NEW_DIR = 'rl/engine-2026-11-04'           # the UTC date of the build; checked against the record
R8D = 'rl/results/r8_catchup_2026-10-29'
REC = R8D + '/r8_release'
PD = REC + '/programs_final'
TOOLS_DIR = REC + '/tools/adoption'
NOTES_P = R8D + '/RELEASE_NOTES.md'
MP_P = 'rl/results/ladder_validation/make_predictions.py'
SR_P = 'rl/strength/README.md'
FRONT_P = 'README.md'
KG_P = 'rl/results/deck_improvement/kingambit_2026-10-15/CHECK.md'
ORDER = ('deckgym', 'legality_scan', 'goldfish')
PLAYERS_EXPECTED = sorted(['engine/src/players/mod.rs', 'engine/src/players/opening_class.rs',
                           'engine/src/players/protocol_player.rs', 'engine/src/players/weighted_random_player.rs'])
NSW_EXPECTED = 14
HARN = 'c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149'
PIN_LABEL_OLD = "kx3 (d513e37b's files, on main-affe56e)"
PIN_PROGRAM_OLD = '23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378'
SC = dict(km3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1',
          kx3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')
CS = dict(line="card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 256, 'RulesUnverified': 4}",
          all_by_status="{'Complete': 4565, 'RulesUnverified': 12}", older='0', exact='yes', check='OK')
PH = re.compile(r'@@([A-Z][A-Z0-9_]*)@@')
CO = 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
TOOL_FILES = ('adopt_r8.py', 'adopt_r8_texts.json', 'fix_texts.py', 'verify_r8.sh')   # identical in the draft and final runs
# Dustin's words, verbatim, with the files that must hold them at the base
YES = 'Adopt all three'
OCT21_MOVE = ("Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the "
              "old engine.")
OCT21_LEAVE = "Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them."
APPROVED_SOURCES = {
    NOTES_P: [f'"{YES}"): one more docs commit'],   # RELEASE_NOTES.md:283-284 (the line breaks before the quote)
    'rl/results/engine_candidate_2026-10-20/RELEASE_NOTES.md': [OCT21_MOVE, OCT21_LEAVE],
}


def git(*a, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO, *a], capture_output=True, input=inp, env=env)
    if r.returncode:
        sys.exit(f'git {" ".join(a)} failed: {r.stderr.decode()}')
    return r.stdout


def gs(*a, **k):
    return git(*a, **k).decode().strip()


def once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f'{what}: the old text occurs {n} times, not once: {old[:100]!r}')
    return text.replace(old, new)


def fill(text, P, what):
    missing = set()

    def rep(m):
        if m.group(1) in P:
            return str(P[m.group(1)])
        missing.add(m.group(1))
        return m.group(0)
    return PH.sub(rep, text), missing


def stop(what):
    sys.exit(f'STOP: {what}. This generator writes the texts of the expected outcome only; bring the record to the coordinator '
             f'(a changed game, a moved digest or a judgment call goes on to Dustin).')


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    V = json.load(open(args[0]))
    final, dry, replace = '--final' in args, '--dry-run' in args, '--replace' in args
    for k, v in V.items():
        if not final and k in ('verified_draft', 'draft_checks'):
            continue
        if isinstance(v, str) and PH.search(v):
            sys.exit(f'VARS["{k}"] still holds a placeholder: {v!r}')
    T = json.load(open(os.path.join(HERE, 'adopt_r8_texts.json'), encoding='utf-8'))
    if T.get('schema') != 'adopt_r8_texts v1':
        sys.exit('adopt_r8_texts.json: wrong schema')
    base = gs('rev-parse', V['base'] + '^{commit}')
    S = gs('rev-parse', V['s_commit'] + '^{commit}')
    main_c = gs('rev-parse', V['main'] + '^{commit}')
    if S != S_EXPECT:
        sys.exit(f'VARS["s_commit"] is {S[:8]}, not S8 {S_EXPECT[:8]}')
    if V.get('base_sha') and base != gs('rev-parse', V['base_sha'] + '^{commit}'):
        sys.exit(f'{V["base"]} is {base[:8]}, not the record commit {V["base_sha"][:8]}: the branch moved')
    NAME = 'main-' + S[:7]
    if OLD['name'] != 'main-' + OLD['commit'][:7] or not re.fullmatch(r'main-[0-9a-f]{7}', NAME):
        sys.exit('the release name is not "main-" plus the first 7 hex characters of the built commit')

    # ---- guards: ancestry, base shape, engine identity --------------------------------------------------------------
    for a, b, what in ((OLD['commit'], S, 'main-affe56e'), (main_c, S, 'main'), (S, base, 'S8')):
        if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', a, b]).returncode:
            sys.exit(f'{what} ({a[:8]}) is not an ancestor of {b[:8]}')
    if gs('rev-parse', base + '^') != S or subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', base + '^2'],
                                                         capture_output=True).returncode == 0:
        sys.exit('the base is not a one-parent child of S8 (the build-record commit)')
    outside = [f for f in gs('diff', '--name-only', S, base).splitlines() if not f.startswith(REC + '/')]
    if outside:
        sys.exit(f'the base changes files outside {REC}/: {outside[:5]}')
    if gs('rev-parse', 'origin/main') != main_c:
        sys.exit('origin/main is not VARS["main"]: fetch, then re-take the base texts')
    if V.get('check_remote', True):
        remote = (gs('ls-remote', 'origin', 'refs/heads/main').split() or ['(none)'])[0]
        if remote != main_c:
            sys.exit(f'main on origin is {remote[:8]}, not VARS["main"] {main_c[:8]}: fetch and look before drafting')
    STREE = gs('rev-parse', S + ':engine')
    if gs('rev-parse', base + ':engine') != STREE or gs('rev-parse', LANE + ':engine') != STREE:
        sys.exit("the base's (or Lane N's) engine/ is not S8's")
    for d in ('engine/Cargo.toml', 'engine/Cargo.lock'):
        if gs('rev-parse', f"{OLD['commit']}:{d}") != gs('rev-parse', f'{S}:{d}'):
            sys.exit(f'{d} changed since main-affe56e')
    players = sorted(gs('diff', '--name-only', OLD['commit'], S, '--', 'engine/src/players').splitlines())
    if players != PLAYERS_EXPECTED:
        sys.exit(f'engine/src/players changed in {players}, not exactly the expected four {PLAYERS_EXPECTED}')
    sw = lambda c: sorted(set(re.findall(r'DECKGYM_[A-Z0-9_]+', gs('grep', '-h', '-o', r'DECKGYM_[A-Z0-9_]*', c, '--', 'engine/src'))))
    if sw(S) != sw(OLD['commit']) or len(sw(S)) != NSW_EXPECTED:
        sys.exit(f'S8 reads {len(sw(S))} DECKGYM_* switches, not main-affe56e\'s same {NSW_EXPECTED}')

    # ---- the programs, as committed in the record ------------------------------------------------------------------
    progs = {}
    for n in ORDER:
        line = gs('ls-tree', base, f'{PD}/{n}')
        m_ = re.fullmatch(r'100755 blob ([0-9a-f]{40})\t' + re.escape(f'{PD}/{n}'), line)
        if not m_:
            sys.exit(f'{PD}/{n}: {line!r} (want a 100755 blob)')
        progs[n] = (hashlib.sha256(git('cat-file', 'blob', m_.group(1))).hexdigest(), m_.group(1))
    sums_blob = gs('rev-parse', f'{base}:{PD}/SHA256SUMS')
    if git('cat-file', 'blob', sums_blob).decode() != ''.join(f'{progs[n][0]}  {n}\n' for n in ORDER):
        sys.exit('programs_final/SHA256SUMS does not match the committed programs')
    if git('show', f'{base}:{PD}/SOURCE_COMMIT').decode().strip() != S:
        sys.exit('programs_final/SOURCE_COMMIT is not S8')
    if gs('ls-tree', base, NEW_DIR):
        sys.exit(f'{NEW_DIR} exists in the base')
    if any(progs[n][0] == OLD[n] for n in ORDER):
        sys.exit('a program is byte-equal to main-affe56e\'s: not a build of S8')

    show = lambda p: git('show', f'{base}:{p}').decode('utf-8')
    R = json.loads(show(f'{REC}/record.json'))

    # ---- the record: only the expected outcome passes ------------------------------------------------------------------
    if R.get('schema') != 'r8-record v1' or R['s'] != S or R['s_engine_tree'] != STREE or R['lane_n'] != LANE:
        sys.exit('record.json is not the record of S8')
    if R['programs_sha256'] != {n: progs[n][0] for n in ORDER} or not R['programs_equal_lane_n']:
        sys.exit("record.json names other programs than programs_final, or they are not Lane N's")
    ran = show(f'{REC}/RAN_SHA256.txt')
    if R.get('ran_sha256', '') != 'all equal (RAN_SHA256.txt)' or not ran.rstrip().endswith('RESULT: all equal') or 'DIFFERS' in ran:
        stop('RAN_SHA256.txt does not show the programs that ran equal to the committed ones')
    st = R['strength']
    if R['k'] != K_EXPECT or st['engine_ref'] != K_EXPECT or st['engine_tree_archived'] != R['k_engine_tree']:
        stop('the strength program is not the build of K8 (b5f15351)')
    if st['harness'] != HARN or st['jobs'] != '2':
        stop('the strength build record has another harness hash or job count')
    sc = R['selfchecks']
    if sc['km3'] != SC['km3'] or sc['kx3'] != SC['kx3'] or sc['kx3_rc'] != 0:
        stop('a self-check text differs from the pin (new pin texts need Dustin)')
    b = R['build']
    if b['lane_start'][:10] != NEW_DIR[-10:] or b['build_ok_at'][:10] != NEW_DIR[-10:]:
        sys.exit(f'the build ran {b["lane_start"]}..{b["build_ok_at"]}: the folder must be rl/engine-<that UTC date>, not {NEW_DIR}')
    if R['gencmp'] != R['gencmp_lane_n'] or R['gencmp'] != {'ids': 'SAME', 'database': 'SAME'}:
        stop(f'gencmp {R["gencmp"]} / {R["gencmp_lane_n"]}')
    if R['card_status'] != CS or R['card_status_lane_n'] != CS:
        stop(f'card_status: {R["card_status"]}')
    su = R['suite']
    if (su['rc'], su['passed'], su['failed'], su['ignored'], su['compile_errors']) != (0, 2633, 0, 0, 0):
        stop(f'the suite: {su}')
    if R['refusal_test_tu']['status'] != 'OK' or R['refusal_test_tu']['ran'] != 4 or R['refusal_test_k8']['ran'] != 4:
        stop(f'the card-support refusal test: {R["refusal_test_tu"]}')
    if not re.fullmatch(r'OK( \(skipped=\d+\))?', R['strength_py']['status']) or R['strength_py']['failing']:
        stop(f'the rl/strength suite: {R["strength_py"]}')
    for key in ('replays', 'replays_official'):
        rp = R[key]
        if (rp['n'], rp['ref_same'], rp['ref_growl_known'], rp['vs_same'], rp['rules_clean']) != (18, 15, 3, 18, 11) or rp['goldfish'] != 'page =, coverage =':
            stop(f'the replays ({key}): {({k: v for k, v in rp.items() if k != "rows"})}')
    if R['replays']['verify'] != 'VERIFY PASS' or not R['replays_official']['equal_lane_n']:
        stop('Lane N\'s VERIFY or the official build\'s replays v Lane N\'s')
    fl = R['floor']
    if fl['n'] != 12 or fl['other'] or len(fl['recompare_pass']) != 12 or fl['goldfish_r8_coverage'] != 11 \
            or fl['floor2s_basis'] != 'floor2S = 92 of 92 committed sums':
        stop(f'the floor re-check: {fl}')

    # ---- the base texts that must still say what this generator replaces ---------------------------------------------------
    pin = json.loads(show('rl/strength/slow_report_pin.json'))
    if pin['pilot_label'] != PIN_LABEL_OLD or pin['program_sha256'] != PIN_PROGRAM_OLD or pin['harness_source_sha256'] != HARN:
        sys.exit('the slow-report pin is not kx3 on main-affe56e (23d8a9b5, harness c4f7da21): the two-step texts would be wrong')
    for path, frags in APPROVED_SOURCES.items():
        t = show(path)
        for f in frags:
            if f not in t:
                sys.exit(f'{path} no longer holds {f!r}: re-read Dustin\'s words before quoting them')

    # ---- the values -------------------------------------------------------------------------------------------------------
    t0, t1 = b['lane_start'], b['build_ok_at']
    P = dict(NAME=NAME, NEW_DIR=NEW_DIR, PD=PD, REC=REC, S=S, S8=S[:8], STREE=STREE, STREE8=STREE[:8], STREE12=STREE[:12],
             PIN=V['pin_date'], PIN_SHORT=V['pin_short'], RECORD8=base[:8], RECORD=base,
             BUILT_AT=f'{t0[:10]}, {t0[11:16]}-{t1[11:16]} UTC', BUILD_SECS=b['secs'],
             K8=K_EXPECT[:8], KTREE12=R['k_engine_tree'][:12], KX8_SHA=st['sha256'], KX8_SHA8=st['sha256'][:8])
    P.update({f'{n.upper()}_SHA': progs[n][0] for n in ORDER})
    P.update({f'{n.upper()}_BLOB': progs[n][1][:8] for n in ORDER})
    if final:
        txt = open(V['draft_checks'], encoding='utf-8').read().replace('\r', '').strip()
        if PH.search(txt) or not txt:
            sys.exit('the draft-checks text is empty or holds a placeholder')
        P['DRAFT_CHECKS'] = txt
    files = {}

    def edits(path, lst, what):
        t = show(path)
        for i, e in enumerate(lst):
            if e['path'] != path:
                sys.exit(f'{what}[{i}] is for {e["path"]}, not {path}')
            t = once(t, e['old'], e['new'], f'{what}[{i}]')
        files[path] = t

    # ---- project_manifest.json ------------------------------------------------------------------------------------------
    raw = show('project_manifest.json')
    m = json.loads(raw)
    if json.dumps(m, indent=2, ensure_ascii=False) + '\n' != raw:
        sys.exit('the manifest does not round-trip through json.dumps(indent=2)')
    old = m['available_release']
    want = dict(name=OLD['name'], artifact=OLD['dir'] + '/deckgym', sha256=OLD['deckgym'], legality_scan=OLD['dir'] + '/legality_scan',
                legality_scan_sha256=OLD['legality_scan'], goldfish=OLD['dir'] + '/goldfish', goldfish_sha256=OLD['goldfish'],
                source_commit=OLD['commit'])
    for k, v in want.items():
        if old.get(k) != v:
            sys.exit(f'manifest available_release.{k} is {old.get(k)!r}, not {v!r}')
    if any(r.get('name') == NAME for r in m['historical_releases']) or m['historical_releases'][-1]['name'] != 'main-4d48844':
        sys.exit('the manifest history is not as expected (tail main-4d48844, no main-543dad0)')
    F = {}
    for k, v in T['manifest_fields'].items():
        F[k], miss = fill(v, P, f'manifest.{k}')
        if miss:
            sys.exit(f'manifest.{k}: no value for {sorted(miss)}')
    hist = dict(old)
    hist['superseded'] = F['superseded']
    m['historical_releases'].append(hist)
    m['available_release'] = {
        'name': NAME,
        'artifact': f'{NEW_DIR}/deckgym', 'sha256': progs['deckgym'][0],
        'legality_scan': f'{NEW_DIR}/legality_scan', 'legality_scan_sha256': progs['legality_scan'][0],
        'goldfish': f'{NEW_DIR}/goldfish', 'goldfish_sha256': progs['goldfish'][0],
        'goldfish_note': F['goldfish_note'], 'source_commit': S, 'source_working_tree': False,
        'built': F['built'], 'identity_evidence': F['identity_evidence'], 'approved': F['approved'], 'purpose': F['purpose'],
    }
    if list(m['available_release']) != list(old):
        sys.exit(f'the new available_release keys differ from the old ones: {list(old)}')
    m['latest_source_commit'] = S
    m['latest_source_note'] = F['latest_source_note']
    text = json.dumps(m, indent=2, ensure_ascii=False) + '\n'
    json.loads(text)
    files['project_manifest.json'] = text

    # ---- the new folder's README, the pin lines, the pointers, RUN5, the strength README, the notes ---------------------
    files[f'{NEW_DIR}/README.md'] = T['new_dir_readme'].replace('\r', '')
    edits('START_HERE.md', T['start_here'], 'START_HERE')
    edits('CLAUDE.md', T['claude'], 'CLAUDE.md')
    for path in (FRONT_P, KG_P, MP_P):
        edits(path, [e for e in T['pointers'] if e['path'] == path], f'pointers {path}')
    if sorted(e['path'] for e in T['pointers']) != sorted([FRONT_P, KG_P, MP_P]):
        sys.exit('pointers: not one edit each for README.md, CHECK.md and make_predictions.py')
    edits('rl/RUN5.md', T['run5'], 'RUN5')
    edits(SR_P, T['strength_readme'], 'rl/strength/README.md')
    edits(NOTES_P, T['release_notes'], 'R8 RELEASE_NOTES')
    # coordinator-155 §3: START_HERE.md and CLAUDE.md hold only the three hunks
    if len(T['start_here']) != 1 or len(T['claude']) != 2:
        sys.exit('START_HERE.md / CLAUDE.md: not exactly the three hunks coordinator-155 §3 allows')

    # ---- placeholders: fill every text; only @@DRAFT_CHECKS@@ may stay, and only in the draft -------------------------------
    for path in list(files):
        before = set(PH.findall(show(path))) if not path.startswith(NEW_DIR + '/') else set()
        if before:
            sys.exit(f'{path} already holds @@...@@ text at the base: {sorted(before)}')
        files[path], missing = fill(files[path], P, path)
        if missing - ({'DRAFT_CHECKS'} if not final else set()):
            sys.exit(f'{path}: no value for {sorted(missing)}')
    left = sorted({k for t in files.values() for k in PH.findall(t)})
    for path, text in files.items():
        if '\r' in text:
            sys.exit(f'{path}: CR in the new text')
    # the generator's own files go with it (the record is already pushed)
    tools = {}
    for f in TOOL_FILES:
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            sys.exit(f'missing {p}')
        tools[f'{TOOLS_DIR}/{f}'] = open(p, 'rb').read().replace(b'\r', b'')

    # ---- the commit -----------------------------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'index'))
        git('read-tree', base, env=env)
        for path, text in files.items():
            blob = gs('hash-object', '-w', '--stdin', inp=text.encode('utf-8'))
            git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
        for path, data in tools.items():
            blob = gs('hash-object', '-w', '--stdin', inp=data)
            git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
        for n in ORDER:
            git('update-index', '--add', '--cacheinfo', f'100755,{progs[n][1]},{NEW_DIR}/{n}', env=env)
        git('update-index', '--add', '--cacheinfo', f'100644,{sums_blob},{NEW_DIR}/SHA256SUMS', env=env)
        tree = gs('write-tree', env=env)
    diff = gs('diff-tree', '-r', '--name-status', base, tree).splitlines()
    want_diff = sorted([f'A\t{NEW_DIR}/{n}' for n in ('README.md', 'SHA256SUMS', 'deckgym', 'goldfish', 'legality_scan')] +
                       [f'A\t{p}' for p in tools] + [f'M\t{p}' for p in files if not p.startswith(NEW_DIR)])
    if sorted(diff) != want_diff:
        sys.exit('unexpected tree diff:\n' + '\n'.join(sorted(diff)))
    if gs('rev-parse', tree + ':engine') != STREE:
        sys.exit("the new tree's engine/ is not S8's")
    if final:
        vd = gs('rev-parse', V['verified_draft'] + '^{commit}')
        if gs('rev-parse', vd + '^') != base:
            sys.exit('the verified draft is not on this base')
        if gs('diff-tree', '-r', '--name-only', gs('rev-parse', vd + '^{tree}'), tree).splitlines() != [NOTES_P]:
            sys.exit('the final differs from the verified draft in more than the release notes')
        P['DRAFT8'] = vd[:8]
    print(f'tree {tree} on base {base[:8]}; {len(diff)} paths:\n' + '\n'.join(diff))
    print('placeholders left:', left)
    if dry:
        out = os.environ.get('ADOPT_DUMP')
        if out:
            for path, text in files.items():
                dst = os.path.join(out, path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'w', encoding='utf-8', newline='\n').write(text)
            print('texts written under', out)
        print('DRY RUN: no commit, no ref')
        return
    msg = (FINAL_MSG if final else DRAFT_MSG).format(**P, BASE=base[:8], R8D=R8D, CO=CO)
    commit = gs('-c', 'user.name=dacz8976-creator', '-c', 'user.email=dacz8976@gmail.com', 'commit-tree', tree, '-p', base, '-F', '-',
                inp=msg.encode())
    branch = V['final_branch'] if final else V['branch']
    if branch in ('main', 'laptop/r8-catchup-2026-10-29') or not branch.startswith('laptop/'):
        sys.exit(f'{branch}: the generator writes only its own laptop/ draft or final branch')
    ref = f'refs/heads/{branch}'
    cur = subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', ref], capture_output=True, text=True).stdout.strip()
    if cur and not replace:
        sys.exit(f'{branch} exists ({cur[:8]}); pass --replace to move it')
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    print(f'{"FINAL" if final else "draft"} {commit} on {branch} (parent {base[:8]}, tree {tree[:8]})')
    print(gs('ls-tree', tree, NEW_DIR + '/'))


DRAFT_MSG = """R8 DRAFT, not on main: pin the engine programs as {NAME} ({NEW_DIR}/)

The R8 adoption commit, drafted for its checks (plan step 6); main moves only after the final review.
Parent {BASE}, the build record (S8 {S8} plus r8_release/). Generator: {REC}/tools/adoption/adopt_r8.py
(texts: adopt_r8_texts.json). Its --final run fills the release notes' "Checks of the adoption commit"
after verify_r8.sh, and changes nothing else.

{CO}
"""

FINAL_MSG = """Pin the engine: {NAME} ({NEW_DIR}/), R8's programs, the catch-up with upstream's card code

Adopted on Dustin's word of Nov 4 ("Adopt all three", answering the approval page "R8 Approval Sheet";
relayed in coordinator-153; verbatim in {R8D}/RELEASE_NOTES.md section 13 and the manifest's "approved").
The slow report stays kx3 on main-affe56e's engine until its kx3 replay check on R8 passes (Dustin, Oct 21).
Parent {BASE}, the build record of S8 ({S8}). Equal to the verified draft {DRAFT8} except the release
notes' "Checks of the adoption commit".

- {NEW_DIR}/: S8's tested programs (deckgym {DECKGYM_SHA}, the same blobs as
  {PD}/, mode 100755), SHA256SUMS, README.md. engine/ is the built commit's tree, {STREE8}.
- project_manifest.json: main-affe56e moves to historical_releases (superseded); available_release is
  {NAME} (source_commit {S8}); latest_source_*.
- START_HERE.md's engine line; CLAUDE.md's engine paragraph and the goldfish card-support bullet (his third yes;
  RELEASE_NOTES section 10 item 9); nothing else in either file (coordinator-155 section 3).
- README.md's engine line; rl/RUN5.md (the status bullet, the Nov 4 pin, the floor re-check, the yardstick, the
  finished list, the baselines exception); make_predictions.py CURRENT_ENGINE (no slow-report tree until the
  re-pin); rl/strength/README.md (the slow report's program is still main-affe56e's until its re-pin);
  deck_improvement/kingambit_2026-10-15/CHECK.md's engine pointer.
- {R8D}/RELEASE_NOTES.md: section 13, the adoption; the header and section 10 item 9 in the past tense.
- {REC}/tools/adoption/: this generator, its texts and their assembly, verify_r8.sh.

{CO}
"""

if __name__ == '__main__':
    main()
