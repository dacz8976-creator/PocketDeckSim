#!/usr/bin/env python3
"""R6 runbook step 10: draft the adoption commit that switches the official engine programs from main-4d48844
(rl/engine-2026-10-21/) to main-<S7> (rl/engine-2026-10-29/). Adapted from
rl/results/engine_candidate_2026-10-20/release/tools/adopt_final.py (whose final run became 93806ec3). DRAFT: not run yet.

  adopt_r6.py VARS.json [--dry-run] [--replace]          the draft (its release notes keep @@DRAFT_CHECKS@@)
  adopt_r6.py VARS.json --final [--dry-run] [--replace]  the final commit: the draft plus the checks text, nothing else

One commit on top of VARS["base"], the release branch tip after commit_record_r6.sh: the build-record commit, whose one parent
is S and which adds only r6_release/. Like 93806ec3 (one parent, 005c16a6, the candidate branch's record), the adoption has that
record as its one parent, so main can fast-forward to it. Built from a private index: nothing checked out, refs/heads/main never
touched, nothing pushed. The programs are the blobs already committed in r6_release/programs_final/.

Files (13 paths): rl/engine-2026-10-29/{deckgym,legality_scan,goldfish} (100755, the programs_final blobs), SHA256SUMS (the
programs_final blob), README.md (from the template README_engine_2026-10-29.md); project_manifest.json; START_HERE.md;
CLAUDE.md; rl/RUN5.md; rl/results/ladder_validation/make_predictions.py; rl/strength/README.md; the seam folder's
RELEASE_NOTES.md and RELEASE_CHECKLIST.md. Every edit of an existing text replaces text that must occur exactly once.

Every number the night produced is read from the record commit (r6_release/record.json, FLOOR_TABLE.md, REPLAY_TABLE.md, the
programs' blobs), never typed in. The texts here describe the EXPECTED outcome only (the runbook's steps 3-8); any other
outcome (a changed game, a moved digest, a failed check, an unexpected failure) stops the script: that goes to the coordinator,
and a judgment call to Dustin. VARS (vars_r6.json): base, base_sha, s_commit, main, pin_date, pin_short, branch, final_branch;
for --final also verified_draft and draft_checks (a text file); optional readme_template (a local path instead of the
committed template), check_remote (default true: compare origin's main with `git ls-remote`)."""
import hashlib, json, os, re, subprocess, sys, tempfile

REPO = '/home/dacz8976/pincand'
S_EXPECT = 'affe56e88985e2997a66beb85efaca0c487617bd'
K_EXPECT = 'e3ddc0149bb9d35fda1becbb17ab5f71d9461609'
OLD = dict(name='main-4d48844', dir='rl/engine-2026-10-21', commit='4d4884492aa85496acf9bafdae18b22739f56647',
           deckgym='2d3709b272abf8a83431c3e72d59f9ff0e2c8ae3e60698f22a1ca79e65ab2085',
           legality_scan='2975381f33fdd7fc650f293f0dd254226cbb6e39527529fd123ffae897051b1a',
           goldfish='db52d3de65ca2577aa39af7539635a1473d4f876842bd711131a3b2c7d797f31')
NEW_DIR = 'rl/engine-2026-10-29'           # the UTC date of the build; checked against the record
SEAM = 'rl/results/dual_type_seam_2026-10-23'
REC = SEAM + '/r6_release'
PD = REC + '/programs_final'
NOTES_P = SEAM + '/RELEASE_NOTES.md'
CHECK_P = SEAM + '/RELEASE_CHECKLIST.md'
README_T = REC + '/tools/README_engine_2026-10-29.md'
MP_P = 'rl/results/ladder_validation/make_predictions.py'
SR_P = 'rl/strength/README.md'
ORDER = ('deckgym', 'legality_scan', 'goldfish')
# R6 changes km3's player files on purpose (the bots read the new cards): this list replaces adopt_final.py's "players unchanged"
PLAYERS_EXPECTED = sorted(['engine/src/players/fuel_credit.rs', 'engine/src/players/opening_class.rs',
                           'engine/src/players/public_pricing_player.rs', 'engine/src/players/value_functions.rs',
                           'engine/src/players/weighted_random_player.rs'])
NSW_EXPECTED = 14
HARN_NEW = 'c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149'
PIN_LABEL_OLD = 'kx3 (d513e37b, on main-4d48844)'
PIN_PROGRAM_OLD = '7d046b6f9c1dcd9a9a834c2995bad256bc784e804ea08d351878e035cb24d319'
SC = dict(km3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1',
          kx3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')
CARD_STATUS_LINE = ("card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 205, 'MissingAbility': 15, 'MissingAttack': 31, "
                    "'MissingTool': 2, 'MissingTrainer': 7}")
PY_FAIL_EXPECTED = re.compile(r'^FAIL: test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on '
                              r'\(test_slow_report_registration\.CommittedPin[.)]')
PH = re.compile(r'@@([A-Z][A-Z0-9_]*)@@')
CO = 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'


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
    out = PH.sub(rep, text)
    return out, missing


def stop(what):
    sys.exit(f'STOP: {what}. This generator writes the texts of the expected outcome only; bring the record to the coordinator '
             f'(a changed game, a moved digest or a judgment call goes on to Dustin).')


OCT21_MOVE = ("Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the "
              "old engine.")
OCT21_LEAVE = "Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them."
# coordinator-076, item 8: his words verbatim, each with its source
APPROVED = (
    "Dustin, Oct 28, 2026, in the laptop session's chat at about 23:00Z (verbatim): \"Yes\", to adopting d0792568 into main with "
    "R5-R7 as follow-through (rl/results/dual_type_seam_2026-10-23/RELEASE_NOTES.md, line 3; coordinator-069); R6 is this switch "
    "of the official programs (RELEASE_CHECKLIST.md there, R6: \"part of the adoption question D answered on Oct 28\"). A "
    "\"partial compatibility update\": Astra's qualification, via coordinator-069 (verbatim: \"My recommendation is yes: adopt it "
    "as a partial compatibility update.\"). His Oct 21 words, via coordinator-072 (verbatim): \"" + OCT21_MOVE + "\" and \""
    + OCT21_LEAVE + "\" The card-support refusal for goldfish and the slow report: coordinator-071, which Dustin was told about "
    "at about 00:05Z on Oct 29 and did not object to (coordinator-072). Old rows are labelled pre-R6/v7, and nothing is "
    "recomputed.")
# fragments of APPROVED that must stand verbatim in the base's files
APPROVED_SOURCES = {
    NOTES_P: ['My recommendation is yes: adopt it as a partial compatibility update.',
              'He confirmed it in the laptop session\'s chat at about 23:00Z: "Yes"'],
    CHECK_P: ['part of the adoption question D answered on Oct 28'],
    'rl/results/engine_candidate_2026-10-20/RELEASE_NOTES.md': [OCT21_MOVE, OCT21_LEAVE],
}


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    V = json.load(open(args[0]))
    final, dry, replace = '--final' in args, '--dry-run' in args, '--replace' in args
    for k, v in V.items():
        if not final and k in ('verified_draft', 'draft_checks'):
            continue                                                  # used by --final only
        if isinstance(v, str) and PH.search(v):
            sys.exit(f'VARS["{k}"] still holds a placeholder: {v!r}')
    base = gs('rev-parse', V['base'] + '^{commit}')
    S = gs('rev-parse', V['s_commit'] + '^{commit}')
    main_c = gs('rev-parse', V['main'] + '^{commit}')
    if S != S_EXPECT:
        sys.exit(f'VARS["s_commit"] is {S[:8]}, not S {S_EXPECT[:8]}')
    if V.get('base_sha') and base != gs('rev-parse', V['base_sha'] + '^{commit}'):
        sys.exit(f'{V["base"]} is {base[:8]}, not the record commit {V["base_sha"][:8]}: the branch moved')
    NAME = 'main-' + S[:7]
    if OLD['name'] != 'main-' + OLD['commit'][:7] or not re.fullmatch(r'main-[0-9a-f]{7}', NAME):
        sys.exit('the release name is not "main-" plus the first 7 hex characters of the built commit')

    # ---- guards: ancestry, base shape, engine identity --------------------------------------------------------------
    for a, b, what in ((OLD['commit'], S, 'main-4d48844'), (main_c, S, 'main'), (S, base, 'S')):
        if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', a, b]).returncode:
            sys.exit(f'{what} ({a[:8]}) is not an ancestor of {b[:8]}')
    if gs('rev-parse', base + '^') != S or subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', base + '^2'],
                                                         capture_output=True).returncode == 0:
        sys.exit('the base is not a one-parent child of S (the build-record commit)')
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
    if gs('rev-parse', base + ':engine') != STREE:
        sys.exit("the base's engine/ is not S's")
    for d in ('engine/Cargo.toml', 'engine/Cargo.lock'):
        if gs('rev-parse', f"{OLD['commit']}:{d}") != gs('rev-parse', f'{S}:{d}'):
            sys.exit(f'{d} changed since main-4d48844')
    players = sorted(gs('diff', '--name-only', OLD['commit'], S, '--', 'engine/src/players').splitlines())
    if players != PLAYERS_EXPECTED:
        sys.exit(f'engine/src/players changed in {players}, not exactly the expected five {PLAYERS_EXPECTED}')
    sw = lambda c: sorted(set(re.findall(r'DECKGYM_[A-Z0-9_]+', gs('grep', '-h', '-o', r'DECKGYM_[A-Z0-9_]*', c, '--', 'engine/src'))))
    if sw(S) != sw(OLD['commit']) or len(sw(S)) != NSW_EXPECTED:
        sys.exit(f'S reads {len(sw(S))} DECKGYM_* switches, not main-4d48844\'s same {NSW_EXPECTED}')
    src_changed = gs('diff', '--name-only', OLD['commit'], S, '--', 'engine/src').splitlines()
    eng_other = [f for f in gs('diff', '--name-only', OLD['commit'], S, '--', 'engine').splitlines()
                 if not f.startswith(('engine/src/', 'engine/tests/'))]

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
        sys.exit('programs_final/SOURCE_COMMIT is not S')
    if gs('ls-tree', base, NEW_DIR):
        sys.exit(f'{NEW_DIR} exists in the base')
    if any(progs[n][0] == OLD[n] for n in ORDER):
        sys.exit('a program is byte-equal to main-4d48844\'s: not a build of S')

    show = lambda p: git('show', f'{base}:{p}').decode('utf-8')
    R = json.loads(show(f'{REC}/record.json'))

    # ---- the record: only the expected outcome passes ------------------------------------------------------------------
    if R.get('schema') != 'r6-record v1' or R['s'] != S or R['s_engine_tree'] != STREE:
        sys.exit('record.json is not the record of S')
    if R['programs_sha256'] != {n: progs[n][0] for n in ORDER}:
        sys.exit('record.json names other programs than programs_final')
    ran = show(f'{REC}/RAN_SHA256.txt')
    if R.get('ran_sha256', '') != 'all equal (RAN_SHA256.txt)' or not ran.rstrip().endswith('RESULT: all equal') or 'DIFFERS' in ran:
        stop('RAN_SHA256.txt does not show the programs that ran equal to the committed ones (coordinator-076, item 2)')
    if R['k'] != K_EXPECT or R['strength']['engine_ref'] != K_EXPECT or R['strength']['engine_tree_archived'] != R['k_engine_tree']:
        stop('the strength program is not the build of K (e3ddc014)')
    if R['strength']['harness'] != HARN_NEW or R['strength']['jobs'] != '2':
        stop('the strength build record has another harness hash or job count')
    if R['selfchecks']['km3'] != SC['km3'] or R['selfchecks']['kx3'] != SC['kx3'] or R['selfchecks']['kx3_rc'] != 0:
        stop('a self-check text differs from the pin (new pin texts need Dustin)')
    b = R['build']
    if b['lane_start'][:10] != NEW_DIR[-10:] or b['build_ok_at'][:10] != NEW_DIR[-10:]:
        sys.exit(f'the build ran {b["lane_start"]}..{b["build_ok_at"]}: the folder must be rl/engine-<that UTC date>, not {NEW_DIR}')
    if R['gencmp'] != {'ids': 'SAME', 'database': 'SAME'}:
        stop(f'gencmp {R["gencmp"]}')
    if R['card_status']['line'] != CARD_STATUS_LINE or R['card_status']['older'] != '0' or R['card_status']['check'] != 'OK':
        stop(f'card_status: {R["card_status"]}')
    su = R['suite']
    if (su['rc'], su['failed'], su['ignored'], su['compile_errors']) != (0, 0, 0, 0):
        stop(f'the suite: {su}')
    swr = R['switch_runs']
    if [swr[k] for k in ('default', 'DECKGYM_FLAT_RETURN_DAMAGE', 'DECKGYM_ROUND2_OFF', 'core_ROUND2_OFF')] != [[32, 0]] * 3 + [[14, 0]]:
        stop(f'the switch runs: {swr}')
    if R['refusal_test']['status'] != 'OK' or R['refusal_test']['ran'] != 4:
        stop(f'the card-support refusal test: {R["refusal_test"]}')
    py = R['strength_py']
    if len(py['failing']) != 1 or not PY_FAIL_EXPECTED.match(py['failing'][0]) \
            or not re.fullmatch(r'FAILED \(failures=1(, skipped=\d+)?\)', py['status']):
        stop(f'the rl/strength suite: {py["status"]} {py["failing"]} (expected: only CommittedPin\'s harness test)')
    rep = R['replays']
    if (rep['n'], rep['vf_same'], rep['vf_other'], rep['ref_growl_known'], rep['ref_same'], rep['rules_clean']) != (18, 17, 0, 3, 15, 11) \
            or rep['goldfish'] != 'page =, coverage =':
        stop(f'the replays: {({k: v for k, v in rep.items() if k != "rows"})}')
    fl = R['floor']
    if fl['n'] != 12 or fl['other'] or len(fl['equal_recorded']) + len(fl['equal_final_only']) != 12:
        stop(f'the floor re-check: {fl}')

    # ---- the base texts that must still say what this generator replaces ---------------------------------------------------
    pin = json.loads(show('rl/strength/slow_report_pin.json'))
    if pin['pilot_label'] != PIN_LABEL_OLD or pin['program_sha256'] != PIN_PROGRAM_OLD:
        sys.exit('the slow-report pin is not kx3 on main-4d48844 (7d046b6f): the two-step texts below would be wrong')
    for path, frags in APPROVED_SOURCES.items():
        t = show(path)
        for f in frags:
            if f not in t:
                sys.exit(f'{path} no longer holds {f!r}: re-read Dustin\'s words before quoting them')

    # ---- the values -------------------------------------------------------------------------------------------------------
    t0, t1 = b['lane_start'], b['build_ok_at']
    fo = fl['equal_final_only']
    P = dict(
        NAME=NAME, NEW_DIR=NEW_DIR, PD=PD, REC=REC, S=S, S8=S[:8], STREE=STREE, STREE8=STREE[:8], STREE12=STREE[:12],
        PIN=V['pin_date'], PIN_SHORT=V['pin_short'], APPROVED=APPROVED, RECORD8=base[:8],
        BUILT_AT=f'{t0[:10]}, {t0[11:16]}-{t1[11:16]} UTC', BUILD_SECS=b['secs'],
        SUITE=f"{su['passed']:,}", SUITE_SECS=su['secs'], NSRC=len(src_changed), NSW=NSW_EXPECTED,
        CARD_STATUS=('all 4,577 cards; 205 of the 260 new C1, SP1 and P-C printings Complete (31 missing an attack, 15 an Ability, '
                     '7 a Trainer, 2 a Tool); older cards neither Complete nor RulesUnverified: 0'),
        SWITCH_RUNS=('32 of 32 under the default, DECKGYM_FLAT_RETURN_DAMAGE and DECKGYM_ROUND2_OFF each, and core\'s hit-back '
                     'module 14 of 14 under DECKGYM_ROUND2_OFF'),
        REPLAYS_SHORT=(f"18 of 18 runs, {rep['games_total']:,} games or deals: the 17 that play games equal main-4d48844's game for "
                       f"game ({rep['vf_same_zero']} of them counted deal by deal, 0 differing), and goldfish's page and coverage file "
                       f"are byte-equal to the reference; against the 08a9b3a references only the 3 known Growl-rule rows differ "
                       f"(new17_k3 8 of 8,500, dev_km3_new17 7 of 8,500, 8_new_km3 1 of 16,000), as on main-4d48844; every rules "
                       f"page says no RULE finding"),
        FLOOR_SHORT=(f"{fl['n']} of {fl['n']} pieces ({fl['games']:,} games) equal to main-4d48844's final pages (games and coverage "
                     f"byte-equal, pages equal apart from the lines that name the programs): "
                     f"{len(fl['equal_recorded'])} equal the recorded pages too"
                     + ((", and " + " and ".join(f"{p} ({v})" for p, v in fo.items())
                         + " differ from the recorded pages exactly as main-4d48844's pages do (its hit-back change)") if fo else "")),
        K8=K_EXPECT[:8], KTREE12=R['k_engine_tree'][:12], KX4_SHA=R['strength']['sha256'], KX4_SHA8=R['strength']['sha256'][:8],
        KX4_SECS=R['strength']['secs'], HARN8=HARN_NEW[:8], KX3_SECS=R['selfchecks']['kx3_secs'],
        SC_KM3_DIGEST=SC['km3'].rsplit('=', 1)[1], SC_KX3_DIGEST=SC['kx3'].rsplit('=', 1)[1],
        REFUSAL=f"{R['refusal_test']['ran']} of {R['refusal_test']['ran']} OK, on kx3's rebuild",
        STRENGTH_PY=(f"{py['ran']} tests; 1 failure, the expected one until the re-pin: "
                     f"`CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on`"),
        FLOOR_HEAD8=R['floor_ran_from']['head_at_record_time'][:8],
        REPLAY_TABLE=show(f'{REC}/REPLAY_TABLE.md').strip(), FLOOR_TABLE=show(f'{REC}/FLOOR_TABLE.md').strip(),
    )
    P['REPLAYS_LONG'] = P['REPLAYS_SHORT'] + ' (`logs/replays_S/`, `REPLAY_TABLE.md`)'
    P['FLOOR_LONG'] = P['FLOOR_SHORT'] + ' (`logs/floor_recheck_S/`, `FLOOR_TABLE.md`)'
    P['REPLAYS_RUN5'] = "equal main-4d48844's games game for game (17 of 17 runs that play games; goldfish's page and coverage byte-equal)"
    P['FLOOR_RUN5'] = f"equal main-4d48844's final pages ({fl['n']} of {fl['n']})"
    P.update({f'{n.upper()}_SHA': progs[n][0] for n in ORDER})
    P.update({f'{n.upper()}_BLOB': progs[n][1][:8] for n in ORDER})
    if final:
        txt = open(V['draft_checks'], encoding='utf-8').read().replace('\r', '').strip()
        if PH.search(txt) or not txt:
            sys.exit('the draft-checks text is empty or holds a placeholder')
        P['DRAFT_CHECKS'] = txt
    files = {}

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
    if any(r.get('name') == NAME for r in m['historical_releases']) or m['historical_releases'][-1]['name'] != 'main-c045ede':
        sys.exit('the manifest history is not as expected (tail main-c045ede, no main-affe56e)')
    hist = dict(old)
    hist['superseded'] = (f"{P['PIN']} by {NAME} (the Dual Fusion release, a partial compatibility update: the B4b, P-B, C1, SP1 "
                          f"and P-C data, dual-type Pokemon, the Ultra Beast list, upstream #430-#432, and the shared card-support "
                          f"refusal; {NEW_DIR}/)")
    m['historical_releases'].append(hist)
    m['available_release'] = {
        'name': NAME,
        'artifact': f'{NEW_DIR}/deckgym', 'sha256': progs['deckgym'][0],
        'legality_scan': f'{NEW_DIR}/legality_scan', 'legality_scan_sha256': progs['legality_scan'][0],
        'goldfish': f'{NEW_DIR}/goldfish', 'goldfish_sha256': progs['goldfish'][0],
        'goldfish_note': (old['goldfish_note'] + f" Since {NAME} it refuses (exit 2, before any game and before it writes its "
                          f"coverage file) a deck that holds a card the engine cannot play (deckgym::card_support, the check "
                          f"deckgym simulate makes); --allow-unsupported-cards lists those cards on stderr and runs anyway."),
        'source_commit': S,
        'source_working_tree': False,
        'built': (f"{P['BUILT_AT']} in WSL: cargo build --release --locked, --example legality_scan and --example goldfish, in the "
                  f"clean worktree /home/dacz8976/r6s_w at {S} (branch laptop/r6-release-2026-10-29: main ffe97adb, which holds "
                  f"the Dual Fusion merge and R5, plus the card-support refusal c0290e37 (merged as 6e1ff1d0) and the held "
                  f"tests-only fixes 3a9413cf and 59fc3054 (merged as {S[:8]}); engine/ tree {STREE[:8]}), with the shared target "
                  f"directory /home/dacz8976/dual_target (reused, not a fresh folder), CARGO_BUILD_JOBS 2, nice 19 "
                  f"({REC}/logs/build_R.log; times in logs/lane_r.log). source_commit is the built commit itself, and main's "
                  f"engine/ is byte-identical to it. The programs here are the tested bytes ({PD}/, the same git blobs), copied, "
                  f"never rebuilt; {REC}/RAN_SHA256.txt shows by sha256 that the replays, the floor and the self-checks ran "
                  f"exactly these programs (and the recorded kx3 rebuild)."),
        'identity_evidence': (
            f"{SEAM}/: (1) the release lane of Oct 28 (release_lane_2026-10-28/): on A (b290e223) and on A+B+C (d0792568), the "
            f"build, gencmp, card_status, the suite and 18 identity replays, each PASS against main-4d48844 (RELEASE_NOTES.md). "
            f"(2) R6's night on S itself ({REC}/): build OK; gencmp SAME, SAME; card_status: {P['CARD_STATUS']}; suite "
            f"{P['SUITE']} passed, 0 failed, 0 ignored; the folded hit-back tests {P['SWITCH_RUNS']}; the 18 identity replays "
            f"on S's programs, {P['REPLAYS_SHORT']}; the floor re-check pages of rl/results/floor_recheck_rules2_2026-10/, "
            f"{P['FLOOR_SHORT']}; kx3's rebuild against S (K {K_EXPECT[:8]}, /home/dacz8976/kx_r4/strength): self-checks "
            f"unchanged (km3 {P['SC_KM3_DIGEST']}, kx3 {P['SC_KX3_DIGEST']}). Engine changes since main-4d48844: {len(src_changed)} "
            f"files under engine/src (git diff --stat 4d488449 {S[:8]} -- engine/src), plus {', '.join(eng_other)} and test "
            f"files; engine/src/players/: 5 files, only so that the bots read the new cards (fuel_credit.rs and "
            f"value_functions.rs: printed type sets; public_pricing_player.rs: C1 012's Astonish audited; "
            f"weighted_random_player.rs: TakeTopDeckCardAndShuffle weight 5; opening_class.rs: a test comment); Cargo.lock and "
            f"Cargo.toml unchanged."),
        'approved': APPROVED,
        'purpose': (
            f"Official engine from {P['PIN']}: main-4d48844's engine (the Growl-to-0 rule and the hit back as attack damage on "
            f"rules switch 2; the kta and km players) plus the Dual Fusion release, a partial compatibility update (Dustin, Oct "
            f"28): the dual-type seam (a printed type set; every printed-type check reads any of a card's printed types, rules/05 "
            f"#32, fan-sourced), the B4b and P-B data with the B4b Trainer reprint arms, the corrected Ultra Beast list (non-ex "
            f"Buzzwole, Blacephalon ex, Guzzlord and Ultra Necrozma ex count for Lusamine, Ultra Thrusters, Beast Wall and "
            f"Beastite), upstream #430's Dual Fusion data, #431's 18 ex designs and #432's 6 Supporters (205 of the 260 C1, SP1 "
            f"and P-C printings Complete), and INFORMATION_MODEL v8 (Serena's Choice; v7 and v8 rows are not pooled); and R6's "
            f"shared card-support refusal (deckgym::card_support: deckgym simulate and optimize as before, and now goldfish, "
            f"refuse a deck that holds any of the other 55 printings, exit 2; --allow-unsupported-cards lists them and runs) and "
            f"the held tests-only fixes. engine/src/players/ changed only so that the bots read the new cards: km3 stays the "
            f"working pilot on both sides of the screen and the floor, and its play on the new cards is unmeasured. No new revert "
            f"switch: the engine reads the same {NSW_EXPECTED} DECKGYM_* variables as main-4d48844, none set by default; set one "
            f"and the program is another engine, so never set one in a recorded run. The slow report's program stays kx3 on "
            f"main-4d48844's engine until its re-pin (Dustin, Oct 21). The 0.7.2 RL add-on wheel and its run identities are "
            f"unchanged."),
    }
    m['latest_source_commit'] = S
    m['latest_source_note'] = (f"engine/ is tracked in git. The available release ({NAME}) was built from this commit's engine/; later "
                               f"engine commits are newer source, not the release build.")
    text = json.dumps(m, indent=2, ensure_ascii=False) + '\n'
    json.loads(text)
    files['project_manifest.json'] = text

    # ---- the release folder's README ------------------------------------------------------------------------------------
    tmpl = open(V['readme_template'], encoding='utf-8').read() if V.get('readme_template') else show(README_T)
    files[f'{NEW_DIR}/README.md'] = tmpl.replace('\r', '')

    # ---- START_HERE.md, CLAUDE.md, RUN5 ---------------------------------------------------------------------------------
    t = show('START_HERE.md')
    t = once(t, "`rl/engine-2026-10-21/` (`deckgym`, `legality_scan`, `goldfish`), main-4d48844: rules4",
             f"`{NEW_DIR}/` (`deckgym`, `legality_scan`, `goldfish`), @@NAME@@: rules4", 'START_HERE engine line')
    t = once(t, "; and since Oct 21 an attack cut to 0 by an attacker-side effect does 0",
             "; since Oct 21 an attack cut to 0 by an attacker-side effect does 0", 'START_HERE engine line, Oct 21')
    t = once(t, "plus upstream #385, #390, #401 (Fossil part) and #344 (narrow)), with the km pilot (kta + N2)",
             "plus upstream #385, #390, #401 (Fossil part) and #344 (narrow); and since @@PIN_SHORT@@ the Dual Fusion release, a "
             "partial compatibility update: the B4b, P-B, C1, SP1 and P-C cards (205 of the 260 new printings implemented; "
             "`deckgym simulate`, `optimize` and `goldfish` refuse a deck that holds one of the other 55), dual-type Pokémon, and "
             "the corrected Ultra Beast list), with the km pilot (kta + N2)", 'START_HERE engine line, history')
    files['START_HERE.md'] = t
    files['CLAUDE.md'] = once(show('CLAUDE.md'), CLAUDE_OLD, CLAUDE_NEW, 'CLAUDE.md engine paragraph')
    t = show('rl/RUN5.md')
    for i, (o, n) in enumerate(RUN5_EDITS):
        t = once(t, o, n, f'RUN5 [{i}]')
    files['rl/RUN5.md'] = t

    # ---- make_predictions.py, rl/strength/README.md ---------------------------------------------------------------------
    files[MP_P] = once(show(MP_P), MP_OLD, MP_NEW, 'make_predictions CURRENT_ENGINE')
    t = show(SR_P)
    for i, (o, n) in enumerate(SR_EDITS):
        t = once(t, o, n, f'rl/strength/README.md [{i}]')
    files[SR_P] = t

    # ---- the seam folder's notes and checklist --------------------------------------------------------------------------
    t = show(NOTES_P)
    for i, (o, n) in enumerate(NOTES_EDITS):
        t = once(t, o, n, f'RELEASE_NOTES [{i}]')
    t = once(t, "\n## Still to do (checklist)\n", "\n" + NOTES_R6 + "\n## Still to do (checklist)\n", 'RELEASE_NOTES R6 section')
    files[NOTES_P] = t
    t = show(CHECK_P)
    for i, (o, n) in enumerate(CHECK_EDITS):
        t = once(t, o, n, f'RELEASE_CHECKLIST [{i}]')
    files[CHECK_P] = t

    # ---- placeholders: fill every text; only @@DRAFT_CHECKS@@ may stay, and only in the draft -------------------------------
    for path in list(files):
        before = set(PH.findall(show(path))) if not path.startswith(NEW_DIR + '/') else set()
        if before:
            sys.exit(f'{path} already holds @@...@@ text at the base: {sorted(before)}')
        files[path], missing = fill(files[path], P, path)
        if missing - ({'DRAFT_CHECKS'} if not final else set()):
            sys.exit(f'{path}: no value for {sorted(missing)}')
    left = sorted({k for t in files.values() for k in PH.findall(t)})

    # ---- the commit -----------------------------------------------------------------------------------------------------
    for path, text in files.items():
        if '\r' in text:
            sys.exit(f'{path}: CR in the new text')
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'index'))
        git('read-tree', base, env=env)
        for path, text in files.items():
            blob = gs('hash-object', '-w', '--stdin', inp=text.encode('utf-8'))
            git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
        for n in ORDER:
            git('update-index', '--add', '--cacheinfo', f'100755,{progs[n][1]},{NEW_DIR}/{n}', env=env)
        git('update-index', '--add', '--cacheinfo', f'100644,{sums_blob},{NEW_DIR}/SHA256SUMS', env=env)
        tree = gs('write-tree', env=env)
    diff = gs('diff-tree', '-r', '--name-status', base, tree).splitlines()
    want_diff = sorted([f'A\t{NEW_DIR}/{n}' for n in ('README.md', 'SHA256SUMS', 'deckgym', 'goldfish', 'legality_scan')] +
                       [f'M\t{p}' for p in files if not p.startswith(NEW_DIR)])
    if sorted(diff) != want_diff:
        sys.exit('unexpected tree diff:\n' + '\n'.join(sorted(diff)))
    if gs('rev-parse', tree + ':engine') != STREE:
        sys.exit("the new tree's engine/ is not S's")
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
    msg = (FINAL_MSG if final else DRAFT_MSG).format(**P, BASE=base[:8], SEAM=SEAM, CO=CO)
    commit = gs('-c', 'user.name=dacz8976-creator', '-c', 'user.email=dacz8976@gmail.com', 'commit-tree', tree, '-p', base, '-F', '-',
                inp=msg.encode())
    branch = V.get('final_branch', 'laptop/r6-adoption-2026-10-29') if final else V.get('branch', 'laptop/r6-adoption-draft-2026-10-29')
    ref = f'refs/heads/{branch}'
    cur = subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', ref], capture_output=True, text=True).stdout.strip()
    if cur and not replace:
        sys.exit(f'{branch} exists ({cur[:8]}); pass --replace to move it')
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    print(f'{"FINAL" if final else "draft"} {commit} on {branch} (parent {base[:8]}, tree {tree[:8]})')
    print(gs('ls-tree', tree, NEW_DIR + '/'))
    print('next:', 'verify_r6.sh draft <new scratch worktree> ' + commit + ' <baseline folder>' if not final else
          'coordinator review, then main fast-forwards to ' + commit[:8] + ' (runbook step 12)')


# ---- texts (the old ones are copied from S; @@...@@ are filled from the record and VARS) -------------------------------------
CLAUDE_OLD = """- The official engine program is `rl/engine-2026-10-21/deckgym` (since Oct 21; main-4d48844: main-c045ede's engine plus the
  Growl-to-0 rule (an attack cut to 0 by an attacker-side effect does 0, no Weakness), an attack's hit back as attack
  damage for the Attacking Pokémon's own cards, and upstream #385, #390, #401 (Fossil part), #344 (narrow) and #367/#418;
  `engine/src/players/` unchanged; `rl/engine-2026-10-21/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-12/`, `-10-02/`, `-09-30/`, `-09-28/`,
  `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
"""
CLAUDE_NEW = """- The official engine program is `rl/engine-2026-10-29/deckgym` (since @@PIN_SHORT@@; @@NAME@@: main-4d48844's engine plus
  the Dual Fusion release, a partial compatibility update: the B4b, P-B, C1, SP1 and P-C cards (205 of the 260 new
  printings implemented; `deckgym simulate`, `optimize` and `goldfish` refuse a deck that holds one of the other 55),
  dual-type Pokémon and the corrected Ultra Beast list; `engine/src/players/` changed only so that the bots read the new
  cards; `rl/engine-2026-10-29/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-21/`, `-10-12/`, `-10-02/`, `-09-30/`,
  `-09-28/`, `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
"""

RUN5_PINNED_R6 = (
    "  - **Pinned @@PIN_SHORT@@** (`results/dual_type_seam_2026-10-23/`: RELEASE_NOTES.md with its section \"R6\", RELEASE_CHECKLIST.md "
    "R6, and the build record `r6_release/`). Dustin, Oct 28, in the laptop session's chat at about 23:00Z (verbatim): \"Yes\", to "
    "adopting d0792568 into main with R5-R7 as follow-through (RELEASE_NOTES.md; coordinator-069). A \"partial compatibility "
    "update\": Astra's qualification, via coordinator-069. The card-support refusal for goldfish and the slow report is "
    "coordinator-071's, which Dustin was told about at about 00:05Z on Oct 29 and did not object to (coordinator-072).\n"
    "    - Not re-run and not new-engine evidence (labelled pre-R6/v7; nothing is recomputed): kx3 and its recorded games, the "
    "mixed kt/kta clause-(d) tables (ec7e1a8), scoreboard v3's frozen cells and thresholds and kta3's status, km3's thresholds, "
    "the ladder predictions (never overwritten), run 3, K21 and the exam rows (v7), and the frozen judge. Dustin, Oct 21, via "
    "coordinator-072 (verbatim): \"Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a "
    "future decision relies on them.\"\n"
    "    - The slow report: not moved by this pin. Dustin, Oct 21, via coordinator-072 (verbatim): \"Move the slow-report program "
    "only after its replay check passes. Until then, its reports must clearly identify the old engine.\" It stays "
    "`/home/dacz8976/kx_r3/strength` (kx3 "
    "on main-4d48844, sha256 7d046b6f…) until its kx3 replay check on @@NAME@@ passes; its pages say \"kx3 (d513e37b, on "
    "main-4d48844)\", and no slow report counts as current meanwhile (`make_predictions.py`; `rl/strength/README.md`). The "
    "re-pin's program is built: kx3's six files on S (K @@K8@@, local branch `laptop/kx3-on-r6-2026-10-29`), "
    "`/home/dacz8976/kx_r4/strength`, both self-checks equal to the pin's texts. Until that re-pin (runbook step 15), "
    "`CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` "
    "(`rl/strength/test_slow_report_registration.py`, 1 of 244) fails on main and the cloud `--program` route must not rebuild "
    "from main; the laptop's pinned slow report is unaffected.\n")

RUN5_EDITS = [
    # [0] the status bullet: the new engine first, main-4d48844's text kept as the previous engine
    ("- **Official engine:** `rl/engine-2026-10-21/`, main-4d48844 (pinned Oct 21; main-c045ede's engine plus the Growl-to-0 rule",
     "- **Official engine:** `rl/engine-2026-10-29/`, @@NAME@@ (pinned @@PIN_SHORT@@, R6 of the Dual Fusion release: "
     "`results/dual_type_seam_2026-10-23/RELEASE_NOTES.md`). It is main-4d48844's engine plus the Dual Fusion release, a partial "
     "compatibility update (Dustin, Oct 28): the B4b, P-B, C1, SP1 and P-C cards (205 of the 260 new printings implemented; "
     "`deckgym simulate`, `optimize` and `goldfish` refuse a deck that holds one of the other 55), dual-type Pokémon read as any "
     "of their printed types, the corrected Ultra Beast list, INFORMATION_MODEL v8 and the held tests-only fixes; "
     "`engine/src/players/` changed only so that the bots read the new cards, and their play on those cards is unmeasured. On "
     "S's programs the 18 identity replays of earlier runs @@REPLAYS_RUN5@@, and the floor re-check pages @@FLOOR_RUN5@@ "
     "(`results/dual_type_seam_2026-10-23/r6_release/`). Old rows are labelled pre-R6/v7 and nothing is recomputed "
     "(coordinator-072, on Dustin's Oct 21 words). The previous engine, `rl/engine-2026-10-21/`, main-4d48844 (pinned Oct 21), "
     "is main-c045ede's engine (plus the Growl-to-0 rule"),
    ("Rules switch 2's engine (`rl/engine-2026-10-12/`, main-c045ede; `results/engine_switch_rules2_2026-10/`), the Oct 2 engine",
     "main-4d48844's engine (`rl/engine-2026-10-21/`; `results/engine_candidate_2026-10-20/`), rules switch 2's engine "
     "(`rl/engine-2026-10-12/`, main-c045ede; `results/engine_switch_rules2_2026-10/`), the Oct 2 engine"),
    # [2] the new pin's bullets go first; the Oct 21 ones stay, named as main-4d48844's
    ("\n  - **Pinned Oct 21** (`results/engine_candidate_2026-10-20/`: PLAN.md and its Oct 20 addendum",
     "\n" + RUN5_PINNED_R6 + "  - **Pinned Oct 21** (main-4d48844; `results/engine_candidate_2026-10-20/`: PLAN.md and its Oct 20 addendum"),
    ("and count as current (`make_predictions.py`).",
     "and counted as current (`make_predictions.py`) until @@NAME@@'s pin (@@PIN_SHORT@@)."),
    ("from the hit back's change, and both still clear the floor; 0 unexplained; `results/engine_candidate_2026-10-20/release/`).",
     "from the hit back's change, and both still clear the floor; 0 unexplained; `results/engine_candidate_2026-10-20/release/`), "
     "and on @@NAME@@'s deckgym before its pin (@@FLOOR_SHORT@@; `results/dual_type_seam_2026-10-23/r6_release/`)."),
    ("Development real error (recorded on earlier engines; not re-measured on main-4d48844: Dustin, Oct 21, no re-baselining)",
     "Development real error (recorded on earlier engines; not re-measured on main-4d48844 or @@NAME@@: Dustin, Oct 21, no "
     "re-baselining, kept at R6 by coordinator-072)"),
    ("rules switch 2 (Oct 11-12), and the Oct 20 engine candidate (pinned Oct 21).",
     "rules switch 2 (Oct 11-12), the Oct 20 engine candidate (pinned Oct 21), and the Dual Fusion release (merged Oct 28; its "
     "programs pinned @@PIN_SHORT@@, `results/dual_type_seam_2026-10-23/`)."),
    ("they are rebuilt on the current engine only when a future decision relies on them.",
     "they are rebuilt on the current engine only when a future decision relies on them. **The same at @@NAME@@'s pin "
     "(@@PIN_SHORT@@; coordinator-072, on Dustin's Oct 21 words):** no baseline moved; the old rows are labelled pre-R6/v7 "
     "(INFORMATION_MODEL v8 is a pooling boundary anyway), and nothing is recomputed."),
]

MP_OLD = """CURRENT_ENGINE = {
    "label": "main-4d48844 (Growl-to-0, the hit back as attack damage, upstream fixes; pinned Oct 21)",
    "harness_engine_trees": ["64de03e2c3c2"],          # slow reports / exams: "engine tree <12 hex>" in manifest.json (kx3 on main-4d48844)
    "floor_engines": ["rl/engine-2026-10-21/deckgym"],  # floor pages: "- Engine: <path>"
}
"""
MP_NEW = """CURRENT_ENGINE = {
    "label": "@@NAME@@ (the Dual Fusion release, a partial compatibility update; pinned @@PIN_SHORT@@)",
    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until the slow report's re-pin on @@NAME@@)
    "floor_engines": ["rl/engine-2026-10-29/deckgym"],  # floor pages: "- Engine: <path>"
}
"""

SR_EDITS = [
    ("The default is `origin/main`; its `engine/` tree is the official engine's (main-4d48844 since Oct 21, tree `46239c19`; the "
     "slow report's pinned program has been kx3's frozen players on this engine since its re-pin (Oct 22; this engine plus kx3's "
     "player files: tree `64de03e2c3c2`), see \"The slow report\" below), and the script prints",
     "The default is `origin/main`; its `engine/` tree is the official engine's (@@NAME@@ since @@PIN_SHORT@@, tree `@@STREE8@@`; "
     "the slow report's pinned program stays kx3's frozen players on the previous engine, main-4d48844 (re-pinned Oct 22: that "
     "engine plus kx3's player files, tree `64de03e2c3c2`), until its re-pin on @@NAME@@, see \"The slow report\" below), and the "
     "script prints"),
    ("**Engine (since the slow report's re-pin):** the pinned program below is kx3's frozen players on main-4d48844's engine",
     "**Engine (since @@NAME@@'s pin, @@PIN_SHORT@@, until the slow report's re-pin):** the pinned program below is still built on "
     "the OLD engine, main-4d48844 (next paragraph), for kx3 and for its km3 baseline alike. Every page names it in its headline "
     "(\"kx3 (d513e37b, on main-4d48844)\"), and `make_predictions.py` counts none of these reports as current. Until the re-pin, "
     "whoever hands a slow report to Dustin says in plain words that it was played on the OLD engine (main-4d48844), not the "
     "official @@NAME@@. That engine knows none of the B4b, P-B 095-103, C1, SP1 or P-C printings. The re-pin moves the program "
     "to @@NAME@@'s engine only after its kx3 replay check passes (Dustin, Oct 21).\n\n"
     "**Engine (since the slow report's Oct 22 re-pin):** the pinned program below is kx3's frozen players on main-4d48844's engine"),
]

NOTES_EDITS = [
    ("# Release notes: Dual Fusion (C1), a partial compatibility update, merged into main Oct 28\n",
     "# Release notes: Dual Fusion (C1), a partial compatibility update, merged into main Oct 28; official programs from @@PIN_SHORT@@ (R6, @@NAME@@)\n"),
    ("## What it does not switch: the official engine programs\nSTART_HERE's official-engine line, `project_manifest.json` and "
     "`current_engine.py` still name `rl/engine-2026-10-21/` (main-4d48844).",
     "## What the merge did not switch: the official engine programs (switched at R6, @@PIN_SHORT@@: section \"R6\" below)\n"
     "Until R6, START_HERE's official-engine line, `project_manifest.json` and `current_engine.py` named `rl/engine-2026-10-21/` "
     "(main-4d48844)."),
    ("The branch lands in the same merge as the re-pin, and `test_slow_report_registration.py` is run after it.",
     "Planned to land with the re-pin, the branch landed instead with R6's engine programs: it is part of S, the built commit, and "
     "main's `engine/` must be S's tree. So from main's move (@@PIN_SHORT@@) until the re-pin this one test fails on main, and "
     "the cloud route refuses a rebuild from main's checkout; the laptop's pinned program is unaffected. "
     "`test_slow_report_registration.py` is run again after the re-pin."),
    ("- **R6:** the switch. It adds the shared card-support refusal to goldfish and the slow report first (above); the cargo build "
     "runs at night hours.",
     "- **R6:** the engine programs switched @@PIN_SHORT@@ (section \"R6\" above); the slow-report re-pin follows its kx3 replay "
     "check."),
]

NOTES_R6 = """## R6: the official programs switch to @@NAME@@ (@@PIN_SHORT@@)
Dustin's words, verbatim, with their sources:
- **The adoption.** Oct 28, in the laptop session's chat at about 23:00Z: "Yes", to adopting d0792568 into main with R5-R7 as follow-through (top of this file; coordinator-069). R6 is this switch (`RELEASE_CHECKLIST.md`, R6: "part of the adoption question D answered on Oct 28"). It is a "partial compatibility update": Astra's qualification, via coordinator-069.
- **The two-step pin.** His Oct 21 words, via coordinator-072: "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine."
- **Baselines as on Oct 21.** His Oct 21 words, via coordinator-072: "Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them." Old rows are labelled pre-R6/v7, and nothing is recomputed.
- **goldfish's and the slow report's refusal** is coordinator-071's decision. At about 00:05Z on Oct 29 the coordinator told Dustin that two of our own tools, goldfish and the slow report, did not block the 55 unsupported printings, and that both would refuse them, each with a test, before the rebuild. He did not object (coordinator-072). The refusal stops unsupported decks only; it changes no result.

### What the adoption activates
- **The three programs** in `rl/engine-2026-10-29/` (`deckgym` @@DECKGYM_BLOB@@… blob, sha256 @@DECKGYM_SHA@@; `legality_scan` @@LEGALITY_SCAN_SHA@@; `goldfish` @@GOLDFISH_SHA@@): S's tested bytes, the same git blobs as `r6_release/programs_final/`, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read it, so the screen and the floor switch with the manifest. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `rl/engine-2026-10-29/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **goldfish's refusal.** The brew pages and the floor's coverage step now stop on a deck that holds an unsupported card (exit 2) instead of counting and skipping its panicking games. On the replayed decks nothing changes: goldfish's page and coverage file are byte-equal to the reference.
- **The slow-report program: not moved by this commit.** The pinned program stays kx3 on main-4d48844's engine (`/home/dacz8976/kx_r3/strength`, sha256 7d046b6f…; 87a7f340, engine tree 64de03e2). Every page names it in its headline ("kx3 (d513e37b, on main-4d48844)"; `rl/strength/README.md` says so too), and `make_predictions.py` counts no slow report as current. The re-pin's program is built and checked: kx3's six files on S (K @@K8@@, local branch `laptop/kx3-on-r6-2026-10-29`, engine tree @@KTREE12@@), built with `rl/strength/build.sh` at STRENGTH_JOBS 2 (`/home/dacz8976/kx_r4/strength`, sha256 @@KX4_SHA@@, @@KX4_SECS@@ s; harness @@HARN8@@…; build record OK); both self-checks equal to the pin's texts (km3 @@SC_KM3_DIGEST@@; kx3 @@SC_KX3_DIGEST@@, @@KX3_SECS@@ s). Its kx3 replay check comes next (runbook steps 13-15).
- **The harness source moves with S, so one test is red until step 15.** S holds the card-support refusal in `rl/strength/src/main.rs` (harness c4f7da21…; the pin says bf9c5d68…). From main's move until runbook step 15, the slow-report re-pin after the kx3 replay check, `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` in `rl/strength/test_slow_report_registration.py` fails on main (1 of 244); the re-pin turns it green. Until then the cloud `--program` route must not rebuild from main. The laptop's pinned slow report is unaffected. The preflight section above planned this branch to land with the re-pin; it is part of S, so it lands with the engine (accepted, coordinator-076).

### Release identity
- Built from S = @@S@@ (@@BUILT_AT@@); engine tree @@STREE12@@. main's `engine/` after the adoption is that tree, byte for byte: no exception. The tests-only fixes held back on Oct 21 are folded into S, so no tests-only exception remains.
- Built in the clean worktree at S with the shared target directory `/home/dacz8976/dual_target` (reused), not in a fresh folder as on Oct 21. The committed programs are the bytes the night's checks ran: `r6_release/RAN_SHA256.txt` shows by sha256 that each replay and each floor piece ran `programs/R`'s programs, equal to `programs_final/`, and that the self-checks ran `/home/dacz8976/kx_r4/strength`, equal to its build record. `r6_release/RUN_CONTEXT.txt` names the checkout the floor and the replays read (`/home/dacz8976/pincand` at @@FLOOR_HEAD8@@) and shows their runners byte-equal to S's.
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd rl/engine-2026-10-29 && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD rl/engine-2026-10-29/`: deckgym @@DECKGYM_BLOB@@…, legality_scan @@LEGALITY_SCAN_BLOB@@…, goldfish @@GOLDFISH_BLOB@@…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `rl/engine-2026-10-29/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.
  5. `git rev-parse HEAD:engine` prints @@STREE@@, S's engine tree.

### R6's night on S (`r6_release/`)
| Check | Result |
|---|---|
| Build: deckgym, legality_scan, goldfish | OK in @@BUILD_SECS@@ s (@@BUILT_AT@@) |
| gencmp (`card_ids.rs`, `database.rs`) | SAME, SAME |
| card_status | @@CARD_STATUS@@ |
| Suite | @@SUITE@@ passed, 0 failed, 0 ignored (@@SUITE_SECS@@ s) |
| The folded hit-back tests under the switches | @@SWITCH_RUNS@@ |
| 18 identity replays (side r = S's programs) | @@REPLAYS_SHORT@@ |
| Floor re-check, 12 pieces, on S's deckgym | @@FLOOR_SHORT@@ |
| kx3's rebuild on K | `/home/dacz8976/kx_r4/strength`, sha256 @@KX4_SHA8@@…, build record OK (the engine tree as archived is K's; harness @@HARN8@@…; jobs 2) |
| Self-checks on it | km3 @@SC_KM3_DIGEST@@ and kx3 @@SC_KX3_DIGEST@@: equal to the pin's texts |
| Card-support refusal test (`test_strength_card_support`, a real program) | @@REFUSAL@@ |
| `rl/strength` Python suite | @@STRENGTH_PY@@ |

**The replays** (`r6_release/REPLAY_TABLE.md`):

@@REPLAY_TABLE@@

**The floor re-check pages** (`r6_release/FLOOR_TABLE.md`):

@@FLOOR_TABLE@@

The floor ran from the laptop's main checkout (`/home/dacz8976/pincand` at @@FLOOR_HEAD8@@) with S's `deckgym`. floor.py takes coverage from the official release's goldfish, which that night was `rl/engine-2026-10-21/goldfish`, so the re-check itself does not exercise the new goldfish. Its replay row above does, and S's goldfish run on the 11 floor decks the way floor.py runs it (coverage only, no games) gives coverage files byte-equal to these (`r6_release/logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt`).

**The floor's acceptance rule was corrected after the run (games unchanged, not re-run; reviewed by the coordinator, coordinator-080).** floor2.py's own comparison says DIFFERS for 11 of the 12 pieces, for one line only: each page's coverage line names the official goldfish, `rl/engine-2026-10-21/goldfish` that night where main-4d48844's final pages name `rl/engine-2026-10-12/goldfish`, because the release moved with the Oct 21 adoption after those pages were made. The coverage files themselves are byte-equal. The night's rule did not allow for that line and marked the step FAILED (the marker is kept in the record). The corrected rule: games and coverage byte-equal to main-4d48844's final pages, and each page equal after normalising only the engine path and that goldfish line (`r6_release/tools/floorS_recompare.sh`; its output is `r6_release/logs/floor_recheck_S/RECOMPARE.txt`). All 12 pass.

### Tied to the old engine: not re-run, labelled pre-R6/v7, nothing recomputed
1. **The slow report and kx3's recorded games**, until the re-pin (above). The reports so far and kx3's replay games of Oct 22 stay main-4d48844's, or older.
2. **Scoreboard v3's frozen cells and thresholds, kta3's status, km3's thresholds, the mixed kt/kta clause-(d) tables and RUN5's development real error:** records of their old engines, as on Oct 21.
3. **The ladder predictions** (`rl/results/ladder_validation/predictions/`), never overwritten. `read_ladder.py` prints "NOT the current engine now" for them.
4. **Run 3, K21 and the exam rows:** v7, frozen, not pooled with v8 rows.
5. **The Oct 12 floor re-check pages and their Oct 21 replays:** records beside the new ones above, never replacements.
6. **The deck journal's "current engine" flags** mean "current when added".

What carries over unchanged: every replayed row that came out equal.

### Checks of the adoption commit (a scratch worktree, before main moved; no engine run)
@@DRAFT_CHECKS@@

### Left as is on purpose
- `engine/UPSTREAM.md` stays as built: it is part of S's tree.
- `rules/`: no engine-status line changes at R6. The Ultra Beast correction has no status line there, and `rules/05` #32 still names the seam branch.
- `rl/RUN5.md`'s A5 item still names `rl/engine-2026-10-21/`: the reproduction it asks for ran against that engine (the release lane's "v f").
- The laptop's `pincand_work` (programs/R, the RR archive, the replay games) stays until the slow report's re-pin.
"""

CHECK_EDITS = [
    ("| L builds; C reviews; D decides | to do (part of the adoption question D answered on Oct 28). Before the switch,",
     "| L builds; C reviews; D decides | **Engine programs switched @@PIN_SHORT@@:** `rl/engine-2026-10-29/`, @@NAME@@, built from S "
     "affe56e8 (main ffe97adb + this refusal, merged as 6e1ff1d0, + the fold of 3a9413cf and 59fc3054); build record "
     "`r6_release/` (@@RECORD8@@); RELEASE_NOTES.md, \"R6\". **Still to do:** the slow-report re-pin after its kx3 replay check "
     "(two-step pin, coordinator-072): K @@K8@@, `/home/dacz8976/kx_r4/strength`, self-checks equal to the pin. Part of the "
     "adoption question D answered on Oct 28. Before the switch,"),
    ("until R6's re-pin records that hash in `slow_report_pin.json`; the branch lands with the re-pin |",
     "until R6's re-pin records that hash in `slow_report_pin.json`. The branch landed with the engine programs (it is in S), not "
     "with the re-pin (accepted, coordinator-076): "
     "`CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` in "
     "`rl/strength/test_slow_report_registration.py` (1 of 244) fails on main from the switch until step 15, the slow-report "
     "re-pin after the kx3 replay check, which turns it green; until then the cloud `--program` route must not rebuild from main. "
     "The laptop's pinned slow report is unaffected |"),
]

DRAFT_MSG = """R6 DRAFT, not on main: pin the engine programs as {NAME} ({NEW_DIR}/)

The R6 adoption commit, drafted for the coordinator's review (runbook steps 10-11); main moves only
after it. Parent {BASE}, the release branch's build record (S {S8} plus r6_release/). Generator:
{REC}/tools/adopt_r6.py. Its --final run fills the release notes' "Checks of the adoption
commit" after verify_r6.sh, and changes nothing else.

- {NEW_DIR}/: S's tested programs (deckgym {DECKGYM_SHA}, the same blobs as
  {PD}/, mode 100755), SHA256SUMS, README.md. engine/ is S's tree, {STREE8}.
- project_manifest.json: main-4d48844 moves to historical_releases (superseded); available_release is
  {NAME} (source_commit {S8}); latest_source_*.
- START_HERE.md and CLAUDE.md pin lines; rl/RUN5.md (the status bullet, the floor re-check, the yardstick,
  the finished list, the baselines exception).
- make_predictions.py CURRENT_ENGINE moves; no slow-report tree until the re-pin.
- rl/strength/README.md: a notice that the slow report's program is still the old engine's.
- {SEAM}/RELEASE_NOTES.md (section "R6") and RELEASE_CHECKLIST.md (R6's state).

{CO}
"""

FINAL_MSG = """Pin the engine: {NAME} ({NEW_DIR}/), the Dual Fusion release's programs (R6)

Adopted on Dustin's word of Oct 28: his answer to the Dual Fusion adoption question, which included R6
(verbatim in {SEAM}/RELEASE_NOTES.md and the manifest's "approved").
Parent {BASE}, the release branch's build record of S ({S8}). Equal to the verified draft {DRAFT8}
except the release notes' "Checks of the adoption commit".

- {NEW_DIR}/: S's tested programs (deckgym {DECKGYM_SHA}, the same blobs as
  {PD}/, mode 100755), SHA256SUMS, README.md. engine/ is the built commit's tree, {STREE8}.
- project_manifest.json: main-4d48844 moves to historical_releases (superseded); available_release is
  {NAME} (source_commit {S8}); latest_source_*.
- START_HERE.md and CLAUDE.md pin lines; rl/RUN5.md (the status bullet, the floor re-check, the yardstick,
  the finished list, the baselines exception).
- make_predictions.py CURRENT_ENGINE moves (no slow-report tree: the slow report stays on main-4d48844's
  engine until its re-pin, which happens only after its kx3 replay check passes).
- rl/strength/README.md: a notice that the slow report's program is still the old engine's.
- Release notes: {SEAM}/RELEASE_NOTES.md (section "R6"); RELEASE_CHECKLIST.md (R6's state).

{CO}
"""

if __name__ == '__main__':
    main()
