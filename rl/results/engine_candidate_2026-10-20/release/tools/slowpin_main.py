#!/usr/bin/env python3
"""The slow report's re-pin ON MAIN, after its replay check passed: kx3 on main-4d48844's engine (VARS["f_commit"]).

  slowpin_main.py VARS.json [--replace] [--dry-run]

Dustin, Oct 21 (verbatim, relayed by the coordinator): "Move the slow-report program only after its replay check passes." The replay
check's record (rl/results/kx3_on_engine_2026-10-21/, READING.md with the verdict "pass") must be on VARS["check_branch"] at
VARS["check_commit"]; this refuses unless READING.md says the check passed.
One merge commit from a private index, nothing checked out, main and the working tree untouched, nothing pushed: first parent VARS["base"]
(main), second parent the check's commit (its branch starts on main and adds only its folder, so the merge brings exactly that folder).
It also changes rl/strength/slow_report_pin.json (program, its sha256 twice, engine_ref, engine_tree, pilot_label, engine,
pilot_provenance, reference_provenance; the self-check texts, the harness hash and every other field stay), rl/strength/README.md (the
cloud route's ref, branch, tree and program; the old-engine notice becomes the re-pin's), and make_predictions.py's CURRENT_ENGINE (the
new harness tree); it adds rl/results/engine_candidate_2026-10-20/slow_pin/ (CERT.md, the build record, the self-check lines). Refuses
unless the build record and both self-checks are what the pin needs. Written from slowpin_final.py (the Oct 20 draft tool, kept)."""
import hashlib, json, os, re, subprocess, sys, tempfile

REPO = '/home/dacz8976/pincand'
CAND = 'rl/results/engine_candidate_2026-10-20'
CHECK = 'rl/results/kx3_on_engine_2026-10-21'
HARN = 'bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e'
OLD = dict(program='/home/dacz8976/kx_r2/strength', sha='76df495bef0b057fd28b4991dce76d3e3e1772667694161c945f17364f9c4e08',
           ref='cd20a97a2e76897fae9883389cee4bf7ce5b3d97', tree='4ebb30a941737d16b80adddbd1466761e0670e63')
SC = dict(km3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1',
          kx3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')


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
        sys.exit(f'{what}: the old text occurs {n} times, not once: {old[:90]!r}')
    return text.replace(old, new)


def main():
    V = json.load(open(sys.argv[1]))
    base = gs('rev-parse', V['base'] + '^{commit}')
    K = gs('rev-parse', V['K'] + '^{commit}')
    kbr = V['kbranch']
    if gs('rev-parse', f'refs/heads/{kbr}') != K:
        sys.exit(f'{kbr} is not {K[:8]}')
    F = gs('rev-parse', V['f_commit'] + '^{commit}')
    NAME = 'main-' + F[:7]
    FB, FTREE = F[:8], gs('rev-parse', F + ':engine')[:8]
    if F not in gs('log', '-1', '--format=%P', K).split():
        sys.exit('K is not a merge onto the final candidate')
    if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', F, base]).returncode:
        sys.exit(f'{NAME} is not on the base {base[:8]}: the engine is not adopted there')
    T = gs('rev-parse', f'{K}:engine')
    # the replay check: its commit, its folder only, and READING.md's verdict
    dry = '--dry-run' in sys.argv

    def need(ok, why):  # a dry run reports what a real run would refuse, and goes on
        if not ok:
            if dry:
                print(f'DRY RUN: a real run would refuse here: {why}')
            else:
                sys.exit(why)

    C = gs('rev-parse', V['check_commit'] + '^{commit}')
    need(gs('rev-parse', f"refs/remotes/origin/{V['check_branch']}") == C, f"origin/{V['check_branch']} is not {C[:8]} (push the check's record first)")
    mb = gs('merge-base', base, C)
    touched = gs('diff', '--name-only', mb, C).splitlines()
    if not touched or any(not p.startswith(CHECK + '/') for p in touched):
        sys.exit(f'the check branch touches more than its folder: {[p for p in touched if not p.startswith(CHECK + "/")][:5]}')
    if subprocess.run(['git', '-C', REPO, 'cat-file', '-e', f'{base}:{CHECK}'], capture_output=True).returncode == 0:
        sys.exit(f'{CHECK} already exists on the base')
    r = subprocess.run(['git', '-C', REPO, 'show', f'{C}:{CHECK}/READING.md'], capture_output=True)
    reading = r.stdout.decode('utf-8') if r.returncode == 0 else ''
    need(re.search(r'^\*\*Verdict: pass\.\*\*', reading, re.M), 'READING.md is missing or does not say "**Verdict: pass.**": no re-pin')
    prog = V['program']
    rec = json.load(open(prog + '.build.json'))
    psha = hashlib.sha256(open(prog, 'rb').read()).hexdigest()
    want = dict(engine_ref=K, engine_tree_archived=T, harness_source_sha256=HARN, jobs='2', program_sha256=psha, program=prog)
    bad = {k: (rec.get(k), v) for k, v in want.items() if rec.get(k) != v}
    if bad:
        sys.exit(f'build record: {bad}')
    sc = {p: open(os.path.join(V['cert_dir'], f'sc_{p}.out')).read().strip() for p in ('km3', 'kx3')}
    if sc != SC:
        sys.exit(f'self-checks differ from the pin texts: {sc}')
    if not os.path.exists(os.path.join(V['cert_dir'], 'sc_kx3.done')) or not os.path.exists(os.path.join(V['cert_dir'], 'sc_km3.done')):
        sys.exit('self-check .done markers missing')
    K8, T12, P8, C8 = K[:8], T[:12], psha[:8], C[:8]
    built = rec['built_at']
    show = lambda p: git('show', f'{base}:{p}').decode('utf-8')
    files = {}

    # ---- the pin ------------------------------------------------------------------------------------------------
    p = 'rl/strength/slow_report_pin.json'
    t = show(p)
    t = once(t, '"pilot_label": "kx3 (d513e37b, on main-c045ede)"', f'"pilot_label": "kx3 (d513e37b, on {NAME})"', 'pilot_label')
    t = once(t, f'"program": "{OLD["program"]}"', f'"program": "{prog}"', 'program')
    t = once(t, f'"program_sha256": "{OLD["sha"]}"', f'"program_sha256": "{psha}"', 'program_sha256')
    t = once(t, f'"selfcheck_measured_on_sha256": "{OLD["sha"]}"', f'"selfcheck_measured_on_sha256": "{psha}"', 'measured_on')
    t = once(t, f'"engine_ref": "{OLD["ref"]}"', f'"engine_ref": "{K}"', 'engine_ref')
    t = once(t, f'"engine_tree": "{OLD["tree"]}"', f'"engine_tree": "{T}"', 'engine_tree')
    m = re.search(r'\n "engine": "[^"\n]*",\n "pilot_provenance": "[^"\n]*",\n "reference_provenance": "[^"\n]*",\n', t)
    if not m:
        sys.exit('engine/provenance block not found')
    t = t.replace(m.group(0), (
        f'\n "engine": "{kbr} {K8} engine tree {T12}: the frozen kx3\'s players (claude/playout-pilot d513e37b, byte for byte) on '
        f'{NAME}\'s engine (the Growl-to-0 rule, the hit back as attack damage, and upstream #385, #390, #401 Fossil part, #344 narrow, #367/#418; built commit {FB}), '
        f'built on the laptop {built[:10]} with rl/strength/build.sh (harness bf9c5d68, STRENGTH_JOBS=2); gate 1: km3\'s self-check '
        f'81b572198c04d5d1, the pinned km3; kx3\'s self-check 31d638dbc818b0fa, equal to the old pin\'s; KX_EXTRA_LISTS unset; the replay check: '
        f'202 of 202 kx3 and 202 of 202 km3 development games identical ({CHECK}/READING.md). Replaces the Oct 12 build (cd20a97a on main-c045ede\'s engine, tree 4ebb30a94173, program 76df495b); '
        f'record {CAND}/slow_pin/CERT.md",\n'
        f' "pilot_provenance": "kx3 from claude/playout-pilot@d513e37b, frozen Oct 4-5; on rules switch 2\'s engine Oct 12 '
        f'(laptop/kx3-on-rules2 cd20a97a); on {NAME}\'s engine since {built[:10]} ({kbr} {K8})",\n'
        f' "reference_provenance": "km3 in the same build; its self-check is the pinned km3\'s 81b572198c04d5d1 (the 240-game '
        f'field-for-field check of Oct 12 was on main-c045ede\'s engine and is not repeated)",\n'))
    pin = json.loads(t)
    assert pin['engine'].startswith(kbr + ' ') and f'engine tree {T12}' in pin['engine'] and K8 in pin['engine']
    assert 'claude/playout-pilot@d513e37b' in pin['pilot_provenance'] and K8 in pin['pilot_provenance'] and 'd513e37b' in pin['pilot_label']
    assert pin['selfcheck'] == SC and pin['harness_source_sha256'] == HARN and pin['program'].endswith('/strength')
    files[p] = t

    # ---- README: the cloud route, and the old-engine notice -----------------------------------------------------
    p = 'rl/strength/README.md'
    t = show(p)
    t = once(t, '("kx3 (d513e37b, on main-c045ede) on your deck v km3', f'("kx3 (d513e37b, on {NAME}) on your deck v km3', 'README 54')
    t = once(t, f'(`{OLD["program"]}`, sha256 `76df495b…`,', f'(`{prog}`, sha256 `{P8}…`,', 'README 57')
    t = once(t, "The commit `cd20a97a2e76897fae9883389cee4bf7ce5b3d97` is on the branch `origin/laptop/kx3-on-rules2` (the frozen kx3 players, `claude/playout-pilot` d513e37b, on main-c045ede's engine: rules switch 2)",
             f"The commit `{K}` is on the branch `origin/{kbr}` (the frozen kx3 players, `claude/playout-pilot` d513e37b, on {NAME}'s engine: the Growl-to-0 rule, the hit back as attack damage and upstream fixes)", 'README 71 commit')
    t = once(t, "(`git fetch origin laptop/kx3-on-rules2`), and", f"(`git fetch origin {kbr}`), and", 'README 71 fetch')
    t = once(t, "`mkdir -p /tmp/cd20 && git archive cd20a97a engine | tar -x -C /tmp/cd20 && (cd /tmp/cd20/engine && env",
             f"`mkdir -p /tmp/{K[:4]} && git archive {K8} engine | tar -x -C /tmp/{K[:4]} && (cd /tmp/{K[:4]}/engine && env", 'README 71 archive')
    t = once(t, f"(`{OLD['program']}` on the laptop:", f"(`{prog}` on the laptop:", 'README 71 path')
    t = once(t, f"bash rl/strength/build.sh {OLD['ref']} $HOME/slow_report_kx3/strength", f"bash rl/strength/build.sh {K} $HOME/slow_report_kx3/strength", 'README 71 build')
    t = once(t, "**The engine tree must be `4ebb30a94173…`", f"**The engine tree must be `{T12}…`", 'README 71 tree')
    t = once(t, "the laptop's `76df495b…`", f"the laptop's `{P8}…`", 'README 71 sha')
    t = once(t, "(`git fetch origin laptop/kx3-on-rules2` for the pinned commit", f"(`git fetch origin {kbr}` for the pinned commit", 'README 75')
    notice = re.findall(r"^\*\*Engine \(since [^\n]*until the slow report's re-pin\):\*\*[^\n]*$", t, re.M)
    if len(notice) != 1:
        sys.exit(f'README: {len(notice)} old-engine notices, not 1')
    t = t.replace(notice[0], (
        f"**Engine (since the slow report's re-pin):** the pinned program below is kx3's frozen players on {NAME}'s engine "
        f"(`{kbr}` {K8}), for kx3 and its km3 baseline alike; its pages say \"kx3 (d513e37b, on {NAME})\" in the headline. "
        f"The reports made before the re-pin (`rl/results/slow_reports/2026-10-12_*` to `2026-10-14_*`) ran on main-c045ede's "
        f"engine and say so in theirs; the 2 of Oct 8-9 predate that build. No report made before the re-pin can be resumed with `--dir` "
        f"or be the base of a `--paired-with` variant. The re-pin came after its replay check: 202 of 202 games identical in each arm "
        f"(`{CHECK}/READING.md`)."))
    t = once(t, "the slow report's pinned program stays on the old engine until its re-pin, see \"The slow report\" below",
             f"the slow report's pinned program has been kx3's frozen players on this engine since its re-pin (Oct 22; tree `{T12}`), "
             f"see \"The slow report\" below", 'README 9')
    for s in ('cd20a97a', 'kx3-on-rules2', '4ebb30a9', '76df495b', 'kx_r2', 'until its re-pin', 'old engine until'):
        if s in t:
            print(f'note: README still mentions {s} at', [i + 1 for i, l in enumerate(t.splitlines()) if s in l])
    files[p] = t

    # ---- RUN5 (the status authority) and the adoption's notes: the re-pin landed ----------------------------------
    p = 'rl/RUN5.md'
    t = show(p)
    old = re.findall(r'^    - The slow report: not moved by this pin:[^\n]*$', t, re.M)
    if len(old) != 1:
        sys.exit(f'RUN5: {len(old)} slow-report status bullets, not 1')
    t = t.replace(old[0], (
        f"    - The slow report: re-pinned Oct 22, after its kx3 replay check (`rl/results/kx3_on_engine_2026-10-21/READING.md`: 202 of 202 kx3 "
        f"and 202 of 202 km3 development games identical; Dustin, Oct 21: the program moves only after that check passes). The program is "
        f"`{prog}` (sha256 {P8}…): kx3's frozen players (`claude/playout-pilot` d513e37b) on this engine, `{kbr}` {K8}, engine tree {T12}; "
        f"its pages say \"kx3 (d513e37b, on {NAME})\" and count as current (`make_predictions.py`). The 8 reports of Oct 12-14 ran on "
        f"main-c045ede's engine and say so; the 2 of Oct 8-9 predate that build. Record: `{CAND}/slow_pin/CERT.md`."))
    files[p] = t
    p = f'{CAND}/RELEASE_NOTES.md'
    t = show(p)
    t = once(t, "its pin tests pass (`slow_pin/PIN_TESTS.txt` on that branch).",
             "its pin tests pass (`slow_pin/PIN_TESTS.txt` on that branch). **Oct 22: re-pinned on main after its replay check** "
             "(`slow_pin/CERT.md`, `../kx3_on_engine_2026-10-21/READING.md`); this paragraph is the state at the adoption.", 'RELEASE_NOTES slow-report bullet')
    files[p] = t
    p = 'rl/engine-2026-10-21/README.md'
    t = show(p)
    t = once(t, "and the slow report until its re-pin:", "and the slow report until its re-pin (re-pinned Oct 22: `../results/engine_candidate_2026-10-20/slow_pin/CERT.md`):",
             'engine README 25')
    files[p] = t
    # the generator itself, so the commit can be rebuilt (SPEC section 4 named slowpin_final.py; this is its main-branch derivative)
    with open(os.path.abspath(__file__), encoding='utf-8') as fh:
        files[f'{CAND}/release/tools/slowpin_main.py'] = fh.read().replace('\r\n', '\n')

    # ---- make_predictions: the new harness tree is current --------------------------------------------------------
    p = 'rl/results/ladder_validation/make_predictions.py'
    t = show(p)
    t = once(t, '    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until the slow report\'s re-pin)\n',
             f'    "harness_engine_trees": ["{T12}"],          # slow reports / exams: "engine tree <12 hex>" in manifest.json (kx3 on {NAME})\n',
             'CURRENT_ENGINE harness tree')
    files[p] = t

    # ---- the certification record -------------------------------------------------------------------------------
    kxsecs = open(os.path.join(V['cert_dir'], 'sc_kx3.rc')).read().split()
    files[f'{CAND}/slow_pin/strength.build.json'] = open(prog + '.build.json', encoding='utf-8').read()
    files[f'{CAND}/slow_pin/selfchecks.txt'] = ''.join(f'{p} {psha} {sc[p]}\n' for p in ('km3', 'kx3'))
    files[f'{CAND}/slow_pin/CERT.md'] = CERT.format(K=K, K8=K8, KBR=kbr, T=T, T12=T12, NAME=NAME, FB=FB, FTREE=FTREE, PROG=prog, PSHA=psha, P8=P8, BUILT=built,
                                                     SCKM3=sc['km3'], SCKX3=sc['kx3'], KXSECS=kxsecs[1] if len(kxsecs) > 1 else '?',
                                                     CHECK=CHECK, C8=C8, CBR=V['check_branch'])
    for path in files:
        if path.startswith(CHECK + '/'):
            sys.exit(f'{path}: the pin would write into the check folder')

    # ---- commit: base + the check's folder (merge) + the pin's files ----------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'index'))
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
    exists = lambda p: subprocess.run(['git', '-C', REPO, 'cat-file', '-e', f'{base}:{p}'], capture_output=True).returncode == 0
    want_diff = sorted([('M' if exists(p) else 'A') + '\t' + p for p in files] + ['A\t' + p for p in gs('ls-tree', '-r', '--name-only', C, '--', CHECK + '/').splitlines()])
    if sorted(diff) != want_diff:
        sys.exit('unexpected diff:\n' + '\n'.join(sorted(set(diff) ^ set(want_diff))))
    if '--dry-run' in sys.argv:
        print(f'DRY RUN: tree {tree} on {base[:8]} + {C8}\n' + '\n'.join(d for d in diff if not d.split('\t')[1].startswith(CHECK + '/'))
              + f'\n(+ {sum(1 for d in diff if d.split(chr(9))[1].startswith(CHECK + "/"))} files of {CHECK}/)')
        return
    msg = (f"The slow report's re-pin: kx3 (d513e37b's players) on {NAME}'s engine, program {P8} ({kbr} {K8})\n\n"
           f"Dustin, Oct 21: \"Move the slow-report program only after its replay check passes.\" The check passed: {CHECK}/READING.md\n"
           f"(merged here from {V['check_branch']} {C8}: the spec, the registrations committed before any game, the games, COMPARE_DEV.txt).\n"
           f"The build record, both self-checks and the pin's other fields: {CAND}/slow_pin/CERT.md. make_predictions.py's CURRENT_ENGINE\n"
           f"lists the new harness tree {T12}. rl/strength/README.md (step 1, the cloud route, the engine notice) and rl/RUN5.md's status\n"
           f"line name the new program; dated pointers in RELEASE_NOTES.md and rl/engine-2026-10-21/README.md. The generator is committed\n"
           f"as {CAND}/release/tools/slowpin_main.py.\n\n"
           f"Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    commit = gs('-c', 'user.name=dacz8976-creator', '-c', 'user.email=dacz8976@gmail.com', 'commit-tree', tree, '-p', base, '-p', C, '-F', '-', inp=msg.encode())
    ref = f"refs/heads/{V['branch']}"
    cur = subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', ref], capture_output=True, text=True).stdout.strip()
    if cur and '--replace' not in sys.argv:
        sys.exit(f"{V['branch']} exists ({cur[:8]}); pass --replace")
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    print(f"re-pin {commit} on {V['branch']} (parents {base[:8]} {C8}, tree {tree[:8]})\n" + '\n'.join(d for d in diff if not d.split('\t')[1].startswith(CHECK + '/')))


CERT = """# The slow report's re-pin on {NAME}: certification

Dustin, Oct 21 (verbatim, relayed by the coordinator): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." The check passed (`{CHECK}/READING.md`, merged with this commit from `{CBR}` {C8}), so the program moves here.

- **The engine ref:** `{K}` on `{KBR}` (pushed). The frozen kx3 (claude/playout-pilot d513e37b, via laptop/kx3-on-rules2 cd20a97a) merged off-tree with the adopted engine's built commit {FB}: `git merge-tree`, no conflict. Its `engine/` is tree {T12} (`{T}`): {FB}'s {FTREE} plus kx3's six files, with `engine/src/players` d513e37b's byte for byte. `rl/strength` is {FB}'s.
- **The build** ({BUILT}): `env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_REPO=/home/dacz8976/pincand STRENGTH_BUILD_DIR=/home/dacz8976/kx_r3_build STRENGTH_TARGET_DIR=/home/dacz8976/kx_r3_build/target STRENGTH_JOBS=2 ionice -c3 bash rl/strength/build.sh {K} {PROG}`, in the night window, one cargo at a time, fresh build folders. Its record (`strength.build.json` here) says engine_ref {K8}, engine_tree_archived {T12}, harness bf9c5d68, jobs "2", program sha256 `{PSHA}`.
- **The gate: both self-checks, measured on {P8} itself** (12 games, t-altaria v t-suicune, the scrubbed environment slow_report.py uses):
  - km3: `{SCKM3}`, equal to the pin's text.
  - kx3: `{SCKX3}`, equal to the pin's text ({KXSECS} s).
- **The replay check:** the development run's 202 kx3 and 202 km3 games replayed on {P8} at their own seeds, against the reading fixed before any game (`{CHECK}/SPEC.md` section 4): passed (`{CHECK}/READING.md`).
- **The pin's changes:** program, program_sha256, selfcheck_measured_on_sha256, engine_ref, engine_tree, pilot_label ("kx3 (d513e37b, on {NAME})"), engine, pilot_provenance and reference_provenance. The self-check texts, the harness hash and every other field are unchanged. `rl/strength/README.md`'s cloud route quotes the new ref, branch, tree and program, its engine notice names the new program, and `make_predictions.py`'s CURRENT_ENGINE lists the harness tree {T12}.
- **The docs:** `rl/RUN5.md`'s status line, `rl/strength/README.md` (step 1 and the engine notice), a dated pointer in `RELEASE_NOTES.md` and in `rl/engine-2026-10-21/README.md`.
- **The generator:** `release/tools/slowpin_main.py`, committed here. SPEC.md section 4 named `release/tools/slowpin_final.py`. This is its main-branch form: the same pin texts and values, written as a merge with the check's record onto main, refused unless the check's READING.md says pass, and with the docs above.
- **The pin tests:** see `PIN_TESTS.txt` (run at this commit, added by the next commit).
- **What it replaces:** the Oct 12 build (cd20a97a on main-c045ede's engine, tree 4ebb30a94173, program 76df495b). The 8 slow reports made on it (`rl/results/slow_reports/2026-10-12_*` to `2026-10-14_*`) are complete and say main-c045ede's engine in theirs. After this pin a `--dir` resume of them is refused, and paired variants of them become impossible (`slow_report_paired.py`).
"""

if __name__ == '__main__':
    main()
